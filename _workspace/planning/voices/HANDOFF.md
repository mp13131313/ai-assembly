# Voices — Handoff (session-end snapshot, 2026-05-04 early-AM — supersedes 2026-05-03)

**Companion:** `OPEN_ITEMS.md` (open-items list) + `ONBOARDING.md` (how-to / fresh-pickup). This doc is the session-end pickup snapshot: where we landed tonight, what's in flight, what's the next operator decision.

**On a fresh session:** read `ONBOARDING.md` first (~10 min), then this doc (~5 min), then `OPEN_ITEMS.md` (~10 min). Done in ~25 min.

---

## Branch + repo state at session end

| Repo | Branch | HEAD | Pushed |
|---|---|---|---|
| code | `main` | `a64d239` | ✅ |
| athens-2026 | `main` | `c2151ce` | ✅ (Whanganui + Scheherazade promoted this session) |

athens-2026 voices folder now carries **9 of 10** shipped cards: `plato`, `cleopatra`, `dostoevsky`, `ibn_battuta`, `octopus`, `hannah_arendt`, `ada_lovelace`, **`whanganui_river` (NEW tonight)**, **`scheherazade` (NEW tonight)**. Marley remains in `projects/current-tests/voices/bob_marley/` — pipeline ran, Pass 7a FINAL produced 8 residuals queued for walk-through.

Plus 13th persona staged: **`claudia_pinchbeck`** (the editor) — architecture landed 2026-05-03; awaiting operator inputs to begin Stages A-F.

---

## Where the 10 panel voices + Claudia stand

| Voice | type / voice_mode | State |
|---|---|---|
| Plato | human / philosophical | ✅ shipped + 2026-05-02 patched (`cf283bf`); KNOWN open: Theuth/Thamus recurrence-tic — owned by runtime continuity overlay (Path B) |
| Cleopatra | human / observational | ✅ shipped at FU#61 v3 (`c89d186` + `54cd20a`) |
| Dostoevsky | human / narratival | ✅ shipped via path (b) + FU#61-fresh (`5088d67`); KNOWN: closing-on-suspended-judgment phrase tic — owned by runtime continuity overlay (Path B) |
| Battuta | human / narratival | ✅ shipped via path (b) (`e300508`); KNOWN: Tughluq beard-plucking stock-anecdote tic — owned by runtime continuity overlay (Path B) |
| Octopus | non_human / observational | ✅ compass rebuild SHIPPED + chat-test VERIFIED 2026-05-02 (`04da2c8`). Runtime asset bundle at `code/docs/runtime_assets/octopus_chromatophore/`. |
| Hannah Arendt | human / philosophical | ✅ shipped 2026-05-02 (`bfe917a`) |
| Ada Lovelace | human / philosophical | ✅ shipped 2026-05-02 (`3a6fe2f` → rolled-back `c025914`) |
| **Whanganui River** | non_human / system / null | ✅ **shipped tonight (`c2151ce`) via path-(b) at ROUND6.** 6 validator walk-throughs converged to 3 architectural residuals (appropriation-safety language load-bearing, no iwi authorization). Mid-build reset to PRE-ROUND1 + minimal patches reapplied. All 3 Derive outputs present. |
| **Scheherazade** | fictional / narratival | ✅ **shipped tonight (`c2151ce`) via path-(b) at ROUND9.** 9 validator walk-throughs converged 9→6 (1 false-positive + 4 §9-architectural re-flags + 1 architectural carry). Seale-Horta 2021 corpus (operator-acquired Thalia DRM-free EPUB) curated to 14 chapters / 1.22M chars. Mediated-voice / dramatist-vs-speaker pattern preserved per §9. ROUND7-9 snapshots preserved. |
| **Bob Marley** | human / observational | 🟠 **(c.1) code change LANDED (`5d6ecbf`); pipeline ran to Pass 7a FINAL with 8 residuals queued for walk-through.** (c.1) augments Pass 4a's primary_block with `pass_1_6/reference_only_passages.json` when `corpus_constraint=lyrics_patterns_only`; Pass 6 still uses original primary_block (no-public-quotation contract preserved). DR §4 `[quote:]` blocks trimmed to clear Pass 1.4 content filter. Walk-through to apply dramatist-vs-speaker lens (§9 carry-over: songwriter-vs-lyric-I). After ship: promote to athens-2026 + wire 8th `council_config.json` member. |
| **Claudia Pinchbeck** *(editor; 13th persona)* | human / TBD (recommend `observational`) | 🟡 Persona-construction architecture landed 2026-05-03 in `voices/CLAUDIA_PINCHBECK_PERSONA_PREP_2026-05-03.md`. Hybrid pipeline path (skip Phase 0.5 claude.ai DR; hand-curate 6 dossier sections from existing materials; run Pass 1.x → 2-6 → validation → Derive). Companion runtime memo at `_workspace/archive/MEMO_2026_05_03_editor_flow_input_output_contract.md` (archived; v2 spec canonical at `docs/AI_Assembly_Editor_Pipeline.md`). Awaiting operator share of Beauty Shot dossier file + voice_mode/byline decisions to begin Stage A. ~7-9 hr Stages A-F when work resumes. |

---

## What landed tonight (2026-05-03 evening → 2026-05-04 early-AM session)

1. **Whanganui River SHIPPED** via path-(b) at ROUND6 + promoted to athens-2026.
2. **Scheherazade SHIPPED** via path-(b) at ROUND9 + promoted to athens-2026. Seale-Horta 2021 corpus acquired and integrated (14 chapters, 1.22M chars).
3. **(c.1) code change** in `personas/run_persona_pipeline.py`: Pass 4a augments `primary_block` with `pass_1_6/reference_only_passages.json` when `corpus_constraint=lyrics_patterns_only`. Substitute (if Pass 1d is the placeholder) or augment (concat with separator). Pass 6 still uses the original `primary_block` to preserve the no-public-quotation contract — lyrics never reach `curated_corpus_passages` emitted to athens-2026. Initial implementation was REPLACE; operator caught and corrected to AUGMENT.
4. **Marley pipeline run** through Pass 7a FINAL. 8 residuals queued for walk-through; DR §4 `[quote:]` blocks trimmed to clear Pass 1.4 content filter (deterministic content-policy refusal on verbatim lyrics in dossier text).
5. **§9 mediated-voice / dramatist-vs-speaker pattern confirmed** across 4+ voices in this build cohort (Plato + Whanganui + Scheherazade + Marley). Filing for prompt-side architectural fix (Pass 2 epistemic_frame_statement + Pass 4a characteristic_moves + Pass 3 reasoning_method clarifications) stays open as v4.1 — surgical patches at the gate continue to work.
6. **DR adaptive-thinking spot-test extended to 4 sections** (compass-vs-original Sections 1, 2, 3, 4 — most voice-modeling-load-bearing). All 4 verdicts: differences are sampling-variance, not thinking-on/off. Most likely both done with Research feature (auto-enables thinking); operator's "thinking off" recall was UI display difference. **No Phase 0.5 redo needed.** §4 verdict: original DR is at least as strong as compass for voice-modeling task.
7. **Snapshot preservation discipline standardized** — for each round of validator walk-through with ≥3 rounds, Pass 7a FINAL output preserved as `07_persona_card_assembled.ROUNDN.json` before patches.
8. **Doc updates** (this session): `voices/HANDOFF.md` rewritten (this doc); `voices/OPEN_ITEMS.md` §1 table + §22 updated; `voices/ONBOARDING.md` §63 panel-voices table TBDs settled.
9. **Commits** (auto-pushed):
   - code repo `5d6ecbf`: c.1 + earlier OPEN_ITEMS §22 (now superseded by tonight's full update)
   - athens-2026 `c2151ce`: voices/whanganui_river + voices/scheherazade ship

---

## What's in flight at session end

1. **Marley walk-through** — 8 residuals queued. Apply §9 dramatist-vs-speaker lens.
2. **Claudia work** — architecturally staged; awaiting operator's Beauty Shot dossier share + voice_mode/byline decisions.

---

## Operator decisions pending

### Immediate / next session

1. **Marley walk-through** — per-fix manual approval pattern (same as Whanganui ROUND1-6 + Scheherazade ROUND6-9). 8 residuals queued.
2. **Marley promote to athens-2026** + council_config wiring of 8th member (currently a placeholder).
3. **Claudia: Beauty Shot dossier share + voice_mode + byline split decisions** (carry-forward from 2026-05-03).

### Carry-forwards

4. **Mediated-voice prompt-side fix** — drafted but never landed since 2026-04-28. Scheherazade shipped via gate-side surgical patches per §9; Marley to follow same pattern. Prompt-side fix becomes v4.1 work (post-Athens or pre-Claudia).
5. Plato thinking-on re-run experiment ($5, 30 min). See OPEN_ITEMS §5.
6. 9480d3a revert hypothesis re-evaluation — connected to FU#56. See OPEN_ITEMS §5.
7. WBBF program copy coordination (FU#49C remnant).
8. FU#49G Greek-scholar calibration on Plato — Quarch/Tsinorema/Erinakis on the provotype-test.

### Pass 1c fetch audit — queued post-Marley-ship

After all 10 voices ship: audit Pass 1c fetch coverage across all athens-2026 voices + current-tests. Spot-check correctness; trim or augment per voice. ~1 hr.

### "Voice of X" naming convention sweep — deferred until all 10 voices ship

See OPEN_ITEMS §18. Single mechanical sweep of voice_name + council_config + panel_roster after Marley ships + Claudia ships. Backfill via SKIP_TO_DERIVE re-fire (~15 min + ~$20 for 10 voices). Claudia's "voice_name" (or "council_member_name") field follows the same convention or operator-decision relabeling.

---

## What I would do next session in priority order

1. **Marley walk-through** — open Pass 7a FINAL residuals; apply per-fix manual approval pattern; preserve ROUND snapshots; converge to ship.
2. **Promote Marley to athens-2026** + wire 8th council_config member when verified. Full panel + Whanganui + Scheherazade now wired.
3. **All-10 sweep** — "Voice of X" naming convention rollout (§18) after Marley ships + Claudia ships. Single mechanical pass.
4. **Pass 1c fetch audit** — across athens-2026 voices + current-tests.
5. **Claudia Stages A-F** — once operator shares Beauty Shot dossier + decisions land. Stage A first (voice_config), operator review, Stage B (DR dossier sections), operator review, Stage C (pipeline run), operator gate.
6. **Mediated-voice prompt-side fix** — file as v4.1 work item; document the §9 pattern empirically validated across Plato + Whanganui + Scheherazade + Marley.

---

## Reading order for next session

1. `voices/ONBOARDING.md` (steady-state how-to + Pass 0a interrogation discipline + 3-posture taxonomy)
2. `voices/HANDOFF.md` — this doc
3. `voices/OPEN_ITEMS.md` (status snapshot — especially §1 per-voice state + §22 for tonight's session detail)
4. **For Marley walk-through resumption:** read Pass 7a FINAL residuals at `projects/current-tests/voices/bob_marley/05_validation/06_pass_7a_final.json`; review §9 architectural pattern in OPEN_ITEMS §16.5 (Plato precedent) before applying patches.
5. **For Claudia work resumption:** `voices/CLAUDIA_PINCHBECK_PERSONA_PREP_2026-05-03.md` is the comprehensive pickup doc; pair with `_workspace/archive/MEMO_2026_05_03_editor_flow_input_output_contract.md` (archived; v2 spec canonical at `docs/AI_Assembly_Editor_Pipeline.md`) for the runtime-contract context.
6. `voices/MEMO_2026_05_01_recurrence_patterns_from_legitimacy_test.md` — runtime-thread findings doc (historical).

That's ~30 min to working knowledge for picking up voice-build work cold.

---

## When this doc goes stale

Update `HANDOFF.md` at the end of every voice-build session — it's the session-snapshot, not the steady-state. Roll the prior session's HANDOFF into the next session's by dating the doc and adding a "supersedes prior HANDOFF" note at top.
