# Claude Deep Research Dossiers

This directory holds manually-produced Claude Deep Research dossiers — one per voice — used as a primary source for Pass 1a alongside Perplexity (Approach C).

## Workflow per voice

1. Open claude.ai, start a Deep Research session with **Opus 4.6 + extended thinking**.
2. Use the prompt template at `flows/shared/prompts/persona_pass_1a_research_human.md` (or the non-human / fictional variant).
3. Substitute the voice's name and any conditionals (e.g. `hostile_sources`).
4. Run Deep Research. Wait 60-120 minutes.
5. Export the response as markdown and save it here as `<voice_slug>_claude_dr.md` (e.g. `whanganui_river_claude_dr.md`, `octopus_claude_dr.md`).
6. Reference the file in the voice's input JSON: `"pass_1a_claude_dr_file": "inputs/dossiers/<voice_slug>_claude_dr.md"`
7. Run the pipeline. Pass 1-merge will three-way-check Perplexity + Claude DR + Gemini.

## Status

| Voice | File | Status |
|---|---|---|
| Plato | plato_claude_dr.md | TODO |
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
</content>
