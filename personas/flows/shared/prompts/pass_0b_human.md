{# Pass 0b — HUMAN branch. Included by pass_0b_dr_prompt.md when type=='human'. #}
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

