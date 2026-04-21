"""Pass 0b hybrid tailoring pass (PB#2).

Runs AFTER the Jinja-rendered DR prompt is produced by run_phase0_1_research.
Reads the base DR prompt + Perplexity dossier + curator's editorial_rationale
+ voice_config, calls Opus 4.7 with `pass_0b_tailor.md`, and writes the
voice-tailored DR prompt to replace the base one.

Invoked automatically at the end of run_phase0_1_research.main() if the
voice_config has editorial_rationale set. If editorial_rationale is null,
the tailoring pass is skipped with a warning (the base Jinja prompt is
still usable; tailoring is optimization, not architectural requirement).

Output (all under PROJECT_ROOT):
- <project_root>/inputs/dossiers/_dr_prompts/<slug>_dr_prompt.md — the
  tailored prompt (overwrites the base Jinja render)
- <project_root>/inputs/dossiers/_dr_prompts/<slug>_dr_prompt.base.md —
  preserved base for comparison
- <project_root>/inputs/dossiers/_dr_prompts/<slug>_tailoring_notes.json —
  the audit log the model produced
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
load_dotenv(REPO_ROOT.parent / ".env", override=True)

from flows.shared import paths as _paths
from flows.shared.clients import call_claude
from flows.shared.io import voice_slug, write_json_atomic
from flows.shared.project_root import add_project_arg, resolve_project_root
from flows.shared.prompt_render import render


def stamp(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def run_pass_0b_tailor(name: str, project_root: Path | None = None,
                        project: str | None = None) -> dict:
    slug = voice_slug(name)
    stamp(f"Pass 0b tailor: '{name}' (slug={slug})")

    if project_root is None:
        project_root = resolve_project_root(project, repo_root=REPO_ROOT)
    stamp(f"  PROJECT_ROOT={project_root}")

    # Paths — all under PROJECT_ROOT per Tier 3 (new per-voice layout).
    voice_config_path = _paths.voice_config(slug, project_root)
    perp_path = _paths.perplexity_dossier(slug, project_root)
    gemini_path = _paths.gemini_broad_scan(slug, project_root)
    base_prompt_path = _paths.monolithic_dr_prompt(slug, project_root)
    base_preserved_path = base_prompt_path.with_suffix(".base.md")
    tailored_prompt_path = base_prompt_path  # overwrite base
    notes_path = _paths.tailoring_notes(slug, project_root)

    for p in (voice_config_path, perp_path, gemini_path, base_prompt_path):
        if not p.exists():
            sys.exit(f"Missing input: {p}")

    voice_config = json.loads(voice_config_path.read_text())

    perp = json.loads(perp_path.read_text())
    perp_text = perp.get("text") or perp.get("text_clean", "")
    gem = json.loads(gemini_path.read_text())
    gem_text = gem.get("text", "")
    base_prompt = base_prompt_path.read_text()

    # Preserve the base BEFORE we overwrite it.
    if not base_preserved_path.exists():
        base_preserved_path.write_text(base_prompt, encoding="utf-8")
        stamp(f"  preserved base prompt → {base_preserved_path.name}")

    # editorial_rationale is OPTIONAL per PB#2: tailoring always runs on the
    # basis of Perplexity-coverage analysis + voice-config specifics. If the
    # curator provided a rationale, it's fed in as an ADDITIONAL signal for
    # the LLM to weight thematic emphasis. Null rationale → the LLM still
    # tailors on coverage + voice alone.
    editorial_rationale = voice_config.get("editorial_rationale") or "(not provided — tailor on coverage + voice-config alone)"

    system = render(
        "pass_0b_tailor",
        name=name,
        voice_config_json=json.dumps(voice_config, ensure_ascii=False, indent=2),
        editorial_rationale=editorial_rationale,
        perplexity_dossier_text=perp_text,
        gemini_broad_scan_text=gem_text,
        base_dr_prompt=base_prompt,
    )
    user = (
        "Produce the voice-tailored DR prompt + tailoring_notes[] per the "
        "system-prompt schema. JSON only."
    )

    stamp("  calling Opus 4.7 + adaptive thinking…")
    t0 = time.time()
    r = call_claude(
        system=system, user=user, model="claude-opus-4-7",
        max_tokens=40000, temperature=1.0, thinking=True,
        response_format_json=True,
    )
    wall = time.time() - t0
    stamp(f"  done in {wall:.1f}s — tokens in={r['usage']['input_tokens']} out={r['usage']['output_tokens']}")

    out = r["json"]
    tailored = out.get("tailored_dr_prompt")
    notes = out.get("tailoring_notes", [])
    if not tailored:
        sys.exit("Pass 0b tailor returned no tailored_dr_prompt key")

    tailored_prompt_path.write_text(tailored, encoding="utf-8")
    write_json_atomic(notes_path, {
        "voice_name": name, "voice_slug": slug,
        "tailoring_notes": notes, "model": r.get("model"), "usage": r["usage"],
    })

    stamp(f"  tailored prompt → {tailored_prompt_path.name} ({len(tailored):,} chars)")
    stamp(f"  tailoring notes → {notes_path.name} ({len(notes)} entries)")
    for n in notes[:8]:
        stamp(f"    · {n}")
    return {"status": "tailored", "tailoring_notes": notes,
            "tailoring_notes_count": len(notes),
            "prompt_size_chars": len(tailored)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pass 0b hybrid tailoring (PB#2)")
    parser.add_argument("name", help='Voice name, e.g. "Plato"')
    add_project_arg(parser)
    args = parser.parse_args()
    run_pass_0b_tailor(args.name, project=args.project)
