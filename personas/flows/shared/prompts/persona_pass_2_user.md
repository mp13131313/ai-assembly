{# Pass 2 USER PROMPT — 1-arch-05 Part A (2026-04-23): per-chunk reads.

Pass 2 produces 10 Identity + Boundaries card fields from chunks 1.1 + 1.5
plus voice-level-debate interpretive_frames subset. Under 1-arch-05 the
per-chunk source-of-truth files drive this pass directly; the prior
`{{ merged_dossier }}` single-blob rendering is replaced by named
chunk-content variables. #}

Chunk 1.1 — BIOGRAPHICAL (life scaffold + formative candidates):

**life_scaffold** (name, dates, family, career, pathe, worldview, ontological
furniture, framework for difficulty, model of selfhood, scholarly_context +
contested_readings):

{{ life_scaffold }}

**formative_candidates** (uncapped list of threshold experiences with
emotional-community + apparatus/condition + engagement-drive-claim per
Boddice §14, plus `resonates_with_commitments` cross-refs for Pass 3
alignment):

{{ formative_candidates }}

Chunk 1.5 — BOUNDARIES (knowledge boundary + sensitive topics + hard limits):

**knowledge_boundary** (general_frame + temporal/geographic/conceptual
exclusions + `anachronism_discipline[]` with dual framings per 1-arch-08 —
pluck `biographical_framing` for your `world.anachronisms_to_avoid` card
field and `epistemic_framing` for your `knowledge_boundary.conceptual_exclusions`
card field narrative):

{{ knowledge_boundary_chunk }}

**sensitive_topics** (topics with what_the_voice_actually_thought +
navigation_guidance + scholarly_reception per 1-arch-03):

{{ sensitive_topics }}

**hard_limits** (character-breaking prohibitions):

{{ hard_limits_chunk }}

Voice-level debates (filtered subset of interpretive_frames where
frame_type == "voice_level_debate", e.g. antisemitism structural-vs-
incidental, Myshkin failure intrinsic-vs-character-limitation). Use these
to inform `topics_requiring_care` nuance — name the controversies scholars
have about the voice as a whole:

{{ voice_level_debate_frames }}

Produce 10 Persona Card fields. Output as JSON with exact field names as keys:
council_member_name, epistemic_frame_statement, world, formative_experience,
character, knowledge_boundary, voice_temporal_stance, translation_protocol,
topics_requiring_care, hard_limits.

`voice_temporal_stance` is a deployment-configurable field per 1-arch-03
fix 2-02 — produce object with `default` (fluid-across-time, mandatory) and
optional `anchored_override` (death-threshold or period-specific anchor for
chat/project deployments). See system prompt Block 3 for spec.

Return ONLY the JSON object. No markdown fences, no preamble.
