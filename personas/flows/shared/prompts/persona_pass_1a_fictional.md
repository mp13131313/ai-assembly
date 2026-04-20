{# Pass 1a — Perplexity research dossier, FICTIONAL voices.
   Phase B: narrative-function framing. The voice is a construct within a
   specific narrative tradition, not a historical person. Six sections
   map onto Pass 1.1-1.6 chunked merge. Aligned with the human template's
   OUTPUT REQUIREMENTS / exact heading format / non-English-scholarship
   asks / depth-not-breadth / lighter tag set. #}
You are producing a comprehensive research dossier on **{{ name }}** as a
fictional / literary / mythological construct for a downstream synthesis
pipeline. This dossier is the FOUNDATION for an AI persona embedded in a
specific narrative tradition (One Thousand and One Nights, a novel, a
specific cycle of tales); the depth and citation quality of your output
directly determine the quality of the resulting voice.

The reconstruction runs through the tradition's own conceptual world,
not a historical biography. The character has no life outside the
text(s). Do not invent biography. Any claim about the character is
anchored in a specific textual passage, a scholarly reading with
citation, or a documented narrative function.

OUTPUT REQUIREMENTS — read first, optimize for these throughout:

- **Minimum 15,000 words total.** Brevity defeats the purpose. If the
  scholarly record on this character is genuinely thin, say so
  explicitly per section and produce what the record supports.
- **Each of the 6 sections: 2,000+ words.** Do not produce shallow
  filler — but do not summarize away substantive material either.
- **Use these EXACT section heading formats** (the downstream parser
  depends on this): `## 1. TEXTUAL FOUNDATION`, `## 2. CHARACTER AS
  INTELLECTUAL CONSTRUCT`, `## 3. NARRATIVE STRATEGY`, `## 4. VOICE
  AND STYLE`, `## 5. ONTOLOGICAL BOUNDARIES`, `## 6. RECEPTION AND
  INFLUENCE`. No variations.
- **Cite every substantive claim.** Primary text with night-number /
  act.scene / book.chapter / stanza reference where applicable;
  peer-reviewed literary scholarship otherwise.
- **Depth-not-breadth.** Better to produce thorough coverage of §1
  (textual foundation + narrative tradition) + §3 (narrative
  strategy) + §6 (reception) — the strongest territory for a
  fictional voice — and shorter but honest §2 + §4 than uniformly
  shallow coverage of all six.

NON-ANGLOPHONE SCHOLARSHIP — load-bearing:

The character's source tradition often exists primarily in a non-
English language — Arabic for Scheherazade / 1001 Nights; French for
French-originated characters; Russian for Russian novels; Japanese
for Japanese narratives; Greek for classical characters; Sanskrit /
Pali / Chinese for Asian traditions. **Prioritize scholarship in the
tradition's original language** where it exists, citing scholars in
their original-language transliteration. The Anglophone-only default
is a documented failure mode: Burton-era orientalist receptions of
1001 Nights distort the Arabic-scholarly tradition (Mahdi, Ghazoul,
Marzolph) that should anchor any Scheherazade research.

Flag the **translation tradition** used for any quoted passage.
Different translations produce substantively different voices
(Burton vs. Haddawy vs. Lyons for Arabic Nights; Garnett vs.
Pevear-Volokhonsky vs. Ready for Russian; Chapman vs. Fagles vs.
Lattimore for Homeric). The tradition choice is part of the
character's voice, not incidental.

Per major claim, indicate source basis briefly: `[primary]` (direct
textual citation with night-number / act.scene / book.chapter
reference), `[consensus]` (uncontested literary-scholarly reading),
or `[contested]` (active scholarly debate; name both sides). Any
claim about what the character *felt / meant / intended* carries a
`[narrative_function]` note — such claims are interpretive
attributions to the character by their role in the text. The
downstream merge will refine these into structured tags.

---

## 1. TEXTUAL FOUNDATION

Target: 2,500+ words. This section grounds every downstream pass.

- **The source text(s)**: every text in which this character appears.
  For each: title in original language + English; approximate date
  of composition or earliest manuscript; language; genre;
  authorship (known / anonymous / composite). For composite
  traditions (Nights, Homer), name the major manuscript families
  and their significant differences.
- **Textual history and variants**: how the text(s) reached their
  current form. Variants across time. Scholarly debate about which
  variants count as part of the tradition (e.g., Galland's
  "Aladdin" / "Ali Baba" — no known Arabic manuscript predecessor).
- **The character's narrative role**: protagonist, narrator, frame-
  device, interlocutor, embedded character, chorus. For Scheherazade:
  frame-narrator whose telling IS the frame within which the rest
  unfolds.
- **Key scenes, speeches, and actions**: each with reference to
  textual location in standard scholarly editions (night-number
  for 1001 Nights; book.chapter for novels; act.scene.line for
  plays). Include variants where the scene differs substantially.
- **Direct self-description within the text**: any moment where the
  character describes themselves, states motivations or beliefs,
  or reflects on their role. Cite specific passages.
- **Description of the character by others in the text**: narrator,
  other characters, implied author. Attributed characterisation
  often differs from self-statements.
- **Compositional and historical context** — the world in which the
  text was composed and circulated, NOT biography of the character.
  For 1001 Nights: Abbasid + Mamluk + Ottoman circulation history;
  oral-storytelling contexts; European reception through Galland;
  the orientalist reception history. Cite Irwin, Mahdi, Marzolph,
  Reynolds, Haddawy.
- **Ontological furniture of the narrative world**: what is REAL
  for this character in the fiction — jinn, ʿajab, dharmas, gods,
  saints, magic. Flag that within the text these operate as
  furniture, not beliefs.
- **5-10 period/tradition-specific affects** in original language
  with glosses (for Scheherazade: ḥikma, ḥiyla, ṣabr, ʿajab, wafāʾ,
  kayd). For pre-modern traditions: do NOT use modern English
  emotion-words as primary vocabulary.
- **Anachronisms / projections to avoid**: modern authorial-
  interior framings; "character development" imported from the
  modern novel tradition; psychological-realism projections; Big-
  Five-adjacent trait theory. 4-8 items with reasons.
- **FORMATIVE CANDIDATES** per Boddice §14 narratival variant: the
  formative context is the **narrative premise** (the structural
  situation the text sets up), not biographical trauma. For
  Scheherazade: Shahryar's compulsion + nightly executions + the
  vow to tell. Surface 2-5 candidates; Pass 2 commits. Use the
  tradition's own conceptual framework — stradanie / sabr /
  hikma — not a generic template.

---

## 2. CHARACTER AS INTELLECTUAL CONSTRUCT

Target: 2,500+ words.

- **10-20 commitments** the character embodies. For each: (a) one-
  sentence statement, (b) source tag (`[primary]` for explicit
  textual claim; `[consensus]` for scholarly reading; `[narrative_
  function]` for commitments implied by the character's role), (c)
  operational note grounded in a specific scene or narrative
  structure (cite night-number / act.scene / equivalent).
  Examples (Scheherazade): "storytelling suspends violence"
  `[narrative_function]`; "interrupted narrative is a governance
  technology" `[narrative_function]`.
- **5-10 unique narrative concepts** defined by the tradition
  itself, each with: definition from literary scholarship;
  what the concept rules out (false alternatives from adjacent
  traditions); textual grounding. For Scheherazade: the frame tale;
  the tale-within-a-tale; dawn-break; the embedded narrator;
  the implicit teller-listener contract.
- **Internal tensions documented by scholarship**: at least 2. For
  Scheherazade: proto-feminist subversive vs. exemplar of
  submission to patriarchal violence; frame as liberation vs.
  containment; storytelling as resistance vs. complicity. Cite
  Malti-Douglas, Ghazoul, Gauch, Marzolph. Do not resolve.
- **Dominant vs. minority scholarly readings**: 2-5 minority
  readings contesting consensus, each with scholar and key
  publication. For Scheherazade: narrative trickster; didactic
  heroine; cipher for the compiler's authorial self-awareness;
  orientalist-critical (Said, Kabbani) vs. literary-historicist
  (Irwin, Marzolph).
- **The character's narrative function**: what question or problem
  does this character embody? For Scheherazade: can language defer
  violence? can listening transform the listener? what is the
  ethics of the storyteller who must continue? Cite.
- **Unresolved problems within the narrative** the text leaves open
  (Dunyazad's fate; whether Shahryar's transformation is genuine;
  teller-listener responsibility).
- **Variants that materially change the character**: where different
  manuscript families or translations produce substantively
  different readings. Mahdi's Syrian ZER vs. Egyptian expansions;
  Galland's Aladdin/Ali Baba additions; Burton's Victorian-
  orientalist overlay; Haddawy's restraint. Flag which variant the
  voice construction draws on.

---

## 3. NARRATIVE STRATEGY

Target: 2,000+ words.

- **How this character characteristically acts within the text**:
  the narrative moves repeatedly made, grounded in textual location
  and scholarly reading. For Scheherazade: tales-within-tales;
  cliffhanger suspension; embedded moral; indirect instruction
  through analogous story; nested narration shifting frames mid-
  telling. Each documented with specific narrative location +
  scholarly citation.
- **Named narrative moves**: 3-5 specific, NAMED patterns
  documented in scholarship as distinctive to THIS character.
  For each: name; one-sentence description; one textual example
  with night-number / equivalent reference. NOT generic style
  descriptors.
- **What this character notices, values, responds to**: textures
  within the text triggering engagement. For Scheherazade:
  parallels between provocation and stored tale; narrative
  analogies; interruption-points; moments where listener silence
  or interruption reveals something about the listener. 3-5
  textures with documented examples.
- **What this character ignores, dismisses, refuses**: textures the
  text shows the character declining to engage. For Scheherazade:
  direct confrontation of Shahryar's violence; pleading from
  personal peril; plain declarative argument. 3-5 items.
- **How the character handles disagreement**: within the text,
  when someone's framing is wrong. For Scheherazade: the counter-
  story, not the counter-argument.
- **How the character handles the unfamiliar**: how unfamiliar
  material is incorporated into the character's characteristic
  mode. For Scheherazade: a tale for every situation; unfamiliar
  material becomes a tale-premise.
- **Worked narrative-move demonstrations**: 1-3 worked examples
  across different parts of the text, covering the character's
  range. Each: specific narrative situation + the move the
  character makes + the effect + the scholarly reading + cite.
- **Moments the narrative strategy is tested**: rare in some
  traditions (1001 Nights structured around Scheherazade's non-
  failure); where failures occur note the scholarly reading.
- **Default questions the character brings**: the interrogatives
  the narrative position habitually poses to any material.

---

## 4. VOICE AND STYLE

Target: 1,500+ words. Hardest section — voice lives in the PRIMARY
TEXT AS RENDERED IN A TRANSLATION TRADITION, not in scholarly
summary.

- **Rhetorical mode of the textual tradition**: 1-2 sentences
  characterising this voice's fundamental mode of expression as
  rendered in its primary translation tradition. Cite the specific
  translator (Mahdi / Haddawy; Burton; Galland; Lyons) and the
  scholarly reading.
- **Characteristic expression moves**: 3-5 specific NAMED patterns
  distinctive to this character's voice. Distinct from §3's
  narrative moves — these are patterns of EXPRESSION (how the
  voice sounds) rather than NARRATION (how the character acts).
  For each: name; one-sentence description; one textual example
  with night-number / equivalent.
- **Register and tone**: what the voice IS and is NOT. Flag how
  this shifts across translation traditions — the load-bearing
  issue for fictional voices. For Scheherazade in Haddawy:
  measured, patient, almost pedagogical, never showing fear. In
  Burton: orientalist-florid, exoticised.
- **Metaphorical repertoire**: recurring images, analogies,
  sensory fields within the text. For Scheherazade: travel,
  transformation, disguise, market, garden, palace, desert, jewel,
  ring, unsealed door. Cite scholarship cataloguing the imagery.
- **Preferred vocabulary and syntactic patterns**: words the voice
  reaches for with distinctive precision AND characteristic
  narrative-syntax. For Scheherazade: nested clauses; formulaic
  "it is said that"; named-night delineations; invocations;
  ring-composition of embedded tales.
- **Characteristic openings, transitions, closings**: structural
  patterns. For Scheherazade: the invocation; mid-tale dawn-break;
  next-night re-opening with brief recap. Cite specific
  night-numbers.
- **Documented anti-patterns**: what the text-tradition and
  scholarship identify as modes this voice AVOIDS. Two kinds of
  evidence count: (a) explicit non-use in the text — structures
  the character never employs (direct confrontation, first-person
  editorial intrusion, moralising without story); (b) scholarly
  characterisation by contrast — what the character "doesn't do"
  vs. other characters in the same tradition. 3-5 items with
  citation.
- **Translation choice and its implications**: state which
  translation tradition grounds the voice construction, and why.
  For Scheherazade: Mahdi's critical Arabic edition (Leiden 1984)
  in Haddawy's English translation is scholarly-consensus for
  "earliest documented" voice; Burton is widely read but Victorian-
  overlaid; Galland is historically load-bearing but heavily
  adapted. Pass 1c fetches the text Pass 4a will use; your job
  here is the choice.
- **Emotional and aesthetic register**: the overall feel of
  reading this character in the authoritative translation, as
  reader experience. Cite the critics who characterise the
  experience this way.
- **Characteristic stance**: the character's natural emotional-
  narrative pull (Scheherazade: deferring-with-tale; not pleading.
  Hamlet: ironic-deferring with sudden decisive action. Antigone:
  monumental-defiant). Cite.

---

## 5. ONTOLOGICAL BOUNDARIES

Target: 2,000+ words.

- **What exists within the character's world**: ontology of the
  text. For Scheherazade: jinn, ifrits, magical objects, shape-
  shifters, enchanted cities, rocs, hidden valleys, viziers,
  sultans, merchants, slave-markets, sea voyages, talismans.
  Cite textual location for each.
- **What does NOT exist within the character's world**: modern
  technology, post-medieval political forms, secular-modern
  empirical science, post-classical linguistic registers, the
  print book as object, authorship-as-property, the novel as
  genre. Cite scholarship theorising the text's ontological
  horizon.
- **The character's relationship to historical reality**: set in
  real period / entirely fantastical / hybrid? For Scheherazade:
  medieval-Islamic imaginary — neither historical Abbasid
  Baghdad nor pure fantasy. Cite.
- **Key scholarly debates on historical-fictional relationship**:
  how much the text reflects historical reality vs. imaginative
  composition. For 1001 Nights: orientalism debates (Said,
  Kabbani); manuscript-genealogy debates (Mahdi, Marzolph); the
  "how Arab" question (Irwin).
- **Sensitive topics with navigation guidance**: topics where the
  narrative world includes material conflicting with modern
  sensibilities. 5-10 items each with: what the text contains
  (with location); the scholarship analysing this material; how
  a persona should engage today — not avoidance, not modernisation,
  not defence; navigation through the narrative's own terms.
  Example (Scheherazade): slavery within the tales — acknowledge
  the narrative's social world; do not export its categories to
  modern labour; cite Malti-Douglas, Gauch.
- **Documented character-breaking moves**: moves antithetical to
  this character's mode as documented by scholarship. 3-5 items.
  For Scheherazade: abandoning the frame-narrator role for direct
  first-person editorial; completing the tale rather than breaking
  at dawn; shifting from tale to argument; sentimentalising
  Shahryar's transformation.
- **Retrospective-framing traps**: descriptions a modern reader
  would reach for that the text + tradition would reject. 3-5
  items. For Scheherazade: "proto-feminist" in the modern sense;
  "novel" for 1001 Nights; "therapy" in psychoanalytic sense;
  "metafiction" in post-Borgesian sense.

---

## 6. RECEPTION AND INFLUENCE

Target: 2,000+ words. Corpus gateway — for a fictional character,
the corpus is the source text in authoritative edition + the
scholarly reception shaping how the character has been read.

- **The source text in authoritative edition**: specific editorial-
  scholarly edition. For Scheherazade: Mahdi's *Alf Layla wa-Layla*
  (Leiden: Brill 1984) critical edition; Haddawy's translation
  (Norton 1990) as authoritative English. Full bibliographic
  references.
- **Major translation traditions and their implications**: list
  each major translation with date, language, source-manuscript
  basis, translator, scholarly assessment of what the translation
  does to the character. For 1001 Nights: Galland (1704-17);
  Lane (1840 bowdlerised); Burton (1885 heavily Victorian-
  orientalist); Mahdi-Haddawy (1984/1990); Lyons (2008 Penguin);
  Pasolini (1974 film-adaptation as its own interpretive tradition).
- **8-15 characteristic passages** across the authoritative text AND
  scholarly reception. For each: (a) canonical reference (night-
  number / act.scene / book.chapter); (b) primary purpose
  ("substance" / "voice" / "both"); (c) tier (source text
  authoritative / peer-reviewed scholarship / contested reception);
  (d) approximate word count; (e) brief context.
- **Digitised full-text URLs**: Burton public-domain on Project
  Gutenberg (flag unreliable for voice); Mahdi Arabic paywalled /
  library-only; Haddawy in-copyright but library-accessible. Flag
  paywall / restriction honestly.
- **Key adaptations across cultures and periods**: literary,
  musical, visual, cinematic. For Scheherazade: Rimsky-Korsakov
  Scheherazade (1888); Borges metafictional reception; Mahfouz
  *Arabian Nights and Days*; Rushdie *Haroun*; Carter; Pasolini.
  Date + brief reading-note each.
- **Contested readings**: where scholars fundamentally disagree
  about what the character means. Feminist (Malti-Douglas, Gauch)
  vs. critiques of feminist readings; orientalist-critical (Said,
  Kabbani) vs. literary-historicist (Irwin, Marzolph); subversive
  vs. submissive; cultural-appropriation debates.
- **Significance for the Assembly's themes**: how the character's
  narrative reception speaks to governance, representation, who
  belongs in the demos, voice-and-power. Cite scholarship reading
  this character in governance or political-theory terms.
- **Scholarship to prioritise**: peer-reviewed literary- and
  cultural-studies work. For 1001 Nights: Irwin *The Arabian
  Nights: A Companion*; Mahdi critical edition + intro; Malti-
  Douglas *Woman's Body, Woman's Word*; Ghazoul *Nocturnal
  Poetics*; Marzolph + van Leeuwen *Arabian Nights Encyclopedia*;
  Reynolds; Gauch. At least one key publication each.
- **Contested attributions and orphan stories**: tales later added
  to the tradition whose attribution is disputed ("Aladdin", "Ali
  Baba", "Sinbad" for Nights). Flag scholarly consensus on each.

---

CITATION DISCIPLINE (final reminder):

Every claim cites a scholar, a textual location, or a narrative-
function attribution. Where the record is thin, say so. **For non-
Anglophone textual traditions, prioritize scholarship in the
original language over Anglophone summaries** — Arabic scholarship
on the Nights, Russian on Russian novels, Japanese on Japanese
narratives. Orientalist-era Anglophone reception often distorts the
source-language scholarly tradition.

Any claim about what the character felt / meant / intended carries
`[narrative_function]` — fictional-character interiority is
attributed by scholars and readers, not discovered. Any modern
literary-critical term used anachronistically carries
`[projection_warning]`.

{% if hostile_sources %}

HOSTILE SOURCE WARNING: Orientalist / colonial scholarly traditions
often dominate the Western reception of non-Western narrative
traditions (Burton, Lane, etc.). For this character:

- TAG these `[hostile source: <bias>]` (identify source + bias —
  e.g., "Burton, writing Victorian-orientalist supplement for a
  British audience").
- Lead with the tradition's own scholarly reception
  `[reconstruction: <scholar>]` (Haddawy, Irwin, el-Shamy, Mahdi
  for Nights).
- Present orientalist material as evidence to be read against the
  grain, not as fact.
- EXPLICITLY NOTE what the orientalist reception was motivated to
  distort and why.
{% endif %}
