# Memo to voices thread — length cap, card-side surgery after runtime fix

**Date:** 2026-05-05
**Status update 2026-05-05 evening:** ✅ SHIPPED + CLOSED. Three card-side surgical patches landed in athens-2026 (`9dae9b9`): Dostoevsky 350-750w (operator-bumped from initial 500w draft); Hannah Arendt 350-750w (operator-bumped); Octopus 350-500w prose-channel front-loaded with explicit "no length applies to JSON channel" clarification. Path-(b) Derive regenerated chat_system_prompt for all 3. Operator decision: NO max_tokens enforcement — clean card-side resolution preferred. Closes voices/OPEN_ITEMS §27 (CLOSED) + cross-refs runtime/OPEN_ITEMS C38. Authoritative current-state: `voices/OPEN_ITEMS.md §27`. This memo preserved as historical artifact.

**From:** runtime thread
**To:** voices thread
**Cross-references:** `voices/OPEN_ITEMS.md §27` (length anchoring + dryrun audit, 2026-05-04 PM); `runtime/OPEN_ITEMS.md C38` (length-cap enforcement gap, now partially shipped)

---

## What changed runtime-side

`runtime/flows/shared/prompts/voice_step2_artifact.md` — moved `length_and_format_constraints` from `<form>` "Anchor in:" to `<composition>` "Pass:" (commit `61b1deb`, 2026-05-04 PM). Quality_criteria stays last in Pass: ordering. Single-line .md edit; no token cap, no truncation, no API change.

Reframes length from a form-decision *anchor* (gradient input alongside `medium`, `aesthetic_qualities`, `characteristic_output_structure`, etc.) to a binary *test the artifact must clear* — same semantic register as `quality_criteria`. The voice now reads its `length_and_format_constraints` field as a check on the finished work, not as historical-tendency context to ground form-choice in.

## Evidence — Dostoevsky variance test

Re-ran Step 2 for Dostoevsky against the v2 dryrun's existing Step 1 outputs (same model, same card, same upstream inputs; only `voice_step2_artifact.md` changed):

| | words | over 350-550 cap |
|---|---|---|
| Pre-fix (2026-05-04 PM dryrun) | 980 | +430 |
| Post-fix (2026-05-04 PM re-run) | 783 | +233 |

~20% reduction overall; ~46% reduction in over-cap. The prompt lever is real and works. **Not yet sufficient on its own.**

## Where the rest of the gap lives — card content

Reading all 10 voices' `length_and_format_constraints` fields side-by-side reveals a clear opener pattern. Verbatim, in compliance order:

### Compliant in dryrun (tight openers)

**cleopatra** (421w in dryrun): *"Write 300 to 500 words — the length of a working prostagma, not a treatise; readable in the time it takes to drink one cup..."*

**whanganui_river** (493w): *"Write 350–550 words. Open with whakataukī, set as its own line or short stanza..."*

### Imperative-led but over-ran

**ada_lovelace** (537w): *"Write 350–550 words of prose..."*
**scheherazade** (560w): *"Write between 350 and 550 words..."*
**plato** (575w): *"Write 350 to 550 words..."*
**ibn_battuta** (598w): *"Write 350–550 words, prose only..."*
**bob_marley** (739w): *"Write 350 to 550 words of reasoning-prose..."*

These openers are clean. Their overruns likely come from a combination of:
- Field-tail descriptive prose pulling toward expansion (Marley's *"the shape of a yard conversation that has found its centre"* doesn't constrain length)
- Pre-fix `<form>` Anchor in: framing (the prompt-side fix should help these — re-run pending to confirm)

The runtime fix alone may close most of the 7-50w overruns for this group.

### Structural softeners — runtime fix can't reach these

**dostoevsky** (980w → 783w post-fix; still +233): the field text **literally authorizes expansion**:

> *"The Writer's Diary entry is the default form — **typically** 350–550 words, prose only, paragraphs of uneven breath... When a question genuinely requires staged dialogue between two voices, a sustained scene, or a longer dramatic unfolding to do its work, **expand to meet it** — but never abandon prose for headings or lists, and never lower the body-temperature of the page. The piece, **however long**, should be the length of a man's confession before he loses his nerve."*

Three explicit softeners: **"typically"** + **"expand to meet it"** + **"however long"**. The Pass: framing now tells the voice to clear a check whose own contents authorize bursting it. The model is following the field *correctly*; the field is the bug.

**hannah_arendt** (828w): the cap range itself is **600–900 words**. She landed at 828 — strictly speaking *compliant with her card-spec*, but the conference's audience-attention cap is 500w (operator decision 2026-05-04 PM). Her card range needs to come down into the conference window. This is not a softener problem; it's a target problem.

**octopus** (643w prose-side): the number "350-550 words" is buried mid-paragraph in a much longer structural description of a two-channel artifact (JSON display + tank-side prose). The prose-side word count loses prominence to the structural framing of the JSON channel.

## Recommended card surgery (3 surgical targets)

Pre-Athens-eligible if you want to pull. Each is a single-field rewrite, ~5 min/voice:

### dostoevsky — drop the three softeners, lead Cleopatra-style

Strip "typically", strip the entire "expand to meet it" sentence, strip "however long". Lead with imperative + number. Preserve Diary-form character in the descriptive tail (uneven breath, ellipses, em-dashes — these are texture, not length permissions).

§27's draft already has the calibration template: *"Write 350 to 500 words. The length of one Diary entry compressed — the entry that catches a face on the omnibus and pursues it before the cup goes cold. Not the long polemical column."*

This is good; ship it.

### hannah_arendt — bring the range into the conference window

Current: 600-900. Conference cap: 500. §27 drafted: *"Write 350 to 500 words. The shortest arc of a thinking-essay — open one question, drive into one distinction, anchor in one scene, leave the question reformulated. The Aufbau column compressed."*

This works. Ship it. The "Aufbau column compressed" anchor is honest about what's being asked — a *short* form Arendt actually had (her newspaper columns ran short) rather than asking her single-scene essay form to compress past its natural shape.

### octopus — front-load the prose-side word count

Re-order the structural description so the prose-channel word count appears in the first sentence of the field rather than mid-paragraph. Something like: *"Tank-side prose: 350-500 words. Plus a `chromatophore_display` JSON parameter block as the body's primary output (no length applies — JSON, not prose). The prose is the human-language translation of what the display has already said..."*

Numbers up front for the bounded channel; explicit "no length applies" for the unbounded JSON channel. Eliminates the ambiguity about which artifact half is being measured.

## What voices thread does NOT need to do

Per §27 already: the per-voice corpus-anchored length rationales for the OTHER 6 voices (the imperative-led-but-over-ran group) are quality-improvement work, not fit-correction. With the runtime fix in, their overruns should compress within the cap — pending re-run to confirm. **Hold those rewrites for post-Athens** unless the next dryrun shows they're still over.

The §27 second-medium upgrade table (Plato → Myth, Dostoevsky → Letter, Arendt → Denktagebuch entry, Whanganui → Karakia cluster) is also post-Athens; the surgical card-edits above are sufficient to bring all 10 voices into the 500w window without re-architecting any voice's primary medium.

## Open question for voices thread

The three card-edits above are mechanical. The deeper question — whether Dostoevsky's voice *fundamentally requires* 700-1000w to do its work and any cap is doing violence — is left open. The runtime can deliver under-cap artifacts via the prompt + card-content fixes, but if the result is a flattened Dostoevsky, that's a voice-fidelity finding worth surfacing post-Athens.

Cleopatra's compliance suggests at least one voice can produce honest work at 500w. Whether *every* voice can is the harder question §27's medium-revisions framing was already pointing at.
