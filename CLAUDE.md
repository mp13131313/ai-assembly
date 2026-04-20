# AI Assembly — Claude context

## Current branch state (2026-04-19)

Active branch: `phase-b-rebuild` (~34 commits ahead of `main`, not yet merged). The v3.10 persona pipeline is being replaced by a chunked Pass 1.1–1.7 architecture with Boddice biocultural rubrics + Pydantic schemas + Position-C DR-prompt tailoring. Pass 1a validated on Dostoevsky; Phase L (first-voice Plato run) is the next gate. `_workspace/planning/OPEN_ITEMS.md` is the authoritative pickup doc.

If you land fresh, read `OPEN_ITEMS.md` before the v3.10 pipeline spec — otherwise you'll build the wrong mental model.

## Repo layout

Four categories:

- `docs/`, `runtime/`, `personas/` — **production** slice. Current specs, running code, canonical pipeline. In scope for every code review and VM deploy.
- `research/` — **preserved grounding**. Deep Research artifacts that ground architecture decisions. Not deletable.
- `_workspace/planning/` — **forward-looking design**. Active docs for unbuilt work (Phase B rebuild plan, binding decisions). Promoted to `docs/` when the work lands.
- `_workspace/archive/` — **historical detritus**. Executed fix plans, stale specs, session artifacts, run artifacts. Eligible for pruning. **Out of scope for code reviews and VM deploys by default — mention it explicitly if you want Claude to look here.**
- `.env` — shared secrets at repo root (not committed). Both sub-trees load from `../.env` (one directory above their own root).

## Orientation reading order

For a fresh Claude session that needs to understand the project:

1. `CLAUDE.md`, `README.md` (this file + top-level — repo conventions)
2. `docs/README.md` (staleness index for all canonical specs)
3. `docs/CURRENT_STATE.md` (authoritative status snapshot — what exists, what's specified-but-not-built, what's not yet specified)
4. `docs/AI_Assembly_Briefing_v3_1.md` (project source of truth)
5. `_workspace/planning/` — read every file in full (small, active, binding design docs for unbuilt work)
6. The newest file in `_workspace/archive/session-artifacts/` (one-doc guided tour from the prior session — sort by date in filename)
7. `docs/AUDIENCE_BRIEF.md`, `docs/LLM_CALL_INVENTORY.md`, `docs/references.md` (cross-cutting reference)
8. Other `docs/AI_Assembly_*_Pipeline.md` and `runtime/` + `personas/` code by area, as the task requires

Stop after step 6 unless the task demands more — that's ~30–45 min of working knowledge. Then ask the user for the specific task.

If a session-artifact references a fix-plan or run artifact in `_workspace/archive/`, read it then. Otherwise treat `_workspace/archive/` as cold storage per the §"Repo layout" rule (mention it explicitly if you want Claude to look there).

## Separate venvs

Runtime and personas each have their own venv:
- `runtime/venv/` — runtime dependencies (FastAPI, Prefect, AssemblyAI, anthropic)
- `personas/venv/` — personas dependencies (Perplexity SDK, google-genai, openai, anthropic)

Both currently pin `anthropic==0.94.1`. The venvs are separate for
dependency isolation, not because the Anthropic version differs. If
at some point they need to diverge (e.g., to test a new SDK release
against one pipeline without touching the other), the split is already
in place.

Always activate the correct venv for the sub-tree you're working in.

## load_dotenv pattern

All scripts load `.env` from the **monorepo root** (`REPO_ROOT.parent / ".env"` or `_REPO_ROOT.parent / ".env"`). Exception: `personas/flows/shared/clients.py` uses bare `load_dotenv()` intentionally — it walks up from CWD and finds the root `.env` automatically when scripts are run from the monorepo root or the `personas/` dir.

## Cross-repo handoff (personas → runtime)

The personas pipeline produces a `provocateur_profile.json` per voice (37 fields, including `voice_name`, `system_prompt`, `council_mode`, and thematic embeddings). These feed into `runtime/reference/council_config.json` as the `members` array before the Provocateur flow runs each night.

## Where specs live

All canonical pipeline specs are in `docs/`:
- `AI_Assembly_Briefing_v3_1.md` — the authoritative project briefing (as of 2026-04-17)
- `AI_Assembly_Persona_Card_v2.md` — the 37-field card template
- `AI_Assembly_Persona_Pipeline_v3_10.md` — persona build pipeline (being replaced by Phase B chunked architecture on `phase-b-rebuild`; see `_workspace/planning/EXECUTION_PLAN_phase_b.md`)
- `AI_Assembly_Researcher_Pipeline.md` — researcher extraction and grouping
- `AI_Assembly_Provocateur_Pipeline.md` — triage, selection, formulation, packaging
- `AI_Assembly_Transcription_Pipeline.md` — audio to clean transcript pipeline
- `AI_Assembly_Voice_Pipeline.md` — voice pipeline Steps 1+2 (Step 3 unspecified)
- `_workspace/archive/specs/AI_Assembly_Architecture_v1.md` — STALE (archived; moved out of docs/)
- `_workspace/archive/specs/AI_Assembly_Infrastructure_Setup.md` — STALE (archived; moved out of docs/)

Forward-looking design docs are in `_workspace/planning/`. Executed fix plans and prior session artifacts are in `_workspace/archive/`.
