# Test fixtures

## synthetic_voice/

A minimal, clearly-fake voice used to exercise pipeline plumbing in unit
tests. NOT a real research subject. If a test fails content-validation
(e.g. "Test Subject Alpha not mentioned in §2"), the test is misspecified —
it is reading the synthetic fixture as if it were a real voice.

**Do NOT edit synthetic_voice/ files without updating corresponding tests.**
Content is hand-crafted to exercise specific code paths (heading regex,
tag markers, section boundary detection).

### Layout

```
synthetic_voice/
  00_intake/
    02_voice_config.json       — type=human, voice_mode=philosophical
  01_research/
    01_perplexity_dossier.json — 6-section dossier, structurally valid
    02_gemini_broad_scan.json  — flat broad-scan JSON
    04_dr_dossier/
      01_section_1.md through 06_section_6.md — per-section DR outputs
```

Each section file contains ~1 KB of obviously synthetic prose about
"Test Subject Alpha" with appropriate `[primary]`, `[~uncertain]`, and
`[quote: Test Work, §N]` markers to exercise tag-parsing paths.

### Integration fixtures

Unit tests use `synthetic_voice`. Integration tests exercise real project
data at `$AI_ASSEMBLY_INTEGRATION_PROJECT/voices/<slug>/` and are gated
via `@pytest.mark.integration` + env var. Default pytest runs skip them.
Run integration tests with:

```
AI_ASSEMBLY_INTEGRATION_PROJECT=projects/phase-l-dostoevsky pytest -m integration
```

## ibn_battuta/ (DELETED — see git history)

The `ibn_battuta/` fixture directory was deleted in Phase B restructure
(commit feat(phase-b/restructure-D)). Ibn Battuta is a production panel
voice; his actual build regenerates fresh when his Athens queue slot opens.
The old fixtures predated the Phase B Pass 0b rewrites and would pre-position
pre-Phase-B biases into his production research.

Regeneration cost (~$10) is worth avoiding that contamination.
