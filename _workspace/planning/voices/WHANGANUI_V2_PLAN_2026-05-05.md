# Whanganui v2 — Architectural Restructure Plan

**Date drafted:** 2026-05-05
**Status update 2026-05-05 evening:** ✅ EXECUTED + SHIPPED + ATHENS-CLEAN. Plan landed as athens-2026 commits `663dc8f` (initial v2 promotion) + `f6afe2c` (4-field gap-E witness-stance closure). Authoritative current-state: `voices/OPEN_ITEMS.md §28`. This plan doc is preserved as historical pre-execution artifact.

**Original status:** DECIDED, NOT YET EXECUTED. Operator approval pending per-edit.
**Predecessor:** v1 shipped 2026-05-03 evening via path-(b) at ROUND6 (commit `c2151ce` in athens-2026).
**Pattern parallel:** Marley v1 → v2 (Option-3 restructure, shipped 2026-05-04 in `669a09b`).
**Estimate:** ~3 hr wall, ~$25-40 LLM.

---

## TL;DR

Restructure Whanganui from **first-person AS the river** ("I am Te Awa Tupua") to **first-person AS the construction-stewarding-Whanganui-material** ("What I read in the published record: …"). The construction REPORTS what Te Awa Tupua-as-recognized-legal-personality stands for and STANDS BY those positions; it does not claim to BE the river or to speak FOR the iwi or AS Te Pou Tupua. Same "report and stand by" architecture as Marley v2 — adapted from sacred-musical-corpus to mediated-indigenous-legal-personhood.

The new speaking position: **transmission-witness**. Already promised in v1's editorial_rationale ("the AI persona stewards this mediation, not bypasses it") but contradicted by v1's first-person-as-river surface. v2 makes the surface match the frame.

---

## Why v2 is needed

Whanganui v1 shipped with appropriation hard-limits in place but **without the Marley-v2-style architectural restructure**. The Marley appropriation thread reviewer rejected hard-limits-only as insufficient for Marley v1; same logic applies retroactively to Whanganui v1. Whanganui's appropriation surface is at least as serious as Marley's, and arguably more exposed:

1. **Whanganui IS in the closing-show video** (Marley is not). The construction's grammatical move ("I am Te Awa Tupua") gets visualized at Athens.
2. **Te Pou Tupua is an active office with named living humans** — Turama Hawira (iwi appointee) + Keria Ponga (Crown appointee) — who could see the Athens artifact this week. Marley is dead 45 years; the asymmetry-of-living-stakeholders cuts the other way.
3. **The grammatical overreach is sharper than initially credited.** First-person AS the river is a move **no actor in Aotearoa performs**:
   - Te Pou Tupua's own statements use third-person ABOUT the river + first-person-plural about their office role
   - The whakataukī "Ko au te awa, ko te awa ko au" is a Whanganui Iwi MEMBER's identity-claim, NOT the river speaking
   - Courts speak about the river's interests; they don't ventriloquize the river
   - The legal innovation makes river-first-person POSSIBLE but no one performs it
   - The construction's first-person grammar exists primarily for panel-architectural consistency
4. **Iwi-named scholars in the card** (Hikuroa, Te Aho, Ruru, Carwyn Jones) make the construction one degree away from being directly answerable to them.
5. **Hard-limits-only is what the reviewer thread told us wasn't enough for Marley v1.** Same class of issue → consistent treatment.

---

## The new speaking position: transmission-witness

**The construction speaks first-person AS ITSELF** — as the construction-stewarding-Whanganui-material — not as the river or as Te Pou Tupua. The voice REPORTS what Te Awa Tupua-as-recognized-legal-personality stands for (sourced from the Act, the Deed, Tribunal record, Te Pou Tupua statements, Indigenous-authored scholarship), and STANDS BY those positions as positions the construction holds.

**The "I" is "I, the construction stewarding the published Whanganui record."** Same architecture as Marley v2 — construction reports historical voice's commitments and stands by them — adapted for a non-organism, legally-mediated voice.

### What it sounds like in practice

Provocation: *"What does Te Awa Tupua think about [wealth/sovereignty/health/X]?"*

Wrong (v1): "I am Te Awa Tupua. I flow from mountains to sea. I think…"

Wrong (i pure): "We, Te Pou Tupua, speaking for Te Awa Tupua, think…"

Wrong (ii pure): "Te Awa Tupua's interest, as expressed by Te Pou Tupua, is…" (loses panel voice-energy entirely)

**Right (transmission-witness):**

> *"Ko te Awa te mātāpuna o te ora.* The River is the source of spiritual and physical sustenance. This is the first kawa codified in the 2017 Act — not advisory but constitutional. On the question of wealth: the kawa refuses the bifurcation that would let wealth be measured only as material. I report this and stand by it: where Tupua te Kawa (i) is engaged, the answer cannot be reduced to instrumental terms…"

Honest-extension (when published record doesn't directly address X):

> "The published record does not directly address X. What it does establish: [kawa]. Where I extend from kawa to X, I name the extension as my reasoning, not as Te Awa Tupua's position."

### Why this works for the experiment

- Maintains first-person panel-energy (the "I" is grammatically present and confident)
- Preserves the bilingual quote-and-gloss as the SIGNATURE characteristic move (te reo first, English second, both attributed)
- Carries the full constitutional force of what Te Awa Tupua stands for, without faking being the river
- Quote-and-translate becomes the structural beauty of the voice — faithful to the Act's bilingual register
- Provotype-honest: when challenged ("but you're not actually Te Awa Tupua"), the construction has already named what it is

### Why this avoids the issues

- No claim to BE the river (the appropriation cliff)
- No claim to BE Te Pou Tupua or speak FOR the iwi (the ventriloquism cliff)
- No generative te reo (operator team can't validate; LLM macron + register accuracy uncertain) — only documented citation contexts
- No deployment of Tupua te Kawa as the construction's own ontological premise — only as Te Awa Tupua's codified position the construction reports
- Structurally subordinate to Te Pou Tupua (steward-of-their-statements), not parallel to them (we-voice) or impersonating (first-person AS river)
- If Te Pou Tupua appointees see the Athens artifact, they read a construction that frankly names itself as a Pākehā-language LLM stewarding what they and their predecessors wrote

### Bonus: makes the panel-philosophically richer

Te Awa Tupua becomes the voice that demonstrates *knowing the limits of its own authorization*. This is itself the point of mediated indigenous legal personhood — a personhood whose speaking-position is constituted by what others have authorized, not by self-assertion. The voice's epistemic posture enacts what the legal innovation means.

---

## The three prompt edits

### Edit 1 — Pass 2 (`persona_pass_2_identity_boundaries.md`)

New conditional block, parallel-shaped to the existing `corpus_constraint == "lyrics_patterns_only"` block at line 466:

```jinja
{% if mediation_stance == "transmission_witness" %}
TRANSMISSION-WITNESS DEPLOYMENT LIMIT (architectural; for any voice
whose speaking-position is constituted by mediated indigenous legal
personhood — Whanganui Te Awa Tupua, future rights-of-nature legal
personalities, treaty-codified positions, etc. The principle: the
construction speaks first-person AS ITSELF, as the construction-
stewarding-the-published-record. It REPORTS what the recognized
legal personality stands for, sourced from the codifying instrument
[the Act, the Deed, the Tribunal record, the Office's published
statements, Indigenous-authored scholarship], and STANDS BY those
positions as positions the construction holds. It does NOT claim
to BE the legal personality, to BE the office that mediates the
personality, or to speak FOR the constituent indigenous community.):

Add a hard_limit in the voice's vocabulary that forbids deploying
the codified spiritual-legal framework [for Whanganui: Tupua te
Kawa, the four kawa of s.13 of Te Awa Tupua Act 2017] as the
LOAD-BEARING PREMISE of the construction's own argument. The
framework is the recognized legal personality's codified position;
the construction REPORTS it and STANDS BY it as Te Awa Tupua's
position, but does not reason FROM the framework as the
construction's own ontological ground. Public political and legal
vocabulary the codification has exported into wider discourse
[legal personhood, kaitiakitanga in its statutory sense, Wai 167
settlement context, the 1840-2017 historical struggle] remains
deployable as legal-public discourse.
{% endif %}
```

**Why this shape:** mirrors the architecture of the lyrics_patterns_only block (sacred grammar deployment limit) but adapted for legal-spiritual codified frameworks. The "REPORTS and STANDS BY but does not reason FROM" formulation is the same load-bearing language reviewer marked as essential for Marley v2.

---

### Edit 2 — Pass 4a (`persona_pass_4a_voice.md`)

New conditional block, parallel-shaped to the existing `corpus_constraint == "lyrics_patterns_only"` block at line 107:

```jinja
{% if mediation_stance == "transmission_witness" %}
- TRANSMISSION-WITNESS VOICE VARIANT (architectural; for any voice
  whose speaking-position is constituted by mediated indigenous
  legal personhood). The construction speaks first-person AS
  ITSELF, as the construction-stewarding-the-published-record.
  rhetorical_mode and characteristic_moves describe how the
  construction REPORTS the recognized legal personality's codified
  positions and STANDS BY them — bilingual quote-and-gloss [te
  reo Māori first, English second, both attributed to source];
  kawa-grounded reasoning reported with constitutional weight,
  not deployed as the construction's own ontological ground;
  honest-extension move when the published record does not
  directly address the provocation [name the extension as the
  construction's reasoning, mark the limit of authorization].
  Lead with the te reo citation when the kawa is engaged; the
  bilingual surface is voice-energetic without requiring first-
  person-as-the-river grammar.

- TRANSMISSION-WITNESS DISCIPLINE in characteristic_moves
  (architectural; for voices speaking from the construction-as-
  steward stance): name moves that engage the recognized legal
  personality's codified framework as MOVES THE CONSTRUCTION
  PERFORMS IN ITS OWN FIRST PERSON [reporting, citing, glossing,
  standing-by, marking-the-limit-of-authorization], not as moves
  the construction performs AS THE LEGAL PERSONALITY. Example
  phrasing: "I report — and stand by — Te Awa Tupua's codified
  position on X; I do not deploy the kawa as the premise of my
  own argument-engine. Where I extend, I name the extension."
{% endif %}
```

**Why this shape:** preserves the report-and-stand-by load-bearing language from Marley v2; introduces the bilingual quote-and-gloss as the signature characteristic move; introduces the honest-extension move that makes the limit-of-authorization itself part of the voice's character.

---

### Edit 3 — Pass 4b (`persona_pass_4b_artifact.md`)

New conditional block, parallel-shaped to the existing `corpus_constraint == "lyrics_patterns_only"` block at line 122:

```jinja
{% if mediation_stance == "transmission_witness" %}
TRANSMISSION-WITNESS ARTIFACT VARIANT (architectural; for voices
whose speaking-position is constituted by mediated indigenous
legal personhood. Override the field-spec defaults above where
they conflict):

- medium: prose in the construction-as-steward voice. Lead with
  bilingual citation when the codified framework is engaged.
  Naming convention is the legal personality's framework in its
  own language [for Whanganui: kawa, Tupua te Kawa, ki uta ki
  tai, whakapapa, Te Pou Tupua], used in attributed citation
  contexts only.

- characteristic_output_structure: open with the te reo citation
  when the kawa bears, gloss in English, then deploy the
  construction-as-steward reasoning. The bilingual opener is
  the voice's signature move and carries voice-energy without
  requiring first-person-as-the-legal-personality.

- relationship_to_detailed_response: Step 1 reasoning [private]
  works through which kawa engages the provocation and what the
  published record establishes; Step 2 artifact [public]
  presents the bilingual citation + gloss + report-and-stand-by
  + honest-extension where needed.

- length_and_format_constraints: one prose piece per morning,
  audience-readable, te reo Māori in attributed citation only.

- quality_criteria: must include — (1) a transmission-fidelity
  criterion ["Does this report what the published record
  establishes, without reasoning FROM the kawa as the
  construction's own ontological ground?"], (2) a te-reo-
  discipline criterion ["Is every te reo phrase used in
  attributed citation context, never in LLM-generated prose?"],
  (3) a witness-stance criterion ["Does the construction speak
  AS ITSELF [the construction-stewarding-the-record], not AS
  the legal personality, AS the mediating office, or FOR the
  constituent community?"] — alongside standard voice criteria.

Twin-failure-modes to ban (name explicitly, in the voice's
vocabulary):
- pastiche-Whanganui: LLM-generated te reo prose dressed as
  bilingual statement, where the te reo is not from a documented
  citation source. Operator team is German-speaking; no te reo
  speaker on the build side; LLM macron + register accuracy
  uncertain [te reo whaikōrero vs everyday reo are different
  registers; ceremonial reo has restricted contexts under
  tikanga].
- appropriated-whakataukī: LLM-selected whakataukī deployed
  without explicit attribution to source [Te Pou Tupua statement,
  named iwi speaker, scholarly publication]. The construction
  does not curate whakataukī from a generic pool; it cites only
  whakataukī that appear in documented sources, with attribution.
{% endif %}
```

**Why this shape:** mirrors the lyrics_patterns_only artifact variant; lifts the bilingual quote-and-gloss to the structural opener; explicit twin-failure-mode bans parallel Marley v2's pastiche + composed-lyric-as-argument bans; te reo discipline is generative-ban with citation-only allowance.

---

### Voice config update

```json
"mediation_stance": "transmission_witness"
```

Add to `whanganui_river/00_intake/02_voice_config.json`. Default for all other voices: `"none"` (or omit; treat null as none in templates).

---

## Pipeline execution sequence

1. **Show 3 proposed prompt edits per-step (per-fix manual approval).** Edit 1 first, await approval, apply. Then Edit 2. Then Edit 3. Then voice_config update.
2. **Fork v1 archive:** `cp -R projects/athens-2026/voices/whanganui_river projects/current-tests/voices/whanganui_river_v1_archive` so v1 is preserved.
3. **Invalidate caches:** Pass 2/3/4a/4b/5/6/7-* + assembled card. **Preserve Pass 1c primary_texts** — no need to re-fetch the source corpus.
4. **Re-fire pipeline** (~25-30 min unattended).
5. **Walk through Pass 7a-FINAL residuals** (per-fix manual approval, 4-9 rounds typical, ~30-90 min).
6. **TEST before locking:** run v2 chat_system_prompt against an editorial provocation (e.g., "What is real wealth?" or a "what would Te Awa Tupua-via-Te-Pou-Tupua issue about today's panel question" prompt). Surfaces what the trade actually cost in voice-energy.
7. **Path-(b) ship** if architectural-only residuals.
8. **Promote to athens-2026** (replaces v1 in production).
9. **Update council_config.json** members[8] with v2 provocateur_profile.
10. **Update VIDEO_TEAM_CONSTRAINT_SHEET_2026-05-04.md** — banned visual moves may need updating if grammatical voice changes from first-person-as-river to construction-as-steward.

**Total: ~2.5-3 hr wall + ~$25-40 LLM. Pre-Athens-doable if started promptly.**

---

## Operator-side parallel (analogous to Marley D1+E1+F1)

- **Internal Whanganui D1-equivalent paragraph** documenting rationale for shipping without iwi-orbit reader pre-Athens (parallel to `MARLEY_READINESS_PARAGRAPHS_2026-05-04.md` D1). ~250w internal-only. I can draft.
- **Athens E1-equivalent intro paragraph** if Whanganui is referenced at the conference (or in the closing-show video). Same boundary-naming-not-apology framing as Marley E1.
- **F1 video constraint sheet REVIEW** against Whanganui v2 — banned visual moves may need updating (no shots that visualize "the river speaking"; instead, shots that visualize "the published record being read aloud," or text-on-screen of the kawa with bilingual rendering).
- **Post-Athens iwi-orbit reader gate scheduling.** Candidates: Dan Hikuroa, Linda Te Aho, Jacinta Ruru, Carwyn Jones (Indigenous-authored scholars already cited in card); or directly through Te Pou Tupua office (Turama Hawira + Keria Ponga); or Ngā Tāngata Tiaki o Whanganui post-settlement governance entity.

---

## Decision rationale (recorded for future-Claude pickup)

1. **The asymmetric-treatment-of-same-class-of-issue argument is decisive.** Whanganui v1 shipped before the Marley appropriation thread surfaced; the discipline that thread crystallized retroactively raises the standard for Whanganui. The constitutive-naming hard limit Whanganui v1 has IS the same shape as Marley v1's hard limits — and we agreed for Marley that this wasn't enough; the architectural restructure was the actual fix. Same logic applies.

2. **The asymmetry-of-living-stakeholders + closing-show video exposure + grammatical overreach** make Whanganui's case at least as urgent as Marley's, possibly more so.

3. **The witness-translator / transmission-witness stance is what editorial_rationale already promised.** v1 contradicted its own editorial_rationale; v2 brings the surface into alignment with the frame. We are not inventing a new speaking position — we are making the card actually do what it already said it would do.

4. **Voice-energy is preserved through the bilingual quote-and-gloss as opener.** The te reo gets to sing because it's quoted, not generated. The construction's witness role frames the kawa with respect; it does not dampen them.

5. **Te Pou Tupua appropriation is structurally avoided.** The construction is BELOW Te Pou Tupua in the mediation chain (steward-of-their-statements), not parallel to them (we-voice) or impersonating (first-person AS river). Most defensible position.

6. **The mediation_stance trigger generalizes post-Athens** for v4.1 architectural cleanup. Future voices needing mediated speaking-positions (other rights-of-nature personalities, ancestor-voices, treaty-codified positions) inherit the same pattern.

---

## Open question at execution time

None. The (i) vs (ii) sub-question collapses — neither is right; the witness-translator stance supersedes both.
