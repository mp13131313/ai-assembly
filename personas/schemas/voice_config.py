"""Pass 0a Voice Config schema — Phase B redesign.

Per REBUILD_PLAN §"Phase 0 — Intake · Pass 0a" + decisions log:
- `conference_context` field DROPPED — Pass 7b loads audience/facts directly
  from the split inputs/ files instead of re-reading from voice_config.
- `editorial_rationale` ADDED — curator writes directly (not model-proposed).
- `manual_grounding` ADDED — unifies `wikipedia_extract` + `disambiguation_hint`;
  for non-human voices, can hold the Godfrey-Smith / Te Awa Tupua excerpt
  instead of a Wikipedia lead paragraph.

Back-compat: legacy v3.10 voice configs with `conference_context` still load
(the field is silently ignored); new configs produced by Phase B Pass 0a do
not emit it.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


VoiceType = Literal["human", "non_human", "fictional"]
VoiceSubtype = Literal["organism", "system"] | None
VoiceMode = Literal["philosophical", "observational", "narratival"] | None
CorpusConstraint = Literal["full", "lyrics_patterns_only", "hostile_read_against_grain"]
MediationStance = Literal["none", "transmission_witness"] | None


class VoiceConfig(BaseModel):
    """Pass 0a output — the classification gate that Phase 0.5 consumes."""

    model_config = ConfigDict(extra="ignore")  # legacy fields (conference_context, primary_text_sources) silently dropped

    name: str
    type: VoiceType
    subtype: VoiceSubtype = None
    voice_mode: VoiceMode = None
    hostile_sources: bool = False
    corpus_constraint: CorpusConstraint = "full"
    mediation_stance: MediationStance = None

    manual_grounding: str | None = Field(
        default=None,
        description="Human-curated grounding text the model can rely on for "
        "classification context. For human voices: Wikipedia lead paragraph "
        "or curator-written disambiguation note. For non-human voices: a "
        "Godfrey-Smith / Te Awa Tupua / similar domain-specific excerpt from "
        "<project_root>/inputs/non_human_grounding/.",
    )
    wikipedia_url: str | None = None

    editorial_rationale: str | None = Field(
        default=None,
        description="Curator-written answer to 'Why is this voice in the "
        "Assembly?' The model does NOT propose this; Pass 0a surfaces the "
        "need, Pass 0b's hybrid tailoring uses it. Fill in after reviewing "
        "the pass_0a_review.md or pass via --editorial-rationale.",
    )
