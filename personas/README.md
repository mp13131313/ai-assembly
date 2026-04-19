# AI Assembly — Personas sub-tree

This is the `personas/` sub-tree of the ai-assembly monorepo. See the
top-level [README.md](../README.md) for overall orientation.

Pre-conference pipeline that produces Persona Cards — one per voice —
that the runtime overnight pipeline consumes.

## Local structure

- `run_pass0a_voice_config.py` — Pass 0a: voice config + human review doc
- `run_phase0_1_research.py` — Phase 0.5: Perplexity + Gemini parallel
  + Pass 0b DR-prompt render
- `run_pass0b_dr_prompt.py` — Pass 0b standalone (DR prompt render only)
- `run_persona_pipeline.py` — main pipeline (Pass 1-merge → Derive)
- `flows/shared/` — shared code: clients, io, node validation, prompts
- `inputs/` — per-voice inputs:
  - `conference_facts.json` / `audience_profile.json` / `panel_roster.json` (Phase B 3-way split)
  - `non_human_grounding/` — curated Octopus + Whanganui grounding for Pass 0a (Phase B)
  - `voices/` — voice configs (v3.10 configs are archaeology; all 12 rebuild under Phase B)
  - `dossiers/` — Claude DR dossiers (manually produced via claude.ai)
- `scripts/` — standalone utilities (DR dossier validator)
- `runs/` — per-voice build outputs (gitignored)

## Setup

```bash
cd personas
python3.12 -m venv venv
venv/bin/pip install anthropic==0.94.1 google-genai==1.73.1 \
  openai==2.31.0 perplexity-ai python-dotenv jinja2 requests
```

API keys live in `../.env` at the monorepo root.

## Run a voice end-to-end

```bash
venv/bin/python run_pass0a_voice_config.py "Voice Name"
venv/bin/python run_phase0_1_research.py "Voice Name"
# [manual: paste DR prompt into claude.ai, save dossier]
venv/bin/python run_persona_pipeline.py "Voice Name"
```

## Output per voice

- `runs/<slug>/persona_card_assembled.json` — 37-field card (consumed
  by runtime Voice Pipeline)
- `runs/<slug>/provocateur_profile.json` — 8-field profile (consumed
  by runtime Provocateur via `council_config.json`)
- `runs/<slug>/evaluation_rubric.json` — 9-test quality rubric

## Specs

- `../docs/AI_Assembly_Persona_Pipeline_v3_10.md` — pipeline spec
- `../docs/AI_Assembly_Persona_Card_v2.md` — 37-field schema
- `HANDOFF.md` — cross-tree handoff contract to runtime
