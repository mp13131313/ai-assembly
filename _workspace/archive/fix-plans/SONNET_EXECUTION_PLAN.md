# Sonnet Execution Plan — Walkthrough Fixes

> **Historical note:** This document describes the transition to Opus 4.6. The current pipeline runs on Opus 4.7 as of commit 35bc8fd (2026-04-17). Content preserved as-is for traceability.

**Paste this into a fresh Claude Sonnet 4.6 session. The plan is self-contained.**

## Your task

Execute the 14 fixes listed in `personas/notes/WALKTHROUGH_FIXES_PENDING.md` in the ordered phases below. Commit after each phase with the specified commit message. Push the branch at the end. Stop and ask if anything is unclear or a verification fails — do NOT proceed through broken state.

## Preflight

1. Read these in order:
   - `personas/notes/WALKTHROUGH_FIXES_PENDING.md` (substantive fix content — this is the source of truth for WHAT to change)
   - `docs/AI_Assembly_Persona_Pipeline_v3_7.md` (spec; skim for context)
   - `personas/run_stage0a_intake.py`, `personas/run_stage0b_dr_prompt.py`, `personas/run_persona_pipeline.py` (files you'll modify heavily)
   - `personas/flows/shared/prompts/stage_0a_intake.md`, `personas/flows/shared/prompts/stage_0b_dr_prompt.md`
   - `personas/flows/shared/node0_validation.py`, `personas/flows/shared/io.py` (validation + shared utilities)

2. Create a feature branch:
   ```bash
   cd /Users/aienvironment/Desktop/ai-assembly
   git checkout -b walkthrough-fixes-2026-04-17
   ```

3. Verify you're on a clean tree (no uncommitted changes).

## Phase A — Renames and structural changes

These come first because subsequent fixes touch the renamed files.

### A.1 — Fix #5 (rebrand Stage→Pass + voice_mode strict validation)

Execute per `WALKTHROUGH_FIXES_PENDING.md` §5.

- Rename files:
  - `personas/run_stage0a_intake.py` → `personas/run_pass0a_voice_config.py` (use `git mv`)
  - `personas/run_stage0b_dr_prompt.py` → `personas/run_pass0b_dr_prompt.py`
  - `personas/flows/shared/prompts/stage_0a_intake.md` → `personas/flows/shared/prompts/pass_0a_voice_config.md`
  - `personas/flows/shared/prompts/stage_0b_dr_prompt.md` → `personas/flows/shared/prompts/pass_0b_dr_prompt.md`
- Grep for every `Stage 0a` / `Stage 0b` / `stage_0a` / `stage_0b` reference in the repo (excluding `personas/runs/**` and `runtime/runs/**` and `personas/inputs/voices/_archive/**`) — replace with `Pass 0a` / `Pass 0b` / `pass_0a` / `pass_0b`. Prompt load calls in the Python files use `load_prompt("stage_0a_intake")` etc.; update to `load_prompt("pass_0a_voice_config")`.
- `node0_validation.py`: revert the freeform `voice_mode` relaxation. Change the validation to strict three-value: reject if `voice_mode not in {"philosophical", "observational", "narratival"}`. Add a clear error message.
- Do NOT rename `voice_mode` to `construction_method`. Keep the spec's field name.

Verify:
- `python -c "from pathlib import Path; assert Path('personas/run_pass0a_voice_config.py').exists()"`
- `grep -r "Stage 0a" personas/ --include="*.py" --include="*.md" | grep -v "runs/" | grep -v "_archive/"` returns nothing (or only in WALKTHROUGH_FIXES_PENDING.md which documents the rename).
- `cd personas && python3 -c "from flows.shared.node0_validation import validate_input"` imports cleanly.

**Commit:** `refactor: rebrand Stage 0a/0b to Phase 0 Pass 0a/0b, restore strict voice_mode validation`

### A.2 — Fix #1 (Opus 4.6 → Opus 4.7)

Execute per `WALKTHROUGH_FIXES_PENDING.md` §1.

- Replace every `claude-opus-4-6` string with `claude-opus-4-7` in:
  - `personas/run_pass0a_voice_config.py`
  - `personas/run_pass0b_dr_prompt.py`
  - `personas/run_persona_pipeline.py`
  - `personas/flows/shared/clients.py` (check defaults)
  - `runtime/flows/researcher_flow.py`
  - `runtime/flows/provocateur_flow.py`
  - `runtime/flows/transcription_flow.py`
  - `.env.example`, `personas/.env.example`, `runtime/.env.example`
- Replace `Opus 4.6` / `opus 4.6` in doc markdown:
  - `docs/AI_Assembly_Persona_Pipeline_v3_7.md`
  - `docs/AI_Assembly_Researcher_Pipeline.md`
  - `docs/AI_Assembly_Provocateur_Pipeline.md`
  - `docs/AI_Assembly_Transcription_Pipeline.md`
  - `personas/notes/IMPLEMENTATION_AUDIT_v3_7.md`
  - `personas/inputs/dossiers/CLAUDE_DR_BRIEFING.md`
  - `personas/inputs/dossiers/README.md`
  - `personas/flows/shared/prompts/pass_0a_voice_config.md`
  - `personas/flows/shared/prompts/persona_pass_7b_provocations.md`
  - `personas/flows/shared/prompts/persona_pass_1merge_three_way_user.md`
  - All prompt files under `personas/flows/shared/prompts/` — grep to find.
- **DO NOT** modify any file under `personas/runs/**` or `runtime/runs/**`. These are historical records.
- **DO NOT** rename Sonnet 4.6 references. Sonnet stays.

Verify:
- `grep -rn "claude-opus-4-6" --include="*.py" personas/ runtime/` returns nothing.
- `grep -rn "claude-opus-4-6" --include="*.md" --include="*.json" --include="*.example"` returns only `personas/runs/**` or `runtime/runs/**` paths.

**Commit:** `refactor: upgrade Opus 4.6 → Opus 4.7 across code, configs, and specs`

## Phase B — Schema simplifications

### B.1 — Fix #2 (remove impossible filter)

Per `WALKTHROUGH_FIXES_PENDING.md` §2.

- `personas/flows/shared/node0_validation.py`: remove the `impossible is not True` rejection block.
- `personas/flows/shared/prompts/pass_0a_voice_config.md`: remove the `impossible` field from the schema and remove any instructions asking the model to emit it.
- `docs/AI_Assembly_Persona_Pipeline_v3_7.md`: remove `impossible` from the Input schema example (around line 120-140) and from Node 0 validation spec (around line 620).
- `docs/AI_Assembly_Persona_Card_v2.md`: remove any mention.
- `personas/inputs/voices/plato.json`, `cleopatra.json`, `hannah_arendt.json`, `octopus.json`: remove the `impossible` key.

Verify: `grep -rn '"impossible"' personas/ --include="*.py" --include="*.md" --include="*.json"` returns nothing outside `_archive/` and `runs/`.

**Commit:** `refactor: remove impossible filter from pipeline (was conceptual premise, not functional gate)`

### B.2 — Fix #8 (strip editorial-assets from voice_config schema)

Per `WALKTHROUGH_FIXES_PENDING.md` §8.

- `personas/flows/shared/prompts/pass_0a_voice_config.md`: remove from the schema block and all instructions:
  - `voice_type_adjustments_needed`
  - `counter_tradition_scholars`
  - `dominant_hostile_sources`
  - `contested_interpretations`
  - `material_culture_evidence`
  - `voice_specific_warnings`
- `personas/run_pass0a_voice_config.py`: the key-presence check currently validates `voice_config` and `review_doc` — keep that. No editorial-asset key validation.
- Voice configs: remove these fields from all files in `personas/inputs/voices/` (not `_archive/`).

Verify: `grep -rn "counter_tradition_scholars\|dominant_hostile_sources\|contested_interpretations\|material_culture_evidence\|voice_specific_warnings\|voice_type_adjustments_needed" personas/ --include="*.py" --include="*.md" --include="*.json" | grep -v "_archive\|runs/\|WALKTHROUGH_FIXES_PENDING"` returns nothing.

**Commit:** `refactor: drop editorial-assets from voice_config schema (beyond-spec; research sources identify specifics themselves)`

### B.3 — Fix #7 (primary_text_sources removed from Pass 0a output)

Per `WALKTHROUGH_FIXES_PENDING.md` §7.

- `personas/flows/shared/prompts/pass_0a_voice_config.md`: remove `primary_text_sources` from the schema block and any instructions about it.
- `personas/run_pass0a_voice_config.py`: after `call_claude` returns, if the model accidentally emitted `primary_text_sources`, strip it before writing the voice_config. Add a comment explaining the field is now manual-override-only.
- `node0_validation.py`: ensure `primary_text_sources` remains optional with default `[]` (already is — verify).
- `run_persona_pipeline.py:219-222`: keep the override branch. Unchanged.

Verify: `grep -n "primary_text_sources" personas/flows/shared/prompts/pass_0a_voice_config.md` returns nothing (outside review_doc explanations if you kept any).

**Commit:** `refactor: remove primary_text_sources from Pass 0a output (now manual-edit hook only)`

### B.4 — Fix #11 (corpus_constraint enum align with spec)

Per `WALKTHROUGH_FIXES_PENDING.md` §11.

- `personas/flows/shared/prompts/pass_0a_voice_config.md`: update the `corpus_constraint` field definition to the spec's three values: `"full" | "lyrics — describe patterns only" | "hostile — read against grain"`. Update all examples. Remove references to `restricted` / `fragmentary` / `reconstructed`.
- `personas/inputs/voices/*.json`: if any voice_config has `corpus_constraint` in the four-value enum, update to the three-value enum per the mapping in WALKTHROUGH_FIXES_PENDING.md §11.
- `node0_validation.py`: already accepts the three-value enum via `VALID_CORPUS_CONSTRAINTS`. Verify and leave as-is.

Verify: `grep -n "corpus_constraint" personas/flows/shared/prompts/pass_0a_voice_config.md` shows only the three-value enum.

**Commit:** `refactor: align corpus_constraint enum with spec (three values, not four)`

### B.5 — Fix #12 (non_human_subtypes trim)

Per `WALKTHROUGH_FIXES_PENDING.md` §12.

- `personas/flows/shared/node0_validation.py:83`: change `non_human_subtypes = {"organism", "system", "legal_entity", "river_personhood"}` to `non_human_subtypes = {"organism", "system"}`.
- `personas/flows/shared/prompts/pass_0a_voice_config.md`: update the subtype definition to list only `"organism"` and `"system"`. Remove references to other values.
- Voice configs: ensure any `subtype` value is either `null`, `"organism"`, or `"system"`. (Whanganui — check — should be `"system"`.)

Verify: `grep -rn '"legal_entity"\|"river_personhood"\|"literary_character"' personas/ --include="*.py" --include="*.md" --include="*.json" | grep -v "_archive\|runs/"` returns nothing.

**Commit:** `refactor: trim non-human subtypes to spec's {organism, system}`

### B.6 — Fix #6 (Pass 0a URL-emission audit)

Per `WALKTHROUGH_FIXES_PENDING.md` §6.

- `personas/flows/shared/prompts/pass_0a_voice_config.md`: grep for any instruction that tells the model to emit URLs or `primary_text_sources`. If found, remove. If the prompt already explains in the review doc section that Pass 0a doesn't do URLs (my read of lines 120-122 of the current prompt shows this), leave that explanation.
- `personas/run_pass0a_voice_config.py`: after `call_claude`, add a defensive strip of `primary_text_sources` from the model output before writing voice_config (as specified in B.3 above — may already be done).

Verify: a smoke test — run `cd personas && python3 run_pass0a_voice_config.py "Ibn Battuta" --hint "the Moroccan traveler"` and confirm the resulting `inputs/voices/ibn_battuta.json` has NO `primary_text_sources` field or URLs. If it does, the stripping logic didn't fire — fix.

**Commit:** `fix: audit Pass 0a prompt for URL emission (no internet access — URLs were hallucinated)`

## Phase C — Pass 0b rewrite

### C.1 — Fix #9 (rewrite Pass 0b as spec Pass 1a prompt instantiator)

Per `WALKTHROUGH_FIXES_PENDING.md` §9.

This is the biggest substantive change. Pass 0b's job becomes: take the voice_config, produce a paste-ready Claude DR prompt that is essentially the spec's Pass 1a user prompt ([spec lines 817-1008](../../docs/AI_Assembly_Persona_Pipeline_v3_7.md)) with substitutions and branching.

**New contents of `personas/flows/shared/prompts/pass_0b_dr_prompt.md`:**

The prompt tells the Pass 0b LLM to take the voice_config + project_context and emit a `dr_prompt` string. The `dr_prompt` should:

1. Start with a preamble telling the human to paste into claude.ai with Opus 4.7 + Extended Thinking + Deep Research enabled.
2. Body: the spec's Pass 1a user prompt for the voice's `type`:
   - `type == "human"`: the six-section HUMAN variant ([spec lines 817-888](../../docs/AI_Assembly_Persona_Pipeline_v3_7.md))
   - `type == "non-human"`: the six-section NON-HUMAN variant ([spec lines 890-950](../../docs/AI_Assembly_Persona_Pipeline_v3_7.md))
   - `type == "fictional"`: the six-section FICTIONAL variant ([spec lines 952-1008](../../docs/AI_Assembly_Persona_Pipeline_v3_7.md))
3. `{% if hostile_sources %}` appendix: the HOSTILE SOURCE WARNING block ([spec lines 866-887](../../docs/AI_Assembly_Persona_Pipeline_v3_7.md)), which tells Claude DR to identify hostile sources and counter-traditions itself (no pre-populated scholar names).
4. `{% if subtype == "system" %}` addendum for system entities ([spec lines 928-949](../../docs/AI_Assembly_Persona_Pipeline_v3_7.md)).
5. `{{name}}` substituted throughout (with optional `(disambiguation hint)` appended if hint present).
6. A closing instruction: "Save the result as `inputs/dossiers/<voice_slug>_claude_dr.md`. Target 15,000-25,000 words. Use the six section headings exactly as given."
7. Note: the existing `CLAUDE_DR_BRIEFING.md` at `personas/inputs/dossiers/` documents the six-section contract for reference — Pass 0b's output is a per-voice instantiation of that contract.

**Remove from `pass_0b_dr_prompt.md`:** all editorial-asset weaving. No `counter_tradition_scholars`, no `dominant_hostile_sources`, no `contested_interpretations`, no `material_culture_evidence`, no `voice_specific_warnings`, no `voice_type_adjustments_needed` references.

**Update `personas/run_pass0b_dr_prompt.py`:**
- Remove the `required_assets` check block (lines ~66-79 of the current code) — those fields no longer exist.
- Update the completion stamp — no longer prints counts of woven-in editorial items (they're gone).

Verify: run `cd personas && python3 run_pass0b_dr_prompt.py "Ibn Battuta"` (after first running Pass 0a for Ibn Battuta). Confirm the generated `inputs/dossiers/_dr_prompts/ibn_battuta_dr_prompt.md` is the spec's Pass 1a prompt with substitutions, not voice-specific editorial scaffolding.

**Commit:** `refactor: rewrite Pass 0b as spec's Pass 1a prompt instantiator (no editorial-asset weaving)`

## Phase D — Robustness + new features

### D.1 — Fix #3 (retry on error)

Per `WALKTHROUGH_FIXES_PENDING.md` §3.

Wrap the `call_claude(...)` calls in `run_pass0a_voice_config.py` and `run_pass0b_dr_prompt.py` in a retry-once-on-failure block. Catch `json.JSONDecodeError`, `anthropic.APIError`, `anthropic.RateLimitError`. On retry: log the failure, wait 15s, retry once. On second failure: `sys.exit` with clear message.

**Commit:** `fix: retry-once on JSON/API errors in Pass 0a and Pass 0b`

### D.2 — Fix #4 (require --hint for ambiguous names)

Per `WALKTHROUGH_FIXES_PENDING.md` §4.

Simplest implementation: require `--hint` always. Modify the argparse in `run_pass0a_voice_config.py` to require `--hint`. Update the script's `--help` text.

Update any docs / README that show the old "--hint optional" usage.

**Commit:** `fix: Pass 0a requires --hint always (prevents name-disambiguation errors)`

### D.3 — Fix #10 (subtype=system overrides in Pass 3/5/7b prompts)

Per `WALKTHROUGH_FIXES_PENDING.md` §10.

Five new blocks total:
- Pass 3 Block 3 system override (before voice_mode branching)
- Pass 3 Block 4 split (organism vs system sub-branches inside current `else`)
- Pass 5 Block 3 system override (before voice_mode branching)
- Pass 5 Block 4 split (organism vs system)
- Pass 7b new `{% if subtype == "system" %}` block

Prompts use Jinja2 (`{% if %}`), not Handlebars. Follow the substantive guidance in WALKTHROUGH_FIXES_PENDING.md §10. Place new blocks such that `subtype=system` pre-empts `voice_mode` branching.

Files:
- `personas/flows/shared/prompts/persona_pass_3_intellectual_core.md`
- `personas/flows/shared/prompts/persona_pass_5_engagement.md`
- `personas/flows/shared/prompts/persona_pass_7b_provocations.md`

**Commit:** `fix: add subtype=system overrides to Pass 3/5/7b prompts (Whanganui support)`

### D.4 — Fix #13 (Pass 1-merge model upgrade)

Per `WALKTHROUGH_FIXES_PENDING.md` §13.

In `personas/run_persona_pipeline.py`, locate the `_pass_1merge` function (around line 145). Change:
- `model="claude-sonnet-4-6"` → `model="claude-opus-4-7"`
- `max_tokens=4096` → `max_tokens=16000`
- `thinking_budget=None` is already adaptive; leave it.

Update the log line to reflect the new model.

**Commit:** `fix: upgrade Pass 1-merge to Opus 4.7 + adaptive thinking (three-way contradiction detection is hard)`

### D.5 — Fix #14 (primary-text review gate)

Per `WALKTHROUGH_FIXES_PENDING.md` §14.

Insert a human-in-the-loop pause between Pass 1c fetch and Pass 1d in `run_persona_pipeline.py`.

Implementation:
1. After `pass1c = call_or_cache(RUN / "01_research/primary_texts.json", "Pass 1c", _pass_1c)` (around line 254), check if `01_research/primary_texts_reviewed.flag` exists.
2. If absent:
   - Write a review markdown at `01_research/primary_texts_review.md` listing: URLs identified (with source: Perplexity / Claude DR / Gemini), fetch status per URL, passages retrieved with char counts, flags for `corpus_constraint == "lyrics — describe patterns only"` or `subtype == "system"`, and instructions for the human.
   - Print a clear message: "REVIEW GATE: Read `<path>/primary_texts_review.md`. Edit `01_research/primary_texts.json` if needed. Then create `01_research/primary_texts_reviewed.flag` and re-run."
   - `sys.exit(0)`.
3. If flag present: proceed to Pass 1d.

Write a helper `_build_primary_texts_review(...)` that generates the markdown from `pass1c_extract` + `pass1c` data.

**Commit:** `feat: add human-review gate for primary texts after Pass 1c fetch (per spec Node 1c manual-review-gate)`

## Phase E — Final verification and push

### E.1 — Syntax / import smoke tests

```bash
cd /Users/aienvironment/Desktop/ai-assembly/personas
python3 -c "import run_pass0a_voice_config"
python3 -c "import run_pass0b_dr_prompt"
python3 -c "import run_persona_pipeline"
python3 -c "from flows.shared.node0_validation import validate_input"
python3 -c "from flows.shared.io import load_prompt; load_prompt('pass_0a_voice_config'); load_prompt('pass_0b_dr_prompt'); load_prompt('persona_pass_3_intellectual_core')"
```

All should succeed. If any fail, diagnose and fix.

### E.2 — Validate existing voice_configs against updated schema

```bash
cd personas
for f in inputs/voices/*.json; do
  if [[ -f "$f" ]]; then
    python3 -c "
import json
from flows.shared.node0_validation import validate_input
data = json.load(open('$f'))
try:
    validate_input(data)
    print('OK: $f')
except Exception as e:
    print('FAIL: $f —', e)
"
  fi
done
```

Any FAIL means the schema changes need follow-up in that voice_config. Fix as needed.

### E.3 — Update spec doc to v3.8

In `docs/AI_Assembly_Persona_Pipeline_v3_7.md`:
- Rename file to `AI_Assembly_Persona_Pipeline_v3_8.md` (use `git mv`)
- Update `**Status:** v3.7 — ...` to `**Status:** v3.8 — walkthrough cleanup (2026-04-17)`
- Add a new Changelog section at the top titled `**Changelog from v3.7:**` summarizing: Opus 4.7 upgrade, impossible filter removal, corpus_constraint enum aligned, subtype trimmed, editorial-assets removed from voice_config, Pass 0b rewritten as Pass 1a prompt instantiator, subtype=system overrides added to Pass 3/5/7b, Pass 1-merge upgraded to Opus, primary-text review gate added.
- Update `CURRENT_STATE.md` references to the spec file and the v3.7 → v3.8 version change.

**Commit:** `docs: bump pipeline spec to v3.8 with walkthrough-cleanup changelog`

### E.4 — Briefing doc cleanup: v2 → v3.1

The briefing doc was superseded on 2026-04-17. `AI_Assembly_Briefing_v3_1.md` is now canonical; `AI_Assembly_Briefing_v2.md` is obsolete and must be deleted with references updated.

**Delete:** `docs/AI_Assembly_Briefing_v2.md` (use `git rm`).

**Update references** — in each of the following, replace `AI_Assembly_Briefing_v2.md` → `AI_Assembly_Briefing_v3_1.md` and `Briefing v2` → `Briefing v3.1`:
- `docs/CURRENT_STATE.md` (multiple references — update the pointer + any "target state" prose)
- `docs/README.md` (table of contents / staleness annotations)
- `CLAUDE.md` (repo root — the "Where specs live" block)

**Verify:**
```bash
grep -rn "AI_Assembly_Briefing_v2\|Briefing v2" /Users/aienvironment/Desktop/ai-assembly --include="*.md" --include="*.py"
```
Should return nothing (except inside the deleted file, which no longer exists, or inside `AI_Assembly_Briefing_v3_1.md` itself if it mentions its own predecessor in the version-history block — that's fine, leave it).

**Commit:** `docs: delete superseded Briefing v2, update references to v3.1`

### E.5 — Push

```bash
git push -u origin walkthrough-fixes-2026-04-17
```

Report back with the branch URL (if remote has a UI) or just confirm the push completed. Note any verification failures or points where you had to improvise beyond the plan.

## Notes for Sonnet

- **If you hit an ambiguity:** stop and write a comment inside `WALKTHROUGH_FIXES_PENDING.md` under a new `## Sonnet Questions` section, then ask the user. Do NOT guess and proceed.
- **If a verify step fails:** stop immediately. Do not commit broken state.
- **If you finish earlier than expected:** run one additional check — generate a Pass 0a output for a new voice (e.g. `Peter Thiel`) as a full smoke test. Do NOT run the full persona pipeline (too expensive).
- **Do NOT edit:** `personas/runs/**`, `runtime/runs/**`, `personas/inputs/voices/_archive/**`.
- **Do NOT commit:** any file containing API keys.
- **Branch must be clean at the end:** no uncommitted changes, no untracked files outside `.gitignore`.
