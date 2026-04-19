"""Pass 1.2 INTELLECTUAL schema.

Intellectual-framework chunk per REBUILD_PLAN C.1: Commitment + Concept +
Tension. Fills the persona card's `constitution`, `concept_lexicon`, and
(through Pass 2 synthesis) the tension-aware parts of `translation_protocol`
and `topics_requiring_care`.

Reuses `_conventions.py` meta-types unchanged. Per PB#7, after chunks 1.1 +
1.2 land, those conventions are FROZEN for chunks 1.3-1.6.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from ._conventions import EvidenceTag, SourceCitation


class Commitment(BaseModel):
    """A deep commitment the voice reasons FROM (not about).

    Fills the persona card's `constitution` field (10-20 principles per voice).
    Specificity rules: "Prioritise knowledge over opinion" is too vague;
    "Prioritise knowledge of stable universal structures over opinion about
    changing particulars; when presented with empirical data, always ask what
    underlying principle the data reveals" is specific enough to steer the
    model.
    """

    statement: str = Field(..., description="The commitment, 1-2 sentences.")
    operational_note: str = Field(
        ...,
        description="How this principle should shape responses — the "
        "if-you-encounter-X-do-Y instruction. Must be concrete.",
    )
    textual_source: str | None = Field(
        default=None,
        description="Primary-text grounding: passage + work + Stephanus / "
        "canonical reference. Null if commitment is inferred from practice.",
    )
    unique_to_this_voice: bool = Field(
        ...,
        description="True if distinctive — e.g. Plato's 'knowledge requires "
        "knowing the Form' is unique; 'value wisdom' is generic.",
    )
    evidence_tag: EvidenceTag
    citations: list[SourceCitation] = Field(default_factory=list)


class Concept(BaseModel):
    """A key term this voice uses with period-specific precision.

    Fills the persona card's `concept_lexicon` field (5-10 concepts per voice).
    The `what_it_rules_out` exclusion is load-bearing — prevents the model
    from sliding into common English usage.
    """

    term: str = Field(..., description="The term as the voice uses it.")
    term_in_original_language: str | None = Field(
        default=None,
        description="Period-language form if distinct from the English term. "
        "Examples: episteme, ibtilā', sobornost', mauri.",
    )
    definition: str = Field(
        ..., description="The voice's definition, not the modern English one."
    )
    what_it_rules_out: str = Field(
        ...,
        description="The exclusion — what this concept IS NOT. Prevents "
        "drift into common usage. Example: episteme rules out treating "
        "polling data or majority opinion as knowledge-in-the-full-sense.",
    )
    textual_source: str | None = None
    unique_to_this_voice: bool
    evidence_tag: EvidenceTag
    citations: list[SourceCitation] = Field(default_factory=list)


class Tension(BaseModel):
    """An unresolved internal tension in the voice's thought.

    Pass 2 uses these to populate `topics_requiring_care` and to prevent
    false-consensus resolution in `constitution`. Tensions are productive:
    they mark where the voice's reasoning genuinely divides.
    """

    description: str = Field(
        ..., description="The tension, named explicitly. 1-2 sentences."
    )
    conflicting_commitments: list[str] = Field(
        default_factory=list,
        description="References to Commitment.statement values or short "
        "summary labels for the commitments that pull against each other.",
    )
    passage_citations: list[SourceCitation] = Field(default_factory=list)
    evidence_tag: EvidenceTag = Field(
        default="scholarly_consensus",
        description="Usually scholarly_consensus (tensions are typically "
        "identified in the literature); occasionally inference.",
    )
