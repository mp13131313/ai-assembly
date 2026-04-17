# Walkthrough Fixes — Pending

Captured during the 2026-04-17 end-to-end pipeline walkthrough. Execute as one coherent commit after the walkthrough finishes.

## Terminology (canonical, per spec)

- **Phase** — top-level pipeline grouping (Phase 0 Intake, Phase 1 Research, Phase 2 Generation, Phase 3 Validation, Phase 4 Derive, Phase 5 Cross-QC).
- **Pass** — concrete unit within a phase (Pass 1a, Pass 2, etc.). Spec uses "Node" interchangeably; we standardize on "Pass".
- **Stage** — ❌ not spec vocabulary; dropped. Current "Stage 0a" + "Stage 0b" become "Pass 0a: Voice Config" and "Pass 0b: Claude DR Prompt" inside a new **Phase 0: Intake**.

## Architecture change (the big one)

**Drop editorial-assets entirely. Phase 0 populates only branching fields. Claude DR uses the same six-section prompt as Perplexity.**

Three research sources run in parallel during Phase 1 — Perplexity (Pass 1a), Gemini (Pass 1b), Claude DR (Pass 1a-DR) — all executing the spec's six-section research prompt on the same voice. No voice-specific editorial scaffolding. Claude DR's depth comes from its own reasoning + web search during the 60–180 min session, not from pre-injected scholar names or source lists. This matches spec intent and simplifies the intake dramatically.

---

## 1. Model rename: Opus 4.6 → Opus 4.7

Only Opus upgrades. Sonnet 4.6 stays (still the latest Sonnet).

**Code (7 files):**
- `personas/run_stage0a_intake.py` (rename to `run_pass0a_voice_config.py` per rebrand — see #5)
- `personas/run_stage0b_dr_prompt.py` (rename to `run_pass0b_dr_prompt.py`)
- `personas/run_persona_pipeline.py` (Pass 2, 3, 4a, 5, 7b)
- `personas/flows/shared/clients.py` (check default)
- `runtime/flows/researcher_flow.py` (CLAUDE_MODEL default)
- `runtime/flows/provocateur_flow.py` (CLAUDE_MODEL default)
- `runtime/flows/transcription_flow.py` (SPEAKER_ID_MODEL fallback)

**Env examples (3):** `.env.example`, `personas/.env.example`, `runtime/.env.example`.

**Docs:** persona pipeline / researcher / provocateur / transcription / IMPLEMENTATION_AUDIT / CLAUDE_DR_BRIEFING / prompt files.

**Do NOT edit:** `personas/runs/**`, `runtime/runs/**` — historical records of which model actually ran.

## 2. Remove `impossible` filter

Drop the Node 0 gate and the field from the schema.
- `personas/flows/shared/node0_validation.py` — remove `impossible === false` rejection.
- `docs/AI_Assembly_Persona_Pipeline_v3_7.md` — remove from Node 0 spec + input schema.
- `docs/AI_Assembly_Persona_Card_v2.md` — remove any mention.
- Pass 0a prompt — stop asking model to emit it.
- Clean the field out of all existing `inputs/voices/*.json` configs.

## 3. Pass 0a: retry-once on JSON/API error

Wrap `call_claude(...)` in retry-once-on-`JSONDecodeError`/`APIError`. Same for Pass 0b.

## 4. Pass 0a: require `--hint` when ambiguous

Require `--hint` whenever the name is ambiguous. Simplest: require always. Nicer: pre-check via a cheap Sonnet call.

## 5. Rebrand Stage 0a / Stage 0b → Phase 0 Intake

Rename files and internal references:
- `run_stage0a_intake.py` → `run_pass0a_voice_config.py`
- `run_stage0b_dr_prompt.py` → `run_pass0b_dr_prompt.py`
- `flows/shared/prompts/stage_0a_intake.md` → `flows/shared/prompts/pass_0a_voice_config.md`
- `flows/shared/prompts/stage_0b_dr_prompt.md` → `flows/shared/prompts/pass_0b_dr_prompt.md`
- All `Stage 0a` / `Stage 0b` string references → `Pass 0a` / `Pass 0b` (docs, comments, log messages)

**voice_mode stays `voice_mode`** (not renamed to `construction_method`). Keep the spec's name. Apply strict three-value validation: `{philosophical, observational, narratival}`. Hard-fail at Node 0 if not one of the three. Revert the freeform relaxation from commit b1868da.

## 6. Pass 0a: audit system prompt for URL emission

Remove any instruction in `pass_0a_voice_config.md` telling the model to emit `primary_text_sources` or primary-text URLs. Pass 0a has no internet access; URLs are hallucinated. Belt-and-braces: strip `primary_text_sources` from model output before writing voice_config (keep field only as manual-override hook).

## 7. `primary_text_sources` removed from Pass 0a output entirely

Pass 0a should not emit this field — not even as an empty array. It's a manual-edit hook, not intake output.
- `pass_0a_voice_config.md` — remove `primary_text_sources` from the schema block and all instructions about it.
- `run_pass0a_voice_config.py` — if the model accidentally emits it, strip before writing.
- `node0_validation.py` — field stays optional, defaults to `[]` if absent.
- `run_persona_pipeline.py:219-222` — keep the override branch (uses hand-populated URLs when present; falls through to Pass 1c-extract otherwise).

Plato's voice_config keeps its hand-populated URLs as-is. All other voice_configs: no `primary_text_sources` field.

## 8. Strip editorial-assets from voice_config schema

Remove these fields entirely from Pass 0a output and voice_config schema:
- `voice_type_adjustments_needed`
- `counter_tradition_scholars`
- `dominant_hostile_sources`
- `contested_interpretations`
- `material_culture_evidence`
- `voice_specific_warnings`

These were code-growth beyond spec. Under the new architecture, each of the three research sources (Perplexity, Gemini, Claude DR) identifies these specifics itself via prompt branching (`{% if hostile_sources %}` etc.), as the spec always intended.

**Files affected:**
- `pass_0a_voice_config.md` — remove all editorial-asset instructions, examples, and field definitions from the schema block.
- `run_pass0a_voice_config.py` — update key-presence check to validate only the 10 spec fields.
- `pass_0b_dr_prompt.md` — remove all editorial-asset weaving (lines that inject `counter_tradition_scholars`, `dominant_hostile_sources`, `contested_interpretations`, `material_culture_evidence`, `voice_specific_warnings`). See #9.
- Existing voice_configs — drop these fields from plato.json, cleopatra.json, hannah_arendt.json, octopus.json.

## 9. Rewrite Pass 0b as spec's Pass 1a prompt instantiator

Pass 0b becomes a simple template filler:

**Input:** voice_config (10 spec fields + hint for disambiguation if present), project_context.
**Output:** a paste-ready Claude DR prompt that is essentially the spec's Pass 1a user prompt ([pipeline spec lines 817-888](ai-assembly/docs/AI_Assembly_Persona_Pipeline_v3_7.md:817)) with:
- `{{name}}` substituted (and disambiguation appended if hint present)
- `{% if hostile_sources %}` branch applied (but telling Claude DR to IDENTIFY hostile sources and counter-traditions itself, not listing pre-computed ones)
- `{% if type == "non-human" %}` branch for non-human variant (the spec's `Node 1a` has a non-human prompt variant)
- `{% if subtype == "system" %}` system-entity adjustments
- `{% if type == "fictional" %}` branch for fictional variant
- A preamble telling the human to paste into claude.ai with Opus + Extended Thinking + Deep Research enabled
- A postamble telling the human to save result as `inputs/dossiers/<slug>_claude_dr.md` and run `run_persona_pipeline.py`

No voice-specific customization beyond the branching flags. Claude DR does the deep research itself.

The existing `CLAUDE_DR_BRIEFING.md` at `inputs/dossiers/` remains as reference documentation for the contract (six-heading structure, word count, not-a-persona-card checks).

## 10. Fill gaps in `subtype=system` prompt branches

Whanganui is the only system entity on the panel. Three passes currently fall through to `voice_mode` branching for her (or lump her with organisms), producing wrong-shaped output. Prompts use Jinja2 syntax (`{% if %}`).

**Validation rule:** `voice_mode` required unless `subtype == "system"`, in which case `null`. The subtype=system branches do the real work.

**Pass 3 — TWO overrides needed:**
- **Block 3 (field specifications).** Add `{% if subtype == "system" %}` before the voice_mode branching, using `[indigenous law]` / `[legal framework]` tags and organizing into systemic properties / relational commitments / boundary principles.
- **Block 4 (voice type).** Current `else` branch lumps organisms and systems. Split into organism + system sub-branches. System sub-branch: constitution grounded in relationship + framework; reasoning method is "assessment cycle read through relational framework"; ban ALL cognitive vocabulary.

**Pass 5 — TWO overrides needed:**
- **Block 3 (bold_engagement_topics).** Add system-entity override: "what the relationship demands be named."
- **Block 4 (voice type).** Split `else` into organism + system. System: engagement is relational, not perceptual.

**Pass 7b — ONE new block.** Add `{% if subtype == "system" %}` block: provocations framed as pressures on the relationship; responses expressed through the entity's condition (silting, flow, flooding).

## 11. Reconcile `corpus_constraint` enum mismatch (spec is canon)

Current Pass 0a prompt emits `"full" | "restricted" | "fragmentary" | "reconstructed"`. Spec + node0_validation accept only `"full" | "lyrics — describe patterns only" | "hostile — read against grain"`.

**Fix:** align Pass 0a to spec. Update `pass_0a_voice_config.md` to tell the model to emit the spec's three values. No change to node0_validation or Pass 4a/Pass 6 prompts.

**Mapping:**
- Marley → `"lyrics — describe patterns only"`
- Cleopatra → `"hostile — read against grain"` + `hostile_sources: true`
- Plato, Arendt, Octopus, Whanganui → `"full"`

Drop `"restricted"` and `"fragmentary"` — they aren't consumed by any pipeline branch.

## 14. Human-review gate after Pass 1c fetch (primary texts)

Spec Node 1c (lines 260-266) specifies a manual review gate after automated fetch. Current code skips it — pipeline proceeds straight from fetch to Pass 1d excerpt selection without human intervention. Restore the gate, for three reasons:

1. **LLMs identify URLs that can't be fetched.** Paywalled journals, 404s, copyright-blocked lyrics — automated fetch returns nothing and downstream silently degrades (Pass 4a falls to voice_basis=training-data, Pass 6 halts as BLOCKED).
2. **Marley-class voices (`corpus_constraint: "lyrics — describe patterns only"`)** — lyrics aren't fetchable by design; human must supply alternative corpus (interview transcripts, speeches, scholarly analyses of catalogue patterns) before Pass 4a and Pass 6 run.
3. **System entities (Whanganui)** — legislation text, indigenous oral sources, scholarly legal analyses. Some may not be web-fetchable or need specific editions the LLMs don't know about. Human supplements.

**Implementation:**
- After Pass 1c fetch completes, pipeline writes `01_research/primary_texts_review.md` showing:
  - URLs identified by Pass 1c-extract (from merged dossier), per source (Perplexity / Claude DR / Gemini)
  - Fetch status per URL (success with char-count / 404 / timeout / SSRF-blocked / copyright-likely)
  - Passages retrieved, with source + length
  - Flag if `corpus_constraint == "lyrics — describe patterns only"` or `subtype == "system"` — these need special handling
- Pipeline checks for `01_research/primary_texts_reviewed.flag` marker file. If absent, writes the review file and exits with a clear message telling the human to (a) review + optionally edit `01_research/primary_texts.json` (add/replace passages), (b) create the flag file, (c) re-run.
- On re-run, if flag present: pipeline proceeds, skipping the gate.

**File changes:**
- `run_persona_pipeline.py` — insert gate between Pass 1c fetch and Pass 1d.
- New helper to generate the review markdown from primary_texts.json + fetch results.

## 13. Pass 1-merge model upgrade: Sonnet → Opus 4.7 + adaptive thinking

Pass 1-merge does three-way contradiction detection across 45-75K tokens of research dossier content (Perplexity + Gemini + Claude DR). Subtle cross-document reasoning at long context. Sonnet can do it; Opus + thinking catches more.

**Change in `run_persona_pipeline.py`:** Pass 1-merge's `call_claude(...)` — model from `claude-sonnet-4-6` to `claude-opus-4-7`, add `thinking_budget=None` (adaptive). Bump `max_tokens` from 4096 to 16000 for headroom.

Cost impact: one call per voice, ~$1.50 each, ~$18 total for 12 voices. Trivial.

## 12. Reconcile `non_human_subtypes` enum drift

`node0_validation.py:83` accepts `{"organism", "system", "legal_entity", "river_personhood"}`. Spec documents only `{"organism", "system"}`. Pass 0a prompt mentions yet another set.

**Fix:** trim `node0_validation.py` + `pass_0a_voice_config.md` to `{"organism", "system"}` only. Whanganui = `subtype: "system"`. Future system entities (mountain, ecosystem) all classify as `"system"`.

## Voice mapping (for voice_config edits)

| Voice | voice_mode | type / subtype | hostile_sources | corpus_constraint |
|---|---|---|---|---|
| Plato | `philosophical` | human | false | `full` |
| Cleopatra | `observational` | human | **true** | `hostile — read against grain` |
| Ibn Battuta | `observational` | human | false | `full` |
| Scheherazade | `narratival` | fictional | false | `full` |
| Ada Lovelace | `philosophical` | human | false | `full` |
| Dostoevsky | `narratival` | human | false | `full` |
| Hannah Arendt | `philosophical` | human | false | `full` |
| Bob Marley | `observational` | human | false | `lyrics — describe patterns only` |
| Audrey Tang | `philosophical` | human | false | `full` |
| Peter Thiel | `philosophical` | human | false | `full` |
| Whanganui | `null` | non-human / system | false | `full` |
| Octopus | `observational` | non-human / organism | false | `full` |

Counts (voice_mode): philosophical 6, observational 4, narratival 2, null (system override) 1.

**Borderlines to watch during actual runs:**
- Ada Lovelace — thin corpus, explicit framework. If Pass 3 `philosophical` shape produces thin constitution, switch to `observational`.
- Audrey Tang — explicit framework, grounded in practice. If Pass 5 `philosophical` (courage list) reads abstract, switch to `observational`.
- Whanganui — only system entity. Watch whether the three new `subtype=system` override blocks produce coherent output.

---

## Round 2 — Added during mock walkthrough (2026-04-17)

### 15. Wikipedia-grounded disambiguation (replaces `--hint` flag)

`--hint` is brittle (quality of hint determines quality of output) and puts disambiguation burden on the human. Replace with Wikipedia-grounded pickup.

**Flow:**
- `run_pass0a_voice_config.py "Name"` — no `--hint` required
- Pass 0a queries Wikipedia Search API (free, unauth, ~1s), shows top 5 results with short descriptions
- User picks a number (or passes `--wiki <url>` to skip the picker)
- Pass 0a fetches the chosen page's lead paragraph + infobox via Wikipedia REST API
- Opus call receives Wikipedia content as grounding alongside the name
- Output voice_config adds `wikipedia_url` field (new — becomes scaffolding for Pass 0b)
- Fall back to `--hint` text input when no Wikipedia match exists

**Files:**
- `run_pass0a_voice_config.py` — add Wikipedia search + picker + page fetch + `--wiki` flag as alternative
- `pass_0a_voice_config.md` — add `wikipedia_url` to schema; tell model to use Wikipedia content as grounding for classification decisions
- `node0_validation.py` + `io.py` — add `wikipedia_url` as optional schema field

### 16. Drop `needs_dr_supplement`

Claude DR bakes deep research into Phase 1. OpenAI Pass 3 supplement is redundant.

- Remove field from voice_config schema (Pass 0a prompt)
- Remove from `node0_validation.py` defaults
- Remove Pass 3 DR supplement block from `run_persona_pipeline.py` (currently around lines 360-403)

Saves ~$2/voice.

### 17. Drop `pass_1a_claude_dr_file`

Redundant — path always derivable from slug.

- Remove field from voice_config schema
- Remove injection at `run_pass0a_voice_config.py:116`
- `run_persona_pipeline.py` constructs path `inputs/dossiers/<slug>_claude_dr.md` from voice name at load time

### 18. Drop `casting_rationale` from voice_config

Field isn't consumed downstream. Belongs in review_doc (human-readable), not voice_config (machine-consumed).

- Remove field from voice_config schema
- Update Pass 0a prompt to put rationale content inside the review_doc instead
- Remove field from `node0_validation.py`

### 19. Pass 0a client-side validation of enum fields

Currently a malformed `voice_mode` / `corpus_constraint` / `subtype` passes Pass 0a silently and only fails at pipeline runtime (Node 0).

- After `call_claude` returns, validate the 10 fields against their enums (reuse `node0_validation.validate_input`)
- On failure: retry once with a critique block appended to the user prompt; if still invalid, `sys.exit`
- Catches the issue at Pass 0a exit, not 20 minutes later

### 20. Pass 0a retry wrapper extension

Current wrapper catches `JSONDecodeError` / `APIError` / `RateLimitError`. Add: missing-required-key case (voice_config or review_doc absent, or 10-field schema incomplete).

- Extend `_call_with_retry` to catch `KeyError` and a new `IncompleteResponse` exception
- Same retry-once semantics

### 21. Convert Pass 0b from Opus call → Jinja template

Pass 0b is now pure template instantiation — type-variant selection + substitution + conditional hostile-sources appendix. No model judgment needed. Currently uses Opus at $0.50-1/voice and risks model drift (emitting editorial customization contrary to instructions).

- Replace `run_pass0b_dr_prompt.py`'s LLM call with a pure Python + Jinja2 template renderer
- `pass_0b_dr_prompt.md` converts from LLM-system-prompt to pure Jinja template
- Deterministic, zero API cost, zero drift risk

### 22. Standalone `validate_dr_dossier.py` script

Human runs this BEFORE saving Claude DR output, to catch truncation/shape errors at file-save time instead of pipeline start-time.

- New file `personas/scripts/validate_dr_dossier.py`
- Reuses the `validate_dr_dossier()` function from `run_persona_pipeline.py` (refactor to shared module)
- Takes a path argument: `python3 scripts/validate_dr_dossier.py inputs/dossiers/cleopatra_claude_dr.md`
- Clear exit codes: 0 = valid, 1 = invalid with diagnostic message

### 23. Option B reorder — Perplexity + Gemini before Claude DR

**Biggest architectural change.** Pass 1a (Perplexity) and Pass 1b (Gemini) run BEFORE the manual Claude DR session. Their findings (hostile sources identified, counter-tradition scholars named, contested interpretations surfaced, material culture catalogued) feed into Pass 0b's DR prompt as scaffolding. Claude DR starts from a grounded position, verifies + expands instead of discovering from zero.

**Script split (B-split-2 — recommended):**
- `run_pass0a_voice_config.py` — unchanged (voice_config + review doc)
- `run_phase0_1_research.py` — new: runs Pass 1a (Perplexity) + Pass 1b (Gemini) in parallel, then Pass 0b (now receives both outputs as scaffolding input), writes DR prompt to `inputs/dossiers/_dr_prompts/<slug>_dr_prompt.md`, exits
- Human runs Claude DR on claude.ai, saves to `inputs/dossiers/<slug>_claude_dr.md`
- `run_persona_pipeline.py` — runs from Pass 1-merge onward (detects DR file), with Pass 1c review gate

**New total sequence:**
```
Pass 0a → Pass 1a (Perplexity) + Pass 1b (Gemini) parallel → Pass 0b
  → manual Claude DR (60-180 min)
  → Pass 1-merge (3-way: Perplexity + Claude DR + Gemini)
  → Pass 1c-extract → Pass 1c fetch → primary-text review gate
  → Pass 1d → Pass 2 → ... → Derive
```

**Pass 0b receives as scaffolding input:**
- Perplexity dossier text (Section 2 Intellectual Framework + Section 6 Primary Texts + hostile-source tags if applicable)
- Gemini broad scan text (lesser-known material, cross-disciplinary links)
- Wikipedia URL + lead paragraph (from fix #15)

**Pass 0b's DR prompt then tells Claude DR:**
- "Here's what Perplexity already found: [...]"
- "Here's what Gemini surfaced: [...]"
- "Start from the Wikipedia page: [url]"
- "Verify these, expand depth, find what they missed. Produce the six-section dossier."

**Cost impact:** same Perplexity + Gemini calls as today, just reordered. Pass 0b Opus call replaced by Jinja template (fix #21) — net save ~$0.50-1/voice.

**Wall time impact:** Phase 0 part 2 now takes ~5-10 min (Perplexity time) before human starts Claude DR. Total wall time per voice unchanged — it's the same work moved.

**Human friction:** two invocations of pipeline scripts instead of one, plus the DR session. Matches the existing resumable pattern.

**Quality win:** hostile-source and obscure voices (Cleopatra, Whanganui edge cases) get grounded scaffolding rather than relying on Claude DR's from-scratch web search. Makes the quality floor more consistent across the 12 voices.

**Files:**
- New: `personas/run_phase0_1_research.py`
- Modify: `run_persona_pipeline.py` — split out Pass 1a, 1b, 0b; pipeline now starts at Pass 1-merge
- Modify: `pass_0b_dr_prompt.md` — Jinja template that accepts `perplexity_dossier`, `gemini_broad_scan`, `wikipedia_summary` as context variables
- Update spec doc `AI_Assembly_Persona_Pipeline_v3_8.md` — new Phase 0.5 section or fold into Phase 0

---

## Deferred (separate work)

**conference_context_paragraph enrichment.** Current value is a one-liner. Embedded verbatim into Pass 7b. Discuss and rewrite separately.

**Dropped from prior plan versions** (no longer needed under new architecture):
- Hard-validate editorial-asset keys on Pass 0a exit — the keys no longer exist.
- Hard-validate editorial-asset keys on Pass 0b entry — the keys no longer exist.
- Rename `voice_mode` → `construction_method` — keep spec's name. Strict validation is enough.
- Two-field `voice_mode + canonical_voice_mode` — abandoned in favor of strict single field.
