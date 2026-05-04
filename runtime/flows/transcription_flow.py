#!/usr/bin/env python3
"""
AI Assembly Transcription Pipeline — Prefect flow.

Runs a single session through the full chain:

  Step 1: AssemblyAI Universal-3 Pro  (ASR + diarization + language detection)
  Step 2: Claude  — Speaker Identification (5-pass attribution: explicit name
          cues → role detection → expertise matching → confidence assignment
          → per-turn sanity check). See prompts/transcription_speaker_id.md.
  Step 3: Claude  — Cleaning (constrained ASR repair, no paraphrase). See
          prompts/transcription_cleaning.md.
  Step 4: Assemble the session_package.json the Researcher consumes.

Level 2 usage (laptop, no Prefect server needed):
    export ANTHROPIC_API_KEY=sk-ant-...
    export ASSEMBLYAI_API_KEY=...
    pip install assemblyai anthropic prefect
    python transcription_flow.py path/to/audio.mp4 path/to/session.json

Level 3 usage (VM with Prefect server):
    Start the server once (prefect server start), register (prefect deploy),
    then bind a file watcher to trigger the flow when files land in
    /mnt/drive/recordings/.

The flow function itself is the same at both levels. Only the entry
point (CLI arg vs file watcher) and the output directory change.

Outputs (written to OUTPUT_DIR, default = current directory):
  out_01_diarized.json     — raw AssemblyAI turns
  out_02_speaker_id.json   — Claude's mapping with evidence and flags
  out_03_cleaned.json      — Claude's cleaned turns
  session_package.json     — final Researcher-ready package
  review.md                — human-readable summary
"""

import json
import os
import sys
import time
from pathlib import Path

# Make `flows.shared.io` importable when this script is run directly
# (python flows/transcription_flow.py ...) — add the repo root to sys.path
# before the try/except that imports third-party deps.
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

try:
    import assemblyai as aai
    from anthropic import Anthropic
    from prefect import flow, task, get_run_logger
    from prefect.tasks import exponential_backoff
    from dotenv import load_dotenv
    load_dotenv(_REPO_ROOT.parent / ".env", override=True)
    from flows.shared.io import load_prompt, get_logger, extract_json, write_json_atomic
except ImportError as e:
    sys.stderr.write(
        f"Missing dependency: {e.name}\n"
        "Install with:  pip install assemblyai anthropic prefect\n"
    )
    sys.exit(1)


# --- Config ---------------------------------------------------------------

# Per-flow override takes precedence over the shared CLAUDE_MODEL.
# This prevents `export CLAUDE_MODEL=claude-opus-4-7` from silently
# upgrading the cleaning pass (which doesn't benefit from Opus) along
# with Researcher/Provocateur (which do).
CLAUDE_MODEL = os.environ.get(
    "TRANSCRIPTION_CLAUDE_MODEL",
    os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-6"),
)
CLAUDE_MAX_TOKENS = 64000

# Optional per-step model override for Speaker ID. Defaults to
# CLAUDE_MODEL (Sonnet in the baseline config). Set to
# "claude-opus-4-7" for difficult sessions where the extra reasoning
# capacity helps — non-native English speakers, complex multi-person
# Q&A, incomplete roster metadata, or any session where Pass 5
# re-attribution has to do non-trivial work. Cleaning and semantic
# drift verification stay on CLAUDE_MODEL (Sonnet) — the cost/benefit
# does not favor Opus for those steps.
SPEAKER_ID_MODEL = os.environ.get(
    "TRANSCRIPTION_SPEAKER_ID_MODEL", CLAUDE_MODEL
)

# Output directory — overridable so Level 3 can point at /mnt/drive/transcripts/dayN/.
# When unset (CLI standalone use), defaults to the audio file's parent dir
# inside process_session() — see _resolve_output_dir(). The module-level value
# below is kept only for callers that import OUTPUT_DIR directly, but that
# path is no longer used inside this module (C31 fix 2026-05-04).
OUTPUT_DIR = Path(os.environ.get("OUTPUT_DIR", "."))


def _resolve_output_dir(audio_path: Path) -> Path:
    """Resolve the per-session output directory.

    Precedence:
      1. OUTPUT_DIR env var (set by ingest layer, orchestrator, Prefect runner)
      2. audio_path.parent (CLI standalone use — outputs land alongside audio)

    Defaulting to audio.parent fixes the C31 footgun where parallel CLI runs
    without OUTPUT_DIR set would all write to CWD and overwrite each other.
    """
    env = os.environ.get("OUTPUT_DIR")
    if env:
        return Path(env)
    return audio_path.parent


# --- Logger shim ----------------------------------------------------------
# Delegates to flows.shared.io.get_logger so all three flows share one
# implementation. Returns the Prefect run logger inside a run context,
# a stdlib stderr logger otherwise.

def _get_logger():
    return get_logger("transcription_flow")


# --- Prompts --------------------------------------------------------------
#
# The canonical prompt text lives as .md files under flows/shared/prompts/
# so they can be reviewed in git without wading through Python string
# literals and edited without touching code. See flows/shared/io.load_prompt.
#
# Speaker ID prompt is v2 (FIVE passes, Pass 5 = per-turn sanity check with
# reassigned_turns output). Cleaning prompt is unchanged from v1.

SPEAKER_ID_SYSTEM = load_prompt("transcription_speaker_id")
CLEANING_SYSTEM = load_prompt("transcription_cleaning")


# --- Helpers (non-task — used inside tasks and the flow) ------------------

def load_session(path):
    with open(path) as f:
        return json.load(f)


def build_vocabulary(session):
    """Flat list of proper nouns from the roster. Used for AssemblyAI word_boost
    and Claude cleaning context."""
    vocab = []
    seen = set()
    for c in session.get("roster", []):
        for part in c["name"].split():
            if part not in seen:
                seen.add(part)
                vocab.append(part)
        aff = c.get("affiliation", "")
        for word in aff.replace("/", " ").replace(",", " ").split():
            word = word.strip()
            if len(word) > 2 and word[0].isupper() and word not in seen:
                seen.add(word)
                vocab.append(word)
    return vocab


def merge_speaker_ids(turns, mapping_output):
    """Apply Speaker ID output to raw diarized turns.

    Two-step process:
    1. Apply `mappings` to translate each turn's anonymous_label into a
       named speaker with role and confidence.
    2. Apply `flags` of type `reassigned_turns` to override individual
       turns whose content Pass 5 identified as contamination — either
       merged audience voices, or a different panelist's turn captured
       under the wrong label.

    For step 2, the reassignment target can be either a roster name
    (another panelist who was confused with the original) or an audience
    member. The role and confidence on the reassigned turn depend on
    which case applies:
    - If `reassigned_to` matches an identified_name from step 1, inherit
      that speaker's role and confidence.
    - Otherwise (e.g., "Audience Member 5"), mark as audience/high.
    """
    mapping = {
        m["anonymous_label"]: m
        for m in mapping_output.get("mappings", [])
    }

    # Build a name -> (role, confidence) lookup so Pass 5 reassignments
    # to other named panelists inherit the right role instead of being
    # hardcoded as "audience"
    name_to_role = {}
    for m in mapping_output.get("mappings", []):
        name = m.get("identified_name")
        if name:
            name_to_role[name] = (
                m.get("role", "panelist"),
                m.get("confidence", "high"),
            )

    # Step 1: apply label-to-name mapping
    unknown_counter = 0
    named = []
    for t in turns:
        m = mapping.get(t["anonymous_label"])
        if m:
            named.append({
                "speaker": m.get("identified_name", "Unidentified"),
                "role": m.get("role", "unknown"),
                "confidence": m.get("confidence", "low"),
                "text": t["text"],
            })
        else:
            unknown_counter += 1
            named.append({
                "speaker": f"Unidentified Speaker {unknown_counter}",
                "role": "unknown",
                "confidence": "low",
                "text": t["text"],
            })

    # Step 2: apply Pass 5 per-turn reassignments from `flags`
    logger = _get_logger()

    for flag in mapping_output.get("flags", []):
        if flag.get("type") != "reassigned_turns":
            continue
        indices = flag.get("reassigned_turn_indices", []) or []
        target = flag.get("reassigned_to", "Audience Member ?")

        # Look up role/confidence: if target is a roster panelist, inherit
        # their attributes; otherwise it's an audience member
        if target in name_to_role:
            target_role, target_confidence = name_to_role[target]
        else:
            target_role, target_confidence = "audience", "high"

        for idx in indices:
            if not isinstance(idx, int) or idx < 0 or idx >= len(named):
                logger.warning(
                    f"Pass 5 reassigned_turns references out-of-range "
                    f"index {idx} (transcript has {len(named)} turns). "
                    f"Ignoring."
                )
                continue
            named[idx] = {
                "speaker": target,
                "role": target_role,
                "confidence": target_confidence,
                "text": named[idx]["text"],
            }

    return named


def build_review_md(session, id_output, cleaned_turns):
    md = [f"# Review — {session['session_title']}\n"]

    speakers_present = sorted(set(t["speaker"] for t in cleaned_turns))
    conf_counts = {}
    for t in cleaned_turns:
        conf_counts[t["confidence"]] = conf_counts.get(t["confidence"], 0) + 1

    md.append("## Summary\n")
    md.append(f"- Roster size: {len(session.get('roster', []))}")
    md.append(f"- Speakers actually present: {len(speakers_present)}")
    md.append(f"- Total turns: {len(cleaned_turns)}")
    md.append(f"- Confidence breakdown: {conf_counts}")
    md.append("")

    md.append("## Speaker mappings\n")
    for m in id_output.get("mappings", []):
        md.append(
            f"- `{m.get('anonymous_label')}` -> **{m.get('identified_name')}** "
            f"[{m.get('confidence')}] | {m.get('role')}"
        )
        md.append(f"  - Evidence: {m.get('evidence', '-')}")
    md.append("")

    if id_output.get("flags"):
        md.append("## Flags\n")
        for f in id_output["flags"]:
            md.append(
                f"- **{f.get('type')}** {f.get('labels', '')}: "
                f"{f.get('note', '')}"
            )
        md.append("")

    md.append("## Named transcript (first 20 turns)\n")
    for t in cleaned_turns[:20]:
        md.append(f"**{t['speaker']}** [{t['confidence']}]: {t['text']}")
        md.append("")

    return "\n".join(md)


# --- Prefect tasks --------------------------------------------------------

# Optional caching on the AssemblyAI call. Development-only — when iterating
# on prompts downstream, re-running the flow would otherwise pay the ~$0.35
# ASR cost every time. Enable with TRANSCRIPTION_CACHE=1 in .env or CLI.
# Production Athens runs should leave this OFF (every session is fresh;
# accidentally serving stale cached audio is a worse failure mode than
# paying full cost).
#
# Note: task_input_hash hashes the input VALUES (audio_path as a str,
# session as a dict), not the file content. If the same path is reused
# with different audio, the cache will return stale output. Fine for
# development where we keep stable sample files, dangerous in production.
_ASR_CACHE_KWARGS: dict = {}
if os.environ.get("TRANSCRIPTION_CACHE") == "1":
    from datetime import timedelta
    from prefect.tasks import task_input_hash
    _ASR_CACHE_KWARGS = {
        "cache_key_fn": task_input_hash,
        "cache_expiration": timedelta(days=30),
    }
    print(
        "TRANSCRIPTION_CACHE=1 — AssemblyAI task caching enabled. "
        "Disable before Athens production runs.",
        file=sys.stderr,
    )


@task(
    name="transcribe-assemblyai",
    retries=3,
    retry_delay_seconds=exponential_backoff(backoff_factor=10),
    retry_jitter_factor=0.3,
    **_ASR_CACHE_KWARGS,
)
def transcribe_with_assemblyai(audio_path, session):
    """Step 1: AssemblyAI Universal-3 Pro - ASR + diarization + language detection.

    Retries on transient network or API failures. Malformed audio surfaces
    as a RuntimeError and halts the flow.
    """
    logger = _get_logger()
    aai.settings.api_key = os.environ["ASSEMBLYAI_API_KEY"]

    expected = session.get(
        "expected_speaker_count", len(session.get("roster", [])) or 10
    )
    vocab = build_vocabulary(session)

    # NOTE: the production pipeline spec calls for custom_spelling and a
    # natural-language ASR context prompt. Level 2 uses word_boost, which
    # is simpler and gets most of the benefit. Put the richer config back
    # for Level 3 production runs.
    config = aai.TranscriptionConfig(
        speaker_labels=True,
        speakers_expected=expected + 2,
        language_detection=True,
    )
    # SDK 0.59.0 uses deprecated/incompatible fields for universal-3-pro.
    # Inject the modern fields directly on the raw model.
    config.raw.speech_models = ["universal-3-pro"]
    config.raw.speech_model = None
    if vocab:
        # universal-3-pro replaces word_boost with keyterms_prompt for
        # biasing recognition toward specific names and terms.
        # Note: AssemblyAI rejects requests that combine `prompt` and
        # `keyterms_prompt`, so we choose keyterms (specific names beat
        # generic context for downstream Speaker ID matching).
        config.raw.keyterms_prompt = vocab

    transcriber = aai.Transcriber(config=config)
    logger.info(f"Transcribing {audio_path.name} (expected speakers: {expected})")
    t0 = time.time()
    transcript = transcriber.transcribe(str(audio_path))

    if transcript.status == aai.TranscriptStatus.error:
        raise RuntimeError(f"AssemblyAI error: {transcript.error}")

    speakers = sorted(set(u.speaker for u in transcript.utterances))
    logger.info(
        f"AssemblyAI done in {time.time()-t0:.1f}s. "
        f"Detected {len(speakers)} speakers across {len(transcript.utterances)} turns."
    )

    turns = []
    for i, utt in enumerate(transcript.utterances):
        turns.append({
            "index": i,
            "anonymous_label": f"speaker_{utt.speaker.lower()}",
            "start_ms": utt.start,
            "end_ms": utt.end,
            "text": utt.text,
        })
    return turns


@task(
    name="identify-speakers",
    retries=2,
    retry_delay_seconds=exponential_backoff(backoff_factor=5),
)
def identify_speakers(turns, session):
    """Step 2: Claude - multi-pass speaker identification."""
    logger = _get_logger()
    client = Anthropic()

    roster_lines = []
    for c in session.get("roster", []):
        line = f"- {c['name']}"
        if c.get("title"):
            line += f", {c['title']}"
        if c.get("affiliation"):
            line += f", {c['affiliation']}"
        if c.get("bio"):
            line += f"\n  Bio: {c['bio']}"
        roster_lines.append(line)

    # Strip timestamps for the ID pass - the prompt only needs label + text,
    # plus turn_index so Pass 5 can report reassigned_turn_indices.
    compact_turns = [
        {
            "turn_index": i,
            "anonymous_label": t["anonymous_label"],
            "text": t["text"],
        }
        for i, t in enumerate(turns)
    ]

    user = (
        f"Session: {session['session_title']}\n"
        f"Format: {session.get('session_format', 'panel')}\n"
        f"Description: {session.get('session_description', '')}\n\n"
        f"Roster:\n" + "\n".join(roster_lines) + "\n\n"
        f"Diarized transcript:\n"
        f"{json.dumps(compact_turns, indent=2, ensure_ascii=False)}"
    )

    logger.info(f"Speaker ID pass (model={SPEAKER_ID_MODEL})")
    t0 = time.time()
    # Intentional exception to the "thinking ON for every Opus 4.7 call" rule:
    # Speaker ID output is small (mappings + flags, <2K tokens), so adaptive
    # thinking's latency cost is large relative to benefit. Per
    # docs/AI_Assembly_Transcription_Pipeline.md "Model selection" section.
    # Speaker ID output is small (mappings + flags, typically <2K tokens).
    # Use a tight per-call cap so we stay under the SDK's 21K non-streaming
    # threshold regardless of the global CLAUDE_MAX_TOKENS budget.
    resp = client.messages.create(
        model=SPEAKER_ID_MODEL,
        max_tokens=4096,
        system=SPEAKER_ID_SYSTEM,
        messages=[{"role": "user", "content": user}],
    )
    logger.info(
        f"  done in {time.time()-t0:.1f}s "
        f"(in={resp.usage.input_tokens}, out={resp.usage.output_tokens})"
    )
    return extract_json(resp.content[0].text)


@task(
    name="clean-transcript",
    retries=2,
    retry_delay_seconds=exponential_backoff(backoff_factor=5),
)
def clean_transcript(named_turns, session, vocabulary):
    """Step 3: Claude - constrained ASR cleaning."""
    logger = _get_logger()
    client = Anthropic()

    user = (
        f"Vocabulary (correct spellings of proper nouns):\n"
        f"{', '.join(vocabulary) if vocabulary else '(none)'}\n\n"
        f"Session context: {session['session_title']} - "
        f"{session.get('session_description', '')}\n\n"
        f"Named transcript:\n"
        f"{json.dumps(named_turns, indent=2, ensure_ascii=False)}"
    )

    logger.info(f"Cleaning pass (model={CLAUDE_MODEL}, streaming)")
    t0 = time.time()
    # Intentional exception to the "thinking ON for every Opus 4.7 call" rule:
    # Cleaning is the largest LLM call by output volume (~18K tokens on big
    # panels) and the work is mostly local per turn, not cross-turn synthesis.
    # Thinking adds little. Per docs/AI_Assembly_Transcription_Pipeline.md.
    # Streaming required for max_tokens > ~21K. The SDK's non-streaming path
    # has a 10-minute connection timeout that's incompatible with long
    # cleaning passes on larger transcripts. Streaming holds the connection
    # open via SSE chunks and lets us collect the full response safely.
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
    logger.info(
        f"  done in {time.time()-t0:.1f}s "
        f"(in={final.usage.input_tokens}, out={final.usage.output_tokens})"
    )
    # Warn if we used >80% of the budget — likely a sign the cleaning is
    # close to truncating and we should bump CLAUDE_MAX_TOKENS for next run.
    if final.usage.output_tokens > CLAUDE_MAX_TOKENS * 0.8:
        logger.warning(
            f"Cleaning used {final.usage.output_tokens}/{CLAUDE_MAX_TOKENS} "
            f"output tokens (>80%). Consider increasing CLAUDE_MAX_TOKENS."
        )
    return extract_json(full_text)


@task(name="assemble-session-package")
def assemble_session_package(session, id_output, cleaned_turns):
    """Step 4: assemble the Researcher-ready session package."""
    speakers_present = sorted(set(t["speaker"] for t in cleaned_turns))
    return {
        "metadata": {
            "session_id": session.get("session_id", "test_session"),
            "session_title": session["session_title"],
            "session_description": session.get("session_description", ""),
            "session_format": session.get("session_format", "panel"),
            "track": session.get("track", ""),
            "date_time": session.get("date_time", ""),
            "venue": session.get("venue", ""),
            "roster": session.get("roster", []),
        },
        "transcript": {
            "speakers_present": speakers_present,
            "turns": [
                {"turn_index": i, **t} for i, t in enumerate(cleaned_turns)
            ],
        },
        "review_queue": {
            "low_confidence_attributions": [
                m for m in id_output.get("mappings", [])
                if m.get("confidence") == "low"
            ],
            "diarization_flags": id_output.get("flags", []),
            "verify_markers": [
                {"index": i, "text": t["text"]}
                for i, t in enumerate(cleaned_turns)
                if "[verify]" in t["text"]
            ],
        },
    }


@task(name="write-outputs")
def write_outputs(output_dir, turns, id_output, cleaned_turns, package, session):
    logger = _get_logger()
    output_dir.mkdir(parents=True, exist_ok=True)

    files = {
        "out_01_diarized.json": turns,
        "out_02_speaker_id.json": id_output,
        "out_03_cleaned.json": cleaned_turns,
        "session_package.json": package,
    }
    for name, data in files.items():
        write_json_atomic(output_dir / name, data)
        logger.info(f"Wrote {output_dir / name}")

    # review.md is human-readable, not JSON — but still write atomically
    # so a partial write doesn't leave a half-formed file on disk.
    review_md = build_review_md(session, id_output, cleaned_turns)
    review_path = output_dir / "review.md"
    tmp = review_path.with_suffix(review_path.suffix + ".tmp")
    try:
        tmp.write_text(review_md, encoding="utf-8")
        tmp.replace(review_path)
    except Exception:
        tmp.unlink(missing_ok=True)
        raise
    logger.info(f"Wrote {review_path}")


# --- Prefect flow ---------------------------------------------------------

@flow(name="transcription-pipeline")
def process_session(audio_path, session_path):
    """The full transcription pipeline for a single session.

    This flow is called from the CLI at Level 2 and from a file watcher
    at Level 3. The body is identical in both cases - only the caller
    differs.

    Returns the session package for optional in-process consumers.
    """
    logger = _get_logger()

    audio = Path(audio_path)
    session_json = Path(session_path)

    if not audio.exists():
        raise FileNotFoundError(f"Audio file not found: {audio}")
    if not session_json.exists():
        raise FileNotFoundError(f"Session JSON not found: {session_json}")

    for key in ("ANTHROPIC_API_KEY", "ASSEMBLYAI_API_KEY"):
        if not os.environ.get(key):
            raise RuntimeError(f"Missing environment variable: {key}")

    session = load_session(session_json)
    logger.info(f"Processing session: {session['session_title']}")

    out = _resolve_output_dir(audio)
    out.mkdir(parents=True, exist_ok=True)
    logger.info(f"Output directory: {out}")

    # Step 2: AssemblyAI — skip if output already on disk (e.g. retry after later failure)
    p1 = out / "out_01_diarized.json"
    if p1.exists():
        turns = json.loads(p1.read_text(encoding="utf-8"))
        logger.info(f"Resuming: loaded {p1.name} from disk (skipping AssemblyAI)")
    else:
        turns = transcribe_with_assemblyai(audio, session)
        p1.write_text(json.dumps(turns, indent=2, ensure_ascii=False))

    # Step 3: Speaker ID
    p2 = out / "out_02_speaker_id.json"
    if p2.exists():
        id_output = json.loads(p2.read_text(encoding="utf-8"))
        logger.info(f"Resuming: loaded {p2.name} from disk (skipping Speaker ID)")
    else:
        id_output = identify_speakers(turns, session)
        p2.write_text(json.dumps(id_output, indent=2, ensure_ascii=False))
    named_turns = merge_speaker_ids(turns, id_output)

    # Step 4: Cleaning
    p3 = out / "out_03_cleaned.json"
    if p3.exists():
        cleaned_turns = json.loads(p3.read_text(encoding="utf-8"))
        logger.info(f"Resuming: loaded {p3.name} from disk (skipping Cleaning)")
    else:
        vocab = build_vocabulary(session)
        cleaned_turns = clean_transcript(named_turns, session, vocab)
        # Validate shape — Claude occasionally wraps the array in an object.
        if isinstance(cleaned_turns, dict):
            for key in ("turns", "transcript", "cleaned_turns", "items"):
                if isinstance(cleaned_turns.get(key), list):
                    logger.warning(f"clean_transcript: unwrapping dict key '{key}'")
                    cleaned_turns = cleaned_turns[key]
                    break
        if not isinstance(cleaned_turns, list):
            raise RuntimeError(
                f"clean_transcript returned unexpected type {type(cleaned_turns).__name__}; "
                f"first 300 chars: {json.dumps(cleaned_turns)[:300]}"
            )
        p3.write_text(json.dumps(cleaned_turns, indent=2, ensure_ascii=False))

    # Step 5: Package + write. `write_outputs` always re-writes all five files,
    # even when Steps 2-4 were resumed from disk. This is intentional — the
    # writes are idempotent and guarantee review.md + session_package.json
    # are always consistent with whatever turns/id_output/cleaned_turns we
    # have in memory (which may be loaded from older on-disk versions).
    package = assemble_session_package(session, id_output, cleaned_turns)
    write_outputs(out, turns, id_output, cleaned_turns, package, session)

    logger.info("Done. Start with review.md, then session_package.json if it looks right.")
    return package


# --- CLI entry point (Level 2) --------------------------------------------

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    process_session(sys.argv[1], sys.argv[2])
