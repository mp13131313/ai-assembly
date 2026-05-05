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
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Any


def assert_run_dir_night_matches(run_dir: Path, night: int) -> None:
    """Defensive check: --night must match the night embedded in run_dir name.

    Both Convention A (`athens_2026_2026_05_07_night1`) and the
    legacy ingest format (`athens_night_1`) embed the night number in
    the run_dir's last path segment. If the run_dir name embeds
    `_night<N>` or `_night_<N>`, verify the supplied --night argument
    matches it. If they don't match, refuse to run with a clear error.

    The dangerous failure mode this guards against: voice_flow run with
    --night=1 against Night 2's run_dir would generate
    `voices/<slug>/continuity_night_2.json` from Night 2's data,
    silently overwriting the file that legitimately summarized Night 1
    for Night 2's voice cards. Cross-night state corruption that's hard
    to spot post-hoc — best caught at the moment of misuse.

    Run_dirs without an embedded night number (legacy dryruns,
    test fixtures, ad-hoc names) skip the check gracefully — the
    regex falls through and no error is raised.
    """
    name = Path(run_dir).name
    m = re.search(r"_night[_]?(\d+)\b", name)
    if not m:
        return  # no embedded night; skip check
    rd_night = int(m.group(1))
    if rd_night != night:
        raise SystemExit(
            f"--night={night} does not match the night embedded in run_dir "
            f"name ('{name}' carries night={rd_night}). Refusing to run.\n"
            f"\n"
            f"This guard catches cross-night state corruption: with the wrong "
            f"--night, voice_flow would write continuity_night_<N+1>.json from "
            f"the wrong night's data, silently overwriting valid prior-night "
            f"continuity. Either fix --night or pick the right run_dir.\n"
            f"\n"
            f"If you're certain you want to override (e.g. testing), rename the "
            f"run_dir to remove the embedded night number."
        )


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
    escaping (preserves accented names).

    Uses mkstemp so concurrent writes to the same path don't race on a
    shared .tmp filename. Cleans up the temp file on failure.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=str(path.parent)
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except FileNotFoundError:
            pass
        raise


def member_slug(name: str) -> str:
    """Convert a council member name to a filesystem-safe slug.

    Lowercases, collapses any run of non-alphanumerics to a single
    underscore, strips leading/trailing underscores.

    C34 (2026-05-04): strip the "Voice of [the] " prefix introduced by
    the athens-2026 naming convention rollout (commit `e8751f5`) so a
    council_config that uses "Voice of Plato" / "Voice of the Octopus"
    still resolves to the per-voice folder slugs `plato/` / `octopus/`.
    Backward-compatible: short names ("Plato") slug as before.
    """
    name = re.sub(r"^\s*Voice\s+of\s+(?:the\s+)?", "", name, flags=re.IGNORECASE)
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


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



_COUNCIL_DIR = Path(__file__).resolve().parent / "council"  # docs + schema live here
# Per Tier 3 (2026-04-20), the council_config.json JSON itself lives under
# PROJECT_ROOT (project data — derived from the persona pipeline's per-voice
# Provocateur Profiles). The README at _COUNCIL_DIR/README.md stays in code.
# `load_council_config()` below resolves PROJECT_ROOT via the shared module.

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
    present, every member must have all nine required profile fields,
    and the `members` array must be non-empty. Fails loudly on any
    missing field rather than silently degrading later.

    Args:
        path: Optional override for testing. Defaults to
            `$PROJECT_ROOT/council_config.json` per Tier 3 (2026-04-20).
            Previously lived at `flows/shared/council/council_config.json`
            under the code repo.

    Returns:
        The parsed config as a dict. The returned dict is trusted by
        downstream tasks — missing fields have already been caught.

    Raises:
        FileNotFoundError: If the config file doesn't exist.
        ValueError: If required fields are missing or `members` is empty.
    """
    if path is None:
        from flows.shared.project_root import resolve_project_root
        config_path = resolve_project_root(None, repo_root=None) / "council_config.json"
    else:
        config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(
            f"Council config not found at {config_path}. "
            f"Expected a JSON file at $PROJECT_ROOT/council_config.json. "
            f"See flows/shared/council/README.md for the schema."
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

    # Warn if we're running against a stub council config. The notes field
    # in council_config.json says to replace stubs before production; the
    # pipeline runs fine on stubs but output quality will be lower.
    version = str(cfg.get("version", ""))
    if "stub" in version.lower():
        import warnings
        warnings.warn(
            f"Loading council config with stub version '{version}'. "
            f"Member profiles are hand-written placeholders, not derived "
            f"from completed Persona Cards. Replace before production.",
            stacklevel=2,
        )

    # Check that member_slug is unique across members — we use it as the
    # filesystem key for per-voice checkpoints. Two members with the same
    # slug would silently overwrite each other's triage_voices/ and
    # formulations/ files.
    slugs: dict[str, str] = {}
    for m in members:
        s = member_slug(m["name"])
        if s in slugs:
            raise ValueError(
                f"Council member slug collision: '{m['name']}' and '{slugs[s]}' "
                f"both produce slug '{s}'. Rename one in council_config.json."
            )
        slugs[s] = m["name"]

    return cfg


def load_conference_facts(path: Path | str | None = None) -> dict[str, Any]:
    """Load conference_facts.json from PROJECT_ROOT.

    Carries deployment-side context not bound to any one voice — the
    gathering's identity, dates, venues, twelve thematic tracks,
    `conference_context_paragraph` (room character) and
    `session_role_for_ai_assembly` (the conceit-of-the-experiment text).

    Editor card_assembly reads this for the deployment-context system-
    prompt block (room/role/panel). Voice card_assembly reads it for
    its own deployment-context block. Persona pipeline Pass 0a also
    reads it for voice_config classification.

    Returns the parsed dict with no schema enforcement (the file is
    operator-curated; missing fields fail at the consumer's get-with-
    default).

    Raises:
        FileNotFoundError: If the file doesn't exist at the expected path.
    """
    if path is None:
        from flows.shared.project_root import resolve_project_root
        config_path = resolve_project_root(None, repo_root=None) / "conference_facts.json"
    else:
        config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(
            f"conference_facts.json not found at {config_path}. "
            f"Expected a JSON file at $PROJECT_ROOT/conference_facts.json."
        )
    with open(config_path, encoding="utf-8") as f:
        return json.load(f)


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
