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
STEP1_MAX_TOKENS = int(os.environ.get("VOICE_STEP1_MAX_TOKENS", "64000"))


def _thinking_kwargs() -> dict:
    """Adaptive thinking kwargs (matches researcher_flow._thinking_kwargs).

    Adaptive mode lets the model decide how much to think; recommended
    for Opus 4.7. Requires temperature=1.0.
    """
    if not VOICE_THINKING:
        return {}
    return {"thinking": {"type": "adaptive"}, "temperature": 1.0}


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
    detailed_response, thinking_trace, final = stream_voice_call(
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
        "thinking_trace": thinking_trace,
        "model": VOICE_MODEL,
        "thinking_enabled": VOICE_THINKING,
        "input_tokens": final.usage.input_tokens,
        "output_tokens": final.usage.output_tokens,
        "thinking_tokens": getattr(final.usage, "thinking_tokens", 0) or 0,
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
