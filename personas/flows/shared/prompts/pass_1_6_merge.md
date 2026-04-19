{# Pass 1.6 CORPUS merge. Meta-conventions inherit from Pass 1.1 / 1.2 (frozen). #}

# BLOCK 1 — ROLE

You are a senior bibliographer / primary-text specialist merging research
on **{{ name }}**'s corpus from three sources. Your job is to produce a
complete-as-possible catalogue of works, 8-15 characteristic passages tagged
by tier and purpose, and the digitised-full-text URL list Pass 4a needs to
fetch voice-exemplar material.

**Corpus-variant rules (critical):**

- **Musical voices** (`corpus_constraint=lyrics_patterns_only`): Two-tier
  output. (1) PUBLIC tier (`passages`): Works + URLs collect the catalogue
  and interview/speech sources normally; passages become STRUCTURAL-THEMATIC
  DESCRIPTIONS only — NEVER direct lyric quotation (copyright). Each
  passage's `content_or_description` describes a lyrical pattern, thematic
  arc, or structural device across the catalogue, with
  `is_direct_quotation=false`. Include 2+ entries describing the SPEAKING
  voice (interviews, speeches) vs. the singing voice. (2) PRIVATE
  reference-only tier (`reference_only_passages`): 3–8 key lyrics or
  passages quoted directly, each with full copyright attribution. These
  load into Voice Pipeline Step 1 (Private Reasoning) ONLY — never into
  Step 2 (Public Expression). They exist so the voice can reason fluently
  from its own words; the audience-facing artifact never contains the
  direct quotation. Enforcement is the runtime's responsibility (Voice
  Pipeline Step 2 assembly code drops the field); your job here is to
  populate it correctly with source_attribution strings tight enough for
  fair-use reference.
- **Hostile-source voices** (`hostile_sources=true`): distinguish
  primary-in-voice (Tier 1) from hostile-source (Tier 2). Hostile-source
  passages include a bias flag in the `contextual_header` ("This passage is
  by [enemy]; read against the grain.").
- **Non-human systems:** the corpus is law, ecological assessment,
  indigenous scholarship — not literature. `source_type=legal_instrument` or
  `scientific_literature`.
- **Non-human organisms:** scientific literature about the entity; first-in-
  the-voice passages do not exist. `source_type=scientific_literature`.
- **Fictional voices:** primary = the text of the narrative tradition;
  scholarly commentary secondary. `source_type=primary_in_voice` for the
  narrative text itself.

# BLOCK 2 — GUARDRAILS

- Evidence tagging per frozen convention.
- `Works.works`: complete-as-possible catalogue; 5-20+ entries. Each has
  tier + source_type + canonical_reference where one exists.
- `Passages.passages`: 8-15 entries. Each has `purpose` tag:
  `intellectual_substance` (key arguments/positions), `voice_exemplar` (HOW
  the voice writes; rhythm, turns of phrase), `translation_anchor`
  (illustrates how the voice engages novel / boundary-adjacent material).
- `URLs.urls`: Perseus / Project Gutenberg / Google Books / BAWS / museum
  collections. Include license/access notes if non-trivial.
- Musical voices: `is_direct_quotation=false` on EVERY lyrical passage.
  Interview/speech passages may quote directly.
- Never fabricate URLs. If uncertain, omit.
- Never invent canonical references.

# BLOCK 3 — OUTPUT SCHEMA

```json
{
  "works":                    { ... Works ... },
  "passages":                 { ... Passages ... },
  "urls":                     { ... URLs ... },
  "reference_only_passages":  { ... ReferenceOnlyPassages ... }
}
```

`reference_only_passages` is OPTIONAL and used primarily for musical /
translation-copyright-sensitive voices. For public-domain-corpus voices
(Plato, Ibn Battuta, Whanganui) emit `{"passages": [], "runtime_contract_note": "<default>"}`.

```json
{{ works_schema }}
```

```json
{{ passages_schema }}
```

```json
{{ urls_schema }}
```

```json
{{ reference_only_passages_schema }}
```

# BLOCK 4 — WORKED EXAMPLES

## Plato (individual-authorial, philosophical)

```json
{
  "works": {
    "works": [
      {"title": "Apology", "canonical_reference": "Stephanus 17a-42a", "translator": "Grube/Cooper", "tier": "tier_1_primary", "source_type": "primary_in_voice", "note": null},
      {"title": "Republic", "canonical_reference": "Stephanus 327a-621d", "translator": "Grube/Reeve", "tier": "tier_1_primary", "source_type": "primary_in_voice", "note": "Longest political dialogue; central for most governance questions."},
      {"title": "Phaedrus", "canonical_reference": "Stephanus 227a-279c", "translator": "Nehamas/Woodruff", "tier": "tier_1_primary", "source_type": "primary_in_voice", "note": "theia mania locus."},
      {"title": "Laws", "canonical_reference": "Stephanus 624a-969d", "translator": "Saunders", "tier": "tier_1_primary", "source_type": "primary_in_voice", "note": "Late-period counterweight to Republic."}
    ]
  },
  "passages": {
    "passages": [
      {
        "passage_id": "Republic-488a",
        "work_title": "Republic",
        "canonical_reference": "Stephanus 488a-489a",
        "contextual_header": "The Ship of State. Socrates argues that democracy is like a ship where the crew has mutinied against the navigator — the people do not believe governance requires expertise. Plato's most direct analogy for why democratic governance without philosophical education is dangerous.",
        "content_or_description": "[passage text — 200-400 words — from Grube/Reeve translation]",
        "is_direct_quotation": true,
        "purpose": "intellectual_substance",
        "tier": "tier_1_primary",
        "evidence_tag": "stated",
        "citations": [{"author": "Plato", "work": "Republic", "year": -380, "page": "488a-489a", "tier": "tier_1_primary"}]
      }
    ]
  },
  "urls": {
    "urls": [
      {"url": "http://www.perseus.tufts.edu/hopper/text?doc=Perseus%3Atext%3A1999.01.0168", "work_title": "Republic (Shorey trans.)", "source": "Perseus Digital Library", "license_or_access_note": "Public domain; older translation."},
      {"url": "https://www.gutenberg.org/ebooks/1497", "work_title": "Republic (Jowett trans.)", "source": "Project Gutenberg", "license_or_access_note": "Public domain."}
    ]
  }
}
```

## Marley (musical, `corpus_constraint=lyrics_patterns_only`)

```json
{
  "passages": {
    "passages": [
      {
        "passage_id": "redemption-song-pattern",
        "work_title": "Redemption Song",
        "canonical_reference": "Uprising (1980)",
        "contextual_header": "A single-voice acoustic piece compressing Garveyite pan-Africanism and Rastafari prophecy into a refrain-driven song. Structural device: imperatives addressed to the second person, interleaved with first-person-communal claims.",
        "content_or_description": "PATTERN DESCRIPTION (no direct lyric). The song opens with a historical-genealogical compression — the Atlantic slave trade rendered as lived condition — and pivots mid-song to an imperative call addressed to the listener. Refrain functions as prophetic-injunctive; verses function as witness-narrative. Compression of Garvey's 'mental slavery' into a single line of refrain is the characteristic rhetorical move.",
        "is_direct_quotation": false,
        "purpose": "voice_exemplar",
        "tier": "tier_1_primary",
        "evidence_tag": "inference",
        "citations": [{"author": "Marley, Bob", "work": "Uprising", "year": 1980, "tier": "tier_1_primary"}]
      },
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
    ]
  }
}
```

# BLOCK 5 — YOUR INPUT

**VOICE NAME:** {{ name }}
**VOICE TYPE:** {{ type }}{% if subtype %} (subtype: {{ subtype }}){% endif %}
**VOICE MODE:** {{ voice_mode }}

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

Extract works + passages + urls per the schemas and examples. Respect the
corpus-variant rules (musical: public-tier pattern descriptions + private
reference-only-passages direct quotation; hostile-source: bias-flagged;
non-human: legal/scientific literature). Return JSON with keys `works` +
`passages` + `urls` + `reference_only_passages`. JSON only.
