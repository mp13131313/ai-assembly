"""Tests for the C23 Phase C drilldowns (2026-05-03):
    /admin/tonight/researcher
    /admin/tonight/provocateur
    /admin/tonight/publish

Covers:
  * dashboard collectors against synthetic Stage 2/3/7 outputs
  * route auth gating (admin only; producer 403)
  * happy-path render
  * empty-state render when run_dir / index missing
  * /admin/tonight Pipeline overview links to all six drilldowns

The patterns mirror test_admin_voice.py (Phase B). Synthesized filesystem
trees keep tests isolated and fast.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest
from starlette.testclient import TestClient

# Required env BEFORE importing ingest.app.
os.environ.setdefault("UPLOAD_APP_PASSWORD", "testpw")
os.environ.setdefault("ADMIN_APP_PASSWORD", "admin_pw")
os.environ.setdefault("ANTHROPIC_API_KEY", "test")
os.environ.setdefault("ASSEMBLYAI_API_KEY", "test")

REPO = Path(__file__).resolve().parent.parent.parent
FAKE_FLOW = REPO / "ingest" / "tests" / "fake_transcription_flow.py"
import shlex as _shlex  # noqa: E402
os.environ["INGEST_FLOW_CMD"] = _shlex.join([sys.executable, str(FAKE_FLOW)])

# Pin post-import in case load_dotenv overrode.
os.environ["UPLOAD_APP_PASSWORD"] = "testpw"
os.environ["ADMIN_APP_PASSWORD"] = "admin_pw"

from ingest.app import app  # noqa: E402
from ingest import dashboard, pipeline  # noqa: E402

ADMIN_AUTH = ("admin", "admin_pw")
PRODUCER_AUTH = ("producer", "testpw")


# --- Synthetic-tree builders -----------------------------------------------


def _write(p: Path, payload) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(payload), encoding="utf-8")


def _make_researcher_tree(run_dir: Path) -> None:
    """02_researcher/ with grouping.json, all_extractions.json, and two
    per-session extraction files."""
    rsr = run_dir / "02_researcher"
    grouping = {
        "themes": [
            {
                "theme_id": "theme_001",
                "title": "The West / The West Divide",
                "abstract": "Whether 'the West' names a discoverable tradition or a contested construct.",
                "clusters": [
                    {"cluster_id": "cluster_01", "cluster_title": "Civilizational claims",
                     "cluster_abstract": "Speakers asserting the West as a real thing.",
                     "extraction_ids": ["e1", "e2", "e3"]},
                    {"cluster_id": "cluster_02", "cluster_title": "Construct critique",
                     "cluster_abstract": "Speakers framing it as constructed.",
                     "extraction_ids": ["e4", "e5"]},
                ],
            },
            {
                "theme_id": "theme_002",
                "title": "Algorithmic governance",
                "abstract": "Algorithms governing algorithms.",
                "clusters": [
                    {"cluster_id": "cluster_03", "cluster_title": "Emergent effects",
                     "cluster_abstract": "Unintended societal-scale outputs.",
                     "extraction_ids": ["e6", "e7", "e8", "e9"]},
                ],
            },
        ],
        "isolates": [
            {"cluster_id": "iso_01", "cluster_title": "Lone voice on liturgy",
             "cluster_abstract": "Stand-alone observation about ritual."},
        ],
    }
    _write(rsr / "grouping.json", grouping)
    _write(rsr / "all_extractions.json", {"extractions": [{"id": f"e{i}"} for i in range(1, 10)]})
    _write(rsr / "session_a_extractions.json", {"extractions": [{"id": "e1"}, {"id": "e2"}]})
    _write(rsr / "session_b_extractions.json", {"extractions": [{"id": f"e{i}"} for i in range(3, 10)]})


def _make_provocateur_tree(run_dir: Path) -> None:
    """03_provocateur/ with manifest, selection, triage_flags, two voices,
    one formulation, one briefing."""
    prov = run_dir / "03_provocateur"
    _write(prov / "manifest.json", {
        "pipeline": "provocateur",
        "outputs": {
            "selected_themes": 2,
            "dropped_themes": 0,
            "formulations": 1,
            "briefings_written": 1,
            "forced_fits": 0,
            "stretch_swaps": 0,
            "voices_below_target": 0,
        },
    })
    _write(prov / "selection.json", {
        "kept_themes": ["theme_001", "theme_002"],
        "dropped_themes": [],
        "assignments_by_member": {"Plato": ["theme_001"], "Cleopatra": ["theme_002"]},
        "coverage_per_member": {"Plato": 1, "Cleopatra": 1},
        "forced_fits": [],
        "stretch_swaps": [],
        "below_target": [],
    })
    _write(prov / "triage_flags.json", {
        "theme_flags": [
            {"theme_id": "theme_001", "worth_surfacing": True,
             "audience_friction": "moderate", "fault_line_present": True,
             "fault_line_description": "West as tradition vs construct."},
            {"theme_id": "theme_002", "worth_surfacing": True,
             "audience_friction": "low", "fault_line_present": False},
        ],
    })
    _write(prov / "triage_voices" / "plato.json", {
        "voice": "Plato",
        "ranked_themes": [
            {"theme_id": "theme_001", "activation": "strong",
             "is_stretch": False, "reason": "Forms vs constructs."},
        ],
        "flat_themes": [
            {"theme_id": "theme_002", "reason": "Algorithms aren't dialectic."},
        ],
    })
    _write(prov / "triage_voices" / "cleopatra.json", {
        "voice": "Cleopatra",
        "ranked_themes": [
            {"theme_id": "theme_002", "activation": "moderate",
             "is_stretch": True, "reason": "Statecraft scaled."},
        ],
        "flat_themes": [],
    })
    _write(prov / "formulations" / "theme_001__plato.json", {
        "theme_id": "theme_001",
        "member": "Plato",
        "mode": "engage",
        "formulation": "What you call the West, I might call a shadow on the cave wall.",
        "theme_display_title": "The West / The West Divide",
        "selected_quotes": [{"text": "..."}, {"text": "..."}],
        "grounding_extraction_ids": ["e1", "e2"],
        "rationale": "Forms vs constructed traditions.",
    })
    _write(prov / "briefings" / "plato.json", {"formulations": [{"theme_id": "theme_001"}]})


def _make_publish_tree(project_root: Path, night: int) -> None:
    """published_artifacts/nights/night_<N>/ with _index.json + 2 voice files."""
    pub_dir = project_root / "published_artifacts" / "nights" / f"night_{night}"
    _write(pub_dir / "_index.json", {
        "night": night,
        "url_path": f"/night-{night}",
        "generated_at": "2026-05-08T03:14:00+02:00",
        "voices": [
            {
                "voice_slug": "plato", "voice_name": "Plato of Athens",
                "url_path": f"/night-{night}/plato",
                "title": "The cave at scale",
                "subtitle": "On what algorithms cannot see",
                "selected_form": "essay", "stance": "engage",
                "themes_addressed": ["theme_001", "theme_002"],
                "decision": "amend", "amendment_count": 1,
                "word_count": 850,
            },
            {
                "voice_slug": "cleopatra", "voice_name": "Cleopatra Thea Philopator",
                "url_path": f"/night-{night}/cleopatra",
                "title": "Reign and ledger",
                "subtitle": "Statecraft as algorithm",
                "selected_form": "letter", "stance": "engage",
                "themes_addressed": ["theme_002"],
                "decision": "no_change", "amendment_count": 0,
                "word_count": 670,
            },
        ],
        "voice_count": 2,
    })
    _write(pub_dir / "plato.json", {"voice_slug": "plato", "night": night})
    _write(pub_dir / "cleopatra.json", {"voice_slug": "cleopatra", "night": night})


# --- Dashboard helpers tested in isolation ---------------------------------


def test_collect_researcher_detail_empty(tmp_path, monkeypatch):
    monkeypatch.setattr(dashboard, "RUNS_DIR", tmp_path / "runs")
    payload = dashboard.collect_researcher_detail(1)
    assert payload["run_exists"] is False
    assert payload["themes"] == []


def test_collect_researcher_detail_full(tmp_path, monkeypatch):
    runs = tmp_path / "runs"
    monkeypatch.setattr(dashboard, "RUNS_DIR", runs)
    run_dir = runs / "athens_night_1"
    _make_researcher_tree(run_dir)
    payload = dashboard.collect_researcher_detail(1)
    assert payload["grouping_present"] is True
    assert payload["totals"]["n_themes"] == 2
    assert payload["totals"]["n_clusters"] == 3
    assert payload["totals"]["n_extractions_in_clusters"] == 9
    assert payload["totals"]["n_isolates"] == 1
    assert payload["totals"]["n_extractions_total"] == 9
    assert len(payload["per_session"]) == 2
    # Themes are preserved in input order; first theme has 2 clusters.
    assert payload["themes"][0]["theme_id"] == "theme_001"
    assert payload["themes"][0]["n_clusters"] == 2
    # Isolates reflected.
    assert len(payload["isolates"]) == 1


def test_collect_provocateur_detail_full(tmp_path, monkeypatch):
    runs = tmp_path / "runs"
    monkeypatch.setattr(dashboard, "RUNS_DIR", runs)
    run_dir = runs / "athens_night_1"
    _make_provocateur_tree(run_dir)
    payload = dashboard.collect_provocateur_detail(1)
    assert payload["manifest_present"] is True
    assert payload["counts"]["n_themes_selected"] == 2
    assert payload["counts"]["n_formulations"] == 1
    # Two voices: plato + cleopatra
    voice_slugs = {v["voice_slug"] for v in payload["voices"]}
    assert voice_slugs == {"plato", "cleopatra"}
    # Two themes from triage + one from formulation = same set
    theme_ids = {t["theme_id"] for t in payload["themes"]}
    assert theme_ids == {"theme_001", "theme_002"}
    # Triage cells: 2 ranked + 1 flat = 3
    assert len(payload["triage_cells"]) == 3
    # Formulation cells: 1 (plato/theme_001)
    assert len(payload["formulation_cells"]) == 1
    fc = payload["formulation_cells"][0]
    assert fc["voice_slug"] == "plato" and fc["theme_id"] == "theme_001"
    # Theme flags reflected
    assert len(payload["theme_flags"]) == 2


def test_collect_publish_detail_empty(tmp_path, monkeypatch):
    monkeypatch.setattr(dashboard, "PROJECT_ROOT", tmp_path / "project")
    monkeypatch.setattr(dashboard, "RUNS_DIR", tmp_path / "runs")
    payload = dashboard.collect_publish_detail(1)
    assert payload["index_present"] is False
    assert payload["voices"] == []


def test_collect_publish_detail_full(tmp_path, monkeypatch):
    pr = tmp_path / "project"
    monkeypatch.setattr(dashboard, "PROJECT_ROOT", pr)
    monkeypatch.setattr(dashboard, "RUNS_DIR", tmp_path / "runs")
    _make_publish_tree(pr, 1)
    payload = dashboard.collect_publish_detail(1)
    assert payload["index_present"] is True
    assert payload["totals"]["n_voices"] == 2
    assert payload["voices"][0]["voice_slug"] == "plato"
    assert payload["voices"][0]["has_per_voice_file"] is True
    assert payload["voices"][1]["decision"] == "no_change"


# --- Route + auth tests -----------------------------------------------------


@pytest.fixture
def client(tmp_path, monkeypatch) -> TestClient:
    tmp_runs = tmp_path / "runs"
    tmp_project = tmp_path / "project"
    monkeypatch.setattr(pipeline, "RUNS_DIR", tmp_runs)
    monkeypatch.setattr(dashboard, "RUNS_DIR", tmp_runs)
    monkeypatch.setattr(dashboard, "PROJECT_ROOT", tmp_project)
    from ingest import sessions as sessions_mod
    monkeypatch.setattr(sessions_mod, "RUNS_DIR", tmp_runs)
    with TestClient(app) as c:
        yield c


@pytest.mark.parametrize("path", [
    "/admin/tonight/researcher",
    "/admin/tonight/researcher.json",
    "/admin/tonight/provocateur",
    "/admin/tonight/provocateur.json",
    "/admin/tonight/publish",
    "/admin/tonight/publish.json",
])
def test_drilldowns_admin_only(client, path):
    # No auth: 401
    assert client.get(path).status_code == 401
    # Producer: 403
    assert client.get(path, auth=PRODUCER_AUTH).status_code == 403


def test_researcher_route_renders_empty(client, tmp_path, monkeypatch):
    # No run_dir created — empty-state branch.
    monkeypatch.setattr(dashboard, "RUNS_DIR", tmp_path / "runs")
    r = client.get("/admin/tonight/researcher?night=1", auth=ADMIN_AUTH)
    assert r.status_code == 200
    assert "No run directory" in r.text or "hasn't produced" in r.text


def test_researcher_route_renders_full(client, tmp_path, monkeypatch):
    runs = tmp_path / "runs"
    monkeypatch.setattr(dashboard, "RUNS_DIR", runs)
    _make_researcher_tree(runs / "athens_night_1")
    r = client.get("/admin/tonight/researcher?night=1", auth=ADMIN_AUTH)
    assert r.status_code == 200
    # Theme titles + cluster ids should appear in the rendered HTML.
    assert "theme_001" in r.text
    assert "The West / The West Divide" in r.text
    assert "cluster_01" in r.text
    assert "Civilizational claims" in r.text
    # Isolate is rendered.
    assert "iso_01" in r.text


def test_researcher_json_mirrors_html(client, tmp_path, monkeypatch):
    runs = tmp_path / "runs"
    monkeypatch.setattr(dashboard, "RUNS_DIR", runs)
    _make_researcher_tree(runs / "athens_night_1")
    r = client.get("/admin/tonight/researcher.json?night=1", auth=ADMIN_AUTH)
    assert r.status_code == 200
    j = r.json()
    assert j["totals"]["n_themes"] == 2
    assert j["totals"]["n_clusters"] == 3


def test_provocateur_route_renders_full(client, tmp_path, monkeypatch):
    runs = tmp_path / "runs"
    monkeypatch.setattr(dashboard, "RUNS_DIR", runs)
    _make_provocateur_tree(runs / "athens_night_1")
    r = client.get("/admin/tonight/provocateur?night=1", auth=ADMIN_AUTH)
    assert r.status_code == 200
    # Triage matrix renders with both voices and theme columns.
    assert "plato" in r.text
    assert "cleopatra" in r.text
    assert "theme_001" in r.text
    assert "theme_002" in r.text
    # Formulation grid: plato/theme_001 cell has the ✓ link to formulations file.
    assert "formulations/theme_001__plato.json" in r.text


def test_provocateur_route_renders_empty(client, tmp_path, monkeypatch):
    monkeypatch.setattr(dashboard, "RUNS_DIR", tmp_path / "runs")
    r = client.get("/admin/tonight/provocateur?night=1", auth=ADMIN_AUTH)
    assert r.status_code == 200
    assert "No run directory" in r.text or "hasn't produced" in r.text


def test_publish_route_renders_full(client, tmp_path, monkeypatch):
    monkeypatch.setattr(dashboard, "PROJECT_ROOT", tmp_path / "project")
    monkeypatch.setattr(dashboard, "RUNS_DIR", tmp_path / "runs")
    _make_publish_tree(tmp_path / "project", 1)
    r = client.get("/admin/tonight/publish?night=1", auth=ADMIN_AUTH)
    assert r.status_code == 200
    # Both voice rows appear with their titles.
    assert "The cave at scale" in r.text
    assert "Reign and ledger" in r.text
    # Per-voice file link rendered.
    assert "plato.json" in r.text


def test_publish_route_renders_empty(client, tmp_path, monkeypatch):
    monkeypatch.setattr(dashboard, "PROJECT_ROOT", tmp_path / "project")
    monkeypatch.setattr(dashboard, "RUNS_DIR", tmp_path / "runs")
    r = client.get("/admin/tonight/publish?night=1", auth=ADMIN_AUTH)
    assert r.status_code == 200
    assert "hasn't produced" in r.text


# --- /admin/tonight Pipeline overview links to all six drilldowns ----------


def test_pipeline_overview_links_phase_c(client, tmp_path, monkeypatch):
    # Build minimal trees so the overview renders without crashing.
    runs = tmp_path / "runs"
    monkeypatch.setattr(dashboard, "RUNS_DIR", runs)
    monkeypatch.setattr(dashboard, "PROJECT_ROOT", tmp_path / "project")
    (runs / "athens_night_1").mkdir(parents=True)
    r = client.get("/admin/tonight?night=1", auth=ADMIN_AUTH)
    assert r.status_code == 200
    assert "/admin/tonight/researcher?night=1" in r.text
    assert "/admin/tonight/provocateur?night=1" in r.text
    assert "/admin/tonight/publish?night=1" in r.text
