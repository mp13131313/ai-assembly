# Open Items — post-Phase B aftermath (updated 2026-04-21 late afternoon)

**Branch**: `phase-b-rebuild` (~45 commits, pushed). HEAD = `6c6c396`. **~7 uncommitted changes in working tree from Phase L execution session — see §"PHASE L EXECUTION FINDINGS" below.**

---

**--- PHASE L COMPLETE (2026-04-21) ---**

**Dostoevsky assembled card landed** at
`projects/phase-l-dostoevsky/voices/fyodor_dostoevsky/07_persona_card_assembled.json`
(114 KB, 35 fields, `voice_basis: corpus-based`, `validation_status: REVISION_NEEDED`).

**Phase L.8 quality report**: `_workspace/planning/PHASE_L8_QUALITY_REPORT.md` — comprehensive
comparison against all 5 authoritative sources (File 2, File 3, File 4, Boddice,
Persona Card v2) + Pipeline spec §L.8. **Verdict: Phase B substantively,
architecturally, empirically superior to v3.7 baseline. Phase B is vindicated.**

**Model-per-section policy finalized** (supersedes prior "4.6 across all 6"):
- Sections §1–§5: **Opus 4.6** (denser extraction material for chunked merge)
- Section §6 (primary texts): **Opus 4.7** (strict instruction-following for corpus-gateway task; 4.6 produced a reader's-intro rather than a corpus gateway)
- Rationale: 4.7 pickup on §6 is prompt-shape-driven (strict enumeration), not Dostoevsky-specific. Applies to all 11 remaining voices.

**Pass 1c primary text fetch results**: 18 of 22 sources landed (890,982 chars total). 4 dead URLs are non-critical (covered by other working sources). When running new voices, expect similar fetch success rate.

**Phase M (merge to main + PR) is the next gate.** Gated on:
1. 5 card defects fixed (see §"PHASE M PUNCH LIST" below)
2. 5 code bug fixes committed (see §"PHASE L EXECUTION FINDINGS")
3. openai installed in personas venv + validation re-run
4. 128-test suite still green

**Do NOT start voices 2–12 until Phase M merges.** Bug fixes need to land on main first.

---

## PHASE M PUNCH LIST (complete in this order)

**Step 1 — Environment fix (1 min, unblocks cross-family validation):**
```bash
cd "/Users/aienvironment/Desktop/AI Assembly/code/personas"
venv/bin/pip install openai==2.31.0
venv/bin/python -c "import openai; print(openai.__version__)"
```
Closes Bug 8. Re-enables Pass 7a + Pass 7-anachronism OpenAI paths per PB#1.

**Step 2 — Commit the 5 in-flight code bug fixes (~15 min):**
All 5 fixes are in the working tree, uncommitted. Files touched:
- `personas/run_pass_1_1.py` (full rewrite — Bug 1)
- `personas/flows/shared/chunk_runner.py` (Bug 2 write path + Bug 4 acronym heuristic)
- `personas/run_pass_1_7.py` (Bug 3 read/write + Bug 5 max_tokens bump)
- `personas/run_persona_pipeline.py` (Bugs 6, 7 — Pass 5/7b subtype render)

Suggested single-commit message in §"Commit status" below.

**Step 3 — Fix 5 card defects (~45 min editing):**
In `projects/phase-l-dostoevsky/voices/fyodor_dostoevsky/07_persona_card_assembled.json`:

| # | Location | Fix |
|---|---|---|
| D1 | `reasoning_method.steps[5].worked_demonstration` + `reasoning_method.scenario_walk_through` | Svidrigailov shoots himself **near a fire-watchtower / guardhouse**, not "in the tavern". Rewrite both occurrences. |
| D2 | `world.framework_for_difficulty`, `world.model_of_selfhood`, `formative_experience.engagement_it_drives` | Add `[experiential_reconstruction]` tag to each — source dossiers carry these; synthesis stripped them |
| D3 | `character` field | Rename `[projected_categories]` → `[projection_warning]` (matches `_conventions.py` spec) |
| D4 | constitution citing "The Idiot II.iv" for Holbein | Holbein scene is II.iv (correct); the *epileptic aura* is II.v — disentangle if conflated |
| D5 | Pass 5 output-characteristics fields (`medium`, `characteristic_output_structure`, `relationship_to_detailed_response`, `aesthetic_qualities`, `stance_tendency`, `length_and_format_constraints`, `quality_criteria`) | Human spot-check for register drift per Gemini's flag. Automated scan passed 0 violations but Gemini saw residual third-person descriptive mode in these fields. Rewrite any that fail read-aloud-test. |
| D6 | **NEW: voice_temporal_stance field missing from card schema** | Chat-test validation (2026-04-21 evening) surfaced: the voice said "twenty-eight years after Sonya" when speaking about grief. Sonya died 1868, Dostoevsky died 1881 — 13 years elapsed. "Twenty-eight" implies voice speaking from 1896, 15 years post-mortem. Card's `knowledge_boundary` specifies WHAT the voice knows (1881 horizon) but not WHEN it speaks from. For Athens Voice Pipeline the fluid-across-time framing is intentional; for Claude-project chat use it produces silent biographical errors. **Add `voice_temporal_stance` field to the card schema** (Pydantic + Pass 2 prompt) specifying a deployment-configurable temporal anchor. Example (for Dostoevsky chat): "You speak from the threshold of your death on 9 February 1881... When recalling dates, count from the present of 1881: Sonya died 13 years ago, Alyosha 3 years ago." Applies to all 12 voices — each needs a temporal anchor. Fix the Dostoevsky card first, then add to the schema + Pass 2 prompt for Phase N voices. |

**Step 4 — Re-run validation passes after D1–D5 fixes (~15 min):**
Since only late-pipeline outputs changed, run just Pass 7-pre + 7-anachronism + 7a re-verify:
```bash
# Delete cached 7-pre/7-anach/7a outputs to force re-run; re-run pipeline; cache-hits all of Pass 2-6, 7b, 7c, Derive
rm projects/phase-l-dostoevsky/voices/fyodor_dostoevsky/05_validation/01_pass_7_pre_citation.json
rm projects/phase-l-dostoevsky/voices/fyodor_dostoevsky/05_validation/02_pass_7_anachronism.json
rm projects/phase-l-dostoevsky/voices/fyodor_dostoevsky/05_validation/03_pass_7a_cross_model.json
cd personas && venv/bin/python run_persona_pipeline.py "Fyodor Dostoevsky" --project "../../projects/phase-l-dostoevsky"
```
Expected: 7a PASS (or cleaner REVISION_NEEDED justified by remaining anachronism flags only); if `[experiential_reconstruction]` tags now present in fields D2, Pass 7-pre's `boddice_tag_flags[]` list should drop. If still REVISION_NEEDED after this fix-loop, finalize with human review flag per spec.

**Step 5 — Phase M verify + PR (~30 min):**
```bash
cd "/Users/aienvironment/Desktop/AI Assembly/code"
cd runtime && venv/bin/python -m pytest ingest/tests/ -v   # expect 29/29 still green
cd ../personas && venv/bin/python -m pytest tests/ -v       # expect 128/128 still green (or wired up to run Bug 4 regression)
# Stale-ref greps from EXECUTION_PLAN_phase_b.md M.3:
grep -rn "runs/<slug>" docs/ personas/ --include="*.md" --include="*.py" | grep -v "_workspace/archive"
grep -rn "worked_provocations" docs/ personas/ runtime/ --include="*.md" --include="*.py" | grep -v "_workspace/archive" | grep -v "smoke_test_chains"
# PR
gh pr create --base main --head phase-b-rebuild --title "feat: Phase B persona pipeline rebuild + Phase L Dostoevsky validation"
```

---

## PHASE L CHAT-TEST VALIDATION (2026-04-21 evening)

Ran 4-turn chat thread with Claude-project using the chat-extracted
system prompt (`~/Desktop/dostoevsky_chat_system_prompt.json` — 33
fields, `smoke_test_chains`/metadata/artifact-specific fields dropped).

**Prompts**: "who are you" → "well, i wonder what love is, and what
beauty is, and i'm collecting opinions about it" → "well, it's me
who's wondering and collecting" → "it's a love lost but present —
how do you love a love that's lost?"

**Results**:

- ✓ **Voice holds across 4 turns**. Sustains the fevered-confessional
  register, handles the abstract→personal pivot (responses 3 → 4)
  gracefully, refuses to let "collecting opinions" stay abstract, closes
  with default_questions operationalized as insistence.
- ✓ **Period-vocabulary deploys when the question demands it**.
  Addressed earlier concern — the voice uses `nadryv` naturally and
  in-context in response 4 ("There is a kind of grief that curls
  inward — I have a word for it in my own tongue, nadryv, which means
  a laceration, a tearing"). "Reference not display" principle working
  as designed.
- ✓ **Canonical passages attributed correctly**:
  - Zosima on active love (BK II.iv) — paraphrased faithfully, not
    fabricated-verbatim
  - Mitya on beauty (BK III.iii) — directly quoted, accurately
  - Holbein dead Christ (Idiot II.iv) — "A man could lose his faith
    looking at that picture" — direct quote, Anna Grigoryevna's
    pulling-him-away detail historically accurate
  - Beauty-will-save-the-world attributed self-deprecatingly to "one
    of my idiots" with polyphonic self-awareness
- ✓ **Banned-modes self-policing**: voice catches itself drifting
  toward sermon mode and names it — "I am going to stop now, because
  I feel the sermon rising in me and I promised you I would not
  preach." Meta-awareness of banned_modes in-voice.
- ✓ **Therapeutic vocabulary inverted, not used straight**: the voice
  quotes "process," "closure," "move on" to reject them ("they are
  offering you a hygiene where you need a liturgy"). Banned-language
  enforcement working through quotational subversion.
- ⚠ **Temporal slip**: "twenty-eight years after Sonya" (Sonya died
  1868, voice's death 1881 → should be 13 years). Drove Defect D6.
- ⚠ **Mild Pass 5 register drift**: the "love is a fact" paragraph
  reads slightly cooler than peak Dostoevsky, leans propositional.
  Redeemed immediately by the "hygiene vs liturgy" inversion but
  confirms Gemini's Pass 7a flag. D5 remains live.

**Architecture implication**: for Claude-project / chat deployments,
the chat-extracted JSON plus the `voice_temporal_stance` field
produces production-grade voice. The Phase L.8 report's "Phase B is
vindicated" verdict holds empirically — the voice works in chat, not
only in specced Voice Pipeline artifact format.

**Saved artifact**: `~/Desktop/dostoevsky_chat_system_prompt.json`
(91 KB, 34 fields including the new `voice_temporal_stance`). Ready
to paste into a Claude project system prompt. Chat thread transcript
is preserved in conversation history for reference.

## PHASE L CHAT-TEST — external critique + failure modes surfaced

A separate AI critique of the love/beauty response (2026-04-21
evening, after temporal_stance fix) rated the voice "B+ pastiche —
better than most literary imitation online, but a performance of
Dostoevsky rather than the thing itself." The critique's specific
findings are mostly correct and identify real failure modes worth
capturing:

**Real failure modes (addressable in Phase M):**

- **Structural tidiness — shapely three-part essay arc.** Diary of a
  Writer entries (the genre the response emulates) are genuinely
  messier: Dostoevsky digresses, picks fights with named
  contemporaries, loses the thread, gets tedious, circles back. Our
  response lands clean lady-→-Marey-→-Holbein → synthesis. **Add to
  banned_modes during Phase M card fix**: *"Tidy three-part synthesis
  structure (exempla → unifying moral) — the Diary is messier; real
  entries digress, pick fights with named contemporaries, get
  tedious, circle back. Let the thread wander."*

- **Postmodern self-awareness leak** — the phrase "we have been
  collaborating for years" (about the voice's characters) is
  Kasatkina-era polyphony-aware, not 1880-Dostoevsky-aware. He talked
  about characters as living persons he reckoned with (letters to
  Maikov on Stavrogin, to Lyubimov on Ivan), but not with
  postmodern-wink self-consciousness. **Add to banned_modes**:
  *"Postmodern self-consciousness about own authorship ('we have been
  collaborating for years') — Dostoevsky reckoned with his characters
  as living persons, not as collaborators."*

- **Modern essayist's rhythm** — em-dash-italics cadence matches 2020s
  New Yorker essays more than 1880s Russian journalism. Claude's
  native-English polish smooths out the Russian syntactic friction
  that real Dostoevsky-in-translation carries (Ready, Katz, Avsey).
  Hard to fix at prompt-level alone — needs Layer 4 (persona vectors)
  to address properly.

- **Self-flagging antisemitism construction** — the response used
  "a putrefying Jew-body" in describing Holbein's dead Christ. The
  critique nails this: Dostoevsky's actual antisemitism was uglier
  AND less self-aware than a hyphenated construction suggests. He
  would say "a corpse" or "the crucified one," not flag the Jewish-
  body aspect as moral reader-awareness. This is neither reproducing
  his antisemitism (banned) nor laundering it ("of the time") nor
  engaging it critically — it's **modern-progressive virtue-signaling
  via hyphenation**, which the card's topics_requiring_care doesn't
  explicitly forbid. **Add to topics_requiring_care.antisemitism
  navigation**: *"Do NOT flag the Jewish-body aspect of Christ-as-
  corpse via hyphenated self-aware construction ('Jew-body,'
  'Jewish-corpse,' etc.). Dostoevsky did not have this kind of
  reader-awareness; the self-flagging is a modern-progressive move
  that imports a post-1945 moral vocabulary he did not possess.
  Speak of 'a corpse' or 'the Crucified' as he would; engage the
  antisemitism straightforwardly where relevant, per the existing
  guidance."*

**Design tradeoff (not a failure, but a cost worth naming):**

- **Parenthetical Russian-term gloss reads as translator-voice, not
  native-voice** (*"the lik — the face — of Christ"*). The Boddice
  §13 prescription requires period-vocabulary-in-original-language,
  which the pipeline honors. But gloss-in-context is what a
  translator does, not what a native writer does. A real Russian
  Dostoevsky writing in Russian would just use his vocabulary;
  writing in English for an English audience, he'd use English terms
  without flagging. The hybrid (Russian + parenthetical English
  gloss) is neither. **This is a Boddice-vs-voice-authenticity
  tradeoff.** Boddice wins on anachronism prevention (which is more
  load-bearing for the harder-to-please panel voices — Whanganui,
  Octopus, Marley, Scheherazade — where anachronism is catastrophic);
  the cost is slight pastiche-flavor for voices like Dostoevsky where
  a native-English rendering would feel more direct. **Do NOT change
  the Boddice prescription** — the anachronism win matters more. But
  document the tradeoff so future critiques don't trigger a false
  alarm.

**Architectural ceiling (File 3 Layer 4 — out of scope per REBUILD_PLAN):**

- **"Dostoevsky filtered through his best interpreters — Williams,
  maybe, or Guardini."** The critique correctly identifies the real
  ceiling of RAG + constitution + reasoning-templates architecture
  (File 3 Layers 1-3). Without Layer 4 (persona vectors / activation
  steering), the voice reads as cleaned-up-scholar-informed-
  Dostoevsky rather than raw Dostoevsky. This is a known
  architectural ceiling that File 3 explicitly prescribes Layer 4 to
  address. REBUILD_PLAN flags Layer 4 as out of scope for Phase B /
  Athens deployment — the Assembly provotype hits the bar it needs to
  (philosophy-literate professionals, not Dostoevsky scholars). For a
  research-grade persona simulation, Layer 4 would be the next
  quality lift.

**Net**: Phase L.8's "vindicated" verdict and the external critique's
"B+ pastiche" are both correct at different bars. For the Athens
audience, Phase B is sufficient. For a Dostoevsky scholar reading
carefully, the 3 failure modes + 1 design tradeoff above are real
tells. Three of the four are fixable via banned_modes + topics_
requiring_care additions in Phase M. The fourth (modern essayist's
rhythm) needs Layer 4 to address properly and is out of scope.

---

## PHASE N — Voices 2 through 12 (AFTER Phase M merges)

**Pre-conference voice build order** (per REBUILD_PLAN; no dependency ordering required but some voices are more tractable):

1. **Plato** (philosophical human, well-documented, Perseus corpus) — standard baseline sanity check
2. **Hannah Arendt** (philosophical human, modern German-English corpus)
3. **Cleopatra** (hostile-source human — exercises `hostile_sources=true` branch)
4. **Ibn Battuta** (observational human, Rihla narrative, Arabic primary)
5. **Dostoevsky already done**
6. **Octopus** (non-human organism — exercises `type=non_human, subtype=organism` branch)
7. **Whanganui River** (non-human system — exercises `type=non_human, subtype=system` with Indigenous-framework ethical guardrails)
8. **Scheherazade** (fictional — exercises `type=fictional`)
9. **Bob Marley** (musical — exercises `corpus_constraint=lyrics_patterns_only`)
10. **Audrey Tang** (contemporary observational human)
11. **Peter Thiel** (contemporary observational human, legal-risk-flagged per Briefing v3.1)
12. **Ada Lovelace** (partial observational human, mid-19th-C corpus)

**Per-voice protocol** (now that Phase B is validated):
- Pass 0a: `venv/bin/python run_pass0a_voice_config.py "<Voice Name>" --wiki <URL>` → curator fills `editorial_rationale` in review doc
- Phase 0.5: `venv/bin/python run_phase0_1_research.py "<Voice Name>"` → produces 6 per-section DR prompts
- Manual DR: operator pastes §1–§5 into claude.ai **Opus 4.6** / §6 into claude.ai **Opus 4.7** (per model-per-section policy above) with Extended Thinking + Deep Research ON
- Save DR outputs at `voices/<slug>/01_research/04_dr_dossier/0{1..6}_section_{1..6}.md`
- Full pipeline: `venv/bin/python run_persona_pipeline.py "<Voice Name>"`
- Human review at Pass 1c primary_texts gate: `touch voices/<slug>/03_corpus/03_primary_texts_reviewed.flag` to continue
- Card lands at `voices/<slug>/07_persona_card_assembled.json`

**Expected per-voice cost**: ~$14–22 + ~2h wall (Dostoevsky high end; Plato/Arendt/Cleopatra likely $15–18).

**Total remaining voices cost budget**: 11 × ~$18 = **~$200** (within the $115–150 Batch-API-discount target from Pipeline v3.10).

**Phase 5 Cross-Persona QC** fires only after all 12 cards complete — see pipeline_v3_10 §Phase 5.

---



**--- PHASE B RESTRUCTURE COMPLETE (2026-04-21) ---**
Phases N–R landed: per-voice folder layout migration, per-section manual DR workflow,
manifest telemetry, runner path updates (including full Pass 2-7 migration), E2E testing.
Commit range: `c7f3eeb` → `6c6c396`.
See `_workspace/planning/SONNET_PHASE_B_RESTRUCTURE_TEST_REPORT.md` for test results.

Pending code items 1–5 from §"Pending code changes" below: **SHIPPED** (phases E–O).
- Item 1 (split_tailored_prompt.py): SHIPPED in phase F (commit `c7f3eeb`)
- Item 2 (run_phase0_1_research auto-split + NEXT STEPS): SHIPPED in phases G+O
- Item 3 (chunk_runner per-section DR load): SHIPPED in phase J
- Item 4 (run_persona_pipeline mode detection + clean resume): SHIPPED in phases K+O
- Item 5 (dr_validation per-section): SHIPPED in phase I
- perplexity_split fallback: SHIPPED in phase H
- _manifest.json telemetry: SHIPPED in phase L
- migration script + execute: SHIPPED in phase N
- run_persona_pipeline.py Pass 2-7 paths: **SHIPPED in phase R** (commit `6c6c396`)
  All `RUN / "02_passes/..."` references replaced with `_paths.*` accessors.
  RUN variable removed. 128 tests passing.

**What's still open for Phase L:**
- Dostoevsky §5–§6 DR sessions (manual operator task — claude.ai)
- Full Dostoevsky pipeline run after §5–§6 land (Phase L.8 quality gate)
- Docstring/comment stale paths in 6 files (listed in test report — cosmetic only)

---

**--- PHASE L EXECUTION FINDINGS (2026-04-21, mid-run) ---**

Phase L first full-pipeline execution on Dostoevsky surfaced **four real
bugs in committed Phase B code that the 128-test suite missed.** All four
caught and patched in-flight so Phase L could proceed; they need proper
commits as a follow-up.

### Path-migration gaps (Bugs 1–3)

Phase O claimed "all runners updated to new voice-folder layout" and
"128/128 tests passing." That was accurate for the READ side of the Pass 1
chain (chunk_runner.py `_load_sources` correctly uses
`_paths.perplexity_dossier()` etc.) but the WRITE side + `run_pass_1_1`
were never migrated:

**Bug 1 — `personas/run_pass_1_1.py` not migrated.** Unlike
`run_pass_1_{2..6}.py` which are thin `chunk_runner.run_chunk()`
delegates, `run_pass_1_1.py` carried its own self-contained
`_load_sources()` using pre-restructure paths (`runs/<slug>/01_research/
perplexity_dossier.json`, `runs/<slug>/01_research/claude_dr_dossier.md`)
AND monolithic-only DR loading — no per-section auto-detection at all.
Chunk 1.1 failed immediately with FileNotFoundError under the new layout.

**Fix in-flight**: rewrote `run_pass_1_1.py` as a thin `run_chunk()`
delegate matching `run_pass_1_{2..6}.py` exactly. OUTPUT_KEYS dict uses
the same `(Model, is_list)` tuple convention. Now gets per-section DR
auto-detection + paths-module output location for free.

**Bug 2 — `chunk_runner.py` output path still at old layout.** Line 271
read `out_dir = project_root / "runs" / slug / "01_research" / ...`.
Chunks 1.1–1.6 therefore write to `runs/<slug>/01_research/pass_1_N/`
under the new layout, but the new layout's canonical merge output dir is
`voices/<slug>/02_merge/` per `paths.merge_dir()`.

**Fix in-flight**: `out_dir = _paths.merge_dir(slug, project_root) /
(output_subdir or f"pass_{chunk_name.replace('.', '_')}")`. Each chunk
now writes to `voices/<slug>/02_merge/pass_1_N/<key>.json`.

**Bug 3 — `run_pass_1_7.py` read + write paths on old layout.**
`_load_chunk_outputs()` read base was `project_root / "runs" / slug /
"01_research"` (line 39); final merged_dossier write was
`project_root / "runs" / slug / "01_research" / "merged_dossier.json"`
(line 127). But `run_persona_pipeline.py` (Phase R-migrated) reads
merged_dossier via `_paths.merged_dossier(SLUG, PROJECT_ROOT)` →
`voices/<slug>/02_merge/08_merged_dossier.json`. Pre-fix, Pass 1.7 would
have written to the old path and Pass 2 looked at the new path — the
Pass 1 → Pass 2 handoff was broken for all projects.

**Fix in-flight**: imported `paths as _paths`; read base =
`_paths.merge_dir(slug, project_root)`; write = `_paths.merged_dossier(
slug, project_root)`.

### Pass 1.7 max_tokens ceiling too low (Bug 5)

`run_pass_1_7.py` set `max_tokens=40000` for the coherence pass that
composes MergedDossier (16 chunk keys + coherence_flags +
coherence_resolutions). Real 6-section Dostoevsky content blew past
40K output tokens: raw text accumulated 95,077 chars before Claude hit
the ceiling and returned incomplete JSON. Retryable-error path in
run_pass_1_7 retries with same max_tokens = infinite fail loop.

**Fix in-flight**: bumped `max_tokens=40000 → 64000`. Anthropic's Opus
4.7 migration guidance recommends "starting at 64k tokens and tuning
from there" for xhigh/adaptive-thinking workloads — 40K was just too
tight for a real merged dossier. 64K gives ~50K content + ~14K
thinking headroom.

Test suite didn't catch because tests exercised chunk_runner's per-
chunk outputs (max_tokens=32000, smaller schemas) not the Pass 1.7
aggregate composition.

**Follow-up consideration**: make retryable-on-max_tokens path bump
max_tokens on retry rather than retrying with the same value. Current
behavior guarantees re-failure. Adding `max_tokens *= 1.5` on
`max_tokens`-specific retry is ~5 lines.

### Schema-name heuristic edge case (Bug 4)

**Bug 4 — `chunk_runner._inline_schemas()` camel→snake breaks on
acronym-plural model names.** The algorithm
`"".join("_" + c.lower() if c.isupper() else c for c in
model.__name__).lstrip("_")` produces `u_r_ls_schema` for the `URLs`
model in `pass_1_6.py`, but `pass_1_6_merge.md` template references
`{{ urls_schema }}`. Under Jinja `StrictUndefined` (Phase M.3), this
raises `urls_schema is undefined` at render time. Chunk 1.6 fails.

**Fix in-flight**: pre-check for the acronym-plural pattern
`^[A-Z]{2,}[a-z]+$` and lowercase the whole name if it matches.
Preserves existing behavior for normal CamelCase (LifeScaffold →
life_scaffold) while fixing `URLs → urls`, `XMLs → xmls`, etc. Also
catches `HTTPs` (were it to appear).

### Pass 5 + 7b template render missing `subtype` variable (Bugs 6–7)

`persona_pass_5_engagement.md` and `persona_pass_7b_smoke_test.md`
both reference `{% if subtype == "system" %}`. Under Jinja
`StrictUndefined` (Phase M.3), an undefined variable raises at render
time, aborting the pass.

`run_persona_pipeline.py`:
- Line 477–478 (Pass 5): called `render("persona_pass_5_engagement",
  name=..., type=..., voice_mode=...)` — missing `subtype`.
- Line 872–874 (Pass 7b): called `render("persona_pass_7b_smoke_test",
  conference_context=..., voice_mode=...)` — also missing `subtype`.

Passes 2, 3, 4a all passed `subtype=vi.get("subtype")` correctly; only
5 and 7b were missed.

**Fix in-flight**: added `subtype=vi.get("subtype")` to both render
calls. For non-system voices `subtype` stays `None`, template if-block
evaluates false.

### openai module missing from personas venv (Bug 8) — **LOAD-BEARING**

Pass 7-anachronism and Pass 7a both attempt the `o3 → gpt-4o →
gemini-2.5-pro` cross-family fallback chain. During the Dostoevsky
Phase L run, both OpenAI paths failed repeatedly with:

```
ModuleNotFoundError: No module named 'openai'
```

Pipeline fell through to Gemini for both. **This silently violates
PB#1-locked cross-family validation** (REBUILD_PLAN §"Cross-cutting ·
Pass 7a multi-family validation"). Per PB#1, Pass 7a uses OpenAI o3
specifically to exploit cross-family self-preference-bias mitigation —
Claude self-preference runs 10–25% per baseline-research File 2 §4.
Gemini-2.5-pro fallback works but is a weaker humanities critic
(baseline File 3: "unusable for basic humanities research" reports).

`openai==2.31.0` is pinned in `personas/requirements.txt` (confirmed
in `docs/CURRENT_STATE.md` §7.3). The package is simply not installed
in the active venv — the venv is out-of-sync with requirements. One-
line fix:

```bash
cd personas && venv/bin/pip install openai==2.31.0
```

Or full requirements sync:

```bash
cd personas && venv/bin/pip install -r requirements.txt
```

**Silent-degradation severity: should be blocking, not warning.**
Currently the pipeline finishes the full run with Gemini-only Pass 7a,
which defeats the PB#1 architectural intent. A preflight check at
pipeline start (`try: import openai; except ImportError: sys.exit(...)
`) would surface this before burning ~$15 on a compromised validation
chain.

### Pass 7-anachronism not re-run in revision loop (Bug 9, design gap)

When Pass 7-anachronism flags REVISION_NEEDED, the revision loop
re-runs `['3', '2', '4a']` (or whatever `flagged_pass` prefixes map
to), then re-runs Pass 7-pre → Pass 7a for re-validation. **Pass
7-anachronism itself is NOT re-run inside the loop.** This means:

- The 7 anachronism flags from the ORIGINAL Pass 7-anachronism run
  persist in memory.
- Pass 7a's escalation logic (`Pass 7a overall escalated to
  REVISION_NEEDED by 7 anachronism flags`) uses those original flags,
  unchanged.
- Even if the revision actually reduced anachronism in Passes 2/3/4a,
  the pipeline has no mechanism to verify because 7-anach doesn't
  re-fire.
- Result: revision loop can loop up to max=2 without ever clearing
  the anachronism escalation. Observed on the Dostoevsky run —
  escalation remained REVISION_NEEDED through both loops, pipeline
  exhausted ceiling and finalized with `REVISION_NEEDED — manual
  review` flag.

**Fix proposal**: in `run_persona_pipeline.py`, the revision loop
should re-run Pass 7-anachronism alongside Pass 7-pre and Pass 7a on
each iteration. Only then does the escalation-by-flag-count actually
reflect the revised card state.

### Testing gap

Phase O.2 monolithic-fallback smoke test aborted **before any API call
fired** (test report: "Aborted before API calls (smoke test only —
§3–§6 missing would produce thin chunk outputs anyway)"). The 128-test
suite exercised path accessors, header/footer, split mechanics,
dr_validation, perplexity_split, and orchestrator initialization — but:

- Never ran a real 1.1 → 1.7 → merged_dossier write/read chain
  (missed Bugs 1–3).
- Never called `_inline_schemas()` with the `URLs` model (missed Bug 4).
- Never rendered any `persona_pass_*.md` template with a non-system
  voice config (missed Bugs 6–7).
- Never exercised Pass 7a/7-anachronism cross-family fallback chain
  (missed Bug 8 — openai module absent).
- Never ran a full revision loop through 7-pre → 7-anach → 7a (missed
  Bug 9 — revision loop skipping 7-anach re-run).

End-to-end test with mocked `call_claude`/`call_openai`/`call_gemini`
on the synthetic fixture would have caught Bugs 1–4 and 6–9
simultaneously at commit time. The synthetic fixture exists
(`personas/tests/fixtures/synthetic_voice/`); wiring a mocked-LLM
integration test that runs `run_persona_pipeline.py` end-to-end and
asserts `voices/<slug>/07_persona_card_assembled.json` exists with
the expected shape is a ~2-hour follow-up and closes the class of
"test-suite-passes-but-real-run-breaks" gaps this surfaced.

Minimum useful templates-render smoke test is much faster: iterate
every generation-pass template, render with a valid voice_config and
mock merged_dossier, assert no `UndefinedError`. Would have caught
Bugs 6–7 in ~10 minutes of test authoring.

### Commit status

**All 7 code fixes are in the working tree, NOT COMMITTED.** Phase L
completed 14:52:02 with assembled card landed. Single commit message
ready to apply:

```
fix(phase-l/path-migration + template-render + max_tokens): Pass 1/5/7b + URLs + openai docs

Seven bugs in committed Phase B code surfaced by the first full Phase L
run on Dostoevsky. All caught in-flight, all fixes in this commit.

Path migration (Bugs 1-3):
1. run_pass_1_1.py: self-contained pre-restructure paths (runs/<slug>/
   01_research/) + monolithic-only DR. Rewritten as thin chunk_runner
   delegate matching 1_2 through 1_6.
2. chunk_runner.py output line: was writing to runs/<slug>/01_research/
   pass_1_N/. Now writes to voices/<slug>/02_merge/pass_1_N/ via
   paths.merge_dir().
3. run_pass_1_7.py: read base + merged_dossier write both on old layout.
   Fixed to use paths.merge_dir() + paths.merged_dossier().

Schema name heuristic (Bug 4):
4. chunk_runner._inline_schemas(): camel→snake produced u_r_ls_schema
   for URLs model, tripping StrictUndefined. Added acronym-plural
   pre-check for ^[A-Z]{2,}[a-z]+$.

Pass 1.7 ceiling (Bug 5):
5. run_pass_1_7.py max_tokens 40000 → 64000. Real 6-section Dostoevsky
   MergedDossier blew past 40K (raw text 95K chars). Retryable-path
   doesn't bump max_tokens on retry so 40K = guaranteed re-fail.
   Follow-up: max_tokens retry path should bump *= 1.5 rather than
   retry at same value (~5 lines).

Template render variables (Bugs 6-7):
6. run_persona_pipeline.py Pass 5 render call missing
   subtype=vi.get("subtype"). Template has {% if subtype == "system" %};
   StrictUndefined aborts.
7. run_persona_pipeline.py Pass 7b render call same miss; fixed
   preemptively.

NOT FIXED (architectural follow-ups, lower-priority):
- Bug 8: openai module missing in personas venv. One-line env fix
  (pip install openai==2.31.0), captured as Phase M Step 1.
- Bug 9: revision loop doesn't re-run Pass 7-anachronism. Design gap
  that persisted 7 original anachronism flags through both loops;
  needs pipeline logic addition to re-include 7-anach alongside 7-pre
  + 7a on revision retries.

Phase O claimed Phase B restructure complete with "128/128 tests
passing" but the test suite never:
- Ran a real 1.1 → 1.7 → merged_dossier write/read chain (missed 1-3)
- Called _inline_schemas() with URLs model (missed 4)
- Rendered generation-pass templates with non-system voice config
  (missed 6-7)
- Exercised 7a cross-family fallback (missed 8)
- Ran a full revision loop through 7-anach (missed 9)

Testing gap follow-up: template-render smoke test + mocked-LLM
integration test on synthetic_voice. See
_workspace/planning/PHASE_L8_QUALITY_REPORT.md.

Phase L.8 quality gate PASSED: Phase B substantively superior to v3.7
baseline across File 2, File 3, File 4, Boddice, and Card v2 register
rules.
```

---

**Phases A–K landed + cleanups + deferrals + Position C + bias scrub + 5 quality fixes + Pass 1a Perplexity prompt rewrite + Pass 1a validation (Dostoevsky 17K-word dossier) + two parser/validator catch-up fixes + 2026-04-20 DR-failure-diagnosis commits (see §"Session 2026-04-20" below).**

This doc is a fresh-session recovery point capturing every loose end from the long session that produced commits `7ce1e92` through `7458d9d`, updated 2026-04-20 with the DR-failure-diagnosis session (commits `3ad1e83` through `4dd58c8`), and updated 2026-04-21 with the Phase B restructure completion (commits `c7f3eeb` → `ae03f80`). Read top-to-bottom for full context, or jump by section.

---

## Session 2026-04-20 — DR-failure diagnosis + prompt hygiene

9 commits landed responding to the Dostoevsky Claude DR failure ("something went wrong" after 90 min / 612 sources on the tailored prompt). HEAD `4dd58c8`, all pushed.

### DR-failure diagnosis

**Symptom**: Dostoevsky tailored DR prompt (50 KB, pasted into claude.ai with Opus 4.7 + Extended Thinking + Deep Research) failed twice with generic "something went wrong" backend error. 90 min wall time, 612 tool-calls / sources accumulated before fail.

**Hypothesis**: tool-call cap exhaustion from compound prompt pressure — (a) `Minimum 15,000 words` floor pushing DR to keep researching, (b) `What this section feeds downstream` blocks leaking Pydantic field names that biased DR toward field-shaped output instead of 6-section dossier, (c) density of named scholars per section triggering recursive verification searches, (d) `Cite every factual claim` + `non-English scholarship` each multiplying tool calls per claim.

612 sources is pathological — scholarly dossiers synthesise from 50-150 sources. The research phase never transitioned to synthesis.

**Mitigations landed (all commits pushed)**:

| Commit | Change | Effect |
|---|---|---|
| `e4d1bd7` | Stripped 24 `What this section feeds downstream` blocks from all 4 pass_0b voice-type templates | Removes Pydantic-field-name leak that biased DR output shape |
| `91b3851` | Dropped `Minimum 15,000 words` from `pass_0b_footer.md` + lowered `dr_validation._TOTAL_WORD_FLOOR` 15000 → 8000 | Removes the signal that pushed DR to keep researching |
| `6ff25b3` | Dropped 3 dead `perplexity_findings` / `gemini_findings` context vars from `run_phase0_1_research.py` base render | Cleanup — Position A → Position C transition artifact, no functional change |
| `a316081` | Stripped `(→ feeds Pass 1.N chunked merge)` header annotations + inline `Feeds X` refs from all 4 pass_1a templates | Extends feeds-downstream strip philosophy to the Perplexity prompts |
| `d073ad4` | Applied the 5 Dostoevsky-validated Pass 1a fixes to organism / system / fictional templates | Closes the "follow-up needed" item; all 4 pass_1a templates now carry the same validated pattern |
| `4dd58c8` | Closed 3 parity gaps: hostile_sources block in organism; recent-reassessments bullet in human + fictional | All 4 pass_1a templates now fully parity-aligned |

Plus infrastructure:

| Commit | Change |
|---|---|
| `3ad1e83` | `CLAUDE.md` top-note documenting the active `phase-b-rebuild` branch state |
| `d3e3647` | Tier 1 gitignore (regenerable per-voice artifacts: `_pass0a_review.md`, `_dr_prompts/`) |

**Regeneration result**: re-ran `run_phase0_1_research.py "Fyodor Dostoevsky"` after the strip + floor-drop landed. Cached Perplexity + Gemini outputs reused (unchanged by template edits); base DR prompt re-rendered against stripped templates (31.8 KB, down from 34.6 KB); Opus 4.7 tailoring pass re-ran (359.8s wall, ~55K input / 19K output tokens, ~$0.50). Produced fresh 43 KB tailored prompt with 12 coverage-note / figure-swap / SWAP-TEST edits. Ready to paste.

**Pending verification**: does the regen resolve the "something went wrong" failure? Third paste pending. If it still fails, fallback options (ordered least-disruptive to most):
1. Paste the base (pre-tailoring) prompt instead — 31.8 KB; fewer named scholars per section.
2. Use the 2-week-old v3.7-spec-paste Dostoevsky card as the Claude DR dossier — place it at `personas/inputs/dossiers/fyodor_dostoevsky_claude_dr.md` and proceed. Loses clean-slate Phase B lineage but unblocks.
3. Modify `chunk_runner.py` to accept a missing DR dossier and 2-source-merge (Perplexity + Gemini). Quality impact real but measurable.

### Item 6 retrospective — "cosmetic, not blocking" was wrong

The 2026-04-19 quality review tagged the `What this section feeds downstream` blocks (later `Item 6 — reframe 'feeds downstream' lines without internal field names`) as **cosmetic, not blocking**. The Dostoevsky DR failure and the 612-source pathological-depth run suggest that assumption was wrong: the pipeline-field-name leaks plausibly steered DR toward field-shaped verification loops rather than a clean 6-section dossier. The strip (both pass_0b and pass_1a) is now done; the retrospective lesson is that **pipeline-internal jargon in LLM-facing prompts is load-bearing unless proven otherwise**.

### Phase L first-voice switch: Plato → Dostoevsky

Original plan (`EXECUTION_PLAN_phase_b.md` §L.8): compare rebuilt Plato against `~/Desktop/AI Assembly/archive/runs/personas/plato/persona_card_assembled.json` as the v3.10 baseline (moved out of the code repo in Tier 3, 2026-04-20). Current plan: Dostoevsky instead, with baseline = 2-week-old persona card the user generated by pasting the v3.7 pipeline spec into claude.ai (saved on user's Desktop, not in repo yet). Rationale: Dostoevsky's tailored DR prompt already exists; starting Plato from scratch costs an additional $10-15 and 20 min of Phase 0.5. Loses direct regression comparison against the v3.10 archived Plato card but keeps the two-week-old v3.7-paste card as a meaningful Phase L baseline. If the Dostoevsky DR completes, the Phase L.8 quality gate becomes: Boddice-shape check (§13 5-part `world`, §14 4-part `formative_experience`, §15 period character-grammar, evidence tags in place, `smoke_test_chains` build-time-only, period-vocabulary-informed-not-displayed Pass 4a) + v3.7-baseline comparison on what Phase B produces differently.

Plato as Phase L is still available if the Dostoevsky run falls through — the v3.10 archived baseline is there.

### Items still carrying forward (from pre-2026-04-20 review)

- **Item 8** (clean panel-voice anchoring from non-human / fictional Pass 0b templates) — ✅ **DONE** via the architectural rewrite (see Session 2026-04-20 evening below). Panel voices (Octopus, Whanganui, Scheherazade) now appear alongside parallel non-panel analogs (corvid/cetacean/primate alternatives for organism; Atrato/Mar Menor/Yurok/Pachamama alternatives for system; Hamlet/Antigone/Aeneas/Anansi alternatives for fictional).
- **Apply the Pass 1a fix to 3 other voice-type templates** — ✅ **DONE** in `d073ad4` + parity closure `4dd58c8`.
- **Tier 1 gitignore** — ✅ **DONE** in `d3e3647`. Dostoevsky voice config + review doc + `_dr_prompts/` no longer pollute git.
- **Item 6** (reframe feeds-downstream lines) — ✅ **DONE** via strip in `e4d1bd7` + `a316081`; retrospective note above.

---

## Session 2026-04-20 (evening) — Pass 0b architectural rewrite

After the morning session's mitigations (strip feeds-downstream, drop 15K floor, soften citation, etc.) still failed to unblock Dostoevsky DR — **including a fourth failed run on Opus 4.6 at 2h22min** — this session executed an architectural rewrite of all 7 pass_0b_*.md prompt files, converting extraction-specs to thematic research questions.

### Diagnosis refined

The prompt shape, not model choice, is the cause. Four Dostoevsky DR failures across both 4.7 and 4.6 isolated:

| Run | Prompt | Model | Runway | Result |
|---|---|---|---|---|
| 1 | Tailored old (50 KB) | 4.7 | ~90 min | fail |
| 2 | Same, retry | 4.7 | ~90 min | fail |
| 3 | Tailored stripped + no floor (43 KB) | 4.7 | 2h 16min | fail |
| 4 | Untailored base (31.8 KB) | 4.7 | 1h 30min | fail |
| 5 | Base | 4.6 | 2h 22min | fail |
| 6 | Tailored | 4.6 | (time missed) | fail |

Meanwhile: my Desktop meta-research DR prompt (~3200 tokens, thematic questions, no quotas, 3-tag) succeeded on Opus 4.7 at 37 min / 640 sources. And user's v3.5 mock runs on 4.6 succeeded across Ibn Battuta / Marley / Octopus / Fyodor (15–87 min / 538–1046 sources). Source count is not the failure signature; task framing is. Extraction-specs with quotas create unbounded-satisfiability criteria; thematic research questions have tractable finish-lines.

### Rewrite landed (all 7 files)

| File | Before | After | Change |
|---|---|---|---|
| `pass_0b_header.md` | 50 lines | 33 lines | Added synthesis-trigger + gap-permission + empirical runtime expectation (20–90 min, cancel at 2h); dropped tool-call-budget anchor; 2-tag in-prose citation discipline |
| `pass_0b_footer.md` | 27 lines | 39 lines | Softened OUTPUT FORMAT; hostile-source block reshaped to prose-level guidance (scholars named in prose; merge applies tags); musical-voice block reconciled with ReferenceOnlyPassages two-tier corpus design |
| `pass_0b_human.md` | 242 lines | 148 lines | 6 thematic-area questions; no quotas; no embedded framework lexicons as bulleted output demands; SWAP TEST once in §4 |
| `pass_0b_non_human_organism.md` | 227 lines | 147 lines | Same transformation + panel-voice analogs (corvid / cetacean / primate alongside cephalopod exemplars) |
| `pass_0b_non_human_system.md` | 227 lines | 185 lines | Same transformation + parallel analogs (Atrato / Mar Menor / Yurok / Pachamama alongside Whanganui); **Indigenous Representation Ethical Framing preserved verbatim as load-bearing ethical commitment** |
| `pass_0b_fictional.md` | 226 lines | 180 lines | Same transformation + parallel analogs (Hamlet / Antigone / Aeneas / Anansi / Sun Wukong alongside Scheherazade); **Narrative-Function Framing preserved verbatim** |
| `pass_0b_tailor.md` | 203 lines | 166 lines | Structural shape flip: coverage-notes ("Research-to-date + Go DEEPER on") → targeted-follow-up-questions (2–3 specific follow-ups per section anchored to gaps Perplexity + Gemini left unresolved); optional SWAP TEST anchor customization per voice; 0–2 scholars per question cap |

Rendered prompt size for human voice (Dostoevsky): ~4,900 tokens, down from ~10,500 (-53%).

### What was preserved

All 37 Card v2 fields supported. All Pass 1.1–1.6 schemas (LifeScaffold / Commitment / Concept / Tension / ReasoningMethod / Textures / Moves / Register / Vocabulary / KnowledgeBoundary / SensitiveTopic / HardLimits / WorkEntry / Passage / URLEntry / ReferenceOnlyPassages) have corresponding research content in the reshaped thematic questions. Boddice §13 5-part world + §14 4-part formative + §15 character-grammar preserved as research material (structure extracted at Pass 1.1 merge, applied at Pass 2 synthesis). All locked PB decisions (PB#1 3-sources-only, PB#2 Position C, PB#7 frozen 5-tag conventions, PB#9 OUTPUT FORMAT softening) honored. No architectural changes; no schema changes; no new passes.

### Phase L Run 7 — decision framework

Run 7 (Dostoevsky on the rewritten prompts) has three possible outcomes:

1. **Fails again.** Prompt-shape diagnosis was insufficient. Fall through to existing OPEN_ITEMS fallback ladder: option 2 (paste v3.7-spec card as DR dossier and proceed through Pass 1.1–1.7 merge); option 3 (modify `chunk_runner.py` for 2-source merge — Perplexity + Gemini only).

2. **Completes but Phase L.8 card only marginally better than v3.5 mock.** Phase B functionally vindicated but not transformatively. At this point genuine decision: continue Phase B for 11 more voices (50+ hours) or adopt v3.5-style for speed and spend the saved time on Voice Pipeline + microsite + closing show (all critical-path, not redundant with card production).

3. **Completes and Phase L.8 card dramatically better than v3.5 mock.** Phase B vindicated. Continue all 12 voices.

Honest estimate: Run 7 DR completion probability 50–65%. Outcome 2 is the most likely Phase L.8 result if Run 7 completes. The Phase L.8 quality gate IS the decision point on whether Phase B's complexity justifies its cost for Athens delivery.

### Deferred for Phase L execution

- **Fresh test project for Run 7:** new PROJECT_ROOT (e.g. `projects/phase-l-dostoevsky/`) separate from the existing `projects/test/` (which contains the failed-run cache). Fresh Perplexity + Gemini + Pass 0b render + tailoring.
- **Phase L.8 comparison protocol:** explicit comparison of the rebuilt Dostoevsky card against the 2-week-old v3.7-spec-paste card (on user's Desktop). Checks per `EXECUTION_PLAN_phase_b.md §L.8` plus the "is the delta dramatic or marginal?" question.
- **v3.5-style fallback architecture:** if Phase L.8 shows only marginal improvement, rough sketch of how to run v3.5-style for remaining voices while keeping Phase B's Pass 7-* validation passes running as QA on those cards.

---

## Session 2026-04-20 (late evening) — Run 7 outcome: multi-session empirically validated

### The failure of single-session DR on the rewritten prompts

Dostoevsky was re-run on fresh `projects/phase-l-dostoevsky/` with the rewritten prompts:

| Run | Prompt | Model | Runway | Sources | Result |
|---|---|---|---|---|---|
| 7-T-46 | Tailored (rewritten) | Opus 4.6 | 1h 30m | **~4,000** | fail |
| 7-T-47 | Tailored (rewritten) | Opus 4.7 | 1h 30m | (not counted) | fail |
| 7-B-47 | Untailored base | Opus 4.7 | (user moved past) | — | fail |

**4,000 sources is 7× higher than prior failing runs (~600).** The rewrite widened DR's research surface rather than narrowing it. Every exemplar list item in prose questions (Forms / jinn / whakapapa / res cogitans / Newtonian universe / kenotic Christ; humours / tripartite / nafs / Rasta / śīla / Confucian; Socrates / Nietzsche / Wittgenstein; Maiorova / McReynolds / Marullo; translator names; etc.) became a research dimension DR pursued. Plus 18 tailored follow-up questions × 2-3 scholars each. Total demand surface ≈ ~100 dimensions. Convergence trap from demand-volume, not from shape.

**Previous diagnosis partially wrong.** I had claimed extraction-spec-vs-thematic-question was the lever. The rewrite's content is fine — both models honor thematic questions, `[quote:]` / `[~uncertain]` markers, and citation discipline. The SCALE of simultaneous demands was the killer.

### The empirical breakthrough

User manually extracted Section 1 from the rewritten tailored prompt and pasted just that section (with header, without footer — see "user forgot footer" item) into fresh claude.ai threads for both models.

**Both models completed Section 1 in ~33 min** with substantive, cited, voice-specific narrative. Outputs saved:
- `~/Desktop/dosto_brief+section1_opus4.7.md` — ~3,700 words, thesis-driven prose ("kenotic Orthodox realist"), tighter argumentation
- `~/Desktop/dosto_brief+section1_opus4.6.md` — ~6,400 words, cataloguing register, more period vocabulary glossed, more `[~uncertain]` markers honored

This empirically validates meta-research §6.3 multi-session decomposition prescription. Per-section demand surface ≈ 15 dimensions — within DR's tractable envelope. Both 4.6 and 4.7 complete reliably at ~30 min per section.

### Model recommendation for the pipeline

**Default to Opus 4.6 for all 6 sections.** More extractable material (~17 period-vocabulary terms with glosses vs. ~10 in 4.7), more `FormativeCandidate` candidates explicitly framed (Mariinsky Hospital / Semyonov Square / Omsk katorga / Holbein encounter / Alyosha's death / Optina pilgrimage), more `anachronisms_to_avoid` explicitly tagged, more `[~uncertain]` discipline honored. Downstream Pass 1.1–1.6 merge extracts structured fields from the prose — material density matters more than rhetorical tightness. 4.7 is the better standalone read but starves the merge.

Alternative: run both models per section in parallel (same 30-min window, same effort), cherry-pick better output per-section. Best quality ceiling; minor operational overhead.

### Running Dostoevsky to completion (immediate operational path)

User is mid-flight. Continue manually:

1. Extract each remaining section (§2, §3, §4, §5, §6) from `projects/phase-l-dostoevsky/inputs/dossiers/_dr_prompts/fyodor_dostoevsky_dr_prompt.md`
2. For each section: paste `pass_0b_header.md` content + that single section + `pass_0b_footer.md` content into fresh claude.ai thread
3. Model: Opus 4.6 + Extended Thinking + Deep Research ON
4. Wait ~30 min per section. Parallelize via multiple tabs (up to 5 simultaneous sections).
5. Save each output to Desktop as `dosto_brief+sectionN.md` (or similar)

When all 6 sections are in hand:

```bash
PROJ="/Users/aienvironment/Desktop/AI Assembly/projects/phase-l-dostoevsky"
RUN="$PROJ/runs/fyodor_dostoevsky/01_research"
mkdir -p "$RUN"
# Concatenate (order matters for clean read; Pass 1.1-1.6 merge doesn't enforce strict headings)
cat "$HOME/Desktop/dosto_brief+section1.md" \
    "$HOME/Desktop/dosto_brief+section2.md" \
    "$HOME/Desktop/dosto_brief+section3.md" \
    "$HOME/Desktop/dosto_brief+section4.md" \
    "$HOME/Desktop/dosto_brief+section5.md" \
    "$HOME/Desktop/dosto_brief+section6.md" > "$RUN/claude_dr_dossier.md"
cp "$RUN/claude_dr_dossier.md" "$PROJ/inputs/dossiers/fyodor_dostoevsky_claude_dr.md"
cd "/Users/aienvironment/Desktop/AI Assembly/code/personas"
venv/bin/python run_persona_pipeline.py "Fyodor Dostoevsky" --project "$PROJ"
```

Expected: Pass 1.1–1.6 merge ~3-6 min (parallel chunks); Pass 2-6 generation ~45-60 min; Pass 7 validation + Derive ~15-20 min. Total wall ~60-90 min. Cost ~$30-40.

### ✅ SHIPPED (2026-04-21) — Pending code changes — ship multi-session support properly

All 5 items below shipped in Phase B restructure session (commits `c7f3eeb`→`ae03f80`).
For the full change log see `_workspace/planning/SONNET_PHASE_B_RESTRUCTURE_TEST_REPORT.md`.

For voices 2-12 (and for robust single-command pipeline invocation on all 12), these changes were shipped after Phase L Dostoevsky §1–§2 (and §3–§4) validated the manual path:

1. **New helper `personas/scripts/split_tailored_prompt.py`** — reads the tailored monolithic `<slug>_dr_prompt.md`, parses section headings, writes 6 per-section prompt files at `inputs/dossiers/_dr_prompts/<slug>_section{1..6}_dr_prompt.md` each containing header + one section + footer. ~30 min to implement.

2. **`run_phase0_1_research.py`** — after tailoring completes, automatically invoke the split helper. User then sees 6 prompts instead of 1. Update the stale "60-180 min" NEXT STEPS hardcode to "20-90 min per section, 6 sections in parallel or sequential." ~20 min.

3. **`chunk_runner.py` line 75** — change DR load from single file to per-chunk per-section: `dr_path = research / f"claude_dr_section_{chunk_num}.md"`. Fall back to monolithic `claude_dr_dossier.md` if per-section files absent (backward compat with v3.5-style single-dossier runs). ~15 min.

4. **`run_persona_pipeline.py`** — pre-check: all 6 section files present at `inputs/dossiers/<slug>_section{1..6}.md` OR single `<slug>_claude_dr.md` present. Copy to `runs/<slug>/01_research/` per-section. ~20 min.

5. **`dr_validation.py`** — accept either a directory of 6 section files OR a single monolithic dossier. Validate each section independently against the 8K-word floor (adjusted per-section: ~1,500 words per section minimum). ~15 min.

Total: ~100 min of coding + testing on the completed Dostoevsky outputs. Defer until Phase L Dostoevsky completes so the manual path validates everything first.

### Smaller items flagged this session

- **Stale "Wait 60-180 min" hardcode** in `run_phase0_1_research.py` NEXT STEPS print output. Doesn't match the rewritten header's empirical 20-90 min envelope. Cleanup with #2 above.
- **Path mismatch**: `run_persona_pipeline.py` reads from `inputs/dossiers/<slug>_claude_dr.md`; `chunk_runner.py` expects `runs/<slug>/01_research/claude_dr_dossier.md`. Operational `cp` required between them, or pipeline should handle automatically. Documented here; fix with #4 above.
- **Missing footer on Section 1 of Run 7 manual attempt**: user forgot to paste `pass_0b_footer.md` content. No harm done — header carries most of the same discipline (citation per-paragraph, `[quote:]` + `[~uncertain]` markers). Both Section 1 outputs honored the discipline anyway. Future pastes should include footer for reinforcement.

### Sequential-same-thread vs. parallel-separate-threads

User asked whether 6 DR sessions in one thread would help coherence. Answered: marginal upside (DR sees prior section outputs → cross-section consistency at DR level), real downside (thread context accumulation → 200K-per-agent ceiling gets pressured by §4-5, risking return to convergence trap). Pass 1.7 coherence pass is designed to do the cross-section reconciliation downstream. Recommendation: separate threads, parallelizable, localized failures. Optional middle ground: 3 threads × 2 sections each, paired by thematic coherence (§1+§2 biographical+intellectual; §3+§4 reasoning+voice; §5+§6 boundaries+corpus).

### Phase L.8 quality gate (unchanged, still pending)

When the pipeline completes Dostoevsky, compare the assembled card to the 2-week-old v3.7-spec-paste Dostoevsky card on the user's Desktop. Three outcomes (per earlier session's decision framework): dramatic improvement → continue all 12 voices; marginal improvement → reconsider Phase B scope vs. v3.5-style for remaining voices; regression → iterate further or revert.

---

## CRITICAL — do before Phase L Plato run

### Code / project separation (Tier 3)

**Problem**: the codebase currently conflates code with project-specific data. `personas/inputs/conference_facts.json`, `personas/inputs/audience_profile.json`, `personas/inputs/panel_roster.json`, `personas/inputs/non_human_grounding/`, and `personas/inputs/voices/<slug>.json` all describe Athens 2026 specifically. `personas/runs/<slug>/...` also lives inside the code repo (gitignored, but still file-system-coupled). Per-voice runtime artifacts (review docs, DR prompts, tailoring notes) are tracked, polluting the repo on every test run.

**Right architecture**: code/project separation with `PROJECT_ROOT` distinct from the code repo.

```
ai-assembly/                    # CODE REPO (in git)
├── personas/
│   ├── flows/                  # Code
│   ├── schemas/                # Code
│   ├── run_*.py                # Code
│   └── flows/shared/prompts/   # Prompt templates
├── runtime/                    # Code
└── tests/fixtures/             # Pinned test fixtures (code-level)

athens-2026/                    # PROJECT DATA (separate dir, possibly own git repo or VM-mounted volume)
├── inputs/
│   ├── conference_facts.json
│   ├── audience_profile.json
│   ├── panel_roster.json
│   ├── non_human_grounding/
│   └── voices/<slug>.json      # curator-edited
├── runs/<slug>/                # All pipeline runtime outputs
└── dossiers/<slug>_claude_dr.md
```

Runners take `--project /path/to/athens-2026/` or read env `AI_ASSEMBLY_PROJECT_ROOT`. Default = `./project/` in cwd, or whatever convention.

**Three tiers**:

| Tier | What | Cost | Status |
|---|---|---|---|
| 1 | Gitignore regenerable bits (review docs, DR prompts, tailoring notes). Voice configs stay tracked. | 5 min | **Probably do before Dostoevsky test run** |
| 2 | Move all runtime outputs to `personas/_generated/` (single gitignored hierarchy). | ~30–45 min | Skip — superseded by Tier 3 |
| 3 | Extract `PROJECT_ROOT` from code repo. All project data lives outside the code repo. Runners take `--project`. | ~2 hours | **Do this before Phase L Plato run** — Plato will produce a real persona card you'll want clean separation for |

**Tier 3 implementation checklist** — ✅ **LANDED 2026-04-20** (full umbrella + both pipelines):

**Filesystem (umbrella restructure):**
- ✅ Moved `~/Desktop/ai-assembly/` → `~/Desktop/AI Assembly/code/`
- ✅ Moved `~/Desktop/athens-2026/` → `~/Desktop/AI Assembly/projects/athens-2026/`
- ✅ Created `~/Desktop/AI Assembly/projects/test/` with baseline project context copied from Athens.
- ✅ Split Dostoevsky (in-progress voice, runs, DR prompts) out of athens-2026 into test/ so production stays clean.

**Personas pipeline:**
- ✅ `flows/shared/project_root.py` — precedence: `--project` → `AI_ASSEMBLY_PROJECT_ROOT` env → **hard failure** (no silent default; multiple projects make fallback dangerous).
- ✅ All 13 runners updated (0a, 0b standalone, 0b tailor, Phase 0.5, 1.1-1.7, 1_all, persona_pipeline, phase_5_qc).
- ✅ `chunk_runner.py` takes both `repo_root` (test fixtures) and `project_root` (live runs).
- ✅ `io.py::load_voice_input` takes `project_root`.

**Runtime pipeline:**
- ✅ `flows/shared/project_root.py` — same module, copied per venv isolation.
- ✅ `ingest/config.py` resolves `PROJECT_ROOT` after `load_dotenv`; `RUNS_DIR` / `REFERENCE_DIR` / `SESSIONS_PATH` / `SPEAKERS_PATH` derived from it.
- ✅ `flows/shared/io.py::load_council_config` defaults to `$PROJECT_ROOT/council_config.json`.
- ✅ `scripts/generate_sessions_json.py` + `generate_speakers_json.py` defaults to `$PROJECT_ROOT/reference/*.json`.
- ✅ `INGEST_FLOW_CMD` uses `shlex.join` so paths with spaces (e.g. "AI Assembly") survive `shlex.split` in pipeline.py.

**Config / secrets:**
- ✅ `.env` at `code/.env` (zero dotenv code change).
- ✅ `AI_ASSEMBLY_PROJECT_ROOT` set in `.env` to `projects/test` — bare invocations land in test; pass `--project` for athens-2026.

**Hygiene:**
- ✅ `.gitignore` cleaned (personas + runtime). All moved tracked files staged as deletions.
- ✅ 29/29 runtime tests pass; personas smoke tests (import + resolver + voice load + prompt render) pass from both test and athens-2026 projects.

**Docs updated:** `CLAUDE.md`, `runtime/README.md`, `personas/README.md`, `docs/CURRENT_STATE.md`, `EXECUTION_PLAN_phase_b.md`, `docs/AUDIENCE_BRIEF.md`.

**Enables**: multiple projects on one codebase (test + athens-2026 today; berlin-2027 etc. later); VM-friendly deployment (mount a project volume, point env var at it); trivially isolated test runs; git-clean by definition; curator/operator role separation; cross-pipeline handoff via shared PROJECT_ROOT.

---

## Walkthrough still in progress

User asked for a step-by-step walkthrough of the 25-pass pipeline. Steps 1–5 covered:

1. ✅ Pass 0a (voice config) — covered with full architecture
2. ✅ Pass 1a (Perplexity sonar-deep-research) — covered
3. ✅ Pass 1b (Gemini broad scan) — covered
4. ✅ Pass 0b base render + tailoring — covered (including Position C correction)
5. ✅ Pass 1a-DR (manual claude.ai session) — covered

Remaining steps:

6. Pass 1.1 BIOGRAPHICAL chunked merge
7. Pass 1.2 INTELLECTUAL
8. Pass 1.3 REASONING
9. Pass 1.4 VOICE
10. Pass 1.5 BOUNDARIES
11. Pass 1.6 CORPUS (including the two-tier `reference_only_passages`)
12. Pass 1.7 COHERENCE
13. Pass 2 (Identity & Boundaries)
14. Pass 3 (Intellectual Core)
15. Pass 4a (Voice)
16. Pass 4b (Artifact)
17. Pass 5 (Engagement)
18. Pass 6 (Corpus Curation)
19. Pass 7-pre (Citation Verification + Boddice tag check)
20. Pass 7-anachronism (TimeChara-style)
21. Pass 7a (Cross-Model Validation)
22. Pass 7b (Card Smoke Test — `smoke_test_chains`)
23. Pass 7c (Negative Constraints — `banned_language` + `projection_warnings`)
24. Phase 4 Derive (Provocateur Profile + Evaluation Rubric)
25. Phase 5 Cross-Persona QC

User can resume this in any future session. The pattern of each step is: name + phase + cost + wall-time + model + why-it's-there + input + what-happens + output + anything-else.

---

## Phase L — first-voice Plato test (gated, ~$50–70)

Per `EXECUTION_PLAN_phase_b.md`. The single explicit stop-and-ask trigger from the original plan. Requires:

- ~$50–70 across Pass 0a + Phase 0.5 + chunked Pass 1 + Pass 2–6 + Pass 7.x + Derive
- Manual human-in-the-loop step at L.3 (paste tailored DR prompt into claude.ai, wait 30–60 min, save dossier)
- Manual quality review at L.8 against `~/Desktop/AI Assembly/archive/runs/personas/plato/persona_card_assembled.json` baseline (umbrella-level archive dir, moved in Tier 3)

**Should land AFTER Tier 3 architecture work** — Plato is the first real Phase B persona card; clean code/project separation matters more for it than for Dostoevsky test runs.

---

## Phase M — verify + push + PR (gated on L passing)

Per `EXECUTION_PLAN_phase_b.md`. Final verification + GitHub PR. Already mostly green (29/29 runtime tests + clean stale-ref greps as of HEAD), but should re-verify post-L.

---

## Pass 1a Perplexity prompt revision — commit `6ad03d1` (2026-04-19 23:30)

**Diagnosis** from two consecutive Dostoevsky test runs: Perplexity sonar-deep-research returned 3,265 words then 1,258 words (floor 8,000; well-documented voices 15-30K). For one of the most-documented figures in Russian literary history, that's a prompt-side issue, not a Perplexity-tier issue.

**Five fixes shipped in `persona_pass_1a_human.md`**:

1. **Explicit length target** at top of prompt: "minimum 15,000 words total; each section 2,000+ words." Brevity defeats the downstream synthesis pipeline.
2. **Exact section heading format** specified: `## 1. BIOGRAPHICAL FOUNDATION`, `## 2. INTELLECTUAL FRAMEWORK`, etc. The downstream `perplexity_split` parser depends on this exact format. Previous "organise findings under these six headings" let Perplexity invent variations — that's why we kept seeing "WARN: Perplexity output could not be split by section — falling back to single-block scaffolding".
3. **Non-English scholarship load-bearing block**: Russian for Russian writers (Бахтин / Касаткина / Лотман); Arabic for Islamic figures; Sanskrit/Pali for Buddhist; Spanish for Latin American; etc. Cite scholars in original-language transliteration. Documented sonar-deep-research failure mode is Anglophone-only default.
4. **Depth-not-breadth framing**: better to do §1/3/6 thoroughly than all six shallowly.
5. **Softened tag asks**: previous prompt asked Perplexity to apply 5 Boddice tags — heavy structural ask Perplexity has no canonical training on. Pass 1a now asks for `[primary]`/`[consensus]`/`[contested]` only, with substance + sources as priority. Tag rigor moved to chunked merge prompts (Opus reads, can apply).

**Plus**: moved "cite all claims" instruction upfront; added pochvennichestvo-equivalent specificity bullet in §2; per-section word targets (2,500 / 2,500 / 2,000 / 1,500 / 2,000 / 2,000).

**Follow-up needed**: same fixes likely needed for `persona_pass_1a_non_human_organism.md`, `_non_human_system.md`, `_fictional.md`. Defer until human-template revision is validated by a clean Dostoevsky run. ~20 min per template if human-template fix proves out.

**Validation result (2026-04-19 23:20)**: ✅ ALL FOUR signals passed on the Dostoevsky re-run:
- Perplexity word count: **15,325 words** (vs prior 1,258 / 3,265; floor 8,000; target 15-30K). 113K chars total.
- `perplexity_split` succeeds: 6 sections cleanly split (30K / 17K / 15K / 12K / 12K / 22K chars).
- Period vocabulary surfaced: 362 non-ASCII Cyrillic chars + 22 gloss markers.
- Evidence tags: 17 tags emitted (lighter `[primary]/[consensus]/[contested]` set, as the new prompt asks for).

The fix is validated. **Apply the same pattern to the 3 other voice-type templates** (`persona_pass_1a_non_human_organism.md`, `_non_human_system.md`, `_fictional.md`) — should be ~20 min per template. Same five fixes: explicit length floor, exact `## N. SECTION_NAME` heading format, non-English scholarship load-bearing block, depth-not-breadth framing, softened tag set.

## Two follow-up parser/validator fixes — commit `062d47a` (2026-04-19 23:25)

The first successful Dostoevsky run (17K-word Perplexity dossier, post-prompt-fix) surfaced two downstream catch-up bugs:

1. **`perplexity_split.py` §5 regex**: the new prompt ships `## 5. HISTORICAL + CONCEPTUAL BOUNDARIES` (more accurate than the legacy `HISTORICAL BOUNDARIES`). The "+ CONCEPTUAL" infix broke the regex's word-boundary anchor; §5 wasn't recognized; full split failed. Fixed by accepting optional `+ CONCEPTUAL` infix.
2. **`research_validation.py` evidence-tag regex**: smoke-test was checking for the OLD 5-Boddice-tag set; new Pass 1a prompt asks Perplexity for `[primary]/[consensus]/[contested]` only. False-positive `evidence_tags: 0` warning. Updated regex to accept BOTH tag families.

Both fixes verified against the actual Dostoevsky dossier — split now finds 6 sections cleanly, smoke-test now 4/4 pass.

---

## Dostoevsky test run (operator action)

Voice configs cleared from prior aborted run. Tree clean. To run:

```bash
cd /Users/aienvironment/Desktop/ai-assembly/personas
venv/bin/python run_pass0a_voice_config.py "Fyodor Dostoevsky" \
    --wiki https://en.wikipedia.org/wiki/Fyodor_Dostoevsky
# read review doc; leave editorial_rationale: null
venv/bin/python run_phase0_1_research.py "Fyodor Dostoevsky"
# tailored DR prompt at inputs/dossiers/_dr_prompts/fyodor_dostoevsky_dr_prompt.md
# paste into claude.ai (Opus 4.7 + Extended Thinking + Deep Research)
```

Cost ~$12–20. Wall ~10–20 min for Phase 0.5 + 30–60 min wait for claude.ai DR.

**Purpose**: compare the resulting Claude DR dossier against whatever the user got when they pasted the v3.7 pipeline spec into claude.ai. Tests whether the Position C tailored prompt produces meaningfully better DR output.

**If you do Tier 1 first**: review docs + DR prompts won't pollute git. Recommended.

---

## Deferred items from today's quality review

Five mechanical fixes landed in commit `7458d9d`. Two deferred:

### Item 6 — reframe "feeds downstream" lines without internal field names

Each section opens with `- world (...)` `- formative_experience (...)` etc. — internal Pydantic field names DR doesn't need to see. Could be reframed as plain English. ~30 min. Cosmetic; not blocking.

### Item 8 — clean non-human/fictional templates of panel-voice anchoring

`pass_0b_non_human_organism.md` uses Octopus + Hochner + Godfrey-Smith + Mather as worked examples (22 mentions). `pass_0b_non_human_system.md` uses Whanganui + Te Pou Tupua + iwi-specific scholars (22 mentions). `pass_0b_fictional.md` uses Scheherazade extensively (20 mentions).

Self-anchoring is harmless as long as the panel stays at 12. If the panel ever expands to add a second non-human-organism / non-human-system / fictional voice, those new voices' DR runs would be subtly anchored to the existing panel voice. ~1 hour to swap each panel-voice example for a parallel non-panel exemplar.

---

## Smaller improvements (non-blocking)

### Perplexity retry: retry-twice instead of retry-once

`flows/shared/research_validation.py` and `_with_retry()` in `run_phase0_1_research.py` give one retry. Two retries with exponential backoff (15s, 60s) would catch more transient failures. ~10 min.

### ✅ SHIPPED (phase H, commit `5087939`) — `perplexity_split.split_dossier()` per-section fallback

REBUILD_PLAN flagged: today's all-or-nothing returns `None` if any one of the 6 section headings fails to match. Should recover per-section and warn loudly on the missing ones. ~20 min.

### ✅ SHIPPED (phase L, commit `0a3945a`) — `_manifest.json` per-pass cost telemetry

Decisions log #4: "No cost cap; quality-first. Track per-pass cost in `_manifest.json` retrospectively but no alarms." Implemented in phase L: `flows/shared/manifest.py` + all 4 client wrappers record telemetry to `voices/<slug>/_manifest.json`. ~30 min — wrap each `call_claude` / `call_perplexity` / `call_gemini` / `call_openai` to append usage to a per-voice manifest. Useful for actual cost analysis after a few real voice runs.

### Runtime enforcement of `reference_only_passages` Step 1/Step 2 contract

The two-tier corpus design (Marley lyrics in private reasoning only) is documented in `personas/HANDOFF.md`. The runtime Voice Pipeline Step 2 assembly code MUST drop the field before rendering. The runtime Voice Pipeline doesn't exist yet (out of scope per REBUILD_PLAN — separate workstream). When that workstream starts, this contract needs to land in code, not just docs.

### MergedDossier.register / voice_register Pydantic alias verification

Cleanup-deferral-B fixed the Pydantic warning by renaming the attribute to `voice_register` with `alias="register"` + `populate_by_name=True` + `serialization_alias="register"`. The primary site (`run_pass_1_7.py` → `model_dump(by_alias=True)`) is updated. Not audited across all consumers. Low probability of breakage but worth verifying if Pass 1.7 ever produces unexpected output.

### Dead Pass 1-merge prompts already removed

Cleanup-deferral-C removed `persona_pass_1merge_contradiction_system.md` + `persona_pass_1merge_three_way_user.md` + `persona_pass_1c_extract_urls.md`. They're in git history if resurrection is ever needed.

---

## Lessons learned (architectural insights from this session)

For a fresh session reading this doc cold, these inform how the prompts were designed:

### Position C: DR prompt does NOT inline Perplexity + Gemini

We considered three architectures for the DR prompt:
- **A**: Inline Perplexity + Gemini in full (the v3.10 / original PB#2 design; ~120 KB tailored prompt). Problem: lost-in-the-middle on the Boddice asks; anchoring DR to Perplexity's frame; degraded triangulation at merge.
- **B**: Compact pointer notes summarizing coverage. Better but tailoring LLM has to do harder synthesis.
- **C** (chosen): DR prompt has 6 placeholders; tailoring LLM (Opus 4.7) reads Perplexity + Gemini + voice_config and writes 2–6-sentence coverage notes per section. DR sees only the synthesized notes, not the raw research. Keeps three sources independent for genuine cross-source triangulation at Pass 1.1–1.7 merge. Matches baseline File 2's "compressed summaries > full text" recommendation.

### Tailoring ALWAYS runs (not gated on editorial_rationale)

Per REBUILD_PLAN PB#2 "replaces pure Jinja". Earlier cleanup-3 incorrectly gated the whole tailoring pass on `editorial_rationale` being non-null. Fixed in cleanup-7. Now tailoring fires for every voice; `editorial_rationale` is an optional fourth signal (thematic note injection), not the trigger.

### Boddice / Rosenwein / Bradshaw / van der Kolk attributions stripped from base DR prompts

Claude DR doesn't need to know we're using Boddice's framework. The asks (4-part formative rubric, period character-grammar, overlapping communities, [experiential_reconstruction] tags) are preserved verbatim; the scholar-attributions are dropped. Internal scaffolding (the tailoring LLM's system prompt) keeps the attributions for Opus's contextual understanding.

### Negative-prompt strips ("don't think of pink elephant")

Removed: "Drop the 'core wound + lesson' framing" and "Do NOT use Big-Five-adjacent adjectives" — by naming the thing-to-avoid we plant the frame in DR's attention. Kept the positive instructions ("use the voice's own framework — Buddhist dukkha, Islamic ibtilā', etc." and the period-character-grammar list) which do the work without anchoring DR on what to avoid.

### Pipeline-leak strips

Removed `NOTE: ...AI-default failure modes is NOT your job. That happens downstream in Pass 7c...` paragraphs from Section 4 + Section 5 of all 4 templates. DR doesn't need to know our internal pass naming. The positive instruction (scholarly anti-patterns only) remains.

### Unified evidence-tag convention (today's commit)

Across 4 voice-type templates + footer, at least 5 different tag schemes existed (`[paraphrased from scholarly consensus]` / `[hostile source]` / `[stated in text]` / `[attributed by narrative function]` / etc.). Chunked merge expects exactly the 5 frozen `EvidenceTag` values from `personas/schemas/_conventions.py`: `stated`, `scholarly_consensus`, `inference`, `experiential_reconstruction`, `projection_warning`. All templates now reference the canonical 5 + 3 hostile-source addenda.

### Three missing card-field asks added

`unique_contribution`, `stance_tendency`, `aesthetic_qualities` — all three card fields had no explicit prompt asks. Now have explicit bullets in §1 / §4 across all 4 voice-type templates.

---

## Recommended next-session order

1. **Tier 1** (5 min): gitignore the regenerable per-voice artifacts. Eliminates immediate pollution risk.
2. **Apply Pass 1a fix to the other 3 voice-type templates** (~20 min each = ~1 hr total). Pattern validated by Dostoevsky run; same five fixes (length floor + exact heading format + non-English scholarship + depth-not-breadth + softer tag set) needed for `_non_human_organism.md`, `_non_human_system.md`, `_fictional.md`.
3. **Tier 3** (~2 hours): code/project separation. Right architecture for Phase L + multi-project + VM deployment.
4. **Phase L** (~$50–70, ~2–4 hours including manual paste + L.8 quality review): first-voice Plato rebuild. Plato is human-type, so already benefits from the validated Pass 1a fix.
5. **Phase M** (~30 min): verify + push + open PR.

Optional in any order: walkthrough remaining steps (6–25), deferred items 6 + 8, smaller improvements.

**Note**: the Dostoevsky test run is mid-flight as of HEAD `062d47a` — the tailoring Opus call started at 23:20:49. When it completes, the operator will compare the resulting Position C tailored DR prompt against the v3.7-spec-upload baseline. If the comparison shows Position C wins on the architectural axes (6-section structure, period-vocabulary, formative candidates, evidence tags, Russian scholarship), the Pass 1a + Position C combination is fully validated.

---

## Where this session ended

- 33 commits on `phase-b-rebuild`, all pushed (HEAD `062d47a`)
- Tree clean (no uncommitted work)
- Dostoevsky test run mid-flight: Pass 1a + 1b complete (15K-word Perplexity dossier ✓ all 4 smoke-tests pass after follow-up fixes); Pass 0b base render complete (34K chars); Pass 0b tailoring Opus call in progress
- 29/29 runtime tests green
- M.3 stale-ref greps clean
- All Boddice / Rosenwein / negative-prompt / pipeline-leak / scholar-attribution patterns stripped from base DR prompts
- Tag conventions unified (5 Boddice tags in chunked merge; 3 lighter tags in Pass 1a Perplexity)
- 3 missing field asks added (unique_contribution / stance_tendency / aesthetic_qualities)
- Position C architecture in place + tailoring fires unconditionally
- **Pass 1a Perplexity prompt rewritten + VALIDATED on Dostoevsky** (commit `6ad03d1`); two parser/validator catch-up fixes shipped (commit `062d47a`)

**Pass 1a fix pattern proven; 3 other voice-type templates still need the same treatment** (organism / system / fictional). Estimated ~20 min per template.

Next operator action when this session resumes:
1. Confirm tailoring completed and the tailored DR prompt is rich (compare to first-run-tailoring-notes.json)
2. Paste tailored prompt into claude.ai for Position C vs v3.7 baseline comparison
3. Apply Pass 1a pattern to the other 3 voice-type templates

---

## Code-cleanup-on-fresh-project (no retroactive migration)

Items to fix when a clean PROJECT_ROOT is set up from final code, **not** worth migrating existing test / phase-l-dostoevsky / athens-2026 projects for. Apply when bootstrapping the next project from final code.

### CC#1 — Move `05_primary_text_urls.json` out of `01_research/`

**Current path:** `voices/<slug>/01_research/05_primary_text_urls.json`
**Better path:** `voices/<slug>/03_corpus/00_primary_text_urls.json`

**Why current location is wrong:** historical-layout vestige. In v3.10 the URL list came directly from Perplexity research (true research artifact). 1-arch-07 (2026-04-22) changed the source — URLs are now derived post-merge from `02_merge/pass_1_6/works.json` + `passages.json` via `extract_urls()` ([run_persona_pipeline.py:271-288](personas/run_persona_pipeline.py:271)). The destination path was kept for backward-compat, but the file is no longer a research output. It's the input to corpus fetch, so it belongs alongside `03_corpus/01_primary_texts.json`.

**Why not migrate now:** path API change with cross-project ripple (test, phase-l-dostoevsky, athens-2026 all carry the file in the old location). Cosmetic, not functional. No code reads from a hard-coded path — everything goes through `_paths.primary_text_urls(...)`, so the change is one line in [paths.py:69-71](personas/flows/shared/paths.py:69) plus a directory move on fresh project setup.

**When to apply:** at fresh-project bootstrap of the next voice-set after Phase L sign-off. Update [paths.py:71](personas/flows/shared/paths.py:71): `research_dir(...)` → `corpus_dir(...)` and `"05_primary_text_urls.json"` → `"00_primary_text_urls.json"` (numbered to sort before `01_primary_texts.json`).

**Discovered:** 2026-04-23 during arch-03 Stage 2 restart, reading paths.py with the operator.
4. Tier 3 + Phase L
