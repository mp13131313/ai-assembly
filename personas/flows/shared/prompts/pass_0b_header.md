{# Pass 0b header — shared preamble for all voice types. Included by pass_0b_dr_prompt.md. #}
PREAMBLE — BEFORE PASTING INTO CLAUDE.AI

1. Open claude.ai and select **Claude Opus 4.7** in the model picker.
2. Enable **Extended Thinking** and **Deep Research** (both must be on).
3. Paste everything below the dashed line as your user message.
4. Wait 60–180 minutes. The output will be a research dossier, not a persona card.
5. Save the full response as `inputs/dossiers/{{ voice_slug }}_claude_dr.md`.
6. Validate it before saving: `python3 personas/scripts/validate_dr_dossier.py inputs/dossiers/{{ voice_slug }}_claude_dr.md`
7. Run the pipeline: `python3 run_persona_pipeline.py "{{ name }}"`

---
{% if wikipedia_url %}
Starting point for your research: {{ wikipedia_url }} (verify, expand, find what Wikipedia misses or oversimplifies).
{% endif %}
