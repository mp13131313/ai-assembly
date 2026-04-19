"""Pipeline worker: ffmpeg normalize, Stage 0 subprocess, status tracking.

Design principle: the filesystem is authoritative. status.json files under
each session dir are the source of truth. The FastAPI BackgroundTask is
just the thing that updates them; transcription subprocesses are detached
so they survive uvicorn restarts.

All status writes go through `write_json_atomic` from flows.shared.io —
reconciliation reads these files from another process/worker, so torn
writes would be a bug.
"""

from __future__ import annotations

import asyncio
import json
import os
import shlex
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from flows.shared.io import write_json_atomic  # noqa: E402 — sys.path set in config

from .config import (
    INGEST_FLOW_CMD,
    NORMALIZED_BITRATE,
    NORMALIZED_CHANNELS,
    NORMALIZED_CODEC,
    NORMALIZED_FILENAME,
    PIPELINE_LOG_FILENAME,
    REPO_ROOT,
    RUNS_DIR,
    STATUS_FILENAME,
)

# --- States ------------------------------------------------------------------

STATE_RECEIVED = "received"
STATE_NORMALIZING = "normalizing"
STATE_TRANSCRIBING = "transcribing"
STATE_DONE = "done"
STATE_ERROR = "error"

TERMINAL_STATES = {STATE_DONE, STATE_ERROR}

# Sub-states derived from pipeline.log (returned by infer_state, never written
# to status.json — they'd be stale within seconds anyway).
SUBSTATE_ASR = "transcribing_asr"
SUBSTATE_SPEAKER_ID = "transcribing_speaker_id"
SUBSTATE_CLEANING = "transcribing_cleaning"
SUBSTATE_FINALIZING = "transcribing_finalizing"

# --- Serialization gate ------------------------------------------------------

# One in-flight ffmpeg normalization at a time per app process. Transcription
# subprocesses are detached and run concurrently — rate-limit pressure is on
# AssemblyAI + Anthropic, not on this process.
_gate = asyncio.Semaphore(1)


# --- Status helpers ----------------------------------------------------------


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def status_path(session_dir: Path) -> Path:
    return session_dir / STATUS_FILENAME


def log_path(session_dir: Path) -> Path:
    return session_dir / PIPELINE_LOG_FILENAME


def read_status(session_dir: Path) -> dict[str, Any]:
    """Read status.json; return {} if absent or malformed."""
    p = status_path(session_dir)
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def update_status(session_dir: Path, **fields: Any) -> dict[str, Any]:
    """Merge fields into status.json atomically. Returns the merged dict."""
    session_dir.mkdir(parents=True, exist_ok=True)
    cur = read_status(session_dir)
    cur.update(fields)
    cur["updated_at"] = _now()
    write_json_atomic(status_path(session_dir), cur)
    return cur


def initialize_status(
    session_dir: Path, *, session_id: str, run_id: str, audio_filename: str
) -> dict[str, Any]:
    """Write the initial status.json on upload receipt."""
    return update_status(
        session_dir,
        session_id=session_id,
        run_id=run_id,
        state=STATE_RECEIVED,
        started_at=_now(),
        pid=None,
        error=None,
        audio_filename=audio_filename,
    )


# --- PID liveness ------------------------------------------------------------


def _is_pid_alive(pid: int | None) -> bool:
    if not pid:
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        # Process exists but is owned by another user — treat as alive.
        return True
    # os.kill(pid, 0) succeeds for zombie (defunct) processes too — they still
    # hold their PID slot. Check stat to distinguish zombie from running.
    try:
        result = subprocess.run(
            ["ps", "-p", str(pid), "-o", "stat="],
            capture_output=True, text=True, timeout=2,
        )
        stat = result.stdout.strip()
        if "Z" in stat or not stat:  # Z = zombie, empty = gone
            return False
    except Exception:
        pass
    return True


def _substate_from_log(session_dir: Path) -> str:
    """Scan pipeline.log for the most-advanced Stage 0 sub-phase marker.

    TODO: This relies on transcription_flow.py's log message strings. If
    those strings change, substate inference silently breaks. A better
    design would have transcription_flow.py write a structured
    substate.txt file at each phase, and this function would prefer that
    over the log scan. Keep as fallback for when the structured file is
    missing (crash mid-phase before write).

    Returns one of the SUBSTATE_* constants, or STATE_TRANSCRIBING if the log
    is absent or has no recognisable markers. Does not mutate any file.

    Markers (in sequence emitted by transcription_flow.py):
      "Transcribing audio"   — AssemblyAI ASR started
      "AssemblyAI done in"   — ASR done; speaker-ID task starting
      "Speaker ID pass"      — speaker-ID task start header (no state change)
      "  done in" (first)    — speaker-ID done; cleaning task starting
      "Cleaning pass"        — cleaning task start header (confirms cleaning)
      "  done in" (second)   — cleaning done; writing output files (finalizing)
    """
    log = log_path(session_dir)
    if not log.exists():
        return STATE_TRANSCRIBING

    substate = STATE_TRANSCRIBING
    last_phase: str | None = None  # "asr", "speaker_id", "cleaning"

    try:
        text = log.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return substate

    for line in text.splitlines():
        if "Transcribing audio" in line:
            substate = SUBSTATE_ASR
            last_phase = "asr"
        elif "AssemblyAI done in" in line:
            substate = SUBSTATE_SPEAKER_ID
            last_phase = "speaker_id"
        elif "Cleaning pass" in line:
            # Cleaning pass header — may arrive before we've seen the speaker_id
            # "done in" line (ordering guarantee from the flow), but set state anyway.
            substate = SUBSTATE_CLEANING
            last_phase = "cleaning"
        elif "done in" in line:
            # "  done in X.Xs" is the per-task completion marker.
            if last_phase == "speaker_id":
                substate = SUBSTATE_CLEANING
                # don't advance last_phase — "Cleaning pass" will follow
            elif last_phase == "cleaning":
                substate = SUBSTATE_FINALIZING
                last_phase = "finalizing"

    return substate


def infer_state(session_dir: Path) -> dict[str, Any]:
    """Return the current authoritative status, reconciling with disk state.

    This is safe to call from any worker/process — it does not mutate state
    unless the stored state is provably stale (non-terminal + dead PID).

    When state is ``transcribing`` and the subprocess is still running, the
    returned dict gets a ``substate`` key with a more granular phase name
    derived from pipeline.log (never written to status.json to avoid churn).
    """
    status = read_status(session_dir)
    if not status:
        return {"state": None, "session_id": session_dir.name}

    state = status.get("state")
    if state in TERMINAL_STATES:
        status = dict(status)
        status["checkpoints"] = {
            "normalized":  (session_dir / "audio.m4a").exists(),
            "asr":         (session_dir / "out_01_diarized.json").exists(),
            "speaker_id":  (session_dir / "out_02_speaker_id.json").exists(),
            "cleaning":    (session_dir / "out_03_cleaned.json").exists(),
        }
        return status

    # Non-terminal: check if transcription succeeded by looking for the
    # canonical Stage 0 output file.
    if (session_dir / "session_package.json").exists():
        status = update_status(session_dir, state=STATE_DONE, pid=None, error=None)
        status = dict(status)
        status["checkpoints"] = {
            "normalized":  (session_dir / "audio.m4a").exists(),
            "asr":         (session_dir / "out_01_diarized.json").exists(),
            "speaker_id":  (session_dir / "out_02_speaker_id.json").exists(),
            "cleaning":    (session_dir / "out_03_cleaned.json").exists(),
        }
        return status

    # Non-terminal + no session_package.json + dead PID → error.
    if state == STATE_TRANSCRIBING and not _is_pid_alive(status.get("pid")):
        status = update_status(
            session_dir,
            state=STATE_ERROR,
            pid=None,
            error="transcription process died without producing session_package.json",
        )
        return status

    # Still running: enrich with sub-state from log parsing.
    if state == STATE_TRANSCRIBING:
        status = dict(status)  # copy — don't mutate the cached read
        status["substate"] = _substate_from_log(session_dir)

    # Always attach checkpoint presence so the UI can show completed steps.
    status = dict(status)
    status["checkpoints"] = {
        "normalized":  (session_dir / "audio.m4a").exists(),
        "asr":         (session_dir / "out_01_diarized.json").exists(),
        "speaker_id":  (session_dir / "out_02_speaker_id.json").exists(),
        "cleaning":    (session_dir / "out_03_cleaned.json").exists(),
    }

    return status


# --- FFmpeg normalization ----------------------------------------------------


class NormalizeError(RuntimeError):
    pass


def _append_log(session_dir: Path, line: str) -> None:
    with log_path(session_dir).open("a", encoding="utf-8") as f:
        f.write(line.rstrip("\n") + "\n")


def normalize_audio(src: Path, session_dir: Path) -> Path:
    """Transcode src to 96 kbps mono AAC → session_dir/audio.m4a.

    Writes to audio.m4a.tmp first; renames on success; raises on failure.
    On success, deletes src (the raw upload) — normalized is canonical.
    """
    session_dir.mkdir(parents=True, exist_ok=True)
    dst = session_dir / NORMALIZED_FILENAME
    tmp = dst.with_suffix(dst.suffix + ".tmp")

    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-nostdin",
        "-y",                     # overwrite tmp if it exists
        "-i", str(src),
        "-vn",                    # drop video track if present
        "-c:a", NORMALIZED_CODEC,
        "-b:a", NORMALIZED_BITRATE,
        "-ac", NORMALIZED_CHANNELS,
        "-f", "mp4",              # container — tmp file has .tmp suffix so
                                  # ffmpeg can't guess format from filename.
        str(tmp),
    ]
    _append_log(session_dir, f"\n--- normalize: {' '.join(shlex.quote(c) for c in cmd)}")

    with log_path(session_dir).open("ab") as logf:
        rc = subprocess.run(cmd, stdout=logf, stderr=subprocess.STDOUT).returncode

    if rc != 0 or not tmp.exists():
        tmp.unlink(missing_ok=True)
        raise NormalizeError(f"ffmpeg exited with {rc}; see {log_path(session_dir)}")

    # Validate: the normalized file must contain an audio stream.
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_streams", "-select_streams", "a", str(tmp)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    if probe.returncode != 0 or "codec_type=audio" not in probe.stdout:
        tmp.unlink(missing_ok=True)
        raise NormalizeError(
            f"ffprobe validation failed for {tmp.name}; no audio stream. "
            f"stderr: {probe.stderr.strip()}"
        )

    tmp.replace(dst)
    try:
        src.unlink()  # raw upload no longer needed
    except OSError:
        pass
    _append_log(session_dir, f"--- normalize: ok → {dst.name}")
    return dst


# --- Stage 0 subprocess ------------------------------------------------------


def _subprocess_env() -> dict[str, str]:
    """Explicit env for the detached transcription process.

    We pass credentials through explicitly rather than relying on the child
    to re-read .env. This avoids the "why is it failing at 2am" class of bug.
    """
    keys = (
        "ANTHROPIC_API_KEY",
        "ASSEMBLYAI_API_KEY",
        "CLAUDE_MODEL",
        "TRANSCRIPTION_CLAUDE_MODEL",
        "TRANSCRIPTION_SPEAKER_ID_MODEL",
        "TRANSCRIPTION_CACHE",
        "PATH",
        "HOME",
        "LANG",
        "LC_ALL",
        "VIRTUAL_ENV",
    )
    env = {k: os.environ[k] for k in keys if k in os.environ}
    return env


def spawn_transcription(
    session_dir: Path, audio_path: Path, session_json_path: Path
) -> int:
    """Launch Stage 0 as a detached subprocess. Return its PID.

    Detached via start_new_session so it survives uvicorn restarts. Output
    is tee'd to pipeline.log alongside normalize output. OUTPUT_DIR is set
    to session_dir so transcription_flow writes into the right place.
    """
    env = _subprocess_env()
    env["OUTPUT_DIR"] = str(session_dir)

    cmd = shlex.split(INGEST_FLOW_CMD) + [str(audio_path), str(session_json_path)]
    _append_log(session_dir, f"\n--- transcribe: {' '.join(shlex.quote(c) for c in cmd)}")

    logf = log_path(session_dir).open("ab")
    try:
        proc = subprocess.Popen(
            cmd,
            cwd=str(REPO_ROOT),  # so `flows.shared` imports + relative flow paths work
            stdout=logf,
            stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL,
            env=env,
            start_new_session=True,
        )
    finally:
        # The child has inherited the fd; close our copy in the parent.
        logf.close()
    return proc.pid


# --- Worker orchestration ----------------------------------------------------


async def run_normalize_and_transcribe(
    session_dir: Path, raw_path: Path, session_json_path: Path
) -> None:
    """Background worker body: normalize → spawn transcription → return.

    We do NOT wait for transcription here. The subprocess is detached; its
    status is inferred from session_package.json presence + PID liveness.
    """
    async with _gate:
        # --- Normalize
        update_status(session_dir, state=STATE_NORMALIZING)
        try:
            normalized = await asyncio.to_thread(normalize_audio, raw_path, session_dir)
        except NormalizeError as e:
            update_status(session_dir, state=STATE_ERROR, error=str(e))
            return
        except Exception as e:  # defensive: any unexpected failure is surfaced
            update_status(session_dir, state=STATE_ERROR, error=f"normalize crashed: {e}")
            return

        update_status(session_dir, audio_size_bytes=normalized.stat().st_size)

        # --- Spawn transcription. Don't hold the gate while the subprocess runs;
        # it's detached, and infer_state() is what reports its status afterwards.
    try:
        pid = spawn_transcription(session_dir, normalized, session_json_path)
    except Exception as e:
        update_status(session_dir, state=STATE_ERROR, error=f"spawn failed: {e}")
        return
    update_status(session_dir, state=STATE_TRANSCRIBING, pid=pid)


def spawn_retry(session_dir: Path, session_json_path: Path) -> dict[str, Any]:
    """Re-spawn Stage 0 without re-uploading. For error recovery.

    Requires the normalized audio.m4a to still be present. Writes a fresh
    'transcribing' status. Call only after user-confirmed retry.
    """
    audio = session_dir / NORMALIZED_FILENAME
    if not audio.exists():
        return update_status(
            session_dir,
            state=STATE_ERROR,
            error=f"cannot retry: {NORMALIZED_FILENAME} missing; re-upload required",
        )
    pid = spawn_transcription(session_dir, audio, session_json_path)
    return update_status(
        session_dir, state=STATE_TRANSCRIBING, pid=pid, error=None, retry_at=_now()
    )


# --- Startup reconciliation --------------------------------------------------


def reconcile_on_startup() -> list[dict[str, Any]]:
    """Walk runs/ and reconcile every session dir's status.

    Called from the FastAPI lifespan. Returns the list of reconciled states
    for logging.
    """
    out: list[dict[str, Any]] = []
    if not RUNS_DIR.exists():
        return out
    for transcription_dir in RUNS_DIR.glob("*/01_transcription/*"):
        if not transcription_dir.is_dir():
            continue
        if not status_path(transcription_dir).exists():
            continue
        before = read_status(transcription_dir).get("state")
        after = infer_state(transcription_dir).get("state")
        if before != after:
            out.append(
                {"dir": str(transcription_dir), "before": before, "after": after}
            )
    return out


# --- Disk pre-flight ---------------------------------------------------------


def free_bytes(path: Path = RUNS_DIR) -> int:
    """Free bytes on the filesystem containing `path`. Used by /upload to
    refuse big uploads before they half-write."""
    path = path if path.exists() else path.parent
    return shutil.disk_usage(path).free
