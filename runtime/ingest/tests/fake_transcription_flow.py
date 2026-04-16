"""Drop-in substitute for flows/transcription_flow.py — for tests and smoke.

Honors the same CLI (two positional args: audio_path session_json_path) and
the same OUTPUT_DIR env var. Produces the same five output files in the same
order as the real flow, but with placeholder content.

Usage::

    INGEST_FLOW_CMD="python /path/to/fake_transcription_flow.py" \\
        uvicorn ingest.app:app ...

Tunables (env vars):
  FAKE_DELAY_SECONDS  — total sleep across the fake run (default 3)
  FAKE_EXIT_CODE      — return this instead of 0 to simulate a failure
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path


def _write_stage(dir_: Path, name: str, payload: dict) -> None:
    path = dir_ / name
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__, file=sys.stderr)
        return 2
    audio_path = Path(sys.argv[1])
    session_json_path = Path(sys.argv[2])
    out_dir = Path(os.environ.get("OUTPUT_DIR", "."))
    out_dir.mkdir(parents=True, exist_ok=True)

    total_delay = float(os.environ.get("FAKE_DELAY_SECONDS", "3"))
    step = total_delay / 4

    print(f"[fake_flow] audio={audio_path} session={session_json_path} out={out_dir}")
    sess = json.loads(session_json_path.read_text(encoding="utf-8"))

    time.sleep(step)
    _write_stage(
        out_dir,
        "out_01_diarized.json",
        {"session_title": sess.get("session_title", ""), "turns": [], "_fake": True},
    )
    print("[fake_flow] wrote out_01_diarized.json")

    time.sleep(step)
    _write_stage(out_dir, "out_02_speaker_id.json", {"_fake": True})
    print("[fake_flow] wrote out_02_speaker_id.json")

    time.sleep(step)
    _write_stage(out_dir, "out_03_cleaned.json", {"_fake": True})
    print("[fake_flow] wrote out_03_cleaned.json")

    time.sleep(step)
    _write_stage(
        out_dir,
        "session_package.json",
        {
            "metadata": {"session_title": sess.get("session_title", "")},
            "transcript": {"speakers_present": [], "turns": []},
            "review_queue": {"verify_markers": []},
            "_fake": True,
        },
    )
    (out_dir / "review.md").write_text("# Fake review\n", encoding="utf-8")
    print("[fake_flow] done")

    return int(os.environ.get("FAKE_EXIT_CODE", "0"))


if __name__ == "__main__":
    raise SystemExit(main())
