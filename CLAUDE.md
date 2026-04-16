# AI Assembly — Claude context

## Repo layout

- `runtime/` — FastAPI ingest app (`runtime/ingest/`) + Prefect flows (`runtime/flows/`). Runs on a VM; also runnable locally as standalone scripts.
- `personas/` — Persona Pipeline. Builds the 37-field voice cards (`provocateur_profile.json`) that the Provocateur flow consumes. Runs on a local machine before the event.
- `docs/` — canonical specs, briefing documents, and pipeline references. See `docs/README.md` for staleness status of each file.
- `.env` — shared secrets at repo root (not committed). Both sub-trees load from `../.env` (one directory above their own root).

## Separate venvs required

Runtime and personas pin different Anthropic SDK versions:
- `runtime/`: `anthropic==0.95.0` (or latest at install time)
- `personas/`: `anthropic==0.94.1` (pinned — different message API surface)

Always activate the correct venv for the sub-tree you're working in.

## load_dotenv pattern

All scripts load `.env` from the **monorepo root** (`REPO_ROOT.parent / ".env"` or `_REPO_ROOT.parent / ".env"`). Exception: `personas/flows/shared/clients.py` uses bare `load_dotenv()` intentionally — it walks up from CWD and finds the root `.env` automatically when scripts are run from the monorepo root or the `personas/` dir.

## Cross-repo handoff (personas → runtime)

The personas pipeline produces a `provocateur_profile.json` per voice (37 fields, including `voice_name`, `system_prompt`, `council_mode`, and thematic embeddings). These feed into `runtime/reference/council_config.json` as the `members` array before the Provocateur flow runs each night.

## Where specs live

All canonical pipeline specs are in `docs/`:
- `AI_Assembly_Briefing_v2.md` — the authoritative project briefing (as of 2026-04-16)
- `AI_Assembly_Persona_Card_v2.md` — the 37-field card template
- `AI_Assembly_Persona_Pipeline_v3_7.md` — persona build pipeline
- `AI_Assembly_Researcher_Pipeline.md` — researcher extraction and grouping
- `AI_Assembly_Provocateur_Pipeline.md` — triage, selection, formulation, packaging
- `AI_Assembly_Transcription_Pipeline.md` — audio to clean transcript pipeline
- `AI_Assembly_Voice_Pipeline.md` — voice pipeline Steps 1+2 (Step 3 unspecified)
- `AI_Assembly_Architecture_v1.md` — STALE (see docs/README.md)
- `AI_Assembly_Infrastructure_Setup.md` — STALE (see docs/README.md)

Working/WIP documents are in `runtime/notes/` and `personas/notes/`.
