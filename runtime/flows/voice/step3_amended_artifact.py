"""Voice Pipeline Step 3 — Amended Artifact (FU#49E).

One LLM call per voice per night. Voice reads its own first-draft +
other voices' first-drafts on themes it shares with them, decides to
amend (extend / mark-limit / sharpen-disagreement) or stand-pat, and
produces the final artifact.

Per docs/AI_Assembly_Voice_Pipeline.md §"Step 3 — Amended Artifact":
  Model: Opus 4.7 + adaptive thinking, max_tokens=64000
  Streaming: REQUIRED
  Output: 04_voice/step3_amended_artifacts/<voice_slug>.json
  Runs after ALL voices complete Step 2 (Step 3 reads other voices'
  first-drafts).
  Cross-voice user prompt is filtered (filter_first_draft_for_step3)
  to drop pipeline-meta from other voices' files before showing them.
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from anthropic import Anthropic

from flows.shared.io import get_logger, write_json_atomic
from flows.voice.card_assembly import (
    assemble_system_prompt,
    filter_first_draft_for_step3,
    load_persona_card,
)
from flows.voice._anthropic_call import stream_voice_call


VOICE_MODEL = os.environ.get(
    "VOICE_MODEL",
    os.environ.get("CLAUDE_MODEL", "claude-opus-4-7"),
)
VOICE_THINKING = os.environ.get("VOICE_THINKING", "1") != "0"
STEP3_MAX_TOKENS = int(os.environ.get("VOICE_STEP3_MAX_TOKENS", "64000"))


def _thinking_kwargs() -> dict:
    if not VOICE_THINKING:
        return {}
    return {"thinking": {"type": "adaptive"}, "temperature": 1.0}


def _find_shared_themes(
    own: dict[str, Any], other: dict[str, Any]
) -> list[str]:
    """Themes that appear in both voices' Step 2 themes_covered."""
    own_themes = set(own["lineage"].get("themes_covered", []))
    other_themes = set(other["lineage"].get("themes_covered", []))
    return sorted(own_themes & other_themes)


def build_step3_user_prompt(
    own_first_draft: dict[str, Any],
    other_first_drafts: list[dict[str, Any]],
    theme_display_titles: dict[str, str] | None = None,
) -> tuple[str, list[dict[str, Any]]]:
    """Render Step 3 user prompt + return the list of voices_read.

    Per spec §"Step 3 — Amended Artifact > User prompt": cross-voice
    framing uses theme_display_title (human-readable) rather than
    pipeline IDs, and other voices' first-drafts are filtered (drops
    lineage / paths / telemetry / thinking_trace).
    """
    theme_display_titles = theme_display_titles or {}
    voices_read: list[dict[str, Any]] = []
    cross_sections: list[str] = []

    for other in other_first_drafts:
        shared = _find_shared_themes(own_first_draft, other)
        if not shared:
            continue
        other_voice_name = other.get("council_member") or other["lineage"].get(
            "voice_slug", "another voice"
        )
        other_slug = other["lineage"]["voice_slug"]
        voices_read.append({
            "voice_slug": other_slug,
            "council_member": other_voice_name,
            "first_draft_path": f"04_voice/step2_first_draft_artifacts/{other_slug}.json",
            "shared_themes": shared,
        })
        # Render as voice-grammar paragraph naming the shared question
        # by display title (or theme_id fallback if no display title).
        for theme_id in shared:
            display = theme_display_titles.get(theme_id, theme_id)
            cross_sections.append(
                f"\nOn the question of \"{display}\" — addressed by you and {other_voice_name}:\n\n"
                f"{other.get('artifact_text', '').strip()}\n"
            )

    own_form = own_first_draft.get("selected_form", "")
    own_focus = own_first_draft.get("focus_decision", "")
    own_stance = own_first_draft.get("stance", "")
    parts = [
        "The piece you wrote earlier today:\n\n",
        f"[Form: {own_form} | Focus: {own_focus} | Stance: {own_stance}]\n\n",
        f"{own_first_draft.get('artifact_text', '').strip()}\n\n",
        "---\n\n",
        "Pieces written today by other voices whose engagement crossed yours:\n",
    ]
    if cross_sections:
        parts.extend(cross_sections)
    else:
        parts.append("\n(No other voices engaged questions related to yours today.)\n")

    parts.append("\n---\n\n")
    parts.append("FULL RECORD of pieces by other voices you may reference:\n\n")
    filtered_record = [
        filter_first_draft_for_step3(o) for o in other_first_drafts
    ]
    parts.append(json.dumps(filtered_record, indent=2, ensure_ascii=False))
    parts.append("\n")

    return "".join(parts), voices_read


_DECISION_RX = re.compile(
    r"^\s*[*_#\-]*\s*decision\s*[:=]\s*(amend|stand[-\s]?pat)",
    re.IGNORECASE | re.MULTILINE,
)


def _parse_step3_output(raw_text: str) -> dict[str, Any]:
    """Parse the model's Step 3 output into structured fields.

    The model is instructed to state decision + decision_rationale
    first, then list amendments (if any) as structured entries, then
    the amended artifact (or first-draft verbatim if standing pat).
    Defensive parser: if structure isn't found, raw text goes into
    amended_artifact_text and decision defaults to "amend".
    """
    out: dict[str, Any] = {
        "decision": "amend",
        "decision_rationale": "",
        "amendments": [],
        "selected_form": "",
        "form_changed_from_first_draft": False,
        "form_change_rationale": None,
        "amended_artifact_title": "",
        "amended_artifact_subtitle": "",
        "amended_artifact_text": "",
    }
    m = _DECISION_RX.search(raw_text)
    if m:
        d = m.group(1).lower().replace(" ", "-")
        out["decision"] = "stand-pat" if "stand" in d else "amend"

    # Pull amended_artifact_text by anchored label.
    aat_rx = re.compile(
        r"^\s*[*_#\-]*\s*(?:amended[_\s]*)?artifact[_\s]*text\s*[:=]\s*(.+?)\Z",
        re.IGNORECASE | re.MULTILINE | re.DOTALL,
    )
    m = aat_rx.search(raw_text)
    if m:
        out["amended_artifact_text"] = m.group(1).strip()
    else:
        out["amended_artifact_text"] = raw_text.strip()

    for key, label in (
        ("decision_rationale", r"decision[_\s]*rationale"),
        ("selected_form", r"selected[_\s]*form"),
        ("form_change_rationale", r"form[_\s]*change[_\s]*rationale"),
        ("amended_artifact_title", r"(?:amended[_\s]*)?(?:artifact[_\s]*)?title"),
        ("amended_artifact_subtitle", r"(?:amended[_\s]*)?(?:artifact[_\s]*)?subtitle"),
    ):
        rx = re.compile(
            rf"^\s*[*_#\-]*\s*{label}\s*[:=]\s*(.+?)(?=\n\s*[*_#\-]*\s*(?:decision|amendment|selected|form|title|subtitle|amended|artifact)[\s_]*[:=]|\Z)",
            re.IGNORECASE | re.MULTILINE | re.DOTALL,
        )
        m = rx.search(raw_text)
        if m:
            out[key] = m.group(1).strip().rstrip("*").strip()

    if out["form_change_rationale"]:
        out["form_changed_from_first_draft"] = True

    # Amendments parsing: accept either a JSON-fenced block or labelled
    # entries. Best-effort; full structure is the model's responsibility
    # under the closing instruction.
    json_block_rx = re.compile(
        r"```(?:json)?\s*\n([\[{].+?[\]}])\s*\n```",
        re.DOTALL,
    )
    for m in json_block_rx.finditer(raw_text):
        try:
            blob = json.loads(m.group(1))
            if isinstance(blob, list) and blob and isinstance(blob[0], dict):
                if any("cited_voice" in entry for entry in blob):
                    out["amendments"] = blob
                    break
        except json.JSONDecodeError:
            continue

    return out


def run_step3_for_voice(
    voice_slug: str,
    own_first_draft: dict[str, Any],
    other_first_drafts: list[dict[str, Any]],
    night: int,
    run_dir: Path,
    project_root: Path | None = None,
    council_member_name: str | None = None,
    theme_display_titles: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Run Step 3 for one voice. Idempotent.

    other_first_drafts is the list of OTHER voices' Step 2 outputs (this
    voice's own first-draft is passed as own_first_draft separately).
    The orchestrator filters to other_first_drafts before calling.
    """
    logger = get_logger("voice_step3")
    out_dir = run_dir / "04_voice" / "step3_amended_artifacts"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{voice_slug}.json"

    if out_path.exists():
        logger.info(f"  Step 3 cached: {voice_slug}")
        with open(out_path, encoding="utf-8") as f:
            return json.load(f)

    card = load_persona_card(voice_slug, night=night, project_root=project_root)
    if council_member_name is None:
        council_member_name = card.get("council_member_name", voice_slug)

    system = assemble_system_prompt(card, step=3, night=night)
    user, voices_read = build_step3_user_prompt(
        own_first_draft, other_first_drafts, theme_display_titles
    )

    logger.info(
        f"  Step 3 calling: {voice_slug} "
        f"({len(voices_read)} other voices on shared themes)"
    )
    client = Anthropic()
    t0 = time.time()
    raw_text, thinking_trace, final = stream_voice_call(
        client,
        model=VOICE_MODEL,
        max_tokens=STEP3_MAX_TOKENS,
        system=system,
        user=user,
        thinking_kwargs=_thinking_kwargs(),
        logger=logger,
    )
    thinking_trace = thinking_trace.strip()
    parsed = _parse_step3_output(raw_text)

    # If standing pat, amended_artifact_text equals first-draft text verbatim.
    if parsed["decision"] == "stand-pat":
        parsed["amended_artifact_text"] = own_first_draft.get("artifact_text", "")
        parsed["amended_artifact_title"] = own_first_draft.get("artifact_title", "")
        parsed["amended_artifact_subtitle"] = own_first_draft.get("artifact_subtitle", "")
        parsed["selected_form"] = own_first_draft.get("selected_form", "")
        parsed["form_changed_from_first_draft"] = False
        parsed["form_change_rationale"] = None

    if not parsed["selected_form"]:
        parsed["selected_form"] = own_first_draft.get("selected_form", "")

    # Enrich amendments with cited_first_draft_path / cited_theme_id /
    # cited_formulation_id derived from voices_read + the amendment's
    # cited_voice. Best-effort: if voice can't be resolved, leave fields
    # empty (the voice still cited the move; downstream can investigate).
    voice_lookup = {v["council_member"].lower(): v for v in voices_read}
    voice_lookup_by_slug = {v["voice_slug"]: v for v in voices_read}
    for amendment in parsed["amendments"]:
        cv = amendment.get("cited_voice", "") or ""
        match = voice_lookup.get(cv.lower()) or voice_lookup_by_slug.get(cv.lower().replace(" ", "_"))
        if match:
            amendment.setdefault("cited_voice_slug", match["voice_slug"])
            amendment.setdefault("cited_first_draft_path", match["first_draft_path"])
            shared = match["shared_themes"]
            if shared and "cited_theme_id" not in amendment:
                amendment["cited_theme_id"] = shared[0]
                amendment["cited_formulation_id"] = (
                    f"{shared[0]}__{match['voice_slug']}"
                )

    # responded_to_graph: edges from this voice to each cited voice.
    responded_to_graph = [
        {
            "this_voice": voice_slug,
            "responded_to": a.get("cited_voice_slug", a.get("cited_voice", "")),
            "theme_id": a.get("cited_theme_id", ""),
            "amendment_type": a.get("amendment_type", ""),
        }
        for a in parsed["amendments"]
    ]

    word_count = len(parsed["amended_artifact_text"].split()) if parsed["amended_artifact_text"] else 0

    output = {
        "lineage": {
            "run_id": run_dir.name,
            "night": night,
            "voice_slug": voice_slug,
            "own_first_draft_path": f"04_voice/step2_first_draft_artifacts/{voice_slug}.json",
            "own_first_draft_themes_covered": own_first_draft["lineage"].get(
                "themes_covered", []
            ),
            "voices_read": voices_read,
            "all_grounding_extraction_ids": own_first_draft["lineage"].get(
                "all_grounding_extraction_ids", []
            ),
            "all_session_ids": own_first_draft["lineage"].get("all_session_ids", []),
        },
        "council_member": council_member_name,
        "decision": parsed["decision"],
        "decision_rationale": parsed["decision_rationale"],
        "amendments": parsed["amendments"],
        "selected_form": parsed["selected_form"],
        "form_changed_from_first_draft": parsed["form_changed_from_first_draft"],
        "form_change_rationale": parsed["form_change_rationale"],
        "amended_artifact_title": parsed["amended_artifact_title"],
        "amended_artifact_subtitle": parsed["amended_artifact_subtitle"],
        "amended_artifact_text": parsed["amended_artifact_text"],
        "thinking_trace": thinking_trace,
        "word_count": word_count,
        "responded_to_graph": responded_to_graph,
        "model": VOICE_MODEL,
        "thinking_enabled": VOICE_THINKING,
        "input_tokens": final.usage.input_tokens,
        "output_tokens": final.usage.output_tokens,
        "thinking_tokens": getattr(final.usage, "thinking_tokens", 0) or 0,
        "wall_clock_s": round(time.time() - t0, 2),
    }

    write_json_atomic(out_path, output)
    logger.info(
        f"  Step 3 done: {voice_slug} "
        f"(decision={parsed['decision']}, "
        f"amendments={len(parsed['amendments'])}, "
        f"voices_read={len(voices_read)}, {output['wall_clock_s']}s)"
    )
    return output
