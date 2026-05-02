# Voices — Open Items (authoritative, 2026-05-02)

**Scope:** EVERYTHING still open or undecided that pertains to the **persona pipeline / voice cards** for athens-2026. Distinct from the Voice Pipeline runtime (Steps 1+2+3) which has its own tracking.

**Date stamp:** 2026-05-01. Supersedes voice-related items in HANDOFF_2026_04_27.md, HANDOFF_2026_04_28.md, HANDOFF_2026_04_29.md (all variants), HANDOFF_2026_04_30.md if any, FU61_DRYRUN_VERDICT_2026_04_30.md, and the voice-relevant FUs in FOLLOW_UPS.md. Read this doc + ONBOARDING.md (sibling) instead of trawling those.

**Truth source:** When this doc disagrees with another, this doc is right (or fix this doc).

---

## 1. Per-voice build state

Panel is **10 voices** (per `athens-2026/panel_roster.json`).

| Voice | type | voice_mode | Hostile? | State | Notes |
|---|---|---|---|---|---|
| Plato | human | philosophical | false | ✅ shipped (with KNOWN defect) | Original-shipped; no FU#61-fresh re-emit. quality_criteria has the FU#61 inspiration line in #5. **Known defect:** dramatist-vs-speaker collision in 3 places — patches drafted in HANDOFF_2026_04_28 §13, never applied. See §9 below. |
| Cleopatra | human | observational | **true** | ✅ shipped | FU#61 v3 prompt-driven re-emission landed (`c89d186`+`54cd20a`). |
| Dostoevsky | human | narratival | false | ✅ shipped | Round 1 + 2 patches → path (b) → fresh quality_criteria patched-in (`5088d67`). |
| Battuta | human | narratival | false | ✅ shipped | Round 1 + 2 patches → path (b). Voice files **untracked** in athens-2026 git. |
| Octopus | non_human | observational | false | ✅ shipped 2026-05-01 (`8bb9981` + `4cff85b`); 🔄 **compass rebuild in progress 2026-05-02** in current-tests sandbox. See §15 below. |
| Hannah Arendt | human | philosophical | false | 🟡 Pass 0a + Phase 0.5 done (in current-tests); DR prompts ready for claude.ai paste |
| Ada Lovelace | human | philosophical | false | 🟡 Pass 0a + Phase 0.5 done; DR prompts ready for claude.ai paste |
| Bob Marley | human | **narratival** | false | 🟡 Pass 0a + Phase 0.5 done; voice_mode flipped observational→narratival (Pass 0a hallucinated Card v2 reference per ONBOARDING DO-list); DR prompts ready for claude.ai paste; lyrics_patterns_only corpus_constraint (atypical) |
| Whanganui River | non_human | system / null | false | 🟡 Pass 0a done; voice_config rewritten **transmission-faithful** (Tupua te Kawa verbatim + Te Pou Tupua mediation); Phase 0.5 in flight at session end. See §17 below. |
| Scheherazade | fictional | narratival | false | 🟡 Pass 0a done (auto-default voice_config; null editorial_rationale); Phase 0.5 in flight at session end. Mediated-voice concern carries through to Pass 2 generation. |
| Whanganui River | non_human | observational (likely) | (TBD) | ❌ not started | Hardest case — non-human/system; the river constructed via human observation/legal status. |
| Scheherazade | fictional | narratival (likely) | false | ❌ not started | **Mediated-voice prompt fix** flagged in earlier session — verify status pre-build. |

### Voice-mode coverage so far

- philosophical: 1 (Plato)
- narratival: 2 (Dostoevsky, Battuta)
- observational: 2 (Cleopatra, Octopus — both shipped)

Going forward, classification calls for the 5 unbuilt voices land via Pass 0a but **operator must check each call independently** — voice_mode is a *construction* decision (how the pipeline builds the voice), not a *historical* one. Don't take Pass 0a's first proposal as final without weighing irreplaceability against the panel.

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

## 3. Five unbuilt voices — operator-bounded work

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

**Per-voice flags worth checking before starting:**

| Voice | Pre-build attention |
|---|---|
| Hannah Arendt | Probably philosophical — FU#49 universal patterns should hold. FU#47 voice-fit: ✓ analytical-workshop. **Pass 1d will pull richer primary-text excerpts** (FU#46 raised budget 30K→60K for richer-corpus voices like Plato/Arendt); expect more anchored claims than early-Plato runs. |
| Ada Lovelace | Mathematical-notation density — FU#61 audience-engagement criterion may benefit (named in FU#61 expansion). FU#47 voice-fit: ✓ analytical-workshop. Candidate for FU#15 Pass 5 A/B test (low-stakes voice). |
| Bob Marley | **Audio render question** — medium is song; runtime layer needs Suno API integration (NOT persona-build scope, flag-up). **Special `corpus_constraint: lyrics_patterns_only`** (atypical — not `full`). FU#47 voice-fit: ⚠ awkward (lyric-rhythmic). Card-side FU#61 audience-engagement will land in Patois/lyric grammar. |
| Whanganui River | **Hardest case** — non-human + no first-person source + legal-personhood-as-frame. Construction-mode question is real (translate-into-human-categories vs preserve-river-grammar). May trigger same layer-instability as Octopus. **Pre-build attention:** Pass 0a originally proposed `hostile_sources: false`; operator's pipeline-fidelity audit later flagged it might need `true`. **Verify hostile_sources on Pass 0a output before Phase 0.5.** Also: voice_mode `null` is valid (subtype=system) — but check what Pass 0a proposes. FU#47 voice-fit: ⚠ awkward (legal-personhood-from-Indigenous-tradition). Plan to budget extra patch rounds. |
| Scheherazade | **Mediated-voice prompt fix** — verify status before Pass 0a. Flagged in earlier session; never resolved. Concerns how the frame-tale form (story-within-stories) gets handled in `voice_mode: narratival`. **Same dramatist-vs-speaker collision risk as Plato** (composer vs speakers within compositions). Either land the prompt-side mediated-voice clarification before her Pass 0a, OR plan for surgical patches at the gate. FU#47 voice-fit: ⚠ awkward (frame-narrative + character-distributed). FU#46 may apply (rich primary-text corpus → 60K excerpt budget). |

---

## 4. Voice-relevant FUs still open (consolidated from FOLLOW_UPS.md)

### Active / conditional

**FU#55 — Form-variance test, rolling per-voice (Pass 4b fork-test pattern)** 🟡 IN PROGRESS
- Plato + Cleopatra populated (both declined permission)
- 8 voices remaining (now 7: Octopus done; Battuta done; 5 unbuilt + Octopus pending decision)
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

## 9. NEWLY DISCOVERED — Plato dramatist-vs-speaker collision UNFIXED on shipped card

**Status:** real defect in shipped Plato card; patches drafted in HANDOFF_2026_04_28 §13 but never applied.

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

### Rebuild backup snapshots preserved

- `voices/octopus_pre_compass_rebuild_2026-05-01/` (full athens-2026 shipped state — 93 files, 9.1MB)
- `voices/octopus/01_research/03_dr_prompts.surgical_v1/` (manual surgical edits before template amendment)
- `voices/octopus/01_research/03_dr_prompts.v2_partial/` (auto-generated before §6 amendment)
- `voices/octopus/01_research/01_perplexity_dossier.pre_6layer.json` (research output before voice_config 6-layer rewrite)
- `voices/octopus/07_persona_card_assembled.pre_*.json` × 3 (Path A patches / FU#61-fresh / compass rebuild)

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
