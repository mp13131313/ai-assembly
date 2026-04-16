# AI Assembly

A provotype for the World Beautiful Business Forum AI Democracy Marathon, Athens, May 7–10, 2026.

Twelve non-human voices (a river, an octopus, Plato, Hannah Arendt, and eight others) read the day's human panel transcripts overnight and produce written responses — provocations, queries, reflections — that re-enter the human conversation the following morning via Substack read-throughs.

## Structure

```
ai-assembly/
├── runtime/        # FastAPI ingest app + Prefect flows (transcription, researcher, provocateur)
├── personas/       # Persona Pipeline: builds the 37-field voice cards that feed the runtime
├── docs/           # Canonical specs and briefing docs
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
venv/bin/pip install anthropic==0.94.1 google-generativeai openai perplexity-ai python-dotenv
# Build persona cards for all voices:
venv/bin/python run_persona_pipeline.py
```

**Note:** personas and runtime require separate venvs — they pin different Anthropic SDK versions (0.94.1 vs 0.95.0).

## Cross-repo handoff

The personas pipeline outputs `provocateur_profile.json` for each voice. Copy or symlink these into `runtime/reference/` as `council_config.json` members before running the Provocateur flow. See `docs/` for the full pipeline specification.

## Docs

See [`docs/`](docs/) for canonical pipeline specs, persona card template, and briefing documents. Start with [`docs/README.md`](docs/README.md) for a staleness guide.
