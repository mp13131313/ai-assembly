# Review: correctness of all 75 prompt files (Task 1 of the Fable batch)

**For:** the operator and the main working session. **Brief:** `_workspace/planning/BRIEF_2026_09_28_fable_batch.md` §Task 1.
**By:** Fable 5.1, 2026-09-28. Read-only, at `phase0-fixes` `4e61444` in a detached worktree. Uncommitted: the main session files it.

**How it was done.**
- No model calls, no pipelines, no pytest.
- Two throwaway offline scripts in the session scratchpad, not the repo:
  - `prompt_vars.py` lists every Jinja variable and include per prompt (`jinja2.meta`) and every `{{x}}` token in the runtime prompts.
  - `render_calls.py` lists every `render(...)` call site and its keyword arguments (`ast`).
- Two read-only subagents took two slices: the Pass 1.1–1.7 merge prompts against their schemas, and the Pass 0a/0b/1a/1b research prompts. I re-checked every finding of theirs that appears below against the code, the schema or the Athens files. Items I could not re-check are marked PLAUSIBLE.
- Athens data under `projects/athens-2026` was read, never written.

---

## 1. Verdict

**No BLOCKER. 3 MAJOR, 19 MINOR, 11 NIT (a few NITs are grouped).**

- **The plumbing is sound.** All 75 prompt files are loaded by live code, so there are no dead files. Every Jinja placeholder and every runtime `{{x}}` fill is supplied by its render call. Every runtime output contract matches its parser.
- **The three MAJORs are all prompts that don't reach, or don't act on, what they were written for.** Each is silent, and nothing in the trackers covers it:
  1. The cross-night echo validator never ran at Athens: the loader reads the wrong key.
  2. The per-section Deep Research prompts, the ones actually pasted for every voice, lose each type's framing block and the curator's emphasis note.
  3. Pass 1.7's edit-path example silently fails, and one Athens voice has a coherence fix recorded as applied that never was.
- **Most MINORs are contradictions inside or between the persona writer prompts:** scholar names, inline tags, `header` stripping, song-vs-prose. The shipped cards mostly settled these by hand. They stay latent until the next build, and fixing them is Stage 4 work behind a sentinel regeneration.

---

## 2. Findings, most severe first

Labels:
- **CONFIRMED:** I read both sides (prompt and code, schema or data), or reproduced the problem offline.
- **PLAUSIBLE:** the defect is confirmed but its runtime effect is inferred.
- **Voice-writing:** the prompt shapes card or artifact text. Changing it needs a sentinel regeneration first (brief, common rules), and `personas/scripts/sentinel_regen.py` can't run today (voices §37 A5).

| # | Sev. | Finding | Main location |
|---|---|---|---|
| 1 | MAJOR | Cross-night echo validator never ran at Athens (wrong key) | `runtime/flows/voice/step2_validation.py:401` |
| 2 | MAJOR | Per-section DR prompts lose the type framing and the curator note | `personas/scripts/split_tailored_prompt.py:70-77` |
| 3 | MAJOR | Pass 1.7 edit paths silently skipped; a fix is recorded as applied | `pass_1_7_coherence.md:141-142`, `:223-255` |
| 4 | MINOR | Echo validator reads the continuity memory as instructions | `voice_step2_validation_cross_night_echo.md:6,21,27,51` |
| 5 | MINOR | Pipeline `cluster_NNN` ids in all 24 published theme abstracts | `researcher_theming.md:36`, `publish_flow.py:352` |
| 6 | MINOR | Raw-loaded prompts send their developer headers to the model | `persona_derive.md:1-6`, `persona_pass_7a_*.md` |
| 7 | MINOR | Step 1 prompt promises "editorial flags" that the code strips | `voice_step1_reasoning.md:2,50` |
| 8 | MINOR | Merge prompts name fields/values the schemas reject (retry cost) | 1.2, 1.3, 1.4, 1.6 merge prompts |
| 9 | MINOR | Merge prompts route content to fields that don't exist (silent drop) | 1.1, 1.3, 1.5 merge prompts |
| 10 | MINOR | Pass 2 both requires and strips scholar names; cards split 8/2 | `persona_pass_2_identity_boundaries.md:78-90` vs `:249,256` |
| 11 | MINOR | Six prompts and the strip code disagree on which inline tags a card carries | Pass 3, 0b-fictional, 7a, 7-pre, `bracket_strip.py` |
| 12 | MINOR | Pass 3/4a user prompts ask for scholarly attribution their system prompts strip | `persona_pass_3_user.md:29-33,58`, `persona_pass_4a_user.md:49-51` |
| 13 | MINOR | Pass 2 system prompt uses inputs its user prompt doesn't send | `persona_pass_2_identity_boundaries.md:12-19,320` |
| 14 | MINOR | Pass 4b `medium` guardrail contradicts its own musical-corpus variant | `persona_pass_4b_artifact.md:87-93` vs `:122-165` |
| 15 | MINOR | Pass 7 anachronism `PERIOD:` gets a truncated dict, never dates | `run_persona_pipeline.py:1044` |
| 16 | MINOR | Editor told `fault_line_present` means the panel split; it means the council | `editor_dossier.md:12` |
| 17 | MINOR | Research/merge prompts branch on voice_config values they never receive | 1.1, 0b-organism, 0b header, 0a |
| 18 | MINOR | DR prompt plumbing: doubled §6 blocks, "six areas" in one-area prompt, stale save path | `split_tailored_prompt.py:63-77`, `pass_0b_header.md:51-57,67-68` |
| 19 | MINOR | Pass 0b tailor: contradictory question count; an empty list aborts Phase 0.5 | `pass_0b_tailor.md:116,118,165` |
| 20 | MINOR | Te Awa Tupua Act section numbers disagree across prompts | `pass_0b_non_human_system.md:148` |
| 21 | MINOR | Step 3 prompt (dormant) gives no output format; its parser needs one | `voice_step3_amendment.md:41-48` |
| 22 | MINOR | Pass 0b fictional asks the DR model for tags the shared rules forbid | `pass_0b_fictional.md:72` vs `_pass_0b_research_discipline.md:9` |
| N1–N11 | NIT | Stale counts, retired names, dead cross-refs | §2.23 |

### 2.1 MAJOR: the cross-night echo validator never ran at Athens

- **Where:** `runtime/flows/voice/step2_validation.py:401` reads `prior.get("artifact_text") or prior.get("body")` from `published_artifacts/nights/night_<N-1>/<slug>.json`. The writer puts the text at `artifact.text` (`runtime/flows/voice/publish.py:223-226`), so the loader returns `None` and the pillar is skipped (`:432-452`). The tests use a flat `{"artifact_text": …}` fixture (`runtime/tests/test_step2_validation.py:112-132`), so they pass.
- **What goes wrong:** `voice_step2_validation_cross_night_echo.md` never runs in production. That was the recurrence safety net: C20a leans on it ("C28b's cross-night echo HOLD catches the worst case", runtime OPEN_ITEMS C20a). It is also the only check against a voice rehashing last night's piece.
- **Evidence, CONFIRMED:**
  - All 20 Night-2/3 validation records have `cross_night_echo: null`, although every Night-1 file existed from `dcaf7ce` (2026-05-08), before Night 2 was validated (2026-05-09).
  - The published file's keys were `artifact.{title,subtitle,text,…}` at that commit.
  - The Voice spec's own call counts agree: 29/30/30 validator calls on Nights 1/2/3, i.e. three pillars, no echo (`docs/AI_Assembly_Voice_Pipeline.md:1274`).
- **Fix direction:** read `prior["artifact"]["text"]` first, keep the old keys as fallbacks, and build the test fixture from a real published file. Land it together with #4, or the first run will raise false flags.

### 2.2 MAJOR: the per-section Deep Research prompts lose the type framing and the curator note

- **Where:**
  - `personas/scripts/split_tailored_prompt.py:70-77` slices each section from its `## Section N:` heading. Everything above `## Section 1:` in the monolithic prompt is discarded. Section mode only restores a one-paragraph intro (`pass_0b_header.md:49-58`).
  - The discarded preambles are `pass_0b_human.md:1-21` (RECONSTRUCTION DISCIPLINE for hostile-sourced voices, "apply throughout all six sections"), `pass_0b_fictional.md:1-43` (NARRATIVE-FUNCTION FRAMING), `pass_0b_non_human_organism.md:1-27` (the two operator postures) and `pass_0b_non_human_system.md:1-51` ("INDIGENOUS REPRESENTATION — ETHICAL FRAMING (applies throughout, especially Sections 3, 5, and 6)", with the CARE/IPAI rules).
  - The curator's thematic note is spliced in just before `## Section 1:` (`personas/run_pass_0b_tailor.py:143-151`), so no slice contains it either.
- **What goes wrong:** every Athens voice ran per-section DR (all ten have `04_dr_dossier/01…06_section_N.md`). So the six Research sessions per voice never saw the type framing or the curator's emphasis. For Whanganui that means the Indigenous-representation ethics block. The prompt pass meant to govern DR's method for the hardest voices does not reach DR.
- **Evidence, CONFIRMED:** read-only greps of the athens-2026 prompt files.
  - Whanganui's monolithic prompt contains the INDIGENOUS block and the curator note; all six section prompts contain neither.
  - Scheherazade: the NARRATIVE-FUNCTION block is in the monolithic prompt, absent from all six sections.
  - Marley, Octopus: the curator note is in the monolithic prompt, absent from all six sections.
- **Runtime effect, PLAUSIBLE:** how much the Athens dossiers lost is unknown. Heavy operator work on Whanganui (voices §17/§28) may have compensated. The shipped cards are canon either way. This matters for the next voice built.
- **Fix direction:** carry the type preamble and the curator note into every section prompt. Either render the preamble in `pass_0b_header.md` section mode, or have `wrap_section` prepend the text that sits between the intro and `## Section 1:`. Add a test that each section prompt contains its type's framing block.

### 2.3 MAJOR: Pass 1.7's edit paths are silently skipped, and a coherence fix is recorded as applied that never was

- **Where:**
  - `pass_1_7_coherence.md:141-142` gives `passages[7].citation` as an example path. Five chunks are wrapper objects, not lists: `passages`, `works`, `moves`, `sensitive_topics`, `hard_limits` (`personas/run_pass_1_7.py:307-318`, `is_list=False`). The real path is `passages.passages[7].citations`, and the field is `citations`, not `citation` (`personas/schemas/pass_1_6.py:110`).
  - `_resolve` raises `KeyError` on the short form. `run_pass_1_7.py:541-544` catches it and skips the edit, printing only to stdout. `_coherence_audit.json` keeps counts, not reasons.
  - The prompt says the opposite: an invalid edit makes "the run fail loudly" (`:253-255`).
  - Its own Example A (`:223-245`) would fail Concept validation (another skip). It has `gloss` and `loadbearing`, which are VocabEntry fields; it lacks the required `definition` and `evidence_tag` (`schemas/pass_1_2.py:103-118`). Its citations lack the required `tier` (`schemas/_conventions.py:61`).
- **What goes wrong:** a resolve-by-edit on any of those five chunks is dropped while the flag reads "Resolved by edit".
- **Evidence, CONFIRMED:**
  - Whanganui `02_merge/_coherence_audit.json`: `edits_applied 4, edits_skipped 6`. The six were CF-02's `passages[...].work_title` sets.
  - 11 of 22 Whanganui passages still carry a `work_title` that matches no work.
  - Arendt's run wrote the correct wrapper path (`passages.passages[8].work_title`) and applied, so the example is what decides. The other nine voices skipped 0.
- **Fix direction:** correct the example paths, list which chunks are wrappers, and make Example A schema-valid. Either make skipped edits loud (non-zero exit, or a `skipped_reasons` field in the audit), or change the prompt's "fails loudly" claim to match.

### 2.4 MINOR: the echo validator reads the continuity memory as instructions (fix with #1)

- **Where:** `voice_step2_validation_cross_night_echo.md:6` calls the continuity overlay "deltas the voice was instructed to deliver tonight … what it committed not to repeat / what it agreed to advance to". It makes "failure to engage with what continuity overlay specifically asked for" echo (`:21`), a HOLD (`:27`) and a WARN (`:51`). The code labels it the same way (`step2_validation.py:336`).
- **The mismatch:** `voice_continuity.md:14-16` writes a first-person memory ("WHAT I CHOSE TO WRITE", "HOW I RESPONDED TO OTHER VOICES"), which asks for nothing. CONFIRMED on real data: Plato's `continuity_night_2.json` artifact block is pure recollection.
- **What goes wrong, PLAUSIBLE:** once #1 is fixed, the validator must judge whether the voice "addressed" instructions that don't exist, so expect spurious WARN/HOLD on an operator gate that halts on any flag.
- **Fix direction:** reword the overlay as "last night's piece, as the voice remembers it" and drop the "not addressed" WARN/HOLD rule. Or have continuity emit an explicit deltas field if the operator wants one.

### 2.5 MINOR: pipeline `cluster_NNN` ids appear in every published theme abstract

- **Where:** `researcher_theming.md:36` ("cite them inline by cluster_id"), with every good example doing it (`:57-61`). The Researcher spec encourages this on purpose (`docs/AI_Assembly_Researcher_Pipeline.md:210,270`).
- **Where it reaches:**
  - The voices' Step 1 surface as `theme_abstract` (`runtime/flows/voice/card_assembly.py:526-527`).
  - The published per-theme files: `publish_flow.py:352` writes `abstract = researcher_abstract`.
  - The Editor's rewrite (`theme_abstract_for_dossier`) removes them, and none appear in dossiers or voice artifacts.
- **Evidence, CONFIRMED:** 24 of 24 Athens theme abstracts cite cluster ids, e.g. published `themes/night_1/theme_002.json` `abstract`: "…cluster_007 raises the threshold question, cluster_002 defends…".
- **What goes wrong:** a reader-facing `abstract` field carries internal ids. Whether the microsite shows it is unknown (C68 R3).
- **Fix direction:** keep the prompt (the ids anchor the synthesis) and publish a clean display abstract. Either use the Editor's `theme_abstract_for_dossier` when one exists, or strip `cluster_\d+` references at publish. Operator decision, §5.

### 2.6 MINOR: prompts loaded raw send their developer headers to the model

- **Where:** `personas/flows/shared/io.py:71-76` reads the file as-is, and nothing strips Jinja comments. So the `{# … #}` block is part of the system prompt for:
  - `persona_derive.md:1-6`: "Claude Sonnet 4.6 … Pure compression task — Sonnet is correct here, no thinking needed". This goes to the Derive call, which runs with thinking on (`run_persona_pipeline.py:922-928`).
  - `persona_pass_7a_cross_model.md:1-7` (`:1091`).
  - `persona_pass_7a_fix.md:1-15` (`:1366`).
  - `pass_0a_voice_config.md` (read with `read_text`, `run_pass0a_voice_config.py:207`) sends a literal `{% if hostile_sources %}` (`:98`) and "Phase B" and CLI-flag notes (`:1,16,38,62,136`).
- **What goes wrong:** the model reads stale developer notes as instructions, e.g. "no thinking needed" and "8 fields" for Derive, and model names. CONFIRMED by reading the call path.
- **Tracker overlap:** the roadmap (0.4) calls the Derive header "harmless at runtime (code wins)", and voices §36 files the model names inside prompt text. The mechanism that makes both model-facing is not filed.
- **Fix direction:** render these files through `prompt_render.render()` (none has variables, so it's a drop-in), or strip `{#…#}` in `load_prompt`. Derive and 7a-FIX shape card text, so treat them as voice-writing.

### 2.7 MINOR: the Step 1 prompt promises "editorial flags" and a "STRUCTURED REASONING SURFACE" that the voice never gets

- **Where:**
  - `voice_step1_reasoning.md:2` and `:50` tell the voice it receives, and should engage, "clusters, raw extractions, theme abstract, editorial flags".
  - `card_assembly.filter_theme_record_for_step1` (`card_assembly.py:510-533`) deliberately drops `theme_flags` (and `co_assigned_voices`).
  - The user prompt labels the record "WIDER RECORD OF TODAY'S CONVERSATION ON THIS THEME" (`step1_private_reasoning.py:113`), not the label the prompt names.
  - The narrative briefing ends by telling the voice that theme flags are "available in the `full_theme_record` field of this briefing entry" (`runtime/flows/provocateur_flow.py:1210-1215`). No such field exists in what the voice receives.
- **What goes wrong, PLAUSIBLE:** the voice looks for flags that aren't there, or invents them. Low impact; seen on every Step 1 call.
- **Spec:** the Voice spec says both things (flags included at `:184,364`, dropped at `:441`).
- **Fix direction:** remove "editorial flags" from the prompt and the briefing hint, and use one label for the surface. Voice-writing.

### 2.8 MINOR: merge prompts name fields and values the schemas reject

Each of these, if followed, fails Pydantic validation and costs a retry, then `sys.exit` on the second failure (`chunk_runner.py:326-335`). All CONFIRMED against the schemas.

| Prompt | Says | Schema |
|---|---|---|
| `pass_1_6_merge.md:78,83` | `purpose_tag="voice_exemplar"` | field is `Passage.purpose` (`schemas/pass_1_6.py:103`) |
| `pass_1_2_merge.md:131` | "Tag as `experiential` or `inference`" | `experiential` isn't an `EvidenceTag` (`schemas/_conventions.py:31-45`) |
| `schemas/_frames.py:124-127` (inlined into the 1.2 prompt) | suggests `interpretive_reconstruction` | not an `EvidenceTag` |
| `pass_1_4_merge.md:104` | skeleton `analytical_context_voice: {…} \| null` | `:142-145` and `run_pass_1_4.py:30` require an object; the comment at `run_pass_1_4.py:20` ("OPTIONAL") is stale |
| `pass_1_3_merge.md:118-126` | voice modes include `organism`, `system` | `ReasoningMethod.voice_mode` allows philosophical / observational / narratival only (`schemas/pass_1_3.py:84`) |
| `pass_1_2_merge.md:377-395` | task block and minimum counts cover 3 keys | `interpretive_frames` is a 4th required key (`run_pass_1_2.py:26-31`) |

- **Evidence:** the Athens outputs are valid, so the models mostly worked around these, at unknown retry cost.
- **Fix direction:** align each line with its schema.

### 2.9 MINOR: merge prompts route content into fields that don't exist, so it is dropped silently

No pass-1 schema sets `extra`, so Pydantic's default ignores unknown keys. CONFIRMED against the schemas.
- `pass_1_5_merge.md:28` routes to `KnowledgeBoundary.contested_exclusions`, which doesn't exist (`schemas/pass_1_5.py:57-116`).
- `pass_1_5_merge.md:87` asks for a `scholarly_context` sub-field on sensitive-topic and knowledge-boundary entries. Neither model has one: SensitiveTopic has `scholarly_reception`, ExclusionEntry has nothing.
- `pass_1_3_merge.md:145` routes to `worked_demonstrations[].textual_evidence`, which doesn't exist (`schemas/_analytical.py:152-176`).
- The copied "Gemini preservation" block in `pass_1_1_merge.md:173-177` routes first to `interpretive_frames[]` and `analytical_context_*`, which Pass 1.1 cannot output (its only keys are `life_scaffold` and `formative_candidates`). `chunk_runner._validate` keeps only OUTPUT_KEYS (`:189-207`). Softer copies of the block sit at 1.3:142, 1.4:87, 1.5:86 and 1.6:86.
- **What goes wrong, PLAUSIBLE:** the "preserve everything" material the arch-03 merge exists for is silently lost wherever the model follows these routes.
- **Fix direction:** point each route at a real field, or add the fields to the schemas.

### 2.10 MINOR: Pass 2 both requires and strips scholar names; the shipped cards split 8/2 (voice-writing)

- **Where:** `persona_pass_2_identity_boundaries.md:78-90` strips from every field value any scholar the voice couldn't have known. `:249` and the templates at `:256,261` require `epistemic_frame_statement` to "name the specific scholars whose readings inform the construction". The card spec says the same on both sides (`docs/AI_Assembly_Persona_Card_v2.md:260-274` with the Plato example naming Vlastos, Annas, Ferrari, Sedley).
- **Evidence, CONFIRMED:** 8 of 10 shipped frames name no scholars. Octopus names eight ("Godfrey-Smith, Mather, Hochner…"); Whanganui names its scholarship as part of the witness stance.
- **What goes wrong:** the next build produces either shape, depending on which instruction wins.
- **Fix direction:** decide once (§5), then change Pass 2 and the card spec together.

### 2.11 MINOR: six prompts and the strip code disagree on which inline tags a card carries (voice-writing)

- **Pass 3, provenance tags:** `persona_pass_3_intellectual_core.md:55-58` strips `[stated]` / `[scholarly_consensus]` / `[inference]` / `[attributed by narrative function]`. Its fictional branch (`:277-279`) requires exactly those tags. Result, CONFIRMED: Scheherazade's shipped constitution carries `evidence_tag` (scholarly_consensus 11, stated 5) on 16 of 17 principles, rendered into her runtime system prompt.
- **Pass 3, category tags:** its human branch (`:273-275`) forces `[ontological]` / `[epistemological]` / `[ethical-political]` on every human voice. That overrides the observational (`[experiential]` / `[artistic]`) and narratival rules in `:247-258`. Cleopatra (observational), and Dostoevsky and Battuta (narratival), shipped with the philosophical categories. Marley shipped with none.
- **Pass 6.5-clean (`bracket_strip.py:22-30,80-99`) strips all of these category and provenance tags** after Pass 6, yet:
  - Pass 3's comment (`:223-231`) says category tags "should remain";
  - Pass 7a (`persona_pass_7a_cross_model.md:47-65`) tells the validator that `[scholarly_consensus]` / `[stated]` / `[inference]` / `[contested]` are "LEGITIMATE … preserved by Pass 6.5-clean's allowlist". They are on the strip list, not the keep list;
  - Pass 7-pre's observational mode classifies claims by `[scholarly_consensus]` / `[inference]` tags (`persona_pass_7pre_extract.md:77-78`, `persona_pass_7pre_verify_batch.md:39-40`). Those tags are gone before 7-pre runs (`run_persona_pipeline.py:832-835`).
- **What goes wrong, CONFIRMED:** the shipped cards are inconsistent. Arendt, Cleopatra, Dostoevsky and Battuta keep category tags; others don't. Inference: the tags survived through the pre-§32.1 7a-FIX write-back or hand edits.
- **Fix direction:** decide the tag policy once (§5), then align Pass 3, 7a, 7-pre and `bracket_strip.py`.

### 2.12 MINOR: Pass 3 and 4a user prompts ask for scholarly attribution their system prompts strip (voice-writing)

- **Where:** `persona_pass_3_user.md:29-33,58` asks for "`concept_lexicon` scholarly attribution" and a `constitution.scholarly_context` sub-field. `persona_pass_4a_user.md:49-51` says "use these for scholarly attribution in register notes". Both system prompts forbid this (`persona_pass_3_intellectual_core.md:77-86`, `persona_pass_4a_voice.md:48-56`). The Pass 3 user prompt's examples are Dostoevsky-only (Kasatkina, Patyk, Williams-vs-Frank), shown to every voice.
- **Evidence:** latent. No shipped card has a `scholarly_context` sub-field (checked all 10).
- **Fix direction:** reword the user prompts as "inform your synthesis; do not cite".

### 2.13 MINOR: the Pass 2 system prompt uses inputs its user prompt doesn't send (voice-writing)

- **Where:** `persona_pass_2_identity_boundaries.md:12-19` tells the model to use `analytical_context_reasoning` and `analytical_context_voice`. `:320` says to build `character` "from merged_dossier.life_scaffold + moves + register". `persona_pass_2_user.md` sends only chunks 1.1 and 1.5 plus the debate frames (`run_persona_pipeline.py:492-500`). This has been stale since the per-chunk split (1-arch-05 Part A).
- **What goes wrong, PLAUSIBLE:** `character` is built without the voice-move material it is told to use.
- **Fix direction:** pass `moves` and `register` to Pass 2, or drop the references. The `banned_language` / `banned_modes` block in Pass 2 (`:178-193`) is for Pass 4a's fields and can go.

### 2.14 MINOR: Pass 4b's `medium` guardrail contradicts its own musical-corpus variant (voice-writing)

- **Where:** `persona_pass_4b_artifact.md:87-93`, unconditional: for `lyrics_patterns_only`, "the medium IS the song … (lyric + Suno-style kind-hint). Do NOT bridge song → prose."
- **The conflict:** the conditional variant (`:122-165`) specifies prose plus an instrumental-only direction string, "No new lyrics composed". `persona_pass_4a_voice.md:111-115` agrees with the variant.
- **History:** a leftover of the 2026-05-04 morning fix (voices §23). The afternoon Option-3 restructure (§24) replaced only the conditional block.
- **Evidence:** latent. Marley's shipped card follows the variant (prose + riddim).
- **Fix direction:** reduce the guardrail line to "see the musical-corpus variant below".

### 2.15 MINOR: Pass 7 anachronism's `PERIOD:` gets a truncated dict, never dates

- **Where:** `run_persona_pipeline.py:1044` assumes `world` is a string. It is a dict on every card, so `PERIOD:` (`persona_pass_7_anachronism.md:79`) becomes `str(dict)[:300]`.
- **Evidence, CONFIRMED** for Plato, Arendt and Octopus: `{'ontological_furniture': "What is fully real are the Forms…`.
- **What goes wrong:** the period check runs without the voice's period. It still has the card's `knowledge_boundary`.
- **Fix direction:** pass life dates, from `life_scaffold` or the `knowledge_boundary` general frame.

### 2.16 MINOR: the Editor is told `fault_line_present` means the panel split; Triage defines it as the council diverging

- **Where:** `editor_dossier.md:12`: "does this theme split the panel? … your article should name the cut rather than smooth it". Triage sets the flag when "the council's traditions would visibly diverge" (`provocateur_triage_flags.md:18-21`), a prediction about the voices, and the fault-line description isn't passed on.
- **What goes wrong, PLAUSIBLE:** Tim is told to name a split among the human speakers that may not have happened.
- **Fix direction:** say "the voices were expected to diverge", or pass `fault_line_description` through. Voice-writing (Tim's published text).

### 2.17 MINOR: research and merge prompts branch on voice_config values they never receive

All CONFIRMED.
- `pass_1_1_merge.md:161` has a hostile-sources branch, but the template never renders `hostile_sources`. The comment at `chunk_runner.py:269-270` wrongly says 1.1 uses it.
- `pass_0b_non_human_organism.md:24,68,106` say "the voice_config's editorial_rationale determines which posture". It isn't in the render context (`run_phase0_1_research.py:248-258`), and its only other route, the curator note, is lost in section mode (#2).
- `display_name_with_hint` reads `wikipedia_disambiguation_hint` (`run_phase0_1_research.py:226`, `split_tailored_prompt.py:88-92`). Pass 0a never emits it, and it is not in `schemas/voice_config.py`. So DR prompts never disambiguate a name.
- Pass 0a's field list (`pass_0a_voice_config.md:34-62`) never mentions `mediation_stance` (`schemas/voice_config.py:41`), which drives branches in Passes 2–6. PLAUSIBLE: a future system voice gets the witness stance only if the curator sets it by hand.
- **Fix direction:** pass the flags in, or delete the branches.

### 2.18 MINOR: Deep Research prompt plumbing

All CONFIRMED.
- **§6 gets the conditional footer blocks twice.** The §6 slice ends at `OUTPUT FORMAT` (`split_tailored_prompt.py:37,63-68`), but the hostile and lyrics blocks come before that line (`pass_0b_footer.md:3-32`), and `wrap_section` then adds a footer again. Marley's `08_section_6_dr_prompt.md` has the lyrics block twice (§5 once); Cleopatra's §6 repeats the hostile block.
- **The §1 section prompt says "organised under the six thematic areas below"** but contains one (`pass_0b_header.md:51-57`).
- **The monolithic preamble's save and validate path is pre-Tier-3.** It points to `inputs/dossiers/<slug>_claude_dr.md` (`pass_0b_header.md:67-68`); the pipeline reads `voices/<slug>/01_research/04_dr_dossier/` (`paths.py:118-120`). Also stale: `dr_validation.py:49` (same old path) and `:140` ("prompt asks for 15,000-25,000" words, which no prompt does).

### 2.19 MINOR: the Pass 0b tailor's question count contradicts itself, and following one version aborts Phase 0.5

- **Where:** `pass_0b_tailor.md:116` says "2–3 questions per section, no exceptions". `:118` says "surface fewer questions" when the gaps are thin. `:165` says "Empty list … is an error".
- **The code:** an empty list makes the splice raise, which becomes `sys.exit` (`run_pass_0b_tailor.py:282-283`). `SystemExit` is not caught by `except Exception` in `run_phase0_1_research.py:291`, so the advertised "base prompt remains in place" fallback never happens.
- **Evidence:** code path CONFIRMED; the trigger is PLAUSIBLE.
- **Also:** `:120` defines `observational` as "perception-and-description registers", which contradicts Pass 0a's definition (`pass_0a_voice_config.md:42-44`: reasoning from practice, "NOT … 'they observe well'").
- **Fix direction:** pick one count rule, and catch `SystemExit` (or raise instead of exiting) so the fallback works.

### 2.20 MINOR: the prompts disagree on Te Awa Tupua Act section numbers

- **Where:** `pass_0b_non_human_system.md:148` says "section 18 (Tupua te Kawa values), sections 19–20 (Te Pou Tupua)", and asks DR to quote them verbatim.
- **The others:** Pass 2 (`persona_pass_2_identity_boundaries.md:526,531`, "the four kawa of s.13"), `persona_pass_1a_non_human_system.md:273` and `persona_pass_1d_excerpt_selection.md:45-46` say s.13 is Tupua te Kawa, with Te Pou Tupua from s.18.
- **Evidence:** the disagreement is CONFIRMED. That s.13 is correct is from my knowledge of the Act (PLAUSIBLE); verify before editing.
- **Fix direction:** correct the 0b line.

### 2.21 MINOR: the Step 3 prompt (dormant) gives no output format, but its parser needs exact labels

- **Where:** `voice_step3_amendment.md:41-48` names the fields in prose only. The parser needs:
  - a bare `decision: amend|stand-pat` line (`step3_amended_artifact.py:121-124`). A `**decision:** amend` fails the regex and defaults to "amend";
  - an `amended_artifact_text:` label;
  - amendments in a fenced JSON block (`:185-196`), which the prompt never mentions.
- **Impact:** none today (`--skip-step3`, OPEN_ITEMS A1). It matters when Step 3 returns (C61).
- **Fix direction:** add an `<output>` template in the Step 2 style.

### 2.22 MINOR: the Pass 0b fictional prompt asks DR for tags the shared rules forbid

- **Where:** `pass_0b_fictional.md:72` asks per commitment for "the evidence basis ([stated] … inference … scholarly consensus …)". `_pass_0b_research_discipline.md:9` says "Do NOT produce … `[scholarly_consensus]` / `[stated]` / `[inference]` tags", and `pass_0b_footer.md:43` says "Do not produce other tag forms". CONFIRMED.
- **Fix direction:** ask for the evidence basis in prose. This is the research-stage twin of #11.

### 2.23 NITs

- **N1.** `persona_pass_7_anachronism.md:93-94` says REVISION_NEEDED makes "the pipeline's revision loop re-run Pass 2 / 4a / 5". The loop was replaced by 7a-FIX (FU#13). This is the twin of the filed 7a "max 2 revision loops" line (roadmap 0.4), which is `persona_pass_7a_cross_model.md:145-147`.
- **N2.** `persona_pass_2_identity_boundaries.md:71` ("`header`, `why_selected` … NEVER in runtime card") and `persona_pass_7a_fix.md:99-101` ("`header` (for cited_passages — strip these entirely)", a retired field name) contradict Pass 6, which requires both on every passage. All 10 shipped cards keep both. Latent: a 7a-FIX patch could strip them.
- **N3.** The Pass 7a field→pass map (`persona_pass_7a_cross_model.md:109-110`) lists three Pass 3 fields and omits `finds_compelling` and `resists`. The FU#51 guard corrects the routing from disk (`run_persona_pipeline.py:1292-1318`), so there's no effect.
- **N4.** Derive: the user prompt says "Provocateur Profile (8 fields)" (`persona_derive_user.md:5`); the system prompt says 9 (`persona_derive.md:9`), and the validator has 9. The cross-reference "`runtime/flows/shared/io.py` line ~117" is now `:244`.
- **N5.** `persona_pass_1d_excerpt_selection.md:69` says "four explicit inputs" and lists five. `persona_pass_4a_voice.md:213` names "Tang, Thiel", who aren't on the council. The Provocateur-side Thiel is filed as C68 A14; this persona-side one isn't.
- **N6.** The 7-pre verify user prompt labels the dossier "Pass 1a/1a-DR/1b" (`persona_pass_7pre_verify_batch_user.md:8`); it is the Phase-B chunked merge. The standard branch says "Extract every direct quote" (`persona_pass_7pre_verify_batch.md:46`), against "you do NOT re-extract" (`:11`).
- **N7.** Speaker ID defines an UNIDENTIFIED tier (`transcription_speaker_id.md:17`), but the `confidence` enum (`:59`) has no value for it.
- **N8.** The Editor `<input>` block doesn't list `panel_speakers[]`, which `<composition>` uses (`editor_dossier.md:146`). It calls `theme_display_title` "the panel's working title" (`:8`); it is the Provocateur's display title.
- **N9.** Pass 1.7 categories: the CoherenceFlag enum (`schemas/merged_dossier.py:32-40`) has nothing for checks 6–9, so 11 Athens flags are `other`. An invented category would fail the whole audit (retry, then exit).
- **N10.** Pass 1.6:
  - the `"runtime_contract_note": "<default>"` placeholder (`pass_1_6_merge.md:116`) invites a rewrite. Octopus replaced the contract text; it has no passages, so there's no effect.
  - `:14-15` still promises a "digitised-full-text URL list" (removed in 1-arch-07).
- **N11.** Small text defects:
  - empty `## Never invent` headings (`pass_1_3_merge.md:149`, `pass_1_4_merge.md:93`, `pass_1_5_merge.md:92`);
  - `pass_1_1_merge.md:92` "8+ formative candidates (6+)";
  - `pass_1_2_merge.md:390` "per Block 2 criteria" (Block 2 has none);
  - `persona_pass_1a_fictional.md:267-268` cites a "TRANSLATION TRADITION block above" that doesn't exist;
  - `pass_0b_footer.md:38,40` names `dr_validation.py` to the DR model;
  - internal field names are sent to Perplexity and Gemini (`persona_pass_1a_non_human_organism.md:106-107`, `persona_pass_1b_non_human_system.md:22-23`).

---

## 3. New evidence on items already filed

- **Roadmap 0.4, Derive header "harmless at runtime (code wins)":** not harmless. The header is sent verbatim (#6). The same applies to 7a and 7a-FIX. The model-name content is voices §36; the raw-load mechanism is new.
- **Dead length check (roadmap 0.2 / C38):** the engagement validator is told "Length compliance is checked mechanically by the orchestrator, not by you" (`voice_step2_validation_engagement.md:58`). `_check_length_compliance` returns `None` for the prose constraints every card carries (`step2_validation.py:193`), so no one checks length. All 20 Night-2/3 records have `length_compliance: null`.
- **C42 (safeguards validator's stale stance):** the dormant Step-1 anachronism validator has the same "fluid-across-time" rule (`voice_step1_validation_anachronism.md:12,16`). Fix it with C42, or before `--enable-step1-validation` is used again.
- **C68 A14 (Thiel):** also at `persona_pass_4a_voice.md:213` (N5).
- **Editor spec, "Inconsistencies in the prompt" (`docs/AI_Assembly_Editor_Pipeline.md:662-666`):** the four `editor_dossier.md` contradictions are recorded there as "docs-only" and have no OPEN_ITEMS row. Not re-reported; they need a tracker row to get fixed.
- **Voices §23 (Pass 4a/4b song branch):** the 4b guardrail leftover (#14) is residue of that fix.
- **Voices §19 (Pass 0b phantom citations):** unaffected, but #2 means any fix to the 0b type templates only reaches DR if the section split carries it.

---

## 4. Seen in passing: code defects outside this task

These are not prompt findings, and I didn't check them beyond what is stated. Each needs its own row if the operator wants it fixed.

- `runtime/flows/transcription_flow.py:201-209`: when a speaker label is missing from the Speaker-ID mappings, the counter increments per turn, so each turn of the same unmapped speaker gets a new "Unidentified Speaker N".
- `personas/run_persona_pipeline.py:351`: the review-gate note compares `corpus_constraint` to `"lyrics — describe patterns only"`. The enum value is `lyrics_patterns_only` (`schemas/voice_config.py:26`), so the lyrics warning never renders.
- `personas/run_pass_1_7.py:549-562`: skipped-edit reasons go to stdout only, and `_coherence_audit.json` keeps a count. This is part of #3.

---

## 5. Operator decisions

1. **Scholar names in `epistemic_frame_statement` (#10).**
   - (a) Drop the "name the scholars" requirement from Pass 2 and the card spec. This matches 8 of 10 cards and the cards-are-canon rule. **Recommended.**
   - (b) Keep it and exempt this one field from the strip.
   - (c) Keep it only for `transmission_witness` voices, where citing the record is the stance (Whanganui).
2. **Inline tag policy (#11, #22).** Which tags may a shipped card carry? Recommended: only the two Boddice tags, `[experiential_reconstruction]` and `[projection_warning]`, which is what `bracket_strip.py` already enforces. Then Pass 3's category and fictional-provenance tagging, 7a's tolerate-list and 7-pre's tag-based observational rule all change to match. The alternative, keeping category tags, means changing `bracket_strip.py` instead.
3. **Cluster ids in published theme abstracts (#5).**
   - (a) Strip them, or substitute the Editor's abstract, at publish. **Recommended.** The Researcher prompt is unchanged.
   - (b) Change the theming prompt, which touches the Researcher spec's deliberate design.
   - Either way, check whether the microsite renders `abstract` (ties to C68 R3).
4. **Re-run the Athens record?** Not recommended for #1, #2 or #3. The published record and the shipped cards stand; each fix is forward-only. The one data item is Whanganui's unapplied CF-02 (orphan `work_title`s in merge data, not in the card). It needs no action unless Whanganui is rebuilt.
5. **Order.** #1 and #4 together first: runtime code plus a validator prompt, testable offline, no voice text involved. Then #2, #3, #8, #9, #17–#20 (research and merge plumbing), which affect only the next build. The voice-writing items (#6 Derive/7a-FIX, #7, #10–#16) go into Stage 4 behind the sentinel gate, which needs voices §37 A5 fixed first.

---

## 6. Coverage

**Read fully by me.**
- **Runtime prompts (19):** all.
- **Persona prompts (26):** persona_pass_1d_excerpt_selection, persona_pass_2 system and user, persona_pass_3 system and user, persona_pass_4a system and user, persona_pass_4b system and user, persona_pass_5 system and user, persona_pass_6 system and user, persona_pass_7_anachronism, persona_pass_7a_cross_model and user, persona_pass_7a_fix and user, persona_pass_7b and user, persona_pass_7c and user, persona_pass_7pre_extract and user, persona_pass_7pre_verify_batch and user, persona_pass_7pre_boddice_check and user, persona_derive and user, persona_coherence_threading.
- **Code:**
  - runtime: `card_assembly.py` (voice, and editor `:40-140`), `step1_private_reasoning.py:50-118`, `step2_first_draft_artifact.py` (prompt build and parser), `step2_validation.py` (all), `step3_amended_artifact.py:56-200`, `continuity.py:60-300`, `provocateur_flow.py` (fills, packaging, parser keys), `researcher_flow.py` (user prompts, parsers), `transcription_flow.py:154-245,546-650`, `editor/dossier_generation.py:140-250`;
  - persona: `run_persona_pipeline.py:1-800,820-1110,1560-1660`, `chunk_runner.py`, `prompt_render.py`, `io.py` (both), `bracket_strip.py:1-110`, `pass_7pre_chunked.py:60-140,250-320`, `split_tailored_prompt.py:25-125`.

**Read fully by a subagent; its findings above re-checked by me.**
- **Persona prompts (30):** pass_1_1 to pass_1_6 merge and pass_1_7_coherence; pass_0a_voice_config; pass_0b_dr_prompt, header, footer, _pass_0b_research_discipline; pass_0b human, fictional, non_human_organism, non_human_system; pass_0b_tailor; all four persona_pass_1a and all four persona_pass_1b.
- **Their code and schemas:** `run_pass_1_1.py` to `run_pass_1_7.py`, all `personas/schemas/*.py`, `run_phase0_1_research.py`, `run_pass_0b_tailor.py`, `run_pass0a_voice_config.py`, `node0_validation.py`, `perplexity_split.py`, `dr_validation.py`, `research_validation.py`, `validate_dr_dossier.py`.
- I read the flagged lines of these prompts myself, not every line.

**Skimmed or checked only in part.**
- Specs: `docs/AI_Assembly_Voice_Pipeline.md`, `docs/AI_Assembly_Persona_Card_v2.md`, `docs/AI_Assembly_Researcher_Pipeline.md` and `docs/AI_Assembly_Editor_Pipeline.md`, checked for the passages cited above only.
- Trackers: runtime OPEN_ITEMS (C20a, C38, C42, C62–C68, section headings), voices OPEN_ITEMS §23, §24, §31–§37, the roadmap Phase 0–1 and its read log, and the doc backlog (prompt rows). Searched for each finding before filing it.
- Inline model-facing prompts in code (e.g. `editor/synthesis_router.py:53`, the one-line system prompts at `run_persona_pipeline.py:476,591`) are outside the 75 files and were not reviewed.

**Athens data, read-only:** 30 Step-2 validation records (Nights 1–3), 10 cards, 10 `_coherence_audit.json` files, per-voice DR prompt files (5 voices), 24 published theme files, 3 grouping files, Plato's `continuity_night_2.json`, Marley's card, and the Whanganui merge chunks.
