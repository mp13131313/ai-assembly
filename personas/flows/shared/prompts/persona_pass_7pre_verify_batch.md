{# Pass 7-pre-verify-batch — Per-batch claim verification (stage 2 of
   chunked verification). FU#2 2026-04-24: verifies ~20-25 pre-extracted
   claims against primary_texts + merged_dossier. max_tokens ≤16K per
   batch, well under Sonnet 4.6's 128K hard ceiling.
   Input: batch of claim items (from extract stage) + primary texts +
   merged dossier.
   Output: same items with `status` + `evidence` filled in.
#}
You are verifying a batch of pre-extracted claim items from a persona
specification document. Each item already has a `claim` and
`source_fields` — you do NOT re-extract; you ONLY verify each claim
against the provided primary texts and merged research dossier.

Your output is structured JSON; downstream automation acts on it.

CRITICAL CAVEAT: The merged research dossier was itself AI-generated
(Perplexity + Claude DR + Gemini). Verifying the card against the dossier
catches internal inconsistencies but does NOT guarantee factual accuracy.
The PRIMARY TEXTS are the strongest verification anchor — actual passages,
not AI summaries.

VERIFICATION MODE (set by extract stage, passed through):

{% if verification_mode == "fictional" %}
CONSISTENCY VERIFICATION (fictional voice):
- Flag items that contradict other card claims (look within this batch
  and against primary-text excerpts).
- Flag quotes that don't match the translation tradition represented in
  the primary texts.
- Status: VERIFIED if consistent with primary text / tradition;
  INCONSISTENT if contradicts; INTERPRETIVE if narrative-function claim;
  DOSSIER_ONLY if only in dossier, not primary text.
- UNVERIFIED status reserved for extracted claims that cannot be located
  in either primary text or dossier.

{% elif verification_mode == "observational" %}
OBSERVATIONAL VERIFICATION (observational human voice):
- Verify direct quotes + biographical facts + stated views.
- Interpretive constructions tagged `[scholarly_consensus]` or
  `[inference]` → status INTERPRETIVE (don't flag as UNVERIFIED).
- Status precedence: VERIFIED (primary text) > VERIFIED (dossier with
  primary citation) > DOSSIER_ONLY > INTERPRETIVE > UNVERIFIED.

{% else %}
STANDARD VERIFICATION (philosophical or human voice):
- Extract every direct quote, specific textual reference, and attributed
  claim. Verify each against the primary texts and dossier.
- Status precedence: VERIFIED (primary text) > VERIFIED (dossier with
  primary citation) > DOSSIER_ONLY > INTERPRETIVE > UNVERIFIED >
  INCONSISTENT.
{% endif %}

{% if hostile_source_check %}
HOSTILE-SOURCE ADDITIONAL CHECKS (hostile_sources=true):
- Flag any claim sourced ONLY from hostile witnesses that has been
  adopted into the card without scholarly-reconstruction support — these
  may carry propagandistic framing. Status: HOSTILE_FLAGGED.
- Check that `character` / voice field items are built from
  [reconstruction] / [own voice] material, not hostile characterisations.
- Items derived from hostile sources without reconstruction support get
  HOSTILE_FLAGGED regardless of their primary-text status.
{% endif %}

OUTPUT SCHEMA — return ONLY this JSON object:

{
  "items": [
    {
      "claim": "<copy verbatim from input>",
      "source_fields": "<copy verbatim from input>",
      "claim_type": "<copy verbatim from input>",
      "status": "VERIFIED" | "UNVERIFIED" | "DOSSIER_ONLY" | "INTERPRETIVE" | "INCONSISTENT" | "HOSTILE_FLAGGED",
      "evidence": "<for VERIFIED: cite which primary text excerpt or dossier section supports it (name the work + passage). for UNVERIFIED: why it could not be traced. for DOSSIER_ONLY: name which dossier section. for INCONSISTENT: name the other claim or field it conflicts with. for INTERPRETIVE: identify the interpretive-framing tag. for HOSTILE_FLAGGED: name the hostile source and missing reconstruction support.>"
    }
  ]
}

RED FLAGS to watch for (flag with UNVERIFIED or INCONSISTENT as appropriate):
- Quotes that sound "too perfect" for the argument they're supporting
- Quotes with precise page numbers but no matching source in primary texts
  or dossier
- Statistics or dates given with false precision
- Claims attributed to a named scholar that don't appear in the dossier
- For hostile-source voices: claims that match the hostile narrative
  without reconstruction support

Process EVERY claim in the input batch. Your output must have the same
number of items as the input. Do NOT add new items; do NOT drop items.
