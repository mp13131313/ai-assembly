"""chat_prompt_builder.py — Build chat-ready system prompt from assembled card.

FU#41 2026-04-24, amended 2026-04-25 (twice):
  - Amendment A (deployment-test reframing): strip 10→5
  - Amendment B (spec-shell suppression): strip 5→11 (5 + 5 + 1 nested)

After Derive completes, writes a 4th artifact alongside provocateur_profile
.json + evaluation_rubric.json: a chat-ready persona-card JSON for direct
paste into Claude project custom instructions.

Architectural framing (amendments A + B):
  Chat deployment is a **test of the configured deployment** (e.g., the
  Athens 2026 Voice Pipeline run), NOT a separate deployment surface.
  The chat artifact should produce the same shape of output the Voice
  Pipeline runtime will produce — same length window, same artifact
  structure, same audience-aware priming. Voice-constitutional fields
  (medium, characteristic_output_structure, etc.) MUST be preserved for
  the voice to deploy faithfully.

  At the same time, fields that label the artifact AS a specification —
  `voice_mode`, `pipeline_version`, `voice_name`, `council_member_name`,
  `corpus_metadata` — make the model reason ABOUT being given a persona
  spec rather than reason FROM WITHIN the voice. Empirically observed
  in Plato chat-test thinking traces 2026-04-25 ("metadata points to a
  test environment for a Plato-voice mode... legitimate philosophical
  voice exercise rather than something problematic"). These spec-shell
  meta-fields are stripped to reduce that meta-reasoning mode.

Strip set (11 items total):

A — Chat-structurally-incompatible (5):
  - metadata (pipeline-internal validation/audit)
  - smoke_test_chains (Pass 7b QC; misread as exemplars-to-follow)
  - reference_only_passages (Step-1-only constraint chat can't enforce)
  - continuity_block_if_night_2 (multi-prompt context absent in single chat)
  - continuity_block_artifact_if_night_2 (same)

B — Spec-shell meta (5 top-level + 1 nested):
  - voice_name (third-person identity scaffold; identity should live in
    epistemic_frame_statement first/second-person prose)
  - voice_mode (schema label — "philosophical"/"narrative" reads as mode-
    selection signal)
  - pipeline_version (provenance — "3.10-chat" reads as test/dev pipeline)
  - generated_date (provenance)
  - council_member_name (Voice-Pipeline scaffolding announcing council role)
  - curated_corpus_passages.corpus_metadata (NESTED — production metadata:
    "Public-domain translations...", source counts, passage counts. The
    rest of curated_corpus_passages.passages[] survives.)

PRESERVED (voice-constitutional + deployment-aware):
  - medium, characteristic_output_structure, length_and_format_constraints,
    technical_capabilities, relationship_to_detailed_response. For voices
    whose `medium` is constitutional (Plato's dialogue commitment per
    Phaedrus's refusal of treatise form), these encode who the voice IS.

Transformation (mechanical, no editorial work):
  - DROP 5 chat-incompatible top-level fields (Strip A)
  - DROP 5 spec-shell meta top-level fields (Strip B)
  - DROP curated_corpus_passages.corpus_metadata sub-field (Strip B nested)
  - PRESERVE all other fields at root level (~33-34 fields)
  - NO marker re-stamp (the prior `-chat` suffix and `generated_date` re-
    stamp behavior is removed; pipeline_version is now in the strip set,
    and operators identify chat artifacts by filename — `03_chat_system
    _prompt.json` — not by in-artifact marker)

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
from pathlib import Path
from typing import Any


# Strip set A — fields chat structurally cannot process. See module
# docstring for full architectural framing.
_CHAT_INCOMPATIBLE_FIELDS = (
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
    # FU#57 (2026-04-29): pre-loaded courage menu pulls reasoning toward
    # predetermined topics rather than letting the matter drive. Empirical
    # observation in chat-test on Plato (pre-12-patches): the voice
    # reasoned more freely with bold_engagement_topics stripped. Field is
    # still emitted by Pass 5 for build-side audit value, but does NOT
    # belong in the runtime chat artifact (or in the Voice Pipeline
    # system prompt — see runtime/flows/voice/card_assembly.py header).
    "bold_engagement_topics",
)

# Strip set B — spec-shell meta fields. These label the artifact AS a
# persona specification (rather than letting it read as the voice itself),
# triggering the model to reason ABOUT being given a spec instead of FROM
# WITHIN the voice. Empirically observed in Plato chat-test thinking
# traces 2026-04-25.
_SPEC_SHELL_META_FIELDS = (
    # Third-person identity scaffold; identity should live in
    # epistemic_frame_statement as first/second-person prose.
    "voice_name",
    # Schema label — "philosophical"/"narrative" reads as mode-selection signal.
    "voice_mode",
    # Provenance — "3.10-chat" reads to the model as test/dev pipeline marker.
    "pipeline_version",
    # Provenance — date stamp adds nothing to runtime behavior.
    "generated_date",
    # Voice-Pipeline scaffolding announcing council-member role.
    "council_member_name",
)

# Combined top-level strip set (10 items; nested production metadata
# stripped separately — see _strip_nested below).
_VOICE_PIPELINE_ONLY_FIELDS = _CHAT_INCOMPATIBLE_FIELDS + _SPEC_SHELL_META_FIELDS

# Nested sub-fields to strip (path: parent_field, child_key).
# curated_corpus_passages.corpus_metadata = production metadata
# ("Public-domain translations...", source counts, passage counts).
# The rest of curated_corpus_passages (passages[] etc.) is preserved.
_NESTED_STRIPS = (
    ("curated_corpus_passages", "corpus_metadata"),
)


def _strip_nested(chat: dict[str, Any]) -> None:
    """Remove nested sub-fields per _NESTED_STRIPS, in place. Tolerant of
    parent-field absence (parent already top-level-stripped) and child-key
    absence (already missing on this voice). Only operates if parent is a
    dict — list/scalar parents are left alone."""
    for parent, child in _NESTED_STRIPS:
        node = chat.get(parent)
        if isinstance(node, dict) and child in node:
            del node[child]


def build_chat_system_prompt(assembled_card: dict[str, Any]) -> dict[str, Any]:
    """Transform an assembled_card dict into a chat-ready system-prompt dict.

    Mechanical field-strip. No content modification. No marker re-stamp
    (pipeline_version is in the strip set under amendment B).

    Returns a new dict; input is not mutated.
    """
    chat = {
        k: v
        for k, v in assembled_card.items()
        if k not in _VOICE_PIPELINE_ONLY_FIELDS
    }
    # Deep-copy nested-strip parents so we mutate our local copy, not the
    # caller's input. (Top-level strips already produce a new dict above;
    # nested strips need their parents copied before we mutate.)
    for parent, _ in _NESTED_STRIPS:
        if parent in chat and isinstance(chat[parent], dict):
            chat[parent] = dict(chat[parent])
    _strip_nested(chat)

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
