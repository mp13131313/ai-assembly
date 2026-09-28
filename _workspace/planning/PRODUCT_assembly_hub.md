# PRODUCT — The Assembly as a governed voice hub

**Status:** strategy note, v1 — 2026-06-14. **Net-new; no OPEN_ITEMS home** (same status as the Phase-2 "versatile assembly" vision). Companion to the technical view in `PLAN_2026_06_12_post_athens_roadmap.md` Phase 2 + the agentic backlog at `runtime/OPEN_ITEMS.md` Section H.
**Provenance:** distilled from the 2026-06-14 product conversation (SaaS-readiness → studio → governed hub). Conversation-only before this; this is its durable home.
**Scope:** what *product* the voice + runtime pipelines become post-Athens, and the governance design the operator chose. Strategy, not tracked work — no FU#/C#/§ numbering; references existing IDs.

---

## 1. The arc (three forks, one chosen)

The post-Athens "what is this as a product" question was worked through three shapes:

1. **Public SaaS** — multi-tenant, self-serve, accounts/billing/compliance. *Rejected as the near-term target:* it requires a multi-tenancy rewrite of the filesystem-state model, full GDPR/SOC2 for transcripts of identifiable people, and — fatally — it forces ethics-gates-at-scale (you cannot let strangers spin up a "Bob Marley" or "Whanganui River" voice unreviewed). Too heavy, and the hardest part has no clean technical answer.
2. **Studio (curated, agency)** — a single-org, multi-*project* production console; you run assemblies *for* events/clients from a curated voice library; clients get outputs, not seats. Achievable (~⅓ of SaaS scope), faithful to the prosumer DNA, and the SaaS *blockers* become *features* (the human gates turn into review screens). But the voice library is closed.
3. **Governed voice hub (CHOSEN)** — the studio console **plus** an extendable, flagged, multi-contributor voice library. Other users can build voices; voices carry flags; a **build-private / publish-gated** split concentrates governance at the one chokepoint that matters. This is the studio's operability with the platform's openness, governed by flags instead of by either total curation or total openness.

**Operator decision (2026-06-14):** the voice library is **extendable, with flags; other users can build voices.** → Shape 3.

---

## 2. What the product is

**A governed voice hub: a production studio + a flagged, extendable, multi-contributor voice library, with a build-private / publish-gated split.**

Closest analogy: a **model hub (HuggingFace) with model cards, licenses, and gated models** — or a plugin marketplace with review tiers. The key enabler is that the project already builds the core primitive: **the persona card *is* the voice card.** The hub extends an artifact you already produce into a *publishable, governed, provenance-carrying unit.*

Two layers:
- **The runtime** runs councils over input material (transcription → researcher → provocateur → voice → editor → publish; or the vatican annotation shape). It is the engine.
- **The hub** is where councils get *composed* from a governed voice library, and where voices get *built, flagged, and published.*

This is the provotype's own argument — *who gets to build the representative, and under what conditions* — turned into product mechanics: construction stays visible (provenance on every card), ethics stay human (attestation, not automation), extendability is real (anyone builds; the gate is on publish).

---

## 3. The core architectural move: build-private vs publish-shared

Extendability and ethics-gating only conflict if you gate *building*. You don't. You gate *publishing to a library others draw from* — which is exactly how the project already reasons (the reader-gate was always about *deployment*, not authorship).

| State | Who can use it | Gate to enter |
|---|---|---|
| **Private voice** | builder only | none — flags auto-attach + disclaimer applied |
| **Org-shared voice** | builder's org | self-attestation of flags; license declared |
| **Public library voice** | anyone | all *ethics-flag* gates cleared (attestation visible on card); validation badge computed; provenance complete |

Extendability stays fully open; governance concentrates at publish-to-public.

---

## 4. The flag taxonomy

Flags must **trigger policy**, not merely label. Three classes, all extensions of metadata the voice card already carries (`subtype` human/non-human/system, `voice_mode`, `corpus_constraint`, the reader-gate concept at voices `OPEN_ITEMS` §24/§28):

**A. Ethics / permission flags — gate publish-to-public**
- *sacred-grammar / living-tradition first-person* (Marley's I-and-I; Whanganui's iwi-voice) — the §24/§28 reader-gate, productized.
- *indigenous-collective (speaks-AS-not-FOR)* — iwi-ventriloquism risk; mediation structure (e.g. Te Pou Tupua) must be declared.
- *living person* — the reason Tang + Thiel were cut (no completion-anchor); likely disallowed for public, or requires consent on file.
- *real, identifiable person / estate-sensitive* — likeness/estate/defamation (the Marley estate-position critique was load-bearing); requires rights note + takedown path.

**B. Validation / quality flags — inform trust, mostly not gates**
- passed reader-gate · passed the **§33 blind-A/B falsification probe** (genuine perspective vs elaborate ventriloquism) · corpus-grounded vs thin.
- This **operationalizes §33 as a public per-voice badge** — the question the project hasn't resolved even for its *own* voices becomes a product signal. (Forces defining the bar — see §8.)

**C. Provenance / license flags**
- who built it · from what corpus · under what license/permission.

**Detection ladder:** auto-detect the sensitive ones where possible (corpus includes a living religious tradition / a contemporary figure → auto-flag) → builder **attestation** as backstop → **review step** before public publish for the highest tier.

---

## 5. The attestation model (the honest answer to "who clears a gated voice?")

You cannot staff in-tradition reviewers for arbitrary traditions. So **the platform is a registry of attestations, not the adjudicator.** For a sacred/indigenous voice, the *builder* supplies a credible reader-gate attestation — named reviewer, stated relationship to the tradition — which the platform **records and displays on the voice card** and enforces *exists and is visible* before public publish. The platform does not certify the attestation is "correct"; it makes the construction and its review legible, and provides a takedown path.

This is faithful to the project's own conclusion (the Rastafari-orbit / iwi reader is the *only* mechanism that can adjudicate): make the platform **demand that mechanism**, don't fake it internally.

---

## 6. Technical shape — what the hub needs (vs full SaaS)

Most gaps downgrade to lighter "studio" forms; the extendable library re-imports a contained slice.

| # | Gap | Hub form |
|---|---|---|
| 1 | Multi-tenancy | → **multi-project** (many assemblies under operating orgs) + visibility tiers; datastore + queue replacing filesystem-state, but no hard stranger-isolation |
| 2 | Config externalization | **unchanged & foundational** — this *is* Phase 2.1 (FU#42 split-card, C52 event-config, the ~8 event-string prompts). New event/council set up in GUI, not code |
| 3 | Accounts / authz / metering | **hardens** (UGC needs real users, orgs, ownership, roles) + **cost-per-run visibility** (hooks the 2.2 vendor abstraction); not a public billing engine |
| 4 | Unattended reliability | **babysitting-reduction**: take the cheap robustness wins from Section H (C43 self-recovery, dup-dispatch guard, checkpoint-resume); agentic triage (C60) stays optional (operator reviews in GUI) |
| 6 | Compliance | **a slice returns** — UGC moderation, estate/likeness takedown (DMCA-shaped), provenance, builder-responsibility terms; *not* full GDPR-SaaS |
| 7 | Input / output | generalized input adapters (audio panels, documents/vatican, reflections) + real render/host story, scoped to served shapes |
| 8 | Model governance | per-project model pinning + the **regression harness you already have** (sentinel-regen + the 9-test rubric) wired into the app |

Net: still substantial, but the extendable-library decision adds **point-3 hardening + a point-6 slice** on top of the studio; everything else stays studio-light.

---

## 7. The GUI surfaces

Several have existing seeds:
1. **Event/council setup wizard** — define an event (replaces editing `council_config`/`sessions.json`); assemble a council from the voice library; reader-gate checklist. *(Depends on Phase 2.1.)*
2. **Voice authoring flow** — productized persona-pipeline entry; flags auto-attach; attestation capture. *(The artisanal pipeline behind it stays internal-grade; this is its front door.)*
3. **Ingest + run launch** — upload material, pick deployment profile, fire. *(Builds on FastAPI ingest + `dashboard.py`.)*
4. **Live run monitor** — stage progress, accruing cost, failures + logs. *(Extends the read-only dashboard, C23.)*
5. **Validation review queue** — the C28b gate as a screen: release/hold with a click instead of hand-writing decision JSON.
6. **Output preview + publish** — read dossiers/artifacts, edit deployment-context, publish to a hosted microsite.
7. **Library + voice cards** — browse/search published voices; each card shows flags, attestations, validation badge, provenance, license; publish-tier controls.

---

## 8. Open decisions (downstream of the hub choice)

1. **Publish tiers + per-flag clearance — the spec that defines the whole governance layer.** Starter:

   | Flag | Auto-detect | Clearance to publish-public |
   |---|---|---|
   | sacred-grammar / living-tradition | partial (corpus signal) | named in-tradition reader attestation, visible on card |
   | indigenous-collective (speaks-AS) | partial | community attestation + declared mediation structure |
   | living person | yes (dates) | disallowed for public, or explicit consent on file |
   | real-identifiable / estate-sensitive | partial | rights note + disclaimer + takedown path |
   | validation: passed blind-A/B | n/a (test result) | badge only — not a gate |

2. **The §33 validation bar.** If voices carry a validation badge, define what "validated" means (the recommended floor, per voices §33: a domain expert **can** reliably tell the configured voice apart from a competent generalist given the same brief — if they can't, the apparatus isn't adding what it claims. *Corrected 2026-09-27: v1 of this note had the direction inverted.*). Currently undefined even for the project's own voices. Draft proposal: §11.3.
3. **How productized is voice authoring?** Fully self-serve persona pipeline (hard — automate DR + validation) vs guided wizard with internal-grade review vs builders submit cards built elsewhere. Affects how much of the artisanal pipeline must become product.
4. **Moderation ownership + liability terms** for user-built flagged content (takedown, builder-responsibility, provenance display).

---

## 9. Relationship to existing plan + OPEN_ITEMS

The hub is **built on Phase 2, not instead of it**:
- **Phase 2.1** (FU#42 split-card + C52 event-config) is the hub's foundation — the voice-card/deployment-card split is what lets one voice publish into many deployments; event-config is what lets the GUI set up an event without code.
- **Phase 2.2** (vendor abstraction) carries cost-metering (point 3).
- **`runtime/OPEN_ITEMS` Section H** (agentic backlog) — the cheap robustness wins (C43 self-recovery, dup-guard) get promoted from design-and-shelve to "worth it for babysitting-reduction"; C60 agentic triage stays optional under the operator-reviews-in-GUI model.
- **voices `OPEN_ITEMS` §24/§28** (reader-gates) → become the ethics-flag *publish gate*.
- **voices §33** (validation track) → becomes the *validation badge* + its bar (decision #2).
- **voices §34** (agentic Step-3 per-voice card fields) — only relevant if a deployment profile wants visible deliberation; orthogonal to the hub.
- **The vatican SPEC** is the first *deployment-profile* the hub would offer (annotation mode) — a worked example of "a council + an input shape + an output mode" as a configured product.

**Net-complexity gate still applies:** the hub is additive surface. Build the **vertical/vatican deployment first** (cheapest, most contained), prove the runtime-as-product, then add the library/contribution layer — don't build the marketplace before there's a council worth publishing into it.

---

## 10. Bottom line

The hub is the most ambitious fork and re-imports a contained slice of the complexity the studio shed (UGC accounts + moderation/takedown). But the **flag taxonomy + build/publish split + attestation-registry** is the right governance design, and it's the truest expression of the project's own subject: the construction of more-than-human representatives, made visible, kept human, and opened to others under conditions. Recommended sequencing: **studio console + vertical deployment first → library/contribution layer second.** The decision that now gates everything: **the publish tiers and per-flag clearance (§8.1)** — draft answers in §11.

---

## 11. DRAFT — governance spec + the two open vision decisions (proposal 2026-09-27 — NOT decided)

Drafted overnight 2026-09-27 as "Move 0" (the first step toward the hub, per the 2026-06-14 sequencing). Every item is a **proposal with a recommendation**; nothing here is decided until the operator marks it. Suggested order to decide: **11.6** (quick yes/no) → **11.5** (shapes all of Phase 2) → **11.1–11.4** (only needed once the hub moves ahead of the vertical vatican deployment).

### 11.1 Publish tiers (answers §8.1, part 1)

| Tier | Who can deploy the voice | Entry requirements | Voice card shows | Revocation |
|---|---|---|---|---|
| **T0 Private** (default) | builder only | none beyond an account; flags auto-attach; any ethics flag stamps every output "unreviewed construction — ⟨flag⟩" | flags, provenance (builder, corpus list, pipeline version), "Private — not reviewed" | builder deletes |
| **T1 Org-shared** | builder's org | builder self-attests each flag (statement per flag); corpus license/permission declared; no *blocked* flag (11.2) | + attestations, marked "self-attested" | builder or org admin |
| **T2 Public library** | anyone | every ethics flag cleared per 11.2 (named-reviewer attestation where required, displayed); validation badge computed (disclosure, not a gate); provenance complete; platform checks attestation *presence and form* (not truth) | + reviewer attestations (name, relationship to the tradition, scope, date), validation badge, license | platform takedown (11.4) or builder unpublishes |

Promotion is explicit and one tier at a time; demotion is instant.

### 11.2 Per-flag clearance (refines the §8.1 starter table)

| Flag | Detection | T1 (org) | T2 (public) | Hard block? |
|---|---|---|---|---|
| sacred-grammar / living-tradition first person | corpus signal (devotional / liturgical first person, living religious tradition) + builder declaration | self-attest | **named in-tradition reader attestation** — name, stated relationship to the tradition, what was reviewed (card *and* sample outputs), date — shown on the card | no; but no attestation ⇒ cannot reach T2 |
| indigenous collective (speaks-AS) | `subtype` system/collective + corpus signal | self-attest + declared mediation structure | **community attestation** from a named body or role (not a self-appointed individual) + mediation structure shown on the card | no; same rule |
| living person | birth/death dates in voice_config (auto) | **blocked** unless consent on file | consent on file (documented, revocable) | **yes** without consent |
| real identifiable person (deceased) / estate-sensitive | named historical person; known rights holder | self-attest + rights note | rights note + disclaimer + takedown path; an estate objection demotes to T0 immediately pending review | no |
| validation (§33) | test result | shown | shown | no — disclosure only |

**Re-review triggers:** a card rebuild that changes any flagged field; a reviewer withdraws their attestation; an upheld takedown.

### 11.3 Validation badge (answers §8 decision #2 + voices §33)
Three levels, **disclosed, not gated**:
- **Unvalidated** — default.
- **Reader-reviewed** — a named domain/tradition reader reviewed *outputs* (not only the card); their verdict is attached. This is §33 point 1: the reader-gate reframed as a validation instrument.
- **Blind-tested** — on ≥10 paired briefs, a domain expert **identifies** the configured voice vs a competent generalist given the same brief in ≥80% of pairs **and** rates it more faithful in the majority. Both halves matter: distinct-but-wrong (caricature) is also distinguishable, so identification alone is not enough. *(Thresholds are a starting proposal, to calibrate on the project's own ten voices first.)*

### 11.4 Takedown + provenance
- Every T1/T2 card shows builder, build date, pipeline version, corpus sources with licenses, flags, attestations, badge.
- Anyone (estate, community, rights holder) can file a takedown. Credible estate/community objections demote to T0 immediately pending review; the builder is notified; restoration requires the objection resolved.
- Builder terms: the builder attests truthfully; the platform verifies presence and form of attestations, not their truth (the §5 registry-not-adjudicator model).

### 11.5 Vision decision A — the Assembly's invariant (PLAN operator decision #10)
**Proposal:** a deployment is "the Assembly" iff all four hold —
1. **A council, not a voice** — ≥3 voices with distinct epistemic frames on the same material.
2. **Construction visible** — each voice appears as "Voice of X", with provenance reachable from the output.
3. **Disagreement preserved** — the headline output is selection/juxtaposition, never a synthesized consensus.
4. **A collective moment** — the voices meet on the same material in one visible surface. *Minimum:* juxtaposition. *Stronger form:* inter-voice response (Step 3 / visible deliberation, runtime C61).

Consequences: the vatican annotation profile **qualifies** (juxtaposition on the same paragraphs); a single-voice chat **doesn't** — name it as a different product ("a Voice from the Assembly"). A strict variant (require inter-voice response) would disqualify vatican until C61 exists. **Recommendation: the loose invariant, and label deployments that have the stronger form.**

### 11.6 Vision decision B — family-of-forms vs the net-complexity gate
**✅ DECIDED 2026-09-28: exempt, conditionally (as proposed below).**

**Proposal: exempt, with the reason on record.** The gate targets deployment surface; family-of-forms is voice-fidelity capability inside the card. Per the 2026-06-13 code read (PLAN Appendix B), runtime Steps 2+3 already support multiple forms (`selected_form`, `form_changed_from_first_draft`; the Step-3 prompt already licenses a form change). The missing link is one upstream Pass 4b edit populating the form menu, i.e. roughly one prompt edit plus a sentinel regen, and no new layer. **Condition:** if the build grows beyond that upstream edit (e.g. new runtime selection logic), it re-enters the gate.
