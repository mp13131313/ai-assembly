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

1-arch-03 additive-merge updates:
- Counts become minimums not maximums (uncapped); prompt-guidance enforces
  preservation of all unique content from sources.
- `LifeScaffold.scholarly_context` preserves scholarly-interpretive debates
  on this voice's biographical reception (Frank vs. Mochulsky on Dostoevsky's
  father's death, Williams vs. Frank on Myshkin failure, etc.).
- `LifeScaffold.contested_readings` preserves biographical disagreements
  where scholarly traditions divide.
- `FormativeCandidate.scholarly_context` + `resonates_with_commitments` add
  cross-chunk coherence aids for Pass 2's primary-formative choice.
- `AnachronismEntry` replaces bare list[str] for anachronisms (backward-compat
  via discriminated union).
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from ._conventions import ContestedReading, EvidenceTag, SourceCitation


class KeyRelationship(BaseModel):
    """One formative relationship (teacher, student, rival, consort, enemy, etc.)."""

    person: str
    relation_type: str  # e.g. "teacher", "student", "rival", "patron", "enemy"
    evidence_tag: EvidenceTag
    citations: list[SourceCitation] = Field(default_factory=list)


class PeriodPathos(BaseModel):
    """One period-specific affect/passion in the voice's own language.

    Per Boddice §13 sub-field 2: period-specific terms in original language
    with short glosses. For pre-1820 voices: no modern English emotion-words
    as primary vocabulary. For post-1820 voices with tradition-specific
    lexicons (Russian Orthodox, Rastafari, Arendtian German-Jewish,
    Confucian civic-tech): preserve the voice's own terms regardless of
    period. Do NOT use 'emotion' as organizing category for pre-1820 voices
    specifically (Dixon's post-1820 invention).
    """

    term_in_original_language: str
    gloss: str
    evidence_tag: EvidenceTag
    citations: list[SourceCitation] = Field(default_factory=list)


class AnachronismEntry(BaseModel):
    """Structured anachronism: modern term + dual framings (biographical +
    epistemic) + voice-native alternative + severity.

    Under 1-arch-08 (2026-04-22), anachronism discipline consolidates into
    `KnowledgeBoundary.anachronism_discipline[]` (Pass 1.5). Each entry
    carries BOTH framings so Pass 2 can pluck the right one for each card
    field it populates:

    - `biographical_framing` → rendered in Pass 2's `world.anachronisms_to_avoid`
      card field ("this would flatten the katorga + mock-execution
      threshold experiences")
    - `epistemic_framing` → rendered in Pass 2's `knowledge_boundary.conceptual_exclusions`
      card field ("post-1980 clinical-psychological category; didn't exist in
      voice's lifetime")

    The pre-1-arch-08 location `LifeScaffold.anachronisms_to_avoid` is
    REMOVED. `reason_excluded` is deprecated in favor of the two framings
    but kept optional for backward compat during migration.
    """

    modern_term: str = Field(
        ...,
        description="The modern-English or modern-clinical term that would "
        "mis-render the voice. Examples: 'trauma', 'depression', 'identity', "
        "'existentialist', 'gender', 'nationalism' (ethno-biological).",
    )
    biographical_framing: str = Field(
        ...,
        description="1-2 sentence reason from the voice's own biographical "
        "experience for why this term flattens or distorts. Pass 2 uses for "
        "`world.anachronisms_to_avoid` card-field narrative.",
    )
    epistemic_framing: str = Field(
        ...,
        description="1-2 sentence reason from the voice's knowledge horizon "
        "(when the term was invented, what it replaced, why it's outside the "
        "voice's conceptual apparatus). Pass 2 uses for `knowledge_boundary."
        "conceptual_exclusions` card-field narrative.",
    )
    voice_native_alternative: str | None = Field(
        default=None,
        description="The voice's own tradition-specific term if one exists. "
        "Example: for 'trauma', voice_native_alternative = 'nadryv' (Dostoevsky) "
        "or 'ibtilā'' (Ibn Battuta). None for fictional / thinly-documented voices.",
    )
    severity: Literal["hard_ban", "use_with_caution", "translator_note"] = Field(
        default="hard_ban",
        description="`hard_ban`: never use, even in scholarly exposition (trauma, "
        "PTSD, existentialist). `use_with_caution`: flaggable with explicit scare-"
        "quoting or scholarly framing (psychology, career). `translator_note`: "
        "translator-tradition artifact that differs in meaning (Garnett's "
        "'conscience' for 'sovest'' — not strictly anachronistic but flattens).",
    )
    reason_excluded: str | None = Field(
        default=None,
        description="DEPRECATED under 1-arch-08. Use biographical_framing + "
        "epistemic_framing instead. Kept optional for backward compat.",
    )
    evidence_tag: EvidenceTag = Field(default="scholarly_consensus")
    citations: list[SourceCitation] = Field(default_factory=list)


class LifeScaffold(BaseModel):
    """Pass 1.1 biographical foundation per Boddice §13.

    This is NOT period-setting. It is the voice's emotional-experiential
    ontology: what was real, what could be felt, what gave suffering meaning,
    what counted as a self.

    Under 1-arch-03 additive merge: permissive container. Counts are
    minimums (preserve all unique content from sources); schema accepts
    scholarly_context + contested_readings to preserve analytical-interpretive
    material that pre-1-arch-03 would have dropped.
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
        ..., description="Period intellectual currents in the voice's own framing. "
        "Preserve full scholarly detail from sources; no length cap."
    )
    ontological_furniture: str = Field(
        ...,
        description="What was *real* for this voice — not beliefs, but the "
        "structure of reality. Gods, Forms, jinn, Jah, whakapapa, distributed "
        "embodiment. Do not write 'they believed X' when X was the furniture. "
        "No length cap; preserve source detail.",
    )
    available_pathe: list[PeriodPathos] = Field(
        default_factory=list,
        description="Period-specific affects in original language with glosses. "
        "MINIMUM 5; uncapped maximum — preserve all non-redundant terms "
        "from sources. Flag terms with no modern equivalent. Tradition-"
        "specific lexicons preserved regardless of period (Russian Orthodox, "
        "Rastafari, etc.). Pre-1820 voices: do NOT use 'emotions' as "
        "organizing category.",
    )
    framework_for_difficulty: str = Field(
        ...,
        description="What gave pain, loss, setback meaning? Afterlife, Forms, "
        "divine testing, karma, theosis, kenosis, Babylonian exile, whakapapa "
        "rupture, endocrine semelparity. Not 'coping mechanism' — experiential "
        "framework. MUST carry [experiential_reconstruction] tag inline (any "
        "claim about what the voice felt suffering to mean is biocultural "
        "reconstruction). No length cap.",
    )
    model_of_selfhood: str = Field(
        ...,
        description="What counted as an 'I'? Modern introspective interior, "
        "tripartite soul, divine-royal corporate body, I-and-I collective-divine "
        "indwelling, mountains-to-sea indivisible whole, fluctuating assemblage "
        "of semi-autonomous arms. State explicitly. MUST carry "
        "[experiential_reconstruction] tag inline. [projection_warning] on "
        "any modern English term used faute de mieux (e.g., 'disease' for "
        "pre-clinical moral-theological bolezn'). No length cap.",
    )
    # 1-arch-08 (2026-04-22): `anachronisms_to_avoid` REMOVED from LifeScaffold.
    # Anachronism discipline consolidates at KnowledgeBoundary.anachronism_discipline[]
    # (Pass 1.5) with dual framings (biographical + epistemic) per entry. Pass 2
    # plucks biographical_framing for world.anachronisms_to_avoid card field and
    # epistemic_framing for knowledge_boundary.conceptual_exclusions card field.
    # Single canonical source eliminates drift; Pass 1.7 Check 4 (anachronism/
    # boundary cross-check) becomes obsolete.

    # 1-arch-03 additions: preserve analytical-interpretive material.
    scholarly_context: str | None = Field(
        default=None,
        description="Scholarly-interpretive context on this voice's biographical "
        "reception. Debates about formative-event interpretation, contested "
        "biographical readings, interpretive traditions. Example for Dostoevsky: "
        "'Frank (5-vol. biography 1976-2002) treats Dostoevsky's father's death "
        "as contested, skeptical of serf-murder; Mochulsky (1967) treats it as "
        "historical fact; Freud (1928 'Dostoevsky and Parricide') reads the "
        "Oedipal frame onto the uncertainty. Williams (2008) reads Myshkin's "
        "failure as intrinsic to the experiment; Frank reads it as limitation "
        "of Myshkin's consciousness within the fallen world.' Preserve; do not "
        "synthesize to one interpretation.",
    )
    contested_readings: list[ContestedReading] = Field(
        default_factory=list,
        description="Biographical facts or interpretive framings where sources "
        "disagree and disagreement is scholarly-real. Each entry: consensus_view "
        "+ minority_view + scholars_per_view.",
    )


class FormativeCandidate(BaseModel):
    """Per Boddice §14 4-part rubric. Multiple candidates preserved (minimum 2,
    uncapped); Pass 2 commits to ONE PRIMARY per fix 2-03, referencing
    1-2 supporting candidates inline for narrative-context.

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

    Under 1-arch-03: `scholarly_context` preserves interpretive-tradition
    breadth per formative candidate; `resonates_with_commitments` provides
    cross-chunk coherence aid for Pass 2's primary-choice reasoning.
    """

    candidate_label: str = Field(
        ..., description="Short name for Pass 2 to reference. "
        "Examples: 'Trial of Socrates 399 BCE', 'Semenovsky mock execution 1849', "
        "'Semelparous lifespan without parenting', "
        "'1977 melanoma diagnosis refused as toe-amputation'."
    )
    formative_emotional_community: str = Field(
        ...,
        description="Per §14 sub-field 1. Overlapping Rosenwein-style "
        "communities that shaped this voice's lexicon of feeling, norms of "
        "expression, and what-could-be-felt. For non-human voices: the "
        "analogous ontogenetic/ecological field (taxon, habitat, lineage). "
        "MUST carry [experiential_reconstruction] tag. No length cap.",
    )
    lived_through_own_apparatus: str | None = Field(
        default=None,
        description="Per §14 sub-field 2 (HUMAN voices). Describe the "
        "formative event AND the framework in which it was meaningful in a "
        "single movement, using period-specific vocabulary from the world field. "
        "NOT event without framework (modern projection) or framework without "
        "event (abstraction). MUST carry [experiential_reconstruction] tag. "
        "If using modern clinical term (e.g., 'trauma') even to flag as "
        "anachronistic, carry [projection_warning: <term> <distortion>] tag.",
    )
    condition_of_being: str | None = Field(
        default=None,
        description="Per §14 sub-field 4 (NON-HUMAN / FICTIONAL / non-event-"
        "driven / cosmic voices). Describe the ongoing state of being that "
        "structures the voice's standing and stake. Replaces "
        "lived_through_own_apparatus. For fictional voices (Scheherazade): the "
        "narratorial/frame-tale condition (speaking under threat of execution "
        "within 1001 Nights). MUST carry [experiential_reconstruction] tag "
        "per §14 attributed-by-narrative-function discipline.",
    )
    engagement_it_drives: str = Field(
        ...,
        description="Per §14 sub-field 3. What does this voice enter the "
        "panel to *do*? What is it motivated to say, notice, refuse, defend? "
        "Functional, not psychological. MUST carry [experiential_reconstruction] "
        "tag — claims about what the formative context drives are biocultural "
        "reconstruction. No length cap.",
    )
    evidence_tag: EvidenceTag = Field(
        default="experiential_reconstruction",
        description="Usually 'experiential_reconstruction' for §14 content.",
    )
    citations: list[SourceCitation] = Field(default_factory=list)
    scholarly_support_score: Literal["strong", "moderate", "contested"] = Field(
        ..., description="Pass 2 uses this when committing to a PRIMARY candidate "
        "per fix 2-03. Strong: documented across multiple tier_1_primary + "
        "scholarly consensus. Moderate: documented but scholarly reception "
        "varies. Contested: sources disagree on interpretation."
    )

    # 1-arch-03 additions: cross-chunk coherence + interpretive preservation.
    scholarly_context: str | None = Field(
        default=None,
        description="How different scholarly traditions frame this candidate. "
        "Example for Dostoevsky's mock execution: 'Frank (Seeds of Revolt, "
        "1976 pp. 245-252) treats as decisive threshold-experience marking "
        "Dostoevsky's pre-Siberia / post-Siberia break; Jackson (1981) reads "
        "as origin of the threshold-chronotope in the fiction; Kasatkina "
        "(2004) reads the same-evening letter to Mikhail as the birth of "
        "the Christ-over-truth formula.' Preserve interpretive breadth; "
        "do not synthesize to one reading.",
    )
    resonates_with_commitments: list[str] = Field(
        default_factory=list,
        description="Labels of commitments (Pass 1.2 output) this formative "
        "context shapes. Cross-chunk coherence aid — Pass 2 uses when "
        "choosing primary formative. Example for Semenovsky mock execution: "
        "['Human freedom is metaphysically radical', 'Suffering accepted in "
        "faith is redemptive', 'Every person responsible for all'].",
    )
