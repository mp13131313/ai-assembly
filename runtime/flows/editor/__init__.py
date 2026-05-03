"""Editor Pipeline — package marker.

Two-stage pipeline per docs/AI_Assembly_Editor_Pipeline.md:

  Stage 1 (deterministic): theme_routing assigns each Step 2 voice artifact
  to exactly one dossier (its primary contribution) and identifies which
  dossiers should mention the voice in their In Brief column.

  Stage 2 (one Anthropic call per dossier on Opus 4.7): Claudia Pinchbeck —
  the editor — reads each theme's submissions and writes the dossier
  (front + article + theme + per-artifact headnotes).

Outputs land under <run_dir>/05_editor/ and are mirrored to
<PROJECT_ROOT>/published_artifacts/dossiers/night_<N>/ for the microsite.
"""
