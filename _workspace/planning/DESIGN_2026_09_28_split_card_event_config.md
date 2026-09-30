# DESIGN (draft) — split card (FU#42) + event config (C52)

**Status:** design draft for operator review. Nothing here is decided and nothing is built. Roadmap §2.1, Stage 5.
**Written:** 2026-09-28/29 by a Fable 5.1 session, per `BRIEF_2026_09_28_fable_batch2.md` Task 1.
**Revised:** 2026-09-29 after the independent review `REVIEWS_OF_FABLE_DELIVERABLES_2026_09_29/07_split_card.md`. All six WRONG findings and most DOUBTFUL ones are adopted. The biggest change: the card split now ships with the voice-card clean-up, not with C52. The full change list is in §8.
**Canonical homes:** FU#42 (`FOLLOW_UPS.md`, voices §10) · runtime C52 (and C55, whose stopgap this finishes) · runtime C68 A10 (continuity) · roadmap `PLAN_2026_06_12_post_athens_roadmap.md` §2.1.
**Labels:** **CONFIRMED** = seen in code or data at the path given. **PLAUSIBLE** = likely, not checked. *Inference* = my reasoning, marked as such.
**Base:** code and prompt lines are at `phase0-fixes` `40fe490`. At HEAD, `personas/run_persona_pipeline.py` lines after `:392` are +5 (`f7e0d4c`); runtime lines are unchanged. Card data is `athens-2026` `0b2af19` (its cards are unchanged at `e4c4e39`).
**Method:** read-only and offline; no model calls. The scans are described in Appendix A so the counts can be reproduced.

---

## 0. Outcome

1. **Three layers, each with one job (the end state).**
   - A **voice card**: who the voice is, with no event content, byte-stable.
   - A **deployment card** per voice per event: temporal stance, length, and the council- and audience-relative fields.
   - **`event_config.json`** per project: the event's facts, its day/night schedule, and the few frame phrases the prompts need. It absorbs `conference_facts.json`, so the project gains no file.
2. **The partition is mostly clean, with one exception.** Of the card's 44 top-level keys, 37 go to the voice card, 5 to the deployment card, and 2 continuity placeholders leave the card. **The exception:** the Athens reader frame ("the reader at breakfast", "one piece per morning", "over coffee") is woven into voice-native sentences of the artifact fields in **9 of 10** voices (all but Plato). It can't be cut out without rewriting those sentences, so the voice cards can't be event-free until they're cleaned.
3. **So: build C52 now, and the split later.**
   - **Now:** golden prompt hashes, `event_config.json`, and count-agnostic continuity (§5 Steps 0–2).
   - **Later:** the card split ships **together with** the voice-card clean-up (voice card v2, per-voice re-validation) when a second deployment is prepared (§5 Step 3).
   - Why not split now: on its own the split leaves the cards Athens-bound and adds more surface than it removes (§6).
4. **Hardcoding is smaller than feared in code and wider in cards.**
   - Code: 5 hardcoded maps, 5 `choices=(1,2,3)` CLIs, 2 night-range guards, 4 "night 3 is last" checks, and 6 run-dir builders/parsers, across **18** runtime files (incl. 2 post-Athens scripts).
   - Continuity is already count-agnostic except two gates.
   - Prompts: the 4 Step-2 validator prompts and the editor prompt carry the event frame. **4** persona prompts are event-coupled, not the 5 the roadmap lists (§3.4).
5. **Net-complexity:**
   - `event_config` removes more than it adds.
   - The card split does not, until the cards are cleaned, so it's sequenced with the clean-up.
   - Also shelved: a deployment-card generator pass, per-voice `generation_parameters`, and moving `--skip-step3` into config.

---

## 1. The design on one page (end state)

```
<PROJECT_ROOT>/                         (one project = one event, as today)
├── event_config.json                   NEW (Step 1) — replaces conference_facts.json
│     facts{}     ← the former conference_facts.json, verbatim
│     schedule{}  ← days, dates, which days are processed nights, run-dir template
│     frame{}     ← 3 short phrases the validator prompts need
├── audience_profile.json, council_config.json, panel_roster.json   (unchanged)
└── voices/<slug>/
      07_persona_card_assembled.json    the VOICE CARD (Step 3: 37 fields)
      08_deployment_card.json           Step 3 — this voice at this event (5 fields + provenance + sha256 pin)
      continuity_night_<N>.json         runtime state, unchanged
```

**Loader rule (Step 3):**
- One shared `load_card(slug)` for every reader: `card = voice_card ∪ deployment_card.fields`.
  - The deployment card is **optional**. Without it, the voice card is the whole card; that's how unsplit Athens cards keep working with no legacy branch.
  - A field in both → hard error.
  - `voice_card_sha256` ≠ sha256 of the voice card's content → hard error. The hash covers every key **except `metadata`**, which the persona pipeline rewrites.
- Continuity overlay afterwards, as today (`runtime/flows/voice/card_assembly.py:187-209`).

**Values move verbatim.** In particular, `voice_temporal_stance` stays the `{default, anchored_override}` dict. CONFIRMED that four readers render it:

| Reader | How it renders the stance |
|---|---|
| Voice renderer | unwraps it (`card_assembly.py:240-282`, called at `:306`) |
| Step-1 validator | imports that unwrap (`runtime/flows/voice/step1_validation.py:151,159`) |
| Editor | JSON-dumps it: no unwrap in `editor/card_assembly.py:164-189` |
| Step-2 safeguards validator | JSON-dumps it (`runtime/flows/voice/step2_validation.py:163`, `_render_field`) |

So unwrapping at split time would change Tim's system prompt and every voice's safeguards user prompt (review F8).

**Why prompts stay byte-identical under a verbatim move:**
- The voice renderer renders fields by fixed tuples in fixed order (`card_assembly.py:82-152`, `_render_section` `:285-310`), not by dict order. The editor and the validators also pick fields by name.
- CONFIRMED for the voice renderer by reading the code. The review's offline render confirmed it for Plato; for the editor it holds only if the value is unchanged.

**Build-side principle (Step 3):** *voice passes are event-blind.*
- Passes 1.x, 2, 3, 4a, 4b (voice part) and 6 never read `event_config`, `audience_profile` or `council_config`.
- Only the deployment step reads them: the deployment half of Pass 5, and Pass 7b.
- Today Pass 5 and 7b read the event (`personas/run_persona_pipeline.py:743-753`, `:1542-1544`), and four prompts name Athens directly (§3.4).

**How the persona pipeline sees the split (Step 3):**
- **Reads** use the same `load_card`, so Pass 7a FINAL (`:1881/:1895`), Derive (`:1999`) and the chat builder (`:2066`) see exactly the fields they see today.
- **Writes** go through one router, keyed by a shared `DEPLOYMENT_FIELDS` set, that sends each field to the file that owns it. That covers the metadata-preserving rewrite (`:1748`), the final write (`:2052`) and the path at `:2174`.
- Metadata writes don't touch the pin. A patch to a voice field breaks the pin on purpose: re-pinning is the explicit act of accepting a new voice card.

This matches the retired C48 design's rule (`_workspace/planning/runtime/DESIGN_voice_deployment_context.md`): descriptive event facts stay out of the persona card's prescriptive layer. The per-voice, per-event *prescriptive* text, which Athens put inside the cards (the stance lead, the length windows), lives in the deployment card.

---

## 2. Field-by-field partition

**V** = voice card · **D** = deployment card · **—** = leaves the card. Evidence is CONFIRMED in `athens-2026/voices/*/07_persona_card_assembled.json` unless marked otherwise. Tim is covered in §2.2.

### 2.1 The 44 keys (voices)

| # | Field | → | Reason | Athens evidence (10 voice cards) |
|---|---|---|---|---|
| 1–4 | `voice_name`, `voice_mode`, `pipeline_version`, `generated_date` | V | Identity and provenance of the voice build. | Clean. |
| 5 | `council_member_name` | V | Identity ("You are …", `card_assembly.py:421-422`). | Clean. |
| 6–9 | `epistemic_frame_statement`, `world`, `formative_experience`, `character` | V | Who the voice is. | Clean. The "gathering", "panel" and "night" hits are the voices' own (Marley's Nyabinghi gathering, the Wai 167 Tribunal panel). The review notes one borderline case: Whanganui `formative_experience` "more-than-human governance". |
| 10 | `knowledge_boundary` | V | The voice's horizon. It holds most dates the stance repeats (see the carry-forward list below). | Clean. |
| 11 | `voice_temporal_stance` | **D** | Event-bound in 11/11 (the literal "Athens" appears in 10; Plato's says *"gathers in YOUR city"*). The lead sentence names the event: *"You have been called to the assembly that gathers in Athens — present in their time, observing the panels but not entering them as participant."* 7 voices use it verbatim; Octopus and Whanganui use variants. *"When the panels' questions require translation…"* recurs later in 8 voices, so the field can't be split by sentence. It moves whole and **verbatim (still a dict)**, because two readers JSON-dump it (§1). | `anchored_override` is null in 11/11, so a later collapse to one string loses nothing. The final text is the operator's short drafts (athens-2026 `08a8253`; voices §31 Gap-K). |
| 12 | `translation_protocol` | V | The voice's method. "Reader/listener/questioner" = whoever asks. | Clean. |
| 13 | `topics_requiring_care` | V | Constitutional (FU#42 said hybrid; the content doesn't bear it out). | Clean. The Athens/Assembly hits are native (Plato's Athens; Marley's "National Assembly Resolution 23"). |
| 14 | `hard_limits` | V | Constitutional. | Clean. |
| 15–19 | `constitution`, `concept_lexicon`, `reasoning_method`, `finds_compelling`, `resists` | V | Intellectual core. | Clean (e.g. Dostoevsky's *provokatsiia*, `constitution[17]`, is his own). |
| 20–26 | `rhetorical_mode`, `characteristic_moves`, `register_and_tone`, `metaphorical_repertoire`, `preferred_vocabulary`, `banned_language`, `banned_modes` | V | How the voice speaks. | Clean. |
| 27 | `medium` | V | The form family: FU#55 Stage 0's `{default_form, forms[]}`, exempted from the gate as voice capability (PRODUCT §11.6). | **Contaminated in 8/10** (all but Plato and Battuta). Examples: Whanganui *"I write one piece of prose each morning… The piece is for reading at breakfast"*; Marley *"Two shapes, one morning piece"*; Cleopatra *"this morning produces one more"*; Dostoevsky *"opened over morning tea, finished before the cup goes cold"*; Scheherazade *"The reader at breakfast should feel…"*; Octopus *"…a 10-15-second looping WebGL animation"* (an output-mode fact). → cleaned in Step 3. |
| 28 | `technical_capabilities` | V | What the medium needs. Which renderers exist is deployment output config (B7). | Dostoevsky *"(English on this morning)"*. → Step 3. |
| 29 | `characteristic_output_structure` | V | Arc per form. | Cleopatra *"where the morning's matter requires it"*; Octopus *"the audience meets my skin first"*. → Step 3. |
| 30 | `relationship_to_detailed_response` | V | Step 1 → Step 2 craft. | Octopus *"The reader at breakfast meets a body"*; Whanganui *"In the public morning piece"*. → Step 3. |
| 31 | `aesthetic_qualities` | V | Gestalt of the voice's work. | Ada *"The reader at breakfast should feel…"*. → Step 3. |
| 32 | `stance_tendency` | V | The voice's pull (not the Derive enum of the same name). | Cleopatra *"If the morning matter resists this stance"*; Whanganui *"I do not flatter the audience"* (mild). → Step 3. |
| 33 | `length_and_format_constraints` | **D** | Length is an output decision; at Athens the operator set it per event (§27 surgery: Dostoevsky and Arendt 350–750, Octopus 350–500; STATE.md:213). | Cup/coffee/morning window in 6/10: Marley, Cleopatra, Dostoevsky, Arendt, Octopus, Whanganui (*"350–550 words of prose for the morning audience. One piece per day"*). It also holds form-native formatting (Plato's speaker names; Octopus's `chromatophore_display` channel), which moves into `medium` in Step 3. |
| 34 | `quality_criteria` | V (fidelity) + **D** (engagement criterion) | The fidelity criteria test voice fields by name. The "+1" audience criterion comes from `persona_pass_4b_artifact.md:105`. | The engagement criterion names the Athens reader in **9/10** (all but Plato). Examples: Ada `[4]`, Dostoevsky `[4]`, Battuta `[4]`, Octopus `[5]`, Scheherazade `[4]` (*"750 strangers"*), Whanganui `[4]`, Marley `[4]` and Cleopatra `[4]` (*"the reader, finishing the decree over coffee"*), and Arendt inside a single **string** (not a list). Until Step 3 the whole field stays V; in Step 3 the criterion moves to D as `engagement_criterion`. |
| 35 | `bold_engagement_topics` | **D** | Pass 5 generates it *from* the event (`persona_pass_5_user.md:10-40`). Never loaded at runtime (FU#57). | At least 9/10 quote or address the Athens audience. Marley `[4]` *"Your well-curated openness itself. You pay the premium not to cluster"*; Battuta `[2]` *"'secular but enchantable'"*; Octopus `[5]` *"The audience is good at performing reception"*; Plato `[2]` *"The Forum's own craft is on trial here"*. The review (F17) adds Cleopatra `[5]` and Dostoevsky `[3]`. |
| 36 | `default_questions` | V | Pass 5 defines them as questions *"the voice brings to ANY material"* (FU#42 had D). | Clean except Scheherazade `[4]` *"has reception been performed…"*. → Step 3. |
| 37 | `disagreement_protocol` | V | How the voice disagrees. | Clean except Octopus *"I will not perform reception…"* and Marley *"than from the panel"*. → Step 3. |
| 38 | `unique_contribution` | **D** | Defined relative to the council (`voice_step1_reasoning.md:21`, *"what no other voice on the panel sees"*) and, in Athens content, to the audience. | **9/10** relative: Ada *"this audience needs it"*; Arendt *"an instrument this audience particularly lacks"*; Plato *"your gathering"*; Battuta *"your new gathering"*; Whanganui *"no other voice at this panel"*; Marley *"the conference schedule"*; Octopus *"performed reception"*; Cleopatra *"the others at this table"*; Scheherazade *"Where another voice will…"*. |
| 39 | `curated_corpus_passages` | V | The voice's own words (`corpus_metadata` still stripped at runtime). | Clean. |
| 40 | `smoke_test_chains` | **D** | Build evidence generated *against the event*: Pass 7b reads `conference_context` (`run_persona_pipeline.py:1542-1544`). Never loaded. | 42 chains across 11 cards (`provocation` is each chain's key, not content). The values name Athens 11 times; per the review, Plato's chains cite *"AI Democracy Marathon … in your city"*. |
| 41 | `reference_only_passages` | V | Copyright-tier corpus; Step 1 only. | Contract-note boilerplate only. |
| 42–43 | `continuity_block_if_night_2`, `continuity_block_artifact_if_night_2` | **—** | Runtime state: it lives in `continuity_night_<N>.json`, overlaid by night-templated keys (`card_assembly.py:197-202`). The placeholders are null and never rendered. Removed in Step 3; removing them alone buys nothing. | Null in 11/11. |
| 44 | `metadata` | V | Build provenance, dropped at runtime. **Except** `metadata.deployment_context` (`run_persona_pipeline.py:1782`) → deployment card `provenance`. Excluded from the sha pin. | — |
| new | `generation_parameters` | D (later) | Per-voice model/vendor. Not yet: `model_routing.json` (C63) is the single model source until the vendor layer (2.2). | — |
| new | `engagement_criterion` | D (Step 3) | Split from `quality_criteria` (row 34). | — |
| new (vatican) | `annotation_register`, `silent_threshold` | D | Vatican spec §6. | — |

**Totals:** 37 V · 5 D (`voice_temporal_stance`, `length_and_format_constraints`, `bold_engagement_topics`, `unique_contribution`, `smoke_test_chains`) · 2 partial moves (the engagement criterion; `metadata.deployment_context`) · 2 removed.

**Departures from FU#42 (2026-04-25):**
- `voice_temporal_stance` moves V→D, because the AF reframe (§30/§31 Gap-K) made it event-bound. Roadmap §2.1 agrees.
- `default_questions`, `disagreement_protocol` and the fidelity part of `quality_criteria` move D→V.

**Carry-forward list** (CONFIRMED only in `voice_temporal_stance`): Dostoevsky's Old/New Style dating; Battuta's hijrī counting; Octopus's *"no calendar, no year"*; birth years for Marley (1945), Arendt (1906) and Plato (428/427). Dostoevsky's 1821 is also in `metadata`, which runtime drops. Whoever drafts the next event's stances must carry these. *Inference:* start each new draft from the Athens deployment card.

**Runtime routing is unchanged.** The stance stays in the cached prefix and `unique_contribution` in ENGAGEMENT at every step, so Step 1 still sees two deployment fields. That's intended (AF-LEADS, §31 Gap-K).

### 2.2 The editor card (Tim)

CONFIRMED: Tim's identity-level fields name Athens, WBBF or May 2026:
- `knowledge_boundary`: *"alive in May 2026 … the Athens forum"*
- `constitution[16]`: *"750 attendees, eight Athens venues"*
- `reasoning_method[7]`, `topics_requiring_care[2]`, `characteristic_moves[6,11]`, `preferred_vocabulary[10]`
- `curated_corpus_passages.passages[0].id = monster_athens_2026`
- `formative_experience`, `epistemic_frame_statement`, `world`

He is a living person who hosts the event; his biography moves with each event.

**Recommendation:** same loader for symmetry; move his 5 D fields in Step 3.
- **His stance keeps the dict, verbatim, with the `{night}` placeholder intact.** The editor renderer JSON-dumps it, so unwrapping would change his system prompt (the review measured prefix sha `8d93245803b2` → `205ce7222b9a`).
- The placeholder is filled at `editor/card_assembly.py:366-367`, and only Tim's card has one.
- Accept that his voice card is re-authored for any other event. Making the editor a variable is C57's job.

---

## 3. Inventory of event hardcoding

**Disposition:** *config* = reads `event_config` · *keep* (already event-neutral) · *out* (not event data; where it belongs is named).

### 3.1 Runtime code

| ID | file:line | What | Disposition |
|---|---|---|---|
| C1 | `runtime/ingest/config.py:91-98` | `DAY_TO_RUN` ("Day One/Two/Three" → `athens_night_1/2/3`; other labels → None) | config: `schedule.days[]` + `run_dir_template`; the None entries go (unlisted labels already resolve to None) |
| C2 | `runtime/ingest/sessions.py:158-160` | `run_for_session` uses `DAY_TO_RUN` | config (follows C1) |
| C3 | `runtime/ingest/dashboard.py:29-35` | `ATHENS_NIGHTS = (1, 2, 3)`; `f"athens_night_{night}"` | config |
| C4 | `runtime/ingest/dashboard.py:606-617` | `next_night <= 3` / `> 3` | config: `is_final_night` |
| C5 | `runtime/ingest/dashboard.py:1355, 1361` | `reversed(ATHENS_NIGHTS)` | config |
| C6 | `runtime/ingest/app.py:397` | `days_ordered` literal | config |
| C7 | `runtime/ingest/app.py:768` | `night_to_day` literal | config |
| C8 | `runtime/ingest/app.py:731, 750, 767, 827, 850, 953, 972, 992, 1010, 1022, 1051, 1063, 1081, 1093, 1111` (guards); `:738, 812, 837, 999, 1037, 1070, 1100` (`all_nights`) | `night in dashboard.ATHENS_NIGHTS` | config (mechanical) |
| C9 | `runtime/ingest/templates/admin_transcription.html:43` | `'runs/athens_night_' ~ night` | config: the view passes the run-dir name |
| C10 | `runtime/ingest/templates/admin_voice.html:237, 239` (logic); `:104`, `:307` (text) | Night-3 ceiling | config: the view passes `is_final`; the text is made count-neutral |
| C11 | `runtime/flows/vendor_intake.py:91-95`, `:409`, `:440`, `:527`, `:543` | `NIGHT_TO_DAY`, `NIGHT_TO_RUN_DIR`, `choices=(1, 2, 3)` | config |
| C12 | `runtime/scripts/overnight_orchestrator.py:66-71`, `:97-99`, `:105-112`, `:596`, `:630-635`; docstring `:29-31` | `DATE_TO_NIGHT`, `NIGHT_TO_DAY`, run dir, `choices` | config |
| C13 | `runtime/scripts/overnight_orchestrator.py:481` | `--skip-step3` always passed (A1) | **out**: a profile knob (2.3); D12 |
| C14 | `runtime/scripts/reset_run.py:60-64`, `:161` | regex `athens_night_(\d+)$` | config: `night_for_run_dir` |
| C15 | `runtime/scripts/generate_sessions_json.py:40-55` (`DAY_TO_DATE`, `DAY_TO_INDEX`, `TZ_OFFSET`); `:344` (day-label list) | Athens dates and days in the program importer | config for dates and labels; the script remains a WBBF-HTML importer |
| C16 | `runtime/flows/voice_flow.py:589`, `:612`, `:697` | `night < 3` continuity gate; `choices` | config |
| C17 | `runtime/flows/voice/card_assembly.py:401` (range); `:240-282` (`_unwrap_voice_temporal_stance(…, deployment="athens")`) | Night range; the deployment hook | Range → config. **The unwrap stays**: it has a second caller (`step1_validation.py:151,159`) and must keep handling the Athens dicts. Only the unused `deployment` parameter goes (no caller passes it). |
| C18 | `runtime/flows/editor/card_assembly.py:308` (range); `:110` (`EDITOR_CARD_SUBPATH`); `:264-277` (hardcoded "YOUR ROLE" paragraph, *"not 'breakfast reading'"*); `:320` (fallback `"Tim Leberecht"`) | Editor range, identity, Athens prescriptive text | Range → config. The slug → `council_config.editor_slug` (D11). The role paragraph → Tim's deployment card (Step 3). The fallback name goes. |
| C19 | `runtime/flows/editor_flow.py:326-327` | `choices=(1, 2, 3)` | config |
| C20 | `runtime/flows/publish_flow.py:1154` | `choices=[1, 2, 3]` | config |
| C21 | `runtime/flows/editor/dossier_generation.py:414-421` | Colophon *"…on the morning of Night {night}."* | keep (the conference profile's cadence, 2.3) |
| C22 | `runtime/flows/editor/dossier_generation.py:87, 164` | Docstrings say `athens_night_N` | keep (cosmetic) |
| C23 | `runtime/flows/shared/io.py:44` | Guard regex `_night[_]?(\d+)\b` needs a leading underscore, so a run dir named `night_1` silently disables the cross-night guard | **config**: use `night_for_run_dir` (review F27) |
| C24 | `runtime/scripts/build_athens_data_graph.py:43` (`NIGHTS = ["night_1","night_2","night_3"]`), `:601` (`f"athens_{night}"`), `:655` (reads `conference_facts.json` with an `or {}` fallback) | Post-Athens explorer | config. **Switch `:655` before deleting `conference_facts.json`**, or its facts go silently blank. |
| C25 | `runtime/scripts/apply_ai_assembly_flags_from_csv.py:43-48` | Day-label → key map | config (labels) |
| C26 | `runtime/flows/voice/card_assembly.py:340-345` | *"MOVES YOU HAVE ALREADY DEPLOYED THIS CONFERENCE"* | keep: conference-shaped cadence wording, not this event (see §8) |

Readers that render the card and are affected by a split (not hardcoding): `step1_validation.py:151,159`, `step2_validation.py:163` (§1).

### 3.2 Card schema and persona code

| ID | file:line | What | Disposition |
|---|---|---|---|
| P1 | `personas/run_persona_pipeline.py:1872-1873` (emits the null continuity fields); `:918`, `:1925`, `:2004` (exclusion sets) | Continuity placeholders | Removed in Step 3 |
| P2 | `personas/flows/shared/chat_prompt_builder.py:109-110` (continuity strips), `:100`, `:118` (`smoke_test_chains`, `bold_engagement_topics` strips) | Blacklist strip | **Keep the FU#57 strips**: a merged deployment card brings those fields back. Only the 2 continuity entries go, in Step 3. |
| P3 | `personas/run_persona_pipeline.py:61-72`, `:75-103` | Build-time reads of `conference_facts.json` + `audience_profile.json` | config: `event_config.facts` (Step 1). In Step 3, only the deployment step uses them. |
| P4 | `personas/run_persona_pipeline.py:1782` | `metadata.deployment_context` | → deployment `provenance` (Step 3) |
| P5 | `personas/run_pass0a_voice_config.py:72-73`, `:184-211` | Pass 0a is fed facts + roster | config (`facts`); casting stays event-relative |
| P6 | `personas/flows/shared/paths.py:269-270` | `conference_facts()` helper | → `event_config()` |
| P7 | `personas/run_persona_pipeline.py:897, 1470, 1748, 1881/1895, 1999, 2052, 2066, 2174` | The pipeline's own card reads and writes (7a FINAL and Derive read the full card) | Step 3: reads via `load_card`, writes via the field router, pin excludes `metadata` (§1) |

### 3.3 Runtime prompts

| ID | file:line | Text (abridged) | Disposition |
|---|---|---|---|
| R1 | `voice_step2_validation_{safeguards,engagement,voice_fidelity}.md:1` | *"a panel of historical voices that comment on conference panels overnight, with their artifacts published the next morning to a real audience (business leaders, conference attendees)"* | config: `frame.*` (C55's real fix) |
| R2 | `voice_step2_validation_safeguards.md:5`, `:9`, `:13` | *"Two universal Athens rules"*; *"attendees … at the conference"*; stale stance rule | `:5` → "Two universal rules"; `:9` → `frame.audience_short`; `:13` = C42 |
| R3 | `voice_step2_validation_cross_night_echo.md:1` | *"voices that publish nightly during the conference"* | config: `frame.assembly` (wording change, intended) |
| R4 | `editor_dossier.md:4`, `:21` | *"(1, 2, or 3)"*, *"Nights 2-3"* | config: `{{night}} of {{night_count}}` (editor tail changes, intended) |
| R5 | `editor_dossier.md:27`, `:35`, `:198` | *"HoBB dossier … House of Beautiful Business"* | config: `facts.host_organization(_short)` (same text for Athens) |
| R6 | `editor_dossier.md:48, 52, 110, 138, 151, 160` | Tim's persona specifics | **out** → C57 |
| R7 | `editor_dossier.md:31`, `:58` | *"What the conference surfaced"* | keep; the per-run override covers non-panel runs (`dossier_generation.py:223-249`) |
| R8 | `voice_step1_reasoning.md:21`, `voice_step3_amendment.md:14-15, 28`, `voice_step2_artifact.md:2, 37`, `voice_continuity.md` | "the panel" (= council), "tonight" | keep |
| R9 | the 3 provocateur prompts (`{{audience}}`, `{{collective_landscape}}`), THE GATHERING / THE SPEAKERS (`provocateur_flow.py:272-330`) | Already variable-fed | keep; THE GATHERING reads `facts` |
| R10 | `researcher_*.md`, `transcription_*.md` | "conference session transcript" | **out** → 2.3 input adapters |

**Substitution:** the Step-2 validators load their prompts raw (`step2_validation.py:152, 242, 295, 329`). `{{…}}` substitution exists only in `provocateur_flow.py:335-345` and `step1_validation.py`. R1–R3 therefore need a small substitution helper: new code, a few lines (review F31).

### 3.4 Persona prompts (the Athens reader baked into card generation)

| ID | file:line | Text | Disposition (Step 3) |
|---|---|---|---|
| S1 | `pass_1_4_merge.md:53-55` | *"The Athens audience is philosophically literate but NOT classics-vocabulary-literate"* | event-neutral rationale (not templated; voice passes are event-blind) |
| S2 | `persona_pass_4a_voice.md:168-170` | same | same |
| S3 | `persona_pass_4b_artifact.md:13-16`, `:88`, `:105`, `:110-111`, `:119` | *"~750 people will encounter at breakfast"*, *"over coffee"*, the "+1" criterion, *"adapted for the conference deliverable"* | neutralize; move the "+1" criterion and length to the deployment step |
| S4 | `persona_pass_2_identity_boundaries.md:339-405` (`:355` *"per Athens brief…"*; `:382` `anchored_override`) | Generates the event-bound stance | remove the block from Pass 2 (D8) |
| S5 | `persona_pass_5_user.md:10-40` | DEPLOYMENT CONTEXT block | keep for the deployment half only |
| S6 | `persona_pass_7b_smoke_test.md` | `conference_context` | keep, deployment-scoped |

**Correction to roadmap §2.1** (CONFIRMED): of its 5 prompts, only `pass_1_4`, `persona_pass_2` and `persona_pass_4a` are event coupling. `pass_0a_voice_config.md:36` and `pass_1_1_merge.md:253, 259, 284` name Athens as Plato's city. `persona_pass_4b` is the fourth.

### 3.5 Continuity's night count

**Count-agnostic except two gates** (CONFIRMED):
- The overlay (`card_assembly.py:197-202`) and the continuity prompt's `N+1` keys (`voice_continuity.md:25`) work for any N.
- So do the prior-night readers: `editor/publish.py:73-79`, `step2_validation.py:385-405`, orchestrator `:460-464`, `editor/edition.py:313`.
- **The two 3-bound gates:** `voice_flow.py:589` and C4/C10.

**C68 A10** (`runtime/OPEN_ITEMS.md:3104`, before this draft; I missed it):
- The code carries only Night N−1's summary into Night N. The spec says Night 3 merges Nights 1+2. The operator put this into Stage 5.
- The cross-night **moves register** already accumulates across all prior nights. CONFIRMED: Plato's `continuity_night_3.json` `signature_moves_deployed` has `night_1` and `night_2` entries.
- This design assumes today's behaviour (last-night summary + accumulated moves register); decision D15.

**The FINAL-NIGHT notice** was hand-appended to all 10 `continuity_night_3.json` files, in both blocks:
- All 10 carry `final_night_notice_appended: true` (9 with the timestamp 2026-05-11T12:18). The timestamps run microseconds apart, which points to a throwaway script.
- No code in either repo writes it (CONFIRMED).
- It is event-specific (*"Act Five (Beastopia) at 20:00"*) and caused the C42 false positive. D7.

### 3.6 Duplicated event data (CONFIRMED)

- Dates in 4 places: `conference_facts.dates`, `DATE_TO_NIGHT`, `DAY_TO_DATE`, and `reference/sessions.json`.
- `council_config.audience` is byte-equal to `audience_profile.participant_profile`.
- The roster names equal `council_config.members[].name`.

**Test files pinning Athens nights/days:** 19, using the pattern `athens_night|Day One|Day Two|Day Three|DAY_TO_RUN|NIGHT_TO_RUN_DIR|NIGHT_TO_DAY|DATE_TO_NIGHT|ATHENS_NIGHTS|night=4|night must be|deployment=` over `runtime/tests`, `runtime/ingest/tests`, `personas/tests` (the review gets 12–17 with other patterns).

---

## 4. `event_config.json`

### 4.1 Schema (Athens instance)

```jsonc
{
  "schema_version": 1,
  "event_id": "athens-2026",
  // The former conference_facts.json, VERBATIM; load_conference_facts() returns
  // this dict, so every existing consumer gets byte-identical input.
  "facts": { "conference_name": "World Beautiful Business Forum", "host_organization": "House of Beautiful Business",
             "host_organization_short": "HoBB", "dates": "May 7-10, 2026", "…": "…all current keys…" },
  "schedule": {
    "timezone": "+03:00",
    "run_dir_template": "athens_night_{n}",
    "days": [
      {"label": "Day Zero",  "date": "2026-05-06"},
      {"label": "Day One",   "date": "2026-05-07", "night": 1},
      {"label": "Day Two",   "date": "2026-05-08", "night": 2},
      {"label": "Day Three", "date": "2026-05-09", "night": 3},
      {"label": "Day Four",  "date": "2026-05-10"},
      {"label": "Special Activations", "date": null}
    ]
  },
  "frame": {
    "assembly": "a panel of historical voices that comment on conference panels overnight",
    "publication": "with their artifacts published the next morning to a real audience",
    "audience_short": "business leaders, conference attendees"
  },
  "final_night_notice": null   // optional (D7); null for Athens, whose notice sits in the continuity files
}
```

**Validation:** nights 1..N with no gaps; `{n}` exactly once in the template; ISO or null dates; unique labels.

**No schedule (one-shot):** an event without `schedule` gets `night_count = 1` and template `night_{n}`. That's safe only with C23 moved to `night_for_run_dir`.

**Deliberately not in the schema:**
- A rename of "night" (it's in the CLI, files, published paths and URLs).
- Model choice (`model_routing.json`).
- Pipeline toggles.
- Per-voice lengths (deployment card).
- Audience text (`audience_profile.json`).

### 4.2 Loader: `flows/shared/event_config.py`

One module, byte-identical in `runtime/` and `personas/`, following the `model_routing.py` twin and its parity test (`runtime/tests/test_model_routing.py:113-115`).

| Function | Replaces |
|---|---|
| `load_event_config(project_root)` | — (fails loudly if missing) |
| `facts(cfg)` | `load_conference_facts()` body (`io.py:359-390`), C24 `:655` |
| `night_numbers(cfg)` | `ATHENS_NIGHTS`, all `choices`, both range guards, C24 `:43` |
| `night_count(cfg)`, `is_final_night(cfg, n)` | `night < 3`, `next_night <= 3`, the template `night >= 3` |
| `run_dir_name(cfg, n)` / `night_for_run_dir(cfg, name)` | 6 builders/parsers incl. C23, C24 `:601` |
| `day_label`, `night_for_day`, `night_for_date`, `processed_day_labels` | `NIGHT_TO_DAY` ×2, `night_to_day`, `DAY_TO_RUN`, `DATE_TO_NIGHT`, `days_ordered`, C25 |
| `day_dates(cfg)` | `DAY_TO_DATE`, `TZ_OFFSET`, C15 `:344` |

**CLI change:** `--night` becomes `type=int` without `choices`, validated after `--project` resolves (one helper, 5 CLIs).

### 4.3 How each hardcoding reads it

| Inventory IDs | Reads |
|---|---|
| C1, C2, C6, C7, C11, C12, C15, C25 | `schedule.days[]` (labels, nights, dates), `schedule.timezone` |
| C3, C5, C8, C9, C14, C23, C24 | `run_dir_template` via `run_dir_name` / `night_for_run_dir`; `night_numbers` |
| C4, C10, C16 | `is_final_night` |
| C11, C12, C16–C20 (choices/ranges) | `night_numbers` |
| P3, P5, P6, R5, R9, C24 `:655` | `facts` |
| R1–R3 | `frame.*` via a small substitution helper in `step2_validation.py` |
| R4 | `night_count` |
| C13, C21, C22, C26, R6–R8, R10 | not read (kept or out) |

### 4.4 Deployment card (Step 3): `voices/<slug>/08_deployment_card.json`

```jsonc
{
  "schema_version": 1,
  "deployment_id": "athens-2026",
  "voice_slug": "plato",
  "voice_card_sha256": "…sha256 of the voice card minus metadata…",
  "fields": {
    "voice_temporal_stance": {"default": "You have been called to the assembly that gathers in YOUR city — …", "anchored_override": null},
    "length_and_format_constraints": "…",
    "unique_contribution": "…",
    "bold_engagement_topics": [ … ],
    "smoke_test_chains": [ … ]
  },
  "provenance": {"deployment_context": "…", "sources": {"voice_temporal_stance": "operator short draft, athens-2026 08a8253"}}
}
```

- A **new** deployment may store the stance as a plain string: the voice unwrap passes strings through. The editor and the safeguards validator would then render that string as-is.
- In Step 3, `fields` gains `engagement_criterion`. It gains `generation_parameters` only with 2.2.
- The editor's card also carries the former C18 role paragraph.

---

## 5. Migration plan (Athens stays reproducible)

**The bar is prompt identity.** Model outputs were never reproducible, so after each step, re-assembling any Athens prompt from `athens-2026` must give the same bytes — or change only where the step says so. Models are pinned by `model_routing.json` (C63).

**Step 0 — Golden hashes first (no behavior change).** A read-only script, `verify_athens_golden.py --project <athens-2026>`, plus a hash table. It records sha256 of:
- every voice system prompt: 10 voices × Steps 1–3 × Nights 1–3, `(prefix, tail)`;
- the editor's × Nights 1–3;
- the Step-1 and Step-2 validator **system and user** prompts (both user prompts render the stance);
- the Provocateur's THE GATHERING block.

Plus one permanent unit test: a fixture card split into voice + deployment cards must render byte-identically through every reader in §1. No existing test compares assembled prompts against the shipped cards.

**Step 1 — `event_config.json` (C52). Build now.**
1. Add the loader twin (§4.2).
2. Write `athens-2026/event_config.json` (facts verbatim) — athens-2026 commit needs operator OK.
3. Replace C1–C12, C14–C20, C23–C25 and P3, P5, P6; add the R1–R3 substitution helper and R4/R5.
4. Switch C24 `:655` **before** deleting `conference_facts.json`.
5. Update the 19 test files; most use `athens_night_N` only as fixture names, which an Athens-shaped fixture config reproduces.

**Verify:** voice prompts, THE GATHERING and the editor prefix are unchanged. Expected re-hashes, and only these:
- the validator system prompts (R1–R3 wording, R2 "Athens" removed);
- the editor tail (R4 "(1, 2, or 3)" → "of 3").

R5 renders the same text for Athens.

**Step 2 — Count-agnostic continuity. Build now.**
- Replace the gates at `voice_flow.py:589`, C4 and C10 with `is_final_night`.
- Settle D15 (C68 A10), and D7 (Athens keeps `null`).
- **Verify:** the golden hashes are unchanged. Add a 4-night fixture test: continuity runs after nights 1–3 and skips after night 4.

**Step 3 — Split the cards *and* clean the voice cards, together.** Gated on a second deployment being prepared, or on the operator's decision (D10, D14).
- **Split mechanics:**
  - `split_cards.py` moves the 5 D fields **verbatim** into `08_deployment_card.json`, and removes the continuity nulls.
  - Pin = sha256 of the voice card minus `metadata`.
  - Add `load_card` + the field router (§1) for the voice loader, editor loader, chat builder and the persona pipeline (P7).
  - The Step-1/Step-2 validators receive the merged card from `voice_flow`, as today.
- **Voice card v2:**
  - Prompt edits S1–S5.
  - Card patches from §2.1:
    - `medium` ×8, `technical_capabilities` ×1, `characteristic_output_structure` ×2, `relationship_to_detailed_response` ×2, `aesthetic_qualities` ×1, `stance_tendency` ×2, `default_questions` ×1, `disagreement_protocol` ×2
    - the engagement criterion ×9, moved to D
    - the `length_and_format_constraints` formatting that belongs to the form, moved into `medium`
  - Re-validate per the cross-cutting DON'T (sentinel regen / chat-test, thinking on, spend cap).
- **Athens:**
  - **`athens-2026` is not rewritten.** Its unsplit cards keep working because the deployment card is optional (§1). Its golden hashes stay valid.
  - v2 cards live in the next project or, later, the hub library.

**Step 4 — Deployment-card generator ("Pass D"). Shelved.** Hand-author the next event's deployment cards: 10 × 5 short fields, starting from the Athens cards and the carry-forward list, as Athens effectively did.

**Interactions:**
- **Stage 4 item 1 vs S4 (D8):** per the review, the Stage 4 backport draft (`voices/DESIGN_2026_09_28_stage4_prompt_backport.md`, `47dcc7a`) rewrites the stance block **inside** Pass 2. I haven't read that file; it isn't at `40fe490`.
- **FU#55 Stage 0 `forms[].length` vs row 33 (D9):** reconcile with `DESIGN_2026_09_28_family_of_forms.md`.
- **C42:** lands in the same edit as R2.

---

## 6. Net-complexity check

**Steps 0–2 (event_config + continuity) — nets out. Build now.**

| | Items |
|---|---|
| Removed | `DAY_TO_RUN`; `NIGHT_TO_DAY` ×2; `NIGHT_TO_RUN_DIR`; `DATE_TO_NIGHT`; `ATHENS_NIGHTS`; `NIGHTS`; 2 `app.py` literals and the C25 map; `DAY_TO_DATE`/`DAY_TO_INDEX`/`TZ_OFFSET` and the `:344` list. 5 CLI `choices`, 2 range guards, 4 "night 3 is last" checks, 6 run-dir builders/parsers. One file (`conference_facts.json`); dates go from 4 copies to 1. The hand-injected final-night notice (if D7 is adopted). |
| Added | `event_config.py` ×2 (~80 lines + parity test); a `--night` validation helper; a ~5-line substitution helper for the validators; 3 `frame` phrases; the golden script and hash table. |

*Inference:* every addition replaces a special case that existed in more than one place, and the frame phrases replace text that was already wrong once (Munich, C55).

**Step 3 (the card split) — does not net out on its own (review F40, adopted).**

| | Items |
|---|---|
| Adds | A file type ×11; `load_card` + overlap/pin checks at ≥4 loaders; a write router in the persona pipeline (~8 sites, P7); pin friction on every voice-card patch; a permanent split-render test. |
| Removes | 2 null placeholders, their exclusion entries and 2 chat-strip entries; the unused `deployment` parameter. |
| Benefit | Reusable, event-free voice cards; per-event surgery (the 10 stance rewrites in `08a8253`, the §27 length surgery) becomes editing deployment cards. **This arrives only with the voice-card clean-up**, so the two go together. |

**Stays shelved:**
- Pass D (a generator).
- `generation_parameters` (a second model source beside `model_routing.json`).
- `--skip-step3` in config (profiles, 2.3).
- `final_night_notice` is marginal (D7).
- The editor gains little from the split until C57.

---

## 7. Open operator decisions

| # | Decision | Options and trade-offs | Recommendation |
|---|---|---|---|
| D1 | Partition departures from FU#42 | (a) As §2.1. (b) FU#42 as written (predates the AF reframe). | (a) |
| D2 | Artifact fields: which card? | (a) Form constitution in V, cleaned in Step 3 (consistent with §11.6; costs re-validation). (b) The whole ARTIFACT section in D (event-free immediately; contradicts §11.6's premise; duplicates the form menu per deployment). | (a) |
| D3 | Where event config lives | (a) `event_config.json` absorbs `conference_facts.json`. (b) A separate new file (5th root file; dates duplicated). (c) Extend `conference_facts.json` (conference-shaped name; mixes config into a facts file). | (a); switch C24 `:655` first |
| D4 | Where voice cards live (Step 3) | (a) A copy per project + pin. (b) A shared library root (the hub). | (a) now, (b) with the hub |
| D5 | Pin strictness | Hard error / warning / none. The pin excludes `metadata`, so pipeline metadata writes don't trip it; only real voice-field changes do. | Hard error, with the re-pin command in the message |
| D6 | Voice card file name | Keep `07_persona_card_assembled.json` (20 referencing files) or rename it. | Keep, with a `metadata.card_schema` marker |
| D7 | Final-night notice | Hand-injection (as at Athens) or `event_config.final_night_notice`. The C42 continuity exemption must cover the latter. | Config field when the next multi-night run is planned |
| D8 | Stage 4 item 1 vs S4 | (a) Remove the stance block from Pass 2 in Stage 4 and keep the AF-LEADS template in an authoring note. (b) Rewrite it in Pass 2 (the Stage 4 draft's choice, per the review), then move it in Step 3. | (a); with (b) the rewrite is thrown away in Step 3 |
| D9 | Family-of-forms lengths | (a) Per-form windows in the deployment card. (b) `forms[].length` in the voice card. | (a) |
| D10 | Step 3 timing and spend | Now, or when a second deployment is prepared. Cost: a 10-voice re-validation. | When a second deployment is prepared |
| D11 | Editor identity | `council_config.editor_slug` + the same loader, or leave until C57. | `editor_slug` now (Step 1); loader in Step 3 |
| D12 | `--skip-step3` | Leave in the orchestrator, or move to config. | Leave (2.3) |
| D13 | Other duplicates | Collapse or leave (byte-equal today). | Leave; note it |
| D14 | **Split timing (new)** | (a) Split together with the voice-card clean-up (Step 3). (b) Split now, clean later (adds surface without the benefit; review F40). | (a) |
| D15 | **C68 A10 (new)** | (a) Fix the spec: last-night summary + accumulated moves register (today's behaviour; bounded context at any N). (b) Fix the code to merge all prior nights (context grows with N; needs a merge rule). | (a) |

---

## 8. Changes after the review (2026-09-29)

| Review ID | Change |
|---|---|
| F40, Q5 | The split moves from "Phase A with C52" to Step 3, together with the clean-up. §0, §5 and §6 are re-sequenced; D14 is added. |
| F8, Q1 | Values move **verbatim**; Tim's stance (and every voice's) stays a dict. The claim that the unwrap is "stored as a string" is removed. The byte-identity claim is scoped to renderers that see unchanged values. |
| F26 | The unwrap is no longer deleted (second caller `step1_validation.py:151,159`); only its unused `deployment` parameter goes. |
| F38, Q3 | Added P7 and the §1 read/write rule for the persona pipeline. The pin excludes `metadata`, and D5 is restated. `athens-2026` cards are **not** rewritten (the deployment card is optional in the merge). |
| F2, F16 | Reader frame 8/10 → 9/10; engagement criterion 8/10 → 9/10 (Cleopatra `[4]` added); patch count ×8 → ×9. |
| F17, F19 | Counts raised: `bold_engagement_topics` ≥9/10; `unique_contribution` 9/10 (Cleopatra and Scheherazade quotes re-checked). |
| F20 | Smoke-test evidence restated: 42 chains; "provocation" is a key; "Athens" appears 11 times in values. |
| F4, F27 | Added C23 (→ config), C24, C25, C15 `:344`, C26. File count 15 → 18. |
| F29 | The FU#57 strips stay; only the continuity strips go. |
| F31 | Added the validator substitution helper and the list of expected re-hashes (validators; editor tail via R4). |
| F33 | C68 A10 added (§3.5, D15). |
| F10, F25, F9/F28 | The C48 path is fixed; C1 is `:91-98`; the HEAD +5 offset for persona lines is noted in the header. |
| F37 | The test-file grep pattern is stated. |
| Review note | Scan method added (Appendix A). |

**Where I disagree with the review:**
- **F4 lists `card_assembly.py:340-345` ("THIS CONFERENCE") as event wording.** I keep it (C26). It is conference-*shaped* cadence, like the colophon (C21), and names no event. It belongs to the conference profile (2.3), not `event_config`.
- Nothing else. F9/F28 are line offsets at HEAD; the draft is pinned to `40fe490`, where its lines are correct.

---

## Appendix A — how the counts were made (reproducible offline)

- **Scope:** Python over `athens-2026/voices/*/07_persona_card_assembled.json` and `editor/tim_leberecht/…`.
- **Walk:** walk every **string value** recursively (dict keys excluded; the first pass wrongly counted keys, F20), and skip `metadata` and `smoke_test_chains` unless a row says otherwise.
- **Terms:** `breakfast|morning|coffee|\bcup\b|\btea\b|\b750\b|audience|\breaders?\b|conference|panel|[Aa]ssembly|gathering|Athens|WBBF|Forum|2026`, plus the audience-profile phrases *performing reception*, *well-curated*, *secular but enchantable*, *extractive systems*, *more-than-human democracy*.
- **Classification:** every hit was read in context (±70 characters) and classified by hand as voice-native or event-coupled.
- **Code and prompt inventory:** `git grep` at `40fe490` for the named constants, `choices`, `(1, 2, 3)`, `athens_night`, `Day One|Two|Three`, and `night [<>]=? ?3`.
