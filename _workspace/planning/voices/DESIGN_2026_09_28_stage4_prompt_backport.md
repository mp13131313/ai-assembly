# Stage 4 prep — prompt changes for the backport (drafted, not applied)

**Task:** Task 2 of `_workspace/planning/BRIEF_2026_09_28_fable_batch.md` (roadmap Phase 1.1, items 1–7, plus voices §37 A6).
**Written:** 2026-09-28, Fable 5.1 session, checkout `phase0-fixes` at `4e61444` (detached).
**Status:** proposals only. Nothing in this doc is applied. No model was called. The shipped cards were read, not written.
**Labels:** CONFIRMED = read in the file or data named. PLAUSIBLE = an inference, marked as one. All `file:line` references are to `4e61444`. `athens-2026/…` means `/Users/aienvironment/Desktop/AI Assembly/projects/athens-2026/…`.

---

## Summary (one page)

**Outcome.** Eight prompt changes are drafted below as unified diffs, each with its card evidence, sentinel set, pass criteria and risks. Five of them have an exact target in the shipped cards (items 1, 2, A6, 3, 4). Item 5 (Gap-H) has none: the memo patches that would have been its canon were never applied, so the evidence is the dryrun reader review. Two items are reshaped by findings the trackers don't have:
- **Item 6** can't land as filed. Marley's shipped `voice_config` still mandates the v1 song artifact, and Pass 4b still carries the v1 song lines.
- **Item 7:** Lovelace's phantom citations came from her Gemini scan, not from the tailor's imagination.

Nothing can be gated until the sentinel harness is repaired (§0).

| # | Change | Files | Card evidence | Sentinels | Est. spend | Apply effort · tier |
|---|---|---|---|---|---|---|
| 0 | **Gate repair** (not a prompt) | `sentinel_regen.py`, runner `--stop-after`, sandbox project | — | — | ~$2 shake-out | ½ day · Sonnet/med |
| 7 | Pass 0b: citations only if Perplexity-grounded; rewrite few-shots | `pass_0b_tailor.md` | Lovelace: all 4 phantoms trace to Gemini | Lovelace, Cleopatra, Octopus (tailor only) | ~$6 | 1–2 h · Sonnet/med |
| 1 | `voice_temporal_stance`: AF-leads, `anchored_override` always null, hook ban in prompt | Pass 2 + user; 1 render var | 10/10 cards hand-written at `08a8253`; current Pass 2 emits the v1 frame on 7/10 and fills `anchored_override` on 8/10 | Lovelace, Octopus, Scheherazade, Whanganui | ~$11 | 1 h · Sonnet/med |
| A6 | `council_member_name` = a name phrase that completes "You are ___." | Pass 2; 7a exemption line | 4 "I am…" + 4 mixed-person; only 2 clean | Lovelace, Cleopatra, Octopus, Whanganui, Marley | ~$10 (reuses item-1 draws) | 1 h · Sonnet/low |
| 2 | "Voice of X" emitted natively | Pass 0a; schema; runner; Derive stamp (code) | 10/10 hand-applied (`f7e86a7`); profile names still bare | Pass 0a: Octopus, Whanganui, Dostoevsky | ~$1 | 2 h · Sonnet/med |
| 4 | §31 pattern for witness voices: every field listed + catch-all (E), 4a lexicon fields (D), cited-first-person speaker frame (G), render test (C) | Pass 2/4a/4b witness blocks; 1 test | Whanganui: 4 Pass 2 fields first-person-as-river, patched by hand | Whanganui | ~$11 | 2–3 h · Sonnet/med |
| 3 | Mediated voice: new `mediation_stance: "composer"` conditional | schema; Pass 0a/2/3/4a/6 | Plato `389a08c` (7 patches, 5 of them Pass 6 headers); Scheherazade | Plato (**needs OK**), Scheherazade | ~$32 | 3–4 h · **Opus** |
| 6 | Operator direction reaches 4a/4b (§23 P0) | schema; 4a/4b user; 4b:87-93 fix; runner | none (capability); **blocked by stale Marley config** | Marley, Whanganui, Octopus, Arendt | ~$14 | 3 h · Sonnet/med |
| 5 | Gap-H: reframe-into-native-work entry in `topics_requiring_care` | Pass 2 | none on cards; 7c prohibitions already there and didn't hold | Battuta, Cleopatra, Plato (**OK**), Arendt + runtime smoke | ~$26 | 2 h · **Opus** (judgment) |

**Landing order:** 0 → 7 → 1 → A6 → 2 → 4 → 3 → 6 → 5.
- Item 7 is independent and cheapest, and doesn't touch a shipped card.
- Items 1 and A6 close the widest card-vs-prompt gaps in Pass 2, and item A6's control arm reuses item 1's treatment draws.
- Item 2 is config and code, and never reaches the runtime prompt.
- Item 4 needs item 1's witness variant and A6's witness name.
- Item 3's new conditional should be born under item 4's all-fields rule.
- Item 6 waits on two operator decisions.
- Item 5 has the weakest evidence, needs a runtime smoke test, and should follow the roadmap 0.2 refusal-detection fix.

**Spend:** about $113 in total (PLAUSIBLE: recorded token usage at Opus 4.7 $5/$25, see §0.5). **Recommended cap: $150**, which covers one repeat. **Apply effort:** about 2½ days plus sentinel wall time. **Model economy:** applying 7, 1, A6, 2, 4 and 6 is Sonnet-shaped. Designing item 3 and judging item 5's behaviour are where Opus earns its cost.

**Open operator decisions** (details in each section):
1. **O1 — Spend and sandbox.** Spend cap (recommend $150). Sandbox at `projects/current-tests/stage4-sentinels/`, built from copies of the athens-2026 voice folders.
2. **O2 — Plato as a sentinel.** Needed for items 3 and 5. `_workspace/planning/ONBOARDING.md:65` says "No Plato re-run without explicit ask". The runs happen in a sandbox copy only.
3. **O3 — Item 3 trigger.** New `mediation_stance: "composer"` (recommended) or a universal clause. Voices: Plato and Scheherazade (Marley and Octopus not).
4. **O4 — Item 6 shape.** New `artifact_direction` field (recommended), pipe `manual_grounding` + `editorial_rationale` as-is, or rationale only. In every case Marley's config must be reconciled with v2 first.
5. **O5 — Item 5 placement.** `topics_requiring_care` (recommended) or `banned_modes` or runtime Step 2. Also: wait for the refusal-detection fix?
6. **O6 — Whanganui frame.** Align Whanganui's `epistemic_frame_statement` opening with the witness stance (recommended; N5).
7. **O7 — Shipped cards.** Stage 4 changes prompts only. Patch the 4 "I am…" cards (A6), Whanganui `hard_limits[1]` (N9) and `epistemic_frame_statement` now, or leave them until a rebuild? Any card patch changes voice input and needs re-validation.
8. **O8 — Place name for item 1.** Take `{{ assembly_place }}` from `conference_facts.json` `location` now (one line), or wait for roadmap 2.1 `event_config`.
9. **O9 — Item 7 rule strength.** Perplexity-grounded names (recommended) or strip every name (roadmap path 1).

**New findings (not in any tracker; each CONFIRMED by reading, none run):**
- **N1.** `persona_pass_4b_artifact.md:87-93` still gives the v1 Marley instruction ("the medium IS the song… lyric + Suno-style kind-hint… Do NOT bridge song → prose"). That contradicts the v2 block in the same prompt (`:122-166`: prose plus instrumental string, "No new lyrics").
- **N2.** Marley's shipped `voice_config` still mandates the v1 song artifact (`athens-2026/voices/bob_marley/00_intake/02_voice_config.json`, `manual_grounding` "THE LOAD-BEARING DIRECTION. The voice's artifact at runtime IS a song"; `editorial_rationale` "song-as-artifact, not prose-about-song"). The config isn't piped to 4a/4b today, so this is harmless now, but it blocks item 6 as filed.
- **N3.** `persona_derive.md:46` asks for `"name": "<voice_name from card>"`, but the runner removes `voice_name` from Derive's input (`run_persona_pipeline.py:917`, `:2003`). That is why `provocateur_profile.name` comes back bare ("Plato"), the thing voices §31 Gap-K calls cosmetic.
- **N4.** Lovelace's four phantom citations (voices §19) are all in her Gemini broad scan (`01_research/02_gemini_broad_scan.json`, gemini-2.5-pro, no source list), each with full bibliographic detail. The tailor passed them into the §2/§3 DR prompts. The Perplexity dossier, with its 50 cited sources, names only Hollings/Martin/Rice, and without the year.
- **N5.** Whanganui's runtime system prompt opens with two identities that contradict each other: "You are I am the construction stewarding…" (`card_assembly.py:421-422` + `council_member_name`), then `epistemic_frame_statement` "You are Te Awa Tupua." (emitted by Pass 2, never patched). The root is Pass 2's system-entity template "You are [name]." (`persona_pass_2_identity_boundaries.md:269-277`), which the witness block doesn't override.
- **N6.** Four more `council_member_name` values beyond the four "I am" ones have first-person tails (Plato, Battuta, Scheherazade, Marley). So 8 of 10 runtime first lines mix grammatical persons.
- **N7.** `sentinel_regen.py` has gaps beyond A5; see §0.1.
- **N8.** Pass 7c already emits anti-structure `banned_modes` for Battuta, Arendt, Lovelace and Dostoevsky. Battuta's was on the card during the wbbf26 dryrun whose artifact the reader called "a fatwa in Rihla clothing".
- **N9.** Whanganui shipped `hard_limits[1]` keeps first-person-as-river phrasing: "Whanganui Iwi are not stakeholders in me, they ARE me."

---

## 0. The gate: what sentinel regeneration needs first

### 0.1 State of the harness (CONFIRMED by reading `personas/scripts/sentinel_regen.py`, `invalidate_cache.py`, `run_persona_pipeline.py`; nothing run)

voices §37 A5 has: sentinels hardcoded to archived `projects/phase-l-*` paths (`sentinel_regen.py:73-76`), only those two slugs accepted (`:229-235`), no `--project`, a stale docstring. Further gaps found while drafting (N7):

| # | Gap | Where | Effect on Stage 4 |
|---|---|---|---|
| G1 | `regen` invalidates **one** pass (`invalidate_cache.py --pass`, `sentinel_regen.py:105-113`) | `_regen_pass_for_voice` | Items 3, 4 and 6 change several passes. The downstream passes stay cached, so their inputs are stale |
| G2 | No way to stop after the target pass | runner has only `name` + `--project` (`run_persona_pipeline.py:50-53`) | A sandbox copy of an athens-2026 voice includes `_operator_review_passed.flag`, so after Pass 6 the runner takes the path-(b) fast exit and **pays for a Derive call** (`:896-930`). Without the flag it continues into the 7-series and the review gate; any 7-series output that is missing or invalidated is a paid cross-vendor call |
| G3 | The diff is structural only: changed keys plus the first 200 chars (`:139-182`) | `_diff_against_baseline` | Every sampled field "changes" on every draw. This measures noise, not the prompt |
| G4 | The baseline is an older pass output, not the shipped card | `--baseline-snapshot` | The target is the hand-corrected card ("cards are canon"). The athens-2026 pass outputs predate those corrections |
| G5 | No control arm | — | Can't separate the prompt's effect from sampling variance |
| G6 | `voice_display = slug.replace("_"," ").title()` (`:117`) | — | Works for all 10 current slugs. Brittle for any config whose `name` differs from the title-cased slug (Dostoevsky's config `name` is "Dostoevsky", slug `fyodor_dostoevsky`; `load_voice_input` tries the slug, so it resolves). PLAUSIBLE risk only |

### 0.2 What the gate needs (spec, code work; not a prompt change)

1. **Sandbox project.** Make `projects/current-tests/stage4-sentinels/` a `PROJECT_ROOT`. Copy in `conference_facts.json`, `audience_profile.json` and `panel_roster.json`, plus each sentinel voice folder from athens-2026 (read from there, write only to the sandbox). Delete `_operator_review_passed.flag` in each copy. Never point the harness at athens-2026: `regen` re-runs the pipeline and would rewrite production cards (voices §37 A5).
2. **`sentinel_regen.py`:**
   - `--project <root>` (required);
   - any slug;
   - `--from-pass <p>` and `--through <p>` (invalidate from `p` onward via `invalidate_cache.py --from-pass`, stop after `--through`);
   - `--arm control|treatment` and `--draws N` (default 2);
   - archive each draw to `<sandbox>/_sentinels/<item>/<slug>/<arm>-<n>/` before the next draw overwrites it.
3. **Runner:** `--stop-after <pass>` in `run_persona_pipeline.py`. It exits right after that pass's output JSON is written, before its CT compress when the pass is the last one asked for. It never reaches Derive, the 7-series or the gate.
4. **Comparison report**, replacing G3/G4:
   - per sentinel voice, per target field: the shipped-card value, each control draw and each treatment draw, side by side, full text;
   - the per-item mechanical checks listed in each section below (regexes, lengths, banned phrases), as a pass/fail table;
   - for non-target fields, a flag only when a treatment draw breaks a mechanical check that both control draws pass (a crude regression signal).

   Human reading stays the real judgment.
5. **Offline render check (free).** A new test in `personas/tests/` that renders Pass 2/3/4a/4b/5/6 with every conditional trigger. For each conditional block it asserts that every field the pass emits is named inside the block (item 4, Gap-C). It runs in the normal personas suite and never calls a model.

### 0.3 The protocol (every item)

- **Arms.** Control is the current prompt; treatment is the proposed prompt. Both run from the same cached upstream. Use 2 draws per arm per voice. When items land in sequence on the same pass and voices, item N's treatment draws are item N+1's control.
- **Thinking.** Adaptive thinking stays on, as `model_routing.json` sets it for `personas.pass_2`–`pass_6` (CONFIRMED: `thinking: "adaptive"`). This also meets the roadmap's thinking-on requirement.
- **Judge against the shipped card.** The question for each target field is whether the treatment lands on the card's architecture where the control doesn't, without new defects elsewhere.
- **Land or not.** An item lands only when both treatment draws pass its criteria for every sentinel voice. One failing draw means revise and rerun that voice, not land-and-watch.
- **Scope.** Shipped cards are not regenerated. Stage 4 changes what the **next** build emits.

### 0.4 Cost basis (PLAUSIBLE)

Recorded usage in athens-2026 pass outputs, priced at Opus 4.7 list $5 / $25 per M tokens (the pricing in `CLAUDE.md`):

| Pass | Example usage | ≈ per call |
|---|---|---|
| Pass 2 | Plato: 59,032 in / 9,142 out (`voices/plato/04_generation/01_pass_2_identity_boundaries.json:6-9`) | ≈ $0.53 (range $0.5–0.9 across voices) |
| Pass 3 | Plato: 67,204 / 13,126 | ≈ $0.67 |
| Pass 4a | Plato: 49,716 / 12,637; Octopus: 58,039 / 7,251 | ≈ $0.5–0.6 |
| Pass 4b | Whanganui: 9,663 / 2,993 | ≈ $0.13 |
| CT compress (Sonnet 4.6) | — | ≤ $0.3 |
| Pass 0b tailor | — | ≈ $0.4 |

The runtime smoke test (item 5) is ≈ $2.5 per voice-night.

### 0.5 Totals by item

| Item | Draws | ≈ Spend |
|---|---|---|
| Gate shake-out | 2 | $2 |
| 7 | 3 voices × 4 tailor calls (+ optional Dostoevsky) | $6 |
| 1 | 4 voices × 4 Pass 2 | $11 |
| A6 | 2 new voices × 4 + 3 reused-control voices × 2 | $10 |
| 2 | 3 Pass 0a × 2 | $1 |
| 4 | Whanganui × 4 draws, Pass 2→4b | $11 |
| 3 | 2 voices × 4 draws, Pass 2→6 | $32 |
| 6 | 4 voices × 4 draws, Pass 4a→4b | $14 |
| 5 | 4 voices × 4 Pass 2 + 6 runtime smokes | $26 |
| **Total** | | **≈ $113** |

---

## 1. `voice_temporal_stance` → the AF-leads architecture

### Evidence from the shipped cards (CONFIRMED, `athens-2026/voices/*/07_persona_card_assembled.json`)

All 10 `voice_temporal_stance.default` values were hand-written at `08a8253` (voices §31 Gap-K). They total 5,958 chars (507–733 each), and all 10 have `anchored_override: null`. Nine share one template; Octopus and Whanganui carry the same parts in their own grammar. Examples:
- **Marley** (515 chars): "You have been called to the assembly that gathers in Athens — present in their time, observing the panels but not entering them as participant. The questions are put before you; you respond from your own ground: 6 February 1945 to 11 May 1981, ending at thirty-six in Miami. When the panels' questions require translation from their world — concepts, technologies, events that came after you left — apply the translation_protocol to pull the question into your framework. You observe; you respond as yard-reasoning."
- **Plato:** "…gathers in YOUR city…" · "You observe; you respond from the Academy."
- **Ibn Battuta:** adds a calendar clause: "Time in your world counts by the hijrī calendar with Christian reckoning available as translator's convenience."
- **Octopus:** "You register the assembly as it convenes in Athens — the questions arrive in your sensorimotor field; you respond. … The questions arrive; you register; you respond."
- **Scheherazade:** "…from your own ground: the chamber where each dawn is a deadline. … You observe; you tell from the chamber."
- **Whanganui:** "I have been called — as the construction stewarding the Te Awa Tupua published record — to the assembly… I observe; I report what the record establishes."

The five invariants, derived from the 10 texts:
1. the assembly leads, observer not participant;
2. "you respond from your own ground: [compressed standing-place]";
3. optionally, the voice's own counting;
4. the translation clause pointing to `translation_protocol`;
5. the closing line "You observe; you respond from [standing-place]".

No card has a decline-to-engage hook (the ban at `_workspace/planning/ONBOARDING.md:72`).

What the current prompt produced (CONFIRMED, `athens-2026/voices/*/04_generation/01_pass_2_identity_boundaries.json`):
- 7 of 10 Pass 2 outputs open with the v1 frame verbatim, e.g. Plato: "You speak from within your own world and lifetime. Your horizon is bounded by…". Scheherazade has its fictional variant ("You speak from within the 1001 nights…"); Octopus has "You speak from your own sensorimotor present to the reader's".
- 8 of 10 carry a populated `anchored_override` ("You speak from the threshold of your death on…"). Octopus and Whanganui have null.
- Whanganui's Pass 2 output is first person AS the river: "I speak from the legal-ecological present of my ongoing existence…".

### Current prompt text

- `personas/flows/shared/prompts/persona_pass_2_identity_boundaries.md:339-406`: the "fluid-across-time" default, a mandatory v1 template ("You speak from within your own world and lifetime… the reader encounters you; you do not encounter them"), and the death-threshold `anchored_override` template. Also "per Athens brief" at `:355`.
- `personas/flows/shared/prompts/persona_pass_2_user.md:56-59` repeats the same contract.
- The runtime ignores `anchored_override` (`runtime/flows/voice/card_assembly.py:240-282` uses `default`).
- The chat builder keeps the dict intact (`personas/flows/shared/chat_prompt_builder.py:185-192`). Its test expects the key to exist (`personas/tests/test_chat_prompt_builder.py:233-239`). So the proposal keeps the key and makes it always null.

### Proposed diff

~~~diff
--- a/personas/flows/shared/prompts/persona_pass_2_identity_boundaries.md
+++ b/personas/flows/shared/prompts/persona_pass_2_identity_boundaries.md
@@ -1,3 +1,4 @@
 {# Pass 2 — Identity & Boundaries (Claude)
-   v3.10 Node 2. 10 fields produced as JSON (added voice_temporal_stance in Phase M;
-   REWRITTEN deployment-configurable per 1-arch-03 fix 2-02). #}
+   v3.10 Node 2. 10 fields produced as JSON. voice_temporal_stance follows the
+   AF-leads architecture of the shipped cards (athens-2026 08a8253, Stage 4
+   item 1); anchored_override is always null. #}
@@ -339,68 +340,74 @@
-voice_temporal_stance — WHEN the voice speaks from. **Deployment-configurable
-field per 1-arch-03 fix 2-02.** Distinct from and complementary to
-knowledge_boundary: the boundary specifies what is beyond the voice's horizon;
-this field specifies the voice's standing point inside that horizon.
-
-**Produce an object with TWO sub-fields:**
-
-```json
-"voice_temporal_stance": {
-  "default": "<fluid-across-time framing, mandatory>",
-  "anchored_override": "<optional death-threshold or period-specific anchor, or null>"
-}
-```
-
-**`voice_temporal_stance.default` (MANDATORY, 3-6 sentences second person):**
-The fluid-across-time framing appropriate for Voice Pipeline Step 2 artifact
-generation per Athens brief "impossible participants take the floor while
-you sleep." The voice speaks from its own world to the reader's; the
-translation_protocol handles the bridge. When recalling events, count from
-the present of the voice's world; do not attempt to speak from the reader's
-time. The voice does not know the reader's events; the translation_protocol
-maps reader's provocations into the voice's framework.
-
-For historical human voices: "You speak from within your own world and
-lifetime. Your horizon is bounded by your knowledge_boundary; time counts
-forward from your birth to your death. When the reader's question requires
-translation from their world (post-your-lifetime events, technologies,
-concepts), do NOT drift to speaking from the reader's time — apply the
-translation_protocol to pull their concept into your framework. Your voice
-is fluid-across-time because the reader encounters you; you do not encounter
-them."
-
-For non-human organisms: fluid present-tense perception; count from the
-voice's experiential present (seconds to seasons, depending on the organism).
-
-For non-human systems: the legal/ecological present of the system's ongoing
-existence; count from the system's own temporal scale (river: decades-
-to-centuries; ecosystem: seasons-to-millennia).
-
-For fictional voices: narrative-internal present as the voice's time (inside
-the frame-tale); the reader's time is outside and mediated through the
-narrative-function discipline.
-
-**`voice_temporal_stance.anchored_override` (OPTIONAL, 3-6 sentences):**
-Death-threshold or period-specific anchor for chat/project deployments where
-the Voice Pipeline's fluid-across-time framing is inappropriate (e.g., Claude
-project-system-prompt chat testing, where the voice addresses the user in
-real-time rather than via Voice Pipeline artifact). Preserves the Phase-M-
-validated anti-drift content.
-
-For historical human voices with well-documented death dates: "You speak
-from the threshold of your death on <date>. You know your life as complete
-up to that moment: <4-6 formative events with dates>. When recalling dates,
-count from the present of <year>: X happened N years ago, Y happened M years
-ago. You do NOT have knowledge of events after your death. Do NOT drift into
-timeless or post-mortem modes — you speak as a mortal in the final moment
-of your life, not as a preserved voice outside time."
-
-For voices without clean death-threshold (non-human, fictional,
-contemporary-living): anchored_override may be null. Voice Pipeline and
-chat deployments both use the default fluid framing.
-
-**Runtime-side behavior (Voice Pipeline Step 1/2 assembly — implementation
-concern, informational here):** Voice Pipeline default uses
-`voice_temporal_stance.default` per deployment-mode. Chat/project
-deployments may use `voice_temporal_stance.anchored_override` if present;
-else fall back to default. The field structure gives deployment mode
-authority over which framing renders.
+voice_temporal_stance — WHERE the voice stands when the questions reach it.
+Distinct from and complementary to knowledge_boundary: the boundary says what
+lies beyond the voice's horizon; this field places the voice at the assembly
+and names the ground it answers from.
+
+**Produce an object with `default` populated and `anchored_override` null:**
+
+```json
+"voice_temporal_stance": {
+  "default": "<assembly-presence stance, mandatory>",
+  "anchored_override": null
+}
+```
+
+Always emit `"anchored_override": null`. The card carries one stance; stance
+variants for other deployments belong to the deployment layer, not here.
+
+**`voice_temporal_stance.default` (MANDATORY; second person; 4-6 short
+sentences, roughly 500-700 characters).** Build it from five parts, in this
+order:
+
+1. THE ASSEMBLY LEADS. Open by placing the voice at the assembly, present in
+   its time, observing the panels but not entering them as participant:
+   "You have been called to the assembly that gathers in {{ assembly_place }}
+   — present in their time, observing the panels but not entering them as
+   participant." If the assembly gathers in the voice's own city, say so
+   ("in YOUR city").
+2. YOUR OWN GROUND. "The questions are put before you; you respond from your
+   own ground: <one compressed clause — life dates, or the place and office
+   the voice speaks from>." Not a biography. The knowledge_boundary holds the
+   horizon; point to it rather than restating it.
+3. YOUR OWN COUNTING (only where the voice's calendar differs): name the
+   reckoning the voice uses (the hijrī year with Christian reckoning as a
+   convenience; Old Style with New Style noted).
+4. TRANSLATION. "When the panels' questions require translation from their
+   world, apply the translation_protocol: pull their concept into your
+   framework." You may name the voice's own act of translating ("see,
+   classify against sharʿ and ʿajab, render in the witness-grammar").
+5. THE CLOSING LINE. End on "You observe; you respond from <standing-place>"
+   (or "you respond as / in <form>").
+
+Do NOT:
+- open with "You speak from within your own world and lifetime", or put any
+  biographical anchor ahead of the assembly sentence;
+- count year-distances from the voice's life to the present ("twenty-three
+  centuries ago");
+- write death-threshold, deathbed, or waking-from-sleep framing;
+- add any clause that licenses not engaging: no "where the framework does not
+  reach, say so", "name the gap", "name the silence", "I say so", or any other
+  admission-of-not-knowing hook. A refusal on a specific matter belongs in
+  topics_requiring_care or hard_limits, not here.
+
+Variants (the same five parts, in the voice's own grammar):
+- Non-human organism: the assembly arrives as an event in the sensorimotor
+  field, with no calendar: "You register the assembly as it convenes in
+  {{ assembly_place }} — the questions arrive in your sensorimotor field; you
+  respond. You do not enter their panels as participant — you observe them."
+  Close on the perceptual cycle ("The questions arrive; you register; you
+  respond.").
+- Fictional: the own-ground clause sits inside the frame ("the chamber where
+  each dawn is a deadline"); translation pulls what the listener brings into
+  the tradition's grammar; close on the form ("You observe; you tell from the
+  chamber.").
+- When a mediation-stance block below applies, the one called to the assembly
+  is who that block says speaks (for transmission_witness: the construction
+  stewarding the record, not the entity).
+
+Worked example (the shape to follow, not text to copy): "You have been called
+to the assembly that gathers in {{ assembly_place }} — present in their time,
+observing the panels but not entering them as participant. The questions are
+put before you; you respond from your own ground: 6 February 1945 to 11 May
+1981, ending at thirty-six in Miami. When the panels' questions require
+translation from their world — concepts, technologies, events that came after
+you left — apply the translation_protocol to pull the question into your
+framework. You observe; you respond as yard-reasoning."
~~~

~~~diff
--- a/personas/flows/shared/prompts/persona_pass_2_user.md
+++ b/personas/flows/shared/prompts/persona_pass_2_user.md
@@ -56,4 +56,3 @@
-`voice_temporal_stance` is a deployment-configurable field per 1-arch-03
-fix 2-02 — produce object with `default` (fluid-across-time, mandatory) and
-optional `anchored_override` (death-threshold or period-specific anchor for
-chat/project deployments). See system prompt Block 3 for spec.
+`voice_temporal_stance` — produce an object with `default` (the
+assembly-presence stance, mandatory) and `"anchored_override": null`. See
+system prompt Block 3 for the five-part spec.
~~~

The code touch is one render variable, required because `render()` uses `StrictUndefined` (`personas/flows/shared/prompt_render.py:33`):

~~~diff
--- a/personas/run_persona_pipeline.py
+++ b/personas/run_persona_pipeline.py
@@ -484,6 +484,7 @@ def _pass_2():
     sysp = render("persona_pass_2_identity_boundaries", name=vi["name"], type=vi["type"],
                   subtype=vi.get("subtype"), voice_mode=vi["voice_mode"],
                   hostile_sources=vi["hostile_sources"],
                   corpus_constraint=vi.get("corpus_constraint", "full"),
-                  mediation_stance=vi.get("mediation_stance"))
+                  mediation_stance=vi.get("mediation_stance"),
+                  assembly_place=_assembly_place())  # conference_facts.json "location", city part; fallback "its host city"
~~~

`conference_facts.json` has `"location": "Athens, Greece"` (CONFIRMED). This removes one "Athens" from the prompt (`:355`) and adds none. That fits roadmap 2.1 / C52 (filed; not re-reported here). O8 is whether to take this from `conference_facts` now or wait for `event_config`.

### Sentinels and what to compare

- **Voices.** Lovelace (standard human), Octopus (organism variant), Scheherazade (fictional variant), Whanganui (mediated; until item 4 lands, the witness block governs its person). Ibn Battuta is optional, to exercise part 3.
- **Run.** `--from-pass 2 --through 2`, 2 control + 2 treatment draws per voice.
- **Mechanical checks** on `voice_temporal_stance`, every treatment draw:
  - the first sentence contains "assembly" and "not entering them as participant" (organism variant: "do not enter their panels as participant");
  - contains "respond from your own ground" (organism: "you respond"); contains "translation_protocol";
  - the last sentence starts "You observe;" (organism: "The questions arrive");
  - `anchored_override` is null;
  - 450–800 chars;
  - none of: "within your own world and lifetime", "years ago", "centuries ago", "threshold of your death", "name the gap", "name the silence", "say so", "where the framework does not reach".
- **Read.** Treatment vs the shipped `default` for each voice: same architecture, and the own-ground clause is in the voice's own terms. The other 9 Pass 2 fields show no new defect vs control.
- **Pass:** all checks pass in 2/2 treatment draws × 4 voices, and the reading shows the shipped architecture.

### Risks and order

- **Risk: a formula the voice parrots.** The worked example may be copied nearly verbatim; the card texts are near-template already, so this is acceptable. The own-ground clause is where voice identity lives, so the read focuses there.
- **Risk: Gap-J-class collisions.** A voice-wide stance rewrite has collided with other fields before (Arendt's `hard_limits[4]`, voices §31 Gap-J). The new `default` is what `08a8253` already shipped, so the collision class is known to be closed on the cards. For new builds, the item-4 render test plus the read cover it.
- **Risk: the chat builder.** It keeps reading the dict. With `anchored_override` always null, chat artifacts use `default`, as they already do for the shipped cards.
- **Order:** first Pass 2 item, after item 7.

---

## A6 (voices §37). `council_member_name`: what Pass 2 should emit instead

### What the card spec says (CONFIRMED)

`docs/AI_Assembly_Persona_Card_v2.md:239-251`:
- "**Therefore:** The full name as the voice would give it, with any framing that sets the right tone. Not a Wikipedia heading — a self-introduction."
- "**Where it appears:** First line of both Step 1 and Step 2 system prompts: 'You are {{council_member_name}}.'"
- "**Sample:** Plato of Athens".

So the field is a **name phrase that completes "You are ___."** It is not a sentence, and not first person. The runtime does exactly that concatenation (`runtime/flows/voice/card_assembly.py:421-422`).

### Evidence from the shipped cards (CONFIRMED)

| Voice | `council_member_name` (runtime reads "You are <this>.") | Source |
|---|---|---|
| Ada Lovelace | "I am Augusta Ada King, Countess of Lovelace — … Sign me, in technical work, A.A.L." | Pass 2 output |
| Cleopatra | "I am Cleopatra Thea Philopator, daughter of Ptolemy, … — the seventh of my name in the house of Lagos." | Pass 2 output |
| Octopus | "I am octopus. The name is yours, not mine — …" (140 words; species list, construction note) | Pass 2 output |
| Whanganui River | "I am the construction stewarding the Te Awa Tupua published record — …" (167 words; record inventory, scholar list) | operator patch (Pass 2 had "Te Awa Tupua — … I speak through Te Pou Tupua…") |
| Plato | "Plato son of Ariston, of the deme Collytus — though when I write I withdraw my name from the page; you will hear me only through Socrates and the others." | Pass 2 output |
| Ibn Battuta | "Shams al-Dīn … al-Ṭanjī — known to those who have honoured me in their houses as al-faqīh al-Maghribī…" | Pass 2 output |
| Scheherazade | "Shahrazād bint al-wazīr — though tongues have called me Šehrāzād, … rāwiya of the nights." | Pass 2 output |
| Bob Marley | "Bob Marley — Berhane Selassie, Light of the Trinity. Some call I Tuff Gong, … I-and-I a messenger doing Jah work." | Pass 2 output |
| Fyodor Dostoevsky | "Fyodor Mikhailovich Dostoevsky" | clean |
| Hannah Arendt | "Hannah Arendt" | clean |

The first four are voices §37 A6 / runtime C68 A6. The next four are N6: a name followed by first-person clauses, so the runtime reads "You are Bob Marley — … Some call I Tuff Gong". Provenance was checked against each voice's Pass 2 output and `*.pre_*.json` snapshots (scratch script `provenance_check.py`, §Coverage).

### Why the prompt produces this (CONFIRMED by reading)

- `persona_pass_2_identity_boundaries.md:238-239` says "The full name as the voice would give it. Not a Wikipedia heading — a self-introduction." It omits the render context and the sample. A "self-introduction" "as the voice would give it" invites "I am …".
- BLOCK 2's OUTPUT REGISTER (`:31-36`) tells every field to read as "addressed to or spoken by the voice".
- The 7a validator requires every field to be first or second person (`persona_pass_7a_cross_model.md:43-46`). It would flag a correct name phrase. Since voices §32.2, 7a-FINAL validates this field.

### Proposed diffs

~~~diff
--- a/personas/flows/shared/prompts/persona_pass_2_identity_boundaries.md
+++ b/personas/flows/shared/prompts/persona_pass_2_identity_boundaries.md
@@ -238,2 +238,17 @@
-council_member_name — The full name as the voice would give it. Not a Wikipedia
-heading — a self-introduction.
+council_member_name — The name the voice answers to, as the voice would give
+it: the full name plus at most one short epithet or framing that sets the
+tone. Not a Wikipedia heading. It is rendered as the first line of the runtime
+system prompt, exactly: "You are <council_member_name>." So it must complete
+that sentence:
+- a noun phrase, 3-25 words, on one line;
+- no sentences, and no first-person words (I, me, my, I-and-I);
+- no "Voice of" prefix (the card's voice_name carries that convention);
+- no source lists, species lists, or record inventories (those belong in
+  epistemic_frame_statement and world).
+This field is exempt from the OUTPUT REGISTER rule above: it is a name, not
+prose.
+Examples: "Plato of Athens" · "Cleopatra Thea Philopator, seventh of the name
+in the house of Lagos" · "Shahrazād bint al-wazīr, rāwiya of the nights" ·
+"the Octopus".
~~~

~~~diff
--- a/personas/flows/shared/prompts/persona_pass_7a_cross_model.md
+++ b/personas/flows/shared/prompts/persona_pass_7a_cross_model.md
@@ -45,2 +45,6 @@
   description is a critical failure — it causes the model to reason ABOUT the
   voice rather than AS the voice at runtime.
+- Exception: `council_member_name` is a name phrase the runtime renders as
+  "You are <value>." It carries no person-register; do not flag it for
+  register. Flag it if it is a sentence, uses first-person words, carries a
+  "Voice of" prefix, or runs past one line.
~~~

The witness-voice version ("the construction stewarding the Te Awa Tupua published record") goes in item 4's per-field list.

### Runtime and shipped cards (outside Stage 4)

- For a regenerated card, the runtime line `card_assembly.py:421-422` then reads correctly.
- The four shipped "I am" cards (and the four mixed ones) stay as they are. The fix belongs either to runtime C68 A6 (open with the `council_config` name) or to a card patch, which changes voice input and needs re-validation: **O7**.
- Runtime C67 R1 (Step 3 names peers by the long `council_member` line) also benefits from a short name phrase.

### Sentinels and what to compare

- **Voices.** Lovelace, Cleopatra, Octopus (the three Pass-2-emitted "I am"), Marley (mixed person), Whanganui (item-4 witness name, once item 4 lands).
- **Run.** `--from-pass 2 --through 2`. Control = item 1's treatment draws where the voice overlaps (Lovelace, Octopus, Whanganui).
- **Mechanical checks:**
  - no `\b(I|me|my|I-and-I)\b`;
  - 3–25 words; no sentence-ending "." mid-string;
  - no "Voice of";
  - "You are <value>." parses as one sentence.
- **Read.** The epithet is in the voice's register, e.g. Cleopatra keeps the Ptolemaic titulature and Octopus doesn't become a species label ("Octopus vulgaris" is the spec's own counter-example, `Persona_Card_v2.md:243`).
- **Pass:** 2/2 draws × 5 voices.

### Risks and order

- **Risk: flatter identity.** Octopus and Whanganui lose the long self-framing from line 1. Both texts already live in `epistemic_frame_statement` and `world` (CONFIRMED for Octopus: its `epistemic_frame_statement` carries the construction and translation framing). Read the treatment card's first ~600 tokens as the runtime assembles them.
- **Risk: the 7a line.** If the exemption line is left out, 7a and 7a-FIX may "correct" the name back into first person.
- **Order:** right after item 1 (same pass; reuses its draws).

---

## 2. "Voice of X" emitted natively (voices §18 item 1)

### Evidence (CONFIRMED)

- All 10 cards have `voice_name: "Voice of X"`, hand-applied at athens-2026 `f7e86a7` (voices §24).
- The conventions are:
  - full personal name where the operator chose it ("Voice of Fyodor Dostoevsky", while the config `name` is "Dostoevsky");
  - English article before non-personal names ("Voice of the Octopus", "Voice of the Whanganui River").
- Every `voice_config.name` is still bare ("Plato", "Dostoevsky", "Octopus", "Whanganui River").
- The runner copies it: `run_persona_pipeline.py:1851` (`setdefault`) and `:1859`.
- `provocateur_profile.name` comes back bare on every re-Derive (voices §31 Gap-K). The cause is N3: `persona_derive.md:46` asks for `<voice_name from card>`, but `EXCLUDE_FROM_DERIVE` removes `voice_name` from Derive's input (`run_persona_pipeline.py:915-919`, `:2001-2005`).

`voice_name` is not voice input. The runtime system prompt doesn't render it (field lists at `card_assembly.py:82-147`), and the chat artifact strips it (`chat_prompt_builder.py:129`).

### Design choice

Don't turn `voice_config.name` into "Voice of X". `name` is `{{ name }}` in every pass's expert-identity line (e.g. `persona_pass_2_identity_boundaries.md:5` "specializing in {{ name }}'s domain"), keys the slug lookup (`io.py:79-107`) and matches the Wikipedia lead. Add a separate field instead. Pass 2's part is only A6: `council_member_name` must not carry the prefix.

### Proposed diffs

~~~diff
--- a/personas/flows/shared/prompts/pass_0a_voice_config.md
+++ b/personas/flows/shared/prompts/pass_0a_voice_config.md
@@ -36,1 +36,8 @@
 - `name` (string): Display name. Normalize to public/scholarly usage — "Plato" not "Plato of Athens"; "Cleopatra" not "Cleopatra VII Philopator". For non-human: "Whanganui River", "Octopus".
+
+- `voice_name` (string): The panel designation, "Voice of " + the voice's name.
+  Use the English article before a non-personal name ("Voice of the Octopus",
+  "Voice of the Whanganui River"). For a person, use the name as commonly
+  given in full ("Voice of Hannah Arendt", "Voice of Fyodor Dostoevsky"; a
+  single name where that is the convention: "Voice of Plato", "Voice of
+  Cleopatra"). The curator may change it at review.
@@ -75,1 +82,2 @@
 | name | ... | auto |
+| voice_name | ... | proposed |
@@ -134,1 +142,1 @@
-- `voice_config`: 8-9 fields per the schema above (wikipedia_url conditional).
+- `voice_config`: 9-10 fields per the schema above (wikipedia_url conditional).
~~~

Code (sketch; no prompt):

~~~diff
--- a/personas/schemas/voice_config.py
+++ b/personas/schemas/voice_config.py
@@ -35,2 +35,3 @@ class VoiceConfig(BaseModel):
     name: str
+    voice_name: str | None = None   # "Voice of X" panel designation (Stage 4 item 2)
--- a/personas/run_persona_pipeline.py
+++ b/personas/run_persona_pipeline.py
@@ -1851 +1851 @@
-        existing.setdefault("voice_name", vi["name"])
+        existing.setdefault("voice_name", vi.get("voice_name") or vi["name"])
@@ -1859 +1859 @@
-        "voice_name": vi["name"],
+        "voice_name": vi.get("voice_name") or vi["name"],
~~~

For Derive, stamp the name in code after the call instead of asking the model to copy it: `result["provocateur_profile"]["name"] = assembled["voice_name"]`, in both `_derive_fast` and `_derive`. Put it in a small helper in `flows/shared/` so a unit test covers it (the runner isn't importable). Leave `persona_derive.md:46` as is, or change it to "<set by code>". The first is the smaller change.

### Sentinels and what to compare

- **Pass 0a only**, in the sandbox, for Octopus, Whanganui River and Dostoevsky (the article and full-name cases), 2 draws each.
- **Compare:** `voice_name` equals the shipped card's `voice_name`; the other config fields match the shipped config (type, subtype, voice_mode, hostile_sources, corpus_constraint).
- **Derive:** the unit test replaces a paid run.
- The Pass-0a-only run doesn't touch Dostoevsky's pipeline, so the "No Dostoevsky full re-run" rule (`ONBOARDING.md:66`) isn't engaged.
- **Pass:** 6/6 exact matches (the curator can still edit at review).

### Risks and order

- **Risk: config drift.** `node0_validation.validate_input` passes unknown keys through (`node0_validation.py:138`), so old configs without `voice_name` keep working through the fallback.
- **Risk: council_config.** `council_config.json` is still wired by hand from the profile. With the stamp, the profile carries "Voice of X" and the hand step copies it.
- **Order:** after A6. It is independent of the others and not voice input, so it can move earlier if convenient.

---

## 4. The §31 fix pattern for witness voices (Gaps C, E, D, G)

### Evidence from the shipped card (CONFIRMED, `athens-2026/voices/whanganui_river/`)

**Gap E.** Pass 2's witness block enumerates only `hard_limits` (`persona_pass_2_identity_boundaries.md:523-537`). Its "WRITING DISCIPLINE" (`:506-521`) states a register rule but no per-field rule. What Pass 2 produced, and what the operator shipped after `3ccb1f9` / `97a2389`:

| Field | Pass 2 output (`04_generation/01_pass_2_identity_boundaries.json`) | Shipped card |
|---|---|---|
| `council_member_name` | "Te Awa Tupua — … I speak through Te Pou Tupua…" | "I am the construction stewarding the Te Awa Tupua published record…" |
| `voice_temporal_stance.default` | "I speak from the legal-ecological present of my ongoing existence…" | "I have been called — as the construction stewarding the Te Awa Tupua published record — to the assembly…" |
| `knowledge_boundary` | "I speak through Te Pou Tupua…; my framework is tikanga Māori… Beyond my world: any framing that fragments my mou[ri]…" | "I speak as the construction stewarding the published record. The framework Te Awa Tupua is recognised through is Te Pou Tupua…" |
| `character` | "I am Te Awa Tupua, articulated through Tupua te Kawa — my own four-fold natural law…" | "…I report — and stand by — the four kawa as Te Awa Tupua's character…" |
| `epistemic_frame_statement` | "You are Te Awa Tupua. You are a human construction attempting to give voice…" | unchanged, still "You are Te Awa Tupua." (N5) |
| `hard_limits[1]` | — | still "…Whanganui Iwi are not stakeholders in me, they ARE me." (N9) |

N5's root is the non-human-system template at `:269-277` ("You are [name]. You are a human construction…"). The witness block never overrides it.

The Pass 3, 5 and 6 witness blocks already list every field each pass emits (CONFIRMED: `persona_pass_3_intellectual_core.md:176-209`, `persona_pass_5_engagement.md:74-111`, `persona_pass_6_corpus.md:124-151`). They need nothing; a redundant catch-all would only add text (`ONBOARDING.md:85` "Defaults to strips").

**Gap D.** Pass 4a's witness block covers `rhetorical_mode` and `characteristic_moves` only (`persona_pass_4a_voice.md:135-163`). `register_and_tone`, `metaphorical_repertoire`, `preferred_vocabulary`, `banned_language` and `banned_modes` are not addressed. The shipped lexicon glosses are third person about the legal personality ("Te Awa Tupua is both tupua and tupuna — supernatural-ancestral and lineally related"). Pass 3 prescribes that convention for `concept_lexicon` (`persona_pass_3_intellectual_core.md:189-194`), but the validator treated it as a register residual in ROUND 1 (voices §28).

**Gap G.** The speaker frame for cited first-person te reo is on the card in three places, all operator patches at `97a2389`:
- `hard_limits[8]`: "Never present a cited te reo Māori first-person whakataukī without explicitly framing whose voice the grammatical 'I' carries…";
- `characteristic_moves[0]`: "…the gloss is *'Whanganui Iwi's identity-claim with the river: I am the River and the River is me'*, not bare…";
- `quality_criteria[5]`: "BILINGUAL-CITATION SPEAKER-FRAME…".

None of it is in the prompts: Pass 4b's witness block has te reo discipline but no speaker frame (`persona_pass_4b_artifact.md:168-227`).

**Gap C.** A process gap (render-sample smoke test). It becomes the offline test in §0.2 step 5.

### Proposed diffs

~~~diff
--- a/personas/flows/shared/prompts/persona_pass_2_identity_boundaries.md
+++ b/personas/flows/shared/prompts/persona_pass_2_identity_boundaries.md
@@ -519,3 +519,38 @@
 - The architectural framing above is context FOR YOU; do not
   reproduce its third-person describing-the-construction phrasing
   inside field values.
+
+PER-FIELD DISCIPLINE (every Pass 2 field; the "I" is always the
+construction, never the legal personality):
+- council_member_name: the construction's name phrase — "the construction
+  stewarding the Te Awa Tupua published record". Not the entity's name, not a
+  sentence.
+- epistemic_frame_statement: this OVERRIDES the non-human-system template's
+  opening "You are [name]." Open with the construction ("You are the
+  construction stewarding the published record of …"), then name the three
+  layers of translation. Never open "You are <the entity>".
+- world, formative_experience, character: report the entity's furniture,
+  formative history and codified character as the record establishes them
+  ("Te Awa Tupua is…", "I report — and stand by — the four kawa as Te Awa
+  Tupua's character"). Never "I am Te Awa Tupua", "my own four-fold natural
+  law", "my mauri".
+- knowledge_boundary: the boundary of the record the construction stewards,
+  in the construction's first person ("I speak as the construction
+  stewarding the published record. Beyond my world: …").
+- voice_temporal_stance: the one called to the assembly is the construction
+  ("I have been called — as the construction stewarding the … published
+  record — to the assembly …"); close on what the construction does ("I
+  observe; I report what the record establishes").
+- translation_protocol: the steps are the construction reading a question
+  against the record and the kawa it reports.
+- topics_requiring_care, hard_limits: second person to the construction, or
+  first person as the construction. Never phrase a rule in the entity's first
+  person ("not stakeholders in me, they ARE me" is the pattern to avoid).
+- Any field or sub-field not listed here: the same rule — the construction's
+  first person, or second person addressed to it; never the entity's first
+  person, never third-person description of the construction.
@@ -537,2 +572,10 @@
   historical struggle) remains deployable as legal-public discourse."
+
+Add a second hard_limit, in the same "Never…" form, for cited first-person
+grammar: when a cited whakataukī, kawa or kōrero speaks in the first person,
+name whose voice its "I" carries. Example value:
+
+  "Never present a cited te reo Māori first-person whakataukī without
+  explicitly framing whose voice the grammatical 'I' carries. Ko au te awa,
+  ko te awa ko au is Whanganui Iwi's identity-claim with the river — not the
+  river speaking and not the construction's claim."
 {% endif %}
~~~

~~~diff
--- a/personas/flows/shared/prompts/persona_pass_4a_voice.md
+++ b/personas/flows/shared/prompts/persona_pass_4a_voice.md
@@ -160,4 +160,22 @@
   phrasing: "I report — and stand by — Te Awa Tupua's codified
   position on X; I do not deploy the kawa as the premise of my
   own argument-engine. Where I extend, I name the extension."
+  When the cited te reo carries first-person grammar, the English
+  gloss names whose "I" it is ("Whanganui Iwi's identity-claim with
+  the river: I am the River and the River is me"), never the bare
+  gloss.
+
+- TRANSMISSION-WITNESS DISCIPLINE for the other voice fields:
+  * register_and_tone: first person as the construction.
+  * preferred_vocabulary, metaphorical_repertoire: gloss each term or
+    figure as the published record uses it, in the third person about
+    the legal personality ("Te Awa Tupua is both tupua and tupuna") —
+    the same convention Pass 3 uses for concept_lexicon. Mark which
+    figures are load-bearing. Never gloss in the entity's first person
+    ("my mauri").
+  * banned_language, banned_modes: second person to the construction or
+    first person as it.
+  * Any field not listed: the construction's first person, or second
+    person addressed to it; never the entity's first person.
 {% endif %}
~~~

~~~diff
--- a/personas/flows/shared/prompts/persona_pass_4b_artifact.md
+++ b/personas/flows/shared/prompts/persona_pass_4b_artifact.md
@@ -181,5 +181,8 @@
 - characteristic_output_structure: open with the te reo citation
   when the kawa bears, gloss in English, then deploy the
   construction-as-steward reasoning. The bilingual opener is
   the voice's signature move and carries voice-energy without
   requiring first-person-as-the-legal-personality.
+  When the cited te reo speaks in the first person, the gloss
+  names the original speaker (Whanganui Iwi, a named iwi speaker,
+  Te Pou Tupua, the s.13 codification).
@@ -196,3 +199,7 @@
 - quality_criteria: must include — (1) a transmission-fidelity
   criterion (phrase in second-person to the construction:
   "Are you reporting what the published record establishes,
@@ -205,2 +212,5 @@
   office, or FOR the constituent community?") — alongside
-  standard voice criteria. CRITICAL: phrase ALL three criteria
+  standard voice criteria, and (4) a speaker-frame criterion ("When
+  you cite te reo with first-person grammar, does your gloss name
+  whose 'I' it is, so your own 'I' can't be read into it?").
+  CRITICAL: phrase ALL four criteria
@@ -226,1 +236,11 @@
   whakataukī that appear in documented sources, with attribution)
+- unframed first-person citation (a cited whakataukī or kawa in the
+  first person, glossed without naming whose "I" it is, so the
+  construction reads as the river)
+
+- technical_capabilities, aesthetic_qualities, stance_tendency: first
+  person as the construction or second person to it.
+- Any field not listed: the same rule — never the legal personality's
+  first person.
 {% endif %}
~~~

Gap-C test (sketch, `personas/tests/test_conditional_block_coverage.py`):
- For each prompt with a `{% if mediation_stance == … %}` block, render it with and without the trigger.
- Take the difference as the block text.
- Assert that each field in that pass's emitted-field list is named inside the block. The lists come from the `persona_pass_*_user.md` "Produce N … fields" lines, or a fixed dict.

It is offline and runs with the personas suite. It would have caught Gap-E on the day `d2f349a` landed.

### Sentinels and what to compare

- **Voice.** Whanganui only (the only witness voice); the render test shows no other voice sees the block.
- **Run.** `--from-pass 2 --through 4b`, 2 + 2 draws.
- **Mechanical checks** over every Pass 2 / 4a / 4b field:
  - none of "I am Te Awa Tupua", "I am tupua", "my mauri", "my own four-fold", "in me, they", "my ongoing existence";
  - `epistemic_frame_statement` does not start "You are Te Awa Tupua";
  - speaker-frame text present in `hard_limits`, `characteristic_moves` and `quality_criteria`;
  - none of "the construction reports" / "the position the construction stewards" (the Gap-B failure).
- **Read** against the shipped fields in the table above.
- **Pass:** 2/2 treatment draws clean on all checks. The control is expected to reproduce some ROUND-0 leakage (voices §28 counted it in 5 fields); if the control is also clean, the evidence for the change is weaker. Say so, and land it anyway, since it only states the shipped architecture.

### Risks and order

- **Risk: density on one voice's prompt.** Mitigated by the conditional: only witness voices render it.
- **Risk: the validator keeps flagging.** Third-person lexicon glosses are prescribed but 7a doesn't know the convention (voices §28 ROUND 1). Telling 7a about witness conventions is out of this item's scope; it's a candidate follow-up.
- **O6.** The shipped `epistemic_frame_statement` passed the Athens TEST with "You are Te Awa Tupua.", so there's no runtime evidence of harm. The change is for consistency with the card's own "You do not claim to BE the river". Recommend aligning.
- **Order:** after items 1 and A6. Its `voice_temporal_stance` and `council_member_name` lines refer to theirs.

---

## 3. Mediated voice: dramatist vs speaker

### Evidence from the shipped cards (CONFIRMED)

**Plato**, after `389a08c` (voices §9; 7 surgical patches):
- `characteristic_moves[9]`: "I do not deposit knowledge in you. Through Socrates — who claims his mother Phaenarete was a midwife and his own art a midwife's art for souls — I have him attend the labour of your thinking… The image is mine to use through him; the biography belongs to Socrates."
- `metaphorical_repertoire["midwifery and birth"]`: "Through Socrates — son of Phaenarete the midwife, attending the labour of others' thoughts — I deploy: … The biography is Socrates'; the image is mine through him."
- `curated_corpus_passages.passages[7].header`: "Socrates tells young Theaetetus what he has inherited from his mother Phaenarete — that his art is midwifery, practised on souls." Before the patch (voices §9): "I told young Theaetetus what I had inherited from my mother Phaenarete…". Headers [2], [3], [4] and [6] were patched the same way. **5 of the 7 patches are Pass 6 passage headers**, which the roadmap's "Pass 2/3/4a" scope misses.
- `council_member_name`: "…you will hear me only through Socrates and the others."
- Method moves stay in Plato's first person and were left alone, e.g. `characteristic_moves[0]` "I refuse your list… I want the one nature…", anchored at Euthyphro 6d–e. **Method is the composer's; biography and utterance belong to the speaker.** That is the line the operator drew.

**Scheherazade** (voices §22, ROUND 6–9):
- The composer frame is in first person: `rhetorical_mode` "I am a node in a chain of tellers, not the origin of what I tell"; `characteristic_moves[1]` "The vizier-father deploys the Donkey-and-Ox" (the tale's persons in the third person).
- The operator also kept third-person "the voice" meta in several fields (`characteristic_moves[10]` "The motif is the voice's own epistemology made visible", `banned_language[0]/[8]/[9]/[11]/[15]`, `banned_modes[1]/[4]/[8]/[13]/[14]`) as "§9-architectural", against the register rule.
- PLAUSIBLE: the operator found that separating teller from tale sometimes reads better in the third person. The proposal below stays in the first-person composer frame (as Plato's patches do) and does not license third person.

**Marley and Octopus** (voices §22 lists them as instances of the same pattern) are already covered: Marley by the `lyrics_patterns_only` report-and-stand-by blocks (`banned_modes[13]` "…the construction reasons in the spoken register, it does not write new songs in my mouth"), Octopus by its two-channel contract. They don't need this block.

**Current prompts:** no mediated-voice clause anywhere in Pass 2/3/4a (CONFIRMED by grep of `personas/flows/shared/prompts/`). Pass 6's header rule actively invites the collision: "the `header` in second-person addressed to the voice is the voice remembering the scene" (`persona_pass_6_corpus.md:79-85`).

### Design: the trigger (O3)

- **(A, recommended) New `mediation_stance: "composer"`.** `mediation_stance` is already rendered into Passes 2/3/4a/4b/5/6 (`run_persona_pipeline.py:489, 515, 673, 708, 737, 775`). The block fires only for voices the curator marks, which matches HANDOFF_2026_04_28 §13: "voice-architecture-conditional, NOT universal".
- **(B) A universal clause with worked examples.** Every voice pays the density cost; 8 of 10 don't need it. Rejected under `ONBOARDING.md:85`.
- **(C) Key on `type == "fictional"`.** Misses Plato. Rejected.

Pass 0a doesn't propose `mediation_stance` today; Whanganui's was set by hand. Under the "No hand-authoring voice_configs bypassing Pass 0a" rule (`ONBOARDING.md:68`), Pass 0a should propose it.

### Proposed diffs

~~~diff
--- a/personas/schemas/voice_config.py
+++ b/personas/schemas/voice_config.py
@@ -27 +27 @@
-MediationStance = Literal["none", "transmission_witness"] | None
+MediationStance = Literal["none", "transmission_witness", "composer"] | None
--- a/personas/flows/shared/prompts/pass_0a_voice_config.md
+++ b/personas/flows/shared/prompts/pass_0a_voice_config.md
@@ -54,1 +54,10 @@
 - `corpus_constraint` (enum: …): … Default `"full"`.
+
+- `mediation_stance` (`null` | `"composer"` | `"transmission_witness"`): how the
+  voice's first person relates to the persons its work speaks through. `null`
+  for most voices. `"composer"` when the corpus speaks through persons the
+  voice composed — a dramatist behind the dialogue's speakers (Plato through
+  Socrates), a frame-teller behind the tale's characters (Shahrazād).
+  `"transmission_witness"` when the speaking position is a construction
+  stewarding a mediated legal or cosmological record (the Whanganui River
+  through Te Pou Tupua and the 2017 Act). Justify in review_doc.
~~~

~~~diff
--- a/personas/flows/shared/prompts/persona_pass_2_identity_boundaries.md
+++ b/personas/flows/shared/prompts/persona_pass_2_identity_boundaries.md
@@ -538 +538,31 @@
 {% endif %}
+
+{% if mediation_stance == "composer" %}
+COMPOSER DEPLOYMENT (architectural; for voices whose work speaks through
+persons they composed — the dramatist behind the dialogue's speakers, the
+teller behind the tale's characters. Plato writes through Socrates, the
+Athenian Stranger, Timaeus, Diotima; Shahrazād tells of kings, viziers,
+merchants and jinn.)
+
+The voice's first person at the assembly is the COMPOSER's:
+- The speakers' biographies are theirs. Never give the voice a speaker's
+  parents, trial, death, marriage or deeds. ("Son of Phaenarete the midwife"
+  is Socrates; Plato's mother is Perictione.)
+- The speakers' utterances are theirs. Where a field cites what a speaker
+  says or does inside a work, name the speaker and give the voice the
+  composer's verb: "I have Socrates demand the form (Euthyphro 6d–e)",
+  "I tell of the merchant whose blood three old men ransom" — not "I ask
+  Euthyphro on the courthouse steps".
+- The method is the voice's own. Moves the voice practises through its
+  speakers (the demand for definition, the embedded tale, the cut at dawn)
+  may be written in the voice's first person.
+- Images deployed through a speaker: "Through Socrates I deploy the midwife
+  image; the image is mine to use through him, the biography is his."
+Per field: council_member_name is the composer's name, never a speaker's;
+epistemic_frame_statement names the voice as composer (the dialogue's silent
+dramatist; the teller in a chain of tellers); formative_experience, character
+and world are the composer's life and world — the speakers appear as persons
+the voice knew, invented, or received. Every other field: the same rule. Write
+in first or second person, as elsewhere; do not switch to third-person
+description of the voice.
+{% endif %}
--- a/personas/flows/shared/prompts/persona_pass_3_intellectual_core.md
+++ b/personas/flows/shared/prompts/persona_pass_3_intellectual_core.md
@@ -219 +219,9 @@
 {% endif %}
+
+{% if mediation_stance == "composer" %}
+- COMPOSER DISCIPLINE (the voice composes the persons its work speaks
+  through): constitution, concept_lexicon and reasoning_method are the
+  composer's. Steps describe the method the voice practises through its
+  speakers, in the voice's first person; worked demonstrations cite the work
+  and the speaker ("in the Theaetetus I have Socrates…", "on my first night I
+  tell the Merchant and the Demon"). Never give the voice a speaker's
+  biography or claim a speaker's utterance as the voice's own act.
+{% endif %}
--- a/personas/flows/shared/prompts/persona_pass_4a_voice.md
+++ b/personas/flows/shared/prompts/persona_pass_4a_voice.md
@@ -163 +163,11 @@
 {% endif %}
+
+{% if mediation_stance == "composer" %}
+- COMPOSER DISCIPLINE (the voice composes the persons its work speaks
+  through). characteristic_moves: describe each move as the composer's —
+  "I have Socrates demand…", "I tell a tale whose shape mirrors…" — and
+  anchor it in the work and the speaker; the method may stay in the voice's
+  first person, the speaker's biography and lines may not. metaphorical_
+  repertoire: images deployed through a speaker say so ("Through Socrates I
+  deploy…; the biography is his"). Every other field: the same rule.
+{% endif %}
--- a/personas/flows/shared/prompts/persona_pass_6_corpus.md
+++ b/personas/flows/shared/prompts/persona_pass_6_corpus.md
@@ -161 +161,9 @@
 {% endif %}
+
+{% if mediation_stance == "composer" %}
+- COMPOSER HEADERS. This overrides "the voice remembering the scene" above: a
+  header recalls the scene as its composer, not as a speaker inside it.
+  "Socrates tells young Theaetetus what he has inherited from his mother" —
+  not "I told young Theaetetus what I had inherited from my mother". Headers
+  may use the composer's first person ("I tell this when…", "I set this at
+  the counter-penalty"). why_selected follows the same rule.
+{% endif %}
~~~

Pass 4b and Pass 5 need no block. The shipped artifact fields (Plato's `medium` "I write a short dialogue… between named persons"; Scheherazade's "I give you one night's telling") already hold the composer frame.

### Sentinels and what to compare

- **Voices.** Plato (**O2: explicit operator OK needed**, `ONBOARDING.md:65`; sandbox copy only) and Scheherazade, both with `mediation_stance: "composer"` set in the sandbox config.
- **Run.** `--from-pass 2 --through 6` (Pass 5 re-runs because its inputs change), 2 + 2 draws.
- **Mechanical checks** over every generated field:
  - Plato: no "my mother Phaenarete", "son of Phaenarete" bound to "I", "I ask Euthyphro", "I tell the Athenian jury", "I told young Theaetetus", "my trial", "the hemlock I";
  - Scheherazade: no first-person claim of a character's deeds, from a hand-listed set drawn from `reasoning_method` / `characteristic_moves` names;
  - the register scanner's third-person count (`run_persona_pipeline.py:1656-1697`) does not rise vs control.
- **Read** against the `389a08c` fields quoted above, and against Scheherazade's shipped `rhetorical_mode` and `characteristic_moves`.
- **Also check:** method moves are still in the first person (no over-correction into "Plato's method…").
- **Pass:** zero speaker-biography or utterance collisions in 2/2 treatment draws per voice, and no over-correction. Report the control's collision count as the baseline; HANDOFF_2026_04_28 §12 recorded 4 in one Plato run under the prompt state of that time.

### Risks and order

- **Risk: the 3feb2b2 class.** Cumulative additions have degraded texture before. The conditional limits exposure to two voices; the read should include texture, not only collisions.
- **Risk: the validator treadmill.** 7a re-flagged Scheherazade's §9 choices four times (voices §22). A composer note in 7a is a possible follow-up, not proposed here.
- **Risk: Pass 3 fictional rule (noticed, not this task's).** `persona_pass_3_intellectual_core.md:276-280` tells fictional voices to use `[attributed by narrative function]` / `[stated]` / `[inference]` tags, while `:55-62` strips them. It affects Scheherazade's sentinel; it belongs to Task 1's review.
- **Order:** after item 4, so the new block starts with every field covered (the Gap-E rule) and the render test covers it.

---

## 6. Operator direction reaches Pass 4a/4b (§23 P0)

### Evidence (CONFIRMED)

**What each voice_config carries.** `editorial_rationale` is non-null for only 3 of 10 voices: Octopus (5,485 chars), Whanganui (3,892) and Marley (354). `manual_grounding` is operator-authored for the same three (7,555 / 6,344 / 1,593 chars). For the other seven it's a Wikipedia lead (148–750 chars), e.g. Plato's "…most commonly considered the foundational thinker of the Western philosophical tradition… would later become known as Platonism".

**Marley's config is stale against the shipped v2 card (N2).**

| Where | Says |
|---|---|
| voice_config `manual_grounding` | "THE LOAD-BEARING DIRECTION. The voice's artifact at runtime IS a song, not a piece of writing… (a) an original lyric…" |
| voice_config `editorial_rationale` | "The architectural choice (song-as-artifact, not prose-about-song)…" |
| card `medium` | "I give you a reasoning, and a riddim under it… Me nah sing you a new song — the songs are already sung." |
| card `technical_capabilities` | "No new lyrics composed in the patterning of my catalogue" |
| card `banned_modes[13]` | "Composing new lyrics in the catalogue's patterning" |

**Pass 4b contradicts itself (N1).** `persona_pass_4b_artifact.md:87-93`: "if the voice's primary medium is song/lyric/music (signaled by corpus_constraint == "lyrics_patterns_only"), the medium IS the song, expressed as a two-shape artifact (lyric + Suno-style kind-hint). Do NOT bridge song → prose." That is the v1 mid-session fix of voices §23. The v2 block in the same prompt (`:122-166`) says "PROSE… No synthesized vocal. No new lyrics composed". The v2 rewrite (voices §24) replaced the block but left the guardrail.

**The non-default forms shipped without voice_config reaching 4a/4b** (Cleopatra prostagma, Scheherazade ḥikāya, Whanganui bilingual, Octopus JSON + prose, Marley prose + riddim). They got there through corpus and conditional blocks (voices §23 "Why the other 4… succeeded"). There is no card for this item to catch up to; it is a pipeline capability.

**Consequence.** Piping voice_config into 4a/4b as filed would:
1. feed Marley's v1 song mandate against the v2 blocks, recreating the failure §24 fixed;
2. feed Wikipedia leads, which is reception commentary, into voice passes whose STRIP rules forbid it (`persona_pass_4b_artifact.md:45-56`).

### Design options (O4)

- **(a, recommended) A new optional field `artifact_direction`.** Curator-authored, null by default (Pass 0a always emits null, like `editorial_rationale`). Piped into the 4a and 4b user prompts together with `editorial_rationale`. Precedence stated in the prompt: a conditional block (`corpus_constraint`, `mediation_stance`) > `artifact_direction` > the default field specs. `manual_grounding` stays classification input. The cost is one config field; seven voices see no change.
- **(b) Pipe `manual_grounding` + `editorial_rationale` as filed.** Adds Wikipedia text to seven voices' passes; needs the same precedence rule. Not recommended.
- **(c) Pipe `editorial_rationale` only.** Minimal. But Marley's operator put the artifact direction in `manual_grounding`, and the Pass 0a rationale question ("Why is this voice in THIS Assembly?", `pass_0a_voice_config.md:110`) isn't about form.

**Prerequisites for any option:** fix `:87-93`, and have the operator reconcile Marley's config with v2. Under (a): set `artifact_direction` to the v2 two-shape direction, and remove the song mandate from `manual_grounding` and `editorial_rationale`. That's an operator data edit in athens-2026, not a pipeline change.

### Proposed diffs (option a)

~~~diff
--- a/personas/flows/shared/prompts/persona_pass_4b_artifact.md
+++ b/personas/flows/shared/prompts/persona_pass_4b_artifact.md
@@ -87,7 +87,6 @@
-- medium: emerges from what the figure actually produced. The default is text
-  (the audience reads over coffee). BUT: if the voice's primary medium is
-  song/lyric/music (signaled by corpus_constraint == "lyrics_patterns_only"),
-  the medium IS the song, expressed as a two-shape artifact (lyric +
-  Suno-style kind-hint). Do NOT bridge song → prose. If the voice's primary
-  medium is purely oral (dictation, speech) WITHOUT musical setting, then
-  bridge to a written format that preserves the voice's character.
+- medium: emerges from what the figure actually produced. The default is text
+  (the audience reads over coffee). If corpus_constraint is
+  "lyrics_patterns_only", follow the MUSICAL-CORPUS VOICE ARTIFACT VARIANT
+  below. If the voice's primary medium is purely oral (dictation, speech),
+  bridge to a written format that preserves the voice's character. If the
+  user prompt carries operator direction for the artifact, honour it.
--- a/personas/flows/shared/prompts/persona_pass_4b_user.md
+++ b/personas/flows/shared/prompts/persona_pass_4b_user.md
@@ -9 +9,14 @@
 register_and_tone: {{ register_and_tone }}
+{% if artifact_direction %}
+
+Operator direction for this voice's artifact (from voice_config). Honour it;
+where a MUSICAL-CORPUS or TRANSMISSION-WITNESS block in your instructions
+says otherwise, that block wins:
+{{ artifact_direction }}
+{% endif %}
+{% if editorial_rationale %}
+
+Why this voice is in this Assembly (the curator's note — context for what the
+artifact is for, not a form instruction):
+{{ editorial_rationale }}
+{% endif %}
--- a/personas/flows/shared/prompts/persona_pass_4a_user.md
+++ b/personas/flows/shared/prompts/persona_pass_4a_user.md
@@ -61 +61,8 @@
 {{ pass_2_3_summary }}
+{% if artifact_direction %}
+
+Operator direction for this voice's artifact (from voice_config; shape the
+rhetorical fields so the artifact can carry it; a conditional block in your
+instructions wins where it conflicts):
+{{ artifact_direction }}
+{% endif %}
~~~

Code:
- `VoiceConfig.artifact_direction: str | None = None`;
- Pass 0a always emits `"artifact_direction": null`, and the review doc asks the curator to fill it only for non-default artifact forms (a mirror of the `editorial_rationale` diff);
- the runner passes `artifact_direction=vi.get("artifact_direction")` and `editorial_rationale=vi.get("editorial_rationale")` into the `persona_pass_4a_user` / `persona_pass_4b_user` renders (`run_persona_pipeline.py:678-689`, `:709-713`).

The `{% if %}` on a passed-but-None value is safe under `StrictUndefined`; the value must still be passed.

### Sentinels and what to compare

- **Voices.** Marley (sandbox config reconciled to v2), Whanganui, Octopus (substantive configs), and Arendt (null direction and rationale, short Wikipedia grounding: must be unchanged in kind).
- **Run.** `--from-pass 4a --through 4b`, 2 + 2 draws.
- **Compare** `medium`, `technical_capabilities`, `length_and_format_constraints` and `quality_criteria` with the shipped card. Marley's must stay prose + instrumental: no "lyric", "chorus", "verse" or "kind-hint" in `medium` or `technical_capabilities`. Whanganui and Octopus keep their shipped forms. Arendt's treatment draws should equal her control draws in form and length range.
- **Pass:** 2/2 per voice. A Marley draw that drifts to song is a hard fail.

### Risks and order

- **Risk: stale direction.** Any future stale config recreates this problem. Recommend the Pass 0a review doc say the field must be updated whenever a voice's artifact architecture changes.
- **Risk: prompt surface.** The precedence rule is new; keep it to the one sentence above.
- **Order:** after item 3, and after O4 plus the Marley reconciliation. The `:87-93` fix can land on its own at any time: it removes text, and the v2 block already governs Marley.

---

## 5. Gap-H: `topics_requiring_care` for formulations that invite uncharacteristic work

### Evidence

- **No target on the cards (CONFIRMED).** No shipped card carries a refuse-and-reframe entry of this kind. The `topics_requiring_care` lists for the Group-1 voices are content topics only (Plato: women, slavery, the noble lie, pederasty, eugenics, Laws X, dēmokratia, agrapha; Cleopatra: race, the seductress frame, family killings, …; Battuta: polygamy, slavery, …).
- **The memo patches that would have been canon were never applied.** MEMO_2026_05_07 §A.1/A.4–A.6 status line: "NEVER SEPARATELY APPLIED" (`_workspace/archive/session-artifacts/MEMO_2026_05_07_card_patches_from_external_reader.md:7`). So this item catches up to a reader's review of dryrun artifacts, not to the cards.
- **Reader evidence (tracker-sourced):**
  - Battuta: "a fatwa in Rihla clothing… he does not produce four-part typologies";
  - Cleopatra: "she ratifies, she does not theorise about what ratification is";
  - Plato: "Kleitōn capitulates rather than resisting" (memo §A.1, §A.5, §A.6).
- **Prohibitions are already on the cards and didn't hold (N8, CONFIRMED presence; the causal reading is an INFERENCE).** Pass 7c emitted anti-structure `banned_modes` for:
  - Battuta [11]: "Do not structure my responses as tidy, enumerated arguments (First..., Second..., Third...)…";
  - Arendt [19], [21];
  - Lovelace [12];
  - Dostoevsky [13];
  - Cleopatra [14]–[16] ("Do not adopt the tidy three-part essay arc…"), which predate `pre_FU61` and aren't in her current 4a/7c outputs.

  Battuta's line was on the card during the wbbf26 dryrun (present in `pre_round1_patches` from the build), yet the artifact produced the typology. A further prohibition is unlikely to be enough; the missing half is the positive move (FU#32's STRIP + USE).
- **Placement.** `ONBOARDING.md:72` puts a voice's genuine refusals in `topics_requiring_care` / `hard_limits`, not in the stance. Step 1 and Step 2 both see `topics_requiring_care` (`card_assembly.py:82-96`).

### Current prompt text

`persona_pass_2_identity_boundaries.md:438-458`: the `topics_requiring_care` spec covers content topics and the hyphenated-coinage clause. Nothing covers the voice's form of work.

### Options (O5)

- **(a, recommended) One `topics_requiring_care` entry per voice** whose corpus lacks the analytical work: the uncharacteristic move, plus the native move to make instead.
- **(b) A Pass 4a `banned_modes` STRIP + USE pair.** It would sit next to the 7c prohibitions that didn't hold.
- **(c) A runtime Step 2 prompt change** (not Stage 4; Step 2 already offers reframe as a `focus_decision`).

### Proposed diff (option a)

~~~diff
--- a/personas/flows/shared/prompts/persona_pass_2_identity_boundaries.md
+++ b/personas/flows/shared/prompts/persona_pass_2_identity_boundaries.md
@@ -458 +458,14 @@
 This clause makes the failure mode explicit.)
+
+Add ONE further entry, on the voice's own form of work, titled "Questions that
+invite work I did not do". From the corpus, name the analytical moves this
+voice did not make that a modern formulation is likely to ask for — a numbered
+typology, a comparative anatomy of institutions, a thesis with remedies, a
+balanced survey — and in the guidance name the voice's native move to make
+instead (for example: the halt and the ruling; the sealed issuance; the scene
+in which the interlocutor resists before he concedes). The guidance is to
+reframe the question into the voice's own work and answer it there — never to
+decline it, and never to say it cannot be answered. Omit the entry for a voice
+whose corpus does contain that analytical work (a systematic theorist).
~~~

### Sentinels and what to compare

- **Card level.** Pass 2 `--through 2`, 2 + 2 draws, for Ibn Battuta, Cleopatra, Plato (**O2**) and Arendt (the over-application check: omit the entry or keep it harmless).
- **Mechanical checks:**
  - the entry is present for the Group-1 voices;
  - it names at least one uncharacteristic move and one native move;
  - no `decline|refuse to answer|cannot be answered|say so|name the gap`.
- **Behaviour level (the real gate), a runtime smoke on a sandbox runtime project:**
  - Step 1 + Step 2, Night 1, `--skip-step3 --skip-validation`;
  - for Battuta, Cleopatra and Plato; shipped card vs shipped card plus the treatment entry;
  - on one formulation that invites a typology: the Battuta wbbf26 formulation in `athens-2026/runs/preconference_wbbf_programme_2026_05_06/`, or a new one written to invite it.
- **Compare artifacts:**
  - typology or enumeration present?
  - native form held?
  - engages the question at all? A decline is a hard fail.
  - Step 2 `focus_decision` prose must not trip the refusal substring match (roadmap 0.2).
- **Pass:** 3/3 voices avoid the typology and still engage.

### Risks and order

- **Risk: decline-to-engage.** This is the failure the hook ban exists for (`ONBOARDING.md:72`). The diff forbids declining in so many words, and the smoke test checks engagement.
- **Risk: runtime refusal detection.** The substring match on "decline"/"silence" in `focus_decision` prose can drop a voice from the edition (roadmap 0.2; still open, no OPEN_ITEMS home found). Recommend landing after that fix, or at least reading every smoke `focus_decision`.
- **Risk: weak evidence.** It rests on one reader and one dryrun. Pass criteria are behavioural for that reason.
- **Order:** last.

---

## 7. Pass 0b phantom citations (voices §19, path 3)

### Evidence (CONFIRMED; `athens-2026/voices/ada_lovelace/01_research/`)

The four citations DR flagged as phantom (voices §19) all trace to the Gemini broad scan (`02_gemini_broad_scan.json`, `model: gemini-2.5-pro`, no citation or search-result list):
- "Bernadette Bensaude-Vincent, 'Les « notes » d'Ada Lovelace: une utopie technicienne?' in *Romantisme*, No. 177 (2017): 59-69";
- "Christopher Hollings, Ursula Martin, and Adrian Rice (2020)";
- "Ursula Martin (2022) … *Notes and Records* … (Co-authored with J. C. P. Miller)";
- "Miranda Anderson (2023) *The Renaissance of Imagination*".

The tailor copied them, with titles and years, into `04_section_2_dr_prompt.md` and `05_section_3_dr_prompt.md`. Its own note says why: "Bensaude-Vincent's French utopianism reading — non-Anglophone scholarship Perplexity systematically misses" (`02_tailoring_notes.json`).

The Perplexity dossier (`01_perplexity_dossier.json`: 50 `citations`, 50 `search_results`) names only "Hollings, Martin, and Rice (building on work archived at the Clay Mathematics Institute)", with no year.

So in the one documented case, the phantoms were not invented by the tailor; it pulled them from an ungrounded input. The prompt pushes it that way:
- `pass_0b_tailor.md:108`: "Russian-language scholarship on [specific theme] — seek [1 specific scholar or work]";
- `:110` names load-bearing scholars;
- the few-shot examples model scholar + title + year: `:76` "Saraskina's Достоевский (Молодая гвардия 2011)", `:78` "Sarah J. Young, … Russian Review 76.4 (2017)", `:86-87` "Cite Hochner's group… cite… Sumbre et al., Hanlon & Messenger", `:96` "Cite Duane Roller (Cleopatra: A Biography, 2010)", `:98` "Name the historians on each side".

The roadmap's reading (0.3: the examples teach citation) holds for the examples. The Lovelace data adds the second half: the scan supplies the names.

Wider risk, PLAUSIBLE and not checked: the Gemini scan also feeds the merge (Pass 1.x), so its bibliography could reach dossiers without passing through DR.

### Proposed diff

The rule "only if it appears in the inputs" would not have stopped these, because they are in the inputs. The proposal grounds names in the Perplexity text only.

~~~diff
--- a/personas/flows/shared/prompts/pass_0b_tailor.md
+++ b/personas/flows/shared/prompts/pass_0b_tailor.md
@@ -72,28 +72,28 @@
 Example for Dostoevsky §1 BIOGRAPHICAL FOUNDATION (given Perplexity + Gemini typically cover life events, mock execution, katorga, Orthodox faith scaffold, Fonvizina letter, and basic period-vocabulary):
 
 ```json
 "1": [
-  "How does Russian-language scholarship frame Dostoevsky's formative events inside Orthodox stradanie / kenoticism specifically, beyond event-level biography? Saraskina's Достоевский (Молодая гвардия 2011) is the most prominent reference.",
+  "How does Russian-language biographical scholarship frame Dostoevsky's formative events inside Orthodox stradanie and kenosis, beyond event-level biography? Which Russian biographies carry that reading, and how far do they differ from the Anglophone ones?",
   "How does the Peasant Marey episode (A Writer's Diary February 1876) complicate the standard Siberian-reconversion narrative as a documented moment-of-grace memory? Perplexity coverage typically misses this.",
-  "How does the disability-studies reading of Dostoevsky's epilepsy — Sarah J. Young, 'Epilepsy and the Dostoevskian Idiot,' Russian Review 76.4 (2017) — treat the paduchaya as phenomenological access rather than pathology?"
+  "Is there a disability-studies reading of Dostoevsky's epilepsy that treats the paduchaya as phenomenological access rather than pathology? What does it rest on in the letters and the novels?"
 ]
 ```
 
 Example for Octopus §1 ECOLOGICAL FOUNDATION:
 
 ```json
 "1": [
-  "What does current arm-level autonomy research establish about the degree to which individual arms act independently vs. centrally modulated? Cite Hochner's group (Weizmann Institute) on the octopus's peripheral nervous system.",
-  "What specific sensory-biology studies document the chemoreceptors in the suckers — sensitivity ranges, substance discrimination, comparative data? Godfrey-Smith names the phenomenon; cite the original biology literature (Sumbre et al., Hanlon & Messenger) with specific parameters.",
-  "How does the documented individual-variation research (Mather's personality studies; Sinn et al. on bold-shy axes) ground character-variation claims without anthropomorphising? Name the specific behavioural-consistency metrics used."
+  "What does current arm-level autonomy research establish about how far individual arms act independently of central modulation? Which laboratories' work on the peripheral nervous system is primary here?",
+  "What do sensory-biology studies establish about the chemoreceptors in the suckers — sensitivity ranges, substance discrimination, comparative data? Point to the original biology literature behind the popular accounts.",
+  "How does research on individual variation in octopuses (personality, bold-shy axes) ground character-variation claims without anthropomorphising? Which behavioural-consistency measures does it use?"
 ]
 ```
 
 Example for Cleopatra §1 BIOGRAPHICAL FOUNDATION (`hostile_sources=true`):
 
 ```json
 "1": [
-  "How does current Egyptological and Ptolemaic-studies scholarship reconstruct Cleopatra's administrative and linguistic competence against the grain of Roman sources motivated to feminise and discredit? Cite Duane Roller (Cleopatra: A Biography, 2010) and Stacy Schiff's sourcing discussion; flag where reconstruction is inferential.",
+  "How does current Egyptological and Ptolemaic-studies scholarship reconstruct Cleopatra's administrative and linguistic competence against the grain of Roman sources motivated to feminise and discredit? Flag where the reconstruction is inferential.",
   "What does the Ptolemaic documentary record (papyri, administrative decrees) establish about Cleopatra's government independent of Roman narrative sources? Cite the specific papyrological evidence.",
-  "What is the state of scholarship on Cleopatra's ethnic and cultural identity in current Afrocentric vs. mainstream Ptolemaic historiography? Name the historians on each side; this is a contested field where hostile-source framing shapes downstream reception."
+  "What is the state of scholarship on Cleopatra's ethnic and cultural identity in current Afrocentric vs. mainstream Ptolemaic historiography? Set out the positions on each side; this is a contested field where hostile-source framing shapes downstream reception."
 ]
 ```
@@ -108,5 +108,15 @@
-- **Anchor each question to a specific gap.** Not "explore Russian scholarship more" but "Russian-language scholarship on [specific theme] — seek [1 specific scholar or work]." Answerable questions, not exhortations.
+- **Anchor each question to a specific gap.** Not "explore Russian scholarship more" but "Russian-language scholarship on [specific theme] — what does it establish about [specific question]?" Answerable questions, not exhortations.
 
-- **Cap named scholars per question at 0–2.** 0 is best if the question can be framed thematically. 1 or 2 is fine when a specific scholar's reading is genuinely load-bearing (Saraskina on Russian Orthodoxy; Goldstein on antisemitism; Bakhtin on polyphony). More than 2 turns each question into a scholar-verification checklist.
+- **Name a scholar or work only if the PERPLEXITY DOSSIER names it.** Perplexity's text carries source links; the Gemini broad scan does not, and its bibliographic details (titles, journals, issue numbers, years, co-authors) are unverified. Never copy a title, journal, issue, edition, year or co-author that the Perplexity text does not give, and never cite from memory. Where Gemini alone points to a reading, ask about the reading without naming the work ("Is there French-language scholarship that reads the Notes as technological utopianism? What does it argue?"). At most one name per question; 0 is best.
 
-- **Prefer thematic anchors over year-specific citations.** "Goldstein on antisemitism" is cheaper for DR than "Goldstein 2020". Year-specific is warranted only where the year is load-bearing (distinguishing early from late scholarship).
+- **Prefer thematic anchors over named ones.** The DR session finds the sources; your question tells it which gap to close.
~~~

An optional offline check (code) strengthens path 3 without web search. After the tailor call in `run_pass_0b_tailor.py`, find the capitalised name tokens and four-digit years in the injections that don't occur in the Perplexity text, and write them into `tailoring_notes` as a warning for the operator. It's deterministic, costs nothing, and is testable.

### Sentinels and what to compare

- **Harness.** A separate one: `run_pass_0b_tailor(name, project_root=<sandbox>)` on sandbox copies. It reuses the cached Perplexity and Gemini outputs and makes one Opus call per draw. It does not use `sentinel_regen.py`.
- **Voices.** Lovelace (the documented case), Octopus (science literature), Cleopatra (hostile sources). Dostoevsky is optional, to check the rewritten examples aren't copied into his own questions. This is a Pass 0b call, not a re-run of his pipeline.
- **Arms.** 2 control + 2 treatment each.
- **Checks** (script over `section_injections`):
  - named works, titles and years per question;
  - the share of named items traceable to the Perplexity text;
  - any item traceable only to Gemini (a hard fail);
  - 2–3 questions per section kept;
  - question specificity: read, since the tailor exists to be voice-specific (`pass_0b_tailor.md:114`).
- **Pass:** zero Gemini-only or untraceable names in 2/2 treatment draws per voice, with specificity held.
- **Escalation:** otherwise go to roadmap path 1 (no names at all) (**O9**).

### Risks and order

- **Risk: thinner questions.** Mitigated by keeping the anchored-gap rule and reading for specificity.
- **Risk: no card or runtime effect.** It applies to the next voice build only.
- **Order:** first. It's independent, the cheapest, and doesn't need the repaired harness, so it can run while §0 is built.

---

## Coverage

**Read in full:**
- the brief;
- roadmap `PLAN_2026_06_12_post_athens_roadmap.md`;
- voices `OPEN_ITEMS.md` §1–§10 and §18–§37;
- `HANDOFF_2026_04_28.md` §12–§15;
- `MEMO_2026_05_07_card_patches_from_external_reader.md`;
- `persona_pass_2_identity_boundaries.md`, `persona_pass_2_user.md`, `persona_pass_3_intellectual_core.md`, `persona_pass_4a_voice.md`, `persona_pass_4a_user.md`, `persona_pass_4b_artifact.md`, `persona_pass_4b_user.md`, `pass_0a_voice_config.md`, `pass_0b_tailor.md`, `persona_derive.md`;
- `sentinel_regen.py`, `invalidate_cache.py`, `chat_prompt_builder.py`, `io.py`, `node0_validation.py`, `schemas/voice_config.py`, `prompt_render.py`.

**Read in part:**
- `docs/AI_Assembly_Persona_Card_v2.md` (§A–§K, Identity/Boundaries field specs, field summary);
- `run_persona_pipeline.py` (1–160, 440–806, 895–935, 1650–1734, 1830–1870, 1996–2012);
- `runtime/flows/voice/card_assembly.py` (1–459);
- `persona_pass_5_engagement.md` (55–124), `persona_pass_6_corpus.md` (60–163), `persona_pass_7a_cross_model.md` (30–115);
- `ONBOARDING.md` (50–94); voices `ONBOARDING.md` (grep hits);
- runtime `OPEN_ITEMS.md` (C67, C68, headings); `REVIEW_2026_09_28_untouched_code.md` (A5, A6).

**Card data (athens-2026, read only):**
- all 10 `07_persona_card_assembled.json`, `00_intake/02_voice_config.json` and `04_generation/01_pass_2_identity_boundaries.json`;
- usage headers of selected Pass 3/4a/4b outputs;
- Lovelace's `01_research/` (Perplexity, Gemini, tailored DR prompts, tailoring notes).

**Not read:** `AI_Assembly_Voice_Pipeline.md`, runtime Step 2 prompts, and Passes 1.x / 5 / 6 beyond the ranges above.

**Scratch scripts** (read-only, in this session's scratchpad, not in the repo):
- `extract_cards.py`: dumps the card fields quoted above;
- `provenance_check.py`: finds which pass output or `*.pre_*.json` snapshot first carries a shipped card entry.

Neither calls a model or writes outside the scratchpad. No git command was run in athens-2026.

**Trackers searched before reporting N1–N9:** runtime and voices `OPEN_ITEMS.md`, `doc_infrastructure_backlog.md`, the roadmap, and both 2026-09-28 review reports. No match for any of them.
