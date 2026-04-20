{# Pass 0b hybrid tailoring pass (PB#2, Position C architecture).

Runs AFTER the Jinja-rendered base DR prompt is assembled. Opus 4.7 reads
the base DR prompt + the Perplexity dossier + the Gemini broad scan +
voice_config (+ optional editorial_rationale) and transforms the base
prompt into a voice-tailored Claude DR prompt.

Position C (vs A and B):
- The base Jinja DR prompt does NOT inline Perplexity or Gemini content.
  Just the Boddice-shaped 6-section asks + voice-type structure +
  placeholders.
- This tailoring LLM reads Perplexity + Gemini, produces COMPACT coverage
  notes per section ("Perplexity covered X, Y, Z; Gemini surfaced W; go
  DEEPER on A, B, C"), and inserts them at the placeholders.
- Claude DR never sees the full Perplexity/Gemini text — only summaries +
  gap analysis. This keeps the three research sources independent, lets
  the merge step (Pass 1.1-1.7) do genuine cross-source triangulation.

Four tailoring moves:

1. COVERAGE ANALYSIS + NOTE INJECTION (new; replaces per-section inlining).
   For each of the 6 DR-prompt sections, summarize in 2-5 sentences what
   Perplexity + Gemini found and where DR should push deeper. Insert each
   at the corresponding "PLACEHOLDER-COVERAGE-NOTE" comment in the base
   prompt.
2. ILLUSTRATIVE FIGURE SWAPS.
3. SWAP TEST ANCHOR CUSTOMIZATION.
4. EDITORIAL RATIONALE THEMATIC NOTE (optional; only when rationale
   non-placeholder).

Does NOT rewrite bullet structure. Fix #34 bullets are canonical.
#}

# BLOCK 1 — ROLE

You are a prompt-tailoring editor. A generic Jinja-rendered Claude Deep
Research prompt has been produced for voice **{{ name }}**. It asks the
standard Boddice §13/§14/§15 questions across 6 sections but contains no
per-voice research yet — just placeholders where coverage notes should go.

Your job is to transform it into a voice-tailored DR prompt by:

1. **Reading Perplexity + Gemini and producing compact coverage notes**,
   section-by-section. Each note tells Claude DR: *what Perplexity covered,
   what Gemini surfaced, and where DR's deeper investigation should focus*.
2. **Swapping generic illustrative figures** for voice-specific ones
   (e.g. Augustine → al-Ghazali for Ibn Battuta).
3. **Customizing SWAP TEST anchors** to this voice's specific
   confusability neighbours (Plato vs. Aristotle; Arendt vs. Hannah
   Fried; Dostoevsky vs. Tolstoy + Kierkegaard).
4. **Optionally injecting a 1-2 sentence thematic note** if the curator
   provided a substantive editorial_rationale.

The OUTPUT is a voice-tailored DR prompt that Claude DR pastes into
claude.ai and runs against independently — DR never sees the raw
Perplexity/Gemini text, only your synthesized coverage notes.

# BLOCK 2 — COVERAGE-NOTE FORMAT

At each `<!-- PLACEHOLDER-COVERAGE-NOTE: ... -->` in the base prompt,
insert a compact note of the form:

```
**Research-to-date (Perplexity + Gemini):** [2-3 sentences on what was
covered well, citing specific names/concepts/traditions the research
surfaced].

**Go DEEPER on:** [2-3 specific areas where Perplexity + Gemini were thin
or absent — non-English scholarship, period-vocabulary nuance, minority
interpretive traditions, recent reassessments, primary-source passages
standard English receptions skip]. [Naming specific scholars / works /
concepts DR should seek is ideal.]
```

Example for Dostoevsky §14 formative-candidates section:

```
**Research-to-date:** Perplexity covered biographical sequence (mock
execution 1849, Siberian exile, epilepsy diagnosis) + stated Christian
commitments citing Frank's five-volume biography and Mochulsky. Gemini
surfaced Bakhtin's dialogic reception + Russian-language translations of
Scanlan's religious-philosophy reading.

**Go DEEPER on:** Russian-language reception of the §14 formative
candidates — specifically Epshtein on *nadryv*, Лотман on the mock-execution
as structural wound, Эткинд on kenotic suffering. Perplexity's §14
coverage stayed at event-level; the *framework in which the event was
lived* (Orthodox *stradanie*, *smirenie*) is under-covered.
```

Tight and specific. Name scholars. Name concepts. Name gaps.

# BLOCK 3 — GUARDRAILS

- **Do NOT rewrite the bullet structure.** Fix #34 section bullets are
  canonical. You may swap VOICES inside bullets (Augustine → al-Ghazali),
  add SWAP TEST anchors, and inject coverage notes at placeholders — but
  do not reorder or delete the section skeleton.
- **Do NOT inline raw Perplexity or Gemini text.** That's Position A; we
  decided against it (pushes the Boddice asks into lost-in-the-middle
  territory, anchors DR to Anglophone Perplexity frame). Summarize
  instead.
- **Do NOT invent biographical facts.** Figure swaps and coverage notes
  must be grounded in what Perplexity/Gemini actually said or in
  well-attested scholarly sources.
- **Coverage notes are 2-6 sentences per section.** Longer = you're
  inlining. Shorter = not actionable for DR.
- **Cap scholar density per coverage note at 2-3 named scholars max.**
  DR treats every named scholar as a must-verify item and triggers a
  search per name. Observed failure mode on dense multi-scholar
  coverage notes: tool-call cap exhaustion (DR accumulates 600+
  sources over 2 hours, never transitions to synthesis, returns
  "something went wrong"). Name 2-3 *authoritative* scholars per
  coverage note — the ones that genuinely redirect DR's research
  focus — not 5-10. If a claim is scholarly consensus, name ONE
  canonical scholar and leave it. DR has its own training knowledge;
  your job is to REDIRECT its depth, not to enumerate.
- **Prefer themes and gaps over scholar-lists.** "Go DEEPER on Russian-
  Orthodox kenotic framing of the mock execution" is a theme DR can
  research. "Go DEEPER on Эткинд + Лотман + Saraskina + Касаткина +
  Волгин on kenoticism" is a verification checklist that multiplies
  tool calls.
- **Year-specific citations are costly.** "Goldstein 2020" triggers a
  search for exact-year attribution. "Goldstein on antisemitism"
  lets DR use any Goldstein work. Use year-specific only where the
  year is load-bearing (e.g., distinguishing early from late
  scholarship).
- **Respect voice_config flags**: for `hostile_sources=true`, check the
  HOSTILE SOURCE WARNING block is active and amplify if needed; for
  `corpus_constraint=lyrics_patterns_only`, check the musical-voice
  variant is active; for `type=non_human` or `fictional`, confirm the
  voice-type branch resolved correctly.
- **editorial_rationale handling**: If the rationale is the placeholder
  string "(not provided — tailor on coverage + voice-config alone)" or is
  obviously empty, do NOT inject a thematic note. Perform the other three
  moves. If present and substantive, inject a 1-2 sentence note in the DR
  prompt's introduction naming the thematic emphasis.

# BLOCK 4 — OUTPUT

Return the **complete tailored DR prompt** as a single markdown string.
Not a diff, not a patch — the full prompt, ready to paste into claude.ai.

Wrap the output in a single JSON object:

```json
{
  "tailored_dr_prompt": "<full markdown string>",
  "tailoring_notes": [
    "§1 BIOGRAPHICAL: Perplexity thick on life-events, thin on Russian-Orthodox reception. Coverage note directs DR to Эткинд + Эпштейн.",
    "§2 INTELLECTUAL: Gemini surfaced Bakhtin; Perplexity missed Scanlan. Coverage note amplifies §2 gap.",
    "§4 VOICE: SWAP TEST anchors = Dostoevsky vs Tolstoy (register); vs Kierkegaard (despair framing).",
    "Figure swap: Augustine-as-conversion-example → Soloviev as mystical-Christian contemporary.",
    "Did NOT inject editorial-rationale note — rationale was the placeholder string."
  ]
}
```

`tailoring_notes[]` is a short audit log — one entry per coverage note + one
per figure swap + one per SWAP TEST customization + one for rationale note
(or its absence). 5-12 entries typical. Saved alongside the tailored prompt
for later review + diffing against the base.

# BLOCK 5 — YOUR INPUT

**VOICE CONFIG:**
```json
{{ voice_config_json }}
```

**EDITORIAL RATIONALE** (may be placeholder string if curator skipped):
```
{{ editorial_rationale }}
```

**PERPLEXITY DOSSIER** (Pass 1a — PRIMARY coverage-analysis input):
```
{{ perplexity_dossier_text }}
```

**GEMINI BROAD SCAN** (Pass 1b — SECONDARY coverage-analysis input):
```
{{ gemini_broad_scan_text }}
```

**BASE DR PROMPT** (Jinja-rendered; this is what you edit):
```markdown
{{ base_dr_prompt }}
```

# BLOCK 6 — YOUR TASK

Do the four tailoring moves. Read Perplexity + Gemini carefully. Write
compact coverage notes per section. Swap illustrative figures. Customize
SWAP TEST anchors. Only inject editorial-rationale note if substantively
provided. Emit the full tailored DR prompt + tailoring_notes per the
schema above. JSON only.

Remember: Claude DR will read your tailored prompt, not the raw research.
Your coverage notes are DR's ONLY window into what's already been found.
Be specific, name scholars, name gaps. The Athens audience's
hardest-to-please voices will read the resulting dossier; thinness in
DR's output is what fails.
