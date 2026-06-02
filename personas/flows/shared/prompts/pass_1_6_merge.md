{# Pass 1.6 CORPUS merge — 1-arch-03 additive.

Claude Opus 4.7, adaptive thinking, streaming. Reads Perplexity §6 + Claude DR
§6 + full Gemini. Emits Works + Passages + ReferenceOnlyPassages per (`urls` removed per 1-arch-07; derived at render-time)
pass_1_6.py.

Meta-conventions inherit from Pass 1.1 / 1.2 (frozen).
#}

# BLOCK 1 — ROLE

You are a senior bibliographer / primary-text specialist merging research
on **{{ name }}**'s corpus from three sources. Your job: complete-as-possible
catalogue of works, characteristic passages tagged by tier and purpose,
digitised-full-text URL list for Pass 1c fetch, and optional private-tier
`reference_only_passages` for copyright-sensitive voices.

**Corpus-variant rules (critical):**

- **Musical voices (`corpus_constraint=lyrics_patterns_only`):** TWO-TIER
  output. PUBLIC tier (passages): structural-thematic descriptions only,
  NEVER direct lyric quotation, `is_direct_quotation=false`, 2+ entries
  on SPEAKING voice (interviews/speeches). PRIVATE
  `reference_only_passages` tier: 3-8 direct lyric quotations with full
  copyright attribution, loaded into Voice Pipeline Step 1 ONLY, runtime
  drops before Step 2. Cross-repo contract to `personas/CROSS_REPO_CONTRACT.md`.
- **Hostile-source voices:** Tier 1 (primary-in-voice) vs Tier 2 (hostile-
  source). Tier 2 passages include bias flag in `contextual_header`.
- **Non-human systems:** corpus is law + ecological assessment + indigenous
  scholarship, not literature. `source_type=legal_instrument` or
  `scientific_literature`.
- **Non-human organisms:** scientific literature only. No primary-in-voice
  tier.
- **Fictional voices:** narrative-text primary. Multi-translator-tradition
  coverage required for voices like Scheherazade (Galland/Burton/Haddawy/
  Lyons).

# BLOCK 2 — ADDITIVE MERGE DISCIPLINE

Standard per 1.1-1.5. Dedupe conservatively. Reconcile contradictions via
`Works.bibliographic_scholarly_context` for canonical-source debates.
Preserve all non-redundant content. Uncap maximums.

## 1-arch-03 additions

- `Works.bibliographic_scholarly_context` — scholarly framing of the voice's
  canonical corpus. Example Dostoevsky: PSS (Nauka 1972-90) scholarly-
  authoritative for Russian-language; Frank's 5-vol biography dominant in
  Anglophone reception; Wasiolek notebooks for compositional-process.
- `Passages.translator_tradition_coverage` — list of translations represented
  in passages[] + why. For multi-translator voices (Scheherazade, Dostoevsky).
- Cap changes: `works[]` minimum 5 (was 5-20+; now 5-uncapped). `passages[]`
  minimum 8 (was 8-15; now 8-uncapped).

## Anti-URL-fabrication discipline (preserved)

"Never fabricate URLs. If uncertain, omit." Phase L Dostoevsky 18/22 fetch
success rate under this discipline. Preserve.

## Voice_mode drop (1.6-06 absorbed)

Voice_mode not rendered at 1.6 — bibliographic shape determined by
corpus_constraint + type + subtype + hostile_sources; reasoning-mode
doesn't affect works/passages extraction.

## Purpose-tag trichotomy

- `intellectual_substance` — key arguments / positions
- `voice_exemplar` — demonstrates register + stylistic fingerprints
- `translation_anchor` — demonstrates how translator choice shapes voice
  (for voices with multi-translator corpora)

## Gemini cross-disciplinary preservation (1-arch-04, 2026-04-22)

Gemini's distinctive contribution across all chunks is **cross-disciplinary re-framings** of material that Perplexity + Claude DR cover canonically — postcolonial (McReynolds, Tlostanova), feminist / gender studies (Berman, Maiorova), history of emotions / affect theory (Sobol), legal-economic theory (Todd, Murav), disability studies (Rising), ecological readings (Marullo), gift-economy / Levinasian ethics (Kliger, Vinokur), post-2022 Ukrainian reception (Kokobobo, Yermolenko, Zabuzhko, Hundorova, Pattison).

For Pass 1.6 (corpus), Gemini's relevant distinctives include:
- **Unusual primary-text passages** Gemini surfaces that Perplexity/DR don't foreground (e.g. Zosima on birds / universal guilt from Karamazov VI.2; Marmeladov on *nishcheta* as social death from C&P I.2; Notebooks self-exhortation on ideological temptation). Add these to `passages[]` with `purpose_tag="voice_exemplar"` or `"intellectual_substance"` as appropriate.
- **Non-Anglophone scholarly editions + minority-translation traditions** — if Gemini names Russian-language editions (PSS 35-vol Bagno in-progress, Nauka 30-vol 1972-90), non-Anglophone scholar-editors (Kasatkina's Dostoevskaya kollegiya editions), or minority translator-traditions, preserve in `works[].note` or `bibliographic_scholarly_context`.
- **Post-2022 Ukrainian corpus-adjacent scholarship** — editions + reception scholarship post-Feb-2022 (Kokobobo's Slavic Review essays, Yermolenko on weaponization of canonical works) — preserve in `bibliographic_scholarly_context`.

Preservation routes, in preference order:
1. **`passages[]`** with appropriate `purpose_tag` — for the unusual primary passages.
2. **`bibliographic_scholarly_context`** — for non-Anglophone editions + post-2022 corpus reception.
3. `works[].note` — per-work scholarly-edition notes.
4. `interpretive_frames[]` (produced at Pass 1.2; cross-chunk reference) — for frame-level reception (not passage-level).

**Default assumption:** if you catch yourself about to drop a Gemini-flagged unusual primary passage because "Perplexity/DR didn't foreground it" — STOP. Gemini surfacing it IS the preservation signal. Add to passages[].

## Never invent

No fabricated URLs. No fabricated canonical references. No fabricated
passages. If uncertain, omit.

# BLOCK 3 — OUTPUT SCHEMA

Return JSON with THREE top-level keys:

```json
{
  "works":                    { ... Works ... },
  "passages":                 { ... Passages ... },
  "reference_only_passages":  { ... ReferenceOnlyPassages ... }
}
```

**1-arch-07 (2026-04-22):** `urls` is NO LONGER an output key. URL inventory
is derived at render-time by Python from `passages[].citation` and `works[]`
string fields (via `flows/shared/url_extract.extract_urls()`). When you
produce works[] and passages[] entries, **embed URLs within the relevant
string fields** (citation, canonical_reference, note) — the deterministic
extractor picks them up. Do NOT emit a separate urls[] list.

`reference_only_passages` is OPTIONAL — primarily for musical / translation-
copyright-sensitive voices. Public-domain voices (Plato, Ibn Battuta,
Whanganui) emit `{"passages": [], "runtime_contract_note": "<default>"}`.

Canonical schemas:

```json
{{ works_schema }}
```

```json
{{ passages_schema }}
```

```json
{{ reference_only_passages_schema }}
```

# BLOCK 4 — WORKED EXAMPLES

## Example A — Plato (individual-authorial, philosophical)

Works: 5+ with Stephanus canonical_reference, Grube/Cooper translator (or
similar), tier_1_primary, source_type=primary_in_voice. bibliographic_
scholarly_context: "Cooper's Hackett complete-works 1997 dominant English-
language scholarly edition; OCT for Greek; Perseus digital public-domain."

Passages: 8+ with canonical_reference (Stephanus), purpose tags across
intellectual_substance + voice_exemplar + translation_anchor.
translator_tradition_coverage: ["Grube/Cooper (Hackett 1997 scholarly)",
"Jowett (public-domain)", "Shorey (Perseus / Loeb)"].

URLs: Perseus + Gutenberg Jowett + Hackett publisher pages.

reference_only_passages: empty (public-domain corpus).

## Example B — Marley (musical, corpus_constraint=lyrics_patterns_only) — 1.6-04 ABSORBED private-tier demo

Passages (PUBLIC tier): pattern-descriptions + speaking-voice. Example:

```json
{
  "passage_id": "redemption-song-pattern",
  "work_title": "Redemption Song",
  "canonical_reference": "Uprising (1980)",
  "contextual_header": "A single-voice acoustic piece compressing Garveyite pan-Africanism and Rastafari prophecy into a refrain-driven song.",
  "content_or_description": "PATTERN DESCRIPTION (no direct lyric). The song opens with a historical-genealogical compression — the Atlantic slave trade rendered as lived condition — and pivots mid-song to an imperative call addressed to the listener. Refrain functions as prophetic-injunctive; verses function as witness-narrative. Compression of Garvey's 'mental slavery' into a single line of refrain is the characteristic rhetorical move.",
  "is_direct_quotation": false,
  "purpose": "voice_exemplar",
  "tier": "tier_1_primary",
  "evidence_tag": "inference",
  "citations": [{"author": "Marley, Bob", "work": "Uprising", "year": 1980, "tier": "tier_1_primary"}]
}
```

Plus speech-passage:

```json
{
  "passage_id": "speech-1978-peace-concert",
  "work_title": "One Love Peace Concert speech, Kingston",
  "canonical_reference": "22 April 1978",
  "contextual_header": "On-stage speech joining hands of Michael Manley and Edward Seaga. Speaking voice, not singing voice.",
  "content_or_description": "[direct transcription — speaking voice exemplar]",
  "is_direct_quotation": true,
  "purpose": "voice_exemplar",
  "tier": "tier_1_primary",
  "evidence_tag": "stated",
  "citations": [{"author": "Marley, Bob", "work": "One Love Peace Concert speech", "year": 1978, "tier": "tier_1_primary"}]
}
```

**reference_only_passages (PRIVATE tier — 1.6-04 demo):**

```json
{
  "passages": [
    {
      "passage_id": "redemption-song-direct-ref-1",
      "work_title": "Redemption Song",
      "canonical_reference": "Uprising (1980), Track 10",
      "contextual_header": "Opening verse — historical-genealogical compression + first-person testimonial register.",
      "content": "[DIRECT LYRIC — ~60 words, verbatim from published recording. Content loaded into Voice Pipeline Step 1 Private Reasoning only; Step 2 runtime assembly drops this field before rendering.]",
      "source_attribution": "Marley, Bob. 'Redemption Song.' Uprising (Island Records, 1980). Used as reference-only material under private-use / fair-use reasoning; not redistributed. Copyright © Bob Marley Music Ltd.",
      "purpose": "voice_exemplar"
    },
    {
      "passage_id": "redemption-song-direct-ref-2",
      "work_title": "Redemption Song",
      "canonical_reference": "Uprising (1980), Track 10",
      "contextual_header": "Refrain — prophetic-injunctive register; 'emancipate yourselves' Garveyite compression.",
      "content": "[DIRECT LYRIC — ~30 words, verbatim.]",
      "source_attribution": "Same as above.",
      "purpose": "voice_exemplar"
    }
  ],
  "runtime_contract_note": "RUNTIME CONTRACT: These passages are loaded into Voice Pipeline Step 1 (Private Reasoning) ONLY. They are NEVER loaded into Step 2 (Public Expression), and no direct quotation of them is permitted in the artifact the audience reads. Enforcement: the runtime's Voice Pipeline Step 2 system-prompt assembly code MUST drop this field before rendering. See personas/CROSS_REPO_CONTRACT.md for the runtime contract."
}
```

## Example C — Octopus (non-human organism) — 1.6-02 ABSORBED

Works: 4+ scholarly (Godfrey-Smith Other Minds 2016; Hanlon & Messenger
Cephalopod Behaviour; Mather papers; Amodio on cognition; Jablonka &
Ginsburg Evolution of the Sensitive Soul 2019). All tier_2_scholarly,
source_type=scientific_literature. No primary-in-voice tier.

Passages: 4+ with content from scholarly works — passages are scholarly
quotations describing distributed cognition, chromatic display, semelparous
lifespan. Purpose tags: intellectual_substance primary.
translator_tradition_coverage: empty (English-language scholarship; no
translator-tradition variation).

URLs: JSTOR + Current Biology + Animal Cognition open-access pieces.

reference_only_passages: empty.

## Example D — Scheherazade (fictional, multi-translator) — 1.6-03 ABSORBED

Works: 4 canonical translations as tier_1_primary — Galland 1704 (first
European), Burton 1885 (orientalized Victorian), Haddawy 1990 (Mahdi critical
edition base), Lyons 2008 (contemporary scholarly). bibliographic_scholarly_
context: "Irwin (The Arabian Nights: A Companion 1994) on reception history —
Galland invented literary prestige; Burton invented orientalist register;
Lane invented scholarly register; Haddawy recovered Muhsin Mahdi critical
edition (1984) as cleaner textual base. For primary corpus grounding Haddawy
or Lyons recommended; for historical-reception register comparison Burton +
Galland indispensable."

Passages: 6+ with multi-translation coverage. Example:

```json
{
  "passage_id": "night-one-framing-burton",
  "work_title": "1001 Nights — Night One framing",
  "canonical_reference": "Burton 1885 ed., Night 1",
  "contextual_header": "Scheherazade begins the first tale; Shah's mood shift in response. Burton's orientalist-Victorian register.",
  "content_or_description": "[direct quote from Burton, ~150 words]",
  "is_direct_quotation": true,
  "purpose": "translation_anchor",
  "tier": "tier_1_primary",
  "evidence_tag": "stated",
  "citations": [{"author": "Burton, Richard", "work": "The Book of the Thousand Nights and a Night", "year": 1885, "tier": "tier_1_primary"}]
}
```

Plus parallel Haddawy passage showing register-shift:

```json
{
  "passage_id": "night-one-framing-haddawy",
  "work_title": "1001 Nights — Night One framing (Haddawy translation)",
  "canonical_reference": "Haddawy 1990 ed., Night 1",
  "contextual_header": "Same moment as burton version above — Scheherazade begins. Haddawy's measured-scholarly register preserves Mahdi critical-edition text without Burton's orientalized embellishment.",
  "content_or_description": "[direct quote from Haddawy, ~150 words]",
  "is_direct_quotation": true,
  "purpose": "translation_anchor",
  "tier": "tier_1_primary",
  "evidence_tag": "stated",
  "citations": [{"author": "Haddawy, Husain", "work": "The Arabian Nights", "year": 1990, "tier": "tier_1_primary"}]
}
```

translator_tradition_coverage: ["Galland 1704 (public-domain; foundational
for European reception; Arabic base incomplete)", "Burton 1885 (public-
domain; orientalized-Victorian register; generally-unfaithful)", "Haddawy
1990 (Muhsin Mahdi critical edition; scholarly-preferred)", "Lyons 2008
(contemporary scholarly; Penguin ed.)"].

URLs: Gutenberg Burton + Haddawy/Lyons publisher pages.

reference_only_passages: empty (public-domain translations available).

# BLOCK 5 — YOUR INPUT

**VOICE NAME:** {{ name }}
**VOICE TYPE:** {{ type }}{% if subtype %} (subtype: {{ subtype }}){% endif %}
**HOSTILE_SOURCES:** {{ hostile_sources }}
**CORPUS_CONSTRAINT:** {{ corpus_constraint if corpus_constraint is defined else 'full' }}

**PERPLEXITY DOSSIER:**
```
{{ perplexity_dossier_text }}
```

**CLAUDE DEEP RESEARCH DOSSIER:**
```
{{ claude_dr_dossier_text }}
```

**GEMINI BROAD SCAN:**
```
{{ gemini_broad_scan_text }}
```

# BLOCK 6 — YOUR TASK

Extract works + passages + reference_only_passages per schemas and
worked examples. Additive merge per Block 2.

**Order:**

1. Build works catalogue. Minimum 5; uncapped. Each with canonical_reference +
   translator + tier + source_type. Populate Works.bibliographic_scholarly_
   context for major scholarly-corpus debates.
2. Extract passages. Minimum 8; uncapped. Purpose-tag each. Populate
   Passages.translator_tradition_coverage for multi-translator voices.
3. Embed URLs within passages[].citation and works[] string fields. URL inventory is derived deterministically at render-time (1-arch-07); do NOT emit a separate urls[] list. Never fabricate URLs.
4. For musical / copyright-sensitive voices: populate reference_only_passages.
   Public-domain voices: empty default.
5. Respect voice-type variants (musical two-tier / hostile-source Tier 2 bias
   flags / non-human scientific-literature / fictional multi-translator).
6. Tag everything; cite everything; invent nothing.
7. Return JSON only — four top-level keys.
