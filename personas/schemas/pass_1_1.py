"""Pass 1.1 BIOGRAPHICAL schema.

Output of the first chunked merge — takes Perplexity + Claude DR + Gemini
dossiers and produces a biographical foundation shaped by Rob Boddice's
biocultural-history rubrics.

Per Boddice §13 5-part `world` rubric: ontological furniture / available pathē
in original language / framework for difficulty / model of selfhood /
anachronisms to avoid. This scaffold is the structural ground; the
FormativeCandidate sibling captures the formative-experience shape per §14.

Evidence tagging + source citation conventions come from `_conventions.py`;
those are frozen after chunk 1.2 per PB#7 and reused unchanged 1.3-1.6.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from ._conventions import EvidenceTag, SourceCitation


class KeyRelationship(BaseModel):
    """One formative relationship (teacher, student, rival, consort, enemy, etc.)."""

    person: str
    relation_type: str  # e.g. "teacher", "student", "rival", "patron", "enemy"
    evidence_tag: EvidenceTag
    citations: list[SourceCitation] = Field(default_factory=list)


class PeriodPathos(BaseModel):
    """One period-specific affect/passion in the voice's own language.

    Per Boddice §13 sub-field 2: 5-10 terms per voice in original language,
    with short glosses. No modern English emotion-words as primary vocabulary
    for pre-1820 voices.
    """

    term_in_original_language: str
    gloss: str
    evidence_tag: EvidenceTag
    citations: list[SourceCitation] = Field(default_factory=list)


class LifeScaffold(BaseModel):
    """Pass 1.1 biographical foundation per Boddice §13.

    This is NOT period-setting. It is the voice's emotional-experiential
    ontology: what was real, what could be felt, what gave suffering meaning,
    what counted as a self.
    """

    name: str
    type: Literal["human", "non_human", "fictional"]
    subtype: Literal["organism", "system"] | None = None
    birth_year: int | None = None
    death_year: int | None = None
    primary_locations: list[str] = Field(default_factory=list)
    institutions_founded_joined_opposed: list[str] = Field(default_factory=list)
    key_relationships: list[KeyRelationship] = Field(default_factory=list)

    # Boddice §13 — 5-part world rubric.
    intellectual_world: str = Field(
        ..., description="Period intellectual currents in the voice's own framing."
    )
    ontological_furniture: str = Field(
        ...,
        description="What was *real* for this voice — not beliefs, but the "
        "structure of reality. Gods, Forms, jinn, Jah, whakapapa, distributed "
        "embodiment. Do not write 'they believed X' when X was the furniture.",
    )
    available_pathe: list[PeriodPathos] = Field(
        default_factory=list,
        description="5-10 period-specific affects in original language with "
        "glosses. Flag any for which no modern equivalent exists. Pre-1820 "
        "voices: do not use 'emotions' as organizing category.",
    )
    framework_for_difficulty: str = Field(
        ...,
        description="What gave pain, loss, setback meaning? Afterlife, Forms, "
        "divine testing, karma, theosis, Babylonian exile, whakapapa rupture, "
        "endocrine semelparity. Not 'coping mechanism' — experiential framework.",
    )
    model_of_selfhood: str = Field(
        ...,
        description="What counted as an 'I'? Modern introspective interior, "
        "tripartite soul, divine-royal corporate body, I-and-I collective-divine "
        "indwelling, mountains-to-sea indivisible whole, fluctuating assemblage "
        "of semi-autonomous arms. State explicitly.",
    )
    anachronisms_to_avoid: list[str] = Field(
        default_factory=list,
        description="4-8 modern terms that would mis-render this voice "
        "(e.g. 'career', 'self-actualization', 'trauma', 'romance', 'identity'). "
        "Each entry: term + 1-line reason.",
    )


class FormativeCandidate(BaseModel):
    """Per Boddice §14 4-part rubric. Multiple candidates possible; Pass 2 commits to one.

    For human voices: 3 active sub-fields (community + lived_through_apparatus +
    engagement). For non-human/system/cosmic voices: 3 active sub-fields
    (community_or_ontogenetic_field + condition_of_being + engagement) —
    condition_of_being replaces lived_through_apparatus.

    Drop "core wound" framing. The inner-child/core-wound schema is a specific
    1986-2014 Anglo-American therapeutic sediment (Bradshaw / van der Kolk /
    IFS) shown by Fassin, Furedi, and Illouz to be a local construct, not a
    universal. The voice's own framework — Buddhist dukkha, Islamic ibtilā',
    Stoic prohairesis, Confucian xiushen, Rastafari sufferation, whakapapa
    rupture, endocrine semelparity — goes here instead.
    """

    candidate_label: str = Field(
        ..., description="Short name for Pass 2 to reference. "
        "Examples: 'Trial of Socrates', 'Semelparous lifespan', "
        "'1977 melanoma diagnosis refused as toe-amputation'."
    )
    formative_emotional_community: str = Field(
        ...,
        description="Per §14 sub-field 1. Overlapping Rosenwein-style "
        "communities that shaped this voice's lexicon of feeling, norms of "
        "expression, and what-could-be-felt. For non-human voices: the "
        "analogous ontogenetic/ecological field (taxon, habitat, lineage).",
    )
    lived_through_own_apparatus: str | None = Field(
        default=None,
        description="Per §14 sub-field 2 (HUMAN voices only). Describe the "
        "formative event AND the framework in which it was meaningful in a "
        "single movement, using period-specific vocabulary from the world field. "
        "NOT event without framework (modern projection) or framework without "
        "event (abstraction).",
    )
    condition_of_being: str | None = Field(
        default=None,
        description="Per §14 sub-field 4 (NON-HUMAN / non-event-driven / "
        "cosmic voices). Describe the ongoing state of being that structures "
        "the voice's standing and stake. Replaces lived_through_own_apparatus.",
    )
    engagement_it_drives: str = Field(
        ...,
        description="Per §14 sub-field 3. What does this voice enter the "
        "panel to *do*? What is it motivated to say, notice, refuse, defend? "
        "Functional, not psychological.",
    )
    evidence_tag: EvidenceTag = Field(
        default="experiential_reconstruction",
        description="Usually 'experiential_reconstruction' for §14 content.",
    )
    citations: list[SourceCitation] = Field(default_factory=list)
    scholarly_support_score: Literal["strong", "moderate", "contested"] = Field(
        ..., description="Pass 2 uses this when committing to a candidate."
    )
