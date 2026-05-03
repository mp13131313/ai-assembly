"""End-to-end test for editor_flow.py with mocked Anthropic.

Covers:
  - card_assembly: load + assemble system prompt; (prefix, tail) shape;
    drops smoke_test_chains + metadata + reference_only_passages
  - publish: write_dossier writes both copies; load_prior_editions
    trims to articles only; empty on Night 1
  - editor_flow.run_editor_pipeline: full Stage 1 + Stage 2 + manifest
    against synthetic run_dir + stub Claudia card with mocked Anthropic
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

_RUNTIME_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_RUNTIME_ROOT))

from flows.editor import card_assembly, dossier_generation, publish  # noqa: E402
from flows.editor import routing  # noqa: E402


FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"
STUB_CARD_PATH = FIXTURES_DIR / "claudia_pinchbeck_stub.json"


# --- card_assembly -------------------------------------------------------


def test_load_editor_card_missing_raises(tmp_path):
    """resolve_project_root + path miss → FileNotFoundError with clear message."""
    with pytest.raises(FileNotFoundError, match="Editor card not found"):
        card_assembly.load_editor_card(project_root=tmp_path)


def test_assemble_system_prompt_returns_tuple():
    card = json.loads(STUB_CARD_PATH.read_text())
    prefix, tail = card_assembly.assemble_system_prompt(card)
    assert isinstance(prefix, str) and isinstance(tail, str)
    assert "Claudia Pinchbeck" in prefix
    assert "IDENTITY" in prefix
    assert "CONSTITUTION" in prefix
    assert "BOUNDARIES" in prefix


def test_assemble_drops_metadata_and_smoke_tests():
    """metadata + smoke_test_chains are always-drop; their VALUES must not
    appear in the rendered card. (The closing prompt may mention field
    NAMES; we check for the stub VALUES instead.)"""
    card = json.loads(STUB_CARD_PATH.read_text())
    prefix, tail = card_assembly.assemble_system_prompt(card)
    rendered = prefix + tail
    # Stub card has metadata._note marker; should not render
    assert "STUB CARD for editor_flow smoke tests" not in rendered


def test_assemble_includes_engagement_two_fields_only():
    """v2: editor's ENGAGEMENT renders default_questions +
    disagreement_protocol only; unique_contribution VALUE must not appear
    in the rendered card (the closing prompt may name the field)."""
    card = json.loads(STUB_CARD_PATH.read_text())
    # Add a unique_contribution VALUE that must not appear in the render
    sentinel_value = "SENTINEL-UNIQUE-CONTRIBUTION-XYZ"
    card_with_uc = {**card, "unique_contribution": sentinel_value}
    prefix, tail = card_assembly.assemble_system_prompt(card_with_uc)
    rendered = prefix + tail
    # The VALUE must not be rendered (proves the field wasn't included)
    assert sentinel_value not in rendered
    # Engagement fields that ARE in scope should render their VALUES
    assert "default_questions" in tail   # field-name OR value reference is fine
    assert "disagreement_protocol" in tail


# --- publish -------------------------------------------------------------


def test_write_dossier_writes_both_copies(tmp_path):
    run_dir = tmp_path / "athens_night_1"
    project_root = tmp_path / "project"
    dossier = {"schema_version": "2.0", "kicker": "K", "headline": "H"}
    run_path, pub_path = publish.write_dossier(
        dossier, run_dir=run_dir, project_root=project_root,
        night=1, dossier_no=1,
    )
    assert run_path.exists()
    assert pub_path.exists()
    assert json.loads(run_path.read_text()) == dossier
    assert json.loads(pub_path.read_text()) == dossier


def test_load_prior_editions_empty_on_night_1(tmp_path):
    assert publish.load_prior_editions(tmp_path, night=1) == []


def test_load_prior_editions_trims_to_articles(tmp_path):
    """Prior dossier JSON has many fields; load_prior_editions returns
    only kicker + headline + body_paragraphs."""
    pr = tmp_path / "project"
    pub_dir = pr / "published_artifacts" / "dossiers" / "night_1"
    pub_dir.mkdir(parents=True)
    full_dossier = {
        "schema_version": "2.0",
        "kicker": "K",
        "headline": "H",
        "subline": "S",
        "body_paragraphs": ["p1", "p2"],
        "headnotes": [{"voice_slug": "plato", "voice_name": "Plato"}],
        "front_abstract": "FA",
        "colophon": "...",
        "metadata": {"issue_no": 42_193, "vol": "CXVI"},
    }
    (pub_dir / "dossier_001.json").write_text(json.dumps(full_dossier))

    prior = publish.load_prior_editions(pr, night=2)
    assert len(prior) == 1
    assert prior[0]["night"] == 1
    assert prior[0]["issue_no"] == 42_193
    assert len(prior[0]["dossiers"]) == 1
    trimmed = prior[0]["dossiers"][0]
    assert set(trimmed.keys()) == {"kicker", "headline", "body_paragraphs"}
    assert trimmed["kicker"] == "K"
    assert trimmed["body_paragraphs"] == ["p1", "p2"]


# --- end-to-end editor_flow ----------------------------------------------


def _setup_run_dir(tmp_path: Path, voice_slugs: list[str], theme_id: str = "theme_001") -> Path:
    """Build a synthetic run_dir with K voices' briefings + Step 2 artifacts."""
    run_dir = tmp_path / "athens_night_1"
    for slug in voice_slugs:
        bp = run_dir / "03_provocateur" / "briefings" / f"{slug}.json"
        bp.parent.mkdir(parents=True, exist_ok=True)
        bp.write_text(json.dumps({
            "formulations": [{
                "theme_id": theme_id,
                "theme_display_title": "Test Theme",
                "mode": "question",
                "narrative_briefing": f"<{slug} briefing>",
                "full_theme_record": {
                    "theme_title_from_researcher": "T",
                    "theme_abstract_from_researcher": "A",
                    "clusters": [],
                    "theme_flags": {},
                },
            }]
        }))
        ap = run_dir / "04_voice" / "step2_first_draft_artifacts" / f"{slug}.json"
        ap.parent.mkdir(parents=True, exist_ok=True)
        ap.write_text(json.dumps({
            "lineage": {"voice_slug": slug, "themes_covered": [theme_id]},
            "council_member": slug.title(),
            "focus_decision": "Focus on Response 1.",
            "artifact_text": f"<{slug} artifact>",
        }))
    return run_dir


def test_editor_flow_end_to_end_mocked(tmp_path, monkeypatch):
    """Mock Anthropic call; verify Stage 1 routing writes theme_routing.json,
    Stage 2 writes per-dossier files + run_dir + published copies, manifest
    records counts."""
    project_root = tmp_path / "project"
    project_root.mkdir()
    # Stage Claudia's stub card under PROJECT_ROOT
    editor_dir = project_root / "editor" / "claudia_pinchbeck"
    editor_dir.mkdir(parents=True)
    (editor_dir / "07_persona_card_assembled.json").write_text(STUB_CARD_PATH.read_text())

    run_dir = _setup_run_dir(tmp_path, ["plato", "cleopatra"], theme_id="theme_001")

    mock_response = """**kicker:** TEST KICKER
**headline:** Test Headline
**subline:** Test deck
**body_paragraphs:**
First.

Second.

**headnotes:**
voice_slug: plato
framing_text: F-plato
voice_slug: cleopatra
framing_text: F-cleopatra

**front_abstract:** Test abstract.
"""
    mock_usage = MagicMock(input_tokens=1, output_tokens=1,
                           cache_creation_input_tokens=0, cache_read_input_tokens=0)
    mock_final = MagicMock(usage=mock_usage)
    monkeypatch.setattr(dossier_generation, "stream_voice_call",
                        lambda *a, **kw: (mock_response, "", mock_final, 0))

    # Also mock Anthropic() to avoid API key requirement
    monkeypatch.setattr("anthropic.Anthropic", lambda *a, **kw: MagicMock())

    from flows.editor_flow import run_editor_pipeline
    manifest = run_editor_pipeline(run_dir, night=1, project_root=project_root)

    # Stage 1 wrote routing
    routing_path = run_dir / "05_editor" / "theme_routing.json"
    assert routing_path.exists()
    routing_data = json.loads(routing_path.read_text())
    assert len(routing_data["voices_routing"]) == 2
    assert len(routing_data["themes_to_dossiers"]) == 1

    # Stage 2 wrote dossier file (run_dir + published)
    dossier_path = run_dir / "05_editor" / "dossiers" / "dossier_001.json"
    assert dossier_path.exists()
    pub_path = project_root / "published_artifacts" / "dossiers" / "night_1" / "dossier_001.json"
    assert pub_path.exists()

    dossier = json.loads(dossier_path.read_text())
    assert dossier["kicker"] == "TEST KICKER"
    assert len(dossier["headnotes"]) == 2
    assert dossier["metadata"]["issue_no"] == 42_193

    # Manifest counts
    assert manifest["counts"]["dossiers_succeeded"] == 1
    assert manifest["counts"]["dossiers_failed"] == 0
    assert manifest["pipeline"] == "editor"
    assert manifest["schema_version"] == "2.0"


def test_editor_flow_handles_failed_dossier(tmp_path, monkeypatch):
    """If one dossier fails (e.g. Anthropic error), other dossiers proceed,
    manifest records the failure."""
    project_root = tmp_path / "project"
    project_root.mkdir()
    editor_dir = project_root / "editor" / "claudia_pinchbeck"
    editor_dir.mkdir(parents=True)
    (editor_dir / "07_persona_card_assembled.json").write_text(STUB_CARD_PATH.read_text())

    # Two themes, one voice each
    run_dir = tmp_path / "athens_night_1"
    for tid, slug in (("theme_001", "v1"), ("theme_002", "v2")):
        bp = run_dir / "03_provocateur" / "briefings" / f"{slug}.json"
        bp.parent.mkdir(parents=True, exist_ok=True)
        bp.write_text(json.dumps({
            "formulations": [{
                "theme_id": tid, "theme_display_title": "T", "mode": "question",
                "narrative_briefing": "<x>",
                "full_theme_record": {
                    "theme_title_from_researcher": "T",
                    "theme_abstract_from_researcher": "A",
                    "clusters": [], "theme_flags": {},
                },
            }]
        }))
        ap = run_dir / "04_voice" / "step2_first_draft_artifacts" / f"{slug}.json"
        ap.parent.mkdir(parents=True, exist_ok=True)
        ap.write_text(json.dumps({
            "lineage": {"voice_slug": slug, "themes_covered": [tid]},
            "council_member": slug.upper(),
            "focus_decision": "Focus on Response 1.",
            "artifact_text": "<x>",
        }))

    call_count = {"n": 0}

    def fake_call(*args, **kwargs):
        call_count["n"] += 1
        # First call (whichever dossier) fails; second succeeds
        if call_count["n"] == 1:
            raise RuntimeError("simulated anthropic failure")
        mock_usage = MagicMock(input_tokens=1, output_tokens=1,
                               cache_creation_input_tokens=0, cache_read_input_tokens=0)
        return ("**kicker:** OK\n**headline:** OK\n**body_paragraphs:**\np1\n",
                "", MagicMock(usage=mock_usage), 0)

    monkeypatch.setattr(dossier_generation, "stream_voice_call", fake_call)
    monkeypatch.setattr("anthropic.Anthropic", lambda *a, **kw: MagicMock())

    from flows.editor_flow import run_editor_pipeline
    manifest = run_editor_pipeline(run_dir, night=1, project_root=project_root)

    assert manifest["counts"]["dossiers_failed"] == 1
    assert manifest["counts"]["dossiers_succeeded"] == 1
    assert len(manifest["dossier_failures"]) == 1
