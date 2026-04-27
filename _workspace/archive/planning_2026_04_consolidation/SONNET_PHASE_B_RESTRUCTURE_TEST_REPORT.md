# Phase B restructure — end-to-end test report

**Branch:** phase-b-rebuild @ 40164aa4f4607ba65c7e8e909fc4c52024e46a2e
**Date:** 2026-04-21
**Dostoevsky state:** §1–§4 present (opus4.6 outputs from ~/Desktop/); §5–§6 pending manual DR.

## Path migration corrections (done during Phase O)

After running the N migration on all three projects, several runners still
referenced old flat paths (`inputs/voices/`, `runs/<slug>/01_research/`, etc.).
These were updated as part of Phase O to unblock testing:

- `flows/shared/io.py:load_voice_input` — updated to `paths.voice_config()` with
  legacy fallback for unmigrated projects
- `run_pass0a_voice_config.py` — voice_config, review_doc, non_human_grounding,
  conference_facts, panel_roster writes updated to new paths
- `run_pass0b_dr_prompt.py` — voice_config read + monolithic_dr_prompt write updated
- `run_pass_0b_tailor.py` — all 3 dr_prompts paths + research input paths updated
- `run_phase0_1_research.py` — DR_PROMPTS_DIR removed; perplexity/gemini paths
  updated; base render writes to `paths.monolithic_dr_prompt()` directly
- `run_persona_pipeline.py` — pass1a/pass1b check paths updated; conference_facts
  updated; `(RUN / "01_research").mkdir(...)` replaced with `paths.ensure_voice_dirs()`

All 122 unit tests still pass after these changes.

## Per-section mode partial-state detection (O.1)

Command:
```
venv/bin/python run_persona_pipeline.py "Fyodor Dostoevsky" --project ../../projects/phase-l-dostoevsky
```

Result (with §1–§4 present, §5–§6 absent):
```
[11:47:51] NODE 0: validating Fyodor Dostoevsky  (PROJECT_ROOT=.../phase-l-dostoevsky)
[11:47:51]   type=human voice_mode=narratival hostile=False
[11:47:51]   CACHE HIT: Pass 1a (pre-computed) -> 01_perplexity_dossier.json
[11:47:51] PASS 1a: loaded Perplexity dossier (136908 chars)
[11:47:51]   CACHE HIT: Pass 1b (pre-computed) -> 02_gemini_broad_scan.json
[11:47:51] PASS 1b: loaded Gemini broad scan (16592 chars)
[11:47:51] ERROR: Partial DR state for fyodor_dostoevsky: 4/6 section files present.
           Missing: sections [5, 6]. Complete DR for these before running pipeline.
```

**Verdict: PASS** — partial state detected cleanly with specific missing section numbers.

## Monolithic fallback smoke test (O.2)

Concatenated §1–§4 into `07_concat_claude_dr.md`, removed per-section files, re-ran:

```
[11:48:08] PASS 1a-DR: detected DR mode = monolithic
[11:48:08]   monolithic DR: 180,804 chars
[11:48:08] PASS 1 (Phase B): chunked merge 1.1-1.7 (parallel + coherence)
[11:48:08] [orchestrator] DR mode: monolithic
[11:48:08] [orchestrator] Phase 1A — chunks 1.1-1.6 in parallel (max_parallel=3)
[11:48:08] Pass 1.1 BIOGRAPHICAL merge: 'Fyodor Dostoevsky' (slug=fyodor_dostoevsky, fixtures=False)
```

Pipeline reached chunk orchestrator successfully. Aborted before API calls (smoke
test only — §3–§6 missing would produce thin chunk outputs anyway).

**Verdict: PASS** — monolithic mode detected, concat loaded (180,804 chars), chunks
started correctly.

## Restore verification (O.3)

Per-section files (§1–§4) restored from ~/Desktop/ Desktop backups; concat removed.
Final dossier dir state: `01_section_1.md`, `02_section_2.md`, `03_section_3.md`,
`04_section_4.md`.

## Unit test suite (O.4)

```
122 passed in 0.47s
```

All 122 tests pass: paths, header/footer, split, perplexity_split, chunk_runner,
dr_validation, pipeline tests.

## Verdict

**Ready for Phase P documentation sweep.**

Phase L full end-to-end still requires Dostoevsky §5–§6 DR completion (operator
task — manual claude.ai sessions). When those land at `01_research/04_dr_dossier/`,
`run_persona_pipeline.py` will auto-detect per_section mode and proceed.

Known remaining stale paths (docstrings/comments only — Phase P will clean these):
- `run_phase0_1_research.py` module docstring (lines 13–15)
- `run_pass0a_voice_config.py` module docstring (lines 6–11)
- `run_pass0b_dr_prompt.py` module docstring (line 7)
- `run_pass_0b_tailor.py` module docstring (lines 14–18)
- `flows/shared/dr_validation.py` comment (line 49)
- `schemas/voice_config.py` doc string (line 47)
