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
  Reasoning method (3 fields, ALL steps as of 2026-05-02): reasoning_method,
    finds_compelling, resists.
  Engagement (3 fields, ALL steps as of 2026-05-02): default_questions,
    disagreement_protocol, unique_contribution.
    Routing change 2026-05-02: previously Step 1 + Step 3 only (Step 2
    received only unique_contribution as a "focus anchor"). Extended to
    Step 2 because voice_step2_artifact.md decision_1_focus explicitly
    cites finds_compelling and resists as focus anchors for the
    artifact's focus decision — but those fields were not in Step 2's
    system prompt scope. Test 2 v2 retrospective showed all 4 voices
    chose "weave across all" focus decisions; the broad anchors that
    WERE loaded (formative_experience, constitution, unique_contribution)
    apply to all detailed responses, while the sharp discriminators
    (finds_compelling, resists) were missing. This was a prompt/system
    mismatch, not a prompt-engineering concern. See OPEN_ITEMS C18+C20.
    FU#57 (2026-04-29): bold_engagement_topics is NOT loaded into
    runtime system prompts — empirical observation that chat-test
    performs better stripped. Field is still emitted by Pass 5 for
    build-side audit value.
  Voice/expression (7 fields, ALL steps as of 2026-05-02):
    rhetorical_mode, characteristic_moves, register_and_tone,
    metaphorical_repertoire, preferred_vocabulary, banned_language,
    banned_modes.
    Routing change 2026-05-02: previously Step 2 + Step 3 only.
    Extended to Step 1 so voice register, banned modes, and
    characteristic moves are present from the cold-start of detailed
    reasoning — not added in a downstream wrapping step. Aligns with
    cold-start conditioning research (briefing 2026-05-02): voice
    fidelity benefits from voice machinery being declared at the
    point of generation, not deferred. Token cost ~+5K cached/voice;
    cached reads thereafter negligible.
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

from flows.shared.io import (
    load_conference_facts,
    load_council_config,
    load_prompt,
    member_slug,
)
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

# Reasoning method — rendered as REASONING METHOD section in all steps
# (1, 2, 3) as of 2026-05-02 routing refactor. Previously Step 1 + 3 only.
# finds_compelling + resists are sharp focus discriminators that Step 2's
# decision_1 prompt explicitly anchors in but were not in scope before.
_REASONING_METHOD = (
    "reasoning_method",
    "finds_compelling",
    "resists",
)

# Engagement — rendered as ENGAGEMENT section in all steps (1, 2, 3) as of
# 2026-05-02 routing refactor. Previously Step 1 + 3 received the full
# triple; Step 2 received only unique_contribution as a "focus anchor" via
# the now-removed _FOCUS_ANCHOR set. unique_contribution stays in this
# group as the focus discriminator the prompt cites.
# FU#57 (2026-04-29): bold_engagement_topics dropped from runtime — see
# header docstring.
_ENGAGEMENT = (
    "default_questions",
    "disagreement_protocol",
    "unique_contribution",
)

# Voice / expression — rendered as VOICE section in all steps (1, 2, 3)
# as of 2026-05-02 routing refactor. Previously Step 2 + 3 only. Loading
# in Step 1 puts banned_modes / banned_language / register_and_tone in
# scope at the cold-start of detailed reasoning so the voice produces
# in-register from the first token (vs default-AI register that Step 2
# then has to translate).
_VOICE = (
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
            # C20a (2026-05-04): cross-night signature-moves register —
            # accumulated across all prior nights so Night 2 sees Night 1's
            # moves and Night 3 sees Night 1's + Night 2's. Rendered into
            # Step 2's system prompt as a "moves already deployed this
            # conference" warning section. Empty/missing → not rendered.
            if "signature_moves_deployed" in override:
                card["signature_moves_deployed"] = override["signature_moves_deployed"]

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


def _unwrap_voice_temporal_stance(vts: Any, *, deployment: str = "athens") -> str:
    """Unwrap the two-part voice_temporal_stance to the single block of
    prose the voice will actually see.

    Athens (the Voice Pipeline's only current runtime deployment) uses
    `default`. The `anchored_override` field exists for chat-test
    deployments (consumed by personas/derive when building the
    chat_system_prompt) and MUST NOT be used at Voice Pipeline runtime
    even when populated — picking it would substitute a deployment-
    specific anchored chronology for the open-deployment fluid framing
    the Voice Pipeline is contracted against.

    `deployment` parameter is a forward hook in case a non-Athens
    runtime deployment ever needs the override path; current callers
    do not pass it.

    Defensive: if the field is already a string (older cards or
    hand-edited), pass through unchanged. If the chosen variant is
    missing, fall back to the other rather than silently dropping
    content.
    """
    if isinstance(vts, str):
        return vts
    if not isinstance(vts, dict):
        return json.dumps(vts, indent=2, ensure_ascii=False)

    default = vts.get("default")
    override = vts.get("anchored_override")

    if deployment == "athens":
        primary, secondary = default, override
    else:
        primary, secondary = override, default

    for candidate in (primary, secondary):
        if candidate:
            return candidate if isinstance(candidate, str) else json.dumps(
                candidate, indent=2, ensure_ascii=False
            )

    # Neither populated — fall back to dumping the whole dict so the
    # operator sees something during dry-run and can investigate.
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
    Step 2 reads continuity_block_artifact_if_night_N (focus/stance/form)
      AND the cross-night signature_moves_deployed register (C20a).
    Step 3 reads BOTH continuity blocks.
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
    # Step 2 only: the cross-night signature-moves register. Voice sees
    # what they've already deployed this conference and decides whether
    # tonight's matter genuinely calls for the same moves again or
    # whether different moves serve better. Empty list → no section.
    if step == 2:
        moves = card.get("signature_moves_deployed") or []
        if moves:
            blocks.append(
                "\n---\n\n# MOVES YOU HAVE ALREADY DEPLOYED THIS CONFERENCE\n\n"
                "Below is a register of signature moves your prior nights' artifacts deployed. "
                "Re-using a stock anecdote, signature phrasing, or distinctive closing shape across "
                "multiple nights risks calcifying it into a tic the audience notices. Before tonight's "
                "artifact, consider for each move whether tonight's matter genuinely calls for it again, "
                "or whether a different move serves better.\n\n"
            )
            for entry in moves:
                if not isinstance(entry, dict):
                    continue
                summary = entry.get("move_summary", "")
                where = entry.get("where_used", "")
                quote = entry.get("short_quote", "")
                blocks.append(f"- **{summary}** (`{where}`)")
                if quote:
                    blocks.append(f" — “{quote}”")
                blocks.append("\n")
            blocks.append("\n")
    return "".join(blocks)


# --- System prompt assembly per step ----------------------------------

def _try_load_deployment_sources(
    council: dict[str, Any] | None,
    conference: dict[str, Any] | None,
) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    """Best-effort loaders for council_config + conference_facts.

    Used by `assemble_system_prompt` to fetch deployment context when
    callers don't pass it explicitly. Failures (missing PROJECT_ROOT,
    missing files, schema errors) return None so test fixtures that
    don't set up the JSON sources still produce a valid system prompt
    — the deployment-context block degrades to empty rather than
    raising. Production paths (orchestrator + voice_flow CLI) always
    have these files at PROJECT_ROOT.
    """
    if council is None:
        try:
            council = load_council_config()
        except (FileNotFoundError, ValueError, SystemExit):
            council = None
    if conference is None:
        try:
            conference = load_conference_facts()
        except (FileNotFoundError, ValueError, SystemExit):
            conference = None
    return council, conference


def _render_deployment_context(
    council: dict[str, Any] | None,
    conference: dict[str, Any] | None,
    self_voice_slug: str | None,
    step: int,
) -> str:
    """Render the deployment-context block: room / panel / readers.

    Three (sometimes four) sub-blocks lifted from operator-curated JSON:

    - **THE GATHERING** — `conference_facts.conference_context_paragraph`.
      Names the conference's character (twelve thematic tracks, Aegean
      Intelligence framing, marketing-vs-substance contrast, agency
      centre of gravity). Same on every step.

    - **THE PANEL** — `council_config.collective_landscape`. Panel-as-
      friction-structure framing, member roster with tradition tags,
      panel fault lines derived from member fields. Same on every step.

    - **YOUR FELLOW VOICES** — Step 2 only. Names the other 9 voices
      (excludes self) and frames the listing as anti-translation
      permission. Step 1 is private reasoning; full peer roster at
      reasoning-time invites premature peer-positioning. Step 2 is
      composition where peer-awareness genuinely earns its place.

    - **YOUR READERS** — `council_config.audience`. Synced 1:1 with
      `audience_profile.json::participant_profile` (canonical source per
      `docs/AUDIENCE_BRIEF.md`). Descriptive — what readers activate
      on, what they go flat on, where their stretch is.

    Intentional omission: `conference_facts.session_role_for_ai_assembly`
    is NOT injected here, even though it carries the project's three-
    bars + anti-smoothing directives. Reason: that text reads as an
    imperative ("the voice marks ... rather than smoothing ..."), and
    putting prescriptive language in the deployment-context layer
    conflates with the persona card's task-instruction layer (`<task>`,
    `<weighing>`, `<focus>`, etc. in the closing prompt). Deployment
    context stays descriptive; the persona card retains its monopoly
    on prescription.

    Returns "" if neither source is available — the system prompt
    proceeds without deployment context (test fixtures + edge cases).
    """
    if council is None and conference is None:
        return ""
    parts: list[str] = []

    if conference and conference.get("conference_context_paragraph"):
        parts.append("\n## THE GATHERING\n\n")
        parts.append(conference["conference_context_paragraph"].strip())

    if council and council.get("collective_landscape"):
        parts.append("\n\n## THE PANEL\n\n")
        parts.append(council["collective_landscape"].strip())

    if step == 2 and council and self_voice_slug:
        peers = [
            m["name"] for m in council.get("members", [])
            if member_slug(m.get("name", "")) != self_voice_slug
        ]
        if peers:
            parts.append("\n\n## YOUR FELLOW VOICES\n\n")
            parts.append(
                "Your work appears alongside the others on shared themes:\n\n"
            )
            for p in peers:
                parts.append(f"- {p}\n")
            parts.append(
                "\nNone of these voices translate themselves into a common "
                "register. The gathering is built to hold the friction of their "
                "differences. You speak from your tradition; the room does not "
                "need you to soften."
            )

    if council and council.get("audience"):
        parts.append("\n\n## YOUR READERS\n\n")
        parts.append(council["audience"].strip())

    return "".join(parts)


def assemble_system_prompt(
    card: dict[str, Any],
    step: int,
    night: int = 1,
    council: dict[str, Any] | None = None,
    conference: dict[str, Any] | None = None,
) -> tuple[str, str]:
    """Assemble the system prompt for one step.

    Returns a `(prefix, tail)` tuple to enable prefix-cache-control:
      - `prefix` is the byte-identical-across-steps shared portion
        (name + IDENTITY + CONSTITUTION + BOUNDARIES). All Step 1, 2,
        and 3 calls for the same voice on the same night share this
        exact prefix string.
      - `tail` is the step-specific portion (reference_only_passages
        for Step 1; reasoning + engagement + voice + artifact for
        Step 2/3; continuity overlay; closing prompt).

    `stream_voice_call` places `cache_control` on both blocks (1h TTL),
    so all calls on the same voice/night hit the prefix cache regardless
    of step (~20-25K tokens of cached input shared across Step 1's 3-5
    calls, Step 2's 1 call, and Step 3's 1 call when enabled). See
    OPEN_ITEMS C19a + 2026-05-02 prefix-caching extension.

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

    # ----- Shared prefix (byte-identical across Step 1/2/3) ---------
    # Render the foundational sections that every step receives identically.
    # This is the cache-eligible shared prefix; placing a cache_control
    # breakpoint at its end (in stream_voice_call) lets Step 2 + Step 3
    # calls READ the prefix that Step 1's first call wrote.
    prefix_parts = []
    name = filtered.get("council_member_name", "this voice")
    prefix_parts.append(f"You are {name}.\n")

    # IDENTITY (5 fields, but council_member_name already opened the prompt).
    prefix_parts.append(
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
    prefix_parts.append(
        _render_section(
            filtered,
            "CONSTITUTION",
            ("constitution", "concept_lexicon", "curated_corpus_passages"),
        )
    )
    # BOUNDARIES + TEMPORAL STANCE (5 fields including voice_temporal_stance).
    prefix_parts.append(
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

    # ----- Deployment context (room / panel / readers) ---------------
    # Sourced from PROJECT_ROOT/conference_facts.json + council_config.json.
    # Stable per-deployment so it sits in the cache-shared prefix (shared
    # across step 1/2/3 calls for the same voice on the same night).
    # `session_role_for_ai_assembly` deliberately omitted — see
    # `_render_deployment_context` docstring. Loader is best-effort:
    # missing files / no PROJECT_ROOT → empty block, system prompt
    # proceeds without deployment context.
    council_loaded, conference_loaded = _try_load_deployment_sources(
        council, conference
    )
    self_slug = (
        member_slug(filtered["council_member_name"])
        if filtered.get("council_member_name")
        else None
    )
    deployment_block = _render_deployment_context(
        council_loaded, conference_loaded, self_slug, step
    )
    if deployment_block:
        prefix_parts.append(deployment_block)

    # ----- Step-specific tail ----------------------------------------
    # Everything after BOUNDARIES diverges by step. Rendered separately
    # so the prefix above can be cached and shared.
    tail_parts = []

    # reference_only_passages is Step 1 only — render it as its own
    # section after CONSTITUTION so the voice can ground reasoning in
    # its actual words. The runtime_contract_note inside the field
    # already carries its own warning.
    if step == 1 and "reference_only_passages" in filtered:
        tail_parts.append(
            _render_section(
                filtered,
                "REFERENCE-ONLY PASSAGES (your actual words; ground reasoning here)",
                ("reference_only_passages",),
            )
        )

    # Reasoning method + engagement — all steps (2026-05-02 refactor;
    # previously Step 1 + Step 3 only, with Step 2 receiving only
    # unique_contribution as a "focus anchor"). See header docstring.
    tail_parts.append(_render_section(filtered, "REASONING METHOD", _REASONING_METHOD))
    tail_parts.append(_render_section(filtered, "ENGAGEMENT", _ENGAGEMENT))

    # Voice / expression — all steps (2026-05-02 refactor; previously
    # Step 2 + Step 3 only). banned_modes / banned_language / register
    # in scope from cold-start of Step 1 reasoning.
    tail_parts.append(_render_section(filtered, "VOICE", _VOICE))

    # Artifact — Step 2 + Step 3 only (artifact-specific fields).
    if step in (2, 3):
        artifact_fields = _STEP2_ARTIFACT if step == 2 else _STEP3_ARTIFACT
        tail_parts.append(_render_section(filtered, "ARTIFACT", artifact_fields))

    # Continuity (Night 2+).
    tail_parts.append(_render_continuity(filtered, night, step))

    # Closing instruction (XML-tagged) loaded from prompts/.
    closing_prompt_name = {
        1: "voice_step1_reasoning",
        2: "voice_step2_artifact",
        3: "voice_step3_amendment",
    }[step]
    closing = load_prompt(closing_prompt_name)
    tail_parts.append(f"\n---\n\n# YOUR TASK\n\n{closing}\n")

    return "".join(prefix_parts), "".join(tail_parts)


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
