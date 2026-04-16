{# Pass 1-merge — Three-way contradiction check (Claude Sonnet).
   v3.7 Node 1-merge, Approach C variant.
   Inputs: Perplexity dossier + (optional) Claude Deep Research dossier + Gemini broad scan.
   Output: JSON list of factual contradictions across the available sources. #}
=== SOURCE A: Perplexity sonar-deep-research ===
{{ perplexity_dossier }}

{% if claude_dr_dossier %}
=== SOURCE B: Claude Deep Research (Opus 4.6 + extended thinking) ===
{{ claude_dr_dossier }}
{% endif %}

=== SOURCE C: Gemini 2.5 Pro broad scan ===
{{ gemini_broad_scan }}

Identify factual contradictions across these sources. For each:
- Quote the conflicting claims (label which source each comes from: A, B, or C)
- Note whether this is likely a factual error or a known scholarly disagreement
- If a claim appears in only one source and is omitted by others, that is NOT a contradiction —
  it is a coverage gap. Only flag genuine disagreements.

Output ONLY valid JSON in one of these two formats:
{"status": "CLEAN"}
or
{"status": "CONTRADICTIONS", "items": [
  {
    "claims": [{"source": "A", "claim": "..."}, {"source": "B", "claim": "..."}, ...],
    "assessment": "factual error" or "scholarly disagreement"
  }
]}

Return ONLY the JSON object. No markdown fences, no preamble.
