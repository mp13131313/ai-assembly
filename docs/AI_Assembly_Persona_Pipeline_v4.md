# AI ASSEMBLY — Persona Pipeline

**Project:** The AI Assembly · World Beautiful Business Forum · Athens · May 7–10, 2026
**Status:** v4.0 — current 2026-04-27. Production for athens-2026.
**Purpose:** Specifies the automated pipeline that produces completed Persona Cards — one per voice. Implemented as a Python script (`run_persona_pipeline.py`), parallel across all voices, calling four model APIs in sequence. **This document describes how the pipeline is actually built; for *why* particular architectural decisions were taken, see `docs/CURRENT_STATE.md` §5.16–5.28.**

**Predecessor:** v3.10 (2026-04-17) at `docs/_archive/AI_Assembly_Persona_Pipeline_v3_10.md`. The v3.10 changelog history (v2.0 → v3.10) is preserved there. v4 is a fresh-write reflecting the current implementation.

---

## Changelog: v3.10 → v4.0

The v3.10 spec describes a monolithic Pass 1-merge plus six generation passes plus a revision loop. Under the hood, that pipeline has been substantially re-engineered between 2026-04-21 and 2026-04-27 while keeping the 35-field card schema + per-voice cost envelope stable. v4 names the result.

| Area | v3.10 | v4.0 | Reference |
|---|---|---|---|
| **Pass 1 merge** | Monolithic 3-way contradiction check (single Opus call) | **Chunked Pass 1.1–1.7** — 6 Pydantic-validated chunk merges in parallel + narrow Pass 1.7 coherence audit | CURRENT_STATE §5.18 (arch-03), schemas/pass_1_*.py |
| **Per-voice on disk** | flat `inputs/voices/<slug>.json` + `runs/<slug>/` | `voices/<slug>/{00_intake … 06_derive, 07_persona_card_assembled.json}` | CURRENT_STATE §5.16 (Phase B) |
| **Code/project separation** | code + project data co-mingled in repo | Tier 3: project data outside code repo at `PROJECT_ROOT`, resolved via `--project` > env > hard fail | CURRENT_STATE §5.17 |
| **Manual DR step** | One monolithic claude.ai session per voice | **6 per-section claude.ai sessions** per voice; §1–§5 use Opus 4.6, §6 uses Opus 4.7 | Phase 0.5 below |
| **Pass 0b** | Single Jinja render | **Two-stage**: Pass 0b base render (Jinja, no LLM) + Pass 0b tailor (LLM, structured injections only) + 6-section split | Phase 0.5 below |
| **Primary text URLs** | In voice_config, supplied by operator or Pass 0a | Derived deterministically at render time from `passages[].citation` + `works[]` (1-arch-07; CC#1) | flows/shared/url_extract.py |
| **Pass 6.5-clean** | — | **NEW**: deterministic regex bracket-strip after Pass 6 (FU#33 P1); preserves Boddice biocultural tags | flows/shared/bracket_strip.py |
| **Pass 7-pre** | Single-shot Sonnet call (hit 128K output ceiling) | **3-stage chunked**: Stage 1 extract → Stage 2 verify N parallel batches → Stage 3 boddice tag check (FU#2) | flows/shared/pass_7pre_chunked.py |
| **Pass 7a-FIX** | — | **NEW**: linear patcher (FU#13) — single Opus call emits surgical JSON patches; replaced revision loop. Cost $1 vs $5–10 per loop | run_persona_pipeline.py:1080–1326 |
| **Pass 7-anachronism** | — | **NEW**: dedicated TimeChara temporal check before Pass 7a; merges into 7a `field_issues` | persona_pass_7_anachronism.md |
| **Chat artifact** | — | **NEW (FU#41)**: 4th Derive output — `06_derive/03_chat_system_prompt.json` for Claude project paste-target. Strips 11 fields | flows/shared/chat_prompt_builder.py |
| **Card field generation patterns** | Static field specs | **FU#49 universal patterns** in Pass 2/4a/4b/5: structural-strain licensing in `epistemic_frame_statement`; two-aporia in `translation_protocol`; phenomena-outside-corpus in `topics_requiring_care`; Position B corpus-accurate softening in `hard_limits`; premature-closure in `banned_modes`; 5+2 quality_criteria; framework-strain closer in `unique_contribution` | CURRENT_STATE §5.23 |
| **Sentinel regen pattern** | — | **NEW (FU#29)**: `scripts/sentinel_regen.py` for prompt-edit smoke-tests | scripts/sentinel_regen.py |
| **`pipeline_version` string** | `"3.10"` | `"4.0"` | run_persona_pipeline.py:1587 |

**Stable from v3.10:**
- 35-field assembled card schema + metadata block + 2 continuity nulls (Persona Card v2)
- Per-field register rule (first / second person, never third)
- 4-deployment-context JSONs at `PROJECT_ROOT` (conference_facts, audience_profile, panel_roster, council_config)
- `voice_mode` strict 3-enum {philosophical, observational, narratival}, null only for `subtype=system`
- Cross-model validator ladder (gpt-5.4 high → gpt-4.1 → o3 → gpt-4o → Gemini 2.5 Pro)
- Output Register rule + Boddice biocultural discipline

---

## What This Document Does

The Persona Pipeline takes a voice name and produces a completed Persona Card — all 35 generated fields populated, 2 continuity slots nulled (filled at runtime), metadata block stamped, three Derive artifacts written. The Persona Card is the pipeline's sole deliverable per voice. Everything downstream (Voice Pipeline, Provocateur Pipeline) consumes the card.

The Persona Card v2 spec defines WHAT each field contains and WHY it matters. This pipeline defines HOW each field is produced — which tool, which prompt, which validation, in which order.

---

## Output Register — First / Second Person, Never Third

Every field the pipeline produces is written in first person (as the voice) or second person (addressed to the voice). Never third person. Never scholarly description.

**Per-field register:**

| Register | Fields |
|---|---|
| **Second person** ("You are…", "Your reasoning…", "Do not…") | `epistemic_frame_statement`, `hard_limits`, `banned_language`, `banned_modes`, `knowledge_boundary`, `translation_protocol`, `topics_requiring_care`, `quality_criteria` |
| **First person** ("I hold that…", "I disagree by…") | `constitution`, `character`, `formative_experience`, `world`, `reasoning_method`, `disagreement_protocol`, `unique_contribution`, `bold_engagement_topics`, `default_questions`, `finds_compelling`, `resists`, `smoke_test_chains` |
| **Either** | `rhetorical_mode`, `characteristic_moves`, `register_and_tone`, `metaphorical_repertoire`, `preferred_vocabulary`, `concept_lexicon`, `curated_corpus_passages`, `medium`, `technical_capabilities`, `characteristic_output_structure`, `relationship_to_detailed_response`, `aesthetic_qualities`, `stance_tendency`, `length_and_format_constraints` |

**Read-aloud test:** if it sounds like a scholar describing someone, it's wrong; if it sounds like the person speaking or being spoken to, it's right.

**Why:** the v3.6 epistemic frame ("You are X") is ~80 tokens; the rest of the card is 10–15K tokens. Third-person field bulk overrides the second-person frame and produces "I think Plato would say..." instead of "I hold that...". Mock execution confirmed this. The register of the bulk determines the register of the output — the frame can't win alone. Enforced via `OUTPUT REGISTER` instruction in Block 2 (Guardrails) of every generation pass + Pass 7a register check + `_check_register()` in `run_persona_pipeline.py:1545`.

---

## Input

Each voice enters the pipeline with a `02_voice_config.json` produced by Pass 0a:

```json
{
  "name": "Plato",
  "type": "human",
  "subtype": null,
  "voice_mode": "philosophical",
  "hostile_sources": false,
  "corpus_constraint": "full",
  "needs_dr_supplement": true,
  "primary_text_sources": [],
  "wikipedia_url": "https://en.wikipedia.org/wiki/Plato",
  "casting_rationale": "(short Pass-0a-authored rationale)",
  "voice_specific_notes": "(optional)"
}
```

- **`name`** — display name; passed to Perplexity and Gemini for research.
- **`type`** ∈ {`human`, `non_human`, `fictional`}. Drives Pass 1a / Pass 1b / Pass 0b template selection.
- **`subtype`** — null for `human`/`fictional`. For `non_human`: `organism` (has neurons; e.g. octopus, whale) or `system` (no cognition; legal/cosmological/geographical entity, e.g. river with personhood, mountain).
- **`voice_mode`** ∈ {`philosophical`, `observational`, `narratival`}. Strict 3-enum; null permitted **only** when `subtype=system`. Enforced at `flows/shared/node0_validation.py:60`.
- **`hostile_sources`** (bool) — when `true`: Pass 1a separates `[hostile source]` / `[reconstruction]` / `[own voice]`; Pass 4a uses voice-construction priority ladder; Pass 7-pre flags hostile-sourced claims for extra scrutiny.
- **`corpus_constraint`** ∈ {`full`, `lyrics_patterns_only`, `hostile_read_against_grain`}. When not `full`: Pass 6 produces structural/thematic descriptions (lyrics) or reads against the grain (hostile).
- **`needs_dr_supplement`** (bool, default `true` since 2026-04-16) — kept for compat; runtime always-on.
- **`primary_text_sources`** — optional manual override. Empty triggers automatic URL extraction at Pass 1c-extract.
- **`wikipedia_url`** — set at Pass 0a (interactive picker or `--wiki URL`); used as grounding context.
- **`casting_rationale`** — short Pass-0a-authored "why this voice" string.

**Conference context** is loaded from `<PROJECT_ROOT>/conference_facts.json` and `<PROJECT_ROOT>/audience_profile.json` at runtime (FU#12-B); not stored per-voice.

---

## Architecture

Five principles:

1. **Multi-model.** Perplexity for cited factual research (90.24% citation accuracy). Gemini for cross-disciplinary breadth. Claude (Opus 4.7) for philosophical analysis, structured synthesis, voice replication. ChatGPT / Claude / Gemini ladder for cross-model validation. No single tool handles every dimension.
2. **Multi-pass.** Single-pass generation degrades quality after ~800–1000 words. Section-by-section generation with Coherence Threading compress between passes.
3. **Parallel across voices.** All voices run simultaneously; per-voice passes are sequential.
4. **Additive merge (v4).** Pass 1 is 6 chunk-passes that emit Pydantic-validated structured outputs; chunks are source of truth (1-arch-05 Part B); coherence is a narrow LLM audit, not a re-merge.
5. **Deterministic-where-possible.** Bracket-strip (Pass 6.5-clean), URL extraction (Pass 1c-extract), DR-prompt section split, FU#33 P2 INCONSISTENT merge, sentinel regen — all Python regex / pure logic. LLMs only where the work needs synthesis.

---

## The Pipeline at a Glance

| Phase | Pass | Tool | Script | Output |
|---|---|---|---|---|
| **0** Intake | 0a Voice Config | Opus 4.7 + adaptive thinking | run_pass0a_voice_config.py | `voices/<slug>/00_intake/02_voice_config.json` + `03_review_doc.md` |
| **0.5** Pre-DR research | 1a Perplexity dossier | Perplexity sonar-deep-research | run_phase0_1_research.py | `voices/<slug>/01_research/01_perplexity_dossier.json` |
| | 1b Gemini broad scan | Gemini 2.5 Pro | run_phase0_1_research.py (parallel ‖ 1a) | `02_gemini_broad_scan.json` |
| | 0b base render | Jinja2 (no LLM) | run_phase0_1_research.py | `03_dr_prompts/01_monolithic_dr_prompt.md` |
| | 0b tailor | Opus 4.7 + thinking (structured injections only) | run_pass0b_dr_prompt.py | tailored monolithic + `02_tailoring_notes.json` |
| | DR-split | Python | scripts/split_tailored_prompt.py | `03_dr_prompts/03_section_1_dr_prompt.md` … `08_section_6_dr_prompt.md` |
| **0.7** Manual gate | 6× Claude DR | claude.ai (manual) | — | `01_research/04_dr_dossier/01_section_1.md` … `06_section_6.md` |
| **1** Chunked merge | 1.1 BIOGRAPHICAL | Opus 4.7 + thinking | run_pass_1_all.py | `02_merge/pass_1_1/{life_scaffold, formative_candidates}.json` |
| | 1.2 INTELLECTUAL | Opus 4.7 + thinking | (parallel ‖ 1.1, max 3 concurrent) | `pass_1_2/{commitments, concepts, tensions, interpretive_frames}.json` |
| | 1.3 REASONING | Opus 4.7 + thinking | parallel | `pass_1_3/{reasoning_method, textures, analytical_context_reasoning}.json` |
| | 1.4 VOICE | Opus 4.7 + thinking | parallel | `pass_1_4/{moves, register, vocabulary, analytical_context_voice}.json` |
| | 1.5 BOUNDARIES | Opus 4.7 + thinking | parallel | `pass_1_5/{knowledge_boundary, sensitive_topics, hard_limits}.json` |
| | 1.6 CORPUS | Opus 4.7 + thinking | parallel | `pass_1_6/{works, passages, reference_only_passages}.json` |
| | 1.7 Coherence audit | Opus 4.7 + thinking (narrow) | run_pass_1_7.py (sequential after 1.1–1.6) | `02_merge/07_pass_1_7_coherence.json`, `08_merged_dossier.json` |
| **1.5** Corpus | 1c-extract | Python (regex, deterministic) | run_persona_pipeline.py | `03_corpus/00_primary_text_urls.json` |
| | 1c fetch | Python (SSRF-hardened) | run_persona_pipeline.py | `03_corpus/01_primary_texts.json` |
| | 1c REVIEW GATE | manual (touch flag) | — | `03_corpus/03_primary_texts_reviewed.flag` |
| | 1d Excerpt selection | Opus 4.7 + thinking, 60K char budget (FU#46) | run_persona_pipeline.py | `03_corpus/02_excerpt_selections.json` |
| **2** Generation | 2 Identity & Boundaries | Opus 4.7 + thinking, max 32K | run_persona_pipeline.py | `04_generation/01_pass_2_identity_boundaries.json` |
| | CT compress | Sonnet 4.6 + thinking, max 16K | (after each gen pass) | `_ct_after_pass_2.json` etc. |
| | 3 Intellectual Core | Opus 4.7 + thinking, max 32K | | `03_pass_3_intellectual_core.json` |
| | 4a Voice (corpus-grounded) | Opus 4.7 + thinking, max 24K | | `05_pass_4a_voice.json` |
| | 4b Artifact | Opus 4.7 + thinking, max 24K | | `07_pass_4b_artifact.json` |
| | 5 Engagement | Opus 4.7 + thinking, max 16K | | `09_pass_5_engagement.json` |
| | 6 Corpus Curation | Opus 4.7 + thinking, max 24K | | `10_pass_6_corpus.json` |
| **2.5** Clean | 6.5-clean (FU#33 P1) | Python (regex) | flows/shared/bracket_strip.py | rewrites `04_generation/*.json` in place |
| **3** Validation | 7-pre Stage 1 (extract claims) | Sonnet 4.6, max 32K | flows/shared/pass_7pre_chunked.py | claims list (in-memory) |
| | 7-pre Stage 2 (verify) | Sonnet 4.6 ×N parallel batches (~25 claims each) | parallel, max 4 workers | per-batch results |
| | 7-pre Stage 3 (boddice check) | Sonnet 4.6 (parallel ‖ Stage 2) | | boddice flags |
| | 7-pre aggregate | Python | | `05_validation/01_pass_7_pre_citation.json` |
| | 7-anachronism | gpt-5.4 high → fallbacks, max 16K | run_persona_pipeline.py | `02_pass_7_anachronism.json` |
| | 7a Cross-Model | gpt-5.4 high → fallbacks, max 16K | merges 7-anachronism + FU#33 P2 INCONSISTENT into `field_issues` | `03_pass_7a_cross_model.json` |
| | 7a-FIX (if `REVISION_NEEDED`) | Opus 4.7 + thinking, max 32K (FU#13 patcher) | linear; FU#5 snapshots `_snapshots/pre_fix_pass/` | `02_merge/_fix_log.json` + re-fires validators once |
| | 7b Worked Provocations | Opus 4.7 + thinking, max 24K | | `04_pass_7b_smoke_test.json` |
| | 7c Negative Constraints | Gemini 2.5 Pro → Sonnet 4.6 fallback, max 16K/8K | overwrites `banned_language` + `banned_modes` from 4a seeds | `05_pass_7c_negative.json` |
| **4** Derive | Derive | Opus 4.7 + thinking, max 24K | | `06_derive/{00_derive_raw, 01_provocateur_profile, 02_evaluation_rubric}.json` |
| **4b** Chat artifact | Chat builder (FU#41) | Python | flows/shared/chat_prompt_builder.py | `06_derive/03_chat_system_prompt.json` |
| **5** Card assembly | — | Python | run_persona_pipeline.py:1583–1681 | `07_persona_card_assembled.json` |
| **6** Triage | CARD COMPLETE summary (FU#7) | Python | run_persona_pipeline.py:1702–1838 | stdout |

**Per-voice cost:** ~$18–22 (excluding the 6 manual claude.ai DR sessions). **Wall time:** ~2 hours after DR dossier complete.

---

## Phase 0: Intake

**Pass 0a — Voice Config.** `run_pass0a_voice_config.py "Voice Name" [--wiki URL] [--hint TEXT] [--project PATH]`. Opus 4.7 + adaptive thinking. Reads `conference_facts.json` + `panel_roster.json` for context. Pre-hook: Wikipedia search via API + interactive picker (or `--wiki URL` direct, or `--hint TEXT` fallback for voices without a Wikipedia match). Output: `02_voice_config.json` (validated against `schemas/voice_config.py`) + `03_review_doc.md`. Validation retries once on `InputRejected.reason` with critique appended; specific failed field name + value logged.

**Operator gate.** The review doc is the human-review surface. Each ends with `✍ CURATOR ACTION REQUIRED` for `editorial_rationale` fill-in. Optional — Phase 0.5 runs without it. **Do NOT hand-author voice configs bypassing Pass 0a** — Pass 0a is operator-trusted (CURRENT_STATE §5.26); if review disagrees, edit and re-run Pass 0a.

---

## Phase 0.5: Pre-DR Research

**Script:** `run_phase0_1_research.py`. **Wall time:** 5–10 min per voice.

**Pass 1a — Perplexity dossier.** `sonar-deep-research`. System prompt: one of `persona_pass_1a_{human, fictional, non_human_organism, non_human_system}.md`, selected by `type`. Hostile-source appendix injected when `hostile_sources=true`. Output: `01_perplexity_dossier.json` (6-section structured dossier — auto-split via `flows/shared/perplexity_split.py` into per-section dict for downstream chunk passes).

**Pass 1b — Gemini broad scan.** Gemini 2.5 Pro. System prompt: one of `persona_pass_1b_{human, fictional, non_human_organism, non_human_system}.md`. Cross-disciplinary breadth, NOT sectioned (passed in full to every chunk pass). Output: `02_gemini_broad_scan.json`.

Pass 1a + Pass 1b run in parallel via `ThreadPoolExecutor`.

**Pass 0b — DR prompt assembly.** Two-stage:

1. **Base render** (`pass_0b_header.md` + type-specific body `pass_0b_{human, fictional, non_human_organism, non_human_system}.md` + `pass_0b_footer.md` + research-discipline include `_pass_0b_research_discipline.md`). Pure Jinja, no LLM. Conditional blocks: hostile-source appendix, `lyrics_patterns_only` constraint, system-entity grounding.
2. **Tailor** (`run_pass0b_dr_prompt.py`, prompt `pass_0b_tailor.md`). Opus 4.7 + thinking. **Structured injections only** — splices voice-specific guidance into the monolithic prompt at marked sections (PB#2 base preservation enforced architecturally per `pass_0b_tailor.py`); does NOT full-rewrite. Outputs tailored monolithic + `02_tailoring_notes.json`.
3. **Split** (`scripts/split_tailored_prompt.py`). Splits the tailored monolithic into 6 per-section prompts. `02_tailoring_notes.json` + 6 section files in `03_dr_prompts/`.

**Operator gate (manual claude.ai DR).** 6 sessions per voice on claude.ai with Extended Thinking + Deep Research:
- §1–§5: **Opus 4.6**
- §6: **Opus 4.7** (Phase L empirical: 4.6 produces reader's-intro on §6; 4.7 required)

Per-section runtime: 20–60 min wall. If past 60 min without draft streaming, cancel + retry. Save each as `01_research/04_dr_dossier/0N_section_N.md`.

**DR mode detection** (`flows/shared/chunk_runner.py:74–98`): per-section files → `per_section`; falls back to `07_concat_claude_dr.md` → `monolithic`; errors on partial state.

---

## Phase 1: Chunked Merge (Pass 1.1–1.7)

**This is the v4 architectural shift** (CURRENT_STATE §5.18, "1-arch" decisions 04–08). Replaced v3.10's monolithic Pass 1-merge.

**Per-chunk runner:** `flows/shared/chunk_runner.py:run_chunk()`.
- Model: Opus 4.7 + adaptive thinking, `max_tokens=48000`.
- System prompt: `pass_1_N_merge.md` for N ∈ {1,2,3,4,5,6}.
- Inputs: relevant Perplexity section (auto-split) + full Gemini scan + per-section Claude DR dossier file (or monolithic fallback).
- Output: Pydantic-validated structured JSON (per-chunk schema in `schemas/pass_1_N.py`).
- Retries: 1 retry on `ValidationError` with critique; transient-error retries on network.
- Writes: per-key JSONs under `02_merge/pass_1_N/<key>.json` (e.g. `pass_1_1/life_scaffold.json`, `pass_1_1/formative_candidates.json`).

**Parallelism:** `run_pass_1_all.py` runs 1.1–1.6 in parallel (`max_parallel=3` default).

**Pass 1.1 BIOGRAPHICAL** → `LifeScaffold` + `FormativeCandidate[]`. Note: `LifeScaffold.anachronisms_to_avoid` removed under 1-arch-08; anachronism discipline now lives at `KnowledgeBoundary.anachronism_discipline[]` (Pass 1.5).

**Pass 1.2 INTELLECTUAL** → `Commitment[]` + `Concept[]` + `Tension[]` + **`InterpretiveFrame[]`** (top-level container, 1-arch-06; `frame_type` discriminator: `interpretive_method` / `cross_disciplinary_reframing` / `voice_level_debate` — cross-cuts chunk boundaries).

**Pass 1.3 REASONING** → `ReasoningMethod` (≥5 steps, uncapped) + `Textures` (finds_compelling, resists) + `AnalyticalContext` (1-arch-04: structural_patterns, worked_demonstrations, scholarly_debates).

**Pass 1.4 VOICE** → `Moves[]` + `Register` (rhetorical_mode, register_and_tone, tradition_note) + `Vocabulary` (preferred_vocabulary, metaphorical_repertoire) + `AnalyticalContext` (optional).

**Pass 1.5 BOUNDARIES** → `KnowledgeBoundary` (with `anachronism_discipline[]` per 1-arch-08, dual framings per entry) + `SensitiveTopics` + `HardLimits`.

**Pass 1.6 CORPUS** → `Works[]` + `Passages[]` + `ReferenceOnlyPassages` (with `runtime_contract_note` carried inline). `URLs` chunk REMOVED under 1-arch-07; URLs derived deterministically by `flows/shared/url_extract.py` at render time.

**Pass 1.7 Coherence audit (NARROW).** Sequential after 1.1–1.6. Three stages:
- Stage A (Python): compose audit prompt from 6 chunks.
- Stage B (Opus 4.7 + thinking, max 24K): emits `CoherenceAuditResult` with `coherence_flags[]` + `coherence_resolutions[]` + `edits[]` (each edit = `{path, op: append|set, value, rationale}`).
- Stage C (Python): `apply_edits_to_chunks()` writes patches into per-key chunk JSONs. **Chunks are source of truth** (1-arch-05 Part B); `08_merged_dossier.json` is convenience snapshot rebuilt from chunks.

**MergedDossier alias gotcha (FU#22):** schema field is `voice_register` (Python attr) aliased to JSON key `register` (Pydantic `register()` method shadow). All consumers use dict-key access `merged_dossier["register"]`, not attribute access. Audit-clean as of 2026-04-26.

---

## Phase 1.5: Corpus assembly

**Pass 1c-extract** (deterministic, no LLM). `flows/shared/url_extract.py:extract_urls()` walks `passages[].citation` + `works[]` for primary-text URLs (Gutenberg landing pages canonicalized to raw text). Output: `03_corpus/00_primary_text_urls.json`. Skipped if `voice_config.primary_text_sources` populated (manual override).

**Pass 1c fetch.** `flows/shared/node1c_fetch.fetch_all()`. SSRF-hardened: scheme restriction (http/https only), RFC1918 block, 5 MB cap. Output: `03_corpus/01_primary_texts.json`. Skipped if no URLs.

**Pass 1c REVIEW GATE.** `sys.exit()` if `03_primary_texts_reviewed.flag` doesn't exist. Writes `04_primary_texts_review.md` with fetch results + operator instructions.

**Pass 1d — Excerpt Selection.** Opus 4.7 + thinking, `max_tokens=16000`. Prompt: `persona_pass_1d_excerpt_selection.md`. **60K char budget** (FU#46 raised from 30K for richer-corpus voices). Inputs: `build_structural_index()` of fetch results + chunk vars (passages, works, reasoning_method_chunk, register, moves). Output: `03_corpus/02_excerpt_selections.json`. SKIPPED if no primary texts (emits SKIPPED status + sets `voice_basis="training-data"`).

**Pass 1d runs late** (after Pass 3 CT compress in code order, before Pass 4a) so the excerpt selection benefits from the compressed Pass 2+3 reasoning summary.

---

## Phase 2: Section-by-Section Generation

Each generation pass uses Opus 4.7 + adaptive thinking. System + user prompt files per pass. CT compress (Sonnet 4.6 + thinking, max 16K) after each pass; CT output feeds the next pass's `pass_N_summary` user-prompt variable.

### Pass 2 — Identity & Boundaries

- **System:** `persona_pass_2_identity_boundaries.md` (599 lines). Template vars: `name`, `type`, `subtype`, `voice_mode`, `hostile_sources`.
- **User:** `persona_pass_2_user.md` (61 lines).
- **Inputs (per-chunk vars from 1-arch-05 Part A):** `life_scaffold`, `formative_candidates`, `knowledge_boundary_chunk`, `sensitive_topics`, `hard_limits_chunk`, `voice_level_debate_frames`.
- **Outputs (canonical card fields produced):** `world`, `epistemic_frame_statement`, `translation_protocol`, `topics_requiring_care`, `knowledge_boundary`, `hard_limits`, `voice_temporal_stance`, `council_member_name`, `formative_experience`, `character`.
- **FU#49 universal patterns landed here:** structural-strain licensing in `epistemic_frame_statement` (49H); two-aporia-distinction in `translation_protocol` (49I); phenomena-outside-corpus universal entry in `topics_requiring_care` (49J); **Position B corpus-accurate softening** in `hard_limits` field-spec preamble (49D — forbids framework-ABANDONMENT, not corpus-internal CROSS-EXAMINATION).
- `max_tokens=32000`, `temperature=1.0`.

### Pass 3 — Intellectual Core

- **System:** `persona_pass_3_intellectual_core.md` (232 lines). **User:** `persona_pass_3_user.md` (70 lines).
- **Per-chunk inputs:** `commitments`, `concepts`, `tensions`, **full `interpretive_frames[]`** (1-arch-06), `reasoning_method_chunk`, `textures`, `analytical_context_reasoning` + `pass_2_summary`.
- **Outputs:** `constitution`, `concept_lexicon`, `reasoning_method`, `finds_compelling`, `resists`.
- **Evidence tagging:** `[ontological] / [epistemological] / [ethical-political]` for philosophical voices; `[indigenous_law] / [legal_framework]` for system entities; `[hostile_source] / [reconstruction] / [own_voice]` for hostile-source voices; `[attributed_by_narrative_function]` for fictional.
- `max_tokens=32000`.

### Pass 4a — Voice (corpus-grounded)

- **System:** `persona_pass_4a_voice.md` (243 lines). **User:** `persona_pass_4a_user.md` (67 lines).
- **Per-chunk inputs:** `moves`, `register`, `vocabulary`, `analytical_context_voice`, `available_pathe`, `reasoning_method_summary`, `cross_disciplinary_frames` + `primary_block` (from Pass 1d) + `pass_2_3_summary`.
- **Outputs:** `rhetorical_mode`, `characteristic_moves`, `register_and_tone`, `metaphorical_repertoire`, `preferred_vocabulary`, `banned_language` (seed; refined by 7c), `banned_modes` (seed; refined by 7c).
- Sets `voice_basis = "corpus-based"` if Pass 1d produced excerpts, else `"training-data"`.
- `max_tokens=24000`.

### Pass 4b — Artifact

- **System:** `persona_pass_4b_artifact.md` (207 lines). **User:** `persona_pass_4b_user.md` (16 lines).
- **Inputs:** `pass_2_3_4a_summary` + `rhetorical_mode`, `characteristic_moves`, `register_and_tone` from Pass 4a.
- **Outputs:** `medium`, `characteristic_output_structure`, `length_and_format_constraints`, `technical_capabilities`, `relationship_to_detailed_response`, `aesthetic_qualities`, `stance_tendency`, `quality_criteria`.
- **FU#49A landed here:** generativity-permitting prompt + `length_and_format_constraints` variance 350–1500. **FU#49J landed here:** don't-silently-complete-incomplete-translation universal entry.
- `max_tokens=24000`.

### Pass 5 — Engagement

- **System:** `persona_pass_5_engagement.md` (141 lines). **User:** `persona_pass_5_user.md` (48 lines).
- **Inputs:** `pass_2_3_4_summary` + `constitution`, `reasoning_method` from Pass 3 + **deployment priming** from `conference_facts.json` + `audience_profile.json` (FU#12-B).
- **Outputs:** `bold_engagement_topics`, `default_questions`, `disagreement_protocol`, `unique_contribution`.
- **FU#49K landed here:** premature-closure-of-either-kind in `banned_modes`; 5 fidelity + 2 generativity `quality_criteria`; framework-strain closer in `unique_contribution`.
- `max_tokens=16000`.

### Pass 6 — Corpus Curation

- **System:** `persona_pass_6_corpus.md` (124 lines). **User:** `persona_pass_6_user.md` (59 lines).
- **Inputs:** `primary_block` + `works`, `passages`, `reference_only_passages` (chunk 1.6) + `pass_2_3_4a_summary` + `constitution`, `concept_lexicon`, `reasoning_method` (Pass 3) + `rhetorical_mode`, `characteristic_moves`, `register_and_tone` (Pass 4a).
- **Output:** `curated_corpus_passages` (single field — 5–10 curated passages with contextual headers).
- **HALTED if no primary texts** — writes BLOCKED sentinel to fields. (Pass 4a degrades gracefully without primary texts; Pass 6 halts.)
- **`corpus_constraint=lyrics_patterns_only` variant:** structural/thematic descriptions, NO actual lyrics.
- `max_tokens=24000`.

### Coherence Threading (CT)

After each generation pass: Sonnet 4.6 + thinking, `max_tokens=16000`. Compresses completed fields into a summary string for the next pass. Files: `02_ct_after_pass_2.json`, `04_ct_after_pass_3.json`, `06_ct_after_pass_4a.json`, `08_ct_after_pass_4b.json`. Prompt: `persona_coherence_threading.md` (17 lines).

---

## Phase 2.5: Pass 6.5-clean (FU#33 P1)

**Script:** `flows/shared/bracket_strip.py:strip_chunks_in_place()`. No LLM. Runs after Pass 6, before Pass 7-pre.

**Strips** (deterministic regex on `04_generation/*.json`): `[ontological]`, `[epistemological]`, `[ethical-political]` / `[ethical_political]`, `[unique]`, `[metaphysical]`, `[psychological]`, `[political]`, `[aesthetic]`, `[cosmological]`, `[epistemic]`, `[ethical]`, `[stated]`, `[scholarly_consensus]`, `[inference]`, `[contested]`, `[curator_note]` / `[curator-note]`, `[pedagogical_note]`, `[editorial_note]`.

**PRESERVES:** `[experiential_reconstruction]`, `[projection_warning: ...]` — Boddice biocultural tags that Pass 7-pre Stage 3 looks for.

If files touched: reloads pass2–pass6 from disk into in-memory vars. Placement before validators ensures reports reflect shipped state.

---

## Phase 3: Validation & Testing

### Pass 7-pre — Citation Verification (FU#2 chunked)

`flows/shared/pass_7pre_chunked.run_chunked_pass_7pre()`. Replaces single-shot Sonnet (which hit 128K output ceiling on rich cards). 3 stages:

**Stage 1: Extract claims.** `persona_pass_7pre_extract.md` + `_user.md`. Sonnet 4.6, `temperature=0.0`, `max_tokens=32000`. Emits verifiable-claim items list.

**Stage 2: Verify claim batches.** `persona_pass_7pre_verify_batch.md` + `_user.md`. Sonnet 4.6, `temperature=0.0`, `max_tokens=16000`. **N parallel batches (~25 claims each), max 4 workers.** 1 retry on transient JSON failures. Inputs per batch: claim batch + `01_primary_texts.json` + Perplexity dossier.

**Stage 3: Boddice tag check.** `persona_pass_7pre_boddice_check.md` + `_user.md`. Sonnet 4.6, `temperature=0.0`, `max_tokens=8000`. **Parallel with Stage 2.** Verifies Boddice biocultural tags survived Pass 6.5-clean.

**Aggregate** (Python): unions Stage 2 + Stage 3 results into final report. Output: `05_validation/01_pass_7_pre_citation.json`. **On any-stage failure:** writes `VERIFICATION_SKIPPED` sentinel.

**Orphaned files:** `persona_pass_7pre_citation.md` and `persona_pass_7pre_citation_user.md` are the legacy single-shot prompts — superseded by FU#2 3-stage architecture, kept on disk but not called anywhere. Eligible for deletion.

### Pass 7-anachronism — TimeChara temporal check

System: `persona_pass_7_anachronism.md` (94 lines). User: inline.

**Model ladder:** gpt-5.4 (`reasoning_effort="high"`) → gpt-4.1 → o3 → gpt-4o → Gemini 2.5 Pro. `max_tokens=16384`, `temperature=0.0`. On all-fail: writes SKIPPED sentinel.

**Output:** `02_pass_7_anachronism.json` with `anachronism_flags[]` (each: `category`, `field_path`, `problematic_text`, `reason`, `suggested_fix`, `severity`) + `overall ∈ {PASS, REVISION_NEEDED}`.

**Post-hook (`run_persona_pipeline.py:980–1011`):** if `overall == REVISION_NEEDED`, merges `anachronism_flags` as `field_issues` into Pass 7a result with field-path → pass mapping; escalates 7a `overall` to REVISION_NEEDED if not already.

### Pass 7a — Cross-Model Validation

System: `persona_pass_7a_cross_model.md` (74 lines). User: `persona_pass_7a_cross_model_user.md` (5 lines, renders card as JSON).

**Model ladder:** same as 7-anachronism. `max_tokens=16384`, `temperature=0.0`.

**Output:** `03_pass_7a_cross_model.json` with `field_issues[]` + `overall` + `revision_target_passes`.

**FU#33 P2 INCONSISTENT merge** (`run_persona_pipeline.py:1013–1078`): finds INCONSISTENT items from Pass 7-pre, maps field paths to passes, injects into 7a `field_issues`. Path-to-pass mapping covers passes 2/3/4a/4b/5/6.

### Pass 7a-FIX — Linear patcher (FU#13)

Fires only if `pass7a.result.overall == REVISION_NEEDED` AND `_fix_log.json` doesn't exist (idempotent).

**Pre-hook (FU#5):** snapshots `04_generation/` + `05_validation/` → `04_generation/_snapshots/pre_fix_pass/`.

System: `persona_pass_7a_fix.md` (147 lines). User: `persona_pass_7a_fix_user.md` (47 lines). Renders `field_issues`, `relevant_pass_outputs`, voice context (`rhetorical_mode`, `register_and_tone`, `characteristic_moves`, `translation_protocol`, `knowledge_boundary` — for FU#44 register-drift + internal-contradiction guardrails).

**Model:** Opus 4.7 + thinking, `max_tokens=32000`, `temperature=1.0`. **Single call** — not a loop.

`flows/shared/patch_walker.apply_patch_in_place()` applies each patch (`{pass_id, field_path, new_value, rationale}`) to in-memory dict + writes cache file.

After applying patches: invalidates pass7pre/7anach/7a/7b/7c/derive_raw/assembled_card/provocateur/rubric caches; **re-fires validators once** (Pass 7-pre, 7-anachronism, 7a). Fix log: `02_merge/_fix_log.json`.

**Cost:** ~$1 per voice vs ~$5–10 per loop in v3.10 surgical revision. **Why it works better than the v3.10 loop:** writer Opus + thinking + critique tends to expand rather than trim; surgical patches operate on field paths only, no rewriter context.

### Pass 7b — Worked Provocations

Opus 4.7 + thinking, `max_tokens=24000`, `temperature=1.0`. System: `persona_pass_7b_smoke_test.md` (88 lines, template vars: `conference_context`, `voice_mode`, `subtype`). User: `persona_pass_7b_smoke_test_user.md` (6 lines).

Output: `04_pass_7b_smoke_test.json` (`smoke_test_chains` field — 3–5 provocation→response chains).

**`smoke_test_chains` is build-time diagnostic, NOT runtime few-shot.** See `personas/HANDOFF.md` §"CRITICAL: do NOT few-shot from `smoke_test_chains`" for the load-bearing rule. The chains exist as evidence the card was working at build time + as input to Pass 7c. Loading them as Step 1 few-shots collapses voice range and re-introduces failures Pass 7c removes.

### Pass 7c — Negative Constraints

System: `persona_pass_7c_negative.md` (102 lines, parameterized by `claude_fallback` bool). User: `persona_pass_7c_negative_user.md` (21 lines).

**Primary:** Gemini 2.5 Pro, `temperature=0.0`, `max_tokens=16384`.
**Fallback:** Sonnet 4.6 with bias-aware variant, `temperature=0.0`, `max_tokens=8192`, `thinking=False`.

**Inputs:** `rhetorical_mode`, `characteristic_moves`, `register_and_tone`, `banned_language`/`banned_modes` (Pass 4a seeds), `smoke_test_chains` (from Pass 7b).

**Output:** `05_pass_7c_negative.json`. **Overwrites** `banned_language` + `banned_modes` from Pass 4a seeds with refined lists. Why Gemini primary: cross-model bias check catches Claude-specific phrasings Claude itself wouldn't flag.

---

## Phase 4: Derived Outputs

### Derive — Provocateur Profile + Evaluation Rubric

Opus 4.7 + thinking, `max_tokens=24000`, `temperature=1.0`. System: `persona_derive.md` (100 lines). User: `persona_derive_user.md` (6 lines).

Emits:
- **`provocateur_profile`** (8 fields): `speaks_from`, `core_commitment`, `activates_on`, `goes_flat_on`, `stretch`, `translation_range`, `stance_tendency`, `medium`. Wired to `runtime/flows/shared/council/council_config.json` `members[]`.
- **`evaluation_rubric`** (9 test prompts): 3 identity + 3 reasoning + 3 stress.

Files: `06_derive/{00_derive_raw, 01_provocateur_profile, 02_evaluation_rubric}.json`.

### Chat artifact (FU#41, 4th Derive output)

`flows/shared/chat_prompt_builder.py:write_chat_system_prompt()`. Pure Python — no LLM. After CARD COMPLETE.

**Strips 11 items** from assembled card:
- **Amendment A — chat-incompatible (5 top-level):** `metadata`, `smoke_test_chains`, `reference_only_passages`, `continuity_block_if_night_2`, `continuity_block_artifact_if_night_2`.
- **Amendment B — spec-shell meta (5 top-level):** `voice_name`, `voice_mode`, `pipeline_version`, `generated_date`, `council_member_name`.
- **1 nested:** `curated_corpus_passages.corpus_metadata` (parent preserved with `passages[]` intact).

Output: `06_derive/03_chat_system_prompt.json`. Operator paste-target for Claude project custom instructions or Claude API system prompt for chat-native deployments. **NOT consumed by Provocateur Pipeline or Voice Pipeline.**

---

## Phase 5: Cross-Persona Quality Control

**Status: scaffolded** (`personas/phase_5_cross_persona_qc.py`, ~487 lines). **Not run** — needs all 12 athens-2026 cards.

Three batch tests:
1. **Swap test** — shuffle constitution principles across 12 voices; can an evaluator attribute each? Misattributed → too generic.
2. **Blind identification** — strip names from `character` + `register_and_tone`, shuffle, can evaluator identify?
3. **Same-question distinctiveness** — run all voices through one provocation, compare for style/metaphor/values similarity.

Tool: ChatGPT (cross-model from Claude-generated cards). Runs last in the pipeline sequence per project.

---

## Card Assembly

`run_persona_pipeline.py:1583–1681`. Composes assembled card from completed pass outputs:

```
{
  "voice_name":         (from voice_config),
  "voice_mode":         (from voice_config),
  "pipeline_version":   "4.0",
  "generated_date":     (today),

  ...35 generated card fields, flat at root (from Pass 2/3/4a/4b/5/6/7b/7c)...,

  "reference_only_passages": (from chunk 1.6, with runtime_contract_note),
  "continuity_block_if_night_2": null,
  "continuity_block_artifact_if_night_2": null,

  "metadata": {
    "passes_completed":    [...],
    "validation_status":   "PASS" | "REVISION_NEEDED",
    "fix_pass_log":        (FU#13 patcher log; replaces v3.10 revision_loops),
    "tools_used":          [...],
    "voice_basis":         "corpus-based" | "training-data",
    "hostile_sources":     bool,
    "corpus_constraint":   str,
    "subtype":             str | null,
    "deployment_context":  (full conference_context used in Pass 7b),
    "human_review_status": "pending",
    "approach_c":          true if Claude DR dossier present,
    "citation_verification": (Pass 7-pre summary),
    "cross_model_validation": (Pass 7a summary),
    "negative_constraints_refinement": (Pass 7c summary),
    "smoke_test_chains_role": "build-time diagnostic — NOT runtime few-shot",
    "field_counts":        {...},
    "register_violations": [...]
  }
}
```

**Note on field count.** v3.10 spec said "35 generated fields"; in practice the LLM may emit additional sub-fields per voice. Code stamps actual count at runtime: `f"Total card fields: {len(full_card)}"`. The 35-field claim is the **target**, not a strict invariant.

---

## CARD COMPLETE summary (FU#7 operator triage)

`run_persona_pipeline.py:1702–1838`. Pure Python. Emits to stdout:
- Register-violations check (`_check_register()` — scans for `<voice>'s` and "<voice> would" patterns; `_LAST_NAME_OVERRIDES` dict at line 1545 handles non-human special cases like Octopus = skip).
- Top concerns severity-ordered list (anachronism, register, INCONSISTENT, citation gaps).
- Recommended next action string.

---

## Non-Human Voice Methodology

The non-human branches (`type=non_human`, `subtype ∈ {organism, system}`) modify multiple passes:

- **Pass 0a** — type-specific voice config schema (`null` voice_mode for `subtype=system`).
- **Pass 1a/1b** — non-human research prompts (`persona_pass_1a_non_human_organism.md` / `_non_human_system.md`); biology + ecology focus for organisms; legal/cosmological framework for systems.
- **Pass 0b** — type-specific body templates; system-entity grounding via indigenous law / legal framework.
- **Pass 1.X** — chunk schemas accept null `formative_emotional_community` (use `condition_of_being` instead).
- **Pass 2** — non-human variant of `epistemic_frame_statement` ("you are a human construction attempting to imagine..."); for systems: triple-honest framing (entity → indigenous cosmology → legal framework → AI simulation).
- **Pass 3** — system-entity constitutions tagged `[indigenous_law]` / `[legal_framework]`.
- **Pass 4a** — non-human voice variants: organism = ecological/cognitive grounding + anti-anthropomorphisation guardrails (no cognitive vocabulary); system = relational/cosmological/legal grounding + bans ALL cognitive vocabulary; voice from relationship, not entity.
- **Pass 5** — system-entity engagement is relational, not perceptual; provocations framed as pressures on the relationship; responses expressed through entity condition.
- **Pass 7b** — non-human worked provocations grounded in body/system, not propositions.

**Anti-anthropomorphisation guardrails** (Pass 4a Block 2 + Pass 7c bias-aware fallback):
- No human-cultural references as "familiar."
- No moral positions in organism mode.
- No sentimentalising mortality.
- No "we" in solitary organisms.
- For systems: silence-as-honest where concept has no physical/ecological dimension.

---

## Cross-Repo Handoff

The pipeline's runtime contract to the Voice Pipeline + Provocateur Pipeline is documented in **`personas/HANDOFF.md`**. Summary:

- **Provocateur Profile** (8 fields) → `runtime/flows/shared/council/council_config.json` `members[]`. Currently dev_stub_v3_audience_sharpened; replaced as athens-2026 cards complete.
- **Persona Card** (35 fields + 2 continuity nulls + metadata) → loaded as Voice Pipeline system prompt. Runtime MUST drop `metadata` and `smoke_test_chains` before assembly.
- **`reference_only_passages`** is loaded into Step 1 ONLY — Step 2 MUST drop it before assembling its system prompt (copyright exposure for musical/copyright-sensitive voices).
- **Chat artifact** is a separate artifact for operator paste into Claude projects — NOT consumed by runtime pipelines.

---

## Sentinel Regen pattern (FU#29)

For prompt edits that risk silently changing card outputs across all voices.

**Workflow:**
1. **Snapshot pre-edit voice:** `<baseline-snapshot-dir>/<voice_slug>/<filename>` (e.g. `_workspace/sentinel_baselines/2026-04-27-pre-49D/plato/01_pass_2_identity_boundaries.json`).
2. Make prompt edit.
3. **Regen:** `python scripts/sentinel_regen.py regen --pass <PASS_NAME> --voices <slug> --baseline-snapshot <DIR>`.
4. Inspect diff. Validate intended pattern surfaced.
5. Restore voice baseline post-validation if it was a smoke-test (not a real generation).

5 sentinel runs landed FU#49H/I/J/K/D this week. Per-voice baseline subdir support landed in FU#50(2).

---

## Cost & Envelope

| Stage | Per-voice cost |
|---|---|
| Pass 0a + Phase 0.5 | ~$2–4 (Perplexity dominates; Gemini cheap; Opus 4.7 thinking on Pass 0a/Pass 0b tailor) |
| Manual claude.ai DR | $0 (counts against operator's claude.ai subscription, not API) |
| Pass 1.1–1.7 chunked merge | ~$5–7 (6 Opus + thinking calls in parallel + 1 narrow audit) |
| Pass 1c-extract / 1c / 1c-review | ~$0 (deterministic + manual gate) |
| Pass 1d | ~$1 (Opus + thinking, 60K char budget) |
| Pass 2/3/4a/4b/5/6 + CT | ~$6–8 |
| Pass 6.5-clean | $0 (deterministic) |
| Pass 7-pre 3-stage | ~$1 (Sonnet, parallel batches) |
| Pass 7-anachronism | ~$0.50 (gpt-5.4 high) |
| Pass 7a | ~$0.50 |
| Pass 7a-FIX (if fires) | ~$1 (replaces ~$5–10 v3.10 revision loop) |
| Pass 7b | ~$1 |
| Pass 7c | ~$0.30 |
| Derive | ~$1 |
| Chat artifact + assembly + summary | $0 |
| **Total** | **~$18–22 per voice** |

**Wall time:** ~2 hours after 6×DR dossier complete (excluding manual claude.ai sessions which run human-in-the-loop, ~60–180 min per section).

For 12 athens-2026 voices: **~$215–265 in API + ~$0 in claude.ai overhead**. Plus operator wall time for 11 × 6 = 66 manual DR sessions.

---

## Constraints

- **Multi-model.** Single-vendor isn't sufficient: Perplexity for citation accuracy, Gemini for breadth, Claude for synthesis, GPT/Gemini for cross-model validation.
- **Output quality ceiling for `corpus_constraint=lyrics_patterns_only`** is lower than for corpus-based voices — Pass 6 produces pattern descriptions only, no actual lyrics.
- **Output quality ceiling for `voice_basis=training-data`** (Pass 1d skipped) is lower than corpus-based — voice grounded in model's training, not the figure's actual words.
- **Hostile-source voices** require operator scrutiny — pipeline modifies multiple passes (Pass 1a appendix, Pass 4a priority ladder, Pass 7-pre extra scrutiny) but cannot fully replace scholarly judgment.
- **`subtype=system` voices** are honest-construction — pipeline cannot produce a "voice" in the cognitive-agent sense; output is voice from relationship, mediated through indigenous law / legal framework.

---

## Scope

**This pipeline produces** the persona card, the provocateur profile, the evaluation rubric, and the chat artifact — per voice, pre-conference.

**Out of scope:**
- Voice Pipeline runtime — see `docs/AI_Assembly_Voice_Pipeline.md`.
- Provocateur Pipeline runtime — see `docs/AI_Assembly_Provocateur_Pipeline.md`.
- Researcher Pipeline runtime — see `docs/AI_Assembly_Researcher_Pipeline.md`.
- Closing-show pipelines — unspecified.
- Microsite / admin console / downstream Render-Publish-Curate-Deliver — unspecified or unbuilt.

---

## See also

- `docs/AI_Assembly_Persona_Card_v2.md` — 35-field schema + per-field "Therefore" + register rule, with v2.1 amendments section (2026-04-27).
- `docs/CURRENT_STATE.md` — gap analysis + architectural rationale (§5.16–5.28 cover what changed since v3.10).
- `personas/HANDOFF.md` — cross-repo runtime contract.
- `_workspace/planning/FOLLOW_UPS.md` — active follow-up tracker.
- `_workspace/planning/HANDOFF_2026_04_27.md` — current session pickup.
- `docs/_archive/AI_Assembly_Persona_Pipeline_v3_10.md` — preceding spec (historical).

---

*End of v4.0 spec. Reflects current implementation as of 2026-04-27. When the implementation drifts: update this doc and `CURRENT_STATE.md` together.*
