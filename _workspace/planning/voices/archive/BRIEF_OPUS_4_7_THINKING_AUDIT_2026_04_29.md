# BRIEF — Opus 4.7 thinking audit (persona pipeline + runtime)

**Date:** 2026-04-29
**Triggered by:** Voice Pipeline first dry-run (Plato solo) showed `thinking_tokens=0` on every Opus 4.7 call despite `thinking={"type":"adaptive"}` being set.
**For:** persona-pipeline session pickup (and runtime — researcher / provocateur — separately)
**Scope:** **Investigation, not code change.** Determine whether the persona pipeline is actually getting extended thinking on its Opus 4.7 calls, document findings, decide whether to adopt the newer `effort` + `display` API surface.

---

## TL;DR — what the voice pipeline discovered

The Voice Pipeline dry-run (Plato, 3 formulations on "The Legitimacy of the Invisible") completed end-to-end with high-quality output. But:

```
plato__theme_001.json: thinking_enabled=True, in=29535, out=4138, thinking_tokens=0, trace_len=0
plato__theme_002.json: thinking_enabled=True, in=29569, out=4702, thinking_tokens=0, trace_len=0
plato__theme_003.json: thinking_enabled=True, in=29541, out=6241, thinking_tokens=0, trace_len=0
```

**Adaptive thinking decided "no thinking needed" on every call.** That is the empirically observed behavior of `{"thinking": {"type": "adaptive"}}` on Opus 4.7 with persona-card-shaped system prompts (~30K input tokens) under default effort.

The voice pipeline's `_thinking_kwargs` matches `researcher_flow._thinking_kwargs` byte-for-byte. So the same question applies to researcher, provocateur, and personas: **are any of these pipelines actually getting extended thinking when they think they are?**

---

## Why this matters for the persona pipeline

The persona pipeline runs **far more Opus 4.7 calls per voice** than the Voice Pipeline:

Per LLM_CALL_INVENTORY.md (2026-04-27 state — may be slightly stale post-FU#52/53/57):

- Pass 0a (Voice Config) — Opus 4.7, adaptive, 24K
- Pass 0b (Tailor) — Opus 4.7, adaptive, 16K
- Pass 1.1–1.6 (chunked DR) — 6× Opus 4.7, adaptive, 48K each
- Pass 1.7 (Coherence audit) — Opus 4.7, adaptive, 24K
- Pass 1d (Excerpt selection) — Opus 4.7, adaptive, 16K
- Pass 2 (Identity & Boundaries) — Opus 4.7, adaptive, 32K
- Pass 3 (Intellectual Core) — Opus 4.7, adaptive, 32K
- Pass 4a (Voice corpus-grounded) — Opus 4.7, adaptive, 24K
- Pass 4b (Artifact) — Opus 4.7, adaptive (per inventory)
- Pass 5 (Engagement) — Opus 4.7, adaptive
- Pass 6 (Corpus integration) — Opus 4.7, adaptive
- Pass 7 family — Opus 4.7 (some) + Sonnet 4.6 (CT passes)

That's ~15 Opus 4.7 calls per voice. If thinking is silently OFF on all of them, the persona pipeline is paying Opus 4.7 prices for Opus-4.7-without-thinking quality. Thinking is the lever Anthropic specifically engineered into 4.7; if we're not using it, we should know.

**Critical observation:** the persona pipeline's call-site outputs record `input_tokens` and `output_tokens` only. **`thinking_tokens` is not surfaced** in the per-pass JSON outputs. So nobody has been able to see the actual thinking-token usage in production — the question hasn't been answerable until now.

---

## What's actually established (and what's newer Anthropic guidance)

### Established (LLM_CALL_INVENTORY.md, 2026-04-27)

All Opus 4.7 call sites across runtime + personas use the same shape:

```python
# researcher_flow.py
return {"thinking": {"type": "adaptive"}, "temperature": 1.0}

# provocateur_flow.py
return {"thinking": {"type": "adaptive"}}  # no explicit temperature

# personas/flows/shared/clients.py (call_claude)
kwargs["thinking"] = {"type": "adaptive"}
# temperature handled separately, defaults to 1.0
```

Voice pipeline matches researcher_flow exactly. None of these throw 400 errors on 4.7. The pattern works at the API level.

### Newer Anthropic guidance NOT yet adopted anywhere

Two API surfaces are post-Opus-4.7-launch additions per `https://platform.claude.com/docs/en/build-with-claude/adaptive-thinking` and `.../effort`:

1. **`output_config: {effort: "low"|"medium"|"high"|"xhigh"|"max"}`** — soft control on thinking depth.
   > "At the default effort level (`high`), Claude almost always thinks. At lower effort levels, Claude may skip thinking for simpler problems."

   Per Anthropic: `xhigh` is the recommended starting point for "coding and agentic work, and for exploratory tasks such as repeated tool calling, detailed web search, and knowledge-base search." `high` is "often the sweet spot." For Sonnet 4.6, `medium` is the explicit recommended default.

2. **`thinking: {type: "adaptive", display: "summarized"}`** — opt-in to actually SEE the thinking text on Opus 4.7.
   > "On Claude Opus 4.7, `thinking.display` defaults to `"omitted"`. Thinking blocks still appear in the response stream, but their `thinking` field is empty unless you explicitly opt in."

   This means even if thinking IS happening, we can't see the trace unless `display: "summarized"` is set explicitly. **This is a 4.7-specific change** from 4.6.

### What about temperature / top_p / top_k?

Bedrock docs claim "Thinking isn't compatible with `temperature`, `top_p`, or `top_k` modifications." But 30+ production call sites set `temperature=1.0` explicitly and work without errors. Likely interpretation: "modifications" means non-default values; explicit set to 1.0 (the SDK default) is OK. Or the Bedrock doc is stale. Voice pipeline observation: `temperature=1.0` does NOT cause 400 errors on Opus 4.7 with adaptive thinking. Established pattern is safe.

---

## Investigation tasks

### Task 1 — Are personas pipeline runs getting thinking tokens at all?

**Tooling needed:** add temporary instrumentation or read raw API responses.

**Quick path:** patch `personas/flows/shared/clients.py:call_claude()` to log `final.usage.thinking_tokens` (or `0` if not present) for each call. Run a single Pass 2 (Identity & Boundaries) for any voice. Check whether `thinking_tokens` is non-zero.

```python
# in call_claude(), after final = stream.get_final_message():
thinking_tokens = getattr(final.usage, "thinking_tokens", 0) or 0
logger.info(f"  thinking_tokens={thinking_tokens}")
```

**Expected outcomes:**

- **Outcome A: thinking_tokens > 0 on persona passes.** Adaptive IS working for persona prompts (probably because they're more diverse / DR-style than voice pipeline's "reason as voice X" prompts). No urgent action; just adopt `display: "summarized"` if you want to see traces.

- **Outcome B: thinking_tokens = 0 on persona passes (matches voice pipeline observation).** Adaptive at default effort is silently OFF across the persona pipeline. Persona cards have been built without the lever Anthropic specifically engineered for 4.7. **This is a real finding worth a follow-up.**

### Task 2 — If Outcome B, evaluate impact

For 1-2 voices already shipped (e.g. Plato), examine the chat-test outputs and the assembled card and ask:

- Is the persona-card quality plausibly explained by Opus 4.7 *without* thinking? (Probably yes — Plato shipped with verdict GOOD.)
- Would adding thinking *break* anything that's currently working (texture, register, voice tissue)? Or would it raise the floor on harder voices?
- Are the FU-stack patches, the 9480d3a revert, the FU#49A v2 quality_criteria 3-dim shift, etc. — were any of those actually compensating for missing thinking?

The 9480d3a revert message specifically said:
> "Empirical investigation tonight (2026-04-28) showed cumulative prompt-side additions since 582af96 (FU#49 stack, cryofreeze framing, tense-discipline OUTPUT REGISTER blocks, family-of-forms emission, mediated-voice pattern mandates) had degraded runtime artifact texture relative to the 2026-04-25 shipped-Plato baseline."

That diagnosis is consistent with "thinking was off" — without thinking, prompt-side additions dominate the model's context-window allocation. With thinking on, the model has room to reason about which directives matter most. Worth thinking about (no pun intended).

### Task 3 — Test `effort` + `display` on a single persona pass

**Surgical test:** patch `_thinking_kwargs` in `personas/flows/shared/clients.py` (or add a feature flag) to use:

```python
{
    "thinking": {"type": "adaptive", "display": "summarized"},
}
```

Plus the call site adds `output_config={"effort": "high"}` or `"xhigh"` (Anthropic's recommended starting points for non-coding intelligence-sensitive workloads vs coding/agentic).

Run one Pass 3 (Intellectual Core) on Plato or a fresh voice. Compare:
- Wall time delta
- `thinking_tokens` value
- Output quality (verdict from Pass 7a critic; chat-test sniff)

If thinking shows up and quality holds or improves: adopt across persona pipeline. File as FU.

If thinking shows up and texture degrades: revert; the 9480d3a finding generalizes (cumulative additions hurt; thinking adds another layer of "cumulative").

If thinking still doesn't show up: there's a deeper SDK or parameter issue; investigate further.

### Task 4 — Verify SDK 0.94.1 supports `output_config`

Both pipelines pin `anthropic==0.94.1`. The `output_config` top-level parameter for `effort` may be newer than that pin. Quick check:

```bash
cd code/personas
venv/bin/python -c "
import anthropic
sig = anthropic.Anthropic().messages.create.__doc__
print('output_config in signature?', 'output_config' in (sig or ''))
import inspect
print(inspect.signature(anthropic.Anthropic().messages.create))
"
```

If `output_config` is not in the SDK signature, either:
- Bump the SDK pin (changes both venvs — coordinate)
- Pass via `extra_body={"output_config": {"effort": "..."}}`  (works on most SDK versions)

---

## Decision points (to bring back to operator)

1. **Are any persona Opus 4.7 calls actually thinking?** (Task 1 result)
2. **If not, what's the cost of leaving it that way through Athens?** (Task 2 judgment call)
3. **If we adopt `effort` + `display`, do we pin a single setting (e.g. `high` everywhere) or per-pass?**
   - Recommendation: per-pass. Pass 1.1–1.6 (chunked DR) is structured-output — `medium` per Anthropic's "structured output can lead to overthinking at xhigh/max" warning. Pass 2/3/4a (creative voice generation) — `high` or `xhigh`. Pass 4b (artifact) — `high` (same overthinking warning applies). Pass 7a (critic) — `xhigh` (deep cross-pass analysis).
4. **Do we backfill LLM_CALL_INVENTORY.md** with the new columns (effort, display, observed thinking_tokens per pass)?
5. **Athens timing constraint:** if changing this requires re-running shipped voices, is the budget there?

---

## Voice Pipeline status (for context)

Branch: `voice-pipeline-v2.1-align-revert` on `voice-pipeline-v2.1-align-revert` (committed; not merged to main).

Three commits:
- `fb33bb9` — v2.1 alignment with 9480d3a persona-prompt revert
- `30a38eb` — v2.1 follow-up (FU#57 spec sync + continuity prompt fix)
- `f68bc3f` — post-dryrun tuning (validator (c) soften + extraction-ID bookkeeping + load_dotenv override)

Voice pipeline is currently **NOT adopting `effort` + `display`** — pending this audit's outcome on the persona side. If the persona pipeline adopts the newer surface, voice pipeline follows in lockstep. If the persona pipeline decides to stay at `{"type": "adaptive"}` baseline, voice pipeline stays too.

The decision is intentionally cross-pipeline: we want one consistent thinking-config story across runtime + personas, not voice-pipeline-only divergence.

---

## References

**Anthropic docs (2026-04-29 fetch):**
- `https://platform.claude.com/docs/en/build-with-claude/adaptive-thinking` — adaptive thinking spec, including `display: "omitted"` default on 4.7
- `https://platform.claude.com/docs/en/build-with-claude/effort` — effort parameter, per-model recommended values
- `https://docs.aws.amazon.com/bedrock/latest/userguide/claude-messages-extended-thinking.html` — Bedrock's parameter compatibility doc (older guidance; partial conflict with platform.claude.com)

**Codebase:**
- `runtime/flows/researcher_flow.py:104-127` — canonical `_thinking_kwargs` pattern
- `runtime/flows/provocateur_flow.py:131-135` — variant without explicit temperature
- `personas/flows/shared/clients.py:60-105` — `call_claude()` thinking handling
- `runtime/flows/voice/step1_private_reasoning.py:50-58` — voice pipeline (matches researcher)
- `docs/LLM_CALL_INVENTORY.md` — call-by-call inventory (last updated 2026-04-27)

**Voice Pipeline dry-run outputs (the empirical 0-thinking observation):**
- `/Users/aienvironment/Desktop/AI Assembly/projects/voice-pipeline-dryrun/runs/dryrun_2026_04_29_plato_solo/04_voice/step1_detailed_responses/plato__theme_*.json` — `thinking_tokens=0` confirmed
- `/tmp/voice_dryrun_2026_04_29_v3.log` — full run log

---

## What this brief is NOT

- Not a diagnosis (we don't know if thinking is off across personas — Task 1 answers that)
- Not a recommendation to change anything yet (only Task 3 does, as a single-pass test)
- Not a critique of the existing pattern (which works at the API level — established by ~30+ production call sites)

It's an **investigation request**, scoped to: figure out the actual state, decide whether action is warranted, file a follow-up if so.

---

## Task 1 RESULT — empirical diagnostic 2026-04-29 22:00

Ran `/tmp/anthropic_thinking_diagnostic.py` — 3 calls to claude-opus-4-7 with persona-pipeline-shaped Hannah Arendt Pass-2 system+user (~2K tokens, smaller than production but representative shape):

| Config | thinking_tokens | trace_chars | wall_s |
|---|---|---|---|
| **A** Current production: `{thinking: {type: adaptive}, temperature: 1.0}` | **0** | **0** | 48.2 |
| **B** `+ thinking.display: summarized` | **0** | **0** | 41.6 |
| **C** `+ output_config.effort: high` | **0** | **167** | 41.0 |

**Findings:**

1. ✅ **SDK 0.94.1 supports `output_config` natively** — Task 4 resolved. No SDK bump needed; can pass `output_config={"effort": "high"}` directly.
2. ❌ **Default adaptive: 0 thinking** on this prompt shape. Matches Voice Pipeline empirical observation.
3. ❌ **`display: summarized` alone doesn't change adaptive's decision** — it's a visibility-flag, not a thinking-trigger.
4. ⚠️ **Even `effort: high` produced only a 167-char single-sentence preamble** ("I'm going to create ten fields..."). Not extended reasoning. Adaptive interpreted the synthesis-shaped task as not needing deep thinking even when explicitly pushed.

**Caveats:**
- `thinking_tokens=0` consistently across all 3 configs — may be SDK 0.94.1 usage-reporting limitation; thinking may billed under `output_tokens` rather than separately exposed. Worth verifying with raw API JSON before drawing strong conclusions about token-spend.
- Test input was ~2K tokens (smaller than production ~30K). Persona-pipeline-real prompts MAY engage adaptive more, though the Voice Pipeline ~30K observation suggests not.
- Synthesis-shaped tasks (Pass 2 card-build) may genuinely not benefit from thinking. Reasoning-heavy passes (Pass 4b artifact selection, Pass 7a critic) may be different.

**Decision points for operator:**

- The brief's hypothesis is empirically supported: persona pipeline has been running effectively without extended thinking.
- The 9480d3a revert hypothesis (cumulative-directives-dominate-without-thinking) stays alive as a candidate explanation for the texture-loss empirical.
- Pre-Athens: shipped Plato + Cleopatra were built without thinking; both chat-tested fine. The cost of NOT thinking is invisible (we don't know what the cards would have looked like under thinking). The cost of switching now is: re-running 2 shipped voices + 8 remaining = 10 voices × ~$5-10 effort-high cost differential = $50-100 + hours of operator time.

**Next steps (require operator decision, not autonomous):**
- **Task 2 (impact eval):** are shipped Plato/Cleopatra plausibly thinking-deficient, or did the prompts compensate? Subjective; needs chat-test comparison if Task 3 lands.
- **Task 3 (single-pass test):** patch one production call site to use `effort: high` + `display: summarized`; re-run a single Pass on a representative voice; compare output quality. ~$5, ~10 min.
- **Task 5 (NEW, post-Task-1):** verify `thinking_tokens` reporting in SDK 0.94.1 — is it actually 0, or unsurfaced? May change the conclusion. ~30 min investigation.

---

## Task 1 + 5 RESULT — full diagnostic 2026-04-29 22:30 (this thread)

Ran `/tmp/anthropic_thinking_truth.py` — 6 tests covering all 5 of the other thread's hard findings + raw usage inspection.

### Definitive table (block_types is the ground truth, not `thinking_tokens` which doesn't exist)

| Test | block_types | trace_chars | output_tokens | Verdict |
|---|---|---|---|---|
| T1 manual `{type:enabled, budget:8000}` | ❌ 400 | — | — | Manual REJECTED on 4.7 |
| T2 adaptive + temp=1.0 (production) + REASONING | `['text']` | 0 | 1638 | NO thinking |
| T3 adaptive, NO temp + REASONING | `['text']` | 0 | 1483 | NO thinking — temp NOT the issue |
| T4 + display=summarized + effort=max + REASONING | `['thinking','text']` | **2188** | 3643 | thinking engaged |
| T5 + display=summarized + effort=max + SYNTHESIS | `['thinking','text']` | 672 | 2059 | thinking engaged less |
| T6 + temp=1.0 + effort=max + REASONING | `['thinking','text']` | **2112** | 4045 | temp=1.0 does NOT break thinking |

### Settled questions

1. ✅ **Manual `{type:"enabled"}` REJECTED on Opus 4.7.** Exact API error: *`"thinking.type.enabled" is not supported for this model. Use "thinking.type.adaptive" and "output_config.effort"`*. The other thread's claim was correct.
2. ✅ **`output_config.effort` is the lever that engages thinking.** Without it (default effort), adaptive declines to think on BOTH synthesis AND reasoning prompts — even when the user prompt explicitly says "show your reasoning."
3. ❌ **`thinking_tokens` is NOT a field in SDK 0.94.1 usage.** Available fields: `input_tokens`, `output_tokens`, `cache_creation_input_tokens`, `cache_read_input_tokens`, `cache_creation`, `inference_geo`, `service_tier`. Voice pipeline's `thinking_tokens=0` came from `getattr(usage, "thinking_tokens", 0)` returning `0` because attribute doesn't exist. **The real metric is `block_types` — `['text']` alone = no thinking; `['thinking', 'text']` = thinking engaged.** Token-level metric: thinking is rolled into `output_tokens` (T4 - T2 = 2005 token diff = the ~2188-char thinking trace).
4. ❌ **Temperature=1.0 is FINE — does NOT break thinking.** T6 with temp=1.0 + effort=max produced 2112-char trace. Bedrock docs claim was wrong/stale. The 30+ production call sites with `temperature=1.0` continue to work.
5. ❌ **`display: summarized` is a visibility flag, NOT a thinking trigger.** Setting display alone without effort still produces zero thinking. Sending display=summarized when effort engages thinking gives you visible trace; when adaptive declines, gives you nothing extra.
6. ✅ **Effort hierarchy works as documented.** `effort: max` engages thinking even on synthesis-shaped tasks (T5: 672 chars). For reasoning tasks: substantial trace (T4/T6: 2100+ chars).

### Empirically settled hypothesis

**~30+ Opus 4.7 call sites across persona + runtime + voice pipelines have been running without engaging extended thinking.** The default-effort + adaptive config silently defaults to text-only on persona-shape prompts. This is consistent across:
- Voice Pipeline dry-run on Plato (3 calls, all text-only)
- This diagnostic's T2/T3 on reasoning + synthesis prompts

### Minimum architectural fix to engage thinking

Three lines per call site:
```python
"thinking": {"type": "adaptive", "display": "summarized"},
"output_config": {"effort": "high"},  # or "xhigh" for reasoning-heavy / "max" for critic
```

NO code change required for:
- Temperature settings (work fine)
- SDK version (0.94.1 supports it natively)
- Manual mode (don't use; rejected on 4.7)

### Connection to 9480d3a revert hypothesis (re-evaluated)

The cumulative-prompt-additions-degrade-texture finding from 04-28 likely was partly compensating for missing reasoning bandwidth. With thinking ON, the model has reasoning bandwidth to balance multiple directives simultaneously; without, each directive dominates one slot in output.

**Implication for FU#49A / cryofreeze / family-of-forms / FU#56 register-discipline:** the 04-28 revert was empirically right under THEN-active config (no thinking). Under thinking-on, the same revert finding may not hold — re-attempting the framework additions AFTER landing thinking might produce different empirical results.

**This is a meaningful pre-Athens decision point** — distinct from the binary "should we land thinking" question.

### Operator decision points (final, post-empirical-truth)

1. **Land thinking on the persona pipeline pre-voice-4?** (Octopus + 7 voices)
   - Cost: ~1-2 hr code edit + first-voice empirical chat-test compare
   - Reward: voices 4-10 built with thinking = potentially better Athens output
   - Risk: ANY change to call config could shift texture in unexpected directions; chat-test would surface
   - Trade: re-running shipped Plato + Cleopatra under thinking-on = ~$50-100 + ~30 min wall

2. **Land thinking on the runtime pipelines (researcher / provocateur / voice)?**
   - These run AT Athens, not pre-build. Cost is per-Athens-run (~$200-300 extra in Opus thinking tokens × 3 nights).
   - Reward: better runtime artifact quality on the night.
   - Risk: same as above — ANY config change should be A/B-tested first.

3. **Re-evaluate 9480d3a revert under thinking-on?**
   - Hypothesis: framework additions (FU#49A v1 / cryofreeze / family-of-forms / FU#56 register-discipline) might not degrade texture when thinking is on.
   - Test: re-land FU#49A v1 + chat-test on Plato under thinking-on. If clean, re-land the rest.
   - Scope: substantial — but might genuinely be the right pre-Athens move if thinking is the missing ingredient.

4. **Backfill `LLM_CALL_INVENTORY.md`** with `effort` + `display` columns + observed `block_types`.
