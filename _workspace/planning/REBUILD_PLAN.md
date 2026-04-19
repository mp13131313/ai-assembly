# Persona Pipeline Rebuild — Plan & Architecture

**Status:** Living document. Single source of truth for the persona pipeline rebuild.
**Scope:** End-to-end rebuild of `personas/` from voice intake through Derive.
**Out of scope:** Voice Pipeline (Steps 1+2+3), Researcher / Provocateur runtime, microsite, closing show, Athens deployment prep, GraphRAG layer (per Briefing v3.1), Persona vector / activation steering / LoRA fine-tuning (per Briefing v3.1).
**Originally derived from:** [`_workspace/archive/session-artifacts/ARCHITECTURE_NEXT_PHASE_HANDOFF_2026_04_18.md`](../archive/session-artifacts/ARCHITECTURE_NEXT_PHASE_HANDOFF_2026_04_18.md) — 2026-04-17/18 design conversation that locked the 9 binding decisions below. Merged into this single doc on 2026-04-19; provenance preserved at the archived path.

---

## Conventions

- **Tags:** `[schema]` (data shape) · `[prompt]` (LLM instructions) · `[runner]` (orchestration / validation / IO) · `[ux]` (human workflow) · `[verify]` (testing / fixtures / eval)
- **Status:** ☐ open · ◐ partially decided · ☑ decided
- **PB#N** = locked architectural decision below (from the original handoff). `→PB#N` flags items downstream of one of those decisions.

---

## Locked architectural decisions (PB#1–9)

These were debated and committed in the 2026-04-17/18 design conversation. **Do not re-litigate without explicit reason.** This section is immutable — proposed changes go through an explicit decision review, not silent edits.

### PB#1 — Drop ChatGPT Deep Research; 3 sources only

Three research sources only: Perplexity sonar-deep-research (factual grounding) + Claude DR (voice/character extraction) + Gemini broad-scan (cross-disciplinary). The 3-way DR cross-verification dropped in favor of simpler architecture. Quality delta from 3→4 sources judged not worth API/manual-paste burden.

**Bounded scope:** PB#1 applies only to research stage (Phase 0.5 / Pass 1a-DR). Pass 7a Cross-Model Validation keeps OpenAI — see §"Cross-cutting · Pass 7a multi-family validation" below.

### PB#2 — Hybrid Jinja + LLM tailoring for the Claude DR prompt render

Replaces pure Jinja. Scope is **Balanced**:
- Jinja produces deterministic scaffold (RESEARCH INTEGRITY, conditional appendices, card-field annotations, section headings, hostile-sources/corpus-constraint blocks).
- LLM tailoring pass customizes per-voice: illustrative figure examples (Augustine → al-Ghazali for Battuta), SWAP TEST anchors, emphasis redirect based on Perplexity coverage, optional pruning of clearly-inapplicable bullets.
- LLM does **NOT** rewrite bullet structure. Fix #34 bullets stay canonical.
- Output: voice-tailored Claude DR prompt, ~120–130 KB per voice.

### PB#3 — Chunked Pass 1 merge

Six per-section mini-merges + coherence pass:
- Pass 1.1 BIOGRAPHICAL → `life_scaffold.json` + `formative_candidates.json`
- Pass 1.2 INTELLECTUAL → `commitments.json` + `concepts.json` + `tensions.json`
- Pass 1.3 REASONING → `reasoning_method.json` + `textures.json`
- Pass 1.4 VOICE → `moves.json` + `register.json` + `vocabulary.json`
- Pass 1.5 BOUNDARIES → `knowledge_boundary.json` + `sensitive_topics.json` + `hard_limits.json`
- Pass 1.6 CORPUS → `works.json` + `passages.json` + `urls.json`
- Pass 1.7 coherence → cross-chunk consistency check, emits final `merged_dossier.json`
- Each chunk reads ALL 3 sources directly (no pre-splitting); LLM does relevance-filtering during merge.
- Chunks 1.1–1.6 can run in parallel after sources are in place.

### PB#4 — Structured JSON, not 6-section markdown, as the canonical merged dossier shape

Markdown was a legacy carryover from DR tools emitting markdown. Pass 1 emits typed JSON matching designed schemas; Pass 2 does field-mapping to persona card.

### PB#5 — No per-chunk human review

Pass 1 LLM output is final. JSON schema validation is the machine gate (LLM re-runs, not humans fix). Human intervention is narrow: only for primary-text / lyrics provisioning when LLM cannot fetch (Pass 1c URL fetching, Pass 4a corpus research). Single human approval at persona-card level after Pass 2.

### PB#6 — Pass 7 becomes primary quality gate

With per-chunk human review removed, Pass 7 (cross-model verification + benchmark-based eval per File 2) carries the quality burden previously distributed across human chunk-review steps. Pass 7 design + build is load-bearing — must be substantive, not a stub.

### PB#7 — Meta-conventions frozen early

First two chunks (1.1 + 1.2) establish the META schema conventions: how evidence is tagged (`evidence_tag` enum), how sources are cited (`source_citation` structure), how contested readings surface, how tiers work, how scholarly_consensus vs minority-readings are represented. After 1.2, conventions are locked into `personas/schemas/_conventions.schema.json` and reused unchanged for 1.3–1.6. Domain-specific fields emerge per chunk; meta stays frozen.

### PB#8 — Opus 4.7 1M context for Pass 1 merge

Token-pressure mitigation: comfortable for 3-source merge per chunk (3 × ~50–130 KB = ~400 KB max input, well within context).

### PB#9 — Validator relaxation + OUTPUT FORMAT softening in DR prompt

DR can produce any structure that fits the research; canonicalization happens at Pass 1 merge, not at DR output. The current rigid 6-section markdown validator is to be loosened.

---

## Voices to build (all 12 fresh under Phase B)

12 voices total. **All are pending under Phase B** — there is no "5 done / 7 to build" split because Pass 0a itself is being redesigned (see §"Phase 0 — Intake · Pass 0a"; 7 changes including `editorial_rationale` field, `manual_grounding` unification, decoupling from full `conference_context`, domain-specific non-human grounding, plus Boddice integration changes the editorial framing). The 5 existing v3.10 configs do not survive the redesigned Pass 0a — they get regenerated along with the other 7.

**v3.10 artifacts now in `_workspace/archive/`** are archaeology, not inputs to the rebuilt pipeline:
- 5 voice configs (Pass 0a outputs): Plato, Cleopatra, Arendt, Octopus, Ibn Battuta
- 3 DR prompts: cleopatra, ibn_battuta, octopus
- 1 full pipeline run: Plato; 2 partial runs: Hannah Arendt, Ibn Battuta

They serve as: (a) test fixtures for validating the new pipeline produces equivalent or better output, (b) reference for v3.10 framing, (c) reference for known failure modes the rebuild is meant to fix (especially Boddice's emotional-experiential vocabulary critique).

**Build sequence under Phase B (per voice):** new Pass 0a → Phase 0.5 (Perplexity + Gemini) → new Pass 0b hybrid-tailored DR prompt (PB#2) → manual Claude DR session → chunked Pass 1 merge (1.1–1.7) → Phase 2 generation (Pass 2–6) → Phase 3 validation (Pass 7-pre / 7a multi-family per §"Cross-cutting · Pass 7a multi-family validation" / 7b / 7c) → Phase 4 Derive.

The 5 voices with v3.10 artifacts are not "ahead" of the other 7 in any meaningful sense.

Voice list: Plato, Cleopatra, Arendt, Octopus, Ibn Battuta, Scheherazade, Whanganui, Marley, Audrey Tang, Peter Thiel, Ada Lovelace, Dostoevsky.

---

## Where Phase A left things (snapshot, 2026-04-18)

Historical context for the rebuild — what existed when Phase B planning began.

- **Fix #34** (extraction-shaped DR prompt bullets, all 3 type branches: human / non-human organism+system / fictional) is in `main`.
- **Phase 0a + Phase 0.5** work end-to-end: voice config → Perplexity sonar-deep-research + Gemini broad-scan in parallel → Jinja-render → Claude DR prompt file (manual paste into claude.ai). Verified on Ibn Battuta.
- **Pass 1** (merge of DR sources into canonical persona dossier) is unbuilt.
- **Pass 2+** (persona card extraction, verification, runtime feed) is unbuilt.

Subsequent fix-plan and reorg work (commits `881280c`–`70ff3dd`, all merged 2026-04-19) cleaned up F-01..F-32 findings and reorganized the repo into the four-category tree (production / research / planning / archive). The persona pipeline v3.10 codebase is current and runnable; the rebuild starts from there.

---

## Cross-cutting

To revisit once all phases are walked.

- ☐ **Split `personas/inputs/conference_context.json`.** Currently a kitchen sink: project facts + audience profile + panel roster + paragraph blurb + Stage-0 notes + canonical-source pointer. Read by Pass 0a, Phase 0.5, Pass 7b. Split into (a) project facts, (b) audience profile (already canonical-sourced from `docs/AUDIENCE_BRIEF.md`), (c) panel roster, (d) per-pass scaffolding hints. `[schema]`
- ☐ **`personas/schemas/` directory.** Phase B's home for JSON Schemas (see §"Phase 1" §B.1 below). Establish convention before landing the first chunk schema: file naming, version field, `_conventions.schema.json` ref pattern, validation entry point. `[schema]` `→PB#7`
- ☐ **Test fixture lifecycle.** Ibn Battuta `perplexity_dossier.json` + `gemini_broad_scan.json` are pinned as test fixtures (see §"Test material in repo"). Need explicit lifecycle: when refresh, what's pinned vs regenerable, where to record the regenerable-cost so a future session knows. `[verify]`
- ☐ **Cost / wall-clock budget per voice for the rebuild.** v3.10 = ~$14–18 + 60–120 min/voice. Phase B adds chunked merge calls (6 + coherence pass = 7 extra Opus calls) — net cost likely up. Set a target before committing chunk shapes. `[verify]`
- ☐ **Decision: keep `voice_mode` 3-enum or expand?** Today's `{philosophical, observational, narratival}` drives prompt branching across 5+ downstream passes. Expanding it without rewriting branches is load-bearing. Phase B is the chance to revisit; default = keep unless review finds a real gap. `[schema]`

---

## Cross-cutting · Boddice integration

Treat Rob Boddice's biocultural critique of the persona card schema (5th baseline research artifact, [`research/baseline_research/compass_artifact_wf-1e84f45b-0c9f-497a-84bc-88b7867c9a26_text_markdown.md`](../../research/baseline_research/compass_artifact_wf-1e84f45b-0c9f-497a-84bc-88b7867c9a26_text_markdown.md)) as the **content payload that PB#2's hybrid Jinja+LLM tailoring carries**, plus PB#1 (voice-type-specific 1a/1b prompts) and PB#7 (`_conventions.schema.json` evidence tags). Boddice extends File 3's anti-projection program one ontological layer deeper: he interrogates not just whether a persona is generic but whether the categorical infrastructure used to organize it ("emotion," "personality," "wound") imports a 1820–2014 Anglo-American framework anachronistic to ~8 of 12 panel voices.

**Scope of items here is integration mapping, not content restatement.** The source doc's §13 (`world` 5-part rubric), §14 (`formative_experience` 4-part rubric), §15 (5-field audit), §12 (two new evidence tags), and §9 (historically-specific emotions catalogue) are the canonical text — read them there.

### Primary integration points

- ☐ **PB#2 hybrid tailoring carries Boddice §13 + §14.** Replace the wound-and-personality framing in the new Pass 0b template with Boddice's `world` 5-part rubric (ontological furniture / available pathē in original language / framework for difficulty / model of selfhood / anachronisms-to-avoid) and `formative_experience` 4-part rubric (formative emotional community / lived-through-own-apparatus / engagement it drives / condition-of-being-for-non-human). Boddice's worked examples for Plato / Arendt / Octopus / Ibn Battuta / Marley / Whanganui / Cleopatra become the few-shot exemplars the LLM tailoring pass studies. `[prompt]` `→PB#2`
- ☐ **PB#1 voice-type-specific 1a/1b prompts inherit Boddice's research-side asks.** Drop "personality traits, quirks, contradictions" and "central biographical trauma" from `persona_pass_1a_*.md`. Add: "5–10 period-specific terms for affects/passions in original language with glosses; use the period's own character-grammar (humours, soul-parts, nafs-stations, four Rasta virtues, Buddhist śīla), not Big-Five-style adjectives." Same for 1b (lighter touch). `[prompt]` `→PB#1`
- ☐ **PB#7 `_conventions.schema.json` adds two new evidence tags.** `[experiential reconstruction]` (any claim about what the voice felt/meant/experienced as biocultural-contextual reconstruction) and `[projection warning]` (any modern English term used faute de mieux that distorts). Slot alongside `[stated]`, `[scholarly consensus]`, `[inference]`. `[schema]` `→PB#7`
- ☐ **Pass 2 + Pass 4a synthesis prompts (post-merge) reuse the same rubric language.** Necessary-but-not-sufficient guard: if synthesis prompts still ask for "fill `formative_experience` with the ONE wound and its lesson," period-specific dossier material gets re-collapsed at synthesis. `[prompt]`

### Secondary integration points

- ☐ **Pass 0a review-doc revision.** "Why this voice is in the Assembly" gets reframed in the voice's own world-terms — or moved out entirely per the existing Pass 0a plan item (`editorial_rationale` curator field). Boddice strengthens the case for moving it out. `[prompt]`
- ☐ **`voice_mode` 3-enum reconsidered through Boddice.** The Cross-cutting open question ("keep or expand?") gets a Boddice-specific framing: calling Marley "observational" or Octopus "observational" uses modern Western mode-of-knowing categories. Candidate additions: `ritual` (Whanganui), `channeled` (Marley), `ecological` (Octopus), `narratival-frame` (Scheherazade). Or reconceive entirely. `[schema]`
- ☐ **§9 historically-specific emotions catalogue as reference material.** Pass 0b template (or its hybrid-tailoring inputs) cites it for the "5–10 period-specific affects" request. Acedia, amae, saudade, toska, Sehnsucht, Zärtlichkeit, liget, fago, ghinnawa, philotimo. `[prompt]`

### Deferred

- ◐ **Field renames in Boddice §15.** `character` → `character_in_period_vocabulary`, `voice_signature` → `speech_register_and_tradition`, `relationships` → `relational_grammars`, `epistemic_frame_statement` → `ontological_commitments_and_method`, `dialogue_instincts` → `dialogical_disposition`. Renames are correct in spirit but cascade to `runtime/flows/shared/council/council_config.json`, runtime consumers, and the future Voice Pipeline. **Revise the field instructions inside the existing names**; rename only in a future Card v3 sweep that touches all consumers in one migration. Most of Boddice's value lands without the rename. `[schema]`
- ◐ **Pass 7c reconciliation with `[projection warning]`.** Adjacent but distinct: `banned_language` = words *the voice* would never use; `[projection warning]` = words *we* used to describe the voice that distort. Resolve when Pass 7c is reviewed. Not blocking. `[prompt]`

### Project-level flag (not pipeline-internal)

- ☐ **Briefing v3.1 sentence on flagged-projection-not-non-projection.** Boddice's reflexive admission (Rosenwein's AHR rejoinder) means no tag eliminates the builder's modern-English category-set. Pipeline cannot promise non-projection, only flagged projection. Briefing should say so. **Till/Matthias decision, not pipeline scope.** Worth raising. `[ux]`

### Why no v3.10 bridge patch

All 12 persona cards (including the 5 with v3.10 partials — Plato, Cleopatra, Arendt, Octopus, Ibn Battuta) get rebuilt on the Phase B architecture per §"Voices to build" above. Existing run outputs (now at `_workspace/archive/runs/personas/`) are archaeology. There is no "ship pre-Athens on v3.10" path; the rebuild itself produces the Athens-ready cards. Bridge patches to v3.10 prompts for Boddice would be discarded. Captured here so a future session doesn't re-suggest it.

---

## Cross-cutting · Pass 7a multi-family validation (locked decision)

**Decision (2026-04-19):** Pass 7a Cross-Model Validation keeps the multi-family fallback chain (`o3 → gpt-4o → gemini-2.5-pro`) in the rebuild. **Do not drop OpenAI from Pass 7a.** PB#1's "drop ChatGPT DR" applies only to research-stage uses (Phase 0.5 / Pass 1a-DR); it does not cover Pass 7a.

**Why locked:**

- Baseline-research File 2 §4 ("Cross-model critique"): *"self-preference bias runs 10–25% — GPT-4o scores its own outputs ~10% higher; earlier Claude models showed ~25% self-preference."* If Claude both writes and judges the card, the swap test is gamed by the model's own bias toward its style.
- Gemini alone is not a credible humanities critic — baseline-research File 3 cites "unusable for basic humanities research" reports.
- OpenAI o3 specifically — reasoning-mode, different family, well-instrumented for structured JSON — fills the cross-family critic role no other model fills.
- The Athens audience's hardest-to-please voices (Mattei, Akomolafe, Bridle, Pahina) will catch anything that survived only Claude self-critique.

**Scope of "drop OpenAI" — bounded to research stage:**

- ☑ PB#1 already drops ChatGPT DR from Phase 0.5 (3 sources only: Perplexity + Claude DR + Gemini broad-scan).
- ☑ Pass 3 ChatGPT DR supplement was removed in commit `d137791` and verified gone via F-27 fix on `fix-review-findings`.
- ☐ Any Phase B work that tries to extend "drop OpenAI" beyond research-stage gets flagged before landing — point at this section.

**What remains using OpenAI in the rebuild:**

- **Pass 7a Cross-Model Validation** primary: `o3` reasoning model (`max_completion_tokens=8192`, no temperature) → fallback `gpt-4o` (`max_tokens=8192`, `temperature=0.0`) → final fallback `gemini-2.5-pro`.
- Nothing else.

---

## Phase 0 — Intake

### Pass 0a (Voice Config)

Reviewed 2026-04-18.

- ☐ **Move "Why this voice is in the Assembly" out.** It's curation, not classification. Add an `editorial_rationale` field the human writes directly into the voice config. Hybrid tailoring pass uses it as DR-prompt scaffolding. `[schema]` `[prompt]` `→PB#2`
- ☐ **Unify `wikipedia_extract` + `disambiguation_hint` → `manual_grounding`.** Same job (text-context for classification); the dual code path is incidental. `[schema]` `[runner]`
- ☐ **Decouple Pass 0a from full conference_context.** Pass 0a needs name + a one-line panel framing, not audience factions. Bundles with the cross-cutting split. `[prompt]` `[schema]`
- ☐ **Domain-specific grounding for non-human voices.** Curated `non_human_grounding/` dir: Octopus → Godfrey-Smith excerpt; Whanganui → Te Awa Tupua Act preamble. Replaces / augments Wikipedia path when `type=="non-human"`. Natural fit with hybrid Jinja+LLM tailoring. `[schema]` `[prompt]` `→PB#2`
- ☐ **Tighten `auto` / `proposed` labels** in the review-doc disposition table. Either everything is `proposed`, or reserve `auto` for `name` only. Current labels overstate determinism. `[prompt]`
- ☐ **Fix `--choose N` TTY inconsistency** in [`run_pass0a_voice_config.py:104-107`](../../personas/run_pass0a_voice_config.py). Always exit on out-of-range, or always fall back. Pick one. `[runner]`
- ☐ **Make the `conference_context` placeholder load-bearing.** Runner currently overwrites silently — warn if model omitted the `INJECTED_BY_RUNNER` placeholder so a prompt regression that drops the field is detectable. `[runner]`

### Pass 0b (DR Prompt) — pending review

`→PB#2` (hybrid Jinja+LLM tailoring), `→PB#9` (validator relaxation, OUTPUT FORMAT softening).

### Node 0 validation — pending review

`→PB#7` (whether `node0_validation.py` becomes JSON-Schema-driven once `_conventions.schema.json` lands).

---

## Phase 0.5 — Pre-DR Research

Reviewed 2026-04-18. Sub-passes: Pass 1a (Perplexity), Pass 1b (Gemini), Pass 0b (Jinja render). Plus the manual Pass 1a-DR (claude.ai) that consumes the rendered prompt.

`→PB#1` (3 sources only, locked), `→PB#2` (hybrid Jinja+LLM tailoring replaces pure Jinja for the DR prompt, locked), `→PB#9` (validator relaxation + OUTPUT FORMAT softening, locked).

### Pass 1a (Perplexity) + Pass 1b (Gemini)

- ☐ **Voice-type-specific prompts.** Today both `persona_pass_1a_research_human.md` and `persona_pass_1b_broad_scan.md` are hard-coded for "human" voices and fire for non-human + fictional too. Split into per-type files; route in the runner via `vi["type"]` + `vi["subtype"]`. Survival rate today depends on `perplexity_split.py` accepting both heading families, but the *content* under §1 is wrong-shaped for non-human. `[prompt]` `[runner]` `→PB#1`
- ☐ **Add 1-retry to `call_perplexity` and `call_gemini`.** Mirror the `_call_with_retry` pattern from Pass 0a. Currently no retry → network blip → hard exit + lost $5 Perplexity call. `[runner]`
- ☐ **Tighten Pass 1b prompt.** 14 lines of generic broad-scan ask. Should reflect what Gemini's actually good at (cross-disciplinary, non-English scholarship, recent reassessments) and forbid factual claims without citation. `[prompt]` `→PB#1`
- ☐ **Surface empty / truncated Gemini output.** `resp.text` falls back to `""` silently when filtered or hit max_output_tokens — no warning. `[runner]` `[verify]`

### Pass 0b (DR prompt render — Jinja today, hybrid Jinja+LLM in Phase B)

- ☐ **Decompose the 1086-line template** into per-type sub-templates (~3 × 300 lines + a wrapper). Cuts cross-edit burden; gives the LLM-tailoring pass smaller surfaces to reason about. `[prompt]` `→PB#2`
- ☐ **Per-section fallback in `split_dossier`.** Today's all-or-nothing returns `None` if any one heading fails to match — drops scaffolding for the other 5. Recover per-section; warn loudly on the missing ones. `[runner]`
- ☐ **Provenance header in the rendered DR prompt.** `<!-- PROMPT_VERSION: 0b-vX | VOICE_SLUG: <slug> | RENDERED_AT: <ts> -->`. `dr_validation.py` then checks the slug at validation time → catches stale-prompt mistakes. `[verify]`
- ☐ **Drop `display_name_with_hint` OR use it.** Currently set equal to `display_name` everywhere — dead variable. Hybrid tailoring is the natural home (prepend a Wikipedia disambiguation hint). `[prompt]` `→PB#2`
- ☐ **Address `run_pass0b_dr_prompt.py` standalone degradation.** Renders with `perplexity_findings=""` + `perplexity_sections=None` → a DR prompt with no research scaffolding. Either drop it or warn loudly. `[runner]` `[ux]`
- ☐ **Use `jinja2.StrictUndefined`** instead of `Undefined`. Same pattern as `personas/flows/shared/prompt_render.py`. Catches future template-renderer mismatches at render time, not at LLM-output time. `[runner]`

### Pass 1a-DR (manual claude.ai) + dossier validation

- ☐ **Section-level word-count floors in `dr_validation.py`.** A 15K-word dossier with a 100-word Section 6 still passes today. Add per-section minimums (~1,500/section). `[verify]`
- ☐ **Schema-validate all three Phase 0.5 outputs** (Perplexity dossier, Gemini scan, Claude DR dossier) before Phase 1's chunked merge consumes them. Fail-fast at the boundary rather than mid-merge. `[schema]` `[verify]` `→PB#7`
- ☐ **Operator-side checklist UX.** Today's "next steps" stamp is a 6-line print. The hand-off to claude.ai is the project's biggest manual gate; consider a small markdown checklist alongside the prompt (`<slug>_dr_briefing.md`) that names: model = Opus 4.7, Extended Thinking = ON, Deep Research = ON, expected wait, expected output shape, link to validator command. `[ux]`

### Architectural seam to flag

- ☐ **Two paths for primary-text URLs into the pipeline.** (a) Manual via `voice_config.primary_text_sources` (Plato has 5 Gutenberg URLs); (b) Automated via Pass 1c-extract from the merged dossier. Phase B should explicitly resolve: kill the manual path or document when it's preferred. Currently silent backward compat. `[schema]` `→PB#3`

---

## Phase 1 — Research Merge (chunked per Phase B)

`→PB#3` (chunked merge), `→PB#4` (structured JSON not markdown), `→PB#5` (no per-chunk human review), `→PB#7` (frozen meta-conventions after 1.1+1.2), `→PB#8` (Opus 4.7 1M context for merge).

### Recommended starting sequence (B.1–B.6)

From the original handoff. Goal: build Pass 1.1 biographical chunk end-to-end as proof of architecture.

- **B.1** — Design `life_scaffold.json` + `formative_candidates.json` schemas as JSON Schema files in `personas/schemas/` (new directory). Start from the persona card v2 schema (`docs/AI_Assembly_Persona_Card_v2.md`) and build outward — merged_dossier schema is a richer superset. Surface meta-conventions (evidence tagging, source citation, contested representation) as you go; commit them to `personas/schemas/_conventions.schema.json`.

- **B.2** — Write the Pass 1.1 merge prompt. Input: relevant material from all 3 source dossiers (Perplexity §1 + Claude DR §1 + Gemini cross-disciplinary slice). Output: structured JSON matching the schemas. Reasoning instructions: reconcile contradictions across sources, tag evidence per convention, surface contested candidates rather than picking one, no fabrication.

- **B.3** — Write the Pass 1.1 runner: load 3 sources, call merge LLM with prompt + schema, validate output against JSON Schema, retry on validation failure with critique.

- **B.4** — Test on Ibn Battuta material. Cached Perplexity + Gemini outputs are at `_workspace/archive/runs/personas/ibn_battuta/01_research/` (post-reorg location). Need a Claude DR dossier — either re-render the prompt (now with hybrid tailoring if D.1 lands first) and re-run claude.ai, or use the existing Battuta DR dossier on the user's Desktop as transitional test material.

- **B.5** — Iterate schema until output cleanly maps to persona card fields (preview Pass 2 mapping mentally).

- **B.6** — Lock meta-conventions. Write Pass 1.2 (intellectual framework). Following conventions; adjust if 1.2's domain (commitments + tensions + minority readings) exposes gaps. Re-freeze conventions.

After B.6, conventions are locked and chunks 1.3–1.6 follow the same pattern with domain-specific fields.

### Detailed task list (chunked merge implementation)

To fill in as Phase 1 work proceeds.

---

## Phase 2 — Section-by-Section Generation

To fill in. Passes 2, 3, 4a, 4b, 5, 6 + Coherence Threading.

---

## Phase 3 — Validation

To fill in. Pass 7-pre, 7a, 7b, 7c. Load-bearing per `→PB#6` (Pass 7 = primary quality gate now that per-chunk review is removed). Pass 7a multi-family is locked — see §"Cross-cutting · Pass 7a multi-family validation" above.

---

## Phase 4 — Derive

To fill in. Provocateur Profile + Evaluation Rubric.

---

## Cross-Persona QC (Phase 5 in v3.10, currently unbuilt)

To fill in. `→PB#6` may shrink its role since Pass 7 carries the quality burden. Open question: what does Phase 5 still uniquely catch?

---

## Test material in repo

- `personas/inputs/voices/ibn_battuta.json` — v3.10 Pass 0a artifact; will be regenerated under the redesigned Pass 0a per §"Phase 0 — Intake · Pass 0a", but useful as a reference shape and for testing the schema fields the new Pass 0a still emits
- `personas/inputs/voices/ibn_battuta_pass0a_review.md` — Pass 0a review doc, v3.10 framing
- `_workspace/archive/runs/personas/ibn_battuta/01_research/perplexity_dossier.json` — real Perplexity sonar-deep-research output (~109 KB, ~$5–10 to regenerate; preserved as test fixture)
- `_workspace/archive/runs/personas/ibn_battuta/01_research/gemini_broad_scan.json` — real Gemini broad-scan output

The Battuta DR dossier (the actual claude.ai output) lives on the user's Desktop, NOT in repo, and is intentionally discarded — it'll be regenerated by the new pipeline once Phase D (hybrid LLM tailoring) lands. Until then, B.4 testing can either use it as transitional test material or wait for the regenerated one.

---

## Pointers for the next session

The orientation reading order in `CLAUDE.md` is the canonical bootstrap sequence. This section adds Phase B-specific reads.

**Primary (active design):**

1. **This document** — single source of truth for Phase B (merged from `ARCHITECTURE_NEXT_PHASE_HANDOFF.md` 2026-04-19; PB#1–9 hoisted to top, original handoff archived)
2. **`CLAUDE.md`** at repo root — four-category repo layout, venv rules, load_dotenv pattern, orientation reading order

**Reference (target shape):**

3. **`docs/AI_Assembly_Persona_Card_v2.md`** — 37-field persona card schema (target shape for Pass 2 output)
4. **`docs/AI_Assembly_Persona_Pipeline_v3_10.md`** — predecessor pipeline spec (predates this rewrite; will be deprecated when Phase B lands)
5. **`research/baseline_research/`** — five baseline research artifacts (3 persona-pipeline + 1 Athens audience + 1 Boddice biocultural critique). See `research/baseline_research/README.md` for the file-by-file index.
6. **`personas/flows/shared/prompts/pass_0b_dr_prompt.md`** — current 1086-line Fix #34 DR prompt template (input to PB#2's hybrid Jinja+LLM tailoring pass)

**Historical context (only if needed):**

7. **`_workspace/archive/session-artifacts/ARCHITECTURE_NEXT_PHASE_HANDOFF_2026_04_18.md`** — original snapshot of the 2026-04-17/18 design conversation that produced PB#1–9 (now merged into this doc; preserved for provenance)
8. **`_workspace/archive/fix-plans/FIX_34_SECTION_BULLETS_DRAFT.md`** — Fix #34 design rationale
9. **`_workspace/archive/fix-plans/SONNET_EXECUTION_PLAN_PHASE_A.md`** — what Phase A executed

**Test fixtures (Pass 1.1 testing):**

10. **`_workspace/archive/runs/personas/ibn_battuta/01_research/`** — Perplexity + Gemini outputs from a real Battuta Phase 0.5 run (perplexity_dossier.json + gemini_broad_scan.json)

---

## Open questions to defer

(Catch-all — items that need a decision but don't belong to a specific phase yet. Add as we go.)

- ☐ When/how does the rebuild get integrated with the runtime side? The cross-repo handoff (`personas/HANDOFF.md`) and `runtime/flows/shared/council/council_config.json` consumers need to keep working through the transition. Probably gated behind shipping the first rebuilt voice card end-to-end.

---

## Settings note

`.claude/settings.local.json` had a Phase A scoped allowlist active (git checkout/pull/merge/push/add/commit, pip install). Post fix-plan + reorg landing (2026-04-19), the allowlist may need adjustment — for Phase B may want to add `./venv/bin/python:*` (currently only `-c` is allowed) for running merge prototypes. Tightening back to read-only-only is appropriate after architecture work fully lands; not needed during active development.

---

*Last updated: 2026-04-19 — merged from `ARCHITECTURE_NEXT_PHASE_HANDOFF.md` (2026-04-18); PB#1–9 hoisted to top, original handoff archived to `_workspace/archive/session-artifacts/ARCHITECTURE_NEXT_PHASE_HANDOFF_2026_04_18.md` for provenance.*
