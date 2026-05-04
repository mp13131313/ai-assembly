"""Reset a run_dir from a chosen stage onward — for replaying the pipeline
without re-uploading audio or re-running upstream work.

Operator workflow:

    # Re-run Provocateur → Voice → Editor → Publish (for example after
    # voice cards land + council_config gains the new voices):
    python scripts/reset_run.py <run_dir> --from-stage provocateur

    # Re-run only Editor → Publish (after editor closing-prompt iteration):
    python scripts/reset_run.py <run_dir> --from-stage editor

The script removes the relevant per-stage subtrees inside the run_dir AND
the corresponding per-night published_artifacts paths so the orchestrator's
sentinel checks (`02_researcher/grouping.json`, `04_voice/manifest.json`,
etc.) trip clean and the next overnight_orchestrator run picks the chosen
stage as the first to fire.

By default the script prints what it would delete and asks for confirmation.
Pass `--yes` to skip the prompt (useful in scripted retries).

Stages and what they own:

    transcription   01_transcription/<sid>/                       (kept by default — re-uploading audio is a separate operator action)
    researcher      02_researcher/                                  + published_artifacts/themes/night_<N>/
    provocateur     03_provocateur/                                 (no published surface — Editor reads from here directly)
    voice           04_voice/                                       + published_artifacts/nights/night_<N>/
    editor          05_editor/                                      + published_artifacts/dossiers/night_<N>/
    publish         (no run_dir subtree)                            + published_artifacts/extractions/, voices/, traces/lineage_graph_night_<N>.json

`--from-stage X` deletes EVERYTHING from stage X downward, since downstream
stages depend on upstream outputs being current. Idempotent — safe to run
twice; missing paths are skipped silently.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
_RUNTIME_DIR = _SCRIPT_DIR.parent
if str(_RUNTIME_DIR) not in sys.path:
    sys.path.insert(0, str(_RUNTIME_DIR))

from dotenv import load_dotenv  # noqa: E402

load_dotenv(_RUNTIME_DIR.parent / ".env", override=True)

from flows.shared.project_root import add_project_arg, resolve_project_root  # noqa: E402

# Order matters: deleting from stage X downward means deleting X and every
# stage that follows it.
_STAGE_ORDER = ("transcription", "researcher", "provocateur", "voice", "editor", "publish")


def _night_from_run_dir(run_dir: Path) -> int | None:
    """Parse `athens_night_<N>` to grab the night number; None if the
    folder name doesn't match. Used to compute per-night published paths."""
    m = re.match(r"athens_night_(\d+)$", run_dir.name)
    return int(m.group(1)) if m else None


def _paths_for_stage(
    stage: str,
    run_dir: Path,
    project_root: Path,
    night: int | None,
) -> list[Path]:
    """All filesystem paths owned by a stage. Per-night published paths
    only included when the run_dir's night number is parseable."""
    out: list[Path] = []
    if stage == "transcription":
        out.append(run_dir / "01_transcription")
    elif stage == "researcher":
        out.append(run_dir / "02_researcher")
        if night is not None:
            out.append(project_root / "published_artifacts" / "themes" / f"night_{night}")
    elif stage == "provocateur":
        out.append(run_dir / "03_provocateur")
    elif stage == "voice":
        out.append(run_dir / "04_voice")
        if night is not None:
            out.append(project_root / "published_artifacts" / "nights" / f"night_{night}")
    elif stage == "editor":
        out.append(run_dir / "05_editor")
        if night is not None:
            out.append(project_root / "published_artifacts" / "dossiers" / f"night_{night}")
    elif stage == "publish":
        # publish_flow writes to several locations; clear the per-night
        # surfaces (cross-night indexes get rebuilt on next publish run).
        out.append(project_root / "published_artifacts" / "extractions")
        out.append(project_root / "published_artifacts" / "voices")
        if night is not None:
            out.append(
                project_root / "published_artifacts" / "traces"
                / f"lineage_graph_night_{night}.json"
            )
            out.append(
                project_root / "published_artifacts" / "traces"
                / f"publish_manifest_night_{night}.json"
            )
        # Cross-night dossier index: rebuilt on next publish run, but
        # delete the stale copy so partial state doesn't survive.
        out.append(project_root / "published_artifacts" / "dossiers" / "_index.json")
    return out


def _stages_from(start_stage: str) -> list[str]:
    if start_stage not in _STAGE_ORDER:
        raise ValueError(
            f"Unknown stage: {start_stage}. "
            f"Valid: {', '.join(_STAGE_ORDER)}"
        )
    idx = _STAGE_ORDER.index(start_stage)
    return list(_STAGE_ORDER[idx:])


def collect_paths_to_delete(
    run_dir: Path,
    project_root: Path,
    from_stage: str,
    *,
    include_transcription: bool = False,
) -> list[Path]:
    """Build the full list of paths to delete for a `--from-stage X` reset.

    `include_transcription` kept off by default: re-uploading audio is a
    separate operator action; reset shouldn't blow away transcribed
    sessions unless explicitly asked.
    """
    night = _night_from_run_dir(run_dir)
    stages = _stages_from(from_stage)
    if not include_transcription and "transcription" in stages:
        stages = [s for s in stages if s != "transcription"]
    paths: list[Path] = []
    for stage in stages:
        paths.extend(_paths_for_stage(stage, run_dir, project_root, night))
    # Existing-only — drop paths that already don't exist so the dry-run
    # output reflects what'll actually change.
    return [p for p in paths if p.exists()]


def _human_size(p: Path) -> str:
    if p.is_dir():
        n = sum(1 for _ in p.rglob("*"))
        return f"{n} entries"
    try:
        return f"{p.stat().st_size:,} bytes"
    except OSError:
        return "?"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Reset a run_dir from a chosen stage onward."
    )
    parser.add_argument("run_dir", help="Run directory (e.g. <PROJECT_ROOT>/runs/athens_night_1)")
    parser.add_argument(
        "--from-stage",
        required=True,
        choices=_STAGE_ORDER,
        help="Earliest stage to reset; downstream stages also reset.",
    )
    parser.add_argument(
        "--include-transcription",
        action="store_true",
        help="Include 01_transcription/ when resetting from `transcription` stage. "
             "Off by default — re-uploading audio is a separate operator action.",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Skip the confirmation prompt. Use in scripted retries.",
    )
    add_project_arg(parser)
    args = parser.parse_args()

    project_root = resolve_project_root(args.project)
    run_dir = Path(args.run_dir)
    if not run_dir.exists():
        sys.stderr.write(f"run_dir does not exist: {run_dir}\n")
        return 2

    paths = collect_paths_to_delete(
        run_dir, project_root, args.from_stage,
        include_transcription=args.include_transcription,
    )
    if not paths:
        print(f"Nothing to delete from stage `{args.from_stage}` onward; already clean.")
        return 0

    print(f"Reset plan (from stage `{args.from_stage}`):")
    print(f"  run_dir:      {run_dir}")
    print(f"  project_root: {project_root}")
    print()
    print("Will delete:")
    for p in paths:
        rel = p
        try:
            rel = p.relative_to(project_root)
        except ValueError:
            pass
        kind = "dir" if p.is_dir() else "file"
        print(f"  - [{kind}] {rel}  ({_human_size(p)})")
    print()

    if not args.yes:
        try:
            answer = input("Proceed with deletion? [y/N] ").strip().lower()
        except EOFError:
            answer = ""
        if answer not in ("y", "yes"):
            print("Aborted.")
            return 1

    for p in paths:
        if p.is_dir():
            shutil.rmtree(p)
        else:
            p.unlink()
        print(f"  deleted: {p}")

    print()
    print(f"Reset complete. Re-run with: overnight_orchestrator.py --night N --once")
    return 0


if __name__ == "__main__":
    sys.exit(main())
