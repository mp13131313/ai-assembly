# Review 2026-09-28: model-era prompt audit (Fable batch, Task 3)

**For:** the operator and the main working session (files it).
**Written:** 2026-09-28 by a Fable 5.1 session (`claude-fable-5-1`), brief `_workspace/planning/BRIEF_2026_09_28_fable_batch.md` Task 3.
**Method:** the `claude-api` skill, subcommand `prompt-audit` (its `shared/prompt-audit.md`, Steps 0–6), with the skill's `shared/model-migration.md` sections for Opus 4.7, 4.8, Opus 5, Sonnet 5 and Opus 5.5.
**Checkout:** written on `phase0-fixes` at `4e61444`; this revision's patches are rebuilt and tested against `main` at `86998b4`.
**Status:** proposal; the diff in §8 is not applied. The 2026-09-28 version is committed as `0910a66`. This corrected revision (2026-09-30) is uncommitted in the originating worktree.

**Revised 2026-09-30** after the independent review (`_workspace/planning/REVIEWS_OF_FABLE_DELIVERABLES_2026_09_29/03_model_era.md`). §10 lists every change and the points of disagreement.

---

## 1. Outcome

**Verdict:** the prompt text holds little classic model-era cruft. The real problems are in the request code and in three places where a fixed rule or developer text reaches the model. Two of them block a Sonnet 5 / Opus 5.5 switch (C62) and nothing catches them today: thinking-off requests would start thinking on Sonnet 5, and no call site handles a refusal. One is a live defect, confirmed in the Athens record: the Step 2 validators let the model compute its own verdict, and it contradicts its own rule.

**Counts by the skill's groups** (findings with a proposed diff / flag-only):

| Group | Diff | Flag only |
|---|---|---|
| 1a pressure language | 1 (F8) | 1 (L3) |
| 1b scaffolds replaced by features or code, self-checks | 4 (F3, F4, F5, F10) | 2 (L4, L6) |
| 1c over-specification | 0 | 2 (L5, L7) |
| 1d fossils (migration-relative text, model-version workarounds) | 1 (F9) | 2 (L1, L2) |
| Tool descriptions | 0 (no tools anywhere) | — |
| 4 request config and architecture | 4 (F1, F2, F6, F7) | 1 (L8) |
| Severity-filter wording (the migration guide's review-harness shift) | 1 (F11) | — |

**The three highest-impact findings:**

- **F1. "Thinking off" is sent by leaving the field out.** On Sonnet 4.6 that means no thinking. On Sonnet 5 it means adaptive thinking (skill: `model-migration.md` → Sonnet 5 → "Silent default change"). Moving any thinking-off step to Sonnet 5 would silently turn thinking on, inside `max_tokens` budgets sized for no thinking (500 for the synthesis router, 4096 for the validators and Speaker ID). Speaker ID would also crash: it reads `resp.content[0].text` (`runtime/flows/transcription_flow.py:587`), and the first block would be a thinking block. `docs/LLM_CALL_INVENTORY.md` §10.2 says the opposite ("Sonnet 5 accepts thinking disabled (no break there)"). The loader can't catch this: the config is right and the request shape is wrong. CONFIRMED by reading all 8 call sites and the tests that pin the omission. The Sonnet 5 behaviour is documented, not run.
- **F2. No Anthropic call site checks `stop_reason == "refusal"`.** Opus 5.5 adds `bio` and `reasoning_extraction` classifiers to `cyber`, and Sonnet 5 runs cyber safeguards. A decline is HTTP 200 with empty or partial content. Today it would pass as a normal reply or fail misleadingly:
  - Voice steps would accept empty or partial text (`runtime/flows/voice/_anthropic_call.py:160-178`).
  - Provocateur would blame "adaptive thinking consumed the entire max_tokens" (`runtime/flows/provocateur_flow.py:432-438`), and its Prefect task would retry the declined request 5 times with backoff.
  - Persona passes would report "Claude returned invalid JSON" (`personas/flows/shared/clients.py:297`).
  - The synthesis router would pick the lowest-numbered theme and log the wrong cause ("model returned unknown theme_id").

  The skill's Opus 5.5 checklist marks this `[BLOCKS]`. CONFIRMED by grep: `stop_reason` is only read for logging (`provocateur_flow.py:420`) and in `call_claude`'s max_tokens warning.
- **F4. The Step 2 validators ask the model to compute `verdict` from fields it has just filled, and code trusts that verdict** (`runtime/flows/voice/step2_validation.py:371`). The voice-fidelity prompt is ambiguous: its rule says any `performed: false` is WARN (`voice_step2_validation_voice_fidelity.md:37-39`), and its next paragraph lets "1 weak performance" pass (`:41`). CONFIRMED by an offline replay of every stored validation file. In the Athens record, 7 of 89 pillar results say PASS while their own fields say WARN under the prompt's stated rule; all seven misses are outright omissions. All seven are voice fidelity: N1 Dostoevsky, Plato, Scheherazade; N2 Arendt, Plato; N3 Battuta, Octopus. Six of them reached the operator gate as overall PASS. Across all stored runs, including `_archive/` and `current-tests/`, the count is 17 of 193.

  The stated rule is itself too strict. The cards carry 8–13 moves against a schema of 3–5 (`REVIEW_2026_09_28_validator_evidence.md` §4.3). Applied as written, it would leave 1 of 30 Athens voice-nights at PASS. The patch therefore derives the verdict in code with a threshold: WARN on any failed quality criterion, or when fewer than 2 moves show. On Athens that keeps voice-fidelity WARNs at 20 of 30, the same count as today. The overall gate goes from 7 PASS / 21 WARN / 2 HOLD to 6 / 22 / 2. The rule disagrees with the model's own verdict on 2 voice-nights: N3 Battuta, which the model passed despite a failed criterion, and N2 Dostoevsky, which it warned on moves alone.

**Brief question 1: what cruft written for older models can go now?** Less than expected. There are no think-step-by-step or scratchpad instructions, no prefills, no forced tool use, and no sampling parameters reaching a thinking call. There are no anti-laziness boosters, no grader vocabulary and no narration suppressors. All-caps emphasis is sparse (at most 6 per file), and nearly all of it sits on schema contracts or on failures shown on Opus 4.7, so the keep list protects it. What can go now:

- the developer headers that leak into three raw-loaded prompts (F3);
- the model-computed verdict (F4, also a live defect);
- a redundant self-count in the Researcher (F5), which code already enforces;
- the dead Provocateur cache writes (F6): 2.99M tokens written in Athens, 0 read;
- the migration-relative "NO LONGER / pre-1-arch-03" text in persona prompts (F9, plus about 100 bare history tags, L1). These should ride along with the Stage 4 edits to the same passes, since those need sentinel regeneration anyway.

**Brief question 2: what would a C62 migration need in the prompts?** Very little prompt text: the 4b self-check phrasing on Opus 5.x (F10), the 7c Claude-fallback block on Sonnet 5 (F8), the safeguards WARN bar on Sonnet 5 (F11), and the re-test list in §6. The real C62 needs are in request code:

- F1, which must land before any thinking-off step moves to Sonnet 5;
- F2, which must land before Opus 5.5 or Sonnet 5;
- F7, if any thinking-off route gets thinking.

Effort and thinking-off-on-Opus-5.5 are already enforced by the loader (`runtime/flows/shared/model_routing.py:154-162`), and `call_claude` drops temperature for models that reject it (`personas/flows/shared/clients.py:158`), so none needs a prompt change.

**Operator decisions** (each detailed below):

1. **F4:** the voice-fidelity threshold. The diff warns on any failed criterion, or when fewer than `_MIN_MOVES_PERFORMED = 2` moves show. Two is the cards' own bar: Plato's criterion asks that "at least two" moves operate visibly. Recommended: this rule, chosen together with the move-list pruning in `validator_evidence` §4.3. The strict rule it replaces would have left 1 of 30 Athens voice-nights at PASS.
2. **F2:** refusal policy for voice-writing steps. The diff detects and fails loud, without retrying the declined request. The alternative is server-side `fallbacks: "default"`, where another model writes that voice's piece. Recommended: fail loud for voice and editor steps; fallbacks are acceptable for Researcher and Provocateur.
3. **F6:** switch formulation caching off (the one-line diff), or split the system prompt into a cached static prefix and an uncached per-call tail. Formulations fan out in parallel (`provocateur_flow.py:1684`), and concurrent calls can't read each other's cache entries. So the split would pay only if a pre-warm call per night ran first, for a few dollars an event. It would also re-layout a prompt that shapes voice inputs, which needs re-validation. Recommended: off, and no split.

---

## 2. Assumptions (Step 0)

- **Scope** (from the brief):
  - all 75 prompt files: `personas/flows/shared/prompts/*.md` (56) and `runtime/flows/shared/prompts/*.md` (19; `_archive/` excluded);
  - the five named code files: `runtime/flows/voice/_anthropic_call.py`, `runtime/flows/voice/card_assembly.py`, `runtime/flows/editor/card_assembly.py`, `personas/flows/shared/clients.py`, `personas/flows/shared/chat_prompt_builder.py`;
  - plus everything the inventory found that also reaches the model or builds requests: the loaders (`runtime/flows/shared/io.py:219-231`, `personas/flows/shared/io.py:71-76`, `personas/flows/shared/prompt_render.py`), every Anthropic call site, and the inline prompts (§3).
- **Target models:** two sets, per the brief. "Cruft now" is judged against production today, Opus 4.7 and Sonnet 4.6. "C62 needs" is judged against Opus 5.5 and Sonnet 5, layering the skill's Opus 4.8 → Opus 5 → Opus 5.5 sections, since Opus 5.5 inherits Opus 5's behaviour as its baseline.
- **Non-Anthropic prompts:** recorded but not audited against Claude behaviour, and no provider switch is proposed.
  - Pass 1a: Perplexity.
  - Pass 1b: Gemini.
  - `persona_pass_7_anachronism.md`, `persona_pass_7a_cross_model*.md`, and the Step 1 validation prompts `voice_step1_validation_*.md`: the GPT/Gemini ladders.
  - `persona_pass_7c_negative.md`: Gemini primary. Only its Claude-fallback branch is audited.
- **Manual prompts:** `pass_0b_*.md` and `_pass_0b_research_discipline.md` are pasted by the operator into claude.ai Research. They were read for text patterns only; no API request is built.
- **Language:** Python; `anthropic==0.94.1` in both venvs.
- **Not re-reported (filed):**
  - Athens/Munich wording (PLAN 2.1 / C52, C55);
  - "12 voices" and Peter Thiel (C68 A14);
  - "FROM NIGHT N-1" (C68 A15);
  - model names in prompt text (voices §36 leftovers);
  - "You are I am …" (C68 A6);
  - Speaker ID's `max_tokens=4096` (C49, roadmap);
  - the editor cache items (C65, C66).
- **Offline scripts**, all under this session's scratchpad. None calls an API, and athens-2026 was only read.
  - `signals.sh` greps the signal patterns.
  - `model_facing.py` greps only the text the model sees, stripping Jinja comments where the loader renders.
  - `verdict_check.py` replays validator verdicts.
  - `build_patches.py` builds the §8 patches on a scratch copy and asserts every anchor.
  - `check_patches.py` checks that each patch applies alone and that the series reproduces the tested tree.
  - For the 2026-09-30 revision: `build_patches_main.py` and `check_patches_main.py` do the same against an export of `main` at `86998b4` (the check uses `git apply --check`, no fuzz), and `revise_body.py` applies the report corrections.
- **Disclosure:** the 2026-09-28 runtime test runs used the default `PREFECT_HOME`, so Prefect's local test database under `~/.prefect` may have been written. That is outside the repo and athens-2026. The 2026-09-30 runs used a scratch `PREFECT_HOME`.

## 3. Inventory (Step 1)

| Surface | Files | How it reaches the model | Model today |
|---|---|---|---|
| Voice Step 1/2/3 closing prompts | `voice_step1_reasoning.md`, `voice_step2_artifact.md`, `voice_step3_amendment.md` | Raw read (`runtime/flows/shared/io.py:231`), appended after the card sections (`runtime/flows/voice/card_assembly.py:498-504`) | Opus 4.7, adaptive |
| Voice card system prompt | card fields | `runtime/flows/voice/card_assembly.py:366-506`: prefix/tail, both cached 1h | Opus 4.7 |
| Continuity | `voice_continuity.md` | raw | Sonnet 4.6, adaptive |
| Step 2 validators | `voice_step2_validation_*.md` (4) | raw, non-streaming `messages.create` (`step2_validation.py:93-100`) | Sonnet 4.6, thinking off |
| Editor | `editor_dossier.md` + editor card + deployment context | `runtime/flows/editor/card_assembly.py:286-368` | Opus 4.7, adaptive |
| Synthesis router | inline `_SYSTEM_PROMPT` (`runtime/flows/editor/synthesis_router.py:53-66`) | inline | Sonnet 4.6, off, `max_tokens=500` |
| Researcher | `researcher_extraction/clustering/theming.md` | raw | Opus 4.7, adaptive |
| Provocateur | `provocateur_triage_voice/triage_flags/formulation.md` | raw + `_fill_template` | Opus 4.7, adaptive |
| Transcription | `transcription_speaker_id.md`, `transcription_cleaning.md` | raw | Sonnet 4.6, off |
| Persona passes 0b-tailor, 1.1–1.7, 1d, 2–6, 7-pre ×3, 7b, 7c, CT | `personas/flows/shared/prompts/*.md` | Jinja `render()` (`prompt_render.py:41-51`) strips `{# … #}` | Opus 4.7 (7-pre, 7c fallback and CT on Sonnet 4.6) |
| **Raw-loaded persona prompts** | `pass_0a_voice_config.md` (`run_pass0a_voice_config.py:207`), `persona_derive.md` (`run_persona_pipeline.py:927, 2013`), `persona_pass_7a_fix.md` (`:1371`), `persona_pass_7a_cross_model.md` (`:1096, 1933`) | `read_text()` / `load_prompt()`, so **Jinja comments reach the model** | Opus 4.7 (7a: GPT ladder) |
| Inline persona system strings | CT `"You compress persona fields…"` (`run_persona_pipeline.py:476`); 1d `"You are a textual scholar…"` (`:591`) | inline | Sonnet 4.6 / Opus 4.7 |
| Chat artifact | `personas/flows/shared/chat_prompt_builder.py` | field strip only; pasted into claude.ai by the operator | — |
| Request builders | `_anthropic_call.py`, `clients.py:80-300`, `step2_validation.py:78-108`, `synthesis_router.py:106-160`, `transcription_flow.py:500-600`, `researcher_flow.py:108-127, 290-540`, `provocateur_flow.py:349-465` | model, thinking, effort, `max_tokens`, `cache_control` | per `model_routing.json` |

No tool definitions, no few-shot message turns, no assistant-turn prefill on any generation call, and no multi-turn histories. The only assistant-role messages go to `count_tokens` for thinking-token telemetry (`_anthropic_call.py:55`, `clients.py:43`). Opus 4.7 accepts them: 51 of the 53 `thinking_tokens` values in Athens N1 `04_voice/` are nonzero.

## 4. Provenance (Step 2)

`git blame` on the lines behind the findings shows all of them date from April–May 2026 and were written for Opus 4.7 and Sonnet 4.6:

- `persona_derive.md:1-6`: `9b58193`, 2026-04-15, Phase 4 Derive, which then ran on Sonnet 4.6 without thinking.
- `persona_pass_7c_negative.md:12-18`: `c90e415`, 2026-04-15.
- `persona_pass_7a_fix.md:1-18`: `64b5029`, 2026-04-23, when 7a-FIX ran on Sonnet 4.6.
- `persona_pass_4b_artifact.md:19-44`: `bba3016`, 2026-04-21, Phase L register failures.
- `researcher_clustering.md:85-89`: `9b5de04`, 2026-04-15, initial commit.
- Validator verdict rules: `dcdd0d6`, 2026-05-04, C28b.
- Formulation `cache_system=True`: `0a3ab9c`, 2026-05-01, C19a.

The persona prompts' emphatic lines mostly carry an FU#, a date and a stated failure. By the skill's rule, those are tied to failures on the production model and stay. On a model switch they become the re-test list (§6).

## 5. Findings (Step 5): proposed-diff items, highest confidence first

Every finding has a patch in §8 with the same ID. Labels: CONFIRMED means read or run here; PLAUSIBLE means inferred from the skill's documented model behaviour without running a model.

### F1. Thinking "off" is omitted, not sent: Sonnet 5 would think silently. High

- **Location:**
  - `runtime/flows/voice/_anthropic_call.py:110-113`
  - `runtime/flows/voice/step2_validation.py:89-92`
  - `runtime/flows/editor/synthesis_router.py:132-135`
  - `runtime/flows/transcription_flow.py:564-567, 624-627`
  - `runtime/flows/provocateur_flow.py:401-404`
  - `runtime/flows/researcher_flow.py:125-127`
  - `personas/flows/shared/clients.py:160-171`
  - plus `transcription_flow.py:587` (`resp.content[0].text`)
  - the tests pinning the omission: `runtime/tests/test_model_routing_call_sites.py:247` and 16 more; `personas/tests/test_call_claude_config.py:64, 85`.
- **Evidence:** `{"thinking": {...}} if cfg.thinking_on else {}` at every site.
- **Pattern:** Group 4, thinking config for the wrong model. Skill: `model-migration.md` → Sonnet 5 → "Silent default change: adaptive thinking on when `thinking` is omitted", checklist item "[TUNE] Thinking-field omitted". Opus 5 is the same ("Breaking change 1: thinking is on by default").
- **Why:**
  - On Sonnet 5 a thinking-off step would think. That adds cost and latency.
  - Those steps' `max_tokens` would then cover thinking plus the reply. Validators are at 4096, the synthesis router at 500, and C49 already truncates Speaker ID at 4096.
  - Speaker ID would raise `AttributeError` on the thinking block.
  - The loader's refusal rules don't help: `"thinking": "off"` is valid for Sonnet 5.
  - Today the change is a no-op: an explicit `{"type": "disabled"}` means the same as omission on Sonnet 4.6 and Opus 4.7 (skill thinking table). PLAUSIBLE until the first live thinking-off call confirms Sonnet 4.6 accepts it.
- **Action:** `rewrite`. Add `StepConfig.thinking_kwargs()` to both byte-identical loader copies, returning adaptive+summarized, `{"type": "disabled"}`, or `{}`. Use it at every site. Read Speaker ID's text blocks by type. Rewrite the pinned test assertions, add one unit test, and correct `docs/LLM_CALL_INVENTORY.md:405`. Give the C67 test mock at `runtime/tests/test_transcription_speaker_id_fallback.py:44` `type="text"`; without it the block is filtered out and the test passes on empty text instead of malformed JSON. `call_claude` sends `disabled` only when a step config exists; raw `model=` dev calls keep omission.
- **Policy:** explicit `disabled` is the no-change default, not a permanent choice. The skill's first suggestion for thinking-off callers moving to Sonnet 5 is adaptive thinking with `effort: "low"`. C62 should trial that for Speaker ID, cleaning, the validators and the synthesis router; it is a one-line `model_routing.json` edit per step, and F7 already gives those routes room.
- **Gate:** none for voices (no request changes on today's models). Suite results are in §7.

### F2. No refusal handling anywhere. High

- **Location:**
  - `_anthropic_call.py:150-194` (and its retry at `:179-188`)
  - `step2_validation.py:93-108`
  - `synthesis_router.py:138-160`
  - `transcription_flow.py:569-587, 630-646`
  - `researcher_flow.py:303-313, 403-413, 522-532`
  - `provocateur_flow.py:405-439`
  - the Prefect task decorators: `transcription_flow.py:508-512, 590-594`; `researcher_flow.py:261-265, 338-342, 469-473`; `provocateur_flow.py:496-500, 573-577, 1076-1080`
  - `clients.py:196-300`
- **Pattern:** Group 4 / migration checklist. Skill: `model-migration.md` → Opus 5.5 → "Safeguards" and checklist "[BLOCKS] Handle `stop_reason: "refusal"` before reading `content`"; Sonnet 5 → "cybersecurity safeguards"; Opus 4.7 → "Real-time cybersecurity safeguards".
- **Why:** a decline returns 200 with empty or partial content, and `reasoning_extraction` declines are not retried on a fallback. This is latent today: the Athens content domain rarely touches cyber or bio. On Opus 5.5 the classifier set widens.
- **Retries:** `stream_voice_call` does not retry a refusal today, because a refusal raises nothing. Once the check raises, two retry layers would re-send the declined request: `stream_voice_call`'s own retry, and the Prefect task retries. Provocateur tasks have `retries=5` with backoff 15, 30, 60, 120, 240 s, so a refusal would take about 7.75 minutes to surface, and a mid-stream refusal would be billed again on each attempt. The first version of this patch handled only the first layer; that was an oversight, not a choice.
- **Action:** `add`.
  - New `runtime/flows/shared/anthropic_checks.py` with `RefusalError` and `raise_if_refused()`, called after every final message in the runtime.
  - `stream_voice_call` re-raises a refusal without its generic retry.
  - `retry_unless_refused`, a Prefect `retry_condition_fn`, goes on the 8 Anthropic-calling tasks. Every other failure keeps its retry policy.
  - The synthesis router falls back and labels the fallback "refusal".
  - `call_claude` records the call in the cost ledger, then raises `ClaudeRefusal` before JSON parsing. A mid-stream refusal is billed, so it is recorded first.
  - Tests: 6 runtime, 1 personas. One runs a real Prefect task: a refused task runs once, and a task failing with `ValueError` runs three times.
- **Open point, not in the diff:** a Speaker ID refusal now halts that session at once. C49's passthrough catches only `JSONDecodeError` (`transcription_flow.py:790`). The operator may prefer that a refusal also degrades to the all-Unidentified passthrough.
- **Not in the diff (operator decision 2):** the `fallbacks: "default"` opt-in. It needs the `server-side-fallback-2026-07-01` beta header and the `client.beta` path, and for voice-writing steps it means another model writes the voice.
- **Note:** SDK 0.94.1 types `stop_details.category` as `cyber | bio` only (`anthropic/types/refusal_stop_details.py`). The code reads it with `getattr`, so `reasoning_extraction` passes through.

### F3. Developer headers in raw-loaded persona prompts reach the model. High

- **Location:**
  - `personas/flows/shared/prompts/persona_derive.md:1-6`: "Phase 4 — Derive (Claude Sonnet 4.6) … Pure compression task — Sonnet is correct here, no thinking needed."
  - `persona_pass_7a_fix.md:1-15`: "the writer with Opus + thinking + critique tends toward EXPANSION rather than the TRIM" … "Model: claude-sonnet-4-6 + thinking".
  - Loaded with `load_prompt()` at `personas/run_persona_pipeline.py:927, 1371, 2013`, not `render()`, so the `{# … #}` survives.
- **Pattern:** 1b, prose that steers thinking depth ("no thinking needed"), plus 1d, model-version workaround and trait claim.
- **Why:** both steps run on Opus 4.7 with adaptive thinking (`model_routing.json:73, 69`). The system prompt tells a thinking model it doesn't need to think, names the wrong model, and tells Opus-with-thinking that Opus-with-thinking over-expands. On Opus 5.5 a "don't think" line can't be followed (skill 1b row).
- **Action:** `rewrite`. Load all three through `render()`, which strips the comments and keeps the developer notes in the files. Adds `personas/tests/test_raw_prompt_headers.py`. A side benefit: `render()` makes `{{ model_name(...) }}` available, which is what voices §36 asks for in 7a-FIX's body ("written by another model (Claude Opus 4.7)"). The same leak exists in `persona_pass_7a_cross_model.md`, loaded raw at `:1096, 1933` and sent to the GPT ladder. It is outside the Claude target, but the header is developer text in any model's prompt, the file has no Jinja syntax, and its rendered body is otherwise unchanged. The patch now includes it, and that is the recommendation.
- **Gate:** the inputs of Derive, 7a-FIX and the 7a validator change, so this goes through the sentinel gate and lands with Stage 4. `personas/scripts/sentinel_regen.py` runs again (voices §37 A5, fixed in `f7e0d4c`).

### F4. Validator verdicts are computed by the model, and it breaks the prompt's rule. High (observed)

- **Location:**
  - `voice_step2_validation_safeguards.md:31-33, 48-51`
  - `voice_step2_validation_engagement.md:44-46, 54-56`
  - `voice_step2_validation_voice_fidelity.md:23-25, 37-41`
  - `voice_step2_validation_cross_night_echo.md:33-35, 49-52`
  - code trusts it: `runtime/flows/voice/step2_validation.py:371`; the engagement length overlay at `:272-273`
- **Pattern:** 1b, an arithmetic rubric the model must compute, belongs in code; Group 4, a deterministic step executed by an LLM.
- **Evidence:** §1. The replay script re-applies each prompt's own stated rule to the stored fields.
- **The rule.** Voice fidelity under different rules, replayed on the 30 Athens voice-nights (N1 Arendt's pillar errored and counts as WARN throughout):

  | Rule | Voice-fidelity WARN | Overall PASS / WARN / HOLD |
  |---|---|---|
  | The model's own verdict (today) | 20 | 7 / 21 / 2 |
  | The prompt's stated rule: any missed move or failed criterion | 27 | 1 / 27 / 2 |
  | **Proposed:** any failed criterion, or fewer than 2 moves showing | 20 | 6 / 22 / 2 |

  - The cards carry 8–13 moves, and the artifacts performed between 2 and 11 of them. So the move floor never fires on Athens data; it guards against a piece that shows almost none of the voice.
  - Warning on criteria alone gives the same Athens numbers.
  - The criteria failures are the consistent signal (`REVIEW_2026_09_28_validator_evidence.md` §4.3), and the proposed rule keeps all of them.
  - If the move lists are pruned to the schema's 3–5 as that report proposes, revisit `_MIN_MOVES_PERFORMED`.
- **Cross-night echo.** This pillar never ran in Athens: `cross_night_echo` is null in all 30 files, because the loader reads a key the published artifact doesn't have (`validator_evidence` §4.1). Its derived rule and prompt edit are therefore untested on real data.
- **Action:** `rewrite`.
  - `_derive_verdict(pillar, parsed)` in `step2_validation.py` sets each pillar's `verdict` from the fields. The model keeps every judgment.
  - Delete the four "Compute `verdict`" blocks and the `verdict` key from the four schemas.
  - Voice fidelity uses the threshold rule above (`_MIN_MOVES_PERFORMED = 2`).
  - Rewrite the ambiguous voice-fidelity paragraph so it calibrates the `performed`/`passed` judgments instead of the verdict.
  - Replace "signature moves the voice MUST perform" with "repertoire" in the prompt (`voice_step2_validation_voice_fidelity.md:9`) and in the user message and docstring (`step2_validation.py:292, 297`).
  - Tests: 5 new.
- **Gate:** no voice output changes; the operator gate's outcomes do (decision 1). The existing gate tests mock the pillar functions and still pass.

### F5. Researcher prompts ask the model to count and fix closure; code already enforces it. Medium

- **Location:** `runtime/flows/shared/prompts/researcher_clustering.md:85-89` ("Before returning, verify … The count of unique `ref` values … must equal the total … find the error and fix it before returning") and `researcher_theming.md:67-71`. The code backstop, CONFIRMED: `researcher_flow.py:587-644` (dedupe, orphans → isolates) and `:659-720` (orphan clusters → single-cluster themes).
- **Pattern:** 1b / Opus 4.7 checklist "Remove knowledge-work verification scaffolding"; Opus 5 → "Self-check instructions are the same trap" (over-verification).
- **Action:** `rewrite`. State the invariant once and drop the count-and-fix choreography.
- **Gate:** the Researcher shapes the night's themes, so replay one recorded night when convenient (an operator-run API call).

### F6. Provocateur formulation writes a cache entry per call that nothing reads. Medium (observed cost)

- **Location:** `runtime/flows/provocateur_flow.py:1146` (`cache_system=True,  # C19a: voice's 3-5 formulations share system prompt`). The system prompt is filled per call with `member_profile` and `theme_material` (`:1119-1128`; template `provocateur_formulation.md:145-168`).
- **Evidence:** CONFIRMED from athens-2026 `runs/athens_night_{1,2,3}/03_provocateur/formulations/*.json`. 128 calls, `cache_creation_input_tokens` sum ≈ 2.99M, `cache_read_input_tokens` sum = 0. C19a's premise (`runtime/OPEN_ITEMS.md:1012`) doesn't hold, because the theme differs per call. This is the same class of bug C66 fixed for the editor.
- **Pattern:** Group 4, cache-hostile ordering (per-call content inside the cached block).
- **Why:** each write bills 1.25× input, a few dollars per event at Opus 4.7 prices. It changes no output.
- **Action:** `rewrite` to `cache_system=False` with a comment carrying the evidence.
- **The split (decision 3).** The first version said a cached static prefix "saves more". That assumed calls could read each other's entries. They can't: formulations are submitted in parallel (`provocateur_flow.py:1684`), like triage. A split would pay only with a pre-warm call per night, and the whole waste is about $3.7 per event. Not worth a prompt re-layout.
- **Related, flag only:** per-voice triage wrote ≈ 544K and read 19.6K across 30 calls. Its system prompt is shared, but the ten calls fan out in parallel (`provocateur_flow.py:1529`), so none can read another's entry. The fix is to run one call first, then the rest; not in the diff.

### F7. `max_tokens` sized for thinking-off calls. Medium (conditional on C62)

- **Location:** `runtime/flows/editor/synthesis_router.py:49-51` (500) and `runtime/flows/voice/step2_validation.py:55-57` (4096). Speaker ID's 4096 is C49 (filed).
- **Pattern:** Group 4, "a `max_tokens` sized for a thinking-off route cuts replies off" (skill Opus 5.5 → Breaking change 1, step 3).
- **Why:** if a C62 switch puts thinking on these routes (Opus 5.5 forces it via the loader), 500 tokens can't hold thinking plus two lines, and the router would fall back to the lowest-numbered theme and log a parse failure.
- **Action:** `rewrite`. Floor at 16000 when `cfg.thinking_on`; unchanged today.

### F8. Pass 7c's Claude-fallback block: a false premise and "Be harsh". Medium

- **Location:** `personas/flows/shared/prompts/persona_pass_7c_negative.md:12-18`: "You generated the worked provocations being evaluated. … Be harsh. The goal is to grow the banned lists".
- **Pattern:** 1a pressure language; Sonnet 5 → "More literal instruction following … holdover style directives now apply at face value".
- **Why:**
  - The premise is false: 7b runs on Opus 4.7, and this fallback runs on Sonnet 4.6.
  - Read literally, "grow the banned lists" rewards adding items, and banned lists ride in every runtime call.
  - The same-family bias concern is real (7a's header cites 10–25% self-preference bias).
- **Action:** `rewrite` to a same-family caveat plus a concrete bar: add an item only when you can point to the passage.
- **Gate:** card content (banned lists), so sentinel regen; lands with Stage 4.

### F9. Migration-relative phrasing in model-facing persona prompts. Medium

- **Location:**
  - `pass_1_1_merge.md:214-216, 272-274` (a `// NOTE` comment inside a JSON example)
  - `pass_1_2_merge.md:73-74`
  - `pass_1_3_merge.md:69, 75-76, 81-82, 265-268`
  - `pass_1_5_merge.md:63-67, 147-152`
  - `pass_1_6_merge.md:107`
  - `pass_1_7_coherence.md:43, 53, 72-74, 100`
  - `persona_pass_6_user.md:17-19`
  - `pass_0a_voice_config.md:62, 136`
  - `persona_pass_1d_excerpt_selection.md:13-18`
- **Evidence:**
  - "`anachronisms_to_avoid` is NO LONGER an output field";
  - "This is what pre-1-arch-03 dropped";
  - "`urls` is NO LONGER an output key";
  - "Pass 1.7 coherence Check 4 … becomes obsolete". This contradicts 1.7, whose Check 4 still exists.
- **Pattern:** 1d, "Migration-relative phrasing … a diff against a previous prompt version the model never saw".
- **Action:** `rewrite` each as a current rule. The JSON example's comment is removed, because a comment inside a JSON example invites comments in JSON output.
- **Gate:** voice-writing passes, so land each hunk with that pass's Stage 4 edit and its sentinel regen.

### F10. Pass 4b's "READ EACH FIELD ALOUD BEFORE RETURNING". Medium (C62 only)

- **Location:** `persona_pass_4b_artifact.md:25-26, 43-44, 69-72`.
- **Pattern:** 1b self-check; Opus 5 → "per-prompt re-check phrasing … triggers the same extra work … inverts a standard prompting best practice"; carried into Opus 5.5.
- **Why:** the quality bar (a field written as a scholar or designer describing the voice fails) is load-bearing; it was shown on Opus 4.7 (`bba3016`, 2026-04-21), so it stays. Only the re-read procedure is the Opus 5-era trap.
- **Action:** `rewrite`. Keep the bar and drop the procedure. **Do not land on Opus 4.7.** Land it with the C62 switch of Pass 4b and its sentinel regen.

### F11. Safeguards WARN bar is qualitative. Medium (C62 only)

- **Location:** `voice_step2_validation_safeguards.md:53`: "be discerning on WARN-tier (only flag clear violations, not mild stylistic shadings)".
- **Pattern:** the migration guide's review-harness shift (Opus 4.7, 4.8 and Sonnet 5 → "Code review harnesses"): qualitative filters are followed literally and depress recall; "be concrete about where the bar is".
- **Action:** `rewrite` to a concrete bar: quote the span and name the card rule. Same false-positive intent.
- **Gate:** compare WARN counts on the next dryrun. Applies after F4 (shared context lines). It edits only the safeguards prompt.

## 6. Flag-only items (low confidence, no diff)

- **L1. About 100 bare history tags in model-facing persona text:** FU# numbers, "1-arch-03", dates, "(1.4-02 ABSORBED)". The offline count is 124 lines in 22 files, and 102 remain after F9. The most are in `persona_pass_2_identity_boundaries.md` (14), `pass_1_6_merge.md` (9), `pass_1_7_coherence.md` (8) and `persona_pass_6_corpus.md` (7). They are archaeology, not instructions; the harm is small. Strip them in the same Stage 4 edit as each pass's content changes, not as a separate regen.
- **L2. "The model tends to…" reasons:** `persona_pass_4a_voice.md:206-210` ("default-composed-arc bias of the underlying model tends to suppress it") and `persona_pass_4b_artifact.md:38-39` ("the model tends to slip into designer-voice"). These are reasons tied to failures shown on Opus 4.7, so they stay now. Re-test in the C62 sentinel run.
- **L3. Scoped emphasis:**
  - `pass_0b_tailor.md:54` (IMPORTANT, tied to the 2026-04-24 Plato rewrite failure);
  - the six "— STOP." lines in `pass_1_1`–`1_6_merge.md` (1-arch-04, 73% content loss);
  - `persona_pass_2_identity_boundaries.md:353, 415`;
  - `persona_pass_4b_artifact.md:206`;
  - `persona_pass_7b_smoke_test.md:25`;
  - `persona_pass_7pre_verify_batch.md:16`;
  - `editor_dossier.md:18, 206` "INVIOLATE".

  Each carries its reason. This is the skill's allowed kind of emphasis: a tested, scoped fix. Re-test at C62.
- **L4. Step 1 "private reasoning" and Opus 5.5's `reasoning_extraction` classifier.** `voice_step1_reasoning.md:5-7, 61-67` asks for the voice's reasoning as the deliverable, not a copy of the model's thinking, so risk is low. Watch the refusal counts F2 adds during the first Opus 5.5 sentinel run.
- **L5. Decision choreography** (weigh → focus → stance → form → compose): `voice_step2_artifact.md:13-59`, `editor_dossier.md:63-118`. It is 1c step-choreography for a judgment task, but it is the tested fix for the synthesis bias (2026-05-02, Test 3). Keep; re-test at C62.
- **L6. JSON-only instructions plus fence-stripping and regex parsing:** `step2_validation.py:111-121`, `clients.py:280-297`, "Return only the JSON object" in 30+ prompts. The skill's replacement is structured outputs (`output_config.format`, typed in SDK 0.94.1). The skill's cached support list names Opus 4.8, Opus 5, Sonnet 5 and others, and omits Opus 4.7 and Sonnet 4.6. An omission from a cached list doesn't show that support is missing; the Models API `capabilities` field would settle it (one read-only call, not made here). Either way, pilot it first on the Step 2 validators (small flat schemas; F4 already touches that module).
- **L7. Speaker ID's "PERFORM FIVE PASSES IN ORDER"** (`transcription_speaker_id.md:5-42`) and **continuity's "≤500 tokens" / "≤300 tokens"** (`voice_continuity.md:9, 14`). Choreography and numeric caps, but on a thinking-off Sonnet route with a documented method, and the caps size a block other prompts consume. Keep; revisit if Speaker ID moves to a thinking model.
- **L8. SDK pin:** 0.94.1 types `effort` without `xhigh` and refusal `category` without `reasoning_extraction`, and it has no `fallbacks` or `display: "updates"`. Dict requests pass through, so nothing breaks. A C62 migration that wants the fallback opt-in should consider the SDK bump (skill `upgrade` subcommand).

**Checked clean:**

- no assistant-turn prefill on generation calls;
- no `tool_choice`, tools or computer use;
- no `budget_tokens` or `stop_sequences`;
- temperature never reaches a thinking call (loader and `call_claude`, `clients.py:158`);
- single-turn requests only, so preserved-thinking and history-editing rules don't apply;
- no timestamps or UUIDs in system prompts (grep of both `card_assembly.py`, `chat_prompt_builder.py`, `prompt_render.py`);
- `display: "summarized"` set explicitly wherever thinking is on;
- no think-step-by-step, scratchpad or `<thinking>` instructions;
- no narration suppressors or anti-formatting rules outside voice-content fields.

## 7. Landing order and gates

1. **F1, F2, F6, F7** (request code): land any time. No output changes on today's models, suites green. F1 and F2 are prerequisites for C62; F2 and F7 need F1 applied first.
2. **F4** (plus **F11** on top): after decision 1. Changes the operator gate, not voice text.
3. **F5**: with a replay of one recorded night's Researcher.
4. **F3, F8, F9, L1**: with the Stage 4 edits to those passes (Task 2's design), behind sentinel regen. The regen script runs again since `f7e0d4c`.
5. **F10, and the re-tests in L2/L3/L5/L7**: only as part of C62, inside the sentinel comparison. In that comparison, also measure length-envelope compliance per voice (Step 2 validation's mechanical length check), since the Opus 5 line writes longer deliverables at the same effort.

**Verification done:** each patch was built on a scratch export of `main` at `86998b4`, with every anchor asserted.

| Suite | Pristine copy | Patched copy |
|---|---|---|
| Runtime (`runtime/tests`) | 385 passed | 397 passed |
| Personas (`personas/tests`; `personas/scripts` not run) | 259 passed | 264 passed |

- No `.env` was reachable and the project root pointed at an empty scratch directory, so no API call was possible.
- Checked with `git apply --check` (no fuzz): F1, F3–F6 and F8–F10 each apply alone to `main`. F2 and F7 need F1, and F11 needs F4.
- The 2026-09-28 version's patches were built on `4e61444`, where the suites went 368 → 377 and 242 → 246.
- Applied in order, the series reproduces the tested tree exactly.

## 8. Proposed diff (not applied)

Apply from the repo root with `git apply <file>`, in ID order. Each patch is one finding.

### F1. Send thinking-off explicitly (`StepConfig.thinking_kwargs()`); read Speaker ID text by block type

`F1_thinking_off_explicit.patch`

````diff
--- a/docs/LLM_CALL_INVENTORY.md
+++ b/docs/LLM_CALL_INVENTORY.md
@@ -402,7 +402,7 @@
 
 ### 10.2 (b) Sonnet 4.6 → Sonnet 5 — most previously-flagged breaks are now defused by `call_claude`'s sampling-params gate
 
-Sonnet 5 accepts thinking disabled (no break there) but rejects `temperature`/`top_p`/`top_k` (`sampling_params: false` in `model_routing.json`, same family as Opus 5.x). The prior edition flagged four explicit-temperature call sites as certain 400s on a Sonnet-5 swap. Re-checked against the new `call_claude` (`sampling_params_ok` gate, §6.1):
+Sonnet 5 accepts thinking disabled, but only when the request says so: a request with no `thinking` field runs adaptive thinking on Sonnet 5 (Sonnet 4.6 ran it off). Thinking-off call sites therefore send `{"type": "disabled"}` via `StepConfig.thinking_kwargs()`. Sonnet 5 also rejects `temperature`/`top_p`/`top_k` (`sampling_params: false` in `model_routing.json`, same family as Opus 5.x). The prior edition flagged four explicit-temperature call sites as certain 400s on a Sonnet-5 swap. Re-checked against the new `call_claude` (`sampling_params_ok` gate, §6.1):
 
 - `personas/flows/shared/pass_7pre_chunked.py:84-91` (Stage 1 extract), `:128-135` (Stage 2 verify), `:267-274` (Stage 3 boddice check) — all three resolve via `step="personas.pass_7pre_extract"`/`"_verify"`/`"_boddice"`. **If `model_routing.json` repoints any of these steps at `claude-sonnet-5`, `call_claude` will see `cfg.sampling_params == False` and silently drop the explicit `temperature=0.0` before it reaches the API — no 400.** This is a real behavior change from the prior edition's prediction (was: certain break; now: silently safe, because the loader-plus-wrapper combination was specifically built to make this swap safe). Worth flagging as a discrepancy the reader should know about: the *2026-09-27* migration notes for this exact call site are now wrong, in the safe direction.
 - `personas/run_persona_pipeline.py:1591-1593` (`_pass_7c` Sonnet fallback, via `cfg.fallback`) — same protection: resolves through `step=`, so `sampling_params_ok` gates it.
--- a/personas/flows/shared/clients.py
+++ b/personas/flows/shared/clients.py
@@ -169,6 +169,11 @@
         # any given call. See `personas/flows/shared/clients.py` thinking_trace
         # field in the returned dict.
         kwargs["thinking"] = {"type": "adaptive", "display": "summarized"}
+    elif cfg is not None:
+        # Thinking off is sent explicitly: on Sonnet 5 and the Opus 5 line a
+        # request without `thinking` runs adaptive thinking. Raw model= calls
+        # (no step) keep the omission, since their model's rules are unknown.
+        kwargs["thinking"] = {"type": "disabled"}
 
     # Anthropic SDK refuses non-streaming for requests it estimates will take
     # >10 min. With max_tokens >= 16384 + adaptive thinking, the estimate
--- a/personas/flows/shared/model_routing.py
+++ b/personas/flows/shared/model_routing.py
@@ -3,7 +3,7 @@
 Reads `<repo>/model_routing.json`. Call sites ask for their step:
 
     cfg = step_config("runtime.researcher.extraction")
-    client.messages.stream(model=cfg.model, **({"thinking": ...} if cfg.thinking_on else {}),
+    client.messages.stream(model=cfg.model, **cfg.thinking_kwargs(),
                            **cfg.output_config_kwargs(), ...)
 
 Legacy per-step env vars (docs/LLM_CALL_INVENTORY.md §5) still override the
@@ -98,6 +98,20 @@
         """`{"output_config": {"effort": ...}}` when an effort is set, else {}."""
         return {"output_config": {"effort": self.effort}} if self.effort else {}
 
+    def thinking_kwargs(self) -> dict[str, Any]:
+        """The `thinking` request field for this step.
+
+        "off" is sent as `{"type": "disabled"}` rather than by leaving the
+        field out: on Sonnet 5 and the Opus 5 line, a request without
+        `thinking` runs adaptive thinking. Non-Anthropic and manual steps
+        get {}.
+        """
+        if self.thinking == "adaptive":
+            return {"thinking": {"type": "adaptive", "display": "summarized"}}
+        if self.thinking == "off":
+            return {"thinking": {"type": "disabled"}}
+        return {}
+
 
 def _env(name: str) -> str | None:
     value = os.environ.get(name, "").strip()
--- a/personas/tests/test_call_claude_config.py
+++ b/personas/tests/test_call_claude_config.py
@@ -61,7 +61,7 @@
     kwargs = client.messages.create.call_args.kwargs
     assert kwargs["model"] == "claude-sonnet-4-6"
     assert kwargs["temperature"] == 0.0
-    assert "thinking" not in kwargs
+    assert kwargs["thinking"] == {"type": "disabled"}
 
 
 def test_sampling_params_false_drops_temperature(tmp_path):
@@ -82,7 +82,7 @@
     kwargs = client.messages.create.call_args.kwargs
     assert kwargs["model"] == "claude-opus-4-7"
     assert "temperature" not in kwargs
-    assert "thinking" not in kwargs
+    assert kwargs["thinking"] == {"type": "disabled"}
 
 
 def test_effort_sent_as_output_config(tmp_path):
--- a/runtime/flows/editor/synthesis_router.py
+++ b/runtime/flows/editor/synthesis_router.py
@@ -129,10 +129,7 @@
 
     user_prompt = _build_user_prompt(voice_slug, artifact_text, candidates)
     cfg = step_config("runtime.synthesis_router")
-    thinking_kwargs = (
-        {"thinking": {"type": "adaptive", "display": "summarized"}}
-        if cfg.thinking_on else {}
-    )
+    thinking_kwargs = cfg.thinking_kwargs()
 
     try:
         message = client.messages.create(
--- a/runtime/flows/provocateur_flow.py
+++ b/runtime/flows/provocateur_flow.py
@@ -398,10 +398,7 @@
         ]
     else:
         system_arg = system
-    thinking_kwargs = (
-        {"thinking": {"type": "adaptive", "display": "summarized"}}
-        if cfg.thinking_on else {}
-    )
+    thinking_kwargs = cfg.thinking_kwargs()
     with client.messages.stream(
         model=cfg.model,
         max_tokens=max_tokens,
--- a/runtime/flows/researcher_flow.py
+++ b/runtime/flows/researcher_flow.py
@@ -107,8 +107,9 @@
 def _thinking_kwargs(cfg) -> dict:
     """Return the thinking kwargs for messages.create/stream when enabled.
 
-    When `cfg.thinking_on` is False, returns an empty dict so
-    `**_thinking_kwargs(cfg)` is a no-op on the API call. When enabled,
+    When thinking is off, returns an explicit `{"type": "disabled"}`
+    (on Sonnet 5 and the Opus 5 line a request without the field
+    thinks). When enabled,
     returns Opus 4.7's recommended 'adaptive' thinking mode — the model
     decides how much to think based on the task, which Anthropic's own
     testing shows outperforms fixed-budget 'enabled' mode.
@@ -122,9 +123,7 @@
     with `temperature` and `top_k` modifications — Opus 4.7 returns
     400 BadRequestError if `temperature` is set on a thinking call.
     """
-    if not cfg.thinking_on:
-        return {}
-    return {"thinking": {"type": "adaptive", "display": "summarized"}}
+    return cfg.thinking_kwargs()
 
 
 # --- Logger shim ----------------------------------------------------------
--- a/runtime/flows/shared/model_routing.py
+++ b/runtime/flows/shared/model_routing.py
@@ -3,7 +3,7 @@
 Reads `<repo>/model_routing.json`. Call sites ask for their step:
 
     cfg = step_config("runtime.researcher.extraction")
-    client.messages.stream(model=cfg.model, **({"thinking": ...} if cfg.thinking_on else {}),
+    client.messages.stream(model=cfg.model, **cfg.thinking_kwargs(),
                            **cfg.output_config_kwargs(), ...)
 
 Legacy per-step env vars (docs/LLM_CALL_INVENTORY.md §5) still override the
@@ -98,6 +98,20 @@
         """`{"output_config": {"effort": ...}}` when an effort is set, else {}."""
         return {"output_config": {"effort": self.effort}} if self.effort else {}
 
+    def thinking_kwargs(self) -> dict[str, Any]:
+        """The `thinking` request field for this step.
+
+        "off" is sent as `{"type": "disabled"}` rather than by leaving the
+        field out: on Sonnet 5 and the Opus 5 line, a request without
+        `thinking` runs adaptive thinking. Non-Anthropic and manual steps
+        get {}.
+        """
+        if self.thinking == "adaptive":
+            return {"thinking": {"type": "adaptive", "display": "summarized"}}
+        if self.thinking == "off":
+            return {"thinking": {"type": "disabled"}}
+        return {}
+
 
 def _env(name: str) -> str | None:
     value = os.environ.get(name, "").strip()
--- a/runtime/flows/transcription_flow.py
+++ b/runtime/flows/transcription_flow.py
@@ -562,10 +562,7 @@
     # wrote (per-session roster + transcript travel in user message). If the
     # system stays below the model's activation threshold, the breakpoint is
     # silently ignored — no penalty.
-    thinking_kwargs = (
-        {"thinking": {"type": "adaptive", "display": "summarized"}}
-        if cfg.thinking_on else {}
-    )
+    thinking_kwargs = cfg.thinking_kwargs()
     resp = client.messages.create(
         model=cfg.model,
         max_tokens=4096,
@@ -584,7 +581,8 @@
         f"  done in {time.time()-t0:.1f}s "
         f"(in={resp.usage.input_tokens}, out={resp.usage.output_tokens})"
     )
-    return extract_json(resp.content[0].text)
+    # Read text blocks by type: with thinking on, content[0] is a thinking block.
+    return extract_json("".join(b.text for b in resp.content if b.type == "text"))
 
 
 @task(
@@ -622,10 +620,7 @@
     # minimum, so this is mostly defensive: if the prompt grows past the
     # threshold later, caching kicks in automatically; if not, the breakpoint
     # is silently ignored).
-    thinking_kwargs = (
-        {"thinking": {"type": "adaptive", "display": "summarized"}}
-        if cfg.thinking_on else {}
-    )
+    thinking_kwargs = cfg.thinking_kwargs()
     chunks = []
     with client.messages.stream(
         model=cfg.model,
--- a/runtime/flows/voice/_anthropic_call.py
+++ b/runtime/flows/voice/_anthropic_call.py
@@ -20,11 +20,10 @@
 
 Model/thinking/effort resolution: callers pass a `StepConfig` (from
 `flows.shared.model_routing.step_config`) instead of raw `model` +
-`thinking_kwargs` values. This is the one place the "adaptive,
-display=summarized" thinking shape and `output_config_kwargs()` are
-applied for every Voice Step 1/2/3, Continuity, and Editor dossier
-call — callers no longer each carry their own `_thinking_kwargs()`
-copy (see docs/LLM_CALL_INVENTORY.md §2.4 preamble).
+`thinking_kwargs` values; `cfg.thinking_kwargs()` and
+`cfg.output_config_kwargs()` build the thinking and effort fields for
+every Voice Step 1/2/3, Continuity, and Editor dossier call (see
+docs/LLM_CALL_INVENTORY.md §2.4 preamble).
 """
 
 from __future__ import annotations
@@ -78,12 +77,12 @@
     Returns: (detailed_text, thinking_trace, final_message, thinking_tokens).
 
     `cfg` is the caller's `step_config("runtime.voice.step1")` (or
-    step2/step3/continuity/editor.dossier) — this function is the single
-    place that turns `cfg.thinking_on` into the `{"type": "adaptive",
-    "display": "summarized"}` payload (FU#60 canonical form: no
-    `temperature` key, since thinking is incompatible with temperature
-    modifications) and forwards `cfg.output_config_kwargs()` (a no-op
-    today since every step's effort is null).
+    step2/step3/continuity/editor.dossier). The thinking field comes from
+    `cfg.thinking_kwargs()` (adaptive with summarized display, or an
+    explicit disabled; FU#60 canonical form: no `temperature` key, since
+    thinking is incompatible with temperature modifications), and
+    `cfg.output_config_kwargs()` is forwarded (a no-op today since every
+    step's effort is null).
 
     `final_message` is the Anthropic Message object — caller can read
     `.usage.input_tokens / .output_tokens` for accounting (the SDK does
@@ -107,10 +106,7 @@
     acceptable.
     """
     model = cfg.model
-    thinking_kwargs: dict[str, Any] = (
-        {"thinking": {"type": "adaptive", "display": "summarized"}}
-        if cfg.thinking_on else {}
-    )
+    thinking_kwargs = cfg.thinking_kwargs()
     output_config_kwargs = cfg.output_config_kwargs()
     # Prompt caching on the system prompt. Two strategies:
     #   - tuple `(prefix, tail)`: place breakpoints on BOTH blocks (1h TTL)
--- a/runtime/flows/voice/step2_validation.py
+++ b/runtime/flows/voice/step2_validation.py
@@ -86,10 +86,7 @@
     cfg = step_config("runtime.voice.step2_validation")
     client = Anthropic()
     t0 = time.time()
-    thinking_kwargs = (
-        {"thinking": {"type": "adaptive", "display": "summarized"}}
-        if cfg.thinking_on else {}
-    )
+    thinking_kwargs = cfg.thinking_kwargs()
     resp = client.messages.create(
         model=cfg.model,
         max_tokens=STEP2_VALIDATION_MAX_TOKENS,
--- a/runtime/tests/test_model_routing.py
+++ b/runtime/tests/test_model_routing.py
@@ -241,3 +241,17 @@
     })
     with pytest.raises(mr.ModelRoutingError):
         mr.step_config("good", path=p)
+
+
+def test_thinking_kwargs_send_off_explicitly(tmp_path):
+    # Sonnet 5 and the Opus 5 line think when the field is absent, so "off"
+    # must go out as disabled, not as a missing field.
+    p = _config(tmp_path, {
+        "on": {"model": SONNET, "thinking": "adaptive", "effort": None},
+        "off": {"model": SONNET, "thinking": "off", "effort": None},
+        "ladder": {"model": "gpt-5.4", "ladder": ["gpt-5.4"]},
+    })
+    assert mr.step_config("on", path=p).thinking_kwargs() == {
+        "thinking": {"type": "adaptive", "display": "summarized"}}
+    assert mr.step_config("off", path=p).thinking_kwargs() == {"thinking": {"type": "disabled"}}
+    assert mr.step_config("ladder", path=p).thinking_kwargs() == {}
--- a/runtime/tests/test_model_routing_call_sites.py
+++ b/runtime/tests/test_model_routing_call_sites.py
@@ -244,7 +244,7 @@
 
         kwargs = client.messages.create.call_args.kwargs
         assert kwargs["model"] == expected_model
-        assert ("thinking" in kwargs) == (expected_thinking == "adaptive")
+        assert kwargs["thinking"]["type"] == ("adaptive" if expected_thinking == "adaptive" else "disabled")
 
     def test_env_override_changes_model(self, monkeypatch):
         client = _make_stream_client()
@@ -270,7 +270,7 @@
 
         kwargs = _stream_kwargs(client)
         assert kwargs["model"] == expected_model
-        assert ("thinking" in kwargs) == (expected_thinking == "adaptive")
+        assert kwargs["thinking"]["type"] == ("adaptive" if expected_thinking == "adaptive" else "disabled")
 
     def test_env_override_changes_model(self, monkeypatch):
         client = _make_stream_client("[]")
@@ -310,7 +310,7 @@
 
         kwargs = _stream_kwargs(client)
         assert kwargs["model"] == expected_model
-        assert ("thinking" in kwargs) == (expected_thinking == "adaptive")
+        assert kwargs["thinking"]["type"] == ("adaptive" if expected_thinking == "adaptive" else "disabled")
 
     def test_env_override_changes_model_and_thinking(self, tmp_path, monkeypatch):
         client = _make_stream_client("[]")
@@ -322,7 +322,7 @@
 
         kwargs = _stream_kwargs(client)
         assert kwargs["model"] == SONNET
-        assert "thinking" not in kwargs
+        assert kwargs["thinking"] == {"type": "disabled"}
 
 
 class TestResearcherClustering:
@@ -335,7 +335,7 @@
 
         kwargs = _stream_kwargs(client)
         assert kwargs["model"] == expected_model
-        assert ("thinking" in kwargs) == (expected_thinking == "adaptive")
+        assert kwargs["thinking"]["type"] == ("adaptive" if expected_thinking == "adaptive" else "disabled")
 
     def test_env_override_changes_model(self, monkeypatch):
         client = _make_stream_client('{"clusters": [], "isolates": []}')
@@ -357,7 +357,7 @@
 
         kwargs = _stream_kwargs(client)
         assert kwargs["model"] == expected_model
-        assert ("thinking" in kwargs) == (expected_thinking == "adaptive")
+        assert kwargs["thinking"]["type"] == ("adaptive" if expected_thinking == "adaptive" else "disabled")
 
     def test_env_override_changes_model(self, monkeypatch):
         client = _make_stream_client('{"themes": []}')
@@ -397,7 +397,7 @@
 
         kwargs = _stream_kwargs(client)
         assert kwargs["model"] == expected_model
-        assert ("thinking" in kwargs) == (expected_thinking == "adaptive")
+        assert kwargs["thinking"]["type"] == ("adaptive" if expected_thinking == "adaptive" else "disabled")
 
     def test_env_override_changes_model(self, monkeypatch):
         client = _make_stream_client("{}")
@@ -419,7 +419,7 @@
 
         kwargs = _stream_kwargs(client)
         assert kwargs["model"] == expected_model
-        assert ("thinking" in kwargs) == (expected_thinking == "adaptive")
+        assert kwargs["thinking"]["type"] == ("adaptive" if expected_thinking == "adaptive" else "disabled")
 
     def test_env_override_changes_model(self, monkeypatch):
         client = _make_stream_client("{}")
@@ -443,7 +443,7 @@
 
         kwargs = _stream_kwargs(client)
         assert kwargs["model"] == expected_model
-        assert ("thinking" in kwargs) == (expected_thinking == "adaptive")
+        assert kwargs["thinking"]["type"] == ("adaptive" if expected_thinking == "adaptive" else "disabled")
 
     def test_env_override_changes_model(self, monkeypatch):
         client = _make_stream_client("{}")
@@ -489,7 +489,7 @@
 
         kwargs = _stream_kwargs(client)
         assert kwargs["model"] == expected_model
-        assert ("thinking" in kwargs) == (expected_thinking == "adaptive")
+        assert kwargs["thinking"]["type"] == ("adaptive" if expected_thinking == "adaptive" else "disabled")
 
     def test_env_override_changes_model_and_thinking(self, tmp_path, monkeypatch):
         _write_card(tmp_path)
@@ -505,7 +505,7 @@
 
         kwargs = _stream_kwargs(client)
         assert kwargs["model"] == SONNET
-        assert "thinking" not in kwargs
+        assert kwargs["thinking"] == {"type": "disabled"}
 
 
 class TestVoiceStep2:
@@ -528,7 +528,7 @@
 
         kwargs = _stream_kwargs(client)
         assert kwargs["model"] == expected_model
-        assert ("thinking" in kwargs) == (expected_thinking == "adaptive")
+        assert kwargs["thinking"]["type"] == ("adaptive" if expected_thinking == "adaptive" else "disabled")
 
     def test_env_override_changes_model(self, tmp_path, monkeypatch):
         _write_card(tmp_path)
@@ -570,7 +570,7 @@
 
         kwargs = _stream_kwargs(client)
         assert kwargs["model"] == expected_model
-        assert ("thinking" in kwargs) == (expected_thinking == "adaptive")
+        assert kwargs["thinking"]["type"] == ("adaptive" if expected_thinking == "adaptive" else "disabled")
 
     def test_env_override_changes_model(self, tmp_path, monkeypatch):
         _write_card(tmp_path)
@@ -615,7 +615,7 @@
 
         kwargs = _stream_kwargs(client)
         assert kwargs["model"] == expected_model
-        assert ("thinking" in kwargs) == (expected_thinking == "adaptive")
+        assert kwargs["thinking"]["type"] == ("adaptive" if expected_thinking == "adaptive" else "disabled")
 
     def test_env_override_changes_model(self, tmp_path, monkeypatch):
         run_dir = self._run_dir_with_step2(tmp_path)
@@ -662,7 +662,7 @@
 
         kwargs = _stream_kwargs(client)
         assert kwargs["model"] == expected_model
-        assert ("thinking" in kwargs) == (expected_thinking == "adaptive")
+        assert kwargs["thinking"]["type"] == ("adaptive" if expected_thinking == "adaptive" else "disabled")
 
     def test_env_override_changes_model(self, tmp_path, monkeypatch):
         run_dir = self._run_dir_with_briefing(tmp_path)
@@ -780,7 +780,7 @@
 
         kwargs = fake_client.messages.create.call_args.kwargs
         assert kwargs["model"] == expected_model
-        assert ("thinking" in kwargs) == (expected_thinking == "adaptive")
+        assert kwargs["thinking"]["type"] == ("adaptive" if expected_thinking == "adaptive" else "disabled")
 
     def test_env_override_changes_model(self, monkeypatch):
         fake_client = MagicMock()
@@ -819,7 +819,7 @@
         assert chosen == "theme_001"
         kwargs = client.messages.create.call_args.kwargs
         assert kwargs["model"] == expected_model
-        assert ("thinking" in kwargs) == (expected_thinking == "adaptive")
+        assert kwargs["thinking"]["type"] == ("adaptive" if expected_thinking == "adaptive" else "disabled")
 
     def test_env_override_changes_model(self, monkeypatch):
         client = MagicMock()
--- a/runtime/tests/test_transcription_speaker_id_fallback.py
+++ b/runtime/tests/test_transcription_speaker_id_fallback.py
@@ -41,7 +41,7 @@
     resp = MagicMock()
     resp.usage = MagicMock(input_tokens=1200, output_tokens=900)
     # Deliberately unparseable — no closing brace, trailing garbage.
-    resp.content = [MagicMock(text='{"mappings": [ this is not valid json')]
+    resp.content = [MagicMock(type="text", text='{"mappings": [ this is not valid json')]
     return resp
 
 
````

### F2. Detect refusals at every Anthropic call site and don't retry them (needs F1 first)

`F2_refusal_handling.patch`

````diff
--- a/personas/flows/shared/clients.py
+++ b/personas/flows/shared/clients.py
@@ -76,6 +76,11 @@
 
 
 # --- Anthropic / Claude --------------------------------------------------
+
+class ClaudeRefusal(RuntimeError):
+    """A safety classifier or the model declined the request: HTTP 200,
+    stop_reason "refusal", empty or partial content. Not a JSON problem."""
+
 
 def call_claude(
     *,
@@ -269,6 +274,17 @@
             "model": model,
             "stop_reason": msg.stop_reason,
         }
+    if out.get("stop_reason") == "refusal":
+        # Record first: a mid-stream refusal is billed for what it streamed.
+        out["_wall_seconds"] = time.time() - _t0
+        _record(slug, pass_name, "anthropic", out["model"], out["usage"],
+                out["_wall_seconds"], project_root)
+        details = getattr(final if use_streaming else msg, "stop_details", None)
+        raise ClaudeRefusal(
+            f"{model} declined the request (stop_reason=refusal, "
+            f"category={getattr(details, 'category', None)!r}); "
+            f"any partial output is discarded."
+        )
     # FU#9 2026-04-24: proactive max_tokens monitoring. `stop_reason == "max_tokens"`
     # means output was truncated. If JSON parsing fails we raise immediately
     # (existing behaviour below); if JSON happens to parse (rare — usually
--- a/personas/tests/test_call_claude_config.py
+++ b/personas/tests/test_call_claude_config.py
@@ -116,3 +116,20 @@
 def test_neither_step_nor_model_raises():
     with pytest.raises(ValueError):
         call_claude(system="sys", user="usr")
+
+
+def test_refusal_raises_instead_of_parsing(tmp_path):
+    """A declined request raises ClaudeRefusal, not an 'invalid JSON' error."""
+    from flows.shared.clients import ClaudeRefusal
+    cfg_path = _write_config(tmp_path, {
+        "s": {"model": "claude-sonnet-4-6", "thinking": "off", "effort": None},
+    })
+    cfg = mr.step_config("s", path=cfg_path)
+    client = _mock_client_for_create(text="")
+    client.messages.create.return_value.stop_reason = "refusal"
+    client.messages.create.return_value.stop_details = SimpleNamespace(
+        category="cyber", explanation=None)
+    with patch("anthropic.Anthropic", return_value=client):
+        with pytest.raises(ClaudeRefusal):
+            call_claude(step=cfg, system="sys", user="usr", max_tokens=100,
+                        response_format_json=True)
--- a/runtime/flows/editor/synthesis_router.py
+++ b/runtime/flows/editor/synthesis_router.py
@@ -148,6 +148,11 @@
         )
         return (fallback_id, f"synthesis-router fallback (API error): {type(exc).__name__}")
 
+    if getattr(message, "stop_reason", None) == "refusal":
+        log.warning(f"synthesis_router({voice_slug}): request declined; "
+                    f"falling back to lowest-numbered={fallback_id}")
+        return (fallback_id, "synthesis-router fallback (refusal)")
+
     try:
         text = "".join(
             getattr(b, "text", "") for b in (message.content or [])
--- a/runtime/flows/provocateur_flow.py
+++ b/runtime/flows/provocateur_flow.py
@@ -103,6 +103,7 @@
     member_slug,
     write_json_atomic,
 )
+from flows.shared.anthropic_checks import raise_if_refused, retry_unless_refused
 from flows.shared.model_routing import StepConfig, step_config
 
 
@@ -421,6 +422,8 @@
         f"stop={stop_reason})"
     )
 
+    raise_if_refused(final, task_label)
+
     if usage.output_tokens > max_tokens * 0.8:
         logger.warning(
             f"  {task_label} used {usage.output_tokens}/{max_tokens} "
@@ -493,6 +496,7 @@
 @task(
     name="provocateur-triage-voice",
     retries=5,
+    retry_condition_fn=retry_unless_refused,
     retry_delay_seconds=exponential_backoff(backoff_factor=15),
 )
 def triage_voice(
@@ -570,6 +574,7 @@
 @task(
     name="provocateur-triage-flags",
     retries=5,
+    retry_condition_fn=retry_unless_refused,
     retry_delay_seconds=exponential_backoff(backoff_factor=15),
 )
 def triage_flags(themes: list[dict], council: dict) -> dict:
@@ -1073,6 +1078,7 @@
 @task(
     name="provocateur-formulate",
     retries=5,
+    retry_condition_fn=retry_unless_refused,
     retry_delay_seconds=exponential_backoff(backoff_factor=15),
 )
 def formulate_for_member(
--- a/runtime/flows/researcher_flow.py
+++ b/runtime/flows/researcher_flow.py
@@ -54,6 +54,7 @@
         write_json_atomic,
     )
     from flows.shared.model_routing import step_config
+    from flows.shared.anthropic_checks import raise_if_refused, retry_unless_refused
 except ImportError as e:
     sys.stderr.write(
         f"Missing dependency: {e.name}\n"
@@ -260,6 +261,7 @@
 @task(
     name="researcher-extract",
     retries=2,
+    retry_condition_fn=retry_unless_refused,
     retry_delay_seconds=exponential_backoff(backoff_factor=5),
 )
 def extract_session(session_package_path: str) -> dict:
@@ -310,6 +312,7 @@
         for text in stream.text_stream:
             chunks.append(text)
         final = stream.get_final_message()
+    raise_if_refused(final, cfg.step)
     full_text = "".join(chunks)
     logger.info(
         f"  done in {time.time()-t0:.1f}s "
@@ -337,6 +340,7 @@
 @task(
     name="researcher-cluster",
     retries=2,
+    retry_condition_fn=retry_unless_refused,
     retry_delay_seconds=exponential_backoff(backoff_factor=5),
 )
 def cluster_extractions(all_extractions: list) -> dict:
@@ -410,6 +414,7 @@
         for text in stream.text_stream:
             chunks.append(text)
         final = stream.get_final_message()
+    raise_if_refused(final, cfg.step)
     full_text = "".join(chunks)
     logger.info(
         f"  done in {time.time()-t0:.1f}s "
@@ -468,6 +473,7 @@
 @task(
     name="researcher-theme",
     retries=2,
+    retry_condition_fn=retry_unless_refused,
     retry_delay_seconds=exponential_backoff(backoff_factor=5),
 )
 def group_clusters_into_themes(clusters_result: dict) -> dict:
@@ -529,6 +535,7 @@
         for text in stream.text_stream:
             chunks.append(text)
         final = stream.get_final_message()
+    raise_if_refused(final, cfg.step)
     full_text = "".join(chunks)
     logger.info(
         f"  done in {time.time()-t0:.1f}s "
--- /dev/null
+++ b/runtime/flows/shared/anthropic_checks.py
@@ -0,0 +1,45 @@
+"""Checks every runtime Anthropic call site applies to a response.
+
+A declined request comes back as HTTP 200 with `stop_reason == "refusal"`
+and empty content (or, mid-stream, partial content). It must not be read
+as a normal reply. Opus 4.7 already runs cybersecurity safeguards; Sonnet 5
+and the Opus 5 line run more classifiers (Opus 5.5 adds bio and
+reasoning-extraction).
+"""
+from __future__ import annotations
+
+from typing import Any
+
+
+class RefusalError(RuntimeError):
+    """The model or a safety classifier declined the request."""
+
+    def __init__(self, label: str, message: Any) -> None:
+        details = getattr(message, "stop_details", None)
+        self.category = getattr(details, "category", None)
+        self.explanation = getattr(details, "explanation", None)
+        super().__init__(
+            f"{label}: request declined (stop_reason=refusal, "
+            f"category={self.category!r}); any partial output is discarded."
+        )
+
+
+def raise_if_refused(message: Any, label: str) -> None:
+    """Raise RefusalError when `message` is a refusal; otherwise do nothing."""
+    if getattr(message, "stop_reason", None) == "refusal":
+        raise RefusalError(label, message)
+
+
+def retry_unless_refused(task: Any, task_run: Any, state: Any) -> bool:
+    """Prefect `retry_condition_fn`: retry any failure except a refusal.
+
+    The same request is declined again, and a mid-stream refusal re-bills
+    the streamed output on every attempt.
+    """
+    try:
+        state.result()
+    except RefusalError:
+        return False
+    except Exception:  # noqa: BLE001 — every other failure keeps its retry policy
+        return True
+    return True
--- a/runtime/flows/transcription_flow.py
+++ b/runtime/flows/transcription_flow.py
@@ -56,6 +56,7 @@
     load_dotenv(_REPO_ROOT.parent / ".env", override=True)
     from flows.shared.io import load_prompt, get_logger, extract_json, write_json_atomic
     from flows.shared.model_routing import step_config
+    from flows.shared.anthropic_checks import raise_if_refused, retry_unless_refused
 except ImportError as e:
     sys.stderr.write(
         f"Missing dependency: {e.name}\n"
@@ -508,6 +509,7 @@
 @task(
     name="identify-speakers",
     retries=2,
+    retry_condition_fn=retry_unless_refused,
     retry_delay_seconds=exponential_backoff(backoff_factor=5),
 )
 def identify_speakers(turns, session):
@@ -581,6 +583,7 @@
         f"  done in {time.time()-t0:.1f}s "
         f"(in={resp.usage.input_tokens}, out={resp.usage.output_tokens})"
     )
+    raise_if_refused(resp, "runtime.transcription.speaker_id")
     # Read text blocks by type: with thinking on, content[0] is a thinking block.
     return extract_json("".join(b.text for b in resp.content if b.type == "text"))
 
@@ -588,6 +591,7 @@
 @task(
     name="clean-transcript",
     retries=2,
+    retry_condition_fn=retry_unless_refused,
     retry_delay_seconds=exponential_backoff(backoff_factor=5),
 )
 def clean_transcript(named_turns, session, vocabulary):
@@ -639,6 +643,7 @@
         for text in stream.text_stream:
             chunks.append(text)
         final = stream.get_final_message()
+    raise_if_refused(final, "runtime.transcription.cleaning")
     full_text = "".join(chunks)
     logger.info(
         f"  done in {time.time()-t0:.1f}s "
--- a/runtime/flows/voice/_anthropic_call.py
+++ b/runtime/flows/voice/_anthropic_call.py
@@ -32,6 +32,7 @@
 import time
 from typing import Any
 
+from flows.shared.anthropic_checks import RefusalError, raise_if_refused
 from flows.shared.model_routing import StepConfig
 
 
@@ -94,6 +95,8 @@
       - First attempt streams normally.
       - On any exception (network, rate limit, 5xx, JSON parse failure
         in the SDK), waits `retry_backoff_s` seconds and retries once.
+      - A refusal (`stop_reason == "refusal"`) raises `RefusalError` at
+        once, without the retry: the same request would be declined again.
       - If the retry also fails, re-raises the second exception. The
         orchestrator handles the failure (logs, skips the pair/voice,
         adds to manifest).
@@ -154,6 +157,7 @@
                 for _ in stream.text_stream:
                     pass  # consume; final assembly via final.content below
                 final = stream.get_final_message()
+            raise_if_refused(final, cfg.step)
             text_parts: list[str] = []
             thinking_parts: list[str] = []
             for block in final.content:
@@ -172,6 +176,8 @@
                 final,
                 thinking_tokens,
             )
+        except RefusalError:
+            raise
         except Exception as e:  # noqa: BLE001 — retry is intentional
             last_err = e
             if attempt == 0:
--- a/runtime/flows/voice/step2_validation.py
+++ b/runtime/flows/voice/step2_validation.py
@@ -46,6 +46,7 @@
 if str(_REPO_ROOT) not in sys.path:
     sys.path.insert(0, str(_REPO_ROOT))
 
+from flows.shared.anthropic_checks import raise_if_refused
 from flows.shared.io import get_logger, load_prompt, write_json_atomic
 from flows.shared.model_routing import step_config
 
@@ -95,6 +96,7 @@
         **thinking_kwargs,
         **cfg.output_config_kwargs(),
     )
+    raise_if_refused(resp, cfg.step)
     text_chunks = [b.text for b in resp.content if hasattr(b, "text")]
     return {
         "text": "".join(text_chunks),
--- /dev/null
+++ b/runtime/tests/test_anthropic_checks.py
@@ -0,0 +1,99 @@
+"""Refusal handling: a declined request raises instead of passing as a reply."""
+from __future__ import annotations
+
+import sys
+from pathlib import Path
+from types import SimpleNamespace
+from unittest.mock import MagicMock
+
+import pytest
+
+_RUNTIME = Path(__file__).resolve().parent.parent
+sys.path.insert(0, str(_RUNTIME))
+
+from flows.shared.anthropic_checks import (  # noqa: E402
+    RefusalError,
+    raise_if_refused,
+    retry_unless_refused,
+)
+from flows.shared.model_routing import step_config  # noqa: E402
+from flows.voice import _anthropic_call  # noqa: E402
+
+
+def _message(stop_reason, category=None):
+    details = (SimpleNamespace(type="refusal", category=category, explanation=None)
+               if stop_reason == "refusal" else None)
+    return SimpleNamespace(stop_reason=stop_reason, stop_details=details, content=[],
+                           usage=SimpleNamespace(input_tokens=1, output_tokens=0))
+
+
+def test_end_turn_passes():
+    raise_if_refused(_message("end_turn"), "x")
+
+
+def test_refusal_raises_with_category():
+    with pytest.raises(RefusalError) as exc:
+        raise_if_refused(_message("refusal", "cyber"), "runtime.voice.step1")
+    assert exc.value.category == "cyber"
+
+
+def test_stream_voice_call_does_not_retry_a_refusal(monkeypatch):
+    monkeypatch.setattr(_anthropic_call.time, "sleep", lambda s: None)
+    stream = MagicMock()
+    stream.__enter__.return_value = stream
+    stream.__exit__.return_value = False
+    stream.text_stream = iter(())
+    stream.get_final_message.return_value = _message("refusal", "bio")
+    client = MagicMock()
+    client.messages.stream.return_value = stream
+    with pytest.raises(RefusalError):
+        _anthropic_call.stream_voice_call(
+            client, cfg=step_config("runtime.voice.step1"), max_tokens=100,
+            system="s", user="u",
+        )
+    assert client.messages.stream.call_count == 1
+
+
+class _State:
+    def __init__(self, exc):
+        self.exc = exc
+
+    def result(self):
+        raise self.exc
+
+
+def test_prefect_retries_skip_refusals_only():
+    assert retry_unless_refused(None, None, _State(RefusalError("x", _message("refusal")))) is False
+    assert retry_unless_refused(None, None, _State(ValueError("boom"))) is True
+
+
+def test_prefect_runs_a_refused_task_once():
+    from prefect import task
+
+    calls = {"refused": 0, "other": 0}
+
+    @task(retries=2, retry_delay_seconds=0, retry_condition_fn=retry_unless_refused)
+    def refused():
+        calls["refused"] += 1
+        raise RefusalError("x", _message("refusal"))
+
+    @task(retries=2, retry_delay_seconds=0, retry_condition_fn=retry_unless_refused)
+    def other():
+        calls["other"] += 1
+        raise ValueError("boom")
+
+    assert refused(return_state=True).is_failed()
+    assert other(return_state=True).is_failed()
+    assert calls == {"refused": 1, "other": 3}
+
+
+def test_prefect_tasks_use_the_retry_condition():
+    from flows import provocateur_flow, researcher_flow, transcription_flow
+    tasks = [
+        transcription_flow.identify_speakers, transcription_flow.clean_transcript,
+        researcher_flow.extract_session, researcher_flow.cluster_extractions,
+        researcher_flow.group_clusters_into_themes,
+        provocateur_flow.triage_voice, provocateur_flow.triage_flags,
+        provocateur_flow.formulate_for_member,
+    ]
+    assert all(t.retry_condition_fn is retry_unless_refused for t in tasks)
````

### F3. Render Derive, 7a-FIX and the 7a validator prompt so their developer headers stay out of the prompt

`F3_raw_loaded_headers.patch`

````diff
--- a/personas/run_persona_pipeline.py
+++ b/personas/run_persona_pipeline.py
@@ -924,7 +924,7 @@
         }
         full_card_for_derive = {k: v for k, v in assembled.items()
                                 if k not in EXCLUDE_FROM_DERIVE}
-        sysp = load_prompt("persona_derive")
+        sysp = render("persona_derive")
         userp = render("persona_derive_user",
                        persona_card_json=json.dumps(full_card_for_derive,
                                                     ensure_ascii=False, indent=2))
@@ -1093,7 +1093,7 @@
     full_card_for_validate = {**combined_2_3_4, **pass5["fields"]}
     if pass6.get("fields"):
         full_card_for_validate.update(pass6["fields"])
-    sysp = load_prompt("persona_pass_7a_cross_model")
+    sysp = render("persona_pass_7a_cross_model")
     userp = render("persona_pass_7a_cross_model_user",
                    persona_card_json=json.dumps(full_card_for_validate, ensure_ascii=False, indent=2))
     # 2026-04-23: ladder updated — gpt-5.4 primary with reasoning_effort=high
@@ -1368,7 +1368,7 @@
         "knowledge_boundary": pass2["fields"].get("knowledge_boundary", ""),
     }
 
-    sysp = load_prompt("persona_pass_7a_fix")
+    sysp = render("persona_pass_7a_fix")
     userp = render(
         "persona_pass_7a_fix_user",
         field_issues_json=json.dumps(field_issues, ensure_ascii=False, indent=2),
@@ -1930,7 +1930,7 @@
         "continuity_block_if_night_2", "continuity_block_artifact_if_night_2",
     }
     full_card_for_validate = {k: v for k, v in assembled.items() if k not in EXCLUDE}
-    sysp = load_prompt("persona_pass_7a_cross_model")
+    sysp = render("persona_pass_7a_cross_model")
     userp = render("persona_pass_7a_cross_model_user",
                    persona_card_json=json.dumps(full_card_for_validate,
                                                  ensure_ascii=False, indent=2))
@@ -2010,7 +2010,7 @@
     }
     full_card_for_derive = {k: v for k, v in assembled.items()
                             if k not in EXCLUDE_FROM_DERIVE}
-    sysp = load_prompt("persona_derive")
+    sysp = render("persona_derive")
     userp = render("persona_derive_user",
                    persona_card_json=json.dumps(full_card_for_derive, ensure_ascii=False, indent=2))
     # 2026-04-23: model upgraded claude-sonnet-4-6 → claude-opus-4-7 + thinking
--- /dev/null
+++ b/personas/tests/test_raw_prompt_headers.py
@@ -0,0 +1,28 @@
+"""Developer headers ({# ... #}) in these prompts must not reach the model."""
+from __future__ import annotations
+
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
+
+_NAMES = ["persona_derive", "persona_pass_7a_fix", "persona_pass_7a_cross_model"]
+
+
+@pytest.mark.parametrize("name", _NAMES)
+def test_header_is_stripped(name):
+    text = render(name)
+    assert "{#" not in text and "#}" not in text
+    assert text.lstrip().startswith("You are")
+
+
+def test_pipeline_renders_these_prompts():
+    src = (_PERSONAS_ROOT / "run_persona_pipeline.py").read_text(encoding="utf-8")
+    for name in _NAMES:
+        assert f'load_prompt("{name}")' not in src
````

### F4. Derive validator verdicts in code, with a threshold rule for voice fidelity

`F4_validator_verdict_in_code.patch`

````diff
--- a/runtime/flows/shared/prompts/voice_step2_validation_cross_night_echo.md
+++ b/runtime/flows/shared/prompts/voice_step2_validation_cross_night_echo.md
@@ -32,7 +32,6 @@
 
 ```json
 {
-  "verdict": "PASS" | "WARN" | "HOLD",
   "echo_level": "none" | "mild" | "moderate" | "heavy",
   "shared_argument": null,
   "shared_claims": [],
@@ -46,9 +45,4 @@
 - `continuity_overlay_addressed`: true/false if overlay was given and you can judge; null if no overlay was given
 - `why`: one-paragraph explanation
 
-Compute `verdict`:
-- HOLD if `echo_level == "heavy"`
-- WARN if `echo_level == "moderate"`, OR if continuity_overlay was given and clearly not addressed
-- PASS if `echo_level == "none"` or `"mild"`
-
 Be discerning: voices SHOULD have continuity of vocabulary and form. The check is about progression of thought, not vocabulary novelty.
--- a/runtime/flows/shared/prompts/voice_step2_validation_engagement.md
+++ b/runtime/flows/shared/prompts/voice_step2_validation_engagement.md
@@ -43,7 +43,6 @@
 
 ```json
 {
-  "verdict": "PASS" | "WARN",
   "form_fidelity": null,
   "grounding_fidelity": null
 }
@@ -51,10 +50,6 @@
 
 Populate `form_fidelity` and `grounding_fidelity` as objects (per shapes above) ONLY if a real failure is found, otherwise leave as `null`.
 
-Compute `verdict`:
-- WARN if either field is non-null
-- PASS otherwise
-
 (Length compliance is checked mechanically by the orchestrator, not by you — don't worry about word count.)
 
 Be discerning, not picky: form fidelity is about visible structural delivery, not subtle textural matters; grounding fidelity is about "is this tonight's panel?" not "did the voice cite every extraction." A voice with strong central engagement on 2-3 panel claims has fine grounding even if it doesn't reference every extraction_id.
--- a/runtime/flows/shared/prompts/voice_step2_validation_safeguards.md
+++ b/runtime/flows/shared/prompts/voice_step2_validation_safeguards.md
@@ -30,7 +30,6 @@
 
 ```json
 {
-  "verdict": "PASS" | "WARN" | "HOLD",
   "ai_self_acknowledgment": null,
   "defamation_risk": null,
   "topics_requiring_care_breach": null,
@@ -45,9 +44,4 @@
 
 For WARN-tier lists (`hard_limits_breach`, `banned_modes_slip`, `banned_language_ai_slop`, `first_person_presence_leak`), append objects `{"text": "<quoted span>", "rule_cited": "<which card field + which item>"}` for each instance found.
 
-Compute `verdict`:
-- HOLD if any of `ai_self_acknowledgment`, `defamation_risk`, `topics_requiring_care_breach` is non-null
-- WARN if any of the WARN-tier lists is non-empty
-- PASS otherwise
-
 Be strict on HOLD-tier rules; be discerning on WARN-tier (only flag clear violations, not mild stylistic shadings).
--- a/runtime/flows/shared/prompts/voice_step2_validation_voice_fidelity.md
+++ b/runtime/flows/shared/prompts/voice_step2_validation_voice_fidelity.md
@@ -6,7 +6,7 @@
 
 **1. Characteristic moves performed**
 
-The user message includes the voice's `characteristic_moves` — a list of signature moves the voice MUST perform in its artifact (e.g. Dostoevsky "moves into a remembered face", Battuta "anchors at a halt with a place named", Hannah Arendt "etymological doublet → single sentence → reformulated question", Plato "starts with a definitional question, then diairesis").
+The user message includes the voice's `characteristic_moves` — the voice's repertoire of signature moves; an artifact performs some of them, not all (e.g. Dostoevsky "moves into a remembered face", Battuta "anchors at a halt with a place named", Hannah Arendt "etymological doublet → single sentence → reformulated question", Plato "starts with a definitional question, then diairesis").
 
 For each move on the list, check whether the artifact actually performed it. Note that move performance is observable in the text — you should be able to point to where the move happens (a paragraph, a sentence, a structural beat).
 
@@ -22,7 +22,6 @@
 
 ```json
 {
-  "verdict": "PASS" | "WARN",
   "characteristic_moves_performed": [
     {"move": "<short summary of the move>", "performed": true | false, "where": "<paragraph/section, or null if not performed>"}
   ],
@@ -34,8 +33,4 @@
 
 For each item in the input lists, append one entry to the corresponding result list. If a move/criterion is too abstract to operationalize against the artifact, mark `performed: true` / `passed: true` with a note in `where`/`why` rather than failing it.
 
-Compute `verdict`:
-- WARN if any `performed: false` OR any `passed: false`
-- PASS otherwise
-
-Be discerning: a voice that performed 4/5 moves with 1 weak performance is PASS (the move was attempted); a voice that omitted a move entirely is WARN. Same for criteria — partial pass with substantive engagement is PASS; clear miss is WARN.
+Mark a move `performed: true` when the artifact attempts it, even weakly, and `false` only when it is absent. Mark a criterion `passed: true` for a partial pass with substantive engagement, and `false` for a clear miss.
--- a/runtime/flows/voice/step2_validation.py
+++ b/runtime/flows/voice/step2_validation.py
@@ -128,6 +128,57 @@
     return json.dumps(value, indent=2, ensure_ascii=False)
 
 
+# Voice fidelity warns when fewer moves than this show in the artifact. Two is
+# the cards' own bar (Plato's quality criterion: "at least two of my
+# characteristic_moves operate visibly"); operator-tunable.
+_MIN_MOVES_PERFORMED = 2
+
+
+def _derive_verdict(pillar: str, parsed: dict[str, Any]) -> str:
+    """PASS / WARN / HOLD for one pillar, from the fields the model filled.
+
+    The model makes the judgments (which spans break which rule, which moves
+    were performed); the verdict is a fixed rule over those fields, so it is
+    computed here and not asked of the model.
+    """
+    if pillar == "safeguards":
+        if any(parsed.get(k) for k in (
+            "ai_self_acknowledgment", "defamation_risk", "topics_requiring_care_breach",
+        )):
+            return "HOLD"
+        if any(parsed.get(k) for k in (
+            "hard_limits_breach", "banned_modes_slip",
+            "banned_language_ai_slop", "first_person_presence_leak",
+        )):
+            return "WARN"
+        return "PASS"
+    if pillar == "engagement":
+        if any(parsed.get(k) for k in ("form_fidelity", "grounding_fidelity", "length_compliance")):
+            return "WARN"
+        return "PASS"
+    if pillar == "voice_fidelity":
+        # The cards list 8-13 moves (schema: 3-5), a repertoire no single piece
+        # performs in full, so a missed move alone doesn't warn. Warn on a
+        # failed quality criterion (the voice's own tests), or when fewer than
+        # _MIN_MOVES_PERFORMED moves show at all.
+        moves = [m for m in parsed.get("characteristic_moves_performed") or [] if isinstance(m, dict)]
+        criteria = parsed.get("quality_criteria_results") or []
+        performed = sum(1 for m in moves if m.get("performed") is True)
+        if any(isinstance(c, dict) and c.get("passed") is False for c in criteria):
+            return "WARN"
+        if performed < min(_MIN_MOVES_PERFORMED, len(moves)):
+            return "WARN"
+        return "PASS"
+    if pillar == "cross_night_echo":
+        level = parsed.get("echo_level")
+        if level == "heavy":
+            return "HOLD"
+        if level == "moderate" or parsed.get("continuity_overlay_addressed") is False:
+            return "WARN"
+        return "PASS"
+    raise ValueError(f"unknown pillar {pillar!r}")
+
+
 # --- Pillar 1: Safeguards ----------------------------------------------
 
 def check_safeguards(
@@ -177,6 +228,7 @@
         "output_tokens": call["output_tokens"],
         "wall_clock_s": call["wall_clock_s"],
     }
+    parsed["verdict"] = _derive_verdict("safeguards", parsed)
     return parsed
 
 
@@ -268,14 +320,13 @@
     # Overlay mechanical length check (no LLM cost).
     length_issue = _check_length_compliance(artifact_text, card)
     parsed["length_compliance"] = length_issue
-    if length_issue and parsed.get("verdict") == "PASS":
-        parsed["verdict"] = "WARN"
     parsed["_call"] = {
         "model": call["model"],
         "input_tokens": call["input_tokens"],
         "output_tokens": call["output_tokens"],
         "wall_clock_s": call["wall_clock_s"],
     }
+    parsed["verdict"] = _derive_verdict("engagement", parsed)
     return parsed
 
 
@@ -288,12 +339,12 @@
     """Voice fidelity pillar — did the voice deliver what its card promised?
 
     Per-voice card fields:
-      - characteristic_moves — signature moves the voice MUST perform
+      - characteristic_moves — the voice's repertoire of signature moves
       - quality_criteria — voice's own per-step pass/fail tests
     """
     system = load_prompt("voice_step2_validation_voice_fidelity")
     user = (
-        f"### characteristic_moves (signature moves the voice MUST perform)\n"
+        f"### characteristic_moves (the voice's repertoire of signature moves)\n"
         f"{_render_field(card.get('characteristic_moves'))}\n\n"
         f"### quality_criteria (voice's self-imposed pass/fail tests)\n"
         f"{_render_field(card.get('quality_criteria'))}\n\n"
@@ -308,6 +359,7 @@
         "output_tokens": call["output_tokens"],
         "wall_clock_s": call["wall_clock_s"],
     }
+    parsed["verdict"] = _derive_verdict("voice_fidelity", parsed)
     return parsed
 
 
@@ -348,6 +400,7 @@
         "output_tokens": call["output_tokens"],
         "wall_clock_s": call["wall_clock_s"],
     }
+    parsed["verdict"] = _derive_verdict("cross_night_echo", parsed)
     return parsed
 
 
--- a/runtime/tests/test_step2_validation.py
+++ b/runtime/tests/test_step2_validation.py
@@ -20,6 +20,7 @@
 from flows.voice.step2_validation import (  # noqa: E402
     _AI_SLOP_LEXICON,
     _check_length_compliance,
+    _derive_verdict,
     _load_prior_artifact,
     _overall_verdict,
     run_step2_validation,
@@ -364,3 +365,49 @@
         }))
         held = _load_held_voices(tmp_path)
         assert held == {"plato"}
+
+
+# --- Pillar verdicts are derived from the fields, not taken from the model --
+
+class TestDeriveVerdict:
+    def test_safeguards_tiers(self):
+        assert _derive_verdict("safeguards", {"defamation_risk": {"text": "x", "why": "y"}}) == "HOLD"
+        assert _derive_verdict("safeguards", {"banned_modes_slip": [{"text": "x"}]}) == "WARN"
+        assert _derive_verdict("safeguards", {"hard_limits_breach": []}) == "PASS"
+
+    def test_engagement_length_only_warns(self):
+        assert _derive_verdict("engagement", {"length_compliance": {"verdict": "over"}}) == "WARN"
+        assert _derive_verdict("engagement", {"form_fidelity": None, "grounding_fidelity": None}) == "PASS"
+
+    def test_voice_fidelity_threshold(self):
+        moves = [{"move": "a", "performed": True}, {"move": "b", "performed": True},
+                 {"move": "The longer way", "performed": False}]
+        ok = [{"criterion": "c", "passed": True}]
+        # A missed move alone is fine once two moves show (Athens N1 Plato shape).
+        assert _derive_verdict("voice_fidelity", {
+            "characteristic_moves_performed": moves, "quality_criteria_results": ok}) == "PASS"
+        # A failed criterion warns even if the model said PASS (Athens N3 Battuta shape).
+        assert _derive_verdict("voice_fidelity", {
+            "verdict": "PASS", "characteristic_moves_performed": moves,
+            "quality_criteria_results": [{"criterion": "c", "passed": False}]}) == "WARN"
+        # Fewer than two moves showing warns.
+        assert _derive_verdict("voice_fidelity", {
+            "characteristic_moves_performed": moves[1:], "quality_criteria_results": ok}) == "WARN"
+
+    def test_cross_night_echo(self):
+        assert _derive_verdict("cross_night_echo", {"echo_level": "heavy"}) == "HOLD"
+        assert _derive_verdict("cross_night_echo",
+                               {"echo_level": "mild", "continuity_overlay_addressed": False}) == "WARN"
+        assert _derive_verdict("cross_night_echo",
+                               {"echo_level": "mild", "continuity_overlay_addressed": None}) == "PASS"
+
+    def test_check_voice_fidelity_overrides_model_verdict(self):
+        from flows.voice import step2_validation as sv
+        text = json.dumps({"verdict": "PASS", "characteristic_moves_performed": [
+            {"move": "m", "performed": True, "where": "p1"},
+            {"move": "n", "performed": True, "where": "p2"}],
+            "quality_criteria_results": [{"criterion": "c", "passed": False, "why": "x"}]})
+        with patch.object(sv, "_call_anthropic", return_value={
+                "text": text, "model": "m", "input_tokens": 1, "output_tokens": 1,
+                "wall_clock_s": 0}):
+            assert sv.check_voice_fidelity("artifact", {})["verdict"] == "WARN"
````

### F5. Researcher: state closure once, drop the count-and-fix step

`F5_researcher_self_count.patch`

````diff
--- a/runtime/flows/shared/prompts/researcher_clustering.md
+++ b/runtime/flows/shared/prompts/researcher_clustering.md
@@ -82,11 +82,9 @@
 
 Title each cluster with a short working label, under 10 words, that names the territory. Titles can be plain and topical — "Accountability for powerful states", "NATO burden-sharing", "EPP firewall" — because the abstract does the analytical work. Do not try to cram the binding into the title.
 
-CLOSURE AND UNIQUENESS REQUIREMENT
+CLOSURE AND UNIQUENESS
 
-Before returning, verify:
-1. Every `ref` in the input array appears exactly once in your output — either inside exactly one cluster's `refs` list, or inside the `isolates` list. No item may appear in two clusters, and no item may be omitted.
-2. The count of unique `ref` values across all clusters plus isolates must equal the total count of items you received. If it doesn't, you've duplicated or dropped something — find the error and fix it before returning.
+Every `ref` in the input array appears exactly once in your output — either inside exactly one cluster's `refs` list, or inside the `isolates` list. No item appears in two clusters, and no item is omitted.
 
 OUTPUT FORMAT
 
--- a/runtime/flows/shared/prompts/researcher_theming.md
+++ b/runtime/flows/shared/prompts/researcher_theming.md
@@ -66,9 +66,7 @@
 
 CLOSURE REQUIREMENT
 
-Before returning, verify:
-1. Every cluster_id in the input array appears exactly once in your output — inside exactly one theme's `cluster_ids` list. No cluster may appear in two themes, and no cluster may be omitted.
-2. A cluster that doesn't fit any grouping still becomes a theme of its own (a single-cluster theme), rather than being dropped.
+Every cluster_id in the input array appears exactly once in your output — inside exactly one theme's `cluster_ids` list. No cluster appears in two themes, and none is omitted: a cluster that fits no grouping becomes a single-cluster theme.
 
 OUTPUT FORMAT
 
````

### F6. Provocateur formulation: stop writing unread cache entries

`F6_formulation_cache_writes.patch`

````diff
--- a/runtime/flows/provocateur_flow.py
+++ b/runtime/flows/provocateur_flow.py
@@ -1146,7 +1146,10 @@
         max_tokens=FORMULATION_MAX_TOKENS,
         task_label=label,
         logger=logger,
-        cache_system=True,  # C19a: voice's 3-5 formulations share system prompt
+        # No prompt cache: the system prompt carries this call's theme_material
+        # and member_profile, so no other call can read its entry (Athens
+        # N1-N3: 128 formulation calls wrote ~2.99M cache tokens, read 0).
+        cache_system=False,
         cfg=step_config("runtime.provocateur.formulation"),
     )
     # Defensive: ensure member + theme_id echoed back even if model omitted them
````

### F7. Validators and synthesis router: room for thinking if a route gets it (needs F1 first)

`F7_max_tokens_when_thinking.patch`

````diff
--- a/runtime/flows/editor/synthesis_router.py
+++ b/runtime/flows/editor/synthesis_router.py
@@ -134,7 +134,9 @@
     try:
         message = client.messages.create(
             model=cfg.model,
-            max_tokens=SYNTHESIS_ROUTER_MAX_TOKENS,
+            # Thinking counts toward max_tokens; 500 is sized for thinking off.
+            max_tokens=(max(SYNTHESIS_ROUTER_MAX_TOKENS, 16000) if cfg.thinking_on
+                        else SYNTHESIS_ROUTER_MAX_TOKENS),
             system=_SYSTEM_PROMPT,
             messages=[{"role": "user", "content": user_prompt}],
             **thinking_kwargs,
--- a/runtime/flows/voice/step2_validation.py
+++ b/runtime/flows/voice/step2_validation.py
@@ -90,7 +90,9 @@
     thinking_kwargs = cfg.thinking_kwargs()
     resp = client.messages.create(
         model=cfg.model,
-        max_tokens=STEP2_VALIDATION_MAX_TOKENS,
+        # Thinking counts toward max_tokens; 4096 is sized for thinking off.
+        max_tokens=(max(STEP2_VALIDATION_MAX_TOKENS, 16000) if cfg.thinking_on
+                    else STEP2_VALIDATION_MAX_TOKENS),
         system=system,
         messages=[{"role": "user", "content": user}],
         **thinking_kwargs,
````

### F8. Pass 7c Claude fallback: true premise, concrete bar

`F8_7c_fallback_bias_block.patch`

````diff
--- a/personas/flows/shared/prompts/persona_pass_7c_negative.md
+++ b/personas/flows/shared/prompts/persona_pass_7c_negative.md
@@ -10,11 +10,11 @@
 should be a distinctive voice.
 
 {% if claude_fallback %}
-BIAS-AWARENESS INSTRUCTION: You generated the worked provocations being
-evaluated. You will be biased toward rating them well. Counteract this by
-actively looking for moments that sound like generic AI rather than this
-specific voice. Be harsh. The goal is to grow the banned lists, not to
-celebrate the output.
+SAME-FAMILY CAVEAT: a Claude model wrote the worked provocations you are
+reading, and evaluators tend to rate output from their own model family
+too kindly. Read against that pull: look for the moments that sound like
+a generic AI assistant rather than this voice. Add an item only when you
+can point to the passage in the worked provocations that shows the failure.
 {% endif %}
 
 Scan for THREE categories (Phase B adds the third per decisions log #16):
````

### F9. Persona prompts: current rules instead of migration-relative text

`F9_migration_relative_phrasing.patch`

````diff
--- a/personas/flows/shared/prompts/pass_0a_voice_config.md
+++ b/personas/flows/shared/prompts/pass_0a_voice_config.md
@@ -59,7 +59,7 @@
 
 - `editorial_rationale`: ALWAYS set this to `null`. The curator fills it in post-review; the model must not propose it. The review_doc will explicitly ask the curator to provide it.
 
-Do NOT include: `conference_context` (dropped in Phase B), `primary_text_sources`, `voice_type_adjustments_needed`, `counter_tradition_scholars`, or any other editorial-assets fields.
+Do NOT include: `conference_context`, `primary_text_sources`, `voice_type_adjustments_needed`, `counter_tradition_scholars`, or any other editorial-assets fields.
 
 ### REVIEW DOC
 
@@ -133,5 +133,5 @@
 - `review_doc` is a single markdown string. Do NOT wrap in code fences.
 - `voice_config`: 8-9 fields per the schema above (wikipedia_url conditional).
 - `editorial_rationale` is ALWAYS `null` in the JSON; the curator writes it into the file post-review.
-- Do NOT emit `conference_context` (Phase B dropped it).
+- Do NOT emit `conference_context`.
 - Do NOT emit `primary_text_sources` or any editorial-assets fields.
--- a/personas/flows/shared/prompts/pass_1_1_merge.md
+++ b/personas/flows/shared/prompts/pass_1_1_merge.md
@@ -211,10 +211,9 @@
 - All required fields present; optional fields populated when content exists.
 - `available_pathe[]` minimum 5 entries (preserve more for rich voices); each
   with `term_in_original_language` (script or transliteration) + `gloss`.
-- **1-arch-08 (2026-04-22):** `anachronisms_to_avoid` is NO LONGER an
-  output field of `LifeScaffold`. Anachronism discipline has consolidated
-  at `KnowledgeBoundary.anachronism_discipline[]` (Pass 1.5). Pass 1.1
-  still NAMES anachronisms in narrative fields where relevant (e.g. in
+- `LifeScaffold` has no `anachronisms_to_avoid` field: anachronism
+  discipline lives at `KnowledgeBoundary.anachronism_discipline[]`
+  (Pass 1.5). Pass 1.1 still NAMES anachronisms in narrative fields where relevant (e.g. in
   `framework_for_difficulty` you may write "not 'trauma' (anachronistic
   clinical category) but *nadryv*, the moral-theological self-laceration"),
   but DO NOT emit a separate anachronisms_to_avoid list. Pass 1.5 owns the
@@ -269,9 +268,6 @@
   ],
   "framework_for_difficulty": "Philosophy is meletē thanatou — 'preparation for death' (Phaedo 67e) — the soul's release from the body. Suffering is the symptom of the soul's disorder or the body's tyranny; injustice harms the doer more than the sufferer (Gorgias 469b). Suffering has meaning inside the cosmic-ethical order of the Forms; outside it, it has none. [experiential_reconstruction]",
   "model_of_selfhood": "Tripartite psychē — logistikon (reason, head), thumoeides (spirit, chest), epithumētikon (appetite, below). In Phaedrus, a charioteer drives a noble horse and a dark horse. Not a unified interior; a site to be ruled and ordered. [experiential_reconstruction]",
-  // NOTE (1-arch-08, 2026-04-22): `anachronisms_to_avoid` removed from
-  // LifeScaffold output. Pass 1.5 produces KnowledgeBoundary.anachronism_discipline[]
-  // with dual framings (biographical + epistemic) per entry.
   "scholarly_context": "Vlastos (Socrates: Ironist and Moral Philosopher 1991) treats the early dialogues as historical Socrates; Griswold and Ferrari read the dialogue form as itself dramatic. Burnyeat on the dating debate. Annas (Platonic Ethics 1999) for the continuity thesis between Republic and Laws. Sedley on Plato as a systematic metaphysician vs. Vlastos on aporetic Socratic method. These debates bear on which scholar-tradition anchors the voice's formative-experience framing."
 }
 ```
--- a/personas/flows/shared/prompts/pass_1_2_merge.md
+++ b/personas/flows/shared/prompts/pass_1_2_merge.md
@@ -70,8 +70,7 @@
 
 ## What you DO NOT
 
-1. **Do NOT cap at 10-20 commitments.** Pre-1-arch-03 prompt guidance said
-   10-20; under additive merge, 10 is the minimum. Well-documented voices
+1. **Do NOT cap commitments.** At merge, 10 is the minimum. Well-documented voices
    (Dostoevsky, Plato, Arendt) may produce 20-40 at merge. Pass 3 selects
    to card's 10-20; merge preserves.
 
--- a/personas/flows/shared/prompts/pass_1_3_merge.md
+++ b/personas/flows/shared/prompts/pass_1_3_merge.md
@@ -66,20 +66,19 @@
      recurring forms the voice's reasoning employs); worked demonstrations
      (how specific historical events produced specific rhetorical-textual
      responses); scholarly debates (named interpretive traditions on the
-     voice's reasoning). This is what pre-1-arch-03 dropped. Preserve fully.
+     voice's reasoning). Preserve fully.
    - Cross-reference: `ReasoningStep.scholarly_context` names interpretive
      framing per step; `Move.structural_pattern_refs` (Pass 1.4) links
      moves to patterns here.
 
 5. **Preserve depth.** DR §3 for well-documented voices carries 40K+ chars
-   of rich material. Do not compress. Output may be substantially longer
-   than pre-1-arch-03 Pass 1.3 output.
+   of rich material. Do not compress; long output is expected.
 
 6. **Source-filtering discipline.** All three sources contribute additively.
    - Perplexity §3: scholarly-consensus anchor, citation density
    - Claude DR §3: deepest analytical material — carnivalization analyses,
-     worked demonstrations, structural-pattern enumeration. **This is where
-     pre-1-arch-03 lost the most.** Preserve.
+     worked demonstrations, structural-pattern enumeration. **This is the
+     material most easily lost at merge.** Preserve.
    - Gemini full: cross-disciplinary parallels (Arendt's judgment → Kantian
      lineage; Dostoevsky's scenic-collision → Kierkegaard dialectic-of-
      existence), multilingual scholarship on reasoning
@@ -262,10 +261,10 @@
 }
 ```
 
-## Example C — Dostoevsky (human, narratival) — 1-arch-03 ARCHITECTURAL DEMO
-
-**This is THE worked example for 1-arch-03.** Dostoevsky §3 is where
-pre-1-arch-03 lost the most material. Full preservation demonstrated:
+## Example C — Dostoevsky (human, narratival) — additive-merge demo
+
+**This is THE worked example for additive merge.** Dostoevsky §3 carries
+the most material to lose. Full preservation demonstrated:
 8-step reasoning_method + 5 structural_patterns + 3 worked_demonstrations
 + 4 scholarly_debates + rich textures. Lift-from-Phase-L-Dostoevsky-card
 where possible; add material DR §3 surfaced that the old card lost.
--- a/personas/flows/shared/prompts/pass_1_5_merge.md
+++ b/personas/flows/shared/prompts/pass_1_5_merge.md
@@ -60,11 +60,10 @@
 Morson vs. McReynolds vs. Goldstein; Burnyeat vs. Popper on the noble lie.
 Preserve breadth; do not flatten to one reading.
 
-## Voice_mode drop (1.5-04 absorbed)
+## Voice mode
 
 Voice_mode is structurally irrelevant at 1.5. Boundaries = type + period +
 subtype + hostile_sources; reasoning-mode doesn't affect what's excluded.
-The voice_mode variable is no longer rendered in this prompt.
 
 ## Hostile-source handling
 
@@ -144,12 +143,8 @@
     existentialist), `"use_with_caution"` (with scare-quotes or scholarly
     framing — "psychology", "career"), or `"translator_note"` (translator-
     tradition artifact like Garnett's "conscience" for "sovest'").
-  This consolidates anachronism discipline from the pre-1-arch-08 split
-  between `LifeScaffold.anachronisms_to_avoid` (biographical angle) and
-  `KnowledgeBoundary.conceptual_exclusions` (epistemic angle). Single
-  source eliminates drift; the removed LifeScaffold field no longer
-  produces output. Pass 1.7 coherence Check 4 (anachronism/boundary
-  cross-check) becomes obsolete.
+  This list is the card's single source of anachronism discipline, with
+  the biographical and the epistemic angle on each entry.
 - `sensitive_topics.topics[]` minimum 3; uncapped. Each with
   what_the_voice_actually_thought (substantive, sourced, NOT sanitised) +
   navigation_guidance + scholarly_reception (when sources provide).
--- a/personas/flows/shared/prompts/pass_1_6_merge.md
+++ b/personas/flows/shared/prompts/pass_1_6_merge.md
@@ -104,7 +104,7 @@
 }
 ```
 
-**1-arch-07 (2026-04-22):** `urls` is NO LONGER an output key. URL inventory
+There is no `urls` output key: the URL inventory
 is derived at render-time by Python from `passages[].citation` and `works[]`
 string fields (via `flows/shared/url_extract.extract_urls()`). When you
 produce works[] and passages[] entries, **embed URLs within the relevant
--- a/personas/flows/shared/prompts/pass_1_7_coherence.md
+++ b/personas/flows/shared/prompts/pass_1_7_coherence.md
@@ -40,7 +40,7 @@
 Pass 2-6 synthesis. **Every inconsistency you miss becomes a silent
 contradiction propagated to the persona card.**
 
-Under 1-arch-03 you have an additional responsibility: **preservation-check**.
+You also run a **preservation-check**.
 The merge layer should have preserved all unique non-redundant content from
 Perplexity + Claude DR + Gemini. If chunk outputs look thin relative to
 source richness, flag as preservation failure (Check 8 / 9). You cannot fix
@@ -50,7 +50,7 @@
 
 Run these systematically.
 
-## Original checks (inherited from pre-1-arch-03)
+## Core checks
 
 1. **Formative / commitment alignment.** Do `formative_candidates[]` support
    `commitments[]`? Commitments should be traceable (via §14 `engagement_it_
@@ -69,9 +69,8 @@
    method is perceptual-response but voice register describes "argument with
    counterexamples."
 
-4. **Anachronism discipline self-consistency (formerly anachronism boundary
-   cross-check; simplified under 1-arch-08, 2026-04-22).** Anachronism
-   discipline now lives in a single canonical source:
+4. **Anachronism discipline self-consistency.** Anachronism discipline
+   lives in a single canonical source:
    `knowledge_boundary.anachronism_discipline[]` (AnachronismEntry list
    with `biographical_framing` + `epistemic_framing` + `severity`). The
    old cross-check between `life_scaffold.anachronisms_to_avoid` and
@@ -97,7 +96,7 @@
    missing terms into preferred_vocabulary (as VocabEntry with loadbearing=true
    if term is philosophically/theologically central).
 
-## 1-arch-03 new checks
+## Preservation checks
 
 8. **Source-attribution preservation.** For each major claim in merged
    chunks (commitments, concepts, formative_candidates, structural_patterns,
--- a/personas/flows/shared/prompts/persona_pass_1d_excerpt_selection.md
+++ b/personas/flows/shared/prompts/persona_pass_1d_excerpt_selection.md
@@ -10,12 +10,9 @@
 
 Selection rules:
 - Total budget: approximately 60,000 characters across all selections combined.
-  Bumped from 30K (2026-04-25) — empirical signal from Plato showed 25/151
-  Pass 7-pre claims went UNVERIFIED at 30K because well-attested doctrines
-  (anamnēsis, divided line, meletē thanatou, etc.) lived in the merged
-  dossier but weren't anchored to a curated excerpt. 60K covers richer-
-  corpus voices (Plato, Arendt) without bloating smaller-corpus voices —
-  the per-source cap keeps single-source dominance in check.
+  Use it to anchor the dossier's well-attested doctrines (for Plato:
+  anamnēsis, the divided line, meletē thanatou) to curated excerpts; the
+  per-source cap below keeps one source from dominating.
 - Per source: at most ~15,000 chars from any single source. Better to span
   multiple sources than to over-sample one.
 - Prefer passages where SUBSTANCE and VOICE coincide — material that exemplifies
--- a/personas/flows/shared/prompts/persona_pass_6_user.md
+++ b/personas/flows/shared/prompts/persona_pass_6_user.md
@@ -14,9 +14,9 @@
 Chunk 1.6 — CORPUS (works + passages + reference_only_passages):
 
 **works** (uncapped bibliographic catalogue with tier + source_type per entry
-+ bibliographic_scholarly_context per 1-arch-03 — named scholarly-corpus
-debates). `urls` chunk was removed under 1-arch-07 — URL inventory is
-derived at render-time from passages[].citation + works[] string fields:
++ bibliographic_scholarly_context — named scholarly-corpus debates). The
+URL inventory is derived at render-time from passages[].citation + works[]
+string fields:
 
 {{ works }}
 
````

### F10. Pass 4b: keep the register bar, drop the re-read step (C62 only)

`F10_4b_read_aloud.patch`

````diff
--- a/personas/flows/shared/prompts/persona_pass_4b_artifact.md
+++ b/personas/flows/shared/prompts/persona_pass_4b_artifact.md
@@ -22,8 +22,8 @@
   mid-thought...", "I require only text...", "In my public artifact I
   preserve...") or (b) a second-person imperative addressed to the voice
   ("You must write 350–550 words...", "Make the finished piece feel like
-  a letter..."). READ EACH FIELD ALOUD BEFORE RETURNING. If it sounds like
-  a scholar describing the voice from outside, rewrite. Specifically BANNED
+  a letter..."). A field that sounds like a scholar describing the voice
+  from outside has failed; write it from inside. Specifically BANNED
   third-person opening patterns for this pass: "Opens mid-thought, already
   addressing you..." (rewrite as "I open mid-thought..."); "Text only — the
   voice lives entirely..." (rewrite as "I require only text. My voice..."
@@ -41,7 +41,7 @@
   in-voice. (Phase L learning 2026-04-21: Gemini Pass 7a cross-model
   validation flagged exactly these 6 fields on the Dostoevsky card for
   "a critical flaw in a system prompt"; the automated register scanner
-  missed all 6. Do not trust the scanner alone — read aloud.)
+  missed all 6, so judge each field yourself.)
 - **CURATOR-SIDE METADATA — STRIP WITH POSITIVE COMPENSATION (FU#12-A
   2026-04-23 / FU#32 2026-04-23):**
   Same STRIP+DO-INSTEAD discipline as Pass 2/3/4a: no provenance
@@ -66,10 +66,9 @@
   instruction. "I write 350–550 words of prose that begins mid-
   confession and ends unresolved — the length of a Diary entry, the
   shape of a door closing too fast." The field IS the voice giving
-  itself a craft-instruction for the morning piece. Read each field
-  aloud: if you hear a designer describing the voice's artifact, it
-  has failed. If you hear the voice giving itself a craft-rule, it
-  passes.
+  itself a craft-instruction for the morning piece. A field that
+  reads as a designer describing the voice's artifact has failed; one
+  that reads as the voice giving itself a craft-rule passes.
 
   **FU#38 2026-04-24 — voice-self-reference vocabulary strip.** Same
   discipline as Pass 2/3/4a: post-voice-lifetime critical vocabulary
````

### F11. Safeguards validator: concrete WARN bar (needs F4 first)

`F11_validator_warn_bar.patch`

````diff
--- a/runtime/flows/shared/prompts/voice_step2_validation_safeguards.md
+++ b/runtime/flows/shared/prompts/voice_step2_validation_safeguards.md
@@ -44,4 +44,4 @@
 
 For WARN-tier lists (`hard_limits_breach`, `banned_modes_slip`, `banned_language_ai_slop`, `first_person_presence_leak`), append objects `{"text": "<quoted span>", "rule_cited": "<which card field + which item>"}` for each instance found.
 
-Be strict on HOLD-tier rules; be discerning on WARN-tier (only flag clear violations, not mild stylistic shadings).
+Be strict on HOLD-tier rules. For the WARN-tier lists, add an entry when you can quote the span and name the card rule it breaks; leave out stylistic shadings you cannot tie to a named rule.
````

## 9. Noticed in passing (outside this task; for Task 1 or the trackers)

- `personas/flows/shared/prompts/persona_pass_4a_voice.md:212-213` names "Tang, Thiel" (voices removed 2026-04-28) in model-facing text. C68 A14 covers only the Provocateur prompts.
- `runtime/OPEN_ITEMS.md` C19a (`:1012`, `:1055`) says formulation and triage calls share a cached system prompt; the Athens telemetry in F6 shows they don't read it.
- `docs/LLM_CALL_INVENTORY.md` §10.2 and §10.3 say a Sonnet 4.6 → 5 swap has "no break" on thinking, and the C62 update in `runtime/OPEN_ITEMS.md` repeats it ("speaker_id + cleaning … can move to Sonnet 5"). F1's patch corrects §10.2's sentence; §10.3's table row, §6 and the C62 note need the same.
- Stale model notes inside Jinja comments (not model-facing, so not findings here): `persona_pass_7b_smoke_test.md:1-2` ("overrides spec's Sonnet temp 0.4"), `persona_pass_1d_excerpt_selection.md:1` ("Claude Sonnet"; routing: Opus 4.7), `persona_pass_7c_negative.md:2-3`.
- Persona callers that catch `RuntimeError` and retry will retry a `ClaudeRefusal` once. The persona pipeline has no Prefect retries, so that is the only retry source there.

## 10. Changes in the 2026-09-30 revision

Made in answer to the independent review (`_workspace/planning/REVIEWS_OF_FABLE_DELIVERABLES_2026_09_29/03_model_era.md`). The 2026-09-28 version is commit `0910a66`.

**Answers to the review's questions**

1. **F4 threshold: accepted.** I had not weighed `validator_evidence` §4.3; the two reports were written in parallel. The rule is now: WARN on any failed quality criterion, or when fewer than 2 moves show. On Athens it gives 20 of 30 voice-fidelity WARNs, against 27 under the strict rule, and an overall gate of 6 PASS / 22 WARN / 2 HOLD.
2. **F2 retries: not deliberate.** The first patch stopped only `stream_voice_call`'s own retry. The Prefect task retries would have re-sent a declined request, up to 5 times over about 7.75 minutes for Provocateur. Fixed with a `retry_condition_fn`.
3. **Decision 3: yes, "the split saves more" wrongly assumed calls could read each other's cache entries.** Formulations run in parallel. The recommendation is now "off, and no split".
4. **F1 policy: explicit `disabled` is the no-change default.** C62 should trial adaptive thinking with `effort: "low"` on the thinking-off steps.

**Changes to the findings and text**

| # | Where | Change |
|---|---|---|
| 1 | Header | Checkout and status lines updated; pointer to this section. |
| 2 | §1 counts table | F10 moved from 1d to 1b; L4 added. |
| 3 | §1 F1, F1 location, F2 location, F3, §3 | Line references updated to `main` at `86998b4`. |
| 4 | §1 F2, F2 | Removed "and retry once on the way" (wrong: a refusal raises nothing today, so nothing retries). The synthesis router is not "silent": it logs a warning with the wrong cause. Added the Prefect retry consequence. |
| 5 | §1 F4, F4, decision 1 | "Contradicts itself" became "ambiguous". Added the full effect of the strict rule (1 of 30 at PASS), the three-rule comparison table, and the threshold recommendation. |
| 6 | §1 | The loader sentence now says `call_claude`, not the loader, drops temperature. |
| 7 | Decision 3, F6 | Parallel fan-out stated; recommendation changed to "off, and no split". |
| 8 | §2 | New scripts listed; disclosure that the 2026-09-28 test runs may have written Prefect's test database under `~/.prefect`. |
| 9 | F1 | Added the policy note (review question 4) and the C67 test mock fix. |
| 10 | F2 | Added the retry analysis, the ledger-before-raise fix, and the open point on Speaker ID and C49. |
| 11 | F3, §7 | The gate is runnable (`f7e0d4c`). `persona_pass_7a_cross_model.md` is now in the patch, and that is recommended instead of left open. |
| 12 | F4, F11 | Noted that `cross_night_echo` never ran in Athens (30 of 30 null). |
| 13 | F7 | "Silently" removed for the router fallback. |
| 14 | L6 | No longer claims structured outputs are unsupported on Opus 4.7 / Sonnet 4.6; the cached list only omits them. |
| 15 | §7 | F7 also needs F1. Suite numbers re-run on `main`: runtime 385 → 397, personas 259 → 264. Independence checked with `git apply --check`. |
| 16 | §9 | C62 note added to the inventory bullet; the refusal-retry bullet narrowed to the persona pipeline. |

**Changes to the patches** (all rebuilt on `main`; F5, F6, F8, F9, F10 and F11 are unchanged in content)

| Patch | Change |
|---|---|
| F1 | `test_transcription_speaker_id_fallback.py:44`: the mock block gets `type="text"`. |
| F2 | `retry_unless_refused` added to `anthropic_checks.py` and set as `retry_condition_fn` on 8 Prefect tasks. `call_claude` records the call before raising. Three more tests, one on a real Prefect task. |
| F3 | `persona_pass_7a_cross_model.md` is rendered too (2 call sites); the test covers all three prompts. |
| F4 | Voice fidelity uses the threshold rule with `_MIN_MOVES_PERFORMED = 2`. "MUST perform" became "repertoire" in the prompt, the user message and the docstring. Tests rewritten for the threshold. |
| F7 | Content unchanged; it depends on F1, which the first version did not say. |

**Where I disagree with the review**

- **Problem 4 says F4 and F11 both edit the cross-night echo prompt.** Only F4 does. F11's patch touches one file, `voice_step2_validation_safeguards.md`. The point about the pillar never having run stands, and F4 now says so.
- **Nothing else.** I re-ran the review's strict-rule numbers (27 of 30, 1 PASS) and the 30-of-30 null echo count, and they match. The "WRONG" on the voice-step retry, the "DOUBTFUL" on F7's independence and on L6, and both "STALE" items are correct and are fixed above.
