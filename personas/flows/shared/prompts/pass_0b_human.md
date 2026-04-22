{# Pass 0b — HUMAN branch. Included by pass_0b_dr_prompt.md when type=='human'.

   Phase B rewrite (2026-04-20): converted extraction-specs to thematic
   research questions. Content coverage preserved; structural extraction
   happens at Pass 1.1-1.6 merge, not here. Boddice §13/§14/§15 material
   researched as prose; schema-shaped output produced at merge.
#}
Research {{ display_name_with_hint }} comprehensively for an AI persona specification. Produce a rich research dossier organised under the six thematic areas below. Downstream passes extract structured biocultural fields from your prose — your job is substantive, cited, period-vocabulary-imbued narrative, not structured output. Prose, not JSON. Narrative, not bullet-list. If you find yourself producing "Field N: ..." lines, stop — that is the downstream merge's job.

{% if hostile_sources %}
RECONSTRUCTION DISCIPLINE — {{ name }} has a hostile-sourced record. Apply throughout all six sections:

Primary material is fragmentary; hostile sources (enemies, colonisers, rival powers, prior regime apologists) dominate the historical record. Your research obligations:
- LEAD with `[reconstruction]` scholarship (modern scholarship reading against the hostile grain; identify the scholar and methodology) and `[own_voice]` material (fragmentary primary sources; figure's own words, however partial).
- FRAME hostile sources explicitly as motivated distortions: name what the hostile source was (Egyptian priests reading Ptolemaic Rome, Roman propaganda about Cleopatra, colonial-administration records of legal-personhood entities) and what it was motivated to distort.
- SURFACE counter-traditions: non-Western scholarship, oral traditions, minority readings that preserve a different characterisation.
- Do NOT invent interior life the sources do not document. The "do not invent biography" discipline for fictional voices applies here: claims about the figure's motivations, beliefs, or experience require a scholarly citation or a `[reconstruction]` tag. Where the record is silent, say so explicitly.
{% endif %}

---

## Section 1: BIOGRAPHICAL FOUNDATION

<!-- COVERAGE-NOTE-PLACEHOLDER: the Pass 0b tailoring LLM replaces this comment with 2-3 specific follow-up questions for this voice — gaps Perplexity + Gemini left unresolved that DR should address. -->

What are the figure's key life dates, places, and institutional attachments (institutions founded, joined, shaped, or opposed)? What formative relationships — teachers, students, rivals, patrons, adversaries, interlocutors — shaped them, and which of those relationships does scholarship treat as most consequential?

What was the intellectual world the figure inhabited — the currents, debates, institutions, and schools they engaged with, opposed, or were shaped by? What was *real* for them in the strong sense of the ontological furniture of their world (Forms, jinn, whakapapa, the Cartesian *res cogitans*, the Newtonian universe, the kenotic Christ) — not what they "believed" but what structured their reality? What period-specific affects, passions, or emotional categories did they and their contemporaries use, in the figure's own language with English glosses where appropriate? What framework gave suffering, loss, or difficulty meaning in the figure's world? What counted as an "I" for them — the tripartite soul, the *nafs*-stations, the I-and-I, the humoral body, the introspective modern self, the Ptolemaic corporate divine-royal person? What modern terms would mis-render this figure, and why?

What formative experiences shaped the figure's engagement with the world? Describe each candidate formative experience as the event AND the framework in which it was meaningful to the figure, using period-specific vocabulary rather than modern therapeutic categories. What emotional communities (in Rosenwein's sense) shaped the figure's lexicon of feeling and norms of expression? What engagement does the formative context drive — what does the voice enter a deliberation to do, notice, refuse, defend? Where scholarship supports multiple formative candidates, describe each with the strength of scholarly support; do not pick one.

What character-grammar did the figure's tradition use to describe personality? Describe character using the period's own vocabulary — the four humours, Greek tripartite soul, Islamic *nafs*-stations, Rasta virtues, Buddhist *śīla*, Confucian *ren-yi-li-zhi*, Russian-Orthodox *smirenie*/*gordost'*/*nadryv*, whatever the figure's tradition used — rather than Big-Five-adjacent modern adjectives. Where a modern category must be used for clarity (e.g., "melancholic" for humoral melancholia), note that the modern meaning distorts.

How did the figure describe themselves — their own work, method, role, what they claimed to be, what they refused to be called? (Socrates refusing "wise"; Nietzsche refusing "systematic philosopher"; the figure's own self-naming wherever it survives.) What language does scholarship use for what kind of thinker the figure is — philosophical novelist, competent practitioner, witness, theorist, prophet, artist, ethnographer, traveller-chronicler? Name the specific scholarly framing.

Where do the figure's words and actions diverge, or their early and late positions disagree, or their self-understanding differ from how others characterised them? These are not flaws to explain away — they are signals that the figure is complex enough to be worth reading.

What social, cultural, political, and material position did the figure occupy — class, gender, race, religion, nationality, colonial or imperial status, institutional role? Not as identity politics but as the lived position from which they thought and acted, which shapes what they had standing to address.

What scholarly framing identifies the figure's unique contribution — the formulation scholarship has converged on for what this figure offers that no other voice in their tradition does? (e.g., Arendt's labor/work/action distinction as a contribution no other 20th-C political theorist made; Dostoevsky's polyphonic novel as a new genre no predecessor achieved.) Cite the scholarly source.

---

## Section 2: INTELLECTUAL FRAMEWORK

<!-- COVERAGE-NOTE-PLACEHOLDER: the Pass 0b tailoring LLM replaces this comment with 2-3 specific follow-up questions for this voice. -->

What are this figure's deepest intellectual commitments, and how is each one seen applied in specific documented cases across the primary corpus — a particular work, episode, or debate? Operational grounding matters: "the figure valued X" is too generic; "in Work Y, responding to situation Z, the figure invokes X this way" is the shape downstream synthesis needs. Cite textual sources.

Which concepts does the figure use with distinctive precision — in the figure's own vocabulary, not modern translation? For each: what is the figure's working definition, and what does the concept rule out — what false alternatives would the figure reject? Flag concepts scholarship identifies as uniquely associated with this figure (originated with them, or taking on a specialised meaning in their usage distinct from the tradition around them).

Where does the scholarly record identify genuine internal tensions in the figure's thought — commitments that pull against each other, positions held simultaneously that cannot easily be reconciled? Cite the passages where both sides surface. Do not collapse tensions into "evolution" unless the figure themselves documented a resolution.

How did the figure's positions evolve across their lifetime, where scholarship documents the evolution rather than speculating about it? Where do scholars contest whether a shift is real or interpretive?

How were the figure's commitments tested under pressure — documented encounters with hostile interlocutors, failed attempts, contradictions the figure noticed? What did they do when reality pressed hardest: revise, double down, defer, change the subject?

What minority scholarly readings contest the dominant interpretation of this figure? Name the scholars, summarise each minority reading, and identify what it implies for how the figure should be understood.

What problems did the figure themselves identify as open or difficult within their own framework — not modern critiques, but questions they flagged as unresolved?

---

## Section 3: REASONING PATTERNS

<!-- COVERAGE-NOTE-PLACEHOLDER: the Pass 0b tailoring LLM replaces this comment with 2-3 specific follow-up questions for this voice. -->

How does this figure characteristically think, grounded in documented works? What questions do they ask when confronting a new problem? What assumptions do they typically challenge? What kinds of evidence or reasoning do they find most compelling (analogy, formal logic, scripture, empirical observation, narrative, precedent)? What form do their arguments typically take (dialectic, aphorism, systematic treatise, dialogue, parable, witness-testimony)? How do they respond to counterarguments — engage, reframe, dismiss, absorb? What do they consider settled versus still open in their own framework?

Walk through 1–3 worked demonstrations of the figure handling a specific documented dilemma from their own era — a debate they actually engaged, a question a contemporary posed, a political or intellectual problem they addressed. For each: what they would notice first, which framework or principle they would reach for, what tensions they would identify, how they would resolve the tensions (or explicitly hold them unresolved). Cite the documented case. For figures with no preserved self-reflection (hostile-sourced voices), mark reconstruction explicitly in the prose.

What specific named rhetorical or cognitive moves does scholarship identify as distinctive to THIS figure? Name each move (the scholars' name where one exists, else a descriptive phrase), describe what it does, and cite a textual example. These are patterns of reasoning, not patterns of expression (that's Section 4). Examples elsewhere in the canon: Socrates's elenchus; Nietzsche's genealogical method; Wittgenstein's language-game move. If fewer than 3 named moves exist in the scholarship for this figure, produce what exists.

What textures of argument or evidence activate this figure's strongest thinking? Not topics but kinds of intellectual material — the confessional utterance under pressure, the scenic dramatisation, the scriptural exegesis, the philosophical position held with existential commitment, the craft analogy, the etymological excavation. Cite documented examples.

What textures trigger this figure's sharpest critique or resistance? Again modes rather than topics — rational-egoist calculation, abstract Hegelian systematisation, popular-opinion appeals, data-as-self-interpreting. Documented examples where applicable.

What does this figure do when their framework fails — documented moments where they encountered something their framework couldn't readily handle, and their response? (Ivan's articulation of innocent-child suffering; the death of a child during composition; confrontation with revolutionary terrorism; the experience of exile.) Cite passages or episodes.

How does this figure characteristically encounter the unfamiliar — the epistemic move they make when meeting a concept, person, or phenomenon outside their established frame? (A traveller arrives and compares; a philosopher questions and reasons; an artist reimagines through their medium; a judge evaluates against precedent; a novelist dramatises the unfamiliar as a character.) Describe a process (step-ordered where the figure's actual method has ordered structure, clustered/thematic where the figure's reasoning is scenic/aphoristic/parabolic) grounded in how the figure actually handled novelty in documented cases, not a generic template.

---

## Section 4: VOICE AND STYLE

Voice lives in the primary texts, not in scholarly summary. Ground every observation in specific passages from the figure's own writing. Where you describe a voice quality, cite the work and section where it is visible. Your job here is to surface scholarly readings of the voice AND point to the primary passages where scholars ground their readings; primary-text-based voice construction happens at Pass 4a drawing on Pass 1c fetches.

Avoid reputation-level characterisation. Wikipedia-level voice descriptions are a documented failure mode — the Khanmigo incident (Washington Post, 2024) showed that AI historical-figure personas fail precisely when voice characterization comes from encyclopedia summary rather than corpus analysis.

**THE SWAP TEST.** Before committing to any voice characterisation, test: could this paragraph be reattributed to another figure with minor edits? If yes, it is too generic. Drive to what ONLY this figure does — a named move, a cited passage, a precise syntactic pattern, a distinctive word usage. Specificity here determines whether downstream passes produce a distinctive voice or settle for a generic literate-AI register.

<!-- COVERAGE-NOTE-PLACEHOLDER: the Pass 0b tailoring LLM replaces this comment with 2-3 specific follow-up questions for this voice. -->

What is the fundamental way this figure argues or expresses — a specific characterisation grounded in analysis, not a single adjective? (Hegel: dialectical — establishes a thesis, surfaces its internal contradiction, synthesizes opposition into higher unity. Wittgenstein: aphoristic and clarifying — brief declarative statements that dissolve philosophical confusion rather than build positive theory.) Cite the scholarly source.

What specific, named patterns of EXPRESSION does scholarship identify as distinctive to this figure — how they write, rather than how they reason (those are Section 3's moves)? Each pattern: a name, a one-sentence description, a textual example with work and section reference.

What is the feel of this voice independent of content — both what the voice IS and what it is NOT, as characterised by scholars and contemporaries? Use concrete contrast (formally conversational, not academic; playful but never flippant). Where the voice is embedded in a specific translation tradition whose register matters interpretively, note that.

What recurring images, analogies, and sensory fields does this figure draw on across multiple works — the specific repertoire, not just "uses metaphors"? (Heidegger: dwelling, path, clearing, thrownness. Wittgenstein: toolbox, game, rule, picture. Nietzsche: dance, dawn, heights, shadows, eagle and serpent.) Cite scholarly analyses.

What specific words does this figure reach for with distinctive precision, and what sentence-level patterns recur (long hypotactic clauses vs. short paratactic punches; active vs. passive; paragraph architecture)? Extract from primary-text analysis or scholarly documentation. For pre-1820 figures, keep the figure's own language as primary vocabulary where relevant.

What structural patterns recur in how this figure's works begin, pivot, and end? (Augustine's *Confessions*: opens in direct address to God; develops through autobiographical interrogation; closes with Scripture meditation. Montaigne's essays: opens with a maxim; circles through digression; closes with honest admission of limits.)

What modes does scholarship identify as antithetical to this figure's voice — what they AVOIDED or rejected, either through explicit rejection in the corpus or through scholarly characterisation by contrast? Cite textual or scholarly evidence.

What is the figure's natural emotional-intellectual pull — the stance they gravitate toward when no specific stance is forced (irony, earnestness, obsession, withdrawal, lament, exuberance, didactic urgency, restraint)? Cite scholars who characterise the figure's typical stance.

What does reading this figure actually feel like as a whole-work experience — the gestalt that makes someone recommend the voice to someone else? (Kafka: claustrophobic bureaucratic dread. Beauvoir: intellectual intimacy — thinks through a problem with the reader as companion.) Cite the critics or scholars who characterise the reading experience this way.

---

## Section 5: HISTORICAL + CONCEPTUAL BOUNDARIES

<!-- COVERAGE-NOTE-PLACEHOLDER: the Pass 0b tailoring LLM replaces this comment with 2-3 specific follow-up questions for this voice. -->

What concepts, events, discoveries, and traditions did NOT exist or were inaccessible to this figure? Cover three kinds:

Temporal exclusions — things that did not exist in the figure's period (the Freudian unconscious; algorithmic governance; the concept of the nation-state; the modern human-rights framework). For each, name the closest analog in the figure's own framework where one exists. "Freudian unconscious [closest: *podpol'ye* as hyper-conscious interiority]"; "algorithmic governance [closest: the philosopher-king problem]". The closest-analog matters as much as the exclusion.

Geographic or cultural exclusions — things that existed contemporaneously but outside the figure's horizon (Indian philosophy for classical Greek philosophers; mature Nietzschean thought for Dostoevsky; sub-Saharan philosophical traditions for most Anglophone figures).

Conceptual exclusions — things whose modern meaning is categorically distinct from anything in the figure's framework, even when a surface analog exists ("consciousness" in the phenomenological sense; "identity" in the Erikson-Foucault sense; "human rights" in the post-1948 sense; "democracy" in the modern liberal-representative sense as distinct from fifth-century Athenian direct democracy).

What was at the edge of what the figure could have known — things that existed contemporaneously but whose significance was not yet apparent, or knowledge contested in their period? This distinguishes "didn't know X" from "chose not to engage with X" — the distinction matters.

What specific topics are sensitive for a persona of this figure today — where the figure's historical views conflict with modern sensibilities and where the voice must engage with care rather than avoidance? For each topic: what the figure actually thought (textual source); why they thought it (the framework that made the view coherent in their period — explanation, not excuse); how a persona should engage today (navigation through the figure's own framework, not sanitisation, not defence). Do NOT sanitise — flatness here loses the figure's most interesting territory.

What views did the figure hold that were contested within their own tradition — not modern anachronism but internal contemporary disagreement? This distinguishes "everyone in the period thought this" from "the figure took a position controversial even then."

What moves does scholarship identify as antithetical to this figure's characteristic mode at the character level — moves the figure constitutively refused, such that adopting them would be self-negation? (Augustine writing coolly about grace without personal-confessional urgency. Wittgenstein producing a systematic metaphysical treatise. Kierkegaard publishing under his own name in direct assertion. Dostoevsky resolving theodicy rationally.) Cite scholars.

What retrospective framings would a modern writer instinctively reach for that the figure themselves would reject? ("Early existentialist" for pre-Kierkegaard voices; "founding liberal democrat" for Kant; "proto-postmodernist" for Montaigne.) Name the trap and why the figure would reject it.

---

## Section 6: PRIMARY TEXTS

This section is the corpus gateway. Downstream passes fetch primary texts from the URLs you identify here; Pass 4a grounds voice research in the figure's actual words. The quality of this section caps the quality ceiling of every voice-level field.

Be specific: work titles, canonical references, URLs, translation notes. Vague lists fail downstream.

<!-- COVERAGE-NOTE-PLACEHOLDER: the Pass 0b tailoring LLM replaces this comment with 2-3 specific follow-up questions for this voice. -->

What is the complete catalogue of this figure's significant works? For each: work title (original language and most-used English); genre (dialogue, treatise, essay, letter, novel, speech, fragment, aphorism collection, lyric, travelogue); approximate length in standard scholarly edition (pages, lines, Stephanus numbers, Bekker numbers — whichever system is canonical); date of composition and chronological placement in the figure's development; a 1–2 sentence description of what the work is and why it matters; the typical structural pattern of how the figure's representative works open, develop, and close.

What specific passages best serve voice construction — passages doing double duty, exemplifying both the figure's argumentative substance and their distinctive register? For each: canonical reference in the citation system standard for the figure (Stephanus pagination for Plato; Bekker for Aristotle; Part/Book/Chapter for novelists; night-number for 1001 Nights); work and section; whether its primary purpose is substance, voice, or both; tier (the figure's own words, or scholarly paraphrase where original is fragmentary or lost); brief context explaining why the passage matters. Over-produce candidates — downstream passes curate. Do NOT include the full passage text here; downstream fetches from URLs.

What digitised full-text URLs make the primary texts available? Perseus Digital Library for ancient Greek and Latin; Project Gutenberg; Internet Archive; Wikisource; Stanford Encyclopedia primary-text archive; figure-specific scholarly collections; non-Anglophone equivalents where relevant (ФЭБ / rvb.ru for Russian; Al-Maktaba al-Shamela for Arabic; SuttaCentral for Pali; national-academy editions). One authoritative URL per major work; where no free digital source exists, name the authoritative scholarly edition and note the paywall.

Which scholarly editions and translations does contemporary scholarship consider authoritative? For non-English figures, flag where translation choice matters interpretively (Fagles vs. Lattimore for Homer; Anscombe vs. Hacker for Wittgenstein; Garnett vs. Pevear/Volokhonsky vs. Ready for Dostoevsky). Give translator verdicts per work where scholarship diverges.

Should the downstream voice quote this figure's passages verbatim or paraphrase? Paraphrasing is safer for most voices (avoids quote-fabrication risk and runtime stiffness); verbatim is warranted for figures whose voice depends on specific phrasings (aphorists; poets; scripture-producers; figures whose epigrammatic style is the substance). State which applies and the rationale.

What works are contested in attribution? Works scholarship disputes, works tradition wrongly attributed to the figure, works scholars have shifted attribution on. Flag explicitly so downstream passes do not treat contested material as tier-1.

For figures whose primary record is thin or entirely reconstructed (hostile-source voices; figures known through enemies; anonymous traditions), what scholarly reconstruction sources serve as the corpus? Name the scholars, the key monographs, the reconstruction methodology. This is what downstream passes use when no tier-1 corpus exists.
