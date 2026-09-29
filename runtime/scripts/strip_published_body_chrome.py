"""Strip the stray `**` from already-published dossier bodies (C64 residual).

Before C64 (`9f415dd`), the editor's body parser left the closing `**` of the
prompt's `**body_paragraphs:**` label in the body, so `body_paragraphs[0]`
of every published dossier starts with "**\\n". The parser is fixed; this
rewrites the dossiers already on disk to what the fixed code emits, without
re-running any LLM stage. Only a leading "**" line on the first paragraph is
removed; every other byte of content is unchanged.

Scope: `published_artifacts/dossiers/night_*/dossier_*.json`. The run-dir
copies under `runs/` are the making-of record and are left alone. Afterwards
rebuild `published_artifacts/data_views/` with build_athens_data_graph.py
(it embeds the bodies).

Dry run by default:
    python scripts/strip_published_body_chrome.py --project <PROJECT_ROOT>
    python scripts/strip_published_body_chrome.py --project <PROJECT_ROOT> --apply
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

_RUNTIME = Path(__file__).resolve().parent.parent
if str(_RUNTIME) not in sys.path:
    sys.path.insert(0, str(_RUNTIME))

from flows.shared.io import write_json_atomic  # noqa: E402

_LEADING_CHROME = re.compile(r"^\*\*[ \t]*\n")


def strip_body(dossier: dict) -> bool:
    """Remove a leading "**" line from body_paragraphs[0]. True if changed."""
    body = dossier.get("body_paragraphs")
    if not body or not isinstance(body[0], str) or not _LEADING_CHROME.match(body[0]):
        return False
    first = _LEADING_CHROME.sub("", body[0], count=1)
    dossier["body_paragraphs"] = ([first] if first.strip() else []) + body[1:]
    return True


def run(project_root: Path, apply: bool) -> list[Path]:
    """Return the dossier files that need (or, with apply, got) the fix."""
    changed = []
    for f in sorted((project_root / "published_artifacts" / "dossiers").glob("night_*/dossier_*.json")):
        data = json.loads(f.read_text(encoding="utf-8"))
        if strip_body(data):
            changed.append(f)
            if apply:
                write_json_atomic(f, data)
    return changed


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--project", type=Path, required=True, help="PROJECT_ROOT (e.g. athens-2026)")
    ap.add_argument("--apply", action="store_true", help="write changes (default: dry run)")
    args = ap.parse_args()
    changed = run(args.project, args.apply)
    verb = "stripped" if args.apply else "would strip"
    for f in changed:
        print(f"  {verb}: {f.relative_to(args.project)}")
    print(f"{len(changed)} dossier(s) {verb}." + ("" if args.apply else " Dry run — pass --apply to write."))


if __name__ == "__main__":
    main()
