"""One-shot migration from flat layout to per-voice-folder layout.

Old paths (per-voice — migrate these):
  $PROJECT_ROOT/inputs/voices/<slug>.json
  $PROJECT_ROOT/inputs/voices/<slug>_pass0a_review.md
  $PROJECT_ROOT/inputs/non_human_grounding/<slug>.md
  $PROJECT_ROOT/inputs/dossiers/<slug>_claude_dr.md
  $PROJECT_ROOT/inputs/dossiers/_dr_prompts/<slug>_dr_prompt.md
  $PROJECT_ROOT/inputs/dossiers/_dr_prompts/<slug>_dr_prompt.base.md
  $PROJECT_ROOT/inputs/dossiers/_dr_prompts/<slug>_tailoring_notes.json
  $PROJECT_ROOT/runs/<slug>/01_research/perplexity_dossier.json
  $PROJECT_ROOT/runs/<slug>/01_research/gemini_broad_scan.json
  $PROJECT_ROOT/runs/<slug>/01_research/claude_dr_dossier.md
  $PROJECT_ROOT/runs/<slug>/01_research/primary_texts.json
  $PROJECT_ROOT/runs/<slug>/01_research/excerpt_selections.json
  $PROJECT_ROOT/runs/<slug>/02_passes/pass_2_identity_boundaries.json
  $PROJECT_ROOT/runs/<slug>/02_passes/pass_3_intellectual_core.json
  $PROJECT_ROOT/runs/<slug>/02_passes/pass_4a_voice.json
  $PROJECT_ROOT/runs/<slug>/02_passes/pass_4b_artifact.json
  $PROJECT_ROOT/runs/<slug>/02_passes/pass_5_engagement.json
  $PROJECT_ROOT/runs/<slug>/02_passes/pass_6_corpus.json
  $PROJECT_ROOT/runs/<slug>/02_passes/_ct_pass*.json
  $PROJECT_ROOT/runs/<slug>/02_passes/pass_7pre_citation.json
  $PROJECT_ROOT/runs/<slug>/02_passes/pass_7_anachronism.json
  $PROJECT_ROOT/runs/<slug>/02_passes/pass_7a.json
  $PROJECT_ROOT/runs/<slug>/02_passes/pass_7b.json
  $PROJECT_ROOT/runs/<slug>/02_passes/pass_7c.json
  $PROJECT_ROOT/runs/<slug>/02_passes/derive.json
  $PROJECT_ROOT/runs/<slug>/persona_card_assembled.json
  $PROJECT_ROOT/runs/<slug>/provocateur_profile.json
  $PROJECT_ROOT/runs/<slug>/evaluation_rubric.json

Old paths (project-level shared — move from inputs/ to project root):
  $PROJECT_ROOT/inputs/conference_facts.json    → $PROJECT_ROOT/conference_facts.json
  $PROJECT_ROOT/inputs/audience_profile.json    → $PROJECT_ROOT/audience_profile.json
  $PROJECT_ROOT/inputs/panel_roster.json        → $PROJECT_ROOT/panel_roster.json

New paths (per-voice under voices/<slug>/):
  voices/<slug>/00_intake/01_non_human_grounding.md
  voices/<slug>/00_intake/02_voice_config.json
  voices/<slug>/00_intake/03_review_doc.md
  voices/<slug>/01_research/01_perplexity_dossier.json
  voices/<slug>/01_research/02_gemini_broad_scan.json
  voices/<slug>/01_research/03_dr_prompts/01_monolithic_dr_prompt.md
  voices/<slug>/01_research/03_dr_prompts/01_monolithic_dr_prompt.base.md
  voices/<slug>/01_research/03_dr_prompts/02_tailoring_notes.json
  voices/<slug>/01_research/04_dr_dossier/07_concat_claude_dr.md
  voices/<slug>/03_corpus/01_primary_texts.json
  voices/<slug>/03_corpus/02_excerpt_selections.json
  voices/<slug>/04_generation/01_pass_2_identity_boundaries.json
  voices/<slug>/04_generation/03_pass_3_intellectual_core.json
  voices/<slug>/04_generation/05_pass_4a_voice.json
  voices/<slug>/04_generation/07_pass_4b_artifact.json
  voices/<slug>/04_generation/09_pass_5_engagement.json
  voices/<slug>/04_generation/10_pass_6_corpus.json
  voices/<slug>/05_validation/01_pass_7_pre_citation.json
  voices/<slug>/05_validation/02_pass_7_anachronism.json
  voices/<slug>/05_validation/03_pass_7a_cross_model.json
  voices/<slug>/05_validation/04_pass_7b_smoke_test.json
  voices/<slug>/05_validation/05_pass_7c_negative.json
  voices/<slug>/06_derive/01_provocateur_profile.json
  voices/<slug>/06_derive/02_evaluation_rubric.json
  voices/<slug>/07_persona_card_assembled.json

Script behaviour:
- Discovers voice slugs by scanning inputs/voices/*.json + runs/*/
- --dry-run: prints moves without executing
- Idempotent: skips if source missing or destination already exists
- Emits _migration_manifest.json at project root with full move log
- Reports empty old dirs at end (does NOT delete them)

Usage:
    python3 scripts/migrate_to_per_voice_layout.py --project /path/to/project
    python3 scripts/migrate_to_per_voice_layout.py --project /path/to/project --dry-run
    python3 scripts/migrate_to_per_voice_layout.py --project /path/to/project --slug fyodor_dostoevsky
"""
from __future__ import annotations

import argparse
import datetime
import json
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from flows.shared.project_root import add_project_arg, resolve_project_root


def _discover_slugs(project_root: Path) -> set[str]:
    """Return all voice slugs found in inputs/voices/ and runs/."""
    slugs: set[str] = set()
    voices_dir = project_root / "inputs" / "voices"
    if voices_dir.is_dir():
        for f in voices_dir.glob("*.json"):
            name = f.stem
            if not name.startswith("_"):
                slugs.add(name)
    runs_dir = project_root / "runs"
    if runs_dir.is_dir():
        for d in runs_dir.iterdir():
            if d.is_dir() and not d.name.startswith("_") and not d.name.startswith("."):
                slugs.add(d.name)
    return slugs


def _per_voice_moves(slug: str, project_root: Path) -> list[tuple[Path, Path]]:
    """Return list of (source, destination) pairs for a single voice slug."""
    inp = project_root / "inputs"
    run = project_root / "runs" / slug
    v = project_root / "voices" / slug

    moves: list[tuple[Path, Path]] = [
        # 00_intake
        (inp / "non_human_grounding" / f"{slug}.md",           v / "00_intake" / "01_non_human_grounding.md"),
        (inp / "voices" / f"{slug}.json",                       v / "00_intake" / "02_voice_config.json"),
        (inp / "voices" / f"{slug}_pass0a_review.md",           v / "00_intake" / "03_review_doc.md"),
        # 01_research
        (run / "01_research" / "perplexity_dossier.json",       v / "01_research" / "01_perplexity_dossier.json"),
        (run / "01_research" / "gemini_broad_scan.json",        v / "01_research" / "02_gemini_broad_scan.json"),
        # 03_dr_prompts
        (inp / "dossiers" / "_dr_prompts" / f"{slug}_dr_prompt.md",
         v / "01_research" / "03_dr_prompts" / "01_monolithic_dr_prompt.md"),
        (inp / "dossiers" / "_dr_prompts" / f"{slug}_dr_prompt.base.md",
         v / "01_research" / "03_dr_prompts" / "01_monolithic_dr_prompt.base.md"),
        (inp / "dossiers" / "_dr_prompts" / f"{slug}_tailoring_notes.json",
         v / "01_research" / "03_dr_prompts" / "02_tailoring_notes.json"),
        # 04_dr_dossier (two possible old paths that map to concat)
        (inp / "dossiers" / f"{slug}_claude_dr.md",             v / "01_research" / "04_dr_dossier" / "07_concat_claude_dr.md"),
        (run / "01_research" / "claude_dr_dossier.md",          v / "01_research" / "04_dr_dossier" / "07_concat_claude_dr.md"),
        # 03_corpus
        (run / "01_research" / "primary_texts.json",            v / "03_corpus" / "01_primary_texts.json"),
        (run / "01_research" / "excerpt_selections.json",        v / "03_corpus" / "02_excerpt_selections.json"),
        # 04_generation (Pass 2–6)
        (run / "02_passes" / "pass_2_identity_boundaries.json", v / "04_generation" / "01_pass_2_identity_boundaries.json"),
        (run / "02_passes" / "pass_3_intellectual_core.json",   v / "04_generation" / "03_pass_3_intellectual_core.json"),
        (run / "02_passes" / "pass_4a_voice.json",              v / "04_generation" / "05_pass_4a_voice.json"),
        (run / "02_passes" / "pass_4b_artifact.json",           v / "04_generation" / "07_pass_4b_artifact.json"),
        (run / "02_passes" / "pass_5_engagement.json",          v / "04_generation" / "09_pass_5_engagement.json"),
        (run / "02_passes" / "pass_6_corpus.json",              v / "04_generation" / "10_pass_6_corpus.json"),
        # 05_validation (Pass 7.*)
        (run / "02_passes" / "pass_7pre_citation.json",         v / "05_validation" / "01_pass_7_pre_citation.json"),
        (run / "02_passes" / "pass_7_anachronism.json",         v / "05_validation" / "02_pass_7_anachronism.json"),
        (run / "02_passes" / "pass_7a.json",                    v / "05_validation" / "03_pass_7a_cross_model.json"),
        (run / "02_passes" / "pass_7b.json",                    v / "05_validation" / "04_pass_7b_smoke_test.json"),
        (run / "02_passes" / "pass_7c.json",                    v / "05_validation" / "05_pass_7c_negative.json"),
        # 06_derive (derive.json splits into two; provocateur_profile + evaluation_rubric may exist separately)
        (run / "runs" / slug / "provocateur_profile.json",      v / "06_derive" / "01_provocateur_profile.json"),
        (run / "provocateur_profile.json",                       v / "06_derive" / "01_provocateur_profile.json"),
        (run / "evaluation_rubric.json",                         v / "06_derive" / "02_evaluation_rubric.json"),
        # 07_persona_card_assembled.json
        (run / "persona_card_assembled.json",                    v / "07_persona_card_assembled.json"),
    ]

    # CT files (wildcard — _ct_pass*.json in 02_passes/)
    passes_dir = run / "02_passes"
    if passes_dir.is_dir():
        for ct_file in sorted(passes_dir.glob("_ct_pass*.json")):
            moves.append((ct_file, v / "04_generation" / ct_file.name))

    return moves


def _project_level_moves(project_root: Path) -> list[tuple[Path, Path]]:
    """Files under inputs/ that should move up to project root."""
    inp = project_root / "inputs"
    return [
        (inp / "conference_facts.json", project_root / "conference_facts.json"),
        (inp / "audience_profile.json", project_root / "audience_profile.json"),
        (inp / "panel_roster.json",     project_root / "panel_roster.json"),
    ]


def _derive_split_move(slug: str, project_root: Path) -> list[tuple[Path, Path, str]]:
    """Handle derive.json split: if it exists and neither target exists, split."""
    run = project_root / "runs" / slug
    derive_path = run / "02_passes" / "derive.json"
    v = project_root / "voices" / slug
    prov_target = v / "06_derive" / "01_provocateur_profile.json"
    eval_target = v / "06_derive" / "02_evaluation_rubric.json"
    return [(derive_path, prov_target, eval_target)]


def migrate(
    project_root: Path,
    slugs: set[str] | None = None,
    dry_run: bool = False,
) -> dict:
    """Run migration. Returns manifest dict."""
    manifest: dict = {
        "timestamp": datetime.datetime.now().isoformat(),
        "project_root": str(project_root),
        "dry_run": dry_run,
        "moves": [],
        "skipped": [],
        "errors": [],
    }

    if slugs is None:
        slugs = _discover_slugs(project_root)

    print(f"{'[DRY RUN] ' if dry_run else ''}Migrating {len(slugs)} voice(s): {sorted(slugs)}")

    # --- Per-voice moves ---
    for slug in sorted(slugs):
        print(f"\n  Voice: {slug}")
        moves = _per_voice_moves(slug, project_root)

        for src, dst in moves:
            _do_move(src, dst, manifest, dry_run, slug=slug)

        # derive.json split (read-only: parse JSON, write two targets)
        run = project_root / "runs" / slug
        derive_path = run / "02_passes" / "derive.json"
        v = project_root / "voices" / slug
        if derive_path.exists():
            prov_target = v / "06_derive" / "01_provocateur_profile.json"
            eval_target = v / "06_derive" / "02_evaluation_rubric.json"
            _do_derive_split(derive_path, prov_target, eval_target, manifest, dry_run, slug=slug)

    # --- Project-level moves ---
    print("\n  Project-level files:")
    for src, dst in _project_level_moves(project_root):
        _do_move(src, dst, manifest, dry_run, slug="(project-level)")

    # --- Report empty old dirs ---
    _report_empty_dirs(project_root, manifest)

    return manifest


def _do_move(
    src: Path,
    dst: Path,
    manifest: dict,
    dry_run: bool,
    slug: str,
) -> None:
    entry = {"slug": slug, "src": str(src), "dst": str(dst)}
    if not src.exists():
        return  # silently skip missing source
    if dst.exists():
        manifest["skipped"].append({**entry, "reason": "destination_exists"})
        print(f"    SKIP  {src.name} → {dst.relative_to(dst.parent.parent.parent.parent.parent) if dst.parts else dst.name}  (dest exists)")
        return
    print(f"    {'WOULD MOVE' if dry_run else 'MOVE'} {src.name}")
    print(f"           → {dst}")
    if not dry_run:
        try:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dst))
            entry["status"] = "moved"
        except Exception as exc:
            entry["status"] = "error"
            entry["error"] = str(exc)
            manifest["errors"].append(entry)
            print(f"    ERROR  {exc}")
            return
    else:
        entry["status"] = "dry_run"
    manifest["moves"].append(entry)


def _do_derive_split(
    derive_path: Path,
    prov_target: Path,
    eval_target: Path,
    manifest: dict,
    dry_run: bool,
    slug: str,
) -> None:
    try:
        data = json.loads(derive_path.read_text(encoding="utf-8"))
    except Exception as exc:
        manifest["errors"].append({"slug": slug, "src": str(derive_path), "error": str(exc)})
        return

    prov_data = data.get("provocateur_profile") or data
    eval_data = data.get("evaluation_rubric")

    for target, content, label in [
        (prov_target, prov_data, "provocateur_profile"),
        (eval_target, eval_data, "evaluation_rubric"),
    ]:
        if content is None:
            print(f"    SKIP  derive.json → {label}  (key missing)")
            continue
        if target.exists():
            print(f"    SKIP  derive.json → {label}  (dest exists)")
            manifest["skipped"].append({"slug": slug, "src": str(derive_path), "dst": str(target), "reason": "destination_exists"})
            continue
        print(f"    {'WOULD SPLIT' if dry_run else 'SPLIT'} derive.json → {target.name}")
        if not dry_run:
            try:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(json.dumps(content, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
                manifest["moves"].append({"slug": slug, "src": str(derive_path), "dst": str(target), "status": "split_written"})
            except Exception as exc:
                manifest["errors"].append({"slug": slug, "src": str(derive_path), "dst": str(target), "error": str(exc)})
        else:
            manifest["moves"].append({"slug": slug, "src": str(derive_path), "dst": str(target), "status": "dry_run"})


def _report_empty_dirs(project_root: Path, manifest: dict) -> None:
    """Find and report old layout dirs that are now empty (after moves)."""
    candidate_dirs = [
        project_root / "inputs" / "voices",
        project_root / "inputs" / "dossiers" / "_dr_prompts",
        project_root / "inputs" / "dossiers",
        project_root / "inputs" / "non_human_grounding",
        project_root / "inputs",
    ]
    runs_dir = project_root / "runs"
    if runs_dir.is_dir():
        for slug_dir in sorted(runs_dir.iterdir()):
            if slug_dir.is_dir():
                candidate_dirs.extend([
                    slug_dir / "02_passes",
                    slug_dir / "01_research",
                    slug_dir,
                ])

    empty: list[str] = []
    for d in candidate_dirs:
        if d.is_dir():
            non_hidden = [f for f in d.iterdir() if not f.name.startswith(".")]
            if not non_hidden:
                empty.append(str(d))

    if empty:
        print(f"\n  Empty old dirs (safe to remove manually):")
        for d in empty:
            print(f"    {d}")
    manifest["empty_old_dirs"] = empty


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    add_project_arg(parser)
    parser.add_argument("--dry-run", action="store_true", help="Print moves without executing")
    parser.add_argument("--slug", help="Migrate only this voice slug (default: all)")
    args = parser.parse_args()

    project_root = resolve_project_root(args.project, repo_root=REPO_ROOT)
    slugs = {args.slug} if args.slug else None

    manifest = migrate(project_root, slugs=slugs, dry_run=args.dry_run)

    moves_done = sum(1 for m in manifest["moves"] if m.get("status") == "moved")
    splits_done = sum(1 for m in manifest["moves"] if m.get("status") == "split_written")
    skipped = len(manifest["skipped"])
    errors = len(manifest["errors"])

    print(f"\n{'[DRY RUN] ' if args.dry_run else ''}Summary: "
          f"{moves_done} moved, {splits_done} split-written, "
          f"{skipped} skipped, {errors} errors")

    if not args.dry_run:
        manifest_path = project_root / "_migration_manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"Manifest written to: {manifest_path}")

    if errors:
        print(f"\nERRORS ({errors}):")
        for e in manifest["errors"]:
            print(f"  {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
