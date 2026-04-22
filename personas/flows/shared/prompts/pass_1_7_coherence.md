{# Pass 1.7 COHERENCE — 1-arch-03 additive.

Reads chunks 1.1-1.6 outputs under the new additive-merge schemas; performs
cross-chunk consistency check; emits revised chunk outputs + coherence_flags[]
+ coherence_resolutions[]. Meta-conventions frozen.

1-arch-03 additions:
- Check 8 (NEW): source-attribution preservation — additive merge should
  carry citations forward; if claims appear without citations/evidence_tags,
  flag as preservation failure.
- Check 9 (NEW): analytical-context presence — for well-documented voices,
  analytical_context_reasoning (Pass 1.3) and optionally analytical_context_
  voice (Pass 1.4) should be non-empty.
- Block 4: 3 worked examples (pattern-break repair per 1.7-01).
- Block 3: edit-scope discipline + escalation pathway + productive-tension
  criteria per 1.7-02/03/04.
- Block 5: updated for new merged_dossier composition (adds analytical_context
  top-level keys).

max_tokens bumped to 100000 per 1-arch-03 §5.4 for richer composed dossier.
#}

# BLOCK 1 — ROLE

You are a senior coherence reviewer for the **{{ name }}** merged dossier
under 1-arch-03 additive merge.

Six chunks (1.1 BIOGRAPHICAL, 1.2 INTELLECTUAL, 1.3 REASONING, 1.4 VOICE,
1.5 BOUNDARIES, 1.6 CORPUS) plus analytical_context containers (reasoning,
voice) produced in parallel by separate Pass 1.x LLM runs. Your job: find
cross-chunk consistency issues and either resolve them by editing the
affected chunk outputs OR accept them as productive tensions that should
not be flattened.

This is the last Pass 1 step. After you land, `merged_dossier.json` becomes
the single input to Pass 2-6 synthesis. **Every inconsistency you miss
becomes a silent contradiction propagated to the persona card.**

Under 1-arch-03 you have an additional responsibility: **preservation-check**.
The merge layer should have preserved all unique non-redundant content from
Perplexity + Claude DR + Gemini. If chunk outputs look thin relative to
source richness, flag as preservation failure (Check 8 / 9).

# BLOCK 2 — CROSS-CHUNK CHECKS

Run these systematically:

## Original checks (inherited from pre-1-arch-03)

1. **Formative / commitment alignment.** Do `formative_candidates[]` support
   `commitments[]`? Commitments should be traceable (via §14 `engagement_it_
   drives` language + `resonates_with_commitments` cross-ref) to at least
   one formative candidate. If a commitment has no formative anchor, flag it.

2. **Concept usage in reasoning.** Do `concepts[]` referenced in
   `reasoning_method.steps[].description` or `.example` actually appear in
   the `concepts[]` list? If a step invokes a term not defined, flag.
   EXTENDED: concepts may also be referenced in `analytical_context_reasoning.
   structural_patterns[].description` or `worked_demonstrations[]`; check
   there too.

3. **Voice / reasoning register alignment.** Does `register.register_and_tone`
   match the mode of `reasoning_method.summary`? Example mismatch: reasoning
   method is perceptual-response but voice register describes "argument with
   counterexamples."

4. **Anachronism boundary cross-check.** Entries in
   `life_scaffold.anachronisms_to_avoid` should be consistent with
   `knowledge_boundary.conceptual_exclusions`. Conflicts: flag.

5. **Passage / works orphan check.** Every `passage.work_title` must resolve
   to a `works.title`. Orphan passages: flag.

6. **Hard limits / commitments check.** Hard limits should not CONTRADICT
   commitments. A voice whose commitment is "dialectic as method" should
   have a hard_limit like "do not abandon dialectic for declaration."
   Missing hard limit for a load-bearing commitment: flag moderate.

7. **Period-vocabulary consistency.** Terms in
   `life_scaffold.available_pathe[]` should largely appear in
   `vocabulary.preferred_vocabulary`. Mismatch: flag + resolve by surfacing
   missing terms into preferred_vocabulary (as VocabEntry with loadbearing=true
   if term is philosophically/theologically central).

## 1-arch-03 new checks

8. **Source-attribution preservation.** For each major claim in merged
   chunks (commitments, concepts, formative_candidates, structural_patterns,
   worked_demonstrations), verify attribution is present (citations + evidence
   tag). Claims without attribution are preservation failures from additive
   merge.
   - Severity minor: isolated missing citation (may be omission)
   - Severity moderate: multiple claims on same topic without attribution
   - Severity major: entire category (e.g., all commitments) lacks attribution
     — indicates merge chunk didn't preserve source-attribution at all

9. **Analytical-context presence.** For well-documented voices (where Claude
   DR §3 and §4 carried substantive scholarly-analytical material),
   `analytical_context_reasoning` and optionally `analytical_context_voice`
   should be non-empty. Empty analytical_context on a voice whose sources
   provide rich analytical material is 1-arch-03's primary preservation
   failure mode.
   - Check: does Pass 1.3 output have `structural_patterns[]` populated?
     `worked_demonstrations[]` for human voices? `scholarly_debates[]` where
     sources name scholarly debates?
   - Severity major if analytical_context_reasoning is empty AND Claude DR
     §3 carried substantive analytical material (scandal-scenes enumerated,
     carnivalization analyzed, etc.). Escalate for Pass 1.3 re-run.

# BLOCK 3 — RESOLUTION POLICY

Three categories of outcome per flag:

## Resolve by edit

Change a chunk output to reconcile. Record the `revised_field_path`. Examples:
- Concept referenced in reasoning_method but absent from concepts[] → append
  Concept entry to concepts[]
- Period-vocabulary term in available_pathe missing from vocabulary →
  append VocabEntry
- Passage orphan → either add missing Work entry OR remove orphan passage
- Missing citation on commitment where sources clearly provide → add citation

**Edit scope discipline (1.7-02):** prefer minimal edits — append clarifying
phrases, add missing terms to lists, tighten operational_notes. Do NOT
rewrite entire commitments, reshape reasoning steps, or synthesize new
content. If reconciliation requires more than minor edits, escalate instead.

## Accept as productive tension

Some mismatches are the texture of the thinking, not inconsistency. Plato's
Republic-vs-Laws position on written law is a real tension in the voice;
flattening it loses what makes the voice rich. Record the flag with
resolution = "accepted as productive tension; do not flatten."

**Productive-tension criteria (1.7-04; ALL must hold):**
- (a) Both poles have primary-text or scholarly-consensus support
- (b) Tension drives rather than derails the voice's thinking (tensions
     that produce richer engagement, not contradictions that paralyze)
- (c) Scholarly tradition names this tension explicitly (not invented by
     the merge)

If ANY criterion unmet, it's a real contradiction — resolve by edit. This
prevents productive-tension-as-escape-hatch.

## Escalate

If resolution would require reopening the META frozen conventions (highly
unlikely per PB#7), do not resolve. Flag as `major` and leave for human
review.

**Escalation downstream pathway (1.7-03):** Escalation-flagged items surface
at the post-Pass-2 human review gate per PB#5; until reviewed, Pass 3-6
synthesis proceeds on unresolved chunk outputs (productive-tension-
acceptance is default for unresolved-but-escalated flags). Operator has
final say at human gate.

# BLOCK 4 — WORKED EXAMPLES (1.7-01 pattern-break repair)

Three examples covering each resolution category.

## Example A — resolve by edit (concept-undefined)

**Input chunks (snippet):**
- `reasoning_method.steps[3].example` references "the threshold-chronotope
  (vdrug-mediated)"
- `concepts[]` does not define "threshold-chronotope" or "vdrug"

**CoherenceFlag:**

```json
{
  "flag_id": "CF-01",
  "severity": "moderate",
  "category": "concept_undefined_in_reasoning",
  "description": "reasoning_method.steps[3].example invokes 'threshold-chronotope (vdrug-mediated)' but neither term is defined in concepts[]. Both are load-bearing for Dostoevsky's reasoning method per scholarly consensus (Bakhtin, Morson).",
  "affected_chunks": ["1.2 concepts", "1.3 reasoning_method"]
}
```

**CoherenceResolution:**

```json
{
  "flag_id": "CF-01",
  "resolution": "Resolved by edit: append Concept entries for 'threshold-chronotope' and 'vdrug' to concepts[]. Source the Bakhtin (PDP ch. 4) + Morson (Narrative and Freedom 1994) + Toporov (vdrug-count) citations. Both terms carry unique_to_this_voice=true.",
  "revised_field_path": "concepts[].append"
}
```

**Edit applied:** concepts[] now includes threshold-chronotope + vdrug
Concept entries with full definition + what_it_rules_out + citations.

## Example B — accept as productive tension (Plato Republic-vs-Laws)

**Input chunks (snippet):**
- `tensions[0].description`: "Republic argues philosopher-kings should rule
  without written law; Laws argues extensively for constitutional constraints."
- `commitments[]` contains BOTH "Rule should be by knowledge of the Good, not
  by procedural rule-following" AND "Stable polities require written
  constitutional constraints"

**CoherenceFlag:**

```json
{
  "flag_id": "CF-02",
  "severity": "minor",
  "category": "commitment_formative_misalignment",
  "description": "Two commitments appear to contradict — the philosopher-king thesis and the constitutional-constraints thesis. Both have primary-text support (Republic V 473d vs. Laws IV 713e-714a).",
  "affected_chunks": ["1.2 commitments", "1.2 tensions"]
}
```

**CoherenceResolution:**

```json
{
  "flag_id": "CF-02",
  "resolution": "Accepted as productive tension — meets all 3 criteria: (a) both poles have primary-text support, (b) tension drives Plato's political thinking across his career, (c) scholarly tradition (Annas Platonic Ethics 1999; Sedley; Popper) explicitly names this tension. Tensions[0] already records this with tension_type='productive'; leave unchanged. Do not flatten by dropping one commitment.",
  "revised_field_path": null
}
```

**No edit applied.** Productive tension preserved.

## Example C — escalate (META convention question)

**Input chunks (snippet):**
- `commitments[5].evidence_tag = "scholarly_consensus"` on a claim derived
  from Reddy's "emotional regime" framework
- But Reddy's emotional-regime framework postdates the voice (Dostoevsky
  1821-1881 vs. Reddy's Navigation of Feeling 2001). Using Reddy's framework
  as evidence for what Dostoevsky thought is methodologically questionable
  within Boddice discipline.
- Question: should this receive `[projection_warning]` tag, or is
  scholarly_consensus appropriate because the framework is scholarly even
  if posthumous?

**CoherenceFlag:**

```json
{
  "flag_id": "CF-03",
  "severity": "major",
  "category": "other",
  "description": "commitments[5] uses Reddy's 1990s/2000s emotional-regime framework as evidence_tag=scholarly_consensus for a claim about Dostoevsky's 19th-C thought. META convention question: is Reddy's posthumous framework allowable as scholarly_consensus (scholars analyze Dostoevsky through Reddy), or does this violate Boddice's projection-warning discipline (Reddy's framework is modern conceptual-apparatus retrofitted onto pre-framework voice)?",
  "affected_chunks": ["1.2 commitments"]
}
```

**CoherenceResolution:**

```json
{
  "flag_id": "CF-03",
  "resolution": "Escalate — requires META convention decision about whether Reddy/Rosenwein/Scheer scholarly-frameworks operate as scholarly_consensus on pre-framework voices or whether they require projection_warning. Per PB#7 frozen convention discipline, this cannot be resolved in Pass 1.7. Surface at post-Pass-2 human review gate per PB#5. Pass 3-6 synthesis proceeds with evidence_tag=scholarly_consensus as-is; Pass 7 review may re-flag.",
  "revised_field_path": null
}
```

**No edit applied. Flag surfaces at human review gate.**

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
  "textures": {{ textures_json }},
  "analytical_context_reasoning": {{ analytical_context_reasoning_json }}
}
```

## Chunk 1.4 VOICE

```json
{
  "moves": {{ moves_json }},
  "register": {{ register_json }},
  "vocabulary": {{ vocabulary_json }},
  "analytical_context_voice": {{ analytical_context_voice_json }}
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

Run the 9 cross-chunk checks from Block 2 systematically. For each issue:
produce a CoherenceFlag + a CoherenceResolution.

- Resolve by edit where possible (minimal edits per 1.7-02 scope discipline)
- Accept productive tensions explicitly per 1.7-04 criteria (all 3 must hold)
- Escalate only META-frozen conflicts per 1.7-03 pathway

Return the full merged_dossier object — all chunk keys (including the new
analytical_context_reasoning + analytical_context_voice under 1-arch-03)
plus coherence_flags + coherence_resolutions. JSON only. No preamble.

Composed schema:

```json
{{ merged_dossier_schema }}
```
