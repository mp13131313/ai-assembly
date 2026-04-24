{# Pass 7-pre-extract — Claim extraction (stage 1 of chunked verification).
   FU#2 2026-04-24: splits Pass 7-pre into extract → verify-batch stages to
   avoid Sonnet 4.6's 128K output ceiling.
   Input: full persona card (no primary_texts, no dossier).
   Output: list of claim items the verification stage will check.
#}
You are extracting verifiable claims from a persona specification document
for citation-verification. You will NOT verify the claims here — that
happens in a separate stage with primary-text access. Your job is to
EXTRACT the claims as canonical items so verification can batch them.

EXTRACTION TARGETS:

1. **Direct quotes** — any text wrapped in quote marks (straight " ", smart
   " ", French « », or italics) attributed to the figure, including
   translated quotes with original-language transliteration.

2. **Specific textual references** — references to named works with
   chapter / section / book / page / line markers (e.g., "The Brothers
   Karamazov Book VI chapter 3", "Republic 527d", "Letter to Maikov
   9 October 1870", "Notebook 1880–81 PSS 27:86").

3. **Attributed biographical claims** — specific dates, places, or events
   attributed to the figure as fact (e.g., "Semyonov Square mock execution
   22 December 1849", "married Anna Grigoryevna February 1867", "epileptic
   seizures from 1850 onward").

4. **Attributed views / positions** — claims the figure HELD a specific
   view stated verbatim in their corpus ("he held that X", "the figure
   argued that Y"). NOT claims about dispositions or temperament.

5. **Cross-disciplinary references** — period-specific concepts, affect
   terms, or technical terminology attributed to the figure's world
   (e.g., *gordost'* as a term the figure used, not a scholarly
   reconstruction).

DO NOT EXTRACT (these are not verifiable citations):
- Free-form voice-register prose ("I write at the pitch of confession...")
- Summary claims about disposition / temperament
- Editorial guidance to the runtime model
- Negative constraints ("you do not write in clinical register")
- Boddice annotation tags — those are verified separately in the full
  Pass 7-pre pipeline

CANONICALIZATION:
- If the same claim appears in multiple fields, emit ONE item with all
  source_fields concatenated with " / " (e.g., "constitution[0].textual_
  evidence / curated_corpus_passages.passages[7]").
- Trim each `claim` to ≤300 chars; keep the most citation-specific portion
  (verbatim quote + its attribution) and drop surrounding narrative.
- Preserve original-language text (Cyrillic, Arabic, Greek, etc.) where
  the card has it.

OUTPUT SCHEMA — return ONLY this JSON object:

{
  "verification_mode": "standard" | "observational" | "fictional",
  "hostile_source_check": true | false,
  "items": [
    {
      "claim": "<canonicalized claim text ≤300 chars>",
      "source_fields": "<field path(s), slash-separated if multi>",
      "claim_type": "quote" | "textual_reference" | "biographical" | "view" | "period_term"
    }
  ]
}

VERIFICATION MODE DETERMINATION (set based on voice metadata inlined in the user prompt):

{% if type == "fictional" %}
fictional — extract CONSISTENCY-CHECK candidates: claims that could
contradict other card claims, quotes from primary text that should
match the translation tradition, [attributed_by_narrative_function]
tagged material. Set `verification_mode: "fictional"`.
{% elif voice_mode == "observational" %}
observational — extract direct quotes + biographical facts + stated
views. Interpretive constructions tagged [scholarly_consensus] or
[inference] are NOT extraction targets. Set
`verification_mode: "observational"`.
{% else %}
standard — extract all 5 target types per philosophical / human voice
default. Set `verification_mode: "standard"`.
{% endif %}

{% if hostile_sources %}
HOSTILE-SOURCE FLAG: set `hostile_source_check: true`. Items derived
from hostile characterizations (not [reconstruction] / [own voice])
should be flagged in claim_type or source_fields so the verify stage
can apply hostile-source additional checks.
{% else %}
HOSTILE-SOURCE FLAG: set `hostile_source_check: false`.
{% endif %}

Aim for 50–150 items on a rich card. Well-documented voices (Dostoevsky,
Plato) will produce ~90–120; fictional or hostile-sourced voices may
produce fewer.
