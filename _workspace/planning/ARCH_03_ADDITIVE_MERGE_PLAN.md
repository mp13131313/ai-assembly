# ARCH-03: Additive Merge Architecture — Implementation Plan

**Status:** PROPOSED · awaiting implementation
**Severity:** HIGH architectural
**Scope:** Pass 1.1–1.7 merge layer redesign
**Depends on:** Nothing (supersedes parts of current architecture)
**Supersedes:** `1-arch-02` (Gemini re-route proposal — absorbed by additive merge)
**Preserves:** `1-arch-01` (curated_corpus_passages routing — still deferred post-Phase-N)
**Affects:** merge prompts + schemas + Pass 1.7 coherence + modest Pass 2–6 tuning
**Does NOT affect:** Research layer (Phase 0 + 0.5), Pass 1c/1d (primary-text fetch + excerpt selection), Pass 7 validation family, Derive, Runtime Voice Pipeline (consumes card, not merged_dossier)

**Companion doc:** `_workspace/planning/PIPELINE_REVIEW_FIXES.md` (Wave 1–3 review findings; fix triage in §9 below references tracker fix IDs)

---

## 0. TL;DR

**Problem:** Current Pass 1.1–1.6 merge chunks compress rich multi-source research into **tight-recipe Pydantic schemas** (e.g., `ReasoningMethod.steps[5-8]`, `Moves[3-6]`), forcing content compression that becomes **content loss**. Phase L Dostoevsky empirical measurement: 60–70% of Claude DR §3/§4/§5 analytical content is dropped at merge and never surfaces downstream.

**Fix:** Redesign merge as **additive consolidation** — three source dossiers per section become one coherent per-section dossier with redundancies stripped, contradictions reconciled, and all unique content preserved. Move synthesis-to-card-field work downstream to Pass 2–6 where it belongs.

**Effect:**
- Merged dossier grows ~2× (~162KB → ~300–400KB for Dostoevsky)
- Pass 2–6 input grows proportionally; modest max_tokens bumps
- ~60–70% of previously-lost DR §3/§4/§5 content preserved for downstream synthesis
- Pass 2–6 becomes genuine synthesis-from-rich-source instead of field-mapping-from-pre-compressed-output
- Per-voice cost: +$20–40; per 12 voices: +$250–500 (small fraction of total pipeline cost)
- Quality hypothesis: measurably richer card fields, especially voice/engagement/reasoning

**Implementation effort:** ~2–3 days focused engineering + testing.

**Timing:** Before Phase N. Avoid running 11 more voices on lossy architecture.

---

## 1. Context + rationale

### 1.1 Problem statement

The research phase produces three source dossiers per voice (Perplexity sonar-deep-research + Gemini 2.5 Pro + Claude Opus 4.7 Deep Research with 6 per-section sessions). Total surfaced research on Dostoevsky: **411,802 chars** of substantive content (Claude DR 258K + Perplexity 137K + Gemini 17K).

The current Pass 1.1–1.6 chunked merge reads 3 per-section source slices and produces schema-shaped JSON outputs: `LifeScaffold`, `Commitment[]`, `Concept[]`, `Tension[]`, `ReasoningMethod`, `Textures`, `Moves`, `Register`, `Vocabulary`, `KnowledgeBoundary`, `SensitiveTopics`, `HardLimits`, `Works`, `Passages`, `URLs`, `ReferenceOnlyPassages`. These schemas have **tight recipe shapes**: `ReasoningMethod.steps: 5–8 items`, `Moves: 3–6 items`, `HardLimits: 3–5 items`, etc.

The LLM (Opus 4.7 adaptive thinking, 32K max_tokens) must fit full per-section research into these tight shapes. What doesn't fit is dropped.

### 1.2 Evidence from Dostoevsky Phase L

Per-section character ratios (DR input → merged chunk output; Perplexity and Gemini also contribute):

| DR § | DR chars | Merged chars | Ratio | Category |
|---|---|---|---|---|
| §1 BIOGRAPHICAL | 49,539 | 41,426 | 84% | Near-parity (schema fits) |
| §2 INTELLECTUAL | 48,442 | 44,630 | 92% | Near-parity (schema fits) |
| §3 REASONING | 41,475 | 11,249 | **27%** | **Heavy loss** |
| §4 VOICE | 45,124 | 10,827 | **24%** | **Heavy loss** |
| §5 BOUNDARIES | 54,025 | 15,970 | **30%** | **Moderate loss** |
| §6 CORPUS | 19,697 | 39,907 | 203% | Expansion (DR thin; Perp+Gemini carry) |

Deep-read of §3 REASONING (documented in tracker Wave 3 notes) confirms ~60–70% of DR §3 analytical content is **lost not compressed**:

- Carnivalization sub-section (§3.2, ~3K): entire 30% of DR §3's structural-analytical framework dropped
- 14-item Menippean features checklist (§3.2, ~1K): dropped
- 4-of-5 scandal-scene instances (§3.1, ~2K): only 1 preserved as example
- 3 worked demonstrations (§3.4, ~10K): connective tissue between life-events and novels gone (Nechaev→Demons via splitting; Alyosha death→Karamazov via Believing Women; Pushkin Speech via Aleko/Onegin/Tatyana)
- Holbein Basel 1867 formative-pressure point: dropped
- Williams vs. Frank interpretive contrast: dropped
- Terras "conclaves" + Grossman + Jackson "obraz" terminology + analysis: lost (some preserved in citations list, content analysis gone)

### 1.3 Root cause

**Tight-recipe schemas at merge force content-shape compression.**

`ReasoningMethod.steps[5–8]` is a reasoning *recipe*, not a scholarly dossier. DR §3's rich biographical-textual-scholarly synthesis doesn't map into 8-step structure. Opus 4.7 is forced to select 8 items and drop the rest. Dropped content goes nowhere — not into other chunks, not into merged_dossier, not surfaced at Pass 2–6.

**Design assumption that produced this (per REBUILD_PLAN PB#3/#4):**
- "Pass 1 emits typed JSON matching designed schemas"
- "Pass 2 does field-mapping to persona card"

This positioned Pass 2 as a field-mapping layer, which is low-value work for Opus 4.7. Field-mapping compressed-output → card field doesn't use Opus's synthesis capabilities. Pass 2 should do genuine synthesis; it requires richer source material.

**The design conflates two tasks:**
1. Consolidate three research sources (dedupe, reconcile, organize) — the legitimate merge job
2. Synthesize research into persona-card-field shapes (extraction + framing) — the legitimate Pass 2–6 job

Current architecture collapses both into the merge step. Loses research at step 1 compressing into step 2's target shape.

### 1.4 The fix

Separate the two tasks. Merge becomes additive consolidation. Pass 2–6 becomes genuine synthesis-from-rich-source.

---

## 2. Architectural contract

### 2.1 What merge layer does under 1-arch-03

Pass 1.1–1.6, per section, produces **one coherent per-section dossier** combining three sources:

1. **Read** Perplexity §N + Claude DR §N + Gemini (full; Gemini not sectioned per PB#1) for the chunk's topical area.
2. **Identify** redundancies across sources (same fact in different wording).
3. **Dedupe** redundancies: keep best-sourced or richest version; discard exact duplicates.
4. **Identify** contradictions across sources (different dates, different interpretations, different scholarly framings).
5. **Reconcile** contradictions:
   - If one source has explicit primary-text or scholarly-consensus support and others don't: prefer the supported one, note others in `contested_readings[]` or `Tension[]`.
   - If contested across scholarly traditions (e.g., Dostoevsky's father's death): preserve contested status in `Tension[]` or equivalent; do NOT pick one arbitrarily.
6. **Organize** all unique content into Boddice §13/§14/§15 section structure + per-chunk canonical organization (life_scaffold, formative_candidates, commitments, etc.).
7. **Preserve** analytical depth: scholarly context, worked demonstrations, structural patterns, interpretive debates, translator-tradition comparisons, biographical-to-textual connections.
8. **Output** permissive-schema JSON with elaborate content fields — uncapped or loosely-capped counts, rich prose content.

**Merge does NOT:**
- Select N-best items to fit a recipe (no "pick 8 reasoning steps from 30 candidates")
- Produce near-final card-field shapes
- Compress to fit downstream consumption patterns
- Make interpretive commit-to-one decisions (formative, primary reasoning mode, etc.)

### 2.2 Contract with downstream Pass 2–6

**Pass 2–6 can now assume:**

1. **Merged_dossier preserves all unique research content** (deduped, contradiction-reconciled, organized). If a detail appeared in any source, it appears in merged_dossier unless flagged redundant or contradictory.
2. **Merged_dossier is organized by Boddice §13/§14/§15 structure** + chunk-specific canonical organization. Pass 2–6 prompts can reference sections/sub-fields specifically.
3. **Contradictions are marked**: `Tension[]`, `contested_readings[]`, or evidence_tag=`inference` with both readings cited.
4. **Evidence tags are preserved** per the 5-tag frozen convention (stated / scholarly_consensus / inference / experiential_reconstruction / projection_warning).
5. **Citations are preserved** (tier_1_primary / tier_2_scholarly / tier_3_contested).

**Pass 2–6's job becomes:**

1. Read rich merged_dossier with full research preserved.
2. **Select** relevant material for each card field (synthesis work).
3. **Shape** selected material into card field (apply Boddice rubrics, register discipline, anti-flattening).
4. **Commit** to single-value fields (primary formative, 10–20 constitution principles, 5–10 curated passages) with explicit reasoning.
5. **Preserve supporting material** where appropriate (multi-source formative context, contested readings as tensions).

Pass 2–6 does genuine field-synthesis from rich source, not field-mapping from pre-compressed output.

### 2.3 What remains unchanged

**Research layer (Phase 0 + 0.5):** unchanged structurally. All Wave 1 tracker fixes still apply.
- Pass 0a voice config
- Pass 1a Perplexity (4 voice-type variants)
- Pass 1b Gemini (4 voice-type variants)
- Pass 0b Jinja render (wrapper + header + 4 bodies + footer)
- Pass 0b tailor (hybrid Jinja+LLM Opus 4.7)
- Manual Claude DR (6 per-section sessions)

**Pass 1c + 1d (primary-text fetch + excerpt selection):** unchanged structurally. Reads merged_dossier.urls to fetch; produces primary_block for Pass 4a. All Wave 2 tracker fixes still apply.

**Pass 7 validation family:** unchanged structurally.
- Pass 7-pre citation verification (reads card against primary texts + merged_dossier)
- Pass 7-anachronism TimeChara-style check
- Pass 7a cross-model validation (Gemini primary, OpenAI fallback chain per PB#1)
- Pass 7b smoke test chains
- Pass 7c negative constraints refinement

**Derive:** unchanged structurally. Reads complete card, produces provocateur_profile + evaluation_rubric.

**Runtime Voice Pipeline:** unchanged. Consumes persona_card_assembled.json, not merged_dossier.json. Architectural change stops at the card boundary.

---

## 3. Schema redesign

Target: `personas/schemas/`. Principle: **structure preserved (Boddice rubrics, section organization); content capacity expanded (uncapped or loosely-capped counts, elaborate prose fields, new analytical-context containers).**

### 3.1 `_conventions.py` — frozen conventions preserved

**No changes to frozen conventions** per PB#7:
- `EvidenceTag` enum: `stated` | `scholarly_consensus` | `inference` | `experiential_reconstruction` | `projection_warning` — UNCHANGED
- `SourceCitation` model (author + work + year + page + url + tier) — UNCHANGED
- `Tier` enum (tier_1_primary | tier_2_scholarly | tier_3_contested) — UNCHANGED
- `ContestedReading` model — UNCHANGED (now actually used; see 3.3)
- `ProjectionWarning` model — UNCHANGED

### 3.2 `pass_1_1.py` — LifeScaffold + FormativeCandidate

**Current shape (recipe-tight):**
- `PeriodPathos` list with "5-10 terms" guidance in prompt
- `anachronisms_to_avoid`: "4-8 modern terms" guidance in prompt
- `FormativeCandidate[]`: "2-5 candidates" guidance in prompt

**Proposed shape (permissive):**

```python
class LifeScaffold(BaseModel):
    """Boddice §13 5-part world rubric + biographical foundation.
    
    Permissive container: accepts full additive-merge content from three
    sources. Counts are minimums, not maximums. Pass 2 synthesizes to
    card's `world` field.
    """
    name: str
    type: Literal["human", "non_human", "fictional"]
    subtype: Literal["organism", "system"] | None = None
    birth_year: int | None = None
    death_year: int | None = None
    primary_locations: list[str] = Field(default_factory=list)
    institutions_founded_joined_opposed: list[str] = Field(default_factory=list)
    key_relationships: list[KeyRelationship] = Field(default_factory=list)
    
    # Boddice §13 5-part world rubric
    intellectual_world: str  # Period intellectual currents; no length cap
    ontological_furniture: str  # What was *real* for this voice; no length cap
    available_pathe: list[PeriodPathos] = Field(
        default_factory=list,
        description="Period-specific affects in original language. MINIMUM 5; "
                    "preserve all non-redundant terms from sources."
    )
    framework_for_difficulty: str  # No length cap
    model_of_selfhood: str  # No length cap
    anachronisms_to_avoid: list[AnachronismEntry]  # Minimum 4; uncapped max
    
    # NEW: scholarly context capture (was silently dropped previously)
    scholarly_context: str | None = Field(
        default=None,
        description="Scholarly-interpretive context: debates about the voice's "
                    "biographical reception, contested readings of formative events, "
                    "interpretive traditions (e.g., Frank vs. Mochulsky on Dostoevsky's "
                    "father's death, Williams vs. Frank on Myshkin failure). Preserve "
                    "what sources provide; not synthesized commitment."
    )
    
    # NEW: contested readings at biographical level
    contested_readings: list[ContestedReading] = Field(
        default_factory=list,
        description="Biographical facts or interpretive framings where sources "
                    "disagree and disagreement is scholarly-real. Each entry: claim + "
                    "position_a (with source) + position_b (with source) + scholarly_status."
    )
```

New model:

```python
class AnachronismEntry(BaseModel):
    """Structured anachronism: modern term + reason + voice-native alternative."""
    modern_term: str
    reason_excluded: str
    voice_native_alternative: str | None = None  # If voice's tradition has native term
    evidence_tag: EvidenceTag = "scholarly_consensus"
    citations: list[SourceCitation] = Field(default_factory=list)
```

`FormativeCandidate` becomes richer:

```python
class FormativeCandidate(BaseModel):
    """Boddice §14 4-part rubric. MULTIPLE candidates preserved (2-N+).
    Pass 2 commits to ONE primary but references supporting candidates per 2-03 fix.
    """
    candidate_label: str
    formative_emotional_community: str  # No length cap; elaborate scholarly context welcome
    lived_through_own_apparatus: str | None = None  # Human voices
    condition_of_being: str | None = None  # Non-human / system / cosmic
    engagement_it_drives: str  # No length cap
    
    # NEW: scholarly interpretation of this candidate
    scholarly_context: str | None = Field(
        default=None,
        description="How scholars have framed this formative context. Williams vs. "
                    "Frank vs. Kasatkina on what Semenovsky-execution meant, etc. "
                    "Preserve; don't synthesize to one interpretation."
    )
    
    # NEW: cross-references to other chunks
    resonates_with_commitments: list[str] = Field(
        default_factory=list,
        description="Labels of commitments (Pass 1.2 output) this formative shapes. "
                    "Cross-chunk coherence aid — Pass 2 uses for primary formative choice."
    )
    
    evidence_tag: EvidenceTag = "experiential_reconstruction"
    citations: list[SourceCitation] = Field(default_factory=list)
    scholarly_support_score: Literal["strong", "moderate", "contested"]
```

### 3.3 `pass_1_2.py` — Commitment + Concept + Tension

**Current:**
- `commitments[10-20]` prompt-guidance
- `concepts[5-10]` prompt-guidance
- `tensions[2-6]` prompt-guidance

**Proposed:** uncap maxes; preserve structure; add scholarly_context per commitment/concept.

```python
class Commitment(BaseModel):
    statement: str
    operational_note: str  # No length cap
    textual_source: str | None = None
    unique_to_this_voice: bool
    evidence_tag: EvidenceTag
    citations: list[SourceCitation]
    
    # NEW: interpretive tradition for this commitment
    scholarly_context: str | None = Field(
        default=None,
        description="How different scholarly traditions frame this commitment. "
                    "Frank vs. Bakhtin vs. Williams on Dostoevsky's Christ-choice. "
                    "Not synthesis; preserve interpretive breadth."
    )
    
    # NEW: contested commitment handling
    contested_readings: list[ContestedReading] = Field(
        default_factory=list,
        description="If this commitment is scholar-disputed, preserve disputing readings."
    )

class Concept(BaseModel):
    term: str
    term_in_original_language: str | None = None
    definition: str  # No length cap
    what_it_rules_out: str  # Mandatory; no length cap
    textual_source: str | None = None
    unique_to_this_voice: bool
    evidence_tag: EvidenceTag
    citations: list[SourceCitation]
    
    # NEW: translation-tradition handling for non-English concepts
    translation_tradition_notes: str | None = Field(
        default=None,
        description="If concept has translator-tradition variation (Garnett vs. P&V on "
                    "Dostoevsky's 'nadryv' renderings), preserve."
    )

class Tension(BaseModel):
    description: str  # No length cap
    conflicting_commitments: list[str]
    passage_citations: list[SourceCitation]
    evidence_tag: EvidenceTag
    
    # NEW: is this tension productive (Plato R-vs-L) or contradictory (to-resolve)?
    tension_type: Literal["productive", "contested", "unresolved"] = "productive"
    scholarly_context: str | None = None
```

Prompt-level count guidance becomes: "MINIMUM 10 commitments, 5 concepts, 2 tensions; preserve all non-redundant commitments from sources — well-documented voices may produce 20-40 commitments. Do NOT cap to fit a card-field shape; Pass 3 synthesizes to constitution."

### 3.4 `pass_1_3.py` — ReasoningMethod + Textures + **NEW** analytical containers

**Current:** `ReasoningMethod.steps[5-8]` + `Textures` (finds_compelling + resists).

**Proposed:** add three new analytical-context containers that hold the DR §3 content currently dropped.

```python
class ReasoningMethod(BaseModel):
    voice_mode: Literal["philosophical", "observational", "narratival"] | None = None
    summary: str  # 1-paragraph summary of how this voice reasons
    steps: list[ReasoningStep]  # MINIMUM 5, uncapped; preserve all step-candidates
    dialectical_signature: DialecticalSignature | None = None  # Card-shape preview
    
    evidence_tag: EvidenceTag = "scholarly_consensus"
    citations: list[SourceCitation]

class ReasoningStep(BaseModel):
    step_number: int | None = None  # Optional — for voices whose reasoning isn't sequential
    name: str
    description: str  # No length cap
    example: str  # Concrete example; no length cap
    scholarly_context: str | None = None  # Williams/Frank/Morson on this step

class Textures(BaseModel):
    finds_compelling: list[str]  # Minimum 4; uncapped
    resists: list[str]  # Minimum 4; uncapped
    scholarly_context: str | None = None

# NEW: analytical-context container for §3.1-3.2-style material
class StructuralPattern(BaseModel):
    """Named recurring structural pattern in voice's work (e.g., scandal-scene,
    crowning/decrowning, threshold-chronotope). Pass 3 may reference in
    reasoning_method synthesis; Pass 4a may use for moves-extraction.
    """
    name: str  # e.g., "scandal-scene", "carnivalization"
    description: str
    instances: list[StructuralPatternInstance]  # Worked examples in voice's texts
    scholarly_source: str  # Bakhtin, Morson, Jackson, etc.
    evidence_tag: EvidenceTag
    citations: list[SourceCitation]

class StructuralPatternInstance(BaseModel):
    work: str  # e.g., "The Idiot I.13-16"
    brief: str  # 2-4 sentence description of the instance
    cross_refs: list[str] = Field(default_factory=list)  # Related passages

# NEW: worked-demonstration container for §3.4-style material
class WorkedDemonstration(BaseModel):
    """Detailed demonstration connecting life-event/historical-event to voice's
    rhetorical-textual response. Pass 3 may reference; Pass 4a/4b may draw from.
    """
    label: str  # e.g., "Nechaev affair 1869 -> Demons splitting mechanism"
    historical_context: str
    voice_response: str  # How voice processed the event in texts
    rhetorical_moves_employed: list[str]  # Cross-ref to ReasoningStep.name
    scholarly_citations: list[SourceCitation]
    evidence_tag: EvidenceTag = "scholarly_consensus"

class AnalyticalContext(BaseModel):
    """Wrapper for §3's analytical-scholarly material previously dropped.
    Added to Pass 1.3 output (and parallel containers in 1.4, 1.5).
    """
    structural_patterns: list[StructuralPattern] = Field(default_factory=list)
    worked_demonstrations: list[WorkedDemonstration] = Field(default_factory=list)
    scholarly_debates: list[str] = Field(
        default_factory=list,
        description="Named scholarly debates bearing on voice's reasoning "
                    "(Williams vs. Frank on Myshkin, Morson/Emerson on "
                    "polyphony-vs-carnivalization, etc.)"
    )
```

### 3.5 `pass_1_4.py` — Moves + Register + Vocabulary + AnalyticalContext

Similar treatment: uncap maxes; add `AnalyticalContext` container for voice-signature scholarly material.

```python
class Moves(BaseModel):
    moves: list[Move]  # Minimum 3; uncapped

class Move(BaseModel):
    name: str
    description: str
    example: str | None = None
    scholarly_context: str | None = None  # Bakhtin/Jackson/Kasatkina on this move
    structural_pattern_refs: list[str] = Field(
        default_factory=list,
        description="Cross-ref to StructuralPattern names in Pass 1.3 analytical_context."
    )

class Register(BaseModel):
    rhetorical_mode: str
    register_and_tone: str  # What IS + what IS NOT
    tradition_note: str | None = None  # For oral/ritual/performative voices
    
    # NEW: register-gradation across genres
    genre_specific_register: dict[str, str] = Field(
        default_factory=dict,
        description="How register varies by genre (e.g., Dostoevsky: fiction = "
                    "feverish-confessional; journalism = polemic-sharp; letter = "
                    "direct-earnest; hagiography = paratactic-scripture-cadenced). "
                    "Preserve genre-register mapping for Pass 4a."
    )
    
    # NEW: translator-tradition notes (for translated voices)
    translator_tradition_notes: str | None = Field(
        default=None,
        description="How different translators shape voice register. Preserve for "
                    "Pass 4a decision on which translation grounds voice exemplar."
    )

class Vocabulary(BaseModel):
    preferred_vocabulary: list[VocabEntry]  # Minimum 15; uncapped
    metaphorical_repertoire: dict[str, str]  # Minimum 3; uncapped
    scholarly_context: str | None = None  # Scholarly treatments of voice's lexicon

class VocabEntry(BaseModel):
    term: str
    term_in_original_language: str | None = None
    gloss: str
    loadbearing: bool = False  # Philosophically/theologically central term
    translation_notes: str | None = None
```

Add voice-specific `AnalyticalContext` to `pass_1_4` output with: stylistic-reception-history, translator-tradition-criticism, metaphor-family scholarly mapping, rhythm-cadence analysis.

### 3.6 `pass_1_5.py` — KnowledgeBoundary + SensitiveTopics + HardLimits + scholarly debate container

```python
class KnowledgeBoundary(BaseModel):
    general_frame: str  # No length cap
    temporal_exclusions: list[ExclusionEntry]
    geographic_exclusions: list[ExclusionEntry]
    conceptual_exclusions: list[ExclusionEntry]

class ExclusionEntry(BaseModel):
    term: str
    reason_excluded: str  # No length cap; preserve scholarly reasoning

class SensitiveTopics(BaseModel):
    topics: list[SensitiveTopic]  # Minimum 3; uncapped

class SensitiveTopic(BaseModel):
    topic: str
    what_the_voice_actually_thought: str  # No length cap; substantive
    navigation_guidance: str  # No length cap; the load-bearing field per §3.6
    scholarly_reception: str | None = Field(
        default=None,
        description="How different scholarly traditions frame this topic (Morson on "
                    "Dostoevsky's Jewish question, McReynolds vs. Goldstein on "
                    "vsechelovechnost' entanglement). Preserve interpretive breadth."
    )
    evidence_tag: EvidenceTag
    citations: list[SourceCitation]

class HardLimits(BaseModel):
    prohibitions: list[Prohibition]  # Minimum 3; uncapped

class Prohibition(BaseModel):
    rule: str  # No length cap
    failure_mode_addressed: str | None = None  # What generic-AI default this catches
    rationale: str | None = None  # Scholarly or empirical grounding
```

### 3.7 `pass_1_6.py` — Works + Passages + URLs + ReferenceOnlyPassages

Pass 1.6 is **already most-permissive** in current architecture (5–20+ works, 8–15 passages with full verbatim text, URLs). Less restructuring needed.

Minor additions:
- `Passages.passages[]`: uncap max (some voices may warrant 20+ passages)
- Add `translator_tradition_coverage: list[str]` to `Passages` for voices with multi-translator corpora
- Add `bibliographic_scholarly_context: str | None` at `Works` level for scholarly treatments of the canonical corpus

**Cross-reference `1-arch-01`:** the curated_corpus_passages-from-Pass-1d refactor remains a separate, post-Phase-N proposal. 1-arch-03 does NOT resolve 1-arch-01. Under 1-arch-03, Pass 1.6 still produces `passages[]` with verbatim text; 1-arch-01 would later move text-carrying to Pass 1d fuzzy-match. The two proposals compose cleanly.

### 3.8 `merged_dossier.py` — composed permissive schema

The 16-key composed MergedDossier is the union of all chunk outputs + coherence audit trail. Under 1-arch-03:

```python
class MergedDossier(BaseModel):
    # Pass 1.1
    life_scaffold: LifeScaffold
    formative_candidates: list[FormativeCandidate]
    # Pass 1.2
    commitments: list[Commitment]
    concepts: list[Concept]
    tensions: list[Tension]
    # Pass 1.3
    reasoning_method: ReasoningMethod
    textures: Textures
    analytical_context_reasoning: AnalyticalContext  # NEW
    # Pass 1.4
    moves: Moves
    register: Register  # serializes as "register" key via alias, internal attr = voice_register
    vocabulary: Vocabulary
    analytical_context_voice: AnalyticalContext | None = None  # NEW, optional
    # Pass 1.5
    knowledge_boundary: KnowledgeBoundary
    sensitive_topics: SensitiveTopics
    hard_limits: HardLimits
    # Pass 1.6
    works: Works
    passages: Passages
    urls: URLs
    reference_only_passages: ReferenceOnlyPassages
    # Pass 1.7 audit
    coherence_flags: list[CoherenceFlag]
    coherence_resolutions: list[CoherenceResolution]
```

Total size ceiling: uncapped. Expect ~300–400K chars for well-documented voices.

---

## 4. Prompt rewrites

Target: `personas/flows/shared/prompts/pass_1_1_merge.md` through `pass_1_6_merge.md`.

### 4.1 Common additive-merge discipline (all 6 chunk prompts)

Replace current Block 2 GUARDRAILS content with:

```markdown
# BLOCK 2 — ADDITIVE MERGE DISCIPLINE

Your job is to produce ONE coherent per-section dossier from three source
dossiers (Perplexity §N + Claude DR §N + Gemini full-content). The output
preserves ALL unique research content, deduped and contradiction-reconciled.

## What you DO

1. **Identify unique claims per source.** For each source, list the distinct
   facts, scholarly framings, analytical observations, and cited evidence
   present in that source on this section's topic.

2. **Dedupe redundancies.** When two or more sources present the same claim:
   - Same claim + same source (rare): keep one instance.
   - Same claim, different wording or sourcing: keep the richest version
     (most detail, best-sourced); do not preserve all wordings.
   - **When in doubt about redundancy: preserve both.** Dedupe
     conservatively. Pass 2-6 tolerates redundancy better than missing content.

3. **Reconcile contradictions.** When sources disagree:
   - If one has explicit primary-text citation or scholarly-consensus support
     and others don't: prefer the supported version. Note others in
     `contested_readings[]` or `Tension[]` as appropriate.
   - If sources represent different scholarly traditions with real scholarly
     support for competing readings: preserve contested status via
     `ContestedReading` or `Tension.tension_type = "contested"`. Do NOT pick
     one arbitrarily.
   - For factual contradictions (dates, places): prefer best-sourced; flag
     others with `evidence_tag: inference` if retained.

4. **Organize additively.** All unique content goes into one of the schema's
   canonical section fields (Boddice §13 sub-fields, commitment, concept,
   tension, reasoning step, etc.). If content doesn't fit an existing field,
   it goes into the chunk's `scholarly_context` field or the relevant
   `AnalyticalContext` container.

5. **Preserve analytical depth.** Scholarly interpretive debates, worked
   demonstrations, structural patterns, translator-tradition comparisons,
   biographical-to-textual connections — all go into scholarly_context or
   analytical_context containers. They are NOT to be compressed to fit a
   recipe shape.

## What you DO NOT

1. **Do NOT select N-best items to fit a recipe.** Schemas have minimum
   counts, not maximums. A well-documented voice may produce 25 commitments,
   40 pathe terms, 12 reasoning steps. Preserve all non-redundant material.

2. **Do NOT commit to a single primary when multiple candidates exist.**
   Pass 2 does the primary-formative-choice, primary-reasoning-step-ordering,
   commit-to-constitution-core work. Your job: preserve candidates.

3. **Do NOT compress to fit downstream consumption patterns.** Pass 2-6 reads
   richer-than-card content by design. Do not pre-shape to card fields.

4. **Do NOT silently drop content.** If content is in any of the three
   sources, it MUST appear in your merged output (deduped, reconciled) or be
   explicitly excluded with reason (flagged as contested, inference-only, or
   redundant-with-[other-entry]).

## Evidence tagging discipline

Evidence tagging (frozen convention per PB#7):
- `stated` — direct primary-text citation
- `scholarly_consensus` — uncontested scholarly reading
- `inference` — contextual inference from biography + period
- `experiential_reconstruction` — biocultural reconstruction of inner state
- `projection_warning` — modern term used faute de mieux, flagged

Every claim carries an evidence_tag. Every sourced claim has citations.
Where sources differ in evidence strength, prefer primary-text-grounded readings.

## Source-filtering discipline (ex-SRI-1)

All three sources are full-content per chunk (not sectioned-filtered):
- Perplexity §N: factual depth, citation density, primary-text anchoring
- Claude DR §N: analytical depth, scholarly synthesis, interpretive framing
- Gemini full: breadth-scan, multilingual scholarship, adjacency surfacing,
  recent reassessments, translator-tradition comparisons

All three contribute additively. Lane-filtering concern (current architecture's
SRI-1) does not apply under additive merge — the merge accepts all
non-redundant content from all three sources.
```

### 4.2 Per-chunk prompt specifications

Each of Pass 1.1–1.6 gets the common block above PLUS chunk-specific guidance.

#### 4.2.1 `pass_1_1_merge.md` — BIOGRAPHICAL

Keep Blocks 1, 3, 5, 6 largely; rewrite Block 2 per 4.1 above; update Block 4 worked examples to demonstrate additive-merge output shape (richer content, permissive counts); keep existing Boddice §13/§14 structural framing.

Chunk-specific guidance to add:
- Dedupe discipline for biographical facts (same date/place from multiple sources → keep one)
- Contested-reading preservation for disputed biographical events (father's death, specific formative-event interpretations)
- `scholarly_context` field usage for biographical-interpretive debates

Worked examples: Plato (philosophical human), Cleopatra (hostile-sourced human — NEW per 1.1-02; preserves hostile-source reconstruction pattern), Octopus (non-human organism), Whanganui (non-human system), Scheherazade (fictional — closes 1.1-06 null-discipline gap). 5 examples instead of 3. Add ~80 lines.

#### 4.2.2 `pass_1_2_merge.md` — INTELLECTUAL

Keep specificity-rule + what_it_rules_out-mandatory + tensions-not-resolved discipline from current (best-engineered chunk). Extend:
- Uncap commitments (minimum 10; well-documented voices may produce 25+)
- Each commitment can carry `scholarly_context` for interpretive debates
- `tensions[]` becomes richer: `tension_type` classification, scholarly-context per tension

Worked examples: Plato + Octopus + Whanganui + Scheherazade (NEW per 1.2-03 fictional example). Add ~40 lines.

#### 4.2.3 `pass_1_3_merge.md` — REASONING (largest restructuring)

Keep: voice_mode 5-way branching (philosophical/observational/organism/system/narratival), specificity self-test, texture-vs-topic discrimination.

Major addition: **Analytical Context instructions.** Explicit directive to produce `AnalyticalContext` containing:
- `structural_patterns[]` — named recurring patterns with worked instances (for Dostoevsky: scandal-scene, crowning/decrowning, threshold-chronotope; for Plato: elenchus, myth-within-argument, guided-question; for Octopus: perceptual-response cycle, chromatic-display, spatial-navigability)
- `worked_demonstrations[]` — connecting life-events to rhetorical-textual responses (for Dostoevsky: Nechaev→Demons splitting; Alyosha-death→Karamazov Believing-Women; Pushkin-Speech→Aleko/Onegin/Tatyana reframing)
- `scholarly_debates[]` — named scholarly debates on voice's reasoning (Williams/Frank/Morson on various interpretive questions)

Worked examples: Plato + Octopus (current) + **Dostoevsky narratival** (NEW per 1.3-02 — full shape: 8 steps + 3 worked demonstrations + 3 structural patterns + 5 scholarly debates). This is the highest-value addition because Dostoevsky is Phase-L-validated and richest in analytical-context material. Add ~150 lines of worked example (substantial but essential).

#### 4.2.4 `pass_1_4_merge.md` — VOICE

Keep: tradition-channelled-vs-individual-authorial discrimination, pathē-carryover from 1.1, reference-not-display discipline.

Additions:
- Uncap moves (minimum 3; well-documented voices may produce 8+)
- `genre_specific_register` capture in `Register`
- `translator_tradition_notes` for translated voices
- Voice-level `AnalyticalContext` with stylistic-reception-history, scholarly metaphor-family mapping

Fix 1.4-02 (complete Marley example with moves) + 1.4-03 (Octopus example) + 1.4-04 (voice_mode prior guidance) all fold in. Add ~60 lines.

#### 4.2.5 `pass_1_5_merge.md` — BOUNDARIES

Keep: sanitisation-paradox naming (best-of-prompt), expression-vs-character-level boundary with Pass 7c handoff.

Additions:
- Uncap sensitive_topics (minimum 3; contested-territory voices like Dostoevsky may produce 8+)
- `scholarly_reception` per sensitive topic (preserve interpretive traditions)
- Fix 1.5-02 (Cleopatra hostile-source example), 1.5-03 (fictional general_frame rule), 1.5-04 (voice_mode drop) all fold in

Add ~50 lines.

#### 4.2.6 `pass_1_6_merge.md` — CORPUS

Keep: two-tier musical corpus design, anti-URL-fabrication discipline, purpose-tag trichotomy.

Additions:
- `translator_tradition_coverage` in Passages
- `bibliographic_scholarly_context` in Works
- Fix 1.6-02 (Octopus example), 1.6-03 (Scheherazade example), 1.6-04 (Marley reference_only_passages private-tier), 1.6-06 (voice_mode drop) all fold in

**Cross-reference `1-arch-01`**: 1.6 still produces `passages[]` with verbatim text under 1-arch-03. 1-arch-01 (curated_corpus_passages-from-Pass-1d) remains a separate post-Phase-N refactor that composes cleanly with 1-arch-03.

Add ~80 lines.

### 4.3 Worked-example strategy

Under 1-arch-03, worked examples grow ~2-3× per chunk because they demonstrate richer output. Trade-off: prompt grows, but Opus has concrete shape to aim for.

**Budget:**
- Current total merge-prompt size: ~60KB across 6 prompts
- Projected 1-arch-03 total: ~100-120KB
- Still well within Opus 4.7 1M context

**Worked-example coverage across 6 chunks × 5 voice-type branches (human-philosophical, human-narratival, non-human-organism, non-human-system, fictional, hostile-human-special-case):**

Minimum coverage: each chunk has 3+ worked examples covering at least 3 voice-type branches. Priority voices:
- Plato (philosophical) — universal coverage
- Dostoevsky (narratival, Phase-L-validated) — universal coverage (richest DR material)
- Octopus (non-human organism) — 1.1, 1.3, 1.4, 1.5, 1.6 coverage
- Whanganui (non-human system) — 1.1, 1.2, 1.5, 1.6 coverage
- Scheherazade (fictional) — 1.1, 1.2, 1.5, 1.6 coverage
- Cleopatra (hostile-source) — 1.1, 1.5 coverage (hostile-source handling)
- Marley (musical corpus_constraint) — 1.4, 1.6 coverage

Most worked examples are lifts-from-Phase-L-Dostoevsky-card or straightforward extrapolations.

---

## 5. Pass 1.7 coherence update

Target: `personas/flows/shared/prompts/pass_1_7_coherence.md`.

### 5.1 Adjusted checks under permissive inputs

Current 7 cross-chunk checks largely survive. Adjustments:

- **Check 5 (passage-work orphan):** unchanged — structural validation, works under permissive inputs.
- **Check 7 (period-vocabulary consistency):** strengthens — pathe→vocabulary mapping should now be near-complete since both 1.1 and 1.4 preserve uncapped lists.
- **Check 6 (hard_limits/commitments consistency):** unchanged semantically; operates on richer content.
- **Check 4 (anachronism/boundary cross-check):** unchanged; may surface more items since both lists are uncapped.
- **Check 3 (voice/reasoning register alignment):** unchanged; uses permissive Register + ReasoningMethod.
- **Check 2 (concept usage in reasoning):** expands — concepts may appear in reasoning steps OR in new analytical_context structural_patterns or worked_demonstrations. Check covers all references.
- **Check 1 (formative/commitment alignment):** uses new `FormativeCandidate.resonates_with_commitments` cross-reference field as input; catches cases where candidates list and commitments list are disjoint.

### 5.2 New preservation-checks

Add two new checks specific to 1-arch-03:

**Check 8 — Source attribution preservation.**
For each major claim in merged chunks, verify source attribution is present (citation + evidence_tag). Claims without attribution: flag for review. This is the structural validator for "did merge preserve sourcing."

**Check 9 — Analytical context presence.**
For Pass 1.3 output: verify `analytical_context_reasoning` is non-empty if any source contains analytical material (structural patterns, worked demonstrations, scholarly debates). For Pass 1.4 output: verify `analytical_context_voice` similarly. Empty analytical_context on a rich-DR voice = preservation failure.

### 5.3 Coherence prompt rewrites

Update prompt text:
- Block 3 resolve-by-edit scope: "Edit scope: prefer minimal edits — append clarifying phrases, add missing terms to lists, tighten operational_notes. Do NOT rewrite entire commitments, reshape reasoning steps, or synthesize new content. If reconciliation requires more than minor edits, escalate." (1.7-02 fix)
- Block 3 escalation pathway: "Escalation-flagged items surface at the post-Pass-2 human review gate per PB#5; until reviewed, Pass 3-6 synthesis proceeds on unresolved chunk outputs." (1.7-03 fix)
- Block 3 productive-tension criteria: "ALL must hold: (a) both poles have primary-text or scholarly-consensus support; (b) tension drives rather than derails voice's thinking; (c) scholarly tradition names tension explicitly. If ANY unmet, resolve by edit." (1.7-04 fix)
- Block 4: ADD worked examples (1.7-01 fix; pattern-break repair — 3 examples covering resolve-by-edit, accept-productive-tension, escalate cases)

### 5.4 Pass 1.7 max_tokens calibration (SUPERSEDED 2026-04-22 — see §5.5)

*Original rationale under the single-call architecture:*

Input size 300-400K chars + inlined MergedDossier schema (~20K); output size full composed MergedDossier (300-400K) + coherence audit (~10-15K). Proposed max_tokens: **100,000** (bump from 64K).

**This is superseded by §5.5.** Under the split architecture, output is audit-only (~24K) and max_tokens drops to 24000. The 100K-output rationale is no longer load-bearing and exists only as historical context for why the pre-split prompt needed the headroom.

### 5.5 Pass 1.7 split architecture (amendment 2026-04-22)

**Problem with single-call Pass 1.7 (§5.1–5.4 original):** the prompt required the LLM to re-emit the full composed MergedDossier *along with* coherence metadata. This gave the LLM direct authorship of every chunk key in the output, and re-compression risk was fought with prompt-level discipline ("preserve by default, edit-scope minor only"). Correct in principle; structurally weaker than having no surface at all.

**Split architecture (landed 2026-04-22):** composition is moved out of the LLM into deterministic Python. The LLM receives the already-composed dossier and emits only a narrow audit result.

**Three stages in `personas/run_pass_1_7.py`:**

- **Stage A — offline compose (Python).** `_compose_dossier(chunks)` builds a MergedDossier-shaped dict from the six chunk JSONs with empty `coherence_flags` / `coherence_resolutions`. Pydantic-validates against `MergedDossier` (catches Pass 1.1-1.6 schema drift before the LLM sees anything). Pure dict-assembly; no semantic work, no re-compression possible.

- **Stage B — LLM coherence audit (narrow output).** One Opus 4.7 call, thinking enabled, `max_tokens=24000`. System prompt is the composed dossier + the 9 checks + edit-scope discipline. Output conforms to a new Pydantic model `CoherenceAuditResult`:

  ```python
  class CoherenceAuditResult(BaseModel):
      coherence_flags: list[CoherenceFlag]
      coherence_resolutions: list[CoherenceResolution]
      edits: list[DossierEdit]  # op: "append"|"set", path: dotted, value: Any
  ```

  The LLM never re-emits dossier content. Its only content contributions are the `value` payload of an `edit` (e.g. a new Concept to append) and the text of flags/resolutions.

- **Stage C — apply edits + re-validate (Python).** `_apply_edit(dossier, edit)` walks the `path` ("commitments[3].operational_note", "concepts", etc.) and performs `append` or `set`. Failed edits are logged-and-skipped (not fatal; final re-validate catches schema-breaking edits). Coherence metadata attached. Full dossier re-validated against `MergedDossier`; any schema break from a malformed edit halts the run.

**Discipline carried from §5.3 original:**
- Check 8 + Check 9 preservation checks remain (unchanged).
- Edit-scope discipline (1.7-02): only `append` and `set` available as ops. Anything requiring more must be escalated. The restriction is enforced by the `DossierEdit` schema, not just prompt wording.
- Productive-tension (1.7-04) and escalation (1.7-03) pathways: unchanged — emit flag + resolution with empty `edits` list.
- Block 4 worked examples (1.7-01): updated to show edit objects rather than dossier re-writes.

**Why 1.1-1.6 do NOT get an analogous split (reviewed 2026-04-22):** Pass 1.7's compose step is pure dict-assembly — zero cognitive work lost by moving to Python. Pass 1.1-1.6's merge is inherently semantic (cross-source dedupe, reconciliation of conflicting claims, identification of same-concept-different-wording across sources). An analogous split would require either (a) an extract-per-source phase feeding a merge phase — 4 LLM calls per chunk instead of 1, more cost without eliminating any judgment surface; or (b) purely-offline dedupe, which is not well-defined on free-text research sources. Arch-03's existing remedies for 1.1-1.6 preservation — permissive schemas + source-attribution fields + additive-merge prompt discipline — are the right shape for the cognitive work those chunks actually do. If Stage 1 under the split 1.7 still shows 1.1-1.6 dropping content, revisit per-chunk at that point; do not invert a working architecture preemptively.

**Files touched by the amendment:**
- `personas/run_pass_1_7.py` — full rewrite to three-stage shape.
- `personas/flows/shared/prompts/pass_1_7_coherence.md` — Block 5 now shows composed dossier (single block), Block 6 output shape is `CoherenceAuditResult`, Block 4 examples updated.
- `personas/schemas/merged_dossier.py` — unchanged (composition uses existing schema).

No prompt-scope regression: every check, every resolution category, every escalation pathway from §5.1–5.3 is preserved. The structural guard replaces the prompt-level guard against re-compression; both are now in force.

---

## 6. Pass 2–6 adjustments

Target: `personas/flows/shared/prompts/persona_pass_2_identity_boundaries.md` through `persona_pass_6_corpus.md` + user prompts + `run_persona_pipeline.py`.

### 6.1 Prompt adjustments per pass

**Pass 2 (Identity & Boundaries)**
- System prompt: add discipline — "Merged dossier under 1-arch-03 preserves richer research than card can hold. Your job is SELECTION + SYNTHESIS, not extraction. Use scholarly_context + analytical_context to inform card-field framing even when the content doesn't directly fit the field."
- Block 2 guardrails: add "For formative_experience: read all formative_candidates + their cross-references to commitments. Commit to ONE PRIMARY but reference 1-2 SUPPORTING inline per fix 2-03."
- Fix 2-01 (stale user prompt "9 fields"): update to "10 fields" + add voice_temporal_stance.
- Fix 2-02 (voice_temporal_stance REWRITE): deployment-configurable shape per user decision.
- max_tokens: 24000 → **32000** (accommodate richer input + 10 fields with richer content).

**Pass 3 (Intellectual Core)**
- System prompt: add "Constitution synthesis draws from full commitments[] list + scholarly_context per commitment. Well-documented voices have 20-40 commitments in merged; distill to constitution's 10-20 principles; preserve the operational specificity test (two-voice swap)."
- User prompt: add explicit reference to `scholarly_context` + `contested_readings` fields.
- max_tokens: 24000 → **32000**.

**Pass 4a (Voice)**
- System prompt: add "Under 1-arch-03, Pass 1.4 output includes analytical_context_voice with scholarly stylistic-reception + translator-tradition notes. Use for voice-signature authoring; apply reference-not-display discipline."
- User prompt: explicit reference to analytical_context + genre_specific_register.
- max_tokens: 24000 → **32000**.

**Pass 4b (Artifact)**
- Reads CT-summarized Pass 2+3+4a outputs (not merged_dossier directly). CT compression more important under 1-arch-03 since upstream is richer.
- Monitor: is CT ~500-token summary preserving enough voice signal for artifact synthesis? Phase-L-validated on current architecture. Under 1-arch-03, Pass 2/3/4a outputs are richer; CT compression is larger delta but also starts from richer base.
- max_tokens: 24000 → **24000** (unchanged; 4b output is artifact spec, not content-rich).
- **Forward-referenced concern:** Pass 4b/5 CT bottleneck (previously flagged in tracker). Under 1-arch-03, this concern becomes more acute (bigger gap between CT summary and underlying knowledge) but also less blocking (richer upstream → richer CT-preserved signal). Monitor in testing.

**Pass 5 (Engagement)**
- Same as 4b. Reads CT summaries.
- Phase L Gemini Pass 7a flagged Pass 5 register drift. Hypothesis: Pass 5 starves on thin CT summaries. Under 1-arch-03, richer Pass 2/3/4a → richer CT → less starvation.
- max_tokens: 24000 → **24000** (4 fields, not content-rich).

**Pass 6 (Corpus Curation)**
- Reads primary_texts + merged_dossier + prior CT summaries.
- Under 1-arch-03, Pass 1.6 passages preserved as verbatim text (1-arch-01 remains deferred). Pass 6 curation draws from richer passage set + scholarly_bibliographic_context.
- max_tokens: 24000 → **32000**.

### 6.2 max_tokens summary table

| Pass | Current | Proposed | Rationale |
|---|---|---|---|
| 2 Identity & Boundaries | 24000 | **32000** | Richer input; 10 fields |
| 3 Intellectual Core | 24000 | **32000** | Constitution from richer commitment pool |
| 4a Voice | 24000 | **32000** | Voice synthesis from analytical_context |
| 4b Artifact | 24000 | 24000 | CT-summary input; artifact spec output |
| 5 Engagement | 24000 | 24000 | CT-summary input; 4 fields |
| 6 Corpus Curation | 24000 | **32000** | Rich passage + scholarly context |

Cost delta per voice: 4 passes × ~30% token increase × ~$1.50 baseline = **+$1.80–3.00 per voice** (smaller than my earlier $20-40 estimate — most of the cost delta is in input tokens which are cheaper than output).

### 6.3 CT mechanism — unchanged structurally

`_ct_compress()` in `run_persona_pipeline.py:357-370` still uses Sonnet 4.6 + max_tokens=2048 + `persona_coherence_threading.md` template.

CT prompt fix (per Step 27 observation): reword "Preserve: ...the wound and its lesson..." to Boddice-aligned language per 1-arch-03. Lands alongside CT prompt review.

### 6.4 Pass 2-6 contract document

Produce `_workspace/planning/PASS_2-6_CONSUMES_MERGED_DOSSIER_CONTRACT.md` — short doc stating exactly what Pass 2-6 prompts should reference in merged_dossier (which fields, which containers). Helps future prompt-drift review.

---

## 7. Test plan

### 7.1 Dostoevsky Phase L fixture as ground truth

Reuse `projects/phase-l-dostoevsky/voices/fyodor_dostoevsky/01_research/` (Perplexity + Gemini + Claude DR 6 sections) as frozen input. Phase L validated Dostoevsky card is available as comparison baseline at `07_persona_card_assembled.json`.

**Test sequence:**

1. **Stage 1 — Merge-layer sanity:** Run new Pass 1.1-1.7 on Dostoevsky inputs. Verify:
   - All chunk outputs produce valid Pydantic under new schemas.
   - merged_dossier.json size: expected 300-400K (vs. current 162K).
   - Per-chunk preservation check: compute character-level diff of unique content between source sections and merged chunks. Target preservation rate: **≥85%** for §3/§4/§5 (current: 27-30%). If <85%, iterate on prompts.
   - Coherence_flags + coherence_resolutions: expect ≥3 each (real reconciliation activity).

2. **Stage 2 — Per-chunk qualitative review:** For each chunk, compare output to source sections. Verify:
   - DR §3 carnivalization analysis → merged analytical_context_reasoning.structural_patterns[]
   - DR §3 Menippean checklist → merged analytical_context_reasoning.structural_patterns[] or scholarly_debates[]
   - DR §3 scandal-scene instances → merged structural_patterns[] with multiple instances (was 1, should be 5)
   - DR §3 worked demonstrations → merged worked_demonstrations[] (3 entries)
   - DR §3 Holbein Basel → merged formative_candidates or life_scaffold scholarly_context
   - DR §3 Williams vs. Frank contrast → merged scholarly_debates[]

   For §4 VOICE and §5 BOUNDARIES: parallel qualitative checks per expected preservation.

3. **Stage 3 — Pass 2-6 synthesis:** Run Pass 2 through 6 on new merged_dossier. Produce new persona_card_assembled.json. Verify:
   - All card fields populate (no schema-validation failures).
   - Field content: richer than baseline card where applicable (e.g., character's formative-experience references multiple candidates; concept_lexicon preserves translation_tradition_notes; curated_corpus_passages includes translator-anchored passages).
   - Register discipline (first/second person) holds.
   - Boddice tags ([experiential_reconstruction] + [projection_warning]) preserved.
   - Pass 5 register (previously Gemini-flagged): improved by richer upstream? Measure.

4. **Stage 4 — Pass 7 validation:** Run Pass 7-pre + 7-anachronism + 7a + 7b + 7c on new card. Compare to baseline card's validation outputs. Verify no new regressions; look for improvements (fewer [experiential_reconstruction] flags if richer upstream preservation; fewer Pass 5 register issues).

5. **Stage 5 — Comparison decision:**
   - Card quality: new ≥ baseline on breadth (more distinct scholarly traditions represented, more named structural patterns, more worked demos referenced inline)?
   - Pass 5 register: new ≥ baseline (fewer Gemini-flagged issues)?
   - Cost: +$2-5 per voice acceptable vs. baseline's ~$20/voice Pass 1-6 total?
   - Wall-time: +5-15 min per voice acceptable vs. baseline's ~90 min?

### 7.2 Pass/fail decision

**PROCEED (merge arch-03 to main, start Phase N on new arch) if:**
- Merge-layer preservation rate ≥85% on §3/§4/§5
- New card equal or better than baseline on qualitative review
- No Pass 2-6 synthesis failures under new inputs
- No Pass 7 validation regressions
- Cost delta <$5/voice; wall-time delta <15 min/voice

**ITERATE (revise prompts/schemas on branch, retest) if:**
- Preservation rate 70-85%: prompt discipline needs refinement
- New card mixed qualitatively: specific field regressions traced to specific prompt/schema gaps

**ROLLBACK (abandon 1-arch-03) if:**
- Preservation rate <70% after 2 iterations (implies merge discipline is fundamentally hard)
- New card materially worse on qualitative review
- Pass 2-6 persistent synthesis failures

### 7.3 Test fixtures + instrumentation

**Fixture path:** `personas/tests/fixtures/phase_l_dostoevsky/` — copy Dostoevsky Phase L research inputs as frozen test fixture. Include baseline `07_persona_card_assembled.json` for comparison.

**Instrumentation script:** `personas/scripts/arch_03_preservation_audit.py` — computes per-section preservation rate (character overlap between source and merged chunk; unique-scholarly-name preservation; named-structural-pattern count). Run post-merge; output JSON audit file.

**Manual review checklist:** `_workspace/planning/ARCH_03_MANUAL_REVIEW_CHECKLIST.md` — per-chunk qualitative checks against DR §N content. Operator completes alongside auto-audit.

---

## 8. Implementation sequence

Sonnet-executable step-by-step. Each step has explicit entry criteria, actions, verification, and exit criteria.

### 8.1 Branch setup

**Step 1.** Open branch `arch-03-additive-merge` from current `main` (HEAD `c67cd73`).

```bash
cd "/Users/aienvironment/Desktop/AI Assembly/code"
git checkout -b arch-03-additive-merge
```

**Verification:** `git status` shows clean tree on new branch.

### 8.2 Schema changes (landing order matters)

**Step 2.** Update `personas/schemas/_conventions.py`.

**Actions:**
- No changes to frozen conventions.
- Verify `ContestedReading` model is exported from `_conventions` (was there but unused; now used by new schemas).
- Add any new shared models: `StructuralPattern`, `WorkedDemonstration`, `AnalyticalContext` (new file `_analytical.py`?).

**Decision:** new file `personas/schemas/_analytical.py` holds the new shared analytical-context models. Imported by pass_1_3, pass_1_4 as needed.

**Verification:** `personas/schemas/_entry.py` `generate_json_schemas()` runs; new files emit generated JSON schemas.

**Step 3.** Update `personas/schemas/pass_1_1.py`.

**Actions:**
- `LifeScaffold`: add `scholarly_context: str | None`, `contested_readings: list[ContestedReading]`; no field-removals.
- `PeriodPathos`: unchanged.
- Add `AnachronismEntry` model (optional; existing `anachronisms_to_avoid: list[str]` could stay as-is with prompt-level guidance for structure, or migrate to `list[AnachronismEntry]` — go with list[str] for backward-compat simplicity, elaborate in prompt).
- `FormativeCandidate`: add `scholarly_context`, `resonates_with_commitments`. Change `evidence_tag` default to remain `experiential_reconstruction`.

**Verification:**
- `Model.model_validate(old_chunk_output_from_phase_l)` succeeds (backward-compat on frozen Dostoevsky output).
- `Model.model_validate(new_test_fixture_with_additive_shape)` succeeds.

**Step 4.** Update `personas/schemas/pass_1_2.py`.

**Actions:**
- `Commitment`: add `scholarly_context: str | None`, `contested_readings: list[ContestedReading]`.
- `Concept`: add `translation_tradition_notes: str | None`.
- `Tension`: add `tension_type: Literal["productive", "contested", "unresolved"]`, `scholarly_context: str | None`.

**Verification:** same backward-compat pattern.

**Step 5.** Update `personas/schemas/pass_1_3.py`.

**Actions:**
- Add `analytical_context_reasoning: AnalyticalContext` top-level field in this chunk's output (or add to MergedDossier-level; see Step 8).
- `ReasoningStep`: add `scholarly_context: str | None`.
- `Textures`: add `scholarly_context: str | None`.

**Decision:** Add `analytical_context_reasoning` as top-level key in pass_1_3 output and in MergedDossier. Prompts direct Opus to populate.

**Step 6.** Update `personas/schemas/pass_1_4.py`.

**Actions:**
- `Move`: add `scholarly_context: str | None`, `structural_pattern_refs: list[str]`.
- `Register`: add `genre_specific_register: dict[str, str]`, `translator_tradition_notes: str | None`.
- `Vocabulary`: migrate `preferred_vocabulary: list[str]` to `list[VocabEntry]` with `term/gloss/loadbearing/translation_notes`. **Breaking change** — existing Dostoevsky merged_dossier has list[str]. Need migration or parallel-support.

**Decision:** Parallel-support for `preferred_vocabulary`: accept both `list[str]` (backward-compat) and `list[VocabEntry]`. Pydantic discriminated union. Deprecation plan: migrate existing cards in Phase N integration.

Actually — simpler: Pass 2-6 synthesizes to card from merged_dossier. Card's `preferred_vocabulary` field is list[str] per Card v2 spec. Pass 4a reads richer VocabEntry at merge level; flattens to list[str] at card level. No cascade breakage.

- Add top-level `analytical_context_voice: AnalyticalContext | None`.

**Step 7.** Update `personas/schemas/pass_1_5.py`.

**Actions:**
- `KnowledgeBoundary`: migrate exclusion lists from `list[str]` to `list[ExclusionEntry]`. Same parallel-support approach.
- `SensitiveTopic`: add `scholarly_reception: str | None`.
- `HardLimits`: migrate `prohibitions: list[str]` to `list[Prohibition]`. Same parallel-support.

**Step 8.** Update `personas/schemas/pass_1_6.py`.

**Actions:**
- `Works`: add `bibliographic_scholarly_context: str | None` at container level.
- `Passages`: add `translator_tradition_coverage: list[str]` at container level.
- Uncap `passages[]` count (currently prompt says 8-15; schema had no cap; prompt-guidance change).

**Step 9.** Update `personas/schemas/merged_dossier.py`.

**Actions:**
- Add `analytical_context_reasoning: AnalyticalContext` (from Pass 1.3).
- Add `analytical_context_voice: AnalyticalContext | None` (from Pass 1.4).
- Verify all other keys compose cleanly.
- Regenerate `personas/schemas/generated/*.schema.json`.

**Verification:** `_entry.generate_json_schemas()` succeeds. Generated schemas committed. `MergedDossier.model_json_schema()` is well-formed JSON.

### 8.3 Prompt rewrites

**Step 10.** Rewrite `pass_1_1_merge.md`.

**Actions:**
- Keep Blocks 1 (Role), 3 (Output Schema via Jinja-inlined schemas; now permissive containers), 5 (Input), 6 (Task).
- Replace Block 2 with additive-merge discipline per §4.1.
- Extend Block 4 worked examples: add Cleopatra (1.1-02), Scheherazade (closes 1.1-06). Total 5 examples.
- Apply 1.1-03 (drop voice_mode), 1.1-04 (period-vocabulary gradation), 1.1-05 (ContestedReading resolved via schema now accepting; prompt mentions it correctly), 1.1-06 (fictional null-discipline).

**Verification:** Render template with Dostoevsky voice_config → valid Jinja output → Pydantic-validated against new schema.

**Step 11.** Rewrite `pass_1_2_merge.md` similarly. Apply 1.2-02 (voice_mode load-bearing), 1.2-03 (Scheherazade example).

**Step 12.** Rewrite `pass_1_3_merge.md` (largest change). Major addition: analytical-context directive + Dostoevsky narratival worked example (1.3-02 lift-from-Phase-L). Apply 1.3-03 (period-vocabulary).

**Step 13.** Rewrite `pass_1_4_merge.md`. Apply 1.4-02 (complete Marley moves), 1.4-03 (Octopus example), 1.4-04 (voice_mode prior).

**Step 14.** Rewrite `pass_1_5_merge.md`. Apply 1.5-02 (Cleopatra hostile-source), 1.5-03 (fictional general_frame), 1.5-04 (voice_mode drop).

**Step 15.** Rewrite `pass_1_6_merge.md`. Apply 1.6-02 (Octopus), 1.6-03 (Scheherazade multi-translator), 1.6-04 (Marley reference_only_passages), 1.6-06 (voice_mode drop).

**Step 16.** Update `pass_1_7_coherence.md`. Add Block 4 worked examples (1.7-01), edit-scope (1.7-02), escalation pathway (1.7-03), productive-tension criteria (1.7-04). Add Check 8 (source attribution) + Check 9 (analytical context presence) per §5.2.

**Step 16a (landed 2026-04-22 per §5.5 amendment).** Split Pass 1.7 into offline compose + narrow LLM audit + Python edit apply. `personas/run_pass_1_7.py` fully rewritten; `pass_1_7_coherence.md` Block 5 replaced with composed-dossier block; Block 6 output shape now `CoherenceAuditResult` (flags + resolutions + edits[]). max_tokens drops from 100000 → 24000. §5.5 is authoritative; §5.4 is superseded historical context.

**Verification (Step 10-16 each):** template renders; Pydantic-validates fixture output (will do proper validation in Stage 1 test below).

### 8.4 Pass 2-6 adjustments

**Step 17.** Update `persona_pass_2_identity_boundaries.md` + `persona_pass_2_user.md`.

**Actions:**
- Apply 2-01 (user prompt "10 fields" + add voice_temporal_stance to list).
- Apply 2-02 per user decision on voice_temporal_stance (REWRITE or KEEP or DELETE). **Awaiting user decision before this step — block.**
- Apply 2-03 (formative-candidate commit-to-ONE reword).
- Add selection-discipline line per §6.1.
- Bump `max_tokens` to 32000 in `run_persona_pipeline.py:375-379` (via `_claude_pass()` kwarg or wrapper override).

**Step 18.** Update `persona_pass_3_intellectual_core.md` + user prompt.

**Actions:**
- Add reference to `scholarly_context` + `contested_readings` fields in user prompt directive.
- Bump max_tokens to 32000.

**Step 19.** Update `persona_pass_4a_voice.md` + user prompt.

**Actions:**
- Add reference to `analytical_context_voice` + `genre_specific_register` + `translator_tradition_notes`.
- Bump max_tokens to 32000.

**Step 20.** Update `persona_pass_4b_artifact.md`, `persona_pass_5_engagement.md`.

**Actions:** Minor — CT-based, no merged_dossier direct read. Verify no prompt references to schema fields that changed.

**Step 21.** Update `persona_pass_6_corpus.md` + user prompt.

**Actions:**
- Add reference to `bibliographic_scholarly_context` + `translator_tradition_coverage`.
- Bump max_tokens to 32000.

**Step 22.** Update `persona_coherence_threading.md`.

**Actions:**
- Apply Step 27 forward-reference fix: reword "Preserve: ...the wound and its lesson..." to Boddice-aligned: "Preserve: key identity facts, the formative emotional community + apparatus + engagement (Boddice §14 3-part), the 3 most important constitutional principles, the core reasoning mode, and the dominant voice register."

**Verification:** all prompts render with Dostoevsky fixture; Pydantic validates outputs once test runs.

### 8.5 Test run — Stage 1 merge-layer

**Step 23.** Run Pass 1.1-1.7 on Dostoevsky fixture.

```bash
cd personas
venv/bin/python run_pass_1_all.py "Fyodor Dostoevsky" --project "../../projects/phase-l-dostoevsky"
```

**Verification:**
- All 7 passes complete without Pydantic failures.
- merged_dossier.json size: 300-400K (target).
- Per-chunk outputs size larger than baseline (compare per-file sizes).
- Run `arch_03_preservation_audit.py` → preservation rate report. Target ≥85% on §3/§4/§5.

**Decision gate:**
- If preservation rate <70%: iterate on prompt discipline (Steps 12/13/14 most likely culprits). Return to Step 10.
- If 70-85%: identify specific content-loss cases; targeted prompt refinement; return to relevant step.
- If ≥85%: proceed to Step 24.

### 8.6 Test run — Stage 2 Pass 2-6 synthesis

**Step 24.** Run Pass 2-6 + Pass 7 validation on new merged_dossier.

```bash
cd personas
venv/bin/python run_persona_pipeline.py "Fyodor Dostoevsky" --project "../../projects/phase-l-dostoevsky"
# (May need cache clearing: rm -r voices/fyodor_dostoevsky/04_generation/ voices/fyodor_dostoevsky/05_validation/ voices/fyodor_dostoevsky/06_derive/)
```

**Verification:**
- Pass 2-6 complete without failures.
- Pass 7-pre citation verification: pass rate ≥ baseline.
- Pass 7-anachronism: flag count ≤ baseline.
- Pass 7a cross-model: register check PASS (fixing baseline's ISSUE).
- Pass 7b smoke test chains: qualitative assessment of voice distinctiveness.
- Pass 7c: banned_language / banned_modes / projection_warnings counts reasonable.

**Decision gate:**
- If new card passes 7-pre + 7-anachronism + 7a better than baseline: proceed.
- If regressions: diagnose. Pass 2-6 prompts may need further tuning.

### 8.7 Test run — Stage 3 manual review

**Step 25.** Manual qualitative review of new Dostoevsky card vs. baseline.

**Checklist (`ARCH_03_MANUAL_REVIEW_CHECKLIST.md`):**
- Does `character` reference multiple formative candidates (not just Semenovsky-execution)?
- Does `constitution` preserve 17+ commitments (currently baseline; may grow to 20-25)?
- Does `reasoning_method.steps` reference or incorporate carnivalization, scandal-scene instances, worked-demonstration material from merged analytical_context?
- Does `curated_corpus_passages` draw from richer translator-tradition-noted corpus?
- Does `topics_requiring_care` include additional scholarly-reception framings?
- Is `voice_temporal_stance` field compliant with user's 2-02 decision?
- Does card feel richer on qualitative read-aloud test per Card v2 register principle?

**Decision gate:**
- If card is qualitatively richer + empirically preserves more: PROCEED to merge.
- If comparable: CONTEXT-SPECIFIC — is the extra cost worth comparable quality? Probably YES (preservation is defensive investment for voices 2-12).
- If worse: ROLLBACK. Diagnose.

### 8.8 Merge-to-main decision

**Step 26.** Merge `arch-03-additive-merge` → `main`.

```bash
git checkout main
git merge arch-03-additive-merge
git push
```

**Pre-merge checks:**
- 128-test suite passes (personas/tests).
- 29-test suite passes (runtime/tests).
- Stale-ref greps clean (no "runs/<slug>" in source; no old schema references).
- OPEN_ITEMS.md updated with 1-arch-03 LANDED entry.
- Tracker updated with 1-arch-03 APPLIED status.

**Post-merge:**
- Phase N proceeds on new architecture.
- Voices 2-12 build on preserved-research foundation.
- Monitor SRI-2 empirical data across voices 2-12.

### 8.9 Rollback plan

If Step 25 or 26 fails decisively:

```bash
git checkout main
# Branch preserved for post-mortem analysis
git branch -D arch-03-additive-merge  # only after confirming no value to preserve
```

Preserve branch for 30 days minimum post-decision in case diagnosis later reveals fixable issue.

**What rollback means for tracker:**
- Wave 1 fixes: unaffected (pre-merge; apply regardless).
- Wave 2 fixes: unaffected.
- Wave 3 fixes: current-architecture fixes (Gemini-filtering, worked examples, etc.) remain APPROVED-PROPOSED; implement under current architecture.
- 1-arch-01, 1-arch-02: remain as deferred-post-Phase-N proposals.
- Pass 2-6 fixes (2-01, 2-02, 2-03): apply under current architecture.

---

## 9. Fix triage under 1-arch-03

**Super-granular status flags for every Wave 1–3 + Step 27 fix in the tracker.**

Status codes:
- **SURVIVES** — unchanged under 1-arch-03; implement as specified in tracker
- **OBSOLETE** — resolved by architectural change; no separate implementation needed
- **RESHAPED** — core concern remains valid but specific fix needs restatement under new architecture
- **ABSORBED** — folded into 1-arch-03 implementation (not a separate fix)
- **SUPERSEDES** — this fix supersedes another tracker item

### 9.1 Wave 1 — Phase 0 + 0.5 fixes (53 fixes across Steps 1-17)

**All Wave 1 fixes SURVIVE 1-arch-03.** Research layer unchanged structurally. Fixes apply as-is.

| Fix ID range | Count | Status |
|---|---|---|
| 0a-01 through 0a-04 | 4 | **SURVIVES** — Pass 0a voice_config |
| 1a-01 through 1a-14 | 14 | **SURVIVES** — Pass 1a Perplexity family |
| 1b-01 (REJECTED) + 1b-02 through 1b-14 | 13 | **SURVIVES** — Pass 1b Gemini family; 1b-01 remains REJECTED |
| 0b-01 through 0b-23 | 23 | **SURVIVES** — Pass 0b render + tailor family |
| 1a-XREF1-6, 1b-XREF1-2, 0b-XREF1-2 | Cross-template observations | **SURVIVES** as implementation-pass coordination notes |

Wave 1 fixes can be implemented **before, during, or after 1-arch-03**. Scheduling flexibility preserved. Recommend landing Wave 1 coordinated patches first (they're smaller scope); 1-arch-03 on branch concurrently.

### 9.2 Wave 2 — Pass 1c + 1d fixes (12 fixes)

**All Wave 2 fixes SURVIVE.** Pass 1c and Pass 1d are structurally unchanged.

| Fix ID range | Count | Status |
|---|---|---|
| 1c-01 through 1c-06 | 6 | **SURVIVES** — Pass 1c fetch mechanics |
| 1d-01 through 1d-05 | 5 | **SURVIVES** — Pass 1d excerpt selection |
| 1d-06 (HIGH architectural) | 1 | **SURVIVES** — fuzzy-match primary-path; composes cleanly with 1-arch-03; remains post-Phase-N revisit |
| 1-arch-01 (HIGH architectural) | 1 | **SURVIVES** — curated_corpus_passages routing; composes cleanly with 1-arch-03; remains post-Phase-N revisit |

### 9.3 Wave 3 — Pass 1.1–1.7 merge fixes (30 fixes + SRIs + architectural proposals)

**Mixed triage.** This is where 1-arch-03 supersedes or reshapes most items.

#### 9.3.1 Step 20 — Pass 1.1 fixes

| ID | Severity | Original Fix | Status under 1-arch-03 | Rationale |
|---|---|---|---|---|
| 1.1-01 | MEDIUM | Add Gemini-filtering directive in Block 2 Reconciliation rule | **OBSOLETE** | Under additive merge, Gemini is full-contributor-not-filtered. Lane-naming concern (SRI-1) dissolves. |
| 1.1-02 | LOW | Add Cleopatra hostile-source worked example | **ABSORBED** into 1-arch-03 | Worked example added to new Block 4 per §4.2.1. |
| 1.1-03 | LOW | Drop `voice_mode` from Block 5 (dead variable) | **SURVIVES** | Voice_mode disposition policy independent of schema architecture. Apply as specified. |
| 1.1-04 | LOW | Reword pre-1820 period-vocabulary cutoff to gradate | **SURVIVES** | Prompt-wording fix independent of architecture. Coordinated patch across 1.1/1.2/1.3. |
| 1.1-05 | LOW | ContestedReading prompt-schema mismatch (phantom reference) | **OBSOLETE** | Under 1-arch-03, ContestedReading is actually used (LifeScaffold.contested_readings + Commitment.contested_readings). Schema-prompt mismatch resolves. |
| 1.1-06 | LOW | Fictional-voice null-discipline rule gap | **ABSORBED** into 1-arch-03 | Fictional null-discipline spelled out in new Block 3/5 per §4.2.1. |

#### 9.3.2 Step 21 — Pass 1.2 fixes

| ID | Severity | Original Fix | Status under 1-arch-03 | Rationale |
|---|---|---|---|---|
| 1.2-01 | MEDIUM | Add Gemini-filtering directive | **OBSOLETE** | Per 1.1-01 rationale. |
| 1.2-02 | LOW | Make voice_mode load-bearing in Block 2 | **SURVIVES** | Voice_mode role at commitment-extraction independent of schema architecture. |
| 1.2-03 | LOW | Add Scheherazade fictional worked example | **ABSORBED** into 1-arch-03 | Worked example added per §4.2.2. |

#### 9.3.3 Step 22 — Pass 1.3 fixes

| ID | Severity | Original Fix | Status under 1-arch-03 | Rationale |
|---|---|---|---|---|
| 1.3-01 | MEDIUM | Add Gemini-filtering directive | **OBSOLETE** | Per 1.1-01 rationale. |
| 1.3-02 | LOW | Add Dostoevsky narratival worked example (lift-from-Phase-L) | **ABSORBED** into 1-arch-03 | The Dostoevsky example becomes richest worked example in §4.2.3 because it demonstrates analytical_context (structural_patterns + worked_demonstrations) — precisely the 1-arch-03 contribution. |
| 1.3-03 | LOW | Period-vocabulary gradation coordination | **SURVIVES** | Coordinated patch with 1.1-04 + 1.2-03 (if applicable to 1.2). Independent of schema. |

#### 9.3.4 Step 23 — Pass 1.4 fixes

| ID | Severity | Original Fix | Status under 1-arch-03 | Rationale |
|---|---|---|---|---|
| 1.4-01 | MEDIUM | Add Gemini-filtering directive | **OBSOLETE** | Per 1.1-01 rationale. |
| 1.4-02 | LOW | Complete Marley worked example (missing moves) | **ABSORBED** into 1-arch-03 | Marley example completion per §4.2.4. |
| 1.4-03 | LOW | Add Octopus non-human organism worked example | **ABSORBED** into 1-arch-03 | Octopus example added per §4.2.4. |
| 1.4-04 | LOW | Add voice_mode prior in Block 2 | **SURVIVES** | Voice_mode load-bearing at register level independent of schema. |

#### 9.3.5 Step 24 — Pass 1.5 fixes

| ID | Severity | Original Fix | Status under 1-arch-03 | Rationale |
|---|---|---|---|---|
| 1.5-01 | MEDIUM | Add Gemini-filtering directive | **OBSOLETE** | Per 1.1-01 rationale. |
| 1.5-02 | LOW | Add Cleopatra hostile-source worked example | **ABSORBED** into 1-arch-03 | Example added per §4.2.5. |
| 1.5-03 | LOW | Extend Block 2 general_frame rule to fictional voices | **SURVIVES** | Prompt-wording fix independent of schema. |
| 1.5-04 | LOW | Drop voice_mode from Block 5 | **SURVIVES** | Voice_mode disposition independent of schema. |

#### 9.3.6 Step 25 — Pass 1.6 fixes

| ID | Severity | Original Fix | Status under 1-arch-03 | Rationale |
|---|---|---|---|---|
| 1.6-01 | MEDIUM | Add Gemini-filtering directive | **OBSOLETE** | Per 1.1-01 rationale. |
| 1.6-02 | LOW | Add Octopus non-human organism worked example | **ABSORBED** into 1-arch-03 | Example added per §4.2.6. |
| 1.6-03 | LOW | Add Scheherazade fictional multi-translator worked example | **ABSORBED** into 1-arch-03 | Example added per §4.2.6. |
| 1.6-04 | LOW | Extend Marley example with reference_only_passages private tier | **SURVIVES** | Private-tier demonstration independent of schema; Marley example completion. |
| 1.6-05 | LOW | translation_anchor purpose tag demonstration | **RESOLVED-VIA-1.6-03** | Already resolved; unchanged under 1-arch-03. |
| 1.6-06 | LOW | Drop voice_mode from Block 5 | **SURVIVES** | Voice_mode disposition independent of schema. |

#### 9.3.7 Step 26 — Pass 1.7 fixes

| ID | Severity | Original Fix | Status under 1-arch-03 | Rationale |
|---|---|---|---|---|
| 1.7-01 | LOW | Add BLOCK 4 worked examples | **SURVIVES** | Pattern-break repair independent of schema; implemented per §5.3. |
| 1.7-02 | LOW | Edit-scope discipline in Block 3 resolve-by-edit | **SURVIVES** | Per §5.3. |
| 1.7-03 | LOW | Escalation downstream pathway documentation | **SURVIVES** | Per §5.3. |
| 1.7-04 | LOW | Productive-tension criteria | **SURVIVES** | Per §5.3. |

#### 9.3.8 Standing review items (SRI)

| Item | Original concern | Status under 1-arch-03 | Rationale |
|---|---|---|---|
| SRI-1 Gemini-noise-leakage watch | Per-chunk Gemini filtering burden | **OBSOLETE** | Additive merge accepts full Gemini content per chunk; no filtering-burden concept. |
| SRI-2 Corpus utilisation depth | Is merge extracting breadth or narrowing? | **ABSORBED** into 1-arch-03 | The whole point of 1-arch-03 is corpus-preservation-at-merge. SRI-2 becomes a preservation-rate metric (target ≥85%) tested empirically in Stage 1 per §7.1. |

#### 9.3.9 Architectural proposals

| Proposal | Status | Rationale |
|---|---|---|
| 1-arch-01 (curated_corpus_passages from Pass 1d) | **SURVIVES** | Independent of 1-arch-03 architecture. Composes cleanly. Remains post-Phase-N deferred per original plan. |
| 1-arch-02 (Gemini re-route: sectioned-per-chunk OR Gemini-only-at-1.7) | **SUPERSEDED by 1-arch-03** | The underlying concern (Gemini's per-chunk role is wrong-lane) dissolves under additive merge — Gemini is full-contributor alongside Perplexity + DR, no filtering burden. Mark 1-arch-02 as RESOLVED-VIA-1-ARCH-03. |
| **1-arch-03 (THIS PLAN)** | **PROPOSED — this document** | HIGH architectural; ~2-3 days implementation; pre-Phase-N recommended. |

### 9.4 Step 27 — Pass 2 fixes

| ID | Severity | Original Fix | Status under 1-arch-03 | Rationale |
|---|---|---|---|---|
| 2-01 | MEDIUM | Stale user prompt — "9 fields" → "10 fields" + add voice_temporal_stance | **SURVIVES** | Drift bug independent of architecture. Apply regardless. |
| 2-02 | MEDIUM · NEEDS-DECISION | voice_temporal_stance keep/rewrite/delete | **SURVIVES** | Decision-gate independent of architecture. User decision required. Apply per user decision in Step 17. |
| 2-03 | MEDIUM | Formative-candidate commit-to-ONE anchor-concentration reword | **RESHAPED under 1-arch-03** | Underlying concern (Pass 2 commit-to-ONE drops supporting candidates) remains valid. Under 1-arch-03, merged_dossier preserves full formative_candidates list + `resonates_with_commitments` cross-references; Pass 2 has richer context for primary-choice decision. Fix wording adjusts: "Use merged_dossier's full formative_candidates list (now preserved additively) + each candidate's `resonates_with_commitments` cross-refs. Commit to ONE PRIMARY for narrative coherence. In `formative_emotional_community` and `engagement_it_drives`, explicitly reference 1-2 SUPPORTING formative candidates inline." |
| 2-04 | LOW (monitor) | max_tokens=24000 at Pass 2 | **SUPERSEDED by 1-arch-03** | 1-arch-03 bumps Pass 2 max_tokens to 32000 per §6.2. Monitor becomes implementation. |

### 9.5 Forward-references registry

| Forward-ref | Original concern | Status under 1-arch-03 |
|---|---|---|
| Zosima-overanchoring at Pass 2 (commits-to-one) | Pass 1.1 surfaces 2-5 candidates; Pass 2 commits to one; supporting candidates lost | **RESHAPED** — 1-arch-03 preserves full candidates list + cross-references; 2-03 fix addresses commit-to-ONE reframing; risk reduced but not eliminated. Re-verify at Pass 2 review on new architecture. |
| Zosima-overanchoring at commitment-selection | Pass 2 constitution selects 10-20 from pool; pool may narrow at 1.2 | **PARTIALLY RESOLVED by 1-arch-03** — 1.2 now preserves 20-40+ commitments; Pass 3 selects 10-20 for constitution from full pool. Compression at Pass 3, not 1.2. |
| `coherence_flags[]` downstream use | Does Pass 2-6 read coherence_flags? | **UNCHANGED** — still forward-referenced for Wave 4 re-examination under new architecture. Expectation: Pass 2-6 should reference flags in user prompts. |
| Merged-dossier size vs Pass 2-6 consumption | Is merged the right size for consumption? | **RESHAPED** — under 1-arch-03, merged grows to 300-400K. Pass 2-6 max_tokens bumped. Re-evaluate consumption at Wave 4 on new architecture. |
| `voice_temporal_stance` keep/rewrite/delete decision | Wave 3/4 boundary decision | **UNCHANGED** — 2-02 fix; user decision required. |
| Reference-not-display boundary at Pass 4a | Does Pass 4a respect 1.4's reference-not-display directive? | **UNCHANGED** — forward-reference for Pass 4a review on new architecture. |
| 1.4's guardrail-level voice-type awareness as meta-pattern | Worth lifting back to 1.1/1.2/1.3 | **ABSORBED** into 1-arch-03 per §4.2 (guardrail-level voice-type awareness applied across all chunks). |
| Pass 1.5 → Pass 7c handoff drift | hard_limits vs banned_language drift risk | **UNCHANGED** — forward-reference for Pass 7c review. |
| Voice_mode cross-chunk disposition policy (1.1-1.5 mapped) | Dropped/load-bearing per chunk | **ABSORBED** into 1-arch-03 — policy applied per §4.2 (1.4-04 + 1.1-03 + 1.5-04 + 1.6-06 all fold in). |
| CT prompt Boddice-deprecated language ("wound and lesson") | v3.10 language surviving in CT | **RESOLVED** via §6.3 — CT prompt fix lands with 1-arch-03 Pass 2-6 updates. |
| Pass 1.7 coherence prompt depth | Does 1.7 have enough teeth? | **ABSORBED** into 1-arch-03 per §5.1-5.3 (Check 8 + 9 added; edit-scope + escalation + productive-tension criteria tightened). |
| Card-size question (114KB Dostoevsky) | Right allocation? | **UNCHANGED** — Wave 5 concern; deferred. |
| scholarly_support_score calibration | Pass 1.1 candidate ranking | **RESHAPED** — under 1-arch-03 richer candidates, calibration matters more for Pass 2's primary choice. Re-evaluate at Step 20 re-review. |
| unique_to_this_voice flag Pass 7 consumption | Does Pass 7 actually read? | **UNCHANGED** — Wave 5 concern; verify at Pass 7a review. |
| Pass 2 revision-loop behavior on Pass 7a escalation | `_critique_suffix("2")` behavior | **UNCHANGED** — Wave 5 concern; independent of architecture. |

---

## 10. Dependencies + interactions

### 10.1 1-arch-01 composition

1-arch-01 (curated_corpus_passages from Pass 1d fuzzy-match) composes cleanly with 1-arch-03. Sequence:

1. 1-arch-03 lands first (pre-Phase-N). Pass 1.6 produces rich `passages[]` with verbatim text (current shape, expanded).
2. Phase N voices 2-12 build on 1-arch-03 architecture.
3. Post-Phase-N: review all 12 cards. If curated_corpus_passages text is ceiling-bound by research-source quotes (the 1-arch-01 concern), implement 1-arch-01 then.

1-arch-01 requires 1d-06 (Pass 1d fuzzy-match) which also depends on 1-arch-03 preserving richer Pass 1.6 passage metadata. Clean compositional order: 1-arch-03 → 1d-06 → 1-arch-01.

### 10.2 1-arch-02 supersession

1-arch-02 (Gemini re-route) is fully superseded by 1-arch-03. Mark in tracker as **RESOLVED-VIA-1-ARCH-03**. No separate implementation needed.

### 10.3 Wave 1 + Wave 2 fix timing

Three options:

**Option A:** Wave 1 + Wave 2 fixes first on `main` (coordinated patches, ~1-2 days), then 1-arch-03 on branch.
**Option B:** 1-arch-03 on branch immediately; Wave 1 + Wave 2 lands post-merge.
**Option C:** Parallel — Wave 1 + Wave 2 on `main`; 1-arch-03 on branch; rebase branch when main updates.

Recommend **Option A**. Wave 1 + Wave 2 fixes are high-confidence discrete patches; land them first. 1-arch-03 branch starts from updated main; no rebase conflicts on research-layer + 1c/1d files. Reduces implementation risk.

### 10.4 Voice Pipeline Step 1/2 consumers

**Not in scope** per user confirmation. Voice Pipeline consumes persona_card_assembled.json, not merged_dossier.json. Architectural change stops at card boundary.

If 2-02 voice_temporal_stance rewrite includes deployment-configurable sub-fields (default + anchored_override), Voice Pipeline Step 1/2 will need to respect the override flag per deployment mode. That's a Voice Pipeline implementation detail, tracked in REBUILD_PLAN / Voice Pipeline workstream. Not blocking 1-arch-03.

---

## 11. Out of scope

- **Runtime Voice Pipeline** — consumes card, not merged_dossier. Architectural change stops at card.
- **Post-1.7 passes** — Pass 7 validation family, Derive — unchanged. Modest Pass 2-6 tuning per §6 is the only downstream adjustment.
- **1-arch-01** — curated_corpus_passages routing — remains deferred post-Phase-N. Composes cleanly with 1-arch-03.
- **Schema migration of existing Dostoevsky card** — the Phase L Dostoevsky card stays as-is (baseline for comparison). Not re-migrating.
- **Runtime side (runtime/)** — not affected.

---

## 12. Cost + quality estimate

### 12.1 Per-voice cost delta

| Pass | Current cost (est) | 1-arch-03 cost (est) | Delta |
|---|---|---|---|
| 1.1-1.6 merge chunks | ~$6-12 | ~$8-15 | +$2-3 |
| 1.7 coherence | ~$3-5 | ~$5-8 | +$2-3 |
| 2-6 synthesis | ~$5-8 | ~$7-11 | +$2-3 |
| Pass 7 validation | unchanged | unchanged | 0 |
| **Total per voice** | **~$14-25** | **~$20-34** | **+$6-9** |

Per 12 voices: +$72-108. Small fraction of total pipeline cost.

(Earlier estimate of +$20-40/voice was high; recalibrated based on input-vs-output token cost asymmetry — bigger inputs are cheaper than bigger outputs.)

### 12.2 Wall-time delta

- Merge chunks: +30-60s per chunk × 6 chunks parallel (max_workers=3) = ~+2-3 min
- Pass 1.7: +60-90s (bigger input + output)
- Pass 2-6: +30-60s per pass × 5 passes = ~+2-5 min
- **Total per voice: +5-10 min wall-time** (vs. current ~90 min/voice)

### 12.3 Implementation effort

| Task | Effort |
|---|---|
| Schema redesign (Steps 2-9) | 1 day |
| Prompt rewrites (Steps 10-16) | 1 day |
| Pass 2-6 adjustments (Steps 17-22) | 4 hours |
| Test runs + iteration (Steps 23-25) | 4-8 hours |
| Merge + verification (Step 26) | 2 hours |
| **Total** | **~2-3 days focused work** |

Plus: Sonnet can execute most of this with this plan document as guide. Manual operator review at Stages 2 and 3 (1-2 hours per stage).

### 12.4 Quality hypothesis

**Primary quality claim:** 1-arch-03 preserves 60-70% of Claude DR §3/§4/§5 content currently lost. This content informs downstream Pass 2-6 synthesis, particularly:

- **Pass 3 constitution**: richer scholarly-context per commitment preserves interpretive-tradition breadth (Frank vs. Bakhtin vs. Williams vs. Kasatkina — currently collapsed to one tradition at merge).
- **Pass 4a voice**: richer `analytical_context_voice` + `genre_specific_register` + `translator_tradition_notes` informs voice-authoring with full stylistic-reception material.
- **Pass 5 engagement**: previously starved of voice signal via CT bottleneck; under 1-arch-03, richer Pass 2/3/4a → richer CT → less starvation. Gemini-flagged Pass 5 register drift hypothesized to resolve.
- **Pass 6 corpus curation**: richer passage metadata + bibliographic_scholarly_context informs curated_corpus_passages selection.

**Secondary claim:** card quality on register + anti-flattening + scholarly-breadth axes measurably improves. Empirically testable on Dostoevsky comparison (Stage 3).

**Tertiary claim (defensive):** even if card quality is flat, the architectural preservation of research investment is itself valuable. Voices 2-12 DR sessions ($30-60 × 6 × 11 = $2-4K of operator labor) don't get silently discarded by merge layer. Defensive investment.

---

## 13. Rollback plan

Detailed rollback triggers and procedures per §8.9. Summary:

**Trigger criteria for rollback:**
- Merge-layer preservation rate <70% after 2 iteration passes
- Pass 2-6 systematic failures
- Card qualitative regression on Dostoevsky comparison
- Cost delta >$15/voice or wall-time delta >30 min/voice (hard business ceilings)

**Rollback procedure:**
- Abandon `arch-03-additive-merge` branch
- Preserve branch 30 days post-decision for post-mortem diagnosis
- Apply Wave 3 tracker fixes to current-architecture prompts (defer 1-arch-03 absorbed fixes via reclassifying them to current-architecture variants)
- Continue Phase N on current architecture

**Post-rollback tracker updates:**
- 1-arch-03: status REJECTED-AFTER-EMPIRICAL-TEST
- Wave 3 fixes marked ABSORBED: reclassify to SURVIVES (under current architecture)
- SRI-1: reactivate as live concern
- 1-arch-02: reactivate as deferred proposal

---

## 14. Locked decisions (closed 2026-04-22)

**Q1. Stage-3 manual review — who decides?** **LOCKED** — operator (user) reviews. `ARCH_03_MANUAL_REVIEW_CHECKLIST.md` drafted by Sonnet during implementation; operator signs off before proceeding past Stage 3.

**Q2. Existing Dostoevsky card migration?** **LOCKED** — Phase L Dostoevsky card stays as baseline at `projects/phase-l-dostoevsky/voices/fyodor_dostoevsky/07_persona_card_assembled.json`. Not re-migrating. Stage 3 comparison uses baseline vs. new-architecture-generated card.

**Q3. `voice_temporal_stance` decision (fix 2-02).** **LOCKED — REWRITE.**

Field becomes deployment-configurable with two sub-fields:
- `voice_temporal_stance.default` — **fluid-across-time framing** appropriate for Voice Pipeline Step 2 artifact generation per Athens brief "impossible participants take the floor while you sleep." Voice speaks from its own world to the reader's; `translation_protocol` handles the bridge. When recalling events, count from the present of the voice's world; do not attempt to speak from the reader's time.
- `voice_temporal_stance.anchored_override` — **optional death-threshold (or period-specific) anchor** for chat/project deployments that need the drift-prevention the Dostoevsky chat-test exposed. Preserves the current Phase-M content (3-paragraph anchor to 9 Feb 1881 for Dostoevsky) as the override content.

Runtime Voice Pipeline Step 1/2 assembly respects the override flag per deployment mode: Voice Pipeline = use default; chat/project = use anchored_override if present, else default.

Schema change:
```python
class VoiceTemporalStance(BaseModel):
    default: str  # Fluid-across-time; required
    anchored_override: str | None = None  # Optional deployment-specific anchor
```

Pass 2 prompt spec (Block 3) updated accordingly: produces both sub-fields; default is mandatory per §14 Boddice-shape discipline; anchored_override is mandatory for historical human voices with death-threshold (Dostoevsky, Plato, Cleopatra, etc.) and omitted for non-human/fictional (Octopus, Whanganui, Scheherazade where "fluid" is the only coherent stance).

This lands during Step 17 of the implementation sequence.

**Q4. 128-test suite coverage.** **LOCKED** — minimum test update for 1-arch-03 is schema-shape tests + render smoke tests. End-to-end integration test with mocked LLMs remains Phase L follow-up (separate workstream, not in 1-arch-03 scope).

**Q5. Preservation-audit metric.** **LOCKED** — three complementary metrics computed by `arch_03_preservation_audit.py`:
- **Character overlap**: unique substrings from source found in merged / total source chars. Target ≥85% on §3/§4/§5.
- **Scholarly-citation preservation**: count of citations in source appearing in merged. Target 100%.
- **Named-structural-pattern preservation**: for §3, count of named patterns preserved as `StructuralPattern` entries (scandal-scene, carnivalization, crowning/decrowning, threshold-chronotope, sideshadowing, confession-under-pressure). Target 100%.

Audit script outputs JSON report for operator review at Stage 1.

---

## 15. Implementation scope + sequencing (locked)

**Scope: comprehensive single-session implementation** per user decision 2026-04-22:

- **Wave 1 fixes** (53 fixes, research layer) — SURVIVES; apply
- **Wave 2 fixes** (12 fixes, Pass 1c + 1d) — SURVIVES; apply (including 1d-06 fuzzy-match HIGH architectural, or defer per user call at implementation start)
- **Wave 3 fixes** — triaged per §9:
  - 8 OBSOLETE (skip; resolved by arch change)
  - 9 ABSORBED (fold into arch changes)
  - 13 SURVIVES (apply independently alongside arch)
  - 1 RESHAPED (2-03 rewording under new arch)
- **1-arch-03 architectural changes** (core of this plan) — Pass 1.1-1.7 schemas + prompts
- **Pass 2-6 downstream tuning** — prompt updates + max_tokens bumps + CT Boddice-align

All in one implementation session on branch `arch-03-additive-merge` from current `main` (HEAD `94672c5`). Estimated 3-4 days focused work.

**Sequencing recommendation (update from plan §10.3 Option A):** single-session over split-session. Rationale: end-to-end testing on Dostoevsky fixture requires all layers be at same architectural state. Cleaner to test whole pipeline once rather than test research-layer changes separately then test merge-layer changes.

**Rerun verification** starts at Pass 1.1 (research layer is frozen fixture from Phase L — not re-run). Exercises Pass 1.1-1.7 on new prompts/schemas + Pass 2-6 under new tuning + Pass 7 validation. Dostoevsky Phase L card stays as baseline for Stage 3 comparison.

**Wave 4 review resumption** happens AFTER 1-arch-03 merges to `main`. Pick up at Step 27 (Pass 2) RE-DONE under new architecture; original Step 27 block in tracker `c67cd73` commit is scrapped (user-approved collateral loss; Pass 2 prompt shape differs post-arch-03).

**Branch-merge authority.** **LOCKED** — user-only. Sonnet executes Steps 1-25 + reports at Stages 1/2/3 gates; user reviews + approves merge-to-main per Step 26.

---

## 16. Sonnet handoff specification

**Entry criteria:** User has locked all 5 decisions in §14 + sequencing in §15. Plan doc + tracker committed to `main` at HEAD `94672c5`. Tree clean.

**Sonnet session prompt template** (user copy-pastes to Sonnet session):

```
You are executing the 1-arch-03 Additive Merge Architecture implementation
in the AI Assembly project. This is a comprehensive pipeline refactor:
research-layer fixes (Wave 1) + post-merge primary-text fixes (Wave 2) +
merge-layer redesign (1-arch-03 core) + downstream Pass 2-6 tuning.

ORIENTATION READING (in order):

1. `_workspace/planning/ARCH_03_ADDITIVE_MERGE_PLAN.md` — the plan. Read
   §1 rationale through §16 handoff. Your execution follows §8 Implementation
   sequence verbatim.

2. `_workspace/planning/PIPELINE_REVIEW_FIXES.md` — fix tracker. Reference
   for specific fix IDs; the plan's §9 triage classifies every fix.

3. `code/CLAUDE.md` — repo conventions, venv rules, orientation.

4. `_workspace/planning/OPEN_ITEMS.md` — project state anchor.

5. `_workspace/planning/REBUILD_PLAN.md` — PB#1-9 locked decisions (do
   NOT re-litigate).

BRANCH SETUP:

Start on `main` at HEAD `94672c5` (verify). Open branch:
  `git checkout -b arch-03-additive-merge`

EXECUTION:

Follow §8 Implementation sequence Steps 1-25 in order. Do NOT merge to main
at Step 26 — operator review required first.

CHECKPOINT GATES:

- After Step 9 (schemas done): commit "schemas: permissive containers
  for 1-arch-03" to branch. Run schema-validation tests. No operator check.

- After Step 16 (merge prompts done): commit "prompts: additive-merge
  merge prompts (1.1-1.7)". Render all 6 merge prompts + 1.7 coherence
  against Dostoevsky fixture; verify Jinja renders without errors. No
  operator check.

- After Step 22 (Pass 2-6 adjustments done): commit "pass 2-6: adjustments
  + max_tokens bumps + CT Boddice-align". No operator check.

- At Step 23 (Stage 1 merge-layer test): run Pass 1.1-1.7 on Dostoevsky
  fixture. Run `arch_03_preservation_audit.py`. **STOP AND REPORT TO
  OPERATOR.** Operator reviews preservation-audit JSON + per-chunk
  qualitative diffs vs baseline merged_dossier. Operator approves or
  directs iteration.

- At Step 24 (Stage 2 Pass 2-6 test): run Pass 2-7 + Derive on new
  merged_dossier. **STOP AND REPORT TO OPERATOR.** Operator reviews new
  Dostoevsky card vs baseline. Operator approves or directs iteration.

- At Step 25 (Stage 3 manual review): present `ARCH_03_MANUAL_REVIEW_
  CHECKLIST.md` completed per Stage 3 criteria. **STOP AND REPORT.**

- At Step 26 (merge-to-main): DO NOT EXECUTE. Operator performs merge
  manually after signing off on Stage 3.

FIX APPLICATION — DETAILED:

Apply every fix marked SURVIVES or RESHAPED in plan §9. Apply every fix
marked ABSORBED as part of the arch-change itself (they're structural,
not additive). Do NOT apply fixes marked OBSOLETE or SUPERSEDED.

Wave 1 fixes (research layer) — apply at Steps before schema work starts
(can land as first commits on branch or intersperse):
  - 0a-01 through 0a-04: Pass 0a voice_config
  - 1a-01 through 1a-14: Pass 1a Perplexity family (4 voice-type variants)
  - 1b-02 through 1b-14: Pass 1b Gemini family (1b-01 REJECTED)
  - 0b-01 through 0b-23: Pass 0b render + tailor family

Wave 2 fixes (Pass 1c + 1d) — apply before Step 23 test:
  - 1c-01 through 1c-06: Pass 1c fetch mechanics
  - 1d-01 through 1d-05: Pass 1d excerpt selection
  - 1d-06 (HIGH fuzzy-match): DEFER per original plan unless operator
    calls in-session

Wave 3 SURVIVES fixes — apply as part of merge-prompt rewrites (Steps
10-16) or coherence update (Step 16):
  - 1.1-03 (voice_mode drop) + 1.1-04 (period-vocab gradation)
  - 1.2-02 (voice_mode load-bearing)
  - 1.3-03 (period-vocab ripple)
  - 1.4-04 (voice_mode prior)
  - 1.5-04 (voice_mode drop)
  - 1.6-04 (Marley reference_only_passages private tier) + 1.6-06 (voice_mode)
  - 1.7-01 (worked examples) + 1.7-02 (edit-scope) + 1.7-03 (escalation
    pathway) + 1.7-04 (productive-tension criteria)

Wave 3 ABSORBED fixes — included in arch changes themselves:
  - 1.1-02 Cleopatra + 1.1-06 fictional null-discipline
  - 1.2-03 Scheherazade
  - 1.3-02 Dostoevsky narratival (main arch demonstration)
  - 1.4-02 Marley moves + 1.4-03 Octopus
  - 1.5-02 Cleopatra + 1.5-03 fictional general_frame
  - 1.6-02 Octopus + 1.6-03 Scheherazade

Pass 2 fixes:
  - 2-01 stale user prompt: apply
  - 2-02 voice_temporal_stance: apply REWRITE per §14 Q3 LOCKED decision
  - 2-03 formative-candidate: apply RESHAPED per §9.4
  - 2-04 max_tokens: subsumed by 1-arch-03 max_tokens bumps per §6.2

COMMIT DISCIPLINE:

One logical commit per major checkpoint (per §CHECKPOINT GATES). Commit
messages follow repo convention:
  feat(arch-03/<layer>): <one-line summary>

  <paragraph explaining what + why>
  <fix IDs covered>

  Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

TEST DISCIPLINE:

At each commit, run:
  - `venv/bin/python -m pytest tests/ -v` from personas/ — expect passes
    (128-suite + any new tests you add)
  - Schema round-trip: Pydantic model(fixture_data).model_dump() == fixture
  - Jinja render smoke: render each prompt against Dostoevsky fixture,
    verify no UndefinedError / StrictUndefined issues

If tests fail: diagnose on branch; do NOT push until passing.

AUTONOMY BOUNDARIES:

DO autonomously:
  - Schema design within plan §3 spec
  - Prompt wording within plan §4 spec
  - Backward-compat discriminated-union patterns for breaking schema changes
  - Test fixture creation under `personas/tests/fixtures/phase_l_dostoevsky/`
  - Commit + push to branch (not main)
  - Run Dostoevsky fixture through pipeline
  - Iterate on prompts if preservation-audit <85% (up to 2 iterations
    per chunk; escalate if more)

DO NOT autonomously:
  - Merge to main (Step 26 — operator only)
  - Modify REBUILD_PLAN PB#1-9 (frozen per PB#7-like discipline)
  - Modify frozen conventions in _conventions.py (EvidenceTag, SourceCitation,
    Tier, ContestedReading, ProjectionWarning models)
  - Change Runtime side (out of scope per §11)
  - Rewrite Wave 1 fix semantics (apply as specified in tracker)
  - Add new architectural proposals (1-arch-04+) without operator approval

MODEL ECONOMY (locked):

**Sonnet 4.6 + medium effort** for the bulk (~80% of work):
  - Step 1 (branch setup)
  - Steps 2-9 (schema redesign — spec-following Pydantic edits)
  - Steps 11, 13, 14, 15 (Pass 1.2, 1.4, 1.5, 1.6 merge prompts — follow
    Step 10's pattern)
  - Steps 18, 20, 21 (Pass 3/4b/5/6 prompt adjustments)
  - Step 22 (CT Boddice-align one-liner)
  - All Wave 1 fixes (53, tracker-specified)
  - All Wave 2 fixes (12, tracker-specified)
  - All Wave 3 SURVIVES fixes (13)
  - Steps 23-24 (running Dostoevsky fixture — deterministic pipeline execution)
  - Git commits + push operations

**Opus 4.7 + adaptive thinking** for these specific steps/situations:

  - **Step 10 (Pass 1.1 merge prompt)** — first merge-prompt rewrite;
    establishes pattern for Steps 11-15. Sharp Block 2 additive-merge
    discipline wording matters because 5 other prompts replicate it.

  - **Step 12 (Pass 1.3 REASONING merge prompt)** — ~150-line Dostoevsky
    narratival worked example with analytical_context (3
    worked_demonstrations + 3-5 structural_patterns + 5 scholarly_debates).
    Requires voice-authoring + Phase-L-card-lifting with accuracy. The
    architectural demonstration. Sonnet would produce adequate-but-flat;
    Opus produces template-quality content.

  - **Step 16 (Pass 1.7 coherence)** — adding Check 8 + Check 9 + 3
    worked examples for resolve-by-edit / accept-productive-tension /
    escalate categories. Nuanced; worked examples need operational
    specificity.

  - **Step 17 (Pass 2 voice_temporal_stance 2-02 REWRITE)** — new
    `VoiceTemporalStance` model + prompt spec for .default (fluid) vs
    .anchored_override (death-threshold). Novel field shape; wording
    distinction matters for Voice Pipeline downstream.

  - **Stage 1 post-audit diagnosis** (if preservation-audit <85% on any
    of §3/§4/§5) — diagnosis-heavy judgment on which prompt tweaks
    recover preservation without breaking other properties. Opus high effort.

  - **Stage 2 qualitative review** of new Dostoevsky card vs baseline —
    reading both cards on breadth, register, Boddice-tag compliance,
    anti-flattening.

  - **Any architectural ambiguity** mid-implementation — escalation per
    autonomy-bounds policy. Sonnet detects ambiguity, stops, requests
    Opus handoff (user re-opens session with Opus).

**Estimated split:** ~80% Sonnet (2.5 days at medium effort), ~20% Opus
(0.5-1 day targeted escalations). Total model cost ~$80-130 for the
implementation. Small fraction of the DR-investment-preservation value.

**Operator (user)** does: Stage 3 manual review, merge-to-main decision,
any escalation not resolvable in session.

EXIT CRITERIA:

Branch ready for operator merge-to-main when:
  - All schema + prompt + runtime changes applied per plan
  - Dostoevsky fixture passes Stage 1 preservation-audit (≥85% + 100%
    citation + 100% structural-pattern)
  - Dostoevsky fixture passes Stage 2 Pass 2-7 (no synthesis failures,
    no validation regressions)
  - ARCH_03_MANUAL_REVIEW_CHECKLIST.md populated for operator Stage 3
    review
  - All commits pushed to origin/arch-03-additive-merge
  - Tree clean on branch

Report back to operator with branch state + Stage 1/2 results summary.
Operator performs Stage 3 review and manual merge.
```

**Implementation start gate:**
- Plan doc committed to `main` with decisions locked (this commit)
- `arch_03_preservation_audit.py` instrumentation script to be drafted by Sonnet as first implementation task (Step 0 — before branch setup)
- Sonnet session opens with copy-pasted prompt template above

---

*Plan document status: PRE-SEED COMPLETE — 2026-04-22. Opus 4.7 pre-seed delivered on branch `arch-03-additive-merge`. Sonnet session handles remaining Sonnet-shaped work.*
*Last updated: 2026-04-22.*

---

## 17. Pre-seed completion status (added 2026-04-22)

Per user decision to pre-seed Opus-heavy steps before Sonnet session fires,
the following deliverables landed on branch `arch-03-additive-merge`:

**Branch state:** `arch-03-additive-merge` opened from `main` HEAD `05896f8`.
Two pre-seed commits:
- `f98370c` — schemas (permissive containers)
- `ceb7b94` — prompts + runner config

### Pre-seed delivered (Opus 4.7 work)

**Schemas (complete per plan §3):**

- `personas/schemas/_analytical.py` — NEW shared models: StructuralPattern
  + StructuralPatternInstance + WorkedDemonstration + ScholarlyDebate +
  AnalyticalContext container. Full docstrings + examples.
- `personas/schemas/pass_1_1.py` — LifeScaffold + FormativeCandidate updated:
  scholarly_context + contested_readings + resonates_with_commitments cross-
  ref + AnachronismEntry structured form (backward-compat via discriminated
  union on list[str | AnachronismEntry]).
- `personas/schemas/pass_1_2.py` — Commitment + Concept + Tension updated:
  scholarly_context + contested_readings + tension_type classification +
  translation_tradition_notes on Concept.
- `personas/schemas/pass_1_3.py` — ReasoningStep + Textures updated with
  scholarly_context; step_number optional.
- `personas/schemas/pass_1_4.py` — Move + Register + Vocabulary updated
  with scholarly_context + structural_pattern_refs + genre_specific_register
  + translator_tradition_notes; VocabEntry structured form (backward-compat
  discriminated union).
- `personas/schemas/pass_1_5.py` — KnowledgeBoundary + SensitiveTopic +
  HardLimits updated: ExclusionEntry + Prohibition structured forms
  (backward-compat); scholarly_reception on SensitiveTopic.
- `personas/schemas/pass_1_6.py` — Works gains bibliographic_scholarly_
  context; Passages gains translator_tradition_coverage.
- `personas/schemas/merged_dossier.py` — analytical_context_reasoning +
  analytical_context_voice (optional) top-level keys composed.

**Verified backward-compat:** Phase L Dostoevsky `merged_dossier.json`
validates against new schemas (optional fields default to empty/null;
existing list[str] fields accept via discriminated union).

**Merge prompts (complete per plan §4):**

All 6 merge prompts rewritten with additive-merge discipline (Block 2
expanded). Worked examples added per ABSORBED Wave 3 fixes:

- `pass_1_1_merge.md` (28K rendered) — 5 worked examples: Plato + Octopus
  + Whanganui + Cleopatra hostile-sourced + Scheherazade fictional.
- `pass_1_2_merge.md` (16K) — Plato + Octopus + Whanganui + Scheherazade.
- `pass_1_3_merge.md` (51K — architectural demo) — Plato + Octopus +
  **full Dostoevsky narratival worked example**: 8-step reasoning_method +
  5 structural_patterns (scandal-scene, carnivalization, threshold-
  chronotope, sideshadowing, confession-under-pressure) + 3 worked_
  demonstrations (Nechaev→Demons, Alyosha-death→Karamazov, Pushkin-Speech)
  + 4 scholarly_debates + rich textures. This IS the architectural
  demonstration — shows what pre-1-arch-03 would have compressed to 11K
  instead preserved in ~50K of merged output.
- `pass_1_4_merge.md` (10K) — Plato + Marley (moves completion per 1.4-02)
  + Octopus (1.4-03).
- `pass_1_5_merge.md` (15K) — Plato + Octopus + Cleopatra hostile-source
  with full 3-topic sensitive_topics demonstration.
- `pass_1_6_merge.md` (12K) — Plato + Marley with reference_only_passages
  private-tier demo (1.6-04) + Octopus + Scheherazade multi-translator
  (1.6-03).

**Pass 1.7 coherence prompt (complete per plan §5):**

- Block 2 checks expanded to 9 (Check 8 source-attribution preservation +
  Check 9 analytical-context presence per plan §5.2).
- Block 3 resolution policy: edit-scope discipline (1.7-02), escalation
  downstream pathway (1.7-03), productive-tension ALL-3-criteria (1.7-04).
- Block 4 worked examples added (1.7-01 pattern-break repair): 3 examples
  covering resolve-by-edit / accept-productive-tension / escalate.

**Pass 2 (complete per plan §6):**

- `persona_pass_2_identity_boundaries.md` — voice_temporal_stance REWRITE
  per fix 2-02 LOCKED: deployment-configurable with `.default` (fluid-
  across-time, mandatory) + `.anchored_override` (optional death-threshold
  for chat/project). 3-6 sentence spec per sub-field. Formative-candidate
  commit-to-ONE-PRIMARY-with-1-2-SUPPORTING-inline reword per 2-03
  RESHAPED. Selection-discipline line naming richer 1-arch-03 merged_
  dossier.
- `persona_pass_2_user.md` — "10 fields" (was 9) per 2-01; voice_temporal_
  stance added to field-name list + spec-hint line.

**Pass 3/4a/6 (minor per plan §6.1):**

Jinja-comment guidance on reading 1-arch-03 new merged_dossier fields:
- Pass 3: commitments + scholarly_context + contested_readings + tensions
- Pass 4a: genre_specific_register + translator_tradition_notes +
  analytical_context_voice + structural_pattern_refs + reference-not-
  display discipline naming
- Pass 6: bibliographic_scholarly_context + translator_tradition_coverage

**Pass 4b + 5 unchanged** (CT-based; no merged_dossier direct read).

**CT prompt (complete per plan §6.3):**

- `persona_coherence_threading.md` — Boddice §14 3-part formative
  vocabulary replaces v3.10 "wound and lesson" language.

**Runner config (complete per plan §6.2):**

- `run_persona_pipeline.py` — `_claude_pass` default max_tokens 24000 →
  32000 (Pass 2/3/4a/6 benefit automatically).
- `run_pass_1_7.py` — max_tokens 64000 → 100000; `_load_chunk_outputs`
  expanded layout for analytical_context keys + sensible optional defaults.
- `run_pass_1_3.py` — OUTPUT_KEYS += analytical_context_reasoning.
- `run_pass_1_4.py` — OUTPUT_KEYS += analytical_context_voice.

### NOT pre-seeded (Sonnet session handles)

Per plan §16 model-economy — Sonnet-shaped work:

- **`personas/scripts/arch_03_preservation_audit.py`** (NEW) —
  instrumentation script for Stage 1 preservation-audit. Sonnet drafts
  per plan §7.3 specification (char overlap / citation preservation /
  named-structural-pattern preservation; JSON audit output).
- **`personas/tests/fixtures/phase_l_dostoevsky/`** — test fixture
  directory setup. Sonnet copies Phase L research inputs + baseline
  card per plan Appendix C.
- **Wave 1 fixes (53 fixes across Pass 0a / 1a×4 / 1b×4 / 0b family)** —
  tracker-specified mechanical applications. Sonnet executes per
  `_workspace/planning/PIPELINE_REVIEW_FIXES.md`.
- **Wave 2 fixes (12 fixes: Pass 1c + 1d)** — tracker-specified. Sonnet.
- **Stages 1/2/3 test runs + iteration** — Sonnet runs Dostoevsky fixture
  through pipeline; operator reviews at Stage 3.
- **128-test suite updates** — schema-shape assertions for permissive
  containers; prompt-render smoke tests. Sonnet per plan §14 Q4 minimum
  coverage.
- **ARCH_03_MANUAL_REVIEW_CHECKLIST.md** drafting — Sonnet stub-drafts
  during Stage 3 preparation; operator reviews + signs off.

### Revised Sonnet handoff (supersedes §16 prompt)

Copy-paste for Sonnet session (updated from §16 to reflect pre-seed done):

```
You are continuing the 1-arch-03 Additive Merge Architecture implementation
for the AI Assembly project. Opus 4.7 pre-seed is COMPLETE on branch
`arch-03-additive-merge` (commits f98370c + ceb7b94). Your job: the
Sonnet-shaped remainder — Wave 1/2/3 mechanical fixes, test fixture
setup, preservation-audit instrumentation, Stage 1/2 execution +
operator-review hand-off.

ORIENTATION READING (in order):

1. `_workspace/planning/ARCH_03_ADDITIVE_MERGE_PLAN.md` — THE plan.
   Read §1-§17 completely. §17 documents pre-seed completion; you pick up
   from §17's "NOT pre-seeded" list.

2. `_workspace/planning/PIPELINE_REVIEW_FIXES.md` — fix tracker. Reference
   for specific fix IDs (Wave 1 + Wave 2 + Wave 3 SURVIVES).

3. `code/CLAUDE.md` — repo conventions.

4. `_workspace/planning/REBUILD_PLAN.md` — PB#1-9 locked decisions.

BRANCH STATE:

You start on `arch-03-additive-merge` at HEAD `ceb7b94`. Verify:
  git status  # clean tree expected
  git log --oneline -3  # should show ceb7b94 + f98370c + main merge-base

SCOPE (what you do):

1. **Draft `personas/scripts/arch_03_preservation_audit.py`** per plan
   §7.3 spec. Three metrics: character overlap (target ≥85% on §3/§4/§5);
   citation preservation (target 100%); named-structural-pattern
   preservation (target 100%). JSON output. Run-from-command-line with
   --voice flag.

2. **Set up `personas/tests/fixtures/phase_l_dostoevsky/`** per plan
   Appendix C. Copy research inputs (Perplexity + Gemini + Claude DR 6
   sections) + baseline card from projects/phase-l-dostoevsky/. README
   documenting fixture purpose.

3. **Apply Wave 1 fixes** — 53 fixes per tracker (Pass 0a, Pass 1a×4,
   Pass 1b×4, Pass 0b family). Tracker specifies exact change language
   per fix. Commit logical groups.

4. **Apply Wave 2 fixes** — 12 fixes per tracker (Pass 1c + Pass 1d).
   1d-06 fuzzy-match HIGH architectural: DEFER unless operator opts in.
   Commit.

5. **Run Stage 1 merge-layer test** on Dostoevsky fixture:
   `cd personas && venv/bin/python run_pass_1_all.py "Fyodor Dostoevsky"
    --project ../../projects/phase-l-dostoevsky --use-test-fixtures`
   Run `arch_03_preservation_audit.py` on output.
   **STOP AND REPORT TO OPERATOR** with audit JSON + per-chunk size/content
   comparison vs. baseline.

6. **Run Stage 2 Pass 2-6 test** on new merged_dossier:
   `venv/bin/python run_persona_pipeline.py "Fyodor Dostoevsky"
    --project ../../projects/phase-l-dostoevsky`
   (Clear 04_generation/ 05_validation/ 06_derive/ caches first.)
   **STOP AND REPORT TO OPERATOR** with new card vs. baseline comparison.

7. **Draft `ARCH_03_MANUAL_REVIEW_CHECKLIST.md`** stub per plan §14 Q1
   for operator Stage 3 review. **STOP AND REPORT.**

8. **DO NOT merge to main** — operator-only per plan §15.

MODEL ECONOMY (you):

Sonnet 4.6 + medium effort handles all above. Escalate to Opus 4.7 ONLY if:
- Audit fails (<70% preservation after 2 iterations on a chunk) — open
  Opus session for diagnosis + prompt-iteration
- Stage 2 card shows qualitative regression — Opus qualitative review
- Plan spec is genuinely ambiguous — Opus judgment

AUTONOMY BOUNDS (inherit from plan §16):

DO autonomously: script drafting, fixture setup, mechanical fix
application per tracker specs, Stage 1/2 execution, commits + pushes
to branch, schema-shape test additions.

DO NOT autonomously: merge to main (operator), modify REBUILD_PLAN
PB#1-9, change Runtime side, rewrite pre-seed deliverables (schemas,
merge prompts, Pass 2 rewrite, CT Boddice-align — all Opus-authored and
LOCKED; you extend + test, not rewrite), add new architectural proposals.

EXIT CRITERIA (branch ready for operator):
- Preservation-audit passes Stage 1 criteria on Dostoevsky fixture
- Pass 2-6 + Pass 7 validation passes Stage 2 on new merged_dossier
- ARCH_03_MANUAL_REVIEW_CHECKLIST.md drafted + populated
- All commits pushed to origin/arch-03-additive-merge
- Tree clean

Report back to operator with:
- Preservation-audit JSON
- Stage 1 + Stage 2 summary
- Any Opus-escalation events during session
- Branch head commit hash for operator merge-review

Start with Step 1 (preservation-audit script drafting). Report for
intermediate check-in after step 4 (Wave 1 + Wave 2 fixes complete +
branch state clean); then run Stage 1.
```

### Tracker updates to land with pre-seed commit-to-main

When operator merges `arch-03-additive-merge` → `main`, update tracker:
- Mark 1-arch-03 status: `APPLIED` (was PROPOSED)
- Mark Wave 3 ABSORBED fixes: `APPLIED` (resolved via arch change)
- Mark Wave 3 OBSOLETE fixes: `OBSOLETE-UNDER-1-ARCH-03 LANDED` (no separate
  implementation)
- Mark 1-arch-02: `RESOLVED-VIA-1-ARCH-03 LANDED`
- Mark Wave 3 SURVIVES fixes: update Status from PROPOSED → APPLIED (per
  commit `ceb7b94` + individual prompt edits)
- Mark Pass 2 fixes (2-01/2-02/2-03): `APPLIED`
- Mark Pass 2 fix 2-04: `APPLIED` (max_tokens bump landed in `_claude_pass`)
- Update Consolidated totals.

Leave Wave 1 + Wave 2 fixes at PROPOSED status — Sonnet session applies
these post-merge or during Sonnet-handoff session.

---

---

## 18. Two-session workflow: Sonnet implementation → Opus testing

**Scope decision (2026-04-22, REVISED):** operator opted for two-session
workflow — Sonnet handles mechanical implementation prep; Opus handles
testing from the merged-dossier point onwards.

- **Session A (Sonnet 4.6 + medium effort):** implementation — draft
  preservation-audit script, set up fixture, apply Wave 1/2/3-SURVIVES
  mechanical fixes per tracker. **Stops BEFORE running Stage 1/2/3 tests.**
- **Session B (Opus 4.7 + adaptive, fresh session):** testing — Stages
  1/2/3 on branch state after Sonnet session completes. Preservation-audit
  judgment, prompt iteration if needed, qualitative card-quality review.

Clean division of labor — Sonnet does mechanical-specified work per tracker;
Opus does judgment-heavy testing + quality validation. Operator receives
Opus reports at Stage 1/2/3 checkpoints and decides merge-to-main.

### §18a — Sonnet implementation session handoff (fires FIRST)

```
You are running the 1-arch-03 Additive Merge Architecture SONNET
IMPLEMENTATION SESSION for the AI Assembly project. Opus 4.7 pre-seed
is complete on branch `arch-03-additive-merge` (HEAD 843b974). Your
job: implement the mechanical parts of the plan — instrumentation
script, test fixture, Wave 1/2/3-SURVIVES fix applications per tracker.
STOP BEFORE running Stage 1/2/3 tests — those fire in a separate Opus
session after yours.

Model: You are Sonnet 4.6 + medium effort. Mechanical execution of
tracker-specified fixes is Sonnet-shaped work. Escalate to Opus ONLY
if plan spec is genuinely ambiguous or a tracker-specified fix has
cross-file implications you can't resolve from spec.

ORIENTATION READING (in order):

1. `_workspace/planning/ARCH_03_ADDITIVE_MERGE_PLAN.md` — THE plan.
   Read §1 through §18 completely. §17 documents pre-seed completion
   (Opus-authored; DO NOT MODIFY). §18a (this section) specifies
   your scope. §9 triages every Wave 1-3 fix — apply SURVIVES +
   RESHAPED status only.

2. `_workspace/planning/PIPELINE_REVIEW_FIXES.md` — fix tracker with
   exact change-language per fix. This is your spec for Wave 1/2/3
   applications.

3. `code/CLAUDE.md` — repo conventions (venv rules, load_dotenv pattern).

4. `_workspace/planning/REBUILD_PLAN.md` — PB#1-9 locked decisions.
   Do NOT re-litigate.

BRANCH STATE:

You start on `arch-03-additive-merge` at HEAD `843b974`. Verify:
  cd "/Users/aienvironment/Desktop/AI Assembly/code"
  git status              # clean tree expected
  git checkout arch-03-additive-merge
  git log --oneline -7    # should show 843b974, 38b84c4, 0c1fb28, 008ab0c, ceb7b94, f98370c, 05896f8

Do NOT start a new branch. Do NOT merge to main.

SCOPE (what you do):

STEP 1 — Draft `personas/scripts/arch_03_preservation_audit.py`

Per plan §7.3, implement three metrics:

(a) **Character overlap.** Computes unique-substring overlap between DR §N
    source section and merged chunk outputs. Target ≥85% on §3/§4/§5.

(b) **Citation preservation.** Extract Bibliography-style citations from
    source; verify appearance in merged chunk citations[]. Target 100%.

(c) **Named-structural-pattern preservation** (§3 specific). Extract named
    scholarly patterns (scandal-scene, carnivalization, threshold-chronotope,
    sideshadowing, crowning/decrowning, Menippean, confession-under-pressure,
    vdrug, polyphony) from DR §3 source; verify each appears in
    analytical_context_reasoning. Target 100%.

JSON output to `projects/phase-l-dostoevsky/voices/fyodor_dostoevsky/_arch_03_audit.json`.

CLI: `venv/bin/python scripts/arch_03_preservation_audit.py --voice fyodor_dostoevsky --project ../../projects/phase-l-dostoevsky`

**Commit:** `feat(arch-03): preservation audit instrumentation`

STEP 2 — Fixture setup (optional)

Two options:
(i) Copy Phase L Dostoevsky research inputs to
    `personas/tests/fixtures/phase_l_dostoevsky/` per plan Appendix C.
    Use for repeatable testing.
(ii) Run in place on `projects/phase-l-dostoevsky/` — research inputs
    already frozen there. Simpler.

Recommend (ii) for this testing round. Skip (i) unless operator requests.
README in fixture dir documenting fixture purpose if you do create.

**Commit if created:** `feat(arch-03): Dostoevsky test fixture`

STEP 3 — Apply Wave 1 SURVIVES fixes (53 fixes)

Per `PIPELINE_REVIEW_FIXES.md` Wave 1 section (Steps 1-17, all 53 fixes
SURVIVE per plan §9.1). These are research-layer fixes:

- 0a-01 through 0a-04 (Pass 0a voice_config)
- 1a-01 through 1a-14 (Pass 1a Perplexity family × 4 voice-type variants)
- 1b-01 REJECTED (do NOT apply); 1b-02 through 1b-14 (Pass 1b Gemini family)
- 0b-01 through 0b-23 (Pass 0b render + tailor family)

Tracker specifies exact change-language per fix. Apply mechanically.

**Commit in logical groups:**
- `fix(wave-1/pass-0a): 4 fixes per tracker`
- `fix(wave-1/pass-1a): 14 fixes across 4 voice-type variants`
- `fix(wave-1/pass-1b): 13 fixes across 4 voice-type variants (1b-01 rejected)`
- `fix(wave-1/pass-0b): 23 fixes across wrapper+header+4 bodies+footer+tailor`

STEP 4 — Apply Wave 2 SURVIVES fixes (12 fixes)

Per tracker Wave 2 section (Steps 18-19):

- 1c-01 through 1c-06 (Pass 1c fetch mechanics)
- 1d-01 through 1d-05 (Pass 1d excerpt selection)
- 1d-06 (HIGH architectural fuzzy-match): DEFER unless operator opts in
  via chat before session start. Operator default: defer.

**Commit:**
- `fix(wave-2/pass-1c): 6 fixes per tracker`
- `fix(wave-2/pass-1d): 5 fixes (1d-06 deferred)`

STEP 5 — Apply Wave 3 SURVIVES fixes

Per plan §9.3, 13 fixes SURVIVE (independent of arch-03 absorption):

- 1.1-03, 1.1-04 (voice_mode drop, period-vocab gradation)
- 1.2-02 (voice_mode load-bearing)
- 1.3-03 (period-vocab ripple)
- 1.4-04 (voice_mode prior)
- 1.5-03 (already in pre-seed — SKIP; verify), 1.5-04 (voice_mode drop)
- 1.6-04 (Marley reference_only_passages — already in pre-seed — SKIP;
  verify), 1.6-06 (voice_mode drop)
- 1.7-01 through 1.7-04 (pre-seed — SKIP; verify all in current prompts)
- 2-01 (already in pre-seed — SKIP; verify)
- 2-02 LOCKED (already in pre-seed — SKIP; verify)
- 2-03 RESHAPED (already in pre-seed — SKIP; verify)

**Most Wave 3 SURVIVES fixes are already applied in pre-seed.** Your job:
VERIFY each is applied in the relevant prompt file; apply any missing.
Period-vocabulary gradation coordinated patch across 1.1/1.2/1.3 is the
main remaining explicit work.

**Commit:** `fix(wave-3/survives): period-vocabulary coordinated patch + voice_mode disposition verification`

STEP 6 — Verify branch state before handoff to Opus

- All commits pushed to origin/arch-03-additive-merge
- Tree clean: `git status`
- 128-test suite passes: `cd personas && venv/bin/python -m pytest tests/ -v`
  (schema-shape tests may need updates — if failing, diagnose and fix)
- Render-smoke test: all merge prompts + Pass 2-6 prompts render cleanly
  against Dostoevsky voice_config

**DO NOT:**
- Run Stage 1 merge-layer test (run_pass_1_all.py on Dostoevsky) — that's
  the Opus testing session's job
- Run Stage 2 Pass 2-7 test
- Draft ARCH_03_MANUAL_REVIEW_CHECKLIST.md — that's Opus
- Merge to main

**DO:**
- Report branch-state summary to operator:
  - Head commit hash
  - Wave 1/2/3 fix-application summary (what landed where)
  - 128-test suite status
  - Any Opus-escalation events during session
- Operator then fires Opus testing session (§18b).

AUTONOMY BOUNDS:

DO autonomously: script drafting, fixture setup (if electing option i),
mechanical fix applications per tracker specs, commits + pushes to
branch.

DO NOT autonomously: merge to main, modify REBUILD_PLAN PB#1-9, modify
frozen `_conventions.py` models, change Runtime side, modify Opus-
authored pre-seed deliverables (schemas + merge prompts + Pass 2 rewrite
+ CT Boddice-align — all LOCKED; you extend/verify but not rewrite),
run Stage 1/2/3 tests (Opus session does these), draft
ARCH_03_MANUAL_REVIEW_CHECKLIST.md (Opus).

EXIT CRITERIA:

Branch `arch-03-additive-merge` ready for Opus testing session:
- Preservation-audit script committed
- Wave 1 + Wave 2 + Wave 3-SURVIVES fixes applied + committed
- 128-test suite passes
- All commits pushed to origin
- Tree clean
- Operator notified with branch-state summary

Operator then opens fresh Opus session with §18b handoff prompt.
```

### §18b — Opus testing session handoff (fires AFTER Sonnet session completes)

```
You are running the 1-arch-03 Additive Merge Architecture TESTING
SESSION for the AI Assembly project. The Sonnet implementation session
has completed; branch `arch-03-additive-merge` is ready with:
- Opus 4.7 pre-seed (schemas + merge prompts + Pass 2-6 adjustments +
  CT Boddice-align + runner config bumps) — the architectural change
- Sonnet implementation (preservation-audit script + Wave 1/2/3-SURVIVES
  fix applications) — mechanical prep

Your job: run Stages 1/2/3 testing from the point where the 3 dossiers
get merged (Pass 1.1) — assess whether arch-03 delivers on its
preservation hypothesis and card-quality improvement.

Model: You are Opus 4.7 + adaptive thinking. Testing requires judgment:
preservation-audit diagnosis when it fails, prompt iteration if needed,
qualitative card-quality comparison vs. baseline.

ORIENTATION READING (in order):

1. `_workspace/planning/ARCH_03_ADDITIVE_MERGE_PLAN.md` — THE plan. Read
   §1-§18 fully. §7 is the test plan. §8 Steps 23-25 are your execution
   sequence. §14 Q5 + §18b (this section) specify your scope.

2. `_workspace/planning/PIPELINE_REVIEW_FIXES.md` — fix tracker. Read §9
   to understand what Sonnet applied.

3. Phase L Dostoevsky baseline card at
   `projects/phase-l-dostoevsky/voices/fyodor_dostoevsky/07_persona_card_assembled.json`
   (114 KB, 35 fields, pre-arch-03 reference — YOUR COMPARISON BASELINE).

4. Phase L research inputs (frozen fixture):
   `projects/phase-l-dostoevsky/voices/fyodor_dostoevsky/01_research/`

BRANCH STATE:

Start on `arch-03-additive-merge` at HEAD provided by operator (post-Sonnet
commits). Verify:
  cd "/Users/aienvironment/Desktop/AI Assembly/code"
  git status
  git checkout arch-03-additive-merge
  git log --oneline -15  # should show Sonnet commits on top of Opus pre-seed

SCOPE (what you do):

STEP 1 — Stage 1 merge-layer test

Run Pass 1.1-1.7 on Dostoevsky fixture:

```bash
cd personas
# Clear old merge outputs for clean test
rm -rf ../../projects/phase-l-dostoevsky/voices/fyodor_dostoevsky/02_merge/pass_1_*
rm -f ../../projects/phase-l-dostoevsky/voices/fyodor_dostoevsky/02_merge/08_merged_dossier.json
venv/bin/python run_pass_1_all.py "Fyodor Dostoevsky" \
    --project ../../projects/phase-l-dostoevsky
```

Expected:
- merged_dossier.json ~300-400K (baseline: 162K)
- pass_1_3/* aggregate ~40-50K (baseline: 11K) — analytical_context_reasoning populated
- pass_1_4/* aggregate ~15-25K (baseline: 11K)
- coherence_flags[] + coherence_resolutions[] populated with real entries

Run preservation-audit:
```bash
venv/bin/python scripts/arch_03_preservation_audit.py --voice fyodor_dostoevsky \
    --project ../../projects/phase-l-dostoevsky
```

**Checkpoint 1: STOP AND REPORT TO OPERATOR** with:
- merged_dossier size + per-chunk sizes vs. baseline
- Preservation-audit JSON
- Sample per-chunk content comparison (choose §3 reasoning to show
  analytical_context_reasoning content vs. pre-1-arch-03 dropping)

If audit fails (<85% §3/§4/§5 char-overlap, or <100% citation, or missing
structural-pattern):
- Diagnose which prompts are under-preserving
- Iterate (max 2 rounds per chunk) — edit prompt on branch, commit, rerun
  affected chunk, re-audit
- Escalate to operator after 2 iterations per chunk

If audit passes: proceed to Step 2.

STEP 2 — Stage 2 Pass 2-7 test

Clear downstream caches, run full pipeline:

```bash
rm -rf ../../projects/phase-l-dostoevsky/voices/fyodor_dostoevsky/04_generation/
rm -rf ../../projects/phase-l-dostoevsky/voices/fyodor_dostoevsky/05_validation/
rm -rf ../../projects/phase-l-dostoevsky/voices/fyodor_dostoevsky/06_derive/
rm -f ../../projects/phase-l-dostoevsky/voices/fyodor_dostoevsky/07_persona_card_assembled.json
rm -rf ../../projects/phase-l-dostoevsky/voices/fyodor_dostoevsky/_ct/
venv/bin/python run_persona_pipeline.py "Fyodor Dostoevsky" \
    --project ../../projects/phase-l-dostoevsky
```

Expected: full 22-pass pipeline end-to-end. New
07_persona_card_assembled.json.

Verify:
- Pass 2-6 complete without Pydantic failures
- voice_temporal_stance is dict with .default + optional .anchored_override
- character field references multiple formative candidates inline (not just
  the PRIMARY)
- Pass 7-pre citation verification pass rate ≥ baseline
- Pass 7-anachronism flag count ≤ baseline
- Pass 7a cross-model register check: PASS (baseline was ISSUE on Pass 5
  output-characteristics fields — hypothesis: richer CT upstream under
  1-arch-03 resolves)
- Pass 7b smoke_test_chains quality
- Pass 7c banned_language / banned_modes / projection_warnings reasonable

**Checkpoint 2: STOP AND REPORT** with:
- New card file size + field counts
- Pass 7 validation summary (compare to baseline)
- 5+ specific field comparisons vs. baseline card showing richer content
- Pass 5 register check: did it resolve from ISSUE to PASS?

STEP 3 — Stage 3 qualitative review

Draft `ARCH_03_MANUAL_REVIEW_CHECKLIST.md` per plan §14 Q1. Populate with
findings from Stages 1+2. Include:

- character: multiple formative candidates referenced inline?
- constitution: 17+ commitments with operational specificity?
- reasoning_method: analytical_context material incorporated (scandal-scene,
  worked-demonstrations, Williams-vs-Frank framing)?
- curated_corpus_passages: translator-tradition-noted corpus used?
- topics_requiring_care: scholarly_reception framings present?
- voice_temporal_stance: dict-shaped deployment-configurable?
- Read-aloud test: richer qualitatively than baseline?

For each check: yes/no + one-line rationale + specific evidence.

**Checkpoint 3: STOP AND REPORT** with filled checklist + your
qualitative verdict + recommendation:
- **PROCEED** — arch-03 delivers; operator should merge to main
- **ITERATE** — specific prompt refinements needed (name them)
- **ROLLBACK** — arch-03 did not deliver; abandon branch

STEP 4 — Operator handoff

DO NOT merge to main. Report back to operator with:
- Preservation-audit JSON (Stage 1)
- Pass 2-7 validation summary + field richness comparisons (Stage 2)
- Filled ARCH_03_MANUAL_REVIEW_CHECKLIST.md (Stage 3)
- Branch head commit hash
- Your PROCEED/ITERATE/ROLLBACK recommendation with reasoning

Operator performs final review + decides merge-to-main.

AUTONOMY BOUNDS:

DO autonomously: Stage 1/2/3 execution, preservation-audit interpretation,
prompt iteration on branch (up to 2 rounds per chunk on Stage 1 failures),
commits + pushes, ARCH_03_MANUAL_REVIEW_CHECKLIST.md drafting.

DO NOT autonomously: merge to main (operator), modify pre-seed deliverables
beyond targeted prompt iteration to fix preservation failures, rewrite
Sonnet-applied Wave 1/2/3 fixes (those are locked per tracker), add new
architectural proposals, modify REBUILD_PLAN PB#1-9 or frozen _conventions.py.

EXIT CRITERIA:

Branch ready for operator final-review + merge decision:
- Stage 1/2/3 results generated + committed
- ARCH_03_MANUAL_REVIEW_CHECKLIST.md committed with your findings
- Your PROCEED/ITERATE/ROLLBACK recommendation delivered
- All commits pushed
- Tree clean

Start with Step 1 — orientation reading + Stage 1 merge-layer test.
```

### Supersession

- §16 (original Sonnet handoff): OBSOLETE
- §17 (revised Sonnet handoff): OBSOLETE
- §18 (this section): ACTIVE — two-session workflow with §18a Sonnet
  implementation + §18b Opus testing

### Post-testing session (separate, not scoped here)

After Opus testing session delivers PROCEED recommendation + operator
merges `arch-03-additive-merge` → `main`:

- Apply tracker updates per plan §17 tracker-update-spec (1-arch-03 APPLIED,
  Wave 3 ABSORBED APPLIED, etc.)
- Phase N voices 2-12 build on new architecture

If Opus delivers ITERATE: specific prompt refinements, re-run Stage 1-3
on iterated branch. Cycle until PROCEED or ROLLBACK.

If Opus delivers ROLLBACK: abandon branch; diagnose + revisit.

### Stale single-session handoff (REMOVED 2026-04-22)

The prior single-session "Opus testing session prompt" that included script
drafting + Wave 1/2/3 fix application within the testing session has been
superseded by §18a + §18b two-session workflow. The operator explicitly
directed: "run the sonnet session. then after, open a fresh opus session to
test everything from the point where the 3 dossiers get merged." Sonnet
does implementation prep (script + Wave 1/2/3 SURVIVES); Opus does
Stages 1/2/3 testing only. The original content has been removed to prevent
confusion — refer to §18a and §18b above.

---

*End plan document — LOCKED for two-session workflow (§18a Sonnet → §18b Opus).*

---

## Appendix A: Schema change diff summary

Quick reference of schema changes:

**Files touched:**
- `personas/schemas/_conventions.py` — no changes (frozen per PB#7)
- `personas/schemas/_analytical.py` — **NEW FILE** — StructuralPattern, WorkedDemonstration, AnalyticalContext
- `personas/schemas/pass_1_1.py` — LifeScaffold + FormativeCandidate: +scholarly_context, +contested_readings, +resonates_with_commitments
- `personas/schemas/pass_1_2.py` — Commitment + Concept + Tension: +scholarly_context, +contested_readings, +translation_tradition_notes, +tension_type
- `personas/schemas/pass_1_3.py` — ReasoningMethod + Textures + analytical_context_reasoning
- `personas/schemas/pass_1_4.py` — Moves + Register + Vocabulary + analytical_context_voice + VocabEntry + genre_specific_register
- `personas/schemas/pass_1_5.py` — KnowledgeBoundary + SensitiveTopics + HardLimits + ExclusionEntry + Prohibition + scholarly_reception
- `personas/schemas/pass_1_6.py` — Works + Passages + URLs: +translator_tradition_coverage, +bibliographic_scholarly_context
- `personas/schemas/merged_dossier.py` — compose new keys (analytical_context_reasoning, analytical_context_voice)

**Breaking changes:**
- `Vocabulary.preferred_vocabulary`: list[str] → list[VocabEntry] (with parallel-support via discriminated union for backward-compat on Phase L card)
- `KnowledgeBoundary.{temporal,geographic,conceptual}_exclusions`: list[str] → list[ExclusionEntry]
- `HardLimits.prohibitions`: list[str] → list[Prohibition]

**Backward-compat strategy:** Pydantic discriminated-union or list[Union[str, StructuredEntry]] pattern. Existing Phase L Dostoevsky merged_dossier still validates.

## Appendix B: Prompt-file diff summary

**Files touched:**
- `personas/flows/shared/prompts/pass_1_1_merge.md` — rewrite Block 2; extend Block 4 (add Cleopatra + Scheherazade); apply 1.1-02/03/04/05/06
- `personas/flows/shared/prompts/pass_1_2_merge.md` — rewrite Block 2; extend Block 4 (add Scheherazade); apply 1.2-02/03
- `personas/flows/shared/prompts/pass_1_3_merge.md` — rewrite Block 2; MAJOR extend Block 4 (add Dostoevsky narratival with analytical_context); apply 1.3-02/03
- `personas/flows/shared/prompts/pass_1_4_merge.md` — rewrite Block 2; extend Block 4 (complete Marley; add Octopus); apply 1.4-02/03/04
- `personas/flows/shared/prompts/pass_1_5_merge.md` — rewrite Block 2; extend Block 4 (add Cleopatra); extend Block 2 general_frame for fictional; apply 1.5-02/03/04
- `personas/flows/shared/prompts/pass_1_6_merge.md` — rewrite Block 2; extend Block 4 (add Octopus; Scheherazade); extend Marley ref_only_passages demo; apply 1.6-02/03/04/06
- `personas/flows/shared/prompts/pass_1_7_coherence.md` — add Block 4 worked examples (1.7-01); apply 1.7-02/03/04; add Check 8 + 9 per §5.2
- `personas/flows/shared/prompts/persona_pass_2_identity_boundaries.md` — add selection-discipline line; apply 2-02 per user decision; apply 2-03
- `personas/flows/shared/prompts/persona_pass_2_user.md` — apply 2-01 (10 fields + voice_temporal_stance)
- `personas/flows/shared/prompts/persona_pass_3_intellectual_core.md` — add reference to scholarly_context + contested_readings
- `personas/flows/shared/prompts/persona_pass_3_user.md` — reference updated merged_dossier fields
- `personas/flows/shared/prompts/persona_pass_4a_voice.md` — add reference to analytical_context_voice + genre_specific_register + translator_tradition_notes
- `personas/flows/shared/prompts/persona_pass_4a_user.md` — reference updated fields
- `personas/flows/shared/prompts/persona_pass_4b_artifact.md` — minor CT-compat
- `personas/flows/shared/prompts/persona_pass_5_engagement.md` — minor CT-compat
- `personas/flows/shared/prompts/persona_pass_6_corpus.md` — add reference to bibliographic_scholarly_context + translator_tradition_coverage
- `personas/flows/shared/prompts/persona_pass_6_user.md` — reference updated fields
- `personas/flows/shared/prompts/persona_coherence_threading.md` — Boddice-align language per Step 27 fwd-ref

**Code touched:**
- `personas/run_persona_pipeline.py` — Pass 2/3/4a/6 max_tokens bumps (24000 → 32000)
- `personas/run_pass_1_7.py` — full rewrite to split architecture per §5.5 amendment (offline compose + narrow LLM audit + Python edit apply). max_tokens: 64000 → 24000 (audit-only output; composition is offline Python). Adds `_compose_dossier`, `_parse_path`, `_apply_edit`, and Pydantic models `DossierEdit` + `CoherenceAuditResult`.
- `personas/scripts/arch_03_preservation_audit.py` — **NEW FILE** for Stage 1 verification

---

## Appendix C: Test fixture specification

**Path:** `personas/tests/fixtures/phase_l_dostoevsky/`

**Contents:**
```
phase_l_dostoevsky/
├── README.md                              # Explains fixture purpose + regeneration cost
├── 01_research/
│   ├── 01_perplexity_dossier.json        # Copy of Phase L Dostoevsky Perplexity
│   ├── 02_gemini_broad_scan.json         # Copy of Phase L Gemini
│   ├── 04_dr_dossier/
│   │   ├── 01_section_1.md ... 06_section_6.md  # Copy of Phase L per-section DR
├── baseline/
│   ├── 07_persona_card_assembled.json    # Phase L baseline card (for comparison)
│   ├── 02_merge/08_merged_dossier.json   # Phase L baseline merged dossier
└── expected/                              # Post-1-arch-03 expected-shape outputs
    └── (populated during Stage 1 testing)
```

**Regeneration cost:** zero (Phase L outputs preserved in projects/phase-l-dostoevsky; fixtures are copies).

**Use in test suite:**
- Schema-validation tests load fixture chunk outputs and verify Pydantic.
- Prompt-render tests use fixture voice_config for Jinja rendering.
- Preservation-audit test compares fixture source (01_research) to Stage-1 merge output.

---

## Next actions (from planning → implementation)

**Decisions landed (2026-04-22):**

1. **2-02 voice_temporal_stance** — RESOLVED: REWRITE to deployment-configurable (default=fluid + anchored_override). Applied at pre-seed in `persona_pass_2_identity_boundaries.md` + `persona_pass_2_user.md`.

2. **Wave 1 + Wave 2 fix landing timing** — RESOLVED: Option B absorbed into two-session workflow. Wave 1/2/3-SURVIVES land inside §18a Sonnet session on `arch-03-additive-merge` branch (after Opus pre-seed, before Opus testing).

3. **Implementation session scope** — RESOLVED: Two-session workflow per §18. §18a Sonnet handles implementation-prep + mechanical fix applications (instrumentation script + Wave 1/2/3-SURVIVES). §18b Opus handles Stages 1/2/3 testing + prompt iteration + recommendation.

4. **Manual review rubric sign-off** — DEFERRED: `ARCH_03_MANUAL_REVIEW_CHECKLIST.md` to be drafted by Opus testing session (§18b Step 3) against Stage 2 card output. Operator reviews filled checklist at Checkpoint 3.

5. **Branch-merge authority** — RESOLVED: User-only. Neither Sonnet nor Opus merges to main. §18a exit criteria: branch ready for Opus. §18b exit criteria: branch ready for operator review + merge decision.

**Active handoffs:**
- §18a Sonnet implementation handoff — copy-paste when firing Sonnet session
- §18b Opus testing handoff — copy-paste when firing Opus session (after Sonnet completes)

---

*Plan document status: PRE-SEED COMPLETE + TWO-SESSION WORKFLOW DEFINED — 2026-04-22.*
*Opus 4.7 pre-seed delivered on branch `arch-03-additive-merge`.*
*Next: operator fires §18a Sonnet session.*
*Last updated: 2026-04-22.*
