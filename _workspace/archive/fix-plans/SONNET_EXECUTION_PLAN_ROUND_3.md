# Sonnet Execution Plan — Round 3

**Paste this into a fresh Claude Sonnet 4.6 session, medium effort. The plan is self-contained.**

## Your task

Execute fixes 24–33 in `personas/notes/WALKTHROUGH_FIXES_PENDING.md`. Commit after each sub-phase. Push at the end. Stop and ask if anything is unclear or a verification fails — do NOT proceed through broken state.

Rounds 1 and 2 (fixes 1–23) are already implemented and merged to main.

**CRITICAL:** Fix #34 (Opus collaborative bullet rewrite) is NOT in this plan's scope. The existing 6-section research bullets in `pass_0b_dr_prompt.md` stay untouched. Fix #34 will be a follow-up commit after your session finishes.

## Preflight

1. Read these in order:
   - `personas/notes/WALKTHROUGH_FIXES_PENDING.md` — especially the Round 3 (items 24–28) and Round 4 (items 29–33) sections
   - `docs/AI_Assembly_Persona_Pipeline_v3_9.md` — current pipeline spec
   - `docs/AI_Assembly_Persona_Card_v2.md` — 37-field card template (source for fix #30's field-level granularity bars)
   - `personas/run_pass0a_voice_config.py`, `personas/run_pass0b_dr_prompt.py`, `personas/run_phase0_1_research.py`
   - `personas/flows/shared/prompts/pass_0a_voice_config.md`, `personas/flows/shared/prompts/pass_0b_dr_prompt.md`
   - `personas/flows/shared/node0_validation.py`, `personas/flows/shared/dr_validation.py`, `personas/flows/shared/wikipedia.py`

2. Verify you're on `main` and the tree is clean. Create feature branch:
   ```bash
   cd /Users/aienvironment/Desktop/ai-assembly
   git checkout main && git pull
   git checkout -b walkthrough-fixes-round3-2026-04-17
   ```

## Phase A — Pass 0a UX hardening (Round 3 fixes 24–28)

### A.1 — Fix #24: Show Wikipedia source in review_doc

Update `pass_0a_voice_config.md` to add a new section near the top of the review_doc template:

```markdown
## Wikipedia grounding

- Source: [<page_title>](<wikipedia_url>)
- Description: <wikipedia_description>
- Extract (first 500 chars): <wikipedia_extract[:500]>...
```

Or, when `wikipedia_url` is absent:
```markdown
## Wikipedia grounding

No Wikipedia page was used — classification derives from Opus training data + `--hint` (if provided).
```

Update `run_pass0a_voice_config.py` — if Wikipedia was used, the review_doc model already receives the extract via the user_payload, but the prompt currently doesn't tell it to surface that verbatim. Update the Pass 0a prompt to instruct the model to include the Wikipedia grounding section.

**Commit:** `fix: show Wikipedia grounding source in Pass 0a review_doc (auditability)`

### A.2 — Fix #25: Disclaimer on "Why this voice is in the Assembly"

Update `pass_0a_voice_config.md`. In the review_doc template's "Why this voice is in the Assembly" section, add explicit instruction for the model to prefix the section with:

> *⚠ Draft rationale — Opus's plausibility guess from training data, not research-verified. Confirm against the DR dossier when it arrives.*

**Commit:** `fix: add disclaimer to Pass 0a review_doc casting-rationale section`

### A.3 — Fix #26: Warning at Pass 0a exit when Wikipedia was skipped

In `run_pass0a_voice_config.py`, before the "Next steps" stamp block, add:

```python
if wiki_summary is None:
    stamp("")
    stamp("⚠ Wikipedia grounding was skipped. Pass 0b's DR prompt will omit the")
    stamp("  'start from Wikipedia' instruction. Expect thinner scaffolding unless")
    stamp("  you hand-edit the DR prompt.")
```

**Commit:** `fix: Pass 0a warns at exit when Wikipedia grounding was skipped`

### A.4 — Fix #27: `--choose N` flag for non-interactive picker

In `run_pass0a_voice_config.py`:
- Add `--choose N` CLI flag (integer, 1-indexed)
- Make `--choose`, `--wiki`, and `--hint` mutually exclusive via argparse
- When `--choose N` provided, skip the interactive picker and select result N from the search results
- If N is out of range (e.g., only 3 results but `--choose 5`): if TTY is available, fall back to the interactive picker; else `sys.exit(f"--choose {N} out of range; only {len(results)} results found")`

**Commit:** `feat: --choose N flag for non-interactive Wikipedia picker (batch/GUI compatibility)`

### A.5 — Fix #28: Log failed field on validation retry

In `run_pass0a_voice_config.py`'s validation exception handler (around line 179), parse the `InputRejected.reason` string to extract the field name (e.g., parse out `voice_mode`, `corpus_constraint`, `subtype`, or `type` from the error message). Log it separately:

```python
except InputRejected as exc:
    # Parse field name from error message
    field_match = re.search(r"Invalid (voice_mode|corpus_constraint|subtype|type)\s*", str(exc))
    field = field_match.group(1) if field_match else "unknown"
    stamp(f"  VALIDATION FAIL: field={field}")
    stamp(f"  Retrying with critique…")
    # ... existing retry logic
```

Add `import re` at top if not present.

**Commit:** `fix: log failed field name on Pass 0a validation retry (telemetry)`

## Phase B — Pass 0b template and scaffolding refactor (Round 4 fixes 29–33)

### B.1 — Fix #29: Python split of Perplexity output by section

Create `personas/flows/shared/perplexity_split.py`:

```python
"""Split Perplexity's 6-section dossier text into a dict keyed by section number."""
from __future__ import annotations
import re

# Section heading patterns — matches same alternatives validate_dr_dossier uses
_SECTION_PATTERNS = [
    (1, re.compile(r"^#+\s*1\.\s*(BIOGRAPHICAL|BIOLOGICAL|TEXTUAL) FOUNDATION\b", re.MULTILINE | re.IGNORECASE)),
    (2, re.compile(r"^#+\s*2\.\s*(INTELLECTUAL FRAMEWORK|PERCEPTUAL WORLD|SYSTEMIC PROPERTIES|CHARACTER AS INTELLECTUAL CONSTRUCT)\b", re.MULTILINE | re.IGNORECASE)),
    (3, re.compile(r"^#+\s*3\.\s*(REASONING PATTERNS|RELATIONAL PATTERNS|NARRATIVE STRATEGY)\b", re.MULTILINE | re.IGNORECASE)),
    (4, re.compile(r"^#+\s*4\.\s*VOICE AND STYLE\b|^#+\s*4\.\s*SCIENTIFIC LITERATURE\b", re.MULTILINE | re.IGNORECASE)),
    (5, re.compile(r"^#+\s*5\.\s*(HISTORICAL BOUNDARIES|ONTOLOGICAL BOUNDARIES|PHILOSOPHICAL AND LEGAL FRAMEWORKS)\b", re.MULTILINE | re.IGNORECASE)),
    (6, re.compile(r"^#+\s*6\.\s*(PRIMARY TEXTS|PRIMARY SCIENTIFIC LITERATURE|PRIMARY DOCUMENTS|RECEPTION AND INFLUENCE)\b", re.MULTILINE | re.IGNORECASE)),
]


def split_dossier(text: str) -> dict[int, str] | None:
    """Split a 6-section Perplexity dossier into {section_number: content} dict.

    Returns None if fewer than 6 sections are recognizable (caller falls back
    to single-block scaffolding).
    """
    # Find all section boundary positions
    boundaries = []
    for section_num, pattern in _SECTION_PATTERNS:
        match = pattern.search(text)
        if match is None:
            return None  # section missing — fallback
        boundaries.append((section_num, match.start()))

    # Sort by position to get true order
    boundaries.sort(key=lambda b: b[1])

    if len(boundaries) != 6:
        return None

    # Split text at each boundary; each section runs from its start to the next
    sections = {}
    for i, (section_num, start) in enumerate(boundaries):
        end = boundaries[i + 1][1] if i + 1 < len(boundaries) else len(text)
        sections[section_num] = text[start:end].strip()

    return sections
```

Update `run_phase0_1_research.py`:
- Import `from flows.shared.perplexity_split import split_dossier`
- After loading `pass1a` output, call `perplexity_sections = split_dossier(perplexity_text)` 
- Pass both `perplexity_findings` (full text, fallback) and `perplexity_sections` (dict or None) to the template context

**Verify:** `python3 -c "from flows.shared.perplexity_split import split_dossier; ..."` (construct a small test dossier and confirm it parses into 6 sections).

**Commit:** `feat: split Perplexity dossier into per-section dict for scaffolding interleave`

### B.2 — Fix #32: Add Section 6 to non-human DR template + update validator

Edit `personas/flows/shared/prompts/pass_0b_dr_prompt.md` — in the `{% elif type == "non-human" %}` branch, add a 6th section after section 5:

For `subtype == "system"`:
```
6. PRIMARY DOCUMENTS
   - Foundational legal documents (legislation, treaties, court decisions)
   - Indigenous oral tradition sources and how they have been documented
   - Key scholarly analyses of the personhood framework
   - Relevant environmental impact assessments or reports
```

For `subtype` organism (default non-human):
```
6. PRIMARY SCIENTIFIC LITERATURE
   - Foundational papers and monographs on this species/entity
   - Key review articles and field guides
   - Seminal behavioural studies with quotable passages (for Pass 1c to fetch)
   - Active research groups and recent publications
```

Update `personas/flows/shared/dr_validation.py` section-6 regex to accept all three alternatives:
```python
r"^#+\s*6\.\s*(PRIMARY TEXTS|PRIMARY SCIENTIFIC LITERATURE|PRIMARY DOCUMENTS|RECEPTION AND INFLUENCE)\b"
```

(The "RECEPTION AND INFLUENCE" alternative is for the fictional branch's existing section 6.)

**Verify:** `python3 personas/scripts/validate_dr_dossier.py` against a hand-constructed minimal non-human dossier containing the new section 6 heading — should succeed.

**Commit:** `fix: add section 6 to non-human DR template + update validator (Octopus/Whanganui now validate)`

### B.3 — Fix #31: `corpus_constraint` conditional block in DR template

Edit `personas/flows/shared/prompts/pass_0b_dr_prompt.md`. After the `{% if hostile_sources %}` block (and its `{% endif %}`), add:

```jinja
{% if corpus_constraint == "lyrics — describe patterns only" %}

MUSICAL VOICE — LYRICS CONSTRAINT: This voice's primary corpus is copyrighted lyrics. Do NOT attempt to reproduce lyrics verbatim. Instead:

- Describe lyrical patterns, thematic arcs, structural devices across the catalogue
- Quote interviews, speeches, and non-lyric writings verbatim (these are the speaking-voice corpus)
- In Section 6 PRIMARY TEXTS, list albums/songs by title + thematic description, not lyrical content
- The downstream Voice Pipeline will produce text not song — research the speaking voice, not the singing voice
{% endif %}
```

Update `run_pass0b_dr_prompt.py` and `run_phase0_1_research.py` to pass `corpus_constraint` into the template context (already should be in voice_config; just ensure it's threaded through).

**Verify:** render the template with `corpus_constraint="lyrics — describe patterns only"` and confirm the block appears; render with `"full"` and confirm it doesn't.

**Commit:** `feat: corpus_constraint conditional block in DR template (Marley-class voices)`

### B.4 — Fix #30: Card-field annotations per section in DR template

Edit `personas/flows/shared/prompts/pass_0b_dr_prompt.md`. For each of the 6 sections across all three type branches (human, non-human, fictional), add a "What this section feeds downstream" block BEFORE the existing section bullets.

**CRITICAL:** Do NOT touch the existing section bullets — they'll be rewritten in the follow-up Step 34 commit. Only INSERT the field-annotations block at the top of each section.

Pull field-level granularity bars from `docs/AI_Assembly_Persona_Card_v2.md`'s "Therefore" instructions.

**Annotation content by section (human type):**

Section 1 BIOGRAPHICAL FOUNDATION:
```
What this section feeds downstream:
  - world (time, place, institutions, intellectual currents)
  - formative_experience (THE ONE wound + the lesson it taught — one specific event, not a category)
  - character (personality traits, quirks, contradictions, self-understanding)
  - topics_requiring_care (historical views conflicting with modern sensibilities — partial)
```

Section 2 INTELLECTUAL FRAMEWORK:
```
What this section feeds downstream:
  - constitution — 10-20 principles with operational notes; ≥2 internal tensions; 3+ concepts unique to this figure with textual references
  - concept_lexicon — 5-10 concepts, each with definition AND what it rules out
  - bold_engagement_topics — derived from the constitution's most provocative commitments
  - epistemic_frame_statement — draws on scholars whose readings inform the construction
```

Section 3 REASONING PATTERNS:
```
What this section feeds downstream:
  - reasoning_method — 5-8 step cognitive moves, each with a worked example
  - finds_compelling / resists — texture of argument that draws the voice in / triggers critique
  - disagreement_protocol — HOW this voice disagrees (not WHAT with)
  - default_questions — 3-5 recurring interrogatives this voice habitually brings
  - translation_protocol — step-by-step process for how this voice encounters the unfamiliar
```

Section 4 VOICE AND STYLE:
```
What this section feeds downstream:
  - rhetorical_mode — fundamental mode of expression in 1-2 sentences
  - characteristic_moves — 3-5 named signature patterns with descriptions
  - register_and_tone — what the voice IS and what it's NOT
  - metaphorical_repertoire — recurring images, analogies, sensory fields from the corpus
  - preferred_vocabulary — the words this voice thinks in
  - banned_language / banned_modes — words/framings this voice would never use
  - medium, characteristic_output_structure — format and arc of typical works
```

Section 5 HISTORICAL BOUNDARIES:
```
What this section feeds downstream:
  - knowledge_boundary — general frame AND specific exclusion list
  - topics_requiring_care — specific topics with navigation guidance per topic
  - hard_limits — 3-5 absolute prohibitions, character-breaking only
```

Section 6 PRIMARY TEXTS:
```
What this section feeds downstream:
  - curated_corpus_passages — 5-10 representative passages (Pass 1c fetches them from the URLs you list)
  - preferred_vocabulary, metaphorical_repertoire — textured content extracted from passages
  - length_and_format_constraints — typical length, pacing, closing patterns
```

For the non-human and fictional type branches, use the analogous annotations (derive from card field specs).

**Verify:** render the template with various type/subtype/corpus_constraint combinations; inspect each rendered prompt to confirm the field annotations appear correctly per section.

**Commit:** `feat: card-field annotations per section in DR template (Medium enrichment)`

### B.5 — Fix #33: Interleave per-section scaffolding in template

Edit `personas/flows/shared/prompts/pass_0b_dr_prompt.md`. The current template places a single `PRIOR RESEARCH FINDINGS` block before the section body. Restructure so each section's scaffolding (from `perplexity_sections[N]`) appears inline.

Proposed structure per section:

```jinja
## Section 1: BIOGRAPHICAL FOUNDATION

[Card-field annotations block from fix #30]

Starting material from Perplexity's §1:
{% if perplexity_sections %}
{{ perplexity_sections.get(1, "(Perplexity §1 not recognized; see full Perplexity block below)") }}
{% else %}
(Perplexity findings available as unstructured block below)
{% endif %}

Your task for Section 1: [EXISTING BULLETS — do not touch; fix #34 will rewrite these later]

---

[Section 2 same pattern, etc.]
```

After all 6 sections:
```jinja
---

CROSS-DISCIPLINARY ADDITIONS (from Gemini broad scan — consult for any section):

{{ gemini_findings }}

{% if not perplexity_sections and perplexity_findings %}
---

FALLBACK: Perplexity output could not be split by section. Full output:

{{ perplexity_findings }}
{% endif %}
```

Remove the standalone "PRIOR RESEARCH FINDINGS" block near the top — scaffolding now lives per-section.

**Verify:** render the template with a test voice_config + mock `perplexity_sections` dict; confirm the per-section starting material appears inline. Render with `perplexity_sections=None` to confirm fallback works.

**Commit:** `refactor: interleave Perplexity per-section scaffolding in DR template (fix #33)`

## Phase C — Final verification and push

### C.1 — Import smoke tests

```bash
cd /Users/aienvironment/Desktop/ai-assembly
python3 -c "from personas.flows.shared.perplexity_split import split_dossier"
python3 -c "from personas.flows.shared.dr_validation import validate_dr_dossier"
python3 -c "import personas.run_pass0a_voice_config"
python3 -c "import personas.run_pass0b_dr_prompt"
python3 -c "import personas.run_phase0_1_research"
```

### C.2 — Template rendering tests

Hand-render the template with a few voice_config variations to confirm structure:
- Human + hostile_sources=true (Cleopatra)
- Non-human + subtype=organism (Octopus)
- Non-human + subtype=system (Whanganui)
- Human + corpus_constraint="lyrics — describe patterns only" (Marley)
- Fictional (Scheherazade)

For each: confirm (a) correct type variant body, (b) correct conditional blocks fire, (c) scaffolding interleaves correctly, (d) field annotations appear per section.

### C.3 — Update pipeline spec

In `docs/AI_Assembly_Persona_Pipeline_v3_9.md`:
- Add a new section "Phase 0.5 Pre-DR Research" if not already present describing fixes 29-33
- Mention the per-section scaffolding + card-field annotations + corpus_constraint conditional
- Note Round 4 Step 34 (bullet rewrites) as a follow-up commit pending

If the spec needs a version bump, use v3.10. Otherwise add a note at the top. Use your judgement based on scope — v3.10 bump feels right given the architectural addition.

**Commit:** `docs: spec update reflecting Phase 0.5 scaffolding refactor (v3.10)`

(Or just update in-place as v3.9 if a version bump feels premature.)

### C.4 — Push

```bash
git push -u origin walkthrough-fixes-round3-2026-04-17
```

Report back with a summary of completed items.

---

## Notes for Sonnet

- **Fix #34 is explicitly out of scope.** Do NOT modify the existing section bullets in `pass_0b_dr_prompt.md`. They'll be rewritten in a separate collaborative commit.
- **If you hit an ambiguity:** stop, write a comment in `WALKTHROUGH_FIXES_PENDING.md` under `## Sonnet Round 3 Questions`, ask.
- **If a verify step fails:** stop immediately. Don't commit broken state.
- **Do NOT edit:** `personas/runs/**`, `runtime/runs/**`, `personas/inputs/voices/_archive/**`.
- **Write a handoff note at `personas/notes/SONNET_HANDOFF_ROUND_3.md` if context runs low** — same pattern as Round 1. Include commit SHAs + next item + any ambiguities.

## Dependency summary

- A.1-A.5 (Round 3 UX): independent of each other and of Phase B.
- B.1 (Perplexity split): independent.
- B.2 (non-human section 6): independent.
- B.3 (corpus_constraint): independent.
- B.4 (card-field annotations): **must run before B.5** so the annotations are in place when scaffolding gets interleaved.
- B.5 (scaffolding interleave): **depends on B.4** and B.1.

Execute: A.1 → A.2 → A.3 → A.4 → A.5 → B.1 → B.2 → B.3 → B.4 → B.5 → C.
