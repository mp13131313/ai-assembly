"""Stage 0b — DR Prompt Generator.

Reads a finalized voice config (which a human has reviewed and possibly
edited after Stage 0a) and produces ONE artifact: the per-voice Claude
Deep Research prompt customized to that exact config.

  inputs/dossiers/_dr_prompts/<slug>_dr_prompt.md   — paste-ready DR prompt

This stage runs SEPARATELY from Stage 0a so the human can edit the voice
config (especially the editorial-assets fields: counter_tradition_scholars,
contested_interpretations, material_culture_evidence, voice_specific_warnings)
between intake and DR-prompt generation. Re-runnable: edit the voice config,
re-run Stage 0b, get a fresh prompt reflecting your edits.

Usage:
    python3 run_stage0b_dr_prompt.py "Cleopatra"
    python3 run_stage0b_dr_prompt.py "Octopus"
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, ".")
from dotenv import load_dotenv
load_dotenv("/Users/aienvironment/Desktop/ai-assembly-personas/.env")

from flows.shared.clients import call_claude


REPO_ROOT = Path(__file__).resolve().parent
PROJECT_CONTEXT_PATH = REPO_ROOT / "inputs/conference_context.json"
SYSTEM_PROMPT_PATH = REPO_ROOT / "flows/shared/prompts/stage_0b_dr_prompt.md"
VOICES_DIR = REPO_ROOT / "inputs/voices"
DR_PROMPTS_DIR = REPO_ROOT / "inputs/dossiers/_dr_prompts"


def slugify(name: str) -> str:
    s = name.lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    return s.strip("_")


def stamp(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def main(name: str) -> None:
    stamp(f"Stage 0b DR-prompt: '{name}'")

    if not PROJECT_CONTEXT_PATH.exists():
        sys.exit(f"Missing project config: {PROJECT_CONTEXT_PATH}")
    if not SYSTEM_PROMPT_PATH.exists():
        sys.exit(f"Missing system prompt: {SYSTEM_PROMPT_PATH}")

    slug = slugify(name)
    voice_path = VOICES_DIR / f"{slug}.json"
    if not voice_path.exists():
        sys.exit(
            f"Missing voice config at {voice_path}. "
            f"Run Stage 0a first: python3 run_stage0a_intake.py \"{name}\""
        )

    voice_config = json.loads(voice_path.read_text())
    project_ctx = json.loads(PROJECT_CONTEXT_PATH.read_text())

    # Sanity-check: voice config has the expected editorial-assets fields
    required_assets = (
        "voice_type_adjustments_needed",
        "counter_tradition_scholars",
        "dominant_hostile_sources",
        "contested_interpretations",
        "material_culture_evidence",
        "voice_specific_warnings",
    )
    missing = [k for k in required_assets if k not in voice_config]
    if missing:
        stamp(f"WARNING: voice config missing editorial-assets fields: {missing}")
        stamp(f"  Stage 0a may not have produced them, or the file pre-dates the schema.")
        stamp(f"  Stage 0b will proceed but the DR prompt may be less customized.")

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

    stamp("Calling Claude Opus 4.6 + adaptive thinking...")
    t0 = time.time()
    r = call_claude(
        system=system,
        user=user,
        model="claude-opus-4-6",
        max_tokens=24000,
        temperature=1.0,
        thinking_budget=None,  # adaptive thinking
        response_format_json=True,
    )
    wall = time.time() - t0
    stamp(f"  done in {wall:.1f}s | tokens in={r['usage']['input_tokens']} out={r['usage']['output_tokens']}")

    out = r["json"]
    if "dr_prompt" not in out:
        sys.exit("Stage 0b output missing required key: dr_prompt")
    dr_prompt = out["dr_prompt"]

    DR_PROMPTS_DIR.mkdir(parents=True, exist_ok=True)
    dr_prompt_path = DR_PROMPTS_DIR / f"{slug}_dr_prompt.md"
    dr_prompt_path.write_text(dr_prompt, encoding="utf-8")

    stamp("Stage 0b complete.")
    stamp(f"  DR prompt:     {dr_prompt_path.relative_to(REPO_ROOT)}")
    stamp("")
    stamp("Next steps:")
    stamp(f"  1. Open claude.ai with Extended Thinking + Deep Research enabled")
    stamp(f"  2. Paste the prompt from {dr_prompt_path.name}")
    stamp(f"  3. Save the result as inputs/dossiers/{slug}_claude_dr.md")
    stamp(f"  4. Run: python3 run_persona_pipeline.py \"{voice_config.get('name', name)}\"")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Stage 0b — DR Prompt Generator")
    parser.add_argument("name", help='Voice name (must match Stage 0a output)')
    args = parser.parse_args()
    main(args.name)
