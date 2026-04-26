# Next session — voices 3-12 buildout (2026-04-26 evening)

**Supersedes for next-session pickup:** `NEXT_SESSION_2026_04_26_PLATO_SHIPPED.md` (this morning's pickup, pre-FU#19/29/40/31 work).
**Code repo branch:** `arch-03-additive-merge` at HEAD `228bd5b` (pushed to `origin/arch-03-additive-merge`).
**Code repo PR:** [#2](https://github.com/mp13131313/ai-assembly/pull/2) open against `main`, awaiting operator review/merge.
**Athens-2026 data backup repo:** [`mp13131313/ai-assembly-athens2026-voices`](https://github.com/mp13131313/ai-assembly-athens2026-voices) (PRIVATE) at HEAD `092ff5b` — clean pre-buildout state pushed 2026-04-26. **NEW**: post-cleanup setup; per-voice card data lives here going forward.
**Status:** Plato shipped + chat-test validated. Pipeline at its cleanest state. Athens-2026 folder cleaned + backup repo live. Voice 3-12 buildout is the next operational step. Operator has stated workflow plan (see SECTION 2).
**Tests:** 212/212 passing. ~133 commits ahead of `origin/main`.

---

## READING ORDER

1. **THIS doc** — self-contained for operational pickup, includes operator's stated buildout plan.
2. `_workspace/planning/FOLLOW_UPS.md` — per-FU# tracker; check entries for any FU# this doc references for full history.

**Historical-only — IGNORE unless investigating WHY:** all other `_workspace/planning/HANDOFF_*` and `NEXT_SESSION_*` docs are archival.

---

## SECTION 1 — STATE OF PLAY (2026-04-26 evening)

### Plato

- ✅ CARD COMPLETE — `projects/phase-l-plato/voices/plato/07_persona_card_assembled.json` (148 KB, 36 fields, REVISION_NEEDED + human_review_pending, Output Register CLEAN)
- ✅ Chat-test validated empirically 2026-04-26 against Athens-program HTML probe. Persona-take-hold restored ("the user is asking me, as Plato, how I feel about this gathering coming to my city"). Translation_protocol applied generatively. Doctor-cook from *Gorgias* invoked. Engagement topics aligned with WBBF themes. Two thinking traces archived in conversation history (not on disk; reproduce by re-running probe if needed).
- 🟡 Validation report shows REVISION_NEEDED + 50 UNVERIFIED + 7 boddice_flags + 6 field_issues + 1 INCONSISTENT — these are **advisory** post-empirical-chat-test. Don't re-iterate Plato unless real-world signal appears.

### Today's full work landed (2026-04-26)

13 commits pushed. Categorically:

**Pipeline improvements for voices 3-12:**
- `aa4ce85` — FU#41 Amendment A: chat strip 10→5 (preserve voice-constitutional)
- `2cbbff6` — FU#41 Amendment B: chat strip 5→11 (spec-shell + nested corpus_metadata)
- `6c0daf5` — FU#33 P1 initial: bracket strip module + Pass 7d-clean
- `cba8fc5` — FU#46: Pass 1d budget 30K → 60K
- `0031c91` — FU#33 P1 amendment: preserve boddice tags + reorder strip BEFORE validators (Pass 6.5-clean)
- `bf49a0a` — FU#43 + FU#44 + FU#45: Pass 6 corpus_metadata cleanliness, patcher register-drift extension, cache-invalidation helper
- `ef91fb6` — CC#1 + FU#33 P2: primary_text_urls relocation, INCONSISTENT-flag wiring
- `620d410` — FU#19 + FU#29 narrow + FU#40 simple + FU#31 architectural note: Pass 0b non-human/fictional template anchoring cleanup, sentinel regen helper, Pass 4a digression-permission for narratival voices, FU#31 integration path note

**Documentation/handoff:**
- `08b0e9f` — earlier handoff doc + FOLLOW_UPS additions for FU#42-46
- `a6a733c` — FU#47 + FU#48 added (FU#48 later withdrawn)
- `b9520f4` — FU#48 withdrawn (audit showed already-done)

### Pipeline shape now

```
Pass 0a → Pass 1a (Perplexity) + Pass 1b (Gemini) parallel
       → Pass 0b (DR-prompt render + tailor)
       → Phase 0.5 split → 6 per-section DR prompts
       → MANUAL: Claude DR §1-§6 sessions (operator runs claude.ai)
       → Pass 1.1-1.7 chunked merge (parallel + coherence)
       → Pass 1c-extract → 1c-fetch → review gate → Pass 1d
       → Pass 2 → CT → Pass 3 → CT → Pass 1d
       → Pass 4a → CT → Pass 4b → CT → Pass 5 → Pass 6
       → ★ Pass 6.5-clean ★ (FU#33 P1, NEW — strip schema-taxonomy +
         EvidenceTag + curator-note brackets; preserve boddice tags)
       → Pass 7-pre chunked → Pass 7-anachronism → Pass 7a
       → ★ Pass 7-pre INCONSISTENT-flag wiring ★ (FU#33 P2, NEW)
       → [Pass 7a-FIX if REVISION_NEEDED] (with FU#44 register-drift +
         internal-contradiction patches)
       → Pass 7b → Pass 7c → Derive
       → Card assembly + chat-prompt-builder (FU#41 Amendments A + B)
       → CARD COMPLETE
```

---

## SECTION 2 — OPERATOR'S STATED WORKFLOW PLAN (2026-04-26 evening)

> *"My general plan now is to generate the 12 voices in an actual Athens folder. I think I will generate them the way we've done them with you running the pipelines and is written basically onto my disk. I'm wondering whether I should somehow create this in a separate repo or create a new git place so that there is a backup but generally I don't think it needs a virtual machine because we just need the cards and then they need to sit somewhere with the runtime virtual machine can use them for that. I would like to use the Athens folder we have but clean it off everything that's there and actually start producing the voices so the first thing would be to double-check what content gets used by all the voices when they get settled from scratch. I think it was audience and panel and conference and those we would need to know first — be very rigorous to absolutely nail them before doing the voices. And then the next steps would be that I would want to create every voice up to the point where they produce the DR prompts so that I can then while I'm doing something else generate all of that research in parallel. And as the research and comes in and completes for one voice then I will actually run the pipeline for that. Understand?"*

### Translation to operational steps

| Phase | Step | Description |
|---|---|---|
| **0** ✅ DONE 2026-04-26 | Backup repo setup | **Option B landed** — separate private GitHub repo `mp13131313/ai-assembly-athens2026-voices` (private). Local `.git/` initialized inside `projects/athens-2026/`; remote `origin` configured; first commit (`092ff5b`) captures cleaned pre-buildout state. **Going-forward workflow:** after each voice CARD COMPLETE, `cd projects/athens-2026 && git add . && git commit -m "voice <slug> shipped" && git push`. |
| **1** ✅ DONE 2026-04-26 | Athens-2026 cleanup | **Executed.** Legacy v3.10 content moved to `~/Desktop/AI Assembly/archive/runs/personas/athens-2026-legacy/`: `voices/` (5 stale voice dirs) → `voices_v3.10/`, `inputs/` → `inputs_v3.10/`, `runs/ibn_battuta/` → `runs_partial_ibn_battuta/`. `.DS_Store` deleted. Athens-2026 now 224 KB; contains: 3 deployment-context JSONs (still need operator update), `council_config.json` + `reference/` (runtime-team-owned, kept), `_migration_manifest.json` (provenance), `voices_batch.txt` (small legacy reference, kept), `.gitignore` (added by backup-repo init). |
| **2** | Deployment-context finalization | Lock `audience_profile.json` + `conference_facts.json` + `panel_roster.json` at `projects/athens-2026/` root. Operator finalizes `docs/AUDIENCE_BRIEF.md` first (canonical source per `_canonical_source` annotation), then re-render JSON. **Be rigorous** — these prime Pass 5 + Derive across all 12 voices |
| **3** | Voice intake authoring | For each of the 11 remaining voices (Cleopatra, Ibn Battuta, Scheherazade, Ada Lovelace, Fyodor Dostoevsky, Hannah Arendt, Bob Marley, Audrey Tang, Peter Thiel, Whanganui River, Octopus), author `voices/<slug>/00_intake/02_voice_config.json` |
| **4** | **Phase 0.5 batch — DR prompts ready** | For each voice: run Pass 0a + Pass 1a (Perplexity) + Pass 1b (Gemini) + Pass 0b render + tailor + split. Output: 6 per-section DR prompts at `voices/<slug>/01_research/03_dr_prompts/0N_section_N_dr_prompt.md`. **All 11 voices' Phase 0.5 done in batch** so operator has 11 × 6 = 66 DR prompts ready. |
| **5** | **Manual claude.ai DR sessions (operator-paced, parallelizable)** | While Phase 0.5 batch finishes / in parallel: operator runs claude.ai DR sessions for each voice § 1–§6. Per-voice §1–§5 = Opus 4.6, §6 = Opus 4.7 (per model-per-section policy). 6 sessions × 11 voices = 66 manual DR sessions. Output saved at `voices/<slug>/01_research/04_dr_dossier/0N_section_N.md` |
| **6** | **Per-voice pipeline run (as DR data lands)** | When voice X has all 6 DR sections saved, run `venv/bin/python run_persona_pipeline.py "<Voice>" --project "/Users/aienvironment/Desktop/AI Assembly/projects/athens-2026"` for that voice. Manual gate at Pass 1c (review primary_texts), then auto through Card Assembly + chat artifact. ETA per voice: ~$18-22 + 2h |
| **7** | **Per-voice chat-test validation** | After CARD COMPLETE: paste `voices/<slug>/06_derive/03_chat_system_prompt.json` into a Claude project, probe in Provocateur-register first, then philosophical-meditation. Per `8057961`, exercise both Sonnet AND Opus model modes |

**Why this order is right:** Phase 0.5 (claude.ai DR batches) is the longest manual operator-side step. Front-loading it lets operator parallelize while pipelines wait. Cards then run as DR data trickles in.

---

## SECTION 3 — PRE-VOICE-3 DEPLOYMENT-CONTEXT FINALIZATION

This is operator-side work, **must complete before Phase 0.5 batch starts**.

### Three project-level files (live at `projects/athens-2026/` root)

| File | What it primes | Current size |
|---|---|---|
| `conference_facts.json` | Pass 5 + Derive — session_role_for_ai_assembly, conference_context_paragraph, dates, location | 1.1 KB |
| `audience_profile.json` | Pass 5 audience-priming (FU#12-B) — `bold_engagement_topics`, `default_questions`, `unique_contribution`, `disagreement_protocol` | 1.6 KB |
| `panel_roster.json` | Cross-voice awareness | 263 B |

### Canonical source

`docs/AUDIENCE_BRIEF.md` carries the audience characterization. `audience_profile.json` has `_canonical_source` annotation pointing to it: *"docs/AUDIENCE_BRIEF.md — update the brief first, then re-render this file. If they drift, the brief wins."*

**Operator action:** finalize `docs/AUDIENCE_BRIEF.md` first, then re-render `audience_profile.json` from it.

### Verification questions (be rigorous)

Per the operator's stated discipline ("very rigorous to absolutely nail them"):

- **Conference facts:** Are the dates, location, host org, founders, tagline all accurate as of 2026-04-26? Is the `session_role_for_ai_assembly` paragraph still the right framing (overnight AIssembly producing breakfast-reading artifacts)?
- **Audience profile:** Is the participant_profile paragraph still accurate? The 7 intellectual factions still represent the WBBF participant cohort? Is the `participants_count_approx: 750` still right?
- **Panel roster:** All 12 voices still committed? Any substitutions from the original list?
- **Programming tracks:** Still "AI Democracy Marathon", "Agentic Agora", "Ministry of Regeneration"? Any new tracks?

After lock-in: copy all three JSONs to `projects/athens-2026/` (overwrite existing).

---

## SECTION 4 — ATHENS-2026 FOLDER CLEANUP ✅ LANDED 2026-04-26

**Cleanup executed 2026-04-26 evening.** What was at `/Users/aienvironment/Desktop/AI Assembly/projects/athens-2026/` (was 456 KB legacy):

```
.DS_Store               (cosmetic)
_migration_manifest.json    (Phase B migration audit; KEEP for provenance)
audience_profile.json       (UPDATE during deployment-context finalization)
conference_facts.json       (UPDATE during deployment-context finalization)
council_config.json         (25 KB — runtime-side artifact; KEEP for runtime team)
inputs/                     (legacy v3.10 dossiers + non-human grounding; ARCHIVE or DELETE per operator)
panel_roster.json           (UPDATE during deployment-context finalization)
reference/                  (sessions.json + speakers.json + sessions.skipped.json; KEEP for runtime)
runs/                       (partial runtime run for ibn_battuta; ARCHIVE or DELETE)
voices/                     (5 stale voice dirs: cleopatra, hannah_arendt, ibn_battuta, octopus, plato)
                            (these are pre-arch-03; the new Plato lives at projects/phase-l-plato/)
voices_batch.txt            (1 KB — legacy batch script reference; check + KEEP or DELETE)
```

### Cleanup actions taken (post-execution)

1. ✅ **Deleted `.DS_Store`**
2. ✅ **Archived `voices/`** (5 stale pre-arch-03 voice dirs) → `~/Desktop/AI Assembly/archive/runs/personas/athens-2026-legacy/voices_v3.10/`
3. ✅ **Archived `inputs/`** (legacy v3.10 dossiers) → `~/Desktop/AI Assembly/archive/runs/personas/athens-2026-legacy/inputs_v3.10/`
4. ✅ **Archived `runs/ibn_battuta/`** (partial runtime run) → `~/Desktop/AI Assembly/archive/runs/personas/athens-2026-legacy/runs_partial_ibn_battuta/`. Empty `runs/` dir then removed
5. **KEPT `council_config.json`** (runtime artifact; runtime team owns it; persona pipeline doesn't write to it)
6. **KEPT `reference/`** (runtime artifact; runtime team owns; sessions.json + speakers.json + sessions.skipped.json)
7. **KEPT `_migration_manifest.json`** (Phase B migration provenance)
8. **KEPT `voices_batch.txt`** (1 KB; legacy reference; harmless)
9. ✅ **`.gitignore` added** by backup-repo init (covers `.DS_Store`, `__pycache__/`, etc.)
10. **Pending operator action — UPDATE `audience_profile.json` + `conference_facts.json` + `panel_roster.json`** per SECTION 3 once `docs/AUDIENCE_BRIEF.md` is finalized.
11. **Open decision: copy Plato over from `projects/phase-l-plato/`?** For unified panel layout (Voice Pipeline runtime expects all 12 voices in one project), recommend yes. Per-voice project pattern was prototype; production deployment wants all voices in `athens-2026/voices/`.

### Final inventory

`projects/athens-2026/` (224 KB):
- `_migration_manifest.json` (3.3 KB; provenance)
- `audience_profile.json` (1.6 KB; pending update)
- `conference_facts.json` (1.1 KB; pending update)
- `council_config.json` (25.7 KB; runtime artifact)
- `panel_roster.json` (263 B; pending update)
- `reference/` (3 files; runtime artifacts)
- `voices_batch.txt` (1.2 KB; legacy reference)
- `.gitignore` (245 B)
- `.git/` (initialized; remote → `mp13131313/ai-assembly-athens2026-voices`)

---

## SECTION 5 — BACKUP STRATEGY ✅ LANDED 2026-04-26

> *"I'm wondering whether I should somehow create this in a separate repo or create a new git place so that there is a backup."*

### What was at risk

`projects/athens-2026/` is OUTSIDE the main code git repo per Tier 3 separation rule. If MacBook fails / hard drive dies BEFORE Athens (May 7-10), all 12 voice cards + intermediate artifacts would be lost. ~600 MB total when full.

### Decision: Option B — separate private GitHub repo

**Repo:** [`mp13131313/ai-assembly-athens2026-voices`](https://github.com/mp13131313/ai-assembly-athens2026-voices) (PRIVATE)

**Setup completed 2026-04-26:**
- `.git/` initialized inside `projects/athens-2026/`
- `.gitignore` covers `.DS_Store`, `__pycache__/`, `venv/`, `voices/*/_run_logs/`, `*.tmp` etc.
- Initial commit `092ff5b` captures the cleaned pre-buildout state
- Remote `origin` → `https://github.com/mp13131313/ai-assembly-athens2026-voices.git`, branch `main` tracking
- First push successful

### Going-forward workflow

After each voice CARD COMPLETE in athens-2026:

```bash
cd "/Users/aienvironment/Desktop/AI Assembly/projects/athens-2026"
git add voices/<slug>/
git commit -m "voice <slug> shipped: <one-line note>"
git push
```

Backup updated automatically. Disk failure recovery: `git clone https://github.com/mp13131313/ai-assembly-athens2026-voices.git` to a fresh location.

### Auth note

Push uses fine-grained PAT in macOS Keychain. PAT scope must include both:
- **Repository access:** `ai-assembly` AND `ai-assembly-athens2026-voices` selected
- **Repository permissions:** `Contents: Read and write` + `Metadata: Read`

If push 403s with "Write access not granted," verify PAT scope at https://github.com/settings/tokens?type=beta. Or push from operator's own terminal session if their personal credentials have broader scope.

### Tier 3 separation preserved

The main code repo (`mp13131313/ai-assembly`) carries persona pipeline CODE only. The voices DATA repo (`mp13131313/ai-assembly-athens2026-voices`) carries per-project DATA only. Two repos, two purposes, never crossed.

### Options A + C (rejected, for record)

- **Option A** — periodic zip + cloud upload. Manual + requires discipline.
- **Option C** — Time Machine / external drive. Fine but no off-site replication.

---

## SECTION 6 — PER-VOICE WORKFLOW DETAIL

For each voice in voices 3-12 (after deployment-context locked + athens-2026 cleaned):

### Step A: Author voice config (~5 min per voice)

`projects/athens-2026/voices/<slug>/00_intake/02_voice_config.json`:

```json
{
  "name": "<Voice Display Name>",
  "type": "human" | "fictional" | "non_human",
  "subtype": null | "philosopher" | "novelist" | "ruler" | "musician" | "system" | "organism" | etc.,
  "voice_mode": "philosophical" | "narratival" | "observational" | null,
  "hostile_sources": false | true,
  "corpus_constraint": "full" | "lyrics_patterns_only" | "scientific_only" | etc.,
  "manual_grounding": "<2-4 sentence Wikipedia-style bio>",
  "wikipedia_url": "<URL>",
  "editorial_rationale": null | "<reasoning if voice has special editorial framing>"
}
```

**DO NOT** include `primary_text_sources` (the legacy backward-compat manual override). The pipeline auto-derives URLs from Pass 1.6's works.json + passages.json per 1-arch-07.

### Step B: Phase 0.5 batch (DR prompts ready) (~$2 + 5 min per voice)

```bash
cd "/Users/aienvironment/Desktop/AI Assembly/code"
set -a && source .env && set +a
cd personas
venv/bin/python run_phase0_1_research.py "<Voice>" --project "/Users/aienvironment/Desktop/AI Assembly/projects/athens-2026"
# (or whatever the Phase 0.5 batch entry-point is — check personas/README or HANDOFF.md)
```

This produces:
- `voices/<slug>/01_research/01_perplexity_dossier.json`
- `voices/<slug>/01_research/02_gemini_broad_scan.json`
- `voices/<slug>/01_research/03_dr_prompts/01_monolithic_dr_prompt.md`
- `voices/<slug>/01_research/03_dr_prompts/02_tailoring_notes.json`
- `voices/<slug>/01_research/03_dr_prompts/03_section_1_dr_prompt.md` … `08_section_6_dr_prompt.md`

**Operator does this for all 11 voices in one batch.** ETA: ~5 min × 11 = ~1 hour wall, ~$22 total.

### Step C: Manual claude.ai DR sessions (operator-paced, parallelizable across voices)

Per voice, 6 sessions:
- §1–§5: paste prompt into claude.ai with Opus 4.6 model selected
- §6: paste prompt into claude.ai with Opus 4.7 model selected (per model-per-section policy)
- Each session ~9-30 min wall (depends on DR-infrastructure load)
- Save output as `voices/<slug>/01_research/04_dr_dossier/0N_section_N.md`

**11 voices × 6 sessions = 66 DR sessions total.** Operator-side; parallelize where possible (e.g. open 3 claude.ai tabs in parallel).

**Optionally per-voice mixed-staging** (per Plato precedent): some voices may benefit from 4.7 dominance (philosophical) vs 4.6 dominance (narratival). Decide per-voice based on §1-§3 comparison if you have time, or use defaults.

### Step D: Per-voice pipeline run (as DR data lands)

When voice X has all 6 DR sections saved at `voices/<slug>/01_research/04_dr_dossier/`, run:

```bash
cd "/Users/aienvironment/Desktop/AI Assembly/code"
set -a && source .env && set +a
cd personas
venv/bin/python run_persona_pipeline.py "<Voice>" --project "/Users/aienvironment/Desktop/AI Assembly/projects/athens-2026"
```

ETA per voice: ~2h, ~$18-22.

**Manual gate at Pass 1c REVIEW GATE:** review `voices/<slug>/03_corpus/04_primary_texts_review.md`, optionally curate `01_primary_texts.json` (drop junk entries; add canonicals if needed — Plato precedent for Laws/Statesman additions). `touch 03_corpus/03_primary_texts_reviewed.flag` to continue.

After REVIEW GATE: pipeline auto-runs through Pass 1d → Pass 2-6 → Pass 6.5-clean (NEW) → Pass 7-family → Derive → Card Assembly + Chat artifact. CARD COMPLETE summary at end.

### Step E: Per-voice chat-test validation

Paste `voices/<slug>/06_derive/03_chat_system_prompt.json` into a Claude project. Probe:
1. **Provocateur-register first** (concrete-situation prompt): *"You've just received the program for the AIssembly panel in Athens. The program mentions 'citizen assembly with AI' and a nightwalk on 'the rule of one.' What's your first reaction?"*
2. **Philosophical-meditation register second** (abstract question): *"What is justice / truth / the good / etc. — voice-appropriate."*

**Both Sonnet AND Opus model modes** per `8057961` — different performance modes (Sonnet → essayistic; Opus → philosophical-extension). 4-cell matrix per voice.

If chat-test passes (persona inhabits, translation_protocol applies, artifact-spec honored): voice ships. Move on.

If chat-test fails: diagnose specifically. Don't fall back to Plato-style hand-editing — voices 3-12 should produce clean shipped artifacts from the pipeline directly.

---

## SECTION 7 — ONBOARDING PROMPT (copy-paste into fresh session)

```
You are resuming the AI Assembly persona-pipeline project on branch
arch-03-additive-merge. Plato shipped 2026-04-25/26 (chat-test validated).
Pipeline at its cleanest state across the project. Voice 3-12 buildout
is the next operational step — operator has stated workflow plan in
NEXT_SESSION_2026_04_26_VOICES_3_TO_12_BUILDOUT.md.

Model: Opus 4.7 + adaptive thinking. Most of voice 3-12 buildout is
mechanical pipeline operation + chat-test paste-and-assess
(Sonnet-shaped). Architectural decisions are off the table per operator
("FU#42 + FU#47 deferred to post-Athens"). Flag the cheaper-model option
when starting per-voice runs.

FIRST ACTIONS:

1. Read _workspace/planning/NEXT_SESSION_2026_04_26_VOICES_3_TO_12_BUILDOUT.md
   in full. That is THIS doc — the authoritative pickup point.

2. Read _workspace/planning/FOLLOW_UPS.md (per-FU# tracker, updated
   through 2026-04-26 with FU#19/29/40 LANDED, FU#42/47 deferred,
   FU#48 withdrawn).

3. Verify repo state:
   cd "/Users/aienvironment/Desktop/AI Assembly/code"
   git log --oneline origin/main..HEAD | head -20
   git status
   cd personas && venv/bin/python -m pytest tests/ -x -q
   (Expect: ~133 commits ahead of origin/main; working tree clean except
    _workspace/arch_03_baseline_snapshot/; 212/212 tests pass.)

4. Verify Plato is shipped:
   ls "/Users/aienvironment/Desktop/AI Assembly/projects/phase-l-plato/voices/plato/"
   - 07_persona_card_assembled.json + 06_derive/{00,01,02,03}.json all present.
   - Card status: REVISION_NEEDED + human_review_pending (advisory; chat-
     test passed empirically — see SECTION 1).

5. Establish where the operator is in their workflow plan (SECTION 2):
   - Phase 0 (backup decision)? Operator may have set up a separate repo
     OR Time Machine / Option C; check projects/athens-2026/.git/ existence
   - Phase 1 (athens-2026 cleanup)? Check projects/athens-2026/voices/
     contents — if still 5 stale voice dirs, cleanup not done yet
   - Phase 2 (deployment-context finalization)? Check
     docs/AUDIENCE_BRIEF.md last-modified + projects/athens-2026/
     audience_profile.json/conference_facts.json/panel_roster.json
     last-modified — if all old, finalization not done
   - Phase 3 onward (voice config authoring, Phase 0.5 batch, DR sessions,
     pipeline runs): check projects/athens-2026/voices/<slug>/ folders
     for each non-Plato voice

6. Pick up where operator left off. The default per the doc is "step
   through phases 1-7 with operator confirmation at each destructive
   step (cleanup deletes, voice-config authoring confirmation)."

DO NOT:
- Delete athens-2026 contents without explicit operator confirmation
  per item (the cleanup involves real legacy data; ask before each
  destructive action).
- Re-run Plato unless operator explicitly asks. Card is shipped.
- Re-run Dostoevsky. Phase 2 + G10 Derive re-fire are on disk.
- Push to origin/main without explicit operator confirmation. PR #2
  is open for review; operator decides on merge.
- Use Opus 4.6 for §6 of any voice's DR. Per model-per-section policy
  §6 = Opus 4.7. (§1–§5 = Opus 4.6.)
- Create files outside the planned per-voice folder layout.

KEY FILES:
- Authoritative planning: this doc
- Per-FU tracker: _workspace/planning/FOLLOW_UPS.md
- Pipeline orchestrator: personas/run_persona_pipeline.py
- Phase 0.5 entry: personas/run_phase0_1_research.py (Pass 0a + 1a +
  1b + 0b render + tailor + split)
- Pass 6.5-clean: personas/flows/shared/bracket_strip.py (FU#33 P1
  amended — preserves boddice tags)
- Chat artifact builder (FU#41 Amendments A + B): personas/flows/shared/
  chat_prompt_builder.py
- Cache invalidation helper (FU#45): personas/scripts/invalidate_cache.py
- Sentinel regen (FU#29 narrow): personas/scripts/sentinel_regen.py
- Patcher prompt (FU#13 + FU#44): personas/flows/shared/prompts/
  persona_pass_7a_fix.md
- Voice config schema: personas/schemas/voice_config.py
- Authoritative briefing: docs/AI_Assembly_Briefing_v3_1.md
- Audience canonical source: docs/AUDIENCE_BRIEF.md (re-render
  audience_profile.json from this)

If unsure, this doc's SECTION 6 has per-voice workflow steps; SECTION 4
has the cleanup checklist; SECTION 5 has the backup recommendation.
```

---

## SECTION 8 — KEY FILES + DON'TS (consolidated)

### Code touched 2026-04-25/26 (no further work needed)

- `personas/flows/shared/bracket_strip.py` — FU#33 P1 (boddice-preserving)
- `personas/flows/shared/chat_prompt_builder.py` — FU#41 Amendments A + B
- `personas/run_persona_pipeline.py` — Pass 6.5-clean integration + FU#33 P2 INCONSISTENT-flag wiring
- `personas/flows/shared/prompts/persona_pass_1d_excerpt_selection.md` — 60K budget
- `personas/flows/shared/prompts/persona_pass_4a_voice.md` — FU#40 simple digression-permission
- `personas/flows/shared/prompts/persona_pass_6_corpus.md` — FU#43 corpus_metadata cleanliness
- `personas/flows/shared/prompts/persona_pass_7a_fix.md` — FU#44 register-drift extension
- `personas/flows/shared/prompts/pass_0b_non_human_organism.md` — FU#19 cleanup
- `personas/flows/shared/prompts/pass_0b_non_human_system.md` — FU#19 cleanup
- `personas/flows/shared/prompts/pass_0b_fictional.md` — FU#19 audit verdict
- `personas/scripts/invalidate_cache.py` — FU#45 helper
- `personas/scripts/sentinel_regen.py` — FU#29 narrow

### Test files

- `personas/tests/test_paths.py` — CC#1 path migration
- `personas/tests/test_chat_prompt_builder.py` — 18 tests covering FU#41 Amendments
- `personas/tests/test_bracket_strip.py` — 21 tests covering FU#33 P1 amendment
- Suite: 212/212 passing

### DON'Ts

- **No Plato re-run** without explicit operator ask. Card shipped per chat-test validation.
- **No Dostoevsky full re-run.** Phase 2 + G10 Derive re-fire are on disk.
- **No deletion of `athens-2026/` contents** without explicit operator confirmation per item.
- **No `--no-verify` / hook bypass.** If a hook fails, fix the underlying issue.
- **No push to origin/main without explicit operator confirmation.** PR #2 awaits review.
- **No Opus 4.6 for §6 of any voice's DR.** Per model-per-section policy.
- **No xattr / ACL / system-attribute modification** without explicit operator instruction.
- **No deletion of `_workspace/arch_03_baseline_snapshot/`** until further Phase L sign-off (FU#11 already pruned partially today).
- **Voices 3-12 should NOT need manual chat-artifact curation** — pipeline produces clean shipped artifacts. If a voice's chat-test fails, diagnose specifically; don't fall back to Plato-style hand-editing.
- **No commits with `--allow-empty`** unless operator explicitly asks.

---

## SECTION 9 — CALIBRATION FOR PICKUP

If picking this up cold:

- **Operator preference is direct.** When they push back ("are you sure?", "reason through each again"), the instinct is usually right even when Claude has declared work done. This entire session has multiple examples of operator pushback catching genuine over-pitches (FU#48 redundant; cache-path mistargeted; chat-only motivations applied to Voice Pipeline). Re-investigate before bulldozing.
- **Tier 3 separation.** `code/` is the git repo. `projects/` is sibling outside the repo. Voice data lives in `projects/<project-name>/`, not `code/projects/...`.
- **Voice Pipeline first, chat-test as instrument.** Voice Pipeline (runtime) consumes specific card fields via API per-step; that's the production target. Chat-test is for development feedback. Don't optimize FOR chat-test; chat is downstream of card quality.
- **Provotype framing is load-bearing.** This is a civic-design artifact for the World Beautiful Business Forum (Athens, May 7-10 2026), not a product. Visible construction is a feature.
- **Model/effort economy is a standing rule.** Per-voice pipeline operation + chat-test paste-and-assess is Sonnet-shaped. Architectural decisions on FU#42/split-card or FU#47/Step 1 mode-switching are Opus-shaped (and currently deferred per operator). Flag the shift if the operator hasn't.
- **Reflections are vendor JSON, not audio.** (Standing memory.)

---

## SECTION 10 — ACTUALLY OPEN ITEMS (not blocking voice 3-12 buildout)

🟢 Active operator decisions (not blocking):
- **AUDIENCE_BRIEF.md finalization (operator) — gates voice 3 startup**
- G8 PR #2 merge timing decision (operator review)
- Whether to copy Plato over to `athens-2026/voices/plato/` (unified panel layout vs per-voice project)

✅ **Done 2026-04-26:**
- Backup strategy: Option B landed (separate private repo `ai-assembly-athens2026-voices`)
- Athens-2026 folder cleanup: 5 stale voice dirs + legacy inputs + partial runs archived; folder ready for buildout

🟡 Trigger-based (post-voice-3 or later):
- FU#11 — further snapshot cleanup gated on Phase L sign-off
- FU#15 — Pass 5 A/B test (~2 hr + ~$10, opportunistic)
- FU#21 — runtime workstream's Step 1/Step 2 contract enforcement (runtime trigger)
- FU#22 — MergedDossier alias audit
- FU#23 — cross-repo handoff timing
- FU#24 — settings allowlist tightening
- FU#25 — split provocateur_flow.py
- FU#26 — typed PROMPTS registry
- FU#27 — runtime flow-level unit tests
- FU#28 — pipeline pass-numbering renumbering (fresh-project bootstrap = athens-2026 setup is a candidate trigger)
- FU#29 broad — any-pipeline-code-change impact analysis (post-Athens)
- FU#30 — card-richness vs runtime-quality empirical check (NOW triggerable; Plato is baseline)
- G4 — voice_distributes_across_characters schema (bound to FU#39)
- G9 — FU#2 chunked telemetry per-stage cost

🔴 Architectural / deferred per operator:
- **FU#42 — Split-card architecture.** Post-Athens default unless audience iterates substantively (operator confirmed audience stable 2026-04-26 → defer)
- **FU#47 — Voice Pipeline Step 1 mode-switching.** Voice Pipeline workstream, post-Athens
- **FU#31 — Voice-tissue validator.** Re-activate only on regression; integrate as Pass 7a rubric extension when triggered
- **FU#37 — Preserve-verbatim load-bearing markers.** Re-activate only on regression
- **FU#39 — Character-distribution stage-quoting.** Conditional; Plato chat-test passed without it
- **FU#40 full version** — voice_config flag opt-in (simple version landed)

---

*Authoritative pickup doc as of 2026-04-26 evening. Plato shipped + chat-test validated. Voice 3-12 buildout is the operational frontier. Operator has stated workflow plan; this doc translates it into concrete steps. If this diverges from FOLLOW_UPS.md's recommended order, this doc wins for 2026-04-26+ next-session scope.*
