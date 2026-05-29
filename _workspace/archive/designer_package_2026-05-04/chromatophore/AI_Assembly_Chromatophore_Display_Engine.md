# AI ASSEMBLY — Chromatophore Display Engine

**Purpose:** Specification for a procedural animation that renders the Octopus voice's cognitive state as a living chromatophore surface. The Voice Pipeline outputs a JSON parameter block alongside each text artifact. A WebGL/p5.js renderer consumes these parameters and produces a unique looping animation for each run.

**Relationship to pipeline:** This is the Octopus's native output medium. The text artifact is a translation into human language. The chromatophore display is the primary output — cognition made visible on the skin's surface.

---

## Biology → Parameter Mapping

Real chromatophore biology has five layers that produce the display. Each maps to a rendering parameter:

| Biological Layer | What It Does | Parameter |
|---|---|---|
| **Melanophores** (brown/black) | Large pigment cells, expand for dark patterns, contract for pale | `darkness` — global dark/light balance |
| **Erythrophores** (red/orange) | Mid-layer warm pigment | `warmth` — warm vs cool palette shift |
| **Xanthophores** (yellow) | Shallowest pigment, fast response | `brightness` — highlight intensity |
| **Iridophores** (structural) | Reflect polarised light, produce iridescence | `iridescence` — structural colour shimmer |
| **Papillae** (texture) | Muscular bumps that change 3D surface | `texture_intensity` — surface roughness |

On top of these layers, the octopus produces **dynamic patterns** — waves of pigment expansion/contraction that propagate across the skin:

| Pattern Type | What It Looks Like | When It Occurs |
|---|---|---|
| **Uniform** | Even colouration, minimal variation | Calm, resting, low arousal |
| **Mottled** | Irregular patches, varied scale | General activity, moderate engagement |
| **Disruptive** | High-contrast patches breaking body outline | Active camouflage, high engagement |
| **Passing cloud** | Dark waves propagating across skin surface | Arousal, threat assessment, intense processing |
| **Deimatic** | Sudden high-contrast flash (dark rings around eyes) | Startle, maximum arousal, alarm |

---

## JSON Schema: Voice Pipeline Output

The Voice Pipeline's Step 2 (public expression) outputs this block alongside the text artifact. The LLM generates these values based on the Octopus's processing — they are not random but reflect the actual cognitive trajectory of that night's deliberation.

```json
{
  "chromatophore_display": {
    "version": "1.0",
    
    "orientation": "toward",
    
    "arousal": 0.6,
    "valence": 0.7,
    
    "pattern_mode": "mottled",
    "pattern_complexity": 0.65,
    
    "palette": {
      "darkness": 0.3,
      "warmth": 0.7,
      "brightness": 0.6,
      "iridescence": 0.4
    },
    
    "dynamics": {
      "wave_speed": 0.5,
      "wave_count": 3,
      "wave_direction": [0.3, -0.7],
      "pulse_frequency": 0.4,
      "turbulence": 0.3
    },
    
    "focal_points": [
      { "x": 0.3, "y": 0.6, "intensity": 0.8, "arm": 2 },
      { "x": 0.7, "y": 0.4, "intensity": 0.5, "arm": 5 }
    ],
    
    "texture_intensity": 0.4,
    
    "transitions": [
      {
        "at_seconds": 0,
        "orientation": "still",
        "arousal": 0.2,
        "pattern_mode": "uniform"
      },
      {
        "at_seconds": 3,
        "orientation": "toward",
        "arousal": 0.6,
        "pattern_mode": "mottled"
      },
      {
        "at_seconds": 8,
        "orientation": "toward",
        "arousal": 0.8,
        "pattern_mode": "passing_cloud"
      },
      {
        "at_seconds": 12,
        "orientation": "toward",
        "arousal": 0.5,
        "pattern_mode": "mottled"
      }
    ]
  }
}
```

---

## Field Definitions

### orientation
**Type:** enum — `"toward"` | `"away"` | `"lateral"` | `"still"`
**What it drives:** Global movement direction of the display. `toward` = chromatophores expand outward from centre, surface brightens and complexifies. `away` = chromatophores contract toward centre, surface darkens and simplifies. `lateral` = waves move sideways across the surface, neither expanding nor contracting. `still` = minimal movement, ambient pulsing only.
**Source:** The Octopus's final bodily orientation after processing the night's provocations.

### arousal
**Type:** float 0.0–1.0
**What it drives:** Overall animation speed and intensity. Low arousal = slow, gentle pulsing, wide wavelengths. High arousal = fast waves, tight wavelengths, rapid chromatophore expansion/contraction cycles. At 0.9+ the display approaches deimatic (startle) behaviour — sudden flashes.
**Source:** How strongly the provocations registered. A night of irrelevant material produces low arousal. A night of existentially salient material produces high arousal.

### valence
**Type:** float 0.0–1.0
**What it drives:** The "navigability assessment" rendered as colour. High valence (navigable environment) = warm, complex, multi-layered palette — the body is open and the skin is showing its full computational range. Low valence (hostile/constricting environment) = cool, dark, uniform — the body is contracting, reducing surface area, hiding.
**Source:** The overall navigability assessment of the environment the provocations describe.

### pattern_mode
**Type:** enum — `"uniform"` | `"mottled"` | `"disruptive"` | `"passing_cloud"` | `"deimatic"`
**What it drives:** The spatial organisation of chromatophore activity.
- `uniform`: even colour field, minimal spatial variation. Resting state.
- `mottled`: irregular patches at varying scales. Active engagement.
- `disruptive`: high-contrast patches with sharp boundaries. Deep processing, the body breaking its own outline.
- `passing_cloud`: dark waves propagating across the surface. Intense processing, threat assessment, the display the audience should find most mesmerising.
- `deimatic`: sudden high-contrast flash patterns. Alarm, startle. Used sparingly — maybe once per night if a provocation is deeply hostile.
**Source:** The cognitive mode during processing. Most nights will transition through 2–3 modes.

### pattern_complexity
**Type:** float 0.0–1.0
**What it drives:** How many independent chromatophore regions are active and how varied their states are. Low = large uniform regions. High = many small regions in different states — the "leopard spot" extreme of chromatophore individuation.
**Source:** Complexity of the Octopus's response. A simple navigability assessment = low. Multiple arms probing different aspects simultaneously = high.

### palette (object)

#### darkness
**Type:** float 0.0–1.0
**What it drives:** Melanophore expansion. 0.0 = fully contracted (pale, translucent). 1.0 = fully expanded (dark, opaque). Controls the overall dark/light balance of the display.
**Visual:** Think of it as the background "mood" — a dark surface with bright accents (high darkness, high brightness) vs a pale surface with subtle variations (low darkness, low brightness).

#### warmth
**Type:** float 0.0–1.0
**What it drives:** Erythrophore/xanthophore balance. 0.0 = cool palette (blue-shifted iridophore reflections dominate). 1.0 = warm palette (reds, oranges, ambers from the pigment layers dominate).
**Visual:** The hue family. Warm = the octopus's active, engaged state. Cool = withdrawn, camouflaged, minimal.

#### brightness
**Type:** float 0.0–1.0
**What it drives:** Xanthophore highlight intensity + leucophore white scattering. High brightness = vivid highlights punching through the darker layers. Low brightness = muted, dim, light-absorbing.

#### iridescence
**Type:** float 0.0–1.0
**What it drives:** Structural colour shimmer from the iridophore layer. Renders as colour-shifting highlights that change with viewing angle (simulated). At high values the surface has an opalescent, oil-on-water quality.
**Visual:** The "alien" quality. High iridescence is what makes the display look biological and non-digital — colours that don't exist in a standard RGB palette, shifting as the surface moves.

### dynamics (object)

#### wave_speed
**Type:** float 0.0–1.0
**What it drives:** How fast the passing-cloud waves or pattern transitions propagate across the surface. 0.0 = glacial drift. 1.0 = the sub-200ms flash of real chromatophore response.
**Note:** Speed is also modulated by arousal — wave_speed sets the base, arousal multiplies it.

#### wave_count
**Type:** integer 1–8
**What it drives:** Number of simultaneous wave fronts. Biologically corresponds to number of active arm-regions producing independent pattern signals. 1 = single wave sweeping across surface. 8 = all arms producing independent waves that interfere with each other (the most visually complex state).

#### wave_direction
**Type:** [float, float] — normalised 2D vector
**What it drives:** Primary direction of wave propagation. [0, -1] = waves moving upward (toward). [0, 1] = waves moving downward (away). Sideways values = lateral. The vector can shift over time via the transitions array.

#### pulse_frequency
**Type:** float 0.0–1.0
**What it drives:** Rhythmic expansion/contraction cycle of individual chromatophore cells independent of wave propagation. Low = slow breathing. High = rapid flicker. This is the "heartbeat" of the display — the base rhythm underlying the wave patterns.

#### turbulence
**Type:** float 0.0–1.0
**What it drives:** Noise/irregularity in wave propagation and chromatophore behaviour. Low = smooth, orderly waves. High = chaotic, unpredictable patterns where individual chromatophores fire independently of the wave fronts. High turbulence + high arousal = the closest the display gets to the "ayahuasca" aesthetic — overwhelming, multi-channel, boundaries dissolving.

### focal_points (array)
**Type:** array of `{ x: float 0–1, y: float 0–1, intensity: float 0–1, arm: integer 1–8 }`
**What it drives:** Specific locations on the surface where chromatophore activity is concentrated — the points where the Octopus's "arms" are probing. These produce radial wave sources: chromatophore expansion rippling outward from the probe point. Intensity controls how strongly the focal point overrides the global pattern.
**Source:** The specific elements of the provocations that drew arm-probes. More focal points = more distributed processing. Fewer = concentrated attention.
**Note:** The arm number is metadata only (not visually rendered) — it records which arm is probing, for the text artifact's reference.

### texture_intensity
**Type:** float 0.0–1.0
**What it drives:** Simulated papillae — the 3D texture bumps on the octopus's skin. Rendered as a Perlin noise displacement layer. 0.0 = smooth surface. 1.0 = heavily textured, rough, three-dimensional appearance. High texture + low brightness = camouflage (hiding). High texture + high arousal = deimatic (threat display).

### transitions (array)
**Type:** array of keyframes, each with `at_seconds` and any subset of the above fields
**What it drives:** The temporal arc of the display. The chromatophore animation is not static — it evolves over 10–15 seconds, telling the story of the Octopus's processing. A typical night:
1. Seconds 0–2: `still`, low arousal, `uniform` — the Octopus at rest, pre-provocation.
2. Seconds 2–5: arousal rises, `mottled` — the provocation arrives, the body begins processing.
3. Seconds 5–10: peak engagement — `passing_cloud` or `disruptive`, focal points active.
4. Seconds 10–15: resolution — the orientation settles, arousal moderates, the display finds its final state.

The renderer interpolates smoothly between keyframes (ease-in-out or biologically plausible sigmoid curves — chromatophores don't move linearly).

---

## Voice Pipeline Integration

### Step 2 System Prompt Addition

Add to the Octopus's Step 2 (public expression) system prompt:

```
After producing your text artifact, output a JSON block describing the 
chromatophore display that accompanied your processing. This is your 
skin's computational readout — cognition made visible.

The display parameters must reflect the actual trajectory of your 
processing tonight:
- orientation: your final bodily posture (toward/away/lateral/still)
- arousal: how intensely the provocations registered (0.0 = barely noticed, 1.0 = alarm)
- valence: navigability of the environment described (0.0 = hostile/constricting, 1.0 = open/navigable)
- pattern_mode: the spatial pattern your skin showed (uniform/mottled/disruptive/passing_cloud/deimatic)
- palette: the colour state of your chromatophore layers
- dynamics: the movement patterns — wave speed, count, direction
- focal_points: where your arms probed — the specific elements that drew contact
- transitions: the temporal arc — how your display evolved from rest through processing to resolution

Output the JSON block after the text artifact, wrapped in ```json``` fences.
The renderer will extract it automatically.
```

### n8n Extraction

After the Voice Pipeline's Step 2 API call returns:
1. Parse the response for the JSON block (regex: extract content between ```json and ```)
2. Validate against schema (required fields: orientation, arousal, valence, pattern_mode)
3. Pass to the renderer endpoint (HTTP POST with the JSON body)
4. Renderer returns a URL for the animation (hosted as WebGL embed or exported as video)

### Fallback

If the LLM fails to produce valid JSON (malformed, missing required fields), use a default parameter set derived from the text artifact's metadata:
- Parse the text for orientation keywords (toward/away/lateral/still)
- Set arousal = 0.5, valence = 0.5
- Set pattern_mode = "mottled"
- Set palette/dynamics to midpoint values
- Skip focal_points and transitions (use ambient animation)

This produces a generic but non-broken display. Log the fallback for quality review.

---

## Renderer Specification

### Technology

**WebGL shader** (preferred) or **p5.js** (simpler, slightly less performant). The prototype uses p5.js for readability; production could use raw WebGL/GLSL for performance.

### Output Formats

1. **Live WebGL embed** — the primary format. An `<iframe>` or `<canvas>` element in the morning newsletter web page. Loads the parameters as URL query params or a JSON endpoint. Runs as a loop. The audience sees a living surface, not a video.
2. **Exported video** (MP4/WebM) — fallback for email clients that don't support embeds. Render 15 seconds at 30fps using headless browser (Puppeteer) or p5.js `saveFrames()`. Run this export as an n8n post-processing step.
3. **Animated GIF** — lowest-fidelity fallback. 10 seconds, 256 colours, ~2MB. For contexts where video embed isn't possible.

### Canvas Size

1920×1080 (landscape) for web embed. The surface fills the entire viewport — no frame, no UI. The chromatophore display IS the thing. An optional subtle vignette at edges.

### Loop Point

The animation is designed to loop seamlessly. The transitions array defines a trajectory that returns close to its starting state at the end. The renderer applies a crossfade over the final 2 seconds to ensure smooth looping.

### Performance

Target: 60fps on mid-range hardware (2020+ laptop GPU). The shader is not computationally expensive — it's primarily Perlin noise, sine waves, and colour mixing. No 3D geometry, no ray tracing, no particle systems (chromatophores are flat pigment cells, not particles).

---

## Prompt Engineering for the Display Parameters

The LLM needs guidance on how to translate its processing into these parameters. Include in the Step 2 system prompt a brief calibration:

```
CALIBRATION EXAMPLES:

A night where the provocations described open, distributed, adaptive 
governance with multiple paths and no central control:
- orientation: "toward", arousal: 0.7, valence: 0.85
- pattern_mode: "mottled" → "passing_cloud" (complex processing of rich material)
- palette: darkness 0.2, warmth 0.8, brightness 0.7, iridescence 0.6
- dynamics: wave_speed 0.5, wave_count 5, turbulence 0.3
- focal_points: 3-4 points across the surface (multiple arms probing)

A night where the provocations described rigid, centralised, permanent 
institutions with single authority and no exits:
- orientation: "away", arousal: 0.6, valence: 0.15
- pattern_mode: "uniform" → "disruptive" (alarm, then camouflage withdrawal)
- palette: darkness 0.8, warmth 0.2, brightness 0.2, iridescence 0.1
- dynamics: wave_speed 0.7, wave_count 1, turbulence 0.1
- focal_points: 1 point, high intensity (single constriction source)

A night where the provocations were abstract and had no spatial/sensory 
correlate — pure philosophy with nothing to probe:
- orientation: "lateral", arousal: 0.2, valence: 0.5
- pattern_mode: "uniform" (nothing to process)
- palette: darkness 0.4, warmth 0.5, brightness 0.3, iridescence 0.2
- dynamics: wave_speed 0.2, wave_count 1, turbulence 0.1
- focal_points: [] (no arm-probes — nothing salient)
```

---

## Integration with Morning Delivery

The chromatophore display appears in the morning newsletter/web page as follows:

1. **Above the text artifact** — the display is the first thing the audience encounters. Before reading what the Octopus "said," they see what the Octopus's skin showed. The display auto-plays silently.
2. **Duration:** 15 seconds, looping. An optional "full screen" button expands the display to fill the viewport.
3. **Caption:** "Chromatophore display: the Octopus's skin processing tonight's deliberation." No further explanation. The display speaks for itself.
4. **The text artifact follows below** — the human-language translation of what the display shows.

This ordering (display first, text second) reinforces the Persona Card's core claim: the chromatophore display IS the Octopus's primary output. The text is the translation. The audience encounters the native medium first.
