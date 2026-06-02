#!/usr/bin/env python3
"""Convert a structured markdown 'researcher output' into the JSON files
the Provocateur Pipeline expects.

Source format: a markdown file with the structure of the WBBF Athens
seed documents (themes_more_than_human_democracy-2.md, themes_wbbf_athens_2026_programme.md):

    # Researcher Output — <session/source name>
    **Session id:** `<session_id>`
    ...
    ## Theme N — <theme title>
    **Abstract.** <theme abstract paragraph>
    ### Cluster N.M — <cluster title>
    - `<extraction_id>` [<source bracket>] <extraction text>
    - ...

Output: writes three JSON files under <run_dir>/02_researcher/:
- grouping.json     — themes[] → clusters[] → extraction_ids[]
- clusters.json     — flat clusters[] mirror (Provocateur reads grouping.json,
                       but downstream tooling sometimes reads this directly)
- all_extractions.json — list of extraction dicts

Defaults applied to missing fields:
- lens:        "assertion" (Provocateur tolerates any string; only used as
                tag in formulation prompts)
- engagement:  "reinforced"
- responds_to: null
- energy:      "normal"
- session:     extracted from the bracketed source if present, else the
                document's `Session id` header

ID conversion:
- Theme headers "## Theme N — <title>" → theme_id "theme_<NNN>" (zero-padded)
- Cluster headers "### Cluster N.M — <title>" → cluster_id "cluster_<NNN>"
  (re-numbered globally across the document, NOT preserving N.M in the id)
- Extraction ids "`mthd:001`" / "`wbbf:001`" → kept as-is (Provocateur is
  content-agnostic on extraction id format; session_prefix:NNN is the
  natural shape)

Cluster abstracts: if the cluster section has its own paragraph before
the bullet list, that's used as the abstract. Otherwise we synthesize
a one-line abstract from the cluster title alone.

CLI:

    python runtime/scripts/markdown_to_researcher_output.py \\
        <input_markdown> <output_run_dir> \\
        [--session-id <id>]    # override doc-level session id
        [--dry-run]             # print preview, don't write

Example:

    python runtime/scripts/markdown_to_researcher_output.py \\
        ~/Desktop/themes_more_than_human_democracy-2.md \\
        $AI_ASSEMBLY_PROJECT_ROOT/runs/<run_dir>
    # (the original Athens-pre-conference dryrun was at
    # runs/_archive/ai_democracy_marathon_opening_2026_05_06/ — moved 2026-06-02)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path


# Regexes for the markdown structure.
_RE_THEME       = re.compile(r"^## Theme (\d+)\s+[—\-]\s+(.+?)\s*$", re.MULTILINE)
_RE_CLUSTER     = re.compile(r"^### Cluster\s+([\d.]+)\s+[—\-]\s+(.+?)\s*$", re.MULTILINE)
_RE_ABSTRACT    = re.compile(r"^\*\*Abstract\.\*\*\s*(.+?)(?=\n\n|\n###|\n##|\Z)", re.MULTILINE | re.DOTALL)
_RE_EXTRACTION  = re.compile(
    r"^- `([^`]+)`\s*\[([^\]]+)\]\s*(.+?)(?=\n- `|\n###|\n##|\Z)",
    re.MULTILINE | re.DOTALL,
)
_RE_SESSION_ID  = re.compile(r"\*\*Session id:\*\*\s*`([^`]+)`")
_RE_SOURCE_NAME = re.compile(r"\*\*Source:\*\*\s*(.+?)$", re.MULTILINE)


@dataclass
class Extraction:
    id: str
    bracket: str       # raw source bracket text e.g. "Round 1 · Nicole Miller, CEO Biomimicry 3.8"
    text: str          # extraction text body
    cluster_id: str = ""

    def to_dict(self, default_session: str) -> dict:
        speaker, session, context = _parse_bracket(self.bracket, default_session)
        # Distinguish lens by superficial form. Default assertion.
        lens = "assertion"
        if self.text.rstrip().endswith("?") or "?" in self.text[-120:]:
            lens = "open question"
        elif "reframe" in self.text.lower() or "reframing" in self.text.lower():
            lens = "reframing"
        return {
            "id":           self.id,
            "session":      session,
            "speaker":      speaker,
            "lens":         lens,
            "extraction":   self.text.strip(),
            "context":      context,
            "engagement":   "reinforced",
            "responds_to":  None,
            "energy":       "normal",
        }


@dataclass
class Cluster:
    id: str
    title: str
    abstract: str
    extractions: list[Extraction] = field(default_factory=list)


@dataclass
class Theme:
    id: str
    title: str
    abstract: str
    clusters: list[Cluster] = field(default_factory=list)


_RE_TIMECODE = re.compile(r"^\s*Day\s+(One|Two|Three|Zero|Four)\s+\d", re.IGNORECASE)
_RE_ROUND    = re.compile(r"^\s*(Round|Act|Final\s+vote)", re.IGNORECASE)
_RE_TIMERANGE = re.compile(r"\d{1,2}:\d{2}")
_RE_NAMELIKE  = re.compile(r"^[A-ZŠČĆŽÄÖÜÉÈÊÍÓÚÑ][a-zšćčžáéíóúýöüäñĒēĀāĪīŌōŪū'’\-\.]+(?:\s+[A-ZŠČĆŽÄÖÜÉÈÊÍÓÚÑ][a-zšćčžáéíóúýöüäñĒēĀāĪīŌōŪū'’\-\.]+)+")


def _looks_like_marker(s: str) -> bool:
    """Round/Act/Day-time/track-name brackets — NOT speakers."""
    s = s.strip().lstrip("*").rstrip("*")
    if not s:
        return True
    if _RE_TIMECODE.match(s) or _RE_ROUND.match(s) or _RE_TIMERANGE.search(s):
        return True
    # Italic-wrapped session title like *Four Pillars of the Life-Centered Economy*
    if s.startswith("*") and s.endswith("*"):
        return True
    # Multi-day patterns like "Day Two and Day Three"
    if re.search(r"\bDay\s+(One|Two|Three|Zero|Four).+\bDay\s+(One|Two|Three|Zero|Four)\b", s, re.IGNORECASE):
        return True
    # Track names — capitalized phrase ending in track-y words
    if any(s.endswith(w) for w in (" Stage", " Salon", " Agora", " Lab", " Care",
                                    " Depth", " Regeneration", " Belonging",
                                    " Reenchantment", " Marathon", " Activations",
                                    " Community", "Special Activations")):
        return True
    return False


def _strip_parenthetical(name: str) -> tuple[str, str]:
    """Pull parenthetical affiliation out of a name.
    'Gianni Giacomelli (MIT Collective Intelligence Design Lab)' →
    ('Gianni Giacomelli', 'MIT Collective Intelligence Design Lab').
    Tolerates unbalanced parens — strips trailing '(foo' too.
    """
    m = re.match(r"^(.+?)\s*\(([^)]*)\)?\s*$", name)
    if m:
        return m.group(1).strip(), (m.group(2) or "").strip()
    return name.strip(), ""


def _looks_like_speaker(s: str) -> bool:
    """Name-shaped strings — capital first letters, ≥2 words, may have comma + affiliation."""
    s = s.strip()
    if not s or _looks_like_marker(s):
        return False
    head = s.split(",")[0].strip()
    head, _ = _strip_parenthetical(head)
    return bool(_RE_NAMELIKE.match(head))


def _parse_bracket(bracket: str, default_session: str) -> tuple[str, str, str]:
    """Parse one extraction's source bracket into (speaker, session, context).

    Two source formats observed:
    - mthd-style: '[Round 1 · Nicole Miller, CEO Biomimicry 3.8]' or
                  '[Round 1 · Nicole Miller — host-written brief]'
                  → speaker is the SECOND part; first is session marker
    - wbbf-style: '[Ministry of Regeneration · Day One 11:00 · *Four Pillars*]' or
                  '[Bureau of Care · Day Three 14:00 · *Beauty Diplomacy* · Moulsari Jain]'
                  → speaker is the LAST part if it looks name-like; many
                    wbbf brackets have no explicit speaker

    Strategy: split on ' · ', mark each part as marker / speaker / other.
    First name-like part is the speaker; non-speaker parts feed session +
    context. Robust to either source format.
    """
    parts = [p.strip() for p in re.split(r"\s+[·∙•]\s+", bracket.strip()) if p.strip()]
    if not parts:
        return ("", default_session, "")
    speaker = ""
    other_parts = []
    for p in parts:
        if not speaker and _looks_like_speaker(p):
            # Speaker often has affiliation after first comma — keep
            # name as speaker, fold affiliation into context.
            head, _, tail = p.partition(",")
            speaker = head.strip()
            # Strip parenthetical affiliation (e.g. "Mike Peng (IDEO CEO)")
            speaker, paren_tail = _strip_parenthetical(speaker)
            if paren_tail:
                tail = paren_tail + ("; " + tail.strip() if tail.strip() else "")
            # Promote anything after em-dash into context too.
            if " — " in speaker:
                speaker, _, em_tail = speaker.partition(" — ")
                speaker = speaker.strip()
                if em_tail.strip():
                    tail = (em_tail.strip()
                            + ("; " + tail.strip() if tail.strip() else ""))
            if tail.strip():
                other_parts.append(tail.strip())
        else:
            other_parts.append(p)
    # Build session: prefix with default_session and join non-speaker parts
    # of the bracket as session-marker context.
    bracket_marker = " · ".join(other_parts).strip()
    session = (f"{default_session} — {bracket_marker}"
               if default_session and bracket_marker
               else (default_session or bracket_marker))
    return (speaker, session, bracket_marker)


def parse_markdown(text: str) -> tuple[list[Theme], str, str]:
    """Walk the markdown and return (themes[], default_session, source_name)."""
    session_id_m = _RE_SESSION_ID.search(text)
    source_m = _RE_SOURCE_NAME.search(text)
    default_session = (source_m.group(1).strip() if source_m
                       else (session_id_m.group(1) if session_id_m else "session"))

    themes: list[Theme] = []
    cluster_counter = 0  # global cluster numbering across themes

    # Find theme headers + their byte ranges
    theme_matches = list(_RE_THEME.finditer(text))
    for i, tm in enumerate(theme_matches):
        theme_num = int(tm.group(1))
        theme_title = tm.group(2).strip()
        theme_id = f"theme_{theme_num:03d}"
        # Slice this theme's section
        start = tm.end()
        end = theme_matches[i + 1].start() if i + 1 < len(theme_matches) else len(text)
        section = text[start:end]

        # Theme abstract: the first **Abstract.** paragraph in the section
        ab_m = _RE_ABSTRACT.search(section)
        theme_abstract = ab_m.group(1).strip().replace("\n", " ") if ab_m else ""

        theme = Theme(id=theme_id, title=theme_title, abstract=theme_abstract)

        # Find clusters within this theme section
        cluster_matches = list(_RE_CLUSTER.finditer(section))
        for j, cm in enumerate(cluster_matches):
            cluster_counter += 1
            cluster_label = cm.group(1)
            cluster_title = cm.group(2).strip()
            cluster_id = f"cluster_{cluster_counter:03d}"
            c_start = cm.end()
            c_end = cluster_matches[j + 1].start() if j + 1 < len(cluster_matches) else len(section)
            cluster_section = section[c_start:c_end]

            # Cluster abstract: first paragraph before the bullet list
            cluster_abstract = ""
            pre_bullet = cluster_section.split("\n- ", 1)[0].strip()
            if pre_bullet and not pre_bullet.startswith("- "):
                cluster_abstract = pre_bullet.replace("\n", " ").strip()
            if not cluster_abstract:
                cluster_abstract = (f"Cluster {cluster_label} of theme {theme_num}: "
                                    f"{cluster_title.lower()}.")

            cluster = Cluster(id=cluster_id, title=cluster_title, abstract=cluster_abstract)

            # Find extractions within this cluster
            for em in _RE_EXTRACTION.finditer(cluster_section):
                ext = Extraction(
                    id=em.group(1).strip(),
                    bracket=em.group(2).strip(),
                    text=em.group(3).strip(),
                    cluster_id=cluster_id,
                )
                cluster.extractions.append(ext)

            theme.clusters.append(cluster)

        themes.append(theme)

    return themes, default_session, (source_m.group(1).strip() if source_m else "")


def build_outputs(themes: list[Theme], default_session: str) -> dict[str, object]:
    """Build the three Researcher output JSON payloads."""
    grouping_themes = []
    flat_clusters = []
    all_extractions = []

    for t in themes:
        grouping_clusters = []
        for c in t.clusters:
            extraction_ids = [e.id for e in c.extractions]
            cluster_payload = {
                "cluster_id":       c.id,
                "cluster_title":    c.title,
                "cluster_abstract": c.abstract,
                "extraction_ids":   extraction_ids,
            }
            grouping_clusters.append(cluster_payload)
            flat_clusters.append(cluster_payload)
            for e in c.extractions:
                all_extractions.append(e.to_dict(default_session))

        grouping_themes.append({
            "theme_id":  t.id,
            "title":     t.title,
            "abstract":  t.abstract,
            "clusters":  grouping_clusters,
        })

    return {
        "grouping":        {"themes": grouping_themes, "isolates": []},
        "clusters":        {"clusters": flat_clusters, "isolates": []},
        "all_extractions": all_extractions,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("input_markdown", type=Path, help="Source markdown file")
    ap.add_argument("output_run_dir", type=Path, help="Run directory to write 02_researcher/ under")
    ap.add_argument("--session-id", default=None,
                    help="Override the doc-level session name passed into per-extraction `session`")
    ap.add_argument("--dry-run", action="store_true",
                    help="Print summary, don't write files")
    args = ap.parse_args(argv)

    if not args.input_markdown.exists():
        print(f"ERROR: input not found: {args.input_markdown}", file=sys.stderr)
        return 2

    text = args.input_markdown.read_text(encoding="utf-8")
    themes, default_session, source_name = parse_markdown(text)
    if args.session_id:
        default_session = args.session_id

    payload = build_outputs(themes, default_session)

    n_themes = len(payload["grouping"]["themes"])
    n_clusters = len(payload["clusters"]["clusters"])
    n_extractions = len(payload["all_extractions"])
    print(f"Parsed {args.input_markdown.name}:")
    print(f"  source: {source_name or '(unknown)'}")
    print(f"  default_session for extractions: {default_session}")
    print(f"  themes:      {n_themes}")
    print(f"  clusters:    {n_clusters}")
    print(f"  extractions: {n_extractions}")
    for t in payload["grouping"]["themes"]:
        print(f"    {t['theme_id']}: {t['title']}  ({len(t['clusters'])} clusters)")
    if args.dry_run:
        print("\n--dry-run: not writing files")
        return 0

    out_dir = args.output_run_dir / "02_researcher"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "grouping.json").write_text(
        json.dumps(payload["grouping"], indent=2, ensure_ascii=False), encoding="utf-8")
    (out_dir / "clusters.json").write_text(
        json.dumps(payload["clusters"], indent=2, ensure_ascii=False), encoding="utf-8")
    (out_dir / "all_extractions.json").write_text(
        json.dumps(payload["all_extractions"], indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nWrote 3 files under {out_dir}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
