# AI Assembly — Claude context

## Repo layout

Four categories:

- `docs/`, `runtime/`, `personas/` — **production** slice. Current specs, running code, canonical pipeline. In scope for every code review and VM deploy.
- `research/` — **preserved grounding**. Deep Research artifacts that ground architecture decisions. Not deletable.
- `_workspace/planning/` — **forward-looking design**. Active docs for unbuilt work (Phase B rebuild plan, binding decisions). Promoted to `docs/` when the work lands.
- `_workspace/archive/` — **historical detritus**. Executed fix plans, stale specs, session artifacts, run artifacts. Eligible for pruning. **Out of scope for code reviews and VM deploys by default — mention it explicitly if you want Claude to look here.**
- `.env` — shared secrets at repo root (not committed). Both sub-trees load from `../.env` (one directory above their own root).

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
- `AI_Assembly_Persona_Pipeline_v3_10.md` — persona build pipeline
- `AI_Assembly_Researcher_Pipeline.md` — researcher extraction and grouping
- `AI_Assembly_Provocateur_Pipeline.md` — triage, selection, formulation, packaging
- `AI_Assembly_Transcription_Pipeline.md` — audio to clean transcript pipeline
- `AI_Assembly_Voice_Pipeline.md` — voice pipeline Steps 1+2 (Step 3 unspecified)
- `_workspace/archive/specs/AI_Assembly_Architecture_v1.md` — STALE (archived; moved out of docs/)
- `_workspace/archive/specs/AI_Assembly_Infrastructure_Setup.md` — STALE (archived; moved out of docs/)

Forward-looking design docs are in `_workspace/planning/`. Executed fix plans and prior session artifacts are in `_workspace/archive/`.
