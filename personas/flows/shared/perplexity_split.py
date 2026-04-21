"""Split Perplexity's 6-section dossier text into a dict keyed by section number."""
from __future__ import annotations
import re

# Section heading patterns — matches same alternatives validate_dr_dossier uses.
# Section-number prefix (e.g. "1.", "Section 1:") is optional: some research tools
# emit "## BIOGRAPHICAL FOUNDATION", others "## 1. BIOGRAPHICAL FOUNDATION",
# others "## Section 1: BIOGRAPHICAL FOUNDATION". All three should split cleanly.
_NUM_PREFIX = r"(?:(?:Section\s+)?\d+[\.:)]\s*)?"
_SECTION_PATTERNS = [
    (1, re.compile(rf"^#+\s*{_NUM_PREFIX}(BIOGRAPHICAL|BIOLOGICAL|TEXTUAL|ECOLOGICAL|SYSTEMIC) FOUNDATION\b", re.MULTILINE | re.IGNORECASE)),
    (2, re.compile(rf"^#+\s*{_NUM_PREFIX}(INTELLECTUAL FRAMEWORK|PERCEPTUAL WORLD|SYSTEMIC PROPERTIES|CHARACTER AS INTELLECTUAL CONSTRUCT)\b", re.MULTILINE | re.IGNORECASE)),
    (3, re.compile(rf"^#+\s*{_NUM_PREFIX}(REASONING PATTERNS|RELATIONAL PATTERNS|NARRATIVE STRATEGY)\b", re.MULTILINE | re.IGNORECASE)),
    (4, re.compile(rf"^#+\s*{_NUM_PREFIX}(VOICE AND STYLE|SCIENTIFIC LITERATURE)\b", re.MULTILINE | re.IGNORECASE)),
    # Section 5 heading variants: "HISTORICAL BOUNDARIES" (legacy),
    # "HISTORICAL + CONCEPTUAL BOUNDARIES" (Phase B human prompt), and the
    # non-human / fictional variants.
    (5, re.compile(rf"^#+\s*{_NUM_PREFIX}(HISTORICAL(?:\s*\+\s*CONCEPTUAL)? BOUNDARIES|ONTOLOGICAL BOUNDARIES|PHILOSOPHICAL AND LEGAL FRAMEWORKS)\b", re.MULTILINE | re.IGNORECASE)),
    (6, re.compile(rf"^#+\s*{_NUM_PREFIX}(PRIMARY TEXTS|PRIMARY SCIENTIFIC LITERATURE|PRIMARY DOCUMENTS|RECEPTION AND INFLUENCE)\b", re.MULTILINE | re.IGNORECASE)),
]


def split_dossier(text: str) -> dict[int, str]:
    """Split a 6-section Perplexity dossier into {section_number: content} dict.

    Returns whatever sections were recognized (1-6 keys). Returns empty dict
    if no section headings match. Callers fall back to full dossier for any
    missing keys rather than blocking on a complete parse.
    """
    # Find all section boundary positions for recognized sections
    boundaries = []
    for section_num, pattern in _SECTION_PATTERNS:
        match = pattern.search(text)
        if match is not None:
            boundaries.append((section_num, match.start()))

    if not boundaries:
        return {}

    # Sort by position to get true document order
    boundaries.sort(key=lambda b: b[1])

    # Split text at each boundary; each section runs from its start to the next
    sections = {}
    for i, (section_num, start) in enumerate(boundaries):
        end = boundaries[i + 1][1] if i + 1 < len(boundaries) else len(text)
        sections[section_num] = text[start:end].strip() + "\n"

    return sections
