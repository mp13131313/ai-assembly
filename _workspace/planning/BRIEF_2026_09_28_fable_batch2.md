# Brief: five more Fable 5.1 tasks (split card + event config, validator evidence, card-field utility, validation-track memo, writing sources)

**For:** five separate sessions on **Fable 5.1** (`claude-fable-5-1`), one task each. Your first message tells you which task is yours.
**Written:** 2026-09-28 by the main working session, at the operator's request.
**Archive this brief** once all five outputs are filed (`_workspace/planning/WAYS_OF_WORKING.md` §11).

---

## Common setup and rules (all five tasks)

- **Checkout:** you're in your own git worktree. Run `git checkout --detach phase0-fixes` to get the latest branch state.
- **You write exactly one file, your deliverable, and don't commit it.** The main session copies it into the repo and files it. No other edits.
- **No real API calls.** Don't run any pipeline, persona runner script, or anything that calls a model. Never run pytest over `personas/scripts/`. Offline scripts that read, count or sample data are encouraged; mention them.
- **`/Users/aienvironment/Desktop/AI Assembly/projects/athens-2026` is read-only.** Everything from Athens is there:
  - `voices/<slug>/`: the shipped cards `07_persona_card_assembled.json`, the corpora `03_corpus/`, and the build passes.
  - `runs/athens_night_{1,2,3}/`: `01_transcription`, `02_researcher`, `03_provocateur`, and `04_voice` (Step 1 responses *with thinking traces*, Step 2 artifacts, `step2_validation/`, `operator_decisions/`), plus `05_editor`.
  - `published_artifacts/`, including `EDITORIAL_ASSESSMENT.md` and `DATA_INVENTORY.md`.
  - `council_config.json`, `conference_facts.json`, `audience_profile.json`, `panel_roster.json`.
- **Orientation:**
  - `STATE.md`
  - the roadmap `_workspace/planning/PLAN_2026_06_12_post_athens_roadmap.md`, in particular the net-complexity gate and its 2026-09-28 amendment
  - `_workspace/planning/PRODUCT_assembly_hub.md`
  - both trackers (`_workspace/planning/{runtime,voices}/OPEN_ITEMS.md`)
  - the project goals: `docs/AI_Assembly_Briefing_v3_1.md`, `docs/design/*.md`
- **Search the trackers before claiming anything is new.**
- **Label claims** CONFIRMED (seen in data or code) or PLAUSIBLE. Label inferences as inferences. Decisions are the operator's: give options with trade-offs and recommend one. Quote real examples with ids and file paths.
- **Write plainly:** outcome first, examples over adjectives, no praise. When done, tell the operator the deliverable's path and a three-line summary.

---

## Task 1: design draft for the split card and event config (roadmap §2.1, Stage 5)

**Goal:** one design for the roadmap's keystone.
- **FU#42 split card** (`_workspace/planning/FOLLOW_UPS.md`): a voice card that stays byte-identical across deployments, plus a deployment card for stance variants, lengths, audience-aware fields, and later `generation_parameters`.
- **C52 event config** (runtime OPEN_ITEMS): `event_config.json` replacing the Athens hardcoding.

**Read:**
- roadmap §2.1, including its list of hardcodings and the prompt sweep across both pipelines;
- `docs/AI_Assembly_Persona_Card_v2.md` and `personas/CROSS_REPO_CONTRACT.md`;
- `_workspace/planning/runtime/DESIGN_voice_deployment_context.md`, the retired C48 design with the same descriptive/prescriptive split;
- the card-loading code: `runtime/flows/voice/card_assembly.py`, `runtime/flows/editor/card_assembly.py`, `personas/flows/shared/chat_prompt_builder.py`.

**Deliver:**
1. **A field-by-field partition of the card:** every field goes to the voice card or the deployment card, with a reason. Check the actual Athens cards for fields whose content is event-specific.
2. **A complete inventory of event hardcoding,** with `file:line` for code and prompts in both pipelines. Include `choices=[1,2,3]`, `DATE_TO_NIGHT` / `NIGHT_TO_DAY`, `DAY_TO_RUN`, `NIGHT_TO_RUN_DIR`, run-dir naming, `deployment="athens"`, Athens and audience wording in prompts, and continuity's night count.
3. **The `event_config.json` schema,** and how each hardcoding reads from it.
4. **A migration plan** that keeps Athens reproducible.
5. **The net-complexity check:** show that this *removes* special-casing rather than adding a layer on top. If some part doesn't, say so.
6. **Open operator decisions.**

**Deliverable:** `_workspace/planning/DESIGN_2026_09_28_split_card_event_config.md`.

## Task 2: evidence on the Step-2 validator (feeds the C42 / C60 decision, roadmap §1.3)

**Goal:** turn the "~100% released" impression into a flag-by-flag evidence base.
- At Athens, 23 of 30 voice-nights were flagged: 7, 8 and 8.
- The data is in `runs/athens_night_*/04_voice/step2_validation/*.json` (pillars, verdicts, reasons) and `.../operator_decisions/*.json`.
- The prompts are `runtime/flows/shared/prompts/voice_step2_validation_{safeguards,engagement,voice_fidelity,cross_night_echo}.md`; the code is `runtime/flows/voice/step2_validation.py`.
- Trackers: C42 (the drafted BREACH-vs-PASS fix), C43, C60 (the prune-vs-agentic-triage fork), and roadmap §1.3's validator economy.

**Deliver:**
1. **Every flag classified** as a real problem, a false alarm (with its cause: rule misfire, card conflict, prompt wording, parse fallback), or ambiguous. Give the evidence: the artifact excerpt and the rule it hit.
2. **Per pillar and per rule:** precision, and whether anything real would have been missed without it.
3. **A concrete prune or fix proposal:** which checks to keep, change or drop, and whether the C42 draft fixes the misfires.
4. **The C60 question:** does the evidence support prune-and-fix, agentic triage, or both, for which deployments?
5. **A short note on the persona-side validators** (7a / 7a FINAL fold, dead QC per roadmap §1.3), only where the Athens build data shows something.

**Deliverable:** `_workspace/planning/runtime/REVIEW_2026_09_28_validator_evidence.md`.

## Task 3: which card fields actually shape the output

**Goal:** each persona card is 38–44K tokens. Find out, from the Athens output, which fields visibly shaped what each voice wrote and which were dead weight.

**Evidence to use:**
- the cards;
- `runtime/flows/voice/card_assembly.py`, for which fields load at which step;
- the Step 1 `thinking_trace`s and detailed responses, and the Step 2 artifacts, across all three nights and ten voices.

**Method:** trace field-specific content into the outputs:
- a card's `characteristic_moves`, `banned_language`, `preferred_vocabulary`, `metaphorical_repertoire` and corpus passages showing up, or explicitly avoided;
- fields named in the thinking traces;
- fields never reflected anywhere.

Watch the confound: a field can matter without leaving a visible trace. Say what the method can't show.

**Deliver:**
1. **A per-field utility table:** strong, weak, or none visible, with example evidence.
2. **Per-voice highlights.**
3. **Implications:** for the split card (Task 1 of this batch), for loading card sections only when needed (runtime C59, "Voice" row), for cost, and for the Stage 4 prompt work.

**Deliverable:** `_workspace/planning/voices/REVIEW_2026_09_28_card_field_utility.md`.

## Task 4: decision memo on the validation track ("genuine perspective vs elaborate ventriloquism?", voices §33)

**Goal:** prepare the operator's open decision from June with evidence, not opinion. Read voices OPEN_ITEMS §33 in full, plus §24 / §28 (the reader gates) and FU#55 / FU#30.

**Gather evidence from the Athens output on both sides:**
- **For a real perspective:** moves a voice made that the brief and corpus support but don't contain; convergences between voices from unrelated traditions (see `EDITORIAL_ASSESSMENT.md`); refusals in character.
- **For competent pastiche:** interchangeable phrasing across voices, generic moves wearing a voice's vocabulary, the same structural template under different registers.

Consider the cheapest honest tests: a blind A/B against a generalist given the same brief, and the reader gates reframed as a validation instrument. Say what each would cost and what each could and couldn't show.

**Deliver:**
1. **The evidence, both ways,** with excerpts and ids.
2. **What it suggests** (as inference).
3. **Two or three concrete validation-track designs** with cost and placement: a gate before Phase 2, or a parallel track.
4. **A recommendation.**

**Deliverable:** `_workspace/planning/voices/MEMO_2026_09_28_validation_track.md`.

## Task 5: source dossier for the operator's writing about the project

**Goal:** the operator plans to write about the AI Assembly. Gather everything they'd need to write from, organized and sourced. You gather; the operator writes. Don't draft the essay.

**Sections:**
1. **What it is and why:** the provotype idea, in the project's own words. Quote the Briefing and Design Principles.
2. **What happened at Athens:** the three nights, the numbers (dossiers, voice pages, sessions, extractions, cost and time from the specs' measured figures), and the timeline.
3. **The strongest material:** the best lines and moments from the voice artifacts and dossiers, with ids, and why each works. Build on `EDITORIAL_ASSESSMENT.md`.
4. **How it was built:** the pipeline in plain language, the key design decisions and why, and what was hard (from STATE, CHANGELOG, the trackers).
5. **Lessons and surprises:** what worked, what didn't, what changed afterwards (e.g. the post-Athens fixes, today's reviews).
6. **Open questions and ethics:** §33's validity question, the reader gates for Marley and Whanganui, the appropriation critiques in the trackers.
7. **Where it goes next:** the governed-hub direction.

Every fact carries its source path.

**Privacy:**
- Programme speakers named in the published record may be named as the record names them.
- **Never name private individuals.** Audience reflection participants are anonymous.
- Don't add personal details beyond what the published record contains.

**Deliverable:** `_workspace/planning/WRITING_SOURCES_2026_09_28.md`.
