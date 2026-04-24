"""test_chat_prompt_builder.py — Tests for FU#41 chat-ready artifact.

Covers:
  1. Voice-Pipeline-only field strip — correct 10 fields dropped
  2. Preserved fields — all other fields pass through byte-identical
  3. Marker fields — pipeline_version gets "-chat" suffix; generated_date
     re-stamped
  4. voice_temporal_stance preserved intact (chat deployment reads whichever
     sub-field it needs)
  5. write_chat_system_prompt atomic — temp-file + rename pattern
"""
from __future__ import annotations

import json
import time
from pathlib import Path

from flows.shared.chat_prompt_builder import (
    _VOICE_PIPELINE_ONLY_FIELDS,
    build_chat_system_prompt,
    write_chat_system_prompt,
)


def _minimal_assembled_card() -> dict:
    """Return a minimal assembled card fixture covering each kind of field."""
    return {
        # Voice-Pipeline-only fields (should be dropped):
        "metadata": {"passes_completed": ["2", "3"], "validation_status": "PASS"},
        "smoke_test_chains": [{"chain_1": "..."}],
        "reference_only_passages": {"passages": []},
        "medium": "prose",
        "characteristic_output_structure": "…",
        "length_and_format_constraints": "350-550 words",
        "technical_capabilities": "Text only.",
        "relationship_to_detailed_response": "…",
        "continuity_block_if_night_2": None,
        "continuity_block_artifact_if_night_2": None,
        # Preserved fields:
        "voice_name": "Test Voice",
        "voice_mode": "philosophical",
        "pipeline_version": "3.10",
        "generated_date": "2026-04-24",
        "council_member_name": "Test",
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
        "curated_corpus_passages": {"passages": []},
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


def test_voice_pipeline_only_fields_list_matches_empirical_diff():
    """The 10 fields documented as Voice-Pipeline-only should match the
    actual set dropped during the transformation. This is a regression
    check — if the FU#41 spec changes, this test flags it."""
    expected = {
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
    assert set(_VOICE_PIPELINE_ONLY_FIELDS) == expected


def test_preserved_fields_pass_through_identical():
    card = _minimal_assembled_card()
    chat = build_chat_system_prompt(card)
    for field in card:
        if field in _VOICE_PIPELINE_ONLY_FIELDS:
            continue
        if field in ("pipeline_version", "generated_date"):
            continue  # Marker fields — modified deliberately; separate tests
        assert chat[field] == card[field], f"Preserved field {field!r} modified"


# ── marker fields ───────────────────────────────────────────────────────────

def test_pipeline_version_gets_chat_suffix():
    card = _minimal_assembled_card()
    card["pipeline_version"] = "3.10"
    chat = build_chat_system_prompt(card)
    assert chat["pipeline_version"] == "3.10-chat"


def test_pipeline_version_idempotent_under_chat_suffix():
    """Calling twice in a row should not produce '3.10-chat-chat'."""
    card = _minimal_assembled_card()
    card["pipeline_version"] = "3.10-chat"
    chat = build_chat_system_prompt(card)
    assert chat["pipeline_version"] == "3.10-chat"


def test_generated_date_is_today():
    card = _minimal_assembled_card()
    card["generated_date"] = "2020-01-01"
    chat = build_chat_system_prompt(card)
    today = time.strftime("%Y-%m-%d")
    assert chat["generated_date"] == today


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
    assert reread["voice_name"] == "Test Voice"
    assert "metadata" not in reread
    assert "smoke_test_chains" not in reread


def test_write_chat_system_prompt_overwrites_existing(tmp_path: Path):
    out = tmp_path / "chat.json"
    out.write_text('{"old": "content"}')
    card = _minimal_assembled_card()
    write_chat_system_prompt(card, out)
    reread = json.loads(out.read_text())
    assert "old" not in reread
    assert reread["voice_name"] == "Test Voice"


def test_write_chat_system_prompt_cleans_tmp_file(tmp_path: Path):
    """Atomic write via temp file + rename should not leave stray .tmp files."""
    out = tmp_path / "chat.json"
    card = _minimal_assembled_card()
    write_chat_system_prompt(card, out)
    stray = list(tmp_path.glob("*.tmp"))
    assert stray == [], f"Temp files left behind: {stray}"


# ── empirical regression: chat v2 shape ─────────────────────────────────────

def test_chat_v2_shape_from_empirical_diff():
    """Regression check against the 2026-04-24 operator-produced chat v2
    Dostoevsky card. Fields in the pipeline-generated card that were NOT
    in the chat v2 are the VOICE_PIPELINE_ONLY_FIELDS set."""
    # These were empirically observed as the chat v2 strip set (diff of
    # Dostoevsky assembled_card vs dostoevsky_chat_system_prompt_v2.json)
    pipeline_only_from_empirical_diff = {
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
    assert set(_VOICE_PIPELINE_ONLY_FIELDS) == pipeline_only_from_empirical_diff
