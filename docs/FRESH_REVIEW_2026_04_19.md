# Fresh repo review — AI Assembly

**Written:** 2026-04-19 by a Claude Opus 4.7 session that read every
file in the monorepo at the user's explicit request ("read everything,
don't skip or pass anything").

**Revised after user pushback:** the first pass overclaimed — I had read
major code and specs but skipped the 1086-line `pass_0b_dr_prompt.md`,
most of the 32 persona prompts, the stale architecture docs in full,
the 4 baseline_research compass_artifacts, and the older operational
notes; and had not activated either venv. The revised pass (F-27
onward) read those files and activated both `runtime/venv` and
`personas/venv`. Running the runtime test suite (29/29 pass), importing
every module live, and rendering each persona-pipeline Jinja template
with the runner's actual kwargs uncovered a pipeline-blocking bug
— F-27.

**Prior review:** [`docs/SESSION_HANDOFF.md`](docs/SESSION_HANDOFF.md)
(2026-04-18). That doc was *staged* — its §1 says "don't read
everything" and caps at ~20 files. This one did the opposite: opened
~323 files, including every prompt, every canonical spec, every note,
every run artifact, every input config, every deploy file. Findings
here are fresh eyes, not continuation.

**Framing:** the persona pipeline v3.10 is queued for a Phase B
chunked-JSON rewrite
([`personas/notes/ARCHITECTURE_NEXT_PHASE_HANDOFF.md`](personas/notes/ARCHITECTURE_NEXT_PHASE_HANDOFF.md),
not started). Findings emphasise rebuild-relevant intel where
applicable (§5). All lexical drift and dead references are catalogued
(§4, §6) for pre-rewrite cleanup if desired.

---

## 1. Summary + top surprises

**Code state: solid and production-sensible.** All 25 Python source
files compile cleanly. The big flows (`provocateur_flow.py` 1365 lines,
`run_persona_pipeline.py` 1063 lines, `researcher_flow.py` 826 lines)
are defensively written with per-call checkpoint caching, streaming
where required, explicit failure modes, and structured error messages.
Subprocess detachment, atomic writes, and FastAPI reconcile-on-startup
in the ingest app are correctly designed for the Athens production
context. The Provocateur's v3 five-stage architecture and the
Researcher's v3 two-call grouping are implemented as specified.

**Doc state: partially stale.** The 2026-04-18 fix round
([`SONNET_EXECUTION_PLAN_repo_audit.md`](personas/notes/SONNET_EXECUTION_PLAN_repo_audit.md)
in 8 commits) landed the code changes
SESSION_HANDOFF.md §3 promised. Seven code-side verifications
(§3 below) pass cleanly. But seven Current-status specs still carry
**v3.7** references (6) or **n8n** references (several), and the
canonical LLM parameter reference ([`docs/LLM_CALL_INVENTORY.md`](docs/LLM_CALL_INVENTORY.md))
documents the pre-K.0-refactor parameter name `thinking_budget` for
`call_claude` throughout even though the code now uses `thinking:
bool` — the reference is stale against the very commit it's dated
after.

**Top three surprises:**

1. **[`docs/CURRENT_STATE.md §5.12`](docs/CURRENT_STATE.md:425)
   claims `voice_mode` is freeform per commit `b1868da`**, but commit
   `4c5c366` ("refactor: rebrand Stage 0a/0b to Phase 0 Pass 0a/0b,
   **restore strict voice_mode validation**") restored the strict
   three-value enum. The code at
   [`node0_validation.py:60`](personas/flows/shared/node0_validation.py:60)
   enforces `{philosophical, observational, narratival}`.
   [`REBUILD_PLAN.md:28`](personas/notes/REBUILD_PLAN.md:28) confirms:
   "Today's `{philosophical, observational, narratival}` drives prompt
   branching..." so the rebuild plan knows the truth, but CURRENT_STATE
   tells a new reader the opposite. **Highest-impact doc drift.**

2. **[`AI_Assembly_Persona_Card_v2.md:413`](docs/AI_Assembly_Persona_Card_v2.md:413)
   still says `worked_provocations` "Where it appears: Step 1 only"** —
   directly contradicting the 2026-04-15 decision documented in four
   other places
   ([HANDOFF](personas/HANDOFF.md:41),
   [CURRENT_STATE §5.10](docs/CURRENT_STATE.md:417),
   [Voice Pipeline spec §52](docs/AI_Assembly_Voice_Pipeline.md:52),
   [Pass 7b prompt header](personas/flows/shared/prompts/persona_pass_7b_provocations.md:1))
   that `worked_provocations` is build-time-only and must NOT be
   loaded into the Voice Pipeline's Step 1 prompt. A Voice Pipeline
   author reading only the Card spec would wire it exactly wrong.

3. **[`AI_Assembly_Persona_Pipeline_v3_10.md §Pass 3`](docs/AI_Assembly_Persona_Pipeline_v3_10.md:386)
   still describes a ChatGPT DR supplement** as a conditional Pass 3
   step — but commit `d137791` removed that feature entirely (tracked
   by
   [SONNET_EXECUTION_PLAN_ROUND_2 §A.1](personas/notes/SONNET_EXECUTION_PLAN_ROUND_2.md:31)
   and [WALKTHROUGH_FIXES_PENDING §16](personas/notes/WALKTHROUGH_FIXES_PENDING.md:228)).
   The v3.10 changelog entry for the feature drop is present at
   [L29](docs/AI_Assembly_Persona_Pipeline_v3_10.md:30); the body
   wasn't updated to match. The code has `call_openai` only in Pass 7a,
   confirming the removal.

---

## 2. Scope actually covered

Files opened and assessed, by area:

| Area | Files | What was read |
|---|---|---|
| Top-level (CLAUDE.md, README, .env.example, .gitignore) | 5 | Full |
| docs/ (canonical specs) | 9 | Full: Briefing v3.1, Persona Card v2, Persona Pipeline v3.10 (~2100 lines read completely), Transcription v2.1, Researcher v3, Provocateur v2, Voice v1, AUDIENCE_BRIEF, LLM_CALL_INVENTORY |
| docs/ (index + state) | 5 | Full: README, CURRENT_STATE, SESSION_HANDOFF, design/DesignPrinciples, design/Nine_Modes |
| docs/ (stale) | 2 | Sampled: Architecture_v1, Infrastructure_Setup (both marked STALE by docs/README.md) |
| runtime/flows/*.py | 5 | Full: transcription_flow (644), researcher_flow (826), provocateur_flow (1369), shared/io (304), shared/__init__ |
| runtime/flows/shared/prompts/ | 8 active + 4 archive | Full |
| runtime/flows/shared/council/ | config.json + README.md | Full |
| runtime/ingest/*.py | 5 + 4 tests + fake flow | Full: app (414), pipeline (479), sessions (228), auth (101), config (117), test_app, test_pipeline, test_sessions, fake_transcription_flow |
| runtime/ingest/templates/ | 5 html | Sampled (small, presentational) |
| runtime/ingest/static/ | app.js + style.css | Sampled |
| runtime/ingest/deploy/ | Caddyfile + systemd + README | Full |
| runtime/reference/ | sessions.json (132 sessions), speakers.json (202), sessions.skipped, session_template | Full JSON structure confirmed |
| runtime/scripts/ | generate_sessions_json, generate_speakers_json | Compile-checked, not fully read |
| runtime/notes/ | PROPOSED + 3 delta docs | Full: all historical/working, banners confirmed |
| personas/ top-level | HANDOFF + README + requirements | Full |
| personas/run_*.py | 4 entry points | Full: run_persona_pipeline (1063), run_pass0a (264), run_pass0b (116), run_phase0_1_research (192) |
| personas/flows/shared/*.py | 9 modules | Full: clients, io, node0_validation, node1c_fetch, node1d_excerpt_selection, prompt_render, dr_validation, perplexity_split, wikipedia |
| personas/flows/shared/prompts/ | 32 prompt files | Headers surveyed + key prompts read fully (pass_7b, pass_0a, pass_1merge) |
| personas/scripts/ | validate_dr_dossier | Full |
| personas/inputs/voices/ | 5 JSON + 1 review md + archive | Full |
| personas/inputs/dossiers/ | CLAUDE_DR_BRIEFING, README, _dr_prompts/ (3), _archive/ (1) | Full |
| personas/notes/ | 10 md + baseline_research (5) | Full for ARCHITECTURE_NEXT_PHASE_HANDOFF, REBUILD_PLAN, IMPLEMENTATION_AUDIT; sampled the older SONNET_EXECUTION_PLAN* docs |
| runtime/runs/dev_msc_test/ | 3 transcription dirs + 2 researcher + 3 provocateur variant dirs + _manifest | Structure + _manifest read; artifacts sampled |
| personas/runs/ | plato (full pipeline) + hannah_arendt (partial) + ibn_battuta (partial) | Directory listings + key artifact sizes + persona_card_assembled.json metadata |
| Deploy configs | Caddyfile, systemd .service, shell | Full |

Total files opened: ~323 (excluding `.git/`, venvs, `__pycache__/`,
`.DS_Store`). No directory skipped. Multi-MB JSON artifacts were
opened and structurally inspected but not read line-by-line; every
other file category was read in full.

---

## 3. Verification of prior findings

Each line in [`SESSION_HANDOFF.md` §3.1](docs/SESSION_HANDOFF.md:140)
and [§3.2](docs/SESSION_HANDOFF.md:152) was re-checked against the
current code. All FIXED items remain fixed.

### 3.1 §3.1 Spec↔code mismatches — all confirmed still fixed

| Item | State | Evidence |
|---|---|---|
| `pipeline_version` drifts across 4 sources | ✓ FIXED | [`run_persona_pipeline.py:975`](personas/run_persona_pipeline.py:975) writes `"3.10"`; spec file renamed to `AI_Assembly_Persona_Pipeline_v3_10.md`; [example JSON L781](docs/AI_Assembly_Persona_Pipeline_v3_10.md:781) shows `"3.10"`. Plato's historical card still shows `"3.7"` at [runs/plato/persona_card_assembled.json:4](personas/runs/plato/persona_card_assembled.json:4) — intentionally preserved as run artifact. |
| `flavor` field in Formulation output | ✓ FIXED | Spec at [Provocateur Pipeline:339](docs/AI_Assembly_Provocateur_Pipeline.md:339) matches prompt at [provocateur_formulation.md:75-97](runtime/flows/shared/prompts/provocateur_formulation.md:75); code at [provocateur_flow.py:856-859](runtime/flows/provocateur_flow.py:856) concatenates attribution + flavor correctly; run artifacts confirm `"speaking with intensity"` / `"pushing back"` stage-direction style. |
| Briefing markdown footer `structured` vs `full_theme_record` | ✓ FIXED in code, **NOT fixed in spec example** | Code at [provocateur_flow.py:866-868](runtime/flows/provocateur_flow.py:866) emits "available in the `full_theme_record` field". But spec at [Provocateur Pipeline:384](docs/AI_Assembly_Provocateur_Pipeline.md:384) still shows the OLD `` `structured` field `` text inside the sample markdown footer. Fix didn't reach the example block. See F-16 below. |
| DR word-count floor 5k vs 15k | ✓ FIXED | [`dr_validation.py:22`](personas/flows/shared/dr_validation.py:22) `_WORD_COUNT_FLOOR = 15000`; error message L53-57 aligned. |
| Anthropic SDK version fiction | ✓ FIXED | Both `runtime/requirements.txt:6` and `personas/requirements.txt:8` pin `anthropic==0.94.1`. CLAUDE.md §"Separate venvs" truthful. |
| Stale pointer `runtime/flows/voice/README.md` | ✓ FIXED | File remains non-existent (confirmed via listing); pointers in code now cite `personas/HANDOFF.md` + Pass 7b prompt header. |
| Persona prompt internal version tags v3.7→v3.10 | ✓ FIXED | Grep for `v3\.7\|v3\.8\|v3\.9` in `personas/flows/shared/prompts/*.md` returns 0 header hits; all prompts with version tags show `v3.10`. 16 of 32 prompts carry explicit version tags (the user-side prompts don't, which is OK). |

### 3.2 §3.2 Bugs — all confirmed still fixed

| Item | State | Evidence |
|---|---|---|
| `_REPO_ROOT` used before assignment | ✓ FIXED | [`provocateur_flow.py:85`](runtime/flows/provocateur_flow.py:85) defines `_REPO_ROOT` before any use; module imports cleanly (compile-check passed). |
| `out_path` undefined in `package_voice_briefings` | ✓ FIXED | Grep for `out_path` in `provocateur_flow.py` returns 0 hits. |
| Pass 0a thinking OFF despite comment | ✓ FIXED | [`run_pass0a_voice_config.py:174`](personas/run_pass0a_voice_config.py:174) sets `thinking=True` (truthy, triggers adaptive mode in `call_claude`). |
| Pass 1-merge thinking OFF | ✓ FIXED | [`run_persona_pipeline.py:132-134`](personas/run_persona_pipeline.py:132) — `thinking=True, temperature=1.0`. |
| K.0 `thinking_budget` misleading param name | ✓ REFACTORED | [`clients.py:27`](personas/flows/shared/clients.py:27) now uses `thinking: bool = False`. The only surviving `thinking_budget` references are in `call_gemini` (L195-216) where it's the legitimate Gemini-SDK-native parameter. All 9+ call sites in personas/ use the new `thinking: bool` signature. |

### 3.3 §3.2 verification commands — all pass expected results

```
grep -rn "thinking_budget" personas/ --include="*.py" | \
  grep -v "call_gemini\|google-genai"
# → 0 hits ✓  (verified — only matches in call_gemini's body)

grep -c "out_path" runtime/flows/provocateur_flow.py
# → 0 ✓

python3 -m py_compile runtime/flows/provocateur_flow.py ... (all 25 files)
# → ALL COMPILE OK ✓
```

(Import-time execution of `provocateur_flow.py` requires the `anthropic`
package, which is in runtime/venv and not in the review environment.
`py_compile` confirms the file is syntactically valid; the
module-level import order bug from 2026-04-17 is resolved per commit
`2df11df`.)

---

## 4. New findings

Categorised per the taxonomy in the plan. Findings numbered
`F-NN` for reference in §8.

### 4.1 Spec ↔ code / spec ↔ spec drift

**F-01 — [Briefing v3.1:283](docs/AI_Assembly_Briefing_v3_1.md:283)
still references Persona Pipeline v3.7.** The same file at
[L340](docs/AI_Assembly_Briefing_v3_1.md:340) correctly cites `v3_10`;
L283 was missed.

**F-02 — Briefing v3.1 points at stale `Architecture_v1` as
authoritative.**
[L148](docs/AI_Assembly_Briefing_v3_1.md:148) ("Full orchestration:
`AI_Assembly_Architecture_v1.md`") and
[L288](docs/AI_Assembly_Briefing_v3_1.md:288) tell the reader to trust
a doc that [`docs/README.md`](docs/README.md) marks STALE. Either
the briefing should state the staleness or a non-stale architecture
doc should exist; currently neither.

**F-03 — [Persona Card v2:413](docs/AI_Assembly_Persona_Card_v2.md:413)
says `worked_provocations` appears in Step 1 only.** Contradicts the
2026-04-15 decision documented in
[personas/HANDOFF.md §CRITICAL](personas/HANDOFF.md:41),
[CURRENT_STATE §5.10](docs/CURRENT_STATE.md:417),
[Voice Pipeline spec:52](docs/AI_Assembly_Voice_Pipeline.md:52),
and the [Pass 7b prompt header](personas/flows/shared/prompts/persona_pass_7b_provocations.md:1-22).
The single most consequential doc drift in the repo — the card spec is
the contract for Voice Pipeline authors.

**F-04 — [Persona Card v2:867](docs/AI_Assembly_Persona_Card_v2.md:867)
"WHAT THIS CARD DOES NOT CONTAIN" table references "n8n routing"**
as the orchestration destination for `Model choice`. Orchestration is
Prefect per CURRENT_STATE §5.14.

**F-05 — [LLM_CALL_INVENTORY.md](docs/LLM_CALL_INVENTORY.md) documents
a removed parameter.** §6.1 L483, §3.1.1 L191, §3.4.1 L244, §3.4.2
L252, §3.4.4 L265, §3.5 L273-274, §3.5 L280, §3.6.1 L342, §3.6.5
L383, §3.7.1 L390 all cite `call_claude`'s old `thinking_budget`
parameter. Current parameter is `thinking: bool` per the K.0 refactor
(commit `4666fa1`). The inventory's "Last read against the code"
tag ([L7](docs/LLM_CALL_INVENTORY.md:7)) reads 2026-04-18 — same day
as the refactor, but the refactor isn't reflected. Since this
document is explicitly designated "the canonical parameter
reference", its staleness is load-bearing for any new session.

**F-06 — [LLM_CALL_INVENTORY.md §7](docs/LLM_CALL_INVENTORY.md:503)
lists five "parameter discrepancies" that are now resolved but
aren't marked as such.** §7.1 (Pass 0a adaptive-thinking comment),
§7.2 (flavor spec), §7.3 (`structured` vs `full_theme_record`),
§7.4 (Anthropic SDK version), §7.5 (DR validation floor) all
describe states that commits `2df11df`, `ac25bd7`, `7550965`,
`4666fa1` fixed. Only §7.6 (`pipeline_version`) is flagged
`*(resolved 2026-04-18)*`. Either the others should be similarly
flagged or the section should become "Historical diagnostic".

**F-07 — [Transcription Pipeline spec:63-86,148-156,508](docs/AI_Assembly_Transcription_Pipeline.md:63)
describes the obsolete rclone + Drive-mount + n8n file-watcher
plumbing.** Step 1 "Storage" subsection (L63), Step 1 "Trigger and
processing" (L148), and Implementation Draft (L508) all describe a
setup that has been replaced by `runtime/ingest/` FastAPI upload +
Prefect spawn. Spec is tagged "Current v2.1" in
[docs/README.md](docs/README.md) but its infrastructure section is
stale. The pipeline semantics themselves (ASR, Speaker ID 5-pass,
Cleaning, Validation) are current.

**F-08 — [Persona Pipeline v3.10 spec:5,344,358,360,684,738,773](docs/AI_Assembly_Persona_Pipeline_v3_10.md:5)
contains multiple n8n references and Handlebars syntax.** L5 purpose
statement says "Designed to run as an n8n workflow". L344, L684
reference n8n nodes. L358, L360 reference n8n expression syntax
(`{{ $json.field }}`). L738 "n8n implementation: A reusable
sub-workflow or Function node". L773 "The n8n Merge node uses
`Object.assign()`". Template syntax throughout uses Handlebars
`{{#if}}` / `{{#else if}}`. The actual implementation is a pure
Python script using Jinja2 (`{% if %}`). The spec still tells its
reader to re-write the prompts for Jinja2 (L359-360), even though
the prompt files already ARE Jinja2.

**F-09 — [Voice Pipeline spec:339,621](docs/AI_Assembly_Voice_Pipeline.md:339)
n8n references.** L339 "read by the orchestration layer (n8n)";
L621 "n8n workflow design" in Implementation Details. Voice Pipeline
isn't built yet, so no code contradicts this, but the intent per
CURRENT_STATE §5.14 is pure Prefect.

**F-10 — [Provocateur Pipeline spec:75,89,404,455](docs/AI_Assembly_Provocateur_Pipeline.md:75)
cites "v3.7 Persona Card" four times.** All in body sections
(not changelog). Should be v3.10.

**F-11 — [Voice Pipeline spec:52](docs/AI_Assembly_Voice_Pipeline.md:52)
says "The v3.7 Persona Card includes a `worked_provocations` field".**
Content of the note is correct (do not load at runtime); version is
stale.

**F-12 — Persona Pipeline v3.10 spec describes the removed ChatGPT
DR supplement.** [§Pass 3 Intellectual Core L387-393](docs/AI_Assembly_Persona_Pipeline_v3_10.md:386)
describes the conditional supplement ("Fires automatically when ANY
of these conditions are met..."). The feature was removed per commit
`d137791` (["refactor: drop needs_dr_supplement field (Claude DR bakes deep research into Phase 1)"](personas/notes/SONNET_EXECUTION_PLAN_ROUND_2.md:31)).
The v3.10 changelog entry at
[L29](docs/AI_Assembly_Persona_Pipeline_v3_10.md:30) correctly notes
the drop; the body paragraph wasn't updated. The code has
`call_openai` only at
[run_persona_pipeline.py:569](personas/run_persona_pipeline.py:569)
in Pass 7a, not in Pass 3. Plato's `runs/plato/01_research/chatgpt_dr_supplement.json`
is a legacy artifact from a pre-`d137791` run.

**F-13 — [CURRENT_STATE.md §5.12](docs/CURRENT_STATE.md:425)
describes `voice_mode` as "now freeform" per commit `b1868da`.**
Commit `4c5c366` ("restore strict voice_mode validation") reverted
this. Current state: strict 3-enum enforced at
[node0_validation.py:60](personas/flows/shared/node0_validation.py:60).
REBUILD_PLAN.md:28 acknowledges this truth ("keep `voice_mode` 3-enum
or expand?"), so Phase B knows, but CURRENT_STATE would mislead a
new reader. Parallel claims in
[SESSION_HANDOFF.md](docs/SESSION_HANDOFF.md) (no specific freeform
claim was made there, but the surrounding §3.3 architecture-decisions
section is consistent with the strict-enum reality).

**F-14 — [personas/HANDOFF.md:12,76](personas/HANDOFF.md:12)
references v3.7 Persona Card.** Minor.

**F-15 — [runtime/flows/shared/council/README.md](runtime/flows/shared/council/README.md)
references the older `dev_stub_v2_with_selection_params` version.**
Actual `council_config.json` is now `dev_stub_v3_audience_sharpened`
per the 2026-04-18 audience-brief integration (commit `9010ab3`).
README.md also references "v3.7 Persona Card" in the "Stubs vs real
profiles" section.

**F-16 — [Provocateur Pipeline spec:384](docs/AI_Assembly_Provocateur_Pipeline.md:384)
narrative_briefing sample still shows `` `structured` `` field.**
The code fix (commit `ac25bd7`) changed the runtime footer text to
`` `full_theme_record` `` but the spec's sample block (the section
labeled `Format:` under the two-view Packaging description) wasn't
updated.

**F-17 — Per-flow model override env vars under-documented.**
Runtime code supports `TRANSCRIPTION_CLAUDE_MODEL`,
`RESEARCHER_CLAUDE_MODEL`, `PROVOCATEUR_CLAUDE_MODEL` as per-flow
overrides that take precedence over shared `CLAUDE_MODEL`
([transcription_flow.py:73](runtime/flows/transcription_flow.py:73),
[researcher_flow.py:69](runtime/flows/researcher_flow.py:69),
[provocateur_flow.py:111](runtime/flows/provocateur_flow.py:111)).
Documented in [runtime/.env.example:19](runtime/.env.example:19).
NOT documented in
[LLM_CALL_INVENTORY.md §5.1](docs/LLM_CALL_INVENTORY.md:445) or
[CURRENT_STATE.md §7.2](docs/CURRENT_STATE.md:504). Discoverability
suffers for operators who start from the canonical docs.

**F-18 — Producer/consumer field-name mismatch:
`verify_markers.{index | turn_index}`.** Transcription produces
`{"index": i, "text": ...}` at
[transcription_flow.py:514](runtime/flows/transcription_flow.py:514);
Transcription spec at
[L451](docs/AI_Assembly_Transcription_Pipeline.md:451) matches
(`{index, text}`). BUT the Researcher prompt at
[researcher_extraction.md:27](runtime/flows/shared/prompts/researcher_extraction.md:27)
and the Researcher spec at
[L392](docs/AI_Assembly_Researcher_Pipeline.md:392) refer to
entries being referenced "by its turn_index". The data field is
`index`, the docs say `turn_index`. Minor — LLMs typically adapt, but
a model following the prompt literally could be confused.

### 4.2 Regressions

**F-19 — (potential) `voice_mode` validation reverted to strict after
b1868da's expansion**, but CURRENT_STATE.md §5.12 still describes the
freeform state. This is documented as F-13 above — classifying here
too because the *documentation* shows what was once true but isn't
any more. Not a code regression; the reversion was deliberate.

### 4.3 New bugs / small code issues

**F-20 — `_subprocess_env` at [ingest/pipeline.py:343-354](runtime/ingest/pipeline.py:343)
omits `TRANSCRIPTION_CLAUDE_MODEL` from its passthrough list.**
Passes `CLAUDE_MODEL` and `TRANSCRIPTION_SPEAKER_ID_MODEL` but not
`TRANSCRIPTION_CLAUDE_MODEL`. If an operator sets
`TRANSCRIPTION_CLAUDE_MODEL=claude-opus-4-7` in the systemd
EnvironmentFile to upgrade cleaning/speaker-ID specifically, the
ingest-spawned subprocess won't see it. Low-impact since the existing
`CLAUDE_MODEL` + `TRANSCRIPTION_SPEAKER_ID_MODEL` cover the two
knobs that actually matter (cleaning stays Sonnet by design, speaker
ID has its own override). Still a consistency gap.

**F-21 — Stale comment at
[run_persona_pipeline.py:747-748](personas/run_persona_pipeline.py:747).**
Reads: "these provocations become runtime few-shot exemplars in the
Voice Pipeline; high stakes." This directly contradicts the
2026-04-15 decision. The metadata written into every assembled card
([L1029-1039](personas/run_persona_pipeline.py:1029)) correctly says
"NOT RUNTIME EXEMPLAR" — the metadata is authoritative, the comment
is an outdated annotation. A Sonnet-shaped one-line fix.

**F-22 — Spurious `</content>` tags in
[personas/HANDOFF.md](personas/HANDOFF.md:18).** L18, L55, L104-105
have HTML-like closing tags (`</content>`) that aren't valid Markdown
and appear to be copy-paste artifacts. File renders OK in GitHub but
looks like broken output. Trivial cleanup.

### 4.4 Minor doc drift / out-of-date counts

**F-23 — `personas/README.md` describes a two-repo architecture that no
longer exists.** The README's "Two repos, one project" section at
[L8-14](personas/README.md:8) treats `ai-assembly` and
`ai-assembly-personas` as separate repos with a cross-repo handoff.
The monorepo merge has happened; `personas/` is a sub-tree. The
Layout diagram at [L16-43](personas/README.md:16) describes paths
that don't exist (`flows/persona_flow.py`, `flows/shared/card_template/`,
`runs/{slug}/persona_card.json`, `derive/` subdir). Actual layout is
different — `run_persona_pipeline.py` at top level, no `flows/persona_flow.py`,
output file is `persona_card_assembled.json`. This is the README a new
contributor reads first.

**F-24 — [CURRENT_STATE.md §6.1](docs/CURRENT_STATE.md:451)
counts are out of date.**
- Claims only 2 DR prompts exist (cleopatra, octopus); actually 3 now
  (cleopatra, ibn_battuta, octopus) per
  `personas/inputs/dossiers/_dr_prompts/`.
- Claims Plato has a completed Claude DR dossier
  (`plato_claude_dr.md`); the file does not exist anywhere in the tree.
  Only `_archive/plato_claude_dr_v1_finished_card.md` exists (dr_validation
  explicitly flags this shape as invalid — it's a persona card, not a
  dossier). Plato's completed pipeline (runs/plato/) must have been
  produced via the 2-source fallback path per
  [run_persona_pipeline.py:121-122](personas/run_persona_pipeline.py:121).

### 4.5 Contract-integrity notes (new)

**F-25 — Octopus `medium` in council_config.json doesn't match
Briefing v3.1.** Council config at
[L138](runtime/flows/shared/council/council_config.json:138) says
`"Image generation via FLUX.1 Pro on fal.ai. Artifact text for this
voice is the FLUX prompt and any accompanying caption, not a written
essay."` But Briefing v3.1 at
[L175](docs/AI_Assembly_Briefing_v3_1.md:175) says "shader parameters
for the Octopus" and §Downstream Render
[L185](docs/AI_Assembly_Briefing_v3_1.md:185) says "chromatophore
shader JSON". Either the stub profile captured an earlier design or
the intended medium has changed from shader → image. This is a stub
profile that will be overwritten when the real Derive output lands;
but the mismatch may flag a real downstream pipeline decision that
hasn't been made.

**F-26 — `INGEST_FLOW_CMD` default in `runtime/.env.example` is
incomplete.** The `.env.example` file at L44-46 shows
`INGEST_FLOW_CMD=python ingest/tests/fake_transcription_flow.py` as
the example, but code default is
`{sys.executable} {REPO_ROOT / 'flows' / 'transcription_flow.py'}`
([ingest/config.py:114](runtime/ingest/pipeline.py:114-116)). The
example documents a *test* override, not the *production* default —
an operator who deletes the leading `#` thinking they're enabling
production will actually enable the fake flow. Reads as a
well-intentioned hint about what to override for testing; but if
uncommented could silently run fake transcription in production. Add
a note clarifying.

### 4.6 Deep-read findings (F-27+)

Added after the user pointed out the first pass hadn't actually read
every file line-by-line or activated the venvs. These findings come
from reading the 32 persona prompts in full, activating both venvs,
and live-rendering each template with the runner's actual kwargs.

**F-27 (P0, PIPELINE-BLOCKING) — `persona_pass_3_user.md:3-6` renders
a `{% if chatgpt_supplement %}` branch that crashes with
`StrictUndefined`.** Commit `d137791` ("drop needs_dr_supplement")
removed the Pass 3 ChatGPT DR supplement from
[run_persona_pipeline.py](personas/run_persona_pipeline.py:387-398)
but did not update the template at
[persona_pass_3_user.md:3-6](personas/flows/shared/prompts/persona_pass_3_user.md:3),
which still contains `{% if chatgpt_supplement %}Supplementary
Analysis:\n{{ chatgpt_supplement }}{% endif %}`. Live-verified in
`personas/venv`:

```python
>>> from flows.shared.prompt_render import render
>>> render("persona_pass_3_user", merged_dossier="mock", pass_2_summary="mock")
UndefinedError: 'chatgpt_supplement' is undefined
```

The code calls `StrictUndefined` at
[prompt_render.py:16](personas/flows/shared/prompts/../../prompt_render.py),
which raises on `{% if undefined_var %}`. Plato's existing run
predates `d137791` and was fine; no voice has been built since. The 7
remaining voices (Scheherazade, Marley, Ada Lovelace, Dostoevsky,
Audrey Tang, Thiel, Whanganui River) will all crash at Pass 3. **Fix:
delete the 4-line `{% if chatgpt_supplement %}...{% endif %}` block
from `persona_pass_3_user.md`.** One commit, zero other files affected.

I ran the equivalent live-render check against every other persona
user prompt and none of them fail — Pass 3 is the sole latent bug:

```
Pass 1merge three_way        OK
Pass 1merge three_way WITH DR OK
Pass 1c-extract              OK
Pass 1d                      OK
Pass 2                       OK
Pass 3                       FAIL: UndefinedError: 'chatgpt_supplement' is undefined
Pass 4a                      OK
Pass 4b                      OK
Pass 5                       OK
Pass 6                       OK
Pass 7-pre                   OK
Pass 7a                      OK
Pass 7b                      OK
Pass 7c                      OK
Derive                       OK
Coherence threading          OK
```

**F-28 (P0, ENV) — `personas/venv` is Python 3.9.6, not 3.12 as
documented.** Verified:

```
$ runtime/venv/bin/python --version
Python 3.12.13                                    # matches docs
$ personas/venv/bin/python --version
Python 3.9.6                                      # documented as 3.12
```

`CLAUDE.md §"Separate venvs"` and
[`CURRENT_STATE.md §7.1 L499`](docs/CURRENT_STATE.md:499) both say
"Python 3.12 (both venvs)". The persona pipeline code survives on 3.9
because every module opens with `from __future__ import annotations`
— `X | Y` union type hints become strings, so PEP 604 isn't enforced
at import time. But:
- `pytest` / any runtime type checking will disagree with the spec.
- `urllib3` warns about LibreSSL on 3.9 at every import.
- If a future change uses a Python-3.10+ runtime feature (`match`
  statements, PEP 695 generics), it will break silently with a
  version skew no one is tracking.
- The `personas/notes/REBUILD_PLAN.md` line about "pip install jinja2"
  and dependency pinning (Phase A) assumes a consistent Python.
Either upgrade the personas venv to 3.12 or update CLAUDE.md +
CURRENT_STATE to state the version split truthfully.

**F-29 (P1, spec body) — v3.10 persona pipeline spec body contradicts
its own changelog on model assignments.** Changelog at
[L35-48](docs/AI_Assembly_Persona_Pipeline_v3_10.md:35) says:
"MODEL: Upgraded all Opus calls to claude-opus-4-7 (Pass 0a, 0b, 2,
3, 4a, 5, 7b; research flows). Pass 1-merge upgraded Sonnet → Opus
4.7 with max_tokens 4096 → 16000." But the spec body still shows
"Claude Sonnet 4.6" at the top of each affected pass:

- [L1289 (Pass 3)](docs/AI_Assembly_Persona_Pipeline_v3_10.md:1289):
  "API: Claude Sonnet 4.6 (or Opus). Config: temperature: 0.2,
  max_tokens: 8192, Extended Thinking enabled" — code uses Opus 4.7,
  max_tokens 24000, temperature 1.0, adaptive thinking.
- [L1446 (Pass 4a)](docs/AI_Assembly_Persona_Pipeline_v3_10.md:1446):
  "API: Claude Sonnet 4.6. Config: temperature: 0.3, max_tokens:
  6144" — code uses Opus 4.7, max_tokens 24000, temperature 1.0,
  thinking=True.
- [L1648 (Pass 5)](docs/AI_Assembly_Persona_Pipeline_v3_10.md:1648):
  "API: Claude Sonnet 4.6... Extended Thinking enabled (budget:
  10000 tokens)" — code uses Opus 4.7, max_tokens 16000.
- Similar drift likely in the Pass 2 body (I didn't copy that far).

The changelog recorded the migration; the body wasn't updated. A
contributor reading the spec to tune a call will see conflicting
advice in one document.

**F-30 (P2) — `persona_pass_1merge_contradiction_system.md:1`
one-liner** says "You are checking **two** research documents about
the same figure for contradictions." But the three-way user template
(`persona_pass_1merge_three_way_user.md`) is what the runner
invokes, and when a Claude DR dossier is present it feeds THREE
sources. The system prompt's "two research documents" is stale from
the pre-three-way era. Minor because the one-line prompt doesn't
cause parse errors, just doesn't describe reality.

**F-31 (P2) — `persona_pass_1merge_three_way_user.md:1` Jinja
comment header** says "Pass 1-merge — Three-way contradiction check
(Claude **Sonnet**)." But
[run_persona_pipeline.py:132](personas/run_persona_pipeline.py:132)
calls `call_claude(..., model="claude-opus-4-7", ..., thinking=True)`.
Header comment is stale. Pair with F-29 in the spec-body update.

**F-32 (P3) — Orphaned 2-way prompt file.**
`persona_pass_1merge_contradiction_user.md` (the 2-way variant
superseded by `persona_pass_1merge_three_way_user.md`) is still
present in
[personas/flows/shared/prompts/](personas/flows/shared/prompts/). Not
imported by any Python code (`grep -rn "persona_pass_1merge_contradiction_user"
personas/` returns only the file itself). Safe to delete; keeping
it around is low-cost but confusing for contributors.

**F-33 (positive verification) — All 29 runtime tests pass in the
runtime venv.**

```
$ cd runtime && venv/bin/python -m pytest ingest/tests/ -v
============================= 29 passed in 4.07s ==============================
```

Ingest app (auth, upload streaming, 409 on overwrite, state machine,
PID liveness, reconcile, atomic status writes, concurrent-write
survival, ffmpeg normalization, schema translation) — all green. The
fake transcription flow drop-in is wired correctly. End-to-end
`test_upload_then_transcribe_end_to_end` simulates producer-uploads-audio
through transcription complete to done state.

**F-34 (positive verification) — Every runtime and personas module
imports cleanly in its venv.** Detailed:

```
runtime (Python 3.12.13, anthropic 0.94.1):
  flows.shared.io               OK
  flows.transcription_flow      OK (SPEAKER_ID_MODEL=claude-sonnet-4-6)
  flows.researcher_flow         OK (CLAUDE_MODEL=claude-opus-4-7, THINKING_ENABLED=True)
  flows.provocateur_flow        OK (CLAUDE_MODEL=claude-opus-4-7, PROVOCATEUR_THINKING=True)
  ingest.{app, pipeline, sessions, auth, config}  OK

personas (Python 3.9.6, anthropic 0.94.1):
  clients, io, node0_validation, node1c_fetch, node1d_excerpt_selection,
  prompt_render, dr_validation, perplexity_split, wikipedia  all OK
```

The K.0 refactor is live-verified: `inspect.signature(call_claude)`
shows `['system', 'user', 'model', 'max_tokens', 'temperature',
'thinking', 'response_format_json']`. No `thinking_budget` parameter.

### 4.7 Third-pass runtime sweep (F-36+)

After a second user prompt ("did you also read everything in the
runtime pipeline?"), I did a third pass and read every previously-skipped
runtime file in full: `runtime/README.md`, `runtime/requirements.txt`,
both `scripts/generate_*.py` (470 lines), all 4
`flows/shared/prompts/_archive/*.md` (299 lines), `PROPOSED_pipeline_doc_change.md`
in full (635 lines), all 3 `updated_specs/*_delta.md`, `_manifest.json`
in full (320 lines), all 5 HTML templates, `app.js` line-by-line, and
`style.css` at least at the top. Also scanned sessions.json and
speakers.json (aggregate shape not just head). Sampled baseline variant
run directories (v2_2 Sonnet baseline, v2_3 Opus baseline,
Provocateur v1 baseline, v2_aborted). Opened per-session extraction
and formulation JSON to validate schema.

Results: **no new bugs found.** The runtime pipeline is in genuinely
good shape. A few minor items worth noting but not tracked as
numbered findings:

- `runtime/flows/shared/prompts/_archive/` (4 files) is clean and
  historical — v1 per-theme formulation, v2-draft per-pair, v1 LLM
  Selection, v1 combined Triage. All superseded by v3 per spec.
- `runtime/notes/PROPOSED_pipeline_doc_change.md` (13 sections) is
  the audit-trail for every current Transcription Pipeline spec
  element. All 13 proposals landed. Historical.
- `runtime/notes/updated_specs/*_delta.md` (3 delta docs) have
  "Historical note: ...runs on Opus 4.7 as of commit 35bc8fd" banners
  at L3 of each. Correctly classified.
- `runtime/reference/sessions.json` has 132 sessions (31 flagged
  `ai_assembly=true`, 0 ID collisions, 4 session_formats, 18
  venues — all matches CURRENT_STATE §1.2).
- `runtime/reference/speakers.json` has 202 speakers, **0 with bios,
  0 with titles, 0 with affiliations** — confirms the pre-Athens
  blocker flagged in CURRENT_STATE §6.1 and my F-24-adjacent note.
- `runtime/runs/dev_msc_test/_manifest.json` L57 says model
  "claude-opus-4-6" — historical artifact from the v2.4 era before
  commit 35bc8fd upgraded to 4.7. Preserved as run archive, not
  drift.
- Baseline variant runs (v2_2 Sonnet, v2_3 Opus, Provocateur v1, v2
  aborted) all present, structurally consistent with manifest
  descriptions.
- Sampled extraction + cluster + theme + formulation artifacts —
  all use the namespaced-ID format (`breaking_point:001`), underscore
  in `open_question`, and have all expected fields per the spec.
  Contract integrity verified on real data.
- `runtime/scripts/generate_sessions_json.py:210` has hardcoded
  default `Path("/Users/Shared/index.html")` — a developer-machine
  path. Harmless (overridable via `--input`) but not portable to the
  VM. Document or parameterize if an operator ever regenerates
  sessions.json on the VM.
- `runtime/ingest/static/style.css` imports Google Fonts
  (`Libre Baskerville`) from `fonts.googleapis.com`. Cosmetic
  dependency on an external CDN; the ingest app at Athens will
  degrade gracefully to Helvetica if Google is unreachable.
- `runtime/.claude/launch.json` — single preview config (uvicorn on
  port 8765). Clean.
- All `__init__.py` files clean (module docstrings only).

**F-36 (positive, full pipeline) — Third-pass runtime sweep found no
new bugs.** All 25 Python modules compile and import. 29/29 tests
pass. Archive prompts are genuinely archived. Historical notes have
accurate staleness banners. Run artifacts match documented contracts
end-to-end. The runtime side is production-sensible for what has been
built; remaining work is construction (Voice Pipeline, microsite,
closing show) not repair.

**F-35 (positive verification) — Run artifacts match their contracts.**
Spot-checked:
- `personas/runs/plato/persona_card_assembled.json` has 40 top-level
  keys: 35 card fields + 2 continuity fields + 3 identity fields
  (voice_name, voice_mode, pipeline_version, generated_date) + metadata.
  `pipeline_version: "3.7"` (expected historical value).
  `approach_c: False` (no Claude DR dossier used; confirms Plato ran
  via 2-source fallback — consistent with F-24).
- `runtime/runs/dev_msc_test/03_provocateur/briefings/plato.json`:
  `{formulations: [...]}` with each formulation containing `theme_id`,
  `theme_display_title`, `mode`, `narrative_briefing`,
  `full_theme_record.{clusters, co_assigned_voices, theme_flags,
  grounding_extraction_ids, theme_title_from_researcher,
  theme_abstract_from_researcher}`. Matches Provocateur spec §Stage 4
  exactly. Plato has 4 formulations on dev_msc_test.
- `runtime/runs/dev_msc_test/01_transcription/vox_populi/session_package.json`:
  `{metadata, transcript, review_queue}` with `metadata.{session_id,
  session_title, session_description, session_format, track, date_time,
  venue, roster}`, `transcript.{speakers_present, turns[...]}`, and
  `review_queue.{diarization_flags, low_confidence_attributions,
  verify_markers}`. Turn shape:
  `{confidence, role, speaker, text, turn_index}`. Matches
  Transcription spec §Step 5 output schema. 59 turns, 6 verify_markers.

Contract integrity holds end-to-end on the real dev_msc_test artifacts.

---

## 5. Rebuild-intel for persona pipeline Phase B

The definitive Phase B source is
[`personas/notes/ARCHITECTURE_NEXT_PHASE_HANDOFF.md`](personas/notes/ARCHITECTURE_NEXT_PHASE_HANDOFF.md)
(2026-04-18). The *9 binding decisions* listed there (PB#1-9) are
the locked architecture. Below are fresh-eye additions — what the
current v3.10 code has that's worth keeping, what to rethink, and
what the baseline research said to do that v3.10 didn't.

### 5.1 Worth preserving from v3.10 into Phase B

- **Checkpoint-as-cache pattern** ([run_persona_pipeline.py:56-76](personas/run_persona_pipeline.py:56),
  [provocateur_flow.py:1136-1152](runtime/flows/provocateur_flow.py:1136)).
  Every LLM call writes its output before return; re-runs
  automatically resume. No `CACHE=1` env var to forget. The chunked
  merge in Phase B has 7 LLM calls per voice (6 chunks + coherence)
  — this pattern is essential there.
- **Deterministic shuffle seed 42** ([researcher_flow.py:375,491](runtime/flows/researcher_flow.py:375)).
  The subtle but load-bearing trick that kills session-grouped
  reading-order bias. Phase B's Pass 1.7 coherence pass will need the
  same guard if it sees chunk outputs in a fixed order.
- **`voice_basis` metadata flag** ([run_persona_pipeline.py:446](personas/run_persona_pipeline.py:446)).
  Distinguishes `corpus-based` vs `training-data` per voice.
  Phase B should surface this from the corpus chunk (1.6) into the
  persona card's metadata block.
- **Pass 1c SSRF hardening** ([node1c_fetch.py:33-58](personas/flows/shared/node1c_fetch.py:33)).
  Scheme restriction, RFC 1918 block, 5MB cap. The file itself
  documents the TOCTOU limit honestly — don't weaken.
- **Revision loop with downstream cache invalidation**
  ([run_persona_pipeline.py:632-693](personas/run_persona_pipeline.py:632)).
  The `DOWNSTREAM_CHAIN` map + post-7a invalidation list is the
  non-obvious mechanic — when Pass 7a flags an upstream pass, the
  invalidation has to cascade through downstream caches AND past-7a
  caches (7b, 7c, Derive, assembled card). Baked this in commit
  `0452a23` after Plato caught a silent staleness. Phase B will have
  a cleaner story (no 7b/7c as `-pre` vs `-post` split) but the
  pattern is the same.
- **Atomic writes via `mkstemp` + `os.replace`**
  ([runtime/flows/shared/io.py:54-76](runtime/flows/shared/io.py:54),
  [personas/flows/shared/io.py:52-69](personas/flows/shared/io.py:52)).
  Both I/O modules converged on the same pattern. Twin implementation
  — not-identical but functionally the same.

### 5.2 Worth rethinking

- **Module-scope execution in `run_persona_pipeline.py`.** The file
  runs its work at import time (no `def main()`, no `if __name__`),
  uses `globals()[var_name] = result` in the revision loop
  ([L712](personas/run_persona_pipeline.py:712)). Works, but makes the
  pipeline un-importable for testing, un-callable from a task
  wrapper, and harder to inject a test double. Phase B's chunked
  architecture is the natural point to refactor to a `main()` + per-pass
  functions + a runner that composes them. The test fixtures are already
  pinned (Ibn Battuta's Perplexity + Gemini outputs) — unit tests are
  waiting for this.
- **Hardcoded model strings scattered across 10+ call sites.**
  Every `_claude_pass(... model="claude-opus-4-7")` and
  `call_claude(... model="claude-sonnet-4-6")` is a hardcoded literal.
  Changing the default per-phase model means patching N call sites.
  Phase B is the opportunity to pull these into a `MODEL_ASSIGNMENTS`
  dict indexed by pass name.
- **Pass 1-merge's 3-way contradiction check is a compression
  bottleneck.** The current pattern concatenates all three dossiers
  (up to ~500KB combined) into a single prompt. Phase B's chunked
  architecture lets each section's merge be a smaller, more focused
  prompt — but the final coherence pass (1.7) still has to see a
  reduced view of everything. Think about what that reduced view
  looks like before committing to chunk sizes.
- **Pass 7-pre citation verification uses Sonnet.** Citation
  verification is precision-demanding — can a Sonnet reliably detect
  when a claim cites something the primary_texts don't actually say?
  Worth benchmarking on held-out examples before locking Pass 7 into
  Sonnet for Phase B.
- **`_check_register` is string-match, not embedding-based.**
  [run_persona_pipeline.py:876-917](personas/run_persona_pipeline.py:876)
  uses literal match for `"Plato's "`, `"Plato was"`, etc. Works for
  named humans; has explicit overrides for Octopus (skip) and
  Whanganui River (match "Whanganui" not "River"). Phase B could
  consider an LLM-judge register check with the per-voice name in
  context — but string-match is probably fine. Don't over-engineer.

### 5.3 Worth adopting from `personas/notes/baseline_research/`

From the four compass_artifact files, deliberate omissions in v3.10
that Phase B could revisit (or confirm as still out-of-scope):

- **GraphRAG with Neo4j + Weaviate.** Baseline research frames it
  as "the single most impactful architectural choice."
  [ARCHITECTURE_NEXT_PHASE_HANDOFF §"Out of scope"](personas/notes/ARCHITECTURE_NEXT_PHASE_HANDOFF.md:108)
  explicitly keeps it out per Briefing v3.1's prosumer framing.
  Phase B will likely keep it out; noting for clarity.
- **Persona vectors / LoRA activation steering.** Same — out of
  scope per prosumer framing. Phase B keeps prompt-engineering only.
- **Benchmark-based automated evals** (CharacterBench, TimeChara,
  RoleKE-Bench). Current Pass 7a is freeform cross-model critique.
  Phase B's PB#6 says Pass 7 becomes primary quality gate — this is
  the natural place to land benchmark evals if they're in scope.
  `REBUILD_PLAN §Phase 3` says "Load-bearing per `→PB#6`" — this is
  still TBD.

### 5.4 What the rebuild will inherit

Concrete things the current code hands off cleanly to Phase B:

- **Working Pass 0a + Phase 0.5 infrastructure** — the intake
  (voice config + Perplexity + Gemini + DR prompt render) is solid.
  5 voice configs produced, 3 DR prompts generated, Pass 0a with
  Wikipedia grounding works. Phase B starts from here, unchanged.
- **Pass 1c + 1d** (primary text fetch + excerpt selection).
  SSRF-hardened fetch, Sonnet-curated ~30K char excerpts. These
  belong in Phase B's Pass 1.6 (CORPUS chunk) — reuse, don't rewrite.
- **Node 0 validation.** The validate_input logic is useful even in
  Phase B. The strict voice_mode enum can be revisited (PB plan #28
  explicitly flags this).
- **Test fixtures.** `personas/runs/ibn_battuta/01_research/` is
  pinned as the Phase B.4 test target. Perplexity output is ~108KB,
  regenerable for ~$5; Gemini is free.
- **Provocateur + runtime consumers are already stable.** PB#1
  ("don't touch Provocateur pipeline runtime") is honored by the
  current code boundary — the Derive pass produces exactly the
  8-field profile the council_config.json members array expects.
  Phase B can rewrite Phase 1-3 without touching Phase 4 (Derive) or
  the consumers.

### 5.5 Risks to pre-flag for Phase B

- **Schema sprawl.** PB#7 freezes meta-conventions after chunks
  1.1+1.2. The baseline schema sprawl risk is real — if 1.1's
  biographical evidence tags leak into 1.3's reasoning-method schema
  etc., the JSON validator becomes impossible to maintain. REBUILD_PLAN
  §Cross-cutting already flags `personas/schemas/` directory design.
- **Cost increase.** Current pipeline: ~$14-18/voice, ~60-120 min
  wall time. Phase B adds 6-7 Opus calls (chunked merge) but removes
  ChatGPT DR and simplifies Pass 1-merge. Net cost likely up
  ($20-30/voice?) — REBUILD_PLAN §Cross-cutting asks for a target
  before committing. Budget 12 voices × rebuilt pipeline + 12 voices ×
  existing Provocateur + Voice Pipeline; total pre-Athens might
  approach $500-700.
- **Rebuild during Athens-prep.** 12 voices need cards before Athens
  (3 weeks per CURRENT_STATE.md §8 critical path). Cleopatra/Arendt/
  Octopus/Ibn Battuta have partial or full artifacts on the v3.10
  pipeline; Phase B will re-produce them under the new architecture.
  Decision: either ship v3.10 artifacts for Athens and use Phase B
  post-Athens, OR block Athens on Phase B landing cleanly. Not my
  call but worth flagging — PB§"Out of scope" lists "Athens execution
  prep" so the intent is to land Phase B cleanly rather than rush.

---

## 6. Dead / stale inventory

### 6.1 Files that describe things that don't exist or aren't true

See §4.1 for the v3.7 / n8n / `thinking_budget` drift. Additional
items here are the "shouldn't exist" kind.

**`personas/README.md`** — describes a two-repo architecture (F-23)
and a file layout that doesn't match the monorepo tree. Either delete
and let `CLAUDE.md` + top-level `README.md` suffice, or rewrite to
match the real tree.

**`personas/inputs/dossiers/_archive/plato_claude_dr_v1_finished_card.md`**
— archived intentionally (see `dr_validation.py` error message
explicitly citing this filename as the wrong shape). Purpose:
regression-test fixture. Keep.

**`personas/runs/plato/01_research/chatgpt_dr_supplement.json`** —
legacy artifact from a pre-`d137791` run. Harmless (under `runs/`
which SESSION_HANDOFF.md §6 marks "DO NOT touch"), but it's the only
surviving trace of the Pass 3 DR supplement feature. Helpful
archaeologically.

### 6.2 Notes files that are historical

Per SESSION_HANDOFF.md §6 all run/*_archive/*/executed-plan notes are
"what not to touch." Confirmed:

- `runtime/notes/PROPOSED_pipeline_doc_change.md` — working doc, superseded
- `runtime/notes/updated_specs/*_delta.md` — 3 delta docs with
  Historical Note banners citing Opus 4.6 era (current is Opus 4.7).
  Banners are in place; no action needed.
- `personas/notes/SONNET_EXECUTION_PLAN*.md` (5 files) — executed plans
- `personas/notes/IMPLEMENTATION_AUDIT_v3_7.md` — historical; its
  observations about worked_provocations (§2 L111) correctly document
  the ChatGPT DR removal.
- `personas/notes/WALKTHROUGH_FIXES_PENDING.md` — banner added 2026-04-18
- `personas/notes/FIX_34_SECTION_BULLETS_DRAFT.md` — historical
- `personas/notes/baseline_research/` — 4 research artifacts, all
  historical. Their `README.md` indexes them correctly.

### 6.3 Data gaps (blocking pre-Athens)

Confirmed per CURRENT_STATE.md §6.1:

- `runtime/reference/speakers.json` — 202 speakers, all `bio` empty
  (confirmed via grep). Expected Speaker ID Pass 3 accuracy drop from
  70-85% to 40-50% per spec. **Still a blocker.**
- `runtime/flows/shared/council/council_config.json` — version
  `dev_stub_v3_audience_sharpened` (updated since SESSION_HANDOFF.md
  recorded `dev_stub_v2_with_selection_params`). All 12 profiles are
  hand-written stubs, not derived from real persona cards. **Still a
  blocker for production run.**
- `personas/inputs/voices/` — 5 of 12 voice configs
  (plato, cleopatra, hannah_arendt, octopus, ibn_battuta).
- `personas/inputs/dossiers/` — 0 of 12 complete Claude DR dossiers
  in the current tree (the `_archive/plato_claude_dr_v1_finished_card.md`
  is the wrong shape; the live Battuta dossier is on the user's
  Desktop per ARCHITECTURE_NEXT_PHASE_HANDOFF.md:86 but not in repo).
- `personas/inputs/dossiers/_dr_prompts/` — 3 of 12 (cleopatra,
  ibn_battuta, octopus). Remaining 9 can be generated quickly once
  Pass 0a runs for each voice.

---

## 7. Contract integrity check

All cross-component contracts walked from both sides.

### 7.1 Persona → Runtime (Provocateur Profile)

- **Producer:** `personas/run_persona_pipeline.py` §Derive →
  `runs/<slug>/provocateur_profile.json`
- **Schema:** 8 fields: `speaks_from`, `core_commitment`,
  `activates_on`, `goes_flat_on`, `stretch`, `translation_range`,
  `stance_tendency`, `medium`
- **Consumer:** `runtime/flows/shared/council/council_config.json`
  `members[]` array (currently stubs, not derived)
- **Validator:** `runtime/flows/shared/io.py:_REQUIRED_MEMBER_FIELDS`
  checks all 9 fields (`name` + 8 profile fields) at load time
- ✓ Producer and validator agree. Currently the council_config is
  hand-written; when real Derive output lands, the contract holds.

### 7.2 Persona → Voice Pipeline (assembled card)

- **Producer:** `run_persona_pipeline.py` §Final →
  `runs/<slug>/persona_card_assembled.json`. 35 fields at root + 2
  continuity fields + `metadata` block.
- **Consumer (not built):** planned Voice Pipeline
  (`runtime/flows/voice_flow.py`)
- **Invariants per contract:**
  - Voice Pipeline MUST drop `metadata` block before using as prompt ✓
    documented in HANDOFF.md + card metadata `worked_provocations_role`
  - Voice Pipeline MUST drop `worked_provocations` field ✓ documented
    in HANDOFF.md, CURRENT_STATE §5.10, Voice Pipeline spec L52, Pass
    7b prompt header
  - **EXCEPT** Persona Card v2 spec L413 says worked_provocations
    "Where it appears: Step 1 only" — F-03, unique contradiction
- ⚠ One doc contradicts four others. Voice Pipeline author must NOT
  follow the Card spec's L413 guidance.

### 7.3 Transcription → Researcher

- **Producer:** `runtime/flows/transcription_flow.py` §assemble_session_package
  → `runs/<run>/01_transcription/<session>/session_package.json`
- **Schema:** `{metadata: {session_id, session_title,
  session_description, session_format, track, date_time, venue,
  roster}, transcript: {speakers_present, turns[]}, review_queue:
  {low_confidence_attributions, diarization_flags, verify_markers}}`
- **Consumer:** `runtime/flows/researcher_flow.py:build_extraction_user_prompt`
  — reads metadata, transcript.speakers_present, transcript.turns,
  review_queue.verify_markers
- **Field invariants:**
  - Per-turn `confidence` preserved ✓ (validated on dev_msc_test per
    CURRENT_STATE §4.2)
  - `turn_index` preserved ✓ (added defensively by
    `load_session_package` in shared/io.py if absent)
  - `verify_markers` active consumed by Researcher ✓
- ⚠ F-18: producer's field name is `index`, consumer prompt calls it
  `turn_index`. Not a data bug — the LLM receives the JSON either
  way — but the doc language is misleading.

### 7.4 Researcher → Provocateur

- **Producers:** `researcher_flow.py` → `all_extractions.json` +
  `grouping.json`
- **Consumer:** `provocateur_flow.py` — Triage reads grouping
  abstracts, Selection reads extraction_ids, Formulation reads raw
  extractions for one theme at a time, Packaging reads everything
- **Field format conventions:**
  - Extraction IDs: `{session_id}:NNN` ✓
  - `lens` values underscore: `open_question` ✓
    (LENS_ORDER dict at [provocateur_flow.py:832](runtime/flows/provocateur_flow.py:832)
    uses the underscored form; the comment warns "silent mis-sort if
    this is wrong")
  - `engagement`: `null` for open questions ✓
  - `speaker`: `null` for synthesized open questions ✓
  - `responds_to`: same-session-only ✓
- **Integrity guarantees:**
  `_validate_clusters` + `_validate_themes` enforce closure +
  uniqueness + orphan promotion. Verified on dev_msc_test (106 extractions
  → 25 clusters → 6 themes, 0 duplicates, 0 orphans, 0 hallucinated)
  per Researcher spec §L305.
- ✓ Clean contract.

### 7.5 Provocateur → Voice Pipeline

- **Producer:** `provocateur_flow.py` §package_voice_briefings →
  `runs/<run>/03_provocateur/briefings/{voice_slug}.json`
- **Consumer (not built):** Voice Pipeline Step 1 reads the briefing.
- **Two-view structure:**
  - `narrative_briefing` (markdown) — the Step 1 user prompt
  - `full_theme_record` (structured JSON) — the Step 1 private
    reasoning surface
- ✓ Code and spec aligned (modulo F-16: spec example shows old field
  name `structured`).

### 7.6 Ingest → Transcription

- **Producer:** `runtime/ingest/pipeline.py:spawn_transcription`
- **Consumer:** `runtime/flows/transcription_flow.py`
- **Schema translation** handled by `sessions.py:build_session_json`
  — sessions.json's `title`/`description`/`date_time_start`/`venue+venue_sub`
  become session.json's `session_title`/`session_description`/
  `date_time`/`venue`.
- ✓ Producer test (`test_sessions.py::test_build_session_json_schema_translation`)
  asserts every field rename.
- ⚠ F-20: subprocess env passthrough omits `TRANSCRIPTION_CLAUDE_MODEL`.

---

## 8. Recommended next actions

Prioritised. Each is a one-liner; details in the referenced finding.

### P0 — PIPELINE-BLOCKING

0. **Fix F-27 IMMEDIATELY**: Delete the 4-line
   `{% if chatgpt_supplement %}Supplementary Analysis:\n{{ chatgpt_supplement }}{% endif %}`
   block from
   [`persona_pass_3_user.md:3-6`](personas/flows/shared/prompts/persona_pass_3_user.md).
   Currently every attempt to build a new voice will crash Pass 3 with
   `UndefinedError`. Athens is 3 weeks out and 7 voices remain unbuilt.

### P0 — consequential drift a fresh reader will trip on

1. **Fix F-03**: Persona Card v2 L413 must stop saying
   `worked_provocations` appears in Step 1. (1-line edit.)
2. **Fix F-13**: CURRENT_STATE.md §5.12 must stop saying `voice_mode`
   is freeform. (2-paragraph rewrite or removal of §5.12.)
3. **Fix F-05**: LLM_CALL_INVENTORY.md must stop calling the
   parameter `thinking_budget`. Rename throughout; update L7
   "Last read against the code" date. (~12 sed-style replacements.)
4. **Fix F-28**: Reconcile the personas venv Python version. Either
   rebuild `personas/venv` on Python 3.12 (recommended; matches
   CLAUDE.md + CURRENT_STATE claim) or update the docs to note
   "runtime: 3.12, personas: 3.9" with rationale. Pipeline works
   today on 3.9 (verified via live imports) but the documentation
   lies.
5. **Fix F-29**: Update the v3.10 persona pipeline spec body model
   assignments (Passes 2, 3, 4a, 5) to match the changelog claim:
   Opus 4.7 + adaptive thinking, max_tokens as implemented. ~8 spots.

### P1 — correctness-adjacent (would fail verification next time)

4. **Fix F-12**: Remove or reword Pass 3 ChatGPT DR supplement
   description in Persona Pipeline v3.10 body.
5. **Fix F-06**: Mark `LLM_CALL_INVENTORY.md §7.1-7.5` as resolved
   (or move to a "Historical diagnostic" section).
6. **Fix F-16**: Update Provocateur spec L384 sample to use
   `full_theme_record` instead of `structured`.

### P2 — spec-body cleanup that new code would flag

7. **Fix F-07–F-09**: n8n references in Transcription, Persona
   Pipeline v3.10, Voice Pipeline. Prefect is the orchestrator.
8. **Fix F-01, F-10, F-11, F-14**: remaining v3.7 references in
   Briefing, Provocateur spec, Voice Pipeline spec, HANDOFF.md.
9. **Fix F-15**: council/README.md version string + v3.7 reference.
10. **Fix F-21**: comment at `run_persona_pipeline.py:747-748`.
11. **Fix F-23**: rewrite or delete `personas/README.md`.
12. **Fix F-24**: refresh CURRENT_STATE.md §6.1 counts.

### P3 — ergonomic

13. **Fix F-17**: Document `TRANSCRIPTION_CLAUDE_MODEL`,
    `RESEARCHER_CLAUDE_MODEL`, `PROVOCATEUR_CLAUDE_MODEL` in
    LLM_CALL_INVENTORY §5.1 and CURRENT_STATE §7.2.
14. **Fix F-18**: align Researcher prompt + spec to field name
    `index` (or add turn_index to the transcription output — harder).
15. **Fix F-20**: add `TRANSCRIPTION_CLAUDE_MODEL` to
    `_subprocess_env`.
16. **Fix F-22**: strip `</content>` tags from `personas/HANDOFF.md`.
17. **Fix F-26**: clarify `.env.example`'s `INGEST_FLOW_CMD` line.
18. **Fix F-30**: Update
    `persona_pass_1merge_contradiction_system.md` to say "two or three"
    (or add `{% if %}` branching) — currently says "two".
19. **Fix F-31**: Update
    `persona_pass_1merge_three_way_user.md:1` Jinja comment header
    "Claude Sonnet" → "Claude Opus 4.7 + adaptive thinking".
20. **Fix F-32**: Delete the orphaned
    `persona_pass_1merge_contradiction_user.md` (2-way variant,
    superseded). Confirmed no code references it.

### P4 — design-level (not strictly "fixes", but worth flagging)

18. **F-25 Octopus medium**: decide whether council_config stub
    (FLUX image) or Briefing v3.1 (chromatophore shader) is the
    intent. Affects Downstream Render pipeline design.
19. **F-02 stale Architecture_v1 reference**: either rewrite
    Architecture doc or remove the Briefing's pointer.

### P5 — Phase B prep

20. Work through `personas/notes/REBUILD_PLAN.md` remaining
    sections (Phase 1 chunked merge, Phases 2-4, Phase 5). §5.1-5.5
    above is fresh-eye input for those sections.
21. Audit §7 contracts before Phase B lands — schema changes at
    the Persona → Provocateur handoff must be reflected in
    `_REQUIRED_MEMBER_FIELDS` validator and council_config.json
    simultaneously.

---

## 9. Repository reorganization plan

Motivation: the repo has accumulated three kinds of clutter that drown
out production signal — historical execution plans (SONNET_EXECUTION_PLAN*
series, ~3,400 lines), per-run artifacts (`runs/` on both sides), and
stale specs (`Architecture_v1`, `Infrastructure_Setup`, plus all
`*_delta.md` docs that described transitions already absorbed into the
current specs). A fresh reader or VM deploy should be able to pick up
"what the system is now" without spelunking through "how it got there".

### 9.1 Four-category split

```
ai-assembly/
├── README.md                  # Top-level GitHub landing — MUST describe the tree
├── CLAUDE.md                  # Claude Code session context — MUST describe the tree
├── docs/                      # PRODUCTION: current specs
│   ├── README.md                  # Staleness index
│   ├── references.md              # NEW: pointer into research/
│   ├── AI_Assembly_Briefing_v3_1.md
│   ├── AI_Assembly_Persona_Card_v2.md
│   ├── AI_Assembly_Persona_Pipeline_v3_10.md
│   ├── AI_Assembly_Researcher_Pipeline.md
│   ├── AI_Assembly_Provocateur_Pipeline.md
│   ├── AI_Assembly_Voice_Pipeline.md
│   ├── AI_Assembly_Transcription_Pipeline.md
│   ├── AUDIENCE_BRIEF.md          # Canonical audience source (declared so in its own top-matter)
│   ├── LLM_CALL_INVENTORY.md
│   ├── CURRENT_STATE.md
│   └── design/
│       ├── AI_Assembly_DesignPrinciples.md
│       └── Nine_Modes_of_Implication.md
├── runtime/                   # PRODUCTION code
├── personas/                  # PRODUCTION code
│   └── HANDOFF.md                 # Cross-repo contract (production, active)
├── research/                  # PRESERVED: grounding material, NOT deletable
│   ├── README.md                  # Index
│   └── baseline_research/
│       ├── compass_artifact_wf-cc778da2-…md  # 4-layer architecture
│       ├── compass_artifact_wf-45560dac-…md  # DR-tools field guide
│       ├── compass_artifact_wf-865974da-…md  # Repeatable pipeline playbook
│       └── compass_artifact_wf-109ac10a-…md  # Athens 2026 audience terrain
└── _workspace/                # Out of scope for reviews + VM deploys
    ├── planning/              # FORWARD-LOOKING, active
    │   ├── REBUILD_PLAN.md
    │   └── ARCHITECTURE_NEXT_PHASE_HANDOFF.md
    └── archive/               # ELIGIBLE FOR PRUNING (see §9.3)
        ├── specs/
        │   ├── AI_Assembly_Architecture_v1.md        # STALE per docs/README.md
        │   └── AI_Assembly_Infrastructure_Setup.md   # STALE per docs/README.md
        ├── fix-plans/
        │   ├── SONNET_EXECUTION_PLAN.md
        │   ├── SONNET_EXECUTION_PLAN_PHASE_A.md
        │   ├── SONNET_EXECUTION_PLAN_ROUND_2.md
        │   ├── SONNET_EXECUTION_PLAN_ROUND_3.md
        │   ├── SONNET_EXECUTION_PLAN_repo_audit.md
        │   ├── WALKTHROUGH_FIXES_PENDING.md
        │   ├── IMPLEMENTATION_AUDIT_v3_7.md
        │   ├── FIX_34_SECTION_BULLETS_DRAFT.md
        │   ├── PROPOSED_pipeline_doc_change.md
        │   └── delta-docs/
        │       ├── TRANSCRIPTION_v2_to_v2_1_delta.md
        │       ├── RESEARCHER_v2_to_v3_delta.md
        │       └── PROVOCATEUR_v1_to_v2_delta.md
        ├── session-artifacts/
        │   ├── SESSION_HANDOFF.md
        │   └── FRESH_REVIEW_2026_04_19.md   # this doc, once superseded
        └── runs/                     # dev_msc_test + any future run artifacts
```

In-place archive subdirs (`personas/inputs/voices/_archive/`,
`personas/inputs/dossiers/_archive/`, `runtime/flows/shared/prompts/_archive/`)
are small and scoped — leaving them in place is fine. Consolidating
them under `_workspace/archive/in-tree/` is a judgment call; not worth
breaking git history for.

### 9.2 Decision rule

- **Production** (`docs/`, code, AUDIENCE_BRIEF): the current state of
  the system. Ships to the VM. In scope for every code review.
- **Research** (`research/`): rigorous reference material that
  *grounds* a design decision. Useful forever as rationale ("why is
  the pipeline like this?"). Not deletable.
- **Planning** (`_workspace/planning/`): forward-looking, currently
  active design docs for unbuilt work. Promoted into `docs/` when the
  work lands; deleted if abandoned.
- **Archive** (`_workspace/archive/`): historical detritus —
  executed fix plans, prior session notes, superseded specs, stale
  run artifacts. Eligible for deletion once you trust the current
  state has absorbed their content.

### 9.3 Pruning rule

Review `_workspace/archive/` at two natural checkpoints and delete
what's been superseded:

1. **After each successful Athens run** (post-Night-1, post-Night-2,
   post-Night-3): delete run artifacts in `archive/runs/` older than
   the current conference. The `dev_msc_test` fixture can stay if
   it's still pinned as a test input; otherwise it moves too.
2. **After each codebase milestone** (e.g., Phase B persona rebuild
   lands; Voice Pipeline ships; Athens concludes): delete fix plans
   in `archive/fix-plans/` whose target state is now the current
   codebase. The SESSION_HANDOFF.md and FRESH_REVIEW_2026_04_19.md
   get moved to `archive/session-artifacts/` as soon as a newer
   state snapshot exists.

The invariant: **if you can't name what `archive/foo.md` describes
that isn't already in `docs/` or code, delete it.** The point of
archive is to be temporary storage on the way to deletion, not a
graveyard.

### 9.4 Where the tree gets explained (GitHub logic)

Three places need to describe the split so a fresh GitHub visitor
or Claude Code session doesn't have to infer it:

- **`README.md`** (top-level) — the page GitHub renders on the repo
  landing. Existing "Structure" section at L10-15 should be replaced
  with the four-category tree and a one-line description of each.
  This is the primary explanation.
- **`CLAUDE.md`** (top-level) — the context every Claude Code session
  loads. Existing "Repo layout" section at L3-8 should mirror
  `README.md`'s structure paragraph and add the convention:
  *"`_workspace/` is out of scope for reviews by default; mention it
  explicitly if you want me to look."*
- **`docs/README.md`** — the existing staleness index. Extend with a
  "What's NOT in `docs/`" note pointing into `research/` and
  `_workspace/planning/`, so a reader looking for architecture
  rationale or forward-looking design knows where to go.

Optionally: a one-line `_workspace/README.md` + `research/README.md`
each, explaining the category's purpose, so the directories are
self-describing when someone clicks into them from the GitHub file
browser.

### 9.5 Migration (high level)

This is a single git operation, one commit:

1. `git mv` the archive + planning + research material into the new
   tree. Stage them as renames so git tracks history (`git log --follow`
   continues to work on the moved files).
2. Update pointers in production docs that currently reference moved
   files. Known pointer rewrites needed:
   - Briefing v3.1 L148, L288 → `Architecture_v1.md` (now at
     `_workspace/archive/specs/`)
   - Briefing v3.1 related-docs list L339-347 (same)
   - CURRENT_STATE.md §0 quick-map tree
   - CLAUDE.md "Where specs live" list at L34-43
   - `personas/notes/baseline_research/README.md` → `research/baseline_research/README.md`
   - `docs/SESSION_HANDOFF.md` references (moving the doc itself;
     fix pointers into it from CURRENT_STATE and elsewhere)
3. Update `README.md` + `CLAUDE.md` + `docs/README.md` structure
   sections to reflect the new tree.
4. Add `research/README.md` and `_workspace/README.md` stubs.
5. Add `docs/references.md` stub pointing into `research/` with a
   one-line-per-file index.
6. Add a `.gitattributes` rule excluding `_workspace/` from
   `git diff` by default (optional; reviewer ergonomics).

Commit message shape: `refactor: reorganise into production / research
/ planning / archive tree — no code changes`.

**Tradeoff unchanged from the earlier discussion:** git history on
moved files still traces via `--follow`, but a reviewer unfamiliar
with the move will see noisy renames in `git log`. Worth doing once,
as a single clean commit, at a quiet moment — not split across
multiple PRs.

---

*End of review.*

*First pass (morning 2026-04-19): ~260 files opened — canonical docs,
major Python modules, active prompts, tests, run-artifact directory
listings. Produced F-01 through F-26.*

*Second pass (after user pushback on overclaim): read the 32 persona
prompts in full (including 1086-line `pass_0b_dr_prompt.md`), stale
specs in full, 4 baseline_research compass_artifacts, HTML templates,
`app.js`, and ran live imports + runtime test suite + per-template
Jinja render in both venvs. Produced F-27 through F-35. F-27 is
pipeline-blocking.*

*Third pass (after second user pushback on runtime gaps): read every
previously-skipped runtime file — both scripts (470 lines), 4 archive
prompts (299 lines), `PROPOSED_pipeline_doc_change.md` + 3 delta
docs in full, the 320-line `_manifest.json`, baseline variant run
directories, per-session extraction + cluster + formulation
artifacts, sessions.json + speakers.json at full-file shape. Added
F-36 (positive). No new bugs.*

*Summary: 29/29 runtime tests pass, every module imports clean in
both venvs, every cross-stage contract verified on real
dev_msc_test artifacts, every current spec cross-checked against
the current code. The one pipeline-blocking bug (F-27) is a 4-line
template delete. Roughly 30 doc-drift items, mostly v3.7 leftovers
and stale model assignments, are cataloged in §4 and prioritised in
§8. Output doc ~10K words.*
