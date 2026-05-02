# AI ASSEMBLY — INFRASTRUCTURE
## Athens 2026 deployment spec

**Project:** The AI Assembly · World Beautiful Business Forum · Athens · May 7–10, 2026
**Status:** v1 draft — 2026-05-02. **Supersedes** archived [`_workspace/archive/specs/AI_Assembly_Infrastructure_Setup.md`](../_workspace/archive/specs/AI_Assembly_Infrastructure_Setup.md), which was written for an n8n + Prefect-server + rclone-Drive architecture that no longer matches the codebase.
**Purpose:** Specifies the runtime infrastructure for Athens 2026 — what runs on a VM and why, what stays on the operator's laptop, and the seam between them. Intended to be readable end-to-end before provisioning.

---

## Why a VM at all

Three reasons, ordered by hardness of requirement:

1. **Ingest must be a network-accessible server during the panel.** HoBB's A/V team uploads recordings to a FastAPI endpoint while the panel is running. A laptop in a hotel room with the lid closed can't host that endpoint. This is the only piece with a hard "must be online during the event" requirement.

2. **Safety.** Three sub-things:
   - **Process survival** — the post-panel pipeline runs for 4–8 hours per night; laptop sleep / lid-close / battery dying kills running flows.
   - **Data preservation** — laptop loss / theft / coffee-spill in Athens.
   - **Recovery access** — if the laptop dies mid-event, the operator can SSH from a borrowed machine and keep going.

3. **Operator detachment.** Even when the laptop *works* fine, the operator should not be tied to it for the multi-hour overnight pipeline. Eat dinner, sleep, walk back to the hotel. A VM lets the pipeline run while the operator is not at the keyboard.

Reason 3 is sometimes folded into Reason 2; whether you treat them as two reasons or three, no fourth reason has been identified. Specifically *not* reasons: compute power (all heavy work is API calls), multi-operator concurrency (single operator), audit/compliance (irrelevant for Athens), cost reduction (VM is more expensive than laptop).

---

## What runs where

### On the VM (mandatory)

- **Ingest service** — FastAPI app at `runtime/ingest/app.py` + per-session normalize/transcribe subprocess pipeline. Receives audio uploads from HoBB during the panel.
- **`<PROJECT_ROOT>/runs/`** — the run_dir tree. Ingest writes here as audio comes in.
- **`<PROJECT_ROOT>/reference/sessions.json`** — read by ingest on every request.
- **`.env`** — `ANTHROPIC_API_KEY`, `ASSEMBLYAI_API_KEY`, `UPLOAD_APP_PASSWORD`, optional `CLAUDE_MODEL` override.

### On the VM (deployed as ready, fall back to laptop until then)

- **Researcher / Provocateur / Voice / Editor / Publish flows** — code already in `/opt/ai-assembly/runtime/flows/`. Each runs as a standalone CLI invocation against a `run_dir`. They use Prefect as a library (`@flow`/`@task` decorators give retry, exponential backoff, task-input-hash caching, run logger) — not as a server. Each `python flows/X.py <run_dir>` is a self-contained Prefect run.
- **Orchestrator** — `runtime/scripts/overnight_orchestrator.py` (designed at [`AUTOMATION_ORCHESTRATOR_DESIGN_2026_05_02.md`](../_workspace/planning/runtime/AUTOMATION_ORCHESTRATOR_DESIGN_2026_05_02.md), not yet built). Polls filesystem at 1-min cadence; fires each downstream stage when its inputs are present.
- **Prefect server** — provides the browser-accessible dashboard for live flow runs, task retries, durations, failures. The flows are already decorated; turning the server on is config, not code.
- **Claude Code** — installed on the VM (`npm install -g @anthropic-ai/claude-code`) and reached via SSH/mosh into a long-lived tmux session. The operator's runtime-ops surface for "why did Night 2 fail at 02:14?" / "show me the live state of tonight's run_dir" / "restart the orchestrator."

### Stays off the VM

- **Operator's laptop Claude Code session** — for code edits, bug fixes, prompt rewrites, planning, design. Pushes to GitHub; VM pulls.
- **Persona pipeline** — build-time work, runs against the operator's `personas/venv/`, not on the VM.
- **Microsite hosting** — separate concern (Vercel / GitHub Pages / wherever); consumes `published_artifacts/` after each night.
- **Both repos' authoritative remotes** — GitHub (`mp13131313/ai-assembly` + `mp13131313/ai-assembly-athens2026-voices`, both private). The VM holds clones, accessing each via a per-repo deploy key.

---

## What changed since the archived infra spec

| Old spec said | What's actually true now |
|---|---|
| n8n in Docker + Prefect server, both on VM | Neither service runs as Docker. Prefect is library-mode. n8n is gone. Orchestrator is a single Python script. |
| rclone-mounted Google Drive folders for audio handoff | FastAPI ingest writes directly to local FS; HoBB uploads via authenticated HTTP POST. |
| `code/` lives at `/opt/ai-assembly/` | Same. But `PROJECT_ROOT` is now a *separate* checkout at `/opt/ai-assembly-athens2026/` (Tier 3 split, 2026-04-20). |
| `sessions.json` lives in the code repo | Lives in `PROJECT_ROOT/reference/`; updated by editing the athens-2026 private repo and pulling on VM. |
| Caddy + Let's Encrypt + Basic Auth, single ingest hostname | Still correct — extended to multiple subdomains (ingest, prefect, optional status). |
| Hetzner CX22 (4 vCPU / 8 GB / 80 GB), ~€6/mo | Recheck against current load. Probably right. |

---

## Filesystem layout on the VM

```
/opt/ai-assembly/                          # code repo clone (private — needs deploy key)
├── .env                                    # mode 0600, owned by service user
├── runtime/venv/                           # runtime venv
├── runtime/ingest/                         # ingest app + deploy assets
├── runtime/flows/                          # all the flows
└── runtime/scripts/                        # orchestrator + helpers

/opt/ai-assembly-athens2026/                # PROJECT_ROOT (private repo clone)
├── reference/sessions.json
├── reference/speakers.json
├── reference/council_config.json
├── voices/<slug>/                          # persona cards
├── runs/                                   # run_dirs land here
└── published_artifacts/                    # publish_flow output

# Set in .env:
# AI_ASSEMBLY_PROJECT_ROOT=/opt/ai-assembly-athens2026
```

Both repos have their own `.git/`; pulled with `git pull` (or a deploy script that handles both).

---

## Services

Three systemd units + one interactive session.

### `ingest.service`

Existing unit at [`runtime/ingest/deploy/ingest.service`](../runtime/ingest/deploy/ingest.service). FastAPI app on `127.0.0.1:8000`, single uvicorn worker, `KillMode=process` so transcription subprocesses survive `systemctl restart`. Already production-ready.

### `orchestrator.service` (new)

Runs `overnight_orchestrator.py --project /opt/ai-assembly-athens2026` as a long-lived loop. Polls filesystem; fires Researcher → Provocateur → Voice → Publish (and Editor, when implemented) when each stage's inputs are ready. Idempotent — restart picks up where the last poll left off via filesystem-as-state.

To be written alongside the orchestrator script. Same hardening profile as `ingest.service` (NoNewPrivileges, ProtectSystem, ReadWritePaths to `runs/` only).

### `prefect-server.service` (new, optional but recommended)

Runs `prefect server start --host 127.0.0.1 --port 4200`. Provides browser dashboard at `prefect.<domain>` (Caddy proxy + Basic Auth). Live view of flow runs, task retries, durations, failures. Useful at 2am from a hotel lobby or phone. The flows are already Prefect-decorated; the server adds observability, not behavior.

### Interactive: `claude` in a tmux session

Not a systemd unit — interactive. Operator reaches it via:

```bash
mosh vm -- tmux attach -t claude || mosh vm -- tmux new -s claude 'claude'
```

Mosh (not plain SSH) handles flaky hotel Wi-Fi and laptop sleep. The tmux session persists across disconnects. Claude Code on the VM sees the VM's filesystem natively — no SSH-piped reads, no rsync acrobatics.

Auth: separate Anthropic API key in `~/.config/claude-code/` for the VM (or the same key as the runtime `.env`; operator decision).

---

## Network surface

Caddy fronts everything on the **single Hetzner-default hostname**, terminates TLS, enforces Basic Auth on protected paths, reverse-proxies by URL path:

```
https://<hetzner-hostname>/             →  127.0.0.1:8000  (ingest.service)
https://<hetzner-hostname>/prefect/*    →  127.0.0.1:4200  (prefect-server.service, Basic Auth)
https://<hetzner-hostname>/status/*     →  static file written by orchestrator (optional, Basic Auth)
```

Firewall: 22 (SSH/mosh), 80 (HTTP for cert renewal), 443 (HTTPS). Nothing else.

DNS: none required. Hetzner's default reverse DNS for the VM (`static.<dashed-ip>.clients.your-server.de`) resolves out-of-the-box. Caddy gets Let's Encrypt certs for it automatically on first request — known-working pattern.

---

## Operator workflow (the laptop ↔ VM seam)

Two contexts. Two Claude Code sessions. Different jobs.

| Task type | Where | Why |
|---|---|---|
| Edit code, fix bugs, write commits, push to GitHub | **Laptop Claude Code** | Local repo; canonical edit surface. |
| Plan, design, write specs | **Laptop Claude Code** | Same. |
| Read VM run_dirs, check live state, intervene mid-flow, restart services, read logs | **VM Claude Code** (via mosh+tmux) | Native VM filesystem access; no SSH-piped reads. |
| Browser monitoring (flow runs, retries, failures) | **Prefect dashboard** | At `prefect.<domain>`. Mobile-friendly. |
| Status check from phone in transit | **Either Prefect dashboard or mosh-reattach to VM tmux** | Both work over flaky networks. |

The two Claude Code sessions are peers, not the same entity — they don't share memory. For mid-night intervention, you want VM Claude Code; for code dev, you want laptop Claude Code. Most tasks naturally split this way.

---

## Provisioning steps

The existing [`runtime/ingest/deploy/README.md`](../runtime/ingest/deploy/README.md) is the canonical provisioning checklist for the **ingest** half. The additions for this spec are:

1. **Provision Hetzner CX22, Ubuntu 24.04** — 1-2 hours wall, mostly DNS propagation + smoke tests. Follow the existing README sections 1–6 verbatim.

2. **Clone the athens-2026 private repo** at `/opt/ai-assembly-athens2026/` as the same service user. Set `AI_ASSEMBLY_PROJECT_ROOT=/opt/ai-assembly-athens2026` in `.env`. Verify with `python -c "from flows.shared.project_root import resolve_project_root; print(resolve_project_root())"`.

3. **End-to-end Voice Pipeline test** against existing test inputs (~10 min, ~$1-2). Confirms the runtime side works on the VM exactly as it does on the laptop. If it doesn't, debug before going further.

4. **Install Prefect server** + write `prefect-server.service` + Caddyfile entry for `prefect.<domain>` + Basic Auth. Verify the dashboard renders.

5. **Build orchestrator** (separate work item; ~3-4 hr per [`AUTOMATION_ORCHESTRATOR_DESIGN_2026_05_02.md`](../_workspace/planning/runtime/AUTOMATION_ORCHESTRATOR_DESIGN_2026_05_02.md)). Add `orchestrator.service`.

6. **Install Claude Code on VM** + auth + verify mosh+tmux+claude flow from operator's laptop and phone.

7. **Full dry-run** with real audio on the VM end-to-end. **Required before Athens Night 1.** Eats one night of the calendar; plan for it at T-2 or T-3.

Steps 1–4 can happen now, independent of the editor pipeline build. Step 5 unblocks fully unattended operation; step 6 is the operator-detachment surface; step 7 is the gating event.

---

## Operations

### Monitoring

- `mosh vm -- tmux attach -t claude` — live conversation with Claude Code on VM
- `prefect.<domain>` — dashboard
- `journalctl -u ingest -f` / `journalctl -u orchestrator -f` — service logs
- `df -h /opt/ai-assembly-athens2026` — disk
- `curl -fsS https://ingest.<domain>/health | jq .` — ingest health

### Updating sessions.json

Edit `reference/sessions.json` in the local clone of the athens-2026 private repo, commit, push. On VM: `cd /opt/ai-assembly-athens2026 && git pull`. No service restart needed — ingest reads `sessions.json` fresh on every request.

### Updating code

`cd /opt/ai-assembly && git pull && systemctl restart ingest orchestrator` (and `pip install -r runtime/requirements.txt` if dependencies changed). Both repos pull cleanly; no merge conflicts expected (operator pushes; VM pulls).

### Backups

VM disk snapshot via Hetzner (manual or scheduled). Per-night belt-and-suspenders: rsync `runs/<run_dir>/` back to the laptop after each night completes. The athens-2026 private repo is the long-term archival home — `published_artifacts/` get committed there post-night.

---

## Failure modes + fallback

### VM dies mid-event

Move to laptop in under 15 minutes:

- Both repos already cloned locally
- `.env` copy in 1Password
- `runtime/venv/` rebuilt with `pip install -r runtime/requirements.txt`
- HoBB notified to upload to a temporary laptop-hosted endpoint (degraded — needs operator's laptop reachable on Wi-Fi during panel)

The honest fallback: ingest can survive on laptop only if the operator sits with laptop open in venue. Not ideal but possible.

### Laptop dies mid-event

VM keeps running. Operator borrows / buys a machine, clones repos, sets up SSH key, reattaches mosh to VM tmux. ~30 min recovery.

### Both die

Recordings still exist on HoBB's side; rerun the full pipeline post-event from the audio files. Slower but possible.

### Stage fails inside orchestrator

Orchestrator halts; logs to `runs/<run_dir>/_orchestrator_logs/`. Operator's morning ritual: check logs, fix, restart orchestrator (which idempotently picks up). Auto-retry is intentionally NOT enabled — failures during overnight processing are usually real issues (rate limits, missing data, prompt errors). Auto-retry burns API budget without resolving root cause.

### Network partition between operator and VM

Pipeline keeps running unattended (this is the Reason 3 detachment payoff). When connectivity returns, `mosh` reattaches to tmux without losing context.

---

## Lifecycle

| Phase | Date (Athens 2026) | Action |
|---|---|---|
| Provision | T-5 → T-4 (May 2–3) | Hetzner CX22 up, ingest deployed, smoke-tested |
| Stage downstream flows | T-4 → T-2 | Researcher / Provocateur / Voice tested on VM; orchestrator built + deployed |
| Editor pipeline (parallel) | T-4 → T-1 | Implementation; deploy to VM if ready, else run from laptop |
| Full dry-run | T-2 (May 5) | End-to-end with real audio |
| Buffer | T-1 (May 6) | Last-minute fixes |
| Athens Night 1 | T (May 7) | Live |
| Athens Night 2 | T+1 (May 8) | Live |
| Athens Night 3 | T+2 (May 9) | Live |
| Post-event window | T+3 → T+14 | Re-runs with updated prompts; archive run_dirs |
| Tear down | T+14 (May 23) | Snapshot final state; destroy VM |

Total VM rental window: ~3 weeks at ~€6/mo = **~€10–15 total**. Disposable infra is good infra.

---

## Cost

| Line item | Estimated cost |
|---|---|
| Hetzner CX22 (3-week Athens window + buffer) | €10–15 |
| Domain registration / DNS (if not already owned) | €10/year |
| AssemblyAI (~25 sessions × 3 nights × ~30 min each) | $20–40 |
| Anthropic — Researcher + Provocateur + Voice (Opus 4.7 $5/$25) | $60–80 across 3 nights |
| Anthropic — Editor Pipeline (Opus 4.7) | $3–5 across 3 nights |
| Microsite hosting (Vercel free tier likely) | $0 |
| **Total estimated event cost** | **~€110–150 + €10–15 VM** |

The big numbers are API usage, not infrastructure. The VM is rounding error.

---

## Open decisions (operator input required)

These are unresolved as of 2026-05-02. Items 1 + 2 block provisioning; 3–7 can be settled before/after.

1. **Domain / DNS.** ✅ Decided 2026-05-02: use Hetzner-provided default hostname (e.g. `static.<ip-with-dashes>.clients.your-server.de`). Caddy gets a Let's Encrypt cert for it on first request — known-working pattern. Subdomains for `prefect.` and `status.` not available with this approach; instead, run all services on path prefixes (`/`, `/prefect/`, `/status/`) on the same hostname. Microsite hosting (separate Decision 3) gets its own URL — Vercel-default or operator-owned domain, decided when microsite work starts.

2. **PROJECT_ROOT clone strategy.** Confirm: clone athens-2026 private repo to `/opt/ai-assembly-athens2026/` on VM. Operator pushes from laptop; VM pulls. (Alternative: keep PROJECT_ROOT laptop-only and rsync run_dirs both ways. Worse — recommend against.)

3. **Microsite hosting.** Out of VM scope but on the critical path. Where does `published_artifacts/` get rendered to a public URL? Vercel / GitHub Pages / something else?

4. **Backup strategy.** Hetzner disk snapshots only? Or per-night rsync to laptop + commit run_dirs to athens-2026 private repo as belt-and-suspenders?

5. **VM size confirmation.** CX22 (4 vCPU / 8 GB / 80 GB) — sufficient based on rough estimates. Resize-up live is cheap if it pinches.

6. **Operator monitoring surface.** Prefect dashboard (recommended) — confirm yes. Optional status page with one-line "what's the state of tonight's pipeline" — needed or skip?

7. **Claude Code on VM auth.** Same Anthropic API key as runtime `.env` (simplest), or separate key for VM operator session (cleaner audit trail)?

---

## Implementation status

- [x] Ingest service code + deploy assets (`runtime/ingest/`)
- [x] All downstream flows built (transcription, researcher, provocateur, voice)
- [ ] Editor pipeline implementation (separate work item; see [Editor Pipeline doc](AI_Assembly_Editor_Pipeline.md))
- [ ] Orchestrator script + systemd unit
- [ ] Prefect server systemd unit + Caddyfile entry
- [ ] VM provisioned
- [ ] athens-2026 private repo cloned on VM
- [ ] Claude Code installed on VM
- [ ] End-to-end dry-run on VM with real audio

Tracked at [`_workspace/planning/runtime/OPEN_ITEMS.md`](../_workspace/planning/runtime/OPEN_ITEMS.md) §B (Athens-blocking).

---

## Cross-references

- [Voice Pipeline](AI_Assembly_Voice_Pipeline.md) — runs on the VM as one stage
- [Editor Pipeline](AI_Assembly_Editor_Pipeline.md) — runs on the VM as one stage (when built)
- [Researcher Pipeline](AI_Assembly_Researcher_Pipeline.md), [Provocateur Pipeline](AI_Assembly_Provocateur_Pipeline.md), [Transcription Pipeline](AI_Assembly_Transcription_Pipeline.md) — same
- [Ingest deploy README](../runtime/ingest/deploy/README.md) — canonical provisioning checklist (sections 1–6)
- [Orchestrator design](../_workspace/planning/runtime/AUTOMATION_ORCHESTRATOR_DESIGN_2026_05_02.md) — to be implemented
- [Archived infra spec](../_workspace/archive/specs/AI_Assembly_Infrastructure_Setup.md) — superseded by this doc; do not consult
