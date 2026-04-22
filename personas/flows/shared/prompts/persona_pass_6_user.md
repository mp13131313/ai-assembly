{# Pass 6 USER PROMPT — 1-arch-05 Part A (2026-04-23): per-chunk reads.

Pass 6 produces the `curated_corpus_passages` card field from chunk 1.6
(works + passages + reference_only_passages) + primary_block from Pass 1d +
card-field references from prior passes (constitution, concept_lexicon,
reasoning_method, rhetorical_mode, characteristic_moves, register_and_tone
— for selection criteria). #}

Primary Text Passages (curated ~30K by Pass 1d — the corpus source you
select FROM for card embedding):

{{ primary_texts }}

Chunk 1.6 — CORPUS (works + passages + reference_only_passages):

**works** (uncapped bibliographic catalogue with tier + source_type per entry
+ bibliographic_scholarly_context per 1-arch-03 — named scholarly-corpus
debates). `urls` chunk was removed under 1-arch-07 — URL inventory is
derived at render-time from passages[].citation + works[] string fields:

{{ works }}

**passages** (Pass 1.6's scholar-flagged passage index with purpose_tags —
voice_exemplar, intellectual_substance, biographical_ground — plus
translator_tradition_coverage per 1-arch-03). Use the purpose_tags and
scholarly-tier metadata to prioritize which passages become card-embedded
`curated_corpus_passages`:

{{ passages }}

**reference_only_passages** (private tier — copyrighted translations or
other reference material loaded at Step 1 only, dropped at Step 2. NEVER
include in curated_corpus_passages (which is Step-2-safe). Pass-through
to final card unchanged):

{{ reference_only_passages }}

Previously completed fields (summary):
{{ pass_2_3_4a_summary }}

Intellectual core (what arguments matter — read in full, do not paraphrase):
{{ constitution }}

{{ concept_lexicon }}

{{ reasoning_method }}

Voice specification (what voice patterns to exemplify — read in full):
{{ rhetorical_mode }}

{{ characteristic_moves }}

{{ register_and_tone }}

Produce 1 Persona Card field: curated_corpus_passages. Output as JSON with
that exact field name as the key, and the value being the {corpus_metadata,
passages} object as specified in the system prompt.

Return ONLY the JSON object. No markdown fences, no preamble.
