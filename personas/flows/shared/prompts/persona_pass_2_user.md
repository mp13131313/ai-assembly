Research Dossier:
{{ merged_dossier }}

Produce 10 Persona Card fields. Output as JSON with exact field names as keys:
council_member_name, epistemic_frame_statement, world, formative_experience,
character, knowledge_boundary, voice_temporal_stance, translation_protocol,
topics_requiring_care, hard_limits.

`voice_temporal_stance` is a deployment-configurable field per 1-arch-03
fix 2-02 — produce object with `default` (fluid-across-time, mandatory) and
optional `anchored_override` (death-threshold or period-specific anchor for
chat/project deployments). See system prompt Block 3 for spec.

Return ONLY the JSON object. No markdown fences, no preamble.
