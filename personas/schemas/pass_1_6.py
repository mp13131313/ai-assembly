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


class Passage(BaseModel):
    """A characteristic passage — 8-15 per voice.

    Each passage tagged with `purpose` (intellectual substance / voice
    exemplar / translation anchor). Pass 4a uses voice exemplars as
    stylistic models. For musical voices: DESCRIPTION ONLY (no direct lyric
    quotation).
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


class URLEntry(BaseModel):
    url: str
    work_title: str
    source: str = Field(
        ..., description="Perseus, Project Gutenberg, Google Books, BAWS-online, etc."
    )
    license_or_access_note: str | None = None


class URLs(BaseModel):
    urls: list[URLEntry]
