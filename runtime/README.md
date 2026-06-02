# AI Assembly — Runtime

The overnight pipeline that turns the day's audio into published voice
artifacts. Ran end-to-end across all three Athens 2026 nights (13 dossiers
+ 30 per-voice pages).

## Where to look

| For… | Read |
|---|---|
| **Project orientation + setup** | [`../README.md`](../README.md) (root) |
| **Current state** | [`../STATE.md`](../STATE.md) |
| **End-to-end operations** (what happens during a night) | [`../docs/AI_Assembly_Runtime_Lifecycle.md`](../docs/AI_Assembly_Runtime_Lifecycle.md) |
| **Stage specs** | [`../docs/AI_Assembly_*_Pipeline.md`](../docs/) per stage |
| **Open items** (v4.1 follow-ups) | [`../_workspace/planning/runtime/OPEN_ITEMS.md`](../_workspace/planning/runtime/OPEN_ITEMS.md) |
| **Onboarding for runtime work** | [`../_workspace/planning/runtime/ONBOARDING.md`](../_workspace/planning/runtime/ONBOARDING.md) |
| **Deployment** (VM spec) | [`../docs/AI_Assembly_Infrastructure.md`](../docs/AI_Assembly_Infrastructure.md) + [`ingest/deploy/README.md`](ingest/deploy/README.md) |

## Six stages + orchestrator

```
audio upload → transcription → researcher → provocateur → voice → editor → publish
```

| Module | Code | Spec |
|---|---|---|
| Transcription | `flows/transcription_flow.py` | `docs/AI_Assembly_Transcription_Pipeline.md` |
| Researcher | `flows/researcher_flow.py` | `docs/AI_Assembly_Researcher_Pipeline.md` |
| Provocateur | `flows/provocateur_flow.py` | `docs/AI_Assembly_Provocateur_Pipeline.md` |
| Voice | `flows/voice_flow.py` + `flows/voice/*.py` | `docs/AI_Assembly_Voice_Pipeline.md` |
| Editor | `flows/editor_flow.py` + `flows/editor/*.py` | `docs/AI_Assembly_Editor_Pipeline.md` |
| Publish | `flows/publish_flow.py` + `flows/voice/publish.py` | (lives inside Voice + Runtime Lifecycle specs) |
| Orchestrator | `scripts/overnight_orchestrator.py` | `docs/AI_Assembly_Runtime_Lifecycle.md` §3 |

**Athens production used manual per-stage fires, not the orchestrator** — see [`../_workspace/planning/runtime/HANDOFF_2026_05_29_ATHENS_COMPLETE.md`](../_workspace/planning/runtime/HANDOFF_2026_05_29_ATHENS_COMPLETE.md) for why.

## Setup

```bash
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

API keys + `AI_ASSEMBLY_PROJECT_ROOT` live in `../.env` at the monorepo
root. PROJECT_ROOT resolves via `--project <path>` > `AI_ASSEMBLY_PROJECT_ROOT`
env > hard fail (per Tier 3 convention). See [`../README.md`](../README.md)
for run examples.
