"""Shared schema conventions for the chunked Pass 1 merge.

# FROZEN as of 2026-04-19 per PB#7, after chunks 1.1 and 1.2 landed cleanly
# against Battuta fixtures. Changes require architectural decision review —
# see REBUILD_PLAN §"Locked architectural decisions". Chunks 1.3-1.6 reuse
# EvidenceTag / Tier / SourceCitation / ContestedReading / ProjectionWarning
# unchanged. Domain-specific fields emerge per chunk; meta stays stable.


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
    "contested",                  # active scholarly disagreement (e.g.
                                  # voice_level_debate frames, antisemitism
                                  # structural-vs-incidental, Williams-vs-
                                  # Frank on Myshkin, Bakhtin polyphony
                                  # relativism-vs-authorial-guidance).
                                  # Distinct from `inference` (a single
                                  # scholar's reasoned extrapolation):
                                  # `contested` means multiple credible
                                  # readings persist in the literature.
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
