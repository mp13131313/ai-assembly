"""Interpretive-frames schema (1-arch-06, 2026-04-22).

A top-level chunk-output key, produced at Pass 1.2, holding cross-cutting
scholarly material that doesn't fit a specific commitment / concept /
reasoning_method / move / etc. Three kinds of content:

1. **Interpretive methods** — ways scholars read the voice: Kasatkina's
   subject-to-subject method (dvusostavnyi obraz), Patyk's provocation
   frame, hesychast reading of Raskolnikov's numerology, etc.

2. **Cross-disciplinary re-framings** — Gemini's signature contribution.
   Postcolonial (McReynolds, Tlostanova), feminist (Berman, Maiorova),
   affect theory (Sobol), legal-economic (Todd, Murav), disability studies
   (Rising), ecological (Marullo), gift-economy / Levinasian (Kliger,
   Vinokur), post-2022 Ukrainian reception (Kokobobo, Yermolenko,
   Zabuzhko, Hundorova, Pattison).

3. **Voice-level contested readings** — controversies about the voice
   as a whole: Dostoevsky's antisemitism structural-vs-incidental;
   Myshkin failure intrinsic-vs-character-limitation; Bakhtin polyphony
   relativism-vs-authorial-guidance.

Without this container, cross-cutting material fragments across
`scholarly_context` sub-fields on multiple keys or drops entirely.
Empirically observed in Dostoevsky Stage 1: hesychasm (Kasatkina 2022
essay) appears in both Perplexity §2 and Gemini §2 but was absent from
the full merged dossier — the merge LLM had nowhere to put it.

Downstream consumption (per 1-arch-05 Part A; not yet wired at
2026-04-22):
- Pass 3 reads `frame_type ∈ {interpretive_method, cross_disciplinary_reframing}`
  to inform constitution framing + concept_lexicon scholarly attribution.
- Pass 4a reads `frame_type = cross_disciplinary_reframing` to inform
  voice register scholarly notes.
- Pass 2 reads `frame_type = voice_level_debate` to inform
  topics_requiring_care nuance.

See _workspace/planning/PIPELINE_REVIEW_FIXES.md § 1-arch-06.
"""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from ._conventions import EvidenceTag, SourceCitation


FrameType = Literal[
    "interpretive_method",           # Kasatkina subject-to-subject, hesychast reading
    "cross_disciplinary_reframing",  # postcolonial, feminist, affect theory, etc.
    "voice_level_debate",            # antisemitism structural-vs-incidental, etc.
]


class InterpretiveFrame(BaseModel):
    """One scholarly frame for reading the voice.

    A frame is not the voice's own claim — it's a lens. The voice doesn't
    "have" a postcolonial frame; scholars use postcolonial analysis to
    read the voice. The `relationship_to_voice` field captures how the
    frame relates to the voice's own conceptual apparatus.
    """

    name: str = Field(
        ...,
        description="Short label — 'hesychast-numerology reading', "
        "'postcolonial Janus face', 'Kasatkina subject-to-subject method', "
        "'Williams-vs-Frank on Myshkin failure'. Noun phrase, not sentence.",
    )
    frame_type: FrameType = Field(
        ...,
        description="Discriminator. `interpretive_method` for methodological "
        "lenses (close-reading-with-a-needle, hesychast structural reading). "
        "`cross_disciplinary_reframing` for second-discipline readings of the "
        "same underlying material (postcolonial, feminist, disability studies, "
        "etc.). `voice_level_debate` for controversies about the voice as a "
        "whole (not about specific claims).",
    )
    description: str = Field(
        ...,
        description="2-4 sentence gloss. What the frame claims; what it re-reads.",
    )
    primary_scholars: list[str] = Field(
        default_factory=list,
        description="Scholar-name + year tags: ['Kasatkina 2022', "
        "'Stepanian-Rumiantseva 2023']. Preserve attribution.",
    )
    what_it_re_reads: list[str] = Field(
        default_factory=list,
        description="Which commitments / concepts / formative-experiences / "
        "works the frame re-reads. Cross-reference strings into other "
        "chunk keys: ['commitments.faith_vs_truth', 'concepts.sobornost'', "
        "'formative_candidates.Semenovsky_execution']. Best-effort; use "
        "natural language when path references don't fit cleanly.",
    )
    relationship_to_voice: Literal[
        "the_voice_invites_this_frame",   # Kasatkina argues the voice's own work invites hesychast reading
        "scholars_impose_this_frame",     # post-hoc disciplinary lens not in voice's conceptual apparatus
        "frame_contested_among_scholars", # debate about whether the frame applies at all
    ] = Field(
        ...,
        description="How does the frame relate to the voice's own self-"
        "understanding? `the_voice_invites_this_frame` when the voice's own "
        "work signals the frame (Kasatkina's dvusostavnyi obraz argues "
        "Dostoevsky's realism ITSELF operates on two-level symbolic-literal; "
        "the voice invites the reading). `scholars_impose_this_frame` when "
        "the frame is post-hoc disciplinary lens (Rising's disability studies "
        "framework is 2020s scholarship, not Dostoevsky's own conceptual "
        "apparatus). `frame_contested_among_scholars` when scholars disagree "
        "on applicability (is Bakhtin's polyphony actually present, or an "
        "interpretive imposition? Vetlovskaya vs. Bakhtin).",
    )
    citations: list[SourceCitation] = Field(
        default_factory=list,
        description="Scholar citations with work + locus where the frame "
        "is developed.",
    )
    evidence_tag: EvidenceTag = Field(
        default="scholarly_consensus",
        description="Evidence tier for the frame's claim. Most frames are "
        "scholarly_consensus or contested; interpretive_reconstruction where "
        "a frame is a single scholar's distinctive thesis not yet absorbed "
        "into mainstream reception.",
    )


class InterpretiveFrames(BaseModel):
    """Top-level chunk output container. Produced at Pass 1.2 per 1-arch-06."""

    frames: list[InterpretiveFrame] = Field(default_factory=list)
