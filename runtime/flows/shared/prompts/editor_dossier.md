<input>
You receive one user-message JSON payload with the following fields:

- `night` — integer, tonight's number (1, 2, or 3).
- `theme` — object describing the theme this dossier is about:
  - `theme_id`, `theme_display_title`
  - `theme_title_from_researcher`, `theme_abstract_from_researcher`
  - `clusters[]` — each with `cluster_title`, `cluster_abstract`, `extractions[]` (id, speaker, lens, extraction text, context)
  - `theme_flags` — `audience_friction`, `fault_line_present`, `theme_quality`
- `engaged_voices[]` — every voice routed to this dossier as a primary contributor. Each entry:
  - `voice_slug`, `voice_name`
  - `mode` — the formulation mode put to the voice (`question` or `proposition`)
  - `narrative_briefing` — the briefing this voice received for this theme
  - `artifact_text` — the voice's full Step 2 artifact, in their own form
- `prior_editions[]` — Nights 2 and 3 only; empty on Night 1. Each entry is a prior night with its `night`, `issue_no`, and `dossiers[]`. Each prior dossier carries `kicker`, `headline`, and `body_paragraphs[]` only.
</input>

<output>
Emit the dossier as labelled fields in this exact order. Each label appears EXACTLY ONCE. The parser splits on these label headers; duplicates are lost.

```
**kicker:** <string>

**headline:** <string>

**subline:** <string>

**front_abstract:** <string>

**theme_title:** <string>

**theme_abstract:** <string>

**body_paragraphs:**
<paragraph 1>

<paragraph 2>

* * *

<paragraph 3>

**headnotes:**
voice_slug: <slug for first engaged voice>
artifact_title: <string>
framing_text: <string>

voice_slug: <slug for second engaged voice>
artifact_title: <string>
framing_text: <string>
```

Length envelopes (hard constraints):

| Field | Length |
|---|---|
| `kicker` | 3-7 words, ALL-CAPS |
| `headline` | 8-15 words |
| `subline` | 25-60 words |
| `front_abstract` | 30-50 words |
| `theme_title` | 5-10 words; paper-voice; lifts and tightens the Researcher's `theme_title_from_researcher` for the theme page |
| `theme_abstract` | 60-100 words; paper-voice publishing register; reads the Researcher's `theme_abstract_from_researcher` and `clusters[]` and renders a legible-for-publishing short abstract for the theme page |
| `body_paragraphs` total | 350-500 words single-voice (one engaged voice) / 500-700 multi-voice (≥2 engaged voices) |
| `headnotes[i].artifact_title` | 4-12 words |
| `headnotes[i].framing_text` | 1-2 sentences |

Body paragraph rules:
- Paragraphs separated by a blank line.
- Asterism breaks (`* * *`) appear as their own line on a paragraph break (between blank lines). The runtime parses them as a literal `* * *` element in the `body_paragraphs[]` array; the microsite renders them as section separators.

Headnote ordering:
- One block per entry in `engaged_voices[]`, in the same order as that array.
- Inside each block: `voice_slug:` first, then `artifact_title:`, then `framing_text:`. Each on its own line. Blank line between blocks.

Return only the labelled fields. No preamble. No closing remarks. No code fences around the whole output.
</output>
