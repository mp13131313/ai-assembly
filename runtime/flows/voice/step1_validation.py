"""Voice Pipeline Step 1 — Validation nodes (OpenAI cross-model).

Two optional checks per Step 1 detailed_response:
  - Anachronism + tense check (against knowledge_boundary +
    voice_temporal_stance)
  - Constitutional self-reflection (against constitution; permits
    Position-B corpus-internal cross-examination, flags only
    framework-abandonment)

Per docs/AI_Assembly_Voice_Pipeline.md §"Validation Nodes":
  Provider: OpenAI ladder (gpt-5.4 reasoning_effort=high → gpt-4.1 →
            o3 → gpt-4o → Gemini 2.5 Pro)
  Why OpenAI: cross-model validation catches blind spots same-family
              validation misses. Voice's Step 1 was Opus; checking
              with another Anthropic model risks the same family blind
              spots.
  Default policy: Athens Night 1 ON; Night 2/3 ON for voices flagged
                  on prior nights.
  Regeneration: 1 retry on failure with critique appended; second
                failure ships output + flags in manifest.

Implements its own thin OpenAI client (no shared runtime client module
exists; mirrors the personas/flows/shared/clients.py:call_openai
pattern with the same fallback ladder).
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

from flows.shared.io import get_logger, load_prompt, write_json_atomic


# Fallback ladder per spec — same as Persona Pipeline Pass 7-anachronism / 7a.
# Override via VOICE_VALIDATION_MODELS env var (comma-separated).
_DEFAULT_LADDER = ("gpt-5.4", "gpt-4.1", "o3", "gpt-4o", "gemini-2.5-pro")
VALIDATION_LADDER = tuple(
    s.strip()
    for s in os.environ.get(
        "VOICE_VALIDATION_MODELS",
        ",".join(_DEFAULT_LADDER),
    ).split(",")
    if s.strip()
)
VALIDATION_MAX_TOKENS = int(os.environ.get("VOICE_VALIDATION_MAX_TOKENS", "8192"))


def _call_openai_with_fallback(
    *,
    system: str,
    user: str,
    max_tokens: int,
    reasoning_effort: str | None = None,
) -> dict[str, Any]:
    """Try the OpenAI ladder; return first success.

    Final entry "gemini-2.5-pro" falls through to Google's GenAI SDK.
    Each call gets temperature=0.0 for determinism on a check task.
    Returns dict with keys: text, model, usage, wall_clock_s.
    """
    from openai import OpenAI  # local import — runtime venv may not have it
    last_err: Exception | None = None
    for model in VALIDATION_LADDER:
        try:
            t0 = time.time()
            if model.startswith("gemini"):
                # Fallback path: Google GenAI
                from google import genai
                client = genai.Client()
                resp = client.models.generate_content(
                    model=model,
                    contents=f"{system}\n\n---\n\n{user}",
                    config={"temperature": 0.0, "max_output_tokens": max_tokens},
                )
                text = resp.text or ""
                return {
                    "text": text,
                    "model": model,
                    "usage": {},
                    "wall_clock_s": round(time.time() - t0, 2),
                }
            client = OpenAI()
            is_o_series = any(model.startswith(p) for p in ("o1", "o3", "o4"))
            use_reasoning = is_o_series or reasoning_effort is not None
            kwargs: dict[str, Any] = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            }
            if use_reasoning:
                kwargs["max_completion_tokens"] = max_tokens
                if reasoning_effort:
                    kwargs["reasoning_effort"] = reasoning_effort
            else:
                kwargs["temperature"] = 0.0
                kwargs["max_tokens"] = max_tokens
            resp = client.chat.completions.create(**kwargs)
            if not resp.choices:
                raise RuntimeError(f"OpenAI returned no choices for {model}")
            text = resp.choices[0].message.content or ""
            return {
                "text": text,
                "model": model,
                "usage": {
                    "input_tokens": resp.usage.prompt_tokens,
                    "output_tokens": resp.usage.completion_tokens,
                },
                "wall_clock_s": round(time.time() - t0, 2),
            }
        except Exception as e:  # noqa: BLE001 — try next ladder rung
            last_err = e
            continue
    raise RuntimeError(
        f"All validation models in ladder failed: {VALIDATION_LADDER}. "
        f"Last error: {last_err}"
    )


def _build_anachronism_prompt(
    detailed_response: str,
    knowledge_boundary: Any,
    voice_temporal_stance: Any,
) -> tuple[str, str]:
    """Build (system, user) for the anachronism check.

    System prompt template lives at
    runtime/flows/shared/prompts/voice_step1_validation_anachronism.md
    with placeholders {{knowledge_horizon_summary}} and
    {{voice_temporal_stance}}; we substitute both from the card so the
    validator checks against the voice's actual stance (whatever the
    persona pipeline produced) rather than a hard-coded framing.

    voice_temporal_stance is unwrapped to its prose form (default text
    for Athens; anchored_override for chat-test deployments) so the
    validator sees the same block of text the voice itself receives in
    its system prompt.
    """
    from flows.voice.card_assembly import _unwrap_voice_temporal_stance

    system_template = load_prompt("voice_step1_validation_anachronism")
    horizon_summary = (
        knowledge_boundary
        if isinstance(knowledge_boundary, str)
        else json.dumps(knowledge_boundary, ensure_ascii=False)
    )
    stance_text = _unwrap_voice_temporal_stance(voice_temporal_stance)
    system = system_template.replace(
        "{{knowledge_horizon_summary}}", horizon_summary[:2000]
    ).replace(
        "{{voice_temporal_stance}}", stance_text[:4000]
    )
    user = f"DETAILED RESPONSE TO CHECK:\n\n{detailed_response}"
    return system, user


def _build_constitution_prompt(
    detailed_response: str,
    constitution: Any,
) -> tuple[str, str]:
    """Build (system, user) for the constitutional check."""
    system_template = load_prompt("voice_step1_validation_constitution")
    constitution_text = (
        constitution
        if isinstance(constitution, str)
        else json.dumps(constitution, indent=2, ensure_ascii=False)
    )
    system = system_template.replace("{{constitution}}", constitution_text[:8000])
    user = f"DETAILED RESPONSE TO CHECK:\n\n{detailed_response}"
    return system, user


def check_anachronism(
    detailed_response: str,
    knowledge_boundary: Any,
    voice_temporal_stance: Any,
) -> dict[str, Any]:
    """Returns {"status": "PASS" | "ISSUES", "text": <verdict>, "model": str}."""
    system, user = _build_anachronism_prompt(
        detailed_response, knowledge_boundary, voice_temporal_stance
    )
    result = _call_openai_with_fallback(
        system=system,
        user=user,
        max_tokens=VALIDATION_MAX_TOKENS,
        reasoning_effort="high",
    )
    text = result["text"].strip()
    status = "PASS" if text.upper().startswith("PASS") else "ISSUES"
    return {
        "status": status,
        "text": text,
        "model": result["model"],
        "wall_clock_s": result["wall_clock_s"],
    }


def check_constitution(
    detailed_response: str,
    constitution: Any,
) -> dict[str, Any]:
    """Returns {"status": "PASS" | "ISSUES", "text": <verdict>, "model": str}."""
    system, user = _build_constitution_prompt(detailed_response, constitution)
    result = _call_openai_with_fallback(
        system=system,
        user=user,
        max_tokens=VALIDATION_MAX_TOKENS,
        reasoning_effort="high",
    )
    text = result["text"].strip()
    status = "PASS" if text.upper().startswith("PASS") else "ISSUES"
    return {
        "status": status,
        "text": text,
        "model": result["model"],
        "wall_clock_s": result["wall_clock_s"],
    }


def run_validation_for_step1_output(
    step1_output: dict[str, Any],
    card: dict[str, Any],
    run_dir: Path,
) -> dict[str, Any]:
    """Run both validators against one Step 1 output. Write per-pair
    validation file. Returns the combined validation result.

    Output shape per spec: `{anachronism: PASS|<issues>, constitution:
    PASS|<issues>, regen_count: 0|1, final_status: clean|flagged}`.
    Regeneration is the orchestrator's responsibility (this module only
    runs the checks).
    """
    logger = get_logger("voice_validation")
    voice_slug = step1_output["lineage"]["voice_slug"]
    theme_id = step1_output["lineage"]["theme_id"]
    out_dir = run_dir / "04_voice" / "validation"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{voice_slug}__{theme_id}.json"

    if out_path.exists():
        with open(out_path, encoding="utf-8") as f:
            return json.load(f)

    detailed_response = step1_output["detailed_response"]
    anach = check_anachronism(
        detailed_response,
        card.get("knowledge_boundary"),
        card.get("voice_temporal_stance"),
    )
    const = check_constitution(detailed_response, card.get("constitution"))
    final_status = (
        "clean"
        if anach["status"] == "PASS" and const["status"] == "PASS"
        else "flagged"
    )
    result = {
        "anachronism": anach,
        "constitution": const,
        "regen_count": 0,
        "final_status": final_status,
    }
    write_json_atomic(out_path, result)
    logger.info(
        f"  Validation done: {voice_slug}__{theme_id} = {final_status} "
        f"(anach={anach['status']}/{anach['model']}, "
        f"const={const['status']}/{const['model']})"
    )
    return result
