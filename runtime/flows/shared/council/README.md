# Council Config

The `council_config.json` file in this directory is the **hot-swap surface** for the Provocateur Pipeline (v3). Everything the Provocateur knows about the AI Assembly council — the collective landscape, the audience, the 12 member profiles, and the Selection-stage editorial knobs — lives in this one file. To change the council right before an Athens night, edit this file and re-run the Provocateur. No code changes, no prompt edits.

## Schema

```json
{
  "version": "string — free-form identifier, written to the output manifest for traceability",
  "last_updated": "YYYY-MM-DD",
  "notes": "optional free-form note about this config",

  "collective_landscape": "one paragraph describing the council as a whole: traditions, eras, ontologies, fault lines",

  "audience": "one paragraph describing the ~750 breakfast attendees: who they are, what activates them, where their stretch is",

  "members": [
    {
      "name": "string — the display name used in all downstream artifacts",
      "speaks_from": "tradition, era, mode of knowing. The intellectual ground this voice stands on.",
      "core_commitment": "the conviction this voice would defend to the last. Not a topic — a hill they'd die on.",
      "activates_on": "the territory where the core commitment meets incoming material and produces the voice's strongest, most distinctive work",
      "goes_flat_on": "territory where the voice has something to say but nothing distinctive — the 'don't assign' signal",
      "stretch": "territory that would push the voice beyond its usual range without breaking it",
      "translation_range": "how the voice speaks — register, tone, grammatical preferences, languages available",
      "stance_tendency": "asserts | reframes | asks — does this voice tend to take hard positions, recast questions, or open them?",
      "medium": "text | song | image | etc. — the output modality for this voice's artifacts"
    }
  ],

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

## Selection parameters — what each knob does

The v3 Selection stage is pure Python (no LLM). It scores themes per voice using Triage activations, multiplies by editorial signals, builds per-voice candidate lists, enforces a quorum, force-fits voices to a minimum, and optionally swaps in a stretch theme. Every parameter below is read at run time from this file — change a value and re-run, no API calls needed.
</content>
**`activation_threshold`** (default 2). The numeric activation score a theme must hit on a given voice to be a candidate for that voice. Strong activations score 3, moderate score 2. With threshold=2, both strong and moderate activations qualify; with threshold=3, only strong qualifies (more selective).

**`min_members_per_theme`** (default 3). Quorum: a theme must have at least this many voices assigned to it (after the per-voice ranking and capping) or it gets dropped at the quorum check. When themes drop, voices whose assignment was dropped cascade to their next candidate. Iterates until stable.

**`min_formulations_per_voice`** (default 1). Force-fit minimum: any voice that ends up with fewer than this many assignments after the algorithm gets backfilled with their highest-ranked surviving theme regardless of activation level. Surfaces as `forced_fits` in `selection.json` for audit.

**`target_formulations_per_voice`** (default 5). Soft target. The algorithm does NOT enforce this — it's used only to log a warning for voices that ended below target after all algorithm passes. Useful at Athens scale for spotting voices that didn't get enough material; at small scale (few themes) most voices will fall below target and that's expected.

**`hard_cap_per_voice`** (default 5). Strict ceiling on how many themes any voice gets assigned. The per-voice candidate list is sorted by (own_score desc, theme_quality desc) and truncated at this cap.

**`friction_multiplier`** (default `{low: 1.0, moderate: 1.3, high: 1.7}`). Multiplier applied to a theme's quality score based on Triage's `audience_friction` flag. High-friction themes (those that touch the audience's stretch territory or contradict their priors) get boosted in the per-voice quality ranking.

**`fault_line_multiplier`** (default `{absent: 1.0, present: 1.5}`). Multiplier applied to a theme's quality score based on Triage's `fault_line_present` flag. Themes where the day surfaced a genuine intellectual disagreement (not just a topic) get boosted.

**`stretch_swap_enabled`** (default `true`). After force-fit, if a voice has zero `is_stretch=true` assignments AND has at least one stretch theme in their candidates, the algorithm swaps their lowest-quality assignment for the highest-scoring stretch theme — but only if the swap doesn't break quorum on the swapped-out theme. Surfaces as `stretch_swaps` in `selection.json` for audit.

## How to swap the council

The council is not baked into code. To change anything about it, edit `council_config.json` and re-run the Provocateur.

**Edit a single member.** Open `council_config.json`, find the member in the `members` array, edit any of the nine fields (`name`, `speaks_from`, `core_commitment`, `activates_on`, `goes_flat_on`, `stretch`, `translation_range`, `stance_tendency`, `medium`). Delete that voice's checkpoint files: `runs/{run}/03_provocateur/triage_voices/{slug}.json` and any `runs/{run}/03_provocateur/formulations/*__{slug}.json`. Re-run the flow. Only that voice's stages re-execute.

**Tune Selection without changing voices.** Edit `selection_parameters` and re-run. Selection always recomputes — no checkpoint deletion needed. Costs nothing.

**Swap the entire council.** Replace the `members` array wholesale. Update `collective_landscape` if the new council has materially different traditions or fault lines. Update `version` and `last_updated` so the output manifest records which council ran. Delete `runs/{run}/03_provocateur/triage_voices/` and `runs/{run}/03_provocateur/formulations/` entirely (the old per-voice and per-pair checkpoints are now invalid). Re-run.

**Use a different config for Night 2.** Two options. (a) Keep one file, edit it between nights — the Night 1 run's manifest records its own version string, so provenance is preserved in the artifacts even after the file changes. (b) Maintain two files side by side and swap them in. Option (b) is cleaner if you expect significant council changes between nights.

</content>## When to delete checkpoint files

The v3 pipeline uses incremental write checkpointing — completed work persists to disk and is auto-skipped on re-run. This is the cache. Delete the relevant files when you change the inputs that produced them:

| You changed | Delete | Reason |
|---|---|---|
| A voice's profile | `triage_voices/{voice_slug}.json` + `formulations/*__{voice_slug}.json` | Profile is in LLM prompt context for both stages |
| `collective_landscape` or `audience` | All of `triage_voices/` and `formulations/` | Both stages see these in prompt context |
| Triage prompts (`provocateur_triage_*.md`) | All of `triage_voices/` (and `triage_flags.json` if flags prompt changed) | LLM output schema/content depends on prompt |
| Formulation prompt (`provocateur_formulation.md`) | All of `formulations/` | Same reason |
| `selection_parameters` only | Nothing | Selection always recomputes from existing Triage data |
| Packaging code (briefing schema) | Nothing | Packaging always recomputes from existing data |

To force a complete clean run: `rm -rf runs/{run}/03_provocateur/` (and re-run).

## Stubs vs real profiles

The current `council_config.json` (version `dev_stub_v2_with_selection_params`) is a development stub. The 12 member profiles were hand-written from project memory for building and testing the Provocateur pipeline. They capture the right shape and fill the required fields, but they are not the real derived profiles the production pipeline will eventually use.

The real workflow is: each council member has a v3.7 Persona Card produced by the Persona Pipeline; the Derive node reads the Persona Card and writes the nine-field profile (`name` through `medium`) back into the council config. To migrate from stubs to real profiles: run the Persona Pipeline Derive step for each member, drop the resulting profile entries into the `members` array, bump `version` to something like `athens_2026_night_1`, and update `last_updated`. The Provocateur code does not care which profiles are stubs and which are real — as long as the nine required fields are present and readable.

## What reads this file

The Provocateur Pipeline (`flows/provocateur_flow.py`) — specifically `triage_voice` (per-voice ranking), `formulate_for_member` (per-pair formulation), and `python_select` (which reads `selection_parameters` only). The Researcher does not read this file by design — the Researcher is council-unaware.
</content>