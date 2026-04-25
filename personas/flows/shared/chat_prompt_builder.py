"""chat_prompt_builder.py — Build chat-ready system prompt from assembled card.

FU#41 2026-04-24, amended 2026-04-25 (deployment-test reframing).

After Derive completes, writes a 4th artifact alongside provocateur_profile
.json + evaluation_rubric.json: a chat-ready persona-card JSON for direct
paste into Claude project custom instructions.

Architectural framing (amended 2026-04-25):
  Chat deployment is treated as a **test of the configured deployment**
  (e.g., the Athens 2026 Voice Pipeline run), NOT as a separate deployment
  surface. The chat artifact should produce the same shape of output the
  Voice Pipeline runtime will produce — same length window, same artifact
  structure, same audience-aware priming. Differences from a fresh hand-
  produced chat card are intentional: chat output IS the deployment-test.

  This was a correction of the prior framing, which treated chat as a
  separate deployment and stripped deployment-format-shaped fields like
  `medium` and `length_and_format_constraints`. That over-stripped voice-
  constitutional content (e.g. Plato's "I write what I have always written:
  a short conversation"). See FOLLOW_UPS.md FU#41 amendment note for the
  empirical case.

Strip set (necessary only — what chat structurally cannot process):
  - Pipeline-internal metadata (validation flags, fix-pass log, audit trail)
  - Pipeline-internal QC artifacts (Pass 7b smoke_test_chains, which would
    be misread by the model as examples-to-follow)
  - Voice-Pipeline-Step-1-only constraints (reference_only_passages, which
    rely on Step 1/Step 2 separation chat doesn't enforce — the model would
    quote them at runtime)
  - Multi-prompt-context fields (continuity_blocks for Night 2, which can't
    be maintained across a single chat deployment's stateless paste)

PRESERVED (vs prior strip):
  - medium, characteristic_output_structure, length_and_format_constraints,
    technical_capabilities, relationship_to_detailed_response.
  These are voice-constitutional + deployment-aware. For voices like Plato
  whose `medium` is constitutional (dialogue commitment per Phaedrus's
  refusal of treatise form), stripping them was the over-strip pattern the
  amendment corrects.

Transformation (mechanical, no editorial work):
  - DROP 5 chat-incompatible fields (listed below)
  - PRESERVE all other fields at root level (~39 fields)
  - MARK pipeline_version with "-chat" suffix
  - RE-STAMP generated_date for the chat artifact

Paste target: Claude project custom instructions (or a Claude API system
prompt for an agentic-chat deployment).

Does NOT attempt:
  - Editorial polish (operator's territory)
  - Factual correction (operator's territory; FU candidate for future
    fact-check-against-dossier pass)
  - Content expansion (operator's territory)

Post-Athens architectural direction (split-card, not yet implemented): the
voice-card / deployment-card distinction would let the strip be principled
per-tag rather than per-blacklist, and would support multiple deployment
contexts per voice (Plato-for-Athens vs Plato-for-future-event etc.).
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any


# Fields dropped from assembled card when building chat-ready artifact.
# Strip set is "what chat structurally cannot process" — not "what chat
# doesn't need." Chat is a test of the configured deployment, so deployment-
# spec fields (medium, length_and_format_constraints, etc.) are PRESERVED
# so the chat output matches what the Voice Pipeline runtime will produce.
# See module docstring for the architectural framing.
_VOICE_PIPELINE_ONLY_FIELDS = (
    # Pipeline-generation metadata (passes_completed, fix_pass_log,
    # tools_used, derived_outputs, field_counts, register_violations,
    # cross_model_validation, etc.) — pure pipeline-internal; would not
    # inform model behavior, only confuse with audit-trail noise.
    "metadata",
    # Pass 7b build-time QC diagnostic. Model would read these as exemplars-
    # to-follow rather than as out-of-band tests. Per HANDOFF.md
    # §"smoke_test_chains is build-time only, NOT runtime few-shot."
    "smoke_test_chains",
    # Two-tier corpus for musical/citation-restricted voices (Marley
    # lyrics, etc.). Voice Pipeline Step 1 reads them, Step 2 drops before
    # rendering. Chat doesn't enforce Step 1/Step 2 separation — pasting
    # plainly would cause the model to quote what should be reference-only.
    "reference_only_passages",
    # Voice Pipeline runtime continuity (populated at deployment when the
    # voice has already spoken Night 1; null at Persona Pipeline output
    # time AND structurally absent in single-paste chat deployment).
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
