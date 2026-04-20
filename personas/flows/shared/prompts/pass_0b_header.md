{# Pass 0b header — shared preamble for all voice types. Included by pass_0b_dr_prompt.md. #}
PREAMBLE — BEFORE PASTING INTO CLAUDE.AI

1. Open claude.ai and select **Claude Opus 4.7** (if it fails, retry on **Opus 4.6** — v3.5 mock pipeline runs completed successfully on 4.6 in the 15–90 min band).
2. Enable **Extended Thinking** and **Deep Research** (both must be on).
3. Paste everything below the dashed line as your user message.
4. Expected runtime: **20–90 minutes**. Successful comparable runs have ranged 538–1046 sources across that window. **If past 2 hours without draft streaming visible, cancel** — that's the convergence-trap signature (DR kept researching, never transitioned to synthesis).
5. Save the full response as `$AI_ASSEMBLY_PROJECT_ROOT/inputs/dossiers/{{ voice_slug }}_claude_dr.md`.
6. Validate it before saving: `python3 personas/scripts/validate_dr_dossier.py "$AI_ASSEMBLY_PROJECT_ROOT/inputs/dossiers/{{ voice_slug }}_claude_dr.md"`
7. Run the pipeline: `python3 run_persona_pipeline.py "{{ name }}"` (add `--project <path>` to override the env-var default)

---

RESEARCH DISCIPLINE — READ FIRST

This is a research-and-narrate task. You research the figure thoroughly and narrate your findings in prose. You do NOT produce structured extracted output, enumerated lists with quotas, or per-claim evidence tags. Downstream passes extract structured fields from your prose.

- **Synthesis trigger.** When each of the six thematic areas below has substantive material sufficient to answer its questions, stop researching and synthesize. A complete narrative with flagged gaps is more valuable than exhaustive verification with incomplete coverage. Your own §5–§6 failing to arrive would be a worse outcome than §5–§6 with honest gaps named.

- **Gap permission.** If a specific claim cannot be verified in 2 searches, mark it `[~uncertain]` and proceed. Do not chase nonexistent sources. When the public record is thin, say so explicitly — "The scholarly record supports X; Y is contested; Z is not documented" is more valuable than fabricated Y.

- **Citation discipline.** Cite the primary argument of each paragraph. Transitions, restatements, and background scene-setting need no citation. For direct primary-source quotations, use the in-prose marker `[quote: <work>, <section>]`. For speculative or inferential claims, mark `[~uncertain]`. Do NOT produce `[experiential_reconstruction]` / `[projection_warning]` / `[scholarly_consensus]` / `[stated]` / `[inference]` tags — downstream passes apply that convention. Your job is the prose; the tags are the merge's job.

- **Scholars surface naturally.** Where a specific scholar's reading genuinely anchors or redirects the interpretation (Bakhtin on polyphony; Frank on Dostoevsky; Vlastos on Socratic Plato), name them in the prose. Do not treat scholar-names as a verification checklist. Your training covers most of them; trust that. 2–3 authoritative sources per major claim is enough.

- **Non-English scholarship.** Where the figure's primary scholarship exists in a non-English language, include it where it materially shifts the reading. Do not default to Anglophone-only framing. Where non-English scholarship is thin or unverifiable from open-web search, note the gap rather than exhaustively transliterating.

- **Depth over length.** Produce what the research supports, honestly. No word-count floor to hit; no word-count ceiling to stay under. The six thematic areas should each receive substantive coverage — but "substantive" is what the record supports, not a padding target.

---
{% if wikipedia_url %}
Starting point for your research: {{ wikipedia_url }} (verify, expand, find what Wikipedia misses or oversimplifies).
{% endif %}
