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

**✅ Resolved 2026-09-28 (voices OPEN_ITEMS §36):** the DR model is now set in `model_routing.json` (manual steps, default Opus 4.7 for all six, per voices ONBOARDING's DO) and rendered into the prompts. Neither the spec nor the prompts name a model any more. The text below is history.

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

### III.6 — athens-2026: 301 tracked `voices/<slug>/_snapshots/` files with dead-SHA names

**Status:** ambiguous intent (deliberate audit trail vs accidental tracking)
**Effort to address:** depends on disposition — 0 hr if "leave as audit
trail"; 1–2 hr if "untrack + gitignore"; 2–3 hr if "rename to remove dead
SHAs"

**The setup:** In the **athens-2026** repo, 10 voices each have a
`voices/<slug>/_snapshots/` directory containing dated pre/post snapshot
subdirs from the late-April persona-pipeline build phase. These ARE
tracked in athens-2026 git (`_snapshots/` is **not** in athens-2026's
`.gitignore`). 301 tracked files across the 10 voices.

**The problem:** several snapshot directory names embed pre-rewrite SHAs
that died in the 2026-05-29 history rewrite:
- `voices/plato/_snapshots/PRE_582af96_REVERT_20260428_231725/`
- `voices/plato/_snapshots/POST_582af96_BASELINE_RUN_20260429_001715/`
- (and others — same SHA pattern as the umbrella archive's old
  `personas_prompts_PRE_582af96_REVERT_20260428_231640/` which we renamed)

Verified: `git log --all --oneline | grep 582af96` in athens-2026
returns nothing. The directory names preserve historical references that
no longer resolve.

**Three possible dispositions:**

- **(a) Leave** — accept the snapshots are tracked audit trail; the dead
  SHA in the dir name is a historical breadcrumb that doesn't need to
  resolve to a live commit. Cheapest. **Default if undecided.**
- **(b) Untrack + gitignore** — add `voices/*/_snapshots/` to
  `.gitignore`, `git rm --cached` the 301 tracked entries. Keeps files
  on disk for operator audit but removes from git. Cost: ~1-2 hr +
  large diff on athens-2026 main.
- **(c) Rename** — rename the dead-SHA subdirs to use the post-rewrite
  SHA equivalents (via the hash-remap TSVs we have) or drop the SHA
  entirely. Preserves audit trail in git + fixes the dead-ref names.
  Cost: ~2-3 hr; touches ~50+ rename operations.

**Why deferred:** no current consumer reads these snapshot directory
names. The dead SHAs are cosmetically wrong but don't break anything.
Operator decision required for which disposition fits.

**Trigger:** operator decision, or next time someone tries to follow a
snapshot SHA back to a commit and finds it dead.

### III.7 — athens-2026: 54 per-voice `.pre_*.json` operator snapshots on disk

**Status:** working as intended (per operator convention)
**Effort:** zero (no action needed)

For completeness: athens-2026 has 54 `.pre_*.json` operator-snapshot
files on disk inside `voices/<slug>/` subdirs. All correctly gitignored
per the `*.pre_*.json` rule in athens-2026's `.gitignore`. They're
filesystem clutter visible to anyone browsing the directory, but the
operator's stated convention (per `code/_workspace/planning/voices/ONBOARDING.md`)
preserves them locally as audit trail.

**Listed here for discoverability, not as work-to-do.** If a future
disposition decides to relocate them (e.g. into a per-voice
`_snapshots/` subdir matching the existing pattern, or a top-level
`_archive/operator_snapshots/`), that's filesystem hygiene; no git
impact.

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

---

## 2026-09-28 staleness sweep — findings (to fix)

First run of the WAYS_OF_WORKING §8 sweep, after the Phase 0 work landed without its spec updates (a §3.2 miss). 9 WRONG · 8 STALE · 2 HISTORICAL. Fix in this order:

| # | Doc · where | Problem | Fix | Sev. |
|---|---|---|---|---|
| 1 ✅ 2026-09-28 | `docs/AI_Assembly_Editor_Pipeline.md` L65, 90, 201, 243–301, 526, 547, 896 | Editor described as Claudia Pinchbeck, card path `editor/claudia_pinchbeck/` — it is Tim Leberecht (`tim_leberecht/`, `b266f51`) | Rewrite identity section + paths; Claudia only as a historical note | WRONG |
| 2 ✅ 2026-09-28 | same, L617–618 | Code sample `"the voice of " + council_member` — the exact C53 bug | Show the council_config lookup ("the " + "Voice of X") | WRONG |
| 3 ✅ 2026-09-28 | same, L135, 931–933 | "No editor pipeline-side index file is maintained" | Document the shared dossier index + the merge rule (C46, PLAN 0.1.2) | WRONG |
| 4 ✅ 2026-09-28 | `CLAUDE.md` L12 (+ L301, 317) | "no work in flight"; editor = Claudia; "Claudia's card pending" | Status one-liner → point at STATE.md; Tim | WRONG |
| 5 ✅ 2026-09-28 | `docs/AI_Assembly_Voice_Pipeline.md` L69, 575–585, 1183–1192 | Step-1 validation "Night 1 ON", opt-out `--skip-validation` — code is default OFF, opt-in `--enable-step1-validation` (C28) | Rewrite policy + CLI subsection | WRONG |
| 6 ✅ 2026-09-28 | `docs/AI_Assembly_Runtime_Lifecycle.md` L134–149, 142, 245–246 | Stage 6 editor "specified, not built"; Claudia card path | Editor built + ran all 3 nights; Tim path | WRONG |
| 7 ✅ 2026-09-28 (with C63) | `docs/AI_Assembly_Researcher_Pipeline.md` L624, 636 | Default model "claude-sonnet-4-6"; `CLUSTERING_MAX_TOKENS=40000` | Opus 4.7 default (now: `model_routing.json`); 64000 since 2026-05-08 | WRONG |
| 8 ✅ 2026-09-28 | `docs/AI_Assembly_Provocateur_Pipeline.md` L53, 156 | "12 parallel calls, one per council member" | 10 (dev_msc_test mentions of 12 are historical — keep) | WRONG |
| 9 ✅ 2026-09-28 | `README.md` (root) L127 | "both repos clean + pushed" | Point at STATE.md's branch section | WRONG |
| 10 ✅ 2026-09-28 (voices §36) | `docs/AI_Assembly_Persona_Pipeline_v4.md` L20, 195 | Opus 4.6 for DR §1–§5 (banned per ONBOARDING DON'T) — already tracked §II.1 above | Resolve §II.1 → **folded into voices OPEN_ITEMS §36** (2026-09-28: automate the DR step; model choice moves into `model_routing.json`) | WRONG (known) |
| 11 ✅ 2026-09-28 | `docs/AI_Assembly_Transcription_Pipeline.md` Step 3 | C49 decode-failure auto-passthrough + `speaker_id_auto_passthrough` flag not documented | Add a failure-mode subsection | STALE (gap) |
| 12 ✅ 2026-09-28 | `docs/README.md` L5 + table | "authoritative as of 2026-06-01", Editor/Lifecycle/etc. rated "Current" | Re-rate per this table; add a "last verified" column (WAYS_OF_WORKING §3.3) | STALE |
| 13 ✅ 2026-09-28 | `docs/AI_Assembly_Persona_Pipeline_v4.md` L356 | 7pre_citation prompts "eligible for deletion" | Deleted 2026-09-27 (`a10e08a`) | STALE |
| 14 ✅ 2026-09-28 | `docs/AI_Assembly_Persona_Card_v2.md` §H L106–120 | Family of forms "aspirational" | BUILD (FU#55) + gate-exempt (2026-09-28) | STALE |
| 15 ✅ 2026-09-28 | `CLAUDE.md` cross-repo handoff | "35 generated + 2 continuity" | 36 per CROSS_REPO_CONTRACT (+ `voice_temporal_stance`) | STALE |
| 16 ✅ 2026-09-28 | `_workspace/planning/runtime/ONBOARDING.md` branch section | "all work on main" | Label historical / point at STATE.md | STALE |
| 17 ✅ 2026-09-28 | vatican SPEC §8 table row | "✅ 3-tier per-voice temperature" | Mark infeasible on Anthropic models (§5 already corrected) | STALE |
| 18 ✅ 2026-09-28 | Editor Pipeline §card assembly L874–883 | Doesn't mention the corpus_metadata strip (C56) | One line | STALE |
| — ✅ 2026-09-28 | model config (C63) | Not mentioned in CLAUDE.md, README, runtime/README, docs/README, LLM_CALL_INVENTORY | Pointers added in CLAUDE.md, README, docs/README; inventory regenerated; specs point at the file (runtime/README had no model statements) | gap |
| 19 ✅ 2026-09-28 | `docs/AI_Assembly_Voice_Pipeline.md` cost + wall-time tables (~L68, 92, 342, 1256–1280) | Figures assume Step-1 validation ON (e.g. "Night 1 ~$20-40 (validation ON)"); it has been OFF since C28 | Recompute from the Athens run manifests | STALE |
| 20 ✅ 2026-09-28 | same | No section of its own for the Step-2 validator (C28b), which is the operator gate | Add a subsection (pillars, halt-on-flag, clearing, `--skip-step2-validation`) from `voice/step2_validation.py` | gap |
| 21 ✅ 2026-09-28 | `docs/AI_Assembly_Editor_Pipeline.md` Dossier Shape, Output Schema, Constraints #5–7, Validation Notes, Open Questions, See Also | ~38 mentions still name Claudia as current (byline "By Claudia Pinchbeck", "— C.P.", "Claudia emits…", dead link to `CLAUDIA_PINCHBECK_CARD_DRAFT_2026_05_02.md`). Some describe voice character that must be checked against Tim's card (athens-2026) | Check against Tim's card + published dossiers; rename or mark historical | WRONG |
| 22 ✅ 2026-09-28 | same, Page 2 table | "~750-word piece" contradicts the spec's own 350–500 / 500–700 word constraint | Check `editor_dossier.md` + published dossiers; fix | STALE |
| 23 ✅ 2026-09-28 | `docs/AI_Assembly_Runtime_Lifecycle.md` §1 + §8 | Editor wall time "~30 min" vs the Editor spec's "~5–10 min per night" | Check the Athens run manifests | STALE? |
| 24 ✅ 2026-09-28 | `docs/AI_Assembly_Editor_Pipeline.md` Dossier Shape (Pages 1–3 tables) + Output Schema (v2) | Describe fields that never shipped (`front_lead_teaser`, `in_brief_items`, `editors_note`, `theme_question`, `voice_abstracts[]`, `handoff_line`). The prompt and all 13 published dossiers use `kicker`, `headline`, `front_abstract`, `subline`, `pull_quote`, `theme_title_for_dossier`, `theme_abstract_for_dossier`, `headnotes`, `body_paragraphs` | Rewrite both sections from `editor_dossier.md` + the published dossiers (found 2026-09-28 while fixing #22). **Done:** spec v3. Residual, listed in the spec's v3 changelog: other sections still describe the pre-ship design (→ row #25), and 4 code/prompt defects (stray `**` in `body_paragraphs[0]`, `front_abstract` prompt contradiction, `publish_flow.py` reading dropped `issue_no`/`vol`, stale `voice_name` comments) — all four fixed 2026-09-28 in `9f415dd` (runtime OPEN_ITEMS C64; Athens data cleanup still open there); spec v3.2 follows | WRONG |
| 25 ✅ 2026-09-28 | `docs/AI_Assembly_Editor_Pipeline.md` Overview, Multi-night convention, What the Editor Pipeline Knows, Principles 1–4, 7, 8, The Paper, Stage 2 per-call inputs + closing prompt, Microsite Render Contract, Scope, Constraint 2, Defensive checks, Open Questions Q5–Q6 | Still described the pre-ship design after v3 (row #24): In Brief column, newspaper masthead + issue/volume numbers, v1/v2 per-call inputs, a 5-section closing prompt, artifacts "referenced, not embedded", a wrong colophon | Rewrite against the code (at `40c4d56`), `editor_dossier.md` and the 13 published dossiers + 3 Athens run dirs. **Done:** spec v3.1 (its changelog has the section-by-section table). Residual, listed there: Stage 1 routing, cost figures and the CLI/defensive-check list not re-verified; `--no-cache` flag not wired (→ runtime C65); 4 more prompt self-contradictions; no cache reads on Nights 2–3 (→ runtime C66) | WRONG |
| 26 ✅ 2026-09-28 | `CLAUDE.md` §"Where specs live", Editor bullet | Held state that went stale: "v2", masthead issue numbering (dropped `641e31d`), "closing prompt rewrite pending / still open (C57)" (shipped `4c7c315`), "Athens cost ~$3-5" (now marked not re-verified in the spec) | Replace with a stable one-line description + pointer to `docs/README.md` for trust status (WAYS_OF_WORKING §1: CLAUDE.md holds no state). Found during row #25. **Done** | WRONG |

HISTORICAL (leave): athens-2026 `EDITORIAL_ASSESSMENT.md` (self-dated 2026-05-29); runtime ONBOARDING pre-Athens dryrun history. Checked current: Briefing v3.1, Infrastructure, AUDIENCE_BRIEF, runtime/ + personas/ READMEs, CROSS_REPO_CONTRACT, planning + voices ONBOARDING, conventions. Possibly no doc action: C54 (internal dispatch logic).
