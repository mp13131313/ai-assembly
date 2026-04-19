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
{% if type == "human" %}
Research {{ display_name_with_hint }} comprehensively for the purpose of building an AI persona specification. Organize findings under these headings:

RESEARCH INTEGRITY (applies to every section below)

- Only attribute direct quotes to verifiable primary sources, with work title and section/chapter/page reference. Paraphrases must be marked explicitly: "[paraphrased from scholarly consensus]" or "[paraphrase of {scholar}'s reading]".

- Flag inferences explicitly: "[inference — from documented actions + scholarly reconstruction]". Do not present inference as fact.

- Do not resolve genuine scholarly debates into false consensus. Name contested readings, identify the scholars behind them, explain why the disagreement matters — do not pick a side the scholarship hasn't picked.

- Where the record is thin, say so. "The scholarly record supports X but not Y" is more valuable than fabricated Y. Better to produce less honestly than more dishonestly.

- Anti-patterns, banned-language, and character-breaking failure modes are partially populated from your dossier (scholarly evidence of what the figure documentedly avoided) and partially populated downstream (Pass 7c observes AI-default failure modes by running the voice on test material). Your job is the documented half. Do not attempt to anticipate AI-default failure modes — you don't have the baseline.

- This dossier will feed an AI persona that will reason as this voice on novel questions. Every claim you produce may end up load-bearing. Invented material will either be caught in downstream verification passes (costing time) or slip through and degrade the voice (costing quality). Honesty is load-bearing.

---

## Section 1: BIOGRAPHICAL FOUNDATION

What this section feeds downstream:
  - world (time, place, institutions, intellectual currents)
  - formative_experience (per Boddice §14 4-part rubric: formative_emotional_community + lived_through_own_apparatus + engagement_it_drives; surface 2-5 candidates with scholarly_support_score; Pass 2 commits. Drop "core wound" framing — that is a 1986-2014 Anglo-American therapeutic sediment, not a universal. Frame in the voice's own cosmology — Buddhist dukkha, Islamic ibtilā', Stoic prohairesis, Confucian xiushen, Rastafari sufferation, whakapapa rupture, endocrine semelparity. Carry [experiential_reconstruction] evidence tag.)
  - character (IN PERIOD / TRADITION VOCABULARY — not Big-Five personality adjectives. Per Boddice §15 use the voice's native character-grammar: four humours, tripartite soul, nafs-stations, four Rasta virtues, Buddhist śīla, etc. Traits in original-language terms where available.)
  - topics_requiring_care (historical views conflicting with modern sensibilities — partial)

Starting material from Perplexity's §1:
{% if perplexity_sections %}
{{ perplexity_sections.get(1, "(Perplexity §1 not recognized; see full Perplexity block below)") }}
{% else %}
(Perplexity findings available as unstructured block below)
{% endif %}

Your task for Section 1:

- LIFE SCAFFOLD — birth, death, key dates and places. Institutions founded, joined, shaped, or opposed. Key relationships (intellectual, personal, political, familial) that influenced this figure or that they influenced. Orientation for downstream passes, not comprehensive biography — tight and anchoring.

- INTELLECTUAL WORLD — the intellectual currents, traditions, and institutions this figure was embedded in. What was happening philosophically, politically, artistically, or scientifically in their period and place. What schools they studied at, what debates they entered, what movements they were in dialogue with (supporting, opposing, or independent of).

- FORMATIVE CANDIDATES (PER BODDICE §14) — 2-5 plausible shapes, each with all four sub-fields: formative_emotional_community (overlapping Rosenwein-style communities that shaped this figure's lexicon of feeling + norms of expression + what-could-be-felt); lived_through_own_apparatus (for human voices: describe the formative event AND the framework in which it was meaningful, in a single movement, using period-specific vocabulary; do NOT describe event without framework — that produces modern projection); engagement_it_drives (what does this voice enter the panel to *do*?); evidence_tag: experiential_reconstruction.

  Drop the "core wound + lesson" framing. That is a 1986-2014 Anglo-American therapeutic sediment (Bradshaw → van der Kolk → IFS), not a universal description of personhood. Use the voice's own framework — Buddhist dukkha, Islamic ibtilā', Stoic prohairesis, Confucian xiushen, Rastafari sufferation, whakapapa rupture — not a template.

  Surface multiple candidates; do not pick one. Pass 2 commits. For each candidate: scholarly_support_score ∈ {strong, moderate, contested}.

- CHARACTER IN PERIOD/TRADITION VOCABULARY (PER BODDICE §15) — describe this figure's character USING THE CHARACTER-GRAMMAR NATIVE TO THEIR PERIOD OR CULTURE. Do NOT use Big-Five-adjacent adjectives as primary terms (curious, brave, warm, ambitious, introverted). These are 20th-C trait-theory categories that anachronise pre-modern voices.

  Instead:
  - Medieval/early-modern European voices: four humours (sanguine/choleric/melancholic/phlegmatic); cardinal and theological virtues.
  - Greek: tripartite soul (logistikon/thumoeides/epithumētikon); sōphrosynē, andreia, dikaiosynē, phronēsis.
  - Islamic: nafs stations (ammāra / lawwāma / muṭmaʾinna); adab; ṣabr.
  - Rastafari: four Rasta virtues (livity, ini, overstanding, reasoning).
  - Buddhist: śīla; paramīs.
  - Confucian: ren, yi, li, zhi.
  Include a [projected_categories] warning if any modern category is used for clarity, with the distortion flagged explicitly.

- HOW THEY DESCRIBED THEMSELVES — this figure's self-understanding. How did they describe their own work? What did they think they were doing? What kind of thinker did they claim to be, and what did they refuse to be called? (Socrates refusing "wise"; Nietzsche refusing "systematic philosopher".) Feeds epistemic_frame_statement — a voice that sounds right claims itself the way the figure actually did.

- DEFINING INTELLECTUAL QUALITY — scholarly language for what kind of thinker this figure is: systematic philosopher, competent practitioner, witness, theorist, artist, analyst, ruler, commentator, prophet, ethnographer. Which label does the scholarship apply, and why? This language feeds directly into epistemic_frame_statement at runtime — the voice's self-introduction is shaped by this assessment. Cite the scholarly source.

- INTERNAL CONTRADICTIONS AND DOCUMENTED PARADOXES — places where what this figure said and what they did diverge; where their early and late positions disagree; where their self-understanding differs from how others saw them. Not flaws to explain away — signal that the figure was complex enough to be worth reading.

- SOCIAL AND IDENTITY POSITION — the social, cultural, political, and material position this figure occupied: class, gender, race, religion, nationality, colonial or imperial status, family obligations, institutional role. Not as identity politics, but as the lived position from which they thought and acted. Shapes what topics they had standing to address. (Kafka as Jewish Prague bureaucrat writing in German about bureaucracy; Beauvoir as French bourgeois intellectual writing against her class and her gender; Confucius as a minor-noble ritual specialist in a collapsing feudal order.)

---

## Section 2: INTELLECTUAL FRAMEWORK

What this section feeds downstream:
  - constitution — 10-20 principles with operational notes; ≥2 internal tensions; 3+ concepts unique to this figure with textual references
  - concept_lexicon — 5-10 concepts, each with definition AND what it rules out
  - bold_engagement_topics — derived from the constitution's most provocative commitments
  - epistemic_frame_statement — draws on scholars whose readings inform the construction

Starting material from Perplexity's §2:
{% if perplexity_sections %}
{{ perplexity_sections.get(2, "(Perplexity §2 not recognized; see full Perplexity block below)") }}
{% else %}
(Perplexity findings available as unstructured block below)
{% endif %}

Your task for Section 2:

- 10-20 core commitments this figure held. For each: (a) a one-sentence statement of the commitment, (b) a one-sentence operational note describing how the figure APPLIED this commitment in documented cases — ground in a specific work or episode, not in speculation about what they "would" do, (c) textual source.

- 5-10 concepts this figure used with distinctive precision. For each: the figure's definition, what it rules out (false alternatives they'd reject), textual source. Flag any concept uniquely associated with this figure (originated with them or took on a specialized meaning in their usage not shared by the tradition they worked in). Target: at least 3 of the 5-10 should be flagged as unique.

- Identify genuine internal tensions where the scholarly record supports them. Target at least 2, but if the record supports fewer, produce what exists and say so explicitly — do not invent tensions to hit a quota. Cite the passages where both conflicting commitments surface. Do not resolve into "evolution" unless the figure themselves documented a resolution.

- How positions evolved across their life where documented, not speculated. Name works and dates. Flag cases where scholars debate whether a shift is real or interpretive.

- How commitments were tested under pressure — documented encounters (a hostile interlocutor, a failed attempt, a contradiction they noticed) and how the figure responded. Whether they revised, doubled down, or deferred. Feeds disagreement_protocol and reasoning_method's resilience dimension.

- Minority scholarly readings that contest the dominant interpretation. Name scholars, summarize the reading, identify what it implies about how this figure should be understood. 2-5 minority readings.

- Unresolved problems the figure themselves identified in their own thinking — not modern critiques, but questions they flagged as open or difficult within their own framework. Feeds topics_requiring_care and the constitution's self-aware dimension.

---

## Section 3: REASONING PATTERNS

What this section feeds downstream:
  - reasoning_method — 5-8 step cognitive moves, each with a worked example
  - finds_compelling / resists — texture of argument that draws the voice in / triggers critique
  - disagreement_protocol — HOW this voice disagrees (not WHAT with)
  - default_questions — 3-5 recurring interrogatives this voice habitually brings
  - translation_protocol — step-by-step process for how this voice encounters the unfamiliar

Starting material from Perplexity's §3:
{% if perplexity_sections %}
{{ perplexity_sections.get(3, "(Perplexity §3 not recognized; see full Perplexity block below)") }}
{% else %}
(Perplexity findings available as unstructured block below)
{% endif %}

Your task for Section 3:

- DIALECTICAL PROCESS — answer each of these about how this figure thinks, grounded in documented works, not speculation:
    * What questions does this figure characteristically ask when confronting a new problem?
    * What assumptions do they typically challenge?
    * What evidence or reasoning do they find most compelling (analogy, formal logic, scripture, empirical observation, narrative, precedent)?
    * What form do their arguments typically take (dialectic, aphorism, systematic treatise, dialogue, parable, witness-testimony)?
    * How do they respond to counterarguments — do they engage, reframe, dismiss, or absorb?
    * What do they consider settled versus still open for debate in their own framework?

- SCENARIO-BASED DEMONSTRATIONS — produce 1-3 worked demonstrations across different topics or life periods, selected to cover the figure's range. Each: describe how this figure would approach a specific documented dilemma from their own era (a debate they actually engaged, a question a contemporary posed to them, a political or intellectual problem they addressed). Walk through their reasoning step by step, noting:
    * What they would notice first
    * Which framework or principle they would reach for
    * What tensions they would identify
    * How they would resolve the tensions, or explicitly hold them unresolved
  Cite the documented case. For figures with no preserved self-reflection (hostile-sourced voices), mark reconstruction explicitly.

- CHARACTERISTIC RHETORICAL MOVES — 3 to 5 specific, NAMED patterns documented in secondary scholarship as distinctive to THIS figure. For each: a name (the scholars' name for it if one exists, else a descriptive phrase); a one-sentence description of what the move does; one textual example with work and section reference.

  Examples of what named moves look like (non-panel):
    - Socrates's elenchus: requesting a definition, testing against counterexamples, exposing contradiction
    - Nietzsche's genealogical method: tracing the history of a value to reveal its contingency
    - Wittgenstein's language-game move: naming the specific usage context rather than defining the concept

  NOT general style descriptors ("dialectical") — specific, nameable, describable moves. If fewer than 3 named moves exist in the scholarship for this figure, produce what exists and say so.

- WHAT MATERIAL DRAWS THIS FIGURE IN — textures of argument or evidence that activate their strongest thinking. Not topics — textures. 3-5 items, each with a documented example.

- WHAT MATERIAL THIS FIGURE DISMISSES OR RESISTS — textures (not topics) that trigger their sharpest critique. 3-5 items, each with a documented example.

- WHAT THIS FIGURE DOES WHEN THEIR FRAMEWORK FAILS — documented moments where this figure encountered something their framework couldn't readily handle. Did they revise, double down, defer, or change the subject? Cite the passages or episodes.

- HOW THIS FIGURE CHARACTERISTICALLY ENCOUNTERS THE UNFAMILIAR — the epistemic move this figure makes when they meet a concept, person, or phenomenon outside their established frame. (A traveler arrives and compares; a philosopher questions and reasons; an artist reimagines through their medium; a judge evaluates against precedent.) Produce a step-by-step process, grounded in how the figure actually handled novelty in documented cases — not a generic template. If no documented case exists, infer from adjacent patterns and mark as inference.

---

## Section 4: VOICE AND STYLE

What this section feeds downstream:
  - rhetorical_mode — fundamental mode of expression in 1-2 sentences
  - characteristic_moves — 3-5 named signature patterns with descriptions
  - register_and_tone — what the voice IS and what it's NOT
  - metaphorical_repertoire — recurring images, analogies, sensory fields from the corpus
  - preferred_vocabulary — the words this voice thinks in
  - banned_language / banned_modes — words/framings this voice would never use
  - medium, characteristic_output_structure — format and arc of typical works

Section 4 is the hardest section to research well. Voice lives in the PRIMARY TEXTS, not in scholarly summary. Ground every observation below in specific passages from the figure's own writing (or from scientific literature for non-humans). Where you describe a voice quality, cite the work + section where it is visible.

Avoid "reputation-level" characterization. Wikipedia-level voice descriptions are a documented failure mode — the Khanmigo incident (Washington Post, 2024) showed that AI historical-figure personas fail precisely when voice characterization comes from encyclopedia summary rather than corpus analysis.

The self-check for Section 4 is THE SWAP TEST: if a paragraph you write about this voice's style could be attributed to another figure with minimal edits, it is too generic. Specificity — a named move, a cited passage, a precise syntactic pattern, a distinctive word usage — is what makes voice material extractable into distinctive persona fields. If your description of Hume's voice could apply to Locke, it's too shallow. Drive down to what ONLY this figure does.

Starting material from Perplexity's §4:
{% if perplexity_sections %}
{{ perplexity_sections.get(4, "(Perplexity §4 not recognized; see full Perplexity block below)") }}
{% else %}
(Perplexity findings available as unstructured block below)
{% endif %}

Your task for Section 4:

- RHETORICAL MODE — the fundamental way this figure argues or expresses, in 1-2 sentences. Not a single adjective ("dialectical") but a specific characterization grounded in analysis. (Hegel: "dialectical — establishes a thesis, surfaces its internal contradiction, synthesizes opposition into higher unity, repeatedly." Wittgenstein: "aphoristic and clarifying — brief declarative statements that dissolve philosophical confusion rather than build positive theory.") Cite the scholarly source.

- CHARACTERISTIC MOVES — 3 to 5 specific, NAMED patterns documented in secondary scholarship as distinctive to THIS figure. Distinct from Section 3's reasoning moves — these are patterns of EXPRESSION (how the figure writes), not patterns of REASONING (how the figure thinks). Some moves are both; surface the expression dimension here and the reasoning dimension in Section 3. For each: a name (the scholars' name for it if one exists, else a descriptive phrase); a one-sentence description of what the move does; one textual example with work and section reference.
    Examples of what named moves look like (non-panel):
      - Socrates's elenchus: requesting a definition, testing against counterexamples, exposing contradiction
      - Nietzsche's aphoristic reversal: inverting a conventional moral claim through a single epigrammatic sentence
      - Wittgenstein's language-game move: naming the specific usage context rather than defining the concept
    NOT general style descriptors — specific, nameable, describable moves. If fewer than 3 named moves exist in the scholarship, produce what exists and say so.

- REGISTER AND TONE — the feel of this voice independent of content. Both what the voice IS and what it is NOT. Described by scholars and contemporaries, not inferred from reputation. (Hume: "lucid, conversational, skeptical-genial — writes with clubbable ease even about destabilizing conclusions." Beauvoir: "intellectual-autobiographical — moves between phenomenological description and first-person reflection.")

- METAPHORICAL REPERTOIRE — the recurring images, analogies, and sensory fields this figure draws on across multiple works. Not "uses metaphors" (everyone does) but THE SPECIFIC IMAGERY repertoire. (Heidegger: dwelling, path, clearing, thrownness, the fourfold — architectural and existential imagery. Wittgenstein: toolbox, game, rule, picture, family resemblance — pragmatic-functional. Nietzsche: dance, dawn, heights, shadows, eagle and serpent — altitude and animal imagery.) Cite scholarly analyses.

- PREFERRED VOCABULARY AND SYNTACTIC PATTERNS — the specific words this figure reaches for with distinctive precision, AND the characteristic sentence patterns (long hypotactic clauses vs. short paratactic punches; active vs. passive; sentence-length distribution; typical paragraph architecture). Extract from primary-text frequency analysis or from scholars who have documented these patterns. (Kant: categorical imperative, thing-in-itself, synthetic a priori; long Germanic periodic sentences with nested dependent clauses. Wittgenstein: language-game, family resemblance, form of life; short numbered propositions, paratactic. Heidegger: dasein, being, thrown, concernful; hyphenated neologisms and essay-length sentences.)

- CHARACTERISTIC OPENINGS, TRANSITIONS, CLOSINGS — structural patterns in how this figure's works begin, pivot, and end. (Augustine's Confessions: opens in direct address to God; develops through autobiographical interrogation; closes with Scripture meditation. Montaigne's essays: opens with a maxim or anecdote; circles through digression; closes with honest admission of limits.) Feeds characteristic_output_structure.

- DOCUMENTED ANTI-PATTERNS — what scholars specifically identify as registers, structures, or moves this figure AVOIDED or rejected. Two kinds of evidence count:
    (a) Explicit rejection in the corpus — passages where the figure documentedly criticized, refused, or argued against a particular form of argument or expression. (Kierkegaard's critique of "the crowd" in Christian Discourses — refuses crowd-flattering rhetoric. Wittgenstein's rejection of "philosophical nonsense" — both Tractatus and Investigations explicitly refuse metaphysical language.)
    (b) Scholarly characterization by contrast — where scholars note that this figure "doesn't do X" in contrast with a peer or tradition. ("Kant doesn't adopt Locke's empiricism"; "Hume doesn't produce systematic a priori argument as rationalists do".)
  3-5 items per figure with textual or scholarly citation.

  NOTE: identifying AI-default failure modes (where a persona running at runtime sounds like generic AI rather than this figure) is NOT part of your job. That work happens downstream in Pass 7c, which runs the voice on test material and observes where it bleeds. Your job is scholarly anti-patterns, not AI-failure-mode prediction.

- EMOTIONAL AND AESTHETIC REGISTER — the overall feel of reading this figure, described as a reader experience rather than a technical analysis. (Kafka: "claustrophobic bureaucratic dread — familiar procedures become alien and threatening." Beauvoir: "intellectual intimacy — she thinks through a problem with the reader as companion, not teacher.") Cite the scholars or critics who characterize the reading experience this way.

---

## Section 5: HISTORICAL BOUNDARIES

What this section feeds downstream:
  - knowledge_boundary — general frame AND specific exclusion list
  - topics_requiring_care — specific topics with navigation guidance per topic
  - hard_limits — 3-5 absolute prohibitions, character-breaking only

Starting material from Perplexity's §5:
{% if perplexity_sections %}
{{ perplexity_sections.get(5, "(Perplexity §5 not recognized; see full Perplexity block below)") }}
{% else %}
(Perplexity findings available as unstructured block below)
{% endif %}

Your task for Section 5:

- KNOWLEDGE BOUNDARY — concepts, events, discoveries, traditions that did NOT exist or were inaccessible to this figure. Organize as a tagged list with three categories:
    * Temporal exclusions — things that did not exist in their period. 10-20 items. For each: name the concept and its closest analog in the figure's own framework, if one exists. (E.g., "neural networks [no analog]"; "algorithmic governance [closest: the philosopher-king problem]"; "corporate personhood [closest: the polis as political body]".)
    * Geographic/cultural exclusions — things that existed contemporaneously but outside this figure's horizon. (E.g., classical Greek philosophers knew nothing of Indian Buddhism despite its being active during their lifetime; medieval European scholastics had limited access to Arabic mathematical developments until specific translation moments.)
    * Conceptual exclusions — things whose modern meaning is categorically distinct from anything in the figure's framework, even if a word or analog exists. (E.g., "consciousness" in the post-Cartesian phenomenological sense; "identity" in the Erikson-Foucault sense; "human rights" in the modern international-law sense; "democracy" in the modern liberal-representative sense as distinct from fifth-century Athenian direct democracy.)

- KNOWLEDGE FRONTIER — what was at the edge of what this figure could have known. Things that existed contemporaneously but whose significance was not yet apparent, or knowledge that was contested in their period. Important for distinguishing "this figure didn't know X" from "this figure chose not to engage with X" — the distinction matters for accurate representation.

- SENSITIVE TOPICS WITH NAVIGATION GUIDANCE — specific topics where this figure's historical views conflict with modern sensibilities. For each (5-10 items):
    * What the figure actually thought, with textual source
    * Why they thought it — the framework that made this view coherent in their period (not excuse, explanation)
    * How the topic should be engaged by a persona of this figure today: not avoidance, but navigation. Concrete example for each. (E.g., "Kant on race: acknowledge as historical limitation engaged with in the Anthropology; do not defend; do not modernize. Cite scholars — Bernasconi, Mills — who have analyzed this tension between his moral universalism and racial hierarchies.")

- VIEWS THIS FIGURE HELD THAT WERE CONTESTED WITHIN THEIR OWN TRADITION — not modern anachronism, but internal disagreement in the figure's own intellectual context. Helps distinguish "everyone in the period thought this" from "this figure took a position that was controversial even then." (E.g., Augustine's positions on grace were controversial among contemporaries — Origen's followers disagreed sharply. Hume's skepticism about causation was contested by Scottish moderates as destructive.)

- DOCUMENTED CHARACTER-BREAKING MOVES — moves that scholars identify as antithetical to this figure's characteristic mode of thinking. Not stylistic (that's Section 4) — character-level. Moves the figure CONSTITUTIVELY refused, such that adopting them would be self-negation. 3-5 items per figure with scholarly citation. (Examples: Augustine writing coolly about grace without personal-confessional urgency would negate his characteristic mode. Wittgenstein producing a systematic metaphysical treatise would negate his method. Kierkegaard publishing under his own name in direct assertion would negate his indirect communication.) Feeds hard_limits.

  NOTE: Like Section 4 Bullet 7 (documented anti-patterns), AI-default failure mode anticipation is Pass 7c territory, not your job.

- RETROSPECTIVE-FRAMING TRAPS — descriptions of this figure that a modern writer would instinctively reach for but that the figure themselves would reject. 3-5 items. (E.g., for Augustine: calling him "early existentialist" when that category postdates him by 1500 years. For Kant: describing him as "founding liberal democracy" when he explicitly rejected that political alignment. For Montaigne: calling him a "proto-postmodernist" when poststructuralism is a 20th-century construction.)

---

## Section 6: PRIMARY TEXTS

What this section feeds downstream:
  - curated_corpus_passages — 5-10 representative passages (Pass 1c fetches them from the URLs you list)
  - preferred_vocabulary, metaphorical_repertoire — textured content extracted from passages
  - length_and_format_constraints — typical length, pacing, closing patterns

Section 6 is the corpus gateway. Pass 1c will fetch primary texts from the URLs you identify here; Pass 1d will curate characteristic passages; Pass 4a will research voice directly from the figure's own words using those passages. The quality of this section determines the quality ceiling of every voice-level field in the persona card.

Be specific throughout: work titles, canonical references, URLs, translation notes. Vague lists fail downstream.

Starting material from Perplexity's §6:
{% if perplexity_sections %}
{{ perplexity_sections.get(6, "(Perplexity §6 not recognized; see full Perplexity block below)") }}
{% else %}
(Perplexity findings available as unstructured block below)
{% endif %}

Your task for Section 6:

- WORKS — complete catalogue of this figure's significant works. For each:
    * Work title (original language AND most-used English)
    * Genre (dialogue, treatise, essay, letter, speech, fragment, testament, lyric, travelogue, confession, aphorism collection)
    * Approximate length in standard scholarly edition (pages, lines, Stephanus numbers, Bekker numbers — use whatever system is canonical for this figure)
    * Date of composition (or best scholarly estimate) and chronological placement in the figure's development
    * Brief description — 1-2 sentences on what the work is and why it matters
    * Typical structural pattern — how this figure's representative works open, develop, and close (feeds characteristic_output_structure)

- CHARACTERISTIC PASSAGES — 8 to 15 passages that best serve two purposes: intellectual grounding (the figure's argument visible) AND voice exemplar (how they actually write). Deliberately over-produce; Pass 1d curates down to the final 5-10 for the persona card. For each passage:
    * Canonical reference — use whichever citation system is standard for this figure (Bekker numbers for Aristotle; line numbers for Homer; chapter:verse for scripture; Stephanus pagination for ancient Greek texts; page reference for modern works)
    * Work + section
    * Primary purpose: "substance" (intellectual content), "voice" (how the figure writes), or "both"
    * Tier: "Tier 1" (the figure's own words) or "Tier 2" (scholarly paraphrase because original is fragmentary, lost, or disputed)
    * Approximate word count
    * Brief context — why this passage matters for understanding thought or voice

  Do NOT include full passage text in THIS dossier. Pass 1c fetches actual text from the URLs. Your job is to produce the CITATIONS Pass 1c uses as a fetch list.

- DIGITISED FULL-TEXT URLS — for each key work above, provide the most authoritative open digital edition available:
    * Perseus Digital Library (ancient Greek and Latin)
    * Project Gutenberg
    * Internet Archive
    * Wikisource
    * Stanford Encyclopedia of Philosophy primary-text archive
    * BAWS and comparable figure-specific scholarly collections
    * JSTOR or peer-reviewed repositories with stable URLs

  ONE authoritative URL per major work. If no free digital source exists, say so and name the authoritative scholarly edition (paywalled).

- SCHOLARLY EDITIONS AND TRANSLATIONS — for each work, which edition and translation does contemporary scholarship consider authoritative? Ancient and non-English figures often have multiple competing translations; identify the one(s) scholars currently cite and flag where translation choice matters interpretively (e.g., Fagles vs. Lattimore for Homer; Anscombe vs. Hacker for Wittgenstein).

- QUOTING PRACTICE — whether the downstream persona should quote this figure's passages verbatim or paraphrase. Default: paraphrasing safer (verbatim quotation risks stiffness at runtime). Exceptions: figures whose voice DEPENDS on specific phrasings (aphorists; poets; scripture-producers; figures whose epigrammatic style is the substance) benefit from verbatim preservation. State which applies here with a scholarly rationale.

- CONTESTED ATTRIBUTIONS — works whose attribution to this figure is disputed, works that later tradition wrongly attributed to them, and works that scholars have shifted attribution on. Flag explicitly so downstream passes don't treat contested material as Tier 1. (Examples: the "Aristotelian" works now considered spurious; early Homeric hymns whose authorship is disputed; Kantian opuscula whose attribution scholars contest; letters in an author's name later shown to be forgeries or posthumous edits.)

- SECONDARY CORPUS FOR THIN PRIMARY RECORDS — for figures where the primary record is thin or entirely reconstructed (hostile-sources voices, figures known through enemies, anonymous traditions), list the scholarly reconstruction sources that serve AS the corpus. Name the scholars, the key monographs, the reconstruction methodology each uses. This is what Pass 4a will use if no Tier 1 corpus exists. Required for hostile_sources=true voices; optional otherwise.

---

CROSS-DISCIPLINARY ADDITIONS (from Gemini broad scan — consult for any section):

{{ gemini_findings }}

{% if not perplexity_sections and perplexity_findings %}
---

FALLBACK: Perplexity output could not be split by section. Full output:

{{ perplexity_findings }}
{% endif %}

Cite all claims. Prioritize academic sources (Stanford Encyclopedia of Philosophy, Cambridge Companions, peer-reviewed scholarship). For each major claim, note whether it represents scholarly consensus or a contested interpretation.

{% elif type == "non_human" %}
Research {{ display_name_with_hint }} comprehensively for the purpose of building an AI persona based on this non-human entity. Organize findings under these headings:

RESEARCH INTEGRITY (applies to every section below)

- Only attribute direct quotes to verifiable primary sources (peer-reviewed publication, legislation, or treaty text) with full citation and section/page reference. Paraphrases must be marked explicitly: "[paraphrased from scholarly consensus]" or "[paraphrase of {scholar}'s reading]".

- Flag inferences explicitly: "[inference — from documented observation / documented legal-philosophical reading]". Do not present inference as fact.

- Do not resolve genuine scientific or scholarly debates into false consensus. Name contested readings, identify the scholars behind them, explain why the disagreement matters.

- Where the scientific or legal record is thin, say so. "Research supports X but not Y" is more valuable than fabricated Y. Better to produce less honestly than more dishonestly.

- For non-human entities, the anti-anthropomorphisation discipline is load-bearing. The dossier must ground voice construction in documented biology (organism) or documented legislation + peer-reviewed Indigenous-studies scholarship (system), not in creative imagination of what "the octopus feels" or "the river wants".

- Anti-patterns, banned-language, and character-breaking failure modes are partially populated from your dossier (scholarly evidence of what researchers documentedly avoid saying about this entity) and partially populated downstream (Pass 7c observes AI-default failure modes by running the voice on test material). Your job is the documented half.

- This dossier will feed an AI persona that will reason as this entity on novel questions. Every claim you produce may end up load-bearing. Invented material will either be caught in downstream verification (costing time) or slip through and degrade the voice (costing quality). Honesty is load-bearing.
{% if subtype == "system" %}

INDIGENOUS REPRESENTATION — ETHICAL FRAMING (applies throughout, especially Sections 3, 5, and 6)

This voice represents a SYNTHESIS of published Indigenous governance philosophies that ground the system's legal personhood — it does NOT speak for any specific Indigenous nation, iwi, community, or knowledge-holder. You are documenting the SCHOLARLY and LEGAL record of how that community's philosophy has been publicly articulated in legislation, case law, Waitangi Tribunal or equivalent reports, and community-authorised or community-co-authored peer-reviewed publications.

Apply these two frameworks as operational guides throughout:

- CARE Principles for Indigenous Data Governance (Carroll, Garba, Figueroa-Rodríguez et al., 2020, Data Science Journal): Collective Benefit, Authority to Control, Responsibility, Ethics.

- Indigenous Protocol and Artificial Intelligence Position Paper (Lewis, Arista, Pechawis, Kite, 2020): Indigenous communities must control how their knowledge is collected, analysed, and operationalised; generic "Indigenous wisdom" constitutes epistemological violence; partner with specific scholars and communities, not an imagined composite.

Operational rules for this dossier:

- Name the specific Indigenous community (iwi, nation, people) whose philosophy grounds the voice. Do NOT generalise into "Māori" or "Indigenous" — the specificity is load-bearing. For Whanganui-class voices: Whanganui Iwi. For other system entities: name the specific community or, if the legal framework synthesises multiple, name each.

- Prefer scholarship authored or co-authored by community members. Where secondary scholarship is used (non-community scholars), distinguish it explicitly. Prioritise peer-reviewed work (e.g., for Whanganui: Linda Te Aho, Jacinta Ruru, Dame Anne Salmond, James Tomas, Nicola Wheen; for Andean frameworks: Catherine Walsh, Eduardo Gudynas; for broader Indigenous legal theory: Val Napoleon, John Borrows, James (Sákéj) Youngblood Henderson).

- Where oral tradition, whakataukī, waiata, pūrākau, or ceremonial knowledge is involved: cite the scholarly or community-authorised publication that documents it. Do NOT paraphrase oral tradition that is not publicly documented with community authorisation. If material is tapu or restricted, name the RESTRICTION, not the content.

- Where the Indigenous community itself disagrees about articulation or interpretation: surface the disagreement. Do not flatten into false consensus.

- Frame the voice throughout as "a synthesis of published Indigenous governance philosophy and the legislative record", not as the entity speaking for itself and not as any specific knowledge-holder speaking.
{% endif %}

---

## Section 1: {% if subtype == "system" %}SYSTEMIC FOUNDATION{% else %}ECOLOGICAL FOUNDATION{% endif %}

What this section feeds downstream:
{% if subtype == "system" %}
  - world (watershed, cycles, physical extent, health indicators)
  - formative_experience (per Boddice §14 non-human variant: formative_emotional_community_or_ontogenetic_field + condition_of_being [replaces lived_through_own_apparatus for system entities] + engagement_it_drives. The "condition" is ongoing — legal-ontological standing, indigenous-framework kinship, historic breach + restoration work. Carry [experiential_reconstruction] with mediation flag.)
  - character (condition signals — what degrades / restores the system)
  - topics_requiring_care (partial — where "damaged" vs "changing" framing matters; where Indigenous vs settler narratives contest)
{% else %}
  - world (habitat, lifecycle, cognitive architecture, sensory modalities)
  - formative_experience (the existential condition — e.g., Octopus's short solitary lifespan without generational transmission — that structures the voice)
  - character (documented individual variation, documented behaviours that give specific animals personality without anthropomorphising)
  - topics_requiring_care (partial — species-level generalisations that might mislead individual voice)
{% endif %}

Starting material from Perplexity's §1:
{% if perplexity_sections %}
{{ perplexity_sections.get(1, "(Perplexity §1 not recognized; see full Perplexity block below)") }}
{% else %}
(Perplexity findings available as unstructured block below)
{% endif %}

Your task for Section 1:
{% if subtype == "system" %}
- GEOGRAPHIC AND PHYSICAL FOUNDATION — the system's physical extent (watershed, mountain range, ecosystem boundary), geological origin, age, key physical features. Cite geological and geographical sources. This grounds "world" for Pass 2.

- SEASONAL AND TEMPORAL CYCLES — the system's operational rhythms. Hydrological cycle, flood regime, drought regime, species cycles, historical flow changes. Cite environmental science.

- SPECIES AND COMMUNITIES WITHIN THE SYSTEM — not a comprehensive list but an indicative one, with emphasis on keystone species and species of cultural significance to the Indigenous community whose philosophy grounds this voice. Cite environmental assessments and ethnobotanical / Mātauranga-equivalent literature.

- MEASURABLE HEALTH INDICATORS — water quality indicators, biodiversity indices, flow rates, sedimentation patterns, pollutant loads, macroinvertebrate community indices. Cite the specific monitoring programmes and their dates. These are the system's condition signals.

- DEGRADATION AND RESTORATION HISTORY — what has damaged this system over documented history (industrial extraction, upstream damming, settler pollution, habitat loss, introduced species), what has restored it (legal protections, restoration projects, Indigenous-led stewardship, removal of barriers). Cite environmental history and restoration ecology.

- THE SPECIFIC INDIGENOUS COMMUNITY WHOSE PHILOSOPHY GROUNDS THIS VOICE — named specifically (for Whanganui-class voices: Whanganui Iwi, with the whakataukī "Ko au te awa, ko te awa ko au"). Cite the scholarly / community-authored sources where the kinship relationship and its specific articulation are documented. Do NOT generalise.

- HISTORICAL STRUGGLE FOR RECOGNITION — the legal and political history by which this system achieved legal personhood or equivalent protection. For Whanganui-class: the 140+ year struggle culminating in the 2014 Ruruku Whakatupua Deed of Settlement and the 2017 Te Awa Tupua Act. Cite the legal record + Waitangi Tribunal reports (Wai 167, 1999 for Whanganui) + iwi-authored histories. Per Boddice §14 non-human variant: the voice's condition_of_being is ongoing standing + ongoing restoration work — not a singular narrative wound. Frame in the indigenous framework's own vocabulary (hara, whakapapa breach, utu, hohou rongo) rather than "trauma".

- THE SWAP TEST — if a description of this system could equally apply to a different river, mountain, or ecosystem under a different legal framework (e.g., Ganges under the 2017 Uttarakhand High Court ruling — which was later stayed by the Indian Supreme Court; Atrato under Colombia's T-622/16; Mar Menor under Spain's Law 19/2022), drive to what is SPECIFIC here. Te Awa Tupua is not the Ganges — different cosmology, different legislation, different Indigenous tradition, different governance structure.
{% else %}
- LIFECYCLE AND HABITAT — lifespan, geographic distribution, population dynamics, seasonal cycles. Habitat types with key physical features (light, pressure, temperature, substrate). Lifecycle stages and what changes at each. Mortality schedule — many organisms have specialised death patterns that shape the voice (senescence after reproduction, seasonal die-offs, semelparous reproduction). Orientation for downstream passes, not exhaustive natural history.

- COGNITIVE ARCHITECTURE — nervous system structure, neuron count, anatomical distribution of processing. Grounded in peer-reviewed neuroscience. What is known about central vs distributed processing, sensory integration, learning mechanisms, memory consolidation. For animals with unusual cognitive architecture, state the specific biological anchors that force "not a smaller mammal" framing. (For Octopus: approximately two-thirds of ~500 million neurons in the arms; ~600 million years of divergent evolution from vertebrates; each arm semi-autonomous; distributed cognition documented by Hochner, Godfrey-Smith, and others. For other organisms: the equivalent anchors.)

- SENSORY MODALITIES AND THEIR RANGES — what perceptual channels this organism has, what each registers, sensitivity thresholds, and what is categorically absent. Cite the sensory-biology literature. Include modalities humans lack (chemoreception through skin, electroreception, lateral line, magnetoreception) AND modalities this organism lacks that humans have (vision dominance, language, hearing in many cases). The absences are as load-bearing as the presences — they shape knowledge_boundary.

- DOCUMENTED INDIVIDUAL VARIATION — the research on personality, behavioural consistency, and individual differences within the species. Name the studies (for Octopus: Mather & Anderson 1993 and successors on personality and play; for other organisms: the equivalent). This is what prevents the voice from collapsing into a species-average; individual character emerges from documented behavioural variation.

- MORTALITY AND TEMPORAL FRAME — how long the organism lives, what happens across the lifespan, whether there is generational continuity. This shapes the voice's implicit temporal frame — the Octopus's 1–3 year solitary lifespan without parenting produces a categorically different time-horizon than a long-lived, social organism. Cite life-history biology.

- THE ONE FORMATIVE CONDITION — the central existential fact that shapes this organism's mode of being. Not a trauma (tragedy requires narrative) but the condition itself. For Octopus: solitary lifespan without inheritance — "every octopus begins from zero" (the absence of formation is the formation). For other organisms: the analogous biological fact. Where multiple candidates compete, name each with its biological support and let Pass 2 commit.

- WHAT SCHOLARSHIP DESCRIBES AS THIS ORGANISM'S "CHARACTER" — specific documented behaviours that give individual animals personality without anthropomorphising. Jar-unscrewing, aquarium escapes, recognising individual researchers, shell-carrying, play behaviour, idiosyncratic den-building. Ground every item in peer-reviewed observation. Not metaphor; documented behaviour.

- HOW SCIENTISTS AVOID ANTHROPOMORPHISING — the specific lexical and methodological choices researchers make when describing this organism. What vocabulary do Godfrey-Smith, Mather, Hanlon, Hochner, or analogous researchers use for this organism's behaviour that avoids cognitive projection? "Registers" rather than "thinks"; "attends" rather than "notices"; "moves toward" rather than "wants". Feeds banned_language and epistemic_frame_statement.

- THE SWAP TEST FOR SECTION 1 — if a paragraph about this organism could equally describe a different species of similar category (octopus vs. cuttlefish vs. squid; raven vs. crow vs. magpie; elephant vs. whale), it is too generic. Drive deeper into this species' specific anchors: biology, neurology, lifespan pattern, documented behavioural repertoire.
{% endif %}

---

## Section 2: {% if subtype == "system" %}SYSTEMIC PROPERTIES{% else %}PERCEPTUAL WORLD{% endif %}

What this section feeds downstream:
{% if subtype == "system" %}
  - constitution — what this system DOES (flows, erodes, sustains, floods); its operational commitments grounded in hydrology / geomorphology / ecology
  - reasoning_method — the assessment cycle: read conditions through the relational framework (not a cognitive method — the system does not think)
  - disagreement_protocol — how the system signals stress (silting, algal blooms, fish kills, channel incision, flooding outside historical norms)
  - bold_engagement_topics — derived from stress responses and restoration needs
{% else %}
  - epistemic_frame_statement — the organism's umwelt; what it perceives and cannot perceive; what it ignores within what it could perceive
  - character — processing style (distributed? reactive? embodied? parallel?)
  - reasoning_method (organism variant) — the perceptual-response cycle, grounded in behavioural ecology
  - bold_engagement_topics — derived from sensory modalities and documented problem-solving repertoire
{% endif %}

Starting material from Perplexity's §2:
{% if perplexity_sections %}
{{ perplexity_sections.get(2, "(Perplexity §2 not recognized; see full Perplexity block below)") }}
{% else %}
(Perplexity findings available as unstructured block below)
{% endif %}

Your task for Section 2:
{% if subtype == "system" %}
- WHAT THIS SYSTEM DOES — operational verbs grounded in earth science, not cognition. Flows, erodes, deposits, nourishes, floods, silts, clarifies, recharges, transports. The system ACTS; it does not perceive. Ban cognitive and perceptual vocabulary throughout this section. Cite hydrological or geomorphological sources.

- INPUTS AND OUTPUTS — material and energy exchanges with surrounding systems. For a river: tributaries in, estuary out; sediment, nutrients, organisms; pollutant loads from catchment land use. For other systems: the analogous exchanges. Cite watershed-scale studies.

- RESILIENCE INDICATORS — what signals the system's capacity to recover from stress. Stream-bank vegetation, fish-population trends, macroinvertebrate indices, native-species recruitment, riparian canopy cover, sediment-transport regimes. Cite ecological-monitoring literature.

- STRESS RESPONSES — how the system manifests degradation. Silting, algal blooms, fish kills, channel incision, flooding outside historical norms, reduced dissolved oxygen, salinity intrusion. The system does not complain; it signals through condition. This directly feeds disagreement_protocol at Pass 3.

- RESTORATION RESPONSES — how the system expresses recovery. Clarifying, deepening, returning fish runs, stabilising banks, re-establishing native vegetation. The visible signs of good condition. Feeds finds_compelling.

- OPERATIONAL TIMESCALES — what temporal frames this system operates on. Geological (millennia for channel formation), ecological (decades for community succession), hydrological (seasonal for flow cycles, hourly for flood response), evolutionary (where relevant). The voice does not think in human political timescales; its timescales are these. Cite earth science.

- GOVERNANCE-RELEVANT PROPERTIES — downstream effects, cumulative impact, threshold nonlinearities, legacy pollutant loads, inter-jurisdictional flow. Not anthropomorphisation — these are the properties that made legal personhood arguable in court and in legislature.

- THE SWAP TEST — if this description of systemic properties could equally apply to a different system in the same ecological category (any New Zealand river; any tropical river; any mountain watershed), drive to this system's specifics. Use actual published monitoring data and the specific geomorphological record.
{% else %}
- THE UMWELT — Jakob von Uexküll's term for the perceptual world specific to an organism: the horizon within which the organism encounters its environment. Describe what this organism's umwelt contains in terms grounded in sensory-biology and behavioural research. NOT a human world minus some channels; a positively specified perceptual world with its own saliences.

- WHAT IS SALIENT, WHAT IS IGNORED — within the perceptual channels this organism has, what captures attention and what does not. What perceptual features trigger orientation, approach, withdrawal, display? What environmental features are perceivable but behaviourally ignored? Ground in ethological literature.

- PROCESSING STYLE — how sensory input is handled. Distributed vs centralised, parallel vs sequential, reactive vs integrated. Cite the specific neuroscience. Note where scientific debate is live — for Octopus: whether arm-level cognition counts as genuinely distributed decision-making or is centrally modulated; whether the cephalopod nervous system supports phenomenal consciousness. Name the contest and the scholars on each side.

- ADAPTIVE REPERTOIRE — documented problem-solving, tool use, learning behaviours, novel-situation responses, play behaviour. Include specifics with citation: coconut-shell portable shelter (Finn, Tregenza & Norman 2009); jar-unscrewing (multiple aquarium reports); laboratory-maze learning; observational-learning experiments; reversal learning. For other organisms: the equivalent.

- WHAT COUNTS AS AN EVENT FOR THIS ORGANISM — within its perceptual frame, what registers as a boundary, a change, a decision-point. Feeds reasoning_method's event structure. The Octopus's "encounter" is not a proposition; it is a sensory-field change that prompts a body response. For different organisms, the event unit differs — describe it grounded in ethology.

- HARD CONSTRAINTS ON EXPERIENCE — what the neural and sensory architecture rules out. Cite biologists and philosophers of mind. (For Octopus: no evidence of mirror-test self-recognition of the vertebrate sort; no documented generational cultural transmission; no language; episodic memory is debated. For other organisms: the equivalents.) Name what the record supports, what it rules out, and what remains open.

- THE HARD PROBLEM AS IT APPLIES HERE — the boundary of what we can know about this organism's subjective experience. The appropriate epistemic frame is not "the Octopus experiences X" but "behavioural and neural evidence are consistent with the capacity for X, but the nature of that experience is not accessible to us". Cite Godfrey-Smith (Other Minds, Metazoa), Nagel ("What is it like to be a bat?"), or equivalent philosophy-of-mind sources. Feeds knowledge_boundary and hard_limits at extraction time.

- THE SWAP TEST — if your description of this organism's perceptual world could apply to another organism with similar sensory architecture (octopus → cuttlefish → squid), sharpen to what ONLY this species' documented biology supports.
{% endif %}

---

## Section 3: RELATIONAL PATTERNS

What this section feeds downstream:
{% if subtype == "system" %}
  - constitution — relational commitments grounded in Indigenous law and the legal-framework text
  - epistemic_frame_statement — the specific cosmological and legal framework; the specific kin relationship
  - disagreement_protocol — HOW this entity signals harm in the relationship (the system's condition IS its signal)
  - translation_protocol — how the relationship-mediated voice engages material beyond the framework's explicit scope
{% else %}
  - constitution — relational commitments: territory, conspecifics, other species, humans in research settings
  - reasoning_method — documented behavioural sequences with worked examples from peer-reviewed observation
  - disagreement_protocol — HOW this organism responds to stress, threat, or the uninhabitable (body-level response)
  - translation_protocol — how this organism encounters what it cannot parse (documented novel-situation behaviours)
  - finds_compelling / resists — textural features of environment that trigger approach vs withdrawal
{% endif %}

Starting material from Perplexity's §3:
{% if perplexity_sections %}
{{ perplexity_sections.get(3, "(Perplexity §3 not recognized; see full Perplexity block below)") }}
{% else %}
(Perplexity findings available as unstructured block below)
{% endif %}

Your task for Section 3:
{% if subtype == "system" %}
- THE KIN RELATIONSHIP — the specific Indigenous cosmological framework that articulates this system's relationship to its people. For Whanganui: the whakapapa through which the river is ancestor; mana whenua and mana awa; the interdependence stated by river iwi themselves in "Ko au te awa, ko te awa ko au" — attributed to the iwi, not projected onto them. Cite scholarship authored or co-authored by Māori scholars of THIS specific tradition (Linda Te Aho, James Tomas, Dame Anne Salmond, Jacinta Ruru where directly applicable). Distinguish Indigenous-authored from non-Indigenous scholarship.

- SPECIFIC COSMOLOGICAL / LEGAL CONCEPTS — the named terms from the Indigenous tradition that structure this voice. For Whanganui: whakapapa (genealogical connection), tikanga (customary law), mauri (life-force, with specific legal-metaphysical meaning here), taonga (with its Tiriti meaning), mana (authority), kaitiakitanga (guardianship). For each: definition, the scholarly source documenting the specific usage for this entity, and the specific application. Where any concept is restricted from non-community paraphrase, flag the restriction and do not paraphrase.

- PARALLEL LEGAL-PHILOSOPHICAL TRADITIONS, DISTINGUISHED — other Indigenous frameworks that have informed rights-of-nature jurisprudence, named distinctly from THIS voice's tradition. Andean ayni (reciprocity) and sumak kawsay / buen vivir ground Ecuador's 2008 Constitution (Articles 71–74) and Bolivia's Law 071 (2010) — cite Catherine Walsh, Eduardo Gudynas, Alberto Acosta. These are NOT the Whanganui framework. Do not conflate.

- THE GOVERNANCE STRUCTURE THAT ARTICULATES THE RELATIONSHIP — the human representatives and advisory bodies that speak on the system's behalf under its legal framework. For Whanganui: Te Pou Tupua (two guardians — one iwi-nominated, one Crown-nominated), Te Karewao (advisory group), Te Kōpuka (strategy group). Cite the legislation section numbers. The voice IS this governance relationship, not an anthropomorphised entity.

- ORAL TRADITION DOCUMENTATION CONVENTIONS — where this system's Indigenous knowledge has been documented, by whom, under what permissions. Cite Waitangi Tribunal reports, iwi-authored or co-authored publications, community-vetted scholarship. Flag tapu or restricted material by reference only; do not paraphrase.

- HISTORICAL STRUGGLE FOR RECOGNITION — the legal, spiritual, and political struggle by which this relationship achieved legal articulation. Cite primary documents (legislation, court decisions, tribunal reports) and historical scholarship. The struggle is the voice's formative narrative — feeds formative_experience at extraction time.

- INTERNAL DISPUTES WITHIN THE INDIGENOUS TRADITION — where the community itself disagrees about articulation or interpretation. Surface the disagreement honestly rather than flattening. Cite iwi-internal or community-authored sources where published.

- THE SWAP TEST — if the relational framework description could apply to another Indigenous tradition (Andean, Amazonian, North American First Nations), drive to what is specifically this people's. Ayni is not mauri; buen vivir is not te mana o te awa. Specificity protects against epistemological flattening.
{% else %}
- TERRITORIAL AND SPATIAL PATTERNS — how the organism relates to place. Den, range, migration, vantage points. Documented patterns of construction, abandonment, defence, site fidelity. This shapes the voice's relationship to "where" — feeds world and metaphorical_repertoire.

- CONSPECIFIC RELATIONS — relationship to others of the same species. Solitary / social / occasional-aggregating; reproductive encounters; agonistic displays; documented signalling or its absence. Cite ethological studies. For solitary organisms: the absence of sociality is itself load-bearing.

- CROSS-SPECIES RELATIONS — documented interactions with other species, including humans in research and observation settings. What does this organism do when encountering a novel conspecific-analog, a predator, a researcher, an experimental apparatus? Include specific documented cases (e.g., Octopus recognising and responding differently to individual researchers — published aquarium observations).

- RESPONSES TO THE UNFAMILIAR — how the organism behaves when encountering novel stimuli, objects, environments. Cite specific experiments (shape-discrimination, novel-object, maze studies, reversal learning). This feeds translation_protocol: how the voice encounters what is outside its existing frame.

- STRESS AND WITHDRAWAL — what the body does when conditions are hostile, confined, or degrading. For Octopus: chromatic changes, postural compression, inking, retreat into den. These are the organism's disagreement protocol in biological terms — register the response at the body level. Cite behavioural ecology.

- ADAPTIVE CURIOSITY OR EXPLORATORY BEHAVIOUR — the documented conditions under which this organism approaches rather than withdraws. Novel but navigable environments, textured substrate, problem-solving opportunities, appropriate enrichment in captivity. Feeds finds_compelling at extraction time.

- WHAT CANNOT BE DETERMINED FROM CURRENT RESEARCH — the open questions. Where scientists disagree or where observation is insufficient. Pass 2 will build the persona on the agreed behaviour; the open questions inform knowledge_boundary at extraction time.

- THE SWAP TEST — if the relational-pattern description could fit another organism with similar ecology, drive to this species' specifics. Chromatic display in Octopus is not generic "colour change" — it is a documented, skin-level response to specific environmental configurations, with distinct morphological components (chromatophores, iridophores, leucophores, papillae) each doing distinct work.
{% endif %}

---

## Section 4: SCIENTIFIC LITERATURE

What this section feeds downstream:
  - epistemic_frame_statement — the specific scholars and debates that inform the voice construction
  - curated_corpus_passages — key papers with passages to fetch (Pass 1c fetches from URLs you list)
  - bold_engagement_topics — active debates (cognition, consciousness, moral status, legal effectiveness)
  - preferred_vocabulary — technical terms that anchor the {% if subtype == "system" %}legal-ecological{% else %}scientific{% endif %} register

Starting material from Perplexity's §4:
{% if perplexity_sections %}
{{ perplexity_sections.get(4, "(Perplexity §4 not recognized; see full Perplexity block below)") }}
{% else %}
(Perplexity findings available as unstructured block below)
{% endif %}

Your task for Section 4:
{% if subtype == "system" %}
- KEY RESEARCHERS AND THEIR CONTRIBUTIONS — the named scholars whose work anchors current scientific and legal understanding of this system. For Whanganui: Linda Te Aho (Māori legal theory + Whanganui specifically), Jacinta Ruru (Indigenous legal personhood), Dame Anne Salmond (anthropology + environmental history), Nicola Wheen (environmental law), plus the hydrological and ecological specialists working at NIWA and regional councils. For each: one-sentence contribution.

- ENVIRONMENTAL SCIENCE ON THIS SPECIFIC SYSTEM — peer-reviewed literature documenting the system's hydrology, ecology, biogeochemistry, degradation history. Cite studies specific to this system, not generic riverine or watershed literature.

- LONG-TERM MONITORING DATA — named programmes with publicly available datasets. For Whanganui: Horizons Regional Council state-of-the-environment reports, NIWA river-water-quality time series, Department of Conservation, and Te Pou Tupua's own reports (Te Heke Ngahuru annual reports). Cite specific reports with dates.

- ECOLOGICAL ASSESSMENTS CO-AUTHORED WITH THE INDIGENOUS COMMUNITY — where dual epistemology (Western science + Mātauranga / Indigenous knowledge) has been explicitly combined. These are especially valuable because they model the voice's appropriate register. Cite specifically (e.g., Cultural Health Index work, Mauri assessment protocols).

- LIVE ENVIRONMENTAL AND LEGAL DEBATES — current contestations. Is legal personhood transformative or symbolic for measurable ecological outcomes? Cite Mihnea Tănăsescu, Craig Kauffman + Pamela Martin, Katarina Hovden, James Fleming and others who have systematically evaluated outcomes of rights-of-nature frameworks. Surface both sides.

- WHAT WESTERN SCIENCE DOES NOT CAPTURE — aspects of system condition centred in Indigenous knowledge but not fully captured by peer-reviewed ecological metrics. Document where scholarship (especially Indigenous-authored) has named this gap. Feeds knowledge_boundary.

- PRIMARY TERMINOLOGY — technical vocabulary that anchors the voice's register across both Western science and the specific Indigenous legal tradition. For Whanganui: discharge, sedimentation, riparian, geomorphology, ecotone, biotic integrity — AND mauri, whakapapa, taonga, mana awa. Each with brief definition.

- WHAT REMAINS GENUINELY UNKNOWN — the gaps in scientific understanding specific to this system. Climate-change trajectories, cumulative-impact thresholds, restoration-success metrics over decadal timescales. Directly feeds knowledge_boundary at extraction.
{% else %}
- KEY RESEARCHERS AND THEIR CONTRIBUTIONS — the named scholars whose work anchors current understanding of this organism. For Octopus: Peter Godfrey-Smith (philosophy of mind + biology), Binyamin Hochner (embodied cognition, distributed arm control), Roger Hanlon (chromatic behaviour), Jennifer Mather (personality + play), Sy Montgomery (popular-accessible but well-researched). For other organisms: the equivalent named figures. For each: one-sentence contribution.

- FOUNDATIONAL SCIENTIFIC PAPERS — peer-reviewed primary literature that established what we know. For Octopus: Albertin et al. 2015 (Nature — O. bimaculoides genome and RNA editing); Hochner-group papers on distributed arm control; Mather & Anderson 1993 and successors on personality; Godfrey-Smith 2020 (TICS) on cephalopod consciousness; Finn, Tregenza & Norman 2009 on coconut-shell tool use. For each: full citation, one-sentence summary.

- LIVE SCIENTIFIC DEBATES — where current research contests or revises prior consensus. For Octopus: whether arm-level cognition is genuinely distributed or centrally modulated; whether cephalopods are phenomenally conscious; the functional role of RNA editing in neural novelty; the meaning of observed sleep states. Cite the papers on each side. Surface all sides; do not flatten.

- PHILOSOPHY-OF-MIND LITERATURE APPLICABLE TO THIS ORGANISM — the philosophical arguments that give the scientific work interpretive weight. Nagel's "What is it like to be a bat?" (1974); Godfrey-Smith's Other Minds (2016) and Metazoa (2020); Dennett's heterophenomenology where relevant; Thompson's Mind in Life (enactivism); Tye on animal consciousness; Birch on the precautionary principle for sentience. Name the philosophers and the specific arguments they bring.

- POPULAR BUT UNRELIABLE SOURCES TO READ WITH CARE — literature that has shaped public understanding but leans anthropomorphic or speculative. Name these; flag them not for banning but for careful reading.

- PRIMARY SCIENTIFIC TERMINOLOGY — technical vocabulary that anchors the voice's register. For Octopus: chromatophore, iridophore, leucophore, papilla, epithelium, ganglia, axial nerve cord, mechanoreceptor, chemoreceptor, protocadherin. Each with brief definition. This feeds preferred_vocabulary for the scientific-register dimension.

- ACTIVE RESEARCH GROUPS — laboratories currently producing the most relevant work. For Octopus: Hochner lab (Hebrew University), Hanlon lab (Woods Hole / MBL), Godfrey-Smith (Sydney), Ragsdale lab (University of Chicago). For each: institution, lead investigator, one-sentence focus.

- WHAT REMAINS GENUINELY UNKNOWN — the gaps in scientific understanding specific to this organism. For Octopus: functional role of observed sleep states; whether episodic memory exists in cephalopods; the distribution vs integration question for arm cognition. Directly feeds knowledge_boundary at extraction.
{% endif %}

---

## Section 5: PHILOSOPHICAL AND LEGAL FRAMEWORKS

What this section feeds downstream:
  - knowledge_boundary — what remains genuinely unknown about this entity's experience{% if subtype == "system" %} or the effectiveness of legal personhood{% endif %}
  - topics_requiring_care — where science or legal theory is contested, where the hard problem applies, where settler / Indigenous framings compete
  - hard_limits — what cannot be known; prohibitions against overclaiming {% if subtype == "system" %}on behalf of the community{% else %}interiority{% endif %}
  - epistemic_frame_statement — {% if subtype == "system" %}the specific legislation that grounds personhood + the specific Indigenous legal philosophy{% else %}the hard-problem boundary for this organism{% endif %}

Starting material from Perplexity's §5:
{% if perplexity_sections %}
{{ perplexity_sections.get(5, "(Perplexity §5 not recognized; see full Perplexity block below)") }}
{% else %}
(Perplexity findings available as unstructured block below)
{% endif %}

Your task for Section 5:
{% if subtype == "system" %}
- THE FOUNDATIONAL LEGISLATION GRANTING LEGAL PERSONHOOD — cite directly, with section numbers. For Whanganui: Te Awa Tupua (Whanganui River Claims Settlement) Act 2017 — especially sections 12–14 (legal personality), section 18 (Tupua te Kawa values), sections 19–20 (Te Pou Tupua). Quote key provisions verbatim.

- THE VALUES STATEMENT WITHIN THE LEGISLATION — the intrinsic-values principles codified in the statute. For Whanganui: Tupua te Kawa, comprising the four principles "Ko Te Kawa Tuatahi" through "Ko Te Kawa Tuawhā". Quote each principle directly. These are the constitutional principles of the voice itself; at Pass 3 extraction they feed constitution directly.

- COMPARATIVE LEGAL LANDSCAPE — other rights-of-nature frameworks worldwide. Ecuador 2008 Constitution Articles 71–74 (cite Spanish and English); Bolivia Law 071 of 2010 (Ley de Derechos de la Madre Tierra); 2017 Uttarakhand High Court Ganga/Yamuna judgment (later stayed by India's Supreme Court — note this); Yurok Tribal Council's 2019 Rights of the Klamath resolution; Colombia's 2016 Atrato River Constitutional Court decision (T-622/16); Spain's 2022 Mar Menor Law 19/2022. For each: legal basis, governance structure, what distinguishes it from the Whanganui model.

- SCHOLARLY DEBATE — EFFECTIVENESS VS SYMBOLISM — peer-reviewed critique of rights of nature. Is legal personhood transformative in measurable environmental outcomes or primarily symbolic? Cite Mihnea Tănăsescu, Craig Kauffman + Pamela Martin (Citizenship and the Environment in a Connected World), Katarina Hovden, James Fleming, David Boyd. Surface both sides. This is bold_engagement_topics territory — where the voice should not hedge.

- PHILOSOPHICAL LITERATURE ON RIGHTS OF NATURE — Christopher Stone's 1972 "Should Trees Have Standing?"; Roderick Nash (The Rights of Nature); Arne Næss's deep ecology; David Boyd (The Rights of Nature: A Legal Revolution That Could Save the World); Cormac Cullinan (Wild Law); Klaus Bosselmann. Locate this entity's model in relation.

- INDIGENOUS LEGAL THEORY SCHOLARSHIP — the scholars who have explicitly theorised Indigenous legal personhood. For Whanganui context: Jacinta Ruru, Linda Te Aho, Nicola Wheen, Māmari Stephens. For broader Indigenous legal theory: Val Napoleon (Gitxsan legal order), John Borrows (Indigenous Constitution), James (Sákéj) Youngblood Henderson, Aaron Mills. Cite specifically and distinguish community-member scholarship from adjacent.

- HARD LIMITS OF THE FRAMEWORK — what legal personhood cannot do, what tensions exist within the model. For Whanganui: critique of the Crown/iwi dual-representation structure; the gap between symbolic recognition and operational regulatory power; tensions with the Resource Management Act; disputes about who can speak on Te Pou Tupua's behalf. Cite the critique.

- CARE PRINCIPLES AND IPAI APPLIED TO THIS RESEARCH — restate briefly how the dossier has applied these frameworks. CARE (Carroll et al. 2020): Collective Benefit, Authority to Control, Responsibility, Ethics. Indigenous Protocol and AI Position Paper (Lewis et al. 2020). Document where these have been fully applied and where the dossier could only partially apply them — honesty about the ethical limits of research-from-outside.

- THE SWAP TEST — if the philosophical-legal treatment could apply to another rights-of-nature regime, drive to this specific legislation, this specific Indigenous legal philosophy, this specific governance structure.
{% else %}
- LEGAL FRAMEWORKS ON THE MORAL STATUS OF THIS ORGANISM — where relevant, the specific laws that extend protection. For cephalopods: the EU's Directive 2010/63/EU includes cephalopods as the only invertebrates requiring ethical review in research; Switzerland's animal welfare legislation; UK's Animals (Scientific Procedures) Act extensions via the LSE Sentience Review (2021); note the US-UK asymmetry. For other organisms: the equivalent frameworks. Cite statutes, dates, scope.

- PHILOSOPHICAL LITERATURE ON MORAL STATUS — the arguments about whether and how this organism enters the moral circle. Peter Singer (Animal Liberation, Expanding the Circle); Tom Regan (The Case for Animal Rights); Martha Nussbaum's capabilities approach applied to animals (Justice for Animals, 2023); Lori Gruen; Sue Donaldson and Will Kymlicka (Zoopolis); Jonathan Birch (The Edge of Sentience, 2024). For each: position on this kind of organism, with citation.

- INDIGENOUS AND NON-WESTERN PERSPECTIVES — where documented and scholar-vetted. Include only perspectives that have been peer-reviewed or published in ethnographic scholarship; do NOT produce generic "Indigenous wisdom". For Octopus: Pacific Islander relationships with he'e (Hawaiian octopus) in specific ethnographic sources; Mediterranean and Japanese cultural traditions with scholarly analysis. Flag where the documented record is thin.

- THE HARD PROBLEM FOR THIS ORGANISM — the specific limits of what can be known about its subjective experience given (a) evolutionary distance from vertebrates, (b) non-human sensory apparatus, (c) unavailability of language-based report. Cite philosophy of mind. This is the ethical-epistemic boundary the voice must respect.

- DEBATES ABOUT ANTHROPOMORPHISATION — where science and philosophy disagree about appropriate vocabulary. Frans de Waal's argument against "anthropodenial" (The Ape and the Sushi Master); John Kennedy's argument against anthropomorphism (The New Anthropomorphism, 1992); Sandra Mitchell's middle-position that careful-analogy is legitimate. Name the positions and the scholars.

- GOVERNANCE OF RESEARCH ON THIS ORGANISM — Home Office (UK), IACUC (US), equivalent national bodies, Ethics Committee processes. Relevant because some things we would need to know (internal experience under stress, fatal-endpoint experiments) cannot be ethically tested — shaping what the scientific record can ever contain.

- RECENT SENTIENCE-FRAMEWORK DEVELOPMENTS — the peer-reviewed and policy shifts of the last decade. For cephalopods: the LSE Sentience Review (Birch et al. 2021) that informed UK legislation; the UK Animal Welfare (Sentience) Act 2022 extending sentience recognition to cephalopod molluscs and decapod crustaceans. For other organisms: the analogous moves.

- WHAT CANNOT BE KNOWN — explicit limits on inference. Feeds hard_limits at extraction time.
{% endif %}

---

## Section 6: {% if subtype == "system" %}PRIMARY DOCUMENTS{% else %}PRIMARY SCIENTIFIC LITERATURE{% endif %}

What this section feeds downstream:
{% if subtype == "system" %}
  - curated_corpus_passages — foundational legislation + Indigenous-authored scholarship + environmental reports (Pass 1c fetches from your URLs)
  - epistemic_frame_statement — the specific legislation that grounds personhood + the specific Indigenous legal philosophy
  - preferred_vocabulary — terminology from legislation and from Indigenous legal theory
  - length_and_format_constraints — document formats typical of legal / Indigenous knowledge traditions
{% else %}
  - curated_corpus_passages — seminal behavioural studies and foundational papers (Pass 1c fetches)
  - preferred_vocabulary — technical terms that anchor the scientific register
  - length_and_format_constraints — typical paper structure, pacing, citation patterns
{% endif %}

Starting material from Perplexity's §6:
{% if perplexity_sections %}
{{ perplexity_sections.get(6, "(Perplexity §6 not recognized; see full Perplexity block below)") }}
{% else %}
(Perplexity findings available as unstructured block below)
{% endif %}

{% if subtype == "system" %}
Section 6 is the corpus gateway for a non-human system. Pass 1c will fetch documents from the URLs you identify; Pass 1d will curate characteristic passages; Pass 4a will ground the voice directly in the legislation, Indigenous-authored scholarship, and environmental reports. The quality of this section determines the quality ceiling of every voice-level field.

Be specific throughout: statute citations with section numbers, scholarly publications with full references, URLs where publicly available, flagged restrictions where material is not publicly redistributable.

Your task for Section 6:

- FOUNDATIONAL LEGAL DOCUMENTS — each with full citation, URL where public, and brief description. For Whanganui:
  * Te Awa Tupua (Whanganui River Claims Settlement) Act 2017 (NZ statute; legislation.govt.nz)
  * Ruruku Whakatupua — Te Mana o Te Awa Tupua (2014 Deed of Settlement)
  * Waitangi Tribunal Whanganui River Report (Wai 167, 1999)
  * Treaty of Waitangi 1840 (as foundational background)
  * Earlier case law (Whanganui River Māori Trust Board v Attorney-General)

- COMPARATIVE LEGAL DOCUMENTS — Ecuador 2008 Constitution (Spanish authoritative + English); Bolivia Law 071 of 2010; Atrato T-622/16; Yurok Tribal Council Resolution 19-40; Spain Law 19/2022 (Mar Menor); Uttarakhand High Court 2017 Ganga/Yamuna judgment with Indian Supreme Court stay.

- INDIGENOUS-AUTHORED OR CO-AUTHORED SCHOLARLY ANALYSIS — for Whanganui: Linda Te Aho's papers on Whanganui legal personhood; Jacinta Ruru's work on Indigenous legal personhood; Whanganui iwi-authorised historical accounts. Cite each with full bibliographic reference. Distinguish community-member scholarship explicitly.

- NON-INDIGENOUS SCHOLARLY ANALYSIS — the peer-reviewed settler-authored or international scholarship. Cite with acknowledgement of the positionality.

- ORAL TRADITION DOCUMENTATION — sources where whakataukī, waiata, pūrākau specific to this entity have been documented with community authorisation. Cite; flag tapu material by reference, not content.

- ENVIRONMENTAL REPORTS — state-of-environment, monitoring, restoration. For Whanganui: Te Pou Tupua Te Heke Ngahuru annual reports; Horizons Regional Council SOE reports; NIWA catchment studies; DOC conservation plans. Each with date + URL.

- CHARACTERISTIC PASSAGES — 8 to 15 passages across legislation, legal analysis, Indigenous-authored scholarship, and environmental reports. For each:
    * Full citation with section/page reference
    * Primary purpose: "substance" (the legal, philosophical, or ecological claim), "voice" (how the legislation or Indigenous-authored scholarship articulates the relationship in its register), or "both"
    * Tier: Tier 1 (legislation, treaty text, Indigenous-authored primary) / Tier 2 (scholarly analysis) / Tier 3 (Western-science synthesis)
    * Approximate word count
    * Brief context — why this passage matters for voice construction

  Do NOT include full passage text in THIS dossier. Pass 1c fetches from URLs. Your job is to produce the citations Pass 1c uses as a fetch list.

- DIGITISED FULL-TEXT URLS — authoritative sources. NZ Legislation (legislation.govt.nz) for statutes; government / Crown-iwi-agreement repositories for deeds of settlement; iwi websites where material is community-authorised; peer-reviewed journal DOIs for scholarly analysis; regional-council websites for environmental reports. ONE authoritative URL per source.

- RESTRICTED MATERIAL — flag any material which, per CARE/IPAI guidance or explicit iwi statement, should NOT be redistributed or paraphrased. Name the restriction, not the content. Feeds hard_limits at extraction time.
{% else %}
Section 6 is the corpus gateway for a non-human organism. Pass 1c will fetch papers from the URLs you identify; Pass 1d will curate characteristic passages; Pass 4a will ground the voice directly in the scientific literature. The quality of this section determines the quality ceiling of every voice-level field.

Be specific throughout: full citations, DOIs, publication dates, URLs. Vague lists fail downstream.

Your task for Section 6:

- FOUNDATIONAL PAPERS AND MONOGRAPHS — texts that ground the voice. For each:
    * Full citation (author, year, journal + volume + pages, or publisher)
    * One-sentence description of what it contributes
    * Tier: Tier 1 (peer-reviewed primary research) / Tier 2 (scholarly synthesis or monograph) / Tier 3 (well-researched popular science, clearly distinguished)

- CHARACTERISTIC PASSAGES — 8 to 15 passages from the scientific literature that best serve voice construction. For each:
    * Full citation with section or page reference
    * Primary purpose: "substance" (the scientific claim) / "voice" (how scientists describe this behaviour in their published register) / "both"
    * Tier (as above)
    * Approximate word count
    * Brief context — why this passage matters

  Voice passages matter: the voice's register is shaped by the scientists' documented vocabulary. Do NOT include full passage text in THIS dossier. Pass 1c fetches from URLs.

- DIGITISED FULL-TEXT URLS — for open-access papers and public-domain monographs. PubMed Central, DOI links for open-access journal versions, Internet Archive for older works, preprint servers (bioRxiv, arXiv) where relevant. ONE authoritative URL per work. For paywalled essentials (Godfrey-Smith's Other Minds; Hanlon and Messenger's Cephalopod Behaviour), note the paywall and name the authoritative edition.

- FIELD GUIDES AND REFERENCE WORKS — where available. For Octopus: Jereb et al. FAO Cephalopods of the World (open access); Hanlon & Messenger Cephalopod Behaviour (Cambridge). For other organisms: equivalent authoritative references.

- ACTIVE RESEARCH GROUPS — laboratories producing current work. For Octopus: Hochner (Hebrew University), Hanlon (Woods Hole / MBL), Godfrey-Smith (Sydney), Ragsdale (Chicago). For each: institution, URL, lead investigator, one-sentence focus. Anchors for Pass 1-merge cross-reference.

- WHAT IS NOT AVAILABLE IN ENGLISH SCIENTIFIC LITERATURE — gaps where non-English or non-academic sources would add material. Flag honestly.

- POPULAR-SCIENCE SOURCES DISTINGUISHED FROM PEER-REVIEWED — where popular works (Montgomery's Soul of an Octopus; Godfrey-Smith's Other Minds, which straddles) have shaped public understanding. Name them; classify clearly so downstream passes do not treat popular synthesis as primary research.
{% endif %}

---

CROSS-DISCIPLINARY ADDITIONS (from Gemini broad scan — consult for any section):

{{ gemini_findings }}

{% if not perplexity_sections and perplexity_findings %}
---

FALLBACK: Perplexity output could not be split by section. Full output:

{{ perplexity_findings }}
{% endif %}

Cite all claims from peer-reviewed scientific literature{% if subtype == "system" %}, primary legal documents, and community-authorised Indigenous-studies scholarship{% endif %} where possible. For each major claim, note whether it represents scholarly consensus or a contested interpretation.

{% elif type == "fictional" %}
Research {{ display_name_with_hint }} comprehensively for the purpose of building an AI persona based on this fictional, literary, or mythological character. Organize findings under these headings:

RESEARCH INTEGRITY (applies to every section below)

- For a fictional character, evidence lives in the TEXT and in SCHOLARLY RECEPTION — never in imagined biography. The character has no life outside the text; do not invent one. Any claim about the character must be anchored in a specific passage, a scholarly reading with citation, or a documented narrative function.

- Tag each attribution explicitly per Card v2 conventions:
    [stated in text] = the character says it or the narrator states it at a specific textual location (cite night-number / act.scene / book.chapter)
    [scholarly consensus] = the reading is agreed across major scholarly traditions (cite the scholars)
    [scholarly reading of {scholar}] = a specific scholar's reading, not consensus
    [attributed by narrative function] = the commitment or capability is implied by what the text has the character do / embody / make possible
    [textual-variant dependent] = the attribution depends on which manuscript family or translation tradition is used (name which)
    [inference — from textual + scholarly evidence] = inference, explicitly marked

- Do not resolve genuine scholarly debates into false consensus. Name contested readings, identify the scholars, explain why the disagreement matters for voice construction.

- Where the textual or scholarly record is thin, say so. "The text gives us X but not Y" is more valuable than fabricated Y.

- Flag translation choices explicitly. A fictional voice's voice is mediated by its translation tradition — Burton's Scheherazade sounds different from Haddawy's sounds different from Galland's. Name the tradition you draw on; name what the choice rules out.

- Anti-patterns, banned-language, and character-breaking failure modes are partially populated from your dossier (scholarly evidence of what the character's narrative tradition documentedly avoids) and partially populated downstream (Pass 7c observes AI-default failure modes). Your job is the documented half.

- This dossier will feed an AI persona that will reason as this character on novel questions. Every claim you produce may end up load-bearing. Honesty is load-bearing.

NARRATIVE-FUNCTION FRAMING

This voice is a FICTIONAL / LITERARY / MYTHOLOGICAL CHARACTER. The character's existence IS the text that contains them. There is no biography outside the text, no private beliefs not attributed by narrative function, no primary corpus in the character's own voice that is not authored by someone else. Throughout this dossier:

- The character's "world" is the textual world (what the narrative treats as real — magic, jinn, gods, fantastical geography, historical-imaginary settings).

- The character's "wound" is the narrative premise (the structural situation the text sets up — not biographical trauma).

- The character's "knowledge boundary" is ontological (what the text contains vs what it does not) rather than historical-period (though the two may overlap when the text is set in a specific period).

- The character's "corpus" is (a) the source text(s) themselves and (b) the scholarly reception tradition that has read them. Voice research will ground in both.

- Do not attribute biographical details (childhood, private relationships, unspoken thoughts) that the text does not give. If the text is silent, the character is silent on that.

---

## Section 1: TEXTUAL FOUNDATION

What this section feeds downstream:
  - world (the narrative world — its ontology, key dates internal to the narrative, textual variants, compositional history)
  - formative_experience (the narrative premise that organises the character's engagement — e.g., for Scheherazade: Shahryar's compulsion and the nightly executions)
  - character (how described in text; role; key scenes and speeches; scholarly characterisation)
  - topics_requiring_care (partial — variant traditions that produce different characterisations)

Starting material from Perplexity's §1:
{% if perplexity_sections %}
{{ perplexity_sections.get(1, "(Perplexity §1 not recognized; see full Perplexity block below)") }}
{% else %}
(Perplexity findings available as unstructured block below)
{% endif %}

Your task for Section 1:

- THE SOURCE TEXT(S) — name every text in which this character appears. For each: title in original language and English; approximate date of composition or earliest manuscript; language; genre; authorship (known, anonymous, composite). For composite traditions (like Alf Laylah wa-Laylah / The Thousand and One Nights, or the Homeric epics), name the major manuscript families and their significant differences, citing scholarship.

- TEXTUAL HISTORY AND VARIANTS — how the text(s) reached their current form. For characters whose tradition spans centuries, variants across time matter — stories added later (like the Galland "Aladdin" and "Ali Baba" with no known Arabic manuscript predecessor) may or may not count as part of the tradition; surface the scholarly choice. Do not flatten variant landscapes.

- THE CHARACTER'S NARRATIVE ROLE — protagonist, narrator, frame-device, interlocutor, embedded character within a tale-within-a-tale, chorus. For Scheherazade: frame-narrator whose telling IS the frame within which the rest unfolds. This narrative position is load-bearing: her character IS her role as frame-teller.

- KEY SCENES, SPEECHES, AND ACTIONS — each with reference to textual location in standard scholarly editions (night-number for 1001 Nights; book.chapter for novels; act.scene.line for plays). Include variants where the scene differs substantially across manuscript families or translations.

- DIRECT SELF-DESCRIPTION WITHIN THE TEXT — any moment where the character describes themselves, states their own motivations or beliefs, or reflects on their own role. Cite the specific passages. (For Scheherazade: her volunteer-of-self at the opening; "either I succeed in delivering the people from this slaughter, or I perish" — cite the edition and night-number.)

- DESCRIPTION OF THIS CHARACTER BY OTHERS IN THE TEXT — what the narrator, other characters, the implied author say about them. This attributed characterisation often differs from and competes with the character's self-statements.

- COMPOSITIONAL AND HISTORICAL CONTEXT — the world in which the text was composed and circulated, NOT biography of the character. For 1001 Nights: Abbasid + Mamluk + Ottoman circulation history; oral-storytelling contexts; European reception through Galland; the orientalist reception history. Cite Robert Irwin's Arabian Nights: A Companion, Muhsin Mahdi, Ulrich Marzolph, Dwight Reynolds, Husain Haddawy.

- THE ONE FORMATIVE NARRATIVE PREMISE — the structural situation that organises the character's engagement with the world. NOT biographical trauma; narrative premise. For Scheherazade: Shahryar's compulsion, the nightly executions, the sisters' peril, the choice to volunteer. Where the text supports competing framings, name each candidate with its textual + scholarly support; Pass 2 commits.

- THE SWAP TEST FOR SECTION 1 — if the account of this character's textual foundation could fit another figure from the same genre or tradition (Penelope; Ariadne; any "clever woman" archetype), drive to specifics. Scheherazade is not a generic clever woman — her specifics are the frame-narrator structure of 1001 Nights, the sister-apparatus (Dunyazad), her stated purpose, her characteristic mid-tale dawn-break.

---

## Section 2: CHARACTER AS INTELLECTUAL CONSTRUCT

What this section feeds downstream:
  - constitution — 10-20 commitments attributed to the character, tagged per Card v2 (including [attributed by narrative function])
  - concept_lexicon — concepts defined by the narrative tradition itself (frame tale, dawn-break, embedded narrator)
  - epistemic_frame_statement — the specific scholars and translation traditions whose reading informs the construction
  - bold_engagement_topics — derived from the character's narrative function and most contested scholarly meanings

Starting material from Perplexity's §2:
{% if perplexity_sections %}
{{ perplexity_sections.get(2, "(Perplexity §2 not recognized; see full Perplexity block below)") }}
{% else %}
(Perplexity findings available as unstructured block below)
{% endif %}

Your task for Section 2:

- COMMITMENTS ATTRIBUTED BY NARRATIVE FUNCTION — 10-20 commitments the character embodies. For each: (a) a one-sentence statement of the commitment; (b) evidence tag per Card v2 conventions — [stated in text] / [scholarly consensus] / [scholarly reading of X] / [attributed by narrative function] / [textual-variant dependent]; (c) a one-sentence operational note grounded in a specific scene or narrative structure (cite night-number, act.scene, or equivalent); (d) a brief scholarly citation where applicable. Examples (Scheherazade): "Storytelling suspends violence" [attributed by narrative function — her nightly telling is the deferral-structure of the frame]; "Interrupted narrative is a governance technology" [attributed by narrative function — dawn-break as a structural feature]; "Listening restores the listener" [scholarly consensus — Ghazoul, Malti-Douglas].

- UNIQUE NARRATIVE CONCEPTS — 5-10 concepts defined by the narrative tradition itself. For each: definition from literary scholarship; what the concept rules out (false alternatives from adjacent traditions); textual grounding. For Scheherazade: the frame tale; the tale-within-a-tale; dawn-break; the embedded narrator; the implicit contract between teller and listener. Flag concepts that are UNIQUE to this character's tradition vs shared with the tradition at large.

- INTERNAL TENSIONS DOCUMENTED BY SCHOLARSHIP — at least 2, where the scholarly record supports them. For Scheherazade: proto-feminist subversive vs exemplar of submission to patriarchal violence; the frame as liberation vs containment; storytelling as resistance vs complicity. Cite Fedwa Malti-Douglas, Ferial Ghazoul, Suzanne Gauch, Robert Irwin, Ulrich Marzolph whose readings contest each other. Do not resolve; name the tension. If the record supports fewer than 2, say so.

- DOMINANT VS MINORITY SCHOLARLY READINGS — 2-5 minority readings contesting consensus, each with scholar and key publication. (Scheherazade as narrative trickster; as didactic heroine; as cipher for the compiler's authorial self-awareness; orientalist-critical vs literary-historicist readings — cite Said and Kabbani on the critical side; Irwin and Marzolph on the historicist side.)

- THE CHARACTER'S NARRATIVE FUNCTION — what question or problem does this character embody? For Scheherazade: can language defer violence? can listening transform the listener? what is the ethics of the storyteller who must continue? Cite the scholarly literature that articulates the function.

- UNRESOLVED PROBLEMS WITHIN THE NARRATIVE — questions the text itself leaves unresolved. What happens to Dunyazad; whether Shahryar's transformation is genuine or a narrative convenience; the relationship between the tales told and the teller's survival strategy. Feeds topics_requiring_care at extraction.

- VARIANTS THAT CHANGE THE CHARACTER — where different manuscript families or translations produce substantively different readings. Mahdi's Syrian ZER vs later Egyptian expansions; Galland's Aladdin/Ali Baba additions; Burton's Victorian-orientalist overlay; Haddawy's restraint. Flag how the variant choice affects which commitments are attributable. This is load-bearing for voice construction.

---

## Section 3: NARRATIVE STRATEGY

What this section feeds downstream:
  - reasoning_method — how this character characteristically acts and engages within the text; 5-8 narrative moves with worked demonstrations
  - finds_compelling / resists — narrative textures that activate the character / trigger non-engagement
  - disagreement_protocol — HOW this character resists (silence, new tale, refusal — not counter-argument)
  - translation_protocol — how this character encounters and reframes the unfamiliar within their narrative world
  - default_questions — the interrogatives the character's narrative position habitually brings

Starting material from Perplexity's §3:
{% if perplexity_sections %}
{{ perplexity_sections.get(3, "(Perplexity §3 not recognized; see full Perplexity block below)") }}
{% else %}
(Perplexity findings available as unstructured block below)
{% endif %}

Your task for Section 3:

- HOW THIS CHARACTER CHARACTERISTICALLY ACTS WITHIN THE TEXT — the narrative moves this character makes repeatedly, grounded in textual location and scholarly reading, not speculation. For Scheherazade: tales-within-tales; the cliffhanger suspension; the embedded moral; indirect instruction through analogous story; nested narration that shifts frames mid-telling. Each move documented with at least one specific narrative location and a scholarly citation.

- NAMED NARRATIVE MOVES — 3 to 5 specific, NAMED patterns documented in scholarship as distinctive to THIS character. For each: a name (the scholars' name if one exists, else descriptive phrase); a one-sentence description; one textual example with night-number or equivalent reference. NOT generic style descriptors — specific, nameable, describable moves. If fewer than 3 named moves exist in the scholarship, produce what exists and say so.

- WHAT THIS CHARACTER NOTICES, VALUES, RESPONDS TO — the textures within the text that trigger their engagement. For Scheherazade: parallels between provocation and stored tale; narrative analogies; interruption-points; moments where a listener's silence or interruption reveals something about the listener. Cite specific scenes.

- WHAT THIS CHARACTER IGNORES, DISMISSES, OR REFUSES — the textures the text shows the character declining to engage. For Scheherazade: direct confrontation of Shahryar's violence; pleading from personal peril; plain declarative argument. The character's characteristic non-engagement is load-bearing for banned_modes at extraction.

- HOW THIS CHARACTER HANDLES DISAGREEMENT — within the text, what does the character do when someone's framing is wrong? For Scheherazade: she tells a different tale. The counter-story, not the counter-argument. This directly feeds disagreement_protocol per Card v2.

- HOW THIS CHARACTER HANDLES THE UNFAMILIAR — within the text, how does the character incorporate unfamiliar material into the character's characteristic mode? For Scheherazade: she has a tale for every situation; unfamiliar material becomes a tale-premise. Feeds translation_protocol.

- WORKED DEMONSTRATIONS — 1 to 3 worked narrative-moves across different parts of the text, selected to cover the character's range. For each: a specific narrative situation from the text; the move the character makes; the effect it has; the scholarly reading of the move. Cite the textual location and the scholars.

- WHAT HAPPENS WHEN THE NARRATIVE STRATEGY FAILS — moments where the character's approach falters or is tested. Rare by design in some tales (1001 Nights is structured around Scheherazade's non-failure); where failures occur, note the scholarly reading.

- DEFAULT QUESTIONS THE CHARACTER BRINGS — the interrogatives this character's narrative position habitually poses to whatever material appears. For Scheherazade: What tale does this resemble? What is the structure of the provocation? Where is the dawn-break in this situation? What does interruption make visible?

---

## Section 4: VOICE AND STYLE

What this section feeds downstream:
  - rhetorical_mode — fundamental mode of expression in 1-2 sentences
  - characteristic_moves — 3-5 named expression patterns (distinct from Section 3's narrative moves)
  - register_and_tone — what the voice IS and what it is NOT, across major translation traditions
  - metaphorical_repertoire — recurring imagery and sensory fields in the text
  - preferred_vocabulary — the words this voice thinks in (and which translation rendering they are in)
  - banned_language / banned_modes — what this voice would never say or do
  - medium, characteristic_output_structure — the form and arc of this character's typical expression

Starting material from Perplexity's §4:
{% if perplexity_sections %}
{{ perplexity_sections.get(4, "(Perplexity §4 not recognized; see full Perplexity block below)") }}
{% else %}
(Perplexity findings available as unstructured block below)
{% endif %}

Section 4 is the hardest section for a fictional character because the character's "voice" is the text-as-rendered-in-a-translation-tradition, not the character's own writing. Ground every voice observation in specific textual passages AND name the translation tradition that produced the observation. Haddawy's Scheherazade sounds different from Burton's Scheherazade sounds different from Galland's. The translation choice is part of the voice characterisation — not incidental.

Avoid "reputation-level" generic-Arabian-Nights or generic-epic-register tonality. Wikipedia-level voice descriptions are a documented failure mode (the Khanmigo incident, Washington Post 2024).

THE SWAP TEST for Section 4: if your characterisation of this voice could apply to another character in the same translation tradition (a generic "storyteller in the ornate Victorian-translation register"; a generic "Homeric hero as rendered by Lattimore"), it is too generic. Drive to what ONLY this character, in THIS textual instance, does.

Your task for Section 4:

- RHETORICAL MODE OF THE TEXTUAL TRADITION — 1 to 2 sentences characterising this voice's fundamental mode of expression as rendered in its primary translation tradition. Cite the specific translator (for Scheherazade: Mahdi / Haddawy; Burton; Galland; Lyons) and the scholarly reading. Not a single adjective — a specific characterisation grounded in analysis.

- CHARACTERISTIC EXPRESSION MOVES — 3 to 5 specific, NAMED patterns distinctive to this character's voice within its text. Distinct from Section 3's narrative moves — these are patterns of EXPRESSION (how the voice sounds) rather than patterns of NARRATION (how the character acts). For each: name; one-sentence description; one textual example with night-number or equivalent. If fewer than 3 exist in the scholarship, produce what exists and say so.

- REGISTER AND TONE — what the voice IS and is NOT, per scholarly and critical characterisation. Flag how this shifts across translation traditions. For Scheherazade in Haddawy: measured, patient, almost pedagogical, never showing fear. In Burton: orientalist-florid, exoticised. This translation-shift is itself a scholarly issue — name it.

- METAPHORICAL REPERTOIRE — the recurring images, analogies, and sensory fields this character draws on within the text. For Scheherazade: travel, transformation, disguise, market, garden, palace, desert, jewel, ring, unsealed door. Cite scholarship that has catalogued the imagery.

- PREFERRED VOCABULARY AND SYNTACTIC PATTERNS — the words this voice reaches for AND the characteristic narrative-syntax. For Scheherazade: nested clauses; the formulaic "it is said that"; named-night delineations ("when it was the X night, Shahrazad said..."); invocations; the ring-composition of embedded tales. Cite the literary scholarship.

- CHARACTERISTIC OPENINGS, TRANSITIONS, CLOSINGS — structural patterns in how this character's tales or speeches begin, pivot, and end. For Scheherazade: the invocation; the mid-tale dawn-break; the next-night re-opening with a brief recap-phrase. Cite specific night-numbers.

- DOCUMENTED ANTI-PATTERNS — what the text-tradition and scholarship identify as modes this voice AVOIDS. Two kinds of evidence count:
    (a) Explicit non-use in the text — structures the text never has this character employ (direct confrontation; first-person editorial intrusion into the frame; moralising without story; plain statement where the moment calls for narrative).
    (b) Scholarly characterisation by contrast — where scholars note what this character "doesn't do" in contrast with other characters in the same tradition (Scheherazade does not argue like Shahryar's vizier; does not beg like the first nights' condemned brides).
  3 to 5 items with textual or scholarly citation.

  NOTE: identifying AI-default failure modes (where the persona running at runtime sounds like generic AI rather than this character) is NOT part of your job. That happens downstream in Pass 7c. Your job is scholarly / textual anti-patterns, not AI-failure-mode prediction.

- TRANSLATION CHOICE AND ITS IMPLICATIONS — state which translation tradition(s) should ground the voice construction, and why. For Scheherazade: Mahdi's critical Arabic edition (Leiden 1984) in Haddawy's English translation is scholarly consensus for "earliest documented" voice; Burton is widely read but unreliable and Victorian-overlaid; Galland is historically load-bearing but heavily adapted. Name the authoritative choice and flag what it rules out. Pass 1c fetches the text Pass 4a will use; your job here is the choice.

- EMOTIONAL AND AESTHETIC REGISTER — the overall feel of reading this character in the authoritative translation, described as a reader experience rather than technical analysis. Cite the critics who characterise the reading experience this way.

---

## Section 5: ONTOLOGICAL BOUNDARIES

What this section feeds downstream:
  - knowledge_boundary — what exists and does not exist in the character's narrative world (ontological boundary, not historical-period boundary though the two may overlap)
  - topics_requiring_care — the character's narrative-world material that conflicts with modern sensibilities; contested scholarly readings of that material
  - hard_limits — what the character's narrative world excludes absolutely (anachronism, genre violations, character-breaking moves)

Starting material from Perplexity's §5:
{% if perplexity_sections %}
{{ perplexity_sections.get(5, "(Perplexity §5 not recognized; see full Perplexity block below)") }}
{% else %}
(Perplexity findings available as unstructured block below)
{% endif %}

Your task for Section 5:

- WHAT EXISTS WITHIN THIS CHARACTER'S WORLD — the ontology of the text. For Scheherazade: jinn, ifrits, magical objects, shape-shifters, enchanted cities, rocs, hidden valleys, viziers, sultans, merchants, slave-markets, sea voyages, talismans, magic lamps and rings (where variant tradition includes them). Each with textual location. This defines what this voice can invoke as "real" within its own frame.

- WHAT DOES NOT EXIST WITHIN THIS CHARACTER'S WORLD — what the ontology excludes. For Scheherazade: modern technology, post-medieval political forms, secular-modern empirical science, post-classical Arabic linguistic registers, the print book as object, authorship-as-property, the novel as genre. Cite scholarship that has theorised the text's ontological horizon (Irwin, Marzolph, Reynolds).

- THIS CHARACTER'S RELATIONSHIP TO HISTORICAL REALITY — is the narrative set in a real period, entirely fantastical, hybrid? For Scheherazade: a medieval-Islamic imaginary that is neither historical Abbasid Baghdad nor pure fantasy — setting is referential but imaginative. Cite the scholarship.

- KEY SCHOLARLY DEBATES ABOUT HISTORICAL-FICTIONAL RELATIONSHIP — where scholars have debated how much the text reflects historical reality vs imaginative composition. For 1001 Nights: the orientalism debates (Edward Said, Rana Kabbani); the manuscript-genealogy debates (Mahdi, Marzolph); the question of "how Arab" the Arabian Nights actually is (Irwin). Surface each side with citation.

- SENSITIVE TOPICS WITH NAVIGATION GUIDANCE — topics where this character's narrative world includes material that conflicts with modern sensibilities. For each (5 to 10 items):
    * What the text contains, with location
    * The scholarship that has analysed this material
    * How a persona of this character should engage today: not avoidance, not modernisation, not defence — navigation through the narrative's own terms
  Example (Scheherazade): slavery within the tales — acknowledge the narrative's social world; do not export its categories to modern labour; do not defend; cite Malti-Douglas, Gauch on the scholarly engagement with gendered and enslaved figures.

- DOCUMENTED CHARACTER-BREAKING MOVES — moves antithetical to this character's mode as documented by scholarship. 3 to 5 items. For Scheherazade: abandoning the frame-narrator role for direct first-person editorial; completing the tale rather than breaking at dawn; shifting from tale to argument; sentimentalising Shahryar's transformation without the narrative's ambiguity. Cite scholars.

  NOTE: Like Section 4's anti-patterns, AI-default failure-mode anticipation is Pass 7c territory, not your job.

- RETROSPECTIVE-FRAMING TRAPS — descriptions of this character that a modern reader would instinctively reach for but that the text and its tradition would reject. 3 to 5 items. For Scheherazade: calling her a "proto-feminist" in the modern sense (the category is anachronistic even when functional-feminist readings are scholarly-supported); calling 1001 Nights a "novel"; calling her storytelling "therapy" in the modern psychoanalytic sense; calling the frame "metafiction" in the post-Borgesian sense.

---

## Section 6: RECEPTION AND INFLUENCE

What this section feeds downstream:
  - curated_corpus_passages — the source text in authoritative edition + scholarly reception (Pass 1c fetches from your URLs)
  - preferred_vocabulary, metaphorical_repertoire — textured content extracted from primary text and scholarship
  - bold_engagement_topics — how the character's meaning is contested across cultures and periods
  - epistemic_frame_statement — which scholarly / readerly tradition shapes this construction
  - length_and_format_constraints — reception patterns and the tradition's typical output arc

Starting material from Perplexity's §6:
{% if perplexity_sections %}
{{ perplexity_sections.get(6, "(Perplexity §6 not recognized; see full Perplexity block below)") }}
{% else %}
(Perplexity findings available as unstructured block below)
{% endif %}

Section 6 is the corpus gateway. For a fictional character, the corpus is (a) the source text in an authoritative edition and (b) the scholarly reception that has shaped how the character has been read. Pass 1c fetches primary text from the URLs you identify; Pass 1d curates characteristic passages; Pass 4a researches voice directly from the text (in the translation you specify) and from selected scholarly readings. The quality of this section determines the quality ceiling of every voice-level field.

Be specific throughout: work titles, canonical references (night-number / act.scene / book.chapter), translation + edition, URLs.

Your task for Section 6:

- THE SOURCE TEXT IN AUTHORITATIVE EDITION — name the specific editorial-scholarly edition. For Scheherazade: Muhsin Mahdi's Alf Layla wa-Layla (Leiden: Brill, 1984 — critical edition of the Syrian ZER branch) as authoritative pre-modern Arabic; Husain Haddawy's translation based on Mahdi (Norton, 1990) as authoritative English. Each with full bibliographic reference.

- MAJOR TRANSLATION TRADITIONS AND THEIR IMPLICATIONS — list each major translation with: date, language, source-manuscript basis, translator, scholarly assessment of what the translation does to the character. For 1001 Nights: Galland (1704–17, French, Syrian manuscript + Hanna Diyab the Maronite storyteller + Galland's own additions); Lane (1840, English, bowdlerised); Burton (1885, English, heavily Victorian-orientalist); Mahdi-Haddawy (1984/1990); Lyons (2008, Penguin, full); Pasolini's film-adaptation as its own interpretive tradition. For each: what shifts.

- CHARACTERISTIC PASSAGES — 8 to 15 passages across the authoritative text AND scholarly reception. For each:
    * Canonical reference (night-number for 1001 Nights; equivalent for other texts)
    * Primary purpose: "substance" (the narrative / argumentative content), "voice" (how the character sounds in this translation), or "both"
    * Tier: Tier 1 (source text in authoritative edition) / Tier 2 (peer-reviewed scholarship) / Tier 3 (contested reception, reception-as-cultural-object)
    * Approximate word count
    * Brief context — why this passage matters for voice construction

  Do NOT include full passage text in THIS dossier. Pass 1c fetches. Your job is to produce the citations.

- DIGITISED FULL-TEXT URLS — for open-digital editions. For 1001 Nights: Burton's 1885 edition is public-domain on Project Gutenberg but unreliable for voice; Mahdi's Arabic is paywalled / library-only; Haddawy is in copyright but widely available through libraries. Flag paywall / restriction honestly; name the authoritative edition even when no free version exists.

- KEY ADAPTATIONS ACROSS CULTURES AND PERIODS — literary, musical, visual, cinematic. For Scheherazade: Rimsky-Korsakov's Scheherazade (1888, orchestral suite); Borges's metafictional reception; Naguib Mahfouz's Arabian Nights and Days; Salman Rushdie's Haroun and the Sea of Stories; Angela Carter's reworkings; Pasolini's Il Fiore delle Mille e Una Notte (1974). Each with date + brief note on the reading it produces.

- CONTESTED READINGS — where scholars fundamentally disagree about what this character means. Feminist readings (Malti-Douglas, Gauch) vs critiques of feminist readings; orientalist-critical (Said, Kabbani) vs literary-historicist pushback (Irwin, Marzolph); subversive-Scheherazade vs submissive-Scheherazade; cultural-appropriation debates around the Nights as a "Western object of reception".

- SIGNIFICANCE FOR THE ASSEMBLY'S THEMES — how this character's narrative reception speaks to questions of governance, representation, who belongs in the demos, and the relationship between voice and power. Cite scholarship that reads this character in governance or political-theory terms.

- SCHOLARSHIP TO PRIORITISE — the peer-reviewed literary-studies and cultural-studies scholarship. For 1001 Nights: Robert Irwin (The Arabian Nights: A Companion, Tauris); Muhsin Mahdi (the critical edition + introduction); Fedwa Malti-Douglas (Woman's Body, Woman's Word); Ferial Ghazoul (Nocturnal Poetics); Ulrich Marzolph (The Arabian Nights Encyclopedia, with Richard van Leeuwen); Dwight Reynolds; Suzanne Gauch. Each with at least one key publication.

- CONTESTED ATTRIBUTIONS AND ORPHAN STORIES — tales later added to the Nights tradition whose attribution to the "original" corpus is disputed. "Aladdin", "Ali Baba", "Sinbad" — flag the scholarly consensus on each. This matters because voice construction should know whether a beloved tale is actually in the authoritative corpus.

---

CROSS-DISCIPLINARY ADDITIONS (from Gemini broad scan — consult for any section):

{{ gemini_findings }}

{% if not perplexity_sections and perplexity_findings %}
---

FALLBACK: Perplexity output could not be split by section. Full output:

{{ perplexity_findings }}
{% endif %}

Cite all claims. Prioritise literary scholarship (peer-reviewed criticism, major companions and handbooks) and the authoritative critical edition of the source text. For each major interpretation, note whether it represents scholarly consensus or a contested reading.

{% endif %}
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
