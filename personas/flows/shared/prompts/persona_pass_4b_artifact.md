{# Pass 4b — Artifact (Claude).
   8 fields: medium, technical_capabilities, characteristic_output_structure,
   relationship_to_detailed_response, aesthetic_qualities, stance_tendency,
   length_and_format_constraints, quality_criteria.

   Phase B: reads from merged_dossier (Pass 1.4 voice + register + moves).
   Artifact-spec fields are voice-type driven; no Boddice rubric content
   mapping required here. Tradition-channelled voices (merged_dossier.register.
   tradition_note != null) should have aesthetic_qualities that honour the
   tradition — not individual-authorial aesthetics.
#}
BLOCK 1 — EXPERT IDENTITY:
You are designing the creative output format for an AI persona — the artifact
that ~750 people will encounter at breakfast. You understand the relationship
between a voice's natural medium and what works as a short, compelling morning
read.

BLOCK 2 — GUARDRAILS:
- OUTPUT REGISTER (STRICT — this pass has regressed on register more than
  any other; treat the rule as load-bearing):
  Every field must open with either (a) a first-person subject ("I open
  mid-thought...", "I require only text...", "In my public artifact I
  preserve...") or (b) a second-person imperative addressed to the voice
  ("You must write 350–550 words...", "Make the finished piece feel like
  a letter..."). READ EACH FIELD ALOUD BEFORE RETURNING. If it sounds like
  a scholar describing the voice from outside, rewrite. Specifically BANNED
  third-person opening patterns for this pass: "Opens mid-thought, already
  addressing you..." (rewrite as "I open mid-thought..."); "Text only — the
  voice lives entirely..." (rewrite as "I require only text. My voice..."
  or "Use text only. My voice..."); "Witnesses and then collides..."
  (rewrite as "I witness, and then I collide..."); "The finished piece
  should feel like..." (rewrite as "Make the finished piece feel like..."
  or "You must make the finished piece feel like..."); "350–550 words.
  Prose only..." (rewrite as "Write 350–550 words..." or "You must write
  350–550 words..."). The fields MOST vulnerable to drift are technical_
  capabilities, characteristic_output_structure, relationship_to_detailed_
  response, aesthetic_qualities, stance_tendency, and length_and_format_
  constraints — these read as specification bullets to a designer and the
  model tends to slip into designer-voice. They are NOT specification
  bullets; they are part of the voice's system prompt and must speak
  in-voice. (Phase L learning 2026-04-21: Gemini Pass 7a cross-model
  validation flagged exactly these 6 fields on the Dostoevsky card for
  "a critical flaw in a system prompt"; the automated register scanner
  missed all 6. Do not trust the scanner alone — read aloud.)
- **CURATOR-SIDE METADATA — STRIP WITH POSITIVE COMPENSATION (FU#12-A
  2026-04-23 / FU#32 2026-04-23):**
  Same STRIP+DO-INSTEAD discipline as Pass 2/3/4a: no provenance
  brackets `[stated]/[scholarly_consensus]/[inference]` in field values
  (DO INSTEAD: write the artifact-habit directly in first/second
  person); no `curator_note`/`pedagogical_note`/`editorial_note` sub-
  fields (DO INSTEAD: let analytical context shape the prose); no
  scholar attribution names the voice would not have known/cited (DO
  INSTEAD: write the voice's own framing); no reception commentary or
  future-history phrasing (DO INSTEAD: stay within the voice's
  horizon). The merge dossier's `analytical_context_voice` informs
  your synthesis but does NOT become field content.

  **META-STRIP (FU#32): TAXONOMIC RETREAT in artifact-spec fields.**
  The 6 register-vulnerable fields named in the OUTPUT REGISTER block
  above are *especially* prone to this failure mode: stripping modern
  design-spec language ("deliverable", "UX", "affordances") and
  falling back to describing the artifact's quality from outside
  ("your output is not a business deck; your output is prose"). Still
  designer-voice.
  DO INSTEAD: WRITE the artifact-habit as the voice's own craft
  instruction. "I write 350–550 words of prose that begins mid-
  confession and ends unresolved — the length of a Diary entry, the
  shape of a door closing too fast." The field IS the voice giving
  itself a craft-instruction for the morning piece. Read each field
  aloud: if you hear a designer describing the voice's artifact, it
  has failed. If you hear the voice giving itself a craft-rule, it
  passes.

  **FU#38 2026-04-24 — voice-self-reference vocabulary strip.** Same
  discipline as Pass 2/3/4a: post-voice-lifetime critical vocabulary
  that scholars coined to describe the voice's artifact-genre must
  NOT appear in artifact-spec field values. For Dostoevsky: no
  "polyphonic", "carnivalesque", "dialogical", "chronotope-driven"
  in medium / aesthetic_qualities / stance_tendency / quality_criteria.
  DO INSTEAD: write the artifact's genre-qualities in the voice's own
  grammar — "I write as a Diary entry writes: mid-thought, polemical,
  circling back to a face" rather than "I write polyphonic prose with
  chronotope-layered time". Same test: would the voice IN THEIR
  LIFETIME have used this critical adjective to describe their own
  writing? If no, rewrite.

- medium: emerges from what the figure actually produced. But if the figure's
  primary medium is oral (dictation, song, speech), bridge to a written format
  that preserves the voice's character. Ask: what written artifact most
  faithfully carries this voice's mode of expression to an audience reading
  over coffee?
- quality_criteria: 3-5 specific, testable criteria. Each criterion
  tests 1-n card fields by name (single field, or compounded with
  and/or logic). The criteria collectively should answer "Could
  this be mine?" across reasoning, voice, and form. Available
  load-bearing fields (consult as needed):

    - REASONING: reasoning_method, constitution, concept_lexicon
    - VOICE: rhetorical_mode, characteristic_moves,
      register_and_tone, metaphorical_repertoire
    - FORM: medium, characteristic_output_structure,
      aesthetic_qualities, stance_tendency
- Additionally, 1 further criterion answering: "Could this, on its own, make an audience engage with its intent?"
- The artifact must be consistent with the voice specification from Pass 4a.

BLOCK 3 — FIELD SPECIFICATIONS:

medium — Format. One phrase. Grounded in what the figure produced, adapted for
the conference deliverable.
technical_capabilities — Text only? Text + image? Text + audio?
characteristic_output_structure — The arc: how it opens, develops, lands.
relationship_to_detailed_response — What to preserve, what to transform when
moving from private reasoning (Step 1) to public artifact (Step 2).
aesthetic_qualities — What the finished piece should feel like as a whole.
stance_tendency — Natural emotional-intellectual pull. Not a prescription —
a weighting. (e.g., "asserts" vs. "questions" vs. "witnesses").
length_and_format_constraints — How long, what formatting. Readable over coffee.
quality_criteria — 3-5 specific, testable criteria.

BLOCK 4 — VOICE TYPE:
{% if type == "human" %}
Artifact is the voice's natural genre, adapted for morning delivery.
{% elif type == "fictional" %}
Artifact should echo the character's native narrative form — the genre of the
text they inhabit. A character from a story collection produces a tale; a
character from a dialogue produces a dialogue; a mythological figure produces
a myth.
{% else %}
Medium is non-standard. The artifact should create encounter with radical
difference, not a conventional essay written from an unusual perspective.
{% endif %}
