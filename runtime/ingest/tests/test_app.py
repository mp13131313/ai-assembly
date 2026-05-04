"""FastAPI route tests via TestClient.

Covers: auth, 404/409 on unknown/unrun sessions, upload happy path end-to-end
through the fake transcription flow, overwrite confirmation, concurrent
uploads to the same session, extension validation.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

import pytest
from starlette.testclient import TestClient

# Set required env BEFORE importing ingest.app (which validates at lifespan).
os.environ.setdefault("UPLOAD_APP_PASSWORD", "testpw")
os.environ.setdefault("ADMIN_APP_PASSWORD", "admin_pw")
os.environ.setdefault("ANTHROPIC_API_KEY", "test")
os.environ.setdefault("ASSEMBLYAI_API_KEY", "test")

REPO = Path(__file__).resolve().parent.parent.parent
FAKE_FLOW = REPO / "ingest" / "tests" / "fake_transcription_flow.py"

# Redirect transcription to the fake flow for all tests in this file.
# shlex.join quotes tokens so paths containing spaces (e.g. "AI Assembly/code")
# survive the shlex.split round-trip in ingest/pipeline.py::_launch_stage0.
import shlex as _shlex  # noqa: E402
os.environ["INGEST_FLOW_CMD"] = _shlex.join([sys.executable, str(FAKE_FLOW)])
os.environ["FAKE_DELAY_SECONDS"] = "1"

from ingest.app import app  # noqa: E402
from ingest import pipeline  # noqa: E402

# config.load_dotenv(override=True) may have overwritten our setdefault value
# above with whatever is in .env. Force-set post-import — auth.py reads the
# env at request time, so this takes effect immediately.
os.environ["UPLOAD_APP_PASSWORD"] = "testpw"
os.environ["ADMIN_APP_PASSWORD"] = "admin_pw"

AUTH = ("producer", "testpw")
ADMIN_AUTH = ("admin", "admin_pw")  # for routes that became admin-only post-C23


@pytest.fixture
def flagged_session_id() -> str:
    """Return the session_id of the first ai_assembly-flagged, audio-source
    Day One session.

    Vendor-source sessions (audio_source: "vendor") skip Stage 0 + the
    upload UI entirely and return 409 from /session/{id}/upload — those
    aren't a fit for the upload-path tests in this file.

    Skips the test if no eligible session exists (prevents false failures
    when the dev is running a clean checkout).
    """
    from ingest.sessions import load_sessions
    for s in load_sessions():
        if s.ai_assembly and s.day == "Day One" and not s.is_vendor:
            return s.session_id
    pytest.skip("no ai_assembly=true audio session found; flag one to run this test")


@pytest.fixture
def client(tmp_path: Path, monkeypatch) -> TestClient:
    # Redirect RUNS_DIR to a tmp dir so the test doesn't splatter files
    # into the real runs/ tree.
    tmp_runs = tmp_path / "runs"
    monkeypatch.setattr(pipeline, "RUNS_DIR", tmp_runs)
    # sessions.session_dir builds paths from the pipeline.RUNS_DIR constant,
    # but the sessions module imports RUNS_DIR directly at module load. Patch
    # both references.
    from ingest import sessions as sessions_mod
    monkeypatch.setattr(sessions_mod, "RUNS_DIR", tmp_runs)

    with TestClient(app) as c:
        yield c


def _make_tiny_audio(tmp_path: Path) -> Path:
    src = tmp_path / "sine.wav"
    subprocess.run(
        ["ffmpeg", "-hide_banner", "-nostdin", "-y",
         "-f", "lavfi", "-i", "sine=frequency=440:duration=1",
         str(src)],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    return src


# --- Auth -------------------------------------------------------------------


def test_health_is_unauthed(client: TestClient):
    assert client.get("/health").status_code == 200


def test_index_requires_auth(client: TestClient):
    assert client.get("/").status_code == 401
    assert client.get("/", auth=AUTH).status_code == 200


def test_wrong_password_rejected(client: TestClient):
    assert client.get("/", auth=("producer", "wrong")).status_code == 401


# --- Navigation -------------------------------------------------------------


def test_unknown_session_404(client: TestClient):
    r = client.get("/session/does_not_exist", auth=AUTH)
    assert r.status_code == 404


def test_unrun_day_session_409(client: TestClient):
    """A Day Zero / Day Four / Special Activations session returns 409."""
    from ingest.sessions import load_sessions
    non_runnable = [
        s for s in load_sessions()
        if s.day in {"Day Zero", "Day Four", "Special Activations"}
    ]
    if not non_runnable:
        pytest.skip("no non-runnable sessions in sessions.json")
    r = client.get(f"/session/{non_runnable[0].session_id}", auth=AUTH)
    assert r.status_code == 409


# --- Upload happy path ------------------------------------------------------


def test_upload_then_transcribe_end_to_end(
    client: TestClient, tmp_path: Path, flagged_session_id: str
):
    audio = _make_tiny_audio(tmp_path)
    sid = flagged_session_id

    # First upload — no overwrite needed.
    with audio.open("rb") as f:
        r = client.post(
            f"/session/{sid}/upload",
            params={"filename": audio.name},
            content=f.read(),
            auth=AUTH,
        )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["ok"] is True
    assert body["status_url"].endswith("/status")

    # C26 (2026-05-04): upload now stops at `normalized` (ffmpeg complete);
    # the overnight orchestrator handles transcription dispatch in its own
    # poll loop, not at upload time. Test asserts upload-side terminal.
    upload_terminal = {"normalized", "error"}
    for _ in range(50):
        r = client.get(f"/session/{sid}/status.json", auth=ADMIN_AUTH)
        st = r.json()
        if st.get("state") in upload_terminal:
            break
        time.sleep(0.2)

    assert st["state"] == "normalized", st

    # Filesystem check: the normalized m4a + session.json should exist; the
    # full transcription outputs (session_package.json) are NOT produced
    # here — orchestrator fires the subprocess separately.
    sdir = pipeline.RUNS_DIR / "athens_night_1" / "01_transcription" / sid
    assert (sdir / "audio.m4a").exists()
    assert (sdir / "session.json").exists()
    assert (sdir / "pipeline.log").exists()
    assert not (sdir / "session_package.json").exists()

    # session.json shape: title got translated to session_title.
    s_json = json.loads((sdir / "session.json").read_text())
    assert s_json["session_title"]
    assert "roster" in s_json

    # C26: invoking pipeline.fire_transcription against the normalized
    # session is exactly what the orchestrator's Stage 0 dispatch does.
    # Verifies the orchestrator-facing entrypoint works end-to-end against
    # a real upload's filesystem state.
    session_json_path = sdir / "session.json"
    fired = pipeline.fire_transcription(sdir, session_json_path)
    assert fired["state"] == "transcribing", fired
    assert fired.get("pid"), fired

    # Now wait for transcription to complete (FAKE_DELAY_SECONDS=1; ~1-2s).
    terminal = {"done", "error"}
    for _ in range(50):
        r = client.get(f"/session/{sid}/status.json", auth=ADMIN_AUTH)
        st = r.json()
        if st.get("state") in terminal:
            break
        time.sleep(0.2)
    assert st["state"] == "done", st
    assert (sdir / "session_package.json").exists()


# --- Validation -------------------------------------------------------------


def test_bad_extension_rejected(client: TestClient, flagged_session_id: str):
    r = client.post(
        f"/session/{flagged_session_id}/upload",
        params={"filename": "not-audio.txt"},
        content=b"junk",
        auth=AUTH,
    )
    assert r.status_code == 400


def test_empty_body_rejected(client: TestClient, flagged_session_id: str):
    r = client.post(
        f"/session/{flagged_session_id}/upload",
        params={"filename": "x.mp3"},
        content=b"",
        auth=AUTH,
    )
    assert r.status_code == 400


def test_overwrite_requires_flag(
    client: TestClient, tmp_path: Path, flagged_session_id: str
):
    """Second upload without overwrite=true gets 409."""
    audio = _make_tiny_audio(tmp_path)
    sid = flagged_session_id
    data = audio.read_bytes()
    r = client.post(
        f"/session/{sid}/upload",
        params={"filename": audio.name},
        content=data, auth=AUTH,
    )
    assert r.status_code == 200

    # Wait for audio.m4a to be created by normalize.
    sdir = pipeline.RUNS_DIR / "athens_night_1" / "01_transcription" / sid
    for _ in range(50):
        if (sdir / "audio.m4a").exists():
            break
        time.sleep(0.2)
    assert (sdir / "audio.m4a").exists()

    r2 = client.post(
        f"/session/{sid}/upload",
        params={"filename": audio.name},
        content=data, auth=AUTH,
    )
    assert r2.status_code == 409
    assert "overwrite=true" in r2.json()["detail"]

    # With overwrite=true, it succeeds.
    r3 = client.post(
        f"/session/{sid}/upload",
        params={"filename": audio.name, "overwrite": "true"},
        content=data, auth=AUTH,
    )
    assert r3.status_code == 200


# --- Vendor-aware session routes (audio_source: "vendor", 2026-05-03) -------


@pytest.fixture
def vendor_session_id() -> str:
    """Return the session_id of the first ai_assembly + vendor-source session.

    Vendor sessions land via flows/vendor_intake.py at the 01_transcription
    boundary; the upload UI must refuse audio for them. These tests pin
    that contract.
    """
    from ingest.sessions import load_sessions
    for s in load_sessions():
        if s.ai_assembly and s.is_vendor:
            return s.session_id
    pytest.skip("no audio_source=vendor session found")


def test_producer_index_excludes_vendor_sessions(
    client: TestClient, vendor_session_id: str
):
    # Producer's index should not surface vendor sessions — they're not the
    # producer's responsibility (no audio to upload).
    r = client.get("/", auth=AUTH)
    assert r.status_code == 200
    assert vendor_session_id not in r.text


def test_admin_index_includes_vendor_sessions(
    client: TestClient, vendor_session_id: str
):
    # Admin sees everything for situational awareness.
    r = client.get("/", auth=ADMIN_AUTH)
    assert r.status_code == 200
    assert vendor_session_id in r.text


def test_producer_get_vendor_session_detail_403(
    client: TestClient, vendor_session_id: str
):
    r = client.get(f"/session/{vendor_session_id}", auth=AUTH)
    assert r.status_code == 403
    assert "vendor" in r.json()["detail"].lower()


def test_admin_get_vendor_session_detail_ok(
    client: TestClient, vendor_session_id: str
):
    r = client.get(f"/session/{vendor_session_id}", auth=ADMIN_AUTH)
    assert r.status_code == 200


def test_upload_to_vendor_session_409_for_admin(
    client: TestClient, vendor_session_id: str
):
    # Even admin can't accidentally upload audio to a vendor session — the
    # bytes would be orphaned (no Stage 0 trigger) and would muddy the
    # dashboard.
    r = client.post(
        f"/session/{vendor_session_id}/upload",
        params={"filename": "x.m4a"}, content=b"junk", auth=ADMIN_AUTH,
    )
    assert r.status_code == 409
    assert "vendor" in r.json()["detail"].lower()


def test_retry_on_vendor_session_409(
    client: TestClient, vendor_session_id: str, tmp_path: Path
):
    # Pre-create a session_dir so retry doesn't 404 first.
    sdir = pipeline.RUNS_DIR / "athens_night_1" / "01_transcription" / vendor_session_id
    sdir.mkdir(parents=True, exist_ok=True)
    (sdir / "status.json").write_text(
        json.dumps({"state": "done", "source": "vendor"})
    )
    r = client.post(f"/session/{vendor_session_id}/retry", auth=ADMIN_AUTH)
    assert r.status_code == 409
    assert "vendor_intake" in r.json()["detail"]
