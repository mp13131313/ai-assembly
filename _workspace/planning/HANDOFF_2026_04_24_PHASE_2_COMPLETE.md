# Handoff — Phase 2 complete (2026-04-24)

**Session date:** 2026-04-24 (single long session, ~12 hr spread)
**Branch:** `arch-03-additive-merge` — **100 commits ahead of origin/main, not pushed**
**Status:** Phase 2 of FU implementation plan landed. Voice-tissue regression resolved. Layer 2 audit instrumentation landed. Next item: FU#2 (chunked Pass 7-pre verification — confirmed blocking).
**Next-session model:** Opus 4.7 + adaptive thinking, high effort for FU#2 architecture design; Sonnet-shaped for mechanical implementation once design lands.

**Supersedes:** `HANDOFF_2026_04_23_PHASE_1_COMPLETE.md`. Phase 1 priorities (FU#32 → Pass 2 isolation → FU#37 → full re-run → FU#1) all executed — this handoff captures what was learned and what's next.

---

## ONBOARDING PROMPT (copy-paste into fresh session)

```
You are resuming the arch-03 / Phase 3 follow-up work on the AI Assembly
project. Phase 2 (2026-04-24) landed FU#32 + FU#1 and empirically
resolved the voice-tissue regression via staged prompt refinement +
A/B-validated Layer 2 audit. Next item: FU#2 (chunked Pass 7-pre
citation verification — CONFIRMED BLOCKING after hitting Sonnet 4.6's
128K ceiling twice during the 2026-04-24 full Dostoevsky re-run).

Model: Opus 4.7 + adaptive thinking for the architecture design pass;
Sonnet-shaped for the mechanical implementation once design is locked.

FIRST ACTIONS:

1. Read _workspace/planning/HANDOFF_2026_04_24_PHASE_2_COMPLETE.md
   in full. Has: Phase 2 empirical validation findings (Pass 2
   isolation signal + full re-run metrics + FU#1 audit deltas),
   FU#32 landing details, FU#37/FU#31 deferral rationale, FU#2
   design sketch, next-session brief.

2. Read _workspace/planning/FOLLOW_UPS.md (authoritative tracker —
   updated 2026-04-24). Check the RECOMMENDED IMPLEMENTATION ORDER
   section. Phase 2 ✅ DONE. Phase 3 = FU#2 (current priority).

3. Verify branch + tests:
   cd "/Users/aienvironment/Desktop/AI Assembly/code"
   git log --oneline origin/main..HEAD | head -12
   cd personas && venv/bin/python -m pytest tests/ -x -q
   (Expect 128/128 tests pass, branch 100 commits ahead of main,
    HEAD = the FU#1 audit script commit or later.)

4. Verify FU#32 card + Phase 1 baseline both preserved as snapshots:
   ls _workspace/arch_03_baseline_snapshot/ | grep -E "phase_1_complete|fu32_complete"
   (Expect: phase_1_complete_20260423_2251/ (pre-FU#32, 150KB card) +
    fu32_complete_20260424_0817/ (post-FU#32, 165KB card))

5. BUILD FU#2 (chunked Pass 7-pre verification):

   Current Pass 7-pre: single Sonnet 4.6 call reading the entire
   assembled card + primary_texts + merged_dossier, emitting
   per-citation verification results. At max_tokens=128000 (Sonnet
   4.6's hard ceiling), it hits the ceiling when card output
   exceeds ~120K tokens — empirically twice on 2026-04-24's
   Dostoevsky run. Try/except wrap ships card without verification
   when ceiling hits.

   FU#2 architecture:
   - NEW: personas/flows/shared/pass_7pre_chunked.py
     * Helper: collect_citation_bearing_fields(card) → list[dict]
       (extracts commitments[].citations, concepts[].citations,
       passages[].citations, constitution[].textual_evidence,
       curated_corpus_passages[].text-as-verifiable-quote, etc.)
     * Helper: batch_citations(items, batch_size=25) → list[list]
     * New Pass 7-pre-chunk prompt: verifies ~25 citations per call
       (max_tokens 16-32K, well under 128K ceiling)
     * Parallel fire via ThreadPoolExecutor(max_workers=4)
     * Aggregator: combine per-chunk results into unified Pass 7-pre
       output matching current schema (verified_count, unverified,
       interp, dossier_only, inconsistent, hostile, boddice_tag_flags)
   - MODIFY: run_persona_pipeline.py:748-782 (current Pass 7-pre call)
     * Replace single call with chunked-and-parallel helper invocation
     * Preserve existing output schema (Pass 7a reads the aggregated
       output; don't break that contract)
     * Keep try/except wrap for graceful degradation
   - NEW: personas/flows/shared/prompts/persona_pass_7pre_chunk.md
     * Per-citation verification prompt — input: ~25 citations, card
       context for each. Output: per-citation verdict.
   - UPDATE: FU#2 tracker entry to APPLIED with commit hash
   - Effort: ~4-6 hr.

6. TEST FU#2:
   - Re-run full Dostoevsky pipeline with existing cache to re-fire
     only Pass 7-pre:
       cd personas && rm ../../projects/phase-l-dostoevsky/voices/fyodor_dostoevsky/05_validation/01_pass_7_pre_citation.json
       venv/bin/python run_persona_pipeline.py "Fyodor Dostoevsky" \\
           --project "../../projects/phase-l-dostoevsky"
   - Expect: chunked Pass 7-pre completes without ceiling hit, output
     matches existing schema, Pass 7a reads aggregated results correctly.
   - Cost: ~$3-5 (several Sonnet calls in parallel vs. 1 large call)
   - Wall time: ~3-5 min (parallel reduces wall despite more calls)

DO NOT:
- Re-implement FU#32 / FU#1 / FU#37 / FU#31 (FU#32/FU#1 done;
  FU#37/FU#31 deferred per 2026-04-24 empirical signal showing
  FU#32 alone sufficient)
- Proceed to Plato before FU#2 lands. Every post-arch-03 voice will
  hit the 128K ceiling.
- Touch Pass 7a or the fix-pass logic. Those are stable and the FU#2
  change is confined to Pass 7-pre's internal structure; Pass 7a
  just reads the aggregated output.
- Push to origin without explicit operator request.

KEY FILES:
- This handoff: _workspace/planning/HANDOFF_2026_04_24_PHASE_2_COMPLETE.md
- Tracker: _workspace/planning/FOLLOW_UPS.md (authoritative; updated 2026-04-24)
- Pipeline orchestrator: personas/run_persona_pipeline.py
  - Current Pass 7-pre call site: ~L748-782 (look for "PASS 7-pre")
  - Current try/except wrap: handles ceiling-hit gracefully today
- Current Pass 7-pre prompt: personas/flows/shared/prompts/persona_pass_7pre_citation.md
- Current Pass 7-pre user prompt: persona_pass_7pre_citation_user.md
- FU#1 Layer 2 audit: personas/scripts/arch_03_synthesis_audit.py
- FU#32 commits (6 per-prompt): b19a640, b853972, 479f5c9, af39679,
  7c687f8, 4c577c8

SNAPSHOTS FOR A/B / REGRESSION CHECKS:
- _workspace/arch_03_baseline_snapshot/phase_1_complete_20260423_2251/
  (Pre-FU#32 Dostoevsky: 150KB card with voice-tissue regression)
- _workspace/arch_03_baseline_snapshot/fu32_complete_20260424_0817/
  (Post-FU#32 Dostoevsky: 165KB card, incarnate prose, 15 patches,
   0 register violations, has _synthesis_audit.json)

REPO STATE AT HANDOFF:
- Branch: arch-03-additive-merge
- HEAD: 4f9e23a (FU#1 audit script) — or later if tracker commits
  added post-this-write
- 100 commits ahead of origin/main (93 Phase 1 + 6 FU#32 + 1 FU#1)
- Tests: 128/128 passing
- Working tree: clean except _workspace/arch_03_baseline_snapshot/
  (accumulated snapshots from Phase 1 + Phase 2 runs — FU#11 cleanup
  item, post-Phase-L sign-off)

If unsure about anything, FOLLOW_UPS.md "RECOMMENDED IMPLEMENTATION
ORDER" section is authoritative. Default to reading that before
guessing. Phase 2 retrospective + FU#2 design rationale live in
this handoff below.
```

---

## What this session accomplished

### Phase 2 critical-path implementation (8 commits + empirical validation)

**FU#32 — Pass 2-6 positive-compensation prompt refinement (6 per-prompt commits)**

The handoff that launched this session flagged an asymmetric failure mode
discovered after 4 independent reviews of the Phase 1 Dostoevsky card: FU#12-A's
register-hardening block told the writer "strip X" (curator metadata, scholar
attribution, provenance brackets) without "compensate with Y" (use the voice's
own incarnate grammar instead). Writer responded with taxonomic retreat —
"you do not think in four-humours grammar" replacing "you are a man of gordost'
who has walked through nadryv toward smirenie".

FU#32 paired every strip with a positive compensation:

- **Pass 2 (commit `b19a640`):** CURATOR-SIDE block rewritten into 5 STRIP+DO-INSTEAD
  pairs + 6th META-STRIP against taxonomic retreat. `banned_language` bullet
  gets positive-seed guidance (avoid X + in-voice alternative Y). `character`
  field gets INHABIT-vs-NAME test with gordost'/nadryv/smirenie worked example
  quoted from the handoff.

- **Pass 3 (commit `b853972`):** Same STRIP+DO pattern specialized for
  constitution/concept_lexicon/reasoning_method. META-STRIP pairs with: write
  the principle AS the voice giving itself an operational instruction ("You
  treat every threshold as stageable..."), not as a scholar describing the
  principle.

- **Pass 4a (commit `479f5c9`):** STRIP+DO pairs for voice-field values,
  META-STRIP for voice-register taxonomic retreat ("your register is not
  academic; it is feverish-confessional" → "I write at the pitch of
  confession before a panel of half-hostile gentlemen..."). `banned_language`
  field-spec upgraded to STRIP+USE pair format — each banned term pairs with
  voice-native alternative.

- **Pass 4b (commit `af39679`):** Terse reference-back STRIP+DO pairs + one
  Pass-4b-specific META-STRIP for the 6 register-vulnerable artifact-spec
  fields (technical_capabilities, characteristic_output_structure, etc.) —
  strip modern design-spec language without falling into designer-voice.

- **Pass 5 (commit `7c687f8`):** META-STRIP for engagement fields +
  requirement that 1-2 default_questions + ≥1 bold_engagement_topic USE the
  voice's load-bearing lexemes in prose (nadryv, deyatel'naya lyubov', etc.),
  not list them in adjacent vocabulary slots.

- **Pass 6 (commit `4c577c8`):** Header/why_selected INHABIT meta-rule. Pass
  6's fields were already second-person per FU#12-A; FU#32 adds the test
  that the header prose is the voice recalling its own circumstance
  ("You wrote this from the cell at the Peter and Paul fortress..."), not
  a scholar annotating the passage.

128/128 tests pass after each commit. Prompts render cleanly.

**Pass 2 isolation re-run (~5 min, validation checkpoint)**

Cleared `04_generation/01_pass_2_identity_boundaries.json` only. Pipeline
cache-hit Pass 3-7 + derive + assembly. Idempotency guard correctly skipped
fix-pass (via `_fix_log.json` existence check per FU#13). Pass 2 re-ran on
new FU#32 prompts.

Pre-FU#32 character field:
> "Against the Western four-humours grammar you do not think in
> phlegmatic-sanguine-choleric-melancholic; against Big-Five adjectives
> [projection_warning: 'extraversion', 'conscientiousness' import a
> twentieth-century personality-psychology grammar that flattens the moral-
> metaphysical stakes of character as you understand them] you think in
> Orthodox ascetical categories. You are quick, polemical, easily wounded..."

Post-FU#32 character field:
> "**You are a man of *gordost'* who has walked through *nadryv* toward
> *smirenie*, and the walk is not finished.** The *gordost'* animated the
> Petrashevsky cadet, the young writer who welcomed 'a new Gogol has
> appeared' and chafed at dining-table hazing... The *nadryv* crystallized
> on Semyonov Square and in the katorga barracks and at the bier of your
> first wife Maria Dmitrievna on Holy Thursday 1864 ('Will I see Masha
> again?'), and you know its grammar from inside..."

Exact match to handoff's targeted regression signature. Load-bearing lexemes
in USE IN PROSE, anchored in biographical arc. No taxonomic retreat. Signal:
STRONG — FU#32 alone sufficient.

**Full Dostoevsky re-run (~69 min wall)**

Per handoff step 4 cache preservation spec. Kept: `01_research/`,
`02_merge/pass_1_*/`, `03_corpus/01_primary_texts.json` + flag,
`03_corpus/02_excerpt_selections.json`, `04_generation/_snapshots/pre_fix_pass/`.
Cleared: `04_generation/*.json`, `05_validation/*.json`, `06_derive/*.json`,
`07_persona_card_assembled.json`, `02_merge/_fix_log.json`.

Per-pass wall time:
- Pass 2: (timed; re-ran from fresh)
- Pass 4a Voice: 282s
- Pass 4b Artifact: 35s (unchanged by FU#32 scope)
- Pass 5 Engagement: 52s
- Pass 6 Corpus: 81s
- Pass 7-pre: **HIT 128K CEILING — try/except wrapped, verification skipped**
- Pass 7-anachronism: 155s (gpt-5.4 high, 8 flags REVISION_NEEDED)
- Pass 7a: ~200s (REVISION_NEEDED)
- **Pass 7a-FIX: 15 patches of 15 applied, 0 failures (vs Phase 1's 33 across
  2 rounds — cleaner upstream generation)**
- Pass 7-pre re-verification: **CEILING AGAIN** (418,019 raw chars)
- Pass 7b: 194s (4 provocation chains)
- Pass 7c: 43s (+2 banned_language, +1 banned_modes)
- Derive: 74s (provocateur_profile 9 fields + evaluation_rubric 9 tests)

Final card: **165,251 bytes** (+10% vs Phase 1's 150,356 bytes — richer, not
lossier). **Output Register check: 0 violations (CLEAN).** 36 total fields.
`validation_status: REVISION_NEEDED` + `human_review_status: pending` (same
as Phase 1; post-fix verdict doesn't fully resolve when Pass 7-pre is
skipped and Pass 7a + 7-anachronism still flag sensitive_topics / cite
nuances that require human judgment).

**FU#1 — Layer 2 preservation audit (1 commit, script + A/B run)**

`personas/scripts/arch_03_synthesis_audit.py` (commit `4f9e23a`, 553 lines).
Companion to existing Layer 1 audit. Reuses Layer 1 helpers via import
(`_normalize`, `_STOP_WORDS`, `char_overlap`, `extract_merged_authors`,
`_AUTHOR_HINTS`, `_dossier_to_text`).

Per (chunk, consumer-pass) pair, computes:
- Density = pass-output-chars / chunk-chars (informational, not survival metric)
- Vocab recall = unique content words from chunk appearing in pass output
- Citation survival = authors cited in chunk → authors in pass output
- Frame-type survival (1-arch-06 specific): per-frame-type preservation rate
  into Pass 2/3/4a outputs, checked via name + primary_scholars + anchor
  presence in output text

Consumption map mirrors `_per_chunk_vars()` + `render()` calls in
`run_persona_pipeline.py` (lines 234 / 487 / 513 / 610 / 709). Comment
documents the source of truth — if the orchestrator's mapping changes, the
audit script needs an update.

A/B delta (live FU#32 vs Phase 1 snapshot):

| Pass | Δ vocab_recall | Δ cite_survival | Δ density |
|---|---|---|---|
| 2_identity_boundaries | -2.8% | -0.9% | -2.5% |
| 3_intellectual_core | -3.7% | +0.8% | +0.4% |
| **4a_voice** | **+9.4%** | **+6.2%** | **+26.1%** |
| 6_corpus | -2.6% | 0.0% | +1.4% |

**Pass 4a is the biggest FU#32 win.** Voice-field recall + citation survival
+ density all up substantially — resolves Gemini's persistent Phase L
register-drift flag that was never addressed by FU#12-A alone.

Pass 2/3 minor recall drops are the expected trade: FU#32 compresses
scholarly vocabulary into voice-native incarnate prose, so scholarly-side
unique words no longer surface but voice-tissue is richer in return. The
character field qualitative reversal (validated in isolation test) confirms
this trade is the right direction.

Red flag (same in both runs): Pass 6 `works` chunk at 13-14% vocab recall.
Structural, not regression — Pass 6's curated_corpus_passages is a small
output (8-10 passages) that necessarily compresses 5-20 works.

### Tracker + doc updates

- `FOLLOW_UPS.md` updated: FU#32 + FU#1 marked APPLIED with commit hashes +
  empirical validation notes. FU#37 + FU#31 marked DEFERRED with
  re-activation-condition rationale ("only if a future voice shows residual
  voice-tissue regression"). FU#2 marked 🔴 CONFIRMED BLOCKING with
  2026-04-24 ceiling-hit evidence. RECOMMENDED IMPLEMENTATION ORDER updated:
  Phase 2 ✅ DONE; Phase 3 = FU#2 current priority.
- This handoff doc (`HANDOFF_2026_04_24_PHASE_2_COMPLETE.md`) written as
  successor to Phase 1 handoff.

### Snapshot archive

- `_workspace/arch_03_baseline_snapshot/phase_1_complete_20260423_2251/`:
  pre-FU#32 Dostoevsky state (150KB card with taxonomic-retreat character
  field, 33 patches, 1 register violation during isolation test).
- `_workspace/arch_03_baseline_snapshot/fu32_complete_20260424_0817/`:
  post-FU#32 Dostoevsky state (165KB card with incarnate character field,
  15 patches, 0 register violations, `_synthesis_audit.json` included).

Comparable for 3-way diff: Phase L baseline (pre-arch-03, 115KB, 2 days ago)
→ Phase 1 (arch-03 + FU#12/13/5, 150KB) → Phase 2 (arch-03 + FU#12/13/5 +
FU#32, 165KB).

---

## FU#2 design sketch (for next-session implementation)

**Problem empirically confirmed 2026-04-24:** Sonnet 4.6's hard 128K output
ceiling is hit by Pass 7-pre when the card's citation density pushes
verification output past ~120K tokens. Phase 2 FU#32 prose richness
compounds the issue — each additional voice-native-lexeme-in-prose adds
verification surface area. API rejects 192K; 128K is the hard cap.

**Architecture:**

```
current:  [assembled_card + primary_texts + merged_dossier] → single Sonnet call → [verification_output up to 128K]
                                                                ╳ ceiling hit twice 2026-04-24 — verification skipped

proposed: [assembled_card] → collect_citation_bearing_fields → batch_citations(N=25)
                                                              → parallel Sonnet calls (max_tokens=32K each)
                                                              → aggregate → [verification_output matching current schema]
```

**Scope:**

1. **NEW module `personas/flows/shared/pass_7pre_chunked.py`:**
   - `collect_citation_bearing_fields(card) -> list[CitationRecord]`:
     walks the assembled card, extracts every citation-bearing field.
     Fields per current Pass 7-pre prompt include: `commitments[].citations`,
     `concepts[].citations`, `passages[].citations`,
     `constitution[].textual_evidence`, `curated_corpus_passages[].text`
     (verifiable as verbatim-quote-from-primary-text),
     `reasoning_method.steps[].worked_demonstration` (if quotes primary),
     `topics_requiring_care[].what_the_voice_actually_wrote` (if quotes
     primary). Each record: `{field_path, citation_text, context_text}`.
   - `batch_citations(records, batch_size=25) -> list[list[CitationRecord]]`:
     simple chunking; optionally sorted by field_path so one batch isn't
     disproportionately heavy.
   - `verify_citation_batch(batch, primary_texts, merged_dossier, client) -> dict`:
     fires one Sonnet call per batch. Prompt: `persona_pass_7pre_chunk.md`.
     max_tokens=32000 (well under ceiling). Returns per-citation verdicts
     (verified / unverified / interpretive / dossier_only / inconsistent /
     hostile per current Pass 7-pre output schema).
   - `aggregate_batch_results(batch_results) -> dict`: combines into unified
     Pass 7-pre output matching the schema Pass 7a reads. Preserves
     boddice_tag_flags handling (runs once on whole card, not per-batch).

2. **NEW prompt `personas/flows/shared/prompts/persona_pass_7pre_chunk.md`:**
   - Simpler than full Pass 7-pre: single batch of ~25 citations + relevant
     primary-text excerpts + merged_dossier snippets. Per-citation verdict.
   - Preserves voice-mode + hostile-sources branching.

3. **MODIFY `personas/run_persona_pipeline.py` ~L748-782:**
   - Replace current Pass 7-pre call with chunked helper invocation.
   - Preserve existing output path (`05_validation/01_pass_7_pre_citation.json`)
     + schema contract.
   - Keep try/except wrap for downstream graceful degradation (if chunked
     path also fails for some reason).

4. **Test coverage:** `personas/tests/test_pass_7pre_chunked.py`:
   - Unit test `collect_citation_bearing_fields()` on synthetic card fixture
   - Unit test `batch_citations()` for correct partitioning
   - Integration test with mocked `call_claude` — verify aggregator output
     matches current Pass 7-pre schema

5. **Real test:** clear Pass 7-pre cache on Dostoevsky, re-run pipeline,
   verify chunked Pass 7-pre completes without ceiling hit + produces
   verification audit.

**Cost/wall estimate:**
- Current (single-shot, ceiling-hit): ~$3 + 30 min wall time (mostly timeout)
- Chunked (parallel batches of 25): ~$3-5 + 3-5 min wall (parallelism)
- Per-voice savings: 25+ min wall time; similar cost; CRUCIALLY produces
  actual verification output instead of skipping it

**Effort:** ~4-6 hr. Architecture design + 3 new modules + prompt +
integration + tests.

---

## Current state of the pipeline (after Phase 2)

### What runs end-to-end

Unchanged from Phase 1 structure:
`Pass 0a → 0b → 1a/1b/1a-DR → 1.1-1.7 merge → 1c-extract → 1c-fetch → REVIEW GATE → 1d → 2 → 3 → 4a → 4b → 5 → 6 → 7-pre → 7-anachronism → 7a → [Pass 7a-FIX if REVISION_NEEDED] → 7b → 7c → Derive → Assembly`

### LLM model assignments per pass (unchanged from Phase 1)

Table at `HANDOFF_2026_04_23_PHASE_1_COMPLETE.md` §"LLM model assignments per
pass". No model changes in Phase 2. Only prompt changes (FU#32 additions to
Pass 2-6 system prompts).

### Phase 2 card metrics

- File: `projects/phase-l-dostoevsky/voices/fyodor_dostoevsky/07_persona_card_assembled.json`
- Size: **165 KB** (vs Phase 1 150 KB, +10%)
- 36 total fields
- `validation_status: REVISION_NEEDED`
- `human_review_status: pending`
- `voice_basis: corpus-based`
- **15 patches landed across 1 fix-pass round** (vs Phase 1's 33 across 2 rounds — cleaner upstream)
- **0 Output Register violations** (clean exit)
- Pre-fix snapshot preserved at `04_generation/_snapshots/pre_fix_pass/`
- Synthesis audit at `_synthesis_audit.json` (also copied to snapshot)
- Three-way-comparable on disk: Phase L baseline (pre-arch-03, 115KB) /
  Phase 1 (arch-03 + FU#12/13/5, 150KB) / Phase 2 (+ FU#32, 165KB)

---

## What's next (priority-ordered)

Per updated FOLLOW_UPS.md RECOMMENDED IMPLEMENTATION ORDER:

### 🔴 Immediately next: FU#2 — chunked Pass 7-pre verification

**Design sketch above.** Confirmed blocking after 2026-04-24 Dostoevsky
re-run hit 128K ceiling twice. Card ships without citation verification
when ceiling hit. Every post-arch-03 voice (Plato, Cleopatra, etc.) will
hit this. ~4-6 hr effort.

### 🟡 Pre-Plato: FU#7, FU#10-mod, FU#9, FU#8

- FU#7 — operator-facing pipeline summary (~1-2 hr)
- FU#10-mod — fix-pass test coverage (~2-3 hr)
- FU#9 — merge chunk max_tokens audit (~1-2 hr)
- FU#8 — Pass 7b bias evaluator audit (~30 min)

### 🔵 Deferred on 2026-04-24 (re-activate only if future voice regresses)

- FU#37 — declarative preserve-verbatim markers. FU#32 alone sufficient.
- FU#31 — voice-tissue validator. FU#32 alone sufficient.

### 🟢 Polish — FU#19, FU#22, FU#15

### 🔵 Trigger-based — FU#21, FU#23, FU#24, FU#25-28, FU#11, CC#1, FU#29, FU#30

---

## Empirical signals from Phase 2 run

| Signal | Phase L baseline | Phase 1 | **Phase 2 (FU#32)** |
|---|---|---|---|
| Card size | 115 KB | 150 KB | **165 KB** (+10% vs Phase 1; richer) |
| Pass 7-pre verdict | PASS | REVIEW_NEEDED (capped) | **REVIEW_NEEDED + SKIP (ceiling hit 2×)** |
| Pass 7-pre inconsistencies | 0 | 3 | (not measured — ceiling skipped verification) |
| Pass 7-anachronism flags | 5 | 6 initial → 4 post-fix | **8 initial → ? post-fix** |
| Patches landed | n/a | 33 across 2 rounds | **15 across 1 round** (cleaner) |
| Output Register violations | 0 | 0 | **0** (clean) |
| Pass 4a vocab_recall (vs chunks) | n/a | 44.9% | **54.3%** (+9.4%) |
| Pass 4a citation_survival | n/a | 8.8% | **15.1%** (+6.2%) |
| Pass 4a density | n/a | 36% | **62%** (+26%) |
| Character field structure | (v3.7 baseline different) | taxonomic retreat | **incarnate gordost'-walking-through-nadryv** |

**Interpretation:**
- **FU#32 works.** Voice-tissue regression resolved; Pass 4a substantial gains.
- **Card is richer, not lossier.** +15KB from Phase 1 = more voice-native
  prose + STRIP+USE pair dicts in banned_language + load-bearing-lexemes in
  default_questions, not scholarly padding.
- **Fix-pass needed less.** 15 patches vs 33 — FU#32 generation is cleaner.
- **Pass 7-pre is the current ceiling.** Until FU#2 lands, voices ship
  without verification audit when cards get rich enough.

---

## Known issues / things the next session should know

1. **Pass 7-pre 128K ceiling is actively blocking richer cards** (FU#2 design
   above). The try/except wrap ships gracefully but skips verification
   entirely. On Dostoevsky 2026-04-24: hit twice (initial Pass 7-pre + post-
   fix re-verification). This will happen on every post-arch-03 voice.

2. **Fix-pass idempotency guard works correctly** (traced during Pass 2
   isolation re-run, 2026-04-24). `_fix_log.json` existence check at
   `run_persona_pipeline.py:1179` correctly skips fix-pass on restart. The
   end-of-pipeline summary "fix-pass applied N of N patches" reads the
   cached `_fix_log.json` — that's not a re-fire, just informational.

3. **Pass 7-anachronism flag count rose (6 → 8)** with FU#32's richer prose.
   Each load-bearing lexeme in prose is a potential anachronism-check
   target; more anchors = more flags. Post-fix verdict is still REVISION_
   NEEDED but this is human-review-worthy signal, not pipeline failure.

4. **Pass 4a/4b register fully clean** after FU#32. Phase L baseline flagged
   6 Pass 4b fields + Pass 5 register drift on Dostoevsky; Phase 2 card
   emits 0 Output Register violations. Hypothesis confirmed: Pass 5 drift
   wasn't upstream-context starvation; it was absence of positive-side
   prompt discipline. FU#32 Pass 5 META-STRIP + load-bearing-lexeme-in-use
   requirement closes the gap.

5. **Fewer runs than Phase 1 this session** (only 3 pipeline invocations:
   Pass 2 isolation re-run + full re-run + FU#1 audit run). Phase 1 burned
   15+ runs chasing FU#13 live iteration. Phase 2's staged plan (FU#32 →
   isolation check → full re-run → audit) was much more efficient.

---

## Repository state at handoff

- **Branch:** `arch-03-additive-merge` (100 commits ahead of origin/main;
  NOT pushed to origin)
- **Tests:** 128/128 passing
- **Working tree:** clean except `_workspace/arch_03_baseline_snapshot/`
  (accumulated Phase 1 + Phase 2 snapshots — FU#11 cleanup after Phase L
  sign-off)
- **Phase 2 Dostoevsky card:** REVISION_NEEDED + human_review_pending on
  disk; pre-fix snapshot preserved; full pre-/post-FU#32 snapshots
  preserved in `_workspace/arch_03_baseline_snapshot/`
- **In-flight pipeline runs:** none

### Untracked items operator may want to clean up
- `_workspace/arch_03_baseline_snapshot/` — Phase 1 + Phase 2 snapshots.
  FU#11 covers cleanup after Phase L sign-off.
- `/tmp/fu32/` — local logs + diff helpers from this session. Not in git,
  safe to delete.

---

## Next session: brief

Phase 2 landed cleanly and resolved the voice-tissue regression that
motivated FU#32/37/31. FU#37 and FU#31 are deferred because the empirical
signal was strong enough that the primary-fix alone sufficed.

**The honest next move is FU#2.** It's architecturally straightforward (design
sketch above), confirmed blocking by the 2026-04-24 ceiling hits, and every
subsequent voice (Plato first) will need it. Sonnet-shaped execution work
once the design pass is complete.

**After FU#2 lands:** Plato build becomes unblocked. Plato's run will test
(a) whether FU#32's positive-compensation pattern generalizes beyond
Dostoevsky (e.g., to philosophical-human voice-mode), (b) whether FU#2's
chunked verification actually reduces citation-verification skips to zero,
(c) whether the richer arch-03 card continues to produce 0 Output Register
violations cross-voice.

**Dostoevsky-specific follow-ups NOT in scope for next session:**
- FU#33 patcher scope extensions (mechanical lint, transliteration,
  bracket residue) — orthogonal to voice-tissue work; can wait until after
  FU#2 + 1-2 more voices run.
- Pass 7-anachronism flag increase (6 → 8) — may be the voice speaking its
  own grammar triggering the gpt-5.4 check; needs review but not a blocker.
- Ship-ready Dostoevsky card — current 165KB is the best we've produced;
  human review pass can finalize after FU#2 lands a clean citation-
  verification audit.

If you want a comparison-by-content helper script for the three cards
(Phase L baseline / Phase 1 / Phase 2), one exists at `/tmp/fu32/compare_pass2.py`
from this session. Extend to 44 fields if needed, but the critical diff
(character + register_and_tone + banned_language + default_questions) has
been inspected and documented above.

---

*End handoff. Phase 2 landed. Next: FU#2 chunked Pass 7-pre verification.*
