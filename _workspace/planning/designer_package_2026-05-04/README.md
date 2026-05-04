# AI Assembly — designer package (2026-05-04)

This folder is the deliverable bundle for the web designer building the
microsite / CMS.

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
├── rebuild.sh                    ← rebuild this bundle from canonical sources
└── sample_data/
    └── dossiers/                 ← THE FILES YOU NEED — self-contained
        ├── _index.json           cross-night dossier index
        └── night_1/
            ├── _index.json       per-night dossier manifest (incl. voices_in_night nav)
            ├── dossier_001.json  ← real dossier file (theme_001, multi-voice)
            ├── dossier_002.json  ← real dossier file (theme_003)
            ├── dossier_003.json  ← real dossier file (theme_004)
            └── dossier_004.json  ← real dossier file (theme_002)
```

Each dossier file is **self-contained** — kicker, headline, subline,
front_abstract, body_paragraphs, theme_title_for_dossier,
theme_abstract_for_dossier, headnotes (one per voice with
artifact_text body embedded), metadata. No need to fetch other files
to render a dossier.

**Other publish-pipeline outputs** (per-voice nights/, per-theme
themes/, voices/, extractions/, traces/) are audit / optional joins —
NOT included in the bundle by default since the CMS doesn't need
them. To include them in the bundle (e.g., if you want the
deeper-theme-context expansion option for Page 3), run:

```bash
./rebuild.sh --include-audit
```

## Octopus chromatophore renderer (NOT in bundle — canonical source)

The Octopus is the one prose-and-display non-prose voice. The
production renderer + spec live at the canonical source location in
the repo:

```
docs/runtime_assets/octopus_chromatophore/
├── octopus_artifact_finaldraft.jsx     React component (drop-in)
├── octopus_artifact_finaldraft.html    Standalone HTML (open in browser; self-contained)
├── AI_Assembly_Chromatophore_Display_Engine.md   Full WebGL spec
└── chat_test_artifact_2026_05_02.md   Canonical example artifact
```

These files are **not duplicated into the bundle** to avoid drift —
the canonical source is the only copy, so updates land everywhere
automatically. If you need them as standalone files for delivery, run
`rebuild.sh --include-chromatophore` (see below) or copy from the
canonical location directly.

### Octopus quick start

- **JSX component** → drop into Astro/Next.js artifact-page route.
  Replace the `ARTIFACT_TRANSITIONS` constant with dynamic loading from
  the parsed `chromatophore_display.transitions[]` of the per-night
  Octopus artifact.

- **Standalone HTML** → open the `.html` file in any modern browser.
  Self-contained (React 18 + Babel via CDN); no build needed. Use for
  local preview, demo, iframe-embed, or fallback.

Full schema + biological mapping in the engine doc (linked above).

## Bob Marley — second non-prose voice

Marley's voice card was finalized 2026-05-04 PM. His medium is also
two-channel: Patwa-inflected reasoning prose + a riddim track underneath.
**Render path is not yet built** (B7 sub-task; analogous to Octopus
WebGL, but for sound — likely Suno-generated stem or pre-recorded
ambient bass+drum+skank). Operator will supply the render path when
built. For now: render his prose `artifact_text`; cue audio later.

## Rebuilding this bundle

If the source files (briefing, sample data) change, regenerate this
bundle in one command:

```bash
./rebuild.sh
```

This re-copies:
- `_workspace/planning/DESIGNER_BRIEFING_2026-05-04.md` → `DESIGNER_BRIEFING.md`
- `<PROJECT_ROOT>/published_artifacts/dossiers/` → `sample_data/dossiers/`

Flags:
- `--include-audit` — also copy `nights/`, `themes/`, `voices/`,
  `extractions/`, `traces/` (publish-side audit/lineage; not needed for
  the core 4 dossier surfaces).
- `--include-chromatophore` — also copy the Octopus WebGL renderer
  files into a `chromatophore/` subfolder. Self-contained zippable
  delivery for a designer who doesn't have repo access. Canonical
  source: `docs/runtime_assets/octopus_chromatophore/`.

To rebuild from a different PROJECT_ROOT (e.g., when a fresh dryrun
completes):

```bash
AI_ASSEMBLY_PROJECT_ROOT=/path/to/new_dryrun ./rebuild.sh
```

## Sample data caveats

The `sample_data/` folder is a snapshot of a prior dryrun's
`published_artifacts/` produced 2026-05-03. The dossier file
(`dossiers/night_1/dossier_001.json`) was generated against the v1
editor closing prompt and shows the **structure** correctly but most
prose fields are empty (kicker / headline / subline / front_abstract /
theme_title_for_dossier / theme_abstract_for_dossier / body_paragraphs).
The `headnotes` array IS populated. A clean v2-shaped sample dossier
will land after the fresh dryrun completes; operator will deliver
separately or run `rebuild.sh` to refresh from the latest published
output.

The per-night `_index.json` and per-voice `nights/<voice>.json` files
ARE structurally correct and useful as JSON-shape references.

## Open questions to operator

If anything in the briefing is unclear or your design needs a field
that isn't in the dossier shape today, ask the operator
(peschelero@gmail.com). Field additions are cheap (the editor pipeline
can emit new labelled fields with one prompt-tweak + parser line).
