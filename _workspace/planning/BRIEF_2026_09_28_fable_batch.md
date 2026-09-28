# Brief: five Fable 5.1 tasks (prompts, Stage 4 prep, model-era audit, family of forms, spec check)

**For:** five separate sessions on **Fable 5.1** (`claude-fable-5-1`), one task each. Your first message tells you which task is yours.
**Written:** 2026-09-28 by the main working session, at the operator's request.
**Archive this brief** once all five outputs are filed (`_workspace/planning/WAYS_OF_WORKING.md` §11).

---

## Common setup and rules (all five tasks)

- **Checkout:** you are in your own git worktree. `phase0-fixes` is checked out in the main checkout, so run `git checkout --detach phase0-fixes`, which puts you at `0998fa2` or later. Read the code and docs as they are there.
- **You write exactly one file, your deliverable, and you don't commit it.** The main session copies it into the repo and files it. No other edits to code, prompts, docs or trackers.
- **No real API calls.** Don't run pipelines, persona runner scripts, or anything that calls a model. Never run pytest over `personas/scripts/`. Throwaway offline scripts under a scratch dir are fine; mention them.
- **`/Users/aienvironment/Desktop/AI Assembly/projects/athens-2026` is read-only.** The shipped voice cards (`voices/<slug>/07_persona_card_assembled.json`), corpora (`voices/<slug>/03_corpus/`), runs and published record are all there. Read them freely; never write or run git there.
- **Tracker first:** before reporting a problem, search `_workspace/planning/runtime/OPEN_ITEMS.md`, `_workspace/planning/voices/OPEN_ITEMS.md`, `_workspace/planning/doc_infrastructure_backlog.md` and the roadmap (`_workspace/planning/PLAN_2026_06_12_post_athens_roadmap.md`). Don't re-report filed items; add new evidence only if you have it.
- **Label claims:** CONFIRMED (read or run) vs PLAUSIBLE. Label inferences as inferences. Decisions belong to the operator, so present options and recommend one.
- **Write plainly:** outcome first, then detail, `file:line` for every code or prompt reference, no praise.
- **Voice-writing prompts are sensitive.** Any change to a prompt that shapes voice output needs a sentinel regeneration before it lands. You propose changes; you never apply them.
- **When done:** tell the operator the deliverable's path and a three-line summary.

**Filed already, don't re-report:**
- Athens / Munich event wording in prompts (PLAN 2.1 / C52; C55 fixed the three validators).
- "12 voices" and the Peter Thiel example in Provocateur prompts (C68 A14).
- "FROM NIGHT N-1" (C68 A15).
- Model names inside model-facing prompt text (voices §36 leftovers).
- "You are I am …" (C68 A6 / voices §37 A6).
- `run_pass0b_dr_prompt.py` can't render (voices §36).

---

## Task 1: prompt correctness review

**Scope:** all 75 prompt files: `personas/flows/shared/prompts/*.md` (56) and `runtime/flows/shared/prompts/*.md` (19), about 10,200 lines.

**Check:**
- **Placeholders vs code:** every `{{ var }}` / `{% include %}` / `.replace("{{…}}")` placeholder is filled by the code that renders it. Find the render calls: `render(...)`, `load_prompt(...)`, `str.replace`, Jinja environments. Also look for variables the code passes that no prompt uses.
- **Output contract vs schema:** a prompt that asks for fields should match what the parser or schema expects (`personas/schemas/*.py`, the parsers in the pass runners, `runtime/flows/*/` parsers).
- **Contradictions:** within a prompt, between passes that feed each other, and between a prompt and the current spec (`docs/README.md` says which specs to trust).
- **Stale facts:** council size and members, removed fields, retired passes, dead cross-references to other prompts or sections.
- **Dead prompts:** files that no code loads.

**Deliverable:** `_workspace/planning/runtime/REVIEW_2026_09_28_prompts_correctness.md`.
1. Verdict line.
2. Findings, most severe first (BLOCKER / MAJOR / MINOR / NIT). Each gives `file:line`, what's wrong, what goes wrong at runtime, and a one-line fix direction.
3. Coverage: which files were read fully and which were skimmed.

## Task 2: Stage 4 prep (prompt changes for the backport, drafted, not applied)

**Context:** Stage 4 (roadmap Phase 1.1) back-ports the architecture of the hand-corrected shipped cards into the persona prompts: "cards are canon, prompts catch up". Each change lands one at a time behind a sentinel regeneration.

**Items:** roadmap §1.1, items 1–7:
1. `voice_temporal_stance` in Pass 2 → the AF-LEADS architecture (athens-2026 commit `08a8253`; drop `anchored_override` emission).
2. Native "Voice of X" (Pass 0a + Pass 2; voices §18 item 1).
3. The mediated-voice / dramatist-vs-speaker clarification → Pass 2 / 3 / 4a. The draft is in `_workspace/archive/voices_consolidation_2026_05_01/HANDOFF_2026_04_28.md` §13.
4. The §31 fix pattern (Gaps C / E / D / G).
5. Gap-H `topics_requiring_care`.
6. §23 P0: `manual_grounding` + `editorial_rationale` → Pass 4a / 4b.
7. §19 Pass 0b phantom citations (path 3).

**Add:** voices §37 A6. Four shipped cards hold a first-person sentence in `council_member_name`. Say what Pass 2 should emit instead, from the card spec (`docs/AI_Assembly_Persona_Card_v2.md`).

**For each item:**
- **Evidence from the shipped cards:** quote the fields, name the voices.
- **The current prompt text** (`file:line`).
- **A proposed unified diff:** written in the doc, not applied.
- **Which voices to regenerate as sentinels,** and what to compare.
- **Risks,** and the order to land it in.

Note that `personas/scripts/sentinel_regen.py` can't run today (voices §37 A5). Say what the gate needs.

**Deliverable:** `_workspace/planning/voices/DESIGN_2026_09_28_stage4_prompt_backport.md`, with a one-page summary on top: items, order, effort, open operator decisions.

## Task 3: model-era prompt audit

- **Method:** invoke the Skill tool with skill `claude-api` and args `prompt-audit`, and follow that skill's instructions.
- **Scope:** both prompt directories, plus the code that assembles system prompts and requests (`runtime/flows/voice/_anthropic_call.py`, `runtime/flows/voice/card_assembly.py`, `runtime/flows/editor/card_assembly.py`, `personas/flows/shared/clients.py`, `personas/flows/shared/chat_prompt_builder.py`).
- **Target models:** production today is Claude Opus 4.7 and Sonnet 4.6. The migration candidates (runtime OPEN_ITEMS C62) are Opus 5.5 and Sonnet 5. `model_routing.json` holds the per-step setup.
- **Two questions:** what cruft written for older models can go now? And what would a C62 migration need in the prompts? Anything the loader already enforces (temperature, thinking, effort; see its docstring) needs no prompt change.
- **Deliverable:** `_workspace/planning/runtime/REVIEW_2026_09_28_prompts_model_era.md`: the skill's audit report plus its proposed diff, not applied.

## Task 4: Stage 5 design draft — family of forms

**Context:** the operator decided on 2026-06-13 to BUILD this (voices OPEN_ITEMS FU#55; roadmap §1.2 has the four-stage outline). It is exempt from the net-complexity gate **on one condition**: it needs only the one upstream Pass 4b edit, and it goes back under the gate if it grows. See `_workspace/planning/PRODUCT_assembly_hub.md` §11.6 and the roadmap's decisions block. The design must stay inside that condition, or say clearly where it can't.

**Draft:**
- **Schema:** `medium` becomes `{default_form, forms: [{name, calls_for, arc, length}]}`. Specify it exactly, including how it replaces today's three-field consistency problem, and what reads it.
- **Per-voice form menus, corpus-attested:** Cleopatra, Dostoevsky, Battuta, Scheherazade, Arendt and Marley, per roadmap §1.2 Stage 1.
  - Cite the corpus or card for each form (athens-2026 `voices/<slug>/03_corpus/`, the cards, voices §27's second-medium table).
  - Plato, Whanganui and Octopus follow the roadmap's special rules.
- **The runtime selection prompt:** the Step 2 `<form>` block, the continuity nudge, and the Gap-I discipline. Give proposed text.
- **Pipeline emission:** the Pass 4b edit.
- **Validation:** the two-night sandbox dryrun (what to measure, pass criteria), and the FU#55 resolution criteria.
- **Surface each voice change adds, and the open operator decisions.**

**Deliverable:** `_workspace/planning/voices/DESIGN_2026_09_28_family_of_forms.md`: a proposal for the operator's decision, not a build.

## Task 5: spec check of the not-yet-verified sections

**Scope:** check these against the code and report discrepancies:
- The Editor spec's Stage 1 routing, cost figures, and CLI list (flagged "not re-verified" in `STATE.md` and the spec's v3.1 changelog).
- `docs/AI_Assembly_Frame_Concept_v1.md` (last checked 2026-06-01).
- The Transcription spec's reflection-handling §7, marked stale in `docs/README.md`. Say what it should say now; see `runtime/scripts/reflections_to_session_package.py` and C68 A1.
- The rest of `docs/AI_Assembly_Runtime_Lifecycle.md`, beyond the Stage 6 section fixed on 2026-09-28.

**Skip:**
- The items being fixed right now under runtime OPEN_ITEMS C67 (read its table), because your checkout predates those fixes.
- Model-choice statements (they point at `model_routing.json`).

**Deliverable:** `_workspace/planning/runtime/REVIEW_2026_09_28_spec_check.md`. Per spec:
- Each discrepancy with its line, what the code does, and the proposed replacement text.
- A recommended trust rating for `docs/README.md`.
