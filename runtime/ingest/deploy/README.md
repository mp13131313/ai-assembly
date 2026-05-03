# Deploying the AI Assembly runtime to a VM

Step-by-step for a fresh Ubuntu 24.04 VM. Covers ingest + orchestrator + (optionally) Prefect server. Sized for the Athens 2026 deployment but adaptable.

For the architectural rationale (why a VM, what runs there, what doesn't), see [`docs/AI_Assembly_Infrastructure.md`](../../../docs/AI_Assembly_Infrastructure.md). For the runtime contract (what happens during a night), see [`docs/AI_Assembly_Runtime_Lifecycle.md`](../../../docs/AI_Assembly_Runtime_Lifecycle.md).

## 1. VM prerequisites

Recommended: 2–4 vCPU, 4 GB RAM, **≥ 100 GB SSD**. Audio storage grows at
~500 MB per session uncompressed, ~55 MB per session after normalization,
so a busy night (≤ 15 sessions) uses a few GB.

```bash
sudo apt update
sudo apt install -y ffmpeg python3.12 python3.12-venv caddy git
```

Create the service user and install dir:

```bash
sudo useradd --system --shell /usr/sbin/nologin --home /opt/ai-assembly ingest
sudo mkdir -p /opt/ai-assembly
sudo chown ingest:ingest /opt/ai-assembly
```

## 2. Clone both repos and install the venv

Both the code repo and the project-data repo are private; clone via deploy keys (one per repo, generated on the VM, public key pasted into each repo's "Deploy keys" settings).

Generate deploy keys on the VM:

```bash
sudo -u ingest -H bash -c '
  ssh-keygen -t ed25519 -N "" -f ~/.ssh/id_code -C "vm@ai-assembly code repo"
  ssh-keygen -t ed25519 -N "" -f ~/.ssh/id_athens -C "vm@ai-assembly athens repo"
  cat ~/.ssh/id_code.pub   # paste into mp13131313/ai-assembly Deploy keys
  cat ~/.ssh/id_athens.pub # paste into mp13131313/ai-assembly-athens2026-voices Deploy keys
'
```

Configure `~/.ssh/config` so each clone uses its own key:

```bash
sudo -u ingest -H bash -c 'cat > ~/.ssh/config <<EOF
Host github-code
  HostName github.com
  User git
  IdentityFile ~/.ssh/id_code
  IdentitiesOnly yes

Host github-athens
  HostName github.com
  User git
  IdentityFile ~/.ssh/id_athens
  IdentitiesOnly yes
EOF
chmod 600 ~/.ssh/config
'
```

Clone both:

```bash
sudo -u ingest -H bash -c '
  cd /opt/ai-assembly
  git clone github-code:mp13131313/ai-assembly.git .
  python3.12 -m venv runtime/venv
  runtime/venv/bin/pip install -U pip
  runtime/venv/bin/pip install -r runtime/requirements.txt
'

sudo -u ingest -H git clone github-athens:mp13131313/ai-assembly-athens2026-voices.git \
    /opt/ai-assembly-athens2026
```

## 3. Configure `.env`

`/opt/ai-assembly/.env`, mode `0600`, owned by `ingest`:

```
UPLOAD_APP_PASSWORD=<strong random, share with producers in Signal>
ADMIN_APP_PASSWORD=<different strong random, operator only — keep in 1Password>
ANTHROPIC_API_KEY=sk-ant-…
ASSEMBLYAI_API_KEY=…

# Required: PROJECT_ROOT for the runtime flows + orchestrator
AI_ASSEMBLY_PROJECT_ROOT=/opt/ai-assembly-athens2026

# Optional overrides
# CLAUDE_MODEL=claude-opus-4-7
# TRANSCRIPTION_CACHE=0
```

**Two roles, two credentials** (per C23, 2026-05-03):

- `UPLOAD_APP_PASSWORD` → role `producer`. HoBB A/V producers' login. They see
  a flat session list + their per-session upload page + a truncated post-upload
  view ("Received: `<filename>` at `<timestamp>`"). They do NOT see pipeline
  state, downstream stages, or other sessions' progress.
- `ADMIN_APP_PASSWORD` → role `admin`. Operator login. Sees everything:
  per-session pipeline state machine, the `/admin/tonight` Pipeline overview,
  per-stage drilldowns, and admin-only routes.

Optional: if `ADMIN_APP_PASSWORD` is unset, admin role is unavailable and
the app behaves exactly as the pre-2026-05-03 single-password setup. The
`/admin/*` routes 401 for any caller. Producers continue to work normally.

### Routes (post-2026-05-03 IA)

```
unauthenticated:  /health
both roles:       /  /session/{id}  /session/{id}/upload (POST)
                  /session/{id}/status   ← producer truncated, admin full
                  /logout                ← 401 with fresh realm string;
                                           best-effort cred clear
admin only:       /status  /status.json  ← legacy cross-night view
                  /session/{id}/status.json  /session/{id}/retry (POST)
                  /admin/tonight  /admin/tonight.json       ← Pipeline overview
                  /admin/tonight/transcription[?night=N]    ← stage drilldown
                  /admin/tonight/researcher[?night=N]  + .json
                  /admin/tonight/provocateur[?night=N] + .json
                  /admin/tonight/voice[?night=N]       + .json
                  /admin/tonight/publish[?night=N]     + .json
                  /admin/file?path=<rel>          ← read-only file viewer
```

The `/admin/tonight` dashboard is **read-only** — all change/intervention
happens via Claude Code on the VM (mosh + tmux). `/admin/file?path=<rel>`
serves files from PROJECT_ROOT inline in the browser (suffix-whitelist:
`.json/.log/.md/.txt/.flag`; max 10 MiB; path-traversal-protected); used
by the dashboard to make every mentioned file path clickable.

### Logout

HTTP Basic Auth has no real logout. `/logout` returns 401 with a
differentiated realm string (`Basic realm="AI Assembly Ingest (logged
out)"`) — most modern browsers (Chrome, Firefox, Safari, Edge) treat
the realm change as a fresh challenge and drop the cached creds. If a
browser hangs onto cached creds, the reliable fallback is to close the
tab/window. Logout link in the top nav, role-aware label.

### Phase C drilldowns shipped 2026-05-03

Five stage drilldowns are live, all admin-only, all read-only, all with a
JSON twin polled by 30s meta-refresh:

- `/admin/tonight/transcription[?night=N]` — per-session ASR/speaker-ID/cleaning state
- `/admin/tonight/researcher[?night=N]` + `.json` — theme/cluster tree + per-session extractions + isolates
- `/admin/tonight/provocateur[?night=N]` + `.json` — voice × theme triage matrix + formulation grid + theme flags + below-target warnings
- `/admin/tonight/voice[?night=N]` + `.json` — Step 1 grid + validation grid + Step 2 + continuity
- `/admin/tonight/publish[?night=N]` + `.json` — per-voice publish artifacts + index

`/admin/tonight/editor` still pending — gated on B1 (`flows/editor_flow.py`);
trivial once that ships (~2 hr to mirror the Voice pattern).

### Vendor-supplied sessions (audio_source: "vendor")

Five athens-2026 sessions are recorded by an external vendor and delivered
as session_package-shaped JSON, not audio. They skip Stage 0 + Stage 1 and
land at the canonical Stage 1 output boundary directly via
`flows/vendor_intake.py`. Tagged with `audio_source: "vendor"` in
`reference/sessions.json`. The producer UI hides them; the admin dashboard
renders them with a "vendor" pill and per-row file links to vendor.flag /
vendor.warnings / vendor.error.

Pre-Athens setup (one-time):

```bash
sudo mkdir -p /opt/ai-assembly-athens2026/vendor_inbox
sudo chown ingest:ingest /opt/ai-assembly-athens2026/vendor_inbox
```

Operator workflow during the event:

```bash
# vendor emails files; operator saves them locally with the convention
#   <session_id>.json  (matches reference/sessions.json session_id)
# and scp's the batch to the VM:
scp ~/Downloads/*.json athens-vm:/opt/ai-assembly-athens2026/vendor_inbox/

# in tmux on VM, after each delivery batch:
ssh athens-vm
cd /opt/ai-assembly-athens2026/runtime
venv/bin/python -m flows.vendor_intake --night 1 --sweep
# → "expected: 3 · landed: 3 · missing: 0"
```

Sweep is idempotent — re-run as files trickle in. Missing files are
reported but don't fail the sweep (exit 0 unless an actual validation
error occurred). The orchestrator's transcription gate sees vendor
sessions as `state=done` exactly the same as audio sessions.

Single-file form for one-offs:

```bash
venv/bin/python -m flows.vendor_intake \
    /opt/ai-assembly-athens2026/vendor_inbox/<session_id>.json \
    --run-dir runs/athens_night_1 \
    --session-id <session_id>
```

Validation is two-tier: hard fails (bad JSON, session_id mismatch, empty
turns, missing required fields, bad confidence values) write `vendor.error`
+ `status.json state=error`; warn-and-accept paths (missing review_queue,
roster drift vs sessions.json, missing turn_index, etc.) write
`vendor.warnings` and proceed. See `flows/vendor_intake.py` docstring for
the full matrix.

```bash
sudo chmod 600 /opt/ai-assembly/.env
sudo chown ingest:ingest /opt/ai-assembly/.env
```

## 4. Install the systemd units

Three systemd units in total — `ingest`, `orchestrator@`, and (optionally) `prefect-server`. Install in this order.

### 4a. Ingest

```bash
sudo cp /opt/ai-assembly/runtime/ingest/deploy/ingest.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now ingest
sudo systemctl status ingest
```

Logs: `sudo journalctl -u ingest -f`.

### 4b. Orchestrator (templated unit, one instance per night)

```bash
sudo cp /opt/ai-assembly/runtime/scripts/deploy/orchestrator@.service \
    /etc/systemd/system/
sudo systemctl daemon-reload
```

The orchestrator is a templated unit — start it per-night when ready. Do NOT `enable --now`; you only want it running during the overnight pipeline window.

```bash
# Before/during Athens Night 1 (May 7, evening):
sudo systemctl start orchestrator@1.service

# Watch it work:
sudo journalctl -u orchestrator@1 -f
```

The orchestrator polls the filesystem at 1-min cadence; fires each downstream stage when its inputs are ready. Idempotent — restart picks up where it left off. See [`docs/AI_Assembly_Runtime_Lifecycle.md`](../../../docs/AI_Assembly_Runtime_Lifecycle.md) for what each stage does.

### 4c. Prefect server (optional dashboard)

```bash
# Install Prefect CLI in the runtime venv (it's already in requirements.txt)
sudo -u ingest /opt/ai-assembly/runtime/venv/bin/prefect server start --help

# Create the systemd unit:
sudo tee /etc/systemd/system/prefect-server.service > /dev/null <<'EOF'
[Unit]
Description=Prefect Server (flow run dashboard)
After=network-online.target

[Service]
Type=simple
User=ingest
Group=ingest
WorkingDirectory=/opt/ai-assembly
ExecStart=/opt/ai-assembly/runtime/venv/bin/prefect server start --host 127.0.0.1 --port 4200
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now prefect-server
```

Cap journald disk use:

```bash
sudo sed -i 's/^#\?SystemMaxUse=.*/SystemMaxUse=500M/' /etc/systemd/journald.conf
sudo systemctl restart systemd-journald
```

## 5. Configure Caddy

The Caddyfile in this repo serves all three services from a single hostname via path-prefix routing — no DNS subdomain config required (the Hetzner-default hostname is fine for Athens).

```bash
sudo cp /opt/ai-assembly/runtime/ingest/deploy/Caddyfile /etc/caddy/Caddyfile

# Replace `your-hostname.example` with the VM's actual hostname (Hetzner-default
# is something like `static.123-45-67-89.clients.your-server.de`):
sudo sed -i "s/your-hostname\.example/$(hostname -f)/g" /etc/caddy/Caddyfile

# Replace REPLACE_WITH_CADDY_HASH_PASSWORD_OUTPUT placeholders for /prefect/*
# and /status/* basic auth (skip if you're not enabling those endpoints):
caddy hash-password   # paste this output into the Caddyfile
sudo $EDITOR /etc/caddy/Caddyfile

sudo systemctl reload caddy
```

After this:

- `https://<vm-hostname>/` → ingest
- `https://<vm-hostname>/prefect/` → Prefect dashboard (Basic Auth)
- `https://<vm-hostname>/status/` → orchestrator status JSON (Basic Auth)

Caddy gets Let's Encrypt certs for the Hetzner-default hostname automatically on first request.

Firewall:

```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

## 6. Smoke test

In order. Stop if any step fails.

1. **Health endpoint** (unauthenticated):
   ```bash
   curl -fsS https://<vm-hostname>/health | jq .
   ```
   Expect `{"ok": true, "free_bytes": …}`.

2. **Auth page renders**: browser → `https://<vm-hostname>/` → enter
   Basic Auth creds → session list loads. Empty-state is OK if no sessions
   are flagged yet.

3. **Flag a session**: SSH to VM, edit
   `/opt/ai-assembly-athens2026/reference/sessions.json`, flip one session's
   `ai_assembly` to `true`. Reload `/` — the session appears.

4. **Tiny upload against fake flow** (no API spend):
   ```bash
   # As ingest user on the VM:
   cd /opt/ai-assembly
   sudo -u ingest ./runtime/venv/bin/python -c '
   import subprocess
   subprocess.run(["ffmpeg","-hide_banner","-y",
                   "-f","lavfi","-i","sine=frequency=440:duration=5",
                   "/tmp/smoke.m4a"], check=True)
   '
   # Temporarily point the app at the fake flow:
   sudo systemctl stop ingest
   sudo -u ingest bash -c '
     cd /opt/ai-assembly
     INGEST_FLOW_CMD="./runtime/venv/bin/python ./runtime/ingest/tests/fake_transcription_flow.py" \
     FAKE_DELAY_SECONDS=3 \
     ./runtime/venv/bin/uvicorn ingest.app:app --host 127.0.0.1 --port 8000 &
   '
   ```
   Upload `/tmp/smoke.m4a` via the browser UI, watch it go through
   `received → normalizing → transcribing → done`. Then:
   ```bash
   sudo systemctl start ingest   # back to the real flow
   ```

5. **One real session** (costs ~$1.50 in AssemblyAI + Anthropic credits):
   upload a real 30-second recording, confirm `session_package.json`
   appears under the run dir, spot-check speaker IDs look plausible.

6. **Restart survival**: upload, and while state is `transcribing`:
   ```bash
   sudo systemctl restart ingest
   ```
   The transcription subprocess should survive. After restart, the status
   page should still transition to `done`.

## 7. Operations

### Monitor

- `sudo journalctl -u ingest -f` — ingest app logs
- `sudo journalctl -u orchestrator@<N> -f` — orchestrator (per night)
- `sudo journalctl -u caddy -f` — proxy access
- `sudo journalctl -u prefect-server -f` — Prefect server (if enabled)
- `df -h /opt/ai-assembly-athens2026` — disk usage
- `curl -fsS http://127.0.0.1:8000/health | jq .free_gib` — free space
- `cat /opt/ai-assembly-athens2026/runs/athens_night_<N>/_orchestrator_logs/status.json` — current pipeline state
- Browser: `https://<vm-hostname>/prefect/` — Prefect dashboard (if enabled)

### Run a night's pipeline

```bash
# Evening of May 7 (Night 1):
sudo systemctl start orchestrator@1.service
sudo journalctl -u orchestrator@1 -f

# Same for nights 2 and 3:
sudo systemctl start orchestrator@2.service
sudo systemctl start orchestrator@3.service
```

If the night includes vendor-supplied sessions (currently 3 on Night 1, 1
on Night 2, 1 on Night 3), land them via `flows/vendor_intake.py` BEFORE
or DURING the orchestrator run — the orchestrator's transcription gate
requires every flagged session to have `status.json state=done` before
firing the Researcher. Audio sessions land via the producer upload UI
+ Stage 0 normalization; vendor sessions land via `vendor_intake --sweep`
(see "Vendor-supplied sessions" section above for the workflow). The two
paths are independent — vendor sessions can be landed at any point in the
night, before or after audio sessions finish transcribing.

If a stage fails, the orchestrator halts and exits non-zero. systemd's
`Restart=on-failure` won't restart on clean failure exits — investigate the
log at `_orchestrator_logs/<stage>.<ts>.log`, fix the cause, then restart
the unit. Each flow has internal checkpointing; re-running picks up where
the last run stopped.

For the full operational picture (what each stage does, what files it writes,
how to inspect state), see [`docs/AI_Assembly_Runtime_Lifecycle.md`](../../../docs/AI_Assembly_Runtime_Lifecycle.md).

### Update sessions.json or other reference data

The reference data lives in the **athens-2026 private repo** (cloned at `/opt/ai-assembly-athens2026/`), not the code repo. Update workflow:

```bash
# On laptop, in the athens-2026 repo:
$EDITOR reference/sessions.json
git commit -am "..." && git push

# On VM:
sudo -u ingest -H git -C /opt/ai-assembly-athens2026 pull
```

No service restart needed — ingest reads `sessions.json` fresh on every request.

### Regenerate sessions.json from an updated HTML program

```bash
sudo -u ingest /opt/ai-assembly/runtime/venv/bin/python \
    /opt/ai-assembly/runtime/scripts/generate_sessions_json.py \
    --input /path/to/new/index.html \
    --output /opt/ai-assembly-athens2026/reference/sessions.json
```
The generator preserves existing `ai_assembly=true` flags across re-runs.

### Post-event

Rotate `UPLOAD_APP_PASSWORD` after Athens ends. The full `runs/` tree under
`/opt/ai-assembly-athens2026/` is the archival record; commit and push it to
the athens-2026 private repo (selectively — exclude raw audio if you don't
want it in git history) for off-VM preservation, or snapshot the disk via
Hetzner before tearing down the VM.
