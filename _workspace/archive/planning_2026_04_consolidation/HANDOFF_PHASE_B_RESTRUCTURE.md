# Handoff — Phase B per-voice-folder restructure

**Paste this into a fresh Claude Sonnet 4.6 session, medium effort.**

You're continuing the AI Assembly project's Phase B rebuild on branch `phase-b-rebuild`. An Opus 4.7 session just finished designing the per-voice-folder restructure + per-section manual DR support. Your job is to execute that design.

## Your first action

Read these in order before touching code:

1. **`_workspace/planning/SONNET_EXECUTION_PHASE_B_RESTRUCTURE.md`** — THE execution plan. Self-contained, step-by-step, ~20 phases. Contains the full locked spec.
2. **`CLAUDE.md`** (repo root) — repo layout, venv rules, Tier 3 project/code separation rules.
3. **`_workspace/planning/OPEN_ITEMS.md`** — current Phase B state. Several items in the "Pending code changes" list close in this session.
4. **`_workspace/planning/REBUILD_PLAN.md`** — architectural decisions (PB#1–9). Do NOT re-litigate.

After reading, report back with:
- (a) You understand the scope.
- (b) Current branch state (`git status`, `git branch --show-current`, `git log phase-b-rebuild -5 --oneline`).
- (c) Any ambiguity in the plan before starting — ambiguities surface cheaper here than mid-execution.

Then execute phases sequentially. Commit after each phase. Push after every 3–4 phases.

## Scope

Two things happen in this session:

1. **Restructure** the per-voice filesystem layout from flat `$PROJECT_ROOT/inputs/...` + `$PROJECT_ROOT/runs/<slug>/...` into nested `$PROJECT_ROOT/voices/<slug>/00_intake/…06_derive/` with two-digit zero-padded numeric prefixes at every level.

2. **Enable per-section manual DR workflow**: operator pastes 6 section prompts (produced by new `split_tailored_prompt.py`) into claude.ai, downloads 6 `.md` files, pipeline auto-detects per-section mode and reads per-section DR + per-section Perplexity + full Gemini per chunked merge. Monolithic fallback preserved.

Bundle 9 smaller improvements flagged in OPEN_ITEMS while touching adjacent code.

**~14.5 hours of work**, 2–3 sittings.

## Branch + commit discipline

- Stay on `phase-b-rebuild` (existing branch). Do NOT create a new branch for this work.
- Commit per phase, not per file. Commit message prefix: `feat(phase-b/restructure-{N})` where N is the phase letter.
- Push after every 3–4 phases so work isn't lost on context loss.
- Do NOT merge to main. Phase M (merge) is gated on Phase L.8 human quality review — separate session.
- Do NOT force-push, reset --hard, rebase, or clean --fd.

## Rules

- **Never touch**: `~/Desktop/AI Assembly/archive/` (historical v3.10 runs), `_workspace/archive/` (historical fix plans), anything under `_archive/` anywhere.
- **Never delete voice data** unless the plan explicitly says to (e.g. Ibn Battuta fixtures at `personas/tests/fixtures/ibn_battuta/` — yes, delete per plan; archived Plato at umbrella archive — no, never).
- **Never skip hooks** (`--no-verify`). If a hook fails, investigate root cause.
- **If a verify step fails**: stop, do not commit broken state, report what failed.
- **If the plan is ambiguous**: write your question to `_workspace/planning/SONNET_QUESTIONS_PHASE_B_RESTRUCTURE.md`, stop execution, ask via user. Do NOT guess.
- **If you discover the plan is wrong** (e.g. references a file that doesn't exist, or a design decision conflicts with reality): flag immediately, do not silently work around.

## Handoff-back protocol

When context runs low or you need to stop mid-session, write a handoff summary at `_workspace/planning/SONNET_PHASE_B_RESTRUCTURE_HANDOFF.md` with:

- Completed phase letters + their commit SHAs
- Current phase + exact step number you stopped at
- Any open questions or decisions the next session needs
- Commit SHAs pushed to `origin/phase-b-rebuild`

Next session resumes from your handoff.

## Model + effort

Claude Sonnet 4.6, medium effort. This is pure execution against a locked spec. If you hit something that feels like it needs architectural judgment (genuine design choice, not filling in implementation details), stop and ask — that's Opus-shaped work, not yours.

## Environment

- Current working directory: `/Users/aienvironment/Desktop/AI Assembly/code/`
- Current branch: `phase-b-rebuild`
- Venv: `personas/venv/` (activate for any Python invocation in personas/)
- Python: 3.12
- Testing: `cd personas && venv/bin/python -m pytest tests/`
- `.env` at `code/.env` (read by both pipelines via `REPO_ROOT.parent / ".env"`)

---

*Plan created 2026-04-21 by Opus 4.7 design session. Execute on Sonnet 4.6 medium.*
