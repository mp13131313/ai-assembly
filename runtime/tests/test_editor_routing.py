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


def test_case_b_single_response_session(run_dir):
    """Voice received only one Step 1 output → wrote 'Single focus on this
    response' / 'Focus on the single response' instead of 'Response 1'.
    Routes cleanly to the single themes_covered entry, no fall-through
    warning."""
    _write_step2_artifact(run_dir, "octopus",
                          focus_decision="Single focus on this response.",
                          themes_covered=["theme_004"])
    _write_briefing(run_dir, "octopus", ["theme_004"])
    manifest = routing.route_themes(run_dir, night=1)
    o = next(v for v in manifest["voices_routing"] if v["voice_slug"] == "octopus")
    assert o["primary_theme"] == "theme_004"
    assert "Case B" in o["primary_theme_source"]


def test_case_b_single_response_alt_phrasing(run_dir):
    """Alternative phrasing 'Focus on the single response' also matches."""
    _write_step2_artifact(run_dir, "river",
                          focus_decision="Focus on the single response.",
                          themes_covered=["theme_003"])
    _write_briefing(run_dir, "river", ["theme_003"])
    manifest = routing.route_themes(run_dir, night=1)
    r = next(v for v in manifest["voices_routing"] if v["voice_slug"] == "river")
    assert r["primary_theme"] == "theme_003"
    assert "Case B" in r["primary_theme_source"]


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


def test_case_c_pure_synthesise_no_client_falls_back(run_dir):
    """Cleopatra's 'Synthesise.' with no synthesis_client → fallback path
    (lowest-numbered tiebreaker). Mirrors the unit-test path where the
    LLM router isn't wired up."""
    _write_step2_artifact(run_dir, "cleopatra",
                          focus_decision="Synthesise.",
                          themes_covered=["theme_003", "theme_002", "theme_001"])
    _write_briefing(run_dir, "cleopatra", ["theme_003", "theme_002", "theme_001"])
    manifest = routing.route_themes(run_dir, night=1)
    cleo = next(v for v in manifest["voices_routing"] if v["voice_slug"] == "cleopatra")
    assert cleo["primary_theme"] == "theme_001"  # lowest-numbered fallback
    assert "Case 2" in cleo["primary_theme_source"]
    assert "no router available" in cleo["primary_theme_source"].lower()


def test_case_c_pure_synthesise_with_router_picks(run_dir):
    """When a synthesis_client is supplied, the router decides instead of
    lowest-numbered. Mock the Anthropic call to return theme_002."""
    from unittest.mock import MagicMock

    _write_step2_artifact(run_dir, "cleopatra",
                          focus_decision="Synthesise across all three.",
                          themes_covered=["theme_003", "theme_002", "theme_001"])
    _write_briefing(run_dir, "cleopatra", ["theme_003", "theme_002", "theme_001"])

    fake_block = MagicMock(type="text", text=(
        "chosen_theme_id: theme_002\n"
        "rationale: the artifact's central reframing turns on theme_002's seal/body distinction."
    ))
    fake_message = MagicMock(content=[fake_block])
    fake_client = MagicMock()
    fake_client.messages.create.return_value = fake_message

    manifest = routing.route_themes(run_dir, night=1, synthesis_client=fake_client)
    cleo = next(v for v in manifest["voices_routing"] if v["voice_slug"] == "cleopatra")
    assert cleo["primary_theme"] == "theme_002"
    assert "LLM-routed" in cleo["primary_theme_source"]
    assert "seal/body" in cleo["primary_theme_source"]
    fake_client.messages.create.assert_called_once()


def test_case_c_synthesise_router_unknown_theme_falls_back(run_dir):
    """If router returns a theme_id not in candidates, fall back to
    lowest-numbered with explanatory rationale."""
    from unittest.mock import MagicMock

    _write_step2_artifact(run_dir, "cleopatra",
                          focus_decision="Synthesise.",
                          themes_covered=["theme_003", "theme_002", "theme_001"])
    _write_briefing(run_dir, "cleopatra", ["theme_003", "theme_002", "theme_001"])

    fake_block = MagicMock(type="text", text="chosen_theme_id: theme_999\nrationale: bogus")
    fake_message = MagicMock(content=[fake_block])
    fake_client = MagicMock()
    fake_client.messages.create.return_value = fake_message

    manifest = routing.route_themes(run_dir, night=1, synthesis_client=fake_client)
    cleo = next(v for v in manifest["voices_routing"] if v["voice_slug"] == "cleopatra")
    assert cleo["primary_theme"] == "theme_001"  # lowest-numbered fallback
    assert "unknown theme_id" in cleo["primary_theme_source"]


def test_case_c_synthesise_single_theme_skips_llm(run_dir):
    """Synthesis voice covering only ONE theme — no choice to make, skip
    the LLM call entirely. The synthesis_client should NOT be invoked."""
    from unittest.mock import MagicMock

    _write_step2_artifact(run_dir, "cleopatra",
                          focus_decision="Synthesise.",
                          themes_covered=["theme_005"])
    _write_briefing(run_dir, "cleopatra", ["theme_005"])

    fake_client = MagicMock()
    manifest = routing.route_themes(run_dir, night=1, synthesis_client=fake_client)
    cleo = next(v for v in manifest["voices_routing"] if v["voice_slug"] == "cleopatra")
    assert cleo["primary_theme"] == "theme_005"
    assert "single theme" in cleo["primary_theme_source"].lower()
    fake_client.messages.create.assert_not_called()


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
