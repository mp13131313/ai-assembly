"""Phase 0.5: Pre-DR Research runner.

Runs Pass 1a (Perplexity) and Pass 1b (Gemini) in parallel for a single voice,
then renders the Pass 0b Jinja template with their outputs and Wikipedia
grounding to produce the Claude DR prompt. No LLM call for the prompt
generation itself (Jinja2, deterministic).

This script runs AFTER Pass 0a (voice config) and BEFORE the manual Claude
DR session. Its outputs scaffold the DR prompt so Claude DR starts from
grounded research instead of zero.

Output files:
  runs/<slug>/01_research/perplexity_dossier.json
  runs/<slug>/01_research/gemini_broad_scan.json
  inputs/dossiers/_dr_prompts/<slug>_dr_prompt.md  — paste-ready DR prompt

Usage:
    python3 run_phase0_1_research.py "Cleopatra"
    python3 run_phase0_1_research.py "Plato"
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))

from dotenv import load_dotenv
load_dotenv(REPO_ROOT.parent / ".env")

import jinja2

from flows.shared.clients import call_perplexity, call_gemini
from flows.shared.io import voice_slug, write_json_atomic, load_voice_input
from flows.shared.node0_validation import validate_input
from flows.shared.prompt_render import render

VOICES_DIR = REPO_ROOT / "inputs/voices"
DR_PROMPTS_DIR = REPO_ROOT / "inputs/dossiers/_dr_prompts"
TEMPLATE_PATH = REPO_ROOT / "flows/shared/prompts/pass_0b_dr_prompt.md"


def stamp(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def cached(path: Path, label: str):
    """Return parsed JSON if path exists, else None and log."""
    if path.exists():
        stamp(f"  CACHE HIT: {label} -> {path.name}")
        with path.open(encoding="utf-8") as f:
            return json.load(f)
    return None


def main(voice_name: str) -> None:
    stamp(f"Phase 0.5 pre-DR research: '{voice_name}'")

    # Load and validate voice config
    vi_raw = load_voice_input(voice_name)
    vi = validate_input(vi_raw)
    SLUG = voice_slug(vi["name"])
    stamp(f"  voice: {vi['name']} | type={vi['type']} | hostile={vi['hostile_sources']}")

    RUN = REPO_ROOT / "runs" / SLUG
    (RUN / "01_research").mkdir(parents=True, exist_ok=True)

    # ---------- PASS 1a (Perplexity) ----------
    def _pass_1a():
        prompt = render("persona_pass_1a_research_human",
                        name=vi["name"], hostile_sources=vi["hostile_sources"])
        r = call_perplexity(user=prompt, temperature=0.0)
        return {
            "voice_name": vi["name"], "voice_slug": SLUG, "pass": "1a_research_dossier",
            "model": r["model"], "usage": r["usage"],
            "citations": r.get("citations", []),
            "search_results": r.get("search_results", []),
            "text": r["text"], "think": r["think"],
        }

    # ---------- PASS 1b (Gemini) ----------
    def _pass_1b():
        prompt = render("persona_pass_1b_broad_scan", name=vi["name"])
        r = call_gemini(user=prompt, temperature=0.2, max_output_tokens=16384)
        return {
            "voice_name": vi["name"], "voice_slug": SLUG, "pass": "1b_broad_scan",
            "model": r["model"], "usage": r["usage"], "text": r["text"],
        }

    pass1a_path = RUN / "01_research/perplexity_dossier.json"
    pass1b_path = RUN / "01_research/gemini_broad_scan.json"

    pass1a = cached(pass1a_path, "Pass 1a")
    pass1b = cached(pass1b_path, "Pass 1b")

    if pass1a is None or pass1b is None:
        # Run whichever are missing in parallel
        futures = {}
        with ThreadPoolExecutor(max_workers=2) as executor:
            if pass1a is None:
                stamp("PASS 1a: Perplexity sonar-deep-research (starting)")
                futures["1a"] = executor.submit(_pass_1a)
            if pass1b is None:
                stamp("PASS 1b: Gemini broad scan (starting)")
                futures["1b"] = executor.submit(_pass_1b)

        for key, future in futures.items():
            try:
                result = future.result()
            except Exception as exc:
                sys.exit(f"Pass {key} failed: {exc}")
            path = pass1a_path if key == "1a" else pass1b_path
            elapsed = result.get("_elapsed_seconds", 0)
            result["_elapsed_seconds"] = elapsed
            write_json_atomic(path, result)
            if key == "1a":
                pass1a = result
                stamp(f"  Pass 1a done: {len(result['text'])} chars")
            else:
                pass1b = result
                stamp(f"  Pass 1b done: {len(result['text'])} chars")

    perplexity_text = pass1a.get("text") or pass1a.get("text_clean", "")
    gemini_text = pass1b["text"]

    # ---------- RENDER PASS 0b JINJA TEMPLATE ----------
    stamp("PASS 0b: rendering DR prompt (Jinja2, no API call)...")

    display_name = vi["name"]
    wiki_url = vi_raw.get("wikipedia_url", "")

    template_src = TEMPLATE_PATH.read_text(encoding="utf-8")
    env = jinja2.Environment(
        undefined=jinja2.Undefined,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.from_string(template_src)

    context = {
        "name": display_name,
        "display_name_with_hint": display_name,
        "voice_slug": SLUG,
        "type": vi["type"],
        "subtype": vi.get("subtype"),
        "hostile_sources": bool(vi.get("hostile_sources", False)),
        "wikipedia_url": wiki_url or "",
        "voice_mode": vi.get("voice_mode"),
        "corpus_constraint": vi.get("corpus_constraint", "full"),
        "perplexity_findings": perplexity_text,
        "gemini_findings": gemini_text,
    }

    dr_prompt = template.render(**context)

    DR_PROMPTS_DIR.mkdir(parents=True, exist_ok=True)
    dr_prompt_path = DR_PROMPTS_DIR / f"{SLUG}_dr_prompt.md"
    dr_prompt_path.write_text(dr_prompt, encoding="utf-8")

    stamp(f"PASS 0b complete: DR prompt written to {dr_prompt_path.relative_to(REPO_ROOT)}")
    stamp(f"  Prompt size: {len(dr_prompt):,} chars (includes Perplexity + Gemini scaffolding)")
    stamp("")
    stamp("=" * 60)
    stamp("NEXT STEPS")
    stamp("=" * 60)
    stamp(f"  1. Review {dr_prompt_path.name}")
    stamp(f"  2. Open claude.ai — select Claude Opus 4.7, enable Extended Thinking + Deep Research")
    stamp(f"  3. Paste the prompt (starts after the '---' line)")
    stamp(f"  4. Wait 60-180 min. Save result as inputs/dossiers/{SLUG}_claude_dr.md")
    stamp(f"  5. Validate: python3 personas/scripts/validate_dr_dossier.py inputs/dossiers/{SLUG}_claude_dr.md")
    stamp(f"  6. Run pipeline: python3 run_persona_pipeline.py \"{display_name}\"")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Phase 0.5 — Pre-DR Research (Pass 1a + 1b + 0b)")
    parser.add_argument("name", help='Voice name, e.g. "Plato" or "Cleopatra"')
    args = parser.parse_args()
    main(args.name)
