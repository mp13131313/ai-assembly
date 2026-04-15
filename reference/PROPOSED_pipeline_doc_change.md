# Proposed addition to AI_Assembly_Transcription_Pipeline.md

**Insertion point:** After "Step 1: Ingest" → "Audio pre-processing" subsection (around line 132).
The current subsection says "None" and explains why audio enhancement hurts ASR.
This addition introduces bitrate normalization as a *separate concern* from enhancement,
and explains the distinction.

---

### Audio bitrate normalization

Normalization is not enhancement. The pipeline does not denoise, EQ, normalize loudness,
or otherwise alter the spectral content of the audio — that's the constraint the
"Audio pre-processing: None" rule is protecting. But the bitrate at which the audio is
*encoded* is a different question entirely: it controls how many bits are used to
represent the same spectral content, not what the spectral content is.

A Prefect task between Stage 0 (Ingest) and Stage 1 (ASR) re-encodes incoming recordings
to a standardized **96 kbps mono AAC** before upload to AssemblyAI:

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

- ASR WER is essentially flat from ~256 kbps down to ~64 kbps on Universal-3 Pro
  and other modern transformer-based ASR models. Degradation begins around 32 kbps,
  becomes obvious around 16 kbps, catastrophic below 8 kbps.
- 96 kbps gives clean fidelity with extra headroom for noisy real-world conditions
  (HVAC, walking-session wind, distant mics) that 64 kbps would not.
- Mono downmixing is appropriate because panel mic feeds are effectively single-channel:
  one speaker per mic, mono recordings preserve all the speech information.
- AssemblyAI's diarization works on voice features, not channel position — so
  collapsing stereo channels does not lose any information the pipeline uses.

**Falsifiability:** if Athens dry runs reveal transcription quality below the
expected baseline, normalization is the first optimization to revert and re-test.
It is additive and reversible.

**Storage and upload impact** for an Athens night with ~6 sessions averaging 75
minutes each:

| Setting | Per-session size | Per-night total | Upload time @ 5 Mbps |
|---|---|---|---|
| 256 kbps stereo (typical raw) | ~145 MB | ~870 MB | ~24 min |
| 128 kbps stereo | ~72 MB | ~432 MB | ~12 min |
| **96 kbps mono** | **~54 MB** | **~324 MB** | **~9 min** |
| 64 kbps mono | ~36 MB | ~216 MB | ~6 min |

The savings matter most when venue Wi-Fi is constrained or when a stage failure
forces a re-upload.

---

**Where this slots in the existing Stage 0–4 numbering:** Stage 0.5, between Ingest
and ASR. The full overnight chain becomes:

0. Ingest from upload location
0.5. **Normalize audio bitrate** (this addition)
1. AssemblyAI Universal-3 Pro: ASR + diarization
2. Claude Sonnet: speaker identification
3. Claude Sonnet: transcript cleaning
4. Validation + human review queue


---

# Additional changes from Level 2 test runs (Apr 13 2026)

The following patches emerged from running three MSC 2026 sessions (Vox Populi, 
Breaking Point, West-West Divide) end-to-end through the pipeline on a laptop. 
They are architectural corrections, not prompt changes. Validation: all three 
sessions produced 100% high-confidence speaker ID with quote-level evidence; 
cleaning preserved non-native English idioms, jokes, and characteristic filler 
patterns; diarization issues were correctly flagged rather than silently 
corrupted.

---

## 2. Streaming is mandatory for the cleaning task

**Insertion point:** Step 3 "Clean transcript" node, implementation section.

**Problem discovered:** On the West-West Divide session (142 turns from a 69-minute 
panel), the cleaning pass generated 18,712 output tokens. With a `max_tokens=16000` 
cap, this truncated silently — the cleaning call hit the budget exactly, returned 
a JSON object with an unterminated string, and the downstream parse failed with 
`JSONDecodeError`. Raising `max_tokens` above ~21,333 triggers the Anthropic SDK's 
non-streaming timeout heuristic and the SDK refuses to send the request at all: 
`"Streaming is required for operations that may take longer than 10 minutes."`

**The SDK's formula** (from `anthropic._base_client._calculate_nonstreaming_timeout`):

```python
expected_time = 3600 * max_tokens / 128_000
if expected_time > 600:  # 10 minutes
    raise ValueError("Streaming required...")
```

Solving: `max_tokens > 600 * 128_000 / 3600 ≈ 21,333` → streaming required.

**Resolution:** The cleaning task must use `client.messages.stream()` as a context 
manager regardless of expected output size. Non-streaming is unsafe for any 
transcript that could plausibly need more than ~20K output tokens, which rules 
out almost any full-length conference panel.

```python
chunks = []
with client.messages.stream(
    model=CLAUDE_MODEL,
    max_tokens=CLAUDE_MAX_TOKENS,
    system=CLEANING_SYSTEM,
    messages=[{"role": "user", "content": user}],
) as stream:
    for text in stream.text_stream:
        chunks.append(text)
    final = stream.get_final_message()
full_text = "".join(chunks)
cleaned_turns = extract_json(full_text)
```

`max_tokens` can safely be 64,000 in streaming mode (Sonnet 4.6's default cap). 
Streaming has no wall-clock ceiling from the SDK side — the SSE connection 
survives as long as chunks keep arriving.

---

## 3. Per-call max_tokens budgets, not a shared global

**Insertion point:** Step 2 "Speaker identification" and Step 3 "Clean transcript" 
implementation sections.

The Speaker ID call produces a small structured mapping (typically 1,500–2,000 
output tokens). It should be capped at **4,096 tokens**, not the global 
CLAUDE_MAX_TOKENS used for cleaning. Three reasons:

1. **It stays non-streaming**, which is simpler and sufficient for small outputs 
   (under the 21K SDK threshold).
2. **It protects against runaway generation** — if the prompt misfires and the 
   model tries to generate an excessive response, a tight cap fails fast rather 
   than burning tokens and wall clock.
3. **It decouples Speaker ID from cleaning budget changes** — raising the 
   cleaning budget for larger transcripts should not change Speaker ID behavior.

```python
# Speaker ID: tight cap, non-streaming is fine
resp = client.messages.create(
    model=CLAUDE_MODEL,
    max_tokens=4096,
    system=SPEAKER_ID_SYSTEM,
    messages=[{"role": "user", "content": user}],
)

# Cleaning: large cap, streaming required
with client.messages.stream(
    model=CLAUDE_MODEL,
    max_tokens=64_000,
    system=CLEANING_SYSTEM,
    messages=[{"role": "user", "content": user}],
) as stream:
    ...
```

---

## 4. Log a warning when cleaning approaches its token budget

**Insertion point:** Step 3 "Clean transcript" implementation, after the stream 
completes.

Silent near-truncation is a real failure mode. The cleaning task should warn 
when the actual output uses more than 80% of the max_tokens budget — this is 
the early-warning signal that the budget needs raising before it catastrophically 
truncates on a larger session.

```python
if final.usage.output_tokens > CLAUDE_MAX_TOKENS * 0.8:
    logger.warning(
        f"Cleaning used {final.usage.output_tokens}/{CLAUDE_MAX_TOKENS} "
        f"output tokens (>80%). Consider increasing CLAUDE_MAX_TOKENS."
    )
```

Observed usage across the three test sessions: Vox Populi 10,827 tokens 
(17% of 64K), Breaking Point ~13,000 tokens (20%), West-West Divide 18,712 
tokens (29%). The 64K budget has ample headroom for even longer panels, but 
the warning is cheap insurance against future regressions.

---

## 5. Cache AssemblyAI output to enable downstream iteration without re-cost

**Insertion point:** Pipeline overview diagram, caching notes.

During development and prompt iteration, re-running the full flow to test a 
small change in the cleaning prompt is expensive: each run pays AssemblyAI 
~$1.50 for the same transcript it already produced. A smart pipeline should 
check for a cached `out_01_diarized.json` file and skip the transcription 
task if it exists.

```python
@task(cache_key_fn=task_input_hash, cache_expiration=timedelta(days=30))
def transcribe_with_assemblyai(audio_path: Path, session: dict) -> list[dict]:
    ...
```

Prefect's built-in task caching via `cache_key_fn` handles this natively. For 
production Athens runs, caching should be **disabled** (every session is fresh) 
but for development and for prompt iteration this saves real money.

**Cost accounting from tonight's testing:** burning through ~$4.50 in AssemblyAI 
costs alone by re-running West-West Divide three times while iterating on SDK/API 
compatibility. Would have been ~$1.50 with caching.

---

## 6. AssemblyAI diarization degrades during open Q&A

**Insertion point:** Step 1 "ASR + diarization" implementation notes, new 
"Known limits" subsection.

**Observed behavior:** Across all three test sessions, AssemblyAI Universal-3 Pro 
produced clean panelist diarization during the main discussion but merged 
multiple audience members into single speaker labels during the open Q&A section. 
This is not a pipeline bug — it's a known limit of speaker diarization when 
multiple brief interventions come from similar-sounding voices through 
similarly-positioned audience mics.

**Frequency of occurrence in testing:**

| Session | Panelist turns | Q&A audience merges |
|---|---|---|
| Vox Populi | Clean | 1 merge (Elena Lazar + Ava Federle → speaker_f) |
| Breaking Point | Clean | 1 merge (Prince Faisal + Mustafa Barghouti → speaker_c) |
| West-West Divide | Clean | **4 merges** — the most complex Q&A of the three, with 6 distinct audience interventions collapsing into 4 panelist labels |

**Mitigation — the prompt catches these:** The Speaker ID node's explicit 
`missing_introduction` and `potential_split` flag types work exactly as 
designed. Every merge in testing was correctly flagged in `review_queue.diarization_flags` 
for human review rather than silently corrupting the attribution. This is the 
**right failure mode** — flag the uncertainty, let the morning editor resolve it.

**Mitigation — recording protocol implications:** If the A/V team can route 
audience question mics to a **separate audio channel** from the panel mics, 
AssemblyAI can transcribe each channel independently and the audience/panel 
contamination disappears. This is a recording-protocol change, not a pipeline 
change. Worth flagging to HoBB: *the best way to avoid audience-panel speaker 
confusion is to not record them on the same track in the first place.*

---

## 7. Live simultaneous interpretation gets captured as English

**Insertion point:** Step 1 "ASR + diarization" implementation notes, new 
"Multilingual content" subsection.

**Observed in Breaking Point:** Colombian Defence Minister Pedro Sánchez Suárez 
explicitly said *"I would like to switch to Spanish in order to have more 
fluency in my words"* and then delivered his substantive content. The raw 
AssemblyAI diarized output already showed that content in fluent English, 
despite the pipeline not running any translation step.

**Mechanism:** The MSC provides live simultaneous interpretation, and the 
English interpreter's voice was captured on the same audio track as the 
speaker. AssemblyAI transcribed whichever voice was louder in each segment, 
which for non-English speakers meant the interpreter. The cleaning prompt 
is *not* translating — it's receiving English input from AssemblyAI.

**Implication for Athens:** If any WBBF session has non-English contributors 
and live interpretation, the transcription will reflect the interpreter's 
English, not the speaker's original language. The upside: downstream 
processing works normally. The downside: the interpreter's phrasing replaces 
the speaker's own — attribution is still correct (the position belongs to 
Sánchez), but the verbatim quote belongs to an unnamed interpreter. This 
matters for the `quote` field of any downstream extraction.

**Decision needed:** For Athens, should the Researcher's `quote` field be 
flagged when the source was interpreted? A simple heuristic: if the session 
metadata declares a language other than English for a speaker's native use, 
any verbatim quote attributed to that speaker should be marked `[interpreted]`. 
Worth discussing with Till before Athens.

---

## 8. Language detection must be enabled on the AssemblyAI config

**Insertion point:** Step 1 implementation, required config fields.

```python
config = aai.TranscriptionConfig(
    speaker_labels=True,
    speakers_expected=expected + 2,  # room for audience + buffer
    language_detection=True,  # required for multilingual panels
)
config.raw.speech_models = ["universal-3-pro"]
```

Without `language_detection=True`, AssemblyAI defaults to English-only 
processing and can produce garbled output when a speaker briefly switches 
languages. With it enabled, the model gracefully handles mid-session language 
switches (including the interpreter-capture behavior documented in section 7).

---

## 9. AssemblyAI SDK version drift — use raw field injection

**Insertion point:** Step 1 implementation, SDK compatibility notes.

**Discovered during testing:** The `assemblyai` Python SDK version 0.59.0 
(current on PyPI as of Apr 2026) lags behind the AssemblyAI server API in 
several important ways:

1. The SDK's `TranscriptionConfig` constructor sends the deprecated singular 
   field `speech_model` instead of the required plural `speech_models`.
2. The SDK exposes `word_boost` / `boost_param` parameters that universal-3-pro 
   rejects — the replacement is `keyterms_prompt` (a list of specific terms) 
   or `prompt` (natural-language context), but **not both in the same request**.
3. The SDK's `SpeechModel` enum exposes `best`, `nano`, `slam_1`, `universal` — 
   but the server only accepts `universal-3-pro` and `universal-2` as valid 
   values for the plural `speech_models` field.

**Resolution pattern:** Bypass the constructor fields and inject raw values 
directly on the pydantic model. This keeps the pipeline working with the 
current SDK while still using current API features:

```python
config = aai.TranscriptionConfig(
    speaker_labels=True,
    speakers_expected=expected + 2,
    language_detection=True,
    # do NOT set speech_model, word_boost, boost_param here
)
config.raw.speech_models = ["universal-3-pro"]
config.raw.speech_model = None  # clear the deprecated singular
if vocabulary_terms:
    config.raw.keyterms_prompt = vocabulary_terms
# NB: do not set config.raw.prompt if keyterms_prompt is set — 
# the server rejects requests that include both
```

**Monitoring recommendation:** On SDK upgrade, retest the transcription pipeline 
end-to-end before Athens. If AssemblyAI releases a newer SDK that supports 
the current fields natively, the `config.raw.*` workarounds can be removed.

---

## 10. Researcher and downstream pipelines need speaker confidence to flow through

**Insertion point:** Data contract section, `session_package.json` schema.

**Observed:** The cleaning task produces a `confidence` field on each turn 
(`high` / `medium` / `low`). Tonight's three test sessions all returned 100% 
high confidence, so the downstream behavior on medium/low turns is untested. 
But the **contract** with the Researcher pipeline requires that confidence 
flow through: the Researcher's Node 1 extraction instructions explicitly 
say to append the flag to the speaker name (e.g., `"Jon Alexander [medium]"`) 
when confidence is not high.

This means `session_package.json` must preserve the per-turn confidence field 
and the Researcher must read it. Validated by reading the output schema:

```json
{
  "transcript": {
    "speakers_present": [...],
    "turns": [
      {
        "turn_index": 0,
        "speaker": "Katrin Bennhold",
        "confidence": "high",
        "text": "..."
      }
    ]
  }
}
```

Confirmed present in all three test session packages.


---

## 11. Speaker ID should re-attribute individual contaminated turns, not just flag them

**Insertion point:** Step 3 "Speaker identification" prompt, new behavior section.

**Problem observed on West-West Divide:** When AssemblyAI diarization merges 
multiple distinct speakers under one label (primarily during open Q&A), the 
Speaker ID prompt currently identifies the label by its dominant speaker and 
then flags the merge in `review_queue.diarization_flags`. The flag is accurate, 
but the per-turn attribution in the transcript is not corrected.

**Concrete example** from `sessions/west_west_divide/session_package.json`:

- `speaker: "Hillary R. Clinton"` → `"I'm not from the Polish Foreign Ministry, 
  sorry. I'm a British MP. I wonder what the panel makes of the fact that 
  President Trump's administration is spending $200 million supporting far-right 
  and MAGA-friendly think tanks in Europe."`

Hillary Clinton is not a British MP. This is audience member Melanie Ward 
asking a question, mis-attributed because AssemblyAI merged her into Clinton's 
speaker_f label during Q&A. The diarization flag on speaker_f correctly 
identifies the issue, but a downstream Researcher reading `transcript.turns[]` 
sees the turn attributed to Clinton and would extract it as such unless it 
ALSO reads `review_queue.diarization_flags` and correctly interprets them.

**The fix is architectural, not a prompt tweak.** Correction belongs upstream 
in the Speaker ID stage, not downstream as a Researcher responsibility. The 
Speaker ID prompt should:

1. Identify the dominant speaker for each anonymous label (current behavior — 
   keep).
2. For each individual turn under a label, check whether the turn's content 
   is internally consistent with being spoken by that dominant speaker. 
   Specific red flags: self-introductions as a different name, questions 
   directed at the speaker themselves, content contradicting the speaker's 
   known role (e.g., an audience member saying "I'm a British MP" appearing 
   in a turn attributed to Clinton).
3. Re-attribute such turns to "Audience Member N" on a per-turn basis, 
   leaving the rest of the label's turns attributed to the dominant speaker.
4. Document which turn indices were re-assigned in the `flags` output so a 
   human editor can verify.

**Prompt addition** (to be inserted into SPEAKER_ID_SYSTEM under the existing 
four-pass workflow):

> PASS 5 — Per-turn sanity check. After assigning dominant speakers to each 
> anonymous label, re-read each turn and check whether its content is 
> consistent with being spoken by the identified speaker. Red flags: the 
> turn is a self-introduction as a different name ("I'm [Name] from [Org]"); 
> the turn is a question directed at the very speaker the label is assigned 
> to ("I have a question for Secretary Clinton..."); the turn claims a role 
> the identified speaker does not hold ("I'm a British MP" in a turn 
> attributed to a non-British non-MP). When a turn is inconsistent, the 
> diarization has merged audience voices into a panelist's label — re-assign 
> that specific turn to "Audience Member N" while leaving the panelist's 
> other turns unchanged. Record the re-assignment in flags with the 
> anonymous_label, the specific turn indices, and the reason.

This pushes correction upstream where it belongs. The Researcher then reads 
a clean transcript where every turn's speaker attribution can be trusted, 
and the `review_queue.diarization_flags` becomes a record of what was fixed 
rather than a list of what still needs fixing.

**Frequency of need:** Of tonight's three test sessions, West-West Divide had 
4 distinct contamination incidents affecting turns in the Q&A portion. Vox 
Populi had 1 (Elena Lazar / Ava Federle merge). Breaking Point had 1 (Prince 
Faisal / Mustafa Barghouti merge). For Athens production with 6-9 sessions 
per night, expect 0-4 contamination incidents per session based on Q&A 
presence and complexity.

**Schema note for the re-attribution output:** The existing `verify_markers` 
section of `review_queue` already uses a back-reference pattern: each marker 
has `{"index": N, "text": "..."}` pointing at a specific turn in 
`transcript.turns[]`. Re-attribution records should use the same pattern 
to stay consistent:

```json
"review_queue": {
  "diarization_flags": [
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

This preserves traceability (a human editor can jump to turns 105, 107, 110 
to verify) and makes it easy to undo a mis-correction if one happens.


---

## 12. `review_queue` is orphaned — no downstream stage reads it

**Insertion point:** Data contract section, session_package.json schema, 
after the review_queue definition.

**The gap:** The Transcription Pipeline writes three things into 
`session_package.review_queue`:

1. `low_confidence_attributions` — Speaker ID mappings with confidence < high
2. `diarization_flags` — potential merges/splits noticed by Speaker ID
3. `verify_markers` — turns containing `[verify]` tags from Cleaning

The Researcher Pipeline's Node 1 prompt reads `metadata` and 
`transcript.turns[]`. It does **not** read `review_queue`. Reviewing the 
Researcher Pipeline doc confirms this: the user prompt block enumerates 
`session_title`, `session_description`, `roster`, `speakers_present`, 
`turns` — no mention of `review_queue`.

Neither does the Provocateur, the Voice nodes, or anything else downstream. 
`review_queue` is currently **write-only** — the Transcription Pipeline 
generates it and nothing consumes it before the breakfast deadline.

**Original design assumption (now broken):** An implicit human editor would 
read `review.md`, open `session_package.json`, correct errors flagged in 
`review_queue`, and save before the Researcher runs. The Athens pipeline 
is overnight and automated — there is no such human editor in the loop. 
No one is awake at 3am to handle flags.

**Recommended fix (two-part):**

**Part A (upstream, already proposed as section 11):** Speaker ID re-attributes 
contaminated turns to audience members on the spot rather than flagging them 
for later human review. This eliminates the diarization_flags class of 
orphaned data — the pipeline corrects what it can correct.

**Part B (downstream, new):** The Researcher reads `review_queue.verify_markers` 
and treats flagged turns as lower-confidence for the quote field specifically. 
Add to Researcher Node 1 system prompt:

> The session package includes a `review_queue.verify_markers` field listing 
> turn indices where the cleaning pass flagged words as uncertain (commonly 
> proper names, acronyms, or policy-specific terms). When extracting an 
> assertion, reframing, or open question whose substance hinges on a 
> `[verify]`-tagged word — e.g., the extraction is centrally about that 
> specific entity — mark the extraction's context field with 
> "[word uncertain in source]" and flag it for human review. When the 
> extraction's substance does not depend on the uncertain word, extract 
> normally.

Add to Researcher Node 1 user prompt:

```
Review queue (turns with [verify] markers needing human confirmation):
{{review_queue.verify_markers}}
```

**Result after both fixes:**

- `low_confidence_attributions` → still currently unused. Could be removed, 
  or retained as a diagnostic field for pipeline monitoring (count per 
  session tracks Speaker ID quality over time).
- `diarization_flags` → becomes a log of what was corrected upstream, not a 
  to-do list. Still valuable for auditing and for tracking when AssemblyAI's 
  diarization struggles, but no downstream stage needs to act on it.
- `verify_markers` → actively consumed by the Researcher, which degrades 
  extraction confidence when uncertainty matters.

**Alternative considered and rejected — human-in-the-loop pause:** Adding a 
Slack-notification-and-wait step between Cleaning and Researcher would let 
a morning editor fix flags before downstream runs. This is closest to the 
original design intent but requires staffing the breakfast deadline with 
someone awake at 3-5am to handle flags, which isn't realistic for Athens. 
Keep the pipeline fully automated; make the stages robust enough that no 
human step is required.


---

## 13. AssemblyAI native speaker_identification is not a drop-in replacement

**Insertion point:** Step 3 "Speaker identification" implementation notes, 
"Alternatives considered" subsection.

**Background:** A market survey conducted Apr 14 2026 identified AssemblyAI's 
Speech Understanding API with `SpeakerIdentificationRequest` and `known_values` 
as the closest commercial equivalent to the custom Claude-based Speaker ID 
stage. The survey suggested this could potentially replace ~150 lines of 
custom orchestration with a single config field.

**Investigation outcome:** The feature exists in the SDK 0.59.0 type 
definitions (`aai.SpeakerIdentificationRequest`, `aai.SpeakerType.name`, 
`aai.types.SpeechUnderstandingFeatureRequests`), and the main 
`TranscriptionConfig` exposes a `speech_understanding` field. However, 
submitting a transcription request with `speech_understanding.speaker_identification` 
populated returns a server-side error:

> `"Invalid endpoint schema, please refer to documentation for examples."`

This indicates Speech Understanding is a **separate API endpoint** that runs 
on top of a completed transcript (transcribe first, then call a distinct 
speech-understanding endpoint with the transcript ID), not a parameter on 
the standard `/transcript` submission. SDK 0.59.0 exposes the request/response 
types but does not expose the client method to call this second endpoint. 
Using it would require either raw HTTP plumbing or waiting for a newer SDK.

**Architectural incompatibility even if it worked:** Even if the plumbing 
were accessible, AssemblyAI's native speaker_identification provides 
label-to-name mapping only. It does NOT produce:

- Evidence fields ("self-identifies at 03:42 as 'Minister of Defense'")
- Confidence reasoning (the four-pass workflow currently in SPEAKER_ID_SYSTEM)
- Bio-based expertise matching (Pass 3 of our current prompt)
- Diarization contamination detection (which the custom prompt caught 
  correctly on all three MSC 2026 test sessions — see section 11)

The Researcher pipeline's downstream logic depends on evidence and confidence 
flowing through, not just names. Replacing the Claude-based Speaker ID with 
AssemblyAI's native feature would produce a simpler pipeline that feeds the 
Researcher less useful data.

**Decision:** Keep the custom Sonnet 4.6 Speaker ID stage. Revisit only if:

1. AssemblyAI publishes an SDK version that exposes the Speech Understanding 
   endpoint directly (likely within 6-12 months)
2. AND that endpoint is extended to return evidence/confidence metadata, 
   not just label-to-name mapping (no public roadmap signal as of Apr 2026)
3. AND the cost per call is meaningfully lower than the current ~$0.05 per 
   Speaker ID call via Claude (unlikely to matter at Athens scale of $25-40 
   total)

All three conditions would need to hold. None hold today. The custom approach 
is architecturally correct for the AI Assembly's requirements and will 
remain so until AssemblyAI ships a fundamentally different product tier.

