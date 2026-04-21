# Runtime Review — 2026-04-20

## Context

User asked for a thorough review of `code/runtime/` — folder structure, files, spec, docs, prompts, code mapping. A first pass that read `runtime/` in isolation mis-flagged several items as gaps because it didn't account for the wider repo conventions (Tier 3 project separation, specs-in-`docs/`, tests-as-roster-integration). After a second orientation across the umbrella, this document captures the corrected review.

**Scope:** `code/runtime/` as it stands on branch `phase-b-rebuild` at 2026-04-20. Voice Pipeline build is out of scope (Phase D per `docs/CURRENT_STATE.md` §8). No `personas/` review.

## Runtime structure as-built

```
runtime/
├── ingest/                     FastAPI upload app (producers) — built + tested
│   ├── app.py, pipeline.py, auth.py, config.py, sessions.py
│   ├── static/, templates/     web UI
│   ├── deploy/                 systemd unit + Caddyfile + deploy README
│   └── tests/                  test_app.py, test_pipeline.py, test_sessions.py, fake_transcription_flow.py
├── flows/
│   ├── transcription_flow.py   Stage 0 — AssemblyAI + 5-pass speaker ID + cleaning
│   ├── researcher_flow.py      Stage 1 — extract → KJ Round 1 → KJ Round 2
│   ├── provocateur_flow.py     Stage 1b — triage (1A+1B) + selection + formulation + packaging (5 stages, 1368 lines)
│   ├── voice/README.md         Stage 2 build notes — NOT YET BUILT
│   └── shared/
│       ├── io.py, project_root.py
│       ├── download_session.sh yt-dlp dev utility — mis-located (see below)
│       ├── council/README.md + council_config.json (dev_stub)
│       └── prompts/            8 active + 4 archived
├── reference/session_template.json   schema template, not project data
├── scripts/                    generate_sessions_json.py, generate_speakers_json.py
├── requirements.txt, README.md, .env.example, .gitignore
└── venv/                       runtime-only deps
```

Specs live in `code/docs/` (canonical): `AI_Assembly_Transcription_Pipeline.md`, `AI_Assembly_Researcher_Pipeline.md`, `AI_Assembly_Provocateur_Pipeline.md`, `AI_Assembly_Voice_Pipeline.md` (partial; Step 3 unspecified). Status snapshot in `docs/CURRENT_STATE.md`. Project data (runs, rosters, council_config) lives under `$PROJECT_ROOT` outside the repo per Tier 3.

## Prompt inventory

| Stage | Prompt file | Role |
|---|---|---|
| Transcription | `transcription_cleaning.md` | Faithful ASR repair; no paraphrase. |
| Transcription | `transcription_speaker_id.md` | 5-pass speaker attribution (explicit cue → role → expertise → confidence → per-turn sanity check). |
| Researcher | `researcher_extraction.md` | Atomic positions + reframings + open questions per session; consumes `verify_markers`. |
| Researcher | `researcher_clustering.md` | KJ Round 1 — minimal `{ref, extraction, context}` input to prevent session-prefix grouping shortcut. |
| Researcher | `researcher_theming.md` | KJ Round 2 — groups clusters into themes at continuity level. |
| Provocateur | `provocateur_triage_flags.md` | Stage 1B — per-theme editorial signals (worth_surfacing, audience_friction, fault_line). |
| Provocateur | `provocateur_triage_voice.md` | Stage 1A — per-voice activation/stretch tagging across themes. |
| Provocateur | `provocateur_formulation.md` | Stage 3 — per-pair PROPOSITION/QUESTION formulation against 5-condition proposition test. |

**`_archive/` lineage** (recovered by reading headers):

| Archived | Replaced by | Reason |
|---|---|---|
| `provocateur_triage_v1_combined.md` | `provocateur_triage_flags.md` + `provocateur_triage_voice.md` | v1 combined editorial flags and per-voice ranking in one prompt; v2 split them so theme-level editorial signals are independent of voice-specific activation. |
| `provocateur_selection_v1_llm.md` | Python Stage 2 in `provocateur_flow.py` | Decision §5.5 in CURRENT_STATE — Selection is combinatorial scoring, not editorial judgment. Python is instant, deterministic, all knobs tunable in `council_config.json`. LLM was slow, non-reproducible, opaque. |
| `provocateur_formulation_v1_per_theme.md` | `provocateur_formulation_v2_per_pair_draft.md` → `provocateur_formulation.md` | Decision §5.6 — one formulation per theme forced generic altitude to fit all assigned voices. Per-pair calls let each formulation aim at one voice's specific territory. |
| `provocateur_formulation_v2_per_pair_draft.md` | `provocateur_formulation.md` | Draft iteration of the per-pair shape; production version tightened proposition test to 5 conditions. |

## Code mapping (three entry points)

**1. HTTP ingest** (`ingest/app.py`): producer POSTs audio via authed `/upload` → `pipeline.py` ffmpeg-normalizes to 96kbps mono AAC → spawns detached subprocess `python flows/transcription_flow.py <audio> <session.json>` → UI polls `status.json` (received → normalizing → transcribing substates → done/error). Reconcile-on-startup scans `runs/` for orphaned PIDs.

**2. Researcher CLI** (`flows/researcher_flow.py <run_dir>`): loads all `01_transcription/*/session_package.json` → per-session extraction → global merge with namespaced IDs (`session_id:NNN`) → KJ Round 1 clustering → KJ Round 2 theming → writes `02_researcher/{session}_extractions.json`, `all_extractions.json`, `grouping.json`.

**3. Provocateur CLI** (`flows/provocateur_flow.py <run_dir>`): loads `02_researcher/grouping.json` + `council_config.json` → Stage 1A (12 parallel per-voice triage calls, incremental checkpoint per voice) → Stage 1B (1 theme-flags call) → Stage 2 Python selection (9 deterministic steps, 8 tunable knobs) → Stage 3 parallel per-pair formulation (batched per `PROVOCATEUR_FORMULATION_BATCH`) → Stage 4 packaging (two-view briefings: `narrative_briefing` markdown + `full_theme_record` structured) → writes `03_provocateur/{triage_*.json, selection.json, formulations/, briefings/}`.

Shared code genuinely reused: `io.py` (atomic writes, `load_session_package` turn_index normalization, prompt loader), `project_root.py` (identical to personas counterpart by design — separate venvs). Council schema doc lives in `flows/shared/council/README.md`, the natural place since only Provocateur loads it.

## Observations

### Clean mappings (what fits well)

- **Stage-per-file** mirrors the three canonical specs 1:1 (Transcription, Researcher, Provocateur Pipeline markdown).
- **Prompt lineage** is coherent: 8 active prompts named by stage, 4 archived with clear replacement story.
- **Ingest self-containment** — no cross-cutting deps into flows; subprocess boundary is clean. Only `ingest/tests/` holds runtime tests.
- **Tier 3 project separation** (2026-04-20) consistently applied — repo holds code + schema template; runs + rosters + council_config live under `$PROJECT_ROOT`.
- **Checkpoints-as-cache** (CURRENT_STATE §5.8): provocateur and transcription write incrementally; restart resumes without `CACHE=1` flag.

### Minor doc-hygiene gaps (optional)

- `_archive/` prompts have no README stating retirement reason; lineage is recoverable only by reading each header against current counterparts.
- `scripts/generate_sessions_json.py` and `scripts/generate_speakers_json.py` lack module docstrings; purpose, inputs, outputs not stated in-file.
- `ingest/pipeline.py` writes `status.json` consumed by UI templates; schema is not documented near the writer (no dataclass, no comment block).
- `CURRENT_STATE.md` §5.10 says "`runtime/flows/voice/README.md` was planned but never built" but the file exists with current build notes — CURRENT_STATE is slightly stale on this one line.
- `flows/shared/download_session.sh` is a standalone yt-dlp + ffmpeg dev utility (fetch a YouTube panel at 96kbps mono AAC for local pipeline testing). It is not imported by any flow and not "shared" in any code-library sense. Natural home is `scripts/` alongside `generate_sessions_json.py` and `generate_speakers_json.py`. Low-stakes move; header docstring is already good.

### Deferred considerations (defer past Phase L)

- `provocateur_flow.py` is 1368 lines covering 5 stages. Splitting into `triage_flow.py`, `selection.py`, `formulation_flow.py`, `packaging.py` would match the spec's shape, but churn risk on `phase-b-rebuild` (~34 commits ahead of main) argues against doing it now.
- `load_prompt(name)` in `flows/shared/io.py:95` takes a string name (`{name}.md` under `_PROMPTS_DIR`). A filename rename surfaces only at runtime as `FileNotFoundError` — not silent, but not caught by static checks either. A typed `PROMPTS` registry would harden the coupling; low priority.
- No flow-level unit tests. Convention is roster-integration against `~/Desktop/AI Assembly/archive/runs/runtime/dev_msc_test/`; that works for the current team size but would need to be restated before growing the contributor set.

## Withdrawn concerns (from the first-pass runtime-only review)

Capturing these explicitly so future reviews don't re-raise them:

- **"Voice Pipeline stubbed"** — Phase D per CURRENT_STATE §8; spec partial by design (Step 3 Amendment unspecified pending Steps 1+2 reference output); `flows/voice/README.md` correctly captures wiring decisions (especially the `smoke_test_chains` ban) as build notes.
- **"PROJECT_ROOT duplicated across two modules"** — intentional per `CLAUDE.md` §Tier 3. Separate venvs, no shared package, modules identical-by-design.
- **"runtime has no spec"** — specs live in `code/docs/AI_Assembly_{Transcription,Researcher,Provocateur,Voice}_Pipeline.md`.
- **"runs/ missing from runtime"** — moved to `$PROJECT_ROOT/runs/` and `~/Desktop/AI Assembly/archive/runs/` in Tier 3 cleanup (2026-04-20). Runtime holds only `reference/session_template.json` as a schema template.
- **"Flow-level test gap"** — `ingest/tests/` covers the web surface. Flow tests are roster-integration against `archive/runs/runtime/dev_msc_test/`, not unit tests. Not a structural gap given current team/convention.

## Neatness assessment

The runtime folder maps cleanly to the three-stage architecture documented in `docs/`. No orphaned code, no duplication, no dead weight. Items worth touching are small doc-hygiene adds (3 items above); structural refactors should wait until after Phase L merges. Promote items from this document into `OPEN_ITEMS.md` when remediation is scheduled.
