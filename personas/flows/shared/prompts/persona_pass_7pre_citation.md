{# Pass 7-pre — Citation Verification (Claude Sonnet). v3.7 Node 7-pre.
   Verifies every direct quote, textual reference, and attributed claim in the
   assembled persona card against:
     (a) the primary text passages fetched in Node 1c — strongest anchor
     (b) the merged research dossier (Perplexity + Claude DR + Gemini)
   Voice-mode branches:
     - philosophical / observational human → standard citation verification
       (with interpretive-flag handling for observational)
     - fictional → consistency verification (no biographical facts to verify)
     - hostile_sources=true → additional propagandistic-framing checks
#}
You are verifying citations and factual claims in a persona specification
document. Your output is structured JSON; downstream automation acts on it.

CRITICAL CAVEAT: The Phase 1 dossier was itself AI-generated (Perplexity +
Claude DR + Gemini). Verifying the card against the dossier catches internal
inconsistencies but does NOT guarantee factual accuracy. The PRIMARY TEXTS are
the strongest verification anchor — actual passages, not AI summaries.

VERIFICATION MODE (driven by voice metadata):

{% if type == "fictional" %}
CONSISTENCY VERIFICATION (fictional voice — no biographical facts to verify):
- Does the constitution contradict itself? (Two principles that cannot both hold.)
- Does the reasoning_method align with the constitution? (Method presupposes
  the principles it claims to apply.)
- Does the voice specification (rhetorical_mode, characteristic_moves,
  register_and_tone) match what the primary text excerpts actually sound like?
- Are [attributed by narrative function] tags used honestly — is the
  interpretive leap named, or is it disguised as textual fact?
- Does knowledge_boundary correctly reflect what the text contains vs. what
  it doesn't?

Flag INCONSISTENCIES, not unverified citations.
{% elif voice_mode == "observational" %}
OBSERVATIONAL VERIFICATION — most of the card's intellectual content is
INTERPRETIVE (tagged [scholarly consensus] or [inference] per Pass 3).
Citation verification focuses on:
  (a) direct quotes attributed to the figure
  (b) specific factual claims (dates, places, events)
  (c) claims about the figure's stated views
Interpretive constructions are NOT "citations" — flag them as
[interpretive — verify reasoning, not source], not as UNVERIFIED.
{% else %}
STANDARD VERIFICATION (philosophical or human voice):
Extract every direct quote, specific textual reference (with work title and
section/page), and attributed claim. Verify each against the primary texts
and dossier.
{% endif %}

{% if hostile_sources %}
HOSTILE-SOURCE ADDITIONAL CHECKS (hostile_sources=true):
- Flag any claim sourced ONLY from hostile witnesses that has been adopted
  into the card without scholarly-reconstruction support — these may carry
  propagandistic framing.
- Verify that `character` and voice fields are built from [reconstruction] and
  [own voice] material, not from hostile characterisations.
- Check that `topics_requiring_care` includes the hostile-source situation
  itself (how the figure has been misrepresented).
- If `voice_basis` is "reconstructed", verify that the reconstruction sources
  are identified and defensible.
{% endif %}

OUTPUT SCHEMA — return ONLY this JSON object, no markdown fences, no preamble:

{
  "verification_mode": "standard" | "observational" | "fictional",
  "hostile_source_check": true | false,
  "items": [
    {
      "claim": "<the exact claim, quote, or reference under verification>",
      "source_field": "<which persona card field it appears in>",
      "status": "VERIFIED" | "UNVERIFIED" | "DOSSIER_ONLY" | "INTERPRETIVE" | "INCONSISTENT" | "HOSTILE_FLAGGED",
      "evidence": "<for VERIFIED: which primary text or dossier section supports it. for UNVERIFIED: why it could not be traced. for DOSSIER_ONLY: which dossier section. for INCONSISTENT: which other field it conflicts with.>"
    }
  ],
  "summary": {
    "verified": <int>, "unverified": <int>,
    "dossier_only": <int>, "interpretive": <int>,
    "inconsistent": <int>, "hostile_flagged": <int>
  },
  "overall": "PASS" | "REVIEW_NEEDED",
  "review_notes": "<one paragraph describing the most important issues found, or 'No issues' if PASS>"
}

RED FLAGS to watch for:
- Quotes that sound "too perfect" for the argument they're supporting
- Quotes with precise page numbers but no matching source in the primary texts
  or dossier
- Statistics or dates given with false precision
- Claims attributed to a named scholar that don't appear in the dossier
- For hostile-source voices: claims that match the hostile narrative without
  reconstruction support
