"""Voice Pipeline Step 1 — Private Reasoning.

One LLM call per (voice, formulation) pair. Voice reads a single
formulation + the day's structured reasoning surface, produces a
detailed_response that engages substantively with what humans said today.

Per docs/AI_Assembly_Voice_Pipeline.md §"Step 1 — Private Reasoning":
  Model: Opus 4.7 + adaptive thinking, max_tokens=64000
  Streaming: REQUIRED
  Output: 04_voice/step1_detailed_responses/<voice_slug>__<theme_id>.json
  Lineage block carries pointers back to briefing + formulation files

The thinking trace is captured alongside the text response (Anthropic
streamed thinking_delta events) and saved into the output JSON for
downstream audit (per spec §"Reasoning trace capture").
"""

from __future__ import annotations

import json
import re
import os
import sys
import time
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from anthropic import Anthropic

from flows.shared.io import write_json_atomic, get_logger
from flows.voice.card_assembly import (
    assemble_system_prompt,
    filter_theme_record_for_step1,
    load_persona_card,
)
from flows.voice._anthropic_call import stream_voice_call


VOICE_MODEL = os.environ.get(
    "VOICE_MODEL",
    os.environ.get("CLAUDE_MODEL", "claude-opus-4-7"),
)
VOICE_THINKING = os.environ.get("VOICE_THINKING", "1") != "0"
VOICE_THINKING_EFFORT = os.environ.get("VOICE_THINKING_EFFORT", "high")
STEP1_MAX_TOKENS = int(os.environ.get("VOICE_STEP1_MAX_TOKENS", "64000"))


def _thinking_kwargs() -> dict:
    """Adaptive thinking kwargs with explicit effort = high.

    Per Anthropic docs (https://docs.anthropic.com/en/docs/build-with-claude/extended-thinking):
    On Opus 4.7, manual `type: "enabled"` returns 400 — only `type:
    "adaptive"` is supported. Effort goes at the request top level:
    `effort: "low" | "medium" | "high"`. `display` is only valid on
    `type: "enabled"` (default on 4.7 adaptive is "omitted").

    We default to `effort: "high"` so reasoning is consistent across
    voices — earlier "adaptive without effort" runs showed some voices
    returning 0 thinking tokens (model decided to skip), which produced
    weaker artifacts. Override via VOICE_THINKING_EFFORT env var.

    Returns no `temperature` — per docs, thinking isn't compatible with
    `temperature` or `top_k` modifications.
    """
    if not VOICE_THINKING:
        return {}
    return {
        "thinking": {"type": "adaptive"},
        "effort": VOICE_THINKING_EFFORT,
    }


_TAIL_RE = re.compile(
    r"^\s*(?:[*_`#\->]+\s*)?extractions[_\s]*engaged\s*[:=]\s*(.+?)\s*$",
    re.IGNORECASE | re.MULTILINE,
)


def _extract_engaged_tail(
    detailed_response: str, *, fallback_ids: list[str]
) -> tuple[str, list[str]]:
    """Strip the bookkeeping `extractions_engaged: id1, id2, id3` tail
    line from the voice's detailed response and return (cleaned_text,
    parsed_ids).

    The closing instruction asks the voice to emit the line at the very
    end as plain bookkeeping. We tolerate light markdown decoration
    (asterisks, leading dashes, backticks, blockquote markers) the
    voice may add, and case variation. The ID set itself is comma-
    separated; we tolerate trailing periods, surrounding brackets, and
    minor whitespace.

    If the line is absent or unparseable, fall back to the briefing's
    grounding_extraction_ids — lineage stays walkable, just at briefing
    granularity rather than voice-engaged granularity.

    Cleaning: only the LAST occurrence of the line is stripped (so a
    voice that mentions an ID format mid-prose isn't mutilated). The
    line and any trailing whitespace/decoration are removed cleanly.
    """
    if not detailed_response:
        return detailed_response, list(fallback_ids)

    matches = list(_TAIL_RE.finditer(detailed_response))
    if not matches:
        return detailed_response, list(fallback_ids)

    last = matches[-1]
    raw = last.group(1).strip()
    # Strip surrounding [], (), markdown emphasis, trailing period
    raw = raw.strip("[]()`*_ .")
    # Split on commas; trim each; drop empties
    ids = [tok.strip(" `*_.[]") for tok in raw.split(",")]
    ids = [i for i in ids if i and ":" in i]  # extraction IDs always have a colon

    if not ids:
        # Line found but unparseable — keep prose untouched, fall back
        return detailed_response, list(fallback_ids)

    # Strip the matched line + any trailing whitespace
    cleaned = (detailed_response[: last.start()] + detailed_response[last.end():]).rstrip()
    return cleaned, ids


def build_step1_user_prompt(formulation_entry: dict[str, Any]) -> str:
    """Render a single formulation into the user prompt the voice sees.

    Per spec: voice receives the briefing's narrative_briefing markdown
    verbatim + a filtered structured reasoning surface (pipeline-meta
    stripped — see card_assembly.filter_theme_record_for_step1).
    """
    narrative = formulation_entry.get("narrative_briefing", "")
    full_record = formulation_entry.get("full_theme_record", {}) or {}
    filtered_record = filter_theme_record_for_step1(full_record)

    return (
        f"{narrative}\n\n"
        f"---\n\n"
        f"WIDER RECORD OF TODAY'S CONVERSATION ON THIS THEME:\n\n"
        f"{json.dumps(filtered_record, indent=2, ensure_ascii=False)}\n"
    )


def run_step1_for_pair(
    voice_slug: str,
    formulation_entry: dict[str, Any],
    night: int,
    run_dir: Path,
    project_root: Path | None = None,
    council_member_name: str | None = None,
) -> dict[str, Any]:
    """Run Step 1 for one (voice, formulation) pair.

    Idempotent: if the output file already exists, returns its content
    without re-calling the model (checkpoints-as-cache, matching
    Researcher / Provocateur convention).
    """
    logger = get_logger("voice_step1")
    theme_id = formulation_entry["theme_id"]
    out_dir = run_dir / "04_voice" / "step1_detailed_responses"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{voice_slug}__{theme_id}.json"

    if out_path.exists():
        logger.info(f"  Step 1 cached: {voice_slug}__{theme_id}")
        with open(out_path, encoding="utf-8") as f:
            return json.load(f)

    card = load_persona_card(voice_slug, night=night, project_root=project_root)
    if council_member_name is None:
        council_member_name = card.get("council_member_name", voice_slug)

    system = assemble_system_prompt(card, step=1, night=night)
    user = build_step1_user_prompt(formulation_entry)

    logger.info(
        f"  Step 1 calling: {voice_slug}__{theme_id} "
        f"(model={VOICE_MODEL}, thinking={VOICE_THINKING})"
    )
    client = Anthropic()
    t0 = time.time()
    detailed_response, thinking_trace, final, thinking_tokens = stream_voice_call(
        client,
        model=VOICE_MODEL,
        max_tokens=STEP1_MAX_TOKENS,
        system=system,
        user=user,
        thinking_kwargs=_thinking_kwargs(),
        logger=logger,
    )
    detailed_response = detailed_response.strip()
    thinking_trace = thinking_trace.strip()

    formulation_id = f"{theme_id}__{voice_slug}"
    full_record = formulation_entry.get("full_theme_record", {}) or {}
    grounding_ids = full_record.get("grounding_extraction_ids", [])
    cluster_ids = [c.get("cluster_id") for c in full_record.get("clusters", []) if c.get("cluster_id")]
    session_ids = sorted({eid.split(":", 1)[0] for eid in grounding_ids if ":" in eid})
    co_assigned = full_record.get("co_assigned_voices", [])

    # Parse the bookkeeping `extractions_engaged: id1, id2, id3` tail line
    # the closing instruction asks the voice to emit. The line gets
    # stripped from `detailed_response` so it doesn't pollute downstream
    # consumers (Step 2 readback, etc). If the voice forgot to emit it
    # (or emitted a malformed version), fall back to the briefing's
    # grounding_extraction_ids — lineage stays walkable either way.
    detailed_response, extractions_engaged = _extract_engaged_tail(
        detailed_response, fallback_ids=grounding_ids
    )

    output = {
        "lineage": {
            "run_id": run_dir.name,
            "night": night,
            "voice_slug": voice_slug,
            "formulation_id": formulation_id,
            "briefing_path": f"03_provocateur/briefings/{voice_slug}.json",
            "formulation_path": f"03_provocateur/formulations/{theme_id}__{voice_slug}.json",
            "theme_id": theme_id,
            "cluster_ids": cluster_ids,
            "grounding_extraction_ids": grounding_ids,
            "session_ids": session_ids,
            "co_assigned_voices": co_assigned,
        },
        "council_member": council_member_name,
        "theme_display_title": formulation_entry.get("theme_display_title", ""),
        "formulation_text": formulation_entry.get("formulation_text", ""),
        "mode": formulation_entry.get("mode", "question"),
        "detailed_response": detailed_response,
        "extractions_engaged": extractions_engaged,
        "thinking_trace": thinking_trace,
        "model": VOICE_MODEL,
        "thinking_enabled": VOICE_THINKING,
        "input_tokens": final.usage.input_tokens,
        "output_tokens": final.usage.output_tokens,
        "thinking_tokens": thinking_tokens,
        "cache_creation_input_tokens": getattr(final.usage, "cache_creation_input_tokens", 0) or 0,
        "cache_read_input_tokens": getattr(final.usage, "cache_read_input_tokens", 0) or 0,
        "wall_clock_s": round(time.time() - t0, 2),
    }

    write_json_atomic(out_path, output)
    logger.info(
        f"  Step 1 done: {voice_slug}__{theme_id} "
        f"(in={output['input_tokens']}, out={output['output_tokens']}, "
        f"think={output['thinking_tokens']}, {output['wall_clock_s']}s)"
    )
    if output["output_tokens"] > STEP1_MAX_TOKENS * 0.8:
        logger.warning(
            f"Step 1 used {output['output_tokens']}/{STEP1_MAX_TOKENS} "
            f"output tokens (>80%) for {voice_slug}__{theme_id}. "
            f"Consider increasing VOICE_STEP1_MAX_TOKENS."
        )
    return output
