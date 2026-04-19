"""Entry points for schema validation + JSON Schema generation.

Pydantic is the source of truth (PB#7). JSON Schema files under
`personas/schemas/generated/` are derived artifacts — regenerate after any
model change via `generate_json_schemas()`. Consumers:

- Merge prompts inline the generated JSON Schema for LLM output-shape guidance.
- Non-Python validators (DR-prompt validation, CI checks) can read the generated
  `.schema.json` files directly.
"""

from __future__ import annotations

import importlib
import json
import pkgutil
from pathlib import Path
from typing import Any, TypeVar

from pydantic import BaseModel, ValidationError


_GENERATED_DIR = Path(__file__).parent / "generated"

T = TypeVar("T", bound=BaseModel)


def validate_chunk_output(model_class: type[T], data: Any) -> T:
    """Validate LLM chunk output against a Pydantic model.

    Raises `ValidationError` with the raw Pydantic critique on failure;
    callers append this string to the user prompt on retry.
    """
    return model_class.model_validate(data)


def _iter_chunk_models() -> list[tuple[str, type[BaseModel]]]:
    """Discover every BaseModel subclass in pass_*.py + merged_dossier.py.

    Skips private classes (names starting with _) and the shared convention
    models (ProjectionWarning, SourceCitation, ContestedReading) — those live
    in `_conventions.py` and are embedded rather than top-level chunk outputs.
    """
    package = importlib.import_module(__package__)
    results: list[tuple[str, type[BaseModel]]] = []
    seen: set[str] = set()
    for info in pkgutil.iter_modules(package.__path__):
        name = info.name
        if name.startswith("_") or name == "generated":
            continue
        module = importlib.import_module(f"{__package__}.{name}")
        for attr in dir(module):
            if attr.startswith("_"):
                continue
            obj = getattr(module, attr)
            if (
                isinstance(obj, type)
                and issubclass(obj, BaseModel)
                and obj is not BaseModel
                and obj.__module__ == module.__name__
                and attr not in seen
            ):
                results.append((attr, obj))
                seen.add(attr)
    return results


def generate_json_schemas() -> list[Path]:
    """Emit one `.schema.json` per chunk model under `generated/`.

    Uses Draft 2020-12 (Pydantic's default). Returns the list of written paths.
    """
    _GENERATED_DIR.mkdir(exist_ok=True)
    written: list[Path] = []
    for name, model in _iter_chunk_models():
        schema = model.model_json_schema()
        path = _GENERATED_DIR / f"{name}.schema.json"
        path.write_text(json.dumps(schema, indent=2, ensure_ascii=False) + "\n")
        written.append(path)
    return written


__all__ = ["validate_chunk_output", "generate_json_schemas", "ValidationError"]
