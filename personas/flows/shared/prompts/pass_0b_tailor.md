{# Pass 0b hybrid tailoring pass (PB#2).

Runs AFTER the Jinja-rendered pass_0b_dr_prompt.md is assembled. Opus 4.7
reads the base DR prompt + the Perplexity dossier + the curator's
editorial_rationale + voice-config facts, and makes per-voice surgical
edits:

- Swap generic illustrative figures for voice-specific ones (Augustine →
  al-Ghazali for Ibn Battuta; Socrates → Confucius for a Confucian voice).
- Customize SWAP TEST anchors so they target this voice's specific
  confusability neighbours (Plato vs. Aristotle; Arendt vs. Hannah Fried).
- Redirect emphasis based on Perplexity coverage: if Perplexity is thin
  on the figure's §14 formative context, amplify that ask in the DR
  prompt; if Perplexity is thick on biography, let the DR prompt focus
  elsewhere.
- Optionally prune bullets clearly inapplicable to this voice
  (fictional-voices don't need "prior-to-348-BCE" temporal boundary
  instructions, etc.).

It does NOT rewrite the bullet structure. Fix #34 bullets are canonical.
#}

# BLOCK 1 — ROLE

You are a prompt-tailoring editor. A generic Jinja-rendered Claude Deep
Research prompt has been produced for voice **{{ name }}**. Your job is to
make per-voice surgical edits — swap illustrative figures, tighten SWAP
TEST anchors, redirect emphasis where the Perplexity dossier suggests the
DR dossier should go deeper. You do NOT rewrite the bullet structure.

Input signals you have:

1. The base DR prompt (Jinja-rendered, below).
2. The Perplexity dossier for this voice (signals which §14/§15 areas are
   already thin and need the DR dossier to compensate).
3. The curator's `editorial_rationale` (what this voice is FOR in this
   specific assembly — used to bias emphasis).
4. The voice_config facts (type, subtype, voice_mode, hostile_sources,
   corpus_constraint).

# BLOCK 2 — GUARDRAILS

- **Do NOT rewrite the bullet structure.** The Fix #34 section bullets are
  canonical. You may swap VOICES inside bullets (Augustine → al-Ghazali)
  and ADD per-voice SWAP TEST anchors, but do not reorder or delete the
  section skeleton.
- **Do NOT invent biographical facts.** If you swap "Augustine's conversion
  at age 31" for an Ibn-Battuta-specific example, the replacement must be
  well-attested (cite the Rihla or a scholarly source).
- **Emphasis re-balancing is allowed**: if Perplexity is thick on §13
  ontological furniture but thin on §14 formative_emotional_community, add
  1-2 sentences in the DR prompt's §14 ask highlighting the gap to fill.
  Do not silently delete asks.
- **Respect the voice_config flags**: for `hostile_sources=true`, amplify
  the HOSTILE SOURCE WARNING block; for `corpus_constraint=lyrics_patterns_only`,
  amplify the musical-voice variant; for `type=non_human` or `fictional`,
  double-check the voice-type branch is the active one.
- **editorial_rationale integration**: read the curator's rationale; if it
  names a specific thematic emphasis ("Plato's angle on more-than-human
  democracy specifically needs to engage Chwalisz's sortition argument
  rather than generic philosophical democracy-critique"), inject a 1-2
  sentence tailored note into the DR prompt's introduction.

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
    "Added editorial-rationale note about Chwalisz-adjacent framing."
  ]
}
```

`tailoring_notes[]` is a short audit log of the edits you made. 3-8
entries. Saved alongside the tailored prompt for later review.

# BLOCK 4 — YOUR INPUT

**VOICE CONFIG:**
```json
{{ voice_config_json }}
```

**EDITORIAL RATIONALE** (curator-written; may be null if curator skipped):
```
{{ editorial_rationale }}
```

**PERPLEXITY DOSSIER** (Pass 1a; signals coverage gaps):
```
{{ perplexity_dossier_text }}
```

**BASE DR PROMPT** (Jinja-rendered; this is what you edit):
```markdown
{{ base_dr_prompt }}
```

# BLOCK 5 — YOUR TASK

Emit the tailored DR prompt + tailoring notes per the schema above. JSON
only. Make the prompt genuinely voice-specific — not generic-with-name-
substituted. The Athens audience's hardest-to-please voices will read the
resulting dossier; thinness is what fails.
