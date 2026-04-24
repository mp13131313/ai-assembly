"""chat_prompt_builder.py — Build chat-ready system prompt from assembled card.

FU#41 2026-04-24. After Derive completes, writes a 4th artifact alongside
provocateur_profile.json + evaluation_rubric.json: a chat-ready persona-
card JSON for direct paste into Claude project custom instructions.

Empirical derivation: compared operator's hand-produced chat v2 card
(Dostoevsky 2026-04-24) to the pipeline assembled_card. The chat v2 is
almost purely strip-out of Voice-Pipeline-only fields + tiny operator
polish (e.g., one factual correction: Freud 25 → 24 at Dostoevsky's
death). 27 of 35 shared fields byte-for-byte identical; 8 differ by
~10-100 chars of minor polish. Content generation is pipeline's job;
the chat artifact just mechanically strips deployment-inappropriate
fields.

Transformation (mechanical, no editorial work):
  - DROP Voice-Pipeline-only fields (10 fields, listed below)
  - PRESERVE all other fields at root level
  - MARK pipeline_version with "-chat" suffix
  - RE-STAMP generated_date for the chat artifact

Paste target: Claude project custom instructions (or a Claude API system
prompt for an agentic-chat deployment).

Does NOT attempt:
  - Editorial polish (operator's territory)
  - Factual correction (operator's territory; FU candidate for future
    fact-check-against-dossier pass)
  - Content expansion (operator's territory)
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any


# Fields dropped from assembled card when building chat-ready artifact.
# Each is Voice-Pipeline-only (build-time diagnostic, artifact-spec for
# Step 2 rendering, runtime continuity populated at deployment, or
# pipeline-generation metadata). See personas/HANDOFF.md §"smoke_test_
# chains is build-time only, NOT runtime few-shot" for smoke_test_chains
# rationale.
_VOICE_PIPELINE_ONLY_FIELDS = (
    # Pipeline-generation metadata (passes_completed, fix_pass_log,
    # tools_used, derived_outputs, field_counts, register_violations,
    # cross_model_validation, etc.)
    "metadata",
    # Pass 7b build-time diagnostic (explicitly NOT runtime few-shot
    # exemplars per spec — goes stale the moment real conference
    # questions arrive).
    "smoke_test_chains",
    # Two-tier corpus for musical voices (Marley). Loaded into Voice
    # Pipeline Step 1 only; Step 2 drops before rendering public artifact.
    # Chat deployments don't use the Voice Pipeline 2-step protocol at all,
    # so this field is dropped.
    "reference_only_passages",
    # Pass 4b artifact-spec fields (describe the Voice Pipeline Step 2
    # rendered artifact — prose/song/shader-params/dialogue). Chat
    # deployments produce chat responses, not these artifact genres.
    "medium",
    "characteristic_output_structure",
    "length_and_format_constraints",
    "technical_capabilities",
    "relationship_to_detailed_response",
    # Voice Pipeline runtime continuity (populated at deployment when the
    # voice has already spoken Night 1/Night 2; null at Persona Pipeline
    # output time).
    "continuity_block_if_night_2",
    "continuity_block_artifact_if_night_2",
)


def build_chat_system_prompt(assembled_card: dict[str, Any]) -> dict[str, Any]:
    """Transform an assembled_card dict into a chat-ready system-prompt dict.

    Mechanical field-strip + marker re-stamp. No content modification.

    Returns a new dict; input is not mutated.
    """
    chat = {
        k: v
        for k, v in assembled_card.items()
        if k not in _VOICE_PIPELINE_ONLY_FIELDS
    }

    # Marker fields: identify as chat-ready variant of the pipeline card.
    orig_version = chat.get("pipeline_version", "unknown")
    if not str(orig_version).endswith("-chat"):
        chat["pipeline_version"] = f"{orig_version}-chat"
    chat["generated_date"] = time.strftime("%Y-%m-%d")

    # Note on voice_temporal_stance: the pipeline card carries the full
    # {default, anchored_override} dict. Chat deployments can read either
    # sub-field per their operator-configured deployment mode (anchored
    # for death-threshold framing, default for fluid-across-time). We
    # preserve the dict intact and let the Claude project's custom-
    # instruction author decide which sub-field to foreground. Future FU
    # candidate: add an explicit `chat_deployment_mode: "anchored" |
    # "default"` marker if operators need programmatic disambiguation.

    return chat


def write_chat_system_prompt(
    assembled_card: dict[str, Any],
    output_path: Path,
) -> Path:
    """Build chat system prompt and write atomically to output_path.

    Returns the resolved output_path.
    """
    chat = build_chat_system_prompt(assembled_card)
    # Atomic write via temp file + rename (survives crash mid-write).
    output_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = output_path.with_suffix(output_path.suffix + ".tmp")
    tmp_path.write_text(
        json.dumps(chat, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    tmp_path.replace(output_path)
    return output_path
