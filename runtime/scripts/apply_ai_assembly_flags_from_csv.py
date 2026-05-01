"""Apply ai_assembly=true flags to sessions.json from an authoritative CSV.

The recording schedule CSV (operator-curated) lists the exact sessions to
be transcribed each night. This script:
  - Reads the CSV
  - Matches each row against sessions.json by title + day + start time
  - Sets ai_assembly=true on matched sessions
  - Sets ai_assembly=false on all unmatched sessions (CSV is authoritative)
  - Reports any CSV rows that couldn't be matched for operator review

CSV expected shape (header on row 4 due to title rows):
  Night,Day,Date,Start,End,Duration,Venue,Capture mode,Track,Session,Speakers,Notes

Matching strategy:
  1. Exact title match in sessions.json
  2. If multiple matches (same title across days/times), disambiguate by:
     a. Day (Day One/Two/Three → day_one/day_two/day_three)
     b. Start time (HH:MM → HHMM suffix on session_id)
  3. If still ambiguous, report for manual review

Usage
-----
    python scripts/apply_ai_assembly_flags_from_csv.py \\
        --csv "/path/to/recording_sessions.csv" \\
        [--sessions /path/to/sessions.json] \\
        [--dry-run]
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
from pathlib import Path


_env_project = os.environ.get("AI_ASSEMBLY_PROJECT_ROOT")
_PROJECT_ROOT = Path(_env_project).expanduser() if _env_project else None
_DEFAULT_SESSIONS = (_PROJECT_ROOT / "reference/sessions.json") if _PROJECT_ROOT else None


DAY_LABEL_TO_KEY = {
    "Day Zero": "day_zero",
    "Day One": "day_one",
    "Day Two": "day_two",
    "Day Three": "day_three",
    "Day Four": "day_four",
}


def parse_csv_rows(csv_path: Path) -> list[dict]:
    """Read recording sessions from CSV. Skip header rows + subtotal rows."""
    rows: list[dict] = []
    with csv_path.open(encoding="utf-8") as f:
        reader = csv.reader(f)
        header_idx: int | None = None
        for i, row in enumerate(reader):
            if not row:
                continue
            # Header row contains "Night,Day,Date,Start,End,..."
            if row[0].strip() == "Night" and header_idx is None:
                header_idx = i
                continue
            if header_idx is None:
                continue
            # Skip subtotal rows ("Night 1 subtotal,,,,, ...")
            if "subtotal" in row[0].lower():
                continue
            # Skip total + legend rows
            if not row[0].startswith("Night ") or len(row) < 10:
                continue
            night, day, date, start, end, duration, venue, capture, track, session = row[:10]
            speakers = row[10] if len(row) > 10 else ""
            notes = row[11] if len(row) > 11 else ""
            rows.append({
                "night": night.strip(),
                "day": day.strip(),
                "date": date.strip(),
                "start": start.strip(),
                "end": end.strip(),
                "duration": duration.strip(),
                "venue": venue.strip(),
                "capture": capture.strip(),
                "track": track.strip(),
                "session": session.strip(),
                "speakers": speakers.strip(),
                "notes": notes.strip(),
            })
    return rows


def normalize_title(title: str) -> str:
    """Lowercase, collapse whitespace, strip surrounding punctuation.

    Also normalizes strikethrough markup: CSV uses `~text~`, HTML/sessions.json
    uses `<s>text</s>`. Both stripped to bare text so they match.
    """
    s = title.lower().strip()
    # Strip strikethrough markup variants
    s = re.sub(r"<s>(.*?)</s>", r"\1", s)
    s = re.sub(r"~([^~]+)~", r"\1", s)
    s = re.sub(r"\s+", " ", s)
    s = s.strip(".,;:!?\"'")
    return s


def time_suffix(start: str) -> str:
    """Convert "10:00" → "1000" for session_id matching."""
    hh, mm = start.split(":")
    return f"{int(hh):d}{mm}"


def match_csv_row_to_session(csv_row: dict, sessions: list[dict]) -> tuple[str | None, list[str]]:
    """Find the best session_id match for a CSV row.

    Returns (best_match_session_id, list_of_candidates_when_ambiguous).
    """
    target_title_norm = normalize_title(csv_row["session"])
    day_key = DAY_LABEL_TO_KEY.get(csv_row["day"], "")
    time_sfx = time_suffix(csv_row["start"]) if csv_row["start"] else ""

    # First pass: exact title match (normalized)
    title_matches = [
        s for s in sessions if normalize_title(s["title"]) == target_title_norm
    ]
    if len(title_matches) == 1:
        return title_matches[0]["session_id"], []
    if len(title_matches) == 0:
        return None, []

    # Multiple title matches — disambiguate by day prefix + time suffix on session_id
    # session_id format: day_<X>_<venue>_<track>_<title_slug>_<HHMM>
    candidates_by_day_time = [
        s for s in title_matches
        if s["session_id"].startswith(day_key + "_")
        and s["session_id"].endswith("_" + time_sfx)
    ]
    if len(candidates_by_day_time) == 1:
        return candidates_by_day_time[0]["session_id"], []

    # Try day-only filter
    candidates_by_day = [
        s for s in title_matches if s["session_id"].startswith(day_key + "_")
    ]
    if len(candidates_by_day) == 1:
        return candidates_by_day[0]["session_id"], []

    # Still ambiguous — return all candidates
    return None, [s["session_id"] for s in title_matches]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--csv", type=Path, required=True,
                    help="Path to recording sessions CSV.")
    ap.add_argument("--sessions", type=Path, default=_DEFAULT_SESSIONS,
                    help="Path to sessions.json (default: $AI_ASSEMBLY_PROJECT_ROOT/reference/sessions.json).")
    ap.add_argument("--dry-run", action="store_true",
                    help="Print summary without writing.")
    args = ap.parse_args()

    if args.sessions is None:
        raise SystemExit("Set AI_ASSEMBLY_PROJECT_ROOT or pass --sessions.")
    if not args.csv.exists():
        raise SystemExit(f"CSV not found: {args.csv}")
    if not args.sessions.exists():
        raise SystemExit(f"sessions.json not found: {args.sessions}")

    csv_rows = parse_csv_rows(args.csv)
    print(f"Parsed {len(csv_rows)} recording-session rows from CSV.")

    data = json.loads(args.sessions.read_text(encoding="utf-8"))
    sessions = data["sessions"]
    by_id = {s["session_id"]: s for s in sessions}

    matched_ids: set[str] = set()
    not_matched: list[tuple[dict, list[str]]] = []

    for row in csv_rows:
        sid, candidates = match_csv_row_to_session(row, sessions)
        if sid:
            matched_ids.add(sid)
        else:
            not_matched.append((row, candidates))

    # Apply: ai_assembly=true on matched, false on all others (CSV authoritative)
    flag_changes_to_true = 0
    flag_changes_to_false = 0
    for s in sessions:
        target = s["session_id"] in matched_ids
        if s.get("ai_assembly") != target:
            if target:
                flag_changes_to_true += 1
            else:
                flag_changes_to_false += 1
            s["ai_assembly"] = target

    print(f"\nMatched: {len(matched_ids)} / {len(csv_rows)} CSV rows")
    print(f"Flag changes:")
    print(f"  set ai_assembly=true:  {flag_changes_to_true}")
    print(f"  set ai_assembly=false: {flag_changes_to_false}")
    print(f"Final ai_assembly=true count: {sum(1 for s in sessions if s.get('ai_assembly'))}")

    if not_matched:
        print(f"\nUnmatched CSV rows ({len(not_matched)} — operator review):")
        for row, candidates in not_matched:
            print(f"  - {row['night']}: {row['session']!r}")
            print(f"      day={row['day']!r}, start={row['start']}, venue={row['venue']!r}")
            if candidates:
                print(f"      ambiguous — title matches multiple session_ids:")
                for sid in candidates:
                    sess = by_id.get(sid, {})
                    print(f"        {sid} (title={sess.get('title', '?')!r}, "
                          f"venue={sess.get('venue', '?')!r})")
            else:
                print(f"      no title match in sessions.json — possibly a new "
                      f"session not yet in scaffold, or title differs")

    if args.dry_run:
        print("\n[DRY RUN — no file written]")
        return 0

    args.sessions.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"\nWritten: {args.sessions}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
