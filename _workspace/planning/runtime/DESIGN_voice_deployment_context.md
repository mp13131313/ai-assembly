# DESIGN — voice-runtime deployment_context block

**Status:** designed pre-Athens (2026-05-05), implemented on
`feature/voice-deployment-context`, **never merged**. Athens Nights 1–3 ran
without it. Filed here so the Phase B persona-pipeline rebuild can decide
whether to re-implement, re-design, or drop.

**Source of truth (read-only archive):**
- Tag: `archive/voice-deployment-context-2026-05-05` → commit `248300c`
- Original implementation commit: `ec77a3c` *runtime(voice/card_assembly):
  inject deployment context (room/panel/readers) into voice system prefix*
- Original test suite: `runtime/tests/test_deployment_context.py` at the tag
  (285 lines, full coverage of the 5 rules below)

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

## Athens ran without this — what voices had instead

Athens voices (Nights 1–3, all 10 voices, all 13 dossiers) composed
with:

- ✅ Full persona card (identity, register, hostile_sources, corpus)
- ✅ Provocateur formulation (topic, fault-lines, audience-friction)
- ✅ Continuity from prior nights (`continuity_night_<N>.json`)

But **without**:

- ❌ Explicit "what gathering / what panel / what fellow voices / what
  readers" descriptive block in the system prompt

The Provocateur formulation carried most of the *implicit* deployment
context (panel topic name, audience tone) and the persona card carried
the voice's identity. The 13 dossiers landed; voices spoke distinctively;
the transmission_witness register worked for Whanganui. Whether the
explicit deployment-context layer would have changed outputs noticeably
is unknown — no A/B was run.

## Phase B decision point

When the persona-pipeline rebuild reaches the voice runtime, three
options:

1. **Re-implement as designed** — port the 5-rule contract into the new
   architecture. The rules are tested + grounded in real JSON shapes.
2. **Re-design** — keep the *principle* (descriptive metadata layer
   separate from prescriptive persona card) but use a different shape
   (e.g., a richer Provocateur formulation that subsumes deployment
   context, eliminating the need for a separate block).
3. **Drop** — Athens shipped without it; if Phase B's voice priming via
   formulation + continuity is strong enough, the explicit block may be
   redundant. Decide consciously, not by omission.

The **rule worth carrying** regardless of choice: keep prescriptive and
descriptive layers separated. The persona card is prescriptive; whatever
carries room-awareness should stay descriptive. Don't mix imperatives
into deployment metadata.
