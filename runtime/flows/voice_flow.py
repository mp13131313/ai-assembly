"""Voice Pipeline — Prefect orchestrator.

Per docs/AI_Assembly_Voice_Pipeline.md v2 (2026-04-28):

  Step 1 (parallel across (voice, formulation) pairs)
    → optional Validation A + B (OpenAI ladder, in parallel; 1 retry on failure)
    → Step 2 (parallel across voices, after each voice's Step 1 settles)
    → Step 3 (parallel across voices, after ALL voices' Step 2 complete)
    → Continuity (parallel across voices, Nights 1+2 only;
                  output consumed on Nights 2+3)

Reads:
  <run_dir>/03_provocateur/briefings/<voice_slug>.json   (input contract)
  <PROJECT_ROOT>/voices/<voice_slug>/07_persona_card_assembled.json
  <PROJECT_ROOT>/voices/<voice_slug>/continuity_night_<night>.json
       (Night 2+ only, if previous night's continuity flow ran)

Writes:
  <run_dir>/04_voice/step1_detailed_responses/<voice_slug>__<theme_id>.json
  <run_dir>/04_voice/validation/<voice_slug>__<theme_id>.json   (if validation on)
  <run_dir>/04_voice/step2_first_draft_artifacts/<voice_slug>.json
  <run_dir>/04_voice/step3_amended_artifacts/<voice_slug>.json
  <run_dir>/04_voice/responded_to_graph_night_N.json
  <run_dir>/04_voice/themes_to_voices_night_N.json
  <run_dir>/04_voice/step3_complete.flag                (sentinel for continuity)
  <run_dir>/04_voice/manifest.json
  <PROJECT_ROOT>/voices/<voice_slug>/continuity_night_<N+1>.json

CLI:
  python flows/voice_flow.py <run_dir> --night N [--skip-validation]
                                                 [--skip-step3]
                                                 [--skip-continuity]
                                                 [--project PATH]
                                                 [--voices SLUG[,SLUG...]]
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

try:
    from prefect import flow, task
    from dotenv import load_dotenv
    # override=True so the .env values win over any empty / placeholder
    # env vars in the parent shell. Matches personas/run_persona_pipeline.py.
    load_dotenv(_REPO_ROOT.parent / ".env", override=True)
    from flows.shared.io import get_logger, member_slug, write_json_atomic
    from flows.shared.project_root import add_project_arg, resolve_project_root
    from flows.voice.card_assembly import load_persona_card
    from flows.voice.step1_private_reasoning import run_step1_for_pair
    from flows.voice.step1_validation import run_validation_for_step1_output
    from flows.voice.step2_first_draft_artifact import run_step2_for_voice
    from flows.voice.step3_amended_artifact import run_step3_for_voice
    from flows.voice.continuity import generate_continuity
    from flows.voice.publish import publish_voice_artifacts_for_night
except ImportError as e:
    sys.stderr.write(
        f"Missing dependency: {e.name}\n"
        "Install with:  pip install anthropic openai google-genai prefect python-dotenv\n"
    )
    sys.exit(1)


VOICE_STEP1_BATCH = int(os.environ.get("VOICE_STEP1_BATCH", "4"))
VOICE_STEP2_BATCH = int(os.environ.get("VOICE_STEP2_BATCH", "4"))
VOICE_STEP3_BATCH = int(os.environ.get("VOICE_STEP3_BATCH", "4"))
VOICE_CONTINUITY_BATCH = int(os.environ.get("VOICE_CONTINUITY_BATCH", "4"))
VOICE_BATCH_WAIT_S = int(os.environ.get("VOICE_BATCH_WAIT_S", "20"))


def _load_briefings(run_dir: Path) -> dict[str, list[dict[str, Any]]]:
    """Load all per-voice briefings from 03_provocateur/briefings/."""
    briefings_dir = run_dir / "03_provocateur" / "briefings"
    if not briefings_dir.exists():
        raise FileNotFoundError(
            f"No Provocateur briefings at {briefings_dir}. "
            f"Run the Provocateur Pipeline first."
        )
    out: dict[str, list[dict[str, Any]]] = {}
    for p in sorted(briefings_dir.glob("*.json")):
        slug = p.stem
        with open(p, encoding="utf-8") as f:
            briefing = json.load(f)
        out[slug] = briefing.get("formulations", [])
    return out


def _resolve_council_member(slug: str, project_root: Path) -> str:
    """Best-effort: look up council_member_name from the assembled card."""
    try:
        card = load_persona_card(slug, night=1, project_root=project_root)
        return card.get("council_member_name", slug)
    except FileNotFoundError:
        return slug


def _theme_display_titles_from_briefings(
    briefings: dict[str, list[dict[str, Any]]],
) -> dict[str, str]:
    """Build a {theme_id → theme_display_title} index across all briefings."""
    out: dict[str, str] = {}
    for formulations in briefings.values():
        for f in formulations:
            tid = f.get("theme_id")
            tt = f.get("theme_display_title")
            if tid and tt and tid not in out:
                out[tid] = tt
    return out


# --- Step 1 batch runner ----------------------------------------------

def _run_step1_batch(
    pairs: list[tuple[str, dict[str, Any]]],
    night: int,
    run_dir: Path,
    project_root: Path,
    council_names: dict[str, str],
) -> dict[tuple[str, str], dict[str, Any]]:
    """Run Step 1 across (voice, formulation) pairs in batches.

    Batch size = VOICE_STEP1_BATCH; wait VOICE_BATCH_WAIT_S between
    batches to respect Anthropic rate limits.
    """
    logger = get_logger("voice_flow")
    results: dict[tuple[str, str], dict[str, Any]] = {}
    total = len(pairs)
    for batch_start in range(0, total, VOICE_STEP1_BATCH):
        batch = pairs[batch_start : batch_start + VOICE_STEP1_BATCH]
        logger.info(
            f"Step 1 batch {batch_start // VOICE_STEP1_BATCH + 1} "
            f"({batch_start + 1}-{batch_start + len(batch)} of {total})"
        )
        with ThreadPoolExecutor(max_workers=VOICE_STEP1_BATCH) as ex:
            futures = {
                ex.submit(
                    run_step1_for_pair,
                    voice_slug=slug,
                    formulation_entry=entry,
                    night=night,
                    run_dir=run_dir,
                    project_root=project_root,
                    council_member_name=council_names.get(slug),
                ): (slug, entry["theme_id"])
                for slug, entry in batch
            }
            for fut in as_completed(futures):
                key = futures[fut]
                try:
                    results[key] = fut.result()
                except Exception as e:  # noqa: BLE001
                    logger.error(f"Step 1 failed for {key}: {e}")
        if batch_start + VOICE_STEP1_BATCH < total:
            time.sleep(VOICE_BATCH_WAIT_S)
    return results


# --- Validation runner ------------------------------------------------

def _run_validation_for_voice(
    voice_slug: str,
    step1_outputs: list[dict[str, Any]],
    project_root: Path,
    night: int,
    run_dir: Path,
) -> list[dict[str, Any]]:
    """Validate every Step 1 output for one voice. Returns validation results."""
    card = load_persona_card(voice_slug, night=night, project_root=project_root)
    out = []
    for s1 in step1_outputs:
        try:
            v = run_validation_for_step1_output(s1, card, run_dir)
            out.append(v)
        except Exception as e:  # noqa: BLE001
            get_logger("voice_flow").error(
                f"Validation failed for {voice_slug}__{s1['lineage']['theme_id']}: {e}"
            )
    return out


# --- Manifest + roll-ups ----------------------------------------------

def _build_themes_to_voices(
    step1_results: dict[tuple[str, str], dict[str, Any]],
    step2_results: dict[str, dict[str, Any]],
    step3_results: dict[str, dict[str, Any]],
) -> dict[str, dict[str, list[str]]]:
    """For each theme_id: which voices engaged at each step."""
    out: dict[str, dict[str, list[str]]] = {}
    for (slug, theme_id), _ in step1_results.items():
        out.setdefault(theme_id, {"step1_voices": [], "step2_voices": [], "step3_voices": []})
        out[theme_id]["step1_voices"].append(slug)
    for slug, s2 in step2_results.items():
        for theme_id in s2["lineage"].get("themes_covered", []):
            out.setdefault(theme_id, {"step1_voices": [], "step2_voices": [], "step3_voices": []})
            out[theme_id]["step2_voices"].append(slug)
    for slug, s3 in step3_results.items():
        for theme_id in s3["lineage"].get("own_first_draft_themes_covered", []):
            out.setdefault(theme_id, {"step1_voices": [], "step2_voices": [], "step3_voices": []})
            out[theme_id]["step3_voices"].append(slug)
    return out


def _build_responded_to_graph(
    step3_results: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Per-night directed graph of cross-voice amendment engagement.

    Edges are derived from each Step 3 output's `decision` +
    `lineage.voices_read` + (when present) structured `amendments[]`.

    Design (post-dryrun #4 finding): voices respond to each other
    holistically in prose rather than enumerating per-passage
    amendments. The voice's `amendments[]` field is therefore often
    empty even when `decision="amend"` and the artifact substantively
    engages other voices. To keep the graph populated without
    pressuring the artifact-writing surface (which at extended-thinking
    + creative-prose is the wrong place for metadata bookkeeping), we
    derive baseline voice-pair edges from `voices_read` + `decision`
    and decorate with per-passage detail ONLY when the voice emitted
    structured amendments.

    Edge shapes:
      - With structured amendments: one edge per amendment, carries
        `amendment_type` ∈ {extend, mark-limit, sharpen-disagreement},
        `theme_id`, `cited_passage`, `rationale`
      - Without structured amendments (the common case): one edge per
        voice-pair, carries `amendment_type: "engaged"`, plus a
        `decision_rationale_excerpt` (≤240 chars) giving qualitative
        texture for downstream consumers (closing-show pipeline,
        publish layer) without requiring per-passage parsing

    Voices with `decision="stand-pat"` produce no edges (they
    deliberately did not engage).
    """
    edges: list[dict[str, Any]] = []
    for slug, s3 in step3_results.items():
        if s3.get("decision") != "amend":
            continue
        # Group structured amendments by cited voice slug (when present)
        amendments = s3.get("amendments", []) or []
        by_voice: dict[str, list[dict[str, Any]]] = {}
        for a in amendments:
            target = (a.get("cited_voice_slug") or "").lower()
            if not target and a.get("cited_voice"):
                target = a["cited_voice"].lower().replace(" ", "_")
            if target:
                by_voice.setdefault(target, []).append(a)
        voices_read = s3.get("lineage", {}).get("voices_read", []) or []
        rationale = s3.get("decision_rationale", "") or ""
        rationale_excerpt = (
            rationale[:240] + ("…" if len(rationale) > 240 else "")
        )
        for vr in voices_read:
            target_slug = vr.get("voice_slug")
            if not target_slug:
                continue
            structured = by_voice.get(target_slug, [])
            if structured:
                for a in structured:
                    edges.append({
                        "from": slug,
                        "to": target_slug,
                        "amendment_type": a.get("amendment_type", "engaged"),
                        "theme_id": a.get("cited_theme_id", ""),
                        "cited_passage": a.get("cited_passage", ""),
                        "rationale": a.get("rationale", ""),
                    })
            else:
                edges.append({
                    "from": slug,
                    "to": target_slug,
                    "amendment_type": "engaged",
                    "theme_id": "",
                    "decision_rationale_excerpt": rationale_excerpt,
                })
    nodes = sorted({s3["lineage"]["voice_slug"] for s3 in step3_results.values()})
    return {"nodes": nodes, "edges": edges}


# --- Main flow --------------------------------------------------------

@flow(name="voice-pipeline")
def run_voice(
    run_dir: str | Path,
    night: int,
    skip_validation: bool = False,
    skip_step3: bool = False,
    skip_continuity: bool = False,
    project_root: Path | None = None,
    voices_filter: list[str] | None = None,
) -> dict[str, Any]:
    """Run the Voice Pipeline end-to-end for one night."""
    logger = get_logger("voice_flow")
    run_dir = Path(run_dir)
    if project_root is None:
        project_root = resolve_project_root(None)

    logger.info(f"Voice Pipeline: run_dir={run_dir}, night={night}, project_root={project_root}")
    briefings = _load_briefings(run_dir)
    if voices_filter:
        briefings = {k: v for k, v in briefings.items() if k in voices_filter}
        logger.info(f"  filtered to voices: {sorted(briefings)}")

    # Resolve council_member_name per voice up front (cached card load).
    council_names = {slug: _resolve_council_member(slug, project_root) for slug in briefings}
    theme_display_titles = _theme_display_titles_from_briefings(briefings)

    # Build (voice, formulation) pair list for Step 1.
    pairs: list[tuple[str, dict[str, Any]]] = []
    for slug, formulations in briefings.items():
        for entry in formulations:
            pairs.append((slug, entry))
    logger.info(f"  Step 1: {len(pairs)} pairs across {len(briefings)} voices")

    t_start = time.time()

    # ---- Step 1 ----
    step1_results = _run_step1_batch(pairs, night, run_dir, project_root, council_names)

    # Group Step 1 results by voice for downstream steps.
    step1_by_voice: dict[str, list[dict[str, Any]]] = {}
    for (slug, _theme_id), result in step1_results.items():
        step1_by_voice.setdefault(slug, []).append(result)

    # ---- Validation (parallel across pairs) ----
    validation_failures: list[dict[str, Any]] = []
    if not skip_validation:
        logger.info(f"  Validation: running on {len(step1_results)} Step 1 outputs")
        with ThreadPoolExecutor(max_workers=VOICE_STEP1_BATCH) as ex:
            futures = {
                ex.submit(
                    _run_validation_for_voice,
                    voice_slug=slug,
                    step1_outputs=outputs,
                    project_root=project_root,
                    night=night,
                    run_dir=run_dir,
                ): slug
                for slug, outputs in step1_by_voice.items()
            }
            for fut in as_completed(futures):
                slug = futures[fut]
                try:
                    results = fut.result()
                    for r in results:
                        if r.get("final_status") == "flagged":
                            validation_failures.append({"voice_slug": slug, "result": r})
                except Exception as e:  # noqa: BLE001
                    logger.error(f"Validation batch failed for {slug}: {e}")
    else:
        logger.info("  Validation: SKIPPED (--skip-validation)")

    # ---- Step 2 (parallel across voices) ----
    logger.info(f"  Step 2: running for {len(step1_by_voice)} voices")
    step2_results: dict[str, dict[str, Any]] = {}
    with ThreadPoolExecutor(max_workers=VOICE_STEP2_BATCH) as ex:
        futures = {
            ex.submit(
                run_step2_for_voice,
                voice_slug=slug,
                step1_outputs=outputs,
                night=night,
                run_dir=run_dir,
                project_root=project_root,
                council_member_name=council_names.get(slug),
            ): slug
            for slug, outputs in step1_by_voice.items()
        }
        for fut in as_completed(futures):
            slug = futures[fut]
            try:
                step2_results[slug] = fut.result()
            except Exception as e:  # noqa: BLE001
                logger.error(f"Step 2 failed for {slug}: {e}")

    # ---- Step 3 (parallel across voices, requires ALL voices' Step 2) ----
    step3_results: dict[str, dict[str, Any]] = {}
    if not skip_step3:
        logger.info(f"  Step 3: running for {len(step2_results)} voices")
        with ThreadPoolExecutor(max_workers=VOICE_STEP3_BATCH) as ex:
            futures = {
                ex.submit(
                    run_step3_for_voice,
                    voice_slug=slug,
                    own_first_draft=own,
                    other_first_drafts=[
                        other for other_slug, other in step2_results.items()
                        if other_slug != slug
                    ],
                    night=night,
                    run_dir=run_dir,
                    project_root=project_root,
                    council_member_name=council_names.get(slug),
                    theme_display_titles=theme_display_titles,
                ): slug
                for slug, own in step2_results.items()
            }
            for fut in as_completed(futures):
                slug = futures[fut]
                try:
                    step3_results[slug] = fut.result()
                except Exception as e:  # noqa: BLE001
                    logger.error(f"Step 3 failed for {slug}: {e}")
    else:
        logger.info("  Step 3: SKIPPED (--skip-step3) — DEV USE ONLY")

    # ---- Roll-ups ----
    out_dir = run_dir / "04_voice"
    out_dir.mkdir(parents=True, exist_ok=True)
    if step3_results:
        write_json_atomic(
            out_dir / f"responded_to_graph_night_{night}.json",
            _build_responded_to_graph(step3_results),
        )
    write_json_atomic(
        out_dir / f"themes_to_voices_night_{night}.json",
        _build_themes_to_voices(step1_results, step2_results, step3_results),
    )

    # Determine voices that completed the night (Step 3 if it ran, else Step 2).
    # Under A1 (Step 3 SKIPPED for Athens production via --skip-step3), the
    # night is "complete" once Step 2 ships — continuity + downstream consumers
    # need a night-completion signal regardless of whether Step 3 ran.
    completed_voices: dict[str, Any] = step3_results if step3_results else step2_results

    # Sentinel for continuity flow / night completion. Filename retained for
    # back-compat with any downstream consumers; semantic is "night complete"
    # not literally "step3 complete" since A1.
    if completed_voices:
        (out_dir / "step3_complete.flag").write_text(time.strftime("%Y-%m-%dT%H:%M:%S\n"))

    # ---- Publish per-voice artifacts to PROJECT_ROOT/published_artifacts/ ----
    # Reads Step 3 (and Step 2 for stance + focus_decision) and writes
    # publish-ready files at <PROJECT_ROOT>/published_artifacts/nights/
    # night_<N>/<slug>.json + per-night _index.json. Themes referenced by
    # ID — full theme metadata produced by separate publish_flow.py
    # (which reads across upstream pipelines: Researcher + Provocateur +
    # Voice).
    publish_summary: dict[str, Any] = {}
    if step3_results and not skip_step3:
        try:
            publish_summary = publish_voice_artifacts_for_night(
                run_dir=run_dir,
                night=night,
                project_root=project_root,
                voice_slugs=sorted(step3_results),
            )
        except Exception as e:  # noqa: BLE001
            logger.error(f"Publish step failed: {e}")
            publish_summary = {"error": str(e)}

    # ---- Continuity (Nights 1+2 only — output is consumed on Nights 2+3) ----
    # Per A1 (2026-05-01), continuity must run when Step 2 completes, even
    # when Step 3 is skipped — so the gate is on `completed_voices`, not on
    # step3 having run. continuity.py already tolerates step3_output=None
    # at runtime (it iterates over Step 1 + 2 + 3 and skips missing parts).
    continuity_results: dict[str, dict[str, Any]] = {}
    if not skip_continuity and night < 3 and completed_voices:
        logger.info(f"  Continuity: generating for {len(completed_voices)} voices (for night {night + 1})")
        with ThreadPoolExecutor(max_workers=VOICE_CONTINUITY_BATCH) as ex:
            futures = {
                ex.submit(
                    generate_continuity,
                    voice_slug=slug,
                    night_just_completed=night,
                    run_dir=run_dir,
                    project_root=project_root,
                ): slug
                for slug in completed_voices
            }
            for fut in as_completed(futures):
                slug = futures[fut]
                try:
                    continuity_results[slug] = fut.result()
                except Exception as e:  # noqa: BLE001
                    logger.error(f"Continuity failed for {slug}: {e}")
    else:
        if night >= 3:
            logger.info("  Continuity: SKIPPED (last night — no Night 4 to feed)")
        elif skip_continuity:
            logger.info("  Continuity: SKIPPED (--skip-continuity)")
        elif not completed_voices:
            logger.info("  Continuity: SKIPPED (no voices completed this night)")

    wall_total = round(time.time() - t_start, 2)

    # ---- Manifest ----
    manifest = {
        "pipeline": "voice",
        "pipeline_version": "v2",
        "night": night,
        "run_id": run_dir.name,
        "model": os.environ.get("VOICE_MODEL", "claude-opus-4-7"),
        "thinking_enabled": os.environ.get("VOICE_THINKING", "1") != "0",
        "voices_processed": sorted(briefings),
        "counts": {
            "step1_pairs_attempted": len(pairs),
            "step1_pairs_succeeded": len(step1_results),
            "step2_voices_succeeded": len(step2_results),
            "step3_voices_succeeded": len(step3_results),
            "continuity_voices_succeeded": len(continuity_results),
            "validation_flagged": len(validation_failures),
        },
        "validation_failures": validation_failures,
        "publish_summary": publish_summary,
        "wall_clock_s": wall_total,
        "config": {
            "VOICE_STEP1_BATCH": VOICE_STEP1_BATCH,
            "VOICE_BATCH_WAIT_S": VOICE_BATCH_WAIT_S,
            "skip_validation": skip_validation,
            "skip_step3": skip_step3,
            "skip_continuity": skip_continuity,
        },
    }
    write_json_atomic(out_dir / "manifest.json", manifest)

    logger.info(
        f"Voice Pipeline complete: night={night}, wall={wall_total}s, "
        f"step1={len(step1_results)}/{len(pairs)}, step2={len(step2_results)}, "
        f"step3={len(step3_results)}, continuity={len(continuity_results)}, "
        f"flagged={len(validation_failures)}"
    )
    logger.info(f"  manifest: {out_dir / 'manifest.json'}")
    return manifest


# --- CLI --------------------------------------------------------------

def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Voice Pipeline — Steps 1+2+3 + validation + continuity for one night."
    )
    p.add_argument("run_dir", help="Run directory containing 03_provocateur/briefings/")
    p.add_argument("--night", type=int, required=True, choices=[1, 2, 3])
    p.add_argument("--skip-validation", action="store_true")
    p.add_argument(
        "--skip-step3",
        action="store_true",
        help="Run Steps 1+2 only. DEV USE ONLY — Step 3 is load-bearing for Athens.",
    )
    p.add_argument("--skip-continuity", action="store_true")
    p.add_argument(
        "--voices",
        default=None,
        help="Comma-separated voice slugs to filter (default: all in briefings/).",
    )
    add_project_arg(p)
    return p.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    project_root = resolve_project_root(args.project)
    voices_filter = (
        [s.strip() for s in args.voices.split(",") if s.strip()] if args.voices else None
    )
    run_voice(
        run_dir=args.run_dir,
        night=args.night,
        skip_validation=args.skip_validation,
        skip_step3=args.skip_step3,
        skip_continuity=args.skip_continuity,
        project_root=project_root,
        voices_filter=voices_filter,
    )
