# Consolidation method: every tracker, plan and report into one coherent plan

**Status:** method, v1, 2026-09-30. Operator decision the same day: **the hybrid**, which means exhaustive capture and product-style planning. Not started. It starts after the prerequisites in §9.
**Owner:** the main session (Opus). **Folder:** this one holds the method, the manifest, the register, the check reports and the tools.

---

## 1. Why, and the principle

Post-Athens work has produced a lot of text: two trackers, a roadmap, a product note, a doc backlog, a frozen FU ledger, 13 Fable 5.1 reports and 11 Opus reviews of them. Together that is about 19,600 lines and 274K words. Insights in it are at risk of being lost: summaries drop things, memory drops things, and one idea (the agentic backlog) once lived only in a chat. The operator paid for these insights and wants none of them wasted.

**The hybrid:**
- **Capture exhaustively, once, and make completeness checkable.**
  - Items that already have an ID (C-numbers, §-sections, FU#, table rows) are listed by script.
  - New, unstructured material is extracted twice, independently.
  - Scripts check coverage, quotes and markers.
  - Nothing counts as captured on trust.
- **Plan the product way.**
  - A short Now / Next / Later roadmap, organized by outcome.
  - A decision log that keeps the rejected options.
  - An explicit "not now / not doing" list, each entry with its gate.
  - Pruned trackers.
- **The register is an archive, not a backlog.** It is kept as the dated consolidation index for search, never maintained. The trackers stay authoritative (`WAYS_OF_WORKING.md` §1, one home per fact).

## 2. Outputs and their homes

| Output | Home | Kind |
|---|---|---|
| Manifest: every source, hash, lines, tier, handling | `CONSOLIDATION_2026_09_30/manifest.json` (+ `.md` view) | working |
| Raw items per chunk | `CONSOLIDATION_2026_09_30/raw/<chunk>.<extractor>.json` | working |
| Check reports | `CONSOLIDATION_2026_09_30/checks/*.md` | kept (evidence) |
| **Register:** merged canonical entries, all sources linked | `CONSOLIDATION_2026_09_30/register.jsonl` + `register.md` (by area) | kept (archive) |
| **Roadmap: Now / Next / Later by outcome** | replaces the sequencing sections of `PLAN_2026_06_12_post_athens_roadmap.md`, after operator approval | authoritative |
| **Decision log** (decided + rejected alternatives + why) | the roadmap's decisions block, restructured | authoritative |
| **Not now / not doing** (with gates) | a roadmap section | authoritative |
| Decision list for the operator session | `CONSOLIDATION_2026_09_30/decisions_pending.md` (possibly an interactive page) | working |
| Tracker write-back | `runtime/OPEN_ITEMS.md`, `voices/OPEN_ITEMS.md`, `doc_infrastructure_backlog.md`, `STATE.md` | authoritative |

## 3. Scope: the manifest (step 0)

The defaults below were proposed on 2026-09-30. The operator confirms or changes them when approving the manifest, and anything excluded is listed with its reason.

| Tier | Handling | Sources |
|---|---|---|
| **S** structured | Script lists every ID and its status; **single** LLM extraction of each item's body (sub-rows, notes, embedded questions) | `runtime/OPEN_ITEMS.md`, `voices/OPEN_ITEMS.md`, `FOLLOW_UPS.md` (frozen, but open FUs are still cited), `doc_infrastructure_backlog.md`, `PLAN_2026_06_12_post_athens_roadmap.md`, `PRODUCT_assembly_hub.md`, `STATE.md` |
| **U** unstructured | **Double** extraction (two models, independent) | The 13 Fable reports: `runtime/REVIEW_2026_09_28_*` (7), `voices/DESIGN_*`, `voices/REVIEW_*`, `voices/MEMO_*`, `DESIGN_2026_09_28_split_card_event_config.md`, `WRITING_SOURCES_2026_09_28.md`. Also: the 11 Opus reviews (`REVIEWS_OF_FABLE_DELIVERABLES_2026_09_29/`), `runtime/NOTE_2026_09_30_researcher_labels.md`, `runtime/SPEC_2026_05_27_magnifica_humanitas_annotated_pipeline.md`, `runtime/DESIGN_voice_deployment_context.md`, the handoffs (`runtime/HANDOFF_2026_09_28.md`, `runtime/HANDOFF_2026_05_29_ATHENS_COMPLETE.md`, `voices/HANDOFF.md`), the operator's memory files (9), and the **final replies of the 13 Fable sessions**, taken from their transcripts (a check that the handoff caught everything) |
| **K** constraints | Single extraction of rules and DON'Ts only; they become constraints the plan must respect | `ONBOARDING.md` ×3, `conventions.md`, `WAYS_OF_WORKING.md`, `CLAUDE.md`, the five `BRIEF_2026_09_28_*` |
| **W** sweep | Marker sweep only (§5 C4); any hit becomes an item | `docs/*.md` (15 specs, including known-quirks and open sections); `TODO`/`FIXME` in `runtime/` and `personas/` code |
| **X** excluded | Listed with its reason | `_workspace/archive/` and `~/Desktop/AI Assembly/archive/` (history); `docs/research/` (preserved grounding, not work items; a sweep can be added); `CHANGELOG.md` (history); `.claude/worktrees/` (copies) |

**Freeze:** the manifest records each file's sha256 at the frozen commit. Check C6 fails if a source changes afterwards. A change means re-extracting that source; the freeze is never silently bypassed.

## 4. The raw item

One JSON object per atomic item. A table row is one item, and a list of three to-dos is three.

| Field | Meaning |
|---|---|
| `id` | `<chunk>-<extractor>-NNN` |
| `source`, `lines` | file and line range (1-based, inclusive) |
| `quote` | ≤ 25 words, **verbatim** from those lines |
| `kind` | `todo` · `open_item` · `finding` · `recommendation` · `question` · `decision_made` · `decision_pending` · `idea` · `rejected` · `withdrawn` · `risk` · `constraint` · `cost` · `done` |
| `stated_status` | as the source states it (never inferred) |
| `refs` | tracker IDs, commits and files it cites |
| `date` | the date the source gives for it, if any |
| `area` | one of: transcription · researcher · provocateur · voice · editor · published-record · orchestration-infra · persona-build · cards · models-routing · validation · product-hub · docs-process · writing · cost (extendable, logged) |

**The extractor's contract:**
- Cover **every non-blank line**: each line falls inside an item's range, or inside a `no_item` range with a reason (heading, context, example, history, restatement of an item in the same chunk).
- Quotes are verbatim.
- Don't judge, summarize or merge across chunks.
- Keep rejected, withdrawn and superseded items.
- Don't read outside the chunk except to resolve a pointer, and cite it if you do.

## 5. Steps

**Step 0. Freeze and manifest.**
- Commit everything, then write `manifest.json` using the §3 defaults.
- **The operator approves the manifest.** This is the one place scope is decided.

**Step 1. Structured listing (script, no LLM).**
- Parse the S-tier headings and ID patterns (`### C\d+`, `## \d+\.`, `FU#\d+`, row IDs such as `A1`–`A17` and `#1`–`#26`), each with its status marker (✅ 🟢 🟡 🔵 ⏸ ⚖ ✖ and text).
- The resulting skeleton is authoritative for "which IDs exist, and in what status".

**Step 2. Chunking.**
- Split at headings, ≤ 200 lines per chunk, never inside a table.
- S-tier chunks follow item boundaries. Chunk IDs are stable and listed in the manifest.

**Step 3. Extraction.**
- S and K tiers: one pass (Sonnet).
- U tier: two independent passes, one Sonnet and one Opus. Same prompt; neither sees the other.
- W tier: a script, no LLM.
- An agent processes its chunks one at a time and writes each chunk's result to `raw/` before it reads the next.

**Step 4. Checks (scripts in `tools/`; each writes `checks/<check>.md`).**

| Check | Passes when | On failure |
|---|---|---|
| **C1 coverage** | Every non-blank line of every chunk is inside an item or a `no_item` range | Re-extract the uncovered ranges |
| **C2 quotes** | Every quote is a whitespace-normalized substring of its cited lines | Fix or drop the item; flag the extractor |
| **C3 double diff** (U tier) | Every item in one pass matches one in the other (overlapping lines + similar quote) | The main session reads the source lines and decides: real item (keep) or not (record why) |
| **C4 marker sweep** | Every hit (`?` sentences, TODO, FIXME, 🔵 ⚖ 🟡 ⏸, "decide", "decision", "pending", "not yet", "open question", "operator", `- [ ]`, numbered IDs like `D13`, `O10`, `Q3`, `N7`, `F4`) lies inside an item range | Extract the missed item |
| **C5 ID sweep** | Every tracker ID mentioned **anywhere** in scope exists in the Step-1 skeleton or as a register entry | File the orphan or record why it's obsolete |
| **C6 freeze** | Source hashes still match the manifest | Re-extract the changed source |

Loop until each check has **zero open failures**. Every resolution is recorded in its check report.

**Step 5. Merge (main session; reads the raw items with their quotes, never summaries).**
- Group the raw items that describe the same thing into one **canonical entry** (`R-NNNN`). It keeps the links to all its raw items and sources.
- **Conflicts are shown, not resolved silently.** Example: C60's "the validator is ~pure noise" against B2's evidence. The entry records both sources and marks itself `conflict`.
- **Status rule:** the most recent dated source gives the current status; an older contradicting source stays linked.
- **Nothing is deleted.** Withdrawn, superseded and rejected items keep their reason.
- **Check M1:** every raw item maps to exactly one canonical entry.

**Step 6. Plan (product-style; main session drafts, operator approves).**
- Every canonical entry gets **exactly one disposition**:
  - `now` / `next` / `later` (roadmap, under an **outcome**);
  - `decide` (decision list);
  - `parked` (not now / not doing, with its gate);
  - `done`;
  - `withdrawn`;
  - `duplicate-of R-…`.
- **Outcomes:** 5 to 8, proposed from the register and approved by the operator. Illustrative: "the published record is correct and anonymized"; "the Researcher's record reads as a map"; "a second event needs no code edits".
- **Decision log:** one ADR-lite entry per decision (date, decision, alternatives considered, why, source entries). It includes standing "keep it this way" decisions, such as C-non-agentic and halt-don't-retry.
- **Every paid test** lists a best-for-quality and a best-value option with cost estimates (roadmap decisions block; no blanket cap since 2026-09-30).
- **Check P1:** every entry has exactly one disposition. **Check P2:** every line of the roadmap, the decision list and the not-doing list cites entry IDs.

**Step 7. Operator decision session.**
- The list is sorted by urgency, then by dependency. The published-record issues come first: the name leak, and the held Whanganui page that went public.
- Each decision shows its options, costs, dependencies and a recommendation labelled as inference.
- The operator decides; the results go into the decision log.

**Step 8. Write-back (separate commits; the operator reviews the diff before any push).**
- **Trackers:** statuses updated, parked items marked with their gate, unfiled findings filed (e.g. B4's leading formulations, B2's gate-order defect), and each item gets a pointer to its register entry.
- **Roadmap:** the sequencing sections are replaced by Now / Next / Later; the decision log and the not-doing list are added.
- **Also updated:** STATE, the handoffs, and a CHANGELOG line (a planning milestone).
- **The register and the check reports stay in this folder** as the consolidation index.

## 6. Roles, models and effort

| Work | Who | Model |
|---|---|---|
| Tools (manifest, chunker, C1–C6, M1, P1–P2, renderers) | an agent, reviewed by the main session | Sonnet (standard code against this spec) |
| Extraction S/K, and pass A of U | agents | Sonnet |
| Extraction pass B of U | agents | Opus |
| Adjudication of C3, merge, outcomes, plan, decision list | main session | Opus |
| Optional final read: does the plan hang together? | one session | Fable 5.1, only if the weekly budget allows (76% used on 2026-09-30) |

**Scale estimate (inference):**
- ≈ 11K lines in S/K → ≈ 60 chunks, one pass each.
- ≈ 8K lines in U → ≈ 40 chunks, two passes each.
- So ≈ 140 extraction jobs.
- These run on the Claude Code plan's usage, not on the API, so no dollar cost.

**How it runs:** as a workflow only if the operator asks for one in their own words (e.g. "use a workflow"). Otherwise as batched Agent calls: ≤ 10 agents per pass, each taking about 10 chunks in sequence.

## 7. Risks and what covers them

| Risk | Covered by |
|---|---|
| An extractor skims a chunk | C1 (every line must be accounted for) and C4 (the marker net) |
| An extractor invents or distorts an item | C2 (verbatim quote), and the source link on every item |
| One model's blind spot | C3 (a second model on the unstructured material) |
| An ID mentioned in passing but never filed | C5 |
| Merge errors | M1, and every canonical entry links back to its quotes |
| The plan silently drops an entry | P1 and P2 |
| Sources change mid-run | C6 |
| The register becomes a second backlog | It is archive-only; the trackers stay authoritative (§1) |
| Over-splitting or under-splitting items | Schema rules and examples in the extraction prompt; duplicates collapse in the merge |

## 8. Decided and open

**Decided (operator, 2026-09-30):**
- the hybrid;
- write this method;
- no blanket spend cap on tests (best-quality and best-value options instead).

**Open until the manifest is approved:** the §3 scope defaults. Specifically:
- FOLLOW_UPS in full;
- the memory files in;
- `docs/` sweep only;
- the Fable session replies in;
- the K tier as constraints;
- `docs/research/` excluded.

**Open at Step 6:** the outcome list, and whether the roadmap file is renamed once its sequencing is replaced.

## 9. Prerequisites and timing

1. The stage-quality review's Part B is done and copied into the repo.
2. The cap re-plans are done and copied: 2/5, B3, B4 and 4/5 all ✅ (2026-09-30).
3. Everything is committed, which is the freeze.

Then Steps 0 → 8 run in order. **After Step 8:** the public snapshot (doc backlog rows #27 and #28; the operator's name in nothing public). Steps 0 and 7 need the operator; the others need the operator only for scope changes and approvals.
