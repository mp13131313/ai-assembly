"""Generate reference/speakers.json — a stub registry, merge-safe on re-run.

Walks every session in reference/sessions.json, collects unique speaker
names, and emits one stub entry per speaker for humans to fill in:

    { "name": "...", "title": "", "affiliation": "", "bio": "",
      "sessions": ["day_one_demos_..."] }

Re-running is safe: existing `title`, `affiliation`, and `bio` values are
preserved; only `sessions` is regenerated from the current sessions.json.
Speakers who disappear from the program are kept with `_dropped_from_program`
set so their bios aren't lost if they return later.

Usage
-----
    python scripts/generate_speakers_json.py
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


# Defaults resolved from $AI_ASSEMBLY_PROJECT_ROOT (Tier 3). Override via
# --sessions / --output for scripted use. Falls back to an empty Path if the
# env var is unset — argparse will report "required" via required=True below
# if the user also omits the explicit flags.
import os as _os
_env_project = _os.environ.get("AI_ASSEMBLY_PROJECT_ROOT")
_PROJECT_ROOT = Path(_env_project).expanduser() if _env_project else None
SESSIONS_PATH = (_PROJECT_ROOT / "reference/sessions.json") if _PROJECT_ROOT else None
SPEAKERS_PATH = (_PROJECT_ROOT / "reference/speakers.json") if _PROJECT_ROOT else None


def load_existing(path: Path) -> dict[str, dict]:
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return {sp["name"]: sp for sp in data.get("speakers", [])}


def build_name_index(sessions: list[dict]) -> dict[str, list[str]]:
    """Map speaker name -> list of session_ids they appear in."""
    index: dict[str, list[str]] = {}
    for s in sessions:
        for name in s.get("speakers", []):
            index.setdefault(name, []).append(s["session_id"])
    return index


def merge(name_to_sessions: dict[str, list[str]], existing: dict[str, dict]) -> list[dict]:
    """Preserve existing bios; add stubs for new speakers; flag dropped ones."""
    merged: list[dict] = []

    # Current speakers: either updated from existing or fresh stubs.
    for name in sorted(name_to_sessions):
        prev = existing.get(name, {})
        merged.append(
            {
                "name": name,
                "title": prev.get("title", ""),
                "affiliation": prev.get("affiliation", ""),
                "bio": prev.get("bio", ""),
                "sessions": name_to_sessions[name],
            }
        )

    # Speakers previously in file but no longer in the program: keep with flag.
    dropped = sorted(set(existing) - set(name_to_sessions))
    for name in dropped:
        prev = existing[name]
        merged.append(
            {
                "name": name,
                "title": prev.get("title", ""),
                "affiliation": prev.get("affiliation", ""),
                "bio": prev.get("bio", ""),
                "sessions": [],
                "_dropped_from_program": True,
            }
        )

    return merged


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--sessions", type=Path, default=SESSIONS_PATH,
                    help="Path to sessions.json (default: $AI_ASSEMBLY_PROJECT_ROOT/reference/sessions.json)")
    ap.add_argument("--output", type=Path, default=SPEAKERS_PATH,
                    help="Path to write speakers.json (default: $AI_ASSEMBLY_PROJECT_ROOT/reference/speakers.json)")
    args = ap.parse_args()

    if args.sessions is None or args.output is None:
        raise SystemExit(
            "Paths unresolved: set AI_ASSEMBLY_PROJECT_ROOT or pass "
            "--sessions / --output explicitly."
        )

    if not args.sessions.exists():
        raise SystemExit(
            f"sessions.json not found at {args.sessions} — run "
            f"scripts/generate_sessions_json.py first."
        )

    sessions = json.loads(args.sessions.read_text(encoding="utf-8"))["sessions"]
    name_to_sessions = build_name_index(sessions)
    existing = load_existing(args.output)

    speakers = merge(name_to_sessions, existing)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(
            {
                "generated_from": str(args.sessions),
                "generated_at_note": "regenerate by re-running scripts/generate_speakers_json.py; "
                                     "existing bios are preserved",
                "speaker_count": len(speakers),
                "speakers": speakers,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    # --- Summary -------------------------------------------------------------
    active = [sp for sp in speakers if not sp.get("_dropped_from_program")]
    dropped = [sp for sp in speakers if sp.get("_dropped_from_program")]
    with_bio = sum(1 for sp in active if sp["bio"].strip())
    new_count = sum(1 for sp in active if sp["name"] not in existing)

    print(f"Speakers: {len(active)} active ({with_bio} with bios, "
          f"{len(active) - with_bio} stubs)")
    if new_count:
        print(f"  New since last run: {new_count}")
    if dropped:
        print(f"Dropped from program: {len(dropped)} (kept in file for bio preservation)")
        for sp in dropped:
            print(f"  - {sp['name']}")
    print(f"Written: {args.output}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
