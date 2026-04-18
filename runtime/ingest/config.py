"""Paths, env loading, and tunable knobs for the ingest app.

Load order:
  1. `.env` at repo root is read via python-dotenv at import time.
  2. Env vars (from the systemd EnvironmentFile in prod, or shell in dev)
     override anything in `.env`.
  3. Optional vars have sensible defaults; required vars fail loud at startup.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# --- Paths -------------------------------------------------------------------

INGEST_DIR = Path(__file__).resolve().parent
REPO_ROOT = INGEST_DIR.parent
RUNS_DIR = REPO_ROOT / "runs"
REFERENCE_DIR = REPO_ROOT / "reference"
SESSIONS_PATH = REFERENCE_DIR / "sessions.json"
SPEAKERS_PATH = REFERENCE_DIR / "speakers.json"
TEMPLATES_DIR = INGEST_DIR / "templates"
STATIC_DIR = INGEST_DIR / "static"

# Make `flows.shared.io` importable — same pattern flows/transcription_flow.py uses.
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# --- Env ---------------------------------------------------------------------

# Load .env early so subsequent os.environ reads see it. override=True because
# the Claude Code shell pre-sets some ANTHROPIC_* env vars to empty strings,
# which would otherwise shadow the real values in .env. In production the VM
# has a .env at /opt/ai-assembly/.env (mode 0600, owned by ingest); load_dotenv
# reads it the same way as in dev — no behavioural difference, just a
# different repo root path resolved at runtime.
load_dotenv(REPO_ROOT.parent / ".env", override=True)


def _required(name: str) -> str:
    v = os.environ.get(name, "").strip()
    if not v:
        print(
            f"FATAL: required env var {name} is not set. "
            f"Set it in .env or export it before starting uvicorn.",
            file=sys.stderr,
        )
        raise SystemExit(2)
    return v


def check_required_env() -> None:
    """Call at app startup. Raises SystemExit with a clear message if missing."""
    _required("UPLOAD_APP_PASSWORD")
    _required("ANTHROPIC_API_KEY")
    _required("ASSEMBLYAI_API_KEY")


UPLOAD_USERNAME = os.environ.get("UPLOAD_APP_USERNAME", "producer")
# These are read lazily (only at check_required_env time and when spawning
# subprocesses) so test-time imports don't blow up without .env.

# --- Day → Run mapping -------------------------------------------------------

# Run names per plan: one run per overnight cycle.
DAY_TO_RUN: dict[str, str | None] = {
    "Day Zero": None,          # not offered for overnight processing
    "Day One": "athens_night_1",
    "Day Two": "athens_night_2",
    "Day Three": "athens_night_3",
    "Day Four": None,          # no cycle after — event ends
    "Special Activations": None,
}

# --- Upload / pipeline knobs -------------------------------------------------

# Audio formats the spec accepts. Video containers are accepted as a convenience
# (AssemblyAI transcribes the audio track; video is discarded by normalization).
ALLOWED_EXTENSIONS = {".m4a", ".mp3", ".wav", ".mp4", ".mov", ".webm"}

# Refuse new uploads if disk free < this many bytes. Prevents half-written
# files and lets the producer know before they waste time.
MIN_FREE_BYTES = 2 * 1024 * 1024 * 1024  # 2 GiB

# Cap total upload body size (defense in depth; Caddy enforces the real limit).
MAX_UPLOAD_BYTES = 2 * 1024 * 1024 * 1024  # 2 GiB

# Chunk size when streaming upload bytes to disk.
UPLOAD_CHUNK_BYTES = 64 * 1024  # 64 KiB

# Normalization target per [AI_Assembly_Transcription_Pipeline.md:168].
NORMALIZED_FILENAME = "audio.m4a"
NORMALIZED_BITRATE = "96k"
NORMALIZED_CHANNELS = "1"   # mono
NORMALIZED_CODEC = "aac"

# Where the ingest app writes the per-session status.json (polled by UI).
STATUS_FILENAME = "status.json"
PIPELINE_LOG_FILENAME = "pipeline.log"
UPLOAD_LOCK_FILENAME = "upload.lock"

# Command used to invoke Stage 0. Overridable via INGEST_FLOW_CMD so tests
# can swap in a fake flow that touches output files without burning credits.
# Bumped whenever app.js or style.css changes materially. Include as
# ?v={{ static_version }} in template <script> and <link> tags.
STATIC_VERSION = "11"

# The app always appends <audio_path> <session_json_path> as positional args.
INGEST_FLOW_CMD = os.environ.get(
    "INGEST_FLOW_CMD",
    f"{sys.executable} {REPO_ROOT / 'flows' / 'transcription_flow.py'}",
)
