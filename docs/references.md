# References

Pointers into `docs/research/` and `_workspace/planning/` from the
production specs in `docs/`.

## Grounding research (`docs/research/baseline_research/`)

When a current spec says "per the baseline research" or you're
wondering why the architecture looks the way it does:

- **4-layer persona architecture** (RAG + constitution + reasoning
  templates + persona vectors) → `docs/research/baseline_research/compass_artifact_wf-cc778da2-1ac5-493e-b406-ab71d3b00234_text_markdown.md`
- **Multi-model research workflow** (Perplexity + Claude DR + Gemini)
  → `docs/research/baseline_research/compass_artifact_wf-45560dac-98db-4376-9002-5ee8e80bb4f5_text_markdown.md`
- **Section-by-section generation + 4-block prompt pattern** →
  `docs/research/baseline_research/compass_artifact_wf-865974da-a7be-4b7b-b770-0ec4fb7b1221_text_markdown.md`
- **Seven-faction audience analysis** (grounding `docs/AUDIENCE_BRIEF.md`)
  → `docs/research/baseline_research/compass_artifact_wf-109ac10a-edff-47ea-8c60-cf7d8565d408_text_markdown.md`
- **Biocultural critique of Persona Card v2** (Boddice's history of
  emotions; integration target = Phase B rebuild via PB#2 hybrid
  Jinja+LLM tailoring + PB#1 voice-type-specific 1a/1b prompts +
  PB#7 evidence tags) → `docs/research/baseline_research/compass_artifact_wf-1e84f45b-0c9f-497a-84bc-88b7867c9a26_text_markdown.md`

## Historical planning (`_workspace/archive/`)

- **Phase B persona pipeline rewrite** → archived at `_workspace/archive/planning_2026_04_consolidation/REBUILD_PLAN.md`. The 9 binding architectural decisions PB#1–9 plus the phase-by-phase task lists. **Status:** the Phase B rebuild shipped as Persona Pipeline **v4** (`docs/AI_Assembly_Persona_Pipeline_v4.md`) — REBUILD_PLAN.md is the historical design record, not active forward-looking work.

## Forward-looking planning (`_workspace/planning/`)

Active design work for unbuilt features lives in the two-workstream tracker
(`_workspace/planning/{runtime,voices}/OPEN_ITEMS.md`). The only forward-looking
spec at this writing is the vatican-2026 annotated-encyclical run at
`_workspace/planning/runtime/SPEC_2026_05_27_magnifica_humanitas_annotated_pipeline.md`
(spec landed, not started).
