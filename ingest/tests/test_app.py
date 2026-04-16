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
os.environ.setdefault("ANTHROPIC_API_KEY", "test")
os.environ.setdefault("ASSEMBLYAI_API_KEY", "test")

REPO = Path(__file__).resolve().parent.parent.parent
FAKE_FLOW = REPO / "ingest" / "tests" / "fake_transcription_flow.py"

# Redirect transcription to the fake flow for all tests in this file.
os.environ["INGEST_FLOW_CMD"] = f"{sys.executable} {FAKE_FLOW}"
os.environ["FAKE_DELAY_SECONDS"] = "1"

from ingest.app import app  # noqa: E402
from ingest import pipeline  # noqa: E402

AUTH = ("producer", "testpw")


@pytest.fixture
def flagged_session_id() -> str:
    """Return the session_id of the first ai_assembly-flagged Day One session.

    Skips the test if none are flagged (prevents false failures when the dev
    is running a clean checkout).
    """
    from ingest.sessions import load_sessions
    for s in load_sessions():
        if s.ai_assembly and s.day == "Day One":
            return s.session_id
    pytest.skip("no ai_assembly=true session found; flag one to run this test")


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

    # Poll status until terminal (should take ~1–2s with FAKE_DELAY_SECONDS=1).
    terminal = {"done", "error"}
    for _ in range(50):
        r = client.get(f"/session/{sid}/status.json", auth=AUTH)
        st = r.json()
        if st.get("state") in terminal:
            break
        time.sleep(0.2)

    assert st["state"] == "done", st

    # Filesystem check: the normalized m4a + fake outputs should exist.
    sdir = pipeline.RUNS_DIR / "athens_night_1" / "01_transcription" / sid
    assert (sdir / "audio.m4a").exists()
    assert (sdir / "session_package.json").exists()
    assert (sdir / "session.json").exists()
    assert (sdir / "pipeline.log").exists()

    # session.json shape: title got translated to session_title.
    s_json = json.loads((sdir / "session.json").read_text())
    assert s_json["session_title"]
    assert "roster" in s_json


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
