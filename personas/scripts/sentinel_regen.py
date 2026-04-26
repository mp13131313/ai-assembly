#!/usr/bin/env python3
"""sentinel_regen.py — FU#29 narrow: prompt-touch sentinel regen for variance management.

When a Pass 2-6 prompt changes (or any other shared prompt under
flows/shared/prompts/), regenerate just that pass's affected card field(s)
for two sentinel voices (Plato + Dostoevsky) and diff against baseline.
Catches silent regressions that would otherwise propagate to the whole
12-voice panel only when each voice next runs.

Empirical motivation: at 12-voice scale, formal regen-on-commit becomes
worth doing for variance management. ~$3-5 per change, ~10 min wall —
vs ~$216 + 12 hr for a full 12-voice panel re-run.

Usage:
    # Detect what's changed since last commit:
    venv/bin/python scripts/sentinel_regen.py --detect-changes

    # Regenerate sentinels for a specific pass + diff vs baseline:
    venv/bin/python scripts/sentinel_regen.py \\
        --pass 4a \\
        --voices plato,fyodor_dostoevsky \\
        --baseline-tag 2026-04-26-baseline

    # Just diff the most recent regen vs baseline:
    venv/bin/python scripts/sentinel_regen.py --diff-only

Prompt → pass mapping (which prompt files affect which pass output):

    Pass 2  ← persona_pass_2_identity_boundaries.md, persona_pass_2_user.md
    Pass 3  ← persona_pass_3_intellectual_core.md, persona_pass_3_user.md
    Pass 4a ← persona_pass_4a_voice.md, persona_pass_4a_user.md
    Pass 4b ← persona_pass_4b_artifact.md, persona_pass_4b_user.md
    Pass 5  ← persona_pass_5_engagement.md, persona_pass_5_user.md
    Pass 6  ← persona_pass_6_corpus.md, persona_pass_6_user.md

Sentinel voices: Plato (philosophical) + Fyodor Dostoevsky (narratival).
Configurable via --voices.

Architecture: this is the NARROW version of FU#29 (prompt-touch detection
only). The BROAD version — detecting any pipeline-code change and
performing impact analysis — is post-Athens architectural work. See
FOLLOW_UPS.md FU#29 for context.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]


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


# Sentinel voice config. Each tuple: (slug, project-root path).
_DEFAULT_SENTINELS: list[tuple[str, Path]] = [
    ("plato", Path("/Users/aienvironment/Desktop/AI Assembly/projects/phase-l-plato")),
    ("fyodor_dostoevsky", Path("/Users/aienvironment/Desktop/AI Assembly/projects/phase-l-dostoevsky")),
]


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


def _regen_pass_for_voice(pass_name: str, slug: str, project_root: Path) -> Path:
    """Invalidate a pass's cache and re-run pipeline through that pass.
    Returns path to the regenerated pass output JSON."""
    invalidate = _REPO_ROOT / "scripts" / "invalidate_cache.py"
    cmd = [
        sys.executable, str(invalidate),
        "--voice", slug,
        "--project", str(project_root),
        "--pass", pass_name,
    ]
    print(f"  invalidate: {' '.join(cmd[1:])}")
    subprocess.run(cmd, check=True)

    # Re-run pipeline; it will cache-hit everything except the invalidated pass.
    orchestrator = _REPO_ROOT / "run_persona_pipeline.py"
    voice_display = slug.replace("_", " ").title()
    cmd = [
        sys.executable, str(orchestrator),
        voice_display,
        "--project", str(project_root),
    ]
    print(f"  re-run: {' '.join(cmd[1:])}")
    subprocess.run(cmd, check=True)

    # Resolve output path from paths module.
    sys.path.insert(0, str(_REPO_ROOT))
    from flows.shared import paths as _paths
    helper_name = f"pass_{pass_name.replace('a', 'a').replace('b', 'b')}"
    helper = getattr(_paths, helper_name, None)
    if helper is None:
        # Try direct mapping for non-trivial names like 4a / 4b
        helper = getattr(_paths, f"pass_{pass_name}", None)
    if helper is None:
        raise RuntimeError(f"No path helper for pass {pass_name!r}")
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


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="mode", required=False)

    p_detect = sub.add_parser("detect", help="List passes affected by changed prompts")
    p_detect.add_argument("--since", help="git ref (default: working-tree changes)")

    p_regen = sub.add_parser("regen", help="Regenerate sentinels for a pass + diff vs baseline")
    p_regen.add_argument("--pass", dest="pass_name", required=True)
    p_regen.add_argument("--voices", default="plato,fyodor_dostoevsky")
    p_regen.add_argument("--baseline-snapshot", required=True,
                          help="absolute path to baseline snapshot dir (for diff)")

    p_help = sub.add_parser("list-prompts", help="Print prompt → pass mapping")

    # Default mode: detect-changes
    parser.set_defaults(mode="detect")
    args = parser.parse_args()

    if args.mode == "list-prompts":
        for prompt, pass_name in sorted(_PROMPT_TO_PASS.items()):
            print(f"  {prompt:50}  →  Pass {pass_name}")
        print(f"\nSentinel voices (default): {[s for s, _ in _DEFAULT_SENTINELS]}")
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
        print(f"\nNext step: run `sentinel_regen.py regen --pass <NAME>` for each.")
        return 0

    if args.mode == "regen":
        voices = [v.strip() for v in args.voices.split(",") if v.strip()]
        sentinel_map = {s: p for s, p in _DEFAULT_SENTINELS}
        results = {}
        for slug in voices:
            project_root = sentinel_map.get(slug)
            if project_root is None:
                print(f"Skipping unknown sentinel voice: {slug!r}", file=sys.stderr)
                continue
            print(f"\n=== Regen Pass {args.pass_name} for {slug} ===")
            regen_path = _regen_pass_for_voice(args.pass_name, slug, project_root)
            baseline_path = Path(args.baseline_snapshot) / regen_path.name
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
            print(f"  fields_changed: {diff['fields_changed']}")
            print(f"  fields_added:   {diff['fields_added']}")
            print(f"  fields_removed: {diff['fields_removed']}")
            for s in diff["sample_diffs"]:
                print(f"  {s['field']}: Δ{s['char_delta']:+d} chars")
        print(f"\n=== Summary ===")
        print(json.dumps(results, indent=2, ensure_ascii=False))
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
