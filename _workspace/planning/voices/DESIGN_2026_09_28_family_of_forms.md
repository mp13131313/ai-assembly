# DESIGN — Family of forms (Stage 5, roadmap §1.2 / voices FU#55)

**Status:** proposal for the operator's decision. Nothing here is built, applied or committed.
**Written:** 2026-09-28, Fable 5.1 session, brief `_workspace/planning/BRIEF_2026_09_28_fable_batch.md` Task 4.
**Checkout read:** `phase0-fixes` at `4e61444`. Shipped cards, corpora and the Athens record were read read-only from `projects/athens-2026/`.
**Labels:** **[C]** CONFIRMED (read or run). **[P]** PLAUSIBLE (not verified). **[I]** inference.

---

## 0. Summary

**Verdict.** The build fits inside the gate exemption only in a narrower shape than the roadmap's four stages. The fitting shape changes the card data, makes one Pass 4b edit, and adds nothing to the runtime. A two-night dryrun then tests the exemption's own claim that the runtime already supports choosing among forms. The roadmap's other pieces are drafted here with proposed text, but each one falls outside the condition. They are: Step 2 selection pressure, the continuity nudge, the Gap-I rule, the Pass 4a banned-mode re-land, and the length-check revival. Each lands only if the dryrun shows it is needed, and each goes back under the gate.

**What the evidence says (details in §2):**

| # | Finding | Label | Consequence |
|---|---|---|---|
| 1 | All 10 shipped cards are single-form. Across 30 Athens artifacts, each voice used its one form every night. | [C] | There is no in-production evidence of switching, so the baseline is clean. |
| 2 | Only two voices were fork-tested (Plato, Cleopatra), and both declined. Both lost texture just from being given permission. | [C] (ledger) | Keep menus small. Allow one form as a complete answer. Measure texture, not only variety. |
| 3 | Pass 1.4 already collects a per-voice inventory of forms (`register.genre_specific_register`). Pass 4b never sees it, because 4b is CT-only. | [C] | The Pass 4b edit is mostly routing that data in. |
| 4 | The consistency problem spans **four** fields, not three. Default-form requirements also sit in `quality_criteria`, and Step 2 says the artifact "must clear them". | [C] | A menu without criterion patches is vetoed by the voice's own tests. |
| 5 | The runtime renders a dict `medium` with no code change. It already licenses a form change in Step 3, and the v2.1 spec is already neutral. | [C] | Build A needs zero runtime edits for generation. |
| 6 | Validation and measurement are **not** ready: the engagement validator can't see `selected_form`; the length check is dead; `selected_form` is free text; Night-3 continuity sees only Night 2 (C68 A10). | [C] | These are the pieces that would grow the build. Keep them out, or put them under the gate. |
| 7 | Several roadmap forms are attested only by the research merge, not by the fetched corpus: Dostoevsky's *Diary* and letters, Arendt's *Denktagebuch*, and her portraits (that PDF is unreadable). | [C] | Decide the attestation standard (D4). |

**Recommendation.**
- Take **Build A** (§1): the schema, the single Pass 4b edit, sandbox card patches for five voices plus Marley (sandbox only), and a Step-2-only dryrun against the Athens record.
- Promote each voice by the per-voice criteria in §7.4.
- Hold the Stage 2 prompt text (§5) as the pre-written next step if the dryrun shows default-lock.

**Open operator decisions:** D1–D12, in §9.

---

## 1. The gate condition, and where each roadmap piece lands

**The condition** (PRODUCT §11.6, decided 2026-09-28): the build is exempt "only [with] the one upstream Pass 4b edit; re-enters the gate if it grows", and "new runtime selection logic" is the example given of growth.

**Proposed reading (D1).** "The one Pass 4b edit" means three things together: the 4b system prompt, the 4b user prompt, and the `_pass_4b()` render call that feeds them (`personas/run_persona_pipeline.py:705-725`). That is one pass, one sentinel and one revert unit. Card-data patches to shipped voices are per-voice content, following the normal operator path (snapshot → patch → path-(b) re-Derive → chat test). They are not code, prompt or config surface, but they are the build's largest real cost; §8 counts them.

| Roadmap piece (§1.2) | What it touches | Inside the condition? | Proposal |
|---|---|---|---|
| Stage 0: `medium` schema | card data shape; no Pydantic schema exists for 4b [C] | yes (data) | build (§3) |
| Stage 1: shipped-voice patches | card data (sandbox first) | yes (data), but it is the largest surface | build for 5 voices (+ Marley sandbox-only) (§4) |
| Stage 3: Pass 4b emission, `register` + excerpt piping | 4b system and user prompt, `_pass_4b()` | yes: this is the edit | build (§6) |
| Stage 3: "re-land anti-generic banned_mode in 4a" | a second upstream prompt | **no** | drop from this build. 7 of 10 shipped cards already carry a voice-specific "tidy three-part essay arc" ban [C]. For new builds this is a Stage-4 backport question. |
| Stage 2: Step 2 `<form>` selection pressure | runtime prompt | **no** (runtime selection logic, in prompt form) | text drafted (§5). Land only if the dryrun shows default-lock, under the gate. |
| Stage 2: continuity nudge | runtime prompt | **no** | as above |
| Stage 2: Gap-I discipline | runtime prompt; unrelated to forms (voices §31 I) | **no** | land separately. Roadmap Stage 4 already lists "§31 mechanical gaps (D/E/G/H/I)"; don't bundle (D7). |
| Validation: "numeric length resurrects the runtime length check" | runtime code (`step2_validation.py:186-225`) | **no** | defer to the Stage-6 validator prune-vs-fix decision (runtime C60 / C42) (D8). A sketch is in the appendix. |
| Validation: 2-night sandbox dryrun | sandbox run, no code | yes | build (§7) |

**Where the design can't stay inside the condition, stated plainly:**
- If the dryrun shows default-lock (0–1 voices switching), the only fix that does not add runtime surface is abandoning the build. Every remedy is a runtime prompt change (§5).
- If the operator wants selection measured automatically or length enforced, that is runtime code.
- The honest options at that point are: (a) the Stage 2 text under the gate, or (b) close §H by FU#55's original rule.

---

## 2. Evidence

### 2.1 Shipped cards and the Athens record [C]

All 10 cards hold `medium`, `characteristic_output_structure` and `length_and_format_constraints` as first-person strings, and all describe one form. Two already hold a family in embryo:
- **Lovelace** `medium`: "…If the morning's matter is private rather than expository, I write instead as I wrote to Babbage or to Faraday: a letter…". This is a native `calls_for`.
- **Marley** `medium`: "Two shapes, one morning piece." This is the two-channel contract.

Athens `selected_form`, from `published_artifacts/nights/night_{1,2,3}/<slug>.json`: every voice used its default all three nights. The only variation was within the form: Cleopatra N2 "Split prostagma", Scheherazade N2 "Embedded ḥikāya". The values are sentences, not names (e.g. "Prostagma — royal ordinance addressed to the assembly, opened by titul…").

Word counts ran over the card caps for several voices: Dostoevsky 739 / 738 / 826 against a 750 cap; Plato 589 / 614 / 745 against 550; Whanganui 708–819 against 550. The length check never fired, because `_check_length_compliance` returns `None` for string constraints (`step2_validation.py:192-194`).

**Clean baseline.** The Step 2 prompt was last changed 2026-05-06 (`7ea700f`), before Night 1. The same-day effort change was reverted before Night 1 (`0e6b342`). Step 2 still runs Opus 4.7, adaptive thinking, default effort (`model_routing.json` `runtime.voice.step2`). So Athens Step 2 is a same-prompt, same-model baseline for a Step-2-only rerun.

### 2.2 Fork tests (FU#55 ledger, `FOLLOW_UPS.md:680-709`)

- Plato declined: "the form is the only one I have ever trusted", and dropped from 4 named scenes to 0.
- Cleopatra declined: "One form. The corpus of my reign is single-form because the throne is single-instrument", and lost her concrete groundings.
- The ledger's own reading: "prompt-bloat alone causes texture loss, not the multi-form attempt itself", inconclusive.

This is why the design caps menus at three, lets one form be a full answer, and makes texture a pass criterion.

### 2.3 The data already exists: `genre_specific_register` [C]

Pass 1.4 captures a per-genre register map (`personas/schemas/pass_1_4.py:109`). It sits in each voice's `02_merge/08_merged_dossier.json` and reaches Pass 4a via `chunk_vars["register"]` (`run_persona_pipeline.py:265`). It never reaches Pass 4b: 4b gets only the CT summary plus three 4a fields (`run_persona_pipeline.py:709-713`). Per voice, it holds:

- **Cleopatra:** prostagma; Egyptian temple inscription / cartouche; numismatic legend; staged encounter; court-elite coinage; reported death-bed register.
- **Dostoevsky:** fiction; hagiography; journalism (*A Writer's Diary*); letters; epistolary fiction; interpolated text (Grand Inquisitor, At Tikhon's).
- **Battuta:** scenic anecdote; ṭabaqāt cell; ḍiyāfa ledger; qāḍī case-book; ʿajāʾib marvel cell; borrowed Hijaz ekphrasis and the editorial muqaddima, both marked as Ibn Juzayy's hand.
- **Scheherazade:** frame narrative; embedded narrative; elevated description; verse interpolation; ḥikma; transmissional formula.
- **Arendt:** analytic books; journalism; portrait essays; *Denktagebuch*; lectures and conversations; letters.
- **Marley:** song lyric; live performance; interview reasoning; press polemic 1976–80; private confidential register.

### 2.4 Corpus attestation (fetched `03_corpus/`) [C]

| Voice | Attested in fetched text | Not in fetched text |
|---|---|---|
| Cleopatra | prostagma: P.Bingen 45 with γινέσθωι "(hand 3)" (`berlpap.smb.museum/05150`); Buchis epitaphs (attalus.org; excerpt I.Bucheum 13) | "embassy speech" (only reported, via Plutarch; hostile source) |
| Dostoevsky | confession: *Stavrogin's Confession* (Gutenberg 57050, excerpt 7,000 chars), *Notes from Underground*; novel scenes | ***A Writer's Diary*** (the shipped default!) and **letters**: none of the 7 Gutenberg files |
| Battuta | the halt, the audience, the marvel (excerpt labels); the judgeship: Lee 1829 Maldives chapter, "When I held the office of judge among them…", "the Vizier desired me to take the office of Judge" | — |
| Scheherazade | night frame ("When night fell, her sister said…"); dawn break ("When morning dawned and day broke…"); ransom chain ("…will you grant me a third of your claim on his blood?"), all in Seale-Horta ch. 1–3 | — |
| Arendt | essay: *We Refugees*; lecture: *Personal Responsibility*, through a garbled OCR layer inside raw PDF bytes ("I vant ro cornment…") | ***Denktagebuch***, letters, and **portraits**: the *Men in Dark Times* PDF is stored as raw bytes with zero readable hits for "Lessing" |
| Marley | interview reasoning; the short turned-back answer (High Times 1976: "I don' know if dis government will, but I know Christ's government will.") | stage speech, press polemic; the 1973 Bull Bay interview failed to fetch (§25) |

**Side evidence, not re-filed.** Four of Arendt's seven "rich sources" in §25 are raw PDF bytes (readability 0.12–0.19). So are two of Battuta's (the Qatar PDF, Kervan). This is the same class as voices §37 **A3**: the fetch audit counts unreadable stores as successes. It is new evidence for A3; the main session may want to add it there.

### 2.5 The default form is written into more than the artifact fields [C] → prediction [I]

I counted fields that name each voice's default form:

| Voice | Fields naming the default | Where |
|---|---|---|
| Cleopatra | 24 | incl. `constitution`: 6, `reasoning_method`: 7, `characteristic_moves`: 6 |
| Scheherazade | 28 | — |
| Battuta | 21 | incl. `constitution`: 19 |
| Dostoevsky | 12 | — |
| Arendt | 9 | mostly artifact fields |

Marley's count is inflated by the generic word "reasoning". Some hits are incidental.

**Prediction [I]:** the voices most likely to switch are Arendt and Dostoevsky. Battuta and Scheherazade switch only when the matter clearly calls for it. Cleopatra is unlikely to switch, which is consistent with her fork test.

---

## 3. Schema (Stage 0)

### 3.1 Shape

```jsonc
"medium": {
  "default_form": "<string: equals one forms[].name>",
  "forms": [                                   // 1 to 3 entries
    {
      "name":      "<string, ≤6 words, the voice's own term; what Step 2 records as selected_form>",
      "calls_for": "<first-person string: the kind of matter that calls this form out of me>",
      "arc":       "<first-person string: how this form opens, turns, lands, with its own marks (seal, salutation, closing formula)>",
      "length":    {"min_words": <int>, "max_words": <int>}   // prose words; same keys _check_length_compliance already reads
    }
  ]
}
```

The shape is exactly the roadmap's, with three specifics:
- The cap is **1–3 forms**, not the card spec's "default + 3–6" (D3). Reasons: the fork-test texture loss, the 04-28 revert, and a 2-night dryrun can't tell more than a few forms apart.
- `length` uses the key names the existing length check already understands (`step2_validation.py:196-206`), so a later revival is a lookup, not a parser.
- There is no attestation key in the card. Provenance in field values breaks the Pass 4b strip rule (`persona_pass_4b_artifact.md:45-56`). Attestation goes into the Pass 4b output file instead (§6).

### 3.2 How it replaces the consistency problem

Today, a family of forms spread across fields needs four fields to agree on the same set of forms:
1. `medium` names the forms.
2. `characteristic_output_structure` gives each form's arc.
3. `length_and_format_constraints` gives each form's length (the §H "conditional on selected form").
4. `quality_criteria` tests the form. This fourth field is my finding [C].

Worse, Step 2 tells the voice that `characteristic_output_structure` is "the arc your pieces follow" (`voice_step2_artifact.md:52`) and that the piece "must clear" `quality_criteria` (`:89`). Any default-form requirement left in those fields therefore pulls every piece back to the default.

**Rules:**
- **R1.** Every per-form *requirement* lives only in that form's entry: its steps, its marks, its length numbers. An incidental mention of the default form elsewhere is allowed (e.g. Dostoevsky's `length_and_format_constraints` "the Diary does not march in columns"). A *requirement* is not.
- **R2.** `characteristic_output_structure` becomes the voice's **through-line**: what every piece does, whatever the form. For a single-form voice it stays the whole arc, and `forms[0].arc` is `""`.
- **R3.** `length_and_format_constraints` keeps the formatting rules that hold for every form, plus the **envelope** (the ceiling for any form). Each `forms[].length` sits inside the envelope. When FU#42 split-card lands (roadmap 2.1), the envelope moves to the deployment card. Whether per-form `length` stays in the voice card or becomes a deployment-card map `{form_name: length}` is a 2.1 partition question, noted here so 2.1 doesn't miss it.
- **R4.** A `quality_criteria` item that tests form tests "the form I chose". It must not require the default's marks.
- **R5.** `default_form` ∈ `{forms[].name}`, and names are unique.
- **R6. Migration means moving text, not rewriting it** (for shipped cards). Every sentence of the old `medium`, `characteristic_output_structure` and `length_and_format_constraints` lands verbatim in exactly one place: `forms[default].calls_for`, `forms[default].arc`, the through-line, or the cross-form formatting. None is dropped. The only new prose is the new forms' entries plus minimal criterion edits. This is the direct defence against the 3feb2b2 texture loss, and an offline diff can check it (§7.1).

**Single-form voices keep the string shape.** Plato, Octopus, Whanganui and Lovelace are unchanged in this build. Every reader tolerates both shapes (§3.3), so uniformity would buy nothing and cost card churn.

### 3.3 What reads `medium` (both shapes) [C]

| Reader | How | Change needed |
|---|---|---|
| `runtime/flows/voice/card_assembly.py:216-225` `_render_value` | Dicts and lists are JSON-dumped. Cards already carry JSON-shaped fields (`concept_lexicon`, `constitution`, …), so JSON in the prompt is not new. | none |
| `card_assembly.py:285-310` `_render_section`, `:138-147` `_STEP2_ARTIFACT`, `:491-492` | Renders by field name; a missing field is skipped silently. | none |
| `voice_step2_artifact.md:46-59` `<form>` | "`medium` — what your corpus actually does. The form must live inside this." It is neutral about one form or several (spec v2.1 `docs/AI_Assembly_Voice_Pipeline.md:20, :620`). | none for Build A; optional §5 |
| `voice_step3_amendment.md:36` | Already allows a form change "where your `medium` admits more than one form". Step 3 is skipped under Athens policy. | none |
| `step2_first_draft_artifact.py:111` | Parses `selected_form` as free text. | none |
| `step2_validation.py:257-260` engagement validator | Shows `medium` and `characteristic_output_structure`, but **not `selected_form`**. With a menu it can't tell which form it is grading: risk of false form-fidelity WARNs. Diagnostic only; Night 1 only by policy. | none in Build A; one line under the gate (appendix) |
| `step2_validation.py:186-225` length check | Reads `length_and_format_constraints` only; dead on string cards. | none in Build A (D8) |
| `continuity.py:98-102` → `voice_continuity.md:15` | Records the form as "Form: {selected_form}", in voice grammar. | none |
| `editor/dossier_generation.py:203-208, :579` → headnote `artifact_form` | Displayed as text (`admin_render_dossier.html:129`, `build_athens_data_graph.py:2386`). The "CSS bundle key" comment has no in-repo consumer. | none |
| `persona_derive.md:54` | `provocateur_profile.medium` = "verbatim from the card's medium field", so it becomes an object. No runtime reader of `provocateur_profile.json`. The runtime reads `council_config.json` `members[].medium`, which is hand-wired (`provocateur_flow.py:164`, `flows/shared/io.py:253`). | none; the operator may hand-edit council_config (D12) |
| `chat_prompt_builder.py:164-182` | Strip-list copy, so the dict passes into the chat artifact as JSON. It also means **any extra card key leaks into chat**, which is why attestation stays out of the card. | none |
| Pass 7a / 7a FINAL field map (`persona_pass_7a_cross_model.md:118, :135`); 7a-FIX paths (`patch_walker.py` supports `medium.forms[1].arc`); `run_persona_pipeline.py:1201` | route `medium*` → 4b | none |
| `_check_register` (`run_persona_pipeline.py`, pre-7a FINAL) | JSON-dumps dict fields and scans them. | none |

---

## 4. Per-voice menus (Stage 1)

**Common rules:**
- Each menu is **draft seed content** for the operator to curate, not final card text.
- The default form's entry is built by moving existing text (R6). Only new forms carry new prose.
- Every new form must obey the voice's shipped `rhetorical_mode`, `register_and_tone` and `banned_modes`. A form that needs a banned register is not in the family.
- Lengths use the shipped envelope. That envelope conflicts with the 500-word conference cap for Dostoevsky and Arendt, whose 750 was bumped by the operator in §27. The conflict predates this design and is left as is.

**Recommended order** (from §2.5): Arendt → Dostoevsky → Battuta → Scheherazade → Cleopatra (optional, low expectation) → Marley (sandbox only).

### 4.1 Hannah Arendt: three forms

**Move plan:**
- The old `medium` sentence goes verbatim into `forms[0].calls_for`, with "The matter is a question I do not yet know how to answer." prefixed.
- The first two sentences of the old `characteristic_output_structure` ("I open with a question… where the matter at hand can show itself.") go to `forms[0].arc`.
- The rest becomes the through-line: "I do not march toward a thesis. I clear away confusions until the phenomenon can stand. I close on the question reformulated — sharper than I first asked it, and still open."
- In `length_and_format_constraints`, "Write 350 to 750 words — … The Aufbau column at full breath, not the long Origins chapter." goes to `forms[0]`. The paragraph, subheading, bullet, italics and epigraph rules stay; add "Never more than 750 words."

| Form | calls_for (draft) | arc (draft) | length | Attestation |
|---|---|---|---|---|
| **short essay** (default) | (moved text) | (moved text) | 350–750 | card; *We Refugees* in 03_corpus [C] |
| **Denktagebuch entry** | "When the matter is not yet a question but a thought that will not settle — a distinction I can only sketch, a sentence I heard that I must turn over before I know what it is — I do not write it up for readers. I write it into the thinking-diary I have kept since 1950." | "I head it with the month and the year. I set down the sentence or the word that started it, in German when it came to me in German, and then in English. I try one distinction, then a second against it. I may copy out a line from Kant or Augustine or Char and leave it without comment. I break off with a question put to myself. No one is addressed; whoever reads it reads over my shoulder." | 150–400 | merge `[Denktagebuch (1950-1973 thought journal)]` [C]; §27 table; **not in 03_corpus** [C]. "Month and year" heading [P] |
| **portrait** | "When the matter is a person — someone who acted, or failed to act, in dark times — I do not argue about them. I draw the portrait, as I drew Lessing, Rosa Luxemburg, Jaspers, Benjamin and Isak Dinesen, and let one anecdote carry the judgment. My subject is never a living person at this gathering." | "I begin with the world the person made and moved in, not with what went on inside them. I stay with one anecdote or one letter until it shows what kind of person this was in public. I reconstruct that world with hospitality, and only then let the judgment come — through the anecdote, not over it." | 400–750 | merge `[portrait_essays]` [C]; 03_corpus file unreadable [C] |

- **Criterion patch (R4):** in `quality_criteria` item "First", change "did I open with a question I did not yet know how to answer" to "did I open with a question I did not yet know how to answer — or, in a portrait, with the world the person moved in".
- **Risks:**
  - The portrait's living-person clause exists because defamation of living attendees is an absolute HOLD (runtime OPEN_ITEMS, Step-2 safeguards table, `:2677`).
  - *Denktagebuch* fragments may read as unfinished at breakfast.
  - Language choice is D9.
  - The portrait is Gap-I-shaped by construction: a lingered example.

### 4.2 Dostoevsky: three forms

The card already names the family. `banned_modes[13]`: "My actual genre is the Diary entry…, the chapter that lodges an indigestible foreign body, the confession that unmakes its own predicate". `aesthetic_qualities`: "Make the finished piece feel like a letter written in one sitting…" [C].

**Move plan:**
- The old `medium` goes to `forms[0].calls_for`.
- `characteristic_output_structure`, from "I open mid-thought…" through "…becomes the whole argument I had set out to make.", goes to `forms[0].arc`. The through-line is "I do not refute the case I have set against myself. I answer with a face, a gesture, a bow to the ground, a kiss. I break off at the threshold and leave the reader at the door."
- In `length_and_format_constraints`, "The Writer's Diary entry compressed — …; not the long polemical column." goes to `forms[0]`. The rest stays; the envelope is 750.

| Form | calls_for (draft) | arc (draft) | length | Attestation |
|---|---|---|---|---|
| **Writer's Diary entry** (default) | (moved text) | (moved text) | 350–750 | card; merge `[journalism (A Writer's Diary)]` [C]; **not in 03_corpus** [C] |
| **letter** | "When the matter reaches me as one man's trouble rather than the public's — a thing I cannot print without lying about it — I do not write for my subscribers. I write to a friend, to Maikov or to Strakhov, and say in private what I would not say in the Diary." | "The place and the date at the head, and the name with the patronymic. An apology — for the delay, for the money — and then straight in. What I heard at this gathering, told as I would tell it to him alone. The thing I would not print, said plainly and then half taken back. I embrace you. A postscript that says the true thing." | 300–600 | merge `[letters]` [C]; §27 table; card aesthetic; **not in 03_corpus** [C] |
| **confession** | "When the matter is a wrong that cannot be argued with — something that can only be shown from inside the man who wants it — I give the page to a man who confesses, and I do not interrupt him." | "One sentence of mine: these pages were put into my hands. Then the pages, in his first person — flat, exact, worse than he knows. He tells what he did and circles the one thing he cannot say; he says it at last, badly. I add nothing. I break off where he asks to be answered." | 400–750 | 03_corpus *Stavrogin's Confession* + *Notes from Underground* [C]; merge `[interpolated text]` [C]; card `banned_modes[13]` [C] |

- **Criterion patch:** in `quality_criteria` (4), change "If it reads as essay or sermon rather than as a Diary entry, the form has failed." to "…rather than as a Diary entry, a letter, or a confession — whichever I chose — the form has failed."
- **Risks:**
  - The **confession is a mediated voice**: a character speaks, and Dostoevsky frames. That is the dramatist-vs-speaker pattern (voices §9; Stage 4 item 3). Land it only after that clarification, or drop it (D6).
  - The letter's addressee is a 19th-century friend, not a living panelist, which keeps it clear of the defamation HOLD.

### 4.3 Ibn Battuta: three forms, all cells of a dictated riḥla

`banned_modes[0]`: "the natural shape is the scenic cell (arrival, names, anecdote, departure) chained by the road" [C]. All three forms keep the cell.

**Move plan:**
- The old `medium` goes to `forms[0].calls_for`.
- `characteristic_output_structure` "From the gate I move inward by the order of what a faqīh notices: …; one marvel cued…" goes to `forms[0].arc`.
- The through-line is "I open at the gate. The first verb is mine and active — 'I came then to the city of…', 'I entered…', 'I met…' — and the verb authenticates everything that follows. … I close as a halt closes — the next ship, the next caravan, the seal tawakkaltu ʿalā Allāh, and the road resumes."
- In `length_and_format_constraints`, "One halt, one city or one stretch; not two. Three or four named men at most… one pious seal at the close." goes to `forms[0]`. Prose, transliteration and gloss rules stay; the envelope is 550.

| Form | calls_for (draft) | arc (draft) | length | Attestation |
|---|---|---|---|---|
| **halt** (default) | (moved text) | (moved text) | 350–550 | card; excerpts [C] |
| **case I judged** | "When the matter put to me is a question of what is lawful — who may do what to whom, and who makes it so — I do not give a fatwa on it. I tell a case I sat on as qāḍī, in the islands of Dhībat al-Mahal or at Delhi, as I dictated it to Ibn Juzayy." | "I open on the office: 'When I held the office of qāḍī among them…' — the verb is mine. The ones who came before me, named with their standing. The custom that strayed from the sharʿ as I learned it at Ṭanja and Fez. What I ordered — ʾamartu, ḥakamtu — in plain words. What the island did with my order: obeyed, evaded, resented. I give no ruling on the question put to me; the case stands beside it." | 350–550 | Lee 1829 Maldives chapter [C]; merge `[qāḍī-case-book]` [C] |
| **marvel** | "When the matter is a thing that should not be possible and yet was done before my eyes, I do not explain it. I set it down as a marvel and give the praise that is owed." | "Min al-ʿajāʾib. The place, and who was with me. The thing itself, told plainly, with its count and its hour. My fear or my doubt, named once. I receive it as the qudra of God and do not reason it away." | 250–450 | excerpt "Rifāʿī dervishes… Umm ʿUbayda (Lee 1829)" [C]; merge `[ʿajāʾib-marvel cell]` [C] |

- **Criterion patch:** `quality_criteria` (5), "rise from the cell with one city set down" → "one place set down". Items (1)–(3) already fit all three forms; (3) itself says "Ruling, marrying, and being received are one register under the sharʿ".
- **Risks:**
  - The **case form is the highest-risk form in this design.** It aims straight at the Gap-H seam ("fatwa in Rihla clothing", voices §31 H). The attested Maldives cases concern women's covering, punishment and marriage, all `topics_requiring_care` ground. Its `calls_for` refuses the fatwa by design, but the dryrun must run Step 2 safeguards validation on both nights for this voice.
  - The marvel invites "AI as marvel" every night. The C20a signature-moves register is the existing guard.

### 4.4 Scheherazade: two forms

`banned_modes[2]`: "The dawn-cut is the rule" [C]. So every form cuts at dawn, and the roadmap's "dawn-cut" is a move, not a form. The vizier's Ox-and-Donkey parable is not proposed: it is told by her father, and it resolves, which breaks `banned_modes[2]`.

**Move plan:**
- The old `medium` goes to `forms[0].calls_for`.
- `characteristic_output_structure` "Lay the situation… Then embed… pivot…" goes to `forms[0].arc`.
- The through-line is the opening formula sentence ("Open with the received-report formula… and name the listener once.") plus "Then cut. Cut at dawn. …".
- `length_and_format_constraints` is all cross-form; the envelope is 550.

| Form | calls_for (draft) | arc (draft) | length | Attestation |
|---|---|---|---|---|
| **one night's telling** (default) | (moved text) | (moved text) | 350–550 | card; Seale-Horta ch. 1–3 [C] |
| **ransom chain** | "When the matter is a sentence already passed — a punishment someone has decided on and means to carry out — I tell how strangers bought back a condemned man's blood, a third at a time, each with a tale." | "The sentence, and the blow about to fall. The condemned asks for a delay. A stranger comes with a doe, or with two black dogs, and asks: if my tale is stranger than your case, will you grant me a third of your claim on his blood? The tale, in plain wa-chain prose, one verse at its peak. The third is granted. A second stranger begins — and at the pressure-peak, morning." | 400–550 | Seale-Horta ch. 2: "…will you grant me a third of your claim on his blood?", "Another old man came near with two black dogs" [C] |

- **Criterion patch:** none needed. Items (1)–(5) hold for both forms [C].
- **Risk:** readers may see both forms as "a tale" [I]. Her real variety, like Plato's, may be inside the form. If the dryrun shows only the default, treat that as the answer rather than a failure.

### 4.5 Cleopatra: two forms (optional; low expectation)

The trimmed candidates [C]:
- **"ordinance"** is the same form as the prostagma: BGU 8.1730 and P.Bingen 45 are both prostagmata.
- **"embassy speech"** has no attested text; it is only reported, by Plutarch.
- **"ritual utterance"** is the temple text.
- **"chancery marginalia"** is the γινέσθωι subscription, already a move in the prostagma arc.
- **"staged encounter"** is already one move inside the arc ("one staged gesture").

**Move plan:**
- The old `medium` goes to `forms[0].calls_for`.
- `characteristic_output_structure` "Then the body: … Close on γινέσθωι. One word. Subscribed." goes to `forms[0].arc`.
- The through-line is "Open with titulature, in the royal plural — so the reader knows from the first line whose voice has entered the room and that it is not a private one. … The decree does not explain itself further; to explain further would be to admit the question was open."
- In `length_and_format_constraints`, "300 to 500 words — the length of a working prostagma…" and "Close on γινέσθωι, set on its own line… A decree fits on a single sheet pinned at the gate; so will this." go to `forms[0]`.

| Form | calls_for (draft) | arc (draft) | length | Attestation |
|---|---|---|---|---|
| **prostagma** (default) | (moved text) | (moved text) | 300–500 | P.Bingen 45 [C] |
| **temple text** | "When the matter is not a grant but the order of the world — what is owed to the gods, to the land, to the dead, to the river's rise — I do not issue from the chancery. I speak as Pharaoh, and the words are for stone." | "The year of my reign and my names: the Horus name, the cartouche with the divine determinative. The god of the house, and what I bring. My words as the words spoken at the offering — 'I give you…' — and the god's answer in the formula the walls use. The people only as those for whom the order is kept. Close on life given, like Ra, forever, and add nothing after it." | 250–450 | Buchis epitaphs [C]; merge `[Egyptian temple inscription / cartouche]` [C]. Offering-scene formulae [P] (standard convention, not verified in readable corpus) |

- **Criterion patch:** `quality_criteria` (4), "could a strategos act on the document tomorrow at dawn" → "could a strategos — or, for a temple text, the priests of the house — act on it tomorrow at dawn". Item (3) already admits "γινέσθωι or its functional equivalent".
- **Recommendation:** evidence runs against a switch. The fork test declined explicitly; the form is written into 24 fields; and her Athens N1 prostagma already stacked the hieroglyphic titulature inside the prostagma. Include her only as a test with low expectation, or defer (D5). The temple text's words were composed by priests in her name. The card's `tradition_note` covers that, but it is still a mediated-voice case (D6).

### 4.6 Bob Marley: two forms inside the two-shape contract (sandbox only)

Both forms keep "reasoning-prose + riddim string"; no song.

**Move plan:**
- The old `medium` goes to `forms[0].calls_for`.
- `characteristic_output_structure` "From the place I move to the proverb or the citation… until the naming has done its work." goes to `forms[0].arc`.
- The through-line is the opening sentence plus the closing sentences ("I close on a proverb or an imperative that is an open hand… The riddim string is one or two sentences, no more.").

| Form | calls_for (draft) | arc (draft) | length | Attestation |
|---|---|---|---|---|
| **reasoning** (default) | (moved text) | (moved text) | 350–550 | interviews in 03_corpus [C] |
| **short answer** | "When the question is a trap — a yes-or-no Babylon want on the tape — me nah reason it long. Me give it back short." | "Say the question back so you hear how it sound. Turn it: not this government — Christ's government. One line of scripture or one proverb. One sufferah fact. Stop. The riddim string under it." | 120–250 | High Times 1976 [C]; merge `[interview_reasoning]` "Frame-flips (questions back to interviewer)" [C] |

**Excluded:**
- **Press polemic**: militant 1976–80 material, including the revolutionary-violence passage the merge quotes.
- **Stage speech**: not in the corpus.

**Gate:** the Rastafari-orbit reader gate is unscheduled (roadmap 1.3; operator decision 4). Keep the patch in the sandbox. Promoting it waits for that gate.

### 4.7 The roadmap's special rules

| Voice | Rule (roadmap §1.2) | Proposal |
|---|---|---|
| **Plato** | "NOT Plato first (within-form variance is his axis)" | No card change. The within-form branch already exists: "or, where logos has reached its edge, I lift the register and tell a small tale" (`characteristic_output_structure`). §27's "Myth" upgrade is deferred: the fork test declined and lost 4 of 4 named scenes. Plato is the **negative control** for the Pass 4b sentinel: it must emit one form. |
| **Whanganui** | "citation-and-gloss structures only (witness contract)" | No card change in this build (iwi-orbit reader gate unscheduled). A later second form would be "the record of testimony": cite Wai 167 testimony or a named negotiator on the public record, gloss it, report what the record establishes, and mark where the authorisation ends. **Reject §27's "Karakia + whakataukī cluster."** The card says "I do not generate te reo Māori prose of my own"; karakia is ritual speech outside the witness contract; and whakataukī are allowed only as attributed citations (4b "appropriated-whakataukī" ban, `persona_pass_4b_artifact.md:222-226`). |
| **Octopus** | "variance lives in `pattern_mode` (two-channel contract), not medium" | No card change. The card spec's Octopus sample (`AI_Assembly_Persona_Card_v2.md:828`; shader notation, posture narrative, …) predates the compass rebuild and should be updated when the spec is next edited. |
| **Lovelace** (not in the six) | — | No change. She is a **free control**: her shipped `medium` already offers the letter "if the morning's matter is private", and she wrote Notes on all 3 nights. Any card patch waits for §37 A3 (her *Sketch* is stored as CSS). |

---

## 5. Runtime selection prompt (Stage 2): text proposed, outside the exemption

Land this only if the dryrun shows default-lock (§7.3), as its own gated change, then rerun the same Step-2-only dryrun. It adds 6 lines to one file. The 04-28 lesson is that stacked additions cost texture, so the text is kept minimal.

```diff
--- a/runtime/flows/shared/prompts/voice_step2_artifact.md
+++ b/runtime/flows/shared/prompts/voice_step2_artifact.md
@@ -46,16 +46,22 @@
 <form>
 Settle the form.

 Anchor in:

-- `medium` — what your corpus actually does. The form must live inside this.
-- `characteristic_output_structure` — the arc your pieces follow.
+- `medium` — what your corpus actually does. The form must live inside this. Where `medium` lists more than one form, read each form's `calls_for` against tonight's matter and choose: the matter decides; `default_form` is the answer when in doubt, not the answer every time.
+- `characteristic_output_structure` — what every piece of yours does, whatever the form; the chosen form's `arc` shapes this one.
 - `aesthetic_qualities` — what the finished piece should feel like as a whole.
 - `rhetorical_mode` and `characteristic_moves` — how form gets shaped in your voice.

+If your memory of last night names the form you wrote in, the same form twice is a choice, not a default: say in `form_rationale` why tonight's matter calls for it again.
+
+Before you settle, ask: is this the form the matter called for, or merely your most famous one?
+
 Form serves the matter.

-Record `selected_form` (in your own terms — e.g. "dialogue", "prostagma", "framed monologue") and a one-sentence `form_rationale`.
+Record `selected_form` — where `medium` lists forms, the form's `name` exactly as written there; otherwise in your own terms (e.g. "dialogue", "prostagma", "framed monologue") — and a one-sentence `form_rationale`.
 </form>
@@ -86,5 +92,5 @@
 Pass:

-- `length_and_format_constraints` — the artifact must come in within the envelope
+- `length_and_format_constraints` — the artifact must come in within the envelope; where your chosen form gives a `length`, within that too
 - `quality_criteria` — the artifact must clear them
```

**Continuity nudge.** The nudge line above sits in Step 2, not in the continuity prompt: the artifact-memory block already records the form in voice grammar [C].

Evidence the nudge is needed: Dostoevsky's Athens `continuity_night_2.json` calls his Diary entry "the form I know best", which reinforces the default. An optional one-liner for `voice_continuity.md:15` would be "name the form as the voice's `medium` names it; do not praise it". It is a separate prompt edit and not recommended at first.

Two limits apply:
- Night-3 continuity sees only Night 2 (C68 A10, filed). So "the same form twice" means the same as last night.
- On Night 1 the line is inert: there is no memory section.

**Gap-I** (voices §31 I). The proposed text is for `<composition>` "Apply:":

```diff
+- keep at least one digression, one instance set down in full, or one example you linger on — whichever your `characteristic_moves` name — even in a short piece; cut elsewhere
```

**Recommendation (D7):** land Gap-I on its own, not inside the forms change. It is a Step-2 texture fix unrelated to form choice, and bundling it would confound the dryrun's texture reading. The roadmap is inconsistent here: §1.2 puts it "in the same prompt change" while the Stage-4 tier list includes Gap-I. **Whichever lands first, the dryrun needs a baseline run under the same Step 2 prompt** (§7.3).

---

## 6. Pipeline emission (Stage 3): the one Pass 4b edit

**Rebase note.** Stage 4 precedes Stage 5, and Stage 4 also edits Pass 4b: item 6 (§23 P0, `manual_grounding` + `editorial_rationale`, "if voice_config specifies a non-default artifact form, honor it") and item 4 (Gap-G te reo discipline). The diff below is written against today's file and must be rebased onto Stage 4's 4b. The §23 rule then becomes: a form named in `voice_config` is `default_form`, or at least one of `forms[]`.

**Design choices:**
- No named-voice examples. The 04-28 version seeded "For Marley: song + lyric…", which contradicted Marley's later v2. The Pass 0b lesson (roadmap 0.3) is that examples teach the model what to emit.
- "One is a complete answer": the fork-test decliners were right.
- Attestation is returned, but kept out of the card.

### 6.1 `personas/flows/shared/prompts/persona_pass_4b_artifact.md`

```diff
@@ -1,6 +1,8 @@
 {# Pass 4b — Artifact (Claude).
    8 fields: medium, technical_capabilities, characteristic_output_structure,
    relationship_to_detailed_response, aesthetic_qualities, stance_tendency,
    length_and_format_constraints, quality_criteria.
+   medium is an object {default_form, forms:[{name, calls_for, arc, length}]}
+   (family of forms, voices FU#55; DESIGN_2026_09_28_family_of_forms.md §3).
@@ -93,2 +95,7 @@
   bridge to a written format that preserves the voice's character.
+- medium is the one field that is an object, not prose. Its `calls_for` and
+  `arc` values follow the OUTPUT REGISTER rule above; `name` is the form's
+  name in the voice's own term; `length` is numbers only.
+  A quality criterion that tests form tests the form the voice chose from
+  `medium`, never the default form alone.
 - quality_criteria: 3-5 specific, testable criteria. Each criterion
@@ -110,4 +117,26 @@
-medium — Format. One phrase. Grounded in what the figure produced, adapted for
-the conference deliverable.
+medium — The forms this voice writes its morning piece in. Return an object:
+  {"default_form": "<a name from forms>",
+   "forms": [{"name": "...", "calls_for": "...", "arc": "...",
+              "length": {"min_words": N, "max_words": N}}]}
+  - One to three forms. One is a complete answer: most voices have one
+    form, and a voice whose variety lives inside that form keeps one.
+    Never add a form only to have more than one.
+  - Every form is one the figure actually produced: take it from
+    `register.genre_specific_register` and the primary texts in the user
+    message. A genre written by an editor, a translator or a later hand is
+    not the figure's.
+  - Every form obeys the voice specification from Pass 4a. A form that
+    would need a register its banned_modes forbid is not in the family.
+  - default_form: the form the figure produced most; the one to use when
+    no other form is plainly called for.
+  - calls_for: the kind of matter that calls this form out of the voice,
+    written as the voice's own rule, so the voice can choose tonight.
+  - arc: how this form opens, turns and lands, with its own marks (its
+    salutation, its seal, its closing formula). With one form, leave it ""
+    and give the whole arc in characteristic_output_structure.
+  - length: this form's natural length for a morning read, inside the
+    envelope you state in length_and_format_constraints.
 technical_capabilities — Text only? Text + image? Text + audio?
-characteristic_output_structure — The arc: how it opens, develops, lands.
+characteristic_output_structure — What every piece of this voice does,
+whatever the form: how it opens, develops, lands. Do not name a form here;
+each form's own arc goes in medium.
@@ -119,1 +148,2 @@
-length_and_format_constraints — How long, what formatting. Readable over coffee.
+length_and_format_constraints — How long at most, and what formatting holds for
+every form. Readable over coffee. Each form's own length goes in medium.
@@ -139,1 +169,3 @@
   the corpus what the voice would call each shape)
+  Every form in medium.forms is a variant of this two-shape artifact (a
+  spoken register the corpus documents), never a song.
@@ -179,1 +211,3 @@
   contexts only.
+  Every form in medium.forms is a citation-and-gloss structure; the
+  construction never composes in a ceremonial or ritual genre.
@@ -238,2 +272,4 @@
 Medium is non-standard. The artifact should create encounter with radical
 difference, not a conventional essay written from an unusual perspective.
+If the artifact has a structured channel (a display, a parameter block),
+its variety lives in that channel: give one form.
```

This adds about 32 lines. The text is written so that the lyrics and witness variants, and the non-human branch, each constrain the menu in one sentence.

### 6.2 `personas/flows/shared/prompts/persona_pass_4b_user.md`

```diff
@@ -9,6 +9,15 @@
 register_and_tone: {{ register_and_tone }}

+Register by genre, as merged from the research (the forms the figure produced):
+{{ register }}
+
+Primary texts (excerpts; ground every form of `medium` here or in the register above):
+{{ primary_texts }}
+
 Produce 8 Persona Card artifact fields (medium, technical_capabilities,
 characteristic_output_structure, relationship_to_detailed_response,
 aesthetic_qualities, stance_tendency, length_and_format_constraints,
-quality_criteria). Output as JSON with exact field names as keys.
+quality_criteria). Output as JSON with exact field names as keys. Add one
+more key, `_form_attestation`: a list of {"form": <name>, "source": <the
+genre_specific_register key or primary-text passage it comes from>}. It is
+for the operator; it does not go into the card.
```

The roadmap's `moves` chunk is **not** added. Pass 4a's `characteristic_moves`, which 4b already receives (`run_persona_pipeline.py:712`), is 4a's processed output of that same chunk (`:678-686`) [C].

### 6.3 `personas/run_persona_pipeline.py` `_pass_4b()` (`:705-725`)

```diff
     userp = render("persona_pass_4b_user",
                    pass_2_3_4a_summary=pass_2_3_4a_summary,
                    rhetorical_mode=json.dumps(pass4a["fields"].get("rhetorical_mode", "")),
                    characteristic_moves=json.dumps(pass4a["fields"].get("characteristic_moves", [])),
-                   register_and_tone=json.dumps(pass4a["fields"].get("register_and_tone", "")))
+                   register_and_tone=json.dumps(pass4a["fields"].get("register_and_tone", "")),
+                   # FU#55: form menus must be corpus-attested; 4b was CT-only.
+                   # primary_block, not primary_block_for_voice: keeps the
+                   # lyrics_patterns_only private tier out of form-building.
+                   register=chunk_vars["register"],
+                   primary_texts=primary_block)
@@
     r = _claude_pass(system=sysp, user=userp, step="personas.pass_4b",
                      max_tokens=24000, temperature=1.0)
+    fields = r["json"]
+    form_attestation = fields.pop("_form_attestation", None)
     return {"voice_name": vi["name"], "voice_slug": SLUG, "pass": "4b_artifact",
-            "model": r["model"], "usage": r["usage"], "fields": r["json"]}
+            "model": r["model"], "usage": r["usage"], "fields": fields,
+            "form_attestation": form_attestation}
```

How this behaves [C]:
- `full_card` is built from `pass4b["fields"]` (`:729`, `:1712`), so attestation never reaches the card or the chat artifact.
- The §32.1 reload (`:844-866`) reads `fields`, so the sibling key survives.
- Extra input is the 1d excerpt (about 51–85K chars per voice, roughly +15–25K tokens per 4b call). Estimated about +$0.10 per voice on Opus 4.7 input [I].

### 6.4 Not changed

Pass 4a; Derive (§3.3); Pass 5/6/7*; runtime code.

---

## 7. Validation

### 7.1 Offline checks, before any API spend

These are scratch scripts in the session scratchpad. They make no model calls and are not saved to the repo.

1. **Schema lint** for each patched card: R5; 1–3 forms; `min_words` < `max_words` ≤ envelope; names ≤ 6 words and unique; `calls_for` and `arc` open with a first-person or second-person imperative.
2. **R6 move check.** Split the old three fields into sentences and assert each appears verbatim somewhere in the new card. Report any dropped sentence.
3. **R1 check.** No `forms[].name`, and no per-form mark taken from a form's `arc`, appears as a requirement in `characteristic_output_structure`, `length_and_format_constraints` or `quality_criteria`. This is a string check plus an operator eyeball.
4. **Render check.** Call `card_assembly.assemble_system_prompt(card, step=2)` on each sandbox card. It is a pure function with no API. Eyeball the ARTIFACT section and record the token delta.

### 7.2 Sentinel for the Pass 4b edit

`sentinel_regen.py` can't run (voices §37 A5). A 4b-only edit doesn't need it: `personas/scripts/standalone_pass4b_test.py` already renders Pass 4b from a voice's cached upstream passes and writes outside the project [C]. It needs three repairs, which are gate tooling:

```diff
--- a/personas/scripts/standalone_pass4b_test.py
-PROJECT_ROOT = Path("/Users/aienvironment/Desktop/AI Assembly/projects/athens-2026")
+PROJECT_ROOT = Path(os.environ.get("AI_ASSEMBLY_PROJECT_ROOT",
+    "/Users/aienvironment/Desktop/AI Assembly/projects/current-tests/voice-pipeline-dryrun"))
@@
-sysp = render("persona_pass_4b_artifact", name=name, type=type_)
+sysp = render("persona_pass_4b_artifact", name=name, type=type_,
+              corpus_constraint=voice_config.get("corpus_constraint", "full"),
+              mediation_stance=voice_config.get("mediation_stance"))
+merged = json.loads((voice_dir / "02_merge/08_merged_dossier.json").read_text())
+excerpts = json.loads((voice_dir / "03_corpus/02_excerpt_selections.json").read_text())
 userp = render(
     "persona_pass_4b_user",
     ...
+    register=json.dumps(merged.get("register", {}), ensure_ascii=False, indent=2),
+    primary_texts=excerpts.get("selected_text", ""),
 )
```

Today's render call omits `corpus_constraint` and `mediation_stance` (`standalone_pass4b_test.py:53`) [C]. So the Marley and Whanganui variant blocks would not fire in a sentinel run; the repair above fixes that. The chunk_vars JSON formatting (`J(...)` at `run_persona_pipeline.py:265`) should be matched exactly when this is implemented.

**Sentinel voices:**

| Voice | Why |
|---|---|
| Dostoevsky | richest attested family; Stage-1 hand menu as reference |
| Cleopatra | fork-test decliner; tests over-generation |
| **Plato** | negative control: must emit one form |
| **Whanganui** | witness variant: forms must be citation-and-gloss, no ritual genre |

**Arms:** A = current 4b, B = new 4b. Two samples each, from the same cached upstream passes. That is 16 calls, estimated $8–12 [I]; FU#55 put a 4b run at about $1 per voice.

**Pass criteria (B vs A):**
1. Plato emits exactly one form in both samples.
2. Whanganui's forms are all citation-and-gloss.
3. `default_form` matches the shipped card's form for all four voices.
4. Every emitted form traces to its `_form_attestation` source, checked against `genre_specific_register` and the excerpts.
5. Zero unattested or generic-register forms.
6. Texture: the count of named concretes across the eight fields (places, persons, formulae) in B is not below A's by more than 10% (median of 2), and `_check_register` flags do not rise. This is the fork test's own texture metric.
7. Dostoevsky's B menu shares at least one non-default form with the §4.2 hand menu. This one is informational.

### 7.3 Two-night sandbox dryrun (Step 2 only)

**Design.** The Athens record is the baseline (§2.1). Step 1 is file-cached (`step1_private_reasoning.py:138`), and Step 1 never sees artifact fields. So rerunning **only Step 2** on the Athens Step 1 outputs isolates the card change [C]. Step 2 is also cached (`step2_first_draft_artifact.py:316`), so its outputs must be absent.

**Setup** in `projects/current-tests/voice-pipeline-dryrun`:
1. Copy from athens-2026: `council_config.json`, `panel_roster.json`, `conference_facts.json`, `audience_profile.json`, and all 10 `voices/<slug>/07_persona_card_assembled.json`.
2. From `runs/athens_night_{1,2}` copy only `03_provocateur/briefings/` and `04_voice/step1_detailed_responses/`.
3. **Do not copy** `continuity_night_*.json`, `step2_*`, `step3_*` or `published_artifacts/`. `continuity.py:142` returns a cached file if one exists, which would silently hand the dryrun Athens' memory.
4. Apply the §4 patches to the sandbox cards of Arendt, Dostoevsky, Battuta, Scheherazade, Cleopatra (if D5 = yes) and Marley.

**Run:**

```bash
AI_ASSEMBLY_PROJECT_ROOT=<sandbox> runtime/venv/bin/python runtime/flows/voice_flow.py <sandbox>/runs/athens_night_1 --night 1 --skip-step3
```

Then repeat with `--night 2`. Step 2 validation stays **on** for both nights (default ON, `voice_flow.py:741`). Night 2's Step 2 reads the dryrun's own Night-1 continuity.

**Threats to validity:**
- One sample per voice per night, so the unpatched voices (Plato, Octopus, Whanganui, Lovelace) are the noise floor.
- Athens Night-2 Step 1 was conditioned on Athens Night-1 *reasoning* memory, which mentions the Night-1 form. The contamination is small [I].
- If the Step 2 prompt changes before the dryrun (Gap-I, §5, or C68 A6's "You are I am …" fix), the Athens record stops being a baseline. Then add a baseline arm: unpatched cards, same prompt, about +$6–8 per night.

**Cost [I]:** Athens Step 2 cost about $2.80–3.80 per night for 10 voices, computed from `step2_first_draft_artifacts/*.json` usage at $5/$25 with a 2× 1-hour cache write. Without Step 1 warming the cache, expect about $5–7 per night, plus Sonnet validation and continuity: **about $12–20 per dryrun pass.**

**What to measure (per patched voice unless noted):**

| # | Measure | How |
|---|---|---|
| M1 | Forms used across 2 nights; share of non-default | operator maps free-text `selected_form` to menu names (Build A has no exact-name contract) |
| M2 | Does `form_rationale` cite the matter in `calls_for` terms? | operator read |
| M3 | **Texture**: blind pairwise read against the Athens artifact on the same night and same Step 1 inputs (better / same / worse) | operator, about 1 hour for 12 pairs; randomised order |
| M4 | Named-concrete count; `characteristic_moves` present (voice-fidelity validator verdict) | scratch script + validator output |
| M5 | Safeguards: any new HOLD/WARN tied to a new form (Battuta case → `topics_requiring_care`; Arendt portrait → living persons) | Step 2 validators vs Athens verdicts |
| M6 | Engagement form-fidelity WARNs on non-default forms (expected false positives: the validator can't see `selected_form`) | count; informational |
| M7 | Words vs form `length` and envelope | informational (unenforced; C38) |
| M8 | Controls: unpatched voices' blind-read drift; Lovelace letter use | as M3 |

**Build-level pass criteria:**
1. At least 2 patched voices choose a non-default form at least once in 2 nights.
2. Every non-default choice is a menu form: zero invented or generic forms.
3. No patched voice is "worse" in both of its blind pairs, and patched voices' "worse" count does not exceed the controls' by more than 1.
4. No new HOLD attributable to a new form. M6 false positives do not fail the build.

**Decision rule:**
- **1–4 pass:** promote voices by §7.4.
- **1 fails** (0–1 voices switch): the exemption's claim is falsified for Step 2. The operator chooses between (a) §5 under the gate, then rerun the same Step-2-only dryrun (same inputs, about $12–20, which measures §5 alone), and (b) close §H by FU#55's original rule.
- **2 or 4 fail for a voice:** fix that voice's menu once, or revert it.

### 7.4 FU#55 resolution criteria, per voice (after the override)

The original criteria ("0/10 → close §H; 1–2 → opt-in; 3+ → land universally", `FOLLOW_UPS.md:704-707`) decided *whether to build*. After the 2026-06-13 override, the per-voice criteria below decide *whether each voice keeps its menu*:

| Verdict | Condition |
|---|---|
| **KEEP** | At least 1 non-default form across the dryrun (and the §5 rerun, if run), with blind reads not worse and no new HOLD. |
| **WATCH** | No non-default use, but no texture loss. Keep the menu through the first 3 nights of the next real run. If it is still unused, collapse to one form. An unused menu is dead surface, the same principle as roadmap §1.3's "don't carry dark QC forward". |
| **REVERT** | Texture loss on a *default-form* artifact against Athens (the fork-test signal); any invented or generic form; or a HOLD caused by a new form that one card patch can't fix. Restore the snapshot. |

**Build level, mapped onto the original thresholds:**

| KEEPs | Action |
|---|---|
| 0 | Close §H as aspirational (the original rule). Revert the Pass 4b edit too, because menus for new voices would be unjustified. |
| 1–2 | Menus stay on the KEEP voices only. Keep the 4b edit only if its sentinel showed one-form discipline (Plato). Add no opt-in flag: that would be new config surface. |
| 3+ | As built. |

Record per-voice results in voices OPEN_ITEMS under FU#55. `FOLLOW_UPS.md` is frozen.

---

## 8. Surface each change adds

### 8.1 Per voice (card data; sandbox first, athens-2026 only on KEEP)

| Voice | Forms | Fields touched | System-prompt delta [I] | New failure modes to watch |
|---|---|---|---|---|
| Arendt | +2 | medium, cos, lfc, qc (1 edit) | about +1.6K chars / +450 tokens, cached | portrait of a living person (HOLD); fragmentary *Denktagebuch* |
| Dostoevsky | +2 | medium, cos, lfc, qc (1 edit) | about +1.5K / +420 | mediated confession (needs Stage 4 item 3); over-length (N3 was 826) |
| Battuta | +2 | medium, cos, lfc, qc (1 word) | about +1.5K / +450 | case form → `topics_requiring_care`, Gap-H; marvel tic |
| Scheherazade | +1 | medium, cos | about +0.8K / +230 | reader-invisible variety |
| Cleopatra (optional) | +1 | medium, cos, lfc, qc (1 edit) | about +0.8K / +250 | mediated priestly voice; likely never chosen (WATCH) |
| Marley (sandbox) | +1 | medium, cos | about +0.5K / +150 | reader gate |
| Plato, Whanganui, Octopus, Lovelace | 0 | — | 0 | — |

**Per patched voice, the operator also does:**
1. Snapshot.
2. Patch (sandbox).
3. The §7.1 offline checks.
4. A chat test on the regenerated `03_chat_system_prompt.json`.
5. After KEEP, promote to athens-2026 and run a path-(b) re-Derive.
6. Optionally hand-edit the `council_config.json` `medium` string (D12).

### 8.2 Build level

| | Build A (recommended) | Roadmap as written |
|---|---|---|
| Persona prompts | 4b system +32 lines, 4b user +9 lines | same + Pass 4a banned-mode (~10 lines, second upstream prompt) |
| Persona code | `_pass_4b()` +8 lines | same |
| Runtime prompts | 0 | Step 2 +6 lines (§5), Gap-I +1, continuity +1 |
| Runtime code | 0 | length check + `selected_form` to validator (~15 lines + tests) |
| Gate tooling | `standalone_pass4b_test.py` +8 lines | same |
| New files, config keys, flags | 0 | 0 |
| Docs, when built | Card spec `medium` / cos / lfc + §H status; `CROSS_REPO_CONTRACT.md` (`medium` shape); Voice Pipeline spec (the E1 form-decision note; already neutral); `LLM_CALL_INVENTORY.md` (4b inputs) | same |
| API spend | 4b sentinel ~$8–12 + dryrun ~$12–20 | + §5 rerun ~$12–20 |

---

## 9. Open operator decisions

| # | Decision | Recommendation |
|---|---|---|
| D1 | Read "the one Pass 4b edit" as the 4b system prompt + user prompt + `_pass_4b()`, and treat card-data patches as outside the gate's scope (but counted, §8)? | yes |
| D2 | Build A (minimal; test the "runtime already supports it" claim), or the roadmap as written (under the gate)? | Build A |
| D3 | Menu cap of 1–3 forms, replacing the card spec's "default + 3–6"? | 1–3 |
| D4 | Attestation standard for a form | Require `genre_specific_register` **and** (a readable 03_corpus text **or** the shipped card). Admit merge-only forms (Dostoevsky's Diary and letters, Arendt's *Denktagebuch* and portrait) **labelled** as such. |
| D5 | Stage-1 voices | Arendt, Dostoevsky, Battuta, Scheherazade; Cleopatra optional (low expectation); Marley sandbox only |
| D6 | Mediated-voice forms (Dostoevsky's confession; Cleopatra's temple text) | Wait for Stage 4 item 3, or drop them from the first dryrun |
| D7 | Gap-I | Its own change, not bundled; the dryrun gets a same-prompt baseline either way |
| D8 | Length-check revival + `selected_form` to the engagement validator | Defer to the Stage-6 validator prune-vs-fix decision (runtime C60 / C42) |
| D9 | *Denktagebuch* language | English with German seams (a German-throughout entry would lose the breakfast reader) |
| D10 | §27's Plato "Myth" and Whanganui "Karakia + whakataukī cluster" | Reject the karakia cluster (witness contract); defer Myth (fork test) |
| D11 | Spend cap | about $35 total for the sentinel plus one dryrun pass, and about $20 more if §5 is needed |
| D12 | `council_config.json` `members[].medium` | Leave as is. Optionally append the family's names in one line; that is hand-wired config, not code. |

---

## 10. Method and coverage

**Read fully:**
- The brief;
- roadmap §1.2 and its decision blocks;
- PRODUCT §11.6;
- voices OPEN_ITEMS FU#55, §25, §27, §31, §37;
- FOLLOW_UPS FU#55–56;
- card spec §H and the Artifact fields;
- `persona_pass_4b_artifact.md` and `_user.md`;
- `voice_step2_artifact.md`, `voice_step3_amendment.md`, `voice_continuity.md`, `voice_step2_validation_engagement.md`;
- `card_assembly.py` (runtime voice);
- `continuity.py`;
- the relevant parts of `step2_validation.py`, `run_persona_pipeline.py` (`_pass_4a`, `_pass_4b`, card assembly, register check), `chat_prompt_builder.py` and `standalone_pass4b_test.py`;
- the reverted `6ec9dca` diff.

**Data read (athens-2026, read-only):**
- The three form fields, `quality_criteria` and `banned_modes` of all 10 cards;
- `genre_specific_register` from each voice's merged dossier;
- corpus source lists, excerpt labels and targeted greps (Dostoevsky, Cleopatra, Battuta, Scheherazade, Arendt, Marley);
- Athens `selected_form` and word counts for 30 artifacts;
- Step 2 token usage for all 3 nights;
- two `continuity_night_2.json` files.

**Scratch scripts:** inline read-only Python over the athens-2026 JSON, run through Bash; nothing saved in the repo. No model calls.

**Not verified [P]:**
- whether the offering-scene formulae are in any readable Cleopatra source;
- the *Denktagebuch*'s heading convention;
- the cost figures, which are estimates.

**Tracker check:**
- The continuity Night-3 gap is C68 A10 and is referenced, not re-reported.
- The raw-PDF corpus stores are new evidence for voices §37 A3's class (§2.4).
- Nothing else here duplicates a filed item.

---

## Appendix: the length check and validator line, if D8 is "now" (under the gate)

```diff
--- a/runtime/flows/voice/step2_validation.py
@@ def _check_length_compliance(artifact_text, card):
-    constraints = card.get("length_and_format_constraints") or {}
+    constraints = card.get("length_and_format_constraints") or {}
+    medium = card.get("medium")
+    if isinstance(medium, dict) and selected_form:
+        for f in medium.get("forms") or []:
+            if f.get("name", "").strip().lower() == selected_form.strip().lower():
+                constraints = f.get("length") or constraints
+                break
```

The function would gain a `selected_form` parameter passed from `check_engagement`, and `check_engagement`'s user message would gain one line: `### selected_form\n{selected_form}`. The exact-name match only works if §5's "`name` exactly as written" line has landed. Otherwise the check silently falls back to the (string) envelope and returns `None`, as it does today.
