"""Tests for the deployment-context block in assemble_system_prompt.

Branch: feature/voice-deployment-context.

Covers `_render_deployment_context` and its integration via
`assemble_system_prompt`. Asserts:
  - THE GATHERING block appears at all steps when conference_facts present
  - THE PANEL block appears at all steps when council present
  - YOUR FELLOW VOICES appears at step 2 only, with self excluded + anti-
    translation framing
  - YOUR READERS appears at all steps when council.audience present
  - session_role_for_ai_assembly is NEVER injected (operator decision —
    deployment context stays descriptive, persona card retains
    prescriptive monopoly)
  - Graceful fallback to empty block when sources missing (test fixtures
    pass council=None / conference=None and the system prompt still
    assembles without raising)
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_RUNTIME_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_RUNTIME_ROOT / "flows"))

from voice.card_assembly import (  # noqa: E402
    _render_deployment_context,
    assemble_system_prompt,
)


# --- Fixtures ---------------------------------------------------------

CONFERENCE = {
    "conference_context_paragraph": (
        "The World Beautiful Business Forum is the 10th-anniversary "
        "flagship gathering... agency — who acts, who decides..."
    ),
    "session_role_for_ai_assembly": (
        "The AIssembly takes the AI Democracy Marathon's night shift. "
        "Three bars in order: first, compelling enough... performing "
        "reception without being changed..."
    ),
}

COUNCIL = {
    "collective_landscape": (
        "Ten voices spanning roughly 2500 years of human thought plus "
        "two non-human participants: Plato (classical dialectic), "
        "Cleopatra (imperial statecraft)..."
    ),
    "audience": (
        "~750 attendees: senior professionals... they go flat on TED-style "
        "resolution... well-curated openness is itself how they avoid being "
        "changed."
    ),
    "members": [
        {"name": "Voice of Plato"},
        {"name": "Voice of Cleopatra"},
        {"name": "Voice of Hannah Arendt"},
        {"name": "Voice of the Octopus"},
    ],
}

# Minimal card to satisfy assemble_system_prompt — all required-by-renderer
# fields present as stubs so the prefix sections render. Real cards have
# 35+ fields; we test deployment-context behaviour, not full assembly.
MIN_CARD = {
    "council_member_name": "Voice of Plato",
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
    "voice_temporal_stance": "stub",
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
    "unique_contribution": "stub",
    "stance_tendency": "stub",
    "medium": "stub",
    "technical_capabilities": "stub",
    "characteristic_output_structure": "stub",
    "relationship_to_detailed_response": "stub",
    "aesthetic_qualities": "stub",
    "length_and_format_constraints": "stub",
    "quality_criteria": "stub",
    "bold_engagement_topics": "stub",
    "disagreement_protocol": "stub",
}


# --- _render_deployment_context (unit tests) --------------------------

class TestRenderDeploymentContext:
    """Tests on the render helper directly, no card_assembly machinery."""

    def test_gathering_block_present_when_conference_given(self):
        out = _render_deployment_context(COUNCIL, CONFERENCE, "plato", step=1)
        assert "## THE GATHERING" in out
        assert "World Beautiful Business Forum" in out

    def test_panel_block_present_when_council_given(self):
        out = _render_deployment_context(COUNCIL, CONFERENCE, "plato", step=1)
        assert "## THE PANEL" in out
        assert "Ten voices spanning" in out

    def test_readers_block_present_when_council_audience_given(self):
        out = _render_deployment_context(COUNCIL, CONFERENCE, "plato", step=1)
        assert "## YOUR READERS" in out
        assert "well-curated openness" in out

    def test_fellow_voices_block_only_at_step_2(self):
        s1 = _render_deployment_context(COUNCIL, CONFERENCE, "plato", step=1)
        s2 = _render_deployment_context(COUNCIL, CONFERENCE, "plato", step=2)
        s3 = _render_deployment_context(COUNCIL, CONFERENCE, "plato", step=3)

        assert "## YOUR FELLOW VOICES" not in s1
        assert "## YOUR FELLOW VOICES" in s2
        assert "## YOUR FELLOW VOICES" not in s3

    def test_fellow_voices_excludes_self(self):
        out = _render_deployment_context(COUNCIL, CONFERENCE, "plato", step=2)
        assert "Voice of Cleopatra" in out
        assert "Voice of Hannah Arendt" in out
        assert "Voice of the Octopus" in out
        # Self should NOT appear in the fellow-voices listing
        # (find the YOUR FELLOW VOICES section + check Plato isn't bulleted)
        section = out.split("## YOUR FELLOW VOICES")[1].split("## YOUR READERS")[0]
        assert "- Voice of Plato" not in section

    def test_fellow_voices_includes_anti_translation_framing(self):
        out = _render_deployment_context(COUNCIL, CONFERENCE, "plato", step=2)
        assert "does not need you to soften" in out
        assert "translate themselves into a common register" in out

    def test_session_role_never_injected(self):
        """Operator decision: keep session_role_for_ai_assembly out of voice
        prompts. Deployment context stays descriptive; persona card retains
        prescriptive monopoly."""
        for step in (1, 2, 3):
            out = _render_deployment_context(COUNCIL, CONFERENCE, "plato", step=step)
            assert "AI Democracy Marathon's night shift" not in out
            assert "Three bars in order" not in out
            assert "performing reception without being changed" not in out

    def test_empty_when_no_sources(self):
        assert _render_deployment_context(None, None, None, step=1) == ""
        assert _render_deployment_context(None, None, "plato", step=2) == ""

    def test_partial_sources_renders_what_it_can(self):
        # Only conference, no council — only THE GATHERING appears
        out = _render_deployment_context(None, CONFERENCE, "plato", step=1)
        assert "## THE GATHERING" in out
        assert "## THE PANEL" not in out
        assert "## YOUR READERS" not in out

        # Only council, no conference
        out2 = _render_deployment_context(COUNCIL, None, "plato", step=1)
        assert "## THE GATHERING" not in out2
        assert "## THE PANEL" in out2
        assert "## YOUR READERS" in out2


# --- assemble_system_prompt integration --------------------------------

class TestAssembleSystemPromptIntegration:
    """Deployment context appears in the prefix portion (cache-shared
    across step 1/2/3 calls for one voice on one night)."""

    def test_deployment_context_in_prefix_step_1(self):
        prefix, tail = assemble_system_prompt(
            MIN_CARD, step=1, council=COUNCIL, conference=CONFERENCE
        )
        assert "## THE GATHERING" in prefix
        assert "## THE PANEL" in prefix
        assert "## YOUR READERS" in prefix
        # Step 1 has no fellow-voices block
        assert "## YOUR FELLOW VOICES" not in prefix
        # Tail should be deployment-free
        assert "## THE GATHERING" not in tail

    def test_deployment_context_in_prefix_step_2_with_fellow_voices(self):
        prefix, tail = assemble_system_prompt(
            MIN_CARD, step=2, council=COUNCIL, conference=CONFERENCE
        )
        assert "## THE GATHERING" in prefix
        assert "## THE PANEL" in prefix
        assert "## YOUR FELLOW VOICES" in prefix
        assert "## YOUR READERS" in prefix
        # Self ('Voice of Plato') excluded from fellow-voices listing
        fv_section = prefix.split("## YOUR FELLOW VOICES")[1].split("## YOUR READERS")[0]
        assert "- Voice of Plato" not in fv_section
        # Other voices present
        assert "Voice of Cleopatra" in fv_section
        assert "Voice of the Octopus" in fv_section

    def test_deployment_context_in_prefix_step_3_no_fellow_voices_block(self):
        # Step 3 (dormant for Athens) gets gathering + panel + readers but
        # not the fellow-voices listing — that's a step-2-composition concern
        prefix, _ = assemble_system_prompt(
            MIN_CARD, step=3, council=COUNCIL, conference=CONFERENCE
        )
        assert "## THE GATHERING" in prefix
        assert "## THE PANEL" in prefix
        assert "## YOUR READERS" in prefix
        assert "## YOUR FELLOW VOICES" not in prefix

    def test_session_role_never_in_prompt(self):
        """End-to-end check: the imperative-flavoured text from
        session_role_for_ai_assembly never reaches voice prompts at any step."""
        for step in (1, 2, 3):
            prefix, tail = assemble_system_prompt(
                MIN_CARD, step=step, council=COUNCIL, conference=CONFERENCE
            )
            full = prefix + tail
            assert "AI Democracy Marathon's night shift" not in full
            assert "Three bars in order" not in full
            assert "performing reception without being changed" not in full

    def test_no_deployment_when_sources_missing(self, monkeypatch):
        """Test fixtures without PROJECT_ROOT files should still produce a
        valid system prompt — deployment context degrades to empty.

        Monkeypatches both loaders to raise FileNotFoundError so the
        fallback path (council=None, conference=None) is exercised even
        when AI_ASSEMBLY_PROJECT_ROOT is set in the test environment."""
        from voice import card_assembly as ca

        def _raise_fnf(*a, **kw):
            raise FileNotFoundError("simulated missing source")

        monkeypatch.setattr(ca, "load_council_config", _raise_fnf)
        monkeypatch.setattr(ca, "load_conference_facts", _raise_fnf)

        prefix, tail = assemble_system_prompt(
            MIN_CARD, step=1, council=None, conference=None
        )
        assert "## THE GATHERING" not in prefix
        assert "## THE PANEL" not in prefix
        assert "## YOUR READERS" not in prefix
        # And the rest of the prefix still renders (prefix is non-empty)
        assert len(prefix) > 100
        assert "Voice of Plato" in prefix

    def test_prefix_byte_identical_across_steps_for_deployment_block(self):
        """The deployment block within the prefix is identical across
        steps 1 and 3 (no fellow-voices), but different at step 2 because
        of the fellow-voices addition. This is intentional — the prefix
        cache hits across step 1 calls (multiple themes per voice) and
        across step 1↔step 3 calls; step 2 has its own cache key."""
        p1, _ = assemble_system_prompt(
            MIN_CARD, step=1, council=COUNCIL, conference=CONFERENCE
        )
        p3, _ = assemble_system_prompt(
            MIN_CARD, step=3, council=COUNCIL, conference=CONFERENCE
        )
        # Extract deployment block from each prefix
        marker = "## THE GATHERING"
        d1 = p1[p1.find(marker):]
        d3 = p3[p3.find(marker):]
        assert d1 == d3, "Step 1 and Step 3 deployment blocks must be byte-identical"

        p2, _ = assemble_system_prompt(
            MIN_CARD, step=2, council=COUNCIL, conference=CONFERENCE
        )
        d2 = p2[p2.find(marker):]
        assert d2 != d1, "Step 2 deployment block should differ (has YOUR FELLOW VOICES)"
