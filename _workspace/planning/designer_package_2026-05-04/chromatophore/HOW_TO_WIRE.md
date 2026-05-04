# Octopus chromatophore — how to wire the renderer

The Octopus voice's artifact is two-channel:
1. A `chromatophore_display` JSON parameter block (its skin's
   computational readout) — RENDERED AS A WEBGL ANIMATION
2. Tank-side prose (the human-language translation) — rendered as
   prose below the animation

Both channels live INSIDE the dossier headnote's `artifact_text` field,
with the JSON in a `​```json` fence at the top and the prose underneath.

This doc shows how to extract the JSON, plug it into the renderer, and
ship a working Octopus artifact page.

---

## Files in this folder

| File | Purpose |
|---|---|
| **`octopus_artifact_finaldraft.jsx`** | Production-ready React component (~1032 lines). 5-pigment-layer chromatophore engine + Voronoi cells + animated centres + fbm noise + pattern-mode blending. Drop into Astro/Next.js artifact-page route. |
| **`octopus_artifact_finaldraft.html`** | Standalone HTML packaging the same component (React 18 + Babel via CDN). Open directly in any modern browser; no build needed. Use for local preview, demo, iframe-embed, or fallback. |
| **`AI_Assembly_Chromatophore_Display_Engine.md`** | Full spec — JSON schema, biological mapping (melanophores / erythrophores / xanthophores / iridophores / papillae), pattern modes, transitions arc. |
| **`chat_test_artifact_2026_05_02.md`** | Original canonical example artifact (chat-test version). |
| **`v2_octopus_chromatophore_sample.json`** | ⭐ The v2 dryrun's actual Octopus chromatophore JSON, extracted from `dossier_003.json`'s headnote. Drop this into the renderer to see fresh output. |

---

## Wiring path 1 — drop into Astro / Next.js

```jsx
import OctopusArtifact from './octopus_artifact_finaldraft.jsx';

// In your artifact-page route handler:
const dossier = await fetch(`/dossiers/night-${night}/dossier_${dossierNo}.json`).then(r => r.json());
const headnote = dossier.headnotes.find(h => h.voice_slug === 'octopus');

// Parse the JSON fence from artifact_text:
const fenceMatch = headnote.artifact_text.match(/```json\s*\n([\s\S]*?)\n```/);
const block = JSON.parse(fenceMatch[1]);
const transitions = block.chromatophore_display.transitions;

// The prose is everything after the fence:
const prose = headnote.artifact_text.replace(/```json[\s\S]*?```\s*/, '').trim();

return <OctopusArtifact transitions={transitions} prose={prose} />;
```

In the JSX file, replace the hardcoded `ARTIFACT_TRANSITIONS` constant
near the top with a prop:

```jsx
// Before:
const ARTIFACT_TRANSITIONS = [...hardcoded canonical example...];

// After:
function OctopusArtifact({ transitions, prose }) {
  // ...rest of the component reads `transitions` instead of ARTIFACT_TRANSITIONS
}
```

---

## Wiring path 2 — standalone HTML (one file, no build)

`octopus_artifact_finaldraft.html` already has a hardcoded
`ARTIFACT_TRANSITIONS` baked in (the original canonical example).
Two ways to swap in fresh data:

### Quick swap (manual edit)
1. Open the HTML file in a text editor
2. Find `const ARTIFACT_TRANSITIONS = [...]`
3. Replace the array literal with the contents of
   `v2_octopus_chromatophore_sample.json`'s `transitions` field
4. Save, reload the file in your browser

### Iframe-embed with runtime injection
Host the HTML on a static path and pass the parameters via URL hash
or query string. Add at the top of the HTML:

```js
const url = new URL(location.href);
const remoteParams = url.searchParams.get('source');
if (remoteParams) {
  const data = await fetch(remoteParams).then(r => r.json());
  ARTIFACT_TRANSITIONS = data.transitions;  // override the default
}
```

Then point an iframe at:
```
/octopus_artifact_finaldraft.html?source=/dossiers/night-1/octopus.json
```

---

## What to extract from artifact_text

The headnote's `artifact_text` looks like this:

```
​```json
{
  "chromatophore_display": {
    "orientation": "...",
    "arousal": 0.55,
    "valence": "...",
    "pattern_mode": "mottled",
    "palette": { ... },
    "dynamics": { ... },
    "focal_points": [ ... ],
    "texture_intensity": 0.36,
    "transitions": [
      { "t": 0.0, "pattern_mode": "uniform", ... },
      { "t": 3.5, "pattern_mode": "mottled", ... },
      ...
    ]
  }
}
​```

Tank-side note. What I render here as a single voice is a
reaching-toward — eight arms each with a local processor...
```

Parsing logic:
1. Find the first ` ```json ` fence; everything between the opening and
   closing ` ``` ` is the JSON block
2. Parse it
3. Read `chromatophore_display.transitions[]` for the animation arc
4. Read `chromatophore_display.{orientation, arousal, valence, ...}`
   for the starting state
5. Everything after the closing fence is the tank-side prose to render
   as text below the canvas

The `transitions[]` array is the authoritative trajectory; top-level
fields are the starting state. Be permissive on top-level enum strings
(e.g. `"passing_cloud_over_mottle"` is a compound mode the renderer
should crossfade rather than reject).

---

## Verifying it works

After wiring, open the artifact page. You should see:

1. A 10-15-second looping WebGL animation (5:4 aspect ratio canvas) at
   the top — the chromatophore display
2. The tank-side prose below it (Octopus's verbatim text)
3. A timeline scrubber underneath the canvas (development-only — can
   be hidden for production)

If the canvas is blank, check:
- Browser console for parse errors (the JSON fence may have escaped
  characters that need stripping)
- WebGL context creation (some sandbox iframes block WebGL)
- Whether `transitions` is an array of objects with at least
  `pattern_mode` and `t` (or `at_seconds`) per keyframe

---

## Open questions to operator

- Should the timeline scrubber be hidden in production? (Currently
  visible for debugging.)
- Should we serve the chromatophore parameters as a separate file
  (e.g. `/dossiers/night-1/octopus.chromatophore.json`) instead of
  parsing the fence from artifact_text? (Cleaner contract; one extra
  publish-step output.)
- For the Bob Marley voice (also two-channel — prose + riddim audio),
  the audio renderer is not yet built (B7). Operator will supply when
  the riddim path is decided.
