# DESIGN (draft) — split card (FU#42) + event config (C52)

**Status:** design draft for operator review. Nothing here is decided and nothing is built. Roadmap §2.1, Stage 5.
**Written:** 2026-09-28/29 by a Fable 5.1 session, per `BRIEF_2026_09_28_fable_batch2.md` Task 1.
**Canonical homes:** FU#42 (`FOLLOW_UPS.md`, voices §10) · runtime C52 (and C55, whose stopgap this finishes) · roadmap `PLAN_2026_06_12_post_athens_roadmap.md` §2.1.
**Labels:** **CONFIRMED** = seen in code or data at the path given. **PLAUSIBLE** = likely, not checked. *Inference* = my reasoning, marked as such.
**Method:** read-only. Offline Python scripts (no model calls) tabulated all 11 shipped cards in `athens-2026` (10 voices + Tim) field by field and scanned every string for event terms; `git grep` swept both pipelines. Scripts are in the session scratchpad, not the repo.

---

## 0. Outcome

1. **Three layers, each with one job.** A **voice card** (who the voice is; no event content; byte-stable), a **deployment card** per voice per event (how this event frames and sizes the voice: temporal stance, length, the council- and audience-relative fields), and **`event_config.json`** per project (the event's facts, its day/night schedule, and the few frame phrases prompts need). `event_config.json` absorbs `conference_facts.json`, so the project gains no file.
2. **The partition is mostly clean, with one exception.** Of the card's 44 top-level keys, 37 go to the voice card, 5 to the deployment card, and the 2 continuity placeholders leave the card. **The exception:** the Athens reader frame ("the reader at breakfast", "one piece per morning", "before the cup goes cold") is woven into voice-native sentences of the artifact fields in 8 of 10 voices. It can't be cut out without changing the text, so the voice card can't be event-free on day one without breaking Athens reproducibility.
3. **So the migration has two phases.** **Phase A** splits the files mechanically; every Athens system prompt stays byte-identical, checked against golden hashes taken first. **Phase B** removes the event wording from the voice cards, which creates voice card v2 and needs per-voice re-validation. Phase B is needed only before a second deployment uses these voices.
4. **Hardcoding is smaller than feared in code and wider in cards.** Code: 5 hardcoded maps, 5 `choices=(1,2,3)` CLIs, 2 night-range guards, 4 "night 3 is last" checks, and 5 run-dir name builders/parsers, across 15 runtime files. Continuity is already count-agnostic except two gates. Prompts: the 4 Step-2 validator prompts and the editor prompt carry the event frame. **4** persona prompts are event-coupled, not the 5 the roadmap lists (§3.4).
5. **Net-complexity:** Phase A plus event_config removes more than it adds (§6). Three parts don't net out and should stay shelved: a deployment-card generator pass, per-voice `generation_parameters`, and moving `--skip-step3` into config.

---

## 1. The design on one page

```
<PROJECT_ROOT>/                         (one project = one event, as today)
├── event_config.json                   NEW — replaces conference_facts.json
│     facts{}     ← the former conference_facts.json, verbatim
│     schedule{}  ← days, dates, which days are processed nights, run-dir template
│     frame{}     ← 3 short phrases the validator/editor prompts need
├── audience_profile.json, council_config.json, panel_roster.json   (unchanged)
└── voices/<slug>/
      07_persona_card_assembled.json    the VOICE CARD (37 fields; deployment fields removed)
      08_deployment_card.json           NEW — this voice at this event (5 fields + provenance + sha256 pin of the voice card)
      continuity_night_<N>.json         runtime state, unchanged
```

**Loader rule (one function, used by the voice pipeline, the editor, and the chat builder):**
`card = voice_card ∪ deployment_card.fields`. A field in both → hard error. Deployment card's `voice_card_sha256` ≠ sha256 of the voice card on disk → hard error, with the one-line re-pin command in the message. Continuity overlay afterwards, exactly as today (`runtime/flows/voice/card_assembly.py:187-209`).

**Why prompts stay byte-identical:** the runtime renders fields by fixed tuples in fixed order (`card_assembly.py:82-152`, `_render_section` at `:285-310`), not by dict order. A field moved between files renders in the same place with the same value. CONFIRMED by reading the code.

**Build-side principle (for Phase B):** *voice passes are event-blind.* Passes 1.x, 2, 3, 4a, 4b(voice part) and 6 never read `event_config`, `audience_profile` or `council_config`. Only the deployment step reads them: the deployment half of Pass 5, Pass 7b, and a future deployment-card pass if one is ever built. This is what makes the voice card reusable. Today Pass 5 and 7b read the event (`personas/run_persona_pipeline.py:743-753`, `:1542-1544`), and four prompts name Athens directly (§3.4).

This matches the retired C48 design's rule (`runtime/DESIGN_voice_deployment_context.md`, "Why it was retired" and the closing principle): descriptive event facts stay out of the persona card's prescriptive layer. Here the descriptive facts live in `event_config.facts`. The per-voice, per-event *prescriptive* text, which Athens put inside the cards (the temporal-stance lead, the length windows), lives in the deployment card.

---

## 2. Field-by-field partition

**V** = voice card · **D** = deployment card · **—** = leaves the card. "Athens evidence" lists the event-specific content actually found in the shipped cards (CONFIRMED, `athens-2026/voices/*/07_persona_card_assembled.json`). Tim's card is covered separately in §2.2.

### 2.1 The 44 keys (voices)

| # | Field | → | Reason | Athens evidence (10 voice cards) |
|---|---|---|---|---|
| 1–4 | `voice_name`, `voice_mode`, `pipeline_version`, `generated_date` | V | Identity and provenance of the voice build. | Clean. (`voice_mode` is null for Whanganui, as `node0_validation.py` allows for `subtype: system`.) |
| 5 | `council_member_name` | V | Identity ("You are …", `card_assembly.py:421-422`). | Clean. |
| 6–9 | `epistemic_frame_statement`, `world`, `formative_experience`, `character` | V | Who the voice is. | Clean. "Gathering", "panel" and "night" hits are the voice's own (Marley's Nyabinghi gathering; the Wai 167 Tribunal panel; Dostoevsky's execution morning). |
| 10 | `knowledge_boundary` | V | The voice's horizon. It holds most of the dates the temporal stance repeats (see carry-forward list below). | Clean. |
| 11 | `voice_temporal_stance` | **D** | Event-bound in 11/11 cards. The lead sentence names the event: *"You have been called to the assembly that gathers in Athens — present in their time, observing the panels but not entering them as participant."* 7 voices use it verbatim; Plato: *"gathers in YOUR city"*; Octopus: *"You register the assembly as it convenes in Athens"*; Whanganui: *"I have been called — as the construction stewarding the Te Awa Tupua published record — to the assembly that gathers in Athens"*. The panel shape recurs later in the text (*"When the panels' questions require translation…"* in 8 voices). So the field can't be split by sentence. It moves whole, stored as the unwrapped string. | `anchored_override` is null in 11/11, so the dict collapses to one string with no loss. The final Athens text is the operator's short drafts (athens-2026 `08a8253`); the AF-leads history is in voices §31 Gap-K. |
| 12 | `translation_protocol` | V | The voice's method. Its "reader/listener/questioner" means whoever asks, which holds in any deployment. | Clean. |
| 13 | `topics_requiring_care` | V | Constitutional (FU#42 called it a hybrid; the Athens content doesn't bear that out). | Clean for voices. The "Athens"/"Assembly" hits are native (Plato's Athens; Marley's "National Assembly Resolution 23"). |
| 14 | `hard_limits` | V | Constitutional. | Clean. |
| 15–19 | `constitution`, `concept_lexicon`, `reasoning_method`, `finds_compelling`, `resists` | V | Intellectual core. | Clean (the "provocation" hits are voice-native: Dostoevsky's *provokatsiia*, `constitution[17]`). |
| 20–26 | `rhetorical_mode`, `characteristic_moves`, `register_and_tone`, `metaphorical_repertoire`, `preferred_vocabulary`, `banned_language`, `banned_modes` | V | How the voice speaks. | Clean. |
| 27 | `medium` | V | The voice's form family. This is FU#55 Stage 0's `{default_form, forms[]}`, and the operator exempted family-of-forms from the gate *as voice capability* (PRODUCT §11.6). | **Contaminated in 8/10** (all but Plato and Battuta). Examples: Whanganui *"I write one piece of prose each morning… The piece is for reading at breakfast"*; Marley *"Two shapes, one morning piece"*; Cleopatra *"this morning produces one more"*; Dostoevsky *"opened over morning tea, finished before the cup goes cold"*; Scheherazade *"The reader at breakfast should feel they have entered the chamber a few sentences late"*; Octopus *"The runtime renders the JSON as a 10-15-second looping WebGL animation"* (an output-mode fact). → Phase B. |
| 28 | `technical_capabilities` | V | What the medium needs. Which renderers exist is deployment output config (B7), not card content. | Dostoevsky *"(English on this morning)"*. → Phase B. |
| 29 | `characteristic_output_structure` | V | Arc per form (FU#55 `forms[].arc`). | Cleopatra *"where the morning's matter requires it"*; Octopus *"the audience meets my skin first"*. → Phase B. |
| 30 | `relationship_to_detailed_response` | V | Step 1 → Step 2 transformation craft. | Octopus *"The reader at breakfast meets a body and a question"*; Whanganui *"In the public morning piece"*. → Phase B. |
| 31 | `aesthetic_qualities` | V | Gestalt of the voice's work. | Ada *"The reader at breakfast should feel…"*. → Phase B. |
| 32 | `stance_tendency` | V | The voice's pull (not the Derive enum of the same name; see roadmap 0.3). | Cleopatra *"If the morning matter resists this stance"*; Whanganui *"I do not flatter the audience"* (mild). → Phase B. |
| 33 | `length_and_format_constraints` | **D** | Length is an output decision. At Athens the operator set it per event: the §27 length-cap surgery gave Dostoevsky and Arendt 350–750 words and Octopus 350–500 (STATE "Voice-build state"). | Cup/coffee/morning window in 6/10 (Marley *"readable in the time it take to drink the morning cup"*, Whanganui *"350–550 words of prose for the morning audience. One piece per day"*, plus Cleopatra, Dostoevsky, Arendt, Octopus). It also holds voice-native formatting (Plato's speaker names; Marley's Patwa rule; Octopus's `chromatophore_display` JSON channel). In Phase B the formatting that belongs to the form moves into `medium`. |
| 34 | `quality_criteria` | V (fidelity criteria) + **D** (engagement criterion) | The fidelity criteria test voice fields by name (Card v2 spec). The final "+1" criterion is audience engagement, generated from `persona_pass_4b_artifact.md:105` (*"Could this, on its own, make an audience engage with its intent?"*). | Engagement criterion names the Athens reader in 8/10: Ada `[4]` *"a reader at breakfast, encountering this cold"*, Dostoevsky `[4]`, Battuta `[4]`, Octopus `[5]`, Scheherazade `[4]` *"make 750 strangers turn the page"*, Whanganui `[4]`, Marley `[4]` *"over coffee"*, and Arendt inside a **single string** (not a list). **Phase A:** the whole field stays V (the string form blocks a byte-identical split). **Phase B:** the engagement criterion moves to D as `engagement_criterion`. |
| 35 | `bold_engagement_topics` | **D** | Pass 5 generates it *from* the event (`persona_pass_5_user.md:10-40` DEPLOYMENT CONTEXT block). Never loaded at runtime (FU#57). | 8/10 quote or address the Athens audience. Marley `[4]` *"Your well-curated openness itself. You pay the premium not to cluster"* (audience_profile verbatim); Battuta `[2]` *"When you call yourselves 'secular but enchantable'"*; Octopus `[5]` *"The audience is good at performing reception"*; Plato `[2]` *"The Forum's own craft is on trial here"*; Marley `[5]` *"Athens is a holy and a downpressing city"*. |
| 36 | `default_questions` | V | Pass 5 defines them as questions *"the voice brings to ANY material"*. FU#42 put them in D; the content doesn't support that. | Clean except Scheherazade `[4]` *"has reception been performed…"*, an echo of the audience profile's *"performing reception"*. → Phase B. |
| 37 | `disagreement_protocol` | V | How the voice disagrees (FU#42: hybrid). | Clean except Octopus *"I will not perform reception I have not been able to register"* (the same echo) and Marley *"than from the panel"*. → Phase B. |
| 38 | `unique_contribution` | **D** | Defined relative to the council (`voice_step1_reasoning.md:21`: *"what no other voice on the panel sees"*) and, in Athens content, to the audience. It changes when either changes. | 7/10 relative: Ada *"this audience needs it cutting through both"*, *"another voice on this panel"*; Arendt *"an instrument this audience particularly lacks"*; Plato *"I will not let your gathering speak of decision procedures"*; Battuta *"your new gathering"*; Whanganui *"no other voice at this panel"*; Marley *"a clock built for the conference schedule"*; Octopus *"performed reception"*. |
| 39 | `curated_corpus_passages` | V | The voice's own words. (`corpus_metadata` is still stripped at runtime.) | Clean. |
| 40 | `smoke_test_chains` | **D** | Build evidence generated *against the event* (Pass 7b reads `conference_context`, `run_persona_pipeline.py:1542-1544`). Never loaded. | 42 "provocation" and 15 "Athens" hits across all 11 cards' chains (Tim included). |
| 41 | `reference_only_passages` | V | Copyright-tier corpus; Step 1 only. | `runtime_contract_note` says "audience reads", which is generic boilerplate. |
| 42–43 | `continuity_block_if_night_2`, `continuity_block_artifact_if_night_2` | **—** | Runtime state. It already lives in `continuity_night_<N>.json` and is overlaid by night-templated keys (`card_assembly.py:197-202`). The card placeholders are null, exist only for night 2, and are never rendered. Removing them changes no prompt byte. | Null in 11/11. |
| 44 | `metadata` | V | Build provenance, dropped at runtime. **Except** `metadata.deployment_context` (the conference paragraph, `run_persona_pipeline.py:1782`), which moves to the deployment card's `provenance`. | — |
| new | `generation_parameters` | D (later) | Per-voice model, vendor or temperature. **Do not add yet:** `model_routing.json` (C63) is the single model source, and a second source should only arrive with the vendor layer (2.2). | — |
| new | `engagement_criterion` | D (Phase B) | Split from `quality_criteria` (row 34). | — |
| new (vatican) | `annotation_register`, `silent_threshold` | D | Vatican spec §6; output-mode specific. | — |

**Totals:** 37 V · 5 D (`voice_temporal_stance`, `length_and_format_constraints`, `bold_engagement_topics`, `unique_contribution`, `smoke_test_chains`) plus 2 partial moves (the engagement criterion in Phase B; `metadata.deployment_context`) · 2 removed.

**Where this departs from FU#42 (2026-04-25):**
- `voice_temporal_stance` moves V→D. The AF reframe (§30/§31 Gap-K) made it event-bound after FU#42 was written. The roadmap §2.1 already agrees.
- `default_questions`, `disagreement_protocol` and the fidelity part of `quality_criteria` move D→V. The content is constitutional; only the one engagement criterion is audience-relative.

**Carry-forward list for new deployments (CONFIRMED only in `voice_temporal_stance`, nowhere else in the card):** Dostoevsky's Old Style/New Style dating rule; Battuta's hijrī counting ("Christian reckoning available as translator's convenience"); Octopus's *"no calendar, no year"*; birth years for Marley (1945), Dostoevsky (1821), Arendt (1906) and Plato (428/427). Death dates, standing places and the other facts also sit in `knowledge_boundary`. Whoever drafts a voice's stance for the next event must carry these four items across. *Inference:* the cheapest guard is to start each new draft from the Athens deployment card.

**Runtime routing is unchanged.** `voice_temporal_stance` stays in the cached prefix (BOUNDARIES) at every step, and `unique_contribution` stays in ENGAGEMENT at every step. So Step 1 still sees two deployment fields. That is intended: AF-LEADS was a deliberate all-steps choice (§31 Gap-K).

### 2.2 The editor card (Tim) — the split doesn't make it portable

CONFIRMED: Tim's card names Athens, WBBF or May 2026 in **identity-level** fields, not only in deployment ones:
- `knowledge_boundary`: *"you are alive in May 2026 visibly retrofitting it in print — weekly Beauty Shots, the Athens forum"*
- `constitution[16]`: *"a gathering that has scaled to 750 attendees, eight Athens venues, ten program tracks"*
- `reasoning_method[7]`: *"The 2026 World Beautiful Business Forum in Athens is structured as five acts"*
- `topics_requiring_care[2]`: *"As of May 2026, eight months of weekly Beauty Shots later"*
- `curated_corpus_passages.passages[0]`: id `monster_athens_2026`
- `formative_experience`, `epistemic_frame_statement`, `world`, `characteristic_moves[6]`, `[11]`, `preferred_vocabulary[10]`

Tim is a living person who hosts the event; his biography and knowledge horizon move with each event. **Recommendation:** use the same loader for symmetry (one code path) and move his 5 D fields. His `voice_temporal_stance` (the only card with a runtime `{night}` placeholder, filled at `editor/card_assembly.py:366-367`) moves to his deployment card with the placeholder intact. Accept that his voice card is re-authored for any other event. Making the editor itself a variable is C57's job, not this design's.

---

## 3. Inventory of event hardcoding

IDs are referenced in §4.3. **Disposition:** *config* = reads `event_config` · *delete* · *keep* (already event-neutral) · *out* (not event data; named where it belongs).

### 3.1 Runtime code

| ID | file:line | What | Disposition |
|---|---|---|---|
| C1 | `runtime/ingest/config.py:89-98` | `DAY_TO_RUN` — "Day One/Two/Three" → `athens_night_1/2/3`; Day Zero, Day Four and Special Activations → None | config: `schedule.days[]` + `run_dir_template`. The None entries are deleted (any unlisted label already resolves to None). |
| C2 | `runtime/ingest/sessions.py:158-160` | `run_for_session` uses `DAY_TO_RUN` | config (follows C1) |
| C3 | `runtime/ingest/dashboard.py:29-35` | `ATHENS_NIGHTS = (1, 2, 3)`; `run_dir_for_night` → `f"athens_night_{night}"` | config |
| C4 | `runtime/ingest/dashboard.py:606-617` | `next_night <= 3` / `> 3`, "Night 3 is the last" | config: `is_final_night(n)` |
| C5 | `runtime/ingest/dashboard.py:1355, 1361` | `latest_active_night` iterates `reversed(ATHENS_NIGHTS)` | config (follows C3) |
| C6 | `runtime/ingest/app.py:397` | `days_ordered = [… "Day One", "Day Two", "Day Three"]` | config |
| C7 | `runtime/ingest/app.py:768` | `night_to_day = {1: "Day One", 2: "Day Two", 3: "Day Three"}` | config |
| C8 | `runtime/ingest/app.py:731, 750, 767, 827, 850, 953, 972, 992, 1010, 1022, 1051, 1063, 1081, 1093, 1111` (guards) and `:738, 812, 837, 999, 1037, 1070, 1100` (`all_nights`) | `night in dashboard.ATHENS_NIGHTS` | config (mechanical, follows C3) |
| C9 | `runtime/ingest/templates/admin_transcription.html:43` | `'runs/athens_night_' ~ night` | config: the view passes the run-dir name |
| C10 | `runtime/ingest/templates/admin_voice.html:237, 239` (logic); `:104`, `:307` (text: "expected on Athens Nights 2/3", "Nights 2+3") | Night-3 ceiling in the template | config: the view passes `is_final`; text made count-neutral |
| C11 | `runtime/flows/vendor_intake.py:91-95` (`NIGHT_TO_DAY`, `NIGHT_TO_RUN_DIR`), `:409`, `:440` (uses), `:527` (help), `:543` (`choices=(1, 2, 3)`) | Night↔day↔run-dir maps | config. `flows/` still must not import `ingest/`; both import the shared loader. |
| C12 | `runtime/scripts/overnight_orchestrator.py:66-71` (`DATE_TO_NIGHT`, `NIGHT_TO_DAY`), `:97-99` (run dir), `:105-112`, `:596` (`choices=[1, 2, 3]`), `:630-635` (date lookup), docstring `:29-31` | The nightly scheduler's calendar | config |
| C13 | `runtime/scripts/overnight_orchestrator.py:481` | `--skip-step3` always passed (the A1 Athens decision) | **out** — a pipeline-profile knob, not event data. Leave until 2.3 profiles (decision D12). |
| C14 | `runtime/scripts/reset_run.py:60-64` (regex `athens_night_(\d+)$`), `:161` (help) | Parses the night from the run-dir name | config: `night_for_run_dir(name)` inverts the template |
| C15 | `runtime/scripts/generate_sessions_json.py:40-55` (`DAY_TO_DATE`, `DAY_TO_INDEX`, `TZ_OFFSET = "+03:00"`) | Athens dates/timezone in the program importer | config for the date table only. The script parses the WBBF program HTML, so it stays an Athens-format importer. |
| C16 | `runtime/flows/voice_flow.py:589` (`night < 3` continuity gate), `:612` (log), `:697` (`choices=[1, 2, 3]`) | 3-night ceiling | config |
| C17 | `runtime/flows/voice/card_assembly.py:401` (`night not in (1, 2, 3)`); `:240-282` (`_unwrap_voice_temporal_stance(…, deployment="athens")`, branch at `:269`); call at `:306` | Night range; the "athens" deployment hook | range → config. The unwrap function is **deleted** (the deployment card holds one string). |
| C18 | `runtime/flows/editor/card_assembly.py:308` (range); `:110` (`EDITOR_CARD_SUBPATH = editor/tim_leberecht/…`); `:264-277` (hardcoded "YOUR ROLE" paragraph: *"You are the Editor of this Assembly… not 'breakfast reading'…"*); `:320` (fallback name `"Tim Leberecht"`) | Editor range, identity and Athens-specific prescriptive text | range → config. Editor slug → `council_config.editor_slug` (decision D11). The role paragraph → Tim's deployment card (it's prescriptive, per-editor, per-event). The fallback name is deleted. |
| C19 | `runtime/flows/editor_flow.py:326-327` | `choices=(1, 2, 3)`, help "Athens night (1, 2, 3)" | config |
| C20 | `runtime/flows/publish_flow.py:1154` | `choices=[1, 2, 3]` | config |
| C21 | `runtime/flows/editor/dossier_generation.py:414-421` | Colophon *"Filed by the Editor's desk on the morning of Night {night}."* | keep. It's the conference cadence, which is the profile's (2.3), not the event's. |
| C22 | `runtime/flows/editor/dossier_generation.py:87, 164` | Docstrings say `runs/athens_night_N/` | keep (cosmetic; reword in passing) |
| C23 | `runtime/flows/shared/io.py:23-60` | `assert_run_dir_night_matches` regex `_night[_]?(\d+)\b` | keep — already event-neutral |

### 3.2 Card schema and persona code

| ID | file:line | What | Disposition |
|---|---|---|---|
| P1 | `personas/run_persona_pipeline.py:1872-1873` (emits two null continuity fields); `:918`, `:1925`, `:2004` (exclusion sets) | Continuity placeholders are part of the card | delete (row 42–43) |
| P2 | `personas/flows/shared/chat_prompt_builder.py:109-110`, `:118` (strip entries for continuity and `bold_engagement_topics`); `:185-192` (VTS dict note) | Blacklist strip | chat artifact = voice card + a chosen deployment card. Those entries are deleted because the fields are no longer in the voice card. |
| P3 | `personas/run_persona_pipeline.py:61-72` (`_load_conference_context_string`), `:75-103` (`_load_deployment_priming` reads `conference_facts.json` + `audience_profile.json`) | Event read at build time | config: reads `event_config.facts`. In Phase B it's used only by the deployment step. |
| P4 | `personas/run_persona_pipeline.py:1782` | `metadata.deployment_context` | → deployment card `provenance` |
| P5 | `personas/run_pass0a_voice_config.py:72-73`, `:184-211` | Pass 0a is fed `conference_facts` + `panel_roster` | config (`facts`). Casting is legitimately event-relative, so no change in intent. |
| P6 | `personas/flows/shared/paths.py:269-270` | `conference_facts()` path helper | → `event_config()` |

### 3.3 Runtime prompts

| ID | file:line | Text (abridged) | Disposition |
|---|---|---|---|
| R1 | `voice_step2_validation_safeguards.md:1`, `voice_step2_validation_engagement.md:1`, `voice_step2_validation_voice_fidelity.md:1` | *"a panel of historical voices that comment on conference panels overnight, with their artifacts published the next morning to a real audience (business leaders, conference attendees)"* | config: `{{frame.assembly}}`, `{{frame.publication}}`, `{{frame.audience_short}}`. This is C55's "real fix". |
| R2 | `voice_step2_validation_safeguards.md:5`, `:9`, `:13` | *"Two universal Athens rules"*; *"attendees … at the conference"*; stale VTS rule | `:5` → "Two universal rules". `:9` → `{{frame.audience_short}}`. `:13` is C42 (rewrite as specified there). |
| R3 | `voice_step2_validation_cross_night_echo.md:1` | *"voices that publish nightly during the conference"* | config: `{{frame.assembly}}` |
| R4 | `editor_dossier.md:4`, `:21` | *"tonight's number (1, 2, or 3)"*, *"Nights 2-3 carry prior_editions"* | config: `{{night}} of {{night_count}}` |
| R5 | `editor_dossier.md:27`, `:35`, `:198` | *"one HoBB dossier — a single editorial publication under the House of Beautiful Business"* | config: `facts.host_organization` / `facts.host_organization_short` (already in the facts) |
| R6 | `editor_dossier.md:48`, `:52`, `:110`, `:138`, `:151`, `:160` | Tim's persona specifics (Stuttgart, Lüneburg, Beauty Shot, Sehnsucht…) | **out** → C57 (editor prompt card-driven). Not event config. |
| R7 | `editor_dossier.md:31`, `:58` | *"What the conference surfaced"* | keep for the conference profile. The non-panel case is already covered by the per-run `deployment_context` override (`dossier_generation.py:223-249`). |
| R8 | `voice_step1_reasoning.md:21`, `voice_step3_amendment.md:14-15, 28`, `voice_step2_artifact.md:2, 37`, `voice_continuity.md` | "the panel" (= the council), "tonight", "last night" | keep — the Assembly's shape and cadence, not the event |
| R9 | `provocateur_formulation.md:159`, `provocateur_triage_flags.md:34`, `provocateur_triage_voice.md:39` (`{{audience}}`) + `{{collective_landscape}}` + THE GATHERING / THE SPEAKERS blocks (`provocateur_flow.py:272-330`) | Already variable-fed | keep. THE GATHERING reads `event_config.facts.conference_context_paragraph`. |
| R10 | `researcher_*.md`, `transcription_*.md` ("conference session transcript", "conference panel") | Input shape | **out** → 2.3 input adapters |

### 3.4 Persona prompts (the Athens reader baked into card generation)

| ID | file:line | Text | Disposition (Phase B) |
|---|---|---|---|
| S1 | `pass_1_4_merge.md:53-55` | *"The Athens audience is philosophically literate but NOT classics-vocabulary-literate"* | Replace with an event-neutral reason for the same reference-not-display rule. Don't template it: voice passes are event-blind. |
| S2 | `persona_pass_4a_voice.md:168-170` | The same sentence | Same |
| S3 | `persona_pass_4b_artifact.md:13-16` (*"~750 people will encounter at breakfast … a short, compelling morning read"*), `:88` (*"the audience reads over coffee"*), `:105` (the audience-engagement "+1" criterion), `:110-111` (*"adapted for the conference deliverable"*), `:119` (*"Readable over coffee"*) | This is how the reader frame entered the artifact fields (§2.1 rows 27–34) | Neutralize BLOCK 1 and 3. Move the "+1" criterion and the length window to the deployment step. |
| S4 | `persona_pass_2_identity_boundaries.md:339-405` (the `voice_temporal_stance` block; `:355` *"per Athens brief 'impossible participants take the floor while you sleep'"*; `:382` `anchored_override`) | Generates the event-bound field, and still specifies the superseded fluid framing | Remove the block from Pass 2 (the field is D). Stage 4 item 1 interacts with this — see decision D8. |
| S5 | `persona_pass_5_user.md:10-40` | DEPLOYMENT CONTEXT block (variable-fed) | Keep, but only for the deployment half (`bold_engagement_topics`, `unique_contribution`). `default_questions` and `disagreement_protocol` are then generated event-blind. |
| S6 | `persona_pass_7b_smoke_test.md` (`conference_context` variable) | Smoke test against the event | Keep as deployment-scoped evidence |

**Correction to roadmap §2.1** (CONFIRMED): of the five prompts it lists as naming Athens, only `pass_1_4`, `persona_pass_2` and `persona_pass_4a` are event coupling. `pass_0a_voice_config.md:36` (*"Plato" not "Plato of Athens"*) and `pass_1_1_merge.md:253, 259, 284` (the Plato worked example) name Athens as Plato's city. `persona_pass_4b` (which the roadmap lists separately) is the fourth.

### 3.5 Continuity's night count

CONFIRMED: continuity is already count-agnostic except for two gates:
- The loader overlays `continuity_block_if_night_{night}` (`card_assembly.py:197-202`).
- The continuity prompt emits `…_if_night_N+1` keys (`voice_continuity.md:25`).
- Prior-night readers use `range(1, night)` or `night - 1`: `editor/publish.py:73-79`, `voice/step2_validation.py:385-405`, orchestrator `:460-464`, `editor/edition.py:313`.

**The two 3-bound gates:** `voice_flow.py:589` (plus the `:612` log) and the dashboard/template pair C4/C10. The card's `_if_night_2` placeholders are vestigial (row 42–43).

**The FINAL-NIGHT notice** (*"THIS IS THE ASSEMBLY'S FINAL NIGHT … The panels conclude with Act Five (Beastopia) at 20:00…"*) was **hand-appended** to all 10 `voices/<slug>/continuity_night_3.json` files, in both continuity blocks. All 10 carry `final_night_notice_appended: true` (9 with the timestamp 2026-05-11T12:18). CONFIRMED that no code in either repo writes it. It is event-specific text, and it caused the C42 false positive. See decision D7.

### 3.6 Duplicated event data in the project JSON (CONFIRMED, `athens-2026`)

- The Athens dates live in **4** places: `conference_facts.dates` ("May 7-10, 2026"), orchestrator `DATE_TO_NIGHT`, `generate_sessions_json.DAY_TO_DATE`, and `reference/sessions.json` (per-session `date`). `event_config.schedule` becomes the single source; the sessions file stays generated from it.
- `council_config.audience` is byte-equal to `audience_profile.participant_profile`.
- `panel_roster.panel_members_final` is equal to the `council_config.members[].name` list.

The last two are optional clean-ups (D13).

---

## 4. `event_config.json`

### 4.1 Schema (Athens instance)

```jsonc
{
  "schema_version": 1,
  "event_id": "athens-2026",

  // The former conference_facts.json, VERBATIM (same keys, same values).
  // load_conference_facts() returns this dict, so every existing consumer
  // (Pass 0a/5/7b, Provocateur THE GATHERING, editor YOUR ROLE) is byte-identical.
  "facts": {
    "conference_name": "World Beautiful Business Forum",
    "conference_short": "WBBF",
    "host_organization": "House of Beautiful Business",
    "host_organization_short": "HoBB",
    "location": "Athens, Greece",
    "dates": "May 7-10, 2026",
    "…": "…all other current keys unchanged…"
  },

  "schedule": {
    "timezone": "+03:00",
    "run_dir_template": "athens_night_{n}",
    "days": [
      {"label": "Day Zero",            "date": "2026-05-06"},
      {"label": "Day One",             "date": "2026-05-07", "night": 1},
      {"label": "Day Two",             "date": "2026-05-08", "night": 2},
      {"label": "Day Three",           "date": "2026-05-09", "night": 3},
      {"label": "Day Four",            "date": "2026-05-10"},
      {"label": "Special Activations", "date": null}
    ]
  },

  // Only the phrases prompts need that aren't already in facts (R1-R3).
  "frame": {
    "assembly": "a panel of historical voices that comment on conference panels overnight",
    "publication": "with their artifacts published the next morning to a real audience",
    "audience_short": "business leaders, conference attendees"
  },

  // Optional (decision D7). Null for Athens: the notice already sits in the
  // continuity_night_3.json files, so adding it here would double it.
  "final_night_notice": null
}
```

**Validation (in the loader):**
- `night` values are 1..N with no gaps.
- `run_dir_template` contains `{n}` exactly once.
- Dates are ISO or null.
- Labels are unique.

Nothing else is required. An event without `schedule` (e.g. a one-shot vatican run) gets `night_count = 1` and `run_dir_template = "night_{n}"`. *Inference:* that default keeps the one-shot case off a special path.

**Deliberately not in the schema:**
- A rename of the internal unit "night" (it's in the CLI, file names, published paths and URLs; renaming is churn with no gain).
- Model choice (`model_routing.json` owns it).
- Pipeline toggles such as `skip_step3` (profiles, 2.3).
- Per-voice lengths (deployment card).
- Audience text (`audience_profile.json` stays; it has its own canonical-source contract with `docs/AUDIENCE_BRIEF.md`).

### 4.2 Loader: `flows/shared/event_config.py`

One module, byte-identical in `runtime/` and `personas/`. This follows the existing `model_routing.py` twin and its parity test (`runtime/tests/test_model_routing.py:114`). Public surface:

| Function | Replaces |
|---|---|
| `load_event_config(project_root)` | — (fails loudly if missing, like `resolve_project_root`) |
| `facts(cfg)` | `load_conference_facts()` body (`io.py:359-390`) |
| `night_numbers(cfg)` → `[1, 2, 3]` | `ATHENS_NIGHTS`, all `choices=(1,2,3)`, both range guards |
| `night_count(cfg)`, `is_final_night(cfg, n)` | `night < 3`, `next_night <= 3`, template `night >= 3` |
| `run_dir_name(cfg, n)` / `night_for_run_dir(cfg, name)` | 4 builders + the `reset_run` regex |
| `day_label(cfg, n)` / `night_for_day(cfg, label)` / `night_for_date(cfg, iso)` | `NIGHT_TO_DAY` ×2, `night_to_day`, `DAY_TO_RUN`, `DATE_TO_NIGHT` |
| `processed_day_labels(cfg)` | `days_ordered` literal |
| `day_dates(cfg)` | `DAY_TO_DATE`, `TZ_OFFSET` |

**CLI change:** argparse can't know the night count before `--project` is parsed. So `--night` becomes `type=int` without `choices`, validated against `night_numbers` right after the project root resolves. That's one helper, used by 5 CLIs.

### 4.3 How each hardcoding reads it

| Inventory IDs | Reads |
|---|---|
| C1, C2, C6, C7, C11 (maps), C12 (maps) | `schedule.days[].label` / `.night` via `day_label`, `night_for_day`, `processed_day_labels` |
| C3, C5, C8, C9, C11 (dir), C12 (dir), C14 | `schedule.run_dir_template` via `run_dir_name` / `night_for_run_dir` |
| C4, C10, C16 (gate) | `is_final_night` |
| C11, C12, C16, C17, C18, C19, C20 (choices/ranges) | `night_numbers` |
| C12 (`--date`), C15 | `schedule.days[].date`, `schedule.timezone` |
| P3, P5, P6, R9 | `facts` |
| R1, R2, R3 | `frame.*` (rendered with the existing `{{…}}` substitution) |
| R4, R5 | `night_count`; `facts.host_organization(_short)` |
| C13, C21, C22, C23, R6, R7, R8, R10 | not read — kept or out, per §3 |

### 4.4 Deployment card: `voices/<slug>/08_deployment_card.json`

```jsonc
{
  "schema_version": 1,
  "deployment_id": "athens-2026",
  "voice_slug": "plato",
  "voice_card_sha256": "…sha256 of 07_persona_card_assembled.json…",
  "fields": {
    "voice_temporal_stance": "You have been called to the assembly that gathers in YOUR city — …",
    "length_and_format_constraints": "…",
    "unique_contribution": "…",
    "bold_engagement_topics": [ … ],
    "smoke_test_chains": [ … ]
  },
  "provenance": {
    "deployment_context": "…former metadata.deployment_context…",
    "sources": {"voice_temporal_stance": "operator short draft, athens-2026 08a8253", "…": "…"}
  }
}
```

In Phase B, `fields` gains `engagement_criterion`. It gains `generation_parameters` only with 2.2. The editor's card lives at `editor/<slug>/08_deployment_card.json`, and its `fields` also carry the former hardcoded "YOUR ROLE" paragraph (C18).

---

## 5. Migration plan (Athens stays reproducible)

**What "reproducible" can mean:** model outputs were never reproducible (thinking and sampling), so the bar is *prompt identity*. After every step, re-assembling any Athens system prompt from `athens-2026` must give the same bytes as today. Models are pinned separately by `model_routing.json` (C63).

**Step 0 — Golden prompts first (no behavior change).**
- Write a read-only script that renders every Athens system prompt with the current code: 10 voices × Steps 1–3 × Nights 1–3 (the continuity files exist on disk), plus the editor × Nights 1–3, as `(prefix, tail)` sha256 pairs.
- Also hash the three validator system prompts and the Provocateur's rendered THE GATHERING block.
- Store the hash table in the code repo and add `verify_athens_golden.py --project <athens-2026>`.
- Why this is needed: no existing test compares assembled prompts against the shipped cards. The tests use small fixture cards (`test_continuity_register.py`, `test_editor_card_assembly_strip.py`).
- Add one permanent unit test: a synthetic fixture card, split into voice + deployment cards, must render byte-identically to the unsplit card.

**Step 1 — `event_config.json` (C52), no card changes.**
- Add the loader twin (§4.2).
- Write `athens-2026/event_config.json`: `facts` = the current `conference_facts.json` verbatim; `schedule` from `DATE_TO_NIGHT`/`DAY_TO_RUN`/`DAY_TO_DATE`; `frame` = the current validator wording, split into the three phrases.
- Replace C1–C12, C14–C20 and P3, P5, P6 with loader calls. Delete `conference_facts.json` once no reader is left (athens-2026 commit needs operator OK).
- Update the 19 test files that pin Athens nights/days (CONFIRMED by grep — `test_orchestrator.py`, `test_reset_run.py`, `test_orchestrator_dispatch.py`, `test_vendor_intake.py` carry most). Most only use `athens_night_N` as fixture names, which an Athens-shaped fixture config reproduces unchanged.
- **Verify:** the golden hashes are unchanged for voice and editor prompts and THE GATHERING. Validator prompts change only by the R2 wording, which is intended; re-hash them.

**Step 2 — Split the cards, byte-identical.**
- Write a one-off offline script, `split_cards.py --project P`. For each voice and the editor, it writes `08_deployment_card.json` with the 5 D fields and provenance, removes those fields and the 2 continuity nulls from `07_…json`, and pins the sha256.
- It stores `voice_temporal_stance` as the unwrapped `default` string, and **refuses** if any `anchored_override` is non-null. That's 0 of 11 today, but the refusal forces a decision rather than a silent drop.
- Runtime: add the merge + overlap check + sha check to both card loaders. Delete `_unwrap_voice_temporal_stance` and the `deployment` hook (C17).
- Chat builder: voice card + named deployment card; delete the P2 strip entries.
- Persona assemble step: route the 5 D fields to the deployment-card file. Phase A still produces them from the current passes; only the output file changes.
- Run the split on every *live* project root (`athens-2026`, `current-tests/voice-pipeline-dryrun`) so no legacy-shape loader path is needed. Frozen archives aren't run and aren't touched.
- **Verify:** golden hashes are unchanged for all voice and editor prompts. The chat artifact is equivalent but not byte-identical (the VTS dict becomes a string); it isn't a runtime prompt.

**Step 3 — Count-agnostic continuity.**
- Replace the gates at `voice_flow.py:589`, C4 and C10 with `is_final_night`.
- Final-night notice: see D7. Athens keeps `null`, so Night-3 prompts stay identical.
- **Verify:** golden hashes unchanged. Add a test with a 4-night fixture config: continuity runs after nights 1–3 and skips after night 4.

**Step 4 — Phase B: event-free voice cards (voice card v2).** Gated on a second deployment being prepared, or on an operator decision (D10).
- Prompt edits S1–S5, so the voice passes become event-blind and the "+1" engagement criterion and length window move to the deployment step.
- Per-voice card patches for the §2.1 contamination list:
  - `medium` ×8, `technical_capabilities` ×1, `characteristic_output_structure` ×2, `relationship_to_detailed_response` ×2, `aesthetic_qualities` ×1, `stance_tendency` ×2, `default_questions` ×1, `disagreement_protocol` ×2
  - the engagement criterion ×8, moved to `engagement_criterion`
- Re-validate per the cross-cutting DON'T (no blanket card changes without per-voice empirics): sentinel regen / chat-test, thinking on, with a spend cap, as for Stage 4.
- **Athens is unaffected:** `athens-2026` keeps its v1 cards and pins. v2 lives in the next project (or, later, the hub library).

**Step 5 — Deployment-card generator ("Pass D"). Shelved.**
- For the next event, write the deployment cards by hand. That's 10 × 5 short fields, starting from the Athens cards and the carry-forward list (§2.1). Athens did the same in effect: the final temporal stances were operator drafts, and the lengths were operator surgery.
- Build a generator only if hand-authoring a second deployment proves too slow.

**Interactions with other stages:**
- **Stage 4 item 1** (rewrite Pass 2's `voice_temporal_stance` block to AF-LEADS) conflicts with S4, which removes that block from Pass 2. Decision D8.
- **Family of forms (FU#55 Stage 0):** `forms[].length` is a per-form length in the voice card. Athens lengths were deployment decisions, so this design puts them in the deployment card. Decision D9. Both land in Stage 5, so decide once.
- **C42 / C55:** R1–R3 finish C55. C42's safeguards rewrite should land in the same edit as R2.

---

## 6. Net-complexity check

**Removed:**
- **Hardcoded calendar data:** `DAY_TO_RUN`; `NIGHT_TO_DAY` ×2; `NIGHT_TO_RUN_DIR`; `DATE_TO_NIGHT`; `ATHENS_NIGHTS`; the `night_to_day` and `days_ordered` literals in `app.py`; `DAY_TO_DATE`/`DAY_TO_INDEX`/`TZ_OFFSET`. Dates go from 4 copies to 1 source.
- **Night-count special cases:** 5 CLI `choices`, 2 range guards, 4 "night 3 is last" checks, 4 run-dir builders and 1 parser.
- **The deployment hook:** `_unwrap_voice_temporal_stance` (~40 lines), the `deployment="athens"` parameter, and the `anchored_override` sub-field (dead in 11/11 cards).
- **Continuity leftovers:** 2 null fields in every card, their 4 exclusion-set entries in persona code, and 3 chat-strip entries.
- **One file:** `conference_facts.json` is absorbed.
- **Event wording in voice passes:** 3 persona prompts lose Athens sentences outright rather than gaining template variables.
- **Manual operations:**
  - Per-event card surgery (the 10 temporal-stance rewrites in `08a8253`, the §27 length surgery) becomes editing deployment cards; voice cards stay untouched.
  - The hand-injected final-night notice becomes a config field (if D7 is adopted).

**Added:**
- `event_config.py` (~80 lines, twinned, plus a parity test).
- One new file type per voice (`08_deployment_card.json`).
- The merge + overlap + sha check (~25 lines, shared by the voice loader, editor loader and chat builder).
- 3 `frame` phrases feeding template variables in 4 prompts.
- The `--night` validation helper.
- 2 one-off scripts (golden verification, split), deletable after migration except the golden check.

*Inference, the verdict:* this passes the gate. Every addition replaces a special case that existed in more than one place. The frame variables replace text that was already wrong once (Munich, C55).

**What doesn't net out:**
1. **Pass D (deployment-card generator):** purely additive. Shelve (Step 5).
2. **`generation_parameters`:** would be a second model source beside `model_routing.json`. Add only with the vendor layer (2.2), and only as per-voice overrides.
3. **`final_night_notice`:** adds a field and ~6 lines of code to save one manual step per multi-night event. Marginal (D7).
4. **Voice card v2 (Phase B):** no code complexity, but a real re-validation cost for 10 voices. It's the price of the cards having absorbed the Athens reader frame at build time (§3.4 S3).
5. **The editor split:** mostly symmetry. Tim's persona stays event-bound (§2.2), so the split buys the editor little until C57.
6. **The sha pin:** new friction. Every hand patch to a voice card needs a re-pin. That friction is the byte-identity guarantee (D5).
7. **`--skip-step3` (C13):** stays hardcoded. Moving it into config is profile work (2.3), not consolidation.

---

## 7. Open operator decisions

| # | Decision | Options and trade-offs | Recommendation |
|---|---|---|---|
| D1 | Partition departures from FU#42 | (a) As §2.1: `default_questions`, `disagreement_protocol` and the fidelity criteria are V; `voice_temporal_stance` is D. (b) FU#42 as written (2026-04-25). The Athens content supports (a); (b) predates the AF reframe. | (a) |
| D2 | Artifact fields: which card? | (a) **Form constitution in V**, cleaned in Phase B. Consistent with §11.6 (family of forms is voice capability); costs a v2 re-validation. (b) **Whole ARTIFACT section in D.** The voice card is event-free immediately with no re-validation, and each output mode (chat, annotation) gets its own artifact spec. But it contradicts §11.6's exemption premise and duplicates the form menu into every deployment. | (a) |
| D3 | Where the event config lives | (a) `event_config.json` absorbs `conference_facts.json` (`facts` block verbatim; file count unchanged). (b) A new file beside `conference_facts.json` (a 5th root file; dates duplicated). (c) Extend `conference_facts.json` (no new file; conference-shaped name for non-conference events; mixes operational config into a prose-facts file). | (a) |
| D4 | Where voice cards live | (a) Copied into each event project, identity checked by sha pin (no new path machinery). (b) A shared voice-library root that projects reference (the hub direction; a new root and resolution rules now). | (a) now; (b) with the hub |
| D5 | sha pin strictness | Hard error / warning / none. Hard error makes every voice-card edit explicit per deployment; warning keeps Athens-style iteration fluid but the guarantee becomes advisory. | Hard error, with the re-pin command in the message |
| D6 | Voice card file name | (a) Keep `07_persona_card_assembled.json` (20 files in runtime/personas/docs reference it; `paths.assembled_card` unchanged). (b) Rename to `07_voice_card.json` (clearer, more churn). | (a), with a `metadata.card_schema` marker |
| D7 | Final-night notice | (a) Keep hand-injection (as at Athens). (b) `event_config.final_night_notice`, rendered on the final night. Removes a manual step; C42's continuity exemption must then also cover the new section. | (b) when the next multi-night run is planned; until then, keep the Athens text on record |
| D8 | Stage 4 item 1 vs S4 | (a) In Stage 4, remove the VTS block from Pass 2 and put the AF-LEADS five-invariant template in a deployment-card authoring note. (b) Rewrite it inside Pass 2 as planned, then move it in Stage 5 (rework). | (a) |
| D9 | Family-of-forms lengths | (a) Per-form length windows in the deployment card (`length_and_format_constraints` as `{default, by_form}`), because Athens lengths were deployment decisions. (b) `forms[].length` in the voice card, as roadmap 1.2 Stage 0 drafts it. | (a) |
| D10 | Phase B timing and spend | Now (under the 2026-09-28 gate amendment the operator's intent suffices), or when a second deployment is prepared. The cost is a 10-voice re-validation. | When a second deployment is prepared. It can ride with Stage 4's regen budget if run then. |
| D11 | Editor identity | (a) `council_config.editor_slug` replaces the `EDITOR_CARD_SUBPATH` hardcode; the editor goes through the same split loader. (b) Leave the editor on its own single-file path until C57. | (a) |
| D12 | `--skip-step3` | Leave in the orchestrator, or `event_config.pipeline.voice_skip_step3`. | Leave (profiles, 2.3) |
| D13 | Other duplicates | Collapse `council_config.audience` into `audience_profile` and `panel_roster` names into `council_config`, or leave. Byte-equal today, so there's no drift yet. | Leave for now; note it |

---

*Evidence base: all card and project findings are from `/Users/aienvironment/Desktop/AI Assembly/projects/athens-2026` at commit `0b2af19` (read-only). Code and prompt line numbers are at `phase0-fixes` `40fe490`.*
