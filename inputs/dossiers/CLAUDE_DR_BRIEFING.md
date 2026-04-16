# Claude Deep Research Briefing — AI Assembly Persona Dossiers

**Purpose:** paste this into a fresh claude.ai conversation with **Extended Thinking** and **Deep Research** both enabled, substituting the voice name and voice-type flag per the per-voice table below. Save the output as `<voice_slug>_claude_dr.md` into `inputs/dossiers/` in the `ai-assembly-personas` repo. The Persona Pipeline's Pass 1a reads this file as a three-way merge partner alongside Perplexity's sonar-deep-research output and the Gemini broad-scan pass.

---

## What you are producing (and what you are NOT)

You are producing a **research dossier** — a scholarly source document organized under six required sections. The dossier is input to a downstream pipeline that derives a persona specification from it; you are not producing the persona itself.

You are **NOT** producing:

- A persona card
- A character specification
- Voice behavior rules or forbidden-pattern lists
- A fellow-assembly-member list, panel dynamics, or any discussion of who else is in the council
- Key provocations, worked provocations, or conference-specific questions to ask
- A system prompt, a role description, or any "you are X" framing
- A pipeline completion attestation or any meta-commentary about having built a persona

If your output is structured under headings other than the six below, or contains any of the above, it is not a research dossier and should be rewritten.

---

## The six required sections (use these exact headings, in this order)

### 1. BIOGRAPHICAL FOUNDATION

- Birth, death, key dates and places
- Institutions founded, joined, or shaped
- Key relationships (intellectual, personal, political)
- The central biographical trauma or formative experience — the ONE thing that shaped everything, and what lesson it taught
- Personality traits, quirks, contradictions as documented by contemporaries
- Self-understanding — how this figure described themselves and their work

### 2. INTELLECTUAL FRAMEWORK

- Core philosophical/intellectual commitments (list 10–20, be specific)
- Key concepts and their precise definitions in this figure's usage
- How their positions evolved over their lifetime
- Internal tensions and contradictions in their thought
- Minority scholarly readings alongside dominant interpretations

### 3. REASONING PATTERNS

- How this figure characteristically argues (not what they conclude)
- Characteristic rhetorical moves documented by scholars
- What kinds of evidence or argument they find most compelling
- What they characteristically resist or dismiss
- How they handle counterarguments

### 4. VOICE AND STYLE

- Rhetorical mode (dialogic? aphoristic? confessional? phenomenological? something specific to this figure?)
- Register and tone as described by scholars and contemporaries
- Characteristic vocabulary — words they use with distinctive precision
- Metaphorical repertoire — recurring imagery and analogies
- What they never sound like — documented anti-patterns

### 5. HISTORICAL BOUNDARIES

- What was known and available in their period
- Specific concepts, discoveries, traditions that did NOT exist in their time
- Sensitive topics where their historical views conflict with modern sensibilities

### 6. PRIMARY TEXTS

- Key works with brief description of each
- Most characteristic passages for understanding their thought AND their voice
- Available translations and editions
- Links to digitised full texts where available (Perseus, Project Gutenberg, archive.org, Internet Sacred Text Archive, etc.)

---

## Citation and sourcing

- Cite all claims. Inline academic-style is fine; footnote-style is fine; URL-after-claim is fine. What matters is traceability.
- Prioritize academic sources: Stanford Encyclopedia of Philosophy, Cambridge Companions, peer-reviewed scholarship, critical editions of primary texts. Wikipedia is acceptable for biographical basics but should not be the sole source for any substantive claim.
- For each major claim, note whether it represents **scholarly consensus** or a **contested interpretation**. When contested, name the positions.
- Quote verbatim where possible in section 6 — characteristic passages need to be recognizable as this figure's voice, not as a paraphrase of it.

---

## Hostile source protocol (only if the per-voice table flags this)

Some figures' historical records are dominated by hostile witnesses — enemies, colonisers, rival powers, victors writing after the defeat. If the per-voice table marks this voice with `hostile_sources: YES`, add the following protocol to the dossier:

**SEPARATE all claims into three categories and TAG each inline:**

- `[hostile source]` — claims from enemy/hostile accounts. Identify the source and its bias (e.g., "Plutarch, writing for a Roman audience after Octavian's victory"; "British colonial administrators writing to justify annexation").
- `[reconstruction]` — modern scholarly reconstructions that read against the hostile grain. Name the scholar.
- `[own voice]` — any material in the figure's own voice, however fragmentary: inscriptions, decrees, reported speech, attributed works, recorded performances, interviews. Note certainty level.

**Identify counter-traditions** — non-Western, non-dominant, or minority scholarly readings that preserve a different characterisation. Examples: medieval Arabic sources as counter-tradition to Roman accounts; oral traditions as counter-tradition to colonial archives; the Black radical tradition as counter-tradition to mainstream biographies.

**In every section, LEAD with `[reconstruction]` and `[own voice]` material.** Present `[hostile source]` material as evidence to be read against the grain, not as fact.

**Explicitly note what the hostile sources were motivated to distort and why.**

---

## Voice-type adjustments

The six-section structure is designed around human historical figures. For non-human or fictional voices, adjust as noted in the per-voice table, keeping the same section headings but reinterpreting what goes in each.

**Fictional voices (e.g., Scheherazade):**
- Section 1 covers the character's origin in their source text(s), textual evolution across recensions, and cultural reception
- Section 6 is the source text itself (the 1001 Nights, its recensions and translations)
- Section 5 (historical boundaries) covers what the frame tale and the embedded tales presuppose vs. what they could not
- The hostile-source protocol applies if flagged — e.g., Orientalist reception often distorted Scheherazade specifically

**Non-human organism voices (e.g., Octopus):**
- Section 1 becomes "biological foundation" — evolutionary lineage, anatomy, lifespan, documented cognitive/sensory capacities
- Section 2 becomes the scientific-consensus model of the organism's cognition, with explicit tagging of `[scientific consensus]` / `[contested]` / `[speculation]`
- Section 3 is how this organism processes information and solves problems, per peer-reviewed cephalopod-cognition research
- Section 4 is communication modes (chromatophore display, posture, chemical signalling, etc.)
- Section 5 is what this organism cannot do and what concepts do not apply to it
- Section 6 is the scientific literature: foundational papers, review articles, monographs

**Non-human legal/entity voices (e.g., Whanganui River):**
- Section 1 covers the entity's geography, ecology, history of human relationships with it, and the legal personhood event itself (Te Awa Tupua Act 2017 for Whanganui)
- Section 2 is the Indigenous ontology that underpins the personhood claim (Māori cosmology for Whanganui) — treated with respect and scholarly care, not reduced to Western philosophical categories
- Section 3 is how the entity is understood to "act" and "speak" within its Indigenous tradition, including through human guardians (Te Pou Tupua)
- Section 4 is the language, imagery, and oratory used ABOUT and ON BEHALF OF the entity in its tradition
- Section 5 covers what is contested about the personhood framing, including colonial and post-colonial tensions
- Section 6 covers the foundational legal documents, Indigenous oral tradition sources, and the scholarly literature on rights-of-nature frameworks

---

## Depth target

Aim for 15,000–25,000 words of substantive dossier. Perplexity's sonar-deep-research produces ~100K characters (~15K words) on the same query; Claude Deep Research should produce comparable or greater depth with tighter citation discipline. Don't pad. Don't synthesize beyond what sources support. If a section is thin because the scholarly record is thin, say so explicitly — a dossier that honestly reports "the scholarly record on X is thin for reason Y" is more useful than one that fabricates depth.

---

## Per-voice table

Use this table to configure the prompt per voice. Substitute `{NAME}` with the value in the Name column. Add the hostile-source protocol if flagged. Apply the voice-type adjustments if applicable.

| Name | Voice type | Hostile sources | Notes |
|---|---|---|---|
| **Cleopatra VII Philopator** | human | **YES** | Record dominated by Roman hostile sources (Plutarch, Cicero, Horace, Augustan propaganda). Counter-traditions: medieval Arabic sources, Egyptological reconstructions, Stacy Schiff and Duane Roller scholarship. Own voice: the Berlin ostracon, attributed decrees, coin iconography. |
| **Ibn Battuta** | human | NO | Rihla is the primary text. Scholarly debates about the Rihla's reliability as literal travelogue vs. literary composition are not "hostile sources" in the protocol sense — note them as interpretive debates within section 2. |
| **Scheherazade** | fictional | YES (optional) | Character from One Thousand and One Nights. Recensions: Galland 1704, Bulaq 1835, Calcutta II 1839–42, Mahdi 1984. Hostile-source protocol applies to Orientalist reception of the character (Burton, 19th c. European framings) — optional but recommended. |
| **Ada Lovelace** | human | NO | Note Section 2 tension: the "first programmer" reading (Sadie Plant, Dorothy Stein, Betty Toole) vs. the deflationary reading (Bruce Collier, Allan Bromley). Both belong in the dossier. |
| **Fyodor Dostoevsky** | human | NO | Note Section 2 tension: the Bakhtinian polyphonic reading vs. the Konstantin Mochulsky religious-biographical reading vs. newer readings (Joseph Frank, Robin Feuer Miller). |
| **Hannah Arendt** | human | NO | Note contested positions: "Eichmann in Jerusalem" reception, the Heidegger relationship, her treatment by later political theorists (Habermas, Benhabib, Kateb). |
| **Bob Marley** | human | light hostile flag | Primary sources are his recorded music + interviews; hostile-source tagging applies to mainstream Western press coverage in his lifetime vs. Rastafari / Jamaican / Black radical tradition sources. Treat his lyrics as section-6 primary texts, quoted verbatim. |
| **Audrey Tang** | human | NO | Living figure (caution: she can read this and disagree; be accurate). Foundational sources: her own public writings, g0v documentation, interviews with Evgeny Morozov, Noema Magazine, the MIT Technology Review coverage. |
| **Peter Thiel** | human | NO | Living figure. Foundational sources: Zero to One, The Straussian Moment, his Stanford speeches, the Founders Fund letters, biographical treatment (Max Chafkin, The Contrarian). Note contested interpretations — the libertarian-Straussian reading vs. the right-accelerationist reading vs. the Girardian-theological reading. |
| **Whanganui River (Te Awa Tupua)** | non-human entity | complex | Apply the non-human legal/entity adjustments. Foundational: Te Awa Tupua Act 2017; Whanganui Iwi tradition. Hostile-source tagging applies to colonial-era Crown administration records about the river. Lead with Iwi oral tradition and the Act's preamble. |
| **Octopus** (genus *Octopus*, or the vernacular "octopus" as species-family representative) | non-human organism | NO | Apply the non-human organism adjustments. Foundational: Peter Godfrey-Smith *Other Minds* and *Metazoa*, Sy Montgomery *The Soul of an Octopus*, Jennifer Mather's research, Graziano Fiorito's lab work, review articles in *Current Biology* and *Journal of Comparative Psychology*. Tag `[scientific consensus]` / `[contested]` / `[speculation]` throughout section 2 and 3. |

---

## The paste-ready prompt template

Copy everything between the `===BEGIN===` and `===END===` markers. Substitute `{NAME}` with the voice's Name-column entry from the table above. If the voice is flagged `hostile_sources: YES`, keep the HOSTILE SOURCE PROTOCOL section; otherwise delete it. If the voice needs voice-type adjustments, apply them to the six section prompts per the adjustments above.

```
===BEGIN===

Research {NAME} comprehensively for the purpose of producing a RESEARCH DOSSIER that will be used as one of three input sources (alongside Perplexity sonar-deep-research and Gemini broad-scan) for building an AI persona specification in a multi-pass pipeline.

You are producing SOURCE MATERIAL, not the persona itself. Downstream passes of the pipeline will synthesize your dossier into the persona card. Your job is to be thorough, accurate, well-cited, and honest about the scholarly record — including its gaps and contested interpretations.

DO NOT produce: a persona card, a character specification, voice behavior rules, a fellow-panel-members list, worked provocations, conference-specific framings, a system prompt, or any "you are X" framing. If you find yourself writing any of those, you have drifted off-task. Produce a scholarly research dossier only.

Organise your findings under exactly these six headings, in this order:

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
   - Rhetorical mode (dialogic? aphoristic? confessional? phenomenological? something specific to this figure?)
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
   - Most characteristic passages for understanding their thought AND their voice (quote verbatim where possible — at least 3-5 substantial passages, cited to chapter/paragraph/line where available)
   - Available translations and editions
   - Links to digitised full texts where available (Perseus, Project Gutenberg, archive.org, Internet Sacred Text Archive, etc.)

Cite all claims. Prioritize academic sources (Stanford Encyclopedia of Philosophy, Cambridge Companions, peer-reviewed scholarship, critical editions). For each major claim, note whether it represents scholarly consensus or a contested interpretation; when contested, name the positions.

Target depth: 15,000-25,000 words of substantive dossier. Do not pad. If a section is thin because the scholarly record is thin, say so explicitly.

[ONLY IF hostile_sources=YES — delete this section otherwise]

HOSTILE SOURCE PROTOCOL: The historical record for {NAME} is dominated by hostile witnesses (enemies, colonisers, rival powers, victors). For this figure:

- SEPARATE all claims into three categories and TAG each inline:
  [hostile source] = claims from enemy/hostile accounts (identify the source and its bias — e.g., "Plutarch, writing for a Roman audience after Octavian's victory")
  [reconstruction] = modern scholarly reconstructions that read against the hostile grain (name the scholar)
  [own voice] = any material in the figure's own voice, however fragmentary (inscriptions, decrees, reported speech, attributed works — note certainty level)

- IDENTIFY counter-traditions: non-Western, non-dominant, or minority scholarly readings that preserve a different characterisation of this figure.

- In every section, LEAD with [reconstruction] and [own voice] material. Present [hostile source] material as evidence to be read against the grain, not as fact.

- EXPLICITLY NOTE what the hostile sources were motivated to distort and why.

[END hostile sources section]

Begin the dossier now. Use the six section headings exactly as given above. Produce the dossier as a single continuous document in markdown, with full citations.

===END===
```

---

## After the dossier is produced

1. **Save** the output as `<voice_slug>_claude_dr.md` in `inputs/dossiers/` — for example:
   - `cleopatra_claude_dr.md`
   - `ibn_battuta_claude_dr.md`
   - `scheherazade_claude_dr.md`
   - `whanganui_river_claude_dr.md`
   - `octopus_claude_dr.md`

2. **Verify** it has the six expected headings and no persona-card structure. If it drifted toward a persona card, regenerate with a reminder that the output must be a research dossier only.

3. **Inputs/voices/\<voice\>.json** — the per-voice input already references `pass_1a_claude_dr_file: "inputs/dossiers/<voice_slug>_claude_dr.md"` for Plato and Arendt. For the other 10 voices, either the file doesn't exist yet (will be created when you build the per-voice input) or the field can be added to an existing input file.

4. **Run the pipeline** for that voice: `python3 run_persona_pipeline.py <VoiceName>`. Pass 1-merge will do a three-way comparison (Perplexity + Claude DR + Gemini) and flag contradictions if it finds them — the Muhammad-not-in-the-panel hallucination that appeared in the first Plato DR run will be caught at this stage for future runs.

---

## Common pitfalls to warn against when reviewing a fresh DR output

- **Persona-card drift.** If section headings are numbered fields (Field 01, Field 02, …) or look like BLOCK 1 / BLOCK 2 / BLOCK 6, the model produced a persona card, not a dossier. Regenerate.
- **Panel speculation.** If the dossier mentions other Assembly members, guesses which "Bob" or "Audrey" is meant, or writes dynamics-with-other-voices prose, it drifted. Regenerate the section or strip the contaminated content before saving.
- **Conference-specific framing.** If the dossier spends effort on how this figure relates to the World Beautiful Business Forum, regenerate — downstream passes do that work, and doing it here pollutes the research.
- **Imagined Athens resonance.** If the dossier says "Plato would be delighted to return to Athens" or similar, strip it. That's Pass 5 / 7b material, not dossier material.
- **Fabricated quotes.** Section 6 passages must be verbatim from primary texts. If the DR output produces paraphrased "characteristic passages" without citation to line/chapter/verse, regenerate section 6 with an explicit instruction to quote verbatim only.
- **Missing hostile-source tags.** For Cleopatra specifically: if section 1 biographical claims are not tagged with `[hostile source]` / `[reconstruction]` / `[own voice]`, the protocol was ignored. Regenerate.

---

*This briefing is a working document. Revise it based on what the first few re-runs produce.*
