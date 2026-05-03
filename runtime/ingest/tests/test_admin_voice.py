"""Tests for the /admin/tonight/voice drilldown (C23 Phase B, 2026-05-03).

Covers:
  * dashboard helpers (voice_step1_grid, voice_validation_grid,
    voice_step2_list, voice_continuity_list, collect_voice_detail)
    against synthetic 04_voice/ trees
  * route auth gating (/admin/tonight/voice + /admin/tonight/voice.json)
  * happy-path render with multiple voices × themes
  * empty-state render when run_dir doesn't exist
  * validation grid renders when validation files present
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest
from starlette.testclient import TestClient

# Required env BEFORE importing ingest.app (validated at lifespan).
os.environ.setdefault("UPLOAD_APP_PASSWORD", "testpw")
os.environ.setdefault("ADMIN_APP_PASSWORD", "admin_pw")
os.environ.setdefault("ANTHROPIC_API_KEY", "test")
os.environ.setdefault("ASSEMBLYAI_API_KEY", "test")

REPO = Path(__file__).resolve().parent.parent.parent
FAKE_FLOW = REPO / "ingest" / "tests" / "fake_transcription_flow.py"
import shlex as _shlex  # noqa: E402
os.environ["INGEST_FLOW_CMD"] = _shlex.join([sys.executable, str(FAKE_FLOW)])
os.environ["FAKE_DELAY_SECONDS"] = "1"

# Pin in case load_dotenv overrode.
os.environ["UPLOAD_APP_PASSWORD"] = "testpw"
os.environ["ADMIN_APP_PASSWORD"] = "admin_pw"

from ingest.app import app  # noqa: E402
from ingest import dashboard, pipeline  # noqa: E402

ADMIN_AUTH = ("admin", "admin_pw")
PRODUCER_AUTH = ("producer", "testpw")


# --- Synthetic-tree builders ------------------------------------------------


def _write(p: Path, payload: dict) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(payload), encoding="utf-8")


def _build_synthetic_voice_run(
    run_dir: Path,
    voices: list[str],
    themes: list[str],
    *,
    with_validation: bool = False,
    with_step2: bool = True,
) -> None:
    """Build a fake 04_voice/ tree under run_dir."""
    s1_dir = run_dir / "04_voice" / "step1_detailed_responses"
    for v in voices:
        for t in themes:
            _write(s1_dir / f"{v}__{t}.json", {
                "lineage": {"voice_slug": v, "theme_id": t, "night": 1},
                "council_member": v.title(),
                "theme_display_title": f"Title for {t}",
                "mode": "question",
                "model": "claude-opus-4-7",
                "input_tokens": 1000, "output_tokens": 5000,
                "thinking_tokens": 3000, "wall_clock_s": 90.5,
            })

    if with_validation:
        v_dir = run_dir / "04_voice" / "validation"
        for v in voices:
            for t in themes:
                _write(v_dir / f"{v}__{t}.json", {
                    "anachronism": {"status": "PASS", "text": "PASS",
                                    "model": "gpt-5.4", "wall_clock_s": 5.0},
                    "constitution": {"status": "PASS", "text": "PASS",
                                     "model": "gpt-5.4", "wall_clock_s": 5.0},
                    "regen_count": 0,
                    "final_status": "clean",
                })

    if with_step2:
        s2_dir = run_dir / "04_voice" / "step2_first_draft_artifacts"
        for v in voices:
            _write(s2_dir / f"{v}.json", {
                "lineage": {"voice_slug": v, "themes_covered": themes, "night": 1},
                "council_member": v.title(),
                "focus_decision": "Synthesise.",
                "focus_rationale": "synthesised across themes",
                "stance": "obsession",
                "stance_rationale": "the matter pressed",
                "selected_form": "dialogue",
                "form_rationale": "native to the voice",
                "artifact_text": "...",
                "word_count": 487,
                "model": "claude-opus-4-7",
                "input_tokens": 41000, "output_tokens": 6500,
                "thinking_tokens": 4500, "wall_clock_s": 125.3,
            })

    _write(run_dir / "04_voice" / "manifest.json", {
        "pipeline": "voice", "pipeline_version": "v2",
        "night": 1, "run_id": run_dir.name,
        "model": "claude-opus-4-7", "thinking_enabled": True,
        "voices_processed": voices,
        "counts": {
            "step1_pairs_attempted": len(voices) * len(themes),
            "step1_pairs_succeeded": len(voices) * len(themes),
            "step2_voices_succeeded": len(voices) if with_step2 else 0,
            "step3_voices_succeeded": 0,
            "continuity_voices_succeeded": 0,
            "validation_flagged": 0,
        },
        "validation_failures": [],
        "publish_summary": {},
        "wall_clock_s": 600,
        "config": {},
    })


# --- Helper-level tests -----------------------------------------------------


def test_voice_step1_grid_synthetic(tmp_path: Path):
    run_dir = tmp_path / "athens_night_1"
    _build_synthetic_voice_run(
        run_dir, voices=["plato", "arendt", "octopus"],
        themes=["theme_001", "theme_002", "theme_003", "theme_004"],
    )
    cells = dashboard.voice_step1_grid(run_dir)
    assert len(cells) == 12  # 3 × 4
    cell = cells[0]
    assert cell["voice_slug"]
    assert cell["theme_id"]
    assert cell["state"] == "done"
    assert cell["input_tokens"] == 1000
    assert cell["wall_clock_s"] == 90.5


def test_voice_validation_grid_synthetic(tmp_path: Path):
    run_dir = tmp_path / "athens_night_1"
    _build_synthetic_voice_run(
        run_dir, voices=["plato"], themes=["theme_001", "theme_002"],
        with_validation=True,
    )
    cells = dashboard.voice_validation_grid(run_dir)
    assert len(cells) == 2
    assert cells[0]["anachronism_status"] == "PASS"
    assert cells[0]["constitution_status"] == "PASS"
    assert cells[0]["final_status"] == "clean"


def test_voice_step2_list_synthetic(tmp_path: Path):
    run_dir = tmp_path / "athens_night_1"
    _build_synthetic_voice_run(
        run_dir, voices=["plato", "arendt"], themes=["theme_001"],
    )
    voices = dashboard.voice_step2_list(run_dir)
    assert len(voices) == 2
    v = voices[0]
    assert v["focus_decision"] == "Synthesise."
    assert v["stance"] == "obsession"
    assert v["selected_form"] == "dialogue"
    assert v["word_count"] == 487


def test_voice_continuity_list_writes_per_voice(tmp_path: Path):
    """Continuity list reflects per-voice continuity_night_<N+1>.json existence."""
    project_root = tmp_path / "project"
    voices = ["plato", "arendt"]
    # Plato has continuity for next night; Arendt doesn't yet.
    _write(project_root / "voices" / "plato" / "continuity_night_2.json",
           {"voice_slug": "plato", "for_night": 2,
            "continuity_block_if_night_2": "...",
            "continuity_block_artifact_if_night_2": "..."})
    cont = dashboard.voice_continuity_list(project_root, night=1, voice_slugs=voices)
    by_slug = {c["voice_slug"]: c for c in cont}
    assert by_slug["plato"]["written"] is True
    assert by_slug["arendt"]["written"] is False


def test_voice_continuity_list_skipped_on_night_3(tmp_path: Path):
    project_root = tmp_path / "project"
    cont = dashboard.voice_continuity_list(
        project_root, night=3, voice_slugs=["plato"],
    )
    assert cont[0]["skipped_last_night"] is True
    assert cont[0]["written"] is False


def test_collect_voice_detail_empty(tmp_path: Path, monkeypatch):
    """No run_dir — payload returns empty lists, run_exists=False."""
    monkeypatch.setattr(dashboard, "RUNS_DIR", tmp_path / "runs")
    payload = dashboard.collect_voice_detail(1)
    assert payload["run_exists"] is False
    assert payload["voices"] == []
    assert payload["step1_cells"] == []


def test_collect_voice_detail_full(tmp_path: Path, monkeypatch):
    """Full happy path: voices + themes + Step 1 cells assemble correctly."""
    runs_dir = tmp_path / "runs"
    monkeypatch.setattr(dashboard, "RUNS_DIR", runs_dir)
    monkeypatch.setattr(dashboard, "PROJECT_ROOT", tmp_path / "project")
    run_dir = runs_dir / "athens_night_1"
    _build_synthetic_voice_run(
        run_dir, voices=["plato", "arendt"], themes=["theme_001", "theme_002"],
    )
    payload = dashboard.collect_voice_detail(1)
    assert payload["run_exists"] is True
    assert {v["voice_slug"] for v in payload["voices"]} == {"plato", "arendt"}
    assert {t["theme_id"] for t in payload["themes"]} == {"theme_001", "theme_002"}
    assert len(payload["step1_cells"]) == 4
    assert len(payload["step2_voices"]) == 2
    assert payload["manifest"]["counts"]["step1_pairs_succeeded"] == 4


# --- Route auth tests -------------------------------------------------------


@pytest.fixture
def client(tmp_path: Path, monkeypatch) -> TestClient:
    tmp_runs = tmp_path / "runs"
    monkeypatch.setattr(pipeline, "RUNS_DIR", tmp_runs)
    monkeypatch.setattr(dashboard, "RUNS_DIR", tmp_runs)
    monkeypatch.setattr(dashboard, "PROJECT_ROOT", tmp_path / "project")
    from ingest import sessions as sessions_mod
    monkeypatch.setattr(sessions_mod, "RUNS_DIR", tmp_runs)
    from ingest import auth as auth_mod
    auth_mod._failures.clear()
    with TestClient(app) as c:
        yield c


def test_voice_route_admin_only(client: TestClient):
    r_p = client.get("/admin/tonight/voice", auth=PRODUCER_AUTH)
    assert r_p.status_code == 403
    r_a = client.get("/admin/tonight/voice", auth=ADMIN_AUTH)
    assert r_a.status_code == 200


def test_voice_json_admin_only(client: TestClient):
    r_p = client.get("/admin/tonight/voice.json", auth=PRODUCER_AUTH)
    assert r_p.status_code == 403
    r_a = client.get("/admin/tonight/voice.json", auth=ADMIN_AUTH)
    assert r_a.status_code == 200


def test_voice_route_empty_state(client: TestClient):
    """No run_dir → empty-state HTML (no crash)."""
    r = client.get("/admin/tonight/voice?night=1", auth=ADMIN_AUTH)
    assert r.status_code == 200
    # Empty-state copy from template:
    assert "No run directory for Night" in r.text


def test_voice_json_empty_state(client: TestClient):
    r = client.get("/admin/tonight/voice.json?night=1", auth=ADMIN_AUTH)
    assert r.status_code == 200
    payload = r.json()
    assert payload["run_exists"] is False
    assert payload["voices"] == []


def test_voice_route_full_render(client: TestClient, tmp_path: Path, monkeypatch):
    """Build a real voice tree and render the full template against it."""
    tmp_runs = tmp_path / "runs2"
    monkeypatch.setattr(dashboard, "RUNS_DIR", tmp_runs)
    monkeypatch.setattr(dashboard, "PROJECT_ROOT", tmp_path / "project2")
    run_dir = tmp_runs / "athens_night_1"
    _build_synthetic_voice_run(
        run_dir,
        voices=["plato", "arendt", "octopus"],
        themes=["theme_001", "theme_002", "theme_003"],
        with_validation=True,
    )
    r = client.get("/admin/tonight/voice?night=1", auth=ADMIN_AUTH)
    assert r.status_code == 200
    body = r.text
    # All voices and themes appear:
    for v in ("plato", "arendt", "octopus"):
        assert v in body
    for t in ("theme_001", "theme_002", "theme_003"):
        assert t in body
    # Section headers from template (sentence-case per 2026-05-04
    # consistency pass — matches Researcher's "Node X — descriptor").
    assert "Step 1 — private reasoning" in body
    assert "Validation" in body
    assert "Step 2 — first-draft artifacts" in body
    assert "Continuity" in body
    # Validation cells rendered (PASS markers):
    assert "anachronism: PASS" in body
    assert "constitution: PASS" in body


def test_voice_invalid_night_falls_back(client: TestClient):
    r = client.get("/admin/tonight/voice.json?night=99", auth=ADMIN_AUTH)
    assert r.status_code == 200
    assert r.json()["night"] in (1, 2, 3)


def test_admin_tonight_links_to_voice(client: TestClient, tmp_path: Path, monkeypatch):
    """/admin/tonight stage row links to the voice drilldown when run_dir exists."""
    tmp_runs = tmp_path / "runs3"
    monkeypatch.setattr(dashboard, "RUNS_DIR", tmp_runs)
    monkeypatch.setattr(dashboard, "PROJECT_ROOT", tmp_path / "project3")
    run_dir = tmp_runs / "athens_night_1"
    _build_synthetic_voice_run(run_dir, voices=["plato"], themes=["theme_001"])
    r = client.get("/admin/tonight?night=1", auth=ADMIN_AUTH)
    assert r.status_code == 200
    assert "/admin/tonight/voice" in r.text
