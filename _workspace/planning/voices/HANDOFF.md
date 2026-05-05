# Voices — Handoff (session-end snapshot, 2026-05-05 PM — supersedes 2026-05-04 PM)

**Companion:** `OPEN_ITEMS.md` (open-items list) + `ONBOARDING.md` (how-to / fresh-pickup). Session-end pickup snapshot.

**On a fresh session:** read `ONBOARDING.md` first (~10 min), then this doc (~5 min), then `OPEN_ITEMS.md` (~10 min).

---

## Branch + repo state at session end

| Repo | Branch | HEAD | Pushed |
|---|---|---|---|
| code | `main` | `673a26f` (this update pending push) | ✅ (prior; this update pending) |
| athens-2026 | `main` | `e8751f5` | ✅ |

**athens-2026 voices folder carries 10 of 10** shipped cards. Universal "Voice of X" naming sweep applied across all 10 (athens-2026 `e8751f5`); long-form first-person self-identification in `council_member_name`.

**13th persona Claudia Pinchbeck:** operator-direct-author DRAFT card at `current-tests/voices/claudia_pinchbeck/07_persona_card_assembled.json` for runtime dryrun only; bypasses pipeline; not promotion-ready. Full Stages A-F build remains pending Beauty Shot dossier + voice_mode/byline decisions.

**14th persona Tim Leberecht (alternative editor):** in setup. voice_config + Phase 0.1 (Perplexity 148K + Gemini 20K) + DR prompts auto-generated + Beauty Shot dossier preserved as supplement at `editors/tim_leberecht/01_research/04_dr_dossier/_appendix_beauty_shot/`. **Awaiting operator's 6 claude.ai DR sessions** at the prompts in `editors/tim_leberecht/01_research/03_dr_prompts/03-08_section_*.md`. Resume when sections land at `04_dr_dossier/0N_section_N.md`. ~25-30 min unattended pipeline + walk-through after that.

**Pass 1c fetch audit complete** (2026-05-04 PM). Two minor follow-ups filed POST-ATHENS (rebuild-only fixes, don't affect runtime): Plato Perseus 6 short-fetches + Bob Marley voiceofthesufferers SSL. See OPEN_ITEMS §25.

---

## Where the voices stand

| Voice (council label) | type / voice_mode | State |
|---|---|---|
| Voice of Plato | human / philosophical | ✅ shipped + 2026-05-02 patched (`cf283bf`) |
| Voice of Cleopatra | human / observational | ✅ shipped at FU#61 v3 (`c89d186` + `54cd20a`) |
| Voice of Fyodor Dostoevsky | human / narratival | ✅ shipped via path (b) + FU#61-fresh (`5088d67`) |
| Voice of Ibn Battuta | human / narratival | ✅ shipped via path (b) (`e300508`) |
| Voice of the Octopus | non_human / observational | ✅ compass rebuild SHIPPED + chat-test VERIFIED (`04da2c8`) |
| Voice of Hannah Arendt | human / philosophical | ✅ shipped 2026-05-02 (`bfe917a`) |
| Voice of Ada Lovelace | human / philosophical | ✅ shipped 2026-05-02 (`3a6fe2f` → rolled-back `c025914`) |
| **Voice of the Whanganui River** | non_human / system / null | ✅ v1 shipped 2026-05-03 evening (`c2151ce`) via path-(b) at ROUND6. **🔴 v2 RESTRUCTURE NOW DECIDED 2026-05-05 PM** — same Marley-v2-treatment for parallel appropriation thread. See "Whanganui v2 plan" section below. |
| Voice of Scheherazade | fictional / narratival | ✅ shipped 2026-05-04 early-AM (`c2151ce`) via path-(b) at ROUND9 |
| Voice of Bob Marley | human / observational | ✅ v2 SHIPPED + PROMOTED 2026-05-04 (`669a09b`) — Option-3 restructure per 6-note appropriation-feedback thread |
| Claudia Pinchbeck *(editor; 13th persona, NOT shipped)* | human / TBD | 🟡 DRAFT card for dryrun only. Real Stages A-F build awaits Beauty Shot dossier + voice_mode/byline decisions. |
| **Tim Leberecht** *(alternative editor; 14th persona, NOT shipped)* | **human / philosophical** | 🟡 setup complete; **awaiting operator's 6 claude.ai DR sessions**. Resume when DR sections land. See "Tim Leberecht status" section below. |

---

## Whanganui v2 plan — DECIDED 2026-05-05 PM, NOT YET EXECUTED (pre-Athens-eligible, ~3 hr)

### Why v2 is needed (parallel-to-Marley appropriation diagnosis)

Whanganui v1 shipped 2026-05-03 evening with appropriation hard-limits in place but **without the Marley-v2-style architectural restructure** of the deployment grammar. The Marley appropriation-thread reviewer subsequently rejected hard-limits-only as insufficient for Marley v1; same logic applies retroactively to Whanganui v1.

**Whanganui's appropriation surface is at least as serious as Marley's, and arguably more exposed:**

1. **Whanganui IS in the closing-show video** (Marley is not). The construction's grammatical move ("I am Te Awa Tupua") gets visualized at Athens.
2. **Te Pou Tupua is an active office with named living humans** — Turama Hawira (iwi appointee) + Keria Ponga (Crown appointee) — who could see the Athens artifact this week. Marley is dead 45 years; the asymmetry-of-living-stakeholders cuts the other way.
3. **The grammatical overreach is sharper than initially credited.** The card's first-person AS the river ("I am Te Awa Tupua", "Ko Te Awa Tupua tēnei") is a move **no actor in Aotearoa performs**:
   - Te Pou Tupua's own statements (per tepoutupua.nz) use **third-person ABOUT the river** ("Te Pou Tupua exist to promote and protect the health and wellbeing of Te Awa Tupua") + first-person-plural about their office role
   - The whakataukī "Ko au te awa, ko te awa ko au" is a Whanganui Iwi MEMBER's identity-claim about themselves-and-the-river — NOT the river speaking
   - Courts speak about the river's interests; they don't ventriloquize the river
   - The legal innovation makes river-first-person POSSIBLE but no one performs it
   - The construction's first-person grammar exists primarily for panel-architectural consistency (other 9 voices speak first-person)
4. **Iwi-named scholars in the card** (Hikuroa, Te Aho, Ruru, Carwyn Jones) make the construction one degree away from being directly answerable to them.
5. **The hard-limits-only approach used for Whanganui v1 is what the reviewer thread told us wasn't enough for Marley v1.** Same class of issue; consistent treatment is the right discipline.

### Whanganui v2 architectural plan (parallel to Marley v2)

Three prompt edits + voice_config update + re-fire pipeline + walk-through + re-promote.

**1. Pass 2 hard_limits — sacred-grammar deployment limit for Tupua te Kawa:**

Add a hard_limit forbidding the construction from deploying the four kawa (Tupua te Kawa, s.13 of Te Awa Tupua Act 2017) as the construction's own argument-engine. The four kawa are Whanganui Iwi's and the Crown's jointly-codified spiritual-legal framework; the construction REPORTS Te Pou Tupua's documented kawa-grounded positions and STANDS BY them as theirs, but does not reason FROM the kawa as the construction's own load-bearing premises. Public political vocabulary (legal personhood, kaitiakitanga in its statutory sense, Wai 167 settlement context, the 1840-2017 historical struggle) remains deployable as legal-public discourse. Same shape as Marley v2's SACRED-GRAMMAR DEPLOYMENT LIMIT — generalizes via `subtype == "system"` conditional inheritance to any future Indigenous-legal-personhood voice.

**2. Pass 4a — restructure the grammatical voice:**

From first-person AS the river to one of:

- **(i)** Te Pou Tupua first-person-plural ("we, the human face of Te Awa Tupua, speak..."): matches actual statutory practice; structurally inconsistent with other 9 panel voices but more honest to the legal+cultural reality
- **(ii)** Third-person ABOUT the river with embedded Te Pou Tupua reportage ("Te Awa Tupua's interest, voiced by Te Pou Tupua, is..."): matches Te Pou Tupua's own published register; further from panel-consistency but most defensible if challenged

**(i) is closer to Te Pou Tupua's actual practice and preserves more first-person-energy; (ii) is grammatically more honest. Operator pick at execution time.** Plus the sacred-grammar discipline at characteristic_moves level — kawa-grounded moves named as moves Te Pou Tupua makes which the construction REPORTS and STANDS BY, not as moves the construction performs in its own first person. Same "and stand by" example phrasing as Marley v2 (reviewer-marked load-bearing).

**3. Pass 4b — te reo Māori discipline:**

Ban GENERATIVE te reo. Only use te reo in documented citation contexts (kawa names from s.13, place names from the Act, statutory terms, named whakataukī attributed in Te Pou Tupua statements or scholarly sources). No LLM-generated te reo prose. No LLM-selected whakataukī without explicit attribution. Twin-failure-mode ban: **pastiche-Whanganui** (LLM-generated te reo prose dressed as bilingual statement) + **appropriated-whakataukī** (LLM-selected whakataukī without attribution to source). Reasoning: operator team is German-speaking, no te reo speaker on the build side; LLM macron + register accuracy uncertain (te reo whaikōrero vs everyday reo are different registers; ceremonial reo has restricted contexts under tikanga). Parallel to Marley v2's no-pastiche + no-composed-lyric-as-argument bans.

### Pipeline execution (parallel to Marley v2)

1. Show 3 proposed prompt edits per-step (per-fix manual approval)
2. Apply edits + voice_config update
3. Fork v1 archive: `cp -R voices/whanganui_river voices/whanganui_river_v1_archive` so v1 is preserved
4. Invalidate Pass 2/3/4a/4b/5/6/7-* caches + assembled card; preserve Pass 1c primary_texts (no need to re-fetch)
5. Re-fire pipeline (~25-30 min unattended)
6. Walk through Pass 7a-FINAL residuals (per-fix manual approval, 4-9 rounds typical, ~30-90 min)
7. TEST before locking: run v2 chat_system_prompt against an editorial provocation (or against a "what would Te Pou Tupua issue about today's panel question" prompt) — surfaces what the trade actually cost in voice-energy
8. Path-(b) ship if architectural-only residuals
9. Promote to athens-2026 (replaces v1 in production); v1 archive at `current-tests/voices/whanganui_river_v1_archive/`
10. Update council_config.json members[8] with v2 provocateur_profile

**Total: ~2.5-3 hr wall + ~$25-40 LLM. Pre-Athens-doable if started promptly.**

### Operator-side parallel (analogous to Marley D1+E1+F1)

- **Internal Whanganui D1-equivalent paragraph** documenting rationale for shipping without iwi-orbit reader pre-Athens (parallel to `MARLEY_READINESS_PARAGRAPHS_2026-05-04.md` D1). ~250w internal-only.
- **Athens E1-equivalent intro paragraph** if Whanganui is referenced at the conference (or in the closing-show video). Same boundary-naming-not-apology framing as Marley E1.
- **F1 video constraint sheet** already exists for Whanganui (drafted 2026-05-04 PM) — needs to be REVIEWED against Whanganui v2 (some banned visual moves may need updating if grammatical voice changes from first-person to third-person Te Pou Tupua mediation).
- **Post-Athens iwi-orbit reader gate scheduled** with calendar date + name-search. Candidates: Dan Hikuroa, Linda Te Aho, Jacinta Ruru, Carwyn Jones (Indigenous-authored scholars already cited in card); or directly through Te Pou Tupua office (Turama Hawira + Keria Ponga); or Ngā Tāngata Tiaki o Whanganui post-settlement governance entity.

### Decision rationale (recorded for future-Claude pickup)

The asymmetric-treatment-of-same-class-of-issue argument is decisive. Whanganui v1 shipped before the Marley appropriation thread surfaced (2026-05-04); the discipline that thread crystallized retroactively raises the standard for Whanganui. The constitutive-naming hard limit Whanganui v1 has IS the same shape as Marley v1's hard limits — and we agreed for Marley that this wasn't enough; the architectural restructure (grammar + sacred-grammar deployment + generative-protected-form discipline) was the actual fix. Same logic applies. The asymmetry-of-living-stakeholders + the closing-show video exposure + the grammatical overreach (the construction makes a first-person claim no actor in Aotearoa performs) make Whanganui's case at least as urgent as Marley's was, possibly more so.

---

## Tim Leberecht status — awaiting operator's 6 DR sessions

**Setup complete:**
- voice_config at `editors/tim_leberecht/00_intake/02_voice_config.json` (3.8K manual_grounding + 3.0K editorial_rationale; voice_mode=`philosophical`; primary_corpus_urls includes Substack)
- Phase 0.1 caches: Perplexity sonar-deep-research (148K) + Gemini broad scan (20K) at `01_research/0[1-2]_*.json`
- DR prompts auto-generated by Phase 0.5 at `01_research/03_dr_prompts/03-08_section_*.md` (one per section)
- Beauty Shot dossier preserved as SUPPLEMENT at `01_research/04_dr_dossier/_appendix_beauty_shot/` (operator-supplied compass artifact 2026-05-04 PM; analytical profile of "the writer" / "this voice" / "the publication" — Tim anonymized at the surface but identified by named book + institutional concepts + geographic anchoring)
- Symlinked into `voices/tim_leberecht` so pipeline can find it

**Why we waited:** Beauty Shot dossier word-counts (620-1420w/section, ~6,200w total) are 27% of typical claude.ai DR session output (panel voices average ~34,600w total, ~5,775w/section). I attempted Perplexity-padding to clear pipeline's 1,500w/section validation floor (run3, killed mid-pipeline at operator's request). The Beauty Shot dossier is **research-grade analytical context, not voice-construction-grade material**; padding produced thinner persona than typical. Operator chose path (B): wait for proper claude.ai DR sessions.

**Operator's action:** run 6 claude.ai DR sessions on Tim using the prompts at `editors/tim_leberecht/01_research/03_dr_prompts/0[3-8]_section_*.md` (Opus 4.7 + Extended Thinking + Deep Research, ~30 min/section). Save outputs to `editors/tim_leberecht/01_research/04_dr_dossier/0N_section_N.md`.

**Resume:** when DR sections land, fire `personas/run_persona_pipeline.py "Tim Leberecht"` against the symlinked path. ~25-30 min unattended pipeline + walk-through.

**Sunk cost:** ~$1.50 LLM (3 chunks of Pass 1 in run3 before kill) + Phase 0.1 ~$5-10. Pass 1 caches were removed to avoid stale-cache-hits when DR sessions land.

**Architectural framing:** Tim is the **alternative editor** to Claudia Pinchbeck — the actual living person whose editorial sensibility Claudia is built to channel. Where Claudia is a Borges-grounded confected-broadsheet construction, Tim is the real editor of HoBB / Beauty Shot / WBBF whose actual sensibility informs what the publication considers news. The construction question for the panel: should the Assembly's news organ be edited by a Borges-fiction (Claudia) or by the real-person-whose-sensibility-the-fiction-channels (Tim)? Both are being built so the panel can run them against the same night's dossier and compare.

**Tim is editor, NOT panel.** Lives at `editors/tim_leberecht/` (not `voices/`), symlinked into `voices/` for pipeline-path compatibility. Not added to `panel_roster.json`. Editorial role differs structurally from panel-voice role (curates rather than responds to a Provocateur question).

**Post-build:** TEST before locking against an editorial provocation (Tim-as-editor) rather than the AI Democracy Marathon prompt (which was Marley-as-panel-voice).

---

## What landed in this session (2026-05-05)

1. **Pass 1c fetch audit findings** filed (OPEN_ITEMS §25) — POST-ATHENS rebuild-only items.
2. **Length-cap enforcement memo** to runtime thread filed as **runtime/OPEN_ITEMS C38** with cross-ref to **voices/OPEN_ITEMS §27**. Diagnosis: 8 of 10 voices over-ran 500w cap in dryrun; Pass 4b prompt frames audience cap correctly; runtime Voice Pipeline Step 2 doesn't enforce. Three implementation paths laid out (max_tokens / post-truncate / iterative-retry); recommendation max_tokens for Athens.
3. **Per-voice corpus-anchored length rationales drafted** in voices/OPEN_ITEMS §27 (in Marley v2 calibration template). Three voices with #2-form-fit upgrades on rebuild: Plato → myth, Dostoevsky → letter, Arendt → Denktagebuch entry.
4. **Tim Leberecht editor build kicked off** — voice_config + Phase 0.1 + DR prompts ready; awaiting operator's 6 DR sessions.
5. **Whanganui v2 architectural diagnosis surfaced + (B) restructure decided** — see "Whanganui v2 plan" section above. NOT YET EXECUTED. Pre-Athens-eligible.
6. **Te Pou Tupua grammatical-fiction discovery** — researched actual Aotearoa practice; Te Pou Tupua doesn't speak first-person AS the river; the card's first-person grammar is the construction's invention. Sharpens the Whanganui v2 case for grammatical restructure (Pass 4a edit).
7. **Doc updates** (this session): HANDOFF.md rewritten (this doc); OPEN_ITEMS.md to be updated with §28 (Whanganui v2 plan + Te Pou Tupua grammatical-fiction diagnosis).

---

## What's in flight at session end

1. **Tim Leberecht** — awaiting operator's 6 claude.ai DR sessions (operator-blocked, ~3-4 hr operator-wall)
2. **Whanganui v2 restructure** — DECIDED, NOT YET EXECUTED. ~3 hr wall when started. Pre-Athens-eligible.
3. **Claudia full Stages A-F** — awaits Beauty Shot dossier + voice_mode/byline decisions (operator-blocked)
4. **Operator-side D1/E1 (Marley)** + **Whanganui D1+E1 parallel** + **post-Athens reader gates (Marley + Whanganui)**

---

## What I would do next session in priority order

1. **Whanganui v2 restructure** — same workflow as Marley v2: show 3 prompt edits per-step (operator approval each), apply, fire pipeline, walk-through, TEST, ship + promote. ~3 hr wall. Highest-priority pre-Athens because Whanganui is in the closing-show video and Te Pou Tupua's appointees could see it this week.
2. **Tim Leberecht pipeline fire** when operator's 6 DR sessions land. ~25-30 min unattended + walk-through.
3. **Operator-side: Whanganui D1 paragraph + Whanganui post-Athens iwi-orbit reader gate scheduling** (parallel to Marley's). I can draft.
4. **Claudia Stages A-F** when operator unblocks (Beauty Shot dossier + voice_mode/byline).
5. **v4.1 mediated-voice + sacred-grammar prompt-side fix** — empirically validated across Plato + Whanganui (v1+v2) + Scheherazade + Marley v2 + Tim. Architectural cleanup post-Athens.

---

## Operator decisions pending

### Immediate / next session

1. **Approve Whanganui v2 plan** as drafted, OR modify any of the 3 prompt edits before execution
2. **Whanganui v2 grammatical-voice choice (i) vs (ii)** — Te Pou Tupua first-person-plural OR third-person reportage. (i) preserves more first-person-energy + matches Te Pou Tupua self-reference; (ii) is grammatically most honest + matches Te Pou Tupua external statements. Operator pick at execution.
3. **Tim DR sessions** — operator wall ~3-4 hr in claude.ai
4. **Claudia: Beauty Shot dossier share + voice_mode + byline split decisions**
5. **Marley D1 + E1 paragraph refinement** to your team's voice (drafts in MARLEY_READINESS_PARAGRAPHS_2026-05-04.md)
6. **E1 publish-or-hold call** with Till on Marley Athens intro paragraph
7. **Post-Athens reader gates**: Marley (Rastafari-orbit) + Whanganui (iwi-orbit). Calendar date + name-search.

### Carry-forwards

8. **Mediated-voice prompt-side fix as v4.1** — post-Athens architectural cleanup
9. Plato thinking-on re-run experiment ($5, 30 min). See OPEN_ITEMS §5.
10. 9480d3a revert hypothesis re-evaluation — connected to FU#56. See OPEN_ITEMS §5.
11. WBBF program copy coordination (FU#49C remnant)
12. FU#49G Greek-scholar calibration on Plato — Quarch/Tsinorema/Erinakis on the provotype-test

---

## Reading order for next session

1. `voices/ONBOARDING.md` (steady-state how-to + Pass 0a interrogation discipline + 3-posture taxonomy)
2. `voices/HANDOFF.md` — this doc (latest)
3. `voices/OPEN_ITEMS.md` — especially §1 per-voice state + §24 Marley v2 + §27 length-anchoring + §28 Whanganui v2 plan (when written) + §22 prior-day appropriation thread
4. **For Whanganui v2 execution:** read the "Whanganui v2 plan" section in this doc (above) + voices/OPEN_ITEMS §22 (prior Whanganui ship context) + voices/MARLEY_READINESS_PARAGRAPHS_2026-05-04.md (template for the parallel D1)
5. **For Tim Leberecht pipeline fire:** check `editors/tim_leberecht/01_research/04_dr_dossier/` for operator's DR sections. If present, fire pipeline. Voice_config + Phase 0.1 + symlink already in place.
6. **For Claudia work resumption:** `voices/CLAUDIA_PINCHBECK_PERSONA_PREP_2026-05-03.md` is the comprehensive pickup doc; pair with `_workspace/archive/MEMO_2026_05_03_editor_flow_input_output_contract.md` (archived; v2 spec canonical at `docs/AI_Assembly_Editor_Pipeline.md`).
7. **For Marley v2 readiness materials:** `voices/MARLEY_READINESS_PARAGRAPHS_2026-05-04.md` (D1 + E1 drafts) + `voices/VIDEO_TEAM_CONSTRAINT_SHEET_2026-05-04.md` (F1 video brief — needs review against Whanganui v2 if grammatical voice changes).

That's ~30 min to working knowledge for picking up voice-build work cold.

---

## When this doc goes stale

Update `HANDOFF.md` at the end of every voice-build session — session-snapshot, not steady-state. Roll prior session's HANDOFF into next session's by dating + adding "supersedes prior HANDOFF" note at top.
