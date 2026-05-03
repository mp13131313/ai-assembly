"""Tests for flows/editor/routing.py — Stage 1 deterministic theme routing.

Validates Cases A/B/C/D classifier against synthetic Step 2 artifacts +
provocateur briefings. Edge cases: hybrid synthesis-anchored
("synthesise around Response 2..."), refusal markers, missing briefings.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_RUNTIME_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_RUNTIME_ROOT))

from flows.editor import routing  # noqa: E402


def _write_step2_artifact(run_dir: Path, voice_slug: str, *, focus_decision: str,
                          themes_covered: list[str], council_member: str = "") -> None:
    p = run_dir / "04_voice" / "step2_first_draft_artifacts" / f"{voice_slug}.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({
        "lineage": {
            "voice_slug": voice_slug,
            "themes_covered": themes_covered,
        },
        "council_member": council_member or voice_slug.title(),
        "focus_decision": focus_decision,
        "selected_form": "test_form",
        "artifact_text": f"<artifact for {voice_slug}>",
    }))


def _write_briefing(run_dir: Path, voice_slug: str, theme_ids_in_order: list[str]) -> None:
    """Mock briefing where formulations[i].theme_id = theme_ids_in_order[i]."""
    p = run_dir / "03_provocateur" / "briefings" / f"{voice_slug}.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({
        "formulations": [
            {
                "theme_id": tid,
                "theme_display_title": tid.replace("_", " ").title(),
                "mode": "question",
                "narrative_briefing": f"<briefing for {voice_slug} on {tid}>",
                "full_theme_record": {
                    "theme_title_from_researcher": tid,
                    "theme_abstract_from_researcher": f"<abstract for {tid}>",
                    "clusters": [],
                    "theme_flags": {},
                },
            }
            for tid in theme_ids_in_order
        ]
    }))


@pytest.fixture
def run_dir(tmp_path: Path) -> Path:
    rd = tmp_path / "athens_night_1"
    rd.mkdir()
    return rd


# --- Case A: explicit Response N anchor ----------------------------------


def test_case_a_focus_on_response_n(run_dir):
    """Plato's 'Focus on Response 3.' → 3rd theme_id in briefings."""
    _write_step2_artifact(run_dir, "plato",
                          focus_decision="Focus on Response 3.",
                          themes_covered=["theme_001", "theme_002", "theme_003"])
    _write_briefing(run_dir, "plato", ["theme_005", "theme_001", "theme_009"])
    manifest = routing.route_themes(run_dir, night=1)
    plato = next(v for v in manifest["voices_routing"] if v["voice_slug"] == "plato")
    assert plato["primary_theme"] == "theme_009"  # 3rd in briefings
    assert "Case A" in plato["primary_theme_source"]


def test_case_a_synthesis_anchored(run_dir):
    """Dostoevsky's 'synthesise around Response 2's threshold-scene' →
    Case A still wins (Response N anchor anywhere in text)."""
    _write_step2_artifact(run_dir, "dostoevsky",
                          focus_decision="synthesise around Response 2's threshold-scene",
                          themes_covered=["theme_001", "theme_002", "theme_003"])
    _write_briefing(run_dir, "dostoevsky", ["theme_001", "theme_002", "theme_003"])
    manifest = routing.route_themes(run_dir, night=1)
    dost = next(v for v in manifest["voices_routing"] if v["voice_slug"] == "dostoevsky")
    assert dost["primary_theme"] == "theme_002"  # 2nd briefing, not lowest-numbered
    assert "Case A" in dost["primary_theme_source"]


def test_case_a_lowercase_response(run_dir):
    """Battuta's 'Focus on response 2 (...)' — case-insensitive regex."""
    _write_step2_artifact(run_dir, "battuta",
                          focus_decision="Focus on response 2 (algorithmic governance)",
                          themes_covered=["theme_001", "theme_002"])
    _write_briefing(run_dir, "battuta", ["theme_001", "theme_002"])
    manifest = routing.route_themes(run_dir, night=1)
    bat = next(v for v in manifest["voices_routing"] if v["voice_slug"] == "battuta")
    assert bat["primary_theme"] == "theme_002"


def test_case_a_response_n_out_of_range(run_dir):
    """If Response N exceeds briefing count, fall through to synthesis or
    Case 3. (Defensive — shouldn't happen if briefings are well-formed.)"""
    _write_step2_artifact(run_dir, "plato",
                          focus_decision="Focus on Response 5.",
                          themes_covered=["theme_001", "theme_002"])
    _write_briefing(run_dir, "plato", ["theme_001", "theme_002"])
    manifest = routing.route_themes(run_dir, night=1)
    plato = next(v for v in manifest["voices_routing"] if v["voice_slug"] == "plato")
    # Falls through to Case 3 (lowest-numbered)
    assert plato["primary_theme"] == "theme_001"


# --- Case C: pure synthesis ----------------------------------------------


def test_case_c_pure_synthesise(run_dir):
    """Cleopatra's 'Synthesise.' → mechanical lowest-numbered tiebreaker."""
    _write_step2_artifact(run_dir, "cleopatra",
                          focus_decision="Synthesise.",
                          themes_covered=["theme_003", "theme_002", "theme_001"])
    _write_briefing(run_dir, "cleopatra", ["theme_003", "theme_002", "theme_001"])
    manifest = routing.route_themes(run_dir, night=1)
    cleo = next(v for v in manifest["voices_routing"] if v["voice_slug"] == "cleopatra")
    assert cleo["primary_theme"] == "theme_001"  # lowest-numbered
    assert "Case 2" in cleo["primary_theme_source"]


# --- Refusal -------------------------------------------------------------


def test_refusal_empty_themes_covered(run_dir):
    _write_step2_artifact(run_dir, "ghost",
                          focus_decision="—",
                          themes_covered=[])
    manifest = routing.route_themes(run_dir, night=1)
    assert all(v["voice_slug"] != "ghost" for v in manifest["voices_routing"])
    assert any(r["voice_slug"] == "ghost" for r in manifest["refusals"])


def test_refusal_marker(run_dir):
    _write_step2_artifact(run_dir, "river",
                          focus_decision="silence — the river declines to receive",
                          themes_covered=["theme_001"])
    manifest = routing.route_themes(run_dir, night=1)
    assert all(v["voice_slug"] != "river" for v in manifest["voices_routing"])
    assert any(r["voice_slug"] == "river" for r in manifest["refusals"])


# --- Multi-voice routing -------------------------------------------------


def test_multi_voice_routing_groups(run_dir):
    """Three voices, two themes — themes_to_dossiers reflects engagement counts."""
    _write_step2_artifact(run_dir, "v1", focus_decision="Focus on Response 1",
                          themes_covered=["theme_a"])
    _write_step2_artifact(run_dir, "v2", focus_decision="Focus on Response 1",
                          themes_covered=["theme_a"])
    _write_step2_artifact(run_dir, "v3", focus_decision="Focus on Response 1",
                          themes_covered=["theme_b"])
    _write_briefing(run_dir, "v1", ["theme_a"])
    _write_briefing(run_dir, "v2", ["theme_a"])
    _write_briefing(run_dir, "v3", ["theme_b"])

    manifest = routing.route_themes(run_dir, night=1)

    # theme_a has 2 voices, theme_b has 1 → theme_a leads
    assert manifest["themes_to_dossiers"][0]["theme_id"] == "theme_a"
    assert manifest["themes_to_dossiers"][0]["n_engaged_voices"] == 2
    assert manifest["themes_to_dossiers"][1]["theme_id"] == "theme_b"
    assert manifest["themes_to_dossiers"][1]["n_engaged_voices"] == 1


# --- Issue numbering -----------------------------------------------------


def test_issue_no_per_night(run_dir):
    _write_step2_artifact(run_dir, "v1", focus_decision="Focus on Response 1",
                          themes_covered=["theme_a"])
    _write_briefing(run_dir, "v1", ["theme_a"])
    m1 = routing.route_themes(run_dir, night=1)
    m2 = routing.route_themes(run_dir, night=2)
    m3 = routing.route_themes(run_dir, night=3)
    assert m1["issue_no"] == 42_193
    assert m2["issue_no"] == 42_194
    assert m3["issue_no"] == 42_195
    assert m3["vol"] == "CXVI"


# --- write_routing_manifest writes to disk -------------------------------


def test_write_routing_manifest_writes(run_dir):
    _write_step2_artifact(run_dir, "v1", focus_decision="Focus on Response 1",
                          themes_covered=["theme_a"])
    _write_briefing(run_dir, "v1", ["theme_a"])
    manifest = routing.write_routing_manifest(run_dir, night=1)
    out_path = run_dir / "05_editor" / "theme_routing.json"
    assert out_path.exists()
    on_disk = json.loads(out_path.read_text())
    assert on_disk == manifest
    assert on_disk["schema_version"] == "1.0"
