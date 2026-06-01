# AI Assembly — Runtime

This is the `runtime/` sub-tree of the ai-assembly monorepo. See the
top-level [README.md](../README.md) for overall orientation and
[STATE.md](../STATE.md) for current status.

The runtime is the overnight pipeline that turns the day's recorded audio
into published voice artifacts. It ran end-to-end across all three Athens
2026 nights (May 7–9), producing 13 dossiers + 30 per-voice pages.

## Pipeline stages (6 flows + orchestrator)

```
audio upload  →  transcription  →  researcher  →  provocateur  →  voice  →  editor  →  publish
   (HTTP)       (per-session,        (themes        (per-voice    (per-voice  (per-theme  (microsite-
                ingest auto-fires)   from           briefings)    artifacts)  dossiers)   ready
                                    extractions)                                          JSON)
```

| Module | File | Notes |
|---|---|---|
| Transcription | `flows/transcription_flow.py` | AssemblyAI Universal-3 Pro + multi-pass speaker attribution. Reflections (vendor JSON) preprocess via `scripts/reflections_to_session_package.py`. |
| Researcher | `flows/researcher_flow.py` | Opus 4.7 + adaptive thinking. Extracts atomic positions, groups via KJ clustering. |
| Provocateur | `flows/provocateur_flow.py` | 5-stage: Triage A + B (parallel) → Selection (Python) → Formulation (per-pair) → Packaging. Deployment-context block added 2026-05-05 (`cbcdf82`). |
| Voice Pipeline | `flows/voice_flow.py` + `flows/voice/*.py` | Steps 1 (private reasoning) + 2 (first-draft artifact) + Continuity (Nights 2/3). Step 3 SKIPPED for Athens per OPEN_ITEMS A1 (module preserved for post-Athens re-add). Field routing per `docs/AI_Assembly_Voice_Pipeline.md`. |
| Editor | `flows/editor_flow.py` + `flows/editor/*.py` | Tim Leberecht as 13th Assembly member. Per-theme dossier composition. Deployment-context override at `<run_dir>/_dossier_deployment_context.md` controls per-night register. |
| Publish | `flows/publish_flow.py` + `flows/voice/publish.py` | Cross-pipeline aggregation. Produces `<PROJECT_ROOT>/published_artifacts/dossiers/night_N/` + `nights/night_N/<voice>.json` + `voices/<voice>_multi_night.json`. |
| Orchestrator | `scripts/overnight_orchestrator.py` | Polls filesystem; fires each downstream stage when inputs ready. Coarse-grained, idempotent, restart-safe. 22 trigger-path tests. **Athens production used manual per-stage fires, not the orchestrator** — see `_workspace/planning/runtime/HANDOFF_2026_05_29_ATHENS_COMPLETE.md` for why. |

`shared/` carries code reused across flows (io, prompts, project_root resolver, council config). `reference/session_template.json` is the schema template; the actual `sessions.json`/`speakers.json` live under `PROJECT_ROOT/reference/`.

## Project data (PROJECT_ROOT — separate dir)

Per Tier 3 (2026-04-20), per-project data lives **outside this repo**. Both pipelines resolve `PROJECT_ROOT` via:

1. `--project <path>` CLI arg
2. `AI_ASSEMBLY_PROJECT_ROOT` env var (typically in `../.env`)
3. **Hard fail** — no silent default

Layout under `PROJECT_ROOT`:

```
<PROJECT_ROOT>/                                  # e.g. ../projects/athens-2026/
├── conference_facts.json                        # at root, NOT under inputs/
├── audience_profile.json
├── panel_roster.json
├── council_config.json                          # runtime artifact
├── reference/
│   ├── sessions.json                            # program data
│   ├── speakers.json
│   └── sessions.skipped.json
├── voices/<slug>/                               # personas pipeline output
│   ├── 07_persona_card_assembled.json           # consumed by voice_flow
│   └── 06_derive/01_provocateur_profile.json    # consumed by council_config wiring
├── runs/
│   └── <run_id>/                                # e.g. athens_night_1
│       ├── 01_transcription/<session>/
│       ├── 02_researcher/
│       ├── 03_provocateur/briefings/
│       ├── 04_voice/{step1_detailed_responses, step2_first_draft_artifacts, validation}/
│       └── 05_editor/dossiers/
└── published_artifacts/                         # cross-run, cross-night
    ├── dossiers/night_N/
    ├── nights/night_N/<voice>.json
    └── voices/<voice>_multi_night.json
```

## Running flows

Each flow takes a run directory and is internally idempotent (resume from disk on restart):

```bash
cd runtime
source venv/bin/activate
export AI_ASSEMBLY_PROJECT_ROOT="../projects/athens-2026"

# Manual stage-by-stage (Athens production pattern):
python flows/transcription_flow.py "$AI_ASSEMBLY_PROJECT_ROOT/runs/<run>/01_transcription/<session>/audio.m4a" \
                                    "$AI_ASSEMBLY_PROJECT_ROOT/runs/<run>/01_transcription/<session>/session.json"
python flows/researcher_flow.py     "$AI_ASSEMBLY_PROJECT_ROOT/runs/<run>"
python flows/provocateur_flow.py    "$AI_ASSEMBLY_PROJECT_ROOT/runs/<run>"
python flows/voice_flow.py          "$AI_ASSEMBLY_PROJECT_ROOT/runs/<run>" --night 1 --skip-step3
python flows/editor_flow.py         "$AI_ASSEMBLY_PROJECT_ROOT/runs/<run>" --night 1
python flows/publish_flow.py        "$AI_ASSEMBLY_PROJECT_ROOT/runs/<run>" --night 1

# Or run unattended:
python scripts/overnight_orchestrator.py --night 1
```

For the full operational picture — what each stage reads/writes, where every file lives, failure modes, manual intervention — see [`../docs/AI_Assembly_Runtime_Lifecycle.md`](../docs/AI_Assembly_Runtime_Lifecycle.md).

## Setup

```bash
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

API keys + `AI_ASSEMBLY_PROJECT_ROOT` live in `../.env` at the monorepo root (not in `runtime/.env`).

## Deployment

VM-provisioning spec at [`../docs/AI_Assembly_Infrastructure.md`](../docs/AI_Assembly_Infrastructure.md); ingest deploy checklist at [`ingest/deploy/README.md`](ingest/deploy/README.md). **Note:** the VM was specified but not actually provisioned for Athens 2026 — operator ran from laptop (see OPEN_ITEMS B10).

## Current status

- **[`../STATE.md`](../STATE.md)** — one-glance entry point (post-Athens)
- **[`../CLAUDE.md`](../CLAUDE.md)** — state block at top + scaffolding
- **[`../_workspace/planning/runtime/OPEN_ITEMS.md`](../_workspace/planning/runtime/OPEN_ITEMS.md)** — v4.1 open items (none Athens-blocking)
- **[`../_workspace/planning/runtime/HANDOFF_2026_05_29_ATHENS_COMPLETE.md`](../_workspace/planning/runtime/HANDOFF_2026_05_29_ATHENS_COMPLETE.md)** — Athens-complete handoff
