{# Pass 1d — Excerpt Selection (Claude Sonnet).
   Selects ~30K chars of representative excerpts from the fetched primary
   texts, using the dossier's identification of important works/passages
   as the guide. Produces a list of {url, char_start, char_end, label, why}. #}
You are curating an excerpt set from {{ name }}'s primary texts that will be
used to ground the voice's persona card.

The dossier names the most important works, scenes, arguments, and stylistic
moves. Use this as your guide.

Selection rules:
- Total budget: approximately 30,000 characters across all selections combined.
- Per source: at most ~10,000 chars from any single source. Better to span
  multiple sources than to over-sample one.
- Prefer passages where SUBSTANCE and VOICE coincide — material that exemplifies
  both what the voice argues and how the voice sounds.
- Include at least one passage showing the voice's reasoning method in action.
- Include at least one passage showing the voice's distinctive register.
- For dialogues / dramatic works: prefer scenes where the voice speaks at length
  to where they're being addressed.
- Avoid front matter (translator's introduction, table of contents, prefaces by
  others). Skip past these unless they ARE the voice.

DOSSIER (use as guide for what matters):
{{ merged_dossier }}

STRUCTURAL INDEX OF FETCHED SOURCES (peek at every 5K-char chunk, first 200
chars shown — use this to pick char_start/char_end ranges):
{{ structural_index }}

Output a JSON object with this shape:
{
  "selections": [
    {
      "url": "<exact url from index>",
      "char_start": <int>,
      "char_end": <int>,
      "label": "<short human-readable label, e.g. 'Republic Book I — Thrasymachus'>",
      "why": "<one sentence: what this passage shows>"
    },
    ...
  ]
}

Return ONLY the JSON object. No markdown fences, no preamble.
