# Voices — Handoff (session-end snapshot, 2026-05-02 PM — supersedes 2026-05-02 AM)

**Companion:** `OPEN_ITEMS.md` (open-items list) + `ONBOARDING.md` (how-to / fresh-pickup). This doc is the session-end pickup snapshot: where we landed today, what's in flight, what's the next operator decision.

**On a fresh session:** read `ONBOARDING.md` first (~10 min), then this doc (~5 min), then `OPEN_ITEMS.md` (~10 min). Done in ~25 min.

---

## Branch + repo state at session end

| Repo | Branch | HEAD | Local commits since session start | Pushed |
|---|---|---|---|---|
| code | `voice-pipeline-v2.1-align-revert` | `7ef6d26` | 3 (`9fe6e87` hygiene §6 retire / `3baa649` FU#49C verified done / `7ef6d26` SKIP_TO_DERIVE + §16.5 decisions) | ✅ |
| athens-2026 | `main` | `cf283bf` | 1 (`cf283bf` Plato legitimacy-test surgical patches) | ✅ |

Plato shipped state was patched today (8 surgical patches: Socrates-death anachronism + dramatist-vs-speaker collision); Octopus + 4 unbuilt voices + Whanganui rebuild all still in `projects/current-tests` sandbox.

---

## Where the 10 panel voices stand

| Voice | type / voice_mode | State |
|---|---|---|
| **Plato** | human / philosophical | ✅ shipped + **2026-05-02 patched** (`cf283bf`): banned_modes[10] sharpened (Socrates-death anachronism); 7 dramatist-vs-speaker patches landed (Phaenarete-mother corrected + 5 passage headers switched to 3rd-person Socrates). KNOWN open: Theuth/Thamus recurrence-tic — owned by runtime continuity overlay (Path B). |
| Cleopatra | human / observational | ✅ shipped at FU#61 v3 (`c89d186` + `54cd20a`) |
| Dostoevsky | human / narratival | ✅ shipped via path (b) + FU#61-fresh (`5088d67`); KNOWN: closing-on-suspended-judgment phrase tic — owned by runtime continuity overlay (Path B) |
| Battuta | human / narratival | ✅ shipped via path (b) (`e300508`); KNOWN: Tughluq beard-plucking stock-anecdote tic — owned by runtime continuity overlay (Path B) |
| **Octopus** | non_human / observational | ✅ shipped 2026-05-01 (`8bb9981` + `4cff85b`); 🔄 **compass rebuild in progress in current-tests** — voice_config + 6-layer chain + manual TAILORING preamble in DR prompts; awaiting operator's claude.ai DR sessions |
| Hannah Arendt | human / philosophical | 🟡 Pass 0a + Phase 0.5 done in current-tests; auto-generated DR prompts ready for claude.ai paste |
| Ada Lovelace | human / philosophical | 🟡 Pass 0a + Phase 0.5 done; auto-generated DR prompts ready |
| Bob Marley | human / **narratival** ✓ flipped | 🟡 Pass 0a + Phase 0.5 done; voice_mode flipped observational→narratival (Pass 0a hallucinated Card v2 reference per ONBOARDING DO-list); DR prompts ready; lyrics_patterns_only corpus_constraint |
| **Whanganui River** | non_human / system / null | 🟡 Pass 0a done + voice_config rewritten **transmission-faithful** (Tupua te Kawa verbatim + Te Pou Tupua mediation + Indigenous-authored scholarship); Phase 0.5 done; DR prompts ready |
| Scheherazade | fictional / narratival | 🟡 Pass 0a done (auto-default voice_config; null editorial_rationale); Phase 0.5 done (after sustained Gemini 503 retry); DR prompts ready. Mediated-voice prompt-fix concern carries through to her Pass 2 generation later |

---

## Octopus compass rebuild (status as of 2026-05-02 session-end)

**Trigger:** chat-test of shipped Octopus card revealed it produced "scholarly translator reporting on the body from outside" rather than the experiment-in-mind voice the operator had originally blueprinted (March 2026 mock card + compass DR artifact). Shipped card was internally coherent + validator-passed but not the build the operator wanted.

**Diagnosis:** the live April 2026 claude.ai DR sessions had drifted toward precautionary-Continental philosophical framing — Birch's bracketing-as-method, Continental ethological-attunement, CARE Principles as binding constraint, research-governance-as-constitutive — propagating through Pass 1.4 voice synthesis into the built card's anti-unified-I refusal-to-render register. Editorial_rationale was actually compass-friendly all along; the drift came from §5 of the live DR + the operator-stage `review_doc` "refuse to invent... Confidence high" auto-generated language (Pass 0a LLM run-variance — see ONBOARDING DO-list).

**Approach: full rebuild from scratch in current-tests sandbox.** Snapshot of shipped Octopus state preserved at `projects/current-tests/voices/octopus_pre_compass_rebuild_2026-05-01/` (93 files, 9.1MB, full pipeline trail). Athens-2026 production state untouched until rebuild verified.

**What's done (2026-05-02):**

1. **Pass 0a re-run** — fresh review_doc surfaced "anthropomorphism vs excessive-alienness twin-risks" framing (vs April's "refuse to invent... Confidence high" precautionary language). Pass 0a interrogation discipline added to ONBOARDING (committed `1c83034`).
2. **`voice_config.manual_grounding`** rewritten — Godfrey-Smith primary + biology + lifecycle + three-registers (technical-neurobiological / philosophical-phenomenological / felt-encounter Montgomery+Scheel) + explicit 6-layer translation chain + compass framing. ~7,500 chars.
3. **`voice_config.editorial_rationale`** — preserved operator-written first paragraph byte-identical; added explicit 6-layer chain + compass scaffolding + twin-risks. ~5,500 chars.
4. **Pass 0b base template amendment** at `personas/flows/shared/prompts/pass_0b_non_human_organism.md` — 7 surgical edits making template **compass-permissive** (both precautionary AND phenomenologically-permissive postures supported; voice_config.editorial_rationale determines which). Committed `a6755d9`.
5. **Phase 0.5 v3.1** auto-generated 6 DR prompts from amended template + compass voice_config.
6. **Manual TAILORING ORIENTATION preamble** added to each of the 6 octopus DR prompts surfacing full 6-layer chain + compass scaffolding + twin-risks at every section paste.

**Status:** Octopus DR prompts ready for operator's claude.ai DR sessions. Each section ~30 min wall = ~3hr operator wall total. After all 6 saved → cache-invalidate from Pass 1.1 → re-fire pipeline.

**Backup snapshots preserved:**
- `voices/octopus_pre_compass_rebuild_2026-05-01/` (full athens-2026 shipped state)
- `voices/octopus/01_research/03_dr_prompts.surgical_v1/` (manual surgical edits)
- `voices/octopus/01_research/03_dr_prompts.v2_partial/` (auto-generated before §6 amendment)
- `voices/octopus/01_research/01_perplexity_dossier.pre_6layer.json` + `02_gemini_broad_scan.pre_6layer.json`

---

## Whanganui transmission-faithful rebuild (2026-05-02 session)

**Posture:** TRANSMISSION-FAITHFUL with mediation-acknowledged. Different from Octopus's compass phenomenologically-permissive imaginative reach — for Whanganui, the iwi and Crown already did the philosophical work in 2017 (Te Awa Tupua Act); the AI persona just stewards what is already written.

**voice_config (in `current-tests/voices/whanganui_river/`):**
- `manual_grounding` ~6,300 chars — verbatim Section 12 + Section 13 Tupua te Kawa (4 values bilingual, te-reo-primary) + Section 14 + Section 18 Te Pou Tupua + named guardians (Keria Ponga, Turama Hawira) + Te Pā Auroa governance ecology (Te Karewao / Te Kōpuka / Te Heke Ngahuru / Ngā Tāngata Tiaki o Whanganui / Ruruku Whakatupua 2014) + Wai 167 + Treaty of Waitangi 1840 + iwi confederation (Te Atihaunui-a-Pāpārangi 3 divisions + Ngāti Hāua + Ngāti Rangi + Tamahaki) + 3-register sources (legislation / Indigenous-authored scholarship / critique)
- `editorial_rationale` ~3,900 chars — TRANSMISSION job + Te Pou Tupua mediation + bilingual integrated register + twin-failure-modes (iwi-ventriloquism / legal-bureaucratese)

**Pass 0b template:** `pass_0b_non_human_system.md` is **already well-aligned** with transmission-faithful posture (no amendment needed). The system template was designed for legal-personhood + Indigenous-cosmology entities; it natively enforces verbatim quotation + iwi-non-ventriloquism + bilingual dual-register vocabulary + CARE-as-citation-discipline.

**Phase 0.5:** in flight at session end (Whanganui + Scheherazade chain).

---

## What landed today (PM session, 2026-05-02)

1. **Hygiene §6 retired** (`9fe6e87`) — verified all 6 sub-items already done; OPEN_ITEMS section retired with audit-trail note. Phase L lone residual cleared at `planning/ONBOARDING.md:67`. Octopus mid-rewrite stray (`07_section_5_dr_prompt.compass.md`) deleted.
2. **FU#49C verified done** (`3baa649`) — JSON rewrite landed clean across athens-2026 deployment JSONs (verified `conference_facts.json` + `audience_profile.json` + `panel_roster.json` + `council_config.json`). Only WBBF program-copy coordination remains operator-side.
3. **Plato legitimacy-test surgical patches** (`cf283bf` athens-2026):
   - banned_modes[10] sharpened (Socrates-death anachronism — Path A)
   - 7 dramatist-vs-speaker patches: characteristic_moves[9] + metaphorical_repertoire["midwifery"] + 5 passage headers (Path A comprehensive)
4. **path-(b) DERIVE-ONLY fast exit** (`7ef6d26`) — `run_persona_pipeline.py` skips Pass 7-* + fix-pass + assembly + 7a FINAL + gate when `_operator_review_passed.flag` + assembled card both present. Saves ~5 min wall + ~$2 per surgical-patch re-fire AND prevents auto-patcher from re-applying false-positive patches against operator-protected content. Tested on Plato: 80s wall, all 8 patches preserved.
5. **§16.5 decisions recorded**: Plato Socrates-death + dramatist collision = Path A (landed); Theuth/Thamus + Tughluq + Dostoevsky-closing = Path B (runtime continuity overlay; owned by runtime/OPEN_ITEMS C20).
6. **Scheherazade Phase 0.5 landed** (after sustained Gemini 503 retry chain) — DR prompts ready alongside the other 4.

---

## What's in flight at session end

1. **All 6 voice rebuilds + new builds queued for operator's claude.ai DR sessions** — Octopus (compass rebuild) + Arendt + Lovelace + Marley + Whanganui + Scheherazade. All 36 DR prompts ready. Each ~30 min wall → ~18hr operator wall if all sequential, less if parallelized across browser tabs.

---

## Operator decisions pending

### From earlier sessions

1. **Plato thinking-on re-run experiment** ($5, 30 min). See OPEN_ITEMS.md §5.
2. **9480d3a revert hypothesis re-evaluation** — connected to FU#56. See OPEN_ITEMS.md §5.
3. **Mediated-voice prompt clarification** — verify status before Scheherazade's pipeline run. OPEN_ITEMS §3. Drafted but never landed; decide before Scheherazade's Pass 0a fires OR plan for surgical patches at her gate.
4. **WBBF program copy coordination** (FU#49C remnant) — verify WBBF materials don't still describe AIssembly with deprecated "breakfast reading" framing.

### Legitimacy-test findings (resolved today via §16.5)

✅ Plato Socrates-death + dramatist-vs-speaker → Path A (landed)
🟡 Plato Theuth/Thamus + Battuta Tughluq + Dostoevsky closing-tic → Path B (runtime continuity; runtime/OPEN_ITEMS C20)

### Octopus rebuild verification (after operator runs DR sessions)

5. **Run pipeline on rebuilt Octopus** — cache-invalidate from Pass 1.1, fire `run_persona_pipeline.py "Octopus" --project /path/to/current-tests`
6. **Verify chat-test artifact** matches experiment-in-mind voice + chromatophore display engine integration
7. **Promote rebuilt Octopus to athens-2026** — copy `current-tests/voices/octopus/` → `athens-2026/voices/octopus/`. Athens-2026 commit + push.
8. **Document rebuild lessons** in voices/ONBOARDING

### Pipeline operations after DR sessions

9. **Run pipeline for Arendt + Lovelace + Marley + Whanganui + Scheherazade** — once their DR dossiers are saved. Each ~30-90 min wall. Validator round + path-(b) accept where appropriate.
10. **Promote new voice cards to athens-2026** — once verified.

---

## What I would do next session in priority order

1. **Run Octopus 6 DR sessions** in claude.ai — using compass-aligned prompts in current-tests. ~3hr operator wall.
2. **Optionally: run Arendt + Marley + Whanganui + Scheherazade DR sessions in parallel browser tabs** while Octopus DR runs.
3. **After Octopus DR done: cache-invalidate + re-fire pipeline + chat-test the rebuilt voice + promote to athens-2026 if good**
4. **Mediated-voice prompt clarification** before Scheherazade's pipeline fires (or plan for surgical patches at her gate per §9 architectural fix that was drafted-never-landed).

---

## Reading order for next session

1. `voices/ONBOARDING.md` (steady-state how-to + Pass 0a interrogation discipline + 3-posture taxonomy)
2. `voices/HANDOFF.md` — this doc
3. `voices/OPEN_ITEMS.md` (status snapshot — especially §15 Octopus rebuild + §16 legitimacy-test findings + §17 Whanganui rebuild + §3 unbuilt voices status update)
4. `voices/MEMO_2026_05_01_recurrence_patterns_from_legitimacy_test.md` — runtime-thread findings doc

That's ~30 min to working knowledge for picking up voice-build work cold.

---

## When this doc goes stale

Update `HANDOFF.md` at the end of every voice-build session — it's the session-snapshot, not the steady-state. Roll the prior session's HANDOFF into the next session's by dating the doc and adding a "supersedes prior HANDOFF" note at top.

If you want a versioned history, save prior HANDOFFs as `HANDOFF_<DATE>.md` in `_workspace/archive/voices_consolidation_<date>/`.
