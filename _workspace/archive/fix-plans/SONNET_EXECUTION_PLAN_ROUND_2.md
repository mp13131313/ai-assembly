# Sonnet Execution Plan — Round 2

**Paste this into a fresh Claude Sonnet 4.6 session, medium effort. The plan is self-contained.**

## Your task

Execute fixes 15–23 in `personas/notes/WALKTHROUGH_FIXES_PENDING.md` (the "Round 2 — Added during mock walkthrough" section). Commit after each phase with the specified commit message. Push the branch at the end. Stop and ask if anything is unclear or a verification fails — do NOT proceed through broken state.

Round 1 (fixes 1–14) was already implemented and merged to main. This is the follow-up round.

## Preflight

1. Read these in order:
   - `personas/notes/WALKTHROUGH_FIXES_PENDING.md` — substantive fix content, especially the "Round 2" section
   - `docs/AI_Assembly_Persona_Pipeline_v3_8.md` — current spec
   - `personas/run_pass0a_voice_config.py`, `personas/run_pass0b_dr_prompt.py`, `personas/run_persona_pipeline.py` — files you'll modify
   - `personas/flows/shared/prompts/pass_0a_voice_config.md`, `personas/flows/shared/prompts/pass_0b_dr_prompt.md`
   - `personas/flows/shared/node0_validation.py`, `personas/flows/shared/io.py`

2. Verify you're on `main` and the tree is clean. Create feature branch:
   ```bash
   cd /Users/aienvironment/Desktop/ai-assembly
   git checkout main && git pull
   git checkout -b walkthrough-fixes-round2-2026-04-17
   ```

## Phase A — Field drops (trivial, independent)

Three fields dropped from voice_config schema. Each is a ~5-file edit.

### A.1 — Fix #16: Drop `needs_dr_supplement`

Per `WALKTHROUGH_FIXES_PENDING.md` §16.

- `pass_0a_voice_config.md` — remove field from schema block.
- `node0_validation.py` — remove `normalized.setdefault("needs_dr_supplement", True)` at line 123.
- `run_persona_pipeline.py` — remove the Pass 3 DR supplement block entirely (currently around lines 360-403: `_should_dr_supplement()`, `_pass_3_dr_supplement()`, and the trigger block that calls them). Remove `chatgpt_supplement` parameter from `_pass_3()`'s `render()` call and from the Pass 3 user prompt template if referenced there.
- `personas/inputs/voices/*.json` — remove `needs_dr_supplement` key from all voice configs.

Verify: `grep -rn "needs_dr_supplement" personas/ --include="*.py" --include="*.md" --include="*.json" | grep -v "_archive\|runs/\|WALKTHROUGH_FIXES_PENDING\|SONNET_EXECUTION_PLAN"` returns nothing.

**Commit:** `refactor: drop needs_dr_supplement field (Claude DR bakes deep research into Phase 1)`

### A.2 — Fix #17: Drop `pass_1a_claude_dr_file`

Per `WALKTHROUGH_FIXES_PENDING.md` §17.

- `pass_0a_voice_config.md` — remove field from schema block.
- `run_pass0a_voice_config.py` — remove the injection at line 116 (`voice_config["pass_1a_claude_dr_file"] = ...`).
- `node0_validation.py` — remove `normalized.setdefault("pass_1a_claude_dr_file", None)` at line 132.
- `run_persona_pipeline.py` — currently reads `vi.get("pass_1a_claude_dr_file")` around line 112. Replace with: derive path from voice slug at load time using `f"inputs/dossiers/{SLUG}_claude_dr.md"`. Keep the rest of the Pass 1a-DR load logic intact.
- `personas/inputs/voices/*.json` — remove the field from all voice configs.

Verify: `grep -rn "pass_1a_claude_dr_file" personas/ --include="*.py" --include="*.md" --include="*.json" | grep -v "_archive\|runs/\|WALKTHROUGH_FIXES_PENDING\|SONNET_EXECUTION_PLAN"` returns nothing.

**Commit:** `refactor: drop pass_1a_claude_dr_file field (path now derived from slug at runtime)`

### A.3 — Fix #18: Drop `casting_rationale` from voice_config

Per `WALKTHROUGH_FIXES_PENDING.md` §18.

- `pass_0a_voice_config.md` — remove `casting_rationale` from the schema block. Add to the review_doc structure a new section `## Why this voice is in the Assembly` with the same content the field used to hold.
- `node0_validation.py` — remove `normalized.setdefault("casting_rationale", "")` at line 127.
- `personas/inputs/voices/*.json` — remove `casting_rationale` from all voice configs.

Verify: `grep -rn "casting_rationale" personas/ --include="*.py" --include="*.md" --include="*.json" | grep -v "_archive\|runs/\|WALKTHROUGH_FIXES_PENDING\|SONNET_EXECUTION_PLAN"` returns nothing.

**Commit:** `refactor: move casting_rationale from voice_config into review_doc (human-readable, not machine-consumed)`

## Phase B — Pass 0a hardening

### B.1 — Fix #19: Pass 0a client-side enum validation

Per `WALKTHROUGH_FIXES_PENDING.md` §19.

Currently `run_pass0a_voice_config.py` calls `call_claude` and then only checks for `voice_config` and `review_doc` keys. Enum values (voice_mode, corpus_constraint, subtype, type) pass through unvalidated — errors surface only at `run_persona_pipeline.py` startup.

- Add a local validation function in `run_pass0a_voice_config.py` that calls `validate_input()` from `flows.shared.node0_validation` on the model's `voice_config` output.
- On `InputRejected`: retry once with a critique block appended to the user prompt (e.g. `f"\n\nYour previous response failed validation: {error}. Fix and return valid JSON."`). Use `_call_with_retry` pattern.
- On second failure: `sys.exit` with the validation error message.

Note: `validate_input()` needs `conference_context` to be non-empty; at the validation point in Pass 0a, it's still the placeholder `"INJECTED_BY_RUNNER"` (injection happens after validation). Temporarily set it to the project context paragraph for validation purposes, then restore the placeholder → inject the real value → write. Or: refactor validation to skip the `conference_context` presence check in Pass 0a (since injection happens right after).

**Commit:** `fix: Pass 0a validates enum fields client-side, retries once on failure`

### B.2 — Fix #20: Extend retry wrapper to missing-required-key case

Per `WALKTHROUGH_FIXES_PENDING.md` §20.

- In `run_pass0a_voice_config.py`, define a new exception: `IncompleteResponse(ValueError)`.
- Add it to the `_RETRYABLE` tuple.
- In `main()`, after `call_claude` returns, raise `IncompleteResponse` if `voice_config` or `review_doc` keys are missing — let the retry wrapper catch it and retry once.
- Same pattern in `run_pass0b_dr_prompt.py` for the `dr_prompt` key (before Fix #21 converts it to a Jinja template — so only apply if this commit happens before C.1).

**Commit:** `fix: Pass 0a/0b retry on missing required response keys (not just JSON/API errors)`

### B.3 — Fix #15: Wikipedia-grounded disambiguation

Per `WALKTHROUGH_FIXES_PENDING.md` §15. Biggest piece of Phase B.

**New Wikipedia helper module** at `personas/flows/shared/wikipedia.py`:
```python
"""Wikipedia Search + Summary REST API helpers."""
import requests

SEARCH_URL = "https://en.wikipedia.org/w/api.php"
SUMMARY_URL = "https://en.wikipedia.org/api/rest_v1/page/summary/{}"

def search(query: str, limit: int = 5) -> list[dict]:
    """Return list of {title, description, url} dicts from Wikipedia OpenSearch."""
    # params: action=opensearch, search=query, limit=5, format=json
    # response shape: [query, [titles], [descriptions], [urls]]
    # transform into list of dicts

def summary(title_or_url: str) -> dict:
    """Return {title, extract, description, url, infobox_dict?} for a specific page."""
    # accepts either a title (from search results) or a full URL (from --wiki flag)
    # Call the REST /page/summary/{title} endpoint
    # Return parsed dict with title, extract (lead paragraph), content_urls.desktop.page, description
```

**Update `run_pass0a_voice_config.py`:**
- Remove `--hint` as required. Add `--wiki URL` as optional.
- After argparse: if `--wiki` provided, skip the picker and call `summary(url)` directly. Otherwise call `search(name)` and interactively prompt the user: print the 5 results numbered, read stdin for the selection (1-5 or 'none' to fall back to manual hint entry).
- Pass the Wikipedia `extract` + `description` as additional context in the user_payload to Claude:
  ```python
  user_payload = {
      "name": name,
      "wikipedia_extract": wiki_summary["extract"],
      "wikipedia_description": wiki_summary["description"],
      "wikipedia_url": wiki_summary["url"],
      "conference_context": project_ctx,
  }
  ```
- After `call_claude`, also add `wikipedia_url` to the voice_config before writing.
- Fallback `--hint "..."` flag stays for voices with no Wikipedia match.

**Update `pass_0a_voice_config.md`:**
- Add `wikipedia_url` to the voice_config schema (new field, always present when Wikipedia found a match).
- Update the INPUT section: model now receives `wikipedia_extract`, `wikipedia_description`, `wikipedia_url`.
- Tell the model to use the Wikipedia content as primary grounding for classification decisions (type, subtype, voice_mode, hostile_sources, corpus_constraint). Specifically: birth/death dates → type; occupation/role → voice_mode; language/origin → hostile_sources hint.

**Update `node0_validation.py`:**
- Add `VALID_WIKIPEDIA_URL_RE = re.compile(r"^https?://en\.wikipedia\.org/wiki/.+")` or similar.
- Add optional `wikipedia_url` field check — if present, must match the regex. If absent, that's OK (fallback voices without Wikipedia matches).

**Update `io.py`:**
- Add `wikipedia_url` to any schema constants if used.

**Verify:**
- `python3 -c "from flows.shared.wikipedia import search, summary; print(search('Cleopatra')[:2])"` returns sane results.
- Run Pass 0a smoke test (without making an API call): mock the `call_claude` call to verify the payload includes wikipedia fields.

**Commit:** `feat: Wikipedia-grounded disambiguation in Pass 0a (replaces --hint)`

## Phase C — Pass 0b and DR validation

### C.1 — Fix #21: Convert Pass 0b from Opus call → Jinja template

Per `WALKTHROUGH_FIXES_PENDING.md` §21.

Pass 0b's job is pure template instantiation (variant selection by type, substitution, conditional hostile-sources block). No model judgment needed.

**Replace `run_pass0b_dr_prompt.py`:**
- Remove `call_claude` import and `_call_with_retry` wrapper.
- Load a Jinja2 template from `pass_0b_dr_prompt.md`.
- Render with context: `name`, `display_name_with_hint` (name + parenthetical disambiguation if available), `voice_slug`, `type`, `subtype`, `hostile_sources` (bool), `wikipedia_url` (from Fix #15), `voice_mode`, `corpus_constraint`.
- Write rendered output to `inputs/dossiers/_dr_prompts/<slug>_dr_prompt.md`.
- Keep the stamp output (human-readable progress + next-steps). No model API call.
- Remove retry wrapper (not needed for deterministic template rendering).

**Convert `pass_0b_dr_prompt.md` from LLM system prompt to Jinja2 template:**
- File becomes a pure Jinja2 template that renders the DR prompt directly.
- Use `{% if type == "human" %}...{% elif ... %}...{% endif %}` for type variants.
- Use `{% if hostile_sources %}...{% endif %}` for the hostile-source appendix.
- Interpolate `{{ display_name_with_hint }}`, `{{ voice_slug }}`, `{{ wikipedia_url }}` etc.
- Include the full six-section prompt body verbatim from the spec's Pass 1a user prompt, per type variant (see `AI_Assembly_Persona_Pipeline_v3_8.md` lines ~817-1008).
- If `wikipedia_url` is present, include a line in the preamble: `"Starting point for your research: {{ wikipedia_url }} (verify, expand, find what's missing)."`

**Verify:**
- `python3 -c "import jinja2; from pathlib import Path; t = jinja2.Template(Path('personas/flows/shared/prompts/pass_0b_dr_prompt.md').read_text()); print(t.render(name='Cleopatra', display_name_with_hint='Cleopatra VII Philopator', voice_slug='cleopatra', type='human', subtype=None, hostile_sources=True, wikipedia_url='https://en.wikipedia.org/wiki/Cleopatra', voice_mode='observational', corpus_constraint='hostile — read against grain')[:2000])"` renders successfully.
- Run `python3 run_pass0b_dr_prompt.py "Plato"` against an existing voice_config — no API call, produces file. Wall time < 1 second.

**Commit:** `refactor: convert Pass 0b from Opus call to Jinja template (deterministic, zero API cost, zero drift risk)`

### C.2 — Fix #22: Standalone `validate_dr_dossier.py` script

Per `WALKTHROUGH_FIXES_PENDING.md` §22.

**Refactor** `validate_dr_dossier()` function out of `run_persona_pipeline.py` (currently at line 293) into `personas/flows/shared/dr_validation.py`. Update `run_persona_pipeline.py` to import from there.

**Create new script** `personas/scripts/validate_dr_dossier.py`:
```python
#!/usr/bin/env python3
"""Standalone validator for Claude DR dossier files.

Usage: python3 scripts/validate_dr_dossier.py <path_to_dossier.md>
Exit codes: 0 = valid, 1 = invalid (with diagnostic message on stderr).
"""
import sys
from pathlib import Path

# Add personas/ to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from flows.shared.dr_validation import validate_dr_dossier

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 validate_dr_dossier.py <path>", file=sys.stderr)
        sys.exit(2)
    try:
        validate_dr_dossier(Path(sys.argv[1]))
        print("VALID: dossier meets six-section contract and word-count floor")
        sys.exit(0)
    except Exception as e:
        print(f"INVALID: {e}", file=sys.stderr)
        sys.exit(1)
```

Create `personas/scripts/` directory if it doesn't exist.

**Verify:**
- `python3 personas/scripts/validate_dr_dossier.py personas/inputs/dossiers/plato_claude_dr.md` exits 0.
- `python3 personas/scripts/validate_dr_dossier.py /tmp/nonexistent.md` exits 1 (file not found error).
- `echo "short" > /tmp/test.md && python3 personas/scripts/validate_dr_dossier.py /tmp/test.md` exits 1 (too short + missing headings).

**Commit:** `feat: standalone validate_dr_dossier.py for human pre-filing check`

## Phase D — Option B reorder

### D.1 — Fix #23: Perplexity + Gemini before Claude DR

Per `WALKTHROUGH_FIXES_PENDING.md` §23. Biggest change in Round 2.

**Goal:** Pass 1a (Perplexity) and Pass 1b (Gemini) run BEFORE the manual Claude DR session. Their findings scaffold Pass 0b's DR prompt so Claude DR starts from grounded research instead of zero.

**Architecture (B-split-2):**
- `run_pass0a_voice_config.py` — unchanged (voice_config + review doc).
- **New:** `run_phase0_1_research.py` — runs Pass 1a + Pass 1b in parallel, then renders Pass 0b Jinja template with their outputs + Wikipedia grounding, writes DR prompt, exits.
- `run_persona_pipeline.py` — strips out Pass 1a + 1b + 0b entry points; starts from Pass 1-merge. Still reads Claude DR from disk via Pass 1a-DR load.

**Implementation steps:**

**1. Create `personas/run_phase0_1_research.py`:**
- Argparse: takes voice name (must match a voice_config on disk).
- Loads voice_config, validates via `validate_input()`.
- Runs Pass 1a (Perplexity sonar-deep-research) — copy the `_pass_1a` function from `run_persona_pipeline.py`. Writes to `runs/<slug>/01_research/perplexity_dossier.json`.
- Runs Pass 1b (Gemini broad scan) — copy the `_pass_1b` function. Writes to `runs/<slug>/01_research/gemini_broad_scan.json`.
- Runs in parallel via `concurrent.futures.ThreadPoolExecutor` (each is an API call, so I/O-bound).
- Renders Pass 0b Jinja template (from Fix #21) — passes `perplexity_dossier`, `gemini_broad_scan`, `wikipedia_url`, plus all existing voice_config fields.
- Writes DR prompt to `inputs/dossiers/_dr_prompts/<slug>_dr_prompt.md`.
- Prints human-readable next-steps (paste into claude.ai, save result, run `run_persona_pipeline.py`).

**2. Update Pass 0b Jinja template (`pass_0b_dr_prompt.md`):**
- Accept two new context variables: `perplexity_findings` (str, from `perplexity_dossier.text`) and `gemini_findings` (str, from `gemini_broad_scan.text`).
- Add a new scaffolding block in the DR prompt body:
  ```
  {% if perplexity_findings %}

  PRIOR RESEARCH FINDINGS

  Two research sources have already scanned this voice. Use their findings as your starting point — verify what they found, expand depth, identify what they missed. Claude Deep Research's job is to go deeper than these did.

  Perplexity sonar-deep-research (cited academic sources) identified:
  {{ perplexity_findings }}

  ---

  Gemini broad scan (lesser-known material, cross-disciplinary) identified:
  {{ gemini_findings }}

  ---
  {% endif %}
  ```
- Place the scaffolding block after the type-variant body but before the hostile-sources appendix.

**3. Update `run_persona_pipeline.py`:**
- Remove Pass 1a (`_pass_1a` and its invocation around line 86-96) — move to `run_phase0_1_research.py`.
- Remove Pass 1b (`_pass_1b` and its invocation around line 131-141) — same.
- At pipeline startup, validate that both `runs/<slug>/01_research/perplexity_dossier.json` and `runs/<slug>/01_research/gemini_broad_scan.json` exist (they were produced by `run_phase0_1_research.py`). If missing, `sys.exit` with clear message: `"Pass 1a + 1b outputs missing. Run run_phase0_1_research.py first."`
- Pass 1a-DR load (the Claude DR file read) stays in `run_persona_pipeline.py`.
- Pass 1-merge (three-way) stays — now reads all three cached outputs from disk.

**4. Update the pipeline spec `AI_Assembly_Persona_Pipeline_v3_8.md`:**
- Rename to `AI_Assembly_Persona_Pipeline_v3_9.md` via `git mv`.
- Add a new "Phase 0.5: Pre-DR Research" section describing Pass 1a + Pass 1b running before DR, scaffolding Pass 0b.
- Update Phase 1 section: it now starts at Pass 1-merge (Pass 1a, 1b, 1a-DR already cached at this point).
- Update the "Pipeline at a Glance" table.
- Bump pipeline_version to "3.9" in `run_persona_pipeline.py`'s final assembly metadata.

**5. Update `personas/README.md`, `CLAUDE.md`, `docs/CURRENT_STATE.md`, `docs/README.md`** — reflect the new flow:
- New script: `run_phase0_1_research.py`
- Spec: v3.8 → v3.9

**Verify:**
- `python3 -c "import run_phase0_1_research"` imports cleanly.
- Existing voice_configs validate under updated `node0_validation.py`.
- Dry-run `run_phase0_1_research.py "Plato"` without actual API calls (mock or inspect only the non-LLM portions).
- `run_persona_pipeline.py "Plato"` gracefully errors when `perplexity_dossier.json` is missing.

**Commit message:** `feat: Option B reorder — Perplexity + Gemini run before Claude DR, scaffold DR prompt with their findings`

## Phase E — Final verification and push

### E.1 — Import smoke tests

```bash
cd /Users/aienvironment/Desktop/ai-assembly/personas
python3 -c "import run_pass0a_voice_config"
python3 -c "import run_pass0b_dr_prompt"
python3 -c "import run_phase0_1_research"
python3 -c "import run_persona_pipeline"
python3 -c "from flows.shared.node0_validation import validate_input"
python3 -c "from flows.shared.dr_validation import validate_dr_dossier"
python3 -c "from flows.shared.wikipedia import search, summary"
python3 -c "from flows.shared.io import load_prompt; load_prompt('pass_0a_voice_config'); load_prompt('pass_0b_dr_prompt')"
```

All should succeed.

### E.2 — Validate existing voice_configs

Same script as Round 1 E.2. All voice_configs should pass `validate_input()` under the updated schema (now 9 fields post-drops: name, type, subtype, voice_mode, hostile_sources, corpus_constraint, conference_context, wikipedia_url [optional], + primary_text_sources [still optional manual override]).

### E.3 — Spec bump + briefing refs

Already done in D.1 step 4/5. Verify:
- `docs/AI_Assembly_Persona_Pipeline_v3_9.md` exists, `v3_8.md` does NOT.
- All references to `v3_8` in the docs have been updated to `v3_9`.

### E.4 — Push

```bash
git push -u origin walkthrough-fixes-round2-2026-04-17
```

Report branch URL and a summary of completed vs skipped items.

---

## Notes for Sonnet

- **If you hit an ambiguity:** stop and add a comment to `WALKTHROUGH_FIXES_PENDING.md` under `## Sonnet Round 2 Questions`, then ask.
- **If a verify step fails:** stop immediately.
- **Do NOT edit:** `personas/runs/**`, `runtime/runs/**`, `personas/inputs/voices/_archive/**`.
- **Commit cadence:** one commit per numbered sub-phase (A.1, A.2, ..., D.1, E.3). Phase E.4 is just push, no commit.
- **Branch must be clean at the end:** no uncommitted changes, no untracked files outside `.gitignore`.
- **Write a handoff note at `personas/notes/SONNET_HANDOFF_ROUND_2.md` if context is running low** — same pattern as Round 1. Record commit SHAs + next item + any notes.

## Dependency summary

- A.1–A.3: independent of each other and of all Phase B/C/D. Run in order for clean history.
- B.1, B.2: depend on A (schema drops reflected in validation).
- B.3 (Wikipedia): independent of A/B.1/B.2 but MUST run before C.1 (Pass 0b template needs `wikipedia_url` context).
- C.1 (Jinja template): depends on B.3 (template variable added).
- C.2 (standalone script): independent; can run any time.
- D.1 (Option B reorder): depends on C.1 (needs Jinja template), B.3 (needs wikipedia_url context), all of A (schema clean).

Execute A → B → C → D → E in order.
