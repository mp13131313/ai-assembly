# Handoff — 2026-04-29 LATE (post-FU#60 thinking audit)

**Supersedes the morning + afternoon entries of 2026-04-29.** This pickup covers the late-evening Cleopatra finalization + FU#56–#60 work + Anthropic adaptive-thinking audit.

**Branch:** `voice-pipeline-v2.1-align-revert` (NOT yet merged to main; shared with parallel voice-pipeline thread)
**Code repo HEAD:** `dd64782` (FU#60 wrapper) — pushed
**Athens-2026 data repo HEAD:** `829cea8` (Cleopatra final + 19 surgical patches) — pushed
**Tests:** 223/223 passing

---

## TL;DR — three architectural finds + 19 patches

1. **Cleopatra shipped end-to-end through FU#53 architecture.** 19 operator-side patches across 2 rounds at the gate; 4 FU#56-class register residuals accepted via `_operator_review_passed.flag`. Validator's overall summary: *"exceptionally researched, distinctive Cleopatra card with strong internal architecture, high specificity, and unusually good resistance to cliché."* 4 of 6 rubrics PASS.

2. **FU#58 + FU#59 + FU#60 filed and landed pre-voice-4** — three architectural fixes that should reduce operator-patch burden ~80-100 across remaining 8 voices.

3. **Adaptive thinking audit (FU#60).** Discovered ~30+ Opus 4.7 call sites across runtime + personas + voice pipelines have been running with thinking *intermittently* engaged but display=omitted (default on Opus 4.7) — meaning thinking content was zeroed out before reaching callers, AND the wrapper dropped `thinking_delta` events anyway. **The config was correct per Anthropic docs.** Visibility was the bug. Wrapper now captures + surfaces. Empirical thinking-engagement rate per persona pass is now measurable on next run.

---

## What this thread landed

### Persona pipeline (commits on `voice-pipeline-v2.1-align-revert`)

| Commit | Description |
|---|---|
| `2fda654` | docs: 12→10 voice-count consistency + FU#21 + FU#33 P2 closures |
| `0ec9755` | docs(specs): refresh Card v2.1 + Pipeline v4 to 2026-04-29 state |
| `08279d0` | docs(planning): FU#55 → rolling per-voice fork-test (Plato + Cleopatra in) |
| `49b3a28` | fix(personas): FU#58 — Pass 7a prompt drift on sensitive_topics + Card v2 clarification |
| `fc48c27` | fix(personas): FU#59 — Pass 7c × Pass 7a FINAL register-rule conflict |
| `dd64782` | fix(personas/clients): FU#60 — adaptive thinking observability + temperature compatibility |

### Athens-2026 data repo
| Commit | Description |
|---|---|
| `4989c64` | voice(plato): drop sensitive_topics over-emission (FU#58) |
| `9c82bbe` | voice(cleopatra): full pipeline run + 7 round-1 patches at gate |
| `829cea8` | voice(cleopatra): final FU#53-equivalent + 12 round-2 patches |

### Other thread (parallel, same branch — voice-pipeline runtime side)
| Commit | Description |
|---|---|
| `f68bc3f`, `30a38eb`, `fb33bb9` | voice-pipeline v2.1 alignment + post-dryrun tuning |
| `f6ee392` | feat: drop title/subtitle from voice + derive themes_covered |
| `0381278` | fix: drop temperature + add display: summarized — voice-pipeline side of FU#60 |

**Branch state:** main is at `c87d415` (10 commits behind tip). Both threads landed cleanly on the shared branch with no conflicts. Eventual merge to main pending operator decision.

---

## FU stack summary (all filed in `_workspace/planning/FOLLOW_UPS.md`)

| FU | State | Description |
|---|---|---|
| **FU#55** | 🟡 IN PROGRESS — rolling per-voice | Form-variance test on each voice's Pass 4b. Plato + Cleopatra populated (both declined permission); 8 voices remaining. Resolution criteria: 0/10 → close §H aspirational; 1-2/10 → opt-in flag; 3+/10 → re-evaluate landing. |
| **FU#56** | 🔵 deferred (Cleopatra-trigger) | Pass 2/3/4a register-discipline gap on long-form fields. Empirically attested on Plato + Cleopatra; structurally produces non-zero Pass 7a FINAL residuals every run. Operator-flag exit is working solution; deeper fix is post-Athens prompt work risking 04-28 revert pattern. |
| **FU#57** | ✅ LANDED | bold_engagement_topics dropped from runtime system prompts + chat artifact (other thread + this thread coordinated). |
| **FU#58** | ✅ LANDED | Pass 7a prompt drift on sensitive_topics — was false-flagging cards as "missing" a field that's Pass 1.5 build-side substrate, not a card field. Plato over-emission cleaned up. |
| **FU#59** | ✅ LANDED | Pass 7c × Pass 7a FINAL register-rule conflict. Pass 7c stops emitting `[ADDED FROM TESTING:]` annotations; Pass 7a FINAL tolerates Boddice biocultural-discipline brackets. Eliminates ~80-100 operator patches across remaining 8 voices. |
| **FU#60** | ✅ LANDED (wrapper level) | Adaptive thinking observability + temperature compatibility. `clients.py` now captures `thinking_delta` + `block_types`; sets `display: "summarized"`; drops `temperature` when `thinking=True` per Anthropic docs §"Feature compatibility". |

---

## Open / undecided from this thread

### High-value, pre-voice-4

1. **Empirical measurement: how often does adaptive thinking actually engage per persona pipeline pass?**
   With FU#60 wrapper changes landed, the data is now visible. Need either:
   - One full voice run with `block_types` + `thinking_trace_chars` logged per call (1-line `stamp()` addition in `run_persona_pipeline.py`)
   - Or a standalone diagnostic script that fires each pass shape against real inputs and reports
   - Decides whether `output_config: {effort: high|xhigh}` should be added per pass to FORCE thinking, or whether default-high engagement is sufficient

2. **9480d3a revert hypothesis re-evaluation.** With thinking now visible AND demonstrated to fire intermittently, the *cumulative-prompt-additions-degrade-texture* finding from 04-28 may have been partly compensating for inconsistent thinking. Could re-attempt a single FU#49A v1 component (e.g., trace-preservation in `relationship_to_detailed_response`) on Plato Pass 4b under thinking-on AND with `effort: high` explicit, see if texture holds. This is the architectural question that FU#56 + FU#55 outcomes hinge on.

3. **Plato re-run with thinking-on (operator decision).** Cost: ~$5 extra, ~30 min wall. Compare card quality + Pass 7a FINAL residual count vs. shipped Plato. If clearly better → land thinking-effort per-pass for voices 4-10 and re-run shipped voices. If equivalent → wrapper changes alone are enough. If worse → revert (over-thinking on synthesis tasks).

### Voice buildout (post-Cleopatra)

4. **Octopus** — DR routing pending. Voice 4.
5. **7 voices needing DR sessions** (~24 hr operator wall): Battuta, Scheherazade, Lovelace, Dostoevsky, Arendt, Marley, Whanganui. Manual claude.ai work.
6. **Mediated-voice prompt fix for Scheherazade** — flagged in earlier session; verify status pre-her-build.

### Branch hygiene

7. **`voice-pipeline-v2.1-align-revert` → main merge** — both threads have committed to this branch. Pre-Athens decision: merge now (clean state) or wait for one more empirical voice run.
8. **Stale branches** (already deleted from origin): `prompt-revert-to-582af96-baseline`, `voice-pipeline-spec-v2`. Local copies may still exist — `git branch -D` if so.
9. **Untracked file**: `docs/AI_Assembly_Frame_Concept_v1.md` (separate workstream — framing layer for Athens; not touched this session). Leave or commit per separate decision.

### Documentation

10. **`LLM_CALL_INVENTORY.md`** — needs update for FU#57/58/59/60. Stale since 04-27.
11. **`OPEN_ITEMS_VOICE_PIPELINE_2026_04_29.md`** (other thread's filing) — separate planning doc; coordinate with parallel thread before next merge.

### Voice Pipeline runtime (other thread's territory, captured for context)

12. **Voice Pipeline end-to-end dry-run** — runtime side; modules built but not yet exercised against real Provocateur briefings beyond a synthetic Plato test that the other thread ran.
13. **Microsite, admin console, closing-show pipelines** — UNBUILT per ONBOARDING.md (refreshed earlier this session). Athens blockers beyond cards.

---

## What I would do next session, in priority order

1. **Verify branch state on a fresh session** — confirm `dd64782` HEAD, `829cea8` athens-2026 HEAD; check for any new other-thread commits since this handoff.
2. **Decide on the Plato thinking-on re-run** (operator call). The wrapper makes it possible to cleanly measure; question is whether the empirical data is worth $5 + 30 min.
3. **If yes:** add a 1-line `stamp()` per pass that logs `r["block_types"]` + `len(r["thinking_trace"])`; cache-invalidate Plato from Pass 2; re-run; compare card vs. shipped Plato.
4. **If no:** continue with Octopus DR routing or one of the 7 DR-needed voices.
5. **In parallel (operator-side):** complete the 7 manual claude.ai DR sessions (~24 hr wall, but operator-time-bounded).

---

## Critical context for next-session pickup

**Empirical state of thinking on persona pipeline (post-FU#60 wrapper):**
- Config IS correct per Anthropic docs (`{type: adaptive}` + `display: summarized` + no temperature)
- Adaptive thinking IS firing on production prompts at default-high effort SOMETIMES (raw Cleopatra Pass 2 test confirmed thinking block + 1032-char signature; but content_len=0 because that test predated `display: summarized` landing)
- Adaptive is non-deterministic — different runs of same prompt + same config decide differently
- We have NEVER run a voice with the FU#60-patched wrapper. Next run is the first time we'll have actual visibility per pass.

**Cleopatra final state validates the whole architecture:**
- FU#49A v2 quality_criteria scaffold landed cleanly
- FU#53 review-gate caught real cross-pass contradictions invisible to per-pass 7a (Jowett-vs-banned_language; constitution[6] Kosmētikon-authorship contradicting hard_limits[5])
- FU#33 P2 INCONSISTENT routing wired correctly
- FU#52 chat_system_prompt invalidation gap closed
- 4 of 6 Pass 7a FINAL rubrics PASS — the architecture is producing high-quality cards on hostile-source-reconstruction voice

**Don't trust LLM_CALL_INVENTORY.md** — last updated 04-27, doesn't reflect FU#57/58/59/60. The wrapper observability fields (`thinking_trace`, `block_types`) aren't in any current doc inventory.

**The 9480d3a-revert finding is now re-interpretable.** Some of the texture loss attributed to "cumulative prompt additions" may have been "cumulative directives without thinking bandwidth." The question is empirically resolvable now — single Plato Pass 4b re-run with thinking visible would tell us a lot.

---

## Reading order for next-session pickup

1. This doc
2. `_workspace/planning/HANDOFF_2026_04_29.md` (revised earlier this session — Plato finalization context)
3. `_workspace/planning/FOLLOW_UPS.md` §FU#55-#60 (most recent)
4. `_workspace/planning/BRIEF_OPUS_4_7_THINKING_AUDIT_2026_04_29.md` (full audit + Task 1+5 results)
5. `_workspace/planning/OPEN_ITEMS_VOICE_PIPELINE_2026_04_29.md` (other thread's parallel filing)
6. `personas/flows/shared/clients.py:80-150` (the wrapper, post-FU#60)

If task is voice 4 build: skip to step 4-5 + `personas/run_persona_pipeline.py` + `_workspace/planning/ONBOARDING.md`'s "After CARD COMPLETE" checklist.

If task is Plato thinking-on experiment: read this doc + `BRIEF_OPUS_4_7_THINKING_AUDIT` + run `/tmp/anthropic_thinking_truth.py` + `/tmp/pass2_thinking_observability_test.py` for context.
