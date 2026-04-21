# AI Assembly — Personas sub-tree

This is the `personas/` sub-tree of the ai-assembly monorepo. See the
top-level [README.md](../README.md) for overall orientation.

Pre-conference pipeline that produces Persona Cards — one per voice —
that the runtime overnight pipeline consumes.

## Local structure (code — this repo)

- `run_pass0a_voice_config.py` — Pass 0a: voice config + human review doc
- `run_phase0_1_research.py` — Phase 0.5: Perplexity + Gemini parallel
  + Pass 0b DR-prompt render
- `run_pass0b_dr_prompt.py` — Pass 0b standalone (DR prompt render only)
- `run_persona_pipeline.py` — main pipeline (Pass 1-merge → Derive)
- `flows/shared/` — shared code: clients, io, node validation, prompts,
  `project_root.py` (PROJECT_ROOT resolver)
- `schemas/` — Pydantic source-of-truth schemas (JSON Schema generated)
- `scripts/` — standalone utilities (DR dossier validator)
- `tests/fixtures/` — pinned test fixtures (code-level, Ibn Battuta)

## Project data (PROJECT_ROOT — separate dir)

Per Tier 3 (2026-04-20), all per-project data lives **outside this repo**,
under `PROJECT_ROOT`. Runners resolve it via `--project <path>` →
`AI_ASSEMBLY_PROJECT_ROOT` env → sibling default `../athens-2026/`.

Layout:

```
<PROJECT_ROOT>/
├── inputs/
│   ├── conference_facts.json       # project metadata
│   ├── audience_profile.json       # compressed audience brief
│   ├── panel_roster.json           # 12 voices for this project
│   ├── non_human_grounding/        # curated grounding (Octopus, Whanganui…)
│   ├── voices/<slug>.json          # Pass 0a outputs (curator-edited)
│   │   └── <slug>_pass0a_review.md
│   └── dossiers/
│       ├── <slug>_claude_dr.md     # manual claude.ai DR output
│       └── _dr_prompts/            # generated tailored prompts
└── runs/<slug>/                    # all pipeline runtime outputs
```

## Setup

```bash
cd personas
python3.12 -m venv venv
venv/bin/pip install anthropic==0.94.1 google-genai==1.73.1 \
  openai==2.31.0 perplexity-ai python-dotenv jinja2 requests
```

API keys live in `../.env` at the monorepo root.

## Run a voice end-to-end

For Athens 2026 (sibling `../athens-2026/` default, no flag needed):

```bash
venv/bin/python run_pass0a_voice_config.py "Voice Name"
venv/bin/python run_phase0_1_research.py "Voice Name"
# [manual: paste DR prompt into claude.ai, save dossier under
#  $PROJECT_ROOT/inputs/dossiers/<slug>_claude_dr.md]
venv/bin/python run_persona_pipeline.py "Voice Name"
```

For another project, point at its root:

```bash
venv/bin/python run_pass0a_voice_config.py "Voice Name" \
  --project /path/to/berlin-2027
# …or set AI_ASSEMBLY_PROJECT_ROOT=/path/to/berlin-2027 and drop the flag.
```

## Batch: Pass 0a + Phase 0.5 for several voices in parallel

The claude.ai Deep Research step is the real wall-time bottleneck
(~60–180 min per voice, human-initiated). To get N DR prompts ready at
once so claude.ai can research in parallel (one tab per voice):

```bash
scripts/batch_pre_dr.sh "$AI_ASSEMBLY_PROJECT_ROOT/voices_batch.txt" --parallel 3
```

`voices_batch.txt` lives under PROJECT_ROOT (per-project data), one
voice per line: `<name> | <wiki_url>` or `<name> | NON_HUMAN` for
voices that use curated grounding from `inputs/non_human_grounding/`.
Blank lines and `#`-comments are ignored. See
`projects/athens-2026/voices_batch.txt` for the Athens seed file.

Outputs go to the usual places; per-voice logs land at
`$PROJECT_ROOT/batch_logs/<slug>.log`. The script is idempotent: a
failed voice resumes from the last cached step on re-run.

## Output per voice (under PROJECT_ROOT)

- `runs/<slug>/persona_card_assembled.json` — 37-field card (consumed
  by runtime Voice Pipeline)
- `runs/<slug>/provocateur_profile.json` — 8-field profile (consumed
  by runtime Provocateur via `council_config.json`)
- `runs/<slug>/evaluation_rubric.json` — 9-test quality rubric

## Specs

- `../docs/AI_Assembly_Persona_Pipeline_v3_10.md` — pipeline spec
- `../docs/AI_Assembly_Persona_Card_v2.md` — 37-field schema
- `HANDOFF.md` — cross-tree handoff contract to runtime
