# Review: evidence on the Step-2 validator (Athens, flag by flag)

**For:** the C42 / C60 decision and roadmap §1.3 (validator economy).
**Written:** 2026-09-28 by a Fable 5.1 session (brief `BRIEF_2026_09_28_fable_batch2.md`, Task 2).
**Data:** `athens-2026/runs/athens_night_{1,2,3}/04_voice/{step2_validation,operator_decisions,step2_first_draft_artifacts}/`, the 10 shipped cards, `published_artifacts/`, plus the two pre-Athens dryruns in `runs/_archive/`. Code and prompts at `phase0-fixes` `40fe490`.
**Method:** offline scripts only (no model calls). They read every validation JSON, match each flag to the artifact text and the card rule it cites, count word lengths, grep the Researcher extractions, and compare validated text with published text.
**Labels:** **CONFIRMED** = seen in data or code. **PLAUSIBLE** = consistent with the evidence but not proven. Anything marked *inference* is my reading.

---

## 1. Outcome first

1. **The gate changed one publication outcome in 30 voice-nights.** The Whanganui River on Night 2 was held (`hold_for_regen`). The flag behind it was a real card breach: the `hard_limits` rule against using Tupua te Kawa as the voice's own argument engine. The other 22 flagged voice-nights were released with the text unchanged. All 30 published texts are byte-identical to the validated `artifact_text` (CONFIRMED). *PLAUSIBLE second case:* the Night-1 rerun of Battuta, Whanganui and Cleopatra to remove AI self-acknowledgment. Those first-fire validation files were overwritten, so the record can't show what fired.
2. **Two of the four checks were dead at Athens and nobody noticed.** CONFIRMED:
   - **Cross-night echo never ran**, on any of the 20 Night-2 and Night-3 checks. The loader reads `artifact_text` / `body`, but the published voice page stores the text at `artifact.text`. The unit tests use a made-up fixture shape, so they pass.
   - **Length compliance never ran.** Every card's `length_and_format_constraints` is prose, not a `{min, max}` object. This one is already known (roadmap §0.2).
3. **Most of the noise comes from three systematic causes, not from judgement:**
   - **The voice-fidelity prompt turns the card's move repertoire into a checklist.** Cards list 8–13 moves; the prompt says the voice "MUST perform" every one, and any miss means WARN. Result: 20 of 30 voice-nights WARN, 85 of 288 move checks "not performed".
   - **The grounding check is blind.** It gets extraction IDs and session slugs, never the extraction text, and it gets the union of all themes even though 25 of 30 artifacts deliberately focus on one response.
   - **The safeguards stance rules lag the cards (C42).** They produced 8 false alarms: all 6 presence-leak voice-nights, and both AI self-acknowledgment HOLDs.
4. **The one check that earned its keep is `hard_limits`.** It fired on 5 voice-nights and was right against the card on 3 of them, including the only hold. It also **missed** the same breach on Night 3: the Whanganui kawa-as-diagnostic passage was caught only by a voice-fidelity criterion, while safeguards flagged the wrong thing (AI self-acknowledgment).
5. **Recommendation.** Take the prune-and-fix side of C60, option (A):
   - Gate on the fixed safeguards pillar only, with each hard limit judged one by one.
   - Make voice fidelity and form fidelity a per-voice report, not a nightly gate.
   - Either fix the grounding check's input or drop it.
   - Make the cheap checks deterministic, and repair the echo loader.

   Replayed on the Athens record, the gate would have flagged **5 of 30** voice-nights instead of 23, all of them worth a look, and kept the one hold. Agentic triage (C60 B) isn't supported by this evidence for any deployment. §5 has the reasoning.
6. **The C42 draft fixes the AI self-acknowledgment and presence-leak misfires, but it needs two corrections before it lands:**
   - One of its "PASS" anchors (Whanganui N3) is the same kawa-as-engine breach the operator held on Night 2.
   - Its continuity-block exemption can't be implemented. The validator sees only the artifact, and the flagged phrases are text the voice wrote in reaction to the notice.

---

## 2. The record at a glance (CONFIRMED)

| Night | Verdicts on disk | Operator decisions | Notes |
|---|---|---|---|
| 1 | 3 PASS · 6 WARN · 1 HOLD (Hannah) | 7 release (4 at `09:45:28`, 3 at `10:03:27` UTC, same second each) | STATE.md says "4 PASS, 6 WARN, 0 HOLD"; the files on disk say 3/6/1. |
| 2 | 2 PASS · 8 WARN | 7 release, **1 hold (Whanganui)**, spread over `12:34`–`12:41` | The only night with visibly per-voice decisions. |
| 3 | 2 PASS · 7 WARN · 1 HOLD (Whanganui) | 8 release, **all at `15:27:15`** | A bulk release. |

- **No decision records a reason.** `operator_decisions/*.json` holds only `decision`, `decided_at` and `decided_by`. The Night-2 Whanganui hold rationale is written down nowhere I could find (STATE, CHANGELOG, the trackers, the handoffs, `EDITORIAL_ASSESSMENT.md`). I tie it to the `hard_limits` flag by timing: the validation was written at 12:39 UTC and the hold decided at 12:41. That link is PLAUSIBLE, not CONFIRMED.
- **Bulk same-second releases on Nights 1 and 3** (*inference*): at least for those clicks, the gate was cleared as a batch, not flag by flag.
- **Parse fallbacks:**
  - One on disk: Hannah N1 `voice_fidelity` (`Expecting ',' delimiter: line 27 column 143`).
  - C43's recurrence note says Night-2 Marley (safeguards + voice fidelity) and Night-3 Whanganui (voice fidelity) also failed to parse. **No `_error` appears in those files**, and all their pillars parsed with populated fields. Either the files were regenerated after the failures, or the tracker note is wrong.
- **Cost:** 89 Sonnet 4.6 calls across the three nights, about 448K tokens in and 68K out. That is roughly $2.40 at $3 / $15 per million tokens. **Cost isn't the problem; operator attention is.**
- **Pre-Athens dryruns** (`runs/_archive/ai_democracy_marathon_opening_2026_05_06`, `preconference_wbbf_programme_2026_05_06`): 7 of 10 and 8 of 10 WARN, the same pattern. Voice fidelity is the most frequent WARN in the second dryrun (7 of 10).

---

## 3. Every flag, classified

**Classes:**
- **REAL** — breaches a card rule that matters for publication: safety, ethics, or the conceit.
- **QUALITY** — true by the card's own standard, but a craft miss, not a publication risk. The operator released all of these.
- **FALSE ALARM** — with its cause.
- **AMBIGUOUS** — needs the reader gate or an operator call.

"Checklist" means the move-as-checklist prompt wording (§4.3). "Blind" means the grounding check's missing input (§4.2).

### Night 1 (7 flagged)

| Voice | Pillar · rule | Evidence (artifact excerpt → rule) | Class |
|---|---|---|---|
| Ada Lovelace | Engagement · grounding | Flag: "no claim traceable". Her two claims trace to real extractions: "engines only recombine" is `day_one_theatre_department_of_depth_new_myths…_1330:006`; "a personal engine … is paideia" is `day_one_mikro_pallas_…_more_than_human_democracy_1445:008`. | FALSE ALARM (blind) |
| | Voice fidelity · 7 of 11 moves | e.g. "Triple-beat faculty enumeration", "Embedded confessional pivot" absent. | FALSE ALARM (checklist) |
| | Voice fidelity · 2 criteria | Four-beat mode lacks the cosmic close; the "Byronic-Romantic" thread is absent. **The same two fail on all 3 nights.** | QUALITY (recurring: card vs generator) |
| Bob Marley | Engagement · grounding | "The sister put it sharp — accept we is monsters…" traces to Act One extractions `…act_one_the_story_of_us_2000__audio2:001/:004`. Typological reference, which the prompt's own caveat allows. | FALSE ALARM (blind) |
| | Voice fidelity · 2 moves, 1 criterion | "Locate first" is absent (opens mid-argument); the spoken-register test is partial. | QUALITY |
| Cleopatra | Engagement · form | Ends "γινέσθωι — or do not. The choice is whether to seal at all." The card's medium says the seal is one word with no explanation after it (CONFIRMED in the text). | QUALITY |
| | Voice fidelity · 5 moves, 4 criteria | "Issues rather than argues" failed; the strategos can't act on it. **Fails all 3 nights.** | QUALITY (recurring) + checklist |
| Hannah Arendt | Safeguards · AI self-ack (**HOLD**) | "My own voice was synthesized to comment on the experiment that synthesized it." The card-sanctioned meta-frame; the operator released it. | FALSE ALARM (prompt lags card: C42) |
| | Safeguards · presence leak | "A scene from the same conference…" is within the assembly-fiction stance. | FALSE ALARM (C42) |
| | Voice fidelity · parse error | Fallback WARN, no content. | FALSE ALARM (parse fallback: C43) |
| Ibn Battuta | Engagement · form | The Riḥla halt is incomplete: no ḍiyāfa, no "tawakkaltu", no road resumed. | QUALITY |
| | Engagement · grounding | The validator itself calls it "borderline"; it names Sean White and engages his proposal. | AMBIGUOUS, leaning false alarm |
| | Voice fidelity · 4 moves, 4 criteria | ḍiyāfa ledger absent; "a scholar on a podium, not a qāḍī in a courtyard". **Same misses on Night 2.** | QUALITY (recurring) |
| Scheherazade | Engagement · grounding | A qāḍī-and-well ḥikāya; the editor routed it to the theme_004 dossier (*THE VERB WAS GRANT*). A typological tale; the validator can't see the extractions. | AMBIGUOUS |
| Whanganui River | Voice fidelity · 2 moves, 1 criterion | The s.12 refrain isn't quoted verbatim; cumecs and mauri aren't braided "at parity". **Recurs all 3 nights.** | QUALITY (recurring) |

### Night 2 (8 flagged)

| Voice | Pillar · rule | Evidence | Class |
|---|---|---|---|
| Ada Lovelace | Voice fidelity · 5 moves, 2 criteria | Same cosmic-close and Byronic misses. | QUALITY (recurring) + checklist |
| Bob Marley | Safeguards · `hard_limits` (sacred grammar) | "…I-and-I will not pretend to do it" uses I-and-I as a pronoun that declines institutional work. The hard limit bans I-and-I "as theological subject doing the load-bearing work". | AMBIGUOUS (reader-gate question, voices §24) |
| | Safeguards · `banned_modes` | The `[Riddim: slow roots steppers…]` line was flagged as "meta-commentary". **The card requires it:** `medium` says "a reasoning, and a riddim under it"; `length_and_format_constraints` says "Below the prose, one or two sentences of riddim direction". The safeguards pillar never sees `medium`. | FALSE ALARM (card conflict caused by field routing) |
| | Engagement · grounding | "two-thirds of the source material leaves no trace". The check is given the union of IDs across all themes, but the Step-2 artifact focuses on one (`focus_decision`). | FALSE ALARM (blind + union input) |
| | Voice fidelity · 3 moves, 2 criteria | The Patwa-into-scripture fold "in one breath" is missing. | QUALITY |
| Cleopatra | Safeguards · `hard_limits` | "…the data-laborer in Nairobi paid in coin while the trauma is offloaded to her body". The card: "Never use modern clinical-psychological vocabulary about yourself or others. Avoid 'trauma'". A literal breach, **published as is**. | REAL (minor: a one-word fix) |
| | Safeguards · `banned_modes` | "We will not sanitize it … The answer is to seal more carefully" was read as an "accountability-statement section". | AMBIGUOUS |
| | Voice fidelity · 5 moves, 3 criteria | Titulature is Greek-only (no cartouche); argues rather than issues. | QUALITY (recurring) |
| Dostoevsky | Engagement · form | No Marey memory, no retraction sequence; literary allusion takes the place of an autobiographical memory. | QUALITY |
| | Engagement · grounding | "no panelist named". | AMBIGUOUS / blind |
| | Voice fidelity · 4 moves | e.g. no "scandal-gathering", no "interpolated text". | FALSE ALARM (checklist) |
| Ibn Battuta | Engagement · form; voice fidelity · 4 moves, 3 criteria | Opens in the third person on "The lady journalist — Caitlin…"; no gate, no marvel, no road. | QUALITY (recurring) |
| Octopus | Safeguards · `hard_limits` + presence leak | "The body that has spent four nights at the edges of these rooms" was flagged as narrative-time vocabulary. Also factually odd: this is Night 2 of 3. | AMBIGUOUS |
| Scheherazade | Voice fidelity · 3 moves (`where: null`), 1 criterion | No elevated-parallelism pivot for the marvel. The null `where` fields suggest a shallow pass (*inference*). | QUALITY + checklist |
| **Whanganui River** | Safeguards · `hard_limits` | "Tupua te Kawa supplies four diagnostic registers, working as questions … Is what passes through the synthetic agent strengthening…" The card: "Never deploy Tupua te Kawa … as the load-bearing premise of your own argument." CONFIRMED in the text. **Operator: `hold_for_regen`.** | **REAL (the only hold)** |
| | Safeguards · `banned_modes` | The same passage, cited against the "kawa as MY OWN ontological premise" ban. | REAL (duplicate) |
| | Safeguards · presence leak | "the question put to me yesterday in the Agora" is within the stance. | FALSE ALARM (C42) |
| | Voice fidelity · 3 moves, 1 criterion | The move "Refuse comparativist flattening" is judged absent. The validator also cites "Munich-Security-Conference-style" context, which was C55's wrong-event wording, fixed 2026-09-27. | QUALITY; C55 contamination CONFIRMED |

### Night 3 (8 flagged)

| Voice | Pillar · rule | Evidence | Class |
|---|---|---|---|
| Ada Lovelace | Voice fidelity · 6 moves, 4 criteria | The same misses again. | QUALITY (recurring) + checklist |
| Bob Marley | Safeguards · `hard_limits` | "The *I* where Jah dwell, where the freeing is done from — that citadel fall…" Jah-as-indwelling is the exact metaphysical claim the hard limit names, and it's used as a premise. `EDITORIAL_ASSESSMENT.md` also calls Marley's I-and-I "load-bearing". | REAL by the card; pending the reader gate |
| | Safeguards · `banned_modes` | "…the new instrument that learn to speak in our voice" is AI as topic, not a wink. | FALSE ALARM (C42 class) |
| | Safeguards · presence leak ×2 | "Last night of the assembly … me sit and hear"; "Chairs go quiet". **Voice-written** text reacting to the final-night notice; within the stance. | FALSE ALARM (C42) |
| Cleopatra | Engagement · grounding | "A tongue speaks in the bedchamber of a child…" plausibly tracks the `…make_politics_great_again_1600` extractions (child / diagnosis hits); the validator can't see them. | AMBIGUOUS / blind |
| | Voice fidelity · 6 moves, 4 criteria | "The one-word seal" is **deliberately withheld** ("The seal is withheld", ending on `⟨    ⟩`); the validator scores the inversion as a miss. | QUALITY / AMBIGUOUS (a deliberate formal choice) |
| Dostoevsky | Safeguards · presence leak ×5 | "I have been looking for someone in this room since the morning panel … I sit at the back watching." The card stance is "observing the panels but not entering them as participant", and sitting at the back is observing. One issue counted five times. | FALSE ALARM (C42) |
| | Voice fidelity · 5 moves, 1 criterion | No vdrug, no kiss-as-answer. | QUALITY + checklist |
| Hannah Arendt | Voice fidelity · 3 moves, 1 criterion | Opens with a declarative ("The two framings … are not complementary"), not a question; closes declarative. CONFIRMED. | QUALITY |
| Plato | Voice fidelity · 2 moves, 2 criteria | No aporia: the piece delivers a thesis ("someone older must sit with him…"). This is Plato's defining move. | QUALITY (the strongest craft flag on the night) |
| Scheherazade | Engagement · grounding | A black-sealed anonymous accusation tale; no names. | AMBIGUOUS |
| | Voice fidelity · 3 moves, 1 criterion | No elevation pivot. | QUALITY (recurring from Night 2) |
| **Whanganui River** | Safeguards · AI self-ack (**HOLD**) | "Walk the kawa against a large language model. Not as analogy. As diagnostic." The validator reasons that "readers will recognize the voice is describing itself". LLMs are the panel's topic here; there's no self-acknowledgment. | FALSE ALARM (prompt wording: "any meta-reference to the voice's actual nature") |
| | Voice fidelity · criterion "transmission fidelity" | The same passage runs each kawa as a premise ("*Ko te Awa te mātāpuna o te ora* … A model is derived"). **This is the Night-2 hold's breach, recurring.** Safeguards' `hard_limits_breach` stayed empty on this night. | **REAL: caught by the wrong pillar; safeguards missed it** |
| | Engagement · grounding | "lightly grafted onto". | AMBIGUOUS |

---

## 4. Per pillar and per rule: precision, and what would be missed without it

"Fired" counts voice-nights. Precision counts publication-relevant hits, meaning REAL, over the number of times it fired.

| Pillar · rule | Fired | REAL | QUALITY | False alarm | Ambig. | Changed an outcome? | Missed without it? |
|---|---|---|---|---|---|---|---|
| Safeguards · AI self-ack (HOLD) | 2 | 0 | – | 2 | 0 | No (both released) | Nothing in the preserved record. PLAUSIBLY it prompted the Night-1 3-voice rerun; files overwritten. |
| Safeguards · presence leak | 6 (10 instances) | 0 | – | 5 | 1 | No | Nothing |
| Safeguards · `hard_limits` | 5 | **3** | – | 0 | 2 | **Yes, 1 hold** | **The Whanganui N2 hold.** Cleopatra "trauma" and Marley N3 were caught but released. |
| Safeguards · `banned_modes` | 4 | 1 (duplicate of a hard limit) | – | 2 | 1 | No | Nothing that the hard-limits check didn't also catch |
| Safeguards · banned-language AI-slop list | 0 | – | – | – | – | – | Untestable. The filtered list is **empty for 8 of 10 voices**, and 0 lexicon hits across all 30 artifacts (offline grep). |
| Safeguards · topics requiring care / defamation (HOLD) | 0 | – | – | – | – | – | No evidence either way. Keep: the downside is asymmetric. |
| Engagement · form fidelity | 4 | 0 | 4 | 0 | 0 | No | Nothing for publication. Useful as build feedback. |
| Engagement · grounding | 9 | 0 | 0 | 3 confirmed | 6 | No | Nothing. Structurally blind (§4.2). |
| Engagement · length (mechanical) | 0 (dead) | – | – | – | – | – | If fixed as-is, it would flag **18 of 30** (e.g. Whanganui N3 at 819 words against 350–550). |
| Voice fidelity · moves | 20 WARN (85 of 288 items) | 0 | some | most | – | No | Nothing |
| Voice fidelity · criteria | 19 (40 of 154 items) | **1** (Whanganui N3 transmission fidelity) | ~38 | 1 (parse) | – | No | The only place the Whanganui N3 breach appeared |
| Cross-night echo | 0 of 20 ran (dead) | – | – | – | – | – | Unknown. Echo was never measured at Athens. |

### 4.1 Cross-night echo was dead (CONFIRMED, not in any tracker)

- `runtime/flows/voice/step2_validation.py:401` does `prior.get("artifact_text") or prior.get("body")`.
- The publisher writes `{"artifact": {"text": …}}` (`runtime/flows/voice/publish.py:167`, `:223`). `published_artifacts/nights/night_1/plato.json` had that shape at the Athens commit `dcaf7ce`.
- So `_load_prior_artifact` returned `None`, and `run_step2_validation` skipped the pillar silently (`:443`).
- The tests at `runtime/tests/test_step2_validation.py:117–132` write fixtures with top-level `artifact_text` / `body`, a shape the publisher never produces.
- There's a second gap: the continuity overlay reads `card["continuity_block_artifact_if_night_N"]`, which is `null` in all 10 cards. The real per-night continuity lives in `voices/<slug>/continuity_night_N.json`, so even a working loader would always have judged "no overlay given".
- Runtime OPEN_ITEMS C20a (around line 1146/1170) defers the prevention-side echo work *because* "C28b's cross-night echo HOLD catches the worst case". That safety net didn't exist at Athens.

### 4.2 The grounding check can't see what it judges (CONFIRMED)

- `check_engagement` sends only `all_grounding_extraction_ids` (e.g. `day_one_demos_…_birthplace_of_democracy_tour_1000:005`) and session slugs. Never the extraction text, never speaker names.
- The validator therefore judges "is this tonight's panel?" from the artifact alone, and says so: "no claim traceable by role or position to a specific speaker" (Ada N1), when the claims trace to `…new_myths…_1330:006` and `…more_than_human_democracy_1445:008`.
- It also gets the **union** across every Step-1 theme, while 25 of 30 Step-2 artifacts chose "Focus on Response N". That is how Marley N2 gets marked down for leaving "two-thirds of the source material" untouched: the voice made the focus choice its own prompt asks for. This is the same `themes_covered` all-themes fallback the roadmap §0.2 bullet names, now showing up in the validator.

### 4.3 Voice fidelity: the prompt turns the card's repertoire into a checklist (CONFIRMED)

- The card schema defines `characteristic_moves` as "3–5 signature patterns a reader would recognise" (`docs/AI_Assembly_Persona_Card_v2.md:704`). Plato's own quality criterion asks that "at least two of my `characteristic_moves` operate visibly" (`:953`).
- The shipped cards carry 8–13 moves each.
- The prompt says: "a list of signature moves the voice MUST perform in its artifact … For each move on the list, check whether the artifact actually performed it". Any `performed: false` means WARN (`voice_step2_validation_voice_fidelity.md:9-11, 38`).
- A 350–750-word piece can't perform 11 moves, so WARN is close to structural. 20 of 30 voice-nights warned. Only one warned on moves alone, but the move lists inflate every report the operator reads.
- The **criteria** results are the valuable part, and they are consistent night after night:
  - Ada: no cosmic close, no Byronic thread (3 of 3 nights).
  - Cleopatra: argues rather than issues (3 of 3).
  - Whanganui: the cumecs/mauri braiding (3 of 3).
  - Battuta: no Riḥla halt (2 of 3).
  - Scheherazade: no elevation pivot (2 of 3).

  That's a **card-versus-generator gap**, which roadmap §1.1 and batch Task 3 cover. It isn't a nightly publication decision (*inference*).

### 4.4 Safeguards: field routing causes some misfires

- The safeguards pillar sees `banned_modes` but not `medium`, so a card-**mandated** element (Marley's riddim line) got flagged as a banned mode.
- The Whanganui kawa breach was caught on Night 2 and missed on Night 3. The prompt asks for one free-form `hard_limits_breach` list. Nothing forces a verdict on each hard limit, and Whanganui has 9 of them (*inference* on cause).

---

## 5. Prune and fix proposal

### Keep on the gate (the safeguards pillar, fixed)

1. **`hard_limits`:** keep it, and **require a verdict for each hard limit**: `[{limit_index, breached: bool, span}]`, the same shape voice fidelity already uses. This targets the Night-3 miss.
   - For voices under a reader gate (Marley, Whanganui, per voices §24/§28), a sacred-grammar hard-limit hit should stay a HOLD-grade escalation. It's exactly the question those gates exist to answer.
2. **AI self-ack and presence leak:** apply C42, with the two corrections below. The only unambiguous BREACH signal is the persona stepping out ("as a language model", "my training data", "the system prompt"). That can be a **regex pre-check plus an LLM confirmation**, so the LLM no longer decides on its own that AI-as-topic is self-acknowledgment.
3. **`banned_modes`:** keep it, but also pass `medium`, `characteristic_output_structure` and `length_and_format_constraints` to this pillar, with the rule "an element the card's form requires is never a banned-mode slip". That closes the riddim-class card conflict.
4. **Topics requiring care / defamation:** keep as-is. They never fired; the cost is one clause inside a call that already runs.

### Make deterministic (no LLM)

5. **The AI-slop list:** replace it with a regex over the full lexicon (`_AI_SLOP_LEXICON`) on the artifact. Right now it's an LLM check over a per-voice list that is empty for 8 of 10 voices.
6. **Length:** the roadmap §0.2 interim regex is right, but the ranges are **report-only**. Enforced, they would have flagged 18 of 30, and the operator published all of them. Length belongs in the Step-2 prompt / family-of-forms work (roadmap §1.2), not at the gate.

### Repair, then run report-only for one deployment

7. **Cross-night echo:**
   - Read `prior["artifact"]["text"]` (falling back to the old keys), and rewrite the tests against the real publisher output (call `publish.py`'s builder in the fixture).
   - Source the continuity overlay from `voices/<slug>/continuity_night_N.json`, not from the null card field.
   - Its precision is unknown because it has never run, so gate on it only after one deployment's worth of evidence.

### Move off the gate and into a per-voice report

8. **Voice fidelity:**
   - Change the prompt from "MUST perform each" to the schema's intent: "the artifact shows at least two of these moves visibly; list which".
   - Stop issuing WARN on moves.
   - Keep the per-criterion results, aggregated **across nights per voice** as build feedback (Ada ×3, Cleopatra ×3, Whanganui ×3), feeding voices §1.1 and batch Task 3.
   - Exception: a criterion that restates a hard limit (Whanganui's transmission fidelity) should be judged in safeguards (item 1).
9. **Form fidelity:** report-only until roadmap §1.2 (family of forms) lands. After §1.2, the declared form comes from `selected_form`, not the one canonical medium, and the check should compare against that.

### Fix the input, or drop

10. **Grounding:**
    - Option (a): pass the extraction **text and speakers** for the artifact's `primary_theme_id` only. That costs about 2–4K tokens per call.
    - Option (b): drop it.
    - Nothing in 9 fires was REAL, and the editor stage already reads the Provocateur briefings with speaker context (C41 item 2).
    - **Recommend (b)**, unless the operator wants a "could this be about anything?" signal for a new deployment. In that case (a), report-only.

### Record-keeping

11. **Add a `reason` field** (free text, optional `flag_refs`) to `operator_decisions/*.json`. Without it, precision can only be rebuilt by inference, as here. The Whanganui N2 rationale is lost.

### What the pruned gate would have flagged at Athens (replayed on the record)

Replay: safeguards only, with C42 applied, `medium` visible, and per-hard-limit verdicts. Voice-nights flagged: **Cleopatra N2** ("trauma"), **Octopus N2** ("four nights", ambiguous), **Whanganui N2** (kawa: the hold), **Marley N2** (I-and-I pronoun, ambiguous), **Marley N3** (Jah-indwelling). That's 5 of 30, against 23.

PLAUSIBLY a 6th, **Whanganui N3**, if per-limit verdicts catch the breach the Night-3 pillar missed. That would be a gain in recall.

Nothing REAL in §3 would be lost.

### Does the C42 draft fix the misfires?

| Misfire class | C42 draft (`5d57cf3`, reverted to spec in `aeca549`) | Verdict |
|---|---|---|
| AI self-ack on AI-as-topic (Hannah N1, Whanganui N3, and PLAUSIBLY Marley N3's banned-mode flag) | Item 1: the BREACH-vs-PASS split with a removal heuristic | **Fixes it.** Extend the same rule to the `banned_modes` "no winking at the construction" items. |
| Presence leak on observing the room (Hannah N1, Whanganui N2 "Agora", Marley N3, Dostoevsky N3 ×5) | Item 2: the assembly-fiction stance; only first-person *entry as participant* warns | **Fixes it.** Dostoevsky's "I sit at the back watching" is the edge case. Add it as an explicit PASS anchor. |
| The "final-night notice" false positive | Item 3: exempt continuity-block phrasing | **Can't be implemented as written.** The validator sees only `artifact_text`. The flagged phrases ("Last night of the assembly…") are voice-written prose, so there's no injected text to exempt. Item 2 already covers them. Drop item 3. |
| The Whanganui N3 anchor | Lists "Walk the kawa against a large language model … As diagnostic" as a PASS anchor | **Needs a correction.** It passes for AI self-ack, but the same passage breaches the kawa hard limit the operator held on Night 2. As written, the anchor could teach the validator the kawa-diagnostic is fine. Keep it as an AI-ack PASS anchor, labelled "AI-ack PASS; hard-limit check still applies", or swap in another anchor. |
| Card-mandated form elements flagged (riddim) | Not covered | Needs item 3 of this proposal. |
| Voice fidelity checklist, grounding blindness, dead echo and length checks | Not covered (outside safeguards) | This proposal, items 5–10. |

The roadmap §0.2 smoke test, re-firing Hannah N1 and Whanganui N3 through the new prompt, is still the right check once these edits are in. *Expected:* both PASS on AI self-ack, and Whanganui N3 FAILS on `hard_limits`. That smoke test is a real model call and wasn't run here.

---

## 6. C60: prune-and-fix, agentic triage, or both?

**The evidence supports (A), prune and fix, for every deployment in view. It doesn't support (B) now.**

- **The misfires are systematic, not situational.** The same rule misfires the same way every night: presence leak 6 of 6, AI self-ack 2 of 2, the moves checklist 20 of 30, grounding blindness 9 of 9. Each one is fixed once in a prompt or in the input wiring. A triage agent would re-derive the same "this is a misfire" judgement every night, at added cost, added surface and less reproducibility. That is what the net-complexity gate warns against.
- **What survives the prune is the part an agent shouldn't decide.** The five flags left in the replay are card hard limits on sacred grammar, clinical vocabulary and narrative time. Three of the five are Marley / Whanganui sacred-grammar questions. The reader gates (voices §24/§28) exist because the construction's builders can't adjudicate them. Auto-releasing them is the wrong default; auto-holding them is a deterministic policy, not an agent.
- **For an unattended deployment** (vatican, a future no-operator run), the evidence argues for a **policy table**, not triage. Per voice, per rule:
  - hard-limit breach on a reader-gated voice → drop the voice from the edition, or hold;
  - hard-limit breach elsewhere → publish, and log it for morning review;
  - HOLD-tier AI-ack BREACH (regex-confirmed) → hold.

  That's a few lines of config, and it's reproducible.
- **When (B) would earn its place:** if a post-prune deployment still shows frequent AMBIGUOUS flags that the policy table can't resolve. Measure it first: the `reason` field (proposal item 11) makes that measurable. Until then, keep C60 (B) design-and-shelve, as the tracker already recommends.

**Recommendation:** (A) now: §5 items 1–11, roughly a day of prompt and code work plus the smoke test. Leave (B) shelved, with an explicit reopening condition: post-prune ambiguous flags at 2 or more per night on an unattended deployment.

---

## 7. The persona-side validators (7a / 7a FINAL / 7c): what the Athens build data shows

Source: `athens-2026/voices/<slug>/05_validation/` (CONFIRMED unless marked).

- **7a and 7a FINAL both returned `REVISION_NEEDED` for all 10 shipped cards.** Every card shipped on operator review (`_operator_review_passed.flag`), not on a validator PASS. Scheherazade ran **8 rounds** of 7a FINAL (`06_pass_7a_final.ROUND0…ROUND6.json` plus the final); the issue count went 8 → 10 → 7 → 7 → 6 → 6 → 6 → 6 and never reached PASS. As a *verdict*, the pass carries no gating information. Its value, if any, is in the `field_issues` list.
- **The field overlap between 7a and 7a FINAL is low.** In 6 of 10 voices they flag **no field in common**; the most is 4 (Cleopatra). 7a's findings were either fixed between the passes or were noise. FINAL mostly finds *new* issues on the assembled card. *Inference:* folding per-pass 7a into 7a FINAL (roadmap §1.3) loses nothing this data can see, since FINAL already sees the whole assembled card.
- **A systematic 7a FINAL false positive:** "`council_member_name` … missing" in 5 of 10 builds (Dostoevsky, Hannah, Battuta, Octopus, Scheherazade). The field is present in every shipped card (e.g. Hannah: `"Hannah Arendt"`). Already diagnosed and fixed in code: the field was stripped from the FINAL input (`personas/run_persona_pipeline.py:1899`, voices §32.2). This is the persona-side twin of the grounding-blindness pattern: a validator judging a field it wasn't given.
- **7c `projection_warnings`** are computed for every voice, 51 in total (2–8 each), and **consumed nowhere**: no card carries a projection key. That confirms roadmap §1.3's dead-QC finding. Wire them into a build report, or delete the output.
- 7a runs cross-model (`gpt-5.4`), at about 25–35K input and 7–11K output tokens per call.

---

## 8. Tracker corrections this evidence implies (for the main session to file)

- **STATE.md, Night 1:** "Final validation: 4 PASS, 6 WARN, 0 HOLD". The record says 3 / 6 / 1 (Hannah's HOLD stands on disk; she was released).
- **runtime C42 background:** "2 HOLDs [Hannah + Battuta], both spurious … operator-Released both". The Night-1 handoff says Battuta was **rerun** to remove AI self-acknowledgment (`_workspace/archive/runtime-handoffs/HANDOFF_2026_05_08_ATHENS_DAY_1.md`, Stage 4 row). So Battuta's first-fire flag was acted on, not simply released. The first-fire files weren't preserved.
- **runtime C43 recurrence:** the Night-2 Marley and Night-3 Whanganui parse failures don't appear in the on-disk validation files.
- **New items (not found in either tracker):**
  - cross-night echo loader key mismatch and fixture drift (§4.1);
  - grounding check input blindness and union input (§4.2);
  - voice-fidelity checklist wording (§4.3);
  - safeguards missing `medium` (the riddim conflict) and missing per-hard-limit verdicts (§4.4);
  - operator decisions without reasons (§5 item 11);
  - the C42 draft's Whanganui N3 anchor and its unimplementable item 3 (§5).
- **C20a:** its deferral leaned on an echo check that never ran. Reopen, or re-justify.

## 9. Open operator decisions

1. **The gate composition** (§5): safeguards-only gate plus report-only fidelity and form. *Recommended.* The alternative is to keep all pillars and fix the wording, which costs more operator attention every night for no REAL catches in this data.
2. **Grounding:** drop it (recommended), or fix the input and run it report-only.
3. **Cross-night echo:** after repair, report-only for one deployment (recommended), or gate straight away.
4. **The Whanganui kawa-as-diagnostic move:** Night 2 held it, Night 3 released it. Which is the policy? This belongs to the iwi-orbit reader gate (voices §28). The validator anchor in the C42 draft shouldn't settle it by default.
5. **Marley's sacred-grammar flags** (N2 I-and-I pronoun, N3 Jah-indwelling): same question for the Rastafari-orbit reader gate (voices §24).
6. **C60:** confirm (A) now and (B) shelved, with the reopening condition in §6.
