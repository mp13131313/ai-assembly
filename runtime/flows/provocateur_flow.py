"""Provocateur Pipeline (v3) — flows/provocateur_flow.py

Reads the Researcher's output (grouping.json + all_extractions.json) and
produces per-voice briefing packages for the AI Assembly council.

Five-stage v3 architecture:
    Stage 1A — triage_voice (×N parallel LLM calls, one per voice):
        Provocateur reasons ABOUT each voice using profile data only,
        ranks themes (strong/moderate activation + is_stretch flag).
    Stage 1B — triage_flags (×1 parallel LLM call):
        Tags themes with worth_surfacing, audience_friction,
        fault_line_present + description.
    Stage 2 — python_select (pure Python, deterministic, NO LLM):
        Drops vetoed themes, scores per voice, computes theme_quality
        with friction + fault-line multipliers, enforces quorum,
        cascades, force-fits voices to a minimum, soft stretch swap.
    Stage 3 — formulate_for_member (×N parallel LLM calls, one per
        (theme, voice) pair, batched to respect rate limits):
        Each call produces formulation + theme_display_title +
        context_narrative + selected_quotes + grounding_extraction_ids
        + rationale, all aimed at this specific voice's territory.
    Stage 4 — package_voice_briefings (pure Python):
        Per-voice briefings with TWO views: narrative_briefing
        (markdown PROMPT for Voice Node Step 1) + full_theme_record
        (wider REASONING SURFACE for Step 1 thinking).

The council is NOT hard-coded. All editorial state — collective
landscape, audience paragraph, the 12 member profiles, and the
selection_parameters block (activation threshold, multipliers, caps,
stretch swap toggle) — lives in flows/shared/council/council_config.json.
Edit that file and re-run to swap the council. See
flows/shared/council/README.md for swap workflows.

Usage:
    python flows/provocateur_flow.py runs/dev_msc_test

Inputs (relative to the run directory):
    02_researcher/all_extractions.json
    02_researcher/grouping.json

Outputs (relative to the run directory):
    03_provocateur/triage_voices/{member_name_snake}.json  (one per voice)
    03_provocateur/triage_flags.json
    03_provocateur/selection.json
    03_provocateur/formulations/{theme_id}__{member_name_snake}.json  (one per pair)
    03_provocateur/briefings/{member_name_snake}.json  (one per member)
    03_provocateur/manifest.json

The per-voice and per-pair files are the source of truth — incremental
write checkpointing means a crash mid-run loses no completed work, and
restarting picks up exactly where the previous run left off. No
PROVOCATEUR_CACHE flag needed; the checkpoints ARE the cache. To force
a clean run, delete the relevant checkpoint files.

For a flat aggregated view of per-checkpoint files:
    cat triage_voices/*.json | jq -s '{voices: .}'
    cat formulations/*.json | jq -s '{formulations: .}'

For full architecture detail, see the v3 stage entry in the run's
_manifest.json (provocateur_v3_observations + post_audit_cleanup blocks).
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any

try:
    from anthropic import Anthropic
    from dotenv import load_dotenv
    from prefect import flow, task
    from prefect.tasks import exponential_backoff
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Install with:  pip install anthropic prefect python-dotenv")
    sys.exit(1)

# Make flows.shared importable regardless of whether we're run as a
# module or as a script from the repo root.
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

# Load .env from the repo root so ANTHROPIC_API_KEY is available when
# the flow runs as a script. Same pattern as researcher_flow and
# transcription_flow. `override=True` defends against the Claude Code
# agent-shell empty-env bug (parent shell pre-sets API keys to empty
# strings; default load_dotenv keeps them).
load_dotenv(_REPO_ROOT.parent / ".env", override=True)

from flows.shared.io import (
    extract_json,
    get_logger,
    get_member_by_name,
    load_council_config,
    load_prompt,
    member_slug,
    write_json_atomic,
)


# --- Config ---------------------------------------------------------------

# Default to Opus 4.7 — canonical model for Provocateur Pipeline v1 per
# the validation run on dev_msc_test. Override via CLAUDE_MODEL env var
# for dev iteration on Sonnet.
CLAUDE_MODEL = os.environ.get(
    "PROVOCATEUR_CLAUDE_MODEL",
    os.environ.get("CLAUDE_MODEL", "claude-opus-4-7"),
)

# Adaptive thinking for all three LLM tasks — the Provocateur is
# editorially heavy (activation scoring, coverage balancing, and
# grounded formulation writing) and benefits from extended thinking
# the same way the Researcher's clustering and theming do.
PROVOCATEUR_THINKING = os.environ.get("PROVOCATEUR_THINKING", "1") == "1"

# Max token budgets. Triage and Selection outputs are small but
# adaptive thinking tokens count against max_tokens, so the ceilings
# are generous. 40K matches the Researcher clustering task where
# thinking also runs. Selection hit the empty-response failure mode
# at 24K on the first run — bumped to 40K to match Triage.
TRIAGE_MAX_TOKENS = 40000
FORMULATION_MAX_TOKENS = 40000
# Note: no SELECTION_MAX_TOKENS — Selection is pure Python, no LLM call.


def _thinking_kwargs() -> dict[str, Any]:
    """Return the thinking block kwargs if thinking is enabled.

    `display: "summarized"` makes the model's thinking trace visible in
    the streamed response (Opus 4.7 default is `omitted`, which returns
    no thinking content). Matches the persona + voice pipeline pattern
    landed under FU#60.
    """
    if not PROVOCATEUR_THINKING:
        return {}
    return {"thinking": {"type": "adaptive", "display": "summarized"}}


def _get_logger() -> Any:
    """Return a logger that works inside or outside a Prefect task run.

    Delegates to flows.shared.io.get_logger — same implementation used by
    transcription_flow and researcher_flow.
    """
    return get_logger("provocateur_flow")


# Load the v3 prompts at module level so syntax errors in the prompt
# files surface at import time, not deep inside a task run. v3 has three
# prompts: per-voice triage ranking, per-theme editorial flags, and the
# per-(theme, member) formulation. Selection is pure Python — no prompt.
TRIAGE_VOICE_SYSTEM = load_prompt("provocateur_triage_voice")
TRIAGE_FLAGS_SYSTEM = load_prompt("provocateur_triage_flags")
FORMULATION_SYSTEM = load_prompt("provocateur_formulation")


# --- Helpers --------------------------------------------------------------

def _format_member_profiles(members: list[dict]) -> str:
    """Format council member profiles for inclusion in a system prompt.

    Compact format: name bold, each field on its own line with a short
    label. Readable by the model and structured enough that the model
    can reliably reference specific members by name.
    """
    out = []
    for m in members:
        out.append(f"=== {m['name']} ===")
        out.append(f"speaks_from: {m['speaks_from']}")
        out.append(f"core_commitment: {m['core_commitment']}")
        out.append(f"activates_on: {m['activates_on']}")
        out.append(f"goes_flat_on: {m['goes_flat_on']}")
        out.append(f"stretch: {m['stretch']}")
        out.append(f"translation_range: {m['translation_range']}")
        out.append(f"stance_tendency: {m['stance_tendency']}")
        out.append(f"medium: {m['medium']}")
        out.append("")
    return "\n".join(out).rstrip()


_member_slug = member_slug  # canonical implementation lives in flows.shared.io


def _normalize_theme_title(title: str) -> str:
    """Normalize a theme title for cross-night exclusion matching.

    Lowercased + whitespace-collapsed. Theme_ids are not stable across
    Researcher runs (each run generates fresh `theme_001`..`theme_NNN`
    IDs), so the cross-night exclusion filter (C9, spec §"Night 2 is
    different from Night 1") matches by content via normalized title.
    Two prior-night themes with semantically distinct titles count as
    different territory; minor formatting differences don't cause misses.
    """
    if not title:
        return ""
    return re.sub(r"\s+", " ", title.strip().lower())


def load_prior_assignments_by_member(
    prior_run_dirs: list[Path],
) -> dict[str, list[str]]:
    """Load per-member theme titles already assigned in prior nights.

    For the C9 cross-night exclusion filter (spec §"Night 2 is different
    from Night 1"). Each prior run_dir is expected to be the parent of
    `02_researcher/grouping.json` (for theme_id → title resolution) and
    `03_provocateur/selection.json` (for assignments_by_member).

    Returns: { member_name: [normalized_theme_title, ...], ... }

    Member names are taken verbatim from the prior selection — the
    caller is responsible for ensuring the same council membership
    across nights (or accepting that renamed members won't filter).

    On any prior-night load failure (missing files, bad JSON, missing
    fields), raises a SystemExit with a clear message — silent partial
    loading would mean the filter quietly under-applies, which is the
    failure mode operator-side review can't catch.
    """
    out: dict[str, list[str]] = {}
    for run_dir in prior_run_dirs:
        sel_path = run_dir / "03_provocateur" / "selection.json"
        gr_path = run_dir / "02_researcher" / "grouping.json"
        if not sel_path.exists():
            raise SystemExit(
                f"Prior-night selection.json not found: {sel_path}\n"
                f"  --prior-nights expects each path to be a Provocateur "
                f"run_dir (containing 03_provocateur/selection.json)."
            )
        if not gr_path.exists():
            raise SystemExit(
                f"Prior-night grouping.json not found: {gr_path}\n"
                f"  --prior-nights expects 02_researcher/grouping.json next "
                f"to 03_provocateur/selection.json."
            )
        sel = json.loads(sel_path.read_text(encoding="utf-8"))
        gr = json.loads(gr_path.read_text(encoding="utf-8"))
        title_by_id = {
            t["theme_id"]: t.get("title", "")
            for t in gr.get("themes", [])
        }
        assignments = sel.get("assignments_by_member", {})
        for member_name, theme_ids in assignments.items():
            out.setdefault(member_name, [])
            for tid in theme_ids:
                title_norm = _normalize_theme_title(title_by_id.get(tid, ""))
                if title_norm and title_norm not in out[member_name]:
                    out[member_name].append(title_norm)
    return out


def _fill_template(template: str, substitutions: dict[str, str]) -> str:
    """Substitute {{placeholder}} values in a prompt template.

    Simple Python-style safe substitution that won't blow up if a
    placeholder is missing from substitutions — it leaves unknown
    placeholders as-is so the failure is visible in the prompt rather
    than silent. No advanced escape handling; prompts do not contain
    literal {{ or }} in production use.
    """
    filled = template
    for key, value in substitutions.items():
        filled = filled.replace("{{" + key + "}}", value)
    return filled


def _stream_and_parse(
    client: Anthropic,
    system: str,
    user: str,
    max_tokens: int,
    task_label: str,
    logger: Any,
    cache_system: bool = False,
) -> dict:
    """Run a streaming LLM call, collect text, parse JSON defensively.

    Centralizes the three-way failure-mode handling that every Provocateur
    task shares: empty text stream (thinking ate the budget), max_tokens
    stop reason, and JSON parse errors with visible content.

    Raises a descriptive exception on any failure so Prefect retries
    have useful context.

    `cache_system`: when True, wrap the system prompt in a cache_control
    block (5-min ephemeral). C19a: enabled for Formulation calls — each
    voice has 3-5 formulations sharing the same voice-profile-filled
    system prompt, so caching saves ~80% of input cost on reads 2-N.
    NOT enabled for Triage (per-voice ranking has unique system prompt
    per call; triage_flags is a single call) — pure write cost with no
    reads. Min 4096 cached tokens for Opus; voice-profile-filled
    Formulation systems are well above this.
    """
    t0 = time.time()
    chunks = []
    if cache_system:
        system_arg: Any = [
            {
                "type": "text",
                "text": system,
                "cache_control": {"type": "ephemeral"},
            }
        ]
    else:
        system_arg = system
    with client.messages.stream(
        model=CLAUDE_MODEL,
        max_tokens=max_tokens,
        system=system_arg,
        messages=[{"role": "user", "content": user}],
        **_thinking_kwargs(),
    ) as stream:
        for text in stream.text_stream:
            chunks.append(text)
        final = stream.get_final_message()
    full_text = "".join(chunks)
    wall = time.time() - t0

    usage = final.usage
    stop_reason = getattr(final, "stop_reason", "unknown")
    logger.info(
        f"  {task_label} done in {wall:.1f}s "
        f"(in={usage.input_tokens}, out={usage.output_tokens}, "
        f"stop={stop_reason})"
    )

    if usage.output_tokens > max_tokens * 0.8:
        logger.warning(
            f"  {task_label} used {usage.output_tokens}/{max_tokens} "
            f"output tokens (>80%). Consider raising max_tokens."
        )

    if not full_text.strip():
        raise ValueError(
            f"{task_label}: empty text stream from model. "
            f"out_tokens={usage.output_tokens}, stop_reason={stop_reason}. "
            f"Likely cause: adaptive thinking consumed the entire max_tokens "
            f"budget before emitting visible text. Raise max_tokens and retry."
        )

    try:
        return extract_json(full_text)
    except json.JSONDecodeError as e:
        preview = full_text[:500].replace("\n", "\\n")
        raise ValueError(
            f"{task_label}: JSON parse failed. out_tokens={usage.output_tokens}, "
            f"stop_reason={stop_reason}. First 500 chars: {preview}"
        ) from e


# --- Task 1: Triage (v3 — split into Part A per-voice + Part B flags) ----

def _build_model_themes(themes: list[dict]) -> list[dict]:
    """Build the model-facing theme list — abstracts only, no raw extractions.

    Each theme carries its cluster abstracts so the model can see the
    structure of the theme without needing to look at the underlying items.
    Shared by both Triage Part A (per-voice) and Part B (flags).
    """
    out = []
    for t in themes:
        clusters_summary = [
            {
                "cluster_id": c["cluster_id"],
                "cluster_title": c["cluster_title"],
                "cluster_abstract": c["cluster_abstract"],
            }
            for c in t.get("clusters", [])
        ]
        out.append({
            "theme_id": t["theme_id"],
            "title": t.get("title", ""),
            "abstract": t.get("abstract", ""),
            "clusters": clusters_summary,
        })
    return out


@task(
    name="provocateur-triage-voice",
    retries=5,
    retry_delay_seconds=exponential_backoff(backoff_factor=15),
)
def triage_voice(
    voice: dict,
    themes: list[dict],
    council: dict,
    out_dir: Path | None = None,
) -> dict:
    """Node 1A: per-voice ranking. One LLM call per council member.

    The Provocateur reads ALL themes through ONE voice's profile and
    ranks where they have distinctive ground to contribute. Reasoning
    ABOUT the voice using profile data — not speaking AS them. Returns
    ranked_themes + flat_themes for that single voice. Designed to run
    12 in parallel, one per council member.

    If out_dir is provided, the result is also written to disk
    incrementally as `{out_dir}/{voice_slug}.json` so a crash or
    rate-limit failure doesn't lose this voice's work.
    """
    logger = _get_logger()
    client = Anthropic()

    model_themes = _build_model_themes(themes)
    voice_profile_str = _format_member_profiles([voice])

    system = _fill_template(TRIAGE_VOICE_SYSTEM, {
        "voice_profile": voice_profile_str,
        "collective_landscape": council["collective_landscape"],
        "audience": council["audience"],
        "themes_with_clusters": json.dumps(
            {"themes": model_themes}, indent=2, ensure_ascii=False
        ),
    })
    user = (
        f"Rank the day's themes for {voice['name']} per the instructions. "
        f"Return only the JSON object."
    )

    label = f"TriageVoice({voice['name']})"
    result = _stream_and_parse(
        client=client,
        system=system,
        user=user,
        max_tokens=TRIAGE_MAX_TOKENS,
        task_label=label,
        logger=logger,
    )
    # Defensive: ensure voice name is echoed back even if model omitted it
    result.setdefault("voice", voice["name"])
    n_ranked = len(result.get("ranked_themes", []))
    n_flat = len(result.get("flat_themes", []))
    logger.info(f"  {voice['name']}: {n_ranked} ranked, {n_flat} flat")

    # Incremental write: persist this voice's result to disk before
    # returning, so a downstream crash doesn't lose the work
    if out_dir is not None:
        out_dir.mkdir(parents=True, exist_ok=True)
        slug = _member_slug(voice["name"])
        write_json_atomic(out_dir / f"{slug}.json", result)

    return result


@task(
    name="provocateur-triage-flags",
    retries=5,
    retry_delay_seconds=exponential_backoff(backoff_factor=15),
)
def triage_flags(themes: list[dict], council: dict) -> dict:
    """Node 1B: theme-level editorial flags. One LLM call total.

    Tags each theme with worth_surfacing, audience_friction, and
    fault_line_present + fault_line_description. These are theme-level
    properties that need cross-theme + audience perspective, not voice
    perspective. Runs in parallel with the 12 per-voice calls.
    """
    logger = _get_logger()
    client = Anthropic()

    model_themes = _build_model_themes(themes)
    system = _fill_template(TRIAGE_FLAGS_SYSTEM, {
        "collective_landscape": council["collective_landscape"],
        "audience": council["audience"],
        "themes_with_clusters": json.dumps(
            {"themes": model_themes}, indent=2, ensure_ascii=False
        ),
    })
    user = "Tag each theme with the three editorial signals. Return only the JSON object."

    result = _stream_and_parse(
        client=client,
        system=system,
        user=user,
        max_tokens=TRIAGE_MAX_TOKENS,
        task_label="TriageFlags",
        logger=logger,
    )
    n_flags = len(result.get("theme_flags", []))
    n_keep = sum(
        1 for tf in result.get("theme_flags", []) if tf.get("worth_surfacing")
    )
    n_high_friction = sum(
        1 for tf in result.get("theme_flags", [])
        if tf.get("audience_friction") == "high"
    )
    n_fault = sum(
        1 for tf in result.get("theme_flags", []) if tf.get("fault_line_present")
    )
    logger.info(
        f"  flagged {n_flags} themes "
        f"({n_keep} worth surfacing, {n_high_friction} high friction, "
        f"{n_fault} with fault lines)"
    )
    return result


# --- Task 2: Selection (v3 — deterministic Python, no LLM) ---------------

def _activation_to_score(activation: str) -> int:
    """Convert Triage activation label to numeric score for Selection."""
    return {"strong": 3, "moderate": 2}.get(activation, 0)


def python_select(
    triage_voice_results: list[dict],
    triage_flags_result: dict,
    grouping: dict,
    council: dict,
    prior_assignments_by_member: dict[str, list[str]] | None = None,
) -> dict:
    """Node 2: deterministic Python Selection. No LLM call.

    Algorithm (v3, with C9 cross-night exclusion 2026-05-01):
    1. Drop themes Triage Part B vetoed (worth_surfacing=false)
    2. Convert per-voice activations to scores (strong=3, moderate=2)
    3. Compute theme_quality per theme:
         base = sum(scores across all voices)
         theme_quality = base * friction_mult * fault_line_mult
    4. Per-voice candidate list = themes scoring >= activation_threshold,
       sorted by (own_score desc, theme_quality desc), capped at hard_cap.
       **C9 exclusion**: when `prior_assignments_by_member` is supplied
       (Night 2/3 production), themes whose title (normalized) was
       already assigned to that member on a prior night are filtered out
       of the candidate list. Theme_ids are not stable across Researcher
       runs, so the match is by normalized title.
    5. Quorum pass: drop themes with < min_members_per_theme assigned
    6. Cascade: voices whose assignment was dropped pick the next
       candidate from their list. Iterate until stable.
    7. Force-fit min: any voice with 0 assignments gets their highest-
       ranked surviving theme regardless of activation level. **C9:
       force-fit also honors exclusions** — a voice with all candidates
       excluded ends with zero assignments rather than re-deploying
       prior-night territory; recorded in `prior_exclusions_blocked`.
    8. Soft stretch swap: if a voice has zero is_stretch=true assignments
       and at least one stretch theme in their candidates, swap their
       lowest-quality assignment for the highest-scoring stretch theme.
       Stretch swap candidates are also exclusion-filtered.
    9. Output assignments_by_member + kept_themes + dropped_themes +
       diagnostic blocks (forced_fits, stretch_swaps, prior_exclusions).

    All knobs read from council['selection_parameters'].

    Args:
        prior_assignments_by_member: optional dict { member_name: [
            normalized_theme_title, ... ] } from prior nights. When
            provided, candidates whose title matches a prior assignment
            for that member are excluded. Spec §"Night 2 is different
            from Night 1". Helper `load_prior_assignments_by_member`
            builds this from prior-night run_dirs.
    """
    logger = _get_logger()
    params = council.get("selection_parameters", {})
    threshold = params.get("activation_threshold", 2)
    min_per_theme = params.get("min_members_per_theme", 3)
    min_per_voice = params.get("min_formulations_per_voice", 1)
    target_per_voice = params.get("target_formulations_per_voice", 5)
    hard_cap = params.get("hard_cap_per_voice", 5)
    friction_mult = params.get("friction_multiplier",
                               {"low": 1.0, "moderate": 1.3, "high": 1.7})
    fault_mult = params.get("fault_line_multiplier",
                            {"absent": 1.0, "present": 1.5})
    stretch_swap_enabled = params.get("stretch_swap_enabled", True)

    voice_names = [m["name"] for m in council["members"]]
    theme_by_id = {t["theme_id"]: t for t in grouping.get("themes", [])}

    # ---- C9 exclusion setup: build per-member excluded-title sets ----
    # Spec §"Night 2 is different from Night 1": on Night 2/3, exclude
    # (member, theme) pairs that were already assigned on prior nights.
    # Theme_ids are not stable across Researcher runs (each run generates
    # fresh sequential IDs), so the match is by normalized title.
    # Empty dict (default) means Night 1 behavior — no filtering.
    prior_excluded_titles: dict[str, set[str]] = {}
    if prior_assignments_by_member:
        for member_name, titles in prior_assignments_by_member.items():
            prior_excluded_titles[member_name] = set(titles)

    # Build current theme title lookup (normalized) for fast exclusion.
    current_title_by_id: dict[str, str] = {
        tid: _normalize_theme_title(theme_by_id.get(tid, {}).get("title", ""))
        for tid in theme_by_id
    }

    def _is_excluded(voice: str, theme_id: str) -> bool:
        """True if (voice, theme_id) matches a prior-night assignment.

        Uses normalized current title — if the current run has no title
        for this theme_id (mis-shaped grouping), returns False (don't
        accidentally exclude themes we can't identify).
        """
        excluded = prior_excluded_titles.get(voice)
        if not excluded:
            return False
        cur_title = current_title_by_id.get(theme_id, "")
        return bool(cur_title) and cur_title in excluded

    # Track exclusion impacts for diagnostics. Use a set keyed on
    # (voice, theme_id) for dedup — candidates_for() may be called
    # multiple times during the cascade (Step 5-6) and would otherwise
    # double-record. Realized as a list at the end of the algorithm.
    _exclusion_pairs: set[tuple[str, str]] = set()
    prior_exclusions_blocked: list[dict] = []  # voices that hit zero due to filter

    # ---- Step 1: Drop themes Triage vetoed --------------------------
    flags_by_theme = {
        tf["theme_id"]: tf for tf in triage_flags_result.get("theme_flags", [])
    }
    dropped_themes = []
    alive_theme_ids = set()
    for theme_id, tf in flags_by_theme.items():
        if not tf.get("worth_surfacing", True):
            dropped_themes.append({
                "theme_id": theme_id,
                "reason": "worth_surfacing=false",
                "stage": "triage_veto",
            })
        else:
            alive_theme_ids.add(theme_id)
    logger.info(
        f"Selection: {len(alive_theme_ids)} themes pass triage veto "
        f"({len(dropped_themes)} dropped)"
    )

    # ---- Step 2: Score matrix per (voice, theme) --------------------
    # Build per-voice info: scores, stretch flags, ranked order
    voice_scores: dict[str, dict[str, int]] = {v: {} for v in voice_names}
    voice_stretch: dict[str, dict[str, bool]] = {v: {} for v in voice_names}
    voice_rank: dict[str, dict[str, int]] = {v: {} for v in voice_names}
    voice_results_by_name = {
        r.get("voice"): r for r in triage_voice_results
    }
    for v in voice_names:
        vr = voice_results_by_name.get(v, {})
        for rank_i, rt in enumerate(vr.get("ranked_themes", [])):
            tid = rt.get("theme_id")
            if tid not in alive_theme_ids:
                continue
            voice_scores[v][tid] = _activation_to_score(rt.get("activation"))
            voice_stretch[v][tid] = bool(rt.get("is_stretch"))
            voice_rank[v][tid] = rank_i

    # ---- Step 3: Theme quality multipliers ---------------------------
    theme_quality: dict[str, float] = {}
    for tid in alive_theme_ids:
        base = sum(voice_scores[v].get(tid, 0) for v in voice_names)
        tf = flags_by_theme.get(tid, {})
        f_key = tf.get("audience_friction", "low")
        fault_key = "present" if tf.get("fault_line_present") else "absent"
        theme_quality[tid] = (
            base
            * friction_mult.get(f_key, 1.0)
            * fault_mult.get(fault_key, 1.0)
        )

    # ---- Step 4: Per-voice candidate lists, capped at hard_cap ------
    def candidates_for(voice: str) -> list[str]:
        """Themes this voice scores >= threshold on, sorted by
        (own_score desc, theme_quality desc, theme_id stable).

        C9: prior-night assignments for this voice (matched by normalized
        title) are excluded from the candidate pool. Each excluded
        theme is recorded in `prior_exclusions_applied` for diagnostics.
        """
        cands = []
        for tid in alive_theme_ids:
            if voice_scores[voice].get(tid, 0) < threshold:
                continue
            if _is_excluded(voice, tid):
                _exclusion_pairs.add((voice, tid))
                continue
            cands.append(tid)
        cands.sort(
            key=lambda tid: (
                -voice_scores[voice].get(tid, 0),
                -theme_quality.get(tid, 0.0),
                tid,
            )
        )
        return cands

    assignments: dict[str, list[str]] = {
        v: candidates_for(v)[:hard_cap] for v in voice_names
    }

    # ---- Steps 5-6: Quorum + cascade ---------------------------------
    def themes_with_quorum() -> set[str]:
        return {
            tid for tid in alive_theme_ids
            if sum(1 for v in voice_names if tid in assignments[v]) >= min_per_theme
        }

    for _iteration in range(10):
        keep = themes_with_quorum()
        dropped_for_quorum = [
            tid for tid in alive_theme_ids if tid not in keep
        ]
        if not dropped_for_quorum:
            break
        # Remove sub-quorum themes from all voice assignments, then
        # backfill from their sorted candidate lists (next picks)
        for v in voice_names:
            kept = [tid for tid in assignments[v] if tid in keep]
            cands = [tid for tid in candidates_for(v) if tid in keep]
            for c in cands:
                if len(kept) >= hard_cap:
                    break
                if c not in kept:
                    kept.append(c)
            assignments[v] = kept[:hard_cap]
        # Recheck — if still sub-quorum themes exist, iterate
    keep = themes_with_quorum()
    for tid in alive_theme_ids - keep:
        dropped_themes.append({
            "theme_id": tid,
            "reason": f"below quorum (min {min_per_theme} voices required)",
            "stage": "quorum",
        })
    # Final assignment cleanup: only keep assignments to surviving themes
    for v in voice_names:
        assignments[v] = [tid for tid in assignments[v] if tid in keep]

    # ---- Step 7: Force-fit minimum -----------------------------------
    # C9: force-fit picks must also honor exclusions. A voice with all
    # candidates filtered ends with zero rather than re-deploying
    # prior-night territory.
    forced_fits: list[dict] = []
    for v in voice_names:
        if len(assignments[v]) >= min_per_voice:
            continue
        vr = voice_results_by_name.get(v, {})
        # Highest-ranked surviving theme that ALSO isn't excluded
        surviving_ranked = [
            rt["theme_id"] for rt in vr.get("ranked_themes", [])
            if rt["theme_id"] in keep
            and not _is_excluded(v, rt["theme_id"])
        ]
        if not surviving_ranked:
            # Try flat themes as last resort, also exclusion-filtered
            surviving_flat = [
                ft["theme_id"] for ft in vr.get("flat_themes", [])
                if ft["theme_id"] in keep
                and not _is_excluded(v, ft["theme_id"])
            ]
            if surviving_flat:
                pick = surviving_flat[0]
                assignments[v].append(pick)
                forced_fits.append({"voice": v, "theme_id": pick, "from": "flat"})
            else:
                # Voice has zero non-excluded themes — record as
                # blocked-by-prior-exclusions for operator visibility.
                # Better to ship voice-with-zero than re-deploy already-
                # covered territory.
                if prior_excluded_titles.get(v):
                    prior_exclusions_blocked.append({
                        "voice": v,
                        "reason": (
                            "all surviving themes for this voice (ranked + flat) "
                            "match prior-night assignments; voice ends with zero "
                            "assignments rather than re-deploying covered territory"
                        ),
                    })
        else:
            pick = surviving_ranked[0]
            if pick not in assignments[v]:
                assignments[v].append(pick)
                forced_fits.append({"voice": v, "theme_id": pick, "from": "ranked"})

    # ---- Step 8: Soft stretch swap -----------------------------------
    stretch_swaps: list[dict] = []
    if stretch_swap_enabled:
        for v in voice_names:
            current = assignments[v]
            has_stretch = any(voice_stretch[v].get(tid) for tid in current)
            if has_stretch or len(current) == 0:
                continue
            # Find best stretch theme in their candidates that survives
            stretch_cands = [
                tid for tid in candidates_for(v)
                if tid in keep
                and voice_stretch[v].get(tid)
                and tid not in current
            ]
            if not stretch_cands:
                continue
            # Swap the lowest-quality (last) current assignment for the
            # best stretch theme, but only if doing so doesn't break
            # quorum on the swapped-out theme
            swap_in = stretch_cands[0]
            swap_out = current[-1]
            # Check quorum impact: swapping out would leave swap_out with
            # one fewer assigned voice; check if that's still >= min_per_theme
            other_voices_on_out = sum(
                1 for vv in voice_names
                if vv != v and swap_out in assignments[vv]
            )
            if other_voices_on_out >= min_per_theme:
                # Safe to swap
                assignments[v] = current[:-1] + [swap_in]
                stretch_swaps.append({
                    "voice": v,
                    "swapped_in": swap_in,
                    "swapped_out": swap_out,
                })

    # ---- Step 9: Build output ----------------------------------------
    # kept_themes ordered by quality desc
    kept_sorted = sorted(
        keep,
        key=lambda tid: -theme_quality.get(tid, 0.0),
    )
    kept_themes_view = []
    for tid in kept_sorted:
        assigned_voices = [v for v in voice_names if tid in assignments[v]]
        kept_themes_view.append({
            "theme_id": tid,
            "title": theme_by_id.get(tid, {}).get("title", ""),
            "theme_quality": round(theme_quality.get(tid, 0.0), 2),
            "assigned_voices": assigned_voices,
            "audience_friction": flags_by_theme.get(tid, {}).get("audience_friction"),
            "fault_line_present": flags_by_theme.get(tid, {}).get("fault_line_present"),
        })

    coverage = {v: len(assignments[v]) for v in voice_names}
    total_pairs = sum(coverage.values())
    logger.info(
        f"  selected {len(keep)} themes, dropped {len(dropped_themes)}, "
        f"{total_pairs} formulation pairs across {len(voice_names)} voices"
    )
    logger.info(f"  coverage: {coverage}")
    if forced_fits:
        logger.info(f"  force-fit: {len(forced_fits)} voices needed minimum-1 backfill")
    if stretch_swaps:
        logger.info(f"  stretch swaps: {len(stretch_swaps)}")

    # Soft target check: warn (but do not fail) for any voice that ended
    # below target_formulations_per_voice. The algorithm already enforces
    # min (via force-fit) and respects hard_cap (via candidate truncation);
    # the target is a desired sweet spot. Voices below target are usually
    # narrow-territory voices honestly served — visibility helps tuning.
    below_target = [
        {"voice": v, "got": coverage[v], "target": target_per_voice}
        for v in voice_names
        if coverage[v] < target_per_voice
    ]
    if below_target:
        names = ", ".join(f"{b['voice']} ({b['got']}/{b['target']})" for b in below_target)
        logger.warning(
            f"  below target ({target_per_voice}): {len(below_target)} voices — {names}"
        )

    # C9 exclusion diagnostics (always emitted; empty when no prior nights).
    # Materialize the deduped exclusion set into a sorted list with full
    # context (voice, theme_id, title) for operator visibility.
    prior_exclusions_applied = sorted(
        [
            {
                "voice": v,
                "theme_id": tid,
                "title": theme_by_id.get(tid, {}).get("title", ""),
            }
            for (v, tid) in _exclusion_pairs
        ],
        key=lambda d: (d["voice"], d["theme_id"]),
    )
    if prior_exclusions_applied:
        logger.info(
            f"  prior-night exclusions applied: {len(prior_exclusions_applied)} "
            f"(voice, theme) pairs filtered from candidate lists"
        )
    if prior_exclusions_blocked:
        logger.warning(
            f"  prior-night exclusions BLOCKED {len(prior_exclusions_blocked)} "
            f"voice(s) from any assignment — operator review recommended"
        )

    return {
        "assignments_by_member": assignments,
        "kept_themes": kept_themes_view,
        "dropped_themes": dropped_themes,
        "coverage_per_member": coverage,
        "forced_fits": forced_fits,
        "stretch_swaps": stretch_swaps,
        "below_target": below_target,
        "prior_exclusions_applied": prior_exclusions_applied,
        "prior_exclusions_blocked": prior_exclusions_blocked,
        "prior_nights_consumed": (
            len(prior_assignments_by_member or {})
        ),
        "selection_parameters_used": {
            "activation_threshold": threshold,
            "min_members_per_theme": min_per_theme,
            "min_formulations_per_voice": min_per_voice,
            "target_formulations_per_voice": target_per_voice,
            "hard_cap_per_voice": hard_cap,
            "friction_multiplier": friction_mult,
            "fault_line_multiplier": fault_mult,
            "stretch_swap_enabled": stretch_swap_enabled,
        },
    }


# --- Task 3: Formulation --------------------------------------------------

def _build_theme_material(theme: dict, all_extractions_by_id: dict, logger) -> dict:
    """Build the full theme_material view for a Formulation call.

    Shared between the per-(theme, member) calls that formulate on this
    theme — the theme material itself is identical across members, only
    the member profile and prompt framing change.
    """
    theme_material = {
        "theme_id": theme["theme_id"],
        "title": theme.get("title", ""),
        "abstract": theme.get("abstract", ""),
        "clusters": [],
    }
    for c in theme.get("clusters", []):
        cluster_view = {
            "cluster_id": c["cluster_id"],
            "cluster_title": c["cluster_title"],
            "cluster_abstract": c["cluster_abstract"],
            "extractions": [],
        }
        for eid in c.get("extraction_ids", []):
            ex = all_extractions_by_id.get(eid)
            if ex is None:
                logger.warning(f"  missing extraction {eid} in {theme['theme_id']}")
                continue
            cluster_view["extractions"].append({
                "id": ex["id"],
                "speaker": ex.get("speaker"),
                "lens": ex.get("lens"),
                "extraction": ex["extraction"],
                "context": ex.get("context", "") or "",
                "engagement": ex.get("engagement"),
                "responds_to": ex.get("responds_to"),
                "energy": ex.get("energy"),
            })
        theme_material["clusters"].append(cluster_view)
    return theme_material


@task(
    name="provocateur-formulate",
    retries=5,
    retry_delay_seconds=exponential_backoff(backoff_factor=15),
)
def formulate_for_member(
    theme: dict,
    member_name: str,
    all_extractions_by_id: dict,
    council: dict,
    theme_flags: dict | None = None,
    out_dir: Path | None = None,
) -> dict:
    """Node 3: write ONE formulation aimed at ONE member for ONE theme.

    Runs once per (theme, member) pair. Each call sees the same theme
    material but loads that single member's profile into the prompt, so
    the formulation is aimed specifically at their activation territory.

    v3 additions:
    - Receives theme_flags (friction + fault_line description) so the
      Formulation can angle toward the editorial signals Triage Part B
      identified.
    - Output includes narrative-briefing components: theme_display_title,
      context_narrative, selected_quotes (with strict-flavor rules),
      grounding_extraction_ids, rationale.
    - If out_dir is provided, the result is also written to disk
      incrementally as `{out_dir}/{theme_id}__{member_slug}.json` so a
      crash or rate-limit failure doesn't lose completed pairs.
    """
    logger = _get_logger()
    client = Anthropic()

    member = get_member_by_name(council, member_name)
    theme_material = _build_theme_material(theme, all_extractions_by_id, logger)
    member_profile_str = _format_member_profiles([member])

    # Theme flags come from Triage Part B. If absent, default to neutral.
    flags = theme_flags or {}
    friction_level = flags.get("audience_friction", "moderate")
    fault_desc = flags.get("fault_line_description") or "no specific fault line identified"

    system = _fill_template(FORMULATION_SYSTEM, {
        "collective_landscape": council["collective_landscape"],
        "member_profile": member_profile_str,
        "audience": council["audience"],
        "theme_friction_level": friction_level,
        "theme_fault_line_description_or_none": fault_desc,
        "theme_material": json.dumps(theme_material, indent=2, ensure_ascii=False),
    })

    user = (
        f"Write one formulation for theme {theme['theme_id']} aimed "
        f"specifically at {member_name}, plus the narrative-briefing "
        f"components per the instructions. Apply the proposition test "
        f"strictly. Apply the strict-flavor rules to selected_quotes."
    )

    label = f"Formulation({theme['theme_id']},{member_name})"
    logger.info(f"{label} start")
    result = _stream_and_parse(
        client=client,
        system=system,
        user=user,
        max_tokens=FORMULATION_MAX_TOKENS,
        task_label=label,
        logger=logger,
        cache_system=True,  # C19a: voice's 3-5 formulations share system prompt
    )
    # Defensive: ensure member + theme_id echoed back even if model omitted them
    result.setdefault("member", member_name)
    result.setdefault("theme_id", theme["theme_id"])

    # Incremental write: persist this (theme, member) result to disk before
    # returning, so a downstream crash or rate-limit failure doesn't lose
    # the completed work
    if out_dir is not None:
        out_dir.mkdir(parents=True, exist_ok=True)
        slug = _member_slug(member_name)
        write_json_atomic(out_dir / f"{theme['theme_id']}__{slug}.json", result)

    return result


# --- Task 4: Packaging ----------------------------------------------------

# Lens ordering for extractions within a cluster in the final briefings.
# Matches the v2.4 Researcher output format — note the underscore in
# `open_question`, NOT a space. Silent mis-sort if this is wrong.
LENS_ORDER = {"assertion": 0, "reframing": 1, "open_question": 2}


def _render_narrative_briefing(formulation: dict, theme_display_title: str) -> str:
    """Render a Formulation's narrative-briefing components into the
    markdown that the Voice Node Step 1 prompt will receive.

    Format: THEME / CONTEXT / EXTRACTION / FORMULATION sections, with
    a final hint at the structured field for deeper inspection. Matches
    the format validated in trial runs.

    Voice Pipeline Step 1 contract (Voice Pipeline v2 2026-04-28): the
    FORMULATION header must surface the `mode` label so the voice's
    closing instruction can branch on question vs proposition without
    the voice having to infer mode from grammar. The mode is also
    available structurally on the briefing entry; surfacing it inline
    here makes the user prompt self-contained.
    """
    mode = formulation.get("mode", "question")
    lines = []
    lines.append(f"THEME: {theme_display_title}")
    lines.append("")
    lines.append("CONTEXT FROM TODAY'S SESSIONS:")
    lines.append(formulation.get("context_narrative", "").strip() or "(no context narrative provided)")
    lines.append("")
    lines.append("EXTRACTION — positions heard today:")
    quotes = formulation.get("selected_quotes", []) or []
    if not quotes:
        lines.append("(no quotes selected)")
    for q in quotes:
        quote_text = (q.get("quote") or "").strip()
        attr = q.get("attribution", "") or ""
        flavor = q.get("flavor")
        attribution_str = attr
        if flavor:
            attribution_str = f"{attr}, {flavor}"
        lines.append(f'• "{quote_text}" ({attribution_str})')
    lines.append("")
    lines.append(f"FORMULATION (mode: {mode}):")
    lines.append((formulation.get("formulation") or "").strip())
    lines.append("")
    lines.append(
        "[Full structured supporting material — theme abstract, cluster "
        "abstracts, all raw extractions sorted by lens, theme flags — is "
        "available in the `full_theme_record` field of this briefing entry "
        "for deeper inspection.]"
    )
    return "\n".join(lines)


@task(name="provocateur-package")
def package_voice_briefings(
    selection: dict,
    formulations: list[dict],
    grouping: dict,
    all_extractions_by_id: dict,
    council: dict,
    out_dir: Path,
) -> dict:
    """Node 4: assemble per-voice briefing packages. No LLM call.

    v3 reads `selection.assignments_by_member` (per-voice dict) and the
    per-(theme, member) formulations list. For each council member,
    bundles all their formulations into a single briefing JSON file.

    Each formulation in a briefing has TWO views, each with a clear purpose:

      - `narrative_briefing`: the markdown PROMPT for Voice Node Step 1
        (paste-and-go). Contains the formulation, context_narrative, and
        selected_quotes — the Provocateur's curated framing of what to think
        about. This is the briefing the voice receives.

      - `full_theme_record`: the wider REASONING SURFACE for Step 1 thinking.
        The voice's private deliberation should range over the full record
        of what was said on this theme — clusters with all extractions
        sorted by lens, the Researcher's theme title and abstract, who else
        is responding to this theme, and the editorial flags. The voice
        reasons over this whole record while answering the curated prompt.

    Intentionally NOT in the briefing:
      - The voice's own profile (the voice agent IS the persona, loaded
        from its v3.7 Persona Card system prompt).
      - council_config_version (lives in manifest, not duplicated 12×).
      - formulations_count (derive from len(formulations)).
      - Provocateur's `rationale` field (would prime the voice toward the
        Provocateur's expected answer — kept in per-pair checkpoint for audit).

    Writes one JSON file per council member to out_dir (even members
    with zero formulations get a file, to make the "who got nothing"
    case visible rather than silent).
    """
    logger = _get_logger()
    out_dir.mkdir(parents=True, exist_ok=True)

    theme_by_id = {t["theme_id"]: t for t in grouping.get("themes", [])}

    # Index formulations by (theme_id, member) pair for fast lookup
    formulation_by_pair = {
        (f["theme_id"], f["member"]): f for f in formulations
    }

    # Index theme flags by theme_id for the structured view
    flags_by_theme = {
        kt["theme_id"]: kt for kt in selection.get("kept_themes", [])
    }

    assignments_by_member = selection.get("assignments_by_member", {})

    summary = {
        "members": {},
        "total_briefings_written": 0,
    }

    for member in council["members"]:
        name = member["name"]
        slug = _member_slug(name)

        my_theme_ids = assignments_by_member.get(name, [])
        my_formulations = []
        for theme_id in my_theme_ids:
            formulation = formulation_by_pair.get((theme_id, name))
            if formulation is None:
                logger.warning(
                    f"  {name}: no formulation found for assigned "
                    f"({theme_id}, {name}) pair — skipping"
                )
                continue

            theme = theme_by_id.get(theme_id, {})
            theme_display_title = (
                formulation.get("theme_display_title")
                or theme.get("title", "")
                or theme_id
            )

            # Build the supporting material: each cluster with its
            # abstract and raw extractions, extractions sorted by lens
            clusters_view = []
            for c in theme.get("clusters", []):
                extractions_view = []
                for eid in c.get("extraction_ids", []):
                    ex = all_extractions_by_id.get(eid)
                    if ex is None:
                        continue
                    extractions_view.append({
                        "id": ex["id"],
                        "speaker": ex.get("speaker"),
                        "lens": ex.get("lens"),
                        "extraction": ex["extraction"],
                        "context": ex.get("context", "") or "",
                        "engagement": ex.get("engagement"),
                        "responds_to": ex.get("responds_to"),
                        "energy": ex.get("energy"),
                    })
                extractions_view.sort(
                    key=lambda e: (LENS_ORDER.get(e.get("lens", ""), 99), e["id"])
                )
                clusters_view.append({
                    "cluster_id": c["cluster_id"],
                    "cluster_title": c["cluster_title"],
                    "cluster_abstract": c["cluster_abstract"],
                    "extractions": extractions_view,
                })

            # Other voices on this same theme — useful context
            co_assigned = [
                v for v, themes in assignments_by_member.items()
                if theme_id in themes and v != name
            ]

            # Theme flags (for the structured view)
            theme_meta = flags_by_theme.get(theme_id, {})

            narrative = _render_narrative_briefing(formulation, theme_display_title)

            # Briefing entry: TWO complementary views.
            #
            # `narrative_briefing` is the markdown PROMPT for Voice Node Step 1
            # (paste-and-go). It contains the formulation, context_narrative,
            # and selected_quotes — the Provocateur's curated framing of what
            # to think about.
            #
            # `full_theme_record` is the wider REASONING SURFACE for Step 1.
            # The voice's private thinking should range over the full record
            # of what was said on this theme, not just what the Provocateur
            # highlighted — clusters with all extractions sorted by lens, the
            # Researcher's own theme title and abstract, who else is responding
            # to this theme, and the editorial flags. A voice with the full
            # picture might notice positions the curated quotes left out, see
            # counter-currents the Provocateur didn't surface, or confirm the
            # framing was right and stay close to it. All good Step 1 moves.
            #
            # INTENTIONALLY NOT in the briefing:
            #   - Voice profile: the voice agent IS the persona (loaded from
            #     v3.7 Persona Card system prompt).
            #   - council_config_version: lives in manifest, not duplicated.
            #   - formulations_count: derive from len().
            #   - Provocateur's `rationale` field: would prime the voice
            #     toward the Provocateur's expected answer. Kept in per-pair
            #     checkpoint (formulations/{theme_id}__{slug}.json) for audit.
            # Voice Pipeline v2 contract (2026-04-28): briefing entry exposes
            # the structured formulation fields alongside the rendered markdown,
            # so Voice Pipeline Step 1's output lineage block can echo
            # `formulation_text` and access `selected_quotes` without parsing
            # the markdown. Provocateur's `rationale` is still excluded
            # (would prime the voice — kept in per-pair file for audit).
            my_formulations.append({
                "theme_id": theme_id,
                "theme_display_title": theme_display_title,
                "mode": formulation.get("mode", "question"),
                "formulation_text": (formulation.get("formulation") or "").strip(),
                "context_narrative": (formulation.get("context_narrative") or "").strip(),
                "selected_quotes": formulation.get("selected_quotes", []) or [],
                "narrative_briefing": narrative,
                "full_theme_record": {
                    "clusters": clusters_view,
                    "theme_title_from_researcher": theme.get("title", ""),
                    "theme_abstract_from_researcher": theme.get("abstract", ""),
                    "co_assigned_voices": co_assigned,
                    "theme_flags": {
                        "audience_friction": theme_meta.get("audience_friction"),
                        "fault_line_present": theme_meta.get("fault_line_present"),
                        "theme_quality": theme_meta.get("theme_quality"),
                    },
                    "grounding_extraction_ids": formulation.get("grounding_extraction_ids", []),
                },
            })

        # Briefing top-level: just the formulations array. The voice agent IS
        # the persona (loaded from the v3.7 Persona Card as its system prompt),
        # so the council_config stub profile is not re-shipped here. Run-level
        # metadata (council_config_version, formulations_count) lives in the
        # manifest, not duplicated 12× across briefings.
        briefing = {
            "formulations": my_formulations,
        }

        briefing_path = out_dir / f"{slug}.json"
        write_json_atomic(briefing_path, briefing)

        summary["members"][name] = {
            "slug": slug,
            "formulations_count": len(my_formulations),
            "path": str(briefing_path.relative_to(out_dir.parent.parent)),
        }
        summary["total_briefings_written"] += 1
        logger.info(f"  {name}: {len(my_formulations)} formulation(s) → {slug}.json")

    return summary


# --- Flow orchestrator ----------------------------------------------------

@flow(name="provocateur-pipeline")
def run_provocateur(
    run_root: str | Path,
    prior_run_dirs: list[str | Path] | None = None,
) -> dict:
    """Run the v3 Provocateur pipeline end-to-end against a run directory.

    v3 architecture:
    - Triage Part A: 12 parallel LLM calls (per voice ranking) with
      per-voice incremental write checkpointing
    - Triage Part B: 1 LLM call in parallel (theme editorial flags),
      cached at triage_flags.json
    - Selection: pure Python, deterministic algorithm (always recomputed,
      never cached — instant + sensitive to council_config edits)
    - Formulation: N parallel LLM calls (one per (theme, voice) pair)
      with per-pair incremental write checkpointing, batched to respect
      Anthropic rate limits
    - Packaging: pure Python, per-voice briefing files

    Expects the Researcher to have already written:
        {run_root}/02_researcher/all_extractions.json
        {run_root}/02_researcher/grouping.json

    Writes:
        {run_root}/03_provocateur/triage_voices/{slug}.json   (per voice)
        {run_root}/03_provocateur/triage_flags.json
        {run_root}/03_provocateur/selection.json
        {run_root}/03_provocateur/formulations/{theme_id}__{slug}.json  (per pair)
        {run_root}/03_provocateur/briefings/{slug}.json       (per voice)
        {run_root}/03_provocateur/manifest.json

    Resume behavior: re-running picks up from per-voice and per-pair
    checkpoints automatically. No PROVOCATEUR_CACHE flag needed — the
    checkpoints ARE the cache. To force a clean run, delete the relevant
    checkpoint files or directories.
    """
    logger = _get_logger()
    run_root = Path(run_root)

    researcher_dir = run_root / "02_researcher"
    out_dir = run_root / "03_provocateur"
    briefings_dir = out_dir / "briefings"
    out_dir.mkdir(parents=True, exist_ok=True)

    # Load Researcher output
    logger.info(f"Loading Researcher output from {researcher_dir}")
    grouping = json.loads((researcher_dir / "grouping.json").read_text(encoding="utf-8"))
    all_extractions = json.loads((researcher_dir / "all_extractions.json").read_text(encoding="utf-8"))
    all_extractions_by_id = {e["id"]: e for e in all_extractions}
    logger.info(
        f"  {len(all_extractions)} extractions, "
        f"{len(grouping.get('themes', []))} themes, "
        f"{sum(len(t.get('clusters', [])) for t in grouping.get('themes', []))} clusters"
    )

    # Load council config
    council = load_council_config()
    logger.info(
        f"Council config: version={council['version']}, "
        f"{len(council['members'])} members"
    )

    themes = grouping.get("themes", [])

    # ---- Stage 1: Triage (Part A per-voice + Part B flags, all parallel) ----
    # Per-voice incremental write checkpointing: each voice's result writes
    # to triage_voices/{voice_slug}.json before the task returns. On startup,
    # already-completed voices are skipped — no PROVOCATEUR_CACHE flag
    # needed, the per-voice files ARE the cache. Triage Flags is a single
    # LLM call with no intermediate state — its triage_flags.json file is
    # the only checkpoint.
    triage_voices_dir = out_dir / "triage_voices"
    triage_voices_dir.mkdir(parents=True, exist_ok=True)
    triage_flags_path = out_dir / "triage_flags.json"

    # Scan per-voice checkpoints; identify which voices need to run
    already_done: dict[str, dict] = {}
    to_run: list[dict] = []
    for v in council["members"]:
        ckpt = triage_voices_dir / f"{_member_slug(v['name'])}.json"
        if ckpt.exists():
            try:
                already_done[v["name"]] = json.loads(ckpt.read_text(encoding="utf-8"))
            except Exception as e:
                logger.warning(f"  failed to load {ckpt}: {e}, re-running")
                to_run.append(v)
        else:
            to_run.append(v)

    flags_already_cached = triage_flags_path.exists()
    if flags_already_cached:
        try:
            triage_flags_result = json.loads(triage_flags_path.read_text(encoding="utf-8"))
        except Exception as e:
            logger.warning(f"  failed to load {triage_flags_path}: {e}, re-running")
            flags_already_cached = False

    n_done = len(already_done)
    n_voices_to_run = len(to_run)
    n_flags_to_run = 0 if flags_already_cached else 1
    logger.info(
        f"Triage: {n_done}/{len(council['members'])} voices already on disk, "
        f"{n_voices_to_run} voices + {n_flags_to_run} flags pass to run"
    )

    # Submit only what's missing
    voice_futures = [
        triage_voice.submit(
            voice=v,
            themes=themes,
            council=council,
            out_dir=triage_voices_dir,
        )
        for v in to_run
    ]
    flags_future = (
        triage_flags.submit(themes=themes, council=council)
        if not flags_already_cached
        else None
    )

    # Wait on results, assemble in council member order
    fresh_voice_results = [f.result() for f in voice_futures]
    fresh_voice_by_name = {r["voice"]: r for r in fresh_voice_results}
    triage_voice_results = [
        already_done.get(v["name"]) or fresh_voice_by_name[v["name"]]
        for v in council["members"]
    ]

    if flags_future is not None:
        triage_flags_result = flags_future.result()
        write_json_atomic(triage_flags_path, triage_flags_result)
        logger.info(f"  wrote {triage_flags_path}")

    # ---- Stage 2: Selection (pure Python, deterministic) ----
    # Always recompute. Selection is instant and re-runs cheaply against
    # whatever Triage data is currently on disk + whatever editorial knobs
    # are currently in council_config.json. Caching it would silently use
    # stale assignments when someone changes selection_parameters.
    #
    # C9 cross-night exclusion: if prior_run_dirs is supplied (Night 2/3),
    # load (member, theme_title) assignments from each prior night's
    # selection.json + grouping.json and pass into Selection. The filter
    # uses normalized titles since theme_ids are not stable across runs.
    prior_assignments: dict[str, list[str]] = {}
    if prior_run_dirs:
        prior_paths = [Path(p) for p in prior_run_dirs]
        logger.info(
            f"  Loading prior-night assignments from {len(prior_paths)} "
            f"run_dir(s) for C9 exclusion filter"
        )
        prior_assignments = load_prior_assignments_by_member(prior_paths)
        n_pairs = sum(len(v) for v in prior_assignments.values())
        logger.info(
            f"    {n_pairs} (member, theme) pair(s) carried forward "
            f"across {len(prior_assignments)} member(s)"
        )

    selection_path = out_dir / "selection.json"
    selection_result = python_select(
        triage_voice_results=triage_voice_results,
        triage_flags_result=triage_flags_result,
        grouping=grouping,
        council=council,
        prior_assignments_by_member=prior_assignments,
    )
    write_json_atomic(selection_path, selection_result)
    logger.info(f"  wrote {selection_path}")

    # ---- Stage 3: Formulation (N parallel LLM calls, one per pair) ----
    theme_by_id = {t["theme_id"]: t for t in themes}
    flags_by_theme = {
        tf["theme_id"]: tf for tf in triage_flags_result.get("theme_flags", [])
    }
    assignments_by_member = selection_result.get("assignments_by_member", {})

    # Per-pair checkpoint directory. Each completed (theme, voice) pair
    # writes its result to formulations/{theme_id}__{voice_slug}.json
    # before returning, so a crash mid-Formulation doesn't lose work.
    formulations_dir = out_dir / "formulations"
    formulations_dir.mkdir(parents=True, exist_ok=True)

    # Build the full pair list for parallel submission, splitting into
    # already-done (loaded from disk) and to-run (need LLM call).
    already_done_formulations: list[dict] = []
    pairs: list[tuple[dict, str, dict | None]] = []
    for member_name, theme_ids in assignments_by_member.items():
        for theme_id in theme_ids:
            theme = theme_by_id.get(theme_id)
            if theme is None:
                logger.warning(
                    f"  Selection references unknown theme_id {theme_id}, skipping"
                )
                continue
            ckpt = formulations_dir / f"{theme_id}__{_member_slug(member_name)}.json"
            if ckpt.exists():
                try:
                    already_done_formulations.append(
                        json.loads(ckpt.read_text(encoding="utf-8"))
                    )
                    continue
                except Exception as e:
                    logger.warning(f"  failed to load {ckpt}: {e}, re-running")
            pairs.append((theme, member_name, flags_by_theme.get(theme_id)))

    total_pairs = len(pairs)
    total_overall = total_pairs + len(already_done_formulations)
    # Batch the parallel submissions to stay within Anthropic's rate limits.
    # Opus 4.7 is rate-limited at 8K output tokens/min and each Formulation
    # call produces ~3K output, so 4 concurrent calls per minute is the
    # sustainable steady-state. Configurable via env vars for tuning.
    batch_size = int(os.environ.get("PROVOCATEUR_FORMULATION_BATCH", "4"))
    batch_wait_s = int(os.environ.get("PROVOCATEUR_BATCH_WAIT_S", "20"))
    n_batches = (total_pairs + batch_size - 1) // batch_size if total_pairs else 0
    if already_done_formulations:
        logger.info(
            f"Formulation: {len(already_done_formulations)} pairs already "
            f"checkpointed, {total_pairs} still to run in {n_batches} batches "
            f"of {batch_size} (wait {batch_wait_s}s between batches)"
        )
    else:
        logger.info(
            f"Formulation: {total_pairs} pairs in {n_batches} batches of "
            f"{batch_size} (wait {batch_wait_s}s between batches)"
        )

    fresh_formulations: list[dict] = []
    for batch_i in range(0, total_pairs, batch_size):
        batch = pairs[batch_i:batch_i + batch_size]
        batch_num = batch_i // batch_size + 1
        logger.info(
            f"  Batch {batch_num}/{n_batches}: submitting {len(batch)} parallel calls"
        )
        batch_futures = [
            formulate_for_member.submit(
                theme=theme,
                member_name=member_name,
                all_extractions_by_id=all_extractions_by_id,
                council=council,
                theme_flags=tf,
                out_dir=formulations_dir,
            )
            for (theme, member_name, tf) in batch
        ]
        batch_results = [f.result() for f in batch_futures]
        fresh_formulations.extend(batch_results)
        done_so_far = len(already_done_formulations) + len(fresh_formulations)
        logger.info(
            f"  Batch {batch_num}/{n_batches}: complete "
            f"({done_so_far}/{total_overall} formulations done)"
        )
        # Sleep between batches to let the rate limit window breathe,
        # except after the last batch (no point waiting after the work is done)
        if batch_i + batch_size < total_pairs:
            logger.info(f"  waiting {batch_wait_s}s for rate limit window to clear")
            time.sleep(batch_wait_s)

    # Combine already-done (from disk) with freshly-computed formulations.
    # No consolidated formulations.json is written — the per-pair files in
    # formulations/ ARE the source of truth. A consolidated file would risk
    # silent drift if anyone hand-edits a per-pair file. To get a flat view
    # for analysis: cat formulations/*.json | jq -s '{formulations: .}'
    formulations = already_done_formulations + fresh_formulations
    logger.info(
        f"  Formulation complete: {len(formulations)} pairs in "
        f"formulations/ (per-pair source of truth)"
    )

    # ---- Stage 4: Packaging (pure Python) ----
    packaging_summary = package_voice_briefings(
        selection=selection_result,
        formulations=formulations,
        grouping=grouping,
        all_extractions_by_id=all_extractions_by_id,
        council=council,
        out_dir=briefings_dir,
    )

    # ---- Manifest ----
    n_kept = len(selection_result.get("kept_themes", []))
    n_dropped = len(selection_result.get("dropped_themes", []))
    coverage = selection_result.get("coverage_per_member", {})

    manifest = {
        "pipeline": "provocateur",
        "pipeline_version": "v3",
        "council_config_version": council["version"],
        "council_members_count": len(council["members"]),
        "model": CLAUDE_MODEL,
        "thinking_enabled": PROVOCATEUR_THINKING,
        "inputs": {
            "extractions": len(all_extractions),
            "themes": len(themes),
            "clusters": sum(len(t.get("clusters", [])) for t in themes),
        },
        "outputs": {
            "triage_voices": len(triage_voice_results),
            "triage_flags": len(triage_flags_result.get("theme_flags", [])),
            "selected_themes": n_kept,
            "dropped_themes": n_dropped,
            "formulations": len(formulations),
            "briefings_written": packaging_summary["total_briefings_written"],
            "coverage_per_member": coverage,
            "forced_fits": len(selection_result.get("forced_fits", [])),
            "stretch_swaps": len(selection_result.get("stretch_swaps", [])),
            "voices_below_target": len(selection_result.get("below_target", [])),
        },
        "selection_parameters_used": selection_result.get("selection_parameters_used", {}),
    }
    write_json_atomic(out_dir / "manifest.json", manifest)

    logger.info("Provocateur v3 pipeline complete.")
    logger.info(f"  manifest: {out_dir / 'manifest.json'}")
    return manifest


# --- CLI -----------------------------------------------------------------

def _parse_args(argv: list[str]) -> tuple[Path, list[Path]]:
    """Parse argv into (run_root, prior_run_dirs).

    Supported forms:
        python flows/provocateur_flow.py <run_root>
        python flows/provocateur_flow.py <run_root> --prior-nights <run_dir>[,<run_dir>...]

    --prior-nights is a comma-separated list of prior-night run_dir paths
    (the parent directories of 02_researcher/ + 03_provocateur/). Used
    on Night 2/3 to apply the C9 exclusion filter — (member, theme_title)
    pairs from prior nights are excluded from this night's candidate
    pool. Spec §"Night 2 is different from Night 1".
    """
    import argparse
    parser = argparse.ArgumentParser(
        description="Run the Provocateur Pipeline against a run directory."
    )
    parser.add_argument(
        "run_root",
        type=Path,
        help="Run directory containing 02_researcher/ output.",
    )
    parser.add_argument(
        "--prior-nights",
        type=str,
        default=None,
        help=(
            "Comma-separated list of prior-night run_dirs. On Night 2 or 3, "
            "apply the C9 cross-night exclusion filter so a voice doesn't "
            "re-deploy territory it already covered on a prior night. "
            "Match is by normalized theme title (theme_ids are not stable "
            "across Researcher runs)."
        ),
    )
    args = parser.parse_args(argv)
    prior: list[Path] = []
    if args.prior_nights:
        prior = [Path(p.strip()) for p in args.prior_nights.split(",") if p.strip()]
    return args.run_root, prior


if __name__ == "__main__":
    run_root, prior_run_dirs = _parse_args(sys.argv[1:])
    run_provocateur(run_root, prior_run_dirs=prior_run_dirs or None)
