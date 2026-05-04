# AI Assembly — designer package (2026-05-04)

This folder is the deliverable bundle for the web designer building the
microsite / CMS. Self-contained — no need to clone the runtime repo.

## Start here

1. **`DESIGNER_BRIEFING.md`** — the canonical briefing. Open this first.
   Describes the dossier as the unit of publication, the per-page
   render contract, JSON shapes, per-voice typography needs, and what's
   TBD.

## Contents

```
designer_package_2026-05-04/
├── README.md                     ← (you are here)
├── DESIGNER_BRIEFING.md          ← MAIN DOC — read this first
├── chromatophore/                ← Octopus voice render assets
│   ├── octopus_artifact_finaldraft.jsx     React component (drop-in)
│   ├── octopus_artifact_finaldraft.html    Standalone HTML (open in browser)
│   ├── AI_Assembly_Chromatophore_Display_Engine.md   Full WebGL spec
│   └── chat_test_artifact_2026_05_02.md   Canonical example artifact
└── sample_data/                  ← Real dryrun publish-output for shape reference
    ├── dossiers/                 Per-night + per-dossier files
    │   ├── _index.json           Cross-night dossier index
    │   └── night_1/
    │       ├── _index.json       Per-night dossier manifest (incl. voices_in_night nav)
    │       └── dossier_001.json  ← Real dossier file (caveat: prior run; v1-shaped, fields mostly empty)
    ├── nights/                   Per-voice published artifacts (audit; not for CMS render)
    ├── themes/                   Researcher's per-theme deeper context (optional joins)
    ├── voices/                   Per-voice cross-night index
    ├── extractions/              Reverse-index lookups (audit)
    └── traces/                   Lineage graphs (audit)
```

## Octopus chromatophore — quick start

The Octopus is the one non-prose voice. Two parallel paths:

- **JSX component** → drop into Astro/Next.js artifact-page route.
  Replace the `ARTIFACT_TRANSITIONS` constant with dynamic loading from
  the parsed `chromatophore_display.transitions[]` of the per-night
  Octopus artifact. See `chromatophore/octopus_artifact_finaldraft.jsx`.

- **Standalone HTML** → open `chromatophore/octopus_artifact_finaldraft.html`
  in any modern browser. Self-contained (React 18 + Babel via CDN); no
  build needed. Use for local preview, demo, iframe-embed, or fallback.

Full schema + biological mapping: `chromatophore/AI_Assembly_Chromatophore_Display_Engine.md`.

## Bob Marley — second non-prose voice

Marley's voice card was finalized 2026-05-04 PM. His medium is also
two-channel: Patwa-inflected reasoning prose + a riddim track underneath.
**Render path is not yet built** (B7 sub-task; analogous to Octopus
WebGL, but for sound — likely Suno-generated stem or pre-recorded
ambient bass+drum+skank). Operator will supply the render path when
built. For now: render his prose `artifact_text`; cue audio later.

## Sample data caveats

The `sample_data/` folder is a snapshot of a prior dryrun's
`published_artifacts/` produced 2026-05-03. The dossier file
(`dossiers/night_1/dossier_001.json`) was generated against the v1
editor closing prompt and shows the **structure** correctly but most
prose fields are empty (kicker / headline / subline / front_abstract /
theme_title_for_dossier / theme_abstract_for_dossier / body_paragraphs).
The `headnotes` array IS populated. A clean v2-shaped sample dossier
will land after the fresh dryrun completes; operator will deliver
separately.

The per-night `_index.json` and per-voice `nights/<voice>.json` files
ARE structurally correct and useful as JSON-shape references.

## Open questions to operator

If anything in the briefing is unclear or your design needs a field
that isn't in the dossier shape today, ask the operator
(peschelero@gmail.com). Field additions are cheap (the editor pipeline
can emit new labelled fields with one prompt-tweak + parser line).
