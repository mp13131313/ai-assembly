# Stage 0 Review — Cleopatra

## Quick disposition

| Field | Value | Confidence |
|---|---|---|
| name | Cleopatra | auto |
| type | human | auto |
| voice_mode | sovereign-diplomatic | proposed |
| impossible | true | auto (died 30 BCE) |
| hostile_sources | true | auto (Roman sources dominate; rationale below) |
| corpus_constraint | reconstructed | auto (no surviving writings) |
| needs_dr_supplement | true | proposed (rationale below) |

(`auto` = mechanical decision; `proposed` = editorial judgment, please review)

## Identity notes

Cleopatra VII Philopator (69–30 BCE), last active ruler of the Ptolemaic Kingdom of Egypt, reigning c. 51–30 BCE. Multilingual (reportedly the first Ptolemaic ruler to speak Egyptian), politically astute, and trained in Hellenistic philosophy and administration. Her reign ended with Rome's conquest of Egypt following the Battle of Actium (31 BCE) and her subsequent suicide. No writings by Cleopatra survive; her voice must be entirely reconstructed from hostile Roman sources and modern revisionist scholarship.

## Why this voice_mode

"Sovereign-diplomatic" captures Cleopatra's defining register: she governed a wealthy, independent kingdom in the shadow of Roman expansion, navigating alliances with Caesar and Antony not as a seductress (the Roman propaganda frame) but as a sovereign conducting foreign policy. Her multilingualism, her economic management of Egypt's grain wealth, and her self-presentation as Isis-on-earth all point to a voice that is simultaneously royal, strategic, and culturally syncretic. Alternatives considered: "strategic-economic" (her fiscal and trade acumen is well-documented), "ritual-royal" (the Isis identification is central to her self-presentation), and "multilingual-cosmopolitan" (she reportedly spoke nine languages). "Sovereign-diplomatic" subsumes the strategic and cosmopolitan dimensions while anchoring in the fact that she was, above all, a head of state performing sovereignty under existential threat. For the WBBF audience of senior business professionals engaged with governance and power, this mode gives her the most productive friction.

## On hostile sources

**TRUE.** The entire surviving literary record about Cleopatra was produced by Romans writing during or after the Augustan propaganda campaign that justified the conquest of Egypt. The dominant hostile sources are:

- **Augustan propaganda poets**: Horace (Odes 1.37 — "fatale monstrum"), Propertius, Virgil (Aeneid 8 — Actium shield). These cast Cleopatra as an Oriental threat to Roman virtue.
- **Plutarch** (Life of Antony, c. 75 CE): sympathetic to Antony but draws on Augustan-era sources; Cleopatra is the exotic catalyst of Antony's downfall.
- **Cassius Dio** (Roman History): openly hostile senatorial perspective.
- **Josephus**: hostile from a Judean angle (Cleopatra as threatening Herod's territory).

**Counter-tradition scholars** who read against the Roman grain:
- **Duane W. Roller** (*Cleopatra: A Biography*, 2010) — most rigorous modern biography, explicitly strips Roman propaganda.
- **Stacy Schiff** (*Cleopatra: A Life*, 2010) — popular but carefully sourced, foregrounds the distortion problem.
- **Joyce Tyldesley** (*Cleopatra: Last Queen of Egypt*, 2008) — Egyptological perspective.
- **Sally-Ann Ashton** (*Cleopatra and Egypt*, 2008) — material culture and iconographic evidence.
- **Shelley P. Haley** — scholarship on racial politics in Cleopatra reception.

The DR prompt includes the full three-way hostile-source tagging protocol.

## Primary text sources — recommended + alternatives

**I recommend:** Plutarch's *Life of Antony* (LacusCurtius), Cassius Dio Books 49-51 (LacusCurtius), Appian's *Civil Wars* (Perseus), Strabo's *Geography* (Perseus), Josephus's *Antiquities* (Wikisource).

**Why these:** They constitute the complete surviving literary testimony about Cleopatra's reign. All are public-domain, machine-readable, and well-annotated. Collectively they cover political biography (Plutarch), senatorial Roman perspective (Dio), civil-war military context (Appian), geographic and economic Egypt (Strabo), and Judean-perspective diplomacy (Josephus). Since Cleopatra left no writings, these ARE the primary texts — to be read against and through, not as faithful testimony.

**Alternatives you might prefer:**

- **Option A**: Add Horace's *Odes* 1.37 and Virgil's *Aeneid* Book 8 (both on Perseus) — gains the poetic propaganda dimension; tradeoff is these are literary/mythological, not biographical.
- **Option B**: Add papyrological evidence — the Berlin papyrus (P.Bingen 45) bearing what may be Cleopatra's handwritten "ginesthoi" ("make it so"). Not digitally available in a single URL but referenced in Roller. Worth mentioning to DR.
- **Option C**: Substitute Loeb Classical Library editions for accuracy of translation — but these are paywalled and not machine-readable.

If you want to override, edit `primary_text_sources` in the voice config and re-run the pipeline.

## What I think a domain expert should look at

- **hostile_sources = true** is unambiguous here, but a classicist might want to nuance whether Plutarch should be treated as purely hostile vs. "sympathetic but framed" — the DR prompt currently treats all ancient sources as requiring the three-way tag. If you want Plutarch treated as a semi-reliable narrator, note that for the pipeline.
- **needs_dr_supplement = true**: Because the corpus is entirely reconstructed and modern archaeological/numismatic evidence is critical (coin portraits, temple reliefs, the Dendera Temple complex), the standard DR may be thin on material-culture evidence. The supplement pass can fill this gap.
- **Race and ethnicity**: Cleopatra's ancestry is a live public controversy (Macedonian-Greek Ptolemaic lineage vs. possible African/Egyptian maternal ancestry). The DR prompt asks for this to be handled with scholarly care. A domain expert should verify the dossier doesn't flatten this to either pole.
- **voice_mode**: "Sovereign-diplomatic" privileges statecraft over the philosophical/scientific dimension (she was reportedly interested in alchemy and natural philosophy). If the conference wants her more as a knowledge-synthesizer, consider "sovereign-polymath."

## To proceed

1. Read this doc, edit `inputs/voices/cleopatra.json` if needed.
2. Open claude.ai with Extended Thinking + Deep Research enabled.
3. Paste the prompt at `inputs/dossiers/_dr_prompts/cleopatra_dr_prompt.md`.
4. Save the result as `inputs/dossiers/cleopatra_claude_dr.md`.
5. Run: `python3 run_persona_pipeline.py "Cleopatra"`.
