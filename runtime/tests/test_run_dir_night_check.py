"""Tests for `assert_run_dir_night_matches` defensive check.

Cross-night state corruption is the silent failure mode this guards
against: wrong --night flag would have voice_flow write
`voices/<slug>/continuity_night_<N+1>.json` from the wrong night's
data, silently overwriting valid prior continuity. The check is
trivial regex parsing of the run_dir's last path segment; tests cover
both naming conventions, fall-through cases, and the actual mismatch.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_RUNTIME_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_RUNTIME_ROOT / "flows"))

from shared.io import assert_run_dir_night_matches  # noqa: E402


class TestRunDirNightCheck:
    """Both run_dir naming conventions + fall-through behavior."""

    def test_convention_a_format_matches(self):
        # Convention A: athens_2026_<date>_night<N>
        assert_run_dir_night_matches(Path("/tmp/athens_2026_2026_05_07_night1"), 1)
        assert_run_dir_night_matches(Path("/tmp/athens_2026_2026_05_08_night2"), 2)
        assert_run_dir_night_matches(Path("/tmp/athens_2026_2026_05_09_night3"), 3)

    def test_legacy_ingest_format_matches(self):
        # Legacy: athens_night_<N>
        assert_run_dir_night_matches(Path("/tmp/athens_night_1"), 1)
        assert_run_dir_night_matches(Path("/tmp/athens_night_2"), 2)
        assert_run_dir_night_matches(Path("/tmp/athens_night_3"), 3)

    def test_test_fixture_format_matches(self):
        # Legitimacy test format: legitimacy_test1_night1
        assert_run_dir_night_matches(Path("/tmp/legitimacy_test1_night1"), 1)
        assert_run_dir_night_matches(Path("/tmp/legitimacy_test1_night2"), 2)

    def test_no_night_in_name_falls_through_gracefully(self):
        # Run_dirs without embedded night number: no check, no error
        assert_run_dir_night_matches(Path("/tmp/dryrun_2026_04_29_plato_solo"), 1)
        assert_run_dir_night_matches(Path("/tmp/legitimacy_test2_single_night"), 1)
        assert_run_dir_night_matches(Path("/tmp/dev_msc_test"), 1)

    def test_mismatch_raises_systemexit(self):
        # The dangerous failure mode this guards: wrong --night
        with pytest.raises(SystemExit, match=r"does not match.*night=1"):
            assert_run_dir_night_matches(
                Path("/tmp/athens_2026_2026_05_07_night1"), 2
            )

    def test_mismatch_legacy_format_raises(self):
        with pytest.raises(SystemExit, match=r"does not match.*night=2"):
            assert_run_dir_night_matches(Path("/tmp/athens_night_2"), 1)

    def test_error_message_is_actionable(self):
        try:
            assert_run_dir_night_matches(
                Path("/tmp/athens_2026_2026_05_08_night2"), 1
            )
        except SystemExit as e:
            msg = str(e)
            assert "night=1" in msg
            assert "night=2" in msg
            assert "continuity" in msg.lower()  # explains the failure mode
            assert "Refusing to run" in msg
        else:
            pytest.fail("expected SystemExit")

    def test_uses_only_basename_not_full_path(self):
        # If the parent path has '_night_3' or similar, it shouldn't
        # confuse the check — only the final segment matters
        assert_run_dir_night_matches(
            Path("/Users/x/runs_for_night_3/athens_night_1"), 1
        )

    def test_word_boundary_prevents_partial_matches(self):
        # `_night10` is a real night number 10, not a partial match for `_night1`
        # (boundary regex \b ensures correct numeric capture).
        # Edge case: someone names a run "_night1abc" — \b prevents that
        # from matching '1' incorrectly. A run named with no clean digit
        # boundary falls through.
        # Verify: _night1 → 1 (correct), _night10 → 10
        assert_run_dir_night_matches(Path("/tmp/something_night10"), 10)
        # Mismatch with multi-digit:
        with pytest.raises(SystemExit):
            assert_run_dir_night_matches(Path("/tmp/something_night10"), 1)
