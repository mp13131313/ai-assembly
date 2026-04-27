"""Pass 1.2 INTELLECTUAL schema.

Intellectual-framework chunk per REBUILD_PLAN C.1: Commitment + Concept +
Tension. Fills the persona card's `constitution`, `concept_lexicon`, and
(through Pass 2 synthesis) the tension-aware parts of `translation_protocol`
and `topics_requiring_care`.

Reuses `_conventions.py` meta-types unchanged. Per PB#7, after chunks 1.1 +
1.2 land, those conventions are FROZEN for chunks 1.3-1.6.

1-arch-03 additive-merge updates:
- Commitment + Concept gain scholarly_context for interpretive-tradition
  preservation (Frank vs. Bakhtin vs. Williams on Dostoevsky's commitments).
- Commitment gains contested_readings for scholar-disputed commitments.
- Concept gains translation_tradition_notes for translator-tradition-varied
  concepts (Garnett vs. P-V vs. Ready renderings of 'nadryv').
- Tension gains tension_type (productive/contested/unresolved) + scholarly_context.
- Counts become minimums not maximums per additive-merge discipline.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from ._conventions import ContestedReading, EvidenceTag, SourceCitation


class Commitment(BaseModel):
    """A deep commitment the voice reasons FROM (not about).

    Fills the persona card's `constitution` field. Pre-1-arch-03 targeted
    10-20 principles per voice; under 1-arch-03 this is the merge-layer
    output which preserves ALL sourced commitments (minimum 10, uncapped —
    well-documented voices may surface 20-40 at merge). Pass 3 synthesizes
    to card's 10-20 constitution principles via selection + compression.

    Specificity rules: "Prioritise knowledge over opinion" is too vague;
    "Prioritise knowledge of stable universal structures over opinion about
    changing particulars; when presented with empirical data, always ask what
    underlying principle the data reveals" is specific enough to steer the
    model. Two-voice swap test: if two voices with different frameworks could
    both honestly assert this commitment, it is too generic — tighten it.
    """

    statement: str = Field(..., description="The commitment, 1-2 sentences.")
    operational_note: str = Field(
        ...,
        description="How this principle should shape responses — the "
        "if-you-encounter-X-do-Y instruction. Must be concrete. No length cap.",
    )
    textual_source: str | None = Field(
        default=None,
        description="Primary-text grounding: passage + work + Stephanus / "
        "canonical reference. Null if commitment is inferred from practice.",
    )
    unique_to_this_voice: bool = Field(
        ...,
        description="True if distinctive — e.g. Plato's 'knowledge requires "
        "knowing the Form' is unique; 'value wisdom' is generic. Pass 7 "
        "cross-persona QC uses this flag to detect flattening.",
    )
    evidence_tag: EvidenceTag
    citations: list[SourceCitation] = Field(default_factory=list)

    # 1-arch-03 additions
    scholarly_context: str | None = Field(
        default=None,
        description="How different scholarly traditions frame this commitment. "
        "Example for Dostoevsky's 'choose Christ over truth' commitment: "
        "'Williams (2008) reads as existential wager; Frank (Mantle of the "
        "Prophet 2002) as post-katorga transformation; Kasatkina (2004) as "
        "Orthodox-kenotic theology; Shestov reads as irrational affirmation.' "
        "Preserve interpretive breadth; do not synthesize.",
    )
    contested_readings: list[ContestedReading] = Field(
        default_factory=list,
        description="Scholar-disputed commitments or contested framings of "
        "this commitment. Preserve the debate at merge; Pass 3 synthesis "
        "may keep or collapse based on card-field demands.",
    )


class Concept(BaseModel):
    """A key term this voice uses with period-specific precision.

    Fills the persona card's `concept_lexicon`. Under 1-arch-03: minimum 5
    concepts, uncapped maximum — preserve all period-vocabulary + tradition-
    specific concepts from sources. Pass 3 selects for card's 5-10.

    The `what_it_rules_out` exclusion is load-bearing — prevents the model
    from sliding into common English usage. File 3 Failure 3 addressed at
    prompt-discipline level: 'generic philosophical positions' prevented
    by mandatory exclusion structure.
    """

    term: str = Field(..., description="The term as the voice uses it.")
    term_in_original_language: str | None = Field(
        default=None,
        description="Period-language form if distinct from the English term. "
        "Examples: episteme, ibtilā', sobornost', mauri, nadryv.",
    )
    definition: str = Field(
        ..., description="The voice's definition, not the modern English one. "
        "No length cap; preserve source detail."
    )
    what_it_rules_out: str = Field(
        ...,
        description="The exclusion — what this concept IS NOT. Prevents "
        "drift into common usage. Example: episteme rules out treating "
        "polling data or majority opinion as knowledge-in-the-full-sense. "
        "No length cap.",
    )
    textual_source: str | None = None
    unique_to_this_voice: bool
    evidence_tag: EvidenceTag
    citations: list[SourceCitation] = Field(default_factory=list)

    # 1-arch-03 additions
    translation_tradition_notes: str | None = Field(
        default=None,
        description="For concepts with translator-tradition variation. Example "
        "for Dostoevsky's 'nadryv': 'Garnett renders as laceration; Pevear-"
        "Volokhonsky preserves nadryv untranslated; Ready renders as rupture. "
        "The Russian carries both physical-wound and moral-self-torture "
        "senses that no single English term preserves. For primary-text "
        "grounding prefer P-V or original-language; for reader-accessibility "
        "Garnett.' Preserve translator debate; Pass 4a selects which "
        "translation to anchor voice exemplar.",
    )
    scholarly_context: str | None = Field(
        default=None,
        description="Scholarly interpretive tradition on this concept. "
        "Named scholars + positions where consensus is contested.",
    )


class Tension(BaseModel):
    """An unresolved internal tension in the voice's thought.

    Pass 2 uses these to populate `topics_requiring_care` and to prevent
    false-consensus resolution in `constitution`. Tensions are (per 1.7
    productive-tension criteria): both poles have primary-text or scholarly
    support; tension drives rather than derails the voice's thinking;
    scholarly tradition names the tension explicitly. If any criterion unmet,
    it's a real contradiction — Pass 1.7 coherence handles resolution.

    Under 1-arch-03: tension_type classifies for downstream handling;
    scholarly_context preserves interpretive-tradition framing.
    """

    description: str = Field(
        ..., description="The tension, named explicitly. 1-2 sentences. "
        "Example: 'Plato's Republic argues philosopher-kings should rule "
        "without written law; the Laws argues constitutional constraints "
        "are necessary because philosopher-kings are rare and unreliable.'"
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

    # 1-arch-03 additions
    tension_type: Literal["productive", "contested", "unresolved"] = Field(
        default="productive",
        description="Classification for downstream handling. "
        "'productive' — texture of the thinking; preserve and do not flatten "
        "(Plato Republic-vs-Laws). "
        "'contested' — scholarly tradition divides on whether this is genuine "
        "tension or interpretive disagreement. "
        "'unresolved' — real logical contradiction that should surface in "
        "Pass 7 validation as candidate for escalation.",
    )
    scholarly_context: str | None = Field(
        default=None,
        description="Interpretive-tradition framing of the tension. "
        "Example: 'Morson/Emerson (1990) insist polyphony and carnivalization "
        "are distinct analytical concepts that must not be collapsed; Scanlan "
        "(2002) treats them as complementary; Emerson's warning matters for "
        "constitutional synthesis — the two concepts do different work.'",
    )
