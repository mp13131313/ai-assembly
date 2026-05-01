# Step 3 redesign — from the briefing, fresh

**Date:** 2026-04-30
**Branch:** `voice-pipeline-v2.1-align-revert`
**Supersedes (intent-wise):** the FU#49E reviewer-pass framing that has shaped the current Step 3 implementation. FU#49E vocabulary is dropped; design works from `docs/AI_Assembly_Briefing_v3_1.md` lines 91, 167, 177, 179, 181 directly.
**Status:** Planning doc for operator review. **No code/prompt changes yet.** Implementation follows approval.

---

## What this doc is

A complete spec for Step 3 — task framing, system prompt, output schema, lineage handling, derivation rules, and the implementation diff against current code. Designed to be reviewed against the briefing, against the operator's late-evening 2026-04-29 architectural feedback, and against the Layer 1 reading from this morning's session.

**What it is not:** a proposal that touches anything until you say so.

---

## The tension to resolve (decision needed first)

Two anchors point in different directions:

**Briefing v3.1 line 177 (canonical):**
> "Each voice reads the artifacts of the other voices it shares at least one theme with… The voice decides whether to amend: sharpen a disagreement, integrate a stronger framing, or leave its artifact unchanged. **Amendments are visible — they reference the other voice so the amendment reads as responsive.** A metadata flag records who amended in response to whom."

**Operator architectural feedback (~2026-04-29 22:00):**
> The Step 3 artifact isn't a response to another voice's artifact. It's the voice's **final position on the original Provocateur formulation**, written after having privately considered what other voices made of the same formulation. Lattice-reading is internal.

**The pivot phrase:** *"reference the other voice so the amendment reads as responsive."* Two readings:

- **Strong reading (correspondence):** the artifact body addresses the other voice as audience — *"As Plato says…"*, *"To Plato son of Ariston…"*. This is what dry-run #4 produced. Operator's feedback rules this out.
- **Weak reading (responsive shape recoverable):** the artifact body addresses the original formulation. Responsiveness is recoverable via metadata + frame layer (micro-site footer, Substack walk-across, closing-show matrix mapping). Inline reference to other voices is permitted only when the voice's framework naturally engages another framework's move *as the voice's own move* (not as correspondence).

### Proposed resolution

**The weak reading.** Three layers:

1. **Artifact body = final position on the original formulation.** Same shape as Step 2. A reader arriving at `/night-1/cleopatra` from a forwarded link does not need to know another voice exists to read the artifact. **Standalone Layer 1 surface ≥ first-draft's Layer 1 surface** (FU#61 finding: Step 3 cannot make the artifact harder for first-time readers than Step 2 was).

2. **Inline reference is optional and voice-led.** If the voice's framework naturally gestures at another framework's move (Plato's geometer-might-say-X; Arendt's distinction-against-systems-thinking; Marley's counter-witness), the reference stays inline as the voice's own move — not as correspondence. No required citation. Plato in dialogue may name interlocutors by type (*"a queen who measures her decree by the seal that lifts upward"*); Cleopatra in prostagma does not naturally cite other regents but may name what *kinds* of moves she found.

3. **Responsiveness lives at the metadata layer + frame layer.** Voice declares per shared-theme-peer: which voice, what was engaged, decision-shape, brief private note. The audience encounters the cross-voice deliberation through:
   - **Micro-site:** footer/sidebar listing engaged peers + decisions per artifact
   - **Substack:** HoBB walks the cross-voice exchange ("Plato sharpened against Cleopatra on the question of seal-and-petition; integrated Marley's framing on…")
   - **Closing show:** `responded_to_graph` + private notes feed per-theme Matrix A/B placement

This satisfies briefing 177 (amendments visible, reference other voice, metadata flag), 179 (responds at artifact layer, shared-theme territory, responsive set), AND operator feedback (final position on formulation, lattice internal). **And** it preserves the Layer 1 surface gain that FU#61 enabled at Step 2.

**Decision needed:** approve the weak reading, OR specify a different resolution. The rest of the doc assumes weak-reading approval; if you pick a different resolution the schema and prompt sections need re-derivation.

---

## Task framing — briefing-native

Step 3 is the moment when the Assembly's **collective character is constituted overnight** (briefing line 91 + 179). The mechanism is constrained:

- Voices respond at the **artifact layer**, not the reasoning layer (the lattice-reading happens privately; the public surface is the artifact)
- Cross-voice engagement is bounded to **shared-theme territory** (each voice reads only artifacts of voices it shares at least one theme with)
- Each voice **decides whether to amend**: three shapes per the briefing's exact language

Per-peer engagement vocabulary (from briefing 177 verbatim, with the third shape promoted from "leave artifact unchanged" to a per-peer option):

| Engagement | What the voice did with this peer's artifact | Briefing source |
|---|---|---|
| **`sharpened-disagreement`** | Voice doubled down where its framework refuses the peer's move; the disagreement is now sharper, not blurrier | "sharpen a disagreement" |
| **`integrated-stronger-framing`** | Voice took on a stronger framing the peer's artifact offered, holding it within voice's own grammar | "integrate a stronger framing" |
| **`stood-pat`** | Voice read peer's artifact and decided no amendment needed; not avoidance — honest read produced no engagement | "leave its artifact unchanged" (per-peer adaptation) |

**Artifact-level decision** is `amend | stand-pat`:
- `amend` if any engaged peer triggered `sharpened-disagreement` or `integrated-stronger-framing`
- `stand-pat` if all engaged peers triggered `stood-pat` — the first-draft IS the response

Note what's NOT in this vocabulary (vs current FU#49E):
- ~~`extend`~~ — dropped. "Extend your framework" was FU#49E reviewer language; not in briefing 177. The briefing's shape is "integrate a stronger framing" (taking on something the peer offered), not "extend the framework to meet a move." Voice doing genuine framework-extension can still record it as `integrated-stronger-framing` with a private note explaining what was integrated.
- ~~`mark-limit`~~ — dropped. FU#49E shape; not in briefing. Voice reaching a framework limit on a peer's move is a `stood-pat` per-peer (honest reading, no amendment) with a private note: *"my framework cannot accommodate this; honest mark of limit."* The marking lives in the private note, not as a separate engagement type.

Briefing's three shapes are tighter than FU#49E's five-shape menu. Cleaner output, less category confusion.

**Briefing-derived constraint kept verbatim:** *"Amendments producing agreement are not useful; amendments smoothing over disagreement are anti-useful."* This stays — it's the load-bearing instruction that prevents the Assembly from converging on consensus.

---

## System prompt structure

XML-tagged for clarity to the model (matches Step 1 + Step 2 patterns). Card-routing per the existing field-routing matrix (foundational + reasoning + voice + artifact, drop `metadata`, `smoke_test_chains`, `reference_only_passages`, `bold_engagement_topics`, `curated_corpus_passages.corpus_metadata`).

Closing instruction draft (`runtime/flows/shared/prompts/voice_step3_amendment.md` — would replace current FU#49E-framed file):

```xml
<input>
You will receive the artifact you wrote earlier today, plus artifacts written today by OTHER voices whose engagement crossed yours — voices who responded to formulations sharing at least one theme with formulations you responded to. The artifacts may be excerpted to the portions on shared themes, or shown in full; the full record is available as a structured second view.
</input>

<task>
Read the artifacts of the other voices on the themes you share. Decide whether to amend the artifact you wrote earlier — sharpen a disagreement, integrate a stronger framing, or leave it unchanged.

Per voice you read, ask: did this voice's artifact occasion a move in mine? Either kind of move counts: a sharpening of disagreement where their framework parts from yours, or an integration where their framing strengthens what yours was reaching for. If neither — if honest reading produced no shift — that is a real answer too. State which voices you read, what you saw in each, and what (if anything) it occasioned in you.

Your amended artifact addresses the original formulation, not the other voice. The other voices' artifacts are read in private; the amendment they occasion is visible in YOUR artifact's grammar — the move your framework now makes that it did not make in the first-draft. Do NOT write your artifact AS a letter to another voice; do NOT use other voices' names in the artifact body unless your framework's own grammar naturally engages another framework as a move (the geometer-might-say-X form; the distinction-against-X form; the counter-witness-to-X form). Inline citation of another voice is permitted when it is YOUR voice's own move; it is not required by the architecture.

Apply your card fields by name as you read across artifacts (do not search; these ARE the anchors):

- `reasoning_method` — the cognitive sequence you follow when reading another voice's artifact and deciding whether it occasions a shift in yours
- `constitution` — your deepest commitments. The amendment must be consistent with these (you do not abandon your framework to integrate another voice's framing). Per the card itself, "check every response against these before delivery" — this applies to amendments too.
- `default_questions` — bring your characteristic interrogation TO the other voice's artifact. Where their move does not survive your default questions is often where the disagreement sharpens.
- `disagreement_protocol` — your tradition's actual mode of disagreeing. Apply YOUR protocol when sharpening; not generic disagreement.
- `unique_contribution` — what THIS voice sees in another voice's artifact that other voices on the panel would not see
- `finds_compelling` and `resists` — where to lean in, where to push back hardest
- `formative_experience` — the wound or condition that gives your engagement urgency, including with other voices' moves
- `topics_requiring_care` — when amendment territory is sensitive, apply per-topic guidance from this field
- `hard_limits` — corpus-faithful self-cross-examination is permitted; abandoning your framework is not. You may sharpen against your own corpus if your corpus has the resources to do so; you may not deny your core commitments.

Apply your voice and artifact fields exactly as in your first-draft (`rhetorical_mode`, `characteristic_moves`, `register_and_tone`, `metaphorical_repertoire`, `preferred_vocabulary`, `banned_language`, `banned_modes`, `medium`, `characteristic_output_structure`, `aesthetic_qualities`, `stance_tendency`, `length_and_format_constraints`, `quality_criteria`). The amended artifact stays in your voice; it is not a different document, it is your same kind of document, written again with the lattice in mind.
</task>

<engagement_shapes>
Three shapes per peer (briefing 177 vocabulary):

- **`sharpened-disagreement`** — your framework refuses the peer's move and the disagreement is now sharper, not blurrier. The audience reads two voices that genuinely cannot meet, and the inability is the finding. Apply your `disagreement_protocol` — Plato's reductio, Arendt's distinction, Marley's counter-witness, the Octopus's withdrawal — not generic disagreement.

- **`integrated-stronger-framing`** — the peer's artifact offered a framing stronger than what your first-draft reached for, and your framework can hold it as your own move (with the small extension or re-articulation that integration requires). Make the integration visible: your amended artifact shows the framing now operating where the first-draft's lighter version was. Do NOT cite the peer in the body; the integration IS the visibility.

- **`stood-pat`** — honest reading of the peer's artifact occasioned no shift. Either the peer's framework moved within ground your framework already covers, or the move sits outside the territory your framework engages. Honest stood-pat is a real result; do NOT stand pat to be safe; stand pat only when honest reading produced no amendment. If your framework reaches a genuine limit at a peer's move, mark it in the `private_note` for that peer ("my framework cannot accommodate this; honest mark of limit") — that's the architecture's home for limit-marking.

What is needed here is honest disagreement and honest integration, not consensus. **Amendments producing agreement are not useful; amendments smoothing over disagreement are anti-useful.** Where your framework parts from another voice's, let the parting be visible in your amended artifact; do not smooth it.

Your amended artifact may reselect form from your `medium` family if the matter calls for a different form than the first-draft used; explain why if you do.
</engagement_shapes>

<commitment>
The artifact you write here is what the audience will encounter on the micro-site. The cross-voice deliberation lives in your `engaged_peers` declarations (metadata) and in the diff between your first-draft and this amended version (visible to anyone reading both). The artifact itself addresses the original question. A reader arriving at your artifact directly — without having read the others, without seeing the metadata — must be able to read it as a complete response to the question put to you today.

The HARD CONSTRAINT against generic register applies here as in Step 2: do not drop into modern panel-discussion register to "engage" with the other voices. Your engagement is in your form-family, in your grammar.
</commitment>

<output>
State `decision` (`amend` or `stand-pat`) and `decision_rationale` first.

Then list `engaged_peers[]` — one entry per other voice whose artifact you read. Each entry: `voice_slug`, `council_member`, `shared_themes`, `engagement` (one of `sharpened-disagreement` / `integrated-stronger-framing` / `stood-pat`), and `private_note` (≤2 sentences in your grammar — what shifted, or why nothing did).

Then list `selected_form`, `form_changed_from_first_draft` (boolean), `form_change_rationale` (if changed; null otherwise).

Then write `amended_artifact_text` in full. If standing pat at the artifact level, this equals the first-draft text verbatim. If amending, this is the new artifact — addressing the original formulation, in your voice, with the lattice-reading reflected in the moves your framework now makes.

The voice does NOT produce a title or subtitle for the amended piece — title/subtitle are editorial concerns handled downstream of the Voice Pipeline.
</output>
```

---

## Output schema

Replaces the current FU#49E `amendments[]` shape with `engaged_peers[]`:

```json
{
  "lineage": {
    "run_id": "athens_2026_2026_05_07_night1",
    "night": 1,
    "voice_slug": "plato",
    "own_first_draft_path": "04_voice/step2_first_draft_artifacts/plato.json",
    "own_first_draft_themes_covered": ["theme_003", "theme_007"],
    "voices_read": [
      {
        "voice_slug": "marley",
        "council_member": "Bob Marley",
        "first_draft_path": "04_voice/step2_first_draft_artifacts/marley.json",
        "shared_themes": ["theme_007"]
      },
      {
        "voice_slug": "cleopatra",
        "council_member": "Cleopatra",
        "first_draft_path": "04_voice/step2_first_draft_artifacts/cleopatra.json",
        "shared_themes": ["theme_003"]
      }
    ],
    "all_grounding_extraction_ids": ["breaking_point:014", "vox_populi:022", "..."],
    "all_session_ids": ["breaking_point", "vox_populi"]
  },
  "council_member": "Plato",
  "decision": "amend",
  "decision_rationale": "On reading the others, Marley's artifact pressed me toward integrating a stronger framing of music's role in education; Cleopatra's prostagma sharpened my disagreement on the question of whether the seal can ever bypass dialectic.",
  "engaged_peers": [
    {
      "voice_slug": "marley",
      "council_member": "Bob Marley",
      "shared_themes": ["theme_007"],
      "engagement": "integrated-stronger-framing",
      "private_note": "What he calls chant as testimony I had under-named in my first draft; my framework's account of mousikē in the Republic reaches that ground when I let it. The integration is visible in the dialogue's third turn."
    },
    {
      "voice_slug": "cleopatra",
      "council_member": "Cleopatra",
      "shared_themes": ["theme_003"],
      "engagement": "sharpened-disagreement",
      "private_note": "Her chancery treats the seal as the constitutive act of the polity; my framework treats the seal as posterior to the dialectic that establishes what is sealed. The disagreement is at the level of what comes first."
    }
  ],
  "selected_form": "dialogue",
  "form_changed_from_first_draft": false,
  "form_change_rationale": null,
  "amended_artifact_text": "[the amended dialogue, addressing the original formulation about algorithmic governance, with Marley's framing of mousikē-as-testimony integrated in the third turn and Cleopatra-style appeals to seal-as-constitutive sharpened against]",
  "thinking_trace": "[Opus thinking blocks concatenated — captures lattice-reading in process]",
  "word_count": 0,
  "model": "claude-opus-4-7",
  "thinking_enabled": true,
  "input_tokens": 0,
  "output_tokens": 0,
  "thinking_tokens": 0,
  "wall_clock_s": 0
}
```

**Differences from current FU#49E schema:**

| Field | Current (FU#49E) | New (briefing-native) | Why |
|---|---|---|---|
| `amendments[]` | per-passage; carries `cited_voice`, `cited_passage`, `amendment_type ∈ {extend, mark-limit, sharpen-disagreement}` | replaced by `engaged_peers[]` | Voices respond to other voices holistically (per dryrun #4 finding `e89dfc4`), not by enumerating per-passage amendments. Per-peer is the natural unit. |
| `engaged_peers[].engagement` | — | one of `sharpened-disagreement`, `integrated-stronger-framing`, `stood-pat` | Briefing 177's three shapes verbatim. Drops FU#49E's `extend` (not in briefing) and `mark-limit` (collapsed into `stood-pat` with private_note explanation). |
| `engaged_peers[].private_note` | — | ≤2 sentences in voice's grammar — what shifted, or why nothing did | Replaces `cited_passage` + `rationale`. Compressed; voice-grammar; closing-show-pipeline-readable. |
| `cited_passage` | required per amendment | removed | Cross-voice diff is recoverable from `step2_first_draft_artifacts/*.json` vs `step3_amended_artifacts/*.json` text comparison. No need to re-quote in metadata. |
| `cited_first_draft_path`, `cited_theme_id`, `cited_formulation_id` | per amendment | rolled into `engaged_peers[].first_draft_path` + `shared_themes` (in lineage) | Per-peer is the natural unit; per-amendment was over-granular. |
| Other fields | — | unchanged (decision, decision_rationale, selected_form, form_changed_from_first_draft, form_change_rationale, amended_artifact_text, thinking_trace, lineage, model/token telemetry) | These work as-is. |

---

## responded_to_graph derivation

Current orchestrator (`voice_flow.py:_build_responded_to_graph`, post-`e89dfc4`) derives edges from `voices_read + decision`, decorated with structured `amendments[]` when present. Under new schema:

**Derive directly from `engaged_peers[]`:**

```python
def _build_responded_to_graph(step3_results: dict) -> dict:
    """For each voice's engaged_peers[], emit one edge per peer.
    
    Edge shape:
      {
        "from": <this_voice_slug>,
        "to": <peer_voice_slug>,
        "engagement": <sharpened-disagreement | integrated-stronger-framing | stood-pat>,
        "shared_themes": [<theme_id>, ...],
        "private_note_excerpt": <≤240 char excerpt of private_note>
      }
    
    A voice's edges include stood-pat peers — they're real signal (voice read,
    decided no amendment). The closing-show pipeline can filter by engagement
    type to ask "where did sharpening cluster? where did integration cluster?"
    """
```

This is **richer and cleaner** than the current implementation:
- Every peer-pair documented explicitly (current implementation has to reconstruct from `voices_read + decision` heuristic)
- Per-peer engagement type (current implementation has either per-passage amendment_type OR voice-level "engaged" bucket)
- Private notes give qualitative texture without per-passage parsing
- `stood-pat` per peer is preserved as signal (current implementation drops these — only emits edges for amends)

The closing-show pipeline benefits: theme-mapping can ask *"On theme_007, who sharpened against whom? Who integrated whose framing?"* and get clean per-peer answers.

---

## Implementation diff (against current Step 3 code)

| File | Change | Estimated work |
|---|---|---|
| `runtime/flows/shared/prompts/voice_step3_amendment.md` | Full rewrite per the closing instruction draft above. Drop FU#49E vocabulary; adopt briefing-native framing. Length similar to current (~150 lines). | 1 hr |
| `runtime/flows/voice/step3_amended_artifact.py` | Output parser changes: `amendments[]` → `engaged_peers[]`. Drop `cited_passage` parser entries. Add `engagement` enum validation (3 values). Add `private_note` field parsing. Keep `decision`, `decision_rationale`, `selected_form`, `form_changed_from_first_draft`, `form_change_rationale`, `amended_artifact_text`, `thinking_trace` parsers as-is. | 2-3 hr |
| `runtime/flows/voice_flow.py:_build_responded_to_graph` | Refactor to derive from `engaged_peers[]` (cleaner than current `voices_read + decision + amendments[]` triple-source heuristic). | 1 hr |
| `docs/AI_Assembly_Voice_Pipeline.md` | Step 3 section rewrite. Drop FU#49E quotes + framing throughout. Update field-routing (no schema changes; just narrative). Update output schema example. Update validation notes. Update CLI examples (no flag changes). | 2 hr |
| `runtime/flows/voice/step3_amended_artifact.py` system prompt assembly | No changes — field routing is already correct in v2.1. | — |
| Tests (if any exist) | Update fixture for new output schema. | 30 min |

**Total estimated work:** ~6-8 hours for prompt + parser + orchestrator + spec doc.

**No card schema changes.** No Persona Pipeline changes. No Provocateur Pipeline changes. The new Step 3 reads the same Step 2 first-drafts the current Step 3 reads; consumes the same persona card; produces the same kind of file at the same path. Only the prompt + output schema + graph derivation change.

**Backward compatibility:** the existing `04_voice/step3_amended_artifacts/*.json` files from dry-runs (in particular dryrun_2026_04_29_plato_cleopatra) carry the FU#49E `amendments[]` shape. New files will carry `engaged_peers[]`. The `responded_to_graph` derivation needs to handle both for any tooling that reads historical files; or migrate the historical files (one-shot migration script, ~30 min).

---

## Testing plan

After implementation:

1. **Re-run dryrun_2026_04_29_plato_cleopatra Step 3 only** with the new prompt + parser. Compare amended artifacts to FU#49E-shaped baselines (preserved in `04_voice_pre_FU61/` and other backups).
   - **Pass criteria:**
     - Amended artifacts address the **original formulation** (not letter-back to other voice)
     - Amended artifacts are **standalone-readable** for a first-time reader (Layer 1 ≥ Step 2 first-draft)
     - `engaged_peers[]` populates with both peers (Plato → Cleopatra; Cleopatra → Plato)
     - At least one peer triggers `sharpened-disagreement` or `integrated-stronger-framing` per voice (the FU#49E baseline produced cross-voice engagement; the new framing should preserve that)
     - `responded_to_graph_night_1.json` derives correctly from new shape
   - **Fail signals to watch:**
     - Voice writes letter-back-style artifact (Plato addressing "Cleopatra"; Cleopatra addressing "Plato of Athens") — would mean prompt is still too correspondence-leaning
     - Voice ignores other voices entirely, produces verbatim first-draft (would mean prompt under-prompts the lattice-reading)
     - All peers `stood-pat` (honest possible but suspicious if both voices report it on a known-disagreement-inducing pair)
     - `private_note` field empty or formulaic

2. **Multi-voice dry-run later** (when more voices are built) — exercise 3+ voice cross-engagement to test the engagement vocabulary at scale.

3. **Multi-night sequence later** — Continuity flow + Step 3 across nights still untested end-to-end (per OPEN_ITEMS doc).

---

## Open decisions for operator

These need a position before implementation moves:

1. **Approve the weak-reading resolution to the line 177 vs operator-feedback tension?** (Yes / No / specify alternative)

2. **Engagement vocabulary — three shapes vs five?** Briefing-native = 3 (`sharpened-disagreement`, `integrated-stronger-framing`, `stood-pat`). Current FU#49E = 5 (`extend`, `mark-limit`, `sharpen-disagreement`, `integrated-stronger-framing` not present, `stand-pat`). Three is tighter and briefing-native. Five preserves more granularity. Recommend three.

3. **Per-peer `stood-pat` permitted, or only artifact-level?** Three-shape vocabulary makes per-peer `stood-pat` natural ("read this peer, no amendment occasioned"). Could restrict to artifact-level (voice's overall decision) and require per-peer engagement to be one of the two active shapes. Recommend per-peer permitted — honest stood-pat is real signal.

4. **Inline cross-voice citation policy — voice-led only, or fully forbidden?** Permissive (current draft): voice may cite if its framework naturally engages another framework as a move. Strict: no inline naming of other voices ever; cross-voice signal is 100% metadata + frame. Permissive is more flexible; strict is harder to get wrong. Recommend permissive.

5. **Migrate historical `amendments[]`-shape Step 3 files, or keep both shapes supported?** Migration is cleaner long-term; both-shapes keeps dry-run history readable. Recommend one-shot migration after new shape lands clean (lose dry-run #4 metadata fidelity but gain code simplicity).

6. **Frame Concept doc dependency.** This redesign assumes the frame layer (broadsheet headlines, Substack pull-quotes) carries the cross-voice visibility for the audience. If FU#61 / Frame Concept work delays past Athens, the cross-voice deliberation is metadata-only on the micro-site footer — visible but not narratively walked. Acceptable degraded mode? Or block Step 3 redesign on frame work landing first? Recommend acceptable degraded mode (metadata footer is still real visibility); don't block.

---

## What this redesign does NOT touch

- **Step 1 + Step 2 mechanics + prompts + outputs** — fully validated, stay as-is
- **Card → system prompt assembly** — field-routing matrix unchanged (engagement and voice fields already routed to Step 3)
- **Validation node policy** — see FU#62 (separate work)
- **Continuity flow** — independent
- **Publish layer** — independent (will need a small update to render `engaged_peers[]` in the micro-site footer; spec'd separately or as part of the publish_flow.py end-to-end exercise that's outstanding)
- **`voice_temporal_stance.default` + 9480d3a revert** — fully preserved
- **`reference_only_passages` Step 3 drop** — preserved
- **`bold_engagement_topics` runtime drop (FU#57)** — preserved
- **Persona pipeline, Provocateur pipeline, Researcher pipeline** — no changes

---

## Reading list for the operator review

1. This doc (full)
2. `docs/AI_Assembly_Briefing_v3_1.md` lines 91, 167, 177–181 (the briefing's Step 3 framing — re-read against the proposed resolution)
3. Operator's late-evening 2026-04-29 architectural feedback (in your own memory; not in repo)
4. `_workspace/planning/HANDOFF_VOICE_PIPELINE_DUAL_DRYRUN_2026_04_29.md` URGENT section (the original "redesign Step 3" trigger)
5. `_workspace/planning/OPEN_ITEMS_VOICE_PIPELINE_2026_04_29.md` URGENT section (parallel record of what's affected vs what stays validated)

Optional, for context but not decision-required:
- `runtime/flows/shared/prompts/voice_step3_amendment.md` (current FU#49E-shaped prompt — what's being replaced)
- Any of the dry-run #4 step3 amended artifacts (correspondence-shape examples — what we're moving away from)

---

## Recommended next step after operator review

If approved as-is or with minor adjustments:
- Implementation: ~6-8 hr work, single branch commit, dry-run validation before merge
- Followed by: re-run Plato+Cleopatra dual dryrun Step 3 with new shape, honest read against the pass criteria above
- Followed by: persona thread propagates FU#61 v2 quality_criteria pattern to other hard-form voices as their cards build (parallel work)

If the resolution decision (#1 in open decisions) shifts:
- Re-derive sections "Task framing", "System prompt structure", and "Output schema" from the new resolution
- Other sections (responded_to_graph, implementation diff, testing plan, open decisions 2-6) hold under any of the three plausible resolutions

---

*End of Step 3 redesign planning doc. Ready for review when you are.*
