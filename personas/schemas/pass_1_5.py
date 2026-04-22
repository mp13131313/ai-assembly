"""Pass 1.5 BOUNDARIES schema.

Fills the persona card's `knowledge_boundary`, `topics_requiring_care`,
`hard_limits`, and (via Pass 2 synthesis) parts of `translation_protocol`.

Knowledge boundaries are cosmology-specific, not just temporal — for Plato,
post-4th-century-BCE frameworks; for the Octopus, all human conceptual
categories; for the Whanganui, property/resource/nature-as-separable framings;
for fictional voices, narrative-internal + translation-tradition boundaries.

1-arch-03 additive-merge additions:
- `ExclusionEntry` structured form (backward-compat via discriminated union).
- `SensitiveTopic.scholarly_reception` preserves interpretive-tradition
  breadth on contested topics (Morson vs. McReynolds vs. Goldstein on
  Dostoevsky's Jewish question).
- `Prohibition` structured form for hard_limits (backward-compat).
- Counts become minimums not maximums per additive-merge discipline.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from ._conventions import EvidenceTag, SourceCitation
from .pass_1_1 import AnachronismEntry  # 1-arch-08: consolidated home is KnowledgeBoundary


class ExclusionEntry(BaseModel):
    """Structured exclusion entry — richer than bare string.

    1-arch-03 addition. Backward-compat preserved via discriminated union
    list[str | ExclusionEntry] in KnowledgeBoundary.

    Example for Plato's conceptual_exclusions: {
        term: "'personality'",
        reason_excluded: "imports 20th-C trait theory (Allport, Cattell, Big
                         Five) foreign to Greek character-grammar; use sōphrosynē /
                         tripartite soul / hexis instead",
        voice_native_alternative: "character in period-vocabulary per Boddice §15"
    }
    """

    term: str
    reason_excluded: str = Field(
        ..., description="1-line reason this term is excluded. "
        "Preserve scholarly reasoning where source provides.",
    )
    voice_native_alternative: str | None = Field(
        default=None,
        description="Voice's own tradition-specific term if one exists. "
        "For pre-modern voices this is usually where period-vocabulary lives.",
    )
    evidence_tag: EvidenceTag = Field(default="scholarly_consensus")
    citations: list[SourceCitation] = Field(default_factory=list)


class KnowledgeBoundary(BaseModel):
    """What lies beyond this voice's world.

    General frame (1-3 sentences setting the conceptual boundary) plus
    specific exclusion lists that catch the things the model would otherwise
    slip on. Voice-type-branched:
    - Pre-modern voices: temporal boundary primary
    - Non-human organisms: ontological-access boundary
    - Non-human systems: mediation/framework boundary
    - Fictional voices: narrative-internal + translation-tradition boundary
    - Cultural voices within modernity: tradition-specific exclusions

    1-arch-03: exclusion lists accept structured ExclusionEntry (preferred)
    or bare str (backward-compat). Uncapped maximums per additive-merge.
    """

    general_frame: str = Field(
        ...,
        description="1-3 sentences setting the boundary. Example for Plato: "
        "'Beyond my world: any event after ~348 BCE.' For Scheherazade: "
        "'Beyond my world: what the text does not include. I know 1001 "
        "nights; I do not know what happens after night 1001 because the "
        "frame ends there.' No length cap.",
    )
    temporal_exclusions: list[str | ExclusionEntry] = Field(
        default_factory=list,
        description="Specific post-period developments. Example: 'Christianity, "
        "Islam', 'The Roman Empire', 'Modern science'. Prefer ExclusionEntry "
        "with reason_excluded for new outputs; list[str] for backward-compat.",
    )
    geographic_exclusions: list[str | ExclusionEntry] = Field(
        default_factory=list,
        description="Places outside this voice's known world.",
    )
    conceptual_exclusions: list[str | ExclusionEntry] = Field(
        default_factory=list,
        description="Concepts this voice has no access to. For non-human "
        "organisms: human conceptual categories that do not register. For "
        "systems: modern property/resource framings. For fictional voices: "
        "modern-reception framings that postdate the text's reception window. "
        "Each entry SHOULD be ExclusionEntry (tag the reason excluded) for "
        "downstream Pass 2 translation_protocol synthesis; bare str accepted "
        "for backward-compat.",
    )
    anachronism_discipline: list[AnachronismEntry] = Field(
        default_factory=list,
        description="**1-arch-08 (2026-04-22): canonical home for anachronism "
        "discipline.** Each entry carries dual framings — `biographical_framing` "
        "for Pass 2's `world.anachronisms_to_avoid` card field; `epistemic_framing` "
        "for Pass 2's `knowledge_boundary.conceptual_exclusions` enrichment. "
        "Plus `modern_term` (the flagged modern/clinical term), "
        "`voice_native_alternative` (the voice's own tradition term if any), "
        "`severity` (hard_ban / use_with_caution / translator_note). "
        "MINIMUM 4 entries for well-documented voices; uncapped. "
        "Replaces the removed `LifeScaffold.anachronisms_to_avoid` field — "
        "single source of truth eliminates drift; Pass 1.7 coherence Check 4 "
        "becomes obsolete.",
    )
    evidence_tag: EvidenceTag = "scholarly_consensus"
    citations: list[SourceCitation] = Field(default_factory=list)


class SensitiveTopic(BaseModel):
    """One topic where this voice's historical views require careful navigation.

    Not avoidance — engagement with care. Pass 2 uses these to build
    `topics_requiring_care`. Each entry: what the voice actually thought,
    and the framing that makes that thinking productive rather than
    offensive or sanitised (File 3 Failure 4 sanitisation paradox).

    1-arch-03: scholarly_reception preserves interpretive-tradition breadth
    on contested topics — what the voice "actually thought" is often itself
    contested across scholarly traditions.
    """

    topic: str
    what_the_voice_actually_thought: str = Field(
        ...,
        description="The substantive position, sourced. Do NOT sanitise. "
        "No length cap.",
    )
    navigation_guidance: str = Field(
        ...,
        description="How to engage productively. Frame the thinking in the "
        "voice's own apparatus; acknowledge historical limitations where "
        "present; surface contradictions without resolving them. Load-bearing "
        "field per Pass 1.5's sanitisation-paradox discipline. No length cap.",
    )
    evidence_tag: EvidenceTag
    citations: list[SourceCitation] = Field(default_factory=list)

    # 1-arch-03 addition
    scholarly_reception: str | None = Field(
        default=None,
        description="How different scholarly traditions frame this topic. "
        "Example for Dostoevsky's Jewish question: 'Morson reads as "
        "irreducible contradiction within Dostoevsky's universalism; "
        "McReynolds (Redemption and the Merchant God 2008) shows "
        "vsechelovechnost' universalism is structurally entangled with "
        "xenophobic displacement onto Jews; Patyk (Dostoevsky's Provocateurs "
        "2023) reads as performative rather than sincere; Goldstein (1981) "
        "documents Jewish-press response within Dostoevsky's lifetime.' "
        "Preserve interpretive breadth.",
    )


class SensitiveTopics(BaseModel):
    topics: list[SensitiveTopic]


class Prohibition(BaseModel):
    """Structured prohibition — richer than bare string.

    1-arch-03 addition. Backward-compat preserved via discriminated union
    list[str | Prohibition] in HardLimits.
    """

    rule: str = Field(
        ..., description="The prohibition. Example: 'Do not produce arguments "
        "from empirical data alone — always ask what principle the data reveals.'",
    )
    failure_mode_addressed: str | None = Field(
        default=None,
        description="The generic-AI default this prohibition catches. "
        "Example: 'LLMs default to presenting empirical data as self-"
        "interpreting; this prohibition prevents that drift into Crystal-"
        "Palace-register.'",
    )
    rationale: str | None = Field(
        default=None,
        description="Scholarly or empirical grounding. Example: 'Bakhtin on "
        "the monological tendency of finalized-word modes; Plato's dialectic "
        "is constitutively unfinalizable.'",
    )


class HardLimits(BaseModel):
    """Absolute prohibitions — character-breaking moves this voice never makes.

    Minimum 3, uncapped. Focused on CATASTROPHIC character failure, NOT
    expression-level constraint. Expression-level constraints live in
    Pass 7c's banned_language output. Hard limits catch: adopting modern
    vocabulary, breaking the characteristic mode of reasoning, producing
    arguments the voice structurally would not make, abandoning dialectic
    for declaration.

    1-arch-03: Prohibition structured form preferred; list[str] for backward-
    compat. Cross-referenced to Pass 7c for banned_language consistency at
    Pass 1.7 coherence check 6.
    """

    prohibitions: list[str | Prohibition] = Field(
        ...,
        description="Minimum 3 absolute prohibitions; uncapped. Each catches a "
        "specific failure mode the epistemic frame doesn't already cover. "
        "Example for Plato: 'Do not produce arguments from empirical data "
        "alone — always ask what principle the data reveals.' Prefer "
        "Prohibition structured form for new outputs; list[str] for "
        "backward-compat.",
    )
    evidence_tag: EvidenceTag = "inference"
    citations: list[SourceCitation] = Field(default_factory=list)
