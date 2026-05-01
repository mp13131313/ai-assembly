# Pipeline downstream of Step 2 — design first, then implementation

**Date:** 2026-04-30
**Status:** Conceptual reasoning, not spec. No implementation decisions yet. The Step 3 redesign work paused pending this; cannot make Step 3 mechanics decisions without knowing what consumes Step 3's output.

---

## Why this doc, and why this order

Yesterday and this morning we treated Step 3 as the next thing to design. That's wrong, because Step 3's output shape, the artifact's audience-grammar, the metadata structure, and even the question "is the artifact body addressed to other voices or to the original question?" all depend on what *comes after* Step 3 in the chain.

The chain is at least six layers, only two of which (Step 2, Substack) are presently settled in shape. The rest are sketched in the Frame Concept doc but not specified to the level where Step 3 can be designed against them.

This doc reasons through the chain in order — what each layer is for, what it consumes, what it produces, and how it relates to the layers before and after. Where the architecture is settled (briefing, Frame Concept, prior decisions), name it. Where there's a real design question, surface it. End with a clean operator decision menu.

**No implementation; no schemas; no prompts. Architecture only.**

---

## The chain at a glance

```
        ┌──────────────────────────────────────────────────────────┐
        │                  the night's pipeline                    │
        │                                                          │
        │   Step 2     Step 3      Editor       Broadsheet         │
        │   (voice)──→ (voice)──→  (frame)──→   (frame)            │
        │   first-     amended     curates      assembles          │
        │   draft      artifact    +            front page         │
        │                          frames                          │
        └──────────────────────────────────────────────────────────┘
                                      │
                                      ▼
        ┌──────────────────────────────────────────────────────────┐
        │             what the audience encounters                 │
        │                                                          │
        │   Microsite              Substack         (Newsletter)   │
        │   (per-artifact pages)   (HoBB voice)     (HoBB blurb)   │
        │   permanent              Day 2/3/4 AM     daily          │
        │                                                          │
        └──────────────────────────────────────────────────────────┘
                                      │
                                      ▼
        ┌──────────────────────────────────────────────────────────┐
        │      separate downstream (out of scope for this doc)     │
        │                                                          │
        │   Closing show (Day 3 evening) — reads across nights     │
        │   Day 4 goodbye (Day 4 morning) — references one voice   │
        │                                                          │
        └──────────────────────────────────────────────────────────┘
```

Each layer is a separate design problem. The chain can't be designed top-down OR bottom-up cleanly — it has to be reasoned through middle-out, because each layer's output shape is constrained by what the next layer needs and what the previous layer produces. This doc walks the chain and surfaces the constraints.

---

## Layer 1 — Step 2 (settled)

**What it is:** the voice's first-draft artifact, in its own form, addressing the Provocateur's formulations from tonight.

**What it produces:** one artifact per voice per night (`step2_first_draft_artifacts/<voice_slug>.json`). Carries `artifact_text`, `selected_form`, `focus_decision`, `stance`, `themes_covered`, lineage back to Step 1 detailed responses.

**What it does NOT produce:**
- title or subtitle (decided 2026-04-29; downstream concern)
- audience-orientation framing (no awareness of Substack, micro-site URL, or that an editor will see it)
- cross-voice consideration (Step 1+2 are private per voice)

**Status:** validated end-to-end across four dryruns. FU#61 patch (Cleopatra criterion 6) demonstrates voice-card patches can lift standalone Layer 1 surface without compromising Layer 2 substance. Pattern propagates to other hard-form voices when their cards build.

**No design questions open at this layer.**

---

## Layer 2 — Step 3 (the layer being redesigned)

**What it is for** — this is the question we cannot yet answer without knowing what comes after.

The briefing (line 91, 177, 179) names Step 3 as the moment when the Assembly's collective character is constituted overnight, via cross-voice deliberation at the artifact layer, on shared-theme territory. Per briefing 177: voice reads the artifacts of others on shared themes, decides whether to amend (sharpen disagreement, integrate stronger framing, leave unchanged), amendments are visible and reference the other voice, metadata records who amended in response to whom.

But "amendments visible / reference the other voice" admits multiple architectural readings, and the right reading depends on what's downstream:

**Reading A — Step 3 produces audience-facing finalized artifacts.** The Step 3 amended artifact IS what lands at `/night-1/plato`. The audience encounters Step 3's output directly. Cross-voice visibility has to live INSIDE the artifact (correspondence shape) OR in a separate metadata footer the microsite renders alongside.

**Reading B — Step 3 produces the artifact-as-finalized-for-the-editor.** The Step 3 amended artifact is the voice's last word; the editor (Layer 3) wraps it for audience consumption. Cross-voice visibility lives at the editor/frame/microsite layers, not in the artifact body. The artifact body addresses the original formulation. The editor walks the cross-voice exchange in its own register.

**Reading C — hybrid.** Step 3 produces an artifact that addresses the original formulation BUT also produces structured engaged-peers metadata. Editor consumes both. Voice may inline-cite other voices ONLY when its own framework naturally engages another framework as a move. The metadata is what cross-voice visibility relies on; inline citation is voice-led optional.

I previously (this morning) recommended Reading C ("the weak reading"). That recommendation only makes sense if there IS an editor layer that does cross-voice visibility work. If there isn't, Reading A is forced. If the editor does extensive cross-voice work, Reading B becomes cleaner than C.

**Step 3 design questions hold pending Layer 3 (editor) decisions.** Specifically:
- (i) does an editor layer exist at all?
- (ii) what does the editor consume? (just artifact text? + engaged-peers metadata? + Step 1 detailed responses?)
- (iii) what does the editor produce? (curatorial preamble? title? pull-quotes? cross-voice contrast paragraphs?)
- (iv) does the editor or the artifact body carry cross-voice visibility?

Reasoning continues at Layer 3.

---

## Layer 3 — Editor / Frame (the new layer)

**Why this layer must exist** — three converging reasons surfaced over the past 24 hours:

**Reason 1 — Layer 1 surface for harder-form voices.** Cleopatra's prostagma, Whanganui's proclamation, the Octopus's chromatophore display do not clear briefing's Layer 1 (Encounter) standalone for a phone-reading senior at breakfast. The artifact form is correct (Layer 2 substance is what only this voice could produce); it just doesn't land cold. The Cairo encounter pattern (Egyptian Museum / Philae / BM) is the proven solution: artifact preserved at full register, narrating voice does the comprehension work, narrator stays outside the artifact's voice. This requires a curatorial layer that the Voice Pipeline doesn't have.

**Reason 2 — title + subtitle generation.** Voice no longer produces these (decided 2026-04-29; voice doing breakfast-headline work would compromise voice fidelity). Microsite needs them (URL pages need titles); Substack needs them (pull-quote anchoring); broadsheet needs them (front-page headlines, though those have their own per-voice headline-poetics requirements). They have to come from somewhere. The editor is the natural home.

**Reason 3 — cross-voice contrast.** Briefing 177 says amendments are visible and reference other voices. If we follow Reading C (Step 3 artifact body addresses original formulation; cross-voice signal lives outside the body), then SOMETHING has to make cross-voice visibility happen for the audience. The editor walking the cross-voice exchange ("Plato sharpened against Cleopatra on the question of seal-and-petition") is one of the cleanest places for this work to live. (The other place is Substack — but Substack is Day 2/3/4 morning, real HoBB voice; the editor is per-night, fictional Assembly voice. Different timing, different register, different surface.)

**What this layer is** — the curatorial / journalistic intelligence of the fictional Assembly. NOT a voice; an institution. Third-person register; sympathetic-archival; doing comprehension scaffolding the artifact deliberately doesn't.

**What it consumes:**
- The Step 3 amended artifact (text + voice-side decisions: focus, stance, form)
- engaged-peers metadata from Step 3 (who this voice read; what the voice did with each)
- The Provocateur briefing (the original formulation; context_narrative; selected_quotes — for naming what was being asked)
- Possibly the persona card (for headline-poetics-per-voice — the per-voice register the editor's headline must hit; per Frame Concept §"headlines do specific work")
- Possibly Step 1 detailed responses (for pull-quote sourcing — the most quotable lines of the voice's reasoning)

**What it produces, per voice per night:**
- **Title** — ~5-9 words, in the voice's headline register (Gorgias-style for Plato, prostagma-formal for Cleopatra, song-title for Marley, wire-service-terse for the river)
- **Subtitle** — optional second-deck, longer; Frame Concept's broadsheet form uses these
- **Curatorial preamble** — ~100-200 word museum-label text. Per FU#61 finding, the preamble is voice-register-conditional: hard-form voices get the museum label; dialogue-form voices get a lighter pull-quote-flavored intro or no preamble at all. Lives ABOVE the artifact on the microsite (strip rule amended for hard-form voices).
- **Pull-quotes** — 1-3 per artifact, sourced from artifact text, for Substack consumption
- **Cross-voice contrast text** — short paragraph(s) walking what this voice did with which peers, in editor's own register. ~50-150 words. Lives in the broadsheet AND/OR in the microsite footer. NOT in the artifact body.

**What it produces, per night, panel-wide:**
- Material for the broadsheet front page (lead-story choices, deck headlines, contrast moves)

**Design questions for this layer:**

- **Q1 — One pass or many?** Is the editor a single Sonnet pass per voice that produces title + subtitle + preamble + pull-quotes + contrast text in one call? Or several specialized passes? Single-pass is simpler; multi-pass lets each output get specialized prompting. Recommendation: single per-voice pass for {title + subtitle + preamble + pull-quotes}; separate per-night pass for the broadsheet assembly (which needs cross-voice synthesis).

- **Q2 — How much human, how much AI?** Three options: (a) fully AI-generated (Sonnet drafts everything, no human polish); (b) AI-drafted, human-polished (~5-15 min per artifact for an editor); (c) human-written from scratch reading the artifact + metadata. For Athens scale (10 artifacts × 3 nights = 30 editorial passes per night surface, though some surfaces consolidate), (a) is operationally cheap, (b) is realistic for a 1-person editorial polish budget, (c) doesn't scale. Recommendation: (b) for Athens — AI drafts, operator polishes 5 min per artifact in the early morning before Substack ships.

- **Q3 — Voice-register-aware editor, or one editor register?** Frame Concept §"headlines do specific work" insists each voice's headline hit that voice's register (Gorgias-style for Plato, etc.). This means the editor must read the persona card's headline-poetics (or an editor-side per-voice register spec) and write IN that register. Same likely true for the curatorial preamble (museum-label register has voice-shape variants — chancery-document for Cleopatra, ode-context for Marley). One editor with per-voice register awareness vs. multiple editor configurations: recommend one editor pass with per-voice register input.

- **Q4 — Strip rule on microsite: voice-register-conditional, yes?** Frame Concept §"micro-site (the artifacts, plain)" says artifact pages are stripped — small masthead identifier, then the artifact, no chrome between reader and substance. FU#61 finding says hard-form voices need the curatorial preamble at the artifact page (otherwise the forwarded-URL reader hits prostagma cold). Resolution: strip rule becomes voice-register-conditional. Hard-form voices: preamble above artifact; everything else below the strip rule. Dialogue-form voices: stripped as before; preamble (if any) inline with masthead, lighter touch. Recommendation: yes, voice-register-conditional. Already surfaced in FU#61.

- **Q5 — Where does cross-voice contrast text actually appear?** Three plausible homes:
  - In the broadsheet front page (one cross-voice section: "Tonight's exchanges")
  - In the microsite per-artifact footer (per-voice: "this artifact engaged X and Y")
  - In the Substack walk (HoBB voice describing the cross-voice exchange)
  All three could carry it. They're not exclusive. Best architecture: editor produces ONE cross-voice contrast block per voice (the metadata-shape, easy to consume); each surface (broadsheet, microsite, Substack) renders or summarizes it in its own register. Recommendation: editor produces voice-side cross-voice block; surfaces consume.

---

## Layer 4 — Broadsheet (the Edition layer)

**What it is:** one front-page broadsheet per night, in the fictional Assembly News register (Caslon-style typography, multi-deck headers, masthead with incrementing issue number, ten voice headlines, short reportage paragraphs). Per Frame Concept §"newspaper": one of N artifacts per night, NOT the wrapper of the others. Reader can engage with broadsheet alone, or with the ten artifacts alone, or both. Lives at `/night-1/edition`.

**What it consumes:**
- Editor outputs (titles, headlines, voice-register awareness)
- Cross-voice contrast blocks (for the "tonight's exchanges" type paragraph if used)
- All ten amended artifacts (for selecting lead stories, source headlines, etc.)
- Headline-poetics per voice (from persona card or editor spec)

**What it produces:**
- Front-page asset for the night (HTML or static rendered image; production format separate decision)
- Lives at `<microsite>/night-N/edition`

**Design questions:**

- **Q6 — Edition Pipeline as separate pass, or part of editor pass?** Frame Concept §"production implications" envisions an Edition Pipeline as a new pipeline pass running after Step 3. If editor (Layer 3) is per-voice and editor produces enough for the broadsheet to assemble deterministically (titles, headlines, voice-register, contrast blocks), then "Edition Pipeline" is just a deterministic Python assembly + visual layout pass — no LLM needed. If editor doesn't produce enough, Edition Pipeline is its own LLM pass that reads all 10 artifacts + does cross-voice synthesis at the panel level. Recommendation: editor produces voice-side; Edition Pipeline is deterministic Python assembly + visual layout. Cleaner; testable; cheaper.

- **Q7 — Broadsheet visual production: what tooling?** Frame Concept §"production implications" lists "front-page layout, masthead, ten-pointed star device, headline placement rules" as needing design work. This is graphic design + page typesetting territory. Options: (a) static HTML/CSS template + per-night content fill; (b) generate as image (Playwright or similar) for screenshot/share; (c) PDF with print-faithful layout. Recommend (a) for microsite + (b) on top for share/preview. Out of scope for this doc; flag for the broadsheet mini-concept.

- **Q8 — Wire-service unavailability + strikethrough discipline.** Frame Concept §"newspaper" specifies these as signature moves but caps them at 1 each per edition. Editor (or Edition Pipeline) needs to choose which voice gets the wire-service paragraph each night, and where the strikethrough lands. This is editorial judgment per night; either AI with strong constraints or operator hand-pick. Recommend operator hand-pick — high-impact decision, low-effort.

---

## Layer 5 — Microsite

**What it is:** the permanent home of all 30 artifacts (10 voices × 3 nights), per-night editions, and an index. Static site, content repo, hosting (Astro or Next.js + Vercel/Netlify per Frame Concept). Stays live after Athens.

**What it consumes:**
- Step 3 amended artifacts (the artifact body)
- Editor outputs (title, subtitle, curatorial preamble, pull-quotes — for hard-form voices the preamble appears above the artifact)
- Engaged-peers metadata (for the per-artifact footer cross-voice listing)
- Broadsheet asset per night
- Edition / index data

**Per-artifact page shape** (revised from Frame Concept §"micro-site"):

For dialogue-form voices (Plato, Dostoevsky probably, Arendt):
```
[masthead identifier — small, top]
[title]
[subtitle, if any]
[artifact body — stripped, no chrome between]
─────
[engaged-peers footer: "this artifact engaged Cleopatra (sharpened-disagreement on theme of seal-as-constitutive); Marley (integrated-stronger-framing on theme of musical pedagogy)"]
[link to the night's edition]
```

For hard-form voices (Cleopatra, Whanganui, possibly Marley if his lyric-on-screen needs the same scaffolding, possibly Octopus):
```
[masthead identifier — small, top]
[title]
[subtitle, if any]
[curatorial preamble — ~150 words, museum-label register, sets up form + central move]
─────
[artifact body — full register, untouched]
─────
[engaged-peers footer]
[link to the night's edition]
```

The differentiating element is the curatorial preamble for hard-form voices. Strip rule remains; just made voice-register-conditional per FU#61 finding.

**Design questions:**

- **Q9 — Index page architecture.** Per night: edition front page + 10 artifact pages + a simple voice index. Across nights: a 3-night per-voice page (Plato N1, N2, N3 in one place)? A theme-spanning view? Per Frame Concept §"micro-site" — minimum viable is per-night index + per-voice 3-night view. Recommend that as MVP; more elaborate views post-Athens.

- **Q10 — Engaged-peers footer rendering.** Plain text? Linked to other voices' artifacts? Iconographic? Recommend: short text + links. Reader can click peer-voice name to read that voice's artifact directly.

- **Q11 — Mobile-first?** ~750 senior professionals reading at breakfast on phones — mobile-first is non-negotiable for Layer 1. Note explicitly. Affects the curatorial preamble's display (collapsible? always-shown?). Recommend always-shown on mobile; preamble IS the encounter for hard-form voices.

---

## Layer 6 — Substack (HoBB voice)

**What it is:** the bridge between the fictional Assembly and the real audience. HoBB's real Substack publication; HoBB's editorial voice; engages substance directly. Per Frame Concept §"substack" — the only surface that does NOT enter the fiction. Day 2 + Day 3 mornings: read-through of previous night's artifacts. Day 4 morning: Night 3 read-through + goodbye.

**What it consumes:**
- The 10 amended artifacts from the previous night (the substance)
- Pull-quotes from editor (or HoBB picks own)
- Cross-voice contrast blocks from editor (HoBB walks the exchange in their voice)
- The previous night's broadsheet (referenced as existing; not routed through)
- Real HoBB editorial sensibility — the human writer's voice

**What it produces:**
- One Substack post per Day 2 + Day 3 + Day 4 morning
- Format: HoBB-voice walkthrough; pull-quotes from artifacts (NOT from broadsheet); deep-links to microsite per-artifact pages
- Engagement-with-substance is the load-bearing function (per Frame Concept §"Substack")

**Design questions:**

- **Q12 — How much AI vs. how much HoBB-editor?** This is a real-organization decision (HoBB writes their own Substack). Range: (a) HoBB writes from scratch reading artifacts; (b) AI drafts, HoBB heavily edits; (c) AI drafts, HoBB lightly polishes. The Substack is the place where HoBB's voice is real and load-bearing — recommend (a) or (b). For our pipeline scope: produce the Substack draft (option (b)) and hand to HoBB editor; let them edit. NOT pipeline-final.

- **Q13 — Substack draft pipeline pass: when does it run?** Could run immediately after broadsheet (overnight, ready by 6am for HoBB editor). Could run early-morning when HoBB editor is at the desk. Recommend overnight — gives HoBB editor max polish time before Day 2 morning send.

- **Q14 — Cross-voice walking specifically.** Substack is one of three places cross-voice deliberation can be made visible to the audience (Q5). HoBB voice walking "Plato sharpened against Cleopatra on..." is rich, warm, real-organization — probably the strongest single carrier of cross-voice visibility for the audience. Recommend Substack as primary carrier of cross-voice narrative; broadsheet does shorter / typographic cross-voice contrast; microsite footer is structural reference.

---

## What this design implies for Step 3

Now that the chain is sketched, Step 3's open questions clarify:

**The audience-grammar question** (artifact body addressed to other voices vs. original formulation) resolves to **Reading C — final position on original formulation, with engaged-peers metadata for the editor to consume.** The editor (Layer 3) carries cross-voice visibility into the audience-facing surfaces (broadsheet, microsite footer, Substack). The artifact body stays clean.

**Step 3's output shape:** (a) amended artifact text addressing original formulation, (b) engaged-peers structured metadata. Both consumed by the editor.

**The 6 prior decisions I asked about now resolve more naturally:**
- #1 (artifact addresses what?) → original formulation. The chain enables this without losing cross-voice visibility (editor carries it).
- #2 (3-shape vs 5-shape engagement vocabulary) → 3-shape briefing-native is sufficient since editor walks the nuance in its own register.
- #3 (per-peer engagement) → permitted; editor needs per-peer detail for the contrast text.
- #4 (inline citation) → voice-led optional, framework-natural only — same recommendation as before, but now on firm architectural ground (cross-voice visibility doesn't depend on inline citation).
- #5 (migrate old Step 3 files) → migrate.
- #6 (block on frame layer or accept degraded) → resolves differently: Step 3 redesign + editor (Layer 3) build go together. Microsite + broadsheet + Substack can land in any order; their absence degrades gracefully.

But none of these decisions should be locked until the editor design is approved.

---

## What this design surfaces as new architectural work

In rough order of build importance:

1. **Editor / Frame layer (Layer 3) — new pipeline pass.** Per-voice Sonnet (probably) call producing title + subtitle + curatorial preamble + pull-quotes + cross-voice contrast block. Reads amended artifact + engaged-peers metadata + Provocateur briefing + persona card (for headline poetics). Lives in `runtime/flows/editor_flow.py` or similar. **No spec exists.** This is the largest piece of new architecture.

2. **Step 3 redesign** — see Step 3 redesign doc; now framed as "produces editor input," cleaner architecture.

3. **Per-voice headline poetics** — Frame Concept §"production implications" lists this as needing spec. Either lives in persona card (new field) or in editor's per-voice config. Per Frame Concept this should be a one-paragraph specification per voice with 3-5 examples. Build-side, persona-pipeline-adjacent or editor-config.

4. **Broadsheet (Edition Pipeline)** — deterministic Python pass per Q6, plus visual production. Two pieces.

5. **Microsite** — static site with the per-page architecture sketched above. Astro or Next.js. Hosting decisions per Frame Concept.

6. **Substack draft pipeline pass** — Sonnet call producing HoBB-style draft for the editor to polish. Smaller than editor pass.

7. **Frame voice register taxonomy** (FU#61) — per-voice editor register specification. Map of which voice gets which editor register (museum-label, pull-quote, liner-notes, etc.).

8. **Frame Concept doc revision** — strip rule becomes voice-register-conditional. Add the three-layer encounter pattern (broadsheet/microsite/Substack consume editor output) explicitly.

---

## Decisions for the operator (BIG architectural decisions, not implementation)

**A. Approve the existence of an editor / frame layer (Layer 3) as a separate pipeline pass between Step 3 and the audience surfaces?**

The reasoning above argues this is structurally needed (Layer 1 surface for hard-form voices; title/subtitle generation; cross-voice contrast text). Without it, Step 3's options collapse to either-or (correspondence shape OR no cross-voice visibility) and Frame Concept's three-surface architecture loses its connective tissue.

If approved: editor design becomes the next layer to spec out (and Step 3 redesign waits on the editor's input contract).

If not approved: alternatives are (i) bake editor work into Step 3 itself (voice does its own museum-labeling, which we already know loses voice fidelity); (ii) bake editor work into the microsite renderer (but cross-voice contrast is content, not template); (iii) move all of it to human-written (operator-written editorial per artifact, doesn't scale to 30 artifacts × 3 nights).

**Recommendation: approve.**

**B. Editor pipeline pass is per-voice (one call per artifact) producing title + subtitle + preamble + pull-quotes + cross-voice contrast?**

This is the cleanest unit of work. Per-voice means voice-register awareness is local; editor output is voice-shaped; broadsheet does deterministic assembly across the 10 voices.

**Recommendation: yes.** Alternative: per-night editor that produces all 10 voices' editorial in one massive call. Less voice-register fidelity per voice; harder to retry on per-voice failure; harder to debug.

**C. Editor produces AI-drafted output for operator polish (option (b) in Q2), not fully AI nor fully human?**

For 10 voices × 3 nights = 30 editorial passes, operator polish at ~5 min per artifact = ~2.5 hr early-morning work per night. Realistic. Pure-AI loses editorial judgment; pure-human doesn't scale.

**Recommendation: yes.** Operator polish is the existing pattern with Substack already.

**D. Strip rule on microsite becomes voice-register-conditional (curatorial preamble appears for hard-form voices, not for dialogue-form)?**

Already surfaced as FU#61 finding. Architecturally sound: museum labels next to paintings is the right inheritance for hard-form voices; dialogue-form voices don't need the scaffold.

**Recommendation: yes.** Update Frame Concept doc accordingly.

**E. Cross-voice deliberation visibility distributed across all three audience surfaces, but Substack as primary narrative carrier?**

Microsite footer = structural per-artifact reference; broadsheet = typographic per-night contrast; Substack = narrative cross-voice walk in HoBB voice.

**Recommendation: yes.** No single surface carries all the work; surfaces complement.

**F. Build order: editor first, then Step 3 redesign against it?**

Editor design (or at least its input contract) has to settle first because Step 3's output shape is constrained by what editor consumes. Once editor input contract is defined, Step 3 redesign becomes cleaner. Microsite + broadsheet + Substack can land in any order downstream of editor.

**Recommendation: yes — editor first.**

---

## What's NOT addressed in this doc (deferred)

- **Closing show pipeline** (Day 3 evening) — separate downstream concern; reads across all nights; not in the per-night chain above. Worth designing after editor + Step 3 land.
- **Day 4 goodbye** (Day 4 morning) — single-voice + HoBB; small spec; defer.
- **Daily HoBB newsletter integration** — operationally separate; HoBB tooling.
- **Edition Pipeline visual production** — graphic design + page typesetting; separate problem.
- **Implementation details** — file layouts, prompt structures, concrete schemas, code diffs. None of this until architecture A-F decisions are made.

---

## Recommended next step

If you approve A-F as recommended:

1. I draft `EDITOR_LAYER_DESIGN_2026_04_30.md` — the editor / frame layer's input contract, output schema, per-voice register specification, prompt structure, and the persona-card vs. editor-config question for per-voice headline poetics. ~400-500 lines, conceptual + implementation-ready.
2. After editor design lands: revise the Step 3 redesign doc against the editor's input contract. Most of the existing draft holds; the engaged-peers metadata becomes "what editor consumes" rather than "what microsite renders directly."
3. After both: implementation phase — editor pass first, then Step 3 redesign, then microsite per-page renderer (uses editor + Step 3 output).

If A-F shift in any way, the next-step doc shifts correspondingly.

---

*End of pipeline downstream design. No code, no implementation. Architecture decisions A-F first.*
