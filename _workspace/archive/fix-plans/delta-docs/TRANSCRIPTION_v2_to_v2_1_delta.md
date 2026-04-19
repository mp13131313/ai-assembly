# TRANSCRIPTION PIPELINE — v2 → v2.1 Delta

> **Historical note:** This document describes the transition to Opus 4.6. The current pipeline runs on Opus 4.7 as of commit 35bc8fd (2026-04-17). Content preserved as-is for traceability.

**Target document:** `AI_Assembly_Transcription_Pipeline.md`
**From:** v2 (Apr 14 2026, post-Level-2 validation)
**To:** v2.1 (Apr 14 2026, post-Researcher v2.4 cross-check)
**Status:** Single additive change — a per-step model override for Speaker ID

---

## Summary

Researcher Pipeline v2.4 validated Opus 4.6 with adaptive extended thinking as a meaningful quality improvement for the editorial-synthesis layer (clustering, theming). That benefit does NOT generalize to the Transcription Pipeline's main steps:

- **Cleaning** stays on Sonnet. It is the largest LLM call in the overnight pipeline by output volume (~18K tokens on the biggest test session). The judgment work is mostly local per turn, not cross-turn synthesis, so thinking adds little. Cost/benefit wrong.
- **Semantic drift verification** stays on Sonnet. It is a short quality-gate check on raw/cleaned pairs, not a reasoning task.
- **Speaker ID** is the only step where Opus could plausibly help — the 5-pass re-attribution logic is reasoning-heavy, and edge cases (non-native English, complex Q&A, incomplete roster metadata) could benefit from the extra capacity. But Sonnet is already hitting 100% high-confidence on all three Level 2 test sessions, so the marginal benefit is small on normal sessions.

The v2.1 resolution: add an optional environment variable to override the Speaker ID model on a per-run basis without code changes. Default stays Sonnet. Athens operators can flip a difficult session to Opus by setting `TRANSCRIPTION_SPEAKER_ID_MODEL=claude-opus-4-6` for that run.

No thinking anywhere in Transcription by default. The combined reasoning + latency + cost tradeoff doesn't favor it at this layer.

---

## Changes

### §14 — Changelog entry for v2.1

**Location:** Top of the Changelog section, add a new entry immediately after the v2 (Apr 14 2026) block.

**New text:**

```markdown
## Changelog (v2.1 — Apr 14 2026)

A single additive change from v2, in response to validating Opus 4.6 + adaptive thinking on the Researcher Pipeline (v2.4). The Researcher upgrade produced a large quality improvement for clustering and theming but did not generalize to the Transcription Pipeline's main LLM calls (Cleaning, drift verification). Speaker ID was the only Transcription step where Opus could plausibly help edge cases, so it gains a per-run model override.

- **§14** → Step 3 "Speaker Identification" implementation gains an optional `TRANSCRIPTION_SPEAKER_ID_MODEL` environment variable. Defaults to `CLAUDE_MODEL` (i.e. Sonnet 4.6 in the baseline config). Can be set to `claude-opus-4-6` on a per-run basis for difficult sessions — non-native English speakers, complex multi-person Q&A, incomplete roster metadata. Cleaning and semantic drift verification remain on Sonnet; the cost/benefit does not favor Opus for those steps.

Model references throughout the document are unchanged — Sonnet 4.6 remains the default for every LLM call in Transcription.
```

### §14 part A — Add "Model selection" subsection to Step 3

**Location:** Inside `## Step 3: Speaker Identification`, add a new subsection at the end (after the existing "Alternatives considered" subsection from v2 §13).

**New text:**

```markdown
### Model selection — default Sonnet, optional Opus for difficult sessions

The Speaker ID LLM call defaults to Claude Sonnet 4.6. Across the three MSC 2026 Level 2 test sessions, Sonnet 4.6 produced 100% high-confidence attributions with 5-pass re-attribution catching real edge cases (Mustafa Barghouti self-introduction in Breaking Point, 15 audience-member reassignments across 8 flags in West-West Divide). The baseline is sufficient for well-behaved conference audio.

For difficult sessions, operators can override the Speaker ID model per-run via the `TRANSCRIPTION_SPEAKER_ID_MODEL` environment variable:

```bash
TRANSCRIPTION_SPEAKER_ID_MODEL=claude-opus-4-6 python flows/transcription_flow.py ...
```

When to flip this toggle:

- **Non-native English speakers with heavy accents** — where the ASR's vocabulary and the transcription text diverge in ways that make name-to-role correlation harder
- **Complex multi-person Q&A** — when the open question period has 5+ distinct audience members on similarly-positioned microphones (the Q&A audience-merging problem documented in §6), and Pass 5 needs to make confident distinctions across many short turns
- **Incomplete roster metadata** — when the program lists contributors but the bios are thin or the title/affiliation fields are missing, giving Pass 1 less signal to match against
- **Mixed-language sessions** — where speakers switch between English and another language and the Speaker ID pass needs to reason across the language boundary

Opus 4.6's extra reasoning capacity helps on these edge cases. It does NOT help on well-behaved sessions and costs ~5× more per call, so it should not be the default.

**Thinking mode is NOT used in Transcription** even when Opus is selected. The Speaker ID output is small (mappings + flags, under 2K tokens), so the latency cost of adaptive thinking is large relative to its benefit. The Speaker ID call stays non-streaming with `max_tokens=4096` regardless of model choice.

**Cleaning and semantic drift verification remain on the default model (Sonnet).** Cleaning is the largest LLM call in the whole overnight pipeline by output volume and its judgment work is mostly local per turn, not cross-turn synthesis, so thinking adds little. Drift verification is a short quality-gate check, not a reasoning task. Neither benefits from the Opus upgrade and both incur significant cost increase if flipped.
```

### §14 part B — Note the env var in the Implementation Draft config block

**Location:** In the Implementation Draft section where the Speaker ID node's runtime config is specified, add the env var reference.

**Find the existing Speaker ID config block (around the Node 3 / "Speaker Identification" implementation section) and update it.**

**Old text (approximately):**

```markdown
**Runtime config:** `model="claude-sonnet-4-6"`, `max_tokens=4096`, non-streaming.
```

**New text:**

```markdown
**Runtime config:** `model` defaults to `CLAUDE_MODEL` env var (baseline: `claude-sonnet-4-6`), overridable via `TRANSCRIPTION_SPEAKER_ID_MODEL` env var for per-run model selection; `max_tokens=4096`; non-streaming. See "Model selection" subsection above for when to override the default.
```

---

## Code changes already applied

For reference — the corresponding code changes in `flows/transcription_flow.py` are already in place as of Apr 14 2026:

1. New config constant after `CLAUDE_MODEL` definition:

```python
# Optional per-step model override for Speaker ID. Defaults to
# CLAUDE_MODEL (Sonnet in the baseline config). Set to
# "claude-opus-4-6" for difficult sessions where the extra reasoning
# capacity helps — non-native English speakers, complex multi-person
# Q&A, incomplete roster metadata, or any session where Pass 5
# re-attribution has to do non-trivial work. Cleaning and semantic
# drift verification stay on CLAUDE_MODEL (Sonnet) — the cost/benefit
# does not favor Opus for those steps.
SPEAKER_ID_MODEL = os.environ.get(
    "TRANSCRIPTION_SPEAKER_ID_MODEL", CLAUDE_MODEL
)
```

2. The `identify_speakers` task now references `SPEAKER_ID_MODEL` instead of `CLAUDE_MODEL`:

```python
logger.info(f"Speaker ID pass (model={SPEAKER_ID_MODEL})")
...
resp = client.messages.create(
    model=SPEAKER_ID_MODEL,
    max_tokens=4096,
    ...
)
```

3. The `clean_transcript` task still uses `CLAUDE_MODEL` (unchanged). The drift verification task still uses `CLAUDE_MODEL` (unchanged).

Validated: `python3 -c "import flows.transcription_flow as t; print(t.SPEAKER_ID_MODEL)"` prints the default; setting `TRANSCRIPTION_SPEAKER_ID_MODEL=claude-opus-4-6` in the environment correctly overrides.

---

*Apply this delta in a single edit session to `AI_Assembly_Transcription_Pipeline.md`. The change is purely additive — no removals from v2 — so the upgrade is safe.*
