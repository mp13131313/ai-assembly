#!/usr/bin/env python3
"""Editor Pipeline — orchestrator entry point.

Per spec v2 (`docs/AI_Assembly_Editor_Pipeline.md`):

  Stage 1 (deterministic): theme_routing — assigns each voice's Step 2
  artifact to one dossier (its primary theme) via Cases A/B/C/D parser
  on focus_decision. Writes <run_dir>/05_editor/theme_routing.json.

  Stage 2 (per-dossier Anthropic call): for each engaged theme, call
  Claudia with the deduped dossier briefing + the night's engaged voices'
  artifacts. One call per dossier; calls run in parallel via
  ThreadPoolExecutor; system prompt cached across the night.

Reads (per spec v2 §"What the Editor Pipeline Knows"):
  <run_dir>/04_voice/step2_first_draft_artifacts/<voice>.json
  <run_dir>/03_provocateur/briefings/<voice>.json
  <PROJECT_ROOT>/editor/tim_leberecht/07_persona_card_assembled.json
  <PROJECT_ROOT>/published_artifacts/dossiers/night_<N-1>/*.json (Night 2/3)

Writes:
  <run_dir>/05_editor/theme_routing.json
  <run_dir>/05_editor/dossiers/dossier_<NNN>.json
  <PROJECT_ROOT>/published_artifacts/dossiers/night_<N>/dossier_<NNN>.json
  <run_dir>/05_editor/manifest.json

CLI:
  python flows/editor_flow.py <run_dir> --night N
                               [--skip-routing]      Stage 1 already written by hand
                               [--single-dossier <theme_id>]   one dossier only (testing)
                               [--no-cache]          disable prompt caching
                               [--project PATH]      PROJECT_ROOT override

Cost (Athens 3 nights, 3-5 dossiers/night, Opus 4.7 + 1h prefix cache):
  ~$3-5 total. Wall ~5-10 min per night with parallel dossier calls.
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
    from dotenv import load_dotenv
    load_dotenv(_REPO_ROOT.parent / ".env", override=True)
    from flows.shared.io import (  # noqa: E402
        assert_run_dir_night_matches,
        get_logger,
        write_json_atomic,
    )
    from flows.shared.project_root import add_project_arg, resolve_project_root  # noqa: E402
    from flows.editor.card_assembly import assemble_system_prompt, load_editor_card  # noqa: E402
    from flows.editor.routing import write_routing_manifest  # noqa: E402
    from flows.editor.dossier_generation import (  # noqa: E402
        EDITOR_MODEL,
        EDITOR_THINKING,
        generate_dossier,
    )
    from flows.editor.publish import load_prior_editions, write_dossier  # noqa: E402
except ImportError as e:
    sys.stderr.write(
        f"Missing dependency: {e.name}\n"
        "Install with:  pip install anthropic prefect python-dotenv\n"
    )
    sys.exit(1)


EDITOR_BATCH = int(os.environ.get("EDITOR_BATCH", "6"))


def _voices_routed_to(routing: dict[str, Any], theme_id: str) -> list[str]:
    """Return voice_slugs whose primary_theme is theme_id."""
    return sorted(
        v["voice_slug"]
        for v in routing.get("voices_routing", [])
        if v.get("primary_theme") == theme_id
    )


def run_editor_pipeline(
    run_dir: Path,
    night: int,
    *,
    project_root: Path,
    skip_routing: bool = False,
    single_dossier: str | None = None,
    no_cache: bool = False,
) -> dict[str, Any]:
    """End-to-end Editor Pipeline. Returns the manifest dict."""
    logger = get_logger("editor_flow")
    t_start = time.time()

    assert_run_dir_night_matches(run_dir, night)

    # ---- Stage 1: routing ------------------------------------------------
    if skip_routing:
        routing_path = run_dir / "05_editor" / "theme_routing.json"
        if not routing_path.exists():
            raise SystemExit(
                f"--skip-routing set but {routing_path} does not exist; "
                f"can't proceed without a hand-written routing manifest."
            )
        with routing_path.open(encoding="utf-8") as f:
            routing = json.load(f)
        logger.info(f"Stage 1 SKIPPED — using existing {routing_path}")
    else:
        logger.info("Stage 1: theme routing")
        routing = write_routing_manifest(run_dir, night, logger=logger)
        logger.info(
            f"  routed {len(routing['voices_routing'])} voices into "
            f"{len(routing['themes_to_dossiers'])} dossier(s); "
            f"{len(routing['refusals'])} refusal(s)"
        )

    # ---- Stage 2: per-dossier calls -------------------------------------
    card = load_editor_card(project_root=project_root)
    system_prompt = assemble_system_prompt(card, night=night)

    prior_editions = load_prior_editions(project_root, night)
    if prior_editions:
        logger.info(
            f"  loaded prior editions from {len(prior_editions)} prior night(s) "
            f"({sum(len(e['dossiers']) for e in prior_editions)} prior dossier(s) total)"
        )

    # Filter dossiers if --single-dossier; else process all.
    dossier_specs = routing["themes_to_dossiers"]
    if single_dossier:
        dossier_specs = [d for d in dossier_specs if d["theme_id"] == single_dossier]
        if not dossier_specs:
            raise SystemExit(
                f"--single-dossier {single_dossier} did not match any theme in "
                f"theme_routing.json; available: "
                f"{[d['theme_id'] for d in routing['themes_to_dossiers']]}"
            )
        logger.info(f"  --single-dossier filter: only {single_dossier}")

    # One Anthropic client per call (thread-safe; Anthropic SDK has internal pooling).
    from anthropic import Anthropic
    client = Anthropic()

    dossier_results: dict[str, dict[str, Any]] = {}
    dossier_failures: list[dict[str, Any]] = []

    def _run_one(dspec: dict[str, Any]) -> tuple[str, dict[str, Any] | None, Exception | None]:
        theme_id = dspec["theme_id"]
        voice_slugs = _voices_routed_to(routing, theme_id)
        if not voice_slugs:
            logger.warning(
                f"  theme={theme_id} has no voices routed to it (n_engaged_voices=0); skipping"
            )
            return (theme_id, None, ValueError("no engaged voices"))
        try:
            dossier = generate_dossier(
                theme_id=theme_id,
                voice_slugs=voice_slugs,
                run_dir=run_dir,
                night=night,
                system_prompt=system_prompt,
                client=client,
                prior_editions=prior_editions,
                logger=logger,
            )
            return (theme_id, dossier, None)
        except Exception as e:  # noqa: BLE001 — orchestrator must not crash on one dossier's failure
            return (theme_id, None, e)

    logger.info(
        f"Stage 2: dossier generation ({len(dossier_specs)} dossier(s), "
        f"batch={EDITOR_BATCH}, model={EDITOR_MODEL}, thinking={EDITOR_THINKING})"
    )
    with ThreadPoolExecutor(max_workers=EDITOR_BATCH) as ex:
        futures = {ex.submit(_run_one, d): d for d in dossier_specs}
        for fut in as_completed(futures):
            theme_id, dossier, err = fut.result()
            if err is not None or dossier is None:
                logger.error(f"  dossier theme={theme_id} FAILED: {err}")
                dossier_failures.append({"theme_id": theme_id, "error": str(err)})
                continue
            # Find dossier_no from routing
            dspec = next(d for d in routing["themes_to_dossiers"] if d["theme_id"] == theme_id)
            dossier_no = dspec["dossier_no"]
            run_path, pub_path = write_dossier(
                dossier,
                run_dir=run_dir,
                project_root=project_root,
                night=night,
                dossier_no=dossier_no,
            )
            dossier_results[theme_id] = dossier
            logger.info(f"  wrote {run_path.name} (run_dir + published)")

    # ---- Manifest -------------------------------------------------------
    wall_total = round(time.time() - t_start, 2)
    manifest = {
        "pipeline":         "editor",
        "pipeline_version": "v2",
        "schema_version":   "2.0",
        "night":            night,
        "run_id":           run_dir.name,
        "model":            EDITOR_MODEL,
        "thinking_enabled": EDITOR_THINKING,
        "counts": {
            "themes_routed":      len(routing["themes_to_dossiers"]),
            "dossiers_succeeded": len(dossier_results),
            "dossiers_failed":    len(dossier_failures),
            "voices_engaged":     sum(
                d.get("n_engaged_voices", 0) for d in routing["themes_to_dossiers"]
            ),
            "refusals":           len(routing.get("refusals", [])),
        },
        "dossier_failures": dossier_failures,
        "wall_clock_s":     wall_total,
        "config": {
            "EDITOR_BATCH":  EDITOR_BATCH,
            "skip_routing":  skip_routing,
            "single_dossier": single_dossier,
            "no_cache":      no_cache,
        },
    }
    write_json_atomic(run_dir / "05_editor" / "manifest.json", manifest)
    logger.info(
        f"Editor Pipeline complete: night={night}, wall={wall_total}s, "
        f"dossiers={len(dossier_results)}/{len(dossier_specs)}, "
        f"failures={len(dossier_failures)}"
    )
    return manifest


# --- CLI -----------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("run_dir", type=Path, help="Per-night run directory.")
    ap.add_argument("--night", type=int, required=True, choices=(1, 2, 3),
                    help="Athens night (1, 2, 3).")
    ap.add_argument("--skip-routing", action="store_true",
                    help="Skip Stage 1; assume theme_routing.json is hand-written.")
    ap.add_argument("--single-dossier", default=None,
                    help="Run Stage 2 for one theme only (theme_id).")
    ap.add_argument("--no-cache", action="store_true",
                    help="Disable prompt caching (useful when iterating on Claudia's card).")
    add_project_arg(ap)
    args = ap.parse_args(argv)

    project_root = resolve_project_root(args.project)
    run_dir = args.run_dir if args.run_dir.is_absolute() else (project_root / args.run_dir)

    manifest = run_editor_pipeline(
        run_dir,
        args.night,
        project_root=project_root,
        skip_routing=args.skip_routing,
        single_dossier=args.single_dossier,
        no_cache=args.no_cache,
    )
    if manifest["counts"]["dossiers_failed"]:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
