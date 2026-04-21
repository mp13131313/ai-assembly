"""Tests for pass_0b_header.md + pass_0b_footer.md section_mode Jinja conditionals."""
import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from flows.shared.prompt_render import render


_BASE_CTX = dict(
    voice_slug="test",
    name="Test",
    type="human",
    subtype=None,
    voice_mode="philosophical",
    corpus_constraint="full",
    hostile_sources=False,
    wikipedia_url="https://en.wikipedia.org/wiki/Test",
)


class TestMonolithicMode:
    def test_header_monolithic_no_section_key(self):
        """Monolithic render (no section_mode passed) should not fail under StrictUndefined."""
        r = render("pass_0b_header.md", **_BASE_CTX)
        assert "six thematic areas below" in r

    def test_header_monolithic_has_claude_dr_path(self):
        r = render("pass_0b_header.md", **_BASE_CTX)
        assert "claude_dr.md" in r

    def test_header_monolithic_no_section_header(self):
        r = render("pass_0b_header.md", **_BASE_CTX)
        assert "Section 1 of 6" not in r
        assert "Section 2 of 6" not in r

    def test_header_monolithic_explicit_false(self):
        r = render("pass_0b_header.md", **_BASE_CTX, section_mode=False)
        assert "six thematic areas below" in r
        assert "Section 1 of 6" not in r

    def test_footer_monolithic_no_section_mode(self):
        r = render("pass_0b_footer.md", corpus_constraint="full",
                   hostile_sources=False, display_name_with_hint="Test")
        assert "six thematic area headings" in r

    def test_footer_monolithic_explicit_false(self):
        r = render("pass_0b_footer.md", corpus_constraint="full",
                   hostile_sources=False, display_name_with_hint="Test",
                   section_mode=False)
        assert "six thematic area headings" in r


class TestSectionModeIndex1:
    def test_header_section_1_label(self):
        r = render("pass_0b_header.md", **_BASE_CTX, section_mode=True, section_index=1)
        assert "Section 1 of 6" in r

    def test_header_section_1_filename(self):
        r = render("pass_0b_header.md", **_BASE_CTX, section_mode=True, section_index=1)
        assert "01_section_1.md" in r

    def test_header_section_1_do_not_run(self):
        r = render("pass_0b_header.md", **_BASE_CTX, section_mode=True, section_index=1)
        assert "Do NOT run the pipeline yet" in r

    def test_header_section_1_no_pipeline_cmd(self):
        r = render("pass_0b_header.md", **_BASE_CTX, section_mode=True, section_index=1)
        assert "run_persona_pipeline.py" not in r

    def test_header_section_1_singular_language(self):
        r = render("pass_0b_header.md", **_BASE_CTX, section_mode=True, section_index=1)
        assert "the thematic area below" in r

    def test_header_section_1_wikipedia_url(self):
        r = render("pass_0b_header.md", **_BASE_CTX, section_mode=True, section_index=1)
        assert "wikipedia.org" in r or "Wikipedia" in r

    def test_header_section_1_runtime_envelope(self):
        r = render("pass_0b_header.md", **_BASE_CTX, section_mode=True, section_index=1)
        assert "20–40 minutes" in r
        assert "60 minutes" in r


class TestSectionModeIndex2to5:
    @pytest.mark.parametrize("idx", [2, 3, 4, 5])
    def test_header_middle_sections_label(self, idx):
        r = render("pass_0b_header.md", **_BASE_CTX, section_mode=True, section_index=idx)
        assert f"Section {idx} of 6" in r

    @pytest.mark.parametrize("idx", [2, 3, 4, 5])
    def test_header_middle_sections_filename(self, idx):
        r = render("pass_0b_header.md", **_BASE_CTX, section_mode=True, section_index=idx)
        assert f"0{idx}_section_{idx}.md" in r

    @pytest.mark.parametrize("idx", [2, 3, 4, 5])
    def test_header_middle_sections_do_not_run(self, idx):
        r = render("pass_0b_header.md", **_BASE_CTX, section_mode=True, section_index=idx)
        assert "Do NOT run the pipeline yet" in r

    @pytest.mark.parametrize("idx", [2, 3, 4, 5])
    def test_header_middle_sections_no_wikipedia(self, idx):
        """Wikipedia URL only in §1."""
        r = render("pass_0b_header.md", **_BASE_CTX, section_mode=True, section_index=idx)
        assert "wikipedia.org" not in r


class TestSectionModeIndex6:
    def test_header_section_6_label(self):
        r = render("pass_0b_header.md", **_BASE_CTX, section_mode=True, section_index=6)
        assert "Section 6 of 6" in r

    def test_header_section_6_filename(self):
        r = render("pass_0b_header.md", **_BASE_CTX, section_mode=True, section_index=6)
        assert "06_section_6.md" in r

    def test_header_section_6_pipeline_cmd(self):
        r = render("pass_0b_header.md", **_BASE_CTX, section_mode=True, section_index=6)
        assert "run_persona_pipeline.py" in r

    def test_header_section_6_no_do_not_run(self):
        r = render("pass_0b_header.md", **_BASE_CTX, section_mode=True, section_index=6)
        assert "Do NOT run the pipeline yet" not in r


class TestFooterSectionMode:
    def test_footer_section_mode_singular(self):
        r = render("pass_0b_footer.md", corpus_constraint="full",
                   hostile_sources=False, display_name_with_hint="Test",
                   section_mode=True)
        assert "the thematic area heading" in r

    def test_footer_section_mode_no_plural(self):
        r = render("pass_0b_footer.md", corpus_constraint="full",
                   hostile_sources=False, display_name_with_hint="Test",
                   section_mode=True)
        assert "six thematic area headings" not in r
