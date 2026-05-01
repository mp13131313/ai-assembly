# Voices — Handoff (session-end snapshot, 2026-05-02 — supersedes 2026-05-01)

**Companion:** `OPEN_ITEMS.md` (open-items list) + `ONBOARDING.md` (how-to / fresh-pickup). This doc is the session-end pickup snapshot: where we landed today, what's in flight, what's the next operator decision.

**On a fresh session:** read `ONBOARDING.md` first (~10 min), then this doc (~5 min), then `OPEN_ITEMS.md` (~10 min). Done in ~25 min.

---

## Branch + repo state at session end

| Repo | Branch | HEAD | Pushed |
|---|---|---|---|
| code | `voice-pipeline-v2.1-align-revert` | (this commit + push) | ✅ yes |
| athens-2026 | `main` | `4cff85b` | ✅ yes (Octopus shipped + FU#61-fresh quality_criteria from 2026-05-01) |

---

## Where the 10 panel voices stand

| Voice | State |
|---|---|
| Plato | ✅ shipped (KNOWN defect — dramatist-vs-speaker collision in 3 places, see OPEN_ITEMS §9; patches drafted but unapplied) |
| Cleopatra | ✅ shipped at FU#61 v3 (committed `c89d186` + `54cd20a`) |
| Dostoevsky | ✅ shipped via path (b) + FU#61-fresh quality_criteria patched (committed `5088d67`) |
| Battuta | ✅ shipped via path (b) — pipeline trail tracked in athens-2026 (`e300508`) |
| **Octopus** | ✅ shipped 2026-05-01 (`8bb9981` + `4cff85b`); 🔄 **rebuild in progress 2026-05-02 in current-tests sandbox** — compass framework + 6-layer translation chain + chromatophore display engine integration. DR prompts ready for claude.ai paste. See §"Octopus compass rebuild" below. |
| Hannah Arendt | 🟡 Pass 0a + Phase 0.5 done in current-tests; DR prompts ready for claude.ai paste |
| Ada Lovelace | 🟡 Pass 0a done; Phase 0.5 retrying (Gemini 503 outage); DR prompts pending |
| Bob Marley | 🟡 Pass 0a + Phase 0.5 done in current-tests; voice_mode flipped observational → narratival (Pass 0a hallucinated Card v2 reference; OPEN_ITEMS §3 prediction was correct); DR prompts ready for claude.ai paste |
| Whanganui River | ❌ not started |
| Scheherazade | ❌ not started — mediated-voice prompt fix flagged as pre-build attention |

---

## Octopus compass rebuild (2026-05-02 session)

**Trigger:** chat-test of shipped Octopus card revealed it produced "scholarly translator reporting on the body from outside" rather than the experiment-in-mind voice the operator had originally blueprinted (in March 2026 mock card + compass DR artifact). The shipped card was internally coherent + validator-passed but not the build the operator wanted.

**Diagnosis:** the live April 2026 claude.ai DR sessions had drifted toward precautionary-Continental philosophical framing — Birch's bracketing-as-method, Continental ethological-attunement, CARE Principles as binding constraint, research-governance-as-constitutive — propagating through Pass 1.4 voice synthesis into the built card's anti-unified-I refusal-to-render register. Editorial_rationale was actually compass-friendly all along; the drift came from §5 of the live DR + the operator-stage `review_doc` "refuse to invent... Confidence high" auto-generated language (Pass 0a LLM run-variance — see voices/ONBOARDING DO-list).

**Approach: full rebuild from scratch in current-tests sandbox.** Snapshot of shipped Octopus state preserved at `projects/current-tests/voices/octopus_pre_compass_rebuild_2026-05-01/` (93 files, 9.1MB, full pipeline trail including all `.pre_*.json` snapshots). Athens-2026 production state untouched until rebuild verified.

**Rebuild pivots:**

1. **Pass 0a re-run** with `--editorial-rationale null` → fresh review_doc surfaced "anthropomorphism vs excessive-alienness twin-risks" framing (vs April 27 run's "refuse to invent... Confidence high"). Lesson: Pass 0a is partly LLM run-variance; treat review_doc as starting proposal to interrogate, not as binding commitment. Documented in voices/ONBOARDING DO-list (committed `1c83034`).

2. **`voice_config.manual_grounding`** — replaced auto-generated Wikipedia-only text with rich grounding: Godfrey-Smith *Other Minds* (2016) framing as primary methodology + biology + lifecycle + three-registers (technical-neurobiological / philosophical-phenomenological / felt-encounter Montgomery+Scheel) + explicit **6-layer translation chain** (Athens theme → Translation IN → Biology → Reaction approximation → Chromatophore display → Translation OUT → Encounter) + compass framing. ~7,500 chars (was ~670).

3. **`voice_config.editorial_rationale`** — preserved operator-written first paragraph byte-identical; added explicit 6-layer chain + compass scaffolding + twin-risks closing. ~2,250 → 5,500 chars.

4. **Pass 0b base template amendment** at `personas/flows/shared/prompts/pass_0b_non_human_organism.md` (this commit) — 6 surgical edits making the template **compass-permissive** (both precautionary AND phenomenologically-permissive postures supported; voice_config.editorial_rationale determines which). Header anti-anthropomorphisation paragraph reframed as posture-conditional; verb-discipline-as-banned-language reframed as craft-choice with debates surfaced; precautionary epistemic frame reframed as posture-conditional; popular-but-unreliable corpus framing reframed as two-registers (felt-encounter vs anthropomorphic); Continental philosophy demoted from foundational to one-strand; CARE Principles reframed from binding-guardrails to citation-discipline; §6 corpus question reframed as three-register-set (technical / philosophical / felt-encounter). **Architectural fix that benefits all future non-human-organism voice rebuilds (Whanganui especially).**

5. **Phase 0.5 v3.1** auto-generated 6 DR prompts from amended template + 6-layer voice_config. Compass framing partially propagated via Pass 0b's tailoring layer (voice-specific follow-up questions inherit compass scaffolding; underlying template-rendered questions also amended).

6. **Manual TAILORING ORIENTATION preamble** added to each of the 6 octopus DR prompts (after section heading, before voice-specific questions). Surfaces the full 6-layer chain + compass scaffolding + twin-risks at every section paste. ~3000 chars per prompt. **Octopus DR prompts now have 11-14 compass+6-layer markers per section** (vs 0-7 in surgical_v1, 0-2 in v2 auto-generated, 0-7 in v3 template-amended-only).

**Status:** Octopus compass rebuild ready for operator's claude.ai DR sessions. Each section ~30 min wall = ~3hr operator wall total. After all 6 saved → cache-invalidate from Pass 1.1 → re-fire pipeline.

**Backup snapshots preserved:**
- `voices/octopus_pre_compass_rebuild_2026-05-01/` (full athens-2026 shipped state)
- `voices/octopus/01_research/03_dr_prompts.surgical_v1/` (manual surgical edits)
- `voices/octopus/01_research/03_dr_prompts.v2_partial/` (auto-generated before §6 amendment)
- `voices/octopus/01_research/01_perplexity_dossier.pre_6layer.json` + `02_gemini_broad_scan.pre_6layer.json` (research outputs from before voice_config 6-layer rewrite)

---

## What this session landed (2026-05-02)

**Code-repo commits (this commit):**
- Pass 0b template amendment (`pass_0b_non_human_organism.md`) — 6 surgical edits + §6 amendment making template compass-permissive while preserving precautionary-posture support
- voices/ONBOARDING DO-list addition: interrogate Pass 0a review_doc framings (committed earlier `1c83034`)
- voices/HANDOFF.md (this doc) + voices/OPEN_ITEMS.md updates

**No athens-2026 changes this session.** Octopus rebuild stays in current-tests until verified.

**4 voices' Pass 0a + Phase 0.5 fired in current-tests sandbox:**
- Octopus (rebuild — full compass framework)
- Arendt (clean Pass 0a, voice_mode=philosophical, DR prompts ready)
- Lovelace (Pass 0a clean, Phase 0.5 retry pending Gemini outage)
- Marley (Pass 0a, voice_mode flipped observational → narratival, DR prompts ready)

---

## What's in flight / open at session end

### Operator wall (claude.ai DR sessions — biggest time investment)

1. **Octopus 6 DR sessions** — paste each section prompt into claude.ai (Opus 4.7 + Extended Thinking + Deep Research), save outputs to `voices/octopus/01_research/04_dr_dossier/`. ~3hr operator wall. Highest priority — completes the rebuild.
2. **Arendt 6 DR sessions** — same pattern, ~3hr.
3. **Marley 6 DR sessions** — same pattern, ~3hr (note voice_mode=narratival; lyrics_patterns_only corpus_constraint).
4. **Lovelace 6 DR sessions** — pending Phase 0.5 completion when Gemini recovers.

These can be parallelized across browser tabs (operator-side parallelism unlimited).

### Operator-decision pending (carried from 2026-05-01)

5. **Plato 3 surgical patches** for dramatist-vs-speaker collision. Drafted in HANDOFF_2026_04_28 §13, never applied. ~10 min. See OPEN_ITEMS.md §9.
6. **Mediated-voice prompt clarification** — land before Scheherazade's Pass 0a, or plan for surgical patches at her gate. See OPEN_ITEMS.md §9.
7. **Plato thinking-on re-run experiment** ($5, 30 min). See OPEN_ITEMS.md §5.
8. **9480d3a revert hypothesis re-evaluation** — connected to FU#56. See OPEN_ITEMS.md §5.

### Octopus rebuild verification (after operator runs DR sessions)

9. **Run pipeline on rebuilt Octopus** — cache-invalidate from Pass 1.1, fire `run_persona_pipeline.py "Octopus" --project /path/to/current-tests`
10. **Verify chat-test artifact** matches experiment-in-mind voice + chromatophore display engine integration (medium + technical_capabilities should prescribe the JSON parameter emission)
11. **Promote rebuilt Octopus to athens-2026** — copy `current-tests/voices/octopus/` → `athens-2026/voices/octopus/` (overwrite shipped state). Athens-2026 commit + push.
12. **Document rebuild lessons** in voices/ONBOARDING — twin-risks calibration, compass-permissive template architecture

### Whanganui-relevant

13. **Whanganui rebuild design** — when she eventually builds, use the compass-permissive template (now in place) + voice_config.editorial_rationale that explicitly chooses precautionary OR phenomenologically-permissive posture. Whanganui has same "non-human + no-first-person-source" structural challenge as Octopus; choose posture deliberately.

### Out of voices/ but related

14. **FU#62 spec-update vs implement** — Voice Pipeline validation regen-on-flag spec/impl gap (recommendation: spec-update path B). Operator decision.
15. **`voice-pipeline-v2.1-align-revert` → `main` merge** — operator decision when.

---

## What I would do next session in priority order

1. **Run Octopus DR sessions** in claude.ai (operator wall ~3hr) using the compass-aligned prompts in current-tests
2. **Optionally: run Arendt + Marley DR sessions** in parallel browser tabs (operator wall ~6hr more)
3. **After Octopus DR done: cache-invalidate + re-fire pipeline + chat-test the rebuilt voice + promote to athens-2026 if good**
4. **Lovelace Phase 0.5 retry** — wakeup scheduled for Gemini recovery; complete when ready
5. **Plato 3 surgical patches** if there's spare time

---

## Reading order for next session

1. `voices/ONBOARDING.md` (steady-state how-to + Pass 0a interrogation discipline, ~10 min)
2. `voices/HANDOFF.md` — this doc (~5 min, especially §"Octopus compass rebuild")
3. `voices/OPEN_ITEMS.md` (status snapshot, ~10 min)

That's ~25 min to working knowledge for picking up voice-build work cold.

---

## When this doc goes stale

Update `HANDOFF.md` at the end of every voice-build session — it's the session-snapshot, not the steady-state. Roll the prior session's HANDOFF into the next session's by dating the doc and adding a "supersedes prior HANDOFF" note at top.

If you want a versioned history, save prior HANDOFFs as `HANDOFF_<DATE>.md` in `_workspace/archive/voices_consolidation_<date>/` (per the umbrella `<topic>_consolidation_<date>/` convention; first instance: `voices_consolidation_2026_05_01/`).
