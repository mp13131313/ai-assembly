# Voices — Open Items (authoritative, 2026-05-01)

**Scope:** EVERYTHING still open or undecided that pertains to the **persona pipeline / voice cards** for athens-2026. Distinct from the Voice Pipeline runtime (Steps 1+2+3) which has its own tracking.

**Date stamp:** 2026-05-01. Supersedes voice-related items in HANDOFF_2026_04_27.md, HANDOFF_2026_04_28.md, HANDOFF_2026_04_29.md (all variants), HANDOFF_2026_04_30.md if any, FU61_DRYRUN_VERDICT_2026_04_30.md, and the voice-relevant FUs in FOLLOW_UPS.md. Read this doc + ONBOARDING.md (sibling) instead of trawling those.

**Truth source:** When this doc disagrees with another, this doc is right (or fix this doc).

---

## 1. Per-voice build state

Panel is **10 voices** (per `athens-2026/panel_roster.json`).

| Voice | type | voice_mode | Hostile? | State | Notes |
|---|---|---|---|---|---|
| Plato | human | philosophical | false | ✅ shipped | Original-shipped; no FU#61-fresh re-emit. quality_criteria has the FU#61 inspiration line in #5. |
| Cleopatra | human | observational | **true** | ✅ shipped | FU#61 v3 prompt-driven re-emission landed (`c89d186`+`54cd20a`). |
| Dostoevsky | human | narratival | false | ✅ shipped | Round 1 + 2 patches → path (b) → fresh quality_criteria patched-in (`5088d67`). |
| Battuta | human | narratival | false | ✅ shipped | Round 1 + 2 patches → path (b). Voice files **untracked** in athens-2026 git. |
| **Octopus** | non_human | observational | false | ⏸ **paused at FU#53 gate** | Layer-instability finding; path A/B/C decision deferred. |
| Hannah Arendt | human | (TBD) | (TBD) | ❌ not started | Phase 0a + 0.5 + DR + pipeline. Likely philosophical. |
| Ada Lovelace | human | (TBD) | (TBD) | ❌ not started | Likely narratival or observational. |
| Bob Marley | human | (TBD) | (TBD) | ❌ not started | Likely narratival (song-as-witness). |
| Whanganui River | non_human | observational (likely) | (TBD) | ❌ not started | Hardest case — non-human/system; the river constructed via human observation/legal status. |
| Scheherazade | fictional | narratival (likely) | false | ❌ not started | **Mediated-voice prompt fix** flagged in earlier session — verify status pre-build. |

### Voice-mode coverage so far

- philosophical: 1 (Plato)
- narratival: 2 (Dostoevsky, Battuta)
- observational: 2 (Cleopatra, Octopus)

Going forward, classification calls for the 5 unbuilt voices land via Pass 0a but **operator must check each call independently** — voice_mode is a *construction* decision (how the pipeline builds the voice), not a *historical* one. Don't take Pass 0a's first proposal as final without weighing irreplaceability against the panel.

---

## 2. Octopus — DEFERRED architectural decision (highest-priority open item)

Pass 7a FINAL flagged **layer instability**: card alternates between (a) Pass 2's translation-honest no-reader frame and (b) Pass 4b's scholar-dispatcher-with-citations frame. Six specific field issues identified.

**Three paths proposed (ONE must be chosen):**

| Path | Description | Cost |
|---|---|---|
| **A** — surgical compromise | Patch the 6 flagged fields in second-person imperative; drop scholar-name leakage in `translation_protocol` Step 5 + `medium`; fix register breaks in `character`/`length_and_format_constraints`/`characteristic_output_structure`/`metaphorical_repertoire.hold-the-gap`. Re-validate via path (a). | ~30 min, no API |
| **B** — Pass 2 rebuild | Pick one frame for who's speaking (α austere translation-honest / β mediated-by-scientist / γ second-person-imperative compromise); cache-invalidate from Pass 2; re-run Pass 2-7. | ~30-60 min, ~$8-15 |
| **C** — accept residuals via flag | `touch _operator_review_passed.flag`, ship. Card has known register flags. | immediate |

**My read (from session): Path A.** Reasons:
- The §5 philosopher-tailoring intentionally grounded Octopus in Birch / Despret / Lestel / Hochner / Mather / Hanlon / Godfrey-Smith — that depth lives in the substrate (`concept_lexicon`, `constitution`, `topics_requiring_care`, `hard_limits`). It does NOT need to surface as runtime scholar-naming.
- Briefing v3.1 Layer 2 demands "an octopus thinking about agency the way an octopus thinks about agency, not a human rhetorical performance about octopuses." Scholar-dispatcher mode IS the failure-mode the briefing names.
- Path A separates substrate (philosophical depth, preserved) from emission (translation-honest voice). Validator's recommended fix matches Path A literally.
- Path B is more invasive than needed; Path C ships a card that will fail Layer 2 on a meaningful fraction of runtime artifacts.

**Surgical patch text drafted but NOT applied** — see session transcript for the exact field-by-field patch proposals.

**Status:** awaiting operator decision. Octopus's card on disk; pipeline paused at gate. Backup at `voices/octopus/07_persona_card_assembled.json` (not at canonical pre-test backup pattern — this is the current state).

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
| Hannah Arendt | Probably philosophical — FU#49 universal patterns should hold |
| Ada Lovelace | Mathematical-notation density — FU#61 audience-engagement criterion may benefit (Lovelace was named in FU#61 expansion) |
| Bob Marley | **Audio render question** — Marley's medium is song; runtime layer needs Suno API integration (NOT persona-build scope but flag-up). Card-side: FU#61 audience-engagement criterion will land in Patois/lyric grammar. |
| Whanganui River | **Hardest case** — non-human + no first-person source + legal-personhood-as-frame. Construction-mode question is real (translate-into-human-categories vs preserve-river-grammar). May trigger same layer-instability as Octopus. Plan to budget extra patch rounds. |
| Scheherazade | **Mediated-voice prompt fix** — verify status before Pass 0a. Flagged in earlier session; never resolved. Likely concerns how the frame-tale form (story-within-stories) gets handled in `voice_mode: narratival`. |

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

## 6. Cleanup / hygiene gaps

### athens-2026 git tracking
- **Battuta:** entire voice folder UNTRACKED (245+ pipeline files). Plato is the reference pattern.
- **Dostoevsky:** card + chat artifact tracked (from `5088d67`); ~240 pipeline files UNTRACKED.
- **Octopus:** intake + DR prompts tracked; merge / corpus / generation / validation / assembled card UNTRACKED.
- **Cleopatra:** main artifacts tracked; snapshots (`*.pre_*.json`) untracked.
- **Plato:** clean (full pipeline trail tracked, ~245 files).

**Action:** sweep-commit Dostoevsky + Battuta + Octopus pipeline trails. Match Plato pattern (245 files per voice). ~700 files total.

### athens-2026 `.gitignore` gaps
Plato's tracked set excludes — but current `.gitignore` doesn't list — the following, which are now accumulating across voices:
- `_pipeline_logs/` (per-voice run logs)
- `*.pre_*.json` (operator-patch snapshots: `pre_FU61.json`, `pre_test.json`, `pre_round1_patches.json`, `pre_round2_patches.json`, `pre_freshqc.json`, `pre_v3_qc_test.json`, `pre_freshrun.json`)
- `_operator_review_passed.flag`

**Action:** add these to athens-2026 `.gitignore` before sweep-commit, so they don't enter history.

### `/tmp/` cleanup material
- `/tmp/standalone_pass4b_test.py` (the standalone test script — useful pattern; could move to `personas/scripts/` if we want to keep it)
- `/tmp/pass4b_test_*.json` (4 fresh-test outputs — empirical-comparison data; can be deleted, the FU#61 verdict captures findings)
- `/tmp/pass4b_test_*.log`
- `/tmp/anthropic_thinking_truth*.py` (older diagnostic scripts from FU#60 work)

**Action:** delete `/tmp/pass4b_test_*` files; consider promoting `standalone_pass4b_test.py` to `personas/scripts/standalone_pass_test.py` if useful for future per-pass empirical work.

### Code repo (athens) tracking gaps
- `docs/AI_Assembly_Frame_Concept_v1.md` — was committed by other thread; verify current state
- LLM_CALL_INVENTORY.md stale since 04-27 — needs update for FU#57/58/59/60/61

### Documentation drift
- "Phase L sign-off" framing — operator explicitly said to drop it. Sweep references in:
  - HANDOFF_2026_04_27.md
  - HANDOFF_2026_04_27_evening.md
  - HANDOFF_2026_04_28.md
  - HANDOFF_2026_04_29.md (and LATE / NIGHT variants)
  - ONBOARDING.md (line 96 mentions "Phase L empirical: 4.6 produces reader's-intro on §6" — also stale: operator now uses 4.7 across §1-§6)
- HANDOFF_2026_04_29_*.md docs are stale since major FU#61 work landed since
- Old voice-pipeline-runtime handoffs (DRYRUN, DUAL_DRYRUN) — unrelated to persona-build; keep under runtime tracking, not voices/

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

## 9. What's NOT in this doc

- **Voice Pipeline runtime** (Steps 1+2+3 — the night-to-morning artifact-generating runtime). Tracked separately. Voices' chat artifact + assembled card are the persona-build deliverable; how the runtime *uses* them is a different domain.
- **Frame Concept** doc and downstream design (other thread's territory).
- **Microsite / admin console / closing-show** — Athens-blockers but not voice-build.
- **Provocateur Pipeline** — different stage of the project.

For those, see ONBOARDING.md (sibling) for pointers + non-voice docs in `_workspace/planning/`.
