# AI Assembly — Runtime

This is the `runtime/` sub-tree of the ai-assembly monorepo. See the
top-level [README.md](../README.md) for the authoritative orientation
and run instructions.

## Local structure (code — this repo)

- `ingest/` — FastAPI upload app (producers upload audio here)
- `flows/` — Prefect flow code, one file per pipeline stage
  - `transcription_flow.py` — Stage 0 (audio → clean transcript)
  - `researcher_flow.py` — Stage 1 (extraction + themed grouping)
  - `provocateur_flow.py` — Stage 1b (triage, selection, formulation, packaging)
  - `shared/` — code reused across flows (io, prompts, project_root resolver,
    council/README.md — the council_config.json itself is project data)
- `reference/session_template.json` — schema template (code-level; the
  `sessions.json`/`speakers.json` themselves are project data)
- `scripts/` — sessions/speakers regeneration
- `notes/` — WIP working documents

## Project data (PROJECT_ROOT — separate dir)

Per Tier 3 (2026-04-20), per-project data lives **outside this repo**. The
runtime resolves `PROJECT_ROOT` at startup (via `ingest.config`) from:

1. `--project` CLI arg on CLI-driven flows (todo — currently via env only)
2. `AI_ASSEMBLY_PROJECT_ROOT` environment variable (typically set in the
   shared `../.env`)

Layout under `PROJECT_ROOT`:

```
<PROJECT_ROOT>/
├── reference/
│   ├── sessions.json           # WBBF-style program data (per project)
│   ├── speakers.json           # speaker roster + bios
│   └── sessions.skipped.json   # opt-outs
├── council_config.json         # 12 members derived from persona cards
├── inputs/…                    # shared with the personas pipeline
└── runs/
    └── <run_id>/
        ├── 01_transcription/<session>/
        ├── 02_researcher/
        └── 03_provocateur/
```

## Running a stage locally

From the `runtime/` directory, with venv activated and
`AI_ASSEMBLY_PROJECT_ROOT` set (either in `../.env` or your shell):

```bash
source venv/bin/activate

# Transcription (one session) — paths can be absolute or $-expanded
OUTPUT_DIR="$AI_ASSEMBLY_PROJECT_ROOT/runs/<run>/01_transcription/<session>" \
  python flows/transcription_flow.py \
    "$AI_ASSEMBLY_PROJECT_ROOT/runs/<run>/01_transcription/<session>/audio.m4a" \
    "$AI_ASSEMBLY_PROJECT_ROOT/runs/<run>/01_transcription/<session>/session.json"

# Researcher (all sessions in a run)
python flows/researcher_flow.py "$AI_ASSEMBLY_PROJECT_ROOT/runs/<run>"

# Provocateur (all sessions in a run)
python flows/provocateur_flow.py "$AI_ASSEMBLY_PROJECT_ROOT/runs/<run>"
```

## Setup

```bash
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

API keys live in `../.env` at the monorepo root — not in `runtime/.env`.
`AI_ASSEMBLY_PROJECT_ROOT` lives there too.

## Deployment

See `ingest/deploy/README.md` for VM deployment (systemd + Caddy).

## Current status

See `../docs/CURRENT_STATE.md` for the authoritative status snapshot.
