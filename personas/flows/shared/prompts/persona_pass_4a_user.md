{# Pass 4a USER PROMPT — 1-arch-05 Part A (2026-04-23): per-chunk reads.

Pass 4a produces 7 Voice card fields from chunk 1.4 (moves + register +
vocabulary + analytical_context_voice) + cross-slices (available_pathe from
1.1 for period-vocabulary grounding; reasoning_method.summary from 1.3 for
voice-reasoning alignment) + cross_disciplinary_reframing subset of
interpretive_frames + primary_block from Pass 1d. #}

Chunk 1.4 — VOICE (moves + register + vocabulary + analytical_context_voice):

**moves** (uncapped list of named voice moves with descriptions + examples +
`structural_pattern_refs` linking to analytical_context_reasoning's
structural_patterns where relevant):

{{ moves }}

**register** (register_and_tone + genre_specific_register dict +
translator_tradition_notes per 1-arch-03):

{{ register }}

**vocabulary** (preferred_vocabulary as VocabEntry list with loadbearing
flag + translation_notes; metaphorical_repertoire dict):

{{ vocabulary }}

**analytical_context_voice** (scholarly-analytical material on voice —
stylistic-reception, translator-tradition scholarship, metaphor-family
scholarly mapping; may be null for voices without substantive voice-level
scholarly material):

{{ analytical_context_voice }}

Cross-slices from other chunks (for voice-alignment context):

**available_pathe** (sub-slice of chunk 1.1 life_scaffold — tradition-specific
pathe terms with native-language spellings + glosses). These inform
`preferred_vocabulary` + `metaphorical_repertoire`:

{{ available_pathe }}

**reasoning_method_summary** (sub-slice of chunk 1.3 reasoning_method.summary —
one-sentence voice-reasoning character; your voice fields must align with this):

{{ reasoning_method_summary }}

Cross-disciplinary interpretive frames (filtered to
`frame_type == "cross_disciplinary_reframing"` from chunk 1.2's
interpretive_frames). Use these for scholarly attribution in register notes
(e.g. postcolonial reading of the voice's register; disability-studies frame
on stammering-as-crip-performance; translator-tradition debates):

{{ cross_disciplinary_frames }}

Primary Text Passages (curated ~30K by Pass 1d — the voice's actual writing,
grounding your voice-characterization):

{{ primary_texts }}

Previously completed fields (summary):
{{ pass_2_3_summary }}

Produce 7 Persona Card voice fields (rhetorical_mode, characteristic_moves,
register_and_tone, metaphorical_repertoire, preferred_vocabulary,
banned_language, banned_modes). Output as JSON with exact field names as keys.

Return ONLY the JSON object. No markdown fences, no preamble.
