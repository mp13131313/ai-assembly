# PROVOCATEUR PIPELINE — v1 → v2 Delta

**Target document:** `AI_Assembly_Provocateur_Pipeline.md`
**From:** v1 (initial conceptual spec — 4 steps, Claude Sonnet throughout)
**To:** v2 (Apr 16 2026, post-dev_msc_test v3 validation)
**Status:** Major architectural rewrite — three of the four pipeline steps changed at the structural level, with one (Selection) dropping its LLM entirely in favor of a deterministic Python algorithm

---

## Summary

The Provocateur went through three architectural iterations between v1 (the original conceptual spec) and v2 (the canonical shape validated on the `dev_msc_test` MSC 2026 test corpus):

- **v1** — Four steps, all LLM on Claude Sonnet: Triage → Selection → Formulation → Packaging. Step 3 (Formulation) ran once per theme and produced one formulation sent to all assigned members. Step 4 (Packaging) was data transformation only.

- **v2 draft** (implementation-only, never landed in spec) — Per-pair Formulation experiment: Step 3 was split so each (theme, voice) pair received its own LLM call, producing a formulation angled at that specific voice. Kept Triage and Selection as single LLM calls. This produced measurably sharper formulations but revealed that the LLM-based Selection step was the new bottleneck — both slower than Python equivalents and non-reproducible.

- **v3** (the canonical architecture — this delta's target) — Five stages. Triage is split into two parallel LLM tasks, Selection is deterministic Python with no LLM, Formulation is per-pair, Packaging is Python with two complementary views per briefing. Model upgraded to Claude Opus 4.6 with `thinking.type=adaptive` for all three LLM tasks. This matches the same upgrade the Researcher Pipeline made in v2.4, validated on the same test corpus.

The naming tension in this delta: the main spec calls this the **v2** Provocateur (matching the Persona Pipeline's v2 Card + the Researcher's v3), while the flow file's internal architecture is called **v3** (three iterations reflected in code). The spec version is what downstream roles should cite; the architecture version is internal history.


---

## Changelog entry for v2

**Location:** Top of the `Changelog` section (i.e., immediately after the "Purpose" metadata block), add a new block at the head of the document.

**New text:**

```markdown
## Changelog (v2 — Apr 16 2026)

This revision captures the architecture validated end-to-end against the MSC 2026 test corpus (`dev_msc_test`) with the Researcher Pipeline's v2.4 output. The Provocateur went through three major iterations before landing on this shape:

- **v1** (original spec) — Four steps, all LLM on Claude Sonnet: Triage → Selection → Formulation → Packaging. Step 3 ran once per theme and produced one formulation sent to all assigned members.

- **v2 draft** — Per-pair Formulation experiment: Step 3 was split so each (theme, voice) pair received its own LLM call, producing a formulation angled at that specific voice. Kept Triage and Selection as single LLM calls.

- **v3** (current, canonical) — Validated architecture. Five stages. Triage is split into two parallel LLM tasks, Selection is deterministic Python with no LLM, Formulation is per-pair, Packaging is Python with two complementary views per briefing. Model upgraded to Claude Opus 4.6 with `thinking.type=adaptive` for all three LLM tasks.

Changes from v1:

- §A through §J — see main spec body for each.
```

The §A–§J list in the main Changelog section of the Provocateur spec is the authoritative per-section summary; this delta expands each with deeper rationale and migration notes for anyone reading old v1 implementations.

---

## §A — Overview: 4-step → 5-stage architecture

**v1 structure:**

> The Provocateur works in four steps:
> 1. Triage — once: scan all themes, tag each with which council members it would activate
> 2. Selection — once: filter the triaged set, balancing for territory and per-member coverage (~3 each)
> 3. Formulation — per selected theme: write the question or proposition, aimed at the assigned members
> 4. Packaging — once: assemble per-voice briefing packages

**v2 structure:**

> The Provocateur works in five stages — three parallel LLM tasks and two deterministic Python tasks:
> 1. Stage 1A — Triage Part A (per-voice ranking): 12 parallel LLM calls, one per council member
> 2. Stage 1B — Triage Part B (theme editorial flags): 1 LLM call in parallel with Part A
> 3. Stage 2 — Selection (pure Python, no LLM): deterministic nine-step algorithm
> 4. Stage 3 — Formulation (per-pair parallel LLM calls, batched): one call per (theme, voice) pair
> 5. Stage 4 — Packaging (pure Python): two-view briefings

**Why the change.** Each of the original four steps was doing work that didn't fit neatly into one LLM call:

- Triage combined per-voice activation judgment (needs specific voice profile) with theme-level editorial judgment (needs cross-theme perspective). In practice the LLM produced shallow output on both when asked for both. Separating them gave each task its own prompt and allowed the 12 per-voice calls to run in parallel, collapsing wall time.
- Selection was a combinatorial scoring task dressed up as editorial judgment. The LLM was slow, non-reproducible, and obscured the rationale behind each assignment. Python does it in milliseconds with fully explicit rules.
- Formulation had to produce one formulation that worked for all voices assigned to a theme, forcing it to a generic altitude. Per-pair calls let each formulation aim at one specific voice's territory.
- Packaging v1 produced one structured output per voice. v2 produces two views — a ready-to-paste markdown prompt (`narrative_briefing`) and a structured reasoning surface (`full_theme_record`) — serving both the Voice Pipeline's system prompt needs and its Step 1 thinking surface.


---

## §B — Triage split into Part A (per-voice) + Part B (theme flags)

**v1 output per theme:**

```json
{
  "theme_id": "theme_001",
  "activated_members": [
    {"member": "Plato", "strength": "strong", "reason": "..."},
    {"member": "The Octopus", "strength": "moderate", "reason": "..."}
  ],
  "audience_friction": {"strength": "strong", "point": "..."},
  "fault_line": {"strength": "moderate", "description": "..."},
  "target_score": 3
}
```

**v2 Part A output per voice** (one file per council member, `triage_voices/{voice_slug}.json`):

```json
{
  "voice": "Plato",
  "ranked_themes": [
    {"theme_id": "theme_003", "activation": "strong", "is_stretch": false, "reason": "..."},
    {"theme_id": "theme_007", "activation": "moderate", "is_stretch": true, "reason": "..."}
  ],
  "flat_themes": [
    {"theme_id": "theme_011", "reason": "..."}
  ]
}
```

**v2 Part B output** (one file, `triage_flags.json`):

```json
{
  "theme_flags": [
    {
      "theme_id": "theme_003",
      "worth_surfacing": true,
      "audience_friction": "high",
      "fault_line_present": true,
      "fault_line_description": "..."
    }
  ]
}
```


**Migration notes.**

- v1 produced a single `triage.json` with one record per theme; v2 produces 12 per-voice files plus one theme-flags file. Any v1 consumer that reads `triage.json` must be updated to aggregate across the per-voice files OR read the `selection.json` output (Stage 2) which already aggregates everything the downstream stages need.
- v1's `audience_friction` was a `{strength, point}` object; v2's is a `low`/`moderate`/`high` enum attached to `triage_flags.json`. The `point` text is gone — it was never read by any downstream step in practice.
- v1's `fault_line` was a `{strength, description}` object with an enum; v2's uses a boolean `fault_line_present` + the full `fault_line_description` sentence. Simpler, and the `fault_line_description` is actually used by Stage 3 Formulation to angle toward the split.
- v1's `activated_members` list was per-theme; v2's per-voice `ranked_themes` inverts that orientation. Equivalent information, but v2's shape makes per-voice workflows (debugging one voice, re-running one voice) trivial.
- `is_stretch` is new in v2. Derived from whether the theme lands in the voice's `stretch` profile field vs. `activates_on`. Read by Selection's Step 8 (optional stretch swap).

---

## §C — Selection: LLM → deterministic Python

**v1 (LLM-based):** A single Claude Sonnet call took the Triage output + council profiles + audience profile + Night 1 context (on Night 2) and returned assignments. System prompt described balancing rules in prose; model made editorial judgment calls.

**v2 (pure Python, no LLM):** The `python_select` function in `flows/provocateur_flow.py` runs a deterministic nine-step algorithm against the Triage outputs. All tunable knobs live in `council_config.json` under `selection_parameters`.

**The nine steps:**

1. Drop themes Triage Part B vetoed (`worth_surfacing: false`)
2. Score matrix per (voice, theme): `strong → 3`, `moderate → 2`
3. Theme quality: `base_score × friction_multiplier × fault_line_multiplier`
4. Per-voice candidate lists, sorted and capped at `hard_cap_per_voice`
5. Quorum pass: drop themes with fewer than `min_members_per_theme` voices
6. Cascade: voices backfill from candidates after drops, iterate until stable
7. Force-fit minimum: any voice with zero assignments gets their highest-ranked survivor
8. Soft stretch swap: voices with zero `is_stretch` assignments get one swapped in, if quorum survives
9. Emit `assignments_by_member`, `kept_themes`, `dropped_themes`, diagnostics


**Why the switch.** Three observations during v2-draft testing:

1. **The balancing task is structurally combinatorial scoring, not editorial judgment.** LLMs are good at the latter and mediocre at the former. The LLM-based Selection was mostly reading Triage's `target_score` and re-confirming — rarely making genuinely novel editorial calls.

2. **LLM Selection was non-reproducible.** Two runs on the same inputs produced different assignments. This made the pipeline impossible to debug — a voice that got a bad assignment one night could get a good one the next without any input change.

3. **The rationale was opaque.** When the LLM dropped a theme or assigned a voice to a stretch theme, the reason was embedded in generated prose. Python makes every lever explicit: the eight `selection_parameters` knobs together determine every assignment given identical Triage output.

**What the LLM could have done that Python cannot.** Selection based on substance — e.g., "this theme is quieter in text but touches a genuine council fault line." In v2, per-voice activation scores from Triage Part A + audience_friction and fault_line_present flags from Triage Part B already encode that reading; Selection's job is just to balance, not to re-read substance. The per-pair Formulation (Stage 3) then does substance-aware work where it actually matters: angling the question at a specific voice's territory.

**Selection parameters (lives in `council_config.json`).** Full table documented in the main spec §J section. Summary:

- `activation_threshold` (default 2): minimum score to enter candidate list
- `min_members_per_theme` (default 3): quorum for theme survival
- `min_formulations_per_voice` (default 1): hard floor per voice
- `target_formulations_per_voice` (default 5): soft target (warning only)
- `hard_cap_per_voice` (default 5): upper bound
- `friction_multiplier` (default `{low:1.0, moderate:1.3, high:1.7}`)
- `fault_line_multiplier` (default `{absent:1.0, present:1.5}`)
- `stretch_swap_enabled` (default true)

---

## §D — Formulation: per-theme → per-(theme, voice) pair

**v1 structure.** Step 3 ran once per selected theme. Input: the theme with full material + profiles of all assigned members. Output: one formulation. The same formulation was sent to all assigned members.

> The same formulation goes to all assigned members — but a well-aimed question finds different entry points for each voice.

**v2 structure.** Stage 3 runs N parallel LLM calls where N = number of (theme, voice) pairs produced by Selection. Each call sees: the theme with full material + ONE member's profile + the theme's editorial flags from Part B + audience paragraph. Output: one formulation angled specifically at that member.

**Why the change.** v1's "well-aimed question finds different entry points" was aspirational but never measured well in testing. In practice, a formulation that had to work for Plato AND Bob Marley AND the Octopus had to be generic enough to span their ranges. The generic altitude weakened it for all three. Per-pair calls let Plato's formulation be about the definitional question (Socratic elenchus), Bob Marley's be about resistance (song as political witness), and the Octopus's be about distributed cognition — three genuinely different questions feeding off the same theme material.

**Migration notes.**

- v1 emitted one formulation per theme to all assigned members. v2 emits N formulations (one per (theme, voice) pair). Consumers iterating over formulations must key by the `(theme_id, member)` pair, not just `theme_id`.
- v2 batches the parallel Formulation calls (default 4 pairs per batch, 20s wait between batches) to respect Anthropic rate limits. Configurable via `PROVOCATEUR_FORMULATION_BATCH` and `PROVOCATEUR_BATCH_WAIT_S` env vars.
- Each per-pair result writes an incremental checkpoint at `formulations/{theme_id}__{voice_slug}.json`. A crash mid-Formulation loses only the in-flight batch; restart automatically skips completed pairs.

---

## §E — Formulation output schema expanded

**v1 schema** (3 fields):

```json
{
  "theme_id": "theme_001",
  "formulation_type": "question",
  "formulation": "..."
}
```


**v2 schema** (10 fields):

```json
{
  "theme_id": "theme_001",
  "member": "Plato",
  "mode": "question",
  "formulation": "...",
  "theme_display_title": "...",
  "context_narrative": "...",
  "selected_quotes": [
    {
      "extraction_id": "session:NNN",
      "quote": "...",
      "attribution": "...",
      "flavor": "assertion|reframing|open_question"
    }
  ],
  "grounding_extraction_ids": ["session:NNN", ...],
  "rationale": "..."
}
```

**Why the expansion.** v1 left Packaging to do its own narrative synthesis from the raw extractions. v2 pushes that synthesis into Formulation where the LLM already has the specific member's profile + theme material open — it's cheaper and sharper to produce the `context_narrative` and `selected_quotes` in the same call that writes the formulation.

**New field semantics.**

- `member` — the voice this formulation is aimed at. Defensive field (pipeline also tracks this in filesystem naming + the Selection assignment structure, but echoing it in the JSON makes per-pair debugging easier).
- `mode` — `question` or `proposition`. Replaces v1's `formulation_type`. See §F for the test that governs the choice.
- `theme_display_title` — the Provocateur's briefing-level title for this theme, which may differ from the Researcher's title (e.g., sharpened for the specific voice). The Researcher's own title is preserved in the `full_theme_record.theme_title_from_researcher` field in Packaging, so the voice can see the discrepancy if one exists.
- `context_narrative` — 2-3 sentences summarizing what was said on this theme in the day's sessions. What the voice reads before the formulation itself.
- `selected_quotes` — 2-4 curated verbatim quotes from the session extractions. Strict rules: must match an actual extraction ID, must be verbatim, `flavor` must match the Researcher's `lens` for that extraction (note: `open_question` with underscore, not space).
- `grounding_extraction_ids` — the specific extractions the formulation is grounded in. Used by Packaging to populate the `full_theme_record` structured view; lets a reviewer trace every claim in the formulation to its source.
- `rationale` — 1-2 sentences explaining why this formulation, for this member, at this angle. **Deliberately excluded from the briefing that reaches the voice** — passing it would prime the voice toward the Provocateur's expected answer. Kept in the per-pair checkpoint file for audit only.

---

## §F — Explicit 5-condition Proposition Test

**v1 guidance:**

> The default formulation is a QUESTION — an open inquiry that takes the day's material and angles it toward the three targets. Formulate as a PROPOSITION only when the material contains a claim so sharp and contested that crystallising it would produce stronger responses.

**v2 test** (all five must hold for proposition; any one fails → question):

1. The theme material contains a SHARP, DEBATABLE CLAIM — a specific assertion made in the room, not a topic or general theme.
2. The claim was STRONGLY ASSERTED — taken seriously by at least one speaker, with weight behind it.
3. The claim was NOT ADEQUATELY CONTESTED in the room — it sits unrefuted, ripe for the council to engage with.
4. This member has CLEAR GROUND to take a position on it — for, against, or qualifying.
5. This member would produce a SHARPER RESPONSE to a proposition than to a question on the same material. Voices with `stance_tendency: asks` rarely sharpen on propositions; voices with `stance_tendency: asserts` often do; reframers vary.

**Why the formalization.** v1's informal guidance drifted during v1 testing: Sonnet produced propositions for a majority of themes, and most of them failed at least one of the above conditions on human review. Two common failure modes:

- **Topic-as-proposition.** Themes like "the future of democracy" got crystallized into propositions like "Democracy must be re-engineered" — too broad for any voice to commit usefully.
- **Mild-to-strong conversion.** A tentative claim from one speaker would get hardened into a strong proposition the theme material didn't actually contain.

The 5-condition test specifically catches both. In v3-validation runs on `dev_msc_test`, out of ~40 pairs, the model wrote 3 propositions (7%) and 37 questions. All 3 propositions passed all 5 conditions on human review; the 37 questions were correctly chosen over propositions. v1's default-to-proposition drift did not recur.

**Migration notes.** Any v1 consumer parsing `formulation_type` should read v2's `mode` field instead (same values: `question` or `proposition`). Downstream voice behavior doesn't change — the voice responds to whatever formulation arrives.

---

## §G — Packaging: single package → two views per formulation

**v1 shape.** Per-voice briefing package containing ~3 formulations with their supporting material. Each formulation included the prompt + theme clusters + extractions ordered by lens. Single structured JSON.

**v2 shape.** Per-voice briefing file containing all the voice's formulations; each formulation has TWO complementary views:

```json
{
  "formulations": [
    {
      "theme_id": "theme_003",
      "theme_display_title": "...",
      "mode": "question",
      "narrative_briefing": "markdown string — the PROMPT for Voice Step 1",
      "full_theme_record": {
        "clusters": [...],
        "theme_title_from_researcher": "...",
        "theme_abstract_from_researcher": "...",
        "co_assigned_voices": ["Cleopatra", "Ada Lovelace"],
        "theme_flags": {...},
        "grounding_extraction_ids": [...]
      }
    }
  ]
}
```

**The two views, clarified.**

- **`narrative_briefing`** — a markdown-formatted prompt the Voice Pipeline's Step 1 call can use paste-and-go. Contains the formulation, `context_narrative`, and `selected_quotes`. This is what the voice agent reads as its user prompt.

- **`full_theme_record`** — a structured reasoning surface available to the voice's private Step 1 thinking. Contains all the raw extractions sorted by lens (assertion → reframing → open_question), the Researcher's own title and abstract, other voices assigned to the same theme, and the editorial flags. A voice with the full picture can notice positions the curated quotes left out, see counter-currents the Provocateur didn't surface, or confirm the framing was right and stay close to it.

**Why the split.** v1 gave the voice one bundle of material and trusted the voice to figure out what to use for its prompt vs. its private thinking. In practice, v2-draft testing showed voices either under-using the material (sticking too close to the formulation) or over-using it (drowning the prompt in structured data). The two-view shape makes the curation/deliberation split explicit: the `narrative_briefing` is the Provocateur's editorial curation; the `full_theme_record` is the unfiltered record the voice can range over if it wants to.


**What is deliberately NOT in the v2 briefing.**

- The voice's own profile. The Voice Pipeline agent IS the persona — it loads its full v3.7 Persona Card as its system prompt. Re-shipping profile fragments in the briefing would be redundant and risk drift between what the Voice Pipeline loads and what the Provocateur describes.
- `council_config_version`. Lives in the run's `manifest.json`, not duplicated 12×.
- `formulations_count`. Derive from `len(formulations)`.
- The Provocateur's `rationale` field. Would prime the voice toward the Provocateur's expected answer. Kept in the per-pair checkpoint file for audit.

**Migration notes.**

- v1 briefings were one JSON file per voice with everything in one structure. v2 is also one JSON file per voice, but the internal structure is different — any v1 consumer must be updated to read either `narrative_briefing` (as text) or `full_theme_record` (as structured) depending on its purpose.
- v2 writes a briefing file for **every** council member, including those with zero formulations. v1 only wrote files for voices that got assigned themes. The v2 choice makes the "who got nothing" case visible rather than silent — a voice with an empty `formulations[]` array is a signal that Triage found no ground and Force-fit had no survivors.

---

## §H — Model: Sonnet → Opus 4.6 + adaptive thinking

**v1:** "All nodes use Claude Sonnet via API."

**v2:** Claude Opus 4.6 with `thinking.type=adaptive` is the default for all three LLM tasks (Triage Part A, Triage Part B, Formulation). Selection and Packaging are Python-only. Override via `CLAUDE_MODEL` env var for Sonnet dev iteration.

**Why the upgrade.** Same reasoning as the Researcher Pipeline's v2.4 upgrade, validated on the same test corpus:

- Per-voice Triage rankings are sharper on Opus+thinking — they cite specific `activates_on` phrases rather than generic gestures.
- Theme-level editorial flags on Opus+thinking correctly identify cross-council fault lines (e.g., West-East framing, expert-vs-lay epistemic authority) that Sonnet missed.
- Per-pair Formulations on Opus+thinking reliably aim at one specific member's profile; Sonnet drifted toward generic-across-voices more often.

**Token budgets.** `max_tokens=40000` for both Triage and Formulation. This is a ceiling; thinking consumes budget before visible text is emitted, so generous ceilings prevent the "empty text stream" failure mode observed during Selection's 24K → 40K bump in earlier testing.

**Cost impact.** Per-voice Triage × 12 + theme-flags × 1 + per-pair Formulation × ~40 pairs ≈ 53 Opus calls per Night 1. Observed per-call cost during validation: $0.25–$0.45. Total Provocateur cost per night: ~$15–$25 on Opus (vs. $5–$8 on Sonnet without thinking). The cost increase is justified by the measured quality improvement on the same axes the Researcher v2.4 upgrade validated.

---

## §I — Runtime: incremental checkpointing + rate-limit batching

**v1:** Runtime behavior was unspecified. An implementation would presumably run the four steps sequentially, producing final outputs only.

**v2:** Every LLM call writes its checkpoint to disk before returning. The checkpoints ARE the cache — no `PROVOCATEUR_CACHE` flag needed.

**Per-voice Triage checkpoints.** Each of the 12 Stage 1A calls writes `triage_voices/{voice_slug}.json` before returning. On restart, already-completed voices are skipped. Stage 1B writes `triage_flags.json` similarly.

**Per-pair Formulation checkpoints.** Each Stage 3 call writes `formulations/{theme_id}__{voice_slug}.json` before returning. On restart, already-completed pairs are skipped. This is the source of truth for formulations — no consolidated `formulations.json` is written (would risk silent drift if anyone hand-edits a per-pair file).

**Rate-limit batching.** Stage 3 (Formulation) submits pairs in batches with a wait between batches:

- Default batch size: 4 pairs
- Default wait: 20 seconds between batches
- Configurable via `PROVOCATEUR_FORMULATION_BATCH` and `PROVOCATEUR_BATCH_WAIT_S` env vars

Opus 4.6 is rate-limited at 8K output tokens/min, each Formulation call produces ~3K output, so 4 concurrent calls per minute is the sustainable steady-state. If Anthropic raises the tier, increase the batch size.

**Restart behavior.** `python flows/provocateur_flow.py runs/<run>` can be run repeatedly. Each run picks up from the checkpoints on disk. To force a clean run, delete `runs/<run>/03_provocateur/` or specific checkpoint files.

**Reproducibility.** Given identical Triage inputs, Selection always produces identical assignments (pure Python). Triage and Formulation are not reproducible (LLM sampling), but their outputs are cached per-voice and per-pair, so a single pipeline run produces a single canonical set of briefings that downstream code can trust.

---

## §J — selection_parameters block in council_config.json

**v1:** No mention of tunable parameters. Selection's balancing rules were embedded in the LLM prompt as prose ("Each council member receives approximately 3 formulations"), mixed with the algorithm's intent.

**v2:** All Selection knobs live in `flows/shared/council/council_config.json` under a `selection_parameters` block. Edit the config and re-run — no code changes required.


**Parameters:**

```json
{
  "selection_parameters": {
    "activation_threshold": 2,
    "min_members_per_theme": 3,
    "min_formulations_per_voice": 1,
    "target_formulations_per_voice": 5,
    "hard_cap_per_voice": 5,
    "friction_multiplier": {"low": 1.0, "moderate": 1.3, "high": 1.7},
    "fault_line_multiplier": {"absent": 1.0, "present": 1.5},
    "stretch_swap_enabled": true
  }
}
```

**Tuning guidance for Athens.**

- `target_formulations_per_voice` is the first knob likely to need adjustment. If Night 1 produces thin briefings for narrow voices (Whanganui, Octopus), lowering this to 3 acknowledges that honesty beats force-fill.
- `friction_multiplier` and `fault_line_multiplier` are symbolic in expressing editorial priority more than numerically load-bearing. Doubling them produces different rankings only when `theme_quality` is close between competing themes. Tune only if you observe Selection consistently picking low-friction / no-fault-line themes over high-friction ones.
- `activation_threshold=2` (= "moderate") is the right default. Raising to 3 (= "strong only") over-constrains; lowering to 1 (= "any tag") makes Selection too permissive.
- `stretch_swap_enabled` can be disabled for conservative runs. For Athens, leaving it on ensures voices don't drift into only-safe-territory briefings.

**Migration notes.** v1 had no config — the balancing rules were part of the Selection prompt. v2 moves them entirely into `council_config.json`. Anyone editing v1's Selection prompt to tune balance must move those edits to the config block instead.

---

## Data flow summary (v1 vs. v2)

**v1 data flow:**

```
Researcher output (grouping.json + all_extractions.json)
  │
  ▼
[LLM] Triage  ─────────────►  triage.json (one record per theme)
  │
  ▼
[LLM] Selection  ──────────►  selection.json (assignments + drops)
  │
  ▼  (loop over selected themes)
[LLM] Formulation  ────────►  formulations.json (one per theme)
  │
  ▼
[Python] Packaging  ───────►  briefings/{voice}.json  (one per voice)
```

4 LLM calls on Night 1 (Triage + Selection + N Formulations + 0 for Packaging).

**v2 data flow:**

```
Researcher output (grouping.json + all_extractions.json)
  │
  ├──► [LLM × 12] Triage Part A  ─►  triage_voices/{voice}.json  (12 files)
  │    (parallel)
  └──► [LLM × 1]  Triage Part B  ─►  triage_flags.json           (1 file)
       (parallel with Part A)
  │
  ▼  (both complete)
[Python] Selection  ──────────────►  selection.json (assignments + diagnostics)
  │
  ▼  (parallel, batched)
[LLM × N pairs] Formulation  ────►  formulations/{theme}__{voice}.json  (N files)
  │
  ▼
[Python] Packaging  ──────────────►  briefings/{voice}.json  (one per voice)
  │
  ▼
[Python] Manifest  ───────────────►  manifest.json
```

13 + N LLM calls on Night 1 (12 per-voice Triage + 1 theme flags + N per-pair Formulations + 0 for Python stages). For `dev_msc_test` with 20 themes and typical selection output of ~40 pairs, N ≈ 40 → ~53 total LLM calls. Wall time: ~12–18 minutes on Opus 4.6 + adaptive thinking, dominated by the Formulation batches (Triage's 13 calls collapse to 1–2 minutes via parallelism).

---

## File layout changes

**v1 (implied):** A single `provocateur.py` flow file with inline prompts; output directory would contain `triage.json`, `selection.json`, `formulations.json`, `briefings/`.

**v2 (actual):**

```
flows/provocateur_flow.py                        — Prefect flow orchestrator
flows/shared/prompts/
  provocateur_triage_voice.md                    — Stage 1A system prompt (per-voice ranking)
  provocateur_triage_flags.md                    — Stage 1B system prompt (theme editorial flags)
  provocateur_formulation.md                     — Stage 3 system prompt (per-pair formulation)
  _archive/
    provocateur_triage_v1_combined.md            — v1's single Triage prompt (kept for reference)
    provocateur_selection_v1_llm.md              — v1's Selection prompt (kept for reference)
    provocateur_formulation_v1_per_theme.md      — v1's per-theme Formulation prompt
    provocateur_formulation_v2_per_pair_draft.md — v2-draft per-pair Formulation (superseded)
flows/shared/council/
  council_config.json                            — collective_landscape, audience, members[], selection_parameters
  README.md                                      — swap workflows (change the council without code changes)

Outputs per run:
runs/<run>/03_provocateur/
  triage_voices/{voice_slug}.json                — Stage 1A checkpoints (12 files)
  triage_flags.json                              — Stage 1B output
  selection.json                                 — Stage 2 output with diagnostics
  formulations/{theme_id}__{voice_slug}.json     — Stage 3 checkpoints (N files)
  briefings/{voice_slug}.json                    — Stage 4 final output (12 files)
  manifest.json                                  — run-level metadata, counts, selection_parameters_used
```

Selection and Packaging have no prompt files — they're pure Python functions (`python_select` and `package_voice_briefings`) inside the flow module.

---

## Validation notes (from `dev_msc_test`)

This architecture was validated end-to-end on the `dev_msc_test` corpus (MSC 2026 panels: Breaking Point, Vox Populi, West-West Divide — 106 extractions, 20 themes, 12 voices) with the Researcher Pipeline's v2.4 output. Key observations:

- **Triage split (1A/1B) produced sharper output than v1's combined prompt.** Per-voice rankings cited specific `activates_on` phrases from each profile (e.g., Plato ranked the "ship of state" theme strong/stretch=false citing his critique of popularity-as-knowledge; Whanganui ranked it moderate/stretch=true citing the legal-personhood angle). Editorial flags correctly identified 6 themes with cross-council fault lines that Selection's multipliers then boosted.

- **Python Selection was instant and fully deterministic.** Identical outputs across 5 repeated runs of the same Triage data. Force-fit triggered twice (narrow-territory voices Cleopatra and Whanganui on this corpus); stretch-swap triggered three times without breaking quorum. Total wall time for Selection: ~80ms.

- **Per-pair Formulation produced genuinely different angles per voice.** Two voices assigned to the same theme received formulations that differed in what they asked, not just in wording. Plato on a democracy theme asked a definitional "what is X?" question; Ibn Battuta on the same theme received a proposition about travel as political pedagogy.

- **Proposition test held.** Out of ~40 pairs, the model wrote 3 propositions (7%) and 37 questions. All three propositions passed all five conditions on human review; the 37 questions were correctly chosen over propositions. v1's default-to-proposition drift did not recur.

- **Two-view briefings read cleanly.** The markdown `narrative_briefing` is paste-ready for Voice Step 1 (3-4 quoted positions + formulation). The `full_theme_record` is dense but structured — a voice that wants more context than the curated quotes provided can drill in without parsing prose.

- **Incremental checkpointing worked.** A deliberate mid-run kill on pair 18 of 40 produced correct resume behavior: the next invocation skipped the 17 completed pairs and continued from pair 18. No data loss, no double-submission.

---

## What this delta does NOT cover

- **Night 2.** The (theme_id, member) exclusion filter for Night 2 is specified in v2 but not yet implemented in the flow. It will be a simple pre-filter applied between Selection's step 1 (veto) and step 4 (candidate lists) before the first Athens production run.

- **Cross-persona QC.** Post-Provocateur quality checks across the 12 voices (e.g., "does every voice have at least one fault-line-boosted theme?") are candidates for a Stage 5 or a pre-flight check against Selection output. Not in v2; deferred.

- **Provocateur Profile generation.** The 8-field profiles loaded as `members[]` in `council_config.json` are produced by the Persona Pipeline's Derive node (see `ai-assembly-personas` repo, Phase 4 Derive). The Provocateur Pipeline only reads them.

---

*End of delta. See `AI_Assembly_Provocateur_Pipeline.md` for the full v2 specification.*
