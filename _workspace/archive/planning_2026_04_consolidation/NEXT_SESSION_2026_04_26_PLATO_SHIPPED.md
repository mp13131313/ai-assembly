# Next session — authoritative pickup doc (2026-04-26)

**Supersedes for next-session tracking:** `NEXT_SESSION_2026_04_25_PLATO_DR_INFLIGHT.md` (yesterday morning's pickup, pre-pipeline-run).
**Branch:** `arch-03-additive-merge` at HEAD `bf49a0a` (pushed to `origin/arch-03-additive-merge` 2026-04-25/26).
**Status:** Plato CARD COMPLETE; chat-test validated empirically; pipeline improvements landed for voices 3–12. Voice 3 is the next operational step.
**Tests:** 212/212 passing. ~125 commits ahead of `origin/main`.

---

## READING ORDER

**Required:**

1. **THIS doc** — self-contained for operational pickup.

**Load-bearing backup references:**

2. `_workspace/planning/FOLLOW_UPS.md` — per-FU# tracker, updated 2026-04-26 with FU#42 (split-card direction), FU#43 (Pass 6 corpus_metadata hardening), FU#44 (patcher register-drift extension), FU#45 (cache helper), FU#46 (Pass 1d budget bump).
3. `_workspace/planning/NEXT_SESSION_2026_04_25_PLATO.md` — older pickup; SECTION 3 (pipeline shape) + ADDENDUM (Athens-piece interpretation) still live reference.

**Historical-only — IGNORE unless investigating WHY:**

All other `_workspace/planning/HANDOFF_*` docs are archival.

---

## ONBOARDING PROMPT (copy-paste into fresh session)

```
You are resuming the AI Assembly persona-pipeline project on branch
arch-03-additive-merge. Plato CARD COMPLETE 2026-04-25 (third re-run);
chat-test validated empirically 2026-04-26; today's pipeline improvements
have landed for voices 3-12. Voice 3 is the next operational step.

Model: Opus 4.7 + adaptive thinking is right for architectural decisions
(if any FU re-activates) and for assessing voice-3 outputs. Mechanical
voice-3 pipeline operation + chat-test paste-and-assess is Sonnet-shaped
— flag if operator prefers cheaper model for that phase.

FIRST ACTIONS:

1. Read _workspace/planning/NEXT_SESSION_2026_04_26_PLATO_SHIPPED.md
   in full. That is THIS doc — the authoritative pickup point.

2. Read _workspace/planning/FOLLOW_UPS.md (per-FU# tracker, updated
   through 2026-04-26 with FU#42-#46).

3. Verify repo state:
   cd "/Users/aienvironment/Desktop/AI Assembly/code"
   git log --oneline origin/main..HEAD | head -20
   git status
   cd personas && venv/bin/python -m pytest tests/ -x -q
   (Expect: ~125 commits ahead of origin/main; working tree clean
    except _workspace/arch_03_baseline_snapshot/; 212/212 tests pass.)

4. Verify Plato is shipped:
   ls "/Users/aienvironment/Desktop/AI Assembly/projects/phase-l-plato/voices/plato/"
   - Should show: 07_persona_card_assembled.json + 06_derive/{00,01,02,03}.json
   - Card status: REVISION_NEEDED + human_review_pending (expected;
     does not block deployment — see SECTION 2 caveats)

5. Decide first operational action:
   - Voice 3 startup (default) — pick a voice from panel_roster.json,
     run Phase 0.5 then full pipeline
   - OR: Plato production-quality iteration (optional; see SECTION 3)
   - OR: split-card architectural work (FU#42; conditional on
     audience-brief stability — see SECTION 4)

DO NOT:
- Re-run Plato unless operator explicitly asks. Card is shipped per
  empirical chat-test validation 2026-04-26. Validation report shows
  REVISION_NEEDED + 50 UNVERIFIED + 6 field_issues + 7 boddice_flags
  + 1 INCONSISTENT — these are advisory; runtime behavior validated.
- Re-run Dostoevsky (Phase 2 + G10 Derive re-fire are on disk; re-run
  would cost $18+ without adding signal).
- Push to origin/main without explicit operator confirmation. The
  arch-03-additive-merge push is up to date.
- Use Opus 4.6 for §6 of any voice's DR. Per model-per-section policy
  §6 = Opus 4.7. (§1-§5 = Opus 4.6, mixed-staging acceptable per
  Plato precedent.)
- Modify xattrs / ACLs / system attributes without explicit ask. (Standing rule.)

KEY FILES:
- Authoritative planning: this doc
- Per-FU tracker: _workspace/planning/FOLLOW_UPS.md
- Pipeline orchestrator: personas/run_persona_pipeline.py
- NEW Pass 6.5-clean (FU#33 P1 amended): personas/flows/shared/bracket_strip.py
  — runs after Pass 6, BEFORE Pass 7-pre. Strips schema-taxonomy +
  EvidenceTag + curator-note tags. PRESERVES boddice tags
  ([experiential_reconstruction], [projection_warning:]) inline.
- Chat artifact builder (FU#41 Amendment A + B): personas/flows/shared/chat_prompt_builder.py
  — strips 11 fields (5 chat-incompatible + 5 spec-shell + 1 nested
  corpus_metadata). Voice-constitutional fields preserved.
- Patcher (FU#13 + FU#44 register-drift extension): personas/flows/shared/prompts/persona_pass_7a_fix.md
- Pass 1d (FU#46 60K budget): personas/flows/shared/prompts/persona_pass_1d_excerpt_selection.md
- Pass 6 (FU#43 corpus_metadata hardening): personas/flows/shared/prompts/persona_pass_6_corpus.md
- Cache invalidation helper (FU#45): personas/scripts/invalidate_cache.py

If unsure, this doc's SECTION 3 has voice-3 startup steps; SECTION 4
has the architectural decision points.
```

---

## SECTION 1 — WHAT LANDED 2026-04-25/26

10 commits, all pushed to `origin/arch-03-additive-merge`:

```
bf49a0a feat(personas): pipeline improvements for voices 3-12 (#4, #5, #6)
0031c91 fix(personas/Pass-6.5-clean): FU#33 P1 amendment — preserve boddice tags + reorder
cba8fc5 feat(personas/pass_1d): bump excerpt budget 30K→60K (richer-corpus voices)
6c0daf5 feat(personas/Pass-7d-clean): FU#33 P1 — bracket-tag residue strip
2cbbff6 fix(personas/chat_prompt_builder): amendment B — spec-shell suppression
aa4ce85 fix(personas/chat_prompt_builder): amend FU#41 strip set 10→5 fields
736979d docs(planning): handoff for 2026-04-25+ pickup (Plato DR in flight)
177365e docs(archive/session-artifacts): external Dostoevsky-card evaluation session
4ebb9d6 docs(planning/FOLLOW_UPS): Plato DR session-time observation under FU#29
ebe4aa6 fix(personas/pass_0b_header): restore 'Research [name] comprehensively...' intro in per-section §1
```

### Pipeline improvements (FU#42–#46)

| FU# | What | Effect for voices 3-12 |
|---|---|---|
| FU#42 | Split-card direction (post-Athens, conditional) | Plato-for-Athens-2026 vs hypothetical 2027 = cheap deployment swap. Architectural; deferred. |
| FU#43 | Pass 6 prompt — `corpus_metadata` cleanliness hardening | Pass 6 emits minimal corpus_metadata at source; patcher doesn't re-trim per voice |
| FU#44 | Patcher prompt — register-drift detection patterns | Patcher catches "the corpus" / "[Voice]ian person" / "[Voice] held that..." rewrites + internal-contradiction patches |
| FU#45 | `scripts/invalidate_cache.py` cache helper | Operator iteration cycles use helper instead of manual `rm -f` (no silent path mismatches) |
| FU#46 | Pass 1d budget bump (30K → 60K) | Richer-corpus voices (Plato, Arendt) anchor more claims to primary text |

### FU#41 chat artifact (Amendments A + B)

- **A** (`aa4ce85`): chat strip 10 → 5. Preserves voice-constitutional fields (`medium`, `characteristic_output_structure`, `length_and_format_constraints`, `technical_capabilities`, `relationship_to_detailed_response`).
- **B** (`2cbbff6`): chat strip 5 → 11. Adds spec-shell meta strip (`voice_name`, `voice_mode`, `pipeline_version`, `generated_date`, `council_member_name`) + nested `curated_corpus_passages.corpus_metadata`.

### FU#33 P1 bracket-strip module

- **Initial** (`6c0daf5`): bracket strip + Pass 7d-clean placement.
- **Amendment** (`0031c91`): preserve boddice tags + reorder strip to Pass 6.5-clean (BEFORE validators). Validators see cleaned content from start; reports reflect shipped state.

---

## SECTION 2 — PLATO STATE (shipped)

### Card

- `voices/plato/07_persona_card_assembled.json` — 36 fields, 147,690 bytes
- `voices/plato/06_derive/01_provocateur_profile.json` — 9 fields (runtime council_config feed)
- `voices/plato/06_derive/02_evaluation_rubric.json` — 3 identity / 3 reasoning / 3 stress tests
- `voices/plato/06_derive/03_chat_system_prompt.json` — 34 fields (chat-test target, FU#41 Amendments applied)

### Validation report (final state)

- **validation_status:** REVISION_NEEDED
- **human_review_status:** pending
- **Output Register check:** CLEAN (0 violations) ✅
- **Patches applied:** 11/11 (failed: 0, skipped: 0)
- **Pass 7-pre items:** 146 verified=88 unverified=50 dossier_only=5 interpretive=2 inconsistent=1 boddice_tag_flags=7
- **Pass 7a field_issues:** 6 (down from 15 pre-fix)

### Empirical chat-test (2026-04-26)

Operator pasted the FU#41 Amendment A+B chat artifact into a Claude project + Athens-program HTML file + asked "they coming to Athens?" probe. Two thinking traces captured.

**Persona-take-hold: validated.** Both traces show first-person inhabitation ("the user is asking **me, as Plato**, how I feel about this gathering coming to **my city**"). Prior failure mode ("the user is roleplaying as Plato") absent. Translation_protocol applied generatively. Artifact-spec honored (350-550 word dialogue, in medias res, aporia/myth close, Greek vocab, no modern jargon).

**Output substantively Platonic:**
- Doctor-cook distinction from *Gorgias* 462b–466a invoked (in card's curated_corpus_passages)
- Phaidros / unnamed Academy companion as interlocutor
- Pnyx tour acknowledged with wry recognition
- AIssembly overnight machines registered
- Funeral-march-for-democracy + widen-democracy contradiction caught
- Conditional welcome: "I welcome the coming the way one welcomes guests whose true nature remains unknown"
- Audience-priming working: kalon/agathon distinction surfaces naturally; engagement_topics align with WBBF themes

### Validation caveats (NOT blocking deployment)

The validation report's HIGH/MED concerns are **advisory** post-empirical-chat-test:

- **6 Pass 7a field_issues** — register-drift items the patcher missed (FU#44 will help voices 3-12). For Plato: hand-editable but chat-test passed regardless.
- **50 UNVERIFIED Pass 7-pre claims** — well-attested Platonic doctrines unanchored to specific primary text excerpts (Pass 1d cache-hit at 30K budget on this run; FU#46 60K applies to voices 3-12). Voice Pipeline runtime injects these as claims; the runtime LLM has dossier context from `merged_dossier` to compensate. Chat-test confirmed runtime behavior is voice-faithful.
- **7 boddice_tag_flags** — Plato is in a one-time post-strip state where biocultural tags were stripped before FU#33 P1 amendment landed. Voices 3-12 will not have this. For Plato: lost biocultural-discipline annotations are a marginal runtime quality cost; chat-test confirms voice still inhabits + applies translation_protocol correctly.
- **1 INCONSISTENT** — minor Pass 7-pre flag; first INCONSISTENT case Plato has surfaced. Could empirically motivate FU#33 P2 (INCONSISTENT-flag wiring into patcher), but trigger has not yet justified the work.

**Operator decision: shipped.** Voice 3 is the next operational step.

---

## SECTION 3 — VOICE 3 NEXT-STEP CHECKLIST

### Pre-flight

1. **Pick voice from `panel_roster.json`:**
   ```
   Plato ✓ shipped
   Cleopatra
   Ibn Battuta
   Scheherazade
   Ada Lovelace
   Fyodor Dostoevsky ✓ Phase 2 done
   Hannah Arendt
   Bob Marley
   Audrey Tang
   Peter Thiel
   Whanganui River
   Octopus
   ```

2. **Decide on project location** — likely `projects/phase-l-<slug>/` per Plato precedent (Tier 3 separation; outside `code/` repo).

3. **Set up voice-specific intake** at `voices/<slug>/00_intake/02_voice_config.json`:
   - Phase B shape: name, type, subtype, voice_mode, hostile_sources, corpus_constraint, manual_grounding, wikipedia_url, editorial_rationale
   - DO NOT include `primary_text_sources` legacy field unless deliberately overriding the 1-arch-07 auto-derive path.

### Phase 0.5 (research)

4. Run Pass 0a (voice config validation), Pass 1a (Perplexity), Pass 1b (Gemini), Pass 0b render + tailor.

5. Manual claude.ai DR §1–§6 sessions:
   - **§1–§5: Opus 4.6** (per model-per-section policy)
   - **§6: Opus 4.7** (per model-per-section policy)
   - Mixed-staging acceptable per Plato precedent (4.7 §1+§2+§4+§5+§6 + 4.6 §3 was operator's chosen mix). For voice 3: pick policy fresh per voice (not all voices need 4.7 dominance).

6. Save sections at `voices/<slug>/01_research/04_dr_dossier/0N_section_N.md`.

### Pipeline run

7. **Cache-aware command:**
   ```bash
   cd "/Users/aienvironment/Desktop/AI Assembly/code"
   set -a && source .env && set +a
   cd personas
   venv/bin/python run_persona_pipeline.py "<Voice>" \
     --project "/Users/aienvironment/Desktop/AI Assembly/projects/phase-l-<slug>"
   ```

8. **Manual gate at Pass 1c:** review `03_corpus/04_primary_texts_review.md`, optionally curate `03_corpus/01_primary_texts.json` (drop junk entries; add canonicals if missing — see Plato precedent for Laws/Statesman additions). `touch 03_corpus/03_primary_texts_reviewed.flag` to continue.

9. **Pipeline auto-runs through Pass 6.5-clean (NEW)** + Pass 7-family + Derive + assembly. ETA ~2h, ~$18-22 for rich-corpus voices.

### Post-run

10. **Read CARD COMPLETE summary.** Voice 3 should show LOWER bracket residue counts than Plato (Pass 6.5-clean runs BEFORE validators on this voice).

11. **Chat-test:** paste `06_derive/03_chat_system_prompt.json` into Claude project. Probe in Provocateur-register first (e.g. "You've just received the program for the AIssembly panel in Athens..."), philosophical-meditation register second. Per `8057961`, exercise both Sonnet AND Opus model modes.

12. **Compare to Plato:**
    - Pass 7-pre verification ratio (verified/items)
    - Pass 7a field_issues count (should be lower with FU#44 patcher extension)
    - Boddice_tag_flags (should be 0 — boddice tags preserved inline now)

### Cache-invalidation tool (FU#45)

If voice 3 needs partial re-run:

```bash
# List path map
venv/bin/python scripts/invalidate_cache.py --list

# Single pass
venv/bin/python scripts/invalidate_cache.py --voice <slug> --project <path> --pass 1d --dry-run

# Cascade from a pass
venv/bin/python scripts/invalidate_cache.py --voice <slug> --project <path> --from-pass 5
```

---

## SECTION 4 — ARCHITECTURAL DECISION POINTS

### FU#42 split-card direction

- **Operationally-useful half:** voice-card / deployment-card schema-level distinction. Enables cheap deployment swapping (Plato-for-Athens vs Plato-for-2027), guarantees voice consistency across deployments, makes audience-brief iteration ~5-8× cheaper.
- **Retracted half:** voice-card prose-flatten. Was chat-test motivation only (JSON-wrapper-as-spec-signal). Voice Pipeline cherry-picks fields via API; never reads card as one document. No production benefit.
- **Trigger options:**
  1. **Post-Athens (default):** voices 3-12 ship under Card v2; migrated to v3 alongside Dosto + Plato post-deadline.
  2. **Pre-Athens IF audience-brief iteration becomes substantive:** 5+ iterations between now and May 7 would justify the architectural cost.
  3. **Partial pre-Athens slice:** just the audience-aware regeneration path (Pass 5 + Pass 4b-deployment + Pass 6-deployment) ≈ 3-4 days; defers full split.
- **Cost:** ~1-2 weeks for full split; ~3-4 days for partial slice.
- **Default decision: defer to post-Athens.** Today's `scripts/invalidate_cache.py --from-pass 5` provides partial-rerun-from-Pass-5 capability at ~$60-96 / 5h for 12-voice panel. Adequate unless audience iterates heavily.

### Plato production-quality iteration (optional)

If operator wants Plato's validation report to look better (REVISION_NEEDED → PASS, fewer UNVERIFIED), three sub-options ranged earlier:

- **A. Regenerate Pass 2-6 to restore boddice tags** (~$15-20, 45 min). Plato's chunks lose post-strip biocultural annotations; full regen would re-emit them, then new Pass 6.5-clean preserves them.
- **B. Corrected Pass 1d invalidation** (`scripts/invalidate_cache.py --voice plato --project ... --from-pass 1d`) → 60K budget applies → fewer UNVERIFIED. ~$5, 30 min.
- **C. Re-run Pass 7a + 7a-FIX with new patcher prompt** (`bf49a0a`) → catches more register-drift. ~$2, 10 min.

Empirical chat-test passed without these; they're polish for the validation report. Operator call.

### FU#33 P2 (INCONSISTENT-flag wiring)

Plato's latest run surfaced 1 INCONSISTENT — first empirical case across Dosto + Plato. Was deferred pending trigger. Trigger may have just fired, but signal is minor (1 case). Consider activating only if voice-3 also surfaces INCONSISTENT.

---

## SECTION 5 — REPO STATE SNAPSHOT (2026-04-26)

- **Branch:** `arch-03-additive-merge`
- **HEAD:** `bf49a0a`
- **Ahead of origin/main:** ~125 commits
- **Pushed to origin/arch-03-additive-merge:** all today's commits
- **Tests:** 212/212 passing (was 162 at session start; +50 across the session: +18 splice + +21 bracket_strip + +4 chat_prompt_builder amendments + +7 misc)
- **Working tree:** clean except `_workspace/arch_03_baseline_snapshot/` (FU#11 cleanup gated on Phase L sign-off)

### Plato project state (outside git per Tier 3)

- `voices/plato/00_intake/02_voice_config.json` ✓
- `voices/plato/01_research/01_perplexity_dossier.json` ✓
- `voices/plato/01_research/02_gemini_broad_scan.json` ✓
- `voices/plato/01_research/03_dr_prompts/` (6 sections + tailoring notes) ✓
- `voices/plato/01_research/04_dr_dossier/` (mixed 4.7/4.6 staging: §1+§2+§4+§5+§6 from 4.7, §3 from 4.6) ✓
- `voices/plato/02_merge/` (Pass 1.1–1.7 + dossier + coherence audit + fix log) ✓
- `voices/plato/03_corpus/` (4.24MB curated corpus: 22 substantive Perseus + 2 full-Jowett Republic/Laws/Statesman) ✓
- `voices/plato/04_generation/` (Pass 2-6 + CT compresses) ✓
- `voices/plato/05_validation/` (Pass 7-family) ✓
- `voices/plato/06_derive/` (4 artifacts: derive_raw + provocateur_profile + evaluation_rubric + chat_system_prompt) ✓
- `voices/plato/07_persona_card_assembled.json` ✓
- `voices/plato/_run_logs/2026_04_25_pipeline_full.log` (full run history)

---

## SECTION 6 — KEY FILES + DON'TS (consolidated)

### Authoritative

- This doc — pickup and onboarding
- `_workspace/planning/FOLLOW_UPS.md` — per-FU# tracker (updated through FU#46)

### Code touched 2026-04-25/26

- `personas/flows/shared/bracket_strip.py` — FU#33 P1 module (boddice-preserving)
- `personas/tests/test_bracket_strip.py` — 21 tests
- `personas/flows/shared/chat_prompt_builder.py` — FU#41 Amendments A + B
- `personas/tests/test_chat_prompt_builder.py` — 18 tests
- `personas/run_persona_pipeline.py` — Pass 6.5-clean integration (after Pass 6, before Pass 7-pre)
- `personas/flows/shared/prompts/persona_pass_1d_excerpt_selection.md` — 60K budget
- `personas/flows/shared/prompts/persona_pass_6_corpus.md` — corpus_metadata cleanliness
- `personas/flows/shared/prompts/persona_pass_7a_fix.md` — register-drift extension + internal-contradiction patches
- `personas/scripts/invalidate_cache.py` — cache-invalidation helper

### DON'TS

- **No Plato re-run** without explicit operator ask. Card shipped per chat-test validation.
- **No Dostoevsky full re-run.** Phase 2 + G10 Derive re-fire are on disk.
- **No `--no-verify` / hook bypass.** If a hook fails, fix the underlying issue.
- **No push to origin/main without explicit operator confirmation.**
- **No Opus 4.6 for §6 of any voice's DR.** Per model-per-section policy.
- **No xattr / ACL / system-attribute modification** without explicit operator instruction.
- **No deletion of `_workspace/arch_03_baseline_snapshot/`** until Phase L sign-off.
- **Voices 3-12 should NOT need manual chat-artifact curation** — FU#41 Amendments A + B + FU#33 P1 amendment + FU#43 + FU#44 + FU#46 should produce clean shipped artifacts from the pipeline. If a voice's chat-test fails, diagnose specifically; don't fall back to Plato-style hand-editing.

---

## SECTION 7 — CALIBRATION FOR PICKUP

If picking this up cold:

- **Operator preference is direct.** When they push back ("are you sure?", "reason through each again"), the instinct is usually right even when Claude has declared work done. This session caught multiple over-pitches (chat-only motivations applied to Voice Pipeline; mistargeted cache invalidation paths) via operator pushback. Re-investigate before bulldozing.
- **Tier 3 separation.** `code/` is the git repo. `projects/` is sibling outside the repo. Voice data lives in `projects/phase-l-<slug>/`, not `code/projects/...`.
- **Reflections are vendor JSON, not audio.** (Standing memory.)
- **Provotype framing is load-bearing.** This is a civic-design artefact for the World Beautiful Business Forum (Athens, May 7-10 2026), not a product. Visible construction is a feature.
- **Model/effort economy is a standing rule.** Mechanical voice-3 pipeline operation + chat-test paste-and-assess is Sonnet-shaped. Architectural decisions on FU#42/split-card are Opus-shaped. Flag the shift if the operator hasn't.
- **Voice Pipeline first, chat-test as instrument.** Voice Pipeline is the production target (consumes specific card fields via API per-step). Chat-test is for development feedback. Don't optimize FOR chat-test; chat is downstream of card quality.

---

*Authoritative pickup doc as of 2026-04-26. Plato shipped. Voice 3 next. If this diverges from `FOLLOW_UPS.md`'s recommended order, this doc wins for 2026-04-26+ next-session scope.*
