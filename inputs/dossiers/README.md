# Claude Deep Research Dossiers

This directory holds manually-produced Claude Deep Research dossiers — one per voice — used as a primary source for Pass 1a alongside Perplexity (Approach C).

## Workflow per voice

1. Open claude.ai, start a Deep Research session with **Opus 4.6 + extended thinking**.
2. Use the briefing at `CLAUDE_DR_BRIEFING.md` (this directory) — it contains the paste-ready prompt template, per-voice flag table, voice-type adjustments for non-human/fictional voices, and common-pitfall warnings.
3. Substitute the voice's name and apply the hostile-source protocol if the per-voice table flags it.
4. Run Deep Research. Wait 60-120 minutes.
5. Export the response as markdown and save it here as `<voice_slug>_claude_dr.md` (e.g. `whanganui_river_claude_dr.md`, `octopus_claude_dr.md`).
6. Before saving, verify the output matches the six-section research-dossier structure and is NOT a persona card (see "Common pitfalls" in the briefing). If it drifted, regenerate.
7. Reference the file in the voice's input JSON: `"pass_1a_claude_dr_file": "inputs/dossiers/<voice_slug>_claude_dr.md"`
8. Run the pipeline. Pass 1-merge will three-way-check Perplexity + Claude DR + Gemini.

## Status

| Voice | File | Status |
|---|---|---|
| Plato | plato_claude_dr.md | TODO — v1 archived to `_archive/plato_claude_dr_v1_finished_card.md` (was a persona card, not a research dossier) |
| Cleopatra | cleopatra_claude_dr.md | TODO |
| Ibn Battuta | ibn_battuta_claude_dr.md | TODO |
| Scheherazade | scheherazade_claude_dr.md | TODO |
| Ada Lovelace | ada_lovelace_claude_dr.md | TODO |
| Dostoevsky | dostoevsky_claude_dr.md | TODO |
| Hannah Arendt | hannah_arendt_claude_dr.md | TODO |
| Bob Marley | bob_marley_claude_dr.md | TODO |
| Audrey Tang | audrey_tang_claude_dr.md | TODO |
| Peter Thiel | peter_thiel_claude_dr.md | TODO |
| Whanganui River | whanganui_river_claude_dr.md | TODO |
| Octopus | octopus_claude_dr.md | TODO |
