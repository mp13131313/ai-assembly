# HANDOFF — Voice Pipeline dual-voice dry-run + late-evening alignment

**Date:** 2026-04-29 late evening (~23:30)
**Branch:** `voice-pipeline-v2.1-align-revert` (pushed; 11 commits ahead of `main`)
**Companion to:** `HANDOFF_2026_04_29_LATE.md` (operator's persona-side late-evening pickup) — this doc covers the voice-pipeline-runtime side of the same session.
**Supersedes:** `HANDOFF_DRYRUN_2026_04_29.md` (the original first-dry-run handoff — the four dry-runs landed in this session)

---

## URGENT — for tomorrow's session: Step 3 redesign

**Operator decision late-evening 2026-04-29:** Step 3 to be **redesigned from scratch** tomorrow, working directly from `docs/AI_Assembly_Briefing_v3_1.md` as canonical source. **FU#49E framing (and the broader reviewer-pass family that informed it) is dropped** — not the design intent to follow.

**What this means concretely:**
- The Step 3 implementation that landed across this session's commits (`voice_step3_amendment.md` prompt + `step3_amended_artifact.py` parser/output schema + the FU#49E-quoted "extend / mark-limit / sharpen" framing) is **provisional, not target-shape**
- Dry-run #4's amended artifacts (Plato's Socratic dialogue addressed to Cleopatra, Cleopatra's prostagma addressed to Plato) **demonstrate Step 3 mechanics work end-to-end** but are **NOT what tomorrow's design will produce** — those artifacts are in correspondence shape; tomorrow's design works from the briefing's "amendments reference the other voice / published set is responsive to itself / collective character constituted at Step 3" formulations directly, without the FU#49E reviewer's intervening framing
- Step 1 + Step 2 + the broader pipeline scaffolding are **validated and stay** — only Step 3's design (prompt, output schema, possibly responded_to_graph derivation, possibly the validation framing) is being redone

**Briefing pointers for tomorrow:**
- Line 91: *"Constitute the collective at specific moments, not continuously. The Assembly's collective character is constituted at Step 3..."*
- Line 167: *"...the overlaps creating the deliberation structure for Step 3"*
- Line 177: *"Each voice reads the artifacts of the other voices it shares at least one theme with... amendments are visible — they reference the other voice so the amendment reads as responsive."*
- Line 179: *"This is where the Assembly's collective character is constituted overnight... The published set is responsive to itself."*
- Line 181: *"Steps 1 and 2: AI_Assembly_Voice_Pipeline.md. Step 3 requires specification before Athens."*
- Line 238: *"The mapped read-through does specific work against the Chwalisz/Alexander critique..."*
- Line 262: *"Step 3 amendments may show more inter-voice dialogue."*
- Line 292: *"Step 3 specification. System prompt template, input format, output format, timing, integration with Voice Pipeline."*

The current Step 3 prompt + artifact schema can be inspected as a "what has been tried" reference, but the design moves from the briefing fresh.

---

## TL;DR (for the rest of the session's work)

In one extended session (~7 hours), the Voice Pipeline went from "v2 spec landed but never run end-to-end" to "**Step 1 + Step 2 mechanics validated against real Plato and Cleopatra cards across four dry-runs; Step 3 mechanics also exercised but in a shape now flagged for redesign**." The branch carries:

- v2.1 alignment with the 9480d3a persona-prompt revert (cryofreeze removal, validator card-driven, family-of-forms neutralized, `_unwrap_voice_temporal_stance` Athens-default fix)
- Post-dryrun tuning (validator (c) soften, extraction-ID bookkeeping, `load_dotenv override=True`)
- Title/subtitle dropped from voice (downstream concern), `themes_covered` derived deterministically, Convention A documented
- Temperature compliance (`thinking` is incompatible with temperature modifications per Anthropic docs), `display: "summarized"` adopted (matches operator's FU#60 on persona side)
- `responded_to_graph` derivation refactored to populate from `voices_read + decision` rather than only from structured `amendments[]` (post-dryrun #4 finding: voices respond holistically in prose, not by enumerating per-passage amendments)

**Athens execution is unblocked** for the voice-pipeline runtime side. Outstanding items below are quality / cross-pipeline polish, not blockers.

---

## Five voice-pipeline commits this session (all on `voice-pipeline-v2.1-align-revert`)

| Commit | Description |
|---|---|
| `fb33bb9` | v2.1 alignment with 9480d3a persona-prompt revert (cryofreeze removal, validator card-driven, `_unwrap_voice_temporal_stance` Athens-default fix) |
| `30a38eb` | v2.1 follow-up — FU#57 spec sync + continuity-prompt logical fix + README cosmetic |
| `f68bc3f` | post-dryrun tuning — validator (c) soften, extraction-ID bookkeeping (option C hybrid), `load_dotenv override=True` |
| `f6ee392` | drop title/subtitle from voice + derive `themes_covered` deterministically + Convention A doc |
| `0381278` | drop `temperature: 1.0` (Anthropic docs §"Feature compatibility" enforces incompatibility), add `display: "summarized"` (matches persona-pipeline FU#60) |
| `e89dfc4` | derive `responded_to_graph` edges from `voices_read + decision` (post-dryrun #4 finding) |

Plus operator's persona-side commits on the same branch: `49b3a28` (FU#58), `fc48c27` (FU#59), `dd64782` + `85f04da` (FU#60), `0093a43` (operator's late-evening handoff), `2fda654`, `0ec9755`, `08279d0` (planning + spec refreshes).

**Branch state:** 11 commits ahead of main. Both threads cohabited the branch cleanly with zero conflicts. Eventual merge to main pending operator decision.

---

## Four dry-runs, all in `<PROJECT_ROOT>/voice-pipeline-dryrun/`

| Run | Setup | Wall | Status / Notes |
|---|---|---|---|
| **#1** | Plato solo, full validation | ~9.5 min | **Lost** — I `rm -rf 04_voice` before re-running. Workflow note: rename, don't delete |
| **#2** | Plato solo, full validation | ~10.8 min | "By the Stoa of the Archon" — 683 words (over Plato's 350-550 cap). Validation correctly flagged Plato's "panel today" / "our condition" / first-person-presence-in-room slips |
| **#3** | Plato solo, no validation, post-tuning | ~3 min | "Lysander, or, On the Rule That Cannot Give Its Account" — 509 words (compliant). Thinking traces visible for first time (display=summarized) — sample: *"I'm framing this as a Socratic dialogue where I respond as Plato to a question about algorithmic governance, drawing on several key concepts from his works..."* |
| **#4** | **Plato + Cleopatra dual, Step 3 enabled** | ~5:47 | **First successful Step 3 cross-voice amendment.** Both decided `amend`; both produced cross-engaged artifacts. Plato wrote a Socratic dialogue continuation where a Greek of Alexandria delivers Cleopatra's letter; Cleopatra issued a prostagma back ("Βασίλισσα Κλεοπάτρα... to Plato son of Ariston, who in the colonnade today divided rightly: greeting") refusing his remedy. **Honest disagreement at framework level**, no smoothing |

### Run #4 artifact summary

**Plato's amended artifact** (run_dir `dryrun_2026_04_29_plato_cleopatra/04_voice/step3_amended_artifacts/plato.json`):

> *"In the colonnade, later. A Greek of Alexandria has come up with a sealed letter, copied from the queen's chancery, and asks me to read it and answer."*
>
> Closes: *"She has the answering body without the seeing soul; we have the unseeing tablet without the body. Neither is the physician. Tell her, when you carry the letter back, that we agree about what is missing in Athens. And tell her I should like to know — in Alexandria, who examines the seal before it falls?"*

**Cleopatra's amended artifact**:

> *"Βασίλισσα Κλεοπάτρα Θεὰ Φιλοπάτωρ Φιλόπατρις Νέα Ἶσις, Lady of the Two Lands — Ḳliwpꜣdrꜣ nb.t-tꜣwy — to Plato son of Ariston, who in the colonnade today divided rightly: greeting."*
>
> Sharpens disagreement: *"a colonnade that refuses the seal in order to keep the question open has not produced justice either; it has produced the suspension of justice in the name of justice, and the cousin pays the difference."*
>
> Closes with `γινέσθωι.`

**`responded_to_graph_night_1.json`** (post-`e89dfc4` derivation logic):
- 2 nodes: `["cleopatra", "plato"]`
- 2 edges: `cleopatra→plato` and `plato→cleopatra`, each with `amendment_type: "engaged"` + a substantive `decision_rationale_excerpt` (≤240 chars)

### Things that worked end-to-end across the 4 runs

| Mechanism | Validated by |
|---|---|
| Persona card → system prompt assembly (Plato + Cleopatra) | All 4 runs (system prompts assemble at 80K-120K chars) |
| Step 1 private reasoning (6 calls × Opus 4.7 + adaptive thinking) | All 4 runs |
| Step 1 validation ladder (gpt-5.4 → fallbacks) | Runs #1, #2 |
| Step 2 form decision tolerant of single-form `medium` (Plato dialogue, Cleopatra prostagma) | All 4 runs |
| Step 3 cross-voice amendment + form retention | Run #4 (first time) |
| `responded_to_graph` populating with edges + decision_rationale_excerpts | Post-`e89dfc4` (rewritten on disk for run #4) |
| `themes_to_voices_night_1.json` reverse index (per-theme → which voices at each step) | Run #4 (first multi-voice) |
| Publish layer writes to `<PROJECT_ROOT>/published_artifacts/nights/night_1/` | All runs (when not skipped) |
| Convention A: per-night run_dir, voice files unsuffixed (`plato.json` not `plato_night_1.json`) | All runs |
| `voice_temporal_stance.default` fluid framing (post-revert), Athens-mode unwrap | All runs |
| `display: "summarized"` makes thinking visible | Run #3, run #4 |

### Things still NOT exercised end-to-end

| Mechanism | Why not |
|---|---|
| **Continuity flow** (Sonnet summariser writes `continuity_night_<N+1>.json` from prior night's outputs) | All 4 runs were Night 1 standalone (`--skip-continuity`); needs Night 1 → Night 2 sequence |
| **Multi-night sequence** (run_dir per night, continuity carries across, publish_flow aggregates per voice across nights) | Same |
| **`publish_flow.py`** (per-theme + per-extraction reverse-index + lineage graph from real Researcher/Provocateur outputs) | All dry-runs used hand-authored briefings, not real Provocateur output. publish_flow has nothing to read on the upstream side in the sandbox |
| **3+ voice cross-engagement** | Only 2 voices in run #4 |
| **Validator regeneration loop** (1 retry, then ship and flag) | No flagged-cards-actually-failed-OpenAI-ladder cases observed |
| **Graceful degradation** (Step 1 partial failures shouldn't stall pipeline) | No transient failures encountered to test |

---

## Where things are

```
<PROJECT_ROOT>/voice-pipeline-dryrun/
├── voices/
│   ├── plato/                                                   v2 card finalized; persisted from athens-2026
│   └── cleopatra/                                               v2 card finalized 2026-04-29 21:55; persisted from athens-2026
├── runs/
│   ├── dryrun_2026_04_29_plato_solo/                            runs #2, #3 outputs (run #2 renamed to _PRE_TEMP_REMOVAL)
│   │   ├── 03_provocateur/briefings/plato.json
│   │   ├── 04_voice/                                            run #3 (current — post `display: summarized`)
│   │   └── 04_voice_run2_PRE_TEMP_REMOVAL/                      run #2 (preserved for diffing)
│   └── dryrun_2026_04_29_plato_cleopatra/                       run #4 (dual voice, Step 3)
│       ├── 03_provocateur/briefings/{plato,cleopatra}.json      hand-authored; co_assigned_voices cross-listed
│       └── 04_voice/                                            full step1+step2+step3 + responded_to_graph + manifest
└── published_artifacts/nights/night_1/{plato,cleopatra}.json + _index.json
```

Real cards (athens-2026), unmodified through any dry-run:

```
<PROJECT_ROOT>/athens-2026/voices/{plato,cleopatra}/07_persona_card_assembled.json
```

---

## Validation flag findings (from runs #2 + #4)

The card-driven anachronism validator caught real signal:

1. **Plato's first-person-presence drift** — *"the panel today"*, *"our condition"*, *"this room has not yet asked"*, *"the panel keeps walking past"*. Voice claims to inhabit the reader's setting in first person. The fluid `voice_temporal_stance` forbids this (the reader has come to consult Plato; Plato has not gone forward to Athens 2026).
2. **Plato's `translation_protocol` underuse** — *"algorithm"*, *"smartphone"*, *"mortgage"*, *"engagement-platforms"*, *"index case"* left raw in Step 1 prose. (Operator: keep — voice-side artifact issue, not pipeline contract.)
3. **Cleopatra (run #4) flagged 0 issues** in Step 1 — her prostagma + chancery framing translated all modern terms cleanly (e.g. "credit scoring" → "the seal that decides").

The validator post-fix is doing its job. **Important caveat:** validation ran against the dry-run voices in runs #1, #2 only. Runs #3 and #4 used `--skip-validation` for speed/cost.

---

## Outstanding / next session pickup

See `OPEN_ITEMS_VOICE_PIPELINE_2026_04_29.md` for full list. Highlights:

### Athens-blocking-eligible (pre-May-7)

1. **Multi-night sequence dry-run** — exercise continuity flow + Convention A end-to-end. Plato + Cleopatra Night 1 → Night 2 sequence. Run-dirs: `runs/athens_2026_..._night1`, `..._night2`. Continuity flow runs after Night 1 Step 3 completes; Night 2's voice system prompts load from `voices/<slug>/continuity_night_2.json`.
2. **`publish_flow.py` end-to-end exercise** — needs real Researcher/Provocateur outputs upstream. Either re-run dev_msc_test through researcher_flow + provocateur_flow + voice_flow OR hand-author fixtures matching the briefing schema.
3. **Cross-pipeline compliance sweep** — `runtime/flows/researcher_flow.py` still has `temperature: 1.0`; `runtime/flows/provocateur_flow.py` lacks `display: "summarized"`. Same fix-pattern as `0381278`. ~3 lines per file.
4. **Voice 3 onwards** — operator-side persona-pipeline buildout (8 voices remaining). Voice pipeline ready to consume them as soon as `07_persona_card_assembled.json` ships.

### Cleanup / nice-to-have

- `LLM_CALL_INVENTORY.md` refresh (post-FU#52/53/57/58/59/60 + voice pipeline rows + thinking-audit columns)
- Naming inconsistency: `council_member_name` (card) → `council_member` (voice output) → `voice_name` (publish output)
- Title source pipeline (where titles come from for the micro-site — voice doesn't produce them)
- Voice-side artifact tuning if dry-runs reveal recurring issues (translation underuse, monologic slip patterns)

---

## Pickup notes

For a fresh session next time:

1. Read this doc + `HANDOFF_2026_04_29_LATE.md` (operator's late-evening handoff covering persona side)
2. `OPEN_ITEMS_VOICE_PIPELINE_2026_04_29.md` for the prioritized backlog
3. `BRIEF_OPUS_4_7_THINKING_AUDIT_2026_04_29.md` is now superseded — FU#60 resolved the audit (see operator's late-evening handoff)
4. Branch is `voice-pipeline-v2.1-align-revert`, pushed. Last voice-pipeline commit: `e89dfc4` (graph derivation fix)
5. Code in solid state. Specs current. Sandbox preserved with all 4 runs' outputs for forensic comparison.

The voice pipeline is **runnable for Athens** as of this commit. The remaining work is multi-night exercise, sibling-pipeline compliance, and downstream-of-voice questions (titling, micro-site).

---

*End of voice-pipeline dual-dryrun handoff. 2026-04-29 23:30.*
