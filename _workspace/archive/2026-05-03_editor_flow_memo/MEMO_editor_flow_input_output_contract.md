> **🗄 ARCHIVED 2026-05-03 PM.** This memo's content has been folded into `docs/AI_Assembly_Editor_Pipeline.md` v2 (canonical going forward). Open questions surfaced here have either been resolved (see v2 changelog) or migrated to v2's §"Open Questions" section. Do not consult this memo for current contracts — use the v2 spec.

---

# Memo: editor flow input/output contract — implications from Claudia persona-construction session

**To:** runtime thread (Editor Pipeline implementation)
**From:** voices thread (Claudia Pinchbeck persona-construction session)
**Date:** 2026-05-03
**Re:** input/output contract clarifications surfaced during Claudia persona prep; what runtime needs to settle vs what the persona card carries
**Companion:** `voices/CLAUDIA_PINCHBECK_PERSONA_PREP_2026-05-03.md` (the persona-construction state)

---

This memo captures editor-flow architectural clarifications that emerged during a long working session on Claudia Pinchbeck's persona card. Most of these are confirmations or refinements of what `docs/AI_Assembly_Editor_Pipeline.md` v1 already specified; some are updates from the Briefing v3 (Matthias's second pass, dated 8 May 2026, at `~/Desktop/Briefing.html`).

The voices thread is constructing Claudia's persona card via a hybrid pipeline path; runtime owns the editor flow implementation. This memo is the seam between them.

---

## 1. Input contract — per-dossier user prompt

Editor Pipeline v1 specified one Anthropic call per dossier; one dossier per theme; N dossiers per night. **Confirmed correct**, with two cleanups below.

### Input shape (cleaned — hallucinated fields removed)

```json
{
  "edition_metadata": {
    "night": 1,
    "issue_no": 42193,
    "vol": "CXVI",
    "publication_date": "2026-05-08",
    "publication_date_long": "Friday, 8th of May 2026",
    "edition_label": "Late Night Edition"
  },
  "theme": {
    "theme_id": "theme_001",
    "theme_title_from_researcher": "...",
    "theme_abstract": "...",
    "clusters": [
      {
        "cluster_id": "...",
        "cluster_title": "...",
        "cluster_abstract": "...",
        "extractions": [...]
      }
    ]
  },
  "engaged_voices": [
    {
      "voice_slug": "plato",
      "voice_name": "Voice of Plato",
      "voice_card_excerpts": {
        "medium": "...",
        "register_and_tone": "...",
        "character": "..."
      },
      "formulation": {
        "text": "...",
        "mode": "question|proposition",
        "context_narrative": "..."
      },
      "step2_artifact": {
        "artifact_text": "...",
        "selected_form": "...",
        "focus_decision": "...",
        "stance": "..."
      }
    }
  ],
  "prior_editions": [...]
}
```

### Removed from earlier Editor Pipeline v1 sketches

- `marathon_panel_source` / `marathon_panel_date` — runtime would have to manufacture these; the Researcher's theme_abstract already carries where the theme came from, and Claudia doesn't need a separate "what session of the WBBF" attribution she wouldn't have a reliable way to derive
- `dossier_no` — duplicates theme position in the night's edition; if needed can be derived from theme order, no separate input field

### Removed from Editor Pipeline v1's per-call shape

- `is_lead_theme` flag and `secondary_themes_summary` array — Claudia doesn't need to know which theme is the lead. Lead-vs-grid is a layout decision (runtime's editor-pipeline-runtime layer, not Claudia's prose-generation layer). Claudia produces ONE uniform front-page teaser block per theme; the layout layer above her picks which is lead and which goes in the grid.

### Confirmed correct from Editor Pipeline v1

- `step2_artifact` includes `selected_form`, `focus_decision`, `stance`, `artifact_text` — all from Voice Pipeline Step 2 output ✓
- `formulation` includes `text`, `mode`, `context_narrative` — from Provocateur briefing ✓
- `voice_card_excerpts` includes `medium`, `register_and_tone`, `character` — small slice of voice card for byline-descriptor and per-voice register-torque cueing ✓
- `prior_editions` for cross-night state on Night 2/3 ✓

### Per-night vs per-theme call architecture — confirmed per-theme

Editor Pipeline v1 §"One Anthropic call per dossier" specifies one call per dossier (per theme). **Confirmed correct.** Reasons:

- Parallelisable across themes
- Prefix caching shares Claudia's persona card across calls within a night
- Bounded input per call (one theme + its engaged voices, not the entire night)
- Each call is independent — no inter-call coordination needed

N calls per night where N = number of engaged themes (1–10 per Briefing v3).

---

## 2. Output contract — per-dossier structured JSON

**This is the big architectural item.** v2 schema's artifact cluster (`medium` + `technical_capabilities` + `characteristic_output_structure` + `relationship_to_detailed_response` + `aesthetic_qualities` + `stance_tendency` + `length_and_format_constraints` + `quality_criteria`) was designed for panel voices producing one artifact per night as one `artifact_text` string. Claudia produces a structured JSON object per theme.

**Resolution:** the persona card describes the compound output **prose-style** in the v2 fields. The Editor Pipeline runtime defines the **JSON shape** as a structured-output contract on `editor_dossier.md` closing prompt + an output schema. Two layers, no breaking conflict.

### Output shape (per-theme dossier)

```json
{
  "theme": {
    "theme_id": "theme_001",
    "theme_display_title": "..."
  },
  "front_page_teaser": {
    "kicker": "...",
    "headline": "...",
    "abstract": "...",
    "pull_quote": "...",
    "pull_quote_attribution": "the voice of Plato"
  },
  "article": {
    "kicker": "Proceedings Of The Assembly · Night One",
    "headline": "...",
    "subline": "...",
    "byline": "By Our Athens Correspondent",
    "body_paragraphs": ["...", "...", "..."]
  },
  "summary": {
    "theme_abstract": "...",
    "plain_summary": "..."
  },
  "headnotes": [
    {
      "voice_slug": "plato",
      "voice_name": "Voice of Plato",
      "formulation_text": "...",
      "framing_text": "..."
    }
  ]
}
```

### Field-level constraints (per Briefing v3 + Editor Pipeline v1)

| Field | Length | Render |
|---|---|---|
| `front_page_teaser.kicker` | 3–7 words | All-caps, tracked |
| `front_page_teaser.headline` | 8–15 words | Sentence about an event; lead on small specific gesture |
| `front_page_teaser.abstract` | ~2 lines | Two-line teaser for grid placement |
| `front_page_teaser.pull_quote` | optional | If used: lead-theme placement only |
| `front_page_teaser.pull_quote_attribution` | "the voice of [X]" form | Always `the voice of` prefix per naming convention |
| `article.kicker` | "Proceedings Of The Assembly · Night [N]" | Standing kicker; same per night |
| `article.headline` | 8–15 words | Sentence about an event; bodily/gestural specific |
| `article.subline` | 25–60 words | Italic deck; multi-clause semicolon-chained |
| `article.byline` | "By Our Athens Correspondent" or "By Claudia Pinchbeck, for the desk · [time] EEST · [N] min read" | Byline split is operator-decision; see §3 |
| `article.body_paragraphs` | 350–500 words single-voice; 500–700 multi-voice | First paragraph survives front-page lift |
| `summary.theme_abstract` | ~80 words | Plain reportage; what the theme is |
| `summary.plain_summary` | ~80 words | Plain reportage; where it came from |
| `headnotes[i].formulation_text` | exact formulation | Italic in render |
| `headnotes[i].framing_text` | 1–2 sentences | Roman in render; light poetic editorial framing |
| `headnotes[i]` total | 30–80 words | 2 lines max 3 |

### Naming convention — non-negotiable in output

Per Briefing v3 + Frame Concept v1: **"the voice of X"** non-negotiable across all fields. Including in headlines (which absorb the constraint via the longer form). The `voice_name` field on engaged voices follows this convention; Claudia's output preserves it.

Example: "The Voice Of Dostoevsky Reports A Cold In His Hands" — yes. "Dostoevsky To Attend Forum" — no.

### Asterism breaks (period convention)

Claudia's output may include section breaks within `article.body_paragraphs` to mark major beat changes (period-correct convention from mid-century broadsheets). Could be encoded as either:
- (a) Inline `* * *` markers within the paragraph array
- (b) Separate `asterism_break_after_paragraph_indices: [2, 5]` field

(b) is cleaner for render; (a) is simpler. Runtime decides.

---

## 3. Byline convention — operator decision still open

Per the prior conversation, two clean options:

**Option A — single house byline.** Everything Claudia touches signed "By Claudia Pinchbeck, for the desk · [time] EEST · [N] min read." Simple, consistent, institutional.

**Option B — split byline by function.** Theme articles filed by correspondents ("By Our Athens Correspondent"); editorial framing (headnotes, colophon) signed by Claudia for the desk. Implies a newsroom: a desk that has correspondents filing to it.

**Recommendation per the prior conversation: Option B.** Truer to the 1947 broadsheet conceit (real papers ran a mix of named bylines, "Our Correspondent" filings, and unsigned desk copy). Maps cleanly onto the article-vs-headnote register split.

Operator decision needed. Affects `article.byline` and `headnotes[*]` (which are unsigned individually but signed collectively at the colophon level).

---

## 4. Per-voice register torques — where they live

The "one spine, ten bends" principle: Claudia's prose has one register (period broadsheet) that bends per voice when reporting on each voice's section.

**Where this lives in the persona card:** `translation_protocol`. Per-voice torque IS a form of translation (form-translation per voice register). One field carrying both layers — modern→period form-translation AND per-voice register torques.

**Implications for editor pipeline runtime:**

- The 10 voices' torque descriptions live in Claudia's `translation_protocol` (loaded into her system prompt always)
- Runtime user prompt's `engaged_voices[i].voice_card_excerpts` pulls `medium`, `register_and_tone`, `character` — these are the cues Claudia uses to apply the right torque to each voice's section
- Claudia is fluent in all 10 voices' registers via `translation_protocol`; the per-call cues from `voice_card_excerpts` are reminders, not definitions

**No schema extension needed.** Earlier proposal of a separate `per_voice_bends` field is dropped. The `translation_protocol` field carries both jobs.

---

## 5. Form-fit honesty — runtime-side implications

Claudia's persona card encodes the form-fit-honesty principle: for voices the form genuinely cannot carry (Whanganui River, Octopus, possibly Marley), the desk's job is to fail honestly in the form rather than perform fluency it does not have.

**Runtime implications:**

- Editor pipeline output's `metadata.form_fit_status: "fits|admits-bad-fit"` — Claudia self-reports per dossier whether her form carried the engaged voices or had to admit failure
- For dossiers where `form_fit_status: "admits-bad-fit"`, the article body is shorter and more terse; the headnote may include a one-line note that the form did not carry the artifact
- The microsite render layer could surface this metadata for operator audit (which dossiers admitted form-failure across the 3 nights — this is editorially interesting per Frame Concept v1)

**Not a runtime mechanism per se** — Claudia handles this in prose generation. Just a metadata signal.

---

## 6. Editor pipeline file layout — confirmed per Editor Pipeline v1

```
runtime/flows/
├── editor_flow.py                          Prefect orchestrator
├── editor/
│   ├── __init__.py
│   ├── card_assembly.py                    Claudia's card → editor-step system prompt
│   ├── routing.py                          Stage 1 — theme routing (deterministic, no LLM)
│   ├── dossier_generation.py               Stage 2 — per-dossier Anthropic call
│   └── publish.py                          write to <PROJECT_ROOT>/published_artifacts/dossiers/
├── shared/prompts/
│   └── editor_dossier.md                   closing prompt for Stage 2 (carries the structured-output contract)
```

Claudia's persona card lives at:
```
<PROJECT_ROOT>/editor/claudia_pinchbeck/07_persona_card_assembled.json
```

Per Editor Pipeline v1, separate from `<PROJECT_ROOT>/voices/<slug>/` because Claudia is structurally distinct (editor not panel voice).

---

## 7. Issue numbering scheme — confirmed per Editor Pipeline v1

```
Athens base issue = 42,192

Night 1 (May 7 panel → publishes May 8 morning) = Issue No. 42,193
Night 2 (May 8 panel → publishes May 9 morning) = Issue No. 42,194
Night 3 (May 9 panel → publishes May 10 morning) = Issue No. 42,195
                                                   = the marathon distance in metres
```

Volume: **Vol. CXVI** (year 2026 - confected first issue 1910 = 116 years).

---

## 8. Open questions for runtime to settle

These came up during the persona-construction session but are runtime-side decisions, not persona-side:

### 8.1 Lead-theme decision layer

Lead-vs-grid is a per-night editorial decision: which of the night's engaged themes leads the front page, which go in the grid. **Claudia doesn't make this decision** (would conflict with the per-theme call architecture).

Options:
- (a) Operator chooses lead manually before editor pipeline fires; runtime passes through the choice when assembling front page
- (b) Runtime applies a deterministic rule (e.g., theme with most engaged voices leads; tiebreak by Researcher's theme_quality score)
- (c) A separate small LLM call after all dossiers are generated, ranking them and picking lead

(a) is the simplest and matches Briefing v3's "designer's call whether to include voice rail" sensibility. (b) is mechanical. (c) is heaviest. Recommend (a).

### 8.2 Asterism break encoding

Inline `* * *` in body_paragraphs vs separate index field (see §2). Microsite render preference decides.

### 8.3 Byline split implementation

If Option B (correspondent vs desk byline split, see §3), runtime decides whether `byline` field is generated by Claudia per-call ("By Our Athens Correspondent") or assembled by the runtime from a `byline_form: "correspondent" | "desk"` flag Claudia emits. The first is simpler; the second is more constrained.

### 8.4 Cross-night dossier number reset

Each night starts dossier numbering at 1, or continuous across nights? Per Editor Pipeline v1 the dossier number resets per-issue (Issue 42,193 / Dossier No. 1, 2, 3...). Confirm operator preference.

### 8.5 Per-night summary across themes

Briefing v3 says front page is by theme not by voice. But across N themes, there may be cross-theme observations the desk would want to make (e.g., "all three of the night's themes converged on the question of legitimacy"). Where does this live?
- (a) Doesn't exist — front page just shows the themes; reader makes the connections
- (b) A small "From the desk" standing column on the front page alongside the lead theme
- (c) Folded into the lead-theme article's lede

Recommend (a) for simplicity and per the Briefing v3 "the paper has a front, and you read forward" discipline. (b) is appealing but adds a surface. (c) is risky (overloads the lead article).

### 8.6 Microsite consumption contract

Editor pipeline writes `<PROJECT_ROOT>/published_artifacts/dossiers/night_<N>/dossier_<NNN>.json` per Editor Pipeline v1. Microsite reads and renders. The render contract:
- Per-theme JSON has all the editor pipeline output
- Per-voice render-config bundles (form-markers, palettes, closing seals) live on microsite side, NOT in editor pipeline output
- Microsite reads voice's `artifact_text` from Voice Pipeline Step 2 output via path-fragment reference, NOT embedded in dossier JSON

This is microsite-side concern; flagged here for awareness only.

---

## 9. Cost / wall envelope for editor pipeline (per Editor Pipeline v1, refreshed)

| Stage | Per call | Per night (3-5 dossiers) | Athens 3-night |
|---|---|---|---|
| Stage 1 routing | $0 (Python) | $0 | $0 |
| Stage 2 first dossier (cache write) | ~$0.45–0.50 | — | — |
| Stage 2 subsequent dossiers (cache read) | ~$0.165–0.24 | ~$0.78–1.46 per night | ~$2.34–4.38 |

**Athens 3-night editor pipeline total: ~$3–5.** Confirmed per Editor Pipeline v1.

Wall time per night: ~5–10 min (parallelisable across themes; per-call ~60–90s on Opus 4.7 + thinking).

---

## 10. What runtime needs from voices thread to ship the editor pipeline

1. **Claudia's persona card** at `<PROJECT_ROOT>/editor/claudia_pinchbeck/07_persona_card_assembled.json` — voices thread will produce this via the hybrid pipeline path documented in `voices/CLAUDIA_PINCHBECK_PERSONA_PREP_2026-05-03.md`. Estimated ship date: dependent on operator's Beauty Shot dossier share + ~7–9 hr of focused construction work. Achievable within the Marley DR window if operator shares dossier promptly.

2. **The closing prompt `editor_dossier.md`** — voices thread can draft this alongside the persona card if it helps; OR runtime drafts based on Claudia's card + this memo's input/output contract. Either works.

3. **The structured output schema for the dossier JSON** — runtime decides format (Anthropic structured output schema vs JSON-mode response_format vs prose-and-parse). The shape is per §2 above; the encoding is runtime's call.

---

## 11. Cross-references

- `docs/AI_Assembly_Editor_Pipeline.md` — current Editor Pipeline v1 spec
- `docs/AI_Assembly_Frame_Concept_v1.md` — Frame layer architecture
- `docs/AI_Assembly_Briefing_v3_1.md` — project source of truth
- `~/Desktop/Briefing.html` — Assembly v2 Design Briefing v3 (Matthias second pass) — supersedes Editor Pipeline v1 on dossier shape
- `voices/CLAUDIA_PINCHBECK_PERSONA_PREP_2026-05-03.md` — paired persona-construction state document
- `runtime/OPEN_ITEMS.md` — A2 (editor as 13th member) + B7 (Octopus chromatophore engine, related runtime concern)

---

*End of memo. The persona-construction work continues on the voices side; runtime has what it needs to begin scaffolding `editor_flow.py` against this contract whenever operator decides to start that work.*
