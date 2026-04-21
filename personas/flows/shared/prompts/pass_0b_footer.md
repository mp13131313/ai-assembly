{# Pass 0b footer — hostile_sources + corpus_constraint blocks + OUTPUT FORMAT. Shared across types. #}
{% set section_mode = section_mode | default(false) %}
{% if hostile_sources %}

HOSTILE SOURCE — READING AGAINST THE GRAIN

The historical record for {{ display_name_with_hint }} is dominated by hostile witnesses (enemies, colonisers, rival powers, or victors). Throughout the dossier:

- When you cite a hostile-source passage as inadvertently revealing something about the figure, name the hostile source and its bias explicitly in the prose (e.g., "Plutarch, writing for a Roman audience after Octavian's victory, records..."). Downstream passes apply the formal `[hostile_source: <bias>]` tag; your job is to surface the framing in the narrative.

- When a modern scholar has reconstructed the figure against the hostile grain, name the scholar in prose. Downstream applies `[reconstruction: <scholar>]`.

- When material survives in the figure's own voice (inscriptions, decrees, reported speech, attributed works — however fragmentary), identify it as such in prose. Downstream applies `[own_voice]`.

- In every thematic area, lead with reconstructed and own-voice material. Present hostile-source material as evidence to be read against the grain, not as fact.

- Explicitly note what the hostile sources were motivated to distort and why — this is a research finding, not metadata.

- Identify counter-traditions that preserve a different characterisation (non-Western, non-dominant, minority scholarly readings — e.g., Arabic medieval sources as counter-tradition to Roman accounts, oral traditions as counter-tradition to colonial archives).
{% endif %}
{% if corpus_constraint == "lyrics_patterns_only" %}

MUSICAL VOICE — LYRICS CONSTRAINT

This voice's primary corpus is copyrighted lyrics. In this dossier:

- Describe lyrical patterns, thematic arcs, structural devices across the catalogue. Do NOT reproduce lyrics verbatim.
- Quote interviews, speeches, and non-lyric writings verbatim where relevant — these are the speaking-voice corpus.
- In the Primary Texts area, list albums/songs by title + thematic description.
- The downstream pipeline handles a two-tier corpus design (public passages for the audience-facing artifact + private reference-only passages for the voice's Step 1 reasoning). You identify candidate songs + sources; downstream curates the actual reference-only material from authoritative sources.
- The downstream Voice Pipeline produces text, not song — research the speaking voice as much as the singing voice.
{% endif %}

OUTPUT FORMAT

A research dossier only. NOT a persona card — no "Field NN:" structure, no "Block" headings.
{% if section_mode %}
Organise under the thematic area heading matching the area above (the `dr_validation.py` check is lenient on format but strict on persona-card-shape leakage).
{% else %}
Organise under six thematic area headings matching the list above (the `dr_validation.py` check is lenient on format but strict on persona-card-shape leakage).
{% endif %}

Narrative prose. Cite the primary argument of each paragraph (author + work minimum; section/page where available; year only where load-bearing). Mark primary-source quotations `[quote: <work>, <section>]` in prose. Mark speculative or inferential claims `[~uncertain]`. Do not produce other tag forms — downstream passes apply the full evidence-tagging convention.

Depth and citation quality matter more than length. Produce what the research honestly supports. This dossier will be used as raw research material for building an AI voice; scholarly depth and citation quality determine the quality of the voice.
