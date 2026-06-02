# CHANGELOG

Time-stamped history of project state changes. The current state lives in
[`STATE.md`](STATE.md); this doc records what changed and when.

Format: dates descending. Entries are coarse (architectural shifts,
production milestones, history rewrites) — fine-grained commit-by-commit
history lives in `git log`.

---

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
