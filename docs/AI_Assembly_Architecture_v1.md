# AI ASSEMBLY — Architecture (v1)

**Project:** The AI Assembly · World Beautiful Business Forum · Athens · May 7–10, 2026
**Audience:** The person building this in n8n.
**Purpose:** System map. What runs when, what feeds what, where the documents fit.

---

## The Seven Documents

| Document | Filename | What it is |
|---|---|---|
| **Architecture** (this document) | `AI_Assembly_Architecture.md` | System map for the builder. |
| **Persona Card** | `AI_Assembly_Persona_Card_v2.md` | 37 runtime fields per voice, 8 sections. Output of the Persona Pipeline, input to the Voice Pipeline. |
| **Persona Pipeline** | `AI_Assembly_Persona_Pipeline_v3_10.md` | Automated agent pipeline for building each voice. 7 passes, 4 models, parallel across 12 voices. Runs pre-conference. |
| **Transcription Pipeline** | `AI_Assembly_Transcription_Pipeline.md` | Turns recorded sessions and participant reflections into clean, named transcripts. First stage of the overnight chain. Runs overnight. |
| **Researcher Pipeline** | `AI_Assembly_Researcher_Pipeline.md` | Processes conference transcripts into extraction tables. Runs overnight. |
| **Provocateur Pipeline** | `AI_Assembly_Provocateur_Pipeline.md` | Formulates provocations and packages per-voice briefings. Runs overnight. |
| **Voice Pipeline** | `AI_Assembly_Voice_Pipeline.md` | Runs each voice: private thinking + public expression. Reads the Persona Card. Runs overnight. |

---

## Two Phases

### Pre-Conference (weeks before Athens)

Build the voices. Fully automated n8n pipeline, parallel across all 12 voices.

```
Input per voice:
{
  "name": "Plato of Athens",
  "quadrant": "Q1",
  "type": "human"
}
    │
    ▼
┌───────────────────────────────────────────────┐
│  PERSONA PIPELINE (×12 voices, parallel)       │
│                                                │
│  Pass 1a: Perplexity API — research dossier    │
│  Pass 1b: Gemini API — broad scan (parallel)   │
│  Merge: Claude — contradiction check           │
│                                                │
│  Pass 2: Claude — Identity & Boundaries  [9]   │
│  Pass 3: Claude — Intellectual Core      [5]   │
│    (+ChatGPT DR conditional)                   │
│  Pass 4: Claude — Voice & Expression    [15]   │
│  Pass 5: Claude — Engagement             [4]   │
│  Pass 6: Claude — Corpus Curation        [1]   │
│                                                │
│  Pass 7-pre: Claude — citation verification    │
│  Pass 7a: ChatGPT — cross-model validation     │
│  Pass 7b: Claude/ChatGPT DR — provocations [1] │
│  Pass 7c: Claude — negative constraints  [2]   │
│                                                │
│  Derive: Provocateur Profile + Eval Rubric     │
└───────────────────────────────────────────────┘
    │
    ▼
Persona Card (37 fields per voice)
    +
Provocateur Profile (5 fields per voice)
Evaluation Rubric (9 test prompts per voice)

    │
    ▼
┌───────────────────────────────────────────────┐
│  CROSS-PERSONA QC (once, after all 12)         │
│  Swap test, blind ID test, same-question test  │
│  Tool: ChatGPT (cross-model)                   │
└───────────────────────────────────────────────┘
```

**n8n:** One workflow triggered per voice. Each workflow runs 13+ API calls across 4 providers (Perplexity, Gemini, Claude, ChatGPT). All 12 workflows run in parallel. A separate batch workflow runs cross-persona QC after all complete.

**Cost:** $100–130 total for all 12 voices (Claude Batch API pricing).

---

### Overnight (2 nights during conference)

Process the day's conference material through the council. Runs automatically.

```
Conference Day 1 recordings
    │
    ▼
┌───────────────────────────────────────────────┐
│  AUDIO → CLEAN TRANSCRIPTS  (Prefect, not n8n) │
│                                                │
│  Stage 0: Ingest from upload location          │
│  Stage 1: AssemblyAI Universal-3 Pro           │
│           ASR + diarization, ≤50 speakers      │
│           language_detection on (Greek etc.)   │
│           (NO audio enhancement — raw only)    │
│  Stage 2: Claude Sonnet — speaker ID           │
│           Multi-pass LLM attribution           │
│           (cues → roles → expertise → linking) │
│  Stage 3: Claude Sonnet — transcript cleaning  │
│           Strict no-paraphrase constraints     │
│  Stage 4: Validation + human review queue     │
│                                                │
│  Output: clean named transcripts → shared     │
│          folder (S3 / GDrive / local)         │
│  Runtime: 10–15 min for ~9 hrs of audio        │
│  Cost: $4–6 per night                         │
│                                                │
│  See: AI_Assembly_Transcription_Pipeline.md    │
└───────────────────────────────────────────────┘
    │  (file-based handoff to n8n)
    ▼
┌───────────────────────────────────────────────┐
│  RESEARCHER PIPELINE                           │
│  Input: clean transcripts                      │
│  Process: extraction + themed grouping         │
│  Output: extraction table                      │
│  Model: Claude Sonnet (1 call per session)     │
└───────────────────────────────────────────────┘
    │
    ▼
┌───────────────────────────────────────────────┐
│  PROVOCATEUR PIPELINE                          │
│  Input: extraction table + Provocateur         │
│         Profiles + Night 1 data (Night 2)      │
│  Process: triage → select → formulate →        │
│           package per-voice briefings           │
│  Output: per-voice briefing packages           │
│  Model: Claude Sonnet (multiple calls)         │
└───────────────────────────────────────────────┘
    │
    ▼
┌───────────────────────────────────────────────┐
│  VOICE PIPELINE (×12 voices, parallel)         │
│                                                │
│  For each voice:                               │
│                                                │
│  Step 1: Private Thinking                      │
│    Parallel per formulation (~3 each)          │
│    System prompt: Foundational + Reasoning +   │
│      Engagement fields from Persona Card       │
│    User prompt: per-voice briefing package      │
│    Output: detailed response per formulation    │
│                                                │
│  [Optional] Validation:                        │
│    Anachronism check vs knowledge_boundary     │
│    Constitutional check vs constitution        │
│    Regenerate if issues found                  │
│                                                │
│  Step 2: Public Expression (once per voice)    │
│    System prompt: Foundational + Voice +        │
│      Artifact fields from Persona Card         │
│    User prompt: all detailed responses          │
│    Output: 1 artifact per voice                │
│                                                │
└───────────────────────────────────────────────┘
    │
    ▼
┌───────────────────────────────────────────────┐
│  DOWNSTREAM PIPELINE                           │
│                                                │
│  Stage A: Render                               │
│    Text artifacts: pass-through                │
│    Marley: Suno API → audio file               │
│    Octopus: package shader params              │
│    (+ future multimedia voices)                │
│                                                │
│  Stage B: Publish to micro-site                │
│    Write artifacts as JSON to content repo     │
│    (GitHub), commit + push                     │
│    Vercel auto-rebuild → permanent URLs        │
│    (/night-1/plato, /night-1/marley, …)        │
│                                                │
│  Stage C: Curate newsletter  (Nights 1 & 2)    │
│    Claude Opus, HoBB style few-shot            │
│    Input: 12 artifacts + micro-site URLs       │
│    Output: HTML newsletter in HoBB voice       │
│    Night 3: SKIPPED (closing show reveals)     │
│                                                │
│  Stage D: Deliver                              │
│    POST to HoBB email tool API                 │
│    Fallback: HTML file to shared folder        │
└───────────────────────────────────────────────┘
    │
    ▼
┌───────────────────────────────────────────────┐
│  CONTINUITY GENERATION (after Night 1 only)    │
│  1 API call per voice                          │
│  Input: all Night 1 output for that voice      │
│  Output: 2 continuity fields inserted into     │
│          Persona Card for Night 2              │
└───────────────────────────────────────────────┘
```

---

## Data Objects

These are the things that move between pipeline stages.

### Persona Card
- **Created:** Pre-conference by the Persona Pipeline
- **Consumed by:** Voice Pipeline (system prompt assembly)
- **Structure:** 37 fields across 8 sections:
  - IDENTITY (5): council_member_name, epistemic_frame_statement, world, formative_experience, character
  - CONSTITUTION (3): constitution, concept_lexicon, curated_corpus_passages
  - BOUNDARIES (4): knowledge_boundary, translation_protocol, topics_requiring_care, hard_limits
  - REASONING (4): reasoning_method, finds_compelling, resists, worked_provocations
  - ENGAGEMENT (4): bold_engagement_topics, default_questions, disagreement_protocol, unique_contribution
  - VOICE (7): rhetorical_mode, characteristic_moves, register_and_tone, metaphorical_repertoire, preferred_vocabulary, banned_language, banned_modes
  - ARTIFACT (8): medium, technical_capabilities, characteristic_output_structure, relationship_to_detailed_response, aesthetic_qualities, stance_tendency, length_and_format_constraints, quality_criteria
  - CONTINUITY (2): continuity_block_if_night_2, continuity_block_artifact_if_night_2
- **Field distribution in Voice Pipeline:**
  - Foundational (both steps): Identity + Constitution + Boundaries = 12 fields
  - Step 1 only: Reasoning + Engagement + Continuity(1) = 9 fields
  - Step 2 only: Voice + Artifact + Continuity(1) = 16 fields
- **Storage:** JSON per voice, accessible to n8n.
- **Mutated:** Night 2 only — 2 continuity fields populated after Night 1.

### Provocateur Profile
- **Created:** Pre-conference by the Persona Pipeline (derived output)
- **Consumed by:** Provocateur Pipeline (triage, selection, formulation)
- **Structure:** 8 fields: speaks_from, core_commitment, activates_on, goes_flat_on, stretch, translation_range, stance_tendency, medium
- **Storage:** Loaded into the Provocateur's system prompt as a roster.

### Extraction Table
- **Created:** Overnight by the Researcher Pipeline
- **Consumed by:** Provocateur Pipeline
- **Structure:** Per-session table of positions, tensions, questions, reframings. See Researcher Pipeline.

### Per-Voice Briefing Package
- **Created:** Overnight by the Provocateur Pipeline
- **Consumed by:** Voice Pipeline (user prompt for Step 1)
- **Structure:** ~3 formulations per voice, each with theme context and extraction material as JSON. See Provocateur Pipeline.

### Detailed Response
- **Created:** Overnight by the Voice Pipeline (Step 1 — Private Thinking)
- **Consumed by:** Voice Pipeline Step 2 (artifact input), downstream pipeline
- **Structure:** JSON per formulation: council_member, night, theme_id, formulation_text, detailed_response.

### Artifact
- **Created:** Overnight by the Voice Pipeline (Step 2 — Public Expression)
- **Consumed by:** Downstream Pipeline (Render → Publish → Curate → Deliver)
- **Structure:** JSON per voice per night: focus_decision, stance, artifact_type, artifact_title, artifact_text, word_count. For multimedia voices, `artifact_text` carries the generator input (Suno prompt, shader params JSON) rather than final rendered output.

### Continuity Block
- **Created:** After Night 1 completes (1 API call per voice)
- **Consumed by:** Voice Pipeline on Night 2 (inserted into system prompts)
- **Structure:** 4 fields: positions taken, key moves, unresolved threads, artifact focus and stance.
- **Split across steps:** Positions/moves/threads → Step 1 prompt. Artifact focus/stance → Step 2 prompt.

---

## n8n Workflow Structure

### Night 1

```
1. Trigger: manual or scheduled (after conference day ends)

2. Audio → Clean Transcripts  (PREFECT, not n8n)
   - Stage 0: Ingest audio files from upload location
   - Stage 1: AssemblyAI Universal-3 Pro (batch, concurrent)
     · speaker_diarization: true
     · max_speakers_expected: per-session metadata
     · language_detection: true (essential — some walking
       sessions may be in Greek)
     · Promptable: "Conference panel, business philosophy,
       international English speakers"
     · Custom vocabulary: all panelist names pre-loaded
     · NO audio enhancement upstream
   - Stage 2: Claude Sonnet — speaker identification
     · Input: diarized transcript + roster + bios
     · Output: {label → name, confidence, evidence}
     · Temperature 0.0, structured output
   - Stage 3: Claude Sonnet — transcript cleaning
     · Strict no-paraphrase, preserve substance + turns
     · Temperature 0.0–0.2, structured output
   - Stage 4: Validation, human review queue for low-conf IDs
   - Handoff: clean transcripts written to shared folder;
     n8n file trigger picks them up for step 3
   - Full logic and prompts: AI_Assembly_Transcription_Pipeline.md

3. Researcher  (n8n from here on)
   - Input: clean transcripts from Prefect output folder
   - Claude Sonnet API via n8n HTTP Request node
     (NOT the Anthropic sub-node — see research #3)
   - Output: extraction table → stored

4. Provocateur
   - Input: extraction table + all Provocateur Profiles
   - Claude Sonnet API (multiple calls: triage → selection → formulation → packaging)
   - Output: per-voice briefing packages → stored

5. Voice Pipeline (parallel branch per voice)
   For each of 12 voices:
   
   5a. Load Persona Card for this voice
   5b. Build Step 1 system prompt (Foundational + Reasoning + Engagement fields)
   5c. Build Step 2 system prompt (Foundational + Voice + Artifact fields)
   5d. For each formulation (parallel):
       - API call: Step 1 system prompt + single formulation as user prompt
       - [Optional] Validation: anachronism + constitutional check
       - Store detailed response
   5e. Collect all detailed responses for this voice
   5f. API call: Step 2 system prompt + all detailed responses as user prompt
       - Store artifact
   
6. Downstream
   6a. Render
       - Text artifacts: pass-through
       - Marley: Suno API call (HTTP Request), retry 3x,
         fallback to lyrics sheet if API fails
       - Octopus: package shader params alongside shader code
   6b. Publish
       - Aggregate all 12 artifacts into night-N.json
       - GitHub API: commit + push to content repo
       - Vercel webhook rebuilds micro-site (~30s)
   6c. Curate (Nights 1 & 2 only — SKIP Night 3)
       - Claude Opus API via HTTP Request node
       - System prompt: HoBB style few-shot (3–5 real newsletters)
       - User prompt: artifacts + micro-site URLs
       - Output: HTML newsletter in HoBB editorial voice
   6d. Deliver
       - POST to HoBB email tool API
       - Fallback: write HTML to shared folder for human copy-paste

7. Continuity generation
   - For each voice: 1 API call
   - Input: all Night 1 output for that voice
   - Output: continuity block → write into Persona Card for Night 2
```

### Night 2

Same as Night 1, with:
- **Provocateur** receives Night 1 formulations to avoid repetition
- **Voice Pipeline** system prompts include continuity blocks

### Day 3

No overnight run. Day 3 closing programme reveals Night 2's output.

---

## API Calls Per Night (Estimate)

| Stage | Calls | Model | Notes |
|---|---|---|---|
| Transcription (AssemblyAI) | 6–9 | Universal-3 Pro | 1 per session, Prefect orchestrated |
| Speaker ID | 6–9 | Sonnet | 1 per session, temp 0.0 |
| Transcript cleaning | 6–9 | Sonnet | 1 per session, temp 0.0–0.2 |
| Researcher | 3–6 | Sonnet | 1 per session |
| Provocateur | 5–10 | Sonnet | Triage + selection + formulation + packaging |
| Voice Step 1 | ~36 | Per-voice (see Persona Card) | ~3 formulations × 12 voices |
| Voice Validation (optional) | ~36 | Sonnet | Same count as Step 1, if enabled |
| Voice Step 2 | 12 | Per-voice (see Persona Card) | 1 per voice |
| Render (Suno) | 1–2 | Suno API | Marley + future musical voices |
| Publish (GitHub) | 1 | GitHub API | Single commit per night |
| Curate newsletter | 1 | Opus | Nights 1 & 2 only; skipped Night 3 |
| Deliver (email tool) | 1 | HoBB tool API | TBD which tool |
| Continuity (Night 1 only) | 12 | Sonnet | 1 per voice |
| **Total** | **~115–160** | | |

**Cost estimate per night:** Audio pipeline $4–6 + overnight LLM pipeline $20–50 / $10–25 with Batch API + Suno $0.50–2 + newsletter Opus call ~$0.50 = **$25–60 total per night** (Night 3 slightly lower, no newsletter).

---

## Model Routing

**Overnight pipeline:** Model assignment is **per-voice and per-step**, not pipeline-wide. Each Persona Card specifies which model to use for Step 1 (Private Thinking) and Step 2 (Public Expression) for that voice. n8n reads these fields and routes accordingly. Sonnet is the common default; Opus is used where a voice benefits from it (e.g., Marley Step 1, Ibn Battuta Rihla entries). Researcher, Provocateur, and Continuity stages default to Sonnet.

**Pre-conference pipeline:** Multi-model. Perplexity (research dossier), Gemini (broad scan), Claude (generation passes), ChatGPT (cross-model validation + conditional supplements). See Persona Pipeline for full tool-to-pass mapping.

---

## Orchestration Split

**The overnight pipeline uses two orchestrators, not one.**

- **Prefect** runs Stage 0–4 (audio → clean named transcripts). Python-native, handles FFmpeg, batch API polling, retries, and parallel fan-out across sessions. n8n is unsuitable here — 25MB file limit, no native audio processing, weak async polling. See `AI_Assembly_Transcription_Pipeline.md` for stage logic and prompts.
- **n8n** runs everything from Researcher onward (extraction → Provocateur → Voice Pipeline → Continuity → Downstream). The handoff is file-based: Prefect writes clean transcripts to a shared folder; an n8n file trigger picks them up.

For n8n Claude calls throughout, use the **HTTP Request node** (`https://api.anthropic.com/v1/messages`), never the native Anthropic sub-node. The sub-node exposes only 4 parameters and lacks structured outputs, extended thinking, and stop_sequences. Set HTTP Request timeout to **300,000ms (5 min)** minimum; self-hosted n8n may enforce a 2-minute proxy ceiling regardless of node settings — test this before Athens.

---

## Downstream Pipeline

The four stages that run after the Voice Pipeline produces 12 artifacts per night. All four live in n8n.

### Stage A — Render

Most artifacts are text and pass through unchanged. Two need rendering work:

- **Marley (Suno).** n8n calls the Suno API with the artifact as prompt input. Songs take a few minutes to ~15 minutes depending on queue. Retry 3× with exponential backoff. **Fallback:** if Suno fails, publish the lyrics sheet as a text artifact so Marley is not silent. Other future musical voices follow the same pattern.
- **Octopus (chromatophore shader).** The artifact is a JSON parameter block. No server-side rendering — the shader runs client-side in the browser. Stage A just packages the params alongside the shader code for deployment in Stage B.

Additional multimedia voices (illustrations, TTS voice-overs, etc.) slot in here as new Switch branches on artifact type.

### Stage B — Publish to micro-site

The micro-site is a **pre-built static web app** that must exist before Athens. n8n cannot build a website — it only writes content into one that exists. Architecture:

- **Content store:** git repository with one JSON file per night (`night-1.json`, `night-2.json`, etc.) plus audio and shader assets. Simple, version-controlled, free, n8n writes to it via the GitHub API.
- **Framework:** Astro or Next.js, static build, deployed to Vercel or Netlify with auto-rebuild on git push.
- **Structure:** per voice, then per night (decision locked). Each artifact gets a permanent URL: `/night-1/plato`, `/night-1/marley`, `/night-2/arendt`, etc. Navigation pattern through the Assembly is TBD — to be designed in Lovable/v0 prototyping.

n8n's Stage B job: aggregate the night's rendered artifacts into `night-N.json`, commit + push to the content repo, wait for Vercel rebuild confirmation (~30s), emit the permanent URLs to Stage C.

### Stage C — Curate newsletter (Nights 1 & 2 only)

Single Claude Opus call via n8n HTTP Request node.

- **System prompt:** 3–5 real HoBB newsletters as few-shot style exemplars + editorial voice instructions. The newsletter is from **HoBB editorial voice**, not from the Assembly as a named entity — HoBB reports on what the Assembly produced.
- **User prompt:** all 12 artifacts with their micro-site URLs + night context.
- **Output:** HTML newsletter walking through each voice with a pull-quote and a deep link back to the micro-site, signed off in HoBB voice.
- **Night 3: SKIPPED.** The closing show on Day 3 reveals Night 2's output live; a newsletter would pre-empt it.

Style-matching is the only non-trivial part. Plan for test runs with real HoBB newsletters as exemplars before Athens and iterate on the prompt until Claude hits the register without drifting into generic AI newsletter prose.

### Stage D — Deliver to HoBB email tool

n8n POSTs the HTML to HoBB's email tool API. Specific integration depends on which tool HoBB uses — Mailchimp, Campaign Monitor, HubSpot, Substack, Beehiiv, and Ghost all have REST APIs that n8n can hit directly, several with native nodes. **Action item:** 30-minute investigation with whoever runs HoBB's list to confirm the tool and obtain API credentials before Athens.

**Fallback:** if API integration isn't possible, n8n writes the HTML to a shared folder and a human copies it into the tool manually.

---

## Pre-Conference Build Workstreams

Two pre-Athens build workstreams run in parallel to the Persona Pipeline:

### Micro-site build

- **Design prototyping:** Lovable or v0 for rapid iteration on layout, navigation, and the way a reader moves through the Assembly. This is a creative problem, not a technical one.
- **Production codebase:** Cursor or Claude Code to turn the prototype into a proper codebase under your own control. Do not ship a Lovable-hosted app to 750 people.
- **Framework:** Astro (recommended — static by default, content-driven, fast) or Next.js.
- **Hosting:** Vercel or Netlify.
- **Content store:** GitHub repository with JSON-per-night schema defined before build begins.
- **Chromatophore shader:** existing WebGL shader integrates as a component.

### Newsletter style calibration

- Collect 3–5 real HoBB newsletters as exemplars.
- Draft the Stage C system prompt with few-shot examples.
- Run test generations against sample Voice Pipeline artifacts.
- Iterate until style fidelity is acceptable; lock the prompt before Athens.

---

## Recording Protocol (Pre-Conference)

Three procedural steps have more impact on transcript quality than any technology choice and must be in place before Athens:

1. **Moderators brief to introduce all panelists by full name** at the start of every session. This single step raises LLM speaker-ID accuracy from ~50% to 70–85%.
2. **Walking-session participants state their names at the start** of each reflection recording. Converts an unreliable inference problem into trivial extraction.
3. **All panelist names, affiliations, and session-specific terminology pre-loaded** into AssemblyAI custom vocabulary before the conference. Catches Greek, Indian, and compound proper nouns that ASR routinely mangles phonetically.

Budget **15–30 minutes of human review per night** for medium/low-confidence speaker attributions flagged in Stage 4. This is the irreducible manual step.

**Decision: no voiceprint enrollment.** The alternative — collecting 30–60s voice samples from ~30–40 named speakers before Athens and matching via pyannoteAI Precision-2 — would raise speaker-ID accuracy but requires pre-event logistics we're not taking on. Precise speaker attribution is not load-bearing for the artifacts: the Researcher extracts positions, tensions, questions, and reframings as *content*, and the Voice Pipeline produces artifacts from thematic material, not speaker-stamped quotes. An anonymous-label transcript with 60–80% named attribution is good enough. If a handful of positions end up misattributed or unattributed, nothing downstream breaks.

---

## Error Handling

| Stage | On failure | Consequence |
|---|---|---|
| AssemblyAI transcription | Retry via Prefect (3×, exponential backoff). Fall back to Speechmatics for heavily accented segments. | Blocking — downstream cannot proceed. |
| Speaker ID (LLM pass) | Leave anonymous labels (`SPEAKER_01`…); flag for human review. | Researcher runs with anonymous attribution. |
| Transcript cleaning | Pass raw diarized transcript through. | Slightly noisier input to Researcher. |
| Voice Step 1 | Retry once. If retry fails, skip formulation. | Voice produces fewer detailed responses. Artifact still runs. |
| Voice Validation | Skip validation. | Unvalidated output proceeds. |
| Voice Step 2 | Retry once. If retry fails, log. | Voice has no artifact for the night. Detailed responses still available. |
| Suno render | Retry 3× with backoff. On final failure, publish lyrics sheet as text artifact. | Marley produces text not audio for that night. |
| GitHub publish | Retry 3×. On failure, write JSON to shared folder. | Micro-site not updated automatically; manual commit required. |
| Newsletter curation | Retry once. | Night's newsletter generated from fallback template or skipped. |
| Email delivery | Retry 3×. On failure, write HTML to shared folder. | Manual send via HoBB's email tool. |
| Researcher / Provocateur | Retry. | Blocking — pipeline cannot proceed without output. |
| Continuity generation | Retry once. Skip on failure. | Night 2 runs without continuity for that voice. |

---

## What This Document Does NOT Cover

- **Conceptual framing** (what the Assembly means, why it matters) → `AI_Assembly_Briefing.md`
- **How to build a voice** (research, quality standards, prompt templates) → `AI_Assembly_Persona_Pipeline_v3_10.md`
- **What fields a voice needs** (37-field spec with Fidelity / Intrigue / Therefore) → `AI_Assembly_Persona_Card_v2.md`
- **Detailed overnight prompt templates** (system/user prompts with `{{fields}}`) → `AI_Assembly_Voice_Pipeline.md`
- **Transcription pipeline logic and prompts** (stage-by-stage spec, speaker-ID and cleaning prompts, schemas) → `AI_Assembly_Transcription_Pipeline.md`
- **Transcription stack research and benchmarks** (ASR engine comparison, diarization benchmarks, failure modes) → `Conference_Transcription_Pipelines_for_AI_Extraction_at_Scale__2025-2026_Strategic_Analysis.md` + the newer "Overnight conference audio to clean named transcript" report
- **Micro-site visual design and navigation pattern** (how a reader moves through the 12 voices) → to be prototyped in Lovable/v0, not specified here
- **HoBB newsletter style specification** (exact voice, structure, sign-off) → to be calibrated via few-shot exemplars before Athens
- **HoBB email tool identity and API** → 30-min investigation needed with HoBB ops
- **Panel composition** → **locked (12 voices):** Plato, Cleopatra, Ibn Battuta, Scheherazade, Ada Lovelace, Dostoevsky, Hannah Arendt, Bob Marley, Audrey Tang, Peter Thiel, Whanganui River, Octopus
