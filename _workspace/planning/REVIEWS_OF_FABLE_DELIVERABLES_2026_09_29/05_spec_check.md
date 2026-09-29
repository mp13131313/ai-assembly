# Review of `_workspace/planning/runtime/REVIEW_2026_09_28_spec_check.md`

## Verdict

1. **Quality:** high. I re-checked every consequential discrepancy against the code on `main`, and all of them hold. The cost figures reproduce to the cent. Only one claim has gone stale since C67 (L15, the test count).
2. **How far to trust it:** trust the diagnoses. Do not paste its replacement blocks unreviewed. One is wrong (L8), two are doubtful (L9, L13), and three need a clause added or corrected (E7, E14, F1).
3. **Biggest issue:** E7's operator-override procedure leaves out `primary_dossier` and `n_engaged_voices`. Stage 3's night index, `publish_flow` and the lead pick all read those two fields. An operator who followed the procedure would publish a moved voice under its old dossier in the index, and the lead pick would score stale counts.

**How I checked.** Everything is read-only, on `main` at `0910a66`, with athens-2026 read-only. I made no API calls. I reproduced E9 with my own offline pricing of the 13 dossiers' `metadata` and compared file mtimes for E10.

The deliverable's `file:line` references are at `4e61444`, and C67 (`02006f5`) has since shifted several of them:

| File | From about line | Shift | Example |
|---|---|---|---|
| `editor/routing.py` | 418 | +9 | refusals: 458 → 467; return dict: 542–551 → 551–560 |
| `editor_flow.py` | 165 | +1 to +2 | CLI: 321–356 → 323–358 |
| `editor/dossier_generation.py` | 137 | +5 | |
| `scripts/overnight_orchestrator.py` | 202 | +2 to +18 | |
| `ingest/app.py` | 458 | +5 | |
| Transcription spec | 397 | +2 | Constraints line: 531 → 533 |

The replacement blocks mostly carry no line numbers, so only the evidence citations are affected. The Editor spec's own existing citations (`routing.py:458-464` at line 174 and `routing.py:542-551` in the Stage 1 note) are now off by 9. Whoever applies the fixes should correct them too.

## Findings, one by one

| ID | Claim (short) | Verdict | Evidence / reason |
|---|---|---|---|
| E1 | Routing mostly happens in Voice Step 2; the editor's Stage 1 is a fallback | VERIFIED | Step 2 resolves the theme at `step2_first_draft_artifact.py:196-296`, and the editor takes it first at `routing.py:143-146`. All 29 Athens entries are "Case A — Step 2 resolved" (10+9+10). I opened all five synthesis voices (N1 Dostoevsky and Scheherazade, N2 Octopus, N3 Cleopatra and Octopus): each has `primary_theme_id_source: "synthesis-routed: …"`. That upgrades the four the document marked PLAUSIBLE. |
| E2 | The spec's Stage 1 input list is incomplete | VERIFIED | Every listed read exists (`routing.py:144, 335-366, 396-411, 471, 481`). Small gap in the replacement: briefings also supply `themes_to_dossiers[].theme_title` (`_theme_titles_from_briefings`, `:382-393`). |
| E3 | Case labels differ, spec Case B doesn't exist, the marker lists differ, refusal is checked first | VERIFIED | Cases at `routing.py:148-233`; markers at `:57-66` and `:87-94`; the refusal check runs before any case (`:467`). The router falls back to lowest-numbered on an API error or an unknown `theme_id` (`synthesis_router.py:146-174`). The replacement algorithm block matches the code's order. |
| E4 | The legitimacy-test sample note is stale | VERIFIED | Same data as E1. |
| E5 | The manifest example differs: `voice_name` form, source labels, the extra `dossier_lead_order_default`, refusal `form` | VERIFIED | `routing.py:498-504, 551-560, 471`. All three Athens files carry the six top-level keys. Addition: `dossier_lead_order_default` has **no reader** anywhere in `runtime/` (grep), so it is always `[1..N]` and nothing uses it. Say so in E6's line. |
| E6 | The v2-changes note should mention `dossier_lead_order_default`, and that the lead pick is in Stage 3 | VERIFIED | `edition.py` is the Stage 3 lead picker (docstring, `pick_lead_dossier`). |
| E7 | There is no review window between Stages 1 and 2; hand edits need `--skip-routing`; a voice moved to an unlisted theme drops out | VERIFIED | `editor_flow.py:154-169, 188, 79-85`. |
| E7-repl | The replacement override procedure | DOUBTFUL (incomplete) | It never tells the operator to update `primary_dossier` or `n_engaged_voices`. Stage 3's night index groups voices by `primary_dossier` (`edition.py:141-142`), and so does `publish_flow` (`:702-704, 877-878`). The lead pick scores `themes_to_dossiers[].n_engaged_voices` (`edition.py:83, 112`). The document itself notes these fields "are not recomputed" but doesn't carry that into the procedure. |
| E8 | "Structured output" contradicts prose-and-parse | VERIFIED | `parse_dossier_output` (`dossier_generation.py:383ff` on main). |
| E9 | Measured cost: about $9.93, not $3–5 | VERIFIED | My independent recomputation gives the same numbers: N1 $2.09, N2 $4.54, N3 $3.29; cache-writing calls $0.77–1.21; cache-reading calls $0.22–0.73; output share 70–83%; write share 43–68%; the C66 counterfactual N2 $2.54, N3 $2.29. Input 8,105–36,677 (median 19,833); output 5,906–24,401 (median 10,444). The replacement table's arithmetic checks out. |
| E10 | The Night 3 interval is not "slower routing"; the editor ran 220 s and 212 s | VERIFIED | Manifests: `wall_clock_s` 220.06 and 212.1. The mtimes confirm the "waiting for releases" cause, which the document had as PLAUSIBLE. N2: the last decision (the Whanganui hold) at 14:41:56, `theme_routing.json` at 14:42:07. N3: all decisions at 17:27:15, routing at 17:27:26, voice manifest at 17:22:14. |
| E11 | Five problems in §"Cost & Envelope" | VERIFIED | The first-call row already contains the $0.30 write, so line 1011 double-counts it. The Stage 1 fallback can call the router. Nuance: there is no automatic serial fallback, but `EDITOR_BATCH=1` gives a serial run by hand. |
| E12 | `max_tokens` 32K; measured output up to 24,401 | VERIFIED | `dossier_generation.py:49`; N1/001 metadata. |
| E13 | The CLI list misses `--bypass-gating` and `--project`; `--night` accepts only 1–3; exit codes 0/2/3; C66 staging | VERIFIED | `editor_flow.py:326, 334-339, 343, 354-358, 254-266`. Two small gaps. Exit 1 (uncaught error or `SystemExit(msg)`, e.g. `--skip-routing` with no file) isn't listed. The module docstring's own CLI block (`:28-33`) also lacks `--bypass-gating`. |
| E14 | One defensive check exists, two don't | VERIFIED | No `04_voice/manifest.json` read anywhere in `editor/` or `editor_flow.py` (grep); `load_editor_card` at `card_assembly.py:116-133`. The replacement is imprecise on the deployment block. Each file drives its own part: `conference_facts.json` gives THE GATHERING and YOUR ROLE, `council_config.json` gives THE PANEL (`card_assembly.py:260-281`). So one missing file drops only its own part. |
| E15 | The tail is identical per night; both blocks carry a 1h breakpoint | VERIFIED | `card_assembly.py:340-367`; `_anthropic_call.py:127-133`. |
| E16 | Open Questions heading, Q1 and Q7 are stale; the dashboard also fires the editor | VERIFIED | `641e31d` added `synthesis_router.py`; orchestrator Stage 3.5 plus `validation_gate_state`; `app.py:877-935`. Unmentioned: `.editor_running.lock` is created (`app.py:919`) and never deleted by any code, and N2's is still on disk. "Lockfile-guarded" therefore also means that after one failed or blocked auto-fire, the dashboard never auto-fires that night again. |
| F1 | Broadsheet → dossiers under HoBB; no masthead, issue numbers, wire-service paragraph or strikethrough; artifacts embedded | VERIFIED | `editor_dossier.md:26-27` "the unnamed editor"; `641e31d` dropped the chrome; `8b84e58` embeds `artifact_text`; no strikethrough or wire-service text in the prompt or in any of the 13 dossiers (grep). |
| F1-hl | "Per-voice torque survives in `artifact_title`, via Tim's `translation_protocol`" | DOUBTFUL | The prompt does route `artifact_title` through `translation_protocol` (`editor_dossier.md:175, 203`). But Tim's `translation_protocol` (3,093 characters) names no voice and never says "headline". The three `_dossier_deployment_context.md` files carry no torque content either. B9 planned that content for Claudia's card, and it never reached Tim's. What survives is a generic register translation, not per-voice headline poetics. Soften the status block to match. |
| F2 | The Edition Pipeline was never built; the Editor Pipeline replaced it | PLAUSIBLE | Consistent with B3 and the code; I did not check the tracker history. |
| F3 | Substack dropped (B4) | VERIFIED | OPEN_ITEMS B4 heading "✅ CLOSED 2026-05-04 (superseded …)". |
| F4 | The micro-site is outside the repo; B7 is partial | PLAUSIBLE | `runtime/assets/octopus_chromatophore/` exists; the rest can't be checked. |
| F5 | No closing-show or matrix code | VERIFIED | Repo grep finds only two comments (`voice_flow.py:293`, `voice/publish.py:6`). |
| F6 | Ten voices; Thiel and Tang dropped | VERIFIED | Frame Concept line 9; OPEN_ITEMS "Recently landed". |
| F7 | Related docs stale; none of the seven "new documents" exists; E5 should be re-scoped | VERIFIED | v3.10 is in `docs/_archive/`; no `Till_Briefing` in `git ls-files`; E5's list at OPEN_ITEMS line 2976. |
| F8 | The FU#61 note is design, not code | PLAUSIBLE | Judgment call. |
| T0 | What happens now on the vendor route | VERIFIED | Read in full: preprocessor `:91-172`; `vendor_intake.py` docstring and CLI; `app.py:518-523` refuses uploads for every role. All five packages carry `_vendor_internal_session_id` and `vendor.warnings`. |
| T1 | "Between Stage 0 and Stage 1" is wrong | VERIFIED | The vendor route lands at the output boundary. |
| T2 | Only `title`, `day`, `venue`, times, `ai_assembly` and `audio_source` reach the package; C68 A1 | VERIFIED | Effect confirmed: those are the metadata keys on all five packages. The code description is imprecise. `:80-86` also tries `track_or_program`, `panelists`, `moderator`, `host`, `roster` and `expected_participant_count`, but `sessions.json` uses `track`, `speakers`, `description` and `session_format`, so nothing matches. That name mismatch is part of A1's cause and worth one line in the fix. |
| T3 | The reflection-as-audio text is wrong throughout; no code parses `__reflection__` | VERIFIED | Repo-wide grep (runtime and personas, excluding venv) finds no `__reflection__` and no `recording_type` in any code or prompt. That settles the document's open "keep `recording_type` only if Cleaning branches on it": remove it. Missed: reflection-as-audio text at lines 280 (phone-quality WER) and 355 (walking-reflection Speaker ID accuracy). Line 531 is now 533 (C67 added two lines). |
| T4 | Step 1 Storage and Trigger are Drive-era, and stale for audio too | VERIFIED | Lines 88–114 and 163–185 as stated. Missed: "Pre-conference setup" (115–151). Its `/metadata/sessions.json` example uses `session_title`, `session_description` and `roster`, which is the translated `session.json` shape, not `reference/sessions.json` (`title`, `description`, `speakers`). That is exactly the confusion behind A1. Line 191ff also puts normalization in "a Prefect task"; it is ingest's ffmpeg step (`pipeline.py:299`). |
| T-repl | The reflections subsection and its two commands | VERIFIED | Both CLIs exist as written. `vendor_intake.py` needs PROJECT_ROOT, and `code/.env` sets no `AI_ASSEMBLY_PROJECT_ROOT`, so add `--project <PROJECT_ROOT>` to step 2. Minor: `language` stays `language`; only the participant id and duration become `_vendor_*`. |
| L1 | The status line is stale | VERIFIED | Line 5. |
| L2 | Since C26, ingest only normalizes and the orchestrator dispatches transcription | VERIFIED | `pipeline.py:1-12, 415-450` (no `_launch_stage0`); orchestrator `fire_pending_transcriptions`, concurrency 4, 60 s poll. Since C67, the Stage 2 text should also mention the `status.json` `"warnings"` field (Speaker ID auto-passthrough), the dashboard badge, and the orchestrator's warning line at Researcher dispatch. |
| L3 | "Done" is read via `infer_state`; a dead PID counts as an error and halts the orchestrator | VERIFIED | `pipeline.py:222-280`; `transcription_state` → `failed:transcription`. |
| L4 | The validation gate is missing; "operator's role: none" is wrong | VERIFIED | `validation_gate_state` and the `awaiting_validation_clearance` state; STATE lines 71, 92 and 109 give 6 / 8 / 7+1 flagged voices. |
| L5 | The orchestrator passes only `--skip-step3`; stale Voice notes | VERIFIED | Orchestrator Stage 3; `voice_flow.py:703-704` marks `--skip-validation` a deprecated no-op. |
| L6 | The publish sentinel is `traces/publish_manifest_night_<N>.json`, not `nights/_index.json` | VERIFIED | The orchestrator's comment and code; `publish_flow.py:1134-1139`; voice_flow writes the per-night index (`:555-570`). See Problems: Athens has no `traces/` at all. |
| L7 | §4 layout gaps; `dossier_<NNN>` | VERIFIED | As listed. |
| L8 | Self-contradiction in §5; a fourth thread (editor `prior_editions`) is missing | VERIFIED | `publish.py:61-99`; orchestrator `--prior-nights`. |
| L8-repl | "The only cross-night reads are selection.json, continuity overlays, published dossiers" | WRONG | The Step 2 validator's cross-night-echo pillar reads the prior night's published voice page, `published_artifacts/nights/night_<N-1>/<slug>.json` (`step2_validation.py:379-403`, used at `:432-446`, Nights 2–3). Add it, or drop "only". |
| L9 | The VM was never provisioned; Voice timing, the editor note and editor cost are stale | VERIFIED | `docs/README.md:20`; STATE lines 67–68 (12:00–12:26) and 163–166. |
| L9-repl | "Night 1 used the orchestrator" | DOUBTFUL | `runs/athens_night_1/` has no `_orchestrator_logs/`, which the orchestrator writes on every poll (`write_status`) and every stage fire. Night 2 has one: a single `status.json` stuck at "transcription 2/12 done", 2026-05-09T09:03Z, i.e. one aborted start. STATE never says Night 1 used it. |
| L10 | `council_config.json` is at the project root, not under `reference/`; Provocateur reads the profiles via council_config | VERIFIED | `io.py:292-294`; athens-2026 root listing. `provocateur_flow.py` never reads `06_derive` (grep; `load_council_config()` at `:1478`). That upgrades the document's PLAUSIBLE. |
| L11 | Continuity names are off by one | VERIFIED | `voice/card_assembly.py:170, 192`; `continuity.py:133, 140`; plato has only `_night_2` and `_night_3`. |
| L12 | `Restart=on-failure` restarts on exits 1 and 2, contradicting the unit's comment | VERIFIED | `orchestrator@.service:22-25, 43-44`, read. Systemd semantics are as stated. Not run. |
| L13 | Researcher and Provocateur lack `--project`; `--skip-validation` is a no-op; editor reruns aren't idempotent; `reset_run.py` should be pointed to | VERIFIED | Argparse in `researcher_flow.py:855-859` and `provocateur_flow.py:1795-1810`. |
| L13-repl | "Researcher and Provocateur resolve PROJECT_ROOT from the env; R/P/V checkpoint, so a rerun resumes" | DOUBTFUL | `researcher_flow.py` never touches PROJECT_ROOT (no `project_root`, `reference/` or `sessions.json` in the file); it reads only the run_dir. Only Provocateur uses the env (`:260-261, 1478`). The checkpointing sentence is carried over from the old spec; the document says it did not trace those flows. |
| L14 | §8 session counts and the Voice, Researcher and Editor rows | VERIFIED | `sessions.json`: 32 `ai_assembly` sessions, 12/12/8; 5 vendor (3/1/1); 7 `__audio*` duplicates. The Voice spec gives ~$23–25; the Researcher spec says $15–25 (`:638`). |
| L15 | Test counts: 9 and 22 are correct | STALE | `02006f5` added `test_researcher_dispatch_flags_sessions_with_warnings`, so `test_orchestrator.py` now has **23** tests. §9 line 467 ("22 trigger-path tests") needs updating. The count of 9 still holds. |
| N1 | The orchestrator's gate and the editor's gate disagree | VERIFIED | `validation_gate_state` opens with no `step2_validation/` directory; `gating_status` needs a PASS verdict or a decision; editor exit 3 → `failed:editor` → HALT. Refinement: a pillar API error still writes a file with a WARN verdict (`step2_validation.py:457-464, 487`), so a missing file only arises when `run_step2_validation` itself raises (`voice_flow.py:481-485`). `--skip-step2-validation` is the realistic trigger. |
| N2 | Refusal substring match runs before `primary_theme_id` | VERIFIED | `routing.py:69-75, 467`; `refusals[]` was empty on all three nights. |
| N3 | Tim's deployment block ignores `--project` | VERIFIED; still open after C67 | C67 #10 threaded `project_root` into `route_themes` and `generate_dossier` only. `editor_flow.py:178` still calls `assemble_system_prompt(card, night=night)`, and `_try_load_deployment_sources` still calls the env-resolving loaders (`io.py:292-294, 379-381`). Worse case, not stated: with `--project` A and `AI_ASSEMBLY_PROJECT_ROOT` = B in the shell, Tim silently gets **B's** conference facts and panel. |
| N4 | The Night 1–3 limits are likely under C52 | PLAUSIBLE | C52 covers the "3-night ceiling" but names only `voice/card_assembly.py`, `DAY_TO_RUN` and similar. It doesn't list these four sites (`editor_flow.py:326`, editor `card_assembly.py:308`, `voice_flow.py:697`, orchestrator `DATE_TO_NIGHT` and `--night` choices). Add them to C52 rather than filing separately. |
| N5 | Same as L12 | VERIFIED | As L12. |
| N6 | Editor output headroom | PLAUSIBLE | 24,401 / 32,000 confirmed; the rest is judgment. |
| §6 | The docs/README trust ratings | PLAUSIBLE | Sensible, and consistent with the findings. |

**Counts:** 45 VERIFIED · 6 PLAUSIBLE · 4 DOUBTFUL (E7-repl, F1-hl, L9-repl, L13-repl) · 1 WRONG (L8-repl) · 1 STALE (L15).

## Problems with the document

- **Replacement text isn't paste-ready.** The diagnoses are sound, but six blocks need a pass first:
  - L8: wrong.
  - L9 and L13: doubtful.
  - E7: incomplete (the most consequential, since it is an operator procedure).
  - E14: imprecise.
  - T-repl: add `--project` to step 2.
- **It reasons from `4e61444` and says so.** C67 has since shifted the line numbers (see the Verdict note) and added one test (L15). It never names the C67 changes that its Lifecycle replacements should now absorb: the `status.json` `"warnings"` field, the dashboard badge, and the orchestrator's warning line (L2, L3). It also doesn't cover the §6 failure-mode row "One session transcription errors", which C49 plus C67 changed from halt to degrade-and-flag.
- **Scope seam.** It rightly skips the already-fixed Stage 6 section. But once L9 corrects §8, Stage 6's own "Cost: ~$1-2 across one night" and its "Fired by: orchestrator" line (no dashboard trigger) will contradict it. Flag them for the same edit.
- **Missed spec text** (Transcription): Pre-conference setup (115–151, the source of the A1 key confusion), the "Prefect task" normalization (191ff), and reflection-as-audio at lines 280 and 355.
- **Unexamined Athens data.** athens-2026 has no `published_artifacts/traces/`, `extractions/` or `voices/`, on disk or anywhere in its git history. So the orchestrator's publish sentinel, and Publish's run record, never existed at Athens. L6 is right about the code. But the Lifecycle's Stage 7 write list (which the document says it did not trace) and the "End state" replacement describe files the Athens record doesn't have. It needs one line, or a check of whether `publish_flow` ever completed at Athens.
- **Upgradable evidence.** Four PLAUSIBLEs are now verified: the four other synthesis voices (E1), the E10 cause, the Provocateur profile path (L10), and the reflection-parsing search (T3, now repo-wide).
- **Rule compliance:** no breach seen. Evidence reads in athens-2026 were read-only, and the cost script prices stored metadata offline (my reproduction matches it exactly). Everything it adds beyond the brief is labelled as such: E8, T4, §5.

## Questions for the originating session

1. **L9: what was the source for "Night 1 used the orchestrator"?**
   - Why it matters: `athens_night_1` has no `_orchestrator_logs/`, and the replacement would write this into the Lifecycle as history.
   - If there is no source, the row should say all three nights were fired by hand (Night 2 shows one aborted orchestrator start).
2. **E7: did you read `edition.py` and `publish_flow.py`'s use of `primary_dossier` and `n_engaged_voices`? Was leaving them out of the override procedure deliberate?**
   - Why it matters: the procedure is an operator runbook step, and those fields drive the night index and the lead pick.
   - If the omission wasn't deliberate, the replacement gains two steps (update `primary_dossier`; recompute `n_engaged_voices`). If you believe something recomputes them, name it.
3. **E3 vs N2: should the Stage 1 algorithm block document the current order (refusal substring check before `primary_theme_id`), or the order you'd fix it to?**
   - Why it matters: if N2 is filed and fixed, the E3 block goes stale at once.
   - The answer decides whether the spec edit waits for the N2 decision.
4. **F1: what did you base "per-voice torque survives via Tim's `translation_protocol`" on?**
   - Why it matters: the card field carries no per-voice or headline content.
   - If it rests only on the prompt wording, the Frame Concept status block should say per-voice headline poetics were not carried over, rather than that they "survive".
5. **§5: which of N1, N2, N3 and N5 would you file now, and which only when a VM or non-Athens run exists?**
   - Why it matters: the document gives no priority, and N3 is the one C67 didn't touch.
   - The answer sets the filing order in runtime OPEN_ITEMS; N4 goes into C52.

## Operator decisions it asks for

1. **`docs/README.md` trust ratings.**
   - Editor: stays "Current with caveat", with reworded notes.
   - Lifecycle: "Current" → **"Partly stale"**.
   - Transcription: keep "Current with caveat", but widen the caveat to say Step 1 Ingest is stale.
   - Frame Concept: "Not re-checked" → **"Historical concept (pre-Athens)"**, optionally moved to a "Design / concept" group.
   - Line 7 ("Last full check against code: 2026-09-28") gets a qualifier pointing to this review.
2. **Whether to file the §5 code issues** (N1, N2, N3, N5; N4 under C52). No recommendation beyond fix directions:
   - N1: one shared gate function used by both the orchestrator and the editor.
   - N5: `RestartPreventExitStatus=1 2` or `Restart=on-abnormal`, plus a corrected comment. Only matters once a VM exists (B10).
3. **Frame Concept.** A status block plus inline notes, not a rewrite. Re-scope OPEN_ITEMS E5: mark the Broadsheet, Edition-Pipeline, Headline-Poetics and Substack docs moot (B3, B4, B9).
4. **Transcription spec.** Replace Step 1 Storage and Trigger with a pointer to the Lifecycle doc, and replace the reflection text with a vendor-JSON subsection. Recommended as written, with my T3/T4 additions.
5. **Lifecycle.** Add a "Stage 5.5 — Operator review gate (C28b)" section, and move `council_config.json` to the project root in §4. Recommended as written.
