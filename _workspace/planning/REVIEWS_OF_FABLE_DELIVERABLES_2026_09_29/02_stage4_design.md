# Review of `_workspace/planning/voices/DESIGN_2026_09_28_stage4_prompt_backport.md`

Reviewed 2026-09-29 against `main` at `0910a66` (prompts unchanged since the doc's `4e61444`; `run_persona_pipeline.py` +5 lines at L390 from `f7e0d4c`; `sentinel_regen.py` rewritten in `f7e0d4c`). Read-only. No API calls. No git in athens-2026. Scratch checks (in this folder): `cards.py` (card and Pass 2 field dumps), `applytest/` (every diff block extracted, dry-run with `git apply --check` and `patch --dry-run` on copies of the current files, plus `hunkcheck.py`, which looks up each hunk's old-side text regardless of hunk headers).

## Verdict

- **Quality: high.** The evidence work is careful. Every card quote, count and prompt `file:line` I checked is accurate, and most of its new findings (N1–N6, N8, N9) hold up.
- **Trust:** trust the evidence and the diagnosis. Don't trust the spend plan or the sentinel protocol as written. The diff *text* matches the current prompts (29 of 31 hunks), but none of the 15 diff blocks applies mechanically, so they must be applied by hand.
- **Biggest issue:** the plan costs about $113 and recommends a $150 cap. The operator has since capped Stage 4 at **USD 10** (`333f8a3`). The estimates also assume harness features that the `f7e0d4c` repair did not build (`--stop-after`, `--from-pass`, arms and draws). With today's harness, every regen draw also pays for a Derive call (about $0.32–0.44). As written, the plan can't run: under the cap it covers the gate shake-out, item 7 and item 2, and nothing else.

## Findings, one by one

| ID | Claim (short) | Verdict | Evidence / reason |
|---|---|---|---|
| S1 | 8 prompt changes; 5 have an exact target in the shipped cards (1, 2, A6, 3, 4) | PLAUSIBLE | Counts right. For A6 the target is the card **spec**, not the cards: 8 of 10 shipped `council_member_name` values are themselves off-spec |
| S2 | Spend ≈ $113; recommended cap $150 (O1) | STALE | Operator cap USD 10 (roadmap decisions block, `333f8a3`, after `4e61444`). The sum 2+6+11+10+1+11+32+14+26 = 113 is correct |
| S3 | Landing order 0→7→1→A6→2→4→3→6→5 | PLAUSIBLE | Dependencies are argued coherently. Under the cap, only 7 and 2 fit (see §0.5 row) |
| N1 | Pass 4b `:87-93` still gives the v1 song instruction, contradicting the v2 block `:122-166` | VERIFIED | Read both ranges. Task 1 found the same issue independently (`REVIEW_2026_09_28_prompts_correctness.md` #14), so file it once |
| N2 | Marley `voice_config` still mandates the v1 song artifact | VERIFIED | `manual_grounding` contains "THE LOAD-BEARING DIRECTION. The voice's artifact at runtime IS a song"; `editorial_rationale` says "song-as-artifact, not prose-about-song". Card `medium`/`technical_capabilities`/`banned_modes[13]` quotes are exact. Nuance: `editorial_rationale` *is* read by the Pass 0b tailor (`run_pass_0b_tailor.py:218`), so "harmless now" holds only until Marley's next build |
| N3 | `persona_derive.md:46` asks for `<voice_name from card>` but Derive's input excludes `voice_name` | VERIFIED | `:46` confirmed. `EXCLUDE_FROM_DERIVE` at `4e61444` L917/L2003 (HEAD +5). Shipped profile names are what the model guessed: "Plato", "Octopus", "Te Awa Tupua", "Shahrazād bint al-wazīr" |
| N4 | All 4 Lovelace phantom citations come from the Gemini scan | VERIFIED | Gemini `02_gemini_broad_scan.json` (gemini-2.5-pro, no citation list) holds all 4 with full bibliographic detail; Perplexity has 50 citations / 50 search_results and none of the four. The tailored §2 prompt holds Bensaude-Vincent; §3 holds Hollings 2020, Anderson 2023 and *Notes and Records*. Tailor note quote exact (`03_dr_prompts/02_tailoring_notes.json`). Minor: Perplexity says "Hollings, Martin, and Rice (2020s)", a decade, not "no year" |
| N5 | Whanganui's runtime prompt opens with two contradicting identities; the root is the Pass 2 system template `:269-277` | VERIFIED | `card_assembly.py:421-422` renders "You are {council_member_name}."; the shipped `epistemic_frame_statement` starts "You are Te Awa Tupua."; the template is at `:269-277` |
| N6 | 4 more names have first-person tails; 8/10 first lines mix grammatical person | VERIFIED | Plato "I withdraw my name", Battuta "honoured me", Scheherazade "called me", Marley "call I… I-and-I" |
| G1 | `regen` invalidates one pass; downstream passes stay stale | VERIFIED (still open) | `sentinel_regen.py:175-176` still calls `invalidate_cache.py --pass`; `invalidate_cache.py:100-104` deletes only that pass and its CT file |
| G2 | No stop-after; the sandbox copy carries `_operator_review_passed.flag`, so every run pays for Derive | VERIFIED (still open) | All 10 athens-2026 voices have the flag. `make_sandbox` uses `shutil.copytree` (`:144`) and copies it. The fast exit (HEAD `run_persona_pipeline.py` ~L902-975) deletes `derive_raw` and calls Opus. The runner has one positional arg plus `--project` (L51) |
| G3 | Structural diff (changed keys + 200 chars) measures noise | VERIFIED (still open) | `_diff_against_baseline` (`:190-233`) is unchanged from `4e61444` `:139-182` |
| G4 | The baseline is an older pass output, not the shipped card | VERIFIED (still open) | `resolve_baseline` (`:158-159`) maps to the same relative path in production, i.e. `04_generation/*.json`. The new docstring's "diff against the shipped version" overstates this |
| G5 | No control arm | VERIFIED (still open) | No arms, draws or per-draw archive; each regen overwrites the sandbox pass output |
| G6 | `slug.title()` voice-display brittleness | STALE | `f7e0d4c`: the pipeline is now invoked by slug (`:184`) |
| A5 | Hardcoded `phase-l-*` paths, two slugs, no `--project` | STALE | Fixed in `f7e0d4c`: `sandbox` subcommand, `--project` required, any slug, refuses git projects (`:115-120`) |
| §0.2-1 | Sandbox project; delete the flag; never point at athens-2026 | STALE (partly) | Sandbox creation and the athens-2026 guard now exist. **The flag is not deleted**, and neither the voices ONBOARDING recipe (`:436-458`) nor the script mentions it |
| §0.2-2..5 | `--from-pass/--through`, arms and draws, archive, runner `--stop-after`, comparison report, offline Gap-C render test | VERIFIED (not built) | None exist (grep for `stop_after`, `conditional_block` in personas: none). Still needed as specified |
| §0.3 | Thinking stays adaptive for Pass 2–6 | VERIFIED | `model_routing.json`: `personas.pass_2`…`pass_6`, `derive`, `ct_compress` all `adaptive` |
| §0.4 | Per-call costs (Pass 2 ≈ $0.53, range $0.5–0.9; Pass 3 ≈ $0.67; 4a $0.5–0.6; 4b ≈ $0.13; CT ≤ $0.3) | VERIFIED | Recomputed from athens-2026 usage at $5/$25: Plato P2 $0.52, Dostoevsky $0.84; P3 $0.66; 4b Whanganui $0.12; CT ≈ $0.05. Missing from the table: **Derive $0.32–0.44 per call** (`06_derive/00_derive_raw.json`) |
| §0.5 | Totals by item | PLAUSIBLE | The arithmetic holds. Item 3 looks ~30–40% high (my estimate ~$20–24). **Every regen-based item assumes `--stop-after`.** With today's harness, a Pass 2 draw costs $0.89–1.27 instead of $0.52–0.84 (Derive + CT), and multi-pass items (4, 3, 6) run through Pass 6 each time. Item 1 alone becomes ≈ $16. My rough total is ≈ $150 (inference, not run) |
| N8 | 7c anti-structure `banned_modes` already on 5 cards and didn't hold | VERIFIED (presence) | Battuta [11], Arendt [19]/[21], Lovelace [12], Dostoevsky [13], Cleopatra [14]–[16] as quoted. The wbbf26 timing is PLAUSIBLE, not checked |
| N9 | Whanganui `hard_limits[1]` keeps "they ARE me" | VERIFIED | The shipped card has it. It is also in the Pass 2 output `hard_limits[1]` (the §4 table shows "—") |
| §1-ev | `voice_temporal_stance` evidence: 5,958 chars, 507–733, all `anchored_override` null; 7/10 Pass 2 v1 frame; 8/10 populated override | VERIFIED | `cards.py`. Marley quote exact; Battuta calendar clause exact; no decline hook on any card |
| §1-tpl | "Nine share one template; Octopus and Whanganui carry the same parts in their own grammar" | WRONG (minor) | 9 + 2 = 11. Eight cards open "You have been called to the assembly…"; Octopus and Whanganui differ |
| §1-refs | Prompt/code refs (`:339-406`, `:355`, user `:56-59`, `card_assembly.py:240-282`, `chat_prompt_builder.py:185-192`, test `:233-239`) | VERIFIED | All read |
| §1-key | "Its test expects the key to exist. So the proposal keeps the key" | DOUBTFUL | The test builds its own card with the key; no code requires Pass 2 to emit it (grep `anchored_override`). Keeping it as null is a choice, and it departs from the roadmap's "drop `anchored_override` emission" |
| §1-diff | Diffs apply to the current text | VERIFIED (text) | Old side found at `:1`, `:339`, user `:56`; the runner render is now at L490 (was L485). The hunk counts are wrong (`-339,68 +74` is actually +75), so `git apply` rejects them |
| §1-var | `{{ assembly_place }}` needs a render var (StrictUndefined) | VERIFIED | `prompt_render.py:33`. The only render site is `run_persona_pipeline.py:490` (grep). `_assembly_place()` is a sketch, undefined |
| §1-checks | Mechanical checks, 2/2 draws × 4 sentinels incl. Whanganui | WRONG | I ran the checks on the shipped defaults (the target): 9/10 pass. **Whanganui fails 3**: no "respond from your own ground", "translation protocol" without the underscore, last sentence "I observe;". A treatment that reproduces the shipped Whanganui card would fail item 1. This also clashes with item 4's first-person "I have been called" line vs item 1's "MANDATORY; second person" |
| A6-spec | Field = name phrase completing "You are ___." | VERIFIED | `Persona_Card_v2.md:245-250`. Note `:241` itself says responses begin "I am Plato", which is part of the ambiguity |
| A6-tab | 10-voice `council_member_name` table, provenance, 140/167 words | VERIFIED | All values checked against the cards and Pass 2 outputs; Whanganui's is an operator patch (Pass 2 had "Te Awa Tupua — … I speak through…") |
| A6-why | Prompt `:238-239`, OUTPUT REGISTER `:31-36`, 7a `:43-46`, 7a-FINAL now validates the field | VERIFIED | Read; voices §32.2 (`a10e08a`) |
| A6-rule | "noun phrase, 3-25 words" + check "3–25 words" | WRONG | Contradicts its own examples: "the Octopus" (2 words, and Octopus is an A6 sentinel) and the "clean" "Hannah Arendt" (2 words). The check would fail the recommended output |
| A6-R1 | "Runtime C67 R1 … also benefits from a short name phrase" | STALE | R1 fixed in `02006f5`: Step 3 now uses `voice_display_name(slug)` (`card_assembly.py` filter_first_draft_for_step3) |
| §2-ev | "Voice of X" on all cards; configs bare; runner `:1851/:1859`; not in runtime field lists; chat strip `:129` | VERIFIED | Runner lines are now L1856/L1864 |
| §2-design | Keep `voice_config.name` bare; add a separate `voice_name` field | DOUBTFUL | Well argued (`{{ name }}` in expert lines, slug lookup), but it departs from the filed 2026-05-02 decision in voices §18, which lists `voice_config.name` as a "Voice of X" field. It needs an O-item, and none is listed |
| §2-schema | Add `voice_name` / `"composer"` / `artifact_direction` to `schemas/voice_config.py` | DOUBTFUL | `VoiceConfig` is **imported nowhere** (grep), and it has `extra="ignore"`. Validation is `node0_validation.validate_input`, which doesn't check `mediation_stance`. The schema edits are inert, so the real checks must go in `node0_validation` |
| §2-sent | Pass 0a sentinel on Octopus/Whanganui/Dostoevsky; pass = 6/6 exact match | DOUBTFUL | The new Pass 0a text quotes exactly those three answers as examples, so the test measures copying. Also, `run_pass0a_voice_config.py:280-284` overwrites the sandbox `02_voice_config.json` (dropping Whanganui's hand-set `mediation_stance` and `editorial_rationale`), and the sandbox lacks the original Pass 0a inputs. Use a separate sandbox |
| §4-ev | Whanganui Pass 2 vs shipped table; witness block `:490-538` covers only `hard_limits`; Gap G on 3 card fields | VERIFIED | All six rows checked; `hard_limits[8]`, `characteristic_moves[0]`, `quality_criteria[5]` exact; "tupua and tupuna" gloss is in `preferred_vocabulary` |
| §4-3/5/6 | Pass 3, 5, 6 witness blocks already list every emitted field | VERIFIED | Pass 3 `:176-209` covers all 5 fields; Pass 5 block names all 4; Pass 6 names header/why_selected/text/citation |
| §4-diff | Diffs for Pass 2 / 4a / 4b | VERIFIED (text) | Old side found at the stated lines. 4b `@@ -196,3 +199,7` is a context-only hunk (no change). 4b `@226` appends the per-field rules **inside the "Twin-failure-modes to ban" list**, where they read as banned modes: move them above that list |
| §3-ev | Plato `389a08c` fields; 5/7 patches are Pass 6 headers; Scheherazade third-person "the voice" | VERIFIED | `characteristic_moves[9]`, `metaphorical_repertoire["midwifery and birth"]`, headers [2][3][4][6][7], `cm[0]` exact; voices §9 lists the 7 patches. Scheherazade `bl[0,8,9,11,15]` and `bm[1,4,8,13,14]` contain "the/The voice" |
| §3-gap | No composer clause in Pass 2/3/4a/6; Pass 6 `:79-85` invites the collision; `mediation_stance` rendered at L489/515/673/708/737/775 | VERIFIED | grep: none. HANDOFF §13 "NOT universal" quote exact |
| §3-diff | Composer blocks after the witness `{% endif %}` | VERIFIED (text) | Anchors at Pass 2 `:538`, Pass 3 `:219`, 4a `:163`, Pass 6 `:161` are the witness-block ends. The Pass 0a hunk's context line is abbreviated ("(enum: …): …") and matches nothing |
| §3-cost | $32 for 2 voices × 4 draws, Pass 2→6 | PLAUSIBLE | Per draw ≈ $2.5–3 from recorded usage (P5 ≈ $0.13, P6 ≈ $0.32) → ~$20–24 |
| §6-ev | `editorial_rationale` non-null for 3/10; `manual_grounding` lengths; Plato's Wikipedia lead | VERIFIED | 5,485/3,892/354 and 7,555/6,344/1,593; others 148–750 |
| §6-diff | 4b `:87-93` fix; 4a/4b user additions; `{% if %}` on None is safe if the value is passed | VERIFIED | Old side at 4b `:87`, 4b_user `:9`, 4a_user `:61`. `standalone_pass4b_test.py` also renders 4b but is already broken (it passes no `corpus_constraint`/`mediation_stance`) |
| §5-ev | Memo patches never applied; reader quotes; placement per `ONBOARDING.md:72`; `topics_requiring_care` in Step 1/2 | VERIFIED | `MEMO_2026_05_07…:7`; quotes at `:90`, `:99`; `card_assembly.py:93` |
| §5-diff | Append after `:458` | WRONG (minor) | The context line is truncated: "This clause makes the failure mode explicit.)" vs the actual `:458` "way he never did. This clause…". Intent is clear; it doesn't apply |
| §5-0.2 | Refusal detection has no OPEN_ITEMS home | VERIFIED | Only roadmap `:51` |
| §7-ev | Tailor prompt `:76,78,86-87,96,98,108,110,114`; path-3 reshaping | VERIFIED | All lines read; diff old side found at `:72`, `:108` (hunk counts off) |
| §7-harness | Call `run_pass_0b_tailor(name, project_root=…)` directly | VERIFIED | Signature `run_pass_0b_tailor.py:162` |
| Cov | Stayed read-only; no model calls; scratch scripts declared | PLAUSIBLE | Consistent with the doc; nothing in the repo or athens-2026 suggests otherwise |

**Diff applicability overall (checked by running):** 0 of 15 blocks pass `git apply --check` or `patch --dry-run -F3`. 29 of 31 hunks' old-side text is found verbatim in the current files; the 2 misses are the abbreviated/truncated context lines above. The prompt line numbers are exact at HEAD. The runner line numbers are now +5.

**What `f7e0d4c` fixed of §0 and what it didn't:**
- **Fixed:** A5 (archived paths, two-slug limit, no `--project`, stale docstring); the athens-2026 overwrite risk (git-repo refusal); G6.
- **Half-fixed:** sandbox creation (it still copies the review flag, so Derive fires); G4 (`--baseline-project` compares production *pass outputs*, not cards).
- **Not fixed:** G1, G2, G3, G5, `--stop-after`, `--from-pass/--through`, arms, draws and archiving, the comparison report, the Gap-C render test.
- **New gap the doc couldn't see:** the repaired defaults are `plato,fyodor_dostoevsky` (`:64`). A bare `regen` touches the two voices ONBOARDING `:65-66` restricts.

## Problems with the document

- **Spend vs decision.** O1 ($150) is superseded by the USD 10 cap. The per-item estimates exclude the Derive call that every `sentinel_regen.py regen` makes today (flag copied into the sandbox), and the full-pipeline re-run for multi-pass items. The plan needs re-scoping: fewer voices, one treatment draw, athens pass outputs as the control, and the harness work (§0.2 steps 2–3) done first. Otherwise the cap buys roughly 8–10 Pass 2 draws in total.
- **Internal contradictions.** A6's 3-word floor vs its own examples. Item 1's second-person checks vs the Whanganui sentinel and item 4's first-person line. "Nine share one template".
- **Diffs are illustrative, not patches.** Hunk counts are wrong throughout; there is one no-op hunk, two truncated contexts, and one misplaced insertion (4b ban list). The doc doesn't say they are hand-written.
- **Code proposals target a dead schema.** `schemas/voice_config.py` isn't used by any code, and the doc didn't notice.
- **Scope drift without an O-item:** item 2 overrides voices §18's `voice_config.name` decision. Items 3 and 6 widen the roadmap's scope (Pass 6 and Pass 0a added; a new `artifact_direction` field instead of piping as filed). These last two are flagged as O3/O4, which is correct.
- **Sentinel design:** item 2's examples leak the answers, and its Pass 0a run clobbers the shared sandbox configs.
- **Stale since writing:** C67 R1 (`02006f5`), N7/G6/A5 (`f7e0d4c`).
- **Rules:** no breach found. It wrote one file, labelled claims, declared its scratch scripts, and says no git ran in athens-2026. The brief's "summary on top" is met.

## Questions for the originating session

1. **Which items in §0.5 assume `--stop-after`, and what is each item's minimum evidence design (voices × draws) you'd still accept?** Why it matters: the USD 10 cap and today's harness (Derive on every draw). If most items can drop to 1 draw × 2 voices with athens outputs as the control, Stage 4 fits the cap in stages. If not, the operator must choose between raising the cap and building §0.2 first.
2. **For Whanganui in item 1, should the pass criteria be witness-variant (first-person "I have been called … I observe;") rather than the second-person checks?** Why it matters: as written, a treatment matching the shipped card fails. The answer decides whether item 1 needs witness-specific text and checks, or whether Whanganui leaves item 1's sentinel set until item 4.
3. **In A6, was the lower bound meant to be 1–2 words ("the Octopus", "Hannah Arendt")?** Why it matters: this changes the prompt rule and the mechanical check. Otherwise the recommended Octopus output fails.
4. **Was the departure from voices §18 (`voice_config.name` stays bare) deliberate, and should it be an operator decision?** And did you intend item 2's Pass 0a sentinel to run in its own sandbox, with the original hint and grounding? Why it matters: it overrides a filed decision, and Pass 0a overwrites the sandbox configs that items 4 and 6 depend on.
5. **Can you regenerate the diffs as real `git diff` output from an edited scratch copy of `main`?** Include moving 4b's per-field lines out of the ban list. Why it matters: the implementer currently has to hand-apply 15 blocks. With real diffs, each Stage 4 step becomes a mechanical apply plus a sentinel run.

## Operator decisions it asks for

| # | Decision | Doc's recommendation | Note |
|---|---|---|---|
| O1 | Spend cap and sandbox location | $150; `projects/current-tests/stage4-sentinels/` | **Decided otherwise:** USD 10 (2026-09-28) |
| O2 | Plato as sentinel (items 3, 5) | Allow, in a sandbox copy only | `ONBOARDING.md:65`; the repaired script's default sentinels also include Plato |
| O3 | Item 3 trigger | New `mediation_stance: "composer"` for Plato and Scheherazade | The schema edit is inert (`VoiceConfig` unused) |
| O4 | Item 6 shape | New `artifact_direction` field; Marley config reconciled to v2 first | The Marley reconciliation is an athens-2026 data edit |
| O5 | Item 5 placement | `topics_requiring_care` entry; land after the refusal-detection fix | — |
| O6 | Whanganui `epistemic_frame_statement` opening | Align with the witness stance | — |
| O7 | Patch shipped cards now (4 "I am" names, N9, N5) or at rebuild | No recommendation (options given) | Any patch changes voice input and needs re-validation |
| O8 | `assembly_place` from `conference_facts.json` now vs `event_config` | Implied: now (one line) | Stage 5 split-card/event config (C52) may supersede it |
| O9 | Item 7 rule strength | Perplexity-grounded names only; escalate to "no names" if it leaks | — |
