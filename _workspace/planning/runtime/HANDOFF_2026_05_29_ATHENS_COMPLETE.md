# Handoff — Athens COMPLETE (all three nights published) · 2026-05-29

**Branch:** code `main` @ `fb47e45` (this doc-cleanup commit will advance it).
athens-2026 `main` @ `3dc4e16`. Both pushed.
**Predecessor handoffs:** Night 1 detail archived at
`_workspace/archive/runtime-handoffs/HANDOFF_2026_05_08_ATHENS_DAY_1.md`.

## State

**Athens Nights 1–3 ran end-to-end and are PUBLISHED.** 13 dossiers + 30
per-voice pages across the three nights, committed + pushed to athens-2026.
Per-night production detail (counts, leads, deployment_context rules) lives
in `CLAUDE.md`'s state block — that is the authoritative current-state record.

| Night | Lead dossier | Dossiers | Voices |
|---|---|---|---|
| 1 | dossier_001 *WHO TEACHES THE TEACHERS* | 5 | 10 |
| 2 | dossier_001 *WHOSE MOUTH IS MOVING* | 5 | 10 |
| 3 (closing) | dossier_002 *THE BODY OFF THE LEDGER* | 3 | 10 |

## Open items filed this run (v4.1 — none Athens-blocking; workarounds held)

In `runtime/OPEN_ITEMS.md`:
- **C42 + C43** validator misfires RECURRED (C42 → Whanganui N3 operator-release;
  C43 parse-fallback on Marley N2 + Whanganui N3).
- **C49** (new) many-speaker speaker_id JSON-decode → manual passthrough
  (N1 ×2 + N2 ×1 + N3 ×2).
- **C50** (new) `nights/_index.json` clobbered by single-voice publish — the
  Night-3 six-missing-pages root cause (republished 2026-05-29).
- **C51** (new) per-theme `themes/night_N/` artifacts never generated for any night.

Still-external (unchanged; Athens ran without them): B2 microsite, B5 closing-show,
B6 Day 4 goodbye, B7 render layer (Octopus shipped; Marley → Suno pending),
B10 VM provisioning.

## Operator workflow that worked (record for next event)

- **Manual per-stage fires, NOT the orchestrator.** Running both makes the
  orchestrator dispatch duplicate transcriptions on top of in-flight manual fires.
- Split-audio sessions → duplicate the session in `reference/sessions.json` with an
  `__audio2` suffix so the second capture transcribes as its own session.
- Many-speaker speaker_id halt → hand-write the all-`Unidentified` `out_02` map +
  re-fire (cleaning-only resume). See C49.
- After any per-voice publish rerun, finish with a full `voice_slugs=None` publish so
  `nights/_index.json` + the page set are complete. See C50.

## Doc cleanup done this session (2026-05-29)

- `CLAUDE.md` refreshed to Nights 1–3 + trimmed (625 → ~535 lines; pre-Athens
  session-log narrative removed, preserved in archived handoffs + git history).
- `runtime/OPEN_ITEMS.md` TL;DR refreshed to post-Athens; C49–C51 filed.
- `runtime/ONBOARDING.md` branch state + top-level `README.md` + `_workspace/README.md`
  refreshed.
- Superseded handoffs (05-06, 05-08) + DRYRUN_PLAN_05-06 archived to
  `archive/runtime-handoffs/`; consumed designer package archived.

## Resume prompt for next Claude

> Read `CLAUDE.md` (state block at top), then `runtime/OPEN_ITEMS.md` (TL;DR +
> C49–C51). Athens is done + published; no runtime work is pending. The v4.1
> items are post-event hardening (validator-prompt alignment C42/C43, speaker_id
> robustness C49, publish idempotency C50, themes-publish decision C51). The
> vatican-2026 annotated-encyclical run is specified (untracked) at
> `runtime/SPEC_2026_05_27_magnifica_humanitas_annotated_pipeline.md` — a separate
> future build, not started.
