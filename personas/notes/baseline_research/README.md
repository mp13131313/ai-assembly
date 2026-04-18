# Baseline Research

Deep-research artifacts that ground downstream work in the repo.

The **first three** (2025–early 2026) were commissioned before the Persona Pipeline was designed and shaped its architecture, the 3-tool research phase, the 4-block prompt pattern, the failure-mode mitigations, and the non-human voice methodology. Their target spec is `docs/AI_Assembly_Persona_Pipeline_v3_10.md`.

The **fourth** (2026-04) grounds the audience brief at `docs/AUDIENCE_BRIEF.md` — faction analysis and reception-condition modeling for the Athens 2026 audience. Its target is the `audience` paragraph in `runtime/flows/shared/council/council_config.json` and the audience section of the Briefing (`docs/AI_Assembly_Briefing_v3_1.md`).

**These are source reference, not active spec.** When they conflict with the canonical docs they ground, trust the doc. The specs are the operationalized version; these are what they were operationalized from.

## The four files

### `compass_artifact_wf-cc778da2-1ac5-493e-b406-ab71d3b00234_text_markdown.md`
**"Building faithful AI philosophers: a technical blueprint for The AI Assembly"**

Architectural blueprint. 4-layer stack (RAG + constitution + reasoning templates + persona vectors), GraphRAG for philosophical texts, 4-phase pipeline, lessons from Khanmigo/Habermas Machine/Generative Agents, 5 failure modes with mitigations, non-human and Indigenous methodology.

Source for: overall 4-layer architecture, constitutional steering, persona-as-reasoning-system-not-knowledge-system, non-human methodology.

### `compass_artifact_wf-45560dac-98db-4376-9002-5ee8e80bb4f5_text_markdown.md`
**"AI deep research tools for structured persona documents: a 2026 field guide"**

Tool comparison. Perplexity vs ChatGPT DR vs Claude on task-specific strengths. 5-phase multi-AI synthesis workflow. Prompt engineering for template population. Benchmark analysis (DeepResearch Bench, PersonaGym, TimeChara, CharacterBench).

Source for: the 3-tool research phase architecture (Perplexity + Gemini + Claude DR), multi-pass reasoning, cross-model verification (10-25% self-preference bias rationale).

### `compass_artifact_wf-865974da-a7be-4b7b-b770-0ec4fb7b1221_text_markdown.md`
**"A repeatable AI pipeline for building 13 philosophical personas"**

Operational playbook. Tool-to-section matching table, multi-pass generation with coherence threading, 4-block prompt architecture (Expert Identity / Guardrails / Field Specs / Voice Type), 4-6 week workflow, 4-phase verification protocol, 6 failure modes with guardrails.

Source for: section-by-section generation pattern, 4-block prompt architecture used in every generation pass, dialectical-process + scenario-based elicitation prompts, the ontological-construction-from-constraint methodology for non-humans.

### `compass_artifact_wf-109ac10a-edff-47ea-8c60-cf7d8565d408_text_markdown.md`
**"The intellectual terrain of Athens 2026"**

Audience research grounding `docs/AUDIENCE_BRIEF.md`. Faction-by-faction reading of the 202 WBBF Athens contributors (seven factions with canons, positions, blind spots, and specific speakers per faction), the four engineered tensions the curators staged, the Aegean intellectual layer as substantive-but-precarious, the five-act dramaturgy as argument, ten hardest-to-please voices ranked by specificity of their published positions, and what AI-mediated deliberation formats face in this particular room.

Source for: the audience paragraph in `runtime/flows/shared/council/council_config.json`, the audience + "seven factions" framing in `docs/AI_Assembly_Briefing_v3_1.md` §The audience, and any future refinement of Triage Part B's `audience_friction` judgment from monolithic to faction-aware.

## How to use these

- Reading a spec and wondering "why this way?" → check here first
- Designing a new pass or extension → check which existing pattern it extends (Files 1–3)
- Encountering a failure mode → the mitigation is likely already here (Files 1–3)
- Extending to a new voice type → the 4-block pattern + methodology sections are the template (Files 1–3)
- Tuning Provocateur audience judgment or sharpening the `audience` paragraph → File 4
- Designing the AIssembly's reception at Athens → File 4 §"What AI-mediated deliberation faces in this room"

## What's in the research but NOT in the current pipeline (potential future work)

- **Persona vectors / activation steering** (File 1 Layer 4). Anthropic's Persona Vector Distillation technique. Would require LoRA-based fine-tuning. Current pipeline is prompt-engineering + RAG only.
- **GraphRAG with Neo4j + Weaviate** (File 1). Knowledge-graph layer with entity/relationship extraction. Current pipeline does plain RAG (Pass 1c fetches, Pass 1d curates).
- **Fine-tuning approaches** (File 1: Character-LLM, Neeko MoE, OpenCharacter). Current pipeline is pure prompt engineering — deliberately, per prosumer-infrastructure framing in Briefing v3.1.
- **Benchmark-based automated eval** (CharacterBench / TimeChara / RoleKE-Bench). Current Pass 7a is a cross-model check but not benchmark-based.
