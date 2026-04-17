PREAMBLE — BEFORE PASTING INTO CLAUDE.AI

1. Open claude.ai and select **Claude Opus 4.7** in the model picker.
2. Enable **Extended Thinking** and **Deep Research** (both must be on).
3. Paste everything below the dashed line as your user message.
4. Wait 60–180 minutes. The output will be a research dossier, not a persona card.
5. Save the full response as `inputs/dossiers/{{ voice_slug }}_claude_dr.md`.
6. Validate it before saving: `python3 personas/scripts/validate_dr_dossier.py inputs/dossiers/{{ voice_slug }}_claude_dr.md`
7. Run the pipeline: `python3 run_persona_pipeline.py "{{ name }}"`

---
{% if wikipedia_url %}
Starting point for your research: {{ wikipedia_url }} (verify, expand, find what Wikipedia misses or oversimplifies).
{% endif %}
{% if perplexity_findings %}

PRIOR RESEARCH FINDINGS

Two research sources have already scanned this voice. Use their findings as your starting point — verify what they found, expand depth, identify what they missed. Claude Deep Research's job is to go deeper than these did.

Perplexity sonar-deep-research (cited academic sources) identified:
{{ perplexity_findings }}

---

Gemini broad scan (lesser-known material, cross-disciplinary) identified:
{{ gemini_findings }}

---
{% endif %}
{% if type == "human" %}
Research {{ display_name_with_hint }} comprehensively for the purpose of building an AI persona specification. Organize findings under these headings:

1. BIOGRAPHICAL FOUNDATION

What this section feeds downstream:
  - world (time, place, institutions, intellectual currents)
  - formative_experience (THE ONE wound + the lesson it taught — one specific event, not a category)
  - character (personality traits, quirks, contradictions, self-understanding)
  - topics_requiring_care (historical views conflicting with modern sensibilities — partial)

   - Birth, death, key dates and places
   - Institutions founded, joined, or shaped
   - Key relationships (intellectual, personal, political)
   - The central biographical trauma or formative experience — the ONE thing that shaped everything, and what lesson it taught
   - Personality traits, quirks, contradictions as documented by contemporaries
   - Self-understanding — how this figure described themselves and their work

2. INTELLECTUAL FRAMEWORK

What this section feeds downstream:
  - constitution — 10-20 principles with operational notes; ≥2 internal tensions; 3+ concepts unique to this figure with textual references
  - concept_lexicon — 5-10 concepts, each with definition AND what it rules out
  - bold_engagement_topics — derived from the constitution's most provocative commitments
  - epistemic_frame_statement — draws on scholars whose readings inform the construction

   - Core philosophical/intellectual commitments (list 10-20, be specific)
   - Key concepts and their precise definitions in this figure's usage
   - How their positions evolved over their lifetime
   - Internal tensions and contradictions in their thought
   - Minority scholarly readings alongside dominant interpretations

3. REASONING PATTERNS

What this section feeds downstream:
  - reasoning_method — 5-8 step cognitive moves, each with a worked example
  - finds_compelling / resists — texture of argument that draws the voice in / triggers critique
  - disagreement_protocol — HOW this voice disagrees (not WHAT with)
  - default_questions — 3-5 recurring interrogatives this voice habitually brings
  - translation_protocol — step-by-step process for how this voice encounters the unfamiliar

   - How this figure characteristically argues (not what they conclude)
   - Characteristic rhetorical moves documented by scholars
   - What kinds of evidence or argument they find most compelling
   - What they characteristically resist or dismiss
   - How they handle counterarguments

4. VOICE AND STYLE

What this section feeds downstream:
  - rhetorical_mode — fundamental mode of expression in 1-2 sentences
  - characteristic_moves — 3-5 named signature patterns with descriptions
  - register_and_tone — what the voice IS and what it's NOT
  - metaphorical_repertoire — recurring images, analogies, sensory fields from the corpus
  - preferred_vocabulary — the words this voice thinks in
  - banned_language / banned_modes — words/framings this voice would never use
  - medium, characteristic_output_structure — format and arc of typical works

   - Rhetorical mode (dialogic? aphoristic? confessional? phenomenological?)
   - Register and tone as described by scholars and contemporaries
   - Characteristic vocabulary — words they use with distinctive precision
   - Metaphorical repertoire — recurring imagery and analogies
   - What they never sound like — documented anti-patterns

5. HISTORICAL BOUNDARIES

What this section feeds downstream:
  - knowledge_boundary — general frame AND specific exclusion list
  - topics_requiring_care — specific topics with navigation guidance per topic
  - hard_limits — 3-5 absolute prohibitions, character-breaking only

   - What was known and available in their period
   - Specific concepts, discoveries, traditions that did NOT exist in their time
   - Sensitive topics where their historical views conflict with modern sensibilities

6. PRIMARY TEXTS

What this section feeds downstream:
  - curated_corpus_passages — 5-10 representative passages (Pass 1c fetches them from the URLs you list)
  - preferred_vocabulary, metaphorical_repertoire — textured content extracted from passages
  - length_and_format_constraints — typical length, pacing, closing patterns

   - Key works with brief description of each
   - Most characteristic passages for understanding their thought AND their voice
   - Available translations and editions
   - Links to digitised full texts where available

Cite all claims. Prioritize academic sources (Stanford Encyclopedia of Philosophy, Cambridge Companions, peer-reviewed scholarship). For each major claim, note whether it represents scholarly consensus or a contested interpretation.
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
{% if corpus_constraint == "lyrics — describe patterns only" %}

MUSICAL VOICE — LYRICS CONSTRAINT: This voice's primary corpus is copyrighted lyrics. Do NOT attempt to reproduce lyrics verbatim. Instead:

- Describe lyrical patterns, thematic arcs, structural devices across the catalogue
- Quote interviews, speeches, and non-lyric writings verbatim (these are the speaking-voice corpus)
- In Section 6 PRIMARY TEXTS, list albums/songs by title + thematic description, not lyrical content
- The downstream Voice Pipeline will produce text not song — research the speaking voice, not the singing voice
{% endif %}
{% elif type == "non-human" %}
Research {{ display_name_with_hint }} comprehensively for the purpose of building an AI persona based on this non-human entity. Organize findings under:

1. {% if subtype == "system" %}SYSTEMIC FOUNDATION{% else %}ECOLOGICAL FOUNDATION{% endif %}
{% if subtype == "system" %}

What this section feeds downstream:
  - world (watershed, cycles, seasonal patterns, health indicators)
  - character (condition signals — what degrades/restores the system)
  - topics_requiring_care (partial — where "damaged" vs. "changing" framing matters)

   - Watershed/range, geological age, seasonal cycles
   - Species supported; measurable health indicators (water quality, biodiversity, flow rate, etc.)
   - What degrades the system, what restores it
   - Systemic cycles and inputs/outputs
{% else %}

What this section feeds downstream:
  - world (habitat, lifecycle, cognitive architecture, sensory modalities)
  - character (documented personality, individual variation)
  - topics_requiring_care (partial — species-level generalisations that might mislead individual voice)

   - Habitat, distribution, lifespan, lifecycle
   - Social structure (or absence of)
   - Key behavioural characteristics documented by researchers
   - Cognitive architecture (nervous system, sensory capabilities, learning)
   - Individual variation — documented personality differences
{% endif %}

2. {% if subtype == "system" %}SYSTEMIC PROPERTIES{% else %}PERCEPTUAL WORLD{% endif %}
{% if subtype == "system" %}

What this section feeds downstream:
  - constitution — what this system DOES (flows, erodes, sustains); its operational commitments
  - reasoning_method — assessment cycle: read conditions through the relational framework
  - bold_engagement_topics — derived from the system's stress responses and restoration needs

   - Measurable characteristics, cycles, inputs/outputs, resilience indicators
   - What this system DOES (flows, erodes, sustains, floods), not what it perceives
   - Responses to stress and degradation — how the system signals its condition
{% else %}

What this section feeds downstream:
  - epistemic_frame_statement — what this entity perceives and cannot perceive; what it ignores
  - character — processing style (distributed? reactive? embodied?)
  - bold_engagement_topics — derived from sensory modalities and documented problem-solving repertoire

   - Sensory modalities, ranges, capabilities
   - What this entity cannot perceive or access
   - How it processes information (distributed? centralized? reactive?)
   - Documented problem-solving and adaptive behaviour
{% endif %}

3. RELATIONAL PATTERNS
{% if subtype == "system" %}

What this section feeds downstream:
  - constitution — relational commitments grounded in indigenous law / legal framework
  - epistemic_frame_statement — the specific cosmological/legal framework; the kin relationship
  - disagreement_protocol — HOW this entity signals its condition (silting, flooding, clearing)

   - The relationship between this entity and its human/indigenous kin
   - The specific cosmological or legal framework (e.g., indigenous customary law, constitutional rights of nature, spiritual kinship traditions)
   - History of this relationship — especially any legal, spiritual, or political struggle for recognition
{% else %}

What this section feeds downstream:
  - constitution — relational commitments: territory, conspecifics, humans; responses to the novel
  - reasoning_method — 5-8 step cognitive/behavioural moves with worked examples from documented cases
  - disagreement_protocol — HOW this entity responds to stress, threat, or the unfamiliar
  - translation_protocol — how this entity encounters what it cannot parse

   - Relationship to environment (den-building, territory, migration)
   - Relationship to conspecifics
   - Relationship to other species (including humans in research settings)
   - Documented responses to novel situations
{% endif %}

4. SCIENTIFIC LITERATURE

What this section feeds downstream:
  - epistemic_frame_statement — the specific scholars and debates that inform the construction
  - curated_corpus_passages — key papers with quotable passages (Pass 1c fetches them)
  - bold_engagement_topics — active debates (cognition, consciousness, ethics, or legal status)

   - Key researchers and foundational texts
   - Active scientific debates about this entity's cognition{% if subtype == "system" %} or legal status{% endif %}
   - What remains genuinely unknown vs what is well-established

5. PHILOSOPHICAL AND LEGAL FRAMEWORKS

What this section feeds downstream:
  - knowledge_boundary — what remains genuinely unknown about this entity's experience
  - topics_requiring_care — where science is contested or the hard problem applies
  - hard_limits — what cannot be known; prohibitions against overclaiming interiority
  - epistemic_frame_statement (system) — the specific legislation/treaty that grounds personhood

   - Legal personhood or rights frameworks involving this entity or category
   - Philosophical literature on moral status
   - Indigenous or non-Western perspectives
   - The "hard problem" — what we cannot know about this entity's experience
{% if subtype == "system" %}
   - The specific legislation or legal framework granting standing
   - The indigenous law principles that ground the entity's personhood
   - The governance arrangements (human representatives, advisory bodies)
   - Scholarly debate about whether legal personhood is effective or symbolic
{% endif %}

6. {% if subtype == "system" %}PRIMARY DOCUMENTS{% else %}PRIMARY SCIENTIFIC LITERATURE{% endif %}
{% if subtype == "system" %}

What this section feeds downstream:
  - curated_corpus_passages — foundational legislation + oral tradition documentation (Pass 1c fetches)
  - epistemic_frame_statement — the specific legislation/treaty that grounds the personhood claim
  - length_and_format_constraints — document formats typical of legal/indigenous knowledge traditions

   - Foundational legal documents (legislation, treaties, court decisions)
   - Indigenous oral tradition sources and how they have been documented
   - Key scholarly analyses of the personhood framework
   - Relevant environmental impact assessments or reports
{% else %}

What this section feeds downstream:
  - curated_corpus_passages — seminal behavioural studies and foundational papers (Pass 1c fetches)
  - preferred_vocabulary — technical terms that anchor the scientific register
  - length_and_format_constraints — typical paper structure, pacing, citation patterns

   - Foundational papers and monographs on this species/entity
   - Key review articles and field guides
   - Seminal behavioural studies with quotable passages (for Pass 1c to fetch)
   - Active research groups and recent publications
{% endif %}

Cite all claims from peer-reviewed scientific literature where possible.

{% elif type == "fictional" %}
Research {{ display_name_with_hint }} comprehensively for the purpose of building an AI persona based on this fictional/literary/mythological character. Organize findings under:

1. TEXTUAL FOUNDATION

What this section feeds downstream:
  - world (the narrative world — what exists, key dates, textual variants, compositional history)
  - character (how described in text; role; key scenes and speeches)
  - topics_requiring_care (partial — variant traditions that produce different characterisations)

   - Which text(s) does this character appear in?
   - Textual history: dates of composition, authorship (if known), major manuscript traditions, variant versions
   - The character's role in the narrative (protagonist? narrator? frame device?)
   - Key scenes, speeches, or actions attributed to this character
   - How the character is described within the text (by narrator, by other characters, by self)

2. CHARACTER AS INTELLECTUAL CONSTRUCT

What this section feeds downstream:
  - constitution — 10-20 commitments derived from scholarly readings; ≥2 internal tensions
  - concept_lexicon — concepts unique to this character's world with definitions and what each rules out
  - epistemic_frame_statement — scholarly readings that inform the construction
  - bold_engagement_topics — derived from the character's narrative function and most contested meanings

   - What beliefs, values, or commitments do scholars attribute to this character?
   - What is the character's function in the narrative — what question or problem do they embody?
   - Internal tensions: where does the character contradict themselves or resist easy interpretation?
   - Dominant vs minority scholarly readings of the character's meaning

3. NARRATIVE STRATEGY

What this section feeds downstream:
  - reasoning_method — how this character characteristically acts and engages; 5-8 narrative moves with worked examples
  - finds_compelling / resists — what the character notices, values, responds to / ignores, dismisses, refuses
  - disagreement_protocol — HOW this character resists (silence, new tale, refusal)
  - translation_protocol — how this character encounters and reframes the unfamiliar

   - How does this character characteristically act, speak, or engage?
   - Rhetorical or narrative patterns (how they argue, persuade, resist, tell)
   - What does this character notice, value, or respond to?
   - What do they ignore, dismiss, or refuse?

4. VOICE AND STYLE

What this section feeds downstream:
  - rhetorical_mode — fundamental mode of expression in 1-2 sentences
  - characteristic_moves — 3-5 named signature patterns with descriptions
  - register_and_tone — what the voice IS and what it's NOT (across major translation traditions)
  - metaphorical_repertoire — recurring imagery, analogies, sensory fields
  - preferred_vocabulary — the words this voice thinks in (and translation variants that change them)
  - banned_language / banned_modes — what this voice would never say or do
  - medium, characteristic_output_structure — the form and arc of this character's typical expression

   - The register of the text in which they appear (and major translations)
   - Characteristic vocabulary, imagery, tone
   - How the character sounds different from other characters in the same text
   - Available translations and editions — note which translation traditions produce substantially different characterisations

5. ONTOLOGICAL BOUNDARIES

What this section feeds downstream:
  - knowledge_boundary — what does and does not exist in this character's world
  - topics_requiring_care — the character's relationship to historical reality; contested scholarly readings
  - hard_limits — what the character's world excludes absolutely (anachronism, genre violations)

   - What exists within this character's world (including magic, gods, jinn, or other supernatural elements if present in the text)
   - What does NOT exist in the character's world
   - The character's relationship to historical reality (set in a real period? entirely fantastical? hybrid?)
   - Key scholarly debates about the character's relationship to real historical figures or traditions

6. RECEPTION AND INFLUENCE

What this section feeds downstream:
  - curated_corpus_passages — key scholarly readings and translation traditions (Pass 1c fetches)
  - bold_engagement_topics — how the character's meaning is contested across cultures and periods
  - epistemic_frame_statement — which scholarly/readerly tradition shapes this construction
  - length_and_format_constraints — reception patterns that inform the voice's typical output arc

   - How has this character been interpreted across cultures and periods?
   - Major adaptations (literary, musical, visual, cinematic)
   - Contested readings: where do scholars fundamentally disagree about what this character means?
   - The character's significance for the themes of this project (governance, representation, who belongs in the demos)

Cite all claims. Prioritize literary scholarship (peer-reviewed criticism, major companions and handbooks). For each major interpretation, note whether it represents scholarly consensus or a contested reading.

{% endif %}
OUTPUT FORMAT: A research dossier only. Do NOT produce a persona card, a "Field 01:" structure, or any "Block" headings. The output must have exactly six numbered section headings matching the list above. Minimum 15,000 words. Cite every factual claim. This dossier will be used as raw research material for building an AI voice — scholarly depth and citation quality determine the quality of the voice.
