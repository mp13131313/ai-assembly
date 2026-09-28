# Review: code `phase0-fixes` does not change (ripple zone + audit)

**Verdict: ripple zone CLEAR for the merge.** No untouched caller breaks on the branch's changed interfaces; two small dormant or visibility gaps are listed below. **Untouched code overall:** the untouched code has 1 BLOCKER-class defect (the reflections preprocessor fed blank session metadata to the Researcher on all 5 Athens reflection sessions) plus 4 MAJOR ones: stale continuity after a reset, Wikisource truncation, the systemd sandbox paths, and a sentinel-regen tool that can't run. All are pre-existing and none blocks the merge.

Reviewed at `cd7c790` (branch `phase0-fixes`, detached), 2026-09-28, by Fable 5.1 using the code-review skill, scoped by `BRIEF_2026_09_28_untouched_code_review.md`. No code edited. Suites green before review: runtime 368 / ingest 114 / personas 242.

---

## 1. Ripple-zone findings

**R1. MINOR: the dormant Step-3 prompt still names peers by their long `council_member` identity line** (CONFIRMED).
- **Where:** `runtime/flows/voice/card_assembly.py:547-565`. `filter_first_draft_for_step3` renames each peer draft's `council_member` to `voice_name` for the Step-3 prompt. The same happens at `step3_amended_artifact.py:76` (a diff file; noted for the tracer).
- **What's wrong:** C53 (`02fb283`) fixed only the Step-3 *publish* path.
- **Failure scenario:** in Athens Night-1 Step 2, 8 of 10 voices' `council_member` is the long identity line ("I am Augusta Ada King, Countess of Lovelace — Byron's daughter…", "I am octopus. The name is yours…"). When Step 3 is re-enabled (C61), every voice would read its peers under those names.
- **Fix:** resolve with `voice_display_name(first_draft["lineage"]["voice_slug"], project_root)`.

**R2. MINOR: the C49 degrade is invisible outside `review.md`** (CONFIRMED by grep).
- **What's wrong:** the new `speaker_id_auto_passthrough` flag lands only in `session_package.review_queue.diarization_flags` and `review.md`. Nothing in `runtime/ingest/*` or the orchestrator reads `diarization_flags`.
- **Failure scenario:** a 47-speaker session now shows plain "done" on the dashboard. The orchestrator fires the Researcher, and the night's extractions carry "Unidentified Speaker N" with no operator signal. In Athens the halt *was* the signal.
- **Fix:** surface a flag count on the dashboard's transcription row, plus one orchestrator log line.

**R3. NIT, external microsite risk (can't verify).** Published data the microsite may read has changed shape:
- per-voice and index `voice_name`: "I am …" became "Voice of X";
- headnote names now read "the Voice of X";
- the dossier indexes lost `issue_no`, `vol` and `publication_date`, and gained `voices_in_night`;
- `themes/night_N/` now exists (C51);
- new dossiers no longer start `body_paragraphs[0]` with `**\n`.

If the microsite special-cased any of these, check it before its next build.

**Checked clean:**
- **Model routing:** `personas/run_pass_1_*` go through `chunk_runner` (`step=personas.pass_1_merge`). `phase_5_cross_persona_qc.py` and `standalone_pass4b_test.py` pass explicit `model=`, which `call_claude` still accepts. `ingest/pipeline._subprocess_env` env passthrough is compatible; the real `.env` sets none of the legacy model vars.
- **Templates:** `split_tailored_prompt.wrap_section` renders the `model_name()` global. I ran it offline for §1/§3/§6: it produces "Claude Opus 4.7" and takes the same-model §6 branch. No code references the deleted 7pre prompts.
- **Orchestrator (C54):** the import-time `AI_ASSEMBLY_PROJECT_ROOT` dependency pre-existed on `main`. Vendor `status=done` and `error` are terminal in `infer_state`.
- **Editor:** no untouched caller of `--no-cache`.
- **Indexes:** `editor/publish.load_prior_editions` reads dossiers only.
- **Scripts:** every untouched script passes `--help` (or `--list`) in its venv.

---

## 2. Audit findings

**A1. BLOCKER: the reflections preprocessor writes metadata keys the Researcher never reads** (CONFIRMED on athens-2026 data; pre-existing, not merge-blocking).
- **Where:** `runtime/scripts/reflections_to_session_package.py:80-87`.
- **What's wrong:** it copies `title`, but the session_package contract (`transcription_flow.assemble_session_package`, Transcription spec §Step 5) is `session_title` / `session_description` / `session_format` / `track` / `roster`. It also copies keys `sessions.json` doesn't have (`track_or_program`, `panelists`, `moderator`, `host`, `roster`, `expected_participant_count`).
- **Failure scenario:** `researcher_flow.py:173-175` built the extraction prompt with `Session:` and `Description:` blank and `Format: panel`, for audience reflections. `session_title` fell back to the raw id in all 103 extractions of the 5 reflection sessions (N1 27+25+12, N2 14, N3 25).
- **Fix:** map `title→session_title` and `description→session_description`, set a `session_format` such as "audience reflections", copy `track`, and build `roster` from `speakers` + `speakers.json`. Have `vendor_intake` warn when `session_title` is missing.

**A2. MAJOR: replaying a night keeps the old continuity** (CONFIRMED by reading).
- **What's wrong:** `runtime/scripts/reset_run.py:84-87` (voice stage) does not delete `<PROJECT_ROOT>/voices/<slug>/continuity_night_<N+1>.json`, and `continuity.generate_continuity` returns an existing file unchanged (`continuity.py:142-145`). `voice_flow` has no way to force regeneration.
- **Failure scenario:** `reset_run.py runs/athens_night_1 --from-stage provocateur` is the docstring's own example. After it, the new Night-1 artifacts publish, but Night-2 voices still get "YOUR PIECE FROM NIGHT N-1" and a signature-move register describing the *deleted* pieces. A `hold_for_regen` single-voice rerun on Night 1 or 2 hits the same cache.
- **Fix:** the voice-stage reset deletes the next-night continuity files (when N<3), or continuity regenerates when the Step-2 artifact is newer than the cached file.

**A3. MAJOR: Wikisource fetches are truncated to the header template** (CONFIRMED: data plus a throwaway script).
- **Where:** `personas/flows/shared/node1c_fetch.py:39-42, 107-109`.
- **What's wrong:** `_WIKISOURCE_CONTENT` captures `(.*?)</div>` non-greedily, so the capture ends at the first nested `</div>` inside `mw-parser-output`.
- **Failure scenario:** Lovelace's *Sketch of the Analytical Engine* (her Notes, the core primary text) is stored in `athens-2026/voices/ada_lovelace/03_corpus/01_primary_texts.json` as 697 chars of header CSS. voices §25 counted it as a successful fetch ("19/20 ✓"). Every future Wikisource source loses its body.
- **Fix:** select `.mw-parser-output` with bs4 (already imported). Treat fetches under ~2K chars as failures in the 1c review gate.

**A4. MAJOR: the systemd sandboxes block the paths the services write** (CONFIRMED by reading; not run, since the VM was never provisioned, B10).
- **Ingest:** `runtime/ingest/deploy/ingest.service:49` allows `/opt/ai-assembly/runtime/{runs,reference}`, the pre-Tier-3 paths. `RUNS_DIR` is `/opt/ai-assembly-athens2026/runs`. Under `ProtectSystem=strict`, every upload fails at `mkdir`, and the ingest editor auto-fire can't write either.
- **Orchestrator:** `runtime/scripts/deploy/orchestrator@.service:60` omits `/opt/ai-assembly-athens2026/voices`. Continuity writes fail, get logged as `continuity_failures`, and Nights 2+ run without memory. PLAUSIBLE, same cause: Prefect's home under `/opt/ai-assembly` is read-only.
- **Fix:** allow `<PROJECT_ROOT>/{runs,published_artifacts,voices,reference,vendor_inbox}` plus a writable `PREFECT_HOME`, and add this to the deploy README.

**A5. MAJOR: `sentinel_regen.py`, the Stage-4 quality gate, can't run** (CONFIRMED: `ls` + read).
- **Where:** `personas/scripts/sentinel_regen.py:73-76, 229-235`.
- **What's wrong:**
  - the default sentinels point at `projects/phase-l-plato` and `projects/phase-l-dostoevsky`, which moved to `archive/` on 2026-05-01;
  - `--voices` accepts only those two slugs; any other prints "Skipping unknown sentinel voice";
  - there's no `--project` flag;
  - the docstring's usage (`--detect-changes`, `--pass`, `--baseline-tag`, `--diff-only`) doesn't match the real subcommands. voices ONBOARDING's `regen --voices <slug>` recipe fails the same way.
- **Failure scenario:** `regen` exits with "PROJECT_ROOT does not exist". It fails loudly, but Stage 4 has no working gate.
- **Fix:** add `--project` and accept any slug. Point it at a sandbox copy, not athens-2026: `regen` re-runs the full pipeline and would rewrite production cards.

**A6. MINOR: four voices' system prompts open "You are I am …"** (CONFIRMED: code + cards).
- **Where:** `runtime/flows/voice/card_assembly.py:421-422` emits `"You are {council_member_name}."`.
- **What's wrong:** the card spec (`Persona_Card_v2.md` §council_member_name) expects a name-style self-introduction ("Plato of Athens"). Four shipped cards hold a first-person sentence instead.
- **Failure scenario:** every Step 1/2/3 call on all three Athens nights opened "You are I am Augusta Ada King…", "You are I am Cleopatra Thea Philopator…", "You are I am octopus…", or "You are I am the construction stewarding…". This is a third surface of the C53 root cause.
- **Fix:** open with the `council_config` name, and render the field as its own self-introduction block. It changes voice input, so re-validate the affected voices.

**A7. MINOR: `vendor_intake.land()` overwrites the valid package before checking the new one** (CONFIRMED by reading).
- **Where:** `runtime/flows/vendor_intake.py:337-356`.
- **What's wrong:** it writes the new `session_package.json` *before* the turn_index alignment check. On failure the older valid package is already gone, contradicting its own comment at `:283-287`, and the Researcher's `*/session_package.json` glob picks up the misaligned one.
- **Also:** a non-string `speaker` (an object) passes validation, then crashes at `sorted({turn["speaker"]})` (`:211`) before any `status.json` error is written.
- **Fix:** validate the in-memory package (or a temp file), then replace; type-check `speaker` and `text` as strings.

**A8. MINOR: a per-night reset deletes every night's published extractions and voice pages** (CONFIRMED by reading).
- **Where:** `runtime/scripts/reset_run.py:92-108`.
- **What's wrong:** every `--from-stage` includes `publish`, which deletes the all-nights `published_artifacts/extractions/` and `voices/` directories and the cross-night `dossiers/_index.json`. Extraction ids are session-scoped, unique across nights (checked on Athens data).
- **Failure scenario:** a Night-3 editor reset wipes Nights 1-2 extraction pages until `publish_flow` re-runs for each night. It's latent today: Athens has no `extractions/` yet.
- **Also:** `run_dir` isn't checked to be under `--project`.
- **Fix:** delete only night-N extraction files, rebuild the cross-night indexes rather than deleting them, and assert `run_dir` is under `<project>/runs`.

**A9. MINOR: the setup scripts silently drop the hand-added second-recording sessions** (CONFIRMED: read + athens-2026 `sessions.json`).
- **Where:** `generate_sessions_json.py:237-296`, `apply_ai_assembly_flags_from_csv.py:114-151`.
- **Failure scenario:**
  - `generate_sessions_json.py` rebuilds only from the program HTML. The 7 `__audio` / `__audio2` sessions (all `ai_assembly=true`; `session_count` 146 vs 153 entries) vanish on re-run with no warning.
  - `apply_ai_assembly_flags_from_csv.py` fails the `_HHMM` suffix match for them, because they share their primary's title, and sets them to `ai_assembly=false`.
- **Also:** collision suffixes are applied after overrides are re-applied, so overrides saved under suffixed ids never match.
- **Fix:** carry forward prior sessions missing from the HTML (with a warning), and match the `__audio*` variants.

**A10. MINOR: Night-3 continuity is not the merged memory the spec describes** (CONFIRMED: code + data).
- **What's wrong:** `docs/AI_Assembly_Voice_Pipeline.md:1123` and `card_assembly.py:57-58` say Night 3's blocks "merge Nights 1+2". But `continuity._build_continuity_user_prompt` sends only the night just completed; only `signature_moves_deployed` accumulates.
- **Failure scenario:** all 10 Athens `continuity_night_3.json` blocks summarise Night 2 only. Their only mention of earlier nights comes from the operator's final-night notice.
- **Fix:** feed the prior continuity blocks to the summariser, or correct the spec.

**A11. MINOR: a session stuck in `normalizing` is never flagged** (PLAUSIBLE: read, not run).
- **Where:** `runtime/ingest/pipeline.py:222-283`, 505-523.
- **What's wrong:** `infer_state` has no liveness check for `normalizing` or `received` (the worker runs in-process), and `reconcile_on_startup` doesn't flag stale sessions either.
- **Failure scenario:** a uvicorn restart mid-normalize leaves the session at `normalizing` forever. The orchestrator, which now dispatches through `infer_state`, counts it as pending until the 14h deadline, and `/retry` refuses ("re-upload required").
- **Fix:** on startup, flip stale `received` / `normalizing` sessions to `error` with a re-upload message.

**A12. MINOR: `patch_walker` silently creates misnamed fields** (CONFIRMED: throwaway script).
- **Where:** `personas/flows/shared/patch_walker.py:92-94`.
- **What's wrong:** a misspelled final path segment (`knowledge_boundry`, `world.framework_for_difficulty`) adds a new key instead of raising.
- **Failure scenario:** 7a-FIX logs the patch "APPLIED" (`run_persona_pipeline.py:1417-1425`), the real field stays unfixed, and a junk key lands in the pass file.
- **Fix:** require the final key to exist; otherwise fail the patch.

**A13. MINOR: the fetch SSRF guard doesn't check redirects** (PLAUSIBLE; related to the filed TOCTOU item in roadmap 0.3b, new evidence).
- **Where:** `node1c_fetch.py:167-173`.
- **What's wrong:** `urlopen` follows redirects to any host, including `169.254.169.254`, without re-running `_check_url`. `_PRIVATE_NETS` also lacks `0.0.0.0/8`, `100.64.0.0/10`, `fe80::/10` and IPv4-mapped IPv6. Pinning the resolved IP, the filed fix, doesn't cover redirects.
- **Fix:** a redirect handler that re-runs `_check_url`, plus the missing ranges.

**A14. NIT: stale council size and member in production Provocateur prompts** (CONFIRMED).
- **What's wrong:** `provocateur_triage_voice.md:27` says "A council with 12 voices"; Athens ran 10. `provocateur_formulation.md:140-141` uses removed member Peter Thiel as its worked example.
- **Fix:** template the council size; swap the example.

**A15. NIT: an unfilled "N-1" reaches the voices.** `card_assembly.py:328, 332`: the section headers read literally "FROM NIGHT N-1".

**A16. NIT: the persona cost ledger is dead** (CONFIRMED by grep). No caller passes `slug` / `pass_name`, so `clients._record` → `manifest.record` never writes `voices/<slug>/_manifest.json`, which `invalidate_cache` then "deletes". `record` is also an unlocked read-modify-write; it would lose entries under the parallel chunk runner if wired. **Fix:** wire it (with a lock) or delete it.

**A17. NIT: a validation check that can't fail.** `research_validation.py:98-102`: section coverage matches bare words ("voice", "primary", "foundation") anywhere, so it effectively always passes.

---

## 3. Coverage

**Read fully:**
- **Ingest:** `runtime/ingest/{auth,sessions,render,config,pipeline}.py`.
- **Runtime flows:** `flows/vendor_intake.py`, `flows/voice/card_assembly.py`, `flows/editor/publish.py`, `flows/shared/project_root.py`.
- **Persona shared modules:** `personas/flows/shared/{io,manifest,patch_walker,bracket_strip,dr_validation,research_validation,node0_validation,node1c_fetch,node1d_excerpt_selection,perplexity_split,url_extract,wikipedia,project_root}.py`.
- **Runners:** `run_pass_1_1`, `run_pass_1_all`.
- **Scripts:** `reset_run`, `generate_sessions_json`, `generate_speakers_json`, `apply_ai_assembly_flags_from_csv`, `reflections_to_session_package`, `markdown_to_researcher_output`, `sentinel_regen`, `invalidate_cache`, `split_tailored_prompt`, `validate_dr_dossier`.
- **Deploy and prompts:** both systemd units, the Caddyfile, `voice_continuity.md`.

**Read in part:**
- `paths.py` (index plus key helpers), `standalone_pass4b_test.py`.
- `phase_5_cross_persona_qc.py` (call sites only), `migrate_to_per_voice_layout.py` (move and guard logic).
- `ingest/app.py` upload and retry paths (a diff file, for tracing only).
- Schemas: `_entry`, `_conventions`.

**Grep-scanned, not read line by line:**
- all untouched runtime prompts (placeholder-vs-fill check: all filled);
- all untouched persona prompts (event, council and removed-member wording);
- ingest templates (no `|safe`; autoescape on).

**Skipped:**
- `run_pass_1_{2..6}` (same wrappers; checked only with `--help`);
- `arch_03_*` (`--help` only);
- the remaining `personas/schemas/*.py`;
- line-by-line reading of the persona generation prompts (full-read 2026-06-12/13);
- tests and fixtures.

**Probes:** three offline `python -c` checks, none calling a model: the Wikisource regex, `patch_walker`, and `wrap_section`. The only file written was a scratch copy of the athens-2026 `reference/*.json`, for the ingest suite. athens-2026 was read only.
