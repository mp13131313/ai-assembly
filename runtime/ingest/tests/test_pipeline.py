"""Pipeline unit tests: status state machine, PID liveness, reconcile.

Runs ffmpeg against a real (tiny) audio file, so it requires ffmpeg on PATH
— but costs no API credits.
"""

from __future__ import annotations

import json
import os
import subprocess
import time
from pathlib import Path

import pytest

from ingest import pipeline


@pytest.fixture
def session_dir(tmp_path: Path) -> Path:
    d = tmp_path / "run" / "01_transcription" / "sess_id"
    d.mkdir(parents=True)
    return d


def test_initialize_and_read_status(session_dir: Path):
    st = pipeline.initialize_status(
        session_dir, session_id="sess_id", run_id="run", audio_filename="audio.mp3"
    )
    assert st["state"] == pipeline.STATE_RECEIVED
    assert st["pid"] is None
    # Round-trip
    assert pipeline.read_status(session_dir)["session_id"] == "sess_id"


def test_update_status_merges(session_dir: Path):
    pipeline.initialize_status(
        session_dir, session_id="s", run_id="r", audio_filename="a.m4a"
    )
    pipeline.update_status(session_dir, pid=1234, state=pipeline.STATE_TRANSCRIBING)
    st = pipeline.read_status(session_dir)
    assert st["state"] == pipeline.STATE_TRANSCRIBING
    assert st["pid"] == 1234
    # Previously-set fields survive.
    assert st["session_id"] == "s"


def test_infer_state_promotes_to_done_when_package_exists(session_dir: Path):
    pipeline.initialize_status(
        session_dir, session_id="s", run_id="r", audio_filename="a.m4a"
    )
    pipeline.update_status(session_dir, state=pipeline.STATE_TRANSCRIBING, pid=99999)
    # Simulate successful completion: session_package.json appears on disk.
    (session_dir / "session_package.json").write_text("{}")
    st = pipeline.infer_state(session_dir)
    assert st["state"] == pipeline.STATE_DONE


def test_infer_state_marks_error_on_dead_pid_no_output(session_dir: Path):
    pipeline.initialize_status(
        session_dir, session_id="s", run_id="r", audio_filename="a.m4a"
    )
    # PID 1 exists (init), but let's use a guaranteed-dead one.
    pipeline.update_status(session_dir, state=pipeline.STATE_TRANSCRIBING, pid=99999)
    st = pipeline.infer_state(session_dir)
    assert st["state"] == pipeline.STATE_ERROR
    assert "died" in st["error"]


def test_infer_state_leaves_live_pid_alone(session_dir: Path):
    pipeline.initialize_status(
        session_dir, session_id="s", run_id="r", audio_filename="a.m4a"
    )
    # Our own PID is definitely alive.
    pipeline.update_status(session_dir, state=pipeline.STATE_TRANSCRIBING, pid=os.getpid())
    st = pipeline.infer_state(session_dir)
    assert st["state"] == pipeline.STATE_TRANSCRIBING


def test_infer_state_returns_terminal_unchanged(session_dir: Path):
    pipeline.initialize_status(
        session_dir, session_id="s", run_id="r", audio_filename="a.m4a"
    )
    pipeline.update_status(session_dir, state=pipeline.STATE_DONE, pid=None)
    st = pipeline.infer_state(session_dir)
    assert st["state"] == pipeline.STATE_DONE


def _make_sine_wave(path: Path, seconds: int = 2) -> None:
    """Use ffmpeg to synthesize a tiny silence-free test audio file."""
    subprocess.run(
        ["ffmpeg", "-hide_banner", "-nostdin", "-y",
         "-f", "lavfi", "-i", f"sine=frequency=440:duration={seconds}",
         str(path)],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )


def test_normalize_audio_produces_m4a(session_dir: Path, tmp_path: Path):
    src = tmp_path / "raw.wav"
    _make_sine_wave(src, seconds=2)
    out = pipeline.normalize_audio(src, session_dir)
    assert out.name == "audio.m4a"
    assert out.exists()
    # Raw should be deleted post-normalize.
    assert not src.exists()
    # ffprobe should see an AAC stream at ~96 kbps mono.
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_streams",
         "-select_streams", "a", str(out)],
        capture_output=True, text=True,
    )
    assert "codec_name=aac" in probe.stdout
    assert "channels=1" in probe.stdout


def test_normalize_audio_rejects_non_audio(session_dir: Path, tmp_path: Path):
    bogus = tmp_path / "not_audio.txt"
    bogus.write_text("this is not audio")
    with pytest.raises(pipeline.NormalizeError):
        pipeline.normalize_audio(bogus, session_dir)


def test_reconcile_on_startup_promotes_terminal(tmp_path: Path, monkeypatch):
    """reconcile_on_startup should find a completed run and promote done."""
    monkeypatch.setattr(pipeline, "RUNS_DIR", tmp_path)
    sdir = tmp_path / "run1" / "01_transcription" / "sess_a"
    sdir.mkdir(parents=True)
    pipeline.initialize_status(
        sdir, session_id="sess_a", run_id="run1", audio_filename="a.m4a"
    )
    pipeline.update_status(sdir, state=pipeline.STATE_TRANSCRIBING, pid=99998)
    (sdir / "session_package.json").write_text("{}")

    changes = pipeline.reconcile_on_startup()
    assert any(c["after"] == pipeline.STATE_DONE for c in changes)
    assert pipeline.read_status(sdir)["state"] == pipeline.STATE_DONE


def test_status_json_survives_concurrent_writes(session_dir: Path):
    """write_json_atomic guarantees no torn files. Smoke: rapid overwrites."""
    pipeline.initialize_status(
        session_dir, session_id="s", run_id="r", audio_filename="a.m4a"
    )
    for i in range(50):
        pipeline.update_status(session_dir, iteration=i)
    # After 50 writes, the file is still valid JSON.
    st = json.loads((session_dir / "status.json").read_text())
    assert st["iteration"] == 49
