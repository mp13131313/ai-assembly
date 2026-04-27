# Handoff prompt — Phase M session

Paste the block below into a fresh Claude Code session at
`/Users/aienvironment/Desktop/`. It replaces the pre-Phase-L handoff
prompt that launched the 2026-04-21 afternoon session.

---

You're picking up an active Phase B / Phase L session on the AI Assembly
project at `/Users/aienvironment/Desktop/AI Assembly/`. **Phase L
(first full Dostoevsky pipeline run) completed 2026-04-21 late afternoon.**
Phase M (verify + commit Phase-L fixes + merge to main + PR) is the
next gate. Before acting, read these files in priority order.

TIER 1 — REQUIRED (current-state anchoring; read every word):

1. `/Users/aienvironment/Desktop/AI Assembly/code/CLAUDE.md`
   Repo conventions, Tier 3 structure, branch state (phase-b-rebuild),
   venv rules, orientation reading order.

2. `/Users/aienvironment/Desktop/AI Assembly/code/_workspace/planning/OPEN_ITEMS.md`
   **Authoritative pickup doc.** Read the "PHASE L COMPLETE
   (2026-04-21)" top banner FIRST — it points at the L.8 report, the
   model-per-section policy, the Phase M punch list, the Phase N
   11-voice roadmap, and 7 uncommitted bug fixes in the working tree.
   Then read §"PHASE L EXECUTION FINDINGS" for the full bug catalogue
   + commit message draft.

3. `/Users/aienvironment/Desktop/AI Assembly/code/_workspace/planning/PHASE_L8_QUALITY_REPORT.md`
   **Phase L.8 quality gate comparison.** Compares the Phase B
   Dostoevsky card against the v3.7 baseline against all 5
   authoritative sources (File 2 DR technical dossier, File 3 RAG +
   constitution + reasoning templates, File 4 13-persona pipeline,
   Boddice File 5, Persona Card v2 register rules) + Pipeline v3.10
   §L.8 explicit checks. Verdict: **Phase B vindicated, proceed to
   Phase M after 6 card defects fixed + 5 code bug fixes committed
   + openai installed + validation re-run. Defect D6 (voice_temporal_stance)
   is a schema addition, not just a card edit — touches Pydantic +
   Pass 2 prompt. Surfaced by chat-test validation after the original
   handoff draft; see OPEN_ITEMS §"PHASE L CHAT-TEST VALIDATION".**

4. `/Users/aienvironment/Desktop/AI Assembly/code/_workspace/planning/EXECUTION_PLAN_phase_b.md`
   Phases A–R landed. Phase L now complete. Phase M (§"Phase M —
   verification + PR (AFTER L passes)") is the active gate.

5. `/Users/aienvironment/Desktop/AI Assembly/code/_workspace/planning/REBUILD_PLAN.md`
   Locked architectural decisions PB#1–9. Do NOT re-litigate without
   explicit reason. PB#1 cross-family validation is temporarily
   violated by Bug 8 (openai module missing) — fix at Phase M Step 1.

6. `/Users/aienvironment/Desktop/AI Assembly/code/docs/AI_Assembly_Briefing_v3_1.md`
   Project source of truth — Athens conference context, deliverables,
   success criteria.

7. `/Users/aienvironment/Desktop/AI Assembly/code/docs/AI_Assembly_Persona_Card_v2.md`
   The 37-field target spec. Card v2 register rules (first/second
   person, never third) are the Pass 7a register-check criterion.

8. `/Users/aienvironment/Desktop/AI Assembly/code/docs/AUDIENCE_BRIEF.md`
   Athens audience profile — 7-faction audience, 10 hardest-to-please
   voices. Matters for how good the Dostoevsky card has to be.

TIER 2 — THE LANDED DOSTOEVSKY CARD (read in full; this is what Phase
L produced and what Phase M is validating):

9. `/Users/aienvironment/Desktop/AI Assembly/projects/phase-l-dostoevsky/voices/fyodor_dostoevsky/07_persona_card_assembled.json`
   114 KB assembled persona card. 35 fields. `voice_basis:
   corpus-based`. `validation_status: REVISION_NEEDED` (carries 5 known
   defects from Phase L.8 — listed explicitly in OPEN_ITEMS §"PHASE M
   PUNCH LIST" Step 3).

10. `/Users/aienvironment/Desktop/Dostoevsky_Persona_Card.md`
    v3.7-paste baseline Dostoevsky card. The thing Phase B had to beat.
    Read for comparison context.

11. `/Users/aienvironment/Desktop/AI Assembly/projects/phase-l-dostoevsky/voices/fyodor_dostoevsky/05_validation/01_pass_7_pre_citation.json`
    Pass 7-pre output — 47/64 verified, 1 inconsistency (Svidrigailov
    location), 2 unverified, 11 dossier-only, 3 interpretive, plus
    `boddice_tag_flags[]` for missing [experiential_reconstruction]
    tags. Drives Defects D2 and D3 in the punch list.

12. `/Users/aienvironment/Desktop/AI Assembly/projects/phase-l-dostoevsky/voices/fyodor_dostoevsky/05_validation/03_pass_7a_cross_model.json`
    Pass 7a output — Gemini REVISION_NEEDED flagging Pass 5 register
    drift. Drives Defect D5 in the punch list.

TIER 3 — LOAD-BEARING RESEARCH (read in full; these ground every
design decision and the Phase L.8 comparison criteria):

13. `/Users/aienvironment/Desktop/compass_artifact_wf-c93e3b1d-f632-4ad0-8f5f-cf8303446984_text_markdown.md`
    File 2 — Claude DR architecture, failure modes, multi-session
    prescription. Phase L.8 criterion source.

14. `/Users/aienvironment/Desktop/AI Assembly/code/research/baseline_research/compass_artifact_wf-1e84f45b-0c9f-497a-84bc-88b7867c9a26_text_markdown.md`
    File 5 — Boddice biocultural critique. Phase L.8 criterion source.

15. `/Users/aienvironment/Desktop/AI Assembly/code/research/baseline_research/compass_artifact_wf-45560dac-98db-4376-9002-5ee8e80bb4f5_text_markdown.md`
    File 2 (the other one) — AI deep research tools field guide.

16. `/Users/aienvironment/Desktop/AI Assembly/code/research/baseline_research/compass_artifact_wf-865974da-a7be-4b7b-b770-0ec4fb7b1221_text_markdown.md`
    File 4 — 13-persona repeatable pipeline architecture. Phase L.8
    criterion source.

17. `/Users/aienvironment/Desktop/AI Assembly/code/research/baseline_research/compass_artifact_wf-cc778da2-1ac5-493e-b406-ab71d3b00234_text_markdown.md`
    File 3 — RAG + constitution + reasoning templates + persona
    vectors blueprint. Phase L.8 criterion source.

TIER 4 — AS-NEEDED REFERENCES:

18. `/Users/aienvironment/Desktop/AI Assembly/code/personas/flows/shared/paths.py`
    Canonical path helpers. Bugs 1–3 required paths.py-awareness;
    review when editing any runner.

19. `/Users/aienvironment/Desktop/AI Assembly/code/personas/flows/shared/chunk_runner.py`
    Patched for Bugs 2 + 4 (write path to voices/<slug>/02_merge/;
    acronym-plural heuristic). In working tree, uncommitted.

20. `/Users/aienvironment/Desktop/AI Assembly/code/personas/run_pass_1_1.py`
    Full rewrite per Bug 1 — thin chunk_runner delegate. In working
    tree, uncommitted.

21. `/Users/aienvironment/Desktop/AI Assembly/code/personas/run_pass_1_7.py`
    Patched for Bug 3 (paths) + Bug 5 (max_tokens 40000 → 64000). In
    working tree, uncommitted.

22. `/Users/aienvironment/Desktop/AI Assembly/code/personas/run_persona_pipeline.py`
    Patched for Bugs 6 + 7 (Pass 5 + Pass 7b subtype render). In
    working tree, uncommitted.

23. `/Users/aienvironment/Desktop/AI Assembly/code/personas/schemas/` + `pass_1_*_merge.md` + `persona_pass_*.md`
    Reference only; no changes from this session.

24. `/Users/aienvironment/Desktop/AI Assembly/code/_workspace/archive/fix-plans/SONNET_EXECUTION_PHASE_B_RESTRUCTURE.md`
    Executed Phase B restructure plan. Read only if investigating
    why the path-migration bugs got through.

25. `/Users/aienvironment/Desktop/AI Assembly/code/_workspace/planning/SONNET_PHASE_B_RESTRUCTURE_TEST_REPORT.md`
    Phase O test report claiming "128/128 passing." Phase L execution
    proved the testing gap documented in Bugs 1–9 writeup.

CURRENT STATE SNAPSHOT (2026-04-21 15:00):
- Branch `phase-b-rebuild`, HEAD `6c6c396`, **7 uncommitted changes in
  working tree** (5 code bug fixes — see OPEN_ITEMS §"Commit status").
- 128/128 unit tests passing (pre-commit state, bugs that slipped past
  tests); re-run after commit to confirm still green.
- Dostoevsky Phase L run completed: full pipeline through Derive, card
  assembled, metadata shows `validation_status: REVISION_NEEDED` due to
  6 identified defects (D1–D6) + Pass 7a Gemini flag. Chat-test
  validation (2026-04-21 evening) confirmed voice works in extended
  conversation; chat-ready JSON at `~/Desktop/dostoevsky_chat_system_prompt.json`
  (91 KB, 34 fields) includes a hand-written `voice_temporal_stance`
  field — use as reference template when adding D6 to the card schema.
- **Cost burned on Phase L**: ~$20 (within budget). **Wall time**:
  ~2 hours including ~25 min of in-flight bug fixing.
- Dostoevsky's 6 DR dossier sections in place at
  `projects/phase-l-dostoevsky/voices/fyodor_dostoevsky/01_research/04_dr_dossier/`:
  - `01_section_1.md` through `04_section_4.md`: Opus **4.6**
  - `05_section_5.md` + `06_section_6.md`: Opus **4.7** (per finalized
    model-per-section policy)
- Original user-Desktop files preserved at
  `~/Desktop/dosto dr test/dosto_brief+section{1..6}_opus{4.6,4.7}.md`.

DO NOT RE-DERIVE (settled in prior sessions OR this session):
- Prompt shape (thematic questions, 2-tag in-prose citation)
- Per-section DR necessity (single-monolithic trap empirically killed)
- PB#1–9 locked architectural decisions
- Per-voice folder layout with numbered pass-group subfolders
- Auto-detect per-section vs monolithic mode (no --mode flag)
- **Model-per-section policy**: Opus 4.6 for §1–§5, Opus 4.7 for §6 —
  finalized this session. Rationale in OPEN_ITEMS "PHASE L COMPLETE"
  banner. Applies to all 11 remaining voices.
- **Phase B vindicated as substantively superior to v3.7** — the L.8
  question "is Phase B worth the complexity?" is answered YES. See
  PHASE_L8_QUALITY_REPORT.md for criteria.

PENDING WORK (in order of execution per OPEN_ITEMS §"PHASE M PUNCH LIST"):

A. **Step 1 — openai install (1 min).** `cd personas && venv/bin/pip
   install openai==2.31.0`. Re-enables PB#1 cross-family validation.

B. **Step 2 — Commit 7 bug fixes (~15 min).** Single commit using the
   message draft in OPEN_ITEMS §"Commit status". All 5 code fixes are
   ready in the working tree.

C. **Step 3 — Fix 6 card defects (~75 min: ~45 min card edits + ~30 min
   schema change for D6).** Defects D1–D6 listed in OPEN_ITEMS §"PHASE M
   PUNCH LIST" Step 3: Svidrigailov location, experiential_reconstruction
   tags, projection_warning rename, Holbein chapter, Pass 5 register drift,
   and **D6 voice_temporal_stance schema addition** (add field to
   `schemas/pass_1_1.py` LifeScaffold OR a new location; extend
   `persona_pass_2_identity_boundaries.md` to emit it; patch the Dostoevsky
   card to include it — reference template is the hand-written version in
   `~/Desktop/dostoevsky_chat_system_prompt.json.voice_temporal_stance`).
   D6 applies to all 12 voices — schema change is once, card population
   is per-voice.

D. **Step 4 — Re-run validation passes (~15 min).** Delete cached
   05_validation/ outputs, re-run pipeline to force re-validation;
   other passes cache-hit. Expect Pass 7a to clear or produce a
   cleaner REVISION_NEEDED.

E. **Step 5 — Phase M verify + PR (~30 min).** Runtime tests green,
   personas tests green, stale-ref greps clean, `gh pr create`.

F. **Phase N — Voices 2–12 (after Phase M merges).** 11 voices × ~$18
   × ~2h = ~$200, ~22h pipeline time. Plato first as baseline sanity
   check. Per-voice protocol in OPEN_ITEMS §"PHASE N" banner.

ENVIRONMENTAL REMINDERS:
- `.env` at `code/.env`; always use `--project <path>` to override env
  default (which is `projects/test` — will resolve to wrong project if
  omitted).
- Correct invocation for Dostoevsky: `--project
  ../../projects/phase-l-dostoevsky` from within `personas/` dir.
- Two venvs (personas/venv, runtime/venv); activate the correct one.

Acknowledge what you've read and the current operational state you
understand. Then propose the order in which to execute Steps A–E.
Auto mode likely active — execute autonomously but surface cost-
relevant decisions (like re-running Pass 7a) before firing.

Most likely user requests:
(1) proceed with Steps A–E in order → Phase M merge,
(2) spot-check the Dostoevsky card against one of the 5 authoritative
    sources before committing to defect fixes,
(3) start Voice #2 (Plato) to test the architecture on a second voice
    before committing Phase M.

Do NOT propose new architecture. Do NOT re-run Pass 1.1–1.7 for
Dostoevsky (they're cached, cost ~$8 to repeat). Do NOT touch voices
other than Dostoevsky until Phase M merges.

Model/effort economy note: Phase M is largely mechanical execution
(commit, edit card fields, re-run validation, PR). Sonnet 4.6 + low
effort is the right fit for Steps A–E. Opus only warranted if the
Pass 7a re-run after defect fixes surfaces something needing judgment.
