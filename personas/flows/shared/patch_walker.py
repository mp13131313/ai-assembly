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

FU#51 (2026-04-27) — `resolve_field_to_pass()` rewrites a field_issue's
`flagged_pass` label to the pass file that actually contains the field.
Pass 7a's validator (gpt-5.4 high) labels `flagged_pass` by topical/domain
category rather than by which pass file the field lives in (e.g. tags
`epistemic_frame_statement` as `flagged_pass=5` because it's
engagement-related, but the field actually lives in pass_2). Belt-and-
braces guard against validator drift; complements the prompt-side fix.
"""
from __future__ import annotations

import re
from typing import Any

_PATH_TOKEN_RE = re.compile(r"([^.\[\]]+)(?:\[(\d+)\])?")


def _top_level_field(path: str) -> str | None:
    """Extract the top-level field name from a dot-notation path.

    Examples:
      "epistemic_frame_statement" -> "epistemic_frame_statement"
      "world.framework_for_difficulty" -> "world"
      "topics_requiring_care[0]" -> "topics_requiring_care"
      "constitution.principles[3].evidence" -> "constitution"
    """
    if not path:
        return None
    m = _PATH_TOKEN_RE.match(path)
    if not m:
        return None
    name = m.group(1)
    return name or None


def resolve_field_to_pass(
    field_path: str,
    pass_outputs: dict[str, dict[str, Any]],
    fallback: str | None = None,
) -> str | None:
    """Look up which pass file actually contains the field.

    `pass_outputs` is `{pass_id: fields_dict}` for each pass file on disk
    (e.g., `{"2": pass2["fields"], "3": pass3["fields"], ...}`).

    Returns the pass_id (str) of the pass whose fields contain the
    top-level key of field_path. Returns `fallback` if the field is not
    found in any pass (could legitimately happen for a synthetic field
    name from a validator that misnamed the field).
    """
    top = _top_level_field(field_path)
    if not top:
        return fallback
    for pass_id, fields in pass_outputs.items():
        if isinstance(fields, dict) and top in fields:
            return pass_id
    return fallback


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
