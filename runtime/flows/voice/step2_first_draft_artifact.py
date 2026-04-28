"""Voice Pipeline Step 2 — First-Draft Artifact.

One LLM call per voice per night. Voice reads back ALL of its Step 1
detailed responses, makes three decisions (focus / stance / form from
its medium family-of-forms), and produces a single artifact text.

Per docs/AI_Assembly_Voice_Pipeline.md §"Step 2 — First-Draft Artifact":
  Model: Opus 4.7 + adaptive thinking, max_tokens=64000
  Streaming: REQUIRED
  Output: 04_voice/step2_first_draft_artifacts/<voice_slug>.json
  Lineage block carries pointers to consumed Step 1 files +
  union of grounding_extraction_ids / session_ids across them
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
from flows.voice.card_assembly import assemble_system_prompt, load_persona_card
from flows.voice._anthropic_call import stream_voice_call


VOICE_MODEL = os.environ.get(
    "VOICE_MODEL",
    os.environ.get("CLAUDE_MODEL", "claude-opus-4-7"),
)
VOICE_THINKING = os.environ.get("VOICE_THINKING", "1") != "0"
STEP2_MAX_TOKENS = int(os.environ.get("VOICE_STEP2_MAX_TOKENS", "64000"))


def _thinking_kwargs() -> dict:
    if not VOICE_THINKING:
        return {}
    return {"thinking": {"type": "adaptive"}, "temperature": 1.0}


def build_step2_user_prompt(step1_outputs: list[dict[str, Any]]) -> str:
    """Render all of one voice's Step 1 detailed responses into the user prompt.

    Each detailed response gets a header naming its theme_id,
    theme_display_title, mode, and formulation_text — all things the
    voice already saw in Step 1, so re-seeing is fine.
    """
    parts = ["Your detailed responses from earlier today:\n"]
    for i, out in enumerate(step1_outputs, 1):
        parts.append(f"\n---\n\n## Detailed response {i} of {len(step1_outputs)}\n\n")
        parts.append(f"**Theme:** {out.get('theme_display_title', '')}\n")
        parts.append(f"**Mode:** {out.get('mode', 'question')}\n\n")
        parts.append(f"**Formulation:** {out.get('formulation_text', '')}\n\n")
        parts.append(f"**Your reasoning:**\n\n{out.get('detailed_response', '')}\n")
    return "".join(parts)


def _parse_step2_output(raw_text: str) -> dict[str, Any]:
    """Parse the model's Step 2 output into structured fields.

    The closing instruction in voice_step2_artifact.md asks the model
    to emit fields in a specific order, each as `**Label:** value` on
    its own line, with `artifact_text` being the last labelled field
    and the artifact body following it without further labels.

    Defensive: if `artifact_text:` label isn't found, the raw text
    remains in artifact_text so nothing is lost. Other field misses
    leave that field empty rather than aborting.
    """
    out: dict[str, Any] = {
        "focus_decision": "",
        "focus_rationale": "",
        "stance": "",
        "stance_rationale": "",
        "selected_form": "",
        "form_rationale": "",
        "themes_covered": [],
        "artifact_title": "",
        "artifact_subtitle": "",
        "artifact_text": "",
    }

    # Single-line fields: extract `**Label:** value` (or `Label: value`)
    # up to the next labelled line or to artifact_text (which is multi-line).
    # The closing instruction asks the model to emit each field on its own
    # `**Label:** value` line; the parser is tolerant of the model varying
    # surrounding markdown (asterisks, underscores, dashes, headings).
    single_line_labels = {
        "focus_decision": r"focus[_\s]*decision",
        "focus_rationale": r"focus[_\s]*rationale",
        # `stance` must not match `stance_rationale`. Negative lookahead
        # requires NO `_rationale` or `\s+rationale` immediately after.
        "stance": r"stance(?![_\s]*rationale)",
        "stance_rationale": r"stance[_\s]*rationale",
        # Same negative-lookahead pattern for selected_form vs form_rationale.
        "selected_form": r"(?:selected[_\s]*)?form(?![_\s]*rationale|[_\s]*change)",
        "form_rationale": r"form[_\s]*rationale",
        "themes_covered": r"themes[_\s]*covered",
        "artifact_title": r"(?:artifact[_\s]*)?title",
        "artifact_subtitle": r"(?:artifact[_\s]*)?subtitle",
    }
    # A "next labelled line" is any newline followed by optional markdown
    # chrome (`**`, `_`, `#`, `-`) and a lowercase identifier (matching
    # any field name that might appear). We terminate the current capture
    # when we see this pattern OR end-of-text.
    next_label_lookahead = r"\n\s*[*_#\-]+\s*[a-z][a-z_]+"
    for key, pattern in single_line_labels.items():
        rx = re.compile(
            rf"^\s*[*_#\-]*\s*{pattern}\s*[*_]*\s*[:=]\s*[*_]*\s*(.+?)(?={next_label_lookahead}|\Z)",
            re.IGNORECASE | re.MULTILINE | re.DOTALL,
        )
        m = rx.search(raw_text)
        if m:
            value = m.group(1).strip()
            # Strip leading + trailing markdown chrome (`**`, `*`, `_`).
            value = re.sub(r"^[*_]+\s*", "", value).strip()
            value = re.sub(r"\s*[*_]+$", "", value).strip()
            if key == "themes_covered":
                # Comma- or whitespace-separated list of theme_ids.
                ids = re.findall(r"theme_[a-z0-9_]+", value, re.IGNORECASE)
                out[key] = [t.lower() for t in ids]
            else:
                out[key] = value

    # artifact_text: the remainder of the response after the
    # `artifact_text:` label. Multi-line; runs to end of response.
    # Tolerant of `**artifact_text:**` markdown by stripping `*`/`_`
    # both before and after the colon.
    text_rx = re.compile(
        r"^\s*[*_#\-]*\s*(?:artifact[_\s]*)?text\s*[*_]*\s*[:=]\s*[*_]*\s*\n?(.+)\Z",
        re.IGNORECASE | re.MULTILINE | re.DOTALL,
    )
    m = text_rx.search(raw_text)
    if m:
        text_value = m.group(1).strip()
        # Strip leading markdown chrome the model may have emitted
        # before the artifact body (e.g. `**\n` from a closing `**`).
        text_value = re.sub(r"^[*_]+\s*", "", text_value).strip()
        out["artifact_text"] = text_value
    else:
        # No artifact_text label found — preserve full raw_text so
        # nothing is silently lost.
        out["artifact_text"] = raw_text.strip()
    return out


def _ensure_themes_covered(
    parsed_themes: list[str],
    focus_decision: str,
    step1_outputs: list[dict[str, Any]],
) -> list[str]:
    """Backstop for themes_covered.

    The voice should emit themes_covered explicitly per the closing
    instruction. If parsing failed AND focus_decision says "woven",
    fall back to all themes. If neither, fall back to all themes (so
    Step 3 sees the union; better-than-empty fallback that may produce
    over-broad sharing rather than missing entirely). Operator should
    investigate any case where this backstop fires (logged downstream
    via wall_clock + manifest).
    """
    if parsed_themes:
        return parsed_themes
    all_themes = [o["lineage"]["theme_id"] for o in step1_outputs]
    return all_themes


def run_step2_for_voice(
    voice_slug: str,
    step1_outputs: list[dict[str, Any]],
    night: int,
    run_dir: Path,
    project_root: Path | None = None,
    council_member_name: str | None = None,
) -> dict[str, Any]:
    """Run Step 2 for one voice, given all of that voice's Step 1 outputs.

    Idempotent (checkpoints-as-cache).
    """
    logger = get_logger("voice_step2")
    out_dir = run_dir / "04_voice" / "step2_first_draft_artifacts"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{voice_slug}.json"

    if out_path.exists():
        logger.info(f"  Step 2 cached: {voice_slug}")
        with open(out_path, encoding="utf-8") as f:
            return json.load(f)

    if not step1_outputs:
        raise ValueError(
            f"Step 2 for {voice_slug}: no Step 1 outputs to read back. "
            f"Step 1 must complete (or at least one detailed_response must succeed) "
            f"before Step 2 runs for a voice."
        )

    card = load_persona_card(voice_slug, night=night, project_root=project_root)
    if council_member_name is None:
        council_member_name = card.get("council_member_name", voice_slug)

    system = assemble_system_prompt(card, step=2, night=night)
    user = build_step2_user_prompt(step1_outputs)

    logger.info(
        f"  Step 2 calling: {voice_slug} "
        f"({len(step1_outputs)} Step 1 inputs, model={VOICE_MODEL})"
    )
    client = Anthropic()
    t0 = time.time()
    raw_text, thinking_trace, final = stream_voice_call(
        client,
        model=VOICE_MODEL,
        max_tokens=STEP2_MAX_TOKENS,
        system=system,
        user=user,
        thinking_kwargs=_thinking_kwargs(),
        logger=logger,
    )
    thinking_trace = thinking_trace.strip()
    parsed = _parse_step2_output(raw_text)
    themes_covered = _ensure_themes_covered(
        parsed["themes_covered"], parsed["focus_decision"], step1_outputs
    )

    # Build lineage block (consumed Step 1 paths + union of grounding ids).
    consumed = []
    all_grounding: set[str] = set()
    all_sessions: set[str] = set()
    formulation_ids = []
    for o in step1_outputs:
        lin = o["lineage"]
        consumed.append({
            "theme_id": lin["theme_id"],
            "formulation_id": lin["formulation_id"],
            "path": f"04_voice/step1_detailed_responses/{voice_slug}__{lin['theme_id']}.json",
        })
        formulation_ids.append(lin["formulation_id"])
        all_grounding.update(lin.get("grounding_extraction_ids", []))
        all_sessions.update(lin.get("session_ids", []))

    word_count = len(parsed["artifact_text"].split()) if parsed["artifact_text"] else 0

    output = {
        "lineage": {
            "run_id": run_dir.name,
            "night": night,
            "voice_slug": voice_slug,
            "briefing_path": f"03_provocateur/briefings/{voice_slug}.json",
            "consumed_detailed_responses": consumed,
            "themes_covered": themes_covered,
            "formulation_ids_engaged": formulation_ids,
            "all_grounding_extraction_ids": sorted(all_grounding),
            "all_session_ids": sorted(all_sessions),
        },
        "council_member": council_member_name,
        "focus_decision": parsed["focus_decision"],
        "focus_rationale": parsed["focus_rationale"],
        "stance": parsed["stance"],
        "stance_rationale": parsed["stance_rationale"],
        "selected_form": parsed["selected_form"],
        "form_rationale": parsed["form_rationale"],
        "artifact_title": parsed["artifact_title"],
        "artifact_subtitle": parsed["artifact_subtitle"],
        "artifact_text": parsed["artifact_text"],
        "thinking_trace": thinking_trace,
        "word_count": word_count,
        "model": VOICE_MODEL,
        "thinking_enabled": VOICE_THINKING,
        "input_tokens": final.usage.input_tokens,
        "output_tokens": final.usage.output_tokens,
        "thinking_tokens": getattr(final.usage, "thinking_tokens", 0) or 0,
        "wall_clock_s": round(time.time() - t0, 2),
    }

    write_json_atomic(out_path, output)
    logger.info(
        f"  Step 2 done: {voice_slug} "
        f"(focus={parsed['focus_decision'][:40]!r}, "
        f"stance={parsed['stance']!r}, form={parsed['selected_form'][:40]!r}, "
        f"words={word_count}, {output['wall_clock_s']}s)"
    )
    return output
