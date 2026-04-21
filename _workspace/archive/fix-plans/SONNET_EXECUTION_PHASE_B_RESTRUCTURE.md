# Sonnet Execution Plan — Phase B per-voice-folder restructure + per-section DR

**Branch:** `phase-b-rebuild`
**Model:** Claude Sonnet 4.6, medium effort
**Scope:** Restructure filesystem to per-voice folders with numbered pass-group subfolders; enable per-section manual Claude DR workflow; bundle 9 smaller improvements. ~14.5 hours across 2–3 sittings.

---

## Your task

Execute the Phase B restructure per this plan, end-to-end. The plan is self-contained. Commit after each phase. Push after every 3–4 phases. Stop and ask on ambiguity — do NOT silently work around issues.

## Context

An Opus 4.7 design session (2026-04-21) locked the architecture for:

1. **Per-voice folder filesystem layout** (replaces flat `$PROJECT_ROOT/inputs/voices/`, `/inputs/dossiers/`, `/runs/<slug>/` split).
2. **Per-section manual DR workflow**: operator pastes six section prompts into claude.ai (producing six `.md` files saved to disk), pipeline auto-detects per-section mode, chunk_runner reads per-section DR + per-section Perplexity + full Gemini per chunked merge.
3. **Monolithic fallback preserved**: if six section files absent but one `<slug>_claude_dr.md` present, pipeline runs v3.5-style monolithic merge.
4. **9 bundled improvements** from OPEN_ITEMS that fit naturally with the restructure.

Empirical basis for per-section: Run 7 §1 + §2 both models (Opus 4.6 + 4.7) completed cleanly in-thread at ~30 min/section on rewritten Pass 0b prompts. Single-thread sequential is viable through at least §2; remains empirically open at §3–§6 (to be validated by Dostoevsky completion during this session's testing phase).

What was killed in prior Run 7 attempts: single-monolithic-prompt convergence trap (~100 demand dimensions, 2h+ wall time, 4K+ sources, generic "Something went wrong"). Per-section shape bounds demand surface to ~15 dimensions per paste, which the Research feature handles cleanly.

## Locked spec

| Decision | Value |
|---|---|
| Folder layout | Per-voice folder with numbered pass-group subfolders (`voices/<slug>/00_intake/…06_derive/`) |
| Header mode | Thread-agnostic (operator chooses single-thread vs fresh-threads per voice) |
| Mode detection | Auto only — no `--mode` CLI flag |
| Partial state | Error with clear message; do NOT proceed with incomplete DR section files |
| Scope | Code + documentation in same commit set |
| Ibn Battuta fixtures | **DELETE** entirely from code repo; no migration; regenerate fresh when his Athens queue slot opens |
| Synthetic test fixtures | `personas/tests/fixtures/synthetic_voice/` — small fake voice exercising plumbing |
| Integration tests | Gated via `@pytest.mark.integration` + env var, run against real project data |
| `_manifest.json` telemetry | Build NOW — wraps every `call_*` for per-pass cost + wall-time + tokens |
| `display_name_with_hint` | Wire — prepend Wikipedia disambiguation to rendered DR prompt |
| Git under `projects/` | Strict Tier 3 — no git inside projects/; curator tracks editorial_rationale edits manually |
| Numbering | Two-digit zero-padded at every level (folders AND files) |
| Path centralization | All path constants in new `personas/flows/shared/paths.py`; no string concatenation in runners |
| `dr_dossier/` location | `voices/<slug>/01_research/04_dr_dossier/` (research-phase, not intake) |
| Pass 7 filenames | Current semantic names + numeric prefix (`01_pass_7_pre_citation.json` through `05_pass_7c_negative.json`) |
| Tailoring | Stays monolithic (one Opus 4.7 call per voice); splitter slices post-tailoring |

## Target directory layout (canonical)

```
$PROJECT_ROOT/voices/<slug>/
  00_intake/                              ← human-curated, rarely changes
    01_non_human_grounding.md             (optional; if voice_config.type == non_human)
    02_voice_config.json                  (Pass 0a output)
    03_review_doc.md                      (Pass 0a review — curator edits editorial_rationale)
  01_research/                            ← Phase 0.5 research corpus (pipeline + human)
    01_perplexity_dossier.json            (Pass 1a)
    02_gemini_broad_scan.json             (Pass 1b)
    03_dr_prompts/                        ← pipeline → human handoff
      01_monolithic_dr_prompt.md          (tailored monolithic; retained for inspection)
      02_tailoring_notes.json             (Opus 4.7 audit log)
      03_section_1_dr_prompt.md           ← PASTE THESE into claude.ai
      04_section_2_dr_prompt.md
      05_section_3_dr_prompt.md
      06_section_4_dr_prompt.md
      07_section_5_dr_prompt.md
      08_section_6_dr_prompt.md
    04_dr_dossier/                        ← human → pipeline handoff (saved DR outputs)
      01_section_1.md
      02_section_2.md
      03_section_3.md
      04_section_4.md
      05_section_5.md
      06_section_6.md
      07_concat_claude_dr.md              (optional; only if operator concatenates for fallback mode)
  02_merge/                               ← Pass 1.1–1.7 outputs
    01_pass_1_1_biographical.json
    02_pass_1_2_intellectual.json
    03_pass_1_3_reasoning.json
    04_pass_1_4_voice.json
    05_pass_1_5_boundaries.json
    06_pass_1_6_corpus.json
    07_pass_1_7_coherence.json
    08_merged_dossier.json
  03_corpus/                              ← Pass 1c + 1d
    01_primary_texts.json                 (Pass 1c fetch)
    02_excerpt_selections.json            (Pass 1d Sonnet)
  04_generation/                          ← Pass 2–6 + coherence-threading summaries
    01_pass_2_identity_boundaries.json
    02_ct_after_pass_2.json
    03_pass_3_intellectual_core.json
    04_ct_after_pass_3.json
    05_pass_4a_voice.json
    06_ct_after_pass_4a.json
    07_pass_4b_artifact.json
    08_ct_after_pass_4b.json
    09_pass_5_engagement.json
    10_pass_6_corpus.json
  05_validation/                          ← Pass 7.*
    01_pass_7_pre_citation.json
    02_pass_7_anachronism.json
    03_pass_7a_cross_model.json
    04_pass_7b_smoke_test.json
    05_pass_7c_negative.json
  06_derive/
    01_provocateur_profile.json
    02_evaluation_rubric.json
  07_persona_card_assembled.json          ← final deliverable
  _manifest.json                          ← per-pass telemetry (cost/wall/tokens)
```

## Preflight

1. Read the docs listed in the handoff file (`HANDOFF_PHASE_B_RESTRUCTURE.md`).

2. Verify branch state:

   ```bash
   cd "/Users/aienvironment/Desktop/AI Assembly/code"
   git status                              # tree must be clean
   git branch --show-current                # must return: phase-b-rebuild
   git log phase-b-rebuild --oneline -10    # sanity-check recent commits
   ```

3. Verify Dostoevsky state is intact before starting:

   ```bash
   ls "/Users/aienvironment/Desktop/AI Assembly/projects/phase-l-dostoevsky/inputs/dossiers/_dr_prompts/"
   ls "/Users/aienvironment/Desktop/AI Assembly/projects/phase-l-dostoevsky/inputs/dossiers/"  # may or may not have the tailored prompt
   ```

   Dostoevsky §1 and §2 claude DR outputs live on user's Desktop at `~/Desktop/dosto_brief+section1_opus4.{6,7}.md` and `~/Desktop/dosto_brief+section2_opus4.{6,7}.md`. These are NOT in the project folder yet; they will migrate in during Phase N. Do not touch them outside Phase N.

4. Confirm the personas venv + base dependencies:

   ```bash
   cd personas
   venv/bin/python -c "import anthropic; import jinja2; import pydantic; print('OK')"
   venv/bin/python -m pytest tests/ --collect-only   # baseline: confirm tests collect
   ```

5. Check nothing is uncommitted that would get swept up:

   ```bash
   git status --porcelain   # should be empty; if not, STOP and ask what to do
   ```

If any preflight step fails or surprises, stop and report.

## Phase list + dependencies

```
A. Preparation                     (no deps; reads code)
B. Path helper module              (A)
C. Synthetic test fixtures         (A)
D. Delete Ibn Battuta              (A)
E. Header + footer Jinja           (B)
F. Splitter helper                 (B, E)
G. Phase 0.5 integration           (B, F)
H. perplexity_split fallback       (B)
I. DR dossier validator            (B)
J. Chunk runner                    (B, H)
K. Pipeline resume + mode detect   (B, I, J)
L. Manifest + telemetry            (B)
M. Miscellaneous bundles           (B)
N. Migration script + execute      (all prior)
O. End-to-end testing              (N)
P. Documentation sweep             (O)
Q. Final verification              (P)
```

Execute in order A → Q. Commit per phase. Push after C, F, J, N, P.

---

## Phase A — Preparation

**Effort:** ~30 min. No commits.

### A.1 — Read current-state code

Spend time reading these files to ground your mental model of what exists today:

- `personas/flows/shared/project_root.py` — Tier 3 resolver
- `personas/flows/shared/io.py` — atomic writes, prompt loader, voice input loader
- `personas/flows/shared/clients.py` — `call_claude`, `call_perplexity`, `call_gemini`, `call_openai` signatures and shapes
- `personas/flows/shared/perplexity_split.py` — current split_dossier implementation
- `personas/flows/shared/dr_validation.py` — current validator
- `personas/flows/shared/chunk_runner.py` — per-chunk merge runner; this is the load-bearing change target
- `personas/flows/shared/prompt_render.py` — Jinja2 renderer
- `personas/run_pass0a_voice_config.py` — intake
- `personas/run_phase0_1_research.py` — Phase 0.5
- `personas/run_pass_0b_tailor.py` — tailoring pass (should exist post cleanup-3)
- `personas/run_pass_1_all.py` — chunked merge orchestrator
- `personas/run_pass_1_7.py` — coherence pass
- `personas/run_persona_pipeline.py` — main pipeline runner
- `personas/scripts/validate_dr_dossier.py` — standalone validator
- `personas/tests/fixtures/ibn_battuta/` — existing fixtures (to be deleted)
- `personas/flows/shared/prompts/pass_0b_header.md` — header template to extend
- `personas/flows/shared/prompts/pass_0b_footer.md` — footer template to extend
- `personas/flows/shared/prompts/pass_0b_tailor.md` — tailoring pass prompt

Build a path inventory: every hardcoded path string or f-string referencing `inputs/voices/`, `inputs/dossiers/`, `runs/<slug>/`, `01_research/`, `02_passes/`, etc. Enumerate them — you'll need this for Phase B's `paths.py` module.

### A.2 — Note path inventory

Write what you find to `_workspace/planning/SONNET_PATH_INVENTORY.md`. Short form: `<file>:<line> — <path pattern>`. Examples:

```
personas/run_persona_pipeline.py:45 — f"{project_root}/inputs/voices/{slug}.json"
personas/flows/shared/chunk_runner.py:75 — research / "claude_dr_dossier.md"
personas/run_phase0_1_research.py:120 — project_root / "inputs" / "dossiers" / "_dr_prompts" / f"{slug}_dr_prompt.md"
...
```

This becomes your working document — every entry needs a corresponding replacement in Phase B's `paths.py`. When inventory is complete (grep-based enumeration across `personas/` should find them all), proceed.

### A.3 — Expected phase scope confirmation

Confirm with yourself:
- You have the path inventory.
- You know which files this session modifies.
- You know which files this session leaves alone (see "What NOT to touch" at bottom of this plan).

If anything is missing, flag and ask before proceeding to Phase B.

---

## Phase B — Path helper module

**Effort:** ~45 min. Commits: 1.

### B.1 — Create `personas/flows/shared/paths.py`

New module. Centralizes every path constant. All runners import from here; no string concatenation outside this module.

Structure:

```python
"""Canonical paths for the persona pipeline.

Every path reference goes through a function in this module. Runners call
paths.voice_config(slug) — not string concatenation. Changes to layout
conventions live here alone.

See _workspace/planning/SONNET_EXECUTION_PHASE_B_RESTRUCTURE.md for the
full layout spec.
"""

from __future__ import annotations
from pathlib import Path
from .project_root import get_project_root


# ==== Voice root + subfolder roots ====

def voice_root(slug: str, project_root: Path | None = None) -> Path:
    """$PROJECT_ROOT/voices/<slug>/"""
    return _resolve(project_root) / "voices" / slug

def intake_dir(slug, project_root=None) -> Path:
    """voices/<slug>/00_intake/"""
    return voice_root(slug, project_root) / "00_intake"

def research_dir(slug, project_root=None) -> Path:
    """voices/<slug>/01_research/"""
    return voice_root(slug, project_root) / "01_research"

def merge_dir(slug, project_root=None) -> Path:
    return voice_root(slug, project_root) / "02_merge"

def corpus_dir(slug, project_root=None) -> Path:
    return voice_root(slug, project_root) / "03_corpus"

def generation_dir(slug, project_root=None) -> Path:
    return voice_root(slug, project_root) / "04_generation"

def validation_dir(slug, project_root=None) -> Path:
    return voice_root(slug, project_root) / "05_validation"

def derive_dir(slug, project_root=None) -> Path:
    return voice_root(slug, project_root) / "06_derive"


# ==== Intake files ====

def non_human_grounding(slug, project_root=None) -> Path:
    return intake_dir(slug, project_root) / "01_non_human_grounding.md"

def voice_config(slug, project_root=None) -> Path:
    return intake_dir(slug, project_root) / "02_voice_config.json"

def review_doc(slug, project_root=None) -> Path:
    return intake_dir(slug, project_root) / "03_review_doc.md"


# ==== Research files ====

def perplexity_dossier(slug, project_root=None) -> Path:
    return research_dir(slug, project_root) / "01_perplexity_dossier.json"

def gemini_broad_scan(slug, project_root=None) -> Path:
    return research_dir(slug, project_root) / "02_gemini_broad_scan.json"

def dr_prompts_dir(slug, project_root=None) -> Path:
    return research_dir(slug, project_root) / "03_dr_prompts"

def monolithic_dr_prompt(slug, project_root=None) -> Path:
    return dr_prompts_dir(slug, project_root) / "01_monolithic_dr_prompt.md"

def tailoring_notes(slug, project_root=None) -> Path:
    return dr_prompts_dir(slug, project_root) / "02_tailoring_notes.json"

def section_dr_prompt(slug, n: int, project_root=None) -> Path:
    assert 1 <= n <= 6, f"section_index must be 1-6, got {n}"
    # §1 → 03_section_1_dr_prompt.md, §2 → 04_..., ... §6 → 08_...
    prefix = n + 2   # 1→3, 2→4, ..., 6→8
    return dr_prompts_dir(slug, project_root) / f"{prefix:02d}_section_{n}_dr_prompt.md"

def dr_dossier_dir(slug, project_root=None) -> Path:
    return research_dir(slug, project_root) / "04_dr_dossier"

def section_dr_dossier(slug, n: int, project_root=None) -> Path:
    assert 1 <= n <= 6, f"section_index must be 1-6, got {n}"
    return dr_dossier_dir(slug, project_root) / f"{n:02d}_section_{n}.md"

def concat_claude_dr(slug, project_root=None) -> Path:
    """Monolithic fallback — concatenation of 6 section files."""
    return dr_dossier_dir(slug, project_root) / "07_concat_claude_dr.md"


# ==== Merge files (Pass 1.1–1.7) ====

_MERGE_CHUNK_NAMES = {
    1: "biographical", 2: "intellectual", 3: "reasoning",
    4: "voice", 5: "boundaries", 6: "corpus",
}

def merge_chunk(slug, chunk_num: int, project_root=None) -> Path:
    assert 1 <= chunk_num <= 6
    name = _MERGE_CHUNK_NAMES[chunk_num]
    return merge_dir(slug, project_root) / f"{chunk_num:02d}_pass_1_{chunk_num}_{name}.json"

def merge_coherence(slug, project_root=None) -> Path:
    return merge_dir(slug, project_root) / "07_pass_1_7_coherence.json"

def merged_dossier(slug, project_root=None) -> Path:
    return merge_dir(slug, project_root) / "08_merged_dossier.json"


# ==== Corpus files ====

def primary_texts(slug, project_root=None) -> Path:
    return corpus_dir(slug, project_root) / "01_primary_texts.json"

def excerpt_selections(slug, project_root=None) -> Path:
    return corpus_dir(slug, project_root) / "02_excerpt_selections.json"


# ==== Generation files (Pass 2–6 + CT) ====

def pass_2(slug, project_root=None) -> Path:
    return generation_dir(slug, project_root) / "01_pass_2_identity_boundaries.json"

def ct_after_pass_2(slug, project_root=None) -> Path:
    return generation_dir(slug, project_root) / "02_ct_after_pass_2.json"

def pass_3(slug, project_root=None) -> Path:
    return generation_dir(slug, project_root) / "03_pass_3_intellectual_core.json"

def ct_after_pass_3(slug, project_root=None) -> Path:
    return generation_dir(slug, project_root) / "04_ct_after_pass_3.json"

def pass_4a(slug, project_root=None) -> Path:
    return generation_dir(slug, project_root) / "05_pass_4a_voice.json"

def ct_after_pass_4a(slug, project_root=None) -> Path:
    return generation_dir(slug, project_root) / "06_ct_after_pass_4a.json"

def pass_4b(slug, project_root=None) -> Path:
    return generation_dir(slug, project_root) / "07_pass_4b_artifact.json"

def ct_after_pass_4b(slug, project_root=None) -> Path:
    return generation_dir(slug, project_root) / "08_ct_after_pass_4b.json"

def pass_5(slug, project_root=None) -> Path:
    return generation_dir(slug, project_root) / "09_pass_5_engagement.json"

def pass_6(slug, project_root=None) -> Path:
    return generation_dir(slug, project_root) / "10_pass_6_corpus.json"


# ==== Validation files (Pass 7.*) ====

def pass_7_pre(slug, project_root=None) -> Path:
    return validation_dir(slug, project_root) / "01_pass_7_pre_citation.json"

def pass_7_anachronism(slug, project_root=None) -> Path:
    return validation_dir(slug, project_root) / "02_pass_7_anachronism.json"

def pass_7a(slug, project_root=None) -> Path:
    return validation_dir(slug, project_root) / "03_pass_7a_cross_model.json"

def pass_7b(slug, project_root=None) -> Path:
    return validation_dir(slug, project_root) / "04_pass_7b_smoke_test.json"

def pass_7c(slug, project_root=None) -> Path:
    return validation_dir(slug, project_root) / "05_pass_7c_negative.json"


# ==== Derive files ====

def provocateur_profile(slug, project_root=None) -> Path:
    return derive_dir(slug, project_root) / "01_provocateur_profile.json"

def evaluation_rubric(slug, project_root=None) -> Path:
    return derive_dir(slug, project_root) / "02_evaluation_rubric.json"


# ==== Voice root files ====

def assembled_card(slug, project_root=None) -> Path:
    return voice_root(slug, project_root) / "07_persona_card_assembled.json"

def manifest(slug, project_root=None) -> Path:
    return voice_root(slug, project_root) / "_manifest.json"


# ==== Project-level files (NOT per-voice) ====

def conference_facts(project_root=None) -> Path:
    return _resolve(project_root) / "conference_facts.json"

def audience_profile(project_root=None) -> Path:
    return _resolve(project_root) / "audience_profile.json"

def panel_roster(project_root=None) -> Path:
    return _resolve(project_root) / "panel_roster.json"


# ==== Helpers ====

def _resolve(project_root: Path | None) -> Path:
    if project_root is None:
        project_root = get_project_root()
    return Path(project_root)

def ensure_voice_dirs(slug, project_root=None) -> None:
    """Create the 7 pass-group subfolders + dr_prompts/ + dr_dossier/."""
    for mk in [intake_dir, research_dir, merge_dir, corpus_dir,
               generation_dir, validation_dir, derive_dir]:
        mk(slug, project_root).mkdir(parents=True, exist_ok=True)
    dr_prompts_dir(slug, project_root).mkdir(parents=True, exist_ok=True)
    dr_dossier_dir(slug, project_root).mkdir(parents=True, exist_ok=True)
```

This is not the final file — you may need to add helpers as you discover more paths used in runners. But these cover the documented layout.

### B.2 — Write unit tests

Create `personas/tests/test_paths.py` with coverage for:
- Each path function returns under `voice_root(slug)`.
- Numbering is consistent (e.g. `section_dr_prompt(slug, 3)` returns path containing `05_section_3`).
- `ensure_voice_dirs` creates all 7 + 2 = 9 subfolders without error, idempotent.
- `project_root=None` resolves via `get_project_root()`.

### B.3 — Verify + commit

```bash
cd "/Users/aienvironment/Desktop/AI Assembly/code"
cd personas && venv/bin/python -m pytest tests/test_paths.py -v
```

All tests pass.

Commit:

```
feat(phase-b/restructure-B): centralize voice paths in flows/shared/paths.py

New module consolidates every path reference used across the personas
pipeline into canonical functions. Replaces string concatenation at
callsites in subsequent phases. Implements per-voice folder layout with
numbered pass-group subfolders per SONNET_EXECUTION_PHASE_B_RESTRUCTURE.md.

Covered: intake/research/merge/corpus/generation/validation/derive dirs;
all per-pass output paths; dr_prompts + dr_dossier subdirs with
per-section accessors; manifest + assembled_card at voice root.

Tests: personas/tests/test_paths.py covers accessor shapes, numeric
prefix correctness, ensure_voice_dirs idempotency.
```

---

## Phase C — Synthetic test fixtures

**Effort:** ~30 min. Commits: 1.

### C.1 — Create synthetic voice fixture

Build at `personas/tests/fixtures/synthetic_voice/` a minimal voice-folder structure that exercises chunk_runner + perplexity_split + validator. NOT a real voice — clearly fake.

```
personas/tests/fixtures/synthetic_voice/
  00_intake/
    02_voice_config.json         # type=human, voice_mode=philosophical,
                                 # name="Test Subject Alpha", voice_slug="test_subject_alpha"
                                 # (no non_human_grounding, no review_doc needed for plumbing tests)
  01_research/
    01_perplexity_dossier.json   # content: ~4KB, 6 sections with standard headings,
                                 #   enough to exercise perplexity_split
    02_gemini_broad_scan.json    # content: ~2KB flat broad-scan JSON
    04_dr_dossier/
      01_section_1.md            # ~1KB each, placeholder prose about "Test Subject Alpha"
      02_section_2.md            # NOT real scholarship
      03_section_3.md
      04_section_4.md
      05_section_5.md
      06_section_6.md
```

Content for `01_perplexity_dossier.json` — needs to match what the current Perplexity output looks like (check an existing fixture or a recent run's Perplexity output as reference). Keep it small but structurally valid:

```json
{
  "content": "## 1. BIOGRAPHICAL FOUNDATION\n\n[Test content: biographical scaffolding for Test Subject Alpha...]\n\n## 2. INTELLECTUAL FRAMEWORK\n\n[Test content: intellectual commitments...]\n\n## 3. REASONING PATTERNS\n\n[...]\n\n## 4. VOICE AND STYLE\n\n[...]\n\n## 5. HISTORICAL + CONCEPTUAL BOUNDARIES\n\n[...]\n\n## 6. PRIMARY TEXTS\n\n[...]\n",
  "citations": [],
  "usage": {"total_tokens": 1000}
}
```

Similar for `02_gemini_broad_scan.json` — flat content block, standard shape.

Section files: ~1KB of prose per section, recognizable placeholders ("Test Subject Alpha exhibits..."). Include a `[quote: Test Work, §1]` marker and one `[~uncertain]` marker in each section to exercise the tag-parsing paths.

### C.2 — README in fixture dir

Create `personas/tests/fixtures/README.md`:

```markdown
# Test fixtures

## synthetic_voice/

A minimal, clearly-fake voice used to exercise pipeline plumbing in unit
tests. NOT a real research subject. If a test fails content-validation
(e.g. "Kasatkina not mentioned in §2"), the test is misspecified — it's
reading the synthetic fixture as if it were a real voice.

**Do NOT edit synthetic_voice/ files without updating corresponding tests.**
Content is hand-crafted to exercise specific code paths (heading regex,
tag markers, section boundary detection).

## Integration fixtures

Unit tests use synthetic_voice. Integration tests exercise real project
data at `$AI_ASSEMBLY_INTEGRATION_PROJECT/voices/<slug>/` and are gated
via `@pytest.mark.integration` + env var. Default pytest runs skip them.
Run integration tests with:

    AI_ASSEMBLY_INTEGRATION_PROJECT=projects/phase-l-dostoevsky pytest -m integration
```

### C.3 — Commit

```
feat(phase-b/restructure-C): synthetic test fixture replacing Ibn Battuta

Creates personas/tests/fixtures/synthetic_voice/ — a small, clearly-fake
voice fixture (Test Subject Alpha) used to exercise chunk_runner,
perplexity_split, and validator plumbing. Not real research content;
not a claim to be any historical figure.

Ibn Battuta fixtures deleted in the next phase. Real-voice research
content no longer lives in the code repo per Tier 3 separation.

Integration tests gated via @pytest.mark.integration + env var.
README at personas/tests/fixtures/README.md explains the split.
```

---

## Phase D — Delete Ibn Battuta fixtures

**Effort:** ~10 min. Commits: 1.

```bash
cd "/Users/aienvironment/Desktop/AI Assembly/code"
git rm -r personas/tests/fixtures/ibn_battuta/
```

Confirm nothing else references `ibn_battuta` under `personas/`:

```bash
grep -rn "ibn_battuta" personas/ --include="*.py" --include="*.md" --include="*.json" --include="*.txt"
```

If any matches appear in code (not docs), they need updating. Current expected state: some docs in `_workspace/planning/` + `docs/` reference Ibn Battuta fixtures; those get updated in Phase P (docs sweep), not now.

Commit:

```
feat(phase-b/restructure-D): delete Ibn Battuta test fixtures from code repo

Per Tier 3 separation: real-voice research content (Perplexity dossier,
Gemini scan) does not live in the code repo. Ibn Battuta is a production
panel voice; his actual build regenerates fresh when his Athens queue
slot opens.

The old fixtures predate the Phase B Pass 0b rewrites (thematic-question
restructure, stripped field-name leaks, softened quotas). Reusing them
would pre-position pre-Phase-B biases into his production research.
Regeneration cost (~$10) is worth avoiding that contamination.

Synthetic replacement at personas/tests/fixtures/synthetic_voice/ (landed
in Phase C).
```

Push after Phase D so B+C+D are preserved:

```bash
git push origin phase-b-rebuild
```

---

## Phase E — Header + footer Jinja conditionals

**Effort:** ~45 min. Commits: 1.

### E.1 — Extend `pass_0b_header.md`

Current header lives at `personas/flows/shared/prompts/pass_0b_header.md`. It's written for monolithic paste. Add Jinja conditionals on two new template variables:

- `section_mode: bool` — if true, per-section mode
- `section_index: int` — 1–6 when `section_mode=true`, else None/unset

The header must branch its CONTENT based on section_mode. Fork logic:

**Monolithic branch** (`section_mode` is falsy): keep existing text verbatim. Operators using monolithic-paste path see the original text.

**Section branch** (`section_mode=true`): emit a per-section preamble.

**IMPORTANT — Jinja StrictUndefined interaction (Phase M.3).** Once `StrictUndefined` lands, any template access to an undefined variable errors. The existing monolithic render path doesn't pass `section_mode` (it didn't exist before this work), so `{% if section_mode %}` would error under StrictUndefined. Mitigation: start the template with a default-to-false guard:

```jinja2
{# Guard: default section_mode to false so monolithic renders don't need to pass it. #}
{% set section_mode = section_mode | default(false) %}
{% set section_index = section_index | default(0) %}
```

Place these two `{% set %}` lines at the very top of `pass_0b_header.md` (and mirror the `section_mode` guard at the top of `pass_0b_footer.md`). After this guard, the rest of the template can branch on `section_mode` without fear of StrictUndefined errors when callers don't set it.

**Rest of the template branches as follows:**

```jinja2
{% if section_mode %}
PREAMBLE — BEFORE PASTING INTO CLAUDE.AI (Section {{ section_index }} of 6)

{% if section_index == 1 %}
1. Open claude.ai and select **Claude Opus 4.6** (Phase B empirically validated; 4.7 acceptable if 4.6 unavailable).
2. Enable **Extended Thinking** and **Deep Research** (both must be on).
3. Paste everything below the dashed line as your user message. Subsequent sections can be pasted in the same thread or in fresh threads — operator's choice.
{% else %}
1. Continue in the thread of your choice (same thread as prior sections for cross-section coherence, or fresh thread for independent sampling). Model and toggles stay as Section 1.
2. Paste everything below the dashed line as your user message.
{% endif %}

{{ (4 if section_index == 1 else 3) }}. Expected runtime: **20–40 minutes** per section. **If past 60 minutes without draft streaming visible, cancel** — that's the convergence-trap signature. Retry with a fresh thread or alternate model.

{{ (5 if section_index == 1 else 4) }}. Save the download as `$AI_ASSEMBLY_PROJECT_ROOT/voices/{{ voice_slug }}/01_research/04_dr_dossier/{{ "%02d" | format(section_index) }}_section_{{ section_index }}.md`.

{{ (6 if section_index == 1 else 5) }}. Validate before proceeding: `python3 personas/scripts/validate_dr_dossier.py "$AI_ASSEMBLY_PROJECT_ROOT/voices/{{ voice_slug }}/01_research/04_dr_dossier/{{ "%02d" | format(section_index) }}_section_{{ section_index }}.md"`

{% if section_index < 6 %}
{{ (7 if section_index == 1 else 6) }}. **Do NOT run the pipeline yet.** Paste `{{ voice_slug }}_section_{{ section_index + 1 }}_dr_prompt.md` next. The pipeline runs after all 6 sections are saved.
{% else %}
{{ (7 if section_index == 1 else 6) }}. All 6 sections now collected. Run the pipeline: `cd personas && venv/bin/python run_persona_pipeline.py "{{ name }}"` (pipeline auto-detects per-section mode).
{% endif %}

---

RESEARCH DISCIPLINE — READ FIRST

[... existing research discipline bullets, with these edits for section mode:]
- "Synthesis trigger. When the thematic area below has substantive material sufficient to answer its questions, stop researching and synthesize."
  (replace "each of the six thematic areas" with "the thematic area")
- "Depth over length. Produce what the research supports, honestly. The thematic area should receive substantive coverage — but 'substantive' is what the record supports, not a padding target."
  (replace "six thematic areas should each receive" with "the thematic area should receive")

---

{% if wikipedia_url and section_index == 1 %}
Starting point for your research: {{ wikipedia_url }} (verify, expand, find what Wikipedia misses or oversimplifies).
{% endif %}

{% else %}
[... existing monolithic preamble text unchanged ...]
{% endif %}
```

**Important:** preserve the existing monolithic branch verbatim (copy it into the `{% else %}` block). The monolithic fallback path still uses this file via Jinja context `section_mode=False`.

Also note: the Option X decision means every message in a single-thread flow gets the FULL header (not a stub for §2–§6). The conditional logic above handles this correctly — §2–§6 messages get preamble steps renumbered 1–6 (not 1–7) because preamble step 1+2 merge into one "continue in thread" instruction.

### E.2 — Extend `pass_0b_footer.md`

One-line edit. Current footer says:

```
A research dossier only. NOT a persona card — no "Field NN:" structure, no "Block" headings. Organise under six thematic area headings matching the list above (the `dr_validation.py` check is lenient on format but strict on persona-card-shape leakage).
```

Under `section_mode`, replace "six thematic area headings matching the list above" with "the thematic area heading matching the area above":

```jinja2
{% if section_mode %}
A research dossier only. NOT a persona card — no "Field NN:" structure, no "Block" headings. Organise under the thematic area heading matching the area above (the `dr_validation.py` check is lenient on format but strict on persona-card-shape leakage).
{% else %}
A research dossier only. NOT a persona card — no "Field NN:" structure, no "Block" headings. Organise under six thematic area headings matching the list above (the `dr_validation.py` check is lenient on format but strict on persona-card-shape leakage).
{% endif %}
```

### E.3 — Test: render monolithic mode, confirm byte-identical to prior output

Construct a minimal test:

```python
# personas/tests/test_header_footer_modes.py
from flows.shared.prompt_render import render_prompt

def test_monolithic_unchanged():
    # Render with section_mode=False and a known set of variables;
    # compare output against a golden file captured before these edits.
    rendered = render_prompt(
        "pass_0b_header.md",
        voice_slug="test", name="Test", type="human", subtype=None,
        corpus_constraint="full", hostile_sources=False,
        wikipedia_url="https://en.wikipedia.org/wiki/Test",
        section_mode=False, section_index=None,
    )
    # Spot-check: contains "six thematic areas"; contains "<slug>_claude_dr.md"
    assert "six thematic areas below" in rendered
    assert "claude_dr.md" in rendered
    assert "Section 1 of 6" not in rendered

def test_section_mode_index_1():
    rendered = render_prompt(
        "pass_0b_header.md",
        voice_slug="test", name="Test", type="human", subtype=None,
        corpus_constraint="full", hostile_sources=False,
        wikipedia_url="https://en.wikipedia.org/wiki/Test",
        section_mode=True, section_index=1,
    )
    assert "Section 1 of 6" in rendered
    assert "01_section_1.md" in rendered
    assert "Do NOT run the pipeline yet" in rendered
    assert "run_persona_pipeline.py" not in rendered
    assert "the thematic area below" in rendered
    assert "Wikipedia" in rendered or "wikipedia.org" in rendered

def test_section_mode_index_6():
    rendered = render_prompt(
        "pass_0b_header.md",
        voice_slug="test", name="Test", type="human", subtype=None,
        corpus_constraint="full", hostile_sources=False,
        wikipedia_url="https://en.wikipedia.org/wiki/Test",
        section_mode=True, section_index=6,
    )
    assert "Section 6 of 6" in rendered
    assert "06_section_6.md" in rendered
    assert "run_persona_pipeline.py" in rendered
    assert "Do NOT run the pipeline yet" not in rendered
```

Run:

```bash
cd personas && venv/bin/python -m pytest tests/test_header_footer_modes.py -v
```

All tests pass.

### E.4 — Commit

```
feat(phase-b/restructure-E): pass_0b header + footer Jinja conditionals for section mode

pass_0b_header.md and pass_0b_footer.md now branch on two new Jinja
template variables:
- section_mode: bool
- section_index: int (1-6, only when section_mode=True)

Monolithic branch preserved verbatim (section_mode=False). Section
branch:
- Preamble renumbers correctly for §1 (full setup) vs §2-§6 (continue-in-thread)
- Filename guidance per section
- Runtime envelope 20-40 min (was 20-90 monolithic)
- Cancel threshold 60 min (was 2h monolithic)
- Pipeline invocation: "don't run" for §1-§5; "now run" for §6
- "The thematic area below" (singular) replaces "six thematic areas"
- Wikipedia URL only in §1

Tests at personas/tests/test_header_footer_modes.py exercise both modes
and assert per-section-index correctness.
```

---

## Phase F — Splitter helper

**Effort:** ~60 min. Commits: 1.

### F.1 — Create `personas/scripts/split_tailored_prompt.py`

Purpose: take the tailored monolithic DR prompt (produced by existing Opus 4.7 tailoring pass) and slice it into 6 section-specific prompt files, each wrapped with mode-aware header + footer.

```python
"""Split the tailored monolithic DR prompt into 6 per-section files.

Runs after Pass 0b tailoring completes. The tailoring pass produces one
monolithic prompt with cross-section-coherent follow-up questions injected
at six COVERAGE-NOTE-PLACEHOLDER slots. This script slices that output
into six section files, each wrapped with mode-aware header + footer.

Operator then pastes each file in turn into claude.ai. Pipeline reads
the resulting 6 saved DR section files via chunk_runner's per-section
mode.
"""
from __future__ import annotations
import argparse
import re
import sys
from pathlib import Path

from flows.shared import paths
from flows.shared.io import load_voice_input
from flows.shared.prompt_render import render_prompt
from flows.shared.project_root import get_project_root


SECTION_HEADING_RE = re.compile(
    r"^(## Section (\d+): [A-Z][A-Z +]+[A-Z])$",
    re.MULTILINE,
)


def split_monolithic(monolithic_text: str) -> dict[int, str]:
    """Return {section_number: section_body_including_heading}.

    Raises ValueError if fewer or more than 6 sections found, or if
    section numbering is non-contiguous.
    """
    matches = list(SECTION_HEADING_RE.finditer(monolithic_text))
    if len(matches) != 6:
        raise ValueError(
            f"Expected 6 section headings, found {len(matches)}. "
            f"Headings: {[m.group(1) for m in matches]}"
        )

    # Verify numbering 1..6 contiguous
    numbers = [int(m.group(2)) for m in matches]
    if numbers != list(range(1, 7)):
        raise ValueError(
            f"Section numbering must be 1..6 contiguous, got {numbers}"
        )

    sections = {}
    for i, m in enumerate(matches):
        start = m.start()
        end = matches[i+1].start() if i+1 < len(matches) else len(monolithic_text)
        sections[i+1] = monolithic_text[start:end].strip() + "\n"
    return sections


def wrap_section(
    section_body: str, section_index: int, voice_config, wikipedia_url: str | None,
) -> str:
    """Wrap a section body with mode-aware header + footer via Jinja."""
    header = render_prompt(
        "pass_0b_header.md",
        voice_slug=voice_config["voice_slug"],
        name=voice_config["name"],
        type=voice_config["type"],
        subtype=voice_config.get("subtype"),
        voice_mode=voice_config.get("voice_mode"),
        corpus_constraint=voice_config.get("corpus_constraint", "full"),
        hostile_sources=voice_config.get("hostile_sources", False),
        wikipedia_url=wikipedia_url,
        section_mode=True,
        section_index=section_index,
    )
    footer = render_prompt(
        "pass_0b_footer.md",
        voice_slug=voice_config["voice_slug"],
        corpus_constraint=voice_config.get("corpus_constraint", "full"),
        hostile_sources=voice_config.get("hostile_sources", False),
        display_name_with_hint=voice_config["name"],  # TODO J.2
        section_mode=True,
    )
    # Add provenance header (item bundled from OPEN_ITEMS)
    provenance = (
        f"<!-- PROMPT_VERSION: pass_0b_section_mode_v1 "
        f"| VOICE_SLUG: {voice_config['voice_slug']} "
        f"| SECTION: {section_index} "
        f"| RENDERED_AT: {__import__('datetime').datetime.now().isoformat()} -->\n\n"
    )
    return provenance + header + "\n\n---\n\n" + section_body + "\n\n---\n\n" + footer


def split_tailored_prompt(voice_slug: str, project_root: Path | None = None) -> list[Path]:
    """Slice the tailored monolithic DR prompt into 6 section files."""
    project_root = project_root or get_project_root()

    monolithic_path = paths.monolithic_dr_prompt(voice_slug, project_root)
    if not monolithic_path.exists():
        raise FileNotFoundError(
            f"Tailored monolithic prompt not found: {monolithic_path}. "
            "Run Phase 0.5 tailoring before splitting."
        )

    monolithic_text = monolithic_path.read_text(encoding="utf-8")
    sections = split_monolithic(monolithic_text)

    voice_config = load_voice_input(voice_slug, project_root)
    wikipedia_url = voice_config.get("wikipedia_url")

    written = []
    for n in range(1, 7):
        out_path = paths.section_dr_prompt(voice_slug, n, project_root)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        wrapped = wrap_section(sections[n], n, voice_config, wikipedia_url)
        out_path.write_text(wrapped, encoding="utf-8")
        written.append(out_path)
        print(f"  wrote {out_path.name}", file=sys.stderr)

    return written


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("voice_slug", help="e.g. fyodor_dostoevsky")
    parser.add_argument("--project", type=Path, default=None)
    args = parser.parse_args()

    paths_written = split_tailored_prompt(args.voice_slug, args.project)
    print(f"\nWrote {len(paths_written)} section prompts.", file=sys.stderr)


if __name__ == "__main__":
    main()
```

### F.2 — Unit tests

Create `personas/tests/test_split_tailored_prompt.py`:

```python
# Build a synthetic monolithic string with 6 section headings + content;
# call split_monolithic; assert 6 sections returned, each containing its
# heading + body; assert header wrapping injects correct section_index.
```

Run tests. All pass.

### F.3 — Manual verification against existing Dostoevsky tailored prompt

IF a tailored monolithic prompt exists at `projects/phase-l-dostoevsky/inputs/dossiers/_dr_prompts/fyodor_dostoevsky_dr_prompt.md` (old path — pre-restructure), do a dry-run test:

```bash
cd personas
# Temporarily test split_monolithic on the real file content
venv/bin/python -c "
from pathlib import Path
from scripts.split_tailored_prompt import split_monolithic
text = Path('/Users/aienvironment/Desktop/AI Assembly/projects/phase-l-dostoevsky/inputs/dossiers/_dr_prompts/fyodor_dostoevsky_dr_prompt.md').read_text()
sections = split_monolithic(text)
print(f'Found {len(sections)} sections')
for n, body in sections.items():
    print(f'  §{n}: {body[:80]}... ({len(body)} chars)')
"
```

Expected: 6 sections found, each with its biographical/intellectual/etc heading visible. If not, investigate whether the section regex needs adjustment (e.g. different heading patterns in non-human organism / system / fictional type files).

Remember: the monolithic prompt contains type-specific section names. For human: "BIOGRAPHICAL FOUNDATION", "INTELLECTUAL FRAMEWORK", etc. For non-human organism: "ECOLOGICAL FOUNDATION", "PERCEPTUAL WORLD", etc. The regex `r"^## Section (\d+): [A-Z][A-Z +]+[A-Z]$"` matches all variants — verify against all 4 type templates (`pass_0b_human.md`, `pass_0b_non_human_organism.md`, `pass_0b_non_human_system.md`, `pass_0b_fictional.md`) before claiming regex is complete.

### F.4 — Commit

```
feat(phase-b/restructure-F): split_tailored_prompt.py — six section files

New script at personas/scripts/split_tailored_prompt.py slices the tailored
monolithic DR prompt (produced by existing Opus 4.7 tailoring pass) into
six section-specific prompt files. Each section gets:
- Section-mode header via Jinja (per-section filename, runtime envelope,
  pipeline invocation, "the thematic area" singular language)
- The tailored section body (with follow-up questions already injected)
- Section-mode footer
- Provenance header (PROMPT_VERSION | VOICE_SLUG | SECTION | RENDERED_AT)

Regex matches all four type-template heading families (human /
non-human organism / non-human system / fictional). Splitter errors out
if section count != 6 or numbering is non-contiguous.

Next phase (G) invokes this script from run_phase0_1_research.py after
tailoring.
```

---

## Phase G — Phase 0.5 integration

**Effort:** ~30 min. Commits: 1.

### G.1 — Integrate splitter into `run_phase0_1_research.py`

After the existing tailoring invocation (Opus 4.7 produces monolithic tailored prompt), invoke the splitter. Example pseudo-code:

```python
# ... existing Pass 0b tailoring call produces tailored_monolithic ...
monolithic_path = paths.monolithic_dr_prompt(voice_slug, project_root)
monolithic_path.parent.mkdir(parents=True, exist_ok=True)
monolithic_path.write_text(tailored_monolithic, encoding="utf-8")

# NEW: split into 6 section files
from scripts.split_tailored_prompt import split_tailored_prompt
section_paths = split_tailored_prompt(voice_slug, project_root)

print_next_steps_sectioned(voice_slug, section_paths)
```

### G.2 — Rewrite NEXT STEPS stamp

Replace the current NEXT STEPS print block (which mentions "Wait 60-180 min" and references monolithic paste) with:

```
NEXT STEPS — manual Claude Deep Research

Phase 0.5 research complete. Tailored monolithic prompt at:
  {monolithic_path}

Split into 6 paste-ready section prompts at:
  voices/{voice_slug}/01_research/03_dr_prompts/
    03_section_1_dr_prompt.md   ← paste these
    04_section_2_dr_prompt.md
    05_section_3_dr_prompt.md
    06_section_4_dr_prompt.md
    07_section_5_dr_prompt.md
    08_section_6_dr_prompt.md

WORKFLOW:

1. Open claude.ai, select Opus 4.6, enable Extended Thinking + Deep Research.

2. For each section (1 through 6):
   (a) Paste the section prompt into claude.ai.
   (b) Wait ~30 min for Research to complete (if past 60 min without draft
       streaming visible, cancel and retry).
   (c) Click "Download as .md" button to save the DR output.
   (d) Move/rename the download to:
       voices/{voice_slug}/01_research/04_dr_dossier/0N_section_N.md

3. Operator choice: paste all 6 in the same thread (for cross-section
   coherence) or in fresh threads per section (for independent sampling).
   Both paths are empirically validated.

4. When all 6 sections are saved, run the pipeline:
   cd personas && venv/bin/python run_persona_pipeline.py "{voice_name}" --project {project_root}

The pipeline auto-detects per-section mode from the dr_dossier/ directory
state. If fewer than 6 section files present, it errors with a clear
message indicating which section is missing.

For monolithic fallback (treat saved DR outputs as one file): concatenate
the 6 section files into voices/{voice_slug}/01_research/04_dr_dossier/07_concat_claude_dr.md
before running the pipeline. Chunk_runner auto-detects the monolithic
file if per-section files absent.
```

### G.3 — Add Perplexity retry-twice

Find the `_call_with_retry` wrapper or equivalent in `run_phase0_1_research.py` (or `flows/shared/clients.py`). Extend it to retry twice with exponential backoff (15s, then 60s) instead of one retry. Applies to both `call_perplexity` and `call_gemini`.

### G.4 — Commit

```
feat(phase-b/restructure-G): Phase 0.5 invokes splitter; NEXT STEPS rewritten

run_phase0_1_research.py now:
- Writes tailored monolithic to voices/<slug>/01_research/03_dr_prompts/01_monolithic_dr_prompt.md
- Invokes split_tailored_prompt after tailoring (six section files land in same dir)
- NEXT STEPS stamp rewritten: per-section paste workflow, runtime envelope
  20-40 min (not 20-90), cancel at 60 min (not 2h), save-to filename
  convention, pipeline auto-detect description

Closes OPEN_ITEMS stale "Wait 60-180 min" hardcode.

Perplexity + Gemini retries now twice (15s, 60s exponential) instead of
once. Closes OPEN_ITEMS "Perplexity retry: retry-twice" smaller improvement.
```

Push:

```bash
git push origin phase-b-rebuild
```

---

## Phase H — perplexity_split per-section fallback

**Effort:** ~20 min. Commits: 1.

### H.1 — Fix perplexity_split.py

Current behavior: `split_dossier(text)` returns `None` if ANY of the 6 section headings fail to match. Desired: recover per-section, return what was found.

```python
def split_dossier(text: str) -> dict[int, str]:
    """Split a Perplexity dossier into {section_number: content} dict.

    If some section headings fail to match, return whatever was found.
    Callers (chunk_runner) fall back to full dossier for sections that
    weren't extracted.
    """
    matches = list(SECTION_HEADING_RE.finditer(text))
    if not matches:
        return {}   # was None previously; now empty dict

    sections = {}
    for i, m in enumerate(matches):
        n = int(m.group(2))
        start = m.start()
        end = matches[i+1].start() if i+1 < len(matches) else len(text)
        sections[n] = text[start:end].strip() + "\n"

    return sections   # may have 1-6 keys
```

Update callers to handle dict-with-missing-keys gracefully (e.g. in chunk_runner, if `perplexity_sections.get(chunk_num)` is None, fall back to full dossier for that chunk).

### H.2 — Tests

Extend `personas/tests/test_perplexity_split.py` (or create if none exists):

- All 6 sections present → returns dict with 6 keys
- 5 sections present (§3 missing) → returns dict with 5 keys (missing §3)
- No sections present (malformed output) → returns empty dict
- Sections out of order → still parsed, keys are their real section numbers

### H.3 — Commit

```
feat(phase-b/restructure-H): perplexity_split per-section fallback

Changed split_dossier return type: now {int: str} dict with per-section
fallback instead of None-or-all-six all-or-nothing.

Callers (chunk_runner) gracefully fall back to full dossier for sections
that couldn't be extracted. Partial parse failures no longer block
per-section merge.

Closes OPEN_ITEMS "perplexity_split.split_dossier() per-section fallback"
smaller improvement.
```

---

## Phase I — DR dossier validator

**Effort:** ~45 min. Commits: 1.

### I.1 — Extend `personas/scripts/validate_dr_dossier.py`

Current: validates a monolithic file for 6-section structure + 15K word floor + persona-card-shape detection.

Desired: auto-detect whether the input path is:
- A single monolithic file (existing behavior) → apply monolithic validation
- A per-section file (`*_section_N.md`) → apply per-section validation
- A directory containing 6 section files → validate each independently

Detection logic:
- If path is a directory: look for `0N_section_N.md` files; validate each independently.
- If path is a file whose name matches `\d+_section_\d+\.md`: per-section validation.
- Else: monolithic validation.

Per-section validation:
- Word count floor: **1,500 words** (instead of 15,000 for monolithic)
- Heading check: exactly one `## Section N:` heading expected (not six)
- Persona-card-shape leakage check: unchanged
- Evidence-tag sanity: unchanged
- Provenance header check: if present, parse and report `VOICE_SLUG` / `SECTION`; mismatch is a warning not an error

### I.2 — Update `flows/shared/dr_validation.py` (if separate module)

Similar changes to the library module. CLI script calls the library.

### I.3 — Tests

Extend existing validator tests with per-section cases:
- Single valid section file → passes with per-section validation
- Directory with 6 section files → validates each, reports summary
- Directory with 5 section files → reports which section is missing
- Section file with malformed heading → fails per-section validation
- Monolithic file → existing behavior unchanged

### I.4 — Commit

```
feat(phase-b/restructure-I): validator auto-detects per-section vs monolithic

validate_dr_dossier.py and flows/shared/dr_validation.py now auto-detect
input type from path/filename pattern:
- Directory → validates each of 6 section files
- *_section_N.md → per-section validation (1,500-word floor)
- Else → monolithic validation (15,000-word floor, existing behavior)

Per-section word floor calibrated from Run 7 §1/§2 empirical evidence
(~3,700-6,500 words typical).

Missing section files detected and reported clearly.

Closes OPEN_ITEMS "section-level word-count floors in dr_validation.py"
smaller improvement.
```

---

## Phase J — Chunk runner

**Effort:** ~45 min. Commits: 1.

### J.1 — Update `flows/shared/chunk_runner.py`

Load order per chunk:

```python
def chunk_runner(
    name: str,
    chunk_num: int,  # 1..6
    voice_type: str,
    voice_mode: str | None,
    project_root: Path | None = None,
    mode: str = "auto",  # "per_section", "monolithic", or "auto"
) -> dict:
    """Run one Pass 1.N chunked merge. Returns the chunk's JSON output."""
    project_root = project_root or get_project_root()
    slug = voice_slug_from(name)  # existing helper

    # Detect mode if "auto"
    if mode == "auto":
        mode = detect_dr_mode(slug, project_root)

    # Perplexity: always per-section via perplexity_split (post Phase H)
    perplexity_full = paths.perplexity_dossier(slug, project_root).read_text()
    perplexity_sections = perplexity_split.split_dossier(perplexity_full)
    perplexity_text = perplexity_sections.get(chunk_num, perplexity_full)  # fallback to full if section missing

    # Claude DR: per-section if mode=per_section, else full monolithic
    if mode == "per_section":
        dr_path = paths.section_dr_dossier(slug, chunk_num, project_root)
    else:
        dr_path = paths.concat_claude_dr(slug, project_root)
        # Also accept legacy monolithic location; see I.4 for migration
    claude_dr_text = dr_path.read_text()

    # Gemini: always full (not sectioned by design)
    gemini_text = paths.gemini_broad_scan(slug, project_root).read_text()

    # ... existing merge prompt render + Opus 4.7 call + Pydantic validation ...


def detect_dr_mode(slug: str, project_root: Path) -> str:
    """Auto-detect per-section vs monolithic DR mode."""
    section_files = [
        paths.section_dr_dossier(slug, n, project_root) for n in range(1, 7)
    ]
    monolithic = paths.concat_claude_dr(slug, project_root)

    n_sections = sum(1 for p in section_files if p.exists())
    if n_sections == 6:
        return "per_section"
    elif n_sections == 0 and monolithic.exists():
        return "monolithic"
    elif n_sections > 0 and n_sections < 6:
        missing = [n for n, p in enumerate(section_files, 1) if not p.exists()]
        raise RuntimeError(
            f"Partial DR state: {n_sections}/6 section files present. "
            f"Missing: sections {missing}. Complete DR for these before running pipeline."
        )
    else:
        raise RuntimeError(
            f"No DR dossier found for {slug}. Expected either:\n"
            f"  (a) 6 section files at {paths.dr_dossier_dir(slug, project_root)}/\n"
            f"  (b) 1 monolithic file at {monolithic}"
        )
```

### J.2 — Update `run_pass_1_all.py`

Thin wiring — pass the `mode` flag through to each chunk_runner invocation. If mode is auto-detected by the orchestrator before spawning chunks, each chunk runs in consistent mode.

### J.3 — Integration test with synthetic fixture

Extend `personas/tests/` with a test that runs chunk_runner against the synthetic_voice fixture and asserts non-trivial chunk output for Pass 1.1. This exercises the full loader path end-to-end against deterministic test data.

Gate behind `@pytest.mark.integration` if it makes real LLM calls; use a mock `call_claude` if you want it in the default test set.

### J.4 — Commit

```
feat(phase-b/restructure-J): chunk_runner per-section load + mode detection

chunk_runner now:
- Loads per-section Claude DR from voices/<slug>/01_research/04_dr_dossier/0N_section_N.md
  when mode=per_section
- Falls back to monolithic at 07_concat_claude_dr.md when mode=monolithic
- Loads per-section Perplexity via perplexity_split (fallback to full dossier
  for sections where split failed)
- Always loads full Gemini broad scan (not sectioned by design — cross-cutting material)

detect_dr_mode helper auto-detects per-section vs monolithic based on
filesystem state; errors cleanly on partial state.

run_pass_1_all passes mode flag through to each chunk.

Closes OPEN_ITEMS chunk_runner "Line 75" pending code change.
```

Push:

```bash
git push origin phase-b-rebuild
```

---

## Phase K — Pipeline resume + mode detection

**Effort:** ~45 min. Commits: 1.

### K.1 — Update `run_persona_pipeline.py`

Before invoking `run_pass_1_all`, detect mode and error on partial state (per Q5a decision). Log detected mode clearly for operator visibility.

```python
from flows.shared.chunk_runner import detect_dr_mode

def main():
    # ... existing arg parsing, voice lookup ...
    slug = voice_slug_from(name)
    project_root = resolve_project_root(args.project)

    try:
        mode = detect_dr_mode(slug, project_root)
    except RuntimeError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"[persona_pipeline] DR mode detected: {mode}")
    # ... continue into Pass 1.1-1.7 merge via run_pass_1_all(..., mode=mode) ...
```

### K.2 — Remove legacy copy-in logic

Previous pipeline copied `$PROJECT_ROOT/inputs/dossiers/<slug>_claude_dr.md` to `$PROJECT_ROOT/runs/<slug>/01_research/claude_dr_dossier.md`. With the new layout, the DR dossier already lives at its canonical location (`voices/<slug>/01_research/04_dr_dossier/`), so the copy step is obsolete. Remove it.

### K.3 — Commit

```
feat(phase-b/restructure-K): run_persona_pipeline mode detection + clean resume

Pipeline entry:
- Auto-detects per-section vs monolithic DR mode via detect_dr_mode()
- Errors cleanly with actionable message on partial state
- Removes legacy copy-in from inputs/dossiers/ → runs/<slug>/01_research/
  (obsolete under per-voice folder layout; DR dossier lives at canonical
  voices/<slug>/01_research/04_dr_dossier/ location)

Closes OPEN_ITEMS pending code change #4.
```

---

## Phase L — Manifest + telemetry

**Effort:** ~30 min. Commits: 1.

### L.1 — Create manifest wrapper

At `personas/flows/shared/manifest.py`:

```python
"""Per-voice manifest — logs every LLM call for cost + wall-time analysis.

Each call_* wrapper appends an entry. Manifest lives at
voices/<slug>/_manifest.json as a list of entries, one per call.
"""
import json
import time
from pathlib import Path
from flows.shared import paths
from flows.shared.project_root import get_project_root


def record(
    slug: str,
    pass_name: str,      # e.g. "pass_1_1", "pass_2", "tailoring", "pass_7a"
    model: str,          # e.g. "claude-opus-4-7"
    provider: str,       # e.g. "anthropic", "perplexity", "google", "openai"
    input_tokens: int,
    output_tokens: int,
    thinking_tokens: int = 0,
    cost_usd: float | None = None,
    wall_seconds: float = 0.0,
    project_root: Path | None = None,
) -> None:
    entry = {
        "timestamp": time.time(),
        "pass_name": pass_name,
        "model": model,
        "provider": provider,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "thinking_tokens": thinking_tokens,
        "cost_usd": cost_usd,
        "wall_seconds": wall_seconds,
    }
    manifest_path = paths.manifest(slug, project_root)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    existing = []
    if manifest_path.exists():
        try:
            existing = json.loads(manifest_path.read_text())
        except json.JSONDecodeError:
            # Corrupt manifest — rename for inspection and start fresh.
            manifest_path.rename(manifest_path.with_suffix(".json.corrupt"))
            existing = []
    existing.append(entry)
    manifest_path.write_text(json.dumps(existing, indent=2) + "\n")
```

### L.2 — Wire into each `call_*` wrapper

In `flows/shared/clients.py`, wrap `call_claude`, `call_perplexity`, `call_gemini`, `call_openai` so each records an entry after the call completes. Passes the current voice's slug (use a context variable or explicit pass-through). You'll need to thread `slug` + `pass_name` through call sites — most already know these.

### L.3 — Commit

```
feat(phase-b/restructure-L): _manifest.json per-pass cost + wall-time telemetry

New flows/shared/manifest.py records every LLM call (provider, model,
tokens, thinking tokens, cost, wall time) to voices/<slug>/_manifest.json.

Wired into call_claude, call_perplexity, call_gemini, call_openai in
clients.py. Pass name threaded from call sites (e.g. "pass_1_1",
"tailoring", "pass_7a").

Enables retrospective per-voice cost analysis and bottleneck detection.

Closes OPEN_ITEMS "_manifest.json per-pass cost telemetry" smaller improvement.
```

---

## Phase M — Miscellaneous bundles

**Effort:** ~45 min. Commits: 1 (bundled).

Four small items. One commit at end.

### M.1 — `--choose N` TTY consistency

In `run_pass0a_voice_config.py`, find `--choose N` handling. Make it always exit on out-of-range (don't fall back to interactive picker). This is the simpler, deterministic path.

### M.2 — `display_name_with_hint` wiring

Currently `display_name_with_hint` in `prompt_render.py` equals `display_name`. Wire it: if `voice_config.wikipedia_disambiguation_hint` is set (or derive from Wikipedia URL), prepend that hint to the display name. E.g. "Plato (ancient Greek philosopher, 428–348 BCE)" instead of just "Plato".

Check if `voice_config` currently has a `wikipedia_disambiguation_hint` field. If not, you may need to derive from the `wikipedia_extract` or first line of `manual_grounding`. Sensible heuristic: first 50 characters of wikipedia_extract with parenthesization.

### M.3 — `jinja2.StrictUndefined` in prompt_render.py

Change Jinja environment config to use `StrictUndefined` so template variable typos fail loudly instead of silently rendering empty strings.

```python
from jinja2 import StrictUndefined, Environment
env = Environment(undefined=StrictUndefined, ...)
```

Run existing tests after; any test that relied on permissive undefined will need fixing (usually means providing a previously-missing variable). Likely small adjustment set.

### M.4 — `MergedDossier.voice_register` alias audit

Grep for any remaining code that accesses `merged_dossier.register` (the Pydantic alias) instead of `merged_dossier.voice_register`. Update to use the canonical attribute name where found. Pydantic handles serialization with `by_alias=True`, so JSON shape stays compatible.

```bash
grep -rn "\.register" personas/ --include="*.py" | grep -v "registry\|registered\|register_and_tone\|registering"
```

Most matches will be `register_and_tone` (different field). Look for the specific `MergedDossier.register` access pattern.

### M.5 — Commit (bundled)

```
feat(phase-b/restructure-M): bundled smaller improvements

Four items from OPEN_ITEMS Smaller Improvements:

1. run_pass0a_voice_config.py: --choose N always exits on out-of-range
   (removed TTY-fallback inconsistency).

2. prompt_render.py: display_name_with_hint now wires Wikipedia
   disambiguation hint into rendered DR prompts for voices with common
   names.

3. prompt_render.py: jinja2.StrictUndefined enables loud-fail on template
   variable typos; catches stale template references at render time
   instead of LLM-output time. pass_0b_header.md + pass_0b_footer.md
   updated to default section_mode to false (guards monolithic rendering
   against StrictUndefined errors when section_mode unset).

4. MergedDossier.voice_register alias audit across consumers: grepped
   all .register accessor patterns, confirmed none use the alias form
   directly. Safe.

Each cleanup addresses a flag from OPEN_ITEMS Smaller Improvements or
REBUILD_PLAN Cross-cutting.
```

Push:

```bash
git push origin phase-b-rebuild
```

---

## Phase N — Migration script + execute

**Effort:** ~1 hr. Commits: 1.

### N.1 — Write migration script

Create `personas/scripts/migrate_to_per_voice_layout.py`:

```python
"""One-shot migration from flat layout to per-voice-folder layout.

Old paths (per-voice — migrate these):
  $PROJECT_ROOT/inputs/voices/<slug>.json
  $PROJECT_ROOT/inputs/voices/<slug>_pass0a_review.md
  $PROJECT_ROOT/inputs/non_human_grounding/<slug>.md
  $PROJECT_ROOT/inputs/dossiers/<slug>_claude_dr.md
  $PROJECT_ROOT/inputs/dossiers/_dr_prompts/<slug>_dr_prompt.md
  $PROJECT_ROOT/inputs/dossiers/_dr_prompts/_tailoring_notes.json
    (or $PROJECT_ROOT/inputs/dossiers/_dr_prompts/<slug>_tailoring_notes.json — verify)
  $PROJECT_ROOT/runs/<slug>/01_research/perplexity_dossier.json
  $PROJECT_ROOT/runs/<slug>/01_research/gemini_broad_scan.json
  $PROJECT_ROOT/runs/<slug>/01_research/claude_dr_dossier.md
  $PROJECT_ROOT/runs/<slug>/01_research/primary_texts.json
  $PROJECT_ROOT/runs/<slug>/01_research/excerpt_selections.json
  $PROJECT_ROOT/runs/<slug>/02_passes/pass_2_identity_boundaries.json
  $PROJECT_ROOT/runs/<slug>/02_passes/pass_3_intellectual_core.json
  $PROJECT_ROOT/runs/<slug>/02_passes/pass_4a_voice.json
  $PROJECT_ROOT/runs/<slug>/02_passes/pass_4b_artifact.json
  $PROJECT_ROOT/runs/<slug>/02_passes/pass_5_engagement.json
  $PROJECT_ROOT/runs/<slug>/02_passes/pass_6_corpus.json
  $PROJECT_ROOT/runs/<slug>/02_passes/_ct_pass*.json
  $PROJECT_ROOT/runs/<slug>/02_passes/pass_7pre_citation.json
  $PROJECT_ROOT/runs/<slug>/02_passes/pass_7_anachronism.json
  $PROJECT_ROOT/runs/<slug>/02_passes/pass_7a.json
  $PROJECT_ROOT/runs/<slug>/02_passes/pass_7b.json
  $PROJECT_ROOT/runs/<slug>/02_passes/pass_7c.json
  $PROJECT_ROOT/runs/<slug>/02_passes/derive.json
    (split into provocateur_profile.json + evaluation_rubric.json in new layout)
  $PROJECT_ROOT/runs/<slug>/persona_card_assembled.json
  $PROJECT_ROOT/runs/<slug>/provocateur_profile.json
  $PROJECT_ROOT/runs/<slug>/evaluation_rubric.json

Old paths (project-level shared — DO NOT migrate; stay at project root):
  $PROJECT_ROOT/inputs/conference_facts.json
  $PROJECT_ROOT/inputs/audience_profile.json
  $PROJECT_ROOT/inputs/panel_roster.json
  (if these are under inputs/ currently, move them up one level to $PROJECT_ROOT/
   as part of the restructure — they're project-level, not per-voice)

New paths (see paths.py):
  $PROJECT_ROOT/voices/<slug>/00_intake/01_non_human_grounding.md
  $PROJECT_ROOT/voices/<slug>/00_intake/02_voice_config.json
  $PROJECT_ROOT/voices/<slug>/00_intake/03_review_doc.md
  $PROJECT_ROOT/voices/<slug>/01_research/01_perplexity_dossier.json
  $PROJECT_ROOT/voices/<slug>/01_research/02_gemini_broad_scan.json
  $PROJECT_ROOT/voices/<slug>/01_research/03_dr_prompts/01_monolithic_dr_prompt.md
  $PROJECT_ROOT/voices/<slug>/01_research/03_dr_prompts/02_tailoring_notes.json
    (03-08_section_*_dr_prompt.md produced fresh by split on next Phase 0.5 run)
  $PROJECT_ROOT/voices/<slug>/01_research/04_dr_dossier/07_concat_claude_dr.md
    (if old claude_dr_dossier.md exists, rename to 07_concat_; per-section files
     populated separately by operator after paste)
  $PROJECT_ROOT/voices/<slug>/02_merge/0N_pass_1_N_*.json
    (rename pass_1_1_biographical, pass_1_2_intellectual, ... if they existed under
     old 02_passes/pass_1_*.json convention; for Dostoevsky there are no Pass 1
     chunk outputs yet)
  $PROJECT_ROOT/voices/<slug>/03_corpus/01_primary_texts.json
  $PROJECT_ROOT/voices/<slug>/03_corpus/02_excerpt_selections.json
  $PROJECT_ROOT/voices/<slug>/04_generation/0N_pass_*.json
  $PROJECT_ROOT/voices/<slug>/05_validation/0N_pass_7_*.json
  $PROJECT_ROOT/voices/<slug>/06_derive/01_provocateur_profile.json
  $PROJECT_ROOT/voices/<slug>/06_derive/02_evaluation_rubric.json
  $PROJECT_ROOT/voices/<slug>/07_persona_card_assembled.json

Script:
- Lists voices present under $PROJECT_ROOT (scan inputs/voices/ + runs/)
- For each voice: maps old → new paths; logs each move
- For project-level shared files: if under inputs/, move up to project root
- --dry-run flag: prints moves without executing
- Idempotent: safe to re-run; skips moves where source doesn't exist or
  destination already exists
- At end: reports manifest of moves + empty-old-directories for manual
  cleanup (does NOT rm -rf old dirs; operator decides)

For Dostoevsky specifically, expect: voice_config + review_doc + tailored
monolithic prompt + perplexity + gemini. No Pass 1, 2-6, 7, Derive outputs
exist yet. Most target paths won't have sources; script should skip
gracefully.
"""
```

Use `shutil.move` (not `git mv` — project data is outside git). Log every move to stdout. Emit a JSON manifest at `$PROJECT_ROOT/_migration_manifest.json` with timestamp + source→destination mapping for rollback.

### N.2 — Dry-run on Dostoevsky

```bash
cd "/Users/aienvironment/Desktop/AI Assembly"
venv/bin/python code/personas/scripts/migrate_to_per_voice_layout.py \
  --project projects/phase-l-dostoevsky --dry-run
```

Review output: every file should map to a sensible new location. If anything looks wrong (missing voice, unexpected source file), stop and investigate.

### N.3 — Execute on Dostoevsky

```bash
venv/bin/python code/personas/scripts/migrate_to_per_voice_layout.py \
  --project projects/phase-l-dostoevsky
```

Verify:

```bash
ls "projects/phase-l-dostoevsky/voices/fyodor_dostoevsky/"
# Expect: 00_intake/ 01_research/ (+ files under each)
```

Spot-check a few specific files are where they should be:

```bash
cat "projects/phase-l-dostoevsky/voices/fyodor_dostoevsky/00_intake/02_voice_config.json" | head -5
```

### N.4 — Post-migration: drop Dostoevsky §1, §2 outputs into new location

From user's Desktop:

```bash
# §1 + §2 outputs currently at (both models):
#   ~/Desktop/dosto_brief+section1_opus4.6.md
#   ~/Desktop/dosto_brief+section1_opus4.7.md
#   ~/Desktop/dosto_brief+section2_opus4.6.md
#   ~/Desktop/dosto_brief+section2_opus4.7.md

# Operator decides which model's output to use as the "real" §1, §2 for Phase L.
# Default per Run 7 analysis: use 4.6 (denser extractable material for the
# chunked merge).
# Copy the 4.6 versions into new location (cp, not mv — keep Desktop originals):

cp "$HOME/Desktop/dosto_brief+section1_opus4.6.md" \
   "projects/phase-l-dostoevsky/voices/fyodor_dostoevsky/01_research/04_dr_dossier/01_section_1.md"
cp "$HOME/Desktop/dosto_brief+section2_opus4.6.md" \
   "projects/phase-l-dostoevsky/voices/fyodor_dostoevsky/01_research/04_dr_dossier/02_section_2.md"
```

**4.7 outputs on Desktop stay on Desktop untouched.** They're useful to preserve for:
- Side-by-side comparison during Phase L.8 quality gate (4.6 vs 4.7 assembled cards)
- Fallback if 4.6 sections turn out to be deficient at merge time
- Empirical record of the Run 7 dual-model validation

Do NOT delete, move, or modify `~/Desktop/dosto_brief+section{1,2}_opus4.7.md`. They stay where they are as Phase B artifacts.

Note: §3–§6 do NOT exist yet (operator task after this Sonnet session). The pipeline will error cleanly on Dostoevsky run until §3–§6 land at `01_research/04_dr_dossier/0N_section_N.md`.

### N.5 — Also run migration on other existing projects

```bash
venv/bin/python code/personas/scripts/migrate_to_per_voice_layout.py \
  --project projects/test --dry-run
```

If `projects/test/` has voice data, migrate it. If not, skip.

`projects/athens-2026/` may have voice configs (curator-produced); migrate similarly.

### N.6 — Archived v3.10 runs: DO NOT MIGRATE

Archived Plato / Arendt / Ibn Battuta at `~/Desktop/AI Assembly/archive/runs/personas/` stay at their archive paths (historical record). DO NOT migrate these.

### N.7 — Empty old directories

After migration, old directories (`inputs/`, `runs/`) are empty for migrated voices. Operator decides when/if to remove. Sonnet does NOT rm -rf the old dirs — leave that as a deliberate human step. At most, script reports which dirs are empty.

### N.8 — Commit

```
feat(phase-b/restructure-N): per-voice layout migration script + Dostoevsky migrated

personas/scripts/migrate_to_per_voice_layout.py: one-shot migration from
flat layout (inputs/voices, inputs/dossiers, runs/<slug>/) to per-voice
folder layout (voices/<slug>/00_intake..06_derive/).

Idempotent, with --dry-run flag. Logs every move to _migration_manifest.json
at project root for rollback audit.

Executed against projects/phase-l-dostoevsky/ — Dostoevsky's Phase 0.5
artifacts (Perplexity, Gemini, tailored monolithic + section prompts,
voice_config, review_doc) now live at the new canonical paths.

Dostoevsky §1 and §2 Claude DR outputs (from ~/Desktop/) copied into
voices/fyodor_dostoevsky/01_research/04_dr_dossier/ (4.6 model outputs
chosen as canonical per Run 7 density analysis). §3-§6 still pending
manual DR sessions.

Archived v3.10 runs at ~/Desktop/AI Assembly/archive/ NOT migrated —
preserved as historical record.
```

Push:

```bash
git push origin phase-b-rebuild
```

---

## Phase O — End-to-end testing

**Effort:** ~1.5 hrs. Commits: 0 (verification only; test reports committed in Phase P).

### O.1 — Per-section mode dry-run

With Dostoevsky §1 + §2 in place (§3–§6 absent), attempt to run the pipeline:

```bash
cd "/Users/aienvironment/Desktop/AI Assembly/code/personas"
AI_ASSEMBLY_PROJECT_ROOT="../projects/phase-l-dostoevsky" \
  venv/bin/python run_persona_pipeline.py "Fyodor Dostoevsky"
```

Expected: errors cleanly with "Partial DR state: 2/6 section files present. Missing: sections [3, 4, 5, 6]."

This verifies error-on-partial-state works. ✓

### O.2 — Monolithic fallback test

Concatenate Dostoevsky §1 + §2 into a monolithic file and retry (as a smoke test of monolithic path, even though it's underspecified).

**SAFETY CHECK FIRST.** Before running the destructive concat+delete sequence, verify Desktop backups exist:

```bash
ls -la "$HOME/Desktop/dosto_brief+section1_opus4.6.md" \
       "$HOME/Desktop/dosto_brief+section2_opus4.6.md"
```

Both files must exist. If either is missing, STOP — do not proceed with O.2. The O.2 destructive step removes §1 + §2 from the project, and O.3 restores them by copying from Desktop. If Desktop backups are gone, O.2 loses work irretrievably.

Only after verifying Desktop backups:

```bash
cat "projects/phase-l-dostoevsky/voices/fyodor_dostoevsky/01_research/04_dr_dossier/01_section_1.md" \
    "projects/phase-l-dostoevsky/voices/fyodor_dostoevsky/01_research/04_dr_dossier/02_section_2.md" \
    > "projects/phase-l-dostoevsky/voices/fyodor_dostoevsky/01_research/04_dr_dossier/07_concat_claude_dr.md"
rm "projects/phase-l-dostoevsky/voices/fyodor_dostoevsky/01_research/04_dr_dossier/01_section_1.md"
rm "projects/phase-l-dostoevsky/voices/fyodor_dostoevsky/01_research/04_dr_dossier/02_section_2.md"

cd personas
AI_ASSEMBLY_PROJECT_ROOT="../projects/phase-l-dostoevsky" \
  venv/bin/python run_persona_pipeline.py "Fyodor Dostoevsky"
```

This should detect monolithic mode (07_concat present, no 01–06 section files) and proceed. HOWEVER: a 2-section concat won't produce valid Pass 1.1–1.6 output (§3–§6 material absent). Expected: Pass 1.1 BIOGRAPHICAL may succeed (§1 content present); Pass 1.3 REASONING will likely produce thin output because §3 content isn't in the concat.

You don't need to run it to completion. Run enough to verify:
- Mode detection reports "monolithic"
- chunk_runner reads the concat file
- At least Pass 1.1 produces non-empty JSON

Abort partway through; this is a smoke test, not an acceptance test.

### O.3 — Restore §1 + §2 for downstream

After O.2 smoke test:

```bash
# Restore from Desktop backups (verified to exist in O.2 safety check)
cp "$HOME/Desktop/dosto_brief+section1_opus4.6.md" \
   "projects/phase-l-dostoevsky/voices/fyodor_dostoevsky/01_research/04_dr_dossier/01_section_1.md"
cp "$HOME/Desktop/dosto_brief+section2_opus4.6.md" \
   "projects/phase-l-dostoevsky/voices/fyodor_dostoevsky/01_research/04_dr_dossier/02_section_2.md"
rm "projects/phase-l-dostoevsky/voices/fyodor_dostoevsky/01_research/04_dr_dossier/07_concat_claude_dr.md"
```

Back to per-section mode for real Phase L testing (after user does §3–§6 DR sessions).

### O.4 — Unit tests sweep

```bash
cd personas && venv/bin/python -m pytest tests/ -v
```

All tests pass. If any failures, diagnose and fix before proceeding.

### O.5 — Report findings

Write a brief report at `_workspace/planning/SONNET_PHASE_B_RESTRUCTURE_TEST_REPORT.md`:

```markdown
# Phase B restructure — end-to-end test report

**Branch:** phase-b-rebuild @ <HEAD SHA>
**Dostoevsky state:** §1 + §2 present (from user's Desktop, 4.6 model);
§3–§6 pending manual DR.

## Per-section mode partial-state detection
...

## Monolithic fallback smoke test
...

## Unit test suite
N tests pass, 0 fail, 0 skip (excluding integration).

## Verdict
Ready for Phase P documentation sweep. Phase L full end-to-end still
requires Dostoevsky §3–§6 DR completion (operator task).
```

---

## Phase P — Documentation sweep

**Effort:** ~1 hr. Commits: 1.

### P.1 — Files to update

Update in place (stale-after-restructure):

1. **`CLAUDE.md`** (repo root) — §"Filesystem layout (umbrella)", §"Code / project separation (Tier 3)". Rewrite to new `voices/<slug>/` layout.
2. **`docs/CURRENT_STATE.md`** — §0 "Quick map", §4 "Cross-repo data contracts", §6 "Known bugs, gaps, limitations" (fixture paths), §8 "Pre-Athens critical path" (Phase A/B/C paths).
3. **`_workspace/planning/OPEN_ITEMS.md`** — mark "Pending code changes" items 1–5 + bundled smaller-improvements as SHIPPED with this session's commit SHAs. Add a top-of-doc note dated 2026-04-21 pointing at the Phase B restructure commit range.
4. **`_workspace/planning/EXECUTION_PLAN_phase_b.md`** — Phase L section (L.1–L.10) paths throughout; mention per-section manual DR workflow; update pipeline-resume command.
5. **`_workspace/planning/REBUILD_PLAN.md`** — §"Test material in repo" (Ibn Battuta → synthetic), §"Phase 0 · Pass 0a" (paths), Phase B implementation checklist.
6. **`personas/README.md`** — path references.
7. **`docs/README.md`** — staleness index note if any referenced specs drift.

### P.2 — Grep for residual stale paths

```bash
grep -rn "inputs/voices/" docs/ personas/ _workspace/planning/ CLAUDE.md --include="*.md" --include="*.py" | grep -v "_workspace/archive"
grep -rn "inputs/dossiers/" docs/ personas/ _workspace/planning/ CLAUDE.md --include="*.md" --include="*.py" | grep -v "_workspace/archive"
grep -rn "runs/<slug>" docs/ personas/ _workspace/planning/ CLAUDE.md --include="*.md" --include="*.py" | grep -v "_workspace/archive"
grep -rn "tests/fixtures/ibn_battuta" docs/ personas/ _workspace/planning/ --include="*.md" --include="*.py"
```

Each match is either (a) an archive file (skip), or (b) a stale reference to update.

### P.3 — Commit

```
docs(phase-b/restructure-P): doc sweep for per-voice layout

Updated for the new voices/<slug>/00_intake..06_derive/ layout:
- CLAUDE.md: Filesystem layout + Tier 3 sections rewritten
- docs/CURRENT_STATE.md: Quick map + data contracts + critical path
- _workspace/planning/OPEN_ITEMS.md: Pending code changes (items 1-5) +
  bundled smaller-improvements marked SHIPPED in this session
- _workspace/planning/EXECUTION_PLAN_phase_b.md: Phase L paths updated;
  per-section manual DR workflow documented
- _workspace/planning/REBUILD_PLAN.md: test-fixture section (Ibn Battuta
  → synthetic); Phase 0.5 paths
- personas/README.md: path references
- docs/README.md: staleness annotations

Ibn Battuta references in docs updated to reflect synthetic replacement +
deleted-from-code-repo status.

Session scope now complete. Phase L.8 human quality gate (Dostoevsky
card review) remains gated on §3-§6 manual DR completion + pipeline run.
```

Push:

```bash
git push origin phase-b-rebuild
```

---

## Phase Q — Final verification

**Effort:** ~15 min. No commits.

### Q.1 — Path hygiene

```bash
cd "/Users/aienvironment/Desktop/AI Assembly/code"
# Confirm no stale hardcoded paths in Python
grep -rn "inputs/voices\|inputs/dossiers\|/runs/<slug>\|/01_research/\|/02_passes/" personas/ --include="*.py" | grep -v "flows/shared/paths.py" | grep -v "migrate_to_per_voice_layout"
# Should be empty or only migration-script references.

# Confirm paths.py is consistently used
grep -c "from flows.shared import paths\|from flows.shared.paths import" personas/*.py personas/flows/**/*.py
# Should return non-zero for every runner
```

### Q.2 — Test suite green

```bash
cd personas && venv/bin/python -m pytest tests/ -v
```

All tests pass.

### Q.3 — Branch state check

```bash
git status              # clean
git log phase-b-rebuild --oneline -20   # all session commits visible
git diff origin/phase-b-rebuild         # empty (all pushed)
```

### Q.4 — Handoff to user

Write final summary at `_workspace/planning/SONNET_PHASE_B_RESTRUCTURE_COMPLETE.md`:

```markdown
# Phase B restructure — complete

**Session date:** <YYYY-MM-DD>
**Branch:** phase-b-rebuild @ <HEAD SHA>
**Model:** Claude Sonnet 4.6 medium
**Total commits in session:** N (list them)

## What shipped

[Enumerate each phase A-Q with one-line summary + commit SHA.]

## What remains gated on operator action

- Dostoevsky §3-§6 manual DR sessions (paste 4 section prompts into claude.ai)
- Once §3-§6 saved at voices/fyodor_dostoevsky/01_research/04_dr_dossier/:
    run: cd personas && venv/bin/python run_persona_pipeline.py "Fyodor Dostoevsky"
- Phase L.8 human quality gate (compare assembled card against v3.7-paste baseline)

## Open items for next sessions

- Phase L.8 review (human quality judgment, not automatable)
- Phase M (verify + push + PR to main), gated on L.8 passing
- Voice Pipeline Steps 1+2 build (separate workstream)
- Remaining OPEN_ITEMS items not bundled in this session

## Test coverage

- Unit: paths.py, split_tailored_prompt, perplexity_split fallback,
  dr_validation per-section mode, chunk_runner mode detection
- Integration (gated): @pytest.mark.integration, requires
  AI_ASSEMBLY_INTEGRATION_PROJECT env var
- End-to-end on Dostoevsky: partial (§1 + §2 present; §3-§6 pending)

## Honest caveats

- Dostoevsky Phase L end-to-end not fully tested because §3-§6 not produced yet.
- Per-section mode chunk_runner tested against synthetic fixture + partial
  Dostoevsky state; full 6-section run deferred to operator completion.
- Monolithic fallback smoke-tested but not acceptance-tested.
- Migration idempotency verified on Dostoevsky; other projects (athens-2026)
  may need re-run if voices were added since migration ran.
```

---

## What NOT to touch

Absolutely do not modify during this session:

- `~/Desktop/AI Assembly/archive/` — historical v3.10 runs. Read-only archive.
- `_workspace/archive/` — historical fix plans + session artifacts. Read-only archive.
- Any `_archive/` subdirectory anywhere.
- `runtime/` tree — this session is personas-only. Runtime tests should stay green by default (no runtime code changes).
- `main` branch — all work on `phase-b-rebuild`; no merges to main.
- Ibn Battuta fixture data OUTSIDE the code repo — if any exists elsewhere, leave alone.
- User's Desktop `dosto_brief+section{1,2}_opus4.{6,7}.md` files except the specific copy step in Phase N.4.
- `.claude/settings.local.json` — allowlist; scope adjustments separate concern.
- Test fixtures for other pipelines (runtime ingest tests, transcription tests, researcher tests, provocateur tests) — don't touch.

## Notes for Sonnet

- **If the plan references a file that doesn't exist**, flag and ask before creating. The plan was written at a specific code snapshot; post-cleanup state may differ. When in doubt, investigate before changing.
- **If a Python import fails in test**, check the venv: `cd personas && venv/bin/python -c "import X"`. Environment issues are rarely the code's fault.
- **If a test that was passing before your change now fails**, the test likely lacks a fixture update. Diagnose before assuming the code change is wrong.
- **The tailoring pass already exists** (`pass_0b_tailor.md` per cleanup-3 in OPEN_ITEMS). If it's missing, flag — we're assuming it's intact from the Phase B evening-session cleanup commits.
- **Pydantic schemas are FROZEN** per PB#7. Do NOT modify `personas/schemas/_conventions.py`, `pass_1_*.py`, `merged_dossier.py`, `voice_config.py` in this session. If a schema change feels needed, stop and ask.
- **Coherence threading** (`_ct_*` files): under generation_dir per paths.py, interleaved with pass outputs. Not a separate subdir. Matches Option X decision.
- **"display_name_with_hint"**: check whether `voice_config` currently has a `wikipedia_disambiguation_hint` field. If not, decide: add to VoiceConfig schema (with care — schemas frozen) OR derive from wikipedia_extract at render time OR keep TODO for a future session. Prefer: derive from wikipedia_extract first 50 chars.

## Dependency summary

Phase execution order is A → B → C → D → E → F → G → H → I → J → K → L → M → N → O → P → Q.

Critical dependencies:
- B (paths.py) must complete before any other phase touching paths.
- E (header/footer Jinja) must complete before F (splitter uses mode-aware rendering).
- F (splitter) must complete before G (Phase 0.5 invokes splitter).
- H (perplexity_split) must complete before J (chunk_runner uses fallback).
- I (validator) must complete before K (pipeline resume uses validator).
- J (chunk_runner) must complete before K (pipeline resume wires mode flag).
- N (migration) must complete before O (testing against real project data).
- O (testing) must pass before P (doc sweep captures current state).
- P (docs) must complete before Q (verification).

Push cadence: after C, F, J, N, P. Don't accumulate >4 phases unpushed.

---

*Plan authored 2026-04-21 by Opus 4.7 design session. Execute on Sonnet 4.6 medium. When complete, move this file to `_workspace/archive/fix-plans/` as executed, consistent with prior SONNET_EXECUTION_PLAN_*.md precedent.*
