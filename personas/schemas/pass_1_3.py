"""Pass 1.3 REASONING schema.

Fills the persona card's `reasoning_method` (Step 1 load-bearing), plus
`finds_compelling` + `resists` (the textures of argument the voice leans
into vs. pushes back against).

1-arch-03 additive-merge additions:
- `ReasoningStep.scholarly_context`: per-step interpretive framing.
- `Textures.scholarly_context`: scholarly framing of voice's argument-
  preferences and allergies.
- Top-level `AnalyticalContext` output (separate chunk output key
  `analytical_context_reasoning`): preserves structural_patterns,
  worked_demonstrations, scholarly_debates previously dropped by tight
  schema. See `_analytical.py` for container shape.

Under additive merge, reasoning_method remains the structured "reasoning
recipe" (5-8 steps for Pass 3 to compress to card), while
analytical_context_reasoning preserves the surrounding scholarly-analytical
material (carnivalization analysis, Menippean checklist, named scandal-
scene instances, 3 worked demonstrations, Williams-vs-Frank debate, etc.).
Pass 3 reads both; card reasoning_method synthesizes from the recipe;
downstream Pass 4a may draw from analytical_context for moves extraction.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from ._conventions import EvidenceTag, SourceCitation


class ReasoningStep(BaseModel):
    """One step in the voice's characteristic reasoning method.

    Minimum 5, uncapped maximum (pre-1-arch-03 cap was 5-8; now lower-bound
    only). For human voices: cognitive moves (dialectic, elenchus, etc.).
    For non-human organisms: perceptual-response cycle. For non-human
    systems: assessment cycle through the relational framework. For
    fictional/narratival: story-construction process.

    `step_number` optional — for voices whose reasoning isn't sequential
    (perceptual-response cycles with parallel activation, narratival
    reasoning where steps are simultaneous).
    """

    step_number: int | None = Field(
        default=None,
        description="Sequential ordering if method is ordered. Omit for "
        "non-sequential methods (parallel perceptual-response, scenic-collision "
        "where multiple moves fire simultaneously).",
    )
    name: str = Field(..., description="Short cognitive-move name, e.g. 'Test with counterexamples'.")
    description: str = Field(..., description="What the step does; what it moves the voice toward. No length cap.")
    example: str = Field(
        ..., description="One concrete example applying this step to a representative provocation. "
        "Prefer lift-from-primary-text where possible. No length cap."
    )

    # 1-arch-03 addition
    scholarly_context: str | None = Field(
        default=None,
        description="Named scholarly framing of this step. Example for "
        "Dostoevsky's 'Incarnate idea in person' step: 'Bakhtin names this "
        "the idea-hero (PDP ch. 5, image of the idea).' For Plato's 'Test "
        "with counterexamples' step: 'Vlastos on Socratic elenchus as the "
        "structural move of early dialogues; refined by Griswold on mature "
        "hypothetical method.' Preserve for Pass 3 synthesis context.",
    )


class ReasoningMethod(BaseModel):
    """Per decisions log + REBUILD_PLAN D.1.

    Minimum 5 steps, uncapped. Pre-1-arch-03 targeted 5-8; additive merge
    accepts more where sources warrant. Test: if two different provocations
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

    Minimum 4 each, uncapped.
    """

    finds_compelling: list[str] = Field(
        ...,
        description="Textures of argument this voice leans into. "
        "Not topics — textures. Example: 'definitional questions', 'craft "
        "analogies', 'etymological excavation', 'confessional utterance "
        "under pressure'. Minimum 4, uncapped.",
    )
    resists: list[str] = Field(
        ...,
        description="Textures of argument that trigger this voice's "
        "sharpest pushback. Not positions — modes. Example: 'arguments from "
        "popular opinion', 'empirical data presented as self-interpreting', "
        "'abstract system-building divorced from lived suffering'. "
        "Minimum 4, uncapped.",
    )
    evidence_tag: EvidenceTag = "scholarly_consensus"
    citations: list[SourceCitation] = Field(default_factory=list)

    # 1-arch-03 addition
    scholarly_context: str | None = Field(
        default=None,
        description="Scholarly framing of the voice's argument-preferences. "
        "Example for Dostoevsky: 'Bakhtin on the inescapably-unfinalizable "
        "word (PDP ch. 5) — Dostoevsky's finds_compelling of confessional-"
        "utterance-under-pressure is the formal correlate of polyphony; the "
        "half-turned-to-internalized-other structure is what distinguishes "
        "Dostoevskian confession from Augustinian/Rousseauian autobiography.'",
    )
