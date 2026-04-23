# Follow-Ups Tracker — single source of truth (2026-04-23)

**Purpose:** consolidates all open work + recently-completed work + closed/superseded items previously tracked across `OPEN_ITEMS.md`, `PIPELINE_REVIEW_FIXES.md` (FU sections), `HANDOFF_PHASE_M.md`, and `REBUILD_PLAN.md` (Open questions to defer).

**Supersedes for tracking purposes:**
- `PIPELINE_REVIEW_FIXES.md` §"FU#1-13" (still authoritative for `1-arch-*` history)
- `OPEN_ITEMS.md` §"PHASE M PUNCH LIST", §"Smaller improvements", §"Code-cleanup-on-fresh-project"
- `REBUILD_PLAN.md` §"Open questions to defer"

**Use this doc going forward.** Older docs retain historical context (Phase B / arch-03 design rationale, executed fix plans, lessons learned) but should not be modified for new tracking.

---

## Status legend

- 🔴 **CRITICAL** — blocks the next intended action
- 🟡 **IMPORTANT** — meaningfully improves quality / cost / safety
- 🟢 **NICE-TO-HAVE** — cosmetic, hygienic, or quality-of-life
- 🔵 **DEFERRED** — waiting on external trigger (Phase L sign-off, Plato run, runtime workstream, etc.)
- ✅ **DONE** — landed in code, with commit reference
- ⚫ **OBSOLETE** — superseded or closed out

---

## ACTIVE FOLLOW-UPS

### 🔴 Phase 1 — Critical for clean Dostoevsky re-run

#### FU#12 — Register hardening (Pass 2-6) + audience-aware engagement_topics (Pass 5)
- **Origin:** This session, surfaced empirically by Pass 7a's findings on the Dostoevsky un-patched card (9 specific field issues + 1 CRITICAL FAILURE on `register` check). All 9 issues share one pattern: scholarly metadata leaking into runtime card.
- **Scope evolution 2026-04-23:** initially proposed adding a per-voice `translation_table` lookup (modern term → voice native re-framing) inspired by external deep-research report §6. **Withdrawn** after critic feedback: pre-computed translations are exactly the "voice as costume of stock phrases rather than mode of reasoning" failure pattern FU#12-A is trying to prevent. Method (`translation_protocol`) is generative — runtime applies it contextually per query. A lookup table replaces method with substitution, foreclosing contextual richness and risking ventriloquism (e.g., the report's example "feminism → wrath of a wounded soul demanding rights against God's order" launders Dostoevsky's reactionary instincts as if they were the correct mapping). The audience-priming insight is preserved differently — see (B).

**Two coordinated changes:**

**(A) Register hardening across Pass 2-6 user prompts** — strip curator-side metadata from runtime card outputs.

Examples flagged on Dostoevsky:
- `[stated]/[scholarly_consensus]/[inference]` provenance tags appearing in runtime field values
- `curator_note` sub-fields with scholar attributions inside `reasoning_method.steps`
- "[curator-note: Toporov]" in concept_lexicon
- post-2022 Ukrainian reception commentary
- third-person pedagogical `header`/`why_selected` annotations on cited passages
- modern theorist names (Levinas/Bakhtin/Eikhenbaum/Kasatkina) in `banned_language` (shouldn't even appear)
- future-history phrasing in `knowledge_boundary`

Why systemic: arch-03 enrichment (1-arch-04 Gemini preservation, 1-arch-06 interpretive_frames, 1-arch-08 anachronism_discipline) gave Pass 2-6 richer source material. Some scholarly metadata leaks into runtime card outputs. Will recur for every voice we run.

Fix: systematic prompt-hardening across Pass 2-6 user prompts:
1. Add explicit register block: "You are writing the runtime persona system prompt. Output ALL fields in second person addressed TO the voice or first person AS the voice. Never write fields as a scholar describing the voice from outside."
2. Explicit don'ts: no `[stated]`/`[scholarly_consensus]`/`[inference]` provenance tags in field values; no `curator_note`/`pedagogical_note`/`editorial_note` sub-fields; no scholar attribution names in field values unless the voice itself would have cited them; no reception-commentary or future-history phrasing; `banned_language` is for terms the voice itself might be tempted to use, not for modern theorist names.
3. Voice-specific scoping: for period voices, scrub all post-knowledge-boundary scholar names + reception terms; for all voices, corpus metadata stays in curator-side files.

**(B) Audience-prime existing Pass 5 fields** — minimal extension, no new lookup table.

Pass 5 currently produces `bold_engagement_topics`, `default_questions`, `disagreement_protocol`, `unique_contribution` — all audience-shaped fields, but currently audience-BLIND (Pass 5 doesn't read deployment context). Extension:

1. Load `audience_profile.json` + `conference_facts.json` into Pass 5 (currently only loaded at final-assembly via `_load_conference_context_string()`).
2. Pass 5 user prompt addition: "Given the audience [...] and conference themes [...], populate `bold_engagement_topics` with topics likely to surface in this deployment. Populate `default_questions` with the voice's actual phrasings for engaging those topics in the voice's MODE OF REASONING (apply translation_protocol method generatively — do not pre-compute substitution phrases)."
3. **Critically: do NOT add a translation_table lookup.** The existing `translation_protocol` field encodes the voice's METHOD for handling modern queries. The runtime applies that method contextually per query. Pre-computing translations would replace generative method with substitution lookup, foreclosing contextual richness and risking ventriloquism (encoding voice's political bias as canonical mapping).

Strengthening `translation_protocol` itself happens via FU#12-A (Pass 2 prompt hardening) — ensure the field is articulated GENERATIVELY ("for any modern term, ask: who bears it, what scene stages it, how does the threshold pressure it") with worked example METHOD demonstrations rather than substitutions.

Pass 5 already on Opus + thinking + 16K tokens — perfect fit, no model upgrade needed.

**Effort:** 5-7 hr total — 4-6 hr for (A) Pass 2-6 register hardening + 1 hr for (B) Pass 5 audience/conference loading + prompt enhancement.

**Related:**
- Combines with FU#13 — fewer revision triggers if FU#12-A prevents leakage at source.
- Audience-priming is a small-but-meaningful runtime quality lift: voice arrives "ready" for the deployment context without sacrificing generative flexibility.

#### FU#13 — Architecture 2: linear `Pass 7a-fix` step (replaces revision loop)
- **Origin:** This session, designed after empirical observation that surgical writer re-invocation (FU#3) over-corrects (introduces 8 new inconsistencies + 29 more dossier_only citations on the Dostoevsky run).
- **Architecture:** `Pass 6 → Pass 7-pre → Pass 7-anachronism → Pass 7a → Pass 7a-FIX → Pass 7b`. Single Sonnet (or Opus) call takes Pass 7a's `field_issues[]` + relevant card fields + voice register exemplars + per-field Pydantic schemas → emits JSON patches → applied with per-field validation. Linear, single-shot, no loops.
- **Cost:** ~$0.50-1 + ~3-5 min per trigger event vs. ~$5-8 + ~20-25 min under FU#3 surgical writer re-invocation.
- **Panel-wide savings:** ~$80-130 + ~6 hr across 12 voices × ~1.5 trigger events.
- **Code simplification:** removes DOWNSTREAM_CHAIN, surgical-vs-cascade branching, revision while-loop, SKIP_REVISION_LOOPS env var, post-7a invalidation list, cumulative-dict refresh. Net ~150 lines removed, ~100 added. Much cleaner conceptually.
- **Quality tradeoffs (mitigatable):**
  - Cross-field coherence: patcher sees relevant context but not whole pass schema. Mitigate by passing nearby fields + voice context.
  - Voice register: Sonnet patcher with exemplars comparable to writer regen for most cases. Opus + thinking available for tougher cases.
  - Schema safety: explicit per-field Pydantic validation; fall back to FU#3 surgical writer re-run on validation failure.
- **Effort:** 4-6 hr (patcher prompt design + per-field-type context picker + apply-patch helper + validation fallback + integration replacing the revision loop).
- **Subsumes:** FU#3 (surgical loop code), FU#4 (anachronism re-fire — FU#13's design re-validates after fix), FU#6 (convergence diagnostic — no loops, no convergence question; effectiveness metric becomes part of `_fix_log.json`).

#### FU#5 — Pre-fix snapshot directory + revision log
- **Origin:** This session, operator request after seeing in-flight loop kill destroyed pre-revision Pass 4a/4b/5/6 outputs.
- **Problem:** Revision loop / fix-pass invalidation DELETES pre-revision outputs. After the run completes, there's no way to see what changed, A/B compare, audit which fields were patched, or diagnose whether revision improved or regressed. Important at panel scale (12 voices) where operator triage requires this signal.
- **Design:**
  - Before fix-pass fires, snapshot `04_generation/*.json` + `05_validation/*.json` into `04_generation/_snapshots/pre_fix_pass/` and `05_validation/_snapshots/pre_fix_pass/`.
  - Write `_fix_log.json` with: `{validator_verdict, validator_model, field_issues_count, anachronism_flags_count, snapshot_dir, started_at, completed_at, post_fix_verdict, issues_resolved, issues_remaining, issues_introduced, patches_applied: [{field_path, prior_value_summary, new_value_summary, rationale}]}`
  - Latest files stay at canonical paths (zero downstream code changes).
  - Snapshots isolated in `_snapshots/` (easy to gitignore + bloat trivial).
- **Effort:** 2-3 hr (simpler under FU#13 — snapshot once before fix-pass, not per-loop-iteration).
- **Cross-voice analysis benefit:** filesystem-grep across `projects/*/voices/*/04_generation/_snapshots/pre_fix_pass/` to identify voice-types most prone to revision, fields most-frequently flagged, etc.

### 🟡 Phase 2 — Important quality-of-life before Plato

#### FU#7 — Operator-facing pipeline summary
- **Origin:** This session, after observing verbose progress logging without a compact end-of-pipeline status.
- **Fix:** Final stdout block before exit prints compact `=== CARD COMPLETE ===` summary with: voice, validation_status, human_review_status, fix-pass effectiveness (issues_resolved / remaining), top concerns (severity-ordered), recommended_action, artifact paths.
- **Effort:** 1-2 hr.

#### FU#10-modified — Fix-pass test coverage
- **Origin:** This session, acknowledged gap in FU#3 commit. Modified to test new Architecture 2 (FU#13) instead of old revision loop.
- **Fix:** `tests/test_fix_pass.py` covering: schema validation success/failure paths, fallback to surgical writer re-run on validation failure, snapshot directory writing, `_fix_log.json` content correctness.
- **Effort:** 2-3 hr.

#### FU#9 — Merge chunk max_tokens audit
- **Origin:** This session, surfaced by Pass 1.2 VALIDATION FAIL → retry pattern in first arch-03 Stage 2 v7 run.
- **Problem:** Each Pass 1.1-1.6 has its own max_tokens setting in `chunk_runner.py`. With arch-03 enrichment + new `contested` evidence_tag enabling more InterpretiveFrame entries, per-chunk max_tokens haven't been audited for new content density.
- **Fix:** Audit each chunk's max_tokens; spot-check actual output token counts from recent runs; bump where heading toward ceiling. Possibly add stop_reason monitoring.
- **Effort:** 1-2 hr.

### 🟡 Phase 3 — Diagnostic + future-proofing (after re-run)

#### FU#1 — Layer 2 preservation audit (chunks → 04_generation synthesis)
- **Origin:** This session, identified gap that existing `arch_03_preservation_audit.py` only covers Layer 1 (DR sources → merge chunks).
- **Problem:** No instrumentation measures how much chunk content survives into `04_generation/` per-pass outputs. Empirical question for arch-03: does Pass 2-6 preserve the merge-layer enriched content (interpretive_frames, anachronism_discipline, contested-tag claims, Gemini cross-disciplinary frames) or silently drop it?
- **Verdict on artifact base** (decided this session):
  - Source: read 19 chunk files in `02_merge/pass_1_*/` directly (not the rebuilt snapshot).
  - Target (primary): `04_generation/pass{2,3,4a,4b,5,6,7b,7c}_*.json` per-pass outputs.
  - Mapping authority: import `_per_chunk_vars()` from `run_persona_pipeline.py` — keeps audit + orchestrator in sync.
- **Recommended metrics:** density (out_chars / chunk_chars per consumer pair); claim survival; citation survival; per-frame-type survival (1-arch-06 specific).
- **Effort:** 3-4 hr.
- **When to build:** after FU#12 lands, so the audit runs on hardened-prompt outputs.

#### FU#8 — Pass 7b bias evaluator audit
- **Origin:** This session.
- **Problem:** `run_persona_pipeline.py:1083+` has a "bias evaluator" that uses Gemini primary + Sonnet fallback. Purpose isn't clearly documented; doesn't appear in spec writeups.
- **Fix:** Read the prompt; understand what's evaluated; verify model choice; document in LLM call inventory.
- **Effort:** 30 min audit + doc update.

### 🟢 Polish

#### FU#19 — Clean panel-voice anchoring in non-human/fictional Pass 0b templates
- **Origin:** OPEN_ITEMS.md "Item 8", deferred from prior session.
- **Problem:** `pass_0b_non_human_organism.md` uses Octopus + Hochner + Godfrey-Smith + Mather as worked examples (22 mentions). `pass_0b_non_human_system.md` uses Whanganui + Te Pou Tupua + iwi-specific scholars (22 mentions). `pass_0b_fictional.md` uses Scheherazade extensively (20 mentions).
- **Why defer-able:** self-anchoring is harmless as long as panel stays at 12. If panel ever expands with a second non-human-organism / non-human-system / fictional voice, those new voices' DR runs would be subtly anchored to the existing panel voice.
- **Fix:** Swap each panel-voice example for a parallel non-panel exemplar.
- **Effort:** ~1 hr per template = ~3 hr total.

#### FU#22 — MergedDossier.register / voice_register Pydantic alias audit
- **Origin:** OPEN_ITEMS.md "Smaller improvements", deferred from prior session.
- **Problem:** Cleanup-deferral-B fixed the Pydantic warning by renaming the attribute to `voice_register` with `alias="register"` + `populate_by_name=True` + `serialization_alias="register"`. Primary site (`run_pass_1_7.py` → `model_dump(by_alias=True)`) is updated. Not audited across all consumers.
- **Risk:** Low probability of breakage but worth verifying if Pass 1.7 ever produces unexpected output.
- **Effort:** ~30 min.

#### FU#15 — Pass 5 A/B test (Sonnet+thinking on a low-stakes voice)
- **Origin:** This session's quality-tuning assessment (operator kept Pass 5 on Opus + thinking under quality lean; flagged for empirical validation).
- **Problem:** Pass 5 has only 4 fields; leverage chain (feeds Pass 7b) is real but not as clear-cut as Derive's. Worth A/B testing on a low-stakes voice.
- **Fix:** Run a low-stakes voice (Cleopatra or Ada Lovelace) twice — once with Pass 5 = Opus + thinking, once with Sonnet + thinking. Compare card quality.
- **Effort:** 1 voice run × 2 = ~2 hr wall + ~$10 cost. Decide based on output.
- **Priority:** low — current default (Opus + thinking) is defensible.

### 🔵 Deferred (waiting on trigger)

#### FU#2 — Chunk Pass 7-pre per-citation verification (parallel batches)
- **Origin:** This session, after Pass 7-pre max_tokens bumped 4× during arch-03 development.
- **Problem:** Linear per-citation verification output blows past Sonnet 4.6's standard output ceiling as cards grow richer. Architectural fix is chunked verification.
- **Fix:** Collect all citation-bearing card fields → batch into groups of ~20-30 → fire N parallel Pass 7-pre-chunk Sonnet calls (max_tokens 16-32K each, well under model ceiling) → aggregate.
- **Trigger:** activate when next voice exceeds 128K Pass 7-pre max_tokens. Until then, 128K + FU#12 prompt hardening (less metadata = fewer citations) likely sufficient.
- **Effort:** ~4-6 hr.

#### FU#21 — Runtime enforcement of `reference_only_passages` Step 1/Step 2 contract
- **Origin:** OPEN_ITEMS.md "Smaller improvements", deferred from prior session.
- **Problem:** Two-tier corpus design (Marley lyrics in private reasoning only) is documented in `personas/HANDOFF.md`. Runtime Voice Pipeline Step 2 assembly code MUST drop the field before rendering.
- **Trigger:** runtime Voice Pipeline workstream starts (out of scope per REBUILD_PLAN — separate workstream).
- **Effort:** unknown until workstream begins.

#### FU#23 — Cross-repo handoff timing (rebuild → runtime integration)
- **Origin:** REBUILD_PLAN.md "Open questions to defer".
- **Problem:** When/how does the rebuild get integrated with the runtime side? Cross-repo handoff (`personas/HANDOFF.md`) and `runtime/flows/shared/council/council_config.json` consumers need to keep working through the transition.
- **Trigger:** gated behind shipping the first rebuilt voice card end-to-end (Phase L).
- **Decision needed:** integration model (continuous merge, batch handoff, parallel-systems window).

#### FU#24 — Settings allowlist tightening
- **Origin:** REBUILD_PLAN.md "Settings note".
- **Problem:** `.claude/settings.local.json` had a Phase A scoped allowlist active (git checkout/pull/merge/push/add/commit, pip install). Post fix-plan + reorg landing (2026-04-19), the allowlist may need adjustment.
- **Trigger:** when active development settles (Phase L sign-off + Plato + a few more voices).
- **Action:** tighten back to read-only-only after architecture work fully lands.

#### FU#11 — Workspace archive cleanup
- **Origin:** This session.
- **Problem:** `_workspace/arch_03_baseline_snapshot/` accumulated archives from multiple Stage 2 attempts. Useful while debugging; bloat after Phase L sign-off.
- **Fix:** After Phase L verdict, prune to: `baseline_*` (Phase L pre-arch-03 reference) + `stage1_v4_run/` (final Stage 1 output) + final shipped Dostoevsky card. Delete intermediate failed-partials.
- **Trigger:** Phase L verdict.
- **Effort:** ~15 min judgment + manual.

#### FU#25 — Split `provocateur_flow.py` into 5 stage files
- **Origin:** RUNTIME_REVIEW_2026_04_20.md "Deferred considerations".
- **Problem:** `provocateur_flow.py` is 1368 lines covering 5 stages (triage, selection, formulation, packaging, ...). Splitting into `triage_flow.py`, `selection.py`, `formulation_flow.py`, `packaging.py` would match the spec's shape.
- **Why deferred:** churn risk on `phase-b-rebuild` branch (~50+ commits ahead of main).
- **Trigger:** after Phase L sign-off + branch merged to main.
- **Effort:** ~3-4 hr (mechanical split + import updates + test runs).

#### FU#26 — Typed `PROMPTS` registry for `load_prompt(name)`
- **Origin:** RUNTIME_REVIEW_2026_04_20.md.
- **Problem:** `load_prompt(name)` in `flows/shared/io.py:95` takes a string name (`{name}.md` under `_PROMPTS_DIR`). A filename rename surfaces only at runtime as `FileNotFoundError` — not silent, but not caught by static checks either.
- **Fix:** Typed `PROMPTS` registry that hardens the coupling.
- **Trigger:** general code-hardening pass.
- **Effort:** ~1-2 hr.

#### FU#27 — Runtime flow-level unit tests
- **Origin:** RUNTIME_REVIEW_2026_04_20.md.
- **Problem:** No flow-level unit tests. Convention is roster-integration against `~/Desktop/AI Assembly/archive/runs/runtime/dev_msc_test/`. Works for current team size; would need restating before growing the contributor set.
- **Trigger:** team-size growth or pre-deployment hardening.
- **Effort:** unknown (significant).

#### FU#28 — Pipeline pass-numbering renumbering
- **Origin:** HANDOFF_PIPELINE_REVIEW.md (deferred during pipeline review session).
- **Problem:** `1a/1b/1c/1d` family vs. `1.1-1.7` merge family naming is confusing for new readers. Pipeline-step-map legend in PIPELINE_REVIEW_FIXES.md was added as a workaround.
- **Fix:** rationalize naming (e.g., 1.0a/1.0b/1.0c/1.0d for research family vs. 1.1-1.7 for merge family, or another scheme).
- **Trigger:** rare opportunity — needs to land alongside other naming changes to avoid mid-stream confusion. Maybe at fresh-project bootstrap.
- **Effort:** ~2-3 hr (renaming + cross-doc references).

#### FU#29 — Smoke regeneration on prompt-touch + cross-voice variance baseline
- **Origin:** External deep-research report critique (2026-04-23) — at 12-voice scale, formal regeneration-on-commit becomes worth doing for variance management.
- **Problem:** When a shared prompt changes (Pass 2-6 user prompts, chunk_runner system, etc.), all 12 voices' affected outputs are silently stale until manual re-run. No CI workflow detects which voices need regeneration. No cross-voice diff/baseline tooling answers "did this change affect Plato + Dostoevsky + Ada Lovelace consistently?"
- **Fix:** Lighter-than-full-regen approach:
  - GitHub Actions / Make target that detects which prompts changed in a commit
  - For each affected prompt → regenerate just that pass for 2 sentinel voices (Plato + Dostoevsky)
  - Diff outputs against baseline; surface deltas in a comment/report
  - Cost: ~$3-5 per change, ~10 min wall (vs. ~$216 + ~12 hr for full 12-voice regen)
  - Use `_manifest.json` cost telemetry for budget tracking
- **Trigger:** after Plato builds (needs first comparison voice for diff baselines).
- **Effort:** ~3-4 hr (CI workflow + diff tooling + sentinel-voice config).

#### FU#30 — Card-richness vs runtime-quality empirical check
- **Origin:** External deep-research report critique (2026-04-23) — "elaborate specs can under-perform simple ones at runtime." Speculative warning, not diagnosis. Worth measuring empirically.
- **Problem:** Card has been progressively enriched (arch-03 + 1-arch-04/06/08 + Pass 7 family). FU#12 trims curator metadata but adds register hardening. There's a point where MORE constraints → WORSE runtime behavior (model has to prioritize across too many instructions; field interactions create unpredictable behavior; over-specified = less generative latitude). We don't currently know if we've crossed that point.
- **Fix:** Comparative chat-test:
  - After Plato builds, chat-test BOTH Plato (clean baseline under FU#12+13 architecture) AND Dostoevsky (current arch-03 card) on the SAME 5-10 prompts
  - Score for voice authenticity, response quality, conversational flow, period-vocabulary deployment, refusal of modern terms
  - If Plato outperforms Dostoevsky on conversational flow despite same architecture → elaboration isn't paying off; consider trimming card schema
  - If Dostoevsky outperforms Plato → richness pays off; keep current direction
  - Adjacent to existing PHASE L CHAT-TEST VALIDATION (OPEN_ITEMS.md §"PHASE L CHAT-TEST VALIDATION") which only tested Dostoevsky in isolation
- **Trigger:** immediately after Plato build completes.
- **Effort:** ~1-2 hr chat-testing + ~30 min scoring.
- **Why high-value despite low-priority:** only empirical check on whether Phase 1 work + arch-03 enrichment pays off at RUNTIME (not just at validation passes).

#### CC#1 — Move `05_primary_text_urls.json` out of `01_research/`
- **Origin:** This session, surfaced reading `paths.py`.
- **Problem:** Historical-layout vestige. In v3.10 the URL list came directly from Perplexity research (true research artifact). 1-arch-07 (2026-04-22) changed the source — URLs now derived post-merge from `02_merge/pass_1_6/works.json` + `passages.json`. Destination path kept for backward-compat but file is no longer a research output.
- **Fix:** Move from `voices/<slug>/01_research/05_primary_text_urls.json` → `voices/<slug>/03_corpus/00_primary_text_urls.json`. Update [`paths.py:71`](../../personas/flows/shared/paths.py:71): `research_dir(...)` → `corpus_dir(...)` + filename change.
- **Trigger:** fresh-project bootstrap of next voice-set after Phase L sign-off.
- **Effort:** ~15 min.

---

## RECENTLY COMPLETED (this session, 2026-04-23)

| Item | Commit | Notes |
|---|---|---|
| ✅ EvidenceTag enum: add `"contested"` | `f2e30fd` | Schema gap that crashed Pass 1.2 retry loop |
| ✅ url_extract canonicalization (Gutenberg + archive.org landing → text) | `1027ced` | Pass 1c-fetch was getting ~5K-char catalogue HTML pages instead of full texts |
| ✅ Pass 7-anachronism + Pass 7a ladder: gpt-5.4 high primary | `7aab7d4` | Was gpt-4.1 (since-retired); validated end-to-end on live Dostoevsky run |
| ✅ Pass 7-pre max_tokens 96K → 128K | `bcd54e8` | Fourth bump in arch-03 cycle; FU#2 is the architectural fix |
| ✅ Pass 1d/4b/6 → Opus 4.7 + thinking | `9cf3fba` | Quality tuning; affects all voices starting Plato |
| ✅ Derive → Opus 4.7 + thinking | `d5d8005` | High-leverage (provocateur_profile drives every runtime turn) |
| ✅ CT compress → Sonnet 4.6 + thinking | `d2b6df4` | 25-50× compression ratios warrant deliberation budget |
| ✅ FU#3 surgical revision loop + SKIP_REVISION_LOOPS escape hatch | `a9f5feb`, `88f0726`, `daf49f0` | Will be removed when FU#13 lands |
| ✅ MAX_REVISION_LOOPS 2 → 1 | `cbe069a` | With surgical mode, single shot is the meaningful unit |
| ✅ Phase M Step 1: openai pip install | (env) | Verified `openai==2.31.0` installed; gpt-5.4 worked |
| ✅ FU#12-A Pass 2-6 register hardening | `3d9eb94` `ffa0b75` `4d258e4` `f34eb30` `8378546` `92fc487` | 6 per-prompt commits |
| ✅ FU#12-B Pass 5 audience-priming | `66017c4` | Loads conference + audience profile; primes existing fields (no new lookup) |
| ✅ FU#13 Architecture 2 — linear Pass 7a-FIX | `a37e4fc` `b34f2cb` | Replaces revision loop entirely; ~150 lines net removed |
| ✅ FU#5 pre-fix snapshot directory | `d4d9baa` | Snapshots 04_generation + 05_validation before fix-pass invalidates |
| ✅ FU#13 idempotency guard | `c9f9503` | Skip fix-pass on restart if `_fix_log.json` exists |
| ✅ FU#13 patcher Sonnet→Opus + 32K | `2e7ebce` | Sonnet adaptive thinking ate budget on 20+ issues; Opus + 32K reliable |
| ✅ FU#13 max_tokens journey + try/except wraps | `125d2f1` `9b81ecb` `5718f18` `11350dc` | 4 ceiling-bumps + try/except wraps to ship Phase 1 baseline despite Sonnet 4.6 128K cap |
| ✅ Phase 1 re-run — first card produced under FU#12+13+5 | (run-15 of 15 in this saga) | 150KB card, 44 fields, REVISION_NEEDED + human_review_pending. 33 patches applied across 2 fix-pass rounds, 0 failed. Snapshot trail preserved. |

---

## CLOSED / OBSOLETE

### Closed by arch-03 + this session

| Item | Why closed | Reference |
|---|---|---|
| ⚫ Phase M Step 2 (5 prior bug fixes — run_pass_1_1.py rewrite, chunk_runner Bug 2/4, run_pass_1_7.py Bug 3/5, run_persona_pipeline.py Bug 6/7) | Files involved fully rewritten by arch-03 commits 1-arch-04/05/06/07/08 | Various arch-03 commits |
| ⚫ D1 (Svidrigailov fire-watchtower vs tavern textual error) | Arch-03 card correctly references "the nameless fireman at Svidrigailov's suicide" | `07_persona_card_assembled.json` audit |
| ⚫ D2 (experiential_reconstruction tags missing on 3 fields) | Arch-03 card has 6 occurrences of the tag | Card audit |
| ⚫ D3 (`projected_categories` → `projection_warning` rename) | `_conventions.py:43` canonical name is `projection_warning` | Schema audit |
| ⚫ D4 (Holbein scene II.iv vs epileptic aura II.v citation disentangle) | Arch-03 card correctly cites "The Idiot II.iv — Rogozhin's copy of Holbein" | Card audit |
| ⚫ D5 (Pass 5 output-characteristics register drift) | Same root cause as FU#12; consolidated | This session |
| ⚫ D6 (`voice_temporal_stance` field missing from card schema) | Field present in `persona_pass_2_identity_boundaries.md` + Pass 2 user prompt | Schema audit |
| ⚫ FU#3 (surgical-patch revision loop) | Superseded by FU#13 (Architecture 2). Code will be removed when FU#13 lands. | Design decision |
| ⚫ FU#4 (Pass 7-anachronism re-fire in revision loop) | Subsumed by FU#13 — fix-pass design re-validates anachronism + 7-pre + 7a together | Design decision |
| ⚫ FU#6 (revision-loop convergence diagnostic) | Slimmed under FU#13 — no loops, no convergence question. Effectiveness metric becomes part of `_fix_log.json` field. | Design decision |
| ⚫ FU#10 original (revision-loop test coverage) | Replaced by FU#10-modified (fix-pass test coverage) | Design decision |
| ⚫ FU#14 (Pass 1a-DR §1-§5 → Opus 4.7 migration) | Operator decision 2026-04-23: stay on 4.6 | Operator call |
| ⚫ FU#18 (Pass 0b DR template field-name reframe) | Verified 2026-04-23: no `world (...)` patterns in current pass_0b prompts. Likely fixed by Wave 1 commit `1fd43f2` (Pass 0b 23 fixes). | Code audit |
| ⚫ FU#20 (Perplexity retry x2 with backoff) | Verified 2026-04-23: `_with_retry()` in run_phase0_1_research.py:64 already retries twice (15s, 60s). Note in OPEN_ITEMS.md was stale. | Code audit |

### Closed before this session (historical reference)

See `OPEN_ITEMS.md` §"Lessons learned (architectural insights)" for arch-03 design rationale + closed items from prior sessions. Notably:
- Position C: DR prompt does NOT inline Perplexity + Gemini (chosen)
- Tailoring ALWAYS runs (not gated on `editorial_rationale`)
- Boddice/Rosenwein/Bradshaw/van der Kolk attributions stripped from base DR prompts
- Negative-prompt strips ("don't think of pink elephant")
- Pipeline-leak strips
- Unified evidence-tag convention (5 frozen `EvidenceTag` values)
- Three missing card-field asks added (`unique_contribution`, `stance_tendency`, `aesthetic_qualities`)

---

## EFFORT TOTALS

| Tier | Items | Effort | When |
|---|---|---|---|
| 🔴 Phase 1 (re-run blockers) | FU#12 + FU#13 + FU#5 | **10-15 hr** | Before re-run |
| 🟡 Phase 2 (before Plato) | FU#7 + FU#10-mod + FU#9 | 4-7 hr | Before Plato run |
| 🟡 Phase 3 (after re-run, diagnostic) | FU#1 + FU#8 | 3-5 hr | After re-run, optional |
| 🟢 Polish | FU#19 + FU#22 + FU#15 | 4-6 hr + 2 hr A/B | Anytime |
| 🔵 Deferred (trigger-based) | FU#2 + FU#11 + CC#1 + FU#21 + FU#23 + FU#24 + FU#25 + FU#26 + FU#27 + FU#28 | trigger-dependent | Various |
| **Critical-path** | FU#12 → FU#13 → FU#5 → re-run | **~12-18 hr + ~60-90 min run** | Now |

---

## RECOMMENDED IMPLEMENTATION ORDER

1. **FU#12** (prompt hardening) — root-cause fix, produces cleaner Pass 2-6 outputs that FU#13 will operate on
2. **FU#13** (Architecture 2 fix-pass) — needs prompt-hardened outputs to test against; supersedes FU#3 code; subsumes FU#4 + FU#6
3. **FU#5** (snapshot directory + revision log) — needs FU#13 to know where the snapshot point is
4. **Re-run from after Pass 1.7** (clear Pass 2 onward; pipeline re-runs Pass 2-6 with hardened prompts → fix-pass → final card)
5. **FU#1** (Layer 2 audit) — validates that FU#12 didn't lose chunk content during synthesis
6. **FU#7** (operator summary) — UX, independent
7. **FU#10-modified** (fix-pass tests)
8. **FU#9** (merge chunk audit) + **FU#8** (bias evaluator audit) — independent
9. **FU#19 + FU#22** (polish, anytime)
10. **FU#15** (Pass 5 A/B) — opportunistic on a low-stakes voice
11. **FU#2** when 128K hit again
12. **FU#11 + CC#1** after Phase L verdict
13. **FU#21 + FU#23** when runtime workstream begins
14. **FU#24** when active development settles
15. **FU#25 + FU#28** at branch merge / fresh project bootstrap
16. **FU#26 + FU#27** general code-hardening / pre-deployment

---

## CROSS-REFERENCE TO HISTORICAL DOCS

- **Original `1-arch-*` fix designs:** `PIPELINE_REVIEW_FIXES.md` §"1-arch-04 through 1-arch-08"
- **Phase B architectural rationale:** `REBUILD_PLAN.md` (PB#1-9 design decisions)
- **Phase L execution findings:** `OPEN_ITEMS.md` §"PHASE L EXECUTION FINDINGS", §"PHASE L CHAT-TEST VALIDATION"
- **Phase L.8 quality verdict:** `PHASE_L8_QUALITY_REPORT.md`
- **arch-03 plan + amendments:** `ARCH_03_ADDITIVE_MERGE_PLAN.md`
- **arch-03 Stage 2 handoff:** `HANDOFF_ARCH_03_STAGE_1_RESTART.md`
- **Phase M handoff (now mostly closed-out):** `HANDOFF_PHASE_M.md`
- **Pipeline review handoff:** `HANDOFF_PIPELINE_REVIEW.md`

When historical context is needed, read those. For active tracking + implementation order, **this doc is authoritative**.

### Important note on PIPELINE_REVIEW_FIXES.md scope

That doc retains historical/design context for the architectural follow-ups (FU#1-13 — now consolidated here as authoritative) and for the pipeline review session's wave structure.

**Wave 1/2/3 SURVIVES items: APPLIED days ago** via commits `bcf77ad` (wave-1/pass-0a, 4 fixes), `abdb13b` (wave-1/pass-1b, 13 fixes), `1fd43f2` (wave-1/pass-0b, 23 fixes), `cf25a79` (wave-2/pass-1c-1d, 11 fixes; 1d-06 deferred), `5975531` (wave-3/merge-prompts, period-vocab + pre-seed verify). ~51 fixes applied total. The "PROPOSED: 99 / APPLIED: 0" status counts at the bottom of PIPELINE_REVIEW_FIXES.md (line 2015-2024) are STALE — never updated when the Wave commits landed. The body of the doc shows individual `APPLIED` markers per item.

**Wave 4 (Pass 2/3/4a/4b/5/6 + CT threading prompt review)** was forward-referenced in PIPELINE_REVIEW_FIXES.md but never formally started. arch-03 (1-arch-04 + 1-arch-05) already modified these prompts substantially. **FU#12 (curator-metadata prompt hardening) is a SPECIFIC fix for a newly-discovered issue** (gpt-5.4's complaint about curator-metadata leakage in this session's run). It's not in Wave 4's original scope but lands on the same prompt files. If you want a "Wave 4 review" pass on these prompts in addition to FU#12, that would be a separate item — not currently tracked because the FU#12 audit is likely sufficient.

**Other orphan items in PIPELINE_REVIEW_FIXES.md:** 2-01 (Pass 2 stale user prompt) and 2-04 (monitor-not-fix). These are minor/already-handled. Not promoted to FU# items here.

---

*Maintained: append new follow-ups under appropriate priority tier; move closed items to CLOSED section with reasoning + commit reference.*
