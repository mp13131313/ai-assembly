# Handoff prompt — Pipeline Review session

Paste the block below into a fresh Claude Code session at
`/Users/aienvironment/Desktop/`. It replaces the Phase M handoff
prompt that launched the 2026-04-21 afternoon-evening session.

---

You're picking up an active **pipeline review session** on the AI
Assembly project at `/Users/aienvironment/Desktop/AI Assembly/`.
**Phase M (Phase-B rebuild + Phase-L Dostoevsky validation + defect
fixes + prompt-level learnings) shipped on 2026-04-21 — PR #1 merged
to `main` at commit `07f989a`.** After Phase M merged, a step-by-step
review of every LLM call and Jinja render in the persona pipeline
began; Waves 1 + 2 (partial) are done, the rest is pending. Before
acting, read these files in priority order.

TIER 1 — REQUIRED (current-state anchoring; read every word):

1. `/Users/aienvironment/Desktop/AI Assembly/code/CLAUDE.md`
   Repo conventions, Tier 3 structure, branch state (now `main`),
   venv rules, orientation reading order.

2. `/Users/aienvironment/Desktop/AI Assembly/code/_workspace/planning/PIPELINE_REVIEW_FIXES.md`
   **THE AUTHORITATIVE PICKUP DOC FOR THIS REVIEW.** Committed at
   `e0880e2`. Contains:
   - Pipeline step-map legend at the top (clarifying the
     `1a/1b/1c/1d` family vs. `1.1-1.7` merge family naming
     confusion — renumbering proposal deferred)
   - Cross-pass architectural proposals (`1-arch-01` —
     `curated_corpus_passages` should flow from Pass 1d not Pass 1.6)
   - Cross-template XREF harmonizations (8 patterns where one
     variant has a gold-standard shape others should lift)
   - Per-step review blocks for Steps 1-19 (Wave 1 all 17 + Wave 2
     Steps 18-19)
   - Severity breakdown: 0 CRITICAL · 2 HIGH (1d-06 + 1-arch-01) ·
     25 MEDIUM · 39 LOW · 1 REJECTED · 3 RETRACTED
   - 66 PROPOSED fixes total
   - Panel composition confirmed (12 voices: Plato, Cleopatra,
     Ibn Battuta, Scheherazade, Fyodor Dostoevsky, Hannah Arendt,
     Ada Lovelace, Peter Thiel, Bob Marley, Audrey Tang, Whanganui,
     Octopus)

3. `/Users/aienvironment/Desktop/AI Assembly/code/_workspace/planning/OPEN_ITEMS.md`
   Authoritative pickup doc for the broader project. Read the
   "PHASE L COMPLETE" and "PHASE N" banners for context. Phase M
   is DONE (not the next gate anymore — next gate is Phase N Plato
   build after review finishes + fixes apply).

4. `/Users/aienvironment/Desktop/AI Assembly/code/_workspace/planning/PHASE_L8_QUALITY_REPORT.md`
   Phase L.8 quality gate comparison against the 5 authoritative
   sources. Read for the Phase-B-is-vindicated verdict and the
   review-criterion framing. Some fixes in the tracker originated
   in this report.

5. `/Users/aienvironment/Desktop/AI Assembly/code/_workspace/planning/REBUILD_PLAN.md`
   Locked architectural decisions PB#1–9. **DO NOT re-litigate**
   without explicit reason. PB#1 (3 research sources only:
   Perplexity + Claude DR + Gemini) constrains the Pass 1b review
   — Gemini's research-backed role is breadth-scan-only per File 4
   (see DO NOT RE-DERIVE below).

6. `/Users/aienvironment/Desktop/AI Assembly/code/docs/AI_Assembly_Briefing_v3_1.md`
   Project source of truth — Athens conference context, deliverables,
   success criteria. Hardest-to-please voices inform review bar.

7. `/Users/aienvironment/Desktop/AI Assembly/code/docs/AI_Assembly_Persona_Card_v2.md`
   The 37-field target spec. Card v2 register rules (first/second
   person, never third-person scholarly description) shape many
   review verdicts.

8. `/Users/aienvironment/Desktop/AI Assembly/code/docs/AUDIENCE_BRIEF.md`
   Athens audience profile — 7-faction audience, 10 hardest-to-please
   voices. Matters for "is this prompt strong enough" judgments.

TIER 2 — THE PHASE-L DOSTOEVSKY ARTIFACTS (reference material for
quality calibration during review):

9. `/Users/aienvironment/Desktop/AI Assembly/projects/phase-l-dostoevsky/voices/fyodor_dostoevsky/07_persona_card_assembled.json`
   ~115 KB assembled card, post-Phase-M defect fixes applied
   manually. `validation_status: REVISION_NEEDED` — carry-forward
   from Phase L, not an active blocker. This is what the pipeline
   produced end-to-end.

10. `/Users/aienvironment/Desktop/Dostoevsky_Persona_Card.md`
    v3.7-paste baseline. Read only if comparing approaches.

11. `/Users/aienvironment/Desktop/AI Assembly/projects/phase-l-dostoevsky/voices/fyodor_dostoevsky/05_validation/01_pass_7_pre_citation.json`
    Pass 7-pre output. Reference when Step 36 (Pass 7-pre prompt
    review) fires.

12. `/Users/aienvironment/Desktop/AI Assembly/projects/phase-l-dostoevsky/voices/fyodor_dostoevsky/05_validation/03_pass_7a_cross_model.json`
    Pass 7a output. Reference when Step 38 (Pass 7a) fires.

TIER 3 — LOAD-BEARING RESEARCH (read in full; these ground many
review verdicts):

13. `/Users/aienvironment/Desktop/compass_artifact_wf-c93e3b1d-f632-4ad0-8f5f-cf8303446984_text_markdown.md`
    File 2 — Claude DR architecture, failure modes, multi-session
    prescription. Drives convergence-trap countermeasures assessed
    across Pass 0b + merge reviews.

14. `/Users/aienvironment/Desktop/AI Assembly/code/research/baseline_research/compass_artifact_wf-1e84f45b-0c9f-497a-84bc-88b7867c9a26_text_markdown.md`
    File 5 — Boddice biocultural critique. Drives `[experiential_
    reconstruction]` / `[projection_warning]` tag discipline and
    §13/§14/§15 rubric shape.

15. `/Users/aienvironment/Desktop/AI Assembly/code/research/baseline_research/compass_artifact_wf-45560dac-98db-4376-9002-5ee8e80bb4f5_text_markdown.md`
    File 2 (other) — AI deep research tools field guide.

16. `/Users/aienvironment/Desktop/AI Assembly/code/research/baseline_research/compass_artifact_wf-865974da-a7be-4b7b-b770-0ec4fb7b1221_text_markdown.md`
    **File 4 — 13-persona pipeline architecture. CRITICAL for
    reviewing Pass 1b.** File 4 documents Gemini as "unusable for
    basic humanities research due to unreliable sourcing"; drove
    the research-sanity-check that retracted 3 Pass 1b elevation
    fixes and kept Gemini in breadth-scan lane.

17. `/Users/aienvironment/Desktop/AI Assembly/code/research/baseline_research/compass_artifact_wf-cc778da2-1ac5-493e-b406-ab71d3b00234_text_markdown.md`
    File 3 — RAG + constitution + reasoning templates + persona
    vectors blueprint.

TIER 4 — REVIEW-SPECIFIC FILES (read per step as you resume):

18. **All Phase 0/0.5 prompts (Steps 1-17 already reviewed).** Under
    `/Users/aienvironment/Desktop/AI Assembly/code/personas/flows/shared/prompts/`:
    `pass_0a_voice_config.md`, `persona_pass_1a_*.md` (4 variants),
    `persona_pass_1b_*.md` (4 variants), `pass_0b_dr_prompt.md`,
    `pass_0b_header.md`, `pass_0b_{human,non_human_organism,non_human_system,fictional}.md`,
    `pass_0b_footer.md`, `pass_0b_tailor.md`. **You do NOT need to
    re-read these unless surfacing something new.** The tracker has
    the review blocks.

19. `/Users/aienvironment/Desktop/AI Assembly/code/personas/flows/shared/chunk_runner.py`
    Shared harness for chunked merge passes 1.1-1.6. **Read at
    Step 20 resumption** — architecture already confirmed (4-block
    prompt + Opus 4.7 streaming + thinking + max_tokens=32000 +
    Pydantic validation + 1-retry-with-critique + per-section DR
    auto-detect). Serves as the invariant for Steps 20-25.

20. `/Users/aienvironment/Desktop/AI Assembly/code/personas/run_pass_1_all.py`
    Orchestrator: chunks 1.1-1.6 in parallel (max_workers=3), then
    1.7 sequentially. Read at Step 20.

21. **Pass 1 merge prompt files (Steps 20-26 pending):**
    - `pass_1_1_merge.md` (BIOGRAPHICAL — Step 20)
    - `pass_1_2_merge.md` (INTELLECTUAL — Step 21)
    - `pass_1_3_merge.md` (REASONING — Step 22)
    - `pass_1_4_merge.md` (VOICE — Step 23)
    - `pass_1_5_merge.md` (BOUNDARIES — Step 24)
    - `pass_1_6_merge.md` (CORPUS — Step 25)
    - `pass_1_7_coherence.md` (COHERENCE — Step 26)

22. **Phase 2 generation prompts (Steps 27+ pending):**
    - `persona_pass_2_identity_boundaries.md`
    - `persona_pass_3_intellectual_core.md`
    - `persona_pass_4a_voice.md`
    - `persona_pass_4b_artifact.md`
    - `persona_pass_5_engagement.md`
    - `persona_pass_6_corpus_curation.md` (or equivalent)
    - Coherence-threading logic inside `run_persona_pipeline.py`

23. **Phase 3 validation prompts (Steps 36-40 pending):**
    - `persona_pass_7pre_citation.md`
    - `persona_pass_7_anachronism.md`
    - `persona_pass_7a_cross_model.md`
    - `persona_pass_7b_smoke_test.md`
    - `persona_pass_7c_negative.md`

24. **Phase 4 derive prompts (Step 41 pending):**
    - Whatever's in `flows/shared/prompts/` for the Derive step.

25. `/Users/aienvironment/Desktop/AI Assembly/code/personas/flows/shared/clients.py`
    LLM wrappers — defaults for `call_claude` / `call_perplexity` /
    `call_gemini` / `call_openai`. Reference when any step's
    model/config needs verification.

CURRENT STATE SNAPSHOT (review-resumption point):

- **Branch:** `main` at commit `e0880e2` (tracker commit) → ahead of
  origin by 1; pipeline-review tracker committed 2026-04-21 evening.
- **Working tree:** `HANDOFF_PHASE_M.md` + this handoff file as
  untracked ephemeral session artifacts. Everything substantive is
  committed.
- **Review coverage:**
  - Wave 1 complete: Steps 1-17 (Phase 0 + 0.5 — voice config,
    Perplexity, Gemini, Pass 0b wrapper/header/4 bodies/footer/tailor)
  - Wave 2 partial: Steps 18-19 (Pass 1c fetch, Pass 1d excerpt-select)
    done. **Step 20 in progress** — Pass 1.1 BIOGRAPHICAL merge
    architecture confirmed (chunk_runner.py, run_pass_1_all.py,
    run_pass_1_1.py, schemas/pass_1_1.py all read); **prompt detail
    review of `pass_1_1_merge.md` is the next action.**
- **Fix counts:** 66 PROPOSED · 1 REJECTED · 3 RETRACTED
- **Model/effort this session ran:** Claude Opus 4.7 (1M) with
  adaptive thinking. See "MODEL + EFFORT" section below.

WHAT'S DONE — DON'T RE-RUN:

- **Phase M shipped 2026-04-21.** PR #1 merged to main (`07f989a`).
  Don't re-review Phase M steps (card defects D1-D6 fixed, prompt
  learnings 0b-11 variants, tests green, PR opened + merged).
- **Steps 1-17** (Wave 1) completed with full review blocks in
  `PIPELINE_REVIEW_FIXES.md`. Don't re-read every prompt to redo
  these.
- **Steps 18-19** (Wave 2 partial) completed. Pass 1c fetch + Pass
  1d excerpt selection reviewed.
- **Architecture confirmation for Wave 2 merge**: chunk_runner.py
  reads all 3 research sources (Perplexity + Claude DR + Gemini)
  per chunk, calls Opus 4.7 streaming + adaptive thinking +
  max_tokens=32000, Pydantic-validates output, retries once with
  critique on validation fail. Parallel 1.1-1.6 (max_workers=3),
  sequential 1.7. **Merge architecture is the user's biggest
  concern; confirmation is done; prompt reviews are next.**
- **Research sanity-check**: Gemini stays in breadth-scan lane per
  File 4. Prior elevation proposal (1b-R1/R2/R3) retracted.
  `gemini-2.5-pro` kept per user preference.
- **Panel composition** (12 voices) confirmed.

DO NOT RE-DERIVE:

- Pipeline step-map legend (tracker top)
- PB#1–9 locked architectural decisions
- Per-voice folder layout / Tier 3 project separation
- Model-per-section policy (§1-§5 Opus 4.6, §6 Opus 4.7) for manual
  DR — this is SETTLED
- Gemini-for-breadth-not-depth finding (File 4)
- Pass 1.6 → Pass 6 canonical-passage flow understanding (NOT
  Pass 1d — Pass 1d feeds Pass 4a voice analysis only; but
  `1-arch-01` proposes restructuring this)

PENDING WORK (in order of original task description):

A. **Step 20 finish** — Pass 1.1 BIOGRAPHICAL merge prompt detail
   review. Architecture already confirmed (Wave 2 wave-3 concern
   addressed). `pass_1_1_merge.md` is 340 lines, needs full read
   + per-step review block.

B. **Steps 21-26** — Pass 1.2-1.7 merge prompts. 7 files, similar
   structure. Each step gets a review block in the tracker. The
   **corpus utilization question** lives here — for each chunk ask:
   is the prompt actually using the full dossier or just slicing
   thin? Per-section DR auto-detect means Perplexity §N + Claude-DR
   §N + full Gemini feed into chunk N — verify this is genuinely
   used, not just referenced.

C. **Wave 3 — Phase 2 generation** (Steps 27-35, approx):
   - Pass 2 Identity & Boundaries (+ its user prompt + CT2)
   - Pass 3 Intellectual Core (+ user + CT2+3)
   - Pass 4a Voice (+ user + CT2+3+4a) — primary_texts consumer
   - Pass 4b Artifact (+ user + CT2+3+4)
   - Pass 5 Engagement
   - Pass 6 Corpus Curation — canonical-passages writer (key to
     `1-arch-01` proposal)
   - Coherence-threading logic in run_persona_pipeline.py
   The **temporal-stance revisit** lives here (when Pass 2 is
   reviewed — `voice_temporal_stance` field the user wants to
   reconsider).

D. **Wave 4 — Phase 3 validation** (Steps 36-40):
   Pass 7-pre, Pass 7-anachronism, Pass 7a cross-model, Pass 7b
   smoke test, Pass 7c negative constraints. Each has a prompt +
   user + potential schema.

E. **Wave 5 — Phase 4 derive + orchestration** (Step 41):
   Derive (provocateur profile + evaluation rubric) + final
   orchestration audit of `run_persona_pipeline.py` control flow,
   revision loop, cache logic.

F. **Wrap-up**: final review summary, card-size question
   (Dostoevsky is 115KB — right allocation? compared to File 2's
   Lister study ~40KB), consolidated implementation plan from
   approved fixes.

REVIEW METHODOLOGY — THE CRITICAL INSTRUCTION:

This is how each step MUST be reviewed. The tracker shows the
format used for Steps 1-19; continue identically.

**Per-step review format:**

```
## Step N — Pass X.Y / <name>

**Does:** <one-line what this step actually does>
**Mechanism:** <LLM call | Jinja render | hybrid | HTTP fetch |
  validator | orchestrator>
**Config (LLM steps):** table with provider · model · thinking ·
  max_tokens · temperature · retry · cost estimate · runs-per-voice
**Prompt file(s):** linked path(s) — ALWAYS READ IN FULL
**What it reads:** input artefacts
**What it writes:** output artefacts

**Prompt structure walkthrough:** block-by-block summary of the
prompt, line-referenced.

**Review — model + config:** opinion with reasoning. Is this model
right for the task? Are max_tokens / temperature / thinking set
appropriately? Any cost-economy flag?

**Review — prompt (critical reading):** strengths + issues, each
line-referenced. Flag: leftovers from prior versions, internal
contradictions, missing pieces, voice-type-specific gaps,
cross-template XREF observations.

**Review — research utilisation:** only for steps that consume
the dossier. Is the prompt actually using the 3 research sources
well, or under-reading them?

**Verdict:** KEEP / TUNE / REWRITE / NEEDS-DECISION — short rationale

**Fixes:** tracker entries (ID / Severity / File:line / Change /
Status) — written into `PIPELINE_REVIEW_FIXES.md` immediately,
not left in conversation.
```

**Severity calibration (critical):**

- **CRITICAL** — blocks Phase N, breaks pipeline, corrupts card
- **HIGH** — quality ceiling risk or architectural flaw; not a
  blocker but materially worth addressing. Includes architectural
  proposals (1d-06, 1-arch-01).
- **MEDIUM** — leftover that should be fixed before scaling to 11
  more voices; tune-level prompt improvements
- **LOW** — cosmetic polish, maintenance, not urgent

**Be skeptical:** "is it broken?" and "is it leveraging the upstream
research well?" are different questions. The user pushed back on
Step 19 Pass 1d being "KEEP with LOW fixes" — they were right. The
honest calibration: current verdict upgraded to HIGH architectural
(fuzzy-match proposal). Remain open to this kind of correction on
remaining steps, especially the merge (Pass 1.1-1.7) where the
user's biggest concern lives — the upstream research investment
needs to actually feed through.

**Always ask per step:**
1. Is this the right model + effort for the task?
2. Is this prompt the right shape / length / discipline?
3. Is the upstream research (dossier / fetched corpus / prior pass
   outputs) actually being used well by this prompt?
4. What downstream does this step feed, and is the interface clean?

**Cross-template harmonization (important):** as patterns appear
across voice-type variants, log them in the tracker's "Cross-template
patterns to harmonize" section as XREF entries. Prevents drift at
implementation time.

**When proposing architectural changes:** write them up in the
tracker's "Cross-pass architectural proposals" section (like
1-arch-01). Include scope, cost of refactor, why-not-now
justification.

MODEL + EFFORT STRATEGY FOR THE REVIEW:

This review runs at Opus 4.7 (1M) + adaptive thinking for the
judgment-heavy steps. Downshift to Sonnet 4.6 + low effort for
mechanical pattern-application.

- **Stay on Opus + thinking for:**
  - Step 20 Pass 1.1 merge prompt (architectural judgment)
  - Steps 21-26 merge prompts if novel prompts with structural
    decisions (probably most)
  - Wave 3 Phase 2 generation (Pass 2, 4a most judgment-heavy)
  - Wave 4 validation architecture
  - Any step where a new architectural proposal might emerge

- **Switch to Sonnet + low for:**
  - Voice-type-variant reviews after the first variant of a family
    is done (pattern established, just applying)
  - Coherence-threading and simple user-prompt reviews
  - Footer / short-prompt reviews

Self-flag periodically: "is this step Opus-shaped or Sonnet-shaped?"
— match the model to the task. The user has said "I want you to
proactively check whether the model + effort level is well-matched."

ENVIRONMENTAL REMINDERS:

- `.env` at `code/.env`; use `--project <path>` for Dostoevsky
  (`projects/phase-l-dostoevsky`) or `projects/test` default
- Two venvs (personas/venv, runtime/venv); activate correct one
- `gh` CLI installed at `~/.local/bin/gh` with authenticated token
  (fine-grained PAT — expiring 2026-04-28 unless rotated)
- Git credential helper configured via `gh auth setup-git` —
  `git push/pull` work with gh's token

TRACKER MAINTENANCE:

- After each step review, APPEND the review block + fix entries
  to `PIPELINE_REVIEW_FIXES.md` before moving on
- Update "Consolidated totals" counts every time a fix is logged
- Keep step-map legend at the top in sync
- Commit the tracker periodically (not every step — perhaps every
  wave completion) so progress doesn't sit in the working tree
- The tracker file is `_workspace/planning/PIPELINE_REVIEW_FIXES.md`
  — git-tracked, committed at `e0880e2` as of handoff

ACKNOWLEDGE + PROPOSE ORDER:

Read the tracker first — it contains the map, the per-step reviews,
and the architectural proposals. Then:

(1) Acknowledge what you've read and the current review state
(2) Confirm you understand the per-step review methodology
(3) Propose resumption approach — default is step-by-step from
    Step 20 (Pass 1.1 merge prompt detail), but user may want to
    fast-forward merge block (Steps 20-26 as one extended pass on
    the user's biggest concern) or skip to implementation-of-fixes
    pass.

MOST LIKELY USER REQUESTS:

(1) Continue step-by-step from Step 20 (Pass 1.1 merge prompt
    detail) — default cadence, one step per turn
(2) Fast-forward Wave 2 merge reviews (Steps 20-26) as a deeper
    single pass on the merge architecture concern, with the 6
    prompts reviewed as a batch
(3) Pause review here; run the implementation pass — read the
    tracker's APPROVED/PROPOSED fixes and apply them before
    continuing the review
(4) Jump to a specific step of interest (e.g., Pass 4a Voice
    because it's where primary-text usage lives)

DO NOT:

- Re-review Steps 1-19 — they're in the tracker. Verdicts are
  calibrated. Adding to them only on user prompt to dig deeper on
  a specific point.
- Re-litigate PB#1-9 or the Gemini-breadth-scan finding
- Skip reading prompt files fully — "I already have it in context"
  claims from the prior session are invalidated on fresh start;
  always fresh-read per step
- Implement fixes during review without user approval — review
  produces proposals; implementation is a separate pass
- Touch voices other than the current review scope

END OF HANDOFF.
