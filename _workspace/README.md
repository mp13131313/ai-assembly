# _workspace

Out of scope for code reviews and VM deploys. Two subdirectories:

## planning/

Forward-looking design documents for work not yet built. Promoted into
`docs/` when the work lands; deleted if abandoned.

- `REBUILD_PLAN.md` — single source of truth for the Phase B persona
  pipeline rewrite. Contains the 9 locked architectural decisions
  (PB#1–9), all phase-by-phase task lists, Boddice integration, Pass 7a
  multi-family validation lock, test material, and bootstrap pointers.
  The original `ARCHITECTURE_NEXT_PHASE_HANDOFF.md` was merged in here
  on 2026-04-19 and archived under
  `archive/session-artifacts/ARCHITECTURE_NEXT_PHASE_HANDOFF_2026_04_18.md`
  for provenance.

## archive/

Historical detritus — executed fix plans, prior session artifacts,
superseded specs, pipeline run artifacts. **Eligible for deletion**
once you trust the current state has absorbed their content. See the
pruning rule in the most recent fresh-review session artifact
(`archive/session-artifacts/`).

### Subdirectories

- `specs/` — two specs marked STALE in `docs/README.md`
  (`Architecture_v1`, `Infrastructure_Setup`)
- `fix-plans/` — executed SONNET_EXECUTION_PLAN series, delta docs,
  walkthrough fixes, implementation audits, draft fix docs
- `session-artifacts/` — prior session handoffs and review reports
- `runs/` — pipeline run artifacts (`runtime/` side and `personas/`
  side)

### Pruning rule

Review this tree at two natural checkpoints:

1. After each successful Athens run — delete run artifacts older than
   the current conference.
2. After each codebase milestone (Phase B lands, Voice Pipeline ships,
   Athens concludes) — delete fix plans whose target state is now the
   current codebase.

If you can't name what `archive/foo.md` describes that isn't already
in `docs/` or code, delete it.
