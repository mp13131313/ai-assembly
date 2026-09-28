# Brief: code review of `phase0-fixes` before it merges into `main`

**For:** a separate review session on **Fable 5.1** (`claude-fable-5-1`), high effort.
**Written:** 2026-09-28 by the main working session, at the operator's request.
**Archive this brief** once its findings are filed (`_workspace/planning/WAYS_OF_WORKING.md` §11).

---

## Your job

Find bugs and unintended behavior changes on the branch before it is merged into `main`. **Review only:** don't fix, don't commit to `phase0-fixes`, don't push, don't merge. Your output is one report file (last section).

## What is being merged

- `main` is the Athens-complete code: `5321f08`, 2026-06-04.
- `phase0-fixes` is 51 commits on top of it, including the June planning branch `post-athens-planning`. `main` has no commits the branch lacks, so the merge will be a fast-forward. **The review is the only gate.**
- Whole diff: `git diff main...phase0-fixes`, 103 files, +6477 / −1894.
- **Code:** 76 files in `runtime/`, `personas/` and `model_routing.json`, +5382 / −749. This is your scope.
- The rest is docs and trackers. Read them only to learn what a change was meant to do.
- **Why each change was made:** see the `CHANGELOG.md` entries for 2026-09-27/28, then the tracker items the commit messages cite:
  - `_workspace/planning/runtime/OPEN_ITEMS.md`: C46, C49, C50, C51, C53, C54, C55, C56, C58, C63, C64, C65, C66.
  - `_workspace/planning/voices/OPEN_ITEMS.md`: §32, §35, §36.

## Setup

- **Venvs:** `runtime/venv` and `personas/venv`. If your worktree lacks them, use the main checkout's at `/Users/aienvironment/Desktop/AI Assembly/code/{runtime,personas}/venv`.
- **Baseline:** all green at `613faf0`. Run each suite before you start and again at the end.

| Suite | Command | Expect |
|---|---|---|
| runtime | `cd runtime && AI_ASSEMBLY_PROJECT_ROOT="/Users/aienvironment/Desktop/AI Assembly/projects/current-tests" venv/bin/python -m pytest tests -q -p no:cacheprovider` | 368 passed |
| ingest | Make a scratch dir, copy `/Users/aienvironment/Desktop/AI Assembly/projects/athens-2026/reference/*.json` into `<scratch>/reference/`, then `cd runtime && AI_ASSEMBLY_PROJECT_ROOT=<scratch> venv/bin/python -m pytest ingest/tests -q -p no:cacheprovider` | 114 passed |
| personas | `cd personas && AI_ASSEMBLY_PROJECT_ROOT="/Users/aienvironment/Desktop/AI Assembly/projects/current-tests" venv/bin/python -m pytest tests -q -p no:cacheprovider` | 242 passed |

A Prefect logging message ("I/O operation on closed file") at the end of the runtime run is known noise, not a failure.

## Hard rules

- **No real API calls.** Don't run any pipeline, persona runner script, or anything that calls a model. The tests are all mocked. Never run pytest over `personas/scripts/`.
- **`/Users/aienvironment/Desktop/AI Assembly/projects/athens-2026` is read-only.** Reading it to check real data shapes is encouraged. Never write to it or run git there.
- **Don't edit code.** A throwaway script or test under your scratch dir to prove a finding is fine; say so in the report.
- **Verify before reporting.** Label each finding CONFIRMED (you read the path or ran it) or PLAUSIBLE (reasoned, not proven).

## Where to look hardest, riskiest first

1. **Model config (C63): touches every LLM call.** Look at `model_routing.json`, the loader `flows/shared/model_routing.py` (a byte-identical copy in `runtime/` and `personas/`; a test checks this), and every converted call site. The core question: **for each call, is what reaches the API identical to `main`?** That means model, thinking on or off, effort sent or not, `temperature` sent or not, `max_tokens`, and caching. Compare each call site on `main` against the branch.
   - Check the golden test in `runtime/tests/test_model_routing.py` isn't circular.
   - Check the precedence of the legacy env overrides (empty value = unset; `CLAUDE_MODEL` applies only to the runtime steps it applied to before).
   - Check the loader's refusal rules.
   - Check the `"manual": true` steps: could an API step marked manual slip past the rules?
   - Check `model_vendor()` and the validator ladders: `personas/flows/shared/clients.py:call_validator_ladder` and `runtime/flows/voice/step1_validation.py:_call_openai_with_fallback`.
   - **Intended behavior changes; confirm these are the only ones:**
     - (a) Persona validator ladders now route each model by vendor, not position. The result is the same for the shipped ladder.
     - (b) The runtime Step-1 validator no longer sends `reasoning_effort` to gpt-4.1 or gpt-4o.
     - (c) `call_claude` sends `temperature` only when thinking is off and the model accepts sampling parameters.
2. **Published voice names (C53).**
   - `runtime/flows/shared/io.py` (`voice_display_name`, `load_council_name_by_slug`), `voice/publish.py`, `editor/routing.py`, `runtime/scripts/restamp_published_voice_names.py`. The script was already applied to the published record.
   - Edge cases: a slug missing from `council_config.json`; the "the " prefix in headnotes; nested Step-3 names.
3. **The dossier index has two writers** (C46, C50, C51).
   - `editor/edition.py:merge_night_index`, with its owned-key sets and `_rebuild_dossiers_from_disk`, against `publish_flow.py`'s index writers and the theme files. Do the ownership rules hold when either writer runs first or re-runs?
   - `voice/publish.py:_rebuild_index_from_disk`.
4. **Orchestrator dispatch (C54).** `runtime/scripts/overnight_orchestrator.py` now dispatches through `infer_state`. Could it launch a stage twice, skip one, or misread a stage that's still running (pid checks)?
5. **Transcription fallback (C49).** `transcription_flow.py:build_speaker_id_fallback` and the `except json.JSONDecodeError` path.
   - Is the handling too narrow or too broad?
   - Is the fallback mapping the right shape for downstream stages?
   - Is the `speaker_id_auto_passthrough` flag written where operators will see it?
6. **Editor** (C56, C64, C65, C66).
   - `card_assembly.py`: the `corpus_metadata` strip.
   - The four C64 fixes (see the C64 tracker entry).
   - C65: the `--no-prompt-cache` path, passed from `editor_flow.py` via `generate_dossier` to `stream_voice_call`.
   - C66: the first dossier call runs alone, then the rest in parallel. What if the first call fails, a theme has no voices routed to it, or `--single-dossier` is used?
7. **Personas pipeline** (`run_persona_pipeline.py`).
   - §32.1: variables rebound after the bracket-strip. Is any stale variable still read afterwards?
   - §32.2: the 7a-FINAL exclude list.
   - §36: `prompt_render.model_name()` template global, also installed in `run_phase0_1_research.py`.
8. **Prompt edits.** Check that each changes only what its item says; the persona prompts feed every voice build:
   - The three `voice_step2_validation_*.md` (C55 event text) and `editor_dossier.md` (C64).
   - `pass_0a_voice_config.md` and `pass_0b_header.md` (§36).
   - `persona_pass_4a_user.md`, `persona_pass_6_user.md`, `persona_pass_1d_excerpt_selection.md` and `pass_1_6_merge.md` (§32.5 count drift).
9. **Tests.** Would each new test have failed on `main`'s bug? Does any test depend on the network, on athens-2026, or on test order or timing? `test_editor_flow.py`'s C66 test uses short sleeps.
10. **Ingest.** `runtime/ingest/app.py` (C58, `sys.executable`) and `dashboard.py`.

## Already known: don't re-report

- `personas/run_pass0b_dr_prompt.py` can't render its template (no Jinja loader). Filed in voices §36.
- Some prompt text sent to models still names models (e.g. `persona_pass_7a_fix.md`). Deferred to Stage 4.
- C66's live check (cache reads on a real run) is pending. The 13 published Athens dossiers start with a stray `**` (C64 residual, cleanup later).
- `personas/phase_5_cross_persona_qc.py` and `personas/scripts/standalone_pass4b_test.py` hardcode models by design; they're dev scripts, exempt.
- The branch names break `conventions.md`; that's handled at merge. The Step-2 validator is noisy (C42), which is a known design issue, not a branch bug.

## Report

Write `_workspace/planning/runtime/REVIEW_2026_09_28_phase0_fixes.md`. Don't commit it; the operator's main session files the findings in the trackers. Keep it to about two pages, with no praise:

1. **Verdict, first line:** ready to merge, merge after the listed fixes, or not ready.
2. **Findings, most severe first.** Severity is one of:
   - **BLOCKER:** wrong behavior on a production path.
   - **MAJOR:** wrong in a real but rarer case, or data risk.
   - **MINOR:** anything smaller that is still wrong.
   - **NIT.**

   Each finding gives `file:line`, what's wrong, a concrete failure scenario (inputs → wrong output), CONFIRMED or PLAUSIBLE, and a one-line fix direction.
3. **Behavior changes against `main` you found,** each marked intended (cite the tracker ID) or unexplained.
4. **Test gaps** that matter.
5. **What you checked and found sound**, one line per area, so the operator knows what the review covered.
