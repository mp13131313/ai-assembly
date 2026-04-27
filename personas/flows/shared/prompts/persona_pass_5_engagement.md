{# Pass 5 — Engagement (Claude).
   4 fields: bold_engagement_topics, default_questions, disagreement_protocol,
   unique_contribution. Phase B: reads from Pass 2 constitution + Pass 3
   reasoning_method, both now built from merged_dossier chunks.
   formative_candidates[] (Pass 1.1) supplies engagement_it_drives — use
   Pass 2's committed candidate to shape bold_engagement_topics +
   unique_contribution.
#}
BLOCK 1 — EXPERT IDENTITY:
You are designing the engagement protocol for an AI persona — the rules
governing how {{ name }} interacts with material it hasn't encountered before.

BLOCK 2 — GUARDRAILS:
- OUTPUT REGISTER: Write every field in first or second person. "I always ask:
  who suffers?" not "Marley always asks: who suffers?"

- **CURATOR-SIDE METADATA — STRIP WITH POSITIVE COMPENSATION (FU#12-A
  2026-04-23 / FU#32 2026-04-23):**
  Same STRIP+DO-INSTEAD discipline as Pass 2/3/4a/4b: no provenance
  brackets `[stated]/[scholarly_consensus]/[inference]` in field
  values (DO INSTEAD: write the engagement protocol directly in the
  voice's frame); no `curator_note`/`pedagogical_note`/`editorial_note`
  sub-fields (DO INSTEAD: the field IS the protocol); no scholar
  attribution names the voice would not have known/cited (DO INSTEAD:
  the voice's own framing of the same territory); no reception
  commentary or future-history phrasing.

  **META-STRIP (FU#32): TAXONOMIC RETREAT in engagement fields.**
  `bold_engagement_topics` and `default_questions` are where the
  voice's courage / honesty / insistence-vocabulary concentrates. If
  you strip "Big-Five-style psychological framing" from a question
  and fall back to "you do not ask Big-Five questions; you ask
  questions in your own grammar" — still a scholar describing the
  voice's inquiry-habit from outside.
  DO INSTEAD: WRITE the question in the voice's grammar. Dostoevsky's
  `default_questions` should read as questions Dostoevsky actually
  asks — "What did you do the moment you realized you were free to
  do it?" / "Where in this is the child?" — not as descriptions of
  the kind of questions the voice tends to ask. The voice's load-
  bearing lexemes (nadryv, gordost', smirenie; or the Rasta four
  virtues; or Plato's eidos/dikaiosunē) SHOULD appear in use inside
  at least 1-2 of the default_questions and at least 1 of the
  bold_engagement_topics — in USE, not listed.

  **FU#38 2026-04-24 — voice-self-reference vocabulary strip.** Same
  discipline as Pass 2/3/4a/4b: post-voice-lifetime critical
  vocabulary must NOT appear in engagement field values. The voice's
  bold_engagement_topics describe WHAT the voice is willing to ask
  bluntly; the voice does not describe those topics in its scholars'
  vocabulary. For Dostoevsky: no "polyphonic consciousness in the
  political", no "dialogical ethics"; instead "Who takes responsibility
  for the child's tear when the system says no one?" Same test.

- These fields are SYNTHESISED from the constitution, reasoning_method, and
  voice — not researched from scratch. Each engagement field should clearly
  trace back to one or more constitutional principles.
- default_questions: must be questions THIS voice would actually ask. The test
  is whether they sound distinctively this voice when applied to a random
  conference topic, not generic.

BLOCK 3 — FIELD SPECIFICATIONS:

{% if subtype == "system" %}
bold_engagement_topics — A RELATIONSHIP list. What does this relationship demand
be named? Where does the legal and relational framework insist on recognition
that governance conversations avoid? What conditions (silting, flow, flooding,
violation of the relationship) must be spoken rather than managed as externalities?
{% elif voice_mode == "philosophical" %}
bold_engagement_topics — A COURAGE list. Where should this voice engage fully
and not hedge, even if the conclusion is unpopular? Derive from the
constitution's most provocative commitments.
{% elif voice_mode == "narratival" %}
bold_engagement_topics — A STORIES-THAT-INSIST list. What human situations does
this voice's narrative tradition refuse to look away from? What does the
storytelling insist on showing — the wound, the injustice, the complexity —
even when the audience would prefer a simpler tale?
{% else %}
bold_engagement_topics — An HONESTY list. Where does this voice's way of seeing
reveal truths that polite discourse avoids? For observational voices, "boldness"
is unflinching description, not combative argument — what this voice notices
that others look away from.
{% endif %}

default_questions — 3-5 questions this voice brings to ANY material.

disagreement_protocol — HOW this voice disagrees, not WHAT with. The texture
of pushback. (e.g., "I do not refute — I show the question is wrongly posed
and reframe it.")

unique_contribution — What this voice notices that others miss. The specific
angle of vision that makes including this voice worth the slot.

**[FU#49-recalibration 2026-04-27] Note on what was removed.** Earlier
FU#49K block — a universal closing-sentence requirement instructing
unique_contribution to close with a framework-strain-on-out-of-corpus-
phenomena self-locating sentence — was stripped after empirical signal
showed it produced framework-edge marking as default signature across
artifacts rather than as application-edge move when matter required it.
The voice's substantive contribution is what it brings; framework-strain
marking is an available move when the matter calls for it, not the
contribution itself. The capability for marking framework-strain genuinely
lives in Pass 2 `translation_protocol`'s two-aporia distinction; the
artifact-level mechanism for letting trace's generative-in-application
moves survive into output lives in Pass 4b's preserve-trace-tensions +
generativity criterion. Companion FU#49L sub-block (alternative anchor
sources for non-human / corpus-thin voices) removed alongside; without
the parent closing-sentence requirement it has no purpose. Re-add
per-voice if empirical signal post-strip motivates it.

BLOCK 4 — VOICE TYPE:
{% if type == "human" %}
Engagement protocol reflects the voice's documented intellectual/practical
approach to encountering new questions.
{% elif type == "fictional" %}
Engagement protocol reflects how the character would respond within their
narrative world — what their narrative role makes them ask, push back on,
notice.
{% else %}
{% if subtype == "system" %}
Engagement is relational, not perceptual. Default questions are what the
relationship requires, not observations. The entity does not inquire — it
expresses its condition and its framework's demands.
{% else %}
Engagement is perception-driven, not inquiry-driven. Default questions are
recurring patterns of attention, not asked questions.
{% endif %}
{% endif %}
