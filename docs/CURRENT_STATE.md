# AI Assembly — Current State

**Last updated:** 2026-04-17
**Purpose:** Gap analysis and project-state snapshot. What's built, what's specified-but-not-built, what's not-yet-specified, key decisions, known bugs, pre-Athens critical path. Complements the briefing docs (which describe the target state) and the pipeline specs (which describe individual components). This doc describes **what exists now** and **what's next**.

> When something lands, update this doc in the same commit. When the system drifts from the briefing, update the briefing and this doc together.

---

## 0. Quick map

```
ai-assembly/  (monorepo; four-category layout as of 2026-04-19)
├── docs/                      # PRODUCTION: current specs + this file
│   ├── CURRENT_STATE.md                   # you are here
│   ├── README.md                          # staleness banner for the other specs
│   ├── references.md                      # pointer into research/ and _workspace/planning/
│   ├── AI_Assembly_Briefing_v3_1.md       # project briefing (current)
│   ├── AI_Assembly_Persona_Card_v2.md
│   ├── AI_Assembly_Persona_Pipeline_v3_10.md
│   ├── AI_Assembly_Provocateur_Pipeline.md
│   ├── AI_Assembly_Researcher_Pipeline.md
│   ├── AI_Assembly_Transcription_Pipeline.md
│   ├── AI_Assembly_Voice_Pipeline.md      # Steps 1+2 only; Step 3 unspecified
│   ├── AUDIENCE_BRIEF.md
│   ├── LLM_CALL_INVENTORY.md
│   └── design/
├── runtime/                   # PRODUCTION code: FastAPI ingest + Prefect flows
│   ├── ingest/                            # FastAPI upload app (built, tested)
│   ├── flows/
│   │   ├── transcription_flow.py          # built, 5-pass Speaker ID, 3 MSC test sessions
│   │   ├── researcher_flow.py             # built, Opus + adaptive thinking, validated
│   │   ├── provocateur_flow.py            # built, 5-stage, validated on dev_msc_test
│   │   ├── voice_flow.py                  # NOT BUILT
│   │   └── shared/
│   │       ├── council/council_config.json# dev_stub_v2 (hand-written, not derived)
│   │       └── prompts/                   # 8 active + 4 archived
│   ├── reference/                         # runtime data: sessions.json, speakers.json
│   └── scripts/                           # sessions/speakers regeneration
├── personas/                  # PRODUCTION code: pre-conference voice card build
│   ├── run_pass0a_voice_config.py         # Pass 0a: voice config + review doc
│   ├── run_phase0_1_research.py           # Phase 0.5: Perplexity + Gemini → DR prompt
│   ├── run_pass0b_dr_prompt.py            # Pass 0b: DR prompt only (no research)
│   ├── run_persona_pipeline.py            # main pipeline (Pass 1-merge → Derive)
│   ├── flows/shared/                      # io, clients, node0_validation, wikipedia, dr_validation, node1c_fetch, node1d_excerpt_selection, prompt_render
│   ├── inputs/
│   │   ├── conference_facts.json          # Phase B split — conference metadata (Pass 0a + Pass 7b)
│   │   ├── audience_profile.json          # Phase B split — audience profile (Pass 7b only)
│   │   ├── panel_roster.json              # Phase B split — 12-voice panel list (Pass 0a)
│   │   ├── non_human_grounding/           # Phase B — curated Octopus + Whanganui grounding for Pass 0a
│   │   ├── voices/                        # voice configs (v3.10 configs archaeology; rebuild under Phase B)
│   │   └── dossiers/                      # Claude DR dossiers (manually produced)
│   └── HANDOFF.md                         # cross-repo contract (production, active)
├── research/                  # PRESERVED: grounding material, not deletable
│   └── baseline_research/                 # 5 Deep Research compass artifacts
├── _workspace/                # Out of scope for code reviews + VM deploys
│   ├── planning/                          # forward-looking: REBUILD_PLAN (single source of truth post-merge 2026-04-19)
│   └── archive/                           # eligible for pruning: specs, fix-plans, session-artifacts, runs
└── .env, .env.example, .gitignore, README.md, CLAUDE.md
```

---

## 1. What exists and is verified

### 1.1 Persona Pipeline (personas/)

**Status: built, end-to-end. Phases 1, 2, 3, 4 complete. Phase 5 Cross-Persona QC not built.**

Two full runs completed: **Plato** (full pipeline, all artifacts in `_workspace/archive/runs/personas/plato/`) and **Hannah Arendt** (01_research + 02_passes populated; final assembled card not yet verified). Runs per voice take 60–120 minutes wall time, cost $14–18 in API calls (before Claude Batch discount).

Built and verified:

| Component | Status | Notes |
|---|---|---|
| Node 0 validation | ✓ | 5 gates: impossible, type, voice_mode (strict 3-enum), subtype, corpus_constraint |
| Pass 0a Intake | ✓ | Claude Opus + adaptive thinking; produces voice config + review doc |
| Phase 0.5 Pre-DR Research | ✓ | `run_phase0_1_research.py`: Pass 1a (Perplexity) + Pass 1b (Gemini) in parallel, then renders DR prompt via Jinja2 |
| Pass 0b DR Prompt | ✓ | Jinja2 template renderer (no API call); scaffolds DR prompt with research findings |
| Pass 1a Perplexity | ✓ | sonar-deep-research; `<think>` block stripped; now runs in Phase 0.5 |
| Pass 1a-DR Claude | ✓ | Manual paste; Approach C merge partner |
| Pass 1b Gemini | ✓ | Broad scan; now runs in Phase 0.5 |
| Pass 1-merge | ✓ | 3-way contradiction check (Perplexity + Claude DR + Gemini) |
| Pass 1c-extract | ✓ | NEW: extracts primary text URLs from merged dossier |
| Pass 1c fetch | ✓ | SSRF-hardened (scheme restriction, RFC1918 block, 5MB cap) |
| Pass 1d excerpt selection | ✓ | Sonnet-curated ~30K char subset (replaces naive 80K slice) |
| Pass 2 Identity & Boundaries | ✓ | Opus + adaptive thinking; 9 fields |
| Pass 3 Intellectual Core | ✓ | Opus + thinking; 5 fields; ChatGPT DR conditional |
| Pass 4a Voice | ✓ | Opus + thinking; 7 fields; corpus-grounded |
| Pass 4b Artifact | ✓ | Sonnet; 8 fields |
| Pass 5 Engagement | ✓ | Opus + thinking; 4 fields; constitution + reasoning_method in user prompt |
| Pass 6 Corpus Curation | ✓ | Sonnet; 1 field; HALT if no primary texts |
| Coherence Threading | ✓ | Per-pass Sonnet compression after Passes 2, 3, 4a, 4b |
| Pass 7-pre Citation | ✓ | Sonnet; voice-mode branching; hostile-source variant |
| Pass 7a Cross-Model | ✓ | GPT-4o → o3 → Gemini fallback; register check |
| Revision loop | ✓ | Max 2; downstream cache invalidation; per-pass critiques |
| Pass 7b Worked Provocations | ✓ | Opus + thinking; diagnostic only, NOT runtime few-shot |
| Pass 7c Negative Constraints | ✓ | Gemini → Sonnet fallback with bias-awareness |
| Derive | ✓ | Sonnet; produces Provocateur Profile + Evaluation Rubric |
| Output Register check | ✓ | Built into runner; flags third-person leaks in voice fields |
| Assembled card write | ✓ | 35 fields at root + metadata block; matches spec |

**What Plato's run produced:**

```
runs/plato/
├── persona_card_assembled.json  (35 fields + metadata, spec-compliant)
├── provocateur_profile.json     (8 fields, ready for council_config)
├── evaluation_rubric.json       (9 test prompts)
├── 01_research/
│   ├── perplexity_dossier.json
│   ├── gemini_broad_scan.json
│   ├── chatgpt_dr_supplement.json  (triggered — DR supplement fired)
│   ├── contradiction_check.json
│   ├── merged_dossier.json
│   ├── primary_texts.json           (5 Gutenberg dialogues fetched)
│   └── excerpt_selections.json      (Pass 1d curated)
└── 02_passes/
    ├── pass2_identity_boundaries.json
    ├── pass3_intellectual_core.json
    ├── pass4a_voice.json
    ├── pass4b_artifact.json
    ├── pass5_engagement.json
    ├── pass6_corpus.json
    ├── pass7pre_citation.json
    ├── pass7a_cross_model.json
    ├── pass7b_smoke_test.json
    ├── pass7c_negative.json
    ├── derive.json
    └── _ct_pass2.json, _ct_pass2_3.json, _ct_pass2_3_4a.json, _ct_pass2_3_4.json
```

### 1.2 Ingest app (runtime/ingest/)

**Status: production-ready, tested, deployed-deployable.**

| Component | Status | Notes |
|---|---|---|
| FastAPI routes (index, session detail, status, overview, upload, retry, health) | ✓ | All routes auth-gated except /health |
| HTTP Basic Auth | ✓ | `secrets.compare_digest`; IP-based rate limiting (10 fails/60s → 429) |
| Upload pipeline: receive → normalize → spawn transcription | ✓ | Atomic JSON writes, fcntl file locking |
| Audio normalization | ✓ | ffmpeg → 96 kbps mono AAC; ffprobe validation (timeout=30s) |
| Status state machine | ✓ | received → normalizing → transcribing (with substates) → done/error |
| Reconcile-on-startup | ✓ | Scans runs/ on app start, marks orphaned PIDs as error |
| Detached subprocess spawn | ✓ | `start_new_session=True`; survives uvicorn restart |
| PID liveness check | ✓ | Detects zombie/defunct processes |
| Incremental crumb display | ✓ | UI shows which step the subprocess is on |
| Retry endpoint | ✓ | Resume from last completed checkpoint |
| Filters (day, venue, search) | ✓ | Client-side JS |
| Track colour system | ✓ | Matches program.worldbeautifulbusinessforum.com |
| Tests | ✓ | `test_app.py`, `test_pipeline.py`, `test_sessions.py` + fake flow |
| Deploy configs | ✓ | `ingest.service` (systemd with hardening), `Caddyfile`, `README.md` |

### 1.3 Transcription Pipeline (runtime/flows/transcription_flow.py)

**Status: built, validated on 3 MSC 2026 test sessions (Vox Populi, Breaking Point, West-West Divide).**

| Component | Status | Notes |
|---|---|---|
| AssemblyAI Universal-3 Pro | ✓ | speaker_diarization, language_detection, keyterms_prompt |
| SDK 0.59.0 workarounds | ✓ | `config.raw.speech_models = ["universal-3-pro"]`; `speech_model = None` |
| Speaker ID (5-pass) | ✓ | Pass 5 = per-turn reassignment; Opus override via `TRANSCRIPTION_SPEAKER_ID_MODEL` |
| Cleaning | ✓ | Streaming required; 64K max_tokens; 80% budget warning |
| Session package assembly | ✓ | Metadata + transcript + review_queue |
| Resume-from-disk | ✓ | Skips completed stages if output JSON exists |
| Prefect task caching (dev) | ✓ | `TRANSCRIPTION_CACHE=1` env var; off in production |

### 1.4 Researcher Pipeline (runtime/flows/researcher_flow.py)

**Status: v3 built, validated on dev_msc_test (106 extractions → 25 clusters → 6 themes, 83% cross-session theme ratio).**

| Component | Status | Notes |
|---|---|---|
| Node 1 Extraction (per-session) | ✓ | Namespaced IDs `{session_id}:NNN`; verify_markers handling |
| Node 2a Clustering | ✓ | Opus + adaptive thinking; minimal input `{ref, extraction, context}`; shuffled seed 42 |
| Node 2b Theming | ✓ | Same model config; cluster-level input only |
| `_validate_clusters` | ✓ | Closure + uniqueness; orphan detection; empty-cluster pruning |
| `_validate_themes` | ✓ | Closure; orphan promotion to single-cluster themes |
| Merge step | ✓ | Python; builds final `grouping.json` with full themes→clusters→extractions nesting |

### 1.5 Provocateur Pipeline (runtime/flows/provocateur_flow.py)

**Status: v3 (5-stage) built, validated on dev_msc_test.**

| Component | Status | Notes |
|---|---|---|
| Stage 1A Triage Part A (per-voice) | ✓ | 12 parallel LLM calls; incremental checkpoint per voice |
| Stage 1B Triage Part B (theme flags) | ✓ | 1 LLM call; `worth_surfacing` + friction + fault_line |
| Stage 2 Selection | ✓ | Pure Python, deterministic, 9 steps, 8 tunable knobs in council_config |
| Stage 3 Formulation (per-pair) | ✓ | Parallel batched; PROPOSITION TEST (5 conditions); narrative briefing components |
| Stage 4 Packaging | ✓ | Two-view briefings: `narrative_briefing` (markdown) + `full_theme_record` (structured) |
| Incremental checkpoints | ✓ | Per-voice triage, per-pair formulation, briefings per voice |
| Rate-limit batching | ✓ | `PROVOCATEUR_FORMULATION_BATCH=4`, `PROVOCATEUR_BATCH_WAIT_S=20` |

---

## 2. Specified but not built

### 2.1 Voice Pipeline Steps 1 + 2 (runtime/flows/voice_flow.py)

**Spec:** `docs/AI_Assembly_Voice_Pipeline.md` (covers Steps 1+2 only).

**Status: not built.** (`runtime/flows/voice/` directory does not exist.)

**What Step 1 does:** Receive Provocateur briefing → load Persona Card as system prompt → produce one detailed response per formulation (~3 per voice).

**What Step 2 does:** Read back all detailed responses → make focus + stance decisions → produce one artifact per voice in the voice's natural medium.

**Key wiring decisions already made (documented in voice/README.md and personas/HANDOFF.md):**
- Load persona card fields as system prompt; DROP `metadata` and `smoke_test_chains` (smoke_test_chains is a build-time smoke test, NOT a runtime few-shot — critical).
- Foundational fields (12) appear in both Step 1 and Step 2 system prompts.
- Step 1 uses Reasoning + Engagement fields; Step 2 uses Voice + Artifact fields.
- Runtime reads `$PROJECT_ROOT/runs/<voice_slug>/persona_card_assembled.json` directly (Tier 3 — project data lives outside the code repo; see CLAUDE.md §"Code / project separation").

**What needs building:**
- Prefect flow with Step 1 task + Step 2 task
- System prompt templates for each step (per voice)
- Per-voice parallel execution; per-formulation parallel within a voice
- Optional validation (anachronism check, constitutional check)
- Output schema: detailed_responses[] + artifact per voice per night
- Cross-voice venv handling (the voice pipeline runs in runtime's venv but reads personas' assembled cards — cross-repo read, same machine)

### 2.2 Phase 5 Cross-Persona QC (personas)

**Spec:** `docs/AI_Assembly_Persona_Pipeline_v3_10.md` § Phase 5.

**Status: not built.** The `IMPLEMENTATION_AUDIT_v3_7.md` flagged this in April 2026; since then Phase 3+4 were built but Phase 5 was not.

**What it does:** After all 12 cards complete, run three batch tests:
1. **Swap test:** shuffle constitution principles, can an evaluator attribute each? Misattributed → too generic.
2. **Blind identification:** remove names from character + register_and_tone, shuffle, can evaluator identify?
3. **Same-question distinctiveness:** run all voices through one provocation, compare for style/metaphor/values similarity.

**Tool:** ChatGPT (cross-model from Claude-generated cards).

**Blocker:** needs all 12 cards to exist first. So it runs last in the persona pipeline sequence.

---

## 3. Not yet specified (and unbuilt)

These are in the briefing but have no detailed spec yet.

### 3.1 Voice Pipeline Step 3 — Amendment

**Briefing v3.1 describes it:** after all 12 voices produce first-draft artifacts, each voice reads first-draft artifacts of OTHER voices it shares at least one theme with, and decides whether to amend its own. Amendments are visible (reference the other voice, implicitly or explicitly). If no amendment, Step 2 artifact publishes unchanged.

**What's needed:**
- System prompt for Step 3 (framed by shared-theme portions of other voices' artifacts)
- Input format: how other voices' artifacts are presented (shared-theme highlighted, other portions summarised?)
- Output format: amended_artifact + amendment metadata (which voices referenced, in response to what)
- Integration with Step 2 output (each voice's Step 2 result feeds all voices' Step 3 via theme-graph)
- Timing within overnight budget

**Dependency order for spec work:** needs Voice Pipeline Steps 1+2 building to have reference outputs, then spec Step 3 against those.

### 3.2 Closing-show pipelines (Day 3 afternoon)

Per Briefing v3.1, THREE pipeline passes run Day 3 afternoon before the closing show:

1. **Theme identification pass** — reads across all 3 nights' Researcher themes, Provocateur formulations, and voice detailed responses. Identifies 3–5 throughline themes.
2. **Per-theme mapping pass** — for each throughline, reads each voice's positions and plots on Matrix A (Power & Agency, human↔nonhuman / many↔one) and Matrix B (Change & Actor, rupture↔progression / individual↔collective). Generates read-through script segment per theme.
3. **Video pipeline pass** — generates per-voice spoken-dialogue fragments for the closing-show running-the-last-kilometre video snippets. Uses persona cards + all 36 artifacts + Video Context block.

**What's needed:**
- Input format for each pass
- System prompts for each pass
- Matrix plotting format (visual spec for the closing-show visualisation team)
- Output handoff to closing-show production (video editors, animators)
- Human editorial pass after generation (~1–2 hours per pass)

### 3.3 Downstream pipeline (per-night, runs after Voice Pipeline completes)

Per Briefing v3.1 + Architecture_v1 (Architecture_v1 is stale on orchestrator but the stage logic stands):

1. **Render** — text passes through; Marley's artifact → Suno API; Octopus's artifact → client-side shader params packaging. Retries + fallbacks.
2. **Publish** — aggregate all 12 artifacts into `night-N.json`; commit+push to microsite content repo; Vercel rebuild.
3. **Curate** — single Claude Opus call generates HoBB-voiced Substack read-through. Few-shot on real HoBB newsletters. Skipped on Night 3 (closing show reveals it).
4. **Deliver** — Substack publishes; blurb inside HoBB daily newsletter.

**Not yet built. Newsletter style calibration is a separate workstream.**

### 3.4 Microsite

Per Briefing v3.1: Astro or Next.js static site, Vercel/Netlify hosting, content repo (GitHub), deep links per artifact (`/night-1/plato`, etc.).

**Needs building:** design prototype (Lovable/v0), production codebase, content schema, chromatophore shader integration, navigation pattern.

### 3.5 Admin Console

**User's intent:** a web UI similar in spirit to the ingest app but covering the full pipeline. Runs under a different user than ingest; ingest narrows to "received" status only. Admin console orchestrates: transcription, researcher, provocateur, voice, downstream, persona card building, council sync, closing-show pipelines.

**Not specified. Not built.** Natural first features:
- Kick off a pipeline stage on demand
- View status across all stages
- View logs
- Sync persona Derive outputs → council_config.json (script already plannable)
- Pre-flight checks

### 3.6 Night 2 / Night 3 plumbing

**Provocateur:** has placeholder for "Night 1/2 exclusion filter" — simple (theme_id, member) exclusion list to avoid repeating assignments. Not implemented. Needs building before first production run past Night 1.

**Voice Pipeline:** Continuity block generation (1 API call per voice after Night 1/2 completes, produces 4-field structured summary inserted into next night's persona card). Not built because Voice Pipeline not built.

**Researcher:** processes fresh each night; no cross-night dependency. Good as is.

### 3.7 Cross-repo tooling

- **Sync council config**: script that reads all `$PROJECT_ROOT/runs/*/provocateur_profile.json` and writes them into `runtime/flows/shared/council/council_config.json` members array, bumping version. Currently manual copy-paste. Easy Python script; natural first feature for admin console.

---

## 4. Cross-repo data contracts

Documented precisely so nothing drifts.

### 4.1 Persona → Runtime (2 artifacts per voice)

**Provocateur Profile (8 fields):**
- File: `$PROJECT_ROOT/runs/<voice_slug>/provocateur_profile.json` (per Tier 3, project data lives outside the code repo; default sibling `../athens-2026/`)
- Consumer: `runtime/flows/shared/council/council_config.json#members[]`
- Fields: `name`, `speaks_from`, `core_commitment`, `activates_on`, `goes_flat_on`, `stretch`, `translation_range`, `stance_tendency`, `medium`
- Currently: **council_config is `dev_stub_v2`** — hand-written, not derived. 12 stub members present. Needs replacement with real derived profiles before production.

**Assembled Persona Card (37 fields):**
- File: `$PROJECT_ROOT/runs/<voice_slug>/persona_card_assembled.json`
- Consumer: `runtime/flows/voice_flow.py` (when built) — loads as system prompt
- Runtime MUST drop `metadata` block and `smoke_test_chains` field before using as prompt (per HANDOFF.md and voice/README.md). Both are build-time artifacts, not runtime contract.
- 35 fields appear as system prompt content; 2 null continuity fields populated during runtime Night 2.

### 4.2 Transcription → Researcher

**Session package:**
- File: `runtime/runs/<run>/01_transcription/<session>/session_package.json`
- Consumer: `runtime/flows/researcher_flow.py`
- Structure: `metadata` (carried forward) + `transcript.turns[]` + `review_queue.verify_markers[]`
- Critical invariant: per-turn `confidence` flows through to Researcher (contract verified on 3 MSC test sessions)
- `review_queue.verify_markers` is actively consumed (Node 1 degrades extraction confidence on hinge words)

### 4.3 Researcher → Provocateur

**Two artifacts per run:**
- `runtime/runs/<run>/02_researcher/all_extractions.json` — flat list of extractions
- `runtime/runs/<run>/02_researcher/grouping.json` — themes → clusters → extraction_ids

**Provocateur interface contract (verified on dev_msc_test):**
- Step 1 Triage reads abstracts only (themes + clusters)
- Step 2 Selection reads abstracts + extraction_ids for counting
- Step 3 Formulation reads raw extractions for the single theme it's formulating on
- Step 4 Packaging reads everything

**Field format conventions:**
- Extraction IDs are namespaced strings: `"breaking_point:014"`
- `lens` values use underscore: `"open_question"` (not space)
- `engagement`: `null` for open questions; `"challenged" | "reinforced" | "unengaged"` otherwise
- `energy`: `"high" | "normal"`
- `speaker`: string or `null` (null for synthesized open questions)

### 4.4 Provocateur → Voice Pipeline

**Per-voice briefing:**
- File: `runtime/runs/<run>/03_provocateur/briefings/<voice_slug>.json`
- Consumer: `runtime/flows/voice_flow.py` (when built)
- Structure: `formulations[]` each with TWO views:
  - `narrative_briefing` — markdown string, the Step 1 user prompt
  - `full_theme_record` — structured JSON, the Step 1 private reasoning surface

### 4.5 Ingest → Transcription

**Per-session trigger:**
- Ingest produces `runs/<run>/01_transcription/<session>/audio.m4a` (normalized)
- Ingest produces `runs/<run>/01_transcription/<session>/session.json` (schema-translated from sessions.json + speakers.json join)
- Ingest spawns `python flows/transcription_flow.py <audio> <session_json>` detached; transcription_flow writes all outputs back into the same dir

**Schema translation (critical):**
- `sessions.json` field `title` → `session.json` field `session_title`
- `sessions.json` field `description` → `session.json` field `session_description`
- `sessions.json` field `date_time_start` → `session.json` field `date_time`
- `venue + venue_sub` → concatenated `venue` (` · ` separator if both)

---

## 5. Architectural decisions & rationale

Key decisions that aren't obvious from reading the code and that a new session/collaborator needs to know.

### 5.1 Separate venvs (runtime + personas)

**Why:** dependency isolation. Both currently pin `anthropic==0.94.1`, but separate venvs mean one pipeline can update a dependency without forcing the other to follow. Admin console can subprocess into whichever venv it needs.

### 5.2 Unified `.env` at monorepo root

**Why:** same API keys used by both pipelines. Single source of truth. All 7 `load_dotenv` callers explicitly load from `_REPO_ROOT.parent / ".env"` where `_REPO_ROOT` is the sub-repo root. `personas/flows/shared/clients.py` keeps bare `load_dotenv()` — it walks up from CWD and finds the root `.env` automatically.

### 5.3 Output Register rule (v3.7)

**Why:** mock execution showed that 10–15K tokens of third-person field content overwhelmed the ~80-token second-person epistemic frame. The model adopted scholarly distance regardless. Every field now in first or second person. Enforced by Pass 7a register check + runner's `_check_register` function + per-field register table in the card spec.

### 5.4 KJ Round 1 minimal input (Researcher v2.4 → v3)

**Why:** Opus+thinking was using the namespace prefix as a grouping shortcut. Round 1 sees only `{ref, extraction, context}` — no real ID, no session, no responds_to, no lens, no engagement. Restored 4.08 extractions/cluster average and 83% cross-session ratio from 2.08 and 25%.

### 5.5 Python Selection (Provocateur v3)

**Why:** Selection is combinatorial scoring, not editorial judgment. LLM was slow, non-reproducible, opaque. Python is instant, deterministic, all knobs tunable in council_config. Substance-aware work moved to per-pair Formulation where it matters.

### 5.6 Per-pair Formulation (Provocateur v3)

**Why:** one formulation per theme forced to generic altitude to fit all assigned voices. Per-pair calls let each formulation aim at one voice's specific territory. Two voices on the same theme now get genuinely different questions, not wording variations.

### 5.7 Proposition Test with 5 conditions (Provocateur v3)

**Why:** v1's informal "use proposition when material contains a sharp claim" drifted to proposition-by-default in testing. Explicit 5-condition test in prompt catches it. Validation: 3/40 propositions on dev_msc_test, all passing all 5 conditions; rest correctly wrote questions.

### 5.8 Checkpoints-as-cache (Provocateur, Personas)

**Why:** explicit cache flag forgotten half the time. Incremental writes of each LLM call to disk before return. Restart picks up from wherever it died. Force clean run by deleting the specific checkpoint. No `CACHE=1` env var needed.

### 5.9 Deterministic shuffle seed 42 (Researcher Round 1 + Round 2)

**Why:** session-ordered concatenation produces session-grouped reading order bias. Fixed seed breaks the bias without losing reproducibility.

### 5.10 `smoke_test_chains` is build-time only, NOT runtime few-shot

**Decision date:** 2026-04-15. Documented in: `personas/flows/shared/prompts/persona_pass_7b_smoke_test.md` and `personas/HANDOFF.md`. (`runtime/flows/voice/README.md` was planned but never built — the rule moved to the two personas locations above.) Rationale: few-shotting from 4 test chains would collapse the voice's range toward those 4 patterns, re-introduce failures Pass 7c removed, propagate stale `conference_context`, and over-constrain a prompt already strong enough.

### 5.11 Pass 1a primary text URLs moved from Pass 0a to Pass 1c-extract (commit b1868da)

**Why:** Pass 0a has no internet access and was proposing URLs from training data — risk of hallucinated or stale URLs. Now primary text URLs are extracted from the merged dossier (which contains Section 6 URLs from all three research sources). Backward compat: if voice config has `primary_text_sources` populated manually (Plato), those are used directly.

### 5.12 `voice_mode` validation — strict 3-value enum

**Current:** {philosophical, observational, narratival}, with null
allowed only for `subtype: "system"` voices (system entities bypass
voice_mode branching entirely).

**History:** commit `b1868da` (2026-04-16) briefly relaxed this to
freeform string to accommodate Pass 0a proposing creative per-voice
modes (`sovereign-diplomatic`, `embodied-distributed`, etc.). Commit
`4c5c366` (restore strict voice_mode validation) reverted that —
downstream prompt branching in Passes 2-5 depends on the fixed
three-value enum; freeform modes broke prompt rendering for any voice
Pass 0a proposed a novel mode for.

**Enforcement:** `personas/flows/shared/node0_validation.py:60`.

**Open question for Phase B:** whether to expand the enum is
`_workspace/planning/REBUILD_PLAN.md §Cross-cutting §"Decision: keep \`voice_mode\` 3-enum
or expand?"`. Default for now: keep the 3-enum.

### 5.13 `needs_dr_supplement` hardcoded to True (commit b1868da)

**Why:** the DR supplement (GPT-4o call in Pass 3) is cheap ($0.10) and always adds depth. No reason to conditionally skip. Removed from Pass 0a schema.

### 5.14 Prefect orchestration (not n8n)

**Why:** n8n's 25MB file limit, weak async polling, and lack of Python-native audio processing ruled it out for the audio stage. Architecture_v1 originally specified "Prefect for audio, n8n for everything else" but in practice the whole pipeline is Prefect. Architecture_v1 is stale on this.

### 5.15 FastAPI web upload (not rclone + Drive mount)

**Why:** rclone was the original design (per Infrastructure_Setup doc, stale). Actual choice: web upload from producers is simpler logistically — no Drive folder permissions to manage, no sync delays, producers upload at venue with mobile data if needed. Infrastructure_Setup doc is stale on this.

---

## 6. Known bugs, gaps, limitations

### 6.1 Data gaps

- **`runtime/reference/speakers.json`**: 202 speakers, **all `title/affiliation/bio` empty**. Speaker ID Pass 3 relies on bios for expertise matching. Expected accuracy degrades from 70–85% to 40–50% without bios. **Pre-Athens blocker** — bios must be populated before first production session.
- **`runtime/reference/sessions.skipped.json`**: 2 sessions with `venue: TBC` (Philosophical Speed-Dating Rave, How to Meet an Idiot). Either firm up venues in program or leave them skipped.
- **`runtime/flows/shared/council/council_config.json`**: version `dev_stub_v3_audience_sharpened`. Hand-written stubs for all 12 members; not derived from real persona-pipeline Derive output. Will be replaced with real Derive output from the rebuilt Phase B persona pipeline.
- **`$PROJECT_ROOT/inputs/voices/`** (for Athens: `../athens-2026/inputs/voices/`): 5 v3.10 Pass 0a artifacts on disk (plato, hannah_arendt, cleopatra, octopus, ibn_battuta) plus an in-progress Dostoevsky config. **All 12 voice configs are pending under Phase B** — Pass 0a itself is being redesigned (per `_workspace/planning/REBUILD_PLAN.md` §"Phase 0 — Intake · Pass 0a"; 7 changes including `editorial_rationale` field, `manual_grounding` unification, decoupling from full conference_context, domain-specific non-human grounding, plus Boddice integration). The existing configs are archaeology; they get regenerated under the redesigned Pass 0a along with the other 7 (Scheherazade, Whanganui, Marley, Audrey Tang, Peter Thiel, Ada Lovelace). Per Tier 3 (2026-04-20), this directory lives outside the code repo under PROJECT_ROOT.
- **`$PROJECT_ROOT/inputs/dossiers/`**: 0 of 12 Claude DR dossiers in the current tree. All 12 will be generated under the new Pass 0b template (PB#2 hybrid Jinja+LLM tailoring) once Phase B lands.
- **`_workspace/archive/runs/personas/_dr_prompts/`**: 3 v3.10 artifacts on disk (cleopatra, ibn_battuta, octopus). Same as voice configs — these are pre-Phase-B outputs that won't survive the redesigned Pass 0b. All 12 DR prompts get regenerated under Phase B's hybrid-tailored renderer.

### 6.2 Pipeline gaps

- **Voice Pipeline**: not built. Without it, persona cards can't produce runtime output. Downstream pipeline can't render. Microsite has no content. Everything from Night 1 downstream is blocked.
- **Phase 5 Cross-Persona QC**: not built. Tests distinctiveness across voices; could surface that e.g. Plato and Arendt sound too similar after their cards complete.
- **Night 2 exclusion filter (Provocateur)**: not implemented; simple pre-filter between Selection steps 1 and 4.
- **Continuity block generation**: not built; 1 API call per voice after Night 1/2 to produce 4-field summary.
- **Downstream pipeline**: Render/Publish/Curate/Deliver — all four stages unbuilt.
- **Closing-show pipelines**: theme identification, per-theme mapping, video pipeline — three passes unbuilt.
- **Microsite**: unbuilt.
- **Admin console**: unbuilt.

### 6.3 Documentation staleness

- **`_workspace/archive/specs/AI_Assembly_Architecture_v1.md`** (archived — stale): describes n8n orchestration (actual is Prefect); 2-step Voice Pipeline (briefing has 3); 2 nights (briefing has 3 + Day 4 goodbye); missing closing-show pipelines, Matrix A/B, newsletter delivery via Substack blurb.
- **`_workspace/archive/specs/AI_Assembly_Infrastructure_Setup.md`** (archived — stale): describes rclone/Drive mount + n8n Docker + file watcher (actual is FastAPI upload + pure Prefect + status.json state machine); pre-flight checklist references obsolete elements.

### 6.4 Code issues (minor)

- **`runtime/scratch/rerun_speaker_id_and_cleaning.py`**: development utility for re-running Speaker ID + Cleaning without paying AssemblyAI twice. Fine as-is but gitignored (`scratch/`).
- **`runtime/flows/shared/io.py#write_json_atomic`**: uses `tempfile.mkstemp` + cleanup on failure (good). Matches personas version.
- **`personas/flows/shared/clients.py#call_perplexity`**: guarded access to `data["choices"][0]["message"]["content"]`. `call_openai`: guarded empty choices check + JSON parse error surfacing. Both hardened.
- **`personas/flows/shared/node1c_fetch.py`**: SSRF-hardened (scheme restriction, RFC1918 block, 5MB cap, narrow exceptions).

### 6.5 Environmental dependencies

- **OpenAI quota**: was exceeded during Plato run (Pass 3 DR supplement fallback was not implemented at the time, mentioned in IMPLEMENTATION_AUDIT). Now hardcoded on by default; needs quota allowance for remaining voices.
- **Google API quota**: personas project had zero free-tier quota at one point (causing Pass 1b to be skipped and Pass 1-merge to fall back to single-source). Verify before batch persona runs.
- **Perplexity quota**: 500 queries/month on Pro plan; 12 voices = 12 queries, fine.

### 6.6 Open design questions (per Briefing v3.1)

- **Introduction location** for Day 1 (4 options; decision between Till and Matthias)
- **Program copy revision** for the AIssembly entry
- **Video production path** (live action / animation / stylised composite)
- **Day 4 goodbye voice** (which voice's final line closes the relationship)
- **Multilingual interpretation policy** (whether to flag interpreted quotes with `[interpreted]`)
- **Audience question mic separation** (recording-protocol change; worth raising with HoBB)
- **Cross-channel audio recording** (panel vs. audience on separate tracks would fix Q&A diarization merges)

---

## 7. Environment, dependencies, constraints

### 7.1 Required on every machine that runs the pipelines

- Python 3.12 (both venvs)
- `ffmpeg` (system package) — required for ingest normalization
- `ffprobe` (comes with ffmpeg) — required for ingest audio validation
- Git (for microsite content commits, when microsite is built)

### 7.2 API keys (unified `.env` at monorepo root)

| Key | Used by | Pre-conference / overnight / both | Notes |
|---|---|---|---|
| `ANTHROPIC_API_KEY` | Both | Both | Largest volume |
| `ASSEMBLYAI_API_KEY` | runtime only | Overnight | Transcription |
| `UPLOAD_APP_PASSWORD` | runtime ingest | Overnight | HTTP Basic Auth |
| `PERPLEXITY_API_KEY` | personas only | Pre-conference | ~$5/voice for Pass 1a |
| `GOOGLE_API_KEY` | personas only | Pre-conference | Gemini broad scan + Pass 7a fallback |
| `OPENAI_API_KEY` | personas only | Pre-conference | Pass 7a primary + Pass 3 DR supplement |
| Optional overrides | — | — | CLAUDE_MODEL, TRANSCRIPTION_CLAUDE_MODEL, RESEARCHER_CLAUDE_MODEL, PROVOCATEUR_CLAUDE_MODEL, PROVOCATEUR_THINKING, RESEARCHER_THINKING, PROVOCATEUR_FORMULATION_BATCH, TRANSCRIPTION_SPEAKER_ID_MODEL, TRANSCRIPTION_CACHE |

Future keys (when components build): `SUNO_API_KEY` (Marley renders), `GITHUB_TOKEN` (microsite commits), `VERCEL_TOKEN` (if auto-deploy), email tool credentials (Substack/HoBB newsletter).

### 7.3 Version pins

- `anthropic==0.94.1` (both venvs) — separate venvs for dependency isolation, same Anthropic version
- `assemblyai==0.59.0` (runtime only)
- `prefect==3.6.26` (both)
- `google-genai==1.73.1` (personas only)
- `openai==2.31.0` (personas only)
- `fastapi==0.135.3` (runtime only)
- `jinja2==3.1.6` (personas only)

### 7.4 VM target (Hetzner CX22/CX32)

- Ubuntu 24.04 LTS
- 2–4 vCPU, 4–8 GB RAM, ≥100 GB SSD
- `ingest` system user (nologin)
- `/opt/ai-assembly/` install root (matches monorepo structure: `runtime/`, `personas/`, `docs/`, `.env`)
- Caddy reverse proxy + Let's Encrypt auto TLS
- systemd service with hardening directives
- ufw: 22/80/443 only
- No admin console user yet; planned for future

### 7.5 Cost estimates (per spec + validation)

| Component | Per-unit cost | Volume | Total |
|---|---|---|---|
| Persona Pipeline per voice | $14–18 | 12 voices | $170–220 |
| + Claude Batch API (50% off Claude portion) | ~$115–150 |
| Transcription (per night, ~6-9 sessions) | $4–6 | 3 nights | $12–18 |
| Researcher (per night, Opus + thinking) | $15–25 | 3 nights | $45–75 |
| Provocateur (per night) | $15–25 | 3 nights | $45–75 |
| Voice Pipeline (per night, ~36 Step1 + 12 Step2) | est $20–40 | 3 nights | $60–120 |
| Downstream (Suno + Curate) | $0.50–2.50 + $0.50 | 2 nights curate | $2–6 |
| **Total infrastructure + API for full Athens run** | | | **~€200–350** |

---

## 8. Pre-Athens critical path

In the sequence the user intends to work:

### Phase A — Persona Pipeline validation (now → +1 day)

- [ ] Re-audit Plato's assembled card against the 37-field spec. Check metadata block completeness, register violations, coherence between fields, realism of smoke_test_chains.
- [ ] Re-read Arendt's 02_passes output; complete any passes that failed or didn't run; produce final assembled card + provocateur_profile.
- [ ] Spot-check Cleopatra's Pass 0a output (review doc + voice config); if it reads well, proceed to DR prompt generation (Pass 0b), then human DR session (60–120 min at claude.ai), then full pipeline run.
- [ ] Spot-check Octopus similarly.
- [ ] Compare the 4 cards side-by-side: do they actually sound different? If Plato and Arendt read similarly, that's a Phase 5 Cross-Persona QC finding (currently caught manually).

### Phase B — Complete persona cards for 3–4 voices (+1 → +1 week)

Candidates, in likely order of tractability:
1. Cleopatra (hostile-sources branch; tests the most complex prompt branching)
2. Octopus (non-human organism; tests anti-anthropomorphisation)
3. Bob Marley (musical voice; tests `corpus_constraint: "lyrics — describe patterns only"`)
4. Dostoevsky or Ada Lovelace (well-documented; baseline check)

Each: Pass 0a (15 min + review) → Pass 0b (seconds) → DR session (60–120 min human-in-loop at claude.ai) → run_persona_pipeline (60–90 min automated) → human review (30–60 min).

Total per voice: ~3–4 hours.

### Phase C — Finish persona pipeline (+1 → +3 weeks)

- Remaining 8 voices × 3–4 hours = ~24–32 hours
- Build Phase 5 Cross-Persona QC (~1 day)
- Run Phase 5 after all 12 cards
- Address any distinctiveness issues flagged by QC
- Update `runtime/flows/shared/council/council_config.json` with real Derive output (tooling: script to assemble members array from all `provocateur_profile.json` files; natural first admin-console feature but can be a one-off script for now)

### Phase D — Voice Pipeline (+3 weeks → +4 weeks)

- Spec Step 3 Amendment (~1 day: system prompt template + input format + output format + integration)
- Build Steps 1+2: Prefect flow, parallel per-voice, system prompt assembly from persona card, optional validation (anachronism + constitutional)
- Build Step 3: inter-voice amendment; requires theme-graph (which voices share which themes)
- Integration test: run full voice pipeline against dev_msc_test Provocateur output
- Build Night 2 continuity generation
- Budget: ~1 week focused work

### Phase E — Microsite (+4 weeks → +5 weeks, parallelisable with D)

- Design prototype in Lovable or v0 (navigation pattern, voice-then-night vs night-then-voice)
- Production codebase in Cursor/Claude Code (Astro preferred per spec; Next.js also acceptable)
- Content schema (night-N.json, per-voice artifact files, shader integration for Octopus, Suno audio hosting for Marley)
- Vercel or Netlify deploy with auto-rebuild on commit
- Placeholder content for test runs
- "Holding page" ready for Night 1 failure fallback

### Phase F — Readout + closing show (+5 weeks → +6 weeks)

- Spec theme identification pass (1 day)
- Spec per-theme mapping pass + Matrix visualization (1–2 days, including visual template design)
- Spec video pipeline pass (1 day)
- Build all three passes (~3–5 days)
- Build Matrix-pair visualization template (static HTML/SVG that renders per-theme data)
- Handoff protocol to closing-show production team (video editors for snippet production)
- Human editorial pass tooling (where the 1–2 hour polish happens)

### Phase G — VM + console/UI (+6 weeks → +7 weeks)

- Provision Hetzner VM (~15 min)
- Install stack per deploy/README (Ubuntu 24.04, Python 3.12, Caddy, ffmpeg)
- Clone monorepo to `/opt/ai-assembly/`, create both venvs, populate `.env`
- Install systemd unit + Caddy + firewall + journald cap
- Smoke test: ingest + fake flow + real session
- Build admin console (FastAPI app mirroring ingest architecture)
  - Route for each pipeline stage
  - Subprocess spawning + status.json pattern per ingest
  - Council sync button (reads persona runs → writes council_config)
  - Log tail viewer
- Dry Run 1 (T–2 weeks before Athens): plumbing test
- Dry Run 2 (T–1 week): full pipeline against real HoBB panel
- Recording protocol briefing to HoBB A/V team

### Phase H — Pre-conference logistics (+7 weeks → Athens)

- Populate `runtime/reference/speakers.json` with bios (blocking for Speaker ID quality)
- Moderators briefed to introduce panelists by full name
- Walking-session participants briefed to self-introduce
- AssemblyAI custom vocabulary populated with all panelist names
- HoBB email tool identified + API credentials (Substack likely)
- Greek SIM for Athens
- Printouts: all pipeline specs, this CURRENT_STATE.md, runbook, filename convention for A/V
- Final full test from hotel Wi-Fi
- Backup person has SSH key + `.env` copy in 1Password

---

## 9. Risks and mitigations

In decreasing order of "if this goes wrong, how bad is it?"

| Risk | Mitigation | Notes |
|---|---|---|
| Voice Pipeline not built by Athens | Drop Step 3 Amendment, ship Steps 1+2 only; briefing is robust to this per Briefing v3.1's "Step 3 is new architecture" flag | Would reduce deliberative character but keep the experiment intact |
| Persona cards not all complete | Ship with 8–10 cards; drop 2–4 voices; adjust council_config members array | Weakens the panel composition but better than no Assembly |
| Closing show too ambitious | Ship mapped read-through only; drop video snippets | Video is nice-to-have; mapped read-through is the structural argument |
| AssemblyAI diarization fails on key session | Speaker ID flags for human review; human 15–30 min pass catches it | Already validated on MSC test sessions |
| API quota exhaustion mid-Athens | Pre-test all keys in final week; have backup keys ready; Anthropic Batch API for non-urgent | Dominant risk is OpenAI (Plus plan has query caps on full-model requests) |
| VM dies mid-conference | Laptop fallback tested pre-Athens; `.env` in 1Password; repo cloned locally | Per Infrastructure_Setup §Failure fallback |
| Audio recording quality bad | Normalized 96 kbps mono is forgiving; speaker-ID 5-pass catches most issues; human review queue catches the rest | 15–30 min human review per night |
| Cleopatra persona produces sanitised output on ethnicity | Voice-specific warnings in her config (no flattening to pop culture readings); Pass 7a register + anachronism checks | Monitor during her card build |
| Thiel persona carries legal risk | Needs review separate from architectural spec | Open question per Briefing v3.1 |
| Audience doesn't engage | Provotype is designed to surface this as a finding; Day 4 goodbye publishes regardless | "Indifference is failure" per Briefing v3.1; build the experiment anyway |

---

## 10. Housekeeping

### 10.1 How to update this doc

- On any significant state change, update the relevant section in the same commit.
- If Phase A completes: move items from §8 Phase A to §1 (what exists) or §6 (known gaps closed).
- If a spec becomes stale: flag in §6.3 and in `docs/README.md`.
- If a new architectural decision is made: add to §5 with rationale.
- If a new data contract is introduced: add to §4.
- Bump the `Last updated` date at top.

### 10.2 Commit convention

For this doc, prefix commits with `state:` — e.g., `state: Phase A complete, 4 persona cards validated`. Keeps state-tracking commits distinguishable from feature commits.

### 10.3 Related docs

- `docs/README.md` — staleness banner for the spec set
- `docs/AI_Assembly_Briefing_v3_1.md` — the target-state document
- `_workspace/archive/fix-plans/IMPLEMENTATION_AUDIT_v3_7.md` — pre-Phase-3/4 audit (historical; superseded by this doc's §1–§3)
- `personas/HANDOFF.md` — persona → runtime handoff contract (still current)
- `personas/flows/shared/prompts/persona_pass_7b_smoke_test.md` — header comment documents the "smoke_test_chains are not runtime few-shot exemplars" rule. Also see `personas/HANDOFF.md` for the full rationale.
- `_workspace/archive/fix-plans/PROPOSED_pipeline_doc_change.md` — working doc of proposed pipeline changes (archived; absorbed into current specs)

---

*End of CURRENT_STATE.md. This document should be read alongside the Briefing v3.1 as the most current picture of the system. When in doubt between them: Briefing describes what we're building; this describes where we are.*
