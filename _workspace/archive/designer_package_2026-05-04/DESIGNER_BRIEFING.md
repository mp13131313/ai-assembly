# AI Assembly — designer briefing

**Date:** 2026-05-04 (simplified)
**For:** the web designer building the microsite / CMS

The publication produces **dossiers** — one self-contained JSON file
per dossier. A night produces 1-5 dossiers; the conference (3 nights)
produces ~10-15.

You receive two things from the publish pipeline:

1. **Per-night dossier index** — `dossiers/night_<N>/_index.json`. A
   thin manifest of the night's dossiers.
2. **One self-contained dossier file per dossier** —
   `dossiers/night_<N>/dossier_<NNN>.json`. Carries everything needed
   to render its 4 surfaces (frontpage teaser, theme article, theme
   page, per-artifact pages).

The website owns masthead chrome (paper title, date strip, issue
numbers); the CMS does not feed it.

---

## The dossier file

```jsonc
{
  "schema_version": "2.0",

  // === FRONTPAGE TEASER + THEME ARTICLE ===
  // kicker + headline are shared between the front teaser (Page 1) and
  // the article (Page 2). subline is article-only. front_abstract is
  // teaser-only.
  "kicker":         "FOUR NAMINGS OF A DISSOLVED THING",
  "headline":       "The voices refused to call it governance",
  "front_abstract": "Four voices declined to call faceless sortings governance; the editor names a convergence she will not call agreement.",
  "subline":        "Four voices, in different vocabularies, decline the term; the editor notes a convergence she will not call agreement",

  // Article body (Page 2)
  "body_paragraphs": [
    "We received the night's submissions in the order they arrived...",
    "...",
    "* * *",
    "Last paragraph..."
  ],

  // === THEME PAGE ===
  // Paper-voice short title + abstract Claudia writes for this surface;
  // she reads the Researcher's source title + abstract + cluster
  // extractions in her own user prompt and reformulates them in
  // publishing register. NOT a copy of the Researcher's text.
  "theme_title_for_dossier":    "On The Legitimacy Of Algorithmic Sortings",
  "theme_abstract_for_dossier": "The theme reaches across last night's three sessions, asking what an institution owes when its sorting devices have begun to issue verdicts no human will sign for.",

  // === ARTIFACT PAGES ===
  // One headnote per engaged voice. Each is fully self-contained:
  // editorial chrome (artifact_title, framing_text) + the voice's
  // actual artifact body (artifact_text) + the CSS-bundle key
  // (artifact_form). No separate file fetch needed to render an
  // artifact page.
  "headnotes": [
    {
      "voice_slug":       "cleopatra",
      "voice_name":       "the voice of Cleopatra",
      "artifact_title":   "A PROSTAGMA, ISSUED AT NIGHT",
      // framing_text — Claudia's editorial gloss; she references the
      // formulation thematically. Use this as the per-artifact headnote.
      "framing_text":     "Cleopatra issues a royal ordinance. Read for the move at the centre.",
      // artifact_form — CSS-bundle key for per-voice rendering of the body.
      "artifact_form":    "prostagma",
      // artifact_text — the voice's full Step 2 body. Render verbatim,
      // in voice-faithful typography keyed by artifact_form.
      "artifact_text":    "[the full artifact body]",
      // formulation_text — the raw briefing the voice received for this
      // theme. Delivered separately from framing_text so the designer
      // can choose: render alongside (e.g. as a small "the question
      // put to her was…" note), use as byline context, or omit
      // entirely. framing_text already contains Claudia's editorial
      // reference to the formulation.
      "formulation_text": "[the briefing the voice received]"
    }
  ],

  // === AUDIT (not render content) ===
  "metadata": {
    "theme_id":              "theme_001",   // join key (see "Optional joins" below)
    "theme_display_title":   "On the Legitimacy of the Invisible",
    "night":                 1,
    "issue_no":              42193,         // masthead chrome — render site-side
    "vol":                   "CXVI",
    "publication_date":      "2026-05-08",
    "publication_date_long": "Friday, 8th of May 2026",
    "edition_label":         "Late Night Edition"
  }
}
```

---

## The 4 surfaces

| Surface | Fields |
|---|---|
| **Frontpage teaser** (one card per dossier on the night's index page) | `kicker`, `headline`, `front_abstract` |
| **Theme article** (Page 2 — Claudia's editorial piece) | `kicker`, `headline`, `subline`, `body_paragraphs[]` |
| **Theme page** (Page 3 — orients a reader landing here) | `theme_title_for_dossier`, `theme_abstract_for_dossier` |
| **Artifact page** (Pages 4-N — one per engaged voice) | `headnotes[i].voice_name`, `.artifact_title`, `.framing_text`, `.artifact_form`, `.artifact_text` (+ optional `.formulation_text` — raw briefing, see note below) |

### Body paragraph rules

- Paragraphs separated by blank lines in the source; in JSON they're
  array elements. Render with paragraph breaks between elements.
- `* * *` appears as its own array element — render as a centred
  asterism break / section separator.

### Length envelopes (for layout planning)

| Field | Length |
|---|---|
| `kicker` | 3-7 words, ALL-CAPS |
| `headline` | 8-15 words |
| `subline` | 25-60 words |
| `front_abstract` | 30-50 words |
| `body_paragraphs` total | 350-500 words single-voice / 500-700 multi-voice |
| `theme_title_for_dossier` | 5-10 words |
| `theme_abstract_for_dossier` | 60-100 words |
| `headnotes[i].artifact_title` | 4-12 words |
| `headnotes[i].framing_text` | 1-2 sentences |
| `headnotes[i].artifact_text` | varies by voice (~400-1000 words typical) |

---

## Per-night dossier index

`dossiers/night_<N>/_index.json` — a thin manifest of the night's
dossiers. Use it for the per-night front page (which dossier in the
lead position, which in the secondary grid).

```jsonc
{
  "night": 1,
  "dossier_count": 3,
  "dossiers": [
    {
      "dossier_no":            1,
      "filename":              "dossier_001.json",
      "url_path":              "/dossiers/night-1/dossier_001",
      "kicker":                "FOUR NAMINGS...",
      "headline":              "The voices refused...",
      "theme_id":              "theme_001",
      "theme_display_title":   "...",
      "voice_count":           3
    }
  ],
  "edition_lead": null,        // see "What's TBD" below

  // Per-voice navigation aid. Each voice appears once per night (v2:
  // each voice routes to exactly one primary dossier). Lets you render
  // a per-night per-voice index — links converge on the dossier
  // (and headnote) that voice's artifact lives in.
  "voices_in_night": {
    "cleopatra": {
      "voice_slug":          "cleopatra",
      "voice_name":          "the voice of Cleopatra",
      "primary_dossier_no":  1,
      "primary_theme_id":    "theme_001",
      "url_path":            "/dossiers/night-1/dossier_001",
      "primary_formulation": "[the briefing the voice received for this theme]",
      "artifact_title":      "A PROSTAGMA, ISSUED AT NIGHT",
      "artifact_form":       "prostagma"
    }
  }
}
```

`edition_lead` is `null` until a small forthcoming step ships. When
populated it'll be `{ "lead_dossier_no": 2 }` — the hint that
dossier_002 sits in the lead position; the others go in the secondary
grid. While it's `null`, fall back to your own picking rule (e.g.,
dossier_001, or operator override).

---

## Per-voice rendering (the `artifact_form` key)

Each headnote's `artifact_form` field tells the microsite which
per-voice CSS bundle to apply when rendering that artifact's body.
Build the registry as a `artifact_form → CSS bundle` map. Common forms:

| Form | Voice | Distinctive needs |
|---|---|---|
| `prostagma` | Cleopatra | Greek titulature, royal-plural body, `γινέσθωι` close, chancery aesthetic |
| `rihla` | Ibn Battuta | Possible Arabic script inserts, single-halt-of-the-road framing |
| `dialogue` | Plato | Date + place opening, named speakers, conversation form, may close on a question |
| `diary_entry` | Dostoevsky | Cyrillic possible (Дневникъ Писателя), Writer's Diary register |
| `essay` | Hannah Arendt | Austere typography; Aufbau / Partisan Review register |
| `note` | Ada Lovelace | Lettered prose addressed to "we", signed A.A.L.; may close on a math table or worked sequence (monospace needed) |
| `hikaya` | Scheherazade | Possible Arabic script, tale-opening formula, broken-at-dawn pacing |
| `bilingual_statement` | Whanganui | te reo Māori + English; opens with whakataukī, four-kawa structure |
| `paired_emission` | **Octopus — non-prose; see next section** | Two-channel: WebGL chromatophore animation + tank-side prose |
| `reasoning_with_riddim` | **Bob Marley — also two-channel; render-layer TBD** | Per his card: *"I give you a reasoning, and a riddim under it. The reasoning is me talking the way I talk when a journalist sit down with me at 56 Hope Road and the tape run — Patwa folding into scripture, scene before argument, proverb where another man would put a thesis. The riddim is the music underneath, no voice on it, just the bass and the drum and the skank, so the reasoning sit in its proper sonic yard."* Two channels in `artifact_text`: prose reasoning (Patwa-inflected) + a separate parameter block for the riddim (audio track / Suno-generated stem / SVG-music-cue). Microsite: render the reasoning as prose; cue the riddim as ambient audio. **Card shipped 2026-05-04 PM; render path is B7 sub-task — analogous to Octopus WebGL but for sound. Operator will supply renderer when built.** |

The operator can supply detailed per-voice render-decision notes on
request.

---

## Octopus — the one non-prose voice

The Octopus's `artifact_text` carries TWO channels:

1. A fenced JSON block at the top — `chromatophore_display` parameters
2. Tank-side prose below the fence — the human-language translation

Microsite logic for the Octopus artifact page:

1. Read the headnote's `artifact_text`
2. Extract the first ```` ```json ```` fenced block
3. Parse it; pull `chromatophore_display`
4. Render as a 10-15-second looping WebGL animation above the prose
5. The remainder of `artifact_text` (after the fence) is the prose body

A production-ready React component lives at
`docs/runtime_assets/octopus_chromatophore/octopus_artifact_finaldraft.jsx`
(also packaged as standalone HTML at the same path with `.html`
extension). Drop-in for the Octopus artifact-page route. Replace the
`ARTIFACT_TRANSITIONS` constant with dynamic loading from the parsed
`chromatophore_display.transitions[]`.

### Chromatophore display fields

```jsonc
{
  "chromatophore_display": {
    "orientation":       "lateral, mantle-low, arms 2 and 3 extended toward the rim",   // global movement direction
    "arousal":           0.55,   // 0-1; animation speed and intensity
    "valence":           "unresolved, vigilance-tinged",   // navigability assessment, rendered as colour
    "pattern_mode":      "passing_cloud_over_mottle",   // spatial organisation; may be a blend
    "palette": {
      "darkness":     0.42,   // melanophore expansion
      "warmth":       0.28,   // erythrophore/xanthophore balance
      "brightness":   0.51,   // xanthophore highlight intensity
      "iridescence":  0.33    // structural-colour shimmer
    },
    "dynamics": {
      "wave_speed":      0.7,
      "wave_count":      4,
      "wave_direction":  [-0.3, 0.95],
      "pulse_frequency": 0.18,
      "turbulence":      0.41
    },
    "focal_points": [
      {"site": "arm_3_distal", "intensity": 0.72, "tag": "ungathered_signature"}
    ],
    "texture_intensity": 0.36,
    "transitions": [
      {"t": 0.0,  "pattern_mode": "uniform",                       "darkness": 0.30, "note": "rim-arrival"},
      {"t": 3.5,  "pattern_mode": "mottled",                       "darkness": 0.44, "turbulence": 0.50, "note": "scene parsed"},
      {"t": 7.0,  "pattern_mode": "passing_cloud_over_mottle",     "darkness": 0.42, "pulse_frequency": 0.22, "note": "non-resolution"},
      {"t": 14.5, "pattern_mode": "mottled",                       "darkness": 0.40, "note": "open"}
    ]
  }
}
```

The `transitions[]` array is the authoritative trajectory; top-level
fields are the starting state. Be permissive on top-level enum strings
(e.g. `"passing_cloud_over_mottle"` is a compound mode the renderer
should crossfade rather than reject).

Full spec at `docs/runtime_assets/octopus_chromatophore/AI_Assembly_Chromatophore_Display_Engine.md`.

---

## Optional joins (deeper context)

The following surfaces are *optional* — the dossier is self-contained
without them. Use only if your design wants deeper navigation.

| File | Use |
|---|---|
| `published_artifacts/themes/night_<N>/<theme_id>.json` | Underlying Researcher record — clusters, panel extractions, formulations per voice. Join via `metadata.theme_id`. Useful if you want a "deeper context" expansion on Page 3. |
| `published_artifacts/voices/<voice_slug>.json` | Per-voice timeline across all nights. Useful if you want a per-voice index page. |
| `published_artifacts/dossiers/_index.json` | Cross-night flat list of every dossier. Useful for a "Past Editions" archive. |
| `published_artifacts/nights/night_<N>/<voice_slug>.json` | Per-voice published artifact (audit/lineage; the body is already in the dossier headnote — these files are NOT needed for CMS rendering). |

---

## What's TBD

- **`edition_lead`** in the per-night index — currently `null`; will
  become `{ "lead_dossier_no": N }` once a small lead-picker step
  ships. Microsite should treat absent/null as "use my fallback rule."
- **Per-voice render bundles** (operator + designer collaboration) —
  the `artifact_form → CSS` registry is microsite-side; operator can
  supply detailed per-voice render-decision notes on request.

---

## Sample data

A complete dryrun against MSC YouTube panels (3 sessions, 7 voices, 1
night, 1 dossier) lives at:

```
<PROJECT_ROOT>/projects/current-tests/dev_msc_dryrun_1777840771/published_artifacts/
```

The current dryrun's `dossier_001.json` is partial — it was generated
against the v1 closing prompt, so most fields are empty. A clean
v2-shaped sample dossier with embedded artifact bodies will land after
the operator re-runs the dryrun with today's pipeline (commit `b02d1fb`
or later).

---

## Operator contact

For schema questions, sample data, or per-voice render-decision notes:
peschelero@gmail.com
