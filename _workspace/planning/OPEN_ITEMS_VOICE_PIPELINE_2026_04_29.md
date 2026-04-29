# OPEN ITEMS — Voice Pipeline + adjacent

**Date:** 2026-04-29
**Branch state:** `voice-pipeline-v2.1-align-revert` carries v2.1 alignment + post-dryrun tuning + title-subtitle-drop + themes_covered derivation + Convention A doc. Validated end-to-end against Plato dry-run #2 (high-quality "By the Stoa of the Archon" Socratic dialogue).
**Convention going forward:** **one run_dir per night** for Athens (see `docs/AI_Assembly_Voice_Pipeline.md` §"Multi-night convention").

---

## Decisions resolved + cross-pipeline status

### Thinking config — RESOLVED 2026-04-29

**The 0 thinking tokens we observed was an instrumentation gap**, not a behavioral problem. Investigation summary:

- **Anthropic SDK 0.94.1** has no `thinking_tokens` field on `Usage` — thinking is rolled into `output_tokens`
- **Opus 4.7** defaults `thinking.display` to `"omitted"` — thinking blocks return with empty `thinking` text (we're still billed)
- **Estimated thinking from voice dry-run #2**: ~1800-2400 hidden tokens per Step 1 call, computed as `output_tokens − visible_response_tokens`. Thinking IS happening
- **Anthropic docs §"Feature compatibility"**: *"Thinking isn't compatible with `temperature` or `top_k` modifications."* Voice Pipeline (and researcher_flow) had been setting `temperature: 1.0` explicitly — copied from pre-Opus-4.7 manual-thinking docstring that said "extended thinking requires temperature=1.0" (true for manual mode, **not** true for adaptive mode)
- **Persona pipeline noted empirically**: *"Opus 4.7 (and newer models) deprecated the `temperature` parameter. Passing it yields a 400 BadRequestError"* (`personas/flows/shared/clients.py`)
- **Persona pipeline FU#60 (2026-04-29)** added `thinking.display: "summarized"` to make traces visible

**Voice Pipeline matched the persona pattern in this branch:**
- All 4 `_thinking_kwargs()` (step1, step2, step3, continuity) now return `{"thinking": {"type": "adaptive", "display": "summarized"}}` — no temperature key
- Compliant with Anthropic docs feature-compatibility section
- Thinking traces now visible (was empty by 4.7 default)

### Cross-pipeline status (post this session)

| Pipeline | Temperature with thinking | display: "summarized" | Status |
|---|---|---|---|
| Voice (this branch) | ✅ removed | ✅ added | Compliant |
| Personas (`clients.py`) | ✅ already removed (FU prior) | ✅ added (FU#60) | Compliant |
| Provocateur (`provocateur_flow.py`) | ✅ never set | ❌ not set | Partial — needs `display` |
| Researcher (`researcher_flow.py`) | ❌ still sets `temperature: 1.0` | ❌ not set | **NON-compliant — needs both fixes** |

**Outstanding cross-pipeline work** (filed as follow-ups, not for this branch):
1. `runtime/flows/researcher_flow.py` `_thinking_kwargs` — drop `temperature: 1.0`, add `display: "summarized"`
2. `runtime/flows/provocateur_flow.py` `_thinking_kwargs` — add `display: "summarized"`
3. (Optional, if cost+latency warrant) Add `output_config: {effort: <level>}` per-call across all pipelines for explicit thinking-depth control. Currently default `high` effort, which docs say "Claude almost always thinks" — likely fine without explicit control

---

## Follow-ups (not for the v2.1 align branch)

### High priority — Athens-blocking-eligible

- **Multi-voice + multi-night dry-runs** — Step 3 + Continuity have **never been exercised end-to-end**. Need:
  - Plato + Cleopatra (once Cleopatra is finalized) for Step 3 amendment cross-voice traffic
  - Night 1 → Night 2 sequence for continuity override consumption
  - Without these, Step 3 + Continuity flows are smoke-tested only
- **`publish_flow.py` exercise** — `runtime/flows/publish_flow.py` (per-theme + per-extraction reverse index + lineage graph) has never run end-to-end against real Researcher/Provocateur outputs. Either re-run those on `dev_msc_test` or hand-author fixtures
- **`researcher_flow.py` + `provocateur_flow.py` `load_dotenv override=True`** — same shell-empty-env bug Voice Pipeline hit (commit `f68bc3f`); not landed for runtime sibling pipelines yet. May only matter when run from the same Claude Code agent shell environment; operator's normal terminal may not exhibit
- **3-night execution dry-run** — exercise the documented Convention A end-to-end (3 separate run_dirs, continuity carries across, publish_flow aggregates). Discovery test for any latent assumption that breaks under multi-night

### Medium priority — quality / hygiene

- **Title / subtitle source pipeline** — Voice Pipeline no longer asks the voice for title/subtitle (this branch). Where DO they come from for the micro-site?
  - **Options:** human editorial (operator authors per artifact), auto-titler step (small Sonnet call reads artifact_text → emits title + subtitle), micro-site templating (CMS-side), or just left empty and the artifact opens with its own scene-setting
  - **Recommendation:** scope a small `runtime/flows/edition/` or `runtime/flows/curation/` step before Athens; or accept the empty-title path through Athens and add titling post-hoc
- **Voice-side artifact tuning** from real validation findings on dry-run #2:
  - Plato underused `translation_protocol` in Step 1 (modern terms left raw — operator: keep as-is, voice-side artifact)
  - "our condition" / first-person-presence-in-room slips in theme_001 Step 1 prose (validator correctly caught these)
  - Theme_002 constitution slip (Plato gave thymos logos's job; shifted to monologic assertion vs elenchus)
  - **None blocking.** Could sharpen via Plato card patches OR via Step 1 closing-instruction guards. Operator-side judgment call
- **Naming inconsistency: `council_member_name` (card) → `council_member` (voice output) → `voice_name` (publish output)** — three names for the same field. Could harmonize in a single rename pass. Low priority

### Low priority — documentation

- **`docs/LLM_CALL_INVENTORY.md`** stale (last updated 2026-04-27). Needs:
  - FU#52 / FU#53 / FU#57 updates
  - Voice Pipeline rows added (currently missing — was "NOT YET BUILT" when inventory was written)
  - Once thinking-audit lands: `effort` + `display` columns + observed `thinking_tokens` per pass
- **Workflow note for Claude (me) on dry-run iteration** — instead of `rm -rf 04_voice` to bust checkpoints, **rename** the prior dir (e.g. `mv 04_voice 04_voice_run1_PRE_<commit>`). Preserves prior outputs for diffing. (Self-discipline, not a code change.)

### Out-of-scope / future architecture

- **Closing-show pipeline** — implied by `themes_to_voices_night_N.json` design (reverse-index intended for closing-show consumption) but not specced or built. Post-Athens
- **Editorial / curation step between Step 3 and publish** — title/subtitle generation, possibly artifact ordering for micro-site presentation. Scope unknown; mentioned as a downstream concern
- **Multi-voice fork-test for FU#55** (Cleopatra-driven family-of-forms re-evaluation) — operator-side persona-pipeline work; mentioned here only because if family-of-forms re-lands prompt-side, Voice Pipeline `medium` field handling stays unchanged (it's already tolerant of single-form OR multi-form per the v2.1 alignment)

---

## What's solid (this branch validated)

- v2.1 alignment with 9480d3a persona-prompt revert (commits `fb33bb9` + `30a38eb`)
- Post-dryrun tuning: validator (c) soften, extraction-ID bookkeeping (option C — speaker-name in prose + structured tail), `load_dotenv override=True` (commit `f68bc3f`)
- Title/subtitle dropped from voice prompts; downstream concern (this commit)
- `themes_covered` derived deterministically from `focus_decision` + briefing themes (this commit) — voice's surface stays clean
- Multi-night convention documented (Convention A: one run_dir per night) (this commit)

Two dry-runs ran successfully end-to-end. Plato produced two genuine Socratic dialogues, both passing his `quality_criteria` cleanly. Validator now embeds the card's actual `voice_temporal_stance` and correctly catches genuine inhabitation drift while letting through "the question put to me today" reception. Extraction-ID prose leakage fixed (zero leaks in run #2; 5/5 IDs cleanly captured per theme).

---

## Pointers

**Specs / docs:**
- `docs/AI_Assembly_Voice_Pipeline.md` — v2.1 spec, current
- `docs/AI_Assembly_Persona_Card_v2.md` — 36-field schema, current
- `docs/LLM_CALL_INVENTORY.md` — stale (see medium-priority above)

**Briefs:**
- `_workspace/planning/BRIEF_OPUS_4_7_THINKING_AUDIT_2026_04_29.md` — for persona-pipeline session pickup
- `_workspace/planning/HANDOFF_DRYRUN_2026_04_29.md` — original dry-run handoff (now superseded by completed dry-runs #1 + #2)

**Code:**
- `runtime/flows/voice_flow.py` — orchestrator, CLI entry
- `runtime/flows/voice/` — Step 1/2/3 + validation + continuity + publish
- `runtime/flows/shared/prompts/voice_*.md` — closing instructions (6 files)

**Sandboxes:**
- `<PROJECT_ROOT>/voice-pipeline-dryrun/` — Plato solo, 3 hand-authored formulations on "The Legitimacy of the Invisible". Run #2 outputs preserved at `04_voice/` post-tuning.
