"""Tests for `_capture_failure` failure-record helper.

C38 (2026-05-04 — Marley × theme_001 silent-drop incident): voice_flow
batch dispatchers used to log-and-swallow exceptions, leaving operators
with manifest counts that didn't add up and no record of which pair
failed or why. `_capture_failure` standardises the failure-record shape
across stages (step1/step2/step3/continuity) so failures land in the
manifest with structured detail.
"""
from __future__ import annotations

import sys
from pathlib import Path

_RUNTIME_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_RUNTIME_ROOT / "flows"))

from voice_flow import _capture_failure  # noqa: E402


def _raise(exc_class, msg):
    """Raise + catch — gives us a real .__traceback__ to feed the helper."""
    try:
        raise exc_class(msg)
    except Exception as e:  # noqa: BLE001
        return e


class TestCaptureFailureStep1:
    """Step 1 path — key is (slug, theme_id) tuple."""

    def test_step1_pair_record_basic(self):
        e = _raise(RuntimeError, "anthropic stream failed")
        rec = _capture_failure(stage="step1", key=("bob_marley", "theme_001"), exc=e)

        assert rec["stage"] == "step1"
        assert rec["voice_slug"] == "bob_marley"
        assert rec["theme_id"] == "theme_001"
        assert rec["error_type"] == "RuntimeError"
        assert rec["error_message"] == "anthropic stream failed"
        assert "traceback_excerpt" in rec
        assert "RuntimeError" in rec["traceback_excerpt"]

    def test_step1_message_truncated_at_500(self):
        long_msg = "x" * 1000
        e = _raise(ValueError, long_msg)
        rec = _capture_failure(stage="step1", key=("a", "b"), exc=e)
        assert len(rec["error_message"]) == 500


class TestCaptureFailureSingleKey:
    """Step 2 / Step 3 / Continuity path — key is a slug string."""

    def test_step2_voice_record(self):
        e = _raise(TimeoutError, "step 2 timed out")
        rec = _capture_failure(stage="step2", key="cleopatra", exc=e)

        assert rec["stage"] == "step2"
        assert rec["voice_slug"] == "cleopatra"
        assert "theme_id" not in rec  # single-voice scope
        assert rec["error_type"] == "TimeoutError"

    def test_step3_voice_record(self):
        e = _raise(KeyError, "missing peer")
        rec = _capture_failure(stage="step3", key="plato", exc=e)
        assert rec["stage"] == "step3"
        assert rec["voice_slug"] == "plato"

    def test_continuity_voice_record(self):
        e = _raise(IOError, "disk full")
        rec = _capture_failure(stage="continuity", key="ada_lovelace", exc=e)
        assert rec["stage"] == "continuity"
        assert rec["voice_slug"] == "ada_lovelace"


class TestCaptureFailureExtras:
    """Optional `extra` dict merges into record without clobbering core fields."""

    def test_extra_merge(self):
        e = _raise(RuntimeError, "boom")
        rec = _capture_failure(
            stage="step1",
            key=("plato", "theme_002"),
            exc=e,
            extra={"attempt": 2, "model": "claude-opus-4-7"},
        )
        assert rec["attempt"] == 2
        assert rec["model"] == "claude-opus-4-7"
        # core fields preserved
        assert rec["voice_slug"] == "plato"
        assert rec["theme_id"] == "theme_002"
        assert rec["stage"] == "step1"
