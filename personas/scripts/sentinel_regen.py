#!/usr/bin/env python3
"""sentinel_regen.py — FU#29 narrow: prompt-touch sentinel regen for variance management.

When a Pass 2-6 prompt changes (or any other shared prompt under
flows/shared/prompts/), regenerate just that pass for a few sentinel voices
and diff the result against the shipped version. Catches silent regressions
before they reach the whole panel. This is the Stage 4 quality gate
(roadmap Phase 1.1: one prompt change at a time, each behind a sentinel regen).

A regen re-runs the persona pipeline and makes real API calls, so it always
runs in a SANDBOX copy of the voices, never in a production project:

    # 1. Copy the sentinel voices (plus the project-level JSON) into a sandbox:
    venv/bin/python scripts/sentinel_regen.py sandbox \\
        --from "/Users/aienvironment/Desktop/AI Assembly/projects/athens-2026" \\
        --to   "/Users/aienvironment/Desktop/AI Assembly/projects/current-tests/sentinel-sandbox" \\
        --voices plato,fyodor_dostoevsky

    # 2. Which passes do the changed prompts affect?
    venv/bin/python scripts/sentinel_regen.py detect [--since <git ref>]

    # 3. Regenerate one pass in the sandbox; diff against the shipped original:
    venv/bin/python scripts/sentinel_regen.py regen --pass 4a \\
        --project "/Users/aienvironment/Desktop/AI Assembly/projects/current-tests/sentinel-sandbox" \\
        --baseline-project "/Users/aienvironment/Desktop/AI Assembly/projects/athens-2026" \\
        --voices plato,fyodor_dostoevsky

    venv/bin/python scripts/sentinel_regen.py list-prompts

`regen` refuses a project that is its own git repository (athens-2026 is),
so it can't overwrite production cards by accident; `--allow-git-project`
overrides. Cost (pre-Athens estimate): ~$3-5 per pass per two voices.

Prompt → pass mapping (which prompt files affect which pass output):

    Pass 2  ← persona_pass_2_identity_boundaries.md, persona_pass_2_user.md
    Pass 3  ← persona_pass_3_intellectual_core.md, persona_pass_3_user.md
    Pass 4a ← persona_pass_4a_voice.md, persona_pass_4a_user.md
    Pass 4b ← persona_pass_4b_artifact.md, persona_pass_4b_user.md
    Pass 5  ← persona_pass_5_engagement.md, persona_pass_5_user.md
    Pass 6  ← persona_pass_6_corpus.md, persona_pass_6_user.md

Default sentinels: Plato (philosophical) + Fyodor Dostoevsky (narratival);
any voice present in the project can be named with --voices.

Architecture: this is the NARROW version of FU#29 (prompt-touch detection
only). The BROAD version — detecting any pipeline-code change and
performing impact analysis — is post-Athens architectural work. See
FOLLOW_UPS.md FU#29 for context. Repaired 2026-09-28 (voices OPEN_ITEMS §37
A5): the old defaults pointed at archived project folders and it had no
--project.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]

_DEFAULT_VOICES = "plato,fyodor_dostoevsky"

# Prompt → pass mapping. Edit as new passes / prompts land.
_PROMPT_TO_PASS: dict[str, str] = {
    "persona_pass_2_identity_boundaries.md": "2",
    "persona_pass_2_user.md": "2",
    "persona_pass_3_intellectual_core.md": "3",
    "persona_pass_3_user.md": "3",
    "persona_pass_4a_voice.md": "4a",
    "persona_pass_4a_user.md": "4a",
    "persona_pass_4b_artifact.md": "4b",
    "persona_pass_4b_user.md": "4b",
    "persona_pass_5_engagement.md": "5",
    "persona_pass_5_user.md": "5",
    "persona_pass_6_corpus.md": "6",
    "persona_pass_6_user.md": "6",
}


def _git_changed_prompts(since: str | None = None) -> list[str]:
    """Return list of prompt-file names that have changed since the
    specified ref (or working-tree changes if no ref). Filenames returned
    are basenames matching _PROMPT_TO_PASS keys."""
    if since:
        cmd = ["git", "diff", "--name-only", since, "--", "personas/flows/shared/prompts/"]
    else:
        cmd = ["git", "diff", "--name-only", "personas/flows/shared/prompts/"]
    try:
        out = subprocess.check_output(cmd, cwd=_REPO_ROOT.parent, text=True).strip()
    except subprocess.CalledProcessError:
        return []
    if not out:
        return []
    changed = [Path(p).name for p in out.splitlines() if p.strip()]
    return [p for p in changed if p in _PROMPT_TO_PASS]


def _detect_passes(changed_prompts: list[str]) -> set[str]:
    """Map changed prompt filenames to affected passes."""
    return {_PROMPT_TO_PASS[p] for p in changed_prompts if p in _PROMPT_TO_PASS}


def _voices(arg: str) -> list[str]:
    return [v.strip() for v in arg.split(",") if v.strip()]


def check_project(project_root: Path, slugs: list[str], allow_git_project: bool = False) -> None:
    """Refuse to regenerate anywhere that looks like production, or where a
    voice is missing. Raises SystemExit with a clear message."""
    if not project_root.is_dir():
        raise SystemExit(f"Project root does not exist: {project_root}")
    if (project_root / ".git").exists() and not allow_git_project:
        raise SystemExit(
            f"{project_root} is its own git repository (a production project such as "
            f"athens-2026). A regen re-runs the pipeline and overwrites its pass outputs. "
            f"Run it in a sandbox (`sentinel_regen.py sandbox --from ... --to ...`), or pass "
            f"--allow-git-project if you really mean it.")
    missing = [s for s in slugs if not (project_root / "voices" / s).is_dir()]
    if missing:
        raise SystemExit(f"No voices/<slug>/ in {project_root} for: {', '.join(missing)}")


def make_sandbox(source: Path, target: Path, slugs: list[str]) -> list[Path]:
    """Copy the project-level JSON files and voices/<slug>/ for each slug from
    `source` into a new sandbox project at `target`. Returns the copied paths."""
    source, target = source.resolve(), target.resolve()
    if target == source or source in target.parents:
        raise SystemExit(f"Sandbox {target} must not be inside the source project {source}.")
    if target.exists() and any(target.iterdir()):
        raise SystemExit(f"Sandbox {target} already exists and is not empty — pick a new path.")
    missing = [s for s in slugs if not (source / "voices" / s).is_dir()]
    if missing:
        raise SystemExit(f"No voices/<slug>/ in {source} for: {', '.join(missing)}")
    target.mkdir(parents=True, exist_ok=True)
    copied = []
    for f in sorted(source.glob("*.json")):  # conference_facts, audience_profile, ...
        shutil.copy2(f, target / f.name)
        copied.append(target / f.name)
    for slug in slugs:
        dst = target / "voices" / slug
        shutil.copytree(source / "voices" / slug, dst)
        copied.append(dst)
    return copied


def resolve_baseline(regen_path: Path, project_root: Path, slug: str,
                     baseline_project: Path | None, baseline_snapshot: Path | None) -> Path:
    """Where the shipped version of `regen_path` lives.

    --baseline-project: the same relative path in another project (e.g. the
    untouched production copy the sandbox was made from).
    --baseline-snapshot: <DIR>/<slug>/<filename>, falling back to the flat
    <DIR>/<filename> (FU#50(2) per-voice snapshot layout).
    """
    if baseline_project is not None:
        return baseline_project / regen_path.relative_to(project_root)
    per_voice = baseline_snapshot / slug / regen_path.name
    flat = baseline_snapshot / regen_path.name
    return flat if (not per_voice.exists() and flat.exists()) else per_voice


def _regen_pass_for_voice(pass_name: str, slug: str, project_root: Path) -> Path:
    """Invalidate a pass's cache and re-run pipeline through that pass.
    Returns path to the regenerated pass output JSON."""
    sys.path.insert(0, str(_REPO_ROOT))
    from flows.shared import paths as _paths
    helper = getattr(_paths, f"pass_{pass_name}", None)
    if helper is None:
        raise SystemExit(f"No path helper for pass {pass_name!r} in flows/shared/paths.py")

    invalidate = _REPO_ROOT / "scripts" / "invalidate_cache.py"
    cmd = [sys.executable, str(invalidate), "--voice", slug,
           "--project", str(project_root), "--pass", pass_name]
    print(f"  invalidate: {' '.join(cmd[1:])}")
    subprocess.run(cmd, check=True)

    # Re-run pipeline; it will cache-hit everything except the invalidated
    # pass. The pipeline accepts the slug as its voice name (voice_slug() of
    # a slug is the slug; load_voice_input() accepts either).
    orchestrator = _REPO_ROOT / "run_persona_pipeline.py"
    cmd = [sys.executable, str(orchestrator), slug, "--project", str(project_root)]
    print(f"  re-run: {' '.join(cmd[1:])}")
    subprocess.run(cmd, check=True)
    return helper(slug, project_root)


def _diff_against_baseline(regen_path: Path, baseline_path: Path) -> dict:
    """Diff the regenerated pass output against a baseline copy. Return
    structured diff: {fields_changed, fields_added, fields_removed,
    char_delta_per_field, sample_diffs}."""
    regen = json.loads(regen_path.read_text(encoding="utf-8"))
    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))

    # Pass output JSONs have a "fields" key with the actual card content.
    r_fields = regen.get("fields", regen)
    b_fields = baseline.get("fields", baseline)

    if not isinstance(r_fields, dict) or not isinstance(b_fields, dict):
        return {"error": "Pass output is not a dict; cannot field-diff"}

    r_keys = set(r_fields.keys())
    b_keys = set(b_fields.keys())
    added = r_keys - b_keys
    removed = b_keys - r_keys
    common = r_keys & b_keys

    changed = []
    char_deltas = {}
    sample_diffs = []
    for k in sorted(common):
        if r_fields[k] != b_fields[k]:
            changed.append(k)
            r_str = json.dumps(r_fields[k], ensure_ascii=False)
            b_str = json.dumps(b_fields[k], ensure_ascii=False)
            char_deltas[k] = len(r_str) - len(b_str)
            if len(sample_diffs) < 3:
                sample_diffs.append({
                    "field": k,
                    "char_delta": char_deltas[k],
                    "baseline_excerpt": b_str[:200] + ("..." if len(b_str) > 200 else ""),
                    "regen_excerpt": r_str[:200] + ("..." if len(r_str) > 200 else ""),
                })

    return {
        "fields_changed": sorted(changed),
        "fields_added": sorted(added),
        "fields_removed": sorted(removed),
        "char_delta_per_field": char_deltas,
        "sample_diffs": sample_diffs,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="mode", required=False)

    p_detect = sub.add_parser("detect", help="List passes affected by changed prompts")
    p_detect.add_argument("--since", help="git ref (default: working-tree changes)")

    p_sandbox = sub.add_parser("sandbox", help="Copy sentinel voices into a new sandbox project")
    p_sandbox.add_argument("--from", dest="source", type=Path, required=True,
                           help="project to copy from (read only)")
    p_sandbox.add_argument("--to", dest="target", type=Path, required=True,
                           help="new, empty sandbox project root")
    p_sandbox.add_argument("--voices", default=_DEFAULT_VOICES)

    p_regen = sub.add_parser("regen", help="Regenerate one pass for the sentinels + diff vs baseline")
    p_regen.add_argument("--pass", dest="pass_name", required=True,
                         choices=sorted(set(_PROMPT_TO_PASS.values())))
    p_regen.add_argument("--project", type=Path, required=True,
                         help="sandbox project root to regenerate in")
    p_regen.add_argument("--voices", default=_DEFAULT_VOICES)
    base = p_regen.add_mutually_exclusive_group(required=True)
    base.add_argument("--baseline-project", type=Path,
                      help="project holding the shipped versions (same relative paths)")
    base.add_argument("--baseline-snapshot", type=Path,
                      help="snapshot dir: <DIR>/<slug>/<file> or <DIR>/<file>")
    p_regen.add_argument("--allow-git-project", action="store_true",
                         help="allow --project to be a git repository (production)")

    sub.add_parser("list-prompts", help="Print prompt → pass mapping")

    parser.set_defaults(mode="detect")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.mode == "list-prompts":
        for prompt, pass_name in sorted(_PROMPT_TO_PASS.items()):
            print(f"  {prompt:50}  →  Pass {pass_name}")
        print(f"\nDefault sentinel voices: {_DEFAULT_VOICES}")
        return 0

    if args.mode == "detect":
        since = getattr(args, "since", None)
        changed = _git_changed_prompts(since=since)
        if not changed:
            print(f"No prompt-file changes detected (since={since or 'working-tree'})")
            return 0
        passes = _detect_passes(changed)
        print(f"Changed prompt files ({len(changed)}):")
        for p in changed:
            print(f"  {p}  →  Pass {_PROMPT_TO_PASS[p]}")
        print(f"\nAffected passes: {sorted(passes)}")
        print("\nNext step: `sentinel_regen.py regen --pass <NAME> --project <sandbox> "
              "--baseline-project <production project>` for each.")
        return 0

    if args.mode == "sandbox":
        copied = make_sandbox(args.source, args.target, _voices(args.voices))
        print(f"Sandbox ready at {args.target.resolve()} ({len(copied)} items):")
        for p in copied:
            print(f"  {p}")
        return 0

    if args.mode == "regen":
        voices = _voices(args.voices)
        project_root = args.project.resolve()
        check_project(project_root, voices, args.allow_git_project)
        results = {}
        for slug in voices:
            print(f"\n=== Regen Pass {args.pass_name} for {slug} ===")
            regen_path = _regen_pass_for_voice(args.pass_name, slug, project_root)
            baseline_path = resolve_baseline(
                regen_path, project_root, slug,
                args.baseline_project.resolve() if args.baseline_project else None,
                args.baseline_snapshot)
            if not baseline_path.exists():
                print(f"  WARN: no baseline at {baseline_path}; skipping diff")
                results[slug] = {"regen_path": str(regen_path), "diff": None}
                continue
            diff = _diff_against_baseline(regen_path, baseline_path)
            results[slug] = {
                "regen_path": str(regen_path),
                "baseline_path": str(baseline_path),
                "diff": diff,
            }
            print(f"  fields_changed: {diff.get('fields_changed')}")
            print(f"  fields_added:   {diff.get('fields_added')}")
            print(f"  fields_removed: {diff.get('fields_removed')}")
            for s in diff.get("sample_diffs", []):
                print(f"  {s['field']}: Δ{s['char_delta']:+d} chars")
        print("\n=== Summary ===")
        print(json.dumps(results, indent=2, ensure_ascii=False))
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
