"""Validation for Claude Deep Research dossier files.

Phase B redesign per PB#9 + decisions log: the rigid 6-section markdown
requirement is relaxed. DR output can be any structure that fits the
research; canonicalisation happens at the chunked Pass 1.1-1.6 merge, not
at DR output. We keep a word-count floor (to catch truncation) and
per-major-section soft floors (to catch shallow-in-some-section output).

Persona-card-shape detection remains strict — that is a real error
(curator pasted the wrong artifact).

Per-section mode: files named `NN_section_N.md` are validated independently
with a lower word-count floor (1,500 words). Directories are validated as
a set of 6 section files.
"""
from __future__ import annotations

import re
from pathlib import Path

# Minimum total word count for monolithic dossier. Guards against truncation.
_TOTAL_WORD_FLOOR = 8000

# Per-section word floor. Calibrated from empirical §1/§2 runs (~3,700-6,500 words).
_SECTION_WORD_FLOOR = 1500

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
_SECTION_FILE_RE = re.compile(r"^\d+_section_(\d+)\.md$")
_PROVENANCE_RE = re.compile(
    r"PROMPT_VERSION:[^|]+\|\s*VOICE_SLUG:\s*(\S+)\s*\|\s*SECTION:\s*(\d+)"
)


def _check_persona_card_shape(text: str, path: Path) -> None:
    if _FIELD_HEADING_RE.search(text):
        raise ValueError(
            f"DR dossier at {path} contains 'Field NN:' headings — this is a "
            f"persona card, not a research dossier. Regenerate using the "
            f"dossier prompt at <project_root>/inputs/dossiers/_dr_prompts/."
        )


def validate_section_dr_dossier(path: Path, expected_section: int | None = None) -> None:
    """Validate a single per-section DR dossier file.

    - Persona-card-shape detection (strict)
    - Word count floor: 1,500 words
    - Provenance header: if present, parse and warn on mismatch (non-fatal)
    """
    if not path.exists():
        raise ValueError(f"Section DR dossier not found: {path}")

    text = path.read_text(encoding="utf-8")
    _check_persona_card_shape(text, path)

    word_count = len(text.split())
    if word_count < _SECTION_WORD_FLOOR:
        raise ValueError(
            f"Section DR dossier at {path} is only {word_count} words — "
            f"minimum 1,500 per section. Likely truncated."
        )

    prov = _PROVENANCE_RE.search(text)
    if prov and expected_section is not None:
        found_section = int(prov.group(2))
        if found_section != expected_section:
            print(
                f"  WARNING: {path.name} provenance header says SECTION={found_section} "
                f"but expected section {expected_section}."
            )


def validate_dr_dossier_dir(directory: Path) -> None:
    """Validate a directory of 6 per-section DR dossier files.

    Reports which section files are missing. Validates each present file.
    """
    if not directory.is_dir():
        raise ValueError(f"Not a directory: {directory}")

    errors: list[str] = []
    for n in range(1, 7):
        candidates = sorted(directory.glob(f"*_section_{n}.md"))
        if not candidates:
            errors.append(f"  Section {n}: MISSING (no *_section_{n}.md in {directory})")
            continue
        path = candidates[0]
        try:
            validate_section_dr_dossier(path, expected_section=n)
            print(f"  Section {n}: VALID ({path.name})")
        except ValueError as e:
            errors.append(f"  Section {n}: INVALID — {e}")

    if errors:
        raise ValueError(
            f"DR dossier directory validation failed for {directory}:\n"
            + "\n".join(errors)
        )


def validate_dr_dossier(path: Path) -> None:
    """Validate a Claude DR dossier — auto-detects monolithic vs per-section.

    - Directory → validate as 6-section directory
    - File named `NN_section_N.md` → per-section validation (1,500-word floor)
    - Else → monolithic validation (8,000-word floor, existing behavior)

    Raises ValueError on hard failures. Prints WARNING for soft issues.
    """
    if path.is_dir():
        validate_dr_dossier_dir(path)
        return

    if not path.exists():
        raise ValueError(f"DR dossier file not found: {path}")

    m = _SECTION_FILE_RE.match(path.name)
    if m:
        validate_section_dr_dossier(path, expected_section=int(m.group(1)))
        return

    # Monolithic validation (original behavior).
    text = path.read_text(encoding="utf-8")
    _check_persona_card_shape(text, path)

    word_count = len(text.split())
    if word_count < _TOTAL_WORD_FLOOR:
        raise ValueError(
            f"DR dossier at {path} is only {word_count} words — minimum "
            f"{_TOTAL_WORD_FLOOR} (prompt asks for 15,000-25,000). Likely "
            f"truncated or incomplete export."
        )

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
