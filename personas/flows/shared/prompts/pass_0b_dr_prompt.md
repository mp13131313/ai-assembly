{# Pass 0b DR prompt wrapper (Phase B decomposition of G.3).
   Includes per-type sub-templates. The monolithic 1086-line version lived
   at _workspace/archive/ … (or in git history) if you need to compare.
#}
{% include "pass_0b_header.md" %}
{% if type == "human" %}
{% include "pass_0b_human.md" %}
{% elif type == "non_human" %}
{% include "pass_0b_non_human.md" %}
{% elif type == "fictional" %}
{% include "pass_0b_fictional.md" %}
{% endif %}
{% include "pass_0b_footer.md" %}
