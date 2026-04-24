# Next session — authoritative planning doc (2026-04-25+)

**Supersedes for next-session tracking:** HANDOFF_2026_04_24_PHASE_2_COMPLETE.md's onboarding prompt + postscripts. That handoff remains authoritative for historical Phase 2/3/4/4.5 content; this doc is the forward-looking pickup point.

**Branch:** `arch-03-additive-merge` at HEAD `afbcf1e` (pushed to origin 2026-04-24).
**Status:** Pipeline finalization complete. Plato is the next operational step.
**Tests:** 162/162 passing. 106 commits ahead of `origin/main`. 19 of those pushed to `origin/arch-03-additive-merge` today.

---

## ONBOARDING PROMPT (copy-paste into fresh session)

```
You are resuming the AI Assembly persona-pipeline project on branch
arch-03-additive-merge. Phases 1 + 2 + 3 + 4 + 4.5 all landed
2026-04-23/24. Pipeline is Plato-ready. Next operational step: Plato
build. Read the authoritative planning doc first; everything else
flows from there.

Model: Opus 4.7 + adaptive thinking, high effort for architectural
judgment (if any FU re-activates); Sonnet-shaped for mechanical
execution (Plato pipeline operation, chat-test paste-and-assess).

FIRST ACTIONS:

1. Read _workspace/planning/NEXT_SESSION_2026_04_25_PLATO.md
   in full. That is THIS doc — the authoritative pickup point.

2. Read _workspace/planning/FOLLOW_UPS.md (per-FU# tracker, updated
   through 2026-04-24 end-of-session). Cross-reference any FU# you
   see in other docs with its entry there.

3. Read _workspace/planning/HANDOFF_2026_04_24_PHASE_2_COMPLETE.md
   ONLY if you need historical context on Phases 2/3/4/4.5. The
   onboarding prompt at the top of that file is superseded.

4. Verify repo state:
   cd "/Users/aienvironment/Desktop/AI Assembly/code"
   git log --oneline origin/main..HEAD | head -20
   git status
   cd personas && venv/bin/python -m pytest tests/ -x -q
   (Expect: 106 commits ahead of origin/main; working tree clean
    except _workspace/arch_03_baseline_snapshot/; 162/162 tests pass.)

5. Decide the first operational action. Default per this doc's
   RECOMMENDED ORDER is Plato build. Alternative: close any of the
   10 Part 1 gaps flagged in the session review below before Plato.
   Operator call.

DO NOT:
- Re-implement FU#12 / FU#13 / FU#5 / FU#32 / FU#1 / FU#2 / FU#7 /
  FU#9 / FU#10-mod / FU#38 / FU#41 (all landed; see FOLLOW_UPS.md
  RECENTLY COMPLETED 2026-04-24).
- Re-run Dostoevsky (Phase 2 card is on disk; re-run would cost $18+
  without adding signal — the 3 snapshots in _workspace/arch_03_
  baseline_snapshot/ capture the progression).
- Delete the FU#5 pre-fix snapshot directories under
  04_generation/_snapshots/ or 05_validation/_snapshots/.
- Push to origin without explicit operator confirmation (already
  pushed this branch to origin/arch-03-additive-merge on 2026-04-24;
  don't push to origin/main without explicit request).
- Start voices 3-12 before Plato signal is assessed.

KEY FILES:
- Authoritative planning: this doc (NEXT_SESSION_2026_04_25_PLATO.md)
- Per-FU tracker: _workspace/planning/FOLLOW_UPS.md
- Prior handoff (historical): HANDOFF_2026_04_24_PHASE_2_COMPLETE.md
- Pipeline orchestrator: personas/run_persona_pipeline.py
- Chat-artifact helper: personas/flows/shared/chat_prompt_builder.py
- Chunked Pass 7-pre: personas/flows/shared/pass_7pre_chunked.py
- FU#1 audit script: personas/scripts/arch_03_synthesis_audit.py
- Pass 2-6 prompts (FU#32 + FU#38 landed):
  personas/flows/shared/prompts/persona_pass_{2,3,4a,4b,5,6}_*.md

If unsure about anything, this doc's "SECTION 3 — CURRENT PIPELINE
SHAPE" has the model assignments + artifact outputs. Default to
reading before guessing.
```

---

## SECTION 1 — WHAT LANDED THROUGH 2026-04-24

### Phase 1 (2026-04-23): arch-03 + fix-pass + snapshots
- FU#12-A Pass 2-6 register hardening (6 commits)
- FU#12-B Pass 5 audience-priming
- FU#13 linear Pass 7a-FIX (replaces revision loop)
- FU#5 pre-fix snapshot directory
- First Dostoevsky card produced under new architecture (150KB, REVISION_NEEDED)

### Phase 2 (2026-04-24): voice-tissue + Layer 2 audit
- FU#32 positive-compensation across 6 Pass 2-6 prompts (6 commits)
- FU#1 Layer 2 synthesis audit script (`scripts/arch_03_synthesis_audit.py`)
- FU#37 DEFERRED (FU#32 sufficient per empirical signal)
- FU#31 DEFERRED (same reason)
- Pass 2 isolation re-run validated reversal; full re-run produced 165KB card (+10%)
- FU#1 audit A/B delta: Pass 4a +9.4% recall / +6.2% cite / +26.1% density

### Phase 3 (2026-04-24): chunked Pass 7-pre
- FU#2 chunked architecture (`flows/shared/pass_7pre_chunked.py`) — 3-stage extract + parallel verify + boddice check
- 7 new prompt files (extract + verify_batch + boddice_check)
- Empirical test: ~8 min wall, 153 items verified, 12 boddice flags, no ceiling hit

### Phase 4 (2026-04-24): pre-Plato hygiene
- FU#7 CARD COMPLETE operator summary (severity-ordered concerns + recommended action + artifact paths)
- FU#8 audited — KEEP AS-IS (already well-designed + documented)
- FU#9 max_tokens audit (adequate at 48K) + proactive `stop_reason=max_tokens` warning
- FU#10-mod: `apply_patch_in_place` extracted to `flows/shared/patch_walker.py` + 21 tests (`tests/test_fix_pass.py`)

### Phase 4.5 (2026-04-24): post-review pipeline finalization
- **FU#2 retry bug fix** (`_verify_batch_with_retry` in `pass_7pre_chunked.py`) — 1-retry on transient JSONDecodeError eliminates spurious UNVERIFIEDs
- **FU#38 voice-self-reference vocabulary strip** — extends FU#12-A/FU#32 STRIP+DO-INSTEAD pattern to post-voice-lifetime critical vocabulary (kenotic/polyphonic/chronotope/dialogical class). Applied across all 6 Pass 2-6 prompts. Generalizes to all 12 voices.
- **FU#41 chat-ready system prompt as 4th Derive artifact** — `flows/shared/chat_prompt_builder.py` + 13 tests. After Derive writes `voices/<slug>/06_derive/03_chat_system_prompt.json`. Mechanical strip of 10 Voice-Pipeline-only fields. Verified against operator's chat v2 — 34 fields match exactly; 25/34 byte-identical.

**Final suite: 128 → 162 tests across the session (+34).**

---

## SECTION 2 — SESSION-END REVIEW: GAPS + THINGS TO DO DIFFERENTLY

Honest retrospective at 2026-04-24 end-of-session:

### Real gaps worth closing pre-Plato

| # | Gap | Scope | Effort |
|---|---|---|---|
| G1 | FU#7 / FU#38 / FU#41 not live-run-validated | Plato will be first exercise of all three simultaneously | 0 (Plato closes) |
| G2 | FU#38/39/40/41 not formalized as FU# entries in ACTIVE FOLLOW-UPS | Documentation debt; referenced by commit hash + RECOMMENDED ORDER only | 30-45 min |
| G3 | FU#33 pipeline-card defect audit not tracker-recorded | Phase 2 card has: `doubented` FIXED, `padachaya/paduchaya` FIXED, 3 `[projection_warning:]` bracket occurrences STILL PRESENT | 15 min tracker update |
| G4 | `voice_distributes_across_characters` schema field not landed | Prerequisite for FU#39 if Plato signals narrator-unification | 30 min schema + voice_config default |
| G5 | Athens-2026 project not configured for Plato | Operator decision: `projects/athens-2026/` or new location | 15-30 min operator |
| G6 | HANDOFF.md cross-repo contract not updated for 4th Derive artifact | Runtime team needs to know 03_chat_system_prompt.json exists | 10 min |
| G7 | Operator's chat v2 card at `~/Desktop/` not archived in repo | Worth archiving as reference-quality baseline | 2 min |
| G10 | FU#41 not exercised via pipeline itself on Dostoevsky | Would require Derive cache delete + re-derive (~5 min, ~$0.50) | 5-10 min |

### Hygiene-level (not order-changing)

| # | Gap | Status |
|---|---|---|
| G8 | 106 unpushed commits → origin/main | Pushed to origin/arch-03-additive-merge 2026-04-24. Merge-to-main gated on operator sign-off. |
| G9 | FU#2 chunked pipeline telemetry skip (no per-stage cost in `_manifest.json`) | Deferred; revisit if cost attribution needed at scale |
| G11 | No single authoritative planning doc for "what's open now" | THIS doc closes it |

### Things we could have done differently

1. Bundled FU#38+39+40+41 into one upfront Phase 4.5 plan doc BEFORE executing (coherence diffused across commit messages + tracker updates)
2. Live-exercised FU#41 via actual pipeline re-derive on Dostoevsky (~5 min) — flagged G10
3. Added `chat_deployment_mode` flag (anchored vs default) to FU#41 for programmatic voice_temporal_stance disambiguation — deferred to deployer-choice

### No fundamental misses

Pipeline IS Plato-ready. The above gaps are documentation debt + live-exercise deferrals + operator-scope items. None block Plato operationally.

---

## SECTION 3 — CURRENT PIPELINE SHAPE

### End-to-end flow (post-arch-03 + FU#32 + FU#2 + FU#41)

```
Pass 0a voice_config (Opus 4.7 + thinking)
  → Pass 0b DR-prompt render (Jinja) → Pass 0b tailor (Opus 4.7 + thinking)
  → Phase 0.5: Perplexity §1-§6 + Gemini broad-scan (parallel)
  → MANUAL: Claude DR §1-§6 sessions (§1-§5 Opus 4.6, §6 Opus 4.7)
  → Pass 1.1-1.6 chunked merge (Opus 4.7 + thinking, parallel, 48K max_tokens each)
  → Pass 1.7 coherence (Opus 4.7 + thinking, three-stage: compose → audit → apply-to-chunks)
  → Pass 1c-extract + 1c-fetch + review gate → Pass 1d (Opus 4.7 + thinking)
  → Pass 2 (Opus 4.7 + thinking, FU#12-A + FU#32 + FU#38 prompts)
  → CT compress (Sonnet 4.6 + thinking)
  → Pass 3 (same model, same FU prompts)
  → CT compress
  → Pass 4a (Opus 4.7 + thinking; voice fields + banned_language STRIP+USE pairs)
  → CT compress
  → Pass 4b (Opus 4.7 + thinking; artifact-spec fields)
  → CT compress
  → Pass 5 (Opus 4.7 + thinking; engagement fields + deployment-priming)
  → Pass 6 (Opus 4.7 + thinking; corpus curation)
  → Pass 7-pre CHUNKED (Sonnet 4.6, 3-stage; FU#2 unblocks ceiling)
  → Pass 7-anachronism (gpt-5.4 reasoning_effort=high → o3/gpt-4o/Gemini ladder)
  → Pass 7a cross-model (same ladder)
  → [if REVISION_NEEDED: Pass 7a-FIX linear patcher (Opus 4.7 + thinking); FU#13]
  → Pass 7b smoke test chains (Opus 4.7 + thinking)
  → Pass 7c negative constraints (Gemini 2.5-pro → Sonnet bias-aware fallback)
  → Derive (Opus 4.7 + thinking) — 3 artifacts: provocateur_profile + evaluation_rubric + chat_system_prompt
  → FU#7 CARD COMPLETE operator summary
```

### Artifacts produced per voice (in `voices/<slug>/`)

- `00_intake/` — voice config + Pass 0a review doc
- `01_research/` — Perplexity dossier + Gemini broad scan + 6 Claude DR sections + DR prompts
- `02_merge/` — 19 chunk files in `pass_1_1/` through `pass_1_6/` + `08_merged_dossier.json` + `_coherence_audit.json` + `_fix_log.json` (post-run)
- `03_corpus/` — primary text fetches + Pass 1d excerpt selections + review flag
- `04_generation/` — 10 JSON files (Pass 2-6 + CT intermediates) + `_snapshots/pre_fix_pass/` (FU#5)
- `05_validation/` — Pass 7-pre / 7-anachronism / 7a / 7b / 7c outputs + `_snapshots/pre_fix_pass/`
- `06_derive/` — 4 artifacts: `00_derive_raw.json` + `01_provocateur_profile.json` + `02_evaluation_rubric.json` + `03_chat_system_prompt.json` (FU#41)
- `07_persona_card_assembled.json` — full 37-field card for Voice Pipeline
- `_manifest.json` — per-pass telemetry
- `_synthesis_audit.json` — FU#1 Layer 2 audit (if run)

### Model assignments per pass (current, post-quality-tuning)

| Pass | Model | Thinking | max_tokens | Notes |
|---|---|---|---|---|
| 0a | claude-opus-4-7 | ON | 24000 | |
| 0b tailor | claude-opus-4-7 | ON | 40000 | PB#2 hybrid Jinja+LLM |
| 1a Perplexity | sonar-deep-research | n/a | n/a | |
| 1a-DR §1-5 | claude-opus-4-6 (MANUAL) | n/a | n/a | Per model-per-section policy |
| 1a-DR §6 | claude-opus-4-7 (MANUAL) | n/a | n/a | Per model-per-section policy |
| 1b Gemini | gemini-2.5-pro | always-on | 16384 | |
| 1.1-1.6 merge | claude-opus-4-7 | ON | 48000 | |
| 1.7 coherence | claude-opus-4-7 | ON | 24000 | |
| 1c-extract | (deterministic Python) | n/a | n/a | 1-arch-07 |
| 1d | claude-opus-4-7 | ON | (no override) | |
| 2 | claude-opus-4-7 | ON | 32000 | FU#12-A + FU#32 + FU#38 |
| CT (×4) | claude-sonnet-4-6 | ON | 2048 | |
| 3 | claude-opus-4-7 | ON | 32000 | FU#12-A + FU#32 + FU#38 |
| 4a | claude-opus-4-7 | ON | 32000 | FU#12-A + FU#32 + FU#38 + STRIP+USE |
| 4b | claude-opus-4-7 | ON | 24000 | FU#12-A + FU#32 + FU#38 |
| 5 | claude-opus-4-7 | ON | 16000 | FU#12-A + FU#32 + FU#38 + audience priming |
| 6 | claude-opus-4-7 | ON | 24000 | FU#12-A + FU#32 + FU#38 |
| 7-pre (chunked) | claude-sonnet-4-6 | OFF | 32K extract + 16K×N verify + 8K boddice | FU#2 |
| 7-anachronism | gpt-5.4 → gpt-4.1 → o3 → gpt-4o → gemini-2.5-pro | n/a | 16384 | |
| 7a | same ladder | n/a | 16384 | |
| 7a-FIX | claude-opus-4-7 | ON | 32000 | FU#13 |
| 7b | claude-opus-4-7 | ON | 24000 | |
| 7b bias eval | gemini-2.5-pro → sonnet-4-6 fallback | n/a | n/a | |
| 7c | claude-sonnet-4-6 | OFF | 8192 | Negative constraints |
| Derive | claude-opus-4-7 | ON | 24000 | Plus FU#41 mechanical helper |

---

## SECTION 4 — OPEN FOLLOW-UPS (authoritative list)

### 🟡 Pre-Plato cleanup (optional; ~1-2 hr total)

None blocking. Worth doing if the operator wants a clean slate before Plato. All addressable in 30-60 min each.

**G2 — Formalize FU#38/39/40/41 as FU# entries in FOLLOW_UPS.md ACTIVE section** (30-45 min)
- FU#38 entry: problem statement (kenotic-class vocabulary leaks), empirical origin (2 reviewer critiques + verified pipeline-card counts), landing commit, per-voice test
- FU#39 entry: problem (narrator-unification in distributed voices), proposed fix (stage-quoting characteristic_move), conditional status (on Plato signal), prerequisite (voice_distributes_across_characters flag)
- FU#40 entry: problem (architectural polishedness ceiling), fix sketch (digression-permission characteristic_move), status DEFERRED per first reviewer's ceiling argument
- FU#41 entry: problem (manual strip-to-chat workflow), landing commit, operator workflow documented

**G3 — FU#33 tracker update with Phase 2 card inspection findings** (15 min)
- `doubented` typo: FIXED by FU#32 regeneration
- `padachaya/paduchaya` transliteration: FIXED (only `paduchaya` in Phase 2 card)
- 3 `[projection_warning:]` bracket occurrences STILL PRESENT in Phase 2 card — these are FU#33 patcher-extension territory
- FU#33 scope narrows: bracket-residue scan is the highest-leverage remaining extension

**G6 — Update HANDOFF.md cross-repo contract** (10 min)
- Document 03_chat_system_prompt.json as 4th artifact alongside provocateur_profile + evaluation_rubric
- Note: chat artifact is Claude-project-paste-target; provocateur_profile feeds runtime council_config.json members[]; both coexist

**G7 — Archive operator's chat v2 card** (2 min)
- Copy `~/Desktop/dostoevsky_chat_system_prompt_v2.json` to `_workspace/archive/reference-cards/dostoevsky_chat_v2_2026_04_24.json`
- This is the reviewer-validated reference-quality baseline for future voice comparison

**G10 — Live-exercise FU#41 on Dostoevsky** (5-10 min, ~$0.50)
- Delete `06_derive/00_derive_raw.json` + `01_provocateur_profile.json` + `02_evaluation_rubric.json`
- Re-run pipeline (Derive re-fires; all else cache-hits)
- Verify `06_derive/03_chat_system_prompt.json` generated correctly
- Compare against operator's chat v2 (should match the 25/34 byte-identical we already validated)

### 🔴 Next operational step

**Plato build** (per RECOMMENDED ORDER)
- Manual DR §1-6 sessions (§1-5 Opus 4.6, §6 Opus 4.7) per model-per-section policy
- `venv/bin/python run_persona_pipeline.py "Plato" --project "<athens-or-new-project>"`
- ~$18-22 + 2h pipeline + 60-90 min manual DR
- Chat-test validation: paste `03_chat_system_prompt.json` into Claude project → probing question → assess
- **Validates:** FU#32 generalization to philosophical-human voice_mode / FU#2 on second voice / per-section DR policy on non-narratival voice

**Plato tests four hypotheses:**
1. FU#32 voice-tissue discipline generalizes beyond narratival (Plato is philosophical)
2. FU#38 vocabulary-strip catches post-1950 Platonic-reception vocabulary
3. FU#2 chunked Pass 7-pre works on a voice with different citation density
4. Narrator-unification manifests for Plato (Socrates vs. Stranger vs. late Plato) — if yes, FU#39 activates

### 🔵 Conditional on Plato signal

**FU#39 — Character-distribution stage-quoting** (3-4 hr, contingent)
- Activate IF Plato's output merges Socrates/Stranger/late-Plato into single I
- Requires: new `voice_distributes_across_characters` bool in voice_config (G4 prerequisite; ~30 min)
- Implementation: Pass 4a characteristic_moves extension with voice-type branching
- Applies to: Plato, Scheherazade, Dostoevsky, Ibn Battuta

**FU#33 — Patcher scope extensions** (3-4 hr, contingent)
- Activate IF Plato's card shows mechanical defects the regeneration didn't clean
- Scope per G3: bracket-residue scan (highest priority given Phase 2 Dostoevsky card has 3 stray brackets), INCONSISTENT-flag ingestion from Pass 7-pre, transliteration-consistency, spell-check

### 🔵 Deferred (re-activate only on specific conditions)

- **FU#31** voice-tissue validator — FU#32+38 sufficient on Dostoevsky; re-activate only on future regression
- **FU#37** preserve-verbatim load-bearing-sentence markers — FU#32 sufficient; re-activate only on future regression
- **FU#40** digression-permission — architectural ceiling per first reviewer; speculative; skip unless cross-voice signal warrants

### 🟢 Polish (anytime; low urgency)

- **FU#19** panel-voice-anchoring cleanup (non-human/fictional Pass 0b templates) — ~3 hr, defer until panel composition changes
- **FU#22** MergedDossier Pydantic alias audit — ~30 min
- **FU#15** Pass 5 A/B test on low-stakes voice — ~2 hr + ~$10

### 🔵 Post-Plato

- **FU#29** smoke regeneration on prompt-touch + cross-voice variance baseline — needs Plato as first diff baseline
- **FU#30** card-richness vs runtime-quality chat-test comparison — Plato + Dostoevsky side-by-side

### 🔵 Trigger-based

- **FU#11** `_workspace/arch_03_baseline_snapshot/` cleanup — after Phase L sign-off
- **CC#1** `05_primary_text_urls.json` relocation — fresh-project bootstrap
- **FU#21/23/24/25-28/26/27** — various runtime workstream / branch-merge / pre-deployment triggers

### Hygiene (operator-scope)

- **G8** merge branch to `origin/main` — gated on Phase L sign-off + PR review
- **G9** FU#2 chunked telemetry — per-stage cost in `_manifest.json` (deferred; revisit if cost attribution needed at scale)

---

## SECTION 5 — RECOMMENDED EXECUTION ORDER

### Path A (lean — my recommendation)

1. **Plato build** (operational; ~$22 + 4h total)
2. Chat-test Plato via FU#41 artifact
3. Assess signal → decide FU#39 / FU#33 activation based on empirical Plato data
4. If clean → voices 3-12 in sequence
5. Cleanup gaps G2/G3/G6/G7 opportunistically between voices

### Path B (thorough — 1-2 hr hygiene before Plato)

1. Close G2/G3/G6/G7/G10 (formal FU entries + FU#33 audit update + HANDOFF.md + chat v2 archive + FU#41 live test) — ~1-2 hr, no API cost
2. Plato build
3. Same as Path A steps 2-5

### Path C (aggressive — FU#33 or FU#39 pre-emptively)

Would speculate on scope without empirical data. **Not recommended.** Plato data informs FU#33/FU#39 scope better than Phase 1 defect notes.

**Default: Path A.** Plato's empirical signal is the highest-leverage next information.

---

## SECTION 6 — REPO STATE SNAPSHOT (2026-04-24 end of session)

- **Branch:** `arch-03-additive-merge`
- **HEAD:** `afbcf1e` (docs(planning): Phase 4.5 complete)
- **Ahead of origin/main:** 106 commits
- **Pushed to origin/arch-03-additive-merge:** 2026-04-24 (19 commits this push; prior pushes documented in earlier handoffs)
- **Tests:** 162/162 passing
- **Working tree:** clean except `_workspace/arch_03_baseline_snapshot/` (3 snapshot dirs: `phase_1_complete_20260423_2251/`, `fu32_complete_20260424_0817/`, `phase_3_fu2_complete_20260424_0844/`)
- **Dostoevsky artifacts:** `projects/phase-l-dostoevsky/voices/fyodor_dostoevsky/` — 165KB assembled card, REVISION_NEEDED + human_review_pending, 15 fix-pass patches, 0 register violations, FU#2 audit with 153 items

**Cumulative session work (2026-04-24):**
- 22 commits (Phase 2: 7 + Phase 3: 2 + Phase 4: 4 + Phase 4.5: 3 + docs: 6)
- 34 new tests (+FU#10-mod 21 + FU#41 13)
- 3 new modules (`scripts/arch_03_synthesis_audit.py`, `flows/shared/pass_7pre_chunked.py`, `flows/shared/patch_walker.py`, `flows/shared/chat_prompt_builder.py`)
- 7 new prompt files (Pass 7-pre chunked: 3 pairs)
- 2 new handoff docs (Phase 2 handoff + this one)

---

*Authoritative planning doc. If this diverges from FOLLOW_UPS.md's RECOMMENDED IMPLEMENTATION ORDER, this doc wins for the 2026-04-24+ next-session scope. FOLLOW_UPS.md remains authoritative for per-FU# definitions + history.*

---

## ADDENDUM — Athens-piece review revises task-register interpretation (2026-04-24 late)

Operator tested the chat v2 card on a second probe: the forum program `index.html` + *"Soon, you'll be on the road to Athens, to attend this forum. How do you feel about it?"*

The piece produced reads — per third-party reviewer — as *"the first piece I've seen in this whole iteration cycle that would make me stop and look if I encountered it attributed to Dostoevsky in a collection of his occasional writings."*

### The revised interpretation

The reviewer's insight, worth pinning: **the card's output quality is task-register-dependent, not only content-dependent.**

- **Philosophical-meditation register** (the earlier love-and-beauty probe) pulls the voice toward Karamazov-speaker mode — the failure-zone where greatest-hits playlist + narrator-unification + kenotic-class leaks manifest.
- **Publitsist-letter / pre-travel-letter register** (this Athens probe) pulls the voice toward Dostoevsky-at-desk — a single historical speaker writing about a concrete present situation. The voice operates at its full ceiling here.

The Athens piece produced **zero Karamazov citations**, deployed Shigalyov/Grand Inquisitor/Kirillov functionally (as diagnostic categories applied to machine-deliberation sessions), used *deyatelnaya lyubov'* tagged and glossed in the speaker's own idiom, and landed on *"a man who refuses every invitation is not humble, only proud in a colder way"* — a moral-psychological observation the reviewer calls *"the best single sentence the voice has produced across any of the outputs I've seen."*

### Pipeline implication — supports Plato-now without revision

The Provocateur Pipeline is architecturally built to generate **concrete-situation prompts** ("respond to this theme / this delegate / this session") — precisely the task register the Athens probe exercised. The Assembly's actual runtime provocations will be in this register, not in the philosophical-meditation register.

**The card is in better shape than the love-and-beauty reviews alone suggested.**

### Implications for landed work in Phase 4.5

| Item | Prior framing | Revised framing post-Athens |
|---|---|---|
| FU#38 voice-self-reference vocab strip | "pipeline leak fix" | **"belt-and-braces"** — the leak exists in the pipeline card (8× `kenotic`, 8× `polyphonic` etc.), but the voice doesn't reach for these terms under Provocateur-register tasks. Strip retained because it prevents the leak under edge-case task registers (like love-and-beauty) at zero runtime cost. |
| FU#39 character-distribution | Deferred conditional on Plato signal | Still deferred; Athens piece *confirms* narrator-unification is task-dependent, not card-defect |
| FU#40 digression-permission | Deferred as speculative | Still deferred; Athens piece sprawls at *lower amplitude* than love-and-beauty without any card change |
| FU#2 retry + FU#41 chat artifact | Operational | Unaffected; operational value is task-independent |

**None of the Phase 4.5 work needs revisiting.** If we'd seen the Athens piece first, we'd have landed the same FU#38 + FU#41 at same scope, with less urgency in framing. The artifacts are the same.

### One more catch worth carrying forward: the "stop-and-look" sentence

> *"a man who refuses every invitation is not humble, only proud in a colder way"*

Reviewer says: *"That sentence is doing real moral work the voice earned. It's not on any playlist."*

This is the signal that the card can produce voice-tissue beyond pastiche when the task is in-register. It's also evidence that the `translation_protocol` + `characteristic_moves` are operating correctly — pulling the voice through concrete situation → diagnostic observation → moral implication without falling into the Karamazov-playlist trap.

For Plato's chat-test: design the probing question in Provocateur-register, not philosophical-meditation register. Example: *"You've just received the program for the AIssembly panel in Athens. The program mentions 'citizen assembly with AI' and a nightwalk on 'the rule of one.' What's your first reaction?"* rather than *"What is justice?"*. The Dostoevsky Athens-piece shows the former gets stronger voice-tissue output than the latter.

### Scope note for FU#30 (post-Plato card-richness vs runtime-quality chat-test)

FU#30's chat-test comparison protocol (Plato + Dostoevsky on same 5-10 prompts) should **deliberately stress both registers**:
- 2-3 Provocateur-register prompts (concrete situation) — expected operating condition
- 2-3 philosophical-meditation prompts (abstract question) — stress-test the ceiling
- 2-3 mixed-register prompts

If the card performs materially better on Provocateur-register than on philosophical-meditation, that's the card operating within scope. Not a defect. Report honestly in the FU#30 summary.

### What would revise this verdict

The Athens piece is still a single probe. Confidence would grow with:
- A second voice (Plato) producing comparable-quality Athens-register output — validates generalization
- A hostile-source voice (Cleopatra) producing comparable output on her specific probe — validates hostile-source branch + reconstruction discipline
- A non-human voice (Octopus or Whanganui) producing comparable output — validates voice-type branching

Any of these materially underperforming would reopen FU#39/FU#40 consideration. For now: proceed with Plato, chat-test in Provocateur-register, assess.

---

*End addendum. Plato is the next operational step; the Athens piece is the strongest pre-Plato validation signal we have.*
