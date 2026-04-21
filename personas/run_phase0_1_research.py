"""Phase 0.5: Pre-DR Research runner.

Runs Pass 1a (Perplexity) and Pass 1b (Gemini) in parallel for a single voice,
then renders the Pass 0b Jinja template with their outputs and Wikipedia
grounding to produce the Claude DR prompt. No LLM call for the prompt
generation itself (Jinja2, deterministic).

This script runs AFTER Pass 0a (voice config) and BEFORE the manual Claude
DR session. Its outputs scaffold the DR prompt so Claude DR starts from
grounded research instead of zero.

Output files (all under PROJECT_ROOT per Tier 3):
  <project_root>/runs/<slug>/01_research/perplexity_dossier.json
  <project_root>/runs/<slug>/01_research/gemini_broad_scan.json
  <project_root>/inputs/dossiers/_dr_prompts/<slug>_dr_prompt.md  — paste-ready DR prompt

Usage:
    python3 run_phase0_1_research.py "Cleopatra"
    python3 run_phase0_1_research.py "Plato" --project /path/to/athens-2026
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
load_dotenv(REPO_ROOT.parent / ".env", override=True)

import jinja2
import requests

from flows.shared import paths
from flows.shared.clients import call_perplexity, call_gemini
from flows.shared.io import voice_slug, write_json_atomic, load_voice_input
from flows.shared.node0_validation import validate_input
from flows.shared.perplexity_split import split_dossier
from flows.shared.project_root import add_project_arg, resolve_project_root
from flows.shared.prompt_render import render
from flows.shared.research_validation import (
    print_warnings,
    validate_gemini_scan,
    validate_perplexity_dossier,
)


# Retryable errors for Perplexity + Gemini. Mirrors the Pass 0a retry pattern.
# Transient network errors, API rate limits, and incomplete / malformed
# responses trigger one retry after 15s. A second failure exits the pass.
_RETRYABLE = (
    RuntimeError,  # our own raise in call_perplexity on missing response structure
    json.JSONDecodeError,
    requests.exceptions.RequestException,  # network + timeout + HTTP errors
)


def _with_retry(fn, *, label: str):
    """Call fn(); on retryable error, retry twice (15s then 60s).

    Saves a failed $5-10 Perplexity call from transient network blips. On
    the third failure, raises — the pipeline loses the call, but at least
    the curator knows to investigate rather than silently proceed with an
    empty result.
    """
    for delay in (15, 60):
        try:
            return fn()
        except _RETRYABLE as exc:
            stamp(f"  {label}: retryable error ({type(exc).__name__}: {str(exc)[:120]}); "
                  f"sleeping {delay}s then retrying")
            time.sleep(delay)
    return fn()  # third attempt — propagates on failure

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


def main(voice_name: str, project: str | None = None) -> None:
    stamp(f"Phase 0.5 pre-DR research: '{voice_name}'")

    project_root = resolve_project_root(project, repo_root=REPO_ROOT)
    stamp(f"  PROJECT_ROOT={project_root}")

    DR_PROMPTS_DIR = project_root / "inputs/dossiers/_dr_prompts"

    # Load and validate voice config
    vi_raw = load_voice_input(voice_name, project_root)
    vi = validate_input(vi_raw)
    SLUG = voice_slug(vi["name"])
    stamp(f"  voice: {vi['name']} | type={vi['type']} | hostile={vi['hostile_sources']}")

    RUN = project_root / "runs" / SLUG
    (RUN / "01_research").mkdir(parents=True, exist_ok=True)

    # Phase B: voice-type-specific 1a + 1b prompts per decisions log #7.
    def _pick_template(base: str) -> str:
        t, sub = vi["type"], vi.get("subtype")
        if t == "human":
            return f"{base}_human"
        if t == "fictional":
            return f"{base}_fictional"
        if t == "non_human":
            if sub == "organism":
                return f"{base}_non_human_organism"
            if sub == "system":
                return f"{base}_non_human_system"
        sys.exit(f"Cannot resolve {base} template for type={t!r} subtype={sub!r}")

    # ---------- PASS 1a (Perplexity) ----------
    def _pass_1a():
        prompt = render(_pick_template("persona_pass_1a"),
                        name=vi["name"], hostile_sources=vi["hostile_sources"])
        r = _with_retry(
            lambda: call_perplexity(user=prompt, temperature=0.0),
            label="Pass 1a (Perplexity)",
        )
        return {
            "voice_name": vi["name"], "voice_slug": SLUG, "pass": "1a_research_dossier",
            "model": r["model"], "usage": r["usage"],
            "citations": r.get("citations", []),
            "search_results": r.get("search_results", []),
            "text": r["text"], "think": r["think"],
        }

    # ---------- PASS 1b (Gemini) ----------
    def _pass_1b():
        prompt = render(_pick_template("persona_pass_1b"), name=vi["name"])
        r = _with_retry(
            lambda: call_gemini(user=prompt, temperature=0.2, max_output_tokens=16384),
            label="Pass 1b (Gemini)",
        )
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

    # ---------- SMOKE-TEST VALIDATORS (non-blocking) ----------
    # Grep-check the research outputs against the Pass 1a/1b prompt's structural
    # asks. Warnings only — Pass 1.1-1.6 merge will attempt synthesis regardless.
    # Surfaces thinness (missing period-vocabulary, missing counter-tradition
    # block, short dossier) early so the curator can re-run Phase 0.5 with a
    # tighter --hint before committing to the manual Claude DR session.
    stamp("Pass 1a smoke-test:")
    perp_checks = validate_perplexity_dossier(
        text=perplexity_text,
        voice_type=vi["type"],
        hostile_sources=vi["hostile_sources"],
    )
    print_warnings(perp_checks, "Pass 1a", stamp)
    stamp("Pass 1b smoke-test:")
    gem_checks = validate_gemini_scan(text=gemini_text, voice_type=vi["type"])
    print_warnings(gem_checks, "Pass 1b", stamp)

    perplexity_sections = split_dossier(perplexity_text)
    if perplexity_sections is None:
        stamp("  WARN: Perplexity output could not be split by section — falling back to single-block scaffolding")
    else:
        stamp(f"  Perplexity split: {len(perplexity_sections)} sections recognized")

    # ---------- RENDER PASS 0b JINJA TEMPLATE ----------
    stamp("PASS 0b: rendering DR prompt (Jinja2, no API call)...")

    display_name = vi["name"]
    wiki_url = vi_raw.get("wikipedia_url", "")

    # Phase B G.3: pass_0b_dr_prompt.md is now a wrapper that `{% include %}`s
    # per-type sub-templates. Need FileSystemLoader pointing at the prompts/
    # directory so includes resolve. Still using jinja2.Undefined (not
    # StrictUndefined) — pass_0b tolerates many conditional vars being absent.
    prompts_dir = TEMPLATE_PATH.parent
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(prompts_dir)),
        undefined=jinja2.Undefined,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.get_template(TEMPLATE_PATH.name)

    # Position C: the base render uses classification vars only. Perplexity +
    # Gemini research content enters the pipeline at the tailoring step
    # (run_pass_0b_tailor.py), not here. The base template has no
    # {{ perplexity_findings }} / {{ gemini_findings }} references in Phase B;
    # prior Position A design inlined them, Position C does not.
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
    }

    dr_prompt = template.render(**context)

    DR_PROMPTS_DIR.mkdir(parents=True, exist_ok=True)
    dr_prompt_path = DR_PROMPTS_DIR / f"{SLUG}_dr_prompt.md"
    dr_prompt_path.write_text(dr_prompt, encoding="utf-8")

    stamp(f"PASS 0b base render complete: {dr_prompt_path.relative_to(project_root)}")
    stamp(f"  Base prompt size: {len(dr_prompt):,} chars")

    # ---------- PASS 0b HYBRID TAILORING (PB#2, always runs) ----------
    # Per REBUILD_PLAN PB#2 "replaces pure Jinja" — always fires, not gated.
    # LLM reads Perplexity + Gemini + voice_config and tailors the DR prompt:
    # swaps generic illustrative figures for voice-specific ones, customizes
    # SWAP TEST anchors, redirects emphasis based on where Perplexity coverage
    # is thin vs thick. editorial_rationale, if present, is an OPTIONAL
    # amplification signal — not the trigger.
    # Overwrites the base prompt; preserves the base at <slug>_dr_prompt.base.md.
    stamp("PASS 0b tailor: hybrid Jinja+LLM tailoring (PB#2)…")
    from run_pass_0b_tailor import run_pass_0b_tailor  # noqa: E402 — deferred
    section_paths: list[Path] = []
    try:
        tailor_result = run_pass_0b_tailor(vi["name"], project_root=project_root)
        stamp(f"  tailoring: {tailor_result['status']} "
              f"({tailor_result.get('tailoring_notes_count', '?')} edits)")

        # Copy tailored output to new per-voice path, then split into 6 sections.
        old_tailored_path = DR_PROMPTS_DIR / f"{SLUG}_dr_prompt.md"
        monolithic_path = paths.monolithic_dr_prompt(SLUG, project_root)
        monolithic_path.parent.mkdir(parents=True, exist_ok=True)
        monolithic_path.write_text(old_tailored_path.read_text(encoding="utf-8"), encoding="utf-8")
        stamp(f"  monolithic → {monolithic_path.relative_to(project_root)}")

        from scripts.split_tailored_prompt import split_tailored_prompt  # noqa: E402
        section_paths = split_tailored_prompt(SLUG, project_root)
        stamp(f"  split → {len(section_paths)} section prompt files")
    except Exception as exc:
        stamp(f"  WARN: tailoring/split pass failed ({type(exc).__name__}: {str(exc)[:120]}); "
              f"base prompt remains in place")

    stamp("")
    stamp("=" * 60)
    stamp("NEXT STEPS — manual Claude Deep Research")
    stamp("=" * 60)
    _mono_rel = paths.monolithic_dr_prompt(SLUG, project_root).relative_to(project_root)
    stamp(f"Phase 0.5 research complete. Tailored monolithic prompt at:")
    stamp(f"  {_mono_rel}")
    _dr_prompts_rel = paths.dr_prompts_dir(SLUG, project_root).relative_to(project_root)
    stamp(f"\nSplit into 6 paste-ready section prompts at:")
    stamp(f"  {_dr_prompts_rel}/")
    for n in range(1, 7):
        p = paths.section_dr_prompt(SLUG, n, project_root)
        arrow = "  ← paste these" if n == 1 else ""
        stamp(f"    {p.name}{arrow}")
    stamp(f"""
WORKFLOW:

1. Open claude.ai, select Opus 4.6, enable Extended Thinking + Deep Research.

2. For each section (1 through 6):
   (a) Paste the section prompt into claude.ai.
   (b) Wait ~30 min for Research to complete (if past 60 min without draft
       streaming visible, cancel and retry).
   (c) Click "Download as .md" button to save the DR output.
   (d) Move/rename the download to:
       voices/{SLUG}/01_research/04_dr_dossier/0N_section_N.md

3. Operator choice: paste all 6 in the same thread (for cross-section
   coherence) or in fresh threads per section (for independent sampling).
   Both paths are empirically validated.

4. When all 6 sections are saved, run the pipeline:
   cd personas && venv/bin/python run_persona_pipeline.py "{display_name}" --project {project_root}

The pipeline auto-detects per-section mode from the dr_dossier/ directory
state. If fewer than 6 section files present, it errors with a clear
message indicating which section is missing.

For monolithic fallback (treat saved DR outputs as one file): concatenate
the 6 section files into voices/{SLUG}/01_research/04_dr_dossier/07_concat_claude_dr.md
before running the pipeline. Chunk_runner auto-detects the monolithic
file if per-section files absent.""")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Phase 0.5 — Pre-DR Research (Pass 1a + 1b + 0b)")
    parser.add_argument("name", help='Voice name, e.g. "Plato" or "Cleopatra"')
    add_project_arg(parser)
    args = parser.parse_args()
    main(args.name, project=args.project)
