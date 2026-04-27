"""patch_walker.py — Path-walker for FU#13 Pass 7a-FIX linear patcher.

Extracted from run_persona_pipeline.py in FU#10-mod (2026-04-24) to enable
unit testing without triggering the orchestrator's top-level pipeline
execution.

The path-walker accepts dot-notation with optional [N] list indices and
replaces values in nested dicts. Used by the Pass 7a-FIX patcher to apply
field-level patches against cached pass outputs.

Examples:
  "knowledge_boundary"          -> d["knowledge_boundary"] = new_value
  "constitution[3]"             -> d["constitution"][3] = new_value
  "constitution[3].principle"   -> d["constitution"][3]["principle"] = new_value

Raises:
  ValueError — empty path
  KeyError — missing dict key mid-path
  TypeError — expected list but got non-list at indexed token
  IndexError — list index out of range
"""
from __future__ import annotations

import re
from typing import Any

_PATH_TOKEN_RE = re.compile(r"([^.\[\]]+)(?:\[(\d+)\])?")


def apply_patch_in_place(d: dict[str, Any], path: str, new_value: Any) -> None:
    """Walk a dot-notation path with optional [N] indices; replace value in-place."""
    tokens = [
        (name, int(idx) if idx else None)
        for name, idx in _PATH_TOKEN_RE.findall(path)
        if name
    ]
    if not tokens:
        raise ValueError(f"Empty path: {path!r}")
    cur: Any = d
    for i, (name, idx) in enumerate(tokens):
        is_last = i == len(tokens) - 1
        if is_last and idx is None:
            cur[name] = new_value
            return
        if is_last and idx is not None:
            if not isinstance(cur.get(name), list):
                raise TypeError(f"Path {path!r}: expected list at {name!r}")
            if idx >= len(cur[name]):
                raise IndexError(f"Path {path!r}: index {idx} out of range for {name!r}")
            cur[name][idx] = new_value
            return
        if name not in cur:
            raise KeyError(f"Path {path!r}: missing key {name!r} at depth {i}")
        cur = cur[name]
        if idx is not None:
            if not isinstance(cur, list):
                raise TypeError(f"Path {path!r}: expected list at {name!r}")
            if idx >= len(cur):
                raise IndexError(f"Path {path!r}: index {idx} out of range for {name!r}")
            cur = cur[idx]
