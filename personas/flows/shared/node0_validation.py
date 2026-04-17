"""Node 0 input validation — pure Python, no API call.

Implements the spec's Node 0:
- type must be valid
- voice_mode must be one of {philosophical, observational, narratival}
  (null allowed for subtype=system voices)
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

    # voice_mode — strict three-value enum; null allowed for subtype=system only
    vmode = voice_input.get("voice_mode")
    _subtype_for_mode = voice_input.get("subtype")
    _valid_voice_modes = {"philosophical", "observational", "narratival"}
    if _subtype_for_mode == "system":
        # system entities bypass voice_mode branching; null is the correct value
        if vmode is not None:
            raise InputRejected(
                status="REJECTED",
                reason=(
                    f"subtype=system voices must have voice_mode=null (system "
                    f"entities use subtype overrides, not voice_mode branching). "
                    f"Got {vmode!r}."
                ),
            )
    else:
        if vmode not in _valid_voice_modes:
            raise InputRejected(
                status="REJECTED",
                reason=(
                    f"Invalid voice_mode {vmode!r}. Must be one of: "
                    f"{sorted(_valid_voice_modes)}. "
                    f"(subtype=system voices may use null.)"
                ),
            )

    # subtype — required for non-human, optional otherwise
    subtype = voice_input.get("subtype")
    if vtype == "non-human":
        non_human_subtypes = {"organism", "system"}
        if subtype not in non_human_subtypes:
            raise InputRejected(
                status="REJECTED",
                reason=(
                    f"non-human voices require a subtype from {sorted(non_human_subtypes)}. "
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
    normalized.setdefault("needs_dr_supplement", True)  # always trigger; cheap and adds depth
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
