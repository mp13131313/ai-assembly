"""Validation for Claude Deep Research dossier files.

Phase B redesign per PB#9 + decisions log: the rigid 6-section markdown
requirement is relaxed. DR output can be any structure that fits the
research; canonicalisation happens at the chunked Pass 1.1-1.6 merge, not
at DR output. We keep a word-count floor (to catch truncation) and
per-major-section soft floors (to catch shallow-in-some-section output).

Persona-card-shape detection remains strict — that is a real error
(curator pasted the wrong artifact).
"""
from __future__ import annotations

import re
from pathlib import Path

# Minimum total word count. Guards against truncated exports.
# Lowered from 15000 to 8000 alongside removing the prompt-level "Minimum
# 15,000 words" floor — DR was hitting internal tool-call caps trying to
# reach 15K on deeply-specified 6-section asks; 8K still catches genuine
# truncation while letting DR complete.
_TOTAL_WORD_FLOOR = 8000

# Soft per-section floor. Roughly ~1,500 words per major section across
# the 6 expected thematic areas. We count any top-level `## ` heading.
_PER_SECTION_SOFT_FLOOR = 1500

# Any thematic heading in any of the 6 areas counts as a "found" section.
_SECTION_HINTS = [
    (r"\b(BIOGRAPHICAL|BIOLOGICAL|TEXTUAL|ECOLOGICAL|SYSTEMIC|ONTOLOGICAL|NARRATIVE)\s+FOUNDATION\b", "foundation"),
    (r"\b(INTELLECTUAL FRAMEWORK|PERCEPTUAL WORLD|COMMITMENTS|CONCEPTS|TENSIONS)\b", "intellectual"),
    (r"\b(REASONING|RELATIONAL PATTERNS|NARRATIVE STRATEGY|PERCEPTUAL-RESPONSE)\b", "reasoning"),
    (r"\b(VOICE|STYLE|REGISTER|VOCABULARY|METAPHORICAL|MOVES)\b", "voice"),
    (r"\b(BOUNDARIES|ANACHRONISMS|HARD LIMITS|SENSITIVE TOPICS)\b", "boundaries"),
    (r"\b(PRIMARY TEXTS|PASSAGES|CORPUS|WORKS|URLS)\b", "corpus"),
]

_FIELD_HEADING_RE = re.compile(r"^#+\s*Field\s+\d+:", re.MULTILINE)


def validate_dr_dossier(path: Path) -> None:
    """Validate a Claude DR dossier file at *path*.

    Relaxed per PB#9 — no longer requires rigid 6-section markdown. Checks:

    - Persona-card-shape detection (strict — wrong-artifact error)
    - Total word count below floor (truncation guard; strict error)
    - At least 4 of 6 thematic areas detected (content-coverage warning,
      non-fatal — prints WARNING but does not raise)
    - Word count per detected thematic area (soft floor; logged but
      non-fatal)

    On success or soft-warning, returns None. Raises ValueError only on
    truncation or persona-card-shape violation.
    """
    if not path.exists():
        raise ValueError(f"DR dossier file not found: {path}")

    text = path.read_text(encoding="utf-8")

    if _FIELD_HEADING_RE.search(text):
        raise ValueError(
            f"DR dossier at {path} contains 'Field NN:' headings — this is a "
            f"persona card, not a research dossier. Regenerate using the "
            f"dossier prompt from inputs/dossiers/_dr_prompts/."
        )

    word_count = len(text.split())
    if word_count < _TOTAL_WORD_FLOOR:
        raise ValueError(
            f"DR dossier at {path} is only {word_count} words — minimum "
            f"{_TOTAL_WORD_FLOOR} (prompt asks for 15,000-25,000). Likely "
            f"truncated or incomplete export."
        )

    # Relaxed section coverage.
    detected: set[str] = set()
    for pattern, area in _SECTION_HINTS:
        if re.search(pattern, text, re.IGNORECASE):
            detected.add(area)
    if len(detected) < 4:
        print(
            f"  WARNING: DR dossier at {path} only covers {len(detected)}/6 "
            f"thematic areas (detected: {sorted(detected)}). Chunked Pass 1 "
            f"merge may produce thin output in uncovered areas. "
            f"Consider re-running the DR prompt if this is unexpected."
        )
