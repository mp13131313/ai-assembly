# Phase B Execution Plan

**Paste into a fresh Claude Opus 4.7 (1M context) session at medium effort.**

## Your task

Execute the Phase B persona-pipeline rebuild end-to-end per `_workspace/planning/REBUILD_PLAN.md`. All architectural decisions (PB#1–9 + 16 walkthrough decisions 2026-04-19) are locked in the Decisions log. Your job is implementation across 13 phases (A–M). Commit after each phase with the provided message template. Stop and report at the stop-and-ask triggers.

## Preflight

1. **Read in order — ALL TIERS MANDATORY before any prompt writing.** This plan rewrites ~17 prompts across Phases B–K. Skipping reads silently degrades output quality (prompts written without project-frame context land technically-correct but tonally wrong; prompts written without AUDIENCE_BRIEF miss the hardest-to-please failure modes; prompts written without the current-prompt text lose good patterns worth preserving). All of Tier 1, Tier 2, and Tier 3 are required.

   **Tier 1 — project + decision context:**
   - `CLAUDE.md` (repo layout, orientation reading order)
   - `_workspace/planning/REBUILD_PLAN.md` in full — §"Locked architectural decisions (PB#1–9)" + §"Decisions log (walkthrough 2026-04-19)"
   - `_workspace/planning/EXECUTION_PLAN_phase_b.md` — this doc
   - `docs/AI_Assembly_Briefing_v3_1.md` — project frame (why the pipeline exists, what "success" looks like, the provotype logic). Essential for Phases H + I tonal awareness.
   - `docs/AUDIENCE_BRIEF.md` — audience profile, 7 factions, ten hardest-to-please voices, the "performing reception" failure mode. Essential for Pass 4a "reference not display" guidance (H.2) + Pass 7b smoke-test provocations (I.4) + Pass 7c projection_warnings (I.5).
   - `docs/AI_Assembly_Persona_Card_v2.md` (target 37-field schema Pass 2 produces)
   - `personas/HANDOFF.md` — the "smoke_test_chains are build-time only, NOT runtime few-shot" rule. Critical for I.4 Pass 7b redesign; skipping this risks a prompt that silently invites runtime few-shotting.

   **Tier 1 — Boddice content** (read in full, not just summary):
   - `research/baseline_research/compass_artifact_wf-1e84f45b-0c9f-497a-84bc-88b7867c9a26_text_markdown.md` — §9, §12, §13, §14, §15 (emotions catalogue + evidence tags + `world` rubric + `formative_experience` rubric + field audit). Source material for all Boddice-shaped schemas + prompts.

   **Tier 1 — methodology grounding:**
   - `research/baseline_research/compass_artifact_wf-865974da-a7be-4b7b-b770-0ec4fb7b1221_text_markdown.md` (File 2) — 4-block prompt architecture (Expert Identity / Guardrails / Field Specs / Voice Type), multi-pass generation, distinctiveness testing, verification protocol. Every merge prompt + generation prompt must follow the 4-block pattern.
   - `research/baseline_research/compass_artifact_wf-cc778da2-1ac5-493e-b406-ab71d3b00234_text_markdown.md` (File 3) — architecture layers, 6 failure modes + mitigations (sanitization paradox, flattening, anachronism, anthropomorphism, etc.), TimeChara citation + rationale. Essential for I.2 Pass 7-anachronism prompt.

   **Tier 1 — existing prompts being replaced:**
   - **All 19 files** in `personas/flows/shared/prompts/persona_pass_*.md` + `pass_0a_voice_config.md` + `pass_0b_dr_prompt.md`. Read to preserve the good patterns (streaming + retry + checkpoint conventions) and invert only the Boddice-problematic parts. Do not rewrite from scratch without reading the current version.

   **Tier 2 — pipeline code patterns** (read to preserve idioms):
   - `personas/flows/shared/clients.py` — `call_claude(thinking: bool)` signature + streaming + adaptive thinking pattern
   - `personas/flows/shared/io.py` — atomic writes + voice_slug
   - `personas/flows/shared/prompt_render.py` — `jinja2.StrictUndefined` pattern
   - `personas/run_persona_pipeline.py` — `_call_with_retry` + revision-loop + cache-as-checkpoint disciplines

   **Tier 2 — rebuild intel + session context:**
   - `_workspace/archive/session-artifacts/FRESH_REVIEW_2026_04_19.md` §5 — what v3.10 patterns to preserve (checkpoint-as-cache, shuffle seed 42, voice_basis metadata), what to rethink
   - `_workspace/archive/session-artifacts/SESSION_REPORT_2026-04-19.md` — context on the 16 decisions (why, not just what)

   **Tier 2 — quality baseline for Phase L review:**
   - `_workspace/archive/runs/personas/plato/persona_card_assembled.json` — the v3.10 Plato card. Reference during Phase H prompt writing (what good output looks like) + Phase L.8 review (does rebuild meet/beat this?)

   **Tier 3 — cross-repo + tool context:**
   - `research/baseline_research/compass_artifact_wf-45560dac-98db-4376-9002-5ee8e80bb4f5_text_markdown.md` (File 1) — tool comparison, relevant for PB#1 research-source rationale
   - `runtime/flows/provocateur_flow.py` (skim — lines 100-200 + package_voice_briefings fn) — Provocateur Profile consumer, so Phase J Derive knows what shape to produce
   - `runtime/flows/shared/council/council_config.json` + `README.md` — council config structure + hot-swap semantics + `_REQUIRED_MEMBER_FIELDS` validator at `runtime/flows/shared/io.py`

2. Baseline must be green:
   ```bash
   cd /Users/aienvironment/Desktop/ai-assembly
   git status                       # clean
   cd runtime && venv/bin/python -m pytest ingest/tests/ -v   # 29/29
   ```

3. Branch:
   ```bash
   git checkout -b phase-b-rebuild
   ```

4. **Personas venv** (already on Python 3.12 post fix-plan). If dependencies needed: `pydantic`, `jsonschema` — install via `personas/venv/bin/pip install pydantic jsonschema`.

---

## Phase A — Infrastructure setup (no chunk work)

### A.1 `personas/schemas/` directory with Pydantic SoT

Create:
- `personas/schemas/__init__.py` (empty)
- `personas/schemas/_conventions.py` — shared types:
  - `EvidenceTag` = `Literal["stated", "scholarly_consensus", "inference", "experiential_reconstruction", "projection_warning"]`
  - `Tier` = `Literal["tier_1_primary", "tier_2_scholarly", "tier_3_contested"]`
  - `SourceCitation` Pydantic model: `{author, work, year?, page?, url?, tier}`
  - `ContestedReading` Pydantic model: `{consensus_view, minority_view, scholars_per_view: list[str]}`
- `personas/schemas/_entry.py`:
  - `validate_chunk_output(model_class, data) -> parsed_instance` (uses `model_class.model_validate(data)`; raises `ValidationError` with critique string for retry)
  - `generate_json_schemas()` — iterates all chunk models, writes `generated/<name>.schema.json` files (for inclusion in LLM prompts + any non-Python consumer)
- `personas/schemas/generated/` directory (empty; populated by `_entry.py:generate_json_schemas()`)
- `personas/schemas/README.md` — brief doc: SoT = Pydantic; regeneration command; conventions frozen after chunk 1.2 per PB#7.

### A.2 Split `personas/inputs/conference_context.json` 3-way

Current file contents distribute into:
- `personas/inputs/conference_facts.json` — `conference_name`, `conference_short`, `host_organization`, `host_founders`, `location`, `dates`, `anniversary`, `tagline`, `conference_context_paragraph`, `session_role_for_ai_assembly`
- `personas/inputs/audience_profile.json` — `participants_count_approx`, `participant_profile`, `programming_tracks_representative`; top-matter pointer: *"Canonical source: `docs/AUDIENCE_BRIEF.md`. Update brief first, then re-render this file."*
- `personas/inputs/panel_roster.json` — `panel_members_final`

Then `git rm personas/inputs/conference_context.json`.

### A.3 Update consumers for the split

- `personas/run_pass0a_voice_config.py` — loads `conference_facts.json` + `panel_roster.json` only (drops audience). Replace the `INJECTED_BY_RUNNER` placeholder hack with explicit load + field injection.
- `personas/run_phase0_1_research.py` + `personas/run_pass0b_dr_prompt.py` — load `conference_facts.json` only for lightweight context.
- `personas/run_persona_pipeline.py` — Pass 7b `conference_context` consumer: load all three files, assemble into the shape Pass 7b expects.

### A.4 Move test fixtures out of archive

```bash
mkdir -p personas/tests/fixtures/ibn_battuta
git mv _workspace/archive/runs/personas/ibn_battuta/01_research/perplexity_dossier.json \
       personas/tests/fixtures/ibn_battuta/perplexity_dossier.json
git mv _workspace/archive/runs/personas/ibn_battuta/01_research/gemini_broad_scan.json \
       personas/tests/fixtures/ibn_battuta/gemini_broad_scan.json
```

Create `personas/tests/fixtures/README.md` per REBUILD_PLAN §"Test material in repo" — costs, commands, last refresh date, refresh triggers.

Update `_workspace/planning/REBUILD_PLAN.md` §"Test material in repo" + §B.4 to point at new paths.

### A.5 Verify + commit Phase A

```bash
cd personas && venv/bin/python -c "
import sys; sys.path.insert(0, '.')
from schemas._conventions import EvidenceTag, SourceCitation, Tier, ContestedReading
from schemas._entry import validate_chunk_output, generate_json_schemas
import json
json.loads(open('inputs/conference_facts.json').read())
json.loads(open('inputs/audience_profile.json').read())
json.loads(open('inputs/panel_roster.json').read())
print('Phase A infra: OK')
"
```

**Commit A:**
```
refactor(phase-b/A): set up schemas/ Pydantic SoT, split conference_context, move test fixtures

- personas/schemas/ created with _conventions.py + _entry.py + generated/ dir.
  Pydantic SoT per decisions log #1.
- personas/inputs/conference_context.json split 3-way (facts/audience/panel)
  per decisions log #6.
- personas/tests/fixtures/ibn_battuta/ migrated from _workspace/archive/
  per decisions log #7.
- Pass 0a/0.5/7b runners updated for new config paths.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```

---

## Phase B — Chunk 1.1 BIOGRAPHICAL (end-to-end proof of architecture)

### B.1 Pydantic models

Create `personas/schemas/pass_1_1.py`:

```python
from pydantic import BaseModel, Field
from typing import Literal
from ._conventions import EvidenceTag, SourceCitation

class LifeScaffold(BaseModel):
    """Pass 1.1 biographical foundation — the voice's life events, dates, places, institutions.

    Per Boddice §13 5-part `world` rubric: ontological furniture / available
    pathē in original language / framework for difficulty / model of selfhood
    / anachronisms-to-avoid. This scaffold is the structural ground; the
    FormativeCandidate sibling captures the formative-experience shape.
    """
    name: str
    type: Literal["human", "non_human", "fictional"]
    subtype: Literal["organism", "system"] | None
    birth_year: int | None
    death_year: int | None
    primary_locations: list[str]
    institutions_founded_joined_opposed: list[str]
    key_relationships: list[dict]  # {person, relation_type, evidence_tag, citations}
    intellectual_world: str  # period intellectual currents, in the voice's own framing
    ontological_furniture: str  # per Boddice §13: what was real for this voice
    available_pathe: list[dict]  # list of {term_in_original_language, gloss, evidence_tag, citations}
    framework_for_difficulty: str  # per Boddice §13
    model_of_selfhood: str  # per Boddice §13
    anachronisms_to_avoid: list[str]  # period-specific; 4-8 items

class FormativeCandidate(BaseModel):
    """Per Boddice §14 4-part rubric. Multiple candidates possible; Pass 2 commits.

    For human voices: 3 active sub-fields (community + lived_through_apparatus + engagement).
    For non-human/system/cosmic voices: 3 active sub-fields (community_or_ontogenetic_field +
    condition_of_being + engagement) — condition_of_being replaces lived_through_apparatus.
    """
    candidate_label: str  # short name e.g. "Trial of Socrates" or "Semelparous lifespan"
    formative_emotional_community: str  # per Boddice §14 sub-field 1
    lived_through_own_apparatus: str | None = None  # per §14 sub-field 2 (human voices)
    condition_of_being: str | None = None  # per §14 sub-field 4 (non-human voices; replacement for #2)
    engagement_it_drives: str  # per §14 sub-field 3
    evidence_tag: EvidenceTag  # usually "experiential_reconstruction"
    citations: list[SourceCitation]
    scholarly_support_score: Literal["strong", "moderate", "contested"]  # Pass 2 uses this when committing
```

### B.2 Pass 1.1 merge prompt

Create `personas/flows/shared/prompts/pass_1_1_merge.md` using the 4-block structure (per baseline research File 2):

```
{# Pass 1.1 Biographical merge (Claude Opus 4.7 + adaptive thinking).
   Reads Perplexity + Claude DR + Gemini dossiers. Emits LifeScaffold +
   FormativeCandidate[] per personas/schemas/pass_1_1.py. #}

BLOCK 1 — ROLE

You are a senior historian-of-emotions merging biographical research on {{ name }}
from three sources (Perplexity sonar-deep-research, Claude Deep Research, Gemini
broad scan) into a structured Boddice-rubric-shaped dossier chunk. Your discipline
is Rob Boddice's biocultural history of emotions — you reconstruct the voice's
emotional-experiential world using period-specific vocabulary, never projecting
modern categories onto the record.

BLOCK 2 — GUARDRAILS

- Only attribute direct quotes to verifiable primary sources (work title, page).
- Paraphrases: tag "[scholarly_consensus]" or "[inference]".
- Claims about what the voice felt / meant / experienced as biocultural reconstruction: tag "[experiential_reconstruction]".
- Modern English terms used because no better word exists: tag "[projection_warning: <distortion>]".
- Do NOT use modern emotion-words where the voice's period had its own vocabulary. For Plato: `pathē`, `theia mania`, `orgē`, `aidōs`, `thumos`, `phobos`, `phthonos`. For Battuta: `sabr`, `tawakkul`, `ibtilā'`. Etc.
- Surface contested readings; do not resolve into false consensus.

BLOCK 3 — OUTPUT SCHEMA

Return a single JSON object with two top-level keys: `life_scaffold` and `formative_candidates`. Schema definitions (generated from Pydantic):

<inline the generated JSON Schema for LifeScaffold + FormativeCandidate from personas/schemas/generated/1_1_life_scaffold.schema.json + 1_1_formative_candidates.schema.json>

BLOCK 4 — WORKED EXAMPLES (three branches, per decisions log #4)

{{ include: Plato-worked-example (human philosophical) — Boddice §13/§14 text for Plato }}

{{ include: Octopus-worked-example (non-human organism) — Boddice §13/§14 text for Octopus }}

{{ include: Whanganui-worked-example (non-human system) — Boddice §13/§14 text for Whanganui }}

BLOCK 5 — YOUR INPUT

VOICE NAME: {{ name }}
VOICE TYPE: {{ type }} (subtype: {{ subtype|default:"null") }})

PERPLEXITY DOSSIER:
{{ perplexity_dossier_text }}

CLAUDE DEEP RESEARCH DOSSIER:
{{ claude_dr_dossier_text }}

GEMINI BROAD SCAN:
{{ gemini_broad_scan_text }}

BLOCK 6 — YOUR TASK

Merge biographical material from all three sources into LifeScaffold +
FormativeCandidate[] per the schemas. Reconcile contradictions across sources.
Surface multiple formative candidates rather than picking one (Pass 2 commits).
Use period-specific vocabulary. Tag evidence. Never invent.

Return JSON only — no preamble, no commentary.
```

### B.3 Pass 1.1 runner

Create `personas/run_pass_1_1.py`:

```python
# Load 3 source dossiers for a voice
# Render pass_1_1_merge.md with dossier contents + voice metadata
# Call Claude Opus 4.7, streaming, adaptive thinking, max_tokens=32000
# Parse JSON response
# Validate via LifeScaffold.model_validate() + list[FormativeCandidate].model_validate()
# On ValidationError: retry once with critique string appended to user prompt
# Write life_scaffold.json + formative_candidates.json to runs/<voice_slug>/01_research/pass_1_1/
```

Mirror the `_call_with_retry` pattern from `run_pass0a_voice_config.py`.

### B.4 Test on Battuta fixtures (merge mechanics only; content will be v3.10-shaped)

```bash
cd personas && venv/bin/python -c "
import sys; sys.path.insert(0, '.')
from run_pass_1_1 import run_pass_1_1
# Simulated: use test fixtures + a mock Claude DR (either the Desktop file or a truncated sample)
result = run_pass_1_1(voice_slug='ibn_battuta', use_test_fixtures=True)
print(f'LifeScaffold fields: {list(result.life_scaffold.model_dump().keys())}')
print(f'FormativeCandidates: {len(result.formative_candidates)}')
print('Merge mechanics: OK')
"
```

Expect: schema validates, JSON writes. Content is v3.10-wound-shaped (fixtures are pre-Boddice), which is expected — end-to-end Boddice content validation lands with the first real voice run in Phase L.

### B.5 Iterate schema until Pass 2 mapping is clean

Mental exercise before committing: given `life_scaffold.json` + `formative_candidates.json`, can Pass 2 fill the persona card's `world` field (per Boddice §13 rubric) and `formative_experience` field (per §14 rubric) cleanly? If missing data or awkward mapping, amend the Pydantic models + merge prompt + re-run. Iterate until clean.

### B.6 Commit B

```
feat(phase-b/B): implement chunked Pass 1.1 BIOGRAPHICAL end-to-end

- personas/schemas/pass_1_1.py: LifeScaffold + FormativeCandidate Pydantic models
  per Boddice §13 + §14 rubrics.
- personas/flows/shared/prompts/pass_1_1_merge.md: merge prompt with 4-block
  structure (role / guardrails / schema / worked examples) per baseline research File 2.
  Worked examples: Plato + Octopus + Whanganui per decisions log #4.
- personas/run_pass_1_1.py: runner loads 3 sources, calls Opus 4.7 streaming,
  validates via Pydantic, retries with critique on ValidationError.
- Tested on Battuta v3.10 fixtures; merge mechanics verified
  (Boddice content validation pending first real voice run).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```

**Stop-and-ask trigger:** if B.5 iteration exceeds 3 rounds, stop and report — the schema may need structural redesign.

---

## Phase C — Chunk 1.2 INTELLECTUAL + lock conventions

### C.1 Pydantic models

Create `personas/schemas/pass_1_2.py`:
- `Commitment`: `{statement, operational_note, textual_source, unique_to_this_voice: bool, evidence_tag, citations}`
- `Concept`: `{term, term_in_original_language?, definition, what_it_rules_out, textual_source, unique_to_this_voice: bool, evidence_tag, citations}`
- `Tension`: `{description, conflicting_commitments: list[str], passage_citations: list[SourceCitation], evidence_tag}`

### C.2 Pass 1.2 merge prompt

Same structure as B.2, tailored for intellectual framework. Includes Plato / Octopus / Whanganui worked examples for §13's intellectual-world + commitments mapping.

### C.3 Runner

`personas/run_pass_1_2.py` mirrors 1.1 pattern.

### C.4 Test + validate on Battuta fixtures.

### C.5 **Lock conventions** per PB#7

After C.4 passes, review `_conventions.py` + both chunk schemas. If META fields (EvidenceTag, SourceCitation, Tier, etc.) are stable, commit them as frozen. Any subsequent chunk (1.3–1.6) reuses them unchanged.

Add a comment header to `_conventions.py`: `# FROZEN as of 2026-XX-XX per PB#7. Changes require architectural decision review.`

### C.6 Commit C

```
feat(phase-b/C): implement chunked Pass 1.2 INTELLECTUAL + lock meta-conventions

- personas/schemas/pass_1_2.py: Commitment + Concept + Tension models
- personas/flows/shared/prompts/pass_1_2_merge.md: merge prompt
- personas/run_pass_1_2.py: runner
- _conventions.py FROZEN per PB#7 — META schema conventions locked after
  chunks 1.1 + 1.2 land cleanly. Chunks 1.3-1.6 reuse unchanged.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```

**Stop-and-ask trigger:** if C.5 reveals a META gap that requires schema restructure, stop and report before proceeding to D.

---

## Phase D — Chunks 1.3, 1.4, 1.5, 1.6 (pattern replication)

Same pattern as B + C. Each chunk: Pydantic models + merge prompt + runner + test. Conventions frozen.

### D.1 Chunk 1.3 REASONING
- Models: `ReasoningMethod` (5-8 step cognitive/perceptual/narrative moves per voice_mode), `Textures` (finds_compelling + resists collections)
- Files: `personas/schemas/pass_1_3.py`, `personas/flows/shared/prompts/pass_1_3_merge.md`, `personas/run_pass_1_3.py`

### D.2 Chunk 1.4 VOICE
- Models: `Moves` (characteristic named moves), `Register` (register_and_tone + rhetorical_mode), `Vocabulary` (preferred_vocabulary + metaphorical_repertoire)
- Files: `pass_1_4.py`, `pass_1_4_merge.md`, `run_pass_1_4.py`

### D.3 Chunk 1.5 BOUNDARIES
- Models: `KnowledgeBoundary` (temporal + geographic + conceptual exclusions), `SensitiveTopics` (topics + navigation guidance), `HardLimits` (3-5 absolute prohibitions)
- Files: `pass_1_5.py`, `pass_1_5_merge.md`, `run_pass_1_5.py`

### D.4 Chunk 1.6 CORPUS
- Models: `Works` (complete catalogue), `Passages` (8-15 characteristic passages with tier + purpose), `URLs` (digitised full-text sources)
- Files: `pass_1_6.py`, `pass_1_6_merge.md`, `run_pass_1_6.py`

### D.5 Commit D (one commit covering all four chunks — they're symmetric)

```
feat(phase-b/D): implement chunked Pass 1.3-1.6 (REASONING/VOICE/BOUNDARIES/CORPUS)

Same pattern as 1.1-1.2: Pydantic models + merge prompts + runners.
Meta-conventions reused unchanged (frozen per PB#7 after chunk 1.2).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```

**Stop-and-ask trigger:** if any chunk's content demands META changes despite the PB#7 freeze, stop and report. Reopening the conventions is a significant decision.

---

## Phase E — Chunk 1.7 coherence pass + merged_dossier

### E.1 `personas/schemas/merged_dossier.py`

Pydantic model composing chunks 1.1–1.6 via inheritance/composition:

```python
class MergedDossier(BaseModel):
    life_scaffold: LifeScaffold
    formative_candidates: list[FormativeCandidate]
    commitments: list[Commitment]
    concepts: list[Concept]
    tensions: list[Tension]
    reasoning_method: ReasoningMethod
    textures: Textures
    moves: Moves
    register: Register
    vocabulary: Vocabulary
    knowledge_boundary: KnowledgeBoundary
    sensitive_topics: SensitiveTopics
    hard_limits: HardLimits
    works: Works
    passages: Passages
    urls: URLs
    # Plus coherence metadata from Pass 1.7:
    coherence_flags: list[dict]  # cross-chunk consistency issues flagged by 1.7
    coherence_resolutions: list[dict]  # how each flag was resolved
```

### E.2 Pass 1.7 coherence prompt

Reads all 6 chunk outputs; checks cross-chunk consistency:
- Does `formative_candidates` support `commitments` (formative event justifies core positions)?
- Do `concepts` referenced in `reasoning_method` actually exist in the concepts chunk?
- Does `voice.register` align with `reasoning_method`?
- Are `knowledge_boundary` anachronisms consistent with `life_scaffold.anachronisms_to_avoid`?
- Does `corpus.passages` cite works from `corpus.works`?

Output: `merged_dossier.json` with `coherence_flags` + `coherence_resolutions` metadata.

### E.3 Runner

`personas/run_pass_1_7.py` — loads 6 chunk outputs, calls Opus 4.7, produces `merged_dossier.json`.

### E.4 Orchestrator

`personas/run_pass_1_all.py` — runs all 7 Pass 1.x (parallel 1.1-1.6, then 1.7). This is the successor to v3.10's monolithic Pass 1-merge.

### E.5 Commit E

```
feat(phase-b/E): implement Pass 1.7 coherence + merged_dossier + orchestrator

- personas/schemas/merged_dossier.py: MergedDossier Pydantic composes
  chunks 1.1-1.6 + coherence_flags/resolutions.
- personas/flows/shared/prompts/pass_1_7_coherence.md: cross-chunk
  consistency check.
- personas/run_pass_1_7.py + run_pass_1_all.py.
- Chunked Pass 1 merge is now end-to-end functional.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```

---

## Phase F — Pass 0a redesign

Per REBUILD_PLAN §"Phase 0 — Intake · Pass 0a" (7 items) + decisions log.

### F.1 Voice config schema

Create `personas/schemas/voice_config.py`:
- Existing fields: `name`, `type`, `subtype`, `voice_mode`, `hostile_sources`, `corpus_constraint`
- New fields: `editorial_rationale` (replaces "Why this voice is in the Assembly"), `manual_grounding` (unifies `wikipedia_extract` + `disambiguation_hint`)
- Dropped: `conference_context` field (decoupled per decisions log)

### F.2 Pass 0a runner redesign

Update `personas/run_pass0a_voice_config.py`:
- Load only `conference_facts.json` + `panel_roster.json` (not full audience)
- `--choose N` fix: always exit on out-of-range (pick one behavior, consistent)
- Drop the `INJECTED_BY_RUNNER` placeholder pattern (now unnecessary)
- Add `editorial_rationale` prompt to human (curator writes it directly; not model-proposed)
- Domain-specific grounding branch for non-human voices: curated `non_human_grounding/` dir with Godfrey-Smith (Octopus) and Te Awa Tupua Act (Whanganui) excerpts

### F.3 Create `personas/inputs/non_human_grounding/`
- `octopus.md` — Godfrey-Smith *Other Minds* excerpt (fair-use short passage)
- `whanganui.md` — Te Awa Tupua (Whanganui River Claims Settlement) Act 2017 preamble + §12-14
- README documenting expected contents

### F.4 Tighten review-doc disposition-table labels: everything is `proposed` except `name` which is `auto`.

### F.5 Commit F

```
feat(phase-b/F): redesign Pass 0a per decisions log + REBUILD_PLAN Pass 0a items

- voice_config schema: editorial_rationale + manual_grounding fields;
  conference_context field dropped.
- Pass 0a runner: loads split conference files, fixed --choose N, drops
  placeholder hack, domain-specific grounding branch for non-human voices.
- personas/inputs/non_human_grounding/ with Octopus + Whanganui grounding texts.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```

---

## Phase G — Phase 0.5 redesign (voice-type-specific prompts + hybrid tailoring)

### G.1 Voice-type-specific Pass 1a prompts

Split current `persona_pass_1a_research_human.md` into:
- `persona_pass_1a_human.md` — unchanged structure + Boddice rubric asks (period-vocabulary, character-grammar-not-Big-Five)
- `persona_pass_1a_non_human_organism.md` — ecological/cognitive framing; ban anthropomorphism
- `persona_pass_1a_non_human_system.md` — Indigenous-representation framing (CARE + IPAI); legal-personhood grounding
- `persona_pass_1a_fictional.md` — narrative-function framing

### G.2 Voice-type-specific Pass 1b prompts (same split; lighter touch)

### G.3 Pass 0b template decomposition

Split the current 1086-line `pass_0b_dr_prompt.md` into:
- `pass_0b_header.md` (shared preamble)
- `pass_0b_human.md` (human branch, ~300 lines)
- `pass_0b_non_human_organism.md` (~300 lines)
- `pass_0b_non_human_system.md` (~300 lines)
- `pass_0b_fictional.md` (~300 lines)
- `pass_0b_footer.md` (shared hostile-sources + corpus_constraint blocks)

Each branch template carries the Boddice rubric asks (drop wound framing, add period-vocabulary requirement per decisions log).

### G.4 NEW: Hybrid Jinja+LLM tailoring pass (PB#2)

Create `personas/run_pass_0b_tailor.py`:
- Runs after Jinja render of the decomposed template
- Opus 4.7 call with tailoring prompt: customize per-voice illustrative figures (Augustine→al-Ghazali for Battuta), SWAP TEST anchors, emphasis redirect based on Perplexity coverage, optional pruning of clearly-inapplicable bullets
- Does NOT rewrite bullet structure
- Output: voice-tailored DR prompt (~120-130 KB)

Update `personas/run_phase0_1_research.py` to call the tailor pass after Jinja render.

### G.5 Update `personas/flows/shared/dr_validation.py`

Relaxed per PB#9: validate shape but soften the rigid 6-section markdown requirement (DR can produce any structure that fits the research; canonicalization at Pass 1 merge).

Add per-section word-count floors (~1,500 per major section) per REBUILD_PLAN Phase 0.5 decision.

### G.6 Commit G

```
feat(phase-b/G): Phase 0.5 redesign — voice-type-specific prompts + hybrid tailoring

- Pass 1a + 1b prompts split by voice type (human/non-human-organism/
  non-human-system/fictional); each carries Boddice rubric asks.
- Pass 0b template decomposed from 1086 lines to per-type sub-templates.
- NEW: Pass 0b hybrid Jinja+LLM tailoring pass (PB#2) — voice-customizes
  illustrative figures, SWAP TEST anchors, emphasis.
- dr_validation.py relaxed per PB#9 + section-level word-count floors added.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```

---

## Phase H — Pass 2–6 generation prompt revisions

### H.1 Pass 2 (Identity & Boundaries)

Update `persona_pass_2_identity_boundaries.md` + `persona_pass_2_user.md`:
- Read `merged_dossier.json` (Boddice-shaped) instead of old 6-section markdown
- Fill `world` field using Boddice §13 5-part rubric from `life_scaffold.ontological_furniture` + related sub-fields
- Fill `formative_experience` field using Boddice §14 4-part rubric from `formative_candidates` (Pass 2 COMMITS to one candidate)
- Tag outputs with `[experiential_reconstruction]` where applicable

### H.2 Pass 4a (Voice)

Update `persona_pass_4a_voice.md`:
- Reads `vocabulary` + `register` + `moves` from merged dossier
- **Critical guidance added (per Boddice sanity check):** *"The card's period-vocabulary is reference material for the voice's reasoning, not required output. Use period-specific terms when the moment calls for it — do not display vocabulary for display's sake. The audience is philosophically literate but not classics-vocabulary-literate; output that reads as scholarly exhibition fails."*

### H.3 Pass 3, 4b, 5, 6

Review + update where Boddice rubric affects inputs. Pass 3 (Intellectual Core) reads `commitments` + `concepts` + `tensions` from merged dossier. Pass 5 (Engagement) reads `constitution` + `reasoning_method` (both now built from merged dossier). Pass 6 (Corpus) reads `works` + `passages` + `urls`.

### H.4 Commit H

```
feat(phase-b/H): Pass 2-6 generation prompts updated for Boddice-shaped merged dossier

- Pass 2: fills world (Boddice §13 5-part) + formative_experience (§14 4-part).
- Pass 4a: reads Boddice voice fields + critical "reference not display"
  guidance on period-vocabulary usage.
- Pass 3/4b/5/6: consume Boddice-shaped merged dossier sub-sections.
- All passes tag outputs with [experiential_reconstruction] / [projection_warning]
  where applicable.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```

---

## Phase I — Pass 7 redesign

Per decisions log #8–11.

### I.1 Pass 7-pre extended

Update `persona_pass_7pre_citation.md`: after citation verification, verify Boddice tags:
- Every claim about what the voice felt/meant/experienced carries `[experiential_reconstruction]`
- Every modern-English term used faute de mieux carries `[projection_warning]`
- Flag missing tags for revision loop

### I.2 NEW: Pass 7-anachronism (TimeChara-style)

Create `persona_pass_7_anachronism.md` + `run_pass_7_anachronism.py`:
- Runs between Pass 7-pre and Pass 7a
- Cross-model (o3 or Gemini) reads assembled card; checks for temporal anachronism
- Explicit test: would this figure have had access to this concept in their historical period? If not, is it explicitly flagged as anachronism or translated via `translation_protocol`?
- Output: `anachronism_flags[]` + overall PASS/REVISION_NEEDED
- Revision loop integration: flagged items trigger re-run of Pass 2 / 4a / 5 with anachronism critique

### I.3 Pass 7a unchanged

Multi-family chain locked per decisions log.

### I.4 Pass 7b renamed to "Card Smoke Test"

- Rename `persona_pass_7b_provocations.md` → `persona_pass_7b_smoke_test.md` (keep file but update header)
- Update runner to reference new name
- Rename assembled-card field from `worked_provocations` → `smoke_test_chains` in:
  - `docs/AI_Assembly_Persona_Card_v2.md` (field definition)
  - `run_persona_pipeline.py` (card assembly code)
  - `personas/HANDOFF.md` (cross-repo docs)
  - Runtime `_REQUIRED_MEMBER_FIELDS` doesn't include this field so no runtime cascade
- Revised prompt asks for provocations testing Boddice-rubric framing under pressure

### I.5 Pass 7c two-list output

Update `persona_pass_7c_negative.md` to emit two lists:
- `banned_language[]` (unchanged role)
- `projection_warnings[]` — each entry: `{term, distortion_explanation}`. Examples: `{"trauma": "imports 1980s Anglo therapeutic sediment; voice's own framework is <X>"}`

Update the Pydantic model for the assembled card accordingly.

### I.6 Commit I

```
feat(phase-b/I): Pass 7 redesign per decisions log #8-11

- Pass 7-pre extended for Boddice tag verification.
- NEW Pass 7-anachronism (TimeChara-style) between 7-pre and 7a.
- Pass 7a unchanged (multi-family locked).
- Pass 7b renamed to "Card Smoke Test"; field worked_provocations →
  smoke_test_chains (build-time-only, no runtime cascade).
- Pass 7c emits two lists: banned_language[] + projection_warnings[].

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```

---

## Phase J — Phase 4 Derive tweaks

### J.1 Derive prompt update

Update `persona_derive.md` + `persona_derive_user.md`:
- Correctly reads Boddice-shaped `world` (5-part rubric) when deriving `speaks_from`
- Correctly reads Boddice-shaped `formative_experience` (3-part per voice type) when deriving `core_commitment` + `activates_on`
- Reads `translation_protocol` unchanged for `translation_range`
- **Provocateur Profile schema unchanged** (preserves cross-repo contract)

### J.2 Commit J

```
feat(phase-b/J): Phase 4 Derive updated to read Boddice-shaped card fields

Derive prompt correctly maps from world (§13 5-part) + formative_experience
(§14 3-part) to the 8-field Provocateur Profile. Schema unchanged —
preserves the council_config.json cross-repo contract.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```

---

## Phase K — Cross-Persona QC (Phase 5) new flow

Per decisions log #13.

### K.1 New flow

Create `personas/phase_5_cross_persona_qc.py`:
- Gates on: all 12 voices have assembled cards at `runs/<voice>/persona_card_assembled.json`
- Loads all 12 cards
- Runs three sub-tests (K.2 below)
- Outputs `runs/cross_persona_qc.json` with per-pair similarity scores + flagged distinctiveness gaps + per-voice "needs rework" recommendations

### K.2 Three sub-tests

**Swap test** (`_swap_test()`):
- For each pair (voice_a, voice_b), construct a test: take a constitution principle from voice_a, present it attributed to voice_b alongside voice_b's actual principles. Ask cross-model evaluator (o3 or Gemini): which one is the interloper?
- Score: % correctly identified across all pairs. Low → cards are too generic.

**Blind identification** (`_blind_id_test()`):
- Remove voice names from `character` + `register_and_tone` fields. Shuffle excerpts. Present to evaluator without attribution. Ask: which voice does this excerpt come from?
- Score: % correctly attributed across all 12 × K excerpts.

**Same-question distinctiveness** (`_same_question_test()`):
- Pick one shared provocation (reuse a smoke_test_chain from Pass 7b). Run all 12 voices through it.
- Evaluator reads 12 responses side-by-side, scores pairwise similarity. Flag pairs scoring >0.7 (too similar).

### K.3 Revision integration

Voices flagged by QC get re-run on the flagged failure dimension:
- Constitution similarity → re-run Pass 3 with cross-card critique
- Voice/register similarity → re-run Pass 4a with cross-card critique
- Max 2 cross-card revision rounds per voice

### K.4 Commit K

```
feat(phase-b/K): Cross-Persona QC (Phase 5) new flow

- personas/phase_5_cross_persona_qc.py: gates on 12 completed cards,
  runs swap + blind_id + same_question sub-tests.
- Cross-model evaluator (OpenAI o3 or Gemini; different family from Claude
  writer per self-preference-bias argument).
- Revision loop: flagged voices get Pass 3 or Pass 4a re-run with
  cross-card critique (max 2 rounds).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```

---

## Phase L — First-voice end-to-end test

**Pick: Plato.** Well-documented, philosophical, covers the common case well. Validates the full rebuilt pipeline end-to-end.

### L.1 Run new Pass 0a on Plato

```bash
cd personas && venv/bin/python run_pass0a_voice_config.py "Plato"
```

Expected: new voice config with `editorial_rationale` + `manual_grounding` fields (no more `conference_context` field).

### L.2 Run Phase 0.5 (Perplexity + Gemini + tailored DR prompt)

```bash
cd personas && venv/bin/python run_phase0_1_research.py "Plato"
```

Expected: fresh Perplexity + Gemini outputs + tailored DR prompt (PB#2 tailoring pass ran).

### L.3 Manual Claude DR session

Human pastes the tailored DR prompt into claude.ai (Opus 4.7 + Extended Thinking + Deep Research). Saves dossier.

### L.4 Chunked Pass 1

```bash
cd personas && venv/bin/python run_pass_1_all.py "Plato"
```

Expected: 6 chunk outputs + merged_dossier.json validated.

### L.5 Phase 2–6 generation

```bash
cd personas && venv/bin/python run_persona_pipeline.py "Plato" --from-phase-2
```

(Runner may need a flag to start from Phase 2 since Phase 1 outputs are now at new paths.)

### L.6 Phase 3 validation

All Pass 7 sub-passes run. Expect PASS across the board; any REVISION_NEEDED triggers the revision loop.

### L.7 Phase 4 Derive

Produces `provocateur_profile.json` + `evaluation_rubric.json`.

### L.8 Review output quality

Human review: is Plato's new card BETTER than his v3.10 card (at `_workspace/archive/runs/personas/plato/persona_card_assembled.json`)?

Checks:
- Does `formative_experience` use Boddice's 4-part rubric?
- Does `world` reflect Boddice's 5-part rubric?
- Is Pass 4a output period-vocabulary-informed but NOT scholarly-display?
- Does smoke_test_chains make sense as build-time diagnostic?
- Do evidence tags (`[experiential_reconstruction]`, `[projection_warning]`) appear appropriately?

### L.9 Iterate if needed

Quality issues surfaced by L.8 feed back into Phase H (Pass 2-6 prompt tuning) or Phase I (Pass 7 redesign). Re-run affected phases, re-test L.

### L.10 Commit L

```
feat(phase-b/L): first-voice end-to-end test — Plato rebuilt under Phase B

Complete pipeline run from new Pass 0a through Phase 4 Derive.
Validates:
- Infrastructure (schemas, config split, fixtures)
- Chunked Pass 1 merge (1.1-1.7)
- Phase 0.5 voice-type-specific prompts + hybrid tailoring (PB#2)
- Phase 2-6 generation with Boddice-shaped inputs
- Phase 3 validation (Pass 7-pre / 7-anachronism / 7a / 7b / 7c)
- Phase 4 Derive with Boddice-aware field mapping

Plato's rebuilt card produced at runs/plato/persona_card_assembled.json.
Reviewed against _workspace/archive/runs/personas/plato/ (v3.10 baseline);
quality comparison recorded in runs/plato/rebuild_review.md.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```

**Stop-and-ask trigger:** if L.8 review reveals significant quality regression vs v3.10 Plato, stop and report. Do not proceed to Phase M.

---

## Phase M — Verification + push + PR

### M.1 All runtime tests pass

```bash
cd runtime && venv/bin/python -m pytest ingest/tests/ -v
```

Expected: 29/29.

### M.2 Schema round-trips

```bash
cd personas && venv/bin/python -c "
import sys; sys.path.insert(0, '.')
from schemas._entry import generate_json_schemas
generate_json_schemas()
print('Schemas regenerated cleanly')
"
```

### M.3 Cross-references updated

Grep for stale references:
```bash
grep -rn "worked_provocations" docs/ personas/ runtime/ --include="*.md" --include="*.py" | grep -v "_workspace/archive" | grep -v "smoke_test_chains"
```
Expected: 0 hits outside archive (all renamed to smoke_test_chains).

```bash
grep -rn "conference_context.json" docs/ personas/ runtime/ --include="*.md" --include="*.py" | grep -v "_workspace/archive"
```
Expected: 0 hits outside archive (split into 3 files).

### M.4 Push + PR

```bash
git push -u origin phase-b-rebuild

gh pr create --title "feat: Phase B persona pipeline rebuild" --body "$(cat <<'EOF'
## Summary

Complete Phase B persona pipeline rebuild per `_workspace/planning/REBUILD_PLAN.md`.

Lands:
- Pydantic schemas with JSON Schema generation (personas/schemas/)
- Chunked Pass 1 merge (1.1 BIOGRAPHICAL through 1.7 coherence) replacing
  monolithic Pass 1-merge
- Boddice biocultural rubric (formative_experience 4-part, world 5-part)
  propagated through research → merge → synthesis layers
- Phase 0.5 voice-type-specific prompts + hybrid Jinja+LLM tailoring (PB#2)
- Pass 7 redesign: Pass 7-anachromism sub-pass + Pass 7b renamed to
  Card Smoke Test + Pass 7c two-list output (banned_language +
  projection_warnings)
- Phase 5 Cross-Persona QC new flow
- First-voice validation on Plato

## Test plan

- [x] 29/29 runtime tests pass
- [x] Schema round-trip clean
- [x] No stale references to old field names / config paths outside archive
- [x] Plato first-voice end-to-end produces valid assembled card
- [x] Quality review of Plato card vs v3.10 baseline (no regression)

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

### M.5 Commit M (or merge as part of PR)

Final verification commit:
```
chore(phase-b/M): verification — all tests pass, schemas clean, no stale refs

Phase B rebuild complete and validated. Ready to rebuild remaining 11
voices under the new architecture (each one ~4-6 hours end-to-end:
Pass 0a + Phase 0.5 + manual DR session + chunked Pass 1 + Phase 2-4).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```

---

## Stop-and-ask rules

- `pytest` fails in preflight → stop; refactor needs a green baseline.
- Phase A, B, or C any pydantic validation fails consistently → stop; schema design may be wrong.
- Phase C.5 conventions freeze reveals gaps → stop; reopening the freeze is significant.
- Phase D chunks can't reuse frozen conventions → stop; same.
- Phase L first-voice review shows quality regression vs v3.10 Plato → stop; prompt tuning needed before Phase M.
- Any runtime test fails at M.1 → stop; Phase B should not have touched runtime.
- Any cross-reference grep at M.3 finds unexpected stale refs → update them before pushing.

## Out of scope

- Voice Pipeline Steps 1+2+3 (separate workstream per REBUILD_PLAN §"Out of scope")
- Runtime changes beyond council_config.json sync (Phase B doesn't touch runtime code)
- Briefing v3.1 sentence on flagged-projection (Till/Matthias decision; flag only)
- §15 field renames beyond the single smoke_test_chains rename (defer to Card v3 sweep)
- Rebuilding voices 2-12 (separate sessions after Phase M merges; follow same pattern as Phase L)

## Model + effort

**Opus 4.7 (1M context), medium effort.** Phase B is design-heavy (schemas + prompts) not mechanical edits; 1M context needed for the Tier 1+2+3 preflight reads (~18 files, ~500K tokens combined) plus chunk merge tests reading multiple source dossiers; medium effort is sufficient given the 16 decisions are pre-locked in REBUILD_PLAN's Decisions log + the enriched preflight closes the context gaps that would otherwise force higher-effort reasoning. No need to escalate to high effort — the decisions are made; Opus is executing them, not re-litigating.

---

*This plan lives in `_workspace/planning/` until Phase B lands, then moves to `_workspace/archive/fix-plans/` as executed.*
