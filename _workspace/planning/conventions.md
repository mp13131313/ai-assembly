# Conventions

Project-wide naming + organization conventions. Future decisions should
land in these patterns. **Document the convention BEFORE breaking it.**

---

## Directory naming

- **snake_case** for code, planning, archive subdirs that aren't dates
- **kebab-case** discouraged but acceptable if already widespread (e.g.
  `phase-l-plato/` — left in place, but new dirs go snake_case)
- **ISO date** when a directory is a snapshot of a moment:
  `YYYY-MM-DD_descriptive_snake_case_name/`
  - leading date, kebab-delimited inside the date, underscored after
  - example: `2026-05-29-history-rewrite/` ✓
  - example: `2026-04-22_arch_03_baseline_snapshot/` ✓
  - **bad:** `arch_03_baseline_snapshot/` (no date — when was this?)
  - **bad:** `personas_prompts_PRE_582af96_REVERT_20260428_231640/`
    (SHA prefix, glued date) — and SHAs become dead after history rewrites

## File naming

- **`.md`** for prose
- **snake_case.py** for Python modules
- **CamelCase.json** for schema files where the convention matches the
  schema name; **snake_case.json** otherwise
- **TitleCase.md** for top-level docs (`README`, `CHANGELOG`, `STATE`,
  `CLAUDE`); **snake_case.md** for body content
- Pipeline specs: `AI_Assembly_<Component>_<Type>.md` is the established
  pattern; not loved but pervasive — leave alone unless doing a full
  spec-rename pass

## Doc roles + ownership

| Doc | Owns | Doesn't own |
|---|---|---|
| `STATE.md` | current state (single source for "what's now") | scaffolding, history, specs |
| `CLAUDE.md` | scaffolding for Claude sessions (filesystem, conventions, reading order) | state, history |
| `CHANGELOG.md` | time-stamped history of changes | current state, specs |
| `README.md` (root) | public-facing project overview + setup pointer | state detail, history |
| `_workspace/README.md` + `_workspace/planning/ONBOARDING.md` | workspace structure + cross-cutting DON'Ts | (mostly merged into ONBOARDING.md, README is short) |
| `_workspace/planning/{runtime,voices}/ONBOARDING.md` | workstream-specific onboarding | cross-cutting rules |
| `_workspace/planning/{runtime,voices}/OPEN_ITEMS.md` | authoritative open-item tracker for that workstream | state |
| `_workspace/planning/{runtime,voices}/HANDOFF.md` | session-state-of-the-moment for that workstream | state in the durable sense |
| `_workspace/planning/conventions.md` (this file) | naming + organization rules | examples (those are tests) |
| Sub-tree `README.md` (runtime/, personas/) | pointer-density nav for that sub-tree | duplicated content |
| `docs/AI_Assembly_*_Pipeline.md` | spec for that pipeline component | state, history |
| `personas/HANDOFF.md` (→ `CROSS_REPO_CONTRACT.md`) | cross-repo contract between personas + runtime | session handoffs |

## When to add an entry to CHANGELOG

- A production milestone (Athens night published, voice shipped)
- An architectural shift (pipeline version bump, repo restructure)
- A history rewrite (filter-branch, mass rename, archive cleanup)
- A branch retirement
- **Not** every commit — that's `git log`.

## When to add an entry to STATE.md

- Production results change (a new event runs)
- Open-item status changes (a C-item resolves or surfaces)
- Voice-build state changes (a voice ships or gets a major rev)
- Architectural validation finding (new empirical evidence)

## When NOT to put state in CLAUDE.md or root README

Almost never. Both should point at STATE.md for current-state queries.
Exception: a single-line "Status: Athens 2026 COMPLETE" header in CLAUDE.md
is acceptable as a heads-up, with the detail living in STATE.md.

## Branch naming

- `main` is canonical
- `feature/<short-name>` for in-flight features
- `fix/<short-name>` for in-flight fixes
- When a feature branch is retired (merged, superseded, or dropped):
  - Tag the tip as `archive/<branch-name>-<YYYY-MM-DD>` before deleting
  - Add a CHANGELOG.md entry recording the retirement
  - Update `STATE.md` if any reference still exists there
  - Capture the design in a `_workspace/planning/<workstream>/DESIGN_*.md`
    memo if it's worth preserving (the option-b retirement pattern from
    C48 / `feature/voice-deployment-context`)

## Archive shape

- Every archive subdir is `YYYY-MM-DD_descriptive_name/` (snake_case after date)
- **No loose files at archive root** — wrap in a dated subdir even if it's a
  single file
- Every archive subdir gets a `README.md` if it's non-obvious what's inside

## Cross-references

- Always use repo-rooted paths (`docs/X.md`, not `../docs/X.md` unless the
  doc is in a sub-tree and the relative form is clearer)
- When a moved file leaves dangling references, update them in the same
  commit as the move
- When a doc cites a commit SHA, use the post-rewrite SHA (translate via
  `~/Desktop/AI Assembly/archive/2026-05-29-history-rewrite/HASH_REMAP_*.tsv`
  if you find a dead one)

## Conventions about conventions

- Add a convention here BEFORE the first time you need it, not after the
  third inconsistency.
- If a convention isn't being followed, either change it or fix the
  inconsistency — don't leave both states alive.
