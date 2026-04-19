"""Shared schema conventions for the chunked Pass 1 merge.

These meta-types — evidence tagging, source citation, tier hierarchy, contested
readings — are intended to be shared unchanged across chunks 1.1-1.6. Per PB#7
(REBUILD_PLAN §"Locked architectural decisions"), these conventions are frozen
after chunks 1.1 and 1.2 land cleanly; subsequent chunks reuse them as-is.

Boddice biocultural addenda (compass_artifact §12):
- `experiential_reconstruction` marks any claim about what the voice
  felt/meant/experienced as the builder's best biocultural-contextual guess.
- `projection_warning` marks any modern English term used faute de mieux that
  is known to distort; each carries a distortion_explanation.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


EvidenceTag = Literal[
    "stated",
    "scholarly_consensus",
    "inference",
    "experiential_reconstruction",
    "projection_warning",
]

Tier = Literal[
    "tier_1_primary",
    "tier_2_scholarly",
    "tier_3_contested",
]


class SourceCitation(BaseModel):
    """A single citation supporting a claim."""

    author: str
    work: str
    year: int | None = None
    page: str | None = None
    url: str | None = None
    tier: Tier


class ContestedReading(BaseModel):
    """A scholarly debate surfaced in the merge rather than resolved into false consensus."""

    consensus_view: str
    minority_view: str
    scholars_per_view: list[str] = Field(
        default_factory=list,
        description="Flat list like ['Vlastos (consensus)', 'Griswold (minority)'].",
    )


class ProjectionWarning(BaseModel):
    """A modern English term used because no better word exists, flagged.

    Pass 7c emits a list[ProjectionWarning] under `projection_warnings[]` per
    REBUILD_PLAN decisions log #16.
    """

    term: str
    distortion_explanation: str
