"""Shared analytical-context models for 1-arch-03 additive merge.

Captures scholarly-interpretive material that the tight-recipe chunk schemas
(ReasoningMethod.steps[5-8], Moves[3-6]) silently dropped under the pre-
1-arch-03 architecture. Under additive merge, this material is preserved
explicitly so downstream Pass 2-6 synthesis draws from full research.

Used by:
- Pass 1.3 REASONING: `analytical_context_reasoning` top-level output
- Pass 1.4 VOICE: `analytical_context_voice` top-level output (optional)
- Pass 1.5 BOUNDARIES: embedded via `SensitiveTopic.scholarly_reception`
- Pass 1.6 CORPUS: `bibliographic_scholarly_context` + `translator_tradition_coverage`

Content examples (Dostoevsky §3 reasoning):
- structural_patterns[]: scandal-scene, carnivalization, crowning/decrowning,
  threshold-chronotope, sideshadowing, confession-under-pressure
- worked_demonstrations[]: Nechaev affair 1869 → Demons splitting mechanism;
  Alyosha death 1878 → Karamazov Believing-Women scene; Pushkin Speech 1880
  → Aleko/Onegin/Tatyana reframing
- scholarly_debates[]: Morson/Emerson on polyphony-vs-carnivalization; Williams
  vs. Frank on Myshkin failure; McReynolds/Patyk/Maiorova on vsechelovechnost'
  entanglement

Underscore-prefixed file per _entry.py convention: shared models are not
auto-discovered as chunk outputs. `chunk_runner._inline_schemas()` inlines
these models into merge prompts via `{{ analytical_context_schema }}` etc.
on-demand via `model.model_json_schema()` — works regardless of file name.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from ._conventions import EvidenceTag, SourceCitation


class StructuralPatternInstance(BaseModel):
    """One concrete instance of a named structural pattern in the voice's work.

    Example for Dostoevsky's scandal-scene pattern:
        work: "The Idiot, Part I, chs. 13-16"
        brief: "Nastasya Filippovna's name-day party. Confession-game as
                carnivalized sacramental-confession; Rogozhin's burst-entry
                with 100,000 roubles wrapped in Stock Exchange News; Nastasya
                throws it into the fire — simultaneous crowning (heiress,
                Myshkin's bride) and decrowning (fallen woman)."
        cross_refs: ["Republic-VII-cave (typological parallel)", "Demons-III-1-fete"]
    """

    work: str = Field(
        ..., description="Canonical reference for the passage/scene. "
        "Example: 'The Brothers Karamazov, Book II, ch. 8 (the Scandalous Scene)'."
    )
    brief: str = Field(
        ..., description="2-4 sentence description of the instance. "
        "Preserve enough detail that Pass 3/4a synthesis can draw from it."
    )
    cross_refs: list[str] = Field(
        default_factory=list,
        description="Other instances of this or related patterns. Optional.",
    )


class StructuralPattern(BaseModel):
    """A named recurring structural pattern in the voice's work — NOT the
    same as a reasoning step. Patterns are descriptive generic forms
    (scandal-scene, carnivalization, threshold-chronotope) that the voice
    employs across multiple works. Reasoning steps are the method's
    cognitive moves.

    Pass 3 may reference structural patterns when synthesizing reasoning_
    method operational_notes. Pass 4a may reference them in
    characteristic_moves. Preserving them at the merge layer prevents loss
    of scholarly analytical framing.

    Example:
        name: "scandal-scene"
        description: "A pre-arranged gathering in a high-decorum setting
                     (salon, monastery cell, name-day party, public fete)
                     into which a buffoon, provocateur, or self-destructive
                     catalyst is introduced, until the container breaks and
                     every character's concealed ideological position is
                     forced into simultaneous open speech. Bakhtin's
                     'anacrisis' — the provocation of the word by the word."
        instances: [... 5 named instances ...]
        scholarly_source: "Bakhtin (PDP ch. 4); Terras (A Karamazov Companion,
                          'conclaves'); Grossman (Poetika Dostoevskogo 1925,
                          edinstvo mesta i vremeni); Jackson (Dialogues with
                          Dostoevsky, ethical reading of obraz)"
    """

    name: str = Field(
        ..., description="Short pattern name as used in scholarship. "
        "Example: 'scandal-scene', 'carnivalization', 'threshold-chronotope'."
    )
    description: str = Field(
        ..., description="What the pattern is, structurally + functionally. "
        "Include scholarly vocabulary (anacrisis, crowning/decrowning, etc.) "
        "where applicable. No length cap."
    )
    instances: list[StructuralPatternInstance] = Field(
        default_factory=list,
        description="Concrete instances in the voice's work. For well-documented "
        "patterns expect 3-5+ instances; include all that sources surface.",
    )
    scholarly_source: str = Field(
        ..., description="Scholar(s) who identified/theorized this pattern. "
        "Named attribution matters for downstream citation.",
    )
    evidence_tag: EvidenceTag = Field(default="scholarly_consensus")
    citations: list[SourceCitation] = Field(default_factory=list)


class WorkedDemonstration(BaseModel):
    """Detailed demonstration connecting a historical event / life-situation
    to the voice's rhetorical-textual response. Captures the 'how did this
    life-event produce this novel' connective tissue that the tight
    reasoning_method.steps schema silently dropped.

    Example (Dostoevsky):
        label: "Nechaev affair 1869 → Demons splitting mechanism"
        historical_context: "Sergey Nechaev's cell strangled, shot, and dumped
                            the student Ivan Ivanov through the ice at Moscow's
                            Petrovsky Agricultural Academy pond on 21 November
                            1869 — a murder staged to bind the cell through
                            shared guilt per Nechaev's Catechism of a
                            Revolutionary. Dostoevsky was in Dresden; Anna's
                            brother Ivan Snitkin, a student at the Academy,
                            had described Ivanov to Dostoevsky personally as
                            someone who had publicly repudiated the radicals."
        voice_response: "Rather than denouncing Nechaev in a pamphlet,
                        Dostoevsky built Pyotr Verkhovensky — and when the
                        type proved too narrow, split off Stavrogin (Byronic
                        aristocratic charisma without belief), Kirillov
                        (logical atheism carried to man-god suicide), Shatov
                        (Slavophile religious nationalism — the converted
                        Ivanov). Shigalyov inherits the doctrinal husk:
                        'Starting from unlimited freedom, I end with unlimited
                        despotism' (Demons II.7). Four distributed bearers
                        of fragments a single character cannot hold."
        rhetorical_moves_employed: ["Incarnate the idea in a person",
                                    "Split the idea across doubles",
                                    "Follow the logic to its lived end"]
        scholarly_citations: [Frank, The Miraculous Years 1995; Wasiolek
                              notebooks 1969-70]
    """

    label: str = Field(
        ..., description="Short label. Format: '<event> → <response>'. "
        "Example: 'Nechaev affair 1869 → Demons splitting mechanism'."
    )
    historical_context: str = Field(
        ..., description="What happened, with dates, locations, actors. "
        "Preserve detail from sources. No length cap."
    )
    voice_response: str = Field(
        ..., description="How the voice processed the event in texts/actions. "
        "Concrete — what novels, what passages, what rhetorical moves. "
        "No length cap.",
    )
    rhetorical_moves_employed: list[str] = Field(
        default_factory=list,
        description="Cross-reference to ReasoningMethod.steps[].name values "
        "or structural pattern names. Links the worked demo back to the "
        "abstract reasoning-method skeleton.",
    )
    scholarly_citations: list[SourceCitation] = Field(default_factory=list)
    evidence_tag: EvidenceTag = Field(default="scholarly_consensus")


class ScholarlyDebate(BaseModel):
    """A named scholarly debate bearing on the voice's reasoning / voice /
    boundaries. Preserve interpretive-tradition breadth; do not flatten to
    one reading.

    Example (Dostoevsky §3):
        name: "Polyphony vs. carnivalization as distinct analytical concepts"
        positions: "Morson/Emerson (Mikhail Bakhtin: Creation of a Prosaics,
                   1990) insist polyphony (a property of authorial position)
                   and carnivalization (generic inheritance via Socratic
                   dialogue + Menippean satire) must NOT be collapsed. The
                   1929 Bakhtin proposed polyphony; the 1963 revision added
                   carnivalization as separate. Scanlan (2002) treats them
                   as complementary; Emerson et al. (1990) warn against
                   flattening."
        bearing: "Reasoning-method synthesis should distinguish
                 authorial-position polyphony (voice speaks with others, not
                 over them) from generic-form carnivalization (scandal-scenes,
                 crowning/decrowning, mésalliance). Flattening misses that
                 polyphony-alone does not produce Dostoevsky's form; the
                 carnival substrate is necessary condition."
    """

    name: str = Field(
        ..., description="Short label naming the debate."
    )
    positions: str = Field(
        ..., description="The debate's structure — named scholarly camps + "
        "their positions. Include evidence / works cited.",
    )
    bearing: str = Field(
        ..., description="What this debate means for synthesizing the voice. "
        "Actionable — not just 'scholars disagree' but 'therefore Pass X "
        "should do Y'.",
    )
    evidence_tag: EvidenceTag = Field(default="scholarly_consensus")
    citations: list[SourceCitation] = Field(default_factory=list)


class AnalyticalContext(BaseModel):
    """Container for scholarly-interpretive material preserved at merge layer.

    Under 1-arch-03, this container holds material that the pre-arch-03
    tight-recipe chunk schemas silently dropped. Pass 2-6 synthesis reads
    this container + the primary chunk outputs (reasoning_method, moves,
    etc.) to produce richer card fields.

    Each list is uncapped — preserve what sources surface. Empty lists are
    acceptable for voices where a given analytical dimension doesn't apply
    (e.g., non-human organisms may have no `worked_demonstrations[]` of the
    life-event-to-response shape; instead their analytical_context might be
    dominated by `structural_patterns` of behavioral repertoire).
    """

    structural_patterns: list[StructuralPattern] = Field(
        default_factory=list,
        description="Named recurring structural patterns (scandal-scene, "
        "carnivalization, threshold-chronotope, perceptual-response cycle, "
        "etc.) with worked instances.",
    )
    worked_demonstrations: list[WorkedDemonstration] = Field(
        default_factory=list,
        description="Detailed demonstrations connecting historical events to "
        "rhetorical-textual responses. For human voices: life-event → novel. "
        "For non-human voices: environmental condition → behavioral pattern.",
    )
    scholarly_debates: list[ScholarlyDebate] = Field(
        default_factory=list,
        description="Named scholarly debates bearing on this dimension of the "
        "voice. Preserve interpretive-tradition breadth; do not flatten.",
    )
