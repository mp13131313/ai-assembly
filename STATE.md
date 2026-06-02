# Project state

**Single source of truth for "what's now."** When this doc disagrees with
another, this doc is right (or fix this doc). Snapshot **2026-06-01**.

---

## Status: Athens 2026 COMPLETE

All three Athens nights ran end-to-end and are **published** — 13 dossiers
+ 30 per-voice pages across Nights 1–3. Both repos clean + pushed; runtime
tests green (358 pass, 1 env-only artifact). Pre-Athens voice-build work
is COMPLETE. No work is in flight.

| Night | Lead dossier | Dossiers | Voices |
|---|---|---|---|
| 1 | dossier_001 *WHO TEACHES THE TEACHERS* | 5 | 10 |
| 2 | dossier_001 *WHOSE MOUTH IS MOVING* | 5 | 10 |
| 3 (closing) | dossier_002 *THE BODY OFF THE LEDGER* | 3 | 10 |

## The two repos

- **`mp13131313/ai-assembly`** (this repo) — runtime + personas + docs +
  planning trackers.
- **`mp13131313/ai-assembly-athens2026-voices`** (private) — the Athens
  production instance: 10 voice cards + config, `published_artifacts/` (the
  3 editions + editorial assessment + data inventory), and `runs/` (the
  full JSON "making-of" record: transcripts → voice reasoning → validation
  → dossiers; **audio excluded for size**).

---

## Per-night production results

### Night 1 (2026-05-07 panels → published 2026-05-08)

- ✅ Transcription: 12/12 sessions landed (9 audio via AssemblyAI + 3
  vendor reflection JSONs via reflection preprocessor + vendor_intake).
  1,454 turns / 80,082 words. Two Act One sessions used manual speaker_id
  passthrough (Sonnet + Opus both produced malformed JSON on 47-speaker
  output; operator-fix path: write passthrough out_02 → resume from
  cleaning-only).
- ✅ Researcher: 205 extractions / 37 clusters / 11 themes (clustering hit
  40K ceiling on 215-extraction first-pass; bumped CLUSTERING_MAX_TOKENS
  to 64K, retry succeeded at 38K/64K = 59% utilization).
- ✅ Provocateur: 46 formulations across 10 voices (8 themes selected,
  3 dropped); per-voice coverage 5/5 for 7 voices, 4/5 for Whanganui +
  Octopus, 3/5 for Ada (per natural Triage activation distribution).
- ✅ Voice: 46 Step 1 / 10 Step 2 outputs. Two fires — full 10-voice
  (12:00–12:26) + 3-voice rerun (12:55–13:00) for Battuta/Whanganui/
  Cleopatra to remove AI-self-acknowledgment from their artifacts
  (operator decision: only Hannah engages with synthesis as load-bearing
  meta-frame). Final validation: 4 PASS, 6 WARN, 0 HOLD.
- ✅ Editor: 5 dossiers · all 10 voices · lead = dossier_001 (theme_002
  paideia, 4 voices Ada+Hannah+Battuta+Plato, score 190 — best piece of
  writing in the edition per operator). Three editor fires: v1 initial
  7-voice composition · v2 full re-fire with voices-interleave rule · v2.1
  single-dossier fires for Marley + Whanganui-pair under sacred-grammar
  discipline.
- ✅ Publish: `published_artifacts/dossiers/night_1/` + `nights/night_1/`.

### Night 2 (2026-05-08 panels → published 2026-05-09)

- ✅ Transcription: 7 sessions — 6 audio + 1 vendor reflection (Dance and
  Dissent). 3 sessions were captured across two recordings, transcribed as
  `__audio2` session duplicates (Act Two / Act Three / The Reality Tunnels)
  → 9 audio files. 1,065 turns / 74,252 words. C49 manual speaker_id
  passthrough on Reality Tunnels primary (many-speaker map).
- ✅ Researcher: 199 extractions / 35 clusters / 8 themes. Wifi-drop
  mid-clustering → resumed from on-disk `all_extractions.json` by calling
  `cluster_extractions.fn()` + `group_clusters_into_themes.fn()` directly
  (`.fn` bypasses the Prefect task wrapper).
- ✅ Provocateur: 46 formulations / 10 briefings.
- ✅ Voice: 46 Step 1 / 10 Step 2. Final validation: 2 PASS, 8 WARN, 0 HOLD.
- ✅ Editor: 5 dossiers · lead = dossier_001 (*WHOSE MOUTH IS MOVING*,
  3 voices). Default framing preserved; Night-1 discipline rules carried
  forward.
- ✅ Publish: `dossiers/night_2/` (5) + `nights/night_2/` (10 voice pages).

### Night 3 — CLOSING EDITION (2026-05-09 panels → published 2026-05-11)

- ✅ Transcription: 6 sessions — 5 audio + 1 vendor reflection (Make
  Politics Great Again). 2 sessions double-captured → `__audio2` for Act
  Four + Act Five → 7 audio files. 652 turns / 54,038 words. C49 manual
  passthrough ×2 (Long Game, Act Five primary).
- ✅ Researcher: 125 extractions / 14 clusters / 5 themes.
- ✅ Provocateur: 36 formulations / 10 briefings.
- ✅ Voice: 36 Step 1 / 10 Step 2. Final validation: 2 PASS (Battuta +
  Octopus → auto-cleared, no operator gate), 7 WARN, 1 HOLD (Whanganui).
  All 8 WARN/HOLD voices operator-released; the HOLD was a C42 validator
  misfire (`ai_self_acknowledgment` / `first_person_presence_leak` on the
  sacred-grammar rerun), not a content defect. **FINAL-NIGHT notice**
  injected into all 10 `continuity_night_3.json` (gitignored): closing-
  edition *awareness*, not *register*.
- ✅ Editor: 3 dossiers · lead = dossier_002 (*THE BODY OFF THE LEDGER* —
  Lovelace + Marley + Dostoevsky, 3 voices). Tim used ~41K thinking tokens
  across the edition (dossier_002 alone 19,117; trace preserved at each
  dossier's TOP LEVEL — `d['thinking_trace']` — not in `metadata`).
- ✅ Publish: `dossiers/night_3/` (3) + `nights/night_3/` (10 voice pages).
  **Caveat:** the original run published only the 4 late-rerun voice pages
  (cleopatra / plato / scheherazade / whanganui); the other 6 were
  republished 2026-05-29 via `publish_voice_artifacts_for_night(night=3)`.
  Root cause + fix filed as `runtime/OPEN_ITEMS.md` C50.

---

## Deployment_context discipline rules

These rules lived in per-night gitignored
`runs/athens_night_<N>/_dossier_deployment_context.md` files; transcribed
here so they survive the gitignored run dirs.

**Night 1 (canonical baseline — three rules):**

1. **Provotypist anonymization** — Matthias Peschel does not appear in any
   publishable surface text; his interventions attribute to "the Voice of
   X, channelled into the room from the Assembly."
2. **Voices interleave, do not sequence** — voices appear inside Tim's
   argumentative paragraphs as evidence, not as section-headed sequenced
   exhibits. Quote-floor satisfied by interleaving.
3. **Sacred-grammar discipline** — Rastafari (`I-and-I`, `dawta`, `sufferah`,
   `livity`, `chanting-down`) and te-reo / Tupua-te-Kawa (`ea`, `mana`,
   `tupuna`, `kawa`, `whakapapa`, `mātauranga`) terms appear ONLY inside
   attributed quotation; editor narrative voice uses English equivalents.
   English-naturalized nouns (`iwi`, `marae`) and proper nouns (`Wai 167`,
   `Ruakā Marae`, `Te Awa Tupua`) remain as journalistic citation. Applies
   to Marley + Whanganui dossiers (the two voices carrying load-bearing
   sacred grammar in their cards).

**Night 2 additions:** default framing PRESERVED (the panels happened today);
cross-night threading to Night 1 enabled (≤1 sentence/article, only where
N2's argument picks up an open Night-1 line).

**Night 3 (closing) additions:** cross-night threading to N1+N2 (9 prior
dossiers). Load-bearing rule: **"closing-edition AWARENESS, not closing-
edition REGISTER."** Final night; the voices conclude their service after
tonight; there is no Night 4. Name an arc's completion ONCE, in-body
(never in kicker/close). Carry a voice's *own* closing register (a riddim
coda, a prostagma's seal, a dawn-cut, the riḥla halt's final dispatch)
into the headnote where the voice authored it — but do NOT impose closure
on a voice that didn't. Not a retrospective; each dossier still bridges
its own panels.

**Pickup pattern (Nights 2–3):** manual per-stage fires, NOT the
orchestrator — once direct fires are in flight, do NOT also start the
orchestrator (it sees `normalized` state and dispatches duplicate
transcriptions on top).

---

## Architectural validation (Athens-confirmed)

The `voice_temporal_stance.default` rewrite (athens-2026 `b2d5eaf` +
`7cdbee3` + `08a8253`) IS WORKING — voices meta-frame their own synthesis
as an object of critique rather than uncritically extending it; the §31
Gap-J / Memo §A.9 collision is empirically resolved.

---

## Voice-build state

**10 of 10 panel voices shipped + promoted + uniformly named** ("Voice of
X" convention across persona_card.voice_name + provocateur_profile.name +
council_config.members[].name + panel_roster.panel_members_final):

Voice of Plato · Voice of Cleopatra · Voice of Fyodor Dostoevsky · Voice
of Ibn Battuta · Voice of the Octopus · Voice of Hannah Arendt · Voice of
Ada Lovelace · **Voice of the Whanganui River v2** (witness-translator
architectural restructure shipped + ATHENS-CLEAN 2026-05-05 evening,
`c2a885b` + `3ccb1f9`; carries `mediation_stance == "transmission_witness"`)
· Voice of Scheherazade · Voice of Bob Marley (v2 Option-3 restructure
shipped 2026-05-04). `council_config.json` fully wired with all 10
pipeline-built provocateur_profiles.

**13th persona Tim Leberecht (Assembly editor)** — SHIPPED 2026-05-05
evening. Card at `athens-2026/editor/tim_leberecht/` (`9347743`). Runtime
`EDITOR_CARD_SUBPATH` renamed `claudia_pinchbeck` → `tim_leberecht`
(`b266f51`); 31/31 runtime tests pass post-rename. Tim is editor, NOT
panel — not in `panel_roster.json`. Earlier Claudia Pinchbeck DRAFT card
DEPRECATED on Tim ship. **Composed 13 dossiers across Athens Nights 1–3.**

**Architectural updates 2026-05-05 evening (athens-2026 main):**

- All 10 `voice_temporal_stance.default` fields shifted to assembly-fiction
  ("voice present at the assembly that gathers in Athens, observes
  panels, responds when consulted"); shipped `3bcbef5`. See
  `voices/OPEN_ITEMS.md §30`. **NOTE 2026-05-08:** this reframe APPENDED
  assembly clauses rather than LEADING with them; superseded by a 4×
  rewrite to the AF-LEADS + operator-short-draft architecture (Gap-K),
  now-final at athens-2026 `08a8253`. §30 carries the SUPERSEDED-by-§31-
  Gap-K pointer.
- Length-cap card surgery (operator decision: NO max_tokens enforcement):
  Dostoevsky 350–750w + Hannah Arendt 350–750w + Octopus 350–500w prose-
  channel front-loaded; shipped `404838d`. Closes `voices/OPEN_ITEMS.md §27`
  + cross-refs `runtime/OPEN_ITEMS.md C38`.

---

## Persona pipeline v4

`docs/AI_Assembly_Persona_Pipeline_v4.md`; `pipeline_version` string in
code: `"4.0"`. v3.10 archived at `docs/_archive/`. Pipeline architecture
includes chunked Pass 1.1–1.7 merge, Phase B per-voice folder layout,
Tier 3 code/project separation, and the FU#1–62 follow-up family
(closed/frozen as of 2026-05-01).

v4 prompt-architecture extensions:

- **2026-05-04:** `corpus_constraint == "lyrics_patterns_only"`
  conditional blocks in Pass 2 / Pass 4a / Pass 4b implementing the
  SACRED-GRAMMAR DEPLOYMENT LIMIT + prose-yard-reasoning artifact spec
  (Marley v2; generalizes to any future musical-corpus voice carrying
  living sacred grammar). See `voices/OPEN_ITEMS.md §24`.
- **2026-05-05:** `mediation_stance == "transmission_witness"` conditional
  blocks in Pass 2 + 3 + 4a + 4b + 5 + 6 implementing the TRANSMISSION-
  WITNESS DEPLOYMENT LIMIT + per-field discipline for witness-stance
  register (Whanganui v2; generalizes to any future rights-of-nature
  legal personalities, treaty-codified positions, ancestor-voices). See
  `voices/OPEN_ITEMS.md §28`.

v4.1 architectural cleanup post-Athens captured at `voices/OPEN_ITEMS.md
§31` (six gaps: A coverage gaps ✅ FIXED / B grammar bug ✅ FIXED / C
smoke-test process gap / D Pass 4a under-covers lexicon-repertoire / E
per-field discipline incompleteness / F v1 baseline drift on uncovered
fields).

---

## Open items (v4.1 — none Athens-blocking)

**`runtime/OPEN_ITEMS.md`** (C42–C52):

- **C42** safeguards-validator alignment with `voice_temporal_stance.default`
- **C43** validator JSON parse robustness
- **C44** researcher per-session extraction caching
- **C45** editor dossier file-existence caching
- **C46** `--single-dossier` index preservation
- **C47** editorial discipline rules → permanent prompt patches
- **C48** voice-pipeline deployment-context ✅ **RESOLVED 2026-06-01** —
  option-b retirement; branch deleted, design at
  `_workspace/planning/runtime/DESIGN_voice_deployment_context.md`, code
  preserved at tag `archive/voice-deployment-context-2026-05-05`
- **C49** many-speaker speaker_id structured-output JSON-decode → manual
  passthrough (recurring transcription failure: N1 ×2 + N2 ×1 + N3 ×2)
- **C50** `nights/_index.json` clobbered by single-voice publish (surfaced
  Athens N3 — left 6 voice pages unpublished)
- **C51** per-theme published artifacts (`themes/night_N/`) never generated
  for any night
- **C52** event-agnostic config externalization (Athens-isms hardcoded in
  `code` — not a zero-edit redeploy)

C42 + C43 both RECURRED in Nights 2–3 (C42 forced the Whanganui N3
operator-release; C43 validator parse-fallback on Marley N2 + Whanganui
N3) — recurrence notes appended to each entry.

**External, not built:** B2 microsite · B5 closing-show pipelines · B6
Day-4 goodbye · B7 full non-text render layer (Octopus shipped; Marley →
Suno pending) · B10 VM provisioning.

**Voices-thread (`voices/OPEN_ITEMS.md`):**

- §16.1 Plato anachronism patch
- §31 Gap-J per-voice coherence audit
- §11 post-Athens Rastafari-orbit + iwi-orbit reader gates
- Pre-Athens operator-side: D1/E1 paragraph use, Marley + Whanganui reader-
  gate work

**Future build (specified, not started):** vatican-2026 annotated-encyclical
run (`_workspace/planning/runtime/SPEC_2026_05_27_magnifica_humanitas_annotated_pipeline.md`).

---

## Where the detail lives

| For… | Read |
|---|---|
| Scaffolding for Claude sessions (filesystem layout, conventions, reading order) | [`CLAUDE.md`](CLAUDE.md) |
| Time-stamped events history | [`CHANGELOG.md`](CHANGELOG.md) |
| Athens-complete operator workflow handoff | [`_workspace/planning/runtime/HANDOFF_2026_05_29_ATHENS_COMPLETE.md`](_workspace/planning/runtime/HANDOFF_2026_05_29_ATHENS_COMPLETE.md) |
| Runtime open items + per-item detail | [`_workspace/planning/runtime/OPEN_ITEMS.md`](_workspace/planning/runtime/OPEN_ITEMS.md) |
| Voices-thread open items | [`_workspace/planning/voices/OPEN_ITEMS.md`](_workspace/planning/voices/OPEN_ITEMS.md) |
| Doc-infrastructure backlog (deferred reshapes, hygiene, operator decisions) | [`_workspace/planning/doc_infrastructure_backlog.md`](_workspace/planning/doc_infrastructure_backlog.md) |
| Naming + organization conventions | [`_workspace/planning/conventions.md`](_workspace/planning/conventions.md) |
| Editorial quality read of the dossiers | `athens-2026/published_artifacts/EDITORIAL_ASSESSMENT.md` (other repo) |
| Co-collaborator-facing tour of what was collected | `athens-2026/published_artifacts/DATA_INVENTORY.md` (other repo) |
| Runtime end-to-end operations | [`docs/AI_Assembly_Runtime_Lifecycle.md`](docs/AI_Assembly_Runtime_Lifecycle.md) |
| Fresh-session onboarding | [`_workspace/planning/ONBOARDING.md`](_workspace/planning/ONBOARDING.md) → `runtime/` or `voices/` |
