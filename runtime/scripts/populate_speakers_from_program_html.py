"""Populate reference/speakers.json from the WBBF program HTML.

The WBBF program page embeds a `const SPEAKERS = {...}` JS object containing
each speaker's `oneliner` (short title/role) and `attributes` (array of
bio bullet-points). This script extracts that data and merges it into the
existing speakers.json scaffold, preserving any manually-curated fields.

Schema mapping:
  HTML.oneliner       → speakers.json title
  HTML.attributes[0]  → speakers.json affiliation  (most senior role / primary org)
  HTML.attributes     → speakers.json bio          (joined: "X · Y · Z")
                        Falls back to oneliner if attributes is empty —
                        speaker has only a one-line role (dancers, DJs, etc.)

Name matching:
  - Exact match first
  - Falls back to accent-stripped + case-insensitive match (so SESSIONS
    and SPEAKERS spelling drift in the source HTML doesn't lose enrichment)

Merge policy:
  - Only populate fields that are currently empty (manually-set values win)
  - Speakers in speakers.json but not in HTML: left as-is, flagged in summary
  - Speakers in HTML but not in speakers.json: ignored (outside scaffold)
  - Re-running is safe: existing populated fields are preserved

Usage
-----
    python scripts/populate_speakers_from_program_html.py \\
        --html "/path/to/index.html" \\
        [--speakers-json /path/to/speakers.json] \\
        [--dry-run]

If --speakers-json is omitted, defaults to
$AI_ASSEMBLY_PROJECT_ROOT/reference/speakers.json.

Use --dry-run to preview changes without writing.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import unicodedata
from pathlib import Path


def _normalize(name: str) -> str:
    """Lowercase + accent-strip + whitespace-collapse. Used for fuzzy match."""
    s = unicodedata.normalize("NFKD", name)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", s).lower().strip()


_env_project = os.environ.get("AI_ASSEMBLY_PROJECT_ROOT")
_PROJECT_ROOT = Path(_env_project).expanduser() if _env_project else None
_DEFAULT_SPEAKERS = (_PROJECT_ROOT / "reference/speakers.json") if _PROJECT_ROOT else None


def extract_speakers_from_html(html_path: Path) -> dict[str, dict]:
    """Pull `const SPEAKERS = {...};` out of the program HTML.

    Returns a name → {oneliner, attributes} dict. Raises SystemExit with a
    clear message if the const isn't found or doesn't parse as JSON.
    """
    text = html_path.read_text(encoding="utf-8")
    # Match the JS object literal — non-greedy through `};` followed by newline.
    m = re.search(r"const\s+SPEAKERS\s*=\s*(\{.*?\});\s*\n", text, re.DOTALL)
    if not m:
        raise SystemExit(
            f"`const SPEAKERS = {{...}};` not found in {html_path}. "
            f"The HTML format may have changed; inspect the file manually."
        )
    try:
        data = json.loads(m.group(1))
    except json.JSONDecodeError as e:
        raise SystemExit(
            f"Failed to parse SPEAKERS JSON from {html_path}: {e}. "
            f"The JS object may use non-JSON syntax (trailing commas, "
            f"single-quoted strings, etc.)."
        )
    return data


def populate(
    speakers: list[dict],
    html_speakers: dict[str, dict],
) -> tuple[list[dict], dict[str, int]]:
    """Merge HTML data into speakers list, preserving curated values.

    Returns the new list + a stats dict for summary reporting.
    """
    stats = {
        "total": len(speakers),
        "matched_in_html": 0,
        "matched_via_fuzzy": 0,
        "populated_title": 0,
        "populated_affiliation": 0,
        "populated_bio": 0,
        "already_curated": 0,
        "not_in_html": 0,
    }
    not_matched: list[str] = []

    # Build a normalized lookup for accent-tolerant fuzzy match.
    norm_to_html_name: dict[str, str] = {_normalize(n): n for n in html_speakers}

    for sp in speakers:
        name = sp["name"]
        # Exact match first.
        html_name = name if name in html_speakers else None
        # Accent-stripped + case-insensitive fallback.
        if html_name is None:
            html_name = norm_to_html_name.get(_normalize(name))
            if html_name is not None:
                stats["matched_via_fuzzy"] += 1

        if html_name is None:
            stats["not_in_html"] += 1
            not_matched.append(name)
            continue

        stats["matched_in_html"] += 1
        html = html_speakers[html_name]
        oneliner = html.get("oneliner", "").strip()
        attributes = [a.strip() for a in html.get("attributes", []) if a.strip()]

        # Title from oneliner. Preserve existing.
        if not sp.get("title", "").strip() and oneliner:
            sp["title"] = oneliner
            stats["populated_title"] += 1
        elif sp.get("title", "").strip():
            stats["already_curated"] += 1

        # Affiliation from first attribute (typically primary role / org).
        # Falls back to oneliner if no attributes (one-line speakers).
        # Preserve existing.
        if not sp.get("affiliation", "").strip():
            if attributes:
                sp["affiliation"] = attributes[0]
                stats["populated_affiliation"] += 1
            elif oneliner:
                sp["affiliation"] = oneliner
                stats["populated_affiliation"] += 1

        # Bio from joined attributes. Falls back to oneliner if attributes
        # is empty so the bio field isn't blank for speakers that only have
        # a one-line role (dancers, DJ collectives, etc.). Preserve existing.
        if not sp.get("bio", "").strip():
            if attributes:
                sp["bio"] = " · ".join(attributes)
                stats["populated_bio"] += 1
            elif oneliner:
                sp["bio"] = oneliner
                stats["populated_bio"] += 1

    return speakers, stats, not_matched


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--html",
        type=Path,
        required=True,
        help="Path to the WBBF program index HTML.",
    )
    ap.add_argument(
        "--speakers-json",
        type=Path,
        default=_DEFAULT_SPEAKERS,
        help="Path to speakers.json (default: $AI_ASSEMBLY_PROJECT_ROOT/reference/speakers.json).",
    )
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="Print summary without writing.",
    )
    args = ap.parse_args()

    if args.speakers_json is None:
        raise SystemExit(
            "speakers.json path unresolved: set AI_ASSEMBLY_PROJECT_ROOT or "
            "pass --speakers-json explicitly."
        )

    if not args.html.exists():
        raise SystemExit(f"HTML not found: {args.html}")
    if not args.speakers_json.exists():
        raise SystemExit(
            f"speakers.json not found: {args.speakers_json}\n"
            f"Run scripts/generate_speakers_json.py first to scaffold it."
        )

    html_speakers = extract_speakers_from_html(args.html)
    print(f"Parsed {len(html_speakers)} speakers from {args.html.name}")

    data = json.loads(args.speakers_json.read_text(encoding="utf-8"))
    speakers = data["speakers"]

    new_speakers, stats, not_matched = populate(speakers, html_speakers)
    data["speakers"] = new_speakers
    data["enriched_from"] = str(args.html.resolve())

    print(f"\nSummary:")
    print(f"  Total in speakers.json:  {stats['total']}")
    print(f"  Matched in HTML:         {stats['matched_in_html']}"
          f" (of which fuzzy: {stats['matched_via_fuzzy']})")
    print(f"  Populated title:         {stats['populated_title']}")
    print(f"  Populated affiliation:   {stats['populated_affiliation']}")
    print(f"  Populated bio:           {stats['populated_bio']}")
    print(f"  Pre-curated (preserved): {stats['already_curated']}")
    print(f"  Not in HTML:             {stats['not_in_html']}")

    if not_matched:
        print(f"\nSpeakers in speakers.json but NOT in HTML "
              f"({len(not_matched)} — operator review):")
        for name in not_matched:
            print(f"  - {name}")

    extra_in_html = sorted(set(html_speakers) - {sp["name"] for sp in speakers})
    if extra_in_html:
        print(f"\nIn HTML but NOT in speakers.json "
              f"({len(extra_in_html)} — possibly new speakers since last "
              f"sessions.json regen):")
        for name in extra_in_html:
            print(f"  + {name}")

    if args.dry_run:
        print("\n[DRY RUN — no file written]")
        return 0

    args.speakers_json.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"\nWritten: {args.speakers_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
