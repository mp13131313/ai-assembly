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

from flows.shared.io import extract_json, get_logger, write_json_atomic
from flows.voice.card_assembly import assemble_system_prompt, load_persona_card


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

    Per spec, the model produces (in order):
      Decision 1: focus_decision + focus_rationale
      Decision 2: stance + stance_rationale
      Decision 3: selected_form + form_rationale
      Then: artifact_title, artifact_subtitle, artifact_text

    Models tend to write this as labelled prose ("Focus: focused on
    theme_X — rationale: …"). We extract by line-pattern matching.
    Defensive: if any field can't be extracted, the raw text remains in
    artifact_text so nothing is lost.
    """
    out: dict[str, Any] = {
        "focus_decision": "",
        "focus_rationale": "",
        "stance": "",
        "stance_rationale": "",
        "selected_form": "",
        "form_rationale": "",
        "artifact_title": "",
        "artifact_subtitle": "",
        "artifact_text": "",
    }
    # Field-extraction patterns — case-insensitive, line-anchored.
    # Each captures everything up to the next labelled field or end of text.
    labels = {
        "focus_decision": r"focus\s*decision",
        "focus_rationale": r"focus\s*rationale",
        "stance": r"^stance(?!\s*rationale)",
        "stance_rationale": r"stance\s*rationale",
        "selected_form": r"(?:selected\s*)?form(?!\s*rationale)",
        "form_rationale": r"form\s*rationale",
        "artifact_title": r"(?:artifact[_\s]*)?title",
        "artifact_subtitle": r"(?:artifact[_\s]*)?subtitle",
        "artifact_text": r"(?:artifact[_\s]*)?text",
    }
    # Naive split: try `KEY: value` lines; if not found, keep raw_text in artifact_text.
    found_any = False
    for key, pattern in labels.items():
        rx = re.compile(
            rf"^\s*[*_#\-]*\s*{pattern}\s*[:=]\s*(.+?)(?=\n\s*[*_#\-]*\s*(?:focus|stance|form|title|subtitle|text|artifact)[\s_]*[:=]|\Z)",
            re.IGNORECASE | re.MULTILINE | re.DOTALL,
        )
        m = rx.search(raw_text)
        if m:
            value = m.group(1).strip()
            # Strip trailing markdown chrome
            value = re.sub(r"\s*\*+\s*$", "", value).strip()
            out[key] = value
            found_any = True
    if not found_any:
        # Couldn't parse structured fields — preserve everything in artifact_text.
        out["artifact_text"] = raw_text.strip()
    return out


def _derive_themes_covered(focus_decision: str, step1_outputs: list[dict[str, Any]]) -> list[str]:
    """Derive themes_covered list from the focus_decision string.

    "woven across all" → all themes from step1_outputs.
    "focused on theme_X" or similar → extract theme IDs that appear in
    the string. Defensive: if nothing matches, fall back to all themes.
    """
    all_themes = [o["lineage"]["theme_id"] for o in step1_outputs]
    fd_lower = focus_decision.lower()
    if "woven" in fd_lower or "across all" in fd_lower:
        return all_themes
    matched = [t for t in all_themes if t in focus_decision]
    return matched if matched else all_themes


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
    text_chunks: list[str] = []
    thinking_chunks: list[str] = []
    with client.messages.stream(
        model=VOICE_MODEL,
        max_tokens=STEP2_MAX_TOKENS,
        system=system,
        messages=[{"role": "user", "content": user}],
        **_thinking_kwargs(),
    ) as stream:
        for event in stream:
            if getattr(event, "type", None) == "content_block_delta":
                delta = event.delta
                if getattr(delta, "type", None) == "text_delta":
                    text_chunks.append(delta.text)
                elif getattr(delta, "type", None) == "thinking_delta":
                    thinking_chunks.append(delta.thinking)
        final = stream.get_final_message()

    raw_text = "".join(text_chunks)
    thinking_trace = "".join(thinking_chunks).strip()
    parsed = _parse_step2_output(raw_text)
    themes_covered = _derive_themes_covered(parsed["focus_decision"], step1_outputs)

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
