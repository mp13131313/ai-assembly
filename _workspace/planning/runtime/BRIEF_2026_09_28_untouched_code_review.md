# Brief: review of the code `phase0-fixes` does *not* change (before the merge into `main`)

**For:** a separate review session on **Fable 5.1** (`claude-fable-5-1`).
**Written:** 2026-09-28 by the main working session, at the operator's request.
**Archive this brief** once its findings are filed (`_workspace/planning/WAYS_OF_WORKING.md` §11).

---

## Why this exists

A second session is already reviewing the branch's **diff** (`BRIEF_2026_09_28_phase0_fixes_review.md`). That leaves two blind spots, which this review covers:

1. **The ripple zone (merge-critical).** Code the diff doesn't touch, but that behaves differently after the merge because it calls, imports or reads something the branch changed.
2. **The untouched code itself.** About 67 Python files (~11,400 lines) and 69 prompt files in `runtime/` and `personas/` carry into `main` unchanged. Most of it had one full read on 2026-06-12/13 (see the roadmap's Appendix B). Yours is a second, independent pass.

**Review only:** don't fix, don't commit, don't push, don't merge. Your output is one report file (last section).

## Setup

- **Worktree:** check out branch `phase0-fixes` (`07ff244` or later), and review the code as it will be after the merge.
- **The untouched set:** `git ls-files runtime personas` minus `git diff --name-only main...phase0-fixes`. Tests and fixtures are only in scope when they're wrong.
- **Venvs and test commands:** the same as in `BRIEF_2026_09_28_phase0_fixes_review.md` §Setup.
  - Baseline: runtime 368, ingest 114, personas 242.
  - Ingest needs a scratch project root holding a copy of `athens-2026/reference/*.json`.

## Hard rules

- **No real API calls.** Don't run any pipeline, persona runner script, or anything that calls a model. Never run pytest over `personas/scripts/`.
- **`/Users/aienvironment/Desktop/AI Assembly/projects/athens-2026` is read-only.** Reading real files there to check data shapes is encouraged.
- **Don't edit code.** A throwaway script under a scratch dir to prove a finding is fine; say so in the report.
- **Label every finding** CONFIRMED (you read the path or ran it) or PLAUSIBLE.
- **Don't re-review the diff.** Diff files are the other session's job. Open them only to trace a ripple.

## Part 1: the ripple zone (do this first)

For each interface below, which the branch changed, find every **untouched** caller or reader. Check it still works with the new behavior. A bug there is merge-blocking.

| What changed | New behavior | Where to look for untouched users |
|---|---|---|
| **Model choice** | Every LLM step reads `model_routing.json` via `flows/shared/model_routing.py`. `call_claude(step=…)` in personas; `stream_voice_call(cfg=…)` in runtime. Model names are no longer hardcoded (a test enforces it). The legacy env vars still override: an empty value counts as unset, and `CLAUDE_MODEL` covers runtime steps only. | Anything calling `call_claude`, `stream_voice_call`, `call_openai`, `call_gemini` or `_stream_and_parse`, or reading `*_MODEL` / `*_THINKING` env vars, especially `personas/run_pass_1_*.py`, `personas/scripts/*`, `runtime/scripts/*` and `personas/phase_5_cross_persona_qc.py` (exempt by design; check it still *runs*). |
| **Voice display names** (C53) | Names come from `council_config.json` by slug: "Voice of X", or "the Voice of X" in headnotes. `flows/shared/io.py: voice_display_name` | Untouched code reading `council_member`, `voice_name` or headnotes: `runtime/flows/editor/publish.py`, `runtime/flows/voice/card_assembly.py`, `runtime/ingest/*` (dashboard pages), `runtime/scripts/*`. |
| **Published indexes** (C46, C50, C51) | The night dossier index has two writers that merge (owned-key sets in `editor/edition.py`). Voice night indexes are rebuilt from disk. Per-theme files now exist. C64 removed the `issue_no`, `vol` and `publication_date` reads. | Untouched readers of `published_artifacts/**`: `editor/publish.py`, the ingest pages, `runtime/scripts/*`. Also flag anything the external microsite might depend on (you can't see it; note the risk). |
| **Orchestrator dispatch** (C54) | Dispatch goes through `infer_state`. | Untouched code writing `status.json` / sentinel files the orchestrator reads: `runtime/ingest/pipeline.py`, `runtime/ingest/sessions.py`, `runtime/flows/vendor_intake.py`, `runtime/scripts/reset_run.py`. |
| **Transcription fallback** (C49) | On a speaker-ID JSON-decode failure, an automatic passthrough mapping plus a `speaker_id_auto_passthrough` flag. | Untouched consumers of `session_package.json` / review files: `vendor_intake.py`, `reflections_to_session_package.py`, `markdown_to_researcher_output.py`, the ingest pages. |
| **Editor** (C64, C65, C66) | `--no-cache` became `--no-prompt-cache` (manifest key `config.no_prompt_cache`). The first dossier call runs alone. Dossier schema fixes. | Untouched code invoking `editor_flow.py` or reading its manifest: the orchestrator's command lines, the ingest dashboard, `runtime/scripts/*`, and docs that give run commands. |
| **Persona prompts / templates** (§32, §36) | `prompt_render.model_name(step)` is a template global. `pass_0b_header.md` renders the Deep Research model. Two 7pre_citation prompts were deleted. | Untouched templates and Jinja environments: `personas/scripts/split_tailored_prompt.py`, `personas/run_pass0b_dr_prompt.py` (known broken, don't report), other `{% include %}` users, and any code still referencing the deleted prompts. |

## Part 2: audit of the untouched code, riskiest first

1. **Production runtime paths:**
   - `runtime/ingest/{pipeline,sessions,auth,config,render}.py`: the producer upload app, including auth.
   - `runtime/flows/vendor_intake.py`
   - `runtime/flows/voice/card_assembly.py`: builds every voice's system prompt.
   - `runtime/flows/editor/publish.py`
   - `runtime/flows/shared/project_root.py`
2. **Production persona paths:**
   - `personas/flows/shared/{io,paths,manifest,patch_walker,bracket_strip,dr_validation,research_validation,node0_validation,node1c_fetch,node1d_excerpt_selection,perplexity_split,url_extract,wikipedia,project_root}.py`
   - `personas/schemas/*.py`
   - `personas/run_pass_1_*.py`
3. **Untouched prompts that shape voice output:** `personas/flows/shared/prompts/*` and `runtime/flows/shared/prompts/*`. Look for placeholders the code never fills, instructions that contradict each other, and leftover event wording. (Athens and Munich wording is already filed in PLAN 2.1; count it only if it's a new instance.)
4. **Operator scripts:** `runtime/scripts/{reset_run,generate_sessions_json,generate_speakers_json,apply_ai_assembly_flags_from_csv,reflections_to_session_package,markdown_to_researcher_output}.py`, `personas/scripts/{sentinel_regen,invalidate_cache,split_tailored_prompt,validate_dr_dossier}.py`.
   - `reset_run` and `invalidate_cache` delete files: check their guards.
5. **Dev / audit scripts, last:** `personas/scripts/{arch_03_*,migrate_to_per_voice_layout,standalone_pass4b_test}.py`, `personas/phase_5_cross_persona_qc.py`. Only report things that are broken or dangerous.

What to look for: wrong behavior on real data shapes, crashes on edge cases, silent data loss or overwrite, security issues in the ingest app (auth, paths, uploads), dead or unreachable code a caller still relies on, and anything that contradicts the current specs (`docs/README.md` says which specs to trust).

## Already known: don't re-report

- **Before reporting anything, search the trackers for the file or function:** `_workspace/planning/runtime/OPEN_ITEMS.md`, `_workspace/planning/voices/OPEN_ITEMS.md` (§31, §32), `_workspace/planning/doc_infrastructure_backlog.md`, and the roadmap's Appendix B. If it's already filed, skip it, or note "already filed as X" if you have new evidence.
- **Known and filed:**
  - `personas/run_pass0b_dr_prompt.py` can't render its template (voices §36).
  - Model names still appear in text sent to models (Stage 4).
  - Event hardcoding: `choices=[1,2,3]`, `DATE_TO_NIGHT`, `DAY_TO_RUN`, Athens wording (PLAN 2.1 / C52).
  - The stray `**` in published dossiers (C64 residual).
  - Branch naming (handled at merge).

## Report

Write `_workspace/planning/runtime/REVIEW_2026_09_28_untouched_code.md` and don't commit it. About two to three pages, with no praise:

1. **Verdict, first line:** ripple zone clear or not clear for the merge, plus one line on the untouched code overall.
2. **Ripple-zone findings**, most severe first.
3. **Audit findings**, most severe first.
   - Severity for both lists: **BLOCKER** (wrong on a production path), **MAJOR**, **MINOR**, **NIT**.
   - Each finding gives `file:line`, what's wrong, a concrete failure scenario, CONFIRMED or PLAUSIBLE, and a one-line fix direction.
4. **Coverage:** what you read fully, what you skimmed, and what you skipped, so the operator knows what the review covered.
