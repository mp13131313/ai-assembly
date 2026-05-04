# Runtime — onboarding / fresh-session pickup

**Date created:** 2026-05-01
**Scope:** Everything you need to pick up runtime work cold. Read this first. Then OPEN_ITEMS.md (in this folder) for what's open.
**Cross-references:** `_workspace/planning/ONBOARDING.md` (project-wide) for repo conventions, project-vs-code separation, common operations. This doc is the runtime-pipeline-specific layer on top.

---

## What runtime is, in one paragraph

The overnight pipeline that consumes the day's human sessions and produces voice artifacts the next morning. Six stages: transcription (audio → text), researcher (text → themes), provocateur (themes → per-voice formulations), Voice Pipeline (formulations → voice artifacts in three steps + validation + continuity), **editor (voices → dossiers; shipped 2026-05-03 PM)**, publish (handoff to downstream). Plus broadsheet, microsite, Substack, closing show — still not built.

Implementation lives at `runtime/`. The persona pipeline (which builds the cards runtime consumes) lives at `personas/`. They are separate workstreams with separate venvs. This doc covers `runtime/` only.

**Operator priority calibration** (per project ONBOARDING.md, refreshed 2026-04-29): *"Athens needs the full runtime stack ready, not just the 12 persona cards."* When recommending build-side improvements, check whether they delay runtime work that's already on the critical path. Persona-side hardening (FU#42 split-card, FU#50(1) Pydantic enforcement, etc.) does NOT pre-empt runtime workstream items. Surface runtime gaps proactively.

---

## First 20 minutes — read in this order

1. **This doc** (you are here)
2. **`_workspace/planning/runtime/OPEN_ITEMS.md`** — runtime-specific authoritative open items
3. **`docs/AI_Assembly_Voice_Pipeline.md`** — the runtime contract for the Voice Pipeline (the central runtime module). v2.1, ~1290 lines. Gold standard for what's built + what each step does + field routing.
4. **`docs/AI_Assembly_Briefing_v3_1.md`** — project source of truth (target state). Re-read lines 91, 167, 177, 179, 181 (the Step 3 specification).
5. **`docs/AI_Assembly_Frame_Concept_v1.md`** — frame layer (broadsheet / microsite / Substack / closing show). Voice Pipeline produces artifacts that the frame layer wraps. This doc is currently stale per FU#61 finding (strip rule needs to be voice-register-conditional) — see OPEN_ITEMS A4.
6. **`_workspace/planning/PIPELINE_DOWNSTREAM_DESIGN_2026_04_30.md`** — the architectural reasoning for everything downstream of Voice Pipeline (Step 3 → editor → audience surfaces). Surfaces 6 gating decisions A-F. Currently untracked; commit before it's lost.

Stop after this unless the task demands more. ~30-45 min of working knowledge.

---

## What's built, what's validated, what's not

### Runtime modules (`runtime/flows/`)

```
runtime/flows/
├── transcription_flow.py            ✅ built
├── researcher_flow.py               ✅ built
├── provocateur_flow.py              ✅ built (1368 lines)
├── voice_flow.py                    ✅ built — orchestrator
├── voice/                           ✅ built end-to-end
│   ├── card_assembly.py
│   ├── step1_private_reasoning.py
│   ├── step1_validation.py
│   ├── step2_first_draft_artifact.py
│   ├── step3_amended_artifact.py    💤 DORMANT for Athens (A1 RESOLVED 2026-05-01: Option A skip; module preserved for ~2-day re-add post-Athens)
│   ├── continuity.py
│   └── publish.py
├── publish_flow.py                  ✅ built — cross-pipeline aggregation
└── editor_flow.py                   ✅ BUILT 2026-05-03 PM (commit `1437dfc`); closing-prompt v1→v2 rewrite still pending (B1 sub-task)
```

### Validation status

| Flow | Validated end-to-end | Evidence |
|---|---|---|
| Voice Pipeline Steps 1+2 | ✅ Plato solo + Plato/Cleopatra dual + 4-voice (Plato/Cleopatra/Dostoevsky/Battuta) | dryruns #2, #3, #4 (2026-04-29) + Legitimacy Tests (2026-05-01) |
| Voice Pipeline Step 3 | 💤 DORMANT for Athens (A1 RESOLVED 2026-05-01 — Option A skip; module/prompt preserved for ~2-day re-add post-editor/microsite) | dryrun #4 (2026-04-29) validated mechanics in old FU#49E correspondence-shape framing; framing dropped 2026-04-29; option A chosen 2026-05-01 |
| Validation nodes (anachronism + constitutional) | ✅ on Plato + Cleopatra; diagnostic-only by spec (FU#62 path B 2026-05-01) | dryruns #2 + the FU#61 v3 test (2026-04-30) |
| Continuity flow | ✅ verified end-to-end after `ccc6229` bugfix (was broken under `--skip-step3` Athens production CLI) | Legitimacy Test 1, 3-night sequence (2026-05-01) |
| Multi-night sequence | ✅ exercised (Convention A run_dir-per-night, continuity overlay loads correctly) | Legitimacy Test 1 (2026-05-01) |
| Multi-voice 4-voice engagement | ✅ all 4 shipped voices in parallel | Legitimacy Test 1 + 2 + 2 v2 (2026-05-01) |
| Step 2 `focus_decision` synthesis branch | ✅ verified (4/4 voices weave under conceptually-converging input on Test 2 v2; under post-2026-05-02 routing+prompt refactor, Test 3 shows synthesis must now be earned with explicit weight-equal reasoning + through-line claim) | Legitimacy Test 2 + 2 v2 + Test 3 |
| Step 2 `focus_decision` focus-on-one branch | ✅ structurally fixed 2026-05-02 (routing refactor + prompt rewrite); Test 3 shows 2/4 voices fully focused on a single response, 1/4 anchored synthesis, 1/4 earned synthesis with field-grounded weight_assessment | commits `d9ca3f9` + `dfb46f7`; OPEN_ITEMS C18 |
| `thinking_tokens` runtime accounting | ✅ fixed (was always 0; now computed via count_tokens subtraction) | commit `8c47e1f`; verified live in Test 2 v2 |
| Anthropic prompt caching | ✅ ENABLED 2026-05-02 — Stage 1 single-breakpoint (commit `c4804d6`); ✅ EXTENDED 2026-05-02 PM — Stage 2 prefix caching with two breakpoints + continuity opt-out (commit `d9ca3f9`). Live verified: Step 2 reads prefix Step 1 wrote (cache_read=20,086 tokens). Athens savings ~$13 across 3 nights (modest in absolute terms; see C19a for corrected pricing math). | commits `c4804d6` + `d9ca3f9` |
| Cache token tracking persisted in artifacts | ✅ LANDED 2026-05-02 PM — step1/step2/step3/continuity all persist `cache_creation_input_tokens` + `cache_read_input_tokens` for accurate post-hoc cost reconciliation | commit `d9ca3f9` |
| Voice Pipeline field routing (voice/expression in Step 1; reasoning fields in Step 2) | ✅ REFACTORED 2026-05-02 PM — closes the prompt/system mismatch where Step 2's decision_1 cited `finds_compelling`/`resists` but the fields weren't loaded | commit `d9ca3f9` |
| Voice Pipeline closing prompts (Step 1 + Step 2) | ✅ REWRITTEN 2026-05-02 PM under Haltung lens — section-by-section word-by-word challenge; Step 2 adds `<weighing>` discrete pre-focus phase + `weight_assessment` first-class field | commit `d9ca3f9` + `dfb46f7` |
| Editor Pipeline (Claudia Pinchbeck → dossier) | 🟢 IMPLEMENTATION SHIPPED 2026-05-03 PM (commit `1437dfc`); v2 spec canonical (`docs/AI_Assembly_Editor_Pipeline.md`); wiring proven via single-dossier live test 2026-05-04 (~$1.50). Pending: Claudia full 35-field card (voices thread) + closing-prompt v1→v2 rewrite (~30-60 min). | OPEN_ITEMS A2 (✅ fully resolved) + B1 (🟢 implementation shipped) |
| Provocateur cross-night exclusion (C9) | ✅ LANDED 2026-05-02 — content-based matching by normalized theme title (theme_ids not stable across Researcher runs); CLI `--prior-nights` arg | commit `99759cb`; 15 unit tests passing |
| publish_flow.py per-theme cross-night collision | ✅ FIXED 2026-05-02 — per-night subdirectory `themes/night_<N>/<theme_id>.json` | commit `e0921de` |
| Defensive `--night` check on voice_flow + publish_flow | ✅ LANDED 2026-05-02 — `assert_run_dir_night_matches()` refuses to run if --night doesn't match run_dir's embedded night number; catches silent cross-night corruption | commit `c0d724e`; 9 unit tests passing |
| Automation orchestrator | ✅ BUILT 2026-05-02 PM — full orchestrator with 22 trigger-path tests + templated systemd unit + path-prefix Caddyfile + lifecycle doc | `runtime/scripts/overnight_orchestrator.py` + `docs/AI_Assembly_Runtime_Lifecycle.md` + OPEN_ITEMS C22 |
| publish_flow.py end-to-end exercise | ❌ never run against real Researcher/Provocateur outputs (collision bug now fixed; safe to exercise) | OPEN_ITEMS C3 |

### Downstream of Voice Pipeline

| Component | Status |
|---|---|
| Editor / Frame layer | 🟢 IMPLEMENTATION SHIPPED 2026-05-03 PM (commit `1437dfc`); v2 spec canonical (`docs/AI_Assembly_Editor_Pipeline.md`); 38 tests; admin drilldown live. Wiring proven via single-dossier live test 2026-05-04. Pending: Claudia full 35-field card (voices thread) + closing-prompt v1→v2 rewrite (~30-60 min). See OPEN_ITEMS B1. |
| Microsite | ❌ NOT BUILT — operator designing; consumes `published_artifacts/`. See OPEN_ITEMS B2 |
| Broadsheet / Edition Pipeline | ❌ NOT BUILT — folded into Editor Pipeline (B1) |
| Substack draft pipeline pass | ✅ DROPPED 2026-05-02 PM per Editor Pipeline spec (microsite-only) |
| Closing-show pipelines (theme ID, matrix mapping, video) | ❌ UNSPECIFIED + NOT BUILT — see OPEN_ITEMS B5 |
| Day 4 goodbye | ❌ UNSPECIFIED — see OPEN_ITEMS B6 |
| Render layer for non-text artifacts (Marley → Suno; Octopus → shader) | ⚠️ Octopus WebGL renderer substantially built 2026-05-02 PM; Marley TBD. See OPEN_ITEMS B7 |
| Admin console | ❌ NOT BUILT — see OPEN_ITEMS B8 |
| **VM infrastructure / orchestration** | ✅ SPEC + IMPLEMENTATION LANDED 2026-05-02 PM. `docs/AI_Assembly_Infrastructure.md` (deployment) + `docs/AI_Assembly_Runtime_Lifecycle.md` (operations) + orchestrator script + 22 tests + multi-service Caddyfile + dual-repo deploy keys. Awaiting operator hands for VM provisioning. See OPEN_ITEMS B10. |

---

## Architecture in working memory

### The pipeline at a glance

```
Day's audio
    ↓
Stage 0 — Transcription (AssemblyAI Universal-3 Pro + multi-pass speaker attribution)
    Output: 01_transcription/<session>/session_package.json
    ↓
Stage 1 — Researcher (Opus 4.7 + adaptive thinking; extract atomic positions, group via KJ)
    Output: 02_researcher/all_extractions.json + grouping.json
    ↓
Stage 1b — Provocateur (5-stage: Triage A + B parallel, Selection deterministic Python, Formulation per-pair, Packaging)
    Output: 03_provocateur/briefings/<voice_slug>.json (one per voice; markdown narrative_briefing + structured full_theme_record)
    ↓
Stage 2 — Voice Pipeline (per-night, ~30-50 min wall on 10-voice panel)
    Step 1 (Opus 4.7 + thinking, 64K max): private reasoning per (voice, formulation) pair
        ↓ 04_voice/step1_detailed_responses/<voice>__<theme>.json
    Validation (OpenAI ladder gpt-5.4 reasoning_effort=high, 8K max): anachronism + constitutional
        ↓ 04_voice/validation/<voice>__<theme>.json + manifest flag
        ⚠️ regen-on-flag NOT implemented (FU#62) — diagnostic only
    Step 2 (Opus 4.7 + thinking, 64K max): first-draft artifact per voice
        ↓ 04_voice/step2_first_draft_artifacts/<voice>.json
    Step 3 (Opus 4.7 + thinking, 64K max): amended artifact per voice (UNDER REDESIGN — see OPEN_ITEMS A1)
        ↓ 04_voice/step3_amended_artifacts/<voice>.json
        + 04_voice/responded_to_graph_night_N.json
        + 04_voice/themes_to_voices_night_N.json
    Continuity (Sonnet 4.6 + thinking, 8K max, Nights 2+3 only): per-voice summary
        ↓ <PROJECT_ROOT>/voices/<voice>/continuity_night_N.json
    ↓
Stage 3 — Publish (cross-pipeline aggregation)
    Output: <PROJECT_ROOT>/published_artifacts/nights/night_N/<voice>.json + _index.json
            <PROJECT_ROOT>/published_artifacts/voices/<voice>_multi_night.json
```

### Convention A — multi-night structure (documented 2026-04-29)

**One run_dir per night.** Each Athens night is a complete, self-contained pipeline run from transcription through publish:

```
<PROJECT_ROOT>/runs/athens_2026_2026_05_07_night1/
                ├── 01_transcription/
                ├── 02_researcher/
                ├── 03_provocateur/
                └── 04_voice/

<PROJECT_ROOT>/runs/athens_2026_2026_05_08_night2/   (same shape, fresh inputs)
<PROJECT_ROOT>/runs/athens_2026_2026_05_09_night3/   (same shape, fresh inputs)
```

Voice files inside each run_dir are unsuffixed (`step2_first_draft_artifacts/plato.json`, not `plato_night_1.json`) — night is implicit in run_dir.

**Cross-night state lives at PROJECT_ROOT, not inside run_dirs:**
- `<PROJECT_ROOT>/voices/<slug>/continuity_night_<N>.json`
- `<PROJECT_ROOT>/published_artifacts/nights/night_<N>/<slug>.json`
- `<PROJECT_ROOT>/published_artifacts/voices/<slug>_multi_night.json`

Per `docs/AI_Assembly_Voice_Pipeline.md` §"Multi-night convention".

### The card → system prompt assembly contract

Voice Pipeline reads `<PROJECT_ROOT>/voices/<slug>/07_persona_card_assembled.json` (produced by personas pipeline). 36 generated card fields + 2 continuity nulls. Field-routing matrix per step (full table in `docs/AI_Assembly_Voice_Pipeline.md` §"Card → System Prompt Assembly"):

- **Foundational fields** (1-13): every step. Identity, constitution, boundaries, `voice_temporal_stance.default`.
- **Reasoning fields** (14-21 minus `smoke_test_chains`): Step 1 + Step 3.
- **Voice/Expression fields** (22-28): Step 2 + Step 3.
- **Artifact fields** (29-36): Step 2 + Step 3 (Step 3 may reselect form from `medium` family).

**5 strip rules (load-bearing):**
1. Drop `metadata` always (build-time provenance)
2. Drop `smoke_test_chains` always (NEVER few-shot)
3. Drop `reference_only_passages` from Step 2 + Step 3 (copyright; Step 1 keeps it)
4. Drop `curated_corpus_passages.corpus_metadata` (nested; FU#41 strip rule)
5. Drop `bold_engagement_topics` always (FU#57 — pre-loaded courage menu pulled reasoning toward predetermined topics)

### Validation policy (Athens production — per FU#62 path B, 2026-05-01)

Validation is **diagnostic-only**: flags are recorded in `04_voice/manifest.json` `validation_failures[]` for operator morning-review; no regen, no retry, the pipeline ships flagged outputs to Step 2 unchanged.

- **Night 1: ON** for all voices (catches drift in fresh card deployment; operator reviews flags morning of Day 2 and intervenes voice-side if material)
- **Nights 2 + 3: OFF** (no regen → pure cost without remediation; operator morning-review handles correction)
- **Dryrun work: always `--skip-validation`** (Step 1 outputs are cached → validation re-runs against unchanged outputs → same flags → ~20-40 min/voice for nothing)

Spec (`docs/AI_Assembly_Voice_Pipeline.md` §"Regeneration policy" + §"Default policy for Athens" + §"Cost & Envelope") was updated 2026-05-01 to match this; spec/impl now aligned.

---

## Active branch + recent history

**Branch:** `voice-pipeline-v2.1-align-revert` — 38+ commits ahead of `main`. Pushed.

**Branch history (chronological — most recent first):**

*2026-05-02 (afternoon — voice pipeline + editor pipeline session):*
- *(pending commit)* docs(editor-pipeline): Editor Pipeline v1 spec + OPEN_ITEMS A2/B1 updates — full editor pipeline contract; Claudia Pinchbeck as named 13th Assembly member; dossier-by-theme architecture; marathon-distance issue numbering; ~$3-5 Athens cost. Resolves A2 fully, moves B1 from NOT BUILT to SPEC LANDED.
- `c4d8346` docs(planning): HANDOFF 2026-05-02 + ONBOARDING + OPEN_ITEMS for voice pipeline session
- `dfb46f7` voice(step2): restore stripped 'transform form, carry substance' guardrail
- `d9ca3f9` voice: routing refactor + prompt rewrite + prefix caching + cost correction (10 files; +286/-182). Synthesis-bias structurally addressed. Test 3 validated.

*2026-05-02 (morning):*
- `c0d724e` feat(runtime): defensive --night check + automation orchestrator design (C22)
- `a6755d9` personas/Pass-0b: amend non_human_organism template to be compass-permissive (persona thread)
- `e0921de` fix(publish_flow): per-night subdirectory for per-theme files
- `c4804d6` feat(voice + provocateur): C19a Anthropic prompt caching enabled + latent continuity unpack-tuple bugfix
- `99759cb` feat(provocateur): C9 cross-night (member, theme) exclusion filter ⚠️ Athens-blocking
- `4f0b3a0` docs(planning): HANDOFF + ONBOARDING reflect Phase 2 late-session work

*2026-05-01:*
- `ee824be` docs(planning): C19 audit + C20 memo + Plato Socrates-death anachronism
- `1a62043` docs(planning): C15 closed — misdiagnosed (lineage IS populated under .lineage.*)
- `69372b7` docs(planning): C18 Test 2 v2 result — title-only fix insufficient
- `366dfe2` docs(planning): external review findings on legitimacy test
- `8c47e1f` fix(voice + personas): thinking_tokens always 0 across both pipelines (count_tokens subtraction approach)
- `1c83034` voices/ONBOARDING: DO interrogate Pass 0a review_doc framings (persona thread)
- `fe8159a` docs(planning): legitimacy-test verification + C15 (Step 2 metadata gap)
- `ccc6229` fix(voice_flow): continuity must fire after Step 2 when Step 3 is skipped (A1) ⚠️ Athens-blocking
- `80ac3f1` docs(planning): A1+A2+A3 decisions + C-section closures + Voice Pipeline spec updates
- `242de7b` feat(runtime/scripts): speaker enrichment + ai_assembly schedule from program data
- `d4cea03` fix(runtime): FU#60 compliance across researcher + provocateur + transcription
- `9eb0222` docs(planning): FU#61 v3 LANDED — prompt-driven approach validated end-to-end
- `91947a7` feat(personas/Pass-4b): FU#61 land — audience-engagement outcome question
- `a6fa848` fix(personas/clients): retry-on-stream-drop for streaming Claude calls
- `57cb0b5` docs(planning): correct FU#61 Option B — Pass 4b not Pass 5 (quality_criteria locus)
- `ba2bcd8` docs(planning): FU#61 v1 empirical verdict + v2 criterion sharpening
- `e90f1e2` fix(personas): add override=True to run_pass0a_voice_config load_dotenv
- `8c1d5f9` docs(planning): file FU#60 + FU#61 — thinking observability landed; voice-side Layer-1 quality_criteria
- `1aefd70` docs(planning): flag Step 3 for redesign-from-briefing tomorrow
- `a279e3f` docs(planning): voice-pipeline dual-dryrun handoff + add Frame Concept v1
- `e89dfc4` fix(voice-pipeline): derive responded_to_graph edges from voices_read + decision (post-dryrun #4)
- `0381278` fix(voice-pipeline): drop temperature, add display: summarized — match Anthropic docs §"Feature compatibility" + persona-pipeline FU#60
- `f6ee392` feat(voice-pipeline): drop title/subtitle from voice + derive themes_covered + Convention A doc
- `f68bc3f` fix(voice-pipeline): post-dryrun tuning — soften validator (c) + extraction-ID bookkeeping + load_dotenv override

Branch is shared with persona thread; both threads cohabited cleanly with zero conflicts. Eventual merge to main pending operator decision.

**athens-2026 git** (separate private repo at `mp13131313/ai-assembly-athens2026-voices`): Cleopatra v3 finalized (`c89d186`), Dostoevsky v3-pattern landed (`5088d67`).

---

## Common runtime operations

### Run Voice Pipeline on a project's run_dir

```bash
cd "/Users/aienvironment/Desktop/AI Assembly/code"

# Athens production (Steps 1+2 + validation Night 1 only + continuity Nights 2+3 + publish)
# Step 3 SKIPPED per A1 decision 2026-05-01; --skip-validation on Nights 2/3 per FU#62 path B
runtime/venv/bin/python runtime/flows/voice_flow.py \
  "/Users/aienvironment/Desktop/AI Assembly/projects/<project>/runs/<run_dir>" \
  --night 1 \
  --project "/Users/aienvironment/Desktop/AI Assembly/projects/<project>" \
  --skip-step3

# Single voice only (dryrun pattern)
runtime/venv/bin/python runtime/flows/voice_flow.py \
  "<run_dir>" \
  --night 1 \
  --voices <voice_slug> \
  --project "<project_root>" \
  --skip-validation \
  --skip-step3 \
  --skip-continuity
```

CLI flags:
- `--night N` (required, 1-3) — controls continuity override loading
- `--voices SLUG[,SLUG...]` — filter to specific voices
- `--project PATH` — explicit PROJECT_ROOT (overrides env var)
- `--skip-validation` — disable both validation nodes (DEV USE; Athens Night 1 should NOT skip)
- `--skip-step3` — **Athens production default per A1 decision 2026-05-01.** Cross-voice visibility moves to editor layer + Substack. Step 3 is dormant for Athens; re-add post-editor/microsite if budget permits.
- `--skip-continuity` — DEV USE for testing; Athens Nights 1+2 should NOT skip

PROJECT_ROOT resolves via `--project` > `AI_ASSEMBLY_PROJECT_ROOT` env > hard fail (per Tier 3 convention — no silent default).

### Cache busting for testing

Voice Pipeline uses checkpoint-as-cache (no `CACHE=1` flag — checkpoints ARE the cache). To force regeneration:

```bash
RUN="<run_dir>"

# Move (don't delete) Step 2 file aside to force Step 2 regen
mv "$RUN/04_voice/step2_first_draft_artifacts/<voice>.json" \
   "$RUN/04_voice/step2_first_draft_artifacts/<voice>.bak.json"

# Or whole 04_voice tree (preserves under suffixed name)
mv "$RUN/04_voice" "$RUN/04_voice_pre_<reason>"
```

**Workflow note:** for dryrun iteration, RENAME — don't delete. Preserves prior outputs for diffing. Established as standing practice 2026-04-29 after losing dryrun #1 to `rm -rf`.

### Run Researcher / Provocateur on test data

```bash
cd "/Users/aienvironment/Desktop/AI Assembly/code/runtime"
venv/bin/python flows/transcription_flow.py path/to/audio.mp4 path/to/session.json
venv/bin/python flows/researcher_flow.py path/to/session_package.json
venv/bin/python flows/provocateur_flow.py path/to/researcher_output.json
```

### Read a Step 2 or Step 3 artifact

```bash
cd "<run_dir>/04_voice/step2_first_draft_artifacts"
python3 -c "
import json
d = json.load(open('<voice>.json'))
print(f\"selected_form: {d.get('selected_form')}\")
print(f\"focus_decision: {d.get('focus_decision')}\")
print(f\"stance: {d.get('stance')}\")
print(f\"word_count: {d.get('word_count')}\")
print('---')
print(d.get('artifact_text'))
"
```

### Compare versions of the same artifact

When iterating on voice cards or prompts, snapshot before re-run:
```bash
cp "<run_dir>/04_voice/step2_first_draft_artifacts/<voice>.json" \
   "<run_dir>/04_voice/step2_first_draft_artifacts/<voice>.<reason>_PRE.json"
```

Then re-run; diff via `diff` or python script reading both files.

---

## Key architectural decisions ratified

### Convention A: one run_dir per night (2026-04-29)

See above + Voice Pipeline doc §"Multi-night convention". Rationale: each night's run_dir is self-contained, easy to archive, doesn't risk cross-night collision. Continuity reads ONE night's `04_voice/` at a time. Multi-night aggregation deliberately at the publish layer.

### Card-as-system-prompt at runtime (2026-04-29)

Voice Pipeline puts the persona card AS the system prompt rendered as structured headers (`IDENTITY` / `CONSTITUTION` / `BOUNDARIES` / etc.) + an XML-tagged closing instruction. NOT JSON blob in user prompt. Reasons:
1. **Anthropic prompt caching:** at 10 voices × 30 briefings/night, system prompt caches per voice; user prompt varies. ~5-10× cost difference at panel scale.
2. **Training emphasis:** Claude's persona-following weights system-prompt content more heavily than user-prompt JSON.
3. **Empirical:** the Plato 2026-04-26 chat test (paste chat_system_prompt as Claude project custom instructions) is what gave the validation that shipped Plato. Don't move what's working.

(Note: Persona Pipeline's Pass 7b smoke test does NOT match this pattern — that's filed as FU#54 post-Athens.)

### voice_temporal_stance.default — fluid framing (2026-04-29 revert)

Per the 9480d3a persona-prompt revert: `voice_temporal_stance.default` is the **fluid-across-time framing** (voice speaks from within its own world and lifetime; reader has come to consult voice). NOT cryofreeze. NOT "voice is in Athens 2026."

Voice Pipeline `_unwrap_voice_temporal_stance(deployment="athens")` enforces use of `default` for Athens runs (was incorrectly preferring `anchored_override` whenever populated; fixed in `voice-pipeline-v2.1-align-revert` branch).

`anchored_override` is for chat-test deployments (consumed by `personas/flows/shared/chat_prompt_builder.py`).

### Adaptive thinking — display: summarized + no temperature (FU#60)

All voice pipeline `_thinking_kwargs()` return:
```python
{"thinking": {"type": "adaptive", "display": "summarized"}}
```
No temperature key. Per Anthropic docs §"Feature compatibility": *"Thinking isn't compatible with temperature or top_k modifications."* + Opus 4.7 returns 400 BadRequestError on `temperature`.

`display: "summarized"` makes thinking traces visible (Opus 4.7 default is `omitted`). Trace captured in `thinking_trace` field of every step output.

researcher_flow.py + provocateur_flow.py have NOT yet been brought into this compliance — see OPEN_ITEMS C1, C2.

### Validation policy — Night 1 only (FU#62)

See OPEN_ITEMS A3 + Validation policy section above.

### Step 3 — SKIPPED for Athens (RESOLVED 2026-05-01 — Option A)

Athens runs ship Steps 1+2 only via `--skip-step3`. The original FU#49E correspondence-shape was dropped 2026-04-29; rather than redesign-then-ship in 6 days, A1 chose to skip Step 3 for Athens entirely and route cross-voice visibility through the editor layer (A2) + Substack walkthrough. Module + prompt + `_build_responded_to_graph` stay in codebase, dormant. Re-add path is ~2 days against B+ shape (engaged_peers metadata + optional postscript appended below body, body untouched). See OPEN_ITEMS A1 for full re-add steps.

**For Athens production runs, always pass `--skip-step3`** (along with `--skip-validation` on Nights 2/3 per FU#62 path B). The orchestrator no longer treats `--skip-step3` as DEV-USE-ONLY — it's the documented Athens production setting.

---

## Dryrun history (for context)

All in `<PROJECT_ROOT>/voice-pipeline-dryrun/runs/`:

| Run | Setup | Wall | Status |
|---|---|---|---|
| #1 | Plato solo, full validation | ~9.5 min | Lost (rm -rf before re-running). Workflow note: rename, don't delete |
| #2 | Plato solo, full validation | ~10.8 min | "By the Stoa of the Archon" — 683 words. Validator caught Plato's "panel today / our condition / first-person-presence-in-room" slips |
| #3 | Plato solo, no validation, post-tuning | ~3 min | "Lysander, or, On the Rule That Cannot Give Its Account" — 509 words (compliant). Thinking traces visible for first time |
| #4 | Plato + Cleopatra dual, Step 3 enabled | ~5:47 | First successful Step 3 cross-voice amendment. Both decided amend. Plato wrote a Socratic dialogue continuation; Cleopatra issued a prostagma back. Honest disagreement at framework level. **In FU#49E correspondence shape — that framing has since been dropped.** |
| FU#61 v1 (2026-04-30 11:09) | Cleopatra Step 2 only, --skip-validation | ~70 sec | Cold-reader hand-patch (criterion 6 v1). Mostly worked, over-corrected at salutation (lost Greek alphabet + Egyptian transliteration) |
| FU#61 v3 (2026-04-30 23:24) | Cleopatra Step 2 only, --skip-validation | ~80 sec | 5-criteria reshape (prompt-driven Pass 4b modification). **Best version** — Greek script preserved, inline glosses, plus issue-not-argue mode + honest mark-of-limit + direct queenly speaker acknowledgment |
| Legitimacy Test 1 (2026-05-01) | 4 voices × 3 nights × 1 formulation, --skip-step3 --skip-validation | ~11 min total | Verified continuity-after-Step-2 bugfix (`ccc6229`) end-to-end. Cross-night memory observed. All 12 artifacts in correct native register. |
| Legitimacy Test 2 (2026-05-01) | 4 voices × 1 night × 3 formulations, same flags | ~7 min | All 4 voices chose `focus_decision: "woven across all three"` — synthesis branch verified |
| Legitimacy Test 2 v2 (2026-05-01) | Same as Test 2 with distinct theme_display_titles | ~7 min | Still all wove. Diagnosis: synthesis bias goes deeper than title shape. Verified `thinking_tokens` fix (`8c47e1f`) live |

Backup files preserved at `<run_dir>/04_voice/step2_first_draft_artifacts/cleopatra.<version>.json` for diffing. Test 2 / 2 v2 artifacts at `legitimacy_test1_night{1,2,3}/`, `legitimacy_test2_single_night/`, `legitimacy_test2_v2_divergent_titles/`. Full report: `voice-pipeline-dryrun/legitimacy_test_report.md`.

---

## Glossary of runtime-specific terms

- **Run_dir** — per-night pipeline run directory; one per Athens night (Convention A)
- **PROJECT_ROOT** — per-project data root (outside code repo per Tier 3 separation)
- **Step 1 / Step 2 / Step 3** — Voice Pipeline three steps (private reasoning, first-draft artifact, amended artifact)
- **engaged_peers[]** — proposed Step 3 metadata structure (under redesign; see A1)
- **Field routing** — which card fields appear in which step's system prompt (matrix in Voice Pipeline doc)
- **Strip rules** — 5 load-bearing card-element drops at system prompt assembly time
- **Convention A** — one run_dir per night, with voice files unsuffixed inside
- **Card-as-system-prompt** — runtime contract: persona card content is the system prompt, not user-prompt JSON
- **Layer 1 / 2 / 3** — briefing's three-layer test (Encounter / Content / Expansion). Layer 1 = does audience engage; Layer 2 = could only this voice produce this; Layer 3 = did the conversation become more-than
- **Family-of-forms** — per Card v2.1 §H, voices may emit default form + 3-6 native variations within their corpus repertoire (Plato dialogue + Apology speech + Cave image; Cleopatra prostagma + ordinance + embassy speech). Step 2 picks per matter; Step 3 may reselect.
- **Postscript** (proposed Step 3) — voice-written addendum to artifact body, recording reading-of-peers without rewriting body
- **Editor / Frame layer** — pipeline pass between Step 2 and audience surfaces. **Per-theme** (not per-voice) per A2 decision 2026-05-01: produces a theme-level article framing one theme + the voices' positions on it. Voice artifacts ship as-is from Step 2, with their Provocateur formulation as micro-header. All-AI drafting (no operator polish). Output schema gated on microsite design. (NOT BUILT)

---

## DON'Ts (runtime-specific)

> **See also cross-cutting DON'Ts** in `_workspace/planning/ONBOARDING.md` §"Cross-cutting DON'Ts" — project-wide rules apply on top of these (no force push, no `--no-verify`, no real-person names in deployment-context JSONs, no commits with `--allow-empty`, no xattr/ACL mods, etc.).

- **Don't `rm -rf 04_voice/` to bust cache.** RENAME (`mv 04_voice 04_voice_pre_<reason>`). Preserves diffable history.
- **Don't run dryrun with default validation ON.** Step 1 outputs are cached → validation re-runs against unchanged outputs → same flags → ~8 min/voice burned. Always `--skip-validation` for dryrun work.
- **Don't run Athens Night 2/3 with validation ON.** Per FU#62: regen-on-flag is unimplemented, so flagged outputs ship to Step 2 regardless. Pure cost without remediation.
- **Don't bake conference-audience awareness into voice cards.** Voice doesn't know about audience (briefing principle). Voice's `quality_criteria` may include public-document-craft criteria (per FU#61), but framed in voice's own terms (queen as public-document-issuer; Plato as dialogue-for-the-colonnade-and-beyond).
- **Don't set `temperature` on Opus 4.7 calls with thinking enabled.** Returns 400. Per Anthropic docs §"Feature compatibility".
- **Don't load `smoke_test_chains` into voice system prompt.** Build-time diagnostic only; few-shotting from it collapses voice range.
- **Don't load `reference_only_passages` into Step 2 or Step 3 system prompt.** Copyright exposure (Marley lyrics, Dostoevsky modern translations). Step 1 keeps it for grounding.
- **Don't modify athens-2026 cards from runtime side.** Voice cards are persona thread's domain. Runtime READS cards; persona thread WRITES them. (Exception: testing patches under `pre_<reason>.json` backup pattern, with explicit operator awareness.)

---

## Quick reference — where things live

| Artifact | Path |
|---|---|
| Voice Pipeline orchestrator | `runtime/flows/voice_flow.py` |
| Voice Pipeline modules | `runtime/flows/voice/*.py` |
| Voice Pipeline prompts | `runtime/flows/shared/prompts/voice_*.md` |
| Council config (**runtime-owned** — Provocateur reads this) | `runtime/flows/shared/council/council_config.json` |
| Provocateur prompts | `runtime/flows/shared/prompts/provocateur_*.md` |
| Researcher prompts | `runtime/flows/shared/prompts/researcher_*.md` |
| Voice Pipeline spec | `docs/AI_Assembly_Voice_Pipeline.md` |
| Frame Concept | `docs/AI_Assembly_Frame_Concept_v1.md` |
| Gap analysis + architectural rationale (cross-cuts persona + runtime) | `docs/CURRENT_STATE.md` (§0 quick map, §1 what exists, §5 architectural decisions) |
| Briefing (project source of truth) | `docs/AI_Assembly_Briefing_v3_1.md` |
| Persona Card schema | `docs/AI_Assembly_Persona_Card_v2.md` |
| Provocateur spec | `docs/AI_Assembly_Provocateur_Pipeline.md` |
| Researcher spec | `docs/AI_Assembly_Researcher_Pipeline.md` |
| Transcription spec | `docs/AI_Assembly_Transcription_Pipeline.md` |
| Cross-repo handoff (persona ↔ runtime contract) | `personas/HANDOFF.md` |
| Runtime open items (this folder) | `_workspace/planning/runtime/OPEN_ITEMS.md` |
| Runtime onboarding (this doc) | `_workspace/planning/runtime/ONBOARDING.md` |
| Project-wide onboarding | `_workspace/planning/ONBOARDING.md` |
| Project-wide follow-ups (FU#1-62) | `_workspace/planning/FOLLOW_UPS.md` |
| Pipeline downstream architecture | `_workspace/planning/PIPELINE_DOWNSTREAM_DESIGN_2026_04_30.md` (untracked; commit) |

---

## How this doc stays current

- After major architectural shifts (Step 3 redesign lands; editor layer lands): update §"What's built" + §"Architecture in working memory" + add to §"Key architectural decisions ratified"
- After new dryruns: append to §"Dryrun history"
- After new branch state: update §"Active branch + recent history"
- After new DON'Ts emerge: append to §"DON'Ts (runtime-specific)"
- After new specs land: update §"Quick reference"

The dated `HANDOFF_<DATE>.md` files in the parent planning folder remain session-state snapshots. This doc is the durable runtime scaffolding.

---

*End of runtime ONBOARDING.md.*
