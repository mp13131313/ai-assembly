"""Tests for the role-split auth + /admin/tonight dashboard (C23, 2026-05-03).

Covers:
  * Producer creds → role "producer", admin creds → role "admin"
  * Admin-only routes 403 producers (/status, /admin/tonight, /retry POST)
  * Per-session /status renders truncated for producer, full for admin
  * /admin/tonight renders for admin
  * dashboard.collect_night_state returns expected pending shape for an
    empty PROJECT_ROOT (no athens_night_<N> dirs yet)
"""

from __future__ import annotations

import os
import shlex as _shlex
import sys
from pathlib import Path

import pytest
from starlette.testclient import TestClient

# Set required env BEFORE importing ingest.app (validated at lifespan).
os.environ.setdefault("UPLOAD_APP_PASSWORD", "testpw")
os.environ.setdefault("ADMIN_APP_PASSWORD", "admin_pw")
os.environ.setdefault("ANTHROPIC_API_KEY", "test")
os.environ.setdefault("ASSEMBLYAI_API_KEY", "test")

REPO = Path(__file__).resolve().parent.parent.parent
FAKE_FLOW = REPO / "ingest" / "tests" / "fake_transcription_flow.py"
os.environ["INGEST_FLOW_CMD"] = _shlex.join([sys.executable, str(FAKE_FLOW)])
os.environ["FAKE_DELAY_SECONDS"] = "1"

from ingest.app import app  # noqa: E402
from ingest import pipeline  # noqa: E402

# config.load_dotenv(override=True) may have overwritten our setdefault — pin.
os.environ["UPLOAD_APP_PASSWORD"] = "testpw"
os.environ["ADMIN_APP_PASSWORD"] = "admin_pw"

PRODUCER_AUTH = ("producer", "testpw")
ADMIN_AUTH = ("admin", "admin_pw")


@pytest.fixture
def client(tmp_path: Path, monkeypatch) -> TestClient:
    """Redirect RUNS_DIR + reset rate-limit state per test."""
    tmp_runs = tmp_path / "runs"
    monkeypatch.setattr(pipeline, "RUNS_DIR", tmp_runs)
    from ingest import sessions as sessions_mod
    monkeypatch.setattr(sessions_mod, "RUNS_DIR", tmp_runs)
    # Reset auth rate-limit between tests so "wrong password" tests don't
    # accumulate failures across the suite and trigger 429.
    from ingest import auth as auth_mod
    auth_mod._failures.clear()
    with TestClient(app) as c:
        yield c


@pytest.fixture
def flagged_session_id() -> str:
    """Same fixture pattern as test_app.py."""
    from ingest.sessions import load_sessions
    for s in load_sessions():
        if s.ai_assembly and s.day == "Day One":
            return s.session_id
    pytest.skip("no ai_assembly=true Day One session found")


# --- Auth role identification ----------------------------------------------


def test_producer_creds_authorize_producer_routes(client: TestClient):
    """Producer can hit / and per-session pages."""
    assert client.get("/", auth=PRODUCER_AUTH).status_code == 200


def test_admin_creds_authorize_producer_routes(client: TestClient):
    """Admin can also hit / (all-role routes accept admin)."""
    assert client.get("/", auth=ADMIN_AUTH).status_code == 200


def test_wrong_creds_rejected(client: TestClient):
    assert client.get("/", auth=("anyuser", "wrong")).status_code == 401


# --- Admin-only routes 403 producers ---------------------------------------


def test_overview_status_admin_only(client: TestClient):
    """`/status` is admin-only (per-session pipeline state is operator concern)."""
    r_p = client.get("/status", auth=PRODUCER_AUTH)
    assert r_p.status_code == 403
    r_a = client.get("/status", auth=ADMIN_AUTH)
    assert r_a.status_code == 200


def test_overview_status_json_admin_only(client: TestClient):
    r_p = client.get("/status.json", auth=PRODUCER_AUTH)
    assert r_p.status_code == 403
    r_a = client.get("/status.json", auth=ADMIN_AUTH)
    assert r_a.status_code == 200


def test_session_status_json_admin_only(
    client: TestClient, flagged_session_id: str,
):
    """Producer's truncated view doesn't poll JSON; route is admin-only."""
    r_p = client.get(
        f"/session/{flagged_session_id}/status.json", auth=PRODUCER_AUTH,
    )
    assert r_p.status_code == 403
    r_a = client.get(
        f"/session/{flagged_session_id}/status.json", auth=ADMIN_AUTH,
    )
    assert r_a.status_code == 200


def test_session_retry_admin_only(client: TestClient, flagged_session_id: str):
    """Retry is an intervention surface — admin only."""
    r_p = client.post(
        f"/session/{flagged_session_id}/retry", auth=PRODUCER_AUTH,
    )
    assert r_p.status_code == 403
    # Admin gets through to the route handler (404 expected since no session
    # dir exists in the tmp runs/ tree — that's fine; we're testing the
    # auth gate, not the underlying logic).
    r_a = client.post(
        f"/session/{flagged_session_id}/retry", auth=ADMIN_AUTH,
    )
    assert r_a.status_code == 404


def test_admin_tonight_admin_only(client: TestClient):
    r_p = client.get("/admin/tonight", auth=PRODUCER_AUTH)
    assert r_p.status_code == 403
    r_a = client.get("/admin/tonight", auth=ADMIN_AUTH)
    assert r_a.status_code == 200


def test_admin_tonight_json_admin_only(client: TestClient):
    r_p = client.get("/admin/tonight.json", auth=PRODUCER_AUTH)
    assert r_p.status_code == 403
    r_a = client.get("/admin/tonight.json", auth=ADMIN_AUTH)
    assert r_a.status_code == 200


# --- Per-session status: producer truncated, admin full --------------------


def test_session_status_producer_renders_truncated(
    client: TestClient, flagged_session_id: str,
):
    """Producer's view contains 'Received' or 'Not yet uploaded'; never 'transcribing'."""
    r = client.get(
        f"/session/{flagged_session_id}/status", auth=PRODUCER_AUTH,
    )
    assert r.status_code == 200
    body = r.text
    # Truncated marker present:
    assert "Not yet uploaded" in body or "Received" in body
    # Full state machine NOT leaked:
    assert "transcribing · ASR" not in body
    assert "speaker ID" not in body


def test_session_status_admin_renders_full(
    client: TestClient, flagged_session_id: str,
):
    """Admin's view contains the full state machine crumbs (status.html)."""
    r = client.get(
        f"/session/{flagged_session_id}/status", auth=ADMIN_AUTH,
    )
    assert r.status_code == 200
    body = r.text
    # Full state machine present (one of the crumb labels):
    assert "transcribing · ASR" in body or "transcribing · speaker ID" in body


# --- Admin tonight payload shape -------------------------------------------


def test_admin_tonight_json_pending_shape(client: TestClient):
    """No run_dir exists in the tmp project root → all stages report pending."""
    r = client.get("/admin/tonight.json", auth=ADMIN_AUTH)
    assert r.status_code == 200
    payload = r.json()
    assert payload["night"] in (1, 2, 3)
    assert payload["run_exists"] is False
    for stage in ("transcription", "researcher", "provocateur",
                  "voice", "editor", "publish"):
        assert payload["stages"][stage]["state"] == "pending"


def test_admin_tonight_night_param(client: TestClient):
    """Explicit ?night=N override."""
    r = client.get("/admin/tonight.json?night=3", auth=ADMIN_AUTH)
    assert r.status_code == 200
    assert r.json()["night"] == 3


def test_admin_tonight_invalid_night_falls_back(client: TestClient):
    """Out-of-range night silently falls back to latest_active_night()."""
    r = client.get("/admin/tonight.json?night=99", auth=ADMIN_AUTH)
    assert r.status_code == 200
    assert r.json()["night"] in (1, 2, 3)


# --- Index page state-dot behavior per role --------------------------------


def test_index_admin_sees_pipeline_state_dots(client: TestClient):
    """Admin index page renders dot classes (none of producer's overrides)."""
    r = client.get("/", auth=ADMIN_AUTH)
    assert r.status_code == 200
    # Admin index includes the "All statuses" + "Tonight" nav links:
    assert "/status" in r.text
    assert "/admin/tonight" in r.text


def test_index_producer_no_admin_nav(client: TestClient):
    """Producer index does NOT show admin-only nav links."""
    r = client.get("/", auth=PRODUCER_AUTH)
    assert r.status_code == 200
    # Admin links absent:
    assert "/admin/tonight" not in r.text
    # /status is admin-only; should not appear in producer nav. (May still
    # appear elsewhere as a string fragment, but not as a navigation link.)
    nav_section = r.text.split("</nav>")[0] if "</nav>" in r.text else r.text
    assert 'href="/status"' not in nav_section
