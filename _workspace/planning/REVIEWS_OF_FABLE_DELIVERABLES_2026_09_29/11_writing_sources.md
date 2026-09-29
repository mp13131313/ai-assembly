# Review of `_workspace/planning/WRITING_SOURCES_2026_09_28.md`

Reviewer: Opus 5.5, 2026-09-29. Read-only. No API calls, no runner scripts. I read the whole deliverable and checked it against the athens-2026 data (`published_artifacts/`, `runs/`), the specs, the trackers, and the code. For line citations to STATE, CHANGELOG and the trackers, I used the versions at `40fe490`, the deliverable's base. In this review, "the operator's name" stands in for the name itself.

## Verdict

- **Quality:** high. The headline counts, 40+ of 45 quoted lines, the transcript turns, the Briefing and tracker quotes, and the editor cost all check out against the data. Privacy handling of third parties is clean.
- **Trust:** trust the counts and most quotes as they stand. Don't reuse the cost total, the §6.6 leak scope, or the Night-2 River framing without the corrections below. Two quotes are wrongly attributed to voice pages.
- **Biggest issue:** §6.6 understates the anonymization leak. The operator's name is also in 7 dossier `headnotes[].formulation_text` fields, and `headnotes` is explicitly inside the Night-1 rule's own listed scope. It is also in the published `thinking_trace` of 5 dossiers. The handoff has already copied the deliverable's narrow "panel_speakers" scope into its urgent list (`runtime/HANDOFF_2026_09_28.md:60`), so a repair filed from it would miss most occurrences. Close second: the Provocateur cost uses the wrong cache multiplier (~$48 should be ~$34), so the "~$130" sentence should read ~$116.

## Findings, one by one

| ID | claim (short) | verdict | evidence / reason |
|---|---|---|---|
| §0.1 | 13 dossiers, 30 voice pages, 30 sessions, 529 positions, 128 questions | VERIFIED | Counted the files: `dossiers/night_*` 5+5+3, `nights/night_*` 10×3, `01_transcription/*` 12+10+8. `all_extractions.json` gives 205+199+125, and `03_provocateur/formulations/` gives 46+46+36. |
| §0.2 | River line; "five voices refusing *grant*" (N3/001); "landed in the room" | VERIFIED | The line is on `N1 whanganui_river` and is the pull quote of N1/003. N3/001 has 5 headnote voices, and its subline says "a single verb the voices refuse from five different chains". Beastopia t56 verbatim. |
| §0.3 | Voice ~$72 measured; Provocateur ~$48; editor ~$10 | Voice VERIFIED · Provocateur **WRONG** · editor VERIFIED | Voice: `Voice_Pipeline.md:1278-1280`. Editor: I recomputed $2.09 / $4.54 / $3.29 = $9.93 from dossier `metadata`. The editor uses `stream_voice_call` with a 1h TTL, so 2× is right there. Provocateur: I reproduced $16.21 / $17.88 / $13.52 at 2× cache writes, but the Provocateur caches with `{"type":"ephemeral"}` (5-min TTL), both today (`provocateur_flow.py:396`) and at Athens (`da8ca9e`). 5-min writes bill at 1.25×. Corrected: $11.83 / $12.89 / $9.65 = **~$34.4**. About 3.5M cache-write tokens were written and ~0.02M read. |
| §0.4 | Step 3, matrices, video, Day 4, Suno, Substack dropped | VERIFIED | A1 (line 92), B2 🔴, B4 closed, B5 🔴, B6 🔴, B7 ⚠️ partial. |
| §0.5 | §33: rigor "does NOT" establish authenticity | VERIFIED | `voices/OPEN_ITEMS.md:1329` (bold markup in source). |
| §1.1 | Briefing quotes with line numbers | VERIFIED (1 minor misquote) | 25 quotes grepped; all present at the cited lines. Minor: *"neither an ML researcher"*: the source (line 31) reads "Neither **is** an ML researcher". |
| §1.2–1.3 | Design Principles §1/4/8/10, line 65; Nine Modes lines 3/66 | VERIFIED | Grep: lines 5, 23, 43, 57, 65; Nine Modes 3, 66. "None of the nine modes shipped" not checked (PLAUSIBLE). |
| §1.4 | Act One t255/t256; the Arendt "prototype" quote exists only in this transcript and the data_views | VERIFIED | Turns read. The quote appears only in that session's transcript files (`session_package`, `out_01`, `out_03`) and the two data_views. The provotype/prototype point is correctly labelled inference. t14 and t378 verbatim. |
| §2.1 | Event 7–10 May 2026; ten voices; Tim as 13th persona | VERIFIED | Briefing line 3; STATE 195. |
| §2.2 | Sessions 12 (9+3) / 10 (9+1) / 8 (7+1) | VERIFIED | `_vendor_*` fields mark 3 / 1 / 1 reflection sessions. |
| §2.2 | Turns, words, extractions, clusters, themes; 8 themes selected, 3 dropped | VERIFIED | Counted from JSON (37/35/14 clusters, 11/8/5 themes). N1 manifest `selected_themes: 8, dropped_themes: 3`. |
| §2.2 | Step-1 files 43/46/36; the missing three are Cleopatra, Battuta, River | VERIFIED | Set difference: cleopatra×theme_004, ibn_battuta×theme_004, whanganui_river×theme_002. The link to the rerun is correctly marked PLAUSIBLE. |
| §2.2 | Validator 3/6/1, 2/8/0, 2/7/1; 22 of 23 released | VERIFIED | Counted `step2_validation/*.json` `overall_verdict` and `operator_decisions/*.json`: N2 has 7 release + 1 `hold_for_regen` (the River). |
| §2.2 | Artifacts 18,466 words (377–826) | VERIFIED | `word_count` field and a whitespace split agree. |
| §2.2 | Dossier bodies 7,179 words (432–633) | STALE | Now **7,166 (431–632)**. athens-2026 `e4c4e39` stripped one stray `**` per dossier. |
| §2.2 | Editor thinking 142,799; Step-1 thinking 534,349 over 125 files | VERIFIED | Recomputed exactly. |
| §2.3 | Editor spec ~$3–6; Researcher $15–25; transcription $5–10; infra €110–150; persona $18–22 | VERIFIED | Lines 176, 638, 445, 255–261, 168 read. |
| §2.3 | "Defensible sentence: roughly $130" | **WRONG** | 72 + 34 + 10 ≈ **$116** once the Provocateur is corrected. Also labelled "inference", but it's a calculation. |
| §2.3 | Times: editor 4m59s / 8m44s; 91–298 s (median 151); Step 1 ~90–115 s, Step 2 ~65–95 s; clock 12:00–12:26 / 12:55–13:00 | VERIFIED | Lifecycle:439, Editor:319, Voice:92, STATE 67–68. |
| §2.4 | Timeline rows | VERIFIED (sample) | CHANGELOG@40fe490 lines 22, 35–39, 147, 163, 171, 177, 193, 226, 241, 258 match. voices §24 dated 2026-05-04. |
| §2.5 | Promised vs ran | VERIFIED | B-item statuses as above; A1 "Trade made (with eyes open)", *Lost:* line 97. |
| §2.6 | No unprompted Assembly mentions on Days 2–3 except Reality Tunnels t52 and Beastopia t56 | VERIFIED | My own regex over the Night-2/3 transcripts: only incidental Plato/Arendt hits, t52, and t56. Day-1 turns t142/146/150/214/215/303/410/463 read. |
| §3.1-1 | Vote: "rivers and forests get a vote (all green)" | DOUBTFUL | The live turn t144 says "Half of the room just gave them a vote." "All green flags went up" comes only from the operator's later retelling (t56). The essay should say which account it is using. Octopus quote (t150) and "Very good, this AI Assembly" (t153) are VERIFIED. |
| §3.1-2/3 | Tim's "presence is something a room dispenses"; the River's "did not fail to show up", "Recognised, not granted … structural fact", "not safe … not non-threatening", 1873 → 20 March 2017, 144 years | VERIFIED | All verbatim on `N1 whanganui_river` (lines 15–17) and N1/003. The source italicises *Recognised, not granted*. |
| §3.1-4 | Scheherazade N1: "dust on her sandals", "I have no witness to bring but myself.", "tell." | VERIFIED (minor) | In the source the sentence continues with a comma ("…but myself, and no claim the law receives…"). |
| §3.1-5 | N3 River "colony's grammar / descendants' grammar"; N3/001 "reached for chain", "kitchen table" | VERIFIED | Minor: "The room's verb was grant…" is N3/001's **headline**, not its opening. |
| §3.1-6 | Closing show t56; labelled "Unidentified Speaker 16" after t55's host line | VERIFIED | Read. |
| §3.2 | ~45 voice/dossier lines "verbatim from the published files" | VERIFIED except the 4 rows below | Scripted check against flattened published JSON (italics/quote marks normalised). |
| §3.2-a | Octopus N1: the criteria each *"presuppose an architecture"* | **WRONG** (attribution) | Not on `N1 octopus`. The phrase is the editor's, in N1/002 ("each criterion presupposes an architecture"). The voice says each criterion presupposes a specific thing ("time as a continuous line…", "a unified inward voice"). |
| §3.2-b | Scheherazade N2: *"and what they could not fit they let stand as a hole in the cloth…"* | **WRONG** (silent elision) | The page reads "…what they could not fit they **guessed at, and what they could not guess** they let stand as a hole in the cloth." The quoted form is the editor's compression in N2/005. The second half ("the holes were where Hind had been…") is VERIFIED. |
| §3.2-c | Dostoevsky N3 "names three speakers (Amy Elizabeth Fox, Indy Johar…)"; "Of Johar:" | DOUBTFUL (minor) | The page uses first names only ("Amy's man", "Then Indy."). The full names come from N3/002 `panel_speakers`, which does name them, so privacy is fine. |
| §3.2-d | Pull-quote and position claims | DOUBTFUL (minor) | N3/001's pull quote is only "The absence of the decision is not the same thing as consent.", not the three-sentence line. "Whose mouth is moving…" is in N2/001's last **paragraph**, not its last line. |
| §3.2-e | N2 River "self-limit" as a strongest moment; "why it was held isn't recorded" | DOUBTFUL | `runs/athens_night_2/04_voice/step2_validation/whanganui_river.json` records a `hard_limits_breach`: "Tupua te Kawa supplies four diagnostic registers…" deploys the kawa "as the artifact's own diagnostic engine" against the card's rule "Never deploy Tupua te Kawa … as the load-bearing premise of your own argument." The operator decision carries no reason, but this flag is the likely one. The batch's validator-evidence report (`runtime/REVIEW_2026_09_28_validator_evidence.md:13`) reaches the same reading. |
| §3.2-f | Octopus N2 `selected_form` note; Dostoevsky N3 form note | VERIFIED | Verbatim. |
| §3.3 | EDITORIAL_ASSESSMENT quotes and line numbers; N3/001 ~3,500 chars | VERIFIED | Lines 14–16, 30, 32–34, 73, 76–78, 80, 83. N3/001 body is 3,466 characters. |
| §4.1 | Pipeline in plain language; ~36-field card; "~100 operator interventions" | PLAUSIBLE / VERIFIED | Roadmap quote present. The "38–44K tokens" figure is sourced to the brief, not measured. |
| §4.2 | Decisions-table quotes | VERIFIED (sample) | Briefing 67, 83, 140, 156, 160; voices §24 "Convention signals construction"; STATE 173. "Deliberate friction" is at Briefing line 136, not in the cited 117–140 range. |
| §4.3 | Speaker-ID malformed JSON; `max_tokens=4096` root cause; N3/002 "Unidentified Speaker…"; 40K→64K; wifi; C50; C53 (99 fields / 49 files) | VERIFIED | STATE 57, 61, 86–89; roadmap text; N3/002 `panel_speakers` lists 7 unidentified speakers; C53 line 2937. |
| §4.3 | "Five sessions were captured in two parts" | **WRONG** | Six: Night 1's Act One is also split (`…the_story_of_us_2000__audio2`; DATA_INVENTORY line 46), plus 3 on Night 2 and 2 on Night 3. DATA_INVENTORY line 103 has the same undercount; the deliverable inherited it. |
| §4.4 | Marley critique 2026-05-04; the trade; River opener fix; validator treadmill | VERIFIED | voices §24 (line 894) and §28 quotes present. |
| §5.1 | "$72 lands inside the estimate" | VERIFIED | Voice spec:1282. |
| §5.2 | Validator "noise, not a gate"; "caught none of the problems the operator fixed by hand" | DOUBTFUL / partly WRONG | 23/30 flagged and 22 released is VERIFIED. But the one hold (N2 River) followed a real card-breach flag (row §3.2-e), so "caught none" is contradicted at least once. The PLAUSIBLE hedge covers only the Night-1 reruns. |
| §5.2 | C55 Munich frame; C61 "both leave unmet"; C68 blank reflection metadata | VERIFIED | Tracker lines 2944–2946, 3251; untouched-code review A1. |
| §5.3 | Phase-0 review "merge after the listed fixes", 0 blockers, 5 minor; untouched: 1 blocker, 4 major; 41 steps | VERIFIED | Review headers and counts; CHANGELOG@40fe490:22. |
| §5.4 | 0/2 opt-in; 19,117 thinking tokens; pre-conference edition quotes; `5321f08` | VERIFIED | Roadmap line 116; dossier metadata; `_archive/dryruns_2026_05_06/dossiers/night_1/dossier_001/003`; code-repo commit exists. |
| §6.1 | §33 quotes; hub ≥80% bar; FU#49G; Quarch/Tsinorema/Erinakis at N2/002 | VERIFIED | voices OPEN_ITEMS lines 1329–1332, 345; hub; N2/002 `panel_speakers` names all three. |
| §6.2 | D1/D2 and reviewer quotes; EDITORIAL lines 31, 92–97; N3 Marley speaks "as I-and-I/me throughout" | VERIFIED except "throughout" | "I-and-I" appears once on `N3 bob_marley` ("me" 5×, "I" 7×). First person holds, but "throughout" overstates the I-and-I use. |
| §6.3 | "In print, the voice holds that line itself" (N2 River) | DOUBTFUL | The quoted self-limits are verbatim, but the same page is the one flagged for breaching the kawa hard limit and held (row §3.2-e). Citing it as the stance holding in print needs that caveat. |
| §6.6-1 | Rule: the operator's name "does not appear in any publishable surface text" (STATE:134, C47) | VERIFIED | STATE@40fe490:134. The run file `runs/athens_night_1/_dossier_deployment_context.md:11` lists the scope: "kicker, headline, subline, front_abstract, body_paragraphs, **headnotes**, theme_title, theme_abstract, pull_quote." |
| §6.6-2 | Dossier prose obeys it | VERIFIED | No hit in any rule-scoped text field *except headnotes* (below). The body uses "channelled into the room" in N1/001, /003, /004. |
| §6.6-3 | The name is in `panel_speakers` of N1/001, N1/003, N1/004 | VERIFIED | `panel_speakers[8]`, `[1]`, `[0]` respectively. |
| §6.6-4 | Scope of the leak | **INCOMPLETE** | Also: (a) `headnotes[].formulation_text` in N1/001 (headnotes 0–3), N1/003 (0–1) and N1/004 (0): 7 headnotes, full name, inside the rule's scope; (b) top-level published `thinking_trace` in N1/001, N1/003, N1/004, N2/001 and N3/002 (first name or surname); (c) `themes/night_1/theme_002` `extractions[15].speaker`, `theme_004` `extractions[3,4,6].speaker` + `[5,7].context`, `theme_007` `extractions[1].speaker` + `formulations_per_voice[0].formulation_text`; (d) data_views: 187 full-name occurrences in both files, mostly transcript speaker labels (88 turns in the More-than-Human session), formulations, voice Step-1 text, headnotes, and the rule text itself. Nothing in `nights/`, `_index.json`, DATA_INVENTORY, EDITORIAL_ASSESSMENT or `_archive`. |
| §6.6-5 | "then propagates to" themes and data_views | DOUBTFUL (direction) | The name starts upstream, in the speaker-ID roster, then flows to extractions, themes and formulations. `panel_speakers` (C38 joins `speakers.json`) and headnotes are both downstream copies. Clearing `panel_speakers` alone leaves the rest. |
| §6.6-6 | "not in any tracker" | VERIFIED, now partly STALE | Still absent from both OPEN_ITEMS, the doc backlog and the roadmap. Since 2026-09-29 it is listed in `runtime/HANDOFF_2026_09_28.md:60` (commit `43f2d0c`) as "urgent, not yet filed", with the same narrow panel_speakers scope. |
| §7 | Hub and roadmap quotes (HuggingFace analogy, attestations, §11.5 invariant, line 142 discipline, line 242) | VERIFIED | Hub lines 17, 27, 39, 188–197; roadmap@40fe490 lines 142, 242. |
| §8 Q3 | "Why the River was held … no reason recorded" | DOUBTFUL | See row §3.2-e. The operator can confirm, but the likely reason is already on disk. |
| §9 | Offline, read-only, no model calls; nothing committed | PLAUSIBLE | Nothing contradicts it. The file was committed later by the operator session (`0910a66`). |

**Privacy check**

- **No private individual is named.** The co-architect goes unnamed, even though Briefing line 31 and More-than-Human t378 give his first name. So do the Marley reader and the reader-gate candidates.
- **Programme speakers are named only as the published dossiers name them:**
  - Chandler: N2/003;
  - Fox and Johar: N3/002;
  - Quarch, Tsinorema and Erinakis: N2/002.
- **Public figures:**
  - Tang and Thiel appear only as Briefing casting.
  - Tim Leberecht, as the editor persona, is a public figure. He isn't named in any dossier or voice page, only in STATE and data_views.
- **The deliverable itself carries the operator's name 4 times:**
  - §3.1: the first name, inside the t55 host quote;
  - §6.6: the full name twice, quoting the rule and stating the leak;
  - §9 item 7: the full name once, in the grep description.

  This doesn't breach the brief: the operator is the reader, and the name is already in STATE.md. But it matters for a dossier meant to be excerpted: these lines need redacting before any sharing.

## Problems with the document

1. **The quote dump missed editor paraphrase.** Two lines attributed to voice pages are the editor's wording (§3.2-a, §3.2-b). Both were most likely lifted from dossier text. The operator will quote from this, so every voice-attributed line should be re-checked against `nights/*/<slug>.json` `artifact.text`, not dossier bodies.
2. **Calculation error propagates.** The Provocateur uses the 1h-TTL multiplier the Voice spec states for *voice* calls, and the Provocateur doesn't use that TTL. The error flows into §0.3, §2.3 and the "~$130" sentence. The "Calculation" label is honest; the multiplier is not.
3. **Unlabelled evaluative claims.** The legend promises CONFIRMED / PLAUSIBLE / Inference / Calculation, but many judgments carry none of those labels:
   - §0.3 "It was cheap."
   - §0.4 "The collective moment happened in the editor's dossiers instead."
   - §3.1 "the best single story" and "the one piece of evidence for … enters the conversation".
   - The §3.2 "Why:" lines, especially:
     - Plato: *"a move the corpus doesn't contain but supports"*. This is a factual claim about the corpus, unchecked.
     - Lovelace: *"a well-read essayist would not make in these terms. It is the Layer 2 claim at its strongest."* This asserts a Layer-2 pass, which §6.1 and §33 say is unestablished.
     - Marley: *"self-criticism from inside the tradition"*. This gives in-tradition standing to a non-Rastafari construction, the exact move §24/§33 caution against. The doc flags the appropriation question in the next line, but the framing itself is unlabelled.
   - §3.2 Octopus "evidence that continuity worked as self-editing".
   - §5.1 "The new stance worked".
   - §5.2 "noise, not a gate".
4. **Internal tension on the River.** §3.2 and §6.3 use the held Night-2 page as evidence that the voice holds its line. §5.2 says the validator caught nothing real. The validator's Night-2 River flag contradicts all three. The batch's own Task-2 report (validator evidence) found this, and the deliverable could have cross-checked it.
5. **§6.6 scope** is too narrow (above). It also frames the data_views as a propagation target when they are the full making-of record by design (README: "every field preserved"). Whether data_views and `themes/` are a "publishable surface" is an open question the doc doesn't raise.
6. **Minor stale or inherited items:**
   - dossier word count (e4c4e39);
   - the split-session undercount (inherited from DATA_INVENTORY);
   - STATE line numbers are now +1 after `730ac24`/`d5c313d`.
7. **Brief compliance and rules.** Stayed within the brief: gathered, didn't draft. The "Defensible sentence" and "A thread for the essay" lines edge toward drafting but are labelled. Every section carries sources. No sign of edits, commits or model calls.

## Questions for the originating session

1. **Did your §9 name grep hit `headnotes[].formulation_text` and `thinking_trace`, and why does §6.6 report only `panel_speakers`?**
   - *Why it matters:* the handoff's urgent item copies your scope, and `headnotes` is in the rule's own listed scope.
   - *What changes:* if you saw them and judged them non-surface, the repair scope stays narrow and that reasoning needs recording. If you missed them, the filed item must cover 7 headnotes and 5 traces.
2. **Do you treat `data_views/` and `themes/` as publishable surfaces?**
   - *Why it matters:* data_views embed full transcripts where the operator is a named speaker, and the rule text itself.
   - *What changes:* if they are internal, the repair is dossier-JSON only. If they are public, it becomes a build-time redaction in `build_athens_data_graph.py` plus roster tagging at speaker ID.
3. **Which cache-write multiplier did you intend for the Provocateur, and did you check its TTL?**
   - *What changes:* at 1.25× the total is ~$34 and the event total ~$116. The cost paragraph and any published number change.
4. **Did you read `runs/athens_night_2/04_voice/step2_validation/whanganui_river.json`?**
   - *What changes:* if its `hard_limits_breach` (kawa as the voice's own diagnostic) is the hold reason, §3.2's "self-limit" entry, §6.3's "holds that line itself", §5.2's "caught none", and §8 Q3 all need rewriting. The Night-2 River becomes an example of the gate working.
5. **For §3.2, was the source the voice-page `artifact.text` or the dossier bodies/headnotes?**
   - *What changes:* if any lines came from dossier text, all voice-attributed quotes need a second pass before the operator quotes them. Two are already misattributed.

## Operator decisions it asks for

| Decision / question | Document's recommendation |
|---|---|
| File the `panel_speakers` anonymization leak as a record-repair item (§6.6) | File it; the document made no edits. Reviewer: widen the scope first (row §6.6-4). |
| Whether the essay says the anonymization held | Don't claim it held without the repair. |
| Arendt "provotype" quote at Act One (§1.4) | Check it against your own copy before quoting. |
| Validator counts: STATE 4/6/0 vs spec 3/6/1 for Night 1 (§2.2) | Prefer the spec. |
| Step-1 count for Night 1: 46 vs 43 (§2.2) | Use 43. |
| §8's eight questions only the operator can answer (microsite hosting and traffic; how attendees met the output; why the River was held on Night 2; whether the three Greek scholars read Plato; whether E1 was used; the original Arendt artifact; the Octopus shader shown live; feedback from named panellists) | No recommendation; open questions. Reviewer: Q3 likely has a partial answer on disk (row §3.2-e). |
| Naming the other people named in the internal record (co-architect, Marley reader, reader-gate candidates) | Leave unnamed unless they agree. |
