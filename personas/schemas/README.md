# `personas/schemas/` — Pydantic source of truth

Per REBUILD_PLAN decisions log #1 (Pydantic SoT) and PB#7 (meta-conventions
frozen after chunks 1.1 + 1.2).

## Layout

- `_conventions.py` — shared types (`EvidenceTag`, `Tier`, `SourceCitation`,
  `ContestedReading`, `ProjectionWarning`). **FROZEN** after chunk 1.2 lands.
- `_entry.py` — `validate_chunk_output(model_class, data)` +
  `generate_json_schemas()`.
- `pass_1_1.py` through `pass_1_6.py` — per-chunk domain models.
- `merged_dossier.py` — composition of all 6 chunks + Pass 1.7 coherence
  metadata.
- `voice_config.py` — Pass 0a output schema.
- `generated/*.schema.json` — derived artifacts; regenerate on model change.

## Regenerate JSON Schemas

```bash
cd personas && venv/bin/python -c "
import sys; sys.path.insert(0, '.')
from schemas._entry import generate_json_schemas
for p in generate_json_schemas():
    print(p)
"
```

## Validation

```python
from schemas.pass_1_1 import LifeScaffold
from schemas._entry import validate_chunk_output, ValidationError

try:
    scaffold = validate_chunk_output(LifeScaffold, data)
except ValidationError as e:
    # Append str(e) to LLM user prompt, retry once.
    ...
```

## Convention freeze

META-shape (evidence tags, source citation, tier, contested reading) is frozen
after chunks 1.1 and 1.2 pass end-to-end. Domain-specific fields emerge per
chunk; meta stays stable. Reopening requires explicit architectural decision
review — see REBUILD_PLAN §"Locked architectural decisions (PB#1-9)".
