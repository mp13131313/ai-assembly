# _workspace

Out of scope for code reviews and VM deploys. Two subdirectories:

## planning/

Active forward-looking design + workstream trackers. The substantive
content lives in two workstream subfolders; the root holds the index +
the frozen follow-up ledger.

- **`ONBOARDING.md`** — thin index: the two-workstream split, cross-cutting
  DON'Ts, and calibration. **Start here.**
- **`FOLLOW_UPS.md`** — FROZEN historical ledger of FU#1–62 (no new
  entries; new items go in the subfolder OPEN_ITEMS).
- **`runtime/`** — runtime-pipeline workstream: `ONBOARDING.md` (durable),
  `OPEN_ITEMS.md` (authoritative open items, A–E sections), and the latest
  dated `HANDOFF_*.md`. Plus active design specs not yet built
  (e.g. the vatican-2026 annotated-encyclical spec).
- **`voices/`** — persona-card workstream: same `{ONBOARDING, OPEN_ITEMS,
  HANDOFF}` shape, plus active operator-refinement docs.

Design specs are promoted into `docs/` when the work lands and archived
once superseded; superseded handoffs move to `archive/`.

## archive/

Historical detritus — executed fix plans, prior session handoffs,
superseded specs, consolidation snapshots. **Eligible for deletion** once
you trust the current state has absorbed their content.

### Subdirectories

- `fix-plans/` — executed SONNET_EXECUTION_PLAN series, delta docs,
  implementation audits.
- `runtime-handoffs/` — superseded dated runtime handoffs + dryrun plans
  (the "keep only the latest in `planning/runtime/`" rule sends them here).
- `session-artifacts/` — prior session handoffs, memos, review reports.
- `planning_2026_04_consolidation/` — the April planning consolidation,
  including the historical `REBUILD_PLAN.md` (Phase B persona-pipeline
  rewrite; superseded by the shipped v4 pipeline).
- `voices_consolidation_2026_05_01/` + `runtime_consolidation_2026_05_01/`
  — the 2026-05-01 two-workstream split snapshots.
- `reference-cards/` — archived reference card material.
- `specs/` — two specs marked STALE in `docs/README.md`
  (`Architecture_v1`, `Infrastructure_Setup`).

Note: pipeline RUN data (persona + runtime runs) lives at the umbrella
level under `~/Desktop/AI Assembly/archive/runs/`, NOT here (Tier 3).

### Pruning rule

Review this tree at two natural checkpoints:

1. After each successful Athens run — delete run artifacts older than the
   current conference.
2. After each codebase milestone (Phase B lands, Voice Pipeline ships,
   Athens concludes) — delete fix plans whose target state is now the
   current codebase.

If you can't name what `archive/foo.md` describes that isn't already in
`docs/` or code, delete it.
