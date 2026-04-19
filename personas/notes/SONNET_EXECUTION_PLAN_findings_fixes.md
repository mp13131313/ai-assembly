# Sonnet Execution Plan — Apply All FRESH_REVIEW Findings

**Paste this into a fresh Claude Sonnet 4.6 session, medium effort. Self-contained.**

## Your task

Execute the P0–P3 fix list from
`docs/FRESH_REVIEW_2026_04_19.md` §8. Every actionable finding (F-01
through F-32) lands in commits here, phased by priority. All 29
runtime tests must still pass at the end. Do not run the
reorganization plan until this one lands — see §"Run order" at the
bottom.

## Preflight

1. Read in order:
   - `docs/FRESH_REVIEW_2026_04_19.md` §4 (the findings themselves),
     §8 (the prioritised action list this plan executes)
   - `personas/run_persona_pipeline.py` L380-400 (so you recognise
     Pass 3 context for F-27)
   - `docs/AI_Assembly_Persona_Pipeline_v3_10.md` L30-50 (the
     changelog whose claims must become consistent with the body in
     F-12 + F-29)

2. Baseline must be green BEFORE any fix:
   ```bash
   cd /Users/aienvironment/Desktop/ai-assembly
   git status                       # clean
   cd runtime && venv/bin/python -m pytest ingest/tests/ -v
   ```
   Must see 29/29. Stop and report if not.

3. Branch:
   ```bash
   cd /Users/aienvironment/Desktop/ai-assembly
   git checkout -b fix-review-findings
   ```

4. Starting-state context (this plan was written before commit `d1b8a2c`
   landed on 2026-04-19; that commit added review artifacts that DO NOT
   conflict with this plan but are worth knowing about):
   - `personas/notes/REBUILD_PLAN.md` exists (forward-looking Phase B
     plan). This plan does not edit it; F-13 (Phase B.5 below) only
     references it as a pointer for the voice_mode question.
   - `personas/notes/SESSION_REPORT_2026-04-19.md` exists (session
     report). Not edited by this plan.
   - `personas/notes/baseline_research/` now contains **5** compass_artifact
     files (the 5th is the Boddice biocultural critique). Earlier
     references to "4 baseline_research files" in the F-23
     personas/README rewrite (Phase F.1) and in CURRENT_STATE references
     are stale; defer the count update — the reorganization plan's
     Phase C.3 `docs/references.md` already accounts for 5.
   - All three artifacts move OUT of `personas/notes/` in the
     reorganization plan that runs AFTER this one. Leave them in
     place here.
   - The grep sweeps in Phase I.4 already exclude `personas/notes/`
     (via `| grep -v "personas/notes/\|..."`), so these files won't
     produce false positives.

---

## Phase A — URGENT: F-27 pipeline-blocker (ship alone, first)

**File:** `personas/flows/shared/prompts/persona_pass_3_user.md`

**Problem:** lines 3-6 reference `{% if chatgpt_supplement %}` but the
runner (`run_persona_pipeline.py`) no longer passes
`chatgpt_supplement` since commit `d137791` removed the Pass 3 DR
supplement. With `StrictUndefined` at
`personas/flows/shared/prompt_render.py:16`, Pass 3 crashes on every
new voice build:

```
UndefinedError: 'chatgpt_supplement' is undefined
```

**Fix:** delete the 4-line block. Current file:

```
Research Dossier:
{{ merged_dossier }}
{% if chatgpt_supplement %}

Supplementary Analysis:
{{ chatgpt_supplement }}
{% endif %}

Previously completed fields (summary):
{{ pass_2_summary }}
```

After fix:

```
Research Dossier:
{{ merged_dossier }}

Previously completed fields (summary):
{{ pass_2_summary }}
```

**Verify the fix before committing:**

```bash
cd personas && venv/bin/python -c "
import sys; sys.path.insert(0, '.')
from flows.shared.prompt_render import render
render('persona_pass_3_user', merged_dossier='mock', pass_2_summary='mock')
print('Pass 3 render: OK')
"
```
Must print "Pass 3 render: OK".

**Commit A:**
```bash
git add personas/flows/shared/prompts/persona_pass_3_user.md
git commit -m "$(cat <<'EOF'
fix(personas): unblock Pass 3 render after ChatGPT DR removal

commit d137791 removed the ChatGPT DR supplement from the Pass 3
runner but left the `{% if chatgpt_supplement %}` branch in the
user-prompt template. StrictUndefined raises on every render. No
voice has been built since that commit — fixing before the next one
lands.

Tested: persona_pass_3_user renders successfully with the runner's
actual kwargs (merged_dossier + pass_2_summary) after the fix.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

---

## Phase B — P0/P1 authoritative docs (correctness-first)

Edit in one commit. Each edit is precise, content-preserving except
where the content is wrong.

### B.1 F-03 — `docs/AI_Assembly_Persona_Card_v2.md` L413

Current: the Card spec's `worked_provocations` row says
`**Where it appears:** Step 1 only: "EXAMPLES — these show what your
thinking looks like in action."` This directly contradicts the
2026-04-15 decision that `worked_provocations` is build-time-only and
MUST NOT be loaded into the Voice Pipeline's Step 1 system prompt.

**Fix:** replace L413 "Where it appears" line with:

```
**Where it appears:** Build-time only (Persona Pipeline Pass 7b output).
**DO NOT load into Voice Pipeline Step 1 system prompt at runtime** —
this is a diagnostic / human-review artifact, not a few-shot exemplar.
Loading it collapses the voice's range and re-introduces failures
Pass 7c removes. See `personas/HANDOFF.md` §"CRITICAL: do NOT few-shot
from worked_provocations" and the `persona_pass_7b_provocations.md`
prompt header's ROLE CLARIFICATION (2026-04-15) for the full
reasoning.
```

### B.2 F-05 — `docs/LLM_CALL_INVENTORY.md` thinking_budget rename

The inventory's canonical parameter reference still describes
`call_claude`'s old parameter name. The K.0 refactor (commit
`4666fa1`) renamed it to `thinking: bool`.

**Fix:** find and replace each of these occurrences (excluding
`call_gemini` — its `thinking_budget` parameter is the Gemini-SDK
native one and stays):

- §3.1.1 L191 "thinking_budget=None → thinking is disabled" → rewrite
  to describe `thinking=True`/`thinking=False`
- §3.4.1 L244 "thinking_budget=None (thinking off)" → `thinking=False`
- §3.4.2 L252 `thinking_budget=None` → `thinking=False`
- §3.4.4 L265 same → same
- §3.5 L273-274 "`thinking_budget=10000` when `thinking=True` →
  triggers adaptive thinking via `clients.py` L46-52" → rewrite:
  "`thinking=True` enables adaptive thinking (no budget argument
  needed)"
- §3.5 L280 `thinking_budget=None` → `thinking=False`
- §3.6.1 L342 same → same
- §3.6.5 L383 same → same
- §3.7.1 L390 same → same
- §6.1 L479-487 — rewrite entire `call_claude` wrapper section to
  describe the current `thinking: bool = False` parameter. Keep the
  streaming-heuristic and JSON-extraction notes unchanged.
- L7 "Last read against the code: 2026-04-18" → "Last read against
  the code: 2026-04-19"

### B.3 F-06 — `LLM_CALL_INVENTORY.md §7` mark resolved

Current: `§7.1–7.5` describe discrepancies that were fixed 2026-04-18.
Only `§7.6` carries `*(resolved 2026-04-18)*`.

**Fix:** append `*(resolved 2026-04-18)*` to the end of each of
§7.1, §7.2, §7.3, §7.4, §7.5 subsection headings. Rename the
section from "Parameter discrepancies worth knowing" to "Historical
parameter discrepancies (all resolved)".

### B.4 F-12 — `docs/AI_Assembly_Persona_Pipeline_v3_10.md` §Pass 3

Current L386-393: describes a conditional ChatGPT DR supplement. The
feature was removed in commit `d137791`.

**Fix:** delete the entire "ChatGPT DR supplement (conditional)"
paragraph and its trigger-conditions list. Replace with:

```
**No Pass 3 supplement:** earlier versions of this pipeline (pre-v3.10)
fired a ChatGPT DR supplement on Pass 3 when the Phase 1 INTELLECTUAL
FRAMEWORK section was thin. That pre-step was removed in commit
`d137791` — the three-way merge (Perplexity + Claude DR + Gemini)
from Phase 1 now supplies the depth this supplement was compensating
for.
```

### B.5 F-13 — `docs/CURRENT_STATE.md` §5.12

Current: "§5.12 `voice_mode` is now freeform (commit `b1868da`)."

That claim is false. Commit `4c5c366` ("restore strict voice_mode
validation") reverted it. Live-verified — strict 3-value enum is
current.

**Fix:** rewrite §5.12 in full:

```
### 5.12 `voice_mode` validation — strict 3-value enum

**Current:** {philosophical, observational, narratival}, with null
allowed only for `subtype: "system"` voices (system entities bypass
voice_mode branching entirely).

**History:** commit `b1868da` (2026-04-16) briefly relaxed this to
freeform string to accommodate Pass 0a proposing creative per-voice
modes (`sovereign-diplomatic`, `embodied-distributed`, etc.). Commit
`4c5c366` (restore strict voice_mode validation) reverted that —
downstream prompt branching in Passes 2-5 depends on the fixed
three-value enum; freeform modes broke prompt rendering for any voice
Pass 0a proposed a novel mode for.

**Enforcement:** `personas/flows/shared/node0_validation.py:60`.

**Open question for Phase B:** whether to expand the enum is
`REBUILD_PLAN.md §Cross-cutting §"Decision: keep `voice_mode` 3-enum
or expand?"`. Default for now: keep the 3-enum.
```

### B.6 F-16 — `docs/AI_Assembly_Provocateur_Pipeline.md` L384

The sample `narrative_briefing` footer example still shows the old
`` `structured` `` field name. The runtime code already emits
`` `full_theme_record` ``.

**Fix:** in L383-385, change `` is available in the `structured` field
of this briefing entry `` to `` is available in the `full_theme_record`
field of this briefing entry ``.

### B.7 F-29 — `docs/AI_Assembly_Persona_Pipeline_v3_10.md` body model assignments

The changelog at L35-48 correctly says "MODEL: Upgraded all Opus calls
to claude-opus-4-7 (Pass 0a, 0b, 2, 3, 4a, 5, 7b; research flows)."
But the spec body still shows Sonnet.

**Fix each pass body:**

- L1289 Pass 3 "API: Claude Sonnet 4.6 (or Opus)" →
  "API: Claude Opus 4.7 with `thinking.type=adaptive`"
  "Config: `temperature: 1.0`, `max_tokens: 24000`, adaptive thinking"
- L1446 Pass 4a "API: Claude Sonnet 4.6. Config: `temperature: 0.3`,
  `max_tokens: 6144`" → "API: Claude Opus 4.7 with
  `thinking.type=adaptive`. Config: `temperature: 1.0`,
  `max_tokens: 24000`, adaptive thinking"
- L1648 Pass 5 "API: Claude Sonnet 4.6... Extended Thinking enabled
  (budget: 10000 tokens)" → "API: Claude Opus 4.7 with
  `thinking.type=adaptive`. Config: `temperature: 1.0`,
  `max_tokens: 16000`, adaptive thinking"
- Find Pass 2 body (the section starting around L1131 per fresh
  review). Update model + config similarly.
- Find Pass 7b body. Update to Opus 4.7 + adaptive thinking.
- Pass 4b (L1573-ish), Pass 6, Pass 7-pre stay on Sonnet — the
  changelog didn't upgrade those. Verify by checking the runner's
  `_pass_4b`, `_pass_6`, `_pass_7pre` in `run_persona_pipeline.py`.

**Verify after B.1-B.7:**

```bash
grep -n "thinking_budget" docs/LLM_CALL_INVENTORY.md | grep -v "call_gemini"
# Should return 0 hits

grep -n "freeform" docs/CURRENT_STATE.md
# Should not mention voice_mode freeform claim

grep -n "structured.*field of this briefing" docs/AI_Assembly_Provocateur_Pipeline.md
# Should return 0 hits (the only occurrence we fixed)

grep -n "chatgpt_supplement\|ChatGPT DR supplement (conditional)" docs/AI_Assembly_Persona_Pipeline_v3_10.md
# Should return 0 hits in body (the changelog entry at L30 about removal is fine)
```

**Commit B:**
```bash
git add docs/
git commit -m "$(cat <<'EOF'
docs(P0/P1): correct authoritative specs per FRESH_REVIEW findings

- F-03 Persona Card v2 L413 — worked_provocations is build-time only,
  NOT a runtime Step 1 few-shot. Explicit warning + pointers to the
  4 authoritative sources documenting the 2026-04-15 decision.
- F-05 LLM_CALL_INVENTORY — rename thinking_budget to thinking: bool
  throughout the call_claude references (K.0 refactor, commit 4666fa1).
  Gemini's native thinking_budget preserved.
- F-06 LLM_CALL_INVENTORY §7 — mark historical parameter
  discrepancies as resolved 2026-04-18.
- F-12 v3.10 spec Pass 3 — remove ChatGPT DR supplement paragraph
  (feature removed in commit d137791).
- F-13 CURRENT_STATE §5.12 — voice_mode is NOT freeform; strict
  3-enum restored by commit 4c5c366. Rewrite with full history.
- F-16 Provocateur spec L384 — `structured` → `full_theme_record`
  in narrative_briefing footer example.
- F-29 v3.10 spec body — update Passes 2, 3, 4a, 5, 7b to Opus 4.7
  + adaptive thinking per the v3.10 changelog that already recorded
  the migration.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

---

## Phase C — v3.7 reference sweep

Six locations in production docs still say "v3.7 Persona Card" / "v3.7
spec". All should be v3.10.

### C.1 Edits

- `docs/AI_Assembly_Briefing_v3_1.md` L283: "Persona Pipeline v3.7" →
  "Persona Pipeline v3.10"
- `docs/AI_Assembly_Provocateur_Pipeline.md` L75, L89, L404, L455 —
  four "v3.7 Persona Card" → "v3.10 Persona Card"
- `docs/AI_Assembly_Voice_Pipeline.md` L52: "The v3.7 Persona Card
  includes…" → "The v3.10 Persona Card includes…" (content otherwise
  correct — don't touch)
- `personas/HANDOFF.md` L12: "(all the v3.7 spec's fields, flat)" →
  "(all the v3.10 spec's fields, flat)"
- `personas/HANDOFF.md` L76: "a properly built v3.7 card" →
  "a properly built v3.10 card"
- `runtime/flows/shared/council/README.md` — any "v3.7 Persona Card"
  references in the "Stubs vs real profiles" section

### C.2 Verify

```bash
grep -rn "v3\.7 Persona Card\|v3\.7 Persona Pipeline\|v3\.7 spec" \
  docs/ README.md CLAUDE.md runtime/ personas/ \
  --include="*.md" \
  | grep -v "personas/notes/\|runtime/notes/\|_archive\|IMPLEMENTATION_AUDIT_v3_7\|changelog\|Changelog"
# Should return 0 or only references in changelog-style historical entries
```

### C.3 Commit C

```bash
git add docs/ personas/ runtime/
git commit -m "$(cat <<'EOF'
docs: update remaining v3.7 → v3.10 references

Surviving v3.7 references in production docs (Briefing, Provocateur
spec ×4, Voice Pipeline spec, HANDOFF ×2, council README) updated to
v3.10. Changelog entries in the v3.10 spec itself are preserved as
historical record.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

---

## Phase D — n8n reference sweep

Orchestration is Prefect + FastAPI; n8n references in current specs
are stale from the pre-merge era.

### D.1 Edits

- `docs/AI_Assembly_Persona_Card_v2.md` L867 "n8n routing" →
  "orchestration layer" (F-04)
- `docs/AI_Assembly_Transcription_Pipeline.md` (F-07):
  - §Step 1 Storage at L63-86: rewrite around `runtime/ingest/`
    FastAPI upload flow. Drop rclone/Drive-mount narrative. Point at
    `runtime/ingest/deploy/README.md` for the actual deployment path.
  - §Step 1 "Trigger and processing" L148-156: replace with brief
    description of the FastAPI upload route + detached subprocess
    spawn model per `runtime/ingest/pipeline.py`.
  - §Implementation Draft L508 "the existing n8n flow picks them up"
    → "the Researcher flow picks them up via `researcher_flow.py`"
- `docs/AI_Assembly_Persona_Pipeline_v3_10.md` (F-08):
  - L5 purpose "Designed to run as an n8n workflow" →
    "Implemented as a Python script (`run_persona_pipeline.py`),
    parallel across all voices, calling four model APIs in sequence"
  - L344: drop the "n8n implementation: HTTP Request node(s)…" line.
  - L358: drop the "n8n's HTTP Request node should validate…" line.
  - L360 Template syntax paragraph: rewrite — the code uses Jinja2
    `{% if %}` directly, not Handlebars-to-n8n conversion. Either
    convert the Handlebars examples in the spec body to Jinja2, OR
    leave them as pseudocode and add a header note: "Spec uses
    Handlebars notation for readability; the actual prompts in
    `personas/flows/shared/prompts/` use Jinja2 (`{% if %}`)."
    Latter is less disruptive.
  - L684 "n8n IF node" → "Python `validate_input()` at
    `personas/flows/shared/node0_validation.py`"
  - L738 "n8n implementation: A reusable sub-workflow" →
    "`_ct_compress` helper in `run_persona_pipeline.py`"
  - L773 "The n8n Merge node uses `Object.assign()`" → drop or
    rephrase: "Each pass's output is merged into the accumulating
    dict via Python dict-spread (`{**old, **new}`)"
- `docs/AI_Assembly_Voice_Pipeline.md` (F-09):
  - L339: "read by the orchestration layer (n8n)" →
    "read by the orchestration layer (Prefect / Python runner —
    specific wiring TBD when Voice Pipeline is built)"
  - L621 "n8n workflow design" → "Prefect flow design"

### D.2 Verify

```bash
grep -n "n8n" docs/*.md | grep -v "AI_Assembly_Architecture_v1\|AI_Assembly_Infrastructure_Setup\|README.md\|CURRENT_STATE.md.*§5.14"
# CURRENT_STATE §5.14 has an "n8n" reference explaining WHY we don't use it — that's correct and stays.
# README.md staleness index mentioning stale n8n docs is correct and stays.
# Should otherwise return 0 hits.
```

### D.3 Commit D

```bash
git add docs/
git commit -m "$(cat <<'EOF'
docs: remove stale n8n references from current specs

- F-04 Persona Card v2 — "n8n routing" in the orchestration note
- F-07 Transcription spec — rewrite §Step 1 Storage / Trigger /
  Implementation Draft around FastAPI ingest + Prefect subprocess
- F-08 Persona Pipeline v3.10 — 6 spots naming n8n IF/Merge/HTTP
  nodes; redirect to Python equivalents in run_persona_pipeline.py
- F-09 Voice Pipeline — 2 orchestration-layer references

Architecture_v1 and Infrastructure_Setup remain STALE (per
docs/README.md) and are not touched — they'll move to archive in the
reorganization commit.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

---

## Phase E — Prompt + code cleanup (P2/P3)

### E.1 F-21 — `personas/run_persona_pipeline.py` L747-748

Current comment:
```python
# Spec: Sonnet temp 0.4. We use Opus + adaptive thinking — these provocations
# become runtime few-shot exemplars in the Voice Pipeline; high stakes.
```

The claim contradicts the 2026-04-15 decision. Rewrite to:
```python
# Spec: Sonnet temp 0.4. We use Opus + adaptive thinking — these
# provocations are a build-time smoke test + Pass 7c diagnostic
# surface + human-review artifact. They are NOT runtime few-shot
# exemplars (see metadata.worked_provocations_role below, and
# personas/HANDOFF.md). High stakes because Pass 7c reads them.
```

### E.2 F-22 — `personas/HANDOFF.md` strip `</content>` tags

Lines 18, 55, 104-105 contain spurious HTML-like `</content>` closing
tags that aren't valid Markdown and appear to be copy-paste artifacts
from an earlier tool. Delete them.

### E.3 F-20 — `runtime/ingest/pipeline.py` `_subprocess_env`

At L343-354 the `keys` tuple in `_subprocess_env()` doesn't include
`TRANSCRIPTION_CLAUDE_MODEL`. Add it right after `CLAUDE_MODEL`:

```python
keys = (
    "ANTHROPIC_API_KEY",
    "ASSEMBLYAI_API_KEY",
    "CLAUDE_MODEL",
    "TRANSCRIPTION_CLAUDE_MODEL",   # NEW: per-flow override
    "TRANSCRIPTION_SPEAKER_ID_MODEL",
    "TRANSCRIPTION_CACHE",
    ...
)
```

### E.4 F-30 — `personas/flows/shared/prompts/persona_pass_1merge_contradiction_system.md`

Current single line: `You are checking two research documents about the same figure for contradictions.`

Replace with: `You are checking multiple research documents about the same figure for contradictions.`

### E.5 F-31 — `persona_pass_1merge_three_way_user.md` header

Current L1: `{# Pass 1-merge — Three-way contradiction check (Claude Sonnet).`

Replace with: `{# Pass 1-merge — Three-way contradiction check (Claude Opus 4.7 + adaptive thinking).`

### E.6 F-32 — delete orphaned `persona_pass_1merge_contradiction_user.md`

The 2-way user prompt is superseded by `persona_pass_1merge_three_way_user.md`
and no code references it.

**Before deleting, verify:**
```bash
grep -rn "persona_pass_1merge_contradiction_user" \
  personas/ --include="*.py" --include="*.md"
# Should return only the file itself + this plan.
```

Then:
```bash
git rm personas/flows/shared/prompts/persona_pass_1merge_contradiction_user.md
```

### E.7 F-17 — document per-flow model override env vars

Add to `docs/LLM_CALL_INVENTORY.md §5.1` env-var table:

```
| `TRANSCRIPTION_CLAUDE_MODEL` | `CLAUDE_MODEL` | Per-flow override for transcription (cleaning + drift verification). Falls through to CLAUDE_MODEL if unset. |
| `RESEARCHER_CLAUDE_MODEL` | `CLAUDE_MODEL` | Per-flow override for researcher extraction/clustering/theming. |
| `PROVOCATEUR_CLAUDE_MODEL` | `CLAUDE_MODEL` | Per-flow override for provocateur triage/formulation. |
```

Add to `docs/CURRENT_STATE.md §7.2` "Optional overrides" row:
`TRANSCRIPTION_CLAUDE_MODEL, RESEARCHER_CLAUDE_MODEL, PROVOCATEUR_CLAUDE_MODEL` after the existing list.

### E.8 F-18 — align `index` vs `turn_index` in Researcher prompt + spec

The Transcription output writes `{"index": i, "text": ...}` in
`review_queue.verify_markers`. The Researcher prompt + spec text
calls it `turn_index`. Cheapest fix: update the prompt + spec to
match the actual field name `index` (the code is the source of truth).

- `runtime/flows/shared/prompts/researcher_extraction.md` L27: "listing
  turn indices where the cleaning pass flagged words" — already
  accurate. The phrase "by its turn_index" appears at L27 — change
  to "by its `index` field" to match the JSON shape.
- `docs/AI_Assembly_Researcher_Pipeline.md` L392: same update.

### E.9 F-26 — clarify `runtime/.env.example` `INGEST_FLOW_CMD`

Current L44-46:
```
# Optional: swap the Stage 0 command for testing. Defaults to
# `python flows/transcription_flow.py`. Set to the fake flow during smoke
# tests to avoid burning credits.
# INGEST_FLOW_CMD=python ingest/tests/fake_transcription_flow.py
```

Make the danger explicit:
```
# Optional: override the Stage 0 command. DEFAULT (when unset):
# `python flows/transcription_flow.py` — this is what production uses.
# Uncomment the line below ONLY for smoke-testing with the fake flow;
# leaving it enabled in production silently runs the fake pipeline
# and produces stub outputs.
# INGEST_FLOW_CMD=python ingest/tests/fake_transcription_flow.py
```

### E.10 Commit E

```bash
git add -A
git commit -m "$(cat <<'EOF'
chore: P2/P3 prompt + code cleanup from FRESH_REVIEW findings

- F-17 document per-flow model env vars in LLM_CALL_INVENTORY + CURRENT_STATE
- F-18 align `index` vs `turn_index` in Researcher prompt + spec
- F-20 add TRANSCRIPTION_CLAUDE_MODEL to ingest _subprocess_env passthrough
- F-21 fix stale comment in run_persona_pipeline.py L747-748
  (worked_provocations are NOT runtime few-shot exemplars)
- F-22 strip spurious </content> tags from personas/HANDOFF.md
- F-26 make INGEST_FLOW_CMD danger explicit in runtime/.env.example
- F-30 persona_pass_1merge_contradiction_system.md "two" → "multiple"
- F-31 persona_pass_1merge_three_way_user.md header Sonnet → Opus 4.7
- F-32 delete orphaned persona_pass_1merge_contradiction_user.md

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

---

## Phase F — Structural doc refreshes

### F.1 F-23 — `personas/README.md` rewrite

Current §"Two repos, one project" treats `ai-assembly` and
`ai-assembly-personas` as separate repos (stale — now a monorepo).
Layout diagram describes non-existent paths (`flows/persona_flow.py`,
`flows/shared/card_template/`, `runs/{slug}/persona_card.json`,
`derive/` subdir).

**Fix:** rewrite the README end-to-end to reflect the actual monorepo
structure. Keep it terse — it's a pointer document. Target shape:

```markdown
# AI Assembly — Personas sub-tree

This is the `personas/` sub-tree of the ai-assembly monorepo. See the
top-level [README.md](../README.md) for overall orientation.

Pre-conference pipeline that produces Persona Cards — one per voice —
that the runtime overnight pipeline consumes.

## Local structure

- `run_pass0a_voice_config.py` — Pass 0a: voice config + human review doc
- `run_phase0_1_research.py` — Phase 0.5: Perplexity + Gemini parallel
  + Pass 0b DR-prompt render
- `run_pass0b_dr_prompt.py` — Pass 0b standalone (DR prompt render only)
- `run_persona_pipeline.py` — main pipeline (Pass 1-merge → Derive)
- `flows/shared/` — shared code: clients, io, node validation, prompts
- `inputs/` — per-voice inputs:
  - `conference_context.json`
  - `voices/` — voice configs (5 of 12 built)
  - `dossiers/` — Claude DR dossiers (manually produced via claude.ai)
- `scripts/` — standalone utilities (DR dossier validator)
- `runs/` — per-voice build outputs (gitignored)

## Setup

```
cd personas
python3.12 -m venv venv
venv/bin/pip install anthropic==0.94.1 google-genai==1.73.1 \
  openai==2.31.0 perplexity-ai python-dotenv jinja2 requests
```

API keys live in `../.env` at the monorepo root.

## Run a voice end-to-end

```
venv/bin/python run_pass0a_voice_config.py "Voice Name"
venv/bin/python run_phase0_1_research.py "Voice Name"
# [manual: paste DR prompt into claude.ai, save dossier]
venv/bin/python run_persona_pipeline.py "Voice Name"
```

## Output per voice

- `runs/<slug>/persona_card_assembled.json` — 37-field card (consumed
  by runtime Voice Pipeline)
- `runs/<slug>/provocateur_profile.json` — 8-field profile (consumed
  by runtime Provocateur via `council_config.json`)
- `runs/<slug>/evaluation_rubric.json` — 9-test quality rubric

## Specs

- `../docs/AI_Assembly_Persona_Pipeline_v3_10.md` — pipeline spec
- `../docs/AI_Assembly_Persona_Card_v2.md` — 37-field schema
- `HANDOFF.md` — cross-tree handoff contract to runtime
```

### F.2 F-24 — `docs/CURRENT_STATE.md §6.1` counts

- Currently says "only 2 prompts exist (cleopatra, octopus). 9 more
  need generating." Update to "3 prompts exist (cleopatra,
  ibn_battuta, octopus). 9 more to generate."
- Currently says "only Plato has a completed Claude DR dossier
  (`plato_claude_dr.md`)." That file doesn't exist. Replace with:
  "0 of 12 Claude DR dossiers in `personas/inputs/dossiers/` at
  present. Plato's run predates the three-source merge; its
  persona_card_assembled.json was produced via the 2-source fallback
  path."

### F.3 Commit F

```bash
git add personas/README.md docs/CURRENT_STATE.md
git commit -m "$(cat <<'EOF'
docs: refresh personas/README.md + CURRENT_STATE §6.1 counts

- F-23 personas/README.md rewritten to reflect monorepo (was
  describing an obsolete two-repo architecture with non-existent paths)
- F-24 CURRENT_STATE §6.1: correct DR-prompt count (3, not 2) and
  correct Plato DR dossier claim (file does not exist)

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

---

## Phase G — Personas venv Python version (F-28)

`personas/venv` runs Python 3.9.6; CLAUDE.md + CURRENT_STATE §7.1
claim 3.12.

**Default path (match docs):** rebuild personas venv on Python 3.12.
Imports already work on 3.9 because every file starts with
`from __future__ import annotations` — so rebuild is mechanical, no
code changes needed.

```bash
cd /Users/aienvironment/Desktop/ai-assembly/personas
ls venv/                        # record existing packages for rebuild
venv/bin/pip freeze > /tmp/personas-pip-freeze.txt

# Rebuild on 3.12
rm -rf venv
python3.12 -m venv venv
venv/bin/pip install -U pip
venv/bin/pip install -r /tmp/personas-pip-freeze.txt

# Verify
venv/bin/python --version      # must show Python 3.12.x
venv/bin/python -c "
import sys; sys.path.insert(0, '.')
from flows.shared.clients import call_claude
from flows.shared.io import load_prompt, voice_slug, load_voice_input
from flows.shared.node0_validation import validate_input
from flows.shared.prompt_render import render
render('persona_pass_3_user', merged_dossier='m', pass_2_summary='s')  # F-27 regression test
print('personas on 3.12: OK')
"
```

Expected: "personas on 3.12: OK". If requirements.txt ships in the
repo, generate one:

```bash
venv/bin/pip freeze > requirements.txt
git add requirements.txt
```

(Check if `personas/requirements.txt` already exists before adding —
commit only if it's new or materially changed.)

**Alternative path (update docs):** if upgrading is unacceptable for
any reason (e.g. a dependency that only builds on 3.9 — unlikely, but
check), instead update `CLAUDE.md §"Separate venvs"` and
`docs/CURRENT_STATE.md §7.1` to truthfully state "runtime: Python
3.12, personas: Python 3.9" with one-line rationale.

### G.1 Commit G

```bash
# Alternative path would just be docs edit:
# git add CLAUDE.md docs/CURRENT_STATE.md
git commit -m "$(cat <<'EOF'
chore(personas): rebuild venv on Python 3.12 to match documented version

F-28 — personas/venv was on Python 3.9.6 while CLAUDE.md and
CURRENT_STATE §7.1 both documented Python 3.12. Imports worked on
3.9 via `from __future__ import annotations`, but the version skew
would eventually break on a 3.10+-only feature.

Post-rebuild: personas/venv reports Python 3.12.x; all module
imports clean; persona_pass_3_user renders successfully (F-27
regression test passes).

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

If you chose the alternative docs-only path, commit message becomes
`docs: admit personas/venv is on Python 3.9, not 3.12`.

---

## Phase H — Deferred items (DO NOT TOUCH IN THIS PLAN)

These appear in the review's findings list but are NOT fixed here:

- **F-02** — Briefing v3.1 L148/L288 pointing at the stale
  `Architecture_v1.md`. Defer. The reorganization plan's Phase B
  rewrites these pointers when `Architecture_v1.md` moves to
  `_workspace/archive/specs/`. Touching them here would cause a
  conflict at reorg time.
- **F-25** — Octopus `medium`: council_config stub says FLUX image,
  Briefing v3.1 says chromatophore shader. This is a design decision,
  not a doc drift. Open a question for the user and wait.
- **F-15 (council/README version string)** — leave as part of the
  v3.7 → v3.10 sweep in Phase C (already handled there, but don't
  update the version string `dev_stub_v2_with_selection_params` →
  `dev_stub_v3_audience_sharpened` in the README here — the council
  config's actual version is now `dev_stub_v3_audience_sharpened` and
  the README version mention should match. Include in Phase C if not
  already.)

---

## Phase I — Verification + push

### I.1 Runtime tests

```bash
cd /Users/aienvironment/Desktop/ai-assembly/runtime
venv/bin/python -m pytest ingest/tests/ -v
```
Expected: 29/29 pass.

### I.2 Live Pass 3 render (F-27 regression)

```bash
cd /Users/aienvironment/Desktop/ai-assembly/personas
venv/bin/python -c "
import sys; sys.path.insert(0, '.')
from flows.shared.prompt_render import render
r = render('persona_pass_3_user', merged_dossier='mock', pass_2_summary='mock')
assert 'chatgpt_supplement' not in r, 'Template leak'
assert 'merged_dossier' in r or 'Research Dossier' in r, 'Template stripped content too'
print('F-27 regression test: PASS')
"
```

### I.3 Every persona user prompt still renders with runner kwargs

```bash
cd /Users/aienvironment/Desktop/ai-assembly/personas
venv/bin/python <<'EOF'
import sys; sys.path.insert(0, '.')
from flows.shared.prompt_render import render

tests = [
    ("persona_pass_1merge_three_way_user", dict(perplexity_dossier="m", claude_dr_dossier=None, gemini_broad_scan="m")),
    ("persona_pass_1c_extract_urls",      dict(name="Test")),
    ("persona_pass_1d_excerpt_selection", dict(name="T", merged_dossier="m", structural_index="m")),
    ("persona_pass_2_user",               dict(merged_dossier="m")),
    ("persona_pass_3_user",               dict(merged_dossier="m", pass_2_summary="s")),
    ("persona_pass_4a_user",              dict(merged_dossier="m", primary_texts="p", pass_2_3_summary="s")),
    ("persona_pass_4b_user",              dict(pass_2_3_4a_summary="s", rhetorical_mode="r", characteristic_moves="c", register_and_tone="r")),
    ("persona_pass_5_user",               dict(pass_2_3_4_summary="s", constitution="c", reasoning_method="r")),
    ("persona_pass_6_user",               dict(primary_texts="p", merged_dossier="m", pass_2_3_4a_summary="s", constitution="c", concept_lexicon="c", reasoning_method="r", rhetorical_mode="r", characteristic_moves="c", register_and_tone="r")),
    ("persona_pass_7pre_citation_user",   dict(persona_card_json="p", primary_texts="p", merged_dossier="m")),
    ("persona_pass_7a_cross_model_user",  dict(persona_card_json="p")),
    ("persona_pass_7b_provocations_user", dict(persona_card_json="p")),
    ("persona_pass_7c_negative_user",     dict(rhetorical_mode="r", characteristic_moves="c", register_and_tone="r", banned_language="b", banned_modes="b", worked_provocations="w")),
    ("persona_derive_user",               dict(persona_card_json="p")),
    ("persona_coherence_threading",       dict(name="T", prior_pass_output_json="j")),
]

for name, kwargs in tests:
    try:
        render(name, **kwargs)
        print(f"{name:50} OK")
    except Exception as e:
        print(f"{name:50} FAIL: {type(e).__name__}: {str(e)[:60]}")
        raise SystemExit(1)
print("\nAll persona user prompts render: OK")
EOF
```
Every line must end with `OK`.

### I.4 Final grep sweeps

```bash
cd /Users/aienvironment/Desktop/ai-assembly
# v3.7 references
grep -rn "v3\.7 Persona Card\|v3\.7 Persona Pipeline\|v3\.7 spec" \
  docs/ README.md CLAUDE.md runtime/ personas/ \
  --include="*.md" \
  | grep -v "personas/notes/\|runtime/notes/\|_archive\|IMPLEMENTATION_AUDIT_v3_7\|Changelog"
# Should return 0

# n8n references in current specs
grep -n "n8n" docs/AI_Assembly_Briefing_v3_1.md \
  docs/AI_Assembly_Transcription_Pipeline.md \
  docs/AI_Assembly_Researcher_Pipeline.md \
  docs/AI_Assembly_Provocateur_Pipeline.md \
  docs/AI_Assembly_Voice_Pipeline.md \
  docs/AI_Assembly_Persona_Card_v2.md \
  docs/AI_Assembly_Persona_Pipeline_v3_10.md \
  | grep -v "§5\.14\|stale\|STALE\|not used"
# Should return 0 (or only intentional references explaining why n8n is NOT used)

# thinking_budget in personas outside call_gemini
grep -rn "thinking_budget" personas/ --include="*.py" \
  | grep -v "call_gemini\|google.genai\|google-genai"
# Should return 0

# chatgpt_supplement references (should be gone)
grep -rn "chatgpt_supplement" personas/ docs/ \
  --include="*.md" --include="*.py" \
  | grep -v "personas/notes/\|_archive"
# Should return 0

# structured field in Provocateur narrative briefing
grep -n '`structured` field' docs/AI_Assembly_Provocateur_Pipeline.md
# Should return 0
```

### I.5 Push + PR

```bash
git push -u origin fix-review-findings

gh pr create --title "fix: apply FRESH_REVIEW findings (F-01 through F-32)" --body "$(cat <<'EOF'
## Summary

Applies all actionable findings from
`docs/FRESH_REVIEW_2026_04_19.md` §4, prioritised per §8.

## What changed

- **F-27 pipeline-blocker** — `persona_pass_3_user.md` stopped
  raising `UndefinedError: 'chatgpt_supplement' is undefined` on new
  voice builds. 4-line template delete.
- **P0/P1 spec correctness (F-03, F-05, F-06, F-12, F-13, F-16,
  F-29)** — Persona Card v2, LLM_CALL_INVENTORY, CURRENT_STATE §5.12,
  Provocateur spec, Persona Pipeline v3.10 Pass 3/4a/5 body aligned
  with actual 2026-04-18 code state.
- **v3.7 version sweep (F-01, F-10, F-11, F-14, F-15)** — 6
  remaining references updated.
- **n8n sweep (F-04, F-07, F-08, F-09)** — 10+ references removed or
  redirected to the actual Prefect/FastAPI implementation.
- **Prompt + code cleanup (F-17, F-18, F-20, F-21, F-22, F-26, F-30,
  F-31, F-32)** — 9 small fixes (orphaned prompt delete, stale
  comment, env-var passthrough, README refresh, etc.)
- **Structural refreshes (F-23, F-24)** — personas/README.md rewritten
  for monorepo; CURRENT_STATE §6.1 counts corrected.
- **F-28** — personas/venv rebuilt on Python 3.12 to match docs.

Deferred (not fixed here):
- F-02 (Briefing pointer to Architecture_v1) — defer to reorganization
  plan, which moves Architecture_v1 to archive.
- F-25 (Octopus medium: FLUX vs chromatophore shader) — needs design
  decision.

## Test plan

- [x] Runtime test suite passes (29/29)
- [x] F-27 regression: persona_pass_3_user renders cleanly
- [x] All 15 persona user prompts render successfully with the
      runner's actual kwargs
- [x] Grep sweeps for v3.7 / n8n / thinking_budget / chatgpt_supplement
      / `structured` field return no hits in current docs

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

---

## Stop-and-ask rules

- `pytest` fails in preflight → stop; refactor needs a green baseline.
- `pytest` fails after Phase A (the F-27 fix) → stop; the Pass 3
  template delete should not break tests. Inspect.
- Any grep in Phase B-D returns unexpected hits that aren't covered
  by the edit list → stop and report; we may have missed a location.
- Phase G venv rebuild fails (pip install error, import error) →
  stop; report the error. Rolling back to Python 3.9 is fine via
  `cd personas && rm -rf venv && python3.9 -m venv venv && pip install -r
  /tmp/personas-pip-freeze.txt` — don't improvise a fix.
- Phase I regression tests fail → stop; don't push a broken state.

---

## Run order

1. **This plan first** (`SONNET_EXECUTION_PLAN_findings_fixes.md`).
   Produces 7 commits on branch `fix-review-findings`. Merge to main
   before proceeding.
2. **Reorganization plan second** (`SONNET_EXECUTION_PLAN_reorganization.md`).
   Produces 3-4 commits on branch `refactor-reorganise-tree`. Merges
   after fix plan lands.

Why this order:
- F-27 ships immediately; 7 voices can be built as soon as fix plan
  merges.
- Reorg moves historical material OUT of production paths. Fixes
  target production paths that don't move. No pointer conflicts.
- `FRESH_REVIEW_2026_04_19.md` ends up archived as a clean snapshot:
  "here's what was true during the review, here's what we fixed,
  here's where the cruft went." If reorg ran first, the snapshot
  would sit in archive with unresolved findings.

## Out of scope

Do NOT, in this plan:

- Fix F-02 (Briefing pointer to Architecture_v1) — defer to reorg
  plan Phase B.
- Make an F-25 Octopus-medium decision — requires user input.
- Move any file out of its current directory — that's the
  reorganization plan's job.
- Touch any `_archive/` directory contents.
- Upgrade any model version or add new features.
- Run the persona pipeline for real (it's fixed but requires API
  keys + cost; a live run is out of scope for a fix PR).

---

*This plan and the reorganization plan will both move to
`_workspace/archive/fix-plans/` when the reorg executes. That's
expected.*
