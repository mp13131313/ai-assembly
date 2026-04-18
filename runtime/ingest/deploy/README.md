# Deploying the AI Assembly Ingest App

Step-by-step for a fresh Ubuntu 24.04 VM. Adapt paths/hostnames as needed.

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

## 2. Clone the repo and install the venv

```bash
sudo -u ingest -H bash -c '
  cd /opt/ai-assembly
  git clone <your-repo-url> .
  python3.12 -m venv runtime/venv
  runtime/venv/bin/pip install -U pip
  runtime/venv/bin/pip install -r runtime/requirements.txt
'
```

## 3. Configure `.env`

`/opt/ai-assembly/.env`, mode `0600`, owned by `ingest`:

```
UPLOAD_APP_PASSWORD=<strong random, share with producers in Signal>
ANTHROPIC_API_KEY=sk-ant-…
ASSEMBLYAI_API_KEY=…
# Optional overrides
# CLAUDE_MODEL=claude-opus-4-7
# TRANSCRIPTION_CACHE=0
```

```bash
sudo chmod 600 /opt/ai-assembly/.env
sudo chown ingest:ingest /opt/ai-assembly/.env
```

## 4. Install the systemd unit

```bash
sudo cp /opt/ai-assembly/runtime/ingest/deploy/ingest.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now ingest
sudo systemctl status ingest
```

Logs: `sudo journalctl -u ingest -f`.

Cap journald disk use:

```bash
sudo sed -i 's/^#\?SystemMaxUse=.*/SystemMaxUse=500M/' /etc/systemd/journald.conf
sudo systemctl restart systemd-journald
```

## 5. Configure Caddy

```bash
sudo cp /opt/ai-assembly/runtime/ingest/deploy/Caddyfile /etc/caddy/Caddyfile
# Edit the hostname:
sudo sed -i 's/ingest\.example\.com/ingest.<your-domain>/g' /etc/caddy/Caddyfile
sudo systemctl reload caddy
```

DNS: point `ingest.<your-domain>` at the VM's public IP. Caddy gets a
Let's Encrypt cert automatically on first request.

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
   curl -fsS https://ingest.<your-domain>/health | jq .
   ```
   Expect `{"ok": true, "free_bytes": …}`.

2. **Auth page renders**: browser → `https://ingest.<your-domain>/` → enter
   Basic Auth creds → session list loads. Empty-state is OK if no sessions
   are flagged yet.

3. **Flag a session**: SSH to VM, edit
   `/opt/ai-assembly/runtime/reference/sessions.json`, flip one session's
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

- `sudo journalctl -u ingest -f` — app logs
- `sudo journalctl -u caddy -f` — proxy access
- `df -h /opt/ai-assembly` — disk usage
- `curl -fsS http://127.0.0.1:8000/health | jq .free_gib` — free space

### Run new day's program

Before Day Two (etc.), flip the `ai_assembly` flag on the relevant sessions
in `reference/sessions.json`. No restart required — the app reads this file
fresh on every request.

### Regenerate sessions.json from an updated HTML program

```bash
sudo -u ingest /opt/ai-assembly/runtime/venv/bin/python \
    /opt/ai-assembly/runtime/scripts/generate_sessions_json.py \
    --input /path/to/new/index.html
```
The generator preserves existing `ai_assembly=true` flags across re-runs.

### Post-event

Rotate `UPLOAD_APP_PASSWORD` after Athens ends. The full `runs/` tree is
the archival record; back it up and keep it for Researcher/Provocateur
re-runs with updated prompts.
