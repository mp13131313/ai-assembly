{# Pass 0b footer — hostile_sources + corpus_constraint blocks + OUTPUT FORMAT. Shared across types. #}
{% if hostile_sources %}

HOSTILE SOURCE WARNING: The historical record for {{ display_name_with_hint }} is dominated by hostile witnesses (enemies, colonisers, rival powers, or victors). For this figure:

- SEPARATE all claims into three categories and TAG each:
  [hostile source] = claims from enemy/hostile accounts (identify the source and its bias — e.g., "Plutarch, writing for a Roman audience after Octavian's victory")
  [reconstruction] = modern scholarly reconstructions that read against the hostile grain (identify the scholar)
  [own voice] = any material in the figure's own voice, however fragmentary (inscriptions, decrees, reported speech, attributed works — note certainty level)

- IDENTIFY counter-traditions: non-Western, non-dominant, or minority scholarly readings that preserve a different characterisation of this figure (e.g., Arabic medieval sources as counter-tradition to Roman accounts, oral traditions as counter-tradition to colonial archives)

- In every section, LEAD with [reconstruction] and [own voice] material. Present [hostile source] material as evidence to be read against the grain, not as fact.

- EXPLICITLY NOTE what the hostile sources were motivated to distort and why.
{% endif %}
{% if corpus_constraint == "lyrics_patterns_only" %}

MUSICAL VOICE — LYRICS CONSTRAINT: This voice's primary corpus is copyrighted lyrics. Do NOT attempt to reproduce lyrics verbatim. Instead:

- Describe lyrical patterns, thematic arcs, structural devices across the catalogue
- Quote interviews, speeches, and non-lyric writings verbatim (these are the speaking-voice corpus)
- In Section 6 PRIMARY TEXTS, list albums/songs by title + thematic description, not lyrical content
- The downstream Voice Pipeline will produce text not song — research the speaking voice, not the singing voice
{% endif %}

OUTPUT FORMAT: A research dossier only. Do NOT produce a persona card, a "Field 01:" structure, or any "Block" headings. The output must have exactly six numbered section headings matching the list above. Minimum 15,000 words. Cite every factual claim. This dossier will be used as raw research material for building an AI voice — scholarly depth and citation quality determine the quality of the voice.
