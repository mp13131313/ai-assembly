"""Split Perplexity's 6-section dossier text into a dict keyed by section number."""
from __future__ import annotations
import re

# Section heading patterns — matches same alternatives validate_dr_dossier uses
_SECTION_PATTERNS = [
    (1, re.compile(r"^#+\s*1\.\s*(BIOGRAPHICAL|BIOLOGICAL|TEXTUAL|ECOLOGICAL|SYSTEMIC) FOUNDATION\b", re.MULTILINE | re.IGNORECASE)),
    (2, re.compile(r"^#+\s*2\.\s*(INTELLECTUAL FRAMEWORK|PERCEPTUAL WORLD|SYSTEMIC PROPERTIES|CHARACTER AS INTELLECTUAL CONSTRUCT)\b", re.MULTILINE | re.IGNORECASE)),
    (3, re.compile(r"^#+\s*3\.\s*(REASONING PATTERNS|RELATIONAL PATTERNS|NARRATIVE STRATEGY)\b", re.MULTILINE | re.IGNORECASE)),
    (4, re.compile(r"^#+\s*4\.\s*VOICE AND STYLE\b|^#+\s*4\.\s*SCIENTIFIC LITERATURE\b", re.MULTILINE | re.IGNORECASE)),
    (5, re.compile(r"^#+\s*5\.\s*(HISTORICAL BOUNDARIES|ONTOLOGICAL BOUNDARIES|PHILOSOPHICAL AND LEGAL FRAMEWORKS)\b", re.MULTILINE | re.IGNORECASE)),
    (6, re.compile(r"^#+\s*6\.\s*(PRIMARY TEXTS|PRIMARY SCIENTIFIC LITERATURE|PRIMARY DOCUMENTS|RECEPTION AND INFLUENCE)\b", re.MULTILINE | re.IGNORECASE)),
]


def split_dossier(text: str) -> dict[int, str] | None:
    """Split a 6-section Perplexity dossier into {section_number: content} dict.

    Returns None if fewer than 6 sections are recognizable (caller falls back
    to single-block scaffolding).
    """
    # Find all section boundary positions
    boundaries = []
    for section_num, pattern in _SECTION_PATTERNS:
        match = pattern.search(text)
        if match is None:
            return None  # section missing — fallback
        boundaries.append((section_num, match.start()))

    # Sort by position to get true order
    boundaries.sort(key=lambda b: b[1])

    if len(boundaries) != 6:
        return None

    # Split text at each boundary; each section runs from its start to the next
    sections = {}
    for i, (section_num, start) in enumerate(boundaries):
        end = boundaries[i + 1][1] if i + 1 < len(boundaries) else len(text)
        sections[section_num] = text[start:end].strip()

    return sections
