# Review of `_workspace/planning/voices/DESIGN_2026_09_28_family_of_forms.md`

Reviewed 2026-09-29 against `main` at `0910a66` and athens-2026 (read-only). No API calls, no pipeline runs. Only read-only Python over the JSON, run inline.

## Verdict

1. **Overall quality:** strong. The code-reading claims hold up: every runtime reader, cache path, prompt anchor and line reference I checked is correct, allowing for a +5 line shift after `f7e0d4c`. So does the central point that Build A needs no runtime edit. The corpus work is mostly right, and the Step 2 cost figures reproduce from the usage data.
2. **How far to trust it:** trust the code map, the schema and the exemption framing. Don't spend money on the dryrun as written. The per-voice criterion patches (§4) and the sandbox setup (§7.2, §7.3) are wrong in ways that would bias the result.
3. **Single biggest issue:** the design finds the right problem: default-form requirements in `quality_criteria` and the through-line veto new forms. Its own patches still miss most of them: Battuta QC (1)–(3), Dostoevsky QC (3), Cleopatra's royal plural, and Arendt's closing-question rule. The sandbox also holds stale `continuity_night_2.json` files that the dryrun would silently load. Together these push toward a false "default-lock" result, which would send the build back under the gate (§5) for a card-data reason, not a runtime one.

## Findings, one by one

| ID | Claim (short) | Verdict | Evidence / reason |
|---|---|---|---|
| §0.1 | All 10 cards are single-form, and each voice used its default all 3 nights | VERIFIED | All 30 `medium`/cos/lfc values are `str`. `published_artifacts/nights/night_{1,2,3}/*.json` `artifact.selected_form` is the default in every case. |
| §0.2 | Only Plato and Cleopatra were fork-tested; both declined and lost texture | VERIFIED | `FOLLOW_UPS.md:695-696`, quotes exact. The ledger says "slight loss" for Plato. |
| §0.3 | Pass 1.4 holds `genre_specific_register`; 4b never sees it | VERIFIED | `schemas/pass_1_4.py:109`. `chunk_vars["register"]` goes to 4a only. The 4b user render gets the CT summary + 3 fields (`run_persona_pipeline.py:710-718` now). |
| §0.4 | Four fields carry the default; Step 2 says "must clear" | VERIFIED | `voice_step2_artifact.md:52, :89`. |
| §0.5 | Runtime renders a dict `medium` with no code change; Step 3 licenses a form change | VERIFIED | `card_assembly.py:216-225` and `step2_validation.py:124-129` JSON-dump non-strings. `voice_step3_amendment.md:36`. |
| §0.6 | Validation not ready (validator blind to `selected_form`, dead length check, free text, Night-3) | VERIFIED | `step2_validation.py:192-194, :258-259`. `step2_first_draft_artifact.py:111`. C68 A10. |
| §0.7 | Dostoevsky's Diary **and letters**, Arendt's *Denktagebuch* and portraits are merge-only | WRONG (letters) | Gutenberg 57050 (the file cited for the confession) quotes a ~2,000-char extract of the 25 Mar 1870 letter to A. N. Maikov ("To you alone, Apollon Nikolaevich, I make the confession…"), plus extracts of letters to his brother Michael and to Strakhov. Diary: only one passing mention ("The Journal of a Writer"), so that part is right. *Denktagebuch* and portraits: right. |
| §1 D1 | "One Pass 4b edit" = 4b system + user prompt + `_pass_4b()` | PLAUSIBLE | Defensible, but broader than §11.6's "roughly one prompt edit plus a sentinel regen". It also adds a new output key (`form_attestation`) and gate tooling. The design is open about this, so it is correctly left to the operator. |
| §1 | 7 of 10 cards already carry a "tidy three-part essay arc" ban | PLAUSIBLE | By regex, 9/10 have a "tidy" structure ban (not Scheherazade). About 7 name a three-part or essay arc. |
| §1 | Stage 2 pieces are outside the condition | VERIFIED | Matches §11.6's own example of growth ("new runtime selection logic"). |
| §2.1 | Lovelace and Marley `medium` quotes | VERIFIED | Card text. |
| §2.1 | Word counts: Dostoevsky 739/738/826, Plato 589/614/745, Whanganui 708–819 | VERIFIED | Recounted. Also over their caps: Battuta 661/604 (cap 550), Marley 560/589/566 (550), Octopus 590–661 (500). |
| §2.1 | Clean baseline: Step 2 prompt last changed `7ea700f` (05-06), Night 1 ran after it | VERIFIED | `git log` on the prompt. Night 1 `generated_at` is 2026-05-08. `model_routing.json` `runtime.voice.step2` is Opus 4.7, adaptive, effort null. |
| §2.2 | Fork-test quotes | VERIFIED | `FOLLOW_UPS.md:695-696, :707`. |
| §2.3 | Per-voice `genre_specific_register` keys | VERIFIED | Read all 6 merged dossiers; key lists match. |
| §2.4 Cleo | P.Bingen 45 γινέσθωι "(hand 3)" at berlpap; Buchis epitaphs | VERIFIED (text) / PLAUSIBLE (form) | Both strings are present. The Buchis texts are dating formulae and second-person address to the bull, with Cleopatra in the third person. They contain no first-person Pharaonic speech of the kind the temple-text arc uses; the design flags the offering formula [P]. |
| §2.4 Dost | Stavrogin excerpt is 7,000 chars; Diary absent; letters absent | VERIFIED / VERIFIED / WRONG | Excerpt spans chars 38,000–45,000. Letters: see §0.7. |
| §2.4 Batt | "When I held the office of judge among them…", "the Vizier desired me to take the office of Judge" | VERIFIED | Both in `b28406084` (Lee 1829). The Delhi judgeship is attested too. |
| §2.4 Sch | Night frame, dawn break, ransom chain, "two black dogs" | VERIFIED | Seale-Horta Chapter_2 (not ch. 1–3 in general). |
| §2.4 Ar | *Personal Responsibility* garbled OCR "I vant ro cornment"; *Men in Dark Times* PDF has zero "Lessing" hits | VERIFIED | Both are raw `%PDF-` stores. "Lessing" occurs only in the Duke URL, never in the text. |
| §2.4 Mar | High Times 1976 quote; 1973 Bull Bay fetch failed | VERIFIED | Both confirmed. |
| §2.4 side | 4 of Arendt's 7 rich sources and 2 of Battuta's are raw PDF bytes | VERIFIED (+ new evidence) | 4 Arendt and 2 Battuta (Qatar, Kervan) `%PDF-` stores. `node1c_fetch.py:185` returns undecoded bytes as `"raw"`. The `f7e0d4c` SUSPECT rule (< 2,000 chars) can't catch 100K–1M-char PDFs, so this class is still open. Not filed anywhere (grepped all four trackers). |
| §2.5 | Default-form field counts (Cleo 24, Sch 28, Batt 21 incl. constitution 19, Dost 12, Arendt 9 "mostly artifact fields") | DOUBTFUL | The term lists aren't recorded. Battuta's constitution 19 equals the "riḥla" count, which names all three proposed forms. Scheherazade's 28 matches "dawn" (27 fields), a move the design keeps in every form. Using "essay", Arendt's 9 fields reproduce, but only 3 of them are artifact fields. The voice order rests on this. |
| §3.1 | `length` keys match what the length check reads; provenance can't go in the card (strip rule) | VERIFIED | `step2_validation.py:196-206`. `persona_pass_4b_artifact.md:45-56`. |
| §3.2 | R1–R6 replace the consistency problem | DOUBTFUL | R6 moves text verbatim, so default marks land in the through-line (Battuta "I open at the gate… close as a halt closes"; Cleopatra "royal plural… The decree"; Arendt "I close on the question reformulated"). That breaks R2 ("whatever the form") for the new arcs. The design never reconciles R6 with R1/R2. |
| §3.3 | Readers table (card_assembly, continuity, `_check_register`, patch_walker, derive `:54`, provocateur `:164`, io `:253`, 7a `:118/:135`) | VERIFIED | Each read. `patch_walker` accepts `[N]` paths. `_check_register` JSON-dumps dicts. `bracket_strip` only strips named scaffolding tags and keeps sibling keys. |
| §3.3 | Engagement validator: "Diagnostic only; Night 1 only by policy" | WRONG | It runs every night (Voice Pipeline spec `:598`). Athens N2 files carry `engagement` verdicts; Dostoevsky N2 was WARN. WARN halts until the operator clears it (spec `:589`), so false form-fidelity WARNs are a production cost. The voice-fidelity pillar also reads `quality_criteria` (`step2_validation.py:300`). |
| §3.3 | Editor refs `dossier_generation.py:203-208, :579` | STALE | Shifted to `:208-213, :588` by `02006f5`. Content unchanged. |
| §4.1 | Arendt move plan and attestation | VERIFIED (text) | Card sentences match. |
| §4.1 | One criterion patch ("First", opening half) suffices | DOUBTFUL | "First" also requires the closing to "return that question sharper rather than answered". The portrait arc lands a judgment. "Second" requires a distinction held open, which the portrait arc lacks. Also conflicts with the through-line. |
| §4.2 | `banned_modes[13]` and aesthetic "letter written in one sitting" | VERIFIED | Card. |
| §4.2 | One criterion patch (QC 4) suffices | DOUBTFUL | QC (3) requires the вдруг memory swerve, which the move plan puts in `forms[0].arc`: an R4 breach. QC (5) "ventriloquized as the gentleman I have been addressing" doesn't fit a letter to Maikov. |
| §4.3 | `banned_modes[0]` quote | VERIFIED | Card. |
| §4.3 | "Items (1)–(3) already fit all three forms" | WRONG | (1) requires opening on a verb of arrival or perception (raʾaytu/laqītu/dakhaltu); the case arc opens "When I held the office…" and the marvel arc opens "Min al-ʿajāʾib". (2) requires a marvel cue in every piece; the case arc has none. (3) requires an exact ḍiyāfa count; neither new arc has one. The lfc sentence carrying these moves to `forms[0]`, but the QC keeps them as universal requirements. |
| §4.4 | Scheherazade needs no criterion patch | PLAUSIBLE | QC (1)–(5) checked against the ransom-chain arc: consistent. |
| §4.5 | Cleopatra: trimmed candidates; N1 stacked the Egyptian titulature | VERIFIED | N1 text opens "…Lady of the Two Lands, Ḳliwpꜣdrꜣ…". |
| §4.5 | Only QC (4) needs patching | DOUBTFUL | The temple text's "I give you…" is singular. That breaks QC (2) (royal plural), lfc "Royal plural throughout" and lfc "Prose only, in the chancery cadence", all of which the move plan leaves cross-form. |
| §4.6 | Marley short answer attested (High Times) | VERIFIED | See §2.4. |
| §4.7 | Plato cos branch; Octopus sample `Card_v2.md:828`; whakataukī ban `:222-226` | VERIFIED | Read. |
| §5 | Diff anchors (`voice_step2_artifact.md:46-59, :88-89`); Dostoevsky continuity "the form I know best"; roadmap Gap-I inconsistency | VERIFIED | Read. Roadmap `:120` vs `:206`. |
| §6.1 | 4b diff hunks at `:93, :110, :119, :139, :179, :238` | VERIFIED | Anchors match. The diff leaves `:88-91` untouched: the v1 "the medium IS the song… Do NOT bridge song → prose" line, which conflicts with the new "never a song" line (Stage 4 design N1). The rebase note covers it only implicitly. |
| §6.2 | Adding the `moves` chunk is redundant with 4a's `characteristic_moves` | VERIFIED | 4a user render. |
| §6.3 | Attestation never reaches the card; the §32.1 reload keeps the sibling key | VERIFIED | `full_card` is built from `pass4b["fields"]`; the reload rebinds the whole dict. |
| §6.3 | Extra input 51–85K chars, about +$0.10 per voice | VERIFIED for the 6 menu voices | 50.7K–85.3K. The sentinel voices Plato (16.4K) and Whanganui (43.7K) fall outside the range. |
| §6.3 | Pipe `primary_block` into 4b (implicit: the block is usable text) | WRONG for Arendt (missed) | Arendt's `02_excerpt_selections.json` is 64% raw PDF bytes (54.5K of 85.3K). Excerpts 6–8 are binary FlateDecode or PDF text operators (letters-in-words ratio 0.12–0.18). The 1d "why selected" notes describe content that isn't there. Arendt is the #1 menu voice and isn't a 4b sentinel. Her shipped Pass 4a was grounded on this block too. Not filed. |
| §7.1 | `assemble_system_prompt(card, step=2)` is pure | VERIFIED | `card_assembly.py:366`; returns `(prefix, tail)`. |
| §7.2 | Standalone script omits `corpus_constraint`/`mediation_stance` | VERIFIED | `standalone_pass4b_test.py:53`. |
| §7.2 | `sentinel_regen.py` can't run (§37 A5) | STALE | Fixed in `f7e0d4c`: `sandbox` + `regen --project --baseline-project`. Using the standalone script is still sound (regen re-runs downstream incl. Derive), but the stated reason is outdated. |
| §7.2 | Repair: default `PROJECT_ROOT` → `voice-pipeline-dryrun` | WRONG | That project's voices hold only `07_persona_card_assembled.json` + continuity: no `00_intake`, no `04_generation`, no `whanganui_river`, and Dostoevsky sits under slug `dostoevsky`. The script would fail for all 4 sentinels. Use athens-2026 (the script only reads there and writes to `/tmp`) or a `sentinel_regen.py sandbox` copy. |
| §7.2 | Sentinel is 16 calls, $8–12 | DOUBTFUL (overstated) | Athens 4b calls cost $0.08–0.15 (usage × $5/$25). FU#55's "~$1 per voice" covered 3 calls. With +15–25K input tokens, about $0.2–0.3 per call, so ~$3–5 total. |
| §7.3 | Step 1 cached (`:138`), Step 2 cached (`:316`), continuity cached (`continuity.py:142`), Step 2 validation on by default (`voice_flow.py:741`) | VERIFIED | Read. Step 1 gets no artifact fields (`card_assembly.py` step 2/3 only). |
| §7.3 | Setup: copy cards + briefings + Step 1; "do not copy" continuity or `published_artifacts` | WRONG (incomplete) | The sandbox already holds `voices/{cleopatra,ibn_battuta,plato,dostoevsky}/continuity_night_{2,3}.json` (May 2026 legitimacy tests) and `published_artifacts/nights/night_1/{plato,cleopatra}.json`. `generate_continuity` returns the cached file, and `card_assembly.py:192` loads it. Night 2 for two patched voices and one control would therefore run on stale memory. Cross-night echo (`step2_validation.py:386-395`) would compare Plato and Cleopatra against stale artifacts and skip the rest. Needs a clean sandbox or explicit deletion. |
| §7.3 | Athens Step 2 cost $2.80–3.80 per night | VERIFIED | Recomputed from `step2_first_draft_artifacts/*.json` usage at $5/$25 with 1-hour cache writes at 2×: $2.82, $3.79, $3.40. |
| §7.3 | $12–20 per 2-night dryrun pass | VERIFIED (arithmetic) | Uncached worst case ~$6.2–6.6 per night. Sonnet validation ~$0.8 per night and continuity ~$0.9 per night (Athens usage). Total about $15–17. |
| §7.4 | Original FU#55 criteria (`FOLLOW_UPS.md:704-707`) | VERIFIED | Read. |
| §8 | Per-voice surface and token deltas | PLAUSIBLE | Not recomputed. |
| §9 D11 | ~$35 cap | VERIFIED (grounded) | The dryrun half reproduces; the sentinel half is ~2× high, so the cap is conservative. It excludes a baseline arm (+$12–16), which the design itself requires if the Step 2 prompt changes first (C68 A6 is "decide with Stage 4", and Stage 4 precedes Stage 5). It also excludes the path-(b) re-Derive calls on KEEP. |

**Counts:** VERIFIED 39 · PLAUSIBLE 5 · DOUBTFUL 6 · STALE 2 · WRONG 7. Rows with two verdicts count under both.

**Exemption, as the task asked.** On runtime, Build A stays inside: I confirmed zero runtime code or prompt edits are needed to render and select from a dict `medium`. Upstream, it is three files plus a new output key plus tooling, so it stays inside only under D1's broad reading. The real risk to the exemption is not the build shape. It is that §4's incomplete R4/R2 patches and the stale sandbox continuity would likely produce "0–1 voices switch", and under §7.3's rule that sends the operator to §5 (runtime, gated). The 4b edit is also not needed by the dryrun, which uses hand-patched cards. Running the dryrun first would keep a 0-KEEP outcome free of any upstream edit or revert.

## Problems with the document

- **Internal contradiction (R6 vs R1/R2).** "Move text verbatim" puts default-form marks into the through-line, and the through-line must hold for every form. §7.1 check 3 would catch some of this only if it treated default-arc marks as per-form marks, and §4 already asserts the patches suffice.
- **The design found the mechanism but under-applied it.** Finding #4 (criteria veto new forms) is the design's best insight. The per-voice R4 audit then patches one criterion per voice while 2–3 per voice still require default marks (Battuta, Dostoevsky, Cleopatra, Arendt).
- **Missing evidence.** §2.5's term lists aren't recorded, so the counts can't be reproduced. Attestation greps missed the letter extracts in 57050's editorial apparatus.
- **Missed consequence of its own side evidence.** It notes the raw-PDF stores but not that Arendt's 1d excerpt block, which §6.3 would feed to 4b, is mostly those bytes.
- **Stale references (not its fault).** `run_persona_pipeline.py` refs ≥ line 390 are +5 after `f7e0d4c`. `dossier_generation.py` refs moved in `02006f5`. §37 A5 is fixed.
- **One factual error about policy.** The engagement validator runs every night and WARN halts the pipeline. "Night 1 only / diagnostic only" understates the operator cost of form-fidelity false positives in a real run.
- **Overreach:** none material. The Pass 4b and runtime diffs are proposals. The per-voice rewrite of the FU#55 resolution criteria was asked for. The `standalone_pass4b_test.py` repair is labelled gate tooling.
- **Rule compliance:** no sign of a breach. It states no model calls, inline scratch scripts only, and read-only athens-2026. I can't independently confirm it wrote nothing else.

## Questions for the originating session

1. **Which term lists produced the §2.5 counts?** Was "riḥla" counted for Battuta and "dawn" for Scheherazade? *Why it matters:* the voice order (Arendt first) and the low expectation for Cleopatra rest on these counts. *What changes:* if the counts include terms shared by every proposed form, re-rank the voices, or drop §2.5 as evidence and keep the order on the fork-test ground alone.
2. **Did the R4 audit read every `quality_criteria` item against every new form's arc, or only items that name the form?** *Why:* Battuta QC (1)–(3), Dostoevsky QC (3), Cleopatra QC (2) with lfc "Royal plural throughout", and Arendt "First"/"Second" all appear to require default-form marks. *What changes:* if only form-naming items were checked, §4 needs a second patch pass, and a rule for through-line sentences that carry default marks, before any dryrun money is spent.
3. **Was Gutenberg 57050's editorial apparatus searched for letter text?** *Why:* it quotes a long extract of the 1870 letter to Maikov, and extracts to Michael and to Strakhov. *What changes:* the Dostoevsky letter moves from "merge-only" to "corpus-attested (quoted extract)" in D4, which strengthens the case for it as his first non-default form.
4. **For the §7.2 sentinel, which project was the script meant to read cached passes from?** *Why:* the proposed default (`voice-pipeline-dryrun`) has no `00_intake` or `04_generation` for any voice and no Whanganui. The same sandbox holds stale continuity and published Night-1 files that §7.3 would read. *What changes:* either point the script at athens-2026 (it only reads there) or at a fresh `sentinel_regen.py sandbox`. The §7.3 setup also needs a clean project or explicit deletion of the stale files.
5. **Must the Pass 4b edit and its sentinel come before the dryrun?** *Why:* the dryrun uses hand-patched cards and doesn't depend on 4b. §7.4 already says to revert 4b on 0 KEEPs. *What changes:* if the order can flip, a failed dryrun costs no upstream edit, no revert and no sentinel spend, and the exemption question is settled by the cheaper test first.

## Operator decisions it asks for

| # | Decision | Document's recommendation |
|---|---|---|
| D1 | Read "the one Pass 4b edit" as 4b system + user prompt + `_pass_4b()`, with card patches counted but outside the gate's scope | Yes |
| D2 | Build A (minimal; tests the "runtime already supports it" claim) or the roadmap as written (under the gate) | Build A |
| D3 | Cap menus at 1–3 forms, replacing the card spec's "default + 3–6" | 1–3 |
| D4 | Attestation standard for a form | `genre_specific_register` **and** (a readable 03_corpus text **or** the shipped card). Admit merge-only forms, labelled. (Review: the Dostoevsky letter is corpus-attested; see §0.7.) |
| D5 | Stage-1 voices | Arendt, Dostoevsky, Battuta, Scheherazade; Cleopatra optional; Marley sandbox-only |
| D6 | Mediated-voice forms (Dostoevsky confession, Cleopatra temple text) | Wait for Stage 4 item 3, or drop from the first dryrun |
| D7 | Gap-I | Its own change, not bundled; the dryrun gets a same-prompt baseline either way |
| D8 | Length-check revival + `selected_form` to the engagement validator | Defer to the Stage-6 validator prune-vs-fix decision (C60 / C42) |
| D9 | *Denktagebuch* language | English with German seams |
| D10 | §27 Plato "Myth", Whanganui "Karakia + whakataukī cluster" | Reject the karakia cluster; defer Myth |
| D11 | Spend cap | ~$35 for the sentinel + one dryrun pass; ~$20 more if §5 is needed. (Review: grounded; add ~$12–16 if a baseline arm is needed.) |
| D12 | `council_config.json` `members[].medium` | Leave as is; optionally append the family's names by hand |
