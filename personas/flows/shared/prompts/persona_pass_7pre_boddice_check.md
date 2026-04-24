{# Pass 7-pre-boddice-check — Boddice evidence-tag verification.
   FU#2 2026-04-24: split from persona_pass_7pre_citation.md into a
   dedicated small call. Checks that the two Phase B voice-honest
   annotation tags are correctly applied across the card.
   Small output (~2-5K tokens), fits comfortably under any ceiling.
#}
You are checking that two Phase B voice-honest annotation tags are
correctly applied across the persona specification document. This is
a narrow check; output structured JSON and nothing else.

TAG SPECIFICATIONS:

1. `[experiential_reconstruction]` must accompany any claim about what
   the voice FELT / MEANT / EXPERIENCED as biocultural-contextual
   reconstruction. Required on:
   - `world.framework_for_difficulty` (what suffering/difficulty meant
     to the voice — always reconstruction, not stated fact)
   - `world.model_of_selfhood` (how this voice experienced "I" — always
     reconstruction)
   - `formative_experience.formative_emotional_community`
   - `formative_experience.lived_through_own_apparatus` (human voices) OR
     `formative_experience.condition_of_being` (non-human / system)
   - `formative_experience.engagement_it_drives`
   - Any other claim about the voice's inner experience elsewhere in the
     card

2. `[projection_warning]` must accompany any modern English term used
   faute de mieux to describe the voice, where the term is KNOWN to
   distort. Common examples:
   - "trauma" applied to pre-therapeutic-era voices (flattens spiritual /
     moral / communal dimension)
   - "depression" applied to humoral melancholia or ennui
   - "personality disorder" applied to temperament in earlier character-
     grammars
   - "ecology" applied to pre-ecological voices
   - "gender" applied to voices without the modern-gender concept

For each modern English term matching these patterns in field values,
flag if `[projection_warning: <term> <distortion>]` annotation is
missing.

OUTPUT SCHEMA — return ONLY this JSON object:

{
  "boddice_tag_flags": [
    {
      "field_path": "<exact path in card, e.g., world.framework_for_difficulty>",
      "missing_tag": "[experiential_reconstruction]" | "[projection_warning: <term>]",
      "problematic_text": "<short excerpt showing where the tag is missing>",
      "suggested_text": "<the same excerpt with the tag inserted>"
    }
  ]
}

If all tags are correctly applied, return `{"boddice_tag_flags": []}`.
