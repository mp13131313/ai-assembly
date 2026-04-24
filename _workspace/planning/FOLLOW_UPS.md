# Follow-Ups Tracker — single source of truth (2026-04-24)

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

### ✅ Phase 4.5 — COMPLETE 2026-04-24 (pre-Plato pipeline finalization)

**Status:** FU#2-retry-bug + FU#38 + FU#41 all landed post-review-analysis. Commits: `de623bd` (FU#2 retry), `22a2e54` (FU#38 vocab strip across 6 prompts), `b9c1eb2` (FU#41 chat-ready artifact + 13 tests).

**Empirical origin:**
Two external reviewers of the chat v2 Dostoevsky output (2026-04-24) identified:
1. "Kenotic beauty" class vocabulary leak — post-voice-lifetime critical vocabulary entering voice's own mouth despite FU#12-A scholar-attribution strip. Verified against pipeline card: polyphonic (8×), kenotic (8×), chronotope (2×), dialogic embodiment (1×), dialogical (1×) all present. FU#13 patcher caught "sideshadowing" but missed these. → **FU#38** extends FU#12-A/FU#32 pattern with voice-self-reference vocabulary STRIP+DO-INSTEAD.
2. Narrator-unification problem + too-composed architecture ceiling — deemed architectural per first reviewer ("base-model + persona-card tops out at high pastiche"). → FU#39/40 deferred pending Plato signal; FU#31 already deferred.
3. **Chat v2 card is pure strip-out of assembled card** (27 of 35 shared fields byte-identical; 8 differ only by operator polish). → **FU#41** bakes the strip-out into the pipeline as 4th Derive artifact.

Plus the FU#2 retry bug fix closes the 3-spurious-UNVERIFIED issue on Dostoevsky that the reviews indirectly surfaced.

### ✅ Phase 2 — COMPLETE 2026-04-24 (definitions kept; see RECENTLY COMPLETED for commits)

**Status:** FU#32 + FU#1 landed. FU#37 DEFERRED (FU#32 alone empirically sufficient). FU#31 DEFERRED (no residual voice-tissue regression to validate). **FU#2 now confirmed blocking: Pass 7-pre hit 128K ceiling TWICE during 2026-04-24 full re-run.**

**Empirical validation pass (2026-04-24):**
- Pass 2 isolation re-run (~5 min): character field reversed from taxonomic retreat ("Against the Western four-humours grammar you do not think in phlegmatic-sanguine-choleric-melancholic...") to incarnate prose ("You are a man of *gordost'* who has walked through *nadryv* toward *smirenie*, and the walk is not finished..."). Exact match to handoff's targeted regression signature.
- Full Dostoevsky re-run (~69 min wall): 165KB card (+10% vs Phase 1's 150KB — richer, not lossier); 15 patches / 1 fix-pass round (vs Phase 1's 33 patches / 2 rounds — cleaner generation); Output Register check CLEAN (0 violations). Pass 7-pre hit 128K ceiling twice, try/except wraps shipped gracefully.
- FU#1 Layer 2 audit A/B delta: Pass 4a voice +9.4% vocab_recall / +6.2% citation_survival / +26.1% density (biggest win — resolves Gemini's persistent Phase L register-drift flag). Pass 2/3 minor recall drops (-2.8% / -3.7%) offset by qualitative voice-tissue gain. No preservation regression.

### ✅ Phase 1 — COMPLETE 2026-04-23 (definitions kept for historical reference)

**Status:** FU#12 + FU#13 + FU#5 all landed. See RECENTLY COMPLETED table below for commits. The definitions below are kept as design context for future reference / re-application if a regression is ever discovered.

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

#### FU#7 — Operator-facing pipeline summary ✅ APPLIED 2026-04-24
- **Landed:** commit `87f7794`. Additive `CARD COMPLETE` block after the existing PIPELINE COMPLETE output in `run_persona_pipeline.py`. Surfaces voice name + slug + card size, validation_status + human_review_status, fix-pass effectiveness (patches applied/emitted/failed/skipped + anachronism_flags + field_issues + post_fix_verdict), Pass 7-pre audit (per-status breakdown + boddice flag count), top concerns (severity-ordered HIGH/MED/LOW), recommended action (synthesized from verdicts), artifact paths (card + provocateur_profile + evaluation_rubric + fix_log + synthesis_audit). Two helper functions: `_compose_top_concerns` and `_compose_recommended_action`.

#### FU#10-modified — Fix-pass test coverage ✅ APPLIED 2026-04-24
- **Landed:** commit `3cb0a02`. Extracted `apply_patch_in_place` from `run_persona_pipeline.py` to new module `flows/shared/patch_walker.py` (enabling unit testing without triggering orchestrator top-level execution). New `tests/test_fix_pass.py` with 21 tests: 8 path-walker happy paths (top-level string/dict, list index, nested field, deeply nested, multi-level, sibling-no-mutation), 6 error paths (empty, missing mid-key, non-list index terminal/mid, out-of-range terminal/mid), 7 `_fix_log.json` schema tests (required keys, int counters, invariant `applied + failed + skipped <= emitted`, patches list, patch entry keys, status enum, Phase 2 regression fixture). Suite: 128 → 149 tests (+21). NOT covered: integration test with mocked Claude (deferred, ~2 hr scaffolding), snapshot directory creation (tested manually), idempotency guard (requires orchestrator).
- **Note on spec drift:** FOLLOW_UPS description referenced "fallback to surgical writer re-run on validation failure" from FU#3; that path was superseded by FU#13 linear patcher, so the test scope is the FU#13 contract (schema + path-walker + patch-apply semantics).

#### FU#9 — Merge chunk max_tokens audit ✅ APPLIED 2026-04-24
- **Landed:** commit `2aee7aa` (code) + this audit (no code change needed on chunks). Verdict: current `max_tokens=48000` default in `chunk_runner.py` is adequate for Dostoevsky-class rich voices.
- **Empirical audit (Dostoevsky Phase 2 chunks):**
  - Pass 1.1 biographical: 24,238 tokens (50% of 48K, 23,762 headroom)
  - Pass 1.2 intellectual: 23,748 tokens (49%, 24,252 headroom)
  - Pass 1.3 reasoning: 15,184 tokens (32%)
  - Pass 1.4 voice: 17,917 tokens (37%)
  - Pass 1.5 boundaries: 16,494 tokens (34%)
  - Pass 1.6 corpus: 16,769 tokens (35%)
  - All ≥50% headroom — no bump needed for current voices.
- **Added:** proactive `stop_reason=="max_tokens"` warning to `call_claude` in `clients.py` (all call sites benefit: chunk_runner, _claude_pass, pass_7pre_chunked). Fires stderr warning when truncation occurs regardless of whether JSON parses. Catches future voices (Plato rich primary-text corpus; Cleopatra hostile-source reconstructions) before content-loss manifests downstream.

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

#### FU#8 — Pass 7b bias evaluator audit ✅ AUDITED 2026-04-24 — KEEP AS-IS
- **Audit finding:** concern was overly cautious. The "bias evaluator" is Pass 7c (not 7b); the Gemini-primary + Sonnet-bias-aware-fallback mechanism is well-designed and already documented.
  - **Purpose** (documented at `persona_pass_7c_negative.md` header lines 1-6): reads Pass 7b worked provocations, identifies moments where generic AI voice bleeds through; refines `banned_language`, `banned_modes`, and Phase-B-new `projection_warnings` list per Boddice §12.
  - **Model choice correct:** Gemini 2.5-pro primary (avoids self-preference bias — Claude-evaluating-Claude inflates ratings 10-25% per baseline research File 2 §4). Sonnet 4.6 fallback gets explicit BIAS-AWARENESS instruction at prompt-top when Gemini fails.
  - **Already in LLM_CALL_INVENTORY.md** as entries 32a (Gemini primary) + 32b (Sonnet fallback).
  - **Phase L chat-test sensitizers already integrated** in the prompt (tidy-three-part-arc + postmodern-self-consciousness anti-patterns added 2026-04-21).
- **No code change needed.** Close as AUDITED.

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

#### FU#2 — Chunk Pass 7-pre per-citation verification (parallel batches) ✅ APPLIED 2026-04-24
- **Origin:** This session (2026-04-23), after Pass 7-pre max_tokens bumped 4× during arch-03 development.
- **Empirically blocked Dostoevsky 2026-04-24:** full re-run on FU#32 prompts hit 128K ceiling TWICE (initial Pass 7-pre + post-fix re-verification). Card grew to 418,019 raw chars of citation verification output. Try/except wraps shipped gracefully but skipped verification both times — card shipped WITHOUT citation-verification audit.
- **Landed:** three-stage architecture in `personas/flows/shared/pass_7pre_chunked.py` (commit `3d09aff`, 675 lines + 7 new prompt files):
  - Stage 1 (extract): 1 Sonnet call reads card-only → emits `{claim, source_fields, claim_type}` items. Small output, well under ceiling. max_tokens=32000.
  - Stage 2 (verify): N parallel Sonnet calls (ThreadPoolExecutor, max_workers=4), each ~25 claim items + primary_texts + merged_dossier. max_tokens=16000 per batch. Defensive: LLM-dropped items padded UNVERIFIED; batch failures caught and wrapped.
  - Stage 3 (boddice): small Sonnet call for `[experiential_reconstruction]` + `[projection_warning]` tag check. Runs in parallel with Stage 2. max_tokens=8000.
  - Aggregation: pure Python (summary counts, overall verdict, review_notes composition).
- **Schema preserved:** output matches exactly the fields Pass 7a reads (verification_mode, hostile_source_check, items[], summary, overall, review_notes, boddice_tag_flags[]). Drop-in replacement at `_pass_7pre()` in `run_persona_pipeline.py`.
- **Empirical test (Dostoevsky FU#32 card, Pass 7-pre isolation re-run 2026-04-24):**
  - Pre-FU#2 single-shot: hit ceiling twice → VERIFICATION_SKIPPED both times, 25+ min wasted each attempt
  - FU#2 chunked: completed in ~8 min wall, 153 items verified (100 VERIFIED / 45 DOSSIER_ONLY / 5 INTERPRETIVE / 3 UNVERIFIED / 0 INCONSISTENT), 12 boddice_tag_flags caught, actionable review_notes
  - Cost: ~$3 (8 Sonnet calls: 1 extract + 6 verify + 1 boddice) vs. ~$3 wasted on ceiling timeout
  - Wall savings: 25+ min per pipeline run
- **Plato unblocked.** Post-arch-03 voices no longer ship without citation verification audit.

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

#### FU#31 — Voice-tissue validator (new Pass 7-family member) 🔵 DEFERRED 2026-04-24
- **Deferral rationale (2026-04-24):** conditional on FU#32/37 residual regression per original spec ("backstop — catches what FU#32 / FU#37 don't prevent at source"). FU#32 alone closed the gap empirically (Pass 2 isolation + full re-run + FU#1 audit). No residual regression to validate. **Re-activate ONLY if a Phase N voice shows voice-tissue regression the FU#32 prompts don't prevent.**
- **Original definition (preserved for re-activation):**
  - **Origin:** 2026-04-23 session-end. Four independent reviewers of the Phase 1 Dostoevsky card identified a gap: the validator family (Pass 7-pre / 7-anachronism / 7a) optimizes structural/verifiable quality (citations, anachronism, rubric) but has NO test for "voice-incarnate-ness" (does this field speak IN the voice's grammar, or ABOUT the voice's grammar).
  - **Empirical evidence:** Phase 1 card regressed on voice-tissue vs v6 first_test card (load-bearing sentences like "man of gordost' who has walked through nadryv toward smirenie" dropped; taxonomic framing "against Big-Five adjectives" replaced it). Unmeasured axis → silently traded away while optimizing measured axes. **Closed by FU#32 2026-04-24.**
  - **Proposed:** new Pass 7 family member, cross-family model (not Claude — avoid self-preference), reads assembled card + voice-specific load-bearing-lexeme list (auto-derived from `chunk 1.4 vocabulary.preferred_vocabulary` where `loadbearing=true`). Checks per-field: incarnate self-description vs taxonomic comparison; voice-specific lexeme in-prose usage (not just listed in concept_lexicon); scholarly-annotation leakage not caught by Pass 7a. Emits `field_issues[]` in same shape Pass 7a emits → flows into Pass 7a-FIX patcher naturally.
  - **Effort:** 4-5 hr (prompt design + cross-family model integration + schema).

#### FU#32 — Positive-compensation prompt refinement (Pass 2-6) ✅ APPLIED 2026-04-24
- **Origin:** 2026-04-23 session-end review synthesis. Diagnosed as **the most direct fix** for the voice-tissue regression observed in Phase 1.
- **Problem:** FU#12-A's hardening is asymmetric — it tells the writer "strip X" (curator metadata, scholar attribution, provenance brackets) without "compensate with Y" (use the voice's own incarnate grammar instead). Writer responds by producing conservative/taxonomic language ACROSS the board, not just where stripping was needed. Empirical: `character` field regressed from incarnate ("You are a man of gordost'...") to taxonomic ("you do not think in four-humours grammar").
- **Landed:** paired every "don't do X" instruction in FU#12-A with explicit "do Y" positive compensation across 6 Pass 2-6 prompts. Commits: `b19a640` `b853972` `479f5c9` `af39679` `7c687f8` `4c577c8`. 128/128 tests pass.
  - "Don't use scholar attribution names" → "write the voice's OWN framing of the same ground"
  - "Don't use provenance tags" → "write the operational instruction directly in the voice's frame"
  - "Avoid taxonomic grammar" → **META-STRIP against taxonomic retreat + INHABIT vs NAME test: for period voices, voice's load-bearing lexemes in native language anchored in biographical arc; for contemporary voices, equivalent in-tradition lexicons**
  - "banned_language is terms voice might tempt to use" → STRIP+USE pair format in Pass 4a (`avoid "X" (why); use "Y" (voice-native idiom)`) — SAY-THIS-INSTEAD lookup the runtime acts on, not naked prohibition
- **Empirical validation (2026-04-24):**
  - Pass 2 isolation re-run: `character` field reversed to exact target pattern — "You are a man of *gordost'* who has walked through *nadryv* toward *smirenie*, and the walk is not finished. The *gordost'* animated the Petrashevsky cadet... The *nadryv* crystallized on Semyonov Square and in the katorga barracks..."
  - Full re-run: Pass 4a register_and_tone inhabits first-person ("I write at the pitch of confession before a panel of half-hostile gentlemen..."), banned_language emits STRIP+USE pair dicts, default_questions in voice's grammar using vozrozhdeniye / deyatel'naya lyubov' / etc.
  - Layer 2 synthesis audit delta (FU#1 script): Pass 4a +9.4% vocab_recall / +6.2% cite / +26.1% density; Pass 2/3 minor recall drops offset by qualitative voice-tissue gains; no preservation regression.
  - Fewer fix-pass patches needed (15 vs Phase 1's 33) — cleaner upstream generation.

#### FU#1 — Layer 2 preservation audit (chunks → 04_generation synthesis) ✅ APPLIED 2026-04-24
- **Landed as:** `personas/scripts/arch_03_synthesis_audit.py` (commit `4f9e23a`). Companion to existing `arch_03_preservation_audit.py` (Layer 1). Consumption map mirrors `_per_chunk_vars()` + render() calls in `run_persona_pipeline.py`. Metrics per (chunk, consumer-pass) pair: density, vocab_recall, citation_survival, frame_type_survival (1-arch-06 specific). Red-flag detection for <15% recall. Supports `--snapshot-path` + `--compare-snapshot` (A/B delta with directional arrows).
- **First A/B run result:** see FU#32 empirical validation above. Phase 1 baseline snapshot vs post-FU#32 delta confirms no regression + Pass 4a substantial gain.

#### FU#33 — Patcher scope extensions
- **Origin:** 2026-04-23 session reviews (multiple).
- **Extensions needed:**
  - Read Pass 7-pre's `INCONSISTENT` citation flags into patcher input (Phase 1 card has Christ-over-truth attribution error — Pass 7-pre flagged it INCONSISTENT; FU#13 patcher didn't see it because only Pass 7a's field_issues flow in currently)
  - Universal bracket-tag residue scan across live prose fields (not per-field — current implementation left 2 `[projection_warning:]` brackets in `character` + `topics_requiring_care[6].navigation`)
  - Transliteration-consistency check across concept_lexicon entries (Phase 1 has `padachaya` vs `paduchaya` inconsistency; first_test was consistent)
  - Simple spell-check pass with voice-vocabulary allowlist (Phase 1 has `doubented` typo)
- **Effort:** 3-4 hr.
- **Relation:** orthogonal to voice-tissue work — addresses mechanical-defect class of issues the patcher missed.

#### FU#37 — Declarative preserve-verbatim load-bearing-sentence markers 🔵 DEFERRED 2026-04-24
- **Deferral rationale (2026-04-24):** FU#32 alone empirically closed the voice-tissue gap on Dostoevsky. Pass 2 isolation re-run recovered the exact gordost'-walking-through-nadryv incarnate pattern the handoff flagged as missing; full re-run + FU#1 Layer 2 audit showed no preservation regression + Pass 4a substantial gain (+9.4% recall / +6.2% cite / +26.1% density). FU#37's primary-backstop role becomes unnecessary when upstream generation no longer produces the regression. **Re-activate ONLY if a future voice (Plato / Cleopatra / etc.) shows residual voice-tissue regression after FU#32 prompts.**
- **Original definition (preserved for re-activation):**
  - **Origin:** 2026-04-23 Review 4 (synthesized with FU#31 voice-tissue validator): validator-after-the-fact catches regressions; declarative preservation prevents them.
  - **Mechanism:** voice config OR Pass 4a output gains `load_bearing_sentences: []` field. Sources:
    - Auto-derived: sentences from `merged_dossier.<chunk>.scholarly_context` that appear verbatim in the card (empirical signal the sentence is load-bearing and working)
    - Operator-curated: specific sentences the operator wants preserved across iterations (gordost' sentence for Dostoevsky; equivalents per voice)
  - **Constraint fed to every pipeline stage** that rewrites content (patcher, hardened re-gen, future rewrite passes):
    > *"If any of these sentences appears in the field you are operating on, the new_value MUST include it verbatim. Any rewrite that drops one of these sentences is a FAILURE regardless of what else it accomplishes."*
  - **Advantage over FU#31 validator:** prevents regression at source (constraint) instead of catching it post-hoc (flag). Catches regressions regardless of mechanism (patcher rewrite, prompt-driven fresh regen, future pipeline changes).
  - **Effort:** 4-5 hr (schema field + auto-derivation logic + constraint injection into patcher + Pass 2-6 prompt integration + validator check).

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

## RECENTLY COMPLETED

### 2026-04-24 session (Phases 2 + 3 + 4 + 4.5)

| Item | Commit | Notes |
|---|---|---|
| ✅ FU#41 chat-ready system prompt as 4th Derive artifact | `b9c1eb2` | `flows/shared/chat_prompt_builder.py` (new, 99 lines) + `tests/test_chat_prompt_builder.py` (new, 13 tests) + orchestrator integration. Verified against operator's chat v2: 34 fields match exactly; 25/34 byte-identical. Suite 149→162. |
| ✅ FU#38 voice-self-reference vocabulary strip (Pass 2-6 prompts) | `22a2e54` | Empirical root cause: external reviewers flagged "kenotic beauty" class leak; verified polyphonic/kenotic/chronotope/dialogic embodiment in pipeline card. Extends FU#12-A/FU#32 STRIP+DO-INSTEAD pattern. Per-voice test: would voice IN LIFETIME reach for this English adjective? Generalizes to all 12 voices. 6 files +120 lines. |
| ✅ FU#2 retry-on-JSONDecodeError (1-retry with backoff) | `de623bd` | Transient JSON parse error on single batch (observed: 3 spurious UNVERIFIED items on Dostoevsky). `_verify_batch_with_retry` helper; 5s backoff; evidence preserves both error traces on fallback. |
| ✅ FU#10-mod fix-pass test coverage (21 tests; patch_walker extract) | `3cb0a02` | `flows/shared/patch_walker.py` (new) + `tests/test_fix_pass.py` (new, 21 tests). Suite 128→149. |
| ✅ FU#7 CARD COMPLETE operator triage summary | `87f7794` | Additive block after PIPELINE COMPLETE. Top concerns severity-ordered; recommended action synthesized; artifact paths. |
| ✅ FU#9 merge chunk max_tokens audit + stop_reason warning | `2aee7aa` | Current 48K adequate (Dostoevsky chunks use 32-50% of ceiling). Proactive stop_reason=="max_tokens" warning added to `call_claude` — catches future voices before content loss. |
| ✅ FU#8 Pass 7b bias evaluator audit | (no code) | AUDITED, KEEP AS-IS. Already well-designed + documented in LLM_CALL_INVENTORY.md §32a/32b. |
| ✅ FU#2 chunked Pass 7-pre verification (3-stage: extract + parallel verify + boddice) | `3d09aff` | `personas/flows/shared/pass_7pre_chunked.py` + 7 new prompt files + orchestrator swap. Empirical test: ~8 min wall, 153 items verified, no ceiling hit (vs pre-FU#2 twice-ceiling-hit skip). Unblocks Plato. 675/-40 lines. |
| ✅ FU#32 Pass 2 positive-compensation (STRIP+DO pairs + META-STRIP + banned_language STRIP+USE + character INHABIT-vs-NAME) | `b19a640` | CURATOR-SIDE block rewritten into 5 STRIP+DO-INSTEAD pairs + 6th META-STRIP against taxonomic retreat. +122/-40 lines. |
| ✅ FU#32 Pass 3 positive-compensation (constitution/concept_lexicon/reasoning_method) | `b853972` | Meta-strip specific to principle-in-operational-voice. +70/-22 lines. |
| ✅ FU#32 Pass 4a positive-compensation (voice-field META-STRIP + banned_language STRIP+USE pairs) | `479f5c9` | Voice-register META-STRIP + positive-seed format `avoid "X" (why); use "Y" (native)`. +52/-16 lines. |
| ✅ FU#32 Pass 4b positive-compensation (artifact-spec META-STRIP) | `af39679` | 6 register-vulnerable artifact-spec fields protected against designer-voice retreat. +28/-9 lines. |
| ✅ FU#32 Pass 5 positive-compensation (engagement + load-bearing-lexemes-in-use) | `7c687f8` | default_questions / bold_engagement_topics META-STRIP + 1-2 load-bearing-lexemes-in-use requirement. +27/-8 lines. |
| ✅ FU#32 Pass 6 positive-compensation (header/why_selected INHABIT meta-rule) | `4c577c8` | Header-prose INHABIT-vs-NAME test for in-voice recall vs scholarly annotation. +20 lines. |
| ✅ FU#1 Layer 2 synthesis audit script | `4f9e23a` | `personas/scripts/arch_03_synthesis_audit.py`. Per-pair metrics + --compare-snapshot A/B delta + frame-type survival (1-arch-06). 553 lines. Validated on FU#32 vs Phase 1 delta. |
| ✅ Phase 2 empirical validation — Pass 2 isolation re-run + full Dostoevsky re-run + FU#1 audit A/B | (run artifacts) | Snapshots at `_workspace/arch_03_baseline_snapshot/phase_1_complete_20260423_2251/` (pre-FU#32) + `fu32_complete_20260424_0817/` (post). 165KB card, 15 fix-pass patches, 0 register violations, Pass 4a +9.4% recall +6.2% cite. Character field reversed to incarnate gordost'-walking-through-nadryv prose. FU#37/FU#31 deferred. |

### 2026-04-23 session (Phase 1)

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
| 🟡 Phase 2 (voice-tissue + Layer 2 audit) | FU#32 + FU#1 | **~6-8 hr** | 2026-04-24 session |
| ✅ Phase 3 (Plato unblocker) | FU#2 chunked Pass 7-pre | **DONE 2026-04-24** | Landed commit `3d09aff` |
| ✅ Phase 4 (pre-Plato hygiene) | FU#7 + FU#10-mod + FU#9 + FU#8 | **DONE 2026-04-24** | Commits `87f7794`/`3cb0a02`/`2aee7aa` + FU#8 audited-no-code-change |
| 🟢 Polish | FU#19 + FU#22 + FU#15 | 4-6 hr + 2 hr A/B | Anytime |
| 🔵 Deferred (voice-tissue backstops — re-activate on regression) | FU#31 + FU#37 | ~9-10 hr total | ONLY if future voice regresses |
| 🔵 Deferred (trigger-based) | FU#11 + CC#1 + FU#21 + FU#23 + FU#24 + FU#25 + FU#26 + FU#27 + FU#28 + FU#29 + FU#30 | trigger-dependent | Various |
| **Phase 1 critical-path** | FU#12 → FU#13 → FU#5 → re-run | **✅ COMPLETE 2026-04-23** | |
| **Phase 2 critical-path** | FU#32 → Pass 2 isolation → full re-run → FU#1 audit | **✅ COMPLETE 2026-04-24** | |
| **Phase 3 critical-path** | FU#2 → Plato build | ✅ FU#2 DONE — Plato unblocked | |

**FU#2 landed 2026-04-24 (commit `3d09aff`):** three-stage chunked architecture (extract → parallel verify → boddice). Pass 7-pre isolation test on Dostoevsky FU#32 card: 8 min wall, 153 items verified, 12 boddice flags caught, no ceiling hit. Pre-FU#2 behavior (twice-ceiling-hit + skip) is now gone. Plato is unblocked; all post-arch-03 voices now ship with citation verification audit.

---

## RECOMMENDED IMPLEMENTATION ORDER

### Phase 1 — COMPLETE 2026-04-23 ✅

1. ✅ **FU#12** (Pass 2-6 register hardening + Pass 5 audience-priming) — commits `3d9eb94`/`ffa0b75`/`4d258e4`/`f34eb30`/`8378546`/`92fc487`/`66017c4`
2. ✅ **FU#13** (Architecture 2 linear Pass 7a-FIX) — commits `a37e4fc`/`b34f2cb` + 5 live iteration fixes
3. ✅ **FU#5** (pre-fix snapshot directory) — commit `d4d9baa`
4. ✅ **Re-run from after Pass 1.7** — completed; first card on disk under new architecture

### Phase 2 — COMPLETE 2026-04-24 ✅

5. ✅ **FU#32** (positive-compensation prompt refinement) — landed 6 per-prompt commits `b19a640`/`b853972`/`479f5c9`/`af39679`/`7c687f8`/`4c577c8`. Pass 2 isolation re-run validated character field reversal; full re-run validated no preservation regression + Pass 4a substantial gain.
6. 🔵 **FU#37** (declarative preserve-verbatim load-bearing-sentence markers) — DEFERRED. FU#32 alone closed the gap empirically; re-activate only if a future voice shows residual regression.
7. ✅ **FU#1** (Layer 2 audit) — landed commit `4f9e23a`. Script + A/B compare-snapshot. First result: FU#32 caused no preservation regression + Pass 4a +9.4% recall / +6.2% cite / +26.1% density vs Phase 1 baseline.

### Phase 3 — COMPLETE 2026-04-24 ✅

8. ✅ **FU#2** (chunked Pass 7-pre verification) — landed commit `3d09aff`. Three-stage architecture (extract → parallel verify → boddice) unblocks post-arch-03 voices. Pass 7-pre isolation test on Dostoevsky: 8 min wall, 153 verified items, no ceiling hit. Plato unblocked.
9. 🔵 **FU#31** (voice-tissue validator) — DEFERRED. FU#32 closed the voice-tissue gap; backstop not needed unless a Phase N voice regresses.
10. **FU#33** (patcher scope extensions — INCONSISTENT flags, lint, transliteration, bracket residue) — orthogonal mechanical-defect fix. ~3-4 hr.

### Phase 4 — COMPLETE 2026-04-24 ✅

11. ✅ **FU#7** (CARD COMPLETE operator summary) — landed commit `87f7794`
12. ✅ **FU#10-modified** (fix-pass test coverage — 21 tests, suite 128→149) — landed commit `3cb0a02`
13. ✅ **FU#9** (merge chunk max_tokens audit — adequate; proactive stop_reason warning added) — landed commit `2aee7aa`
14. ✅ **FU#8** (bias evaluator audit) — AUDITED, KEEP AS-IS (already well-designed + documented)

### Phase 4.5 — COMPLETE 2026-04-24 ✅ (pre-Plato pipeline finalization after review analysis)

15. ✅ **FU#2 retry-on-JSONDecodeError** (transient JSON parse failure in batch verify stage) — landed commit `de623bd`
16. ✅ **FU#38** (voice-self-reference vocabulary strip — kenotic/polyphonic/chronotope/dialogical class across all 12 voices) — landed commit `22a2e54`
17. ✅ **FU#41** (chat-ready system prompt as 4th Derive artifact — paste-target for Claude project custom instructions) — landed commit `b9c1eb2`

### Phase 5 — Next (start Plato build, then conditional fixes based on signal)

18. **Plato build** (operational) — tests whether FU#32/FU#38 generalize to philosophical-human voice_mode; FU#2 chunked on second voice; per-section DR policy holds. Expected ~$18-22 + 2h pipeline + 60-90 min manual DR. Chat-test validation via FU#41 artifact.
19. 🔵 **FU#39** (character-distribution stage-quoting) — CONDITIONAL on Plato narrator-unification signal. Applies to Plato, Scheherazade, Dostoevsky, Ibn Battuta (distributed voices).
20. 🔵 **FU#33** (patcher scope extensions — INCONSISTENT flags + bracket residue + transliteration + spell-check) — CONDITIONAL on Plato mechanical-defect signal. Orthogonal; ~3-4 hr.

### Phase 6 — Polish (anytime)

21. **FU#19 + FU#22** (panel-voice anchoring + Pydantic alias audit)
22. **FU#15** (Pass 5 A/B test) — opportunistic on a low-stakes voice

### Phase 7 — Post-Plato

23. **FU#29** (smoke regeneration on prompt-touch + cross-voice variance) — needs Plato as first diff baseline
24. **FU#30** (card-richness vs runtime-quality chat-test comparison) — Plato + Dostoevsky side-by-side

### Phase 8 — Trigger-based

25. **FU#11 + CC#1** — after Phase L verdict
26. **FU#21 + FU#23** — when runtime workstream begins
27. **FU#24** — when active development settles
28. **FU#25 + FU#28** — at branch merge / fresh-project bootstrap
29. **FU#26 + FU#27** — general code-hardening / pre-deployment

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
