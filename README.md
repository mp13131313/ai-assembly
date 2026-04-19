# AI Assembly

A provotype for the World Beautiful Business Forum AI Democracy Marathon, Athens, May 7–10, 2026.

Twelve non-human voices (a river, an octopus, Plato, Hannah Arendt, and eight others) read the day's human panel transcripts overnight and produce written responses — provocations, queries, reflections — that re-enter the human conversation the following morning via Substack read-throughs.

## Structure

```
ai-assembly/
├── docs/           # PRODUCTION: canonical specs and briefing docs
├── runtime/        # PRODUCTION: FastAPI ingest app + Prefect flows (transcription, researcher, provocateur)
├── personas/       # PRODUCTION: Persona Pipeline — builds the 37-field voice cards that feed the runtime
├── research/       # PRESERVED: grounding Deep Research artifacts (not deletable)
├── _workspace/     # Out of scope for reviews/deploys: planning/ (active design) + archive/ (historical)
└── .env            # Shared secrets (not committed — see .env.example)
```

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
venv/bin/pip install anthropic==0.94.1 google-genai openai perplexity-ai python-dotenv jinja2 requests
```

Building a voice card is a 4-step workflow per voice:

```bash
# 1. Voice config + human review doc (Pass 0a)
venv/bin/python run_pass0a_voice_config.py "Voice Name"

# 2. Perplexity + Gemini parallel research + Claude DR prompt render (Phase 0.5)
venv/bin/python run_phase0_1_research.py "Voice Name"

# 3. Manual: open claude.ai (Opus 4.7 + Extended Thinking + Deep Research),
#    paste the generated DR prompt, wait 60–180 min, save the dossier to
#    inputs/dossiers/<slug>_claude_dr.md

# 4. Main pipeline: Pass 1-merge → Pass 7c → Derive (all LLM passes)
venv/bin/python run_persona_pipeline.py "Voice Name"
```

**Note:** personas and runtime require separate venvs for dependency isolation (both currently pin `anthropic==0.94.1`).

## Cross-repo handoff

The personas pipeline outputs `provocateur_profile.json` per voice (8 fields: `name`, `speaks_from`, `core_commitment`, `activates_on`, `goes_flat_on`, `stretch`, `translation_range`, `stance_tendency`, `medium`). These feed the `members` array in `runtime/flows/shared/council/council_config.json` before the Provocateur flow runs each night.

**Current state:** `council_config.json` is `dev_stub_v2_with_selection_params` — hand-written stubs for all 12 members, not yet synced from real persona-pipeline Derive output. Pre-Athens blocker tracked in `docs/CURRENT_STATE.md` §6.1. See `docs/` for the full pipeline specification.

## Docs

See [`docs/`](docs/) for canonical pipeline specs, persona card template, and briefing documents. Start with [`docs/README.md`](docs/README.md) for a staleness guide.
