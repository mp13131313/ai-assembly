"""Pass 0b — DR Prompt Generator.

Reads a finalized voice config (which a human has reviewed and possibly
edited after Pass 0a) and produces ONE artifact: the per-voice Claude
Deep Research prompt customized to that exact config.

  inputs/dossiers/_dr_prompts/<slug>_dr_prompt.md   — paste-ready DR prompt

Re-runnable: edit the voice config, re-run Pass 0b, get a fresh prompt
reflecting your edits.

Usage:
    python3 run_pass0b_dr_prompt.py "Cleopatra"
    python3 run_pass0b_dr_prompt.py "Octopus"
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))

from dotenv import load_dotenv
load_dotenv(REPO_ROOT.parent / ".env")

import anthropic as _anthropic
from flows.shared.clients import call_claude
from flows.shared.io import voice_slug

_RETRYABLE = (RuntimeError, json.JSONDecodeError, _anthropic.APIError, _anthropic.RateLimitError)


def _call_with_retry(stamp_fn, **kwargs):
    try:
        return call_claude(**kwargs)
    except _RETRYABLE as exc:
        stamp_fn(f"  Error on attempt 1 ({exc}); retrying in 15 s…")
        time.sleep(15)
    try:
        return call_claude(**kwargs)
    except _RETRYABLE as exc:
        sys.exit(f"Pass 0b failed after retry: {exc}")


PROJECT_CONTEXT_PATH = REPO_ROOT / "inputs/conference_context.json"
SYSTEM_PROMPT_PATH = REPO_ROOT / "flows/shared/prompts/pass_0b_dr_prompt.md"
VOICES_DIR = REPO_ROOT / "inputs/voices"
DR_PROMPTS_DIR = REPO_ROOT / "inputs/dossiers/_dr_prompts"


def stamp(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def main(name: str) -> None:
    stamp(f"Pass 0b DR-prompt: '{name}'")

    if not PROJECT_CONTEXT_PATH.exists():
        sys.exit(f"Missing project config: {PROJECT_CONTEXT_PATH}")
    if not SYSTEM_PROMPT_PATH.exists():
        sys.exit(f"Missing system prompt: {SYSTEM_PROMPT_PATH}")

    slug = voice_slug(name)
    voice_path = VOICES_DIR / f"{slug}.json"
    if not voice_path.exists():
        sys.exit(
            f"Missing voice config at {voice_path}. "
            f"Run Pass 0a first: python3 run_pass0a_voice_config.py \"{name}\" --hint \"...\""
        )

    voice_config = json.loads(voice_path.read_text())
    project_ctx = json.loads(PROJECT_CONTEXT_PATH.read_text())

    system = SYSTEM_PROMPT_PATH.read_text()
    user_payload = {
        "voice_config": voice_config,
        "project_context": project_ctx,
    }
    user = (
        "Generate the DR prompt for the voice below by instantiating the "
        "template per the system prompt. Return ONLY the JSON object with "
        "the single key dr_prompt.\n\n"
        f"INPUT:\n{json.dumps(user_payload, ensure_ascii=False, indent=2)}"
    )

    stamp("Calling Claude Opus 4.7 + adaptive thinking...")
    t0 = time.time()
    r = _call_with_retry(
        stamp,
        system=system,
        user=user,
        model="claude-opus-4-7",
        max_tokens=24000,
        temperature=1.0,
        thinking_budget=None,  # adaptive thinking
        response_format_json=True,
    )
    wall = time.time() - t0
    stamp(f"  done in {wall:.1f}s | tokens in={r['usage']['input_tokens']} out={r['usage']['output_tokens']}")

    out = r["json"]
    if "dr_prompt" not in out:
        sys.exit("Pass 0b output missing required key: dr_prompt")
    dr_prompt = out["dr_prompt"]

    DR_PROMPTS_DIR.mkdir(parents=True, exist_ok=True)
    dr_prompt_path = DR_PROMPTS_DIR / f"{slug}_dr_prompt.md"
    dr_prompt_path.write_text(dr_prompt, encoding="utf-8")

    stamp(f"Pass 0b complete — review {dr_prompt_path.name} before pasting into claude.ai.")
    stamp(f"  DR prompt:     {dr_prompt_path.relative_to(REPO_ROOT)}")
    stamp("")
    stamp("Next steps:")
    stamp(f"  1. Open claude.ai, select Claude Opus 4.7 in the model picker")
    stamp(f"     (DR inherits the selected model; Opus is required for dossier depth)")
    stamp(f"  2. Enable Extended Thinking + Deep Research")
    stamp(f"  3. Paste the prompt from {dr_prompt_path.name}")
    stamp(f"  4. Expect 60-180 min wait")
    stamp(f"  5. Save the result as inputs/dossiers/{slug}_claude_dr.md")
    stamp(f"  6. Run: python3 run_persona_pipeline.py \"{voice_config.get('name', name)}\"")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pass 0b — DR Prompt Generator")
    parser.add_argument("name", help='Voice name (must match Pass 0a output)')
    args = parser.parse_args()
    main(args.name)
