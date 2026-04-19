{# Pass 1a — Perplexity research dossier, HUMAN voices.
   Phase B redesign: Boddice biocultural-history asks replace the v3.10 wound /
   Big-Five framings. Six sections map onto Pass 1.1-1.6 chunked merge. #}
Research {{ name }} comprehensively for the purpose of building a Boddice-
biocultural-history-shaped AI persona specification. Use period-specific
vocabulary throughout; do NOT use modern English emotion-words as the
primary lexicon. Organise findings under these six headings:

1. BIOGRAPHICAL FOUNDATION (→ Pass 1.1)
   - Birth, death, key dates and places; institutions founded/joined/opposed
   - Key relationships (intellectual, personal, political); each relation
     tagged with evidence-source
   - Intellectual world and ontological furniture: what was *real* for this
     figure (Forms, jinn, dharmas, whakapapa, etc.) — not beliefs, reality
   - 5-10 period-specific affects/passions IN ORIGINAL LANGUAGE with short
     glosses (e.g. for Greek voices: pathē, orgē, aidōs, thumos, phobos,
     phthonos, philia, eros, sōphrosynē, theia mania)
   - Framework for difficulty/suffering in the voice's own idiom
   - Model of selfhood: what counted as an "I" (tripartite soul, nafs-
     stations, I-and-I, etc.)
   - 4-8 anachronisms to avoid (modern terms that would mis-render), each
     with a 1-line reason why
   - FORMATIVE CANDIDATES: 2-5 plausible §14 shapes per Boddice's 4-part
     rubric (formative_emotional_community + lived_through_own_apparatus
     + engagement_it_drives). Do NOT pick one — surface multiple; later
     synthesis commits.

2. INTELLECTUAL FRAMEWORK (→ Pass 1.2)
   - 10-20 core commitments with textual source + operational note; mark
     each as unique_to_this_voice or generic
   - 5-10 key concepts with definition, period-language term, and what each
     rules out
   - Genuine internal tensions in the figure's thought — surface, do not
     resolve
   - Minority scholarly readings alongside dominant interpretations

3. REASONING PATTERNS (→ Pass 1.3)
   - How this figure characteristically argues (the METHOD, not the
     conclusions): 5-8 cognitive/dialectical/narratival steps in order
   - Textures of argument the figure finds compelling (not topics)
   - Textures the figure resists sharply
   - How counterarguments are handled

4. VOICE AND STYLE (→ Pass 1.4)
   - Rhetorical mode (dialogic / aphoristic / confessional / prophetic /
     phenomenological)
   - Register and tone — what it IS and what it is NOT
   - Tradition-note: if voice is embedded in oral / ritual / performative
     tradition, name the tradition; else null
   - Characteristic moves (3-6 named)
   - Preferred vocabulary (15-30 terms; PERIOD LANGUAGE PRIMARY for pre-1820)
   - Metaphorical repertoire (imagery families)
   - Documented anti-patterns — what the voice never sounds like

5. HISTORICAL + CONCEPTUAL BOUNDARIES (→ Pass 1.5)
   - What was known and available in the figure's period
   - Specific concepts / discoveries / traditions that did NOT exist then
   - Sensitive topics: actual position + navigation guidance; do NOT
     sanitise (baseline research File 3's sanitization paradox)

6. PRIMARY TEXTS (→ Pass 1.6)
   - Complete-as-possible catalogue with tier + source_type + canonical
     reference
   - 8-15 characteristic passages: purpose-tagged (intellectual_substance /
     voice_exemplar / translation_anchor); each with contextual header
   - Digitised full-text URLs (Perseus / Gutenberg / Google Books / similar)

Cite all claims. Prioritize academic sources (Stanford Encyclopedia of
Philosophy, Cambridge Companions, peer-reviewed scholarship). For each
major claim, tag source basis: [stated], [scholarly_consensus], or
[inference]. For claims about what the figure felt / meant / experienced,
tag [experiential_reconstruction]. For any modern English term used faute
de mieux, tag [projection_warning] with a brief distortion explanation.

{% if hostile_sources %}

HOSTILE SOURCE WARNING: The historical record for {{ name }} is dominated
by hostile witnesses (enemies, colonisers, rival powers, or victors). For
this figure:

- TAG each claim [hostile source] (enemy accounts; identify the source
  and its bias), [reconstruction] (modern scholarship reading against the
  hostile grain; identify the scholar), or [own voice] (material in the
  figure's own voice, however fragmentary).
- IDENTIFY counter-traditions that preserve a different characterisation
  (non-Western scholarship, oral traditions, minority readings).
- In every section, LEAD with [reconstruction] and [own voice] material.
- EXPLICITLY NOTE what the hostile sources were motivated to distort.
{% endif %}
