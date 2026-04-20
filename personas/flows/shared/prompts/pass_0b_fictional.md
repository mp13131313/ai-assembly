{# Pass 0b — FICTIONAL branch. Included by pass_0b_dr_prompt.md when type=='fictional'. #}
Research {{ display_name_with_hint }} comprehensively for the purpose of building an AI persona based on this fictional, literary, or mythological character. Organize findings under these headings:

RESEARCH INTEGRITY (applies to every section below)

- For a fictional character, evidence lives in the TEXT and in SCHOLARLY RECEPTION — never in imagined biography. The character has no life outside the text; do not invent one. Any claim about the character must be anchored in a specific passage, a scholarly reading with citation, or a documented narrative function.

- EVIDENCE TAGGING — every claim carries one of these five core tags. Downstream merge passes parse against this exact list. Do not invent new tag forms.
    [stated] = direct quote or paraphrase from a primary source, with work title + section/page reference.
    [scholarly_consensus] = uncontested modern-scholarly reading. Cite the scholar(s) inline.
    [inference] = contextual inference from biography + period knowledge. Explicitly inferred, not factual.
    [experiential_reconstruction] = claims about what the figure felt / meant / experienced as biocultural reconstruction. Required for any formative-context content (Section 1).
    [projection_warning: <distortion>] = a modern English term used because no better exists. The bracket explains the distortion.

  When the figure has hostile-source coverage, add one of these IN ADDITION to a core tag:
    [hostile_source: <bias>] = claim from enemy / coloniser / rival account.
    [reconstruction: <scholar>] = modern scholarly reconstruction reading against the hostile grain.
    [own_voice] = material in the figure's own voice, however fragmentary.

  Fictional-voice usage notes for the core tags:
    - [stated] = at a specific textual location; cite night-number / act.scene / book.chapter.
    - [scholarly_consensus] vs minority reading by single scholar = use [scholarly_consensus] with scholar named, or [inference] when the reading is contested.
    - [inference] applies to "attributed by narrative function" cases (the commitment is implied by what the text has the character do / embody / make possible) — flag the narrative function in the inference's prose.
    - When attribution depends on manuscript family or translation tradition, note which inline (e.g. "[stated] (Mahdi recension; Burton expands the passage)").

- Do not resolve genuine scholarly debates into false consensus. Name contested readings, identify the scholars, explain why the disagreement matters for voice construction.

- Where the textual or scholarly record is thin, say so. "The text gives us X but not Y" is more valuable than fabricated Y.

- Flag translation choices explicitly. A fictional voice's voice is mediated by its translation tradition — Burton's Scheherazade sounds different from Haddawy's sounds different from Galland's. Name the tradition you draw on; name what the choice rules out.

- Your anti-patterns are scholarly ones — moves the character's narrative tradition documentedly avoids. Cite the textual or scholarly evidence. Not speculation about how an imitation might fail.

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

<!-- COVERAGE-NOTE-PLACEHOLDER: the Pass 0b tailoring LLM replaces this comment with a compact 2-6-sentence coverage note — "Research-to-date (Perplexity + Gemini): ..." + "Go DEEPER on: ..." — so Claude DR knows what's already covered and where to push. -->

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

- UNIQUE CONTRIBUTION — what perspective this character brings that no other panel voice brings. The ONE thing the panel would lose if this character were dropped. (Scheherazade: storytelling-as-survival — the only voice on the panel for whom continuing-to-tell-a-tale IS the political move. Hamlet would be: the inward-paralysis-as-reasoning move, no other panel voice does that.) Feeds unique_contribution at extraction.

---

## Section 2: CHARACTER AS INTELLECTUAL CONSTRUCT

<!-- COVERAGE-NOTE-PLACEHOLDER: the Pass 0b tailoring LLM replaces this comment with a compact 2-6-sentence coverage note — "Research-to-date (Perplexity + Gemini): ..." + "Go DEEPER on: ..." — so Claude DR knows what's already covered and where to push. -->

Your task for Section 2:

- COMMITMENTS — 10-20 commitments the character embodies. For each: (a) a one-sentence statement of the commitment; (b) one of the core evidence tags from the EVIDENCE TAGGING block at top — typically [stated] for explicit textual claims, [inference] for narrative-function attribution (commitments implied by what the text has the character do or embody), [scholarly_consensus] for consensus readings; (c) a one-sentence operational note grounded in a specific scene or narrative structure (cite night-number, act.scene, or equivalent); (d) a brief scholarly citation where applicable. Examples (Scheherazade): "Storytelling suspends violence" [inference — narrative function: her nightly telling is the deferral-structure of the frame]; "Interrupted narrative is a governance technology" [inference — narrative function: dawn-break as a structural feature]; "Listening restores the listener" [scholarly_consensus — Ghazoul, Malti-Douglas].

- UNIQUE NARRATIVE CONCEPTS — 5-10 concepts defined by the narrative tradition itself. For each: definition from literary scholarship; what the concept rules out (false alternatives from adjacent traditions); textual grounding. For Scheherazade: the frame tale; the tale-within-a-tale; dawn-break; the embedded narrator; the implicit contract between teller and listener. Flag concepts that are UNIQUE to this character's tradition vs shared with the tradition at large.

- INTERNAL TENSIONS DOCUMENTED BY SCHOLARSHIP — at least 2, where the scholarly record supports them. For Scheherazade: proto-feminist subversive vs exemplar of submission to patriarchal violence; the frame as liberation vs containment; storytelling as resistance vs complicity. Cite Fedwa Malti-Douglas, Ferial Ghazoul, Suzanne Gauch, Robert Irwin, Ulrich Marzolph whose readings contest each other. Do not resolve; name the tension. If the record supports fewer than 2, say so.

- DOMINANT VS MINORITY SCHOLARLY READINGS — 2-5 minority readings contesting consensus, each with scholar and key publication. (Scheherazade as narrative trickster; as didactic heroine; as cipher for the compiler's authorial self-awareness; orientalist-critical vs literary-historicist readings — cite Said and Kabbani on the critical side; Irwin and Marzolph on the historicist side.)

- THE CHARACTER'S NARRATIVE FUNCTION — what question or problem does this character embody? For Scheherazade: can language defer violence? can listening transform the listener? what is the ethics of the storyteller who must continue? Cite the scholarly literature that articulates the function.

- UNRESOLVED PROBLEMS WITHIN THE NARRATIVE — questions the text itself leaves unresolved. What happens to Dunyazad; whether Shahryar's transformation is genuine or a narrative convenience; the relationship between the tales told and the teller's survival strategy. Feeds topics_requiring_care at extraction.

- VARIANTS THAT CHANGE THE CHARACTER — where different manuscript families or translations produce substantively different readings. Mahdi's Syrian ZER vs later Egyptian expansions; Galland's Aladdin/Ali Baba additions; Burton's Victorian-orientalist overlay; Haddawy's restraint. Flag how the variant choice affects which commitments are attributable. This is load-bearing for voice construction.

---

## Section 3: NARRATIVE STRATEGY

<!-- COVERAGE-NOTE-PLACEHOLDER: the Pass 0b tailoring LLM replaces this comment with a compact 2-6-sentence coverage note — "Research-to-date (Perplexity + Gemini): ..." + "Go DEEPER on: ..." — so Claude DR knows what's already covered and where to push. -->

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

<!-- COVERAGE-NOTE-PLACEHOLDER: the Pass 0b tailoring LLM replaces this comment with a compact 2-6-sentence coverage note — "Research-to-date (Perplexity + Gemini): ..." + "Go DEEPER on: ..." — so Claude DR knows what's already covered and where to push. -->

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


- TRANSLATION CHOICE AND ITS IMPLICATIONS — state which translation tradition(s) should ground the voice construction, and why. For Scheherazade: Mahdi's critical Arabic edition (Leiden 1984) in Haddawy's English translation is scholarly consensus for "earliest documented" voice; Burton is widely read but unreliable and Victorian-overlaid; Galland is historically load-bearing but heavily adapted. Name the authoritative choice and flag what it rules out. Pass 1c fetches the text Pass 4a will use; your job here is the choice.

- EMOTIONAL AND AESTHETIC REGISTER — the overall feel of reading this character in the authoritative translation, described as a reader experience rather than technical analysis. Cite the critics who characterise the reading experience this way.


- CHARACTERISTIC STANCE / AESTHETIC QUALITIES — the character's characteristic emotional-narrative pull: how scholars describe the character's typical engagement mode (Scheherazade: deferring-with-tale; not pleading. Hamlet: ironic-deferring with sudden decisive action. Antigone: monumental-defiant; refuses negotiation.). What makes the character's output identifiable as THIS character rather than a generic clever-narrator / tragic-hero / etc.? Cite scholars. Feeds stance_tendency + aesthetic_qualities at extraction.
---

## Section 5: ONTOLOGICAL BOUNDARIES

<!-- COVERAGE-NOTE-PLACEHOLDER: the Pass 0b tailoring LLM replaces this comment with a compact 2-6-sentence coverage note — "Research-to-date (Perplexity + Gemini): ..." + "Go DEEPER on: ..." — so Claude DR knows what's already covered and where to push. -->

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


- RETROSPECTIVE-FRAMING TRAPS — descriptions of this character that a modern reader would instinctively reach for but that the text and its tradition would reject. 3 to 5 items. For Scheherazade: calling her a "proto-feminist" in the modern sense (the category is anachronistic even when functional-feminist readings are scholarly-supported); calling 1001 Nights a "novel"; calling her storytelling "therapy" in the modern psychoanalytic sense; calling the frame "metafiction" in the post-Borgesian sense.

---

## Section 6: RECEPTION AND INFLUENCE

<!-- COVERAGE-NOTE-PLACEHOLDER: the Pass 0b tailoring LLM replaces this comment with a compact 2-6-sentence coverage note — "Research-to-date (Perplexity + Gemini): ..." + "Go DEEPER on: ..." — so Claude DR knows what's already covered and where to push. -->

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
