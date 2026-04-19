# Sonnet Execution Plan — Repo Reorganization

**Paste this into a fresh Claude Sonnet 4.6 session, medium effort. The plan is self-contained.**

## Your task

Execute §9 of `docs/FRESH_REVIEW_2026_04_19.md`: reorganise the
repo into four categories (production / research / planning / archive)
via a single clean refactor. **No code changes, no prompt changes, no
spec content changes.** Only file moves and pointer updates. All 29
runtime tests must still pass at the end. Commit after each phase with
the specified commit message. Push the branch at the end. Stop and ask
if anything is unclear or a verification fails — do NOT proceed through
broken state.

## Preflight

1. Read these in order:
   - `docs/FRESH_REVIEW_2026_04_19.md` §9 (the plan being executed —
     includes the exact four-category tree and migration steps)
   - `README.md` (top-level — will be rewritten in Phase C)
   - `CLAUDE.md` (top-level — will be rewritten in Phase C)
   - `docs/README.md` (will be extended in Phase C)

2. Verify clean tree + establish test baseline:
   ```bash
   cd /Users/aienvironment/Desktop/ai-assembly
   git status                           # clean
   git log -5 --oneline                 # last few commits
   cd runtime && venv/bin/python -m pytest ingest/tests/ -v
   ```
   All 29 tests must pass BEFORE any moves. If the baseline is red,
   stop and report.

3. Create the feature branch:
   ```bash
   cd /Users/aienvironment/Desktop/ai-assembly
   git checkout -b refactor-reorganise-tree
   ```

4. This plan itself currently sits at
   `personas/notes/SONNET_EXECUTION_PLAN_reorganization.md`. It will be
   moved into `_workspace/archive/fix-plans/` in Phase A along with the
   other execution plans. That's expected.

---

## Phase A — Create new tree and git mv archive material

### A.1 Create the new directories

```bash
cd /Users/aienvironment/Desktop/ai-assembly
mkdir -p research
mkdir -p _workspace/planning
mkdir -p _workspace/archive/specs
mkdir -p _workspace/archive/fix-plans/delta-docs
mkdir -p _workspace/archive/session-artifacts
mkdir -p _workspace/archive/runs
```

### A.2 Move into `research/`

```bash
git mv personas/notes/baseline_research research/baseline_research
```

### A.3 Move into `_workspace/planning/`

```bash
git mv personas/notes/REBUILD_PLAN.md _workspace/planning/
git mv personas/notes/ARCHITECTURE_NEXT_PHASE_HANDOFF.md _workspace/planning/
```

### A.4 Move stale specs into `_workspace/archive/specs/`

```bash
git mv docs/AI_Assembly_Architecture_v1.md _workspace/archive/specs/
git mv docs/AI_Assembly_Infrastructure_Setup.md _workspace/archive/specs/
```

### A.5 Move executed fix plans

```bash
# Persona-side execution plans
git mv personas/notes/SONNET_EXECUTION_PLAN.md _workspace/archive/fix-plans/
git mv personas/notes/SONNET_EXECUTION_PLAN_PHASE_A.md _workspace/archive/fix-plans/
git mv personas/notes/SONNET_EXECUTION_PLAN_ROUND_2.md _workspace/archive/fix-plans/
git mv personas/notes/SONNET_EXECUTION_PLAN_ROUND_3.md _workspace/archive/fix-plans/
git mv personas/notes/SONNET_EXECUTION_PLAN_repo_audit.md _workspace/archive/fix-plans/
git mv personas/notes/SONNET_EXECUTION_PLAN_reorganization.md _workspace/archive/fix-plans/
git mv personas/notes/SONNET_EXECUTION_PLAN_findings_fixes.md _workspace/archive/fix-plans/

# Other executed / working fix docs
git mv personas/notes/WALKTHROUGH_FIXES_PENDING.md _workspace/archive/fix-plans/
git mv personas/notes/IMPLEMENTATION_AUDIT_v3_7.md _workspace/archive/fix-plans/
git mv personas/notes/FIX_34_SECTION_BULLETS_DRAFT.md _workspace/archive/fix-plans/

# Runtime-side working docs
git mv runtime/notes/PROPOSED_pipeline_doc_change.md _workspace/archive/fix-plans/

# Delta docs
git mv runtime/notes/updated_specs/TRANSCRIPTION_v2_to_v2_1_delta.md _workspace/archive/fix-plans/delta-docs/
git mv runtime/notes/updated_specs/RESEARCHER_v2_to_v3_delta.md _workspace/archive/fix-plans/delta-docs/
git mv runtime/notes/updated_specs/PROVOCATEUR_v1_to_v2_delta.md _workspace/archive/fix-plans/delta-docs/

# Remove now-empty directories
rmdir runtime/notes/updated_specs
rmdir runtime/notes
rmdir personas/notes
```

If `rmdir` fails because a directory still contains files (e.g. a
`.DS_Store`), list the contents and delete the stragglers explicitly —
do NOT use `rm -rf` without listing first.

### A.6 Move session artifacts

```bash
git mv docs/SESSION_HANDOFF.md _workspace/archive/session-artifacts/
git mv docs/FRESH_REVIEW_2026_04_19.md _workspace/archive/session-artifacts/
git mv personas/notes/SESSION_REPORT_2026-04-19.md _workspace/archive/session-artifacts/
```

### A.7 Move run artifacts

```bash
git mv runtime/runs _workspace/archive/runs/runtime
git mv personas/runs _workspace/archive/runs/personas
```

Note: `runs/` may be gitignored in each sub-tree. If `git mv` reports
"fatal: bad source, source=...runs, ... destination", check `.gitignore`
and either (a) skip the git mv and use `mv` for the untracked parts,
then `git add` the new location, or (b) update `.gitignore` first to
unignore the archived location.

### A.8 Verify Phase A

```bash
git status  # should show renames only, no unexpected add/delete
ls runtime personas  # notes/ should be gone; runs/ gone
ls _workspace/archive/fix-plans/  # 12 files + delta-docs/
ls research/baseline_research/    # 5 compass_artifacts + README.md
ls _workspace/archive/session-artifacts/  # 3 files: SESSION_HANDOFF, FRESH_REVIEW, SESSION_REPORT_2026-04-19
ls docs/  # no Architecture_v1, no Infrastructure_Setup, no SESSION_HANDOFF, no FRESH_REVIEW
```

### A.9 Commit A

```bash
git add -A
git commit -m "$(cat <<'EOF'
refactor: create research/ + _workspace/ tree, move archive material

No code changes. Production slice (docs/, runtime/ code, personas/
code) is preserved. Historical material moves:

- research/baseline_research/ — 4 compass_artifacts (grounding)
- _workspace/planning/ — REBUILD_PLAN, ARCHITECTURE_NEXT_PHASE_HANDOFF
- _workspace/archive/specs/ — Architecture_v1, Infrastructure_Setup (STALE)
- _workspace/archive/fix-plans/ — all SONNET_EXECUTION_PLAN*, WALKTHROUGH_FIXES,
  IMPLEMENTATION_AUDIT, FIX_34_DRAFT, PROPOSED_pipeline_doc_change, 3 delta docs
- _workspace/archive/session-artifacts/ — SESSION_HANDOFF, FRESH_REVIEW
- _workspace/archive/runs/ — runtime/runs and personas/runs

Per §9 of the fresh review.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

---

## Phase B — Rewrite pointers in production docs

Any doc that currently points at a path that just moved needs an
update. Exact list of files + line ranges to edit:

### B.1 `docs/AI_Assembly_Briefing_v3_1.md`

- L148: "Full orchestration: `AI_Assembly_Architecture_v1.md`" →
  `_workspace/archive/specs/AI_Assembly_Architecture_v1.md` **AND** add
  parenthetical: "(archived — marked stale in `docs/README.md`)"
- L288: "Specified in `AI_Assembly_Architecture_v1.md`." → same
  treatment as L148
- L339-347 related-docs list: update
  `AI_Assembly_Architecture_v1.md` path; keep all `AI_Assembly_*_Pipeline.md`
  pointers unchanged (they're all still in `docs/`).

### B.2 `docs/CURRENT_STATE.md`

- L13-53 §0 "Quick map" tree: replace with the four-category tree from
  `_workspace/archive/session-artifacts/FRESH_REVIEW_2026_04_19.md`
  §9.1. Keep the level of detail similar; don't expand.
- L682 "docs/SESSION_HANDOFF.md" pointer (if present anywhere):
  `_workspace/archive/session-artifacts/SESSION_HANDOFF.md`
- Any reference to `runtime/notes/`, `personas/notes/`,
  `runtime/runs/`, `personas/runs/`, `personas/notes/baseline_research/`
  → updated path.

### B.3 `CLAUDE.md` (top-level)

- L3-8 "Repo layout" section: replace with the four-category tree
  (production / research / _workspace/planning / _workspace/archive).
  Mirror the description style of the original — concise one-liners.
- L34-43 "Where specs live" list: unchanged (all paths remain
  `docs/*.md`).
- Add a new convention line: `_workspace/` is out of scope for code
  reviews and VM deploys by default; Claude Code sessions should
  mention it explicitly if they want me to look.

### B.4 `README.md` (top-level)

- L10-15 "Structure" section: replace with the four-category tree.

### B.5 `docs/README.md`

- Extend the end with a new "What's NOT in `docs/`" section pointing
  into:
  - `research/` for grounding material
  - `_workspace/planning/` for forward-looking design
  - `_workspace/archive/` for historical record (eligible for pruning)

### B.6 `research/baseline_research/README.md` (moved in Phase A)

- Verify internal pointers still resolve:
  - `docs/AI_Assembly_Persona_Pipeline_v3_10.md` — unchanged, still in
    `docs/`
  - `docs/AI_Assembly_Briefing_v3_1.md` — unchanged
  - `docs/AUDIENCE_BRIEF.md` — unchanged
  - `runtime/flows/shared/council/council_config.json` — unchanged
  - No path updates needed; just double-check.

### B.7 Other internal pointer sweeps

Run these greps from repo root to surface any lingering pointers that
need updating:

```bash
# Pointers to moved files from production docs/code
grep -rn "AI_Assembly_Architecture_v1\|AI_Assembly_Infrastructure_Setup" \
  docs/ README.md CLAUDE.md runtime/ personas/ \
  --include="*.md" --include="*.py" --include="*.json" \
  | grep -v "_workspace\|research/"
# Each hit needs: update pointer to _workspace/archive/specs/… OR remove if redundant

grep -rn "SESSION_HANDOFF\|FRESH_REVIEW_2026_04_19" \
  docs/ README.md CLAUDE.md runtime/ personas/ \
  --include="*.md" --include="*.py" --include="*.json" \
  | grep -v "_workspace\|research/"
# Each hit needs: update pointer to _workspace/archive/session-artifacts/…

grep -rn "personas/notes\|runtime/notes\|personas/runs\|runtime/runs" \
  docs/ README.md CLAUDE.md runtime/ personas/ \
  --include="*.md" --include="*.py" --include="*.json" \
  | grep -v "_workspace\|research/"
# Each hit needs: update to _workspace/archive/…

grep -rn "baseline_research\|REBUILD_PLAN\|ARCHITECTURE_NEXT_PHASE" \
  docs/ README.md CLAUDE.md runtime/ personas/ \
  --include="*.md" --include="*.py" --include="*.json" \
  | grep -v "_workspace\|research/"
# Hits pointing at personas/notes/baseline_research → research/baseline_research
# Hits pointing at personas/notes/REBUILD_PLAN → _workspace/planning/REBUILD_PLAN
# Hits pointing at personas/notes/ARCHITECTURE_NEXT_PHASE_HANDOFF → _workspace/planning/…
```

If a grep returns nothing in each of the four greps, pointers are
clean. If any returns a hit, update that file BEFORE continuing.

**Additionally — internal pointers in moved files.** The four greps
above search the production tree, not `_workspace/` itself. After the
greps return clean, also check the two newly-moved-in REBUILD_PLAN
and SESSION_REPORT for stale internal pointers from before they moved:

- `_workspace/planning/REBUILD_PLAN.md` §"Cross-cutting · Boddice
  integration" contains a markdown link with relative href
  `baseline_research/compass_artifact_wf-1e84f45b-…md`. That relative
  href broke when the file moved out of `personas/notes/`. Update both
  the display path (`personas/notes/baseline_research/…` →
  `research/baseline_research/…`) and the href (`baseline_research/…`
  → `../../research/baseline_research/…`).
- `_workspace/archive/session-artifacts/SESSION_REPORT_2026-04-19.md`
  references several now-moved paths in display text (REBUILD_PLAN,
  baseline_research). As a session snapshot, the stale references
  are honest historical record. Add ONE note line at the top of the
  file: `*Note: paths in this report reference the pre-reorganization
  layout (commit `d1b8a2c`).*` — do NOT rewrite the body.

### B.8 Commit B

```bash
git add -A
git commit -m "$(cat <<'EOF'
docs: update pointers to match reorganised tree

Rewrite path references in the production docs (Briefing v3.1,
CURRENT_STATE, CLAUDE.md, README.md, docs/README.md) to point at the
new locations under research/, _workspace/planning/, and
_workspace/archive/. No content changes beyond paths.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

---

## Phase C — Add stub READMEs + docs/references.md

### C.1 Create `research/README.md`

```markdown
# Research

Preserved grounding material that informed the production specs. Not
deletable — these are rigorous reference documents, not fix plans.
When you want to know "why is the pipeline like this?", look here.

## Contents

### baseline_research/

Four Deep Research artifacts commissioned before the persona pipeline
was designed. Together they ground:

- the architecture choices in `docs/AI_Assembly_Persona_Pipeline_v3_10.md`,
- the audience framing in `docs/AUDIENCE_BRIEF.md`,
- the validation / evaluation protocols.

See `baseline_research/README.md` for the file-by-file index.
```

### C.2 Create `_workspace/README.md`

```markdown
# _workspace

Out of scope for code reviews and VM deploys. Two subdirectories:

## planning/

Forward-looking design documents for work not yet built. Promoted into
`docs/` when the work lands; deleted if abandoned.

- `REBUILD_PLAN.md` — Phase B persona pipeline rewrite (chunked-JSON
  architecture; not yet started)
- `ARCHITECTURE_NEXT_PHASE_HANDOFF.md` — binding design decisions for
  Phase B (9 locked decisions, PB#1 through PB#9)

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
```

### C.3 Create `docs/references.md`

```markdown
# References

Pointers into `research/` and `_workspace/planning/` from the
production specs in `docs/`.

## Grounding research (`research/baseline_research/`)

When a current spec says "per the baseline research" or you're
wondering why the architecture looks the way it does:

- **4-layer persona architecture** (RAG + constitution + reasoning
  templates + persona vectors) → `research/baseline_research/compass_artifact_wf-cc778da2-…md`
- **Multi-model research workflow** (Perplexity + Claude DR + Gemini)
  → `research/baseline_research/compass_artifact_wf-45560dac-…md`
- **Section-by-section generation + 4-block prompt pattern** →
  `research/baseline_research/compass_artifact_wf-865974da-…md`
- **Seven-faction audience analysis** (grounding `docs/AUDIENCE_BRIEF.md`)
  → `research/baseline_research/compass_artifact_wf-109ac10a-…md`
- **Biocultural critique of Persona Card v2** (Boddice's history of
  emotions; integration target = Phase B rebuild via PB#2 hybrid
  Jinja+LLM tailoring + PB#1 voice-type-specific 1a/1b prompts +
  PB#7 evidence tags) → `research/baseline_research/compass_artifact_wf-1e84f45b-…md`

## Forward-looking planning (`_workspace/planning/`)

Active design work for unbuilt features:

- **Phase B persona pipeline rewrite** → `_workspace/planning/REBUILD_PLAN.md`
  + `_workspace/planning/ARCHITECTURE_NEXT_PHASE_HANDOFF.md`
```

### C.4 Commit C

```bash
git add research/README.md _workspace/README.md docs/references.md
git commit -m "$(cat <<'EOF'
docs: add research/ + _workspace/ READMEs and docs/references.md

Three new stub docs so a GitHub visitor or Claude Code session finds
the new structure self-describing:

- research/README.md — what's preserved and why
- _workspace/README.md — planning vs archive distinction + pruning rule
- docs/references.md — pointer from production docs into research/
  and _workspace/planning/ for rationale / forward-looking material

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

---

## Phase D — Optional: mark `_workspace/` as low-diff-priority

Small ergonomic win for reviewers: `git diff` won't show
`_workspace/` changes unless explicitly requested.

```bash
cat >> .gitattributes <<'EOF'

# _workspace/ is historical material, out of scope for reviews by default.
_workspace/** linguist-documentation
_workspace/** -diff
EOF
git add .gitattributes
git commit -m "chore: mark _workspace/ as out-of-scope for git diff + language stats"
```

Skip this phase if `.gitattributes` doesn't exist yet and you prefer
not to introduce it for a one-liner. Not load-bearing.

---

## Phase E — Final verification

### E.1 Tests

```bash
cd runtime && venv/bin/python -m pytest ingest/tests/ -v
```
Expected: 29/29 pass. If any test fails, stop and investigate — a
pure file move should not break tests.

### E.2 Imports

```bash
cd /Users/aienvironment/Desktop/ai-assembly/personas
venv/bin/python -c "
import sys; sys.path.insert(0, '.')
from flows.shared.clients import call_claude
from flows.shared.io import load_prompt, voice_slug, load_voice_input
from flows.shared.node0_validation import validate_input
from flows.shared.prompt_render import render
print('personas imports: OK')
"

cd /Users/aienvironment/Desktop/ai-assembly/runtime
venv/bin/python -c "
import sys; sys.path.insert(0, '.')
import flows.transcription_flow, flows.researcher_flow, flows.provocateur_flow
import ingest.app, ingest.pipeline, ingest.sessions, ingest.auth, ingest.config
print('runtime imports: OK')
"
```
Expected: both print OK. If either fails, stop.

### E.3 No broken pointers

Re-run the four greps from B.7. Each should return nothing.

### E.4 `git log --follow` still traces moved files

```bash
git log --follow --oneline -5 research/baseline_research/README.md
git log --follow --oneline -5 _workspace/archive/specs/AI_Assembly_Architecture_v1.md
```
Each should show at least one commit predating the move.

### E.5 Push

```bash
cd /Users/aienvironment/Desktop/ai-assembly
git push -u origin refactor-reorganise-tree
```

Then open a PR:

```bash
gh pr create --title "refactor: reorganise repo into production / research / planning / archive tree" --body "$(cat <<'EOF'
## Summary

- Introduces four-category repo structure per §9 of the most recent
  fresh-review session artifact.
- Moves historical material (runs, fix plans, stale specs, session
  artifacts, baseline research) out of the production slice via
  `git mv` so history is preserved.
- Updates pointers in production docs (Briefing v3.1, CURRENT_STATE,
  CLAUDE.md, README.md, docs/README.md) to match the new layout.
- Adds README stubs (research/, _workspace/) and a
  docs/references.md pointer file so the new tree is self-describing
  in the GitHub browser.

No code changes, no prompt changes, no spec content changes beyond
path pointers. All 29 runtime tests pass before and after.

## Test plan

- [x] Runtime test suite passes (29/29)
- [x] All runtime + personas modules import clean in their venv
- [x] No production doc contains a pointer to a moved path
- [x] `git log --follow` traces the history of at least two moved
      files to commits predating the rename

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

---

## Stop-and-ask rules

- **`pytest` fails in preflight (Phase A.2)** → stop; baseline must
  be green before refactor.
- **Any `git mv` fails** (path typo, destination exists, source
  untracked) → stop, report the command and error, wait for direction.
  Do NOT use `rm` or `mv` without git's knowledge.
- **`rmdir` fails on `runtime/notes`, `personas/notes`, or
  `runtime/notes/updated_specs`** → list the remaining contents; if
  `.DS_Store` or similar, `rm` just those; if anything else, stop and
  report.
- **Phase B grep finds a broken pointer** → fix that file, stage it,
  include it in commit B. Do NOT commit broken pointers.
- **Phase E pytest fails after moves** → stop; the refactor should
  not break tests. A failure here indicates either a missed pointer
  (look in `runtime/ingest/pipeline.py` subprocess env / `INGEST_FLOW_CMD`
  / reference data paths) or an actual test-infrastructure dependency
  on a moved path.
- **Running out of context mid-phase** → complete the current phase's
  commit before responding; never leave an uncommitted intermediate
  state.

## Out of scope

Do NOT, in this refactor:

- Delete any archive material. Pruning is a later, separate
  operation per the pruning rule documented in `_workspace/README.md`.
- Rewrite spec content (only pointer paths).
- Touch the in-place `_archive/` subdirectories inside
  `personas/inputs/voices/`, `personas/inputs/dossiers/`, or
  `runtime/flows/shared/prompts/`. They're small, scoped, and leaving
  them in place is less disruptive than moving them.
- Modify any code, prompt, or .env file.
- Upgrade any model version or add any new feature.

---

*This plan will move itself to `_workspace/archive/fix-plans/` in
Phase A.5. That's expected.*
