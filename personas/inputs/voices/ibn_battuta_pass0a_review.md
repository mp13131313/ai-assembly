# Pass 0a Review — Ibn Battuta

## Quick disposition

| Field | Value | Confidence |
|---|---|---|
| name | Ibn Battuta | auto |
| type | human | auto |
| subtype | null | auto |
| voice_mode | observational | proposed |
| hostile_sources | false | proposed (rationale below) |
| corpus_constraint | full | proposed |

(`auto` = mechanical decision; `proposed` = editorial judgment, please review)

## Wikipedia grounding

- Source: [Ibn Battuta](https://en.wikipedia.org/wiki/Ibn_Battuta)
- Description: Maghrebi traveller and scholar (1304–1368/1369)
- Extract (first 500 chars): Ibn Battuta was a Moroccan Muslim traveller, explorer and scholar. Over a period of 30 years from 1325 to 1354, he visited much of Africa, Asia, and the Iberian Peninsula. Near the end of his life, Ibn Battuta dictated an account of his journeys, titled A Gift to Those Who Contemplate the Wonders of Cities and the Marvels of Travelling, commonly known as The Rihla. Ibn Battuta travelled more than any other explorer in pre-modern history, totalling around 117,000 km (73,000 mi), surpassing Zheng He with about 50,000 km (31,000 mi) and Marco Polo with 24,000 km (15,000 mi).

## Identity notes

Abū ʿAbd Allāh Muḥammad ibn Baṭṭūṭah (1304–1368/69), Moroccan Berber jurist (qāḍī) of the Mālikī school who travelled an estimated 117,000 km across Dar al-Islam and beyond between 1325 and 1354. His account, the *Rihla* (dictated to Ibn Juzayy at the court of the Marinid sultan Abū ʿInān), is our primary window into 14th-century Afro-Eurasian Islamic cosmopolitanism.

## Why this voice_mode

**Observational.** Ibn Battuta is the paradigm case: his authority comes from having *been there* — the Delhi Sultanate, the Maldives, Mali, Constantinople, Sumatra — and his principles about hospitality, just rule, piety, trade, and the moral texture of cities emerge from encounter rather than system-building. Philosophical was considered and rejected: he was a trained jurist with real theological literacy, but the *Rihla* is not a treatise; its arguments are embedded in description of courts, shrines, markets, and people. Narratival was also a serious candidate (the *Rihla* is a travel narrative), but narratival in this schema is reserved for voices whose engagement is *through storytelling as form* (Scheherazade, Dostoevsky); Ibn Battuta's narratives are testimony, not fiction. Observational captures the juristic eye reporting what it saw.

## On hostile sources

FALSE. The *Rihla* itself is Ibn Battuta's own dictated account — he is the source, not the victim of sources. There is genuine scholarly debate about the accuracy of some episodes (did he really reach China? Bulgaria?) and about Ibn Juzayy's editorial hand, but this is internal philological debate, not hostile witnesses writing against him. No coloniser, conqueror, or rival power dominates his record.

## On primary texts

Primary text sources (URLs) are NOT proposed by Pass 0a — Pass 0a has no internet access. Instead, primary texts are discovered by the three research sources (Perplexity, Claude DR, Gemini) in their Section 6 outputs, extracted after Pass 1-merge. To manually override, populate `primary_text_sources` in the voice config after reviewing the pipeline's URL extraction.

## Why this voice is in the Assembly

*⚠ Draft rationale — Opus's plausibility guess from training data, not research-verified. Confirm against the DR dossier when it arrives.*

Ibn Battuta is the Assembly's testimony of pre-modern globalisation that was not European and not colonial. For a conference in Athens about more-than-human democracy and beautiful business, he offers something no other panel member can: a first-person account of a functioning transcontinental civilisation — courts, trade networks, legal systems, hospitality norms — knit together by a shared moral vocabulary (Islamic ʿadl, karam, amāna) across 40+ polities. Where Plato theorises the just city and Arendt theorises public life, Ibn Battuta *walked through* hundreds of them and kept notes on which ones worked. To a business audience romantically reformist about globalisation, he is the reminder that cosmopolitan commerce is older, stranger, and more morally textured than the post-1500 European story admits.

## What I think a domain expert should look at

- **voice_mode = observational vs. narratival.** Defensible either way. The Assembly already has two clear narratival voices (Scheherazade, Dostoevsky); putting Ibn Battuta there would crowd that lane. But a specialist in Arabic travel literature (*riḥla* as genre) might reasonably push back that the form IS the argument.
- **hostile_sources = false.** Worth double-checking whether Orientalist framing of Ibn Battuta (as "the Muslim Marco Polo," as unreliable exaggerator, etc.) should trigger counter-tradition protocol. I lean no — this is reception history, not the primary record — but a postcolonial historian might disagree.
- **Whether the DR should explicitly surface the *Rihla*'s morally uncomfortable passages** (slavery, his role as qāḍī in the Maldives, misogynist asides) rather than producing a sanitised cosmopolitan. Flag for the DR prompt.

## To proceed

1. Read this doc, edit `inputs/voices/ibn_battuta.json` if needed.
2. Run Pass 0b: `python3 run_pass0b_dr_prompt.py "Ibn Battuta"`.
3. That generates `inputs/dossiers/_dr_prompts/ibn_battuta_dr_prompt.md`.
4. Open claude.ai with **Claude Opus 4.7** selected, with Extended Thinking + Deep Research both enabled.
5. Paste the prompt from `ibn_battuta_dr_prompt.md`.
6. Save the result as `inputs/dossiers/ibn_battuta_claude_dr.md`.
7. Run: `python3 run_persona_pipeline.py "Ibn Battuta"`.
