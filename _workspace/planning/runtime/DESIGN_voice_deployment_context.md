# DESIGN — voice-runtime deployment_context block

**Status:** designed + implemented + dryrun-tested + **retired as superseded**
(2026-05-05 design; 2026-06-01 retired). Athens Nights 1–3 ran with
deployment_context at the **Provocateur + Editor stages** instead of the
voice stage; the dryrun verdict was that the same priming effect lands
one stage earlier at lower architectural cost. Filed here so the Phase B
persona-pipeline rebuild has the full decision trail.

This is not "we didn't get around to it" — it is "we tested it, found it
works, and chose a different placement." See *Why it was retired* below.

**Source of truth (read-only archive):**
- Tag: `archive/voice-deployment-context-2026-05-05` → commit `248300c`
- Original implementation commit: `ec77a3c` *runtime(voice/card_assembly):
  inject deployment context (room/panel/readers) into voice system prefix*
- Original test suite: `runtime/tests/test_deployment_context.py` at the tag
  (285 lines, full coverage of the 5 rules below)
- **Dryrun verdict doc:** `projects/current-tests/dev_msc_dryrun_v2_20260504/runs/athens_night_1/04_voice/COMPARISON_2026_05_05.md`
  (1024 lines, full voice-output comparison WITH vs WITHOUT the block)

---

## What it does

Before a voice's persona card renders into a system prompt, inject a
*deployment-context block* — descriptive metadata about the room, the
panel, the fellow voices, and the readers. Sourced from operator-curated
JSON at `$PROJECT_ROOT/`:

- `conference_facts.json` → `conference_context_paragraph`
- `council_config.json` → `collective_landscape`, `members[].name`,
  `audience`

The editor side of deployment_context **did** land in main (commits
`0f751b7`, `fda8091`, `7e99c63`, `cbcdf82`) and ran in Athens. The voice
side is what this doc captures.

## The contract — 5 rules

1. **THE GATHERING block** — emit at *all* steps when
   `conference_facts.conference_context_paragraph` is present. Names the
   conference's character (twelve thematic tracks, Aegean Intelligence
   framing, marketing-vs-substance contrast, agency centre of gravity).

2. **THE PANEL block** — emit at *all* steps when
   `council.collective_landscape` is present. Panel-as-friction-structure
   framing, member roster with tradition tags, panel fault-lines derived
   from member fields.

3. **YOUR FELLOW VOICES block** — emit at **step 2 only**, listing the
   other voices on the panel (self excluded). Step 1 is private
   reasoning — full peer roster at reasoning time invites premature
   peer-positioning. Step 2 is composition where peer-awareness genuinely
   earns its place. The listing is framed as **anti-translation
   permission**:

   > "None of these voices translate themselves into a common register.
   > The gathering is built to hold the friction of their differences.
   > You speak from your tradition; the room does not need you to soften."

4. **YOUR READERS block** — emit at *all* steps when `council.audience`
   is present. Synced 1:1 with `audience_profile.json::participant_profile`
   (canonical source per `docs/AUDIENCE_BRIEF.md`). Descriptive — what
   readers activate on, what they go flat on, where their stretch is.

5. **`session_role_for_ai_assembly` is NEVER injected.** This is the
   load-bearing design decision. The conceit-of-the-experiment text
   ("the voice marks... rather than smoothing...") reads as imperative.
   Putting prescriptive language in the deployment-context layer
   conflates with the persona card's task-instruction layer (`<task>`,
   `<weighing>`, `<focus>` in the closing prompt). **Deployment context
   stays descriptive; the persona card retains its monopoly on
   prescription.**

## Empty-fallback rule

If neither source is available (test fixtures, edge cases, missing
PROJECT_ROOT), `_render_deployment_context` returns `""` and the system
prompt assembles without the block — does not raise. Production paths
(orchestrator + voice_flow CLI) always have these files; the fallback
exists so tests + dev work don't need full deployment JSON.

## Why it was retired (the dryrun + decision)

The original commit message ended *"Awaiting dryrun comparison before
merge."* The comparison fired on 2026-05-05 against
`runs/athens_night_1`, baselining the 2026-05-04 v2 dryrun against a
re-run on this branch. The verdict was **positive but redirected**:

**What the dryrun found** (full table at `COMPARISON_2026_05_05.md`):

- **6 of 10 voices shifted theme focus** between PRE and POST runs — not
  just different prose on the same theme, but choosing a *different
  theme* to engage. Plato (theme_004 → theme_003), Cleopatra (single
  → synthesis), Battuta (reordered synthesis), Scheherazade, Ada,
  Dostoevsky, Hannah all shifted; only Marley, Whanganui, and Octopus
  kept the same focus (the latter two having only one theme available).
- **+348 words net** across the 10 voices — voices "engaged more
  concretely" with room-awareness primed.
- Effect was real and measurable. The block does what the design promised.

**Why the runtime thread retired it anyway** (filed at the time as C39,
now `C41`):

> **"Richness lever sits at the briefing layer, not the
> deployment-context layer."**

The same priming effect — voices becoming room-aware, panel-aware,
audience-aware — could be achieved one stage earlier by enriching the
Provocateur's formulation + briefing instead of injecting a parallel
block at the voice's system prompt. The Provocateur is already where
themes get fault-lines and audience-friction added; making it the
single carrier of deployment context kept the system *one stage's worth*
simpler.

**What shipped instead — same need, earlier stage:**

- **Provocateur deployment_context** (`cbcdf82`, *runtime: panel-speaker
  attribution end-to-end + Provocateur deployment context*) — landed
  2026-05-05 evening, ran in all three Athens nights.
- **Editor deployment_context** (`fda8091`, `7e99c63`, `0f751b7`) —
  landed 2026-05-05 through 05-07, ran in all three Athens nights.
- **Voice stage**: persona card + briefing-enriched formulation +
  continuity. No explicit deployment block.

The dryrun explicitly noted the placements are **additive, not
alternative** — putting deployment_context at all three stages (Provocateur
+ Editor + voice) would compound the effect. The retirement decision was
about scope and parsimony, not about correctness.

## Phase B re-implementation note

When the persona-pipeline rebuild reaches the voice runtime, the question
to ask is *not* "should we add this block?" but **"is the Provocateur's
formulation carrying enough deployment context for the voice's
purposes?"** If yes, leave the voice stage descriptively minimal. If the
rebuild ever surfaces a case where Provocateur-stage enrichment isn't
enough (e.g. step-2 fellow-voices-awareness needs explicit listing rather
than implicit "you're on a panel" framing), the 5-rule contract is here
to port.

The **principle worth carrying** regardless of placement: keep
prescriptive and descriptive layers separated. The persona card is
prescriptive; whatever carries room-awareness should stay descriptive
("THE GATHERING is X" not "BE AWARE OF X"). Don't mix imperatives into
deployment metadata — that's why
`conference_facts.session_role_for_ai_assembly` was deliberately excluded
from the voice block (Rule 5). The Provocateur formulation today honors
the same split.
