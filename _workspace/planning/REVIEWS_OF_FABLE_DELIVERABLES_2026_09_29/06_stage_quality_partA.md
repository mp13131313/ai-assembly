# Review of `_workspace/planning/runtime/REVIEW_2026_09_28_stage_output_quality.md` (Part A, Researcher)

Reviewer: read-only. I made no API calls and ran no pipeline scripts. My offline Python scripts read JSON from `athens-2026/runs/athens_night_{1,2,3}/`, `current-tests/dev_msc_test/`, the prompts, the specs and git. They are in `scratchpad/rr/partA/`.

## Verdict

1. **Overall quality:** strong on the grouping layer. Almost every count reproduces exactly: the A.1 table, 0 challenged in N1 theme_005 and in Clash, the triage flags, the dropped themes, the shared-blind-spot count, the dominant-session share. The reading also holds: themes are inventories, the edge is recovered per voice at Formulation, and it never reaches the record. The document is weak on causation and on its own illustrations.
2. **How far to trust it:** trust the counts and the diagnosis of the record and the triage. Do not trust the MSC-versus-Athens causal story, the grammar statistics as evidence that Athens is worse, or Illustrations 1–3 as examples of what a correct "room reading" would say.
3. **Biggest issue:** the central causal claim, "the method mirrors the room", rests on a false premise and on one kind of material.
   - The premise: "the same model" ran both. In fact MSC v2.4 ran on Opus 4.6 and Athens on the 4.7 default.
   - The material: the headline "room" examples come mostly from vendor reflection takeaways. These reached the Researcher labelled as a panel (runtime C68 A1), so "unchallenged" and "the room moved on" are artifacts of that format.
   - The document's own prototype room readings contain two factual errors about the room. The "checkable by script" safeguard it proposes would not catch them.

## Findings, one by one

| ID | Claim (short) | Verdict | Evidence / reason |
|---|---|---|---|
| H1 | Ran on `3b185f2`; the two later commits touch no Researcher prompt or spec | VERIFIED | `git log 3b185f2..HEAD` over the Researcher prompts, spec, `researcher_flow.py`, `provocateur_flow.py` and `build_athens_data_graph.py` shows no change. The only later commit touching the deliverable is its own save (`0910a66`). |
| H2 | "Uncommitted" | STALE | The main session committed it in `0910a66`. That is not a breach by the Fable session. |
| H3 | No API calls; `athens-2026` only read | PLAUSIBLE | Nothing contradicts it. The scripts (`textstats.py` etc.) stayed in the Fable scratchpad and cannot be inspected. |
| M1 | Prompts are byte-identical to the spec except two closure sentences | VERIFIED (near) | A difflib comparison against the prompts embedded in the spec differs only in closure and id-assignment sentences, plus one extra BAD example in `researcher_theming.md`. |
| M2 | Prompts unchanged since 2026-04-16, so Athens ran v2.4 | VERIFIED | Only `bd3e27d` (the subtree add) touches them; the pre-subtree history is `51941a5` (2026-04-15). The MSC v2.4 run is dated 2026-04-14 in the manifest, before any commit, so "same text as MSC" is only PLAUSIBLE. |
| S1 / A.2.3 | 86/86 cluster abstracts take "the items" as subject | VERIFIED, not diagnostic | 80 open with "Items" / "All" / "<N> items"; 4 open with "Arc…" and 2 with "Practical/Prescriptive moves…". **MSC does the same: 25/25 open "These / Both / All / Each items…".** This is the prompt's house style, not an Athens symptom. |
| S2 / A.2.3 | 74/86 are em-dash lists | DOUBTFUL | 74 contain an em-dash, but about 17 of them use it for a qualifier or aside, not a list (N1 cluster_002, _004, _016; N2 cluster_002, _015; N3 cluster_007…). About 57 are lists. MSC has an em-dash in 21 of 25. |
| S3 / A.2.3 | 24/24 theme abstracts cite cluster ids | VERIFIED, not diagnostic | MSC does too (6/6). The theming prompt recommends inline ids. |
| S4 | The v2.4 clustering prompt bans "declarative findings" | VERIFIED | `researcher_clustering.md` BAD examples. The same line calls findings "the theme-level move", and the theming prompt's first GOOD example is a finding: "cluster_001 and cluster_004 together reveal that…". |
| S5 | The flatness is "designed, not accidental" | DOUBTFUL | True at cluster level. At theme level the prompt invites findings. Several Athens cluster abstracts also copy the clustering prompt's own BAD "topic metadata" form ("Items arguing that…"): N1 cluster_001, _025 and _030 all begin "Items articulating that…". Part of the flatness is non-compliance, possibly linked to the model change (A4.6). |
| S6 / A.4 #3 | The clustering call is never shown who disagreed | VERIFIED | `researcher_flow.py:383-385` sends only `ref`, `extraction` and `context`. |
| A1.1 | The A.1 table | VERIFIED | My recount reproduces every Athens cell and the MSC figures (106 extractions, 34 challenged, 25 clusters, 21 single-session, 6 themes). One slip: MSC has 4 isolates, shown as "—". |
| A1.2 | 7% challenged on audio panels, 4% on reflections | VERIFIED | The 5 vendor sessions hold 103 extractions with 4 challenged (3.9%). Audio: 28 of 426 (6.6%). |
| A1.3 | `hdid_audio:011` quote and "the room did not interrogate this" | VERIFIED | |
| A2.1 | N1 theme_005: 28 extractions, 6 sessions, 0 challenged | VERIFIED | `grouping.json` plus an engagement recount. |
| A2.2 | "Twenty-eight positions and not one contested: that is the finding" | DOUBTFUL | **24 of the 28 come from vendor reflection takeaways** (birthplace 16, nightwalk 6, hdid_refl 2). `metadata._reflection_source` is `takeaway_export`: separate summarised takeaways. They reached the Researcher with format "panel" (C68 A1). "Challenged" can hardly occur in that material. At Night 1's 6.8% base rate, the chance of 0 in 28 is 0.14 anyway. |
| A2.3 | Clash: 30 extractions, 0 challenged; nobody defended the cuts; `clash:002` context | VERIFIED | 22 + 8 extractions, all reinforced, unengaged or open questions. No extraction argues for the layoffs. |
| A2.4 | 15 abstracts open with "All…" | VERIFIED | |
| A2.5 | N3 cluster_002 "misstates" the room; "the room was near-unanimous" | DOUBTFUL | The quotes are correct (`beastopia:005`, `citizen:013`, `citizen:004`). But the cluster pools three sessions. The 4–5 scores describe the Citizen Assembly room, reported second-hand at Beastopia. `citizen:015` is a group that started at "3+". 10 of the 25 items come from the MPGA reflections, including `mpga:013`, which defends representative democracy and prefers subsidiarity to sortition, and `mpga:014`. "Across the 1–5 spectrum" is loose; "misstates" overstates. |
| A2.6 | 17 abstracts have a trailing qualifier | PLAUSIBLE | My regex finds 14. These overlap the non-list dashes in S2, so the two counts partly double-count. |
| A2.7 | Only 5 theme abstracts contain a claim verb ("reveal", "argue that", "show that") | DOUBTFUL | I could not reproduce it: "reveal" appears in 0 Athens theme abstracts, and the argu*/show* stems hit 8. |
| A2.8 | The quoted titles | VERIFIED | |
| A2.9 | 0 of 86 clusters use the "shared blind spot" binding | VERIFIED | The prompt names this binding. All 5 regex hits are content words (N1 cluster_009, _034; N2 cluster_029; N3 cluster_009, _012). |
| A2.10 | `mpga:025` and `hdid_audio:010` quotes | VERIFIED | Minor misquote: `:010` says "neither was tested…", not "never tested…". |
| A2.11 | 55 of 86 single-session clusters; N2 dominant-session share 94%; MSC 21 of 25 | VERIFIED | Mean dominant share: N1 0.81, N2 0.936, N3 0.90. |
| A2.12 | `mthd:007` is high energy, reinforced, and the most-cited item of Night 1 | VERIFIED | Top in `selected_quotes` (9). In grounding ids it is tied at 9 with `mthd:021`. |
| A2.13 | `beastopia:006` is an isolate; the explorer stores isolates but draws none | VERIFIED | Night-3 `grouping.json` isolates; `build_athens_data_graph.py:199-201`. No code in `view_by_theme.html` reads `*_isolates`. |
| A2.14 | `beastopia:006` is "the one piece of Layer-3 evidence (G6)" | WRONG | The speaker is the operator: the transcript labels him "Unidentified Speaker 16 [low]" and he is introduced as "Matthias". He is recounting the **Night-1** game show, which is already captured as `mthd:007`. G6 requires *attendees* to reference artifacts. His own words were that it "shifted the conversation a little bit"; "visibly shifted the room" is the Researcher's gloss. |
| A2.15 | No other audience reference to the Assembly in the N2/N3 transcripts | VERIFIED | My own search for "AI Assembly", "octopus", "artifact" and "the assembly" over the N2/N3 `session_package.json` files finds only this turn. |
| A2.16 | The grouping layer produced "zero findings of its own" across 24 themes | DOUBTFUL | N3 theme_004 claims clusters 012 and 013 "are two vocabularies for the same practice", which settles a question the speakers left open in cluster_013. Also N1 theme_011 ("does not directly converse…") and N3 theme_005 ("more ready than the discourse admits"). There are few such findings, not none. |
| A3.1 | Illustration 1 (theme_005: "none was challenged", `hdid_refl:003` "drew no response") | DOUBTFUL | See A2.2. For a separately recorded takeaway, "drew no response" is guaranteed by the format. |
| A3.2 | Illustration 2: "sortition versus election, which the room settled" | DOUBTFUL | Contradicts `mpga:025`, which the document itself quotes in A.2.4 ("both diagnoses but no engagement between proponents"), and `mpga:013`. |
| A3.3 | Illustration 3: the octopus explanation — "nobody took it up or answered it" | WRONG | `mthd:007` is `engagement: reinforced`, `energy: high`, as A.2.6 itself says. The operator's account: "people appreciated it". Only the principle question (`mthd:021`) was "never resolved". |
| A3.4 | Half of cluster_008's 8 items are the Assembly speaking, or about the Assembly | VERIFIED | `mthd:007`, `mthd:020`, `act_one:015`, `act_one:021`. |
| A3.5 | The Provocateur independently wrote this finding (Plato, Marley quotes) | VERIFIED | All quotes found. But the groundings are reflection items: 6 of 7 (Plato), 3 of 5 (Marley theme_005), 5 of 6 (Marley theme_006). |
| A4.1 | Neutrality was intended (Briefing, Researcher spec l.52 and l.321, Provocateur spec l.49, DATA_INVENTORY) | VERIFIED | Every quote found. |
| A4.2 | Spec l.190, the prompt's BAD examples, and changelog §G ("replacing the v2.2 'declarative finding' framing") | VERIFIED | The dev_msc_test manifest calls the prior framing v2.3; the spec says v2.2. |
| A4.3 | The theme prompt allows findings and rewards inline ids; KJ labels are sentences | VERIFIED (prompt) / PLAUSIBLE (KJ) | |
| A4.4 | Round 2 sees only Round 1 abstracts | VERIFIED | `researcher_flow.py:494-501`. |
| A4.5 | `birthplace:006`, `:007` and `:008` all respond to `:005` and are "reinforced" | WRONG (detail) | `:008` is `unengaged`. The concern itself is confirmed by C68 A1: the reflections were fed in with format "panel" and a blank title. |
| A4.6 | "The same prompts … and the same model (`claude-opus-4-7` … per `model_routing.json`)" ran MSC and Athens | WRONG | `dev_msc_test/_manifest.json`: v2.4 ran on "claude-opus-4-6 with thinking.type=adaptive". The code default switched to 4.7 in `37e883b` (2026-04-17). `model_routing.json` was created in `6a5a828` (2026-09-28), so it cannot document either run. The output also drifted: MSC wrote the lens as `open_question`, Athens as `open question`. |
| A4.7 | "The method mirrors the room" (inference, "strongly supported") | DOUBTFUL | Confounded three ways: the model changed, 19% of Athens extractions are reflection takeaways, and the control is a single run of three MSC panels. The MSC manifest itself describes v2.4 Opus themes as "taxonomic … without taking sides". At most PLAUSIBLE. |
| A4.8 | No prompt looks for references to the Assembly | VERIFIED | |
| A5.1 | worth_surfacing 24/24, fault_line_present 22/24, audience_friction high 17/24 | VERIFIED | `triage_flags.json`, all three nights (model `claude-opus-4-7`). |
| A5.2 | All 22 fault lines start "Whether…"; 21 are "A, B or C" menus restating the clusters | WRONG (count) | All 22 start "Whether" (VERIFIED). But only 12 of 22 offer three or more options; 10 are binary. Several map the divide onto council traditions, which is what the prompt asks for: `provocateur_triage_flags.md` defines FAULT_LINE as "where the council's traditions would visibly diverge", not as dispute in the room. |
| A5.3 | The multipliers are "symbolic … numerically load-bearing" | VERIFIED | Provocateur spec l.267. |
| A5.4 | Dropped below quorum: N1 theme_008 (5 of 14 challenged), N2 theme_006 (3 of 13), N2 theme_004 | VERIFIED | `selection.json`. Many Clash items still reached voices via N2 theme_002 (cluster_019). |
| A5.5 | 23 of 128 formulation-plus-narrative texts hit the "room gap" regex | PLAUSIBLE | 128 = 46 + 46 + 36 (VERIFIED). My narrower regex finds 16. |
| A5.6 | Formulation and narrative quotes; Plato's Step 1 "torch" quote | VERIFIED | `04_voice/step1_detailed_responses/plato__theme_005.json`. |
| A5.7 | N1 theme_004: 8 of 9 formulations open with the octopus reframing; Cleopatra's does not | VERIFIED | |
| A5.8 | `theme_abstract_from_researcher` reaches every voice | VERIFIED | `provocateur_flow.py:1386`. |
| A5.9 | Lens stored as `"open question"`, while `LENS_ORDER` expects `open_question`; still sorts last by fallback | VERIFIED | `.get(…, 99)` at `provocateur_flow.py:1169/1324`. MSC data used the underscore. |
| A6.1 | Option 1: `contested_by` is "nearly deterministic" from engagement plus `responds_to` | PLAUSIBLE | `responds_to` carries no polarity and links only within a session. |
| A6.2 | Option 4 errors are "checkable by script: every cited id must exist and support the statement", like `_validate_clusters` | DOUBTFUL | `_validate_clusters` (`researcher_flow.py:581`) checks only closure and uniqueness. "Supports" needs an LLM or human judge. A3.2 and A3.3 would pass an existence check. |
| A6.3 | Option 4 routing: "fault lines come from `open`" | DOUBTFUL | This silently turns a council-divergence signal into a room-contestedness signal (see A5.2). Room contestedness needs its own flag. |
| A6.4 | One extra Opus call, small next to the spec's ~$15–25 per night | PLAUSIBLE | The spec estimate (l.638) is for a 6-session night; Athens nights had 9–12 sessions. |
| A6.5 | A deterministic Assembly-reference flag would have kept `beastopia:006` alive | PLAUSIBLE | True, but it catches little: the only hit is the operator's own report. A regex on voice names also matches content (Plato, Arendt and Cleopatra appear as topics, e.g. N1 cluster_018). |
| A6.6 | Roadmap fit: Phase 2 "stage routing as function of input shape"; the 2026-09-28 gate amendment | VERIFIED | Roadmap l.142, l.149. |

Tally: 35 VERIFIED, 6 PLAUSIBLE, 11 DOUBTFUL, 1 STALE, 5 WRONG.

## Problems with the document

- **Internal contradictions.**
  - A.2.6 records `mthd:007` as reinforced and high energy, but Illustration 3 says nobody took it up.
  - A.2.4 cites `mpga:025` (no engagement between the election-reform and sortition camps), but Illustration 2 says the room "settled" sortition versus election.
  - A.1 argues the low challenge rate "is not an artifact of the reflection format". A.4 #5 then concedes that engagement labels on reflections are inferred. The document never reconciles the two, and its headline example (theme_005) is 86% reflections.
- **Missing control.** The grammar statistics (S1–S3) were not run on MSC. MSC has the same house style: items as subject, em-dashes, inline cluster ids. What separates the two runs is content, such as MSC's synthesis clauses ("together revealing that…"), not grammar.
- **Missing evidence for the causal claim.** The document asserts "the same model" without checking which model each run used, and cites a config file dated after both runs (A4.6). The counting regexes stayed in the scratchpad, so "5 claim verbs" and "23 of 128" cannot be reproduced.
- **Missed design facts.**
  - The extraction prompt says: "Do not extract observations about group dynamics, tone, or process as findings." That is the most direct prompt-level ban on what a room reading does, and a room reading would reverse it. The document never cites it.
  - Some flat cluster abstracts copy the clustering prompt's own BAD topic-metadata form, so they are non-compliance rather than design (S5).
  - Fault-line flags are meant to measure council divergence, not the room's disagreement (A5.2).
- **Context the session probably lacked.** C68 A1 (filed the same day) records that all 103 reflection extractions reached the Researcher with a blank title and format "panel". This confirms the document's own suspicion in A.4 #5 and undermines A2.2, A3.1 and A3.5. It is also a precondition for any room reading.
- **Overreach.**
  - It treats `beastopia:006` as G6 attendee evidence (A2.14).
  - It calls its causal inference "strongly supported" (A4.7).
  - It claims "zero findings" at theme level (A2.16).
- **Rules and brief.**
  - No sign of API calls or writes to `athens-2026`.
  - It stayed within Part A and stopped at the checkpoint, as the brief asked.
  - It labels claims CONFIRMED or PLAUSIBLE as asked. Some CONFIRMED labels cover counts that depend on regexes nobody else can see.

### Is the "room reading" proposal well founded?

**Partly.**

The need is demonstrated:
- the record shows no findings;
- the triage flags do not discriminate (24/24, 22/24);
- the edge is re-derived nine times per theme at Formulation and lost with dropped themes.

The shape is sound:
- additive, with `grouping.json` left untouched;
- routed to the record and triage first, not to the voices;
- evidence ids on every statement;
- claims about the room, never about the question.

The foundation is weak in three ways:

1. **Accuracy is the real risk, not only plurality.** The document's three prototype room readings contain one WRONG and two DOUBTFUL claims about the room, and a check that cited ids exist would pass all three. A trial needs a support check: an LLM judge or a human pass.
2. **There are preconditions.**
   - Session format must reach the Researcher: fix C68 A1.
   - Any room reading must know what kind of "room" each session was: reflection takeaways, a staged board meeting with a scripted pitch, a scored workshop reported second-hand, or an operator channelling the Assembly.
   - The extraction prompt's ban on group-dynamics observations needs an explicit operator decision.
3. **Cheaper steps were not weighed.**
   - (a) Deterministic per-theme room statistics in the explorer, at no LLM cost and with no hallucination risk: challenged, unengaged and high-energy counts; the Researcher's synthesized open questions; isolates. This alone answers part of the operator's complaint about the record.
   - (b) Theme-level compliance: the theming prompt already invites "together reveal that…" findings, and Athens under the 4.7 default mostly did not deliver them.

   Either should be tried or ruled out before adding a Round 3 call under the net-complexity gate.

## Questions for the originating session

1. **Which model and thinking setting did the Athens Researcher run with, and did you check that MSC v2.4 ran on Opus 4.6?**
   - Why it matters: A.4 #6 is the "central causal point".
   - What changes: if the model differs (as the manifest and `37e883b` indicate), the MSC contrast cannot separate "hospitable room" from "model drift". The proposal should then first test theme-prompt compliance, which is cheap, before adding Round 3.
2. **Did you count reflection-sourced items in your headline examples, and did you know of C68 A1 (reflections fed in as format "panel")?**
   - Why it matters: 24 of theme_005's 28 items, and most groundings of the Plato and Marley "moved on" formulations, are takeaways.
   - What changes: if Illustration 1 cannot be rebuilt from audio sessions alone, drop "0 challenged" as a finding and make any room reading format-aware.
3. **Illustration 3 says nobody took up the octopus explanation, yet `mthd:007` is labelled reinforced and high energy. What was the source?**
   - Why it matters: it is the prototype output of the proposal, and it contradicts the Researcher's own label.
   - What changes: an answer of "the Researcher's labels are unreliable" and an answer of "my illustration is wrong" lead to different trial designs (a label audit, or a support judge).
4. **Did you run `textstats.py` on MSC, and what exact regexes produced 74, 17 and 5?**
   - Why it matters: if MSC scores the same (my recount: 25/25 items-as-subject, 21/25 em-dash, 6/6 inline ids), the grammar section describes house style, not Athens flatness.
   - What changes: the argument would have to rest on content instead.
5. **Did you intend Option 4 to change what `fault_line_present` means (council divergence, per `provocateur_triage_flags.md`), or to add a separate room-contestedness signal?**
   - Why it matters: this decides whether Triage Part B's prompt contract changes, or whether a new flag and multiplier is added.

## Operator decisions it asks for

1. **Confirm or correct the Part A reading** before Part B starts (the checkpoint). No recommendation beyond asking.
2. **Build Option 4, a separate per-theme and per-night "room reading" (`room_reading.json`),** with evidence ids, routed to the explorer and Triage Part B first and **not** to the voices. Recommended.
3. **Add the deterministic Assembly-reference flag,** which exempts matching items from isolate-dropping. Recommended.
4. **Keep Option 1's `contested_by` as a field filled in Python,** if cheap. Recommended.
5. **Option 2 (cluster by fault line):** decline as the primary change. Option 3 (propositional theme titles) only if Option 4 is declined.
6. **Build now or design-and-shelve** under the net-complexity gate (the operator's own decision now counts). No firm recommendation; the document defers this to Part B's synthesis.
7. **Allow a capped API trial of Round 3 on Athens Night 1,** scored against the 128 context narratives and Illustrations 1–3. Recommended. Given this review, it also needs a support check and a fix for C68 A1 first.
8. **Side fix:** make the lens spelling (`open question` vs `open_question`) consistent in the spec or prompt, a one-line change. Recommended as not a finding.
