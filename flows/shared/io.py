"""I/O helpers for the Persona Pipeline.

Mirrors the patterns from ai-assembly/flows/shared/io.py:
- atomic JSON writes (temp file + rename)
- prompt loader from flows/shared/prompts/
- voice input loader + Node 0 validation
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_PROMPTS_DIR = _REPO_ROOT / "flows" / "shared" / "prompts"
_INPUTS_DIR = _REPO_ROOT / "inputs" / "voices"


VALID_TYPES = {"human", "non-human", "fictional"}
VALID_VOICE_MODES = {"philosophical", "observational", "narratival"}
VALID_SUBTYPES = {None, "organism", "system"}
VALID_CORPUS_CONSTRAINTS = {
    "full",
    "lyrics — describe patterns only",
    "hostile — read against grain",
}


def _slugify(name: str) -> str:
    """Convert a voice name to a filename-safe slug."""
    return (
        name.lower()
        .replace(" ", "_")
        .replace(".", "")
        .replace(",", "")
        .replace("'", "")
        .replace("/", "_")
    )


def voice_slug(name: str) -> str:
    """Public alias — voice name to slug."""
    return _slugify(name)


def write_json_atomic(path: Path | str, data: Any) -> None:
    """Write JSON via temp file + rename, so partial writes never leave
    a half-written file on disk."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=str(path.parent)
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except FileNotFoundError:
            pass
        raise


def load_prompt(name: str) -> str:
    """Load a prompt file from flows/shared/prompts/ by base name (no .md)."""
    prompt_path = _PROMPTS_DIR / f"{name}.md"
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt not found: {prompt_path}")
    return prompt_path.read_text(encoding="utf-8")


def load_voice_input(name_or_slug: str) -> dict[str, Any]:
    """Load a voice's input schema from inputs/voices/{slug}.json.

    Accepts either the full name ("Hannah Arendt") or the slug
    ("hannah_arendt").
    """
    candidates = [name_or_slug, _slugify(name_or_slug)]
    for c in candidates:
        path = _INPUTS_DIR / f"{c}.json"
        if path.exists():
            with path.open(encoding="utf-8") as f:
                return json.load(f)
    raise FileNotFoundError(
        f"No input schema for {name_or_slug!r}. Tried: "
        + ", ".join(str(_INPUTS_DIR / f"{c}.json") for c in candidates)
    )
