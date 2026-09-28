**Verdict: merge after the listed fixes.** Fix finding 1 before merging; it is a one-line regression in how the legacy env overrides chain. There are no BLOCKER or MAJOR findings. Findings 2–10 can be filed as follow-ups.

# Review: `phase0-fixes` → `main` (2026-09-28)

**Reviewed:** `git diff main...phase0-fixes` at `07ff244` (includes `613faf0`), code only: `runtime/`, `personas/`, `model_routing.json`. The `code-review` skill was run at high effort, together with the brief's risk-ranked areas. `phase0-fixes` is checked out in the main checkout, so this worktree used `git switch --detach phase0-fixes`, which is the same commit. No code edits and no commits. The throwaway proof scripts ran only in the session scratchpad, against copies of athens-2026 data. athens-2026 itself was only read.

**Suites, same result before and after the review:** runtime 368 passed · ingest 114 passed (scratch root with copies of athens-2026 `reference/*.json`) · personas 242 passed.

**Counts:** BLOCKER 0 · MAJOR 0 · MINOR 5 · NIT 5.

## 1. Findings, most severe first

**1. MINOR · CONFIRMED: `TRANSCRIPTION_CLAUDE_MODEL` no longer reaches Speaker ID.** `runtime/flows/shared/model_routing.py:45`
- On `main`, `SPEAKER_ID_MODEL` fell back to the module's `CLAUDE_MODEL`, which was itself `TRANSCRIPTION_CLAUDE_MODEL` → `CLAUDE_MODEL` → Sonnet (main `transcription_flow.py:72-88`). The branch chain for `runtime.transcription.speaker_id` is `TRANSCRIPTION_SPEAKER_ID_MODEL` → `CLAUDE_MODEL`. The middle rung is gone.
- **Scenario:** `TRANSCRIPTION_CLAUDE_MODEL=claude-opus-4-7`, other vars unset. On `main`, Speaker ID and Cleaning both ran on Opus. On the branch, Speaker ID runs on Sonnet and Cleaning on Opus (ran it).
- This var is on the ingest subprocess allowlist (`runtime/ingest/pipeline.py:367`), so it is a supported VM knob. `docs/LLM_CALL_INVENTORY.md:233` was updated to match the new chain, not the old behavior.
- **Fix:** make the speaker_id tuple `("TRANSCRIPTION_SPEAKER_ID_MODEL", "TRANSCRIPTION_CLAUDE_MODEL", "CLAUDE_MODEL")` in both copies. Add a test next to `test_claude_model_applies_only_where_it_did`.

**2. MINOR · CONFIRMED: the C49 fallback is saved as a real Speaker ID result, so retries never re-attempt Speaker ID.** `runtime/flows/transcription_flow.py:744` (write) and `:722` (resume)
- The all-"Unidentified" mapping is written to `out_02_speaker_id.json`. The resume branch at `:722` loads that file whenever it exists and skips Speaker ID.
- **Scenario:** the JSON-decode failure was transient. The operator presses retry on the dashboard, or re-runs `process_session`. The log says "Resuming: loaded out_02_speaker_id.json (skipping Speaker ID)", and the session again ships with no named attribution.
- On `main`, the failure left no `out_02`, so a retry did re-run Speaker ID.
- **Fix:** on resume, treat an `out_02` whose `flags` contain `speaker_id_auto_passthrough` as absent and re-run Speaker ID. Alternatively, write the fallback under another name.

**3. MINOR · PLAUSIBLE: the degraded Speaker ID state is invisible where operators look at night.** `runtime/flows/transcription_flow.py:302`
- The flag lands only in `session_package.json` `review_queue.diarization_flags` and in `review.md`. `infer_state` marks the session `done` once the package exists, so the ingest dashboard and orchestrator show a normal success.
- **Scenario:** a large-roster session silently degrades to "Unidentified Speaker N". The Researcher, Provocateur and Voice stages run on it before anyone opens `review.md`.
- **Fix:** have the dashboard session row show a badge when `diarization_flags` contains `speaker_id_auto_passthrough`, or record it in `status.json` (e.g. `warnings: [...]`).

**4. MINOR · CONFIRMED (scratch repro): a held voice can no longer be dropped from the night index.** `runtime/flows/voice/publish.py:452`
- `_rebuild_index_from_disk` lists every `<slug>.json` on disk, including held voices.
- **Scenario:** `voice_flow` publishes all voices before the operator gate (its publish runs right after Step 2), and the operator then marks `octopus` `hold_for_regen`. On `main`, a full republish rebuilt `_index.json` from that call's voices and dropped `octopus`. On the branch it stays listed. Repro: index `['octopus', 'plato']`, `voice_count` 2, after the hold.
- C50's tracker entry records this as a "known edge", which implies nothing changed. In fact it is a behavior change against `main` for the C28b gate.
- **Fix:** pass the held set into `_rebuild_index_from_disk` and skip those slugs (the page file can stay).

**5. MINOR · CONFIRMED: `"manual": true` on an API step bypasses both refusal rules, and no call site checks `cfg.manual`.** `runtime/flows/shared/model_routing.py:142`
- A manual step gets `thinking=None`, and effort isn't checked.
- **Scenario:** a config slip marks `runtime.voice.step1` as manual. The loader accepts it and `stream_voice_call` sends Opus 4.7 with thinking silently off. The same slip on `claude-opus-5-5` with `effort: null` is also accepted (ran both).
- Call sites also don't check `cfg.vendor`, so an env override that routes a non-Anthropic model into an Anthropic call site isn't refused before the call. The API errors at call time, same as on `main`.
- **Fix:** in `stream_voice_call`, `call_claude` and the other `step_config` consumers, raise on `cfg.manual` or on a vendor that doesn't match the SDK. Or have the loader refuse `manual` outside `personas.dr_*`.

**6. NIT · CONFIRMED: the C53 restamp skips nested amendment names.** `runtime/scripts/restamp_published_voice_names.py:54`
- It only rewrites dicts that carry both `voice_slug` and `voice_name`. `deliberation.amendments[].cited_voice_name` (keyed `cited_voice_slug`) is never restamped.
- **Scenario:** a Step 3 night published before C53 keeps "I am Augusta Ada King…" in `cited_voice_name`. Athens isn't affected: Step 3 was skipped, and a dry run on a copy of the published record changes 0 fields; no field anywhere starts "I am".
- **Fix:** also handle the `cited_voice_slug` / `cited_voice_name` pair.

**7. NIT · CONFIRMED: a malformed ladder env value crashes with the wrong error.** `runtime/flows/shared/model_routing.py:192`
- **Scenario:** `VOICE_VALIDATION_MODELS=","` raises `IndexError: tuple index out of range` instead of `ModelRoutingError`.
- **Fix:** raise `ModelRoutingError` when the parsed ladder is empty.

**8. NIT · CONFIRMED: `PROVOCATEUR_THINKING` now means something different.** `runtime/flows/shared/model_routing.py:187`
- On `main`, thinking was on only when the value was exactly `"1"`. On the branch, anything outside `{0,false,off,no}` turns it on, and an empty value falls through to the file's `adaptive`.
- **Scenario:** `PROVOCATEUR_THINKING=` (empty) or `=true`: thinking was off on `main`, is on on the branch. It isn't set in `code/.env` today.
- **Fix:** accept it as the uniform rule, but note it in `LLM_CALL_INVENTORY §5`.

**9. NIT · PLAUSIBLE: the C66 test depends on thread timing.** `runtime/tests/test_editor_flow.py:329` and `:346`
- It needs both remaining threads to start within one 50 ms sleep.
- **Scenario:** on a loaded CI box, thread 1 finishes before thread 2 is scheduled, so `rest[1]` is `("end", 1)` and the test fails.
- **Fix:** use a `threading.Barrier(2, timeout=…)` in `fake_call` for the parallel phase instead of the sleep.

**10. NIT · PLAUSIBLE: the editor finds `council_config.json` from `run_dir.parent.parent`, not from the `project_root` it was given.** `runtime/flows/editor/routing.py:440`, `runtime/flows/editor/dossier_generation.py:168`
- **Scenario:** `editor_flow.py <run_dir> --project P` with a run dir outside `P/runs/` finds no `council_config.json`. Names then fall back to title-cased slugs, which drop the article: "the Voice of Octopus". The same fallback hits any slug missing from the config.
- **Fix:** thread `project_root` from `run_editor_pipeline` into `route_themes` and `build_dossier_briefing`.

## 2. Behavior changes against `main`

- **Intended (C63):**
  - (a) The persona ladders route each rung by vendor. For the shipped ladder the request shapes are identical: gpt-5.4 gets `reasoning_effort=high`, gpt-4.1 / o3 / gpt-4o get none, Gemini is last, and `max_tokens` stays 16384.
  - (b) Runtime Step-1 validation: gpt-4.1 and gpt-4o now get `temperature=0.0` + `max_tokens` with no `reasoning_effort`. gpt-5.4, o3 and Gemini are unchanged.
  - (c) `call_claude` drops `temperature` only for `sampling_params:false` models. It is a no-op for every current caller.
- **Intended (C63):** env overrides are read per call, not at import. An override naming a model that isn't listed now raises before any API call. Empty values count as unset (C63).
- **Intended, per-item:** C46 / C50 rebuild the indexes from disk (see finding 4). C49 now degrades instead of halting. C53 resolves names from `council_config`. C54 has the orchestrator self-heal `status.json`: `done` when a session package exists, `error` on a dead or zombie PID. On `main` it waited for the dashboard to do this. C56 strips `corpus_metadata`, which the editor's system prompt previously carried (the real card is a dict). C64: the body no longer starts with `**`, and `issue_no` / `vol` / `publication_date` are gone. C65: `--no-cache` is renamed `--no-prompt-cache`, and nothing else passes the old flag. C66: the first call runs alone.
- **Intended but unlisted:** `publish_flow.py:85` now uses `load_dotenv(override=True)` (`4b7ac0d`). That matches every other flow, and `code/.env` sets no model or thinking vars.
- **Unexplained:** finding 1 (Speaker ID chain) and finding 8 (`PROVOCATEUR_THINKING` values). Also, `GEMINI_MODEL` no longer reaches Pass 7c's primary call or the ladders' Gemini rung, which now pass `model=` explicitly. That env var is unset today.

## 3. Test gaps that matter

- No test covers the Speaker ID env chain, including `TRANSCRIPTION_CLAUDE_MODEL` (finding 1).
- No test covers a C49 resume or retry after the fallback was written (finding 2).
- No test covers held voices in the rebuilt voice index (finding 4).
- No test checks that call sites refuse a `manual` step (finding 5).
- By reading the fixed paths, the new C46, C49, C50, C51, C53, C64, C65 and C66 tests all target the old bug and would have failed on `main`. No new test reads athens-2026 or the network. The athens shapes are embedded as data. The only timing dependency is finding 9.

## 4. Checked and found sound

- **Loader:** byte-identical in both copies. `CONFIG_PATH` resolves to the repo root, and the VM deploy is a full clone. The whole file is validated on load. The refusal rules work: thinking-off on an undisableable model, missing effort on a model defaulting below high, non-OpenAI/Google ladder rungs, and unknown models, whether from the file or from env.
- **Golden test:** not circular. It is a hand table of `main`'s models and thinking, checked independently against every `main` call site. The call-site tests exercise the real code through fake clients.
- **Every converted call site** (transcription ×3, researcher ×3, provocateur ×3, voice step1/2/3, continuity, step2_validation, synthesis_router, editor, persona passes 0a/0b/1-merge/1.7/1d/2–6/ct/7-pre ×3/7a-fix/7b/7c + fallback/derive, 1a/1b): model, thinking shape, no effort, temperature, max_tokens and caching all match `main`.
- **Personas env:** `CLAUDE_MODEL` never reached personas on `main`, because every caller passed `model=`.
- **C53:** `member_slug` strips "Voice of [the]". All ten real slugs resolve verbatim, including the two with "the". Headnotes are "the " + name. Nested `voices_read` resolve. The published record is fully restamped.
- **Dossier index, two writers:** each writer keeps the other's fields whichever runs first or reruns: `edition_lead` survives publish, `voices_in_night` survives the editor. Both now read the dossier list from disk, and `.tmp` files are excluded.
- **C51:** the `cluster_ids` fallback matches the real `grouping.json` shape (`clusters[].cluster_id`).
- **C54:** there is no double-launch or skip path. Zombie children read as dead through `ps` stat.
- **C49:** handling is scoped exactly. `extract_json` raises `JSONDecodeError`, and Prefect 3.6 re-raises the original after retries. Other errors still halt. The mapping is one per label, in the shape `merge_speaker_ids` expects.
- **C65 / C66:** the flag reaches the call, with no `cache_control` for either system-prompt shape. A failed first call, a theme with no voices, and `--single-dossier` all degrade safely (no cache read, same failure records).
- **C56:** strips the dict-shaped `corpus_metadata` of the real card.
- **§32.1:** no stale variable is read after the strip, because `combined_2_3` is refreshed at `:1479` before its only later use.
- **§32.2:** `council_member_name` is now validated.
- **§36:** `model_name()` is installed in both Jinja envs. `pass_0a_voice_config.md` is read raw and has no Jinja.
- **Prompt edits:** each changes only its item's text. The 4a / 6 "~60K" matches the 1d prompt body. `TARGET_TOTAL_CHARS = 30000` in `node1d_excerpt_selection.py` is an untouched, unused constant.
- **Ingest:** C58's `_sys.executable` is imported. The dashboard lookup is fixed. `__SUMMARY__` is fully removed. The new three-value return of `populate()` is unpacked correctly.
