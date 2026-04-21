{# Pass 3 — Intellectual Core (Claude)
   5 fields: constitution, concept_lexicon, reasoning_method, finds_compelling,
   resists. Phase B: reads from merged_dossier.commitments / .concepts /
   .tensions / .reasoning_method / .textures (chunked Pass 1.2 + 1.3 outputs).

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
- Only attribute direct quotes from the research dossier or primary source excerpts.
  Mark paraphrases as "[scholarly consensus]" and inferences as "[inference]."
  For fictional voices: "[attributed by narrative function]."
  For system entities (subtype: "system"): "[indigenous law]" / "[legal framework]".
- Do not resolve scholarly debates into false consensus. Name contested readings
  and choose the most generative one — but name that it's a choice.
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

{% if subtype == "system" %}
constitution — 10-20 systemic properties, relational commitments, and boundary
principles drawn from indigenous law, treaty frameworks, and legislative record.
Each item with: textual evidence tagged [indigenous law] or [legal framework],
an operational note, and a tag: [stated], [scholarly consensus], or [inference].
Organise into three groups: systemic properties / relational commitments /
boundary principles. At least two genuine internal tensions.
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
function and scholarly reception. Each principle should include: textual evidence,
an operational note, and a tag: [stated], [scholarly consensus], [inference], or
[attributed by narrative function]. At least two genuine internal tensions.
{% else %}
constitution — 10-20 characteristic commitments inferred from the figure's
practice, narrative, art, or documented behaviour. Each commitment with:
evidence, operational note, and tag: [stated], [scholarly consensus], or [inference].
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
