# Next session — authoritative pickup doc (2026-04-25 evening +)

**Supersedes for next-session tracking:** `NEXT_SESSION_2026_04_25_PLATO.md` (its onboarding prompt was for the pre-Plato pickup; that work has now landed).
**Branch:** `arch-03-additive-merge` at HEAD `177365e` (pushed to `origin/arch-03-additive-merge` 2026-04-25).
**Status:** Pre-Plato hygiene complete. 3 latent pipeline bugs fixed mid-session. Plato Phase 0.5 complete; **DR sessions in flight by operator**. Pipeline run is the next operational step once §1–§6 are saved.
**Tests:** 186/186 passing. 119 commits ahead of `origin/main`.

---

## READING ORDER — only this doc is required for pickup

**Required:**

1. **THIS doc** — self-contained for operational pickup.

**Load-bearing backup references (consult only on demand):**

2. `_workspace/planning/FOLLOW_UPS.md` — per-FU# tracker. Consult when this doc cites a specific FU# (e.g. FU#33, FU#41) and you need history/definition.
3. `_workspace/planning/NEXT_SESSION_2026_04_25_PLATO.md` — prior pickup doc; its addendum (Athens-piece interpretation) and SECTION 3 (pipeline shape) are still live reference. Its onboarding prompt is **superseded** by this doc.
4. `_workspace/planning/REBUILD_PLAN.md` — PB#1–9 locked architectural decisions. Consult only if modifying pipeline architecture.

**Historical-only — IGNORE unless investigating WHY:**

All other `_workspace/planning/HANDOFF_*` docs are archival. None need reading for pickup.

---

## ONBOARDING PROMPT (copy-paste into fresh session)

```
You are resuming the AI Assembly persona-pipeline project on branch
arch-03-additive-merge. Plato Phase 0.5 is complete; manual claude.ai
DR sessions §1–§6 are in flight, run by the operator. Pipeline run is
the next operational step once all six sections are saved.

Model: Opus 4.7 + adaptive thinking is good for any architectural
re-activation (FU#33 / FU#39) or DR-output assessment. The mechanical
pipeline run + chat-test paste-and-assess is Sonnet-shaped — flag if
the operator prefers the cheaper model for that phase.

FIRST ACTIONS:

1. Read _workspace/planning/NEXT_SESSION_2026_04_25_PLATO_DR_INFLIGHT.md
   in full. That is THIS doc — the authoritative pickup point.

2. Read _workspace/planning/FOLLOW_UPS.md (per-FU# tracker, updated
   2026-04-25). Cross-reference any FU# you see in other docs there.

3. Verify repo state:
   cd "/Users/aienvironment/Desktop/AI Assembly/code"
   git log --oneline origin/main..HEAD | head -15
   git status
   cd personas && venv/bin/python -m pytest tests/ -x -q
   (Expect: 119 commits ahead of origin/main; working tree clean
    except _workspace/arch_03_baseline_snapshot/; 186/186 tests pass.)

4. Verify Plato DR session progress:
   ls "/Users/aienvironment/Desktop/AI Assembly/projects/phase-l-plato/voices/plato/01_research/04_dr_dossier/" 2>/dev/null
   - Empty / not present → operator still running DR sessions
   - 6 files (01_section_1.md … 06_section_6.md) → ready for pipeline run

5. Decide first operational action:
   - If 6 DR sections present → run pipeline (see §"PLATO RUN COMMAND")
   - If still in flight → wait + offer to spot-check any saved sections
     against §"DR SECTION OBSERVATION HOOKS" below
   - Otherwise: one of the three optional gaps in §"OPEN ITEMS"

DO NOT:
- Re-run Dostoevsky (Phase 2 + G10 Derive re-fire are both on disk;
  re-run would cost $18+ without adding signal).
- Delete the 3 snapshot dirs under _workspace/arch_03_baseline_snapshot/
  (FU#11 cleanup is gated on Phase L sign-off).
- Push to origin/main without explicit operator confirmation. The
  arch-03-additive-merge push is up to date.
- Use Opus 4.6 for §6 of any voice's DR. Per model-per-section policy,
  §6 = Opus 4.7. (§1–§5 = Opus 4.6.)
- Modify xattrs / ACLs / system attributes on any file without explicit
  ask. Flag and ask instead. (Standing rule.)

KEY FILES:
- Authoritative planning: this doc
- Per-FU tracker: _workspace/planning/FOLLOW_UPS.md
- Prior pickup (now superseded for onboarding): NEXT_SESSION_2026_04_25_PLATO.md
- Pipeline orchestrator: personas/run_persona_pipeline.py
- Chat-artifact helper: personas/flows/shared/chat_prompt_builder.py
- Chunked Pass 7-pre: personas/flows/shared/pass_7pre_chunked.py
- Pass 0b tailor (post-rewrite): personas/run_pass_0b_tailor.py +
  personas/flows/shared/prompts/pass_0b_tailor.md
- Splitter: personas/scripts/split_tailored_prompt.py
- Plato project: /Users/aienvironment/Desktop/AI Assembly/projects/phase-l-plato/

If unsure, read NEXT_SESSION_2026_04_25_PLATO.md SECTION 3 (current
pipeline shape) before guessing.
```

---

## SECTION 1 — WHAT LANDED 2026-04-25

10 commits, all pushed to `origin/arch-03-additive-merge`:

```
177365e docs(archive/session-artifacts): external Dostoevsky-card evaluation session
4ebb9d6 docs(planning/FOLLOW_UPS): Plato DR session-time observation under FU#29
ebe4aa6 fix(personas/pass_0b_header): restore 'Research [name] comprehensively...' intro in per-section §1
d8ec8b7 fix(personas/split_tailored_prompt): stop §6 at monolithic footer boundary
6caff75 fix(personas/pass_0b_tailor): enforce PB#2 base preservation architecturally
8057961 docs(planning): add model-axis requirement to Plato chat-test
260a3cf fix(personas/phase0_5): pass hostile_sources to Pass 1b Gemini render
94550dd docs(planning/FOLLOW_UPS): formalize FU#38-41 + FU#33 Phase 2 update
b16c1a3 docs(personas/HANDOFF): document 03_chat_system_prompt as 4th Derive artifact
e46277b docs(archive): reference baseline — operator Dostoevsky chat v2
```

### Path B pre-Plato hygiene (G2/G3/G6/G7/G10) — all closed

- **G7** — operator chat v2 archived as reference baseline
  (`_workspace/archive/reference-cards/dostoevsky_chat_v2_2026_04_24.json`, 131 KB)
- **G6** — `personas/HANDOFF.md` documents 4-artifact Derive layout +
  3rd consumer ("Chat deployments → paste 03_chat_system_prompt.json")
- **G2** — FU#38 / FU#39 / FU#40 / FU#41 formalized in `FOLLOW_UPS.md`
- **G3** — FU#33 updated with Phase 2 bracket-residue findings
  (3 brackets: `world.model_of_selfhood` ×2 +
  `formative_experience.lived_through_own_apparatus` ×1)
- **G10** — Dostoevsky `06_derive/` re-fire validated FU#41 chat artifact
  (25/34 byte-identical match against operator v2; restored from snapshot
  before re-run since "DO NOT re-run Dostoevsky" applied to full $18+
  cycles, not the targeted Derive-only ≈$0.50 re-fire)

### 3 latent pipeline bugs fixed mid-session

1. **`260a3cf`** — Pass 1b Gemini render missing `hostile_sources`. Phase B
   never exercised it because Dostoevsky has hostile sources; Plato (no
   hostile sources, default empty list) tripped the Jinja undefined.
   Fix: pass `hostile_sources=vi["hostile_sources"]` in
   `run_phase0_1_research.py`.

2. **`6caff75`** — **Pass 0b tailor architectural rewrite**. Operator caught
   a regression: Plato §1 was 17,245 bytes vs base 26,320 bytes (-34%);
   Dostoevsky had been +29%. Tailoring was *overwriting* base content,
   not adding to it. Rewrote the contract:

   - **Old:** LLM returns complete tailored DR prompt (free-form).
   - **New:** LLM returns structured `{section_injections, swap_test_anchor,
     thematic_note, tailoring_notes}` JSON; deterministic Python splicer
     (`splice_injections()` in `run_pass_0b_tailor.py`) iterates 6
     placeholders in REVERSE so earlier indices stay valid; post-splice
     sanity asserts no remaining placeholders + output > base length.

   18 new tests (`tests/test_pass_0b_tailor_splice.py`), including
   regression test `test_splice_prevents_plato_regression`. PB#2
   "base preservation" now an architectural guarantee, not an LLM
   instruction.

3. **`d8ec8b7`** — Splitter §6 footer duplication. Operator caught
   `OUTPUT FORMAT` appearing twice in §6. Cause: `pass_0b_human.md`
   doesn't end with `---`, so footer concatenated into §6 range. Fix:
   `_FOOTER_BOUNDARY_RE` searched only AFTER last section heading.

### Section-mode prompt parity

Operator asked whether Plato §1 prompt diverged from Dostoevsky reference
intentionally. Git archaeology (`1fd43f2` "23 fixes per tracker" +
`c60eb29` test-pinned distinction) showed most diffs (panel→scholarly
framing, section_mode conditionals, scholar-example stripping) were
**INTENTIONAL** at landing time. Only the
`Research [name] comprehensively...` intro line was an incidental drop.

Restored that one line via `ebe4aa6`:
`pass_0b_header.md` adds type-conditional intro inside section_mode §1
branch + `display_name_with_hint` default guard;
`split_tailored_prompt.py:wrap_section()` computes and passes
`display_name_with_hint`. Confirmed §3 fine; §1/§2 now match Dostoevsky
reference shape.

### External Dostoevsky-card evaluation session captured

`8057961` (planning) + `e46277b` (reference) + `177365e` (transcript):
~60K-token claude.ai-project review of operator's Dostoevsky chat v2
saved as `_workspace/archive/session-artifacts/2026-04-24_external-dostoevsky-evaluation-session.md`. 5-point in-session summary at top, line-by-line transcript at bottom. Architectural directions (post-Athens) documented: split-card design, deployment-context middle layer, Provocateur craft-hardening for voices 3–12.

### FU#29 Plato DR session-time observation

`4ebb9d6` adds an inline note: Plato §1 + §2 each ran ≈9 min on Opus 4.6;
Dostoevsky's §1 against the same prompt template had taken ≈30 min.
This is observational — not a flag — but FU#29 will want to reconcile it
when cross-voice DR-runtime variance baselining is on the table.

---

## SECTION 2 — PLATO STATE (in flight)

### Phase 0.5 complete

- `voices/plato/00_intake/02_voice_config.json` (Phase B shape: name,
  type=human, subtype=philosopher, voice_mode=philosophical,
  hostile_sources=false, corpus_constraint=full, manual_grounding,
  wikipedia_url, editorial_rationale=null,
  primary_text_sources=5 Gutenberg URLs preserved from athens-2026 era)
- `voices/plato/01_research/01_perplexity_dossier.json`
- `voices/plato/01_research/02_gemini_broad_scan.json`
- `voices/plato/01_research/03_dr_prompts/`:
  - `01_monolithic_dr_prompt.md` (post-tailor, post-splice)
  - `01_monolithic_dr_prompt.base.md` (pre-tailor reference)
  - `02_tailoring_notes.json` (audit trail of section_injections/swap_test_anchor/thematic_note actually spliced)
  - `03_section_1_dr_prompt.md` … `08_section_6_dr_prompt.md` (6 per-section prompts ready for claude.ai DR sessions)

### DR sessions in flight (operator)

Per session-time-of-summary snapshot:

- **§1** — confirmed run on Opus 4.6 (≈9 min). Also re-run on Opus 4.7
  (≈9 min) for the 4.6-vs-4.7 comparison. Outputs saved at
  `Plato DR comparison/4.6/4.6plato1.md` + `4.7/4.7plato1.md` on
  `~/Desktop/`.
- **§2** — confirmed run on Opus 4.6 (≈9 min). Compared 4.6 vs 4.7
  (`4.6plato2.md` / `4.7plato2.md`).
- **§3** — compared 4.6 vs 4.7 (`4.6plato3.md` / `4.7plato3.md`).
- **§4 / §5** — status not confirmed at time of summary.
- **§6** — must run on Opus 4.7 per model-per-section policy.

`voices/plato/01_research/04_dr_dossier/` does **not yet exist** —
operator has not started saving the canonical pipeline-input copies into
the project tree. They are still iterating in `~/Desktop/Plato DR
comparison/`.

### 4.6 vs 4.7 DR-output comparison — established pattern

Across §1/§2/§3 the 4.6-vs-4.7 outputs were **complementary, not
redundant**. Sonnet-style 4.6 → essayistic; Opus-style 4.7 →
philosophical-extension with compositional moves on canonical primitives.
The model-axis matters for chat-test (per `8057961`) AND potentially for
DR feed: open question whether Pass 1.2 / Pass 1.3 should consume both
4.6 and 4.7 dossiers and merge, or stick with single-source per §.
**Decision deferred** until operator finishes §1–§6 on the chosen primary
model and has the comparison data laid out.

### DR section observation hooks (use these if operator asks for spot-checks)

When the operator pastes a DR section output, these are the patterns to
watch for:

- **Length**: Dostoevsky § ran ≈30 min; Plato § ran ≈9 min. Watch for
  whether shorter wall time correlates with shorter content or just
  faster generation. Length isn't itself a signal — depth is.
- **Voice-tissue**: per FU#32+38, post-1950 Platonic-reception vocabulary
  (e.g. "speech-act", "performative", "deconstruction") leaking in
  → flag, but pipeline strip should catch it. Plato is the first
  philosophical voice to exercise FU#38.
- **Narrator-unification**: Socrates / Eleatic Stranger / late-Plato
  authorial position should remain *distinct*; if the DR collapses them
  into a single I, that's the FU#39 signal.
- **Translation_protocol cues**: section should produce experiential
  reconstruction with [projection_warning:] tags around modern
  inferences. The Phase 2 Dostoevsky card had 3 stray brackets (FU#33);
  worth a head-up scan in Plato's DR output too, though those usually
  manifest at Pass 2-6 not at DR.

### PLATO RUN COMMAND (when 6 sections saved)

```bash
cd "/Users/aienvironment/Desktop/AI Assembly/code"
set -a && source .env && set +a
cd personas
venv/bin/python run_persona_pipeline.py "Plato" \
  --project "/Users/aienvironment/Desktop/AI Assembly/projects/phase-l-plato"
```

Expected: ≈$18–22 + ≈2 hr wall time. Watch for FU#38 prompt-strip
behavior (philosophical voice, first exercise) and FU#2 chunked Pass 7-pre
on a non-narratival voice. If REVISION_NEEDED → FU#13 linear
patcher fires automatically.

After completion, the four Derive artifacts land at
`voices/plato/06_derive/`. Chat-test workflow per FU#41 + post-Athens
notes: paste `03_chat_system_prompt.json` into both an Opus and a Sonnet
claude.ai project, probe in Provocateur-register first
(*"You've just received the program for the AIssembly panel in Athens…"*),
philosophical-meditation register second (*"What is justice?"*).

---

## SECTION 3 — OPEN ITEMS

### 🔴 Operational next step

- **Plato pipeline run** — gated on operator finishing DR §1–§6.
- **Plato chat-test (Provocateur + meditation register × Sonnet + Opus)** —
  after pipeline. Per `8057961`, model axis is mandatory.

### 🟡 Open if operator wants to use the time

- **G4** — `voice_distributes_across_characters` schema field +
  voice_config default. Prerequisite for FU#39 if Plato signals
  narrator-unification. ≈30 min. Cheap to land before signal.
- **Dual-feed Pass 1.2/1.3 from 4.6+4.7 DR dossiers** — speculative;
  weigh value vs. complexity *only* if operator decides the comparison
  data justifies it. Not in scope until Plato run completes.
- **FU#15** Pass 5 A/B test on low-stakes voice — ≈2 hr + ≈$10. Polish.

### 🔵 Conditional on Plato signal

- **FU#39** Character-distribution stage-quoting. Activate IF Plato
  collapses Socrates/Stranger/late-Plato into a single I. Implementation:
  Pass 4a `characteristic_moves` extension with voice-type branching.
  ≈3–4 hr.
- **FU#33** Patcher scope extensions (bracket-residue scan,
  INCONSISTENT-flag ingestion, transliteration, spell-check). Activate IF
  Plato's card shows mechanical defects FU#32 regeneration didn't clean.
  ≈3–4 hr.

### 🔵 Post-Plato (architectural; from external review)

Captured in
`_workspace/archive/session-artifacts/2026-04-24_external-dostoevsky-evaluation-session.md`:

- **Split-card architecture** — separate "voice card" (canonical sources,
  primitives, characteristic moves) from "deployment card" (audience,
  occasion, register). Card v2 conflates them; the housing-panel mode
  divergence makes that visible.
- **Deployment-context middle layer** — explicit deployment-context
  artifact between persona card and runtime, parameterizing register +
  audience + occasion separately from voice-stable fields.
- **Provocateur craft-hardening for voices 3–12** — bake the
  "Athens-piece" task-register lessons into the Provocateur prompt
  itself (concrete-situation framing, not philosophical-meditation
  framing).

These are post-Athens directions; do not start until Plato is signed off
and at least 2 more voices are end-to-end.

### 🔵 Deferred / trigger-based

- **FU#11** snapshot cleanup — gated on Phase L sign-off
- **G8** merge `arch-03-additive-merge` → `origin/main` — gated on
  Phase L sign-off + PR review
- **FU#19 / 22 / 30 / 31 / 37 / 40** — re-activate only on specific
  conditions (see `FOLLOW_UPS.md`)
- **CC#1** `05_primary_text_urls.json` relocation — fresh-project bootstrap

---

## SECTION 4 — REPO STATE SNAPSHOT (2026-04-25 end of session)

- **Branch:** `arch-03-additive-merge`
- **HEAD:** `177365e`
- **Ahead of origin/main:** 119 commits
- **Pushed to origin/arch-03-additive-merge:** all 10 today's commits +
  prior pushes
- **Tests:** 186/186 passing (+24 since previous handoff: +18 splice +
  +6 incremental)
- **Working tree:** clean except `_workspace/arch_03_baseline_snapshot/`
- **Plato project tree (outside git per Tier 3):**
  `projects/phase-l-plato/voices/plato/00_intake/` +
  `01_research/{01_perplexity_dossier.json, 02_gemini_broad_scan.json, 03_dr_prompts/}`.
  `04_dr_dossier/` not yet created — DR sessions in flight.

### Cumulative session work (2026-04-25)

- 10 commits
- 24 new tests (mainly splice regression coverage)
- 1 new module worth flagging (architectural rewrite of
  `run_pass_0b_tailor.py` + `splice_injections()`)
- 3 new prompt files updated (`pass_0b_tailor.md`, `pass_0b_header.md`,
  `split_tailored_prompt.py`)
- 1 new reference card archived
- 1 new session-artifact archived (60K-token external evaluation)

---

## SECTION 5 — KEY FILES + DON'TS (consolidated)

### Authoritative

- This doc — pickup and onboarding
- `_workspace/planning/FOLLOW_UPS.md` — per-FU# tracker
- `_workspace/planning/NEXT_SESSION_2026_04_25_PLATO.md` — superseded for
  onboarding, but **SECTION 3 (pipeline shape)** + **ADDENDUM
  (Athens-piece interpretation)** remain live reference

### Code touched this session

- `personas/run_pass_0b_tailor.py` — architectural rewrite (deterministic
  splicer)
- `personas/flows/shared/prompts/pass_0b_tailor.md` — new structured
  injections schema
- `personas/scripts/split_tailored_prompt.py` — footer-boundary fix +
  `display_name_with_hint` plumb-through
- `personas/flows/shared/prompts/pass_0b_header.md` — section-mode §1
  intro line + Jinja default guard
- `personas/run_phase0_1_research.py` — Pass 1b `hostile_sources` plumb
- `personas/tests/test_pass_0b_tailor_splice.py` — 18 splice tests
- `personas/HANDOFF.md` — 4-artifact Derive doc

### Archive additions

- `_workspace/archive/reference-cards/dostoevsky_chat_v2_2026_04_24.json`
- `_workspace/archive/session-artifacts/2026-04-24_external-dostoevsky-evaluation-session.md`

### DON'TS

- **No Dostoevsky full re-run.** Phase 2 + G10 Derive re-fire are on disk.
- **No `--no-verify` / hook bypass.** If a hook fails, fix the underlying
  issue.
- **No push to origin/main without explicit operator confirmation.**
  `arch-03-additive-merge` push is up to date.
- **No Opus 4.6 for §6 of any voice's DR.** Per model-per-section policy
  §6 is Opus 4.7. (§1–§5 are Opus 4.6.)
- **No xattr / ACL / system-attribute modification** without explicit
  operator instruction. Flag and ask. (Standing rule.)
- **No deletion of `_workspace/arch_03_baseline_snapshot/`** until Phase L
  sign-off (FU#11 trigger).
- **No starting voices 3–12** until Plato signal is assessed.

---

## SECTION 6 — POSTSCRIPT: CALIBRATION FOR PICKUP

If you are picking this up cold:

- **Operator preference is direct.** When they push back ("i have a
  feeling…", "go through all commits"), the instinct is usually right
  even if you've already declared the work done. This session caught a
  regression and a section-mode mis-framing that way. Don't bulldoze —
  re-investigate.
- **Tier 3 separation is real.** `code/` is the git repo. `projects/` is
  a sibling outside the repo. Plato data lives in `projects/phase-l-plato/`,
  not `code/projects/…`.
- **Reflections are vendor JSON, not audio.** (Standing memory.)
- **Provotype framing is load-bearing.** This is a civic-design artefact
  for the World Beautiful Business Forum (Athens, May 2026), not a
  product. Visible construction is a feature.
- **Model/effort economy is a standing rule.** Mechanical Plato pipeline
  operation + chat-test paste-and-assess is Sonnet-shaped. Architectural
  decisions on FU#33/FU#39/split-card are Opus-shaped. Flag the shift if
  the operator hasn't.

---

*Authoritative pickup doc as of 2026-04-25 evening. Plato DR sessions in
flight; pipeline run is the next operational step. If this diverges from
`FOLLOW_UPS.md`'s recommended order, this doc wins for 2026-04-25+
next-session scope.*
