# HANDOFF — Voice Pipeline first dry-run (Plato solo, 3 formulations)

**Date:** 2026-04-29
**Scope:** First end-to-end dry-run of the Voice Pipeline against a real persona card. Plato only, 3 hand-authored formulations all on the theme "The Legitimacy of the Invisible". Validates Step 1 + Step 2 + publish step end-to-end on real Opus output. Does NOT exercise Step 3 (no other voices to amend) or Continuity (single-night).

**Sandbox PROJECT_ROOT:** `/Users/aienvironment/Desktop/AI Assembly/projects/voice-pipeline-dryrun/`
**Run ID:** `dryrun_2026_04_29_plato_solo`

---

## What's been staged for you

```
projects/voice-pipeline-dryrun/                 NEW sandbox PROJECT_ROOT
├── voices/
│   └── plato/
│       ├── 07_persona_card_assembled.json     COPIED from athens-2026 (the finalized
│       │                                      Plato card — FU#49A v2 + FU#53 + 12 patches)
│       └── 06_derive/
│           └── 03_chat_system_prompt.json     COPIED (chat artifact, FU#57-stripped)
└── runs/
    └── dryrun_2026_04_29_plato_solo/
        └── 03_provocateur/
            └── briefings/
                └── plato.json                 NEW — 3 hand-authored formulations matching the
                                               post-FU#57 Provocateur briefing schema
                                               (formulation_text + context_narrative +
                                                selected_quotes + mode label in markdown
                                                + full_theme_record with clusters / extractions /
                                                theme_flags)
```

The 3 formulations all sit under the umbrella display title "The Legitimacy of the Invisible" with 3 distinct sub-aspects:

| theme_id | sub-aspect | mode |
|---|---|---|
| `theme_001` | Algorithmic Governance Without Consent (morning panel) | question |
| `theme_002` | Being Seen by Another Person (afternoon workshop) | question |
| `theme_003` | Civilizational Withdrawal from Public Life (closing session) | question |

All 3 carry full `full_theme_record` with cluster + 5 extractions each (per session: `morning_panel:001-005`, `afternoon_workshop:001-005`, `closing_session:001-005`), `theme_flags` (high friction, fault-line present, theme_quality scores), `co_assigned_voices: []` (Plato solo), and the markdown `narrative_briefing` rendered with the FU#57 mode-labelled FORMULATION header.

---

## How to run the dry-run

### Pre-flight checks

```bash
cd "/Users/aienvironment/Desktop/AI Assembly/code/runtime"

# Verify modules import cleanly + Plato card loads + system prompts assemble
AI_ASSEMBLY_PROJECT_ROOT="/Users/aienvironment/Desktop/AI Assembly/projects/voice-pipeline-dryrun" \
venv/bin/python -c "
import sys; sys.path.insert(0, '.')
from flows.voice.card_assembly import assemble_system_prompt, load_persona_card
card = load_persona_card('plato', night=1)
print(f'Plato card loaded: {len(card)} fields')
for step in (1, 2, 3):
    sp = assemble_system_prompt(card, step=step, night=1)
    print(f'  Step {step} system prompt: {len(sp):,} chars')
"

# Confirm openai + google-genai are installed in runtime venv (needed for validation)
venv/bin/python -c "from openai import OpenAI; from google import genai; print('OK')"
```

If imports fail, run: `venv/bin/python -m pip install openai==2.31.0 google-genai==1.73.1`

### The dry-run command

**Recommended first run** (Step 1 + validation + Step 2 + publish; skip Step 3 since solo voice; skip continuity since Night 1 standalone):

```bash
cd "/Users/aienvironment/Desktop/AI Assembly/code/runtime"

AI_ASSEMBLY_PROJECT_ROOT="/Users/aienvironment/Desktop/AI Assembly/projects/voice-pipeline-dryrun" \
venv/bin/python flows/voice_flow.py \
  "/Users/aienvironment/Desktop/AI Assembly/projects/voice-pipeline-dryrun/runs/dryrun_2026_04_29_plato_solo" \
  --night 1 \
  --voices plato \
  --skip-step3 \
  --skip-continuity \
  --project "/Users/aienvironment/Desktop/AI Assembly/projects/voice-pipeline-dryrun"
```

**Cost estimate for this single-voice run** (Opus 4.7 + thinking + OpenAI validation):
- Step 1: 3 calls × ~$2.50 = ~$7.50
- Validation A (anachronism) + B (constitution): 6 OpenAI calls × ~$0.50 = ~$3
- Step 2: 1 call × ~$5 = ~$5
- Publish step: deterministic, $0
- **Total: ~$15-20**

**Wall time estimate:** ~10-15 min (Step 1 in batches of 4 with the 20s wait, but only 3 calls so one batch; Step 2 single call; validation parallel with Step 2)

### Cheaper alternatives if you want to validate mechanics first

**Skip validation** (saves ~$3, doesn't exercise OpenAI ladder):

Add `--skip-validation`. Means anachronism + constitutional checks won't run; you won't know if Plato hallucinates modern terms. Only do this for a first sanity-check run.

**Single formulation only** (saves ~$10, only validates one Step 1 call + Step 2):

Edit `runs/dryrun_2026_04_29_plato_solo/03_provocateur/briefings/plato.json` to remove 2 of the 3 formulations from the `formulations` array, then run.

---

## What outputs to expect

After a successful run, the sandbox will contain:

```
projects/voice-pipeline-dryrun/
├── voices/plato/...                          (unchanged — read-only for the dry-run)
├── runs/dryrun_2026_04_29_plato_solo/
│   └── 04_voice/
│       ├── step1_detailed_responses/
│       │   ├── plato__theme_001.json         Plato's reasoning on algorithmic governance
│       │   ├── plato__theme_002.json         …on being-seen
│       │   └── plato__theme_003.json         …on civilizational withdrawal
│       ├── validation/
│       │   ├── plato__theme_001.json         Anachronism + constitutional check results
│       │   ├── plato__theme_002.json
│       │   └── plato__theme_003.json
│       ├── step2_first_draft_artifacts/
│       │   └── plato.json                    Plato's artifact (focus + stance + form decisions
│       │                                      + the actual artifact text — likely a dialogue)
│       ├── responded_to_graph_night_1.json   Empty edges (no Step 3 amendments since solo)
│       ├── themes_to_voices_night_1.json     Plato across the 3 themes
│       ├── briefings_consumed/plato.json     (echo of input briefing for traceability)
│       └── manifest.json                     Run-level summary + cost + wall time
└── published_artifacts/
    └── nights/night_1/
        ├── plato.json                        Publish-ready artifact (themes by ref)
        └── _index.json                       Per-night index (1 voice)
```

---

## What to look at in the outputs

### 1. Did Plato actually engage these formulations as Plato? (Layer 2 test)

Read `runs/dryrun_2026_04_29_plato_solo/04_voice/step1_detailed_responses/plato__theme_001.json` →
`detailed_response` field. Check:

- **Tense discipline:** does Plato write *"I reason by ti esti"* (present tense — voice's tools) and *"I founded the Academy long ago"* (past — voice's life)? Or does it slip into eternal-present scholar-tense (*"Plato writes dialogues to dramatize…"*) or frozen-in-past (*"in 348 BCE I am writing…"*)? The cryofreeze framing should hold.
- **No year-distance computation:** does Plato avoid *"twenty-three centuries"* / *"fifty-one years ago"*? Loose temporal language (*"long ago"*, *"in my time"*) is correct.
- **Voice grammar, not pipeline grammar:** does Plato refer to the formulation as something put before him, or does he use words like "formulation" / "Provocateur" / "the Assembly"? (The latter would be a leak.)
- **Translation, not disclaim:** does Plato translate "algorithm" / "credit scoring" / "predictive policing" into his own framework (philosopher-king, the Cave, techne vs episteme), or does he say "I do not know what an algorithm is"? Translation is correct.
- **Constitution check:** does the position align with `constitution` (rule by knowledge of the good, dialectical method, etc.)?
- **Citing extractions:** does the response cite by ID (*"morning_panel:003"*) or attribute by speaker name (*"the legal scholar said…"*)? The closing instruction asks for citation by ID — see if it lands.
- **Valid landings:** does the response land on a defensible position, a sharper question, a marked aporia, or a redirection — and not hedge into "balanced consideration of both sides"?

### 2. Did Step 2 produce the right shape?

Read `runs/dryrun_2026_04_29_plato_solo/04_voice/step2_first_draft_artifacts/plato.json` →

- Does it parse cleanly? All 9 structured fields populated (`focus_decision`, `focus_rationale`, `stance`, `stance_rationale`, `selected_form`, `form_rationale`, `themes_covered`, `artifact_title`, `artifact_subtitle`, `artifact_text`)?
- Is `selected_form` a member of Plato's family-of-forms? (per the card: dialogue / monologue speech / framed monologue / dialogue+myth / dialogue+image)
- Is `themes_covered` populated as an actual list of theme_ids? (FU#3+#9 fix — the voice should emit it explicitly; if it's empty or wrong, the parser fallback fired)
- `artifact_text`: does it read as Plato's dialogue (or chosen form), not generic essay? Is it within the form-family per the anti-generic-register banned_modes entry?

### 3. Did validation flag anything?

Read `04_voice/validation/plato__theme_*.json` →

- Anachronism check: `status: PASS` ideally. If `status: ISSUES`, see the OpenAI verdict for what was flagged.
- Constitutional check: same.

### 4. Did publish layer produce the right shape?

Read `published_artifacts/nights/night_1/plato.json` →

- Is the artifact text + title + subtitle present and clean?
- `themes_addressed` is a list of theme_ids (refs, not inlined data)?
- `deliberation.decision: "stand-pat"` (since we skipped Step 3)?
- No lineage / telemetry / thinking_trace leaked?
- `voice_name`, `voice_slug`, `night`, `url_path: /night-1/plato`, `generated_at` populated?

### 5. Manifest sanity

Read `04_voice/manifest.json` →

- `counts.step1_pairs_succeeded: 3`
- `counts.step2_voices_succeeded: 1`
- `counts.step3_voices_succeeded: 0` (skipped per `--skip-step3`)
- `counts.continuity_voices_succeeded: 0` (skipped)
- `counts.validation_flagged: ?` — if non-zero, look at the validation outputs
- `wall_clock_s` matches your wall observation

---

## Likely failure modes and how to triage them

The Voice Pipeline has been smoke-tested at the import + system-prompt-assembly + parser levels. It has NEVER run a real Anthropic API call. The first dry-run is where unknowns surface. Most likely failures:

### A. Anthropic API errors
- **Rate-limit / 529:** The retry wrapper should handle one transient failure (5s backoff). If both attempts fail, the orchestrator catches the exception and the pair is skipped.
- **Auth error:** check `ANTHROPIC_API_KEY` in `code/.env` (loaded by `voice_flow.py` via `load_dotenv`).

### B. Step 2 / Step 3 parser fragility (self-review item #4 — deliberately deferred)
- **Symptoms:** `step2_first_draft_artifacts/plato.json` has empty fields like `focus_decision: ""` or `themes_covered: []`, with the actual content all dumped into `artifact_text`. Means the regex parser didn't match the model's output format.
- **Triage:** read the model's raw output (it's in `artifact_text` if the parser failed). Compare to what the parser regex expects. Two fixes possible:
  1. Tighten the closing instruction to require a more rigid output format (e.g. JSON-only response wrapped in code fences) — change the prompt
  2. Loosen the parser regex to match whatever Opus actually emits — change `_parse_step2_output()` in `runtime/flows/voice/step2_first_draft_artifact.py`
- The closing instruction already specifies the `**Label:** value` format with each field on its own line. If Opus deviates, that's signal — capture an example and tighten.

### C. OpenAI validation never runs
- **Symptoms:** `04_voice/validation/` doesn't exist or is empty.
- **Triage:** check `openai` and `google-genai` are installed in the runtime venv (pre-flight check above). Check `OPENAI_API_KEY` in `code/.env`.

### D. Card content unexpected
- **Symptoms:** Plato's response cites concepts that aren't in `concept_lexicon` or behaves out-of-character.
- **Triage:** the card itself is the contract. If Plato is misbehaving, the card needs a patch (operator side, not Voice Pipeline side). Look at the `metadata.fix_pass_log` to see what was already patched; the residual Jowett-translation conflict your handoff §"Open" item flagged might surface here.

### E. Empty thinking_trace
- **Symptoms:** `step1_detailed_responses/plato__theme_*.json` has `thinking_trace: ""` despite `thinking_enabled: true`.
- **Triage:** `final.content` may not contain ThinkingBlock objects in the SDK version. Verify via `print([type(b) for b in final.content])` patched into `_anthropic_call.stream_voice_call` temporarily. Adaptive thinking should still produce thinking blocks; if not, the model may have decided no thinking was needed (rare for a complex prompt but possible).

---

## Three runs in sequence, if you want to iterate

The user's request mentioned "do 3 runs". Here's how to layer them:

**Run 1 (mechanics validation):** the command above as-is. Verifies the pipeline executes end-to-end.

**Run 2 (re-run after parser/prompt fixes if Run 1 surfaced issues):**
```bash
# Delete previous step output to force regeneration (checkpoints-as-cache otherwise skips)
rm -rf "/Users/aienvironment/Desktop/AI Assembly/projects/voice-pipeline-dryrun/runs/dryrun_2026_04_29_plato_solo/04_voice"

# Re-run same command — picks up any code changes you made to fix Run 1 issues
```

**Run 3 (re-run with continuity flow + Step 3 disabled is meaningless solo, but you can validate continuity by faking a "Night 2" run):**

To exercise the continuity-block path, you'd need to:
1. Run Night 1 first (above command) so Step 1 + Step 2 outputs exist
2. Drop `--skip-continuity` so continuity flow runs after Step 3 (it won't because Step 3 is skipped — this is a chicken-and-egg)
3. OR temporarily drop `--skip-step3` and let Step 3 run with empty `voices_read` (will produce stand-pat decisions)

Realistically, **continuity testing wants a 2-voice setup** (Plato + Cleopatra once Cleopatra finalizes) so Step 3 has someone to amend. For Run 3 with Plato solo, the more useful test is **re-run to verify checkpoints-as-cache** (delete a single Step 1 output file, re-run, see only that one re-computes).

---

## When to commit / push the dry-run output

The sandbox is at `projects/voice-pipeline-dryrun/` — **outside the code repo** per Tier 3. Per CLAUDE.md, `projects/` is "NEVER pushed to GitHub." So:

- The dry-run output stays local to your machine
- Don't `git add` from inside the sandbox
- If you want to share findings, copy interesting snippets into a HANDOFF doc in `code/_workspace/planning/`

If the dry-run reveals issues that need code fixes (parser tightening, prompt edits, etc.), those go on a branch off main with a normal PR flow.

---

## Outstanding items separate from the dry-run

These are NOT blocking the dry-run but worth noting:

1. **Step 3 spec'd + built but never exercised.** Solo voice can't amend. Validates only after Cleopatra ships and we can run Plato + Cleopatra together.
2. **Continuity flow built but never exercised.** Same — needs a Night 1 → Night 2 sequence with real Step 3 output.
3. **publish_flow.py never exercised.** Builds per-theme + per-extraction + lineage graph from upstream pipelines. For this dry-run we're using a hand-authored briefing (no upstream pipelines), so publish_flow has nothing to read on the Researcher / Provocateur side. If you want to test publish_flow:
   - Run the Researcher + Provocateur on `dev_msc_test` transcripts to produce real upstream outputs
   - OR hand-author `02_researcher/all_extractions.json` + `02_researcher/grouping.json` + `03_provocateur/formulations/*.json` matching the briefing
   - Then run `publish_flow.py` after voice_flow

4. **First real Cost & wall-time numbers** from this dry-run will validate (or invalidate) the ~$210-280/night + ~30-50 min/night spec estimates. Multiply this dry-run's per-voice numbers by 10 for the full panel.

---

## File / directory reference

- Sandbox PROJECT_ROOT: `/Users/aienvironment/Desktop/AI Assembly/projects/voice-pipeline-dryrun/`
- Briefing fixture: `…/runs/dryrun_2026_04_29_plato_solo/03_provocateur/briefings/plato.json`
- Plato card source: `/Users/aienvironment/Desktop/AI Assembly/projects/athens-2026/voices/plato/07_persona_card_assembled.json`
- Voice Pipeline spec: `code/docs/AI_Assembly_Voice_Pipeline.md`
- Voice Pipeline code: `code/runtime/flows/voice/` + `code/runtime/flows/voice_flow.py`
- Publish layer: `code/runtime/flows/voice/publish.py` + `code/runtime/flows/publish_flow.py`
- runtime venv (where openai + google-genai are installed): `code/runtime/venv/`

Good luck with the dry-run.
