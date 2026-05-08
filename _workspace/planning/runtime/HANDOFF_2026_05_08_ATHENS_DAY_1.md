# Handoff — Athens Night 1 production (2026-05-07 → 2026-05-08)

**Branch:** code at `main` `1337d04` (operator merged `feature/editor-deployment-context` between sessions). Athens-2026 at `main` `7908707`.
**Tests:** 245/245 runtime pass (pre-Voice-fire).
**Dashboard:** uvicorn on `:8766` pointed at athens-2026, admin/dev auth.

## Current state (mid-day 2026-05-08, Voice mid-flight)

| Stage | Status | Notes |
|---|---|---|
| Stage 1 — Transcription | ✅ 12/12 sessions | 1,454 turns / 80,082 words. 9 audio (AssemblyAI) + 3 vendor reflection JSONs. |
| Stage 2 — Researcher | ✅ Complete | 205 extractions / 37 clusters / 11 themes. Wall ~14 min. |
| Stage 3 — Provocateur | ✅ Complete | 46 formulations across 10 voices, 8 themes selected, 3 dropped. Wall ~10 min. |
| Stage 4 — Voice | 🔄 IN FLIGHT | 10 voices firing all together. Test fire on Hannah + Plato landed clean before this full run. ETA ~30 min. |
| Stage 5 — Editor | ⏳ Pending Voice | No-op until Voice publishes. |

## What landed this session (2026-05-07 PM → 2026-05-08 mid-day)

### Code changes (all on `main`, all pushed)

| Commit | What |
|---|---|
| `ea7f4a8` | runtime: editor `deployment_context` override + reflection preprocessor + voices-stream memo (ext. reader review on wbbf26) |
| `0957ac4` | docs + planning: pre-Athens dryruns + Editor v2.1 deployment_context + Transcription v2.2 reflection-preprocessor + voices §31 Gap-H/I/J |
| `3072857` | runtime(editor prompt): tighten headnote spec to 50-80w self-standing (theme→formulation→read-for) |
| `22734fb` | planning(runtime) C41: Provocateur-briefing-too-thin item |
| `3421da1` | runtime: reflection preprocessor `--session-id` override (vendor sent UUID instead of canonical) |
| `79e4080` | runtime(editor): pull_quote field — Tim picks one quote per dossier with attribution |
| `1337d04` | **runtime trio (today):** CLUSTERING_MAX_TOKENS 40K→64K + dashboard validator `_error` rendering + researcher page direct cluster/extractions links |

### athens-2026 commits

| Commit | What |
|---|---|
| `b1184d7` | published_artifacts: pre-Athens production-equivalent dryruns (mthd + wbbf26 v2) |
| `6536f16` | wbbf26 v3 dossiers (tightened headnote spec) |
| `734f043` | pre-Athens-Night-1 cleanup: archive dryrun outputs + create vendor_inbox |
| `25ec751` | voices(all 10): remove epistemic-honesty hook from voice_temporal_stance.default |
| `5cc04ad` | voices(hannah_arendt): drop residual v1 "speak from within your own world and lifetime" leakage |
| `3fd94e6` | voices(all 10): voice_temporal_stance.default — operator short drafts |
| `0065f00` | sessions.json: duplicate Human Democracy Is Dead session (audio + vendor) |
| `658e8d0` | sessions.json: duplicate Act One: The Story of Us — second audio capture |
| `7908707` | **today:** vendor_inbox Day 1 reflection JSONs |

### Architectural fix VALIDATED on Athens Night 1

The `voice_temporal_stance.default` rewrite (athens-2026 `25ec751` + `5cc04ad` + `3fd94e6`) closes the AF/hard_limits collision that was logged as memo §A.9 / OPEN_ITEMS §31 Gap-J. Hannah's test-fire artifact opens with self-aware acknowledgement of her own synthesis:

> *"There is a comedy in being asked this... I am told that yesterday a voice bearing my name was synthesized to address the assembly..."*

She uses "synthesized voice", "trained model", "training-corpus" as **objects of critique**, never as native vocabulary uncritically — the hard_limits[4] discipline holds via meta-framing rather than literal extension-tagging.

Plato's test-fire artifact is pure Athenian (Stoa, paideia, dēmokratia, the cobbler/doctor/pilot homely-particular, closing reference to "the cup that my teacher drank"). No anachronism.

Both test artifacts backed up at `/tmp/voice_test_hannah_plato_2026_05_08/` before the full 10-voice fire.

## Bugs / quirks encountered + resolutions

| # | Bug | Resolution |
|---|---|---|
| 1 | `transcription_flow.py` CLI fired silently on wrong arg shape (printed docstring then exited fast) | Pass 2 args + `OUTPUT_DIR` env var instead of just session_dir |
| 2 | Act One pair (47-speaker sessions) failed speaker_id step with JSON decode error on both Sonnet and Opus output | Manual passthrough: write `out_02_speaker_id.json` with all-Unidentified-Speaker-N mappings, resume flow from cleaning step (out_01 + out_02 both exist → skip ASR + speaker_id) |
| 3 | Researcher clustering hit 40K output ceiling on 215 extractions (truncated JSON, parse fail) | Bump `CLUSTERING_MAX_TOKENS` to 64K; retry succeeded at 38K used (59%). Future high-volume nights may need extended-output beta header for 128K. |
| 4 | Reflection preprocessor wrote `review_queue: []` (list); Researcher's `review_queue.get(...)` AttributeError'd on the 3 vendor reflection session_packages | Fixed preprocessor to write dict shape `{low_confidence_attributions: [], diarization_flags: [], verify_markers: []}`. Patched 3 existing session_packages in place. |
| 5 | Vendor JSON delivered with their internal UUID as session_id (not our canonical) | Added `--session-id` override flag to preprocessor; vendor's UUID preserved as `_vendor_internal_session_id` for audit |
| 6 | Validator's pillar JSON parse failures on Hannah artifact were rendered on dashboard with verdict=WARN but all check fields showed "— none" — operator couldn't see WHY it WARNed | Patched `admin_render_step2_validation.html` to surface `_error` field with red callout + parse error text |
| 7 | Researcher dashboard linked grouping.json directly but not clusters.json or all_extractions.json | Patched `admin_researcher.html` to add direct file links for all three |

## Open items / follow-ups

### Active

- **Voice Pipeline mid-flight on athens_night_1.** Will publish to `published_artifacts/nights/night_1/` when complete. Then operator review gate (per-voice Release/Hold) → editor auto-fire on completion.
- **Validator parse-failure pattern** — Sonnet's structured-output for safeguards + voice_fidelity pillars produced malformed JSON for Hannah. Could be: long verdict-evidence strings with unescaped quotes/commas; specific to complex artifacts. Workaround: defensive WARN fallback. Real fix: try Opus 4.7 for validator (model override env var) OR add JSON-repair logic. File for v4.1.
- **Per-session extraction caching for Researcher** — `extract_session` task lacks `cache_key_fn`, so re-fires re-extract everything. 215→205 drift between v2 and v3 fires. Worth adding `cache_key_fn=task_input_hash` for determinism. File for runtime/OPEN_ITEMS C-class.

### Pending operator decisions

- **Card patches from external-reader memo** (B-list 9 items) — voices stream territory; not blocking Athens. Memo at `_workspace/planning/voices/MEMO_2026_05_07_card_patches_from_external_reader.md`.
- **Marley sacred-grammar discipline empirical case** from wbbf26 dryrun — operator-accepted gap pre-Athens via D1 paragraph + post-Athens Rastafari-orbit reader gate. Empirical evidence from wbbf26 strengthens the post-Athens reader-gate calendaring case.

## Resume prompt for next Claude

> Read `CLAUDE.md` first (current branch state at top), then this HANDOFF.
> Athens Night 1 Voice Pipeline is mid-flight on athens_night_1; Stage 5 (Editor)
> awaits Voice completion + operator review-gate Release decisions.
> Once Voice lands, fire `flows/editor_flow.py "$RUN_DIR" --night 1 --bypass-gating`
> (or via dashboard auto-fire after operator releases per-voice).
> Dashboard at http://127.0.0.1:8766/admin/tonight (admin/dev).
> Fresh Hannah + Plato test artifacts saved at `/tmp/voice_test_hannah_plato_2026_05_08/`
> for pre/post comparison if needed.

## File pointers

| What | Where |
|---|---|
| Voice flow CLI | `runtime/flows/voice_flow.py` (supports `--voices` filter for subset runs) |
| Editor flow | `runtime/flows/editor_flow.py` (auto-fire via dashboard or `--bypass-gating` CLI) |
| Reflection preprocessor | `runtime/scripts/reflections_to_session_package.py` (with `--session-id` override) |
| Vendor intake | `runtime/flows/vendor_intake.py` (validates session_package shape; lands at 01_transcription/) |
| Editor closing prompt (v2.1 + headnote spec + pull_quote) | `runtime/flows/shared/prompts/editor_dossier.md` |
| Voice cards (athens-2026 main, AF-leads temporal_stance) | `athens-2026/voices/<slug>/07_persona_card_assembled.json` |
| Hannah test artifact (pre-full-fire backup) | `/tmp/voice_test_hannah_plato_2026_05_08/step2_first_draft_artifacts/hannah_arendt.json` |
