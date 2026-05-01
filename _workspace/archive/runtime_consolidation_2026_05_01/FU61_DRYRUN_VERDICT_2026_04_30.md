# FU#61 Cleopatra dryrun — verdict

**Date:** 2026-04-30
**Branch:** `voice-pipeline-v2.1-align-revert`
**Test:** Persona thread patched Cleopatra's `07_persona_card_assembled.json` `quality_criteria` field — added one new criterion (criterion 6, cold-reader / public-document accessibility, in her grammar). Voice Pipeline re-ran Step 2 only against the existing dryrun briefing.

**Run dir:** `<PROJECT_ROOT>/voice-pipeline-dryrun/runs/dryrun_2026_04_29_plato_cleopatra/`

---

## TL;DR

**Mostly worked, with one material over-correction.**

- 4 of 5 Layer 1 failure points improved (#2 clean, #3 N/A — argument restructured, #4 better anchor, #5 partial)
- 1 over-correction: salutation lost Greek alphabet AND Egyptian transliteration entirely (#1)
- Criterion 6 needs a script-preservation clause distinguishing head/seal (where script IS the authority) from body (where gloss does the work)
- Borderline: P.Bingen 45 reference (modern catalog name; voice-temporal-stance violation); final standalone γινέσθωι still untranslated

Recommend: sharpen the criterion text, re-test, then propagate the pattern to other hard-form voices (Whanganui River, Marley, possibly Octopus).

---

## Setup

- Backed up entire `04_voice/` directory → `04_voice_pre_FU61/` (preserves Run #4 Cleopatra baseline)
- Verified card patch: `quality_criteria` length = 6, criterion 6 starts with "Does the prostagma reach a reader who was not at our chancery..."
- First re-run (Steps 1+2 with default validation ON): wall 495s, 8 min spent on validation calls; **Step 2 was checkpoint-cached** — patched card never executed
- Moved cached Step 2 aside → `cleopatra.pre_FU61_inplace.json`
- Second re-run (Step 2 only, `--skip-validation`): wall 69s, new artifact written

Both backups byte-identical to original Run #4 Cleopatra; diffable any time.

---

## Pass status per failure point

| # | Failure point | Pre-patch | Post-patch | Verdict |
|---|---|---|---|---|
| 1 | **Salutation** | Greek alphabet + 5 epithets + Egyptian transliteration before English gloss | "Cleopatra Thea Philopator Philopatris, Basilissa, Lady of the Two Lands — to the chanceries of a later age…" — fully Latin-script, "New Isis" dropped, Egyptian transliteration dropped | **OVER-CORRECTED** |
| 2 | **bia/prostagma/nomos triplet** | Three un-glossed terms in load-bearing sentence | *"Prostagma kai enteuxis — the decree descending, the petition ascending"* + *"Bia in the costume of nomos — force wearing the form of decree"* | **PASSED clean** |
| 3 | **εὐεργεσία/mrwt** | εὐεργεσία un-glossed; mrwt glossed | Argument restructured around different terms (*enteuxis*, P.Bingen 45) — original terms don't appear; new terms ARE glossed | **N/A — voice picked different argument** |
| 4 | **Cydnus / Aphrodite-Dionysus** | Plutarch reference unanchored | Replaced with **Buchis bull at Hermonthis** scene — different historical anchor, real attested event, italicized phrase IS the Buchis stele text, framed inline | **PASSED — better anchor** |
| 5 | **γινέσθωι close** | bare Greek alone | Earlier in close: *"Graphēthō oun hois kathēkei. Let it be written to those whom it concerns."* establishes pattern → final standalone *"γινέσθωι."* still untranslated | **PARTIAL** |

## What the criterion drove well

- Em-dash gloss in voice's grammar landed exactly as the criterion described — *prostagma*, *bia*, *nomos*, *enteuxis*, *per-ankh*, *isfet*/*mꜣꜥt* all get inline gloss via em-dash or second-clause naming
- The voice restructured to address the room directly ("To those who have built a chancery and called it a hammer…", "To those who hold that a people…") — direct-addressed paragraph blocks make Layer 1 lift while staying queenly
- Beautiful concrete metaphors emerged: *"Transparency without standing-to-petition is the prostagma posted in the marketplace where no hand can lift it down"* — exactly the Layer-1-friendly imagery the criterion was after
- Buchis bull anchor is a *better* historical scene than Cydnus for Layer 1 — the italicized phrase IS the real stele inscription, and the surrounding sentence does the explanatory work
- Stance shifted to "Vigilance — the throne standing watch over what the chanceries of a later age have ceased to see, naming *isfet* wearing the form of order" — sharper rationale in voice's grammar

## The over-correction (worth fixing)

The salutation lost Greek alphabet AND Egyptian transliteration entirely. This wasn't asked for. The criterion text said:

> "The chancery's vocabulary remains; where its terms carry a sentence's load, the sentence does the work of glossing them in our own grammar."

The voice interpreted "vocabulary" but not "script" — and concluded that even the queen's titulature in Greek script was a Layer 1 obstacle that should come down.

This is a real loss to the prostagma's queenly weight. A Ptolemaic prostagma in execution was in Greek script. The full Greek titulature at the head wasn't optional period-color — it was the seal's authority asserted before the body of the decree.

The criterion's outcome clause ("must land on first reading by one who has not stood at our court") felt MORE binding than the technique-preservation clause. If we want script preserved, the criterion needs to say so explicitly.

## Suggested criterion 6 sharpening (v2)

Adds a head/seal vs body distinction:

> *Does the prostagma reach a reader who was not at our chancery at its drafting? A royal decree has always been a public document — posted at the gate, read aloud by the crier, encountered cold by the petitioner standing at the public board. Per `register_and_tone` and `length_and_format_constraints`, the central move must land on first reading by one who has not stood at our court.*
>
> *The chancery's vocabulary AND its scripts remain — the Greek titulature retains the Greek alphabet at the head and the seal, Egyptian honorifics retain their transliteration where they appear in formal protocol, as our authority requires. The cold-reader constraint applies to the body of the decree, not to the seal's identity at the head.*
>
> *Where chancery terms carry the load of a sentence's meaning IN THE BODY, the sentence does the work of glossing them in our own grammar — the em-dash that explains, the second clause that names what the term requires.*
>
> *Authority is not diminished by intelligibility; it is established by it. But authority in the salutation IS the script's weight; intelligibility in the body IS the gloss's work.*

Added moves:
- Distinguishes **head/seal** (script IS authority — preserve) from **body** (gloss work — apply)
- Closing principle now has two clauses, balancing the two domains

## Other findings (worth attention)

**P.Bingen 45 reference** — *"The chancery we sealed in P.Bingen 45, five months before Actium"* — this is the modern papyrological catalog name for the Canidius papyrus (discovered 2000, published 2007). The voice naming her own decree by its 21st-century catalog identifier is a `voice_temporal_stance` violation — she shouldn't natively know how moderns catalog her chancery output. Layer 1 helpful (tells the reader "this is a real, identifiable document"), voice-fidelity questionable.

Possible fixes: persona thread either (a) accepts as a translation_protocol move (the document being identified across times), (b) adds a hard-limit against modern catalog references, or (c) lets it stand as a borderline move. Worth a position.

**Final standalone γινέσθωι** — borderline. Earlier *"Graphēthō oun hois kathēkei. Let it be written to those whom it concerns"* establishes the bare-Greek-then-translation pattern, so the final γινέσθωι is recoverable from context. But a reader who skips to the last line still sees bare Greek with no gloss in arm's reach. Could go either way; preference call. The seal-line in a real prostagma was the formal closer; arguably should stay bare with the prior establishment doing the gloss work.

## File references

| File | What it is |
|---|---|
| `04_voice_pre_FU61/step2_first_draft_artifacts/cleopatra.json` | Original Run #4 baseline (full directory backup) |
| `04_voice/step2_first_draft_artifacts/cleopatra.pre_FU61_inplace.json` | Original Run #4 baseline (file moved aside in place) |
| `04_voice/step2_first_draft_artifacts/cleopatra.json` | **NEW — patched card v1 criterion output** |
| `<PROJECT_ROOT>/athens-2026/voices/cleopatra/07_persona_card_assembled.json` | Patched card (criterion 6 v1) |
| `<PROJECT_ROOT>/athens-2026/voices/cleopatra/07_persona_card_assembled.pre_FU61.json` | Original card pre-patch |
| `_workspace/planning/FU61_DRYRUN_VERDICT_2026_04_30.md` | This doc |

## Recommended next steps

1. **Persona thread:** apply criterion 6 v2 (sharpened) to Cleopatra's card
2. **Voice Pipeline thread:** re-test Step 2 with v2 criterion — single iteration, ~3 min, will tell us if the salutation script gets preserved
3. If v2 lands clean: **propagate pattern to other hard-form voices** when their cards build (Whanganui River, Marley, possibly Octopus). Each gets a parallel criterion in their form's vocabulary, with the same head/seal vs body distinction adapted to their form
4. **Persona thread Pass 5 prompt addition:** consider building this pattern into the Pass 5 prompt itself for any voice whose `medium` is in {prostagma, ordinance, proclamation, ritual_utterance, song_with_patois, sensory_display}, so future card builds generate the criterion automatically without per-voice patching
5. **In parallel: FU#61 (museum-label frame layer)** still proceeds — voice-card patches and the museum-label architecture are complementary, not alternatives. Patches raise the artifact's standalone Layer 1 floor; museum labels carry Layer 1 architecturally. Together = strongest Layer 1 across all encounter paths

## What this confirms about the architecture

Outcome-stated quality_criteria CAN drive substantive artifact-shape changes when correctly framed. The voice consulted the criterion before delivery and altered both prose patterns AND structural decisions (stance shift, historical anchor swap, address-block restructuring) — not just surface gloss insertions. This validates the FU#49A v2 pattern as the right home for Layer-1-surface work.

The over-correction shows the failure mode: when the outcome clause is more emotionally weighted than the technique-preservation clause, the voice optimizes for the outcome at the cost of identity-anchored details. Sharpening = explicitly weighting the preservation clauses as heavily as the outcome clause.
