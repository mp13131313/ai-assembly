# Handoff — Athens Night 1 production (2026-05-07 → 2026-05-08)

**Branch:** code at `main` `1337d04` (operator merged `feature/editor-deployment-context` between sessions). Athens-2026 at `main` `7908707`.
**Tests:** 245/245 runtime pass (pre-Voice-fire).
**Dashboard:** uvicorn on `:8766` pointed at athens-2026, admin/dev auth.

## Final state (afternoon 2026-05-08, Athens Night 1 PUBLISHED)

| Stage | Status | Notes |
|---|---|---|
| Stage 1 — Transcription | ✅ 12/12 sessions | 1,454 turns / 80,082 words. 9 audio (AssemblyAI) + 3 vendor reflection JSONs. |
| Stage 2 — Researcher | ✅ Complete | 205 extractions / 37 clusters / 11 themes. Wall ~14 min. |
| Stage 3 — Provocateur | ✅ Complete | 46 formulations across 10 voices, 8 themes selected, 3 dropped. Wall ~10 min. |
| Stage 4 — Voice | ✅ Complete | 46 Step 1 / 10 Step 2 outputs. Full 10-voice fire 12:00–12:26; 3-voice rerun 12:55–13:00 to remove AI-self-acknowledgment from Battuta/Whanganui/Cleopatra (operator decision: only Hannah engages with synthesis as load-bearing meta-frame). |
| Stage 5 — Editor | ✅ Complete (v2.1) | 5 dossiers · all 10 voices represented · lead = dossier_001 (theme_002 paideia, 4 voices, score 190). Three editor fires: v1 (12:45) with first 7 voices · v2 (13:18) full re-fire with interleave rule · v2.1 (13:26 + 13:29) single-dossier fires for Marley + Whanganui-pair under sacred-grammar discipline. |
| Stage 6 — Publish | ✅ Auto | `published_artifacts/dossiers/night_1/` (5 dossiers + `_index.json`) + `published_artifacts/nights/night_1/` (10 voice artifacts + `_index.json`); both committed at `87abdf2` and pushed to athens-2026 GitHub. |

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
| `7908707` | vendor_inbox Day 1 reflection JSONs |
| `bfa1f8a` | **published_artifacts(night_1) v1:** 10 voice artifacts + 5 dossiers · first complete editor pass with 7 released voices · v1 had Peschel surfaced + sequenced-voice catalogue pattern |
| `87abdf2` | **published_artifacts(night_1) v2:** edition with editorial-discipline rules · 3 deployment_context rules (panels-happened-preserved + Peschel anonymization + voices-interleave + sacred-grammar discipline) · 5 dossiers committed under final ruleset |

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

## Athens Night 1 final edition

| # | Theme | Voices | Kicker |
|---|---|---|---|
| 001 ★ LEAD | theme_002 (paideia) | 4 — Ada · Hannah · Battuta · Plato | WHO TEACHES THE TEACHERS |
| 002 | theme_001 (the line at depth) | 2 — Dostoevsky · Octopus | WHERE THE LINE RUNS |
| 003 | theme_004 (personhood vote) | 2 — Scheherazade · Whanganui | THE VERB WAS GRANT |
| 004 | theme_007 (friendship as polity) | 1 — Cleopatra | GARLAND OR COLUMN |
| 005 | theme_010 (belonging & monstrosity) | 1 — Marley | THE DIRECTION OF THE FIRE |

**Editorial-discipline guarantees verified in published surface text:**
- ✅ No mention of Matthias Peschel / "Provotypist" anywhere in publishable fields (kicker, headline, subline, front_abstract, pull_quote, body_paragraphs, theme titles, headnote framing). Where his interventions were load-bearing in the panel record, attribution moves to "the Voice of X, channelled into the room from the Assembly."
- ✅ Voices interleave inside argumentative paragraphs — they appear as evidence inside Tim's argument rather than section-headed exhibits. Lead dossier_001 weaves Ada/Hannah/Battuta/Plato across two paragraphs that converge on the "ijāza, paideia, aitias logismos, the operation-cards" synthesis.
- ✅ Rastafari sacred grammar (`I-and-I`, `dawta`, `sufferah`, `livity`, `chanting-down`) appears only inside attributed quotation in Marley dossier_005; closing line shifted to *"Watch where the fire is pointing"* in editor English.
- ✅ Te reo / Tupua-te-Kawa grammar (`ea`, `mana`, `tupuna`, `kawa`, `whakapapa`, `mātauranga`) appears only inside attributed quotation in Whanganui dossier_003; English-naturalized nouns (`iwi`, `marae`) and proper nouns (`Wai 167`, `Ruakā Marae`, `Tongariro Power Development`, `Te Awa Tupua`) remain in editor narrative as journalistic citation.

**Timing nuance (audit):** dossier_001/002/004 composed at 13:18–13:23 under v2 ruleset (interleave + Peschel exclusion). dossier_003/005 composed at 13:26–13:30 under v2.1 ruleset (interleave + Peschel + sacred-grammar). Sacred-grammar rule is voice-specific to Marley + Whanganui; not applicable to Ada/Hannah/Battuta/Plato/Dostoevsky/Octopus/Cleopatra. Lead dossier_001 preserved in published surface as composed under v2 (operator preference: it is the strongest piece of writing in the edition).

## Open items / follow-ups

### Filed for v4.1 (post-Athens)

- **Safeguards validator alignment with `voice_temporal_stance.default`** — Sonnet validator's `safeguards.ai_self_acknowledgment` pillar applies the OLD absolute "no AI-self-ack" rule and HOLDs Hannah + Battuta when they meta-frame synthesis as object of critique. The architectural fix in athens-2026 `25ec751` legitimizes that meta-framing, but the validator prompt didn't get the update. Operator-Released both for Athens; v4.1 needs validator prompt to know that meta-framing of synthesis is PASS for voices whose temporal_stance permits it.
- **Validator JSON parse-failure pattern** — Sonnet's structured-output for safeguards + voice_fidelity pillars produced malformed JSON on Hannah's complex artifact (long verdict-evidence with unescaped quotes/commas). Workaround: defensive WARN fallback + dashboard `_error` rendering. Real fix: try Opus 4.7 for validator OR add JSON-repair logic.
- **Editor doesn't cache dossiers** — `editor_flow.py` regenerates all dossiers on every fire (no `out_path.exists() → return cached` short-circuit like voice/step1 has). Means a "rebuild index" full-fire produces fresh Opus calls for all dossiers and risks regressing already-good content. Add file-existence cache like `run_step1_for_pair`.
- **`--single-dossier` rebuilds index with only that one dossier** — when running `--single-dossier theme_X`, Stage 3 rewrites `_index.json` to reflect only the processed dossier, dropping the others from the index. Either: (a) `--single-dossier` should preserve the existing index entries for unmodified dossiers, or (b) require a full re-fire to rebuild index. Currently mitigated by manual `build_night_index()` call.
- **Per-session extraction caching for Researcher** — `extract_session` task lacks `cache_key_fn`, so re-fires re-extract everything. 215→205 drift between v2 and v3 fires. Worth adding `cache_key_fn=task_input_hash` for determinism.
- **Editorial-discipline rules → permanent prompt patches** — three deployment_context rules from Athens Night 1 (Peschel anonymization, voices interleave, sacred-grammar discipline) candidates for permanent inclusion in `runtime/flows/shared/prompts/editor_dossier.md`. The voices-interleave rule is fully general (applies to any multi-voice dossier). The sacred-grammar rule is voice-specific (Marley + Whanganui) and could remain per-voice in card form (or be added to editor prompt as "voices declared with `sacred_grammar: true` get this discipline applied"). Peschel anonymization is operator-side per-event and probably belongs as deployment_context across nights.

### Pending operator decisions

- **Card patches from external-reader memo** (B-list 9 items) — voices stream territory; not blocking Athens. Memo at `_workspace/planning/voices/MEMO_2026_05_07_card_patches_from_external_reader.md`.
- **Marley sacred-grammar discipline empirical case** from wbbf26 dryrun — operator-accepted gap pre-Athens via D1 paragraph + post-Athens Rastafari-orbit reader gate. Empirical evidence from wbbf26 strengthens the post-Athens reader-gate calendaring case.

## Resume prompt for next Claude

> Read `CLAUDE.md` first (current branch state at top), then this HANDOFF.
> Athens Night 1 production COMPLETE — 5 dossiers + 10 voice artifacts published
> at athens-2026 `87abdf2` and pushed. Edition lead = dossier_001 (theme_002,
> 4 voices, "WHO TEACHES THE TEACHERS"). Editorial-discipline rules in
> `runs/athens_night_1/_dossier_deployment_context.md` (gitignored under runs/):
> Peschel anonymization + voices interleave + sacred-grammar discipline
> (Marley + Whanganui).
>
> For Athens Night 2 (2026-05-08 evening into 2026-05-09): copy or recreate the
> deployment_context at `runs/athens_night_2/_dossier_deployment_context.md` if
> the rules should carry forward. Voice cards are stable on athens-2026 main
> (`7908707`); no voice changes expected. Pipeline pickup is the standard
> overnight orchestrator path.
>
> Open v4.1 items (file under runtime/OPEN_ITEMS): safeguards validator
> alignment with voice_temporal_stance.default · validator JSON parse robustness
> · editor dossier file-existence caching · `--single-dossier` index preservation
> · researcher per-session extraction caching · editorial discipline rules →
> permanent prompt patches.
>
> Dashboard at http://127.0.0.1:8766/admin/tonight (admin/dev). Backups of all
> intermediate Night 1 states preserved at
> `/tmp/voice_athens_n1_meta_backup_2026_05_08/`.

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
