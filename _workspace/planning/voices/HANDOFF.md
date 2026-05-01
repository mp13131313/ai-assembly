# Voices — Handoff (session-end snapshot, 2026-05-01)

**Companion:** `OPEN_ITEMS.md` (open-items list) + `ONBOARDING.md` (how-to / fresh-pickup). This doc is the session-end pickup snapshot: where we landed today, what's in flight, what's the next operator decision.

**On a fresh session:** read `ONBOARDING.md` first (~10 min), then this doc (~5 min), then `OPEN_ITEMS.md` (~10 min). Done in ~25 min.

---

## Branch + repo state at session end

| Repo | Branch | HEAD | Pushed |
|---|---|---|---|
| code | `voice-pipeline-v2.1-align-revert` | `80338f6` | ✅ yes |
| athens-2026 | `main` | `5088d67` | ✅ yes |

`voice-pipeline-v2.1-align-revert` is 22+ commits ahead of `main`. Merge decision deferred.

---

## Where the 5-of-10 panel voices stand

| Voice | State |
|---|---|
| Plato | ✅ shipped (KNOWN defect — dramatist-vs-speaker collision in 3 places, see OPEN_ITEMS §9; patches drafted but unapplied) |
| Cleopatra | ✅ shipped at FU#61 v3 (committed `c89d186` + `54cd20a`) |
| Dostoevsky | ✅ shipped via path (b) + FU#61-fresh quality_criteria patched (committed `5088d67`) |
| Battuta | ✅ shipped via path (b) — pipeline trail tracked in athens-2026 (`e300508`) |
| Octopus | ✅ shipped via Path A surgical 6-patch + path (b) — committed `8bb9981` |
| Hannah Arendt | ❌ not started |
| Ada Lovelace | ❌ not started |
| Bob Marley | ❌ not started |
| Whanganui River | ❌ not started |
| Scheherazade | ❌ not started — mediated-voice prompt fix flagged as pre-build attention |

---

## What this session landed (since the LATE handoff)

**Voice cards committed to athens-2026:**
- Cleopatra FU#61 v3 + chat sync (`c89d186` + `54cd20a`)
- Dostoevsky FU#61-fresh quality_criteria + chat sync (`5088d67`)

**Code-repo commits:**
- `91947a7` — FU#61 Pass 4b prompt: +1 audience-engagement question
- `9eb0222` — FU#61 v3 verdict + lessons in FOLLOW_UPS.md
- `e90f1e2` — Pass 0a `load_dotenv override=True` bug fix
- `a6fa848` — clients.py retry-on-stream-drop (httpx.RemoteProtocolError)
- `57cb0b5` — FU#61 Pass 4b not Pass 5 doc correction
- `d0457cb` — voices/ subfolder created (OPEN_ITEMS + ONBOARDING)
- `80338f6` — voices/ docs authoritative sweep (incorporates every planning doc + thread)
- `8c1d5f9`, `ba2bcd8` — FU#60/61 filing in FOLLOW_UPS.md
- `85f04da` — clients.py alignment refactor

**Voices built end-to-end this session:** Octopus (to gate, deferred), Dostoevsky (shipped), Battuta (shipped). FU#61 prompt change empirically validated on Cleopatra + Dostoevsky.

---

## What's in flight / open at session end

### Operator-decision pending

1. **Plato 3 surgical patches** for dramatist-vs-speaker collision (`I am the son of Phaenarete` etc.). Drafted in HANDOFF_2026_04_28 §13, never applied. ~10 min. See OPEN_ITEMS.md §9.
2. **Octopus FU#53 review-gate path** — A (surgical 6-patch) / B (Pass 2 rebuild) / C (accept residuals via flag). See OPEN_ITEMS.md §2.
3. **Mediated-voice prompt clarification** — land before Scheherazade's Pass 0a, or plan for surgical patches at her gate. See OPEN_ITEMS.md §9 + ONBOARDING.md "Mediated voices".
4. **Plato thinking-on re-run experiment** ($5, 30 min). See OPEN_ITEMS.md §5.
5. **9480d3a revert hypothesis re-evaluation** — connected to FU#56 + FU#4. See OPEN_ITEMS.md §5.
6. **5 unbuilt voices DR session sequencing** — operator wall time, ~3-4 hr per voice. See OPEN_ITEMS.md §3.

### Cleanup operations (operator confirmation)

7. **Athens-2026 archive file revert** — `archive/first_run/voices/cleopatra/01_research/03_dr_prompts/08_section_6_dr_prompt.md` has 80 lines deleted (forensic, NOT this session). Revert or commit?
8. **Athens-2026 sweep-commit** — Battuta entire voice folder + Dosto pipeline trail + Octopus missing files = ~700 files matching Plato pattern.
9. **Athens-2026 `.gitignore` additions** — `_pipeline_logs/`, `*.pre_*.json`, `_operator_review_passed.flag`.
10. **`/tmp/` cleanup** — pass4b_test_* + standalone_pass4b_test.py + older diagnostic scripts.
11. **Code repo 4 untracked planning docs** — FU61_DRYRUN_VERDICT, PIPELINE_DOWNSTREAM_DESIGN, STEP3_REDESIGN, runtime/ subfolder. Other-thread artifacts; commit or leave?

### Voice-build-affecting but outside voices/ scope

12. **Parent `_workspace/planning/ONBOARDING.md`** — drop "Phase L sign-off" framing + correct §1-§5 vs §6 DR-model spec (stale: pattern is now 4.7 across all 6 sections).
13. **Older HANDOFF_*.md docs** — sweep for "Phase L sign-off" references, or leave as historical?
14. **`LLM_CALL_INVENTORY.md`** — stale since 04-27.
15. **`voice-pipeline-v2.1-align-revert` → `main` merge** — operator decision when.
16. **Pipeline v4 spec doc** — needs reflecting recent FU#52/53/57/58/59/60/61 changes.

### Out of voices/ but related

17. **FU#62 spec-update vs implement** — Voice Pipeline validation regen-on-flag spec/impl gap (recommendation: spec-update path B). Operator decision.

---

## What I would do next session in priority order

1. **Verify branch state** — confirm `80338f6` HEAD on code repo + `5088d67` on athens-2026; check for new other-thread commits.
2. **Pick the next operator-decision** from the list above. Highest-value low-cost: A1 (Plato patches) or B-cluster (athens-2026 sweep + .gitignore).
3. **Or: pick a next voice to build** — Battuta queue is exhausted; 5 voices left. DR sessions are operator-bounded (~3-4 hr each). Sequence: Arendt (philosophical, FU#49 patterns proven) is the easiest pick if Battuta DR-prompts approach was clean.

If task is voice-build:
1. Pass 0a + Phase 0.5 for next voice (~7 min, $)
2. Operator does manual claude.ai DR sessions (~3-4 hr operator wall)
3. Run pipeline: chunked merge → Pass 1c gate → Pass 2-7 → FU#53 gate → operator decision (a/b)
4. Match the 4-shipped-voices pattern: 2 patch rounds + path (b) accept-residuals via flag

If task is cleanup / archive: see §10-11 of this doc.

---

## Reading order for next session

1. `voices/ONBOARDING.md` (steady-state how-to, ~10 min)
2. `voices/HANDOFF.md` — this doc (~5 min)
3. `voices/OPEN_ITEMS.md` (status snapshot, ~10 min)

That's ~25 min to working knowledge for picking up voice-build work cold.

---

## When this doc goes stale

Update `HANDOFF.md` at the end of every voice-build session — it's the session-snapshot, not the steady-state. Roll the prior session's HANDOFF into the next session's by dating the doc and adding a "supersedes prior HANDOFF" note at top.

If you want a versioned history, save prior HANDOFFs as `HANDOFF_<DATE>.md` in `_workspace/archive/voices_consolidation_<date>/` (per the umbrella `<topic>_consolidation_<date>/` convention; first instance: `voices_consolidation_2026_05_01/`).
