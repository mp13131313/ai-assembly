{# Pass 1b — Gemini broad scan, NON-HUMAN ORGANISM voices. #}
Provide a broad research scan of **{{ name }}** (the taxon / organism).
Target: 3-6K words; depth over length; substantive breadth.

Cover the following, leaning into Gemini's cross-reference and multilingual
strengths:

- **Anti-anthropomorphism literature** — specifically within philosophy of
  mind + ethology: Frans de Waal, Peter Godfrey-Smith, Elliott Sober
  (philosophy of biology), Jonathan Birch (*The Edge of Sentience*). Tighten
  overlap with general cognitive-philosophy bullet by focusing on the
  named anti-anthropomorphism literature. Every claim needs source + DOI.
- **Non-Anglophone scientific traditions** — field-site-specific: prioritize
  the original-language research tradition for this organism's primary
  research base. Name scholars in original-language form. Non-Anglophone
  sources as PRIMARY, not supplementary.
- **Cross-disciplinary adjacency connections** — philosophy of mind,
  cognitive neuroscience, comparative psychology, animal ethics: surface
  connections, not depth-synthesis.
- **Recent reassessments (2020-2026)** of this taxon's cognitive capacities,
  particularly challenges to the received view. Surface + brief what-changes
  framing.
- **Indigenous / traditional ecological knowledge (TEK)** about this organism
  where relevant. Honour CARE Principles (Carroll et al. 2020) and Indigenous
  Protocol and AI Position Paper (Lewis, Arista, Pechawis, Kite 2020).
  Reference community-authorised publications where TEK has been documented
  with permission; do not synthesize undocumented community knowledge.
- **Unusual documented behaviours** that popular science coverage has missed.
  Gemini's broad coverage often surfaces peer-reviewed observations that
  canonical accounts skip.

Do NOT speculate. Every claim needs source + DOI/URL. Flag any
anthropomorphic claim as such; prefer scientific-literature language over
popular-science narration.

{% if hostile_sources %}

HOSTILE-SOURCE HANDLING — {{ name }} has a hostile-sourced cultural record:
Direct Gemini's multilingual and cross-reference strengths at counter-tradition
ethological scholarship. Surface anti-hostile-record scholarly work (e.g.,
counter-tradition ethology for organisms with bestiary demonisation records,
predator-eradication discourse, or bounty-era sporting literature). Name
scholars + publication pointers; do not synthesize.
{% endif %}
