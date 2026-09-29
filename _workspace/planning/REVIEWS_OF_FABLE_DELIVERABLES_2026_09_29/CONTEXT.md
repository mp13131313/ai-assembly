# Context for reviewers (what changed after the Fable reports were written)

Repo: /Users/aienvironment/Desktop/AI Assembly/code (branch main). Reports were written 2026-09-28 at commits 0998fa2 / 4e61444 / 40fe490. Since then, on main:
- 02006f5 (runtime OPEN_ITEMS C67): speaker-ID env chain restored (TRANSCRIPTION_CLAUDE_MODEL); C49 fallback re-runs Speaker ID on retry + status.json "warnings" + dashboard badge + orchestrator log line; held voices excluded from rebuilt night index; loader refuses "manual": true outside personas.dr_*; restamp handles cited_voice_slug/name; empty ladder env raises ModelRoutingError; *_THINKING env rule documented; C66 test uses a Barrier; editor threads project_root to council_config lookup; dormant Step-3 peer names via voice_display_name; CLAUDE.md voice-spec summary fixed.
- f7e0d4c (voices OPEN_ITEMS §37): sentinel_regen.py repaired (new `sandbox` subcommand; `regen --project <sandbox> --baseline-project <prod>` diffs regenerated PASS OUTPUTS against production pass outputs — NOT against the assembled cards; it still re-runs the whole persona pipeline after invalidating one pass, incl. Derive); patch_walker requires the final key; Wikisource extraction fixed (personas venv has NO bs4 → regex fallback now drops script/style, matches nested divs); fetch redirects re-checked for SSRF + more private ranges; the 1c review list marks fetches < 2000 chars as SUSPECT.
- 129d314 + athens-2026 e4c4e39: stray "**" stripped from all 13 published dossier bodies; data_views rebuilt.
- Operator decisions 2026-09-28: Stage 4 spend cap USD 10; Athens reflection record left as published (fix the converter going forward, C68 A1); Night-3 continuity: correct the spec now, decide the code in Stage 5 (C68 A10); Lovelace re-fetched, NO card patch needed (her Notes were in the corpus via fourmilab + psychclassics, and her excerpts drew on both).
- Tests now: runtime 385, ingest 114, personas 259.

Rules for you: read-only. No API calls, no pipeline/persona runner scripts, never pytest over personas/scripts/. athens-2026 (/Users/aienvironment/Desktop/AI Assembly/projects/athens-2026) read-only. Write ONLY your review file in the scratchpad folder given in your task. Trackers: _workspace/planning/{runtime,voices}/OPEN_ITEMS.md, _workspace/planning/doc_infrastructure_backlog.md, roadmap _workspace/planning/PLAN_2026_06_12_post_athens_roadmap.md.

# Output file format (markdown)
# Review of <deliverable path>
## Verdict — 3 lines: overall quality; how far to trust it; the single biggest issue.
## Findings, one by one — in the document's own order and numbering. Table: | ID | claim (short) | verdict | evidence / reason |
   verdict ∈ VERIFIED (you checked code/data yourself — say how) · PLAUSIBLE (consistent, not checked) · DOUBTFUL (reason) · STALE (fixed or changed since — cite commit) · WRONG (evidence).
   Spot-check at least the 5–8 most consequential claims yourself against code/data.
## Problems with the document — contradictions, missing evidence, overreach beyond the brief, rule breaches (did it stay read-only / no API calls?).
## Questions for the originating session — at most 5; only questions that session can answer from its own work and that matter for a decision. For each: the question, why it matters, what answer would change what.
## Operator decisions it asks for — list, each with the document's recommendation.
