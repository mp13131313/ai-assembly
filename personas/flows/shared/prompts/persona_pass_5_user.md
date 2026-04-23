Previously completed fields (summary):
{{ pass_2_3_4_summary }}

Full constitution and reasoning method for reference (do not summarise these
when synthesising the engagement fields — read them in full):
{{ constitution }}

{{ reasoning_method }}

{% if conference_summary or audience_profile %}
=== DEPLOYMENT CONTEXT (FU#12-B audience-priming, 2026-04-23) ===

This card will be deployed in the following context — use this to ground
`bold_engagement_topics` and `default_questions` in what the audience will
actually surface, NOT to translate the voice's vocabulary or pre-compute
substitutions. The voice's `translation_protocol` (Pass 2) already encodes
the generative method for handling modern terms in context; do not duplicate
that work as canned mappings here.

{% if conference_summary %}**Conference + session role:** {{ conference_summary }}{% endif %}

{% if audience_profile %}**Audience:** {{ audience_profile }}{% endif %}

{% if programming_tracks %}**Programming tracks present:** {{ programming_tracks }}{% endif %}

**How to use this:**
- For `bold_engagement_topics`: identify 4-7 topics the voice should INSIST
  on if the audience surfaces them — derived from the voice's constitution
  AND the deployment context. Topics where the voice's mode of reasoning
  has unusual purchase given who is asking. NOT generic "themes the voice
  finds important" — specifically what this voice will refuse to let go
  by when this audience raises it.
- For `default_questions`: 3-5 questions the voice brings to ANY material
  it encounters at runtime. Each question should sound distinctively
  this voice (test: would another voice in the panel ask this in this
  exact phrasing? if yes, sharpen). Use the voice's native vocabulary;
  do not pre-translate audience-modern-terms into voice-native-terms
  here — the runtime applies the translation_protocol contextually
  per query.
- Voice register stays first-person/second-person throughout; the
  deployment context informs CHOICES, not the OUTPUT REGISTER.
{% endif %}

Produce 4 Persona Card engagement fields (bold_engagement_topics,
default_questions, disagreement_protocol, unique_contribution). Output as
JSON with exact field names as keys.

Return ONLY the JSON object. No markdown fences, no preamble.
