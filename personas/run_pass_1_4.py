"""Pass 1.4 VOICE merge."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))

from dotenv import load_dotenv
load_dotenv(REPO_ROOT.parent / ".env", override=True)

from flows.shared.chunk_runner import run_chunk
from schemas.pass_1_4 import Moves, Register, Vocabulary


OUTPUT_KEYS = {"moves": Moves, "register": Register, "vocabulary": Vocabulary}


def run_pass_1_4(**kwargs) -> dict:
    return run_chunk(
        repo_root=REPO_ROOT, chunk_name="1.4",
        template_name="pass_1_4_merge", output_keys=OUTPUT_KEYS, **kwargs,
    )


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("name")
    p.add_argument("--type", default="human", choices=["human", "non_human", "fictional"])
    p.add_argument("--subtype", default=None, choices=[None, "organism", "system"])
    p.add_argument("--voice-mode", default="philosophical")
    p.add_argument("--use-test-fixtures", action="store_true")
    a = p.parse_args()
    run_pass_1_4(name=a.name, voice_type=a.type, subtype=a.subtype,
                 voice_mode=a.voice_mode, use_test_fixtures=a.use_test_fixtures)
