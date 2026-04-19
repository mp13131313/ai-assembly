# Architecture — Next Phase Handoff

**Status:** Phase A cleanup complete. Phase B (chunked Pass 1 merge architecture) not yet started.
**Date:** 2026-04-18

This document captures the architectural decisions reached in the 2026-04-17/18 design conversation that took the persona pipeline from rigid-6-section-markdown to chunked-structured-JSON. **Read this before resuming architecture work.**

---

## Where Phase A left things

- **Fix #34** (extraction-shaped DR prompt bullets, all 3 type branches: human / non-human organism+system / fictional) is in `main`.
- **Phase 0a + Phase 0.5** work end-to-end: voice config → Perplexity sonar-deep-research + Gemini broad-scan in parallel → Jinja-render → Claude DR prompt file (manual paste into claude.ai). Verified on Ibn Battuta.
- **Pass 1** (merge of DR sources into canonical persona dossier) is unbuilt.
- **Pass 2+** (persona card extraction, verification, runtime feed) is unbuilt.
- **Existing voice configs:** Plato, Cleopatra, Hannah Arendt, Octopus, Ibn Battuta. 7 voices still to build.

---

## Architectural decisions (binding for next session)

These were debated and committed in the design conversation. Do not re-litigate without explicit reason.

1. **Drop ChatGPT Deep Research.** Three research sources only: Perplexity sonar-deep-research (factual grounding) + Claude DR (voice/character extraction) + Gemini broad-scan (cross-disciplinary). File 2's 3-way DR cross-verification dropped in favor of simpler architecture. Quality delta from 3→4 sources judged not worth API/manual-paste burden.

2. **Hybrid Jinja + LLM tailoring** for the Claude DR prompt render (replaces pure Jinja). Scope is **Balanced**:
   - Jinja produces deterministic scaffold (RESEARCH INTEGRITY, conditional appendices, card-field annotations, section headings, hostile-sources/corpus-constraint blocks).
   - LLM tailoring pass customizes per-voice: illustrative figure examples (Augustine→al-Ghazali for Battuta), SWAP TEST anchors, emphasis redirect based on Perplexity coverage, optional pruning of clearly-inapplicable bullets.
   - LLM does **NOT** rewrite bullet structure. Fix #34 bullets stay canonical.
   - Output: voice-tailored Claude DR prompt, ~120–130KB per voice.

3. **Chunked Pass 1 merge.** Six per-section mini-merges + coherence pass:
   - Pass 1.1 BIOGRAPHICAL → `life_scaffold.json` + `formative_candidates.json`
   - Pass 1.2 INTELLECTUAL → `commitments.json` + `concepts.json` + `tensions.json`
   - Pass 1.3 REASONING → `reasoning_method.json` + `textures.json`
   - Pass 1.4 VOICE → `moves.json` + `register.json` + `vocabulary.json`
   - Pass 1.5 BOUNDARIES → `knowledge_boundary.json` + `sensitive_topics.json` + `hard_limits.json`
   - Pass 1.6 CORPUS → `works.json` + `passages.json` + `urls.json`
   - Pass 1.7 coherence → cross-chunk consistency check, emits final `merged_dossier.json`
   - Each chunk reads ALL 3 sources directly (no pre-splitting); LLM does relevance-filtering during merge.
   - Chunks 1.1–1.6 can run in parallel after sources are in place.

4. **Structured JSON, not 6-section markdown, as the canonical merged dossier shape.** Markdown was a legacy carryover from DR tools emitting markdown. Pass 1 emits typed JSON matching designed schemas; Pass 2 does field-mapping to persona card.

5. **No per-chunk human review.** Pass 1 LLM output is final. JSON schema validation is the machine gate (LLM re-runs, not humans fix). Human intervention is narrow: only for primary-text / lyrics provisioning when LLM cannot fetch (Pass 1c URL fetching, Pass 4a corpus research). Single human approval at persona-card level after Pass 2.

6. **Pass 7 becomes primary quality gate.** With per-chunk human review removed, Pass 7 (cross-model verification + benchmark-based eval per File 2) carries the quality burden previously distributed across human chunk-review steps. Pass 7 design + build is load-bearing — must be substantive, not a stub.

7. **Meta-conventions frozen early.** First two chunks (1.1 + 1.2) establish the META schema conventions: how evidence is tagged (`evidence_tag` enum), how sources are cited (`source_citation` structure), how contested readings surface, how tiers work, how scholarly_consensus vs minority-readings are represented. After 1.2, conventions are locked into `personas/schemas/_conventions.schema.json` and reused unchanged for 1.3–1.6. Domain-specific fields emerge per chunk; meta stays frozen.

8. **Token-pressure mitigation:** use Opus 4.7 1M context as the Pass 1 merge model. Comfortable for 3-source merge per chunk (3 × ~50–130KB = ~400KB max input, well within context).

9. **Validator relaxation + OUTPUT FORMAT softening** in DR prompt. DR can produce any structure that fits the research; canonicalization happens at Pass 1 merge, not at DR output. The current rigid 6-section markdown validator is to be loosened.

---

## Phase B starting point

**Goal:** build Pass 1.1 biographical chunk end-to-end as proof of architecture.

**Recommended sequence:**

- **B.1** — Design `life_scaffold.json` + `formative_candidates.json` schemas as JSON Schema files in `personas/schemas/` (new directory). Start from the persona card v2 schema (`docs/AI_Assembly_Persona_Card_v2.md`) and build outward — merged_dossier schema is a richer superset. Surface meta-conventions (evidence tagging, source citation, contested representation) as you go; commit them to `personas/schemas/_conventions.schema.json`.

- **B.2** — Write the Pass 1.1 merge prompt. Input: relevant material from all 3 source dossiers (Perplexity §1 + Claude DR §1 + Gemini cross-disciplinary slice). Output: structured JSON matching the schemas. Reasoning instructions: reconcile contradictions across sources, tag evidence per convention, surface contested candidates rather than picking one, no fabrication.

- **B.3** — Write the Pass 1.1 runner: load 3 sources, call merge LLM with prompt + schema, validate output against JSON Schema, retry on validation failure with critique.

- **B.4** — Test on Ibn Battuta material. Cached Perplexity + Gemini outputs are at `_workspace/archive/runs/personas/ibn_battuta/01_research/` (post-reorg location). Need a Claude DR dossier — either re-render the prompt (now with hybrid tailoring if D.1 lands first) and re-run claude.ai, or use the existing Battuta DR dossier on the user's Desktop as transitional test material.

- **B.5** — Iterate schema until output cleanly maps to persona card fields (preview Pass 2 mapping mentally).

- **B.6** — Lock meta-conventions. Write Pass 1.2 (intellectual framework). Following conventions; adjust if 1.2's domain (commitments + tensions + minority readings) exposes gaps. Re-freeze conventions.

After B.6, conventions are locked and chunks 1.3–1.6 follow the same pattern with domain-specific fields.

---

## Test material in repo

- `personas/inputs/voices/ibn_battuta.json` — v3.10 Pass 0a artifact; will be regenerated under the redesigned Pass 0a per `REBUILD_PLAN.md` §"Phase 0 — Intake · Pass 0a", but useful as a reference shape and for testing the schema fields the new Pass 0a still emits
- `personas/inputs/voices/ibn_battuta_pass0a_review.md` — Pass 0a review doc, v3.10 framing
- `_workspace/archive/runs/personas/ibn_battuta/01_research/perplexity_dossier.json` — real Perplexity sonar-deep-research output (~109KB, ~$5–10 to regenerate; preserved as test fixture)
- `_workspace/archive/runs/personas/ibn_battuta/01_research/gemini_broad_scan.json` — real Gemini broad-scan output

The Battuta DR dossier (the actual claude.ai output) lives on the user's Desktop, NOT in repo, and is intentionally discarded — it'll be regenerated by the new pipeline once Phase D (hybrid LLM tailoring) lands. Until then, B.4 testing can either use it as transitional test material or wait for the regenerated one.

---

## Voices to build (all 12 fresh under Phase B)

12 voices total. **All are pending under Phase B** — there is no "5 done / 7 to build" split because Pass 0a itself is being redesigned (see `REBUILD_PLAN.md` §"Phase 0 — Intake · Pass 0a"; 7 changes including `editorial_rationale` field, `manual_grounding` unification, decoupling from full `conference_context`, domain-specific non-human grounding, plus Boddice integration changes the editorial framing). The 5 existing v3.10 configs do not survive the redesigned Pass 0a — they get regenerated along with the other 7.

**v3.10 artifacts now in `_workspace/archive/`** are archaeology, not inputs to the rebuilt pipeline:
- 5 voice configs (Pass 0a outputs): Plato, Cleopatra, Arendt, Octopus, Ibn Battuta
- 3 DR prompts: cleopatra, ibn_battuta, octopus
- 1 full pipeline run: Plato; 2 partial runs: Hannah Arendt, Ibn Battuta

They serve as: (a) test fixtures for validating the new pipeline produces equivalent or better output, (b) reference for v3.10 framing, (c) reference for known failure modes the rebuild is meant to fix (especially Boddice's emotional-experiential vocabulary critique).

**Build sequence under Phase B (per voice):** new Pass 0a → Phase 0.5 (Perplexity + Gemini) → new Pass 0b hybrid-tailored DR prompt (PB#2) → manual Claude DR session → chunked Pass 1 merge (1.1–1.7) → Phase 2 generation (Pass 2–6) → Phase 3 validation (Pass 7-pre / 7a multi-family per `REBUILD_PLAN.md` §"Pass 7a multi-family validation" / 7b / 7c) → Phase 4 Derive.

The 5 voices with v3.10 artifacts are not "ahead" of the other 7 in any meaningful sense.

Voice list: Plato, Cleopatra, Arendt, Octopus, Ibn Battuta, Scheherazade, Whanganui, Marley, Audrey Tang, Peter Thiel, Ada Lovelace, Dostoevsky.

---

## Out of scope for personas-pipeline architecture rewrite

These are separate workstreams, do not pull them into Phase B–F:

- **Voice Pipeline Steps 1+2+3** (text-to-audio for the AI Assembly's spoken output)
- **Researcher pipeline** (extracting themes from session audio/transcripts)
- **Provocateur pipeline runtime** (consumes finished persona cards; doesn't change with this rewrite)
- **Microsite** (Astro/Next.js attendee-facing site)
- **Closing-show pipelines** (theme identification + per-theme video)
- **Athens execution prep** (deployment, infrastructure, dry runs)
- **GraphRAG layer** (File 1 Layer 4 — out of scope per briefing v3.1)
- **Persona vector / activation steering** (LoRA fine-tuning — out of scope per briefing v3.1)

---

## Pointers for the next session

Read in order. Primary reads first; reference and historical context follow.

**Primary (active design):**

1. **This document** — architectural decisions binding for Phase B (PB#1–9)
2. **`_workspace/planning/REBUILD_PLAN.md`** — active task list. Boddice integration locked, Pass 7a multi-family validation locked, Phase 0 + Phase 0.5 reviewed (21 items captured). Phase 1 / 2 / 3 / 4 stubs to fill in.
3. **`CLAUDE.md`** at repo root — four-category repo layout (post-reorg), venv rules, load_dotenv pattern, orientation reading order

**Reference (target shape):**

4. **`docs/AI_Assembly_Persona_Card_v2.md`** — 37-field persona card schema (target shape for Pass 2 output)
5. **`docs/AI_Assembly_Persona_Pipeline_v3_10.md`** — predecessor pipeline spec (predates this rewrite; will be deprecated when Phase B lands)
6. **`research/baseline_research/`** — five baseline research artifacts (3 persona-pipeline + 1 Athens audience + 1 Boddice biocultural critique). See `research/baseline_research/README.md` for the file-by-file index.
7. **`personas/flows/shared/prompts/pass_0b_dr_prompt.md`** — current 1086-line Fix #34 DR prompt template (input to PB#2's hybrid Jinja+LLM tailoring pass)

**Historical context (only if needed):**

8. **`_workspace/archive/fix-plans/FIX_34_SECTION_BULLETS_DRAFT.md`** — Fix #34 design rationale
9. **`_workspace/archive/fix-plans/SONNET_EXECUTION_PLAN_PHASE_A.md`** — what Phase A executed

**Test fixtures (Pass 1.1 testing):**

10. **`_workspace/archive/runs/personas/ibn_battuta/01_research/`** — Perplexity + Gemini outputs from a real Battuta Phase 0.5 run (perplexity_dossier.json + gemini_broad_scan.json)

---

## Settings note

`.claude/settings.local.json` has the Phase A scoped allowlist active (git checkout/pull/merge/push/add/commit, pip install). For Phase B, may want to add `./venv/bin/python:*` (currently only `-c` is allowed) for running merge prototypes. Tightening back to read-only-only is appropriate after architecture work fully lands; not needed during active development.
