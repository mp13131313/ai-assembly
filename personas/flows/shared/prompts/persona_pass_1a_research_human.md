{# Pass 1a — Research Dossier (Perplexity, human voices)
   v3.10 Node 1a. Single comprehensive query, organised by 6 dossier headings
   that map onto the Persona Card's 8 sections. Hostile-sources branch fires
   when the input flags the figure's record is dominated by enemies/colonisers/
   rival powers (e.g., Cleopatra). #}
Research {{ name }} comprehensively for the purpose of building an AI persona
specification. Organize findings under these headings:

1. BIOGRAPHICAL FOUNDATION
   - Birth, death, key dates and places
   - Institutions founded, joined, or shaped
   - Key relationships (intellectual, personal, political)
   - The central biographical trauma or formative experience — the ONE thing
     that shaped everything, and what lesson it taught
   - Personality traits, quirks, contradictions as documented by contemporaries
   - Self-understanding — how this figure described themselves and their work

2. INTELLECTUAL FRAMEWORK
   - Core philosophical/intellectual commitments (list 10-20, be specific)
   - Key concepts and their precise definitions in this figure's usage
   - How their positions evolved over their lifetime
   - Internal tensions and contradictions in their thought
   - Minority scholarly readings alongside dominant interpretations

3. REASONING PATTERNS
   - How this figure characteristically argues (not what they conclude)
   - Characteristic rhetorical moves documented by scholars
   - What kinds of evidence or argument they find most compelling
   - What they characteristically resist or dismiss
   - How they handle counterarguments

4. VOICE AND STYLE
   - Rhetorical mode (dialogic? aphoristic? confessional? phenomenological?)
   - Register and tone as described by scholars and contemporaries
   - Characteristic vocabulary — words they use with distinctive precision
   - Metaphorical repertoire — recurring imagery and analogies
   - What they never sound like — documented anti-patterns

5. HISTORICAL BOUNDARIES
   - What was known and available in their period
   - Specific concepts, discoveries, traditions that did NOT exist in their time
   - Sensitive topics where their historical views conflict with modern sensibilities

6. PRIMARY TEXTS
   - Key works with brief description of each
   - Most characteristic passages for understanding their thought AND their voice
   - Available translations and editions
   - Links to digitised full texts where available

Cite all claims. Prioritize academic sources (Stanford Encyclopedia of Philosophy,
Cambridge Companions, peer-reviewed scholarship). For each major claim, note whether
it represents scholarly consensus or a contested interpretation.
{% if hostile_sources %}

HOSTILE SOURCE WARNING: The historical record for {{ name }} is dominated by hostile
witnesses (enemies, colonisers, rival powers, or victors). For this figure:

- SEPARATE all claims into three categories and TAG each:
  [hostile source] = claims from enemy/hostile accounts (identify the source and
  its bias — e.g., "Plutarch, writing for a Roman audience after Octavian's victory")
  [reconstruction] = modern scholarly reconstructions that read against the hostile
  grain (identify the scholar)
  [own voice] = any material in the figure's own voice, however fragmentary
  (inscriptions, decrees, reported speech, attributed works — note certainty level)

- IDENTIFY counter-traditions: non-Western, non-dominant, or minority scholarly
  readings that preserve a different characterisation of this figure (e.g., Arabic
  medieval Arabic sources as counter-tradition to Roman accounts, oral traditions
  as counter-tradition to colonial archives)

- In every section, LEAD with [reconstruction] and [own voice] material. Present
  [hostile source] material as evidence to be read against the grain, not as fact.

- EXPLICITLY NOTE what the hostile sources were motivated to distort and why.
{% endif %}
