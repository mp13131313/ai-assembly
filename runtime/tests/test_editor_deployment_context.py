"""Tests for editor deployment-context block + {night} substitution.

Branch: feature/editor-deployment-context.

Mirrors test_deployment_context.py (voice-side) for editor:
  - THE GATHERING + YOUR ROLE + THE PANEL appear in system prefix
  - Audience block intentionally NOT injected (Tim's card carries
    audience-calibration through register)
  - {night} substitutes correctly in voice_temporal_stance + anywhere
    else the placeholder appears
  - YOUR ROLE includes the editor-reconciling line (chrome carries
    voices' work without sanding edges; chrome holds three bars)
  - Graceful fallback when sources missing
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_RUNTIME_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_RUNTIME_ROOT / "flows"))

from editor.card_assembly import (  # noqa: E402
    _render_deployment_context,
    assemble_system_prompt,
)


# --- Fixtures ---------------------------------------------------------

CONFERENCE = {
    "conference_context_paragraph": (
        "The World Beautiful Business Forum is the 10th-anniversary "
        "flagship gathering... centre of gravity is agency..."
    ),
    "session_role_for_ai_assembly": (
        "The AIssembly takes the AI Democracy Marathon's night shift. "
        "Three bars in order: first, compelling enough... performing "
        "reception without being changed..."
    ),
}

COUNCIL = {
    "collective_landscape": (
        "Ten voices spanning roughly 2500 years of human thought... "
        "friction structure..."
    ),
    "audience": (
        "~750 attendees: senior professionals... well-curated openness "
        "is itself how they avoid being changed."
    ),
    "members": [
        {"name": "Voice of Plato"},
        {"name": "Voice of Cleopatra"},
    ],
}

# Minimal Tim card for assemble_system_prompt to render. {night} placeholder
# in voice_temporal_stance.default lets us assert substitution behavior.
MIN_CARD = {
    "council_member_name": "Tim Leberecht",
    "epistemic_frame_statement": "stub",
    "world": "stub",
    "formative_experience": "stub",
    "character": "stub",
    "constitution": "stub",
    "concept_lexicon": "stub",
    "curated_corpus_passages": [],
    "knowledge_boundary": "stub",
    "translation_protocol": "stub",
    "topics_requiring_care": "stub",
    "hard_limits": "stub",
    "voice_temporal_stance": {
        "default": (
            "You speak from the editor's desk at WBBF, overnight after "
            "Night {night}'s panels — May 2026."
        ),
        "anchored_override": None,
    },
    "reasoning_method": "stub",
    "default_questions": "stub",
    "rhetorical_mode": "stub",
    "characteristic_moves": "stub",
    "register_and_tone": "stub",
    "metaphorical_repertoire": "stub",
    "preferred_vocabulary": "stub",
    "banned_language": "stub",
    "banned_modes": "stub",
    "finds_compelling": "stub",
    "resists": "stub",
    "disagreement_protocol": "stub",
    "medium": "stub",
    "technical_capabilities": "stub",
    "characteristic_output_structure": "stub",
    "relationship_to_detailed_response": "stub",
    "aesthetic_qualities": "stub",
    "stance_tendency": "stub",
    "length_and_format_constraints": "stub",
    "quality_criteria": "stub",
}


# --- _render_deployment_context (unit tests) --------------------------

class TestRenderDeploymentContext:
    def test_gathering_present_when_conference_given(self):
        out = _render_deployment_context(COUNCIL, CONFERENCE)
        assert "## THE GATHERING" in out
        assert "World Beautiful Business Forum" in out

    def test_role_present_with_reconciling_line(self):
        out = _render_deployment_context(COUNCIL, CONFERENCE)
        assert "## YOUR ROLE" in out
        # The base session_role text
        assert "AI Democracy Marathon's night shift" in out
        # The reconciling line — Tim is the Editor, chrome carries without sanding
        assert "You are the Editor of this Assembly" in out
        assert "without sanding the edges off" in out
        assert "three bars" in out  # the chrome holds the same three bars

    def test_panel_present_when_council_given(self):
        out = _render_deployment_context(COUNCIL, CONFERENCE)
        assert "## THE PANEL" in out
        assert "Ten voices" in out

    def test_audience_NOT_injected(self):
        """Operator decision: Tim's card calibrates audience through
        register; deployment-context block does not include the audience
        text from council_config."""
        out = _render_deployment_context(COUNCIL, CONFERENCE)
        assert "## YOUR READERS" not in out
        assert "## THE READERS" not in out
        assert "well-curated openness" not in out  # audience text fragment

    def test_empty_when_no_sources(self):
        assert _render_deployment_context(None, None) == ""

    def test_partial_sources(self):
        only_conference = _render_deployment_context(None, CONFERENCE)
        assert "## THE GATHERING" in only_conference
        assert "## YOUR ROLE" in only_conference
        assert "## THE PANEL" not in only_conference

        only_council = _render_deployment_context(COUNCIL, None)
        assert "## THE GATHERING" not in only_council
        assert "## YOUR ROLE" not in only_council
        assert "## THE PANEL" in only_council


# --- assemble_system_prompt integration --------------------------------

class TestAssembleSystemPromptIntegration:
    def test_deployment_context_in_prefix(self):
        prefix, tail = assemble_system_prompt(
            MIN_CARD, night=1, council=COUNCIL, conference=CONFERENCE
        )
        assert "## THE GATHERING" in prefix
        assert "## YOUR ROLE" in prefix
        assert "## THE PANEL" in prefix
        assert "## THE GATHERING" not in tail

    def test_night_substitutes_in_temporal_stance(self):
        for n in (1, 2, 3):
            prefix, _ = assemble_system_prompt(
                MIN_CARD, night=n, council=COUNCIL, conference=CONFERENCE
            )
            assert f"Night {n}" in prefix
            assert "{night}" not in prefix
            assert "{night}" not in _

    def test_session_role_text_passes_through(self):
        prefix, _ = assemble_system_prompt(
            MIN_CARD, night=1, council=COUNCIL, conference=CONFERENCE
        )
        # session_role's anti-shallow + three-bars language present
        assert "performing reception without being changed" in prefix

    def test_no_deployment_when_sources_missing(self, monkeypatch):
        """Test fixtures without PROJECT_ROOT files should still produce
        a valid system prompt — deployment context degrades to empty."""
        from editor import card_assembly as ca

        def _raise_fnf(*a, **kw):
            raise FileNotFoundError("simulated missing source")

        monkeypatch.setattr(ca, "load_council_config", _raise_fnf)
        monkeypatch.setattr(ca, "load_conference_facts", _raise_fnf)

        prefix, tail = assemble_system_prompt(
            MIN_CARD, night=1, council=None, conference=None
        )
        assert "## THE GATHERING" not in prefix
        assert "## YOUR ROLE" not in prefix
        assert "## THE PANEL" not in prefix
        # But the prefix is still rendered
        assert len(prefix) > 100
        assert "Tim Leberecht" in prefix

    def test_invalid_night_raises(self):
        with pytest.raises(ValueError):
            assemble_system_prompt(MIN_CARD, night=4)

    def test_explicit_pass_overrides_loaders(self, monkeypatch):
        """Passing council/conference explicitly should bypass the loaders
        even when AI_ASSEMBLY_PROJECT_ROOT could resolve them."""
        from editor import card_assembly as ca

        def _raise_fnf(*a, **kw):
            raise FileNotFoundError("loader called when it shouldn't be")

        monkeypatch.setattr(ca, "load_council_config", _raise_fnf)
        monkeypatch.setattr(ca, "load_conference_facts", _raise_fnf)

        # Passing both explicitly — should not call the loaders, no exception
        prefix, _ = assemble_system_prompt(
            MIN_CARD, night=1, council=COUNCIL, conference=CONFERENCE
        )
        assert "## THE GATHERING" in prefix
        assert "## THE PANEL" in prefix


# --- Closing prompt (editor_dossier.md) renders new blocks ----

class TestEditorDossierPrompt:
    """The closing prompt at flows/shared/prompts/editor_dossier.md gets
    appended verbatim to the tail; assert it carries the field-by-field
    briefings we just added."""

    def _load(self):
        from shared.io import load_prompt
        return load_prompt("editor_dossier")

    def test_input_block_walks_each_field(self):
        text = self._load()
        # The expanded <input> block names each top-level field
        assert "`night`" in text
        assert "`theme`" in text
        assert "`engaged_voices[]`" in text
        assert "`prior_editions[]`" in text
        # And explains the per-theme sub-fields with 'You translate'
        assert "You translate" in text  # at least once for the theme_*_for_dossier translation hint
        # 'INVIOLATE' for the artifact_text contract
        assert "INVIOLATE" in text

    def test_emitted_fields_block_exists_with_pages(self):
        text = self._load()
        assert "<emitted_fields>" in text
        assert "</emitted_fields>" in text
        # All four page-surfaces named
        assert "Page 1" in text
        assert "Page 2" in text
        assert "Page 3" in text
        assert "Pages 4-N" in text

    def test_emitted_fields_names_each_field(self):
        text = self._load()
        for field in (
            "`kicker`", "`headline`", "`front_abstract`", "`subline`",
            "`body_paragraphs", "`theme_title_for_dossier`",
            "`theme_abstract_for_dossier`",
            "`headnotes[i].voice_slug`", "`headnotes[i].artifact_title`",
            "`headnotes[i].framing_text`",
        ):
            assert field in text, f"emitted_fields missing reference to {field}"

    def test_emitted_fields_names_artifact_inviolate(self):
        text = self._load()
        # The block ends by reminding artifact_text is NOT emitted by Tim
        assert "INVIOLATE" in text
