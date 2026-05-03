"""Tests for the /admin/tonight/editor drilldown.

Mirrors test_admin_phase_c.py patterns. Synthesizes a 05_editor/ tree
+ tests dashboard collector + route auth gating + happy/empty render.
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


def _write(p: Path, payload) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(payload), encoding="utf-8")


def _make_editor_tree(run_dir: Path) -> None:
    """Synthetic 05_editor/ with manifest + theme_routing + 2 dossiers."""
    ed = run_dir / "05_editor"
    _write(ed / "manifest.json", {
        "pipeline": "editor",
        "pipeline_version": "v2",
        "schema_version": "2.0",
        "night": 1,
        "counts": {
            "themes_routed": 2,
            "dossiers_succeeded": 2,
            "dossiers_failed": 0,
            "voices_engaged": 4,
            "refusals": 0,
        },
        "dossier_failures": [],
        "wall_clock_s": 320.5,
    })
    _write(ed / "theme_routing.json", {
        "schema_version": "2.0",
        "night": 1,
        "issue_no": 42193,
        "vol": "CXVI",
        "themes_to_dossiers": [
            {"theme_id": "theme_001", "dossier_no": 1, "theme_title": "T1", "n_engaged_voices": 2},
            {"theme_id": "theme_002", "dossier_no": 2, "theme_title": "T2", "n_engaged_voices": 2},
        ],
        "voices_routing": [
            {"voice_slug": "plato", "primary_theme": "theme_001", "primary_dossier": 1,
             "primary_theme_source": "Case A — Response N anchor"},
            {"voice_slug": "cleopatra", "primary_theme": "theme_001", "primary_dossier": 1,
             "primary_theme_source": "Case 2 — synthesis, lowest-numbered tiebreaker"},
        ],
        "refusals": [],
    })
    _write(ed / "dossiers" / "dossier_001.json", {
        "schema_version": "2.0",
        "kicker": "FOUR NAMINGS",
        "headline": "Test Headline About An Event",
        "subline": "deck",
        "body_paragraphs": ["First paragraph.", "Second paragraph.", "* * *", "Third paragraph here."],
        "headnotes": [
            {"voice_slug": "plato", "voice_name": "the voice of Plato", "framing_text": "..."},
            {"voice_slug": "cleopatra", "voice_name": "the voice of Cleopatra", "framing_text": "..."},
        ],
        "front_abstract": "Test abstract.",
        "metadata": {
            "theme_id": "theme_001",
            "theme_display_title": "On The Question",
            "issue_no": 42193,
            "input_tokens": 18000,
            "output_tokens": 3500,
            "wall_clock_s": 75.2,
        },
    })
    _write(ed / "dossiers" / "dossier_002.json", {
        "schema_version": "2.0",
        "kicker": "ANOTHER NAMING",
        "headline": "Another Headline",
        "body_paragraphs": ["Single paragraph."],
        "headnotes": [],
        "metadata": {"theme_id": "theme_002", "wall_clock_s": 60.0,
                     "input_tokens": 16000, "output_tokens": 3000},
    })


@pytest.fixture
def client(tmp_path, monkeypatch) -> TestClient:
    tmp_runs = tmp_path / "runs"
    monkeypatch.setattr(pipeline, "RUNS_DIR", tmp_runs)
    monkeypatch.setattr(dashboard, "RUNS_DIR", tmp_runs)
    monkeypatch.setattr(dashboard, "PROJECT_ROOT", tmp_path / "project")
    from ingest import sessions as sessions_mod
    monkeypatch.setattr(sessions_mod, "RUNS_DIR", tmp_runs)
    with TestClient(app) as c:
        yield c


# --- Dashboard collector ---------------------------------------------------


def test_collect_editor_detail_empty(tmp_path, monkeypatch):
    monkeypatch.setattr(dashboard, "RUNS_DIR", tmp_path / "runs")
    payload = dashboard.collect_editor_detail(1)
    assert payload["run_exists"] is False
    assert payload.get("dossiers", []) == []


def test_collect_editor_detail_full(tmp_path, monkeypatch):
    runs = tmp_path / "runs"
    monkeypatch.setattr(dashboard, "RUNS_DIR", runs)
    _make_editor_tree(runs / "athens_night_1")
    payload = dashboard.collect_editor_detail(1)
    assert payload["run_exists"] is True
    assert payload["editor_dir_present"] is True
    assert payload["counts"]["dossiers_succeeded"] == 2
    assert len(payload["dossiers"]) == 2
    assert len(payload["voices_routing"]) == 2

    # First dossier — kicker, headline, body word count, headnote count
    d1 = payload["dossiers"][0]
    assert d1["dossier_no"] == 1
    assert d1["kicker"] == "FOUR NAMINGS"
    assert d1["headline"] == "Test Headline About An Event"
    assert d1["n_body_paragraphs"] == 4
    assert d1["n_words"] > 0
    assert d1["n_headnotes"] == 2
    assert d1["wall_clock_s"] == 75.2

    # Second dossier
    d2 = payload["dossiers"][1]
    assert d2["dossier_no"] == 2
    assert d2["theme_id"] == "theme_002"


# --- Routes ---------------------------------------------------------------


@pytest.mark.parametrize("path", [
    "/admin/tonight/editor",
    "/admin/tonight/editor.json",
])
def test_editor_drilldown_admin_only(client, path):
    assert client.get(path).status_code == 401
    assert client.get(path, auth=PRODUCER_AUTH).status_code == 403


def test_editor_route_renders_empty(client, tmp_path, monkeypatch):
    monkeypatch.setattr(dashboard, "RUNS_DIR", tmp_path / "runs")
    r = client.get("/admin/tonight/editor?night=1", auth=ADMIN_AUTH)
    assert r.status_code == 200
    assert "No run directory" in r.text or "hasn't run yet" in r.text


def test_editor_route_renders_full(client, tmp_path, monkeypatch):
    runs = tmp_path / "runs"
    monkeypatch.setattr(dashboard, "RUNS_DIR", runs)
    _make_editor_tree(runs / "athens_night_1")
    r = client.get("/admin/tonight/editor?night=1", auth=ADMIN_AUTH)
    assert r.status_code == 200
    assert "FOUR NAMINGS" in r.text
    assert "ANOTHER NAMING" in r.text
    assert "Test Headline" in r.text
    assert "plato" in r.text
    assert "cleopatra" in r.text


def test_editor_json_mirrors_html(client, tmp_path, monkeypatch):
    runs = tmp_path / "runs"
    monkeypatch.setattr(dashboard, "RUNS_DIR", runs)
    _make_editor_tree(runs / "athens_night_1")
    r = client.get("/admin/tonight/editor.json?night=1", auth=ADMIN_AUTH)
    assert r.status_code == 200
    j = r.json()
    assert j["counts"]["dossiers_succeeded"] == 2
    assert len(j["dossiers"]) == 2


def test_pipeline_overview_links_to_editor(client, tmp_path, monkeypatch):
    """/admin/tonight should now link to /admin/tonight/editor."""
    runs = tmp_path / "runs"
    monkeypatch.setattr(dashboard, "RUNS_DIR", runs)
    monkeypatch.setattr(dashboard, "PROJECT_ROOT", tmp_path / "project")
    (runs / "athens_night_1").mkdir(parents=True)
    r = client.get("/admin/tonight?night=1", auth=ADMIN_AUTH)
    assert r.status_code == 200
    assert "/admin/tonight/editor?night=1" in r.text
