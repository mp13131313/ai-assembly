"""Pass 1.3 REASONING merge."""
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
from schemas.pass_1_3 import ReasoningMethod, Textures


OUTPUT_KEYS = {"reasoning_method": ReasoningMethod, "textures": Textures}


def run_pass_1_3(project_root=None, project=None, **kwargs) -> dict:
    if project_root is None:
        project_root = resolve_project_root(project, repo_root=REPO_ROOT)
    return run_chunk(
        repo_root=REPO_ROOT, project_root=project_root, chunk_name="1.3",
        template_name="pass_1_3_merge", output_keys=OUTPUT_KEYS, **kwargs,
    )


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("name")
    p.add_argument("--type", default="human", choices=["human", "non_human", "fictional"])
    p.add_argument("--subtype", default=None, choices=[None, "organism", "system"])
    p.add_argument("--voice-mode", default="philosophical")
    p.add_argument("--use-test-fixtures", action="store_true")
    add_project_arg(p)
    a = p.parse_args()
    run_pass_1_3(name=a.name, voice_type=a.type, subtype=a.subtype,
                 voice_mode=a.voice_mode, use_test_fixtures=a.use_test_fixtures,
                 project=a.project)
