# AI Assembly — Personas

Pre-conference pipeline that produces Persona Cards (one per voice) that
the runtime overnight pipeline consumes. Pipeline v4 (2026-04-27).

## Where to look

| For… | Read |
|---|---|
| **Project orientation + setup** | [`../README.md`](../README.md) (root) |
| **Current state** | [`../STATE.md`](../STATE.md) |
| **Pipeline spec** | [`../docs/AI_Assembly_Persona_Pipeline_v4.md`](../docs/AI_Assembly_Persona_Pipeline_v4.md) |
| **Card schema** | [`../docs/AI_Assembly_Persona_Card_v2.md`](../docs/AI_Assembly_Persona_Card_v2.md) |
| **Cross-repo runtime contract** | [`HANDOFF.md`](HANDOFF.md) (renamed to `CROSS_REPO_CONTRACT.md` 2026-06-01) |
| **Voice-build open items** | [`../_workspace/planning/voices/OPEN_ITEMS.md`](../_workspace/planning/voices/OPEN_ITEMS.md) |
| **Voice-build onboarding** | [`../_workspace/planning/voices/ONBOARDING.md`](../_workspace/planning/voices/ONBOARDING.md) |

## Per-voice subfolder layout

Under `<PROJECT_ROOT>/voices/<slug>/`:

```
voices/<slug>/
├── 00_intake/                          # Pass 0a (voice_config + review_doc)
├── 01_research/                        # Phase 0.5 + 6 manual claude.ai DR sessions
├── 02_merge/                           # Pass 1.1-1.7 chunked merge (arch-03)
├── 03_corpus/                          # Pass 1c-extract + fetch + review gate
├── 04_generation/                      # Pass 2-6 (Identity / Intellectual / Voice / Artifact / Engagement / Corpus)
├── 05_validation/                      # Pass 7-pre + 7-anachronism + 7a + 7b + 7c + 7a FINAL
├── 06_derive/                          # Provocateur Profile + Evaluation Rubric + Chat Artifact
└── 07_persona_card_assembled.json      # THE deliverable (consumed by runtime Voice Pipeline)
```

Per-project files at PROJECT_ROOT root: `conference_facts.json`,
`audience_profile.json`, `panel_roster.json`. Runtime artifacts:
`council_config.json`, `reference/{sessions, speakers}.json`.

## Setup

```bash
python3.12 -m venv venv
venv/bin/pip install anthropic==0.94.1 google-genai==1.73.1 \
  openai==2.31.0 perplexity-ai python-dotenv jinja2 requests
```

API keys + `AI_ASSEMBLY_PROJECT_ROOT` live in `../.env`. See
[`../README.md`](../README.md) for run examples.

## Run a voice end-to-end

```bash
export AI_ASSEMBLY_PROJECT_ROOT="../projects/athens-2026"
venv/bin/python run_pass0a_voice_config.py "Voice Name"
venv/bin/python run_phase0_1_research.py "Voice Name"
# [Manual: 6 claude.ai sessions per voice with Extended Thinking +
#  Deep Research. Use Opus 4.7 across all 6 sections (see
#  voices/ONBOARDING.md DOs). Save each as
#  $PROJECT_ROOT/voices/<slug>/01_research/04_dr_dossier/0N_section_N.md]
venv/bin/python run_persona_pipeline.py "Voice Name"
```

Batch wrapper for parallel DR-prompt prep:

```bash
scripts/batch_pre_dr.sh "$AI_ASSEMBLY_PROJECT_ROOT/voices_batch.txt" --parallel 3
```

## Sentinel regen (FU#29) — for prompt edits

Snapshot pre-edit voice, edit prompt, re-fire with `sentinel_regen.py`,
diff. Pattern documented in [`../_workspace/planning/voices/ONBOARDING.md`](../_workspace/planning/voices/ONBOARDING.md).
