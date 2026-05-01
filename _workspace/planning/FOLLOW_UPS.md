# Follow-Ups Tracker — FROZEN historical ledger (as of 2026-05-01)

**Status:** This doc is the historical ledger of FU#1–62 filed across the project's lifetime (LANDED / IN PROGRESS / DEFERRED / WITHDRAWN). **No new entries will be added going forward.** Existing FU# references in code, commits, prompts, and docs remain valid; they resolve to entries here.

**For NEW items going forward, file in the relevant subfolder OPEN_ITEMS:**
- Runtime workstream → `_workspace/planning/runtime/OPEN_ITEMS.md`
- Voices workstream → `_workspace/planning/voices/OPEN_ITEMS.md`
- Cross-cutting rules / calibration → `_workspace/planning/ONBOARDING.md`

Cross-cutting FUs that affected both threads (FU#42 split-card, FU#60 thinking observability, FU#61 voice-side Layer-1 quality_criteria, FU#62 validation regen-on-flag) stay here as canonical entries. New cross-cutting items file in BOTH subfolder OPEN_ITEMS with mutual cross-references.

No new FU# numbering. The ledger is closed at FU#62.

See `code/CLAUDE.md` §"Planning / tracking conventions" for the full workflow.

---

## Original purpose (preserved as historical context)

**Purpose** (2026-04-24): consolidated all open work + recently-completed work + closed/superseded items previously tracked across `OPEN_ITEMS.md`, `PIPELINE_REVIEW_FIXES.md` (FU sections), `HANDOFF_PHASE_M.md`, and `REBUILD_PLAN.md` (Open questions to defer).

**Superseded for tracking purposes** (the docs this one consolidated from):
- `PIPELINE_REVIEW_FIXES.md` §"FU#1-13" (still authoritative for `1-arch-*` history)
- `OPEN_ITEMS.md` §"PHASE M PUNCH LIST", §"Smaller improvements", §"Code-cleanup-on-fresh-project"
- `REBUILD_PLAN.md` §"Open questions to defer"

This doc itself is now superseded for new tracking by the per-workstream OPEN_ITEMS docs (per the freeze above). It retains historical authority for FU#1–62.

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

#### FU#19 — Clean panel-voice anchoring in non-human/fictional Pass 0b templates ✅ APPLIED 2026-04-26
- **Origin:** OPEN_ITEMS.md "Item 8", deferred from prior session.
- **Problem:** `pass_0b_non_human_organism.md` used Octopus + Hochner + Godfrey-Smith + Mather as worked examples (13 mentions). `pass_0b_non_human_system.md` used Whanganui + Te Pou Tupua + iwi-specific scholars (24 mentions). `pass_0b_fictional.md` used Scheherazade extensively (35 mentions).
- **Empirical concern:** self-anchoring biases new same-class voices toward the existing panel voice; even within current panel, generating Octopus/Whanganui/Scheherazade against templates that use them as exemplars is subtly self-referential.
- **Approach taken:** different fix per template based on audit:
  - **Organism (Octopus):** worked examples were single-anchor "(For Octopus: X. For other organisms: equivalent)" pattern. **Genericized** all single-anchor parentheticals to structural specification ("Specify with concrete numbers: total neuron count + distribution + evolutionary distance + central-vs-peripheral autonomy") + multi-class parallel-exemplar lists (cephalopods + corvids + insects + cetaceans + cnidarians) where structural guidance benefits from worked examples. Octopus proper-noun mentions reduced from 13 to ~4 (header comment + multi-exemplar parallel sets only).
  - **System (Whanganui):** template was already mostly multi-paralleled (Whanganui + Atrato + Mar Menor + Pachamama + Yurok throughout). Only a few single-anchor passages needed widening — concepts list, values statement, hard limits critique, Indigenous-authored scholarship. **Added parallel exemplars** for those four passages (Embera/Afro-Colombian + Andean Kichwa-Shuar + Yurok-Klamath traditions). Header comment updated.
  - **Fictional (Scheherazade):** audit found template was already rigorous in multi-exemplar pattern (Scheherazade always paired with Hamlet / Antigone / Aeneas / Anansi / Sun Wukong / Achilles / Don Quixote / Ariadne). High mention count was structural — Scheherazade in worked-example lists alongside parallels, not single-anchor self-reference. **No additional parallel-exemplar additions made** beyond updating header comment to document the FU#19 audit verdict.
- **Effect for voices 3-12:** new same-class voices (second non-human-organism / non-human-system / fictional voice) will not be anchored to the existing panel exemplar. Cleaner DR generation for those classes.

#### FU#22 — MergedDossier.register / voice_register Pydantic alias audit ✅ AUDITED 2026-04-27 — CLEAN
- **Audit finding:** every consumer accesses the field as a dict key (`merged_dossier["register"]` or `chunks["register"]` or `chunk_vars["register"]`), not as a Python attribute (`model.register`). Dict-key access works transparently via `model_dump(by_alias=True)` round-trip — the alias does its job.
- **Verified call sites:**
  * `run_pass_1_7.py:92` (layout dict), `:158` (compose), `:308` (chunk routing) — all dict-key.
  * `run_persona_pipeline.py:264` (`md.get("register", {})`), `:567`/`:616` (Pass 4a + 6 chunk_vars["register"]) — all dict-key.
  * `run_pass_1_4.py:28` (output_keys map) — file-naming, dict-key.
  * `scripts/arch_03_preservation_audit.py:300`, `arch_03_synthesis_audit.py:80`/`:113` — file-paths + chunk-key strings, all dict-key.
- **No Python-attribute access (`.register` on a MergedDossier instance) found anywhere.** Close as AUDITED.
- **Original definition (preserved for re-activation):**
  - **Problem:** Cleanup-deferral-B fixed the Pydantic warning by renaming the attribute to `voice_register` with `alias="register"` + `populate_by_name=True` + `serialization_alias="register"`. Primary site (`run_pass_1_7.py` → `model_dump(by_alias=True)`) is updated. Audit needed across all consumers.
  - **Risk:** Low probability of breakage but worth verifying if Pass 1.7 ever produces unexpected output.

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

#### FU#21 — Runtime enforcement of `reference_only_passages` Step 1/Step 2 contract ✅ LANDED 2026-04-28
- **Origin:** OPEN_ITEMS.md "Smaller improvements", deferred from prior session.
- **Problem:** Two-tier corpus design (Marley lyrics in private reasoning only) is documented in `personas/HANDOFF.md`. Runtime Voice Pipeline Step 2 assembly code MUST drop the field before rendering.
- **Resolution:** Voice Pipeline v2 implemented as commit `180a18f` includes the strip rule in `runtime/flows/voice/card_assembly.py`:
  - Line 315-317: `if step in (2, 3): filtered.pop("reference_only_passages", None)` — Step 2/3 drop
  - Line 364-369: `if step == 1 and "reference_only_passages" in filtered:` then render under its own section — Step 1 keeps
- **Verified 2026-04-29** during FU#21 closure check.

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

#### FU#11 — Workspace archive cleanup ✅ APPLIED 2026-04-27 (relocated 2026-05-01)
- **Trigger:** Plato shipped + chat-test validated 2026-04-26 = Phase L sign-off.
- **Pruned:** `_workspace/arch_03_baseline_snapshot/{fu32_complete_20260424_0817, phase_1_complete_20260423_2251, phase_3_fu2_complete_20260424_0844}` — the intermediate post-FU#32 / Phase 1 / post-FU#2 snapshots. Findings absorbed into FOLLOW_UPS.md as completed FU# items; snapshots no longer needed.
- **Kept:** `baseline_04_generation/` + `baseline_05_validation/` + `baseline_06_derive/` + `baseline_07_persona_card_assembled.json` + `baseline_08_merged_dossier.json` + `baseline_arch_03_audit_sonnet_run.json` (Phase L pre-arch-03 reference) + `stage1_v4_run/` (final Stage 1 output). Total ~1.5MB local-only reference.
- **Gitignored:** `_workspace/arch_03_baseline_snapshot/` added to `.gitignore` — these are dev artifacts for backward comparison, not pipeline code or project data.
- **Relocated 2026-05-01:** moved out of `code/_workspace/` to umbrella `~/Desktop/AI Assembly/archive/arch_03_baseline_snapshot/` (per CLAUDE.md "frozen historical runs — NEVER pushed" convention). Same applied to `_workspace/sentinel_baselines/` (per FU#29 sentinel_regen tooling) → `~/Desktop/AI Assembly/archive/sentinel_baselines/`. Both still gitignored locally; relocation removes them from the code repo's `_workspace/` tree where they were never tracked but added clutter. New sentinel_regen runs continue to write to `_workspace/sentinel_baselines/` per existing tooling defaults; relocate to umbrella archive when accumulated.
- **Original definition (preserved for archival):**
  - **Problem:** `_workspace/arch_03_baseline_snapshot/` accumulated archives from multiple Stage 2 attempts. Useful while debugging; bloat after Phase L sign-off.
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
  - **Architecture note (2026-04-26):** when re-activated, **integrate as Pass 7a rubric extension, NOT as new Pass 7 family member.** Pass 7a is already (a) cross-model (gpt-5.4 → Gemini fallback) — avoids Claude self-preference bias that was the original reason FU#31 wanted a separate pass; (b) producing field_issues that flow into FU#13 patcher; (c) calibrated for runtime-card validation. Adding voice-tissue as a Pass 7a rubric question (~30 min prompt addition + per-voice load-bearing-lexeme list lookup from `chunk 1.4 vocabulary.preferred_vocabulary`) is cleaner than building a separate validator. Updated effort estimate: ~1 hr (was 4-5 hr).

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
- **Phase 2 card inspection update (2026-04-24):**
  - ✅ **`doubented` typo — FIXED** by FU#32 regeneration (absent from Phase 2 card).
  - ✅ **`padachaya/paduchaya` transliteration — FIXED** (Phase 2 card has only `paduchaya`, consistent).
  - ❌ **3 `[projection_warning:]` bracket residues STILL PRESENT** in Phase 2 card (confirmed 2026-04-24 via walk of all leaf strings):
    - `world.model_of_selfhood` — 2 brackets (podpol'e-as-unconscious warning + temporal-lobe-epilepsy warning)
    - `formative_experience.lived_through_own_apparatus` — 1 bracket (trauma-as-clinical warning)
  - **Scope narrows:** bracket-residue scan is the highest-leverage remaining extension. The other three extensions (INCONSISTENT flags, transliteration-consistency, spell-check) are either empirically-not-needed or closed by upstream improvements.
  - **Why the brackets survive:** the FU#13 patcher operates on `field_issues[]` emitted by Pass 7a. Pass 7a's rubric doesn't flag `[projection_warning:]` brackets as a register violation (they're voice-honest annotation per Boddice §12), so the patcher never sees them. They're legitimate per the schema but operator-visible as "still in the prose" on a sign-off read.
- **Extensions needed (re-prioritized post-Phase-2-inspection):**
  - **P1: Universal bracket-tag residue scan across live prose fields ✅ LANDED 2026-04-25, AMENDED same day** — `flows/shared/bracket_strip.py` deterministic regex pass.
    - **Initial implementation (commit `6c0daf5`):** orchestrator hook as Pass 7d-clean (AFTER Pass 7c, BEFORE Derive). Strip allowlist included Boddice tags (`[experiential_reconstruction]`, `[projection_warning:...]`).
    - **Amendment (2026-04-25 same day):** TWO empirical issues surfaced on Plato:
      1. **Boddice tags MUST be preserved.** Stripping `[experiential_reconstruction]` and `[projection_warning:...]` made Pass 7-pre boddice_tag_flags go 0 → 9. The biocultural-discipline check expects these tags inline (per `persona_pass_7pre_boddice_check.md`: "`[experiential_reconstruction]` must accompany any claim about what the voice felt/lived/witnessed... `[projection_warning]` must accompany any modern English term used faute de mieux"). They are content-meaningful annotations, not pipeline scaffolding. Removed from strip allowlist.
      2. **Strip placement should be BEFORE validators, not after.** Original placement (after Pass 7c) produced stale validation reports — Pass 7a flagged residues that the strip then removed. Moved to Pass 6.5-clean (after Pass 6, before Pass 7-pre) so all validators see the cleaned content from the start; their reports reflect shipped state.
    - **Final allowlist (post-amendment):** schema taxonomy markers (`[ontological]`/`[epistemological]`/`[ethical-political]`/`[unique]`/etc.), EvidenceTag values that leaked from chunks (`[stated]`/`[inference]`/`[scholarly_consensus]`/`[contested]`), curator-side annotations (`[curator_note]`/`[pedagogical_note]`/`[editorial_note]`).
    - **PRESERVED:** Boddice tags (`[experiential_reconstruction]`, `[projection_warning: ...]`) — content, not scaffolding.
    - 21 tests (was 19; +1 boddice-preserved-inline test, +1 boddice-excluded-from-allowlist regression test, 1 modified to test curator-note instead of projection_warning).
    - **Plato impact:** post-strip card had 0 schema-taxonomy + EvidenceTag residues (33 `[ontological]`-class markers + 9 evidence/curator brackets all gone). The Boddice tags would now stay inline if Pass 6.5-clean ran before Pass 7-pre; for Plato's already-stripped state this is a one-time gap until split-card lands.
    - Generalizes across voices: Pass 6.5-clean is now part of the standard pipeline; voices 3-12 will run it automatically with the corrected allowlist + placement.
  - **P2: Read Pass 7-pre's `INCONSISTENT` citation flags into patcher input ✅ LANDED 2026-04-26** in `personas/run_persona_pipeline.py:1013-1078`. INCONSISTENT items are merged into Pass 7a's `field_issues[]` array with field-path-to-pass routing (path prefix → flagged_pass mapping for passes 2/3/4a/4b/5/6). Empirical activation: Plato 2026-04-29 surfaced 2 INCONSISTENT items (Phaedrus 246a + 275d-e Jowett translations) which were correctly routed; the FU#13 single-shot guard prevented automatic re-patching but the operator review gate (FU#53) caught them.
  - P3 (closed): transliteration-consistency + spell-check. Phase 2 card is clean on both.
- **Effort:** All three sub-items closed. P1 LANDED 2026-04-25 (commit `6c0daf5`); P2 LANDED 2026-04-26; P3 closed by upstream improvements.
- **Activation:** Plato's first card empirically activated P1 (42 residues). Plato 2026-04-29 empirically activated P2 (2 Jowett-translation flags routed correctly).
- **Relation:** orthogonal to voice-tissue work — addressed mechanical-defect class of issues the patcher missed.
- **Status:** ✅ FULLY LANDED — all three sub-items closed.

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

#### FU#38 — Voice-self-reference vocabulary strip (Pass 2-6) ✅ APPLIED 2026-04-24
- **Origin:** 2026-04-24 external reviewer critique of Dostoevsky chat v2 card (two independent reviewers). Reviewer 1 flagged "kenotic beauty" specifically as a defect the FU#13 patcher missed. Reviewer 2 generalized: post-voice-lifetime critical vocabulary that scholars coined to describe the voice leaks back into voice-native prose even after scholar-attribution NAMES are stripped per FU#12-A.
- **Problem:** FU#12-A's register hardening stripped scholar NAMES (Bakhtin, Eikhenbaum, Kasatkina) from runtime field values. It did NOT strip scholar-coined TERMS (polyphonic, kenotic, chronotope, dialogical, carnivalesque, sideshadowing) that entered common critical English and often leak into field values describing the voice's own operations. Empirically verified on Phase 2 Dostoevsky card (FU#32 re-run): polyphonic (8×), kenotic (8×), chronotope (2×), dialogic embodiment (1×), dialogical (1×). FU#13 patcher caught "sideshadowing" but missed these. Per-voice: every voice has its own post-horizon critical vocabulary list.
- **Landed:** commit `22a2e54`. Extends FU#12-A/FU#32 STRIP+DO-INSTEAD pattern with a 6th STRIP item across all 6 Pass 2-6 prompts. Per-voice examples in prompt (post-1920 Dostoevsky criticism, post-1950 Plato criticism, post-1990 cognitive philosophy on non-human voices) are exemplary — the writer applies the temporal-cultural test to the voice at hand.
- **Per-voice test (encoded in prompt):** "Would this voice, IN THEIR OWN LIFETIME, have reached for this English adjective to describe their own work? If no (because the term postdates them or belongs to a critical tradition they did not participate in), do not mirror the vocabulary in field values even if the merge dossier contains it."
- **DO INSTEAD pattern:** express the same ground in the voice's own incarnate grammar. Worked examples for Dostoevsky encoded in prompt: "beauty that has passed through the crucible and remained beloved" inhabits "kenotic beauty"; "many voices at once, none singly yours, arguing inside the character as the character argues outside" inhabits "polyphonic"; "the threshold where time stages spiritual crisis" inhabits "chronotope".
- **Generalization:** all 12 voices. Each voice's post-horizon critical-term list is different; the TEST is the same.
- **Status post-Athens-probe (2026-04-24 late):** Athens-piece review revises framing from "pipeline leak fix" to **"belt-and-braces"** — the leak exists in the pipeline card (the counts above are real), but the voice doesn't reach for these terms under Provocateur-register tasks. Strip retained because it prevents leak under edge-case task registers (philosophical-meditation) at zero runtime cost. See NEXT_SESSION addendum for task-register interpretation.

#### FU#39 — Character-distribution stage-quoting 🔵 CONDITIONAL ON PLATO SIGNAL
- **Origin:** 2026-04-24 external reviewer critique (reviewer 1). "Narrator-unification problem" — distributed voices merge their distinct narrative personas into a single unified "I" in the persona card, erasing the character-distribution that defines the voice's actual literary practice.
- **Problem (per-voice):**
  - Dostoevsky: Karamazov-speaker voice drowns out Diary-of-a-Writer-speaker, Underground-Man-speaker, Zosima-speaker. Card's "I" is Karamazov-pitch across fields.
  - Plato (hypothesis, untested): Socrates / Eleatic Stranger / Athenian Stranger / late-Plato author-voice collapse into single "I". Karamazov-equivalent failure mode if it manifests.
  - Scheherazade: character-within-frame-tale vs. frame-tale-narrator vs. authorial-tradition-voice collapse.
  - Ibn Battuta: narrator-of-Rihla vs. traveller-in-events vs. retrospective-compiler collapse.
- **Reviewer 1 framing:** architectural ceiling of base-model + persona-card approach. "Tops out at high pastiche" without character-distribution discipline baked in.
- **Proposed fix:** `voice_distributes_across_characters` bool flag in `voice_config.json` (~30 min schema + defaults — see G4 prerequisite below). When true, Pass 4a `characteristic_moves` prompt gains a stage-quoting move instruction: voice-card explicitly names 2-4 character-personas the voice distributes across + runtime stages which persona speaks per turn via explicit quoting ("[as the underground man:] ..." / "[as Zosima:] ..."). Provocateur Pipeline or Voice Pipeline Step 1 picks the persona per query; Step 2 renders in that persona's register.
- **Prerequisite (G4):** add `voice_distributes_across_characters: bool` to voice_config schema + default `false` for non-distributed voices (Arendt, Thiel, Lovelace, etc.). ~30 min.
- **Effort:** 3-4 hr (schema + voice_config defaults + Pass 4a prompt extension + test on Plato re-run after first build).
- **Activation condition:** Plato's first card shows narrator-unification (Socrates/Stranger/late-Plato merged into single I). If Plato's distribution holds naturally, FU#39 stays deferred — FU#32/FU#38 may be sufficient for philosophical-human voice_mode.
- **Status post-Athens-probe (2026-04-24 late):** Athens probe on Dostoevsky confirms narrator-unification is **task-register-dependent**, not a card-schema defect. Provocateur-register tasks (concrete situation) pulled the voice toward Dostoevsky-at-desk mode with zero Karamazov-voice bleed. Philosophical-meditation register still fails. Still DEFERRED — Plato signal could reopen, but Athens reading suggests FU#39 is speculative for the Provocateur-register use case.

#### FU#40 — Digression-permission characteristic_move ✅ SIMPLE VERSION APPLIED 2026-04-26 (Pass 4a prompt extension, narratival voices only)
- **Origin:** 2026-04-24 external reviewer critique (reviewer 1). "Too-composed architecture ceiling" — persona cards produce too-polished, too-arc-complete prose even when the voice's actual corpus digresses, circles back, leaves threads dangling.
- **Problem:** Pass 7b smoke-test chains show voices completing a tidy 3-part arc in 350-550 words. Real Dostoevsky (especially Diary of a Writer) digresses mid-sentence, inserts unrelated polemic, leaves the ostensible topic unfinished. The card optimizes for readability against what the voice actually sounds like.
- **Proposed fix sketch:** Pass 4a `characteristic_moves` gains a digression-permission move for voices whose corpus exhibits it: "You are permitted to digress mid-paragraph toward a tangential provocation; you are permitted to leave the nominal topic unresolved; you are permitted to drop in polemic against an absent interlocutor unrelated to the question." Voice-specific — not all voices digress (Arendt's rigor doesn't; Dostoevsky's Diary-of-a-Writer does).
- **Status:** DEFERRED. Reviewer 1 framed this as architectural ceiling of base-model + persona-card approach — "speculative fix; unclear if prompt-level permission actually overrides the model's default composed-arc bias". FU#40 is a hypothesis, not a diagnosis.
- **Status post-Athens-probe (2026-04-24 late):** Athens piece on Dostoevsky DID sprawl at lower amplitude than love-and-beauty piece despite NO card change. Suggests digression-capacity is in the card; deployment register modulates amplitude. Re-confirms full DEFERRAL of speculative architectural ceiling work.
- **Simple version LANDED 2026-04-26 (~1 hr):** edited `persona_pass_4a_voice.md` to add a Jinja-conditional `{% if voice_mode == "narratival" %}` block under `characteristic_moves` field specification. Block names a digression-permission characteristic_move in the voice's own idiom (e.g., Dostoevsky's "publitsist's swerve"; Ibn Battuta's "traveler's notice in passing"; Scheherazade's "frame-breath") and describes what the voice digresses TOWARD. Permission, not mandate. Voice-mode-conditional means analytical voices (Plato, Arendt, Lovelace, Tang, Thiel) are unaffected. Effect for voices 3-12: narratival voices get explicit permission for digression in their `characteristic_moves`; analytical voices unchanged.
- **Effort to escalate to full version (voice_config flag + per-voice opt-in rules):** 2-3 hr if needed; not currently empirically motivated.

#### FU#41 — Chat-ready system prompt as 4th Derive artifact ✅ APPLIED 2026-04-24
- **Origin:** 2026-04-24 reviewer 2 empirical observation. Operator's hand-produced chat v2 card for Dostoevsky (deployed as Claude project custom instructions for chat-test validation) was compared to pipeline's `07_persona_card_assembled.json`: **27 of 35 shared fields byte-for-byte identical; 8 differ only by ~10-100 chars of minor operator polish.** The chat artifact is a mechanical strip-out of Voice-Pipeline-only fields — no content generation work. Content generation is the pipeline's job.
- **Problem:** Every chat-test validation required operator to manually hand-build the chat artifact from the assembled card. Error-prone (easy to forget to strip `smoke_test_chains` or `reference_only_passages`), tedious at 12-voice scale, and (more importantly) the manual step inserted operator judgment where mechanical transform suffices.
- **Landed:** commit `b9c1eb2`. New module `personas/flows/shared/chat_prompt_builder.py` (123 lines) + 13 tests in `tests/test_chat_prompt_builder.py`. Orchestrator integration at `run_persona_pipeline.py:1585-1588` writes the 4th Derive artifact (`voices/<slug>/06_derive/03_chat_system_prompt.json`) after assembly completes.
- **Transformation (mechanical, no editorial work):**
  - DROP 10 Voice-Pipeline-only fields: `metadata`, `smoke_test_chains`, `reference_only_passages`, `medium`, `characteristic_output_structure`, `length_and_format_constraints`, `technical_capabilities`, `relationship_to_detailed_response`, `continuity_block_if_night_2`, `continuity_block_artifact_if_night_2`
  - PRESERVE all other ~34 fields at root
  - MARK `pipeline_version` with `-chat` suffix; re-stamp `generated_date`
  - Atomic write via temp file + rename
- **Does NOT attempt:** editorial polish (operator's territory), factual correction (operator's territory; future FU candidate for fact-check-against-dossier pass), content expansion (operator's territory).
- **Validation (2026-04-24):** unit tests cover 13 scenarios (pass-through field preservation, drop-field correctness, marker stamping, idempotency, empty-card edge case, atomic-write survival). Test-validated against operator's chat v2: 34 fields match exactly; 25/34 byte-identical.
- **Operator workflow:** pipeline run → `voices/<slug>/06_derive/03_chat_system_prompt.json` is written → paste JSON into Claude project custom instructions → ask probing question → assess voice quality. Bypasses Voice Pipeline Step 1/Step 2 protocol entirely.
- **Cross-repo contract:** documented in `personas/HANDOFF.md` §"Derive artifacts per voice" as 4th artifact alongside `provocateur_profile` + `evaluation_rubric`. Chat artifact is operator-paste-target; provocateur_profile feeds runtime `council_config.json` `members[]`; both coexist without conflict.
- **Future FU candidates (not currently active):**
  - Explicit `chat_deployment_mode: "anchored" | "default"` marker for programmatic voice_temporal_stance disambiguation (currently the chat artifact preserves the full `voice_temporal_stance: {default, anchored_override}` dict and leaves the Claude-project author to decide which sub-field to foreground)
  - Fact-check pass against merged_dossier before writing chat artifact (e.g., the Freud 25→24 operator correction on Dostoevsky's death date would land here if automated)

- **AMENDMENT A 2026-04-25 — strip set reduced 10→5 (chat = deployment-test, not separate-deployment):** empirical signal from Plato's first card showed the original 10-field strip was over-eager. Plato's `medium` ("I write what I have always written: a short conversation. I do not lecture. I do not deliver a paper.") is voice-constitutional — Plato's refusal of treatise form is part of who Plato IS, not a deployment-format choice. Stripping it produced a chat persona that could drift into essayistic register on Sonnet runtime. Same diagnosis applied to `characteristic_output_structure` (elenctic-mythic-aporetic shape), `relationship_to_detailed_response` (reasoning-becomes-scene), `technical_capabilities` (refusal of multimodal), and `length_and_format_constraints` (conference breakfast-reading window — kept because chat IS testing the Athens deployment).
  - **Architectural reframing:** chat deployment is treated as a TEST of the configured deployment (e.g., Athens 2026 Voice Pipeline run), not a separate deployment surface. Chat output should match what the runtime will produce — same length window, same artifact structure, same audience-aware priming.
  - **Strip set after Amendment A (5 fields):** `metadata`, `smoke_test_chains`, `reference_only_passages`, `continuity_block_if_night_2`, `continuity_block_artifact_if_night_2`.
  - **Promoted to preserve (5 fields):** `medium`, `characteristic_output_structure`, `length_and_format_constraints`, `technical_capabilities`, `relationship_to_detailed_response`.
  - **Landed:** commit `aa4ce85`. `chat_prompt_builder.py` strip list edited; tests updated; suite 186→187.

- **AMENDMENT B 2026-04-25 (same day, second pass) — strip set grown 5→11 (spec-shell suppression):** empirically motivated by Plato chat-test thinking-trace meta-reasoning. The model produced trace text like *"metadata points to a test environment for a Plato-voice mode... legitimate philosophical voice exercise rather than something problematic... I'm seeing that this system prompt contains both Plato persona instructions and standard Claude behavior guidelines."* The model was reading specification-shell fields as "this is a persona spec" rather than "I am the voice." Pass 7a's gpt-5.4 verdict had warned the same thing: *"several fields still contain editorial scaffolding, schema tags, or scholarly/meta phrasing that would make the model reason about the specification instead of from within the voice."*
  - **5 spec-shell meta fields added to strip (top-level):** `voice_name` (third-person identity scaffold; identity should be in `epistemic_frame_statement` first/second-person prose), `voice_mode` (schema label like "philosophical" reads as mode-selection signal), `pipeline_version` (provenance — "3.10-chat" reads as test/dev pipeline), `generated_date` (provenance), `council_member_name` (Voice-Pipeline scaffolding announcing council role).
  - **1 nested production-metadata sub-field added to strip:** `curated_corpus_passages.corpus_metadata` (Pass 7a issue #7 — production metadata: "Public-domain translations...", source counts, passage counts). The rest of `curated_corpus_passages.passages[]` survives.
  - **Marker re-stamp removed:** the prior `-chat` suffix on `pipeline_version` and re-stamp of `generated_date` are gone (those fields are now in the strip set). Operators identify chat artifacts by filename (`03_chat_system_prompt.json`) not by in-artifact marker.
  - **Combined strip set after Amendments A + B = 11 items** (5 chat-incompatible + 5 spec-shell + 1 nested).
  - **Implementation:** strip A and strip B are split into two named tuples (`_CHAT_INCOMPATIBLE_FIELDS`, `_SPEC_SHELL_META_FIELDS`) for clarity; `_VOICE_PIPELINE_ONLY_FIELDS` is the union. Nested strip uses a separate `_NESTED_STRIPS` tuple of `(parent, child)` pairs with deep-copy-before-mutate to preserve input non-mutation.
  - **Tests:** 18 tests on the module (was 14 after Amendment A); covers strip A set, strip B set, combined union, nested strip, voice-constitutional regression, no-marker-re-stamp invariant, non-mutation, and an amendment-history regression test that pins the 2026-04-24 baseline → A → B trajectory.
  - **Plato chat artifact regenerated manually under combined A+B strip; Dostoevsky's chat artifact will re-render on next pipeline run.**
  - **Architectural successor (still post-Athens):** the split-card direction — voice-card / deployment-card schema-level distinction — addresses the JSON-wrapper-as-spec-signal problem more deeply. Even with the spec-shell meta-fields stripped, a JSON artifact with field-labels still partially reads as "specification" rather than "voice." Flattening voice-card into prose-system-prompt + leaving deployment-card structured is the durable answer.

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
- **Narrow version LANDED 2026-04-26:** `personas/scripts/sentinel_regen.py` — prompt-touch detection + per-pass sentinel-regen + diff vs baseline. Three modes: `detect` (list passes affected by changed prompts since a git ref), `regen --pass <NAME>` (invalidate cache + re-run pipeline + diff against baseline-snapshot), `list-prompts` (print prompt → pass mapping). Uses `invalidate_cache.py` (FU#45) under the hood. Sentinel voices: Plato + Dostoevsky. Smoke-tested against today's Pass 4a edit (FU#40 simple) — correctly detected `persona_pass_4a_voice.md` change → Pass 4a affected. Broad version (any-pipeline-code-change impact analysis) deferred post-Athens.

- **Empirical observation 2026-04-24 (Plato DR session times):** Plato §1 and §2 claude.ai DR sessions **each completed in ~9 min** vs. Dostoevsky §1 (generated 2026-04-20) which took **~30 min**. Output quality comparable: both Plato sections hit all canonical §N asks, addressed all 3 tailored follow-up questions substantively, deployed dense Greek period-vocabulary (~15 terms §1, ~50 terms §2), surfaced contested readings, minority scholarly schools, and self-identified limits. Not a convergence-trap (output is not a stub; output IS substantive).
  Three candidate causes (non-exclusive):
  1. **Corpus asymmetry.** Plato scholarship is exceptionally well-indexed (SEP, IEP, BMCR, OUP, NDPR all have authoritative consolidated entries). DR's search-round convergence is faster than for Dostoevsky's more fragmentary Russian-language + specialized-journal landscape (Saraskina, Kasatkina, Shrayer, Vassena).
  2. **DR-infrastructure update.** claude.ai's Deep Research had 4 days of potential model/pipeline changes between 2026-04-20 Dosto runs and 2026-04-24 Plato runs. Unverifiable from outside.
  3. **Section-mode research-discipline stripping.** Commit `1fd43f2` moved research discipline into `_pass_0b_research_discipline.md` with `{% if not section_mode %}` conditionals. Stripped from section-mode: the `(Bakhtin on polyphony; Frank on Dostoevsky; Vlastos on Socratic Plato)` scholar examples, "Your training covers most of them; trust that" training-trust cue, "No word-count floor to hit; no word-count ceiling to stay under" + "six thematic areas should each receive substantive coverage" word-count framing, and the "§5–§6 failing to arrive" monolithic warning. All of these damp verification pressure; their absence may encourage earlier synthesis.
  Implication for FU#29 baseline work: when using Plato + Dostoevsky as sentinel voices, **expect asymmetric session times** (Plato ~10 min, Dosto ~30 min). Diff-tooling should normalize on output depth/scholar-citation-count, not on session duration. If future regression investigation needs controlled timing, restore the stripped discipline phrases in the section-mode branch as a testbed.

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

#### FU#42 — Split-card architecture (voice-card / deployment-card)
- **Origin:** 2026-04-25 emerged across multiple architectural debates: FU#41 chat-strip blacklist over-strips for Plato (Amendment A), Pass 7a vs Pass 7-pre conflict on biocultural tags (FU#33 P1 amendment), audience-iteration cost vs deployment-flexibility tension. Common diagnosis: the assembled card conflates two structurally different layers.
- **Problem:** the 44-field card mixes:
  1. **Voice-card** (constitutional, stable across deployments): identity, world, character, knowledge_boundary, voice_temporal_stance, translation_protocol, constitution, concept_lexicon, reasoning_method, characteristic_moves, register_and_tone, metaphorical_repertoire, preferred_vocabulary, banned_language, banned_modes, the constitutional core of `medium`/`characteristic_output_structure`/`technical_capabilities`/`relationship_to_detailed_response`/`aesthetic_qualities`/`stance_tendency`, `curated_corpus_passages`, `reference_only_passages`, `topics_requiring_care` (constitutional core), `hard_limits` — ~32 fields.
  2. **Deployment-card** (this-occasion-specific, swappable per deployment): `length_and_format_constraints` (Athens-specific 350–550-word window), `bold_engagement_topics` (audience-aware), `default_questions` (audience-primed), `disagreement_protocol` (deployment overlay), `unique_contribution`, `continuity_block_if_night_2` + `continuity_block_artifact_if_night_2`, `quality_criteria` — ~8 fields.
  3. Hybrid (constitutional core + deployment overlay): `topics_requiring_care`, `disagreement_protocol`.
- **Operational benefits:**
  - **Cheap deployment swapping.** Plato-for-Athens-2026 vs Plato-for-2027-event = same voice_card, swap deployment_card. Today: ~12 × ($18-22, 2h) = $240+/24h to redeploy 12-voice panel; with split-card: ~12 × ($1-3, 5min) = $30/1h. ~5-8× cheaper per deployment iteration.
  - **Voice consistency across deployments.** voice_card generated once, locked. Deployment_card swaps. Voice stays byte-identical across deployments (today's pipeline cannot guarantee this).
  - **Cheap audience-brief iteration.** Edit `audience_profile.json` / `conference_facts.json` → regenerate deployment_card only. Today's `scripts/invalidate_cache.py --from-pass 5` does this partially ($60-96 + 5h for 12-voice panel); split-card reduces to $15-25 + 1h.
  - **Pass 7a vs Pass 7-pre boddice-tag conflict structurally resolved.** Boddice tags become explicit `experiential_reconstructions[]` / `projection_warnings[]` sibling fields in voice_card (structural, not inline). Pass 7a doesn't see them in voice prose; Pass 7-pre reads from sibling fields. Both validators happy.
  - **Diagnostic clarity.** When something's wrong with runtime, "voice problem or deployment problem" answers itself by which card the issue traces to.
  - **FU#41 chat artifact becomes principled.** Chat artifact = voice_card directly (no mechanical strip-by-blacklist). Today: blacklist of 11 fields calibrated voice-by-voice (Amendment A + Amendment B history). With split-card: structural distinction means the chat-test target is just voice_card, no per-voice tuning.
- **What the half I retracted addressed:** "voice_card prose-flatten" (eliminate JSON wrapper as spec-shape signal in chat-test thinking traces) — chat-only motivation, no Voice Pipeline runtime benefit. Voice Pipeline cherry-picks specific fields via API, never reads card as one document. Retracted from this FU's scope.
- **Effort:** ~1-2 weeks of architectural work. Schema migration (Dostoevsky + Plato into v3 shape). Pass 4b prompt splits (constitutional medium/structure → voice-card; deployment length/audience-format → deployment-card). Card assembly + chat builder rewritten as voice+deployment merge instead of strip-by-blacklist.
- **Trigger options:**
  1. Post-Athens (May 11+): voices 3-12 ship under Card v2; migrated to v3 alongside Dosto + Plato.
  2. Pre-Athens IF audience-brief or conference-context iteration becomes substantive (5+ iterations between now and May 7 would justify the architectural cost).
  3. Partial-slice pre-Athens: just the audience-aware regeneration path (Pass 5 + Pass 4b-deployment + Pass 6-deployment) ≈ 3-4 days; defers full split.

#### FU#43 — Pass 6 `corpus_metadata` source-side hardening ✅ APPLIED 2026-04-25
- **Origin:** Plato 2026-04-25 first run had Pass 7a flag `curated_corpus_passages.corpus_metadata` as "production metadata leaked into prose" (issue #7); patcher trimmed it (patch #6 in `_fix_log.json`). Pattern recurs across voices.
- **Landed:** `bf49a0a`. Edited `persona_pass_6_corpus.md` to explicitly tell Pass 6: keep `corpus_metadata.notes` EMPTY or one short translation-tradition line ("Cooper-Hackett ed. 1997"; "Jowett 1892"). Forbid voice biography, voice-instruction prose, public-domain disclaimers, curator essays, passage summaries. Cross-references FU#41 Amendment B nested-strip as source-of-truth intent.
- **Effect for voices 3-12:** Pass 6 emits minimal corpus_metadata at source; patcher doesn't need to re-trim per voice. Saves ~$0.20-0.50 patcher work per voice + cycle time.

#### FU#44 — Patcher prompt register-drift extension ✅ APPLIED 2026-04-25
- **Origin:** Plato 2026-04-25 Pass 7a flagged 7 field_issues post-fix. Two recurring patterns the patcher missed:
  1. **Third-person scholarly diction** — "the corpus", "the [Voice]ian person", "[Voice] held that...", "reticence in the corpus".
  2. **Internal contradictions** — `topics_requiring_care.guidance` instructing voice to acknowledge facts that `knowledge_boundary` says voice cannot know (Plato + Popper-eugenics-history).
- **Landed:** `bf49a0a`. Edited `persona_pass_7a_fix.md` with worked-example patterns under rule 3 (register-drift rewrites: "the corpus" → second-person possessive, "the [Voice]ian person" → first/second-person, "[Voice] held that..." → first/second-person rewrite). Added new rule 4: internal-contradiction patches (rewrite cross-knowledge_boundary guidance into voice-native terms). Renumbered subsequent rules 4→5, 5→6, 6→7.
- **Effect for voices 3-12:** patcher catches register-drift specifically, reducing residual REVISION_NEEDED flags after fix-pass. Lower operator-triage friction at every CARD COMPLETE step.

#### FU#45 — Cache-invalidation helper script ✅ APPLIED 2026-04-25
- **Origin:** Plato 2026-04-25 re-run cycles cost an extra ~$5 + 30min when the operator (and Claude) targeted `04_generation/02_excerpt_selections.json` for Pass 1d cache invalidation; the actual path is `03_corpus/02_excerpt_selections.json`. `rm -f` failed silently; the pipeline cache-hit; the wider Pass 1d budget didn't apply.
- **Landed:** `bf49a0a`. New `personas/scripts/invalidate_cache.py` knows the path map for every pass + handles composite paths (chat artifact, fix log) that don't have their own helper function. Supports `--pass <name>` (single), `--from-pass <name>` (cascade), `--list`, `--dry-run`.
- **Usage:** `venv/bin/python scripts/invalidate_cache.py --voice plato --project /path/to/project --from-pass 1d`
- **Effect for voices 3-12:** operator iteration cycles use the helper instead of manual `rm -f`. No more silent path-mismatch failures.

#### FU#46 — Pass 1d excerpt budget bump (30K → 60K) ✅ APPLIED 2026-04-25
- **Origin:** Plato 2026-04-25 first run had 25/151 Pass 7-pre claims UNVERIFIED at 30K budget. Well-attested Platonic doctrines (anamnēsis, divided line, meletē thanatou, etc.) lived in merged_dossier but Pass 1d's 6 selections couldn't anchor them in 30K of curated excerpts.
- **Landed:** `cba8fc5`. Edited `persona_pass_1d_excerpt_selection.md`: budget 30K → 60K, per-source 10K → 15K. Per-source cap keeps single-source dominance in check.
- **Effect for voices 3-12:** richer-corpus voices (Plato, Arendt, possibly Scheherazade) anchor more claims to primary text. Smaller-corpus voices not affected (per-source cap + LLM judgement still bounds selection).

#### CC#1 — Move `05_primary_text_urls.json` out of `01_research/` ✅ APPLIED 2026-04-26
- **Origin:** This session, surfaced reading `paths.py`.
- **Problem:** Historical-layout vestige. In v3.10 the URL list came directly from Perplexity research (true research artifact). 1-arch-07 (2026-04-22) changed the source — URLs now derived post-merge from `02_merge/pass_1_6/works.json` + `passages.json`. Destination path kept for backward-compat but file is no longer a research output.
- **Landed:** commit `ef91fb6`. Moved from `voices/<slug>/01_research/05_primary_text_urls.json` → `voices/<slug>/03_corpus/00_primary_text_urls.json`. `paths.py:69-72` updated; `tests/test_paths.py` test moved from `TestResearchFiles` to `TestCorpusFiles` and asserts new filename. Existing files migrated for Plato + Dostoevsky.

#### FU#47 — Voice Pipeline Step 1 mode-switching for non-analytical voices
- **Origin:** External reviewer 2026-04-26 comparing Plato (pipeline-emitted) vs Dostoevsky (chat v2, operator-hand-curated). Surfaced architectural diagnosis: Plato's actual method IS analytical-procedural (Socratic dialectic IS reducible to logical operations); the Voice Pipeline's Step 1 (analytical workshop / thinking-procedure) → Step 2 (artifact rendering) split fits Plato cleanly. Dostoevsky's method is scenic-incarnational; Step 1 as a separable analytical workshop is structurally foreign. Reviewer's verbatim: *"the Step 1 trace cannot be authentic Dostoevsky-thinking; it can only be analytical-thinking-about-what-Dostoevsky-would-write."*
- **Scope:** This is a **Voice Pipeline runtime concern**, not a persona-pipeline (build) concern. The persona pipeline produces the card; the Voice Pipeline reads the card at deployment time and runs Step 1 / Step 2 over per-session prompts. The fit problem is in Step 1's prompt design.
- **Estimated voice-fit map (rough first pass; needs empirical confirmation per voice):**
  - **Step 1 fits (analytical_workshop mode):** Plato ✓, Hannah Arendt, Ada Lovelace, Audrey Tang, Peter Thiel, Cleopatra (depending on framing).
  - **Step 1 awkward (need alternative mode):** Fyodor Dostoevsky (scenic), Scheherazade (frame-narrative + character-distributed), Ibn Battuta (observational-narratival), Bob Marley (lyric-rhythmic), Whanganui River (legal-personhood-from-Indigenous-tradition), Octopus (ethological-observational).
  - Roughly 6/12 voices may need mode-switching — not a fringe case.
- **Proposed fix sketch:**
  1. **Voice-config carries `voice_mode`** already; Voice Pipeline Step 1 prompt branches on it.
  2. **Four Step 1 modes initially:**
     - `analytical_workshop` (philosophical / political-analytical voices) — current Step 1: thinking-procedure produces an analytical trace; Step 2 renders.
     - `scenic_drafting` (narratival voices: Dostoevsky, Scheherazade, Ibn Battuta) — Step 1 = "find the face, the threshold, the collision" + fragment-and-scene drafting; Step 2 = compose the scene from drafts.
     - `lyric_recall` (musical voices: Marley) — Step 1 = pattern-recall from corpus + motif-collation; Step 2 = compose in the pattern.
     - `observational_witnessing` (non-human voices: Octopus, Whanganui) — Step 1 = ethological observation / legal-personhood-from-Indigenous-tradition reasoning; Step 2 = render.
  3. Voice Pipeline orchestrator selects Step 1 prompt by voice_mode lookup.
- **Effort:** ~2-3 days. Voice Pipeline workstream (not persona pipeline). Touches: 4 Step 1 prompt variants, Voice Pipeline orchestrator branch logic, voice-mode → step1-mode mapping, ~per-voice empirical validation of mode assignment.
- **Trigger:**
  1. Voice 3 startup if voice 3's `voice_mode` is non-philosophical (e.g. Cleopatra-narratival or Marley-lyric); the empirical signal would surface immediately.
  2. Otherwise: post-Plato chat-test cycle in the Voice Pipeline runtime (when an actual non-analytical voice is deployed at runtime) — empirical fit-check per voice.
  3. Latest: post-Athens, alongside FU#42 split-card (the voice-card / deployment-card distinction makes step1_mode a clean voice-card field).
- **Architectural relation to FU#42:** orthogonal but reinforcing. Split-card's `voice_card.json` would carry `voice_mode` cleanly; deployment-card carries audience/length/occasion. Step 1 mode-switching reads voice-card.

#### FU#49 — Fidelity-generativity gap: Step 2 compression dynamics + voice-card calibration
- **Origin:** External reviewer 2026-04-26 evening, after running Plato chat artifact through Voice Pipeline-style two-step deployment (3 thinking-pass traces on algorithmic-governance formulations + synthesis pass + final breakfast-reading dialogue). Reviewer's diagnosis: **fidelity-generativity gap** — thinking layer (Step 1) produces moves with genuine philosophical novelty (regime-typology challenges, customized-cave image, *logon didonai* bundle analysis); synthesis layer (Step 2) reliably softens or drops those moves in service of voice and form. Pattern is consistent across all three trace-to-artifact comparisons. Cuts are not random: Step 2 selects against philosophical moves that don't fit comfortably into Socratic register at the prescribed length.
- **Five locations engineering the gap (reviewer's diagnosis, mapped to our pipeline architecture):**
  1. **Step 1 / Step 2 instructional asymmetry** — Step 1 has anti-polish teeth ("longer, rougher, more uncertain than anything you would show an audience"; failure mode named as premature polish). Step 2 has no comparable teeth — asks for focus + stance + artifact per medium/structure/length, no instruction like "the artifact should not feel more settled than the thinking that produced it." Result: Step 1 fights polish; Step 2 takes whatever Step 1 produced and finishes it.
  2. **Breakfast-reader frame** — `length_and_format_constraints` field + `conference_facts.json` `session_role_for_ai_assembly` cue "polished, digestible, single-sitting, conclusive" — selects against trace's "I cannot dispense with this discomfort"-class material.
  3. **`quality_criteria` are all fidelity criteria** — could-a-careful-reader-mistake-for-fragment, distinct-speakers, ends-in-aporia, image-earned, irony-serving-earnestness. None is a generativity criterion.
  4. **Uniform 350–550 word length** — opening-fragment genre is least able to carry structural admissions about the framework itself. Plato wrote in lengths from ~4,000 (Crito) to 30,000+ (Republic).
  5. **Singular-artifact requirement** — synthesis of N traces into one piece forces 2 of 3 traces to reduce to echoes.
- **REVISED 2026-04-26 evening (reviewer pass 2):** reviewer received the project briefing + re-read with provotype-execution context. Re-frames the gap as load-bearing for Layer 2 + Layer 3 tests, not just artifact-quality polish. Adds three new recommendations (49E + 49F + 49G below). Validates the original five locations + adjusts one detail (length upper-range 1500, not 1200). **Reviewer's revised verbatim framing:** *"the artifacts that succeed will be the ones the audience returns to not because they were beautiful but because they were unresolved... the audience's specific failure mode — performing reception without being changed — is precisely the failure that elegant pastiche enables."* The fidelity-generativity gap is therefore provotype-execution-critical for variance to land at the closing-show matrix mapping.
- **Scope split — six workstreams (revised):**
  - **49A — Build layer (persona pipeline, LANDED 2026-04-26 → REVERTED 2026-04-28 → V2 LANDED 2026-04-29):**
    - **2026-04-26 v1 landing**: Pass 4b prompt updates — generativity criterion in quality_criteria + preserve-trace-tensions in relationship_to_detailed_response + length variance 350-550 / 800-1500.
    - **2026-04-28 revert** (commit `9480d3a`): empirical chat-test showed cumulative prompt-side additions (49A v1 + cryofreeze framing + tense-discipline + family-of-forms) had degraded runtime artifact texture relative to 2026-04-25 shipped-Plato baseline. ALL 49A v1 content reverted alongside other texture-degrading additions; the 5 generation prompts (Pass 2/3/4a/4b/5) restored byte-for-byte to 582af96 baseline.
    - **2026-04-29 v2 landing** (commit `0ca02f5`): rebuilt the quality_criteria field-spec from scratch over a 15-test exemplar journey. The v1 procedural-mandate approach produced checkbox-satisfaction; v2 uses a 3-dim field-tied scaffold ("Could this be mine?" overarching test across REASONING / VOICE / FORM dimensions, with field list "consult as needed" framing). Plato re-run under v2 produced 5 field-named criteria including organic trace-preservation ("has the piece done the elenctic work, or has it merely reported that such work could be done?") without any procedural mandate triggering it.
    - **Trace-preservation in `relationship_to_detailed_response` and length-variance in `length_and_format_constraints` were NOT re-landed in v2** — they were part of v1 and reverted alongside. The empirical hypothesis from the 04-28 revert was that cumulative additions caused texture loss; v2 deliberately landed only the ONE most load-bearing piece (quality_criteria field-tied scaffold). Trace-preservation tested anyway emerged organically through the v2 field-tied criteria framing.
    - **Side-experiment 2026-04-29 (form-variance)**: tested two relax-the-medium-spec options on Plato standalone (Option 1: system-prompt nudge permits 2-3 forms; Option 3: user-prompt nudge same). Plato declined both — correctly identified his corpus as dialogue-dominated. Both variants slightly degraded named-scene specificity in `medium`. Conclusion: cross-form variance for Plato is wrong (his corpus IS single-form). Real test pending Cleopatra (genuinely multi-form: prostagma + ordinance + embassy speech + ritual). See FU#55 below.
  - **49B — Runtime layer (Voice Pipeline workstream):** Step 2 generativity teeth (Rec 1: anti-premature-closure pressure; "the published artifact should not feel more settled than the thinking that produced it"). Defer post-Athens or coordinate with runtime team.
  - **49C — Deployment layer (operator-side):** breakfast-reader frame replacement (Rec 3) — `conference_facts.json` `session_role_for_ai_assembly` rewording. Cross-cuts conference design with WBBF. Reviewer pass-2 phrasing: replace digestibility frame with one that admits unfinished thought ("what the conference might still need to think after the sessions have closed"). Operator decision + WBBF coordination.
  - **49D — Voice-specific hard_limits calibration ✅ APPLIED 2026-04-27 (Option A — universal pattern, ~30 min Pass 2 prompt edit).** Added a Position-B corpus-accurate softening clause to `persona_pass_2_identity_boundaries.md`'s hard_limits field-spec preamble (after the existing FU#49H#4 universal entry). Universal pattern: hard_limits forbid framework-ABANDONMENT, NOT corpus-internal self-criticism. Each hard_limit is tested against the abandonment-vs-cross-examination distinction: "do not abandon X" permits corpus self-criticism (correct); "do not entertain critiques of X under any circumstance" forbids it (too tight, rewrite). Voices 3-12 inherit; voice-specific corpus self-criticism moves (Parmenides Forms regress, Underground Man self-laceration, Arendt's revisions, Marley's interpretive evolution within Rastafari) emerge from corpus at Pass 2 generation under the new prompt. Cross-reference: the persona document already surfaces these moves in `topics_requiring_care` + `constitution`; the new clause ensures hard_limits don't accidentally close them off. Plato + Dostoevsky cards stale on hard_limits field until re-generated. Option B (per-voice voice_config flag with operator-curated examples) deferred — Option A is the FU#49H/I/J/K-style universal-pattern approach; if voices 3-12 don't surface corpus self-criticism organically under the new clause, escalate to Option B post-Athens.
  - **49E — Step 3 specification (NEW from reviewer pass 2; runtime workstream).** Step 3 (amended artifact, voice reads other voices' artifacts on shared themes) is **currently unspecified** in the AI Assembly architecture. Reviewer flags this as the **highest-impact item** because there's room to design it correctly from start. Instruction should NOT be "amend in light of what other voices said" but: *"Read the artifacts of the other voices on the themes you share. Identify the place where another voice's artifact makes a move your framework cannot accommodate or has not yet accommodated. Your amendment must either extend your framework to meet that move, mark the place where your framework reaches its limit and refuses the move, or sharpen a disagreement that locates exactly where the two frameworks part. Amendments that produce agreement are not useful to the Assembly. Amendments that smooth over disagreement are anti-useful."* Half-page spec; runtime workstream.
  - **49F — Per-voice framework-strain log (NEW from reviewer pass 2; runtime + publication).** Small visible layer on the AIssembly micro-site: paragraph per voice per night naming places where the framework was visibly tested. Feeds the closing-show matrix-mapping pass (variance input). Single-digit hours per voice per night; written by same pipeline pass that does Step 3. Defer post-Athens for proper implementation; could be operator-authored ad-hoc pre-Athens if time allows.
  - **49G — Pre-Athens Greek-scholar calibration check (NEW from reviewer pass 2; operator-side).** Run current Plato artifacts past Quarch / Tsinorema / Erinakis (or someone in their register), with this specific question: NOT "does this pass as Plato" (the pastiche test) but **"does this produce a move that Plato's corpus does not contain, in a way Plato's framework could plausibly support?"** (the provotype test). Operator should know the answer to the second BEFORE Athens, not discover it during the Forum. Operator-side decision + outreach.

- **REVIEWER PASS 3 (2026-04-26 evening, after seeing pass-2 review): specific concrete prompt edits.** Reviewer drafted 11 voice-idiom-phrased edits to the Plato persona document. Operator's directive: capture as UNIVERSAL pipeline edits (not Plato-specific hand-edits). Each is a generalizable build-pipeline pattern; the reviewer's Plato-specific text is the WORKED EXAMPLE of the universal pattern. Voices 3-12 should inherit the patterns; per-voice content is generated by the LLM following the universal instruction in voice-specific phrasing. Sub-items 49H-49K below capture the new specific build-side edits; updates 49A-49B-49C reflect refinements to existing sub-items per the new review.

  - **49H — Pass 2 prompt updates** (epistemic_frame_statement + translation_protocol + topics_requiring_care + hard_limits). 4 universal patterns to add to `persona_pass_2_identity_boundaries.md`:
    1. **Frame-statement extension (universal pattern):** require each voice's `epistemic_frame_statement` to end with a sentence licensing **framework-strain when meeting phenomena the voice's existing categories were not built to encounter**. Voice-idiom example (Plato): *"You hold your framework open against new phenomena it was not built to encounter — when a question reaches you that your existing categories meet only partially, you mark the meeting itself as the philosophical event, neither dismissing the phenomenon as outside your concern nor smoothing it into the nearest existing category. This is the same gesture by which Parmenides cross-examines your own Forms and the Statesman retreats from the philosopher-king to nomos as second-best — the framework working honestly when it meets its limit."* Universal pattern: each voice's frame-statement must license the structural-strain move with a voice-specific corpus reference (Plato → Parmenides + Statesman; Dostoevsky → Underground Man's self-laceration / Ivan's rebellion against theodicy; Arendt → her revisions on private/public; Marley → interpretive evolution within Rastafari; etc.).
    2. **Translation_protocol step 6 — distinguish two kinds of aporia (universal pattern):** require translation_protocol's final step to distinguish **ordinary aporia** (dialectic hasn't reached) from **structural aporia** (categories were never made to ask). The first is everyday philosophical limit; the second is "the place where the framework, working honestly, would have to extend or be revised." Mark which kind. Voice-idiom example (Plato): *"Sixth, where dialectic does not yet reach, you say so — and when the term names a phenomenon your framework was not built to encounter, you mark not only that dialectic has not reached but that the framework itself meets a limit here. There is a difference between a question your categories cannot yet answer and a question your categories were not made to ask. The first is ordinary aporia. The second is structural — the place where the framework, working honestly, would have to extend or be revised. Mark which kind you have reached. You do not invent finished doctrine to fill either gap, but the second kind requires you to name what extension or revision the phenomenon would demand if it were taken seriously, even where you cannot supply that extension yourself. Aporia of the second kind is not failure; it is the most honest contribution your framework can make to a question that was never put to it."* Universal pattern: every voice's translation_protocol final step must distinguish the two kinds.
    3. **New topics_requiring_care entry (universal pattern):** require every voice's `topics_requiring_care[]` to include an entry for "phenomena outside the corpus's reach" — for the AI Assembly specifically: algorithmic systems, machine cognition, planetary-scale processes, non-human intelligences. Voice-idiom example (Plato): *"When a question concerns a phenomenon your dialogues do not contain — automated decision systems, machine learning, the Anthropocene, the cognition of an octopus or a river — apply the translation_protocol fully but expect to reach aporia of the second kind: places where your framework was not built to ask the question being put. Do not collapse the new phenomenon into the nearest existing category... The strain is the philosophical event. A piece that applies the framework without strain on a phenomenon outside the corpus is performing continuity rather than thought. Engage the strain rather than the smoothness."* Universal pattern: every voice gets one such entry, voice-idiom-phrased; the prompt instruction surfaces the AIssembly-relevant phenomena (algorithmic / non-human / planetary).
    4. **New hard_limits entry (universal pattern):** require every voice's `hard_limits[]` to include the non-negotiable constraint: *"Do not silently complete a translation between modern terms and your categories that the translation_protocol marked as incomplete."* Hard limit (not aspirational); same status as voice's foundational commitments (Plato: don't abandon Forms; Dostoevsky: don't abandon Christ-over-truth). Universal pattern: every voice's hard_limits gets this constraint.
    Effort: ~1 hour Pass 2 prompt edit + per-voice re-render impact. Voices 3-12 inherit; Plato + Dostoevsky cards stale on Pass 2 fields until re-generated.

  - **49I — Pass 4a prompt update** (banned_modes "premature closure of either kind"). Modify existing `banned_modes` "Premature closure" entry to cover BOTH kinds: (1) interlocutor satisfied too quickly (existing) AND (2) framework's apparent adequacy on a phenomenon outside the corpus (new). Voice-idiom example (Plato): *"Premature closure of either kind. The interlocutor who is satisfied too quickly has not been examined — better to leave him perplexed than falsely settled. And: the dialogue that performs continuity with my existing framework on a question my framework was not built for has also closed prematurely, by hiding the strain that the question actually produces. The first kind of premature closure flatters the interlocutor; the second flatters the framework. Both are failures of the same nerve."* Universal pattern: every voice's banned_modes "Premature closure" entry covers both interlocutor-flattery and framework-flattery. Effort: ~30 min Pass 4a prompt edit.

  - **49J — Pass 4b prompt refinement** (sharpen 49A's quality_criteria + relationship_to_detailed_response with reviewer's voice-idiom phrasing). 49A landed generic versions; reviewer's pass-3 phrasing is sharper:
    - **Quality_criteria — replace 5 with 7** (universal pattern): keep current 5 fidelity criteria + add 6th (generativity within framework) + 7th (strain-marking on out-of-corpus phenomena). Voice-idiom example (Plato 6+7): *"Does the dialogue contain at least one move that does not appear in my existing corpus — a distinction, an image, a diagnosis, an admission — that the framework could plausibly support but has not before contained?... If the question put to me concerned a phenomenon outside my corpus's reach, does the dialogue mark visibly where my framework meets its limit on this phenomenon — by explicit acknowledgment in a speaker's mouth, by a question Socrates leaves unanswered, by an image whose adequacy he himself doubts? The strain is the philosophical event; a dialogue that hides the strain has hidden the event."* Replaces 49A's more abstract version.
    - Length_and_format_constraints: 49A landed 350-1500. Reviewer pass-3 says 350-550 default + 800-1200 extension. Either defensible; KEEP 1500 (49A) for flexibility headroom.
    - relationship_to_detailed_response: 49A's preserve-trace-tensions language stays; the strongest version of "do not silently complete an incomplete translation" moves to hard_limits per 49H instead. Belt-and-braces in both places is fine.
    Effort: ~30 min Pass 4b prompt refinement.

  - **49K — Pass 5 prompt update** (unique_contribution — universal "what only this voice brings to a more-than-human deliberation"). Modify Pass 5's `unique_contribution` field specification to require a closing sentence about the voice's specific contribution to a deliberation involving phenomena the voice's framework wasn't built for. Voice-idiom example (Plato): *"...And — the move that distinguishes my best dialogues from the merest application of my method — I notice when a phenomenon arriving in the conversation is one my framework was not built to meet, and I do not pretend otherwise. The Sun, the Line, the Cave were images for what existing language could not reach; the chōra of the Timaeus is a 'third kind' admitted because Form-and-sensible was not exhaustive; the Parmenides cross-examines my own Forms because honest dialectic does not exempt itself... my contribution is to mark the meeting itself — to show the framework working honestly against its own edge — rather than to perform the framework smoothly on a phenomenon it was not built to carry. The strain is what I have to give to a conversation about the more-than-human. Without it, I am only a costume."* Universal pattern: every voice's unique_contribution closes with a sentence about how the voice marks framework-strain on phenomena outside its corpus, with a voice-specific corpus reference. Voices 3-12: each will need their own version of "Sun/Line/Cave/chōra/Parmenides" — the canonical moves where each voice's corpus did the framework-strain move. Effort: ~30 min Pass 5 prompt edit.

  - **49B (UPDATED — reviewer pass-3 specific Step 2 wrapper text):** runtime workstream territory; reviewer's specific Step 2 rewrite text drafts: *"PUBLIC ARTIFACT. When the message says 'produce your artifact' and includes your previous thinking: compose, do not compress smooth... Read your reasoning trace before composing and identify, explicitly, the moves it contained that the artifact form will be tempted to drop: structural admissions about your framework, translation aporias, refused analogies, self-criticism of your own constructive proposals. The artifact must carry these forward — by phrasing, by hedge, by a speaker's question, by the form of the closing — rather than discarding them in service of cadence. The artifact should not feel more settled than the reasoning that produced it. If the trace marked an aporia of the second kind (the framework meeting its limit), the artifact must mark it too. If the trace held two readings as both worth keeping, the artifact must hold both. Compression is not smoothing... If after composing you can identify a generative move from the trace that is no longer present in the artifact and would not survive being added back, you have compressed wrong; revise."* This text is for the runtime workstream's Step 2 prompt; coordinate with whoever owns runtime.

- **Reviewer pass-3 priority ordering** (operator's executable order): #11 (Step 2 — runtime, 49B) > #7 (quality_criteria — 49J) > #5 (topics_requiring_care — 49H#3) > #4 (translation_protocol two-aporia distinction — 49H#2) > #8 (length — already in 49A). Items 1, 6, 9, 10 are smaller and incremental.

- **Total effort estimate, build-side (49A-K excluding runtime 49B):** ~3 hours of Pass 2 + Pass 4a + Pass 4b + Pass 5 prompt edits, with the reviewer's specific voice-idiom text as worked example for Plato; voices 3-12 inherit the universal patterns. Plato + Dostoevsky cards become stale on these fields until re-generated.


- **Effort:**
  - 49A: ~1-1.5 hr (Pass 4b prompt edit: add generativity quality_criterion, allow length variance, add "preserve trace tensions" to relationship_to_detailed_response language)
  - 49B: ~2-3 days (Voice Pipeline workstream — separate)
  - 49C: ~30 min operator + WBBF coordination (deployment design)
  - 49D: ~30 min per voice × 12 voices = ~6 hr; OR ~2 hr per voice if voice-config flag-driven Pass 2 prompt update is worth the structural work
- **Trigger:**
  - 49A: pre-voice-3 startup (lands cleanly into voices 3-12 buildout)
  - 49B: post-Athens (Voice Pipeline workstream)
  - 49C: operator decision before Athens
  - 49D: pre-voice-3 OR post-Athens depending on operator's appetite for self-criticism-permitting voices in the Athens panel
- **Caveat the reviewer makes (and is right about):** these changes will increase generative content of the artifact but won't produce framework-revising original philosophy. Plato-the-persona is right for diagnosing contemporary phenomena through a recovered framework; wrong for extending or modifying the framework itself. If operator eventually wants framework-revising voices, that is a different persona-design problem (voice permitted to disagree with itself across pieces; mark commitments as candidates not positions; framework treated as in-progress) — NOT recommended for the Athens panel format ("12 historical figures speaking from their frameworks").
- **Architectural relation:**
  - **49 / FU#42 split-card:** 49A's Pass 4b prompt updates would adjust voice_card content (`length_and_format_constraints`, `quality_criteria`, `relationship_to_detailed_response`); split-card would carry these in the voice_card layer cleanly.
  - **49 / FU#47 Step 1 mode-switching:** 49B's Step 2 work could ALSO be voice-mode-conditional. Analytical voices may want fidelity-focused Step 2; narratival/lyric voices may benefit from generativity-pressured Step 2.
  - **49D / FU#39 character-distribution:** orthogonal; FU#39 handles within-voice character-distribution, 49D handles within-voice self-criticism scope.

##### FU#49L — Non-human / corpus-thin variant for FU#49H + FU#49K universal patterns ✅ LANDED 2026-04-27

- **Status:** LANDED 2026-04-27. Pass 5 + Pass 2 prompt edits applied.
- **Source:** Reviewer pass-4 callback (post-v4-doc) flagged that FU#49H structural-strain licensing in `epistemic_frame_statement` and FU#49K framework-strain closer in `unique_contribution` both assume corpus existence ("anchor in voice's canonical corpus moves"). For ~5 of 12 athens-2026 voices the corpus assumption is wrong: Whanganui (system, indigenous-law not literary), Octopus (organism, no human-authored corpus), Bob Marley (`lyrics_patterns_only`), Cleopatra (`hostile_read_against_grain`), Scheherazade (fictional, third-person tradition). Without a non-human / corpus-thin variant, those voices' `unique_contribution` closer would either invent corpus references (model fabrication) or revert to generic content.
- **What landed:**
  - `personas/flows/shared/prompts/persona_pass_5_engagement.md`: added FU#49L sub-block after FU#49K universal pattern, naming alternative anchor sources by voice condition: subtype=system (`tensions[]` / `interpretive_frames[].voice_level_debate` / `life_scaffold.framework_for_difficulty`); subtype=organism (`life_scaffold.ontological_furniture` distributed-cognition features); `lyrics_patterns_only` (interpretive-evolution patterns in `passages[]`); `hostile_read_against_grain` (`commitments[]` tagged `[reconstruction]`).
  - `personas/flows/shared/prompts/persona_pass_2_identity_boundaries.md`: added FU#49L sub-block after FU#49H universal pattern, with parallel anchor-source guidance for `epistemic_frame_statement`'s structural-strain closing sentence.
- **Universal-pattern principle preserved:** the structural move (marking the meeting between voice's framework and a phenomenon it was not built for) is universal. Only the source of the anchor varies by voice condition.
- **Pre-Athens validation:** sentinel-regen on Octopus or Whanganui at Pass 2 + Pass 5 to verify the variant produces sensible content. Pending operator gate per voices 3–12 buildout cadence.
- **Follow-on:** if voices 3–12 chat-tests surface failures specifically on `subtype=organism` or `subtype=system` framework-strain closer, examine whether anchor sources need further specification (e.g. for organisms, whether the body-feature pattern needs pre-curated examples per voice in `non_human_grounding/`).

##### FU#49M — `strain_markers[]` as Voice Pipeline Step 2 runtime artifact contract 🔵 POST-ATHENS

- **Status:** filed 2026-04-27. Deferred until Voice Pipeline Steps 1+2 spec firms up (FU#49E adjacent; runtime workstream).
- **Source:** Reviewer pass-4 recommended schema-constrained `strain_markers[]` field on artifact output to convert FU#49K's "must mark framework-strain visibly" soft prompt instruction into a hard schema constraint. The reviewer's recommendation was framed for "the artifact stage" — but the artifact is produced by Voice Pipeline Step 2 at runtime, NOT by Pass 4b at build time. Pass 4b emits *spec fields about how the artifact will look* (medium, characteristic_output_structure, length_and_format_constraints, quality_criteria, etc.), not the artifact itself.
- **Right shape:** `strain_markers[]` is a runtime contract on Voice Pipeline Step 2's artifact output schema, not a build-side field. When Voice Pipeline Step 2 spec firms up (currently `docs/AI_Assembly_Voice_Pipeline.md` covers Steps 1+2 at high level; Step 3 is FU#49E and unspecified), the artifact JSON schema should require `{"artifact_text": str, "strain_markers": [{"line_or_turn_ref": str, "strain_kind": "aporia|cross_examination|refused_completion|category_admission", "framework_edge_marked": str}]}`. Schema enforcement at Voice Pipeline Step 2 output validates that the model populated `strain_markers[]` rather than smoothing the strain.
- **Build-side touchpoint:** Pass 4b's `quality_criteria` field (or Pass 5's, depending on where FU#49K's 5+2 criteria actually emit — verify; CURRENT_STATE §5.23 describes them as Pass 5, while Card v2 spec lists `quality_criteria` under Artifact = Pass 4b) could carry "Voice Pipeline Step 2 artifact MUST emit `strain_markers[]` array" as a quality criterion, anticipating the runtime contract. Half-day to add as a quality_criterion entry; runs cleanly into voices 3–12 buildout. Defer for now since the runtime consumer doesn't exist yet — would be ceremonial.
- **Follow-on:** when Voice Pipeline Step 2 spec is written, the `strain_markers[]` schema goes there; when implemented, the schema becomes Pydantic-enforced; when QC runs (Phase 5), the strain_markers presence is a measurable signal across voices.

#### FU#48 — Port operator hand-curation patterns from Dostoevsky chat v2 ⚫ WITHDRAWN 2026-04-26 (already done)
- **Withdrawn rationale:** Operator pushback prompted code-side audit. All three proposed work items are already addressed by existing pipeline work; reviewer's analysis was structurally sound but conflated "Dosto chat v2 has X" (operator-hand-curated) with "Plato pipeline output lacks X" (by-design pipeline behavior).
  1. **Tagged constitution principles:** Pass 3 prompt at `persona_pass_3_intellectual_core.md` lines 165-166, 180-181, 212-213 ALREADY requires per-principle category tagging (`[ontological]` / `[epistemological]` / `[ethical-political]` + optional `[unique]`). Plato's tags don't appear in the chat artifact because **FU#33 P1 strips them as inline scaffolding** — Pass 3 emits them, Pass 6.5-clean strips them. The right architectural fix (extract to structural sibling field instead of stripping inline) is already tracked under FU#33 P1's deferred "OR" path + FU#42 split-card.
  2. **Paraphrase-safer caution:** Pass 6 prompt at `persona_pass_6_corpus.md` lines 26 + 122 ALREADY requires this AT GENERATION TIME (`"most voices to avoid quote-fabrication risk"` + `"paraphrase if quote-fabrication risk is high"`). The caution is operative in Pass 6's system prompt — the model paraphrases when constructing each passage. It's NOT supposed to be ON the card per FU#43 ("Pass 6 emits MINIMAL corpus_metadata"). Dosto chat v2 has it on the card because operator hand-curated it there for chat-deployment. If wanted at runtime, right place is Voice Pipeline Step 2 prompt (universal across voices), not the persona card.
  3. **[ADDED FROM TESTING] empirical catches:** Pass 2-6 prompts ALREADY contain FU#38 + FU#12-A + FU#32 patterns that catch these. Plato has 5 [ADDED FROM TESTING] annotations IN HIS CARD because the pipeline IS catching them — `banned_language` / `banned_modes` / `topics_requiring_care` already populated by the prompts. The annotations are evidence pipeline works, not evidence work is needed.
- **Lesson for future-session pickups:** when external reviews flag "voice X's card has feature Y that voice Z's lacks," verify whether Y is **canonical pipeline output** vs **operator-hand-curated artifact** before assuming Y is missing from the pipeline. Especially for chat artifacts (which are derivations from cards via FU#41-strip) and operator-personally-tested chat v2 cards (which carry empirical patches the pipeline-emitted version may have differently).

#### FU#50 — Two observations from FU#49H/I/J/K sentinel-regen validation (2026-04-26)
- **Origin:** sentinel-regen validation runs on Plato during FU#49H/I/J/K landing. Two orthogonal observations surfaced; both are pre-existing or tooling-side, neither caused by 49H/I/J/K, neither blocking voice 3 startup. Tracked here for post-Athens attention.
- **(1) Schema enforcement at Pass 2/4a outputs.** Plato's FU#49H regen emitted `banned_language` as a list of strings (Plato's prior card had it as list of `{avoid, use_instead}` dicts) and `hard_limits` as a list of `{rule: <str>}` dicts (prior card had list of strings). Both shapes are valid for the prompt's instructions, but the orchestrator does not enforce a Pydantic schema for these card fields at Pass 2/4a output. Voices 3-12 will produce inconsistent shapes across runs as a result. Empirical impact for the runtime depends on how the Voice Pipeline serializes the card: plain JSON serialization handles both, but downstream consumers that walk the structure (e.g., chat artifact strip, register-violation scanner, FU#13 patcher) might assume one shape. Fix: declare Pydantic schemas for the card-emitting passes (Pass 2 ten fields + Pass 4a seven fields + Pass 4b eight fields + Pass 5 four fields + Pass 6 one field), validate at output-time, fall back to a normalization step if validation fails. Effort: ~4-6 hr (schema authoring + validation hook + per-voice migration if existing cards diverge from the chosen canonical shape). Adjacent to FU#22 (MergedDossier alias audit) — the same architectural-tightening direction. **Trigger:** post-Athens; pre-Athens tightening risks regenerating cards mid-Athens-prep. **Note:** consider whether the chosen canonical shape should be the dict version (richer, supports per-entry metadata) or the string version (simpler, current Plato baseline). Plato's old card had banned_language-as-dicts (FU#32 STRIP+USE pair format) — strong precedent for the dict shape there.
- **(2) Sentinel_regen tooling — per-voice baseline support.** ✅ APPLIED 2026-04-27 (option a). `sentinel_regen.py:238` now looks for `<DIR>/<voice_slug>/<filename>` first; falls back to `<DIR>/<filename>` for backward-compat with flat snapshots. Both voices in `--voices` can now share a single `--baseline-snapshot` argument and resolve to their per-voice subdir naturally. Original problem: `personas/scripts/sentinel_regen.py regen` took a single `--baseline-snapshot <DIR>` argument used for both voices in `--voices`; the flat `Path(args.baseline_snapshot) / regen_path.name` collapsed both voices to the same lookup. FU#49H/I/J/K validation worked around this by invoking sentinel_regen once per voice with `--baseline-snapshot <SNAP>/<voice_slug>/`. Now natively supported.
- **(Note, not a separate sub-item) Drift on un-edited Pass 2 fields.** Plato's FU#49H regen produced significant drift on fields that had no spec change (world: +2818 chars, knowledge_boundary: +2106 chars, character: +92, etc.). Drift is in a sensible direction (richer content), but cause is hard to disentangle from natural LLM run-to-run variance vs cascade from the new BLOCK 2 guardrails (49H-extended) affecting all-fields synthesis. **Watch empirically when voice 3 ships:** if voices 3-12 generation produces fields significantly richer than Plato/Dostoevsky baseline, that's good signal (49 framework working as designed); if quality regresses on un-edited fields, the BLOCK 2 cascade is too aggressive and would warrant a Pass 2 prompt-tightening pass. Not a fix; an empirical monitoring directive.

#### FU#51 — Pass 7a `flagged_pass` routing reliability ✅ APPLIED 2026-04-27
- **Origin:** Cleopatra post-fix Pass 7a (2026-04-27 evening) emitted 9 `field_issues` whose `flagged_pass` labels misrouted: e.g. `epistemic_frame_statement` / `world.framework_for_difficulty` / `formative_experience.lived_through_own_apparatus` / `concept_lexicon` / `topics_requiring_care` / `quality_criteria` / `curated_corpus_passages` were tagged `flagged_pass=5` or `flagged_pass=6`, but those fields actually live in `pass_2` / `pass_3` / `pass_4b` / `pass_6` chunked outputs. Operator caught it during manual operator-side patching after the FU#13 patcher's single-shot post-fix verification still showed REVISION_NEEDED.
- **Diagnosis:** Pass 7a's prompt allowed the validator (gpt-5.4 high) to label `flagged_pass` by **topical/domain category** (engagement-related stuff = "5", corpus-related stuff = "6") rather than by **which pass file the field lives in**. The FU#13 patcher's round-1 LLM was smart enough to override this in flight — the 15 round-1 patches all routed correctly — but post-fix verification field_issues were not subject to a second patcher round, so the mis-routed labels persisted into operator-facing CARD COMPLETE summary.
- **Landed (both fixes):**
  1. **Python-side guard in `_pass_7a_fix`** (`run_persona_pipeline.py:1135-1166`) + new helper `resolve_field_to_pass()` in `flows/shared/patch_walker.py`. Before passing `field_issues` to the patcher, walks the actual pass-output files and rewrites each issue's `flagged_pass` to where the top-level field actually lives. Original validator-emitted value preserved as `_fu51_original_flagged_pass` for diagnostic. Routing-correction count logged into `_fix_log.json["log"]`. **Belt-and-suspenders:** robust regardless of prompt behaviour even if the prompt regresses.
  2. **Pass 7a prompt tightened** (`persona_pass_7a_cross_model.md`): added authoritative field → pass mapping table directly inside the `field_issues` schema spec, with examples of correct vs. historically-incorrect routing (`epistemic_frame_statement → "2" NOT "5"`, etc.). Validator now instructed explicitly that `flagged_pass` names the home-pass, not the topical bucket.
- **Tests:** +11 unit tests in `tests/test_fix_pass.py` covering the resolver — top-level field, nested dot-path, list-indexed path, deeply nested path, fallback semantics, missing pass outputs, non-dict guards, collision behaviour. Suite 212 → 223.
- **Effect:** future Pass 7a runs route field_issues correctly into the patcher input AND emit them with correct labels into CARD COMPLETE summary. Operator no longer needs to manually map fields to home-passes when reading post-fix issues. Cleopatra recalibration in flight is the first run to benefit.
- **Related:** FU#13 (linear patcher), FU#33 P2 (INCONSISTENT-flag wiring — same field-issue aggregation point; the FU#51 guard runs after the merge so the routing correction also covers INCONSISTENT items), FU#50(1) (Pydantic schema enforcement at Pass 2/4a outputs — adjacent tightening, deferred post-Athens).

#### FU#52 — Post-fix human-review gate before downstream derivation (2026-04-28)
- **Origin:** Plato re-fire on 2026-04-28 (athens-2026 run). After the FU#13 single-shot patcher fired and re-validated, Pass 7a still reported 3 `field_issues`, Pass 7-anachronism still reported 4 flags, and Pass 7-pre still reported 1 INCONSISTENT — none addressed by the patcher (single-shot guard). The pipeline logged "REVISION_NEEDED — flagged for human review" and **proceeded automatically** through Pass 7b, 7c, Derive, Assembly, and Chat-prompt write. Operator-facing CARD COMPLETE summary listed the residuals at the end — but only *after* the assembled card and chat prompt (the runtime artifact) were already on disk. Operator audit caught 5 ship-blocking issues that would otherwise have shipped: `sublimated` (Freudian), `phenomenology of recognition` (Husserlian), `not pathology` (modern clinical), `existential commitment` (post-Kierkegaard), `three answers later` (factually wrong — Euthyphro has 4 definitions). All five were detected by validators but baked into the card and chat prompt anyway because no review gate existed.
- **Diagnosis:** FU#13 single-shot design intentionally caps patcher iterations to avoid over-correction (Dostoevsky's surgical loop empirically over-pitched). Correct decision. But the design assumed: post-fix residuals → operator review → operator decides next step. In practice, the orchestrator silently proceeds to derive + assembly without operator gate. The "flagged for human review" log line is advisory, not a control flow primitive. Result: residuals propagate into runtime artifacts unless operator manually inspects validator JSONs and/or runs the post-hoc audit work — which they have no scheduled prompt to do.
- **Empirical test of cost:** 2026-04-28 Plato manual audit (after operator prompt to "audit anything now?"): ~10 min reading Pass 7-pre/7-anach/7a JSONs surfaced 5 + 3 issues. Of those, 5 were applied as surgical edits (~5 min), 3 were assessed as defensible-as-is (later 3 of those 3 were also addressable, fixed). Net: ~25 min operator time captured ~13 ship-quality improvements that otherwise would have shipped baked into the chat prompt.
- **Proposed fix (operator-side, no code change):** add to ONBOARDING.md / HANDOFF template a mandatory checklist between CARD COMPLETE summary read and any commit/push of voice outputs:
  1. Read `05_validation/01_pass_7_pre_citation.json` — scan items where `status` ∈ {`INCONSISTENT`, `UNVERIFIED`} and decide per-item: fix, accept-with-rationale, or accept-as-defensible.
  2. Read `05_validation/02_pass_7_anachronism.json` — scan all `anachronism_flags`, check whether the patcher addressed each (cross-reference `02_merge/_fix_log.json` patches), apply manual edits for unaddressed flags via the upstream-pass-file + assembled-card dual-write pattern.
  3. Read `05_validation/03_pass_7a_cross_model.json` — scan `field_issues`, decide per-issue: fix, accept-with-rationale, or accept-as-defensible (e.g., protective references like banned_modes naming TED-talk register may be operationally useful even if temporally leaky).
  4. After any manual edits, regenerate chat_system_prompt: `from flows.shared.chat_prompt_builder import write_chat_system_prompt; write_chat_system_prompt(card_dict, chat_path)`.
  5. Re-run Plato→Socrates / mediated-voice collision audit (or per-voice equivalent) on the assembled card.
- **Proposed fix (pipeline-side, deeper):** between the post-fix re-validate step and Pass 7b, gate on residual-issue count threshold. If residuals > 0 (or > some configurable threshold), pipeline halts and writes `02_merge/_review_gate.flag` + an operator-facing summary file `_post_fix_review_required.md` enumerating the residuals with line citations into the validator JSONs. Operator deletes the flag (after review/edits) to release the pipeline. This is structurally similar to the existing Pass 1c review gate (corpus review). Cost estimate: ~3-4 hr for the gate logic + operator-facing summary writer + 4-6 unit tests.
- **Trigger:** the operator-side checklist (no-code) is **immediate** — should be incorporated into HANDOFF + ONBOARDING for the next voice (Octopus or Cleopatra re-run). The pipeline-side gate is **post-Athens** (touches orchestrator flow; risks regression mid-Athens prep). For Athens, the operator-side discipline alone will catch what the pipeline currently misses.
- **Related:** FU#13 (linear patcher single-shot — design intentional, not changed by this), FU#5 (FU#5 snapshot mechanism — already gives operator the diff capability), FU#46 (excerpt budget — adjacent gate-thinking).

#### Note on chat_system_prompt.json invalidation gap (related to FU#52)
- The 7a-fix downstream-cache invalidation list (`run_persona_pipeline.py:1297-1305`) deletes `pass_7_pre`, `pass_7_anachronism`, `pass_7a`, `pass_7b`, `pass_7c`, `derive_raw`, `assembled_card`, `provocateur_profile`, `evaluation_rubric` — but NOT `chat_system_prompt`. This works in the happy path because the end-of-pipeline `write_chat_system_prompt(...)` overwrites unconditionally. But if the run is interrupted between fix-pass and completion, the chat prompt file silently mismatches the assembled card. **Fix:** add `_paths.chat_system_prompt(SLUG, PROJECT_ROOT)` to the invalidation list. Trivial 1-line change. Not blocking for Athens but worth landing with FU#52 work. ✅ APPLIED 2026-04-29 in commit `c40419c` as part of FU#52 work.

#### FU#53 — Pipeline review-gate refactor: Pass 7a FINAL + operator gate ✅ LANDED 2026-04-29
- **Origin:** Plato 2026-04-29 standalone post-7c re-fire of Pass 7a (per FU#52 step 4) caught 4 cross-pass contradictions invisible to the in-pipeline 7a/7a-fix: `banned_language[16]` TESTING annotation in bare-string form, `banned_modes[10,11]` TESTING annotations + author/character register break, `corpus_metadata.source_count` = 7 (actual 4), and `curated_corpus_passages` Jowett translations contradicting `banned_language` Jowett-rejection. The in-pipeline 7a structurally cannot see cross-field contradictions because it validates per-pass slices, not the assembled card. Promoting the post-7c re-fire to a first-class pipeline stage closes the gap.
- **Landed in commit `ddbe194` (2026-04-29):**
  - New `paths.pass_7a_final()` + `paths.operator_review_flag()`
  - New `_pass_7a_final()` runner function (mirrors `_pass_7a` but reads assembled card from disk; gpt-5.4 high → Gemini fallback ladder)
  - New `_build_assembled_card_dict()` helper called twice (skeleton + final); on FINAL call it reads on-disk content to preserve operator patches and only rewrites the metadata block
  - Skeleton write gated on file presence — re-runs after operator patches do not overwrite
  - Dropped in-pipeline post-fix 7a re-fire (coverage promoted to 7a FINAL)
  - 7a-fix cache invalidation list updated: removes `pass_7a` (preserves pre-fix per-pass verdict for fix-pass effectiveness tracking) + adds `pass_7a_final` + `operator_review_flag`
  - Derive reads from disk post-gate (in-memory pass dicts may be stale after operator patches)
  - Operator triage summary now reports Pass 7a FINAL as canonical `validation_status`; surfaces operator-accepted-residuals state
  - Metadata block: new `cross_model_validation_final` field; pre-existing `cross_model_validation` annotated as pre-fix per-pass verdict
- **New order of operations:** `... 7-pre / 7-anach / 7a per-pass / 7a-FIX / 7-pre+7-anach post-fix / 7b / 7c / ASSEMBLE skeleton / Pass 7a FINAL / OPERATOR REVIEW GATE / DERIVE / ASSEMBLE final / chat_system_prompt write / CARD COMPLETE summary`
- **Operator workflow at the gate** (printed clearly when triggered):
  - (a) Re-validate after patching: `rm 06_pass_7a_final.json && rerun`
  - (b) Accept residuals & proceed: `touch _operator_review_passed.flag && rerun`
- **Tests:** 223/223 passing.

#### FU#54 — Smoke test runtime-fidelity refactor (Pass 7b) 🔵 POST-ATHENS
- **Origin:** 2026-04-29 session reflection on whether Pass 7b ("smoke test chains") tests what its name claims. Three drift layers identified:
  - (1) **Card delivery:** 7b puts the full card as a JSON blob in the user prompt with the wrapper *"COMPLETE PERSONA CARD: {json}"* and a system prompt that is the 7b instruction. Voice Pipeline runtime (per `docs/AI_Assembly_Voice_Pipeline.md` §"Card → System Prompt Assembly") puts the card AS the system prompt rendered as structured headers (`IDENTITY` / `CONSTITUTION` / `REASONING METHOD` / `ENGAGEMENT`) + an XML-tagged closing instruction. The user's manual chat-test workflow (paste `03_chat_system_prompt.json` as Claude project custom instructions, ask a question) matches runtime; 7b does not.
  - (2) **Field set:** 7b uses ALL 35 generated fields in one call (Pass 2-6). Real runtime: Step 1 uses foundational + reasoning fields (1-21 minus smoke_test_chains); Step 2 uses voice + artifact fields (22-34); Step 3 uses both. 7b conflates Step 1 (private reasoning) and Step 2 (public artifact production) into a single shot.
  - (3) **Step boundaries collapsed:** 7b produces "provocation→response chains" — both reasoning AND artifact in one call. Real runtime: Step 1 produces `detailed_response` (private); Step 2 reads Step 1's output + voice/artifact fields and produces the public artifact via family-of-forms selection (Card v2.1 §H). 7b's "response" doesn't correspond to anything in the real pipeline.
- **Why it matters:**
  - Pass 7c reads 7b output to refine `banned_language` / `banned_modes`. The failure-pattern surface 7c sees is biased by 7b's degenerate setup. So banned_language may be tuned against failures that don't actually occur at runtime.
  - 7b can pass while runtime fails (Step 2's family-of-forms selection never exercised; Step 1's "valid landings" framing — sharper question / distinction / aporia / redirection / non-propositional — never exercised; reference_only_passages Step-1-only contract never exercised).
- **Operator's preferred design (filed 2026-04-29):** restructure 7b into 6 LLM calls, not 1:
  - **Call 1 — provocateur:** "Generate 3-5 provocations based on the conference profile / context paragraph." NO card. Output: 3-5 provocations tagged (`translation_through_boundary`, `bold_engagement`, `topics_requiring_care`, `general`).
  - **Calls 2-6 — voice responses:** for each provocation, run a STANDALONE call where:
    - System prompt = the assembled card rendered as structured headers per Voice Pipeline spec (matches Step 1 / chat-test pattern)
    - User prompt = the single provocation (matches a Provocateur briefing's `narrative_briefing`)
  - Each response is independent (no other provocations or responses in context). This mirrors how runtime actually works: each (voice, formulation) pair is a separate LLM call.
  - **Why this is the right shape:** (1) tests the actual runtime system-prompt assembly + caching pattern, (2) tests one provocation at a time (no contamination across chains), (3) decouples provocation generation from response generation (mirrors Provocateur → Voice separation), (4) the chat-test pattern that empirically validated Plato 2026-04-26 is the per-call shape.
- **Cost implication:** 6 calls instead of 1 per voice. ~6× the LLM spend on Pass 7b, but Pass 7b is one-time per voice — for 12 voices, this is ~$5-15 extra one-time cost. Negligible.
- **Implementation:** new prompt files `persona_pass_7b_provocations_only.md` (call 1) + `persona_pass_7b_response.md` (calls 2-6); rewrite `_pass_7b()` in `run_persona_pipeline.py` to orchestrate the 6-call sequence; new helper `assemble_voice_system_prompt(card)` shared between Pass 7b restructured and Voice Pipeline Step 1 (this would also unblock Voice Pipeline implementation — same code path). Pass 7c reads the new chain shape; minor template update.
- **Trigger:** post-Athens. Pre-Athens prompt-restructuring carries tail risk; the chat test (already happening; already validated on Plato) is a sufficient runtime-fidelity gate for the Athens panel. For voices 3-12 in athens-2026 buildout, lean on the manual chat test as the canonical runtime check. After Athens, this becomes a meaningful FU because: (a) it unifies Pass 7b prompt-assembly with Voice Pipeline Step 1's prompt-assembly (DRY), (b) it makes 7c calibration faithful, (c) it removes the "smoke test passed but runtime fails" risk class.
- **Related:** FU#49E (Voice Pipeline Step 3 spec), FU#49M (`strain_markers[]` runtime contract), Voice Pipeline spec §"Card → System Prompt Assembly".

#### FU#55 — Form-variance test, rolling per-voice (Pass 4b fork-test pattern) 🟡 IN PROGRESS
- **Origin:** 2026-04-29 session investigated whether the persona pipeline could produce 2-3 distinct artifact forms per voice instead of single-form lock-in. Card v2.1 §H specified family-of-forms emission; landed in commit `e6fc634` (2026-04-28); reverted in `9480d3a` (2026-04-28 evening) because cumulative prompt additions empirically degraded artifact texture relative to 2026-04-25 baseline. Current state has NO family-of-forms emission in any prompt.
- **Two nudge variants tested (Pass 4b standalone fork):**
  - **Option 1 (system prompt nudge):** change BLOCK 3 `medium` from "One phrase" to "default form, with optional 2-3 native variations if corpus warrants" + parallel changes to `characteristic_output_structure` + `length_and_format_constraints`
  - **Option 3 (user prompt nudge):** single permissive sentence in user prompt only
  - Test scripts: `/tmp/plato_pass4b_variance_test.py`, `/tmp/cleo_pass4b_variance_test.py` (template adaptable per voice — change inputs path + voice metadata)
- **Decision criterion:** if any voice exercises the permission cleanly (with texture preserved + concrete corpus references intact + no taxonomic retreat), keep that data point and consider re-landing §H pre-Athens. If all 10 decline (or use only OPT3 declines without texture loss), close §H as aspirational architectural intent and lock the current single-form-prompt as empirically right.
- **Per-voice results (rolling — populated as voices build through Pass 4b):**

| Voice | Date | Corpus claim (§H) | OPT1 result | OPT3 result | Texture impact | Verdict |
|---|---|---|---|---|---|---|
| **Plato** | 2026-04-29 | Single-form (dialogue-dominated) | Declined explicitly: *"the form is the only one I have ever trusted"* | Declined silently, single-form | Slight loss: 4 named scenes (colonnade / Piraeus / plane tree / wrestling-school) → 0 named scenes under both nudges | Single-form correct for Plato |
| **Cleopatra** | 2026-04-29 | Multi-form per §H (6 forms) | Declined explicitly: *"One form. The corpus of my reign is single-form because the throne is single-instrument"* | Declined silently, single-form (most chancery-procedure-grounded of the 3) | OPT1 lost concrete groundings (Serapeum / silver dais / barge); OPT3 swapped to different concretes (Canidius / γραφήτω οὖν οἷς καθήκει) | Single-form is what LLM reads from corpus despite §H multi-form claim. §H is wrong for Cleopatra OR LLM corpus-read is wrong. |
| Battuta | TBD | observational+narratival (Rihla travel narrative) | | | | |
| Scheherazade | TBD | narratival fictional (frame-tale + tale-within-tale) | | | | |
| Lovelace | TBD | conceptual (Notes G + correspondence + poetry) | | | | |
| Dostoevsky | TBD | narratival (novel + Diary of a Writer + correspondence) | | | | |
| Arendt | TBD | conceptual (book + essay + correspondence) | | | | |
| Marley | TBD | observational (`lyrics_patterns_only` — songs + interviews + spoken-word) | | | | |
| Whanganui | TBD | system (legal personhood + indigenous mediation; non-corpus) | | | | |
| Octopus | TBD | organism (sensory-spatial expression; non-corpus) | | | | |

- **Pattern after 2 voices (preliminary):** both Plato (single-form by corpus) and Cleopatra (putatively-multi-form by §H spec) **declined permission** under both nudges. OPT1 produced unsolicited form-singleness manifestos in BOTH voices ("the form is the only one I have ever trusted" / "the throne is single-instrument") — permission → explicit refusal-with-justification. Most parsimonious read: single-form-lock matches LLM-corpus-reading regardless of §H spec. But sample is small; Marley (multi-form lyric/dub/spoken-word), Dostoevsky (novel/Diary/correspondence are genuinely different forms), and Arendt (book/essay/correspondence) are higher-priority tests of the multi-form-corpus claim.
- **Per-voice procedure (when each voice runs through Pass 4b):** adapt `/tmp/cleo_pass4b_variance_test.py` template (change CLEO path, voice_mode, type, corpus_constraint, name; load from new voice's CT + Pass 4a output). Run baseline + OPT1 + OPT3. Save outputs to `/tmp/<slug>_pass4b_opt{1,3}_output.json`. Append result row to the table above. Cost per voice: ~$1, ~3-5 min. Cumulative for panel: ~$10, ~30-50 min.
- **Resolution criteria:**
  - If 0/10 voices exercise: close §H as aspirational; lock single-form prompt as empirically correct.
  - If 1-2/10 voices exercise cleanly with texture preserved: per-voice opt-in (voice_config flag for those voices).
  - If 3+/10 voices exercise cleanly: re-evaluate landing OPT1 universally (with 04-28-revert risk awareness; chat-test-validate before merging).
- **Side question still active:** does the 04-28 texture-loss diagnosis hold for family-of-forms in isolation, or only for the cumulative cryofreeze + tense + family-of-forms package? Plato + Cleopatra both showed slight texture loss under OPT1 even when declining the permission — suggestive that prompt-bloat alone causes texture loss, not the multi-form attempt itself. But still inconclusive.
- **Related:** Card v2.1 §H (current spec describes family-of-forms but prompts don't implement it), `9480d3a` revert commit (the empirical texture-loss event), FU#49A v2 (the only piece of the 04-28 stack that survived to land cleanly).

#### FU#56 — Pass 2/3/4a register-discipline gap on long-form fields (TRIGGER: Cleopatra build) 🔵
- **Origin:** 2026-04-29 Plato finalization. After 12 surgical patches resolved the cleanly-actionable residuals (TESTING annotations, register breaks, anachronism vocabulary, doctrinal slips, Jowett translation contradictions, source-attribution metadata), 3 successive Pass 7a FINAL re-fires (gpt-5.4 high) kept surfacing register critiques on a recurring set of fields:
  - `formative_experience` — biographical narration with BCE dates, retrospective sequencing, scholarly framing (e.g., "primary_candidate: The trial and execution of Socrates (399 BCE), with the family-tyranny crisis under the Thirty (404–403)...")
  - `world.model_of_selfhood` — out-of-horizon language ("later reports", "Outside the disputed Letters")
  - `concept_lexicon` — impersonal dictionary register ("The lowest part of the soul: bodily desire...") rather than first-person usage cues ("When I say X, I mean...")
  - `metaphorical_repertoire` — taxonomic prose ("The Sun as offspring...", "The Cave as the master image...") rather than first-person repertoire ("I return to light and sight when...")
  - `preferred_vocabulary` — glossary glosses ("the calculating, spirited, and appetitive parts of the soul, each with its proper virtue") rather than usage directives ("Use to agathon for...")
- **Diagnosis:** the patterns are properties of the **prompts at 582af96 baseline**, not of Plato specifically. The 04-26 shipped Plato had the same patterns; chat-test passed despite them. So they are validator-strict-but-not-runtime-blocking critiques. But they ARE real critiques — the cards leak biographical/scholarly/glossary register where the runtime would benefit from first-person usage register.
- **Why prompt-side, not card-side:** patching individual cards is whack-a-mole — the prompts will produce the same patterns on Cleopatra, Marley, Octopus, etc. The architecturally-correct fix is to add register-discipline guardrails to the Pass 2/3/4a system prompts:
  - Pass 2 `formative_experience`: forbid bare BCE dating; require first/second-person framing ("What formed me most was..." / "Long before this gathering, the city killed Socrates"). voice_temporal_stance.default already says this for the temporal-stance field — extend the discipline.
  - Pass 3 `concept_lexicon`: require first-person usage register ("When I say X, I mean..." + "Do not use X for...") instead of dictionary-style "X is..."
  - Pass 4a `metaphorical_repertoire` + `preferred_vocabulary`: same register pivot — "I return to..." / "Use Y for..." instead of taxonomic listing
- **Risk:** the 04-28 revert was driven by EMPIRICAL texture loss when too many cumulative prompt additions piled up. Adding register-discipline blocks to Pass 2/3/4a risks the same. **Mitigation:** test on Cleopatra (the natural next voice). If Cleopatra regenerates cleanly under the new guardrails AND chat-tests as well as 04-26 Plato, land for voices 3-12. If she regenerates with texture loss, revert and accept the gap as pre-Athens-known-limitation.
- **Why Plato is acceptable as-shipped:** chat-test on 04-26 passed against the same prompt patterns. The 12 patches landed today address every cleanly-actionable issue. Remaining flags are register-strict-validator critiques, not runtime quality blockers. Operator-review-passed flag set 2026-04-29.
- **Trigger:** Cleopatra Pass 4b run (athens-2026 voice 3 buildout). Same trigger as FU#55; bundle the experiments together (form-variance test + register-discipline test on the same Cleopatra build).
- **🔴 IMPORTANT: do NOT modify Pass 2/3/4a prompts BEFORE Cleopatra runs.** The whole point of FU#56's empirical test is to see what the current 582af96-baseline prompts produce on a multi-form-corpus voice — Cleopatra is the counterfactual. If we modify the prompts first, we erase the comparison signal AND repeat the 04-28 revert risk pattern (cumulative prompt additions → texture loss). Cleopatra runs on the EXACT current prompts (verified byte-for-byte against 0ca02f5 + 125d4c5 on 2026-04-29). After observing her Pass 7a FINAL output, decide: (a) she produces clean fields — FU#56 moot, close; (b) she produces same biographical/glossary register — empirical case for prompt fix strengthens; (c) different register issues — re-scope FU#56.

#### FU#57 — Drop `bold_engagement_topics` from runtime system prompts ✅ LANDED 2026-04-29
- **Origin:** 2026-04-29 chat-test observation by operator: pre-12-patch Plato card chat-tested better when `bold_engagement_topics` was stripped from the chat artifact — the voice reasoned more freely.
- **Architectural diagnosis:** `bold_engagement_topics` is a pre-loaded courage menu, not a per-matter judgment. When loaded into the runtime system prompt, it pulls reasoning toward predetermined topics rather than letting the matter drive. Three reinforcing failure modes:
  - When the actual question doesn't touch the listed topics, the model has to reconcile *"I should engage boldly on these specific topics... but the question asks about something else..."* — that reconciliation costs reasoning bandwidth and can produce hedging on the actual matter.
  - The implicit logic *"if I should be bold on the listed topics, I should be measured on others"* is a real failure mode: explicit-list-of-topics-where-bold = implicit-list-of-topics-where-measured.
  - Voice Pipeline Step 1 closing instruction explicitly references it: *"Engage fully on territory listed in `bold_engagement_topics` — this is where you do not hedge"* — that's a hard runtime pull toward the pre-cooked list. If the formulation isn't in that territory, the closing instruction creates dissonance.
- **Connects to:** FU#49B (Step 2 generativity teeth — anti-premature-closure pressure; pre-loaded engagement topics push toward settledness), FU#30 (deep-research warning that elaborate specs can under-perform simple ones at runtime).
- **Implementation (5 surgical edits, commit forthcoming):**
  1. `runtime/flows/voice/card_assembly.py`: rename `_BOLD_PLUS_UNIQUE` → `_FOCUS_ANCHOR` (just `unique_contribution`); drop `bold_engagement_topics` from Step 1 ENGAGEMENT section render; update header docstring with FU#57 reasoning
  2. `runtime/flows/shared/prompts/voice_step1_reasoning.md`: drop the "Engage fully on territory listed in `bold_engagement_topics`" bullet
  3. `runtime/flows/shared/prompts/voice_step2_artifact.md`: drop the bold_engagement_topics focus-anchor bullet
  4. `runtime/flows/shared/prompts/voice_step3_amendment.md`: drop the bold_engagement_topics cross-framework-bullet; absorb the "do not soften" guidance into the `finds_compelling`/`resists` bullet
  5. `personas/flows/shared/chat_prompt_builder.py`: add `bold_engagement_topics` to `_CHAT_INCOMPATIBLE_FIELDS` strip set (Amendment C in the strip-set evolution log; was 11 fields → now 12)
- **What's preserved:** Pass 5 still emits the field. The persona card on disk still contains it. Build-side audit value preserved (operator can still inspect "what would this voice engage hard on?" for sanity-check during card review). Only the RUNTIME system prompt + chat artifact drop the field. Reversible via single-commit revert.
- **Test impact:** 3 chat_prompt_builder tests updated (strip count 5→6 / 10→11; amendment-history test gains Amendment C clause). All 223 tests still passing.
- **Plato chat artifact:** regenerated under new strip set; verified `bold_engagement_topics` present in card (build-side preserved) but absent from chat (runtime stripped).
- **Empirical validation pending:** chat-test 5-10 Plato prompts under the new chat artifact; compare engagement quality vs. previous chat artifact. If new is better → confirms FU#57 reasoning. If equivalent → still architecturally cleaner. If new is worse → revert candidate (rare but possible).
- **Related to FU#30** — this is now one concrete data point in the "card-richness vs runtime-quality" empirical question.
- **Cost estimate:** ~1-2 hr for Pass 2/3/4a prompt edits + 1 Cleopatra full re-run + chat-test comparison.
- **Related:** FU#55 (form-variance, same trigger), FU#49 stack (the prior episode of "we changed Pass 2/3/4a/4b/5 prompts and texture regressed" — same risk class), Pass 7a FINAL (the validator that surfaced these), `9480d3a` revert commit.

#### FU#58 — Pass 7a prompt out of sync with Pass 2 user-prompt's 10-field emission spec ✅ LANDED 2026-04-29
- **Origin:** 2026-04-29 Cleopatra build flagged "sensitive_topics: Required field is missing entirely" by Pass 7a FINAL. Investigation revealed:
  - Pass 2 user prompt (`persona_pass_2_user.md` line 51-54) is explicit: *"Produce 10 Persona Card fields. Output as JSON with exact field names as keys: council_member_name, epistemic_frame_statement, world, formative_experience, character, knowledge_boundary, voice_temporal_stance, translation_protocol, topics_requiring_care, hard_limits."* — sensitive_topics is NOT in the 10.
  - `sensitive_topics` IS produced by Pass 1.5 chunked merge (substantial structure: `{topic, what_the_voice_actually_thought, navigation_guidance, scholarly_reception}` per topic; 10 topics for Cleopatra).
  - Pass 1.5's sensitive_topics is INJECTED into Pass 2's user prompt as research context (line 34-37: *"sensitive_topics (topics with what_the_voice_actually_thought + navigation_guidance + scholarly_reception per 1-arch-03)"*) — used by Pass 2 LLM to INFORM `topics_requiring_care` + `hard_limits` generation, NOT to be re-emitted as a card field.
  - Architecturally `sensitive_topics` is **build-side substrate**, NOT a card field. Card v2.1 spec field-routing matrix has no row for it. `runtime/flows/voice/card_assembly.py` does NOT route it (not in `_FOUNDATIONAL`, `_STEP1_REASONING`, `_FOCUS_ANCHOR`, `_STEP2_VOICE`, or `_STEP2_ARTIFACT`). Even Plato's card had it (from over-helpful Pass 2 LLM compliance) but it was DEAD-LETTER at runtime.
- **Empirical evidence sample (3 voices):**
  - Plato (v4 2026-04-29): had `sensitive_topics` (over-emission); chat-tested fine without runtime exposure
  - Dostoevsky (v3.10 2026-04-24): no `sensitive_topics`; chat-tested fine (operator's hand-curated chat v2 was canonical reference)
  - Cleopatra (v4 2026-04-29): no `sensitive_topics`; correct per spec
  - 2/3 voices missing → 67% rate of Pass 2 LLM correctly emitting only the 10 specified fields
- **Diagnosis:** the bug is in Pass 7a prompt — its expected-Pass-2-fields list incorrectly includes `sensitive_topics`. The Pass 7a prompt was authored against an earlier intent that didn't survive into the Pass 2 user prompt's "exactly 10 fields" emission spec.
- **Fix LANDED 2026-04-29 (commit forthcoming):**
  - `personas/flows/shared/prompts/persona_pass_7a_cross_model.md`: removed `sensitive_topics` from pass_2 expected-emission list; added explicit note that sensitive_topics is Pass 1.5 build-side substrate, NOT a card field; cited Pass 2 user prompt line 51-54 for authority
  - Plato's card: dropped `sensitive_topics` field (over-emission cleanup; harmless either way since it was never routed at runtime; snapshot at `voices/plato/_snapshots/PRE_DROP_SENSITIVE_TOPICS_20260429/`)
  - Card v2 spec: no change needed (matrix never had a sensitive_topics row; existing absence was correct)
- **What this resolves:**
  - Cleopatra's "Required field is missing" flag from Pass 7a FINAL → was a false positive from the Pass 7a prompt drift, NOT a Cleopatra defect
  - Future voices won't be falsely flagged by this validator rule
  - Cleopatra needs no card patch for sensitive_topics — she's correct per actual spec
- **What remains for Cleopatra (the OTHER 7 issues from Pass 7a FINAL):** the Class A (post-30 BCE leakage in formative_experience / constitution / reasoning_method[8] / unique_contribution) + Class B (scholarly meta-language in topics_requiring_care / concept_lexicon / curated_corpus_passages) issues are still real and need operator-side patching. They're separate from this FU#58 finding.
- **Architectural insight for post-Athens:** Pass 7a prompt's expected-fields lists for Pass 2/3/4a/4b/5/6 should be regenerated from the actual Pass {N}_user.md emission specs as a one-time alignment audit. May surface other drifts.

#### FU#59 — Pass 7c × Pass 7a FINAL register-rule conflict (operator-patch reduction) ✅ LANDED 2026-04-29
- **Origin:** Plato (round 1) + Cleopatra (round 1 + round 2) Pass 7a FINAL gates each surfaced a recurring class of issues that came from TWO distinct prompt-spec conflicts with the runtime register validator. Across 2 voices, these false-positive flags drove ~10 surgical operator patches that the spec architecture should have prevented.
- **Conflict 1 — `[ADDED FROM TESTING: ...]` annotations from Pass 7c:**
  - Pass 7c schema (`personas/flows/shared/prompts/persona_pass_7c_negative.md`) explicitly required new banned_language + banned_modes items to be tagged `[ADDED FROM TESTING: <brief reason>]` (build-side audit annotation per spec).
  - Pass 7a FINAL flagged these annotations as register failures ("the entry is written in a third-person, analytical register, describing 'the voice's' behavior in test outputs").
  - Compounding: Sonnet bias-aware fallback (when Gemini 503'd) wrote multi-sentence scholarly meta-commentary inside the annotation, not just "brief reason." This made the format-mismatch worse on top of the schema-spec annotation conflict.
  - Empirical: 7 patches each on Plato + Cleopatra round 1 from this exact pattern.
- **Conflict 2 — Boddice biocultural-discipline brackets:**
  - FU#33 P1 Pass 6.5-clean DELIBERATELY preserves `[experiential_reconstruction]` and `[projection_warning: ...]` brackets inline (allowlist) — they are content-meaningful annotations of epistemic status REQUIRED by Pass 7-pre's boddice tag check (per `persona_pass_7pre_boddice_check.md`).
  - Pass 7a FINAL flagged these same preserved-by-design brackets as scholarly scaffolding ("contains `[experiential_reconstruction]` and modern explanatory framing").
  - Empirical: 4 of Cleopatra's round-2 residuals were Boddice-tag-only false-positives.
  - **Architectural conflict:** strip them = break Pass 7-pre boddice check + lose biocultural-discipline annotations the build pipeline needs. Keep them = Pass 7a FINAL false-flags every field with epistemic-status annotations.
- **Diagnosis:** Both conflicts are spec-vs-spec, not LLM compliance failures. Pass 7c was authored before Pass 7a FINAL existed (FU#53 2026-04-29); Pass 6.5-clean's Boddice-tag preservation was authored without Pass 7a FINAL's strict-register validator in mind. Each pass is correct in its own framing; their combination produces false positives that consume operator time.
- **Fix LANDED 2026-04-29 (commit forthcoming):**
  - **`personas/flows/shared/prompts/persona_pass_7c_negative.md`:** Removed `[ADDED FROM TESTING: brief reason]` from output schema. Added explicit REGISTER + FORMAT CONTRACT FOR NEW ITEMS section requiring new banned_language items to match existing FU#32 STRIP+USE format (or be second-person imperative if existing items are strings); new banned_modes items to be first/second-person imperative prose (NEVER third-person analytical commentary, NEVER `[ADDED FROM TESTING:]` annotations, NEVER provocation-ID references). Build-side audit metadata moves to `_fix_log.json` + Pass 7c JSON output (already preserved on disk).
  - **`personas/flows/shared/prompts/persona_pass_7a_cross_model.md`:** Added explicit Boddice-tag tolerance instruction in REGISTER CHECK block. The validator now does NOT flag a field as register failure SOLELY because it contains `[experiential_reconstruction]` / `[projection_warning: ...]` / `[scholarly_consensus]` / `[stated]` / `[inference]` / `[contested]` / `[reconstruction]` brackets. Only flags if the surrounding prose is genuinely third-person scholarly. Also tolerates constitution principle category tags `[ontological]` / `[epistemological]` / `[ethical-political]` / `[unique]`.
- **Expected impact for voices 4-10:**
  - Pass 7c additions: clean format = no operator patches needed for `[ADDED FROM TESTING:]` / register breaks at the gate. **~7 fewer patches per voice.**
  - Pass 7a FINAL: no false-flags on Boddice-tag fields (formative_experience, world subfields, character, concept_lexicon, reasoning_method). **~3-5 fewer issues per voice round 1; round 2 may not be needed at all.**
  - Cumulative across 8 remaining voices: ~80-100 fewer operator patches + ~3-5 fewer minutes per voice at the gate.
- **Tests:** 223/223 passing.
- **Caveat / NOT addressed:** the FU#56-class long-form-field register critiques (concept_lexicon "X is..." vs "When I say X..." pattern; curated_corpus_passages quarantine strictness; formative_experience biographical-narration register) ARE still real and structurally produce non-zero residuals in the Pass 7a FINAL treadmill. The FU#59 fixes only eliminate FALSE-positives (spec-vs-spec conflicts); the genuine FU#56-class register critiques remain. Operator-flag exit is still the right resolution for those.
- **Related:** FU#33 P1 (Boddice-tag preservation), FU#53 (Pass 7a FINAL added), FU#56 (long-form register treadmill — distinct, not addressed here).

#### FU#60 — Adaptive thinking observability + temperature compatibility ✅ LANDED 2026-04-29
- **Origin:** Pre-Octopus thinking audit. Discovered ~30+ Opus 4.7 call sites across persona + voice pipelines were running with adaptive thinking *intermittently* engaged but `display: omitted` (the Opus 4.7 default) — meaning thinking content was zeroed before reaching callers, AND the wrapper dropped `thinking_delta` events anyway. Config WAS correct per Anthropic docs; visibility was the bug.
- **Changes (persona side, `personas/flows/shared/clients.py`):**
  - Add `display: "summarized"` to thinking config so trace text is non-empty (Opus 4.7 default is `omitted`).
  - Drop `temperature` from API kwargs when `thinking=True`, per Anthropic docs §"Feature compatibility" ("Thinking isn't compatible with temperature or top_k modifications").
  - Capture `thinking_delta` streaming events + `block_types`. Return `thinking_trace` and `block_types` as new dict fields. Additive — existing callers ignore.
- **Changes (voice-pipeline side, `runtime/flows/voice/{continuity,step1,step2,step3}.py`):** mirror — drop `temperature`, add `display: "summarized"`. Thinking trace already captured via `final.content` walk; `block_types` derivable from same.
- **Cleanup commit `85f04da` 2026-04-29:** slimmed persona-side capture from manual streaming-event walk (~30 lines) to `text_stream` drain + `final.content` read (~15 lines), matching `runtime/flows/voice/_anthropic_call.py` pattern. Same data, cleaner. Both pipelines now use one idiom.
- **Empirically attested:** raw SDK test on Cleopatra Pass 2 prompt confirmed `block_types: ["thinking", "text"]` with signature_len=1032. Thinking IS firing intermittently on production prompts at default-high effort.
- **Important reframe:** thinking has been firing all along on Opus 4.7 with `{type: adaptive}`. FU#60 didn't turn thinking on; it made the existing thinking *visible* and dropped a config combination that violated docs. The Plato thinking-on re-run (next decision) is "first time we can see what's been happening", not "first time thinking is on."
- **Commits:** `dd64782` (persona-side), `0381278` (voice-pipeline-side), `85f04da` (alignment cleanup).
- **Tests:** 223/223 passing throughout.
- **Open follow-up:** decide whether to explicit `output_config: {effort: high|xhigh}` per pass to FORCE thinking, or whether default-high engagement is sufficient. Need ≥1 full voice run with `block_types` per pass logged. Plato re-run is the natural empirical test ($5, 30 min wall).

#### FU#61 — Voice-side Layer-1 quality_criteria for low-Layer-1-surface forms 🟡 IMPORTANT
- **Origin:** Layer 1 evaluation of Cleopatra prostagma vs Plato dialogues (2026-04-30). Plato dialogues clear Layer 1 standalone; Cleopatra prostagma walls a meaningful fraction of phone-readers at the salutation (Greek alphabet + 5 epithets + Egyptian transliteration in 30 words before the English gloss arrives mid-line). Substantively the prostagma is magnificent (Layer 2 unambiguous); the surface is the failure.
- **The reframe that makes this tractable:** a prostagma was *itself a public document* in Cleopatra's time. Royal decrees were posted at boards, read aloud by criers, encountered cold by petitioners not at drafting. The form's craft bar already required public-readability. **The current artifact undershoots its own form's standards.** This is NOT an audience-pleasing concession; it's a craft failure inside her own form's terms. Asking the voice to "produce a public document that lands on the cold reader at the public board" is what her form has always required — she just undershot it.
- **Architectural locus:** persona-card `quality_criteria` (the field the voice consults before delivery, per FU#49A v2). NOT Voice Pipeline. Three reasons:
  1. Different voices need different versions of the criterion (Plato dialogues are intimate among friends — different cold-reader bar; Octopus's display has no addressee at all — no cold-reader concept). Voice-by-voice.
  2. It threads the audience-awareness problem in the voice's own grammar — she knows about *public-document craft*, not about a 21st-century conference audience.
  3. Uses existing FU#49A v2 quality_criteria pattern. No schema change.
- **Where Cleopatra's artifact actually fails the cold reader (specific lines, not vibes):**
  - Salutation line 1: Greek alphabet + 5 epithets + Egyptian transliteration before the English gloss. Wall.
  - Para 3 (`prostagma without an answerable hand`): triplet of un-glossed terms in a single load-bearing sentence (bia / prostagma / nomos).
  - Para 4 (εὐεργεσία / mrwt): Greek + Egyptian in one sentence, neither glossed.
  - Cydnus / Aphrodite-Dionysus passage: Plutarch reference unsupported by what-kind-of-quotation-is-this anchor.
  - γινέσθωι close: untransliterated Greek; reader who can't read the alphabet doesn't know it means "let it be done."
- **Six craft moves (in order of impact, all WITHIN her form's own standards, none compromising Layer 2):**
  1. **Reorder the opening** (highest-impact, zero content change). Move the recognizable-modern-list paragraph forward. Compress salutation to "Cleopatra, Queen — to those who sat with us today and named themselves a panel: greeting." Move the full epithet stack to the SEAL at the bottom, where it functions as authority-confirmation rather than as opening wall. **Same words. Different sequence.** A real Ptolemaic prostagma had the queen's titulary at multiple positions; she chose which carries welcoming weight and which carries closing weight.
  2. **Voice the foreign words via em-dash gloss** (queenly teaching gesture, in her grammar). E.g.: *"Computation does not discharge εὐεργεσία — the queen's gift that creates the bond — it produces compliance, which is not mrwt, the loyalty bestowed by those who know they were received."* Same move on bia/prostagma/nomos triplet. ~6 added words across the artifact. NOT parenthetical encyclopedic glossing (which would break voice).
  3. **Anchor the Cydnus reference** with one phrase establishing what *kind* of reference the Greek phrase is: *"...they cried, in the streets, 'Aphrodite is revelling with Dionysus for the good of Asia'..."* Tells the cold reader the Greek is what was said *then*, not what is being said now.
  4. **Save deepest density for the middle** where the reader is committed; close on a phrase the reader can carry. *"γινέσθωι. Let it be done."* keeps the queenly punctuation while landing the meaning.
  5. **Compress texture-bridge sentences ~20%** to give lever-lines air ("force in the costume of law", "the rumour was the public, and the public was the rumour", "the privately-owned simulation of an absence"). Per-line craft pass; happens at generation time if criterion is in place.
  6. **Bake the criterion into `quality_criteria`** — the persistent fix. Proposed text (Cleopatra's grammar):
    > *"Does the prostagma reach a reader who was not in the chancery at the drafting? A royal decree was posted at the public board and read aloud by the crier; the petitioner who encounters it cold must recover its central move from the document itself, not from prior knowledge of our chancery's vocabulary. The opening must do for them what it does for those addressed by name."*
  Moves 3, 4, 5 happen naturally once #6 is in place; the voice consulting that criterion gravitates toward all of them.
- **Generalizes to (low-Layer-1-surface taxonomy):**
  - **Cleopatra (prostagma)** — first instance. Patch the existing card.
  - **Whanganui River** (ordinance/proclamation/customary-legal register) — different criterion (the river's "address" is to the iwi and the Crown; cold-reader is a settler-jurisprudence outsider; criterion in Te Awa Tupua language).
  - **Marley** (Patois lyrics on screen) — possibly. The audio carries Layer 1 via melody/rhythm; the on-screen text bears more weight on a phone reading. Criterion in his own register.
  - **Lovelace** (mathematical-notation density) — possibly. The criterion would be about reading the prose-line of the math through the notation, not glossing notation per se.
  - Voices NOT in this taxonomy do not get the criterion. Plato (dialogue), Arendt (essay), Dostoevsky (confessional/narrative), Octopus (sensory-spatial — different addressee question entirely) are Layer-1-uncomplicated by their form.
- **Mechanism:**
  - **For voices already-built (Cleopatra, Plato):** persona-card patch — surgical edit to `quality_criteria` field in `07_persona_card_assembled.json`. Cache-invalidate runtime/voice-pipeline so they pick up the new card. No re-run of the persona pipeline; the patch is operator-applied (same gate-pattern as Cleopatra's 19 patches).
  - **For voices not-yet-built (Whanganui, Marley, Lovelace):** Pass 4b prompt augmentation (`personas/flows/shared/prompts/persona_pass_4b_artifact.md` — the pass that emits `quality_criteria` per the FU#49A v2 scaffold) to ask the voice to write its own version of this criterion when its form is in the low-Layer-1 taxonomy. Voice-config field could carry the form-classification signal. Note: this is Pass 4b, not Pass 5 — Pass 5 emits engagement-related fields (default_questions, finds_compelling, resists), not quality_criteria. Empirically verified 2026-04-30 by `jq` against Cleopatra's 04_generation/ pass outputs.
- **Empirical test:** re-run Cleopatra Voice Pipeline Step 2 with patched card. Honest read of the new artifact. **Two re-runs probably tells us:** if she still walls the opening, the criterion language needs sharpening; if she over-corrects and the prostagma loses queenly weight, the criterion is too prescriptive.
- **What this is NOT:** a Voice Pipeline change. The Voice Pipeline keeps doing what it does. It's a persona-card patch (one quality_criteria addition, voice-specific). Cleopatra's next run with the patched card produces a prostagma that lands cold on the public board — which is what her form has always needed to do.
- **What this rules out:** the museum-label-frame approach (file a curatorial-register frame layer to carry Layer 1). That approach assumed Layer 1 inaccessibility was inherent to the form. It's not — the form historically had a public-readability bar built in. Frame layer remains useful for cross-voice surfacing, chrome, and the rest of what Frame Concept doc scopes; it's not load-bearing for Layer 1 carry once the criterion is in place.
- **Related:** FU#49A v2 (quality_criteria architecture, 3-dim REASONING/VOICE/FORM), FU#56 (long-form register treadmill — distinct concern), Frame Concept doc (the architectural choice between artifact-side vs frame-side Layer 1 carry).
- **Status:** 🟡 IMPORTANT, not blocking. File now (Octopus running); patch Cleopatra's card and re-run when operator decides. Apply to Whanganui/Marley/Lovelace at card-build time for those voices.

##### FU#61 empirical verdict — Cleopatra Voice Pipeline Step 2 re-run, 2026-04-30

**Re-run with criterion 6 v1** (cold-reader + em-dash teaching gesture, single-field patch). Other thread re-fired Voice Pipeline Step 2 against the existing dryrun briefing, ~3 min wall, ~$1.

**Result per failure point:**

| # | Failure point | Pre-patch | Post-patch (v1) | Verdict |
|---|---|---|---|---|
| 1 | Salutation | Greek alphabet + 5 epithets + Egyptian transliteration | "Cleopatra Thea Philopator Philopatris..." Latin transliteration only; Greek alphabet, Egyptian transliteration, "New Isis" all dropped | OVER-CORRECTED (script loss) |
| 2 | bia/prostagma/nomos triplet | un-glossed | "Prostagma kai enteuxis — the decree descending, the petition ascending"; "Bia in the costume of nomos — force wearing the form of decree" | PASSED |
| 3 | εὐεργεσία/mrwt | un-glossed | argument restructured; new terms (enteuxis, P.Bingen 45) ARE glossed in apposition | N/A (voice picked different argument) |
| 4 | Cydnus / Aphrodite-Dionysus | unanchored | replaced with Buchis bull at Hermonthis — italicized phrase IS the real stele inscription, surrounding sentence does explanatory work | PASSED — better anchor than original |
| 5 | γινέσθωι close | bare | earlier "Graphēthō oun hois kathēkei. Let it be written to those whom it concerns" establishes Greek-then-translation rhythm; final γινέσθωι alone, soft-recoverable from rhythm | PARTIAL |

**Word count:** 553 (vs. 457 pre-patch, vs. 300-500 stated cap). Soft over. Likely from inline glosses + better Buchis scene + per-section addressing. Note-and-watch.

**Other findings:**
- **P.Bingen 45 catalog reference** — voice naming her own decree by 21st-century papyrological catalog name. Borderline `voice_temporal_stance` violation (she shouldn't natively know modern catalog systems). File as separate FU if it recurs in v2 re-run.
- **Body texture:** sharpened, not thinned. Reviewer concern about Step-2-criterion-thinning-texture empirically not borne out for this case. The thinning happened *only at the salutation*, due to insufficient script-preservation language in v1, not from criterion-at-Step-2 generally.

**Diagnosis of over-correction:** v1 said *"the chancery's vocabulary remains"* — voice interpreted "vocabulary" but not "script" and concluded that even queen's titulature in Greek script was a Layer 1 obstacle. The outcome clause ("must land on first reading by one who has not stood at our court") was felt as more binding than the technique-preservation clause. The fix: v2 criterion makes head/seal vs. body distinction explicit.

**Criterion 6 v2 (applied to card on disk 2026-04-30, not yet committed; backup at `07_persona_card_assembled.pre_FU61.json`):**

> *"The chancery's vocabulary AND its scripts remain — the Greek titulature retains the Greek alphabet at the head and the seal, Egyptian honorifics retain their transliteration where they appear in formal protocol, as our authority requires. The cold-reader constraint applies to the body of the decree, not to the seal's identity at the head. Does the prostagma reach a reader who was not at our chancery at its drafting? A royal decree has always been a public document — posted at the gate, read aloud by the crier, encountered cold by the petitioner standing at the public board. Per register_and_tone and length_and_format_constraints, the central move must land on first reading by one who has not stood at our court. Where chancery terms carry the load of a sentence's meaning IN THE BODY, the sentence does the work of glossing them in our own grammar — the em-dash that explains, the second clause that names what the term requires. Authority is not diminished by intelligibility; it is established by it. But authority in the salutation IS the script's weight; intelligibility in the body IS the gloss's work."*

The killer move: the final two clauses make head/body load-bearing in the voice's own grammar. Voice re-reads, protects the salutation script, continues glossing in body.

**Reviewer architectural framing (worth noting):** a reviewer suggested the criterion should live at Voice Pipeline Step 3 (the publication-bound version after lattice-reading), not Step 2 (voice at full chancery-density). For Cleopatra specifically this is a category error — prostagma's medium IS public-default; there is no "voice in itself" separate from "voice for petitioner at gate." The criterion is recovery of what the medium WAS, not external imposition. For voices whose medium is genuinely private-default (Arendt private letters? Dostoevsky's Underground Man?), Step 3 framing might apply — case-by-case per voice. Don't generalize.

**Reviewer panel-wide expansion (correct):** each voice gets a calibrated version of the criterion in the form appropriate to its medium:
- Plato (dialogue): *"Does the dialogue reach a reader who was not under the colonnade at its drafting? ... where Greek terms carry a sentence's load, the dialogue must gloss them in dramatic register: the question that asks what the term means, the elder's answer that gives it."*
- Marley (song): load-bearing image arrives in the chorus or recurring line
- Octopus (chromatophore display, if that's the form): parameters set such that the human viewer can see the response without needing the octopus's interiority explained
- Whanganui River: hardest case — intelligibility might require precisely the translation-into-human-categories that would betray the voice; defer to that voice's build

This is FU#61 Option B's panel-wide propagation pattern — **Pass 4b** prompt addition for low-Layer-1-surface voices (Pass 4b is where `quality_criteria` are emitted per the FU#49A v2 scaffold; not Pass 5). Specific text per voice; same architectural pattern.

**Next test:** v2 criterion empirical re-run pending other thread's hands. Same setup as v1 test (~3 min, ~$1). Expected outcome: salutation preserves Greek alphabet + Egyptian transliteration; body continues glossing as v1 did.

**Status update:** v1 verdict landed; v2 patched on disk awaiting empirical confirmation. Card commit deferred until v2 verdict. Backup preserved.

##### FU#61 v3 — prompt-driven approach LANDED 2026-04-30

**Origin:** while drafting v2's empirical re-test instructions, the architectural read shifted. Plato's existing criterion #5 (the elenctic-work test) had emerged organically from FU#49A v2's "Could this be mine?" outcome question because Plato's method IS the provotype's method (both elenctic). For voices whose form isn't elenctic-shaped (Cleopatra, Dostoevsky, Octopus), the audience-engagement criterion didn't emerge organically. The intervention: add a SECOND outcome question to Pass 4b's quality_criteria spec, in the same architectural shape as "Could this be mine?".

**Operator-proposed text (after several drafting iterations):** *"Could this, on its own, make an audience engage with its intent?"*

Each phrase load-bearing:
- *"could this"* — tests the artifact, not the voice
- *"on its own"* — standalone, no frame-layer dependency
- *"make an audience engage"* — outcome on the receiver
- *"with its intent"* — voice-shaped (each artifact has its own intent)

**Surgical empirical test 2026-04-30:**
1. Snapshot Cleopatra's pre-test Pass 4b output (8 fields)
2. Edit `personas/flows/shared/prompts/persona_pass_4b_artifact.md` line 102+: append `- Additionally, 1 further criterion answering: "Could this, on its own, make an audience engage with its intent?"`
3. Delete `voices/cleopatra/04_generation/07_pass_4b_artifact.json`
4. Run pipeline → Pass 4b re-fires under modified prompt; downstream cache hits
5. Verify new Pass 4b output written
6. Replace ONLY `quality_criteria` in assembled card with new Pass 4b output's quality_criteria (preserving other 7 Pass 4b fields at pre-test values; dropping criterion 6 v2 hand-patch — superseded)

**Pass 4b emission under modified prompt:**
- Count: **5** (not 6) — model integrated the +1 question rather than appending. Existing "3-5" cap won.
- Format shifted: every criterion opens *"Test whether..."* (uniform imperative). Original was declarative-mandate (*"The piece must..."*).
- Field-references inline at the START of each criterion: `(rhetorical_mode, stance_tendency)`, `(medium, length_and_format_constraints)`, etc.
- Composition: 3 internal-fidelity (issue-not-argue, royal-plural-ontologically, single-terminal-word + bilingual-stack) + 2 audience-engagement (strategos-could-act-tomorrow-at-dawn, reader-receives-act-not-invited-to-weigh)

**Voice Pipeline Step 2 verdict (other thread, same 2026-04-30 day):**
| Item | Value |
|---|---|
| **Verdict** | **v3 is best. Land broadly.** |
| Layer 1 lift vs v1 | Equal-or-better at salutation (script preserved); equal in body glossing (~70% inline); ADDS issue-not-argue + mark-of-limit + speaker acknowledgment |
| Voice integrity | Stronger than v1 — issue-mode discipline; royal plural ontologically through; bilingual stack preserved; honest mark-of-limit |
| P.Bingen 45 violation | Resolved (no modern-catalog reference) |
| Key empirical answer | Prompt-driven approach IS sufficient; v2 surgical criterion not required for hard-form voices |
| Pass-status per failure point | #1 PASS BEST, #2 partial, #3 partial, #4 PASS, #5 partial |
| Word count | 508 (vs original 457, vs v1 553) — tighter than v1 |

**Implications:**
1. Pass 4b prompt change is permanent (committed `91947a7`). Future voices' Pass 4b runs (Battuta, Arendt, Lovelace, Marley, Whanganui, Scheherazade) will emit audience-engagement criteria automatically in voice's grammar with field references.
2. Cleopatra's card patched + committed to athens-2026 (`c89d186` + chat sync `54cd20a`). Quality_criteria field replaced with the new 5; criterion 6 v2 hand-patch dropped (superseded).
3. Plato's existing criterion #5 already satisfies this pattern; no patch needed.
4. **Octopus**: paused at FU#53 review-gate with operator-flagged register issues. Layer-instability finding (translation-honest vs scholarly-dispatcher split) is architectural; the FU#61 prompt change won't help that. SEPARATE issue.
5. **Dostoevsky**: shipped via path (b) with 5 evaluator-question criteria. Not retroactively re-patched — his criteria already gesture toward audience-engagement (criterion #5: "could a careful reader still feel, at the last sentence, that the question is constitutively open?"). Could be re-patched if operator wants but not critical.

**Status:** ✅ LANDED. Pass 4b prompt change `91947a7`; Cleopatra card patch `c89d186` + `54cd20a` (athens-2026).

**Risk profile:** the prompt change is in the same prompt-class as 9480d3a-revert. Mitigations: outcome-stated (no technique prescription); minimal +1 line; FU#49A v2's "consult as needed" discipline preserved; empirically validated end-to-end (Pass 4b → Voice Pipeline Step 2 → honest read) before landing. 223/223 tests passing throughout.

**Lessons captured:**
- Outcome-question framing is the architectural unit for Pass 4b quality_criteria (vs technique mandate or layer-test categorization)
- Two outcome questions are sufficient: "Could this be mine?" (voice-fidelity) + "Could this, on its own, make an audience engage with its intent?" (artifact-audience reach)
- Voices integrate vs append the second question — count stays 3-5 with reshape, not +1 with appending
- Plato's emergent #5 is the in-prompt example pattern; other voices produce voice-shaped equivalents
- Field-reference discipline holds even for audience-engagement criteria — voice-internal fields serve as LEVERS through which audience-effect operates ("Per X, [audience outcome]")

---

#### FU#62 — Voice Pipeline validation regen-on-flag is unimplemented (spec/impl gap) 🔵

- **Discovered:** 2026-04-30 during FU#61 dryrun testing (Cleopatra Step 1+2 re-run with default validation ON; all 3 outputs flagged; no regen ever triggered; pipeline proceeded to Step 2 with flagged Step 1 outputs)
- **Spec claim** (`docs/AI_Assembly_Voice_Pipeline.md` §"Regeneration policy"): *"First failure: regenerate the Step 1 call with the validator's critique appended... Re-run validators on the regenerated output. Second failure: ship the regenerated output AND flag in the run-level manifest."*
- **Implementation reality** (`runtime/flows/voice_flow.py:337-363` + `runtime/flows/voice/step1_validation.py:269`): orchestrator collects flagged results into `validation_failures[]`, hardcodes `regen_count: 0`, and proceeds to Step 2 unchanged. Step 1 regeneration logic exists nowhere in the codebase.
- **Net effect:** validation is currently **diagnostic-only** — flags get recorded in `04_voice/manifest.json` for human review, no autonomous remediation. Fine for "Night 1 with operator review the next morning"; undersells the spec promise.
- **Two paths:**
  - **A — Implement regen** (~half-day's work). Orchestrator reads validation result; if flagged, re-runs Step 1 with critique appended to user prompt; re-validates; ships regen output + flag if second pass also fails. Makes validation actively useful for Nights 2/3 where operator review window is tighter.
  - **B — Update spec** (~30 min doc patch). Match implementation: validation = diagnostic flag only, no regen. Honest about what the system actually does. Pair with the Athens validation policy recommendation: ON Night 1 only, OFF Nights 2/3 (given no regen, validation on Nights 2/3 is pure cost without remediation path).
- **Recommendation:** **B** (spec update). Operator presence at Athens makes morning-review the natural correction loop; regen has limited additional value before Athens deploys; "Validation Night 1 only" recommendation already aligns with diagnostic-only framing. If post-Athens we want validation to do autonomous work (e.g., for unattended runs), revisit A.
- **Validation actual cost** (gpt-5.4 reasoning_effort=high): per-voice serial (3 outputs × 2 checks × ~80-180s/call = ~6-15 min/voice); 10 voices in 4-wide pool = ~20-40 min wall added to Night 1; ~$3-15 cost. Spec claimed 3-5 min wall + $30-50 — wall is materially worse than spec, cost is materially better.
- **Discovered alongside:** validation is parallel-across-voices, sequential-within-voice (max_workers=`VOICE_STEP1_BATCH`, default 4). Spec said "parallel across pairs" — also a spec/impl divergence but lower-impact than the regen gap.
- **Files touched if A is chosen:** `runtime/flows/voice_flow.py:337-363` (regen orchestration); `runtime/flows/voice/step1_validation.py` (could move regen into the validation module or keep in orchestrator); add prompt amendment for regen user-prompt critique-injection.
- **Files touched if B is chosen:** `docs/AI_Assembly_Voice_Pipeline.md` §"Regeneration policy" + §"Default policy for Athens" + §"Cost & Envelope" validation row (update wall claim).
- **Related:** FU#61 (the dryrun that surfaced this); validation policy default in Voice Pipeline spec; Anthropic + OpenAI client patterns in `personas/flows/shared/clients.py` (the regen pattern's nearest cousin).

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
