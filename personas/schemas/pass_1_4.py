"""Pass 1.4 VOICE schema.

Fills the persona card's `characteristic_moves`, `register_and_tone`,
`rhetorical_mode`, `preferred_vocabulary`, `metaphorical_repertoire`.

Per Boddice §15 `voice_signature` revision: voice is tradition-channelled
for many panel members (Scheherazade, Marley, Whanganui via Te Pou Tupua),
not individual-authorial. The `Register.tradition_note` field makes that
mediation explicit rather than smuggling it as individual authorship.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from ._conventions import EvidenceTag, SourceCitation


class Move(BaseModel):
    """One named rhetorical / characteristic move.

    3-6 per voice. These are the fingerprints — things that make a reader
    who knows this voice say "that's unmistakably X."
    """

    name: str = Field(..., description="Short name, e.g. 'The definitional challenge'.")
    description: str = Field(..., description="What the move does; when the voice deploys it.")
    example: str | None = Field(
        default=None,
        description="One concrete example — short phrase or sentence illustrating the move in action.",
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
        "ironic — NOT pompous.'",
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


class Vocabulary(BaseModel):
    """The voice's characteristic lexicon + imagery.

    `preferred_vocabulary` — words the voice reaches for. For pre-1820 voices,
    keep the primary terms in the voice's own language (transliterated where
    necessary).
    """

    preferred_vocabulary: list[str] = Field(
        ...,
        description="15-30 words/terms the voice reaches for. Period vocabulary "
        "primary for pre-1820 voices. No generic management terms.",
    )
    metaphorical_repertoire: dict[str, str] = Field(
        ...,
        description="Named metaphor families → short description. Example: "
        "{'craft and labour': 'medicine, navigation, weaving', 'light and "
        "darkness': 'sun, cave, illumination'}.",
    )
    evidence_tag: EvidenceTag = "scholarly_consensus"
    citations: list[SourceCitation] = Field(default_factory=list)
