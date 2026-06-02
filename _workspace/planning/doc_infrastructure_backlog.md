# Doc-infrastructure backlog

Future work on the **doc + filesystem architecture itself** — not the
pipeline, not the voices. These items were considered + intentionally
deferred during the 2026-06-01 doc/filesystem sweep (commits `9eb5f49`,
`b4fc377`, `857b928`, `69d0f1f`, `cc7cad9`). Filed here so they're
discoverable but don't bloat the runtime/voices OPEN_ITEMS trackers.

**None of these block anything.** Each has a stated trigger condition for
when revisiting becomes worthwhile.

---

## I. Deferred doc-architecture reshapes

### I.1 — Tier 3: persona runner consolidation

**Status:** deferred until persona pipeline rebuild
**Effort:** 1–2 hr
**Trigger:** start of the planned v3.10 → next persona rebuild (per
operator's standing memory: *"Persona Pipeline rebuild planned — Phase B
chunked-JSON architecture; review is prep for rewrite, not patch list"*).
Doing the runner consolidation as part of the rebuild = one disruption.
Doing it separately = two disruptions.

**What:** move `personas/run_*.py` (14 files at root) into
`personas/runners/`, drop `run_` prefix, fix naming inconsistencies
(`run_pass0a_*` vs `run_pass_0b_*` vs `run_pass_1_1.py` — different
delimiters). Restore symmetry with `runtime/` (which has zero Python at
root).

**Why deferred:** breaks every shell invocation operator has memorized,
every batch script (`scripts/batch_pre_dr.sh`,
`scripts/run_pipeline_batch.sh`), every Claude session prompt that
documents how to run the pipeline. **High disruption.** A rebuild would
restructure the runners anyway; doing this in isolation pays the cost
twice.

### I.2 — Tier 5: `_workspace/` → `planning/` rename

**Status:** skipped (cost > benefit at current scale)
**Effort:** 1–2 hr
**Trigger:** if the project shape changes (multi-collaborator,
significantly larger codebase, public docs site).

**What:** rename `_workspace/` to a standard convention name like
`planning/` at the code repo root.

**Why skipped:** `_workspace/` is non-standard (industry uses
`planning/`, `internal/`, `meta/`), but every internal cross-reference
(~40+), commit-message convention, Claude session prompt, and the
operator's muscle memory all assume `_workspace/`. The rename is
aesthetic; the cost is real. At single-operator scale: negative ROI.

### I.3 — Option C: full Diátaxis-style reshape

**Status:** skipped (over-engineered for current scale)
**Effort:** 2–3 days
**Trigger:** project grows into multi-collaborator + multiple-event
maintenance (3+ events, 2+ contributors per workstream).

**What:** restructure `docs/` into `docs/{about,pipelines,persona,deployment,research}/`
subdirs; drop the `AI_Assembly_` filename prefix; add an `operations/`
top-level folder consolidating how-to content; potentially fold parts
of `_workspace/planning/` into a `process/` folder.

**Why skipped:** the architecture is correct (Diátaxis is real best
practice for multi-audience docs), but the benefit accrues to an
audience that doesn't currently exist (collaborators with first-time
onboarding needs). The 30+ file moves + 50+ cross-reference updates +
breaking search-engine continuity for the `AI_Assembly_*` names + every
saved Claude prompt — pay cost now, get benefit later if ever. Negative
ROI at solo-operator scale.

---

## II. Operator decision pending

### II.1 — Opus 4.6 vs 4.7 for DR sections

**Status:** half the project says one thing, half says the other
**Effort to resolve:** 10 min decision + 15-30 min execution

The split:
- `voices/ONBOARDING.md` DOs + recent root/personas READMEs (post-2026-06-01 drift sweep): *"use Opus 4.7 across all 6 DR sections"* (`§1-§5 use 4.6` flagged as stale)
- `docs/AI_Assembly_Persona_Pipeline_v4.md` (canonical pipeline spec): *"§1-§5 use Opus 4.6, §6 uses Opus 4.7"*
- `personas/flows/shared/prompts/pass_0a_voice_config.md` (the actual prompt rendered into operator's DR sessions): *"§1-§5 use Claude Opus 4.6 + Extended Thinking; §6 uses Claude Opus 4.7"*
- `personas/flows/shared/prompts/pass_0b_header.md` (Pass 0b header): same

**What to decide:** which guidance is canonical?

- **(a) Standardize on 4.7 across all 6** — operator's stated preference
  in voices/ONBOARDING DOs. Update the v4 spec + Pass 0a/0b prompts.
- **(b) Revert to 4.6-for-§1-§5** — what the prompts the operator
  actually sees say. Revert voices/ONBOARDING + recent README updates.

Either is fine; what isn't fine is the split. The prompts are
load-bearing — they're what the operator copy-pastes into claude.ai
sessions — so whichever way you go, **align the prompts with the
guidance.**

---

## III. Filesystem hygiene (small wins not taken)

These are real but the cost-per-win didn't justify doing them in the
2026-06-01 sweep.

### III.1 — Umbrella archive subdirs still using bare-noun convention

Per the convention doc, every snapshot subdir should be
`YYYY-MM-DD_descriptive_name/`. Renamed during the sweep:
`athens-2026/` → `2026-04-27_athens-2026_first_run_pre_v4/`;
`personas_prompts_PRE_582af96_REVERT_*` → `2026-04-28_personas_prompts_pre_revert/`.

**Still bare-noun:**
- `arch_03_baseline_snapshot/` — could be `2026-04-22_arch_03_baseline_snapshot/`
- `dostoevsky_sandbox/` — could be `2026-04-XX_dostoevsky_sandbox_pre_phase_b/` (date needed)
- `phase-l-plato/` and `phase-l-dostoevsky/` — could be `2026-04-XX_phase_l_{plato,dostoevsky}_dormant/`
- `athens-2026_octopus_pre_compass_promotion_2026-05-02/` — date is suffix, not prefix; should be `2026-05-02_athens_2026_octopus_pre_compass_promotion/`

**Trigger:** next umbrella-archive review (e.g. when revisiting the
late-2026 deletion review for `2026-05-29-history-rewrite/`).

### III.2 — `.pytest_cache/` at code repo root

**Status:** present at code/.pytest_cache/ (gitignored, so not in git, but on disk)
**What:** leftover from running `pytest` at the repo root rather than
inside `runtime/` or `personas/`. Each subtree has its own
`.pytest_cache/` already (`runtime/.pytest_cache/`, `personas/.pytest_cache/`).
**Trigger:** next time anyone notices and `rm -rf code/.pytest_cache/`.
Zero risk.

### III.3 — `runtime/flows/` asymmetry

Some flows are flat (`transcription_flow.py`, `researcher_flow.py`,
`provocateur_flow.py`, `publish_flow.py`); others are subdirs
(`voice/`, `editor/`). Readers must learn two patterns.

**Two ways to fix:**
- Make all flows subdirs (`flows/transcription/transcription_flow.py`)
  — symmetric but adds ceremony to small flows.
- Document the rule (single-module flows = flat `.py`; multi-module
  flows = subdir) in `runtime/README.md` or `runtime/flows/README.md`
  — preserves the existing shape, accepts the asymmetry as deliberate.

**Trigger:** next time a flow grows from single-file to multi-module
(natural conversion moment) or a new flow lands.

### III.4 — Two `deploy/` subdirs

`runtime/scripts/deploy/` and `runtime/ingest/deploy/` both exist.
Possibly serving different purposes; possibly overlapping. Not audited.

**Trigger:** next time the deployment workflow gets revisited (e.g.
provisioning the Hetzner VM per OPEN_ITEMS B10).

### III.5 — `runtime/flows/voice/README.md` is still long (~205 lines)

Not trimmed in the 2026-06-01 sub-tree-README sweep because it's a
code-internal reference (file-by-file commentary on `voice/*.py`), not a
sub-tree onboarding doc. Different role. Could still benefit from
trimming but lower priority than top-level READMEs.

**Trigger:** if a future Claude session reading code finds the doc
mostly-stale relative to the code, or if voice/ gets restructured (per
the persona-rebuild forcing function in §I.1).

---

## IV. Doc consolidation

### IV.1 — Spec-doc preamble version-history → CHANGELOG.md

**Status:** identified as the right move during the 2026-06-01 sweep but
not executed
**Effort:** 1–2 hr

Several `docs/AI_Assembly_*.md` carry preamble version-history
sections (e.g., `AI_Assembly_Persona_Pipeline_v4.md` has a "Changelog:
v3.10 → v4.0" table; `AI_Assembly_Editor_Pipeline.md` has v1→v2
refinement notes; `AI_Assembly_Voice_Pipeline.md` has a v2.1 alignment
note). These should migrate to `CHANGELOG.md` (or be referenced from
it), so spec docs stay focused on "what the system is" rather than
"what changed and when."

**Why deferred:** mechanical work; doesn't block anything; the existing
preambles aren't wrong, they're just duplicative of what CHANGELOG.md
now owns.

**Trigger:** next time someone edits a spec doc — they should drop the
preamble version-history during the edit, pointing at CHANGELOG.

### IV.2 — Archived `CURRENT_STATE_2026-04-27.md` §5.x sections still cited

The archive doc captured §5.16–5.28 architectural rationale that's
referenced from `docs/AI_Assembly_Persona_Pipeline_v4.md`,
`docs/AI_Assembly_Voice_Pipeline.md`, etc. These references work today
(the archive is available), but the long-term right move is to migrate
the relevant §5.x content INTO the spec docs themselves, so the archive
becomes truly cold storage.

**Trigger:** next time a spec doc is being substantively edited — pull
the §5.x rationale it cites into the spec doc inline.

---

## V. Microsite-driven future moves

### V.1 — Octopus chromatophore assets

The Octopus voice's render artifact (now at
`runtime/assets/octopus_chromatophore/`) is currently in the code repo
but designed to be loaded by the microsite — which is **a separate
project (per OPEN_ITEMS B2, not built).** When the microsite lands:

- `octopus_artifact_finaldraft.jsx` should be consumed by the microsite
  (could live in the microsite repo OR continue to be served from
  here as a library asset)
- `octopus_artifact_finaldraft.html` (standalone runnable) could be
  served separately for preview / Substack-embed
- Design notes (`AI_Assembly_Chromatophore_Display_Engine.md`,
  `render_decisions_*.md`, `reviewer_notes_*.md`,
  `chat_test_artifact_*.md`) should stay in the code repo's docs/design/
  or runtime/assets/ — they describe the engine, not the artifact

**Trigger:** when the microsite is built (OPEN_ITEMS B2).

### V.2 — Future per-voice render assets

If post-Athens render work for Marley (→ Suno per OPEN_ITEMS B7) or
other voices produces similar asset bundles, the right home is
`runtime/assets/<voice>/` matching the Octopus pattern. Or in the
microsite repo, depending on the B2 architecture.

**Trigger:** when Marley → Suno work happens (or any other per-voice
render workstream).

---

## VI. Archive deletion timing

Captured already in the umbrella archive README and the
`2026-05-29-history-rewrite/README.md`, but consolidating here for
discoverability:

| Archive subdir | Review trigger |
|---|---|
| `~/Desktop/AI Assembly/archive/2026-05-29-history-rewrite/` | **late 2026** — ~6 months post-rewrite, when confidence no subtle data corruption surfaces |
| `~/Desktop/AI Assembly/archive/arch_03_baseline_snapshot/` | Next persona-pipeline rebuild (per §I.1) — natural point to compare-and-delete |
| `~/Desktop/AI Assembly/archive/sentinel_baselines/` | Same — rebuild forcing function |
| `~/Desktop/AI Assembly/archive/phase-l-*/` | Could delete once voices stable through ≥1 more event (Athens already shipped — vatican-2026 would close it) |
| `~/Desktop/AI Assembly/archive/2026-04-27_athens-2026_first_run_pre_v4/` | Same as phase-l — could delete after vatican-2026 if confidence holds |
| `code/_workspace/archive/*` | Per `_workspace/README.md` pruning rule: review at each codebase milestone; delete if function fully absorbed |

---

## How this doc stays current

- **Adding items:** when a future-work item is intentionally deferred
  during a session, file it here with the same structure (status,
  effort, trigger condition).
- **Removing items:** when an item gets done, delete the entry and add
  a CHANGELOG.md note pointing at the resolving commit. (Don't accumulate
  "✅ DONE" entries — that's what CHANGELOG.md is for.)
- **When this doc empties:** delete it. The presence of this file is a
  signal that doc-infrastructure work is pending; an empty doc is
  noise.
