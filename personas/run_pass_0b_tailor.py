"""Pass 0b hybrid tailoring pass (PB#2).

Runs AFTER the Jinja-rendered DR prompt is produced by run_phase0_1_research.
Reads the base DR prompt + Perplexity dossier + curator's editorial_rationale
+ voice_config, calls Opus 4.7 with `pass_0b_tailor.md`, and writes the
voice-tailored DR prompt to replace the base one.

2026-04-24 architectural rewrite (Plato regression fix):

  Old: LLM returned the complete tailored DR prompt as a single markdown
  string, trusted to preserve base content verbatim while inserting
  injections. Plato's run ignored that trust and rewrote every §1-5
  into a shortened summary + its follow-up questions, dropping every
  canonical Fix #34 bullet — violating PB#2's "LLM does NOT rewrite
  bullet structure."

  New: LLM returns a STRUCTURED INJECTIONS object (section_injections,
  swap_test_anchor, thematic_note, tailoring_notes). Python deterministically
  splices injections into the base at known placeholder slots. Base
  preservation is architectural, not prompt-discipline-trusted.

Splicing targets (in base prompt):
- Six `<!-- COVERAGE-NOTE-PLACEHOLDER: ... -->` comments (one per
  section) → replaced with formatted follow-up-questions blocks.
- `**THE SWAP TEST.**` paragraph in §4 → optionally followed by a
  voice-specific anchor note.
- Prompt introduction → optionally prepended with a thematic note
  when editorial_rationale is substantive.

Output (all under PROJECT_ROOT, per-voice layout):
- <project_root>/voices/<slug>/01_research/03_dr_prompts/01_monolithic_dr_prompt.md —
  the tailored prompt (overwrites the base Jinja render)
- <project_root>/voices/<slug>/01_research/03_dr_prompts/01_monolithic_dr_prompt.base.md —
  preserved base for comparison
- <project_root>/voices/<slug>/01_research/03_dr_prompts/02_tailoring_notes.json —
  the audit log the model produced
"""
from __future__ import annotations

import argparse
import json
import re
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


# ── splicing primitives ─────────────────────────────────────────────────────

_PLACEHOLDER_RE = re.compile(
    r"<!-- COVERAGE-NOTE-PLACEHOLDER:[^>]*-->",
)

# Matches the opening of §4's SWAP TEST paragraph. The full paragraph ends
# with "a generic literate-AI register." or similar; we append our anchor
# AFTER the paragraph's trailing newline by splicing right after the first
# occurrence of the opening marker's enclosing paragraph. Simpler: regex
# the whole paragraph on the assumption it's a single line in the base.
_SWAP_TEST_PARAGRAPH_RE = re.compile(
    r"\*\*THE SWAP TEST\.\*\* [^\n]+",
)


def _format_questions_block(questions: list[str]) -> str:
    """Format a list of 2-3 question strings as a markdown block."""
    if not questions:
        raise ValueError("questions list must not be empty")
    items = "\n\n".join(f"{i+1}. {q.strip()}" for i, q in enumerate(questions))
    return (
        "**Voice-specific follow-up questions for this section** "
        "(gaps Perplexity + Gemini left unresolved):\n\n"
        + items
    )


def splice_injections(
    base_prompt: str,
    section_injections: dict[str, list[str]],
    swap_test_anchor: str | None = None,
    thematic_note: str | None = None,
) -> str:
    """Deterministically splice LLM-produced injections into the base prompt.

    Replaces each of the six COVERAGE-NOTE-PLACEHOLDER comments with a
    formatted questions block from section_injections[str(n)].

    Optionally appends swap_test_anchor after §4's SWAP TEST paragraph
    and prepends thematic_note to the prompt introduction.

    Raises ValueError if the base prompt doesn't contain exactly 6
    placeholders or if any required section_injections key is missing/empty.
    """
    # Validate placeholder count
    matches = list(_PLACEHOLDER_RE.finditer(base_prompt))
    if len(matches) != 6:
        raise ValueError(
            f"Base prompt must contain exactly 6 COVERAGE-NOTE-PLACEHOLDER "
            f"comments, found {len(matches)}. Cannot splice."
        )

    # Validate injections
    for n in range(1, 7):
        key = str(n)
        if key not in section_injections:
            raise ValueError(f"section_injections missing required key {key!r}")
        questions = section_injections[key]
        if not isinstance(questions, list) or not questions:
            raise ValueError(
                f"section_injections[{key!r}] must be a non-empty list, "
                f"got {type(questions).__name__} ({questions!r})"
            )

    # Replace placeholders in reverse order so earlier indices stay valid
    result = base_prompt
    for n in range(6, 0, -1):
        match = matches[n - 1]
        formatted = _format_questions_block(section_injections[str(n)])
        result = result[: match.start()] + formatted + result[match.end():]

    # Optional: append swap_test_anchor after §4's SWAP TEST paragraph
    if swap_test_anchor:
        swap_match = _SWAP_TEST_PARAGRAPH_RE.search(result)
        if swap_match:
            insertion = "\n\n" + swap_test_anchor.strip()
            result = (
                result[: swap_match.end()] + insertion + result[swap_match.end():]
            )
        # else: silent skip — base format changed or SWAP TEST missing; log at
        # caller level so audit stays honest.

    # Optional: prepend thematic_note before first section heading
    if thematic_note:
        first_section_re = re.compile(r"^## Section 1:", re.MULTILINE)
        first_section = first_section_re.search(result)
        if first_section:
            insertion = "**Curator thematic emphasis:** " + thematic_note.strip() + "\n\n"
            result = (
                result[: first_section.start()] + insertion + result[first_section.start():]
            )

    return result


# ── runner ──────────────────────────────────────────────────────────────────

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

    for p in (voice_config_path, perp_path, gemini_path):
        if not p.exists():
            sys.exit(f"Missing input: {p}")
    # base_prompt_path: accept either the live path (fresh Jinja render) OR
    # the .base.md preserved copy (re-running tailor after a prior attempt).
    if not base_prompt_path.exists() and not base_preserved_path.exists():
        sys.exit(
            f"Missing base prompt. Expected {base_prompt_path.name} "
            f"(from Jinja render) or {base_preserved_path.name} (preserved "
            f"from prior tailor run) under "
            f"{base_prompt_path.parent.relative_to(project_root)}/"
        )

    voice_config = json.loads(voice_config_path.read_text())

    perp = json.loads(perp_path.read_text())
    perp_text = perp.get("text") or perp.get("text_clean", "")
    gem = json.loads(gemini_path.read_text())
    gem_text = gem.get("text", "")

    # Prefer the preserved base if it exists (re-run case); otherwise the live
    # path IS the base (fresh Jinja render). After we finish splicing, the
    # live path gets overwritten with the tailored result and .base.md always
    # holds the canonical base.
    if base_preserved_path.exists():
        base_prompt = base_preserved_path.read_text()
        stamp(f"  using preserved base from {base_preserved_path.name} "
              f"({len(base_prompt):,} chars)")
    else:
        base_prompt = base_prompt_path.read_text()
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
        "Produce the structured injections object + tailoring_notes[] per the "
        "Block 4 schema. JSON only — do NOT reproduce the base prompt."
    )

    stamp("  calling Opus 4.7 + adaptive thinking…")
    t0 = time.time()
    r = call_claude(
        system=system, user=user, model="claude-opus-4-7",
        max_tokens=16000, temperature=1.0, thinking=True,
        response_format_json=True,
    )
    wall = time.time() - t0
    stamp(f"  done in {wall:.1f}s — tokens in={r['usage']['input_tokens']} out={r['usage']['output_tokens']}")

    out = r["json"]

    # Validate response shape
    section_injections = out.get("section_injections")
    if not isinstance(section_injections, dict):
        sys.exit(
            f"Pass 0b tailor returned malformed section_injections "
            f"(got {type(section_injections).__name__}); "
            f"expected dict with keys '1'-'6'."
        )

    swap_test_anchor = out.get("swap_test_anchor")
    if swap_test_anchor is not None and not isinstance(swap_test_anchor, str):
        stamp(f"  WARN: swap_test_anchor is {type(swap_test_anchor).__name__}, expected str|null — dropping")
        swap_test_anchor = None
    if isinstance(swap_test_anchor, str) and not swap_test_anchor.strip():
        swap_test_anchor = None

    thematic_note = out.get("thematic_note")
    if thematic_note is not None and not isinstance(thematic_note, str):
        stamp(f"  WARN: thematic_note is {type(thematic_note).__name__}, expected str|null — dropping")
        thematic_note = None
    if isinstance(thematic_note, str) and not thematic_note.strip():
        thematic_note = None

    notes = out.get("tailoring_notes", [])
    if not isinstance(notes, list):
        stamp(f"  WARN: tailoring_notes is {type(notes).__name__}, expected list — coercing to []")
        notes = []

    # Splice — raises on malformed inputs; surfaces as clear error
    try:
        tailored = splice_injections(
            base_prompt=base_prompt,
            section_injections=section_injections,
            swap_test_anchor=swap_test_anchor,
            thematic_note=thematic_note,
        )
    except ValueError as e:
        sys.exit(f"Pass 0b tailor splice failed: {e}")

    # Post-splice sanity: result must contain no remaining placeholders and
    # must be larger than base (injections always ADD content).
    if _PLACEHOLDER_RE.search(tailored):
        sys.exit("Pass 0b tailor splice produced output with unreplaced placeholders")
    if len(tailored) < len(base_prompt):
        sys.exit(
            f"Pass 0b tailor splice produced shorter output than base "
            f"({len(tailored):,} vs {len(base_prompt):,}) — something is wrong"
        )

    tailored_prompt_path.write_text(tailored, encoding="utf-8")
    write_json_atomic(notes_path, {
        "voice_name": name, "voice_slug": slug,
        "tailoring_notes": notes,
        "model": r.get("model"),
        "usage": r["usage"],
        "splice_summary": {
            "base_chars": len(base_prompt),
            "tailored_chars": len(tailored),
            "added_chars": len(tailored) - len(base_prompt),
            "sections_injected": sorted(section_injections.keys()),
            "swap_test_anchor_applied": bool(swap_test_anchor),
            "thematic_note_applied": bool(thematic_note),
        },
    })

    stamp(f"  tailored prompt → {tailored_prompt_path.name} ({len(tailored):,} chars, "
          f"+{len(tailored) - len(base_prompt):,} vs base)")
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
