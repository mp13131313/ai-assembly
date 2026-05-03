# Voices — Handoff (session-end snapshot, 2026-05-03 — supersedes 2026-05-02 late-night)

**Companion:** `OPEN_ITEMS.md` (open-items list) + `ONBOARDING.md` (how-to / fresh-pickup). This doc is the session-end pickup snapshot: where we landed today, what's in flight, what's the next operator decision.

**On a fresh session:** read `ONBOARDING.md` first (~10 min), then this doc (~5 min), then `OPEN_ITEMS.md` (~10 min). Done in ~25 min.

---

## Branch + repo state at session end

| Repo | Branch | HEAD | Pushed |
|---|---|---|---|
| code | `main` | `98d7e04` | ✅ |
| athens-2026 | `main` | `c025914` | ✅ (unchanged this session) |

athens-2026 voices folder still carries **7 of 10** shipped cards: `plato`, `cleopatra`, `dostoevsky`, `ibn_battuta`, `octopus`, `hannah_arendt`, `ada_lovelace`. The 3 unshipped voices live in `projects/current-tests/voices/`: `bob_marley` (rebuild kicked off — see below), `whanganui_river` (Phase 0.5 staged from 2026-05-02), `scheherazade` (Phase 0.5 staged from 2026-05-02).

Plus a NEW 13th persona staged: **`claudia_pinchbeck`** (the editor) — architecture landed but no voice_config or pipeline run yet. Lives in `projects/current-tests/editor/claudia_pinchbeck/` (path TBD; not yet on disk — Editor Pipeline v1 layout puts her under `editor/` not `voices/`).

---

## Where the 10 panel voices + Claudia stand

| Voice | type / voice_mode | State |
|---|---|---|
| Plato | human / philosophical | ✅ shipped + 2026-05-02 patched (`cf283bf`); KNOWN open: Theuth/Thamus recurrence-tic — owned by runtime continuity overlay (Path B) |
| Cleopatra | human / observational | ✅ shipped at FU#61 v3 (`c89d186` + `54cd20a`) |
| Dostoevsky | human / narratival | ✅ shipped via path (b) + FU#61-fresh (`5088d67`); KNOWN: closing-on-suspended-judgment phrase tic — owned by runtime continuity overlay (Path B) |
| Battuta | human / narratival | ✅ shipped via path (b) (`e300508`); KNOWN: Tughluq beard-plucking stock-anecdote tic — owned by runtime continuity overlay (Path B) |
| Octopus | non_human / observational | ✅ compass rebuild SHIPPED + chat-test VERIFIED 2026-05-02 to athens-2026 (`04da2c8`). Runtime asset bundle at `code/docs/runtime_assets/octopus_chromatophore/`. |
| Hannah Arendt | human / philosophical | ✅ shipped 2026-05-02 to athens-2026 (`bfe917a`) |
| Ada Lovelace | human / philosophical | ✅ shipped 2026-05-02 to athens-2026 (`3a6fe2f` → rolled-back `c025914`) |
| **Bob Marley** | human / **observational** ✓ flipped this session | 🟠 **REBUILD KICKED OFF 2026-05-03**. Prior-state snapshot at `bob_marley_pre_song_rebuild_2026-05-03/` preserves the 35 verbatim-lyric passages (operator-supplied via lyrics archive parser) + the 6 prior DR sections + all generation/validation state. Fresh Pass 0a + new operator-authored voice_config (~1,950 chars total: manual_grounding + editorial_rationale encoding song-as-artifact mandate) + Phase 0.5 done (Pass 0b tailor explicitly registered the song-mandate as load-bearing config direction; injected 18 song-aware questions across 6 DR sections). DR prompts staged at `01_research/03_dr_prompts/`. Awaiting operator's 6 claude.ai DR sessions (~3hr wall). |
| Whanganui River | non_human / system / null | 🟡 Pass 0a done + voice_config rewritten transmission-faithful (Tupua te Kawa verbatim + Te Pou Tupua mediation + Indigenous-authored scholarship); Phase 0.5 done; DR prompts ready (from 2026-05-02) |
| Scheherazade | fictional / narratival | 🟡 Pass 0a done (auto-default voice_config; null editorial_rationale); Phase 0.5 done (after sustained Gemini 503 retry); DR prompts ready (from 2026-05-02). Mediated-voice prompt-fix concern carries through to her Pass 2 generation later |
| **Claudia Pinchbeck** *(editor; 13th persona)* | human / TBD (recommend `observational`) | 🟡 **NEW THIS SESSION.** Persona-construction architecture landed; documented in `voices/CLAUDIA_PINCHBECK_PERSONA_PREP_2026-05-03.md`. Hybrid pipeline path agreed (skip Phase 0.5 claude.ai DR; hand-curate 6 dossier sections from existing materials; run Pass 1.x → 2-6 → validation → Derive). Companion runtime memo at `_workspace/archive/MEMO_2026_05_03_editor_flow_input_output_contract.md (archived; v2 spec canonical at docs/AI_Assembly_Editor_Pipeline.md)`. Awaiting operator share of Beauty Shot dossier file + voice_mode/byline decisions to begin Stage A. ~7-9 hr Stages A-F when work resumes. |

---

## Bob Marley song-rebuild — kicked off 2026-05-03

**Trigger:** Marley pipeline pre-this-session was at Pass 3 with the artifact-form drifting toward prose-reasoning rather than song. Operator's manual Pass 4b patch caught the drift but post-mortem analysis showed the root cause was the original voice_config's null `editorial_rationale` + minimal `manual_grounding` — no operator-architectural direction flowing through Pass 0b tailor → DR prompts → downstream. Without strong direction, Pass 4b defaulted to text-shape medium for any human/narratival voice.

**Approach:** full rebuild from scratch following the Octopus compass-rebuild pattern (OPEN_ITEMS §15) + Whanganui transmission-faithful pattern (OPEN_ITEMS §17). Snapshot prior state, hand-author rich `manual_grounding` + `editorial_rationale` encoding the song-as-artifact mandate, run Pass 0a fresh, run Phase 0.5, hand off to operator for fresh DR sessions, run pipeline + re-inject the 35 lyrics at Pass 1c gate.

**Voice_config decisions landed this session:**
- `voice_mode`: **observational** (operator-confirmed; reversed from prior run's `narratival`). Pass 0a's reasoning held: Marley's songs are "instruments of witness, exhortation, and reasoning-from-suffering rather than as tales whose form is the engagement." Empirically: 3 of 5 material Pass-2-through-Pass-7b voice_mode-conditional branches favor observational for Marley-as-song. Most concrete: FU#40's narratival-only digression-permission would actively work against the song-form (lyrics compress, not digress).
- `corpus_constraint`: lyrics_patterns_only (unchanged)
- `manual_grounding`: ~1,600 chars. Encodes: load-bearing song-as-artifact direction (lyric + kind-hint two-shape contract; Suno-mediated kind-hint translation since Suno prompts are a different production language); genre framing (default roots reggae one-drop, recognizable catalogue range from Babylon System through Three Little Birds; not avant-garde dub / pop-crossover / ska); twin-failure-modes (pastiche-Marley + prose-Marley, with prose-Marley explicitly cited as the failure that triggered the rebuild). Bio + Rastafari context + scholarly pointers explicitly LEFT to the pipeline (research-discoverable, not operator-architectural).
- `editorial_rationale`: ~350 chars. Brief — Marley is the panel's only musical voice; song-as-artifact is the architectural direction; everything else the pipeline produces with Arendt-grade fidelity.

**Phase 0.5 outcome:** Pass 0b tailor's audit notes explicitly registered the editorial direction. Quote from `tailoring_notes.json`:

> *"Editorial rationale: substantive — emitted thematic_note emphasizing the song-as-artifact architecture and the dual speaking/singing voice research demand, which is the load-bearing config direction."*

18 song-aware questions injected across 6 DR sections, including (§4 VOICE) "the under-documented speaking-voice (interview) corpus distinct from singing voice" and (§6 PRIMARY TEXTS) "interview/speech corpus mapping (critical given musical-voice-with-lyrics-constraint config)." SWAP TEST anchor: Peter Tosh / Burning Spear / Marcus Garvey — correct confusability neighbours.

**Next session pickup for Marley:**
1. Operator runs 6 DR sessions on claude.ai with Opus 4.7 + Extended Thinking + Deep Research, ~30 min per section, save as `01_research/04_dr_dossier/0N_section_N.md`
2. Run `run_persona_pipeline.py "Bob Marley" --project current-tests`
3. At Pass 1c REVIEW GATE: re-inject 35 verbatim lyrics from `bob_marley_pre_song_rebuild_2026-05-03/02_merge/pass_1_6/reference_only_passages.json` into the fresh `02_merge/pass_1_6/reference_only_passages.json`, then `touch 03_primary_texts_reviewed.flag`
4. Pipeline runs through to Pass 7a FINAL gate
5. §7 convention applies: round 1 patches + round 2 patches + path-(b) ship via `_operator_review_passed.flag`. Surface verdict + ask operator before each round (Ada over-patching post-mortem).
6. Promote to athens-2026 + wire 8th `council_config.json` member when verified

---

## Claudia Pinchbeck persona-construction architecture — landed 2026-05-03

**Comprehensive prep document:** `voices/CLAUDIA_PINCHBECK_PERSONA_PREP_2026-05-03.md`

**Companion runtime memo:** `_workspace/archive/MEMO_2026_05_03_editor_flow_input_output_contract.md (archived; v2 spec canonical at docs/AI_Assembly_Editor_Pipeline.md)`

**Architecture summary:**
- Claudia is the **13th member** of the Assembly — the editor of *The Assembly*'s news organ. Functionally distinct from panel voices (she edits; they contribute). Her medium is the dossier (compound publication structure), not a single artifact.
- The voice triangulates four reference traditions: **Talk of the Town** (sentence texture; uncredited institutional voice); **TLS until 1974** (anonymous reviews; intellectual material at full weight without performing erudition); **Borges** (constructed reportage in serious form, reader trusted); **Manchester Guardian "London Letter"** (institutional voice, byline convention).
- Critical architectural split: the desk's **prose register** is mid-century broadsheet; the desk's **editorial attention** is what the publication itself (HoBB / Beauty Shot voice) would consider news. Different things. Both load-bearing.
- "One spine, ten bends" — the desk's prose has a single register that bends per voice when reporting on each (Plato in clipped dialogic; Arendt in surgical dryness; etc.). Per-voice torque lives in `translation_protocol`.
- "When the form does not fit" — for voices the form genuinely cannot carry (Whanganui, Octopus, Marley), the desk fails honestly in the form rather than performing fluency it does not have.
- Hybrid pipeline path: skip Phase 0.5's claude.ai DR sessions (Claudia is invented, no biography to research); hand-curate 6 DR dossier sections from existing materials (Beauty Shot dossier + Frame Concept v1 + Briefing v3 + Editor Pipeline v1 + reference-tradition source material + canonical reference articles); run Pass 1.1-1.7 → Pass 1c-1d → Pass 2-6 → validation → Derive against the curated dossier. Same density as panel voices.

**Pending operator inputs before Claudia work resumes:**
1. **Beauty Shot dossier file** (operator confirmed they have it; not shared as of session end). Critical for §2 INTELLECTUAL of the DR dossier and for `constitution`/`finds_compelling`/`resists`/`topics_requiring_care`.
2. `voice_mode` decision (recommend `observational` with notation — none of the v2 enum values fit cleanly)
3. Byline split decision: Option A (single house byline) or Option B (correspondent for articles, desk for headnotes). Recommend Option B per the prior conversation.

**Estimated wall when resumed:** ~7-9 hr Stages A-F (most operator-side; pipeline ~2-3 hr unattended).

---

## What landed today (2026-05-03 session)

1. **Voices session onboarding** — fresh-session pickup via `voices/ONBOARDING.md` + `voices/OPEN_ITEMS.md` + `voices/HANDOFF.md` + `MEMO_2026_05_01_recurrence_patterns_from_legitimacy_test.md`. Plus full re-read of canonical pipeline specs (Researcher / Provocateur / Voice / Editor / Frame / Briefing v3.1 / Persona Card v2 / Persona Pipeline v4 / Runtime Lifecycle / Infrastructure / LLM Call Inventory / Audience Brief / Transcription Pipeline / personas README + HANDOFF / runtime README).

2. **Marley pipeline state diagnosis** — disk-state inspection revealed pipeline was paused at Pass 5 with Pass 4b operator-patched (artifact-form rewritten from "reasoning in prose" to "Original reggae song"). Pre/post 4b diff revealed near-complete regeneration of all 8 Pass 4b fields, not surgical edit. Diagnosis: original voice_config's null editorial_rationale + minimal manual_grounding allowed Pass 4b to drift; rebuild needed.

3. **Marley song-rebuild kicked off** — see "Bob Marley song-rebuild" section above.

4. **Claudia Pinchbeck persona-construction architecture landed** — see "Claudia Pinchbeck" section above. Two new docs filed:
   - `voices/CLAUDIA_PINCHBECK_PERSONA_PREP_2026-05-03.md` (persona prep state, 462 lines)
   - `_workspace/archive/MEMO_2026_05_03_editor_flow_input_output_contract.md (archived; v2 spec canonical at docs/AI_Assembly_Editor_Pipeline.md)` (cross-thread memo, 345 lines)

5. **Commit + push** — `98d7e04` on `main`. Both docs diff-suppressed by `.gitattributes`'s `_workspace/** -diff` rule per project convention.

---

## What's in flight at session end

1. **Marley DR sessions** — operator-wall (~3hr if 6 sessions parallelized in browser tabs). Awaiting operator to run.
2. **Whanganui DR sessions** — same shape. From 2026-05-02.
3. **Scheherazade DR sessions** — same shape. From 2026-05-02.
4. **Claudia work** — architecturally staged; awaiting operator's Beauty Shot dossier share + voice_mode/byline decisions.

All three voices' DR can run in parallel browser tabs; Claudia's 7-9 hr work can run in the same wall window.

---

## Operator decisions pending

### Immediate / next session

1. **Marley DR sessions** — operator-run on claude.ai
2. **Whanganui + Scheherazade DR sessions** — same
3. **Mediated-voice prompt-fix decision before Scheherazade's Pass 2 fires** — drafted but never landed since 2026-04-28; same dramatist-vs-speaker collision risk Plato had
4. **Claudia: Beauty Shot dossier share + voice_mode + byline split decisions**
5. **Marley pipeline gate (when it hits)** — apply §7 convention; ask before each patch round
6. **Marley promote to athens-2026** + council_config wiring of 8th member (replaces placeholder entry)

### Carry-forwards from earlier sessions

7. Plato thinking-on re-run experiment ($5, 30 min). See OPEN_ITEMS.md §5
8. 9480d3a revert hypothesis re-evaluation — connected to FU#56. See OPEN_ITEMS.md §5
9. WBBF program copy coordination (FU#49C remnant)
10. FU#49G Greek-scholar calibration on Plato — Quarch/Tsinorema/Erinakis on the provotype-test

### "Voice of X" naming convention sweep — deferred until all 10 voices ship

See OPEN_ITEMS §18. Single mechanical sweep of voice_name + council_config + panel_roster after Marley + Whanganui + Scheherazade ship; backfill via SKIP_TO_DERIVE re-fire (~15 min + ~$20 for 10 voices). Claudia's "voice_name" (or "council_member_name") field follows the same convention or operator-decision relabeling.

---

## What I would do next session in priority order

1. **Check Marley DR session status** — has operator run them? If yes, pipeline-fire. If no, surface the wall-time priority (T-4 to Athens).
2. **Run Marley pipeline post-DR** — `run_persona_pipeline.py` from cache; halt at Pass 1c review gate; re-inject 35 lyrics from snapshot; touch flag; resume; §7 convention at Pass 7a FINAL.
3. **Promote Marley to athens-2026** + wire 8th council_config member when verified.
4. **If Whanganui + Scheherazade DRs done in parallel** — fire those pipelines too.
5. **Claudia Stages A-F** — once operator shares Beauty Shot dossier + decisions land. Stage A first (voice_config), operator review, Stage B (DR dossier sections), operator review, Stage C (pipeline run), operator gate.
6. **All-10 sweep** — "Voice of X" naming convention rollout (§18) after Marley/Whanganui/Scheherazade ship + Claudia ships. Single mechanical pass.

---

## Reading order for next session

1. `voices/ONBOARDING.md` (steady-state how-to + Pass 0a interrogation discipline + 3-posture taxonomy)
2. `voices/HANDOFF.md` — this doc
3. `voices/OPEN_ITEMS.md` (status snapshot — especially §1 per-voice state for Marley rebuild status)
4. **For Marley pipeline resumption:** the snapshot + injection mechanics are documented in this doc's "Bob Marley song-rebuild" section; no separate pickup doc needed
5. **For Claudia work resumption:** `voices/CLAUDIA_PINCHBECK_PERSONA_PREP_2026-05-03.md` is the comprehensive pickup doc; pair with `_workspace/archive/MEMO_2026_05_03_editor_flow_input_output_contract.md (archived; v2 spec canonical at docs/AI_Assembly_Editor_Pipeline.md)` for the runtime-contract context
6. `voices/MEMO_2026_05_01_recurrence_patterns_from_legitimacy_test.md` — runtime-thread findings doc (historical)

That's ~30 min to working knowledge for picking up voice-build work cold.

---

## When this doc goes stale

Update `HANDOFF.md` at the end of every voice-build session — it's the session-snapshot, not the steady-state. Roll the prior session's HANDOFF into the next session's by dating the doc and adding a "supersedes prior HANDOFF" note at top.

If you want a versioned history, save prior HANDOFFs as `HANDOFF_<DATE>.md` in `_workspace/archive/voices_consolidation_<date>/`.
