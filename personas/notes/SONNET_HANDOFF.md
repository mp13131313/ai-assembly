# Sonnet Handoff — walkthrough-fixes-2026-04-17

## Last completed item

**Phase C.1** (Fix #9 — Pass 0b rewrite as Pass 1a prompt instantiator)
Commit: `a9a0ffb` — "refactor: rewrite Pass 0b as spec's Pass 1a prompt instantiator"

All phases up to and including C.1 are complete and committed. Branch pushed to origin.

## Commits on this branch (in order)

1. `4c5c366` — Phase A.1: rebrand Stage 0a/0b → Pass 0a/0b, strict voice_mode validation
2. `35bc8fd` — Phase A.2: Opus 4.6 → Opus 4.7
3. `7801292` — Phase B.1: remove impossible filter
4. `f5614d6` — Phase B.2: strip editorial-assets from voice_config schema
5. `03dc56b` — Phase B.4: align corpus_constraint enum (three values)
6. `2296595` — Phase B.5: trim non_human_subtypes to {organism, system}
7. `a9a0ffb` — Phase C.1: rewrite Pass 0b as Pass 1a prompt instantiator

**Note:** B.3 and B.6 had no new file changes — their substantive work was already captured in A.1 (primary_text_sources strip in run_pass0a) and B.2 (prompt prohibition). D.2 (require --hint always) was also done in A.1 as part of the run_pass0a rewrite.

## Next item to start: Phase D.1

**Fix #3 — Retry-once on JSON/API errors in Pass 0a and Pass 0b**

Wrap the `call_claude(...)` calls in `run_pass0a_voice_config.py` and `run_pass0b_dr_prompt.py` in a retry-once-on-failure block. Catch `json.JSONDecodeError`, `anthropic.APIError`, `anthropic.RateLimitError`. On retry: log the failure, wait 15s, retry once. On second failure: `sys.exit` with clear message.

Commit message: `fix: retry-once on JSON/API errors in Pass 0a and Pass 0b`

## Remaining items after D.1

- **D.3** — Fix #10: subtype=system overrides in Pass 3/5/7b prompts (biggest remaining task — 5 new blocks in 3 prompt files)
- **D.4** — Fix #13: Pass 1-merge model upgrade (in `run_persona_pipeline.py`, `_pass_1merge` function): `model="claude-sonnet-4-6"` → `"claude-opus-4-7"`, `max_tokens=4096` → `16000`
- **D.5** — Fix #14: Primary-text review gate after Pass 1c in `run_persona_pipeline.py`
- **E.1** — Syntax/import smoke tests
- **E.2** — Validate existing voice_configs against updated schema
- **E.3** — Rename spec doc to v3.8, add changelog
- **E.4** — Push (done already, just for any new commits)

## Ambiguities / notes

1. **B.6 (Pass 0a URL-emission audit) smoke test**: The plan asks to run `python3 run_pass0a_voice_config.py "Ibn Battuta" --hint "the Moroccan traveler"` as a smoke test. This requires a live ANTHROPIC_API_KEY. Skipped due to API cost — the defensive stripping code and prompt prohibition are both in place.

2. **D.2 (require --hint always)**: Already done in A.1 — `run_pass0a_voice_config.py` already has `--hint` as `required=True` in argparse. No separate commit needed. Also updated docs/CURRENT_STATE.md in the bulk Stage→Pass replacement.

3. **B.3 commit**: No separate commit was possible since the stripping logic was already in the A.1 rewrite. The B.2 commit captured the prompt prohibition. All substantive B.3 work is done.

4. **io.py VALID_CORPUS_CONSTRAINTS and VALID_SUBTYPES**: Updated in the A.1 commit along with the voice_mode validation. These are the authoritative enum sets imported by node0_validation.py.

5. **D.3 (subtype=system overrides)**: Read the WALKTHROUGH_FIXES_PENDING.md §10 carefully. Five new Jinja2 blocks needed. The prompts are in `personas/flows/shared/prompts/`. Read the current `persona_pass_3_intellectual_core.md`, `persona_pass_5_engagement.md`, and `persona_pass_7b_provocations.md` before starting.

## No Sonnet Questions

No ambiguities requiring user input were encountered. All plan steps had sufficient specification.
