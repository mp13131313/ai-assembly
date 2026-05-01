# AI Assembly — Personas sub-tree

This is the `personas/` sub-tree of the ai-assembly monorepo. See the
top-level [README.md](../README.md) for overall orientation.

Pre-conference pipeline that produces Persona Cards — one per voice — that
the runtime overnight pipeline consumes. Pipeline v4 (2026-04-27); see
`../docs/AI_Assembly_Persona_Pipeline_v4.md`.

## Local structure (code — this repo)

- `run_pass0a_voice_config.py` — Pass 0a: voice config + human review doc
- `run_phase0_1_research.py` — Phase 0.5: Perplexity + Gemini parallel +
  Pass 0b base render + tailor + 6-section split
- `run_pass0b_dr_prompt.py` — Pass 0b standalone (DR prompt render only)
- `run_pass_1_all.py` — arch-03 chunked merge driver (Pass 1.1–1.6 in
  parallel)
- `run_pass_1_7.py` — narrow coherence audit (Pass 1.7)
- `run_persona_pipeline.py` — main orchestrator (Pass 1c → Derive → Card
  Assembly → CARD COMPLETE)
- `flows/shared/` — shared code: `clients.py`, `io.py`, `paths.py`,
  `node0_validation.py`, `chunk_runner.py`, `bracket_strip.py` (FU#33 P1),
  `pass_7pre_chunked.py` (FU#2), `chat_prompt_builder.py` (FU#41),
  `patch_walker.py` (FU#13), `url_extract.py` (1-arch-07),
  `perplexity_split.py`, `project_root.py` (Tier 3 resolver)
- `flows/shared/prompts/` — all system + user prompt files
- `schemas/` — Pydantic source-of-truth (chunk schemas + voice_config +
  merged_dossier)
- `scripts/` — `batch_pre_dr.sh`, `sentinel_regen.py` (FU#29),
  `migrate_to_per_voice_layout.py`, `validate_dr_dossier.py`,
  `arch_03_synthesis_audit.py`, `arch_03_preservation_audit.py`,
  `split_tailored_prompt.py`, `invalidate_cache.py`
- `tests/` — 212 tests, all passing 2026-04-27. Fixtures at
  `tests/fixtures/synthetic_voice/`.
- `HANDOFF.md` — cross-tree handoff contract (current)

## Project data (PROJECT_ROOT — separate dir, Tier 3)

Per Tier 3 (2026-04-20), all per-project data lives **outside this repo**,
under `PROJECT_ROOT`. Runners resolve it via `--project <path>` →
`AI_ASSEMBLY_PROJECT_ROOT` env → **hard fail** (no silent default — with
multiple projects active, defaulting risks writing to the wrong one).

Active projects (sibling to `code/`):

- `../projects/current-tests/{dev_msc_test, voice-pipeline-dryrun}/` — two active test surfaces. `current-tests/` itself is a container, NOT a PROJECT_ROOT. Pass `--project .../projects/current-tests/voice-pipeline-dryrun` (the only PROJECT_ROOT-shape entry inside) for sandbox testing.
- `../projects/athens-2026/` — production (own backup git repo,
  `mp13131313/ai-assembly-athens2026-voices`, private)
- Dormant Phase L projects + prior Dostoevsky sandbox PROJECT_ROOT relocated to umbrella `~/Desktop/AI Assembly/archive/` 2026-05-01 (`phase-l-{plato,dostoevsky}/`, `dostoevsky_sandbox/`).

### Project-level files (at `PROJECT_ROOT/` root, NOT under `inputs/`)

- `conference_facts.json` — program / deployment context (Pass 0a + Pass 7b)
- `audience_profile.json` — audience descriptive (Pass 5 priming + Pass 7b)
- `panel_roster.json` — 12 voices + casting principle (Pass 0a)
- `reference/` — runtime artifacts (sessions.json, speakers.json — runtime team owns)
- `council_config.json` — runtime artifact (runtime team owns)

### Per-voice subfolder layout

```
<PROJECT_ROOT>/voices/<slug>/
├── 00_intake/
│   ├── 01_non_human_grounding.md   (optional)
│   ├── 02_voice_config.json        (Pass 0a output)
│   └── 03_review_doc.md            (Pass 0a operator-review surface)
├── 01_research/
│   ├── 01_perplexity_dossier.json
│   ├── 02_gemini_broad_scan.json
│   ├── 03_dr_prompts/
│   │   ├── 01_monolithic_dr_prompt.md
│   │   ├── 02_tailoring_notes.json
│   │   └── 03_section_1_dr_prompt.md … 08_section_6_dr_prompt.md
│   └── 04_dr_dossier/
│       └── 01_section_1.md … 06_section_6.md  (manual claude.ai DR outputs)
├── 02_merge/
│   ├── pass_1_1/{life_scaffold, formative_candidates}.json
│   ├── pass_1_2/{commitments, concepts, tensions, interpretive_frames}.json
│   ├── pass_1_3/{reasoning_method, textures, analytical_context_reasoning}.json
│   ├── pass_1_4/{moves, register, vocabulary, analytical_context_voice}.json
│   ├── pass_1_5/{knowledge_boundary, sensitive_topics, hard_limits}.json
│   ├── pass_1_6/{works, passages, reference_only_passages}.json
│   ├── 07_pass_1_7_coherence.json   (narrow audit metadata)
│   ├── 08_merged_dossier.json       (convenience snapshot — chunks are SoT)
│   └── _fix_log.json                (if FU#13 patcher fired)
├── 03_corpus/
│   ├── 00_primary_text_urls.json   (CC#1 — derived deterministically)
│   ├── 01_primary_texts.json
│   ├── 02_excerpt_selections.json
│   └── 03_primary_texts_reviewed.flag  (manual review gate)
├── 04_generation/   (Pass 2/3/4a/4b/5/6 + CT compress files)
├── 05_validation/   (Pass 7-pre/7-anachronism/7a/7b/7c)
├── 06_derive/
│   ├── 00_derive_raw.json
│   ├── 01_provocateur_profile.json    (Provocateur Pipeline consumer)
│   ├── 02_evaluation_rubric.json      (9 test prompts)
│   └── 03_chat_system_prompt.json     (FU#41 — Claude project paste-target)
└── 07_persona_card_assembled.json     (Voice Pipeline consumer)
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

For Athens 2026 (set the env var or pass `--project`):

```bash
export AI_ASSEMBLY_PROJECT_ROOT="../projects/athens-2026"

venv/bin/python run_pass0a_voice_config.py "Voice Name"
venv/bin/python run_phase0_1_research.py "Voice Name"

# [Manual: 6 claude.ai sessions per voice with Extended Thinking + Deep
#  Research. §1–§5 use Opus 4.6; §6 uses Opus 4.7. Save each as
#  $PROJECT_ROOT/voices/<slug>/01_research/04_dr_dossier/0N_section_N.md]

venv/bin/python run_persona_pipeline.py "Voice Name"
```

For another project, point at its root:

```bash
venv/bin/python run_pass0a_voice_config.py "Voice Name" \
  --project /path/to/berlin-2027
```

## Batch the slow step: Pass 0a + Phase 0.5 in parallel

The 6 claude.ai DR sessions per voice are the wall-time bottleneck
(~60–180 min per session, human-initiated). To get N voices' DR prompts
ready at once for parallel manual sessions:

```bash
scripts/batch_pre_dr.sh "$AI_ASSEMBLY_PROJECT_ROOT/voices_batch.txt" --parallel 3
```

`voices_batch.txt` lives under PROJECT_ROOT, one voice per line:
`<name> | <wiki_url>` or `<name> | NON_HUMAN` for voices that use curated
grounding from `inputs/non_human_grounding/`. Blank lines and `#` comments
are ignored. See `../projects/athens-2026/voices_batch.txt` for the Athens
seed file.

Per-voice logs land at `$PROJECT_ROOT/batch_logs/<slug>.log`. The script is
idempotent: a failed voice resumes from the last cached step on re-run.

## Output per voice (under PROJECT_ROOT)

- `voices/<slug>/07_persona_card_assembled.json` — 35 generated + 2
  continuity null + metadata block (consumed by runtime Voice Pipeline)
- `voices/<slug>/06_derive/01_provocateur_profile.json` — 8-field profile
  (consumed by runtime Provocateur via `council_config.json`)
- `voices/<slug>/06_derive/02_evaluation_rubric.json` — 9 test prompts
- `voices/<slug>/06_derive/03_chat_system_prompt.json` — chat artifact
  (operator paste-target for Claude projects; not consumed by runtime)

## Sentinel regen (FU#29) — for prompt edits

Prompt edits silently affect every voice generated thereafter. To smoke-test
on a specific voice:

```bash
# Snapshot pre-edit
mkdir -p _workspace/sentinel_baselines/2026-MM-DD-pre-CHANGE/<slug>
cp <PROJECT_ROOT>/voices/<slug>/04_generation/<file>.json \
   _workspace/sentinel_baselines/2026-MM-DD-pre-CHANGE/<slug>/

# Make prompt edit, then:
python scripts/sentinel_regen.py regen \
  --pass <PASS_NAME> --voices <slug> \
  --baseline-snapshot _workspace/sentinel_baselines/2026-MM-DD-pre-CHANGE
```

Inspect diff. Validate intended pattern surfaced. Restore baseline if it
was a smoke-test.

## Specs

- `../docs/AI_Assembly_Persona_Pipeline_v4.md` — pipeline spec (current)
- `../docs/AI_Assembly_Persona_Card_v2.md` — 35+2 field schema (with v2.1
  amendments section)
- `../docs/CURRENT_STATE.md` — gap analysis + architectural rationale
- `HANDOFF.md` — cross-repo runtime contract (current)
