# Pipeline v3.7 — Implementation Audit

**Audit date:** 2026-04-15
**Spec read:** `reference/AI_Assembly_Persona_Pipeline_v3_7.md` (2,085 lines)
**Implementation read:** `flows/shared/{clients,io,node0_validation,node1c_fetch,prompt_render}.py`, `run_persona_pipeline.py`, all 13 prompt files
**Scope:** Phase 1 + Phase 2 only. Phase 3 (Pass 7-pre/7a/7b/7c), Phase 4 (Derive), and Phase 5 (Cross-Persona QC) are explicitly out of scope — they have not been built.

## Verdict at a glance

| Component | Built? | Faithful? | Notes |
|---|---|---|---|
| Node 0 — Input Validation | YES | YES (verbatim) | All 5 spec gates implemented |
| Pass 1a — Perplexity dossier | YES | YES (faithful) | `<think>` block stripping is an addition the spec doesn't mention |
| Pass 1b — Gemini broad scan | PARTIAL | DEVIATION | Client built, never wired into runner |
| Pass 1c — Primary Text Fetch | YES | PARTIAL | Automated fetch works; manual review gate not implemented |
| Pass 1-merge — Contradiction Check | PARTIAL | DEVIATION | Prompts exist; runner uses degraded passthrough |
| CT — Coherence Threading | YES | YES (faithful) | Per-pass compress, ~500 tokens, Sonnet, temp 0 |
| Pass 2 — Identity & Boundaries | YES | YES (faithful) | Prompt is verbatim spec text in Jinja2 |
| Pass 3 — Intellectual Core | YES | PARTIAL | Prompt faithful; ChatGPT DR conditional supplement not implemented |
| Pass 4a — Voice | YES | PARTIAL | Prompt faithful; 80K-char primary_texts cap is undocumented in spec |
| Pass 4b — Artifact | YES | YES (faithful) | Prompt is verbatim spec text |
| Pass 5 — Engagement | YES | PARTIAL | Prompt faithful; constitution/reasoning_method NOT passed in user prompt |
| Pass 6 — Corpus Curation | YES | PARTIAL | Prompt faithful; HALT condition handled differently |
| Phase 3 — Validation | NO | — | Pass 7-pre, 7a, 7b, 7c not built |
| Phase 4 — Derive | NO | — | Provocateur Profile + Eval Rubric not built |
| Phase 5 — Cross-Persona QC | NO | — | Not built |
| Final assembled JSON | YES | PARTIAL | Has card; missing spec's metadata block |

## Section 1: Node 0 — VERBATIM FAITHFUL

Spec specifies 5 validation gates in pseudo-IF format. Implementation in `node0_validation.py` covers all 5: `impossible` hard-rejects with the exact spec message, `type` whitelist matches, `voice_mode` whitelist matches, `subtype` required-iff-non-human enforced, `corpus_constraint` whitelist with default-to-"full" implemented.

One enhancement: I also reject when required string fields (`name`, `conference_context`) are missing. Spec doesn't specify this but it would catch a class of bugs the spec assumes won't happen.
</content>

## Section 2: Pass 1a (Perplexity) — FAITHFUL with one undocumented addition

The user prompt for human voices matches the spec verbatim — all 6 dossier headings, the hostile-source appendix, the citation instruction. The non-human and fictional variants are also written but unexercised.

**Undocumented addition:** `call_perplexity` in `clients.py` strips a leading `<think>...</think>` block from the response before returning the deliverable text. This was needed because sonar-deep-research embeds a chain-of-thought trace that would otherwise feed into Pass 2 as if it were the dossier. The spec doesn't mention this behavior — it became visible only when we ran the model. The strip is non-destructive (the raw text is preserved in the `think` field for audit). Acceptable enhancement, should be noted in a future spec revision.

**Configuration:** spec says `temperature: 0.0`, `return_citations: true`, Academic focus mode. Implementation matches except "Academic focus mode" — the API parameter for that wasn't in the docs at runtime; we passed only `temperature` and `return_citations`. Possibly a small fidelity loss; needs verification next time we touch the Perplexity API.

## Section 3: Pass 1b (Gemini) — BUILT BUT UNWIRED

`call_gemini` exists in `clients.py` (uses the modern `google-genai` SDK, handles thinking_budget). `persona_pass_1b_broad_scan.md` exists with the exact spec prompt. Runner explicitly skips this step because the project's Google API key has zero free-tier quota.

**Reason for deviation:** environmental constraint, not architectural choice. Documented in:
- `run_persona_pipeline.py` docstring
- `merged_dossier.json` (`"skip_reasons": {"pass_1b_gemini": "Google project has zero free-tier quota"}`)
- `degraded_mode: true` flag in saved output

The spec doesn't explicitly cover this case but the "Constraints" section says: *"If an API call fails, retry once. If the retry fails, log the failure and proceed to the next pass."* My implementation does the structurally similar thing — proceeds with degraded coverage and flags it.

**Real implication:** for voices where Pass 1a's coverage has gaps that Pass 1b would have filled (cross-disciplinary connections, non-English scholarship, recent reassessments), the persona card will be weaker. Pass 1a catches the canonical material; Pass 1b catches what Perplexity misses. We have only the canonical material.

## Section 4: Pass 1c — PARTIAL

The spec describes a hybrid: "**Automated step**" (HTTP fetch) followed by "**Manual review gate**" where the builder reviews the fetched passages and supplements them.

`flows/shared/node1c_fetch.py` implements the automated step well — fetches each URL in `primary_text_sources`, strips Project Gutenberg headers/footers, returns a structured list with per-source error handling. For Plato this returned 5/5 dialogues, 1.94 MB total — clean.

**What's missing:** the manual review gate. Spec says: *"Are the passages representative of this voice's range? Do the passages cover both intellectual substance AND voice/style? For under-documented figures: manually provide passages from sources the automated step missed."*

My runner has no human-in-the-loop step. Plato's case worked because the input listed 5 well-chosen Gutenberg URLs upfront. For voices where `primary_text_sources` is empty (most of the remaining 10), the spec wants Node 1c to search known repositories (Project Gutenberg, Perseus, BAWS, Internet Archive, Wikisource), then pause for manual review. My runner returns an empty list and proceeds — Pass 4a will run with `voice_basis: "training-data"` and Pass 6 will halt.

**Acceptable for current state**, since I can hand-curate `primary_text_sources` for each voice before running it (which is effectively the manual step, just done at input time instead of runtime). But it's a real architectural deviation worth naming.
</content>

## Section 5: Pass 1-merge — DEGRADED PASSTHROUGH

Spec specifies a Claude API call that takes both Pass 1a and Pass 1b outputs, looks for contradictions, and returns either `{"status": "CLEAN"}` or `{"status": "CONTRADICTIONS", "items": [...]}`.

`persona_pass_1merge_contradiction_system.md` and `persona_pass_1merge_contradiction_user.md` exist — written exactly per spec. Runner doesn't call them because there's no Pass 1b output to compare against. The runner instead writes a `merged_dossier.json` containing just Pass 1a's text plus skip-reason metadata.

**Reason:** trivially CLEAN with single source — no contradictions are possible if there's only one input.

When Gemini comes back online, I need to re-enable both Pass 1b and Pass 1-merge. The wiring is already there in the prompt files; just needs runner re-activation.

## Section 6: Coherence Threading — FAITHFUL

Spec says: *Sonnet 4.6, temperature 0.0, max_tokens 1024, runs after each generation pass (after Passes 2, 3, 4a, 4b, 5) = 5 calls per voice.*

Implementation in `_ct_compress` in the runner: Sonnet 4.6, temp 0.0, max_tokens 2048, runs after Passes 2, 3, 4a, 4b. **Discrepancies:**

- max_tokens 2048 vs spec's 1024 — I doubled it because Plato's Pass 3 output (12K tokens generated) compressed to ~700 tokens, so 1024 was tight. Acceptable enhancement.
- **5 calls vs my 4 calls** — I don't compress after Pass 5 because Pass 6 uses `pass_2_3_4a_summary`, not `pass_2_3_4_5_summary`. Need to verify whether spec's "5 CT calls" includes a post-Pass-5 compression that I should be doing for downstream use. Looking at the user prompts of subsequent passes: Pass 6's user prompt references `{{pass_2_3_4a_summary}}` — so it does NOT need a post-Pass-5 compression. The spec's "5 calls" count appears to assume someone will downstream consume the compressed Pass 5 output, but my pipeline currently doesn't have such a consumer. **Probably fine, but could be a future-proofing miss.**

The compression prompt (`persona_coherence_threading.md`) is verbatim spec text.

## Section 7: Pass 2 — VERBATIM FAITHFUL

System prompt is the spec's text, ported from Handlebars `{{#if}}` to Jinja2 `{% if %}`. Block 1, 2, 3, 4 all match. Hostile-source guardrail present (untested branch). System-subtype Block 3 epistemic-frame variant present (untested branch). All three Block 4 type variants present (only `human` exercised so far).

User prompt matches spec.

Configuration: spec says Sonnet 4.6 (or Opus for complex figures), temperature 0.2, max_tokens 8192, Extended Thinking with budget 10000. My runner uses Opus 4.7, temperature 1.0, max_tokens 24000, adaptive thinking. **Deviations:**
- **Opus instead of Sonnet:** intentional — both Arendt and Plato are "complex figures" per spec's allowance.
- **Temperature 1.0 instead of 0.2:** Anthropic requires temperature=1.0 when extended thinking is enabled. The spec's 0.2 was written before this constraint existed.
- **max_tokens 24000 instead of 8192:** I bumped this when Pass 3 truncated mid-JSON at 16K. Pass 2 itself doesn't need it but the helper is shared.
- **Adaptive thinking instead of budget=10000:** Anthropic deprecated `thinking.type=enabled` in favor of `thinking.type=adaptive`, which doesn't accept budget_tokens. The spec's "budget: 10000" can't be expressed under adaptive mode.

These are all forced by API evolution since the spec was written, not architectural choices. Should update the spec.

## Section 8: Pass 3 — PARTIAL

System prompt is faithful — all 4 blocks match the spec, all 3 voice_mode branches present, all 3 type-branch Block 4 variants present, hostile-source guardrails in Block 2.

**Real deviations:**

1. **ChatGPT DR conditional supplement is not implemented.** Spec specifies firing OpenAI DR when ANY of: `needs_dr_supplement=true`, dossier INTELLECTUAL FRAMEWORK <500 words, `voice_mode="observational"`. My runner passes `chatgpt_supplement=None` unconditionally. The user prompt template has `{% if chatgpt_supplement %}...{% endif %}` so the rendering is correct — just no supplement is ever generated.

   **Reason:** OpenAI quota was exceeded during Plato run. Was unblocking, not architectural.

   **Real consequence:** when we run Marley or Ibn Battuta (observational), this branch should fire automatically and the supplement matters. Until OpenAI is restored, those voices will run without DR depth — known weakness flagged.

2. **Same temperature/max_tokens/thinking deviations as Pass 2** (forced by API evolution).
</content>

## Section 9: Pass 4a — PARTIAL

System prompt is faithful — Block 1 matches, the non-human Block 1 addition is present, Block 2 has the corpus-grounding guardrail, the hostile-source priority ladder is present (untested), the musical-voice corpus_constraint variant is present (untested), the system-entity voice variant is present (untested).

User prompt matches spec verbatim.

**Real deviation: 80K-character cap on `{{primary_texts}}` block.** Spec doesn't mention any cap. The runner's `_build_primary_texts_block` function caps the concatenated primary text at 80,000 characters. Plato's 5 fetched dialogues totaled 1.94 MB; without the cap, Pass 4a's user prompt would exceed Claude's context budget (200K tokens at the time of writing).

**Why this matters for fidelity:** the slice is naive. It takes the first 80K characters from the first source, then continues into the next source, etc. This means Republic Book I gets covered but Republic Books V-X (where the philosopher-king and Cave allegory live) might not. For Plato this happened to land in a sweet spot because Republic Book I has the famous Thrasymachus exchange — but it's luck, not curation.

**Better implementation:** Pass 1c should support per-source excerpt selection (e.g., "fetch Republic, take Books I, V, VII, X" instead of "fetch full Republic and slice the first 80K"). Or Pass 4a could ask Claude to pick which sections of which sources to read, then a second call with just those.

**Acceptable for current state** because Plato got lucky and the corpus-grounded test passed (model referenced Thrasymachus blushing, city of pigs — real Republic I/II material). Should improve before scaling.

## Section 10: Pass 4b — VERBATIM FAITHFUL

System prompt and user prompt both match spec verbatim. Block 4 has all 3 type variants. Configuration matches: Sonnet 4.6, temperature 0.2, max_tokens 6144 — these are the spec's exact values, no thinking required so no API-forced deviations.

## Section 11: Pass 5 — PARTIAL (real bug)

System prompt matches spec — voice_mode branching correct, Block 4 type variants present, OUTPUT REGISTER guardrail present.

**Real bug in user prompt.** Spec user prompt is:

```
Previously completed fields (summary):
{{pass_2_3_4_summary}}

Full constitution and reasoning method for reference:
{{constitution}}
{{reasoning_method}}

Produce 4 Persona Card engagement fields. Output as JSON.
```

My `persona_pass_5_user.md` is:

```
Previously completed fields (summary):
{{ pass_2_3_4_summary }}

Produce 4 Persona Card engagement fields (bold_engagement_topics, ...).
```

I dropped the `{{constitution}}` and `{{reasoning_method}}` references. **The spec explicitly wants the FULL versions because Pass 5 synthesizes from constitution and reasoning_method, and the CT compression strips the operational notes.** This is the kind of detail that compression was specifically designed to drop.

**Real consequence:** Plato's Pass 5 output (`bold_engagement_topics`, `default_questions`, `disagreement_protocol`, `unique_contribution`) was probably weaker than it should have been because it had to work from the compressed summary alone. The output looked good in inspection ("I insist on the question beneath the question") but it might have been even more grounded with full constitution access.

**Fix:** add `constitution` and `reasoning_method` parameters to the Pass 5 render call in the runner, update `persona_pass_5_user.md` to include them. ~5 lines of code. Should be done before next voice runs Pass 5.

## Section 12: Pass 6 — PARTIAL

System prompt is faithful — selection criteria, purpose tags, Tier 1/Tier 2 ordering, paraphrasing guidance, musical-voice variant — all match spec. The output JSON structure I specify (`{corpus_metadata, passages: [{id, source, header, text, purpose_tag, why_selected}]}`) is more structured than the spec's loose "JSON array" requirement. **Acceptable enhancement** — gives downstream consumers a stable schema.

User prompt deviates somewhat:

| Spec | My implementation |
|---|---|
| Includes `{{merged_dossier}}` for context | Doesn't pass it |
| Includes `{{constitution}}, {{concept_lexicon}}, {{reasoning_method}}` | Doesn't pass them |
| Includes `{{rhetorical_mode}}, {{characteristic_moves}}, {{register_and_tone}}` | Doesn't pass them |
| Has `{{primary_texts}}` and `{{pass_2_3_4a_summary}}` | Has these too |

**Same shape of bug as Pass 5** — I rely on the CT summary to carry context that the spec wants passed in full. For Pass 6 (a selection task that needs to know what makes a passage worth selecting), the operational notes from the constitution and the voice's distinctive moves are exactly the kind of context the compression strips.

**Fix:** richer user prompt template + corresponding render call updates. ~10 lines.

**HALT condition handling:** spec says when `{{primary_texts}}` is unavailable, set `curated_corpus_passages: "BLOCKED — awaiting Node 1c manual provision"` in the card. My runner returns `{"status": "HALTED", "reason": "...", "fields": {}}` and the assembled card doesn't get a `curated_corpus_passages` key at all. **Functionally equivalent** (both say "this didn't run") but the spec's pattern is better for consistency — every card has the field, with the BLOCKED placeholder making the issue immediately visible.
</content>

## Section 13: Final assembled JSON — PARTIAL

Spec specifies a flat JSON with all 37 card fields at root level plus a `metadata` block:

```json
{
  "voice_name": "...",
  "voice_mode": "...",
  "pipeline_version": "3.7",
  "generated_date": "...",
  
  "council_member_name": "...",
  ... 35 more flat fields ...,
  
  "continuity_block_if_night_2": null,
  "continuity_block_artifact_if_night_2": null,
  
  "metadata": {
    "passes_completed": [...],
    "validation_status": "...",
    "revision_loops": 0,
    "tools_used": [...],
    "voice_basis": "corpus-based",
    "hostile_sources": false,
    "corpus_constraint": "full",
    "subtype": null,
    "deployment_context": "{{conference_context}}",
    "human_review_status": "pending"
  }
}
```

My runner produces:

```json
{
  "voice_name": "...",
  "voice_slug": "...",
  "field_counts": {"pass2": 9, "pass3": 5, ...},
  "total_fields": 34,
  "voice_basis": "corpus-based",
  "register_violations": 0,
  "card": { ...34 flat card fields... }
}
```

**Deviations:**
- Card fields are nested under `card` key instead of being at root level. **Easy fix.**
- `pipeline_version`, `generated_date`, `voice_mode` not at top level. **Easy fix.**
- `continuity_block_if_night_2` and `continuity_block_artifact_if_night_2` not initialized. These are runtime fields populated by the Voice Pipeline, not the Persona Pipeline — but the spec wants them present-with-null so consumers don't get KeyErrors. **Easy fix.**
- Metadata block: I have `voice_basis` and `register_violations`. Missing: `passes_completed`, `validation_status` (depends on Phase 3), `revision_loops` (depends on Phase 3), `tools_used`, `hostile_sources`, `corpus_constraint`, `subtype`, `deployment_context`, `human_review_status`. **Most of these are easy** (just inputs/runtime state). `validation_status` and `revision_loops` need Phase 3.

## What's NOT built (Phase 3, 4, 5)

The audit's most important finding isn't a deviation — it's an absence:

**Phase 3: Validation & Testing** — 4 sub-passes that verify the card before it ships.
- Pass 7-pre: Citation Verification — checks every quote and reference against primary texts and dossier, flags fabrications.
- Pass 7a: Cross-Model Validation — feeds the assembled card to ChatGPT or Gemini for an outside read on anachronism, consistency, voice-intellect coherence, distinctiveness, completeness, register.
- Pass 7b: Worked Provocations — generates 3-5 example provocation→response chains using `{{conference_context}}`. Produces the `worked_provocations` field.
- Pass 7c: Negative Constraints — reads Pass 7b output and refines `banned_language` and `banned_modes`.

**Phase 4: Derive** — produces the Provocateur Profile (8 fields) that drops into the runtime ai-assembly repo's `council_config.json`, plus an Evaluation Rubric (9 test prompts).

**Phase 5: Cross-Persona QC** — batch step after all voices complete. Three tests: cross-voice swap test, blind identification, same-question distinctiveness.

**Until at least Phase 3 + Phase 4 are built**, the cards we have for Plato and Arendt are pre-validation drafts and there's no Provocateur Profile to hand to the runtime — meaning even though the cards exist, the voices can't actually plug into the ai-assembly council.

## Bottom line

**Phase 1 + Phase 2 are ~85% spec-compliant.** The faithful parts are very faithful (prompt text largely verbatim from spec). The deviations cluster in three categories:

1. **Environmental** — no Gemini quota, no OpenAI mid-Plato. Not architectural choices; will resolve when keys are restored.
2. **Practical** — 80K char cap on primary_texts, no manual review gate in Pass 1c. Forced by the gap between spec and runtime reality. Should be improved but not urgent.
3. **Real bugs** — Pass 5 missing constitution+reasoning_method in user prompt; Pass 6 user prompt missing the same context fields; assembled JSON has wrong wrapper structure; metadata block is sparse. **All small, all easy to fix.**

Three untested branch sets exist (3 voice_modes × 3 types × 2 hostile flags × 2 corpus_constraints) and only one combination has been exercised. Templates are written for all combinations but they could hide branch-specific bugs that only surface at runtime.

**Phase 3 + Phase 4 are completely unbuilt.** This is the real outstanding work — without them no card is deployment-ready and no voice can join the runtime council.
</content>

---

## Addendum 2026-04-15: worked_provocations role clarification

After Phase 3 was built and validated on Plato, Matthias raised a fair
question: in what sense can AI-generated worked provocations be "right"?
The persona card itself is AI-generated; the worked provocations are
Claude-generated responses to AI-generated test questions. It's Claude
all the way down.

The honest answer: worked_provocations are not predictions of "what Plato
would have said." They are commitments — "if we deploy this voice, this
is the kind of output we expect."

But the spec was sloppy in framing them as "few-shot exemplars in the
runtime Voice Pipeline's Step 1 prompt." That framing makes them
load-bearing in a way they shouldn't be. Decision (2026-04-15):

`worked_provocations` are explicitly NOT runtime exemplars. They are:

1. **A smoke test of the assembled card** — does the 35-field spec
   actually cohere into a voice when asked to do work?
2. **A diagnostic surface for Pass 7c** — Pass 7c reads them to surface
   failure patterns and refine `banned_language` and `banned_modes`.
3. **A pre-runtime artifact for human review** — anyone evaluating the
   completed card can read 4 example provocations to immediately know
   what kind of voice they're approving.

The persona card is the contract. The provocations are the smoke test.

This decision is documented in:
- `flows/shared/prompts/persona_pass_7b_provocations.md` (header comment)
- `run_persona_pipeline.py` (assembled JSON `metadata.worked_provocations_role`)
- `HANDOFF.md` (this repo)
- `ai-assembly/flows/voice/README.md` (runtime repo, prevents accidental
  few-shot wiring when the Voice Pipeline gets built)
</content>
