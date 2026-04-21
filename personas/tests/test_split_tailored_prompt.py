"""Tests for scripts/split_tailored_prompt.py."""
import sys
import tempfile
import textwrap
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.split_tailored_prompt import split_monolithic, wrap_section


_SECTION_NAMES = [
    "BIOGRAPHICAL FOUNDATION",
    "INTELLECTUAL FRAMEWORK",
    "REASONING PATTERNS",
    "VOICE AND STYLE",
    "HISTORICAL + CONCEPTUAL BOUNDARIES",
    "PRIMARY TEXTS",
]

_MONOLITHIC = "\n".join(
    f"## Section {n}: {name}\n\nContent for section {n}.\n"
    for n, name in enumerate(_SECTION_NAMES, 1)
)

_VOICE_CONFIG = {
    "name": "Test Voice",
    "type": "human",
    "subtype": None,
    "voice_mode": "philosophical",
    "corpus_constraint": "full",
    "hostile_sources": False,
}


class TestSplitMonolithic:
    def test_returns_six_sections(self):
        sections = split_monolithic(_MONOLITHIC)
        assert len(sections) == 6

    def test_keys_are_1_through_6(self):
        sections = split_monolithic(_MONOLITHIC)
        assert set(sections.keys()) == {1, 2, 3, 4, 5, 6}

    def test_each_section_contains_its_heading(self):
        sections = split_monolithic(_MONOLITHIC)
        for n, name in enumerate(_SECTION_NAMES, 1):
            assert f"## Section {n}: {name}" in sections[n]

    def test_each_section_contains_its_content(self):
        sections = split_monolithic(_MONOLITHIC)
        for n in range(1, 7):
            assert f"Content for section {n}." in sections[n]

    def test_section_does_not_contain_next_heading(self):
        sections = split_monolithic(_MONOLITHIC)
        for n in range(1, 6):
            assert f"## Section {n + 1}:" not in sections[n]

    def test_trailing_newline(self):
        sections = split_monolithic(_MONOLITHIC)
        for n in range(1, 7):
            assert sections[n].endswith("\n")

    def test_plus_sign_in_heading_matches(self):
        """HISTORICAL + CONCEPTUAL BOUNDARIES has a + — regex must handle it."""
        sections = split_monolithic(_MONOLITHIC)
        assert "HISTORICAL + CONCEPTUAL BOUNDARIES" in sections[5]

    def test_wrong_count_raises(self):
        bad = "## Section 1: BIOGRAPHICAL FOUNDATION\n\ncontent\n"
        with pytest.raises(ValueError, match="Expected 6 section headings, found 1"):
            split_monolithic(bad)

    def test_non_contiguous_numbering_raises(self):
        bad = "\n".join(
            f"## Section {n}: {name}\n\nContent.\n"
            for n, name in zip([1, 2, 3, 4, 5, 7], _SECTION_NAMES)
        )
        with pytest.raises(ValueError, match="contiguous"):
            split_monolithic(bad)

    def test_empty_string_raises(self):
        with pytest.raises(ValueError):
            split_monolithic("")


class TestWrapSection:
    def test_header_contains_section_label(self):
        result = wrap_section(
            "## Section 1: BIOGRAPHICAL FOUNDATION\n\nSome content.\n",
            section_index=1,
            slug="test_voice",
            voice_config=_VOICE_CONFIG,
            wikipedia_url=None,
        )
        assert "Section 1 of 6" in result

    def test_footer_singular_language(self):
        result = wrap_section(
            "## Section 2: INTELLECTUAL FRAMEWORK\n\nSome content.\n",
            section_index=2,
            slug="test_voice",
            voice_config=_VOICE_CONFIG,
            wikipedia_url=None,
        )
        assert "the thematic area heading" in result
        assert "six thematic area headings" not in result

    def test_wikipedia_url_in_section_1(self):
        result = wrap_section(
            "## Section 1: BIOGRAPHICAL FOUNDATION\n\nContent.\n",
            section_index=1,
            slug="test_voice",
            voice_config=_VOICE_CONFIG,
            wikipedia_url="https://en.wikipedia.org/wiki/Test",
        )
        assert "wikipedia.org" in result

    def test_no_wikipedia_url_in_section_2(self):
        result = wrap_section(
            "## Section 2: INTELLECTUAL FRAMEWORK\n\nContent.\n",
            section_index=2,
            slug="test_voice",
            voice_config=_VOICE_CONFIG,
            wikipedia_url="https://en.wikipedia.org/wiki/Test",
        )
        assert "wikipedia.org" not in result

    def test_provenance_header_present(self):
        result = wrap_section(
            "## Section 3: REASONING PATTERNS\n\nContent.\n",
            section_index=3,
            slug="test_voice",
            voice_config=_VOICE_CONFIG,
            wikipedia_url=None,
        )
        assert "PROMPT_VERSION: pass_0b_section_mode_v1" in result
        assert "VOICE_SLUG: test_voice" in result
        assert "SECTION: 3" in result

    def test_section_6_shows_pipeline_cmd(self):
        result = wrap_section(
            "## Section 6: PRIMARY TEXTS\n\nContent.\n",
            section_index=6,
            slug="test_voice",
            voice_config=_VOICE_CONFIG,
            wikipedia_url=None,
        )
        assert "run_persona_pipeline.py" in result
        assert "Do NOT run the pipeline yet" not in result

    def test_section_body_included(self):
        body = "## Section 4: VOICE AND STYLE\n\nMy specific content here.\n"
        result = wrap_section(body, 4, "test_voice", _VOICE_CONFIG, None)
        assert "My specific content here." in result
