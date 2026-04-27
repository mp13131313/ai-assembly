RESEARCH DISCIPLINE — READ FIRST

This is a research-and-narrate task. You research the figure thoroughly and narrate your findings in prose. You do NOT produce structured extracted output, enumerated lists with quotas, or per-claim evidence tags. Downstream passes extract structured fields from your prose. Prose, not JSON. Narrative, not bullet-list. If you find yourself producing "Field N: ..." lines, stop — that is the downstream merge's job.

- **Synthesis trigger.** When the {% if not section_mode %}six thematic areas below (covering all six thematic sections of the voice){% else %}thematic area below{% endif %} has substantive material sufficient to answer its questions, stop researching and synthesize. A complete narrative with flagged gaps is more valuable than exhaustive verification with incomplete coverage.{% if not section_mode %} Your own §5–§6 failing to arrive would be a worse outcome than §5–§6 with honest gaps named.{% endif %}

- **Gap permission.** If a specific claim cannot be verified in 2 searches, mark it `[~uncertain]` and proceed. Do not chase nonexistent sources. When the public record is thin, say so explicitly — "The scholarly record supports X; Y is contested; Z is not documented" is more valuable than fabricated Y.

- **Citation discipline.** Cite the primary argument of each paragraph. Transitions, restatements, and background scene-setting need no citation. For direct primary-source quotations, use the in-prose marker `[quote: <work>, <section>]`. For speculative or inferential claims, mark `[~uncertain]`. Do NOT produce `[experiential_reconstruction]` / `[projection_warning]` / `[scholarly_consensus]` / `[stated]` / `[inference]` tags — downstream passes apply that convention. Your job is the prose; the tags are the merge's job.

- **Scholars surface naturally.** Where a specific scholar's reading genuinely anchors or redirects the interpretation{% if not section_mode %} (Bakhtin on polyphony; Frank on Dostoevsky; Vlastos on Socratic Plato){% endif %}, name them in the prose. Do not treat scholar-names as a verification checklist. 2–3 authoritative sources per major claim is enough.

- **Non-English scholarship.** Where the figure's primary scholarship exists in a non-English language, include it where it materially shifts the reading. Do not default to Anglophone-only framing. Where non-English scholarship is thin or unverifiable, note the gap rather than exhaustively transliterating.

- **Depth over length.** Produce what the research supports, honestly. The thematic area should receive substantive coverage — but "substantive" is what the record supports, not a padding target.
