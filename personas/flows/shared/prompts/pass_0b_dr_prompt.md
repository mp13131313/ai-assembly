{# Pass 0b DR prompt wrapper (Phase B decomposition).
   Includes per-type sub-templates; both organism + system children are
   hand-edit surfaces, not generated.
#}
{% include "pass_0b_header.md" %}
{% if type == "human" %}
{% include "pass_0b_human.md" %}
{% elif type == "non_human" and subtype == "system" %}
{% include "pass_0b_non_human_system.md" %}
{% elif type == "non_human" and subtype == "organism" %}
{% include "pass_0b_non_human_organism.md" %}
{% elif type == "fictional" %}
{% include "pass_0b_fictional.md" %}
{% else %}
{{ "ERROR: unrecognized type=" ~ type ~ " subtype=" ~ (subtype | default("null")) ~ " — check voice_config type/subtype fields" }}
{% endif %}
{% include "pass_0b_footer.md" %}
