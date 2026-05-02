# Voices — Handoff (session-end snapshot, 2026-05-02 — supersedes earlier today)

**Companion:** `OPEN_ITEMS.md` (open-items list) + `ONBOARDING.md` (how-to / fresh-pickup). This doc is the session-end pickup snapshot: where we landed today, what's in flight, what's the next operator decision.

**On a fresh session:** read `ONBOARDING.md` first (~10 min), then this doc (~5 min), then `OPEN_ITEMS.md` (~10 min). Done in ~25 min.

---

## Branch + repo state at session end

| Repo | Branch | HEAD | Pushed |
|---|---|---|---|
| code | `voice-pipeline-v2.1-align-revert` | `a6755d9` (pre-this-doc-update) | ✅ |
| athens-2026 | `main` | `4cff85b` | ✅ |

athens-2026 production state untouched today — Octopus rebuild + 4 unbuilt voices + 1 deferred rebuild (Whanganui) all in `projects/current-tests` sandbox.

---

## Where the 10 panel voices stand

| Voice | type / voice_mode | State |
|---|---|---|
| Plato | human / philosophical | ✅ shipped (KNOWN: Socrates-self-referencing-death anachronism — see §16; dramatist-vs-speaker collision in 3 places — see §9) |
| Cleopatra | human / observational | ✅ shipped at FU#61 v3 (`c89d186` + `54cd20a`) |
| Dostoevsky | human / narratival | ✅ shipped via path (b) + FU#61-fresh (`5088d67`); KNOWN tic risk — closing on suspended judgment (see §16) |
| Battuta | human / narratival | ✅ shipped via path (b) (`e300508`); KNOWN tic risk — Tughluq beard-plucking anecdote (see §16) |
| **Octopus** | non_human / observational | ✅ shipped 2026-05-01 (`8bb9981` + `4cff85b`); 🔄 **compass rebuild in progress in current-tests** — voice_config + 6-layer chain + manual TAILORING preamble in DR prompts; awaiting operator's claude.ai DR sessions |
| Hannah Arendt | human / philosophical | 🟡 Pass 0a + Phase 0.5 done in current-tests; auto-generated DR prompts ready for claude.ai paste |
| Ada Lovelace | human / philosophical | 🟡 Pass 0a + Phase 0.5 done; auto-generated DR prompts ready |
| Bob Marley | human / **narratival** ✓ flipped | 🟡 Pass 0a + Phase 0.5 done; voice_mode flipped observational→narratival (Pass 0a hallucinated Card v2 reference per ONBOARDING DO-list); DR prompts ready; lyrics_patterns_only corpus_constraint |
| **Whanganui River** | non_human / system / null | 🟡 Pass 0a done + voice_config rewritten **transmission-faithful** (Tupua te Kawa verbatim + Te Pou Tupua mediation + Indigenous-authored scholarship); Phase 0.5 in flight at session end |
| Scheherazade | fictional / narratival | 🟡 Pass 0a done (auto-default voice_config; null editorial_rationale); Phase 0.5 in flight at session end. Mediated-voice prompt-fix concern carries through to her Pass 2 generation later |

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

## What's in flight at session end

1. **Phase 0.5 chain** — Whanganui + Scheherazade (~14 min wall + 503-retry buffer; scheduled wakeup at 09:12)
2. **All 6 voice rebuilds + new builds queued for operator's claude.ai DR sessions** — Octopus (compass rebuild) + Arendt + Lovelace + Marley + Whanganui + Scheherazade (DR prompts ready or pending Phase 0.5). 36 DR sessions total available across the 6 voices. Each ~30 min wall → ~18hr operator wall if all sequential, less if parallelized across browser tabs.

---

## Operator decisions pending (carried from 2026-05-01 + new)

### From earlier sessions

1. **Plato 3 surgical patches** for dramatist-vs-speaker collision. Drafted in HANDOFF_2026_04_28 §13, never applied. ~10 min. See OPEN_ITEMS.md §9.
2. **Plato thinking-on re-run experiment** ($5, 30 min). See OPEN_ITEMS.md §5.
3. **9480d3a revert hypothesis re-evaluation** — connected to FU#56. See OPEN_ITEMS.md §5.
4. **Mediated-voice prompt clarification** — verify status before Scheherazade's pipeline run. OPEN_ITEMS §3.

### From 2026-05-01 runtime-thread MEMO (legitimacy test findings) — NEW

5. **Plato — Socrates-self-referencing-death anachronism** 🔴 (sharpest finding, see OPEN_ITEMS §16). Voice-card constraint needed: banned_modes / quality_criteria / narrator-choice. Athens validation policy: ON N1 / OFF N2+3 — without voice-card guard, similar anachronism on N2/N3 would land in published artifacts.
6. **Plato — Theuth/Thamus reach** 🟡 (recurrence-tic risk; 3 resolution paths)
7. **Battuta — Tughluq beard-plucking** 🟡 (stock-anecdote tic; 3 resolution paths)
8. **Dostoevsky — closing on suspended judgment** 🟡 (closing-phrase tic; 2 resolution paths)

### Octopus rebuild verification (after operator runs DR sessions)

9. **Run pipeline on rebuilt Octopus** — cache-invalidate from Pass 1.1, fire `run_persona_pipeline.py "Octopus" --project /path/to/current-tests`
10. **Verify chat-test artifact** matches experiment-in-mind voice + chromatophore display engine integration
11. **Promote rebuilt Octopus to athens-2026** — copy `current-tests/voices/octopus/` → `athens-2026/voices/octopus/`. Athens-2026 commit + push.
12. **Document rebuild lessons** in voices/ONBOARDING

### Pipeline operations after DR sessions

13. **Run pipeline for Arendt + Lovelace + Marley + Whanganui + Scheherazade** — once their DR dossiers are saved. Each ~30-90 min wall. Validator round + path-(b) accept where appropriate.
14. **Promote new voice cards to athens-2026** — once verified.

---

## What I would do next session in priority order

1. **Run Octopus 6 DR sessions** in claude.ai — using compass-aligned prompts in current-tests. ~3hr operator wall.
2. **Optionally: run Arendt + Marley + Whanganui DR sessions in parallel browser tabs** while Octopus DR runs.
3. **After Octopus DR done: cache-invalidate + re-fire pipeline + chat-test the rebuilt voice + promote to athens-2026 if good**
4. **Plato Socrates-death anachronism patch** (highest-priority among legitimacy-test findings) — banned_modes addition or narrator-choice constraint
5. **Phase 0.5 chain check** — confirm Whanganui + Scheherazade landed cleanly; retry if Gemini 503 hit

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
