# Ways of working — keeping the documentation true

How work gets recorded so every doc stays current. `conventions.md` says
*what each doc owns*; this doc says *when and how it gets updated*. Written
2026-09-28 from the misses of the post-Athens work (listed at the end) —
each rule below exists because its absence cost something.

---

## 1. One home per fact

Every fact has exactly one authoritative home. Other docs **point** to it;
they don't restate it (restated facts drift).

| Question | Home |
|---|---|
| What's the state *now*? What's on which branch? | `STATE.md` |
| What changed, and when? | `CHANGELOG.md` (coarse) · `git log` (fine) |
| What's open, and what's its status? | `_workspace/planning/{runtime,voices}/OPEN_ITEMS.md` |
| In what order do we work? What did the operator decide? | `_workspace/planning/PLAN_2026_06_12_post_athens_roadmap.md` |
| Where is the product going? | `_workspace/planning/PRODUCT_assembly_hub.md` |
| How does a pipeline behave? | `docs/AI_Assembly_*_Pipeline.md` (+ `docs/README.md` says which specs to trust) |
| Which model runs which step? | `model_routing.json` — nowhere else (a test fails on model names hardcoded in code) |
| Every LLM call and its parameters | `docs/LLM_CALL_INVENTORY.md` (generated from code, see §6) |
| How a Claude session finds its way | `CLAUDE.md` (scaffolding only — never state) |
| Naming, organization, doc roles | `conventions.md` |
| How docs stay current (this process) | this file |

If a fact needs to appear in two places, one of them is a link.

## 2. File before you build

New work gets its tracker entry **before** the first code change: a C-number
(runtime) or §-number (voices), with the *why*, the approach, and what "done"
means. Commit messages cite the ID (`Refs runtime/OPEN_ITEMS.md C63`). Work
that spans both pipelines is filed in both trackers with cross-references.
Work that changes the order of things also gets a line in the roadmap.

*Small, obvious fixes found mid-task* can be filed in the same commit as the
fix — but they are still filed.

## 3. Done means documented

A change is **done** when, on the same branch as the code:

1. **Tracker** — the item's status is updated with the date and commit hash
   (✅ FIXED / 🟢 IN PROGRESS / ⏸ waiting on …), plus any residual left open.
2. **Spec** — every `docs/` spec that describes the changed behavior says the
   new thing. Specs describe *current* behavior; history goes to CHANGELOG,
   not into spec preambles.
3. **Staleness index** — if a spec's trust status changed, `docs/README.md`
   says so (with the date it was last checked against code).
4. **Tests** — green, and they exercise production-shaped data (clean
   fixtures hid the C53 name corruption for four months).
5. **STATE.md** — if current state changed (per `conventions.md`: a result,
   an item resolving, a voice shipping, a branch landing).
6. **CHANGELOG.md** — if it's a milestone (per `conventions.md`).

Code without its doc updates is not "done, docs later" — it's not done.

## 4. Decisions are the operator's; inferences are labelled

- **Operator decisions** are recorded with the date and, where possible, the
  operator's own words (roadmap "Operator decisions" block + the item's
  tracker entry).
- **Claude's inferences** are written as inferences: *"inferred from X —
  confirm"*. An inference is never recorded as a decision. (2026-09-28:
  "no next event" was written down as "shelved"; the operator's actual
  position was "I build on my own intent".)
- When a draft changes meaning on review (e.g. a test's direction), fix it
  and mark the correction in place, dated.

## 5. Nothing stays "pending" silently

Anything marked pending / waiting / in progress names **what** it waits on.
When that thing happens, the marker is updated **in the same session** — the
push, the merge, the decision. A periodic grep for `pending|in progress|awaits`
across the trackers and roadmap catches leftovers (§8).

## 6. Generated docs are regenerated, never hand-edited

| Generated doc | How to regenerate |
|---|---|
| `docs/LLM_CALL_INVENTORY.md` | re-derive from code (read every call site; a subagent task) — whenever calls, models or wrappers change |
| athens-2026 `published_artifacts/data_views/` | `runtime/scripts/build_athens_data_graph.py` (reads the project; no API calls) |
| athens-2026 published voice names / night indexes | `runtime/scripts/restamp_published_voice_names.py` (dry run by default) |

A generated doc carries its generation date at the top.

## 7. If it only exists in the conversation, it doesn't exist

Before a session ends — and before any context compaction — everything
decided, found or designed in that session is written to its home (§1).
Conversation transcripts are not documentation. (June 2026: a full
agentic-architecture analysis survived only because the operator pasted the
transcript back in.)

Verify before writing: claims about data or behavior are checked against the
code or the production files first, and cite `file:line`, a commit, or the
command that showed it. ("Night 2 index: cosmetic" was written without
checking Night 1, which listed 3 of 10 voices.)

## 8. Rhythm — checklists

**Per change (before commit):**
- [ ] tracker entry exists (§2) and is updated (§3.1)
- [ ] specs describing the behavior updated (§3.2); staleness index if needed
- [ ] tests green on production-shaped data
- [ ] commit message cites the ID; attribution line per `CLAUDE.md`

**Per work session (before ending or compacting):**
- [ ] `STATE.md`: snapshot date, status paragraph, branch situation
- [ ] `CHANGELOG.md`: entry if a milestone landed
- [ ] every "pending" marker touched today is still true (§5)
- [ ] conversation-only findings/decisions filed (§7)
- [ ] push status stated (what's local-only is a risk until pushed)

**At every merge into `main`:**
- [ ] branch tagged `archive/<branch>-<YYYY-MM-DD>` before deletion
  (per `conventions.md`); CHANGELOG entry; `STATE.md` branch section updated

**Monthly, or after any large batch (a "staleness sweep"):**
- [ ] `docs/README.md`: re-check each spec against code; update its
  "last verified" date
- [ ] grep trackers + roadmap for stale `pending / in progress / awaits`
- [ ] regenerate generated docs whose sources changed (§6)
- [ ] read `STATE.md` top to bottom as a newcomer — does it match reality?

## 9. Writing so it reads well

- **Lead with the outcome**, then the detail. A reader should know the state
  from the first two lines of any entry.
- **Plain language** first; the technical term in brackets if needed.
- **Date every status** (`✅ FIXED 2026-09-27`) and cite IDs and commits so
  anything can be traced.
- **Say why**, not just what — the reason is what survives a rewrite.
- **Short sections, tables for status**, one idea per paragraph.
- **Mark history as history** (dated, or "was …") rather than deleting it
  from trackers; delete only from docs that describe *current* behavior.

## 10. Proportionate enforcement

What's already automatic: the model-literal test (model names only in
`model_routing.json`), the golden model test, and the loader copy check. What
isn't: everything else here relies on the checklists. A small
`docs_check` script (list stale `pending` markers; list specs whose code
changed after their "last verified" date) would turn §8's sweep into one
command — worth building if the sweep starts getting skipped.

## 11. Planning-folder hygiene (moved from ONBOARDING.md, 2026-09-28)

To keep this folder load-bearing rather than archival, follow these rules. They apply to both workstream subfolders.

**Stays here:**

- **One current HANDOFF per workstream.** Append within the day; spawn a new dated HANDOFF only when starting a fresh day's work. Within `runtime/`, name it `HANDOFF_<YYYY_MM_DD>.md`. Within `voices/`, single rolling `HANDOFF.md` is fine (different convention, both work).
- **OPEN_ITEMS.md** (per workstream) — authoritative, durable.
- **ONBOARDING.md** (per workstream + this root one) — durable; updates are surgical, not append-only.

**Gets archived (move to `_workspace/archive/session-artifacts/`):**

- **Yesterday's HANDOFF** when today's HANDOFF supersedes it via "Predecessor handoff:" header. Keep only the latest in `_workspace/planning/<workstream>/`.
- **Design docs** (e.g., `*_DESIGN_*.md`) once the thing they spec exists. Their content migrates to: implementation + a lifecycle/operations doc + an OPEN_ITEMS entry. The design doc itself becomes historical context.
- **One-off briefs / audits** (`BRIEF_*.md`, `*_AUDIT_*.md`) once their findings have been actioned.

**Stays under `docs/` (not here):**

- Canonical pipeline specs.
- Operational/lifecycle docs.

**Trigger:** when proposing a new doc, ask first whether the content can live in OPEN_ITEMS, ONBOARDING, or an existing pipeline doc. Default is no new top-level doc. Spec → archive once shipped. *(This file is a deliberate exception, 2026-09-28: the operator asked for a written ways of working, and it absorbed this section so the process has one home.)*

---

## Why these rules exist (the 2026 misses)

| Miss | Rule |
|---|---|
| `STATE.md` stayed at its 2026-06-01 snapshot through months of planning and two days of fixes | §3.5, §8 per-session |
| The model config was built before any tracker had it | §2 |
| "Shelved" recorded as a decision; it was an inference | §4 |
| "Push pending" markers outlived the push | §5 |
| `docs/README.md` said "refresh pending" for months | §3.3, §6, §8 monthly |
| Clean test fixtures hid the published-name corruption | §3.4 |
| "Night 2 index cosmetic" written without checking Night 1 | §7 verify |
| An architecture analysis existed only in a chat transcript | §7 |
| Branches named `post-athens-planning` / `phase0-fixes` instead of `feature/…` / `fix/…` | `conventions.md` branch naming (§8 at merge) |
