# THE PROVOCATEUR PIPELINE
## AI Assembly — Role Specification

**Project:** The AI Assembly · World Beautiful Business Forum · Athens · May 7–10, 2026
**Status:** Conceptual briefing — working draft (v2, post-dev_msc_test v3 validation)
**Purpose:** This document specifies the Provocateur's function, process, and design constraints in enough detail that a technical team could build and prompt it.

---

## Changelog (v2 — Apr 16 2026)

This revision captures the architecture validated end-to-end against the MSC 2026 test corpus (`dev_msc_test`) with the Researcher Pipeline's v2.4 output. The Provocateur went through three major iterations before landing on this shape:

- **v1** (original spec) — Four steps, all LLM on Claude Sonnet: Triage → Selection → Formulation → Packaging. Step 3 ran once per theme and produced one formulation sent to all assigned members.

- **v2 draft** — Per-pair Formulation experiment: Step 3 was split so each (theme, voice) pair received its own LLM call, producing a formulation angled at that specific voice. Kept Triage and Selection as single LLM calls.

- **v3** (current, canonical) — Validated architecture. Five stages. Triage is split into two parallel LLM tasks, Selection is deterministic Python with no LLM, Formulation is per-pair, Packaging is Python with two complementary views per briefing. Model upgraded to Claude Opus 4.7 with `thinking.type=adaptive` for all three LLM tasks.

Changes from v1:

- **§A** → Overview rewritten around the 5-stage architecture: Stage 1A (Triage Part A, per-voice parallel LLM calls), Stage 1B (Triage Part B, one LLM call for theme-level editorial flags), Stage 2 (Selection, pure Python deterministic algorithm, no LLM), Stage 3 (Formulation, one LLM call per (theme, voice) pair), Stage 4 (Packaging, pure Python two-view briefings).

- **§B** → Triage (§Step 1 in v1) split into two parallel tasks. Part A runs once per council member: the Provocateur reads ALL themes through ONE voice's profile and ranks where that voice has distinctive ground. Each voice's call writes an incremental checkpoint to `triage_voices/{voice_slug}.json`. Part B runs once: the Provocateur tags each theme with three editorial signals (`worth_surfacing`, `audience_friction`, `fault_line_present` + `fault_line_description`). The Part A/Part B split is deliberate: per-voice reasoning and theme-level editorial judgment are different cognitive tasks and combine poorly in a single prompt.

- **§C** → Selection (§Step 2 in v1) is now entirely deterministic Python — NO LLM call. A nine-step algorithm operates on the triage outputs: drop vetoed themes, convert activations to numeric scores, compute per-theme quality with friction + fault-line multipliers, build per-voice candidate lists capped at hard_cap, enforce per-theme quorum via cascade, force-fit any voice with zero assignments, optional soft stretch swap, emit assignments. All knobs live in `council_config.json` under `selection_parameters`. This change was made because the Selection task is structurally combinatorial scoring, not editorial judgment; an LLM was both slower and less stable than a direct algorithm, and obscured the rationale behind each assignment.

- **§D** → Formulation (§Step 3 in v1) is per-(theme, voice) pair. One LLM call writes one formulation aimed at one specific member. Two different members on the same theme receive genuinely different formulations — different in what they ask, not just in wording. The rationale: a single formulation that worked for all assigned voices had to be generic enough to span their different territories, and the result was always the weakest possible angle. Per-pair calls let each formulation aim at a specific `activates_on` territory and a specific `stance_tendency`.


- **§E** → Formulation output schema expanded. v1 emitted `{theme_id, formulation_type, formulation}`. v3 emits `{theme_id, member, mode (question|proposition), formulation, theme_display_title, context_narrative, selected_quotes[] (with strict-flavor rules), grounding_extraction_ids[], rationale}`. The extra fields exist so Packaging can build a ready-to-use narrative briefing without a second LLM call. `rationale` is a Provocateur reasoning trail — kept in per-pair checkpoint for audit, deliberately excluded from the briefing that reaches the voice node.

- **§F** → The proposition-vs-question choice is governed by an explicit **PROPOSITION TEST** with five required conditions. v1 used the informal rule "use proposition when the material contains a claim so sharp that framing it as a question would lose the force." The test in v3 formalizes this: proposition if and only if all five of (1) sharp debatable claim in theme material, (2) strongly asserted in the room, (3) not adequately contested, (4) this member has clear ground for stance, (5) this member would sharpen more on proposition than question given their `stance_tendency`. If any one condition fails, formulate as question. This catches a v1 failure mode where Sonnet produced propositions for every theme.

- **§G** → Packaging (§Step 4 in v1) now writes TWO views per formulation into each per-voice briefing file. `narrative_briefing` is the markdown PROMPT for the Voice Pipeline's Step 1 (paste-and-go) — formulation, `context_narrative`, and `selected_quotes`. `full_theme_record` is the wider REASONING SURFACE for Step 1 thinking — all clusters with full extractions sorted by lens, the Researcher's own title/abstract, co-assigned voices, theme flags, `grounding_extraction_ids`. The voice reasons over the full record while answering the curated prompt. This two-view shape supersedes v1's single-package-per-voice output.

- **§H** → Model recommendation updated from "Claude Sonnet" to "Claude Opus 4.7 with `thinking.type=adaptive`" for all three LLM tasks (Triage Part A, Triage Part B, Formulation). Selection and Packaging are Python-only. The model upgrade mirrors the same change the Researcher Pipeline made in v2.4, validated on the same test corpus.

- **§I** → Runtime behavior section added: incremental per-voice checkpoints for Triage Part A (`triage_voices/{slug}.json`), incremental per-pair checkpoints for Formulation (`formulations/{theme_id}__{slug}.json`), and batched parallel submission of Formulation calls to respect Anthropic rate limits (default batch size 4, wait 20s between batches — configurable via `PROVOCATEUR_FORMULATION_BATCH` and `PROVOCATEUR_BATCH_WAIT_S`). Restart picks up automatically from existing checkpoints; no cache flag needed.

- **§J** → New "Selection parameters" section added, documenting the `selection_parameters` block in `council_config.json`: `activation_threshold`, `min_members_per_theme`, `min_formulations_per_voice`, `target_formulations_per_voice`, `hard_cap_per_voice`, `friction_multiplier`, `fault_line_multiplier`, `stretch_swap_enabled`. These are the tunable knobs for editorial balance without code changes.

---

# Overview

The Provocateur is the second agent in the overnight pipeline. It receives the Researcher's output — an **extraction table** (per-session atomic positions, reframings, and open questions) and a **themed grouping** (those extractions clustered into themes by KJ-method affinity) — and turns it into **per-voice briefing packages** for the Assembly's council members. Each briefing contains the formulations that specific voice will respond to, with curated framing material and the full reasoning surface they can range over while thinking.

The Provocateur is the strategic, editorial agent in the pipeline. Unlike the Researcher (content-faithful, council-unaware), the Provocateur knows the council — both as a collective landscape of traditions and fault lines (for formulating where diversity activates) and as individual profiles (for assigning formulations to the voices each would activate most). It knows the audience. It makes choices designed to produce the strongest possible artifacts.

The Provocateur works in **five stages** — three parallel LLM tasks and two deterministic Python tasks:

1. **Stage 1A — Triage Part A (per-voice ranking):** 12 parallel LLM calls, one per council member. The Provocateur reads ALL themes through ONE voice's profile and ranks where that voice has distinctive ground to contribute. Reasoning ABOUT the voice using profile data — not speaking AS them. Each voice's result writes an incremental checkpoint to disk.

2. **Stage 1B — Triage Part B (theme editorial flags):** 1 LLM call in parallel with the 12 Part A calls. Tags each theme with three editorial signals: `worth_surfacing` (boolean veto), `audience_friction` (low/moderate/high), and `fault_line_present` (boolean) + `fault_line_description`. Cross-theme editorial judgment that needs the whole set at once.

3. **Stage 2 — Selection (pure Python, no LLM):** Deterministic nine-step algorithm. Drops vetoed themes, scores per voice, computes theme quality with friction + fault-line multipliers, builds per-voice candidate lists capped at hard_cap, enforces quorum via cascade, force-fits the minimum, optional stretch swap. Emits per-voice assignments. Always re-runs; not cached.

4. **Stage 3 — Formulation (per-pair parallel LLM calls, batched):** N parallel LLM calls where N is the total number of (theme, voice) pairs produced by Selection. Each call writes one formulation aimed at one specific member for one specific theme, plus narrative-briefing components. Batched to respect Anthropic rate limits. Each pair writes an incremental checkpoint.

5. **Stage 4 — Packaging (pure Python):** Assembles per-voice briefing files, each containing TWO complementary views per formulation: a markdown `narrative_briefing` (the prompt for Voice Step 1) and a structured `full_theme_record` (the wider reasoning surface for Step 1 thinking).

The Researcher's output arrives as a JSON extraction table (`all_extractions.json`) plus a JSON theme/cluster structure (`grouping.json`). The Provocateur reads both. No intermediate transformation or cleanup happens at the interface — the Researcher's output is the Provocateur's input as-is, following the Provocateur interface contract documented at the end of the Researcher Pipeline spec.

---

# What the Provocateur Knows

### 1. The Council

The Provocateur knows the council at two levels.

**Collective landscape** — a single paragraph describing the council as a whole: what traditions, eras, ontologies, and modes of knowing are represented, and where the major fault lines between them lie. Used in Triage Part B (fault-line detection) and in Formulation (angling for fault-line friction). Lives in `council_config.json`.

**Individual profiles** — eight fields per council member, derived pre-conference by the Persona Pipeline's Derive node from the completed v3.10 Persona Card. Loaded into the Provocateur's system prompts as a roster.

| Field | What it tells the Provocateur |
|---|---|
| **speaks_from** | The tradition, era, and mode of knowing this voice represents. The intellectual ground they stand on. |
| **core_commitment** | The conviction this voice would defend to the last. Not a topic — a hill they'd die on. |
| **activates_on** | The territory where the core commitment meets incoming material and produces the voice's strongest, most distinctive work. |
| **goes_flat_on** | Territory where the voice has something to say but nothing distinctive. The "don't assign" signal. |
| **stretch** | Territory adjacent to the core commitment but outside the voice's natural mode. Where the voice would have to work harder and the result is less predictable. Used as a nudge when a member's other assignments are already in safe territory — encoded as `is_stretch` flags in Triage Part A output and acted on by Selection's optional stretch-swap step. |
| **translation_range** | How well this voice handles modern concepts it never encountered (narrow / moderate / wide). Informs Triage's tolerance for flagging themes the voice can't fully reach. |
| **stance_tendency** | The posture the voice's artifacts tend to take (asserts / reframes / asks, or a phrase like refusal, synthesis, witness, provocation, lament). Used directly in Formulation's proposition test condition 5 and in angling questions vs. propositions. |
| **medium** | Artifact format (dialogue, song, testimony, shader, etc.). Used only in Packaging for display; Voice Pipeline loads it from the Persona Card, not the Provocateur's briefing. |


**Separation from the Persona Card.** The eight-field profile is a compressed view of the full v3.10 Persona Card, derived by the Persona Pipeline's Derive node. The Provocateur never loads the full card. The Voice Pipeline, downstream, loads the full card as the voice agent's own system prompt. The Provocateur and the voice agent are reading different surfaces of the same underlying persona.

### 2. The Audience

The Provocateur knows who will encounter the council's artifacts at breakfast — and targets accordingly.

**Who they are**

~750 senior business professionals, founders, designers, and creatives — predominantly European, highly educated, philosophically literate. They are embedded in the corporate system (SAP, Google, BCG, Porsche, Chanel are represented) while critiquing it. They self-selected into an event that costs €1,895 and promises no PowerPoints. They come from 40+ countries, skew 35–55, and are comfortable with foreign-language vocabulary, interdisciplinary thinking, and emotional openness unusual for a business audience.

| Field | |
|---|---|
| **Speaks from** | European humanism, Continental philosophy, design thinking, Buddhist practice, post-colonial thought. They operate from a "life-centered economy" framing — business should serve all life, not just shareholders. They are romantic reformists: critical of the system, embedded within it, committed to transforming it from within through beauty, meaning, and humaneness. |
| **Core commitment** | Business can and should be made beautiful — not abolished, but reimagined. The system is broken but salvageable. They would defend this against both revolutionaries who say burn it down and traditionalists who say nothing is wrong. |
| **Activates on** | Genuine intellectual risk within a frame they respect. Moments where their own contradictions become visible. Paradox they haven't encountered before. Felt experience over information. They are transformed by discomfort delivered with craft — not by being told what to think but by being shown what they haven't seen. The council's most alien perspectives (the Octopus, distributed intelligence, non-linguistic governance) will fascinate them precisely because they already believe more-than-human perspectives matter but have never encountered one that actually thinks differently from them. |
| **Goes flat on** | Standard progressive talking points delivered without edge: "AI is dangerous," "we need more empathy," "nature has rights." These are their priors restated. Also: academic jargon without grounding, corporate keynote register, anything that resolves too cleanly, and any formulation where both the audience and the council would be predictable. |
| **Stretch** | Where their self-awareness fails. They critique extraction while embedded in extractive systems and they know it — but knowing it hasn't changed behaviour. Their embrace of paradox has become comfortable — the aesthetic of discomfort is itself a form of complacency. "Beautiful capitalism" is still capitalism — the assumption that transformation from within is sufficient goes largely untested. They are better at dismantling systems than building new ones. Their cosmopolitanism carries a European/Western philosophical centrism despite genuine Global South engagement. Their own organisations are not democratic — they benefit from meritocracy and hierarchy while critiquing both. Whether "more-than-human democracy" is a genuine expansion of the demos or a category error that dissolves the concept — this question would genuinely unsettle them. |


**Intellectual altitude**

The audience is comfortable with philosophical concepts, poetic-intellectual framing, and unresolved questions. Formulations should be pitched at a level they would find compelling, not simplistic — even though the audience reads the council's artifacts, not the formulations themselves. The altitude of the formulation determines the altitude of the artifacts.

**The Athens context**

The event is structured as a Greek drama in five acts, grounded in democratic heritage (Pnyx walks, citizen assemblies, a funeral march for human democracy). The audience arrives primed to think about democracy's crisis. The AI Assembly operates overnight while they sleep — they encounter its output at breakfast. They are participants in the democratic experiment, not observers of it.

The audience profile is a single paragraph loaded into every Stage 1/Stage 3 LLM system prompt verbatim. It lives in `council_config.json` next to the collective landscape.

### 3. The Conceptual Terrain

The project maps governance thinking along two axes: **Power & Agency** (human↔nonhuman / many↔one) and **Change & Actor** (rupture↔progression / individual↔collective). The Provocateur uses these in Triage Part B and in Selection's theme-quality scoring as an implicit check that the surviving set covers different parts of this terrain — not to predict where responses will land, but to ensure the set isn't narrow. In v3 this is not modeled as a hard constraint; the audience_friction and fault_line_present flags plus the quality multipliers deliver the same effect.

### 4. Night 2 + Night 3 cross-night exclusion (C9, implemented 2026-05-01)

On Night 2 (and Night 3), the Provocateur receives prior night(s)' formulations and assignments and avoids repeating territory per member. Implemented as the **C9 cross-night exclusion filter** in Selection.

**Mechanism.** On Night 2/3 the runner passes `--prior-nights <run_dir>[,<run_dir>...]` to `provocateur_flow.py`. The flow loads each prior night's `selection.json` + `02_researcher/grouping.json`, builds a per-member set of normalized theme titles already assigned, and threads it through `python_select(prior_assignments_by_member=...)`. Inside Selection (Step 4), each voice's candidate list is filtered: themes whose **normalized title** matches a prior assignment for that member are dropped before quorum + cascade run.

**Why title, not theme_id.** Theme_ids are not stable across Researcher runs — each Researcher run generates fresh sequential `theme_001`..`theme_NNN` IDs from its own clusters. The spec language "exclusion list keyed on (theme_id, member)" is informal; actual implementation matches by content (normalized title — lowercased, whitespace-collapsed) so a theme with substantively the same title across nights counts as the same territory regardless of its per-night ID.

**Force-fit honors exclusions.** If a voice's entire ranked + flat lists are exclusion-filtered, the voice ends with zero assignments rather than re-deploying covered territory. Recorded in `prior_exclusions_blocked` for operator visibility — usually a signal that the conference content overlapped heavily across nights.

**Diagnostics.** `selection.json` includes `prior_exclusions_applied` (deduped list of `{voice, theme_id, title}` filtered out), `prior_exclusions_blocked` (voices whose force-fit was blocked entirely), and `prior_nights_consumed` (count of prior run_dirs loaded).

**CLI:**
```bash
# Night 1 (no priors)
python flows/provocateur_flow.py runs/athens_2026_2026_05_07_night1

# Night 2 (Night 1 priors)
python flows/provocateur_flow.py runs/athens_2026_2026_05_08_night2 \
    --prior-nights runs/athens_2026_2026_05_07_night1

# Night 3 (Nights 1 + 2 priors)
python flows/provocateur_flow.py runs/athens_2026_2026_05_09_night3 \
    --prior-nights runs/athens_2026_2026_05_07_night1,runs/athens_2026_2026_05_08_night2
```

Tests: `runtime/tests/test_provocateur_selection.py` covers the filter end-to-end (15 cases including the loader). Always pass `--prior-nights` on Athens Nights 2 + 3.

---

## Stage 1A: Triage Part A — Per-Voice Ranking

**Input:** All themes from the Researcher (titles and abstracts at theme level; cluster titles and abstracts within each theme — no raw extractions at this stage). The profile of ONE council member. The collective landscape and audience paragraph.

**Runs:** 12 parallel LLM calls, one per council member. The Provocateur reads ALL themes through this one voice's profile.

**What it produces:** A ranked list of themes for this voice. Each ranked theme carries an `activation` label (`strong` or `moderate`), a boolean `is_stretch` flag (true if this theme lands in the voice's `stretch` field rather than `activates_on`), and a one-sentence `reason`. Themes where the voice would go flat or couldn't reach go into a separate `flat_themes` list with a one-sentence reason each, so the model's full judgment is preserved for Selection even though only ranked themes participate in scoring.

**Why split from Triage Part B.** Reasoning about one voice requires holding that voice's specific profile in mind while scanning the day's themes — a pattern-match between `activates_on`/`goes_flat_on`/`stretch` and theme abstracts. Adding cross-theme editorial judgment (is this theme worth surfacing to the audience at all? does it open a fault line in the council?) pulls the model away from per-voice thinking into a different mode. The v1 combined-Triage prompt tried both at once and produced shallow activation tags + shallow editorial flags. Separating the tasks lets each prompt do one thing well.

**Why parallel.** The 12 per-voice calls are fully independent — each reads the same themes but through a different voice's profile. Parallel submission brings wall time for Triage down to roughly one call's duration (60–120s on Opus + adaptive thinking) rather than 12× that.

**Output per voice:**
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

**Checkpoint:** `runs/<run>/03_provocateur/triage_voices/{voice_slug}.json` — written atomically as each call returns. On restart, already-completed voices are skipped; only missing voices re-run.

---

## Stage 1B: Triage Part B — Theme Editorial Flags

**Input:** All themes from the Researcher (titles, abstracts, cluster titles and abstracts). The collective landscape and audience paragraph. Does NOT receive voice profiles.

**Runs:** 1 LLM call, in parallel with the 12 Part A calls.

**What it produces:** Three editorial signals per theme, spanning the whole set at once.

| Signal | Values | What it feeds |
|---|---|---|
| **worth_surfacing** | `true` / `false` | Selection's hard veto — themes marked `false` are dropped before scoring. Used for themes the audience would go flat on (restated priors, corporate keynote register, resolves-too-cleanly material). |
| **audience_friction** | `low` / `moderate` / `high` | Selection's theme-quality multiplier. Default multipliers: low=1.0, moderate=1.3, high=1.7. Tunable in `council_config.json`. |
| **fault_line_present** + **fault_line_description** | boolean + one sentence | Selection's theme-quality multiplier (absent=1.0, present=1.5) and Formulation's angling material (passed into the Formulation prompt for pairs on this theme). |

**Why one call, not per-theme.** Audience-friction and fault-line judgment both require seeing the whole set. A theme that's moderate friction in isolation may be high friction relative to the rest of the day. A fault line is a fault line precisely because it splits the council in a way that matters given what else is on offer.

**Why no voice profiles here.** Part B is asking "is this theme editorially worth our time?" — a question about the theme and the audience. Adding voice profiles pulls the model into per-voice activation reasoning, which is Part A's job.

**Output:**
```json
{
  "theme_flags": [
    {
      "theme_id": "theme_003",
      "worth_surfacing": true,
      "audience_friction": "high",
      "fault_line_present": true,
      "fault_line_description": "one-sentence description of where the council splits"
    }
  ]
}
```

**Checkpoint:** `runs/<run>/03_provocateur/triage_flags.json`.

---

## Stage 2: Selection — Deterministic Python Algorithm

**Input:** All 12 per-voice triage results (`triage_voices/*.json`), the Triage Part B flags (`triage_flags.json`), the Researcher's `grouping.json` (for theme lookup), and `council_config.json` (for `selection_parameters` and member list).

**Runs:** Pure Python, no LLM call. Always recomputed on every pipeline run — never cached, instant to re-run. Caching Selection would silently produce stale assignments when someone edits `selection_parameters` between runs.

**What it produces:** Per-voice theme assignments (~3–5 themes per voice by default), plus a `kept_themes` view (themes that survived), a `dropped_themes` list with reasons, and diagnostic blocks (`forced_fits`, `stretch_swaps`, `below_target`).

### The Nine-Step Algorithm

1. **Drop themes Triage Part B vetoed.** Any theme with `worth_surfacing: false` goes into `dropped_themes` with reason `worth_surfacing=false`. Reduces the working set.

2. **Score matrix per (voice, theme).** Convert Part A's activation labels to numeric scores: `strong → 3`, `moderate → 2`. Also record each voice's `is_stretch` flag per theme and the rank index from their `ranked_themes` list (stable tiebreaker).

3. **Theme quality.** For each surviving theme, compute:
   ```
   theme_quality = (sum of voice scores) × friction_multiplier × fault_line_multiplier
   ```
   Defaults: friction_multiplier ∈ {low:1.0, moderate:1.3, high:1.7}, fault_line_multiplier ∈ {absent:1.0, present:1.5}. Friction and fault-line come from Part B.

4. **Per-voice candidate lists, capped at hard_cap.** For each voice, filter to themes where their score ≥ `activation_threshold` (default 2 = "moderate"), sort by `(-own_score, -theme_quality, theme_id)` (own score first, then global quality, then stable ID), truncate to `hard_cap_per_voice` (default 5). This is the voice's initial assignment.

5. **Quorum pass.** A theme survives only if at least `min_members_per_theme` voices (default 3) have it assigned. Sub-quorum themes are dropped.

6. **Cascade.** When themes drop for quorum, each voice's assignment list shrinks; voices backfill from their sorted candidates (next picks) up to hard_cap. Re-check quorum. Iterate until stable (bounded at 10 iterations in implementation — converges in 1–2 in practice).

7. **Force-fit minimum.** Any voice with zero assignments after the cascade settles gets their highest-ranked surviving theme regardless of `activation_threshold`. Falls back to their `flat_themes` list if no ranked theme survives. Recorded in `forced_fits` for visibility — a voice that hit force-fit is a signal that Triage didn't find good ground for them, not a failure.

8. **Soft stretch swap.** If `stretch_swap_enabled` (default true), any voice whose final assignments contain zero `is_stretch=true` themes gets their lowest-quality assignment swapped for their highest-scoring stretch candidate — but only if doing so doesn't break quorum on the swapped-out theme. This is the nudge that prevents a voice from only receiving safe territory.

9. **Emit assignments.** Write `assignments_by_member` (voice → list of theme_ids), `kept_themes` (ordered by theme_quality desc), `dropped_themes` (with reason + stage), and diagnostic blocks.


### Selection Parameters (lives in `council_config.json`)

All knobs are declared in a single `selection_parameters` block and read by the algorithm at runtime. Edit the config and re-run — no code changes required.

| Parameter | Default | What it does |
|---|---|---|
| `activation_threshold` | 2 | Minimum per-voice score to enter that voice's candidate list. 2 = "moderate" from Triage Part A. |
| `min_members_per_theme` | 3 | Quorum. A theme with fewer than this many assigned voices is dropped. |
| `min_formulations_per_voice` | 1 | Hard floor per voice. Force-fit runs if any voice ends below this. |
| `target_formulations_per_voice` | 5 | Soft target per voice. Voices below this generate a `below_target` warning but aren't force-filled — narrow-territory voices should honestly come in below target. |
| `hard_cap_per_voice` | 5 | Upper bound on assignments per voice. Prevents one broadly-activating voice from dominating the set. |
| `friction_multiplier` | `{low:1.0, moderate:1.3, high:1.7}` | Theme-quality boost from audience friction. |
| `fault_line_multiplier` | `{absent:1.0, present:1.5}` | Theme-quality boost from council fault lines. |
| `stretch_swap_enabled` | true | Whether step 8 runs. Disable for conservative runs that don't push voices into stretch. |

**Tuning guidance.** The defaults validated well on `dev_msc_test` (12 voices, 6 themes → ~4 assignments per voice, 2-3 kept themes per voice's territory). For the Athens deployment, the first knob likely to need adjustment is `target_formulations_per_voice` — if Night 1 produces thin briefings for narrow voices, lowering this to 3 acknowledges that honesty beats force-fill. The friction and fault-line multipliers are symbolic in expressing editorial priority more than numerically load-bearing; doubling them produces different rankings only when theme_quality is close between competing themes.

### Why Python, not LLM

The v1 spec called for an LLM to balance the set. Testing in v2 showed three problems: (1) the balancing task is structurally a combinatorial optimization over numeric scores, not editorial judgment — LLMs are good at the latter and mediocre at the former; (2) an LLM produced different assignments on repeated runs of the same input, making the pipeline non-reproducible; (3) the rationale for each assignment was opaque. The Python algorithm runs in milliseconds, produces identical output for identical input, and its selection_parameters block makes every editorial lever explicit and tunable.

What the LLM-based Selection could have done that Python cannot: produce assignments that require reading the substance of a theme beyond its score. In practice, the per-voice activation scores from Triage Part A already encode that reading — the LLM-based Selection was mostly re-reading and reconfirming. Per-pair Formulation (Stage 3) then does the substance-aware work where it actually matters: angling the question at a specific voice's territory.

---

## Stage 3: Formulation — Per-(Theme, Voice) Pair

**Input:** One theme with its FULL material (theme title, abstract, clusters, all raw extractions from the Researcher with speaker, lens, context, engagement, responds_to, energy fields). One council member's profile (only this member, not the full roster). The theme's editorial flags from Triage Part B (friction level, fault-line description). Collective landscape and audience paragraph.

**Runs:** N parallel LLM calls where N is the total number of (theme, voice) pairs produced by Selection. Batched to respect Anthropic rate limits (default batch size 4, wait 20s between batches, both configurable via `PROVOCATEUR_FORMULATION_BATCH` and `PROVOCATEUR_BATCH_WAIT_S`).

**What it produces per call:** One formulation (question or proposition) aimed specifically at this member, plus the narrative-briefing components that will be delivered to them in Packaging.

### The Key Move: Aim at the Member, Not at the Theme

Two different members on the same theme should receive genuinely different formulations — different in what they ask, not just in wording. If a draft could equally well be sent to any of the council, it is a general question about the theme rather than a targeted provocation. The Formulation prompt instructs the model to rewrite in that case.

The theme material contains many possible angles. The model picks the angle that most activates this specific member and writes the formulation from there, using:

- **`activates_on`** — where the member has distinctive ground; aim here
- **`core_commitment`** — what they would defend; the formulation can press against it
- **`goes_flat_on`** — territory to avoid; if the draft lands here, rewrite
- **`stretch`** — reach for stretch when the material supports it; stretch produces the strongest artifacts
- **`stance_tendency`** (asserts / reframes / asks) — if they tend to reframe, invite reframing; if they tend to assert, invite commitment

### Three Targets (Angling)

Each formulation is angled toward three targets. The best formulation hits all three. Two of three is workable. One of three is weak.

1. **Council fault line** — formulate where this member's tradition diverges from others on the council. The `fault_line_description` from Triage Part B tells the model where the council splits.
2. **Member activation** — aim at this member's `activates_on` territory specifically.
3. **Audience friction** — aim at the audience's stretch territory. The friction level from Triage Part B tells the model how much friction this theme carries; high-friction themes should sharpen, not soften.


### The Proposition Test (Question vs. Proposition)

A formulation is either a QUESTION or a PROPOSITION. The default is a question. A proposition is chosen if AND ONLY IF all five of these conditions hold:

1. The theme material contains a **sharp, debatable CLAIM** — a specific assertion made in the room, not a topic or general theme.
2. The claim was **STRONGLY ASSERTED** — taken seriously by at least one speaker, with weight behind it.
3. The claim was **NOT ADEQUATELY CONTESTED** in the room — it sits unrefuted, ripe for the council to engage with.
4. This member has **CLEAR GROUND** to take a position on it — for, against, or qualifying.
5. This member would produce a **SHARPER RESPONSE** to a proposition than to a question on the same material. Voices with `stance_tendency: asks` rarely sharpen on propositions; voices with `stance_tendency: asserts` often do; reframers vary.

If all five hold, write a proposition. If any one fails, write a question. Length either way: one to three sentences.

### What Each Is

**Question** — an open inquiry that contains a gap, not a claim. The voice is not asked to take a stance — they are asked to go somewhere the day's conversations couldn't. A good question (a) arises directly from the theme's material, (b) lands inside this member's `activates_on` territory, (c) gives them something to push back on, extend, or reframe. A question is NOT a proposition in disguise — it does not contain its own answer.

**Proposition** — a specific, debatable statement made in the Provocateur's authorial voice, demanding a stance. Three types:
- **Fact** — "X is the case"
- **Value** — "X is better/worse than Y"
- **Policy** — "we should do X"

A proposition is NOT a question, NOT a topic, and NOT a thesis that already contains its answer.

### Failure Modes (Questions)

**Too open.** Every response is valid. No focal point, no productive divergence. *Example: "What is democracy?"*

**Too closed.** A yes/no question disguised as an open inquiry. *Example: "Should rivers have legal standing in the EU?"*

**Leading.** Contains its own answer. *Example: "Why is expanding the demos always beneficial?"*

**Poorly targeted.** Hits zero or one of the three targets. Too specific to open council fault lines (e.g. "Should the Whanganui River model be adopted in Greece?") or too abstract to activate specific members or the audience (e.g. "What is justice?").


### Failure Modes (Propositions)

**Too broad.** The voice won't commit to anything. *Example: "The future of democracy."*

**Too narrow.** The voice gives a novelty answer and moves on. Nothing feeds the larger conversation. *Example: "Athens should grant voting rights to pigeons."*

**Pre-answered.** No voice on the panel would disagree. Dead on arrival. *Example: "All beings deserve representation."*

### Output Schema (per call)

```json
{
  "theme_id": "theme_003",
  "member": "Plato",
  "mode": "question",
  "formulation": "One to three sentences. The question or proposition itself.",
  "theme_display_title": "A short evocative title for this member's briefing (may differ from the Researcher's title)",
  "context_narrative": "Two or three sentences setting up what was said on this theme today — what the audience will read before the formulation. Not an abstract; a curated framing.",
  "selected_quotes": [
    {
      "extraction_id": "session:NNN",
      "quote": "the quoted text",
      "attribution": "speaker name or role",
      "flavor": "speaking with intensity | pushing back | extending the previous point | ..."
    }
  ],
  "grounding_extraction_ids": ["session:NNN", "session:MMM"],
  "rationale": "One or two sentences explaining why this formulation, for this member, at this angle. Used for audit; deliberately NOT passed to the voice node."
}
```

**Strict-flavor rules on `selected_quotes`.** The quotes are a curated sample, not exhaustive. 2–4 quotes per formulation is the working range. `flavor` is a stage-direction-style phrase derived **only** from Researcher metadata — `energy: high` maps to phrases like "speaking with intensity", "with weight"; `engagement: challenged` maps to "pushing back", "contesting the framing"; `engagement: reinforced` maps to "extending the previous point", "building on what came before"; `lens: open_question` maps to "asking aloud", "leaving the question open"; `responds_to: <id>` maps to "responding to the previous speaker". Omit `flavor` entirely when the metadata does not support it. Visual, tonal, or interior-state phrasings ("visibly emotional", "quietly", "after a pause") are **disallowed** — the pipeline has no audio or video data to justify them. See `provocateur_formulation.md` STRICT-FLAVOR RULES section for the authoritative rules. Quotes must be attributable — never composite, never paraphrased.

**Why `rationale` is kept out of the voice's briefing.** Passing the Provocateur's rationale to the voice would prime the voice toward the Provocateur's expected answer. The voice should respond to the formulation on its own terms. The rationale stays in the per-pair checkpoint file (`formulations/{theme_id}__{slug}.json`) for audit — anyone reviewing a briefing can see what the Provocateur was aiming for, without the voice ever seeing it.

**Checkpoint:** `runs/<run>/03_provocateur/formulations/{theme_id}__{voice_slug}.json` — written atomically as each call returns. On restart, already-completed pairs are skipped; only missing pairs re-run. This is the source of truth for formulations; no consolidated file is written.

---

## Stage 4: Packaging — Two Views per Formulation

**Input:** Selection's `assignments_by_member`, all per-pair formulations from Stage 3, the Researcher's `grouping.json` and `all_extractions.json`, and the council config.

**Runs:** Pure Python, no LLM call.

**What it produces:** One briefing file per council member at `runs/<run>/03_provocateur/briefings/{voice_slug}.json`. Each briefing contains all of that voice's formulations; each formulation has TWO complementary views.

### The Two Views

**`narrative_briefing` — the PROMPT for Voice Node Step 1 (paste-and-go).**

Rendered as markdown. Contains the formulation, `context_narrative`, and `selected_quotes` — the Provocateur's curated framing of what to think about. Format:

```
THEME: {theme_display_title}

CONTEXT FROM TODAY'S SESSIONS:
{context_narrative}

EXTRACTION — positions heard today:
• "{quote_text}" ({attribution}, {flavor})
• "{quote_text}" ({attribution}, {flavor})

FORMULATION (mode: {question|proposition}):
{formulation_text}

[Full structured supporting material — theme abstract, cluster abstracts,
all raw extractions sorted by lens, theme flags — is available in the
`full_theme_record` field of this briefing entry for deeper inspection.]
```

This is what the voice's Step 1 LLM call sees as its user prompt. No parsing required — the voice agent reads it as prose and responds.

**Mode label in the FORMULATION header (added 2026-04-28 for Voice Pipeline v2 contract):** the Provocateur tags each formulation as `mode: question` or `mode: proposition` per the PROPOSITION TEST (Stage 3). The Voice Pipeline's Step 1 closing instruction has explicit logic that branches on mode (proposition expects a default stance; question allows a sharper question, distinction, or aporia as valid landings) — both modes also share six valid landings in the Voice Pipeline v2 spec. Surfacing `mode` inline in the markdown header lets the voice's user prompt be self-contained; the voice does not have to look up the mode field in JSON metadata to know how to respond.

**`full_theme_record` — the wider REASONING SURFACE for Step 1 thinking.**

Structured JSON. The voice's private deliberation during Step 1 should range over the full record of what was said on this theme, not just what the Provocateur highlighted. Contains:

- `clusters[]` — each cluster's id, title, abstract, and all raw extractions (id, speaker, lens, extraction, context, engagement, responds_to, energy). Extractions sorted within each cluster: assertions first, reframings next, `open_question`s last.
- `theme_title_from_researcher` and `theme_abstract_from_researcher` — the Researcher's own labels, not the Provocateur's display title. The voice can see the discrepancy if one exists.
- `co_assigned_voices[]` — other voices who received this same theme, so the voice knows its response is not the only one coming.
- `theme_flags` — `audience_friction`, `fault_line_present`, `theme_quality`.
- `grounding_extraction_ids[]` — the specific extractions the formulation is grounded in, per the Provocateur's rationale.


A voice with the full picture might notice positions the curated quotes left out, see counter-currents the Provocateur didn't surface, or confirm the framing was right and stay close to it. All are good Step 1 moves.

### What is NOT in the Briefing

**The voice's own profile.** The Voice Pipeline agent IS the persona — it is loaded with its full v3.10 Persona Card as its system prompt. Re-shipping profile fragments in the briefing would be redundant and risks drift between what the Voice Pipeline loads and what the Provocateur describes.

**`council_config_version`.** Lives in the run's `manifest.json`, not duplicated 12× across briefings.

**`formulations_count`.** Derive from `len(formulations)`.

**The Provocateur's `rationale` field.** Would prime the voice toward the Provocateur's expected answer. Kept in `formulations/{theme_id}__{slug}.json` for audit.

### Briefing File Shape

```json
{
  "formulations": [
    {
      "theme_id": "theme_003",
      "theme_display_title": "...",
      "mode": "question",
      "formulation_text": "...",
      "context_narrative": "...",
      "selected_quotes": [
        {"extraction_id": "session:NNN", "quote": "...", "attribution": "...", "flavor": "..."}
      ],
      "narrative_briefing": "markdown string...",
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

**Structured fields added 2026-04-28 for Voice Pipeline v2 contract:** `formulation_text`, `context_narrative`, and `selected_quotes` are now exposed at the briefing-entry top level, alongside the rendered `narrative_briefing` markdown. The Voice Pipeline reads these structurally (rather than parsing the markdown) when populating its Step 1 output's `formulation_text` lineage echo and when downstream steps need access to the curated quotes (e.g. Step 3's amendment may want to cite a `selected_quote` directly rather than having the Step 3 model re-extract it from prose). The Provocateur's `rationale` field is still excluded from the briefing — kept in `formulations/{theme_id}__{slug}.json` for audit, never passed to the voice (would prime it toward the Provocateur's expected answer).

Voices with zero assignments still get a briefing file (empty `formulations[]` array), to make the "who got nothing" case visible rather than silent. A voice showing up with zero is a signal that Triage found no ground for them and Force-fit had no survivors to grab — worth investigating in that run's diagnostics.

---

## Constraints

**Time window.** The Provocateur runs after the Researcher completes. It must finish fast enough that the Voice Pipeline and all downstream processing can complete before breakfast. The five-stage architecture is the key enabler here — Triage's 13 parallel LLM calls collapse to ~1-2 minutes wall time, Selection is instant, and Formulation's parallel batches scale with (themes × voices) pairs up to the rate-limit ceiling. On `dev_msc_test` (6 themes, 12 voices, ~40 surviving pairs), total wall time was roughly 12-18 minutes on Opus 4.7 with adaptive thinking.

**Rate limits.** Anthropic's Opus 4.7 tier caps output tokens per minute. Formulation generates ~3K output tokens per call, so the default batch size of 4 parallel calls with a 20-second wait between batches keeps the pipeline well inside the rate window. If Anthropic raises the tier or a future model lifts the cap, increasing `PROVOCATEUR_FORMULATION_BATCH` is the first place to recover time.

**Reproducibility.** Given identical Triage inputs, Selection always produces identical assignments — pure deterministic Python. Triage and Formulation are not reproducible (LLM sampling), but their outputs are cached per-voice and per-pair, so a single pipeline run produces a single canonical set of briefings that downstream code can trust.

**Night 2 + Night 3 are different from Night 1.** Implemented 2026-05-01 (C9): on Night 2/3, pass `--prior-nights <run_dir>[,<run_dir>...]` to `provocateur_flow.py`. The flow loads prior nights' `selection.json` + `grouping.json`, builds a per-member exclusion set keyed on **normalized theme title** (lowercased, whitespace-collapsed — theme_ids are not stable across Researcher runs, so content-based matching is the canonical key), and applies the filter inside `python_select` Step 4 (candidate-list construction). Step 7 force-fit also honors the exclusions — a voice with all candidates filtered ends with zero assignments rather than re-deploying covered territory. No LLM involvement. Diagnostics: `prior_exclusions_applied`, `prior_exclusions_blocked`, `prior_nights_consumed` in `selection.json`. See §"Night 2 + Night 3 cross-night exclusion" above for details + CLI examples.

**Incremental restart.** Every LLM call writes its checkpoint before returning. A crashed run resumes from the last completed checkpoint. There is no `PROVOCATEUR_CACHE` flag — the checkpoints ARE the cache. To force a clean run, delete `runs/<run>/03_provocateur/` or the specific checkpoint files that need re-running. Selection always recomputes against whatever Triage data and `selection_parameters` are on disk at the moment.

---

## Scope

The Provocateur does not extract or group — that's the Researcher. It does not process isolated extractions from the Researcher's output — only themed material. It does not produce what participants see — that's the council's artifacts and downstream roles. It does not interpret or map the council's responses — that's a downstream role. It does not load the full v3.10 Persona Card — only the 8-field profile derived from it.

The Provocateur's sole function is to take the Researcher's faithful map of the day's conversations and turn it into per-voice briefings that maximise the strength, distinctiveness, and interest of every artifact the council produces.

---

## Implementation

The Provocateur is implemented as a Prefect flow at `flows/provocateur_flow.py` in the `ai-assembly` repo. Prompts live at `flows/shared/prompts/` alongside the Researcher's prompts. All editorial state lives in `flows/shared/council/council_config.json`.

### File Layout

```
flows/provocateur_flow.py             — Prefect flow orchestrator
flows/shared/prompts/
  provocateur_triage_voice.md         — Stage 1A system prompt
  provocateur_triage_flags.md         — Stage 1B system prompt
  provocateur_formulation.md          — Stage 3 system prompt
flows/shared/council/
  council_config.json                 — collective_landscape, audience, members[], selection_parameters
  README.md                           — swap workflows (change the council without code changes)
```

Selection and Packaging have no prompt files — they're pure Python functions (`python_select` and `package_voice_briefings`) inside the flow module.

### Model Configuration

Default model: `claude-opus-4-7` with `thinking.type=adaptive`. Override via `CLAUDE_MODEL` env var for Sonnet dev iteration. Thinking can be disabled via `PROVOCATEUR_THINKING=0` (not recommended; validated quality relies on adaptive thinking).

Token budgets: Triage and Formulation both set `max_tokens=40000`. This is a ceiling, not a target — thinking consumes budget before visible text is emitted, so generous ceilings prevent the "empty text stream" failure mode. Observed usage in validation: 15-25K output tokens per call, well inside the ceiling.

### Outputs

```
runs/<run>/03_provocateur/
  triage_voices/{voice_slug}.json     — one per council member (Stage 1A checkpoints)
  triage_flags.json                   — single file (Stage 1B output)
  selection.json                      — Stage 2 output with diagnostics
  formulations/{theme_id}__{voice_slug}.json   — one per pair (Stage 3 checkpoints)
  briefings/{voice_slug}.json         — one per council member (Stage 4 final output)
  manifest.json                       — run-level metadata, counts, and selection_parameters_used
```

For a flat aggregated view of per-pair checkpoints:
```
cat runs/<run>/03_provocateur/formulations/*.json | jq -s '{formulations: .}'
```

### CLI

```
python flows/provocateur_flow.py runs/<run>
```

Expects the Researcher to have already written `runs/<run>/02_researcher/all_extractions.json` and `runs/<run>/02_researcher/grouping.json`.

---

## Validation Notes

This architecture was validated end-to-end on the `dev_msc_test` corpus (MSC 2026 panels: Breaking Point, Vox Populi, West-West Divide — 106 extractions, 6 themes, 12 voices) with the Researcher Pipeline's v2.4 output. Key observations:

- **Triage split (1A/1B) produced sharper output than v1's combined prompt.** Per-voice rankings cited specific `activates_on` phrases; editorial flags correctly identified 6 themes with cross-council fault lines (e.g., West-East framing, expert-vs-lay epistemic authority) that Selection's multipliers then boosted.

- **Python Selection was instant and fully deterministic** — identical outputs across repeated runs of the same Triage data. Forced-fit triggered twice (narrow-territory voices Cleopatra and Whanganui on this test corpus); stretch-swap triggered three times without breaking quorum.

- **Per-pair Formulation produced genuinely different angles per voice.** Two voices assigned to the same theme received formulations that differed in what they asked, not just in wording — Plato on a democracy theme asked a definitional "what is X?" question, Ibn Battuta on the same theme was given a proposition about travel as political pedagogy.

- **Proposition test held.** Out of ~40 pairs, the model wrote 3 propositions (7%) and 37 questions. All three propositions passed all five conditions on human review; the 37 questions were correctly chosen over propositions. v1's default-to-proposition drift did not recur.

- **Two-view briefings read cleanly.** The markdown `narrative_briefing` is paste-ready for Voice Step 1. The `full_theme_record` is dense but structured — a voice that wants more context than the curated quotes provided can drill in without parsing prose.

These are draft instructions, calibrated on a test corpus. Revise against the first Athens-session output before production deployment.
