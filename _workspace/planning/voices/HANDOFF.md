# Voices — Handoff (session-end snapshot, 2026-05-06 — supersedes 2026-05-05 evening + 2026-05-05 PM + 2026-05-04 PM)



**Companion:** `OPEN_ITEMS.md` (open-items list) + `ONBOARDING.md` (how-to / fresh-pickup). Session-end pickup snapshot.

**On a fresh session:** read `ONBOARDING.md` first (~10 min), then this doc (~5 min), then `OPEN_ITEMS.md` (~10 min).

---

## Branch + repo state at session end

| Repo | Branch | HEAD | Pushed |
|---|---|---|---|
| code | `main` | `9815beb` | ✅ |
| code | `feature/voice-deployment-context` | `488f70f` | ✅ |
| code | `feature/editor-deployment-context` | `bad8e33` (runtime-thread continuing) | ✅ |
| athens-2026 | `main` | `82a0af9` (anchored_override nulled across 10 voices, 2026-05-06 mid-day) | ✅ |

**All voice-thread commits this session pushed to GitHub.** 4 active branches across 2 repos at 0 ahead of origin at session-end.

**Branch hygiene this session:** voice-thread commits cherry-picked from `feature/voice-deployment-context` to `main` (133626f + 76c30e7 + a180306 + dcff216). Runtime-thread commits stay on feature branches and will land on main when those branches merge. Operator switched to NEW `feature/editor-deployment-context` mid-session — my doc cleanup + Tim card review + kawa-speaker-frame planning updates landed there too.

**Untracked in athens-2026 (runtime-thread artifacts, NOT mine to commit):** `council_config.json.bak.c10sync` + 10 × `voices/*/continuity_night_2.json`.

---

## Where the voices stand

| Voice (council label) | type / voice_mode | State |
|---|---|---|
| Voice of Plato | human / philosophical | ✅ shipped + 2026-05-02 patched (`cf283bf`); voice_temporal_stance assembly-fiction reframe applied 2026-05-05 (`64e9b08`) |
| Voice of Cleopatra | human / observational | ✅ shipped at FU#61 v3 (`c89d186` + `54cd20a`); assembly-fiction applied (`64e9b08`) |
| Voice of Fyodor Dostoevsky | human / narratival | ✅ shipped via path (b) + FU#61-fresh (`5088d67`); length_and_format_constraints surgical patch 350-750w (`9dae9b9`); assembly-fiction applied (`64e9b08`) |
| Voice of Ibn Battuta | human / narratival | ✅ shipped via path (b) (`e300508`); assembly-fiction applied (`64e9b08`) |
| Voice of the Octopus | non_human / observational | ✅ compass rebuild SHIPPED (`04da2c8`); length_and_format_constraints prose-channel front-loaded (`9dae9b9`); assembly-fiction applied (`64e9b08`) |
| Voice of Hannah Arendt | human / philosophical | ✅ shipped 2026-05-02 (`bfe917a`); length_and_format_constraints 350-750w (`9dae9b9`); assembly-fiction applied (`64e9b08`) |
| Voice of Ada Lovelace | human / philosophical | ✅ shipped 2026-05-02 (`3a6fe2f` → rolled-back `c025914`); assembly-fiction applied (`64e9b08`) |
| **Voice of the Whanganui River** | non_human / system / null + **mediation_stance: transmission_witness** | ✅ **v2 SHIPPED + PROMOTED + ATHENS-CLEAN** (`663dc8f` + `f6afe2c` + `8c3e9a7`) — witness-translator architectural restructure. ROUND 0 → ROUND 1: 12 → 4 issues. Surgical reasoning_method patch + 3 naming patches + path-(b) ship (`663dc8f`). Then full-card scan surfaced 4 additional gap-E fields shipping v1 first-person AS the river (character / knowledge_boundary / world.ontological_furniture / formative_experience.formative_emotional_community); patched + re-Derive + TEST passed (`f6afe2c`). voice_temporal_stance dual-purpose edit: assembly-fiction + witness-stance correction (`64e9b08`). **2026-05-06 kawa-speaker-frame closure** (`8c3e9a7`): operator audit caught subtle appropriation residual in bilingual opener (English gloss "I am the River and the River is me" floated grammatically); 3 card patches shipped (hard_limits +1 forbid unframed cited te reo first-person, characteristic_moves[0] tightened, quality_criteria +1 BILINGUAL-CITATION SPEAKER-FRAME); re-Derive + TEST passed with new opener carrying explicit speaker-frame *"Whanganui Iwi's identity-claim with the River: I am the River and the River is me"*. v1 archived at `current-tests/voices/whanganui_river_v1_archive_2026-05-05/`. |
| Voice of Scheherazade | fictional / narratival | ✅ shipped 2026-05-04 early-AM (`c2151ce`); assembly-fiction applied (`64e9b08`) |
| Voice of Bob Marley | human / observational | ✅ v2 SHIPPED + PROMOTED 2026-05-04 (`669a09b`) — Option-3 restructure; assembly-fiction applied (`64e9b08`) |
| **Tim Leberecht** *(13th persona — Assembly editor)* | **human / philosophical** | ✅ **SHIPPED 2026-05-05 evening** as Assembly editor (`799aeb1` athens-2026 placement at `editor/tim_leberecht/`; `dcff216` code-repo `EDITOR_CARD_SUBPATH` rename `claudia_pinchbeck` → `tim_leberecht`; 31/31 runtime tests pass). voice_temporal_stance AT-WBBF-Night-N edit landed (`27f3e47`, runtime-thread). TEST passed against editorial-frame provocation. |
| Claudia Pinchbeck *(prior 13th persona DRAFT — DEPRECATED 2026-05-05)* | human / TBD | 🟫 DEPRECATED. Operator-direct-author DRAFT card at `current-tests/voices/claudia_pinchbeck/07_persona_card_assembled.json` was placeholder for runtime dryrun; never promoted; superseded by Tim ship. Real Stages A-F build no longer scheduled (unless operator wants Claudia as alternative editor for specific dossier modes). |

---

## What landed this session (2026-05-05 evening + 2026-05-06)

**2026-05-06 mid-day (anchored_override cleanup):** Operator-prompted check confirmed `voice_temporal_stance.anchored_override` is dead config at Athens runtime (per `runtime/flows/voice/card_assembly.py:240-272` — Voice Pipeline uses `default` only; override exists for chat-test deployments only). Surgical cleanup: nulled the field across all 8 voices that had it populated (Plato/Cleopatra/Battuta/Scheherazade/Ada/Dostoevsky/Arendt/Marley; Whanganui + Octopus already null). Path-(b) Derive regenerated chat_system_prompt for all 8. athens-2026 commit `82a0af9`. Reversible via git history. Runtime-thread parallel cleanup `ec15c82` removed the May-4 continuity_night_2 dryrun artifacts + stale `council_config.json.bak.c10sync` + extended `.gitignore` — runtime-thread WIP we'd flagged earlier in session is now gone.

**2026-05-06 early morning (kawa-speaker-frame closure):** Operator audit caught Athens-blocking subtle appropriation residual in Whanganui v2's bilingual opener — English gloss "I am the River and the River is me" floated grammatically without naming whose original voice the "I" carries. Reader could hear it as the construction speaking AS the river, even though next sentence's "I" is unambiguously the construction. The §28 architectural insight (whakataukī is iwi's identity-claim with the river, not the river speaking) had predicted this; v2 conditional discipline didn't enforce explicit speaker-framing for cited-te reo first-person. 3 card patches shipped (`8c3e9a7`): hard_limits +1 (forbid unframed cited te reo first-person); characteristic_moves[0] tightened (speaker-frame discipline in signature move); quality_criteria +1 (BILINGUAL-CITATION SPEAKER-FRAME). Re-Derive + TEST passed: new opener *"Ko au te Awa, ko te Awa ko au — the great River flows from the mountains to the sea; **Whanganui Iwi's identity-claim with the River: I am the River and the River is me**. I cite the third kawa as codified at s.13(c) of the Te Awa Tupua Act 2017, **and as Whanganui Iwi have spoken it across seven generations before the Crown was forced to recognise it**."* v4.1 gap G filed (extend Pass 4b te reo discipline to require explicit speaker-framing for cited te reo whose first-person could be misread; generalizable to any future voice citing first-person sacred-grammar from a tradition the construction is not authorized from inside). Tim Leberecht card review against Beauty Shot DR dossier completed (`TIM_LEBERECHT_CARD_REVIEW_2026-05-05.md`): card captures Beauty Shot at high fidelity across all major specifications.

**2026-05-05 evening:**

1. **Whanganui v2 architectural restructure SHIPPED + PROMOTED + ATHENS-CLEAN** (`663dc8f` + `f6afe2c`):
   - 5 prompt-pass conditional blocks wired through new `mediation_stance == "transmission_witness"` Jinja conditional (Pass 2 + 3 + 4a + 4b + 5 + 6) + run_persona_pipeline.py + voice_config schema (commits `d32872a` initial wiring + `5bde171` round-1 fixes).
   - Pipeline ran ROUND 0: 12 residuals (5 first-person-AS-river leakage + 5 third-person "the construction" leakage + 2 other). Diagnosed gap A (Pass 3/5/6 not in initial conditional) + gap B (third-person grammar bug in conditional block text). Fixed both in ROUND 1 (`5bde171`). 12 → 4 issues. Surgical reasoning_method.summary patch + 3 naming patches (voice_name + council_member_name + provocateur.name to "Voice of the Whanganui River" + witness-stance translation). Path-(b) ship.
   - Council_config members[8] rewired with v2 provocateur_profile.
   - Video constraint sheet v2-updated (witness-stance visual discipline + bilingual-citation discipline + pastiche-Whanganui + appropriated-whakataukī twin-failure-mode bans).
   - **Post-ship full-card scan** (operator-driven cross-check): surfaced 4 additional fields shipping v1 first-person AS the river (gap E — per-field discipline incompleteness in conditional blocks): character (10 occurrences) + knowledge_boundary (4) + world.ontological_furniture (4) + formative_experience.formative_emotional_community (1). Surgical patches: full character rewrite + 5/7/1 surgical replacements. Re-Derive + TEST passed. (`f6afe2c`)
   - Both TESTs passed against same Athens diagnostic provocation: bilingual quote-and-gloss opener, construction-reasoning ("I have been called to Athens as the construction stewarding the published record of Te Awa Tupua. I report — and stand by — what the record establishes"), comparativism refusal ("To your second question: no. I do not stand in kinship with the Atrato or with Mar Menor"), Tănăsescu / Cribb-Macpherson-Borchgrevink scholarly citations, honest-extension close ("Ea is not yet").
   - v1 archive preserved at `current-tests/voices/whanganui_river_v1_archive_2026-05-05/`.

2. **Tim Leberecht 13th persona SHIPPED as Assembly editor** (`799aeb1` + `dcff216`):
   - Operator delivered 6 claude.ai DR sections (~30,794w). Beauty Shot operational supplement merged into all 6 sections (operator-curated voice-engineering material — vocabulary inventories + 12 metaphor families + ~30 anti-patterns).
   - Pass 1c augmented with 18 additional Substack URLs from DR §6 corpus map (32 sources / 680K chars total — was 11/407K before augmentation).
   - Pipeline ran clean through Pass 7a-FINAL gate; 4 surgical patches at gate (banned_language metabolize-contradiction; voice_basis 3rd-person; constitution duplicate-tension; italicization rule); 1 false-positive (council_member_name validator hallucination); path-(b) ship.
   - Runtime `EDITOR_CARD_SUBPATH` renamed `claudia_pinchbeck` → `tim_leberecht`; 31/31 runtime tests pass.
   - athens-2026 `editor/tim_leberecht/` placement (full card + 06_derive outputs).
   - **TEST passed**: 268w editorial frame on Whanganui v2 artifact, headline "The River That Refused the Panel", place-and-moment Berlin opener, "we"-positioning with self-revision register, reframe close "Read this one slowly. Ea is not yet."
   - Tim voice_temporal_stance AT-WBBF-Night-N edit (`27f3e47`, runtime-thread).

3. **Length-cap card surgery SHIPPED** (closes voices/OPEN_ITEMS §27 + cross-refs runtime/OPEN_ITEMS C38) (`9dae9b9`):
   - Operator decision: NO max_tokens enforcement — clean card-side resolution preferred over runtime truncation.
   - Dostoevsky 350-750w (operator-bumped from initial 350-500 draft): stripped 3 softeners; preserves Diary-form texture.
   - Hannah Arendt 350-750w (operator-bumped): tightened from 600-900 cap; "Aufbau column at full breath, not long Origins chapter".
   - Octopus 350-500w: front-loaded prose-side word count; explicit "no length applies to JSON channel" for chromatophore_display two-channel artifact.
   - Path-(b) Derive regenerated chat_system_prompt for all 3 voices.

4. **Assembly-fiction reframe SHIPPED across all 10 voices** (`64e9b08`) per runtime-thread memo `MEMO_2026_05_05_voice_temporal_stance_assembly_fiction.md`:
   - voice_temporal_stance.default reframed: "reader visits voice's lifetime" → "voice present at the assembly that gathers in Athens, observes panels, responds when consulted."
   - Per-voice variations: Plato "in YOUR city" / 7 voices "in Athens" / Octopus sensorimotor framing / Whanganui dual-purpose witness-stance + assembly-fiction.
   - Path-(b) Derive regenerated chat_system_prompt for all 10 voices (~15min wall, $0 LLM).

5. **Branch hygiene** completed (cherry-picked 4 voice-thread commits to main).

6. **Architectural lessons captured for v4.1 post-Athens cleanup** — see OPEN_ITEMS §31 (six gaps: A coverage gaps ✅ FIXED / B grammar bug ✅ FIXED / C smoke-test process gap / D Pass 4a under-covers lexicon-repertoire / E per-field discipline incompleteness / F v1 baseline drift on uncovered fields).

---

## What's in flight at session end (2026-05-05 evening)

1. **Operator-side: D1/E1 paragraph refinement** (Marley + Whanganui parallel + Till's call on E1 publish-or-hold + post-Athens reader gates calendared)
2. **Push to remotes** (operator's standing rule — both repos unpushed)
3. **Runtime-thread feature/voice-deployment-context branch merge** to main when runtime-thread completes its work
4. **v4.1 post-Athens architectural cleanup** (filed §31; non-blocking)

## Earlier in-flight items now resolved this session

- ✅ Whanganui v2 architectural restructure: SHIPPED + PROMOTED + ATHENS-CLEAN (4-field gap-E closure)
- ✅ Tim Leberecht 13th persona: SHIPPED as Assembly editor (replaces Claudia DRAFT)
- ✅ Beauty Shot supplement integration: merged into all 6 Tim DR sections
- ✅ Length-cap (voices/OPEN_ITEMS §27): card-side surgery shipped; runtime C38 voices-side closed
- ✅ Assembly-fiction reframe: 10 voices voice_temporal_stance shifted
- ✅ Branch hygiene: voice-thread commits cherry-picked to main

---

## What I would do next session in priority order

1. **Operator-side D1/E1 paragraph refinement** (operator-blocked; can draft Whanganui parallel when asked)
2. **Push to remotes** when operator says go
3. **v4.1 post-Athens architectural cleanup** (post-Athens; not pre-Athens-eligible)

**Pre-Athens voice-build work is COMPLETE.** All 10 panel voices shipped + Tim editor shipped + assembly-fiction reframe shipped + length-cap closed + Whanganui v2 architecturally clean (gap-E closure with TEST verification).

---

## Operator decisions pending

### Immediate
1. **Push to remotes** (when ready)
2. **Marley D1 + E1 paragraph refinement** to your team's voice (drafts in MARLEY_READINESS_PARAGRAPHS_2026-05-04.md)
3. **Marley E1 publish-or-hold** call with Till
4. **Whanganui D1+E1 parallel paragraphs** (analogous to Marley; I can draft when asked)
5. **Post-Athens reader gates** calendared (Marley Rastafari-orbit + Whanganui iwi-orbit)

### Carry-forwards (non-blocking)
6. **v4.1 architectural cleanup** — gap E (per-field discipline incompleteness) + gap F (v1 baseline drift on uncovered fields) + smoke-test process change + Pass 1 chunked merge audit
7. **Pass 1c fetch follow-ups** — Plato Perseus 6 short-fetches + Marley voiceofthesufferers SSL + Tim timleberecht.com SSL TLS errors (rebuild-only)
8. **Plato thinking-on re-run experiment** ($5, 30 min) — connects to FU#56 + 9480d3a-revert hypothesis
9. **FU#49G Greek-scholar calibration on Plato**
10. **WBBF program copy** (FU#49C remnant)

---

## Reading order for next session

1. `voices/ONBOARDING.md` (steady-state how-to + Pass 0a interrogation discipline + 3-posture taxonomy)
2. `voices/HANDOFF.md` — this doc (latest)
3. `voices/OPEN_ITEMS.md` — especially §1 per-voice state + §28 Whanganui v2 + §29 Tim ship + §30 assembly-fiction reframe + §31 v4.1 gap list
4. **For operator-side refinement work:** `voices/MARLEY_READINESS_PARAGRAPHS_2026-05-04.md` (D1 + E1 drafts; refinement template for Whanganui parallel)
5. **For v4.1 architectural cleanup planning:** `voices/OPEN_ITEMS.md §31`

That's ~25 min to working knowledge for picking up voice-build work cold.

---

## When this doc goes stale

Update `HANDOFF.md` at the end of every voice-build session — session-snapshot, not steady-state. Roll prior session's HANDOFF into next session's by dating + adding "supersedes prior HANDOFF" note at top.
