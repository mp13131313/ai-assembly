"""Pass 0b — DR Prompt Generator (Jinja2 template renderer).

Reads a finalized voice config (which a human has reviewed and possibly
edited after Pass 0a) and renders ONE artifact: the per-voice Claude
Deep Research prompt for that exact config.

  <project_root>/inputs/dossiers/_dr_prompts/<slug>_dr_prompt.md   — paste-ready DR prompt

Re-runnable: edit the voice config, re-run Pass 0b, get a fresh prompt
reflecting your edits. No API call — deterministic, zero API cost.

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

try:
    import jinja2
except ImportError:
    sys.exit("Pass 0b requires jinja2. Install with: pip install jinja2")

from flows.shared.io import voice_slug
from flows.shared.project_root import add_project_arg, resolve_project_root

TEMPLATE_PATH = REPO_ROOT / "flows/shared/prompts/pass_0b_dr_prompt.md"


def stamp(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def main(name: str, project: str | None = None) -> None:
    stamp(f"Pass 0b DR-prompt: '{name}'")

    project_root = resolve_project_root(project, repo_root=REPO_ROOT)
    voices_dir = project_root / "inputs/voices"
    dr_prompts_dir = project_root / "inputs/dossiers/_dr_prompts"

    if not TEMPLATE_PATH.exists():
        sys.exit(f"Missing template: {TEMPLATE_PATH}")

    slug = voice_slug(name)
    voice_path = voices_dir / f"{slug}.json"
    if not voice_path.exists():
        sys.exit(
            f"Missing voice config at {voice_path}. "
            f"Run Pass 0a first: python3 run_pass0a_voice_config.py \"{name}\""
        )

    voice_config = json.loads(voice_path.read_text())

    # Build display_name_with_hint: name + Wikipedia description if available
    display_name = voice_config.get("name", name)
    wiki_url = voice_config.get("wikipedia_url")
    display_name_with_hint = display_name

    # Render Jinja2 template
    template_src = TEMPLATE_PATH.read_text(encoding="utf-8")
    env = jinja2.Environment(
        undefined=jinja2.Undefined,  # silently ignore unknown vars
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.from_string(template_src)

    context = {
        "name": display_name,
        "display_name_with_hint": display_name_with_hint,
        "voice_slug": slug,
        "type": voice_config.get("type", "human"),
        "subtype": voice_config.get("subtype"),
        "hostile_sources": bool(voice_config.get("hostile_sources", False)),
        "wikipedia_url": wiki_url or "",
        "voice_mode": voice_config.get("voice_mode"),
        "corpus_constraint": voice_config.get("corpus_constraint", "full"),
        # D.1 scaffolding variables (empty until run_phase0_1_research.py provides them)
        "perplexity_findings": "",
        "perplexity_sections": None,
        "gemini_findings": "",
    }

    dr_prompt = template.render(**context)

    dr_prompts_dir.mkdir(parents=True, exist_ok=True)
    dr_prompt_path = dr_prompts_dir / f"{slug}_dr_prompt.md"
    dr_prompt_path.write_text(dr_prompt, encoding="utf-8")

    stamp(f"Pass 0b complete — review {dr_prompt_path.name} before pasting into claude.ai.")
    stamp(f"  DR prompt:     {dr_prompt_path.relative_to(project_root)}")
    stamp("")
    stamp("Next steps:")
    stamp(f"  1. Open claude.ai, select Claude Opus 4.7 in the model picker")
    stamp(f"  2. Enable Extended Thinking + Deep Research")
    stamp(f"  3. Paste the prompt from {dr_prompt_path.name}")
    stamp(f"  4. Expect 60-180 min wait")
    stamp(f"  5. Save the result as <project_root>/inputs/dossiers/{slug}_claude_dr.md")
    stamp(f"  6. Run: python3 run_persona_pipeline.py \"{display_name}\"")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pass 0b — DR Prompt Generator")
    parser.add_argument("name", help='Voice name (must match Pass 0a output)')
    add_project_arg(parser)
    args = parser.parse_args()
    main(args.name, project=args.project)
