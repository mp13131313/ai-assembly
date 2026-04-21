"""Pass 1.1 BIOGRAPHICAL merge.

Emits `life_scaffold.json` + `formative_candidates.json` under
`voices/<slug>/02_merge/pass_1_1/`. Per Boddice §13 5-part world rubric
+ §14 4-part formative rubric.

Phase B restructure: thin wrapper around chunk_runner.run_chunk() matching
1_2 through 1_6. Earlier self-contained implementation used the pre-
restructure runs/<slug>/ layout and monolithic DR only; chunk_runner gives
us per-section DR auto-detection + paths.py output location for free.
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
from flows.shared.project_root import add_project_arg, resolve_project_root
from schemas.pass_1_1 import FormativeCandidate, LifeScaffold


OUTPUT_KEYS = {
    "life_scaffold": (LifeScaffold, False),
    "formative_candidates": (FormativeCandidate, True),
}


def run_pass_1_1(project_root=None, project=None, **kwargs) -> dict:
    if project_root is None:
        project_root = resolve_project_root(project, repo_root=REPO_ROOT)
    return run_chunk(
        repo_root=REPO_ROOT,
        project_root=project_root,
        chunk_name="1.1",
        template_name="pass_1_1_merge",
        output_keys=OUTPUT_KEYS,
        **kwargs,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pass 1.1 BIOGRAPHICAL merge")
    parser.add_argument("name")
    parser.add_argument("--type", default="human", choices=["human", "non_human", "fictional"])
    parser.add_argument("--subtype", default=None, choices=[None, "organism", "system"])
    parser.add_argument("--voice-mode", default="philosophical")
    parser.add_argument("--use-test-fixtures", action="store_true")
    add_project_arg(parser)
    args = parser.parse_args()
    run_pass_1_1(
        name=args.name,
        voice_type=args.type,
        subtype=args.subtype,
        voice_mode=args.voice_mode,
        use_test_fixtures=args.use_test_fixtures,
        project=args.project,
    )
