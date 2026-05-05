"""Editor Pipeline — Claudia card loading + system prompt assembly.

Mirrors `runtime/flows/voice/card_assembly.py` with editor-specific routing
per docs/AI_Assembly_Editor_Pipeline.md §"Editor card → System Prompt
Assembly". The differences:

  - Card lives at <PROJECT_ROOT>/editor/tim_leberecht/07_persona_card_assembled.json
    (not under voices/)
  - Engagement section has 2 fields, not 3 (no unique_contribution — Claudia
    is structurally distinct from panel voices)
  - reference_only_passages is N/A for Claudia (no copyrighted corpus to
    ground in)
  - No continuity blocks (Editor is per-night fresh; no cross-night carryover)
  - Single step (dossier-generation), not Steps 1/2/3

The four load-bearing strip rules from voice card assembly carry over:
  - Drop `metadata` (build-time provenance)
  - Drop `smoke_test_chains` (NEVER few-shot)
  - Drop `curated_corpus_passages.corpus_metadata` (FU#41 nested-strip)
  - reference_only_passages: dropped if present (Claudia has none, but
    defensively strip)

Returns a (prefix, tail) tuple with prefix-cache breakpoint after BOUNDARIES,
matching the voice pipeline pattern. All per-night dossier calls (3-5 per
night) share the cached prefix; the per-dossier theme/voice payload lives in
the user prompt, not the system tail.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Iterable

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from flows.shared.io import load_prompt  # noqa: E402
from flows.shared.project_root import resolve_project_root  # noqa: E402


# --- Field routing per docs/AI_Assembly_Editor_Pipeline.md ----------------


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

# Reasoning method — same set as voice pipeline.
_REASONING_METHOD = (
    "reasoning_method",
    "finds_compelling",
    "resists",
)

# Engagement — TWO fields (no unique_contribution; Claudia is the editor,
# not a contributing voice — she has no "what only she could add" claim
# in the same sense).
_ENGAGEMENT = (
    "default_questions",
    "disagreement_protocol",
)

# Voice / expression — same set as voice pipeline.
_VOICE_FIELDS = (
    "rhetorical_mode",
    "characteristic_moves",
    "register_and_tone",
    "metaphorical_repertoire",
    "preferred_vocabulary",
    "banned_language",
    "banned_modes",
)

# Artifact — same as voice's Step 2 set (8 fields). Editor's task is
# always "produce a dossier"; there's no Step 1/3 distinction.
_ARTIFACT = (
    "medium",
    "technical_capabilities",
    "characteristic_output_structure",
    "relationship_to_detailed_response",
    "aesthetic_qualities",
    "stance_tendency",
    "length_and_format_constraints",
    "quality_criteria",
)

# Always-drop fields.
_ALWAYS_DROP_TOP_LEVEL = ("metadata", "smoke_test_chains")
_NESTED_STRIP = ("curated_corpus_passages", "corpus_metadata")

EDITOR_CARD_SUBPATH = Path("editor") / "tim_leberecht" / "07_persona_card_assembled.json"


# --- Loaders --------------------------------------------------------------


def load_editor_card(project_root: Path | None = None) -> dict[str, Any]:
    """Load Claudia's assembled persona card from PROJECT_ROOT/editor/...

    Raises FileNotFoundError with a clear message if absent — the editor
    pipeline cannot run without the card. Per the spec's defensive checks,
    callers should fail loud rather than silently use a default voice.
    """
    pr = project_root or resolve_project_root(None)
    path = pr / EDITOR_CARD_SUBPATH
    if not path.exists():
        raise FileNotFoundError(
            f"Editor card not found at {path}.\n"
            f"Claudia's hand-authored card must exist before the editor "
            f"pipeline runs. See docs/AI_Assembly_Editor_Pipeline.md "
            f"§'The Editor — Claudia Pinchbeck'."
        )
    with path.open(encoding="utf-8") as f:
        return json.load(f)


# --- Rendering ------------------------------------------------------------


def _render_value(value: Any) -> str:
    """Render a field value for inclusion in the system prompt.

    Mirrors voice/card_assembly.py — strings render verbatim; dicts/lists
    render as JSON for structural fidelity.
    """
    if isinstance(value, str):
        return value
    return json.dumps(value, indent=2, ensure_ascii=False)


def _strip_nested_corpus_metadata(curated: Any) -> Any:
    """Drop curated_corpus_passages[*].corpus_metadata (FU#41 strip)."""
    if not isinstance(curated, list):
        return curated
    out = []
    for item in curated:
        if not isinstance(item, dict):
            out.append(item)
            continue
        cleaned = {k: v for k, v in item.items() if k != "corpus_metadata"}
        out.append(cleaned)
    return out


def _render_section(
    card: dict[str, Any],
    header: str,
    fields: Iterable[str],
) -> str:
    """Render a `# HEADER` section followed by populated fields.

    Empty / absent fields are skipped silently. The nested
    `corpus_metadata` strip is applied transparently when curated_corpus_passages
    is rendered.
    """
    lines = [f"\n# {header}\n"]
    any_rendered = False
    for field in fields:
        if field not in card:
            continue
        value = card[field]
        if value is None or value == "" or value == [] or value == {}:
            continue
        if field == "curated_corpus_passages":
            value = _strip_nested_corpus_metadata(value)
        lines.append(f"## {field}\n\n{_render_value(value)}\n")
        any_rendered = True
    if not any_rendered:
        return ""
    return "".join(lines)


# --- System prompt assembly ----------------------------------------------


def assemble_system_prompt(
    card: dict[str, Any],
    *,
    night: int = 1,
) -> tuple[str, str]:
    """Assemble Claudia's dossier-generation system prompt.

    Returns (prefix, tail) for prefix-cache control. The prefix is identical
    across all dossier calls within a night; the tail carries the closing
    instruction (the same `editor_dossier.md` prompt for every call).

    `night` is accepted for API symmetry with the voice pipeline but is not
    used in the prompt itself — Claudia's editorial frame is night-agnostic;
    night-specific context comes via the user prompt (theme + artifacts).
    """
    if night not in (1, 2, 3):
        raise ValueError(f"night must be 1, 2, or 3 (got {night})")

    # Filter always-drop fields. Claudia has no reference_only_passages, but
    # defensively strip if present.
    filtered = {
        k: v for k, v in card.items()
        if k not in _ALWAYS_DROP_TOP_LEVEL
    }
    filtered.pop("reference_only_passages", None)

    # ---- Prefix (byte-identical across all dossier calls per night) ----
    name = filtered.get("council_member_name", "Claudia Pinchbeck")
    prefix_parts = [f"You are {name}.\n"]

    # IDENTITY
    prefix_parts.append(_render_section(
        filtered, "IDENTITY",
        ("epistemic_frame_statement", "world", "formative_experience", "character"),
    ))
    # CONSTITUTION
    prefix_parts.append(_render_section(
        filtered, "CONSTITUTION",
        ("constitution", "concept_lexicon", "curated_corpus_passages"),
    ))
    # BOUNDARIES + TEMPORAL STANCE
    prefix_parts.append(_render_section(
        filtered, "BOUNDARIES",
        ("knowledge_boundary", "translation_protocol", "topics_requiring_care",
         "hard_limits", "voice_temporal_stance"),
    ))

    # ---- Tail (loads after the cache breakpoint) ----
    tail_parts = []
    tail_parts.append(_render_section(filtered, "REASONING METHOD", _REASONING_METHOD))
    tail_parts.append(_render_section(filtered, "ENGAGEMENT", _ENGAGEMENT))
    tail_parts.append(_render_section(filtered, "VOICE", _VOICE_FIELDS))
    tail_parts.append(_render_section(filtered, "ARTIFACT", _ARTIFACT))

    closing = load_prompt("editor_dossier")
    tail_parts.append(f"\n---\n\n# YOUR TASK\n\n{closing}\n")

    return "".join(prefix_parts), "".join(tail_parts)
