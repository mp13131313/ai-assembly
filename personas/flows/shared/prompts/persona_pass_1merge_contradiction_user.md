Research Dossier (Perplexity):
{{ research_dossier }}

Broad Scan (Gemini):
{{ broad_scan }}

Identify any factual contradictions between them. For each:
- Quote the conflicting claims from each source
- Note whether this is likely a factual error or a known scholarly disagreement

Output ONLY valid JSON in one of these two formats:
{"status": "CLEAN"}
or
{"status": "CONTRADICTIONS", "items": [{"claim_a": "...", "claim_b": "...", "assessment": "factual error" or "scholarly disagreement"}]}
