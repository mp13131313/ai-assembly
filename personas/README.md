# AI Assembly — Persona Pipeline

**Project:** The AI Assembly · World Beautiful Business Forum · Athens · May 7-10, 2026

This is the pre-conference build pipeline that produces the **Persona Cards** — one per voice — that the runtime overnight pipeline (`ai-assembly`) consumes. Every voice in the Assembly council needs a completed Persona Card before Athens. This pipeline produces them.

## Two repos, one project

| Repo | Cadence | Function |
|---|---|---|
| `ai-assembly` | Runs nightly during Athens | Audio → Transcription → Researcher → Provocateur → Voice → Artifacts |
| `ai-assembly-personas` (this) | Runs in the weeks before | Voice name + input → 17-node pipeline → completed Persona Card |

The interface is the **Persona Card v2 schema** (37 fields, JSON). Cards produced here are dropped into `ai-assembly/flows/shared/council/personas/` and referenced by the runtime council.

## Layout

```
ai-assembly-personas/
├── flows/
│   ├── persona_flow.py             # The orchestrator
│   └── shared/
│       ├── io.py                   # File I/O helpers
│       ├── prompts/                # System prompts for each pass
│       └── card_template/          # Persona Card v2 field specs
├── inputs/
│   └── voices/                     # Per-voice input schema files
└── runs/
    └── {voice_slug}/               # Per-voice run directory
        ├── 01_research/
        ├── 02_passes/
        ├── persona_card.json       # Final 37-field artifact
        ├── derive/
        │   └── provocateur_profile.json
        └── manifest.json
```

## Pipeline overview (per voice)

```
Node 0     Input Validation          (Python, no API)
Node 1a    Research Dossier          Perplexity sonar-deep-research
Node 1b    Broad Scan                Gemini 2.5 Pro
Node 1c    Primary Text Fetch        web fetch + manual review
Node 1m    Contradiction Check       Claude
Node CT    Coherence Threading       Claude (after each generation pass)
Pass 2     Identity & Boundaries     Claude (9 fields)
Pass 3     Intellectual Core         Claude + ChatGPT DR conditional (5 fields)
Pass 4a    Voice                     Claude (7 fields)
Pass 4b    Artifact                  Claude (8 fields)
Pass 5     Engagement                Claude (4 fields)
Pass 6     Corpus Curation           Claude (1 field)
Pass 7-pre Citation Verification     Claude
Pass 7a    Cross-Model Validation    GPT-4o → Gemini fallback
Pass 7b    Worked Provocations       Claude (1 field)
Pass 7c    Negative Constraints      Claude / Gemini (refines 2 fields)
Derive     Provocateur Profile       Claude (writes the 9-field profile that
                                     drops into ai-assembly's council_config)
```

Total: 35 pre-conference fields populated + 2 runtime continuity fields = 37.

## Output Register Rule (CRITICAL)

The Persona Card is not a document about a voice. It IS the system prompt the voice reads at runtime. Every field must be in **first person** (as the voice) or **second person** (addressed to the voice). Never third person. Never scholarly description.

Validated by the read-aloud test: if it sounds like a scholar describing someone, it's wrong. If it sounds like a person speaking or like an instruction addressed to that person, it's right.

## Setup

```bash
cd ai-assembly-personas
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt   # or: pip install anthropic prefect python-dotenv requests google-generativeai openai
cp .env.example .env
# Then fill in the four API keys
```

## Specs

The canonical specs live in project knowledge:
- `AI_Assembly_Persona_Pipeline_v3_8.md` — pipeline architecture
- `AI_Assembly_Persona_Card_v2.md` — 37-field schema
