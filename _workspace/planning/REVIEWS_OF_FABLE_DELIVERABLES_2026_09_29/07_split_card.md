# Review of `_workspace/planning/DESIGN_2026_09_28_split_card_event_config.md`

## Verdict
1. **Quality:** a strong, well-sourced draft. Every quoted card phrase is at the field the draft names. The runtime `file:line` inventory matches `40fe490` line for line, and those lines are still current on `main`. It delivers all six items in the brief.
2. **How far to trust it:** trust the field partition and the hardcoding inventory, and recount the per-voice numbers (four counts are off, one because a scan counted JSON keys). Trust the byte-identity and migration claims **for the voice prompts only**. The editor path and the persona-pipeline path were not checked.
3. **Biggest issue:** the net-complexity pass (§0.5, §6) treats "Phase A + event_config" as one item. `event_config` clearly removes special cases. The Phase A card split on its own does not: the voice cards stay Athens-bound until Phase B, which is deferred. Meanwhile it adds a file type, a merge in at least 4 loaders, a sha pin and a golden-hash table. As the gate is worded, the split should ride with Phase B, not with C52.

## Findings, one by one

Method: read-only. I ran offline Python over `athens-2026` (HEAD `e4c4e39`; its voice and editor cards are unchanged since `0b2af19`, the draft's base). I used `git show 40fe490:<file>` and the HEAD versions of the code. For F7/F8 I ran one offline render: I imported `runtime/flows/{voice,editor}/card_assembly.py` in the runtime venv and made no model call.

**Commit note:** `02006f5` (C67) is an **ancestor** of `40fe490`, the draft's code base (`git merge-base --is-ancestor` = yes). So C67 moved nothing the draft cites, and CONTEXT.md's "since then" does not apply to it. From `40fe490` to HEAD, no runtime file the draft cites has changed; `f7e0d4c` added 5 lines at `personas/run_persona_pipeline.py:393`.

| ID | Claim (short) | Verdict | Evidence / reason |
|---|---|---|---|
| F1 | §0.2/§2.1: the card has 44 top-level keys → 37 V, 5 D, 2 removed | VERIFIED | Same 44 keys in the same order in all 10 voice cards and in Tim's. Summing the row assignments gives 37/5/2. |
| F2 | §0.2: the reader frame is woven into the artifact fields of **8 of 10** voices | WRONG (count) | `medium` alone is 8/10 (all but Plato and Battuta), which is correct. Across fields 27–34 it is **9/10**: Battuta's only hit is `quality_criteria[4]` ("the reader at his breakfast"). Only Plato is clean. Literal "breakfast" appears in 7/10 (Ada, Dostoevsky, Arendt, Battuta, Octopus, Scheherazade, Whanganui); Marley and Cleopatra use coffee/cup/morning. |
| F3 | §0.4: 5 maps, 5 `choices` CLIs, 2 range guards, 4 "night 3 is last" checks and 5 builders/parsers, across 15 runtime files | VERIFIED | Each listed site checked at `40fe490`. The file count is 15 once `dossier_generation.py` and `io.py` (both "keep") are excluded. |
| F4 | §3: the inventory is complete | DOUBTFUL | Missing: `runtime/scripts/build_athens_data_graph.py:43` (`NIGHTS = ["night_1","night_2","night_3"]`), `:586`/`:601` (`f"athens_{night}"` run-dir builder) and `:655` (reads `conference_facts.json` directly, with an `or {}` fallback, so Step 1's "delete once no reader is left" would silently blank its facts); `runtime/scripts/apply_ai_assembly_flags_from_csv.py:45-47` (day-label map); `generate_sessions_json.py:344` (day list); the second unwrap caller (F26); `card_assembly.py:340-345` ("MOVES YOU HAVE ALREADY DEPLOYED THIS CONFERENCE", which is conference wording in code). |
| F5 | §0.4/§3.4: 4 persona prompts are event-coupled, not the roadmap's 5 | VERIFIED | `pass_0a_voice_config.md:36` ("Plato" not "Plato of Athens") and `pass_1_1_merge.md:253/259/284` (Plato worked example) name Athens as Plato's city. Roadmap §2.1 lists the 5 as the draft says. |
| F6 | §1: loader rule; continuity overlay at `card_assembly.py:187-209` | VERIFIED | Overlay at `:187-209` at `40fe490`, unchanged at HEAD. |
| F7 | §1: voice prompts stay byte-identical because fields render from fixed tuples | VERIFIED | Tuples `:82-152`, `_render_section` `:285-310`. The unwrap passes a string through (`:260-261`). Offline render of Plato, Step 2, Night 3, with VTS as the dict and as the `default` string: identical. |
| F8 | §5 Step 2: golden hashes unchanged "for all voice **and editor** prompts" | **WRONG** | The editor's `_render_section` (`editor/card_assembly.py:163-190`) never unwraps VTS. `_render_value` json-dumps the dict, so Tim's prefix contains `"anchored_override": null`. Offline render of Tim, Night 3: prefix sha changes `8d93245803b2` → `205ce7222b9a` when VTS becomes the string (tail unchanged). The Safeguards validator's user prompt is affected the same way: `step2_validation.py:163` renders VTS through `_render_field`, which is also a JSON dump. The Step-0 golden set hashes only the validator *system* prompts, so that change would pass unseen. Fix: keep Tim's VTS as the dict in his deployment card, or accept and re-hash one intended editor change. |
| F9 | §1/§3.2: Pass 5 and 7b read the event at `run_persona_pipeline.py:743-753`, `:1542-1544` | STALE (`f7e0d4c`) | Correct at `40fe490`. At HEAD they are +5: `:748-758` and `:1547-1549`. |
| F10 | §1: C48 design at `runtime/DESIGN_voice_deployment_context.md` | WRONG (trivial) | The file is at `_workspace/planning/runtime/DESIGN_voice_deployment_context.md`, as the brief gives it. |
| F11 | Row 11: VTS event-bound in 11/11; 7 verbatim; Plato "YOUR city"; `anchored_override` null 11/11; "panels' questions require translation" in 8 | VERIFIED | All checked by script. Nuance for the caller: the literal word "Athens" appears in **10/11** (Plato's says "YOUR city"). The draft's wording, "event-bound 11/11", is exact. |
| F12 | Rows 1–26, 36–37, 39, 41 are "Clean" | VERIFIED | Regex scan (breakfast, coffee, cup, audience, conference, Forum, WBBF, 750, Athens, room): all hits are voice-native (Cleopatra's "audiences", Plato's Athens, Marley's "fan / audience"). Borderline: Whanganui `formative_experience` "every deliberation about more-than-human governance", which echoes the event theme. |
| F13 | Row 27: `medium` contaminated in 8/10 | VERIFIED | The 8 are Ada, Marley, Cleopatra, Dostoevsky, Arendt, Octopus, Scheherazade, Whanganui. Every quote was found in `medium`. |
| F14 | Rows 28–32: examples | VERIFIED | Every quote located at its stated field (`technical_capabilities`, `characteristic_output_structure`, `relationship_to_detailed_response`, `aesthetic_qualities`, `stance_tendency`). |
| F15 | Row 33: cup/coffee/morning in 6/10; 350–750 for Dostoevsky and Arendt, 350–500 for Octopus | VERIFIED | Marley, Cleopatra, Dostoevsky, Arendt, Octopus, Whanganui. Scheherazade's "morning gaining" is her native dawn-cut. STATE.md:213 matches. |
| F16 | Row 34: the engagement criterion names the Athens reader in **8/10** | WRONG | It is **9/10**. Missing: Cleopatra `quality_criteria[4]` *"the reader, finishing the decree over coffee"*. The indices for the 8 listed are right (Octopus `[5]`; Arendt is a single string). The Phase-B patch count "×8" becomes ×9. |
| F17 | Row 35: `bold_engagement_topics` addresses the audience in 8/10 | VERIFIED (count conservative) | Quotes verified: Marley `[4]` and `[5]`, Battuta `[2]`, Octopus `[5]`, Plato `[2]`. More echoes of the audience profile: Cleopatra `[5]`, Dostoevsky `[3]`, Scheherazade `[4]`, Whanganui `[5]`, Arendt `[3]` and `[6]`. That is at least 9/10, which makes the D disposition stronger. |
| F18 | Rows 36–37: exceptions in `default_questions` and `disagreement_protocol` | VERIFIED | Scheherazade `default_questions[4]`; Octopus and Marley `disagreement_protocol`. |
| F19 | Row 38: `unique_contribution` is council- or audience-relative in 7/10 | VERIFIED (count conservative) | All 7 quotes found. Cleopatra ("the others at this table") and Scheherazade ("Where another voice will…") are council-relative too. |
| F20 | Row 40: smoke tests have "42 'provocation' and 15 'Athens' hits" | WRONG (evidence) | 42 = the number of chains. "provocation" is the JSON **key** of each chain, and it appears 0 times in the values. "Athens" appears 11 times; 15 only if you count "Athen*". The disposition still holds: chains are generated from `conference_context`, e.g. Plato's "AI Democracy Marathon … in your city". |
| F21 | Rows 42–43: continuity placeholders null in 11/11, never rendered | VERIFIED | `_render_continuity` skips `None`, and the editor tuples exclude these fields. |
| F22 | "Departs from FU#42" | VERIFIED | FOLLOW_UPS.md:448ff puts VTS in V and `default_questions`, `disagreement_protocol`, `quality_criteria` in D, as the draft says. |
| F23 | Carry-forward items appear only in VTS | VERIFIED | Old/New Style, hijrī, "Christian reckoning", "no calendar/no year", 1945, 1906, 428/427 appear only in VTS. Dostoevsky's 1821 also appears in `metadata`. |
| F24 | §2.2: Tim's identity fields name Athens/WBBF; `{night}` only in Tim | VERIFIED | `constitution[16]`, `reasoning_method[7]`, `topics_requiring_care[2]`, `characteristic_moves[6,11]`, `preferred_vocabulary[10]`, `passages[0].id=monster_athens_2026`. Of all cards, only Tim's contains `{night}`. |
| F25 | §3.1 C1–C22 `file:line` | VERIFIED | All match `40fe490` (C1's map is at `:91-98`, not `:89`). The C8 guard and `all_nights` lists match exactly (15 + 7). No runtime file changed through HEAD. |
| F26 | §3.1 C17: unwrap called at `:306`, so the function "is deleted" | WRONG (incomplete) | Second caller: `runtime/flows/voice/step1_validation.py:151,159` imports `_unwrap_voice_temporal_stance`. Deleting it breaks opt-in Step-1 validation (`--enable-step1-validation`). |
| F27 | §3.1 C23 "keep — already event-neutral"; §4.1 default `run_dir_template = "night_{n}"` | DOUBTFUL | `io.py:44` regex `_night[_]?(\d+)\b` does not match `night_1`, because it needs a leading underscore. With the proposed default, the cross-night corruption guard switches off silently. It should use `night_for_run_dir`. |
| F28 | §3.2 P1/P4 lines (`:918`, `:1872-1873`, `:1925`, `:2004`, `:1782`) | STALE (`f7e0d4c`) | At HEAD: `:923`, `:1877-1878`, `:1930`, `:2009`, `:1787`. |
| F29 | §3.2 P2 and §6: chat artifact = voice card + deployment card; delete the strip entries (§6 says "3 chat-strip entries") | DOUBTFUL (self-contradictory) | If the builder merges a deployment card, `bold_engagement_topics` and `smoke_test_chains` come back unless their strips stay (`chat_prompt_builder.py:100`, `:118`; FU#57). Only the 2 continuity entries can go. |
| F30 | §3.3 R1–R10 lines | VERIFIED | Validator line 1s, safeguards `:5/:9/:13`, `editor_dossier.md:4/21/27/31/35/48/58/198`, `{{audience}}` in the 3 provocateur prompts. |
| F31 | §3.3/§4.3: frame variables use "the existing `{{…}}` substitution"; §5 Step 1: validators change "only by the R2 wording" | DOUBTFUL | `step2_validation.py:152/242/295/329` load prompts raw. `{{…}}` exists only in `provocateur_flow.py:335-345` and `step1_validation.py`, so this needs new, if small, code. R3's text ("publish nightly during the conference") differs from the proposed `frame.assembly`, and R4 ("1, 2, or 3") can't render identically, so the editor tail would change. R4/R5 are not placed in any migration step. |
| F32 | §3.4 S1–S6 lines | VERIFIED | `pass_1_4:53-55`, `4a:168-170`, `4b:13-16/88/105/110-111/119`, `pass_2:339-405`, `pass_5:10-40`. |
| F33 | §3.5: continuity handles any night count except two gates | VERIFIED (with caveat) | `continuity.py` writes `_if_night_{N+1}`, `_render_continuity` is keyed by night, and the prior-night readers (`publish.py:73-79`, `step2_validation.py:385-405`, orchestrator `:460-464`, `edition.py:313`) are count-agnostic. Caveat: the draft does not mention runtime C68 A10 (filed `0998fa2`, before the draft). A10: Night-N continuity summarises only Night N−1. The operator (2026-09-28) put that code decision into Stage 5, which is this design. |
| F34 | §3.5: final-night notice hand-appended to all 10; flag true; 9 timestamps at 2026-05-11T12:18; no code writes it; caused the C42 false positive | VERIFIED | All 10 files carry the flag and have "FINAL NIGHT" in both blocks. Scheherazade has no timestamp. `git grep` of both repos finds no writer. C42's 2026-05-29 recurrence paragraph names the notice. The timestamps run microseconds apart (.514→.521), which points to a throwaway script rather than a literal paste. |
| F35 | §3.6: duplicates | VERIFIED | `council_config.audience == audience_profile.participant_profile`: True. Roster equals the member names. The dates are in 4 places. |
| F36 | §4.2: `model_routing.py` twin + parity test `:114` | VERIFIED | `test_personas_copy_is_identical` at `:113-115`. |
| F37 | §5 Step 1: "19 test files" pin Athens nights/days | PLAUSIBLE | My greps give 12–17 files depending on the pattern. The draft doesn't state its pattern. |
| F38 | §5 Step 2: only the persona "assemble step" needs rerouting; sha pin is a hard error (D5) | DOUBTFUL | The persona pipeline re-reads and re-writes `07_…json` in several places (HEAD `:1753` metadata-preserving rewrite, `:1886`, `:1900` Pass 7a FINAL on the full card, `:2004` Derive, `:2057` final metadata write, `:2071` chat). Derive and 7a FINAL consume D fields. If the pin covers `metadata`, every pipeline metadata write breaks the pin. Step 2 also rewrites the shipped athens-2026 cards in place, which needs an operator OK. The draft flags that only for Step 1. |
| F39 | §6: event_config removes the listed special cases | VERIFIED | Every listed literal, guard and builder exists at the cited lines. Replacing them with one file and one loader is real consolidation (plus the F4 sites). |
| F40 | §0.5/§6: "Phase A plus event_config removes more than it adds" | DOUBTFUL | True for event_config. For the Phase A split alone, the draft admits voice cards stay event-bound (F2/F16: 9/10) until Phase B. The per-event surgery saving and the reuse only arrive with Phase B. Phase A adds a file type ×11, merge/overlap/sha logic in ≥4 loaders (voice, editor, chat, the persona pipeline's 7a FINAL/Derive) plus `step1_validation`, pin friction, and a permanent golden table. It removes about 40 lines of unwrap, 2 nulls, 3 exclusion entries and 2 strip entries. As the gate is worded ("adds config surface without removing special-casing → don't"), the split belongs with Phase B. |

**Tally:** 25 VERIFIED · 1 PLAUSIBLE · 6 DOUBTFUL · 2 STALE · 6 WRONG.

## Problems with the document
- **Contradictions:**
  - §0.2's "8 of 10" doesn't match its own rows (row 34 Battuta, plus Cleopatra missing).
  - P2 deletes the FU#57 strip, yet the chat artifact merges the deployment card (F29).
  - Step 1 says "only R2 changes", while R3 and R4 as mapped change wording (F31).
  - Step 2 claims editor byte-identity, but the editor json-dumps VTS (F8).
- **Unchecked scope:**
  - §1's "CONFIRMED by reading the code" covers the voice renderer only. The editor, the Step-2 validator and the persona pipeline's own card reads were not checked (F8, F38).
  - The counting scripts stayed in the Fable scratchpad, so the counts can't be reproduced. One scan counted JSON keys (F20).
- **Missing from the inventory:** see F4 and F26. The roadmap §2.1 "Researcher scale mode" bullet isn't mentioned (not in the brief's six items, so optional).
- **Continuity:** §3.5 doesn't mention C68 A10, which was already filed (F33).
- **Rules:** no sign of a breach. The draft says read-only and offline. The file was committed by the main session (`0910a66`), as the brief intended. I could not check the Fable scratchpad scripts.
- **Line base:** everything is pinned to `40fe490`. Runtime lines are still current; the persona pipeline lines after `:392` are +5 (F9, F28).

## Questions for the originating session
1. **Did you check how the editor and the Step-2 safeguards validator render `voice_temporal_stance`?** Both json-dump the dict. *Why it matters:* the Step-2 byte-identity claim and D5. *What changes:* if Tim's deployment card must keep the dict, the "store as unwrapped string" rule becomes per-renderer, or the editor gets one accepted re-hash.
2. **Can you rerun your per-voice scan with JSON keys excluded and a term list that includes coffee and cup, and attach the table?** *Why it matters:* the Phase-B patch list and D10's cost. *What changes:* the engagement criterion ×8 becomes ×9, the smoke-test evidence gets restated, and the §0.2 count gets fixed.
3. **How should the persona pipeline's own card reads and writes (7a FINAL, Derive, the metadata rewrites) see the split, and does the sha pin cover `metadata`?** *Why it matters:* D5 (hard error). *What changes:* if the pin includes metadata, a hard error fires on every pipeline run, so the pin must exclude metadata or D5 flips to warning.
4. **For N>3 nights, does your Step 3 assume continuity carries only Night N−1 (today's behaviour) or all prior nights (the spec)?** *Why it matters:* C68 A10, which the operator put into Stage 5. *What changes:* "all prior nights" adds a merge rule to Step 3; "last only" means fixing the spec.
5. **With Phase B deferred, would you still recommend Step 2 (the split) before a second deployment exists?** Or would you sequence Steps 0, 1 and 3 now and Step 2 together with Phase B? *Why it matters:* the net-complexity gate. *What changes:* if the split doesn't net out alone, Stage 5's 2.1 shrinks to C52 plus continuity.

## Operator decisions it asks for
| # | Decision | Draft's recommendation |
|---|---|---|
| D1 | Depart from FU#42 (VTS → D; `default_questions`, `disagreement_protocol`, fidelity criteria → V) | Depart (a) |
| D2 | Artifact fields: form constitution in V, cleaned in Phase B, vs the whole ARTIFACT section in D | V, cleaned in Phase B (a) |
| D3 | `event_config.json` absorbs `conference_facts.json` | Absorb (a) *(note F4: `build_athens_data_graph.py` still reads the old file)* |
| D4 | Voice cards copied per project with a sha pin, vs a shared library root | Copy now; library with the hub |
| D5 | sha-pin strictness | Hard error with a re-pin command *(see Q3)* |
| D6 | Keep the `07_persona_card_assembled.json` name | Keep, add `metadata.card_schema` |
| D7 | Final-night notice as config | `event_config.final_night_notice` when the next multi-night run is planned; Athens keeps its hand-injected text |
| D8 | Stage 4 item 1 vs S4 | Remove the VTS block from Pass 2 during Stage 4. *Now live:* the Stage 4 backport draft (`voices/DESIGN_2026_09_28_stage4_prompt_backport.md` item 1, `47dcc7a`) rewrites it **inside** Pass 2, i.e. option (b). |
| D9 | Family-of-forms lengths in the deployment card vs `forms[].length` in the voice card | Deployment card (a); needs reconciling with `DESIGN_2026_09_28_family_of_forms.md` |
| D10 | Phase B timing | When a second deployment is prepared |
| D11 | Editor identity via `council_config.editor_slug` and the same loader | Yes (a) |
| D12 | `--skip-step3` | Leave in the orchestrator (profiles, 2.3) |
| D13 | Collapse the byte-equal duplicates | Leave for now |
