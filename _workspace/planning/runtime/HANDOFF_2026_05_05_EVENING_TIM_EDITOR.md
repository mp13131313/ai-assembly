# Handoff — Tim editor closing-prompt + deployment context

**Date:** 2026-05-05 evening (~95% context, before compact)
**Active branch:** `feature/editor-deployment-context` (code repo)
**athens-2026:** main, last commit `f6afe2c` (Whanganui v2 patches; Tim card edit `27f3e47` is two commits back, pushed)

---

## Session goal

Build Tim Leberecht's runtime closing prompt to mirror voice Step 1 + Step 2 merged structure, drop newspaper/edition framing, ground in Tim's bridging job + DR-dossier register. Plus the deployment context blocks (THE GATHERING / YOUR ROLE / THE PANEL) that voice cards got on a sibling branch.

---

## What landed (committed + pushed)

**Code repo, on branch `feature/editor-deployment-context`:**
- Commit `999450b` "runtime(editor): inject deployment context (gathering/role/panel) + {night} substitution + field-by-field briefings in closing prompt"
  - `runtime/flows/editor/card_assembly.py` — `_render_deployment_context` + `_try_load_deployment_sources` + `{night}` substitution
  - `runtime/flows/shared/io.py` — `load_conference_facts()` added
  - `runtime/flows/shared/prompts/editor_dossier.md` — first rewrite (field-by-field input + emitted_fields block; this got further iterated post-commit)
  - `runtime/tests/test_editor_deployment_context.py` — 16 tests
- Commit `e8cd902` (later, possibly operator-side) — planning + README updates

**athens-2026, on main:**
- Commit `27f3e47` — Tim's `voice_temporal_stance.default` opener rewrite: AT WBBF on Night `{night}`, edition framing dropped

---

## What's UNCOMMITTED on the branch (live edits this session, post-`999450b`)

```
M runtime/flows/editor/card_assembly.py        ← H1 fix (## → #) on deployment blocks
M runtime/flows/editor/dossier_generation.py   ← parser extracts 7 audit fields, stamp_runtime_fields includes them
M runtime/flows/shared/prompts/editor_dossier.md ← MAJOR rewrite (see below)
M runtime/tests/test_editor_deployment_context.py ← assertions updated for # H1
```

Tests: **33/33 pass** as of last run.

---

## What changed in `editor_dossier.md` since the commit

Read it verbatim at `runtime/flows/shared/prompts/editor_dossier.md`. Major reworks:

1. **Structure rebuilt to mirror voice Step 1 + Step 2 merged** — 14 blocks now: `<input>` → `<task>` → `<your_core>` → `<engaging_the_material>` → `<weighing>` → `<focus>` → `<stance>` → `<form>` → `<boundaries>` → `<composition>` (Apply / Quote / Ground / Pass) → `<theme_page>` → `<headnotes>` → `<emitted_fields>` → `<output>`.

2. **Newspaper/edition framing dropped.** No more "broadsheet," "issue," "Vol. CXVI," "front teaser," etc. Replaced with HoBB editorial framing: "publication under House of Beautiful Business, you are the unnamed editor, your work is the bridging itself."

3. **Three-pole bridge task** (per operator):
   - What the conference surfaced (Researcher + Provocateur)
   - What the assembly and the voices did with it (artifacts)
   - The reader (may/may not have been at sessions, may/may not know the voices; Tim's job is to get them up to speed AND pull them in)

4. **`paper-voice` → `your editorial register`** throughout (10 instances replaced).

5. **Quote rule added** in `<composition>`: 1-3 short quotes per article, max 2 per voice, sourced from voice artifacts (cite by voice name) or panel speakers (cite by role/title). Foretaste, not substitute.

6. **Audit-field drop — PARTIAL** (in progress, not finished):
   - "Record `weight_assessment`" → replaced with "Land on what carries weight... not emit it as a separate field" ✓
   - "Record `focus_decision`" → replaced with "Commit to a focus internally" ✓
   - **Still need to**: remove "Record" lines from `<stance>` and `<form>` blocks; remove the 7 audit field labels from `<output>` schema; revert parser to NOT extract those fields; revert stamp_runtime_fields to NOT include them; update tests.
   - Operator's call: "we don't need it recorded for him" — they confirmed the drop. Just unfinished.

---

## Pending decisions (operator deferred / proposed but not applied)

### 1. Length envelope tightening — APPROVED IN PRINCIPLE, NOT APPLIED

Operator: "I'd lean tight. Nobody has time in the morning." Confirmed they're not tight enough. I proposed 10 tightenings:

| Field | Current | Proposed |
|---|---|---|
| `kicker` | 3-7 words | 3-5 |
| `headline` | 8-15 | 8-12 |
| `subline` | 25-60 | 25-40 |
| `front_abstract` | 30-50 | 25-40 |
| `theme_title_for_dossier` | 5-10 | 4-8 |
| `theme_abstract_for_dossier` | 60-100 | 50-80 |
| `body_paragraphs` single-voice | 350-500 | 300-450 |
| `body_paragraphs` multi-voice | 500-700 | 450-600 |
| `headnotes[i].artifact_title` | 4-12 | 4-8 |
| `headnotes[i].framing_text` | "1-2 sentences" | "25-50 words" |

Need to apply to BOTH `<emitted_fields>` block AND `<output>` length-envelope table. Operator pivoted before approving the specific numbers.

### 2. "B9-torqued" replacement — NOT APPLIED

`editor_dossier.md` still has "B9-torqued per your `translation_protocol`" (in `<headnotes>` block + `<emitted_fields>`). I committed to replacing with "translated through your `translation_protocol` so the voice's register inflects the title without flattening it" but didn't get to it.

### 3. DR dossier additions to closing prompt — PROPOSED, NOT APPLIED

I checked Tim's `01_research/04_dr_dossier/_appendix_beauty_shot/` (7 files, ~600 lines) and found three things sharper than what's currently in his card/prompt:

- **Six-beat Beauty Shot arc** (Section 6, Post A): anecdote → cultural diagnosis → named-thinker pivot → coined concept → reframe → aphoristic close. Could be referenced in `<form>`.
- **"Inspirational uplift unearned by darkness"** — THE diagnostic anti-pattern. "Walk through the dark first; only then permit the third-term reframe." Could land in `<boundaries>` or `<composition>` Pass.
- **Host-mode framing** (Section 6, Post B) — Tim's Assembly editorial article IS Beauty Shot's host-mode form. "Compact intro that situates the guest in community and moment; then *step back* and let the guest speak." Maps almost exactly onto Tim's article+headnotes shape. Could sharpen `<task>` or `<form>`.

Operator was reading my summary when context window pressure forced this handoff.

---

## Side context the next Claude should know

- **Voice-side parallel branch**: `feature/voice-deployment-context` (code repo, pushed). Same architecture pattern landed for voices' system prompts (THE GATHERING / THE PANEL / YOUR FELLOW VOICES at Step 2 / YOUR READERS). Was kept separate from main; main pulled most of its sibling commits but NOT the deployment-context impl + C39 OPEN_ITEMS filing. See `voices/MEMO_2026_05_05_voice_temporal_stance_assembly_fiction.md` (✅ SHIPPED to athens-2026 commit `64e9b08`).
- **Voice card temporal-stance shift** ✅ shipped to all 10 voices in athens-2026. They speak from "the assembly that gathers in Athens / present in their time / responding to what's put before them, observing the panels." Tim's edit (commit `27f3e47`) is the editor-side analog.
- **Length-cap surgery** ✅ shipped on Dostoevsky / Hannah Arendt / Octopus cards (athens-2026 commit `9dae9b9`).
- **CLAUDE.md is current as of 2026-05-05 evening** — read for full context.

---

## To pick up where I left off

In order, smallest to largest:

1. **Finish the audit-field drop** in `editor_dossier.md`:
   - Replace `<stance>` block's "Record `stance` and a one-sentence `stance_rationale`." with similar internal-commit language
   - Same for `<form>` block
   - Remove the 7 audit field labels from the `<output>` schema (lines 196-208 of current file)
   - Revert `dossier_generation.py::_FIELD_LABEL_RE` to NOT include the 7 audit fields
   - Revert `parse_dossier_output`'s default `out` dict to NOT include them
   - Revert `stamp_runtime_fields` return dict to NOT include them
   - Run tests; expect some test breakage on `test_editor_dossier_generation.py` if any tested those fields
   - Re-run full editor test suite to confirm green

2. **Apply length envelope tightenings** — 10 changes across `<emitted_fields>` + `<output>` table

3. **Replace "B9-torqued"** — 2 occurrences in `editor_dossier.md` (`<headnotes>` block + `<emitted_fields>` block). Replacement text proposed: "translated through your `translation_protocol` so the voice's register inflects the title without flattening it"

4. **Decide on DR-dossier additions** — operator asked "any info in there?" — I summarized three findings. Operator hadn't decided whether to apply any. Default would be: NO additions (the persona card already encodes the same content via `characteristic_output_structure` / `quality_criteria` / `characteristic_moves` fields rendered in the system prompt). The dossier is the ground; the card is the rendered version. Three findings would be a sharpening, not new content.

5. **Commit + push the rebuilt prompt**. Single commit message capturing: rewrite to Step 1+2 merged structure, three-pole bridge task, paper-voice→editorial register, quote rule, audit-field drop, tightened length envelopes, B9-torqued replacement.

6. **Re-run dryrun — held**: operator agreed to hold the voice-pipeline re-run until Tim was deep-and-step-by-step done. Once Tim's prompt is committed, ready to fire.

---

## Tests state at handoff time

`runtime/tests/test_editor_deployment_context.py` (16) + `test_editor_dossier_generation.py` (17) = 33 pass.

Full runtime suite NOT re-run after the audit-field-drop partial work — recommend re-run after all the cleanups land.

Athens-2026: Tim's card committed + pushed (`27f3e47`); other 6 unpushed commits on main are operator's voices-thread work (Whanganui v2 patches, etc.).

---

## Resume prompt for next Claude

> "Read `_workspace/planning/runtime/HANDOFF_2026_05_05_EVENING_TIM_EDITOR.md`. Branch is `feature/editor-deployment-context`. Pick up at item 1 (finish audit-field drop in `editor_dossier.md`); the operator confirmed they want the seven audit fields gone (weight_assessment / focus_decision / focus_rationale / stance / stance_rationale / selected_form / form_rationale). Then items 2 (length tightenings) and 3 (B9-torqued replacement) without further confirmation — operator approved both directions. Item 4 (DR-dossier additions) needs operator confirmation. Run tests after each step. Single commit + push when all four items done."

---

## File pointers

| What | Where |
|---|---|
| Current closing prompt | `runtime/flows/shared/prompts/editor_dossier.md` |
| Tim's persona card | `projects/athens-2026/editor/tim_leberecht/07_persona_card_assembled.json` |
| Tim's DR dossier (ground for the card) | `projects/current-tests/editors/tim_leberecht/01_research/04_dr_dossier/_appendix_beauty_shot/` |
| Card assembly logic | `runtime/flows/editor/card_assembly.py` |
| Parser logic | `runtime/flows/editor/dossier_generation.py` |
| Tests | `runtime/tests/test_editor_deployment_context.py` |
| Voice-side parallel work | `runtime/feature/voice-deployment-context` branch + `voices/MEMO_2026_05_05_voice_temporal_stance_assembly_fiction.md` |
| Tim's full system prompt rendered (snapshot) | `projects/current-tests/_tim_prompt_dump_2026_05_05/tim_SYSTEM_prompt_night1.txt` (133KB) |
| Tim's full user prompt rendered (snapshot, theme_001 + scheherazade) | `projects/current-tests/_tim_prompt_dump_2026_05_05/tim_USER_prompt_night1_theme_001_scheherazade.txt` (31KB) |
