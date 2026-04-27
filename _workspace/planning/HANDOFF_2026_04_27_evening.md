# Handoff — 2026-04-27 evening

**Supersedes for next-session pickup:** `HANDOFF_2026_04_27.md` (morning). That doc covered Tasks A–H consolidation. This doc carries forward what happened in the afternoon/evening.

**Code repo:** `mp13131313/ai-assembly`, branch `main` HEAD `9566c37` (pushed). PR #2 merged & closed earlier today. ~146 commits ahead of pre-session baseline.

**Athens-2026 data repo:** `mp13131313/ai-assembly-athens2026-voices` (PRIVATE) HEAD `dabaf03` (pushed). 11 commits this session.

**Tests:** 212/212 passing.

---

## TL;DR

Cleopatra pipeline currently **running in background** (~46 min in, currently in Pass 7a-FIX → re-firing Pass 7-pre post-fix). Do not interrupt unless it stalls > 30 min on a single pass. Octopus is at end of Phase 0.5 — manual claude.ai DR sessions (6 per voice) is the operator wall-time blocker.

The 4.6-vs-4.7 per-section DR-comparison heuristic is now N=3 (Plato + Cleopatra + Octopus). Reliable cross-voice signals: §4 = 4.7, §6 = 4.7. §1/§2/§5 vary by voice.

---

## 1. State at this moment

### Code repo commits this session (in chronological order)

| Hash | What landed |
|---|---|
| `547122e` | Pipeline v4 + Card v2.1 + planning consolidation (Tasks A–G) |
| `fa6cfe6` | LLM_CALL_INVENTORY rewrite for v4 |
| `989ba45` | Merge `arch-03-additive-merge` → `main` |
| `662bbb3` | FU#49L non-human variant + Position-B naming refinement |
| `ad214aa` | Wrong-folder safety harness (project_root.py banner + production warning) + batch wrapper script (`scripts/run_pipeline_batch.sh`) |
| `f9bd9cb` | ONBOARDING update for batch + safety harness |
| `b4a191b` | Pass 0a prompt tightened with canonical voice_mode definitions per Card v2 spec (operator-flagged that pre-tighten review_docs used cognitive-style framing rather than "extrapolating-from-practice" methodological framing) |
| `9566c37` | ONBOARDING update: Athens needs runtime pipeline ready, not just cards (operator priority addition; saved to memory as `project_athens_runtime_priority.md`) |

### Athens-2026 commits this session

| Hash | What landed |
|---|---|
| `931213b` | voices/ibn_battuta tailor re-run against canonical narratival voice_mode (audit-miss fix from morning) |
| `581729e` | voices/plato + peter_thiel Phase 0.5 re-run to fix truncated Perplexity dossiers |
| `7d13d12` | remove `voices_batch.txt` |
| `d605b1f` | archive: move first-run voice generation to `archive/first_run/` |
| `e4da589` | voices/cleopatra Pass 0a (redo against tightened prompt) |
| `9b8d526` | voices/cleopatra Phase 0.5 outputs |
| `ef352d4` | voices/cleopatra: per-section DR dossiers routed (§1/§2/§5 = 4.6, §3/§4/§6 = 4.7) |
| `dabaf03` | voices/octopus Pass 0a (redo, tightened prompt) + manual_grounding rewritten (curator-written option G, embodiment-first ~364 words) + editorial_rationale filled (~145 words) + Phase 0.5 outputs |

### Cleopatra pipeline IN-PROGRESS (background)

- **PID alive** as of last check (~16:32). Log: `/tmp/cleopatra_pipeline.log`.
- **Sequence completed**: Pass 1.1–1.7 chunked merge ✓ → Pass 1c-extract/fetch (49 sources, 8.3M chars) ✓ → Pass 2 ✓ (after 1× JSON-decode retry, 389s) → CT ✓ → Pass 3 ✓ (427s) → CT ✓ → Pass 1d ✓ (194s; **voice_basis="corpus-based"**, 9 curated selections, 68440 chars) → Pass 4a ✓ (186s) → CT ✓ → Pass 4b ✓ → CT ✓ → Pass 5 ✓ → Pass 6 ✓ → Pass 6.5-clean ✓ (stripped 27 inline tags) → Pass 7-pre ✓ → Pass 7-anachronism ✓ → Pass 7a ✓ → **Pass 7a-FIX** (FU#13 linear patcher) running on 19 field issues across passes 2/3/4a/5/6 → re-firing Pass 7-pre post-fix as of 16:32:00.
- **Remaining sequence**: re-fire Pass 7-anach + Pass 7a once → Pass 7b → Pass 7c → Derive → Card Assembly → CARD COMPLETE.
- **ETA**: ~15-30 min more wall time depending on luck.
- **Outputs already on disk** (uncommitted, partial): `voices/cleopatra/02_merge/` (chunked merge complete), `03_corpus/` (primary texts + reviewed flag), `04_generation/` (passes 2-6 + CT files; partial).

### Octopus state

- Pass 0a + Phase 0.5 complete. Voice config canonical with new manual_grounding (option G, embodiment-first composite, ~364 words, no philosophy-of-mind contamination) + editorial_rationale filled (~145 words, biological-proof-of-concept-for-distributed-intelligence framing).
- **Awaiting**: 6 manual claude.ai DR sessions (operator wall time). §1–§5 use Opus 4.6, §6 uses Opus 4.7.

### Octopus old-DR comparison done (this evening)

Operator already ran Octopus DR sessions earlier on the OLD prompts (4.6 + 4.7 versions). Per-section comparison done:

| § | Verdict | Reasoning |
|---|---|---|
| §1 | **4.7** | Broader taxonomic coverage (Cirrina/Incirrina, Argonauta, Vulcanoctopus, Casper, Hapalochlaena TTX); more recent papers (Birch 2021, Birk 2023, Schnell 2025, Whitelaw 2025); explicit `[~uncertain]` discipline |
| §2 | **4.7** | Lettered structure; "live scientific debates" explicit; "what architecture rules out, leaves open, supports" |
| §3 | **4.7** (marginal) | Lettered cleaner; both comparable on relational coverage |
| §4 | **4.7** | Architectural setup ("constitutively double" voice register); "register is action-based, not agentic"; "swap test catches" |
| §5 | **4.7** (narrow) | Both cover similar topical ground; 4.7's "thin record honestly described" + structural-asymmetry framing |
| §6 | **4.7** | Explicit "Critical errata catalogued for downstream merge" — high value for Pass 1.6 evidence_tag |

**Final pick: 4.7 across all 6 sections.** Octopus follows the **Plato pattern**, not Cleopatra pattern.

**NOT YET ROUTED** — operator hasn't said go. Files live at `~/Desktop/Claude DR dossiers/Octopus/4.{6,7}octopus{1-6}.md`. To route: copy 4.7 versions into `voices/octopus/01_research/04_dr_dossier/0N_section_N.md`. Total: ~37,100 words / ~275,800 chars.

### Cleopatra Pass 0a + Pass 0b tightening / archive issue

Working tree on athens-2026 has untracked:
- `voices/cleopatra/00_intake/02_voice_config.PRE_PROMPT_TIGHTEN.json` — pre-tighten Cleopatra Pass 0a snapshot (audit trail, not yet committed)
- `voices/cleopatra/00_intake/03_review_doc.PRE_PROMPT_TIGHTEN.md` — same

Plus `archive/first_run/voices/cleopatra/01_research/03_dr_prompts/08_section_6_dr_prompt.md` shows as modified — likely an artifact of an earlier `sed` command in this session. Worth checking with `git diff` before reverting/committing.

These are minor cleanup items; can be handled in next session.

---

## 2. Cross-voice 4.6/4.7 picking heuristic (N=3 calibrated)

| Pattern | Voices | §1 | §2 | §3 | §4 | §5 | §6 |
|---|---|---|---|---|---|---|---|
| Plato (rich Continental reception) | Plato | 4.7 | 4.7 | 4.6 | 4.7 | 4.7 | 4.7 |
| Cleopatra (Anglophone-dominant + 4.7 structural failure on §1/§2) | Cleopatra | 4.6* | 4.6* | 4.7 | 4.7 | 4.6 | 4.7 |
| Octopus (technical-empirical, recent literature) | Octopus | 4.7 | 4.7 | 4.7 | 4.7 | 4.7 | 4.7 |

\* Cleopatra §1/§2 4.6 forced by 4.7 truncation (900 words / 414 words — operator-side claude.ai session collapse, not substantive failure)

### Reliable cross-voice signals (N=3)

- **§4 = 4.7 default.** Confirmed across all 3 voices.
- **§6 = 4.7 default.** Confirmed across all 3 voices.

### Predictions for upcoming voices (do not generalize blindly)

- **Likely Plato/Octopus pattern (4.7 all)**: Hannah Arendt (rich Continental reception), Dostoevsky (Bakhtin/Frank), Whanganui (technical indigenous-law literature)
- **Likely Cleopatra pattern (4.6 in §1/§2/§5)**: Ada Lovelace (Anglophone), Bob Marley (Anglophone), Audrey Tang (Anglophone), Peter Thiel (Anglophone), Ibn Battuta (mixed but Anglophone-dominant), Scheherazade (mixed)
- **Always check 4.7 §1/§2 for truncation/collapse before defaulting**

---

## 3. Operational state at session end

### Code repo `main` (HEAD `9566c37`)

- All v4 docs current. Pipeline v4 spec, Card v2.1, CURRENT_STATE.md, top README, docs/README, ONBOARDING.md, personas/README.md, personas/HANDOFF.md, code/CLAUDE.md, LLM_CALL_INVENTORY.md all rewritten this session.
- Wrong-folder safety harness landed: `flows/shared/project_root.py` prints PROJECT_ROOT + SOURCE banner; warns when production target reached via env-var fallback.
- Batch wrapper landed: `scripts/run_pipeline_batch.sh` for batching multiple voices' full pipeline runs (refuses env-var fallback).
- Pass 0a prompt tightened with canonical voice_mode framings (operator-side QA caught the pre-tighten cognitive-style framing).
- ONBOARDING.md carries operator priority directive: Athens needs full runtime stack, not just cards.

### Athens-2026 (HEAD `dabaf03`)

- 4 deployment-context JSONs current (conference_facts, audience_profile, panel_roster, council_config).
- First-run voice work archived to `archive/first_run/`.
- Cleopatra: voice_config canonical, Phase 0.5 done, 6 DR dossiers routed (mixed 4.6/4.7), pipeline running.
- Octopus: voice_config canonical with curator-written manual_grounding + editorial_rationale, Phase 0.5 done, 6 DR dossiers ready to route (4.7 all) but routing pending operator confirmation.
- 10 voices remaining (Ibn Battuta, Scheherazade, Ada Lovelace, Dostoevsky, Hannah Arendt, Bob Marley, Audrey Tang, Peter Thiel, Whanganui River, Plato — though Plato is shipped under phase-l-plato; athens-2026 Plato build is open question).

### Memory updates

- `project_athens_runtime_priority.md` saved (operator priority: runtime equally critical to cards).
- `MEMORY.md` index updated.

---

## 4. What's next (per priority)

### Immediate

1. **Wait for Cleopatra pipeline to finish.** Likely ~15–30 min more. Monitor `/tmp/cleopatra_pipeline.log`. If it errors or hangs > 30 min on a single pass, investigate. When CARD COMPLETE summary appears, commit `voices/cleopatra/02_merge/` through `07_persona_card_assembled.json` to athens-2026.

2. **Chat-test Cleopatra.** Paste `voices/cleopatra/06_derive/03_chat_system_prompt.json` into a Claude project. Probe with Athens-relevant questions. Especially watch for hostile-source navigation (does she read Plutarch/Dio against the grain?) and Position-B self-cross-examination (does she engage corpus-internal contestation per FU#49D?).

3. **Route Octopus DR dossiers.** Operator says go → I copy `~/Desktop/Claude DR dossiers/Octopus/4.7octopus{1-6}.md` into `voices/octopus/01_research/04_dr_dossier/0N_section_N.md`. Then run pipeline.

### Near-term operator gates (parallel to next code session)

4. **Manual claude.ai DR sessions** for remaining 9 voices: 9 × 6 = 54 sessions. §1–§5 Opus 4.6, §6 Opus 4.7. Save each as `voices/<slug>/01_research/04_dr_dossier/0N_section_N.md`.

5. **For each voice as DR data lands**: run `scripts/run_pipeline_batch.sh --project ../../projects/athens-2026 [--parallel 3] "<Voice>"`.

### Build-side options not blocked by DR sessions

6. **LLM-as-judge + sampling-and-selection (criteria 6+7) with gpt-5.4 high ladder** — pilot on Plato baseline first. Deferred per "run Cleopatra first, get signal" decision (this session).

7. **Voice Pipeline Step 3 specification (FU#49E)** — currently UNSPECIFIED, reviewer-flagged as conceptually load-bearing for the deliberative-character claim. Spec writing is design work, ~2-3 days.

8. **Voice Pipeline Steps 1+2 build** — runtime infrastructure that consumes persona cards. ~1 week focused. Highest single Athens blocker after voice cards complete.

9. **Cleanup candidates** (low priority): delete orphaned legacy Pass 7-pre prompts (`persona_pass_7pre_citation.md`/_user.md), promote hardcoded paths to `paths.py`, FU#50(1) Pydantic enforcement post-Athens.

### Operator-side, non-build

10. **FU#49G Greek-scholar calibration** — Quarch/Tsinorema/Erinakis on Plato with provotype-test question.
11. **Editorial rationale fill-in** for review_docs that still have `null` (optional; tailor accepts null).

---

## 5. DON'Ts (carry from previous handoff)

- No Plato re-run without explicit ask. Card shipped per chat-test 2026-04-26 (operator authorized one re-run today for Phase 0.5 truncation fix in athens-2026 only; phase-l-plato shipped card untouched).
- No Dostoevsky full re-run.
- No deletion of athens-2026 contents without explicit operator confirmation per item.
- No `--no-verify` / hook bypass.
- No push to `origin/main` without explicit operator confirmation. (PR #2 already closed; current main is canonical.)
- No Opus 4.6 for §6 of any voice's DR.
- No xattr / ACL / system-attribute modification without explicit operator instruction.
- No commits with `--allow-empty`.
- No real-person names in the 4 deployment-context JSONs.
- No hand-authoring voice_configs bypassing Pass 0a.
- Voices 3–12 should NOT need manual chat-artifact curation.
- Never optimize FOR chat-test — Voice Pipeline (runtime) is the production target.
- **NEW (this session): never skip Pass 0a operator-review step.** Pass 0a writes review_doc; operator MUST review before Phase 0.5. (Operator caught this skip at start of Octopus run today.)
- **NEW: always pass `--project` explicitly for production runs (athens-2026).** Env-var fallback exists but defaults to `projects/test`. Use `scripts/run_pipeline_batch.sh` for batches (refuses env-var fallback).

---

## 6. Calibration carried forward

- Operator preference is direct. When pushed back, re-investigate.
- Provotype framing is load-bearing.
- **Athens needs full runtime stack ready, not just cards.** (Operator priority codified this session — see ONBOARDING.md + memory.)
- Voice Pipeline first, chat-test as instrument.
- Model/effort economy: per-voice pipeline operation + chat-test paste-and-assess is Sonnet-shaped.
- Reflections are vendor JSON, not audio.

---

## 7. Cumulative cost this session

Rough estimate (operator-paid):
- Pipeline v4 docs + LLM_CALL_INVENTORY rewrite: ~$5
- Cleopatra Pass 0a × 2 + Phase 0.5 + pipeline run (in progress): ~$28
- Octopus Pass 0a + Phase 0.5: ~$6
- Plato + Thiel Phase 0.5 re-runs: ~$10
- Battuta tailor re-run: ~$1
- FU#49L sentinel-regen on Plato (Pass 2 + Pass 5): ~$2
- **Total: ~$52** (excluding manual claude.ai DR session subscription cost)

---

## 8. Branch / repo state

| Repo | Branch | HEAD | Pushed | Notes |
|---|---|---|---|---|
| `mp13131313/ai-assembly` | `main` | `9566c37` | yes | clean tree; v4 era |
| `mp13131313/ai-assembly-athens2026-voices` | `main` | `dabaf03` | yes | working tree has in-progress Cleopatra pipeline outputs (uncommitted), 2 PRE_PROMPT_TIGHTEN snapshots (untracked), 1 archive file showing as modified (forensic) |

---

## 9. Closing notes

This was a long session. Major moves:
1. **Tasks A–G** (doc consolidation): pipeline v4 + Card v2.1 + CURRENT_STATE rewrite + safety harness + batch wrapper + ONBOARDING.
2. **Athens-2026 redo**: archive first run, refresh Cleopatra + Octopus from clean Pass 0a → Phase 0.5.
3. **Per-voice DR comparison** (Cleopatra + Octopus 4.6/4.7): heuristic now N=3 calibrated.
4. **Pipeline run** (Cleopatra): in flight.
5. **Operator priority**: runtime stack equally critical to cards (codified).

When picking up: read this doc + `_workspace/planning/HANDOFF_2026_04_27.md` (morning) for full session context. `FOLLOW_UPS.md` is current SoT for FU#1–50 family.

*End of HANDOFF_2026_04_27_evening.md.*
