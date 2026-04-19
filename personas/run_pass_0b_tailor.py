"""Pass 0b hybrid tailoring pass (PB#2).

Runs AFTER the Jinja-rendered DR prompt is produced by run_phase0_1_research.
Reads the base DR prompt + Perplexity dossier + curator's editorial_rationale
+ voice_config, calls Opus 4.7 with `pass_0b_tailor.md`, and writes the
voice-tailored DR prompt to replace the base one.

Invoked automatically at the end of run_phase0_1_research.main() if the
voice_config has editorial_rationale set. If editorial_rationale is null,
the tailoring pass is skipped with a warning (the base Jinja prompt is
still usable; tailoring is optimization, not architectural requirement).

Output:
- inputs/dossiers/_dr_prompts/<slug>_dr_prompt.md — the tailored prompt
  (overwrites the base Jinja render)
- inputs/dossiers/_dr_prompts/<slug>_dr_prompt.base.md — preserved base
  for comparison
- inputs/dossiers/_dr_prompts/<slug>_tailoring_notes.json — the audit
  log the model produced
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

from flows.shared.clients import call_claude
from flows.shared.io import voice_slug, write_json_atomic
from flows.shared.prompt_render import render


def stamp(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def run_pass_0b_tailor(name: str) -> dict:
    slug = voice_slug(name)
    stamp(f"Pass 0b tailor: '{name}' (slug={slug})")

    # Paths.
    voice_config_path = REPO_ROOT / "inputs" / "voices" / f"{slug}.json"
    perp_path = REPO_ROOT / "runs" / slug / "01_research" / "perplexity_dossier.json"
    base_prompt_path = REPO_ROOT / "inputs/dossiers/_dr_prompts" / f"{slug}_dr_prompt.md"
    base_preserved_path = REPO_ROOT / "inputs/dossiers/_dr_prompts" / f"{slug}_dr_prompt.base.md"
    tailored_prompt_path = base_prompt_path  # overwrite base
    notes_path = REPO_ROOT / "inputs/dossiers/_dr_prompts" / f"{slug}_tailoring_notes.json"

    for p in (voice_config_path, perp_path, base_prompt_path):
        if not p.exists():
            sys.exit(f"Missing input: {p}")

    voice_config = json.loads(voice_config_path.read_text())
    if not voice_config.get("editorial_rationale"):
        stamp(
            "  editorial_rationale is null; skipping tailoring pass. "
            "The base Jinja DR prompt remains in place."
        )
        return {"status": "skipped", "reason": "editorial_rationale null"}

    perp = json.loads(perp_path.read_text())
    perp_text = perp.get("text") or perp.get("text_clean", "")
    base_prompt = base_prompt_path.read_text()

    # Preserve the base BEFORE we overwrite it.
    if not base_preserved_path.exists():
        base_preserved_path.write_text(base_prompt, encoding="utf-8")
        stamp(f"  preserved base prompt → {base_preserved_path.name}")

    system = render(
        "pass_0b_tailor",
        name=name,
        voice_config_json=json.dumps(voice_config, ensure_ascii=False, indent=2),
        editorial_rationale=voice_config["editorial_rationale"],
        perplexity_dossier_text=perp_text,
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
            "prompt_size_chars": len(tailored)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pass 0b hybrid tailoring (PB#2)")
    parser.add_argument("name", help='Voice name, e.g. "Plato"')
    args = parser.parse_args()
    run_pass_0b_tailor(args.name)
