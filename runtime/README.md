# AI Assembly — Local Build

**Project:** The AI Assembly · World Beautiful Business Forum · Athens · May 7–10, 2026

This is the local development tree for the overnight processing pipeline. Full conceptual documentation lives in the project knowledge folder (Transcription / Researcher / Provocateur / Voice / Persona pipeline docs). This README is the quick orientation for when you open the folder.

## Layout

```
ai-assembly/
├── flows/              # Prefect flow code, one file per pipeline stage
│   ├── transcription_flow.py
│   ├── researcher_flow.py
│   ├── provocateur_flow.py
│   ├── voice_flow.py          (to be built)
│   ├── nightly_flow.py        (to be built — orchestrates the above)
│   └── shared/                # code reused across flows
│       ├── io.py              # load_session_package, write_json_atomic
│       ├── council/           # council_config.json + README
│       ├── prompts/           # system/user prompts as .md files (_archive/ holds older versions)
│       └── download_session.sh
│
├── reference/          # frozen inputs (pre-Athens assets)
│   ├── PROPOSED_pipeline_doc_change.md
│   ├── session_template.json
│   ├── personas/              (to be populated with 12 cards)
│   ├── council_profiles.json  (to be written)
│   ├── council_landscape.md   (to be written)
│   ├── audience_profile.json  (to be written)
│   └── sessions.json          (to be written — Athens program)
│
├── runs/               # one folder per run (test or production)
│   ├── dev_msc_test/   # Level 2 validation, 3 MSC sessions
│   │   ├── _manifest.json
│   │   └── 01_transcription/
│   │       ├── vox_populi/
│   │       ├── breaking_point/
│   │       └── west_west_divide/
│   └── night_01/       (to be created during Athens)
│
├── scratch/            # gitignored, for experiments
├── venv/               # Python 3.12 venv
├── .env                # API keys (gitignored)
└── .gitignore
```

## Running a stage locally

From the repo root, with venv activated:

```bash
source venv/bin/activate

# Transcription (one session)
OUTPUT_DIR=runs/dev_msc_test/01_transcription/vox_populi python flows/transcription_flow.py \
  runs/dev_msc_test/01_transcription/vox_populi/audio.m4a \
  runs/dev_msc_test/01_transcription/vox_populi/session.json

# Researcher (all sessions in a run)
python flows/researcher_flow.py runs/dev_msc_test

# Provocateur (all sessions in a run)
python flows/provocateur_flow.py runs/dev_msc_test
```

## Setup

```bash
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then fill in your API keys
```

## Status

- **Transcription Pipeline:** v2 code working end-to-end, validated against 3 MSC panels. Speaker ID is v2 (5 passes); cleaning is v1.
- **Researcher Pipeline:** v3 built (Opus + extended thinking), validated on dev_msc_test.
- **Provocateur Pipeline:** v3 built (triage → deterministic selection → per-pair formulation → briefing packaging), not yet validated at production scale.
- **Voice Pipeline:** spec exists, not yet built.
- **Persona Pipeline:** spec exists; pre-Athens work to produce the 12 persona cards.

See `runs/dev_msc_test/_manifest.json` for the current test run details and known gaps.
