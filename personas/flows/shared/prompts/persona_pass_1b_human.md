{# Pass 1b — Gemini broad scan, HUMAN voices. Phase B: Boddice-biocultural
   touch. Catches what Perplexity misses; not relied on for factual accuracy. #}
Provide a broad research scan of **{{ name }}**. Target: 3-6K words; depth
over length; do not pad but produce substantive breadth. Your role is
breadth-first discovery — surface what Perplexity under-weights, not
synthetic depth (that is Claude DR's job).

Cover the following, leaning into Gemini's documented strengths
(cross-reference, multilingual indexing, recent reassessments, unusual
passages):

- **History-of-emotions and biocultural-history scholarship** — surface
  Rosenwein (emotional communities), Reddy (emotional regimes), Stearns
  (emotionology), Boddice (biocultural critique) as scholarly-anchor points
  where applicable to the figure's period. Non-English sources prioritised.
  Name scholars; do not synthesize their readings in depth (that is Claude
  DR's job).
- **Non-Anglophone scholarship indexing** — particularly from the figure's
  own language/region tradition (which Perplexity underweights). Name
  scholars + publication pointers in original-language form; Claude DR
  handles interpretation. Prioritize non-Anglophone scholarship as PRIMARY
  rather than supplementary for non-Western figures.
- **Recent scholarly reassessments (2020-2026)** that invert, complicate,
  or reject the dominant reception — surface + brief what-changes framing.
  Cite author + year + key publication.
- **Unusual or surprising primary-text passages** that standard encyclopedic
  accounts tend to skip. Gemini's broad coverage often surfaces passages
  Perplexity's canonical-first search misses.
- **Lineage and affinity connections** across traditions the figure did not
  self-identify with — adjacency-surfacing, not synthesis. Cross-disciplinary
  *connections* (not synthesis — Perplexity handles depth).
- **Period-specific affect / character-grammar** native to the figure's
  world (humours / soul-parts / nafs-stations / virtues-of-the-tradition)
  in original language with short English gloss; do NOT use modern emotion-
  words as primary lexicon for pre-1820 figures.

Do NOT speculate without citation. Every claim needs source title + author.
Flag non-English sources as such; do not translate-paraphrase claims out
of the source language without noting.

{% if hostile_sources %}

HOSTILE-SOURCE HANDLING — {{ name }} has a hostile-sourced record:
Direct Gemini's breadth and multilingual cross-reference strengths at
counter-tradition scholars and minority scholarly readings. Specifically:
- Surface non-Western or minority scholarly traditions that preserve a
  different characterisation of the figure.
- Name multilingual scholarship that reads against the dominant hostile
  record (without synthesizing it — pass names and publication pointers
  for Claude DR to interpret).
- Surface recent counter-tradition reassessments (2020-2026) that reclaim
  or reframe the figure from hostile sources.
Stay in Gemini's breadth lane: surface counter-tradition sources, do not
synthesize them.
{% endif %}
