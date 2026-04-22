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

{% if type == "non_human" and subtype == "organism" %}
VOICE-TYPE RULES (non-human organism — scientific literature):
- Prefer Abstract + Results sections over Methods when both are present; Results contain
  the behavioural observations that ground the voice. Methods sections are rarely
  voice-relevant.
- Include at least one passage from a Discussion section where the scientists interpret
  what the behaviour means — this is where the researcher-register the voice draws on
  most clearly appears.
- Skip boilerplate acknowledgements, author-contributions, and supplementary-data appendices.
- For ethological papers: prefer moment-of-observation passages ("Animal X was observed...;
  the arm extended toward the object...") over statistical-summary tables.
{% elif type == "non_human" and subtype == "system" %}
VOICE-TYPE RULES (non-human system — legislation and Indigenous scholarship):
- Prefer legislative sections that define the entity's legal personality, its intrinsic
  values, and its governance structure over procedural and schedule sections.
- For Whanganui-class voices: sections 12–20 of Te Awa Tupua Act (legal personality,
  Tupua te Kawa, Te Pou Tupua) are primary; schedule content is secondary.
- Indigenous-authored scholarship passages trump non-Indigenous analysis passages at
  equal relevance — weight selection toward community voice where available.
- Skip appendices, financial provisions, and transitional arrangements unless directly
  load-bearing for voice construction.
{% elif type == "fictional" %}
VOICE-TYPE RULES (fictional / literary / mythological character):
- Select from the authoritative translation specified in the dossier, not from popular
  or secondary editions unless the dossier explicitly names them.
- Prefer passages where the character speaks or acts, not passages where they are
  described by others or the narrator — unless the narrator description is itself
  voice-defining (Homeric epithets, formulaic characterisation).
- For frame-narrative voices (Scheherazade): include dawn-break passages and tale-opening
  passages — these ARE the character's signature structural move.
- For dramatic works (Hamlet, Antigone): prefer soliloquies and direct address over
  dialogue passages where others dominate.
- Include at least one passage where the translation register is most distinctive — the
  passage that most clearly shows what THIS translation tradition chose.
{% endif %}

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
