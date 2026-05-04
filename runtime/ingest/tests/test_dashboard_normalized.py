"""C26: dashboard surfaces `normalized` state distinctly from `received`
and `transcribing`. Awaiting-dispatch is its own UI state so operators
can tell the bottleneck is the orchestrator dispatcher, not ffmpeg or
AssemblyAI.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_RUNTIME = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_RUNTIME))

from flows.shared.io import write_json_atomic  # noqa: E402
from ingest.dashboard import _transcription_summary  # noqa: E402


def _seed_status(run_dir: Path, sid: str, *, state: str, source: str = "audio"):
    sdir = run_dir / "01_transcription" / sid
    sdir.mkdir(parents=True, exist_ok=True)
    write_json_atomic(
        sdir / "status.json",
        {"session_id": sid, "state": state, "source": source},
    )


class TestTranscriptionSummaryNormalized:
    def test_normalized_counted_separately(self, tmp_path):
        _seed_status(tmp_path, "s1", state="normalized")
        summary = _transcription_summary(tmp_path)
        assert summary["counts"]["normalized"] == 1
        assert summary["counts"]["received"] == 0
        assert summary["counts"]["transcribing"] == 0

    def test_only_normalized_state_is_awaiting_dispatch(self, tmp_path):
        # All normalized + nothing in flight → top-level state surfaces
        # the orchestrator-dispatch bottleneck.
        _seed_status(tmp_path, "s1", state="normalized")
        _seed_status(tmp_path, "s2", state="normalized")
        summary = _transcription_summary(tmp_path)
        assert summary["state"] == "awaiting_dispatch"

    def test_normalized_label_includes_awaiting_dispatch(self, tmp_path):
        _seed_status(tmp_path, "s1", state="normalized")
        _seed_status(tmp_path, "s2", state="normalized")
        summary = _transcription_summary(tmp_path)
        assert "2 awaiting dispatch" in summary["label"]

    def test_mixed_normalized_and_transcribing_is_running(self, tmp_path):
        # When some are mid-flight, top-level is still "running" since
        # the orchestrator HAS dispatched something — only the
        # all-normalized case earns "awaiting_dispatch".
        _seed_status(tmp_path, "s1", state="transcribing")
        _seed_status(tmp_path, "s2", state="normalized")
        summary = _transcription_summary(tmp_path)
        assert summary["state"] == "running"
        assert summary["counts"]["normalized"] == 1
        assert summary["counts"]["transcribing"] == 1
        # Both get surfaced in the label.
        assert "1 transcribing" in summary["label"]
        assert "1 awaiting dispatch" in summary["label"]

    def test_all_done_unaffected(self, tmp_path):
        _seed_status(tmp_path, "s1", state="done")
        _seed_status(tmp_path, "s2", state="done")
        summary = _transcription_summary(tmp_path)
        assert summary["state"] == "done"
        assert summary["counts"]["normalized"] == 0
