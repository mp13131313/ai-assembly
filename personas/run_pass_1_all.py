"""Pass 1 orchestrator — runs chunks 1.1-1.6 in parallel, then 1.7 sequentially.

Successor to v3.10's monolithic Pass 1-merge. Each chunk is a checkpointed,
schema-validated LLM call; orchestrator coordinates them + the final
coherence pass that produces `merged_dossier.json`.
"""
from __future__ import annotations

import argparse
import concurrent.futures as _cf
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))

from dotenv import load_dotenv
load_dotenv(REPO_ROOT.parent / ".env", override=True)

from run_pass_1_1 import run_pass_1_1
from run_pass_1_2 import run_pass_1_2
from run_pass_1_3 import run_pass_1_3
from run_pass_1_4 import run_pass_1_4
from run_pass_1_5 import run_pass_1_5
from run_pass_1_6 import run_pass_1_6
from run_pass_1_7 import run_pass_1_7


CHUNKS = [
    ("1.1", run_pass_1_1),
    ("1.2", run_pass_1_2),
    ("1.3", run_pass_1_3),
    ("1.4", run_pass_1_4),
    ("1.5", run_pass_1_5),
    ("1.6", run_pass_1_6),
]


def stamp(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] [orchestrator] {msg}", flush=True)


def run_pass_1_all(
    *,
    name: str,
    voice_type: str = "human",
    subtype: str | None = None,
    voice_mode: str = "philosophical",
    use_test_fixtures: bool = False,
    max_parallel: int = 3,
) -> dict:
    stamp(f"Pass 1 orchestrator: '{name}' type={voice_type} subtype={subtype} mode={voice_mode}")
    stamp(f"Phase 1A — chunks 1.1-1.6 in parallel (max_parallel={max_parallel})")

    t0 = time.time()
    with _cf.ThreadPoolExecutor(max_workers=max_parallel) as pool:
        futures = {
            pool.submit(
                fn, name=name, voice_type=voice_type, subtype=subtype,
                voice_mode=voice_mode, use_test_fixtures=use_test_fixtures,
            ): chunk_id
            for chunk_id, fn in CHUNKS
        }
        results: dict[str, dict] = {}
        for fut in _cf.as_completed(futures):
            chunk_id = futures[fut]
            try:
                results[chunk_id] = fut.result()
                stamp(f"  chunk {chunk_id} complete")
            except Exception as exc:
                stamp(f"  chunk {chunk_id} FAILED: {exc}")
                raise
    stamp(f"Phase 1A done in {time.time() - t0:.1f}s ({len(results)}/6 chunks)")

    stamp("Phase 1B — Pass 1.7 coherence")
    t1 = time.time()
    dossier = run_pass_1_7(name=name)
    stamp(f"Phase 1B done in {time.time() - t1:.1f}s")
    stamp(f"Total Pass 1 wall: {time.time() - t0:.1f}s")
    return dossier


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Pass 1 orchestrator (chunks 1.1-1.7)")
    p.add_argument("name")
    p.add_argument("--type", default="human", choices=["human", "non_human", "fictional"])
    p.add_argument("--subtype", default=None, choices=[None, "organism", "system"])
    p.add_argument("--voice-mode", default="philosophical")
    p.add_argument("--use-test-fixtures", action="store_true")
    p.add_argument("--max-parallel", type=int, default=3)
    a = p.parse_args()
    run_pass_1_all(
        name=a.name, voice_type=a.type, subtype=a.subtype, voice_mode=a.voice_mode,
        use_test_fixtures=a.use_test_fixtures, max_parallel=a.max_parallel,
    )
