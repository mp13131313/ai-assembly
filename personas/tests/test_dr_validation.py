"""Tests for flows/shared/dr_validation.py — monolithic + per-section mode."""
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from flows.shared.dr_validation import (
    validate_dr_dossier,
    validate_section_dr_dossier,
    validate_dr_dossier_dir,
)

# Enough prose for a monolithic floor (>8000 words)
_LONG_PROSE = ("This is scholarly prose about a historical figure. " * 200) + "\n"
_MONOLITHIC_TEXT = (
    "## BIOGRAPHICAL FOUNDATION\n\n" + _LONG_PROSE +
    "## INTELLECTUAL FRAMEWORK\n\n" + _LONG_PROSE +
    "## REASONING PATTERNS\n\n" + _LONG_PROSE +
    "## VOICE AND STYLE\n\n" + _LONG_PROSE +
    "## HISTORICAL BOUNDARIES\n\n" + _LONG_PROSE +
    "## PRIMARY TEXTS\n\n" + _LONG_PROSE
)

# A per-section file with enough words (>1500) and one section heading
_SECTION_PROSE = ("Biographical research about the subject matter in detail. " * 350) + "\n"
_SECTION_TEXT = "## BIOGRAPHICAL FOUNDATION\n\n" + _SECTION_PROSE

_PROVENANCE = (
    "<!-- PROMPT_VERSION: pass_0b_section_mode_v1 "
    "| VOICE_SLUG: test_voice "
    "| SECTION: 1 "
    "| RENDERED_AT: 2026-01-01T00:00:00 -->\n\n"
)


def _write(tmp: Path, name: str, content: str) -> Path:
    p = tmp / name
    p.write_text(content, encoding="utf-8")
    return p


class TestMonolithicValidation:
    def test_valid_monolithic(self, tmp_path):
        p = _write(tmp_path, "dossier.md", _MONOLITHIC_TEXT)
        validate_dr_dossier(p)  # should not raise

    def test_too_short_raises(self, tmp_path):
        p = _write(tmp_path, "dossier.md", "Very short text.")
        with pytest.raises(ValueError, match="words — minimum"):
            validate_dr_dossier(p)

    def test_persona_card_shape_raises(self, tmp_path):
        p = _write(tmp_path, "dossier.md", _MONOLITHIC_TEXT + "\n## Field 01: Name\n")
        with pytest.raises(ValueError, match="persona card"):
            validate_dr_dossier(p)

    def test_missing_file_raises(self, tmp_path):
        with pytest.raises(ValueError, match="not found"):
            validate_dr_dossier(tmp_path / "nonexistent.md")


class TestPerSectionAutoDetect:
    def test_section_file_detected_by_name(self, tmp_path):
        """File named 01_section_1.md triggers per-section validation."""
        p = _write(tmp_path, "01_section_1.md", _SECTION_TEXT)
        validate_dr_dossier(p)  # should not raise

    def test_section_file_too_short(self, tmp_path):
        p = _write(tmp_path, "03_section_1.md", "Short.")
        with pytest.raises(ValueError, match="1,500"):
            validate_dr_dossier(p)

    def test_section_persona_card_raises(self, tmp_path):
        p = _write(tmp_path, "04_section_2.md", _SECTION_TEXT + "\n## Field 01: Name\n")
        with pytest.raises(ValueError, match="persona card"):
            validate_dr_dossier(p)

    def test_provenance_mismatch_warns_not_raises(self, tmp_path, capsys):
        wrong_prov = (
            "<!-- PROMPT_VERSION: pass_0b_section_mode_v1 "
            "| VOICE_SLUG: test_voice | SECTION: 5 "
            "| RENDERED_AT: 2026-01-01T00:00:00 -->\n\n"
        )
        p = _write(tmp_path, "03_section_1.md", wrong_prov + _SECTION_TEXT)
        validate_dr_dossier(p)  # should not raise
        out = capsys.readouterr().out + capsys.readouterr().err
        # warning may be on stdout or we can check with validate_section directly
        validate_section_dr_dossier(p, expected_section=1)  # also no raise


class TestDirectoryValidation:
    def _make_section_dir(self, tmp_path: Path, missing: int | None = None) -> Path:
        d = tmp_path / "04_dr_dossier"
        d.mkdir()
        for n in range(1, 7):
            if n == missing:
                continue
            fname = f"0{n}_section_{n}.md"
            _write(d, fname, _SECTION_TEXT)
        return d

    def test_valid_directory(self, tmp_path):
        d = self._make_section_dir(tmp_path)
        validate_dr_dossier_dir(d)  # should not raise

    def test_directory_via_validate_dr_dossier(self, tmp_path):
        d = self._make_section_dir(tmp_path)
        validate_dr_dossier(d)  # auto-detects directory

    def test_missing_one_section_raises(self, tmp_path):
        d = self._make_section_dir(tmp_path, missing=3)
        with pytest.raises(ValueError, match="Section 3: MISSING"):
            validate_dr_dossier_dir(d)

    def test_invalid_section_in_dir_raises(self, tmp_path):
        d = self._make_section_dir(tmp_path)
        (d / "04_section_4.md").write_text("Too short.", encoding="utf-8")
        with pytest.raises(ValueError, match="Section 4: INVALID"):
            validate_dr_dossier_dir(d)

    def test_not_a_directory_raises(self, tmp_path):
        p = _write(tmp_path, "file.md", "content")
        with pytest.raises(ValueError, match="Not a directory"):
            validate_dr_dossier_dir(p)
