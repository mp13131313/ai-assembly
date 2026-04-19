"""Pass 1.2 INTELLECTUAL merge.

Emits `commitments.json` + `concepts.json` + `tensions.json` under
`runs/<slug>/01_research/pass_1_2/`. Per PB#7, meta-conventions (evidence
tagging, source citation, tier, contested reading) are FROZEN after this
chunk lands cleanly; chunks 1.3-1.6 reuse them unchanged.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))

from dotenv import load_dotenv
load_dotenv(REPO_ROOT.parent / ".env", override=True)

from flows.shared.chunk_runner import run_chunk
from schemas.pass_1_2 import Commitment, Concept, Tension


OUTPUT_KEYS = {
    "commitments": (Commitment, True),
    "concepts": (Concept, True),
    "tensions": (Tension, True),
}


def run_pass_1_2(**kwargs) -> dict:
    return run_chunk(
        repo_root=REPO_ROOT,
        chunk_name="1.2",
        template_name="pass_1_2_merge",
        output_keys=OUTPUT_KEYS,
        **kwargs,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pass 1.2 INTELLECTUAL merge")
    parser.add_argument("name")
    parser.add_argument("--type", default="human", choices=["human", "non_human", "fictional"])
    parser.add_argument("--subtype", default=None, choices=[None, "organism", "system"])
    parser.add_argument("--voice-mode", default="philosophical")
    parser.add_argument("--use-test-fixtures", action="store_true")
    args = parser.parse_args()
    run_pass_1_2(
        name=args.name,
        voice_type=args.type,
        subtype=args.subtype,
        voice_mode=args.voice_mode,
        use_test_fixtures=args.use_test_fixtures,
    )
