"""Pass 1.3 REASONING schema.

Fills the persona card's `reasoning_method` (Step 1 load-bearing), plus
`finds_compelling` + `resists` (the textures of argument the voice leans
into vs. pushes back against).
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from ._conventions import EvidenceTag, SourceCitation


class ReasoningStep(BaseModel):
    """One step in the voice's characteristic reasoning method.

    5-8 steps per voice. For human voices: cognitive moves (dialectic,
    elenchus, etc.). For non-human organisms: perceptual-response cycle.
    For non-human systems: assessment cycle through the relational framework.
    For fictional/narratival: story-construction process.
    """

    step_number: int
    name: str = Field(..., description="Short cognitive-move name, e.g. 'Test with counterexamples'.")
    description: str = Field(..., description="What the step does; what it moves the voice toward.")
    example: str = Field(
        ..., description="One concrete example applying this step to a representative provocation."
    )


class ReasoningMethod(BaseModel):
    """Per decisions log + REBUILD_PLAN D.1.

    5-8 steps. Includes concluding steps for how the voice evaluates claims
    and how it structures conclusions. Test: if two different provocations
    run through this method, do the results sound like the same voice
    engaging differently — or like a generic responder?
    """

    voice_mode: Literal["philosophical", "observational", "narratival"] | None
    summary: str = Field(..., description="1-3 sentences naming the method's overall shape.")
    steps: list[ReasoningStep]
    evidence_tag: EvidenceTag = "scholarly_consensus"
    citations: list[SourceCitation] = Field(default_factory=list)


class Textures(BaseModel):
    """Textures-of-argument the voice leans into vs. pushes back against.

    Fills persona card's `finds_compelling` + `resists`. These are TEXTURES,
    not topics — the kinds of argument, evidence, or rhetorical moves the
    voice is drawn to / triggered by, regardless of subject.
    """

    finds_compelling: list[str] = Field(
        ...,
        description="4-8 textures of argument this voice leans into. "
        "Not topics — textures. Example: 'definitional questions', 'craft "
        "analogies', 'etymological excavation'.",
    )
    resists: list[str] = Field(
        ...,
        description="4-8 textures of argument that trigger this voice's "
        "sharpest pushback. Not positions — modes. Example: 'arguments from "
        "popular opinion', 'empirical data presented as self-interpreting'.",
    )
    evidence_tag: EvidenceTag = "scholarly_consensus"
    citations: list[SourceCitation] = Field(default_factory=list)
