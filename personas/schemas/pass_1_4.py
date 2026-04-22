"""Pass 1.4 VOICE schema.

Fills the persona card's `characteristic_moves`, `register_and_tone`,
`rhetorical_mode`, `preferred_vocabulary`, `metaphorical_repertoire`.

Per Boddice §15 `voice_signature` revision: voice is tradition-channelled
for many panel members (Scheherazade, Marley, Whanganui via Te Pou Tupua),
not individual-authorial. The `Register.tradition_note` field makes that
mediation explicit rather than smuggling it as individual authorship.

1-arch-03 additive-merge additions:
- `Move.scholarly_context` + `structural_pattern_refs` for cross-chunk
  coherence with Pass 1.3 analytical_context_reasoning.
- `Register.genre_specific_register` for voices whose register varies by
  genre (Dostoevsky: fiction vs. journalism vs. letter vs. hagiography).
- `Register.translator_tradition_notes` for translated voices.
- `Vocabulary.preferred_vocabulary: list[str | VocabEntry]` — structured
  entries with loadbearing + translation_notes flags; backward-compat
  preserved via discriminated union.
- `Vocabulary.scholarly_context`: scholarly treatment of voice's lexicon.
- Top-level `analytical_context_voice: AnalyticalContext | None` output
  (optional for voices without substantive voice-signature scholarly
  material; populated for richly-scholarly voices like Dostoevsky).
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from ._conventions import EvidenceTag, SourceCitation


class Move(BaseModel):
    """One named rhetorical / characteristic move.

    Minimum 3, uncapped. These are the fingerprints — things that make a
    reader who knows this voice say "that's unmistakably X."

    1-arch-03: scholarly_context + structural_pattern_refs provide cross-
    chunk coherence with Pass 1.3 analytical_context_reasoning.
    """

    name: str = Field(..., description="Short name, e.g. 'The definitional challenge'.")
    description: str = Field(..., description="What the move does; when the voice deploys it. No length cap.")
    example: str | None = Field(
        default=None,
        description="One concrete example — short phrase or sentence illustrating the move in action.",
    )

    # 1-arch-03 additions
    scholarly_context: str | None = Field(
        default=None,
        description="Scholarly framing of this move. Example for Dostoevsky's "
        "'Scripture read existentially' move: 'Kasatkina (2004) on sacred-in-"
        "the-everyday; Jackson on Scripture-as-recognition-scene; Williams "
        "(2008) on the non-argumentative answer (kiss, Cana dream).'",
    )
    structural_pattern_refs: list[str] = Field(
        default_factory=list,
        description="Cross-ref to StructuralPattern.name values in Pass 1.3 "
        "analytical_context_reasoning. Example: ['scandal-scene', 'threshold-"
        "chronotope', 'sideshadowing-via-vdrug']. Links moves to their "
        "structural-pattern substrate.",
    )


class Moves(BaseModel):
    moves: list[Move]
    evidence_tag: EvidenceTag = "scholarly_consensus"
    citations: list[SourceCitation] = Field(default_factory=list)


class Register(BaseModel):
    """Register + tone + rhetorical mode.

    Per decisions log + §15: `tradition_note` names the tradition that speaks
    through the voice (oral, ritual, performative). For individual-authorial
    voices set it to null.

    1-arch-03: genre_specific_register captures voices whose register varies
    across genres they worked in (novel vs. journalism vs. letter for
    Dostoevsky; sermon vs. song vs. interview for Marley). translator_
    tradition_notes captures how translator choice shapes voice (for
    translated voices).
    """

    rhetorical_mode: str = Field(
        ...,
        description="One or two sentences naming the primary mode of expression. "
        "Example: 'Dialogic and interrogative; primary mode is the guided question.'",
    )
    register_and_tone: str = Field(
        ...,
        description="The overall feel. Include both what the voice IS and what it "
        "is NOT. Example: 'Formally conversational, respectful but direct, playfully "
        "ironic — NOT pompous.' No length cap.",
    )
    tradition_note: str | None = Field(
        default=None,
        description="For oral, ritual, or performative traditions: name the tradition "
        "that speaks through the voice. For non-human voices: describe the mediation "
        "(Te Pou Tupua, scientific reconstruction, narratorial construct). Null for "
        "individual-authorial voices.",
    )
    evidence_tag: EvidenceTag = "scholarly_consensus"
    citations: list[SourceCitation] = Field(default_factory=list)

    # 1-arch-03 additions
    genre_specific_register: dict[str, str] = Field(
        default_factory=dict,
        description="How register varies by genre. Example for Dostoevsky: "
        "{'fiction': 'fevered-confessional, half-turned-to-internalized-other, "
        "scandalously-exposed', 'journalism (Diary of a Writer)': 'polemic-"
        "sharp, directly-addressed, cuttingly-specific on contemporaries', "
        "'letter': 'direct-earnest, debt-apologetic, confiding', 'hagiography "
        "(Zosima sections)': 'paratactic, scripture-cadenced, shorn of "
        "ellipses'}. Preserve genre-register mapping; Pass 4a may select "
        "one primary genre-register for card or may blend.",
    )
    translator_tradition_notes: str | None = Field(
        default=None,
        description="How translator choice shapes voice for translated voices. "
        "Example for Dostoevsky: 'Garnett (1912-20) Victorian-English "
        "register; Pevear-Volokhonsky (1990-2002) preserves Russian "
        "syntactical friction + Cyrillic terms; Ready (2014-18) contemporary "
        "British; Katz modernist-austere. For primary-text corpus and voice-"
        "exemplar anchor, P-V recommended; for reader-accessibility, Garnett.'",
    )


class VocabEntry(BaseModel):
    """Structured vocabulary entry — richer than bare string.

    1-arch-03 addition. Backward-compat preserved via
    `Vocabulary.preferred_vocabulary: list[str | VocabEntry]` discriminated
    union — existing Dostoevsky card's list[str] still validates.

    loadbearing=True marks philosophically/theologically central terms
    (Dostoevsky's `podpol'e`, `nadryv`, `obraz`; Plato's `to agathon`,
    `eidē`, `episteme`). These terms survive downstream card compression
    with higher priority.
    """

    term: str = Field(..., description="The term as voice uses it.")
    term_in_original_language: str | None = Field(
        default=None,
        description="Period-language / native-tradition form. Examples: "
        "'подпольe' (Russian), 'ibtilā'' (Arabic), 'mauri' (Maori).",
    )
    gloss: str | None = Field(
        default=None,
        description="Brief English approximation. Null if term is universally "
        "recognizable (Crystal Palace, obraz).",
    )
    loadbearing: bool = Field(
        default=False,
        description="True for philosophically/theologically central terms "
        "that must survive downstream card compression.",
    )
    translation_notes: str | None = Field(
        default=None,
        description="Translator-tradition variation notes. Example for "
        "'nadryv': 'Garnett laceration; P-V preserves untranslated; Ready "
        "rupture. Russian carries physical-wound + moral-self-torture "
        "senses; no single English term preserves both.'",
    )


class Vocabulary(BaseModel):
    """The voice's characteristic lexicon + imagery.

    `preferred_vocabulary` — words the voice reaches for. For pre-1820 voices,
    keep the primary terms in the voice's own language (transliterated where
    necessary). For post-1820 voices with tradition-specific lexicons
    (Russian Orthodox, Rastafari, Arendtian German-Jewish), preserve native
    terms regardless of period.

    Minimum 15 entries, uncapped maximum. 1-arch-03: list accepts both
    bare str (backward-compat) and VocabEntry structured form (preferred
    for new outputs).
    """

    preferred_vocabulary: list[str | VocabEntry] = Field(
        ...,
        description="Words/terms the voice reaches for. Minimum 15, uncapped. "
        "Tradition-specific lexicon preserved regardless of period. No "
        "generic management terms. Prefer VocabEntry structured form for "
        "new outputs; list[str] accepted for backward-compat.",
    )
    metaphorical_repertoire: dict[str, str] = Field(
        ...,
        description="Named metaphor families → description. Example: "
        "{'craft and labour': 'medicine, navigation, weaving', 'light and "
        "darkness': 'sun, cave, illumination', 'yellow Petersburg': 'yellow "
        "wallpaper, yellow ticket, yellow face — chromatic signature of "
        "jaundice, bureaucratic shame, civic decay'}. Minimum 3, uncapped.",
    )
    evidence_tag: EvidenceTag = "scholarly_consensus"
    citations: list[SourceCitation] = Field(default_factory=list)

    # 1-arch-03 addition
    scholarly_context: str | None = Field(
        default=None,
        description="Scholarly treatment of voice's lexicon. Example for "
        "Dostoevsky: 'Kasatkina on the lik/litso distinction — lik is the "
        "iconic-ideal face, litso the ordinary phenomenal face; lichina "
        "the mask. The triadic structure is theologically loaded per Florovsky. "
        "Williams (2008) on Dostoevsky's vocabulary as sacramental.'",
    )
