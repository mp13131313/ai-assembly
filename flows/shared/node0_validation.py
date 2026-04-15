"""Node 0 input validation — pure Python, no API call.

Implements the v3.7 spec's Node 0:
- impossible must be true (Assembly requires impossible participants)
- type must be valid
- voice_mode must be valid
- subtype must be valid (and required if type is non-human)
- corpus_constraint must be valid

Returns a normalized input dict on success, raises ValueError with the
spec's REJECTED message on failure.
"""

from __future__ import annotations

from typing import Any

from .io import (
    VALID_CORPUS_CONSTRAINTS,
    VALID_SUBTYPES,
    VALID_TYPES,
    VALID_VOICE_MODES,
)


class InputRejected(ValueError):
    """Raised when Node 0 rejects an input — pipeline must not proceed."""

    def __init__(self, status: str, reason: str, action: str = ""):
        self.status = status
        self.reason = reason
        self.action = action
        super().__init__(f"{status}: {reason}" + (f" ({action})" if action else ""))


def validate_input(voice_input: dict[str, Any]) -> dict[str, Any]:
    """Validate a voice input dict and return it normalized.

    Raises InputRejected on any v3.7 spec violation.
    """
    name = voice_input.get("name", "<unknown>")

    # impossible — hard gate. Living, reachable figures violate the premise.
    impossible = voice_input.get("impossible")
    if impossible is not True:
        raise InputRejected(
            status="REJECTED",
            reason=(
                f"{name} is not flagged as an impossible participant. The "
                f"Assembly requires voices that cannot physically attend: "
                f"the dead, the non-human, the fictional. Living, reachable "
                f"figures violate the core premise."
            ),
            action=(
                "If this figure has recently died or become unreachable, "
                "update the impossible field to true and re-run."
            ),
        )

    # type
    vtype = voice_input.get("type")
    if vtype not in VALID_TYPES:
        raise InputRejected(
            status="REJECTED",
            reason=(
                f"Invalid type {vtype!r}. Must be one of: "
                f"{sorted(VALID_TYPES)}."
            ),
        )

    # voice_mode
    vmode = voice_input.get("voice_mode")
    if vmode not in VALID_VOICE_MODES:
        raise InputRejected(
            status="REJECTED",
            reason=(
                f"Invalid voice_mode {vmode!r}. Must be one of: "
                f"{sorted(VALID_VOICE_MODES)}."
            ),
        )

    # subtype — required for non-human, ignored otherwise
    subtype = voice_input.get("subtype")
    if vtype == "non-human":
        if subtype not in {"organism", "system"}:
            raise InputRejected(
                status="REJECTED",
                reason=(
                    f"non-human voices require subtype 'organism' or 'system'. "
                    f"Got {subtype!r}."
                ),
            )
    else:
        if subtype not in VALID_SUBTYPES:
            raise InputRejected(
                status="REJECTED",
                reason=(
                    f"Invalid subtype {subtype!r} for type {vtype!r}. "
                    f"Allowed: {sorted(VALID_SUBTYPES, key=str)}."
                ),
            )

    # corpus_constraint
    cc = voice_input.get("corpus_constraint", "full")
    if cc not in VALID_CORPUS_CONSTRAINTS:
        raise InputRejected(
            status="REJECTED",
            reason=(
                f"Invalid corpus_constraint {cc!r}. Must be one of: "
                f"{sorted(VALID_CORPUS_CONSTRAINTS)}."
            ),
        )

    # Required string fields
    for field in ["name", "conference_context"]:
        if not voice_input.get(field):
            raise InputRejected(
                status="REJECTED",
                reason=f"Missing required field: {field!r}",
            )

    # Defaults for optional flags
    normalized = dict(voice_input)
    normalized.setdefault("hostile_sources", False)
    normalized.setdefault("needs_dr_supplement", False)
    normalized.setdefault("primary_text_sources", [])
    normalized.setdefault("subtype", None)
    normalized.setdefault("corpus_constraint", "full")
    normalized.setdefault("casting_rationale", "")
    # Approach C: optional path to a manually-produced Claude Deep Research
    # markdown dossier (run in claude.ai with Opus + extended thinking + DR).
    # When present, Pass 1-merge does a three-way contradiction check across
    # Perplexity, Claude DR, and Gemini.
    normalized.setdefault("pass_1a_claude_dr_file", None)

    return normalized
