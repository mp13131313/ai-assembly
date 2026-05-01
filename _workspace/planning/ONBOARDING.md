# Onboarding — planning folder index

**Living document.** Thin shell pointing at the two workstream subfolders + the cross-cutting rules that apply across both. The substantive onboarding content lives in the subfolder ONBOARDINGs.

---

## What this project is

A provotype for the **World Beautiful Business Forum** AI Democracy Marathon, Athens, **May 7–10, 2026**. Ten non-human voices (a river, an octopus, Plato, Hannah Arendt, and 6 others) read the day's human panel transcripts overnight and produce written responses — provocations, queries, reflections — that re-enter the human conversation the following morning via Substack read-throughs.

Civic-design artifact, not a product. Visible construction is a feature.

For project-wide context (filesystem layout, Tier 3 separation, two venvs, cross-repo handoff, where specs live, orientation reading order): **`code/CLAUDE.md`**.

---

## Two workstreams

The work splits cleanly into two parallel subfolders:

| Subfolder | What it covers | Owner thread |
|---|---|---|
| **`runtime/`** | overnight pipeline: transcription, researcher, provocateur, voice pipeline (steps 1+2+3 + validation + continuity), publish, downstream (editor / broadsheet / microsite / Substack / closing show / Day 4 goodbye) | runtime thread |
| **`voices/`** | persona-card pipeline: voice configs, deep research, chunked merge, generation passes, validation, derive, card assembly. The pre-Athens build that produces the cards runtime consumes | persona thread (also called "voices" thread) |

Each subfolder has the same shape:

```
<subfolder>/
├── HANDOFF*.md      session-state-of-the-moment (dated)
├── ONBOARDING.md    durable scaffolding (orientation, architecture, common operations)
└── OPEN_ITEMS.md    authoritative open-items tracker (gating decisions, blockers, hygiene)
```

**For runtime work:** read `runtime/ONBOARDING.md` first, then `runtime/OPEN_ITEMS.md`, then the latest dated `runtime/HANDOFF_*.md`.

**For voice-build work:** read `voices/ONBOARDING.md` first, then `voices/OPEN_ITEMS.md`, then `voices/HANDOFF.md`.

---

## Cross-cutting tracker (frozen)

**`FOLLOW_UPS.md`** at this folder root is the **frozen historical ledger** of FU#1–62 (as of 2026-05-01). Existing FU# references in code, commits, prompts, and docs resolve to entries there — no new entries are added.

**For NEW items going forward,** file in the relevant subfolder OPEN_ITEMS in the appropriate section:
- Runtime: `runtime/OPEN_ITEMS.md` (sections A gating / B Athens-blocking / C hygiene / E docs pending)
- Voices: `voices/OPEN_ITEMS.md` (per its structure)

Cross-cutting items file in BOTH subfolder OPEN_ITEMS with mutual cross-references. Cross-cutting **rules / calibration** (not items) file in this doc's §"Cross-cutting DON'Ts" or §"Cross-cutting calibration".

No new FU# numbering. See `code/CLAUDE.md` §"Planning / tracking conventions" for the full workflow.

---

## Cross-cutting DON'Ts (apply in both workstreams)

Standing rules. Operator-level ones come from `~/.claude/CLAUDE.md` (global) and the project's calibration history.

- **No `--no-verify` / hook bypass.** If a hook fails, fix the underlying issue.
- **No push to `origin/main`** without explicit operator confirmation.
- **No commits with `--allow-empty`.**
- **No xattr / ACL / system-attribute modification** without explicit operator instruction.
- **No deletion of athens-2026 contents** without explicit operator confirmation per item.
- **No real-person names in the 4 deployment-context JSONs** at `<PROJECT_ROOT>/`: `conference_facts.json`, `audience_profile.json`, `panel_roster.json`, `council_config.json`. Use generic descriptions ("a former PM," "a leading cognitive-warfare theorist").
- **No Plato re-run without explicit ask.** Card shipped per chat-test 2026-04-26.
- **No Dostoevsky full re-run.** Phase 2 + G10 Derive re-fire on disk in `phase-l-dostoevsky/`.
- **No Opus 4.6 for §6 of any voice's DR.** Per model-per-section policy: §6 uses Opus 4.7 (Phase L empirical: 4.6 produces reader's-intro on §6).
- **No hand-authoring voice_configs bypassing Pass 0a.** If review disagrees, edit and re-run Pass 0a.
- **Reflections are vendor JSON, not audio.** Stage 0 transcription does not apply.
- **Never optimize FOR chat-test.** Voice Pipeline (runtime) consumes specific card fields via API per-step; that's the production target. Chat-test is a development feedback instrument.

Subfolder-specific DON'Ts live in the respective `runtime/ONBOARDING.md` and `voices/ONBOARDING.md`.

---

## Cross-cutting calibration

- **Operator preference is direct.** When pushed back ("are you sure?", "reason through each again"), the instinct is usually right even when work has been declared done. Re-investigate before bulldozing.
- **Provotype framing is load-bearing.** Civic-design artifact for WBBF Athens 2026, not a product. Visible construction is a feature.
- **Athens needs full runtime stack ready, not just cards.** When recommending build-side improvements (LLM-as-judge, FU#50(1) Pydantic enforcement, FU#42 split-card, etc.), check whether they delay runtime work that's already on the critical path. Surface runtime gaps proactively.
- **Voice Pipeline first, chat-test as instrument.** Voice Pipeline (runtime) consumes specific card fields via API per-step; that's the production target.
- **Model/effort economy.** Per-voice pipeline operation + chat-test paste-and-assess is Sonnet-shaped. Architectural decisions and complex code reading are Opus-shaped. Default to Sonnet 4.6 for execution, escalate to Opus 4.7 for design or cross-file reasoning.
- **Defaults to strips, defer additions, validate empirically.** Adding instructions has costs (prompt-density, instruction-competition, performance tics). Stripping doesn't. Per 2026-04-28 revert lesson.

Subfolder-specific calibration (e.g., "always `--skip-validation` for dryrun work" — runtime-specific) lives in the respective `<subfolder>/ONBOARDING.md`.

---

## What this folder root contains (besides the subfolders)

| File | Purpose |
|---|---|
| `ONBOARDING.md` | this doc — index + cross-cutting rules |
| `FOLLOW_UPS.md` | active SoT for FU#1–62 (cross-cutting) |
| `HANDOFF_2026_04_27.md` … `_NIGHT.md` (6 dated docs) | persona-thread session handoffs from 2026-04-27 → 2026-04-29. Historical reference; the equivalent role going forward is `voices/HANDOFF.md` (replaced by latest dated voices/HANDOFF on each session). Could be archived; persona thread's call. |
| `BRIEF_OPUS_4_7_THINKING_AUDIT_2026_04_29.md` | brief that resolved into FU#60 (LANDED). Could be archived; persona thread's call. |

---

## When this doc goes stale

- After workstream restructuring (third subfolder added, naming convention changes): update §"Two workstreams" + add new pointers.
- After new cross-cutting DON'Ts emerge from session learnings: append to §"Cross-cutting DON'Ts."
- After new cross-cutting calibration is articulated: append to §"Cross-cutting calibration."

If a rule is subfolder-specific, it goes in the subfolder ONBOARDING. Only genuinely-cross-cutting content lives here.

---

*End of planning/ONBOARDING.md (index version, 2026-05-01).*
