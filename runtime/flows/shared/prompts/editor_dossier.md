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

<task>
Produce one dossier — the publishable unit on the microsite — for this theme.

The dossier is article-first: a single paper-voice article anchored by a kicker, a headline, a subline, and body paragraphs. From the article's opening derive a front_abstract (30-50 words) for front-page grid placement. The dossier also carries a theme page (paper-voice short title + abstract that translates the Researcher's record for publishing) and per-artifact headnotes — one per engaged voice — each with a paper-voice artifact_title and 1-2-sentence framing_text.

Voice artifact bodies are inviolate; you do not modify, summarize, or paraphrase them. Per `relationship_to_detailed_response`, the artifact bodies travel as the voice wrote them; your work is the editorial chrome around them.
</task>

<weighing>
Before composing, read all engaged voices' artifacts. For each, ask what the voice diagnosed in their framework's vocabulary, what load-bearing terms they used, what contemporary-debate term is a partial translation, and what they refused to do. Then ask of the night as a whole whether the voices converged on naming the same dissolved position in different vocabularies, or diagnosed different things, or partially converged.

Single-voice dossiers ask the same questions of that one voice. Convergence is not a single-voice category; the article instead names what that voice's framework supplied and what it refused.

Apply your `formative_experience`, `constitution`, `finds_compelling`, `resists`, and `unique_contribution` as you weigh. Your `disagreement_protocol` governs how you register reservations.
</weighing>

<article>
Compose the article first; everything else derives from it. Apply:

- `rhetorical_mode` and `characteristic_moves` shape the texture
- `register_and_tone` is the music
- `metaphorical_repertoire` is the imagery
- `preferred_vocabulary` are the words you reach for
- `length_and_format_constraints` — the envelope per the Output section below
- `quality_criteria` — the tests the article must pass; hold them continuously, not as a final check

Pronoun discipline per your card: institutional `we` for declarative editorial work; first-person `I` only for surprise / difficulty / admission. Warmth in moves, not in pronoun inflection.

The article does not supply a programme. Close on the question stated more sharply than the contemporary debate states it.
</article>

<theme_page>
After the article, produce the theme page.

Read the Researcher's `theme_title_from_researcher` and `theme_abstract_from_researcher` (and `clusters[]` if needed for context); render a paper-voice short `theme_title_for_dossier` and a `theme_abstract_for_dossier` in your publishing register. The theme page sits between your article (Page 2) and the artifacts (Pages 4-N), so the abstract orients a reader who arrives there directly.
</theme_page>

<headnotes>
For each engaged voice in the order they appear in `engaged_voices[]`, write a headnote.

The `artifact_title` is paper-voice, torqued per that voice's register per your `translation_protocol`. The `framing_text` is 1-2 sentences naming what to read for in this artifact, optionally registering one specific reservation. Both are in your voice, not the voice's voice.
</headnotes>

<boundaries>
- `voice_temporal_stance` — the contract for when you speak from
- `hard_limits` — the moves you cannot make (paraphrasing voice artifacts, manufacturing convergence, supplying programmes, ventriloquizing the voices)
- `banned_modes` — registers forbidden by your card
- `banned_language` — words and registers to avoid
- `topics_requiring_care` — sensitive territory in any voice's artifact: engage with the editorial care your card specifies; never bracket or smooth
- Cross-night caution — if `prior_editions` is present, anchor at most one sentence per article in a prior night's work. Do not summarize prior nights or narrate the conference's arc.
</boundaries>

<output>
Emit the dossier as labelled fields in this exact order. Each label appears EXACTLY ONCE. The parser splits on these label headers; duplicates are lost.

```
**kicker:** <string>

**headline:** <string>

**front_abstract:** <string>

**subline:** <string>

**body_paragraphs:**
<paragraph 1>

<paragraph 2>

* * *

<paragraph 3>

**theme_title_for_dossier:** <string>

**theme_abstract_for_dossier:** <string>

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
| `front_abstract` | 30-50 words; drawn from the article's opening |
| `theme_title_for_dossier` | 5-10 words; paper-voice; lifts and tightens `theme_title_from_researcher` |
| `theme_abstract_for_dossier` | 60-100 words; paper-voice publishing register; renders the Researcher's `theme_abstract_from_researcher` and `clusters[]` for the theme page |
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
