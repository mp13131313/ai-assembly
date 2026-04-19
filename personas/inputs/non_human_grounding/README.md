# Non-human voice grounding

Per REBUILD_PLAN decisions log #4, non-human voices (organisms and systems)
require domain-specific curated grounding rather than Wikipedia lead
paragraphs. Pass 0a's runner checks this directory first for
`<voice_slug>.md` before falling back to Wikipedia.

## Contents

| Slug | Voice | Primary source |
|---|---|---|
| `octopus.md` | Octopus | Godfrey-Smith, *Other Minds* (2016), ch. 3-4 |
| `whanganui_river.md` | Whanganui River / Te Awa Tupua | Te Awa Tupua (Whanganui River Claims Settlement) Act 2017, preamble + s.12–14 |

## Format

Each file is a ~500-1500 word curated excerpt the model can read as
classification grounding. Scope: enough to establish the ontological /
biological / legal frame so Pass 0a correctly classifies `type`, `subtype`,
and `voice_mode`. Not a full dossier — that comes from Phase 0.5.

## Fair-use caveat

Text excerpts from published works (Godfrey-Smith etc.) are kept short
enough for fair-use classification. If a file is extended significantly,
review the fair-use status and add an attribution note.

## When to add a new file

Each time a new non-human voice enters the panel. For the current 12-voice
panel, the two non-human voices are Octopus and Whanganui River.
