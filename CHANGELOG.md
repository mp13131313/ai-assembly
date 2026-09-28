# CHANGELOG

Time-stamped history of project state changes. The current state lives in
[`STATE.md`](STATE.md); this doc records what changed and when.

Format: dates descending. Entries are coarse (architectural shifts,
production milestones, history rewrites) — fine-grained commit-by-commit
history lives in `git log`.

---

## 2026-09-28

### Published record repaired; central model config

- **athens-2026 published record repaired and pushed** (`0b2af19`):
  - **Voice names (C53):** 99 fields in 49 files carried each voice card's long identity opening ("I am Augusta Ada King…") as the display name. Restamped to "Voice of X" (headnotes: "the Voice of X") with `runtime/scripts/restamp_published_voice_names.py`. Prose untouched; no model calls.
  - **Voice indexes (C50):** Night 1's listed 3 of 10 voices, Night 2's 1 of 10. Both rebuilt from disk.
  - **Per-theme files (C51):** 24 generated after fixing the builder, which had never worked (`4b7ac0d`).
  - **data_views** regenerated.
- **Dossier-index writers** (editor + publish_flow) now merge instead of clobbering each other (PLAN 0.1.2, `3871e11`).
- **`model_routing.json`** (C63, done): every LLM step in both pipelines (41) now reads its model, thinking mode and effort from this one file. It refuses unsafe setups and keeps the legacy env overrides working.
  - Validator ladders route each rung by vendor rather than position. The runtime Step-1 ladder's gpt-4.x fallback rungs, which could only fail, now work.
  - `docs/LLM_CALL_INVENTORY.md` regenerated; the specs point at the file. Two specs had stated wrong model defaults (Voice, Researcher) and were corrected.
- **Operator decisions:**
  - Family of forms is exempt from the net-complexity gate (conditional).
  - The Assembly invariant is the loose four-part version (PRODUCT §11.5).
  - The hub is the active direction, built on the operator's own intent; the gate is amended so the operator's decision to build counts.
  - Stage 4 approved, deferred until the current work is done.

## 2026-09-27

### Phase 0 fixes (branch `phase0-fixes`)

- **Runtime:**
  - C49: speaker-ID decode failure now degrades to an auto-passthrough.
  - C50: night index rebuilt from disk.
  - C53: voice-name corruption fixed at three code surfaces.
  - C54: orchestrator dispatch goes through `infer_state`.
  - C55: event-neutral validator prompts.
  - C56: editor `corpus_metadata` strip.
  - C58: `sys.executable`.
  - C46: editor dossier index rebuilt from disk.
- **Persona pipeline:**
  - §32.1: bracket-strip reload.
  - §32.2: 7a-FINAL field.
  - §32.3: dead prompts deleted.
  - §32.5: count drifts.
- **`docs/LLM_CALL_INVENTORY.md`** regenerated from code. It adds the Voice and Editor pipelines and a migration section.
- **C62 model audit:** the pinned models are still live. Sonnet 5 would break Pass 7-pre; Opus 5.5 would lower the default effort.
- **Planning corrections:**
  - Per-voice temperature isn't available on current Anthropic models (vatican spec §5, PLAN 2.2).
  - The direction of the validation test in PRODUCT §8 is fixed.
- **Governance draft** added (PRODUCT §11).

## 2026-06-12 → 2026-06-14

### Post-Athens planning

- **Roadmap** `_workspace/planning/PLAN_2026_06_12_post_athens_roadmap.md`: a sequencing layer over the two trackers.
- **Line-by-line code read** filed as runtime C53–C58 and voices §32–§33.
- **FU#55 family of forms:** BUILD.
- **Agentic-architecture backlog:** runtime Section H, voices §34.
- **Product direction:** the governed voice hub (`_workspace/planning/PRODUCT_assembly_hub.md`).

## 2026-06-01

### Doc-architecture sweep

- **State centralized in `STATE.md`.** Previously the same facts (Athens
  production results, deployment_context rules, voice-build state, v4.1
  follow-ups) lived in CLAUDE.md state block + STATE.md pointer + root
  README cross-repo paragraph. Three docs needed updating in sync;
  drift accumulated. Now: STATE.md is the single authoritative source;
  CLAUDE.md and root README point at it.
- **Sub-tree READMEs trimmed** to pointer-density (~50 lines). Drops
  duplicated setup, pipeline overview, run examples. Each sub-tree
  README now says "what this is + where the canonical sources are."
- **CHANGELOG.md created** (this file). Spec docs no longer need to
  accumulate preamble version-history.
- **Docs drift sweep** (preceding commit `4f9f87f`): archived stale
  `docs/CURRENT_STATE.md` (was 60% wrong post-Athens), refreshed
  `docs/README.md` staleness index, rewrote runtime/README.md to reflect
  6 stages + orchestrator, fixed dead `REBUILD_PLAN.md` references,
  retired stale "Opus 4.6 for §1-§5" guidance in operator-facing READMEs
  (split with prompts + pipeline spec remains — surfaced as open question).

### Filesystem cleanup

- **History-rewrite artifacts moved to `~/Desktop/AI Assembly/archive/2026-05-29-history-rewrite/`**
  with a README explaining what each file is, when to consult, and when
  (late 2026) to revisit deletion. Was cluttering the umbrella root.
- **Tier-2 mislocations fixed:** `docs/runtime_assets/octopus_chromatophore/`
  → `runtime/assets/octopus_chromatophore/` (was docs but is runtime
  asset code); `personas/HANDOFF.md` → `personas/CROSS_REPO_CONTRACT.md`
  (overloaded with session-handoff term); `docs/design/` surfaced in
  `docs/README.md`; `_workspace/archive/designer_package_2026-05-04.zip`
  removed (duplicate of unpacked dir, accidentally tracked in `4f9f87f`).
- **Tier-4 archive cleanup:**
  - `_workspace/archive/` loose files wrapped in dated subdirs:
    `CURRENT_STATE_2026-04-27.md` → `2026-04-27_current_state_snapshot/`;
    `DESIGNER_BRIEFING_2026-05-04.md` deleted (identical to copy inside
    `designer_package_2026-05-04/`); `MEMO_2026_05_03_editor_flow_*.md`
    → `2026-05-03_editor_flow_memo/`.
  - Umbrella archive `athens-2026/` renamed to
    `2026-04-27_athens-2026_first_run_pre_v4/` (was clashing with live
    project name).
  - Umbrella archive `personas_prompts_PRE_582af96_REVERT_20260428_231640/`
    renamed to `2026-04-28_personas_prompts_pre_revert/` (was using dead
    SHA + glued date).
  - Umbrella archive gained a `README.md` cataloging every subdir.
- **`feature/voice-deployment-context` retired as superseded** (C48
  option-b). Branch deleted; design captured at
  `_workspace/planning/runtime/DESIGN_voice_deployment_context.md`; code
  preserved at tag `archive/voice-deployment-context-2026-05-05` (commit
  `248300c`; original implementation `ec77a3c`). Dryrun verdict (`6/10
  voices shifted theme focus, +348w net`) was positive but redirected
  to Provocateur + Editor stages (`cbcdf82`, `0f751b7`, `fda8091`,
  `7e99c63`).
- **`feature/editor-deployment-context` deleted** (fully merged, redundant).

---

## 2026-05-29

### Post-Athens history rewrite + force-push

- **~680 commits re-authored** from `AI Sandbox <peschelero@gmail.com>`
  to `Matthias Peschel <276296109+mp13131313@users.noreply.github.com>`
  via `git filter-branch --env-filter`. Author dates preserved. Both
  repos force-pushed. Fix: missing GitHub contributions on the operator's
  public profile. Pre-rewrite backups + hash-remap TSVs at
  `~/Desktop/AI Assembly/archive/2026-05-29-history-rewrite/`.
- **Post-rewrite SHA-citation sweep** (`d80a0ac`) remapped ~530 stale
  hash citations across 21 planning docs.

### Athens publication finalized

- All three Athens nights pushed: Night 1 (`50d88e1` v2 + `dcaf7ce` v1),
  Night 2 (`9ad06ff`), Night 3 (`394914b`).
- 6 Night-3 voice pages republished after C50 surface (`nights/_index.json`
  clobbered by single-voice publish).
- `runs/` directory tracked on athens-2026 with audio excluded (~20MB).
- `EDITORIAL_ASSESSMENT.md` and `DATA_INVENTORY.md` written + published
  in athens-2026/published_artifacts/.

### Doc cleanup
- CLAUDE.md refreshed (625 → 535 lines) for post-Athens state.
- Superseded handoffs archived; new `STATE.md` entry-point created.

---

## 2026-05-11 — Athens Night 3 PUBLISHED (closing edition)

3 dossiers (lead = *THE BODY OFF THE LEDGER* — Lovelace + Marley +
Dostoevsky) + 10 voice pages. Final-night discipline rules: closing-
edition AWARENESS not REGISTER; carry voice's own closing register where
authored, don't impose closure where not. Whanganui HOLD = C42 validator
misfire (not content defect) → operator-released.

## 2026-05-09 — Athens Night 2 PUBLISHED

5 dossiers (lead = *WHOSE MOUTH IS MOVING*) + 10 voice pages. Night-1
discipline rules carried forward. Wifi-drop mid-clustering → `.fn()`
bypass workaround for Prefect task wrapper.

## 2026-05-08 — Athens Night 1 PUBLISHED

5 dossiers (lead = *WHO TEACHES THE TEACHERS*, theme_002 paideia) + 10
voice pages. Three editor fires (initial 7-voice → v2 voices-interleave
re-fire → v2.1 Marley + Whanganui single-dossier under sacred-grammar).
Three Night-1 discipline rules established: Provotypist anonymization +
voices-interleave + sacred-grammar discipline. v4.1 follow-ups filed
(C42–C47).

## 2026-05-07 — Athens Day 1 begins

Production pipeline fires live for the first time. Three reflection JSONs
land via vendor_intake; nine audio sessions transcribed. First voice run.

---

## 2026-05-05 — pre-Athens evening sprint

### Architectural updates (athens-2026 main)

- **Tim Leberecht (Assembly editor)** SHIPPED as 13th persona. Card at
  `athens-2026/editor/tim_leberecht/` (`9347743`). Runtime
  `EDITOR_CARD_SUBPATH` rename `claudia_pinchbeck` → `tim_leberecht`
  (`b266f51`). Earlier Claudia Pinchbeck DRAFT card DEPRECATED.
- All 10 `voice_temporal_stance.default` fields shifted to assembly-
  fiction (`3bcbef5`). (Note 2026-05-08: superseded by Gap-K AF-LEADS +
  operator-short-draft rewrite at `08a8253`.)
- Length-cap card surgery (Dostoevsky 350-750w, Hannah 350-750w, Octopus
  350-500w prose-channel front-loaded; `404838d`).
- Voice of Whanganui River v2 — witness-translator architectural
  restructure with `mediation_stance == "transmission_witness"` shipped
  (`c2a885b` + `3ccb1f9`).

### Voice-runtime deployment_context branch created (later retired)

`feature/voice-deployment-context` `ec77a3c` — 139 LOC injecting THE
GATHERING / THE PANEL / YOUR FELLOW VOICES / YOUR READERS blocks into
voice Step 1/2 system prefix. Dryrun verdict positive (6/10 voices
shifted theme focus, +348w net) but redirected to Provocateur + Editor
placements (Athens ran without voice-stage block). Branch retired
2026-06-01 — see top.

## 2026-05-04 — pre-Athens sacred-grammar architecture

Voice of Bob Marley v2 Option-3 restructure shipped. `corpus_constraint
== "lyrics_patterns_only"` conditional blocks in Pass 2 / Pass 4a / Pass
4b implementing SACRED-GRAMMAR DEPLOYMENT LIMIT + prose-yard-reasoning
artifact spec.

## 2026-05-03 — Editor Pipeline v2 shipped

`runtime/flows/editor_flow.py` + `runtime/flows/editor/*.py` (38 tests,
`fc5c2fb`). Tim Leberecht (initially placeholder Claudia Pinchbeck) as
13th Assembly member; per-theme dossier composition; one Opus 4.7 call
per dossier; marathon-distance issue numbering.

## 2026-05-02 — Voice Pipeline alignment + caching

Field-routing refactor (`ffad93f`); closing-prompts rewritten under
Haltung lens (`9e1c987`); Anthropic prompt caching enabled (`0a3ab9c`);
defensive `--night` check + automation orchestrator design (`373051e`);
overnight orchestrator + 22 trigger-path tests; Runtime Lifecycle + VM
Infrastructure specs landed.

## 2026-05-01 — two-workstream planning split + Tier 3 cleanup

`_workspace/planning/` reorganized into `runtime/` + `voices/`
subfolders with `{ONBOARDING, OPEN_ITEMS, HANDOFF}.md` per subfolder.
Phase B persona-pipeline rebuild SHIPPED as Persona Pipeline v4 (`"4.0"`
in code). FU#1–62 ledger frozen.

---

## 2026-04 — Phase B persona-pipeline rebuild

Pipeline v3.10 → v4. Chunked Pass 1.1–1.7 merge (arch-03 additive-merge
architecture). Phase B per-voice folder layout. Tier 3 code/project
separation (`PROJECT_ROOT` outside code repo). Pass 6.5-clean (FU#33 P1)
+ chunked Pass 7-pre (FU#2) + FU#13 linear patcher + FU#41 chat artifact
+ FU#49 universal patterns. v3.10 archived at `docs/_archive/`.

## 2026-04-26 — Plato shipped

First voice end-to-end. Chat-test validated. Pre-Athens persona pipeline
production-ready.

---

## How to extend this changelog

- Each significant state change gets an entry under a date heading.
- Coarse-grained; commit-level detail belongs in `git log`.
- When spec docs would carry version-history preambles, point at
  CHANGELOG instead.
- Dates descending. New entries at top of the relevant month section.
