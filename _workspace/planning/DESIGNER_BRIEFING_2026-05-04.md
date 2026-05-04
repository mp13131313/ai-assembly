# AI Assembly — designer briefing

**Date:** 2026-05-04
**For:** the web designer building the microsite / CMS
**Status:** describes the publish-side surface as it stands today; one
forthcoming LLM step (per-night "edition" lead) is provisioned as a
placeholder and noted below.

---

## What you're rendering

The AI Assembly produces a **publication** — three nights at the World
Beautiful Business Forum (Athens, 7-9 May 2026). Each night, a council of
~10 personae read the day's panel transcripts, write artifacts in their
own forms, and an editor (Claudia Pinchbeck) composes them into themed
**dossiers**.

**Unit of publication is the dossier.** Each dossier is a single themed
publication with a fixed five-page swipeable structure:

```
Page 1 — THE FRONT          masthead + lead headline + teaser
Page 2 — THE ARTICLE        Claudia's editorial article
Page 3 — THE THEME          theme statement + abstract
Pages 4-N — THE ARTIFACTS   one per engaged voice (their own form)
```

A night produces 1-5 dossiers. The conference produces ~10-15 dossiers
total. Each dossier renders as one swipeable surface; the front-page
"index" of the night composes dossiers into a grid (lead + secondary
positions).

---

## Where the files live

All publish-ready files land under `<PROJECT_ROOT>/published_artifacts/`:

```
published_artifacts/
├── dossiers/                          ← primary microsite-render surface
│   ├── _index.json                    cross-night index of every dossier
│   ├── night_1/
│   │   ├── _index.json                per-night index (the night's "edition")
│   │   ├── dossier_001.json           one dossier
│   │   ├── dossier_002.json           ...
│   │   └── dossier_003.json
│   ├── night_2/
│   └── night_3/
│
├── nights/                            ← per-voice published artifacts
│   ├── night_1/
│   │   ├── _index.json                per-night voice index
│   │   ├── plato.json                 Plato's full Step 2 artifact
│   │   ├── cleopatra.json
│   │   └── ...
│   └── night_2/, night_3/
│
├── themes/                            ← deeper theme context (optional)
│   ├── night_1/
│   │   ├── theme_001.json             theme + clusters + extractions
│   │   └── ...
│
├── voices/                            ← per-voice cross-night timeline
│   ├── plato.json                     all of Plato's nights, summarised
│   └── ...
│
├── extractions/                       ← reverse-index lookups (optional)
└── traces/                            ← lineage graph (optional)
```

The microsite needs **only `dossiers/` + `nights/`** for the core
publication surface. Everything else is for deeper navigation
(theme-page context, per-voice timeline, audit/lineage) — render those
if they fit your design; safe to ignore otherwise.

---

## Page-by-page render guide

### Page 1 — THE FRONT (per-night index)

The website owns the masthead (paper title, date strip, issue chrome).
The CMS does not feed the masthead — render it site-side.

What the CMS feeds Page 1: **the list of tonight's dossiers** + a hint
about which one is the lead.

**Read:** `dossiers/night_<N>/_index.json` → `dossiers[]` list

**Render per dossier card** (lead position + secondary grid):
- `kicker` (ALL-CAPS, 3-7 words)
- `headline` (8-15 words)
- `front_abstract` (30-50-word teaser)

`edition_lead.lead_dossier_no` (when populated; currently `null`) tells
you which dossier sits in the lead position vs. the secondary grid.
Without it, fall back to picking algorithmically or via operator
override.

### Page 2 — THE ARTICLE (per-dossier)

**Read:** `dossiers/night_<N>/dossier_<NNN>.json`

**Render fields:**
- `kicker` — 3-7 words, ALL-CAPS (also appears on Page 1)
- `headline` — 8-15 words (also appears on Page 1)
- `subline` — 25-60 words; italic deck; semicolon-chained 1910s
  broadsheet register
- `body_paragraphs[]` — array of strings. Render with paragraph breaks
  between elements. Asterism breaks (`* * *`) appear as their own
  array element — render as a centred section separator.
- 350-500 words single-voice / 500-700 multi-voice (constraint Claudia
  honours)

Byline conventions:
- "By Claudia Pinchbeck" appears below headline + subline
- Closing: *— C.P.* below the last paragraph

### Page 3 — THE THEME (per-dossier)

**Read:** same `dossier_<NNN>.json`

**Render fields:**
- `theme_title` — 5-10 words; paper-voice short title
- `theme_abstract` — 60-100 words; paper-voice publishing-register
  abstract; orients a reader who arrives directly on Page 3

If you want extra context (the underlying clusters, raw extractions,
formulations per voice), join via `metadata.theme_id` to
`themes/night_<N>/<theme_id>.json` — see file reference below.

### Pages 4-N — THE ARTIFACTS (one per engaged voice)

**Read:** `dossier_<NNN>.json`'s `headnotes[]` for editorial chrome,
and `nights/night_<N>/<voice_slug>.json` for each voice's actual artifact.

**Render per artifact page:**
- Page heading: "PAGE [N] — [VOICE NAME]" (use `headnotes[i].voice_name`)
- Artifact title: `headnotes[i].artifact_title` (4-12 words, paper-voice)
- Editorial headnote: `headnotes[i].framing_text` (1-2 sentences, paper-voice)
- Form-marker (a glyph centred above the artifact): per-voice CSS bundle
  keyed by voice's `medium` (see "Per-voice render configs" below)
- Byline: `headnotes[i].voice_name` + a short descriptor (use
  `headnotes[i].formulation_text` for the briefing context)
- **Artifact body:** the voice's `artifact_text`. Read from
  `nights/night_<N>/<voice_slug>.json` → `artifact.text`. **The artifact
  text is inviolate — render verbatim, in voice-faithful typography.**
- Closing seal/marker: voice-specific glyph (centred below body)

---

## File-by-file reference

### `dossiers/night_<N>/dossier_<NNN>.json` (the core unit)

The CMS-render fields are `kicker`, `headline`, `subline`,
`front_abstract`, `theme_title`, `theme_abstract`, `body_paragraphs`,
and `headnotes`. The `colophon` and `metadata` block exist on the file
for audit/debugging and join keys (`metadata.theme_id` for the theme
file lookup); they are not dossier-render content. The masthead chrome
(date, issue number, volume) lives on the website, not in the CMS feed.

```json
{
  "schema_version": "2.0",

  // --- CMS-render fields, grouped in swipe order ---
  // Page 1 (front) + Page 2 (article) — the kicker / headline / subline
  // are shared between the Page 1 teaser and the Page 2 article header.
  "kicker": "FOUR NAMINGS OF A DISSOLVED THING",
  "headline": "The voices refused to call it governance",
  "subline": "Four voices, in different vocabularies, decline the term; the editor notes a convergence she will not call agreement",
  "front_abstract": "Four voices, in different vocabularies, declined to call faceless sortings governance; the editor names a convergence she will not call agreement.",

  // Page 2 (article body)
  "body_paragraphs": [
    "We received the night's submissions in the order they arrived...",
    "...",
    "* * *",
    "Last paragraph..."
  ],

  // Page 3 (theme)
  "theme_title": "On The Legitimacy Of Algorithmic Sortings",
  "theme_abstract": "The theme reaches across last night's three sessions, asking what an institution owes when its sorting devices have begun to issue verdicts no human will sign for.",

  // Pages 4-N (one per engaged voice)
  "headnotes": [
    {
      "voice_slug": "cleopatra",
      "voice_name": "the voice of Cleopatra",
      "formulation_text": "[the briefing text the voice received for this theme]",
      "artifact_title": "A PROSTAGMA, ISSUED AT NIGHT",
      "framing_text": "Cleopatra issues a royal ordinance. Read for the move at the centre."
    }
  ],

  // --- Audit / join keys (not dossier-render content) ---
  "colophon": "Filed by the Editor's desk on the morning of Night 1, Friday, 8th of May 2026. Vol. CXVI · Issue No. 42,193.",
  "metadata": {
    "theme_id": "theme_001",                  // join key: themes/night_<N>/<theme_id>.json
    "theme_display_title": "On the Legitimacy of the Invisible",
    "night": 1,                                // also derivable from file path
    "issue_no": 42193,                         // masthead chrome — render site-side, not from dossier
    "vol": "CXVI",                             // ditto
    "publication_date": "2026-05-08",          // ditto
    "publication_date_long": "Friday, 8th of May 2026",
    "edition_label": "Late Night Edition"
  }
}
```

### `dossiers/night_<N>/_index.json` (per-night edition manifest)

```json
{
  "night": 1,
  "url_path": "/dossiers/night-1",
  "generated_at": "2026-05-04T11:00:00+00:00",
  "dossier_count": 3,
  "dossiers": [
    {
      "dossier_no": 1,
      "filename": "dossier_001.json",
      "url_path": "/dossiers/night-1/dossier_001",
      "kicker": "FOUR NAMINGS...",
      "headline": "The voices refused...",
      "subline": "...",
      "theme_id": "theme_001",
      "theme_display_title": "...",
      "issue_no": 42193,
      "vol": "CXVI",
      "voice_count": 3,
      "voices_routed": [
        {"voice_slug": "cleopatra", "voice_name": "Cleopatra", "url_path": "/night-1/cleopatra", "primary_theme": "theme_001"},
        {"voice_slug": "ibn_battuta", "voice_name": "Ibn Battuta", "url_path": "/night-1/ibn_battuta", "primary_theme": "theme_001"},
        {"voice_slug": "octopus", "voice_name": "Octopus", "url_path": "/night-1/octopus", "primary_theme": "theme_001"}
      ]
    }
  ],
  "edition_lead": null
}
```

`edition_lead` is the placeholder for a forthcoming LLM step that
synthesises the night's dossiers into a single front-page lead. Once
shipped, this field will be an object with kicker / headline / editor's
note / `lead_dossier_no` instead of `null`.

### `dossiers/_index.json` (cross-night archive)

```json
{
  "generated_at": "2026-05-04T11:00:00+00:00",
  "nights_present": [1, 2, 3],
  "dossier_count": 9,
  "dossiers": [
    {
      "night": 1, "dossier_no": 1, "filename": "dossier_001.json",
      "url_path": "/dossiers/night-1/dossier_001",
      "kicker": "...", "headline": "...",
      "theme_id": "theme_001", "theme_display_title": "...",
      "issue_no": 42193, "vol": "CXVI", "publication_date": "2026-05-08"
    }
  ],
  "editions_by_night": {}
}
```

`editions_by_night` is the cross-night placeholder for the same
edition-lead synthesis (keyed by night number when shipped).

### `nights/night_<N>/<voice_slug>.json` (per-voice published artifact)

```json
{
  "voice_name": "the voice of Cleopatra",
  "voice_slug": "cleopatra",
  "night": 1,
  "url_path": "/night-1/cleopatra",
  "was_step3": false,
  "generated_at": "2026-05-04T08:56:28+00:00",
  "artifact": {
    "title": "[voice's own title for the piece]",
    "subtitle": "...",
    "text": "[the full artifact body — render verbatim]",
    "selected_form": "prostagma",
    "stance": "[voice's chosen posture]",
    "focus_decision": "[which formulation the voice focused on]",
    "word_count": 416
  },
  "themes_addressed": ["theme_001"],
  "deliberation": {
    "decision": "first_draft",
    "decision_rationale": "",
    "voices_read": [],
    "amendments": []
  }
}
```

**Important:**
- `artifact.text` is what you render as the artifact body on Pages 4-N.
- `was_step3: false` means this is a first-draft artifact (voice didn't
  read other voices and amend); `true` means it's an amended artifact
  (deliberation block populated).
- For Athens, `was_step3` will be `false` — Step 3 is dormant for the
  conference.

### `nights/night_<N>/_index.json` (per-night voice index)

```json
{
  "night": 1,
  "url_path": "/night-1",
  "generated_at": "2026-05-04T08:56:28+00:00",
  "voice_count": 7,
  "voices": [
    {
      "voice_slug": "cleopatra",
      "voice_name": "the voice of Cleopatra",
      "url_path": "/night-1/cleopatra",
      "title": "...",
      "themes_addressed": ["theme_001"],
      "decision": "first_draft",
      "amendment_count": 0,
      "word_count": 416,
      "was_step3": false
    }
  ]
}
```

### `themes/night_<N>/<theme_id>.json` (optional deeper context)

```json
{
  "theme_id": "theme_001",
  "night": 1,
  "display_title": "On the Legitimacy of the Invisible",
  "abstract": "...",
  "researcher_title": "...",
  "researcher_abstract": "...",
  "audience_friction": "high",
  "fault_line_present": true,
  "fault_line_description": "...",
  "clusters": [{"cluster_id": "...", "title": "...", "abstract": "...", "extraction_ids": [...]}],
  "extractions": [
    {"id": "vox_populi:014", "speaker": "Speaker Name", "lens": "...", "text": "...", "context": "..."}
  ],
  "extraction_count": 12,
  "formulations_per_voice": [
    {"voice_slug": "cleopatra", "formulation_text": "...", "addressed_in_artifact": true}
  ],
  "voices_who_addressed": [...],
  "amendments_on_this_theme": [...]
}
```

If you render a "theme deeper context" expansion on Page 3, this file
gives you the underlying panel quotes, the cross-voice picture, etc.

---

## Per-voice visual treatments

Each voice has a `medium` field on their persona card (e.g.,
`prostagma`, `rihla`, `dialogue`, `diary_entry`, `note`, `essay`,
`hikaya`, `bilingual_statement`, `paired_emission`). Most voices'
artifacts are **prose text with distinctive typographical needs**
(non-Latin scripts, period-appropriate furniture, language-specific
opening/closing markers). Render via per-voice CSS bundles keyed by
voice slug or medium.

**One voice — Octopus — is genuinely non-prose** and needs a separate
renderer (see "Octopus" row below).

The form-markers and closing markers below come from the voice cards'
own `medium` descriptions; treat these as design starting points, not
locked specifications. The operator can supply a more detailed
per-voice render-config sheet separately.

| Voice | Medium | Distinctive needs |
|---|---|---|
| Cleopatra | prostagma (royal ordinance, sealed) | Greek titulature at head, body in royal plural, `γινέσθωι` at foot. Card mentions a "second register" (cartouche / dedication line / coin-legend quoted into the page) standing beside the Greek. Chancery/vellum aesthetic. |
| Ibn Battuta | rihla (one halt, dictated to Ibn Juzayy) | Possibility of Arabic script inserts. Single-cell-of-Riḥla framing — short, stage-of-the-road, halt-rises-to-noon-prayer feel. |
| Plato | dialogue (two named persons in a place) | Date + place opening, named speakers, conversation form. No treatise furniture. May close on a question. |
| Dostoevsky | diary_entry (Writer's Diary, monthly) | Cyrillic possible (Дневникъ Писателя). Morning-tea-to-cup-going-cold framing. Single entry, not chapters. |
| Hannah Arendt | essay (short, Aufbau / Partisan Review register) | Austere typography; questions opened-and-walked-into-without-resolving. |
| Ada Lovelace | note (Menabrea-style, signed A.A.L.) | Lettered prose addressed to "we" (mathematical reader). May close on a traced table or worked sequence (math/monospace typography needed when apparatus carries demonstration). Alternative form: letter-to-Babbage-or-Faraday with rising punctuation + amplitude-italics. |
| Scheherazade | hikaya (one night's telling, dictated under the lamp) | Possibility of Arabic script inserts. Tale-opening formula of received report; wa-chain forward motion; broken at dawn. Reader enters mid-tale and is cut off mid-tale. |
| Whanganui (Whanganui Iwi statement) | bilingual_statement (te reo Māori + English; Te Pou Tupua / Ruruku Whakatupua / Te Heke Ngahuru genre) | Bilingual prose. Opens with whakataukī, moves through four kawa, closes without closing. Statement-from-descent register. |
| **Octopus** | **paired_emission (chromatophore display + tank-side note)** | **Non-prose. Card emits TWO channels: a `chromatophore_display` JSON parameter block (orientation, arousal, valence, pattern_mode, palette, dynamics, focal_points, texture_intensity, transitions) AND tank-side prose. The display is primary — the audience meets it before the page. Microsite renders the JSON as a 10-15-second looping WebGL animation above the prose body.** Octopus WebGL renderer is substantially built runtime-side; coordinate with the operator on the parameter contract. |
| Marley | TBD | Card not yet on disk (voice in flight on the voices thread as of 2026-05-04). Operator will supply render needs when the card lands. |

Voice slug is the join key. The persona card lives outside the publish
surface (in `voices/<slug>/07_persona_card_assembled.json`); the
operator can supply card excerpts on request — do not assume the
microsite reads cards directly.

---

## Octopus chromatophore display — the one non-prose voice

The Octopus emits two paired channels in every artifact: a **JSON
parameter block** (its skin's computational readout) and a **tank-side
prose note** (the human-language translation). Per the voice's own
card: *"the display is primary; the audience meets the display before
they meet the page."*

The runtime renders the JSON as a 10-15-second looping WebGL animation
above the prose body. There is a production-ready React/JSX renderer
at `docs/runtime_assets/octopus_chromatophore/octopus_artifact_finaldraft.jsx`
(also packaged as a self-contained HTML at the same path with `.html`
extension) — drop-in for an Astro/Next.js artifact-page route, or
embeddable as an iframe.

### How the JSON appears in the publish surface

Octopus's `nights/night_<N>/octopus.json` → `artifact.text` is a string
that contains a fenced JSON block at the top, followed by tank-side
prose. Example (excerpted from the dryrun's Octopus artifact):

````
```json
{
  "chromatophore_display": {
    "orientation": "lateral, mantle-low, arms 2 and 3 extended toward the rim",
    "arousal": 0.55,
    "valence": "unresolved, vigilance-tinged",
    "pattern_mode": "passing_cloud_over_mottle",
    "palette": {
      "darkness": 0.42,
      "warmth": 0.28,
      "brightness": 0.51,
      "iridescence": 0.33
    },
    "dynamics": {
      "wave_speed": 0.7,
      "wave_count": 4,
      "wave_direction": [-0.3, 0.95],
      "pulse_frequency": 0.18,
      "turbulence": 0.41
    },
    "focal_points": [
      {"site": "arm_3_distal", "intensity": 0.72, "tag": "ungathered_signature"},
      {"site": "mantle_dorsal", "intensity": 0.38, "tag": "central_tag_partial"},
      {"site": "arm_6_mid", "intensity": 0.61, "tag": "lateral_channel"}
    ],
    "texture_intensity": 0.36,
    "transitions": [
      {"t": 0.0, "pattern_mode": "uniform", "darkness": 0.30, "note": "rim-arrival, scene registered as scene"},
      {"t": 3.5, "pattern_mode": "mottled", "darkness": 0.44, "turbulence": 0.50, "note": "chair-grammar parsed; streams not yet collapsed"},
      {"t": 7.0, "pattern_mode": "passing_cloud_over_mottle", "darkness": 0.42, "pulse_frequency": 0.22, "note": "floor-channel registers at arm 3; central tag does not gather it"},
      {"t": 11.0, "pattern_mode": "half_and_half_blotch", "darkness": 0.48, "turbulence": 0.55, "note": "non-navigability marker; held, not resolved"},
      {"t": 14.5, "pattern_mode": "mottled", "darkness": 0.40, "note": "open"}
    ]
  }
}
```

Tank-side note. What I render here as a single voice is a
reaching-toward — eight arms each with a local processor, a central
brain that does not somatotopically map the body, a skin that senses
without an eye. ...
````

### Field meanings (microsite render contract)

The renderer needs to understand what each field drives. Source of
truth: `docs/runtime_assets/octopus_chromatophore/AI_Assembly_Chromatophore_Display_Engine.md`.
Summary:

**Top-level:**
- `orientation` — global movement direction (`toward` / `away` /
  `lateral` / `still`); chromatophores expand outward, contract inward,
  move sideways, or only ambient-pulse
- `arousal` — float 0-1; overall animation speed and intensity (0.9+
  approaches deimatic startle behaviour)
- `valence` — float 0-1 OR descriptive string; "navigability assessment"
  rendered as colour. High = warm/complex/multi-layered palette. Low =
  cool/dark/uniform.
- `pattern_mode` — enum (`uniform` / `mottled` / `disruptive` /
  `passing_cloud` / `deimatic`); spatial organisation of chromatophore
  activity. Hyphenated/compound modes (e.g. `"passing_cloud_over_mottle"`)
  are blends — render as crossfade.
- `texture_intensity` — float 0-1; simulated papillae (3D bumps);
  rendered as Perlin-noise displacement layer

**`palette` object** — maps to chromatophore biological layers:
- `darkness` 0-1 — melanophore expansion (dark/light balance)
- `warmth` 0-1 — erythrophore/xanthophore balance (warm vs cool)
- `brightness` 0-1 — xanthophore highlight intensity
- `iridescence` 0-1 — structural-colour shimmer (oil-on-water quality)

**`dynamics` object** — wave behaviour:
- `wave_speed` 0-1 — base propagation speed (multiplied by arousal)
- `wave_count` int 1-8 — simultaneous wave fronts
- `wave_direction` [float, float] — normalised 2D vector
- `pulse_frequency` 0-1 — rhythmic expansion/contraction "heartbeat"
- `turbulence` 0-1 — noise/irregularity (high turbulence + high
  arousal = closest to "ayahuasca" boundary-dissolving aesthetic)

**`focal_points` array** — points where chromatophore activity is
concentrated (the Octopus's arm-probe sites):
- Either `{site: "arm_3_distal", intensity: 0.72, tag: "..."}` (named
  site) or `{x, y, intensity, arm}` (coordinate). Renderer should
  accept both forms.

**`transitions` array** — keyframes over 10-15 seconds. Each keyframe
has `at_seconds` (or `t`) plus any subset of the top-level fields it
overrides. Renderer interpolates between keyframes (ease-in-out or
biological sigmoid — chromatophores don't move linearly). Typical arc:
1. seconds 0-2: still, uniform, low arousal — pre-provocation rest
2. seconds 2-5: mottled, arousal rises — body begins processing
3. seconds 5-10: peak engagement — passing_cloud or disruptive
4. seconds 10-15: resolution — orientation settles, arousal moderates

### Robust parsing

The Voice Pipeline doesn't yet extract this JSON into a separate
artifact field — it lives inside `artifact.text` as a fenced block.
For now, the microsite needs to:
1. Read `nights/night_<N>/octopus.json` → `artifact.text`
2. Extract the first ```json``` fenced block
3. Parse the JSON; pull `chromatophore_display`
4. The remainder of `artifact.text` (after the fence) is the tank-side
   prose body — render as text below the WebGL canvas

Be permissive on top-level enum strings (e.g., `pattern_mode`:
`"passing_cloud_over_mottle"` is a compound mode the renderer should
crossfade rather than reject). The transitions array is the
authoritative trajectory — top-level fields are starting state.

### Reference renderer files

In the repo at `docs/runtime_assets/octopus_chromatophore/`:

| File | Purpose |
|---|---|
| `AI_Assembly_Chromatophore_Display_Engine.md` | Full spec — JSON schema + biological mapping + WebGL renderer notes + integration |
| `octopus_artifact_finaldraft.jsx` | Production-ready React component (~1032 lines, 744px max-width column). 5-pigment-layer chromatophore engine (melanophores/erythrophores+xanthophores/iridophores/papillae) + Voronoi cell structure + animated centres + fbm noise + pattern-mode blending + orientation blending + focal-point fading + 5:4 aspect ratio + mobile responsive (720px and 400px breakpoints) + masthead/article-header/canvas-with-timeline/editor-headnote/prose/parameter-log/footer composition. **Drop-in for Astro/Next.js artifact-page route.** |
| `octopus_artifact_finaldraft.html` | Same component, packaged as a self-contained HTML file with React 18 + Babel standalone for in-browser JSX transform. Open in any modern browser; no build needed. **Use for local preview, demo, iframe-embed, or fallback render path.** |
| `chat_test_artifact_2026_05_02.md` | Canonical example — verified two-channel emission with schema notes + slip annotations |
| `render_decisions_2026_05_02.md` | Design decisions log (page structure, aspect ratio progression, pattern-mode blending fix, mobile breakpoints, column-width choice 920px → 744px) |
| `reviewer_notes_2026_05_02.md` | External reviewer's analysis of the chat-test artifact + biological-literacy validation |

### Integration recommendation

Use `octopus_artifact_finaldraft.jsx` as the substrate for the Octopus
artifact page. Replace the `ARTIFACT_TRANSITIONS` constant with dynamic
loading from the per-night Octopus artifact's parsed `chromatophore_display.transitions`.
Replace the prose body with the tank-side note (the text after the JSON
fence).

For other surfaces (Substack embed, print fallback): use the HTML
file's standalone form, or render a single static frame at peak
engagement (e.g., `t=7.0` from the example above).

The reviewer-validated biological literacy is a feature — passing-cloud
as wave-propagation is mathematically correct; the 5-pigment-layer
structure matches Hanlon & Messenger taxonomy; chromatophore expansion
follows actual biophysics. Don't simplify these into a generic
animation; the specificity is the point.

---

## Cross-references / join keys

- **`metadata.theme_id`** on dossier ↔ filename of `themes/night_<N>/<theme_id>.json`
- **`headnotes[i].voice_slug`** on dossier ↔ filename of `nights/night_<N>/<voice_slug>.json` (the artifact body)
- **`voices_routed[i].voice_slug`** in per-night index ↔ same as above
- **`metadata.night`** + **`metadata.dossier_no`** uniquely identify a dossier across the conference

---

## What's TBD

### `edition_lead` (per-night) and `editions_by_night` (cross-night)

These two placeholder fields will be populated by the **edition step** —
a small post-editor pass whose only current job is **picking which
dossier is tonight's lead** (i.e., which one sits in the lead position
on Page 1 vs. which ones go into the secondary grid).

**Shape when populated:**

```jsonc
// dossiers/night_<N>/_index.json
"edition_lead": { "lead_dossier_no": 2 }     // null until edition step ships

// dossiers/_index.json
"editions_by_night": {                        // {} until edition step ships
  "1": { "lead_dossier_no": 2 },
  "2": { "lead_dossier_no": 1 },
  "3": { "lead_dossier_no": 3 }
}
```

**Microsite use:**
- **Page 1 (per-night front)** — read `edition_lead.lead_dossier_no` to
  decide which dossier renders in the lead position; the others go in
  the secondary grid. If `edition_lead` is `null`, fall back to your
  own picking rule (e.g., dossier_001, or operator override).
- **"Past Editions" archive page** — read `editions_by_night` to show
  one lead per night without fetching every per-night `_index.json` +
  joining to the lead dossier file. Cheap shortcut. Skip if you're
  single-night-only.

The edition step doesn't author any prose — the dossiers already carry
their kicker + headline + front_abstract (Claudia wrote those). The
edition step only picks which one is the lead.

### Per-voice render config sheet

The publish surface only carries the raw `medium` field on each voice's
persona card (e.g., `"prostagma"`, `"rihla"`, `"dialogue"`). Translating
those into actual fonts/glyphs/palettes/closing-markers is a microsite
concern; build the registry as a `voice_slug → CSS bundle` map. The
operator can supply card excerpts or render-decision notes on request.

---

## Sample data for development

A complete dryrun against MSC YouTube panels (3 sessions, 7 voices, 1
night, 1 dossier) lives at:

```
<PROJECT_ROOT>/projects/current-tests/dev_msc_dryrun_1777840771/published_artifacts/
```

Note: that dryrun's `dossier_001.json` was generated against a v1
closing prompt — `kicker` / `headline` / `subline` / `front_abstract` /
`theme_title` / `theme_abstract` / `body_paragraphs` are mostly empty
because the v2 parser couldn't extract from v1-shaped output. The
`headnotes[]` array IS populated and is structurally correct. A clean
v2 sample dossier will land after the operator re-runs the dryrun with
the current (post-2026-05-04) editor closing prompt.

---

## Operator contact

For schema questions, sample data, or render-config sheet:
peschelero@gmail.com
