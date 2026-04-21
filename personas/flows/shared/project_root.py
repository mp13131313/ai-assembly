"""PROJECT_ROOT resolution (Tier 3 code/project separation).

Per `_workspace/planning/OPEN_ITEMS.md` §"Code / project separation (Tier 3)":
code repo holds runners, schemas, prompts, and fixtures; project data
(per-voice configs, DR prompts, runs, conference facts, session transcripts,
council_config, runtime reference data) lives outside the code repo under
a PROJECT_ROOT.

Both the personas pipeline and the runtime pipeline resolve PROJECT_ROOT
via this module — they share a project root per deployment (personas writes
the persona cards, runtime reads them from the same place).

Precedence:
  1. `--project <path>` CLI arg (passed explicitly by the runner)
  2. `AI_ASSEMBLY_PROJECT_ROOT` environment variable (read via python-dotenv
     from the shared `.env`, or set in the shell / systemd EnvironmentFile)
  3. Hard failure with a clear message. There is **no** silent default —
     with multiple projects on one codebase (test / athens-2026 / …), a
     fallback would risk writing to the wrong project on a forgotten flag.

Typical dev-machine setup: the shared `.env` sets
`AI_ASSEMBLY_PROJECT_ROOT=.../projects/test` so bare invocations land in
the test project; pass `--project .../projects/athens-2026` for production.
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


def resolve_project_root(
    cli_value: str | None = None,
    *,
    repo_root: Path | None = None,
) -> Path:
    """Resolve PROJECT_ROOT per precedence. Exits loudly if unset.

    `repo_root` is retained on the signature for call-site symmetry across
    pipelines (personas / runtime) and for possible future use; it is not
    read today.
    """
    del repo_root  # currently unused; kept for call-site symmetry
    if cli_value:
        root = Path(cli_value).expanduser().resolve()
        source = "--project"
    elif os.environ.get("AI_ASSEMBLY_PROJECT_ROOT"):
        root = Path(os.environ["AI_ASSEMBLY_PROJECT_ROOT"]).expanduser().resolve()
        source = "AI_ASSEMBLY_PROJECT_ROOT env"
    else:
        sys.exit(
            "PROJECT_ROOT is not set. Pass --project <path>, or set "
            "AI_ASSEMBLY_PROJECT_ROOT in the shared .env / shell (e.g. "
            "AI_ASSEMBLY_PROJECT_ROOT=\"/Users/you/Desktop/AI Assembly/projects/test\"). "
            "See CLAUDE.md §'Code / project separation (Tier 3)'."
        )

    if not root.exists():
        sys.exit(
            f"PROJECT_ROOT does not exist: {root}\n"
            f"  (resolved from: {source})\n"
            f"Pass --project <path> or fix AI_ASSEMBLY_PROJECT_ROOT."
        )
    if not root.is_dir():
        sys.exit(f"PROJECT_ROOT is not a directory: {root}")
    return root


def get_project_root() -> Path:
    """Resolve PROJECT_ROOT from environment (no CLI arg). Exits loudly if unset.

    Use when there is no CLI arg available (e.g. inside library modules that
    don't own a parser). For runner entry points use resolve_project_root()
    with the CLI arg.
    """
    return resolve_project_root(None)


def add_project_arg(parser: argparse.ArgumentParser) -> None:
    """Attach the standard --project argument to a runner's argparse."""
    parser.add_argument(
        "--project",
        metavar="PATH",
        default=None,
        help="Project data root (overrides $AI_ASSEMBLY_PROJECT_ROOT). "
             "Contains inputs/, runs/, council_config.json, reference/.",
    )
