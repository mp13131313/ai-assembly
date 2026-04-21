{# Pass 0b DR prompt wrapper (Phase B decomposition, G.3 complete).
   Includes per-type sub-templates. The monolithic 1086-line version is in
   git history before commit 84cf26f if you need to compare. The shared
   pass_0b_non_human.md was an intermediate splitting step; both the
   organism + system children are now hand-edit surfaces, not generated.
#}
{% include "pass_0b_header.md" %}
{% if type == "human" %}
{% include "pass_0b_human.md" %}
{% elif type == "non_human" and subtype == "system" %}
{% include "pass_0b_non_human_system.md" %}
{% elif type == "non_human" %}
{% include "pass_0b_non_human_organism.md" %}
{% elif type == "fictional" %}
{% include "pass_0b_fictional.md" %}
{% endif %}
{% include "pass_0b_footer.md" %}
