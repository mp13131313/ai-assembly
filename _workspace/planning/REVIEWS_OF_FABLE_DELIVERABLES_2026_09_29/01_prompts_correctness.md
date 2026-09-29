# Review of `_workspace/planning/runtime/REVIEW_2026_09_28_prompts_correctness.md`

Reviewed 2026-09-29 at `main` `0910a66`, read-only. No API calls and no pipeline runs. One offline Jinja `parse()` of four prompt files was run in the personas venv to test the fix proposed in #6. The athens-2026 files were read, never written.

## Verdict

1. **Quality: high.** All three MAJORs hold up against the code and the Athens data. Of the 19 MINORs, 16 hold up in full when checked line by line. #6 is half wrong, #14 is overstated, and #20 is plausible but not checked against the Act. The evidence is concrete and reproducible, and CONFIRMED is kept apart from PLAUSIBLE.
2. **Trust:** you can act on #1, #2, #3, #5, #7, #15, #18, #19 and #21 as written. Take #6, #11, #14 and #20 with the corrections below. One statement is stale: "sentinel_regen.py can't run". It was fixed by `f7e0d4c`. C67 (`02006f5`) and §37 (`f7e0d4c`) changed no prompt file, so no finding is fixed. Only some line numbers have drifted.
3. **Biggest issue:** the fix proposed in #6 is wrong for `pass_0a_voice_config.md`. The document says rendering the raw-loaded prompts "through `prompt_render.render()`" is a drop-in. For Pass 0a it isn't: the literal `{% if hostile_sources %}` at `:98` has no closing tag, so Jinja fails to parse the file ("Unexpected end of template … 'endif'"). The lines of Pass 0a it calls "developer notes" are also mostly real instructions to the model.

## Findings, one by one

| ID | Claim (short) | Verdict | Evidence / reason |
|---|---|---|---|
| §1 | All 75 prompt files are loaded by live code; no dead files | VERIFIED | Grepped every basename outside the tests. 67 are referenced directly. The 8 `persona_pass_1a_*`/`1b_*` files load via `_pick_template("persona_pass_1a"/"1b")` (`run_phase0_1_research.py:129,148`). There are 56 + 19 files. |
| §1 | "Every runtime output contract matches its parser" | DOUBTFUL | The document's own #21 (Step 3's prompt vs its parser) and N7 (Speaker ID's `confidence` enum has no UNIDENTIFIED value) contradict this. It is true only of the *active* contracts. |
| Header, §5.5 | `sentinel_regen.py` can't run; voice-writing fixes must wait for §37 A5 | STALE | Fixed in `f7e0d4c` (`sandbox` + `regen --project … --baseline-project …`). Caveat from CONTEXT: the gate diffs pass outputs, not assembled cards, and re-runs the whole pipeline including Derive. |
| 1 | Echo loader reads the wrong key; the echo pillar never ran at Athens | VERIFIED | `step2_validation.py:401` reads `artifact_text`/`body`, but `publish.py:223-226` writes `artifact.text`. Athens `published_artifacts/nights/night_1/*.json` all have `artifact.{title,subtitle,text,…}`. All 20 Night-2/3 records have `cross_night_echo: null`, and null (not a WARN dict) means the pillar was never scheduled (`:438-443`, `:470`). The test fixture is flat (`test_step2_validation.py:117-124`). The spec shows 29/30/30 calls (`Voice_Pipeline.md:1274`). C20a leans on it (OPEN_ITEMS `:1146,1166,1170`). Not filed anywhere (grepped trackers). |
| 2 | Per-section DR prompts drop the type preamble and the curator note | VERIFIED | `split_tailored_prompt.py:70-77` slices from `## Section N:`, and `pass_0b_dr_prompt.md` puts each type file's preamble before §1. The curator note is spliced before `## Section 1:` (`run_pass_0b_tailor.py:144-151`). Greps of athens-2026: Whanganui's monolithic prompt has the INDIGENOUS block (`:35`) and the curator note (`:59`), and all six section files have neither. Scheherazade's NARRATIVE-FUNCTION block and the Marley and Octopus curator notes follow the same pattern. All 10 voices have `04_dr_dossier/01…06`. |
| 3 | Pass 1.7 example paths are wrong; edits are skipped silently; Whanganui CF-02 is recorded as "Resolved by edit" but was never applied | VERIFIED | Prompt `:141-142` gives `passages[7].citation`. `_CHUNK_ROUTING` has `passages` as a wrapper (`run_pass_1_7.py:317`), and the field is `citations` (`schemas/pass_1_6.py:110`). Skips are caught (`:541-544`) and only counted in the audit. The prompt claims "fails loudly" (`:251-253`). Example A lacks `definition`/`evidence_tag` (`schemas/pass_1_2.py:103-118`) and citation `tier` (`_conventions.py:61`). Whanganui audit: applied 4, skipped 6, CF-02 "Resolved by edit", and no passage edit in `edit_log`. 11 of 22 passages have orphan `work_title`s in both the chunk file and `08_merged_dossier.json`. Arendt used `passages.passages[8]`; the other 9 voices skipped 0. That the six skips were the short-form path is an inference; the audit keeps no reasons. |
| 4 | The echo validator treats the continuity memory as instructions | VERIFIED | The prompt reads the overlay as instructions and flags ignoring it (`:6,21,27,51`); the user-prompt label is at `step2_validation.py:337`. `voice_continuity.md` asks for a first-person memory ("WHAT I CHOSE TO WRITE"). The spurious WARN/HOLD once #1 is fixed is PLAUSIBLE. |
| 5 | `cluster_NNN` ids appear in every published theme abstract | VERIFIED | 24 of 24 `themes/night_*/theme_*.json` `abstract`s match `cluster_\d+`. `publish_flow.py:352` publishes `abstract = researcher_abstract`. Zero hits in `dossiers/` and `nights/`. (`data_views/` also contains them, but that is an internal viewer.) |
| 6a | Derive, 7a and 7a-FIX send their `{# … #}` headers to the model | VERIFIED | `io.py:71-76` returns the raw text. Derive is loaded raw (`run_persona_pipeline.py:927`, was 922) and routed to opus-4-7 with thinking `adaptive` (`model_routing.json`), yet the header says "Sonnet … no thinking needed". All three files parse as Jinja with no variables, so `render()` really is a drop-in for these three. |
| 6b | Pass 0a sends developer notes (`:1,16,38,62,136`) and a literal `{% if %}` (`:98`); fix by rendering through `render()` | WRONG | Those lines are instructions to the model ("Do NOT emit `conference_context`", the field enums), not developer notes. `:98` is prose describing the branch. `jinja2.Environment().parse()` on the file raises "Unexpected end of template … 'endif'", so the proposed drop-in would break Pass 0a. |
| 7 | Step 1 promises "editorial flags" that the code strips | VERIFIED | Prompt `:2,50`. `filter_theme_record_for_step1` drops `theme_flags` (`card_assembly.py:511-534`). The label is "WIDER RECORD…" (`step1_private_reasoning.py:113`). The briefing hint about `full_theme_record` is at `provocateur_flow.py:1210-1215`. |
| 8 | Merge prompts name fields/values the schemas reject | VERIFIED | Checked 5 of 6 rows: `purpose_tag` vs `Passage.purpose`; `experiential` and `interpretive_reconstruction` are not in `EvidenceTag` (`_conventions.py:31-45`); `voice_mode` is a Literal of three values (`pass_1_3.py:82`); 1.4 skeleton `\| null`, but `chunk_runner._validate` calls `validate_chunk_output(model, None)`. The 1.2 row (4th key missing from the task block) matches `pass_1_2_merge.md:377-395`. The retry cost is PLAUSIBLE. |
| 9 | Merge prompts route content to fields that don't exist | VERIFIED | No pass-1 schema sets `extra` (only `voice_config.py` and `merged_dossier.py` have a `model_config`). `contested_exclusions` and `textual_evidence` appear in no schema. The 1.1 block's first two routes can't be emitted by 1.1. Its third route (`scholarly_context`) *is* valid for `FormativeCandidate` (`pass_1_1.py:297`), so the loss is partial and PLAUSIBLE. |
| 10 | Pass 2 both requires and strips scholar names; cards split 8/2 | VERIFIED | `:78-90` STRIP vs `:249-262` "name the specific scholars". Shipped frames: only Octopus and Whanganui name scholars. Marley mentions "scholar" only as a negation. |
| 11 | Pass 3 / 7a / 7-pre / `bracket_strip.py` disagree on inline tags | VERIFIED (slightly overstated) | Scheherazade: `evidence_tag` scholarly_consensus 11 + stated 5 on 16 of 17 principles. Cleopatra, Dostoevsky, Arendt and Battuta carry the `[ontological]/[epistemological]/[ethical-political]` tags. 7a `:47-65` calls them "preserved by … allowlist", but they are on the strip list (`bracket_strip.py:77-100`). Overstated: the strip list does **not** include `[experiential]`, `[artistic]`, `[attributed by narrative function]` or `[scholarly consensus]` (with a space), so "strips all of these" is not quite right. |
| 12 | Pass 3/4a user prompts ask for the attribution their system prompts strip | VERIFIED | `persona_pass_3_user.md:29-33,58` and `persona_pass_4a_user.md:49-51` vs the STRIP rules (`persona_pass_3_intellectual_core.md:55-58` and following). That no shipped card has a `scholarly_context` sub-field was not re-checked. |
| 13 | Pass 2 system prompt uses inputs its user prompt doesn't send | VERIFIED | The system prompt cites `analytical_context_*` (`:12-19`) and "moves + register" (`:320`). The render at `run_persona_pipeline.py:498-505` passes only the 1.1/1.5 chunks and the debate frames. |
| 14 | Pass 4b `medium` guardrail contradicts the musical variant | DOUBTFUL (severity) | The text conflict is real (`:87-93` vs `:122+`). But the variant opens with "Override the field-spec defaults above", so the prompt itself declares which rule wins. At most a NIT. |
| 15 | Pass 7 `PERIOD:` gets `str(dict)[:300]` | VERIFIED | `run_persona_pipeline.py:1049` (was 1044). `world` is a dict on all 10 cards. |
| 16 | Editor told `fault_line_present` means the panel split | VERIFIED | `editor_dossier.md:12` vs `provocateur_triage_flags.md:18-20` (the council's traditions). |
| 17 | Research/merge prompts branch on voice_config values they never get | VERIFIED | `hostile_sources` is passed to 1.1 (`chunk_runner.py:285-293`) but only prose uses it (`pass_1_1_merge.md:161`). `wikipedia_disambiguation_hint` is absent from `schemas/voice_config.py` and Pass 0a. `mediation_stance` is not in the Pass 0a prompt. The 0b render context has no `editorial_rationale` (`run_phase0_1_research.py:248-258`). |
| 18 | DR plumbing: doubled §6 blocks, "six areas" in a one-area prompt, stale save path | VERIFIED | Marley's §6 has "MUSICAL VOICE — LYRICS CONSTRAINT" twice (§1–§5 once each). Cleopatra's §6 has the HOSTILE block twice. Marley §1 says "six thematic areas below" (`:36`). The save path was not re-checked. |
| 19 | Tailor's question-count rules contradict each other; an empty list aborts Phase 0.5 | VERIFIED | `run_pass_0b_tailor.py:275-283` turns the `ValueError` into `sys.exit`. `run_phase0_1_research.py:291` catches only `Exception`, so `SystemExit` escapes and the "base prompt remains" fallback never runs. The trigger is PLAUSIBLE. |
| 20 | Te Awa Tupua section numbers disagree | PLAUSIBLE | 0b `:148` says "section 18 (Tupua te Kawa)". Pass 2 (`:526,530`) and 1a (`:275-276`, "§13") say s.13. 1d (`:45-46`) gives only the range "sections 12–20", not s.13. That s.13 is correct matches my knowledge of the Act; verify against legislation.govt.nz before editing. |
| 21 | Dormant Step 3 prompt has no output format its parser can read | VERIFIED | `_DECISION_RX` is now at `step3_amended_artifact.py:127-130` (was 121-124). C67 R1 changed peer names, not the parser. `**decision:** stand-pat` fails the regex (after `:` it expects the value, not `**`) and defaults to "amend". The amendments JSON-fence (`:191-196`) is never asked for in `voice_step3_amendment.md:41-48`. |
| 22 | 0b fictional asks DR for tags the shared rules forbid | VERIFIED | `pass_0b_fictional.md:72` vs `_pass_0b_research_discipline.md:9` ("Do NOT produce … `[scholarly_consensus]` / `[stated]` / `[inference]`") and `pass_0b_footer.md:43`. |
| N1 | Anachronism prompt cites the retired revision loop | PLAUSIBLE | Not re-checked. |
| N2 | Pass 2/7a-FIX say strip `header`/`why_selected`; Pass 6 requires them | VERIFIED | `persona_pass_2…:71`, `persona_pass_7a_fix.md:99-101`. All 10 cards keep both on every `curated_corpus_passages.passages` entry. |
| N3 | 7a field→pass map omits two Pass 3 fields | PLAUSIBLE | Not re-checked. |
| N4 | Derive 8 vs 9 fields; stale `io.py` line | VERIFIED, but partly already filed | `persona_derive_user.md:5` says 8, `persona_derive.md:9` says 9. `_REQUIRED_MEMBER_FIELDS` is at `io.py:244`. The roadmap already records the 8-vs-9 count (`PLAN…roadmap.md:65`, "just whether `name` is counted") and the document doesn't cite it. `CLAUDE.md` also says "8 fields". |
| N5 | 1d "four inputs" lists five; 4a names Tang, Thiel | VERIFIED (Thiel part) | `persona_pass_4a_voice.md:213`. The 1d count was not re-checked. |
| N6 | 7-pre verify labels | PLAUSIBLE | Not re-checked. |
| N7 | Speaker ID UNIDENTIFIED tier has no enum value | VERIFIED | `transcription_speaker_id.md:17` vs `:59`. |
| N8 | Editor `<input>` omits `panel_speakers[]`; title wording | PLAUSIBLE | `:8` wording confirmed; `panel_speakers` not checked. |
| N9 | No CoherenceFlag category for checks 6–9; 11 Athens flags are `other` | VERIFIED | `merged_dossier.py:32-40`. Exactly 11 `other` across the 10 audits. |
| N10, N11 | Pass 1.6 placeholders; small text defects | PLAUSIBLE | Not re-checked. |
| §3a | The Derive header is not "harmless" | VERIFIED | Sent verbatim (see 6a). The roadmap text is at `PLAN…roadmap.md:65`. |
| §3b | The length check is dead | VERIFIED | `length_and_format_constraints` is a string on all 10 cards, so `_check_length_compliance` returns None (`step2_validation.py:193-194`). All 20 Night-2/3 records have `engagement.length_compliance: null`. |
| §3c–f | C42 twin; 4a Thiel; Editor spec inconsistencies lack a tracker row; §23/§19 links | VERIFIED (c, d, e: grep), PLAUSIBLE (f) | Editor spec `:662-666`: no OPEN_ITEMS or backlog row. |
| §4a | An unmapped speaker gets a new "Unidentified Speaker N" on every turn | VERIFIED, not fixed by C67 | `transcription_flow.py:191-209`: the counter increments per turn, not per label. |
| §4b | The lyrics warning in the review gate never renders | VERIFIED | `run_persona_pipeline.py:351` vs `voice_config.py:26`. |
| §4c | Skip reasons go only to stdout | VERIFIED | `run_pass_1_7.py:549-562`. |

**Tally (42 rows):** VERIFIED 32 · PLAUSIBLE 6 · DOUBTFUL 2 · STALE 1 · WRONG 1.

## Problems with the document

- **An internal contradiction:** §1 says "every runtime output contract matches its parser", but #21 and N7 are output-contract mismatches in runtime prompts.
- **#6 has the wrong fix and overreaches.** The Pass 0a part is wrong (see 6b), and following the fix literally breaks Pass 0a. A safer fix for all four files: strip `{#…#}` in `load_prompt`, or render only the three files that parse.
- **Overstatements:** #11 (the strip list is narrower than stated), #14 (the variant declares that it overrides), #20 (1d cites a range, not s.13).
- **A re-report:** N4's 8-vs-9 count is already in the roadmap (`:65`). The brief says don't re-report filed items without adding evidence.
- **Stale since writing:** the sentinel gate statement (`f7e0d4c`). §5.5's ordering ("behind the sentinel gate, which needs §37 A5 fixed first") should now read "behind the sentinel gate, which compares pass outputs, not the assembled cards". That matters for #6 (the Derive output is downstream of the card) and for the card-level items #10 and #11.
- **Line drift after `f7e0d4c`/C67:** `run_persona_pipeline.py` shifted +5 after line 390 (1044→1049, 1091→1096, 1366→1371, 922→927), and `step3_amended_artifact.py` shifted 121→127. The references were correct at `4e61444`.
- **Brief coverage:** the brief also asked for "variables the code passes that no prompt uses". The document reports no explicit result, only one example (`hostile_sources` in 1.1, #17). The reader can't tell whether the check was run.
- **Extra sections:** §3–§5 go beyond the brief's three-part deliverable. They are useful and labelled as such. §4 is out of scope but flagged as unchecked.
- **Rules:** complied. It was read-only, made no model calls or pytest runs, put its scratch scripts outside the repo and named them, and only read athens-2026. It used read-only subagents, which the brief doesn't forbid, and says it re-checked their findings.

## Questions for the originating session

1. **#3: did you see the actual skipped paths (a stdout log of the Whanganui 1.7 run), or infer that the six skips were short-form `passages[N].work_title`?**
   - *Why it matters:* the audit keeps no reasons.
   - *What it changes:* if the skips were validation failures (the passage model rejecting the new `work_title`) or index errors instead, the fix is in `_route_edit_to_chunk_file`/validation, not just in the prompt example.
2. **#6: did you mean the "render via `prompt_render.render()`" fix to cover `pass_0a_voice_config.md`?**
   - *Why it matters:* that file doesn't parse as Jinja.
   - *What it changes:* if yes, the fix direction must change to stripping comments in `load_prompt`, or rendering only Derive, 7a and 7a-FIX.
3. **#1: did you compare any Night-2/3 artifacts with the voice's previous-night piece, to see whether real echo got through at Athens?**
   - *What it changes:* whether #1 is a forward-only fix or also needs a note in the published-record assessment, and whether it goes ahead of C68 A10 (the Stage 5 continuity redesign).
4. **#2: is there any evidence the operator pasted the monolithic preamble or curator note into the Deep Research threads by hand?** For example, from voices §17/§28 or the Marley `PRE-TRIM` history.
   - *What it changes:* the Athens runtime effect goes from PLAUSIBLE to confirmed or refuted. That decides whether #2 carries an Athens-record caveat for Whanganui.
5. **#14: given that the musical variant says "Override the field-spec defaults above", do you still rate it MINOR?**
   - *What it changes:* if not, it drops to a NIT and leaves the Stage 4 voice-writing queue.

## Operator decisions it asks for

1. **Scholar names in `epistemic_frame_statement` (#10).** Recommended: (a) drop the "name the scholars" requirement from Pass 2 and the card spec. This matches 8 of 10 cards. The alternatives are (b) exempt the field from the strip, or (c) keep names for `transmission_witness` voices only.
2. **Inline tag policy (#11, #22).** Recommended: only `[experiential_reconstruction]` and `[projection_warning]` survive, as `bracket_strip.py` does now. Align Pass 3, 7a and 7-pre to match. The alternative is to keep the category tags and change `bracket_strip.py`.
3. **Cluster ids in published abstracts (#5).** Recommended: (a) strip them at publish, or substitute the Editor's abstract, and leave the Researcher prompt unchanged. Either way, check whether the microsite renders `abstract` (C68 R3).
4. **Re-run the Athens record?** Not recommended for #1, #2 or #3; all fixes are forward-only. Whanganui's unapplied CF-02 needs no action unless Whanganui is rebuilt.
5. **Order.** Recommended:
   - first, #1 and #4 together;
   - then the research and merge plumbing: #2, #3, #8, #9, #17–#20;
   - last, the voice-writing items (#6, #7, #10–#16), in Stage 4 behind the sentinel gate. That gate now runs (`f7e0d4c`), so the "fix §37 A5 first" precondition is gone.
