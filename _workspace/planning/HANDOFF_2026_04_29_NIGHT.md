# Handoff — 2026-04-29 NIGHT (post-FU#60 alignment)

**Supersedes `HANDOFF_2026_04_29_LATE.md`.** This is a small delta on top of the LATE handoff: one cross-thread audit + one alignment refactor.

**Branch:** `voice-pipeline-v2.1-align-revert` (still not merged to main)
**Code repo HEAD:** `85f04da` (mine — FU#60 cleanup) + `e89dfc4` (other thread — voice-pipeline post-dryrun #4) — both pushed
**Athens-2026 data repo HEAD:** `829cea8` (unchanged since LATE handoff)
**Tests:** 223/223 passing

---

## What this thread added since LATE handoff

### Cross-thread audit of all commits since `08279d0`

Examined all 7 commits on the shared branch since the FU#55 docs commit:

| Commit | Thread | Files |
|---|---|---|
| `49b3a28` FU#58 | persona | persona prompts + Card v2 doc |
| `f68bc3f` voice tuning | runtime | `runtime/flows/voice/*` + voice prompt |
| `fc48c27` FU#59 | persona | `persona_pass_7a` + `persona_pass_7c` |
| `f6ee392` voice title/themes | runtime | `runtime/flows/voice/*` + voice prompts |
| `0381278` FU#60 voice side | runtime | `runtime/flows/voice/{continuity,step1,step2,step3}.py` |
| `dd64782` FU#60 persona side | persona | `personas/flows/shared/clients.py` |
| `0093a43` LATE handoff | docs | planning |
| `85f04da` FU#60 cleanup (mine) | persona | `clients.py` slim |
| `e89dfc4` voice-pipeline #4 (other) | runtime | `voice_flow.py` + voice doc |

**Interference: none.** Disjoint paths persona ↔ runtime; planning files were appended cleanly.

**Half-done finding:** runtime's `_anthropic_call.py` and persona's `clients.py` had diverged in capture style for the same observability story. Runtime walked `final.content` (lean, ~8 lines); persona walked streaming events manually (~30 lines). Both yielded same data with `display: summarized`. Aligned in `85f04da`.

### `85f04da` — clients.py alignment refactor

Slimmed `clients.py` streaming branch to match runtime pattern:
- Drain `text_stream` to consume
- Walk `final.content` once for text + thinking + block_types
- Net -5 lines (-30, +25); same return shape, same values
- Both pipelines now use one idiom for Anthropic streaming capture

Tests 223/223 pass; observable behaviour identical.

---

## Re-resolved point: thinking has been firing all along

Operator caught a framing error in the LATE handoff. The Plato re-run is **not** "first time thinking is on" — adaptive thinking has been firing intermittently on Opus 4.7 the whole time. What FU#60 added was:

1. `display: summarized` so the trace is non-empty (Opus 4.7 default is `omitted`)
2. Drop `temperature` per Anthropic docs §"Feature compatibility"
3. Observability fields (`thinking_trace`, `block_types`)

So the Plato re-run is "first time we can *see* what's been happening, and first time `temperature` isn't being passed alongside thinking." The behaviour change that matters for the experiment is items (1)+(2), already in `dd64782`. The `85f04da` alignment doesn't touch the experiment's signal.

---

## Branch state

- `voice-pipeline-v2.1-align-revert`: 12 commits ahead of `main` (was 10 at LATE)
- main remains at `c87d415`
- No conflicts; both threads landed cleanly
- Working tree clean except untracked `docs/AI_Assembly_Frame_Concept_v1.md` (separate workstream — Athens framing layer; leave per prior decision)

---

## Open / undecided (carryover from LATE — still applicable)

### High-value, pre-voice-4

1. **Plato thinking-on re-run** (operator decision). Wrapper now instrumented + aligned. Cost ~$5, ~30 min wall. Compares card quality + Pass 7a FINAL residual count vs. shipped Plato under `display: summarized` + dropped temperature.
2. **9480d3a revert hypothesis re-evaluation** under thinking-visible conditions.

### Voice buildout (post-Cleopatra)

3. **Octopus** — voice 4, DR routing pending.
4. **7 voices needing DR sessions** (~24 hr operator wall): Battuta, Scheherazade, Lovelace, Dostoevsky, Arendt, Marley, Whanganui.
5. **Mediated-voice prompt fix for Scheherazade** — verify status pre-build.

### Branch hygiene

6. **`voice-pipeline-v2.1-align-revert` → main merge** decision.
7. **Stale local branches** — `prompt-revert-to-582af96-baseline`, `voice-pipeline-spec-v2` may still exist locally.
8. **Untracked `docs/AI_Assembly_Frame_Concept_v1.md`** — leave or commit per separate decision.

### Documentation

9. **`LLM_CALL_INVENTORY.md`** — stale since 04-27; needs update for FU#57/58/59/60 + alignment.
10. **`OPEN_ITEMS_VOICE_PIPELINE_2026_04_29.md`** (other thread) — coordinate before next merge.

### Voice Pipeline runtime

11. **End-to-end dry-run** — modules built, partially exercised; full run not yet under FU#60-instrumented config.
12. **Microsite, admin console, closing-show pipelines** — UNBUILT per ONBOARDING.md.

---

## What I would do next session

1. **Verify branch state** — `85f04da` HEAD; check for any new other-thread commits since this handoff.
2. **Decide on Plato thinking-on re-run** (operator call). Now genuinely just a measurement question: how often does adaptive engage per pass on a real voice run.
3. **If yes:** add 1-line `stamp()` per pass logging `r["block_types"]` + `len(r["thinking_trace"])`; cache-invalidate Plato from Pass 2; re-run; compare card vs. shipped Plato.
4. **If no:** Octopus DR routing or one of the 7 DR-needed voices.

---

## Reading order for next-session pickup

1. This doc
2. `_workspace/planning/HANDOFF_2026_04_29_LATE.md` (full session context — Cleopatra finalization + FU#56-60 audit)
3. `_workspace/planning/FOLLOW_UPS.md` §FU#55-#60
4. `_workspace/planning/BRIEF_OPUS_4_7_THINKING_AUDIT_2026_04_29.md` (full audit results)
5. `personas/flows/shared/clients.py` (post-`85f04da` — aligned with runtime pattern)
6. `runtime/flows/voice/_anthropic_call.py` (the pattern persona now matches)
