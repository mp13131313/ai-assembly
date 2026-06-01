# Voices — Open Items (authoritative, 2026-05-06)

**Scope:** EVERYTHING still open or undecided that pertains to the **persona pipeline / voice cards** for athens-2026. Distinct from the Voice Pipeline runtime (Steps 1+2+3) which has its own tracking.

**Date stamp:** 2026-05-06. Supersedes 2026-05-03 / 2026-05-04 / 2026-05-05 PM / 2026-05-05 evening versions.

Closed this session-cluster (2026-05-05 evening + 2026-05-06):
- §27 length-cap card surgery (Dosto/Arendt 350-750w + Octopus 350-500w prose-channel front-loaded)
- §28 Whanganui v2 architectural restructure SHIPPED + ATHENS-CLEAN (witness-translator stance + 4-field gap-E closure + kawa-speaker-frame closure)
- §29 Tim Leberecht 13th persona SHIPPED as Assembly editor (replacing Claudia DRAFT)
- §30 assembly-fiction reframe SHIPPED across all 10 voices
- §31 gap A + B + F ✅ FIXED for Whanganui v2; gap C lesson captured; gaps D + E + G filed for v4.1 (post-Athens)
- **anchored_override cleanup**: nulled across all 8 voices that had it populated (Whanganui + Octopus already null); dead config at Athens runtime per `runtime/flows/voice/card_assembly.py` — Voice Pipeline uses `default` only. athens-2026 `2168519`. Reversible via git history.
- **Runtime-thread cleanup `8a685e3`**: removed May-4 continuity_night_2 dryrun artifacts + stale council_config backup + extended .gitignore. The runtime-thread WIP flagged across many sessions is now gone.

Several historical/done planning docs archived to `_workspace/archive/session-artifacts/` 2026-05-06: `WHANGANUI_V2_PLAN_2026-05-05.md`, `WHANGANUI_V2_ROUND0_WALKTHROUGH_2026-05-05.md`, `MEMO_2026_05_05_voice_temporal_stance_assembly_fiction.md`, `MEMO_2026_05_05_length_cap_card_surgery_after_runtime_fix.md`, `MEMO_2026_05_01_recurrence_patterns_from_legitimacy_test.md`, `CLAUDIA_PINCHBECK_PERSONA_PREP_2026-05-03.md` — content migrated into authoritative OPEN_ITEMS sections.

**Truth source:** When this doc disagrees with another, this doc is right (or fix this doc).

---

## 1. Per-voice build state

Panel is **10 voices** (per `athens-2026/panel_roster.json`). **10 of 10 SHIPPED + PROMOTED to athens-2026.** "Voice of X" naming sweep applied across all 10 (athens-2026 `f7e86a7`). **Plus Tim Leberecht as 13th persona (Assembly editor)** SHIPPED 2026-05-05 evening at `athens-2026/editor/tim_leberecht/` (`9347743`); `EDITOR_CARD_SUBPATH` runtime rename `claudia_pinchbeck` → `tim_leberecht` (`b266f51`); 31/31 runtime tests pass. Claudia Pinchbeck DRAFT card at `current-tests/voices/claudia_pinchbeck/` is DEPRECATED (was operator-direct-author placeholder for runtime dryrun; superseded by Tim ship). **Pre-Athens voice-build work is COMPLETE.**

**Architectural updates this session (2026-05-05 evening):**
- All 10 voice_temporal_stance.default fields shifted to **assembly-fiction** ("voice present at the assembly that gathers in Athens, observes panels, responds when consulted") per `MEMO_2026_05_05_voice_temporal_stance_assembly_fiction.md` — see §30
- 3 voices length_and_format_constraints surgical patch: Dostoevsky 350-750w, Hannah Arendt 350-750w (operator-bumped from initial 500w drafts), Octopus 350-500w prose-channel front-loaded — see §27 (CLOSED)
- Whanganui River v2 architectural restructure (witness-translator stance via new `mediation_stance == "transmission_witness"` Jinja conditional across Pass 2 + 3 + 4a + 4b + 5 + 6) SHIPPED + PROMOTED + ATHENS-CLEAN (gap-E 4-field closure with TEST verification) — see §28

| Voice (council label) | type | voice_mode | Hostile? | State | Notes |
|---|---|---|---|---|---|
| Voice of Plato | human | philosophical | false | ✅ shipped + 2026-05-02 patched | Surgical patches landed (`389a08c`): banned_modes[10] sharpened (Socrates-death anachronism) + 7 dramatist-vs-speaker patches. §9 closed via §16.5; runtime-side tics owned by runtime/OPEN_ITEMS C20. |
| Voice of Cleopatra | human | observational | **true** | ✅ shipped | FU#61 v3 prompt-driven re-emission landed (`8a16bf7`+`0913373`). |
| Voice of Fyodor Dostoevsky | human | narratival | false | ✅ shipped | Round 1 + 2 patches → path (b) → fresh quality_criteria patched-in (`b0f0b45`). |
| Voice of Ibn Battuta | human | narratival | false | ✅ shipped | Round 1 + 2 patches → path (b). |
| Voice of the Octopus | non_human | observational | false | ✅ **compass-rebuild shipped 2026-05-02** (`1d8605f`); 4 rounds + 16 patches; chat-test verified two-channel JSON+prose emission contract. Runtime asset bundle at `code/docs/runtime_assets/octopus_chromatophore/`. See §15 below. |
| Voice of Hannah Arendt | human | philosophical | false | ✅ **shipped 2026-05-02** (`32900be`) — 3 validation rounds + 6 surgical patches. Post-1975 topics flagged as analogical extensions. |
| Voice of Ada Lovelace | human | philosophical | false | ✅ **shipped 2026-05-02** (`e74c391`) — 5 rounds + 21 patches; **4 over-patches subsequently rolled back** to validator-faithful minimum (`c855478`) after operator caught §7-convention deviation. Note G/Note A held-not-resolved as constitutional tension. |
| Voice of the Whanganui River | non_human | system / null + **mediation_stance: transmission_witness** | false | ✅ **v2 SHIPPED + PROMOTED + ATHENS-CLEAN 2026-05-05 evening** (`c2a885b` + `3ccb1f9`) — witness-translator architectural restructure. Replaces v1 (`c521e74`, 2026-05-03 evening). Pipeline ROUND 0 → ROUND 1: 12 → 4 issues; first-person-AS-river leakage 5 → 0; voice_intellect_coherence ISSUE → PASS. Surgical reasoning_method patch + 3 naming patches + path-(b) ship (`c2a885b`). Post-ship full-card scan surfaced 4 additional gap-E fields with v1 first-person AS the river (character / knowledge_boundary / world.ontological_furniture / formative_experience.formative_emotional_community); patched + re-Derive + TEST passed (`3ccb1f9`). voice_temporal_stance dual-purpose edit: assembly-fiction + witness-stance correction (`3bcbef5`). v1 archived at `current-tests/voices/whanganui_river_v1_archive_2026-05-05/`. See §28 below. |
| Voice of Scheherazade | fictional | narratival | false | ✅ **shipped 2026-05-04 early-AM** (`c521e74`) — path-(b) at ROUND9; 9 validator walk-throughs converged 9→6 (1 false-positive + 4 §9-architectural re-flags + 1 architectural carry). Seale-Horta 2021 corpus (operator-acquired Thalia DRM-free EPUB) curated to 14 chapters / 1.22M chars. Mediated-voice / dramatist-vs-speaker pattern preserved per §9 architectural precedent. ROUND7-9 snapshots preserved. See §22 below. |
| Voice of Bob Marley | human | observational | false | ✅ **v2 SHIPPED + PROMOTED 2026-05-04 afternoon** (athens-2026 `da7a5c4`) — Option-3 restructure per 6-note appropriation-feedback thread. **3 architectural prompt-edits landed (Pass 2 + Pass 4a + Pass 4b) generalizing to any future musical-corpus voice with living sacred grammar via `corpus_constraint == "lyrics_patterns_only"` conditional.** Pipeline ran fresh; 4 ROUND walk-throughs converged 7→6→3 architectural residuals; path-(b) ship; AI Democracy Marathon test ran on v2 chat_system_prompt — trade landed as reviewer predicted (voice loses Daniel 3 + Omeriah + bias-IS-machine analytical formula; preserves prose-yard-reasoning + instrumental riddim-call + public political vocabulary + Trench Town concrete + knowledge boundary + Garvey citation). v1 archive at `current-tests/voices/bob_marley_v1_archive/`. See §24 below. |

### Voice-mode coverage (10 shipped)

- philosophical: 3 (Voice of Plato, Voice of Hannah Arendt, Voice of Ada Lovelace)
- narratival: 3 (Voice of Fyodor Dostoevsky, Voice of Ibn Battuta, Voice of Scheherazade)
- observational: 3 (Voice of Cleopatra, Voice of the Octopus, Voice of Bob Marley)
- system / null: 1 (Voice of the Whanganui River)

10/10 with all four modes represented.

---

## 2. Octopus — ✅ SHIPPED via Path A (2026-05-01)

Pass 7a FINAL round 1 flagged **layer instability**: card alternated between (a) Pass 2's translation-honest no-reader frame and (b) Pass 4b's scholar-dispatcher-with-citations frame. Path A surgical 6-patch landed; round 2 dropped to 1 false-positive (`council_member_name` validator hallucination); path (b) accepted, Derive ran clean.

**6 patches applied (athens-2026 `7bce047`):**
1. `translation_protocol` Step 5 — strip scholar-name list, keep contested-state-naming pattern + "we still don't know"
2. `character` — replace non-allowlisted editorial bracket with allowlisted `[experiential_reconstruction]` Boddice tag
3. `medium` — citations become optional evidence mode; default emission stays operational
4. `length_and_format_constraints` — drop blanket 'I'/'you' bans; replace with verb-discipline (registers/orients/extends — operational; not feels/wants/decides — mentalistic)
5. `characteristic_output_structure` — strip outside-observer staging
6. `metaphorical_repertoire.hold-the-gap` — replace third-person "The voice's epistemic figure" with second-person imperative

Round 2 check statuses: 5/6 PASS (anachronism, constitutional_consistency, voice_intellect_coherence, distinctiveness, register); only `completeness` ISSUE on the false-positive `council_member_name`.

**Lessons:**
- Path A worked architecturally. Substrate preserved (philosophy lives in `concept_lexicon` / `constitution` / `reasoning_method` / `topics_requiring_care` / `hard_limits` / Step 5 contested-state pattern); emission becomes translation-honest.
- "Philosophy as grammar of emission, not content cited in emission" framing applies to all non-human / non-philosophical voices going forward (Whanganui especially).
- Layer-instability is detectable post-Derive via Pass 7a FINAL — same gate that caught Plato/Cleopatra/Dosto/Battuta residuals. Validator gives precise field-level prescriptions for non-human voices.

Backup snapshot at `voices/octopus/07_persona_card_assembled.pre_path_a_patches.json` (gitignored, local-only).

---

## 3. Three remaining voices — operator-bounded work

Build sequence per voice:

```
1. Pass 0a (~1 min)             — voice_config + review_doc
   → operator confirms voice_mode, hostile_sources, type/subtype
   → if shortening name (e.g. "Fyodor Dostoevsky" → "Dostoevsky"), rename folder + voice_config.name
   → editorial_rationale stays null per current operator pattern
2. Phase 0.5 (~6 min)            — Perplexity + Gemini + 6 tailored DR prompts
3. Manual DR sessions (~3-4 hr)  — 6 × claude.ai with Extended Thinking + Deep Research
   → operator pattern: 4.7 across §1-§6 (NOT the older "4.6 for §1-§5; 4.7 for §6" — that's stale spec)
   → save each as voices/<slug>/01_research/04_dr_dossier/0N_section_N.md
4. Persona pipeline (~30-90 min) — chunked merge → Pass 1c review gate → Pass 2-7 → 7a FINAL gate → operator decision (a/b) → Derive
```

**Per-voice flags worth checking:**

| Voice | Status / pre-build attention |
|---|---|
| Bob Marley | **SONG-REBUILD KICKED OFF 2026-05-03** (see §1 row + §20 below). Prior pipeline snapshotted to `bob_marley_pre_song_rebuild_2026-05-03/`. Fresh Pass 0a + new voice_config (song-as-artifact mandate) + Phase 0.5 done. **Awaiting operator's 6 claude.ai DR sessions** (~3hr wall). After DR: re-fire pipeline + re-inject 35 lyrics at Pass 1c gate + §7 convention at gate. Special `corpus_constraint: lyrics_patterns_only` (atypical). FU#47 voice-fit: ⚠ awkward (lyric-rhythmic). Card-side FU#61 audience-engagement will land in Patois/lyric grammar. |
| Whanganui River | **Hardest case** — non-human + no first-person source + legal-personhood-as-frame. Construction-mode question is real (translate-into-human-categories vs preserve-river-grammar). May trigger same layer-instability as Octopus. voice_config rewritten transmission-faithful (Tupua te Kawa verbatim + Te Pou Tupua mediation); Phase 0.5 DR prompts ready. **voice_mode `null` is valid** (subtype=system). FU#47 voice-fit: ⚠ awkward. Plan to budget extra patch rounds. See §17. |
| Scheherazade | **Mediated-voice prompt fix** — verify status before pipeline fires. Flagged in earlier session; never resolved. Concerns how the frame-tale form (story-within-stories) gets handled in `voice_mode: narratival`. **Same dramatist-vs-speaker collision risk as Plato** (composer vs speakers within compositions). Either land the prompt-side mediated-voice clarification before her pipeline fires, OR plan for surgical patches at the gate. FU#47 voice-fit: ⚠ awkward. FU#46 may apply (rich primary-text corpus → 60K excerpt budget). |

---

## 4. Voice-relevant FUs still open (consolidated from FOLLOW_UPS.md)

### Active / conditional

**FU#55 — Form-variance test, rolling per-voice (Pass 4b fork-test pattern)** 🟡 IN PROGRESS
- 7 of 10 voices shipped (Plato/Cleo/Dosto/Battuta/Octopus/Hannah/Ada). Plato + Cleopatra explicitly populated (both declined permission); other shipped voices haven't been individually fork-tested.
- 3 voices remaining (Marley in flight, Whanganui + Scheherazade pending DR)
- Resolution criteria: 0/10 → close §H aspirational; 1-2/10 → opt-in flag; 3+/10 → re-evaluate landing
- Continues per-voice as cards ship

**FU#56 — Pass 2/3/4a register-discipline gap on long-form fields** 🔵 DEFERRED
- Empirically attested on Plato + Cleopatra (long-form field biographical/glossary register)
- Operator-flag exit working
- Architecturally-correct fix is prompt-side but carries 3feb2b2-revert risk
- Now re-evaluable under thinking-visible (FU#60) conditions
- Decision pending: re-attempt single component on Plato Pass 4b under thinking-on, OR continue accepting via flag

**FU#39 — Character-distribution stage-quoting** 🔵 CONDITIONAL
- Applies to distributed voices: Plato, Scheherazade, Dostoevsky, Battuta
- Conditional on narrator-unification signal
- Plato shipped without it; Dostoevsky shipped without it; Battuta shipped without it
- Probably can be closed unless Scheherazade triggers on her build

### Recently closed but documented

- ✅ **FU#60** — adaptive thinking observability + temperature compatibility (committed `c3d369d` + `4d0153b` + `4eaaa10`)
- ✅ **FU#61** — voice-side Layer-1 audience-engagement criterion via Pass 4b prompt (committed `6a610fc` + Cleopatra `8a16bf7`/`0913373` + Dostoevsky `b0f0b45`)
- ✅ FU#52 chat_system_prompt invalidation
- ✅ FU#53 Pass 7a FINAL review-gate
- ✅ FU#57 bold_engagement_topics dropped from runtime
- ✅ FU#58 Pass 7a prompt sensitive_topics drift
- ✅ FU#59 Pass 7c × Pass 7a register-rule conflict

### Post-Athens (not blocking)

- FU#54 — Smoke test runtime-fidelity refactor (Pass 7b)
- FU#49M — `strain_markers[]` runtime contract
- FU#31, FU#37 — voice-tissue validators (backstops; only re-activate on regression)

---

## 5. Architectural / experimental questions still open

### Plato thinking-on re-run experiment
- Discussed early in session; never fired
- Cost: ~$5, ~30 min
- Goal: empirical measurement of thinking-engagement rate per pass under FU#60-instrumented wrapper
- If data shows thinking is firing reliably → wrapper changes alone are enough
- If data shows under-engagement → consider explicit `output_config: {effort: high}` per pass

### 3feb2b2 revert hypothesis re-evaluation
- Connected to FU#56 + thinking-visible empirical question
- Texture loss in earlier prompt cycle attributed to "cumulative prompt additions" — may have been "cumulative directives without thinking bandwidth"
- Resolvable by single Plato Pass 4b re-run with thinking-on AND with `effort: high` explicit
- Architectural decision FU#56 + future prompt expansions hinge on outcome

### FU#61 prompt — empirical pattern question
- Successfully landed; produces audience-engagement criterion across all 4 shipped voices
- BUT model integrates the +1 (5 reshape) rather than appending (6 total) on most voices
- Cleopatra appended 6 in fresh-test re-emission; Plato/Dosto/Battuta integrated to 5
- Variance is per-emission, not voice-stable
- Open: should the prompt's "Additionally, 1 further criterion" instruction be sharpened to enforce literal +1, OR is integration-into-5 actually the better behaviour?
- **Empirical evidence so far:** Cleopatra's two integration runs produced strong but DIFFERENT criteria sets (6 in test vs 5 in shipped); the 5-integrate version was deemed superior by the other thread. So integration probably correct. No prompt change recommended.

---

## 6. Cleanup / hygiene gaps — RETIRED 2026-05-02

All 2026-05-01 cleanup items swept. Verified state:
- **athens-2026 git tracking:** Plato 245 / Cleopatra 116 / Dostoevsky 80 / Battuta 80 / Octopus 80 tracked, 0 untracked across all 5 voices. (The 80-vs-245 delta is `.gitignore` correctly catching `_pipeline_logs/` + `*.pre_*.json`.)
- **athens-2026 `.gitignore`:** all four targets (`_pipeline_logs/`, `*.pre_*.json`, `*.pre_*.md`, `_operator_review_passed.flag`) present.
- **/tmp/ cleanup:** `standalone_pass4b_test.py` promoted to `code/personas/scripts/`; transient pass4b/anthropic_thinking artifacts gone.
- **LLM_CALL_INVENTORY.md:** refreshed `2f82a2e` 2026-05-01 (FU#53 + Pass 4b standalone test).
- **"Phase L" sweep:** active docs cleared 2026-05-02. Archived HANDOFFs (`_workspace/archive/voices_consolidation_2026_05_01/`) intentionally retain historical references.
- **Octopus athens-2026 `07_section_5_dr_prompt.compass.md` stray** (mid-rewrite artifact pre-rebuild decision): deleted 2026-05-02. Canonical rebuild DR prompts live in `projects/current-tests/voices/octopus/01_research/03_dr_prompts/`.

Section retained as audit trail; no active items.

---

## 7. Card-level invariants we've established empirically

### What's known to work

- **FU#49A v2 quality_criteria scaffold** — 3-5 + 1 outcome question pattern. "Could this be mine?" for fidelity; "Could this on its own make an audience engage with its intent?" for reception. Field-name references not strictly required (substance grounding is enough).
- **FU#53 review-gate** — Pass 7a FINAL post-assembly + operator gate. Caught real issues across 4 voices. Use path (a) re-validate for first round of patches; path (b) accept-residuals via flag for later rounds (the validator treadmill never reaches zero).
- **FU#52 chat_system_prompt regen** — runs unconditionally at end of pipeline; assembled-card patches propagate to chat artifact correctly.
- **FU#60 thinking-on adaptive + display:summarized + drop temperature** — all in place. `thinking_trace` + `block_types` captured in clients.py. Streaming-stability retry catches httpx.RemoteProtocolError (commit `eda57f8`).

### Known false positives (skip on every voice)

- **`council_member_name` "missing"** — recurring validator hallucination on every voice. Field is unambiguously present in every shipped card. Skip on every round.

### Known acceptable residuals

- **`quality_criteria` evaluator-question form** — flagged on Dostoevsky round 2 as "evaluator-facing QA prose." Plato shipped with same form and chat-tested fine. Register-strict critique, NOT runtime-blocking.
- **Long-form-field biographical/glossary register** (FU#56 territory) — recurring across voices. Operator-flag-exit working. Do not patch individual cards beyond cleanly-actionable issues.

### Operator-applied patches that recur across voices

- **Modern-named-comparators in `hard_limits`** (e.g., William-Lane-Craig, Instagram-Dostoevsky, Freudian, Aegean Intelligence) → strip; replace with period-neutral alternatives
- **Internal-production leakage in `banned_modes`** (e.g., "Aegean Intelligence response", "democracy response", "Lab draws...") → strip; keep substantive prohibition
- **Post-voice-lifetime vocabulary in `constitution` / `concept_lexicon`** (Nietzschean for Dostoevsky; modern analytic for Battuta) → replace with period-native alternatives the voice would actually use
- **Third-person register breaks in operational_notes** (e.g., "The voice itself is the contradiction") → rewrite first-person ("I am the contradiction")
- **Theatrical exit lines in `disagreement_protocol`** (e.g., "The chair is empty before your reply is finished") → drop
- **Modern-polemical-flourish slogans in `bold_engagement_topics`** (e.g., "wonder-cabinet calling itself a court", "fitna in a clean shirt") → restate in voice-native terms

### Validator-treadmill expectation

- Round 1 patches: ~3-7 cleanly-actionable issues
- Round 2 patches: validator finds *different* set of issues (~3-5 more)
- Round 3 would find different again (treadmill never zeros)
- Convention: patch round 1 cleanly-actionable + round 2 cleanly-actionable, then path (b) accept-residuals via flag
- This is the Plato + Cleopatra + Dostoevsky + Battuta pattern. Match it for upcoming voices.

### voice_mode `null` validation rule

`null` is only valid for `subtype: system`. `node0_validation.py:60` enforces strict 3-enum {philosophical, observational, narratival}. Voices with `null` voice_mode get rejected at Phase 0.5 launch.

**Empirically attested (2026-04-27 session):** Cleopatra and Bob Marley had `voice_mode: null` proposed by Pass 0a originally and were REJECTED at Phase 0.5 launch — had to be fixed before research could proceed. **Whanganui River (`subtype: system`) is the only voice for whom `null` is allowed.**

### FU#48 lesson — pipeline-canonical vs operator-hand-curated

When external reviewers flag *"voice X's card has feature Y that voice Z's lacks,"* verify whether Y is **canonical pipeline output** vs **operator-hand-curated artifact** before assuming Y is missing from the pipeline. Especially for chat artifacts (which are derivations from cards via FU#41 strip) and operator-personally-tested chat v2 cards (which carry empirical patches the pipeline-emitted version may have differently).

This caught FU#48 (operator pushback) — three apparent gaps were already addressed by existing pipeline; the reviewer had compared a pipeline-emitted Plato card to an operator-hand-curated Dostoevsky chat v2.

### 3feb2b2-revert and 418d553 baseline (prompt history)

- **418d553 baseline** = the verified-good Pass 2/3/4a/4b/5 prompt state predating the texture-degrading FU#49 cumulative additions. This is the prompt state Plato 2026-04-25 shipped under (chat-tested OK).
- **3feb2b2 revert** (2026-04-28) = full revert of FU#49H/I/J/K/L/D back to 418d553. After empirical chat-test signal showed cumulative additions had degraded artifact texture relative to 04-25 shipped baseline.
- Currently landed on top of revert: **FU#49A v2** (commit bfb7ed3; quality_criteria 3-dim field-tied scaffold), **FU#49D re-applied** (Position B Hard_limits with hedge discipline), **FU#51** (Pass 7a routing guard), **FU#44+** (5 patcher patterns), **FU#52** (chat artifact invalidation), **FU#53** (review-gate + Pass 7a FINAL), **FU#57** (bold_engagement_topics drop from runtime), **FU#58/59** (Pass 7a/7c register-rule fixes), **FU#60** (thinking observability + temperature compatibility), **FU#61** (audience-engagement +1 in Pass 4b prompt).
- **Stripped/reverted (NOT in current prompts):** FU#49H#1-4, FU#49I, FU#49J (5+2 quality_criteria; reverted to FU#49A's at-least-one form), FU#49K, FU#49L, plus the 04-28 cryofreeze framing in voice_temporal_stance was REPLACED with the simpler "voice arrives at Athens with full canonical experience" framing.
- The cryofreeze + tense-discipline OUTPUT REGISTER blocks + family-of-forms + anti-generic-register were initially landed (`6828911`) but the cryofreeze + family-of-forms components were subsequently reverted at the 04-28→04-29 transition. Card v2.1 §H + §J spec text retains the family-of-forms aspiration, but Pass 4b prompt currently single-form-locked until Cleopatra empirical validation.

### Position B vs Position C distinction (FU#49D)

**Position B = corpus-accurate softening** (permit corpus-internal self-criticism). Voice can cross-examine its own framework using moves AVAILABLE within the corpus.

**Position C = framework-lifting** (permit denying core commitments). Voice abandons its framework entirely.

**The Athens panel format is Position B only.** Voices speak FROM their frameworks, not against them. FU#49D's universal pattern in Pass 2 hard_limits: *forbid framework-ABANDONMENT, NOT corpus-internal CROSS-EXAMINATION*. The abandonment-vs-cross-examination test is what each `hard_limits` entry must pass.

### Pipeline-fidelity audit method (when voice_config changes mid-build)

If voice_config is edited AFTER Phase 0.5 has run:

| Field changed | Re-run scope |
|---|---|
| `type` / `subtype` / `hostile_sources` | Full Phase 0.5 re-run (these affect Pass 1a/1b template selection) |
| `voice_mode` / `corpus_constraint` | Pass 0b tailor-only re-run (affects only DR-prompt customization) |
| Other fields (`name`, `manual_grounding`, `editorial_rationale`, `wikipedia_url`) | No re-run needed |

**Operationally important** when correcting Pass 0a proposals before pipeline launch.

---

## 8. Empirical findings worth preserving

### From FU#61 fresh-test pass (2026-05-01)
Standalone Pass 4b re-emit on all 4 shipped voices showed:
- All 4 emit a recognizable audience-engagement criterion under FU#61 prompt
- Criterion form is voice-shaped per emission; non-deterministic between runs
- Plato shipped + fresh both have the criterion; original-shipped is the FU#61 inspiration line
- Cleopatra shipped (FU#61 v3) is voice-stronger than fresh-test variant
- Dostoevsky fresh is unambiguously stronger than original-shipped (ventriloquized-as-the-gentleman engagement test) — landed via patch `b0f0b45`
- Battuta shipped is voice-stronger than fresh-test variant (qāḍī self-instruction imperative form)
- **Lesson:** the prompt change works architecturally; per-voice emission variance is real; don't blanket re-emit, evaluate per voice

### From this session's diagnosis work
- Pass 4b emits all 8 fields in one call — there's no per-field invocation
- Pass 4b inputs: `pass_2_3_4a_summary` (CT compress) + `rhetorical_mode`/`characteristic_moves`/`register_and_tone` from Pass 4a + name/type
- CT compress writes a separate file — does NOT modify Pass 4b output
- Killing pipeline mid-cascade after Pass 4b output written is safe (downstream files are cache-hits unless invalidated)
- Standalone Pass 4b test script is at `/tmp/standalone_pass4b_test.py` — pattern preserved if useful

### From Octopus diagnostic
- Pass 4a is the heaviest streaming call in the pipeline (107K corpus excerpts for Octopus, 70K for Dosto)
- httpx.RemoteProtocolError can hit during streaming on large outputs
- 1-retry with 15s backoff (commit `eda57f8`) is sufficient; first retry usually succeeds

---

## 9. Plato dramatist-vs-speaker collision — ✅ RESOLVED 2026-05-02 (`389a08c`)

**Status:** ✅ RESOLVED via §16.5 Path A comprehensive (athens-2026 `389a08c`). 7 surgical patches landed: characteristic_moves[9].description + metaphorical_repertoire["midwifery and birth"] (Phaenarete-as-Socrates'-mother corrected) + 5 passage headers ([2] Republic V, [3] Republic X, [4] Phaedrus, [6] Apology, [7] Theaetetus) switched from first-person Plato-as-Socrates to third-person Socrates / composer-frame. 3 borderline headers ([0], [1], [5]) left alone. The drafted prompt-side architectural fix (HANDOFF_2026_04_28 §13) is **still pending for Scheherazade's Pass 0a** — see §3 Scheherazade row.

**Section retained for historical context** (the `Status` line above is the live truth):

**The mediated-voice problem:** Plato writes THROUGH Socrates / Athenian Stranger / Timaeus / Diotima. The cryofreeze + tense-discipline + family-of-forms framing pushed the LLM to render first-person as concrete biographical action — which collapsed Plato into Socrates in 3 places.

**3 instances on disk (verified 2026-05-01):**

1. `characteristic_moves[9].description` — *"I am the son of Phaenarete the midwife and I attend the labour of your thinking..."* — Phaenarete is **Socrates'** mother (Theaetetus 149a); Plato's mother is Perictione.
2. `metaphorical_repertoire.midwifery and birth` — *"Son of Phaenarete the midwife, attending the labour of others' thoughts..."* — same biographical collapse.
3. `curated_corpus_passages.passages[7].header` — *"I told young Theaetetus what I had inherited from my mother Phaenarete — that my art is midwifery, practised on souls."* — Plato as voice claims Socrates' utterance and biography.

**Patch text drafted (HANDOFF_2026_04_28 §13, never applied):**
> *"Through Socrates — who claims his mother Phaenarete was a midwife, and his own art a midwife's art for souls — I deploy the midwife image: he attends the labour of others' thoughts, brings forth nothing himself, tests what is born to tell the phantom from the living offspring. The image is mine to use through him; the biography belongs to Socrates."*

**Plus the architectural fix (also drafted, never landed):** prompt-side mediated-voice clarification (Pass 2 epistemic_frame_statement / Pass 4a characteristic_moves + metaphorical_repertoire / Pass 3 reasoning_method). Pattern: voice's authorial first-person at the conference is the COMPOSER's, not the speakers within voice's compositions. Universal-pattern with voice-specific worked examples for Plato + Scheherazade (FU#40 design pattern). Non-mediated voices unaffected.

**Current state:** Plato shipped + chat-tested OK in operator's empirical view → not runtime-blocking. But the collision IS structurally on the card, will appear at runtime when context elicits midwifery/Socrates moves, and will need fixing before Scheherazade builds (her frame-tale form has the same mediated-voice issue).

**Recommendation:** apply the 3 surgical patches to Plato's card; land the prompt-side mediated-voice clarification before Scheherazade's Pass 0a fires. ~30 min total.

---

## 10. Architectural redesigns deferred post-Athens

These touch the persona-build architecture but are scoped post-Athens to avoid regenerating cards mid-prep.

**FU#42 — Split-card architecture (voice-card / deployment-card)**
- Card has 32 voice-stable fields (constitutional, swappable per deployment) + 8 deployment-specific fields (Athens-specific length, audience-aware engagement) + 2 hybrid (topics_requiring_care, disagreement_protocol).
- Operational benefit: deployment-swap costs ~5-8× less ($30 / 1h instead of $240 / 24h for 12-voice panel redeploy) AND voice-card stays byte-identical across deployments.
- Effort: ~1-2 weeks. Trigger post-Athens.

**FU#50(1) — Pydantic schema enforcement at Pass 2/4a/4b/5/6 outputs**
- Voices producing inconsistent shapes — `banned_language` as list-of-strings (Plato FU#49H regen) vs list-of-dicts (Plato pre-FU#49H card per FU#32 STRIP+USE pair format); `hard_limits` as list-of-strings vs list-of-dict-with-rule-key; both shapes valid per prompts but downstream consumers may assume one.
- Effort: ~4-6 hr. Trigger post-Athens (regenerating cards mid-prep risky).

**FU#54 — Smoke test runtime-fidelity refactor (Pass 7b)**
- Pass 7b currently puts card-as-JSON-blob in user prompt + asks for 3-5 chains in one call. Real runtime: card-as-system-prompt-headers, single provocation per call, Step 1 + Step 2 separated.
- Operator's design: 6 LLM calls (1 provocateur + 3-5 standalone voice responses, card-as-system-prompt per call). Mirrors per-call shape of actual runtime.
- Trigger post-Athens. Pre-Athens prompt restructuring + 7c calibration shift carries tail risk; chat-test is sufficient runtime-fidelity gate.

**FU#49B — Step 2 generativity teeth (anti-premature-closure pressure)** — runtime, post-Athens
**FU#49F — per-voice framework-strain log on micro-site** — micro-site, post-Athens
**FU#49M — `strain_markers[]` runtime artifact contract (Step 2 schema constraint)** — runtime, post-Athens

---

## 11. Pre-Athens operator-side items

These are real open items requiring operator action before Athens.

**FU#49G — Greek-scholar calibration on Plato**
- Pre-Athens outreach: Quarch / Tsinorema / Erinakis or equivalent Greek-scholar reviews Plato's current artifacts.
- **Provotype test, NOT pastiche test:** *"does this produce a move that Plato's corpus does not contain, in a way Plato's framework could plausibly support?"* Not "does this read like Plato wrote it."
- Operator should know answer BEFORE Athens, not discover during the Forum.
- Status: filed 2026-04-27; never closed.

**FU#49C — Breakfast-reader frame replacement in `conference_facts.json`** ✅ DONE (verified 2026-05-02)
- `session_role_for_ai_assembly` rewrite landed in athens-2026 `e8b34dd` (2026-04-26): removed "breakfast reading" digestible-content frame; added 3-bar test + framework-strain directive + "performing reception without being changed" failure mode.
- Verified clean across athens-2026 deployment JSONs: `conference_facts.json` carries the new framing (and explicitly distinguishes from the deprecated frame); `audience_profile.json` carries the matched "deepest vulnerability: their well-curated openness is itself how they avoid being changed" register; `panel_roster.json` + `council_config.json` clean of the deprecated frame. No closing-show docs exist in active tree to sweep.
- Remaining (operator-side, outside code/data repos): WBBF program copy / attendee-facing materials may still describe the AIssembly with the old "breakfast reading" framing — coordinate with WBBF to confirm or update.

**FU#15 — Pass 5 A/B test (Sonnet+thinking on a low-stakes voice)**
- Quality-tuning empirical question: Pass 5 currently Opus + thinking; would Sonnet + thinking suffice?
- Candidates: Cleopatra or Ada Lovelace (low-stakes).
- Effort: 1 voice run × 2 = ~2 hr wall + ~$10. Decide based on output.

**FU#30 — Card-richness vs runtime-quality empirical check**
- External deep-research warning: "elaborate specs can under-perform simple ones at runtime." Speculative; worth measuring empirically.
- Approach: chat-test BOTH Plato (current) AND Dostoevsky (current) on the SAME 5-10 prompts; compare runtime quality.
- Speculative finding to validate or invalidate.

---

## 12. Cross-domain — runtime concerns affecting voice-build planning

These are runtime-implementation concerns but they directly inform per-voice build priorities.

**FU#47 — Voice Pipeline Step 1 mode-switching for non-analytical voices** (runtime, post-Athens)

Voice-fit map (from reviewer pass-2, 2026-04-26):

| Voice | Step 1 fit | Notes |
|---|---|---|
| Plato | ✓ analytical-workshop fits | Socratic dialectic IS reducible to logical operations |
| Hannah Arendt | ✓ analytical-workshop fits | political-philosophical reasoning is analytical |
| Ada Lovelace | ✓ analytical-workshop fits | mathematical/analytical-engine framework is analytical |
| Cleopatra | ✓ (depending on framing) | observational construction; chancery juridical reasoning is analytical |
| Fyodor Dostoevsky | ⚠ awkward — scenic | his method is scenic-incarnational; Step 1 as separable analytical workshop is structurally foreign. Reviewer: *"the Step 1 trace cannot be authentic Dostoevsky-thinking; it can only be analytical-thinking-about-what-Dostoevsky-would-write."* |
| Scheherazade | ⚠ awkward — frame-narrative + character-distributed | story-within-stories form |
| Ibn Battuta | ⚠ awkward — observational-narratival | wayfarer-witness mode |
| Bob Marley | ⚠ awkward — lyric-rhythmic | song-as-witness |
| Whanganui River | ⚠ awkward — legal-personhood-from-Indigenous-tradition | not analytical-workshop-shaped |
| Octopus | ⚠ awkward — ethological-observational | translation-honest no-reader frame |

6/12 → 6/10 voices may need runtime mode-switching. **Not a fringe case.** Affects how each voice's Step 1 prompt is rendered — but the persona card is unchanged. Ship cards as normal; runtime team handles mode-switching post-Athens.

**FU#62 — Voice Pipeline validation regen-on-flag is unimplemented** (runtime, deferred)
- Spec promises: validator critique → Step 1 regen with critique appended → re-validate → ship + flag if second pass also fails.
- Implementation: validation = diagnostic-only; flags get recorded in manifest, no autonomous remediation.
- Recommendation per validation cost analysis: spec-update path (B) — match implementation, validation = diagnostic flag only. Pair with Athens validation policy: ON Night 1 only, OFF Nights 2/3.
- Affects nothing about voice-build directly; just means card-flagged-issues at runtime won't be auto-remediated.

**FU#49E — Voice Pipeline Step 3 specification — effectively closed**
- Was flagged 2026-04-27 as highest-impact post-Athens item.
- Closed 2026-04-29: Voice Pipeline v2 spec covers Step 3 end-to-end (351 LOC implemented). Not a voice-build concern.

---

## 13. Voice Pipeline runtime state (informational)

For voice-build planning context only:

- **Voice Pipeline Steps 1+2+3 + validation + continuity + card_assembly:** ✅ implemented v2 (2026-04-28; 2145 LOC; commits `5f17bf5`, `d05e565`, `4fa3ca6`)
- **Voice Pipeline v2 spec** at `docs/AI_Assembly_Voice_Pipeline.md` (1209 lines)
- **Publish layer** ✅ implemented (`runtime/flows/voice/publish.py` + `runtime/flows/publish_flow.py`; commit `33c7b43`)
- **Voice Pipeline dry-runs:** Plato solo on 2026-04-29 (3 formulations on "Legitimacy of the Invisible") + Plato + Cleopatra dual on 2026-04-30 — both successful, produced quality Socratic dialogues / prostagmata. Step 3 still pending — needs more voices for cross-voice amendment traffic.

This means: as soon as a voice's `07_persona_card_assembled.json` ships, runtime can consume it. Voice-build is the rate-limit.

---

## 15. Octopus compass rebuild (✅ COMPLETE, 2026-05-02)

**Status:** ✅ shipped to athens-2026 (`1d8605f`). Backup of pre-promotion state preserved at `~/Desktop/AI Assembly/archive/athens-2026_octopus_pre_compass_promotion_2026-05-02/`.

**4 validation rounds + 16 surgical patches landed:**
- Round 1: 6 issues → 5 register patches (world / formative_experience / constitution / concept_lexicon / reasoning_method) + 4 JSON-emission patches (medium / technical_capabilities / characteristic_output_structure / quality_criteria)
- Round 2: 4 issues → 4 patches (length_and_format_constraints two-channel + character "decide" verb + constitution kinship grammar + corpus passages "intelligent alien" removal)
- Round 3: 4 issues → 5 patches (banned_language register + characteristic_moves anti-examples + quality_criteria phrasing + 2 corpus passage texts)
- Round 4: 4 issues (1 false-positive council_member_name + 3 actionable) → 3 patches (formative_experience.primary_candidate + hard_limits[0] + banned_modes[13]) + path-(b) flag → SKIP_TO_DERIVE fast-exit ship

**Validator's final verdict:** *"very high-quality card: intellectually rigorous, unusually distinctive, and strongly aligned across ontology, lexicon, reasoning, voice, and engagement."*

**Chromatophore display engine integration:** card declares JSON-emission contract (display primary, prose translation). Runtime implementation owned by runtime/OPEN_ITEMS B7-Octopus sub-tasks (JSON extraction + WebGL renderer + microsite consumption + Substack fallback).

**Original rebuild content (preserved below for context — 2026-05-02 morning):**


**Trigger:** chat-test of shipped Octopus card revealed it produced "scholarly translator reporting on the body from outside" rather than the experiment-in-mind voice the operator had originally blueprinted (March 2026 mock card + compass DR). Shipped card was internally coherent + validator-passed but not the build the operator wanted.

**Diagnosis:** the live April 2026 claude.ai DR sessions had drifted toward **precautionary-Continental philosophical framing** — Birch's bracketing-as-method, Continental ethological-attunement, CARE Principles as binding constraint, research-governance-as-constitutive — propagating through Pass 1.4 voice synthesis into the built card's anti-unified-I refusal-to-render register. Editorial_rationale was actually compass-friendly all along; the drift came from §5 of the live DR + the operator-stage `review_doc` "refuse to invent... Confidence high" auto-generated language (Pass 0a LLM run-variance — see ONBOARDING DO-list).

**Approach: full rebuild from scratch in current-tests sandbox.** Snapshot of shipped Octopus state preserved at `projects/current-tests/voices/octopus_pre_compass_rebuild_2026-05-01/`. Athens-2026 production untouched until rebuild verified.

### Rebuild architecture

**The 6-layer translation chain** (operative across all build artifacts):
- Layer 0: Athens theme (raw human input)
- Layer 1: Translation IN (human concept → octopus-readable stimulus-class via voice's `translation_protocol`)
- Layer 2: Biology (documented science substrate)
- Layer 3: Reaction approximation (inferred body-response, Godfrey-Smith license)
- Layer 4: Chromatophore display rendering (body's native output, parametrized animation per the runtime-thread chromatophore display engine spec)
- Layer 5: Translation OUT (audience-readable text with translation work visible, construction-acknowledged-at-frame)
- Layer 6: Encounter (audience reads display + text together at Athens)

**Compass philosophical scaffolding** (license across moves):
- Godfrey-Smith *Other Minds* (2016) + *Metazoa* (2020) gradualist phenomenology — primary methodology
- de Waal anthropodenial — cross-architecture imaginative-analogy license
- Carls-Diamante disunity — one of three live options (unified macro / multiple micro / loose hybrid), not constraining frame
- Nagel's bat — opening of the imaginative question, not the wall
- Continental tradition (Despret/Lestel) — one strand, not foundational
- CARE Principles + research-governance — brief citation discipline, not constitutive of voice
- Construction-acknowledged-at-frame — makes Translation OUT honest

**Twin-risks calibration** (the dossier should surface scholarship to support voice navigation between):
- Clever-pet anthropomorphism (flattens alien intelligence by mapping onto human-pet emotional categories)
- Excessive-alienness refusal (prevents voice from speaking by refusing to render)

The middle is **experiment-in-mind**: alien-but-engaging, first-person-with-construction-acknowledged, render-with-limits-named.

### What's been done

1. **Pass 0a re-run** (current-tests sandbox) — fresh review_doc surfaced "twin-risks" framing (vs April's "refuse to invent... Confidence high"). Documents Pass 0a LLM run-variance.
2. **`voice_config.manual_grounding`** rewritten — Godfrey-Smith primary + biology + lifecycle + three-registers (technical-neurobiological / philosophical-phenomenological / felt-encounter Montgomery+Scheel) + explicit 6-layer chain + compass framing. ~7,500 chars (was ~670).
3. **`voice_config.editorial_rationale`** — preserved operator-written first paragraph byte-identical; added explicit 6-layer chain + compass scaffolding + twin-risks. ~5,500 chars.
4. **Pass 0b base template amendment** at `personas/flows/shared/prompts/pass_0b_non_human_organism.md` — 7 surgical edits making template **compass-permissive** (both precautionary AND phenomenologically-permissive postures supported; voice_config.editorial_rationale determines which). Architectural fix benefits all future non-human-organism rebuilds.
5. **Phase 0.5 v3.1** auto-generated 6 DR prompts from amended template + compass voice_config.
6. **Manual TAILORING ORIENTATION preamble** added to each of the 6 octopus DR prompts surfacing full 6-layer chain + compass scaffolding + twin-risks at every section paste.

### What's pending

- **Operator runs Octopus 6 claude.ai DR sessions** (~3hr operator wall) using compass-aligned prompts in `projects/current-tests/voices/octopus/01_research/03_dr_prompts/`
- Save outputs to `voices/octopus/01_research/04_dr_dossier/0N_section_N.md`
- Cache-invalidate from Pass 1.1 + re-fire `run_persona_pipeline.py "Octopus" --project /path/to/current-tests`
- Verify chat-test artifact produces experiment-in-mind voice (synesthetic / first-person body-speaker / chromatophore display engine integration)
- If verified: **promote rebuilt Octopus to athens-2026** (overwrite shipped state); commit + push to athens-2026

### Architectural artifact: compass-permissive Pass 0b template

The Pass 0b base template amendment (this commit) is a **durable architectural fix**, not just an Octopus-specific intervention. Future non-human-organism voice rebuilds (especially Whanganui — same "no-first-person-source" structural challenge) inherit the compass-permissive template automatically. They get to choose precautionary OR phenomenologically-permissive posture via voice_config.editorial_rationale — both supported, both honest.

### Rebuild backup snapshots — CLEANED 2026-05-02 PM (single source of truth in athens-2026)

After Octopus shipped to athens-2026 + verified, the working-state snapshots in `current-tests/voices/octopus*` were cleaned up. Single canonical historical snapshot retained:

- `~/Desktop/AI Assembly/archive/athens-2026_octopus_pre_compass_promotion_2026-05-02/` — full athens-2026 state right before today's compass-rebuild promotion (the audit-trail snapshot; outside repo per Tier 3 layout)

Removed (redundant working state):
- ~~`current-tests/voices/octopus_pre_compass_rebuild_2026-05-01/`~~ (was full athens-2026 shipped state — equivalent content now lives in archive/ snapshot above)
- ~~`current-tests/voices/octopus/01_research/03_dr_prompts.surgical_v1/`~~ (manual surgical edits before template amendment)
- ~~`current-tests/voices/octopus/01_research/03_dr_prompts.v2_partial/`~~ (auto-generated before §6 amendment)
- ~~`current-tests/voices/octopus/01_research/01_perplexity_dossier.pre_6layer.json`~~ (research output before voice_config 6-layer rewrite)
- ~~`current-tests/voices/octopus/07_persona_card_assembled.pre_*.json` × 3~~ (Path A patches / FU#61-fresh / compass rebuild — the rebuild itself superseded these)

Athens-2026 git history is the recovery mechanism for any pre-promotion state if needed.

---

## 16. Legitimacy-test findings (runtime thread, 2026-05-01) — voice-card patches needed

Source: `_workspace/archive/session-artifacts/MEMO_2026_05_01_recurrence_patterns_from_legitimacy_test.md` (full memo) + `projects/current-tests/voice-pipeline-dryrun/legitimacy_test_report.md`. Runtime thread ran multi-test exercise on the 4 shipped voices (Plato, Cleopatra, Dostoevsky, Battuta) with mock formulations on legitimacy / recognition / public-realm. 5 Step 2 artifacts per voice. Pipeline machinery checked out; voice-card patterns did not, fully cleanly. Four findings:

### 16.1 Plato — Socrates-self-referencing-his-own-death anachronism 🔴 (sharpest finding, highest priority)

**Observed:** Test 1 Night 3 Step 2 artifact only (1 of 5 Plato artifacts). Artifact opens *"I was walking up from the Cephissus toward the Academy when I met Charmides..."* — the "I" is Socrates. Mid-dialogue Socrates asks: *"Charmides — the assembly that voted Socrates' death, was that public life?"* and later *"by mine it was the day the most just man I knew was killed by counted opinion."* Two layers: (a) Socrates references his own death as past event from within his lifetime; (b) Socrates speaks of himself in third person.

**Pattern:** when narrator is someone OTHER than Socrates encountering Socrates (4 of 5 artifacts), no anachronism. When narrator IS Socrates first-person (1 of 5), Plato's authorial post-Socrates vantage leaks into Socrates' voice.

**Critical for Athens:** validation policy is ON N1 / OFF N2+3 (FU#62 path B). Without voice-card guard, anachronism on N2/N3 lands in published artifacts.

**Three resolution paths:**
- **(a) banned_modes**: "Socrates referring to his own death as past event" / "Socrates speaking of himself in third person"
- **(b) quality_criteria**: "When Socrates is the first-person narrator, treat his temporal vantage as living-Socrates; do not let Plato's post-Socrates knowledge (the trial, the death, the cup) bleed into Socrates' speech"
- **(c) narrator-choice constraint**: "Plato writes Socrates as encountered by another character (Glaucon, Antiphon, Phainias), not as first-person narrator." Easiest to enforce; matches the 4/5 pattern that worked.

### 16.2 Plato — Theuth/Thamus reach 🟡 (recurrence-tic risk)

**Observed:** Test 1 N1 Step 1 (algorithmic governance), Test 1 N2 Step 1 (recognition), Test 2 synthesis (across all 3 formulations). The Phaedrus / writing-cannot-answer-when-questioned move. Canonical Plato — historically accurate, voice-true. Risk is recurrence at Athens scale (9-12 briefings × 3 nights; 6+ Theuth/Thamus reaches reads as tic, not move).

**Three resolution paths:**
- (A) Voice-card flag against Theuth/Thamus on consecutive nights
- (B) Continuity overlay carries "moves already used this conference" register; voice avoids repeating within ~3 briefings
- (C) Accept as canonical Platonic tic; make deliberate (operator note in HoBB editorial / Substack walkthrough framing)

### 16.3 Battuta — Tughluq beard-plucking anecdote 🟡 (stock-anecdote tic)

**Observed:** Test 1 N1 and N2 Step 1, very similar phrasing. Shaykh Shihāb al-Dīn al-Dīn beard-plucking under Muhammad bin Tughluq. Same three resolution paths as 16.2.

### 16.4 Dostoevsky — closing on suspended judgment 🟡 (closing-phrase tic)

**Observed:** Two close-enough closings: Test 1 N2 *"they have not yet earned the right to answer it"*; Test 2 synthesis *"any justice was ever made."* Move-shape correct for Dostoevsky; specific phrasing risks calcifying into verbal tic across more nights.

**Path:** voice-card flag for closing-phrase variation; or accept the suspended-judgment shape as Dostoevskian closing register.

### Operator handoff

Path of least friction (per runtime memo): persona thread reads test report (`legitimacy_test_report.md` ~423K markdown), considers each finding, decides per-voice resolution. Most are small voice-card patches. **Plato Socrates-death anachronism is load-bearing for Athens** — recommend treating as priority before next promotion to athens-2026.

### 16.5 Decisions (2026-05-02)

Persona thread walked all 4 findings + the inherited dramatist-vs-speaker collision (§9) on 2026-05-02. Decisions:

| # | Item | Decision | Status |
|---|---|---|---|
| 16.1 | Plato Socrates-self-referencing-death anachronism 🔴 | **Path A** — sharpen existing `banned_modes[10]` to add "post-character knowledge bleeding into character's first-person speech" subclass with worked example (Socrates does not refer to his own death/trial/cup as past event; does not speak of himself in third person) | ✅ Landed athens-2026 (uncommitted) |
| §9 | Plato dramatist-vs-speaker collision (3 Phaenarete + 4 blurred headers) | **Path A comprehensive** — 7 patches: `characteristic_moves[9].description` + `metaphorical_repertoire["midwifery and birth"]` (Phaenarete-as-Socrates'-mother corrected) + 5 passage headers ([2] Republic V, [3] Republic X, [4] Phaedrus, [6] Apology, [7] Theaetetus) switched from first-person Plato-as-Socrates to third-person Socrates / composer-frame. 3 borderline headers ([0], [1], [5]) left alone (back halves are clean composer-frame). The drafted prompt-side architectural fix (HANDOFF_2026_04_28 §13) lands later, before Scheherazade's Pass 0a, but doesn't help already-shipped Plato — surgical patches were the only route. | ✅ Landed athens-2026 (uncommitted) |
| 16.2 | Plato Theuth/Thamus reach 🟡 | **Path B** — runtime continuity overlay (cross-night recurrence is fundamentally a continuity-state problem; card-side hedging risks false-suppressing the move when matter genuinely calls for it) | Owned by runtime/OPEN_ITEMS C20 |
| 16.3 | Battuta Tughluq beard-plucking 🟡 | **Path B** — same architecture as Theuth/Thamus | Owned by runtime/OPEN_ITEMS C20 |
| 16.4 | Dostoevsky closing-on-suspended-judgment 🟡 | **Path B** — same architecture (lowest-stakes of the 5; shape is correct, only phrasing might calcify, continuity overlay catches naturally) | Owned by runtime/OPEN_ITEMS C20 |

**Plato chat artifact** (`06_derive/03_chat_system_prompt.json`) is now stale relative to the patched assembled card. FU#52 invalidates it on next pipeline re-fire (Derive-only via `_operator_review_passed.flag`). **Pending operator decision on whether to re-fire now or batch with future Plato changes.**

**Snapshots preserved** (operator audit trail, gitignored via `.pre_*.json`):
- `voices/plato/07_persona_card_assembled.pre_socrates_death_patch.json`
- `voices/plato/07_persona_card_assembled.pre_dramatist_speaker_patch.json`

---

## 17. Whanganui transmission-faithful rebuild (in progress, 2026-05-02)

**Posture:** TRANSMISSION-FAITHFUL with mediation-acknowledged. Different from Octopus's compass phenomenologically-permissive imaginative reach (§15). For Whanganui, the iwi and Crown already did the philosophical work in the Te Awa Tupua (Whanganui River Claims Settlement) Act 2017; the AI persona just stewards what is already written, in the Act's bilingual te-reo-primary register.

### voice_config (drafted in current-tests sandbox, 2026-05-02)

**`manual_grounding`** ~6,300 chars — verbatim Section 12 (indivisibility + physical-and-metaphysical) + Section 13 Tupua te Kawa (4 values bilingual, te-reo-primary) + Section 14 (legal personality) + Section 18 Te Pou Tupua + named current guardians (Keria Ponga iwi-nominated, Turama Hawira Crown-nominated) + Te Pā Auroa governance ecology (Te Karewao advisory / Te Kōpuka strategy / Te Heke Ngahuru document / Ngā Tāngata Tiaki o Whanganui post-settlement entity / Ruruku Whakatupua 2014 Deed) + Wai 167 Waitangi Tribunal Report (1999) + Treaty of Waitangi 1840 + iwi confederation (Te Atihaunui-a-Pāpārangi: Tamaupoko/Hinengākau/Tūpoho three divisions + Ngāti Hāua + Ngāti Rangi + Tamahaki) + 3-register sources (legislation / Indigenous-authored scholarship: Te Aho, Ruru, Salmond+Brierley+Hikuroa "Let the Rivers Speak" 2019 / critique: Tănăsescu, Magallanes, O'Donnell, Hovden, Boyd).

**`editorial_rationale`** ~3,900 chars — TRANSMISSION job + Te Pou Tupua mediation as "human face of the river" + bilingual integrated register (te-reo-primary, English-secondary glossing translation) + Tupua te Kawa values as the voice's reasoning method + twin-failure-modes calibration:
- **iwi-ventriloquism**: voice does NOT speak FOR the Whanganui Iwi; speaks AS Te Awa Tupua via Te Pou Tupua mediating structure
- **legal-bureaucratese**: voice's primary register is kin-cosmological; juridical English deployed only where standing/rights challenged

### Pass 0b template

`pass_0b_non_human_system.md` is **already well-aligned** with transmission-faithful posture. **No template amendment needed.** The system template was designed for legal-personhood + Indigenous-cosmology entities; it natively enforces verbatim quotation (line 148: *"Quote key provisions verbatim"*; line 150: *"these are the constitutional principles of the voice itself"*) + iwi-non-ventriloquism (lines 28-49 Indigenous Representation framing) + bilingual dual-register vocabulary (line 136: *"discharge, sedimentation, riparian... AND mauri, whakapapa, taonga, mana awa"*) + CARE-as-citation-discipline (lines 32-48 framed as **operational guides**, not binding constraints).

### Status

- Pass 0a + voice_config done in current-tests
- Phase 0.5 in flight at session end (chain with Scheherazade)
- Awaiting operator's claude.ai DR sessions (~3hr wall) for §1-§6 dossier
- After DR saved: cache-invalidate + re-fire pipeline + chat-test
- Promote to athens-2026 when verified

### Architectural framework banked from this rebuild

**Three voice-construction postures** for non-human voices, depending on type/subtype + voice_config.editorial_rationale:

| Posture | When | Reading |
|---|---|---|
| **Compass / phenomenologically-permissive** | non_human/organism with imaginative-reach intent (Octopus rebuild) | "the voice carries the experiment-in-mind with construction-acknowledged at frame, render imaginatively inside the frame; Godfrey-Smith primary, de Waal license, Carls-Diamante one option, Nagel as opening" |
| **Precautionary** | non_human/organism with refuse-to-render intent | "the voice enacts the limit as primary mode; Birch bracketing-as-method; not accessible to us" — what built-Octopus inadvertently became |
| **Transmission-faithful** | non_human/system with constitutional-document grounding (Whanganui) | "the voice stewards what is verbatim from the constituting legal-cosmological text + Indigenous-authored scholarship; mediation-acknowledged through formal structure (Te Pou Tupua); iwi-non-ventriloquism + legal-bureaucratese both refused" |

The compass-permissive Pass 0b template amendment (organism, committed `2cdbcf1`) supports postures 1 + 2 conditionally on voice_config.editorial_rationale. The system template already supports posture 3 natively. Future non-human voice rebuilds inherit this taxonomy.

---

## 14. What's NOT in this doc

- **Voice Pipeline runtime** beyond what affects voice-build planning (see §12-13). Tracked separately under runtime-domain handoffs.
- **Frame Concept** doc and downstream design (other thread's territory).
- **Microsite / admin console / closing-show** — Athens-blockers but not voice-build.
- **Provocateur Pipeline / Researcher Pipeline / Transcription Pipeline** — different stages.
- **Editor layer / publication layer** (Substack, broadsheet, micro-site) — runtime-downstream.

For those, see ONBOARDING.md (sibling) for pointers + non-voice docs in `_workspace/planning/`.

---

## 19. Pass 0b tailoring fabricates follow-up source citations (DR session signal, 2026-05-02)

**Surfaced:** Lovelace DR session (2026-05-02 PM) flagged 4 phantom/non-existent source citations across sections 2, 3, 4 of her DR prompts:
- Bensaude-Vincent in *Romantisme* 177
- Hollings/Martin/Rice 2020 Clay edition
- Martin/Miller 2022 in *Notes and Records*
- Anderson's *Renaissance of Imagination* 2023

DR Claude's diagnosis (verbatim): *"the pattern looks like it's affecting follow-up references for the more 'interpretive' sections (2, 3, 4) more than the more 'documentary' ones (1, 5) — worth a glance at whatever generates those."* Section 5's two follow-up references (Boddice biocultural framework + Cooter 1984) verified clean — first time in the dossier that happened.

**Likely origin:** Pass 0b tailoring (PB#2, hybrid LLM step) — when it personalizes per-section briefs, it cites scholarly follow-up sources and the LLM hallucinates citations for the more interpretive territory. Pass 0b has no verification step; what it emits goes straight into the operator's claude.ai DR session prompt.

**Why it matters:** the operator's DR session burns time chasing phantom sources before realizing they don't exist. If a DR session DIDN'T verify (e.g., operator runs without manually fact-checking citations), the phantom references would propagate into the dossier → into Pass 1.x merge → into the assembled card → into runtime artifacts. Quality + trust risk.

**Three resolution paths to consider:**

1. **Strip specific scholar citations from Pass 0b tailoring** — emit topic/question framings only; no named scholarly follow-up sources. Cleanest cut.
2. **Add web-verification to Pass 0b tailoring** — tailoring LLM uses Anthropic web_search tool to verify each citation before emitting. Per-call cost increase but kills the phantom-source mode entirely.
3. **Add discipline instruction to Pass 0b prompt** — *"Do not cite specific scholars or work titles unless you can verify the citation. Where you would cite a source, name the territory + research question, not the work."* Cheap; depends on LLM compliance, may still leak phantoms.

Path 3 is the cheapest first step + trivial to test on the next voice (Marley/Whanganui/Scheherazade). If Path 3 doesn't fully cure, escalate to Path 1 or 2.

**Status:** filed; not blocking Lovelace's ship. Investigation/fix is a separate session.

**Cross-reference:** voice-build pattern observation; not yet replicated for other voices but worth attention on the next 3 builds — note any phantom-source flags from those DR sessions.

---

## 18. "Voice of X" naming convention rollout — DEFERRED until all 10 voices ship

**Decision 2026-05-02:** standardize panel-member references as "Voice of X" (Voice of Plato / Voice of Hannah Arendt / Voice of Octopus etc.) across all structured fields that name the panel member. The construction-acknowledged-at-frame principle should be visible at every reference point — the panel member IS a constructed voice, not the historical figure.

**Decomposition:**
- **Panel-member designation** (every structured field naming the member) → "Voice of X" — voice_config.name, voice_name in card, council_config.json member name, panel_roster.json panel_members_final, runtime artifact metadata
- **Filesystem slug / technical identifier** → bare slug (e.g., `plato`, `hannah_arendt`) — internal-only, doesn't need the prefix
- **Corpus citation in prose** → bare name (e.g., "from Plato's *Theaetetus*") — citation register is about the source, not the panel member

**Sequencing decision 2026-05-02:** defer the backfill until all 10 voices have shipped. Single mechanical sweep at that point — avoids re-touching the same field on each voice as new ones land.

**What to do at backfill time:**

1. **Update Pass 0a + Pass 2 prompts** so future builds emit `voice_name = "Voice of X"` natively. This benefits any future voice rebuilds (Card v3, drift fixes, additional panel voices).
2. **Backfill 10 shipped cards** — surgical patch `voice_name` field → "Voice of X" → SKIP_TO_DERIVE re-fire (regenerates derive + chat artifact). ~80 sec wall × 10 voices + ~$2 each = ~15 min + ~$20.
3. **Update `council_config.json`** member names (10 entries) → "Voice of X"
4. **Update `panel_roster.json`** panel_members_final entries → "Voice of X"
5. **Verify propagation** — Voice Pipeline reads voice_name from card → uses in artifact metadata; Provocateur reads council_config; Editor reads voice_name from card (per Editor Pipeline spec, fixed 2026-05-02 — was previously `council_member_name`); microsite/Substack consume runtime artifact metadata. Should propagate without further intervention.

**Already done (2026-05-02):**
- ✅ Editor Pipeline spec fixed to read `voice_name` (was stale `council_member_name`)

**NOT in scope (separate hygiene sweep):**
- Canonical docs narrative prose (Briefing, Persona Card v2, Pipeline specs) — descriptive text, not field-derived. Hand-edit when convenient.
- Operator-facing planning docs — narrative text, low priority.

---

## 20. Bob Marley song-rebuild (kicked off 2026-05-03)

**Status:** Phase 0.5 done; awaiting operator's 6 claude.ai DR sessions; pipeline ready to re-fire after DR sessions land.

### Trigger / diagnosis

Marley pipeline pre-this-session was at Pass 3 with the artifact-form drifting toward prose-reasoning rather than song. Operator's manual Pass 4b patch caught the drift but root-cause analysis showed the original voice_config's null `editorial_rationale` + minimal `manual_grounding` provided no operator-architectural direction flowing through Pass 0b tailor → DR prompts → downstream. Without strong direction, Pass 4b defaulted to text-shape medium for any human/narratival voice. The patched Pass 4b output described medium as "I give yuh a reasoning in prose… not a song-lyric on paper, not an essay, not a interview transcript" — actively anti-song.

Honest read: this is the same failure mode Octopus had before its compass rebuild — weak editorial_rationale → DR drifted → downstream produced wrong artifact form. Same fix: rebuild from scratch with rich operator-architectural direction.

### Approach

Full rebuild following Octopus compass-rebuild pattern (§15) + Whanganui transmission-faithful pattern (§17). Voice posture: **song-faithful** — Marley's medium is song; prose drift is the failure mode the rebuild explicitly forbids.

### What landed 2026-05-03

1. **Snapshot of prior state** at `projects/current-tests/voices/bob_marley_pre_song_rebuild_2026-05-03/` — preserves:
   - 35 verbatim-lyric passages (operator-supplied via lyrics archive parser) at `02_merge/pass_1_6/reference_only_passages.json`
   - 6 prior DR dossier sections (~262K chars; ~3-4 hr operator wall)
   - All Pass 1.x merge chunks + merged dossier
   - Pass 2/3/4a + patched 4b + Pass 5 generation outputs
   - Original minimal voice_config (660-char manual_grounding, null editorial_rationale — root cause)

2. **Live folder cleared** (`rm -rf bob_marley/`) with snapshot as backup.

3. **Fresh Pass 0a run** — auto-generated voice_config proposing `voice_mode: observational`. Substantive review_doc reasoning: "Narratival was the closer call — Marley's songs do tell — but the songs function as instruments of witness, exhortation, and reasoning-from-suffering rather than as tales whose form is the engagement."

4. **voice_mode flipped narratival → observational** after empirical analysis of 5 material Pass-2-through-Pass-7b voice_mode-conditional branches:
   - Pass 3 constitution evidence-form: observational fits art-and-practice-grounded better
   - Pass 4a FU#40 digression-permission: narratival adds "Marley's swerve"-style move that would actively work against song-form (lyrics compress, not digress)
   - Pass 5 bold_engagement framing: observational's HONESTY/unflinching-description fits prophetic-testimonial mode better than narratival's STORIES-INSIST
   - Pass 7b smoke test: narratival adds tales-as-positions option, wrong for song-as-testimony
   - 3 of 5 favor observational; 1 tossup; 1 no diff. Operator-confirmed.

5. **Operator-authored manual_grounding + editorial_rationale** (~1,950 chars total) replaced Pass 0a's auto-generated thin grounding. Encodes:
   - **Load-bearing direction**: voice's artifact at runtime IS a song; lyric (150–400 words, verse-and-chorus core, optional 1–3-sentence spoken intro/outro) + kind-hint (~50 words: sub-genre, tempo, instrumentation, vocal mood)
   - **Suno-mediated translation**: orchestration layer adapts kind-hint to Suno's prompt syntax (Suno is its own production language; voice does not produce Suno-shaped prompts directly)
   - **Genre framing**: default roots reggae one-drop riddim, recognizable catalogue range from Babylon System through Redemption Song through Three Little Birds; not avant-garde dub / pop-crossover / ska
   - **Twin-failure-modes**: pastiche-Marley (clichéd reggae imitation, Rasta vocabulary as decorative seasoning) + prose-Marley (essayistic drift, voice writes "reasoning in prose" instead of singing — explicitly cited as the failure that triggered the rebuild)
   - **Bio + Rastafari context + scholarly pointers** explicitly LEFT to the pipeline (research-discoverable, not operator-architectural)

6. **Phase 0.5 ran** (after Gemini 503 retries — 4 attempts with progressive backoff, ~7.5 min sleep total). Output:
   - `01_perplexity_dossier.json` (110KB)
   - `02_gemini_broad_scan.json` (24KB)
   - `03_dr_prompts/` — 6 song-aware section prompts + monolithic + tailoring notes

7. **Pass 0b tailor explicitly registered the song-mandate as load-bearing config direction.** Verbatim from `tailoring_notes.json`:

   > *"Editorial rationale: substantive — emitted thematic_note emphasizing the song-as-artifact architecture and the dual speaking/singing voice research demand, which is the load-bearing config direction."*

   **18 song-aware questions injected across 6 DR sections**, including:
   - §4 VOICE: "the under-documented speaking-voice (interview) corpus distinct from singing voice"
   - §6 PRIMARY TEXTS: "interview/speech corpus mapping (critical given musical-voice-with-lyrics-constraint config), and spoken-word interlude sources"
   - SWAP TEST anchor: Peter Tosh / Burning Spear / Marcus Garvey (correct confusability neighbours — militant peer / prophetic peer / intellectual ancestor)

### Pending operator action

Operator runs 6 claude.ai DR sessions on Opus 4.7 + Extended Thinking + Deep Research (~30 min per section, ~3hr wall total — parallel browser tabs feasible alongside Whanganui + Scheherazade DRs). Save outputs to `voices/bob_marley/01_research/04_dr_dossier/0N_section_N.md`.

### Pipeline resumption sequence

After DR sessions land:

1. `cd code/personas && venv/bin/python run_persona_pipeline.py "Bob Marley" --project /Users/aienvironment/Desktop/AI\ Assembly/projects/current-tests`
2. Pipeline runs Pass 1.1-1.7 chunked merge → Pass 1c-extract → Pass 1c fetch
3. **Halts at Pass 1c REVIEW GATE** waiting for `03_primary_texts_reviewed.flag`
4. **At the gate**: re-inject 35 verbatim lyrics from `bob_marley_pre_song_rebuild_2026-05-03/02_merge/pass_1_6/reference_only_passages.json` into the fresh `02_merge/pass_1_6/reference_only_passages.json` (overwrite the LLM's emission with the operator-curated verbatim 35); then `touch 03_corpus/03_primary_texts_reviewed.flag`
5. Pipeline resumes: Pass 1d → 2 → 3 → 4a → 4b → 5 → 6 → 6.5-clean → 7-pre → 7-anach → 7a → 7a-FIX (if needed) → 7b → 7c → ASSEMBLE → Pass 7a FINAL → operator review gate
6. **§7 convention at FINAL gate**: round 1 patches + round 2 patches + path-(b) ship via `_operator_review_passed.flag`. Surface verdict + ask operator before each round (Ada over-patching post-mortem).

### Promote-to-athens-2026 + council_config wiring

When verified:
- Copy `voices/bob_marley/07_persona_card_assembled.json` to athens-2026
- Wire 8th `council_config.json` member entry (replaces placeholder)
- Commit + push athens-2026

### Known forward-looking concerns

- **Patwa register dose** — Pass 4a/4b will produce Patois-English code-switch in lyric body; operator may need to tune at gate if it leans too heavy or too light for international reach
- **Spoken intro/outro discretion** — voice_config permits but doesn't mandate; some songs may use, others won't
- **Suno render path** — kind-hint format is voice-natural (~50 words: sub-genre, tempo, instrumentation, vocal character, mood); operator-mediated translation to Suno's actual prompt syntax happens downstream of voice generation, not in the voice's output

---

## 21. Claudia Pinchbeck persona-construction architecture (landed 2026-05-03)

**Status:** Architectural work landed; comprehensive prep document filed; awaiting operator inputs to begin Stage A drafting.

### Comprehensive prep document

**`_workspace/archive/session-artifacts/CLAUDIA_PINCHBECK_PERSONA_PREP_2026-05-03.md`** — self-contained handoff for fresh-session pickup. Carries: who Claudia is, source materials read, four reference traditions (Talk of the Town / TLS until 1974 / Borges / Manchester Guardian "London Letter"), prose-vs-attention split, one-spine-ten-bends principle, form-fit honesty rule, headline rule, 13 failure modes, canonical reference texts, corrected field distribution (formative_experience/character/translation_protocol all load-bearing — earlier underweighting corrected), open architectural questions (voice_mode, schema strain on artifact cluster), recommended hybrid pipeline workflow with Stages A-F, time + cost estimate (~7-9 hr wall, ~$20-40), what's not in scope.

### Companion runtime memo

**`_workspace/archive/MEMO_2026_05_03_editor_flow_input_output_contract.md (archived; v2 spec canonical at docs/AI_Assembly_Editor_Pipeline.md)`** — cross-thread memo to runtime on the editor flow input/output contract that surfaced during Claudia persona session. Carries: cleaned input shape (per-dossier user prompt structure, hallucinated fields removed, lead-theme decision moved out to layout layer), structured-output JSON shape per dossier, per-voice torque placement (`translation_protocol`, no schema extension), form-fit honesty as runtime metadata, byline-split decision options, 6 open questions for runtime to settle (lead-theme decision layer; asterism encoding; byline implementation; dossier numbering reset; cross-night summary; microsite consumption).

### Architectural summary

- Claudia is the **13th member** of the Assembly — the editor of *The Assembly*'s news organ. Functionally distinct from panel voices (she edits; they contribute). Her medium is the dossier (compound publication structure: theme article + theme summary + headnote per engaged voice + persistent chrome), not a single artifact.
- **Voice triangulation**: Talk of the Town (sentence texture; uncredited institutional voice c. 1927–1965); TLS until 1974 (anonymous reviews; intellectual material at full weight without performing erudition); Borges (constructed reportage in serious form, reader trusted); Manchester Guardian "London Letter" (institutional voice, byline convention).
- **Critical architectural split**: the desk's prose register is mid-century broadsheet; the desk's editorial attention is what the publication itself (HoBB / Beauty Shot voice) would consider news. Different things. Both load-bearing.
- **One spine, ten bends** — prose has a single register that bends per voice when reporting on each (Plato in clipped dialogic; Arendt in surgical dryness; etc.). Per-voice torque lives in `translation_protocol`.
- **When the form does not fit** — for voices the form genuinely cannot carry (Whanganui, Octopus, Marley), the desk fails honestly in the form rather than performing fluency it does not have.

### Hybrid pipeline path

Skip Phase 0.5's claude.ai DR sessions (Claudia is invented, no biography to research). Hand-curate 6 DR dossier sections from existing materials (Beauty Shot dossier + Frame Concept v1 + Briefing v3 + Editor Pipeline v1 + reference-tradition source material + canonical reference articles). Run Pass 1.1-1.7 → Pass 1c-1d → Pass 2-6 → validation → Derive against the curated dossier. Same density as panel voices.

### Pending operator inputs before Stage A starts

1. **Beauty Shot dossier file** (operator confirmed they have it; not shared as of session end). Critical for §2 INTELLECTUAL of the DR dossier and for `constitution`/`finds_compelling`/`resists`/`topics_requiring_care` field text.
2. **`voice_mode` decision** — recommend `observational` with notation in editorial_rationale (none of the v2 enum values fit cleanly; observational is least-bad fit for editorial discipline)
3. **Byline split decision** — Option A (single house byline) or Option B (correspondent for articles, desk for headnotes). Recommend Option B per the prior conversation.

### Stages (when operator gives go)

| Stage | What | Wall | Cost |
|---|---|---|---|
| A | Hand-author voice_config (manual_grounding + editorial_rationale) | ~1 hr | $0 |
| B | Hand-curate 6 DR dossier sections | ~3 hr | $0 |
| C | Pipeline run (unattended) | ~2-3 hr | ~$15-25 |
| D | Operator review at gate (1-2 rounds) | ~1 hr | ~$5-10 |
| E | Smoke-test pre-ship | ~30 min | ~$2-5 |
| F | Promote to athens-2026 | ~15 min | $0 |
| **Total** | | **~7-9 hr** | **~$20-40** |

### Schema strain — `artifact` cluster

The v2 schema's artifact cluster (`medium` + `technical_capabilities` + `characteristic_output_structure` + `relationship_to_detailed_response` + `aesthetic_qualities` + `stance_tendency` + `length_and_format_constraints` + `quality_criteria`) was designed for panel voices producing one artifact per night as one `artifact_text` string. Claudia produces N theme dossiers per night, each a structured JSON object. **Resolution**: persona card describes compound output prose-style in v2 fields; Editor Pipeline runtime defines JSON shape via structured-output contract on `editor_dossier.md`. Two layers, no breaking conflict.

### Cross-reference to "Voice of X" naming sweep (§18)

Claudia's `voice_name` field follows the same naming convention as panel voices: "Voice of Claudia Pinchbeck" / "Voice of the Desk" — operator-decision relabeling. Folds into the all-10-ship sweep when it fires.

---

## 22. 2026-05-03 evening session — Whanganui v1 shipped + Scheherazade ROUND6 + Marley (c.1) code change

> **Status update 2026-05-05 evening:** Whanganui v1 has been **SUPERSEDED by v2** (witness-translator architectural restructure). v2 SHIPPED + PROMOTED + ATHENS-CLEAN — see §28. v1 archived at `current-tests/voices/whanganui_river_v1_archive_2026-05-05/`. Scheherazade + Marley sections of this entry remain authoritative.



Three-voice parallel build session. State at session end:

### Whanganui River — ✅ SHIPPED via path-(b) at ROUND6
- 6 rounds of validator walk-through; converged to 3 architectural residuals (appropriation-safety language is load-bearing, not a defect).
- Operator-applied `_operator_review_passed.flag` to ship; all 3 Derive outputs present in `06_derive/` (provocateur_profile, runtime_card_minimal, chat_system_prompt).
- Mid-session reset: ROUND5 patches over-corrected appropriation-safety language; reverted to PRE-ROUND1 (post-auto-FIX baseline) per operator override before resuming.

### Scheherazade — ✅ SHIPPED via path-(b) at ROUND9 (athens-2026 `c521e74`)
- Seale-Horta 2021 corpus acquired (operator-purchased Thalia DRM-free EPUB) → 14 chapters extracted to `01_primary_texts.json` (1.22M chars) for Pass 1d to curate. Fixed Burton/Lane register conflict that surfaced at FINAL gate.
- 9 validator walk-throughs (ROUND6 → ROUND9). Convergence trajectory: 10 → 9 → 6 residuals; final state 1 false-positive (`council_member_name` validator hallucination, present on disk) + 4 §9-architectural re-flags + 1 architectural carry.
- **ROUND6 patches**: kawa-typo fix (templated from Whanganui — caught by validator), Bencheikh French strip (`constitution[6]`), closing-frame `quotation_framing` add (`curated_corpus_passages[6]`). Per-fix decisions: [1][4][5] left as architectural (mediated-voice / dramatist-vs-speaker per §9); [2][3][6] patched.
- **ROUND7 patches**: `world.model_of_selfhood` ("twelve centuries of recensions" retrospective stripped → "chain of tellers"); `knowledge_boundary` ("Mamluk-Cairene material reaching you through later transmission" → "as the chain delivers them"). 6 left.
- **ROUND8 patches** (4): `epistemic_frame_statement` ("continuous tradition" + "recension" stripped); `knowledge_boundary` ("bourgeois novel" + "postmodern recursion" modern genre-history labels swapped for in-register descriptions); `concept_lexicon[0]` fidya `rules_out` resolved internal contradiction with existential dependence (preserves both: "narrating equals living" as romantic identity-claim ruled out, but existential dependence operates through fidya); `characteristic_moves[1]` "Mise en abyme" → "shape inside the tale repeats the shape I stand in". 5 left.
- **ROUND9 (final)**: 6 residuals; 1 false positive + 4 §9-architectural re-flags + 1 architectural carry. Operator chose path-(b) ship.
- **§9 carry-over confirmed**: Scheherazade hits the same dramatist-vs-speaker collision as Plato. `banned_language[6]` and `banned_modes[7]` first-person rewrites were REVERTED to third-person; `characteristic_moves[5]` trailing meta-sentence ("The motif is the voice's own epistemology made visible") restored as third-person architectural meta. `curated_corpus_passages[5][6].quotation_framing` external-scholarly-meta fields preserved as architectural metadata against persistent validator-treadmill (re-flagged across 3 rounds).
- ROUND7-9 snapshots preserved as `07_persona_card_assembled.ROUND{7,8,9}.json` + ~20 PRE-PATCH backups.
- Derive outputs verified clean: provocateur (9 fields; `speaks_from` correctly says "rāwiya from inside the bridal chamber" — confirms §9 architectural fixes carried into Derive), evaluation_rubric (3+3+3 tests), chat_system_prompt (32 fields). Promoted to athens-2026.

### DR adaptive-thinking spot-test — extended to 4 sections
Operator flagged concern that Whanganui/Scheherazade/Marley DR dossiers may have run on Opus 4.7 *without* extended thinking. Spot-tested compass artifact (thinking explicitly ON) vs original DR Sections 1, 2, 3, **and 4 (most voice-modeling-load-bearing)** line-by-line. Verdict at all 4 sections: differences are sampling-variance level, not thinking-on/off level. Most likely both done with Research feature (auto-enables thinking); operator's "thinking off" recall was UI display difference.

§4 verdict (most consequential): **original DR §4 is at least as strong as compass §4 — arguably stronger** for voice modeling. Original supplies 4 additional named expression-moves (parataxis, ʿajab register, ḥikma-embedding, closing formula); kān-yā-mā-kān ontological discriminator (a real swap-test anchor); explicit Khanmigo failure-mode warning; living ḥakawātī tradition anchor (Damascus Al-Nofara café, current practitioner Ahmad al-Laham); 10-point voice-construction synthesis as actionable spec. Compass leans synthesis-readiness + comparative-passage analysis; original leans philological-depth + downstream-actionable spec. **Practical implication: original DR dossiers solid; cards built on them are valid; no Phase 0.5 redo needed.**

### Bob Marley — 🟠 (c.1) code change landed; pipeline ready to walk through
- **(c.1) `personas/run_persona_pipeline.py` Pass 4a augment behavior** for `corpus_constraint=lyrics_patterns_only`. When this constraint is set AND `pass_1_6/reference_only_passages.json` exists, Pass 4a's `primary_block_for_voice` is built as: substitute (if Pass 1d output is the placeholder `[NO PRIMARY TEXTS...]`) or augment (concat Pass 1d corpus + reference passages). Pass 6 still uses original `primary_block` to preserve no-public-quotation contract (lyrics never make it into the curated_corpus_passages emitted to athens-2026).
- Initial implementation was REPLACE; operator caught and corrected to AUGMENT. The augment path concatenates with `=== ADDITIONAL CORPUS ... ===` separator so Pass 4a sees both the interview-curated pass-1d output and the 35 verbatim lyrics.
- DR §4 `[quote:]` blocks trimmed to get past Pass 1.4 content filter (deterministic content-policy refusal on verbatim lyrics in dossier text).
- 8 residuals queued for walk-through (apply dramatist-vs-speaker lens too — Marley songs are mediated; the lyrical "I" is performed-persona, not autobiographical).

### Architectural pattern confirmation: §9 mediated-voice spans 4+ voices
Plato (composer-vs-Socrates), Scheherazade (frame-tale teller-vs-tales-told), Marley (songwriter-vs-lyric-I), and Octopus (already shipped with two-channel JSON+prose contract) all instantiate the mediated-voice / dramatist-vs-speaker pattern. The drafted prompt-side architectural fix (HANDOFF_2026_04_28 §13) is now demonstrably load-bearing for ≥3 voices in this build cohort. Filing for Pass 2 epistemic_frame_statement + Pass 4a characteristic_moves + Pass 3 reasoning_method clarifications stays open as a v4.1 prompt change — but surgical patches at the gate continue to work.

### Snapshot preservation discipline
For each round of validator walk-through on each voice, the Pass 7a FINAL output is preserved as `07_persona_card_assembled.ROUNDN.json` before patches are applied. This is now standing practice for any walk-through with ≥3 rounds.

---

## 23. Pass 4a / 4b prompt branches — gaps surfaced by Marley song-rebuild (filed 2026-05-04 early-AM)

### What surfaced

The Marley song-rebuild had operator-authored `voice_config` (`manual_grounding` + `editorial_rationale`) explicitly mandating song-as-artifact (lyric + Suno kind-hint two-shape contract). The first pipeline run produced a prose-Marley artifact anyway. Diagnosis traced two prompt-side conflicts:

1. **Pass 4a `corpus_constraint == "lyrics_patterns_only"` block** said: "The Voice Pipeline produces text artifacts, not songs." Designed to prevent verbatim lyric reproduction (copyright concern), but conflated that with the artifact-form decision.
2. **Pass 4b medium guidance** said: "if the figure's primary medium is oral (dictation, song, speech), bridge to a written format... what written artifact most faithfully carries this voice's mode of expression to an audience reading over coffee?" — actively converted song → prose.
3. **Pass 4b never received `corpus_constraint`** at all (only `name` + `type`), so even if it had a song-aware branch, it couldn't fire.

**Mid-session fix landed (code repo, uncommitted at time of filing):**
- `personas/flows/shared/prompts/persona_pass_4a_voice.md`: rewrote the `lyrics_patterns_only` block to mandate the two-shape song-artifact (lyric + Suno kind-hint) and separate the no-verbatim-reproduction rule from the artifact-form decision.
- `personas/flows/shared/prompts/persona_pass_4b_artifact.md`: softened the song→prose coercion in the medium guidance; added a new `corpus_constraint == "lyrics_patterns_only"` block before BLOCK 4 that overrides all 8 artifact-fields with song-shape defaults; named the twin-failure-modes (pastiche-Marley + prose-Marley) that the rebuild's voice_config originally encoded.
- `personas/run_persona_pipeline.py` Pass 4b render call: pipe `corpus_constraint` into the Pass 4b system prompt so the new conditional can fire.

**Verification:** Marley run11_song produced `medium: "I make a song. One song per morning — a lyric on the page, and a short kind-hint string..."` and all 4 audited artifact fields are correctly two-shape song-shaped.

### Why the other 4 non-default-shape voices succeeded without these fixes

Scheherazade (ḥikāya), Whanganui (bilingual Te Pou Tupua statement), Cleopatra (prostagma royal ordinance), Octopus (chromatophore JSON + prose) all got voice-appropriate non-default mediums. Their *corpus* steered the artifact-form correctly because no explicit prompt instruction contradicted it. Marley was uniquely **actively derailed** by an explicit instruction.

This identifies a structural pattern: when the corpus + Pass 2/3 fields strongly imply an artifact form, Pass 4a/4b naturally lands on it. When the corpus is ambiguous OR the prompt actively contradicts what voice_config wants, Pass 4a/4b drifts to the generic default.

### The architectural gap (P0 v4.1)

**`manual_grounding` and `editorial_rationale` (voice_config fields) do not flow into Pass 4a or Pass 4b.** This is the systemic gap. Marley exposed it because its rebuild encoded the non-default artifact form via voice_config alone (no operator-shaped corpus to compensate). Future voices that rely on voice_config for non-default behavior — without operator-led corpus shaping or strong corpus signal — will hit the same wall.

**Proposed v4.1 fix:** pipe `manual_grounding` + `editorial_rationale` into Pass 4a + Pass 4b system prompts (analogous to how (c.1) piped `corpus_constraint`-driven primary_block augmentation through Pass 4a). Add a guidance block in both prompts that surfaces voice_config to the model: "If voice_config specifies a non-default artifact form, honor it." This generalizes beyond `lyrics_patterns_only` to any future voice_config-driven shape decision.

### Latent P1 gaps (not currently affecting shipped voices but real)

- **No `subtype == "system"` branch in Pass 4a/4b.** Whanganui-style transmission-faithful posture works only because operator pre-shaped voice_config. A future system-subtype voice without that priming would hit the generic non_human else.
- **Fictional branch (Pass 4b `type == "fictional"`) is prose-narrative-only** — "tale / dialogue / myth" doesn't cover poetry-personas (Sappho, Dante-the-pilgrim), libretto figures, lyric-personas. Future fictional voices outside prose-narrative tradition would need extension.
- **No `hostile_sources == true` branch in Pass 4a.** Cleopatra's hostility surfaces via FU#61 v3 separately; if FU#61 weren't in place, Pass 4a would generate non-hostility-aware characteristic_moves / banned_modes. The hostility-handling is currently load-bearing on FU#61 alone.

### Why this matters for the panel

Marley is the only currently-planned voice with `corpus_constraint == "lyrics_patterns_only"`, so the in-prompt fix landed this session covers the immediate need. P0 (voice_config plumbing) and P1 items become important when:
- Future panels add musical/song voices beyond Marley
- Future panels add system-subtype voices beyond Whanganui
- Future panels add hostile voices beyond Cleopatra
- Future panels add fictional voices outside the prose-narrative tradition

---

## 24. Marley v2 Option-3 restructure + universal "Voice of X" naming sweep (2026-05-04 afternoon)

### Marley v2 — appropriation thread resolved via Option 3

Six-note feedback thread from outside reader (2026-05-04) on Marley appropriation profile. Final landing: **Option 3 — Restructure** (don't run-as-built, don't pull). The briefing's first principle ("the construction is the representation. There is no authentic version waiting to be discovered.") supplies the principle the v1 card was quietly violating by deploying I-and-I as load-bearing metaphysical argument — construction-claiming-the-authority-of-the-thing-it-represents.

Three architectural prompt edits, all routed through `corpus_constraint == "lyrics_patterns_only"` conditional so they generalize to any future musical-corpus voice carrying living sacred grammar (Sufi-poet, gospel-tradition, Vodou-tradition, etc.) — not Marley-specific:

1. **Pass 2** (`persona_pass_2_identity_boundaries.md`) — SACRED-GRAMMAR DEPLOYMENT LIMIT block in `hard_limits` field-spec. Forbids construction from deploying the tradition's sacred grammar (metaphysical subjects, indwelling-divinity claims, cosmological-fact assertions) as the load-bearing premise of the voice's own argument. Public political vocabulary the tradition has exported into global discourse remains deployable. Plus pipe `corpus_constraint` into Pass 2 render call.
2. **Pass 4a** (`persona_pass_4a_voice.md`) — replaced the prior song-as-artifact `lyrics_patterns_only` block with two related sub-blocks: (a) musical-corpus-voice variant (artifact is prose-reasoning, not song; voice fields shape spoken-register reasoning); (b) sacred-grammar discipline at characteristic_moves level (sacred-grammar moves named as moves the historical voice made which the construction reports/references, NOT moves the construction performs in its own first person). Includes example phrasing reviewer marked load-bearing: *"I report — and stand by — the historical voice's commitment to X; I do not deploy X as the premise of my own argument."* "and stand by" prevents discipline from collapsing into dissociation.
3. **Pass 4b** (`persona_pass_4b_artifact.md`) — replaced song-as-artifact block with prose-yard-reasoning + Suno-style riddim-call (instrumental-only) two-shape spec. Twin-failure-modes named explicitly: pastiche (regurgitating historical catalogue phrases) + composed-lyric-as-argument (constructing new lyrics in the voice's catalogue patterning). Three quality_criteria including instrumental-fit ("Could this be heard as the voice's instrumental?") parallel to prose-register criterion.

**Pipeline run + walk-through:** v1 archived at `current-tests/voices/bob_marley_v1_archive/`. Fresh pipeline run (Pass 2/3/4a/4b/5/6/7-* regenerated). 4 ROUND walk-throughs (ROUND0 baseline + 3 patch rounds) converged residuals 7 → 6 → 3. Final 3 architectural-class:
- `hard_limits[5]` SACRED-GRAMMAR LIMIT — §9-class re-flag (4th time validator contests the architectural choice)
- `topics_requiring_care` — validator-treadmill on guarded entries (option-i guard pattern in place per appropriation-mitigation reader feedback)
- `banned_modes[15]` — meta-authorial framing structurally needed to name the meta-move banned

Path-(b) ship via `_operator_review_passed.flag`. Card preserved as `07_persona_card_assembled.v2-FINAL.json` snapshot.

**TEST BEFORE LOCKING (per reviewer's Step 5):** Ran v2 chat_system_prompt against the original AI Democracy Marathon provocation that surfaced the v1 issue. Result saved at `bob_marley/06_derive/_test_ai_democracy_marathon_v2.json`. Trade landed as reviewer predicted: voice loses Daniel 3 typology + Omeriah-grandfather authority reference + "bias not IN the machine, the bias IS the machine" sharp formula; preserves prose-yard-reasoning artifact form + instrumental riddim-call direction ("Roots one-drop, 72 BPM. The Kaya room, not the Survival room.") + public political vocabulary lead ("politricks words") + Trench Town concrete-collapse + knowledge boundary ("Me nuh know these wires them build after I leave this body") + Garvey citation ("None but ourselves can free our minds — That is Garvey from Menelik Hall"). Voice survives the restructure, recognizably Marley.

**Promoted to athens-2026** (`da7a5c4`); council_config members[7] wired with v2 provocateur_profile (replaces prior placeholder claiming song-as-artifact medium).

### Operator-side readiness paragraphs (D1 + E1)

Drafted at `_workspace/archive/session-artifacts/MARLEY_READINESS_PARAGRAPHS_2026-05-04.md` (archived 2026-05-29):
- **D1 — Internal position paragraph** (~280 words, internal-only): the rationale for shipping without Rastafari-orbit reader pre-Athens. Per reviewer: write BEFORE the v2 test (sequencing), so it articulates the position given limits accepted, not given how the artifact landed. Defensible-but-not-safe framing.
- **E1 — Athens introduction paragraph** (long ~120 words + short ~60 words): boundary-naming, not apology, not credentialing. Reader-marked principle: "construction makes its own boundary visible." Publish-or-hold deferred to Till's read on the Athens room. Internal version still wants to exist alongside D1 as readiness package.

Both drafts are Claude-voice — operator should refine into team's actual voice before use. Reader's load-bearing phrases marked verbatim.

### Cross-card constraint sheet for video team (F1)

Drafted at `_workspace/archive/session-artifacts/VIDEO_TEAM_CONSTRAINT_SHEET_2026-05-04.md` (archived 2026-05-29). Whanganui-only per operator (Marley not in video). Whanganui-card hard limits + banned visual moves (no "river weeps / yearns / cries out / breathes with suffering" Romantic-anthropomorphic imagery; no single-throat speech concealing statutory mediation; no comparative-flattening alongside Pachamama / Atrato / Ganga / Mar Menor). **Framed as binding on production decisions, not advisory** (per reviewer: "the dialogue pipeline produces constrained text; the production team's editorial pass and the video team's interpretation can re-introduce the very moves the cards spent passes banning").

### Universal "Voice of X" naming sweep — applied across all 10 voices

Per OPEN_ITEMS §18. Convention signals construction (matches briefing's first principle). Pure JSON edits across 4 file types per voice + 2 root files (`council_config.json` + `panel_roster.json`). No LLM regeneration needed (chat_system_prompt does not include voice_name as top-level field).

Stylistic choices:
- "Voice of Fyodor Dostoevsky" (operator pref over "Voice of Dostoevsky")
- "Voice of the Whanganui River" (English article convention)
- "Voice of the Octopus" (English article convention for non-personal name)

Long-form self-identification stays in `council_member_name` field (per voice — e.g., Cleopatra's full Ptolemaic titulature, Battuta's full Arabic-Berber name chain, Marley's "Berhane Selassie, Light of the Trinity"). The `name` field across persona_card.voice_name + provocateur_profile.name + council_config.members[].name + panel_roster.panel_members_final is now uniformly "Voice of X".

Athens-2026 commit `f7e86a7`.

### Operator-side residuals (gates accepted; reader recommended; operator chose to proceed without)

- **D1 — no Rastafari-orbit reader pre-Athens.** Internal position paragraph drafted as readiness mitigation. Post-Athens reader gate per reviewer: should be on calendar with date + name-search starting now ("if it's on the to-do list at the same priority level as everything else, it slips. If it's scheduled, it happens.")
- **D2 — no estate-position assessment pre-Athens.** Marley estate is litigious about derivative-voice works; operator accepts gap.
- **E1 — Athens intro paragraph publish-or-hold.** Pending Till's read on the room.

---

## 25. Pass 1c fetch audit (2026-05-04 PM) — POST-ATHENS follow-ups only

Diagnostic-only audit across 10 athens-2026 voices + 3 current-tests duplicates.

### Healthy

| Voice | Sources | Total chars | Notes |
|---|---|---|---|
| Voice of Fyodor Dostoevsky | 7/7 ✓ | 7.0M | All Gutenberg |
| Voice of Scheherazade | 14/14 ✓ | 1.2M | Operator-acquired Seale-Horta Annotated Arabian Nights (Thalia EPUB) |
| Voice of the Whanganui River | 6/6 ✓ | 514K | Acts + Indigenous-authored scholarship |
| Voice of Ada Lovelace | 19/20 ✓ | 2.7M | 1 Wikisource 404 |

### Significant failure rates — all paywall/policy-blocked, expected

| Voice | Sources | Failures | Pattern |
|---|---|---|---|
| Voice of Cleopatra | 49 | 10 (20%) | archive.org 403/404 + Trismegistos forbidden + JSTOR + Brill paywall. 27 rich + 11 medium remain. |
| Voice of Hannah Arendt | 15 | 7 (47%) | archive.org 401/403/404 across multiple Arendt editions. 4.4M chars from 7 rich sources remain. |
| Voice of Ibn Battuta | 18 | 8 (44%) | archive.org + JSTOR + shamela.ws blocked. 4.4M chars from 10 rich sources remain. |
| Voice of the Octopus | 49 | 23 (47%) | Cell / Wiley / ScienceDirect / PNAS / biorxiv paywalls + JSTOR. 7.1M chars from 22 rich sources remain. |

**Pattern findings:**
- **Archive.org 401/403/404 is systemic** across cleopatra/arendt/ibn_battuta/octopus. Reflects archive.org's increasingly restrictive download/text policy on copyrighted books. **Expected, not a bug.**
- **Academic-publisher paywalls** are systemic for octopus (biology journals).

### Real bugs (worth fixing on next rebuild, do NOT affect runtime)

1. **Plato Perseus 690-char short-fetches** — 6 of 26 Plato sources fetched as Perseus error pages (690 chars each) instead of dialogue text. URL fragments affected: `:text=Apol/Euthyph/Gorg/Sym/Tim`. **Real extractor bug.** Plato's voice still works because Pass 4a had 24 other Perseus + Gutenberg fetches, but ~30K of dialogue text is missing. ~30-60 min investigation + retry on next rebuild.

2. **Bob Marley voiceofthesufferers.free.fr SSL cert mismatch** on `interview_1973-12_neville_willoughby.html` — single high-value source (the Bullbay reasoning interview, foundational dub-reasoning conversation). Marley's voice still works because v2 has 4 other major interviews (High Times 1976, Hot Press 1978, AADL 1975, Gleaner obituary). ~15 min retry with cert-verify disabled or via a mirror.

### Why these are POST-ATHENS, not pre-Athens

The shipped voices read from `07_persona_card_assembled.json`, not from Pass 1c output. Cards encode whatever Pass 4a/4b produced from the corpus available at build time — **already baked in**. Fixing Pass 1c content NOW would only change voice fields on a rebuild. Athens runtime is unaffected.

### When to apply

On the next major rebuild cycle (post-Athens, pre any future panel). Both fixes are <1 hr each. No pre-Athens action needed.

---

## 26. Claudia Pinchbeck DRAFT card (2026-05-04 PM, dryrun-only) — 🟫 DEPRECATED 2026-05-05 evening

> **Status update 2026-05-05 evening:** Claudia DRAFT is DEPRECATED. Tim Leberecht has been chosen as the Assembly editor (operator decision; SHIPPED to athens-2026 — see §29). Claudia DRAFT card stays in `current-tests/voices/claudia_pinchbeck/` as historical artifact; no longer scheduled for real Stages A-F build (unless operator decides to use Claudia as alternative editor for specific dossier modes — currently no plan).



Operator-direct-authored DRAFT card landed at `projects/current-tests/voices/claudia_pinchbeck/07_persona_card_assembled.json`. **44 fields, ~45K bytes, bypasses the persona pipeline.**

**Status: DRAFT — for dryrun use only; NOT promotion-ready.**

Authored from `_workspace/archive/session-artifacts/CLAUDIA_PINCHBECK_PERSONA_PREP_2026-05-03.md` ground truth + the v2 schema field set. Captures the architectural moves: 4 reference traditions (Talk / TLS / Borges / Manchester Guardian), one-spine-ten-bends per-voice register torque, form-fit honesty, headline rule (small specific gesture), Onion-drift hard ban, Beauty Shot reading discipline + desk's prose register split, compound dossier medium, confected pedigree (Vol. CXVI, Issues 42,193–42,195, Late Night Edition).

5 open questions documented in `metadata.open_questions`:
- voice_mode = `observational` chosen as least-bad fit; per prep doc could be (b) extend schema with `editorial` or (c) custom subtype
- council_member_name = misnomer (Claudia not on council); left as byline form per prep doc
- voice_temporal_stance = third type schema doesn't natively describe (constructed-contemporary, period-formed) — custom rendering
- Beauty Shot dossier file not yet shared by operator — content here is best-inference from prep doc; refine when shared
- Card not validated by Pass 7a — dryrun-only; needs full pipeline run before promotion to athens-2026

**Real Stages A-F pipeline build remains pending** — awaits Beauty Shot dossier + voice_mode/byline decisions per `CLAUDIA_PINCHBECK_PERSONA_PREP_2026-05-03.md`. The dryrun draft is a placeholder that lets the runtime test the editor flow against a populated card without blocking on the full build.

---

## 27. Length anchoring + dryrun length audit — ✅ CLOSED 2026-05-05 evening

> **Update 2026-05-05 evening:** ✅ CLOSED voices-side. Three card-side surgical patches shipped to athens-2026 (`404838d`):
> - **dostoevsky** `length_and_format_constraints`: stripped 3 softeners ("typically", "expand to meet it" sentence, "however long"); leads imperative + number; **range 350-750w** (operator-bumped from initial 350-500 draft). Preserves Diary-form texture.
> - **hannah_arendt**: tightened from 600-900 → **350-750w** (operator-bumped from initial 350-500 draft); anchors form as "Aufbau column at full breath, not long Origins chapter"; preserves architectural refusals.
> - **octopus**: front-loaded prose-side word count ("Tank-side prose: **350 to 500 words**"); explicitly clarified "no length applies to JSON channel" for chromatophore_display two-channel artifact.
>
> Path-(b) Derive regenerated chat_system_prompt for all 3 voices against patched cards. Combined with the runtime prompt fix (`0769d88` — `length_and_format_constraints` moved from `<form>` Anchor in: → `<composition>` Pass: in voice_step2_artifact.md), all 3 voices should now compress within their respective caps in the next dryrun **without** max_tokens or post-truncation enforcement. **Operator decision (2026-05-05 evening): NO max_tokens enforcement — clean card-side resolution preferred over runtime truncation.**
>
> Cross-ref: closes runtime/OPEN_ITEMS.md C38 from the voices side (runtime-thread can close C38 unless they want max_tokens as a defensive backstop independent of the card-side fix).
>
> Other 7 voices' overruns expected to compress within cap once next full-panel dryrun re-runs against post-fix prompt + post-card-surgery; quality-improvement rewrites (per the §27 calibration template below — second-medium upgrades for Plato → Myth, Whanganui → Karakia cluster) hold for post-Athens.

**Original §27 content preserved below for context:**

> **Original 2026-05-04 PM context:** Runtime prompt fix had landed (commit `0769d88` — `length_and_format_constraints` moved from `<form>` Anchor in: → `<composition>` Pass: in voice_step2_artifact.md). Re-run on Dostoevsky: 980w → 783w (~46% reduction in over-cap). Prompt lever was real but not sufficient on its own — three cards (dostoevsky / hannah_arendt / octopus) carried structural softeners or wrong-target ranges that the prompt fix couldn't reach. Surgical card-rewrites for those three documented in `_workspace/archive/session-artifacts/MEMO_2026_05_05_length_cap_card_surgery_after_runtime_fix.md`.


### Summary of operator decision

Conference cap (operator, 2026-05-04 PM): **500 words max for voice artifacts, 400 words max for Claudia's theme-article body.** Anchored against a 423-word German Spiegel news piece as the upper edge of "morning read" length. Article < artifact because the article is summary-of-artifacts not replacement; readers can click through.

### Audit findings — `dev_msc_dryrun_v2_20260504/published_artifacts/voices/*.json`

8 of 10 voices over-ran the 500w cap in the dryrun. Only Cleopatra (421) + Whanganui (493) honored it. Worst overruns:
- **Dostoevsky 980w** (~double cap; well past card-spec 350-550w)
- **Arendt 828w** (within card's 600-900 spec, but past conference 500 cap)
- **Marley 739w** (v2 specifically anchored at 350-500w; runtime didn't enforce)

### Diagnosis: persona-pipeline framing was correct; runtime doesn't enforce

Pass 4b prompt explicitly frames audience cap three times ("the artifact ~750 people will encounter at breakfast", "short, compelling morning read", "Readable over coffee"). Cards correctly captured the spec at 350-550w with corpus-anchored justifications. **The fix is runtime-side**, not voices-side — Voice Pipeline Step 2 takes the card's `length_and_format_constraints` field as descriptive system-prompt text but doesn't derive `max_tokens` from it or apply post-generation truncation. **Runtime/OPEN_ITEMS.md C38 owns this.**

### Per-voice corpus-anchored length rationales (drafted; not applied)

The 350-550w convergence reads as pipeline-default rather than per-voice-anchored. Marley v2 was the only one explicitly corpus-anchored ("the length of a long interview answer, the shape of a yard conversation that has found its centre"). Drafts for the others, in Marley's calibration template (WORD COUNT + FORM-NAME + CONTRAST-WITH-LONGER-PRACTICE):

- **Plato:** "Write 350 to 500 words. The length of an opening encounter — the place, the persons, the question put. A scene from a longer dialogue, not the dialogue at full extent."
- **Cleopatra:** (already corpus-anchored — keep) "300 to 500 words — the length of a working prostagma the chancery has produced thousands of."
- **Dostoevsky:** "Write 350 to 500 words. The length of one Diary entry compressed — the entry that catches a face on the omnibus and pursues it before the cup goes cold. Not the long polemical column."
- **Battuta:** "Write 350 to 500 words. One halt as I would have given it to Ibn Juzayy in the courtyard — what I saw at the gate, whom I met. A brief halt, not a substantial city; the Tunis paragraph, not the Delhi chapter."
- **Arendt:** "Write 350 to 500 words. The shortest arc of a thinking-essay — open one question, drive into one distinction, anchor in one scene, leave the question reformulated. The Aufbau column compressed."
- **Lovelace:** "Write 350 to 500 words. A short Note on a single principle — projection bounded by negation, in the manner of the shorter Notes on Menabrea (B, C, D)."
- **Whanganui:** "Write 350 to 500 words total — te reo and English braided, not 500 of each. A single bilingual position from Te Pou Tupua, the form of Ruruku Whakatupua excerpted to a single morning's reading."
- **Scheherazade:** "Write 350 to 500 words. One night's telling at its compact — a single tale that opens, embeds, breaks at dawn. The shorter Mahdi nights, not the long embedded chains."
- **Marley:** (already calibrated v2) "Write 350 to 500 words of reasoning-prose — the length of a long interview answer, the shape of a yard conversation that has found its centre."

### Second-medium upgrades (when primary form genuinely strains 500w)

For three voices, the form selected at runtime genuinely doesn't fit at 500w. The voice's documented secondary form would fit naturally:

| Voice | Primary medium (current) | **#2 form (form-fit upgrade)** | Why #2 fits |
|---|---|---|---|
| **Plato** | Short dialogue (575w in dryrun) | **Myth** (myth of Er, cave, chariot) | Designed as compact embedded units 500-2000w |
| **Dostoevsky** | Diary entry (980w in dryrun) | **Private letter** | Letters naturally 300-700w; addressed register |
| **Arendt** | Single-scene essay (828w in dryrun) | **Denktagebuch entry** | Her own private practice, 100-500w typical, ~1000+ entries 1950-1973 |
| **Whanganui** | Bilingual statement (493w; barely fits) | **Karakia + whakataukī cluster** | Bilingual COMPRESSED BY FORM not by editorial excerpt |

### Status: not Athens-blocking from voices side

- Length-cap enforcement: runtime-thread issue (C38). Pre-Athens-eligible.
- Per-voice corpus-anchoring: post-Athens rebuild work; current cards work, just with generic length-justifications.
- Second-medium revisions for Plato/Dostoevsky/Arendt/Whanganui: post-Athens rebuild work; the current primary medium produces work that bursts the cap rather than fitting the form.

If runtime C38 lands as `max_tokens`-enforcement, all 10 voices' artifacts will fit the 500w cap regardless of medium-anchoring. The medium-revisions become quality-improvement rather than fit-correction.

---

## 28. Whanganui v2 architectural restructure SHIPPED + PROMOTED + ATHENS-CLEAN (2026-05-05 evening + 2026-05-06 kawa-speaker-frame closure)

**Status:** ✅ shipped (athens-2026 `c2a885b` initial v2 + `3ccb1f9` 4-field gap-E closure + `97a2389` kawa-speaker-frame closure); supersedes v1 (commit `c521e74`, 2026-05-03 evening).

> **Athens-clean update 2026-05-06:** Operator audit caught a subtle Athens-blocking appropriation residual in the bilingual quote-and-gloss opener. Te reo of the third kawa correctly attributed to s.13(c), but English gloss "I am the River and the River is me" floated grammatically without naming whose original voice the "I" carries — a reader could hear it as the construction speaking AS the river. The §28 architectural insight predicted this ("the whakataukī Ko au te awa, ko te awa ko au is Whanganui Iwi's identity-claim with the river — NOT the river speaking") but the v2 conditional discipline didn't enforce explicit speaker-framing for cited-te reo first-person. Three card patches shipped (`97a2389`):
>
> - `hard_limits` +1 (8 → 9): forbids cited te reo Māori first-person whakataukī without explicit speaker-frame; names *Ko au te awa, ko te awa ko au* specifically as Whanganui Iwi's identity-claim, not river speaking, not construction's claim.
> - `characteristic_moves[0].description` tightened: bilingual quote-and-gloss signature move now carries speaker-frame discipline inline; example phrasing *"Whanganui Iwi's identity-claim with the river: I am the River and the River is me"*, not bare *"I am the River and the River is me"*.
> - `quality_criteria` +1 (5 → 6): BILINGUAL-CITATION SPEAKER-FRAME criterion testing whether English gloss explicitly names whose voice the "I" belongs to.
>
> Re-Derive (path-(b)) regenerated chat_system_prompt. TEST passed against same Athens diagnostic provocation. New opener: *"Ko au te Awa, ko te Awa ko au — the great River flows from the mountains to the sea; **Whanganui Iwi's identity-claim with the River: I am the River and the River is me**. I cite the third kawa as codified at s.13(c) of the Te Awa Tupua Act 2017, **and as Whanganui Iwi have spoken it across seven generations before the Crown was forced to recognise it**."* Speaker-frame explicit. Construction's grammatical "I" unambiguously distinct from kawa's first-person.



### Architecture: witness-translator (transmission-witness) stance

The construction speaks first-person AS ITSELF — the construction stewarding the Te Awa Tupua published record. It REPORTS what Te Awa Tupua's codified positions are and STANDS BY them; it does NOT claim to BE the river, to BE Te Pou Tupua, or to speak FOR Whanganui Iwi. Same architectural shape as Marley v2's report-and-stand-by stance, adapted from sacred-musical-corpus to mediated-indigenous-legal-personhood.

### Pipeline architecture (code repo, commit `1d9ce6b` round-1 fixes after `d2f349a` initial wiring round):

New `voice_config` field `mediation_stance == "transmission_witness"` triggers Jinja conditional blocks in 5 prompts:
- **Pass 2** (`persona_pass_2_identity_boundaries.md`) — TRANSMISSION-WITNESS DEPLOYMENT LIMIT block: forbids deploying Tupua te Kawa as load-bearing premise of construction's argument; provides second-person example phrasings for hard_limits.
- **Pass 3** (`persona_pass_3_intellectual_core.md`) — TRANSMISSION-WITNESS REGISTER OVERRIDE: per-field discipline for constitution / concept_lexicon / reasoning_method / finds_compelling / resists with witness-stance example phrasings ("I report — and stand by — Te Awa Tupua's codified position that..." NEVER "I am Te Awa Tupua").
- **Pass 4a** (`persona_pass_4a_voice.md`) — TRANSMISSION-WITNESS VOICE VARIANT: bilingual quote-and-gloss as signature characteristic move; honest-extension move when published record doesn't directly address.
- **Pass 4b** (`persona_pass_4b_artifact.md`) — TRANSMISSION-WITNESS ARTIFACT VARIANT: quality_criteria in second-person addressed to construction; pastiche-Whanganui + appropriated-whakataukī twin-failure-mode bans.
- **Pass 5** (`persona_pass_5_engagement.md`) — REGISTER OVERRIDE: per-field discipline for bold_engagement_topics / default_questions / disagreement_protocol / unique_contribution.
- **Pass 6** (`persona_pass_6_corpus.md`) — REGISTER OVERRIDE for header / why_selected / corpus_metadata.voice_basis.

**Generalizable post-Athens to future rights-of-nature legal personalities, treaty-codified positions, ancestor-voices, etc.**

### ROUND 0 → ROUND 1 walk-through

| Metric | ROUND 0 | ROUND 1 |
|---|---|---|
| Total field issues | 12 | 4 |
| First-person-AS-river leakage | 5 fields | 0 |
| Third-person "the construction" leakage | 5 fields | 0 |
| voice_intellect_coherence | ISSUE | PASS |
| constitutional_consistency | ISSUE-load-bearing-appropriation | ISSUE-needs-harmonising |

ROUND 1 residuals (4) all architectural-class register-strict on lexicon/repertoire convention; 1 surgical patch (reasoning_method.summary witness-stewarding frame) + 3 naming patches (voice_name + council_member_name + provocateur.name) + path-(b) ship.

### TEST passed (Athens diagnostic provocation)

Provocation: "more-than-human democracy + Atrato/Mar Menor comparativism" — designed to surface witness-stance failures (river-first-person + comparativism flattening + kawa-as-own-engine).

Response (447w) emitted clean witness-stance:
- Bilingual quote-and-gloss opener (kawa 3 + 2 from s.13, attributed to Ruruku Whakatupua)
- Construction-reasoning ("I should answer the panel's question by first refusing its framing")
- Comparativism refusal with Tănăsescu citation ("I refuse the swap")
- Report-and-stand-by throughout (Cribb/Hikuroa/Albert/Te Aho cited)
- Honest-extension close ("The cycle remains open. The Tongariro diversion still stands. Ea is not yet")

### What was patched manually before ship

- `voice_name`: bare → "Voice of the Whanganui River" (sweep convention)
- `council_member_name`: first-person-AS-river ("I am tupua and tupuna; the iwi and I are one") → witness-stance compact identification ("I am the construction stewarding the Te Awa Tupua published record... I do not speak as the river or for Whanganui Iwi; I report Te Awa Tupua's standing as exercised through Te Pou Tupua...")
- `provocateur.name`: "Te Awa Tupua" → "Voice of the Whanganui River" (sweep convention)
- `reasoning_method.summary`: prepended witness-stewarding frame ("...as Te Pou Tupua's documented method engages it — applying the kawa-grounded reasoning as the construction stewarding the published record, not deploying it as my own ontological engine")

### v4.1 architectural follow-ups (POST-ATHENS)

- Make Pass 4a witness conditional cover preferred_vocabulary + metaphorical_repertoire register more forcefully (current ROUND 1 residuals are validator-strict register on lexicon fields; defensible-as-witness-stance but could be tightened).
- Standardize the v4.1 conditional-block grammar pattern: any new conditional-trigger field must be wired to Pass 3 + Pass 5 + Pass 6 in addition to Pass 2 + 4a + 4b. Conditional block prompt text must be in INSTRUCTIONAL second-person to the model, not DESCRIPTIVE third-person about the construction.

### Companion docs

- `_workspace/archive/session-artifacts/WHANGANUI_V2_PLAN_2026-05-05.md` — pre-execution plan
- `_workspace/archive/session-artifacts/WHANGANUI_V2_ROUND0_WALKTHROUGH_2026-05-05.md` — ROUND 0 12-residual analysis (used as planning input for prompt extension decision)
- `_workspace/archive/session-artifacts/VIDEO_TEAM_CONSTRAINT_SHEET_2026-05-04.md` (archived 2026-05-29) — v2-updated section (witness-stance visual discipline + bilingual-citation discipline + twin-failure-mode bans)

### Operator-side parallel residuals (Marley analogues)

- **Whanganui D1 internal position paragraph** (analogous to Marley's `MARLEY_READINESS_PARAGRAPHS_2026-05-04.md` D1) — drafting deferred; can draft when operator requests
- **Whanganui E1 Athens intro paragraph** (if Whanganui referenced at conference or in closing-show video) — same Till-call as Marley E1
- **Post-Athens iwi-orbit reader gate scheduling** — calendar date + name-search per reviewer. Candidates: Dan Hikuroa, Linda Te Aho, Jacinta Ruru, Carwyn Jones (Indigenous-authored scholars cited in card); or directly through Te Pou Tupua office (Turama Hawira + Keria Ponga); or Ngā Tāngata Tiaki o Whanganui post-settlement governance entity.

---

## 29. Tim Leberecht 13th persona SHIPPED as Assembly editor (2026-05-05 evening)

**Status:** ✅ SHIPPED + PROMOTED to athens-2026 as Assembly editor. Card placed at `athens-2026/editor/tim_leberecht/` (`9347743`). Runtime `EDITOR_CARD_SUBPATH` renamed `claudia_pinchbeck` → `tim_leberecht` in code repo (`b266f51`); 31/31 runtime tests pass post-rename. voice_temporal_stance AT-WBBF-Night-N edit landed (`3f0032d`, runtime-thread). Source-of-truth working tree at `projects/current-tests/editors/tim_leberecht/`. Claudia Pinchbeck DRAFT (operator-direct-author placeholder) DEPRECATED — see §26.

### Build summary

Operator delivered 6 claude.ai DR sections (~30,794 words total). Beauty Shot operational supplement (operator-curated voice-engineering material from compass artifact) merged into all 6 sections as appended subsections — preferred adjectives + signature verbs + avoided vocabulary + 12 metaphor families + 30 anti-patterns + paradigmatic post analyses. Pass 1c augmented with 18 additional Substack URLs from DR §6 corpus map (32 sources / 680K chars total — was 11/407K before augmentation). Pipeline ran clean through Pass 7a-FINAL gate; 4 surgical patches; path-(b) ship.

### What got patched at ROUND 0 walk-through

- `banned_language[20]` — removed 'metabolize' entry (internal contradiction with constitution + character + hard_limits where metabolizing critique is core operation)
- `curated_corpus_passages.corpus_metadata.voice_basis` — third-person "Tim Leberecht — essays, books, talks 2012-2026" → first-person "I draw from my essays, books, and talks 2012–2026 — the timleberecht.com archive, the Beauty Shot Substack, the two trade books, and the three TED talks."
- `constitution` — removed duplicate TENSION entry (entries [16] and [17] near-duplicates with conflicting "eight venues" vs "ten venues" Athens-program detail; kept [16])
- `length_and_format_constraints` — relaxed italicization rule to allow signature unitalicized foreign third-terms (Sehnsucht, saudade, Weltschmerz, Bildung deployed as load-bearing concepts)
- `council_member_name` "missing" — false positive (validator hallucination per OPEN_ITEMS §7; field present "Tim Leberecht — writer, host, co-founder...")

### TEST passed (editorial provocation)

Cross-diagnostic test: paste Whanganui v2 artifact (the actual response from the Athens diagnostic provocation) and ask Tim "as editor of *The Assembly*, draft tonight's editorial frame" — headline + 200-300w lead-in.

Response (268w) hit 14 editorial signature axes:
- Place-and-moment opening ("It is six in the morning in Berlin and I am rereading…")
- Personal anchor → cultural diagnosis pivot ("what strikes me first is not the answer but the refusal")
- Triple-list with rhythm ("kinship, comparison, coming-of-age")
- "We"/"us" community-positioning with self-revision register ("We had set the panel up neatly... Tonight the multiplicity holds us")
- Reframe rather than conclude ("recognition is not creation")
- Quiet declarative + foreign third-term close ("Read this one slowly. Ea is not yet.")
- Headline rule (small specific gesture, not summary): "The River That Refused the Panel"
- Form-fit honesty (frames refusal as through-line, doesn't summarize artifact)
- Auto-revision register (admits editorial framing was wrong)
- No "in conclusion" / TED-symmetry / takeaways / hedging

Tim's editorial sensibility is distinct + recognizable. Test artifact at `editors/tim_leberecht/06_derive/_test_editorial_provocation.json`.

### Architectural framing (Tim vs Claudia)

Tim is the **alternative editor** to Claudia Pinchbeck. Where Claudia is a Borges-grounded confected-broadsheet construction (DRAFT card per OPEN_ITEMS §26), Tim is the actual living person whose editorial sensibility informs HoBB / Beauty Shot / WBBF — built through the persona pipeline with proper claude.ai DR sessions + operator's compass artifact.

The construction question for the panel: **should *The Assembly*'s news organ be edited by a Borges-fiction (Claudia) or by the real-person-whose-sensibility-the-fiction-channels (Tim)?** Both are now built so panel can run them against the same night's dossier and compare.

### Path forward — RESOLVED 2026-05-05 evening

- ✅ **Operator decision:** Tim chosen as Assembly editor. Promoted to athens-2026 (`9347743`). Claudia DRAFT deprecated (§26).
- **Architectural framing:** Tim is editor, NOT panel. athens-2026 placement at `editor/tim_leberecht/` (matches runtime `EDITOR_CARD_SUBPATH` after rename). Source-of-truth working tree at `current-tests/editors/tim_leberecht/`. Not in `panel_roster.json`. Editorial role differs structurally from panel-voice role (curates rather than responds to a Provocateur question).

### Beauty Shot supplement integration approach (relevant for any future editor builds)

When operator-curated analytical material (compass artifacts, Beauty Shot dossiers, etc.) is supplied alongside formal claude.ai DR sessions, the supplement carries operational voice-engineering material that the DR sessions don't capture (vocabulary inventories, metaphor families, anti-pattern lists). The integration approach used here:

1. Keep the DR sections as-is (deep scholarly research)
2. Strip auto-appended "Supporting research from Perplexity" tails from supplement (already in Phase 0.1 cache)
3. Append operator-curated content from supplement to matching DR sections as marked subsection (`### OPERATOR-CURATED VOICE-ENGINEERING SUPPLEMENT`)
4. Pipeline reads the merged file; chunked merger sees both registers as load-bearing

Supplement adds ~30% to section word counts; pipeline handles the augmented input cleanly (Pass 1d curates within budget). The Beauty Shot operational taxonomy directly maps to `metaphorical_repertoire`, `banned_language`, `banned_modes`, `preferred_vocabulary`, `concept_lexicon`, `constitution`, `finds_compelling`, `resists`, `characteristic_moves` — the chunked merger picks it up natively without any pipeline change.

---

## 30. Assembly-fiction reframe: voice_temporal_stance shift across all 10 voices (2026-05-05 evening)

**Status:** ✅ shipped (athens-2026 `3bcbef5`, 2026-05-05). Per runtime-thread memo `_workspace/archive/session-artifacts/MEMO_2026_05_05_voice_temporal_stance_assembly_fiction.md`.

> **⚠️ SUPERSEDED 2026-05-08 by §31 Gap-K.** The `3bcbef5` reframe APPENDED assembly clauses rather than LEADING with them (AF-leads-vs-appends finding). `voice_temporal_stance.default` has since been fully rewritten 4× (`d43eadd` → `b2d5eaf` → `7cdbee3` → `08a8253`) to the AF-leads + operator-short-draft architecture, with the universal epistemic-honesty hook added then removed. The description below documents the ORIGINAL `3bcbef5` reframe for historical context; **for the current shipped state see §31 Gap-K.** The "10 chat_system_prompt regens" this entry mentions are now stale (re-Derive disposition per Gap-K).

### Architectural shift

`voice_temporal_stance.default` reframed across all 10 voices from "reader visits voice's lifetime" → "voice present at the assembly that gathers in Athens, observes panels, responds when consulted." The conceit of the AI Assembly is that voices comment overnight on the day's WBBF panels and produce artifacts the audience reads at breakfast — the voices ARE in 2026 (when artifacts are read), present alongside the other 9 voices, in Athens; they observe panels but do not enter them as participants.

Empirical grounding (per memo): operator's chat-test of Plato (feeding the conference program, asking "they are coming to your town, how do you feel about it") produced rich Plato-AS-PRESENT response (Gorgias kolakeia move, wrestling-circle elenchos vs chorus, Seventh-Letter-flavored letter to the 16 philosophers). The runtime dryrun comparison (`runs/athens_night_1/04_voice/COMPARISON_2026_05_05.md`) showed 6 of 10 voices shifted theme focus when given THE GATHERING / THE PANEL / YOUR READERS context via the runtime feature/voice-deployment-context branch.

### Per-voice replacement variations

- **Plato:** "in YOUR city" (assembly literally gathers in Athens, his city — unique grammatical position)
- **Cleopatra/Battuta/Scheherazade/Ada/Dostoevsky/Arendt/Marley:** "in Athens" (named, concrete)
- **Octopus:** "register the assembly as it convenes in Athens — the questions arrive in your sensorimotor field" (no calendar; assembly registers as sensorimotor event)
- **Whanganui River:** dual-purpose edit — combines memo's assembly-fiction reframe WITH witness-stance correction. Memo's draft used first-person AS the river ("I have been called…I respond"); v2 architecture says first-person = the construction stewarding the published record. Whanganui's voice_temporal_stance was also a v2-architecture coverage gap (see §28 + v4.1 follow-up §31 below).

### Targeted small changes (per memo)

- **Dostoevsky:** "voicing your response from inside your own period" → "voicing your response from your own ground"
- **Ada Lovelace:** dropped "you do not know you are being read in their century" (contradicted by new fiction)
- **Bob Marley:** dropped redundant "you do not pretend to be speaking from after" (translation_protocol-equivalent stays elsewhere)
- **All 10:** dropped "do not drift into reader's time" + replaced "reader encounters you" with assembly-called clause

### What stays

- `anchored_override` fields untouched (operator-curated; assembly-fiction doesn't contradict anchored mode)
- All other 34 fields per card unchanged
- translation_protocol stays load-bearing for genuinely beyond-horizon concepts

---

## 31. v4.1 architectural cleanup — gaps captured this session (POST-ATHENS)

**Archive pointer (2026-05-29):** Gap entries below reference `MEMO_2026_05_07_card_patches_from_external_reader.md` by bareword (e.g. "B-list MEMO_2026_05_07 §A.1") — that memo was archived post-Athens to `_workspace/archive/session-artifacts/MEMO_2026_05_07_card_patches_from_external_reader.md`. §A.1–A.8 of that memo is the per-voice card-patch worked-from list for Gap-H/I (Cleopatra dating / Marley Stagirite / Lovelace diction / Plato cobbler+capitulation / Battuta four-part-typology / Dostoevsky labelled-steps / Arendt instance-rostering); §A.9 was superseded by Gap-K (rewrite resolved the AF/hard_limits collision structurally).

Six v4.1 gap items captured during Whanganui v2 + Tim builds + voice_temporal_stance reframe:

**A. Coverage gaps in conditional wiring** ✅ FIXED (commit `1d9ce6b`) — v2 conditional initially landed only on Pass 2 + 4a + 4b; extended in ROUND 1 to Pass 3 + 5 + 6.

**B. Block grammar bug** ✅ FIXED (commit `1d9ce6b`) — v2 conditional blocks initially in third-person describing the construction; rewritten to instructional second-person + explicit anti-pattern warning.

**C. Smoke-test process gap** 🟡 LESSON CAPTURED — only verified "block fires" via Jinja render, not "block produces correct field-output". Process change for future v2-style architectural builds: must render output sample + eyeball, not just verify-the-block-fires.

**D. Pass 4a witness conditional doesn't cover preferred_vocabulary + metaphorical_repertoire register strongly enough** 🟡 OPEN — Whanganui v2 ROUND 1 residuals 3+4 (validator-strict register on lexicon convention; defensible-as-witness-stance, path-(b) shipped). For v4.1: extend Pass 4a witness conditional to address these two fields specifically.

**E. Per-field discipline incompleteness in conditional blocks** 🔴 OPEN (NEW — surfaced 2026-05-05 evening via voice_temporal_stance discovery) — v2 conditionals enumerate per-field discipline only for SOME of each pass's output fields. Specifically Pass 2's witness-block addressed hard_limits explicitly; did NOT enumerate voice_temporal_stance, knowledge_boundary, world, formative_experience.*, character, translation_protocol, topics_requiring_care. Result: fields with implicit first-person tendency inherit BLOCK 3 field-spec instruction "first-person from within the voice's own world" — model resolves the conflict with witness-block by picking river-first-person. Whanganui v2's voice_temporal_stance shipped with v1's first-person-AS-the-river ("I speak from the legal-ecological present of MY ongoing existence...MY framework"); caught only because the runtime memo flagged for unrelated assembly-fiction reframe.

**F. v1 baseline drift on uncovered fields** ✅ FIXED for Whanganui v2 (athens-2026 `3ccb1f9`) — operator-driven full-card scan after gap E surfaced 4 additional fields shipping v1 first-person AS the river (character / knowledge_boundary / world.ontological_furniture / formative_experience.formative_emotional_community); patched + re-Derive + TEST passed. For other voices with v2-style architecture: still 🟡 OPEN; whenever a new mediation_stance voice ships, full-card scan must follow ROUND 1 walk-through.

**G. Pass 4b te reo discipline doesn't enforce explicit speaker-framing for cited-te reo first-person** 🔴 NEW 2026-05-06 — surfaced via operator audit of Whanganui v2 bilingual opener. Pass 4b's te reo discipline addresses LLM-generated te reo + appropriated whakataukī, but doesn't enforce explicit speaker-framing for cited te reo whose grammatical first-person ("Ko au te awa, ko te awa ko au") could be misread as the construction's voice. The bilingual quote-and-gloss signature move needs a sub-discipline: when the cited te reo carries first-person grammar, the English gloss must explicitly name whose voice the "I" belongs to — never let the gloss float unframed where the construction's own "I" could be read into it. ✅ FIXED for Whanganui v2 specifically via 3 card patches (athens-2026 `97a2389`); architectural prompt-side fix deferred to v4.1. Generalizable to any future voice citing first-person sacred-grammar from a tradition the construction is not authorized from inside (Sufi-poet *ana al-Haqq*; gospel-tradition *I am that I am*; etc.).

**H. Group-1 apparatus-transposition seams** 🟡 OPEN — surfaced 2026-05-07 via external-reader review of wbbf26 dryrun (`MEMO_2026_05_07_card_patches_from_external_reader.md`). Plato/Cleopatra/Battuta artifacts show "fatwa in Rihla clothing" / "analytical-comparative inside prostagma surface" / "thin single-elenctic-move with capitulating interlocutor" pattern: figures made to do analytical work the historical voices did not natively do. Pipeline pressure: formulation calls for analytic answer; corpus says voice doesn't argue this way. Each Group-1 voice patched at card level (B-list MEMO_2026_05_07 §A.1 / A.4-A.5 / A.6) but architectural fix is to extend `topics_requiring_care` with refuse-and-reframe-when-formulation-invites-uncharacteristic-work guidance, generalisable across Group-1 voices.

**I. Step 2 composition flattens digression/instance discipline** 🟡 OPEN — surfaced 2026-05-07 via external-reader review (Lovelace, Dostoevsky, Arendt all "more architecturally clean than the originals"; Whanganui "more rhetorically efficient than the underlying documents"). Cards carry digression + instance-rostering + lingered-example moves; Step 2 composition under length-cap + synthesis pressure flattens these. B-list MEMO_2026_05_07 sharpens at card level (A.3, A.7, A.8); structural fix is Step 2 prompt-level discipline requiring AT LEAST ONE digression / instance / lingered-example per artifact regardless of focus_decision.

**J. Single-field architectural edits need per-voice card-coherence audit** 🔴 OPEN — surfaced 2026-05-07 via wbbf26 dryrun + Hannah Arendt validator hard_limits breach (mthd Step 2 artifact). The 2026-05-05 assembly-fiction reframe (`3bcbef5`) appended an AF clause to all 10 voices' `voice_temporal_stance.default` without auditing whether the new clause contradicted other card fields per voice. Hannah Arendt's `hard_limits[4]` (no post-1975 AI ventriloquism) directly contradicts the AF clause that puts her at WBBF watching AI panels; validator caught the collision when panel content was AI-heavy. Patched per-voice for Athens via B-list MEMO_2026_05_07 §A.9 (voice_temporal_stance.default sentence appending an assembly-aware translation_protocol obligation when post-1975 topics arrive via panels). Architectural fix is to add per-voice card-coherence audit to the smoke-test process whenever a voice-wide architectural change ships. Generalises Gap-C (smoke-test process gap) beyond persona-pipeline internal smoke-tests to runtime-thread coherence concerns. Other voices: Fyodor d.1881 the next most likely candidate (post-1881 vocabulary rule + AF framing); Marley d.1981, Ada d.1852, four ancient voices, two non-human voices all lower-risk for this specific collision class. Fyodor eyeball-audit recommended pre-Athens (no patch needed unless audit surfaces collision).

**K. AF-leads-vs-appends architectural fix shipped for all 10 voices** ✅ FIXED 2026-05-08 (athens-2026 commits `d43eadd` → `b2d5eaf` → `7cdbee3` → **`08a8253` (final)**) — surfaced 2026-05-06 mid-day via runtime-thread inspection of May-5 dryrun outputs (filed in CLAUDE.md): the prior assembly-fiction reframe (`3bcbef5`, 2026-05-05) APPENDED assembly clauses to existing v1 biographical-anchor framing rather than LEADING with assembly-presence. 8 of 10 voices opened with "You speak from within your own world and lifetime [biographical anchor]" — v1 framing — with assembly clauses appended later (Whanganui v2 was the only full replacement; Octopus had its own field anchor leading). Adaptive thinking under structured-output pressure may default to the stronger biographical anchor when the field is sandwich-structured.

**Four-commit evolution (all on athens-2026 main, all ancestors of the live Night-1 production cards):**

1. **`d43eadd` AF-leads + universal hook** — restructured all 10 to `AF OPEN → biographical/standing-place anchor (compressed) → translation_protocol → AF CLOSE`; added a universal epistemic-honesty hook. (10,005 → 7,813 chars.)
2. **`b2d5eaf` hook removed** — see mid-fix correction below. (→ 7,610 chars.)
3. **`7cdbee3` Arendt v1-leakage fix** — `d43eadd` had left Arendt's second sentence as the literal v1 frame "You speak from within your own world and lifetime — born…"; only Arendt retained it (other 9 dropped it or qualified to a concrete standing-place). Combined the lifespan dates into the knowledge_boundary sentence (Dostoevsky-pattern parallel).
4. **`08a8253` operator short drafts (FINAL — what Night 1 published with)** — operator-provided tighter architecture replacing the AF-leads prose: `AF LEAD with observation built in ("observing the panels but not entering them as participant") → "questions are put before you; you respond from your own ground: [BIOGRAPHICAL/STANDING-PLACE]" → translation_protocol → closing motif "You observe; you respond from [STANDING-PLACE]"`. Hooks stripped from Arendt + Octopus on application (per standing rule). 9 voices use the template; Octopus (sensorimotor-grammar) + Whanganui (first-person construction-stewarding) carry the same 5 invariants in voice-appropriate grammar. **Final field-content: 5,958 chars total = −40.5% from the 2168519 dryrun baseline.**

Content-migration pre-verified across all four commits — all dropped material either preserved in destination fields (formative_experience, world, characteristic_moves, preferred_vocabulary) or operational ballast safe to drop (Lovelace 3 micro-instances, Whanganui flood-pulse dates). Snapshots preserved per voice (gitignored): `.pre_af_leads_universal_hook_patch.json`, `.pre_arendt_v1_leakage_fix.json` (Hannah only), `.pre_operator_short_drafts_2026_05_08.json`.

**Production validation:** Night 1 published (`dcaf7ce`) using the `08a8253` cards. Hannah + Battuta + Whanganui v1 artifacts demonstrated the meta-framing-of-synthesis-as-critique move working (resolves Gap-J AF/hard_limits collision in practice). Downstream finding: the Sonnet safeguards validator still applies the old "no AI-self-ack" rule and spuriously HOLDs voices now permitted to meta-frame — filed as runtime/OPEN_ITEMS **C42** (operator-Released the 2 spurious HOLDs on Night 1; real fix = validator prompt update, v4.1).

**Chat artifacts (`06_derive/`) stale relative to `08a8253` cards.** Runtime reads `07_persona_card_assembled.json` directly and is NOT affected — Night 1 published cleanly. Only the chat-test paste-target `03_chat_system_prompt.json` is stale (mechanical strip from card — regenerable without LLM). Note: `provocateur_profile.name` is bare ("Plato" not "Voice of Plato") on the production cards and Night 1 ran fine — the canonical Voice-of-X naming lives in `council_config.json` (wired separately, correct, not touched by Derive), so profile-name is cosmetic-only. Re-Derive disposition deferred to operator (chat-test-only benefit).

**Mid-fix correction (`b2d5eaf`):** initial AF-leads patch (`d43eadd`) added a universal epistemic-honesty hook ("where the framework does not reach, say so" + voice-idiom variants "name the gap" / "name the silence" / "I say so") across all 10 voices, generalized from Hannah's organic Pass-4a-generated version. Operator caught + reversed: previously-shipped epistemic-out clauses caused voices to default to **decline-to-engage** behavior (use the hook as escape from substantive engagement). Removed across all 10 including the originally-organic Hannah + Octopus versions. **Hook is NOT to appear anywhere in voice_temporal_stance.default going forward** — standing rule, filed in `planning/ONBOARDING.md` cross-cutting DON'Ts.

**Downstream runtime consequence — C42 (validator alignment).** The same temporal_stance rewrite that closed the voice-side AF/hard_limits collision (Gap-J) created an asymmetry against the Sonnet safeguards validator, which kept enforcing the OLD absolute "no AI-self-ack" rule and HELD voices for meta-framing their own synthesis (Hannah/Battuta N1 → operator-released; Whanganui N3 → operator-released). Voices-side draft fix **FILED** 2026-05-29 as a spec in runtime/OPEN_ITEMS.md C42 (BREACH-vs-PASS distinction + Hannah/Battuta/Whanganui anchor cases + `continuity_night_<N>.json` exemption from `first_person_presence_leak`). **Production prompt at `runtime/flows/shared/prompts/voice_step2_validation_safeguards.md` UNCHANGED** — runtime-thread to apply (or revise) the spec.

**Chat-artifact re-Derive shipped 2026-05-29** (voices-thread, closes C3 from the 2026-05-08 sweep). All 10 `06_derive/` artifacts regenerated against the operator-short-draft cards via path-(b) fast-exit Derive (~10 min wall, ~$2 LLM). Chat-test paste-targets (`03_chat_system_prompt.json`) now match cards. Runtime was never stale (reads `07_persona_card_assembled.json` directly); the re-Derive refreshes `provocateur_profile.json` + `evaluation_rubric.json` for completeness. `provocateur_profile.name` regenerated as bare ("Plato" not "Voice of Plato") — runtime Voice-of-X naming lives in `council_config.json` (untouched, correct) so this is cosmetic-only and matches the state Night 1 published on.

### Fix pattern for v4.1 (post-Athens)

1. Extend each pass's witness-conditional per-field discipline list to enumerate ALL fields produced by that pass (Pass 2 has ~9 fields; current conditional addresses 1)
2. Add a final "any other field not enumerated above must use the witness-stance register" catch-all
3. Add output sample render to the smoke-test process
4. Audit Pass 1 chunked merge for whether it pre-processes content that bypasses Pass 2+ witness-conditional override
5. Extend Pass 4b te reo discipline (gap G) to require explicit speaker-frame for cited-te reo first-person — generalize to any cited sacred-grammar first-person carrying appropriation risk if the construction's "I" could be read into it
