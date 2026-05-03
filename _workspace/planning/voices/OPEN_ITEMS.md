# Voices — Open Items (authoritative, 2026-05-03)

**Scope:** EVERYTHING still open or undecided that pertains to the **persona pipeline / voice cards** for athens-2026. Distinct from the Voice Pipeline runtime (Steps 1+2+3) which has its own tracking.

**Date stamp:** 2026-05-03. Supersedes 2026-05-02 late-night version. Supersedes voice-related items in HANDOFF_2026_04_27.md through HANDOFF_2026_04_30.md (all variants), FU61_DRYRUN_VERDICT_2026_04_30.md, and the voice-relevant FUs in FOLLOW_UPS.md. Read this doc + ONBOARDING.md (sibling) instead of trawling those.

**Truth source:** When this doc disagrees with another, this doc is right (or fix this doc).

---

## 1. Per-voice build state

Panel is **10 voices** (per `athens-2026/panel_roster.json`). **7 of 10 shipped to athens-2026.** 1 in flight; 2 awaiting operator DR sessions.

| Voice | type | voice_mode | Hostile? | State | Notes |
|---|---|---|---|---|---|
| Plato | human | philosophical | false | ✅ shipped + 2026-05-02 patched | Surgical patches landed (`cf283bf`): banned_modes[10] sharpened (Socrates-death anachronism) + 7 dramatist-vs-speaker patches. §9 closed via §16.5; runtime-side tics owned by runtime/OPEN_ITEMS C20. |
| Cleopatra | human | observational | **true** | ✅ shipped | FU#61 v3 prompt-driven re-emission landed (`c89d186`+`54cd20a`). |
| Dostoevsky | human | narratival | false | ✅ shipped | Round 1 + 2 patches → path (b) → fresh quality_criteria patched-in (`5088d67`). |
| Battuta | human | narratival | false | ✅ shipped | Round 1 + 2 patches → path (b). |
| Octopus | non_human | observational | false | ✅ **compass-rebuild shipped 2026-05-02** (`04da2c8`); 4 rounds + 16 patches; chat-test verified two-channel JSON+prose emission contract. Runtime asset bundle at `code/docs/runtime_assets/octopus_chromatophore/`. See §15 below. |
| Hannah Arendt | human | philosophical | false | ✅ **shipped 2026-05-02** (`bfe917a`) — 3 validation rounds + 6 surgical patches. Post-1975 topics flagged as analogical extensions. |
| Ada Lovelace | human | philosophical | false | ✅ **shipped 2026-05-02** (`3a6fe2f`) — 5 rounds + 21 patches; **4 over-patches subsequently rolled back** to validator-faithful minimum (`c025914`) after operator caught §7-convention deviation. Note G/Note A held-not-resolved as constitutional tension. |
| Bob Marley | human | **observational** ✓ flipped 2026-05-03 (was narratival) | false | 🟠 **SONG-REBUILD KICKED OFF 2026-05-03**. Snapshot at `bob_marley_pre_song_rebuild_2026-05-03/` preserves the 35 verbatim-lyric passages + 6 prior DR sections + all generation/validation state. Fresh Pass 0a + new operator-authored voice_config (~1,950 chars: manual_grounding + editorial_rationale encoding song-as-artifact mandate; lyric + kind-hint two-shape contract; Suno-mediated kind-hint translation; default roots reggae one-drop genre framing; twin-failure-modes pastiche-Marley + prose-Marley). Phase 0.5 done — Pass 0b tailor explicitly registered the song-mandate as load-bearing config direction; injected 18 song-aware questions across 6 DR sections; SWAP TEST anchor Tosh/Burning-Spear/Garvey. DR prompts staged at `01_research/03_dr_prompts/`. **Awaiting operator's 6 claude.ai DR sessions** (~3hr wall, Opus 4.7 + Extended Thinking + Deep Research). After DR: re-fire pipeline; at Pass 1c gate re-inject 35 lyrics from snapshot; §7 convention at Pass 7a FINAL. See §20 below for full rebuild detail. |
| Whanganui River | non_human | system / null | false | 🟡 Pass 0a done + voice_config rewritten **transmission-faithful** (Tupua te Kawa verbatim + Te Pou Tupua mediation + Indigenous-authored scholarship); Phase 0.5 done; DR prompts ready for operator's claude.ai sessions. See §17 below. |
| Scheherazade | fictional | narratival | false | 🟡 Pass 0a done (auto-default voice_config; null editorial_rationale); Phase 0.5 done (after sustained Gemini 503 retry); DR prompts ready. Mediated-voice prompt-fix concern carries through to her Pass 2 generation. |

### Voice-mode coverage so far (7 shipped)

- philosophical: 3 (Plato, Hannah Arendt, Ada Lovelace)
- narratival: 2 (Dostoevsky, Battuta)
- observational: 2 (Cleopatra, Octopus)

Marley = narratival in build; Whanganui = system/null; Scheherazade = narratival. Pass 0a calls for the 3 remaining voices already landed but **operator must re-check each call independently** — voice_mode is a *construction* decision (how the pipeline builds the voice), not a *historical* one. Don't take Pass 0a's first proposal as final without weighing irreplaceability against the panel.

---

## 2. Octopus — ✅ SHIPPED via Path A (2026-05-01)

Pass 7a FINAL round 1 flagged **layer instability**: card alternated between (a) Pass 2's translation-honest no-reader frame and (b) Pass 4b's scholar-dispatcher-with-citations frame. Path A surgical 6-patch landed; round 2 dropped to 1 false-positive (`council_member_name` validator hallucination); path (b) accepted, Derive ran clean.

**6 patches applied (athens-2026 `8bb9981`):**
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
- Architecturally-correct fix is prompt-side but carries 9480d3a-revert risk
- Now re-evaluable under thinking-visible (FU#60) conditions
- Decision pending: re-attempt single component on Plato Pass 4b under thinking-on, OR continue accepting via flag

**FU#39 — Character-distribution stage-quoting** 🔵 CONDITIONAL
- Applies to distributed voices: Plato, Scheherazade, Dostoevsky, Battuta
- Conditional on narrator-unification signal
- Plato shipped without it; Dostoevsky shipped without it; Battuta shipped without it
- Probably can be closed unless Scheherazade triggers on her build

### Recently closed but documented

- ✅ **FU#60** — adaptive thinking observability + temperature compatibility (committed `dd64782` + `0381278` + `85f04da`)
- ✅ **FU#61** — voice-side Layer-1 audience-engagement criterion via Pass 4b prompt (committed `91947a7` + Cleopatra `c89d186`/`54cd20a` + Dostoevsky `5088d67`)
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

### 9480d3a revert hypothesis re-evaluation
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
- **LLM_CALL_INVENTORY.md:** refreshed `bd15f84` 2026-05-01 (FU#53 + Pass 4b standalone test).
- **"Phase L" sweep:** active docs cleared 2026-05-02. Archived HANDOFFs (`_workspace/archive/voices_consolidation_2026_05_01/`) intentionally retain historical references.
- **Octopus athens-2026 `07_section_5_dr_prompt.compass.md` stray** (mid-rewrite artifact pre-rebuild decision): deleted 2026-05-02. Canonical rebuild DR prompts live in `projects/current-tests/voices/octopus/01_research/03_dr_prompts/`.

Section retained as audit trail; no active items.

---

## 7. Card-level invariants we've established empirically

### What's known to work

- **FU#49A v2 quality_criteria scaffold** — 3-5 + 1 outcome question pattern. "Could this be mine?" for fidelity; "Could this on its own make an audience engage with its intent?" for reception. Field-name references not strictly required (substance grounding is enough).
- **FU#53 review-gate** — Pass 7a FINAL post-assembly + operator gate. Caught real issues across 4 voices. Use path (a) re-validate for first round of patches; path (b) accept-residuals via flag for later rounds (the validator treadmill never reaches zero).
- **FU#52 chat_system_prompt regen** — runs unconditionally at end of pipeline; assembled-card patches propagate to chat artifact correctly.
- **FU#60 thinking-on adaptive + display:summarized + drop temperature** — all in place. `thinking_trace` + `block_types` captured in clients.py. Streaming-stability retry catches httpx.RemoteProtocolError (commit `a6fa848`).

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

### 9480d3a-revert and 582af96 baseline (prompt history)

- **582af96 baseline** = the verified-good Pass 2/3/4a/4b/5 prompt state predating the texture-degrading FU#49 cumulative additions. This is the prompt state Plato 2026-04-25 shipped under (chat-tested OK).
- **9480d3a revert** (2026-04-28) = full revert of FU#49H/I/J/K/L/D back to 582af96. After empirical chat-test signal showed cumulative additions had degraded artifact texture relative to 04-25 shipped baseline.
- Currently landed on top of revert: **FU#49A v2** (commit 0ca02f5; quality_criteria 3-dim field-tied scaffold), **FU#49D re-applied** (Position B Hard_limits with hedge discipline), **FU#51** (Pass 7a routing guard), **FU#44+** (5 patcher patterns), **FU#52** (chat artifact invalidation), **FU#53** (review-gate + Pass 7a FINAL), **FU#57** (bold_engagement_topics drop from runtime), **FU#58/59** (Pass 7a/7c register-rule fixes), **FU#60** (thinking observability + temperature compatibility), **FU#61** (audience-engagement +1 in Pass 4b prompt).
- **Stripped/reverted (NOT in current prompts):** FU#49H#1-4, FU#49I, FU#49J (5+2 quality_criteria; reverted to FU#49A's at-least-one form), FU#49K, FU#49L, plus the 04-28 cryofreeze framing in voice_temporal_stance was REPLACED with the simpler "voice arrives at Athens with full canonical experience" framing.
- The cryofreeze + tense-discipline OUTPUT REGISTER blocks + family-of-forms + anti-generic-register were initially landed (`180a8ee`) but the cryofreeze + family-of-forms components were subsequently reverted at the 04-28→04-29 transition. Card v2.1 §H + §J spec text retains the family-of-forms aspiration, but Pass 4b prompt currently single-form-locked until Cleopatra empirical validation.

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
- Dostoevsky fresh is unambiguously stronger than original-shipped (ventriloquized-as-the-gentleman engagement test) — landed via patch `5088d67`
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
- 1-retry with 15s backoff (commit `a6fa848`) is sufficient; first retry usually succeeds

---

## 9. Plato dramatist-vs-speaker collision — ✅ RESOLVED 2026-05-02 (`cf283bf`)

**Status:** ✅ RESOLVED via §16.5 Path A comprehensive (athens-2026 `cf283bf`). 7 surgical patches landed: characteristic_moves[9].description + metaphorical_repertoire["midwifery and birth"] (Phaenarete-as-Socrates'-mother corrected) + 5 passage headers ([2] Republic V, [3] Republic X, [4] Phaedrus, [6] Apology, [7] Theaetetus) switched from first-person Plato-as-Socrates to third-person Socrates / composer-frame. 3 borderline headers ([0], [1], [5]) left alone. The drafted prompt-side architectural fix (HANDOFF_2026_04_28 §13) is **still pending for Scheherazade's Pass 0a** — see §3 Scheherazade row.

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
- `session_role_for_ai_assembly` rewrite landed in athens-2026 `fc233b8` (2026-04-26): removed "breakfast reading" digestible-content frame; added 3-bar test + framework-strain directive + "performing reception without being changed" failure mode.
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

- **Voice Pipeline Steps 1+2+3 + validation + continuity + card_assembly:** ✅ implemented v2 (2026-04-28; 2145 LOC; commits `180a18f`, `aca0e4c`, `fa88db7`)
- **Voice Pipeline v2 spec** at `docs/AI_Assembly_Voice_Pipeline.md` (1209 lines)
- **Publish layer** ✅ implemented (`runtime/flows/voice/publish.py` + `runtime/flows/publish_flow.py`; commit `ddec38a`)
- **Voice Pipeline dry-runs:** Plato solo on 2026-04-29 (3 formulations on "Legitimacy of the Invisible") + Plato + Cleopatra dual on 2026-04-30 — both successful, produced quality Socratic dialogues / prostagmata. Step 3 still pending — needs more voices for cross-voice amendment traffic.

This means: as soon as a voice's `07_persona_card_assembled.json` ships, runtime can consume it. Voice-build is the rate-limit.

---

## 15. Octopus compass rebuild (✅ COMPLETE, 2026-05-02)

**Status:** ✅ shipped to athens-2026 (`04da2c8`). Backup of pre-promotion state preserved at `~/Desktop/AI Assembly/archive/athens-2026_octopus_pre_compass_promotion_2026-05-02/`.

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

Source: `voices/MEMO_2026_05_01_recurrence_patterns_from_legitimacy_test.md` (full memo) + `projects/current-tests/voice-pipeline-dryrun/legitimacy_test_report.md`. Runtime thread ran multi-test exercise on the 4 shipped voices (Plato, Cleopatra, Dostoevsky, Battuta) with mock formulations on legitimacy / recognition / public-realm. 5 Step 2 artifacts per voice. Pipeline machinery checked out; voice-card patterns did not, fully cleanly. Four findings:

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

The compass-permissive Pass 0b template amendment (organism, committed `a6755d9`) supports postures 1 + 2 conditionally on voice_config.editorial_rationale. The system template already supports posture 3 natively. Future non-human voice rebuilds inherit this taxonomy.

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

**`voices/CLAUDIA_PINCHBECK_PERSONA_PREP_2026-05-03.md`** — self-contained handoff for fresh-session pickup. Carries: who Claudia is, source materials read, four reference traditions (Talk of the Town / TLS until 1974 / Borges / Manchester Guardian "London Letter"), prose-vs-attention split, one-spine-ten-bends principle, form-fit honesty rule, headline rule, 13 failure modes, canonical reference texts, corrected field distribution (formative_experience/character/translation_protocol all load-bearing — earlier underweighting corrected), open architectural questions (voice_mode, schema strain on artifact cluster), recommended hybrid pipeline workflow with Stages A-F, time + cost estimate (~7-9 hr wall, ~$20-40), what's not in scope.

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

## 22. 2026-05-03 evening session — Whanganui shipped + Scheherazade ROUND6 + Marley (c.1) code change

Three-voice parallel build session. State at session end:

### Whanganui River — ✅ SHIPPED via path-(b) at ROUND6
- 6 rounds of validator walk-through; converged to 3 architectural residuals (appropriation-safety language is load-bearing, not a defect).
- Operator-applied `_operator_review_passed.flag` to ship; all 3 Derive outputs present in `06_derive/` (provocateur_profile, runtime_card_minimal, chat_system_prompt).
- Mid-session reset: ROUND5 patches over-corrected appropriation-safety language; reverted to PRE-ROUND1 (post-auto-FIX baseline) per operator override before resuming.

### Scheherazade — 🟡 ROUND6 walk-through complete; run14 in flight
- Seale-Horta 2021 corpus acquired (operator-purchased Thalia DRM-free EPUB) → 14 chapters extracted to `01_primary_texts.json` (1.22M chars) for Pass 1d to curate. Fixes Burton/Lane register conflict that surfaced at FINAL gate.
- ROUND6 patches: kawa-typo fix (templated from Whanganui — caught by validator), Bencheikh French strip (`constitution[6]`), closing-frame `quotation_framing` add (`curated_corpus_passages[6]`).
- Per-fix decisions: [1][4][5] left as architectural (mediated-voice / dramatist-vs-speaker per §9 — third-person preserved); [2][3][6] patched.
- **§9 carry-over confirmed**: Scheherazade hits the same dramatist-vs-speaker collision as Plato. `banned_language[6]` and `banned_modes[7]` first-person rewrites were REVERTED to third-person; `characteristic_moves[5]` trailing meta-sentence ("The motif is the voice's own epistemology made visible") restored as third-person architectural meta.

### Bob Marley — 🟠 (c.1) code change landed; pipeline ready to walk through
- **(c.1) `personas/run_persona_pipeline.py` Pass 4a augment behavior** for `corpus_constraint=lyrics_patterns_only`. When this constraint is set AND `pass_1_6/reference_only_passages.json` exists, Pass 4a's `primary_block_for_voice` is built as: substitute (if Pass 1d output is the placeholder `[NO PRIMARY TEXTS...]`) or augment (concat Pass 1d corpus + reference passages). Pass 6 still uses original `primary_block` to preserve no-public-quotation contract (lyrics never make it into the curated_corpus_passages emitted to athens-2026).
- Initial implementation was REPLACE; operator caught and corrected to AUGMENT. The augment path concatenates with `=== ADDITIONAL CORPUS ... ===` separator so Pass 4a sees both the interview-curated pass-1d output and the 35 verbatim lyrics.
- DR §4 `[quote:]` blocks trimmed to get past Pass 1.4 content filter (deterministic content-policy refusal on verbatim lyrics in dossier text).
- 8 residuals queued for walk-through (apply dramatist-vs-speaker lens too — Marley songs are mediated; the lyrical "I" is performed-persona, not autobiographical).

### Architectural pattern confirmation: §9 mediated-voice spans 4+ voices
Plato (composer-vs-Socrates), Scheherazade (frame-tale teller-vs-tales-told), Marley (songwriter-vs-lyric-I), and Octopus (already shipped with two-channel JSON+prose contract) all instantiate the mediated-voice / dramatist-vs-speaker pattern. The drafted prompt-side architectural fix (HANDOFF_2026_04_28 §13) is now demonstrably load-bearing for ≥3 voices in this build cohort. Filing for Pass 2 epistemic_frame_statement + Pass 4a characteristic_moves + Pass 3 reasoning_method clarifications stays open as a v4.1 prompt change — but surgical patches at the gate continue to work.

### DR adaptive-thinking spot-test
Operator flagged concern that Whanganui/Scheherazade/Marley DR dossiers may have run on Opus 4.7 *without* extended thinking. Spot-test compared compass artifact (thinking explicitly ON) vs original DR Section 1 line-by-line: differences are sampling-variance level, not thinking-on/off level. Most likely explanation — both done with Research feature (auto-enables thinking); operator's "thinking off" recall was UI display difference. **Practical implication: original DR dossiers solid; cards built on them are valid; no need to redo Phase 0.5.**

### Snapshot preservation discipline
For each round of validator walk-through on each voice, the Pass 7a FINAL output is preserved as `07_persona_card_assembled.ROUNDN.json` before patches are applied. This is now standing practice for any walk-through with ≥3 rounds.
