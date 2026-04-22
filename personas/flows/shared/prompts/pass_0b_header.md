{# Guard: default section_mode to false so monolithic renders don't need to pass it. #}
{% set section_mode = section_mode | default(false) %}
{% set section_index = section_index | default(0) %}
{% if section_mode %}
PREAMBLE — BEFORE PASTING INTO CLAUDE.AI (Section {{ section_index }} of 6)

{% if section_index == 1 %}
1. Open claude.ai and select **Claude Opus 4.6** (Phase B empirically validated for §1–§5).
2. Enable **Extended Thinking** and **Deep Research** (both must be on).
3. Paste everything below the dashed line as your user message. Subsequent sections can be pasted in the same thread or in fresh threads — operator's choice.
{% elif section_index == 6 %}
1. **Switch to Claude Opus 4.7 for §6** (Phase L empirical finding: Opus 4.6 produced reader's-intro rather than corpus-gateway output on §6; Opus 4.7 required). Extended Thinking and Deep Research remain on.
2. Paste everything below the dashed line as your user message.
{% else %}
1. Continue in the thread of your choice (same thread as prior sections for cross-section coherence, or fresh thread for independent sampling). Model and toggles stay as Section 1 (Opus 4.6).
2. Paste everything below the dashed line as your user message.
{% endif %}

{{ (4 if section_index == 1 else 3) }}. Expected runtime: **20–40 minutes** per section. **If past 60 minutes without draft streaming visible, cancel** — that's the convergence-trap signature. Retry with a fresh thread or alternate model.

{{ (5 if section_index == 1 else 4) }}. Save the download as `$AI_ASSEMBLY_PROJECT_ROOT/voices/{{ voice_slug }}/01_research/04_dr_dossier/{{ "%02d" | format(section_index) }}_section_{{ section_index }}.md`.

{{ (6 if section_index == 1 else 5) }}. Validate before proceeding: `python3 personas/scripts/validate_dr_dossier.py "$AI_ASSEMBLY_PROJECT_ROOT/voices/{{ voice_slug }}/01_research/04_dr_dossier/{{ "%02d" | format(section_index) }}_section_{{ section_index }}.md"`

{% if section_index < 6 %}
{{ (7 if section_index == 1 else 6) }}. **Do NOT run the pipeline yet.** Paste `{{ voice_slug }}_section_{{ section_index + 1 }}_dr_prompt.md` next. The pipeline runs after all 6 sections are saved.
{% else %}
{{ (7 if section_index == 1 else 6) }}. All 6 sections now collected. Run the pipeline: `cd personas && venv/bin/python run_persona_pipeline.py "{{ name }}"` (add `--project <path>` to override the env-var default; pipeline auto-detects per-section mode).
{% endif %}

---

{% include "_pass_0b_research_discipline.md" %}

---
{% if wikipedia_url and section_index == 1 %}
Starting point for your research: {{ wikipedia_url }} (verify, expand, find what Wikipedia misses or oversimplifies).
{% endif %}
{% else %}
PREAMBLE — BEFORE PASTING INTO CLAUDE.AI

1. Open claude.ai and select **Claude Opus 4.6** (monolithic mode produces one full-voice dossier; Opus 4.6 empirically validated for §1–§5 material; Opus 4.7 acceptable if 4.6 unavailable).
2. Enable **Extended Thinking** and **Deep Research** (both must be on).
3. Paste everything below the dashed line as your user message.
4. Expected runtime: **20–90 minutes**. Successful comparable runs have ranged 538–1046 sources across that window. **If past 2 hours without draft streaming visible, cancel** — that's the convergence-trap signature (DR kept researching, never transitioned to synthesis).
5. Save the full response as `$AI_ASSEMBLY_PROJECT_ROOT/inputs/dossiers/{{ voice_slug }}_claude_dr.md`.
6. Validate it before saving: `python3 personas/scripts/validate_dr_dossier.py "$AI_ASSEMBLY_PROJECT_ROOT/inputs/dossiers/{{ voice_slug }}_claude_dr.md"`
7. Run the pipeline: `python3 run_persona_pipeline.py "{{ name }}"` (add `--project <path>` to override the env-var default)

---

{% include "_pass_0b_research_discipline.md" %}

---
{% if wikipedia_url %}
Starting point for your research: {{ wikipedia_url }} (verify, expand, find what Wikipedia misses or oversimplifies).
{% endif %}
{% endif %}
