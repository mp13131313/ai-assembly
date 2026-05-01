# Voices — Onboarding (authoritative, 2026-05-01)

**Scope:** fresh-session pickup for **persona pipeline / voice cards** work specifically — building the 10 panel voices for athens-2026.

**Companion:** `OPEN_ITEMS.md` (sibling). When a fresh session starts on voices work: read this first, then OPEN_ITEMS.md, then act.

**Truth source:** When this doc disagrees with another planning doc, this doc is right (or fix this doc). Older docs may have stale framings.

---

## What "voices" means here

The **persona pipeline** generates a **persona card** + **provocateur profile** + **chat system prompt** per voice. These are the build-side deliverables. The Voice Pipeline (runtime) consumes the cards + profiles to produce overnight artifacts at Athens. Persona-build is separate from Voice Pipeline runtime; this doc is about the former only.

A "voice" is a participant on the Athens-2026 Assembly panel. Panel is **10 voices** per `panel_roster.json`.

---

## Where everything lives

```
~/Desktop/AI Assembly/
├── code/
│   ├── personas/                   ← the persona pipeline (Pass 0a → assembled card)
│   │   ├── run_pass0a_voice_config.py
│   │   ├── run_phase0_1_research.py
│   │   ├── run_persona_pipeline.py
│   │   └── flows/shared/prompts/   ← all Pass 1.x → Pass 7.x prompts
│   ├── docs/
│   │   ├── AI_Assembly_Persona_Pipeline_v4.md   ← canonical pipeline spec
│   │   ├── AI_Assembly_Persona_Card_v2.md        ← canonical card schema
│   │   └── AI_Assembly_Briefing_v3_1.md          ← project source of truth (Layer 1/2/3 framing)
│   └── _workspace/planning/
│       ├── voices/                 ← YOU ARE HERE
│       │   ├── ONBOARDING.md       (this doc)
│       │   └── OPEN_ITEMS.md       (sibling)
│       ├── FOLLOW_UPS.md           ← FU#1-61 tracker (broader; voices-relevant ones consolidated in OPEN_ITEMS.md)
│       ├── HANDOFF_*.md            ← older handoffs; mostly superseded by voices/ docs for voice-build state
│       └── (other planning docs not voice-specific)
└── projects/
    └── athens-2026/                ← the production data project (own private git repo)
        ├── voices/<slug>/          ← per-voice working tree
        │   ├── 00_intake/          (Pass 0a)
        │   ├── 01_research/
        │   │   ├── 03_dr_prompts/  (Phase 0.5 output — operator pastes into claude.ai)
        │   │   └── 04_dr_dossier/  (manual claude.ai DR results — operator saves here)
        │   ├── 02_merge/           (Pass 1)
        │   ├── 03_corpus/          (Pass 1c primary-text fetch + review gate)
        │   ├── 04_generation/      (Pass 2-6)
        │   ├── 05_validation/      (Pass 7-pre, 7a, 7b, 7c, 7a FINAL)
        │   ├── 06_derive/          (provocateur profile + evaluation rubric + chat artifact)
        │   ├── 07_persona_card_assembled.json  ← THE deliverable
        │   └── _operator_review_passed.flag    (path-b shipping flag)
        ├── panel_roster.json
        ├── conference_facts.json
        └── audience_profile.json
```

---

## The 10 panel voices

| # | Voice | Slug | type | voice_mode | hostile? |
|---|---|---|---|---|---|
| 1 | Plato | `plato` | human | philosophical | false |
| 2 | Cleopatra | `cleopatra` | human | observational | **true** |
| 3 | Ibn Battuta | `ibn_battuta` | human | narratival | false |
| 4 | Scheherazade | `scheherazade` | fictional | (likely narratival) | false |
| 5 | Ada Lovelace | `lovelace` | human | (TBD) | false |
| 6 | Fyodor Dostoevsky | `dostoevsky` | human | narratival | false |
| 7 | Hannah Arendt | `arendt` | human | (likely philosophical) | false |
| 8 | Bob Marley | `marley` | human | (likely narratival) | false |
| 9 | Whanganui River | `whanganui_river` | non_human | (likely observational) | (TBD) |
| 10 | Octopus | `octopus` | non_human | observational | false |

Slugs are auto-derived from `name` field via `voice_slug()` in `personas/flows/shared/io.py`. Some operator pattern: shorten multi-name to single recognizable name (Plato, Dostoevsky, Octopus); keep canonical short form when it IS the canonical (Ibn Battuta).

**Build state:** see `OPEN_ITEMS.md` §1.

---

## Build pipeline overview

```
1. Pass 0a — voice_config + review_doc                                 ~1 min
   python3 run_pass0a_voice_config.py "<Voice Name>" \
     --wiki <wikipedia_url> \
     --project /Users/aienvironment/Desktop/AI\ Assembly/projects/athens-2026
   
   → produces voices/<slug>/00_intake/{02_voice_config.json, 03_review_doc.md}
   → operator reviews voice_mode, hostile_sources, type/subtype proposals
   → operator decides: fill editorial_rationale OR leave null (current pattern: leave null)

2. Phase 0.5 — Perplexity + Gemini + DR prompt tailoring               ~6 min
   python3 run_phase0_1_research.py "<Voice Name>" --project ...
   
   → produces voices/<slug>/01_research/{01_perplexity_dossier.json, 02_gemini_broad_scan.json, 03_dr_prompts/}
   → 6 tailored DR section prompts ready for manual paste

3. Manual DR sessions — operator wall                                  ~3-4 hr operator time
   → Open claude.ai with Opus 4.7 + Extended Thinking + Deep Research enabled
     [NOTE: older spec said "§1-§5 use 4.6, §6 uses 4.7" — STALE. Current operator pattern: 4.7 across §1-§6]
   → For each section: paste prompt, wait ~30 min, save .md output
   → Save each as voices/<slug>/01_research/04_dr_dossier/0N_section_N.md

4. Persona pipeline — chunked merge → generation → validation → derive  ~30-90 min
   python3 run_persona_pipeline.py "<Voice Name>" --project ...
   
   Inside this:
   - Pass 1.1-1.7 chunked merge (parallel + coherence audit)            ~15-25 min
   - Pass 1c-extract + Pass 1c-fetch + REVIEW GATE                      ~1-2 min
       → operator reviews voices/<slug>/03_corpus/04_primary_texts_review.md
       → (optional) edit 01_primary_texts.json
       → touch voices/<slug>/03_corpus/03_primary_texts_reviewed.flag
       → re-fire run_persona_pipeline.py to resume
   - Pass 2-6 (Identity, Intellectual Core, Voice, Artifact, Engagement, Corpus)  ~10-30 min
   - Pass 7-pre + 7-anachronism + 7a + 7b + 7c + 7a FINAL                 ~10-20 min
   - FU#53 REVIEW GATE — operator decision (a/b)                         ↓
   - Derive (provocateur profile + evaluation rubric + chat artifact)    ~5 min
   - Final assembled card on disk
```

---

## FU#53 review-gate decision pattern

When Pass 7a FINAL flags `REVISION_NEEDED`, pipeline blocks at gate. Operator chooses:

### Path (a) — re-validate
```bash
# Patch the assembled card based on flagged issues (edit JSON)
rm voices/<slug>/05_validation/06_pass_7a_final.json
python3 run_persona_pipeline.py "<Voice Name>" --project ...
# Pipeline re-fires Pass 7a FINAL against the patched card; blocks at gate again
```

### Path (b) — accept residuals + ship
```bash
touch voices/<slug>/_operator_review_passed.flag
python3 run_persona_pipeline.py "<Voice Name>" --project ...
# Pipeline skips gate, runs Derive, completes
```

### When to use which

**Round 1 (first gate hit):** path (a). Patch the cleanly-actionable issues, re-validate.

**Round 2:** Validator surfaces a *different* residual set (treadmill). Patch the cleanly-actionable issues again, re-validate.

**Round 3+:** Path (b). The validator never reaches zero — round 3+ produces register-strict critiques that aren't runtime-blocking. Accept and ship.

**Operator pattern across 4 voices:** every shipped voice (Plato, Cleopatra, Dostoevsky, Battuta) hit 2 patch rounds + path (b). Match this; budget 2 rounds.

---

## Common patches you'll apply at the gate

These recur across voices — pattern-recognize them quickly:

### Always skip (false positives)

- **`council_member_name` "missing"** — validator hallucinates this on every voice. Field is unambiguously present. Don't waste cycles patching.

### Sometimes skip (register-strict, not runtime-blocking)

- **`quality_criteria` evaluator-question form** ("Does the piece...") — Plato shipped with this form and chat-tested fine. Don't patch unless paired with operator preference for imperative form.
- **Long-form-field biographical/glossary register** (FU#56 territory) — accepted via path (b) since 9480d3a-revert risk on prompt-side fix.

### Always patch (real issues)

- **Modern-named-comparators in `hard_limits`** (e.g., William-Lane-Craig, Instagram-Dostoevsky, Freudian, Aegean Intelligence) — strip; replace with period-neutral alternatives
- **Internal-production leakage in `banned_modes`** (e.g., "Aegean Intelligence response", "democracy response", "Lab draws a different line") — strip; keep substantive prohibition
- **Post-voice-lifetime vocabulary in `constitution` / `concept_lexicon`** (Nietzschean for Dostoevsky; modern analytic for Battuta) — replace with period-native alternatives
- **Third-person register breaks in operational_notes / character / metaphorical_repertoire** (e.g., "The voice itself is...") — rewrite first-person ("I am the...")
- **Theatrical exit lines in `disagreement_protocol`** (e.g., "The chair is empty before your reply is finished") — drop
- **Modern-polemical-flourish slogans** ("wonder-cabinet calling itself a court", "fitna in a clean shirt") — restate in voice-native terms
- **`voice_temporal_stance.default` vs `anchored_override` conflict** — make default commit to a primary speaking-now; override is the more-specific subset

### Voice-specific (one-offs)

- Cleopatra round 2 needed source-attribution stripping + Jowett-vs-banned_language patches + bilingual-stack discipline. See `voices/cleopatra/` git history.
- Dostoevsky needed Nietzschean → period-native (3 places), modern named comparators removed, internal-production stripped. See `5088d67` commit.
- Battuta needed voice_temporal_stance horizon collapse + opening-line first-person commitment + 3 bold_engagement_topics flourish-trimmings + 1 disagreement_protocol theatrical-line drop. See backup at `voices/ibn_battuta/07_persona_card_assembled.pre_round1_patches.json`.

---

## Voice-mode is a CONSTRUCTION decision, not a HISTORICAL one

Per the spec, `voice_mode` is one of `philosophical` / `narratival` / `observational`. **This is about how the pipeline constructs the voice, not what the historical figure produced.**

- **philosophical** — voice reasons FROM a stated framework; when framework doesn't reach a question, applies/extends framework or marks the gap
- **narratival** — voice reasons THROUGH dramatized confrontation; gives question to characters, lets answer emerge
- **observational** — voice reasons by EXTRAPOLATING from practice/embodied engagement; framework is not stated but lived. Specifically: this mode is for voices with **no direct/hostile-only sources** where the pipeline must construct via third-party observation. NOT for voices with first-person dictated voice (e.g. Battuta has *Rihla* in his voice → narratival, not observational).

**Common Pass 0a mistake:** the runner sometimes proposes `observational` for any non-Western voice or anyone with limited primary sources. **Re-check.** The strongest construction-mode argument is "what's irreplaceable about this voice on the panel?" — choose the mode that lets that contribution land.

Empirically:
- Plato → philosophical (Forms, dialectic, written-as-dialogue but the dialectic IS the framework)
- Cleopatra → observational (corpus is hostile reconstruction; no first-person diary; we observe her through artifacts)
- Octopus → observational (no language, no first-person, voice constructed via science writing)
- Dostoevsky → narratival (corpus is novels staging confrontation between voiced characters)
- Battuta → narratival (Rihla IS dictated tale-form)

---

## Operator-confirmed conventions / DON'Ts

### DON'Ts (operator-explicit)

- **DON'T re-introduce "Phase L" framing.** Operator dropped it. The empirical baseline is the post-Plato-2026-04-26 voice runs — including 2 more recent Plato versions.
- **DON'T modify Pass 2/3/4a/4b prompts mid-pipeline-run.** Mid-run prompt edits affect later voices' passes inconsistently. Edit prompts when no pipeline is in flight.
- **DON'T blanket-apply changes to shipped voices without per-voice empirical comparison.** The FU#61 fresh-test pass showed only Dosto benefited from re-emit; Plato/Cleopatra/Battuta were voice-stronger in their original-shipped state.
- **DON'T use `git add -A` or `git add .`** in athens-2026 — many operator-snapshot files (`*.pre_*.json`) and `_pipeline_logs/` are local-only. See OPEN_ITEMS.md §6 for the .gitignore additions still pending.
- **DON'T treat the validator's flags as the runtime quality bar.** Validator is gpt-5.4 high (cross-model) — produces register-strict critiques. Plato shipped with multiple flags; chat-test passed. Treadmill never zeros.

### DO (current patterns)

- **DO use Opus 4.7 across all 6 DR sections.** The older "§1-§5 use 4.6" spec is stale.
- **DO patch round 1 + round 2, then ship via path (b).** Match the 4-voice pattern.
- **DO leave `editorial_rationale` null** unless operator explicitly wants to fill it. Pipeline runs fine with null.
- **DO read voice's full Pass 7a FINAL output before patching.** The `field_issues` list is what matters; the rubric pass/fail status alone doesn't tell you what's actionable.
- **DO snapshot before patching.** Pattern: `cp 07_persona_card_assembled.json 07_persona_card_assembled.pre_<roundN>_patches.json`. Pre-patch snapshots untracked but local — preserve audit trail for inspection.

---

## Key prompt files (where edits land)

| File | What it controls |
|---|---|
| `personas/flows/shared/prompts/persona_pass_0a_voice_config.md` | Pass 0a — voice_mode/type/subtype/hostile_sources proposals |
| `persona_pass_0b_*.md` | Pass 0b tailoring — DR prompt customization per voice type |
| `persona_pass_2_identity_boundaries.md` + `_user.md` | Pass 2 — voice_name, world, formative_experience, character, knowledge_boundary, hard_limits, topics_requiring_care, voice_mode, voice_temporal_stance, translation_protocol |
| `persona_pass_3_intellectual_core.md` + `_user.md` | Pass 3 — constitution, concept_lexicon, reasoning_method, finds_compelling, resists |
| `persona_pass_4a_voice.md` + `_user.md` | Pass 4a — rhetorical_mode, characteristic_moves, register_and_tone, metaphorical_repertoire, preferred_vocabulary, banned_language, banned_modes |
| `persona_pass_4b_artifact.md` + `_user.md` | Pass 4b — medium, technical_capabilities, characteristic_output_structure, relationship_to_detailed_response, aesthetic_qualities, stance_tendency, length_and_format_constraints, **quality_criteria** |
| `persona_pass_5_engagement.md` + `_user.md` | Pass 5 — bold_engagement_topics, default_questions, disagreement_protocol, unique_contribution |
| `persona_pass_6_corpus.md` + `_user.md` | Pass 6 — curated_corpus_passages, reference_only_passages |
| `persona_pass_7*.md` | Pass 7-pre / 7-anach / 7a / 7b / 7c / 7a FINAL validation suite |
| `persona_coherence_threading.md` | CT compress — summarizes prior pass outputs for next-pass context |

**Most-edited prompt this period:** `persona_pass_4b_artifact.md` — landed FU#49A v2 quality_criteria scaffold (`0ca02f5`) + FU#61 audience-engagement +1 (`91947a7`).

---

## Streaming-stability + thinking config (already landed; informational)

`personas/flows/shared/clients.py` was hardened in the FU#60 cycle (committed):

- **`{type: "adaptive"}` thinking** + `display: "summarized"` (Opus 4.7 default is `omitted`)
- **Drops `temperature`** when `thinking=True` (Anthropic docs §"Feature compatibility")
- **Captures `thinking_trace` + `block_types`** in returned dict (additive)
- **1-retry on `httpx.RemoteProtocolError` / `ReadError` / `ReadTimeout`** with 15s backoff (Pass 4a streaming-drop on large outputs needed this; commit `a6fa848`)

If a future pass dies at streaming, check the log for `httpx.RemoteProtocolError` — usually self-heals on the retry.

---

## Pass 4b prompt — the FU#61 +1

Current (committed `91947a7`) `quality_criteria` block in `persona_pass_4b_artifact.md`:

```
- quality_criteria: 3-5 specific, testable criteria. Each criterion
  tests 1-n card fields by name (single field, or compounded with
  and/or logic). The criteria collectively should answer "Could
  this be mine?" across reasoning, voice, and form. Available
  load-bearing fields (consult as needed):

    - REASONING: reasoning_method, constitution, concept_lexicon
    - VOICE: rhetorical_mode, characteristic_moves,
      register_and_tone, metaphorical_repertoire
    - FORM: medium, characteristic_output_structure,
      aesthetic_qualities, stance_tendency
- Additionally, 1 further criterion answering: "Could this, on its own, make an audience engage with its intent?"
```

**Empirical pattern:** the model integrates the +1 into the 5 (5 reshape with 1-2 audience-engagement criteria) rather than appending literally. That's been the right behavior — don't sharpen the prompt to force literal +1 unless empirics on a future voice say otherwise.

---

## What's NOT in this doc

- **Voice Pipeline runtime** (Steps 1+2+3) — separate domain
- **Microsite, admin console, closing-show** — Athens-blockers but post-card-build
- **Frame Concept doc + Step 3 redesign** — runtime / publication-layer work, other thread

For those, see the broader project planning in:
- `docs/AI_Assembly_Briefing_v3_1.md` (project source of truth)
- `_workspace/planning/HANDOFF_DRYRUN_2026_04_29.md` (Voice Pipeline runtime state)
- `_workspace/planning/STEP3_REDESIGN_2026_04_30.md` (other thread)
- `_workspace/planning/PIPELINE_DOWNSTREAM_DESIGN_2026_04_30.md` (other thread)

---

## First 30 minutes (fresh session pickup)

1. **This doc** — read fully (~10 min)
2. **`OPEN_ITEMS.md`** sibling — read §1 (per-voice state) + §2 (Octopus) + §3 (5 unbuilt) (~10 min)
3. **`docs/AI_Assembly_Persona_Card_v2.md`** — confirm card schema if you'll be editing field-spec or operator-patching (~5 min)
4. **`docs/AI_Assembly_Briefing_v3_1.md` lines 49-53** — Layer 1/2/3 framing, the experimental test the panel must clear (~3 min)

That's ~30 min to working knowledge. Then check `OPEN_ITEMS.md` §6 for any cleanup the operator wants done first, otherwise pick a next-voice and start at Pass 0a.

---

## When this doc goes stale

Update this doc when:
- A new voice ships (update §"build state" via OPEN_ITEMS.md)
- An architectural pattern is established or invalidated (update §"Common patches" or §"DON'Ts")
- A prompt-level change lands (update §"Key prompt files" or §"Pass 4b prompt — the FU#61 +1")
- A new always-skip false positive emerges (update §"Common patches you'll apply at the gate")
- A new operator-explicit DON'T arrives (update §"DON'Ts")

If this doc gets older than ~2 weeks of active voice-build work, sweep it for staleness.
