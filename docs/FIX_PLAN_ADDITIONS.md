# Fix plan additions

**Purpose:** Net-new items discovered after the fork diverged, plus the two directives received 2026-04-18: (a) remove remaining `Opus 4.6` references, (b) use extended/adaptive thinking everywhere `claude-opus-4-7` is called. Keep this file separate from the fork's original fix plan so it's clear what's new.

---

## 1. NEW FINDING — Pass 0a thinking comment is a lie

**File:** `personas/run_pass0a_voice_config.py` L169-176
**Severity:** Low-medium (silently weaker Pass 0a output; not a crash)
**Discovered:** 2026-04-18 while writing `docs/LLM_CALL_INVENTORY.md`
**Not in the fork's fix plan.**

### What the code does

```python
_call_kwargs = dict(
    system=system,
    model="claude-opus-4-7",
    max_tokens=24000,
    temperature=1.0,
    thinking_budget=None,  # adaptive thinking
    response_format_json=True,
)
```

### What actually happens

`call_claude` in `personas/flows/shared/clients.py` L46-52:

```python
if thinking_budget:
    kwargs["thinking"] = {"type": "adaptive"}
```

`thinking_budget=None` is falsy, so the `thinking` kwarg is **not added**. Pass 0a runs on Opus 4.7 with thinking **off**, despite the comment.

### Why this matters

Pass 0a produces the voice config that seeds all downstream research. The whole point of running Opus 4.7 instead of Sonnet at this step is to get better editorial judgment on `voice_mode`, `hostile_sources`, `corpus_constraint` classification. Without thinking, Opus 4.7 is giving a first-thought-best-thought classification — which is roughly what Sonnet would do at 1/5 the cost.

### Fix

Change L174 to either:

```python
thinking_budget=10000,  # adaptive thinking (budget value ignored under adaptive mode)
```

Or (clearer — eliminates the confusing `budget` semantics):

```python
thinking_budget=10000,  # truthy value enables adaptive thinking per clients.py
```

Alternatively: refactor `call_claude` to accept `thinking="adaptive"` directly and remove the `thinking_budget` pseudo-parameter entirely. That's a bigger change; see §4.

### Verify after fix

```bash
# Should see "thinking" kwarg in the call
python3 -c "from personas.run_pass0a_voice_config import _call_kwargs; print(_call_kwargs)"
```

Check a run: Pass 0a latency should jump from ~15s to 60-120s (thinking visible in `usage.output_tokens` including thinking tokens).

---

## 2. Directive — remove remaining `Opus 4.6` references

The main refactor was commit `35bc8fd` (2026-04-17). Audit as of 2026-04-18:

### Already clean ✅

- **All Python code**: `grep -rn "claude-opus-4-6" --include="*.py" personas/ runtime/` returns 0 matches.
- **All main spec docs in `docs/*.md`**: clean. All 7 pipeline specs + CURRENT_STATE + README.
- **Top-level configs**: `.env.example`, `runtime/.env.example`, `personas/.env.example` — all on 4.7.

### Remaining references — two categories

**Category A: touch — stale current-tense references that should read 4.7**

| File | Lines | Context | Action |
|---|---|---|---|
| *(none in code paths)* | — | — | — |

**No current-tense code or spec references remain.** The 35bc8fd commit caught them all.

**Category B: leave — historical records**

These intentionally reference Opus 4.6 because they describe the state *at the time*. Editing them would rewrite history.

| File | Why it's historical |
|---|---|
| `runtime/notes/updated_specs/TRANSCRIPTION_v2_to_v2_1_delta.md` | "v2.1 delta" describing a refactor that landed on Opus 4.6. Record of what the refactor was at the time. |
| `runtime/notes/updated_specs/RESEARCHER_v2_to_v3_delta.md` | Same shape — v3 delta, historical record. |
| `runtime/notes/updated_specs/PROVOCATEUR_v1_to_v2_delta.md` | Same shape. |
| `personas/notes/SONNET_EXECUTION_PLAN.md` | Explicitly the plan for the 4.6 → 4.7 rename (task A.2). Now historical. |
| `personas/notes/WALKTHROUGH_FIXES_PENDING.md` | Pending-fixes doc that predated the rename. Task 1 is "Model rename: Opus 4.6 → Opus 4.7". Now done. |
| `personas/notes/baseline_research/compass_artifact_*.md` | Commissioned research docs that pre-dated the repo. Reference Opus 4.6 because that's what was current. |
| `personas/runs/**/*.json` | Persona card outputs — record of what model actually ran. MUST NOT be edited. |
| `runtime/runs/**/manifest.json` | Run manifests — record of what model actually ran. MUST NOT be edited. |

**Recommendation:** leave Category B alone. These are the project's memory.

**Optional polish (low priority):** the three delta docs in `runtime/notes/updated_specs/` could gain a one-line banner at top:

```markdown
> **Historical note:** This delta describes the transition to Opus 4.6. The current pipeline runs on Opus 4.7 (commit 35bc8fd, 2026-04-17). Content preserved as-is for traceability.
```

Same for the two personas planning docs. Only bother if the Opus-4.6 references are confusing you when you re-read these files; otherwise skip.

---

## 3. Directive — extended/adaptive thinking ON for every Opus 4.7 call

### Audit of all Opus 4.7 call sites

Read `docs/LLM_CALL_INVENTORY.md` for the full enumeration. Opus 4.7 call sites and their current thinking state:

| # | Call site | File:Line | Thinking state | Compliant with new rule? |
|---|---|---|---|---|
| 4 | Researcher Extraction | `runtime/flows/researcher_flow.py:261` | Adaptive (if `RESEARCHER_THINKING≠0`, default on) | ✅ Yes |
| 5 | Researcher Clustering | `researcher_flow.py:323` | Adaptive (same toggle) | ✅ Yes |
| 6 | Researcher Theming | `researcher_flow.py:452` | Adaptive (same toggle) | ✅ Yes |
| 7 | Provocateur Triage Voice | `provocateur_flow.py:287` | Adaptive (if `PROVOCATEUR_THINKING=1`, default on) | ✅ Yes |
| 8 | Provocateur Triage Flags | `provocateur_flow.py:354` | Adaptive (same toggle) | ✅ Yes |
| 9 | Provocateur Formulation | `provocateur_flow.py:741` | Adaptive (same toggle) | ✅ Yes |
| 10 | Personas Pass 0a Voice Config | `personas/run_pass0a_voice_config.py:174` | **OFF** (thinking_budget=None) | ❌ **No — see §1** |
| 15 | Personas Pass 1-merge | `personas/run_persona_pipeline.py:132` | **OFF** (thinking_budget=None) | ❌ **No — see §3.1** |
| 19 | Personas Pass 2 Identity | `run_persona_pipeline.py:377` | Adaptive (via `_claude_pass` thinking=True) | ✅ Yes |
| 21 | Personas Pass 3 Intellectual Core | `run_persona_pipeline.py:393` | Adaptive | ✅ Yes |
| 23 | Personas Pass 4a Voice | `run_persona_pipeline.py:442` | Adaptive | ✅ Yes |
| 27 | Personas Pass 5 Engagement | `run_persona_pipeline.py:483` | Adaptive | ✅ Yes |
| 31 | Personas Pass 7b Worked Provocations | `run_persona_pipeline.py:758` | Adaptive | ✅ Yes |

**Not Opus 4.7 (skip for this directive):**
- All Sonnet 4.6 calls (coherence threading, 1c-extract, 1d, 4b, 6, 7-pre, 7c-fallback, Derive, Speaker ID default, Cleaning default)
- All non-Anthropic calls (Perplexity, Gemini, OpenAI o3/gpt-4o)

### Two current violations to fix

#### 3.1 Pass 1-merge — Opus 4.7, thinking off

**File:** `personas/run_persona_pipeline.py` L126-141

```python
def _pass_1merge():
    sysp = load_prompt("persona_pass_1merge_contradiction_system").strip()
    userp = render("persona_pass_1merge_three_way_user",
                   perplexity_dossier=dossier_text,
                   claude_dr_dossier=claude_dr_text or None,
                   gemini_broad_scan=broad_scan_text)
    r = call_claude(system=sysp, user=userp, model="claude-opus-4-7",
                    max_tokens=16000, temperature=0.0, thinking_budget=None,  # ← thinking off
                    response_format_json=True)
```

The task is 3-way contradiction detection across large research dossiers. Thinking would help. But temperature=0.0 is set — and adaptive thinking requires temp=1.0 per Anthropic SDK's current constraint.

**Fix (two options):**

**Option A — enable thinking, bump temperature to 1.0:**
```python
r = call_claude(system=sysp, user=userp, model="claude-opus-4-7",
                max_tokens=16000, temperature=1.0, thinking_budget=10000,
                response_format_json=True)
```

**Option B — keep deterministic contradiction check, drop to Sonnet:**
```python
r = call_claude(system=sysp, user=userp, model="claude-sonnet-4-6",
                max_tokens=16000, temperature=0.0, thinking_budget=None,
                response_format_json=True)
```

Option A applies your new rule. Option B preserves determinism (a contradiction-check task arguably wants reproducibility more than creative reasoning).

**Recommendation:** Option A, since the directive is "thinking everywhere Opus 4.7 is used." If you later observe that temp=1.0 is destabilizing the JSON output, fall back to Option B.

#### 3.2 Pass 0a Voice Config — Opus 4.7, thinking off

Already covered in §1 above. Same fix.

### Three conflicts with existing specs — flag before applying

**3.3 Transcription Speaker ID — spec says NO thinking on Opus**

`docs/AI_Assembly_Transcription_Pipeline.md` L340-361 explicitly states:

> **Thinking mode is NOT used in Transcription** even when Opus is selected. The Speaker ID output is small (mappings + flags, under 2K tokens), so the latency cost of adaptive thinking is large relative to its benefit.

Current code in `runtime/flows/transcription_flow.py:409-414` (Speaker ID):

```python
resp = client.messages.create(
    model=SPEAKER_ID_MODEL,  # default Sonnet; override to Opus 4.7 via env
    max_tokens=4096,
    system=SPEAKER_ID_SYSTEM,
    messages=[{"role": "user", "content": user}],
)
```

No thinking. Uses non-streaming `messages.create` with `max_tokens=4096`.

**What your new rule implies:** If a user sets `TRANSCRIPTION_SPEAKER_ID_MODEL=claude-opus-4-7`, thinking should turn on.

**What the spec says:** Don't turn on thinking for this call even on Opus — latency not worth it.

**Decision to make:**
- **Apply new rule uniformly** → modify Speaker ID to enable adaptive thinking when model is Opus, and update the transcription spec to remove the "no thinking" carve-out.
- **Keep the carve-out** → accept that Speaker ID is an intentional exception to the "thinking everywhere Opus 4.7" rule, and document it as such in `docs/LLM_CALL_INVENTORY.md` §7.

Recommended: **keep the carve-out**. The spec's reasoning is correct — for a small-output structured task, thinking buys latency, not quality. But make the exception explicit by adding a comment in `transcription_flow.py` near the Speaker ID call, and note it in the inventory spec.

**3.4 Transcription Cleaning — spec says NO thinking, even on Opus via CLAUDE_MODEL override**

Same spec section:

> **Cleaning and semantic drift verification remain on the default model (Sonnet).** Cleaning is the largest LLM call in the whole overnight pipeline by output volume and its judgment work is mostly local per turn, not cross-turn synthesis, so thinking adds little.

Current code in `transcription_flow.py:447-456` uses `CLAUDE_MODEL` (Sonnet default), no thinking. If someone sets `CLAUDE_MODEL=claude-opus-4-7`, Cleaning would run on Opus without thinking.

**Same decision as §3.3.** Recommended: keep the carve-out. The spec's reasoning is explicit and valid. Document as exception.

**3.5 Semantic drift verification (Transcription Node 4) — currently not built**

The v2.1 spec mentions a "drift verification" quality-gate call on Sonnet. Not implemented in code (no `drift_check` task in `transcription_flow.py`). If this gets built later and someone runs it on Opus, the rule kicks in. Flag for future reference.

---

## 4. Optional cleanup — refactor `call_claude`'s thinking parameter

Not urgent, but the confusion in §1 was caused by `thinking_budget` being misleadingly named. Anthropic's `adaptive` mode doesn't use a budget — the budget is ignored.

### Current shape (`personas/flows/shared/clients.py` L20-113)

```python
def call_claude(
    *,
    system: str,
    user: str,
    model: str | None = None,
    max_tokens: int = 8192,
    temperature: float = 0.2,
    thinking_budget: int | None = None,  # ← misleadingly named
    response_format_json: bool = False,
) -> dict[str, Any]:
    ...
    if thinking_budget:
        kwargs["thinking"] = {"type": "adaptive"}
```

### Proposed shape

```python
def call_claude(
    *,
    system: str,
    user: str,
    model: str | None = None,
    max_tokens: int = 8192,
    temperature: float = 0.2,
    thinking: bool = False,  # ← explicit
    response_format_json: bool = False,
) -> dict[str, Any]:
    ...
    if thinking:
        kwargs["thinking"] = {"type": "adaptive"}
```

Updates required at call sites (in `personas/` only; runtime flows don't use this wrapper):
- Pass 0a L174: `thinking_budget=None` → `thinking=True` (per §1 fix)
- Pass 1-merge L132: `thinking_budget=None` → `thinking=True` (per §3.1 fix)
- Pass 1c-extract L211: `thinking_budget=None` → `thinking=False` (unchanged; already off)
- Pass 1d L419: `thinking_budget=None` → `thinking=False` (unchanged)
- Pass 7-pre L540: `thinking_budget=None` → `thinking=False` (unchanged; Sonnet)
- Pass 7c fallback L796: `thinking_budget=None` → `thinking=False` (unchanged; Sonnet)
- Derive L831: `thinking_budget=None` → `thinking=False` (unchanged; Sonnet)
- CT `_ct_compress` L365: `thinking_budget=None` → `thinking=False` (unchanged; Sonnet)
- `_claude_pass` wrapper L345: adjust `thinking=thinking` parameter to pass through directly instead of translating to `thinking_budget`

Also clean up: `PERSONA_THINKING_BUDGET` documented in `.env.example` but unused — either implement it or remove.

**Decide after §1 and §3.1 fixes land.** The rename is low-value but eliminates recurrence of the bug class.

---

## 5. Summary of actions

In priority order:

1. **Apply fix §1 / §3.2 — Pass 0a thinking on.** One line in `run_pass0a_voice_config.py`. Smoke test: run Pass 0a for any voice, verify latency and token usage both increase.
2. **Apply fix §3.1 — Pass 1-merge thinking on.** Two lines (`temperature=1.0` + truthy thinking budget). Smoke test: re-run Pass 1-merge on any voice with a cached dossier; verify JSON still parses.
3. **Decide §3.3, §3.4 — Transcription exceptions.** Recommended: keep the carve-out, document the exception in both `LLM_CALL_INVENTORY.md` and `transcription_flow.py` comments.
4. **Optional — historical doc banners (§2 Category B).** Only if Opus-4.6 references are confusing you on re-read.
5. **Optional — `call_claude` refactor (§4).** Low priority; eliminates recurrence of the class of bug that produced §1.

No run-artifact edits. No spec edits for Opus 4.6 in the delta/notes docs (historical).

---

*Separate from the fork's original fix plan. Net-new as of 2026-04-18.*
