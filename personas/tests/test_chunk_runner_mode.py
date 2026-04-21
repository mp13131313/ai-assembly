"""Tests for chunk_runner.detect_dr_mode()."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from flows.shared import paths
from flows.shared.chunk_runner import detect_dr_mode


def _touch(p: Path) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("content", encoding="utf-8")


class TestDetectDrMode:
    def test_six_section_files_returns_per_section(self, tmp_path):
        slug = "test_voice"
        for n in range(1, 7):
            _touch(paths.section_dr_dossier(slug, n, tmp_path))
        assert detect_dr_mode(slug, tmp_path) == "per_section"

    def test_monolithic_file_returns_monolithic(self, tmp_path):
        slug = "test_voice"
        _touch(paths.concat_claude_dr(slug, tmp_path))
        assert detect_dr_mode(slug, tmp_path) == "monolithic"

    def test_partial_sections_raises_with_missing_list(self, tmp_path):
        slug = "test_voice"
        for n in [1, 2, 4, 5, 6]:  # missing §3
            _touch(paths.section_dr_dossier(slug, n, tmp_path))
        with pytest.raises(RuntimeError, match="sections \\[3\\]"):
            detect_dr_mode(slug, tmp_path)

    def test_no_dr_raises(self, tmp_path):
        with pytest.raises(RuntimeError, match="No DR dossier found"):
            detect_dr_mode("no_voice", tmp_path)

    def test_per_section_takes_precedence_over_monolithic(self, tmp_path):
        """If all 6 sections exist alongside a monolithic, return per_section."""
        slug = "test_voice"
        for n in range(1, 7):
            _touch(paths.section_dr_dossier(slug, n, tmp_path))
        _touch(paths.concat_claude_dr(slug, tmp_path))
        assert detect_dr_mode(slug, tmp_path) == "per_section"
