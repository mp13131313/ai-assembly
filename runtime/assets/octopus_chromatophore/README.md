# Octopus Chromatophore Display — Runtime Assets

Reference materials for the Octopus voice's chromatophore display engine. The Octopus voice's persona card declares a two-channel emission contract (JSON parameter block + tank-side prose); the runtime layer consumes both.

This folder is the canonical source of truth for the **rendering substrate**, the **canonical chat-test artifact**, the **reviewer-validated quality criteria**, and the **design decisions log** for the Octopus's runtime render path.

## Files

| File | Contents | Purpose |
|---|---|---|
| `AI_Assembly_Chromatophore_Display_Engine.md` | Full engine spec — JSON schema, biological mapping, WebGL renderer, n8n extraction, fallback rules, integration with morning delivery | Specifying contract for runtime team |
| **`octopus_artifact_finaldraft.jsx`** | **Production-ready artifact-page React component** (~1032 lines, 744px max-width column). 5-pigment-layer chromatophore engine (melanophores/erythrophores+xanthophores/iridophores/papillae) with Voronoi cell structure + animated centers + fbm noise + **pattern-mode blending** (no hard switches — both modes computed per-pixel during transitions, mixed by eased blend factor) + **orientation blending** + **focal-point fading** + 5:4 aspect ratio + mobile responsive (720px and 400px breakpoints) + masthead/article-header/canvas-with-timeline/editor-headnote/prose/parameter-log/footer composition. Reviewer-validated biological literacy. | **Use this for production** — drop-in for Astro/Next.js artifact-page route |
| **`octopus_artifact_finaldraft.html`** | **Standalone runnable HTML** (~1097 lines). Same component as the JSX, packaged as a self-contained HTML file with React 18 + Babel standalone for in-browser JSX transform. Open in any modern browser to see the artifact play; no build tooling needed. Includes Cormorant Garamond + JetBrains Mono Google Fonts loaded over CDN. OG/Twitter meta tags for sharing. | Local preview / demo / Substack-embeddable / fallback render path |
| `chat_test_artifact_2026_05_02.md` | The rebuilt Octopus voice's first verified two-channel emission. JSON parameter block + verbatim prose. Schema notes + slip annotations for runtime extractor. | **Canonical example** for Voice Pipeline Step 2 JSON extraction (B7 sub-task #1) and renderer trajectory loading (B7 sub-task #2) |
| `reviewer_notes_2026_05_02.md` | External reviewer's analysis of the chat-test artifact. Validates the rebuild's compass posture; flags two minor JSON notational slips (absorbed by render layer); analyzes pastiche vs generative layers; closing diagnostic *"the architecture's answer is not no, it is not yes, it is the trajectory"* | Quality-assessment baseline + frame-quote source for canonical-docs sweep |
| `render_decisions_2026_05_02.md` | Design decisions log: page structure, aspect ratio (16:10 → 1:1 → 5:4), pattern-mode blending fix, "architecture" word handling, mobile breakpoints, parameter log treatment, column width 920px → 744px (more text-readable proportion) | Reference for future renderer work + runtime team handoff |

## Current state of B7 Octopus runtime work

Per `_workspace/planning/runtime/OPEN_ITEMS.md` B7:

| Sub-task | State | Notes |
|---|---|---|
| **#1 Voice Pipeline Step 2 JSON extraction** | ❌ pending | Runtime must parse ```` ```json ```` fence from Step 2 LLM output, validate against schema (required: orientation, arousal, valence, pattern_mode), persist as separate artifact alongside prose. Permissive extraction needed for descriptive enum-strings at top level (truth lives in `transitions[]` array). See chat_test artifact for canonical example + slip annotations. |
| **#2 WebGL renderer** | ✅ substantially built | `octopus_artifact_finaldraft.jsx` is the production substrate. Reviewer-validated biological literacy (matches Hanlon & Messenger taxonomy + actual chromatophore biophysics; passing-cloud as wave-propagation is mathematically correct). Includes: 5-pigment-layer shader, Voronoi cell structure, pattern-mode blending (no hard switches), focal-point fading, 5:4 aspect ratio, mobile responsive, 744px text-readable column width. **`octopus_artifact_finaldraft.html`** also available as standalone runnable for local preview / Substack embed / fallback. Output formats still pending: MP4-WebM video + animated GIF (fallback chain, separate from the HTML). |
| **#3 Microsite consumption** | 🟡 single-artifact template ready | The JSX is drop-in-ready for an Astro/Next.js route at e.g. `/dossier-1/octopus`. The standalone HTML is drop-in-ready for any iframe-embed or static-host. Routing/integration into broader microsite still operator's separate workstream. |
| **#4 Substack/print fallback** | 🟡 partial | Standalone HTML is Substack-embeddable as iframe. Print-only fallback (single static frame export) still pending. |

## How to use

**For the runtime team building Step 2 JSON extraction (B7 #1):**
1. Read `AI_Assembly_Chromatophore_Display_Engine.md` for the schema.
2. Read `chat_test_artifact_2026_05_02.md` for a canonical example with slip annotations.
3. Implement permissive parser: accept descriptive enum strings at top level, source truth from `transitions[]` array.
4. Validate required fields (orientation, arousal, valence, pattern_mode at minimum).
5. Persist as separate artifact alongside prose; pass the JSON to the renderer.

**For the microsite integration (B7 #3):**
1. Drop `octopus_artifact_finaldraft.jsx` into the artifact-page route.
2. Replace `ARTIFACT_TRANSITIONS` constant with dynamic loading of the runtime-extracted JSON's `transitions[]` array per artifact.
3. Replace prose body with dynamic loading of the runtime-extracted prose per artifact.
4. Test mobile rendering at 375px and 320px viewports.

**For local preview / Substack embed:**
1. Open `octopus_artifact_finaldraft.html` directly in any modern browser — fully self-contained, no build needed.
2. For Substack embed, host the HTML as a static file and use Substack's iframe embed feature.

**For the Substack/print fallback (B7 #4):**
1. Use the same shader/parameter pipeline.
2. Render single static frame at peak-engagement state (`t=6.0s` mottled) OR at disengaged-not-quite-rest state (`t=10.5s` uniform_pale-residual) — the latter is more diagnostic of the trajectory's claim.
3. Export as PNG/JPG for print; optional caption noting the display existed in the digital edition.

## Cross-references

- Persona card: `projects/athens-2026/voices/octopus/07_persona_card_assembled.json` (athens-2026 commit `1d8605f`)
- Voices/OPEN_ITEMS §15: Octopus compass rebuild (complete)
- Runtime/OPEN_ITEMS B7: Render layer for non-text artifacts (this folder is its substrate)
- Cross-thread record: persona-thread side complete; runtime owns consumption.
