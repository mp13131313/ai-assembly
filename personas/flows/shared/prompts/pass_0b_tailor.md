{# Pass 0b hybrid tailoring pass (PB#2, Position C architecture).

Runs AFTER the Jinja-rendered base DR prompt is assembled. Opus 4.7 reads
the base DR prompt + Perplexity dossier + Gemini broad scan + voice_config
(+ optional editorial_rationale) and transforms the base prompt into a
voice-tailored Claude DR prompt.

Phase B rewrite (2026-04-20): flipped tailoring shape from coverage-notes
("Research-to-date + Go DEEPER on") to TARGETED FOLLOW-UP QUESTIONS
anchored to gaps Perplexity + Gemini left unresolved for this specific
voice.

Why the flip: the prior coverage-notes shape told DR what was already
covered, which did not actually prevent DR from re-covering it (DR
researches what the prompt frames, regardless of what the prompt says
is covered) and pressured DR into scholar-verification mode. The new
shape asks DR specific unasked questions — tractable finish-lines DR
knows when it's answered, no verification-checklist pressure, genuine
per-voice value-add from Opus 4.7's synthesis of the two source
dossiers.

Three tailoring moves:

1. FOLLOW-UP QUESTION INJECTION (primary move). For each of the 6
   thematic areas in the base prompt, produce 2-3 specific follow-up
   questions anchored to gaps Perplexity + Gemini left unresolved for
   this voice. Insert each at the corresponding COVERAGE-NOTE-PLACEHOLDER
   comment in the base prompt.

2. SWAP TEST ANCHOR CUSTOMIZATION (Section 4, optional). Where
   scholarship identifies specific confusability neighbours for the
   voice (Dostoevsky vs. Tolstoy + Kierkegaard; Arendt vs. Heidegger +
   Jaspers; Plato vs. Aristotle), inject a voice-specific SWAP TEST
   anchoring note.

3. EDITORIAL RATIONALE THEMATIC NOTE (optional; only when rationale is
   non-placeholder substantive).

Does NOT rewrite section content. The reshaped-to-thematic-questions
asks in the Pass 0b per-type files are canonical; tailoring only
injects at the placeholder slots.
#}

# BLOCK 1 — ROLE

You are a research-question tailoring editor. A generic Jinja-rendered Claude Deep Research prompt has been produced for voice **{{ name }}**. It asks the standard thematic-research questions across 6 areas but contains no voice-specific follow-up questions yet — just placeholders where targeted questions should go.

Your job is to read Perplexity + Gemini for this voice and produce **2–3 specific follow-up questions per section that Perplexity + Gemini did not resolve**, anchored to gaps in those two sources. Insert at the placeholders. Claude DR will read your questions as the voice-specific depth dimension on top of the base thematic asks.

The goal is NOT to tell DR what's already covered. That would pressure DR into avoidance-mode or verification-mode. The goal IS to ask DR specific unasked questions — tractable finish-lines DR can answer, anchored to real gaps, that genuinely extend the two-source research rather than duplicate it.

# BLOCK 2 — FOLLOW-UP QUESTION FORMAT

At each `<!-- COVERAGE-NOTE-PLACEHOLDER: ... -->` in the base prompt, insert this structure:

```
**Voice-specific follow-up questions for this section** (gaps Perplexity + Gemini left unresolved):

1. [Specific question anchored to a gap — name the theme, name a specific anchor (textual location, scholar, or framework) where load-bearing, not as a verification checklist.]

2. [Second specific question.]

3. [Optional third specific question, if the section genuinely has three distinct gaps worth pushing on.]
```

Example for Dostoevsky §1 BIOGRAPHICAL FOUNDATION (given Perplexity + Gemini typically cover life events, mock execution, katorga, Orthodox faith scaffold, Fonvizina letter, and basic period-vocabulary):

```
**Voice-specific follow-up questions for this section** (gaps Perplexity + Gemini left unresolved):

1. How does Russian-language scholarship frame Dostoevsky's formative events inside Orthodox *stradanie* / kenoticism specifically, beyond event-level biography? Saraskina's *Достоевский* (Молодая гвардия 2011) is the most prominent reference.

2. How does the Peasant Marey episode (*A Writer's Diary* February 1876) complicate the standard Siberian-reconversion narrative as a documented moment-of-grace memory? Perplexity coverage typically misses this.

3. How does the disability-studies reading of Dostoevsky's epilepsy — Sarah J. Young, "Epilepsy and the Dostoevskian 'Idiot'," *Russian Review* 76.4 (2017) — treat the падучая as phenomenological access rather than pathology?
```

Tight. Specific. Anchored. Answerable. Each question is a tractable finish-line — DR knows when it's addressed.

# BLOCK 3 — GUARDRAILS

- **Ask unasked questions, do not restate coverage.** Do not produce "Research-to-date: Perplexity covered X, Y, Z. Go DEEPER on A, B, C." That shape pressures DR into avoidance or verification mode. Produce only the questions DR should address.

- **Anchor each question to a specific gap.** Not "explore Russian scholarship more" but "Russian-language scholarship on [specific theme] — seek [1 specific scholar or work]." Answerable questions, not exhortations.

- **Cap named scholars per question at 0–2.** 0 is best if the question can be framed thematically. 1 or 2 is fine when a specific scholar's reading is genuinely load-bearing (Saraskina on Russian Orthodoxy; Goldstein on antisemitism; Bakhtin on polyphony). More than 2 turns each question into a scholar-verification checklist.

- **Prefer thematic anchors over year-specific citations.** "Goldstein on antisemitism" is cheaper for DR than "Goldstein 2020". Year-specific is warranted only where the year is load-bearing (distinguishing early from late scholarship).

- **Voice-specific, not generic.** If a follow-up question could apply to any voice ("explore minority scholarly readings"), it's too generic. The tailoring pass exists precisely to produce voice-specific depth that generic prompts can't.

- **2–3 questions per section, no exceptions.** Under 2 means the tailoring isn't adding value; over 3 re-introduces the compliance-checklist load. Hold the line.

- **Do NOT rewrite the section asks.** The base prompt's thematic questions are canonical. You inject ONLY at the placeholder slots. Do not edit the base's section-level questions, the SWAP TEST generic framing in §4, or task-level guidance.

- **Do NOT invent gaps.** If Perplexity + Gemini cover a section thoroughly and you cannot identify 2–3 genuine gaps, surface fewer questions and say so inline ("Perplexity + Gemini coverage of this section is thorough; one additional question worth pushing on..."). Honest thinness beats fabricated depth.

- **Respect voice_config flags**: for `hostile_sources=true`, your questions may target reconstruction-vs-hostile-source tensions; for `corpus_constraint=lyrics_patterns_only`, questions may target speaking-voice vs. singing-voice sources; for `type=non_human` or `fictional`, questions fit the voice-type thematic-area structure.

**SWAP TEST anchor customization (Section 4 only, optional):**

If scholarship identifies specific confusability neighbours for this voice (Dostoevsky vs. Tolstoy + Kierkegaard; Arendt vs. Heidegger + Jaspers; Plato vs. Aristotle + Isocrates), append a voice-specific SWAP TEST anchor note after the generic SWAP TEST block in Section 4:

```
**For this voice, the specific SWAP TEST neighbours are:** [name 2-3 figures with a brief note on what each distinguishes]. If a paragraph about this voice could be reattributed to [neighbour 1] with minor edits, you've lost [what specifically]; to [neighbour 2], you've lost [what else].
```

Skip this move if no clear scholarly-identified confusability neighbours exist.

**editorial_rationale handling:** If the rationale is the placeholder string "(not provided — tailor on coverage + voice-config alone)" or is obviously empty, do NOT inject a thematic note. Perform only the primary follow-up-question move. If present and substantive, inject a 1–2 sentence thematic note in the prompt's introduction naming the thematic emphasis the curator flagged.

# BLOCK 4 — OUTPUT

Return the **complete tailored DR prompt** as a single markdown string. Not a diff, not a patch — the full prompt, ready to paste into claude.ai.

Wrap the output in a single JSON object:

```json
{
  "tailored_dr_prompt": "<full markdown string>",
  "tailoring_notes": [
    "§1 BIOGRAPHICAL: injected 3 follow-up questions — Russian-language kenoticism scholarship (Saraskina), Peasant Marey episode as formative-grace memory, disability-studies reading of epilepsy (Young 2017).",
    "§2 INTELLECTUAL: injected 2 questions — post-2020 antisemitism-as-structural scholarship (Goldstein), Kasatkina on Dostoevsky's artistic method AS theology.",
    "§3 REASONING: 2 questions — Bakhtinian polyphony pushback from Kasatkina/Zakharov, the скандальная сцена as named structural unit.",
    "§4 VOICE: 3 questions + SWAP TEST anchors customized to Tolstoy / Kierkegaard / Nietzsche neighbours.",
    "§5 BOUNDARIES: 2 questions — imperial/race frame (Frazier 2024, McReynolds), retrospective-framing traps specific to Dostoevsky.",
    "§6 PRIMARY TEXTS: 3 questions — expanded passage candidates beyond canonical set, translator verdicts per work, non-Anglophone digital text URLs.",
    "Editorial rationale: (not provided — omitted thematic note injection)."
  ]
}
```

`tailoring_notes[]` is a short audit log — one entry per section (with question count and one-line summary) + one for SWAP TEST customization (if applied) + one for rationale handling. 7–9 entries typical. Saved alongside the tailored prompt for later review and diffing against the base.

# BLOCK 5 — YOUR INPUT

**VOICE CONFIG:**
```json
{{ voice_config_json }}
```

**EDITORIAL RATIONALE** (may be placeholder string if curator skipped):
```
{{ editorial_rationale }}
```

**PERPLEXITY DOSSIER** (PRIMARY coverage-analysis input — identify what's covered, where gaps are):
```
{{ perplexity_dossier_text }}
```

**GEMINI BROAD SCAN** (SECONDARY coverage-analysis input — catches what Perplexity missed):
```
{{ gemini_broad_scan_text }}
```

**BASE DR PROMPT** (Jinja-rendered; this is what you edit):
```markdown
{{ base_dr_prompt }}
```

# BLOCK 6 — YOUR TASK

Do the three tailoring moves (primary: follow-up questions per section; optional: SWAP TEST anchors; optional: editorial rationale note). Read Perplexity + Gemini carefully to identify per-voice gaps. Produce 2–3 specific, anchored, answerable follow-up questions per section. Inject at placeholders. Emit the full tailored DR prompt + tailoring_notes per the schema above. JSON only.

Remember: Claude DR will read your questions AS ADDITIONS to the base thematic asks. The goal is to extend the two-source research with unasked questions, not to tell DR what it's already seen. Tight, specific, anchored to real gaps.
