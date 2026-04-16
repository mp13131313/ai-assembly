# AI ASSEMBLY — Infrastructure Setup

**Project:** The AI Assembly · World Beautiful Business Forum · Athens · May 7–10, 2026
**Purpose:** The physical and cloud infrastructure that runs the overnight pipeline. Pre-conference provisioning, Athens-time operation, and fallback paths.
**Scope:** Ops-facing. Pipeline logic lives in `AI_Assembly_Architecture.md` and the five pipeline documents.

---

## The Box

**One cloud VM, not your laptop.** Laptop lids close, Wi-Fi drops, Docker eats RAM. A small rented VM is cheap insurance and the right place to run production.

- **Provider:** Hetzner (Munich-based, good latency to Athens, cheapest sensible option)
- **Instance:** CX22 (4 vCPU / 8 GB RAM / 80 GB disk) — ~€6/month. CX32 if you want headroom.
- **OS:** Ubuntu 24.04 LTS
- **Rental window:** Provision 2 weeks before Athens, tear down 2 weeks after. Total VM cost for the full window: ~€10–15.

Your laptop remains the development environment, monitoring surface, and emergency fallback execution environment.

---

## Software Stack

Everything runs on the one VM.

### Prefect (audio pipeline orchestrator)

- **Self-hosted Prefect server** as a systemd service. `prefect server start` gives you the dashboard, flow runs, and logs on one box.
- Python 3.11+, code in a venv at `/opt/ai-assembly/`, pulled from the project git repo.
- **Trade-off noted:** Prefect Cloud's free tier would give you browser-accessible monitoring from anywhere (useful at 2am from the hotel lobby when laptop Wi-Fi is flaky). Self-hosted is simpler and has no external dependency, but if the VM has any issue you lose execution *and* observability at the same time. Self-hosted is the committed choice; revisit only if you hit problems during dry runs.

### n8n (everything from Researcher onward)

- **Same VM.** Run n8n in Docker alongside Prefect. 8 GB RAM is enough for both. File handoff becomes a local filesystem path — simplest possible contract.
- **Alternative considered and rejected:** n8n Cloud for managed upgrades. Rejected because it would force the Prefect→n8n handoff through Drive sync, adding latency and a failure mode to the boundary.
- n8n behind a reverse proxy (Caddy) with basic auth. The Prefect dashboard too. Never expose either on raw IP:port — anyone who finds the IP can see everything.

### Python environment

- Python 3.11+, single venv
- Dependencies pinned in `requirements.txt` committed to the repo
- `python-dotenv` for `.env` loading
- `watchdog` for the file watcher
- `rclone` (system package, not pip) for Drive sync

---

## Storage & File Flow

### Google Drive via rclone

- **Not the official Drive desktop client.** The Linux client is unreliable and headless-unfriendly.
- `rclone` with a Drive remote, mounted via `rclone mount` with `--vfs-cache-mode full`. Standard headless-Drive pattern. Mount survives reboots via systemd unit.
- Folder structure lives in Drive; the VM sees it as a local filesystem at `/mnt/drive/`:
  - `/mnt/drive/recordings/` — audio in (HoBB A/V team drops files here)
  - `/mnt/drive/transcripts/` — clean named transcripts out (n8n Researcher picks up here)
  - `/mnt/drive/metadata/` — `sessions.json`, rosters, bios
  - `/mnt/drive/review/` — catches filename-convention failures and flagged low-confidence speaker IDs

### File watcher

- Python `watchdog` running inside a Prefect deployment, watching `/mnt/drive/recordings/`
- New file event → parse filename → load `sessions.json` → fire the flow
- **Debounce 10–20 seconds** so Drive sync finalization doesn't trigger multiple runs on the same file

### sessions.json lifecycle

- **Source of truth:** file in the project git repo, pulled to the VM on update
- Contains session roster: session ID, title, expected speakers (names, affiliations, bios), language, session type
- Updated by you via git push when the conference schedule shifts (and it will shift)
- Loaded by the Prefect flow at the start of each run — no caching, always fresh off disk

### Disk space monitoring

Audio files are not tiny. 9 hours of session audio at 128 kbps MP3 is ~500 MB/night; higher-quality recording is multiples of that. 80 GB is plenty but you want an alert before it fills.

- Cron: `df -h / | awk 'NR==2 {if ($5+0 > 80) print "disk high"}'` → Telegram webhook
- Clean old raw audio after successful transcription (keep transcripts, drop source audio after 7 days)

---

## Secrets & Access

### API keys

- `.env` file at `/opt/ai-assembly/.env`, gitignored, 600 permissions
- Loaded via `python-dotenv`
- Backed up in 1Password

Keys you'll need:
- `ANTHROPIC_API_KEY` (Claude — the big one)
- `ASSEMBLYAI_API_KEY` (transcription)
- `PERPLEXITY_API_KEY` (persona research dossiers — pre-conference only)
- `GEMINI_API_KEY` (persona broad scan — pre-conference only)
- `OPENAI_API_KEY` (ChatGPT cross-model validation — pre-conference only)
- `SUNO_API_KEY` (Marley songs)
- `GITHUB_TOKEN` (content repo commits for micro-site)
- `VERCEL_TOKEN` (if you automate deploys)
- HoBB email tool credentials (TBD which tool)
- `TELEGRAM_BOT_TOKEN` + chat ID (alerts)

### SSH access

- **Who has keys:** decide now and write it down. At minimum: you + one backup person in a different timezone.
- Your SSH key and the backup person's SSH key both in `/root/.ssh/authorized_keys`
- Password auth disabled, root login via key only
- UFW firewall: 22 (SSH, restrict to known IPs if possible), 80/443 (reverse proxy), nothing else
- **If you lose your laptop at Athens airport on Day 0, can the pipeline still run?** If the answer is no, fix it before you fly.

### NTP

- `systemd-timesyncd` is on by default in Ubuntu 24.04. Confirm it's running: `timedatectl status`. Matters for log correlation and any time-based triggers.

---

## Monitoring & Alerting

### Logs

- Structured JSON logs to `/var/log/ai-assembly/` with `logrotate`
- Prefect's built-in run logs for flow-level events
- Loki + Grafana would be nice but is overkill — tail the files or open the Prefect UI when something breaks

### Alerts

One Telegram bot (or Slack webhook — Telegram is simpler on a phone at 2am). Fires on:

- Flow start: `session_003 processing started`
- Flow success: `session_003 done (12 min, $0.52)`
- Flow failure: `session_003 FAILED — AssemblyAI 502, retried 3x`
- Disk >80% full
- Handoff to n8n success/failure
- Newsletter sent confirmation

You need to know within minutes if something breaks during the conference. You won't be watching a dashboard at 23:00 after Day 1 of Athens.

---

## Handoff to n8n

- n8n watches `/mnt/drive/transcripts/` via a file trigger node
- When a new `.json` file lands, n8n pulls it and kicks off the Researcher flow
- No API call, no queue, no shared database — just files on disk
- The simplest contract possible and matches architecture.md

---

## AssemblyAI Configuration

Per the transcription research report, but with additions:

- `speaker_diarization: true`
- `max_speakers_expected: N` — from sessions.json per session
- `language_detection: true` — **essential** since some walking sessions may be in Greek
- Promptable text: `"Conference panel, business philosophy, international English speakers"`
- Custom vocabulary: all panelist names, organizations, session-specific terms pre-loaded
- **No audio enhancement upstream** — raw audio direct to ASR

---

## Pre-Conference Dry Runs

At least two full rehearsals. The second is non-negotiable.

### Dry run 1 — Plumbing test (2 weeks before Athens)

- Record 5 minutes of you + one other person
- Drop the file in `/mnt/drive/recordings/`
- Confirm: watcher fires, Prefect runs, AssemblyAI returns, speaker ID passes, cleaning passes, file lands in `/mnt/drive/transcripts/` in the right shape, n8n trigger fires
- Goal: prove the plumbing end-to-end

### Dry run 2 — Realistic rehearsal (1 week before Athens, MINIMUM)

- Use a real 90-minute panel recording from a past HoBB event
- Build a sessions.json entry from the real program (names, bios)
- Process through the full pipeline
- Goal: confirm latency, cost per session, speaker ID quality on real accented English, catch surprises (crosstalk, audience questions, unusual names)
- This is the only way to know whether speaker ID holds up on realistic material before you're standing on it in Athens

Both dry runs should end with a written "what broke, what I fixed" note committed to the repo.

---

## Failure & Fallback

### VM dies mid-conference

Move to laptop in under 10 minutes:

- Repo cloned locally: `~/projects/ai-assembly/`
- `.env` copy in 1Password
- Test `python -m prefect deployment run` on your laptop once before flying
- The whole stack is portable — it's Python, rclone, and two API calls. "Move to laptop" is a real fallback, not a theoretical one.

### AssemblyAI or Anthropic API outage

- No mitigation other than manual retry
- Both have >99.9% uptime
- Graceful degradation per architecture.md error handling table: speaker ID failure → anonymous labels; cleaning failure → pass raw transcript through; nothing blocking

### Wrong filename from A/V team

- `/mnt/drive/review/` catches filename-convention failures
- You need to be watching for this, especially Night 1
- Put the filename convention in a printed sheet on the A/V desk

### Complete pipeline failure Night 1

- **Have a pre-written "holding page"** on the micro-site ready to swap in
- A 30-second Slack message Tim can broadcast: *"The Assembly is still processing overnight. Artifacts will be live by 10am."*
- Decide now who writes and sends this if it's needed

### Total connectivity failure at the venue

- Greek data SIM (Vodafone or Cosmote, ~€20 for 20+ GB, buy at Athens airport on arrival)
- Mobile hotspot as primary uplink when needed
- Know which neighboring hotel has decent Wi-Fi

---

## Cost (Full Athens Run)

| Line item | Cost |
|---|---|
| Hetzner VM (1 month + margin) | €10–15 |
| AssemblyAI (~9 hrs/night × 2 nights, more if all sessions recorded) | $5–20 |
| Anthropic (speaker ID + cleaning + Researcher + Provocateur + Voice + newsletter, per architecture.md) | $40–120 |
| Suno (Marley songs, ~3 generations over 2 nights) | $1–5 |
| Perplexity / Gemini / OpenAI (pre-conference Persona Pipeline only) | $100–130 |
| Vercel + GitHub + Prefect self-hosted | free |
| Greek data SIM | €20 |
| **Total infrastructure + API** | **~€200–350** |

Dominant cost is your time, not the money.

Budget ~€500 total for comfort through build + both nights + re-runs + debugging headroom.

---

## Pre-Flight Checklist

### T–4 weeks

- [ ] Hetzner VM provisioned, Ubuntu 24.04, SSH key in place
- [ ] Project repo cloned to `/opt/ai-assembly/`
- [ ] Python venv + dependencies installed
- [ ] `.env` created with all keys, 600 permissions, backed up in 1Password
- [ ] rclone configured, Drive folder mounted at `/mnt/drive/`
- [ ] Drive folder structure created: `/recordings/`, `/transcripts/`, `/metadata/`, `/review/`
- [ ] Prefect installed as systemd service, dashboard accessible via Caddy + basic auth
- [ ] n8n running in Docker on same VM, also behind Caddy
- [ ] Telegram bot set up, test alert fires
- [ ] UFW firewall configured (22, 80, 443 only)
- [ ] NTP confirmed running
- [ ] Disk monitoring cron installed
- [ ] Backup person's SSH key added to VM

### T–2 weeks

- [ ] Dry run 1 complete, notes committed
- [ ] `sessions.json` schema finalized, committed to repo
- [ ] AssemblyAI config confirmed including `language_detection: true`
- [ ] n8n Researcher Pipeline built and tested against a known-good transcript
- [ ] HoBB recording arrangement confirmed with Tim/Till
- [ ] HoBB email tool identified, API credentials obtained
- [ ] 3–5 HoBB newsletters collected as style exemplars

### T–1 week

- [ ] Dry run 2 complete (real HoBB panel), notes committed
- [ ] Full overnight pipeline end-to-end test against dry run 2 output
- [ ] Newsletter curator prompt calibrated against HoBB exemplars
- [ ] Micro-site live with placeholder content, auto-rebuild confirmed working
- [ ] Laptop fallback tested: `prefect deployment run` from laptop with same `.env`
- [ ] Backup person briefed, has credentials, knows how to SSH in

### T–1 day

- [ ] Final git pull on the VM
- [ ] Disk space confirmed >50 GB free
- [ ] All API keys confirmed still valid (re-check rate limits)
- [ ] Printouts: architecture.md, persona pipeline v3.7, transcription pipeline, this runbook, error handling table
- [ ] Filename convention printed for the A/V desk
- [ ] Holding-page ready on micro-site
- [ ] Holding-page Slack message drafted

### On arrival in Athens

- [ ] Greek data SIM purchased at airport
- [ ] Mobile hotspot tested
- [ ] One last end-to-end test from hotel Wi-Fi
- [ ] Brief HoBB A/V team in person on filename convention and drop location
- [ ] Confirm moderators have been briefed to introduce panelists by full name
- [ ] Confirm walking-session participants will state their names at start

---

## What This Document Does NOT Cover

- **Pipeline logic** → `AI_Assembly_Architecture.md`
- **Persona construction** → `AI_Assembly_Persona_Pipeline_v3_7.md`
- **Transcription pipeline logic and prompts** → `AI_Assembly_Transcription_Pipeline.md`
- **Transcription stack research and benchmarks** → `Conference_Transcription_Pipelines_for_AI_Extraction_at_Scale__2025-2026_Strategic_Analysis.md` + "Overnight conference audio to clean named transcript" report
- **Micro-site visual design** → Lovable/v0 prototyping work
- **Newsletter style** → calibration workstream with HoBB exemplars
