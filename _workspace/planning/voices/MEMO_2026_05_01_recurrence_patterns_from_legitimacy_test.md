# Memo: voice-card observations from the legitimacy test

**To:** persona / voices thread
**From:** runtime thread
**Date:** 2026-05-01
**Re:** four voice-side findings worth voice-card consideration before Athens
**Test artifacts:** `projects/current-tests/voice-pipeline-dryrun/runs/legitimacy_test1_night{1,2,3}/` + `legitimacy_test2_single_night/` + `legitimacy_test2_v2_divergent_titles/`
**Test report:** `voice-pipeline-dryrun/legitimacy_test_report.md`

The runtime thread ran a multi-test exercise on the 4 shipped voices (Plato, Cleopatra, Dostoevsky, Battuta) using mock formulations on legitimacy / recognition / public-realm questions. Five Step 2 artifacts per voice across the runs. The pipeline machinery checked out (continuity flow + Convention A verified end-to-end after a bugfix in `voice_flow.py:458`). What did NOT check out cleanly are some voice-card-side patterns. These are persona-thread territory.

---

## 1. Plato — `Socrates referencing his own death` anachronism 🔴 (the sharpest finding)

**Observed in:** Test 1 Night 3 Step 2 artifact only (1 of 5 Plato artifacts).

**The artifact opens:** *"I was walking up from the Cephissus toward the Academy when I met Charmides — not the famous one, but a younger man of the same name..."*

The "I" is Socrates (Charmides addresses him as "Socrates"). Mid-dialogue, Socrates asks Charmides:

> *"Charmides — the assembly that voted Socrates' death, was that public life?"*

And later:

> *"by mine it was the day the most just man I knew was killed by counted opinion"*

Two layers of anachronism: (a) Socrates references his own death as a past event from within his own lifetime; (b) Socrates speaks of himself in third person ("Socrates' death", "the most just man I knew"). The validator (Pass 7-anachronism) would catch this — that's its purpose — but Test 1 ran with `--skip-validation`.

**Pattern observed across all 5 Plato artifacts:** when the narrator is **someone other than Socrates encountering Socrates** (Test 1 N1, N2; Test 2; Test 2 v2), no anachronism. When the narrator IS Socrates first-person (Test 1 N3 only), Plato's authorial post-Socrates vantage leaks into Socrates' voice.

**Recommendation:** voice-card constraint on Plato — either:
- `quality_criteria`: "When Socrates is the first-person narrator, treat his temporal vantage as living-Socrates; do not let Plato's post-Socrates knowledge (the trial, the death, the cup) bleed into Socrates' speech."
- `banned_modes`: "Socrates referring to his own death as past event" / "Socrates speaking of himself in third person."
- Or constrain narrator-choice: "Plato writes Socrates as encountered by another character (Glaucon, Antiphon, Phainias), not as first-person narrator." (Easiest to enforce; matches the pattern that worked in 4/5 Plato artifacts.)

Athens production policy per A1 has validation ON Night 1 / OFF Nights 2+3 (FU#62 path B). Without this voice-card guard, similar anachronism on Night 2 or 3 would land in published artifacts.

---

## 2. Plato — Theuth/Thamus reach 🟡

The Phaedrus / writing-cannot-answer-when-questioned move appears in:
- Test 1 N1 Step 1 (algorithmic governance angle)
- Test 1 N2 Step 1 (recognition angle)
- Test 2 synthesis (across all 3 formulations)

Canonical Plato — historically accurate, voice-true. The risk is recurrence at Athens scale: with 9-12 briefings landing on Plato across 3 nights, if 6+ reach for Theuth/Thamus the audience will notice it as a tic rather than a move.

**Three resolution paths:**
- (A) Voice-card flag — instruct against Theuth/Thamus on consecutive nights.
- (B) Continuity overlay carries a "moves already used this conference" register; voice avoids repeating within ~3 briefings.
- (C) Accept as a Platonic tic the audience would recognize as canonical — but make this deliberate (operator note in HoBB editorial / Substack walkthrough framing).

Operator decision per voice; no runtime-side change needed.

---

## 3. Ibn Battuta — Tughluq beard-plucking anecdote 🟡

The Shaykh Shihāb al-Dīn al-Dīn beard-plucking (under Muhammad bin Tughluq) appears in **both Test 1 N1 and N2 Step 1** with very similar phrasing. Stock anecdote risk.

Same three resolution paths as Plato — voice-card guard, continuity-overlay "stock examples used" register, or accept as Battutan tic.

---

## 4. Dostoevsky — closing on suspended judgment 🟡

Two close-enough closings to flag:
- Test 1 N2 artifact ends: *"they have not yet earned the right to answer it"*
- Test 2 synthesis ends: *"any justice was ever made"*

The move-shape (closing on suspended judgment) is correct for Dostoevsky. The specific phrasing risks calcifying into a verbal tic across more nights.

**Path:** voice-card flag for closing-phrase variation; or accept the suspended-judgment shape as a Dostoevskian closing register.

---

## Pipeline-side observations (FYI — not requesting persona-thread action)

For context on what's already in motion:

- **Continuity-after-Step-2 bugfix** landed (`voice_flow.py:458`, commit `ccc6229`). Without it, Athens N2/N3 would have launched with no continuity carried forward.
- **Thinking-tokens-always-0 bugfix** landed across both pipelines (commit `8c47e1f`). This affects persona pipeline observability too — `manifest.json` token rows now report real billed thinking tokens via `count_tokens` subtraction.
- **Test 2 synthesis bias.** All 4 voices chose `focus_decision: "woven across all three"` even with distinct theme_display_titles (Test 2 v2). Each voice articulated a unifying through-line in their own grammar. Diagnosis: voices with rich conceptual machinery default to synthesis when content converges. To test the focus-on-one branch cleanly would need Test 3 with formulations on substantively-different conceptual territories.

---

## Suggested handoff form

Path of least friction: persona thread reads the test report (`legitimacy_test_report.md` in voice-pipeline-dryrun/, ~423K markdown), considers each of the 4 findings, and decides per-voice resolution. Most should be small voice-card patches at most. The Plato Socrates-death anachronism is the only one I'd suggest treating as load-bearing for Athens (operator-discovered the validator would catch it on N1 but not on N2/N3).

`_workspace/planning/runtime/OPEN_ITEMS.md` C20 cross-references this memo. No runtime-side action items pending here — all four findings are voice-card territory.

—runtime thread
