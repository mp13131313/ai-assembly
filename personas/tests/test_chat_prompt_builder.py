"""test_chat_prompt_builder.py — Tests for FU#41 chat-ready artifact.

Amended 2026-04-25 (twice):
  - Amendment A (deployment-test reframing): strip 10→5
  - Amendment B (spec-shell suppression): strip 5→11 (5 + 5 + 1 nested)

Covers:
  1. Strip set A — 5 chat-structurally-incompatible fields dropped
  2. Strip set B — 5 spec-shell meta fields dropped (top-level)
  3. Strip set B — 1 nested sub-field dropped (corpus_metadata)
  4. Preserved fields — all other fields pass through byte-identical
  5. NO marker re-stamp — pipeline_version + generated_date are now in
     the strip set; the prior "-chat" suffix behavior is removed
  6. voice_temporal_stance preserved intact
  7. Voice-constitutional / deployment-aware fields (medium,
     characteristic_output_structure, length_and_format_constraints,
     technical_capabilities, relationship_to_detailed_response) ARE preserved
     — regression check against the over-strip pattern from FU#41 original
  8. write_chat_system_prompt atomic — temp-file + rename pattern
"""
from __future__ import annotations

import json
from pathlib import Path

from flows.shared.chat_prompt_builder import (
    _CHAT_INCOMPATIBLE_FIELDS,
    _NESTED_STRIPS,
    _SPEC_SHELL_META_FIELDS,
    _VOICE_PIPELINE_ONLY_FIELDS,
    build_chat_system_prompt,
    write_chat_system_prompt,
)


def _minimal_assembled_card() -> dict:
    """Return a minimal assembled card fixture covering each kind of field."""
    return {
        # Strip set A — chat-structurally-incompatible (dropped):
        "metadata": {"passes_completed": ["2", "3"], "validation_status": "PASS"},
        "smoke_test_chains": [{"chain_1": "..."}],
        "reference_only_passages": {"passages": []},
        "continuity_block_if_night_2": None,
        "continuity_block_artifact_if_night_2": None,
        # Strip set B — spec-shell meta (dropped):
        "voice_name": "Test Voice",
        "voice_mode": "philosophical",
        "pipeline_version": "3.10",
        "generated_date": "2026-04-24",
        "council_member_name": "Test",
        # Voice-constitutional / deployment-aware fields (PRESERVED under
        # Amendment A — were stripped under FU#41 original):
        "medium": "I write what I have always written: a short conversation.",
        "characteristic_output_structure": "I open in the middle of life…",
        "length_and_format_constraints": "350-550 words",
        "technical_capabilities": "Text only.",
        "relationship_to_detailed_response": "…",
        # Other preserved fields:
        "epistemic_frame_statement": "You are…",
        "world": {"ontological_furniture": "…"},
        "formative_experience": {"formative_emotional_community": "…"},
        "character": "You are a person of…",
        "voice_temporal_stance": {
            "default": "fluid framing text",
            "anchored_override": "anchored framing text",
        },
        "constitution": [{"principle": "P1", "operational_note": "N1"}],
        "concept_lexicon": [{"term": "T1", "definition": "D1"}],
        "reasoning_method": {"summary": "…", "steps": []},
        "characteristic_moves": [{"name": "M1", "description": "…"}],
        "register_and_tone": "…",
        "metaphorical_repertoire": {"groups": []},
        "preferred_vocabulary": [],
        "banned_language": [],
        "banned_modes": [],
        "curated_corpus_passages": {
            "passages": [{"work_title": "Republic", "stephanus": "327a"}],
            # Production metadata — Strip B nested (dropped); rest of dict survives.
            "corpus_metadata": "Public-domain translations; 5 sources; 12 passages.",
        },
        "knowledge_boundary": "…",
        "translation_protocol": "…",
        "topics_requiring_care": [],
        "hard_limits": [],
        "bold_engagement_topics": [],
        "default_questions": [],
        "disagreement_protocol": "…",
        "unique_contribution": "…",
        "aesthetic_qualities": "…",
        "stance_tendency": "…",
        "quality_criteria": [],
        "finds_compelling": [],
        "resists": [],
        "rhetorical_mode": "…",
    }


# ── field-strip correctness ─────────────────────────────────────────────────

def test_all_voice_pipeline_only_fields_are_dropped():
    card = _minimal_assembled_card()
    chat = build_chat_system_prompt(card)
    for field in _VOICE_PIPELINE_ONLY_FIELDS:
        assert field not in chat, f"Voice-Pipeline-only field {field!r} leaked into chat prompt"


def test_chat_incompatible_strip_set():
    """Strip set A — 6 chat-structurally-incompatible fields per Amendment A
    (5 original) + Amendment C (FU#57 2026-04-29: bold_engagement_topics)."""
    expected_a = {
        "metadata",
        "smoke_test_chains",
        "reference_only_passages",
        "continuity_block_if_night_2",
        "continuity_block_artifact_if_night_2",
        "bold_engagement_topics",  # FU#57 2026-04-29
    }
    assert set(_CHAT_INCOMPATIBLE_FIELDS) == expected_a


def test_spec_shell_strip_set():
    """Strip set B — 5 spec-shell meta fields per Amendment B."""
    expected_b = {
        "voice_name",
        "voice_mode",
        "pipeline_version",
        "generated_date",
        "council_member_name",
    }
    assert set(_SPEC_SHELL_META_FIELDS) == expected_b


def test_combined_strip_set_total():
    """Combined top-level strip set = 11 fields (A=6 + B=5; nested strip is
    separate). FU#57 2026-04-29 bumped A from 5→6 with bold_engagement_topics."""
    assert set(_VOICE_PIPELINE_ONLY_FIELDS) == set(_CHAT_INCOMPATIBLE_FIELDS) | set(_SPEC_SHELL_META_FIELDS)
    assert len(_VOICE_PIPELINE_ONLY_FIELDS) == 11


def test_nested_strip_set():
    """Strip set B nested — corpus_metadata sub-field of curated_corpus_passages."""
    assert _NESTED_STRIPS == (("curated_corpus_passages", "corpus_metadata"),)


def test_voice_constitutional_fields_preserved():
    """The 5 voice-constitutional / deployment-aware fields stripped under
    the original FU#41 framing must NOT be in the strip set. Regression
    check against the over-strip pattern Amendment A corrected."""
    must_be_preserved = {
        "medium",
        "characteristic_output_structure",
        "length_and_format_constraints",
        "technical_capabilities",
        "relationship_to_detailed_response",
    }
    leaks = must_be_preserved & set(_VOICE_PIPELINE_ONLY_FIELDS)
    assert leaks == set(), (
        f"Voice-constitutional fields leaked into strip set: {leaks}. "
        f"This regresses Amendment A — chat is a TEST of the configured "
        f"deployment, so these must be preserved."
    )


def test_spec_shell_fields_dropped_in_output():
    """Amendment B regression: voice_name / voice_mode / pipeline_version /
    generated_date / council_member_name should not appear in chat output."""
    card = _minimal_assembled_card()
    chat = build_chat_system_prompt(card)
    for f in _SPEC_SHELL_META_FIELDS:
        assert f not in chat, f"Spec-shell meta field {f!r} leaked into chat output"


def test_corpus_metadata_nested_strip():
    """Amendment B nested: curated_corpus_passages.corpus_metadata is dropped,
    but the rest of curated_corpus_passages (passages[] etc.) survives."""
    card = _minimal_assembled_card()
    chat = build_chat_system_prompt(card)
    assert "curated_corpus_passages" in chat
    ccp = chat["curated_corpus_passages"]
    assert "corpus_metadata" not in ccp
    assert "passages" in ccp
    assert ccp["passages"][0]["work_title"] == "Republic"


def test_corpus_metadata_strip_does_not_mutate_input():
    """The nested-strip path must deep-copy the parent before mutation, so
    the caller's input dict is not affected."""
    card = _minimal_assembled_card()
    snapshot = json.dumps(card["curated_corpus_passages"], sort_keys=True)
    _ = build_chat_system_prompt(card)
    assert json.dumps(card["curated_corpus_passages"], sort_keys=True) == snapshot, (
        "Nested-strip mutated caller's curated_corpus_passages dict"
    )


def test_preserved_fields_pass_through_identical():
    card = _minimal_assembled_card()
    chat = build_chat_system_prompt(card)
    for field in card:
        if field in _VOICE_PIPELINE_ONLY_FIELDS:
            continue
        if field == "curated_corpus_passages":
            continue  # Has a nested strip — checked separately above
        assert chat[field] == card[field], f"Preserved field {field!r} modified"


# ── no-marker invariant (marker re-stamp removed under Amendment B) ─────────

def test_no_marker_re_stamp():
    """Amendment B removes the prior `-chat` suffix + generated_date re-stamp.
    pipeline_version + generated_date are now in the strip set; the artifact
    carries no provenance marker. Operators identify chat artifacts by
    filename, not by in-artifact content."""
    card = _minimal_assembled_card()
    card["pipeline_version"] = "3.10"
    card["generated_date"] = "2026-04-25"
    chat = build_chat_system_prompt(card)
    assert "pipeline_version" not in chat
    assert "generated_date" not in chat


# ── voice_temporal_stance handling ──────────────────────────────────────────

def test_voice_temporal_stance_preserved_intact():
    card = _minimal_assembled_card()
    chat = build_chat_system_prompt(card)
    assert chat["voice_temporal_stance"] == {
        "default": "fluid framing text",
        "anchored_override": "anchored framing text",
    }


def test_voice_temporal_stance_without_override():
    card = _minimal_assembled_card()
    card["voice_temporal_stance"] = {"default": "fluid only", "anchored_override": None}
    chat = build_chat_system_prompt(card)
    assert chat["voice_temporal_stance"] == {
        "default": "fluid only",
        "anchored_override": None,
    }


# ── non-mutation invariant ──────────────────────────────────────────────────

def test_build_does_not_mutate_input():
    card = _minimal_assembled_card()
    snapshot = json.dumps(card, sort_keys=True)
    _ = build_chat_system_prompt(card)
    assert json.dumps(card, sort_keys=True) == snapshot, "Input card was mutated"


# ── atomic write ────────────────────────────────────────────────────────────

def test_write_chat_system_prompt_creates_file(tmp_path: Path):
    card = _minimal_assembled_card()
    out = tmp_path / "06_derive" / "03_chat_system_prompt.json"
    write_chat_system_prompt(card, out)
    assert out.exists()
    reread = json.loads(out.read_text())
    # voice_name is now in the strip set (Amendment B); identity lives in
    # epistemic_frame_statement
    assert reread["epistemic_frame_statement"] == "You are…"
    assert "voice_name" not in reread
    assert "metadata" not in reread
    assert "smoke_test_chains" not in reread


def test_write_chat_system_prompt_overwrites_existing(tmp_path: Path):
    out = tmp_path / "chat.json"
    out.write_text('{"old": "content"}')
    card = _minimal_assembled_card()
    write_chat_system_prompt(card, out)
    reread = json.loads(out.read_text())
    assert "old" not in reread
    assert reread["epistemic_frame_statement"] == "You are…"


def test_write_chat_system_prompt_cleans_tmp_file(tmp_path: Path):
    """Atomic write via temp file + rename should not leave stray .tmp files."""
    out = tmp_path / "chat.json"
    card = _minimal_assembled_card()
    write_chat_system_prompt(card, out)
    stray = list(tmp_path.glob("*.tmp"))
    assert stray == [], f"Temp files left behind: {stray}"


# ── architectural-amendment historical record ───────────────────────────────

def test_amendment_history_2026_04_24_to_2026_04_29():
    """Documents the strip-set evolution across three amendments.

    Original (2026-04-24 FU#41 b9c1eb2) stripped 10 fields; same 10
    operator's hand-produced Dostoevsky chat v2 had stripped.

    Amendment A (2026-04-25 deployment-test reframing): chat = test of
    configured deployment, not separate deployment. Strip shrinks 10→5
    by RESTORING 5 voice-constitutional / deployment-aware fields.

    Amendment B (2026-04-25 spec-shell suppression): empirically motivated
    by Plato chat-test thinking-trace meta-reasoning. Strip grows 5→11
    by ADDING 5 spec-shell meta fields (top-level) + 1 nested production-
    metadata sub-field.

    Amendment C (FU#57 2026-04-29 bold_engagement_topics): empirically
    motivated by Plato chat-test observation that the voice reasons more
    freely with bold_engagement_topics stripped (pre-loaded courage menu
    pulls reasoning toward predetermined topics rather than letting the
    matter drive). Strip grows 11→12 by ADDING bold_engagement_topics to
    Strip A. Coordinated with runtime/flows/voice/card_assembly.py drop
    from runtime system prompts (FU#57)."""
    original_2026_04_24_strip = {
        "metadata",
        "smoke_test_chains",
        "reference_only_passages",
        "medium",
        "characteristic_output_structure",
        "length_and_format_constraints",
        "technical_capabilities",
        "relationship_to_detailed_response",
        "continuity_block_if_night_2",
        "continuity_block_artifact_if_night_2",
    }
    amendment_a_promoted_to_preserve = {
        "medium",
        "characteristic_output_structure",
        "length_and_format_constraints",
        "technical_capabilities",
        "relationship_to_detailed_response",
    }
    amendment_b_added_to_strip = {
        "voice_name",
        "voice_mode",
        "pipeline_version",
        "generated_date",
        "council_member_name",
    }
    amendment_b_nested = (("curated_corpus_passages", "corpus_metadata"),)
    amendment_c_added_to_strip = {
        "bold_engagement_topics",  # FU#57 2026-04-29
    }

    current = set(_VOICE_PIPELINE_ONLY_FIELDS)
    expected_current = (
        (original_2026_04_24_strip - amendment_a_promoted_to_preserve)
        | amendment_b_added_to_strip
        | amendment_c_added_to_strip
    )
    assert current == expected_current
    assert _NESTED_STRIPS == amendment_b_nested

    # Amendment A's promoted-to-preserve set must NOT have leaked back into
    # the strip (Amendment A regression).
    assert current & amendment_a_promoted_to_preserve == set()
