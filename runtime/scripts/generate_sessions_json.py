"""Generate reference/sessions.json from the WBBF program HTML.

Reads the `const SESSIONS = [...]` array embedded in the program's index.html
and produces a normalized sessions.json that the AI Assembly upload UI and
pipeline can consume.

Usage
-----
    python scripts/generate_sessions_json.py \
        --input /Users/Shared/index.html \
        --output reference/sessions.json

Re-run whenever the program changes. The source HTML is the source of truth;
any hand-edits to the emitted sessions.json will be overwritten on re-run.

Notes
-----
- `ai_assembly` defaults to `false` on every session. Flip to `true` for the
  subset that should be transcribed by the overnight pipeline.
- `session_format` is inferred (walking / keynote / workshop / panel) and
  marked `session_format_confidence: "inferred"`. A human pass should flip
  that to `"reviewed"` once confirmed.
- Rows that can't be cleanly transformed (no title, TBC venue, missing date
  for Special Activations) are emitted to sessions.skipped.json for manual
  review rather than silently dropped.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

# --- Constants ---------------------------------------------------------------

# Conference dates. Athens is UTC+3 (EEST) throughout May.
DAY_TO_DATE = {
    "Day Zero": "2026-05-06",   # Wednesday
    "Day One": "2026-05-07",    # Thursday
    "Day Two": "2026-05-08",    # Friday
    "Day Three": "2026-05-09",  # Saturday
    "Day Four": "2026-05-10",   # Sunday
}
DAY_TO_INDEX = {
    "Day Zero": 0,
    "Day One": 1,
    "Day Two": 2,
    "Day Three": 3,
    "Day Four": 4,
    "Special Activations": -1,
}
TZ_OFFSET = "+03:00"

# Tracks typically run as workshops (hands-on, smaller groups).
WORKSHOP_TRACKS = {
    "BEAUTY SALON",
    "LONGEVITY LAB",
    "TEMPLE OF REENCHANTMENT",
    "BUREAU OF CARE",
    "HOME OF BELONGING",
}

# --- Helpers -----------------------------------------------------------------


def slugify(text: str, max_len: int = 40) -> str:
    """Lowercase, replace non-alphanumerics with underscores, collapse, trim."""
    s = text.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s[:max_len].rstrip("_")


def extract_sessions_array(html: str) -> list[dict]:
    """Pull the `const SESSIONS = [...]` JS array out of the HTML."""
    m = re.search(r"const\s+SESSIONS\s*=\s*(\[.*?\]);", html, re.DOTALL)
    if not m:
        raise SystemExit("Could not find `const SESSIONS = [...]` in HTML.")
    return json.loads(m.group(1))


def split_speakers(raw: str) -> list[str]:
    """Turn 'A, B and C' / 'A, B, and C' / 'A, B, C' into ['A', 'B', 'C']."""
    if not raw or not raw.strip():
        return []
    # Normalize " and " / " & " to commas before splitting.
    s = re.sub(r"\s+(?:and|&)\s+", ", ", raw)
    parts = [p.strip() for p in s.split(",")]
    return [p for p in parts if p]


def parse_bool(v: str) -> bool:
    return str(v).strip().lower() in {"yes", "true", "1", "y"}


def parse_capacity(v: str) -> int | None:
    v = str(v).strip()
    if not v:
        return None
    m = re.search(r"\d+", v)
    return int(m.group(0)) if m else None


def infer_session_format(
    *, venue: str, title: str, description: str, track: str, n_speakers: int
) -> str:
    """Best-guess mapping onto {walking, keynote, workshop, panel}."""
    blob = f"{title} {description}".lower()
    if venue.strip().lower() == "outdoors" or re.search(
        r"\b(walk|tour|stroll|procession)\b", blob
    ):
        return "walking"
    if track.strip().upper() in WORKSHOP_TRACKS and n_speakers <= 2:
        return "workshop"
    if track.strip().upper() == "MAIN STAGE" and n_speakers == 1:
        return "keynote"
    if n_speakers == 1:
        return "keynote"
    return "panel"


def build_session_id(row: dict) -> str:
    """Format: {day}_{venue}_{track}_{title}_{timeStart}, each slugified."""
    day = slugify(row.get("day", ""), max_len=20) or "unknown_day"
    venue = slugify(row.get("venue", ""), max_len=20) or "unknown_venue"
    track = slugify(row.get("track", ""), max_len=30) or "unknown_track"
    title = slugify(row.get("title", ""), max_len=40) or "untitled"
    time_raw = row.get("timeStart", "").replace(":", "")
    time_slug = slugify(time_raw, max_len=8) or "0000"
    return f"{day}_{venue}_{track}_{title}_{time_slug}"


def iso_datetime(date_iso: str | None, hhmm: str) -> str | None:
    """Combine '2026-05-07' + '11:30' into ISO datetime with Athens offset."""
    if not date_iso or not hhmm:
        return None
    m = re.match(r"^(\d{1,2}):(\d{2})$", hhmm.strip())
    if not m:
        return None
    h, mm = m.group(1).zfill(2), m.group(2)
    return f"{date_iso}T{h}:{mm}:00{TZ_OFFSET}"


# --- Transformation ----------------------------------------------------------


@dataclass
class Skipped:
    row: dict
    reason: str


def transform(row: dict) -> dict | Skipped:
    title = (row.get("title") or "").strip()
    if not title:
        return Skipped(row, "missing title")

    venue = (row.get("venue") or "").strip()
    if venue.upper() == "TBC":
        return Skipped(row, "venue is TBC — firm up in program first")

    day = (row.get("day") or "").strip()
    date_iso = DAY_TO_DATE.get(day)  # None for Special Activations
    day_index = DAY_TO_INDEX.get(day, -1)

    speakers = split_speakers(row.get("speakers") or "")
    session_format = infer_session_format(
        venue=venue,
        title=title,
        description=(row.get("description") or "").strip(),
        track=(row.get("track") or "").strip(),
        n_speakers=len(speakers),
    )

    return {
        "session_id": build_session_id(row),
        "ai_assembly": False,
        "day": day,
        "day_index": day_index,
        "date": date_iso,                 # null for Special Activations
        "date_display": (row.get("date") or "").strip(),
        "start_time": (row.get("timeStart") or "").strip(),
        "end_time": (row.get("timeEnd") or "").strip(),
        "date_time_start": iso_datetime(date_iso, row.get("timeStart") or ""),
        "venue": venue,
        "venue_sub": (row.get("venueSub") or "").strip(),
        "track": (row.get("track") or "").strip(),
        "title": title,
        "description": (row.get("description") or "").strip(),
        "speakers": speakers,
        "session_format": session_format,
        "session_format_confidence": "inferred",
        "partner": (row.get("partner") or "").strip(),
        "limited_capacity": parse_bool(row.get("limitedCapacity") or ""),
        "capacity": parse_capacity(row.get("capacity") or ""),
    }


# --- Main --------------------------------------------------------------------


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--input",
        type=Path,
        default=Path("/Users/Shared/index.html"),
        help="Path to the program HTML containing `const SESSIONS = [...]`",
    )
    ap.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "reference" / "sessions.json",
        help="Where to write the normalized sessions.json",
    )
    args = ap.parse_args()

    if not args.input.exists():
        print(f"Input not found: {args.input}", file=sys.stderr)
        return 1

    html = args.input.read_text(encoding="utf-8")
    raw_sessions = extract_sessions_array(html)

    # Preserve existing ai_assembly flags so hand-flipped values survive re-runs.
    # Same philosophy as generate_speakers_json.py preserving bios.
    existing_flags: dict[str, bool] = {}
    if args.output.exists():
        try:
            prior = json.loads(args.output.read_text(encoding="utf-8"))
            for s in prior.get("sessions", []):
                if "session_id" in s:
                    existing_flags[s["session_id"]] = bool(s.get("ai_assembly", False))
        except (json.JSONDecodeError, OSError):
            pass  # ignore a malformed prior file; treat as first run

    kept: list[dict] = []
    skipped: list[dict] = []
    for row in raw_sessions:
        result = transform(row)
        if isinstance(result, Skipped):
            skipped.append({"reason": result.reason, "row": result.row})
        else:
            kept.append(result)

    # Re-apply preserved ai_assembly flags by session_id.
    preserved = 0
    for s in kept:
        if existing_flags.get(s["session_id"]):
            s["ai_assembly"] = True
            preserved += 1

    # Sort kept sessions by day_index then start_time for readable output.
    kept.sort(key=lambda s: (s["day_index"], s.get("start_time") or "", s["title"]))

    # Detect duplicate session_ids and rename the collisions with a numeric
    # suffix. Better to emit a valid file with a warning than to fail.
    seen: dict[str, int] = {}
    for s in kept:
        sid = s["session_id"]
        if sid in seen:
            seen[sid] += 1
            s["session_id"] = f"{sid}_{seen[sid]}"
            s["_id_collision"] = True
        else:
            seen[sid] = 0

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(
            {
                "generated_from": str(args.input),
                "generated_at_note": "regenerate by re-running scripts/generate_sessions_json.py",
                "session_count": len(kept),
                "sessions": kept,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    if skipped:
        skipped_path = args.output.with_name("sessions.skipped.json")
        skipped_path.write_text(
            json.dumps(
                {"count": len(skipped), "skipped": skipped},
                indent=2,
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
        )

    # --- Summary -------------------------------------------------------------
    from collections import Counter

    by_day = Counter(s["day"] for s in kept)
    by_format = Counter(s["session_format"] for s in kept)
    collisions = sum(1 for s in kept if s.get("_id_collision"))
    speakers_flat = {n for s in kept for n in s["speakers"]}

    print(f"Kept:    {len(kept)} sessions → {args.output}")
    if preserved:
        print(f"Preserved ai_assembly=true on {preserved} session(s) from prior run")
    if skipped:
        print(f"Skipped: {len(skipped)} sessions → {args.output.with_name('sessions.skipped.json')}")
        for sk in skipped:
            title = (sk["row"].get("title") or "(no title)").strip()
            print(f"  - [{sk['reason']}] {title}")
    print()
    print("Sessions per day:")
    for day in ["Day Zero", "Day One", "Day Two", "Day Three", "Day Four", "Special Activations"]:
        if day in by_day:
            print(f"  {day:<22} {by_day[day]}")
    print()
    print("Inferred session_format distribution:")
    for fmt, n in by_format.most_common():
        print(f"  {fmt:<10} {n}")
    print()
    print(f"Unique speakers: {len(speakers_flat)}")
    if collisions:
        print(f"WARNING: {collisions} session_id collisions — suffixed with _1, _2, ...")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
