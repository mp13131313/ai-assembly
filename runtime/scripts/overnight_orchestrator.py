"""Overnight pipeline orchestrator. Fires each stage when its inputs are ready.

Designed to run as a background loop (or systemd unit at 1-min cadence) for the
3 Athens nights. Idempotent — re-running mid-pipeline picks up where the last
poll left off via filesystem-as-state.

Machine-agnostic: works unchanged on operator laptop or VM. Subprocess paths
are computed relative to this script's location; Python interpreter is
sys.executable; PROJECT_ROOT comes from --project arg or env var.

Stage chain (coarse-grained — each stage fires once at upstream completion):

    transcription (auto-fired by ingest)
        │  (all sessions state=done; halt if any state=error)
        ▼
    researcher  ─►  provocateur  ─►  voice  ─►  editor (skip if not built)  ─►  publish

Per-session transcription is auto-fired by ingest's pipeline.py — orchestrator
does NOT fire it, only polls for completion.

Usage:

    python scripts/overnight_orchestrator.py --night N [--project PATH] [--once]
    python scripts/overnight_orchestrator.py --date 2026-05-07 [--project PATH]

  --night N    Tonight's night number (1, 2, or 3). Required if --date not given.
  --date DATE  YYYY-MM-DD; looked up in DATE_TO_NIGHT.
  --project    PROJECT_ROOT path (overrides $AI_ASSEMBLY_PROJECT_ROOT).
  --once       Single poll, exit. Default: loop until pipeline complete or deadline.
  --poll-s S   Poll interval in seconds (default 60).
  --deadline-h H  Hard deadline in hours from start (default 14).
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
_RUNTIME_DIR = _SCRIPT_DIR.parent
_FLOWS_DIR = _RUNTIME_DIR / "flows"
_REPO_ROOT = _RUNTIME_DIR

if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from dotenv import load_dotenv  # noqa: E402

load_dotenv(_REPO_ROOT.parent / ".env", override=True)

from flows.shared.project_root import add_project_arg, resolve_project_root  # noqa: E402

# --- Constants --------------------------------------------------------------

DATE_TO_NIGHT = {
    "2026-05-07": 1,  # Day One
    "2026-05-08": 2,  # Day Two
    "2026-05-09": 3,  # Day Three
}
NIGHT_TO_DAY = {1: "Day One", 2: "Day Two", 3: "Day Three"}

DEFAULT_POLL_INTERVAL_S = 60
DEFAULT_DEADLINE_HOURS = 14

# Per-session transcription states (from runtime/ingest/pipeline.py:41-45).
TRANSCRIPTION_STATE_DONE = "done"
TRANSCRIPTION_STATE_ERROR = "error"

# --- Helpers ----------------------------------------------------------------


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def run_dir_for_night(project_root: Path, night: int) -> Path:
    """Match runtime/ingest/config.py:80-87 DAY_TO_RUN naming."""
    return project_root / "runs" / f"athens_night_{night}"


def sessions_for_tonight(project_root: Path, night: int) -> list[str]:
    """Filter sessions.json to tonight's transcription scope.

    Tonight = sessions where day == NIGHT_TO_DAY[night] AND ai_assembly is True.
    """
    sessions_path = project_root / "reference" / "sessions.json"
    if not sessions_path.exists():
        raise SystemExit(f"sessions.json not found at {sessions_path}")
    payload = json.loads(sessions_path.read_text(encoding="utf-8"))
    sessions = payload.get("sessions", payload) if isinstance(payload, dict) else payload
    target_day = NIGHT_TO_DAY[night]
    return sorted(
        s["session_id"]
        for s in sessions
        if s.get("day") == target_day and s.get("ai_assembly") is True
    )


def transcription_state(run_dir: Path, session_ids: list[str]) -> dict:
    """Classify transcription state across required sessions.

    Returns dict with keys:
      - all_done: bool — every session state=done
      - any_error: bool — at least one state=error
      - error_sessions: list[str]
      - pending_sessions: list[str]  (received | normalizing | transcribing | absent)
      - done_count: int
      - total_count: int
    """
    error_sessions: list[str] = []
    pending_sessions: list[str] = []
    done_count = 0
    for sid in session_ids:
        status_path = run_dir / "01_transcription" / sid / "status.json"
        if not status_path.exists():
            pending_sessions.append(sid)
            continue
        try:
            status = json.loads(status_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            pending_sessions.append(sid)
            continue
        state = status.get("state")
        if state == TRANSCRIPTION_STATE_DONE:
            done_count += 1
        elif state == TRANSCRIPTION_STATE_ERROR:
            error_sessions.append(sid)
        else:
            pending_sessions.append(sid)
    return {
        "all_done": done_count == len(session_ids) and len(session_ids) > 0,
        "any_error": bool(error_sessions),
        "error_sessions": error_sessions,
        "pending_sessions": pending_sessions,
        "done_count": done_count,
        "total_count": len(session_ids),
    }


def fire_stage(cmd: list[str], stage_name: str, log_dir: Path) -> tuple[bool, Path]:
    """Run a stage subprocess. Returns (success, log_path)."""
    log_dir.mkdir(parents=True, exist_ok=True)
    ts = int(time.time())
    log_path = log_dir / f"{stage_name}.{ts}.log"
    with log_path.open("w", encoding="utf-8") as f:
        f.write(f"# {stage_name} start: {_now_iso()}\n")
        f.write(f"# cmd: {' '.join(cmd)}\n\n")
        f.flush()
        result = subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT)
        f.write(f"\n# {stage_name} end: {_now_iso()} (returncode={result.returncode})\n")
    return (result.returncode == 0, log_path)


def write_status(run_dir: Path, status: dict) -> None:
    """Atomic-ish write of orchestrator status JSON. Optional Caddy /status endpoint reads this."""
    status_dir = run_dir / "_orchestrator_logs"
    status_dir.mkdir(parents=True, exist_ok=True)
    tmp = status_dir / "status.json.tmp"
    tmp.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    tmp.replace(status_dir / "status.json")


# --- Stage commands (machine-agnostic; relative to this script's location) ---

_PYTHON = sys.executable


def _flow_cmd(name: str, *args: str) -> list[str]:
    """Build a subprocess invocation for a flow script.

    Uses sys.executable (not bare 'python') and resolves the flow path relative
    to this script's location, so it works unchanged on laptop and VM.
    """
    script = _FLOWS_DIR / name
    if not script.exists():
        raise FileNotFoundError(f"Flow script not found: {script}")
    return [_PYTHON, str(script), *args]


def editor_flow_exists() -> bool:
    """Editor pipeline is a planned 5th stage (B1). Skip cleanly until it ships."""
    return (_FLOWS_DIR / "editor_flow.py").exists()


# --- Per-stage triggers + fire logic ----------------------------------------


def poll_once(
    project_root: Path,
    night: int,
    *,
    skip_publish: bool = False,
) -> dict:
    """Single poll. Returns a status dict with at least:
      - 'state': one of {idle, fired:STAGE, complete, failed:STAGE[:DETAIL]}
      - 'detail': free-form context
      - 'transcription': transcription_state() result (may be omitted post-researcher)
    """
    run_dir = run_dir_for_night(project_root, night)
    if not run_dir.exists():
        return {
            "state": "idle",
            "detail": f"run_dir {run_dir} does not exist yet",
            "ts": _now_iso(),
        }

    log_dir = run_dir / "_orchestrator_logs"
    session_ids = sessions_for_tonight(project_root, night)
    if not session_ids:
        return {
            "state": "failed:config",
            "detail": f"sessions_for_tonight(night={night}) is empty — check sessions.json",
            "ts": _now_iso(),
        }

    # Sentinels for each downstream stage. Match what each flow actually writes.
    researcher_done = (run_dir / "02_researcher" / "grouping.json").exists()
    provocateur_done = (run_dir / "03_provocateur" / "manifest.json").exists()
    voice_done = (run_dir / "04_voice" / "manifest.json").exists()
    editor_done = (run_dir / "05_editor" / "manifest.json").exists()
    publish_index = project_root / "published_artifacts" / "nights" / f"night_{night}" / "_index.json"
    publish_done = publish_index.exists()

    if publish_done or (skip_publish and (editor_done or (voice_done and not editor_flow_exists()))):
        return {"state": "complete", "detail": "pipeline complete", "ts": _now_iso()}

    # Stage 1: Researcher — needs all transcriptions in done state.
    if not researcher_done:
        ts = transcription_state(run_dir, session_ids)
        if ts["any_error"]:
            return {
                "state": "failed:transcription",
                "detail": f"sessions in error state: {ts['error_sessions']}",
                "transcription": ts,
                "ts": _now_iso(),
            }
        if not ts["all_done"]:
            return {
                "state": "idle",
                "detail": f"transcription {ts['done_count']}/{ts['total_count']} done",
                "transcription": ts,
                "ts": _now_iso(),
            }
        ok, log_path = fire_stage(
            _flow_cmd("researcher_flow.py", str(run_dir)),
            "researcher",
            log_dir,
        )
        return {
            "state": "fired:researcher" if ok else "failed:researcher",
            "detail": f"log at {log_path}",
            "transcription": ts,
            "ts": _now_iso(),
        }

    # Stage 2: Provocateur — needs grouping.json from Researcher.
    if not provocateur_done:
        prior_dirs = [
            str(run_dir_for_night(project_root, n))
            for n in range(1, night)
            if run_dir_for_night(project_root, n).exists()
        ]
        cmd_args = [str(run_dir)]
        if prior_dirs:
            cmd_args += ["--prior-nights", ",".join(prior_dirs)]
        ok, log_path = fire_stage(
            _flow_cmd("provocateur_flow.py", *cmd_args),
            "provocateur",
            log_dir,
        )
        return {
            "state": "fired:provocateur" if ok else "failed:provocateur",
            "detail": f"log at {log_path}; prior_nights={prior_dirs}",
            "ts": _now_iso(),
        }

    # Stage 3: Voice — needs Provocateur manifest.
    if not voice_done:
        cmd_args = [str(run_dir), "--night", str(night), "--skip-step3"]
        if night > 1:
            cmd_args.append("--skip-validation")  # FU#62 path B: validation N1 only
        ok, log_path = fire_stage(
            _flow_cmd("voice_flow.py", *cmd_args),
            "voice",
            log_dir,
        )
        return {
            "state": "fired:voice" if ok else "failed:voice",
            "detail": f"log at {log_path}",
            "ts": _now_iso(),
        }

    # Stage 4: Editor — skip if editor_flow.py not yet built (B1 in flight).
    if editor_flow_exists() and not editor_done:
        ok, log_path = fire_stage(
            _flow_cmd("editor_flow.py", str(run_dir), "--night", str(night)),
            "editor",
            log_dir,
        )
        return {
            "state": "fired:editor" if ok else "failed:editor",
            "detail": f"log at {log_path}",
            "ts": _now_iso(),
        }

    # Stage 5: Publish.
    if not publish_done and not skip_publish:
        ok, log_path = fire_stage(
            _flow_cmd("publish_flow.py", str(run_dir), "--night", str(night)),
            "publish",
            log_dir,
        )
        return {
            "state": "fired:publish" if ok else "failed:publish",
            "detail": f"log at {log_path}",
            "ts": _now_iso(),
        }

    return {"state": "complete", "detail": "pipeline complete", "ts": _now_iso()}


def loop(
    project_root: Path,
    night: int,
    *,
    poll_interval_s: int,
    deadline_hours: int,
    skip_publish: bool,
) -> int:
    run_dir = run_dir_for_night(project_root, night)
    deadline_ts = time.time() + deadline_hours * 3600
    last_state = None

    while time.time() < deadline_ts:
        status = poll_once(project_root, night, skip_publish=skip_publish)
        if run_dir.exists():
            write_status(run_dir, {**status, "night": night, "deadline_hours": deadline_hours})

        # Print on every state change; log to stdout (journalctl on VM, terminal on laptop).
        if status["state"] != last_state:
            print(f"[{status['ts']}] poll: {status['state']}  ({status['detail']})", flush=True)
            last_state = status["state"]

        if status["state"] == "complete":
            return 0
        if status["state"].startswith("failed:"):
            print(
                f"[{_now_iso()}] HALT — {status['state']}: {status['detail']}\n"
                f"Investigate logs at {run_dir / '_orchestrator_logs'} then re-run orchestrator.",
                file=sys.stderr,
                flush=True,
            )
            return 1

        time.sleep(poll_interval_s)

    print(
        f"[{_now_iso()}] DEADLINE — pipeline did not complete within {deadline_hours}h",
        file=sys.stderr,
        flush=True,
    )
    return 2


# --- CLI --------------------------------------------------------------------


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Overnight pipeline orchestrator.")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--night", type=int, choices=[1, 2, 3], help="Night number (1, 2, or 3).")
    g.add_argument("--date", help="YYYY-MM-DD; looked up in DATE_TO_NIGHT.")

    add_project_arg(p)
    p.add_argument("--once", action="store_true", help="Single poll, exit.")
    p.add_argument(
        "--poll-s",
        type=int,
        default=DEFAULT_POLL_INTERVAL_S,
        dest="poll_s",
        help=f"Poll interval seconds (default {DEFAULT_POLL_INTERVAL_S}).",
    )
    p.add_argument(
        "--deadline-h",
        type=int,
        default=DEFAULT_DEADLINE_HOURS,
        dest="deadline_h",
        help=f"Hard deadline hours (default {DEFAULT_DEADLINE_HOURS}).",
    )
    p.add_argument(
        "--skip-publish",
        action="store_true",
        help="Stop after editor (or voice if no editor). For dry-runs without microsite render.",
    )
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    project_root = resolve_project_root(args.project)

    if args.night is not None:
        night = args.night
    else:
        if args.date not in DATE_TO_NIGHT:
            raise SystemExit(
                f"--date {args.date} not in DATE_TO_NIGHT mapping "
                f"({list(DATE_TO_NIGHT.keys())})"
            )
        night = DATE_TO_NIGHT[args.date]

    if args.once:
        status = poll_once(project_root, night, skip_publish=args.skip_publish)
        run_dir = run_dir_for_night(project_root, night)
        if run_dir.exists():
            write_status(run_dir, {**status, "night": night})
        print(json.dumps(status, indent=2))
        if status["state"].startswith("failed:"):
            return 1
        return 0

    return loop(
        project_root,
        night,
        poll_interval_s=args.poll_s,
        deadline_hours=args.deadline_h,
        skip_publish=args.skip_publish,
    )


if __name__ == "__main__":
    raise SystemExit(main())
