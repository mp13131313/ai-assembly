# Stage 4 prep — prompt changes for the backport (drafted, not applied)

**Task:** Task 2 of `_workspace/planning/BRIEF_2026_09_28_fable_batch.md` (roadmap Phase 1.1, items 1–7, plus voices §37 A6).
**Written:** 2026-09-28, Fable 5.1 session. **Revised twice on 2026-09-30:** after the Opus review (`_workspace/planning/REVIEWS_OF_FABLE_DELIVERABLES_2026_09_29/02_stage4_design.md`), and again when the operator lifted the Stage 4 spend cap. Every change is listed in the revision log at the end.
**Status:** proposals only. Nothing in this doc is applied. No model was called. The shipped cards were read, not written.
**Base:** `main` at `86998b4`. All `file:line` references and all diffs are against that commit. The files the patches touch are unchanged on `main` at `e674893` (checked 2026-09-30). `athens-2026/…` means `/Users/aienvironment/Desktop/AI Assembly/projects/athens-2026/…`.
**Labels:** CONFIRMED = read in the file or data named, or run offline. PLAUSIBLE = an inference, marked as one.

---

## Summary (one page)

**Outcome.** Eight prompt changes are drafted as nine patches (item 3 is split in two). The patches are real `git diff` output; they pass `git apply --check` against `main`, in order. Two test plans are costed below (§0.4). The operator chooses between them.

| | **Plan A — best for quality** | **Plan B — best value** |
|---|---|---|
| Idea | Several draws per arm, fresh controls, every variant, then rebuilt cards and a runtime comparison | One treatment draw for every part of every patch, a free control, and one end-state voice |
| Draws per check | 3 treatment + 2 fresh control (the athens-2026 output is a third control) | 1 treatment; control = the athens-2026 pass output |
| Items 1 and A6 | separate draws (strict one at a time) | one shared Pass 2 draw |
| Voices | 10: every variant, and two voices for the composer block | 8: one voice per variant |
| End state | 5 voices rebuilt from Pass 2 through 7a FINAL, plus 2 rebuilt on the unpatched prompts; cards diffed field by field | Whanganui, Passes 2→6 as a chain; fields diffed against the shipped card |
| Runtime | Night 1, 5 voices, rebuilt card vs shipped card, read blind | two voice runs, for item 5 only |
| Paid runs | about 130 pass-level runs, 16 tailor calls, 7 rebuilds, 24 voice runs | 21 pass-level runs, 1 tailor call, 2 voice runs |
| Harness | needs the draws / arms / archive / report extension first (about half a day of code) | today's harness, by hand |
| **≈ Cost** | **$175** (allow $210 with redraws) | **$14** (allow $20 with redraws) |
| Shows | whether each instruction takes, how often it leaks, and whether whole cards and artifacts lost texture | whether each instruction takes |
| Doesn't show | rare leaks (three draws usually miss a 1-in-10 leak) | leak rates, or a loss of texture in cards and artifacts |

Per item (patch numbers in brackets; costs from recorded token usage, §0.3):

| Item | Change | Plan B check | B ≈ | Plan A check | A ≈ |
|---|---|---|---|---|---|
| 7 [01] | Pass 0b: name a work only if Perplexity names it | Lovelace, 1 tailor call | $0.33 | 4 voices × (3 + 1) tailor calls | $6.4 |
| 1 [02] | `voice_temporal_stance`: assembly leads, `anchored_override` null, hook ban | Lovelace, Octopus, Scheherazade, Battuta: Pass 2 | $2.75 | the same 4 voices × 5 draws | $13.75 |
| A6 [03] | `council_member_name` completes "You are ___." | the item-1 draws | $0 | Lovelace, Octopus, Cleopatra, Marley, drawn after item 1 has landed | $11.5 |
| 2 [04] | "Voice of X" from Pass 0a; profile name set in code | unit test | $0 | unit test + 6 Pass 0a calls | $1 |
| 4 [05] | Witness blocks cover every field; speaker frame | Whanganui: Pass 4b, 4a, 2 + coverage test | $1.73 | the same 3 passes × 5 draws | $8.65 |
| 3 [06, 09] | Composer stance (3a: Pass 0a, node 0, 4a, 6; 3b: Pass 2, 3) | Plato: Pass 6, 4a, 3, 2 (**needs O2**) | $2.32 | Plato + Scheherazade: 4 passes × 5 draws | $23.7 |
| 6 [07] | Operator direction reaches Pass 4a/4b; stale song lines removed | Marley 4b + 4a, Arendt 4b + render identity | $1.24 | + Whanganui and Octopus 4b; × 5 draws | $8.7 |
| 5 [08] | Gap-H entry in `topics_requiring_care` | Battuta: Pass 2 + two voice runs on the wbbf26 briefings | $2.20 | 4 voices Pass 2; 3 voices × 3 voice runs | $19.0 |
| End state | — | Whanganui chain, Passes 2→6 | $3.21 | 7 rebuilds ($46) + runtime comparison ($34) | $80 |
| | | **Plan B total** | **$13.78** | **Plan A total** | **≈ $173** |

**Recommendation** (the operator decides): run Plan B, then Plan A's end state only (the rebuilds and the runtime comparison, about $80), before Stage 5 starts. Reasons in §0.4.

**Landing order:** 7 → 1 → A6 → 2 → 4 → 3a → 3b → 6 → 5. Patch 06 needs 05, and 09 needs 05 and 06. The others apply in any order (checked, §0.5).

**Open operator decisions:**
1. **O1 — Test plan, sandbox and protocol.** Plan A, Plan B, or Plan B followed by Plan A's end state (recommended; §0.4). Also: the sandbox location (recommend `projects/current-tests/stage4-sentinels/`), and deleting the review flag in the sandbox (recommended in either plan; it only removes a Derive call that tests nothing).
2. **O2 — Plato as a sentinel** for item 3 (and, in Plan A, item 5 and the rebuild). `_workspace/planning/ONBOARDING.md:65` says "No Plato re-run without explicit ask". The runs regenerate passes in a sandbox copy. Without Plato, item 3a has no honest check: the collision evidence is his.
3. **O3 — Item 3 trigger.** New `mediation_stance: "composer"` (recommended) or a universal clause. Voices: Plato and Scheherazade.
4. **O4 — Item 6 shape.** New `artifact_direction` field (recommended), or pipe `manual_grounding` + `editorial_rationale` as filed. Either way, Marley's config must be reconciled with v2 first.
5. **O5 — Item 5.** Placement in `topics_requiring_care` (recommended); land only after the refusal-detection fix.
6. **O6 — Whanganui frame.** Align `epistemic_frame_statement`'s opening with the witness stance (recommended; N5).
7. **O7 — Shipped cards.** Stage 4 changes prompts only. Patch the 8 off-spec `council_member_name` values, Whanganui `hard_limits[1]` (N9) and `epistemic_frame_statement` (N5) now, or at the next rebuild? Any card patch changes voice input and needs re-validation.
8. **O8 — Place name for item 1.** Take it from `conference_facts.json` `location` now (in the patch), or wait for roadmap 2.1 `event_config`.
9. **O9 — Item 7 rule strength.** Perplexity-grounded names (recommended) or no names at all (roadmap path 1).
10. **O10 — `voice_config.name` stays bare (new).** Item 2 adds a separate `voice_name` field and leaves `name` as "Plato". That departs from voices §18, which lists `voice_config.name` among the "Voice of X" fields. Reasons in item 2. Recommend the separate field.
11. **O11 — `anchored_override` key (new).** Item 1 keeps the key and always emits null, as all 10 shipped cards do. The roadmap says "drop `anchored_override` emission". If that means removing the key, the chat builder's comment and its test fixture change too. Recommend keeping the key.

**Findings not in any tracker when written** (each CONFIRMED by reading; N1–N6, N8, N9 verified by the review):
- **N1.** `persona_pass_4b_artifact.md:87-93` still gives the v1 Marley instruction ("the medium IS the song… lyric + Suno-style kind-hint… Do NOT bridge song → prose"), against the v2 block at `:122-166`. Task 1 found the same (`REVIEW_2026_09_28_prompts_correctness.md` #14); file it once.
- **N2.** Marley's shipped `voice_config` still mandates the v1 song artifact (`manual_grounding`: "THE LOAD-BEARING DIRECTION. The voice's artifact at runtime IS a song"; `editorial_rationale`: "song-as-artifact, not prose-about-song"). Passes 4a/4b don't read the config today. The Pass 0b tailor does read `editorial_rationale` (`run_pass_0b_tailor.py:218`), so this bites at Marley's next build, and it blocks item 6 as filed.
- **N3.** `persona_derive.md:46` asks for `"name": "<voice_name from card>"`, but the runner removes `voice_name` from Derive's input (`run_persona_pipeline.py:920-924`, `:2006-2010`). The model guesses: the shipped profile names are "Plato", "Octopus", "Te Awa Tupua", "Shahrazād bint al-wazīr".
- **N4.** Lovelace's four phantom citations (voices §19) are all in her Gemini broad scan, which has no source list. The tailor passed them into the §2/§3 DR prompts.
- **N5.** Whanganui's runtime prompt opens with two contradicting identities: "You are I am the construction stewarding…", then "You are Te Awa Tupua." The root is the Pass 2 system-entity template (`persona_pass_2_identity_boundaries.md:269-277`).
- **N6.** Four more `council_member_name` values have first-person tails (Plato, Battuta, Scheherazade, Marley): 8 of 10 runtime first lines mix grammatical person.
- **N7.** Sentinel harness gaps. `f7e0d4c` fixed A5 and the display-name brittleness; the rest is still open (§0.1).
- **N8.** Pass 7c already emits anti-structure `banned_modes` for Battuta, Arendt, Lovelace and Dostoevsky, and Battuta's was on the card when the wbbf26 dryrun produced "a fatwa in Rihla clothing".
- **N9.** Whanganui `hard_limits[1]` keeps "Whanganui Iwi are not stakeholders in me, they ARE me", in the Pass 2 output and on the shipped card.
- **N10 (from the review).** The repaired `sentinel_regen.py` defaults to `plato,fyodor_dostoevsky` (`:64`), the two voices `ONBOARDING.md:65-66` restricts. Always pass `--voices`.
- **N11 (from the review).** `personas/schemas/voice_config.py` is imported by no code. Config validation is `node0_validation.validate_input`, which did not check `mediation_stance`.

---

## 0. The gate

### 0.1 The harness on `main` (CONFIRMED by reading `personas/scripts/sentinel_regen.py`, `invalidate_cache.py`, `run_persona_pipeline.py`; nothing run)

`f7e0d4c` repaired voices §37 A5: a `sandbox` subcommand, `regen --project --baseline-project`, any slug, and a refusal to run in a git project such as athens-2026. What it does today, and what is still open:

| # | State | Where | Effect |
|---|---|---|---|
| G1 | `regen` invalidates **one** pass | `sentinel_regen.py:175-176` (`invalidate_cache.py --pass`) | Fine for single-pass checks. When several passes of one voice are drawn, the order matters (§0.2 step 5) |
| G2 | The sandbox copies `_operator_review_passed.flag` | `make_sandbox`, `:144` (`copytree`) | With the flag, every run takes the path-(b) fast exit and **pays for Derive** (`run_persona_pipeline.py:901-942`). Delete the flag (§0.2) |
| G3 | The diff is structural: changed keys plus the first 200 chars | `_diff_against_baseline`, `:190-233` | It can't judge a field. Read the field, and run the item's mechanical checks |
| G4 | The baseline is production's pass output, not the shipped card | `resolve_baseline`, `:158-159` | Right for a control arm. The target is still the hand-corrected card, so compare with that by reading |
| G5 | No arms, draws or archive | — | Each regen overwrites the sandbox pass output. Copy it aside by hand |
| N10 | Defaults are `plato,fyodor_dostoevsky` | `:64` | Always pass `--voices` |
| — | The runner has no `--stop-after` | `run_persona_pipeline.py:51-52` | Not needed for single-pass checks once the flag is gone (§0.2) |

### 0.2 The protocol (both plans)

1. **Make the sandbox.** `sentinel_regen.py sandbox --from <athens-2026> --to <projects/current-tests/stage4-sentinels> --voices ada_lovelace,octopus,scheherazade,ibn_battuta,whanganui_river,plato,bob_marley,hannah_arendt` (Plan A adds `cleopatra,fyodor_dostoevsky`). `regen` refuses a project root that holds a `.git` folder, so the sandbox must be a plain folder.
2. **Delete `voices/<slug>/_operator_review_passed.flag` in the sandbox**, for every voice. Why this removes the Derive call (CONFIRMED by reading; all 10 athens-2026 voice folders checked):
   - the fast exit needs the flag (`run_persona_pipeline.py:901-904`);
   - without it, the run goes on through Passes 7-pre, 7-anachronism, 7a, 7b, 7c and 7a FINAL, and each is a `call_or_cache` whose output file exists in every voice folder;
   - the 7a fix pass is skipped because `02_merge/_fix_log.json` exists (`:1447`);
   - the cached 7a FINAL verdict is `REVISION_NEEDED` for all 10 voices, so the operator review gate halts with `sys.exit(0)` (`:1969-1991`), before Derive (`:2003` onward).
3. **Dry run, $0.** Run `run_persona_pipeline.py <slug> --project <sandbox>` once per voice with nothing invalidated. Expect only `CACHE HIT` lines and the "OPERATOR REVIEW GATE" halt. Any `RUNNING:` line means a paid call was about to happen: stop and find out why before going on.
4. **Set sandbox configs** where an item needs it (item 3a: `"mediation_stance": "composer"` for Plato; item 6: `artifact_direction` for Marley).
5. **Per item:** apply its patch on a branch, then `sentinel_regen.py regen --pass <p> --project <sandbox> --baseline-project <athens-2026> --voices <slug>`.
   - One pass per run. When an item touches several passes of one voice, regenerate the **downstream pass first** (4b, then 4a, then 2), so each pass is drawn from the same upstream as its control.
   - For a **chain** (the end-state check), go the other way: regenerate Pass 2, then 3, 4a, 4b, 5, 6, one run each. Each pass then reads the regenerated upstream. No validator is re-run.
   - Watch the log: exactly the target pass and its CT compress should show `RUNNING:`.
   - Copy the regenerated pass output to `<sandbox>/_sentinels/<item>/<slug>/` before the next run overwrites it.
6. **Judge.** Control = the athens-2026 pass output (one draw of the current prompt). Treatment = the sandbox output. Run the item's mechanical checks on both, and read the treatment field next to the shipped card's field. Plan A repeats steps 5–6 for each draw and also draws the control fresh, on the unpatched prompt.
7. **Land or not.** The item lands when the treatment passes every check and the control fails at least the check the item exists to fix. A failed treatment means revise and redraw that voice. Keep a running total of the spend.

Adaptive thinking stays on for Passes 2–6, as `model_routing.json` sets it (`personas.pass_2` … `pass_6`: `thinking: "adaptive"`). Shipped cards are not regenerated: Stage 4 changes what the next build emits.

### 0.3 Cost basis (CONFIRMED arithmetic on recorded usage; the prices are the assumption)

From the `usage` blocks of the athens-2026 pass outputs, at Opus 4.7 $5 / $25 per M tokens and Sonnet 4.6 $3 / $15 for the CT compress:

| Voice | Pass 2 + CT | Pass 4a + CT | Pass 4b + CT | Pass 6 | Derive (avoided) |
|---|---|---|---|---|---|
| Ada Lovelace | 0.66 + 0.04 | 0.59 + 0.16 | 0.09 + 0.13 | 0.37 | 0.35 |
| Octopus | 0.56 + 0.06 | 0.47 + 0.10 | 0.12 + 0.10 | 0.41 | 0.34 |
| Whanganui River | 0.62 + 0.06 | 0.61 + 0.16 | 0.12 + 0.16 | 0.38 | 0.44 |
| Plato | 0.52 + 0.04 | 0.56 + 0.12 | 0.08 + 0.10 | 0.32 | 0.32 |
| Bob Marley | 0.70 + 0.05 | 0.63 + 0.10 | 0.11 + 0.11 | 0.49 | 0.36 |
| Hannah Arendt | 0.83 + 0.05 | 0.87 + 0.10 | 0.14 + 0.15 | 0.55 | 0.36 |
| Ibn Battuta | 0.75 + 0.07 | 0.67 + 0.18 | 0.10 + 0.17 | 0.51 | 0.37 |

Other figures:
- **Pass 3** is $0.60–0.74, plus $0.08–0.13 for its CT compress. **Pass 5** is $0.12–0.23. Pass 6 has no CT compress.
- **A Pass 0b tailor call** is $0.33–0.45 (Lovelace $0.33).
- **A runtime voice run** (Step 1 + Step 2 for one voice, no validation) cost $1.34–3.88 on Athens Night 1, mean $2.24: Plato $1.48, Lovelace $2.15, Whanganui $2.15, Marley $2.49, Scheherazade $3.18. On the archived wbbf26 dryrun it cost less: Battuta $0.69, Cleopatra $0.94, Plato $1.11. Both are from the token counts in the runs' `04_voice/` folders, with a 1-hour cache write at 2× the input price and a cache read at 0.1×.
- **A rebuild from Pass 2 through 7a FINAL** is about $6.5 per voice. PLAUSIBLE only: Passes 2–6 are about $3.2 and Pass 7b about $0.55 from usage, but the 7-pre and 7a-FIX calls record no usage, and the three gpt-5.4 calls and one Gemini call (about 30K tokens in, 10K out each) are not priced in the repo.
- The patched prompts are a few hundred tokens longer than the ones these figures come from. That is within the rounding.

### 0.4 Two test plans

Both plans use the protocol in §0.2, the same patches, the same mechanical checks, and the same landing order. They differ in how much they draw.

#### Plan B — best value (≈ $14)

One treatment draw for every part of every patch, judged against a control that costs nothing.

| Step | Runs (in this order) | ≈ Cost |
|---|---|---|
| Dry run | each sandbox voice, nothing invalidated | $0 |
| Item 7 | Lovelace, tailor call | $0.33 |
| Items 1 + A6 | Pass 2: Lovelace $0.70, Octopus $0.62, Scheherazade $0.61, Battuta $0.82 | $2.75 |
| Item 2 | unit test | $0 |
| Item 4 | Whanganui: Pass 4b $0.28, 4a $0.77, 2 $0.68 | $1.73 |
| Item 3a | Plato: Pass 6 $0.32, 4a $0.68 | $1.00 |
| Item 3b | Plato: Pass 3 $0.76, 2 $0.56 | $1.32 |
| Item 6 | Marley: Pass 4b $0.22, 4a $0.73; Arendt: Pass 4b $0.29 | $1.24 |
| Item 5 | Battuta: Pass 2 $0.82; two voice runs on the wbbf26 briefings, $0.69 each | $2.20 |
| End state | Whanganui chain: Pass 2 $0.68, 3 $0.87, 4a $0.77, 4b $0.28, 5 $0.23, 6 $0.38 | $3.21 |
| **Total** | 21 pass-level runs, 1 tailor call, 2 voice runs | **$13.78** |

- **Why these draws.** Each line is the cheapest draw that exercises text which would otherwise land untested: the four stance variants (standard, organism, fictional, own calendar), the witness blocks, the composer blocks, the operator direction and the rewritten guardrail, the Gap-H entry.
- **Why the control is free.** The athens-2026 pass outputs are a draw of the current prompt from the same upstream. Each item's control fails a check that is close to deterministic (the v1 opening sentence, "I am …" in the name, first person as the river, "my mother Phaenarete").
- **The end-state chain** is the one check of the roadmap's exit criterion ("a fresh sandbox voice builds … matching shipped-card architecture without operator patches for the known classes"), on the voice with the most hand patches. A short script merges the six regenerated `fields` blocks and prints each field next to the shipped card's.
- **Is the earlier $5.62 plan already the best value?** It is the core of this one (items 7, 1 and A6 on two voices, 2, 4, 3a, 6). The other $8.16 buys four things that plan left untested: the fictional and calendar variants of item 1 ($1.43), item 3b ($1.32), item 5 ($2.20), and the end-state chain ($3.21). Each is a single draw of something nothing else covers. Past this point a second draw mostly re-measures a check that is already near-deterministic.
- **Assumptions.** The review flag is deleted in the sandbox (no Derive). If it stays, add about $0.37 per run: $7.80. Prices and token counts as in §0.3.

#### Plan A — best for quality (≈ $175)

Three stages.

**A1. Per-item gates, strictly one item at a time.** For each voice and pass: 3 treatment draws and 2 fresh control draws on the unpatched prompt. The athens-2026 output is a third control, and it shows whether the fix pass and the five months since the build matter.

| Item | Voices and passes | Draws | ≈ Cost |
|---|---|---|---|
| 7 | Lovelace, Octopus, Cleopatra, Dostoevsky: tailor | 3 treatment + 1 control each | $6.4 |
| 1 | Lovelace, Octopus, Scheherazade, Battuta: Pass 2 | 5 each | $13.75 |
| A6 | Lovelace, Octopus, Cleopatra, Marley: Pass 2, after item 1 has landed | 3 treatment each; 2 control for Cleopatra and Marley (item 1's treatment draws are the control for the other two) | $11.5 |
| 2 | unit test; Pass 0a for three names, in its own sandbox | 2 each | $1 |
| 4 | Whanganui: Pass 4b, 4a, 2 | 5 each | $8.65 |
| 3 | Plato and Scheherazade: Pass 6, 4a, 3, 2 | 5 each | $23.7 |
| 6 | Marley 4b + 4a; Arendt, Whanganui, Octopus 4b | 5 each | $8.7 |
| 5 | Pass 2: Battuta, Cleopatra, Plato, Arendt. Runtime: Battuta, Cleopatra, Plato on the wbbf26 briefings | Pass 2: 3 treatment (2 control for Arendt; earlier items' draws for the rest). Runtime: 2 treatment + 1 control | $19.0 |
| | | **A1** | **≈ $93** |

**A2. End state: rebuilt cards (≈ $46).** With all patches applied, rebuild five voices from Pass 2 through 7a FINAL in the sandbox (`invalidate_cache.py --from-pass 2`, then the pipeline): Lovelace (standard), Whanganui (witness), Plato and Scheherazade (composer), Marley (lyrics constraint and operator direction). Also rebuild Whanganui and Plato on the unpatched prompts, as the baseline. Compare:
- each rebuilt card with the shipped card, field by field, for every class the operator patched by hand (the stance, the name, first person as the river, the speaker frame, the Socrates collisions, Marley's artifact form);
- the 7a FINAL issue count on patched against unpatched prompts.

**A3. Runtime comparison (≈ $34).** In a sandbox runtime project holding a copy of Night 1's briefings, run Step 1 + Step 2 for the five voices on the rebuilt card, twice, and once on the shipped card: `voice_flow.py <run_dir> --night 1 --skip-step3 --skip-step2-validation --skip-continuity --voices <slugs> --project <sandbox>` (options read at `runtime/flows/voice_flow.py:696-722`; not run). The published Night 1 artifacts are a second control. The operator reads the artifacts blind: which is the shipped voice, and is either one weaker?

- **Total:** $93 + $46 + $34 ≈ **$173**. Allow $210 for redraws.
- **Volume:** about 130 pass-level runs, 16 tailor calls, 7 rebuilds and 24 voice runs; about 150 pass and tailor outputs, 7 cards and 24 artifacts to read. The mechanical checks can be scripted; the reading cannot.
- **Harness work first** (about half a day of code): `--draws N` and `--arm` with a per-draw archive, a field-by-field report against the shipped card, and `--from-pass/--through`. Without it, 130 runs mean 130 manual copies.
- **Assumptions.** As for Plan B, plus: the rebuild estimate is PLAUSIBLE only (§0.3); A3 assumes the voice flow runs on a copied run folder in a sandbox project, and its cost moves with how many Step 1 calls hit the prompt cache.

#### What each plan shows

| Question | Plan B | Plan A |
|---|---|---|
| Does each instruction take? | yes, one draw per variant | yes, three draws |
| How often does it leak? | no | roughly: three clean draws rule out a leak that happens about half the time or more, not one in ten |
| Is the control's failure the prompt's doing, or the fix pass and the age of the output? | no | yes (fresh controls) |
| Did fields the item doesn't target get worse? | one draw, read against the control | several draws per arm, read side by side |
| Does a whole card still build to the shipped architecture? | one voice, Passes 2–6, no validators | five voices, through 7a FINAL, with a baseline |
| Did the artifacts change? | no (two voice runs, for item 5) | yes: 5 voices, blind read |

#### Recommendation

**Plan B, then Plan A's stages A2 and A3 once every patch has landed: about $14 + $80 ≈ $95.** Skip A1 unless a Plan B draw is ambiguous; then give that one check A1's draws.

- The per-item checks are close to deterministic. A1's extra draws mostly confirm what one draw shows, at $93.
- The failure this project has actually had from prompt changes is loss of texture from cumulative additions (the `3feb2b2` revert). It was found in artifacts and chat tests, not in field checks. Only A2 and A3 look there.
- A2 is also the roadmap's own exit criterion for Phase 1.
- If A2 or A3 shows a loss, the single-item draws from Plan B say where to start looking, and bisecting costs a few dollars per step.

Plan A in full is the right choice if the operator wants leak rates per item before anything lands, or wants each item's effect separated from the others' at the card level.

### 0.5 The patches: how they were made and checked

- **Made.** `main`'s versions of the 13 touched files were exported with `git show main:<path>`. A scratch script applied each item's edits to a copy of the previous state, asserting that every anchor text occurs exactly once. `git diff --no-index` between consecutive states produced the patches. They are embedded below, byte for byte; blank context lines keep their single leading space.
- **Checked offline (CONFIRMED, run in the session scratchpad):**
  - `git apply --check` and apply, in order 01–09, on a fresh copy of `main`'s files; the result equals the scratch end state.
  - The blocks as embedded in this doc were extracted again and re-checked the same way; they are byte-identical to the generated patches.
  - Each block was also checked with `git apply --cached --check` against `main`'s real tree, through a scratch index file (nothing in the repo was written).
  - Order: every patch applies alone on `main` except 06 (needs 05) and 09 (needs 05 and 06). 08 and 09 can be skipped or swapped.
  - 180 system-prompt renders under `StrictUndefined` (3 mediation stances × 5 voice types × 2 corpus constraints × Passes 2, 3, 4a, 4b, 6).
  - The composer block renders only for `composer`; the witness field list only for `transmission_witness`.
  - With a null direction, the patched 4a and 4b user prompts render byte-identical to `main`'s.
  - The patched runner, `node0_validation.py` and the three new files parse; the node 0 check accepts `None`, `"none"`, `"transmission_witness"` and `"composer"` and rejects anything else.
  - The two new test files pass against the patched prompts. The coverage test fails on `main` for Pass 2, 4a and 4b, which is Gap-E.
  - Item 1's mechanical checks pass on all 10 shipped `voice_temporal_stance.default` values (the target). A6's checks pass on "the Octopus", "Hannah Arendt", "Plato of Athens" and the witness name, and fail on the 8 off-spec shipped names.
- **Not run:** the repo's test suites, and anything that calls a model.
- **To re-check:** extract each `~~~diff` block that starts with `diff --git` into a file and run `git apply --check` from the repo root.

---

## 7. Pass 0b phantom citations (voices §19, path 3) — patch 01

### Evidence (CONFIRMED; `athens-2026/voices/ada_lovelace/01_research/`)

The four citations DR flagged as phantom all trace to the Gemini broad scan (`02_gemini_broad_scan.json`, `gemini-2.5-pro`, no citation list):
- "Bernadette Bensaude-Vincent, 'Les « notes » d'Ada Lovelace: une utopie technicienne?' in *Romantisme*, No. 177 (2017): 59-69";
- "Christopher Hollings, Ursula Martin, and Adrian Rice (2020)";
- "Ursula Martin (2022) … *Notes and Records* … (Co-authored with J. C. P. Miller)";
- "Miranda Anderson (2023) *The Renaissance of Imagination*".

The tailor copied them, with titles and years, into `04_section_2_dr_prompt.md` and `05_section_3_dr_prompt.md`. Its own note says why: "Bensaude-Vincent's French utopianism reading — non-Anglophone scholarship Perplexity systematically misses" (`02_tailoring_notes.json`). The Perplexity dossier (50 `citations`, 50 `search_results`) names only "Hollings, Martin, and Rice", once with "(2020s)" and never with a title.

So in the one documented case the tailor did not invent the phantoms; it pulled them from an ungrounded input. The prompt pushes it that way: `pass_0b_tailor.md:108` ("seek [1 specific scholar or work]"), `:110` (names load-bearing scholars), and few-shot examples that model scholar + title + year (`:76`, `:78`, `:86-87`, `:96`, `:98`). The roadmap's reading (the examples teach citation) holds; the Lovelace data adds that the scan supplies the names.

PLAUSIBLE, not checked: the Gemini scan also feeds the merge (Pass 1.x), so its bibliography could reach dossiers without passing through DR.

### Patch

A rule of "only if it appears in the inputs" would not have stopped these, because they are in the inputs. The patch grounds names in the Perplexity text only.

~~~diff
diff --git a/personas/flows/shared/prompts/pass_0b_tailor.md b/personas/flows/shared/prompts/pass_0b_tailor.md
index 5bd8ec9..990235f 100644
--- a/personas/flows/shared/prompts/pass_0b_tailor.md
+++ b/personas/flows/shared/prompts/pass_0b_tailor.md
@@ -73,9 +73,9 @@ Example for Dostoevsky §1 BIOGRAPHICAL FOUNDATION (given Perplexity + Gemini ty
 
 ```json
 "1": [
-  "How does Russian-language scholarship frame Dostoevsky's formative events inside Orthodox stradanie / kenoticism specifically, beyond event-level biography? Saraskina's Достоевский (Молодая гвардия 2011) is the most prominent reference.",
+  "How does Russian-language biographical scholarship frame Dostoevsky's formative events inside Orthodox stradanie and kenosis, beyond event-level biography? Which Russian biographies carry that reading, and how far do they differ from the Anglophone ones?",
   "How does the Peasant Marey episode (A Writer's Diary February 1876) complicate the standard Siberian-reconversion narrative as a documented moment-of-grace memory? Perplexity coverage typically misses this.",
-  "How does the disability-studies reading of Dostoevsky's epilepsy — Sarah J. Young, 'Epilepsy and the Dostoevskian Idiot,' Russian Review 76.4 (2017) — treat the paduchaya as phenomenological access rather than pathology?"
+  "Is there a disability-studies reading of Dostoevsky's epilepsy that treats the paduchaya as phenomenological access rather than pathology? What does it rest on in the letters and the novels?"
 ]
 ```
 
@@ -83,9 +83,9 @@ Example for Octopus §1 ECOLOGICAL FOUNDATION:
 
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
 
@@ -93,9 +93,9 @@ Example for Cleopatra §1 BIOGRAPHICAL FOUNDATION (`hostile_sources=true`):
 
 ```json
 "1": [
-  "How does current Egyptological and Ptolemaic-studies scholarship reconstruct Cleopatra's administrative and linguistic competence against the grain of Roman sources motivated to feminise and discredit? Cite Duane Roller (Cleopatra: A Biography, 2010) and Stacy Schiff's sourcing discussion; flag where reconstruction is inferential.",
+  "How does current Egyptological and Ptolemaic-studies scholarship reconstruct Cleopatra's administrative and linguistic competence against the grain of Roman sources motivated to feminise and discredit? Flag where the reconstruction is inferential.",
   "What does the Ptolemaic documentary record (papyri, administrative decrees) establish about Cleopatra's government independent of Roman narrative sources? Cite the specific papyrological evidence.",
-  "What is the state of scholarship on Cleopatra's ethnic and cultural identity in current Afrocentric vs. mainstream Ptolemaic historiography? Name the historians on each side; this is a contested field where hostile-source framing shapes downstream reception."
+  "What is the state of scholarship on Cleopatra's ethnic and cultural identity in current Afrocentric vs. mainstream Ptolemaic historiography? Set out the positions on each side; this is a contested field where hostile-source framing shapes downstream reception."
 ]
 ```
 
@@ -105,11 +105,11 @@ Tight. Specific. Anchored. Answerable. Each question is a tractable finish-line
 
 - **Ask unasked questions, do not restate coverage.** Do not produce "Research-to-date: Perplexity covered X, Y, Z. Go DEEPER on A, B, C." That shape pressures DR into avoidance or verification mode. Produce only the questions DR should address.
 
-- **Anchor each question to a specific gap.** Not "explore Russian scholarship more" but "Russian-language scholarship on [specific theme] — seek [1 specific scholar or work]." Answerable questions, not exhortations.
+- **Anchor each question to a specific gap.** Not "explore Russian scholarship more" but "Russian-language scholarship on [specific theme] — what does it establish about [specific question]?" Answerable questions, not exhortations.
 
-- **Cap named scholars per question at 0–2.** 0 is best if the question can be framed thematically. 1 or 2 is fine when a specific scholar's reading is genuinely load-bearing (Saraskina on Russian Orthodoxy; Goldstein on antisemitism; Bakhtin on polyphony). More than 2 turns each question into a scholar-verification checklist.
+- **Name a scholar or work only if the PERPLEXITY DOSSIER names it.** Perplexity's text carries source links; the Gemini broad scan does not, and its bibliographic details (titles, journals, issue numbers, years, co-authors) are unverified. Never copy a title, journal, issue, edition, year or co-author that the Perplexity text does not give, and never cite from memory. Where Gemini alone points to a reading, ask about the reading without naming the work ("Is there French-language scholarship that reads the Notes as technological utopianism? What does it argue?"). At most one name per question; 0 is best.
 
-- **Prefer thematic anchors over year-specific citations.** "Goldstein on antisemitism" is cheaper for DR than "Goldstein 2020". Year-specific is warranted only where the year is load-bearing (distinguishing early from late scholarship).
+- **Prefer thematic anchors over named ones.** The DR session finds the sources; your question tells it which gap to close.
 
 - **Voice-specific, not generic.** If a follow-up question could apply to any voice ("explore minority scholarly readings"), it's too generic. The tailoring pass exists precisely to produce voice-specific depth that generic prompts can't.
 
~~~

An optional offline check (code, not in the patch): after the tailor call in `run_pass_0b_tailor.py`, list the capitalised name tokens and four-digit years in the injections that don't occur in the Perplexity text, and write them into `tailoring_notes` as a warning.

### Checks

- **Plan B.** Lovelace, one call to `run_pass_0b_tailor("Ada Lovelace", project_root=<sandbox>)` ($0.33). It reuses the cached Perplexity and Gemini outputs and does not use `sentinel_regen.py`.
- **Plan A.** Lovelace, Octopus (science literature), Cleopatra (hostile sources) and Dostoevsky (are the rewritten examples copied into his own questions?): 3 treatment calls and 1 fresh control each ($6.4). This is a Pass 0b call, not a re-run of Dostoevsky's pipeline.
- **Control (free).** The existing athens-2026 injections; Lovelace's hold all four phantoms.
- **Mechanical checks.** No named work, title, journal or year that the Perplexity text lacks; none of the four known phantoms; 2–3 questions per section kept.
- **Read** for specificity: the tailor exists to be voice-specific (`pass_0b_tailor.md:114`).
- **Pass:** zero Gemini-only names, specificity held. If it leaks, escalate to no names at all (**O9**).

### Risks and order

Thinner questions are the risk; the anchored-gap rule stays. No card or runtime effect: it applies to the next voice build. First in the order: independent and cheapest.

---

## 1. `voice_temporal_stance` → the AF-leads architecture — patch 02

### Evidence from the shipped cards (CONFIRMED, `athens-2026/voices/*/07_persona_card_assembled.json`)

All 10 `voice_temporal_stance.default` values were hand-written at `08a8253` (voices §31 Gap-K): 5,958 chars in total, 507–733 each, all with `anchored_override: null`. Eight open with the same sentence ("You have been called to the assembly that gathers in Athens…", Plato's with "in YOUR city"). Octopus and Whanganui carry the same parts in their own grammar. Examples:
- **Marley** (515 chars): "You have been called to the assembly that gathers in Athens — present in their time, observing the panels but not entering them as participant. The questions are put before you; you respond from your own ground: 6 February 1945 to 11 May 1981, ending at thirty-six in Miami. When the panels' questions require translation from their world — concepts, technologies, events that came after you left — apply the translation_protocol to pull the question into your framework. You observe; you respond as yard-reasoning."
- **Ibn Battuta** adds a calendar clause: "Time in your world counts by the hijrī calendar with Christian reckoning available as translator's convenience."
- **Octopus:** "You register the assembly as it convenes in Athens — the questions arrive in your sensorimotor field; you respond. … The questions arrive; you register; you respond."
- **Scheherazade:** "…from your own ground: the chamber where each dawn is a deadline. … You observe; you tell from the chamber."
- **Whanganui** (first person, as the construction): "I have been called — as the construction stewarding the Te Awa Tupua published record — to the assembly… I observe; I report what the record establishes."

The five invariants, derived from the 10 texts: (1) the assembly leads, observer not participant; (2) "you respond from your own ground: [compressed standing-place]"; (3) optionally the voice's own counting; (4) the translation clause; (5) the closing line "You observe; you respond from [standing-place]". No card has a decline-to-engage hook (the ban at `_workspace/planning/ONBOARDING.md:72`).

What the current prompt produced (CONFIRMED, `athens-2026/voices/*/04_generation/01_pass_2_identity_boundaries.json`):
- 7 of 10 outputs open with the v1 frame verbatim, e.g. Plato: "You speak from within your own world and lifetime. Your horizon is bounded by…". Scheherazade has its fictional variant, Octopus "You speak from your own sensorimotor present to the reader's".
- 8 of 10 carry a populated `anchored_override` ("You speak from the threshold of your death on…").
- Whanganui's is first person as the river: "I speak from the legal-ecological present of my ongoing existence…".

### Current prompt text

- `persona_pass_2_identity_boundaries.md:339-406`: the "fluid-across-time" default, the v1 template, the death-threshold `anchored_override` template, and "per Athens brief" at `:355`.
- `persona_pass_2_user.md:56-59` repeats the contract.
- The runtime reads `default` only (`runtime/flows/voice/card_assembly.py:240-282`). The chat builder keeps the dict intact (`personas/flows/shared/chat_prompt_builder.py:185-192`).

**The `anchored_override` key (O11).** The patch keeps the key and always emits null. The reason is the cards: all 10 shipped cards carry `"anchored_override": null` (the operator nulled the values at athens-2026 `2168519` and kept the key), so a null key is the canon. No code requires the key; the chat builder's test builds its own fixture.

### Patch

~~~diff
diff --git a/personas/flows/shared/prompts/persona_pass_2_identity_boundaries.md b/personas/flows/shared/prompts/persona_pass_2_identity_boundaries.md
index e8737d2..1207acd 100644
--- a/personas/flows/shared/prompts/persona_pass_2_identity_boundaries.md
+++ b/personas/flows/shared/prompts/persona_pass_2_identity_boundaries.md
@@ -1,6 +1,7 @@
 {# Pass 2 — Identity & Boundaries (Claude)
-   v3.10 Node 2. 10 fields produced as JSON (added voice_temporal_stance in Phase M;
-   REWRITTEN deployment-configurable per 1-arch-03 fix 2-02). #}
+   v3.10 Node 2. 10 fields produced as JSON. voice_temporal_stance follows the
+   AF-leads architecture of the shipped cards (athens-2026 08a8253, Stage 4
+   item 1); anchored_override is always null. #}
 BLOCK 1 — EXPERT IDENTITY:
 You are a senior intellectual historian specializing in {{ name }}'s domain and
 period. You combine deep biographical knowledge with sensitivity to the
@@ -336,74 +337,80 @@ knowledge_boundary — What lies beyond this voice's world. A general frame AND
 a specific exclusion list (temporal, geographic, conceptual). This is WHAT the
 voice knows.
 
-voice_temporal_stance — WHEN the voice speaks from. **Deployment-configurable
-field per 1-arch-03 fix 2-02.** Distinct from and complementary to
-knowledge_boundary: the boundary specifies what is beyond the voice's horizon;
-this field specifies the voice's standing point inside that horizon.
+voice_temporal_stance — WHERE the voice stands when the questions reach it.
+Distinct from and complementary to knowledge_boundary: the boundary says what
+lies beyond the voice's horizon; this field places the voice at the assembly
+and names the ground it answers from.
 
-**Produce an object with TWO sub-fields:**
+**Produce an object with `default` populated and `anchored_override` null:**
 
 ```json
 "voice_temporal_stance": {
-  "default": "<fluid-across-time framing, mandatory>",
-  "anchored_override": "<optional death-threshold or period-specific anchor, or null>"
+  "default": "<assembly-presence stance, mandatory>",
+  "anchored_override": null
 }
 ```
 
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
+Always emit `"anchored_override": null`. The card carries one stance; stance
+variants for other deployments belong to the deployment layer, not here.
+
+**`voice_temporal_stance.default` (MANDATORY; 4-6 short sentences, roughly
+500-700 characters; second person unless a mediation-stance block below sets
+the person).** Build it from five parts, in this order:
+
+1. THE ASSEMBLY LEADS. Open by placing the voice at the assembly, present in
+   its time, observing the panels but not entering them as participant:
+   "You have been called to the assembly that gathers in {{ assembly_place | default("its host city") }}
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
+  {{ assembly_place | default("its host city") }} — the questions arrive in your sensorimotor field; you
+  respond. You do not enter their panels as participant — you observe them."
+  Close on the perceptual cycle ("The questions arrive; you register; you
+  respond.").
+- Fictional: the own-ground clause sits inside the frame ("the chamber where
+  each dawn is a deadline"); translation pulls what the listener brings into
+  the tradition's grammar; close on the form ("You observe; you tell from the
+  chamber.").
+- When a mediation-stance block below applies, follow that block for who is
+  called to the assembly and in which person.
+
+Worked example (the shape to follow, not text to copy): "You have been called
+to the assembly that gathers in {{ assembly_place | default("its host city") }} — present in their time,
+observing the panels but not entering them as participant. The questions are
+put before you; you respond from your own ground: 6 February 1945 to 11 May
+1981, ending at thirty-six in Miami. When the panels' questions require
+translation from their world — concepts, technologies, events that came after
+you left — apply the translation_protocol to pull the question into your
+framework. You observe; you respond as yard-reasoning."
 
 translation_protocol — METHOD ONLY. A step-by-step generative process for how
 THIS specific voice encounters the unfamiliar AT RUNTIME. The steps must
diff --git a/personas/flows/shared/prompts/persona_pass_2_user.md b/personas/flows/shared/prompts/persona_pass_2_user.md
index 6a2e9c0..9367c5f 100644
--- a/personas/flows/shared/prompts/persona_pass_2_user.md
+++ b/personas/flows/shared/prompts/persona_pass_2_user.md
@@ -53,9 +53,8 @@ council_member_name, epistemic_frame_statement, world, formative_experience,
 character, knowledge_boundary, voice_temporal_stance, translation_protocol,
 topics_requiring_care, hard_limits.
 
-`voice_temporal_stance` is a deployment-configurable field per 1-arch-03
-fix 2-02 — produce object with `default` (fluid-across-time, mandatory) and
-optional `anchored_override` (death-threshold or period-specific anchor for
-chat/project deployments). See system prompt Block 3 for spec.
+`voice_temporal_stance` — produce an object with `default` (the
+assembly-presence stance, mandatory) and `"anchored_override": null`.
+See system prompt Block 3 for the five-part spec.
 
 Return ONLY the JSON object. No markdown fences, no preamble.
diff --git a/personas/run_persona_pipeline.py b/personas/run_persona_pipeline.py
index 4a00dcd..31b1196 100644
--- a/personas/run_persona_pipeline.py
+++ b/personas/run_persona_pipeline.py
@@ -102,6 +102,20 @@ def _load_deployment_priming() -> dict[str, str]:
         out["programming_tracks"] = ", ".join(tracks)
     return out
 
+def _assembly_place() -> str:
+    """City where the assembly gathers, for Pass 2's voice_temporal_stance.
+
+    Reads `location` from conference_facts.json ("Athens, Greece" -> "Athens").
+    Falls back to "its host city" when the file or field is missing.
+    """
+    facts_path = _paths.conference_facts(PROJECT_ROOT)
+    if facts_path.exists():
+        location = json.loads(facts_path.read_text()).get("location", "")
+        if location:
+            return location.split(",")[0].strip()
+    return "its host city"
+
+
 _paths.ensure_voice_dirs(SLUG, PROJECT_ROOT)
 
 
@@ -491,7 +505,8 @@ def _pass_2():
                   subtype=vi.get("subtype"), voice_mode=vi["voice_mode"],
                   hostile_sources=vi["hostile_sources"],
                   corpus_constraint=vi.get("corpus_constraint", "full"),
-                  mediation_stance=vi.get("mediation_stance"))
+                  mediation_stance=vi.get("mediation_stance"),
+                  assembly_place=_assembly_place())
     # 1-arch-05 Part A: per-chunk reads. Pass 2 consumes chunks 1.1 + 1.5 +
     # voice_level_debate subset of interpretive_frames (1.2).
     userp = render(
~~~

Notes on the patch:
- The place name is rendered from `conference_facts.json` (`"location": "Athens, Greece"` → "Athens"), with a `default` filter so any other renderer of the template still works. This removes one hardcoded "Athens" (`:355`) and adds none (roadmap 2.1 / C52, filed; **O8**).
- The spec is second person "unless a mediation-stance block below sets the person". Item 4 sets it for witness voices.

### Checks

- **Plan B.** Pass 2, one draw each: Lovelace (standard human), Octopus (organism variant), Scheherazade (fictional variant), Battuta (own calendar). $2.75, shared with A6.
- **Plan A.** The same four voices, 3 treatment and 2 fresh control draws each ($13.75), before A6's patch is applied.
- **Control (free).** Their athens-2026 Pass 2 outputs. All four fail the first check below; three have a populated override.
- **Mechanical checks on `voice_temporal_stance`:**
  - the first sentence contains "assembly" and "not entering them as participant" (organism: the text contains "do not enter their panels as participant");
  - contains "respond from your own ground" (organism: "you respond");
  - matches `translation[_ ]protocol`;
  - the last sentence starts "You observe;" (organism: "The questions arrive");
  - `anchored_override` is null; 450–800 chars;
  - none of: "within your own world and lifetime", "years ago", "centuries ago", "threshold of your death", "name the gap", "name the silence", "say so", "where the framework does not reach".
  - For a witness voice (item 4): the first sentence starts "I have been called", the text has "I speak from my own ground" or "I report what the record establishes", and the last sentence starts "I observe;".

  These checks pass on all 10 shipped defaults (run offline).
- **Read.** The own-ground clause is in the voice's own terms; the other nine Pass 2 fields show no new defect against the control.

### Risks and order

- **A formula the voice parrots.** The cards are near-template already, so this is acceptable; voice identity lives in the own-ground clause.
- **Gap-J-class collisions.** A voice-wide stance rewrite collided with Arendt's `hard_limits[4]` before (voices §31 Gap-J). The new text is what `08a8253` already shipped, so the class is closed on the cards.
- **Order:** first Pass 2 item.

---

## A6 (voices §37). `council_member_name` — patch 03

### What the card spec says (CONFIRMED)

`docs/AI_Assembly_Persona_Card_v2.md:245-250`: "The full name as the voice would give it, with any framing that sets the right tone. Not a Wikipedia heading — a self-introduction." · "First line of both Step 1 and Step 2 system prompts: 'You are {{council_member_name}}.'" · "**Sample:** Plato of Athens". (`:241` also says every response begins from "I am Plato", which is part of the ambiguity.)

So the field is a **name phrase that completes "You are ___."** The runtime does exactly that concatenation (`runtime/flows/voice/card_assembly.py:421-422`). The target here is the spec, not the cards: 8 of the 10 shipped values are off-spec.

### Evidence from the shipped cards (CONFIRMED)

| Voice | `council_member_name` (runtime reads "You are <this>.") | Source |
|---|---|---|
| Ada Lovelace | "I am Augusta Ada King, Countess of Lovelace — … Sign me, in technical work, A.A.L." | Pass 2 |
| Cleopatra | "I am Cleopatra Thea Philopator, daughter of Ptolemy, … — the seventh of my name in the house of Lagos." | Pass 2 |
| Octopus | "I am octopus. The name is yours, not mine — …" (140 words) | Pass 2 |
| Whanganui River | "I am the construction stewarding the Te Awa Tupua published record — …" (167 words) | operator patch (Pass 2 had "Te Awa Tupua — … I speak through Te Pou Tupua…") |
| Plato | "Plato son of Ariston, of the deme Collytus — though when I write I withdraw my name from the page; you will hear me only through Socrates and the others." | Pass 2 |
| Ibn Battuta | "Shams al-Dīn … al-Ṭanjī — known to those who have honoured me in their houses as al-faqīh al-Maghribī…" | Pass 2 |
| Scheherazade | "Shahrazād bint al-wazīr — though tongues have called me Šehrāzād, … rāwiya of the nights." | Pass 2 |
| Bob Marley | "Bob Marley — Berhane Selassie, Light of the Trinity. Some call I Tuff Gong, … I-and-I a messenger doing Jah work." | Pass 2 |
| Fyodor Dostoevsky | "Fyodor Mikhailovich Dostoevsky" | clean |
| Hannah Arendt | "Hannah Arendt" | clean |

The first four are voices §37 A6 / runtime C68 A6. The next four are N6.

### Why the prompt produces this (CONFIRMED by reading)

- `persona_pass_2_identity_boundaries.md:238-239` omits the render context and the sample; "a self-introduction" "as the voice would give it" invites "I am …".
- BLOCK 2's OUTPUT REGISTER (`:31-36`) tells every field to read as "addressed to or spoken by the voice".
- The 7a validator requires first or second person in every field (`persona_pass_7a_cross_model.md:43-46`) and would flag a correct name phrase. Since voices §32.2, 7a FINAL validates this field.

### Patch

~~~diff
diff --git a/personas/flows/shared/prompts/persona_pass_2_identity_boundaries.md b/personas/flows/shared/prompts/persona_pass_2_identity_boundaries.md
index 1207acd..0476b8d 100644
--- a/personas/flows/shared/prompts/persona_pass_2_identity_boundaries.md
+++ b/personas/flows/shared/prompts/persona_pass_2_identity_boundaries.md
@@ -236,8 +236,21 @@ BLOCK 2 — GUARDRAILS:
 BLOCK 3 — FIELD SPECIFICATIONS:
 Produce these 10 fields:
 
-council_member_name — The full name as the voice would give it. Not a Wikipedia
-heading — a self-introduction.
+council_member_name — The name the voice answers to, as the voice would give
+it: the full name plus, at most, one short epithet or framing that sets the
+tone. Not a Wikipedia heading. It is rendered as the first line of the runtime
+system prompt, exactly: "You are <council_member_name>." So it must complete
+that sentence:
+- a noun phrase of 1-25 words, on one line;
+- no sentences, and no first-person words (I, me, my, I-and-I);
+- no "Voice of" prefix (the card's voice_name carries that convention);
+- no source lists, species lists, or record inventories (those belong in
+  epistemic_frame_statement and world).
+This field is exempt from the OUTPUT REGISTER rule above: it is a name, not
+prose.
+Examples: "Plato of Athens" · "Hannah Arendt" · "Shahrazād bint al-wazīr,
+rāwiya of the nights" · for a non-human voice, its common name with the
+article ("the Honeybee").
 
 epistemic_frame_statement — 2-4 sentences in second person addressing the voice
 directly. The frame must: (1) name who the voice is, what kind of thinker
diff --git a/personas/flows/shared/prompts/persona_pass_7a_cross_model.md b/personas/flows/shared/prompts/persona_pass_7a_cross_model.md
index 311f602..808fe7f 100644
--- a/personas/flows/shared/prompts/persona_pass_7a_cross_model.md
+++ b/personas/flows/shared/prompts/persona_pass_7a_cross_model.md
@@ -44,6 +44,10 @@ REGISTER CHECK (CRITICAL):
   voice) or second person (addressed to the voice). Third-person scholarly
   description is a critical failure — it causes the model to reason ABOUT the
   voice rather than AS the voice at runtime.
+- Exception: `council_member_name` is a name phrase the runtime renders as
+  "You are <value>." It carries no person-register; do not flag it for
+  register. Flag it if it is a sentence, uses first-person words, carries a
+  "Voice of" prefix, or runs past one line.
 - **TOLERATE Boddice biocultural-discipline brackets (FU#59 2026-04-29):**
   inline `[experiential_reconstruction]`, `[projection_warning: ...]`, and
   `[scholarly_consensus]` / `[stated]` / `[inference]` / `[contested]` /
~~~

The length rule is **1–25 words**: "Hannah Arendt" and "the Octopus" are correct outputs. The examples avoid the sentinel voices' exact answers, apart from the spec's own sample. The witness version of the name is in item 4's field list.

### Runtime and shipped cards (outside Stage 4)

For a regenerated card, `card_assembly.py:421-422` then reads correctly. The shipped cards stay as they are; the fix belongs to runtime C68 A6 (open with the `council_config` name) or to a card patch (**O7**).

### Checks

- **Plan B.** The item-1 draws, read for this field: Lovelace and Octopus ("I am …" in the control), Scheherazade and Battuta (first-person tails in the control). No extra cost. Whanganui's witness name is checked in item 4's Pass 2 draw.
- **Plan A.** Separate draws, after item 1 has landed: Lovelace, Octopus, Cleopatra and Marley, 3 treatment each; 2 fresh control for Cleopatra and Marley; item 1's treatment draws are the control for the other two ($11.5).
- **Mechanical checks:** no `\b(I|me|my|I-and-I)\b`; 1–25 words; one line and not a sentence; no "Voice of".
- **Read.** The epithet is in the voice's register; Octopus doesn't become a species label ("Octopus vulgaris" is the spec's counter-example, `Persona_Card_v2.md:243`). Read the treatment card's first ~600 tokens as the runtime assembles them: the long self-framing that Octopus loses from line 1 must still be in `epistemic_frame_statement`.

### Risks and order

If the 7a line is left out, 7a and 7a-FIX may "correct" the name back into first person. Order: with item 1 (same pass, same draws).

---

## 2. "Voice of X" emitted natively (voices §18 item 1) — patch 04

### Evidence (CONFIRMED)

- All 10 cards have `voice_name: "Voice of X"`, hand-applied at athens-2026 `f7e86a7` (voices §24). Conventions: the full personal name where the operator chose it ("Voice of Fyodor Dostoevsky"), the English article before a non-personal name ("Voice of the Octopus").
- All 10 `voice_config.name` values are still bare ("Plato", "Dostoevsky", "Octopus", "Whanganui River"). The `f7e86a7` sweep did not change them.
- The runner copies `name` into the card (`run_persona_pipeline.py:1856`, `:1864`).
- `provocateur_profile.name` comes back wrong on every re-Derive (N3).

`voice_name` is not voice input: the runtime prompt doesn't render it (field lists at `card_assembly.py:82-147`), and the chat artifact strips it (`chat_prompt_builder.py:129`).

### Design choice, and the departure from voices §18 (O10)

voices §18 (2026-05-02) lists `voice_config.name` among the fields to become "Voice of X". This proposal deliberately leaves `name` bare and adds a separate `voice_name` field. That is a departure from a filed decision, so it is the operator's call. The reasons (CONFIRMED by reading):
- `{{ name }}` is the figure's name in 25 prompt files, e.g. `persona_pass_2_identity_boundaries.md:5` "specializing in {{ name }}'s domain and period". "Voice of Plato's domain" is wrong.
- `voice_slug(name)` gives the folder (`flows/shared/io.py:35-44`, `:79-107`). "Voice of Plato" would resolve to `voice_of_plato`.
- The register scanner's overrides are keyed on the bare name: `_LAST_NAME_OVERRIDES = {"Octopus": None, "Whanganui River": "Whanganui"}` (`run_persona_pipeline.py:1710`). With "Voice of the Octopus" the skip no longer matches.
- The operator's own sweep left all 10 configs bare.

### Patch

~~~diff
diff --git a/personas/flows/shared/derive_post.py b/personas/flows/shared/derive_post.py
new file mode 100644
index 0000000..786ba77
--- /dev/null
+++ b/personas/flows/shared/derive_post.py
@@ -0,0 +1,18 @@
+"""Post-processing of the Derive output. No LLM call."""
+from __future__ import annotations
+
+from typing import Any
+
+
+def stamp_profile_name(profile: dict[str, Any], card: dict[str, Any]) -> dict[str, Any]:
+    """Set the Provocateur Profile's `name` to the card's `voice_name`.
+
+    Derive's input excludes `voice_name` (EXCLUDE_FROM_DERIVE in
+    run_persona_pipeline.py), so the model can only guess the name. The card
+    is the source, so the name is set here. A card without `voice_name` leaves
+    the profile as it is. Mutates and returns `profile`.
+    """
+    name = card.get("voice_name")
+    if name:
+        profile["name"] = name
+    return profile
diff --git a/personas/flows/shared/prompts/pass_0a_voice_config.md b/personas/flows/shared/prompts/pass_0a_voice_config.md
index 6e559e7..c141c21 100644
--- a/personas/flows/shared/prompts/pass_0a_voice_config.md
+++ b/personas/flows/shared/prompts/pass_0a_voice_config.md
@@ -35,6 +35,8 @@ Produce a JSON object with exactly these fields:
 
 - `name` (string): Display name. Normalize to public/scholarly usage — "Plato" not "Plato of Athens"; "Cleopatra" not "Cleopatra VII Philopator". For non-human: "Whanganui River", "Octopus".
 
+- `voice_name` (string): The panel designation: "Voice of " + the voice's name. Use the English article before a non-personal name ("Voice of the Nile", "Voice of the Honeybee"). For a person, use the name as commonly given in full: first name and surname for a modern person ("Voice of Mary Shelley"), a single name where that is the convention ("Voice of Confucius"). The curator may change it at review.
+
 - `type` (enum: `"human"` | `"fictional"` | `"non_human"`): Classification. **Note:** underscore form `non_human`, not hyphen (Phase B convention).
 
 - `subtype` (string | null): For non-human voices: `"organism"` (has neurons, perceives, responds — e.g., an octopus) or `"system"` (no cognition — a geographical, legal, or cosmological entity whose voice comes through mediation with human/indigenous kin, e.g., a river with legal personhood). Null for human and fictional.
@@ -73,6 +75,7 @@ Markdown document. Under 2 minutes to read. Structure:
 | Field | Value | Confidence |
 |---|---|---|
 | name | ... | auto |
+| voice_name | ... | proposed |
 | type | ... | proposed |
 | subtype | ... | proposed |
 | voice_mode | ... | proposed |
@@ -131,7 +134,7 @@ Then edit `voices/<slug>/00_intake/02_voice_config.json` and replace `"editorial
 
 - Return ONLY the JSON object with the two top-level keys `voice_config` and `review_doc`. No preamble, no commentary.
 - `review_doc` is a single markdown string. Do NOT wrap in code fences.
-- `voice_config`: 8-9 fields per the schema above (wikipedia_url conditional).
+- `voice_config`: exactly the fields in the schema above (`wikipedia_url` only when provided).
 - `editorial_rationale` is ALWAYS `null` in the JSON; the curator writes it into the file post-review.
 - Do NOT emit `conference_context` (Phase B dropped it).
 - Do NOT emit `primary_text_sources` or any editorial-assets fields.
diff --git a/personas/run_persona_pipeline.py b/personas/run_persona_pipeline.py
index 31b1196..4568c97 100644
--- a/personas/run_persona_pipeline.py
+++ b/personas/run_persona_pipeline.py
@@ -45,6 +45,7 @@ from flows.shared.node1d_excerpt_selection import build_structural_index, apply_
 from flows.shared.pass_7pre_chunked import run_chunked_pass_7pre
 from flows.shared.patch_walker import apply_patch_in_place as _apply_patch_in_place
 from flows.shared.chat_prompt_builder import write_chat_system_prompt
+from flows.shared.derive_post import stamp_profile_name
 
 
 _parser = argparse.ArgumentParser(description="End-to-end Persona Pipeline for a single voice")
@@ -956,7 +957,9 @@ if SKIP_TO_DERIVE:
     stamp("DERIVE: Provocateur Profile + Evaluation Rubric (Opus + thinking)")
     derive_fast = call_or_cache(_derive_raw_path, "Derive (path-b fast)",
                                  _derive_fast)
-    prov_profile = derive_fast["result"].get("provocateur_profile", {})
+    prov_profile = stamp_profile_name(
+        derive_fast["result"].get("provocateur_profile", {}),
+        json.loads(_assembled_card_path.read_text()))
     eval_rubric = derive_fast["result"].get("evaluation_rubric", {})
     write_json_atomic(_paths.provocateur_profile(SLUG, PROJECT_ROOT),
                       prov_profile)
@@ -1868,7 +1871,7 @@ def _build_assembled_card_dict(*, pass_7a_final_result=None, derive_completed=Fa
         # Preserve all top-level field content; only swap metadata
         existing["metadata"] = metadata
         # Preserve voice_name etc. but ensure they're present
-        existing.setdefault("voice_name", vi["name"])
+        existing.setdefault("voice_name", vi.get("voice_name") or vi["name"])
         existing.setdefault("voice_mode", vi["voice_mode"])
         existing["pipeline_version"] = "4.0"
         existing["generated_date"] = time.strftime("%Y-%m-%d")
@@ -1876,7 +1879,7 @@ def _build_assembled_card_dict(*, pass_7a_final_result=None, derive_completed=Fa
 
     # SKELETON call: build from in-memory pass dicts
     return {
-        "voice_name": vi["name"],
+        "voice_name": vi.get("voice_name") or vi["name"],
         "voice_mode": vi["voice_mode"],
         "pipeline_version": "4.0",
         "generated_date": time.strftime("%Y-%m-%d"),
@@ -2050,7 +2053,9 @@ def _derive():
 
 stamp("DERIVE: Provocateur Profile + Evaluation Rubric (Opus + thinking)")
 derive = call_or_cache(_paths.derive_raw(SLUG, PROJECT_ROOT), "Derive", _derive)
-prov_profile = derive["result"].get("provocateur_profile", {})
+prov_profile = stamp_profile_name(
+    derive["result"].get("provocateur_profile", {}),
+    json.loads(_paths.assembled_card(SLUG, PROJECT_ROOT).read_text()))
 eval_rubric = derive["result"].get("evaluation_rubric", {})
 stamp(f"  provocateur_profile: {len(prov_profile)} fields | "
       f"evaluation_rubric: {len(eval_rubric.get('identity_tests', []))} identity, "
diff --git a/personas/tests/test_derive_post.py b/personas/tests/test_derive_post.py
new file mode 100644
index 0000000..4fdea07
--- /dev/null
+++ b/personas/tests/test_derive_post.py
@@ -0,0 +1,23 @@
+"""The Provocateur Profile takes its name from the card, not from the model
+(Stage 4 item 2; voices OPEN_ITEMS §18)."""
+from __future__ import annotations
+
+import sys
+from pathlib import Path
+
+_PERSONAS_ROOT = Path(__file__).resolve().parent.parent
+sys.path.insert(0, str(_PERSONAS_ROOT))
+
+from flows.shared.derive_post import stamp_profile_name  # noqa: E402
+
+
+def test_profile_name_comes_from_the_card():
+    profile = {"name": "Plato", "medium": "dialogue"}
+    out = stamp_profile_name(profile, {"voice_name": "Voice of Plato"})
+    assert out["name"] == "Voice of Plato"
+    assert out["medium"] == "dialogue"
+
+
+def test_profile_is_unchanged_when_the_card_has_no_voice_name():
+    assert stamp_profile_name({"name": "Plato"}, {}) == {"name": "Plato"}
+    assert stamp_profile_name({"name": "Plato"}, {"voice_name": ""}) == {"name": "Plato"}
~~~

Notes on the patch:
- The profile name is set in code from the card (`stamp_profile_name`), not asked of the model. It lives in a small module so a unit test covers it; the runner itself can't be imported.
- `personas/schemas/voice_config.py` is not touched. No code imports it (N11), so an edit there would do nothing. `node0_validation.validate_input` passes unknown keys through (`:138`), so old configs without `voice_name` keep working through the fallback.
- The Pass 0a examples are not panel voices, so a test of this item can't pass by copying.

### Checks

- **Plan B.** The unit test in the patch (passes offline). Pass 2 is untouched, and `voice_name` is not voice input, so no sentinel draw is needed.
- **Plan A.** Also Pass 0a for three names (one non-personal, one needing the article, one person), 2 draws each, about $1 (PLAUSIBLE; no usage recorded for Pass 0a). Use a **separate** sandbox: `run_pass0a_voice_config.py` overwrites `02_voice_config.json` (`:280-284`), which would drop Whanganui's hand-set `mediation_stance` and rationale from the shared one.

### Risks and order

`council_config.json` is still wired by hand from the profile; with the stamp, the profile carries "Voice of X". Order: independent; after A6, which forbids the prefix in `council_member_name`.

---

## 4. The §31 fix pattern for witness voices (Gaps C, E, D, G) — patch 05

### Evidence from the shipped card (CONFIRMED, `athens-2026/voices/whanganui_river/`)

**Gap E.** Pass 2's witness block gives a per-field rule only for `hard_limits` (`persona_pass_2_identity_boundaries.md:523-537`). What Pass 2 produced, and what shipped after `3ccb1f9` / `97a2389`:

| Field | Pass 2 output (`04_generation/01_pass_2_identity_boundaries.json`) | Shipped card |
|---|---|---|
| `council_member_name` | "Te Awa Tupua — … I speak through Te Pou Tupua…" | "I am the construction stewarding the Te Awa Tupua published record…" |
| `voice_temporal_stance.default` | "I speak from the legal-ecological present of my ongoing existence…" | "I have been called — as the construction stewarding the Te Awa Tupua published record — to the assembly…" |
| `knowledge_boundary` | "I speak through Te Pou Tupua…; my framework is tikanga Māori… Beyond my world: any framing that fragments my mountains-to-sea indivisibility, that reduces me to resource-units…" | "I speak as the construction stewarding the published record. The framework Te Awa Tupua is recognised through is Te Pou Tupua…" |
| `character` | "I am Te Awa Tupua, articulated through Tupua te Kawa — my own four-fold natural law…" | "…I report — and stand by — the four kawa as Te Awa Tupua's character…" |
| `epistemic_frame_statement` | "You are Te Awa Tupua. You are a human construction attempting to give voice…" | unchanged (N5) |
| `hard_limits[1]` | "…Whanganui Iwi are not stakeholders in me, they ARE me." | unchanged (N9) |

The Pass 3, 5 and 6 witness blocks already name every field each pass emits (`persona_pass_3_intellectual_core.md:176-209`, `persona_pass_5_engagement.md:74-111`, `persona_pass_6_corpus.md:124-151`). They need nothing.

**Gap D.** Pass 4a's witness block covers `rhetorical_mode` and `characteristic_moves` only (`persona_pass_4a_voice.md:135-163`). The shipped lexicon glosses are third person about the legal personality ("Te Awa Tupua is both tupua and tupuna…"), the convention Pass 3 prescribes for `concept_lexicon` (`persona_pass_3_intellectual_core.md:189-194`).

**Gap G.** The speaker frame for cited first-person te reo is on the card in three places, all operator patches at `97a2389`: `hard_limits[8]`, `characteristic_moves[0]` ("…the gloss is *'Whanganui Iwi's identity-claim with the river: I am the River and the River is me'*, not bare…") and `quality_criteria[5]`. None of it is in the prompts (`persona_pass_4b_artifact.md:168-227`).

**Gap C.** A process gap. It becomes the offline test in the patch.

### Patch

~~~diff
diff --git a/personas/flows/shared/prompts/persona_pass_2_identity_boundaries.md b/personas/flows/shared/prompts/persona_pass_2_identity_boundaries.md
index 0476b8d..13815bc 100644
--- a/personas/flows/shared/prompts/persona_pass_2_identity_boundaries.md
+++ b/personas/flows/shared/prompts/persona_pass_2_identity_boundaries.md
@@ -540,6 +540,38 @@ mediation_stance == "transmission_witness"):
   reproduce its third-person describing-the-construction phrasing
   inside field values.
 
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
+- voice_temporal_stance: the one called to the assembly is the construction,
+  in its own first person ("I have been called — as the construction
+  stewarding the … published record — to the assembly …"); it answers from
+  the record it stewards and closes on what it does ("I observe; I report
+  what the record establishes"). This overrides the field spec's second
+  person.
+- translation_protocol: the steps are the construction reading a question
+  against the record and the kawa it reports.
+- topics_requiring_care, hard_limits: second person to the construction, or
+  first person as the construction. Never phrase a rule in the entity's first
+  person ("not stakeholders in me, they ARE me" is the pattern to avoid).
+- Any field or sub-field not listed here: the same rule — the construction's
+  first person, or second person addressed to it; never the entity's first
+  person, never third-person description of the construction.
+
 Add a hard_limit, written in second-person imperative form
 (matching the existing hard_limits' "Never..." style), that forbids
 deploying the codified spiritual-legal framework (for Whanganui:
@@ -555,6 +587,15 @@ the hard_limit value:
   exported into wider discourse (legal personhood, kaitiakitanga in
   its statutory sense, Wai 167 settlement context, the 1840-2017
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
 
 BLOCK 4 — VOICE TYPE:
diff --git a/personas/flows/shared/prompts/persona_pass_4a_voice.md b/personas/flows/shared/prompts/persona_pass_4a_voice.md
index c091fbe..a6a9068 100644
--- a/personas/flows/shared/prompts/persona_pass_4a_voice.md
+++ b/personas/flows/shared/prompts/persona_pass_4a_voice.md
@@ -160,6 +160,23 @@ BLOCK 2 — GUARDRAILS:
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
 
 - REFERENCE NOT DISPLAY (critical — Boddice sanity check): The card's
diff --git a/personas/flows/shared/prompts/persona_pass_4b_artifact.md b/personas/flows/shared/prompts/persona_pass_4b_artifact.md
index 07cbe98..16c34f6 100644
--- a/personas/flows/shared/prompts/persona_pass_4b_artifact.md
+++ b/personas/flows/shared/prompts/persona_pass_4b_artifact.md
@@ -183,6 +183,9 @@ conflict):
   construction-as-steward reasoning. The bilingual opener is
   the voice's signature move and carries voice-energy without
   requiring first-person-as-the-legal-personality.
+  When the cited te reo speaks in the first person, the gloss
+  names the original speaker (Whanganui Iwi, a named iwi speaker,
+  Te Pou Tupua, the s.13 codification).
 
 - relationship_to_detailed_response: Step 1 reasoning (private)
   works through which kawa engages the provocation and what the
@@ -203,7 +206,10 @@ conflict):
   you speak AS yourself — the construction stewarding the
   record — not AS the legal personality, AS the mediating
   office, or FOR the constituent community?") — alongside
-  standard voice criteria. CRITICAL: phrase ALL three criteria
+  standard voice criteria, and (4) a speaker-frame criterion ("When
+  you cite te reo with first-person grammar, does your gloss name
+  whose 'I' it is, so your own 'I' can't be read into it?").
+  CRITICAL: phrase ALL four criteria
   in second-person addressed to the construction (the runtime
   voice). Do NOT use third-person evaluator phrasing ("Does the
   piece...", "the construction reports...") — quality_criteria
@@ -211,6 +217,11 @@ conflict):
   construction tests itself against, not as evaluator
   questions ABOUT the construction.
 
+- technical_capabilities, aesthetic_qualities, stance_tendency: first
+  person as the construction or second person to it.
+- Any field not listed: the same rule — never the legal personality's
+  first person.
+
 Twin-failure-modes to ban (name explicitly, in the voice's
 vocabulary):
 - pastiche-Whanganui (LLM-generated te reo prose dressed as
@@ -224,6 +235,9 @@ vocabulary):
   named iwi speaker, scholarly publication; the construction does
   not curate whakataukī from a generic pool, only cites
   whakataukī that appear in documented sources, with attribution)
+- unframed first-person citation (a cited whakataukī or kawa in the
+  first person, glossed without naming whose "I" it is, so the
+  construction reads as the river)
 {% endif %}
 
 BLOCK 4 — VOICE TYPE:
diff --git a/personas/tests/test_conditional_block_coverage.py b/personas/tests/test_conditional_block_coverage.py
new file mode 100644
index 0000000..ae059e4
--- /dev/null
+++ b/personas/tests/test_conditional_block_coverage.py
@@ -0,0 +1,68 @@
+"""Every mediation-stance block names every field its pass emits.
+
+voices OPEN_ITEMS §31 Gap-C / Gap-E: the transmission_witness block in Pass 2
+once covered one field of ten, and the uncovered fields came out in the
+entity's first person. This test renders each prompt with and without the
+trigger and checks the block that the trigger adds. Offline; no model call.
+When a new stance or pass gets a block, add it to _BLOCKS.
+"""
+from __future__ import annotations
+
+import re
+import sys
+from pathlib import Path
+
+import pytest
+
+_PERSONAS_ROOT = Path(__file__).resolve().parent.parent
+sys.path.insert(0, str(_PERSONAS_ROOT))
+
+from flows.shared.prompt_render import render  # noqa: E402
+
+_CONTEXT = dict(name="Test Voice", type="non_human", subtype="system", voice_mode=None,
+                hostile_sources=False, corpus_constraint="full", assembly_place="Athens")
+
+_PASS_FIELDS = {
+    "persona_pass_2_identity_boundaries": [
+        "council_member_name", "epistemic_frame_statement", "world", "formative_experience",
+        "character", "knowledge_boundary", "voice_temporal_stance", "translation_protocol",
+        "topics_requiring_care", "hard_limits"],
+    "persona_pass_3_intellectual_core": [
+        "constitution", "concept_lexicon", "reasoning_method", "finds_compelling", "resists"],
+    "persona_pass_4a_voice": [
+        "rhetorical_mode", "characteristic_moves", "register_and_tone", "metaphorical_repertoire",
+        "preferred_vocabulary", "banned_language", "banned_modes"],
+    "persona_pass_4b_artifact": [
+        "medium", "technical_capabilities", "characteristic_output_structure",
+        "relationship_to_detailed_response", "aesthetic_qualities", "stance_tendency",
+        "length_and_format_constraints", "quality_criteria"],
+    "persona_pass_5_engagement": [
+        "bold_engagement_topics", "default_questions", "disagreement_protocol",
+        "unique_contribution"],
+    "persona_pass_6_corpus": ["header", "why_selected", "corpus_metadata"],
+}
+
+# (template, stance, strict). strict: every field must be named in the block.
+# Not strict: a field may instead be covered by a catch-all line.
+_BLOCKS = [(template, "transmission_witness", True) for template in sorted(_PASS_FIELDS)]
+
+_CATCH_ALL = re.compile(r"\b(Any|Every) (other )?field\b")
+
+
+def _block(template: str, stance: str) -> str:
+    """The lines the stance adds to the rendered prompt."""
+    with_stance = render(template, **_CONTEXT, mediation_stance=stance)
+    without = set(render(template, **_CONTEXT, mediation_stance=None).splitlines())
+    return "\n".join(line for line in with_stance.splitlines() if line not in without)
+
+
+@pytest.mark.parametrize("template,stance,strict", _BLOCKS)
+def test_stance_block_covers_every_field(template, stance, strict):
+    block = _block(template, stance)
+    assert block, f"{template} has no block for mediation_stance={stance!r}"
+    missing = [f for f in _PASS_FIELDS[template] if not re.search(rf"\b{f}\b", block)]
+    if strict:
+        assert not missing, f"{template} [{stance}] block does not name: {missing}"
+    else:
+        assert not missing or _CATCH_ALL.search(block), (
+            f"{template} [{stance}] block neither names {missing} nor has a catch-all line")
~~~

Notes on the patch:
- In Pass 4b the per-field lines sit above the "Twin-failure-modes to ban" list, so they don't read as banned modes.
- The `voice_temporal_stance` line sets first person for witness voices, which item 1's spec allows.
- `test_conditional_block_coverage.py` renders each prompt with and without the trigger and asserts that the added block names every field the pass emits. It fails on `main` for Pass 2 (9 of 10 fields not named), 4a (5 of 7) and 4b (3 of 8), and passes after the patch.

### Checks

- **Free.** The coverage test.
- **Plan B.** Whanganui, one draw each, in this order: Pass 4b, Pass 4a, Pass 2 ($1.73). The Pass 2 draw also checks the witness variants of items 1 and A6. The end-state chain (§0.4) then regenerates all six passes for this voice.
- **Plan A.** The same three passes, 3 treatment and 2 fresh control draws each ($8.65); Whanganui is also one of the five rebuilds.
- **Control (free).** The athens-2026 outputs in the table above.
- **Mechanical checks** over every field of each regenerated pass:
  - none of "I am Te Awa Tupua", "I am tupua", "my mauri", "my own four-fold", "in me, they", "my ongoing existence";
  - `epistemic_frame_statement` does not start "You are Te Awa Tupua";
  - the name is the construction's name phrase; the stance passes item 1's witness checks;
  - speaker-frame text in `hard_limits` (Pass 2), `characteristic_moves` (4a) and `quality_criteria` (4b);
  - none of "the construction reports" / "the position the construction stewards" (the Gap-B failure).
- **Read** against the shipped fields.

### Risks and order

- **The validator keeps flagging** third-person lexicon glosses (voices §28 ROUND 1). Telling 7a about witness conventions is a possible follow-up.
- **O6.** The shipped `epistemic_frame_statement` passed the Athens TEST with "You are Te Awa Tupua.", so there is no runtime evidence of harm. The change is for consistency with the card's own "You do not claim to BE the river".
- **Order:** after items 1 and A6.

---

## 3. Mediated voice: dramatist vs speaker — patches 06 (3a) and 09 (3b)

### Evidence from the shipped cards (CONFIRMED)

**Plato**, after `389a08c` (voices §9; 7 surgical patches):
- `characteristic_moves[9]`: "I do not deposit knowledge in you. Through Socrates — who claims his mother Phaenarete was a midwife and his own art a midwife's art for souls — I have him attend the labour of your thinking… The image is mine to use through him; the biography belongs to Socrates."
- `metaphorical_repertoire["midwifery and birth"]`: "Through Socrates — son of Phaenarete the midwife, attending the labour of others' thoughts — I deploy: … The biography is Socrates'; the image is mine through him."
- `curated_corpus_passages.passages[7].header`: "Socrates tells young Theaetetus what he has inherited from his mother Phaenarete — that his art is midwifery, practised on souls."
- Headers [2], [3], [4] and [6] were patched the same way. **5 of the 7 patches are Pass 6 passage headers**, which the roadmap's "Pass 2/3/4a" scope misses.
- Method moves stay in Plato's first person, e.g. `characteristic_moves[0]` "I refuse your list… I want the one nature…". **Method is the composer's; biography and utterance belong to the speaker.**

**Where the collisions are in the pipeline's own output (CONFIRMED by grep of `athens-2026/voices/plato/04_generation/`):**

| Pass output | Collisions |
|---|---|
| Pass 4a | "I am the son of…", "son of Phaenarete" |
| Pass 6 | headers [2] "Glaucon had pressed me toward the third and greatest wave; I went…", [3] "I told Glaucon the tale of Er", [4] "I told Phaedrus under the plane tree…", [6] "I refused to propose a life of silence", [7] "I told young Theaetetus what I had inherited from my mother Phaenarete" |
| Pass 2, Pass 3 | none |

This is why item 3 is two patches. **3a** (Pass 4a and Pass 6, plus the trigger) has a failing control, so a draw can show a fix. **3b** (Pass 2 and Pass 3) is preventive: HANDOFF_2026_04_28 §13 proposed clauses there, but the current outputs show no collision, so a draw can only show "no harm". They can land together or 3a first.

**Scheherazade** (voices §22): the composer frame is in first person (`rhetorical_mode`: "I am a node in a chain of tellers, not the origin of what I tell"). The operator also kept third-person "the voice" meta in several fields (`characteristic_moves[10]`, `banned_language[0]/[8]/[9]/[11]/[15]`, `banned_modes[1]/[4]/[8]/[13]/[14]`). The patch stays in the first-person composer frame, as Plato's patches do, and does not license third person.

**Marley and Octopus** are already covered by the `lyrics_patterns_only` blocks and the two-channel contract.

**Current prompts:** no composer clause in Pass 2/3/4a/6 (CONFIRMED by grep). Pass 6's header rule invites the collision: "the `header` in second-person addressed to the voice is the voice remembering the scene" (`persona_pass_6_corpus.md:79-85`).

### Design: the trigger (O3)

- **(A, recommended) `mediation_stance: "composer"`.** `mediation_stance` is already rendered into Passes 2/3/4a/4b/5/6 (`run_persona_pipeline.py:494, 520, 678, 713, 742, 780`). The block fires only for voices the curator marks, which matches HANDOFF §13: "voice-architecture-conditional, NOT universal".
- **(B) A universal clause.** Every voice pays the density cost; 8 of 10 don't need it.
- **(C) Key on `type == "fictional"`.** Misses Plato.

Pass 0a doesn't propose `mediation_stance` today; Whanganui's was set by hand. Under `ONBOARDING.md:68` ("No hand-authoring voice_configs bypassing Pass 0a"), Pass 0a should propose it, and node 0 should validate it (it didn't; N11).

### Patch 06 — item 3a (Pass 0a, node 0, Pass 4a, Pass 6)

~~~diff
diff --git a/personas/flows/shared/node0_validation.py b/personas/flows/shared/node0_validation.py
index d42802a..46293c1 100644
--- a/personas/flows/shared/node0_validation.py
+++ b/personas/flows/shared/node0_validation.py
@@ -113,6 +113,18 @@ def validate_input(voice_input: dict[str, Any]) -> dict[str, Any]:
             ),
         )
 
+    # mediation_stance — optional; must be a known stance when present
+    # (Stage 4 item 3 adds "composer").
+    ms = voice_input.get("mediation_stance")
+    if ms not in (None, "none", "transmission_witness", "composer"):
+        raise InputRejected(
+            status="REJECTED",
+            reason=(
+                f"Invalid mediation_stance {ms!r}. Must be null, 'none', "
+                f"'transmission_witness' or 'composer'."
+            ),
+        )
+
     # Required string fields — Phase B redesign drops `conference_context`
     # (Pass 7b loads conference facts + audience + roster directly from the
     # split inputs/ files; voice_config no longer carries conference context).
diff --git a/personas/flows/shared/prompts/pass_0a_voice_config.md b/personas/flows/shared/prompts/pass_0a_voice_config.md
index c141c21..28a2744 100644
--- a/personas/flows/shared/prompts/pass_0a_voice_config.md
+++ b/personas/flows/shared/prompts/pass_0a_voice_config.md
@@ -55,6 +55,8 @@ Produce a JSON object with exactly these fields:
 
 - `corpus_constraint` (enum: `"full"` | `"lyrics_patterns_only"` | `"hostile_read_against_grain"`): `"full"` = primary texts can be quoted. `"lyrics_patterns_only"` = copyrighted musical corpus; produce pattern descriptions not excerpts. `"hostile_read_against_grain"` = primary record is hostile accounts requiring reconstruction. Default `"full"`.
 
+- `mediation_stance` (`null` | `"composer"` | `"transmission_witness"`): how the voice's first person relates to the persons its work speaks through. `null` for most voices. `"composer"` when the corpus speaks through persons the voice composed — a dramatist behind the dialogue's speakers (Plato through Socrates), a frame-teller behind the tale's characters (Shahrazād). `"transmission_witness"` when the speaking position is a construction stewarding a mediated legal or cosmological record (the Whanganui River through Te Pou Tupua and the 2017 Act). Justify in review_doc.
+
 - `manual_grounding` (string | null): Echo back the manual_grounding text if provided (verbatim — do not normalize or paraphrase), else null.
 
 - `wikipedia_url` (string | null): Echo back if provided; else omit field entirely (do NOT emit `null`).
@@ -81,6 +83,7 @@ Markdown document. Under 2 minutes to read. Structure:
 | voice_mode | ... | proposed |
 | hostile_sources | ... | proposed |
 | corpus_constraint | ... | proposed |
+| mediation_stance | ... | proposed |
 
 (`auto` reserved for mechanical-only decisions — currently only `name` normalization. Everything else is `proposed` — editorial judgment, please review.)
 
diff --git a/personas/flows/shared/prompts/persona_pass_4a_voice.md b/personas/flows/shared/prompts/persona_pass_4a_voice.md
index a6a9068..066e5f9 100644
--- a/personas/flows/shared/prompts/persona_pass_4a_voice.md
+++ b/personas/flows/shared/prompts/persona_pass_4a_voice.md
@@ -179,6 +179,17 @@ BLOCK 2 — GUARDRAILS:
     person addressed to it; never the entity's first person.
 {% endif %}
 
+{% if mediation_stance == "composer" %}
+- COMPOSER DISCIPLINE (the voice composes the persons its work speaks
+  through). characteristic_moves: describe each move as the composer's —
+  "I have Socrates demand…", "I tell a tale whose shape mirrors…" — and
+  anchor it in the work and the speaker; the method may stay in the voice's
+  first person, the speaker's biography and lines may not.
+  metaphorical_repertoire: images deployed through a speaker say so
+  ("Through Socrates I deploy…; the biography is his"). Every other field:
+  the same rule.
+{% endif %}
+
 - REFERENCE NOT DISPLAY (critical — Boddice sanity check): The card's
   period-vocabulary is REFERENCE MATERIAL for the voice's reasoning, not
   required output. Use period-specific terms when the moment calls for it —
diff --git a/personas/flows/shared/prompts/persona_pass_6_corpus.md b/personas/flows/shared/prompts/persona_pass_6_corpus.md
index 1f2bb99..c8c2db0 100644
--- a/personas/flows/shared/prompts/persona_pass_6_corpus.md
+++ b/personas/flows/shared/prompts/persona_pass_6_corpus.md
@@ -160,6 +160,17 @@ BLOCK 2 — GUARDRAILS:
   — never in expository third-person about the construction.
 {% endif %}
 
+{% if mediation_stance == "composer" %}
+- COMPOSER HEADERS. This overrides "the voice remembering the scene" above: a
+  header recalls the scene as its composer, not as a speaker inside it.
+  "Socrates tells young Theaetetus what he has inherited from his mother" —
+  not "I told young Theaetetus what I had inherited from my mother". Headers
+  may use the composer's first person ("I tell this when…", "I set this at
+  the counter-penalty"). why_selected follows the same rule, and so does
+  corpus_metadata.voice_basis ("I speak through these passages as I do
+  through Socrates and the others").
+{% endif %}
+
 BLOCK 3 — FIELD SPECIFICATION:
 
 curated_corpus_passages — Object with two keys:
diff --git a/personas/tests/test_conditional_block_coverage.py b/personas/tests/test_conditional_block_coverage.py
index ae059e4..cc09d96 100644
--- a/personas/tests/test_conditional_block_coverage.py
+++ b/personas/tests/test_conditional_block_coverage.py
@@ -45,6 +45,8 @@ _PASS_FIELDS = {
 # (template, stance, strict). strict: every field must be named in the block.
 # Not strict: a field may instead be covered by a catch-all line.
 _BLOCKS = [(template, "transmission_witness", True) for template in sorted(_PASS_FIELDS)]
+_BLOCKS += [("persona_pass_4a_voice", "composer", False),
+            ("persona_pass_6_corpus", "composer", True)]
 
 _CATCH_ALL = re.compile(r"\b(Any|Every) (other )?field\b")
 
~~~

### Patch 09 — item 3b (Pass 2, Pass 3)

~~~diff
diff --git a/personas/flows/shared/prompts/persona_pass_2_identity_boundaries.md b/personas/flows/shared/prompts/persona_pass_2_identity_boundaries.md
index 438dd95..8141fc7 100644
--- a/personas/flows/shared/prompts/persona_pass_2_identity_boundaries.md
+++ b/personas/flows/shared/prompts/persona_pass_2_identity_boundaries.md
@@ -609,6 +609,36 @@ name whose voice its "I" carries. Example value:
   river speaking and not the construction's claim."
 {% endif %}
 
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
+  composer's verb: "I have Socrates demand the form (Euthyphro 6d-e)",
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
+
 BLOCK 4 — VOICE TYPE:
 {% if type == "human" %}
 Ground in the biocultural world reconstructed per Boddice §13/§14. Formative
diff --git a/personas/flows/shared/prompts/persona_pass_3_intellectual_core.md b/personas/flows/shared/prompts/persona_pass_3_intellectual_core.md
index 4a59de0..5605288 100644
--- a/personas/flows/shared/prompts/persona_pass_3_intellectual_core.md
+++ b/personas/flows/shared/prompts/persona_pass_3_intellectual_core.md
@@ -218,6 +218,17 @@ BLOCK 2 — GUARDRAILS:
   third-person about the construction.
 {% endif %}
 
+{% if mediation_stance == "composer" %}
+- COMPOSER DISCIPLINE (the voice composes the persons its work speaks
+  through): constitution, concept_lexicon and reasoning_method are the
+  composer's. Steps describe the method the voice practises through its
+  speakers, in the voice's first person; worked demonstrations cite the work
+  and the speaker ("in the Theaetetus I have Socrates…", "on my first night I
+  tell the Merchant and the Demon"). finds_compelling and resists are the
+  composer's own tastes, not a speaker's. Never give the voice a speaker's
+  biography or claim a speaker's utterance as the voice's own act.
+{% endif %}
+
 BLOCK 3 — FIELD SPECIFICATIONS:
 
 {# Per FU#12-A guardrail above: do NOT emit merge-source provenance brackets
diff --git a/personas/tests/test_conditional_block_coverage.py b/personas/tests/test_conditional_block_coverage.py
index cc09d96..4c62de4 100644
--- a/personas/tests/test_conditional_block_coverage.py
+++ b/personas/tests/test_conditional_block_coverage.py
@@ -45,7 +45,9 @@ _PASS_FIELDS = {
 # (template, stance, strict). strict: every field must be named in the block.
 # Not strict: a field may instead be covered by a catch-all line.
 _BLOCKS = [(template, "transmission_witness", True) for template in sorted(_PASS_FIELDS)]
-_BLOCKS += [("persona_pass_4a_voice", "composer", False),
+_BLOCKS += [("persona_pass_2_identity_boundaries", "composer", False),
+            ("persona_pass_3_intellectual_core", "composer", False),
+            ("persona_pass_4a_voice", "composer", False),
             ("persona_pass_6_corpus", "composer", True)]
 
 _CATCH_ALL = re.compile(r"\b(Any|Every) (other )?field\b")
~~~

Pass 4b and Pass 5 need no block: the shipped artifact fields already hold the composer frame (Plato's `medium`: "I write a short dialogue… between named persons").

### Checks

All draws use a sandbox config with `"mediation_stance": "composer"`.

- **Plan B.** Plato (**O2**): Pass 6, then Pass 4a, for 3a ($1.00); then Pass 3, then Pass 2, for 3b ($1.32).
- **Plan A.** Plato and Scheherazade, the same four passes, 3 treatment and 2 fresh control draws each ($23.7); both are among the five rebuilds.
- **Control (free).** The athens-2026 outputs above.
- **Mechanical checks (3a):** no "my mother Phaenarete"; no "son of Phaenarete" bound to "I"; no "I told young Theaetetus", "I told Glaucon", "I told Phaedrus", "I ask Euthyphro", "I tell the Athenian jury"; the five patched headers name Socrates. The operator left headers [0], [1] and [5] alone as borderline, so read those rather than failing them.
- **3b is a no-harm check.** The control has no collision in Pass 2 or 3, so the draw can only show that the composer block did not damage those fields, and that the composer frame appears where it should (`epistemic_frame_statement` names the voice as composer).
- **Read** against the `389a08c` fields. Check for over-correction: method moves must stay in the first person (no "Plato's method…").
- **Free.** The coverage test gains the composer blocks (in the patches).

### Risks and order

- **The `3feb2b2` class.** Cumulative additions have degraded texture before. The conditional limits exposure to two voices.
- **The validator treadmill.** 7a re-flagged Scheherazade's §9 choices four times (voices §22).
- **Order:** after item 4; patch 06 extends item 4's test.

---

## 6. Operator direction reaches Pass 4a/4b (§23 P0) — patch 07

### Evidence (CONFIRMED)

**What each voice_config carries.** `editorial_rationale` is non-null for 3 of 10 voices: Octopus (5,485 chars), Whanganui (3,892), Marley (354). `manual_grounding` is operator-authored for the same three (7,555 / 6,344 / 1,593 chars); for the other seven it is a Wikipedia lead (148–750 chars).

**Marley's config is stale against the shipped v2 card (N2).**

| Where | Says |
|---|---|
| voice_config `manual_grounding` | "THE LOAD-BEARING DIRECTION. The voice's artifact at runtime IS a song, not a piece of writing… (a) an original lyric…" |
| voice_config `editorial_rationale` | "The architectural choice (song-as-artifact, not prose-about-song)…" |
| card `medium` | "I give you a reasoning, and a riddim under it… Me nah sing you a new song — the songs are already sung." |
| card `technical_capabilities` | "No new lyrics composed in the patterning of my catalogue" |
| card `banned_modes[13]` | "Composing new lyrics in the catalogue's patterning" |

**Pass 4b contradicts itself (N1).** `persona_pass_4b_artifact.md:87-93` is the v1 mid-session fix of voices §23; the v2 block (`:122-166`) replaced the block and left this guardrail.

**The non-default forms shipped without the config reaching 4a/4b** (Cleopatra prostagma, Scheherazade ḥikāya, Whanganui bilingual, Octopus JSON + prose, Marley prose + riddim; voices §23). There is no card for this item to catch up to; it is a pipeline capability.

**Consequence.** Piping the config into 4a/4b as filed would feed Marley's v1 song mandate against the v2 blocks, and would feed Wikipedia leads (reception commentary) into passes whose STRIP rules forbid it (`persona_pass_4b_artifact.md:45-56`).

### Design options (O4)

- **(a, recommended) A new optional field `artifact_direction`.** Curator-authored, null by default. Piped into the 4a and 4b user prompts, with `editorial_rationale` into 4b. Precedence in the prompt: a conditional block (`corpus_constraint`, `mediation_stance`) > `artifact_direction` > the default field specs. Seven voices see no change.
- **(b) Pipe `manual_grounding` + `editorial_rationale` as filed.** Adds Wikipedia text to seven voices' passes. Not recommended.
- **(c) Pipe `editorial_rationale` only.** Marley's operator put the artifact direction in `manual_grounding`, and the rationale question isn't about form (`pass_0a_voice_config.md:110`).

**Prerequisite for any option:** the operator reconciles Marley's config with v2 (an athens-2026 data edit). The `:87-93` fix can land on its own at any time: it removes text, and the v2 block already governs Marley.

### Patch (option a)

~~~diff
diff --git a/personas/flows/shared/prompts/pass_0a_voice_config.md b/personas/flows/shared/prompts/pass_0a_voice_config.md
index 28a2744..f40d30a 100644
--- a/personas/flows/shared/prompts/pass_0a_voice_config.md
+++ b/personas/flows/shared/prompts/pass_0a_voice_config.md
@@ -61,6 +61,8 @@ Produce a JSON object with exactly these fields:
 
 - `wikipedia_url` (string | null): Echo back if provided; else omit field entirely (do NOT emit `null`).
 
+- `artifact_direction`: ALWAYS set this to `null`. The curator fills it in only when the voice's artifact departs from the default written piece (a song, a two-channel display, a bilingual citation form), stating the form the voice produces. When a voice's artifact architecture changes, this field must be updated with it.
+
 - `editorial_rationale`: ALWAYS set this to `null`. The curator fills it in post-review; the model must not propose it. The review_doc will explicitly ask the curator to provide it.
 
 Do NOT include: `conference_context` (dropped in Phase B), `primary_text_sources`, `voice_type_adjustments_needed`, `counter_tradition_scholars`, or any other editorial-assets fields.
diff --git a/personas/flows/shared/prompts/persona_pass_4a_user.md b/personas/flows/shared/prompts/persona_pass_4a_user.md
index bc0af3a..38ea466 100644
--- a/personas/flows/shared/prompts/persona_pass_4a_user.md
+++ b/personas/flows/shared/prompts/persona_pass_4a_user.md
@@ -59,6 +59,13 @@ grounding your voice-characterization):
 
 Previously completed fields (summary):
 {{ pass_2_3_summary }}
+{% if artifact_direction is defined and artifact_direction %}
+
+Operator direction for this voice's artifact (from voice_config; shape the
+rhetorical fields so the artifact can carry it; a conditional block in your
+instructions wins where it conflicts):
+{{ artifact_direction }}
+{% endif %}
 
 Produce 7 Persona Card voice fields (rhetorical_mode, characteristic_moves,
 register_and_tone, metaphorical_repertoire, preferred_vocabulary,
diff --git a/personas/flows/shared/prompts/persona_pass_4b_artifact.md b/personas/flows/shared/prompts/persona_pass_4b_artifact.md
index 16c34f6..f7844b6 100644
--- a/personas/flows/shared/prompts/persona_pass_4b_artifact.md
+++ b/personas/flows/shared/prompts/persona_pass_4b_artifact.md
@@ -85,12 +85,11 @@ BLOCK 2 — GUARDRAILS:
   writing? If no, rewrite.
 
 - medium: emerges from what the figure actually produced. The default is text
-  (the audience reads over coffee). BUT: if the voice's primary medium is
-  song/lyric/music (signaled by corpus_constraint == "lyrics_patterns_only"),
-  the medium IS the song, expressed as a two-shape artifact (lyric +
-  Suno-style kind-hint). Do NOT bridge song → prose. If the voice's primary
-  medium is purely oral (dictation, speech) WITHOUT musical setting, then
-  bridge to a written format that preserves the voice's character.
+  (the audience reads over coffee). If corpus_constraint is
+  "lyrics_patterns_only", follow the MUSICAL-CORPUS VOICE ARTIFACT VARIANT
+  below. If the voice's primary medium is purely oral (dictation, speech),
+  bridge to a written format that preserves the voice's character. If the
+  user prompt carries operator direction for the artifact, honour it.
 - quality_criteria: 3-5 specific, testable criteria. Each criterion
   tests 1-n card fields by name (single field, or compounded with
   and/or logic). The criteria collectively should answer "Could
diff --git a/personas/flows/shared/prompts/persona_pass_4b_user.md b/personas/flows/shared/prompts/persona_pass_4b_user.md
index 446c70c..2119201 100644
--- a/personas/flows/shared/prompts/persona_pass_4b_user.md
+++ b/personas/flows/shared/prompts/persona_pass_4b_user.md
@@ -7,6 +7,19 @@ rhetorical_mode: {{ rhetorical_mode }}
 characteristic_moves: {{ characteristic_moves }}
 
 register_and_tone: {{ register_and_tone }}
+{% if artifact_direction is defined and artifact_direction %}
+
+Operator direction for this voice's artifact (from voice_config). Honour it;
+where a MUSICAL-CORPUS or TRANSMISSION-WITNESS block in your instructions
+says otherwise, that block wins:
+{{ artifact_direction }}
+{% endif %}
+{% if editorial_rationale is defined and editorial_rationale %}
+
+Why this voice is in this Assembly (the curator's note — context for what the
+artifact is for, not a form instruction):
+{{ editorial_rationale }}
+{% endif %}
 
 Produce 8 Persona Card artifact fields (medium, technical_capabilities,
 characteristic_output_structure, relationship_to_detailed_response,
diff --git a/personas/run_persona_pipeline.py b/personas/run_persona_pipeline.py
index 4568c97..b1cc342 100644
--- a/personas/run_persona_pipeline.py
+++ b/personas/run_persona_pipeline.py
@@ -707,6 +707,7 @@ def _pass_4a():
         cross_disciplinary_frames=chunk_vars["cross_disciplinary_frames"],
         primary_texts=primary_block_for_voice,  # (c.1): augmented for lyrics_patterns_only voices
         pass_2_3_summary=pass_2_3_summary,
+        artifact_direction=vi.get("artifact_direction"),  # Stage 4 item 6
     )
     # Opus + adaptive thinking: long-context pattern recognition across primary
     # texts. Especially load-bearing for hard voice types (musical, system, etc.)
@@ -731,7 +732,9 @@ def _pass_4b():
                    pass_2_3_4a_summary=pass_2_3_4a_summary,
                    rhetorical_mode=json.dumps(pass4a["fields"].get("rhetorical_mode", "")),
                    characteristic_moves=json.dumps(pass4a["fields"].get("characteristic_moves", [])),
-                   register_and_tone=json.dumps(pass4a["fields"].get("register_and_tone", "")))
+                   register_and_tone=json.dumps(pass4a["fields"].get("register_and_tone", "")),
+                   artifact_direction=vi.get("artifact_direction"),  # Stage 4 item 6
+                   editorial_rationale=vi.get("editorial_rationale"))
     # 2026-04-23: model upgraded claude-sonnet-4-6 → claude-opus-4-7 + thinking
     # ON (quality-tuning checklist). Pass 4b owns 8 output_characteristics
     # fields and is CT-only (no chunk reads); baseline Pass 7a flagged 6 of
~~~

Notes on the patch:
- The user-prompt blocks are guarded with `is defined`, so `personas/scripts/standalone_pass4b_test.py`, which also renders `persona_pass_4b_user`, is not affected.
- With a null direction and rationale, the patched user prompts render byte-identical to `main`'s (checked). For the seven voices without direction, only the 4b system prompt changes, by the `:87-93` rewrite.
- No schema edit (N11). The new key needs no validation: it is an optional string.

### Checks

- **Free.** The render-identity check above.
- **Plan B.** Marley Pass 4b, then Pass 4a, with `artifact_direction` set to the v2 form in the sandbox config ($0.22 + $0.73); Arendt Pass 4b as the default-voice check of the rewritten guardrail ($0.29). Total $1.24.
- **Plan A.** Also Whanganui and Octopus Pass 4b, which carry real rationales; 3 treatment and 2 fresh control draws each ($8.7). Marley is one of the five rebuilds.
- **Control (free).** The athens-2026 Pass 4a/4b outputs.
- **Checks.** Marley's `medium` and `technical_capabilities` stay prose + instrumental: no "lyric", "chorus", "verse" or "kind-hint" as the artifact. Arendt's form and length range match her control's. A Marley draw that drifts to song is a hard fail.

### Risks and order

A stale direction recreates the Marley problem; the Pass 0a text says the field must be updated when a voice's artifact architecture changes. Order: after item 3, and after O4 and the sandbox reconciliation.

---

## 5. Gap-H: `topics_requiring_care` for formulations that invite uncharacteristic work — patch 08

### Evidence

- **No target on the cards (CONFIRMED).** The Group-1 voices' `topics_requiring_care` lists hold content topics only. The memo patches that would have been canon were never applied (`_workspace/archive/session-artifacts/MEMO_2026_05_07_card_patches_from_external_reader.md:7`: "NEVER SEPARATELY APPLIED"). This item catches up to a reader's review of dryrun artifacts, not to the cards.
- **Reader evidence (tracker-sourced):** Battuta "a fatwa in Rihla clothing… he does not produce four-part typologies"; Cleopatra "she ratifies, she does not theorise about what ratification is"; Plato "Kleitōn capitulates rather than resisting".
- **Prohibitions are already on the cards and didn't hold (N8; presence CONFIRMED, the causal reading is an INFERENCE).** Pass 7c emitted anti-structure `banned_modes` for Battuta [11], Arendt [19] and [21], Lovelace [12], Dostoevsky [13]; Cleopatra has [14]–[16]. Battuta's was on the card during the wbbf26 dryrun (the timing is PLAUSIBLE, from snapshot names). The missing half is the positive move (FU#32's STRIP + USE).
- **Placement.** `ONBOARDING.md:72` puts a voice's genuine refusals in `topics_requiring_care` / `hard_limits`. Step 1 and Step 2 both read `topics_requiring_care` (`card_assembly.py:82-96`).

### Options (O5)

- **(a, recommended)** One `topics_requiring_care` entry: the uncharacteristic move plus the native move to make instead.
- **(b)** A Pass 4a `banned_modes` pair, next to the 7c prohibitions that didn't hold.
- **(c)** A runtime Step 2 prompt change (not Stage 4).

### Patch (option a)

~~~diff
diff --git a/personas/flows/shared/prompts/persona_pass_2_identity_boundaries.md b/personas/flows/shared/prompts/persona_pass_2_identity_boundaries.md
index 13815bc..438dd95 100644
--- a/personas/flows/shared/prompts/persona_pass_2_identity_boundaries.md
+++ b/personas/flows/shared/prompts/persona_pass_2_identity_boundaries.md
@@ -477,6 +477,17 @@ neither reproducing Dostoevsky's actual antisemitism, nor laundering it,
 nor engaging it critically, but virtue-signaling via hyphenation in a
 way he never did. This clause makes the failure mode explicit.)
 
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
+
 hard_limits — 3-5 absolute prohibitions. Character-breaking only. Do NOT
 duplicate the epistemic frame's gap-naming instruction. Hard limits catch
 specific failure modes: producing arguments the voice couldn't make, adopting
~~~

### Checks

- **Card level.** The entry is present, names an uncharacteristic move and a native one, and has none of `decline|refuse to answer|cannot be answered|say so|name the gap`.
- **Behaviour level (the real gate).** Put the emitted entry into a sandbox copy of the voice's shipped card and run Step 1 + Step 2 for that voice (the command is in §0.4, A3). The same voice on the unchanged shipped card, same briefings, is the control. Pass: no typology, the native form held, and the voice still engages. A decline is a hard fail. Read the `focus_decision` prose: the refusal substring match (roadmap 0.2, still open, no OPEN_ITEMS home) can drop a voice from the edition.
- **Which run.** The reader's evidence is the wbbf26 dryrun, archived with its briefings and artifacts at `athens-2026/runs/_archive/preconference_wbbf_programme_2026_05_06/`. It ran on 2026-05-06, before the stance rewrite of `08a8253`, so its artifacts came from an older card. Draw the control fresh, on today's shipped card, and keep the archived artifact as a second, older control.
- **Plan B.** Battuta: Pass 2 ($0.82); then two voice runs on the wbbf26 briefings, one on the shipped card and one on the shipped card plus the entry ($0.69 each, from that run's recorded usage). Total $2.20.
- **Plan A.** Pass 2 for Battuta, Cleopatra, Plato (**O2**) and Arendt (the over-application check: the entry is omitted or harmless), 3 treatment draws each ($10.8); then Battuta, Cleopatra and Plato on the wbbf26 briefings, 2 treatment runs and 1 control each ($8.2). Total $19.0.
- A card-level draw alone is not an honest check here: the evidence is behavioural, and N8 shows that text on the card did not change the behaviour.

### Risks and order

Decline-to-engage is the failure the hook ban exists for; the patch forbids declining in so many words. The evidence is one reader and one dryrun. Last.

---

## Coverage

**Read in full:** the brief; the review; roadmap `PLAN_2026_06_12_post_athens_roadmap.md`; voices `OPEN_ITEMS.md` §1–§10 and §18–§37; `HANDOFF_2026_04_28.md` §12–§15; `MEMO_2026_05_07_card_patches_from_external_reader.md`; the Pass 0a, 0b tailor, 2, 3, 4a, 4b prompts and their user prompts; `persona_derive.md`; `sentinel_regen.py` (at `4e61444`, and the parts of the `main` version cited in §0.1); `invalidate_cache.py`; `chat_prompt_builder.py`; `io.py`; `node0_validation.py`; `schemas/voice_config.py`; `prompt_render.py`.

**Read in part:** `docs/AI_Assembly_Persona_Card_v2.md`; `run_persona_pipeline.py` (the ranges cited); `runtime/flows/voice/card_assembly.py` (1–459); Pass 5, 6 and 7a prompts (the ranges cited); `ONBOARDING.md`; runtime `OPEN_ITEMS.md` (C67, C68); `REVIEW_2026_09_28_untouched_code.md` (A5, A6).

**Card data (athens-2026, read only):** all 10 cards, voice configs and Pass 2 outputs; Plato's Pass 3, 4a and 6 outputs; the `usage` blocks of the pass, CT and Derive outputs for eight voices; the presence of the flag, `_fix_log.json` and the 7-series outputs for all 10; Lovelace's `01_research/`; the token counts of the Night 1 and archived wbbf26 voice runs.

**Not read:** `AI_Assembly_Voice_Pipeline.md`, the runtime Step 2 prompts, Passes 1.x. Of the runtime CLI, only the argument list of `voice_flow.py` was read.

**Scratch scripts** (session scratchpad, not in the repo; none calls a model, writes outside the scratchpad, or runs git in athens-2026): `extract_cards.py`, `provenance_check.py`, `make_patches.py`, `verify_patches.py`, `run_new_tests.py`, `order_check.py`, `revise_two_plans.py`.

---

## Revision log

### 2026-09-30 (first revision) — after the Opus review of 2026-09-29

The test plan this revision introduced was written for a spend limit that was lifted later the same day; the second entry below replaces it. The review's evidence verdicts were accepted unless noted under "Disagreements".

**Changed because the facts changed**
1. **Spend.** The $113 plan and its $150 recommendation were replaced by a single-draw plan with a free control, $5.62 for six items. (Superseded: see the second revision.)
2. **Harness.** §0.1 now describes the script as repaired in `f7e0d4c`: A5 and the display-name gap (old G6) are fixed; G1–G5 are restated for today's code; N10 added.
3. **Derive.** New §0.2 step 2: deleting the review flag in the sandbox makes the run halt at the review gate before Derive. The old text said a run without the flag might pay for 7-series calls; reading the cached files shows it doesn't. A $0 dry run is added as the first step.
4. **Line numbers.** Runner references moved to `main` (`86998b4`), +5 from `4e61444`. Prompt line numbers are unchanged.
5. **C67 R1.** The A6 sentence about runtime C67 R1 is removed; it was fixed in `02006f5`.

**Corrected errors**
6. **Diffs.** All hand-written diff blocks are replaced by generated `git diff` output (§0.5). This removes the wrong hunk counts, the no-op Pass 4b hunk, and the two truncated context lines (Pass 0a in item 3, Pass 2 `:458` in item 5).
7. **Pass 4b placement.** The witness per-field lines moved above the "Twin-failure-modes to ban" list.
8. **A6 length rule.** "3–25 words" is now "1–25 words", in the prompt text and the check. The examples changed so they don't hand the sentinels their answers.
9. **Item 1 vs Whanganui.** The spec said "MANDATORY, second person" while item 4 asked for first person, and the checks failed the shipped Whanganui stance. The spec now defers to a mediation-stance block for the person, item 4's line says so, the checks have a witness variant, and `translation_protocol` is matched with or without the underscore. Whanganui left item 1's sentinel set; item 4's Pass 2 draw covers it.
10. **"Nine share one template."** Now "eight", with Octopus and Whanganui apart.
11. **`anchored_override` key.** The argument from the chat builder's test is withdrawn. The reason given now is that all 10 shipped cards carry the key with null. Listed as O11.
12. **Schema edits.** The proposed edits to `schemas/voice_config.py` are dropped: no code imports it. The `mediation_stance` check is in `node0_validation.py` (patch 06). N11 added.
13. **Item 2 sentinel.** The Pass 0a examples no longer quote the sentinel voices; the paid Pass 0a run is optional and must use its own sandbox. A unit test replaces the paid check.
14. **§18 departure.** Keeping `voice_config.name` bare is now stated as a deliberate departure from voices §18, with reasons, and listed as O10.
15. **S1 wording.** For A6 the target is the card spec, not the cards.
16. **N2.** "Harmless now" is narrowed: the Pass 0b tailor reads `editorial_rationale`.
17. **N4.** Perplexity names Hollings, Martin and Rice once with "(2020s)"; "no year" was wrong.
18. **N9 and the item-4 table.** `hard_limits[1]` is in the Pass 2 output too; the table's "—" is replaced.
19. **N1.** Noted that Task 1 reported the same issue.
20. **§0.4 of the old doc.** CT compress costs are now taken from usage files at Sonnet prices ($0.04–0.18, not "≤ $0.3"), and Derive ($0.32–0.44) is listed.

**Added**
21. **Item 3 split.** 3a (Pass 0a, node 0, Pass 4a, Pass 6) has a failing control in Plato's pass outputs; 3b (Pass 2, Pass 3) does not, and was deferred in that revision. The grep evidence is in item 3.
22. **Tests in the patches.** `test_conditional_block_coverage.py` (patch 05, extended by 06 and 09) and `test_derive_post.py` with `flows/shared/derive_post.py` (patch 04). The coverage test caught a gap in this doc's own Pass 3 composer block (`finds_compelling`, `resists`), which is fixed.
23. **`_assembly_place()`** is now real code in patch 02, and the template uses a `default` filter.
24. **Pass 0a count line.** Patch 04 replaces "8-9 fields" with wording that has no number, so later patches don't depend on each other through that line.
25. **Pass 6 composer block** names `corpus_metadata.voice_basis`.
26. **Order.** The doc's sections now follow the landing order.

**Disagreements with the review**
- **The review's spend estimate** (every regen pays for Derive; about $150 for the plan as first written). That holds only if the review flag stays in the sandbox and the control arm is drawn fresh. With the flag deleted (§0.2, from `run_persona_pipeline.py:901-904`, `:1447`, `:1969-1991` and the cached files in all 10 voice folders) and the athens-2026 outputs as the control, a single-draw check costs $0.2–0.9. The halt is read from code, not run; the $0 dry run is the test.
- **§1-key (DOUBTFUL).** The review is right that the test does not force the key. The proposal stands for a different reason: the shipped cards have the key with null, and "cards are canon". It is now O11.
- **§2-design (DOUBTFUL).** Agreed that it needed an operator decision (now O10). The proposal itself stands, on the four reasons in item 2.
- **§3-cost.** The review's $20–24 for item 3 assumed full Pass 2→6 chains on two voices. One draw of the two passes that show the collision, on one voice, is $1.00.

### 2026-09-30 (second revision) — the spend cap was lifted

The operator lifted the USD 10 Stage 4 cap on 2026-09-30 (relayed by the main session; the roadmap on `main` at `e674893` still records the cap, at its line 251).

1. **Two test plans** replace the single capped plan: Plan A, best for quality (≈ $175), and Plan B, best value (≈ $14), side by side in the Summary and in full in §0.4, each with its assumptions and what it does and doesn't show.
2. **Recommendation added:** Plan B, then Plan A's end state (rebuilt cards and a runtime comparison), about $95 in all. The operator decides.
3. **Plan B is wider than the first revision's $5.62 plan.** It adds item 1's fictional and calendar variants, item 3b, item 5 and an end-state chain for Whanganui, one draw each.
4. **Cap framing removed** from the Summary, O1, O5, §0.2 (title, the stop rule), §0.4 and every item's check section, which is now "Checks" with a Plan B and a Plan A line.
5. **Item 3.** 3b is no longer deferred; both halves are in both plans. The landing order is 7 → 1 → A6 → 2 → 4 → 3a → 3b → 6 → 5.
6. **Item 5's check** now runs on the archived wbbf26 briefings, with the control drawn fresh on today's shipped card (the archived artifacts came from an older card). Its cost is from that run's recorded usage: $0.69 for a Battuta voice run, not the earlier estimate of about $2.5.
7. **§0.3 additions:** runtime voice-run costs from the Night 1 and wbbf26 token counts; the Pass 3 and Pass 5 figures; an estimate for a rebuild from Pass 2 through 7a FINAL, marked PLAUSIBLE.
8. **§0.2 additions:** the chain order for an end-state check (upstream first), and two more voices in the sandbox command.
9. **Base.** `main` moved to `e674893`; the files the patches touch are unchanged there.
10. **Patches:** unchanged, byte for byte.
