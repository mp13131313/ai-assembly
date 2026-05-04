# Voices — Handoff (session-end snapshot, 2026-05-04 PM — supersedes 2026-05-04 early-AM)

**Companion:** `OPEN_ITEMS.md` (open-items list) + `ONBOARDING.md` (how-to / fresh-pickup). This doc is the session-end pickup snapshot: where we landed today, what's in flight, what's the next operator decision.

**On a fresh session:** read `ONBOARDING.md` first (~10 min), then this doc (~5 min), then `OPEN_ITEMS.md` (~10 min). Done in ~25 min.

---

## Branch + repo state at session end

| Repo | Branch | HEAD | Pushed |
|---|---|---|---|
| code | `main` | `f6fa58b` (this update pending push) | ✅ (prior; this update pending) |
| athens-2026 | `main` | `e8751f5` | ✅ |

**athens-2026 voices folder now carries 10 of 10** shipped cards — the panel is complete:
`plato`, `cleopatra`, `dostoevsky`, `ibn_battuta`, `octopus`, `hannah_arendt`, `ada_lovelace`, `whanganui_river`, `scheherazade`, **`bob_marley` (NEW v2 today)**.

**Universal "Voice of X" naming sweep applied** across all 10 voices (athens-2026 `e8751f5`). Long-form first-person self-identification stays in `council_member_name`.

13th persona **`claudia_pinchbeck`** — operator-authored DRAFT card landed today at `current-tests/voices/claudia_pinchbeck/07_persona_card_assembled.json` for dryrun use only. Bypasses the persona pipeline; not promotion-ready. Real Stages A-F build awaits Beauty Shot dossier + voice_mode/byline decisions.

**Pass 1c fetch audit complete** (2026-05-04 PM). 10 athens-2026 voices + 3 current-tests duplicates. Findings: paywall + archive.org policy patterns produce 20-47% failure rates on cleopatra / hannah_arendt / ibn_battuta / octopus, but all voices have 4-7M chars of rich corpus from successful sources — no voice is corpus-starved. Two minor follow-ups filed as POST-ATHENS (do not affect runtime, only matter on rebuild): (a) Plato Perseus extractor bug — 6 sources fetched as 690-char error pages instead of dialogue text; (b) Bob Marley voiceofthesufferers.free.fr SSL cert mismatch on the Bullbay-reasoning interview URL. Audit details in OPEN_ITEMS §25.

---

## Where the 10 panel voices + Claudia stand

| Voice (council label) | type / voice_mode | State |
|---|---|---|
| Voice of Plato | human / philosophical | ✅ shipped + 2026-05-02 patched (`cf283bf`) |
| Voice of Cleopatra | human / observational | ✅ shipped at FU#61 v3 (`c89d186` + `54cd20a`) |
| Voice of Fyodor Dostoevsky | human / narratival | ✅ shipped via path (b) + FU#61-fresh (`5088d67`) |
| Voice of Ibn Battuta | human / narratival | ✅ shipped via path (b) (`e300508`) |
| Voice of the Octopus | non_human / observational | ✅ compass rebuild SHIPPED + chat-test VERIFIED (`04da2c8`) |
| Voice of Hannah Arendt | human / philosophical | ✅ shipped 2026-05-02 (`bfe917a`) |
| Voice of Ada Lovelace | human / philosophical | ✅ shipped 2026-05-02 (`3a6fe2f` → rolled-back `c025914`) |
| Voice of the Whanganui River | non_human / system / null | ✅ shipped 2026-05-03 evening (`c2151ce`) via path-(b) at ROUND6 |
| Voice of Scheherazade | fictional / narratival | ✅ shipped 2026-05-04 early-AM (`c2151ce`) via path-(b) at ROUND9 |
| **Voice of Bob Marley** | **human / observational** | ✅ **v2 SHIPPED + PROMOTED today** (`669a09b`) — Option-3 restructure per 6-note appropriation-feedback thread; 3 architectural prompt-edits landed (Pass 2 + Pass 4a + Pass 4b) generalizing to any future musical-corpus voice with living sacred grammar; AI Democracy Marathon test ran on v2; voice survives restructure with predicted rhetorical-force trade. v1 archived at `current-tests/voices/bob_marley_v1_archive/`. See OPEN_ITEMS §24. |
| **Claudia Pinchbeck** *(editor; 13th persona, NOT yet shipped)* | human / TBD (recommend `observational`) | 🟡 Persona-construction architecture landed 2026-05-03 in `voices/CLAUDIA_PINCHBECK_PERSONA_PREP_2026-05-03.md`. Hybrid pipeline path. Awaiting operator share of Beauty Shot dossier file + voice_mode/byline decisions to begin Stage A. ~7-9 hr Stages A-F when work resumes. |

**Universal "Voice of X" naming sweep applied today** across all 10 voices. Long-form self-identification stays in `council_member_name` (e.g., Cleopatra's Ptolemaic titulature, Battuta's full name chain). The `name` field across persona_card.voice_name + provocateur_profile.name + council_config.members[].name + panel_roster.panel_members_final is now uniformly "Voice of X".

---

## What landed today (2026-05-04 morning + afternoon session)

1. **Marley v2 SHIPPED + PROMOTED** via Option-3 restructure (athens-2026 `669a09b`). The construction steps back from deploying Rastafari sacred grammar (I-and-I as metaphysical subject, Jah-as-indwelling, Selassie-as-divinity) as the load-bearing premise of its own argument; treats them as Marley's attested commitments which the voice reports and stands by. Public political vocabulary (Babylon, Zion, downpression, sufferah, chanting-down, politricks, overstanding) remains deployable.

2. **3 architectural prompt edits landed** (uncommitted in code repo at session end — being committed now):
   - `personas/flows/shared/prompts/persona_pass_2_identity_boundaries.md`: SACRED-GRAMMAR DEPLOYMENT LIMIT block in `hard_limits` field-spec, conditional on `corpus_constraint == "lyrics_patterns_only"`. Generalizes to any future musical-corpus voice carrying living sacred grammar.
   - `personas/flows/shared/prompts/persona_pass_4a_voice.md`: replaced song-as-artifact `lyrics_patterns_only` block with two sub-blocks (musical-corpus-voice variant + sacred-grammar discipline at characteristic_moves level, with reviewer-marked-load-bearing example phrasing).
   - `personas/flows/shared/prompts/persona_pass_4b_artifact.md`: replaced song-as-artifact block with prose-yard-reasoning + Suno-style riddim-call (instrumental-only) two-shape spec; twin-failure-modes named (pastiche + composed-lyric-as-argument).
   - Plus `personas/run_persona_pipeline.py`: pipe `corpus_constraint` into Pass 2 render call.

3. **AI Democracy Marathon test ran on v2** (per reviewer's Step 5 "test before locking"). Result at `bob_marley/06_derive/_test_ai_democracy_marathon_v2.json`. Voice survives restructure with predicted rhetorical-force trade.

4. **Universal "Voice of X" naming sweep applied** across all 10 voices (athens-2026 `e8751f5`). Pure JSON edits, no LLM regen.

5. **Three operator-side readiness paragraphs drafted** (`voices/MARLEY_READINESS_PARAGRAPHS_2026-05-04.md` + `voices/VIDEO_TEAM_CONSTRAINT_SHEET_2026-05-04.md`):
   - D1 internal position paragraph (Marley appropriation; pre-Athens readiness)
   - E1 Athens intro paragraph (long + short; publish-or-hold pending Till)
   - F1 video team constraint sheet (Whanganui banned visual moves; framed as binding on production decisions)

6. **Doc updates** (this session): `voices/HANDOFF.md` rewritten (this doc); `voices/OPEN_ITEMS.md` §1 table → 10/10 + new naming + §24 added for Marley v2; `voices/ONBOARDING.md` §63 panel table refreshed with "Voice of X" labels.

---

## What's in flight at session end

Nothing pipeline-side. Marley v2 is shipped + promoted. Three operator-blocked tracks remain:

1. **Claudia Stages A-F** — awaits Beauty Shot dossier + voice_mode/byline decisions
2. **D1/E1 paragraph refinement to operator's voice** + E1 publish-or-hold call with Till
3. **Post-Athens Rastafari-orbit reader gate scheduling** — calendar date + name-search starts now

---

## Operator decisions pending

### Immediate / next session

1. **Claudia: Beauty Shot dossier share + voice_mode + byline split decisions** (carry-forward from 2026-05-03)
2. **D1 + E1 paragraph refinement** to your team's voice (Claude-voice drafts in MARLEY_READINESS_PARAGRAPHS_2026-05-04.md)
3. **E1 publish-or-hold call** with Till on Athens intro paragraph
4. **Post-Athens Rastafari-orbit reader gate** — calendar date + name-search (Tafari-Ama orbit / Cooper orbit / Bob Marley Foundation / Anthony Bogues at Brown)

### Carry-forwards

5. **Mediated-voice prompt-side fix as v4.1** — empirically validated across Plato + Whanganui + Scheherazade + Marley v1 (now Marley v2 has the upstream architectural fix); other voices' prompt-side fix remains v4.1 work
6. Plato thinking-on re-run experiment ($5, 30 min). See OPEN_ITEMS §5.
7. 9480d3a revert hypothesis re-evaluation — connected to FU#56. See OPEN_ITEMS §5.
8. WBBF program copy coordination (FU#49C remnant)
9. FU#49G Greek-scholar calibration on Plato — Quarch/Tsinorema/Erinakis on the provotype-test

### Pass 1c fetch audit — queued next

After today: audit Pass 1c fetch coverage across all 10 athens-2026 voices + 3 in current-tests. Spot-check correctness; trim or augment per voice. ~1-2 hr diagnostic, free.

---

## What I would do next session in priority order

1. **Pass 1c fetch audit** — read-only diagnostic across all 10. Surfaces any fetch gaps to fix. ~1-2 hr.
2. **Claudia Stages A-F** — once operator shares Beauty Shot dossier + decisions land. Stage A first (voice_config), operator review, Stage B (DR dossier sections), operator review, Stage C (pipeline run), operator gate.
3. **Operator-side D1/E1 refinement + post-Athens reader gate scheduling** — operator's actions, but I can support drafting / scheduling reminders if asked.
4. **Mediated-voice / sacred-grammar v4.1 prompt-side fix** — file as v4.1 work item; document the §9 + §24 pattern empirically validated across Plato + Whanganui + Scheherazade + Marley v2.

---

## Reading order for next session

1. `voices/ONBOARDING.md` (steady-state how-to + Pass 0a interrogation discipline + 3-posture taxonomy)
2. `voices/HANDOFF.md` — this doc
3. `voices/OPEN_ITEMS.md` (status snapshot — especially §1 per-voice state + §24 for today's Marley v2 work + §22 for prior-day Marley/Whanganui/Scheherazade work)
4. **For Claudia work resumption:** `voices/CLAUDIA_PINCHBECK_PERSONA_PREP_2026-05-03.md` is the comprehensive pickup doc; pair with `_workspace/archive/MEMO_2026_05_03_editor_flow_input_output_contract.md` (archived; v2 spec canonical at `docs/AI_Assembly_Editor_Pipeline.md`) for the runtime-contract context.
5. **For Marley v2 readiness materials:** `voices/MARLEY_READINESS_PARAGRAPHS_2026-05-04.md` (D1 + E1 drafts) + `voices/VIDEO_TEAM_CONSTRAINT_SHEET_2026-05-04.md` (F1 video-team brief).
6. `voices/MEMO_2026_05_01_recurrence_patterns_from_legitimacy_test.md` — runtime-thread findings doc (historical).

That's ~30 min to working knowledge for picking up voice-build work cold.

---

## When this doc goes stale

Update `HANDOFF.md` at the end of every voice-build session — it's the session-snapshot, not the steady-state. Roll the prior session's HANDOFF into the next session's by dating the doc and adding a "supersedes prior HANDOFF" note at top.
