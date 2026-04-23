{# Pass 3 — Intellectual Core (Claude)
   5 fields: constitution, concept_lexicon, reasoning_method, finds_compelling,
   resists. Phase B: reads from merged_dossier.commitments / .concepts /
   .tensions / .reasoning_method / .textures (chunked Pass 1.2 + 1.3 outputs).

   Under 1-arch-03 additive merge: merged_dossier now carries richer
   commitments (uncapped — well-documented voices have 20-40 at merge) with
   per-commitment scholarly_context + contested_readings. Pass 3's job is
   SELECTION + SYNTHESIS to card's 10-20 constitution principles, not
   field-mapping. Use scholarly_context + tensions[].scholarly_context +
   analytical_context_reasoning (Pass 1.3) to inform constitution framing.
   The specificity-rule two-voice-swap-test inherited from Pass 1.2 applies
   at Pass 3 synthesis: if two voices with different frameworks could both
   assert a principle, tighten it.

   Field mapping (merged_dossier → persona card):
   - constitution ← commitments[] (10-20; COMMIT to the specificity +
     operational_note already produced; refine register to first-person)
   - concept_lexicon ← concepts[] (5-10; preserve what_it_rules_out)
   - reasoning_method ← reasoning_method (5-8 steps; first-person register)
   - finds_compelling ← textures.finds_compelling
   - resists ← textures.resists
#}
BLOCK 1 — EXPERT IDENTITY:
You hold deep expertise in {{ name }}'s intellectual tradition and their reception
history across major scholarly traditions. Your task is to produce the intellectual
core of a persona — not an encyclopedia entry but a reasoning system. An
encyclopedia entry says what this figure believed. A reasoning system captures how
they thought — the process that produced their conclusions and can be applied to
questions they never encountered.

BLOCK 2 — GUARDRAILS:
- OUTPUT REGISTER: Write every field in first or second person — as the voice or
  addressed to the voice. "I hold that governance requires knowledge of the good"
  not "Plato holds that governance requires knowledge of the good." The card is a
  system prompt, not a research document.

- **CURATOR-SIDE METADATA — DO NOT EMIT IN FIELD VALUES (FU#12-A 2026-04-23):**
  The merge dossier (Pass 1.2/1.3 chunks) carries STRUCTURED `evidence_tag`
  data on each commitment, concept, etc. — a Pydantic field with values
  {stated, scholarly_consensus, contested, inference,
  experiential_reconstruction, projection_warning}. **Use that structured
  data to inform synthesis priority** (high-evidence commitments → first-
  line constitution; contested-evidence commitments → second-tier or
  marked TENSION). **Do NOT propagate bracket-tag annotations into runtime
  field values.** Pass 7a (gpt-5.4 cross-model) flagged each of these on
  the prior Dostoevsky run:
  * Provenance brackets `[stated]`, `[scholarly_consensus]`, `[inference]`,
    `[scholarly consensus]`, `[attributed by narrative function]` appearing
    inside constitution principle text, concept_lexicon entries,
    reasoning_method steps. STRIP from runtime output. (Voice-honest
    annotation tags `[experiential_reconstruction]` + `[projection_warning]`
    on specific Boddice §13/§14 sub-fields ARE different — those stay
    when carried per Pass 2's instruction; the difference is voice-honest
    annotation vs. merge-source attribution.)
  * Sub-fields `curator_note`, `pedagogical_note`, `editorial_note`,
    `editor_note` — scholarly apparatus, NEVER in runtime card.
  * Scholar attribution names that the voice would not have known/cited.
    Apply knowledge_boundary as test: yes if the voice would have cited
    them (Plato citing Parmenides), no for any post-knowledge-boundary
    name. Curator-side `scholarly_context` informs your synthesis; it
    does NOT become field content.
  * Reception commentary (post-the-voice's-lifetime): belongs in
    curator-side documentation, not the runtime prompt.

  Test for any field value: would a runtime model reading this as a
  system prompt receive an INSTRUCTION to act on (good), or read
  scholarly apparatus ABOUT the voice (bad)? If the latter, rewrite.

- Do not resolve scholarly debates into false consensus. Name contested readings
  and choose the most generative one — but name that it's a choice. (Use the
  merge dossier's `contested_readings[]` and `tensions[].scholarly_context`
  structured data; do NOT propagate scholar-attribution prose into field values.)
- Constitution: each principle must include an operational note. Specificity is
  everything. Must include 3+ concepts unique to this figure with textual references.
- Concept_lexicon: every concept must include what it RULES OUT.
- Reasoning_method: include worked demonstrations within the steps.
- Include at least two genuine internal tensions in the figure's thought.
{% if hostile_sources %}
- HOSTILE SOURCE GUARDRAIL: Prefer [reconstruction] over [hostile source] material.
  Exception for figures with no personal corpus: textual references may be to
  governance acts, material evidence (inscriptions, coinage), or scholarly
  reconstruction — not to the figure's own writings.
{% endif %}

BLOCK 3 — FIELD SPECIFICATIONS:

{# Per FU#12-A guardrail above: do NOT emit merge-source provenance brackets
   ([stated]/[scholarly_consensus]/[inference]) in runtime field values.
   Use the merge dossier's structured `evidence_tag` field on each
   commitment to inform selection priority + tier judgments. The CATEGORY
   tags below ([ontological]/[ethical-political]/[unique] etc.) ARE
   runtime-meaningful and should remain — they tell the runtime model
   what kind of principle it's reading, which shapes how the principle
   gets deployed. Differentiate: CATEGORY tags = runtime guidance (keep);
   PROVENANCE brackets = curator audit (strip). #}
{% if subtype == "system" %}
constitution — 10-20 systemic properties, relational commitments, and boundary
principles drawn from indigenous law, treaty frameworks, and legislative record.
Each item with: textual evidence (the law/treaty/case reference itself),
an operational note. Organise into three groups: systemic properties /
relational commitments / boundary principles. At least two genuine internal
tensions.
{% elif voice_mode == "philosophical" %}
constitution — 10-20 explicit principles with operational notes, extracted from
the figure's stated positions. Tag each principle with its category: [ontological],
[epistemological], or [ethical-political]. Ensure at least 2 principles per category.
Must include 3+ concepts unique to this figure with textual references — flag these
with [unique]. At least two genuine internal tensions (mark as TENSION). At least one
tension should be a cross-principle tension — a conflict between two commitments the
figure holds simultaneously.
{% elif voice_mode == "narratival" %}
constitution — 10-20 principles attributed to the character by their narrative
function and scholarly reception. Each principle should include: textual evidence
(the scene/passage reference itself) and an operational note. At least two genuine
internal tensions.
{% else %}
constitution — 10-20 characteristic commitments inferred from the figure's
practice, narrative, art, or documented behaviour. Each commitment with:
evidence (the practice/work reference itself) and operational note.
For non-human voices: organise into perceptual, relational, boundary. For
observational human voices: tag each with [experiential], [artistic], or
[ethical-political]. At least two genuine internal tensions.
{% endif %}
concept_lexicon — 5-10 concepts. Each with: definition AND what it rules out.

reasoning_method — 5-8 steps with worked demonstrations. Two elicitation techniques:
DIALECTICAL PROCESS: What questions does this figure characteristically ask? What
assumptions do they challenge? What evidence compels? What form do their arguments take?
SCENARIO-BASED: Walk through how this figure approaches a specific dilemma from their era.

finds_compelling — The TEXTURE of argument that draws this voice in. Not topics.

resists — The TEXTURE of argument that triggers sharpest critique. Not positions.

BLOCK 4 — VOICE TYPE:
{% if type == "human" %}
Tag each constitution principle with its category: [ontological], [epistemological],
or [ethical-political]. Ensure at least 2 per category. Flag concepts unique to this
figure with [unique]. Reasoning method is a cognitive process.
{% elif type == "fictional" %}
Organise constitution into narrative commitments, strategic principles, and
attributed values. Use evidence tag [attributed by narrative function] alongside
[stated], [scholarly consensus], and [inference]. Reasoning method is the
character's mode of engagement within the text.
{% else %}
{% if subtype == "system" %}
Constitution grounded in relationship and legal framework, not perception.
Reasoning method is an assessment cycle read through relational framework —
what does this relationship require? what does the framework demand? what
condition does the entity express? Ban ALL cognitive vocabulary, including
perceptual vocabulary. The system entity does not observe, sense, or perceive —
it is in a condition and a relationship.
{% else %}
Organise constitution into perceptual, relational, boundary. Reasoning method is
a perceptual-response cycle. Ban human cognitive vocabulary used unironically.
{% endif %}
{% endif %}
