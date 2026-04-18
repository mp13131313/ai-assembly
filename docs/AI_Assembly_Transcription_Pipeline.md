# THE TRANSCRIPTION PIPELINE
## AI Assembly — Role Specification

**Project:** The AI Assembly · World Beautiful Business Forum · Athens · May 7–10, 2026
**Status:** Conceptual briefing — working draft (v2.1, post-Researcher v2.4 cross-check)
**Purpose:** This document specifies the Transcription stage's function, process, and design constraints in enough detail that a technical team could build and prompt it.

---

## Changelog (v2.1 — Apr 14 2026)

A single additive change from v2, in response to validating Opus 4.7 + adaptive thinking on the Researcher Pipeline (v2.4). The Researcher upgrade produced a large quality improvement for clustering and theming but did not generalize to the Transcription Pipeline's main LLM calls (Cleaning, drift verification). Speaker ID was the only Transcription step where Opus could plausibly help edge cases, so it gains a per-run model override.

- **§14** → Step 3 "Speaker Identification" implementation gains an optional `TRANSCRIPTION_SPEAKER_ID_MODEL` environment variable. Defaults to `CLAUDE_MODEL` (i.e. Sonnet 4.6 in the baseline config). Can be set to `claude-opus-4-7` on a per-run basis for difficult sessions — non-native English speakers, complex multi-person Q&A, incomplete roster metadata. Cleaning and semantic drift verification remain on Sonnet; the cost/benefit does not favor Opus for those steps.

Model references throughout the document are unchanged — Sonnet 4.6 remains the default for every LLM call in Transcription.

---

## Changelog (v2 — Apr 14 2026)

This revision integrates findings from three MSC 2026 test sessions (Vox Populi, Breaking Point, West-West Divide) processed end-to-end against the pipeline. The conceptual structure is preserved; the amendments are additive. Each change is traceable to a numbered section of `PROPOSED_pipeline_doc_change.md`:

- **§1** → Step 1 gains an "Audio bitrate normalization" subsection (distinct from the "Audio pre-processing: None" rule, which is preserved).
- **§2, §3, §4** → Step 4 "Cleaning" implementation gains mandatory streaming, per-call `max_tokens` budgets, and an >80% budget warning; Step 3 "Speaker identification" implementation gains an explicit 4,096-token cap.
- **§5** → Implementation Draft gains a Prefect caching note for development runs.
- **§6** → Step 2 "Transcription & Diarization" gains a "Known limit: audience merging during Q&A" subsection.
- **§7** → Step 2 gains a "Multilingual content and live interpretation" subsection.
- **§8, §9** → Step 2 / Node 1 gains explicit `language_detection=True` and SDK 0.59.0 drift workarounds (`config.raw.speech_models`, `keyterms_prompt`).
- **§10** → Step 5 output schema confirms per-turn `confidence` flows through to the Researcher. (No structural change; contract clarified.)
- **§11** → Step 3 Speaker ID prompt gains **PASS 5** (per-turn sanity check) and a `reassigned_turns` flag type in the output schema.
- **§12** → Step 5 output schema gains a "`review_queue` is not orphaned" note explaining that `verify_markers` is consumed by the Researcher (Part B lives in `AI_Assembly_Researcher_Pipeline.md`).
- **§13** → Step 3 gains an "Alternatives considered" subsection recording the investigation of AssemblyAI's native `SpeakerIdentificationRequest`.

Model reference throughout the doc updated from "Claude Sonnet 4" to "Claude Sonnet 4.6".

---

# Overview

The Transcription Pipeline is the first stage in the overnight chain. It receives raw audio recordings of conference sessions — including video files, whose audio track is used and whose visual channel is discarded — and, in some cases, participant reflection recordings that are the only record of a session. It produces clean, speaker-attributed transcripts in the schema the Researcher consumes. It is the bridge between what happened in the room and what the rest of the pipeline can reason about.

The stage takes two kinds of input per session: **program metadata** (title, description, full contributor list with names, titles, and bios) known in advance from the conference program, and **recordings** (audio or video files, plus any participant reflection recordings) delivered after the session ends. It produces one **session package** per session: the program metadata carried forward intact, the list of speakers who actually spoke, and a cleaned transcript with every turn attributed to a named individual. Carrying the metadata forward — rather than discarding it after processing — gives the Researcher session context for extraction and gives downstream stages (Provocateur, Voice) the bios they need to reason about who took which position.

The Transcription Pipeline does not interpret content. It does not select which sessions to process — that's a human editorial decision upstream. It does not extract positions or themes — that's the Researcher. Its sole function is to turn recorded human conversation into a faithful, named, machine-readable record.

The pipeline runs in five steps:

1. **Ingest** — collect recordings and metadata, validate, normalize audio bitrate, fan out to parallel session processing
2. **Transcription & Diarization** — produce a timestamped, speaker-anonymous transcript
3. **Speaker Identification** — map anonymous speaker labels to named individuals using content cues and the contributor roster
4. **Cleaning** — repair ASR errors, remove disfluencies, preserve substance
5. **Validation & Output** — verify, flag low-confidence attributions, deliver the session package

---

## Step 1: Ingest

This step defines how recordings and metadata get into the pipeline. It is the only step where a human is actively in the loop during the conference — everything downstream is automatic.

### Storage

The pipeline lives in a single Google Drive folder. Prefect runs on a VM that mounts the Drive folder locally via `rclone` (not the Google Drive desktop client — see `AI_Assembly_Infrastructure_Setup.md` for the rationale), watches it for new files, and writes its output back into the same mount. There is no separate input/output system.

```
/mnt/drive/
  /metadata/
    sessions.json                                ← frozen pre-conference
  /recordings/
    /day1/
      session_001.m4a
      session_002.mp4
      session_003.m4a
      session_003__reflection__alice.m4a
      session_003__reflection__bob.m4a
    /day2/
      ...
  /transcripts/                                  ← Prefect writes session packages here
    /day1/
      session_001.json
      session_002.json
      session_003.json
  /review/                                       ← human review queue from Step 5
    /day1/
      session_001_review.json
```

### Pre-conference setup (one-time)

Before Athens begins, one file is created and frozen: `/metadata/sessions.json`. It contains one entry per session in the conference program, with all the metadata fields the pipeline needs to carry forward. Once the conference starts, this file is not edited — it is a stable reference.

```json
{
  "sessions": [
    {
      "session_id": "session_001",
      "session_title": "The More-Than-Human Democracy",
      "session_description": "The opening assembly of the Marathon: a fast-paced, Parliament-style gathering of thinkers, activists, technologists, and policy makers who ask what democratic life looks like when it includes nature, artificial intelligence, and the voices of those not yet born.",
      "session_format": "panel",
      "track": "AI Democracy Marathon",
      "date_time": "2026-05-07T14:45:00+03:00/2026-05-07T16:30:00+03:00",
      "venue": "Mikro Pallas",
      "expected_speaker_count": 17,
      "roster": [
        {
          "name": "Mark Aanderud",
          "title": "Composer and Multi-Instrumentalist",
          "affiliation": "Musical Director, House of Beautiful Business / Musical Curator, World Beautiful Business Forum",
          "bio": ""
        },
        {
          "name": "Jon Alexander",
          "title": "Citizen Futurist",
          "affiliation": "Co-founder of the New Citizenship Project / Author of Citizens",
          "bio": ""
        }
      ]
    }
  ]
}
```

The `session_id` is the join key for the entire pipeline. Every recording filename references it; every output file references it; every cross-session lookup uses it.

### Filename convention

Filenames are the only mechanism that connects recordings to metadata. They must be deterministic and parseable:

- **Session recording:** `{session_id}.{ext}` — e.g. `session_001.m4a`
- **Reflection recording:** `{session_id}__reflection__{slug}.{ext}` — e.g. `session_003__reflection__alice.m4a`. The slug can be a participant name, a sequence number, or any short identifier; it only has to be unique among reflections of the same session.

Multiple reflections per session are allowed and expected — walking sessions in particular may produce one recording per participant. Each one becomes its own session package downstream, with the same `session_id` but a distinct `recording_id`.

Accepted formats: `.m4a`, `.mp3`, `.wav` for audio; `.mp4`, `.mov`, `.webm` for video. Video files are accepted as a convenience — AssemblyAI transcribes the audio track directly and the visual channel is discarded. This pipeline is audio-only by design; face tracking and lip-sync attribution are not used. Anything outside these formats is rejected at validation and routed to the review folder with a note.

### Per-session human workflow

For every session of the conference, a runner does one thing: drop the recording into the right folder with the right name.

1. Recording happens (venue AV team for sessions, phone for walking reflections)
2. Runner saves the file to `/recordings/dayN/` as `{session_id}.{ext}` — or, for reflections, as `{session_id}__reflection__{slug}.{ext}`
3. Done

That is the entire human contribution. The rclone mount sees the file within seconds of it appearing in Drive; the file watcher fires; the pipeline runs.

### Trigger and processing

Prefect's deployment is bound to a filesystem watcher (Python `watchdog`) on the synced `/recordings/` directory. When a new file appears:

1. The watcher emits an event with the file path.
2. Prefect parses the filename to extract `session_id` and (if present) the reflection slug.
3. Prefect loads `sessions.json`, finds the matching session entry, and constructs the work package.
4. The work package fans out to Steps 2–5 in parallel with any other sessions currently processing.
5. The completed session package is written to `/transcripts/dayN/{session_id}.json` (or `{session_id}__reflection__{slug}.json`).
6. Any review items are written to `/review/dayN/{session_id}_review.json`.
7. The downstream n8n flow watches `/transcripts/` and picks up new packages for the Researcher.

If the same file is uploaded twice (e.g., a corrected version), the second upload triggers a re-run and overwrites the previous output. If a file lands with a `session_id` that does not appear in `sessions.json`, it is moved to `/review/` with a "no matching session" note — never silently dropped.

### Audio pre-processing

None. Modern ASR models perform measurably worse on enhanced audio than on raw input — speech enhancement introduces spectral artifacts that confuse models trained on noisy real-world data. Recordings are passed to ASR untouched. If audio is needed elsewhere for human listening (archival, playback), a separate enhancement pass runs outside this pipeline and never feeds the ASR path.

### Audio bitrate normalization

Normalization is not enhancement. The pipeline does not denoise, EQ, normalize loudness, or otherwise alter the spectral content of the audio — that's the constraint the "Audio pre-processing: None" rule above is protecting. But the bitrate at which the audio is *encoded* is a different question entirely: it controls how many bits are used to represent the same spectral content, not what the spectral content is.

A Prefect task between Ingest and the AssemblyAI call re-encodes incoming recordings to a standardized **96 kbps mono AAC** before upload:

```python
@task
def normalize_audio(input_path: Path, output_path: Path) -> Path:
    """Re-encode incoming audio to 96 kbps AAC mono for upload.

    96 kbps sits well above the threshold where ASR accuracy degrades on
    spoken-word content (degradation only begins below ~32 kbps for clean
    speech). Mono is correct because panel mic feeds are functionally
    single-channel and stereo at the same bitrate gives each channel half
    the bits.

    Saves bandwidth on slow venue Wi-Fi, standardizes input format
    regardless of what the A/V team provides, and shrinks files by 2-3x
    versus typical defaults — meaningful when uploading 6-9 sessions per
    night across 2 nights from a constrained connection.
    """
    subprocess.run([
        "ffmpeg", "-i", str(input_path),
        "-c:a", "aac",
        "-b:a", "96k",
        "-ac", "1",
        "-y", str(output_path)
    ], check=True)
    return output_path
```

**Why 96 kbps mono and not other values:**

- ASR WER is essentially flat from ~256 kbps down to ~64 kbps on Universal-3 Pro and other modern transformer-based ASR models. Degradation begins around 32 kbps, becomes obvious around 16 kbps, catastrophic below 8 kbps.
- 96 kbps gives clean fidelity with extra headroom for noisy real-world conditions (HVAC, walking-session wind, distant mics) that 64 kbps would not.
- Mono downmixing is appropriate because panel mic feeds are effectively single-channel: one speaker per mic, mono recordings preserve all the speech information.
- AssemblyAI's diarization works on voice features, not channel position — so collapsing stereo channels does not lose any information the pipeline uses.

**Falsifiability:** if Athens dry runs reveal transcription quality below the expected baseline, normalization is the first optimization to revert and re-test. It is additive and reversible.

**Storage and upload impact** for an Athens night with ~6 sessions averaging 75 minutes each:

| Setting | Per-session size | Per-night total | Upload time @ 5 Mbps |
|---|---|---|---|
| 256 kbps stereo (typical raw) | ~145 MB | ~870 MB | ~24 min |
| 128 kbps stereo | ~72 MB | ~432 MB | ~12 min |
| **96 kbps mono** | **~54 MB** | **~324 MB** | **~9 min** |
| 64 kbps mono | ~36 MB | ~216 MB | ~6 min |

The savings matter most when venue Wi-Fi is constrained or when a stage failure forces a re-upload.

### Step 1 Output

Per recording, a work package with two parts: a **metadata** block (carried forward intact through the whole pipeline and into the final session package) and **processing fields** (used internally and dropped after Step 4).

**Metadata (persistent — survives to the final session package):**

| Field | Description |
|---|---|
| **session_id** | From `sessions.json`, parsed from filename |
| **recording_id** | `{session_id}` for primary recordings; `{session_id}__reflection__{slug}` for reflections |
| **session_title** | From `sessions.json` |
| **session_description** | From `sessions.json` |
| **session_format** | keynote / panel / workshop / walking — from `sessions.json` |
| **track** | From `sessions.json` (e.g., "AI Democracy Marathon") |
| **date_time** | From `sessions.json` |
| **venue** | From `sessions.json` |
| **roster** | Full list of scheduled contributors: name, title, affiliation, bio — from `sessions.json` |

**Processing fields (internal — dropped after cleaning):**

| Field | Description |
|---|---|
| **recording_type** | `session` for primary recordings; `reflection` for participant reflection recordings. Parsed from filename. Orthogonal to `session_format`: a reflection on a panel and a reflection on a walking session are both `recording_type: reflection`. Flags which prompt context to apply. |
| **audio_path** | Local path to the normalized audio file (post-bitrate-normalization) |
| **expected_speaker_count** | From `sessions.json`; for reflections, defaults to 3 |
| **vocabulary** | Flat list of proper nouns built from roster + session description, passed to AssemblyAI as `keyterms_prompt` and to the Cleaning node as context |

---

## Step 2: Transcription & Diarization

**Input:** One session work package. Runs once per session in parallel across all sessions.

**Operation.** The normalized audio is sent to AssemblyAI Universal-3 Pro with diarization enabled. The model is given a natural-language context prompt describing the session format and speaker mix, and the vocabulary list is passed as `keyterms_prompt` to anchor proper nouns. The `speakers_expected` parameter is set slightly above the contributor count to prevent premature speaker merging.

**Why this model.** Universal-3 Pro is the only commercial system in April 2026 that combines high ASR accuracy, integrated diarization, support for up to 50 speakers per recording, and a promptable interface that accepts natural-language context. Speaker counts of 10–18 — typical for the Marathon panels — sit comfortably within its operating range, where pure end-to-end systems like NVIDIA Sortformer collapse.

**Quality expectations.** For conference room recordings with international English speakers, expect 5–10% WER and a diarization error rate of 12–20% at high speaker counts. For phone-quality reflection recordings, expect 15–25% WER and degraded diarization on outdoor noise. Both are workable for downstream processing — the cleaning and identification steps are designed to absorb these error rates.

### Known limit: audience merging during Q&A

Across all three MSC 2026 test sessions, Universal-3 Pro produced clean panelist diarization during the main discussion but merged multiple audience members into single speaker labels during the open Q&A section. This is not a pipeline bug — it's a known limit of speaker diarization when multiple brief interventions come from similar-sounding voices through similarly-positioned audience mics.

**Frequency observed in Level 2 testing:**

| Session | Panelist turns | Q&A audience merges |
|---|---|---|
| Vox Populi | Clean | 1 merge (Elena Lazar + Ava Federle → `speaker_f`) |
| Breaking Point | Clean | 1 merge (Prince Faisal + Mustafa Barghouti → `speaker_c`) |
| West-West Divide | Clean | **4 merges** — the most complex Q&A of the three, with 6 distinct audience interventions collapsing into 4 panelist labels |

**Mitigation — the prompt catches these:** Step 3's Speaker ID node uses explicit `missing_introduction` and `potential_split` flag types, and (as of v2) Pass 5 per-turn re-attribution. Every merge in testing was correctly flagged and — after §11 — correctly re-attributed at the per-turn level rather than silently corrupting the transcript. This is the right failure mode.

**Mitigation — recording protocol:** If the A/V team can route audience question mics to a **separate audio channel** from the panel mics, AssemblyAI can transcribe each channel independently and the audience/panel contamination disappears. This is a recording-protocol change, not a pipeline change. Worth raising with HoBB during pre-Athens logistics: the best way to avoid audience-panel speaker confusion is to not record them on the same track in the first place.

### Multilingual content and live interpretation

**Observed in Breaking Point:** Colombian Defence Minister Pedro Sánchez Suárez explicitly said *"I would like to switch to Spanish in order to have more fluency in my words"* and then delivered his substantive content. The raw AssemblyAI diarized output already showed that content in fluent English, despite the pipeline not running any translation step.

**Mechanism:** MSC provides live simultaneous interpretation, and the English interpreter's voice was captured on the same audio track as the speaker. AssemblyAI transcribed whichever voice was louder in each segment, which for non-English speakers meant the interpreter. The cleaning prompt is *not* translating — it's receiving English input from AssemblyAI.

**Implication for Athens:** If any WBBF session has non-English contributors and live interpretation, the transcription will reflect the interpreter's English, not the speaker's original language. The position is still correctly attributed to the speaker (Sánchez's arguments belong to Sánchez), but the verbatim phrasing belongs to an unnamed interpreter. This matters for any downstream step that depends on the exact words rather than the substance.

**Decision to take before Athens:** If a session metadata entry declares a language other than English for a speaker's native use, any verbatim quote attributed to that speaker should be marked `[interpreted]` in the cleaned text so downstream stages know the phrasing is not the speaker's own. Worth discussing with Till before Athens; the policy choice affects both the Transcription cleaning prompt and any downstream quote field.

### AssemblyAI SDK version drift — use raw field injection

The `assemblyai` Python SDK version 0.59.0 (current on PyPI as of Apr 2026) lags behind the AssemblyAI server API in several important ways:

1. The SDK's `TranscriptionConfig` constructor sends the deprecated singular field `speech_model` instead of the required plural `speech_models`.
2. The SDK exposes `word_boost` / `boost_param` parameters that universal-3-pro rejects — the replacement is `keyterms_prompt` (a list of specific terms) or `prompt` (natural-language context), but **not both in the same request**.
3. The SDK's `SpeechModel` enum exposes `best`, `nano`, `slam_1`, `universal` — but the server only accepts `universal-3-pro` and `universal-2` as valid values for the plural `speech_models` field.

**Resolution pattern:** Bypass the constructor fields and inject raw values directly on the underlying pydantic model. This keeps the pipeline working with the current SDK while still using current API features:

```python
config = aai.TranscriptionConfig(
    speaker_labels=True,
    speakers_expected=expected + 2,        # room for audience + buffer
    language_detection=True,               # required for multilingual panels
    # do NOT set speech_model, word_boost, boost_param here
)
config.raw.speech_models = ["universal-3-pro"]
config.raw.speech_model = None             # clear the deprecated singular
if vocabulary_terms:
    config.raw.keyterms_prompt = vocabulary_terms
# NB: do not set config.raw.prompt if keyterms_prompt is set —
# the server rejects requests that include both
```

`language_detection=True` is non-optional. Without it, AssemblyAI defaults to English-only processing and can produce garbled output when a speaker briefly switches languages. With it enabled, the model gracefully handles mid-session language switches (including the interpreter-capture behavior documented above).

**Monitoring recommendation:** On SDK upgrade, retest the transcription pipeline end-to-end before Athens. If AssemblyAI releases a newer SDK that supports the current fields natively, the `config.raw.*` workarounds can be removed.

### Step 2 Output

A diarized transcript per session: a JSON array of turns, each with anonymous speaker label (`speaker_a`, `speaker_b`, ...), start and end timestamps, and the recognized text. Speaker labels are local to the session — `speaker_a` in Session 1 has no relationship to `speaker_a` in Session 2.

---

## Step 3: Speaker Identification

**Input:** The diarized transcript from Step 2 plus the session work package (roster, bios, session metadata). Runs once per session.

**Operation.** A single Claude Sonnet 4.6 call performs multi-pass attribution: explicit name cues first (self-introductions, moderator introductions, direct address), then role detection (moderator vs. panelist vs. audience), then expertise matching (utterance content against bios), then confidence-gated output, **then a per-turn sanity check that re-attributes individual contaminated turns to audience members** (Pass 5, new in v2). The model is explicitly instructed never to guess: speakers below the confidence threshold are returned as `Unidentified Speaker N`, not force-matched to a roster name.

**Why this approach.** Voice enrollment is not available — there are no advance voice samples for the contributors. Published research on text-based speaker identification (Adobe Research 2024, DiarizationLM, "From Who Said What to Who They Are" 2025) consistently shows that LLM attribution from content cues works well when speakers introduce themselves or are introduced, and degrades sharply when those cues are absent. The multi-pass structure exploits the strong cues first and falls back to weaker ones only as needed, with confidence flags exposing the difference.

**Per-turn re-attribution (added in v2 after Level 2 testing).** The original four-pass prompt identified the dominant speaker for each anonymous label and flagged merges for human review, but did not correct individual contaminated turns. On West-West Divide, this produced a concrete failure: audience member Melanie Ward ("I'm a British MP...") appeared under Hillary Clinton's speaker_f label because AssemblyAI merged her into Clinton's diarization cluster during Q&A. The flag correctly identified the merge, but a downstream Researcher reading `transcript.turns[]` would extract the position as Clinton's unless it also read `review_queue.diarization_flags`. Pass 5 closes this gap upstream: the model re-reads each turn, checks whether the content is internally consistent with the dominant speaker's identity, and re-attributes contaminated turns to `Audience Member N` on the spot while leaving the speaker's other turns intact. The re-attribution is recorded in `review_queue.diarization_flags` as `type: "reassigned_turns"` with the specific turn indices, so a human editor can audit the corrections.

**Cross-session linking (optional).** After all sessions in a night have been processed independently, a second pass can link confident identifications across sessions: if Speaker B in the morning panel was confidently identified as Jon Alexander and a speaker in the afternoon panel discusses overlapping content with similar turn patterns, the LLM can propose a tentative link. This is additive — it never overwrites a high-confidence within-session attribution.

**Expected accuracy.** For well-moderated panels with introductions: 70–85% high-confidence identifications, 10–15% medium-confidence. For walking session reflections where participants self-introduce: 90%+. For panels without introductions or reflections without self-naming: as low as 40–50%, with the rest correctly flagged as low-confidence rather than wrongly attributed. Level 2 test results on three MSC 2026 panels: 100% high-confidence panelist attribution with quote-level evidence.

### Alternatives considered — AssemblyAI native `SpeakerIdentificationRequest`

A market survey conducted Apr 14 2026 identified AssemblyAI's Speech Understanding API with `SpeakerIdentificationRequest` and `known_values` as the closest commercial equivalent to this custom Claude-based stage. The survey suggested it could potentially replace ~150 lines of custom orchestration with a single config field.

**Investigation outcome:** The feature exists in the SDK 0.59.0 type definitions (`aai.SpeakerIdentificationRequest`, `aai.SpeakerType.name`, `aai.types.SpeechUnderstandingFeatureRequests`), and `TranscriptionConfig` exposes a `speech_understanding` field. However, submitting a transcription request with `speech_understanding.speaker_identification` populated returns a server-side error: `"Invalid endpoint schema, please refer to documentation for examples."` This indicates Speech Understanding is a **separate API endpoint** that runs on top of a completed transcript, not a parameter on the standard `/transcript` submission. SDK 0.59.0 exposes the request/response types but does not expose a client method to call this second endpoint. Using it would require either raw HTTP plumbing or waiting for a newer SDK.

**Architectural incompatibility even if it worked.** Even if the plumbing were accessible, AssemblyAI's native speaker_identification provides label-to-name mapping only. It does NOT produce evidence fields ("self-identifies at 03:42 as 'Minister of Defense'"), confidence reasoning (the multi-pass workflow), bio-based expertise matching (Pass 3), or diarization contamination detection (Pass 5). The downstream Researcher depends on evidence and confidence flowing through, not just names. Replacing the Claude-based stage with AssemblyAI's native feature would produce a simpler pipeline that feeds the Researcher less useful data.

**Decision:** Keep the custom Sonnet 4.6 Speaker ID stage. Revisit only if (1) AssemblyAI publishes an SDK version that exposes the Speech Understanding endpoint directly, AND (2) that endpoint returns evidence/confidence metadata, not just label-to-name mapping, AND (3) the cost per call is meaningfully lower than the current ~$0.05 per Speaker ID call via Claude. All three must hold. None hold today.

### Model selection — default Sonnet, optional Opus for difficult sessions

The Speaker ID LLM call defaults to Claude Sonnet 4.6. Across the three MSC 2026 Level 2 test sessions, Sonnet 4.6 produced 100% high-confidence attributions with 5-pass re-attribution catching real edge cases (Mustafa Barghouti self-introduction in Breaking Point, 15 audience-member reassignments across 8 flags in West-West Divide). The baseline is sufficient for well-behaved conference audio.

For difficult sessions, operators can override the Speaker ID model per-run via the `TRANSCRIPTION_SPEAKER_ID_MODEL` environment variable:

```bash
TRANSCRIPTION_SPEAKER_ID_MODEL=claude-opus-4-7 python flows/transcription_flow.py ...
```

When to flip this toggle:

- **Non-native English speakers with heavy accents** — where the ASR's vocabulary and the transcription text diverge in ways that make name-to-role correlation harder
- **Complex multi-person Q&A** — when the open question period has 5+ distinct audience members on similarly-positioned microphones (the Q&A audience-merging problem documented in §6), and Pass 5 needs to make confident distinctions across many short turns
- **Incomplete roster metadata** — when the program lists contributors but the bios are thin or the title/affiliation fields are missing, giving Pass 1 less signal to match against
- **Mixed-language sessions** — where speakers switch between English and another language and the Speaker ID pass needs to reason across the language boundary

Opus 4.7's extra reasoning capacity helps on these edge cases. It does NOT help on well-behaved sessions and costs ~5× more per call, so it should not be the default.

**Thinking mode is NOT used in Transcription** even when Opus is selected. The Speaker ID output is small (mappings + flags, under 2K tokens), so the latency cost of adaptive thinking is large relative to its benefit. The Speaker ID call stays non-streaming with `max_tokens=4096` regardless of model choice.

**Cleaning and semantic drift verification remain on the default model (Sonnet).** Cleaning is the largest LLM call in the whole overnight pipeline by output volume and its judgment work is mostly local per turn, not cross-turn synthesis, so thinking adds little. Drift verification is a short quality-gate check, not a reasoning task. Neither benefits from the Opus upgrade and both incur significant cost increase if flipped.

### Step 3 Output

A mapping table merged into the transcript: each turn now carries a named speaker (or `Unidentified Speaker N` or `Audience Member N`), a confidence level (high / medium / low), an evidence note for the attribution, and a role tag (moderator / panelist / audience). A `diarization_flags` list records any merges, splits, missing introductions, or per-turn re-attributions for downstream auditing.

---

## Step 4: Cleaning

**Input:** The named transcript from Step 3 plus the vocabulary list. Runs once per session.

**Operation.** A single Claude Sonnet 4.6 call performs constrained cleaning: fix ASR errors using the vocabulary list (especially proper nouns), remove disfluencies and false starts, repair sentence fragments. The model is given hard rules against paraphrasing, summarizing, adding content, or altering speaker labels and turn boundaries. Uncertain corrections are marked `[verify]` rather than silently applied.

**Why these constraints.** The downstream Researcher extracts atomic positions and atomic positions are exactly what gets flattened when an LLM is allowed to "format" a transcript. Standard cleaning produces smoother prose and worse fidelity. The constraints exist to make cleaning narrowly mechanical: it fixes what is provably wrong (misspelled names, dropped phonemes, broken sentences) and leaves everything else exactly as recognized, including the characteristic phrasings of non-native English speakers, which are themselves signal.

**Single-pass over chunked.** Sonnet 4.6's 200K context window accommodates a full 120-minute transcript in one pass, which eliminates the chunk boundary errors (dropped turns, duplicated segments) that plague chunked cleaning. For exceptionally long sessions, cleaning is split at natural turn boundaries with explicit overlap.

**Streaming is mandatory.** On the West-West Divide Level 2 test session (142 turns from a 69-minute panel), the cleaning pass generated 18,712 output tokens. With a `max_tokens=16000` cap, this truncated silently — the cleaning call hit the budget exactly, returned a JSON object with an unterminated string, and the downstream parse failed with `JSONDecodeError`. Raising `max_tokens` above ~21,333 triggers the Anthropic SDK's non-streaming timeout heuristic (formula: `expected_time = 3600 * max_tokens / 128_000`; if `expected_time > 600` seconds the SDK refuses to send the request). Resolution: the cleaning task **must** use `client.messages.stream()` as a context manager regardless of expected output size. Non-streaming is unsafe for any transcript that could plausibly need more than ~20K output tokens, which rules out almost any full-length conference panel.

```python
chunks = []
with client.messages.stream(
    model=CLAUDE_MODEL,              # "claude-sonnet-4-6"
    max_tokens=64_000,                # Step 4 budget — large, streaming required
    system=CLEANING_SYSTEM,
    messages=[{"role": "user", "content": user}],
) as stream:
    for text in stream.text_stream:
        chunks.append(text)
    final = stream.get_final_message()
full_text = "".join(chunks)
cleaned_turns = extract_json(full_text)

if final.usage.output_tokens > 64_000 * 0.8:
    logger.warning(
        f"Cleaning used {final.usage.output_tokens}/64000 output tokens "
        f"(>80%). Consider increasing the budget."
    )
```

Streaming has no wall-clock ceiling from the SDK side — the SSE connection survives as long as chunks keep arriving — so `max_tokens` can safely be 64,000 in streaming mode regardless of how long the generation takes.

Observed usage across the three Level 2 test sessions: Vox Populi 10,827 tokens (17% of 64K), Breaking Point ~13,000 (20%), West-West Divide 18,712 (29%). The 64K budget has ample headroom for even longer panels; the >80% warning is cheap insurance against future regressions.

**Budget decoupling from Speaker ID.** Step 3's Speaker ID call is capped independently at `max_tokens=4096` (non-streaming, small structured output). Raising the Cleaning budget for larger transcripts should not change Speaker ID behavior, and a tight Speaker ID cap fails fast if the prompt misfires.

### Step 4 Output

A cleaned transcript in the same shape as the Step 3 output: array of turns with named speaker, confidence, role, and now-clean text. Any unresolved corrections carry `[verify]` markers.

---

## Step 5: Validation & Output

**Input:** The cleaned transcript from Step 4 plus the original work package.

**Operation.** A short verification pass checks: speaker count is within the expected range; no high-confidence attribution conflicts (one name mapped to two anonymous labels, or vice versa); no semantic drift between raw and cleaned text on a sampled basis; all `[verify]` markers and low-confidence attributions are collected into a human review queue.

**Human review handoff.** Sessions where review is needed are flagged but not blocked — the session package proceeds to the Researcher with whatever confidence it has. The review queue is a parallel artifact for a human to scan in the morning. Expected review time: 15–30 minutes per night across all sessions.

### Step 5 Output

The **session package** the Researcher consumes. It has three parts: the metadata block carried forward intact from Step 1, the transcript itself, and a review queue.

```
session_package:
  metadata:
    session_id
    session_title
    session_description
    session_format
    track
    date_time
    venue
    roster: [{name, title, affiliation, bio}, ...]   # who was scheduled
  transcript:
    speakers_present: [list of names who actually spoke]   # subset of roster + any audience members
    turns: [
      {
        turn_index,      # integer, 0-based — used as target for review_queue back-references
        speaker,         # named individual, "Audience Member N", or "Unidentified Speaker N"
        role,            # moderator / panelist / audience
        confidence,      # high / medium / low — MUST flow through to Researcher
        text
      },
      ...
    ]
  review_queue:
    low_confidence_attributions: [...]
    verify_markers: [{index, text}, ...]                 # back-references into transcript.turns[]
    diarization_flags: [
      {
        type: "potential_merge" | "potential_split" | "missing_introduction" | "reassigned_turns",
        # for reassigned_turns (from Step 3 Pass 5):
        original_label,
        original_attribution,
        reassigned_turn_indices: [int, ...],
        reassigned_to,
        reason
      },
      ...
    ]
```

**Three things worth noting about the schema:**

- **`roster` vs `speakers_present`** are different and both matter. `roster` is who the program said would be there. `speakers_present` is who actually spoke in the recording — typically a subset of the roster, plus any audience members (labeled `Audience Member 1`, `Audience Member 2`, etc.) who took a turn. Downstream stages can compare the two to see who was scheduled but absent or who joined the conversation unexpectedly.

- **Per-turn `confidence` is a contract with the Researcher.** The Researcher's Node 1 extraction prompt reads `confidence` on each turn and appends `[medium]` or `[low]` to the speaker label when confidence is not high. This contract was validated on the three Level 2 test sessions (all returned 100% `high`, so degraded behavior is untested in production but the plumbing is verified). The `confidence` field MUST be preserved in `session_package.json` and MUST NOT be dropped in any cleanup step.

- **`review_queue` is not orphaned — but only `verify_markers` is actively consumed.** Before v2 of this document, the review_queue was written by the Transcription Pipeline but not read by anything downstream (the Researcher's prompt read `metadata` and `transcript.turns[]` only), which meant flagged items silently vanished into the 3am gap. The v2 resolution is two-part:
  - **Upstream (Part A, in Step 3 Pass 5):** `diarization_flags` are now a log of what was *corrected* by Speaker ID re-attribution, not a to-do list for a nonexistent human editor. The pipeline fixes what it can fix rather than flagging for later.
  - **Downstream (Part B, in `AI_Assembly_Researcher_Pipeline.md`):** The Researcher's Node 1 prompt reads `review_queue.verify_markers` and degrades extraction confidence on any extraction whose substance hinges on a `[verify]`-tagged word. See that document for the prompt addition.
  - **`low_confidence_attributions`** is retained as a diagnostic field for pipeline monitoring (count per session tracks Speaker ID quality over time) but is not read by any downstream LLM call.
  - **Alternative considered and rejected:** A human-in-the-loop pause between Cleaning and Researcher (Slack notification, wait for ack, timeout) would let a morning editor fix flags before downstream runs. This is closest to the original design intent but requires staffing the breakfast deadline with someone awake at 3–5am, which isn't realistic for Athens. Keep the pipeline fully automated.

- **The `vocabulary` list is dropped** at this stage. It is a cleaning artifact, not downstream signal. If a later stage needs proper-noun normalization, it can rebuild the list from the roster.

This is the complete deliverable. It feeds the Researcher Pipeline.

---

# Constraints

**Time window.** The Transcription Pipeline runs first in the overnight chain. For ~9 hours of audio across 6–8 sessions, the full pipeline must complete in well under an hour to leave runway for Researcher, Provocateur, voice generation, and artifact production before breakfast. With parallel session processing, the realistic target is 10–15 minutes wall clock.

**Faithful, not interpretive.** The pipeline never extracts, summarizes, or paraphrases. Its job is to capture what was said, not what it meant. Interpretation begins at the Researcher.

**Confidence over coverage.** Wrong attributions are worse than missing ones. A speaker labeled `Unidentified Speaker 3` is information the Researcher and Provocateur can handle. A speaker confidently misattributed to Hannah Arendt's biographer when it was actually the Patagonia executive corrupts every downstream extraction tied to that turn.

**No voice enrollment.** Voice samples of contributors are not collected in advance. Speaker identification relies entirely on content cues from the transcript and the contributor bios. This is a hard constraint, not a temporary state.

**Reflections are first-class.** Walking session reflections are sometimes the only input for a session. The pipeline treats them as session recordings, not as a secondary stream — same schema, same processing, same downstream consumption.

---

# Scope

The Transcription Pipeline does not select which sessions to process. It does not enhance or denoise audio for ASR. It does not extract positions, identify themes, or formulate questions. It does not know the council, the audience, or the governance matrices.

Its sole function is to turn recorded human conversation into a clean, named, machine-readable transcript.

---

# Implementation Draft

The pipeline is orchestrated by **Prefect** (Python-native, parallel by default, robust async handling) rather than n8n — the audio stage's needs (large files, long-running async API polls, parallel fan-out) sit outside what n8n handles well. Prefect writes completed session packages to a watched location; the existing n8n flow picks them up from there for Researcher and downstream stages.

**Development caching.** During prompt iteration, re-running the full flow to test a small change in the cleaning prompt is expensive: each run pays AssemblyAI ~$1.50 for the same transcript it already produced. The Prefect transcription task uses native task caching via `cache_key_fn` to skip the AssemblyAI call if the audio file hasn't changed:

```python
@task(cache_key_fn=task_input_hash, cache_expiration=timedelta(days=30))
def transcribe_with_assemblyai(audio_path: Path, session: dict) -> list[dict]:
    ...
```

For production Athens runs, caching should be **disabled** (every session is fresh). For development and for prompt iteration this saves real money — tonight's Level 2 testing burned ~$4.50 in AssemblyAI costs re-running West-West Divide three times while iterating on SDK compatibility; with caching it would have been ~$1.50.

Four LLM-facing nodes need prompts. All Claude nodes use **Claude Sonnet 4.6** via API (`claude-sonnet-4-6`).

---

### Node 1: ASR Context Prompt (AssemblyAI Universal-3 Pro)

Universal-3 Pro accepts a natural-language context prompt to bias recognition. One per session, generated from program metadata.

**Template:**

This is a recording from the World Beautiful Business Forum in Athens, May 2026 — a conference on business philosophy, democratic innovation, and the future of work. The session is titled "{{session_title}}" and is a {{session_format}} format with {{expected_speaker_count}} contributors. Speakers include international participants with Greek, European, American, Indian, and other accents; most speak English as a second or third language. Expect formal panel discussion with occasional audience questions. Key terms and proper nouns include: {{vocabulary_list}}.

**API parameters (SDK 0.59.0 pattern — inject via `config.raw.*`):**

```python
config = aai.TranscriptionConfig(
    speaker_labels=True,
    speakers_expected=expected_speaker_count + 2,   # slight buffer to prevent premature merging
    language_detection=True,                         # required — multilingual / interpreter handling
)
config.raw.speech_models = ["universal-3-pro"]
config.raw.speech_model = None                       # clear deprecated singular
config.raw.keyterms_prompt = vocabulary_terms        # replaces deprecated word_boost/custom_spelling
# NB: do not set config.raw.prompt alongside keyterms_prompt — server rejects the combination
```

See Step 2 "AssemblyAI SDK version drift" for the rationale.

---

### Node 2: Speaker Identification (Claude Sonnet 4.6 — once per session)

**Runtime config:** `model` defaults to `CLAUDE_MODEL` env var (baseline: `claude-sonnet-4-6`), overridable via `TRANSCRIPTION_SPEAKER_ID_MODEL` env var for per-run model selection; `max_tokens=4096`; non-streaming. See "Model selection" subsection above for when to override the default.

**System prompt:**

You are identifying speakers in a conference panel transcript. You will receive a diarized transcript with anonymous speaker labels and a roster of known contributors with bios. Your job is to map anonymous labels to real names — but only when the evidence is clear.

This is a faithful attribution task, not a guessing task. Wrong attributions are worse than missing ones. When evidence is weak, leave the speaker as Unidentified.

PERFORM FIVE PASSES IN ORDER:

PASS 1 — Explicit name cues. Scan for self-introductions ("I'm Sarah Martinez from..."), moderator introductions ("Let's hear from Professor Asante"), and direct address ("Jon, what do you think?"). These are the strongest signals. A name mentioned by the previous, current, or next speaker reliably identifies the person being referred to.

PASS 2 — Role detection. Identify the moderator: typically speaks first with welcoming language, introduces the topic and panelists, speaks between panelist turns, and asks questions rather than making sustained arguments. Distinguish panelists (sustained turns, substantive positions) from audience members (brief turns, questions from the floor).

PASS 3 — Expertise matching. For speakers not yet identified, match the content of their utterances to the bios on the roster. A speaker discussing citizens' assemblies and deliberative democracy maps to the contributor whose bio mentions DemocracyNext. A speaker citing Hannah Arendt's distinction between making and acting maps to the Hannah Arendt Center director. Be specific about the evidence — do not match on surface topic alone.

PASS 4 — Confidence assignment. For each anonymous label, assign:
- HIGH (0.9+): explicit naming AND content consistent with the bio
- MEDIUM (0.6–0.9): expertise match with multiple consistent signals but no explicit naming
- LOW (0.3–0.6): weak positional or topic cues only
- UNIDENTIFIED (<0.3): leave as "Unidentified Speaker N"

PASS 5 — Per-turn sanity check. After assigning dominant speakers to each anonymous label, re-read each turn and check whether its content is consistent with being spoken by the identified speaker. Red flags: the turn is a self-introduction as a different name ("I'm [Name] from [Org]"); the turn is a question directed at the very speaker the label is assigned to ("I have a question for Secretary Clinton..."); the turn claims a role the identified speaker does not hold ("I'm a British MP" in a turn attributed to a non-British non-MP). When a turn is inconsistent, the diarization has merged audience voices into a panelist's label — re-assign that specific turn to "Audience Member N" while leaving the panelist's other turns unchanged. Record the re-assignment in `flags` with the anonymous_label, the specific turn indices, and the reason.

RULES:

- Each name on the roster maps to at most one anonymous label, and each anonymous label maps to at most one name.
- Audience members are not on the roster. Label them "Audience Member 1", "Audience Member 2", etc.
- If diarization appears to have split one speaker into two labels (two labels expressing identical expertise that never appear in the same time window), flag a potential merge but do not merge silently.
- If diarization appears to have merged two speakers into one label (one label with inconsistent expertise or contradicting positions), Pass 5 should re-attribute contaminated turns. If Pass 5 cannot cleanly separate them (e.g., both voices span the entire label with no clear per-turn distinction), flag a `potential_split` but do not split silently.
- Never alter the transcript text. Your output is the speaker mapping plus per-turn re-attributions only.

Return as JSON:

```
{
  "mappings": [
    {
      "anonymous_label": "speaker_a",
      "identified_name": "Jon Alexander" | "Unidentified Speaker 1" | "Audience Member 1",
      "confidence": "high" | "medium" | "low",
      "role": "moderator" | "panelist" | "audience",
      "evidence": "Specific quote or cue supporting this attribution"
    }
  ],
  "flags": [
    {
      "type": "potential_merge" | "potential_split" | "missing_introduction",
      "labels": ["speaker_c", "speaker_e"],
      "note": "Description of the issue"
    },
    {
      "type": "reassigned_turns",
      "original_label": "speaker_f",
      "original_attribution": "Hillary R. Clinton",
      "reassigned_turn_indices": [105, 107, 110],
      "reassigned_to": "Audience Member 5",
      "reason": "Turn content is a self-introduction as 'British MP Melanie Ward', inconsistent with Clinton's identity"
    }
  ]
}
```

**User prompt:**

Session: {{session_title}}
Format: {{session_format}}
Description: {{session_description}}

Roster:
{{for each contributor: name, title, affiliation, bio}}

Diarized transcript:
{{json array of turns with anonymous labels, turn_index, and text}}

---

### Node 3: Cleaning (Claude Sonnet 4.6 — once per session)

**Runtime config:** `model="claude-sonnet-4-6"`, `max_tokens=64000`, **streaming required** (`client.messages.stream()` context manager). See Step 4 "Streaming is mandatory" for the rationale.

**System prompt:**

You are cleaning an ASR transcript of a conference panel for downstream analysis. The transcript has been diarized and speaker-attributed. Your job is to fix what is provably wrong and leave everything else untouched.

This is a faithful cleaning task, not an editing task. The downstream pipeline extracts atomic positions from this transcript. Anything you smooth, paraphrase, or "improve" destroys the signal you are meant to preserve.

DO:

- Fix ASR errors using the vocabulary list, especially proper nouns (speaker names, organizations, technical terms).
- Remove filler words (um, uh, you know, like) when they are clearly disfluencies, not substantive.
- Remove false starts and self-corrections ("I think — I mean — what I'm saying is").
- Repair sentence fragments by joining clauses where the original meaning is unambiguous.
- Mark uncertain corrections with [verify] inline so a human reviewer can check them.

DO NOT:

- Paraphrase, summarize, or rewrite for clarity.
- "Correct" non-native English phrasings or unusual constructions — these are signal, not error.
- Add information not present in the original, including transitional phrases or context.
- Alter speaker labels, turn boundaries, or the order of turns.
- Smooth out characteristic speaker voice (hesitation, repetition for emphasis, idiosyncratic word choice).
- Translate or normalize across languages.

When in doubt, leave it alone. The Researcher will handle ambiguity downstream.

Return as JSON: an array of turns matching the input structure exactly, with cleaned text in place of raw text, and preserving `turn_index`, `speaker`, `role`, `confidence` unchanged.

```
[
  {
    "turn_index": 0,
    "speaker": "Jon Alexander",
    "role": "panelist",
    "confidence": "high",
    "text": "cleaned text here"
  },
  ...
]
```

**User prompt:**

Vocabulary (correct spellings of proper nouns):
{{vocabulary_list}}

Session context: {{session_title}} — {{session_description}}

Named transcript:
{{json array of turns with named speakers and raw text}}

---

### Node 4: Validation Diff (Claude Sonnet 4.6 — optional, once per session)

A cheap insurance pass that compares raw vs. cleaned transcript and flags any segments where meaning may have shifted.

**Runtime config:** `model="claude-sonnet-4-6"`, `max_tokens=4096`, non-streaming.

**System prompt:**

You are checking whether a cleaning pass introduced semantic drift in a transcript. You will receive matched pairs of raw and cleaned segments. For each pair, determine whether the cleaning preserved the original meaning or whether something was lost, added, or changed.

Most segments will be fine — only flag segments where:
- The cleaned version says something the raw version did not, or vice versa
- A position, claim, or named entity was altered
- A negation was dropped or added
- A speaker's characteristic phrasing was normalized in a way that flattens substance

Return as JSON: an array of flagged segment indices with a short note explaining what shifted. If nothing shifted, return an empty array.

```
{
  "flagged_segments": [
    {
      "index": 47,
      "raw": "the original text",
      "cleaned": "the cleaned text",
      "issue": "Description of what shifted"
    }
  ]
}
```

**User prompt:**

{{json array of {index, raw, cleaned} pairs}}

---

*These draft instructions were validated against three MSC 2026 panels (Vox Populi, Breaking Point, West-West Divide) in Level 2 testing on Apr 13–14 2026. All three produced 100% high-confidence speaker ID with quote-level evidence; cleaning preserved non-native English idioms, jokes, and characteristic filler patterns; diarization contamination was detected and (after §11) re-attributed at the per-turn level. Refine further during pre-Athens dry runs against real HoBB recordings.*
