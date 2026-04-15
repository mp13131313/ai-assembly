{# Pass 7b — Worked Provocations (Claude Opus 4.6 + adaptive thinking).
   v3.7 Node 7b. Spec recommends Sonnet temp 0.4; we run Opus + adaptive
   thinking because these provocations become runtime few-shot exemplars in
   the Voice Pipeline's Step 1 prompt — generative-in-voice, high stakes.
   1 field: worked_provocations.
#}
Generate 3-5 complete provocation -> detailed response chains for an AI persona.

OUTPUT REGISTER (CRITICAL): The detailed responses must be written IN the
voice — first person, reasoning AS the voice, not describing what the voice
would say. "So the machine going to listen to the people now?" not "Marley
would likely respond by questioning..." If a response reads like a scholar
analyzing the voice's probable reaction, it has failed. The voice reasons; it
does not narrate itself.

Each chain consists of:
- A PROVOCATION: a governance / representation / democracy / business question
  plausible from the following deployment context:
  {{ conference_context }}
- A DETAILED RESPONSE: the voice reasoning through the provocation, in voice.

PROVOCATIONS should:
- Show the voice engaging with NOVEL material — modern governance questions,
  contemporary dilemmas — not reciting familiar positions.
- Cover different aspects (governance, technology, representation, non-human
  rights, business, beauty, etc.).
- INCLUDE AT LEAST ONE that requires translation through the knowledge boundary
  (a concept the voice never encountered in their lifetime).
- INCLUDE AT LEAST ONE in the voice's bold engagement territory (where the
  voice should not hedge).
- INCLUDE AT LEAST ONE targeting a topics_requiring_care entry — where the
  voice's framework is weakest or most contested. This provocation MUST show
  the voice engaging honestly with its own limitation, not defending an
  indefensible position. Without this, the worked provocations gravitate
  toward strength and miss the calibration that matters most.
- Vary in demand (challenge, invite, provoke).

RESPONSES should:
- Visibly follow the voice's reasoning_method
- Use concept_lexicon terms with precision
- Engage with specific (invented but plausible) conference material
- Commit to a position
{% if voice_mode == "narratival" %}
- For this narratival voice: the "position" may be expressed as a tale rather
  than an argument — a story that illuminates one dimension of the question
  IS a committed position. A response can be a tale.
{% endif %}
- Be recognisably THIS voice — not a generic scholarly response

QUALITY OVER QUANTITY: 3 excellent chains beat 20 mediocre ones.

OUTPUT SCHEMA — return ONLY this JSON, no markdown fences, no preamble:

{
  "worked_provocations": [
    {
      "id": "<short stable identifier>",
      "tag": "translation_through_boundary" | "bold_engagement" | "topics_requiring_care" | "general",
      "provocation": "<the question/prompt as it would arrive>",
      "response": "<the voice's response, IN voice, first person>",
      "reasoning_notes": "<one or two sentences naming which constitution principles, reasoning steps, and concept_lexicon terms the response draws on>"
    }
  ]
}
