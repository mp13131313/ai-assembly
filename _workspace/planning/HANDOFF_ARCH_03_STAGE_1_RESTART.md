# Arch-03 Stage 1 Restart — Handoff & Onboarding

**Session date:** 2026-04-23
**Branch:** `arch-03-additive-merge`
**Status:** implementation complete; branch ready for fresh-session Stage 1 restart on Dostoevsky
**Next session model:** operator's call; Stage 1 test is judgment-lite once the pipeline runs, so Opus 4.7 + adaptive or Sonnet 4.6 + high both work

---

## What this handoff is

A clean onboarding for whoever (human operator or fresh Claude session) picks up the arch-03 testing track after this session. The 2026-04-22 → 2026-04-23 work cycle landed five architectural fixes on top of the original arch-03 pre-seed + Sonnet Wave 1/2/3 implementation. All fix-stack work is now complete; the branch is ready for Stage 1 empirical validation on the Dostoevsky fixture.

If you are a fresh Claude session reading this: **do not re-implement anything in the fix tracker without checking commit history first.** Everything tagged as `APPLIED` or landed in this session is in the commits listed below.

---

## Branch state at handoff

**HEAD:** (see `git log --oneline origin/main..HEAD` for the current head and full commit sequence)

Commit sequence on `arch-03-additive-merge` above `origin/main` at handoff time, newest first:

1. **docs(arch-03):** plan amendments + tracker status updates + this handoff doc
2. **feat(arch-03/1-arch-05-A):** per-chunk reads at Pass 1d/2/3/4a/6 — 5 user prompts + runner refactor
3. **feat(arch-03/1-arch-05-B):** Pass 1.7 Stage C routes edits to chunk files; coherence metadata to `_coherence_audit.json`; merged_dossier rebuilt as snapshot
4. **feat(arch-03/1-arch-08):** anachronism discipline consolidated at `KnowledgeBoundary.anachronism_discipline[]` with dual framings; `LifeScaffold.anachronisms_to_avoid` removed
5. **feat(arch-03/1-arch-06):** `interpretive_frames[]` container at Pass 1.2 (cross-cutting scholarly material: interpretive methods + cross-disciplinary re-framings + voice-level debates)
6. **feat(arch-03/1-arch-04):** Gemini cross-disciplinary preservation discipline block in all 6 merge prompts
7. **feat(arch-03/1-arch-07):** `urls` chunk dropped; URLs derived at render-time via `flows/shared/url_extract.py`
8. **docs(arch-03):** tracker additions for 1-arch-04/05/06/07/08 + WATCH-ITEM
9. Prior: Pass 1.7 split (§5.5 amendment) + chunk_runner fixes (voice_config loading, retry widening, skip-if-exists) + Sonnet Wave 1/2/3 applications + preservation-audit script + Opus arch-03 pre-seed

All commits pushed to `origin/arch-03-additive-merge` as of handoff.

**Working tree:** expected clean. `_workspace/arch_03_baseline_snapshot/` is untracked (backup artifacts from prior runs — safe to keep or discard).

---

## Architecture as of handoff

The arch-03 merge pipeline under the full fix stack looks like this:

### Stage 1A — Parallel chunk merge (Pass 1.1-1.6)

Each Pass 1.N reads Perplexity §N + Claude DR §N + full Gemini; emits per-key JSON files. 19 chunk output files total after 1-arch-07 (`urls` dropped) and 1-arch-06 (new `interpretive_frames`):

- `02_merge/pass_1_1/`: `life_scaffold.json`, `formative_candidates.json`
- `02_merge/pass_1_2/`: `commitments.json`, `concepts.json`, `tensions.json`, **`interpretive_frames.json`** (NEW per 1-arch-06)
- `02_merge/pass_1_3/`: `reasoning_method.json`, `textures.json`, `analytical_context_reasoning.json`
- `02_merge/pass_1_4/`: `moves.json`, `register.json`, `vocabulary.json`, `analytical_context_voice.json`
- `02_merge/pass_1_5/`: `knowledge_boundary.json` (now carries `anachronism_discipline[]` per 1-arch-08), `sensitive_topics.json`, `hard_limits.json`
- `02_merge/pass_1_6/`: `works.json`, `passages.json`, `reference_only_passages.json` (`urls.json` **removed** per 1-arch-07)

**Note for 1-arch-08:** `LifeScaffold.anachronisms_to_avoid` is gone. Anachronism discipline lives at `KnowledgeBoundary.anachronism_discipline[]` with `biographical_framing` + `epistemic_framing` + `severity` per entry.

**Note for 1-arch-04:** each merge prompt carries a Gemini-preservation-discipline block (Block 2) instructing the LLM not to deduplicate Gemini's cross-disciplinary re-framings as overlap with Perplexity/DR canonical claims.

### Stage 1B — Pass 1.7 Coherence (three stages, chunks-as-source-of-truth)

- **Stage A** (Python, deterministic): compose 19 chunks into in-memory MergedDossier dict; Pydantic-validate.
- **Stage B** (LLM, Opus 4.7, `max_tokens=24000`, thinking on): narrow coherence audit; emits `CoherenceAuditResult` = `{flags[], resolutions[], edits[]}` only. Does NOT re-emit the dossier.
- **Stage C** (Python, 1-arch-05 Part B): each edit routed to its owning chunk file under `02_merge/pass_1_N/<key>.json` via the `_CHUNK_ROUTING` map; chunk re-validated against its Pydantic model; atomic write-back. Coherence metadata writes to `02_merge/_coherence_audit.json` (new file). Merged dossier snapshot is rebuilt from post-edit chunks and written to `02_merge/08_merged_dossier.json` as a human-review convenience artifact.

### Stage 2 — Pass 2-6 Generation (chunks-as-source-of-truth via named template vars)

Per 1-arch-05 Part A, each of Pass 1d/2/3/4a/6 user prompts declares named chunk-content template variables instead of `{{ merged_dossier }}` blob. Runner helper `_per_chunk_vars(merged_dossier_dict)` produces 23 named vars (19 chunk keys + 2 sub-slices + 3 filtered interpretive_frames subsets). Each pass receives only what it needs.

Per-pass consumption (see `run_persona_pipeline.py` render calls for exact kwargs):

| Pass | Model | Chunk inputs | Card fields produced |
|---|---|---|---|
| 1d | Sonnet 4.6 | passages, works, reasoning_method_chunk, register, moves + structural_index | (primary_block for Pass 4a/6) |
| 2 | Opus 4.7 | life_scaffold, formative_candidates, knowledge_boundary_chunk, sensitive_topics, hard_limits_chunk, voice_level_debate_frames | 10 |
| 3 | Opus 4.7 | commitments, concepts, tensions, interpretive_frames, reasoning_method_chunk, textures, analytical_context_reasoning | 5 |
| 4a | Opus 4.7 | moves, register, vocabulary, analytical_context_voice, available_pathe, reasoning_method_summary, cross_disciplinary_frames, primary_texts | 7 |
| 4b | Sonnet 4.6 | (CT-only; no chunk reads) | 8 |
| 5 | Opus 4.7 | (CT + constitution + reasoning_method card fields) | 4 |
| 6 | Sonnet 4.6 | works, passages, reference_only_passages + primary_texts + 6 prior card-field refs | 1+1 |

**Chunk-key variable-naming convention:** `_chunk` suffix on chunk vars that collide with downstream card-field names (`reasoning_method_chunk`, `knowledge_boundary_chunk`, `hard_limits_chunk`). Other 16 chunks use natural names.

---

## What to do in the next session

### 1. Orient (10 min)

- Read this handoff (you're doing it).
- `git log --oneline origin/main..HEAD` — confirm the commit sequence matches what's listed above.
- `cd personas && venv/bin/python -m pytest tests/ -x -q` — confirm 128/128 tests pass.
- Briefly skim `_workspace/planning/ARCH_03_ADDITIVE_MERGE_PLAN.md` §5.5–§5.8 for arch-03's evolved architecture.

### 2. Restart Stage 1 (Pass 1.1-1.7 on Dostoevsky)

Archive prior run, clear merge outputs, restart:

```bash
cd /Users/aienvironment/Desktop/AI\ Assembly/code
BASE="../projects/phase-l-dostoevsky/voices/fyodor_dostoevsky"
mkdir -p _workspace/arch_03_baseline_snapshot/pre_stage1_v4_run
mv "$BASE/02_merge/pass_1_"* "$BASE/02_merge/08_merged_dossier.json" \
   "$BASE/02_merge/_coherence_audit.json" \
   "$BASE/_arch_03_audit.json" \
   _workspace/arch_03_baseline_snapshot/pre_stage1_v4_run/ 2>/dev/null

cd personas
venv/bin/python run_pass_1_all.py "Fyodor Dostoevsky" \
    --project "../../projects/phase-l-dostoevsky"
```

Expected wall-time: 15-25 min (6 merge chunks in parallel, max 3 concurrent; then Pass 1.7 sequential).

### 3. Run preservation audit

```bash
cd personas
venv/bin/python scripts/arch_03_preservation_audit.py \
    --voice fyodor_dostoevsky \
    --project "../../projects/phase-l-dostoevsky"
```

Output at `projects/phase-l-dostoevsky/voices/fyodor_dostoevsky/_arch_03_audit.json`.

**Audit metrics to check** (per plan §7.3):

- (a) Character-overlap ≥85% on §3/§4/§5 (vocabulary-recall metric; has known false-positive issues — read report text, not just pass/fail)
- (b) Citation preservation — 100% target (extractor has false-positive issues with character names)
- (c) Named structural patterns §3: 9/9 (scandal-scene, carnivalization, threshold-chronotope, sideshadowing, crowning/decrowning, Menippean, confession-under-pressure, vdrug, polyphony)

### 4. Critical new checks (specific to this session's fixes)

**Verify `interpretive_frames[]` populated (1-arch-06 + 1-arch-04 effectiveness):**

```bash
cd personas
venv/bin/python -c "
import json
d = json.load(open('../../projects/phase-l-dostoevsky/voices/fyodor_dostoevsky/02_merge/08_merged_dossier.json'))
frames = d.get('interpretive_frames', [])
print(f'interpretive_frames count: {len(frames)}')
for f in frames:
    print(f'  [{f[\"frame_type\"]}] {f[\"name\"]} — scholars: {f.get(\"primary_scholars\", [])}')
"
```

**Expect**: ≥3 frames for Dostoevsky (well-documented voice). Expected content per 1-arch-06 + 1-arch-04 preservation discipline:
- At least 1 `interpretive_method` (hesychast reading per Kasatkina 2022, or subject-to-subject method, or Patyk provocation frame)
- At least 1-2 `cross_disciplinary_reframing` (post-2022 Ukrainian scholarship, postcolonial reading, etc.)
- At least 1 `voice_level_debate` (Williams-vs-Frank on Myshkin, antisemitism structural-vs-incidental, or similar)

**Verify `anachronism_discipline[]` consolidated (1-arch-08 effectiveness):**

```bash
cd personas
venv/bin/python -c "
import json
d = json.load(open('../../projects/phase-l-dostoevsky/voices/fyodor_dostoevsky/02_merge/08_merged_dossier.json'))
ad = d['knowledge_boundary'].get('anachronism_discipline', [])
print(f'anachronism_discipline count: {len(ad)}')
for a in ad[:3]:
    print(f'  {a[\"modern_term\"]} ({a.get(\"severity\",\"?\")}):')
    print(f'    bio: {a.get(\"biographical_framing\",\"\")[:80]}...')
    print(f'    epi: {a.get(\"epistemic_framing\",\"\")[:80]}...')
print()
ls = d.get('life_scaffold', {})
assert 'anachronisms_to_avoid' not in ls, 'LifeScaffold should not have anachronisms_to_avoid under 1-arch-08'
print('LifeScaffold.anachronisms_to_avoid correctly absent ✓')
"
```

**Expect**: ≥4 entries each with both framings populated, for a well-documented voice like Dostoevsky. Trauma / depression / existentialist / identity at minimum.

**Verify `_coherence_audit.json` separation (1-arch-05 Part B effectiveness):**

```bash
cd personas
ls -la ../../projects/phase-l-dostoevsky/voices/fyodor_dostoevsky/02_merge/_coherence_audit.json
venv/bin/python -c "
import json
c = json.load(open('../../projects/phase-l-dostoevsky/voices/fyodor_dostoevsky/02_merge/_coherence_audit.json'))
print(f'flags: {len(c[\"coherence_flags\"])}')
print(f'resolutions: {len(c[\"coherence_resolutions\"])}')
print(f'edits applied: {c[\"edits_applied\"]}')
print(f'edits skipped: {c[\"edits_skipped\"]}')
for desc in c['edit_log']:
    print(f'  → {desc}')
"
```

**Expect**: separate file exists; flags/resolutions/edits all captured; `edit_log` shows `pass_1_N/<key>.json` file paths if edits were applied.

**Verify chunks edited (Part B source-of-truth check):**

If any edits were applied, spot-check that the chunk file reflects them. Example for a vocabulary edit:

```bash
cd personas
venv/bin/python -c "
import json
v = json.load(open('../../projects/phase-l-dostoevsky/voices/fyodor_dostoevsky/02_merge/pass_1_4/vocabulary.json'))
terms = [e['term'] if isinstance(e, dict) else e for e in v.get('preferred_vocabulary', [])]
print(f'vocabulary.preferred_vocabulary: {len(terms)} terms')
print(f'  sample: {terms[:10]}')
"
```

### 5. Stage 2 (Pass 2-7 full pipeline) — operator pauses before

Per the original Opus testing handoff (§18b), Stage 2 runs `run_persona_pipeline.py` end-to-end and measures new card quality vs. Phase L baseline. Under this session's fix stack, Pass 2-6 exercise the per-chunk reads (Part A). Recommended to pause after Stage 1 preservation-audit review, report findings, then decide on Stage 2.

If Stage 1 preservation confirms 1-arch-04 + 1-arch-06 closed the Gemini gap (interpretive_frames populated with post-2022 + cross-disciplinary content), Stage 2 should empirically test whether richer upstream resolves Pass 7a's baseline register-drift (ISSUE on 6 Pass 4b fields).

### 6. What to NOT do

- Do NOT re-implement fixes already in commit history (use `git log --grep` to confirm before editing any 1-arch-* file).
- Do NOT modify Pass 0a/0b/1a/1b/1c/1d code beyond what this session already landed; those are locked per Wave 1/2 SURVIVES status.
- Do NOT merge to main autonomously — operator decision per §18b.
- Do NOT regenerate the Dostoevsky research inputs (frozen fixture per §7.1; if Stage 1 shows research-side content gap, that's a separate diagnostic question).

---

## Known issues / watch items carried forward

1. **Preservation audit script false-positive rate** — the `citation preservation` metric extracts names via regex that catches fictional character names (Alyosha, Mitya, Zosima), first names, country names (France), and epithets ("Younger" from "Holbein the Younger") as "missing authors." Script needs recalibration as a post-Stage-1 improvement task. Run the manual verification queries in step 4 above for authoritative readings.

2. **Pass 4b / Pass 5 register drift** (baseline Pass 7a ISSUE on 6 Pass 4b output-characteristics fields) — arch-03's hypothesis is that richer CT upstream resolves this. **Empirical question for Stage 2.** If it persists, the fix is prompt-hardening at Pass 4b's first-person/second-person register discipline (chunk reads at Pass 4b were considered and withdrawn during the retrospective — chunks are third-person descriptive, would likely worsen the drift).

3. **`reference_only_passages` scope** (WATCH-ITEM in tracker) — untested for Dostoevsky (public-domain corpus; field is empty). First voice with a copyrighted-corpus (Whanganui, contemporary voices) will test whether it should be a merge output or move to project-level intake config. Revisit when that first voice processes.

4. **`1-arch-01`** (curated_corpus_passages from Pass 1d) remains **deferred post-Phase-N**. Not a conflict with this session's fixes; 1-arch-05 Part A to Pass 1d actually pre-enables 1-arch-01 by making selection criteria explicit.

5. **`1d-06`** (fuzzy-match primary-path, Wave 2 HIGH architectural) remains **deferred** per operator default. Not material for Stage 1.

---

## Files of record

- **Planning docs (authoritative):**
  - `_workspace/planning/ARCH_03_ADDITIVE_MERGE_PLAN.md` (§5.5–§5.8 for this session's amendments)
  - `_workspace/planning/PIPELINE_REVIEW_FIXES.md` (1-arch-01 through 1-arch-08 + WATCH-ITEM)
  - `_workspace/planning/OPEN_ITEMS.md` (broader project pickup)
  - `_workspace/planning/REBUILD_PLAN.md` (Phase B locked decisions PB#1-9)

- **Code of record:**
  - `personas/run_persona_pipeline.py` — orchestrator; `_per_chunk_vars()` helper is the 1-arch-05 Part A entry point
  - `personas/run_pass_1_7.py` — Stage A/B/C; `_CHUNK_ROUTING` map + `_route_edit_to_chunk_file()` is the 1-arch-05 Part B entry point
  - `personas/schemas/_frames.py` — InterpretiveFrame + FrameType (1-arch-06)
  - `personas/schemas/pass_1_1.py` — AnachronismEntry expanded (1-arch-08); LifeScaffold.anachronisms_to_avoid removed
  - `personas/schemas/pass_1_5.py` — KnowledgeBoundary.anachronism_discipline[] added (1-arch-08)
  - `personas/flows/shared/url_extract.py` — URL extraction helper (1-arch-07)
  - `personas/flows/shared/prompts/pass_1_1_merge.md` through `pass_1_6_merge.md` — 1-arch-04 Gemini discipline block in each
  - `personas/flows/shared/prompts/persona_pass_2_user.md`, `persona_pass_3_user.md`, `persona_pass_4a_user.md`, `persona_pass_6_user.md`, `persona_pass_1d_excerpt_selection.md` — 1-arch-05 Part A per-chunk user prompts

- **Baselines preserved under `_workspace/arch_03_baseline_snapshot/`:**
  - `baseline_07_persona_card_assembled.json` — Phase L pre-arch-03 card (for Stage 2/3 comparison)
  - `baseline_08_merged_dossier.json` — Phase L pre-arch-03 merged dossier
  - `baseline_05_validation/` — Phase L Pass 7 validation outputs
  - `baseline_04_generation/`, `baseline_06_derive/` — Phase L generation + derive outputs
  - `partial_killed_run/`, `partial_run_2/`, `pre_fixstack_run/` — intermediate run archives from this session's testing

---

## Operator quick-start (if you want to just go)

```bash
cd /Users/aienvironment/Desktop/AI\ Assembly/code

# Verify branch + tests
git log --oneline origin/main..HEAD | head -10
cd personas && venv/bin/python -m pytest tests/ -x -q && cd ..

# Clear prior merge outputs, keep archive
BASE="../projects/phase-l-dostoevsky/voices/fyodor_dostoevsky"
mkdir -p _workspace/arch_03_baseline_snapshot/pre_stage1_v4_run
mv "$BASE/02_merge/pass_1_"* "$BASE/02_merge/08_merged_dossier.json" \
   "$BASE/02_merge/_coherence_audit.json" \
   "$BASE/_arch_03_audit.json" \
   _workspace/arch_03_baseline_snapshot/pre_stage1_v4_run/ 2>/dev/null

# Restart Stage 1 (15-25 min wall time)
cd personas
venv/bin/python run_pass_1_all.py "Fyodor Dostoevsky" \
    --project "../../projects/phase-l-dostoevsky"

# Preservation audit
venv/bin/python scripts/arch_03_preservation_audit.py \
    --voice fyodor_dostoevsky \
    --project "../../projects/phase-l-dostoevsky"
```

Then run the 3 verification blocks in step 4 above for the new-fix-specific checks (interpretive_frames + anachronism_discipline + _coherence_audit.json + chunks-as-source-of-truth).

---

*End handoff. Next session: restart Stage 1, measure, report PROCEED / ITERATE / ROLLBACK.*
