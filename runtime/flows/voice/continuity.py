"""Voice Pipeline Continuity Block Generation.

Per docs/AI_Assembly_Voice_Pipeline.md §"Continuity Block Generation":
runs after Night N completes (Step 3 artifacts written), before
Night N+1's Provocateur runs. Per-voice Sonnet call summarises the
voice's prior-night work in voice-grammar memory; output is written
to <PROJECT_ROOT>/voices/<slug>/continuity_night_N+1.json and loaded
by the next-night Voice Pipeline as a card override.

Trigger: voice_flow.py writes a sentinel `04_voice/step3_complete.flag`
after all voices' Step 3 succeed; this module watches for that.

Model: Sonnet 4.6 + adaptive thinking (per spec — compression task,
doesn't carry the same generative pressure as Steps 1/2/3, but
adaptive thinking still on so the summariser can hold the voice's
own grammar and temporal stance while compressing).
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

from flows.shared.io import extract_json, get_logger, load_prompt, write_json_atomic
from flows.shared.project_root import resolve_project_root
from flows.voice._anthropic_call import stream_voice_call


CONTINUITY_MODEL = os.environ.get(
    "VOICE_CONTINUITY_MODEL",
    "claude-sonnet-4-6",
)
CONTINUITY_THINKING = os.environ.get("VOICE_CONTINUITY_THINKING", "1") != "0"
CONTINUITY_MAX_TOKENS = int(os.environ.get("VOICE_CONTINUITY_MAX_TOKENS", "8000"))


def _thinking_kwargs() -> dict:
    if not CONTINUITY_THINKING:
        return {}
    return {"thinking": {"type": "adaptive"}, "temperature": 1.0}


def _load_voice_step1_outputs(
    run_dir: Path, voice_slug: str
) -> list[dict[str, Any]]:
    """Load all of one voice's Step 1 detailed_response files."""
    step1_dir = run_dir / "04_voice" / "step1_detailed_responses"
    if not step1_dir.exists():
        return []
    pattern = f"{voice_slug}__*.json"
    out = []
    for p in sorted(step1_dir.glob(pattern)):
        with open(p, encoding="utf-8") as f:
            out.append(json.load(f))
    return out


def _load_voice_step2(run_dir: Path, voice_slug: str) -> dict[str, Any] | None:
    p = run_dir / "04_voice" / "step2_first_draft_artifacts" / f"{voice_slug}.json"
    if not p.exists():
        return None
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def _load_voice_step3(run_dir: Path, voice_slug: str) -> dict[str, Any] | None:
    p = run_dir / "04_voice" / "step3_amended_artifacts" / f"{voice_slug}.json"
    if not p.exists():
        return None
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def _build_continuity_user_prompt(
    voice_slug: str,
    night: int,
    step1_outputs: list[dict[str, Any]],
    step2_output: dict[str, Any] | None,
    step3_output: dict[str, Any] | None,
) -> str:
    """Render the voice's Night N work into the summariser's user prompt."""
    parts = [
        f"Voice: {voice_slug}\n",
        f"Night being summarised: {night}\n",
        f"For night: {night + 1}\n\n",
        "---\n\n",
        f"## Detailed responses ({len(step1_outputs)})\n\n",
    ]
    for i, o in enumerate(step1_outputs, 1):
        parts.append(f"### Response {i}\n\n")
        parts.append(f"**Theme:** {o.get('theme_display_title', '')}\n")
        parts.append(f"**Mode:** {o.get('mode', 'question')}\n")
        parts.append(f"**Formulation:** {o.get('formulation_text', '')}\n\n")
        parts.append(f"{o.get('detailed_response', '')}\n\n")

    if step2_output:
        parts.append("---\n\n## First-draft artifact\n\n")
        parts.append(
            f"Focus: {step2_output.get('focus_decision', '')}\n"
            f"Stance: {step2_output.get('stance', '')}\n"
            f"Form: {step2_output.get('selected_form', '')}\n\n"
        )
        parts.append(
            f"### {step2_output.get('artifact_title', '')}\n"
            f"_{step2_output.get('artifact_subtitle', '')}_\n\n"
            f"{step2_output.get('artifact_text', '')}\n\n"
        )

    if step3_output:
        parts.append("---\n\n## Amended artifact (Step 3)\n\n")
        parts.append(f"Decision: {step3_output.get('decision', '')}\n")
        parts.append(f"Decision rationale: {step3_output.get('decision_rationale', '')}\n\n")
        amendments = step3_output.get("amendments", [])
        if amendments:
            parts.append(f"Amendments ({len(amendments)}):\n")
            for a in amendments:
                parts.append(
                    f"- {a.get('amendment_type', '')}: cited {a.get('cited_voice', '')} — {a.get('rationale', '')}\n"
                )
            parts.append("\n")
        parts.append(f"{step3_output.get('amended_artifact_text', '')}\n")

    return "".join(parts)


def generate_continuity(
    voice_slug: str,
    night_just_completed: int,
    run_dir: Path,
    project_root: Path | None = None,
) -> dict[str, Any]:
    """Generate continuity blocks for one voice for the next night.

    Idempotent: if the override file at
    <PROJECT_ROOT>/voices/<voice_slug>/continuity_night_<N+1>.json
    already exists, returns it.
    """
    logger = get_logger("voice_continuity")
    next_night = night_just_completed + 1
    if project_root is None:
        project_root = resolve_project_root(None)
    out_path = project_root / "voices" / voice_slug / f"continuity_night_{next_night}.json"

    if out_path.exists():
        logger.info(f"  Continuity cached: {voice_slug} for night {next_night}")
        with open(out_path, encoding="utf-8") as f:
            return json.load(f)

    step1_outputs = _load_voice_step1_outputs(run_dir, voice_slug)
    step2_output = _load_voice_step2(run_dir, voice_slug)
    step3_output = _load_voice_step3(run_dir, voice_slug)
    if not step1_outputs and not step2_output and not step3_output:
        logger.warning(
            f"  Continuity skipped: {voice_slug} has no Night {night_just_completed} "
            f"output to summarise."
        )
        return {}

    system = load_prompt("voice_continuity")
    user = _build_continuity_user_prompt(
        voice_slug, night_just_completed, step1_outputs, step2_output, step3_output
    )

    logger.info(
        f"  Continuity calling: {voice_slug} for night {next_night} "
        f"(model={CONTINUITY_MODEL})"
    )
    client = Anthropic()
    t0 = time.time()
    raw_text, _thinking_trace, final = stream_voice_call(
        client,
        model=CONTINUITY_MODEL,
        max_tokens=CONTINUITY_MAX_TOKENS,
        system=system,
        user=user,
        thinking_kwargs=_thinking_kwargs(),
        logger=logger,
    )

    # The model returns JSON with two keys, with the night number
    # substituted for "N+1". We accept either spelling.
    parsed = extract_json(raw_text)
    cb_reasoning = (
        parsed.get(f"continuity_block_if_night_{next_night}")
        or parsed.get("continuity_block_if_night_N+1")
        or ""
    )
    cb_artifact = (
        parsed.get(f"continuity_block_artifact_if_night_{next_night}")
        or parsed.get("continuity_block_artifact_if_night_N+1")
        or ""
    )

    output = {
        "voice_slug": voice_slug,
        "from_night": night_just_completed,
        "for_night": next_night,
        f"continuity_block_if_night_{next_night}": cb_reasoning,
        f"continuity_block_artifact_if_night_{next_night}": cb_artifact,
        "generated_date": time.strftime("%Y-%m-%d"),
        "model": CONTINUITY_MODEL,
        "input_tokens": final.usage.input_tokens,
        "output_tokens": final.usage.output_tokens,
        "wall_clock_s": round(time.time() - t0, 2),
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    write_json_atomic(out_path, output)
    logger.info(
        f"  Continuity done: {voice_slug} for night {next_night} "
        f"({output['wall_clock_s']}s)"
    )
    return output
