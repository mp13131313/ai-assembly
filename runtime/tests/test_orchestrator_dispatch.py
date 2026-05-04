"""C26: orchestrator-driven transcription dispatch.

Tests the new fire_pending_transcriptions() function and the extended
transcription_state() classification (normalized vs transcribing
buckets). Mocks ingest.pipeline.fire_transcription so no subprocesses
spawn during tests.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

_RUNTIME = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_RUNTIME))

from flows.shared.io import write_json_atomic  # noqa: E402

# Import via the script module path the orchestrator uses internally.
_SCRIPTS = _RUNTIME / "scripts"
sys.path.insert(0, str(_SCRIPTS))
from overnight_orchestrator import (  # noqa: E402
    fire_pending_transcriptions,
    transcription_state,
)


# --- Fixture builders --------------------------------------------------

def _seed_session(run_dir: Path, sid: str, *, state: str, pid: int | None = None) -> Path:
    sdir = run_dir / "01_transcription" / sid
    sdir.mkdir(parents=True, exist_ok=True)
    (sdir / "audio.m4a").write_bytes(b"fake-audio")
    (sdir / "session.json").write_text(json.dumps({"session_id": sid}))
    write_json_atomic(
        sdir / "status.json",
        {"session_id": sid, "state": state, "pid": pid},
    )
    return sdir


# --- transcription_state extended classification -----------------------

class TestTranscriptionStateBuckets:
    def test_normalized_session_is_pending(self, tmp_path):
        run = tmp_path / "athens_night_1"
        _seed_session(run, "s1", state="normalized")
        ts = transcription_state(run, ["s1"])
        assert ts["all_done"] is False
        assert ts["pending_sessions"] == ["s1"]
        assert ts["normalized_sessions"] == ["s1"]
        assert ts["transcribing_sessions"] == []

    def test_transcribing_session_is_pending(self, tmp_path):
        run = tmp_path / "athens_night_1"
        _seed_session(run, "s1", state="transcribing", pid=12345)
        ts = transcription_state(run, ["s1"])
        assert ts["pending_sessions"] == ["s1"]
        assert ts["normalized_sessions"] == []
        assert ts["transcribing_sessions"] == ["s1"]

    def test_substate_transcribing_classified_as_transcribing(self, tmp_path):
        run = tmp_path / "athens_night_1"
        _seed_session(run, "s1", state="transcribing_asr", pid=12345)
        ts = transcription_state(run, ["s1"])
        assert ts["transcribing_sessions"] == ["s1"]

    def test_done_session_excluded_from_pending(self, tmp_path):
        run = tmp_path / "athens_night_1"
        _seed_session(run, "s1", state="done")
        ts = transcription_state(run, ["s1"])
        assert ts["all_done"] is True
        assert ts["done_count"] == 1
        assert ts["normalized_sessions"] == []
        assert ts["transcribing_sessions"] == []


# --- fire_pending_transcriptions dispatch logic -----------------------

class TestFirePendingTranscriptions:
    def test_no_normalized_no_op(self, tmp_path):
        run = tmp_path / "athens_night_1"
        _seed_session(run, "s1", state="done")
        with patch("ingest.pipeline.fire_transcription") as mock_fire:
            result = fire_pending_transcriptions(run, ["s1"])
        mock_fire.assert_not_called()
        assert result["fired"] == []
        assert result["normalized_pending"] == 0

    def test_fires_one_normalized_session(self, tmp_path):
        run = tmp_path / "athens_night_1"
        _seed_session(run, "s1", state="normalized")
        with patch("ingest.pipeline.fire_transcription") as mock_fire:
            mock_fire.return_value = {"state": "transcribing", "pid": 99}
            result = fire_pending_transcriptions(run, ["s1"])
        assert mock_fire.call_count == 1
        assert result["fired"] == ["s1"]
        assert result["inflight_after"] == 1

    def test_concurrency_cap_skips_excess(self, tmp_path):
        run = tmp_path / "athens_night_1"
        for sid in ["s1", "s2", "s3", "s4"]:
            _seed_session(run, sid, state="normalized")
        with patch("ingest.pipeline.fire_transcription") as mock_fire:
            mock_fire.return_value = {"state": "transcribing", "pid": 99}
            result = fire_pending_transcriptions(run, ["s1", "s2", "s3", "s4"], max_concurrent=2)
        assert len(result["fired"]) == 2
        assert len(result["skipped_capacity"]) == 2
        assert mock_fire.call_count == 2

    def test_inflight_counted_against_cap(self, tmp_path):
        run = tmp_path / "athens_night_1"
        # One already in-flight + two normalized + cap = 2 → fire 1 only.
        _seed_session(run, "s1", state="transcribing", pid=12345)
        _seed_session(run, "s2", state="normalized")
        _seed_session(run, "s3", state="normalized")
        with patch("ingest.pipeline.fire_transcription") as mock_fire:
            mock_fire.return_value = {"state": "transcribing", "pid": 99}
            result = fire_pending_transcriptions(run, ["s1", "s2", "s3"], max_concurrent=2)
        assert result["inflight_before"] == 1
        assert len(result["fired"]) == 1
        assert len(result["skipped_capacity"]) == 1
        assert mock_fire.call_count == 1

    def test_substate_transcribing_counted_as_inflight(self, tmp_path):
        run = tmp_path / "athens_night_1"
        # transcribing_asr is a substate — orchestrator should count it.
        _seed_session(run, "s1", state="transcribing_asr", pid=12345)
        _seed_session(run, "s2", state="normalized")
        with patch("ingest.pipeline.fire_transcription") as mock_fire:
            mock_fire.return_value = {"state": "transcribing", "pid": 99}
            result = fire_pending_transcriptions(run, ["s1", "s2"], max_concurrent=1)
        assert result["inflight_before"] == 1
        assert result["fired"] == []  # already at cap
        mock_fire.assert_not_called()

    def test_received_state_not_dispatched(self, tmp_path):
        run = tmp_path / "athens_night_1"
        # Session that uploaded but ffmpeg hasn't finished — orchestrator
        # leaves it alone (only `normalized` is dispatchable).
        _seed_session(run, "s1", state="received")
        with patch("ingest.pipeline.fire_transcription") as mock_fire:
            result = fire_pending_transcriptions(run, ["s1"])
        mock_fire.assert_not_called()
        assert result["fired"] == []

    def test_fire_returning_error_does_not_count_as_inflight(self, tmp_path):
        run = tmp_path / "athens_night_1"
        _seed_session(run, "s1", state="normalized")
        with patch("ingest.pipeline.fire_transcription") as mock_fire:
            mock_fire.return_value = {"state": "error", "error": "spawn failed"}
            result = fire_pending_transcriptions(run, ["s1"], max_concurrent=4)
        assert mock_fire.call_count == 1
        # Did not transition to transcribing → not in fired list, no inflight bump.
        assert result["fired"] == []
        assert result["inflight_after"] == 0

    def test_missing_status_skipped(self, tmp_path):
        run = tmp_path / "athens_night_1"
        # Session listed in session_ids but no status.json yet.
        with patch("ingest.pipeline.fire_transcription") as mock_fire:
            result = fire_pending_transcriptions(run, ["nonexistent"])
        mock_fire.assert_not_called()
        assert result["fired"] == []
        assert result["normalized_pending"] == 0
