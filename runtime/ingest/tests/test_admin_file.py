"""Tests for /admin/file (read-only file viewer) and the new
/admin/tonight/transcription drilldown (C23 UX iteration, 2026-05-03).
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest
from starlette.testclient import TestClient

os.environ.setdefault("UPLOAD_APP_PASSWORD", "testpw")
os.environ.setdefault("ADMIN_APP_PASSWORD", "admin_pw")
os.environ.setdefault("ANTHROPIC_API_KEY", "test")
os.environ.setdefault("ASSEMBLYAI_API_KEY", "test")

REPO = Path(__file__).resolve().parent.parent.parent
FAKE_FLOW = REPO / "ingest" / "tests" / "fake_transcription_flow.py"
import shlex as _shlex  # noqa: E402
os.environ["INGEST_FLOW_CMD"] = _shlex.join([sys.executable, str(FAKE_FLOW)])

os.environ["UPLOAD_APP_PASSWORD"] = "testpw"
os.environ["ADMIN_APP_PASSWORD"] = "admin_pw"

from ingest.app import app  # noqa: E402
from ingest import dashboard, pipeline  # noqa: E402

ADMIN_AUTH = ("admin", "admin_pw")
PRODUCER_AUTH = ("producer", "testpw")


@pytest.fixture
def isolated_project(tmp_path: Path, monkeypatch):
    """Build a fake PROJECT_ROOT and patch every reference."""
    project = tmp_path / "project"
    runs = project / "runs"
    runs.mkdir(parents=True)
    # Drop a sample JSON file to view.
    payload = {"hello": "world", "n": 42}
    (runs / "sample.json").write_text(json.dumps(payload), encoding="utf-8")
    # And a log file.
    (runs / "sample.log").write_text("line one\nline two\n", encoding="utf-8")
    # And a forbidden binary file (no allowed suffix).
    (runs / "secret.bin").write_text("\x00\x01\x02", encoding="utf-8")

    # Patch all the places PROJECT_ROOT is read.
    from ingest import app as app_mod
    from ingest import config as config_mod
    monkeypatch.setattr(config_mod, "PROJECT_ROOT", project)
    monkeypatch.setattr(config_mod, "RUNS_DIR", runs)
    monkeypatch.setattr(dashboard, "PROJECT_ROOT", project)
    monkeypatch.setattr(dashboard, "RUNS_DIR", runs)
    from ingest import auth as auth_mod
    auth_mod._failures.clear()
    return project


@pytest.fixture
def client(isolated_project: Path) -> TestClient:
    with TestClient(app) as c:
        yield c


# --- /admin/file tests ------------------------------------------------------


def test_file_admin_only(client: TestClient):
    r_p = client.get("/admin/file?path=runs/sample.json", auth=PRODUCER_AUTH)
    assert r_p.status_code == 403
    r_a = client.get("/admin/file?path=runs/sample.json", auth=ADMIN_AUTH)
    assert r_a.status_code == 200


def test_file_serves_json_inline(client: TestClient):
    r = client.get("/admin/file?path=runs/sample.json", auth=ADMIN_AUTH)
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("application/json")
    assert "inline" in r.headers["content-disposition"]
    assert r.json() == {"hello": "world", "n": 42}


def test_file_serves_log_as_plaintext(client: TestClient):
    r = client.get("/admin/file?path=runs/sample.log", auth=ADMIN_AUTH)
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/plain")
    assert "line one" in r.text


def test_file_rejects_traversal(client: TestClient):
    r = client.get(
        "/admin/file?path=../../../etc/passwd", auth=ADMIN_AUTH,
    )
    # Either 400 (rejected as absolute resolved escapes root) or 403.
    assert r.status_code in (400, 403, 404)


def test_file_rejects_absolute_path(client: TestClient):
    r = client.get("/admin/file?path=/etc/passwd", auth=ADMIN_AUTH)
    assert r.status_code == 400
    assert "relative" in r.json()["detail"].lower()


def test_file_rejects_disallowed_suffix(client: TestClient):
    r = client.get("/admin/file?path=runs/secret.bin", auth=ADMIN_AUTH)
    assert r.status_code == 400
    assert "viewable" in r.json()["detail"].lower()


def test_file_rejects_missing_path(client: TestClient):
    r = client.get("/admin/file?path=runs/does-not-exist.json", auth=ADMIN_AUTH)
    assert r.status_code == 404


def test_file_rejects_empty_path(client: TestClient):
    r = client.get("/admin/file?path=", auth=ADMIN_AUTH)
    assert r.status_code == 400


def test_file_rejects_directory(client: TestClient, isolated_project: Path):
    r = client.get("/admin/file?path=runs", auth=ADMIN_AUTH)
    # Directory has no suffix → suffix check rejects with 400.
    # Also: not is_file() rejects with 400. Either way 400.
    assert r.status_code == 400


# --- /admin/tonight/transcription tests ------------------------------------


def test_transcription_drilldown_admin_only(client: TestClient):
    r_p = client.get(
        "/admin/tonight/transcription?night=1", auth=PRODUCER_AUTH,
    )
    assert r_p.status_code == 403
    r_a = client.get(
        "/admin/tonight/transcription?night=1", auth=ADMIN_AUTH,
    )
    assert r_a.status_code == 200


def test_transcription_drilldown_renders(client: TestClient):
    r = client.get(
        "/admin/tonight/transcription?night=1", auth=ADMIN_AUTH,
    )
    assert r.status_code == 200
    body = r.text
    # Title + breadcrumb back to Pipeline:
    assert "Transcription — Night 1" in body
    assert "← Pipeline · Night 1" in body
    # Night picker present:
    assert 'href="/admin/tonight/transcription?night=2"' in body


def test_transcription_drilldown_invalid_night_falls_back(client: TestClient):
    r = client.get(
        "/admin/tonight/transcription?night=99", auth=ADMIN_AUTH,
    )
    assert r.status_code == 200


def test_pipeline_overview_links_to_transcription_drilldown(
    client: TestClient, tmp_path: Path, monkeypatch,
):
    """When run_dir exists, the Transcription stage cell links to its drilldown."""
    runs = tmp_path / "runs2"
    monkeypatch.setattr(dashboard, "RUNS_DIR", runs)
    monkeypatch.setattr(dashboard, "PROJECT_ROOT", tmp_path / "p2")
    run_dir = runs / "athens_night_1"
    (run_dir / "_orchestrator_logs").mkdir(parents=True)
    (run_dir / "01_transcription").mkdir(parents=True)
    r = client.get("/admin/tonight?night=1", auth=ADMIN_AUTH)
    assert r.status_code == 200
    assert "/admin/tonight/transcription?night=1" in r.text
