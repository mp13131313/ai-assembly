# Spec check of the not-yet-verified sections — 2026-09-28 (brief Task 5)

**Verdict:** none of the four checked parts matches the code as written.
- **Editor spec:** Stage 1 routing now happens mostly in Voice Step 2. Measured cost is ≈ $10 across Athens against the spec's $3–5. The CLI and defensive-check lists are incomplete.
- **Lifecycle:** it predates the orchestrator taking over transcription dispatch (C26) and the review gate (C28b). It also has wrong paths for `council_config.json` and the continuity files.
- **Frame Concept:** a pre-Athens design whose broadsheet, Substack and closing-show surfaces did not ship as described.
- **Transcription §7:** the reflection text should become a vendor-JSON subsection. The whole Step 1 Ingest section is Drive-era and stale for audio too.

All four sections below are complete. §5 lists six code issues found in passing, none of them filed.

- **Checkout:** `phase0-fixes` at `4e61444` (detached; contains `0998fa2`). All `file:line` references are at that commit.
- **Skipped per brief:** every row of runtime OPEN_ITEMS C67's table (rows 1–10, R1, the `CLAUDE.md` doc row), and model-choice statements.
- **Read-only evidence:** athens-2026 (`runs/athens_night_{1,2,3}/05_editor/{theme_routing,manifest}.json`; the 13 published dossiers' `metadata`; one Step 2 artifact). Nothing there was written.
- **Scratch script (offline, no API):** `<scratchpad>/dossier_costs.py` prices the 13 dossiers' token metadata at Opus 4.7 list rates: $5/MTok input, $25/MTok output, 1h cache write at 2× input, cache read at 0.1× input. These are the rates the spec and `_anthropic_call.py:121-123` use.
- **Labels:** CONFIRMED means read in code or data. PLAUSIBLE means inferred. Proposed replacement text is in blockquotes.

---

## 1. `docs/AI_Assembly_Editor_Pipeline.md` (v3.2)

### 1.1 Stage 1 — Theme Routing (lines 441–544)

**E1 — Where routing happens (lines 443–445, 452–481). CONFIRMED.**
The spec presents a four-case parser on `focus_decision` as the router, with an LLM pass "planned".

What the code does:
- **Voice Step 2 routes each voice** when it writes the artifact: `_resolve_primary_theme_id` (`runtime/flows/voice/step2_first_draft_artifact.py:196-296`).
  1. Single-response session → that theme.
  2. "Response N", read against the order the voice actually saw its Step 1 outputs.
  3. Synthesis marker with more than one output → one call to `flows/editor/synthesis_router.py::route_synthesis_voice` (step `runtime.synthesis_router`).
  4. Otherwise `primary_theme_id` is left null.
- **Editor Stage 1** takes `lineage.primary_theme_id` first (`runtime/flows/editor/routing.py:143-146`). Only when that is null does it run its own fallback chain (`routing.py:148-233`).
- **The editor's own synthesis-router call is a safety net.** It needs a client, which `editor_flow.py:150-168` always passes unless `--skip-routing` is set.

Athens evidence:
- All 29 routed entries across the three nights say `"Case A — Step 2 resolved primary_theme_id (authoritative)"`. That is 10 + 9 + 10; Night 2's Whanganui River was held.
- This includes the five "Synthesise…" voices: N1 Dostoevsky and Scheherazade, N2 Octopus, N3 Cleopatra and Octopus.
- N1 Dostoevsky's Step 2 lineage has `primary_theme_id_source: "synthesis-routed: The artifact directly answers theme_001's formulation …"`. So the router ran inside Voice Step 2 (CONFIRMED for that voice; PLAUSIBLE for the other four, which I did not open).

> **Replacement for the italic note + first paragraph (443–445):**
> Theme routing assigns each voice's Step 2 artifact to exactly one dossier (its primary theme). Most of the work happens upstream: Voice Step 2 resolves `lineage.primary_theme_id` when it writes the artifact (`runtime/flows/voice/step2_first_draft_artifact.py:196-296`) — a single-response session goes to its one theme; "Response N" is read against the order the voice saw its Step 1 outputs; a synthesis ("Synthesise…", "weave", "across all") is decided by one LLM call, the synthesis router (`runtime/flows/editor/synthesis_router.py`, step `runtime.synthesis_router` in `model_routing.json`). Editor Stage 1 takes that field as authoritative (`routing.py:143-146`) and only falls back to its own parser, and its own synthesis-router call, when Step 2 left it null. At Athens every routed voice (29 entries, three nights) came through the Step 2 field, including five synthesis voices.

**E2 — Inputs (449–450). CONFIRMED.** The list omits several inputs Stage 1 reads:
- `lineage.primary_theme_id` (`routing.py:144`).
- `artifact_text`, which the fallback router reads (`routing.py:472`).
- `selected_form`, which becomes a refusal's `form` (`routing.py:462`).
- `04_voice/operator_decisions/*.json`: held voices are skipped (`routing.py:335-366`).
- `council_config.json`, for voice names (`routing.py:396-411, 440`).

> **Replacement:**
> - `<run_dir>/04_voice/step2_first_draft_artifacts/*.json` — `lineage.primary_theme_id` (authoritative), `lineage.themes_covered`, `focus_decision`, `artifact_text` (fallback router only), `selected_form` (refusal form)
> - `<run_dir>/04_voice/operator_decisions/*.json` — voices with `hold_for_regen` are left out
> - `<run_dir>/03_provocateur/briefings/<voice>.json` — the legacy Response-N lookup and the fallback router's candidate themes
> - `<PROJECT_ROOT>/council_config.json` — each voice's display name

**E3 — Case table (454–481). CONFIRMED.** The case labels and one case do not exist in code:

| Spec | Code (`routing.py`) |
|---|---|
| Case A: "Response N" regex, Nth theme in briefings | Case A: Step 2's `primary_theme_id` (`:143-146`). "Case A (legacy)": Response N against `briefings[]` order, commented as fragile (`:148-157`) |
| Case B: explicit `theme_id` mention | **Not implemented.** Code's Case B is a single-response session (only one theme covered, and a "single response" / "this response" phrase) (`:159-170`) |
| Case C: synthesis → lowest-numbered, LLM pass "planned" | "Case 2": one theme → that theme; else the synthesis router (LLM); lowest-numbered only if the router is unavailable or fails (`:172-225`; `synthesis_router.py:120-179`) |
| Case D: fall-through | "Case 3": lowest-numbered, logged warning (`:227-233`, `:483-487`) |

Marker lists also differ:
- **Synthesis markers:** the code adds `"weave"` and `"synthesis"` (`:87-94`).
- **Refusal markers:** the code adds `"declines"`, `"not receiving"` and `"refusal of receiving"` (`:57-66`).
- **Order:** the refusal check runs **before** any case (`:458`).

> **Replacement for the algorithm block:**
> ```
> Refusal (checked first) — empty themes_covered, OR focus_decision contains a refusal
>   marker ("refused", "silence", "decline(s)", "not-receiving" / "not receiving",
>   "refusal-of-receiving" / "refusal of receiving") → refusals[]; no dossier
> Case A — lineage.primary_theme_id set by Step 2 → that theme (authoritative; all of Athens)
> Case A (legacy) — "response N" in focus_decision → Nth entry of the voice's briefings[]
>   (older artifacts only; briefings order may not match what the voice saw)
> Case B — one theme covered and a single-response phrase ("this response", …) → that theme
> Case 2 — synthesis marker ("synthesise", "synthesize", "synthesis", "weave", "across all"):
>   one theme covered → that theme; otherwise the synthesis router (one LLM call:
>   artifact + each candidate's title, abstract, formulation, cluster titles);
>   lowest-numbered theme only if the router fails or returns an unknown theme_id
> Case 3 — anything else → lowest-numbered theme in themes_covered; warning logged
> ```

**E4 — Sample note (483–489). CONFIRMED stale.** It cites the 2026-05-01 legitimacy test, which predates `primary_theme_id`. It also says "~25% land in Case C", but at Athens no voice reached the editor parser.

> **Replacement:** "At Athens (29 routed entries over three nights) every voice was routed by Step 2's `primary_theme_id`; the editor's own parser and router never ran. Five of those were synthesis voices, which Step 2 sent through the synthesis router."

**E5 — Routing manifest example (495–526). CONFIRMED.** Four differences from what `route_themes` writes (`routing.py:489-551`):
- **`voice_name`** is `"Voice of Plato"`: the `council_config` name via `voice_display_name`, with no leading "the" (`routing.py:396-411`). The example has `"the voice of Plato"`.
- **`primary_theme_source`** strings are the code's labels, e.g. `"Case A — Step 2 resolved primary_theme_id (authoritative)"`.
- **`dossier_lead_order_default`**: the manifest has this extra top-level key, a list of dossier numbers (`:548-550`). Because it is computed after numbering, it is always `[1..N]`. All three Athens files have it.
- **Refusals** carry `form` = the artifact's `selected_form`, or `"refusal"` if empty (`:462`).

Informational: the Athens **run-dir** `theme_routing.json` files still carry pre-C53 long identity lines in `voice_name` (e.g. "I am Augusta Ada King…"). C53's restamp covered published files, not run dirs. The spec example should show the current form.

> **Replacement example voice entry:** `{"voice_slug": "plato", "voice_name": "Voice of Plato", "primary_theme": "theme_001", "focus_decision_parsed": "Focus on Response 3.", "primary_theme_source": "Case A — Step 2 resolved primary_theme_id (authoritative)", "primary_dossier": 1}`; add `"dossier_lead_order_default": [1, 2, 3]` after `refusals`.

**E6 — "v2 changes vs v1" (530–534). CONFIRMED, minor.** It says `dossier_lead_order` was dropped from routing.json. The code writes `dossier_lead_order_default` (E5). Add one line saying so, and note that the lead pick lives in Stage 3 (`edition.py`).

**E7 — Operator override (536–538). CONFIRMED.**
The spec says the window between Stage 1's write and Stage 2's read is the review surface. There is no such window:
- Stage 2 uses the in-memory `routing` dict in the same process (`editor_flow.py:164-168, 187`).
- A hand edit only takes effect on a rerun with `--skip-routing` (`:154-163`).
- A rerun without that flag overwrites the edit.

Editing `voices_routing[].primary_theme` alone is also not enough:
- Stage 2 iterates `themes_to_dossiers` (`:187`) and picks voices by `primary_theme` (`:79-85`).
- So a voice moved to a theme that is not listed there silently drops out of every dossier.
- `n_engaged_voices` and `primary_dossier` are not recomputed.
- A rerun regenerates every dossier, which costs a full night's calls, unless `--single-dossier` is used.

> **Replacement:**
> "To change the routing: after a run, edit `05_editor/theme_routing.json` — `voices_routing[].primary_theme`, and add or remove the matching `themes_to_dossiers[]` entry (with `dossier_no`) if a theme gains or loses its only voice — then rerun with `--skip-routing`. Stage 2 generates one dossier per `themes_to_dossiers[]` entry, with the voices whose `primary_theme` matches; a voice pointed at an unlisted theme appears in no dossier. The rerun regenerates every dossier; use `--single-dossier <theme_id>` to redo one. Without `--skip-routing`, Stage 1 runs again and overwrites the edit."

**E8 — Stage 2 intro (550). CONFIRMED; outside the three flagged parts, found in passing.** "The call generates all dossier components as structured output" contradicts Principle 7 and §"Output Schema" (prose-and-parse, `dossier_generation.py:378-403`).

> **Replacement:** "…fires one Anthropic call, which returns every dossier component as labelled prose that the runtime parses (prose-and-parse, Principle 7)."

### 1.2 Cost figures (Overview 176; Stage 2 624–637 and 678–692; §"Cost & Envelope" 998–1015)

**E9 — Measured figures. CONFIRMED from the 13 published dossiers' `metadata`, priced by the scratch script.**

| Item | Spec | Measured at Athens |
|---|---|---|
| Cached system prompt | ~30K | 52,641 tokens on every call |
| Uncached user prompt (`input_tokens`) | ~15–25K | 8,105–36,677 (median 19,833) |
| Output, thinking included | ~3–5K | 5,906–24,401 (median 10,444); thinking 4,300–21,939 |
| Call that writes the cache | ~$0.45–0.50 | $0.77–1.21 (Nights 2–3, every call) |
| Call that reads the cache | ~$0.165–0.24 | $0.22–0.73 (Night 1, every call) |
| Night | ~$0.83 (3 dossiers) / ~$1.30 (5) | N1 $2.09 (5) · N2 $4.54 (5) · N3 $3.29 (3) |
| Athens total | ~$3–5 | **$9.93** for the published calls |

Caveats:
- **Night 1 is understated.** STATE records three editor fires that night; only the final calls survive in the published files. Night 1's five calls all read a cache that an earlier fire had written.
- **Future nights (estimate, PLAUSIBLE).** With C66's scheduling (one write, then reads), Night 2 would have cost ≈ $2.54 and Night 3 ≈ $2.29.
- **Where the cost goes.** Output was 70–83% of each call's cost when the call read the cache (Night 1). When every call wrote the cache (Nights 2–3), the write was 43–68% of the call.

> **Replacement for both per-call tables (626–637 and 682–692), one table only:**
> | Item | Tokens (Athens, 13 calls) | Cost at Opus 4.7 ($5/$25, 1h cache) |
> |---|---|---|
> | System prompt, cache write (first call of the night) | 52.6K | $0.53 |
> | System prompt, cache read (later calls) | 52.6K | $0.03 |
> | User prompt (theme record + K formulations + K artifacts + prior editions), uncached | 8–37K (median 20K) | $0.04–0.18 |
> | Output incl. summarized thinking | 6–24K (median 10K) | $0.15–0.61 |
> | **First call** | | **~$0.75–1.30** |
> | **Later calls** | | **~$0.22–0.80** |
>
> Measured nights (as published): Night 1 $2.09 (5 dossiers, all cache reads), Night 2 $4.54 and Night 3 $3.29 (every call wrote the cache, fixed since by C66). Athens total ≈ $10 for the published calls; Night 1's earlier fires are extra. With C66's one-write-then-reads scheduling, a 3–5-dossier night is ≈ $2.3–2.6 (estimate). Output tokens (thinking included) are the largest cost item once the cache is read. Prices come from the model in `model_routing.json` (step `runtime.editor.dossier`); re-derive if it changes.

**E10 — Overview envelope (176). CONFIRMED.**

> **Replacement for the first two sentences:**
> "**Per-night envelope (Athens, measured):** 3–5 dossiers, ≈ $2–4.5 per night as run; ≈ $2.3–2.6 with the C66 cache scheduling; Athens total ≈ $10. Output (with thinking) ran 6–24K tokens per dossier. See §"Stage 2" → "Cost per call"."

The same line says Night 3's 8m44s voice-to-editor interval reflects "slower theme routing". That is unsupported:
- Routing made no LLM call at Athens (E1).
- The editor's own `wall_clock_s` was 220.06 s on Night 2 and 212.1 s on Night 3 (`runs/athens_night_{2,3}/05_editor/manifest.json`).
- So the rest of each interval passed before the editor started. That was the review gate and operator releases, PLAUSIBLE per STATE's per-night notes.

> **Replacement for the "Measured" sentence:** "…Night 2 = 4m59s, Night 3 = 8m44s from voice manifest to editor manifest; the editor itself ran 220 s and 212 s (`05_editor/manifest.json` `wall_clock_s`), the rest being the wait for operator releases before it started. Since C66 the first dossier runs alone, so a night's editor wall is about one dossier call (1.5–5 min) plus the slowest of the rest."

**E11 — §"Cost & Envelope" (998–1015). CONFIRMED.** Five problems:
- **Stage 1 row.** "Deterministic, no API call, $0" is wrong: the fallback can call the synthesis router (`routing.py:178-219`). At Athens it made no calls.
- **Double count.** Line 1011's "Plus prefix-cache write penalty … ~$0.90" counts the write twice, since the first-call row already includes it.
- **Per-call wall.** "~60-90s" against a measured 91–298 s (median 151 s, as Principle 7 already says).
- **Serial fallback.** "Single-threaded fallback wall" is a mode that doesn't exist.
- **Output share.** "cost dominated by output tokens" held only once the cache was read (E9).

> **Replacement table:**
> | Stage | Calls/night | Per call | Per night (Athens) |
> |---|---|---|---|
> | Stage 1 routing | 0 at Athens; one small router call per synthesis voice only if Step 2 left `primary_theme_id` null | ≈ $0.05 (router docstring estimate) | $0 |
> | Stage 2, first call (writes cache) | 1 | $0.75–1.30 | — |
> | Stage 2, later calls (read cache) | 2–4 | $0.22–0.80 | — |
> | **Total** | 3–5 | | **≈ $2.3–2.6 with C66; $2.1–4.5 as run** |
>
> Wall: per call 91–298 s (median 151 s). Since C66 the first call runs alone, then the rest in parallel (`EDITOR_BATCH`, default 6): about one call plus the slowest of the rest, ≈ 3–9 min.

**E12 — Models + thinking, `max_tokens` (944). CONFIRMED.** The spec says "actual output ~3-5K". The ceiling is `EDITOR_MAX_TOKENS`, default 32000 (`dossier_generation.py:49`). Measured output reached 24,401 (N1/001), 76% of the ceiling, with thinking counted in output.

> **Replacement:** "**max_tokens:** 32,000 (`EDITOR_MAX_TOKENS`); measured output 6–24K including thinking (N1/001: 24,401, 76% of the ceiling). A five-voice dossier with long thinking could approach it; watch `stop_reason`."

(The model and thinking lines are model choice and were skipped per the brief.)

### 1.3 §"Implementation" → CLI (890–907) and Defensive checks (947–953)

**E13 — CLI. CONFIRMED against `editor_flow.py:321-356`.**
- **Missing flags:** `--bypass-gating` (`:332-336`) and `--project PATH` (`:337`).
- **`--night` restricted:** it accepts only 1, 2 or 3 (`:324`), and `assemble_system_prompt` raises for any other night (`card_assembly.py:308-309`). This is an event-agnostic limit; see §5, N4.
- **Relative run dir:** a relative `run_dir` resolves against PROJECT_ROOT (`:341`).
- **Exit codes:** 0 = success; 2 = at least one dossier failed; 3 = review gate blocked (`:352-356`).
- **Stale example run dir:** `athens_2026_2026_05_07_night1`. §"Multi-night convention" (v3.1) already says `athens_night_<N>`.
- **"All dossiers generate in parallel"** is stale since C66: the first dossier runs alone, then the rest up to `EDITOR_BATCH` (env, default 6) (`:252-264`).

> **Replacement:**
> ```bash
> python flows/editor_flow.py <run_dir> --night N [--skip-routing] [--single-dossier <theme_id>]
>                             [--no-prompt-cache] [--bypass-gating] [--project PATH]
> ```
> - `<run_dir>` — the night's run directory, e.g. `<PROJECT_ROOT>/runs/athens_night_1`; a relative path is taken from PROJECT_ROOT
> - `--night N` — 1, 2 or 3 only (argparse `choices`; the card assembly also refuses other nights); `assert_run_dir_night_matches()` checks it against the run_dir name
> - `--skip-routing` — use the existing `05_editor/theme_routing.json` (required after a hand edit, §"Stage 1" → "Operator override")
> - `--single-dossier <theme_id>` — regenerate one dossier; the edition index is still rebuilt from every dossier on disk
> - `--no-prompt-cache` — (unchanged text)
> - `--bypass-gating` — skip the per-voice review gate; tests and one-off forces only
> - `--project PATH` — PROJECT_ROOT override (else `AI_ASSEMBLY_PROJECT_ROOT`)
>
> Exit codes: 0 success · 2 one or more dossiers failed · 3 review gate blocked (`05_editor/gating_blocked.json` written).
> Athens production: `python flows/editor_flow.py <run_dir> --night N` (fired by the orchestrator, or by the dashboard when the last flagged voice is released or held). Stage 1 runs, then the first dossier alone, then the rest in parallel.

**E14 — Defensive checks. CONFIRMED.** One check exists, two don't:
- **Exists:** `assert_run_dir_night_matches` (`flows/shared/io.py:23-48`). It skips silently when the run_dir name carries no night.
- **Not implemented:** "Refuse to run if `04_voice/manifest.json` shows incomplete voice pipeline". `editor_flow.py` never reads the voice manifest.
  - What exists instead is the review gate (`routing.py:280-332`, called at `editor_flow.py:115-145`). It blocks while any voice that has a Step 2 artifact has neither a PASS verdict nor an operator decision.
  - A voice whose Step 2 never ran is invisible to the gate.
  - The wait for `04_voice/manifest.json` is the orchestrator's (`scripts/overnight_orchestrator.py:383, 464`).
- **Not implemented:** "fails schema validation". `load_editor_card` checks that the file exists and parses its JSON; nothing more (`card_assembly.py:116-133`).

Unlisted behaviour:
- A missing `council_config.json` or `conference_facts.json` silently drops the deployment block (THE GATHERING / YOUR ROLE / THE PANEL) from Tim's prompt (`card_assembly.py:195-217, 256-257`).
- `--skip-routing` without the file, and an unknown `--single-dossier`, both exit (`editor_flow.py:156-160, 190-195`).

> **Replacement list:**
> - `assert_run_dir_night_matches(run_dir, night)` — refuses a `--night` that contradicts the run_dir name; run_dirs without a night in the name are not checked
> - Per-voice review gate (Stage 0, `routing.py::gating_status`) — refuses to run while any voice with a Step 2 artifact has neither a PASS verdict nor an operator decision; writes `05_editor/gating_blocked.json`, exit 3. It does not check that every voice produced a Step 2 artifact — the orchestrator's wait for `04_voice/manifest.json` covers that when the editor is fired by the orchestrator.
> - Tim's card missing → `FileNotFoundError` (no schema check)
> - `council_config.json` / `conference_facts.json` missing → the deployment block is left out of the system prompt without a warning
> - `--skip-routing` with no `theme_routing.json`, or `--single-dossier` naming an unrouted theme → exit with a message

**E15 — System prompt assembly (936). CONFIRMED.** The spec says the breakpoint lets calls share the prefix "even when their step-specific tails differ slightly (per-dossier `theme` injection)". The tail is identical for every call of a night: the per-dossier material is in the user prompt (`card_assembly.py:23-26, 353-367`). Both blocks carry a 1h breakpoint (the spec's own line 556). The deployment block sits in the prefix after BOUNDARIES (`:340-351`).

> **Replacement for that sentence:** "The prefix (IDENTITY, CONSTITUTION, BOUNDARIES, then the deployment block) and the tail (the other sections plus the closing prompt) are both identical for every dossier call of a night, and both carry a 1h cache breakpoint; the per-dossier theme and voices travel in the user prompt."

**E16 — Open Questions (1032–1047). CONFIRMED.**
- **Heading:** "(v2 — pending operator decisions before first build)" is stale. The pipeline shipped.
- **Q1 notes:** "TODO … ~30 min implementation" should say shipped: `641e31d`, `synthesis_router.py`, called from Voice Step 2 and as the Stage 1 fallback.
- **Q7:** "orchestrator polls `04_voice/manifest.json` and fires editor as soon as voice pipeline completes". The orchestrator fires it only after that manifest exists **and** its own validation gate clears (`overnight_orchestrator.py:482-513`).
- **Q7, second trigger:** the dashboard also fires the editor. It does so when the operator's release or hold clears the editor's gate and no `05_editor/manifest.json` exists yet (`runtime/ingest/app.py:872-900`, `_maybe_auto_fire_editor`).

> **Replacement for Q7's decision cell:** "✅ **Auto, two triggers:** the orchestrator fires the editor after `04_voice/manifest.json` exists and every WARN/HOLD voice has an operator decision; the dashboard fires it when a release/hold clears the editor's gate and the editor has not yet run (lockfile-guarded)."

Also stale in code comments, not the spec (no edit asked; noted for whoever fixes the spec):
- `editor_flow.py:6-8` says "Cases A/B/C/D".
- `routing.py:23-38` says "purely deterministic — no LLM call".
- `dossier_generation.py:6-12, 23-26` still names "Claudia" and says the prompt is "v1-shaped".
- `editor_flow.py:35-36` has the old "$3-5" cost line.

---

## 2. `docs/AI_Assembly_Frame_Concept_v1.md`

**Outcome:** the body is still an accurate record of the pre-Athens *intent*, but three of its five surfaces did not ship as described, and the doc never says so.
- **Superseded:** the broadsheet (replaced by the Editor Pipeline's dossiers).
- **Dropped:** the Substack (runtime OPEN_ITEMS B4, closed 2026-05-04).
- **Not built in this repo:** the closing show and the Day 4 goodbye (B5, B6 🔴).
- **Pointing at nothing:** its "new documents" list; none of them exists.

The tracker already records each of these decisions (B2–B9). The fix is a status block plus short inline notes, not a rewrite. What the code can settle is below; the reception analysis and the closing-show design have no code to check against.

**F1 — Surface 2, the newspaper (93–105). CONFIRMED against the Editor Pipeline and the tracker.**

| Frame Concept | What shipped |
|---|---|
| One broadsheet front page per night, "one of eleven artifacts" | 3–5 per-theme dossiers per night (`editor_flow.py`; 13 across Athens). The night's lead is picked by Stage 3 (`editor/edition.py`, B3 narrowed to a lead picker). |
| A fictional organisation ("Assembly News"; "no such organisation exists") | Dossiers are published under the House of Beautiful Business, a real organisation, with Tim Leberecht as "the unnamed editor" (`runtime/flows/shared/prompts/editor_dossier.md:27`) |
| Masthead "Vol. CXIV. No. 39,288" with an incrementing issue number (51, 69, 95, 99) | No masthead, volume or issue number; dropped 2026-05-05 (`641e31d`; Editor spec §"The Publication") |
| Per-voice headlines with "headline poetics" (61, 103, 230) | One `kicker` + `headline` per dossier, by Tim. The per-voice torque survives only in each headnote's `artifact_title`, via Tim's card field `translation_protocol` (B9: per-voice broadsheet headline dropped 2026-05-04 PM). No headline-poetics field exists in any persona schema (repo search: no match). |
| Wire-service unavailability paragraph and strikethrough, at most once each per edition (105) | Neither exists: no such field, and no strikethrough in the closing prompt or any published dossier (Editor spec §"The Publication") |
| "The paper points; the artifact is the destination" (97) | Dossiers **embed** each artifact verbatim (`headnotes[].artifact_text`, since `8b84e58`) |

**F2 — The Edition Pipeline (228, 315). CONFIRMED.** The spec describes "a new pipeline pass running after Step 3 … two lead stories, eight brief mentions, ten voice-specific headlines". This was never built. Its place is taken by the Editor Pipeline (Stages 1–3). Step 3 itself was skipped for Athens (A1). No "brief mentions" exist: the In Brief column was dropped (Editor spec v3.1).

**F3 — Surface 3, the HoBB Substack (107–119; move Six, 59; decision at 250). CONFIRMED dropped.** B4 was closed 2026-05-04: "Substack bridge dropped, micro-site only". The real-voice HoBB bridge now lives *inside* the dossier. Tim writes it as HoBB's unnamed editor, so the fiction/bridge split this section argues for no longer exists in the shipped form.

**F4 — Surface 1, the micro-site (85–91, 232). PLAUSIBLE; built outside this repo, so not checkable.**
- The repo contains no micro-site (B2 🔴 "designed elsewhere").
- Its contract is `published_artifacts/`: per-voice pages at `nights/night_<N>/<slug>.json` and dossiers at `dossiers/night_<N>/`.
- "Marley's song plays" and "the Octopus's chromatophore shader runs in the browser" depend on B7. That item is ⚠️ partial: the Octopus WebGL component exists at `runtime/assets/octopus_chromatophore/`; Step 2 does not extract the display JSON; no Marley audio path exists.
- Artifact URLs (`/night-1/plato`) and the `thessembly.org` domain (97, 115) can't be verified. The domain is an open decision in `AI_Assembly_Infrastructure.md`.

**F5 — Closing show and matrices (123–162, 184–194, 234–236), and the Day 4 goodbye (166–172, 240). CONFIRMED not built here.** B5 (closing-show pipelines, including the Matrix A/B mapping) and B6 are 🔴 unbuilt. No matrix or closing-show code exists under `runtime/` (repo search). Whether a closing show ran at Athens can't be told from the code; STATE records only the Night 3 "closing edition" of dossiers.

**F6 — Panel (9, 251). CONFIRMED correct:** ten voices, with Thiel and Tang dropped.

**F7 — Related documents (299–320). CONFIRMED.**
- `AI_Assembly_Persona_Pipeline_v3_10.md` is archived (`docs/_archive/`); v4 is current.
- "Voice Pipeline — Steps 1 and 2 (Step 3 pending)": Steps 1–3 are built, and Step 3 was skipped for Athens.
- The Editor Pipeline, the doc that operationalises this frame, is missing from the list.
- `Till_Briefing_The_AIssembly_Athens_2026_v3_1.md` is not in the repo (`git ls-files`: no match).
- **None of the seven "new documents this concept implies" exists.** runtime OPEN_ITEMS E5 still lists them as needed "when B1 lands", which has happened. E5 should be re-scoped: the Broadsheet, Edition-Pipeline, Headline-Poetics and Substack docs are moot per B3, B4 and B9.

**F8 — docs/README's FU#61 note ("the strip rule needs to be voice-register-conditional").** This refers to the micro-site's stripped artifact pages (89). It is a design follow-up, not a code discrepancy; left as is.

> **Proposed status block, inserted after the title (no body rewrite):**
> **Status (2026-09-28):** pre-Athens concept, kept as the record of intent. What shipped differs: the broadsheet became the Editor Pipeline's per-theme dossiers, published under the House of Beautiful Business with Tim Leberecht as unnamed editor — no masthead, issue numbers, wire-service paragraph or strikethrough, and artifacts embedded rather than pointed at (`AI_Assembly_Editor_Pipeline.md`); the Substack was dropped (runtime OPEN_ITEMS B4); per-voice headline poetics survive only as each headnote's `artifact_title` (B9); the closing-show pipelines and the Day 4 goodbye were not built in this repo (B5, B6); the micro-site is built outside this repo (B2). The "new documents" listed at the end were not written.
>
> **Inline notes:** at §"Surface 2" and §"Production implications" → "Broadsheet mini-concept + Edition Pipeline" — *"Superseded: see the Editor Pipeline spec and B3/B9."* At §"Surface 3" — *"Dropped 2026-05-04 (B4)."* In "Related documents" — update the persona pipeline to v4, the Voice line to "Steps 1–3 (Step 3 skipped for Athens)", add `AI_Assembly_Editor_Pipeline.md`, and mark `Till_Briefing…` as not in the repo.

## 3. `docs/AI_Assembly_Transcription_Pipeline.md` §7 (reflection handling)

The spec has no numbered §7 today. Its v2.2 changelog uses "§7 Step 1 ingest" for the reflection-recording text in **Step 1: Ingest** (lines 84–270). That text is spread over the Overview, Step 1, Step 1 Output, Step 4 and Constraints. The v2.2 changelog (10–33) describes the vendor route, but two of its claims are wrong.

**What happens now. CONFIRMED in code and on the five Athens reflection sessions (N1 ×3, N2 ×1, N3 ×1).**
- **How sessions are marked.** Reflection sessions have `audio_source: "vendor"` in `reference/sessions.json`. The upload form refuses them (`runtime/ingest/app.py:247-256, 513-518`).
- **Step 1, the preprocessor (operator-run).** `runtime/scripts/reflections_to_session_package.py <vendor.json> [--session-id <our id>] [--project-root PATH] [--out PATH]` converts the vendor's `Reflection Import Format` into a `session_package.json` (`:91-172, 175-209`).
  - Each `reflections[i]` becomes one turn, with speaker `Participant {i+1}`, role `audience` and confidence `high`.
  - `language` is kept, and so are `_vendor_participant_id` and `_vendor_duration_seconds`.
  - `review_queue` is an empty stub.
  - All five Athens packages carry `_vendor_internal_session_id`, so the vendor sent its own UUIDs and `--session-id` was used every time.
- **Step 2, the intake (operator-run).** `runtime/flows/vendor_intake.py` validates the package. It is run either on one file (`<file> --run-dir <run_dir> --session-id <id>`) or as a sweep over `<PROJECT_ROOT>/vendor_inbox/<session_id>.json` for a night (`--night N --sweep`) (`vendor_intake.py:30-69`). It writes `session_package.json`, `status.json` (`state: done`, `source: vendor`), `vendor.flag`, and `vendor.warnings` or `vendor.error` under `01_transcription/<session_id>/`. All five Athens sessions have `vendor.warnings`.
- **What is skipped.** Everything in Transcription Steps 1–5: no audio, no ASR, no speaker ID, no cleaning. The orchestrator counts the session as done.

**T1 — v2.2 changelog line 14. CONFIRMED.** "The integration point is between Stage 0 and Stage 1" is wrong. The vendor route replaces the whole pipeline and lands at its **output** boundary: the same files Step 5 writes.

**T2 — v2.2 line 25 and line 31. CONFIRMED. Cross-reference C68 A1; not re-reported.**
- **Line 25** says title, description and contributor roster are merged from `sessions.json`. The script copies only `title` (under that key, not `session_title`), `day`, `venue`, the times, `ai_assembly` and `audio_source` (`:80-87`). Those are exactly the metadata keys on all five Athens packages. No description, format, track or roster reaches the package.
- **Line 31** says "downstream Researcher contract met". It isn't: see C68 A1.
- **New evidence for A1:** the audio path does the right translation in `ingest/sessions.py::build_session_json` (`:201-225`: `title→session_title`, `description→session_description`, `session_format`, `track`, roster from `speakers.json`). The preprocessor can reuse it.

**T3 — The reflection-recording text is wrong throughout. CONFIRMED.**
- Overview lines 68 and 70 ("participant reflection recordings").
- The storage tree (101–102).
- The filename convention (157–159) and the per-session workflow (167–168).
- The trigger steps (178, 181).
- Step 1 Output `recording_id` / `recording_type` / `expected_speaker_count` "for reflections" (252, 265, 267).
- Step 4's reflection prompt context (changelog line 29).
- Constraints line 531: "Reflections are first-class … same schema, same processing".

No reflection audio file was ever processed, and no code parses `__reflection__` filenames. (PLAUSIBLE: not searched repo-wide beyond `runtime/ingest` and `runtime/flows`.)

**T4 — Step 1 Storage and Trigger (88–114, 163–185) are also wrong for audio. CONFIRMED. Outside the brief's reflection scope, but it changes the trust rating.**
- The spec describes a Google Drive folder mounted with rclone, a `watchdog` file watcher, `/transcripts/dayN/` and `/review/dayN/`, and it cites the archived `Infrastructure_Setup.md`.
- The code has a FastAPI upload form. It writes `<run_dir>/01_transcription/<session_id>/`, then ffmpeg normalizes to `audio.m4a`, then `state=normalized`, then the orchestrator dispatches (§4, L2).
- The Lifecycle spec and `AI_Assembly_Infrastructure.md` describe the real path.

**What the reflection text should say now.** Replace lines 157–159 and the reflection parts of 101–102, 167–168, 178 and 181 with one subsection under Step 1:

> ### Reflections (vendor-transcribed JSON)
> Participant reflections do not come in as audio. A vendor collects them and delivers one JSON file per session in the operator's `Reflection Import Format` (`source`, `session_id`, `collected_at`, `reflections[]` of `{participant_id, duration_seconds, text, language?}`). Such sessions are marked `audio_source: "vendor"` in `reference/sessions.json`; the upload form refuses them.
>
> The operator lands each one in two steps, and the session then skips Steps 1–5 entirely:
> 1. `python runtime/scripts/reflections_to_session_package.py <vendor.json> --session-id <session_id> --project-root <PROJECT_ROOT> --out <PROJECT_ROOT>/vendor_inbox/<session_id>.json` — one turn per reflection (`speaker` "Participant {i+1}", `role` audience, `confidence` high, text verbatim; `language` and the vendor's participant id and duration kept as `_vendor_*` fields), session metadata merged from `reference/sessions.json`. Use `--session-id` whenever the vendor sends its own id (every Athens file did); the vendor's id is kept as `_vendor_internal_session_id`.
> 2. `python runtime/flows/vendor_intake.py --night N --sweep` (or `<file> --run-dir <run_dir> --session-id <id>` for one file) — validates the package and writes `session_package.json`, `status.json` (`done`, `source: vendor`) and `vendor.flag` / `vendor.warnings` / `vendor.error` under `01_transcription/<session_id>/`. From there the orchestrator and the Researcher treat it exactly like a transcribed audio session.
>
> **Known gap (runtime OPEN_ITEMS C68 A1):** the preprocessor writes `title` rather than `session_title`, and no description, format, track or roster, so the Researcher sees reflection sessions with a blank title and description and format "panel". Until A1 is fixed, the metadata contract of Step 5 does not hold for reflections.

Alongside:
- **Line 68:** "…and, in some cases, participant reflections delivered as vendor-transcribed JSON (§"Reflections")".
- **Line 70:** "recordings (audio or video files) delivered after the session ends; reflections arrive separately as JSON".
- **Remove:** the `__reflection__` rows in Step 1 Output (252, 265, 267) and the storage tree (101–102). Keep `recording_type` only if the Cleaning prompt still branches on it; not checked.
- **Line 531:** "Reflections are first-class inputs: they may be a session's only record, and they reach the Researcher in the same session-package schema — but by the vendor route, not through ASR."
- **v2.2 changelog lines 14, 25 and 31:** correct per T1 and T2.
- **Step 1 Storage and Trigger (T4):** replace with a short pointer. "Audio arrives through the ingest upload form, is normalized by ingest, and is dispatched by the overnight orchestrator — see `AI_Assembly_Runtime_Lifecycle.md` Stages 1–2."

---

## 4. `docs/AI_Assembly_Runtime_Lifecycle.md` (beyond the Stage 6 section)

The Stage 6 section (lines 134–152) was fixed on 2026-09-28 and is not re-checked here.

**L1 — Status line (5). CONFIRMED.** "v1 — 2026-05-02". The document has since had partial edits (Stage 6, §8 editor timing).

> **Replacement:** "**Status:** v1.1 — 2026-09-28 (checked against `runtime/scripts/overnight_orchestrator.py` and `runtime/ingest/pipeline.py`); v1 2026-05-02."

**L2 — Who fires transcription (§1 line 39, the diagram 16–20, Stage 2 lines 66–79, §3 line 185). CONFIRMED.**

The spec says ingest spawns normalize and transcribe at upload, via `_launch_stage0`. Since C26 (2026-05-04) this has changed:
- **Ingest only normalizes.** It sets `received`, then `normalizing`, then `normalized`, and stops (`runtime/ingest/pipeline.py:8, 54-59, 422-445`). No `_launch_stage0` exists in `pipeline.py`.
- **The orchestrator dispatches transcription.** Its Stage 0 runs each poll: it finds `normalized` sessions and calls `fire_transcription` for up to `ORCHESTRATOR_TRANSCRIPTION_CONCURRENCY` in flight (default 4) (`overnight_orchestrator.py:86-88, 120-192, 398-404`).
- **Transcribing has sub-states:** `transcribing_asr`, `_speaker_id`, `_cleaning` and `_finalizing`, derived from the log (`pipeline.py:72-75, 165-220`).
- **Consequence:** without the orchestrator running, uploads stop at `normalized`.

> **Replacement for line 39:** "**Start trigger:** the first audio file lands at the ingest endpoint. Ingest normalizes it (ffmpeg) and sets `state="normalized"`; the orchestrator, polling every minute, dispatches transcription for normalized sessions, up to 4 at a time (`ORCHESTRATOR_TRANSCRIPTION_CONCURRENCY`). Without the orchestrator running, uploads stop at `normalized`."
>
> **Replacement for Stage 2's trigger / states / fired-by:**
> - **Trigger:** the session is `normalized` and fewer than 4 transcriptions are in flight; dispatched by the orchestrator's Stage 0 (`overnight_orchestrator.py::fire_pending_transcriptions` → `ingest/pipeline.py::fire_transcription`). Vendor sessions (reflection JSON) skip this: `vendor_intake.py` writes `session_package.json` and `state="done"` directly.
> - **States:** `received` → `normalizing` → `normalized` (ingest) → `transcribing` (sub-states `transcribing_asr` / `_speaker_id` / `_cleaning` / `_finalizing`) → `done` ★ or `error`.
>
> **§3 "Stages it does NOT fire":** remove "Per-session transcription"; add "Audio normalization (ingest, at upload)". **"Stages it does fire":** prepend "Transcription dispatch (Stage 0)".

**L3 — Researcher trigger (83). CONFIRMED, minor.** "Done" is read through `infer_state` (C54), not raw `status.json` (`overnight_orchestrator.py:195-256`). Under `infer_state`:
- a session counts as done once `session_package.json` exists;
- a `transcribing` session whose PID died counts as an error, which halts the orchestrator.

> **Add to the trigger:** "(state as read by `ingest/pipeline.py::infer_state`, the same view as the dashboard: a session with `session_package.json` counts as done even if `status.json` lags; a `transcribing` session whose process died counts as an error)."

**L4 — Missing: the orchestrator's validation gate, and the operator's role (§1 line 45; §2; §3). CONFIRMED.**
- After Voice, the orchestrator halts in state `awaiting_validation_clearance` while any voice has `overall_verdict` WARN or HOLD without an `operator_decisions/<slug>.json` (`overnight_orchestrator.py:259-300, 482-500`).
- The operator clears it from the dashboard.
- Every Athens night needed this: N1 had 6 WARN, N2 8 WARN, N3 7 WARN + 1 HOLD (STATE).
- So "Operator's role during the night: none, by design" is wrong. §2 has no step for the gate.

> **Replacement for line 45:** "**Operator's role during the night:** one review step. After Voice, the orchestrator halts (`awaiting_validation_clearance`) until every voice the Step 2 validator marked WARN or HOLD has an operator decision (release or hold for regeneration), made on the dashboard's voice page. At Athens every night needed it. Otherwise the orchestrator runs unattended and halts on a stage failure, with logs at `<run_dir>/_orchestrator_logs/`."
>
> **New stage between 5 and 6:** "**Stage 5.5 — Operator review gate (C28b).** Trigger: `04_voice/manifest.json` exists. Reads `04_voice/step2_validation/<slug>.json` (`overall_verdict`) and `04_voice/operator_decisions/<slug>.json`. Holds the pipeline while any WARN/HOLD voice has no decision; no `step2_validation/` directory means the gate is open. Cleared by the operator on `/admin/tonight/voice`; the dashboard may fire the editor itself once its gate clears (`ingest/app.py::_maybe_auto_fire_editor`)." — see also §5 N1: the two gates don't agree.

**L5 — Stage 5 Voice (113–132). CONFIRMED for the orchestrator's flags.**
- **Flags:** the orchestrator passes only `--skip-step3` (`overnight_orchestrator.py:465-470`). Its comment says Step-1 validation is off by default since C28 and `--skip-validation` is redundant.
- **Stale:** the "Night 1 only per FU#62" note on `validation/` (line 122) and the `[--skip-validation]` in line 130.
- **Missing:** the writes list has no `04_voice/step2_validation/<slug>.json` (the C28b validator). `operator_decisions/` is written by the dashboard, not by Voice.

> **Replacement fired-by:** "orchestrator runs `python runtime/flows/voice_flow.py <run_dir> --night N --skip-step3` (Step-1 validation is off by default since C28; the Step 2 validator runs and writes `04_voice/step2_validation/<slug>.json`)."

**L6 — Publish done-detection and the night's end state (§1 line 41; Stage 7 line 167; §3 line 219). CONFIRMED in the orchestrator.**
- The orchestrator treats publish as done when `published_artifacts/traces/publish_manifest_night_<N>.json` exists (`overnight_orchestrator.py:385-393`).
- Its comment gives the reason: `nights/night_<N>/_index.json` is now written at the end of `voice_flow` itself (post-C32). Using it as the signal skipped the editor and publish in a dry run.
- So `nights/.../_index.json` existing does not mean the night is published. The operational query at line 219 would report "publish done" right after Voice. (The claim that `voice_flow` writes it comes from that comment; not re-read in `voice_flow.py`.)

> **Replacement for line 41:** "**End state:** `<PROJECT_ROOT>/published_artifacts/traces/publish_manifest_night_<N>.json` exists (Publish's own run record; the orchestrator's sentinel). `nights/night_<N>/_index.json` is not a completion signal: Voice writes a first version of it before the editor runs."
> Stage 7 done detection and the §3 query: use the same file.

**L7 — §4 filesystem layout (227–312). CONFIRMED against the code paths cited.**
- **`05_editor/`** is missing `theme_routing.json` and `gating_blocked.json` (written only when blocked), plus `.editor_running.lock` and `auto_fire.log` from dashboard auto-fire (`app.py:889, 916`). `dossier_<NN>` should be `dossier_<NNN>`.
- **`04_voice/`** is missing `step2_validation/` and `operator_decisions/`.
- **`published_artifacts/`** is missing `dossiers/` (`night_<N>/dossier_<NNN>.json`, `night_<N>/_index.json`, root `_index.json`) and `traces/publish_manifest_night_<N>.json` as the sentinel.
- **Also wrong:** the location of `council_config.json` (listed under `reference/`; see L10) and the continuity file names (see L11).

**L8 — §5 cross-night threading (324–334). CONFIRMED.**
- **Self-contradiction:** "no artifact written under one night's run_dir is ever read by another night's pipeline" contradicts item 2. Provocateur reads earlier run dirs' `03_provocateur/selection.json`, and the orchestrator passes those dirs (`overnight_orchestrator.py:443-451`).
- **A fourth thread is missing:** the editor reads every earlier night's published dossiers as `prior_editions` (`editor/publish.py:61-99`).

> **Replacement for the closing sentence:** "Apart from these, each `runs/athens_night_<N>/` tree is self-contained: the only cross-night reads are prior run dirs' `03_provocateur/selection.json` (item 2), the continuity overlays under `voices/` (item 1), and the published dossiers under `published_artifacts/dossiers/` (item 4)."
> **Add item 4:** "**Editor prior editions.** On Nights 2–3 the editor reads the kicker, headline and body of every dossier published on earlier nights (`published_artifacts/dossiers/night_<M>/`, M < N) as `prior_editions`."

**L9 — §8 Athens specifics (401–452). CONFIRMED against STATE and docs/README.**
- **VM commands (412–424).** The VM was never provisioned (`docs/README.md:20`; B10), and the operator ran from a laptop. From Night 2 on, stages were fired by hand, not by the orchestrator (`STATE.md:163-166`).
- **Voice timing, "2–4 hr" (434).** STATE records Night 1's full 10-voice Voice fire as 12:00–12:26.
- **The 2026-09-28 editor timing note (439).** It repeats "slower theme routing" for Night 3 (see E10). The editor itself ran 220 s and 212 s.
- **Editor cost, "$1–2" per night (449).** Measured $2.09–4.54 as run (E9).

> **Replacement for "Operator commands per night":** "Athens ran from the operator's laptop; the VM (`orchestrator@<N>.service`) was specified but never provisioned (B10). Night 1 used the orchestrator (`python runtime/scripts/overnight_orchestrator.py --night 1`); Nights 2–3 were fired stage by stage (§7), and the orchestrator was not started alongside, since it would dispatch duplicate transcriptions."
> **Editor note:** replace "slower theme routing that night" with "most of it waiting for operator releases; the editor itself ran 212 s".
> **Editor cost row:** "$2–4.5 as run at Athens; ≈ $2.5 with the C66 cache fix". The other stages' timing and cost rows: see L10.

**L10 — Where `council_config.json` lives (Stage 4 line 99; §4 line 236). CONFIRMED.** Both say `reference/council_config.json`. It is at the project root:
- `load_council_config` defaults to `$PROJECT_ROOT/council_config.json` (`flows/shared/io.py:264-282`);
- athens-2026 has `council_config.json` at its root, next to `conference_facts.json`, `panel_roster.json` and `audience_profile.json`.

Line 100 also says Provocateur reads each voice's `06_derive/01_provocateur_profile.json`. At runtime it reads the profiles as wired into `council_config.json` `members[]` (CLAUDE.md "Cross-repo handoff"). PLAUSIBLE: not traced in `provocateur_flow.py`.

> **Stage 4 reads:** replace lines 99–100 with "`<PROJECT_ROOT>/council_config.json` — panel members, including each voice's Provocateur profile (wired in from `voices/<slug>/06_derive/01_provocateur_profile.json` at build time)".
> **§4 layout:** move `council_config.json` to the root, and add `conference_facts.json`, `panel_roster.json` and `audience_profile.json` beside it.

**L11 — Continuity file naming (Stage 5 line 119; §4 lines 243–245). CONFIRMED.**
- Voice on Night N **reads** `continuity_night_<N>.json` (`voice/card_assembly.py:170, 192`).
- Voice **writes** `continuity_night_<N+1>.json` (`voice/continuity.py:133, 140`).
- Line 119's `continuity_night_<N-1>` is wrong. The §4 comments ("`continuity_night_1.json` — written by Voice after Night 1", and so on) are off by one.
- athens-2026 `voices/plato/` has only `continuity_night_2.json` and `continuity_night_3.json`.
- (What Night 3's continuity summarises is C68 A10; not re-reported.)

> **Line 119:** "For Night 2/3: `<PROJECT_ROOT>/voices/<slug>/continuity_night_<N>.json` — written at the end of Night N-1". **§4:** "`continuity_night_2.json` — written by Voice after Night 1, read on Night 2" and "`continuity_night_3.json` — written after Night 2, read on Night 3"; drop `continuity_night_1.json`.

**L12 — The systemd unit would retry failed stages, contrary to §3 and §6. CONFIRMED by reading the unit. The runtime behaviour follows from documented systemd semantics; not run.**
- **What §3 says:** the orchestrator "stops at the failure of any stage rather than retrying". §6 says systemd restarts it only after a crash.
- **What the unit has:** `Restart=on-failure` with `RestartSec=30` (`runtime/scripts/deploy/orchestrator@.service:43-44`).
- **Why that conflicts:** in systemd, `on-failure` also restarts after a **non-zero exit code**. The unit's own comment (`:22-25`) says the opposite: that exits 1 and 2 leave it stopped.
- **Consequence:** a failed stage (exit 1) or a missed deadline (exit 2) restarts the orchestrator every 30 s. Each restart re-fires the failed stage, because its sentinel is still missing. With 30 s between restarts, the default start-rate limit (5 starts in 10 s) never trips.
- **Impact today:** nothing. The VM was never provisioned (B10). See §5, N5.

> **§6 "Orchestrator script crashes" row:** "systemd restarts it after a crash. The unit must not restart it after a stage failure (exit 1) or the deadline (exit 2) — see runtime OPEN_ITEMS (to file: `RestartPreventExitStatus=1 2`)." Until that lands, the §3 sentence "stops at the failure of any stage" holds on a laptop, not under the shipped unit.

**L13 — §7 manual runs (362–397). CONFIRMED.**
- **`--project`:** "All flows take … a `--project` that resolves PROJECT_ROOT" is wrong for two flows. `researcher_flow.py` and `provocateur_flow.py` define no `--project` argument (repo search: no match). `voice_flow.py`, `editor_flow.py` and `publish_flow.py` do.
- **Stale flag:** `voice_flow`'s `--skip-validation` "for Night 2/3" is a deprecated no-op (`voice_flow.py:700-704`).
- **Editor idempotence:** "individually idempotent — each has internal checkpointing" does not hold for the editor. A rerun regenerates every dossier; no dossier is skipped because it exists (`editor_flow.py:187-264`). Only `--single-dossier` narrows it.
- **Orchestrator won't re-fire:** once `05_editor/manifest.json` exists, the orchestrator never re-fires the editor.
- **Missing pointer:** `runtime/scripts/reset_run.py`, which exists for these resets and whose caveats are C68 A2 / A8.

> **Replacement for the comment block:** "Every flow takes the run_dir as its first argument. `voice_flow`, `editor_flow` and `publish_flow` also take `--project`; `researcher_flow` and `provocateur_flow` resolve PROJECT_ROOT from `AI_ASSEMBLY_PROJECT_ROOT`. Researcher, Provocateur and Voice checkpoint their work, so a rerun resumes. The editor does not: a rerun regenerates every dossier (use `--single-dossier <theme_id>` for one) and pays for each call."
> Drop `[--skip-validation]` from the Voice line. Add: "To reset a stage and everything after it, see `runtime/scripts/reset_run.py` (read its caveats in runtime OPEN_ITEMS C68 A2 and A8 first)."

**L14 — §8 tables. CONFIRMED where stated.**
- **Session counts (403–410).** 10 / 9 / 6 = 25 is the 2026-05-01 CSV count (runtime OPEN_ITEMS "Recently landed"). `reference/sessions.json` now has 32 `ai_assembly` sessions: 12 / 12 / 8, including 5 vendor sessions (3 / 1 / 1) and the hand-added `__audio*` duplicates (C68 A9). STATE's landed counts are 12 sessions (N1); 7 sessions from 9 audio files (N2); 6 sessions from 7 audio files (N3).
- **Voice wall "2–4 hr" (434).** The Voice spec (§"Cost & Envelope", measured 2026-09-28) says a night's total isn't recoverable. Its per-call medians and STATE's Night 1 full fire (12:00–12:26) put the main pass at under an hour.
- **Voice cost "$15–30" (448).** Consistent with the measured ~$23–25 per night.
- **Editor rows.** See L9 and E9.
- **Researcher "$5–15" (447).** The Researcher spec's own estimate is $15–25 (`AI_Assembly_Researcher_Pipeline.md:638`). No measured figure exists; the two specs disagree.

> **Session table:** replace the counts with the landed counts from STATE and a note: "(`sessions.json` now also lists hand-added `__audio2` duplicates for double-captured sessions and 5 vendor reflection sessions; 32 `ai_assembly` entries.)"
> **Timing row, Voice:** "~30–60 min for a clean 10-voice pass (Night 1: 26 min); per-call medians in the Voice spec". **Cost rows:** Voice "~$23–25 (measured)", Editor "$2–4.5 as run; ≈ $2.5 with C66", Researcher "estimate; the Researcher spec says $15–25".

**L15 — Test counts (§6 line 347; §9 line 467). CONFIRMED correct:** 9 tests in `test_run_dir_night_check.py` and 22 in `test_orchestrator.py`. The design doc link (`_workspace/archive/specs/AUTOMATION_ORCHESTRATOR_DESIGN_2026_05_02.md`) resolves.

---

## 5. Code issues found in passing (not spec text)

**Tracker check:** I searched runtime and voices OPEN_ITEMS, the doc backlog, the roadmap, and both 2026-09-28 review reports. None of N1, N2, N3 or N5 is filed. N4 probably falls under C52. The main session decides whether to file them; nothing was filed from here.

- **N1 — The orchestrator's gate and the editor's gate disagree (CONFIRMED by reading; not run).**
  - The orchestrator's gate opens when no WARN/HOLD voice lacks a decision. It is fully open when `step2_validation/` doesn't exist (`overnight_orchestrator.py:270-277, 286-295`).
  - The editor's gate needs every voice with a Step 2 artifact to have a PASS verdict or a decision (`routing.py:315-331`).
  - **Failure case:** `voice_flow.py --skip-step2-validation` (`voice_flow.py:711-712`) leaves no validation files. The orchestrator then fires the editor, the editor exits 3 (every voice pending), and the orchestrator reports `failed:editor` and halts. The same happens if one voice's validation file is missing (PLAUSIBLE: not checked whether the validator writes a file when it fails).
  - **Not a problem:** the validator emits only PASS / WARN / HOLD (`step2_validation.py:357-376`), so the FAIL that `routing.py:260` documents never occurs. That docstring is stale.
  - **Fix direction:** one shared gate function, used by both.
- **N2 — The refusal check is a substring match that runs before everything else (CONFIRMED by reading).**
  - `_is_refusal` flags any `focus_decision` containing "silence" or "decline", e.g. "Focus on Response 2, where the room's silence…" (`routing.py:69-75, 458`).
  - A flagged voice is dropped from every dossier, even though `primary_theme_id` is set.
  - At Athens no `focus_decision` tripped it: `refusals[]` was empty all three nights.
- **N3 — `council_config` / `conference_facts` for Tim's prompt ignore `--project`.** `load_council_config()` and `load_conference_facts()` resolve PROJECT_ROOT from the environment (`io.py:379-381`). A failure is swallowed (`card_assembly.py:207-216`), so with `--project` and no env var, Tim's prompt silently loses THE GATHERING / YOUR ROLE / THE PANEL. This is next to C67 row 10 (a different call site), not the same finding.
- **N4 — Night 1–3 hard limits.** These are in `editor_flow.py:324`, `card_assembly.py:308-309`, `voice_flow.py:697` and `overnight_orchestrator.py:66-71, 580`. They are likely covered by C52; not re-filed.
- **N5 — `orchestrator@.service` restarts on the orchestrator's own failure exits (CONFIRMED by reading; systemd semantics, not run).** See L12. The comment at `:22-25` is wrong about `Restart=on-failure`. **Fix direction:** add `RestartPreventExitStatus=1 2` (or `Restart=on-abnormal`), and correct the comment. It only matters once a VM exists (B10). It is separate from C68 A4, which covers the sandbox paths in the same file.
- **N6 — Editor output headroom (PLAUSIBLE risk).** Measured output reached 24,401 of the 32,000-token ceiling (E12). No dossier has hit it yet.

---

## 6. Recommended trust ratings for `docs/README.md`

**Recommendation:** downgrade two rows, reword two. Each row carries the fixes it waits on; the ratings go back to "Current" once those land.

| File | Today | Recommended | Suggested Notes text |
|---|---|---|---|
| `AI_Assembly_Editor_Pipeline.md` | Current with caveat | **Current with caveat** (reworded) | "Stage 1 routing, cost figures and CLI checked 2026-09-28 (`_workspace/planning/runtime/REVIEW_2026_09_28_spec_check.md` §1): routing now happens mostly in Voice Step 2 (Stage 1 is a fallback); measured Athens cost ≈ $10, not $3–5; CLI misses `--bypass-gating` / `--project`; two listed defensive checks don't exist. Fixes pending." |
| `AI_Assembly_Runtime_Lifecycle.md` | Current | **Partly stale** | "Stage 6 current (2026-09-28). The rest predates C26 (the orchestrator dispatches transcription) and C28b (the operator review gate), and has wrong paths for `council_config.json` and the continuity files and the wrong publish sentinel; §8 describes a VM run that never happened. See the spec check §4." |
| `AI_Assembly_Transcription_Pipeline.md` | Current with caveat | **Current with caveat** (widen the caveat) | "Steps 2–5 (audio: ASR, speaker ID incl. C49, cleaning, output) current. **Step 1 Ingest is stale**: it describes a Drive/rclone/watchdog intake — actual intake is the ingest upload form + orchestrator dispatch (see the Lifecycle spec) — and treats reflections as audio; reflections arrive as vendor JSON via `runtime/scripts/reflections_to_session_package.py` → `runtime/flows/vendor_intake.py`, with a metadata gap (runtime OPEN_ITEMS C68 A1). Replacement text: spec check §3." |
| `AI_Assembly_Frame_Concept_v1.md` | Not re-checked | **Historical concept (pre-Athens)** — move to a "Design / concept" group or keep with this status | "Checked 2026-09-28 (spec check §2): records pre-Athens intent. The broadsheet became the Editor Pipeline's dossiers (HoBB, no masthead); Substack dropped (B4); headline poetics reduced to headnote titles (B9); closing show and Day 4 not built here (B5, B6); micro-site outside the repo (B2). The FU#61 strip-rule note still applies." |

Also for `docs/README.md` line 7: "Last full check against code: 2026-09-28" overstates for these four parts, which had not been checked until now. Suggest adding "(except the parts listed in `REVIEW_2026_09_28_spec_check.md`, fixes pending)". This review did not re-check the other rows.

---

## 7. Coverage

- **Editor spec:** read in full (1,077 lines). Code read in full: `editor_flow.py`, `editor/routing.py`, `editor/synthesis_router.py`, `editor/card_assembly.py`. Read in part: `editor/dossier_generation.py` (1–80, 540–622), `voice/step2_first_draft_artifact.py` (190–414), `shared/io.py` (loaders and night check).
- **Lifecycle spec:** read in full (467 lines).
  - Read in full: `scripts/overnight_orchestrator.py`, `scripts/deploy/orchestrator@.service`.
  - Searched or read in part: `ingest/pipeline.py` (states and function list), `ingest/app.py` (`_maybe_auto_fire_editor`, vendor guards), `voice_flow.py` (argparse, publish hook), `voice/card_assembly.py` and `voice/continuity.py` (continuity paths), `voice/step2_validation.py` (verdicts).
  - Checked for `--project`: researcher, provocateur and publish flows.
  - **Not traced:** `researcher_flow.py` and `provocateur_flow.py` outputs (Stage 3–4 write lists), and `publish_flow.py`'s write list (Stage 7). These are unverified; no discrepancy is claimed for them.
- **Transcription spec:** read lines 1–275 in full. Lines 276–759 (Steps 2–5, Implementation) were searched for reflection text only.
  - Read in full: `scripts/reflections_to_session_package.py`.
  - Read in part: `flows/vendor_intake.py` (docstring, `land`, argparse), `ingest/sessions.py::build_session_json`.
  - Checked for field reads: `researcher_flow.py` and `transcription_flow.py`, for `session_title` / `session_description` / `session_format`.
- **Frame Concept:** read in full (324 lines). Checked against runtime OPEN_ITEMS B2–B9, `docs/` and `git ls-files`.
- **Data (athens-2026, read-only):**
  - the three `theme_routing.json` and `05_editor/manifest.json` files;
  - the metadata of all 13 published dossiers;
  - N1 Dostoevsky's Step 2 lineage;
  - all five vendor sessions' `01_transcription/<id>/` files;
  - `reference/sessions.json` field names and counts;
  - the project-root file list;
  - `voices/plato/` continuity files.
- **Scratch:** `dossier_costs.py` (read-only pricing of dossier metadata) and inline `python3 -c` reads of sessions.json and vendor packages. None calls an API.
