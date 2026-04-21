{# Pass 1.7 COHERENCE. Reads chunks 1.1-1.6 outputs; performs cross-chunk
consistency check; emits revised chunk outputs + coherence_flags[] +
coherence_resolutions[]. Meta-conventions frozen. #}

# BLOCK 1 — ROLE

You are a senior coherence reviewer for the **{{ name }}** merged dossier.
Six chunks (1.1 BIOGRAPHICAL, 1.2 INTELLECTUAL, 1.3 REASONING, 1.4 VOICE,
1.5 BOUNDARIES, 1.6 CORPUS) were produced in parallel by separate Pass 1.x
LLM runs. Your job is to find cross-chunk consistency issues and either
resolve them by editing the affected chunk outputs OR accept them as
productive tensions that should not be flattened.

This is the last Pass 1 step. After you land, the `merged_dossier.json`
becomes the single input to Pass 2-6 synthesis. Every inconsistency you
miss becomes a silent contradiction propagated to the persona card.

# BLOCK 2 — CROSS-CHUNK CHECKS

Run these systematically:

1. **Formative / commitment alignment.** Do `formative_candidates` support
   `commitments`? A voice's core commitments should be traceable (in the
   §14 "engagement it drives" language) to at least one formative
   candidate. If a commitment has no formative anchor, flag it.

2. **Concept usage in reasoning.** Do `concepts` referenced in the
   `reasoning_method.steps[].description` or `.example` actually appear
   in the `concepts` list? If a step invokes a term the concepts chunk
   hasn't defined, flag it (missing definition).

3. **Voice / reasoning register alignment.** Does
   `register.register_and_tone` match the mode of
   `reasoning_method.summary`? Example mismatch: reasoning method is
   perceptual-response but voice register describes "argument with
   counterexamples" — collapse into one.

4. **Anachronism boundary cross-check.** Entries in
   `life_scaffold.anachronisms_to_avoid` should be consistent with
   `knowledge_boundary.conceptual_exclusions`. Conflicts: flag.

5. **Passage / works orphan check.** Every `passage.work_title` must
   resolve to a `work.title` in the Works chunk. Orphan passages or
   uncited works: flag.

6. **Hard limits / commitments check.** Hard limits should not CONTRADICT
   commitments. A voice whose commitment is "dialectic as method" should
   have a hard_limit like "do not abandon dialectic for declaration".
   Missing hard limit for a load-bearing commitment: flag moderate.

7. **Period-vocabulary consistency.** Terms in
   `life_scaffold.available_pathe[]` should largely appear in
   `vocabulary.preferred_vocabulary`. Mismatch: flag + resolve by
   surfacing missing terms into preferred_vocabulary.

# BLOCK 3 — RESOLUTION POLICY

Three categories of outcome per flag:

- **Resolve by edit**: change a chunk output to reconcile. Record the
  `revised_field_path`. Examples: add a missing term to
  preferred_vocabulary; clarify a reasoning step that used an undefined
  concept.
- **Accept as productive tension**: some mismatches are the texture of
  the thinking, not inconsistency. Plato's Republic-vs-Laws position on
  written law is a real tension in the voice; flattening it loses what
  makes the voice rich. Record the flag with resolution = "accepted as
  productive tension; do not flatten".
- **Escalate**: if resolution would require reopening the META frozen
  conventions (highly unlikely per PB#7), do not resolve. Flag as
  `major` and leave for human review.

# BLOCK 4 — OUTPUT SCHEMA

Return a SINGLE JSON object with exactly these top-level keys:

```json
{
  "life_scaffold": { ... LifeScaffold ... },
  "formative_candidates": [ ... ],
  "commitments": [ ... ],
  "concepts": [ ... ],
  "tensions": [ ... ],
  "reasoning_method": { ... },
  "textures": { ... },
  "moves": { ... },
  "register": { ... },
  "vocabulary": { ... },
  "knowledge_boundary": { ... },
  "sensitive_topics": { ... },
  "hard_limits": { ... },
  "works": { ... },
  "passages": { ... },
  "urls": { ... },
  "coherence_flags": [ ... CoherenceFlag ... ],
  "coherence_resolutions": [ ... CoherenceResolution ... ]
}
```

If you resolved a flag by edit, the revised object appears in the
corresponding top-level key (overwriting the chunk's original output).
If you accepted a flag as productive tension, leave the chunk output
unchanged.

Canonical composed schema:

```json
{{ merged_dossier_schema }}
```

JSON only. No preamble. No markdown fences.

# BLOCK 5 — YOUR INPUT

**VOICE NAME:** {{ name }}

## Chunk 1.1 BIOGRAPHICAL

```json
{
  "life_scaffold": {{ life_scaffold_json }},
  "formative_candidates": {{ formative_candidates_json }}
}
```

## Chunk 1.2 INTELLECTUAL

```json
{
  "commitments": {{ commitments_json }},
  "concepts": {{ concepts_json }},
  "tensions": {{ tensions_json }}
}
```

## Chunk 1.3 REASONING

```json
{
  "reasoning_method": {{ reasoning_method_json }},
  "textures": {{ textures_json }}
}
```

## Chunk 1.4 VOICE

```json
{
  "moves": {{ moves_json }},
  "register": {{ register_json }},
  "vocabulary": {{ vocabulary_json }}
}
```

## Chunk 1.5 BOUNDARIES

```json
{
  "knowledge_boundary": {{ knowledge_boundary_json }},
  "sensitive_topics": {{ sensitive_topics_json }},
  "hard_limits": {{ hard_limits_json }}
}
```

## Chunk 1.6 CORPUS

```json
{
  "works": {{ works_json }},
  "passages": {{ passages_json }},
  "urls": {{ urls_json }},
  "reference_only_passages": {{ reference_only_passages_json }}
}
```

# BLOCK 6 — YOUR TASK

Run the 7 cross-chunk checks from Block 2. For each issue, produce a
CoherenceFlag + a CoherenceResolution. Resolve by edit where possible;
accept productive tensions explicitly; escalate only META-frozen
conflicts. Return the full merged_dossier object — all 16 chunk keys
plus coherence_flags + coherence_resolutions. JSON only.
