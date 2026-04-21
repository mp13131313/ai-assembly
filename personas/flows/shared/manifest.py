"""Per-voice manifest — logs every LLM call for cost + wall-time analysis.

Each call_* wrapper appends an entry when slug is provided. Manifest lives at
voices/<slug>/_manifest.json as a list of entries, one per call.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

from flows.shared import paths
from flows.shared.project_root import get_project_root


def record(
    slug: str,
    pass_name: str,
    model: str,
    provider: str,
    input_tokens: int,
    output_tokens: int,
    thinking_tokens: int = 0,
    cost_usd: float | None = None,
    wall_seconds: float = 0.0,
    project_root: Path | None = None,
) -> None:
    """Append one LLM call entry to voices/<slug>/_manifest.json."""
    entry = {
        "timestamp": time.time(),
        "pass_name": pass_name,
        "model": model,
        "provider": provider,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "thinking_tokens": thinking_tokens,
        "cost_usd": cost_usd,
        "wall_seconds": wall_seconds,
    }
    project_root = project_root or get_project_root()
    manifest_path = paths.manifest(slug, project_root)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    existing: list = []
    if manifest_path.exists():
        try:
            existing = json.loads(manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            manifest_path.rename(manifest_path.with_suffix(".json.corrupt"))
            existing = []
    existing.append(entry)
    manifest_path.write_text(json.dumps(existing, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
