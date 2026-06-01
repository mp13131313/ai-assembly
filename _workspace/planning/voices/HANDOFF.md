# Voices — Handoff (2026-05-29 — supersedes 2026-05-06; preserved in git history)

**Companion:** `OPEN_ITEMS.md` (open items) + `ONBOARDING.md` (how-to / fresh-pickup).

**On a fresh session:** read `ONBOARDING.md` first (~10 min), then this doc (~5 min), then `OPEN_ITEMS.md` (~10 min).

---

## Headline state

**Athens 2026 is COMPLETE.** All three nights ran end-to-end and are published — 13 dossiers + 30 per-voice pages across Nights 1–3 — using the 10 voice cards + Tim Leberecht editor card. Pre-Athens voice-build work is COMPLETE; post-Athens work is documentation hygiene + v4.1 cleanup + operator-side reader-gate work.

---

## Branch + repo state (post-history-rewrite, 2026-05-29)

| Repo | Branch | HEAD | Pushed |
|---|---|---|---|
| code | `main` | `aeca549` (voices-thread: revert C42 prompt overreach + clarify "FILED" not "applied") | ✅ |
| code | `feature/voice-deployment-context` | `248300c` (holds shelved `6a8e825` — runtime/OPEN_ITEMS C48; runtime-thread's disposition call) | ✅ |
| code | `feature/editor-deployment-context` | `9c21ac0` (content already in `main` — redundant; runtime-thread's call to delete) | ✅ |
| athens-2026 | `main` | `06245ad` (voices-thread: re-Derive 10× `06_derive/` against operator-short-draft cards — closes runtime/OPEN_ITEMS C3 sweep) | ✅ |

**Important:** both repos were force-pushed 2026-05-29 by the runtime/production thread (re-authored ~680 commits to operator's real identity). All pre-rewrite SHAs in older docs / handoffs / commits / planning entries are DEAD; translate via `~/Desktop/AI Assembly/archive/2026-05-29-history-rewrite/HASH_REMAP_{code,athens}_2026-05-29.tsv` if needed. Pre-rewrite backups at `~/Desktop/AI Assembly/archive/2026-05-29-history-rewrite/BACKUP_{code,athens}_pre-rewrite.bundle` (see the folder's `README.md` for usage). The runtime thread's `d80a0ac` ("docs: remap commit-hash citations to post-rewrite SHAs (21 files)") swept most planning docs; if you find a dead SHA in voices-thread docs, the file may have been missed.

---

## Where the voices stand

| Voice | type / voice_mode | State |
|---|---|---|
| Voice of Plato | human / philosophical | ✅ shipped + Athens N1–N3 served |
| Voice of Cleopatra | human / observational | ✅ shipped + Athens N1–N3 served |
| Voice of Fyodor Dostoevsky | human / narratival | ✅ shipped + Athens N1–N3 served |
| Voice of Ibn Battuta | human / narratival | ✅ shipped + Athens N1–N3 served |
| Voice of the Octopus | non_human / observational | ✅ shipped + Athens N1–N3 served |
| Voice of Hannah Arendt | human / philosophical | ✅ shipped + Athens N1–N3 served (canonical meta-framing PASS case for C42 spec) |
| Voice of Ada Lovelace | human / philosophical | ✅ shipped + Athens N1–N3 served |
| Voice of the Whanganui River | non_human / system + `mediation_stance: transmission_witness` | ✅ v2 SHIPPED + ATHENS-CLEAN; N3 sacred-grammar rerun (4 voice pages) under sacred-grammar discipline; operator-released the C42 HOLD |
| Voice of Scheherazade | fictional / narratival | ✅ shipped + Athens N1–N3 served |
| Voice of Bob Marley | human / observational | ✅ v2 SHIPPED + ATHENS-CLEAN; load-bearing I-and-I worked per editorial assessment; deferred to post-Athens Rastafari-orbit reader gate |
| Tim Leberecht *(13th persona — Assembly editor)* | human / philosophical | ✅ shipped; composed 13 dossiers across N1–N3 |

**Voice cards remained stable across all three nights** (no per-night card patches; the temporal_stance rewrite was 2026-05-08, before Athens). Athens published `bfa1f8a`(N1 v1)/`50d88e1`(N1 v2) + `9ad06ff`(N2) + `394914b`(N3 closing) on the operator-short-draft cards; today's `06245ad` is a chat-test paste-target refresh, no runtime impact.

---

## What landed between the prior HANDOFF (2026-05-06) and today (2026-05-29)

### 2026-05-08 — `voice_temporal_stance.default` 4× rewrite (Gap-K)

Runtime-thread inspection of the May-5 dryrun outputs surfaced that the 2026-05-05 assembly-fiction reframe (`3bcbef5`) had APPENDED assembly clauses to v1 biographical-anchor framing rather than LEADING with assembly-presence. Voices-thread fix iterated four times:

1. `d43eadd` AF-leads + universal epistemic-honesty hook
2. `b2d5eaf` hook removed (operator caught: previously-shipped hooks caused decline-to-engage)
3. `7cdbee3` Hannah residual v1-leakage fix
4. `08a8253` operator short drafts (FINAL — what Athens N1–N3 published on)

Total field-content reduction 10,005 → 5,958 chars (−40.5% from the 82a0af9-pre-rewrite-equivalent dryrun baseline). Per-voice snapshots preserved. Standing rule filed in `planning/ONBOARDING.md`: no epistemic-out hooks in `voice_temporal_stance.default`.

**See:** `voices/OPEN_ITEMS.md §31 Gap-K` for the full evolution; `§30` for the original assembly-fiction reframe (now marked SUPERSEDED-by-Gap-K).

### 2026-05-29 — runtime/production thread shipped Athens N1–N3 + history rewrite

External work; surfacing here because it confirms voices-thread architectural choices empirically:

- **Athens-confirmed architectural validation:** voices meta-framed their own synthesis as objects of critique rather than uncritically extending; the §31 Gap-J / Memo §A.9 collision is empirically resolved. Hannah's N1 opening *"My own voice was synthesized to comment on the experiment that synthesized it"* is the canonical case.
- **C42 recurrence (Nights 2–3):** the Sonnet safeguards validator still applies the OLD absolute "no AI-self-ack" rule and HOLDs voices for meta-framing — Whanganui N3 HOLD → operator-released; Final-night continuity-notice generates spurious `first_person_presence_leak` flags. Validator prompt lags card discipline.
- **History rewrite + force-push:** ~680 commits re-authored to operator's real-identity. Shared checkout already on new history; cached SHAs are dead; remap TSVs on Desktop. Voices-thread doc content was preserved byte-intact; SHA citations in 21 planning files were remapped automatically by the runtime thread (`d80a0ac`).

### 2026-05-29 — voices-thread sweep + close-out (today)

1. **Re-Derive shipped** (athens-2026 `06245ad`): all 10 `06_derive/` artifacts regenerated against operator-short-draft cards via path-(b) fast-exit Derive (~10 min wall, ~$2 LLM). Chat-test paste-targets now match cards. Runtime unaffected (it reads cards directly). Closes runtime/OPEN_ITEMS C3 from 2026-05-08 sweep.
2. **C42 voices-side spec filed** (code repo `aeca549`): in `runtime/OPEN_ITEMS C42` — 3-change spec (BREACH-vs-PASS distinction with Hannah N1 / Battuta N1 / Whanganui N3 anchors + `voice_temporal_stance` rule update + `continuity_night_<N>` exemption from `first_person_presence_leak`). **Production prompt at `runtime/flows/shared/prompts/voice_step2_validation_safeguards.md` UNCHANGED** — runtime thread to apply (or revise) the spec.
3. **Gap-K final-state documentation** + §30 SUPERSEDED pointer + C48 voice-deployment-context shelving record + universal-hook calibration note + designer-zip moved to archive.
4. **Two miscalibration notes filed**: "universal" (planning/ONBOARDING.md cross-cutting calibration); "file" means file/record, not apply (offered, not separately filed — second instance of the over-aggressive-verb-reading pattern).

---

## What's pending

### Operator-side (post-Athens)

1. **Marley + Whanganui post-Athens reader gates** — Rastafari-orbit reader (Imani Tafari-Ama / Carolyn Cooper / Bob Marley Foundation / Anthony Bogues orbit) for Marley's load-bearing I-and-I; iwi-orbit reader for Whanganui v2 witness-translator stance. Per §11 + §24 + §28.
2. **D1/E1 paragraph use post-Athens** — drafts at `_workspace/archive/session-artifacts/MARLEY_READINESS_PARAGRAPHS_2026-05-04.md` (archived 2026-05-29) were written for pre-Athens; if you publish post-Athens commentary or the Rastafari reader-gate work, these are the refinement starting point. Whanganui parallel drafts not yet written.
3. **Branch hygiene (runtime-thread's call)** — `feature/editor-deployment-context` is fully merged + redundant; `feature/voice-deployment-context` holds shelved `6a8e825` (C48). Runtime thread owns disposition.

### v4.1 architectural cleanup (post-Athens; not pre-Athens-eligible)

Filed in `voices/OPEN_ITEMS.md §31`:
- **Gap-H** (apparatus-transposition seams) — Group-1 voices need refuse-and-reframe discipline when formulation invites uncharacteristic analytical work
- **Gap-I** (Step 2 composition flattens digression/instance discipline) — structural prompt-level fix
- **Gap-J** (per-voice card-coherence audit on architectural edits) — empirically validated; Hannah was the canonical case; resolved by Gap-K rewrite
- **Gap-K** ✅ FIXED — AF-leads-vs-appends + operator short drafts
- **Pass 4b te-reo discipline (Gap-G)** — generalize the Whanganui kawa-speaker-frame closure into the prompt
- **Pass 1 chunked merge audit** + Pass 1c fetch follow-ups (Plato Perseus / Marley SSL / Tim SSL — rebuild-only)

### Runtime-thread (downstream of voices work)

- **C42** — voices-thread spec filed; runtime to apply + smoke-test (re-fire Hannah N1 / Whanganui N3 through the new prompt; both should PASS) + close.
- **C43** validator JSON parse robustness (recurred N2–N3)
- C49/C50/C51/C52 (runtime-only)

### Low-priority cleanup (no urgency)

- **C4 from sweep:** snapshot proliferation — 6 `.pre_*.json` files per voice in athens-2026; gitignored, local-only; cleanup someday
- **MEMO_2026_05_07 §A.1–A.8** card-patch slips (Cleopatra dating / Marley Stagirite / Lovelace diction / Plato cobbler+capitulation / Battuta four-part-typology / Dostoevsky labelled-steps / Arendt instance-rostering) — never separately applied; status post-Athens unknown to me. If you're doing v4.1 card cleanup, these are the worked-from list. Memo archived 2026-05-29 → `_workspace/archive/session-artifacts/MEMO_2026_05_07_card_patches_from_external_reader.md`.

---

## What would I do next session

1. **If runtime thread wants C42 closed:** supply the smoke-test artifacts (Hannah N1 + Whanganui N3 paste-ready through the new safeguards prompt → expected verdict PASS).
2. **If operator wants reader-gate work:** draft Whanganui D1/E1 parallel paragraphs; refine the Marley drafts.
3. **If v4.1 cleanup time:** start with Gap-G (Pass 4b te-reo discipline generalization, since the Whanganui v2 work surfaced the pattern) or the MEMO_2026_05_07 §A.1–A.8 card-patch slips.

**No work is currently in flight.** Both repos clean + pushed; the runtime-thread's `runtime/ingest/*` WIP from a prior intermediate state is no longer in the working tree.

---

## Reading order for next session

1. `voices/ONBOARDING.md` (durable how-to)
2. `voices/HANDOFF.md` — this doc
3. `voices/OPEN_ITEMS.md` — §31 (v4.1 gaps + Gap-K post-Athens state) + §28 + §29 + §11 (reader gates)
4. **For runtime-side context:** `code/STATE.md` + `code/CLAUDE.md` state block at top + `_workspace/planning/runtime/HANDOFF_2026_05_29_ATHENS_COMPLETE.md`
5. **For C42 work specifically:** `runtime/OPEN_ITEMS.md C42` (voices-side spec; production prompt UNCHANGED)

That's ~25 min to working knowledge for voice-build cold-start.

---

## When this doc goes stale

Rolling single-file convention for voices/. Overwrite when voices-thread work landing materially changes state. The prior 2026-05-06 snapshot is preserved in git history; don't append, refresh.
