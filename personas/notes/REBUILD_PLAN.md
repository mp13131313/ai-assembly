# Persona Pipeline Rebuild — Plan

**Status:** Living draft. Grows per pass during the step-by-step review (started 2026-04-18).
**Scope:** End-to-end rebuild of `personas/` from voice intake through Derive.
**Out of scope:** Voice Pipeline (Steps 1+2+3), Researcher / Provocateur runtime, microsite, closing show, Athens deployment prep.
**Binding spec:** [`personas/notes/ARCHITECTURE_NEXT_PHASE_HANDOFF.md`](ARCHITECTURE_NEXT_PHASE_HANDOFF.md) §"Architectural decisions" 1–9 (referred to as `PB#1`..`PB#9` below).

This plan does **not** override Phase B decisions. Items here either implement them, fill gaps they don't cover, or flag follow-on work.

---

## Conventions

- **Tags:** `[schema]` (data shape) · `[prompt]` (LLM instructions) · `[runner]` (orchestration / validation / IO) · `[ux]` (human workflow) · `[verify]` (testing / fixtures / eval)
- **Status:** ☐ open · ◐ partially decided · ☑ decided
- **Phase B link:** `→PB#N` when an item is downstream of (or modifies) one of the locked decisions.

---

## Cross-cutting

To revisit once all phases are walked.

- ☐ **Split `personas/inputs/conference_context.json`.** Currently a kitchen sink: project facts + audience profile + panel roster + paragraph blurb + Stage-0 notes + canonical-source pointer. Read by Pass 0a, Phase 0.5, Pass 7b. Split into (a) project facts, (b) audience profile (already canonical-sourced from `docs/AUDIENCE_BRIEF.md`), (c) panel roster, (d) per-pass scaffolding hints. `[schema]`
- ☐ **`personas/schemas/` directory.** Phase B's home for JSON Schemas (handoff §B.1). Establish convention before landing the first chunk schema: file naming, version field, `_conventions.schema.json` ref pattern, validation entry point. `[schema]` `→PB#7`
- ☐ **Test fixture lifecycle.** Ibn Battuta `perplexity_dossier.json` + `gemini_broad_scan.json` are pinned as test fixtures (handoff §"Test material in repo"). Need explicit lifecycle: when refresh, what's pinned vs regenerable, where to record the regenerable-cost so a future session knows. `[verify]`
- ☐ **Cost / wall-clock budget per voice for the rebuild.** v3.10 = ~$14–18 + 60–120 min/voice. Phase B adds chunked merge calls (6 + coherence pass = 7 extra Opus calls) — net cost likely up. Set a target before committing chunk shapes. `[verify]`
- ☐ **Decision: keep `voice_mode` 3-enum or expand?** Today's `{philosophical, observational, narratival}` drives prompt branching across 5+ downstream passes. Expanding it without rewriting branches is load-bearing. Phase B is the chance to revisit; default = keep unless review finds a real gap. `[schema]`

---

## Cross-cutting · Boddice integration

Treat Rob Boddice's biocultural critique of the persona card schema (5th baseline research artifact, [`personas/notes/baseline_research/compass_artifact_wf-1e84f45b-0c9f-497a-84bc-88b7867c9a26_text_markdown.md`](baseline_research/compass_artifact_wf-1e84f45b-0c9f-497a-84bc-88b7867c9a26_text_markdown.md)) as the **content payload that PB#2's hybrid Jinja+LLM tailoring carries**, plus PB#1 (voice-type-specific 1a/1b prompts) and PB#7 (`_conventions.schema.json` evidence tags). Boddice extends File 3's anti-projection program one ontological layer deeper: he interrogates not just whether a persona is generic but whether the categorical infrastructure used to organize it ("emotion," "personality," "wound") imports a 1820–2014 Anglo-American framework anachronistic to ~8 of 12 panel voices.

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

All 12 persona cards (including the 5 with v3.10 partials — Plato, Cleopatra, Arendt, Octopus, Ibn Battuta) get rebuilt on the Phase B architecture per `ARCHITECTURE_NEXT_PHASE_HANDOFF.md` §"Other voices to build later". Existing `personas/runs/*/` outputs are archaeology. There is no "ship pre-Athens on v3.10" path; the rebuild itself produces the Athens-ready cards. Bridge patches to v3.10 prompts for Boddice would be discarded. Captured here so a future session doesn't re-suggest it.

---

## Phase 0 — Intake

### Pass 0a (Voice Config)

Reviewed 2026-04-18.

- ☐ **Move "Why this voice is in the Assembly" out.** It's curation, not classification. Add an `editorial_rationale` field the human writes directly into the voice config. Hybrid tailoring pass uses it as DR-prompt scaffolding. `[schema]` `[prompt]` `→PB#2`
- ☐ **Unify `wikipedia_extract` + `disambiguation_hint` → `manual_grounding`.** Same job (text-context for classification); the dual code path is incidental. `[schema]` `[runner]`
- ☐ **Decouple Pass 0a from full conference_context.** Pass 0a needs name + a one-line panel framing, not audience factions. Bundles with the cross-cutting split. `[prompt]` `[schema]`
- ☐ **Domain-specific grounding for non-human voices.** Curated `non_human_grounding/` dir: Octopus → Godfrey-Smith excerpt; Whanganui → Te Awa Tupua Act preamble. Replaces / augments Wikipedia path when `type=="non-human"`. Natural fit with hybrid Jinja+LLM tailoring. `[schema]` `[prompt]` `→PB#2`
- ☐ **Tighten `auto` / `proposed` labels** in the review-doc disposition table. Either everything is `proposed`, or reserve `auto` for `name` only. Current labels overstate determinism. `[prompt]`
- ☐ **Fix `--choose N` TTY inconsistency** in [`run_pass0a_voice_config.py:104-107`](../run_pass0a_voice_config.py). Always exit on out-of-range, or always fall back. Pick one. `[runner]`
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

To fill in. Pass 1.1–1.7 per handoff §"Phase B starting point".

`→PB#3` (chunked merge), `→PB#4` (structured JSON not markdown), `→PB#5` (no per-chunk human review), `→PB#7` (frozen meta-conventions after 1.1+1.2), `→PB#8` (Opus 4.7 1M context for merge).

---

## Phase 2 — Section-by-Section Generation

To fill in. Passes 2, 3, 4a, 4b, 5, 6 + Coherence Threading.

---

## Phase 3 — Validation

To fill in. Pass 7-pre, 7a, 7b, 7c. Load-bearing per `→PB#6` (Pass 7 = primary quality gate now that per-chunk review is removed).

---

## Phase 4 — Derive

To fill in. Provocateur Profile + Evaluation Rubric.

---

## Cross-Persona QC (Phase 5 in v3.10, currently unbuilt)

To fill in. `→PB#6` may shrink its role since Pass 7 carries the quality burden. Open question: what does Phase 5 still uniquely catch?

---

## Open questions to defer

(Catch-all — items that need a decision but don't belong to a specific phase yet. Add as we go.)

- ☐ When/how does the rebuild get integrated with the runtime side? The cross-repo handoff (`personas/HANDOFF.md`) and `runtime/flows/shared/council/council_config.json` consumers need to keep working through the transition. Probably gated behind shipping the first rebuilt voice card end-to-end.

---

*Last updated: 2026-04-19 — after Pass 0a + Phase 0.5 reviews + Boddice integration mapping.*
