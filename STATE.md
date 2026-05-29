# Project state — quick entry point

One-glance status + where the authoritative detail lives. Snapshot **2026-05-29**.

## Status: Athens 2026 COMPLETE

All three Athens nights ran end-to-end and are **published** — 13 dossiers + 30
per-voice pages across Nights 1–3. Both repos clean + pushed; runtime tests green
(358 pass, 1 env-only artifact). No work is in flight.

## Where the detail lives

| For… | Read |
|---|---|
| Current state · per-night production detail · deployment-context rules | [`CLAUDE.md`](CLAUDE.md) (state block at top) |
| Open items to improve (v4.1) | [`_workspace/planning/runtime/OPEN_ITEMS.md`](_workspace/planning/runtime/OPEN_ITEMS.md) — TL;DR + C42–C51, B-items, E-items |
| Athens-complete handoff | [`_workspace/planning/runtime/HANDOFF_2026_05_29_ATHENS_COMPLETE.md`](_workspace/planning/runtime/HANDOFF_2026_05_29_ATHENS_COMPLETE.md) |
| Editorial quality assessment of the dossiers | `athens-2026/published_artifacts/EDITORIAL_ASSESSMENT.md` (other repo) |
| How the runtime works end-to-end | [`docs/AI_Assembly_Runtime_Lifecycle.md`](docs/AI_Assembly_Runtime_Lifecycle.md) |
| Fresh-session onboarding | [`_workspace/planning/ONBOARDING.md`](_workspace/planning/ONBOARDING.md) → `runtime/` or `voices/` |

## The two repos

- **`mp13131313/ai-assembly`** (this repo) — runtime + personas + docs + planning trackers.
- **`mp13131313/ai-assembly-athens2026-voices`** (private) — the Athens production
  instance: 10 voice cards + config, `published_artifacts/` (the 3 editions +
  editorial assessment), and `runs/` (the full JSON "making-of" record:
  transcripts → voice reasoning → validation → dossiers; **audio excluded for size**).

## Known-open at a glance

- **Improve (v4.1, none blocking):** validator-prompt alignment (C42/C43), speaker_id
  JSON robustness (C49), publish idempotency (C50), per-theme publish decision (C51),
  editor dossier caching (C45), discipline rules → permanent prompts (C47).
- **External, not built:** microsite (B2), closing-show pipelines (B5), Day-4 goodbye
  (B6), full non-text render layer (B7), VM provisioning (B10).
- **Voice-build (voices thread):** Plato anachronism patch (§16.1), per-voice
  coherence audit (§31 Gap-J), post-Athens Rastafari-orbit + iwi-orbit reader gates (§11).
- **Future build (specified, untracked):** vatican-2026 annotated-encyclical run
  (`_workspace/planning/runtime/SPEC_2026_05_27_magnifica_humanitas_annotated_pipeline.md`).
