# AI Assembly — Runtime

This is the `runtime/` sub-tree of the ai-assembly monorepo. See the
top-level [README.md](../README.md) for the authoritative orientation
and run instructions.

## Local structure

- `ingest/` — FastAPI upload app (producers upload audio here)
- `flows/` — Prefect flow code, one file per pipeline stage
  - `transcription_flow.py` — Stage 0 (audio → clean transcript)
  - `researcher_flow.py` — Stage 1 (extraction + themed grouping)
  - `provocateur_flow.py` — Stage 1b (triage, selection, formulation, packaging)
  - `shared/` — code reused across flows (io, prompts, council config)
- `reference/` — frozen inputs (sessions.json, speakers.json, session_template.json)
- `runs/` — per-run outputs (gitignored)
- `scripts/` — sessions/speakers regeneration
- `notes/` — WIP working documents

## Running a stage locally

From the repo root, with venv activated:

```bash
source venv/bin/activate

# Transcription (one session)
OUTPUT_DIR=runs/<run>/01_transcription/<session> python flows/transcription_flow.py \
  runs/<run>/01_transcription/<session>/audio.m4a \
  runs/<run>/01_transcription/<session>/session.json

# Researcher (all sessions in a run)
python flows/researcher_flow.py runs/<run>

# Provocateur (all sessions in a run)
python flows/provocateur_flow.py runs/<run>
```

## Setup

```bash
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

API keys live in `../.env` at the monorepo root — not in `runtime/.env`.

## Deployment

See `ingest/deploy/README.md` for VM deployment (systemd + Caddy).

## Current status

See `../docs/CURRENT_STATE.md` for the authoritative status snapshot.
