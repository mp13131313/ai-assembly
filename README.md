# AI Assembly

A provotype for the World Beautiful Business Forum AI Democracy Marathon, Athens, May 7–10, 2026.

Ten non-human and historical voices (a river, an octopus, Plato, Hannah Arendt, and others) read each day's human panel transcripts overnight and produce written responses — provocations, queries, reflections — that re-enter the human conversation the following morning via a published microsite.

## Filesystem layout (Tier 3 — code/project separation)

```
~/Desktop/AI Assembly/
├── code/                   # THE GIT REPO — `mp13131313/ai-assembly` (private)
│   ├── docs/               # PRODUCTION: canonical specs + briefing docs
│   │   ├── research/       # PRESERVED: grounding Deep Research artifacts
│   │   └── _archive/       # historical specs (e.g. v3.10 pipeline)
│   ├── runtime/            # PRODUCTION: ingest + flows + orchestrator
│   ├── personas/           # PRODUCTION: Persona Pipeline (v4)
│   ├── _workspace/         # planning/ + archive/ (out of scope for code reviews)
│   └── .env                # Shared secrets (gitignored — see .env.example)
├── projects/               # NEVER pushed — per-project data, sibling to code/
│   ├── current-tests/      # container: dev_msc_test/ + voice-pipeline-dryrun/
│   └── athens-2026/        # PRODUCTION — own git repo (private):
│                           # `mp13131313/ai-assembly-athens2026-voices`
└── archive/                # frozen historical runs + dormant projects — NEVER pushed
```

Per-project data lives **outside** the code repo at `PROJECT_ROOT`. Both pipelines resolve it via:

1. `--project <path>` CLI flag, or
2. `AI_ASSEMBLY_PROJECT_ROOT` environment variable, or
3. **Hard fail** — no silent default.

## What's in the runtime

The runtime is a 5-stage pipeline that turns audio → published dossiers, plus an orchestrator that chains the stages unattended.

```
audio upload  →  transcription  →  researcher  →  provocateur  →  voice  →  editor  →  publish
   (HTTP)       (per-session,        (themes        (per-voice    (per-voice  (per-theme  (microsite-
                ingest auto-fires)   from           briefings)    artifacts)  dossiers)   ready
                                    extractions)                                          JSON)
```

For a complete operational picture — what each stage reads/writes, where every file lives during a night, failure modes, manual intervention — see [`docs/AI_Assembly_Runtime_Lifecycle.md`](docs/AI_Assembly_Runtime_Lifecycle.md).

### Running individual flows

Each flow takes a run directory and is internally idempotent (resume from disk on restart):

```bash
cd runtime
python3.12 -m venv venv
venv/bin/pip install -r requirements.txt

# Set PROJECT_ROOT (or pass --project to the orchestrator)
export AI_ASSEMBLY_PROJECT_ROOT="../projects/athens-2026"

# Manual stage-by-stage:
venv/bin/python flows/researcher_flow.py    "$AI_ASSEMBLY_PROJECT_ROOT/runs/athens_night_1"
venv/bin/python flows/provocateur_flow.py   "$AI_ASSEMBLY_PROJECT_ROOT/runs/athens_night_1"
venv/bin/python flows/voice_flow.py         "$AI_ASSEMBLY_PROJECT_ROOT/runs/athens_night_1" \
    --night 1 --skip-step3
venv/bin/python flows/publish_flow.py       "$AI_ASSEMBLY_PROJECT_ROOT/runs/athens_night_1" \
    --night 1
```

### Running the orchestrator (recommended)

The orchestrator polls the filesystem and fires each downstream stage when its inputs are ready. Coarse-grained, idempotent, restart-safe. Use this for overnight unattended operation:

```bash
venv/bin/python scripts/overnight_orchestrator.py --night 1
# or by date:
venv/bin/python scripts/overnight_orchestrator.py --date 2026-05-07
```

22 trigger-path tests in `runtime/tests/test_orchestrator.py`. See [`docs/AI_Assembly_Runtime_Lifecycle.md`](docs/AI_Assembly_Runtime_Lifecycle.md) §3 for details.

### VM deployment

For Athens 2026, the runtime deploys to a single Hetzner VM (ingest service + orchestrator + Prefect dashboard). Architecture rationale: [`docs/AI_Assembly_Infrastructure.md`](docs/AI_Assembly_Infrastructure.md). Provisioning checklist: [`runtime/ingest/deploy/README.md`](runtime/ingest/deploy/README.md).

## What's in the personas pipeline

Builds the 35-field persona card per voice. Per-voice cost ~$18–22; ~2 hr after 6 manual claude.ai DR sessions complete (~60–180 min each, human-in-the-loop on claude.ai).

```bash
cd personas
python3.12 -m venv venv
venv/bin/pip install anthropic==0.94.1 google-genai==1.73.1 \
  openai==2.31.0 perplexity-ai python-dotenv jinja2 requests

export AI_ASSEMBLY_PROJECT_ROOT="../projects/athens-2026"

# 1. Voice config + human review doc (Pass 0a)
venv/bin/python run_pass0a_voice_config.py "Voice Name"

# 2. Phase 0.5: Perplexity + Gemini parallel research, then Pass 0b base render
venv/bin/python run_phase0_1_research.py "Voice Name"

# 3. Manual: 6 claude.ai sessions per voice with Extended Thinking + Deep Research
#    Use Opus 4.7 across all 6 sections (the older "§1-§5 use 4.6, §6 uses 4.7"
#    guidance is stale — see _workspace/planning/voices/ONBOARDING.md DOs).
#    Save each as $PROJECT_ROOT/voices/<slug>/01_research/04_dr_dossier/0N_section_N.md

# 4. Main pipeline: chunked Pass 1.1–1.7 → Pass 2..6 → Pass 6.5 → Pass 7-pre/anachronism/7a/b/c → Derive
venv/bin/python run_persona_pipeline.py "Voice Name"
```

**Batch the slow step:**

```bash
scripts/batch_pre_dr.sh "$AI_ASSEMBLY_PROJECT_ROOT/voices_batch.txt" --parallel 3
```

Per-voice subfolder layout under `<PROJECT_ROOT>/voices/<slug>/` is documented in [`personas/README.md`](personas/README.md) §"Per-voice subfolder layout".

**Note:** personas and runtime require separate venvs for dependency isolation.

## Cross-repo handoff (personas → runtime)

The personas pipeline produces three runtime-relevant artifacts per voice:

- **Provocateur Profile** (8 fields) at `<PROJECT_ROOT>/voices/<slug>/06_derive/01_provocateur_profile.json` → wires into `<PROJECT_ROOT>/reference/council_config.json` `members[]`.
- **Persona Card** (35 generated + 2 continuity null + metadata) at `<PROJECT_ROOT>/voices/<slug>/07_persona_card_assembled.json` → loaded as Voice Pipeline system prompt. Runtime drops `metadata`, `smoke_test_chains`, and (for Step 2 only) `reference_only_passages`.
- **Chat artifact** at `<PROJECT_ROOT>/voices/<slug>/06_derive/03_chat_system_prompt.json` → operator paste-target for Claude project custom instructions; not consumed by runtime pipelines.

**Current state:** Athens 2026 COMPLETE — 13 dossiers + 30 per-voice pages across Nights 1–3, both repos clean + pushed. For the per-night production detail, deployment_context discipline rules, voice-build state, open items, and follow-ups, see [`STATE.md`](STATE.md).

The athens-2026 production project has its own private git repo (`mp13131313/ai-assembly-athens2026-voices`) for backup of the per-project data. The code repo never touches per-project data.

See `personas/HANDOFF.md` for the full cross-repo runtime contract.

## Docs

Start with [`docs/README.md`](docs/README.md) — staleness index for canonical specs.

**Pipeline specs** (one per stage):

- [Briefing v3.1](docs/AI_Assembly_Briefing_v3_1.md) — project source of truth (target state)
- [Persona Pipeline v4](docs/AI_Assembly_Persona_Pipeline_v4.md) — voice card build
- [Persona Card v2](docs/AI_Assembly_Persona_Card_v2.md) — 35+2 field schema
- [Transcription Pipeline](docs/AI_Assembly_Transcription_Pipeline.md)
- [Researcher Pipeline](docs/AI_Assembly_Researcher_Pipeline.md)
- [Provocateur Pipeline](docs/AI_Assembly_Provocateur_Pipeline.md)
- [Voice Pipeline v2.1](docs/AI_Assembly_Voice_Pipeline.md)
- [Editor Pipeline v2](docs/AI_Assembly_Editor_Pipeline.md) — spec + implementation shipped 2026-05-03; closing-prompt rewrite to v2 still pending

**Runtime / operations:**

- [Runtime Lifecycle](docs/AI_Assembly_Runtime_Lifecycle.md) — what happens during a night, end to end
- [Infrastructure](docs/AI_Assembly_Infrastructure.md) — Athens 2026 VM deployment spec
- [Ingest deploy README](runtime/ingest/deploy/README.md) — VM provisioning checklist

**Planning / fresh-session pickup:**

- [`_workspace/planning/ONBOARDING.md`](_workspace/planning/ONBOARDING.md) — thin index + cross-cutting rules
- Two workstreams in `_workspace/planning/{runtime,voices}/{ONBOARDING,OPEN_ITEMS,HANDOFF}.md`
- [`_workspace/planning/FOLLOW_UPS.md`](_workspace/planning/FOLLOW_UPS.md) — frozen historical FU#1–62 ledger
