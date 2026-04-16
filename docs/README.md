# docs/ — Pipeline specs and briefing documents

> **Read this first.** Not all files here are current. This index tells you which to trust.

## Current (authoritative as of 2026-04-16)

| File | Status | Notes |
|------|--------|-------|
| `AI_Assembly_Briefing_v2.md` | **Current** | Project source of truth. Supersedes Briefing v1. |
| `AI_Assembly_Persona_Card_v2.md` | **Current** | 37-field card template. |
| `AI_Assembly_Persona_Pipeline_v3_7.md` | **Current** | Persona build pipeline v3.7. |
| `AI_Assembly_Researcher_Pipeline.md` | **Current** | Researcher extraction and grouping (v3). |
| `AI_Assembly_Provocateur_Pipeline.md` | **Current** | Triage, selection, formulation, packaging (v2). |
| `AI_Assembly_Transcription_Pipeline.md` | **Current** | Audio to clean transcript pipeline (v2.1). |
| `AI_Assembly_Voice_Pipeline.md` | **Partial** | Covers Steps 1+2 only. Step 3 Amendment (per Briefing v2) is unspecified — spec not yet written. |

## Stale

| File | What's stale |
|------|-------------|
| `AI_Assembly_Architecture_v1.md` | Describes n8n orchestration, but the actual implementation is pure Prefect flows. Describes a 2-step voice pipeline; Briefing v2 has 3 steps. Describes 2 conference nights; Briefing v2 has 3. Missing: closing-show pipelines, Governance Matrix A/B split, Day 4 goodbye sequence, and the changed newsletter delivery model (standalone HoBB newsletter → blurb + Substack read-through). |
| `AI_Assembly_Infrastructure_Setup.md` | Describes rclone/Google Drive mount and n8n Docker, but the actual ingest is a FastAPI upload app writing to local disk with pure Prefect flows. Pre-flight checklist references n8n and Drive. |

When these stale docs conflict with `AI_Assembly_Briefing_v2.md` or the code in `runtime/`, trust the briefing and the code.
