"""Pass 1.6 CORPUS schema.

Fills the persona card's `curated_corpus_passages` + primary-text URL
provisioning for Pass 4a. Three sub-outputs: Works (complete catalogue),
Passages (8-15 characteristic passages with tier + purpose), URLs
(digitised full-text sources).

Variants per voice type:
- Musical voices (`corpus_constraint: lyrics_patterns_only`): Works + URLs
  collect the catalogue and interview/speech sources, but Passages become
  structural-thematic descriptions only — NEVER direct lyric quotation.
- Hostile-source voices: Works distinguish primary-in-voice (Tier 1) from
  hostile-source (Tier 2, tagged for against-the-grain reading).
- Non-human systems: the corpus is law + ecological assessment + indigenous
  scholarship, not literature.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from ._conventions import EvidenceTag, SourceCitation, Tier


class WorkEntry(BaseModel):
    """One work in the voice's corpus."""

    title: str
    canonical_reference: str | None = Field(
        default=None,
        description="Stephanus pagination for Plato, BAWS volume for Ambedkar, "
        "stemma reference for Scheherazade, catalogue number for songs, etc. "
        "Null where no canonical scheme exists.",
    )
    translator: str | None = None
    tier: Tier
    source_type: Literal[
        "primary_in_voice",
        "hostile_source",
        "scholarly_commentary",
        "legal_instrument",
        "scientific_literature",
        "musical_catalogue",
        "interview_or_speech",
    ]
    note: str | None = None


class Works(BaseModel):
    works: list[WorkEntry]

    # 1-arch-03 addition
    bibliographic_scholarly_context: str | None = Field(
        default=None,
        description="Scholarly framing of the voice's canonical corpus. "
        "Example for Dostoevsky: 'PSS (Polnoe sobranie sochinenii, Nauka "
        "1972-90, 30 vols) is scholarly-authoritative for Russian-language "
        "primary; Frank's 5-volume biography (Princeton UP 1976-2002) "
        "dominant in Anglophone reception; Wasiolek-edited notebooks "
        "(Chicago UP 1967-71) preserve compositional-process documents. For "
        "Scheherazade: the canonical corpus is multi-translator (Galland "
        "1704 shaped European reception; Burton 1885 orientalized; Haddawy "
        "1990 restored Muhsin Mahdi's critical edition; Lyons 2008 contemporary "
        "scholarly). No single canonical source-text.' Preserve for Pass 6 "
        "corpus curation decisions.",
    )


class Passage(BaseModel):
    """A characteristic passage — 8-15 per voice.

    Each passage tagged with `purpose` (intellectual substance / voice
    exemplar / translation anchor). Pass 4a uses voice exemplars as
    stylistic models. For musical voices: DESCRIPTION ONLY (no direct lyric
    quotation).

    Two-tier corpus note (Phase B): this is the PUBLIC-SAFE tier. Voices
    with `corpus_constraint: lyrics_patterns_only` emit pattern descriptions
    here (`is_direct_quotation=false`). The private-reasoning tier lives in
    the sibling `ReferenceOnlyPassage` — loaded into Voice Pipeline Step 1
    only, never Step 2. See the `ReferenceOnlyPassages` model.
    """

    passage_id: str = Field(..., description="Short reference label, e.g. 'Republic-488a' or 'Rihla-Delhi-imprisonment'.")
    work_title: str
    canonical_reference: str | None
    contextual_header: str = Field(
        ..., description="What the passage is and why it matters. 1-3 sentences."
    )
    content_or_description: str = Field(
        ...,
        description="For corpus-based voices: the passage text from scholarly translation. "
        "For musical voices: STRUCTURAL-THEMATIC DESCRIPTION only — no direct lyric. "
        "For hostile-source passages: the text with bias flag in contextual_header.",
    )
    is_direct_quotation: bool = Field(
        default=True,
        description="True for corpus passages; False for musical-voice descriptions or "
        "paraphrases.",
    )
    purpose: Literal[
        "intellectual_substance",
        "voice_exemplar",
        "translation_anchor",
    ]
    tier: Tier
    evidence_tag: EvidenceTag = "stated"
    citations: list[SourceCitation] = Field(default_factory=list)


class Passages(BaseModel):
    passages: list[Passage]

    # 1-arch-03 addition
    translator_tradition_coverage: list[str] = Field(
        default_factory=list,
        description="For voices whose corpus spans multiple translation "
        "traditions: which translations are represented in passages[] and "
        "why. Example for Dostoevsky: ['Garnett (Victorian register, "
        "public-domain, audience-accessible)', 'Pevear-Volokhonsky "
        "(preserves Russian syntactical friction + Cyrillic terms)', "
        "'Ready (contemporary British, tighter prose)']. For Scheherazade: "
        "['Burton 1885 (orientalized, public-domain)', 'Haddawy 1990 "
        "(Muhsin Mahdi critical-edition base)', 'Lyons 2008 (contemporary "
        "scholarly)']. Pass 4a uses this to select primary translation for "
        "voice-exemplar anchoring. Pass 6 uses for curated-passage selection.",
    )


class ReferenceOnlyPassage(BaseModel):
    """Private-reasoning corpus — injected into Voice Pipeline Step 1 ONLY.

    Two-tier corpus design (Phase B, cleanup deferrals): for voices whose
    primary corpus is copyright-sensitive (musical voices: Marley; possibly
    Dostoevsky if we pin specific modern-critical-edition translations),
    pattern descriptions alone in `Passages` underfit the voice. The voice
    can reason much more fluently if it has direct access to its own words
    as REFERENCE MATERIAL inside private reasoning.

    Critical runtime contract:
      - Voice Pipeline Step 1 (Private Reasoning) loads these passages into
        its system prompt alongside the public `curated_corpus_passages`.
      - Voice Pipeline Step 2 (Public Expression) does NOT load these. The
        artifact the audience reads must not contain direct lyric quotation
        (copyright) or any material flagged here as reasoning-only.
      - The PROHIBITION against quoting these is stronger than banned_language:
        it applies to ANY output the audience sees, including paraphrase
        that's identifiably sourced.

    Leakage risk: the model could still lift phrases inadvertently in Step 2
    even though the passages aren't loaded there. Pass 7c scans for this
    and should add such lift-phrases to `banned_language` if observed.

    Voices for which this field is populated:
      - `corpus_constraint: lyrics_patterns_only` voices (Marley): YES
      - Translation-sensitive corpora (Dostoevsky translations under
        copyright, perhaps): optionally YES with scholarly-edition attribution
      - Voices with fully public-domain corpora (Plato, Ibn Battuta):
        usually empty — the regular `Passages` already carries the material
    """

    passage_id: str
    work_title: str
    canonical_reference: str | None = None
    contextual_header: str = Field(
        ..., description="What the passage is. Same shape as public Passage."
    )
    content: str = Field(
        ..., description="The actual text — lyrics, copyrighted translation, "
        "etc. Injected into Step 1 ONLY. Never reaches the audience-facing "
        "artifact.",
    )
    source_attribution: str = Field(
        ..., description="Full copyright attribution: 'Marley, Bob. \"Redemption Song.\" "
        "Uprising (Island Records, 1980). Used as reference-only material under "
        "private-use / fair-use reasoning; not redistributed.'",
    )
    purpose: Literal["voice_exemplar", "intellectual_substance"]
    # No tier / no citations Pydantic model — this is internal reference,
    # not scholarly corpus. Structure is deliberately thinner to discourage
    # treating these as public primary sources.


class ReferenceOnlyPassages(BaseModel):
    """Container for the private-reasoning tier. Step 1 reads; Step 2 does not."""

    passages: list[ReferenceOnlyPassage] = Field(
        default_factory=list,
        description="Usually empty; populated for musical + translation-"
        "sensitive voices.",
    )
    runtime_contract_note: str = Field(
        default=(
            "RUNTIME CONTRACT: These passages are loaded into Voice Pipeline "
            "Step 1 (Private Reasoning) ONLY. They are NEVER loaded into "
            "Step 2 (Public Expression), and no direct quotation of them is "
            "permitted in the artifact the audience reads. Enforcement: the "
            "runtime's Voice Pipeline Step 2 system-prompt assembly code "
            "MUST drop this field before rendering. See personas/CROSS_REPO_CONTRACT.md "
            "for the runtime contract."
        ),
        description="Inline reminder the runtime reads.",
    )


# NOTE (1-arch-07, 2026-04-22): URLEntry + URLs removed as chunk-output
# schema. URL inventory is now derived at render-time by Python from
# `passages[].citation` and `works[]` entries — see
# `flows/shared/url_extract.py`. Deterministic extraction beats LLM-emitted
# list, which invited drift between urls.json and the URLs embedded in
# sibling chunk files. Historical schema preserved here as comment for
# migration audit reference:
#
#   class URLEntry(BaseModel):
#       url: str
#       work_title: str
#       source: str  # Perseus, Gutenberg, etc.
#       license_or_access_note: str | None = None
#   class URLs(BaseModel):
#       urls: list[URLEntry]
