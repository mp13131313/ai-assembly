# Test fixtures — Ibn Battuta Phase 0.5 outputs

Per REBUILD_PLAN §"Test material in repo" + decisions log #7 (2026-04-19).

## Contents

- `ibn_battuta/perplexity_dossier.json` — real Perplexity sonar-deep-research
  output from a live Battuta Phase 0.5 run.
- `ibn_battuta/gemini_broad_scan.json` — real Gemini broad-scan output from
  the same run.

No Claude Deep Research dossier is pinned — the Battuta DR output lives on the
curator's Desktop and is intentionally discarded; Phase B regenerates DR via
the new hybrid-tailored prompt.

## Refresh cost + cadence

- **Regen cost:** ~$5–10 per Perplexity call (sonar-deep-research priced per
  request + search units). Gemini broad-scan is ~free on the current paid tier
  but still slow (~3–5 min).
- **Last refresh:** 2026-04-18 (Battuta Phase 0.5 verification run).
- **Refresh triggers:**
  1. Phase 0.5 prompts (`persona_pass_1a_*.md`, `persona_pass_1b_broad_scan.md`)
     change non-trivially — not typo fixes, real new asks.
  2. Fixture-content-dependent test failures (shape change in Perplexity /
     Gemini API response; broken citation format; etc.).
  3. Annual freshness check (these dossiers cite scholarly sources; refresh
     once a year to stay within 12 months of current scholarship).
- **Do not refresh for:** prompt copy-edits, runner code changes, new validator
  fields — schema evolution should work against the existing fixtures.

## Refresh command

```bash
cd personas && venv/bin/python run_phase0_1_research.py "Ibn Battuta"
# then move outputs:
cp runs/ibn_battuta/01_research/perplexity_dossier.json \
   tests/fixtures/ibn_battuta/perplexity_dossier.json
cp runs/ibn_battuta/01_research/gemini_broad_scan.json \
   tests/fixtures/ibn_battuta/gemini_broad_scan.json
```

Update the "Last refresh" line above with the new date + commit.

## How tests use them

Pass 1.1 / 1.2 / 1.3 / 1.4 / 1.5 / 1.6 merge runners accept a
`use_test_fixtures=True` flag that reads from here instead of `runs/<slug>/`.
The pinned fixtures let merge-mechanics (schema validation, retry-with-critique,
atomic write) be exercised without a live Phase 0.5 run.

Note: fixture content is v3.10-wound-shaped (pre-Boddice). B.4 tests merge
mechanics only; end-to-end Boddice-shape validation lands with the first real
voice run in Phase L.
