"""Composed merged_dossier — output of Pass 1.7 coherence pass.

Aggregates all six chunks (1.1-1.6) + adds coherence_flags / resolutions.
This is the successor to v3.10's monolithic Pass 1-merge. Pass 2-6 read from
this object instead of the 6-section markdown.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from ._analytical import AnalyticalContext
from .pass_1_1 import FormativeCandidate, LifeScaffold
from .pass_1_2 import Commitment, Concept, Tension
from .pass_1_3 import ReasoningMethod, Textures
from .pass_1_4 import Moves, Register, Vocabulary
from .pass_1_5 import HardLimits, KnowledgeBoundary, SensitiveTopics
from .pass_1_6 import Passages, ReferenceOnlyPassages, Works


CoherenceSeverity = Literal["minor", "moderate", "major"]


class CoherenceFlag(BaseModel):
    """One cross-chunk consistency issue flagged by Pass 1.7."""

    flag_id: str = Field(..., description="Short label, e.g. 'CF-01'.")
    severity: CoherenceSeverity
    category: Literal[
        "cross_chunk_citation_mismatch",
        "commitment_formative_misalignment",
        "concept_undefined_in_reasoning",
        "voice_reasoning_mismatch",
        "anachronism_boundary_mismatch",
        "passage_work_orphan",
        "other",
    ]
    description: str = Field(..., description="1-3 sentences naming the issue.")
    affected_chunks: list[str] = Field(
        ..., description="e.g. ['1.1 formative_candidates', '1.2 commitments']"
    )


class CoherenceResolution(BaseModel):
    """How Pass 1.7 resolved (or declined to resolve) a flag."""

    flag_id: str
    resolution: str = Field(
        ..., description="What was changed, or why the flag was accepted as-is "
        "(productive tension rather than inconsistency)."
    )
    revised_field_path: str | None = Field(
        default=None,
        description="If a chunk output was revised, dotted path to the field "
        "(e.g. 'pass_1_2.commitments[3].operational_note').",
    )


class MergedDossier(BaseModel):
    """Chunks 1.1-1.6 composed + Pass 1.7 coherence metadata.

    Note on the `voice_register` / `register` aliasing:
    Pydantic's BaseModel metaclass inherits a `register()` method from the
    abstract-base-class machinery. Using `register` directly as a field name
    triggers `UserWarning: Field name "register" in "MergedDossier" shadows
    an attribute in parent "BaseModel"` plus a JSON-schema warning about the
    inherited method being treated as a default. We rename the Python
    attribute to `voice_register` but preserve the JSON key `register` via
    alias + serialization_alias + `populate_by_name=True`, so callers that
    read `merged_dossier["register"]` continue to work unchanged.

    All `.model_dump()` calls in runners that serialize to JSON consumed by
    the pipeline use `by_alias=True` — see run_pass_1_7.py.
    """

    model_config = ConfigDict(populate_by_name=True)

    # Chunk 1.1
    life_scaffold: LifeScaffold
    formative_candidates: list[FormativeCandidate]

    # Chunk 1.2
    commitments: list[Commitment]
    concepts: list[Concept]
    tensions: list[Tension]

    # Chunk 1.3
    reasoning_method: ReasoningMethod
    textures: Textures
    analytical_context_reasoning: AnalyticalContext = Field(
        default_factory=AnalyticalContext,
        description="1-arch-03 addition: scholarly-analytical material "
        "(structural_patterns, worked_demonstrations, scholarly_debates) "
        "preserved from merge layer. Default empty for voices without "
        "substantive reasoning-level scholarly context.",
    )

    # Chunk 1.4
    moves: Moves
    voice_register: Register = Field(
        ..., alias="register", serialization_alias="register",
        description="Voice register/tone block — aliased to JSON key 'register'.",
    )
    vocabulary: Vocabulary
    analytical_context_voice: AnalyticalContext | None = Field(
        default=None,
        description="1-arch-03 addition: scholarly-analytical material on "
        "voice-signature (stylistic-reception, translator-tradition "
        "criticism, metaphor-family scholarly mapping). Optional — null "
        "for voices without substantive voice-level scholarly context.",
    )

    # Chunk 1.5
    knowledge_boundary: KnowledgeBoundary
    sensitive_topics: SensitiveTopics
    hard_limits: HardLimits

    # Chunk 1.6 — `urls` removed per 1-arch-07 (2026-04-22); URL inventory
    # now derived at render-time via flows/shared/url_extract.extract_urls().
    works: Works
    passages: Passages
    reference_only_passages: ReferenceOnlyPassages = Field(
        default_factory=ReferenceOnlyPassages,
        description="Private-reasoning corpus; Step 1 loads, Step 2 drops. "
        "Usually empty for public-domain voices.",
    )

    # Pass 1.7 coherence metadata.
    coherence_flags: list[CoherenceFlag] = Field(default_factory=list)
    coherence_resolutions: list[CoherenceResolution] = Field(default_factory=list)
