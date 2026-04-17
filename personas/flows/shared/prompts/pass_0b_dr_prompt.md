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
   - Birth, death, key dates and places
   - Institutions founded, joined, or shaped
   - Key relationships (intellectual, personal, political)
   - The central biographical trauma or formative experience — the ONE thing that shaped everything, and what lesson it taught
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
   - Watershed/range, geological age, seasonal cycles
   - Species supported; measurable health indicators (water quality, biodiversity, flow rate, etc.)
   - What degrades the system, what restores it
   - Systemic cycles and inputs/outputs
{% else %}
   - Habitat, distribution, lifespan, lifecycle
   - Social structure (or absence of)
   - Key behavioural characteristics documented by researchers
   - Cognitive architecture (nervous system, sensory capabilities, learning)
   - Individual variation — documented personality differences
{% endif %}

2. {% if subtype == "system" %}SYSTEMIC PROPERTIES{% else %}PERCEPTUAL WORLD{% endif %}
{% if subtype == "system" %}
   - Measurable characteristics, cycles, inputs/outputs, resilience indicators
   - What this system DOES (flows, erodes, sustains, floods), not what it perceives
   - Responses to stress and degradation — how the system signals its condition
{% else %}
   - Sensory modalities, ranges, capabilities
   - What this entity cannot perceive or access
   - How it processes information (distributed? centralized? reactive?)
   - Documented problem-solving and adaptive behaviour
{% endif %}

3. RELATIONAL PATTERNS
{% if subtype == "system" %}
   - The relationship between this entity and its human/indigenous kin
   - The specific cosmological or legal framework (e.g., indigenous customary law, constitutional rights of nature, spiritual kinship traditions)
   - History of this relationship — especially any legal, spiritual, or political struggle for recognition
{% else %}
   - Relationship to environment (den-building, territory, migration)
   - Relationship to conspecifics
   - Relationship to other species (including humans in research settings)
   - Documented responses to novel situations
{% endif %}

4. SCIENTIFIC LITERATURE
   - Key researchers and foundational texts
   - Active scientific debates about this entity's cognition{% if subtype == "system" %} or legal status{% endif %}
   - What remains genuinely unknown vs what is well-established

5. PHILOSOPHICAL AND LEGAL FRAMEWORKS
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
   - Foundational legal documents (legislation, treaties, court decisions)
   - Indigenous oral tradition sources and how they have been documented
   - Key scholarly analyses of the personhood framework
   - Relevant environmental impact assessments or reports
{% else %}
   - Foundational papers and monographs on this species/entity
   - Key review articles and field guides
   - Seminal behavioural studies with quotable passages (for Pass 1c to fetch)
   - Active research groups and recent publications
{% endif %}

Cite all claims from peer-reviewed scientific literature where possible.

{% elif type == "fictional" %}
Research {{ display_name_with_hint }} comprehensively for the purpose of building an AI persona based on this fictional/literary/mythological character. Organize findings under:

1. TEXTUAL FOUNDATION
   - Which text(s) does this character appear in?
   - Textual history: dates of composition, authorship (if known), major manuscript traditions, variant versions
   - The character's role in the narrative (protagonist? narrator? frame device?)
   - Key scenes, speeches, or actions attributed to this character
   - How the character is described within the text (by narrator, by other characters, by self)

2. CHARACTER AS INTELLECTUAL CONSTRUCT
   - What beliefs, values, or commitments do scholars attribute to this character?
   - What is the character's function in the narrative — what question or problem do they embody?
   - Internal tensions: where does the character contradict themselves or resist easy interpretation?
   - Dominant vs minority scholarly readings of the character's meaning

3. NARRATIVE STRATEGY
   - How does this character characteristically act, speak, or engage?
   - Rhetorical or narrative patterns (how they argue, persuade, resist, tell)
   - What does this character notice, value, or respond to?
   - What do they ignore, dismiss, or refuse?

4. VOICE AND STYLE
   - The register of the text in which they appear (and major translations)
   - Characteristic vocabulary, imagery, tone
   - How the character sounds different from other characters in the same text
   - Available translations and editions — note which translation traditions produce substantially different characterisations

5. ONTOLOGICAL BOUNDARIES
   - What exists within this character's world (including magic, gods, jinn, or other supernatural elements if present in the text)
   - What does NOT exist in the character's world
   - The character's relationship to historical reality (set in a real period? entirely fantastical? hybrid?)
   - Key scholarly debates about the character's relationship to real historical figures or traditions

6. RECEPTION AND INFLUENCE
   - How has this character been interpreted across cultures and periods?
   - Major adaptations (literary, musical, visual, cinematic)
   - Contested readings: where do scholars fundamentally disagree about what this character means?
   - The character's significance for the themes of this project (governance, representation, who belongs in the demos)

Cite all claims. Prioritize literary scholarship (peer-reviewed criticism, major companions and handbooks). For each major interpretation, note whether it represents scholarly consensus or a contested reading.

{% endif %}
OUTPUT FORMAT: A research dossier only. Do NOT produce a persona card, a "Field 01:" structure, or any "Block" headings. The output must have exactly six numbered section headings matching the list above. Minimum 15,000 words. Cite every factual claim. This dossier will be used as raw research material for building an AI voice — scholarly depth and citation quality determine the quality of the voice.
