"""Tests for the Pass 0b tailor splicer.

Covers the deterministic injection splicing introduced 2026-04-24 to fix
the Plato regression where LLM-owned full-prompt tailoring dropped
canonical Fix #34 bullets. New architecture: LLM emits structured
injections; Python splices. These tests pin that Python contract.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Adjust path so tests find run_pass_0b_tailor module
_PERSONAS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_PERSONAS))

from run_pass_0b_tailor import (
    _format_questions_block,
    splice_injections,
)


# ── fixtures ────────────────────────────────────────────────────────────────

_BASE_PROMPT_6_PLACEHOLDERS = """# DR Prompt Intro

Intro paragraph for the voice.

## Section 1: BIOGRAPHICAL FOUNDATION

<!-- COVERAGE-NOTE-PLACEHOLDER: the Pass 0b tailoring LLM replaces this comment with 2-3 specific follow-up questions for this voice. -->

Canonical §1 thematic ask A.

Canonical §1 thematic ask B.

---

## Section 2: INTELLECTUAL FRAMEWORK

<!-- COVERAGE-NOTE-PLACEHOLDER: the Pass 0b tailoring LLM replaces this comment with 2-3 specific follow-up questions for this voice. -->

Canonical §2 thematic ask.

---

## Section 3: REASONING PATTERNS

<!-- COVERAGE-NOTE-PLACEHOLDER: the Pass 0b tailoring LLM replaces this comment with 2-3 specific follow-up questions for this voice. -->

Canonical §3 thematic ask.

---

## Section 4: VOICE AND STYLE

**THE SWAP TEST.** Before committing to any voice characterisation, test whether reattribution is plausible.

<!-- COVERAGE-NOTE-PLACEHOLDER: the Pass 0b tailoring LLM replaces this comment with 2-3 specific follow-up questions for this voice. -->

Canonical §4 thematic ask.

---

## Section 5: HISTORICAL + CONCEPTUAL BOUNDARIES

<!-- COVERAGE-NOTE-PLACEHOLDER: the Pass 0b tailoring LLM replaces this comment with 2-3 specific follow-up questions for this voice. -->

Canonical §5 thematic ask.

---

## Section 6: PRIMARY TEXTS

<!-- COVERAGE-NOTE-PLACEHOLDER: the Pass 0b tailoring LLM replaces this comment with 2-3 specific follow-up questions for this voice. -->

Canonical §6 thematic ask.
"""


def _valid_injections() -> dict[str, list[str]]:
    """A valid section_injections dict with 2-3 questions per section."""
    return {
        "1": ["§1 Q1 about formative events.", "§1 Q2 about intellectual world.", "§1 Q3 about character-grammar."],
        "2": ["§2 Q1 about commitments.", "§2 Q2 about concepts."],
        "3": ["§3 Q1 about reasoning method.", "§3 Q2 about named structural units.", "§3 Q3 about evidence."],
        "4": ["§4 Q1 about rhetorical signatures.", "§4 Q2 about translator verdicts.", "§4 Q3 about register."],
        "5": ["§5 Q1 about retrospective-framing traps.", "§5 Q2 about imperial frame."],
        "6": ["§6 Q1 about primary text URLs.", "§6 Q2 about passage candidates.", "§6 Q3 about translator verdicts."],
    }


# ── _format_questions_block ─────────────────────────────────────────────────

def test_format_questions_block_three_questions():
    """Three questions render as numbered list with header."""
    block = _format_questions_block(["Q1.", "Q2.", "Q3."])
    assert "**Voice-specific follow-up questions for this section**" in block
    assert "1. Q1." in block
    assert "2. Q2." in block
    assert "3. Q3." in block


def test_format_questions_block_two_questions():
    """Two questions is also valid (per Block 3 '2-3 per section')."""
    block = _format_questions_block(["Q1.", "Q2."])
    assert "1. Q1." in block
    assert "2. Q2." in block
    assert "3." not in block


def test_format_questions_block_empty_raises():
    """Empty list is an error — enforces 'at least 2' invariant upstream."""
    with pytest.raises(ValueError):
        _format_questions_block([])


def test_format_questions_block_strips_whitespace():
    """Leading/trailing whitespace on questions is trimmed in rendering."""
    block = _format_questions_block(["  Q1 with padding.  ", "Q2."])
    assert "1. Q1 with padding." in block
    # Padding should be gone
    assert "  Q1 " not in block


# ── splice_injections happy paths ───────────────────────────────────────────

def test_splice_all_six_placeholders_replaced():
    """All 6 COVERAGE-NOTE-PLACEHOLDER comments are replaced; none remain."""
    result = splice_injections(_BASE_PROMPT_6_PLACEHOLDERS, _valid_injections())
    assert "COVERAGE-NOTE-PLACEHOLDER" not in result


def test_splice_preserves_canonical_content():
    """Base canonical Fix #34 content remains verbatim — the whole point of this fix."""
    result = splice_injections(_BASE_PROMPT_6_PLACEHOLDERS, _valid_injections())
    # Every canonical thematic ask from the base must survive
    for marker in [
        "Canonical §1 thematic ask A.",
        "Canonical §1 thematic ask B.",
        "Canonical §2 thematic ask.",
        "Canonical §3 thematic ask.",
        "Canonical §4 thematic ask.",
        "Canonical §5 thematic ask.",
        "Canonical §6 thematic ask.",
    ]:
        assert marker in result, f"Canonical content missing after splice: {marker}"


def test_splice_preserves_section_headings():
    """All 6 '## Section N:' headings survive, in order."""
    result = splice_injections(_BASE_PROMPT_6_PLACEHOLDERS, _valid_injections())
    for n, title in enumerate(
        ["BIOGRAPHICAL FOUNDATION", "INTELLECTUAL FRAMEWORK", "REASONING PATTERNS",
         "VOICE AND STYLE", "HISTORICAL + CONCEPTUAL BOUNDARIES", "PRIMARY TEXTS"], start=1
    ):
        assert f"## Section {n}: {title}" in result


def test_splice_places_injections_in_correct_sections():
    """§1 questions appear before §2 heading, §2 before §3, etc. — order preserved."""
    result = splice_injections(_BASE_PROMPT_6_PLACEHOLDERS, _valid_injections())
    sec1_idx = result.index("## Section 1:")
    sec2_idx = result.index("## Section 2:")
    sec3_idx = result.index("## Section 3:")
    # §1 Q3 is placed between §1 heading and §2 heading
    q1_idx = result.index("§1 Q3 about character-grammar.")
    assert sec1_idx < q1_idx < sec2_idx
    # §2 Q2 is between §2 and §3
    q2_idx = result.index("§2 Q2 about concepts.")
    assert sec2_idx < q2_idx < sec3_idx


def test_splice_output_larger_than_base():
    """Splicing ADDS content — tailored output is strictly larger than base."""
    base = _BASE_PROMPT_6_PLACEHOLDERS
    result = splice_injections(base, _valid_injections())
    assert len(result) > len(base), (
        f"Splice should grow base, got {len(result)} vs base {len(base)}"
    )


# ── splice_injections optional features ─────────────────────────────────────

def test_splice_swap_test_anchor_appended():
    """swap_test_anchor is inserted after §4's THE SWAP TEST paragraph."""
    anchor = "**For this voice, the specific SWAP TEST neighbours are:** Aristotle; Xenophon."
    result = splice_injections(
        _BASE_PROMPT_6_PLACEHOLDERS,
        _valid_injections(),
        swap_test_anchor=anchor,
    )
    assert "specific SWAP TEST neighbours are:" in result
    # Anchor must appear AFTER the generic SWAP TEST paragraph
    swap_intro_idx = result.index("**THE SWAP TEST.**")
    anchor_idx = result.index("specific SWAP TEST neighbours are:")
    assert swap_intro_idx < anchor_idx
    # And BEFORE §4's placeholder replacement (the voice-specific Qs)
    q4_idx = result.index("§4 Q1 about rhetorical signatures.")
    assert anchor_idx < q4_idx


def test_splice_no_swap_test_anchor_when_null():
    """swap_test_anchor=None leaves base SWAP TEST paragraph untouched."""
    result = splice_injections(
        _BASE_PROMPT_6_PLACEHOLDERS,
        _valid_injections(),
        swap_test_anchor=None,
    )
    assert "specific SWAP TEST neighbours are:" not in result


def test_splice_thematic_note_prepended():
    """thematic_note is inserted before §1 heading."""
    note = "Foreground the voice's engagement with deliberation under uncertainty."
    result = splice_injections(
        _BASE_PROMPT_6_PLACEHOLDERS,
        _valid_injections(),
        thematic_note=note,
    )
    assert "Curator thematic emphasis:" in result
    note_idx = result.index("Curator thematic emphasis:")
    sec1_idx = result.index("## Section 1:")
    assert note_idx < sec1_idx


def test_splice_no_thematic_note_when_null():
    """thematic_note=None leaves prompt intro clean."""
    result = splice_injections(
        _BASE_PROMPT_6_PLACEHOLDERS,
        _valid_injections(),
        thematic_note=None,
    )
    assert "Curator thematic emphasis:" not in result


# ── splice_injections error paths ───────────────────────────────────────────

def test_splice_wrong_placeholder_count_raises():
    """Base with != 6 placeholders raises ValueError."""
    base_missing_one = _BASE_PROMPT_6_PLACEHOLDERS.replace(
        "<!-- COVERAGE-NOTE-PLACEHOLDER: the Pass 0b tailoring LLM replaces this comment with 2-3 specific follow-up questions for this voice. -->",
        "<!-- missing -->",
        1,  # replace only the first
    )
    with pytest.raises(ValueError, match="exactly 6"):
        splice_injections(base_missing_one, _valid_injections())


def test_splice_missing_section_key_raises():
    """Injections dict missing a section key raises ValueError."""
    injections = _valid_injections()
    del injections["3"]
    with pytest.raises(ValueError, match="missing required key"):
        splice_injections(_BASE_PROMPT_6_PLACEHOLDERS, injections)


def test_splice_empty_section_raises():
    """Injections dict with an empty list for a section raises ValueError."""
    injections = _valid_injections()
    injections["5"] = []
    with pytest.raises(ValueError, match="non-empty"):
        splice_injections(_BASE_PROMPT_6_PLACEHOLDERS, injections)


def test_splice_non_list_section_raises():
    """Injections dict with non-list value for a section raises ValueError."""
    injections = _valid_injections()
    injections["2"] = "not a list"
    with pytest.raises(ValueError, match="non-empty list"):
        splice_injections(_BASE_PROMPT_6_PLACEHOLDERS, injections)


# ── regression test — the Plato failure mode ────────────────────────────────

def test_splice_prevents_plato_regression():
    """Regression test for the Plato failure mode.

    Old architecture: LLM returned a 'complete tailored DR prompt' that dropped
    canonical Fix #34 bullets. Plato's tailored output was 17KB vs 26KB base
    (34% smaller). New architecture: LLM returns injections only; Python
    splices. Tailored MUST be larger than base + canonical content MUST survive.

    If this test ever fails, the tailor has regressed to the old failure
    mode and canonical bullets are being lost.
    """
    base = _BASE_PROMPT_6_PLACEHOLDERS
    result = splice_injections(base, _valid_injections())

    # Size invariant: tailored > base (Plato had tailored < base)
    assert len(result) > len(base), (
        "Tailored output shorter than base — regressed to Plato failure mode"
    )

    # Canonical preservation: every base line without a placeholder comment
    # still appears verbatim in output
    base_canonical_lines = [
        line for line in base.splitlines()
        if line.strip() and "COVERAGE-NOTE-PLACEHOLDER" not in line
    ]
    for line in base_canonical_lines:
        assert line in result, (
            f"Canonical base line lost after splice: {line!r}"
        )
