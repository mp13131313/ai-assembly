# Review of `_workspace/planning/runtime/REVIEW_2026_09_28_prompts_model_era.md`

Reviewed 2026-09-29 against `main` at `43f2d0c`. Its code matches `f7e0d4c`; the only later commits change docs. All 1,757 lines were read, including patches F1–F11.

## Verdict

- **Overall quality: high.** Every number I re-derived matched exactly: 7/89, 17/193, 2,985,437 written / 0 read, 544,451 / 19,609, 51/53 and the 17 pinned tests. All 11 patches still apply to current `main` after C67 and §37, and both suites pass with them applied. The API claims match the `claude-api` skill.
- **How far to trust it:** trust the evidence and the patch mechanics. Treat the F4 recommendation (operator decision 1) and a few details as open (see Problems).
- **Biggest issue:** F4's code-derived verdict is the right mechanism, but the rule it recommends is not safe as it stands. Enforcing "any `performed: false` → WARN" on the Athens record changes the overall gate from 7 PASS / 21 WARN / 2 HOLD to 1 PASS / 27 WARN / 2 HOLD, and voice-fidelity WARNs rise from 20 to 27 of 30. The document mentions only "7 more WARNs". It also doesn't engage with the sibling deliverable `REVIEW_2026_09_28_validator_evidence.md` §4.3: that review finds the cards carry 8–13 moves against a schema of 3–5, so a WARN on moves is close to structural.

## Findings, one by one

How I checked (all offline, in the scratchpad `rr/work/`):
- `replay.py` re-applies each prompt's stated verdict rule to the stored athens-2026 `04_voice/step2_validation/*.json`.
- `git archive` copies of `4e61444` and `HEAD`, with `git apply --check`, `git apply -v` and `patch -p1` for each patch alone and in series.
- The runtime and personas suites, run on a pristine and a fully patched copy of `main`, with no `.env`, API keys unset and an empty project root.
- The skill's `shared/model-migration.md`, `prompt-caching.md` and `tool-use-concepts.md`, plus the installed SDK 0.94.1 types.

| ID | claim (short) | verdict | evidence / reason |
|---|---|---|---|
| §2 | Scope: 75 prompt files (56 personas + 19 runtime) | VERIFIED | `ls` counts 56 and 19. No prompt file changed between `4e61444` and `HEAD`. |
| §3 | Routing per step: Derive and 7a-FIX on Opus 4.7 adaptive; 7-pre, 7c fallback and CT on Sonnet 4.6 | VERIFIED | Read from `model_routing.json` `steps`. |
| §3 | Assistant-role messages go only to `count_tokens`, and Opus 4.7 accepts them (51 of 53 `thinking_tokens` nonzero, N1) | VERIFIED | grep finds them only at `_anthropic_call.py:55` and `clients.py:43`. Walking N1 `04_voice/**/*.json` gives 53 values, 51 nonzero. |
| §1/§6 | The loader already enforces effort, temperature and thinking-off on Opus 5.5 (`model_routing.py:144-156`) | VERIFIED (line refs shifted) | The rules are now at `:154-162`; C67 inserted the `manual` guard at `:143-147`. Nit: the loader supplies the `sampling_params` flag, but the temperature drop happens in `call_claude` (`clients.py:158`). |
| F1 | Thinking-off is sent by omitting the field at every call site, and tests pin that | VERIFIED | Omitted at all 8 sites: `{...} if cfg.thinking_on else {}` in `_anthropic_call.py:110-113`, `step2_validation.py:89-92`, `synthesis_router.py:132-135`, `provocateur_flow.py:401-404`, `transcription_flow.py:564-567` and `:624-627`, and `researcher_flow.py:125-127`; `clients.py` uses `if thinking:`. Pinned: 17 asserts in `test_model_routing_call_sites.py`, plus `test_call_claude_config.py:64,85`. Unchanged by C67. |
| F1 | On Sonnet 5 (and Opus 5), omitting `thinking` runs adaptive thinking | VERIFIED (skill) | `model-migration.md` → Sonnet 5 → "Silent default change: adaptive thinking on when `thinking` is omitted", its checklist "[TUNE] Thinking-field omitted", and the thinking table row "Sonnet 5 … Omitting → Runs adaptive". Opus 5 → "Breaking change 1". The loader lets Sonnet 5 run with `off`, since `thinking_can_disable: true` in `model_routing.json`. |
| F1 | Speaker ID would crash on `resp.content[0].text` | VERIFIED (line moved) | Now at `transcription_flow.py:587` (C67 moved it). The SDK `ThinkingBlock` has only `signature`, `thinking` and `type`, so reading `.text` raises `AttributeError`. |
| F1 | `docs/LLM_CALL_INVENTORY.md` §10.2 says the opposite | VERIFIED | Still at `:405` ("no break there"). The C62 update in `runtime/OPEN_ITEMS.md` repeats the premise: "speaker_id + cleaning … can move to Sonnet 5". |
| F1 | Explicit `disabled` is a no-op today on Sonnet 4.6 and Opus 4.7 | PLAUSIBLE | Labelled PLAUSIBLE in the document too. The skill table says `disabled` is accepted on 4.7/4.8; the Sonnet 4.6 row is silent. |
| F2 | No call site checks `stop_reason == "refusal"` | VERIFIED | grep: `stop_reason` is read only at `provocateur_flow.py:420-447` (logging and error text) and `clients.py:243-292` (max_tokens handling). |
| F2 | Voice steps accept empty or partial text… | VERIFIED | `_anthropic_call.py:160-178`: a refusal raises nothing, so `""` or partial text comes back. `step2_first_draft_artifact.py:351` parses it leniently. |
| F2 | …"and retry once on the way" | WRONG | The retry fires only on an exception inside the `try`. A refusal raises none; `_estimate_thinking_tokens` returns 0 on empty text. So no retry happens today. The retry concern applies only once F2's own `raise_if_refused` sits inside that `try`, which is why F2 adds `except RefusalError: raise`. |
| F2 | Provocateur blames "adaptive thinking consumed…"; personas report "invalid JSON"; the router picks the lowest-numbered theme | VERIFIED (one word overstated) | `provocateur_flow.py:432-438`; note its message does print `stop_reason=refusal`. `clients.py:297` raises "invalid JSON". The router is not "silent": it logs a warning, but mislabels the cause as "model returned unknown theme_id" (`synthesis_router.py:168-174`). |
| F2 | API semantics: HTTP 200 with empty or partial content; Opus 5.5 adds `bio` and `reasoning_extraction`; `reasoning_extraction` isn't retried on a fallback; `fallbacks: "default"` needs `server-side-fallback-2026-07-01` on `client.beta` | VERIFIED (skill) | `model-migration.md:1367` (refusal section), `:2012-2014` and `:2055` (Opus 5.5 safeguards and checklist). Sonnet 5 "cybersecurity safeguards" and Opus 4.7 "Real-time cybersecurity safeguards" sections both exist. |
| F2 | SDK 0.94.1 types `category` as `cyber` \| `bio` only | VERIFIED | `anthropic/types/refusal_stop_details.py:14`. `Message.stop_details` exists (`message.py:78`), and `StopReason` includes `"refusal"`. |
| F3 | Developer headers in raw-loaded Derive and 7a-FIX reach the model; `render()` strips them | VERIFIED | `load_prompt` is a plain `read_text` (`personas/flows/shared/io.py:71-76`); call sites are now at `run_persona_pipeline.py:927, 1371, 2013`. I ran `render()` against `load_prompt()` on a copy of main: after removing `{#…#}` the bodies are byte-identical (stripped). Neither body contains `{{` or `{%`. |
| F3 | Gate: "`sentinel_regen.py` can't run yet (voices §37 A5)" (also §7 item 4) | STALE | Fixed in `f7e0d4c`. Per CONTEXT, regen now diffs pass outputs and re-runs Derive, so it covers F3's Derive change. |
| F4 | Code trusts the model-computed verdict (`step2_validation.py:371`) | VERIFIED | `_overall_verdict` reads `.get("verdict","PASS")`. The only code overlay is the length check (`:272-273`). |
| F4 | 7 of 89 Athens pillar results say PASS while their fields say WARN; all are voice fidelity; the seven voice-nights named; six reached the gate as overall PASS; 17 of 193 across all stored runs | VERIFIED | My replay reproduces all of it: the same 7 files; overall 6 PASS + 1 WARN (N1 Scheherazade); `_archive` 6/60 and `current-tests` 4/44 give 17/193. 89 = 90 − 1 parse-error fallback (N1 Arendt `_error`). `cross_night_echo` is null in all 30, see Problems. |
| F4 | The voice-fidelity prompt "contradicts itself" (`:37-39` vs `:41`) | DOUBTFUL | Line 41 reads as ambiguous rather than contradictory ("4/5 moves with 1 **weak** performance is PASS (the move was attempted)"; "omitted entirely is WARN"). But all 7 failing moves are outright omissions ("structurally absent", "No … appears"), so the model broke even the lenient reading. The defect stands; the diagnosis wording doesn't. |
| F4 | Decision 1: the strict rule "would have added 7 WARNs" | VERIFIED (consequence omitted) | Correct count. Unstated: overall PASS 7 → 1 of 30, voice-fidelity WARN 20 → 27 of 30. |
| F5 | Researcher prompts ask for a count-and-fix self-check; code already enforces closure | VERIFIED | Prompts at `researcher_clustering.md:85-89` and `researcher_theming.md:67-71`. Backstop at `researcher_flow.py:580-644` (dedupe, orphans → isolates) and `:659-720` (orphan clusters → single-cluster themes). Nuance: the backstop dumps orphans into isolates, which is a quality loss, not an equivalent. The replay gate the document proposes is the right one. |
| F6 | Formulation: 128 calls, about 2.99M cache tokens written, 0 read; system prompt unique per call; 5-min TTL so 1.25× write | VERIFIED | Sums over `runs/athens_night_{1,2,3}/03_provocateur/formulations/*.json`: 46 + 46 + 36 files, 2,985,437 written, 0 read. `_fill_template` puts `member_profile` and `theme_material` into the system prompt (`provocateur_flow.py:1119-1128`). `cache_control` has no TTL (`:391-399`), so the 5-min write rate of 1.25× applies (skill `prompt-caching.md:144`). Waste ≈ 0.25 × 2.99M × $5/MTok ≈ $3.7 over the event, which matches "a few dollars". |
| F6 | Triage: about 544K written, 19.6K read over 30 calls; parallel fan-out at `:1529` | VERIFIED | 544,451 / 19,609 over 30 files. `.submit` at `:1528`. The skill confirms that concurrent calls can't read each other's entries (`prompt-caching.md:252-256`). |
| F7 | `max_tokens` of 500 and 4096 are sized for thinking off; thinking counts toward `max_tokens` | VERIFIED | `synthesis_router.py:49-51`, `step2_validation.py:55-57`. Skill Opus 5.5 → Breaking change 1, step 3. 16,000 non-streaming stays under the SDK's 10-min guard (PLAUSIBLE). |
| F8 | 7c's Claude-fallback block has a false premise and "Be harsh" | VERIFIED | `persona_pass_7c_negative.md:12-18`. 7b runs on Opus 4.7 and the fallback on Sonnet 4.6. |
| F9 | Migration-relative phrasing; Pass 1.5 says "Check 4 becomes obsolete" while 1.7 still runs Check 4 | VERIFIED | Patch contexts match the current files. `pass_1_7_coherence.md` still carries Check 4 (anachronism self-consistency). |
| F10 | "READ EACH FIELD ALOUD" is a self-check trap on the Opus 5 line | VERIFIED | Present at `persona_pass_4b_artifact.md:25, 44, 69`. Skill `model-migration.md:1075` ("Self-check instructions are the same trap"). |
| F11 | The qualitative WARN bar depresses recall on literal models | VERIFIED (skill) | Sonnet 5 → "Code review harnesses": "be concrete about where the bar is". |
| L1 | 124 history-tag lines in 22 files | PLAUSIBLE | Not recounted. |
| L2/L3/L5/L7 | Keep and re-test at C62 | PLAUSIBLE | Consistent with the skill's keep list; not re-checked line by line. |
| L4 | Step 1 "private reasoning" poses low `reasoning_extraction` risk | PLAUSIBLE | Inference; the skill's trigger is prompting to reproduce the model's own reasoning. |
| L6 | Structured outputs aren't available on Opus 4.7 / Sonnet 4.6, so this is a C62-time option | DOUBTFUL | The skill's list (`tool-use-concepts.md:532`) omits 4.7 and Sonnet 4.6, but it includes legacy Opus 4.5 and 4.1. A cached list's omission isn't evidence that support is missing; the Models API `capabilities` field would settle it. Low stakes (flag-only). |
| L8 | SDK 0.94.1 has no `xhigh`, no `reasoning_extraction`, no `fallbacks`, no `display:"updates"` | VERIFIED | `output_config_param.py:14` has `low`/`medium`/`high`/`max`. There's no `fallbacks` in `resources/beta/messages/` and no `"updates"` literal. |
| §6 | "Checked clean" list (no prefill, `tool_choice`, `budget_tokens` or `stop_sequences`) | VERIFIED | grep over `runtime/flows`, `personas/flows`, `personas/*.py`. |
| §7 | Suites green with patches applied | VERIFIED (re-run on main) | Pristine `main`: runtime 385, personas 259 passed. Patched `main`: 394 and 263 passed (+9 and +4, the same deltas as the document). |
| §7 | "F1, F3–F10 each apply alone; F2 needs F1, F11 needs F4" | DOUBTFUL (F7) | `git apply --check` rejects F7 alone: its step2_validation context is F1's `cfg.thinking_kwargs()` line. It applies alone only through `patch(1)` fuzz. F2 and F11 fail alone, as stated. |
| §8 | Patches apply to current main (after C67 `02006f5` and §37 `f7e0d4c`) | VERIFIED | All 11 apply in ID order on `HEAD`, with offsets only: `transcription_flow.py` +49, `run_persona_pipeline.py` +5, `model_routing.py` +1/+2, `runtime/tests/test_model_routing.py` +26 (F1). No fuzz. The same result holds on `4e61444`. |
| header | "This file is uncommitted" | STALE | Committed in `0910a66`. |
| §9 | Pass 4a names "Tang, Thiel"; C19a's premise contradicted; inventory §10.2/§10.3 | VERIFIED | `persona_pass_4a_voice.md:213`; `runtime/OPEN_ITEMS.md:1012`; inventory `:405`. |
| §9 | `ClaudeRefusal` is retried once by callers that catch `RuntimeError` | PLAUSIBLE (incomplete) | It misses the bigger retry source, Prefect task retries (see Problems). |

**Counts:** VERIFIED 29 · PLAUSIBLE 5 · DOUBTFUL 3 · STALE 2 · WRONG 1.

## Problems with the document

1. **The F4 rule recommendation omits its effect and crosses a sibling deliverable** (the biggest issue, above).
   - `validator_evidence` §4.3 argues that voice-fidelity moves are an over-long checklist and should be pruned; F4 would make that checklist binding.
   - The mechanism (the verdict computed in code) should land regardless.
   - The rule should be chosen jointly with that proposal: for example, WARN on criteria only, or WARN on fewer than N moves performed (Plato's own criterion asks for "at least two").
2. **F2 doesn't handle Prefect task retries.** `RefusalError` raised inside the Prefect tasks will be retried by them:
   - Provocateur tasks: `retries=5`, with exponential backoff factor 15 (`provocateur_flow.py:498-499`, `:1078-1079`), about 7.5 min of waiting per pair;
   - Researcher: `retries=2`;
   - Speaker ID: `retries=2`, and C49's fallback catches only `JSONDecodeError`, so a refusal halts the session after those retries.

   A mid-stream refusal re-bills the streamed output on each retry. F2 needs a `retry_condition_fn` that excludes `RefusalError`, or the policy should state that the retries are intended. Separately, `call_claude` raises before `_record(...)`, so a billed mid-stream refusal never reaches the cost ledger.
3. **An interaction with a C67 test.** After F1, `test_transcription_speaker_id_fallback.py:44` builds `MagicMock(text=…)` without `type="text"`. The block is therefore filtered out, and the test passes on empty text instead of malformed JSON. F1 should add `type="text"` to that mock. The document couldn't have seen this, because the test post-dates it.
4. **The replay missed that `cross_night_echo` is null in all 30 Athens files.** The pillar never ran (wrong key; found by Task 1 and `validator_evidence` §4.1). F4 and F11 edit that pillar's prompt and derive its rule without noting that it has never produced data.
5. **Decision 3 (F6 split)** doesn't say that formulations fan out in parallel (`provocateur_flow.py:1684` `.submit`). A shared static prefix pays off only if one call goes first, which is the same point the document makes for triage.
6. **Small inconsistencies:**
   - the §1 counts table leaves out L4, and puts F10 under 1d while the F10 text says 1b;
   - stale line references after C67 (`transcription_flow.py:537` → `:587`, `516-519` → `564-567`, `576-579` → `624-627`; `model_routing.py:144-156` → `154-162`; `run_persona_pipeline.py:922/1366/2008` → `927/1371/2013`).
7. **Rule compliance:** no breach found.
   - The document reports its own compliance: repo not edited, no API calls, offline scripts in its scratchpad, tests only over `runtime/tests` and `personas/tests`.
   - Scope went beyond the brief's five named code files to every Anthropic call site. That is justified under the skill's Group 4 and flagged in §2.
   - Disclosure for this review: my first runtime pytest run used the default `PREFECT_HOME`, so Prefect's local test DB in `~/.prefect` may have been written. That is outside the repo and athens-2026; later runs used a scratch `PREFECT_HOME`.

## Questions for the originating session

1. **Did you weigh `validator_evidence` §4.3 (8–13 moves per card, 20/30 voice-nights already WARN) before recommending the strict rule in decision 1?** Why it matters: the strict rule leaves 1 of 30 Athens voice-nights at PASS, and a gate that warns on everything stops discriminating. What changes: if you'd accept a threshold rule instead, F4's `_derive_verdict` changes before it lands, and F11 is rebased on it.
2. **Was leaving Prefect task-level retries in place deliberate in F2?** Why it matters: "fail loud" becomes up to 5 retries with backoff (Provocateur) and repeated billing on mid-stream refusals. What changes: F2 gains a `retry_condition_fn` plus test before it's filed as ready.
3. **For decision 3, did "the split saves more" assume sequential formulation calls?** Why it matters: they're submitted in parallel, and concurrent calls can't read each other's entries. What changes: without sequencing, the split may save little, which leaves "off now" as the whole fix.
4. **Is F1's choice of explicit `disabled`, rather than adaptive + `effort: "low"` (the skill's first suggestion for Sonnet 5 thinking-off callers), meant as a permanent policy or only as the no-change default?** Why it matters: it decides whether C62 re-tests Speaker ID, cleaning and the validators with thinking on. What changes: the C62 re-test list in §6/§7.

## Operator decisions it asks for

1. **F4 (voice-fidelity rule):** should one missed move or criterion make the pillar WARN? **Recommends: yes.** It would have added 7 WARNs at Athens; see Problem 1 for the full effect.
2. **F2 (refusal policy for voice-writing steps):** fail loud, or server-side `fallbacks: "default"`? **Recommends:** fail loud for voice and editor steps; fallbacks acceptable for Researcher and Provocateur.
3. **F6 (formulation cache):** turn it off now (one line), or split the system prompt into a cached static prefix and an uncached tail? **Recommends:** off now; split later with Stage 4, which needs re-validation.
4. Implicit, from §7 and F3:
   - F1, F2, F6 and F7 can land any time;
   - F3, F8, F9 and L1 land with the Stage 4 edits, behind sentinel regen (now runnable);
   - F10 lands only as part of C62;
   - applying the same `render()` fix to `persona_pass_7a_cross_model.md` (GPT ladder) is left "if the operator wants", with no recommendation.
