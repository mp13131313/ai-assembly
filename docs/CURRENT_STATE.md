# AI Assembly — Current State

**Last updated:** 2026-04-27
**Purpose:** Gap analysis and project-state snapshot. What's built, what's specified-but-not-built, what's not-yet-specified, key decisions, known bugs, pre-Athens critical path. Complements the briefing docs (which describe the target state) and the pipeline specs (which describe individual components). This doc describes **what exists now** and **what's next**.

> When something lands, update this doc in the same commit. When the system drifts from the briefing, update the briefing and this doc together.

> **Major rewrite 2026-04-27.** Reflects Phase B per-voice folder layout (2026-04-21), arch-03 chunked merge architecture (2026-04-22), Tier 3 code/project separation (2026-04-20), and the FU#1–50 follow-up family (2026-04-22 through 2026-04-27). Pipeline-version string still `3.10` per code, but the pipeline implementation is materially v4 — see §5.16–5.23 and the v4 spec doc for the architectural shift.

---

## 0. Quick map

```
~/Desktop/AI Assembly/                  # umbrella (Tier 3, separating code from project data)
├── code/                               # THE GIT REPO — `mp13131313/ai-assembly`
│   ├── docs/                           # PRODUCTION specs + this file
│   │   ├── CURRENT_STATE.md            # you are here
│   │   ├── README.md                   # staleness banner for the spec set
│   │   ├── AI_Assembly_Briefing_v3_1.md
│   │   ├── AI_Assembly_Persona_Card_v2.md         # 35 generated + 2 continuity null
│   │   │                                            (+ v2.1 amendments section, 2026-04-27)
│   │   ├── AI_Assembly_Persona_Pipeline_v4.md     # current pipeline (2026-04-27)
│   │   ├── _archive/AI_Assembly_Persona_Pipeline_v3_10.md  # historical (2026-04-17 spec)
│   │   ├── AI_Assembly_Provocateur_Pipeline.md
│   │   ├── AI_Assembly_Researcher_Pipeline.md
│   │   ├── AI_Assembly_Transcription_Pipeline.md
│   │   ├── AI_Assembly_Voice_Pipeline.md          # Steps 1+2 only; Step 3 unspecified
│   │   ├── AUDIENCE_BRIEF.md
│   │   └── LLM_CALL_INVENTORY.md
│   ├── runtime/                        # PRODUCTION code: FastAPI ingest + Prefect flows
│   │   ├── ingest/                     # built, tested, deployable
│   │   ├── flows/
│   │   │   ├── transcription_flow.py   # built, validated 3 MSC sessions
│   │   │   ├── researcher_flow.py      # built, validated dev_msc_test
│   │   │   ├── provocateur_flow.py     # built, validated dev_msc_test
│   │   │   ├── voice_flow.py           # NOT BUILT
│   │   │   └── shared/council/         # council_config (dev_stub_v3_audience_sharpened)
│   │   ├── reference/                  # sessions.json, speakers.json
│   │   └── scripts/
│   ├── personas/                       # PRODUCTION code: Persona Pipeline (v4)
│   │   ├── run_pass0a_voice_config.py
│   │   ├── run_phase0_1_research.py
│   │   ├── run_pass_1_all.py           # arch-03 chunked merge driver (1.1–1.6)
│   │   ├── run_pass_1_7.py             # arch-03 coherence audit
│   │   ├── run_persona_pipeline.py     # main orchestrator (Pass 1c → Derive)
│   │   ├── flows/shared/               # prompts, schemas, clients, paths, etc.
│   │   ├── schemas/                    # Pydantic source-of-truth (chunk schemas + card)
│   │   ├── scripts/                    # batch_pre_dr.sh, sentinel_regen.py, migrators
│   │   ├── tests/                      # 212 tests, all passing 2026-04-27
│   │   └── HANDOFF.md                  # cross-repo contract (production, current)
│   ├── research/                       # PRESERVED Deep Research compass artifacts (5)
│   ├── _workspace/
│   │   ├── planning/                   # active: HANDOFF_2026_04_27, FOLLOW_UPS, ONBOARDING
│   │   ├── archive/                    # historical (planning_2026_04_consolidation/, specs/, fix-plans/)
│   │   ├── arch_03_baseline_snapshot/  # gitignored: Phase L pre/post snapshots
│   │   └── sentinel_baselines/         # gitignored: per-prompt-edit snapshots
│   ├── .env                            # shared secrets (gitignored at code/.env)
│   ├── README.md, CLAUDE.md
│   └── (other top-level files)
├── projects/                           # NEVER pushed — per-project data, sibling to code
│   ├── test/                           # sandbox / experimentation
│   ├── phase-l-plato/                  # Plato Phase L working project (carry-over source)
│   ├── phase-l-dostoevsky/             # Dostoevsky Phase L working project
│   └── athens-2026/                    # PRODUCTION — own git repo `mp13131313/ai-assembly-athens2026-voices` (private)
│       ├── conference_facts.json       # at root, NOT under inputs/
│       ├── audience_profile.json
│       ├── panel_roster.json
│       ├── reference/                  # runtime artifacts (sessions, speakers)
│       └── voices/<slug>/              # per-voice work — see §0.1
└── archive/                            # frozen historical runs — NEVER pushed
    └── runs/{personas,runtime}/        # v3.10 + dev_msc_test rehearsal artifacts
```

### 0.1 Per-voice folder layout (Phase B, since 2026-04-21)

Per voice under `<PROJECT_ROOT>/voices/<slug>/`:

```
voices/<slug>/
├── 00_intake/
│   ├── 01_non_human_grounding.md       # optional, for non-human voices
│   ├── 02_voice_config.json            # Pass 0a output (validated)
│   └── 03_review_doc.md                # Pass 0a operator-review surface
├── 01_research/
│   ├── 01_perplexity_dossier.json      # Pass 1a
│   ├── 02_gemini_broad_scan.json       # Pass 1b
│   ├── 03_dr_prompts/                  # 9 files: monolithic + base + tailoring_notes + 6 sections
│   └── 04_dr_dossier/
│       ├── 01_section_1.md ... 06_section_6.md   # operator's manual claude.ai DR outputs
├── 02_merge/
│   ├── pass_1_1/ ... pass_1_6/         # chunk JSONs (arch-03)
│   ├── 07_pass_1_7_coherence.json      # Pass 1.7 (narrow audit)
│   ├── 08_merged_dossier.json          # convenience snapshot rebuilt from chunks
│   └── _fix_log.json                   # FU#13 patcher log (if revisions ran)
├── 03_corpus/
│   ├── 00_primary_text_urls.json       # CC#1 — derived from chunks
│   ├── 01_primary_texts.json           # Pass 1c fetch
│   ├── 02_excerpt_selections.json      # Pass 1d
│   └── 03_primary_texts_reviewed.flag  # manual gate
├── 04_generation/                      # Pass 2/3/4a/4b/5/6 + CT compress files
├── 05_validation/                      # Pass 7-pre/7-anachronism/7a/7b/7c
├── 06_derive/
│   ├── 00_derive_raw.json
│   ├── 01_provocateur_profile.json     # Provocateur Pipeline consumer
│   ├── 02_evaluation_rubric.json       # 9 test prompts
│   └── 03_chat_system_prompt.json      # FU#41 chat artifact (Claude project paste-target)
└── 07_persona_card_assembled.json      # 35 fields + 2 continuity null + metadata block
```

---

## 1. What exists and is verified

### 1.1 Persona Pipeline (personas/) — PRODUCTION

**Status: production-ready for voices 3–12. End-to-end validated on Plato (2026-04-26).**

Plato shipped per chat-test 2026-04-26 → Phase L sign-off. Voice 3–12 buildout for athens-2026: 12 voice_configs authored via Pass 0a (Pass 0a now operator-trusted, no hand-authoring); Phase 0.5 research complete for all 12; pipeline-fidelity audit confirmed all voice_configs match Phase 0.5 research outputs.

Per-voice cost: ~$18–22, wall time ~2 hours (excluding manual claude.ai DR sessions which run human-in-the-loop on 6 sections per voice).

| Component | Status | Notes |
|---|---|---|
| Node 0 validation | ✓ | strict 3-enum voice_mode {philosophical, observational, narratival}, null permitted only for `subtype=system` |
| Pass 0a (voice_config + review_doc) | ✓ | Opus + adaptive thinking; operator-trusted — do NOT hand-author bypassing this |
| Phase 0.5 research | ✓ | Pass 1a (Perplexity sonar-deep-research) ‖ Pass 1b (Gemini); then Pass 0b base render (Jinja) + Pass 0b tailor (LLM splice — structured injections only); split into 6 per-section DR prompts |
| Manual claude.ai DR gate | — | 6 sessions per voice (sections 1–5 = Opus 4.6, section 6 = Opus 4.7 per Phase L finding); 60–180 min per session |
| Pass 1.1–1.6 chunked merge (arch-03) | ✓ | Replaced monolithic Pass 1-merge — see §5.18. 6 chunks: BIOGRAPHICAL, INTELLECTUAL, REASONING, VOICE, BOUNDARIES, CORPUS. Each emits Pydantic-validated structured output |
| Pass 1.7 coherence (arch-03) | ✓ | Narrow LLM audit — emits flags + resolutions + edits[]; Python applies edits to chunk files (chunks = source of truth) |
| Pass 1c-extract | ✓ | Deterministic regex URL extraction from `passages[].citation` + `works[]` (1-arch-07; CC#1 relocation) |
| Pass 1c fetch | ✓ | SSRF-hardened (scheme restriction, RFC1918 block, 5 MB cap) |
| Pass 1c review gate | ✓ | Manual: touch `03_primary_texts_reviewed.flag` |
| Pass 1d excerpt selection | ✓ | Opus + thinking; 60K char budget (FU#46 raised from 30K for richer-corpus voices) |
| Pass 2 Identity & Boundaries | ✓ | Opus + thinking; FU#49D Position B corpus-accurate softening landed in `hard_limits` field-spec preamble |
| Pass 3 Intellectual Core | ✓ | Opus + thinking |
| Pass 4a Voice (corpus-grounded) | ✓ | Opus + thinking |
| Pass 4b Artifact | ✓ | Sonnet; FU#49A generativity-permitting prompt + length variance 350–1500 |
| Pass 5 Engagement | ✓ | Opus + thinking; audience-primed via FU#12-B |
| Pass 6 Corpus Curation | ✓ | Sonnet; HALT if no primary texts |
| Coherence Threading | ✓ | Per-pass Sonnet compress after Passes 2/3/4a/4b |
| **Pass 6.5-clean (FU#33 P1)** | ✓ | Deterministic regex bracket-strip — preserves Boddice biocultural tags `[experiential_reconstruction]`, `[projection_warning:...]`; runs BEFORE validators so reports reflect shipped state |
| Pass 7-pre (FU#2 chunked) | ✓ | 3-stage: Stage 1 extract claims (1 Sonnet call) → Stage 2 verify N parallel batches (~25 claims each) → Stage 3 boddice tag check (parallel with Stage 2). Replaced single-shot which hit 128K output ceiling |
| Pass 7-anachronism | ✓ | gpt-5.4 high → fallbacks |
| Pass 7a Cross-Model | ✓ | gpt-5.4 high → fallbacks; merges Pass 7-anachronism + FU#33 P2 INCONSISTENT flags into `field_issues` |
| **Pass 7a-FIX (FU#13 linear patcher)** | ✓ | Replaces revision loop — Opus 4.7 + thinking; emits surgical JSON patches via path-walker; FU#44 register-drift + internal-contradiction patches; ~$1 per voice vs $5–10 per loop |
| Pass 7b Worked Provocations | ✓ | Opus + thinking; build-time diagnostic NOT runtime few-shot |
| Pass 7c Negative Constraints | ✓ | Gemini → Sonnet bias-aware fallback |
| Derive (Profile + Rubric) | ✓ | Opus + thinking |
| **FU#41 chat artifact** | ✓ | `flows/shared/chat_prompt_builder.py` — strips 11 fields (5 chat-incompatible + 5 spec-shell + 1 nested) |
| Card assembly | ✓ | 35 generated fields + metadata block + 2 continuity nulls |
| **Sentinel regen (FU#29/50(2))** | ✓ | `sentinel_regen.py` per-voice baseline subdir support; standard prompt-edit smoke-test workflow |

**Voices 3–12 state (athens-2026):**

| Voice | type/subtype/voice_mode/hostile/corpus | Phase 0.5 | DR sessions |
|---|---|---|---|
| Plato | human / – / philosophical / F / full | ✓ | ✓ (carry-over from phase-l-plato) |
| Cleopatra | human / – / observational / **T** / **hostile_read_against_grain** | ✓ (re-tailored) | – |
| Ibn Battuta | human / – / narratival / F / full | ✓ | – |
| Scheherazade | fictional / – / narratival / F / full | ✓ | – |
| Ada Lovelace | human / – / philosophical / F / full | ✓ | – |
| Fyodor Dostoevsky | human / – / narratival / F / full | ✓ | – |
| Hannah Arendt | human / – / philosophical / F / full | ✓ | – |
| Bob Marley | human / – / narratival / F / **lyrics_patterns_only** | ✓ | – |
| Audrey Tang | human / – / philosophical / F / full | ✓ | – |
| Peter Thiel | human / – / philosophical / F / full | ✓ | – |
| Whanganui River | non_human / system / **null** / T / full | ✓ (re-run) | – |
| Octopus | non_human / organism / observational / F / full | ✓ (serial after 429) | – |

### 1.2 Ingest app (runtime/ingest/) — PRODUCTION-READY

**Status: production-ready, tested, deployable.** No change since 2026-04-17 description.

| Component | Status | Notes |
|---|---|---|
| FastAPI routes (index, session detail, status, overview, upload, retry, health) | ✓ | All routes auth-gated except `/health` |
| HTTP Basic Auth | ✓ | `secrets.compare_digest`; IP-based rate limiting (10 fails/60s → 429) |
| Upload pipeline: receive → normalize → spawn transcription | ✓ | Atomic JSON writes, fcntl locking |
| Audio normalization | ✓ | ffmpeg → 96 kbps mono AAC; ffprobe validation (timeout=30s) |
| Status state machine | ✓ | received → normalizing → transcribing (substates) → done/error |
| Reconcile-on-startup | ✓ | Scans runs/ on app start, marks orphaned PIDs as error |
| Detached subprocess spawn | ✓ | `start_new_session=True`; survives uvicorn restart |
| Tests + deploy configs | ✓ | `test_app.py`, `test_pipeline.py`, `test_sessions.py`, `ingest.service`, `Caddyfile`, deploy README |

### 1.3 Transcription Pipeline (runtime/flows/transcription_flow.py)

**Status: built, validated on 3 MSC 2026 test sessions.** Unchanged since 2026-04-17.

### 1.4 Researcher Pipeline (runtime/flows/researcher_flow.py)

**Status: v3 built, validated on dev_msc_test (106 extractions → 25 clusters → 6 themes, 83% cross-session theme ratio).** Unchanged.

### 1.5 Provocateur Pipeline (runtime/flows/provocateur_flow.py)

**Status: v3 (5-stage) built, validated on dev_msc_test.** Unchanged.

---

## 2. Specified but not built

### 2.1 Voice Pipeline Steps 1 + 2 (runtime/flows/voice_flow.py)

**Spec:** `docs/AI_Assembly_Voice_Pipeline.md` (covers Steps 1+2 only).
**Status: not built.** (`runtime/flows/voice/` directory does not exist.)

**What Step 1 does:** Receive Provocateur briefing → load Persona Card as system prompt → produce one detailed response per formulation (~3 per voice).

**What Step 2 does:** Read back all detailed responses → make focus + stance decisions → produce one artifact per voice in the voice's natural medium.

**Key wiring decisions already made:**
- Load persona card fields as system prompt; DROP `metadata` and `smoke_test_chains` (build-time diagnostic, NOT runtime few-shot — see §5.10).
- Foundational fields (12) appear in both Step 1 and Step 2.
- Step 1 uses Reasoning + Engagement fields (9); Step 2 uses Voice + Artifact fields (15).
- **`reference_only_passages`** (FU#41-related) is loaded into Step 1 system prompt but MUST be dropped from Step 2 system prompt to avoid copyright exposure for musical/copyright-sensitive voices (see `personas/HANDOFF.md`).
- Runtime reads `<PROJECT_ROOT>/voices/<slug>/07_persona_card_assembled.json` directly.

### 2.2 Phase 5 Cross-Persona QC (personas)

**Spec:** Pipeline v4 (and v3.10) §"Phase 5 Cross-Persona Quality Control".
**Status:** Scaffolded but not run. `personas/phase_5_cross_persona_qc.py` exists (~487 lines) as scaffolding; needs all 12 athens-2026 cards complete before invocation.

Three batch tests:
1. **Swap test** — shuffle constitution principles, can an evaluator attribute each? Misattributed → too generic.
2. **Blind identification** — remove names from character + register_and_tone, shuffle, can evaluator identify?
3. **Same-question distinctiveness** — run all voices through one provocation, compare for style/metaphor/values similarity.

---

## 3. Not yet specified (and unbuilt)

### 3.1 Voice Pipeline Step 3 — Amendment

**Briefing v3.1 describes it:** after all 12 voices produce first-draft artifacts, each voice reads first-draft artifacts of OTHER voices it shares at least one theme with, and decides whether to amend its own. Amendments are visible (reference the other voice).

**Status: UNSPECIFIED.** FU#49E flagged this as the **highest-impact post-Athens item** during reviewer pass 2 (2026-04-26).

**Dependency order:** needs Voice Pipeline Steps 1+2 building first to have reference outputs, then spec Step 3 against those.

### 3.2 Closing-show pipelines (Day 3 afternoon)

Per Briefing v3.1: theme identification, per-theme mapping (Matrix A + B), video pipeline. **Not specified, not built.**

### 3.3 Downstream pipeline (per-night, runs after Voice Pipeline)

Render → Publish → Curate → Deliver. **Not built.** Newsletter style calibration is a separate workstream.

### 3.4 Microsite

**Not specified, not built.** Astro/Next.js + Vercel/Netlify + content repo + deep links per artifact.

### 3.5 Admin Console

**Not specified, not built.** Web UI to orchestrate all pipelines (transcription, researcher, provocateur, voice, downstream, persona card building, council sync, closing-show).

### 3.6 Night 2 / Night 3 plumbing

- **Provocateur** Night 1/2 exclusion filter — placeholder, not implemented.
- **Voice Pipeline** continuity block generation — not built (because Voice Pipeline isn't).
- **Researcher** processes fresh each night; no cross-night dependency.

### 3.7 Cross-repo tooling

- **Sync council config** — script that reads all `<PROJECT_ROOT>/voices/*/06_derive/01_provocateur_profile.json` and writes them into `runtime/flows/shared/council/council_config.json`. Currently manual. Easy Python script; natural first admin-console feature.

---

## 4. Cross-repo data contracts

### 4.1 Persona → Runtime (per voice)

**Provocateur Profile (8 fields):**
- File: `<PROJECT_ROOT>/voices/<slug>/06_derive/01_provocateur_profile.json`
- Consumer: `runtime/flows/shared/council/council_config.json#members[]`
- Fields: `name`, `speaks_from`, `core_commitment`, `activates_on`, `goes_flat_on`, `stretch`, `translation_range`, `stance_tendency`, `medium`
- Currently: council_config is **`dev_stub_v3_audience_sharpened`** — hand-written. Will be replaced as athens-2026 cards complete.

**Assembled Persona Card (35 generated + 2 continuity null + metadata):**
- File: `<PROJECT_ROOT>/voices/<slug>/07_persona_card_assembled.json`
- Consumer: `runtime/flows/voice_flow.py` (when built) — loads as system prompt
- Runtime MUST drop `metadata`, `smoke_test_chains`, `reference_only_passages` (Step 2 only) before assembling system prompt.
- 35 fields populate at build time; 2 null continuity fields populated at runtime on Night 2.

**Chat artifact (FU#41, 4th Derive output):**
- File: `<PROJECT_ROOT>/voices/<slug>/06_derive/03_chat_system_prompt.json`
- Consumer: operator paste-target for Claude project custom instructions
- 11 fields stripped from assembled card per Amendments A+B (chat-incompatible + spec-shell meta + 1 nested)
- NOT consumed by runtime pipelines — standalone for chat-test validation pre-ship and for chat-native deployments

**Evaluation Rubric (9 test prompts):**
- File: `<PROJECT_ROOT>/voices/<slug>/06_derive/02_evaluation_rubric.json`
- Consumer: Voice Pipeline testing harness (when built)

### 4.2 Transcription → Researcher

**Session package** at `runtime/runs/<run>/01_transcription/<session>/session_package.json`. Critical invariant: per-turn `confidence` flows through to Researcher (validated on 3 MSC test sessions). `review_queue.verify_markers` is actively consumed.

### 4.3 Researcher → Provocateur

`all_extractions.json` (flat) + `grouping.json` (themes → clusters → extraction_ids). Field-format conventions per dev_msc_test validation: namespaced extraction IDs (`"breaking_point:014"`), `lens` underscored (`"open_question"`), `engagement` ∈ {null, challenged, reinforced, unengaged}, `energy` ∈ {high, normal}.

### 4.4 Provocateur → Voice Pipeline

Per-voice briefing at `runtime/runs/<run>/03_provocateur/briefings/<voice_slug>.json`. Two-view per formulation: `narrative_briefing` (markdown, Step 1 user prompt) + `full_theme_record` (structured JSON, Step 1 private reasoning surface).

### 4.5 Ingest → Transcription

Schema translation from `sessions.json` to `session.json`: `title→session_title`, `description→session_description`, `date_time_start→date_time`, `venue+venue_sub→` concatenated (` · ` if both).

---

## 5. Architectural decisions & rationale

Decisions a new session/collaborator needs to know that aren't obvious from reading the code.

### 5.1 Separate venvs (runtime + personas)

Dependency isolation. Both currently pin `anthropic==0.94.1`.

### 5.2 Unified `.env` at monorepo root

Single source of truth. All loaders explicitly load from `_REPO_ROOT.parent / ".env"` (or bare `load_dotenv()` for `personas/flows/shared/clients.py`).

### 5.3 Output Register rule (v3.7)

Every field in first or second person; never third-person scholarly. Mock execution showed 10–15K tokens of third-person field content overwhelmed the ~80-token second-person epistemic frame. Enforced by Pass 7a register check + per-field register table in Card v2 spec.

### 5.4 KJ Round 1 minimal input (Researcher v2.4 → v3)

Round 1 sees only `{ref, extraction, context}`; namespace prefix as grouping shortcut was producing session-grouped clusters. Restored 4.08 extractions/cluster average and 83% cross-session ratio.

### 5.5 Python Selection (Provocateur v3)

Selection is combinatorial scoring, not editorial judgment. Python is instant, deterministic, all knobs tunable in council_config. Substance-aware work moved to per-pair Formulation.

### 5.6 Per-pair Formulation (Provocateur v3)

One formulation per theme forced generic altitude. Per-pair lets each formulation aim at one voice's specific territory.

### 5.7 Proposition Test with 5 conditions (Provocateur v3)

Explicit 5-condition test in prompt catches default-to-proposition drift.

### 5.8 Checkpoints-as-cache

Incremental writes of each LLM call to disk before return. Restart picks up from wherever it died. No `CACHE=1` env var.

### 5.9 Deterministic shuffle seed 42 (Researcher Round 1 + Round 2)

Fixed seed breaks session-ordering bias without losing reproducibility.

### 5.10 `smoke_test_chains` is build-time only, NOT runtime few-shot

**Decision date:** 2026-04-15. Documented in `personas/flows/shared/prompts/persona_pass_7b_smoke_test.md` and `personas/HANDOFF.md`. Few-shotting from 4 test chains would collapse the voice's range, re-introduce failures Pass 7c removed, propagate stale `conference_context`, and over-constrain a prompt already strong enough.

### 5.11 Pass 1a primary text URLs moved out of voice_config (b1868da → CC#1 2026-04-26)

Pass 0a has no internet access; URLs from training data risk hallucination/staleness. Now derived deterministically at render time from `passages[].citation` + `works[]` via `flows/shared/url_extract.py` (CC#1 1-arch-07; relocated from research/ to corpus/00_primary_text_urls.json).

### 5.12 `voice_mode` strict 3-value enum

{philosophical, observational, narratival}, with null permitted only for `subtype: "system"`. Enforced at `personas/flows/shared/node0_validation.py:60`. Brief relaxation to freeform in commit `b1868da` was reverted (`4c5c366`) — downstream prompt branching depends on the fixed enum; freeform broke prompt rendering.

**Watch-out:** This bit during voice 3–12 buildout — Cleopatra and Bob Marley needed voice_mode fixed before Phase 0.5 launched.

### 5.13 `needs_dr_supplement` hardcoded to True (b1868da)

DR supplement is cheap (~$0.10) and always adds depth. No reason to skip.

### 5.14 Prefect orchestration (not n8n)

Architecture_v1 originally specified "Prefect for audio, n8n for everything else" — in practice the whole pipeline is Prefect. Architecture_v1 archived as stale (2026-04-19).

### 5.15 FastAPI web upload (not rclone + Drive mount)

Producers upload at venue with mobile data; no Drive permissions to manage. Infrastructure_Setup archived as stale.

### 5.16 Phase B per-voice folder layout (2026-04-21)

Per-voice data moved from flat `inputs/voices/` + `runs/<slug>/` to `voices/<slug>/{00_intake, 01_research, 02_merge, 03_corpus, 04_generation, 05_validation, 06_derive}/`. Migrated by `personas/scripts/migrate_to_per_voice_layout.py`. Reason: clearer ownership per pipeline stage, easier per-voice deletion + resumability, better fits the manual claude.ai DR step (6 per-section files per voice instead of one monolithic dossier).

### 5.17 Tier 3 code/project separation (2026-04-20)

Per-project data lives **outside** the code repo at `PROJECT_ROOT`. Resolves via `--project <path>` > `AI_ASSEMBLY_PROJECT_ROOT` env > **hard fail** (no silent default). Multiple projects (test / phase-l-plato / phase-l-dostoevsky / athens-2026) share the same code, separate data. athens-2026 has its own git repo (`mp13131313/ai-assembly-athens2026-voices`, private) for backup; the code repo never touches per-project data.

### 5.18 Arch-03 additive-merge architecture (2026-04-22)

Pass 1-merge replaced with Pass 1.1–1.7 chunked merge. 6 chunks (BIOGRAPHICAL, INTELLECTUAL, REASONING, VOICE, BOUNDARIES, CORPUS) each emit Pydantic-validated structured output via `chunk_runner.run_chunk()`. Pass 1.7 coherence is a **narrow LLM audit** (not a re-merge): emits flags + resolutions + edits[]; Python applies edits to chunk files (chunks = SoT per 1-arch-05 Part B).

Sub-architecture decisions:
- **1-arch-04**: AnalyticalContext containers preserve scholarly-interpretive material previously dropped (structural_patterns, worked_demonstrations, scholarly_debates).
- **1-arch-05 Part A**: Pass 2–6 read per-chunk variables instead of `merged_dossier` blob (`_per_chunk_vars()` in `run_persona_pipeline.py`). **Part B**: chunks are source of truth; `08_merged_dossier.json` is convenience snapshot.
- **1-arch-06**: top-level `interpretive_frames[]` container at Pass 1.2 (frame_type discriminator: interpretive_method / cross_disciplinary_reframing / voice_level_debate). Cross-cuts chunk boundaries.
- **1-arch-07**: `urls` chunk removed; URL inventory derived deterministically at render time from `passages[].citation` + `works[]` via `flows/shared/url_extract.py`.
- **1-arch-08**: anachronism discipline consolidated at `KnowledgeBoundary.anachronism_discipline[]` (Pass 1.5) with dual framings per entry. Removed from `LifeScaffold.anachronisms_to_avoid`.

### 5.19 FU#33 P1 bracket-strip (Pass 6.5-clean, 2026-04-25)

After Pass 6, before Pass 7-pre, runs deterministic regex strip on `04_generation/*.json` files. Strips schema-taxonomy markers (`[ontological]`, `[stated]`, `[curator_note]`, etc.) but **preserves Boddice biocultural tags** (`[experiential_reconstruction]`, `[projection_warning:...]`) which Pass 7-pre's boddice check looks for. Placement before validators ensures their reports reflect shipped state.

### 5.20 FU#13 linear patcher replaces revision loop (2026-04-23)

Pass 7a + Pass 7-anachronism `field_issues` feed a single Sonnet/Opus patcher call (`run_persona_pipeline.py:_pass_7a_fix`) emitting surgical JSON patches via path-walker (`flows/shared/patch_walker.py`). Replaced FU#3 surgical revision loop, which over-corrected (writer Opus + thinking + critique tends to expand rather than trim). FU#5 pre-fix snapshot dirs preserve pre-patch state. Cost: ~$1 vs ~$5–10 per loop. FU#44 added register-drift + internal-contradiction patch types.

### 5.21 FU#41 chat artifact (4th Derive output, 2026-04-24, amended 2x)

After CARD COMPLETE, `flows/shared/chat_prompt_builder.py` writes `06_derive/03_chat_system_prompt.json` — assembled card with 11 fields stripped (5 chat-incompatible per Amendment A: `metadata`, `smoke_test_chains`, `reference_only_passages`, 2 continuity blocks; 5 spec-shell meta per Amendment B: `voice_name`, `voice_mode`, `pipeline_version`, `generated_date`, `council_member_name`; 1 nested: `curated_corpus_passages.corpus_metadata`). Operator paste-target for Claude project custom instructions.

### 5.22 FU#2 chunked Pass 7-pre (2026-04-24)

Replaces single-shot Pass 7-pre (which hit Sonnet 4.6's 128K output ceiling on rich cards). 3-stage architecture in `flows/shared/pass_7pre_chunked.py`: Stage 1 extract claims (1 Sonnet call), Stage 2 verify N parallel batches (~25 claims each), Stage 3 boddice tag check (parallel with Stage 2). Aggregation pure Python.

### 5.23 FU#49 family — fidelity-generativity gap (2026-04-26/27)

Reviewer-flagged structural issue: Step 1 (private reasoning) had anti-polish teeth; Step 2 (artifact) didn't. Result: thinking layer produced genuine novelty; synthesis layer reliably softened or dropped those moves.

**Landed (universal patterns in 4 prompt files: Pass 2 + Pass 4a + Pass 4b + Pass 5):**
- **49A**: Pass 4b prompt updates (generativity criterion + preserve-trace-tensions + length variance 350–1500).
- **49C**: `conference_facts.json` `session_role_for_ai_assembly` rewrite (removed "breakfast reading" frame; added 3-bar test + framework-strain directive).
- **49D**: Position B corpus-accurate softening — `hard_limits` field-spec preamble forbids framework-ABANDONMENT, NOT corpus-internal CROSS-EXAMINATION (e.g. Plato's Parmenides cross-examining the Forms is permitted; denying the Forms exist is not). Sentinel-validated on Plato.
- **49H**: structural-strain licensing in `epistemic_frame_statement`.
- **49I**: two-aporia distinction in `translation_protocol`.
- **49J**: phenomena-outside-corpus universal entry in `topics_requiring_care`.
- **49K**: 5 fidelity + 2 generativity quality_criteria + don't-silently-complete-incomplete-translation entry in `banned_modes`.

**Universal-pattern principle:** voice-specific corpus self-criticism moves emerge from the corpus at generation time. Voices 3–12 generate their own voice-specific content following the universal instruction in the prompt; the Plato text is the worked example, not the prescription.

**Deferred post-Athens:**
- **49B** Step 2 generativity teeth (runtime workstream)
- **49E** Step 3 specification (currently UNSPECIFIED — reviewer flagged as highest-impact)
- **49F** per-voice framework-strain log on micro-site
- **49G** Greek-scholar calibration (operator outreach: Quarch / Tsinorema / Erinakis on Plato with the **provotype-test** question, not the pastiche-test)

### 5.24 Position B vs Position C (2026-04-27)

**Position B** = corpus-accurate softening (permit corpus-internal self-criticism). **Position C** = framework-lifting (permit denying core commitments). The Athens panel format is **Position B only** — voices speak FROM their frameworks, not against them. FU#49D's universal pattern enforces this in `hard_limits`.

### 5.25 Pipeline-fidelity audit method

When `voice_config` changes after Phase 0.5 ran: three voice-config fields affect 1a/1b template selection (`type`/`subtype`/`hostile_sources`); the rest only affect Pass 0b tailor. If `hostile_sources` flipped, the dossier was generated WITHOUT the hostile-source warning block and must be re-run from scratch. If only `voice_mode`/`corpus_constraint` changed, only the tailor needs to re-run. Audit caught Whanganui hostile_sources misalignment during voice 3–12 buildout.

### 5.26 Pass 0a is operator-trusted

Hand-authoring voice_configs bypasses the operator-review checkpoint (`03_review_doc.md`). Pass 0a output is canonical; if operator review disagrees, edit and re-run Pass 0a (do NOT hand-edit downstream). Caught and corrected during voice 3–12 buildout for Cleopatra, Whanganui, Battuta — Pass 0a was sound on each.

### 5.27 Sentinel_regen smoke-test pattern

For prompt edits: snapshot pre-edit voice (`<baseline-snapshot-dir>/<voice_slug>/<filename>`), make prompt edit, run `sentinel_regen.py regen --pass <NAME> --voices <slug> --baseline-snapshot <DIR>`, inspect diff. Validate that intended pattern surfaced. Restore voice baseline post-validation if it was a smoke-test (not a real generation). 5 sentinel runs landed FU#49H/I/J/K/D this week.

### 5.28 Four deployment-context JSONs at project root (Tier 3)

- `conference_facts.json` (program — used by Pass 0a + Pass 7b)
- `audience_profile.json` (audience descriptive — Pass 7b)
- `panel_roster.json` (12 voices + casting principle — Pass 0a)
- `council_config.json` (runtime artifact, runtime team owns)

Each layer has single ownership. **Never** put real-person names in these — use generic descriptions ("a former PM," "a leading cognitive-warfare theorist"). Voices generate their own engagement_topics; we don't pre-populate with operator-curated targets. Refreshed for athens-2026 per `AUDIENCE_BRIEF.md` Part 3 (contributors-vs-audience distinction).

---

## 6. Known bugs, gaps, limitations

### 6.1 Data gaps

- **`runtime/reference/speakers.json`**: 202 speakers, **all `title/affiliation/bio` empty**. Speaker ID Pass 3 relies on bios for expertise matching (degrades from 70–85% to 40–50% without). **Pre-Athens blocker.**
- **`runtime/reference/sessions.skipped.json`**: 2 sessions with `venue: TBC`. Either firm up or leave skipped.
- **`runtime/flows/shared/council/council_config.json`**: version `dev_stub_v3_audience_sharpened`. Hand-written stubs. Replaced as athens-2026 cards complete.
- **athens-2026 voice_configs**: 12 of 12 written via Pass 0a (closed since 2026-04-26).
- **athens-2026 DR dossiers**: 1 of 12 voices have all 6 sections (Plato, carry-over). 11 voices × 6 sections = **66 manual claude.ai DR sessions outstanding**.
- **athens-2026 review_doc editorial_rationale**: 12 of 12 review_docs have `editorial_rationale: null` (each ends with `✍ CURATOR ACTION REQUIRED`). Optional — tailor already ran without these.

### 6.2 Pipeline gaps

- **Voice Pipeline** (Steps 1+2+3): not built. Without it, persona cards can't produce runtime output. Everything from Night 1 downstream is blocked.
- **Step 3 Amendment**: unspecified (FU#49E flagged highest-impact post-Athens).
- **Phase 5 Cross-Persona QC**: scaffolded (`phase_5_cross_persona_qc.py`), not run — needs all 12 cards.
- **Night 2 exclusion filter (Provocateur)**: placeholder, not implemented.
- **Continuity block generation**: not built.
- **Downstream pipeline** (Render/Publish/Curate/Deliver): unbuilt.
- **Closing-show pipelines** (theme identification, per-theme mapping, video): unspecified, unbuilt.
- **Microsite**: unbuilt.
- **Admin console**: unbuilt.

### 6.3 Documentation staleness

- **`_workspace/archive/specs/AI_Assembly_Architecture_v1.md`** — stale (n8n vs Prefect; 2-step vs 3-step Voice Pipeline; missing closing-show pipelines).
- **`_workspace/archive/specs/AI_Assembly_Infrastructure_Setup.md`** — stale (rclone/Drive mount + n8n Docker vs FastAPI upload).
- **`docs/AI_Assembly_Persona_Pipeline_v3_10.md`** — superseded by **v4** (2026-04-27). Body retained at `docs/_archive/` for history.
- **`docs/LLM_CALL_INVENTORY.md`** — needs update (new passes: 6.5-clean, 7a-fix, FU#2 3-stage, FU#41 chat builder).

### 6.4 Code issues (minor)

- `personas/flows/shared/clients.py#call_perplexity` + `call_openai`: hardened (guarded access, narrow exceptions).
- `personas/flows/shared/node1c_fetch.py`: SSRF-hardened.
- **FU#50(1) Pydantic enforcement at Pass 2/4a outputs**: deferred post-Athens. List-of-string vs list-of-dict shapes both currently valid per prompts; orchestrator accepts both. Voices 3–12 may produce inconsistent shapes — empirical monitor on voice 3 ship.

### 6.5 Environmental dependencies

- **OpenAI quota**: needs allowance for voices 3–12 + Pass 7a calls.
- **Google API quota**: verify before batch persona runs.
- **Perplexity quota**: 500 queries/month on Pro; 12 voices = 12 queries, fine.

### 6.6 Open design questions (per Briefing v3.1)

- Introduction location for Day 1 (4 options).
- Program copy revision for the AIssembly entry.
- Video production path.
- Day 4 goodbye voice.
- Multilingual interpretation policy (whether to flag interpreted quotes).
- Audience question mic separation (recording-protocol change).

---

## 7. Environment, dependencies, constraints

### 7.1 Required on every machine that runs the pipelines

- Python 3.12 (both venvs)
- `ffmpeg` + `ffprobe` (system) — required for ingest normalization + validation
- Git

### 7.2 API keys (unified `.env` at monorepo root)

| Key | Used by | Phase | Notes |
|---|---|---|---|
| `ANTHROPIC_API_KEY` | Both | Both | Largest volume |
| `ASSEMBLYAI_API_KEY` | runtime | Overnight | Transcription |
| `UPLOAD_APP_PASSWORD` | runtime ingest | Overnight | HTTP Basic Auth |
| `PERPLEXITY_API_KEY` | personas | Pre-conference | ~$5/voice for Pass 1a |
| `GOOGLE_API_KEY` | personas | Pre-conference | Gemini broad scan + Pass 7c fallback |
| `OPENAI_API_KEY` | personas | Pre-conference | Pass 7-anachronism + Pass 7a primary |

Future keys: `SUNO_API_KEY` (Marley renders), `GITHUB_TOKEN` (microsite), `VERCEL_TOKEN`, email tool credentials.

### 7.3 Version pins

- `anthropic==0.94.1` (both)
- `assemblyai==0.59.0` (runtime)
- `prefect==3.6.26` (both)
- `google-genai==1.73.1` (personas)
- `openai==2.31.0` (personas)
- `fastapi==0.135.3` (runtime)
- `jinja2==3.1.6` (personas)

### 7.4 VM target (Hetzner CX22/CX32)

Ubuntu 24.04 LTS; 2–4 vCPU, 4–8 GB RAM, ≥100 GB SSD; `ingest` system user (nologin); `/opt/ai-assembly/` install root; Caddy reverse proxy + Let's Encrypt; systemd hardening; ufw 22/80/443.

### 7.5 Cost estimates

| Component | Per-unit cost | Volume | Total |
|---|---|---|---|
| Persona Pipeline per voice | $18–22 | 12 voices | $215–265 |
| Transcription per night | $4–6 | 3 nights | $12–18 |
| Researcher per night | $15–25 | 3 nights | $45–75 |
| Provocateur per night | $15–25 | 3 nights | $45–75 |
| Voice Pipeline per night (est) | $20–40 | 3 nights | $60–120 |
| Downstream (Suno + Curate) | ~$1–3 | 2 nights curate | $2–6 |
| **Total Athens run** | | | **~€400–600** |

Per-voice envelope rose from v3.10's $14–18 to v4's $18–22 due to: (a) per-section claude.ai DR sessions are operator-paid (not per-API), but Phase 0.5 + Pass 1d (60K char budget) + arch-03 chunked merge runs cost slightly more; (b) FU#13 patcher replaces revision loop, **lowering** API cost ~$5–10 → ~$1; net higher because FU#2 chunked Pass 7-pre adds Sonnet calls.

---

## 8. Pre-Athens critical path

Given today's state: voices 3–12 are at Phase 0.5 complete; 11 × 6 = 66 manual DR sessions outstanding; Voice Pipeline + downstream all unbuilt.

### Phase A — Persona pipeline build-side (DONE 2026-04-27)

- ✓ Plato shipped + chat-test validated (2026-04-26)
- ✓ Voice 3–12 voice_configs (Pass 0a, all 12)
- ✓ Phase 0.5 research for all 12 voices
- ✓ Pipeline-fidelity audit
- ✓ FU#49 family of universal patterns landed (49A, 49C, 49D, 49H, 49I, 49J, 49K)
- ✓ 212/212 tests passing

### Phase B — Voice 3–12 cards complete (now → Athens-3w)

**Operator gates (parallel to code work):**
1. **66 manual claude.ai DR sessions** (11 voices × 6 sections, ~60–180 min each).
   - §1–§5: claude.ai with **Opus 4.6** + Extended Thinking + Deep Research
   - §6: claude.ai with **Opus 4.7** + Extended Thinking + Deep Research (Phase L empirical: 4.6 produces reader's-intro on §6; 4.7 required)
   - Save each as `voices/<slug>/01_research/04_dr_dossier/0N_section_N.md`
2. **Optional**: editorial_rationale fill-in on 12 review_docs.
3. **FU#49G** Greek-scholar calibration (Quarch / Tsinorema / Erinakis on Plato — provotype-test, not pastiche-test).
4. **As DR data lands per voice**, run pipeline:
   ```bash
   cd code/personas
   set -a && source ../.env && set +a
   venv/bin/python run_persona_pipeline.py "<Voice>" \
     --project "/Users/aienvironment/Desktop/AI Assembly/projects/athens-2026"
   ```
   ETA: ~2h / ~$18–22. After CARD COMPLETE: chat-test paste `06_derive/03_chat_system_prompt.json` into Claude project.

**When 12/12 ship:** closes the pre-Athens persona pipeline workstream.

### Phase C — Voice Pipeline + supporting infrastructure (Athens-4w → Athens-1w)

- Spec **Step 3 Amendment** (currently unspecified — FU#49E)
- Build Voice Pipeline Steps 1+2 (Prefect flow, system prompt assembly from cards, optional validation)
- Build Step 3 Amendment + theme-graph
- Integration test against dev_msc_test Provocateur output
- Build Night 2 continuity generation
- Phase 5 Cross-Persona QC — run after all 12 cards complete; address distinctiveness issues
- Sync `council_config.json` from real Derive output (script or admin-console feature)

### Phase D — Microsite (parallelisable with C)

- Lovable / v0 prototype for nav pattern
- Production Astro/Next.js codebase, content schema, shader integration (Octopus), Suno hosting (Marley)
- Vercel/Netlify auto-rebuild
- Holding-page fallback for Night 1 failure

### Phase E — Closing show + readout

- Spec theme identification, per-theme mapping (Matrix A+B), video pipeline
- Build all three passes
- Matrix-pair visualization template
- Handoff protocol to closing-show production team
- Human editorial pass tooling

### Phase F — VM + admin console

- Hetzner provision, install stack, clone monorepo, populate `.env`
- systemd + Caddy + ufw
- Build admin console (FastAPI mirroring ingest architecture); council sync button; log tail
- Dry Run 1 (T–2w): plumbing test
- Dry Run 2 (T–1w): full pipeline against real HoBB panel
- Recording-protocol briefing to A/V team

### Phase G — Pre-conference logistics

- Populate `runtime/reference/speakers.json` bios (blocking for Speaker ID quality)
- Moderator briefings (full-name introductions)
- Walking-session participant briefings (self-introduce)
- AssemblyAI custom vocabulary populated
- HoBB email tool + API credentials (Substack)
- Greek SIM
- Printouts: pipeline specs, this CURRENT_STATE.md, runbook, A/V filename convention
- Final hotel Wi-Fi test
- Backup person has SSH key + `.env` copy in 1Password

---

## 9. Risks and mitigations

In decreasing order of "if this goes wrong, how bad?"

| Risk | Mitigation | Notes |
|---|---|---|
| Voice Pipeline not built by Athens | Drop Step 3, ship Steps 1+2 only; briefing robust to this | Reduces deliberative character but keeps experiment intact |
| Persona cards not all complete | Ship with 8–10 cards; drop voices; adjust council_config | Weakens panel, better than no Assembly |
| Closing show too ambitious | Ship mapped read-through only; drop video snippets | Video is nice-to-have |
| AssemblyAI diarization fails on key session | Speaker ID flags for human review; 15–30 min human pass | Validated on MSC test sessions |
| API quota exhaustion mid-Athens | Pre-test all keys final week; backup keys; Anthropic Batch | Dominant: OpenAI |
| VM dies mid-conference | Laptop fallback; `.env` in 1Password; repo cloned locally | Per Infrastructure_Setup §Failure fallback |
| Audio recording quality bad | Normalized 96 kbps mono is forgiving; 5-pass Speaker ID | 15–30 min human review per night |
| Cleopatra voice produces sanitised output on ethnicity | hostile_sources=true + Pass 7a register/anachronism checks | Voice config is `hostile_read_against_grain` |
| Thiel voice carries legal risk | Needs review separate from architectural spec | Open question per Briefing v3.1 |
| Audience doesn't engage | Provotype is designed to surface this as a finding; Day 4 publishes regardless | "Indifference is failure" |

---

## 10. Housekeeping

### 10.1 How to update this doc

- On any significant state change, update the relevant section in the same commit.
- If a phase completes: move items from §8 to §1 or §6.
- If a spec becomes stale: flag in §6.3 and `docs/README.md`.
- New architectural decision: add to §5 with rationale.
- New data contract: add to §4.
- Bump `Last updated` at top.

### 10.2 Commit convention

For this doc, prefix commits with `state:`.

### 10.3 Related docs

- `docs/README.md` — staleness banner
- `docs/AI_Assembly_Briefing_v3_1.md` — target state
- `docs/AI_Assembly_Persona_Pipeline_v4.md` — current persona pipeline (2026-04-27)
- `docs/AI_Assembly_Persona_Card_v2.md` — 35+2 field schema (with v2.1 amendments section)
- `personas/HANDOFF.md` — persona → runtime contract (current)
- `_workspace/planning/HANDOFF_2026_04_27.md` — current session pickup
- `_workspace/planning/FOLLOW_UPS.md` — active FU# tracker
- `_workspace/planning/ONBOARDING.md` — fresh-session onboarding
- `_workspace/archive/specs/AI_Assembly_Architecture_v1.md` — STALE (archived)
- `_workspace/archive/specs/AI_Assembly_Infrastructure_Setup.md` — STALE (archived)

---

*End of CURRENT_STATE.md. Read alongside Briefing v3.1 as the most current picture of the system. When in doubt: Briefing describes what we're building; this describes where we are.*
