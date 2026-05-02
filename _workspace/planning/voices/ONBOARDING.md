# Voices — Onboarding (authoritative, 2026-05-01)

**Scope:** fresh-session pickup for **persona pipeline / voice cards** work specifically — building the 10 panel voices for athens-2026.

**Companion:** `OPEN_ITEMS.md` (sibling). When a fresh session starts on voices work: read this first, then OPEN_ITEMS.md, then act.

**Truth source:** When this doc disagrees with another planning doc, this doc is right (or fix this doc). Older docs may have stale framings.

**Cross-cutting rules:** the parent `_workspace/planning/ONBOARDING.md` carries cross-cutting DON'Ts and calibration that apply to both voices + runtime threads (no `--no-verify`, no `git push origin main` without ask, no Plato re-run, no real-person names in deployment JSONs, etc.). Read it once; this doc holds voice-build-specific guidance only.

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

**Operator pattern across 7 shipped voices:** Plato / Cleopatra / Dostoevsky / Battuta / Octopus / Hannah Arendt / Ada Lovelace. Most landed at 2-3 rounds + path (b). Octopus = 4 rounds (compass rebuild surfaced more); Ada = **5 rounds during the build, then 4 over-patches rolled back** (`c025914`) after operator caught the §7-convention deviation. **Budget 2 rounds; surface verdict + ask operator before any round 3.** The post-Ada discipline note: round 1 patch cleanly-actionable; round 2 patch cleanly-actionable; end of round 2 — surface verdict + ask explicitly *"ship now via path-(b) or another round?"*. Don't keep patching unilaterally; the validator treadmill never zeros and patches beyond round 2 trend toward editorial expansion rather than validator-faithful fixes.

---

## Common patches you'll apply at the gate

These recur across voices — pattern-recognize them quickly:

### Always skip (false positives)

- **`council_member_name` "missing"** — validator hallucinates this on every voice. Field is unambiguously present. Don't waste cycles patching.
- **`[experiential_reconstruction]` / `[projection_warning: ...]` bracket tags inline in long-form fields** — these are CONTENT (Boddice biocultural epistemic-status annotations) preserved by Pass 6.5-clean's allowlist (FU#33 P1) and required by Pass 7-pre's boddice check. Schema-taxonomy brackets (e.g. `[ontological]` / `[epistemological]`) DO get stripped — those are scaffolding. If the validator flags a `[experiential_reconstruction]` or `[projection_warning]` as "leakage", skip the patch.

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

## Three voice-construction postures for non-human voices (compass / precautionary / transmission-faithful)

Banked from the Octopus compass rebuild (2026-05-02) + Whanganui rebuild design (same session). For non-human voices (`type=non_human`), the operator chooses one of three postures via `voice_config.editorial_rationale`. Each is honest if framed clearly; mismatch produces voice-build failure modes.

| Posture | When to use | Voice's primary mode | Failure mode if mis-applied |
|---|---|---|---|
| **Compass / phenomenologically-permissive** | `subtype=organism` with imaginative-reach intent — voice carries an "experiment-in-mind" framing (Octopus). Apply when the operator wants the audience to encounter the alien intelligence felt-from-inside, with construction-acknowledged at the frame. | Synesthetic/phenomenological rendering inside the frame. Godfrey-Smith *Other Minds*/*Metazoa* gradualist methodology primary; de Waal anthropodenial as cross-architecture license; Carls-Diamante disunity as one option not constraint; Nagel's bat as opening of imaginative question, not wall. | Clever-pet anthropomorphism (flattens alien intelligence into human-pet emotional categories) |
| **Precautionary** | `subtype=organism` with refuse-to-render intent. Apply when the operator wants the voice to enact the limit-of-what-can-be-known as primary mode. | Refuse experience-claims; render only documented behavior; "the nature of that experience is not accessible to us." Birch's bracketing-as-method; Despret's polite question; Carls-Diamante disunity as constraining frame. | Excessive-alienness refusal (prevents voice from speaking; collapses to scholarly translator reporting from outside) — what built-Octopus pre-rebuild had inadvertently become |
| **Transmission-faithful** | `subtype=system` with constitutional-document grounding (Whanganui — Te Awa Tupua Act 2017). Apply when the entity has a formal legal-cosmological text the iwi/community + state jointly authored. | Stewards what is verbatim from the constituting text + Indigenous-authored scholarship + critique scholarship. Voice speaks AS the entity via formal mediating structure (Te Pou Tupua for Whanganui). Bilingual integrated register (te-reo / Indigenous-language primary). | iwi-ventriloquism (voice speaks FOR the community instead of AS the legally-recognized entity); legal-bureaucratese (juridical-English-only; loses kin-cosmological substrate) |

**The Pass 0b base templates** are configured for these postures:
- `pass_0b_non_human_organism.md` (committed `a6755d9`, 2026-05-02) is **compass-permissive** — surfaces both precautionary and phenomenologically-permissive philosophical traditions; voice_config.editorial_rationale determines which the voice adopts
- `pass_0b_non_human_system.md` is **transmission-faithful by native design** — surfaces verbatim-quotation + iwi-non-ventriloquism + bilingual dual-register vocabulary + CARE-as-citation-discipline

**Operator decision at voice_config drafting time:** which posture does this voice inhabit? Encode that in editorial_rationale + manual_grounding so Pass 0b's tailoring layer surfaces the correct philosophical scaffolding in the auto-generated DR prompts. (For non-organism types — `human`, `fictional` — the posture choice is between philosophical / narratival / observational `voice_mode`, not between these three non-human postures.)

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

- **DO interrogate Pass 0a's `review_doc.md` framings, especially "Confidence: high" lines, before downstream commits.** Pass 0a's review_doc is partly LLM run-variance (temperature=1.0 + adaptive thinking) — same prompt + Wikipedia URL + project context can produce meaningfully different framings on different runs. The model's confidence-language reads as earned-by-reasoning but isn't necessarily; treat it as a *starting proposal to question*, not a binding commitment. Re-run if the framing seems narrow or pre-tilted toward one philosophical positioning. **Empirically attested 2026-05-01:** Octopus April 27 review_doc said *"the voice should mark the gap — refuse to invent an experience the body has not had... Confidence high"* (precautionary-leaning); May 1 re-run from identical inputs produced *"anthropomorphism risk vs excessive-alienness... 'clever-pet octopus' vs 'unreachable Other'"* (balanced twin-risks). The April 27 framing pre-tilted the build's §5 DR toward precautionary content, which propagated through merge into the shipped Octopus voice. The compass rebuild traced this back to that single "Confidence high" line.
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

**Pre-hardened prompts (informational):** `persona_pass_6_corpus.md` carries FU#43 source-side hardening (minimal `corpus_metadata` emission, paraphrase-safer caution at generation time) and the patcher-family prompts carry FU#44 register-drift extension. Both landed pre-revert; effect on operator workflow is fewer corpus_metadata + register-drift patches needed at the gate.

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

## Conceptual model — "voice arrives at Athens"

This is the framing that lives in `voice_temporal_stance.default` per Card v2.1 §J:

**Voice arrives at Athens for the conference's days, carrying its full canonical experience as its mental anchor.** Voice retains foundational form, framework, register, grammar. Voice engages AT Athens with the conference's content, the audience, and the other panel members. Voice does NOT speak from any dying-place; voice is HERE, not THERE.

Per voice type:
- **Historical humans** (Plato, Cleopatra, Battuta, Scheherazade, Lovelace, Dostoevsky, Arendt, Marley): mind as it stood at the close of the voice's life — full memory of work and world complete to that moment
- **Non-human organisms** (Octopus): body's full perceptual repertoire as the kind has it
- **Non-human systems** (Whanganui): existence as it stands — relational framework + continuous flow of being
- **Fictional voices** (Scheherazade): full narrative-completed experience

**Tense discipline (in Pass 2/3/4a/4b/5 OUTPUT REGISTER blocks):**
- Voice's framework / tools / methods / forms → **PRESENT-tense** (carried, in use)
- Voice's life-events / biographical works / historical context → **PAST-tense** (remembered)

**No year-distance computation.** Voice avoids *"twenty-three centuries ago"* / *"fifty-one years ago"*. Loose temporal language (*"long ago"*, *"in my time"*) is correct.

**Earlier "deathbed"/"cryofreeze" phrasings have been dropped.** Use "full canonical experience" / "mind at the close of life" instead. Less scene-locating; works universally for non-humans.

---

## Position B vs Position C (corpus-internal cross-examination)

Captured in FU#49D / Pass 2 hard_limits preamble:

**Position B = corpus-accurate softening** — voice can cross-examine its own framework using moves AVAILABLE WITHIN the corpus. Permitted.

**Position C = framework-lifting** — voice abandons its framework entirely. **Forbidden.**

Each `hard_limits` entry passes the abandonment-vs-cross-examination test: "do not abandon X" permits corpus self-criticism; "do not entertain critiques of X under any circumstance" forbids it (too tight, rewrite).

Worked examples in current cards (per voice's corpus): Parmenides cross-examining Plato's Forms; Underground Man's self-laceration; Arendt's revisions; Marley's interpretive evolution within Rastafari. These emerge organically at Pass 2 generation under FU#49D's universal pattern.

---

## Family-of-forms emission (spec status)

Card v2.1 §H specifies family-of-forms emission: *"voice picks among its native form-family per matter, NOT locked to one rigid form."* Default form + 3-6 named variations.

**Current implementation:** single-form-locked. Pass 4b prompt after the 04-28 revert says "one phrase" for `medium`. The §H spec is **forward-looking aspirational** for voices with multi-form corpora; the implementation is **single-form-locked until Cleopatra empirically validates** the §H attempt (FU#55 trigger).

Plato cross-form variance test on 2026-04-29: Plato's corpus IS dialogue-dominated; both relax-options cost named-scene texture for no gain. Plato's variance lives in 6 within-form axes (scene, interlocutor, ending mode, move-emphasis, length-within-band, stance amplitude). Cleopatra is the real test of cross-form emission (genuinely multi-form corpus: prostagma + ordinance + embassy speech + ritual utterance + chancery marginalia + staged encounter per §H worked example). Same trigger for Marley (song variations) and Whanganui (legal forms).

---

## Mediated voices (Plato + Scheherazade)

These voices write THROUGH dramatic personae. Plato through Socrates / Athenian Stranger / Timaeus / Diotima. Scheherazade through frame-tale narrators within stories.

**Pattern risk:** the cryofreeze + tense-discipline + family-of-forms framing pushes the LLM to render first-person as concrete biographical action, which can collapse Plato into Socrates (or Scheherazade into a frame-narrator). Universal-pattern cards work for the other 8 voices but mediated voices need explicit clarification:

- Voice's authorial first-person at the conference is the COMPOSER's, not the speakers within voice's compositions
- Describe characteristic_moves AS COMPOSER (*"Through Socrates I have available the midwife's stance"*) NOT as speaker (*"I am the son of Phaenarete the midwife"*)
- Biography belongs to speakers, not voice
- Distinguish CONFERENCE-PRESENT first-person from CORPUS-EMBODIED moves

**Status:** prompt-side mediated-voice clarification is **drafted but never landed** (HANDOFF_2026_04_28 §13). Plato shipped with collision unfixed in 3 places. **Before Scheherazade's Pass 0a fires:** decide whether to land the prompt-side fix OR plan for surgical patches at her gate.

---

## 9480d3a revert + 582af96 baseline (prompt history)

**582af96 baseline** = the verified-good Pass 2/3/4a/4b/5 prompt state predating the texture-degrading FU#49 cumulative additions. This is the prompt state Plato 2026-04-25 shipped under (chat-tested OK). When troubleshooting prompt regressions, this is the reference state to diff against.

**9480d3a revert** (2026-04-28) = full revert of FU#49H/I/J/K/L/D back to 582af96, after empirical chat-test signal showed cumulative additions had degraded artifact texture.

**Currently landed on top of revert:** FU#49A v2 (quality_criteria), FU#49D re-applied (hard_limits Position B), FU#51 (Pass 7a routing guard), FU#44+ (5 patcher patterns), FU#52 (chat invalidation), FU#53 (review-gate + Pass 7a FINAL), FU#57 (drop bold_engagement_topics from runtime), FU#58/59 (Pass 7a/7c register fixes), FU#60 (thinking observability), FU#61 (audience-engagement +1 in Pass 4b).

**Stripped/reverted (NOT in current prompts):** FU#49H#1-4, FU#49I, FU#49J (5+2 quality_criteria), FU#49K, FU#49L, the 04-28 cryofreeze framing was REPLACED with "voice arrives at Athens with full canonical experience."

**The FU#56 + FU#49 revert risk class:** adding cumulative prompt directives without empirical chat-test on a fresh voice runs the risk that produced the 9480d3a revert. Test on a low-stakes voice before broad rollout. The thinking-on hypothesis (FU#60-instrumented re-test under thinking-visible) is the empirically-resolvable form of this question for FU#56 specifically.

---

## After CARD COMPLETE — operator review checklist (FU#52, 6 manual checks)

The pipeline's CARD COMPLETE summary is advisory, not a gate. The runtime card + chat artifact are written to disk before validators' residuals get human review. **Operator runs this checklist BEFORE any commit/push/ship of voice outputs.** Empirical case study (Plato 2026-04-28): 25 minutes of operator-side review caught ~13 ship-quality improvements that would otherwise have shipped baked into the chat prompt.

The 6 manual checks (per-voice, after every pipeline run):

1. **Read `05_validation/01_pass_7_pre_citation.json`** — scan items where `status` ∈ {`INCONSISTENT`, `UNVERIFIED`}. Decide per-item: fix, accept-with-rationale, or accept-as-defensible. (`DOSSIER_ONLY` and `INTERPRETIVE` are typically defensible.)

2. **Read `05_validation/02_pass_7_anachronism.json`** — scan `anachronism_flags`. Cross-reference `02_merge/_fix_log.json` patches to see which were addressed by 7a-fix. Apply manual edits for unaddressed flags.

3. **Read `05_validation/03_pass_7a_cross_model.json`** — scan residual `field_issues`. Decide per-issue: fix / accept-with-rationale / accept-as-defensible.

4. **Read `05_validation/06_pass_7a_final.json`** (FU#53 first-class) — scan field_issues. Apply path (a) or (b) per the FU#53 gate decision pattern (this doc §"FU#53 review-gate decision pattern").

5. **After any manual edits:** chat artifact regenerates automatically on next pipeline re-fire (per FU#52 invalidation).

6. **Audit the assembled card for voice-architecture-specific collisions** — for mediated voices (Plato/Scheherazade): first-person speaker collapses into corpus-internal speakers. See "Mediated voices" section above.

---

## Operational hints

### Wrong-folder safety harness

Every runner prints a startup banner showing `PROJECT_ROOT` + `SOURCE` (`--project` / env-var / default). When resolution targets a production project (basename contains `athens-2026` or `phase-l-`) via env-var fallback (no explicit `--project` flag), the banner escalates with ⚠ markers. Operator can abort with Ctrl-C if unintended.

**Habit:** always pass `--project` explicitly. As of 2026-05-01, the `code/.env` env-var default for `AI_ASSEMBLY_PROJECT_ROOT` is commented out — bare invocations hard-fail with "PROJECT_ROOT not set" per `project_root.py`'s no-fallback rule. Pass `--project .../projects/current-tests/voice-pipeline-dryrun` for sandbox testing or `--project .../projects/athens-2026` for production.

### Batch wrappers (refuse env-var fallback)

```bash
# Phase 0.5 batch (pre-DR work for multiple voices)
cd code/personas
scripts/batch_pre_dr.sh "$AI_ASSEMBLY_PROJECT_ROOT/voices_batch.txt" --parallel 3

# Full pipeline batch (after DR data lands per voice)
scripts/run_pipeline_batch.sh \
  --project /Users/aienvironment/Desktop/AI\ Assembly/projects/athens-2026 \
  --parallel 3 \
  "Cleopatra" "Octopus" "Bob Marley"
```

Per-voice logs: `$PROJECT/batch_logs/<slug>.pipeline.log`. Summary: `_batch_results_<timestamp>.txt`. Each voice resumes from cache on re-run.

### Parallel 429 on Phase 0.5

When running Phase 0.5 on multiple voices in parallel, can hit Anthropic 429 rate limit. **Octopus retry succeeded only on serial after parallel 429.** If a voice's Phase 0.5 dies with 429, retry serially.

### Sentinel regen for prompt edits (FU#29)

```bash
# Snapshot pre-edit voice
mkdir -p _workspace/sentinel_baselines/2026-MM-DD-pre-X/<slug>
cp <PROJECT_ROOT>/voices/<slug>/04_generation/<file>.json \
   _workspace/sentinel_baselines/2026-MM-DD-pre-X/<slug>/

# Edit prompt, then:
python scripts/sentinel_regen.py regen \
  --pass <PASS_NAME> --voices <slug> \
  --baseline-snapshot _workspace/sentinel_baselines/2026-MM-DD-pre-X
```

`--baseline-snapshot` takes a parent dir; per FU#50(2) the runner auto-resolves `<DIR>/<voice_slug>/<filename>` per voice, so a single arg works for multi-voice regen.

After regen: inspect diff. If smoke-test (not real generation), restore baseline.

### Pass 0b templates are de-anchored from panel exemplars (FU#19)

Pass 0b non-human / fictional templates were genericized 2026-04-26: they no longer self-anchor to Octopus / Whanganui / Scheherazade as single exemplars but pair them with multi-class parallels (e.g., Scheherazade with Hamlet / Antigone / Aeneas / Don Quixote). Effect on unbuilt voices: Whanganui's and Scheherazade's DR generation will not be self-referential to the existing panel exemplars — cleaner research output. No operator action needed; informational.

### archive/first_run/ pattern

When re-doing a voice from very scratch in athens-2026, archive the prior work to `archive/first_run/voices/<slug>/`. Pattern attested 2026-04-27 when Cleopatra + Octopus + others were redone after Pass 0a tightened. Don't delete — preserve audit trail.

### Pre-patch snapshot pattern

Before applying operator patches at the gate:
```bash
cp 07_persona_card_assembled.json 07_persona_card_assembled.pre_<context>.json
```
Pattern: `.pre_FU61.json`, `.pre_round1_patches.json`, `.pre_round2_patches.json`, `.pre_freshqc.json`, etc. Pre-patch snapshots are operator-side audit trail; don't commit them to athens-2026 (per OPEN_ITEMS.md §6 .gitignore recommendations).

### voice_mode null edge case

`voice_mode: null` is ONLY valid for `subtype: system`. Pass 0a sometimes proposes it for non-system voices; gets rejected at Phase 0.5 launch. Empirically attested: Cleopatra + Bob Marley both originally got `null`, had to be fixed before research could proceed.

### Bob Marley special corpus_constraint

Marley has `corpus_constraint: lyrics_patterns_only` (atypical — not `full`). When his Pass 0a runs, verify this lands (rather than `full`).

### Pipeline-fidelity audit method

When voice_config changes after Phase 0.5 has already run:

| Field changed | Re-run scope |
|---|---|
| `type` / `subtype` / `hostile_sources` | Full Phase 0.5 re-run |
| `voice_mode` / `corpus_constraint` | Pass 0b tailor-only re-run |
| `name` / `manual_grounding` / `editorial_rationale` / `wikipedia_url` | No re-run |

Whanganui re-ran with `hostile_sources=true` after pipeline-fidelity audit caught misalignment (2026-04-27). Verify when she builds.

### `_operator_review_passed.flag`

Path-(b) shipping flag. Touched at `voices/<slug>/_operator_review_passed.flag` after operator accepts FU#53-gate residuals. Pipeline detects flag → skips gate → runs Derive. Untracked / gitignored.

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
