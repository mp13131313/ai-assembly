"""Shared I/O helpers for AI Assembly flows.

This module holds the contract-enforcement layer between stages: loaders
that normalize older file shapes, path resolvers, and atomic writers.

The most important function here is `load_session_package` — it handles
both pre- and post-turn_index versions of session_package.json, so the
Researcher flow doesn't have to care which one it got.
"""

from __future__ import annotations

import json
import logging
import re
import sys
from pathlib import Path
from typing import Any


def load_session_package(path: Path | str) -> dict[str, Any]:
    """Load a session_package.json, defensively injecting `turn_index` if absent.

    Session packages produced by transcription_flow.py on or after
    Apr 14 2026 include an explicit `turn_index` field on each turn.
    Older packages do not — `turn_index` is implicit via array position.
    This loader normalizes both shapes so downstream consumers (Researcher,
    Provocateur, etc.) can always rely on `turn_index` being present.

    Every turn in the returned dict is guaranteed to have a `turn_index`
    field equal to its position in the `transcript.turns` array.
    """
    path = Path(path)
    with path.open() as f:
        pkg = json.load(f)

    turns = pkg.get("transcript", {}).get("turns", [])
    for i, turn in enumerate(turns):
        if "turn_index" not in turn:
            turn["turn_index"] = i
        elif turn["turn_index"] != i:
            # The contract says turn_index must match array position.
            # If it doesn't, something upstream reordered without updating
            # the indices. Fail loudly rather than silently corrupt.
            raise ValueError(
                f"{path}: turn at position {i} has turn_index={turn['turn_index']}. "
                f"turn_index must equal array position."
            )
    return pkg


def write_json_atomic(path: Path | str, data: Any) -> None:
    """Write JSON to `path` via a temp file + rename, so partial writes
    can never leave a truncated file on disk. Indented, UTF-8, no ASCII
    escaping (preserves accented names)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    tmp.replace(path)


# Prompts live as standalone .md files under flows/shared/prompts/ so they
# can be reviewed in git without wading through Python string literals,
# edited at 2am without touching code, and compared directly against the
# canonical prompt specs in AI_Assembly_*_Pipeline.md.
_PROMPTS_DIR = Path(__file__).parent / "prompts"


def load_prompt(name: str) -> str:
    """Load a prompt by name from flows/shared/prompts/{name}.md.

    The `.md` extension is implicit. Trailing whitespace is stripped so
    prompts don't end with a spurious newline that some models interpret
    as the start of the response."""
    path = _PROMPTS_DIR / f"{name}.md"
    if not path.exists():
        raise FileNotFoundError(
            f"Prompt not found: {path}. "
            f"Expected a .md file in {_PROMPTS_DIR}."
        )
    return path.read_text().rstrip()



_COUNCIL_DIR = Path(__file__).resolve().parent / "council"
_COUNCIL_CONFIG_PATH = _COUNCIL_DIR / "council_config.json"

# Fields every council member is required to have, per the Provocateur
# Pipeline spec. Enforced at load time so downstream tasks can rely on
# them being present without defensive None-checking.
_REQUIRED_MEMBER_FIELDS = {
    "name",
    "speaks_from",
    "core_commitment",
    "activates_on",
    "goes_flat_on",
    "stretch",
    "translation_range",
    "stance_tendency",
    "medium",
}

_REQUIRED_CONFIG_TOP_LEVEL = {
    "version",
    "collective_landscape",
    "audience",
    "members",
}


def load_council_config(path: Path | str | None = None) -> dict[str, Any]:
    """Load and validate the Provocateur's council configuration.

    The council config is the hot-swap surface for the Provocateur —
    everything the Provocateur knows about the AI Assembly council
    (collective landscape, audience, individual member profiles, and
    editorial knobs like conceptual_axes) lives in one JSON file and
    is loaded at run time. Edit the file, re-run the flow, done.

    This loader enforces the schema: top-level required fields must be
    present, every member must have all eight required profile fields,
    and the `members` array must be non-empty. Fails loudly on any
    missing field rather than silently degrading later.

    Args:
        path: Optional override for testing. Defaults to the canonical
            location at flows/shared/council/council_config.json.

    Returns:
        The parsed config as a dict. The returned dict is trusted by
        downstream tasks — missing fields have already been caught.

    Raises:
        FileNotFoundError: If the config file doesn't exist.
        ValueError: If required fields are missing or `members` is empty.
    """
    config_path = Path(path) if path is not None else _COUNCIL_CONFIG_PATH
    if not config_path.exists():
        raise FileNotFoundError(
            f"Council config not found at {config_path}. "
            f"Expected a JSON file. See flows/shared/council/README.md "
            f"for the schema."
        )
    with open(config_path, encoding="utf-8") as f:
        cfg = json.load(f)

    missing_top = _REQUIRED_CONFIG_TOP_LEVEL - set(cfg.keys())
    if missing_top:
        raise ValueError(
            f"Council config at {config_path} is missing required "
            f"top-level fields: {sorted(missing_top)}"
        )

    members = cfg.get("members", [])
    if not isinstance(members, list) or not members:
        raise ValueError(
            f"Council config at {config_path} has no members. "
            f"Expected a non-empty `members` array."
        )

    for i, member in enumerate(members):
        missing = _REQUIRED_MEMBER_FIELDS - set(member.keys())
        if missing:
            name = member.get("name", f"<index {i}>")
            raise ValueError(
                f"Council member '{name}' is missing required fields: "
                f"{sorted(missing)}"
            )

    return cfg


def get_logger(name: str) -> Any:
    """Return a logger that works inside or outside a Prefect run context.

    Tasks call `get_run_logger()` to get Prefect's structured logger, but
    that call raises MissingContextError when invoked outside a Prefect
    task run (e.g. from a rerun script that calls `.fn`). This helper
    returns the Prefect run logger when available and falls back to a
    stdlib logger (named `name`, with a stderr handler at INFO) otherwise.

    The stdlib logger is configured once per name; subsequent calls with
    the same name reuse it without attaching duplicate handlers.
    """
    try:
        from prefect import get_run_logger
        return get_run_logger()
    except Exception:
        logger = logging.getLogger(name)
        if not logger.handlers:
            h = logging.StreamHandler(sys.stderr)
            h.setFormatter(logging.Formatter("%(levelname)s %(message)s"))
            logger.addHandler(h)
            logger.setLevel(logging.INFO)
        return logger


def extract_json(text: str) -> Any:
    """Parse the first complete JSON value out of a model response.

    Handles three failure modes seen across Researcher/Provocateur runs:
    1. Markdown code fence wrapping (```json ... ```)
    2. Leading/trailing whitespace
    3. Trailing commentary after a valid JSON value — models occasionally
       write a short note after the closing brace despite instructions.

    Uses json.JSONDecoder.raw_decode() to extract the first complete
    value and ignore anything after it. Falls back to locating the
    first '{' if the leading text isn't itself valid JSON.
    """
    t = text.strip()
    if t.startswith("```"):
        t = re.sub(r"^```(?:json)?\s*", "", t)
        t = re.sub(r"\s*```\s*$", "", t)
        t = t.strip()

    decoder = json.JSONDecoder()
    try:
        value, _end = decoder.raw_decode(t)
        return value
    except json.JSONDecodeError:
        start = t.find("{")
        if start == -1:
            # Let the original error propagate via strict parse so the
            # caller sees a meaningful message.
            return json.loads(t)
        value, _end = decoder.raw_decode(t[start:])
        return value


def get_member_by_name(cfg: dict[str, Any], name: str) -> dict[str, Any]:
    """Look up a single council member profile by name.

    Used by the Provocateur's Formulation step when it needs to load
    the full 8-field profile for each member assigned to a theme.
    Name matching is exact and case-sensitive — Formulation passes
    names that were emitted by Triage/Selection, which themselves
    come from the council config, so the strings should round-trip.

    Raises ValueError if the name is not found, with a list of the
    available names to make typos easy to spot.
    """
    for member in cfg.get("members", []):
        if member.get("name") == name:
            return member
    available = [m.get("name") for m in cfg.get("members", [])]
    raise ValueError(
        f"Council member '{name}' not found. "
        f"Available: {available}"
    )
