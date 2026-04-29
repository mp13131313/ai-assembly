# docs/ — Pipeline specs and briefing documents

> **Read this first.** Not all files here are current. This index tells you which to trust.

## Current (authoritative as of 2026-04-28)

| File | Status | Notes |
|------|--------|-------|
| `CURRENT_STATE.md` | **Current** (rewritten 2026-04-27) | Gap analysis + architectural rationale (§5.16–5.28 cover the v3.10 → v4 shift). Read alongside the briefing. |
| `AI_Assembly_Briefing_v3_1.md` | **Current** | Project source of truth. Supersedes Briefing v2 (deleted). Adds prosumer/infrastructure second-order provotype condition. |
| `AI_Assembly_Persona_Card_v2.md` | **Current** (v2 schema; v2.1 amendments 2026-04-27) | 35-generated + 2-continuity-null + metadata-block schema. v2.1 amendments section near top covers FU#41 chat artifact, FU#49 universal patterns, Boddice tag preservation, Position B vs C, updated `metadata` block. |
| `AI_Assembly_Persona_Pipeline_v4.md` | **Current** (2026-04-27) | Persona build pipeline v4. Replaces v3.10 spec. Reflects arch-03 chunked merge (Pass 1.1–1.7), Phase B per-voice layout, Tier 3 separation, Pass 6.5-clean (FU#33 P1), FU#2 chunked Pass 7-pre, FU#13 linear patcher, FU#41 chat artifact, FU#49 universal patterns. |
| `AI_Assembly_Researcher_Pipeline.md` | **Current** | Researcher extraction and grouping (v3). Validated on dev_msc_test. |
| `AI_Assembly_Provocateur_Pipeline.md` | **Current** | Triage, selection, formulation, packaging (v2). Validated on dev_msc_test. |
| `AI_Assembly_Transcription_Pipeline.md` | **Current** | Audio to clean transcript pipeline (v2.1). Validated on 3 MSC test sessions. |
| `AI_Assembly_Voice_Pipeline.md` | **Current** (v2 fresh-write 2026-04-28) | Replaces v1 partial. Steps 1+2+3 + validation + continuity end-to-end. Field-routing matrix for all 36 generated card fields. FU#49E reviewer framing wired into Step 3 verbatim. Family-of-forms selection in Step 2 (Card v2.1 §H). 10-voice panel. Implementation pending. |
| `AUDIENCE_BRIEF.md` | **Current** (refreshed 2026-04-26 for athens-2026 deployment) | Audience characterization + contributors-vs-audience distinction. |

## Partial / pending update

| File | Status | Notes |
|------|--------|-------|
| `LLM_CALL_INVENTORY.md` | **Current** (rewritten 2026-04-27) | Updated for arch-03 chunked merge (Pass 1.1–1.7), Pass 0b tailor, Pass 6.5-clean, Pass 7-pre 3-stage (FU#2), Pass 7-anachronism, Pass 7a-FIX linear patcher (FU#13), FU#41 chat builder. 5-model fallback ladder for Pass 7-anach + Pass 7a (gpt-5.4 high → gpt-4.1 → o3 → gpt-4o → Gemini 2.5 Pro). Does not yet include Voice Pipeline calls — add after Voice Pipeline implementation lands. |

## Archived / stale

| File | What's stale |
|------|-------------|
| `_archive/AI_Assembly_Persona_Pipeline_v3_10.md` | Superseded by v4 (2026-04-27). Body retained as historical record (changelog from v2.0 → v3.10 is preserved there). |
| `_archive/AI_Assembly_Voice_Pipeline_v1_partial.md` | Superseded by v2 (2026-04-28). v1 covered Steps 1+2 conceptually only; omitted Step 3; was stale on `voice_temporal_stance`, family-of-forms, tense discipline, and 10-voice panel. Body retained for historical context. |
| `_workspace/archive/specs/AI_Assembly_Architecture_v1.md` | Describes n8n orchestration; actual implementation is pure Prefect. 2-step Voice Pipeline; Briefing v3.1 has 3 steps. 2 nights; Briefing v3.1 has 3 + Day 4 goodbye. Missing closing-show pipelines, Matrix A/B, Substack delivery model. |
| `_workspace/archive/specs/AI_Assembly_Infrastructure_Setup.md` | Describes rclone/Drive mount + n8n Docker + file watcher; actual is FastAPI upload + pure Prefect + status.json state machine. Pre-flight checklist references obsolete elements. |

When archived/stale docs conflict with `AI_Assembly_Briefing_v3_1.md`, `CURRENT_STATE.md`, or the code in `runtime/`+`personas/`, trust the current docs and the code.

## What's NOT in `docs/`

- **`research/`** — preserved grounding material (5 Deep Research compass artifacts). Not deletable. When you want to know *why* the pipeline is designed the way it is, look here.
- **`_workspace/planning/`** — forward-looking design + active follow-ups. Currently:
  - `HANDOFF_2026_04_27.md` — current session pickup
  - `FOLLOW_UPS.md` — active follow-up tracker (FU#1–50 family)
  - `ONBOARDING.md` — permanent fresh-session pickup
- **`_workspace/archive/`** — historical record (executed fix plans, stale specs, session artifacts). Out of scope for code reviews by default.
