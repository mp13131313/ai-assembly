"""Restamp corrupted `voice_name` fields in already-published artifacts (C53).

Before the C53 fix, published per-voice pages, night indexes, dossier
headnotes and the dossier-index `voices_routed` carried each voice's
`council_member` — the long card identity opening ("I am Augusta Ada King…")
— as its display name. The code now resolves names from council_config;
this rewrites the fields already on disk to what the fixed code emits,
without re-running any LLM stage:

  - dossier headnotes (value starts "the Voice of ")  ->  "the " + name
  - everything else                                    ->  name
  where name = the council_config `name` for the slug, verbatim
  ("Voice of X" / "Voice of the X").

Only dicts carrying both `voice_slug` and `voice_name` are touched; every
other byte of content is unchanged.

Also repairs the C50 symptom still in the record: a per-night voice index
(`nights/night_N/_index.json`) that lists fewer voices than the page files
on disk is rebuilt from disk with the fixed `_rebuild_index_from_disk`
(after the pages are restamped, so it picks up the corrected names).
Complete indexes are left alone. Skips `_archive/` (historical record)
and `data_views/` (derived — rebuild it afterwards with
build_athens_data_graph.py).

Dry run by default:
    python scripts/restamp_published_voice_names.py --project <PROJECT_ROOT>
    python scripts/restamp_published_voice_names.py --project <PROJECT_ROOT> --apply
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_RUNTIME = Path(__file__).resolve().parent.parent
if str(_RUNTIME) not in sys.path:
    sys.path.insert(0, str(_RUNTIME))

from flows.shared.io import (  # noqa: E402
    load_council_name_by_slug,
    voice_display_name,
    write_json_atomic,
)
from flows.voice.publish import _rebuild_index_from_disk  # noqa: E402

SKIP_DIRS = {"_archive", "data_views"}


def _restamp(node, project_root: Path, changes: list, path: str = "$") -> None:
    if isinstance(node, dict):
        slug, old = node.get("voice_slug"), node.get("voice_name")
        if isinstance(slug, str) and slug and isinstance(old, str):
            name = voice_display_name(slug, project_root)
            new = "the " + name if old.startswith("the Voice of ") else name
            if new != old:
                changes.append((path, slug, old, new))
                node["voice_name"] = new
        for k, v in node.items():
            _restamp(v, project_root, changes, f"{path}.{k}")
    elif isinstance(node, list):
        for i, v in enumerate(node):
            _restamp(v, project_root, changes, f"{path}[{i}]")


def _incomplete_night_indexes(base: Path) -> list[tuple[Path, int, int, int]]:
    """(night_dir, night, listed, on_disk) for voice indexes missing pages."""
    out = []
    for d in sorted((base / "nights").glob("night_*")):
        suffix = d.name.split("_", 1)[1]
        if not suffix.isdigit():
            continue
        pages = {p.stem for p in d.glob("*.json") if p.name != "_index.json"}
        try:
            index = json.loads((d / "_index.json").read_text(encoding="utf-8"))
            listed = {v.get("voice_slug") for v in index.get("voices", [])}
        except (OSError, json.JSONDecodeError):
            listed = set()
        if pages and listed != pages:
            out.append((d, int(suffix), len(listed & pages), len(pages)))
    return out


def restamp(project_root: Path, apply: bool = False) -> int:
    """Return the number of fields changed (or that would change)."""
    if not (project_root / "council_config.json").exists():
        sys.exit(f"No council_config.json at {project_root} — refusing: "
                 f"names would fall back to slug-derived guesses.")
    known = load_council_name_by_slug(project_root)
    base = project_root / "published_artifacts"

    plan: list[tuple[Path, dict, list]] = []
    unresolved: set[str] = set()
    for f in sorted(base.rglob("*.json")):
        if SKIP_DIRS & set(f.relative_to(base).parts):
            continue
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            print(f"  skip (unreadable): {f.relative_to(project_root)} — {e}")
            continue
        changes: list = []
        _restamp(data, project_root, changes)
        if changes:
            plan.append((f, data, changes))
            unresolved |= {slug for _, slug, _, _ in changes if slug not in known}

    total = sum(len(c) for _, _, c in plan)
    for f, _, changes in plan:
        print(f"{f.relative_to(project_root)}: {len(changes)}")
        for path, _, old, new in changes:
            print(f"    {path}: {old[:50]!r} -> {new!r}")

    incomplete = _incomplete_night_indexes(base)
    for d, _, listed, on_disk in incomplete:
        print(f"{(d / '_index.json').relative_to(project_root)}: lists {listed} "
              f"of {on_disk} voice pages -> rebuild from disk")

    if unresolved:
        sys.exit(f"Slugs not in council_config.json: {sorted(unresolved)} — "
                 f"refusing to write fallback names. Fix council_config first.")
    if apply:
        for f, data, _ in plan:
            write_json_atomic(f, data)
        for d, night, _, _ in incomplete:
            write_json_atomic(d / "_index.json", _rebuild_index_from_disk(d, night))
        print(f"\n{total} field(s) rewritten in {len(plan)} file(s); "
              f"{len(incomplete)} night index(es) rebuilt.")
        if total:
            print("Next: re-run scripts/build_athens_data_graph.py to regenerate "
                  "data_views/, then review `git diff` in the project repo.")
    else:
        print(f"\n{total} field(s) in {len(plan)} file(s) would change; "
              f"{len(incomplete)} night index(es) would be rebuilt "
              f"(dry run — pass --apply to write).")
    return total


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--project", type=Path, required=True,
                    help="PROJECT_ROOT (contains council_config.json + published_artifacts/)")
    ap.add_argument("--apply", action="store_true", help="write changes (default: dry run)")
    args = ap.parse_args()
    restamp(args.project.resolve(), apply=args.apply)


if __name__ == "__main__":
    main()
