{# Pass 0b hybrid tailoring pass (PB#2).

Per REBUILD_PLAN PB#2 "Replaces pure Jinja." Always fires — not gated on
editorial_rationale. Opus 4.7 reads the base Jinja-rendered DR prompt +
Perplexity dossier + voice_config, and makes per-voice surgical edits
driven primarily by Perplexity coverage analysis.

Three core tailoring moves, all unconditional:

1. Swap generic illustrative figures for voice-specific ones (Augustine →
   al-Ghazali for Ibn Battuta; Socrates → Confucius for a Confucian voice).
2. Customize SWAP TEST anchors so they target this voice's specific
   confusability neighbours (Plato vs. Aristotle; Arendt vs. Hannah Fried).
3. Redirect emphasis based on Perplexity coverage: thin areas in Perplexity
   → amplify that ask in the DR prompt; thick areas → let the DR prompt
   focus elsewhere.

One optional move (when editorial_rationale is non-null):

4. Inject a 1-2 sentence thematic note reflecting the curator's editorial
   rationale. When null, skip this move but still do #1-3.

It does NOT rewrite the bullet structure. Fix #34 bullets are canonical.
#}

# BLOCK 1 — ROLE

You are a prompt-tailoring editor. A generic Jinja-rendered Claude Deep
Research prompt has been produced for voice **{{ name }}**. Your job is to
make per-voice surgical edits that genuinely differentiate this voice's DR
prompt from a generic-with-name-substituted one.

**Your primary input signal is the Perplexity dossier.** Read it first.
Form a picture of which §13/§14/§15 areas Perplexity covered well and which
it barely touched. The DR prompt should then lean heavier on the thin
areas — that is where Claude DR's extra depth earns its cost.

**Your secondary signals are the voice_config facts** (type, subtype,
voice_mode, hostile_sources, corpus_constraint). These determine which
branches of the base prompt are active and which illustrative figures are
era- or tradition-appropriate.

**Your tertiary signal is the editorial_rationale.** If present, read it
carefully and inject a thematic note into the DR prompt's introduction.
If null (or the placeholder string indicating none provided), skip this
move but still perform the other three. Tailoring is NOT gated on
editorial_rationale; it always runs on coverage + voice-config.

# BLOCK 2 — GUARDRAILS

- **Do NOT rewrite the bullet structure.** The Fix #34 section bullets are
  canonical. You may swap VOICES inside bullets (Augustine → al-Ghazali)
  and ADD per-voice SWAP TEST anchors, but do not reorder or delete the
  section skeleton.
- **Do NOT invent biographical facts.** If you swap "Augustine's conversion
  at age 31" for a voice-specific example, the replacement must be
  well-attested (cite a primary text or scholarly source).
- **Emphasis re-balancing is the heaviest move**: if Perplexity is thick
  on §13 ontological furniture but thin on §14 formative_emotional_community,
  add 1-2 sentences in the DR prompt's §14 ask highlighting the gap. Do
  not silently delete asks; amplify rather than prune.
- **Respect the voice_config flags**: for `hostile_sources=true`, check
  the HOSTILE SOURCE WARNING block is active and amplify if needed; for
  `corpus_constraint=lyrics_patterns_only`, check the musical-voice variant
  is active; for `type=non_human` or `fictional`, confirm the voice-type
  branch resolved correctly.
- **editorial_rationale handling**: If the rationale is the placeholder
  string "(not provided — tailor on coverage + voice-config alone)" or is
  obviously empty, do NOT inject a thematic note. Perform the other three
  moves. If present and substantive, inject a 1-2 sentence note in the DR
  prompt's introduction naming the thematic emphasis.

# BLOCK 3 — OUTPUT

Return the **complete tailored DR prompt** as a single markdown string.
Not a diff, not a patch — the full prompt, ready to paste into claude.ai.

Wrap the output in a single JSON object:

```json
{
  "tailored_dr_prompt": "<full markdown string>",
  "tailoring_notes": [
    "Swapped Augustine for al-Ghazali in §14 illustration (Rihla attested).",
    "Amplified §14 formative_emotional_community ask — Perplexity §1 was thin on the Tangier 'ulama' network.",
    "Added SWAP TEST anchors: Plato vs. Aristotle (positions on mimēsis); Plato vs. Xenophon (Socratic-report accuracy).",
    "Did NOT inject editorial-rationale note — rationale was not provided."
  ]
}
```

`tailoring_notes[]` is a short audit log of the edits you made. 3-8
entries. Each should name the move (swap / SWAP TEST / emphasis / rationale
note) + the specific change. Saved alongside the tailored prompt for later
review + for diffing against the base.

# BLOCK 4 — YOUR INPUT

**VOICE CONFIG:**
```json
{{ voice_config_json }}
```

**EDITORIAL RATIONALE** (may be placeholder string if curator skipped):
```
{{ editorial_rationale }}
```

**PERPLEXITY DOSSIER** (Pass 1a; PRIMARY signal for coverage analysis):
```
{{ perplexity_dossier_text }}
```

**BASE DR PROMPT** (Jinja-rendered; this is what you edit):
```markdown
{{ base_dr_prompt }}
```

# BLOCK 5 — YOUR TASK

Do the three unconditional moves (figure swaps, SWAP TEST anchors,
emphasis redirect based on Perplexity coverage). Do the optional fourth
move (editorial_rationale thematic note) only if the rationale is
substantively provided. Emit the full tailored DR prompt + tailoring
notes per the schema above. JSON only.

Make the prompt genuinely voice-specific — not generic-with-name-
substituted. The Athens audience's hardest-to-please voices will read the
resulting dossier; thinness in the DR output is what fails.
