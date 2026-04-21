"""Tests for flows/shared/perplexity_split.py."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from flows.shared.perplexity_split import split_dossier


_HEADINGS = [
    "## 1. BIOGRAPHICAL FOUNDATION",
    "## 2. INTELLECTUAL FRAMEWORK",
    "## 3. REASONING PATTERNS",
    "## 4. VOICE AND STYLE",
    "## 5. HISTORICAL + CONCEPTUAL BOUNDARIES",
    "## 6. PRIMARY TEXTS",
]

_FULL_DOSSIER = "\n\n".join(
    f"{h}\n\nContent for section {i+1}." for i, h in enumerate(_HEADINGS)
)


class TestSplitDossierFullSix:
    def test_returns_dict_with_six_keys(self):
        result = split_dossier(_FULL_DOSSIER)
        assert set(result.keys()) == {1, 2, 3, 4, 5, 6}

    def test_each_section_contains_its_heading(self):
        result = split_dossier(_FULL_DOSSIER)
        for i, h in enumerate(_HEADINGS):
            assert h in result[i + 1]

    def test_each_section_contains_its_content(self):
        result = split_dossier(_FULL_DOSSIER)
        for n in range(1, 7):
            assert f"Content for section {n}." in result[n]

    def test_section_does_not_bleed_into_next(self):
        result = split_dossier(_FULL_DOSSIER)
        for n in range(1, 6):
            assert f"Content for section {n + 1}." not in result[n]

    def test_trailing_newline(self):
        result = split_dossier(_FULL_DOSSIER)
        for n in range(1, 7):
            assert result[n].endswith("\n")


class TestSplitDossierPartial:
    def test_five_sections_missing_three(self):
        """When §3 heading is absent, return 5-key dict without §3."""
        headings_without_3 = [h for i, h in enumerate(_HEADINGS) if i != 2]
        dossier = "\n\n".join(
            f"{h}\n\nContent." for h in headings_without_3
        )
        result = split_dossier(dossier)
        assert 3 not in result
        assert set(result.keys()) == {1, 2, 4, 5, 6}

    def test_one_section_only(self):
        result = split_dossier("## 1. BIOGRAPHICAL FOUNDATION\n\nOnly section.")
        assert set(result.keys()) == {1}

    def test_sections_out_of_order_parsed_by_section_number(self):
        """Sections can appear in any order; keys reflect section number, not position."""
        reversed_dossier = "\n\n".join(
            f"{h}\n\nContent for {i+1}." for i, h in enumerate(reversed(_HEADINGS))
        )
        result = split_dossier(reversed_dossier)
        assert set(result.keys()) == {1, 2, 3, 4, 5, 6}


class TestSplitDossierEmpty:
    def test_no_sections_returns_empty_dict(self):
        result = split_dossier("Some text with no section headings at all.")
        assert result == {}

    def test_empty_string_returns_empty_dict(self):
        result = split_dossier("")
        assert result == {}


class TestSplitDossierHeadingVariants:
    def test_section_prefix_variant(self):
        text = "## Section 1: BIOGRAPHICAL FOUNDATION\n\nContent.\n\n## Section 2: INTELLECTUAL FRAMEWORK\n\nContent2."
        result = split_dossier(text)
        assert 1 in result
        assert 2 in result

    def test_plus_sign_boundary_heading(self):
        text = "## 5. HISTORICAL + CONCEPTUAL BOUNDARIES\n\nContent."
        result = split_dossier(text)
        assert 5 in result

    def test_ecological_foundation_maps_to_section_1(self):
        text = "## ECOLOGICAL FOUNDATION\n\nOrganism content."
        result = split_dossier(text)
        assert 1 in result
