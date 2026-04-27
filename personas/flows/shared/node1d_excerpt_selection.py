"""Pass 1d — Excerpt Selection (Claude).

Replaces the naive first-80K-character slice with a curated subset chosen by
Claude reading the dossier (which already names the most important works /
passages) plus a structural index of each fetched source.

Input: list of {url, source, text, char_count} from Node 1c, plus the dossier.
Output: list of {url, char_start, char_end, why, label} totalling ~30K chars.

Used by Pass 4a (Voice) and Pass 6 (Corpus Curation) as the basis for
`{{primary_texts}}`.
"""
from __future__ import annotations
import json
from typing import Any

INDEX_CHUNK_SIZE = 5000
# 1d-01: 400 chars (up from 200) — mid-chapter chunks need content context,
# not just genre/register, for Sonnet to resolve structural-ref→char-range.
INDEX_PEEK_CHARS = 400
TARGET_TOTAL_CHARS = 30000

# 1d-02: paragraph-snap window — how far to search for a \\n\\n boundary.
_SNAP_WINDOW = 500


def _snap_to_paragraph(text: str, pos: int, forward: bool) -> int:
    """Snap pos to the nearest paragraph break (double newline).

    forward=True: snap char_end rightward to paragraph end.
    forward=False: snap char_start leftward to paragraph start.
    Falls back to original pos if no paragraph break found within _SNAP_WINDOW.
    """
    if forward:
        idx = text.find("\n\n", pos, pos + _SNAP_WINDOW)
        return idx + 2 if idx != -1 else pos
    else:
        idx = text.rfind("\n\n", max(0, pos - _SNAP_WINDOW), pos)
        return idx + 2 if idx != -1 else pos


def build_structural_index(passages: list[dict[str, Any]]) -> str:
    """Build a peek-index: every 5K chars of every source, show first 400 chars.
    The selector reads this to choose char_start/char_end ranges."""
    out_parts: list[str] = []
    for p in passages:
        if not p.get("text"):
            continue
        text = p["text"]
        out_parts.append(f"\n=== SOURCE: {p['url']} ({p['char_count']:,} chars) ===")
        for start in range(0, len(text), INDEX_CHUNK_SIZE):
            end = min(start + INDEX_CHUNK_SIZE, len(text))
            peek = text[start:start + INDEX_PEEK_CHARS].replace("\n", " ")
            out_parts.append(f"  [chars {start:>7,}-{end:>7,}]: {peek}...")
    return "\n".join(out_parts)


def apply_selections(passages: list[dict[str, Any]], selections: list[dict]) -> str:
    """Take selector output (list of {url, char_start, char_end, label, why})
    and produce the concatenated primary_texts block.

    Applies paragraph boundary-snapping (1d-02): char_start snaps back to
    the nearest \\n\\n; char_end snaps forward. Prevents mid-sentence splits
    that degrade voice-analysis input at Pass 4a.
    """
    by_url = {p["url"]: p for p in passages}
    parts: list[str] = []
    for sel in selections:
        p = by_url.get(sel["url"])
        if not p or not p.get("text"):
            continue
        full_text = p["text"]
        char_start = _snap_to_paragraph(full_text, sel["char_start"], forward=False)
        char_end = _snap_to_paragraph(full_text, sel["char_end"], forward=True)
        char_end = min(char_end, len(full_text))
        text = full_text[char_start:char_end]
        header = f"=== {sel.get('label', sel['url'])} ({char_start:,}-{char_end:,}) ==="
        why = sel.get("why", "")
        parts.append(f"{header}\n[Why selected: {why}]\n\n{text}")
    return "\n\n".join(parts) if parts else "[NO SELECTIONS]"
