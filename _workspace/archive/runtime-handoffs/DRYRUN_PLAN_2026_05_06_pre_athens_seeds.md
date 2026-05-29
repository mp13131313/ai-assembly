# Dryrun plan — pre-Athens content seeds (2026-05-06)

**Status:** STAGED, not fired. Operator confirmation needed before LLM-heavy
pipeline runs (~$80-130 across both).

## What's set up

Two markdown sources from `~/Desktop/`:
- `themes_more_than_human_democracy-2.md` (mthd) — one session script
  (the AI Democracy Marathon opening session, May 7 14:55-16:15)
- `themes_wbbf_athens_2026_programme.md` (wbbf26) — pre-conference
  programme content from the WBBF website (147 sessions across 10 tracks)

Converted via `runtime/scripts/markdown_to_researcher_output.py` into
proper Researcher-output JSON shapes. Outputs staged at:

```
projects/athens-2026/runs/
├── ai_democracy_marathon_opening_2026_05_06/
│   └── 02_researcher/
│       ├── grouping.json          # 5 themes / 17 clusters
│       ├── clusters.json
│       └── all_extractions.json   # 77 extractions
└── preconference_wbbf_programme_2026_05_06/
    └── 02_researcher/
        ├── grouping.json          # 5 themes / 14 clusters
        ├── clusters.json
        └── all_extractions.json   # 66 extractions
```

`runs/` is gitignored in athens-2026 (as of `ec15c82`), so dryrun
state stays local.

## Why athens-2026 as PROJECT_ROOT

These dryruns share the production setup with Night 1/2/3:
- `conference_facts.json` (THE GATHERING block)
- `panel_roster.json` (the 10 voices)
- `voices/<slug>/07_persona_card_assembled.json` (athens-2026 main —
  10 shipped cards including Whanganui v2 with kawa-frame patches `8c3e9a7`)
- `council_config.json` (10 voices wired)
- `reference/speakers.json` (224 active entries; 97% speaker-match rate
  for both seed sources)

Run-dir names `ai_democracy_marathon_opening_2026_05_06` and
`preconference_wbbf_programme_2026_05_06` deliberately don't embed
`_night_N`, so the runtime's `assert_run_dir_night_matches` validator
passes through (Night 1/2/3 production runs use the canonical
`athens_night_N` naming).

## Speaker coverage (panel-speaker attribution chain)

| Source | Unique speakers | In `reference/speakers.json` | Missing |
|---|---|---|---|
| mthd | 15 | 15 (100%) | — |
| wbbf26 | 30 | 29 (97%) | Kristen Bennie (Barclays — could be added to reference) |

Tim's editor will cite by name + role/title for both dryruns.

## Ready-to-fire commands (NOT YET EXECUTED)

### mthd — AI Democracy Marathon opening session

```bash
export AI_ASSEMBLY_PROJECT_ROOT="/Users/aienvironment/Desktop/AI Assembly/projects/athens-2026"
RUN_DIR="$AI_ASSEMBLY_PROJECT_ROOT/runs/ai_democracy_marathon_opening_2026_05_06"
cd "/Users/aienvironment/Desktop/AI Assembly/code/runtime"

# Provocateur (~$15-20, ~5 min)
./venv/bin/python3.12 flows/provocateur_flow.py "$RUN_DIR"

# Voice (~$20-30, ~10-15 min for 10 voices)
./venv/bin/python3.12 flows/voice_flow.py "$RUN_DIR" --night 1 --skip-step3 --skip-validation --skip-continuity

# Editor (~$1-2, ~5 min — auto-fires after Release on dashboard, OR run manually with --bypass-gating)
./venv/bin/python3.12 flows/editor_flow.py "$RUN_DIR" --night 1 --bypass-gating
```

### wbbf26 — Pre-conference programme

Same shape, swap `RUN_DIR` to `$AI_ASSEMBLY_PROJECT_ROOT/runs/preconference_wbbf_programme_2026_05_06`.

## Cost envelope (per dryrun, full 10 voices)

- Provocateur: ~$15-20
- Voice Step 1+2: ~$20-30
- Editor (4-5 dossiers): ~$1-2
- **Total per dryrun: ~$40-65**
- **Both dryruns: ~$80-130**

Wall: ~25-40 min per dryrun (could run sequentially or in parallel via different terminals; each fires its own Anthropic client).

## Two distinct dryrun characters

| Source | Voices reasoning ABOUT |
|---|---|
| mthd | One session's actual script-level material (real speaker quotes, raw wishes, host pitches). Closer to a real Researcher output shape. The intended primary test for Athens-equivalent pipeline behavior on real per-session content. |
| wbbf26 | Conference programme blurbs — voices respond to *promises the conference is about to make*, not to anything actually said. Useful as pre-Athens warm-up content the operator could publish before Day 1. Different beast — voices commenting on the conference's framing of itself rather than panel content. |

## Caveats

1. Voice Step 2 validation is SKIPPED by default in voice_flow CLI args
   above (`--skip-validation`). To exercise the editor gating + auto-fire
   chain end-to-end, drop `--skip-validation` and use the dashboard
   Release/Hold buttons instead of `--bypass-gating`.
2. Continuity flow SKIPPED (`--skip-continuity`) — no Night 2/3 for these
   dryruns. Real Athens runs use continuity.
3. Editor's `panel_speakers[]` block fires automatically. Tim should cite
   by name + role given the 97% reference coverage.
4. Whanganui will use the post-`8c3e9a7` card (kawa-frame discipline
   shipped). Should NOT see the v1-style "I am the river" opening.
5. Synthesis routing fires automatically for any voice whose
   focus_decision is "synthesise across X" — Sonnet router picks the
   primary theme. Cost included in voice Step 2 envelope.
6. **Athens-2026 production main** at `8c3e9a7`. These dryruns share the
   production card set; running them does NOT modify athens-2026 git state
   (runs/ is gitignored).

## Decision points

Before firing, confirm:
- **All 10 voices** vs filter to a subset? (Production = 10. Subset
  cheaper but less representative of real Athens.)
- **Both dryruns** or just mthd first? (mthd is the primary test;
  wbbf26 is bonus.)
- **Sequential** vs **parallel**? (Sequential safer, easier to inspect.
  Parallel ~halves wall time.)
