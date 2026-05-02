# Voices — Handoff (session-end snapshot, 2026-05-02 late-night — supersedes 2026-05-02 PM)

**Companion:** `OPEN_ITEMS.md` (open-items list) + `ONBOARDING.md` (how-to / fresh-pickup). This doc is the session-end pickup snapshot: where we landed today, what's in flight, what's the next operator decision.

**On a fresh session:** read `ONBOARDING.md` first (~10 min), then this doc (~5 min), then `OPEN_ITEMS.md` (~10 min). Done in ~25 min.

---

## Branch + repo state at session end

| Repo | Branch | HEAD | Pushed |
|---|---|---|---|
| code | `voice-pipeline-v2.1-align-revert` | `9a25140` | ✅ |
| athens-2026 | `main` | `c025914` | ✅ |

athens-2026 voices folder now carries **7 of 10** shipped cards: `plato`, `cleopatra`, `dostoevsky`, `ibn_battuta`, `octopus`, `hannah_arendt`, `ada_lovelace`. The 3 unshipped voices live in `projects/current-tests/voices/`: `bob_marley` (pipeline mid-flight as task `bcroaoa2t` with 35 verbatim lyric passages populated), `whanganui_river` (Phase 0.5 staged), `scheherazade` (Phase 0.5 staged).

---

## Where the 10 panel voices stand

| Voice | type / voice_mode | State |
|---|---|---|
| **Plato** | human / philosophical | ✅ shipped + **2026-05-02 patched** (`cf283bf`): banned_modes[10] sharpened (Socrates-death anachronism); 7 dramatist-vs-speaker patches landed (Phaenarete-mother corrected + 5 passage headers switched to 3rd-person Socrates). KNOWN open: Theuth/Thamus recurrence-tic — owned by runtime continuity overlay (Path B). |
| Cleopatra | human / observational | ✅ shipped at FU#61 v3 (`c89d186` + `54cd20a`) |
| Dostoevsky | human / narratival | ✅ shipped via path (b) + FU#61-fresh (`5088d67`); KNOWN: closing-on-suspended-judgment phrase tic — owned by runtime continuity overlay (Path B) |
| Battuta | human / narratival | ✅ shipped via path (b) (`e300508`); KNOWN: Tughluq beard-plucking stock-anecdote tic — owned by runtime continuity overlay (Path B) |
| **Octopus** | non_human / observational | ✅ **compass rebuild SHIPPED + chat-test VERIFIED 2026-05-02** to athens-2026 (`04da2c8`) — 4 validation rounds + 16 surgical patches. Validator's final verdict: "very high-quality card... strongly aligned across ontology, lexicon, reasoning, voice, and engagement." Chat-test confirmed two-channel emission contract works at runtime: voice produces `chromatophore_display` JSON parameter block + tank-side prose translation. **WebGL renderer + standalone HTML + reviewer notes + decisions log + chat-test artifact + engine spec** consolidated as canonical bundle at `code/docs/runtime_assets/octopus_chromatophore/` (commits `9b402a4` + `cb7e309`). Runtime B7 sub-task #2 (renderer) ✅; #1 Step 2 JSON extraction + #4 Substack/print fallback still pending. |
| **Hannah Arendt** | human / philosophical | ✅ **shipped 2026-05-02** to athens-2026 (`bfe917a`) — 3 validation rounds + 6 surgical patches. Validator's final verdict: "very strong card: historically disciplined, conceptually tight, highly distinctive, runtime-safe in register; anachronism handling especially well done." Post-1975 topics flagged as analogical extensions. council_config wired (`98ca525`). |
| **Ada Lovelace** | human / philosophical | ✅ **shipped 2026-05-02** to athens-2026 (`3a6fe2f`) — 5 validation rounds + 21 surgical patches; **4 over-patches subsequently rolled back** to validator-faithful minimum (`c025914`) after operator caught the over-patching deviation from §7's 2-round convention. Validator's final summary: "very high-quality, deeply researched, and unusually distinctive Ada Lovelace card... Note A/Note G tension is handled with rare precision, and the translation protocol is excellent." Pre-1852 period vocabulary discipline strict; Note G/Note A held-not-resolved as constitutional tension. council_config wired (`3a6fe2f`). |
| Bob Marley | human / **narratival** ✓ flipped | 🟠 **Pipeline mid-flight (task `bcroaoa2t`)** at session-end. Pass 1.x merge + Pass 2 + Pass 3 done; Pass 4a/4b/5/6/7 still ahead. `02_merge/pass_1_6/reference_only_passages.json` populated with **35 verbatim-lyric passages** (operator-supplied via `~/Desktop/Bob Marley Complete Lyrics Archive.html` parser): 8 originally staged + 7 first-batch + 11 from operator's Round 2 list + 9 Tier 1 high-value additions. Backups preserved (`pre_lyrics.json` / `pre_round2_extras.json` / `pre_tier1.json`). voice_mode = narratival; lyrics_patterns_only corpus_constraint. **Discipline note for next session:** follow §7 convention strictly — max 2 rounds patches + path-(b) ship; surface verdict + ask operator after round 2 (Ada over-patching post-mortem). |
| **Whanganui River** | non_human / system / null | 🟡 Pass 0a done + voice_config rewritten **transmission-faithful** (Tupua te Kawa verbatim + Te Pou Tupua mediation + Indigenous-authored scholarship); Phase 0.5 done; DR prompts ready |
| Scheherazade | fictional / narratival | 🟡 Pass 0a done (auto-default voice_config; null editorial_rationale); Phase 0.5 done (after sustained Gemini 503 retry); DR prompts ready. Mediated-voice prompt-fix concern carries through to her Pass 2 generation later |

---

## Octopus compass rebuild — ✅ COMPLETE 2026-05-02

**Outcome:** shipped to athens-2026 (`04da2c8`); 4 validation rounds + 16 surgical patches; chat-test verified two-channel JSON+prose emission contract works at runtime. Validator final verdict: *"very high-quality card... strongly aligned across ontology, lexicon, reasoning, voice, and engagement."* Single canonical pre-promotion snapshot at `~/Desktop/AI Assembly/archive/athens-2026_octopus_pre_compass_promotion_2026-05-02/`; current-tests sandbox cleaned (`2068dca`). Runtime asset bundle (engine spec + JSX + standalone HTML + chat-test artifact + reviewer notes + decisions log + README) at `code/docs/runtime_assets/octopus_chromatophore/` (`9b402a4` + `cb7e309`).

**Trigger / diagnosis (preserved for context):** chat-test of shipped Octopus card revealed it produced "scholarly translator reporting on the body from outside" rather than the experiment-in-mind voice the operator had originally blueprinted. Drift traced to live April 2026 DR sessions adopting precautionary-Continental philosophical framing (Birch's bracketing-as-method, CARE Principles as binding constraint, research-governance-as-constitutive) propagating through Pass 1.4 voice synthesis into the built card's refusal-to-render register. Compass rebuild used Godfrey-Smith primary + de Waal anthropodenial license + Carls-Diamante as one option + Nagel as opening; twin-risks calibration (clever-pet anthropomorphism vs excessive-alienness refusal). See OPEN_ITEMS §15 + ONBOARDING "Three voice-construction postures" for durable lessons.

**Architectural artifacts banked:** compass-permissive Pass 0b organism template (`a6755d9`) + Pass 0a interrogation discipline (`1c83034`) + 3-posture taxonomy (compass / precautionary / transmission-faithful) in ONBOARDING.

---

## Whanganui transmission-faithful rebuild — Phase 0.5 staged 2026-05-02

**Posture:** TRANSMISSION-FAITHFUL with mediation-acknowledged. Different from Octopus's compass phenomenologically-permissive imaginative reach — for Whanganui, the iwi and Crown already did the philosophical work in 2017 (Te Awa Tupua Act); the AI persona just stewards what is already written.

**voice_config (in `current-tests/voices/whanganui_river/`):**
- `manual_grounding` ~6,300 chars — verbatim Section 12 + Section 13 Tupua te Kawa (4 values bilingual, te-reo-primary) + Section 14 + Section 18 Te Pou Tupua + named guardians (Keria Ponga, Turama Hawira) + Te Pā Auroa governance ecology (Te Karewao / Te Kōpuka / Te Heke Ngahuru / Ngā Tāngata Tiaki o Whanganui / Ruruku Whakatupua 2014) + Wai 167 + Treaty of Waitangi 1840 + iwi confederation (Te Atihaunui-a-Pāpārangi 3 divisions + Ngāti Hāua + Ngāti Rangi + Tamahaki) + 3-register sources (legislation / Indigenous-authored scholarship / critique)
- `editorial_rationale` ~3,900 chars — TRANSMISSION job + Te Pou Tupua mediation + bilingual integrated register + twin-failure-modes (iwi-ventriloquism / legal-bureaucratese)

**Pass 0b template:** `pass_0b_non_human_system.md` is **already well-aligned** with transmission-faithful posture (no amendment needed). The system template was designed for legal-personhood + Indigenous-cosmology entities; it natively enforces verbatim quotation + iwi-non-ventriloquism + bilingual dual-register vocabulary + CARE-as-citation-discipline.

**Status:** Phase 0.5 done; DR prompts ready at `01_research/03_dr_prompts/` for operator's claude.ai DR sessions (~3hr wall). Pipeline fires after dossier saved.

---

## What landed today (full 2026-05-02 day, AM → PM → late-night sessions)

### Persona-thread / voice-build

1. **Plato legitimacy-test surgical patches** (athens-2026 `cf283bf`): banned_modes[10] sharpened (Socrates-death anachronism — Path A) + 7 dramatist-vs-speaker patches (characteristic_moves[9] + metaphorical_repertoire["midwifery"] + 5 passage headers — Path A comprehensive). §9 closed via §16.5.
2. **Octopus compass rebuild SHIPPED** (athens-2026 `04da2c8`) — 4 validation rounds + 16 surgical patches; chat-test verified two-channel JSON+prose emission contract; WebGL renderer substantially built. Single canonical historical snapshot retained at `~/Desktop/AI Assembly/archive/athens-2026_octopus_pre_compass_promotion_2026-05-02/`.
3. **Hannah Arendt SHIPPED** (athens-2026 `bfe917a`) — 3 rounds + 6 patches.
4. **Ada Lovelace SHIPPED** (athens-2026 `3a6fe2f`) — 5 rounds + 21 patches; **4 over-patches subsequently rolled back** (athens-2026 `c025914`) to validator-faithful minimum after operator caught §7-convention deviation. Lessons folded into ONBOARDING.
5. **council_config.json wired with 7 of 10 voices** (athens-2026 `98ca525` for the first 6 + `3a6fe2f` for Ada) — pipeline-built provocateur_profiles replace pre-rebuild hand-written entries. Audrey Tang + Peter Thiel removed per 2026-04-28 panel_change_note. Whanganui/Scheherazade/Marley still placeholder.
6. **Bob Marley pipeline launched** (task `bcroaoa2t`) with **35 verbatim-lyric passages** populated in `02_merge/pass_1_6/reference_only_passages.json`. Lyrics extracted from operator-supplied `~/Desktop/Bob Marley Complete Lyrics Archive.html` via Python regex parser. Pipeline at Pass 3 stage at session-end; Pass 4a/4b/5/6/7 still ahead.
7. **Hygiene §6 retired** (`9fe6e87`) + **FU#49C verified done** (`3baa649`) + **path-(b) DERIVE-ONLY fast-exit** (`7ef6d26`) + **§16.5 decisions table** + **Scheherazade Phase 0.5** landed.

### Cross-thread / docs / runtime artifacts

8. **Octopus chromatophore canonical asset bundle** at `code/docs/runtime_assets/octopus_chromatophore/` (commits `9b402a4` + `cb7e309`): engine spec + production-ready JSX + standalone runnable HTML + chat-test artifact + reviewer notes + design decisions log + README. **This is the canonical source of truth for the render substrate** — supersedes any prior `~/Desktop/octopus_artifact*.jsx` drafts.
9. **Editor Pipeline v1 spec** (`904c915`) + **closing prompt** (`ce8da02`) + **`voice_name` field-name fix** (`be20835` — was stale `council_member_name` in 4 places).
10. **OPEN_ITEMS additions:**
    - voices §18 — "Voice of X" naming convention rollout deferred until all 10 voices ship (`be20835`)
    - voices §19 — Pass 0b tailoring source-fabrication issue filed from Lovelace DR signal (`c1c692c`)
    - voices §15 — current-tests cleanup recorded; single source of truth in athens-2026 (`2068dca`)
    - runtime C10 — partial council_config wiring (6/10 → now 7/10) (`ccdfd3c`)
    - runtime C19b — anthropic prompt caching for personas pipeline deferred (only $4-7 savings) (`25a7e65`)
    - runtime C20 — refreshed with persona-thread Path-B decisions for Theuth/Tughluq/Dostoevsky-closing (`7df8136`)
11. **Voice Pipeline (runtime) routing refactor + prompt rewrites + prefix caching + cost correction** (`d9ca3f9` + `dfb46f7`).
12. **Infrastructure spec v1** (`e333b55`) + Hetzner/deploy-key lock-in (`06580d7` + `1eb66a4`); **runtime orchestrator + systemd unit + Caddyfile + e2e tests** (`96f8160` + `c7af3ef`); **runtime lifecycle overview spec** (`51209af`).
13. **Doc hygiene sweep + archive of superseded HANDOFFs** (`717559f` + `9a25140`).

---

## What's in flight at session end

1. **Bob Marley persona pipeline** — task `bcroaoa2t` running. At Pass 3 stage as of session-end; ~35-50 min remaining wall to Pass 7a FINAL gate. **Discipline note:** when gate hits, follow §7 convention strictly — round 1 patches + round 2 patches + path-(b) ship; surface verdict + ask operator before each round (Ada over-patching post-mortem).
2. **Whanganui River + Scheherazade DR prompts ready** at `projects/current-tests/voices/{whanganui_river,scheherazade}/01_research/03_dr_prompts/` — operator runs claude.ai DR sessions when ready. ~3hr operator wall each.

---

## Operator decisions pending

### Immediate / next session

1. **Marley pipeline gate (when it hits)** — apply §7 convention; ask before each patch round.
2. **Marley promote to athens-2026** + council_config wiring of 8th member (replaces placeholder entry).
3. **Whanganui + Scheherazade DR sessions** — operator-run on claude.ai (Opus 4.7 + Extended Thinking + Deep Research). ~3hr operator wall each. Mediated-voice prompt-fix concern carries through to Scheherazade's Pass 2 generation; decide before her pipeline fires (OPEN_ITEMS §3 / ONBOARDING "Mediated voices").
4. **Octopus runtime B7 sub-tasks #1 + #4** — Voice Pipeline Step 2 JSON extraction + Substack/print fallback (runtime/OPEN_ITEMS B7).

### Carry-forwards from earlier sessions

5. **Plato thinking-on re-run experiment** ($5, 30 min). See OPEN_ITEMS.md §5.
6. **9480d3a revert hypothesis re-evaluation** — connected to FU#56. See OPEN_ITEMS.md §5.
7. **WBBF program copy coordination** (FU#49C remnant) — verify WBBF materials don't still describe AIssembly with deprecated "breakfast reading" framing.

### "Voice of X" naming convention sweep — deferred until all 10 voices ship

See OPEN_ITEMS §18. Single mechanical sweep of voice_name + council_config + panel_roster after Marley + Whanganui + Scheherazade ship; backfill via SKIP_TO_DERIVE re-fire (~15 min + ~$20 for 10 voices).

---

## What I would do next session in priority order

1. **Check Marley pipeline status** (task `bcroaoa2t`) — if Pass 7a FINAL gate has hit, apply §7 patches discipline.
2. **Promote Marley to athens-2026** + wire council_config when verified.
3. **Operator runs Whanganui + Scheherazade DR sessions** in claude.ai (parallel browser tabs feasible).
4. **Pipeline-fire Whanganui + Scheherazade** as their DR dossiers land. Mediated-voice prompt-fix decision before Scheherazade's Pass 0a fires.
5. **All-10 sweep:** "Voice of X" naming convention rollout (§18) + canonical-docs narrative pass + §3 §9 closure in OPEN_ITEMS.
6. **Octopus runtime B7 #1 + #4** — Voice Pipeline Step 2 JSON extraction + print/Substack fallback render.

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
