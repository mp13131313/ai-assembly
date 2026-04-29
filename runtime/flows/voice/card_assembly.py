"""Voice Pipeline — card loading + per-step system prompt assembly.

Load the assembled persona card from PROJECT_ROOT, apply the field-
routing matrix per docs/AI_Assembly_Voice_Pipeline.md §"Card → System
Prompt Assembly", and produce a system prompt for Steps 1 / 2 / 3.

The four load-bearing strip rules (always enforced):
  - Drop `metadata` (build-time provenance)
  - Drop `smoke_test_chains` (NEVER few-shot — see HANDOFF.md)
  - Drop `reference_only_passages` from Step 2 + Step 3 (copyright)
  - Drop `curated_corpus_passages.corpus_metadata` (FU#41 nested-strip)

Per-step field routing (canonical table — see spec §"Field-routing
table"):
  Foundational (13 fields, all steps): council_member_name,
    epistemic_frame_statement, world, formative_experience, character,
    constitution, concept_lexicon, curated_corpus_passages,
    knowledge_boundary, translation_protocol, topics_requiring_care,
    hard_limits, voice_temporal_stance.
  Reasoning/engagement (Step 1 + Step 3): reasoning_method,
    finds_compelling, resists, default_questions, disagreement_protocol.
    Plus bold_engagement_topics + unique_contribution which also
    appear in Step 2 (anchor focus decision).
  Voice (Step 2 + Step 3): rhetorical_mode, characteristic_moves,
    register_and_tone, metaphorical_repertoire, preferred_vocabulary,
    banned_language, banned_modes.
  Artifact (Step 2 + Step 3, except relationship_to_detailed_response
    which is Step 2 only): medium, technical_capabilities,
    characteristic_output_structure, relationship_to_detailed_response,
    aesthetic_qualities, stance_tendency, length_and_format_constraints,
    quality_criteria.
  Continuity (Night 2+ via override file): continuity_block_if_night_2
    (Step 1 + Step 3); continuity_block_artifact_if_night_2 (Step 2 +
    Step 3). On Night 3 the same fields carry merged Nights 1+2 content.

The closing instruction is loaded from
runtime/flows/shared/prompts/voice_step{1,2,3}_*.md and appended to the
rendered card.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Iterable

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from flows.shared.io import load_prompt
from flows.shared.project_root import resolve_project_root


# --- Field routing per docs/AI_Assembly_Voice_Pipeline.md ---------------

_FOUNDATIONAL = (
    "council_member_name",
    "epistemic_frame_statement",
    "world",
    "formative_experience",
    "character",
    "constitution",
    "concept_lexicon",
    "curated_corpus_passages",
    "knowledge_boundary",
    "translation_protocol",
    "topics_requiring_care",
    "hard_limits",
    "voice_temporal_stance",
)

# Step 1 reasoning/engagement (Step 3 also reads these).
_STEP1_REASONING = (
    "reasoning_method",
    "finds_compelling",
    "resists",
    "default_questions",
    "disagreement_protocol",
)

# Routed to Step 1 + Step 2 (focus anchors) + Step 3.
_BOLD_PLUS_UNIQUE = (
    "bold_engagement_topics",
    "unique_contribution",
)

# Voice / expression (Step 2 + Step 3).
_STEP2_VOICE = (
    "rhetorical_mode",
    "characteristic_moves",
    "register_and_tone",
    "metaphorical_repertoire",
    "preferred_vocabulary",
    "banned_language",
    "banned_modes",
)

# Artifact (Step 2 + Step 3, except relationship_to_detailed_response).
_STEP2_ARTIFACT = (
    "medium",
    "technical_capabilities",
    "characteristic_output_structure",
    "relationship_to_detailed_response",
    "aesthetic_qualities",
    "stance_tendency",
    "length_and_format_constraints",
    "quality_criteria",
)

# Step 3 artifact set drops relationship_to_detailed_response (Step 2-specific).
_STEP3_ARTIFACT = tuple(
    f for f in _STEP2_ARTIFACT if f != "relationship_to_detailed_response"
)

# Always-drop fields (4-place load-bearing rule + nested strip).
_ALWAYS_DROP_TOP_LEVEL = ("metadata", "smoke_test_chains")
_NESTED_STRIP = ("curated_corpus_passages", "corpus_metadata")  # nested under parent

# reference_only_passages: kept in Step 1, dropped from Step 2 + Step 3.


def load_persona_card(
    voice_slug: str,
    night: int = 1,
    project_root: Path | None = None,
) -> dict[str, Any]:
    """Load the assembled persona card + apply continuity override on Night 2+.

    Reads `<PROJECT_ROOT>/voices/<voice_slug>/07_persona_card_assembled.json`.
    On Night 2+, also reads
    `<PROJECT_ROOT>/voices/<voice_slug>/continuity_night_<night>.json` (if
    present) and overlays its two continuity_block_* fields onto the card.
    """
    if project_root is None:
        project_root = resolve_project_root(None)
    card_path = (
        project_root / "voices" / voice_slug / "07_persona_card_assembled.json"
    )
    if not card_path.exists():
        raise FileNotFoundError(
            f"Persona card not found: {card_path}. "
            f"Expected the Persona Pipeline v4 output at this path "
            f"(see personas/HANDOFF.md)."
        )
    with open(card_path, encoding="utf-8") as f:
        card = json.load(f)

    if night >= 2:
        override_path = (
            project_root
            / "voices"
            / voice_slug
            / f"continuity_night_{night}.json"
        )
        if override_path.exists():
            with open(override_path, encoding="utf-8") as f:
                override = json.load(f)
            for key in (
                f"continuity_block_if_night_{night}",
                f"continuity_block_artifact_if_night_{night}",
            ):
                if key in override:
                    card[key] = override[key]

    return card


# --- Field rendering --------------------------------------------------

def _render_value(value: Any) -> str:
    """Render a single card-field value for inclusion in a system prompt.

    Strings pass through; lists/dicts pretty-print as JSON. The persona
    pipeline emits mixed shapes (some fields are list-of-string, some
    list-of-dict, some nested objects); JSON dump handles all.
    """
    if isinstance(value, str):
        return value
    return json.dumps(value, indent=2, ensure_ascii=False)


def _strip_nested_corpus_metadata(curated: Any) -> Any:
    """FU#41 nested strip: drop `corpus_metadata` from `curated_corpus_passages`.

    Parent dict preserved with `passages[]` intact. No-op if structure
    isn't a dict or doesn't carry the nested field.
    """
    if not isinstance(curated, dict):
        return curated
    out = {k: v for k, v in curated.items() if k != "corpus_metadata"}
    return out


def _unwrap_voice_temporal_stance(vts: Any) -> str:
    """Per spec §"What the Voice Pipeline Knows §1": Athens uses the
    `default` text. If `anchored_override` is non-null, the operator
    selected a non-Athens deployment and the override is used instead.
    Either way, the voice sees a single block of prose, not the JSON
    container with both keys.

    Defensive: if the field is already a string (older cards or hand-
    edited), pass through unchanged. If the dict has neither key
    populated, fall back to JSON dump so nothing is silently dropped.
    """
    if isinstance(vts, str):
        return vts
    if not isinstance(vts, dict):
        return json.dumps(vts, indent=2, ensure_ascii=False)
    override = vts.get("anchored_override")
    if override:  # non-null + non-empty
        return override if isinstance(override, str) else json.dumps(
            override, indent=2, ensure_ascii=False
        )
    default = vts.get("default")
    if default:
        return default if isinstance(default, str) else json.dumps(
            default, indent=2, ensure_ascii=False
        )
    # Neither key populated — fall back to dumping the whole dict so
    # the operator sees something during dry-run and can investigate.
    return json.dumps(vts, indent=2, ensure_ascii=False)


def _render_section(card: dict[str, Any], header: str, fields: Iterable[str]) -> str:
    """Render a named section of the system prompt from the card.

    Outputs a markdown-style header followed by each present field as
    `### <field_name>\\n<value>`. Missing fields are silently skipped
    (the orchestrator should ensure required fields exist; missing
    optional fields just don't appear).

    Two field-specific transforms are applied here:
      - `curated_corpus_passages`: nested strip of `corpus_metadata`
      - `voice_temporal_stance`: unwrap to default (or anchored_override
        if non-null) text so the voice reads clean prose, not JSON
    """
    lines = [f"\n---\n\n# {header}\n"]
    for field in fields:
        if field not in card:
            continue
        value = card[field]
        if field == "curated_corpus_passages":
            value = _strip_nested_corpus_metadata(value)
        if field == "voice_temporal_stance":
            value = _unwrap_voice_temporal_stance(value)
        lines.append(f"\n### {field}\n")
        lines.append(_render_value(value))
        lines.append("\n")
    return "".join(lines)


def _render_continuity(card: dict[str, Any], night: int, step: int) -> str:
    """Render Night 2+ continuity blocks into the system prompt.

    Step 1 reads continuity_block_if_night_N (positions/moves/threads).
    Step 2 reads continuity_block_artifact_if_night_N (focus/stance/form).
    Step 3 reads BOTH.
    Night 1 has no continuity; returns empty string.
    """
    if night < 2:
        return ""
    blocks = []
    cb_reasoning = card.get(f"continuity_block_if_night_{night}")
    cb_artifact = card.get(f"continuity_block_artifact_if_night_{night}")
    if step in (1, 3) and cb_reasoning:
        blocks.append("\n---\n\n# WHAT YOU CARRIED FORWARD FROM NIGHT N-1 (your reasoning memory)\n\n")
        blocks.append(_render_value(cb_reasoning))
        blocks.append("\n")
    if step in (2, 3) and cb_artifact:
        blocks.append("\n---\n\n# YOUR PIECE FROM NIGHT N-1 (memory of focus, stance, form)\n\n")
        blocks.append(_render_value(cb_artifact))
        blocks.append("\n")
    return "".join(blocks)


# --- System prompt assembly per step ----------------------------------

def assemble_system_prompt(
    card: dict[str, Any],
    step: int,
    night: int = 1,
) -> str:
    """Assemble the system prompt for one step.

    step: 1 (Private Reasoning) | 2 (First-Draft Artifact) | 3 (Amended Artifact).
    night: 1 | 2 | 3 — controls continuity-block inclusion.

    Field routing per the canonical matrix in
    docs/AI_Assembly_Voice_Pipeline.md §"Card → System Prompt Assembly".

    Strip rules (enforced here, never bypassed):
      - metadata + smoke_test_chains: always dropped
      - reference_only_passages: kept on Step 1, dropped on Step 2 + 3
      - curated_corpus_passages.corpus_metadata: nested-stripped always
    """
    if step not in (1, 2, 3):
        raise ValueError(f"step must be 1, 2, or 3 (got {step})")
    if night not in (1, 2, 3):
        raise ValueError(f"night must be 1, 2, or 3 (got {night})")

    # Filter out always-drop top-level fields.
    filtered = {
        k: v
        for k, v in card.items()
        if k not in _ALWAYS_DROP_TOP_LEVEL
    }

    # Step 2 + Step 3 drop reference_only_passages (copyright).
    if step in (2, 3):
        filtered.pop("reference_only_passages", None)

    # Render foundational sections (header per spec).
    parts = []
    name = filtered.get("council_member_name", "this voice")
    parts.append(f"You are {name}.\n")

    # IDENTITY (5 fields, but council_member_name already opened the prompt).
    parts.append(
        _render_section(
            filtered,
            "IDENTITY",
            (
                "epistemic_frame_statement",
                "world",
                "formative_experience",
                "character",
            ),
        )
    )
    # CONSTITUTION (3 fields).
    parts.append(
        _render_section(
            filtered,
            "CONSTITUTION",
            ("constitution", "concept_lexicon", "curated_corpus_passages"),
        )
    )
    # BOUNDARIES + TEMPORAL STANCE (5 fields including voice_temporal_stance).
    parts.append(
        _render_section(
            filtered,
            "BOUNDARIES",
            (
                "knowledge_boundary",
                "translation_protocol",
                "topics_requiring_care",
                "hard_limits",
                "voice_temporal_stance",
            ),
        )
    )

    # reference_only_passages is Step 1 only — render it as its own
    # section after CONSTITUTION so the voice can ground reasoning in
    # its actual words. The runtime_contract_note inside the field
    # already carries its own warning.
    if step == 1 and "reference_only_passages" in filtered:
        parts.append(
            _render_section(
                filtered,
                "REFERENCE-ONLY PASSAGES (your actual words; ground reasoning here)",
                ("reference_only_passages",),
            )
        )

    # Step 1 + Step 3: reasoning + engagement.
    if step in (1, 3):
        parts.append(
            _render_section(
                filtered,
                "REASONING METHOD",
                ("reasoning_method", "finds_compelling", "resists"),
            )
        )
        parts.append(
            _render_section(
                filtered,
                "ENGAGEMENT",
                (
                    "bold_engagement_topics",
                    "default_questions",
                    "disagreement_protocol",
                    "unique_contribution",
                ),
            )
        )

    # Step 2: bold_engagement_topics + unique_contribution as focus anchors.
    if step == 2:
        parts.append(
            _render_section(
                filtered,
                "ENGAGEMENT (anchors for focus decision)",
                _BOLD_PLUS_UNIQUE,
            )
        )

    # Step 2 + Step 3: voice + artifact fields.
    if step in (2, 3):
        parts.append(_render_section(filtered, "VOICE", _STEP2_VOICE))
        artifact_fields = _STEP2_ARTIFACT if step == 2 else _STEP3_ARTIFACT
        parts.append(_render_section(filtered, "ARTIFACT", artifact_fields))

    # Continuity (Night 2+).
    parts.append(_render_continuity(filtered, night, step))

    # Closing instruction (XML-tagged) loaded from prompts/.
    closing_prompt_name = {
        1: "voice_step1_reasoning",
        2: "voice_step2_artifact",
        3: "voice_step3_amendment",
    }[step]
    closing = load_prompt(closing_prompt_name)
    parts.append(f"\n---\n\n# YOUR TASK\n\n{closing}\n")

    return "".join(parts)


# --- User-prompt filters (strip pipeline-meta from upstream JSON) ----

def filter_theme_record_for_step1(full_theme_record: dict[str, Any]) -> dict[str, Any]:
    """Strip pipeline-meta from a briefing's full_theme_record before
    showing it to the voice in Step 1.

    Per spec §"Step 1 — Private Reasoning > User prompt shape":
      Drop:  theme_flags (audience_friction, fault_line_*, theme_quality)
      Drop:  co_assigned_voices (panel composition leak)
      Rename: theme_title_from_researcher → theme_title (drop "_from_researcher")
      Rename: theme_abstract_from_researcher → theme_abstract
      Rename: grounding_extraction_ids → extractions_grounding_this_formulation
      Keep:  clusters[] (essential — speakers, lens, extraction text)
    """
    out: dict[str, Any] = {}
    if "theme_title_from_researcher" in full_theme_record:
        out["theme_title"] = full_theme_record["theme_title_from_researcher"]
    if "theme_abstract_from_researcher" in full_theme_record:
        out["theme_abstract"] = full_theme_record["theme_abstract_from_researcher"]
    if "clusters" in full_theme_record:
        out["clusters"] = full_theme_record["clusters"]
    if "grounding_extraction_ids" in full_theme_record:
        out["extractions_grounding_this_formulation"] = full_theme_record[
            "grounding_extraction_ids"
        ]
    return out


def filter_first_draft_for_step3(first_draft: dict[str, Any]) -> dict[str, Any]:
    """Strip pipeline-meta from a Step 2 first-draft artifact before
    showing it to a different voice in Step 3.

    Per spec §"Step 3 — Amended Artifact > User prompt":
      Drop:   lineage block (entire), file paths, voice_slug,
              model/token telemetry, thinking_trace, word_count
      Keep:   voice_name (renamed from council_member),
              focus/stance/form decisions + rationales,
              themes_covered, artifact title/subtitle/text
    """
    keep_fields = (
        "council_member",  # → renamed below
        "focus_decision",
        "focus_rationale",
        "stance",
        "stance_rationale",
        "selected_form",
        "form_rationale",
        "themes_covered",
        "artifact_title",
        "artifact_subtitle",
        "artifact_text",
    )
    out: dict[str, Any] = {}
    for k in keep_fields:
        if k in first_draft:
            if k == "council_member":
                out["voice_name"] = first_draft[k]
            else:
                out[k] = first_draft[k]
    return out
