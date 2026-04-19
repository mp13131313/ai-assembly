"""Pass 1.5 BOUNDARIES schema.

Fills the persona card's `knowledge_boundary`, `topics_requiring_care`,
`hard_limits`, and (via Pass 2 synthesis) parts of `translation_protocol`.

Knowledge boundaries are cosmology-specific, not just temporal — for Plato,
post-4th-century-BCE frameworks; for the Octopus, all human conceptual
categories; for the Whanganui, property/resource/nature-as-separable framings.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from ._conventions import EvidenceTag, SourceCitation


class KnowledgeBoundary(BaseModel):
    """What lies beyond this voice's world.

    General frame (1-3 sentences setting the conceptual boundary) plus a
    specific exclusion list that catches the things the model would
    otherwise slip on. For pre-modern voices: temporal exclusions. For
    non-human voices: ontological-access exclusions. For cultural voices
    within modernity: tradition-specific exclusions.
    """

    general_frame: str = Field(
        ...,
        description="1-3 sentences setting the boundary. Example for Plato: "
        "'Beyond my world: any event after ~348 BCE.'",
    )
    temporal_exclusions: list[str] = Field(
        default_factory=list,
        description="Specific post-period developments. Example: 'Christianity, "
        "Islam', 'The Roman Empire', 'Modern science'.",
    )
    geographic_exclusions: list[str] = Field(
        default_factory=list,
        description="Places outside this voice's known world.",
    )
    conceptual_exclusions: list[str] = Field(
        default_factory=list,
        description="Concepts this voice has no access to. For non-human "
        "organisms: human conceptual categories that do not register. For "
        "systems: modern property/resource framings. Tag each with the "
        "reason it's excluded.",
    )
    evidence_tag: EvidenceTag = "scholarly_consensus"
    citations: list[SourceCitation] = Field(default_factory=list)


class SensitiveTopic(BaseModel):
    """One topic where this voice's historical views require careful navigation.

    Not avoidance — engagement with care. Pass 2 uses these to build
    `topics_requiring_care`. Each entry: what the voice actually thought,
    and the framing that makes that thinking productive rather than
    offensive or sanitised (the sanitization paradox per baseline File 3).
    """

    topic: str
    what_the_voice_actually_thought: str = Field(
        ...,
        description="The substantive position, sourced. Do NOT sanitise.",
    )
    navigation_guidance: str = Field(
        ...,
        description="How to engage productively. Frame the thinking in the "
        "voice's own apparatus; acknowledge historical limitations where "
        "present; surface contradictions without resolving them.",
    )
    evidence_tag: EvidenceTag
    citations: list[SourceCitation] = Field(default_factory=list)


class SensitiveTopics(BaseModel):
    topics: list[SensitiveTopic]


class HardLimits(BaseModel):
    """3-5 absolute prohibitions — character-breaking moves this voice never makes.

    Minimal and focused on CATASTROPHIC character failure, not expression-level
    constraint. Expression-level constraints live in Pass 1.4's banned-language
    output (Pass 7c-derived). Hard limits catch: adopting modern vocabulary,
    breaking the characteristic mode of reasoning, producing arguments the
    voice structurally would not make, abandoning dialectic for declaration.
    """

    prohibitions: list[str] = Field(
        ...,
        description="3-5 absolute prohibitions. Each catches a specific "
        "failure mode the epistemic frame doesn't already cover. Example for "
        "Plato: 'Do not produce arguments from empirical data alone — always "
        "ask what principle the data reveals.'",
    )
    evidence_tag: EvidenceTag = "inference"
    citations: list[SourceCitation] = Field(default_factory=list)
