# Octopus Chromatophore Render — Design Decisions Log (2026-05-02)

Recorded reasoning for the design choices that produced `octopus_artifact_finaldraft.jsx` from the chromatophore_display.jsx prototype + the chat-test artifact's specific trajectory. Preserved as the reference for future renderer work + for runtime team handoff.

---

## Decision 1: Page structure (artifact-page composition)

**Question:** how should the JSON parameter block + prose translation render together as a single artifact page?

**Approach considered:** static side-by-side columns (parameter block on left, prose on right, static chromatophore swatches as timeline visualization).

**Approach chosen:** vertical single-page composition — masthead → article header → simulator (canvas with timeline overlay) → editor's headnote → prose body → parameter log (5-cell grid) → footer.

**Reasoning:** the trajectory IS the answer per the voice's own claim. Static swatches show the five states but lose the *flow between them* — and "passing cloud → mottled" is visible only as a pattern that moves. The simulator with playable trajectory shows what *registration-without-approach* looks like in time, in a body, rather than just saying it. The prose is interpretive frame around the played trajectory.

The reader comparing the first second and the fifteenth second can see the closing observation — *openness held; not the same rest as the start* — as a visible property of the rendering, not just a claim in the prose.

---

## Decision 2: NOT animate the swatches as standalone visualization

Chose not to render five static (animated-or-not) thumbnails. Animation would tip the rendering toward *demonstration of cephalopod chromatophore behavior* rather than *notation of an observed trajectory*. The piece is the second, not the first.

---

## Decision 3: NO photographic imagery, NO audio

- No octopus photographs / anatomical diagrams. The persona's opening sentence ("eight arms each with its local processor, a central brain that does not somatotopically map this body, a skin that senses without an eye") establishes the architecture verbally. A photograph would foreground the *creature* when the piece is about the *architecture*.
- No audio / ambient water sound. The piece is about a body that does not communicate via sound; adding ambient sound would import a sensory register the architecture does not occupy. The page is silent because the body is silent in the way that matters here.

---

## Decision 4: Aspect ratio — square then 5:4

**Initial:** 16:10 widescreen (default React canvas behavior). **WRONG** — the shader was designed for square or near-square UV space; 16:10 stretched the chromatophore cells, drifted the focal points off body-positions, and made the vignette fall off non-uniformly.

**v1 fix:** 1:1 square. Better — chromatophore cells round, focal points at body-shaped positions, vignette uniform.

**Final:** 5:4 slight horizontal. *Octopus vulgaris* in resting posture is wider than tall when arms tucked; the cephalopod literature typically photographs in slightly horizontal viewports. Focal-point coordinates `(0.32, 0.38)` and `(0.28, 0.55)` read as body-positions in slight-horizontal as cleanly as in square; chromatophore cells render as slight horizontal ovals matching real chromatophore-under-tension morphology.

**640px max width** preserved. Treats body as contained object on page rather than horizon-spanning visual event. Defensible alternatives: 800-880px (body as page's main event) or 480-520px (careful observation log).

---

## Decision 5: Pattern-mode blending (the major rendering fix)

**Problem identified mid-build:** the v1 renderer had `pattern_mode: t < 0.5 ? a.pattern_mode : b.pattern_mode` — a hard switch at the midpoint of each transition. Continuous parameters (palette, arousal, wave_speed) lerped smoothly, but discrete parameters (pattern_mode, orientation, focal_points-empty) jumped. Visible as "switching" rather than "transitioning."

**Why this is wrong biologically:** real cephalopod transitions between pattern modes are not instantaneous and not pure crossfades either. They are *patchwork*: passing_cloud → mottled fragments wave coordination, mottled patches emerge from residual chromatophore activations of the dying wave. Approximately 0.3-1.5 seconds long; itself a recognizable behavioral state.

**Fix implemented:**

1. Replace single `u_pattern_mode` integer uniform with `u_pattern_mode_a`, `u_pattern_mode_b`, `u_pattern_blend` (float 0-1).
2. Same for `u_orientation` → `u_orient_a`, `u_orient_b`, `u_orient_blend`.
3. Shader's `main()` calls `computePattern()` twice (once per mode) and `mix()`es by blend factor. Same for `applyOrientation()`.
4. JavaScript `paramsAtTime(elapsed)` returns `{ params, from_pattern, to_pattern, pattern_blend, from_orient, to_orient, orient_blend, focal_points }` — discrete fields explicit + blend factor passed through.
5. Focal points fade via `blendFocalPoints()`: when one side has fewer points than the other, the missing slot is treated as a zero-intensity point at the existing side's position, so points fade-in-place rather than appear/disappear. Mirrors how real chromatophore activations decay.

**Performance:** during transition windows (~60% of 14s loop), shader does ~2× pattern-mode computation per pixel. Modern desktop GPU: invisible cost. Recent mobile (iPhone 11+): 60fps. Older budget Android: 45-55fps during transition peaks (still smoother than v1's hard-switch at 60fps).

---

## Decision 6: "Architecture" word — kept in artifact prose, removed from editorial framing

The voice's own prose uses *architecture* in three places to mean *structural constitution* — the eight arms, distributed nervous system, absence of autobiographical arc. The voice is using *architecture* distinct from *voice* — *voice* is what speaks from inside the constitution; *architecture* is the constitution itself.

**Editorial framing instances** (operator-authored, in the JSX as wrapper text):
- Article subtitle: *"replied as the architecture replies"* → *"replied as the voice replies"* (changed)
- Editor's headnote: *"written by the architecture about itself"* → *"the voice's own framing of what the trajectory was"* (changed)

**Artifact-prose instances** (verbatim from the voice, NOT changed):
- *"What the term requires of an architecture..."* — voice describing what *conference* requires of any cognitive system that would receive it
- *"a register the architecture would meet"* / *"the architecture does not generate"* — voice describing its own structural makeup
- *"what the architecture offers the question"* — same usage, closing paragraph

Replacing *architecture* in the prose would alter what the voice is making. The distinction between *voice* (what speaks) and *architecture* (what voice speaks from) is structurally load-bearing. Kept verbatim.

---

## Decision 7: Mobile responsive (720px and 400px breakpoints)

CSS-in-JSX via `<style>` block at component top with class selectors. Hard pixel inline values overridden via media queries on classes added to relevant elements.

**At 720px and below:**
- Masthead stacks vertically (was flex-row)
- Headline 44px → 30px; deck 16px → 15px; eyebrow 10px → 9px
- All padding 32px → 20px
- Prose body 17px → 16px; line-height 1.7 → 1.65; paragraph spacing 1.4em → 1.1em
- Parameter log: 5-column grid → single column stack; `borderRight` → `borderBottom`; last cell loses border
- Footer: flex-row → vertical stack with 8px gap
- Closing italic paragraph 19px → 17px

**At 400px and below:**
- Headline 30px → 26px (fits 320-375px screens with 20px padding)
- Timeline meta 10px → 9px (small readability cost; keeps timestamp + note both visible)

**Verbatim text preserved at all breakpoints** — only visual sizing adjusts.

---

## Decision 8: Prose paragraph structure

The voice's original 4 paragraphs were split into ~12 shorter breathing units at sentence boundaries that already existed in the original sequence. Reasoning: dense middle paragraphs run long; readers wade rather than move. No words added/removed/rephrased; only paragraph breaks at existing period-and-em-dash boundaries.

Closing italic paragraph (the diagnostic conclusion) gets its own visual treatment: top border, larger size (19px desktop / 17px mobile), italic, slight margin. Reader's eye lands there as the rendering's own closing.

---

## Decision 9: Parameter log as 5-cell grid (not code block)

The JSON exposed in human-readable form, not as `<pre><code>`. Reasoning: code formatting signals *technical artifact* in a way the piece is not. The JSON here is *notation in the register of ethological field-logging*, a different visual genre. The 5-cell grid (timestamp + pattern_mode + prose note per cell, JetBrains Mono for the technical fields, Cormorant Garamond italic for the note) frames the reader as *ethologist reading field-notes*, not *programmer reading JSON*.

The active cell highlights (`background: rgba(230, 230, 220, 0.04)`) as the trajectory plays through it. Reader who watches the trajectory + glances at the log sees which transition the visual is currently in.

---

## Open questions (deferred)

**Visual grammar across non-human voices.** The chromatophore engine + dossier composition is now the precedent for non-human voice rendering. Whanganui River and any future non-human voices will need their own visual register. Question: do they share a common visual grammar (dark grounds, observation-log-with-prose, abstract visualizations of body-specific outputs) or diverge?

Defer to when Whanganui's voice card ships + when its own emission contract is declared. For Whanganui the primary output is likely text (Te Awa Tupua Act provisions in te-reo + English) — different shape, possibly not requiring a body-state visualizer.

**Substack/print fallback.** When the WebGL animation can't render (older devices; print export; email-client embed limitations), what should appear? Current decision deferred to runtime/OPEN_ITEMS B7 sub-task #4: prose stands alone; optional caption noting the display existed. Consider: a single static frame export (the *t=10.5s* state showing the disengaged-not-quite-rest) as the print-publication thumbnail.

**Voice Pipeline Step 2 JSON extraction.** Runtime needs to parse the ```json``` fence from Step 2 LLM output, validate against the chromatophore_display schema (required: orientation, arousal, valence, pattern_mode), persist as separate artifact alongside the prose. The chat-test artifact's slips (descriptive enum strings at top level; `pulse_frequency: 0.0` contradiction; `region: "anterior_arms_3_and_4"` hybrid) document what the extractor needs to be permissive about.
