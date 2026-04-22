{# Pass 3 USER PROMPT — 1-arch-05 Part A (2026-04-23): per-chunk reads.

Pass 3 produces 5 Intellectual Core card fields from chunks 1.2 + 1.3 +
interpretive_frames (filtered by frame_type to interpretive_method +
cross_disciplinary_reframing subsets — voice_level_debate frames belong
to Pass 2 / topics_requiring_care). #}

Chunk 1.2 — INTELLECTUAL (commitments + concepts + tensions + interpretive_frames):

**commitments** (uncapped list with scholarly_context + contested_readings
per 1-arch-03):

{{ commitments }}

**concepts** (uncapped list with translation_tradition_notes per 1-arch-03):

{{ concepts }}

**tensions** (productive / contested / unresolved per tension_type discriminator;
must surface ≥2 in your constitution output per card spec):

{{ tensions }}

**interpretive_frames** (per 1-arch-06, top-level container for cross-cutting
scholarly material). Filter to `frame_type ∈ {interpretive_method,
cross_disciplinary_reframing}` for your synthesis — `voice_level_debate` is
Pass 2's concern. Interpretive methods (Kasatkina subject-to-subject,
hesychast reading, Patyk provocation frame, Vetlovskaya narrator-as-programmatic-
frame) inform `constitution.operational_note` + `concept_lexicon` scholarly
attribution. Cross-disciplinary re-framings (postcolonial, feminist, affect
theory, legal-economic, disability studies, ecological, Mauss/Levinas)
enrich how the voice's commitments are read by contemporary scholars; cite
them in `constitution.scholarly_context` where load-bearing:

{{ interpretive_frames }}

Chunk 1.3 — REASONING (reasoning_method + textures + analytical_context_reasoning):

**reasoning_method** (summary + steps — the RECIPE for how the voice reasons;
you produce a card field of the same name which DISTILLS to 5-8 operational
steps):

{{ reasoning_method_chunk }}

**textures** (finds_compelling[] + resists[] — what activates the voice's
strongest thinking vs. what triggers critique):

{{ textures }}

**analytical_context_reasoning** (arch-03's big preservation win:
structural_patterns[] — named recurring reasoning forms like scandal-scene,
carnivalization, threshold-chronotope; worked_demonstrations[] — specific
historical events that produced specific rhetorical-textual responses;
scholarly_debates[] — named interpretive traditions on the voice's reasoning
like Williams-vs-Frank on Myshkin failure, Morson-vs-Emerson on
polyphony-vs-carnivalization). Incorporate structural_patterns into
`reasoning_method.steps[]` examples; weave worked_demonstrations into
operational narrative; surface scholarly_debates in scholarly_context
attribution. DO NOT drop this material — it is the Phase-L failure mode
arch-03 was built to prevent.

{{ analytical_context_reasoning }}

Previously completed fields (summary):
{{ pass_2_summary }}

Produce 5 Persona Card fields (constitution, concept_lexicon, reasoning_method,
finds_compelling, resists). Output as JSON with exact field names as keys.

Return ONLY the JSON object. No markdown fences, no preamble.
