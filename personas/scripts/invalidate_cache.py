#!/usr/bin/env python3
"""invalidate_cache.py — Targeted cache invalidation for pipeline re-runs.

Empirical motivation: during Plato 2026-04-25 re-runs, manually deleting
cache files cost a re-run cycle when the operator (and Claude) targeted
04_generation/02_excerpt_selections.json instead of the actual path
03_corpus/02_excerpt_selections.json. `rm -f` failed silently, the
pipeline cache-hit, and the wider Pass 1d budget didn't apply.

This script knows the pipeline's path map and invalidates by pass name.

Usage:
    venv/bin/python scripts/invalidate_cache.py --voice plato \
        --project /path/to/project \
        --from-pass 1d
    venv/bin/python scripts/invalidate_cache.py --voice plato \
        --project /path/to/project \
        --pass 7a

`--pass <name>` invalidates ONLY that one pass's cache.
`--from-pass <name>` invalidates that pass and everything downstream of
it (recommended for re-runs after a prompt change or input change).
`--list` prints the path map without deleting anything.

Pass dependency order (downstream of each requires it to be re-fired):
    1a → 1b → 1c-extract → 1c → 1d → 2 → 3 → 4a → 4b → 5 → 6 → 6.5-clean
    → 7-pre → 7-anachronism → 7a → 7a-FIX → 7b → 7c → derive → assembled
    → chat
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO_ROOT))

from flows.shared import paths as _paths


# Ordered list: each pass + the file (or files) that, if absent, force re-fire.
# Ordering matters: invalidating "from-pass X" deletes all entries from X onward.
# Path-helper resolvers. Most map to flows.shared.paths functions; a few
# resolve to filenames not exposed as their own helper (chat artifact,
# fix log) and so use _composite_paths below.
def _composite_paths(slug: str, project_root: Path) -> dict[str, Path]:
    """Return the small set of paths that don't have their own helper
    function in flows.shared.paths."""
    return {
        "chat_system_prompt": _paths.derive_dir(slug, project_root) / "03_chat_system_prompt.json",
        "fix_log": _paths.merge_dir(slug, project_root) / "_fix_log.json",
    }


_PASS_ORDER: list[tuple[str, list[str]]] = [
    ("1a-perplexity", []),  # cached at 01_perplexity_dossier.json — typically not invalidated
    ("1b-gemini", []),       # cached at 02_gemini_broad_scan.json — typically not invalidated
    ("1c-extract", ["primary_text_urls"]),
    ("1c", ["primary_texts"]),
    ("1c-review", ["primary_texts_reviewed_flag"]),
    ("1d", ["excerpt_selections"]),
    ("2", ["pass_2", "ct_after_pass_2"]),
    ("3", ["pass_3", "ct_after_pass_3"]),
    ("4a", ["pass_4a", "ct_after_pass_4a"]),
    ("4b", ["pass_4b", "ct_after_pass_4b"]),
    ("5", ["pass_5"]),
    ("6", ["pass_6"]),
    ("7-pre", ["pass_7_pre"]),
    ("7-anachronism", ["pass_7_anachronism"]),
    ("7a", ["pass_7a"]),
    ("7a-fix", ["fix_log"]),  # composite path
    ("7b", ["pass_7b"]),
    ("7c", ["pass_7c"]),
    ("derive", ["derive_raw", "provocateur_profile", "evaluation_rubric",
                "chat_system_prompt"]),  # last is composite
    ("assembled", ["assembled_card", "manifest"]),
]


def _path_for(name: str, slug: str, project_root: Path) -> Path:
    """Resolve a path-helper name to a concrete path. First tries
    flows.shared.paths function; falls back to composite paths."""
    helper = getattr(_paths, name, None)
    if helper is not None:
        return helper(slug, project_root)
    composites = _composite_paths(slug, project_root)
    if name in composites:
        return composites[name]
    raise ValueError(f"Unknown path helper: {name!r}")


def _resolve_invalidation(slug: str, project_root: Path,
                          single_pass: str | None,
                          from_pass: str | None) -> list[Path]:
    """Build the list of paths to delete. `single_pass` invalidates one
    pass; `from_pass` invalidates that pass + everything downstream."""
    pass_names = [name for name, _ in _PASS_ORDER]
    targets: list[tuple[str, list[str]]] = []
    if single_pass:
        for name, helpers in _PASS_ORDER:
            if name == single_pass:
                targets.append((name, helpers))
                break
        else:
            raise ValueError(f"Unknown pass: {single_pass!r}. Known: {pass_names}")
    elif from_pass:
        try:
            start = pass_names.index(from_pass)
        except ValueError:
            raise ValueError(f"Unknown pass: {from_pass!r}. Known: {pass_names}")
        targets = _PASS_ORDER[start:]
    else:
        raise ValueError("Must specify either --pass or --from-pass")

    paths: list[Path] = []
    for _, helpers in targets:
        for helper in helpers:
            paths.append(_path_for(helper, slug, project_root))
    return paths


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--voice", required=False, help="voice slug (lower-case, e.g. 'plato')")
    parser.add_argument("--project", required=False, type=Path,
                        help="absolute path to project root (e.g. projects/phase-l-plato)")
    parser.add_argument("--pass", dest="single_pass",
                        help="invalidate one pass only (e.g. '1d', '7a')")
    parser.add_argument("--from-pass", dest="from_pass",
                        help="invalidate this pass + everything downstream (e.g. '1d')")
    parser.add_argument("--list", action="store_true",
                        help="print the path map without deleting anything")
    parser.add_argument("--dry-run", action="store_true",
                        help="show what would be deleted without deleting")
    args = parser.parse_args()

    if args.list:
        print("Pass dependency order (each downstream of the prior):")
        for name, helpers in _PASS_ORDER:
            print(f"  {name:18}  paths: {', '.join(helpers) or '(no cache)'}")
        return 0

    if not args.voice or not args.project:
        parser.error("--voice and --project are required (unless using --list)")

    if args.single_pass and args.from_pass:
        parser.error("specify only one of --pass / --from-pass")

    try:
        targets = _resolve_invalidation(args.voice, args.project,
                                        args.single_pass, args.from_pass)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    deleted = 0
    missing = 0
    for path in targets:
        if path.exists():
            if args.dry_run:
                print(f"  WOULD DELETE  {path}")
            else:
                if path.is_dir():
                    import shutil
                    shutil.rmtree(path)
                else:
                    path.unlink()
                print(f"  deleted  {path}")
            deleted += 1
        else:
            print(f"  (absent)  {path}")
            missing += 1

    action = "would delete" if args.dry_run else "deleted"
    print(f"\n{action} {deleted} file(s); {missing} were already absent")
    return 0


if __name__ == "__main__":
    sys.exit(main())
