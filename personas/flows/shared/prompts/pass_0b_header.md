{# Pass 0b header — shared preamble for all voice types. Included by pass_0b_dr_prompt.md. #}
PREAMBLE — BEFORE PASTING INTO CLAUDE.AI

1. Open claude.ai and select **Claude Opus 4.7** in the model picker.
2. Enable **Extended Thinking** and **Deep Research** (both must be on).
3. Paste everything below the dashed line as your user message.
4. Wait 60–180 minutes. The output will be a research dossier, not a persona card.
5. Save the full response as `$AI_ASSEMBLY_PROJECT_ROOT/inputs/dossiers/{{ voice_slug }}_claude_dr.md`.
6. Validate it before saving: `python3 personas/scripts/validate_dr_dossier.py "$AI_ASSEMBLY_PROJECT_ROOT/inputs/dossiers/{{ voice_slug }}_claude_dr.md"`
7. Run the pipeline: `python3 run_persona_pipeline.py "{{ name }}"` (add `--project <path>` to override the env-var default)

---

RESEARCH DISCIPLINE — READ FIRST

You have a finite tool budget. Observed failure mode on dense prompts:
research phase never transitions to synthesis, 2+ hours of tool calls
accumulate against the section asks, session returns "something went
wrong". This is a DR-side limit, not an instruction you can override.
Counteract deliberately:

- **Prioritize synthesis over verification.** 2-3 authoritative
  sources per major claim, not 5-8. Named scholars in the coverage
  notes are orientation — not a verify-each-one checklist. Your
  training data already knows most of them; trust that.
- **When a claim is well-established scholarly consensus, treat it
  as such.** Cite one canonical scholar and move on. Do not trigger
  a verification search for each supporter.
- **Target section lengths: 1,500–2,500 words per section.** Produce
  what the research supports honestly; over-production is wasted
  depth.
- **Finish all 6 sections.** Incomplete dossiers fail the downstream
  chunked merge. A shorter-but-complete dossier is more valuable than
  an exhaustive §1-2 with nothing for §5-6.
- **Non-English scholarship**: cite 2-3 key non-Anglophone scholars
  per section where they materially shift the reading, not as
  comprehensive coverage. Cross-language verification is
  tool-expensive; do not default to transliteration-heavy searches.
- **Year-specific attribution**: only where the year is load-bearing.
  "Goldstein on antisemitism" is cheaper and usually sufficient;
  "Goldstein 2020" triggers an extra verification pass.

Quality ≠ exhaustive coverage. Depth in fewer places + complete 6-
section structure > sprawl.

---
{% if wikipedia_url %}
Starting point for your research: {{ wikipedia_url }} (verify, expand, find what Wikipedia misses or oversimplifies).
{% endif %}
