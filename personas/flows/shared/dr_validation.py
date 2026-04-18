"""Validation for Claude Deep Research dossier files.

Implements the six-section contract and word-count floor from CLAUDE_DR_BRIEFING.md.
Raises ValueError with a diagnostic message on any violation.
"""
from __future__ import annotations

import re
from pathlib import Path

_REQUIRED_HEADINGS = [
    r"^#+\s*1\.\s*(BIOGRAPHICAL|BIOLOGICAL|TEXTUAL|ECOLOGICAL|SYSTEMIC) FOUNDATION\b",
    r"^#+\s*2\.\s*(INTELLECTUAL FRAMEWORK|PERCEPTUAL WORLD|SYSTEMIC PROPERTIES|CHARACTER AS INTELLECTUAL CONSTRUCT)\b",
    r"^#+\s*3\.\s*(REASONING PATTERNS|RELATIONAL PATTERNS|NARRATIVE STRATEGY)\b",
    r"^#+\s*4\.\s*(VOICE AND STYLE|SCIENTIFIC LITERATURE)\b",
    r"^#+\s*5\.\s*(HISTORICAL BOUNDARIES|PHILOSOPHICAL AND LEGAL FRAMEWORKS|ONTOLOGICAL BOUNDARIES)\b",
    r"^#+\s*6\.\s*(PRIMARY TEXTS|PRIMARY SCIENTIFIC LITERATURE|PRIMARY DOCUMENTS|RECEPTION AND INFLUENCE)\b",
]

# Matches the "Minimum 15,000 words" instruction at the bottom of
# pass_0b_dr_prompt.md. A dossier below this is truncated or shallow.
_WORD_COUNT_FLOOR = 15000
_FIELD_HEADING_RE = re.compile(r"^#+\s*Field\s+\d+:", re.MULTILINE)


def validate_dr_dossier(path: Path) -> None:
    """Validate a Claude DR dossier file at *path*.

    Raises ValueError with a diagnostic message on any violation:
    - Missing any of the six required section headings
    - Word count below floor (15,000 words — indicates truncation)
    - Contains "Field NN:" headings (persona card shape, not a dossier)

    On success, returns None.
    """
    if not path.exists():
        raise ValueError(f"DR dossier file not found: {path}")

    text = path.read_text(encoding="utf-8")

    missing = [h for h in _REQUIRED_HEADINGS
               if not re.search(h, text, re.MULTILINE | re.IGNORECASE)]
    if missing:
        raise ValueError(
            f"DR dossier at {path} is missing expected section headings — "
            f"may be a persona card rather than a research dossier. "
            f"See inputs/dossiers/_archive/plato_claude_dr_v1_finished_card.md "
            f"for an example of the wrong shape, and CLAUDE_DR_BRIEFING.md "
            f"for the correct six-section structure."
        )

    word_count = len(text.split())
    if word_count < _WORD_COUNT_FLOOR:
        raise ValueError(
            f"DR dossier at {path} is only {word_count} words — minimum "
            f"15,000 (prompt asks for 15,000-25,000). Likely truncated or "
            f"incomplete export."
        )

    if _FIELD_HEADING_RE.search(text):
        raise ValueError(
            f"DR dossier at {path} contains 'Field NN:' headings — this is "
            f"a persona card, not a research dossier. Regenerate using the "
            f"dossier prompt from inputs/dossiers/_dr_prompts/."
        )
