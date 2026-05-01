# AI Assembly

A provotype for the World Beautiful Business Forum AI Democracy Marathon, Athens, May 7–10, 2026.

Twelve non-human voices (a river, an octopus, Plato, Hannah Arendt, and eight others) read the day's human panel transcripts overnight and produce written responses — provocations, queries, reflections — that re-enter the human conversation the following morning via Substack read-throughs.

## Filesystem layout (Tier 3 — code/project separation)

```
~/Desktop/AI Assembly/
├── code/                   # THE GIT REPO — `mp13131313/ai-assembly`
│   ├── docs/               # PRODUCTION: canonical specs + briefing docs
│   │   └── research/       # PRESERVED: grounding Deep Research artifacts (5; under docs/)
│   ├── runtime/            # PRODUCTION: FastAPI ingest + Prefect flows
│   ├── personas/           # PRODUCTION: Persona Pipeline (v4) — builds 35-field cards
│   ├── _workspace/         # planning/ + archive/ (out of scope for code reviews)
│   └── .env                # Shared secrets (gitignored — see .env.example)
├── projects/               # NEVER pushed — per-project data, sibling to code/
│   ├── test/               # sandbox
│   ├── phase-l-plato/      # Plato Phase L working project
│   ├── phase-l-dostoevsky/ # Dostoevsky Phase L working project
│   └── athens-2026/        # PRODUCTION — own git repo (private):
│                           # `mp13131313/ai-assembly-athens2026-voices`
└── archive/                # frozen historical runs — NEVER pushed
```

Per-project data lives **outside** the code repo at `PROJECT_ROOT`. Both pipelines resolve it via:

1. `--project <path>` CLI flag (personas runners), or
2. `AI_ASSEMBLY_PROJECT_ROOT` environment variable, or
3. **Hard fail** — no silent default. With multiple projects active, a silent default risks writing to the wrong one.

See `docs/CURRENT_STATE.md` §5.16–5.17 for the rationale.

## Running the runtime side

```bash
cd runtime
python3.12 -m venv venv
venv/bin/pip install -r requirements.txt
cp ../.env.example ../.env   # then fill in keys

# Transcribe a session:
venv/bin/python flows/transcription_flow.py path/to/audio.mp4 path/to/session.json

# Run the researcher:
venv/bin/python flows/researcher_flow.py path/to/session_package.json

# Run the provocateur:
venv/bin/python flows/provocateur_flow.py path/to/researcher_output.json
```

See `runtime/ingest/deploy/README.md` for VM deployment.

## Running the personas side

```bash
cd personas
python3.12 -m venv venv
venv/bin/pip install anthropic==0.94.1 google-genai==1.73.1 \
  openai==2.31.0 perplexity-ai python-dotenv jinja2 requests
```

Building a voice card is a 4-stage workflow per voice (Pipeline v4 — see `docs/AI_Assembly_Persona_Pipeline_v4.md`):

```bash
# Set PROJECT_ROOT once per shell (or pass --project to every command)
export AI_ASSEMBLY_PROJECT_ROOT="../projects/athens-2026"

# 1. Voice config + human review doc (Pass 0a)
venv/bin/python run_pass0a_voice_config.py "Voice Name"

# 2. Phase 0.5: Perplexity + Gemini parallel research, then Pass 0b base render
#    + tailor (LLM splice) + 6-section split for manual claude.ai DR
venv/bin/python run_phase0_1_research.py "Voice Name"

# 3. Manual: 6 claude.ai sessions per voice with Extended Thinking + Deep Research
#    §1–§5: Opus 4.6
#    §6:    Opus 4.7  (Phase L empirical: 4.6 produces reader's-intro on §6)
#    Save each as
#      $PROJECT_ROOT/voices/<slug>/01_research/04_dr_dossier/0N_section_N.md

# 4. Main pipeline: chunked Pass 1.1–1.7 → Pass 2..6 → Pass 6.5-clean →
#    Pass 7-pre/7-anachronism/7a (+optional FU#13 patcher) → Pass 7b/7c → Derive
venv/bin/python run_persona_pipeline.py "Voice Name"
```

Per-voice cost: ~$18–22. Wall time: ~2 hours after the 6 manual DR sessions complete. Manual DR sessions run human-in-the-loop on claude.ai (~60–180 min each).

**Batch the slow step:** the claude.ai DR step is the wall-time bottleneck. To get N DR prompts ready at once for parallel manual sessions:

```bash
scripts/batch_pre_dr.sh "$AI_ASSEMBLY_PROJECT_ROOT/voices_batch.txt" --parallel 3
```

Per-voice subfolder layout under `<PROJECT_ROOT>/voices/<slug>/` is documented in `docs/CURRENT_STATE.md` §0.1.

**Note:** personas and runtime require separate venvs for dependency isolation (both currently pin `anthropic==0.94.1`).

## Cross-repo handoff

The personas pipeline produces three runtime-relevant artifacts per voice:

- **Provocateur Profile** (8 fields) at `voices/<slug>/06_derive/01_provocateur_profile.json` → wires into `runtime/flows/shared/council/council_config.json` `members[]`.
- **Persona Card** (35 generated + 2 continuity null + metadata) at `voices/<slug>/07_persona_card_assembled.json` → loaded as Voice Pipeline system prompt (when built). Runtime MUST drop `metadata` and `smoke_test_chains` before assembly.
- **Chat artifact** at `voices/<slug>/06_derive/03_chat_system_prompt.json` → operator paste-target for Claude project custom instructions; not consumed by runtime pipelines.

**Current state:** `runtime/flows/shared/council/council_config.json` is `dev_stub_v3_audience_sharpened` — hand-written stubs for all 12 members, replaced as athens-2026 cards complete. Pre-Athens blocker tracked in `docs/CURRENT_STATE.md` §6.1.

The athens-2026 production project has its own private git repo (`mp13131313/ai-assembly-athens2026-voices`) for backup of the per-project data. The code repo never touches per-project data.

See `personas/HANDOFF.md` for the full cross-repo runtime contract.

## Docs

Start with [`docs/README.md`](docs/README.md) — staleness index for canonical specs.

Key entry points:

- [`docs/AI_Assembly_Briefing_v3_1.md`](docs/AI_Assembly_Briefing_v3_1.md) — project source of truth (target state)
- [`docs/CURRENT_STATE.md`](docs/CURRENT_STATE.md) — gap analysis + architectural rationale (current)
- [`docs/AI_Assembly_Persona_Pipeline_v4.md`](docs/AI_Assembly_Persona_Pipeline_v4.md) — current persona pipeline spec
- [`docs/AI_Assembly_Persona_Card_v2.md`](docs/AI_Assembly_Persona_Card_v2.md) — 35+2 field schema (with v2.1 amendments)
- [`_workspace/planning/HANDOFF_2026_04_27.md`](_workspace/planning/HANDOFF_2026_04_27.md) — current session pickup
- [`_workspace/planning/FOLLOW_UPS.md`](_workspace/planning/FOLLOW_UPS.md) — active follow-up tracker
- [`_workspace/planning/ONBOARDING.md`](_workspace/planning/ONBOARDING.md) — fresh-session pickup (permanent)
