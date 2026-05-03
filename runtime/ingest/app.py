"""FastAPI ingest app. Routes, lifespan, background tasks.

Design principles (see plan):
  * The filesystem is authoritative; status.json under each session dir is
    the single source of truth.
  * Transcription subprocesses are detached (start_new_session=True); if
    uvicorn restarts mid-run, reconcile_on_startup adopts them.
  * Upload body is streamed chunk-by-chunk, never buffered into RAM.
  * Single worker + asyncio.Semaphore serializes normalize (ffmpeg) only.
    Transcription subprocesses run detached and can execute concurrently
    across sessions; rate-limit exposure is bounded by AssemblyAI's and
    Anthropic's per-key caps.
"""

from __future__ import annotations

import json
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote
from typing import Any

from fastapi import (
    BackgroundTasks,
    Depends,
    FastAPI,
    HTTPException,
    Request,
    status as http,
)
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from flows.shared.io import write_json_atomic  # noqa: E402 — sys.path set in config

from . import dashboard, pipeline
from .auth import require_admin, require_auth
from .config import (
    ALLOWED_EXTENSIONS,
    MAX_UPLOAD_BYTES,
    MIN_FREE_BYTES,
    STATIC_DIR,
    STATIC_VERSION,
    TEMPLATES_DIR,
    UPLOAD_CHUNK_BYTES,
    check_required_env,
)
from .sessions import (
    Session,
    build_session_json,
    derive_roster,
    find_session,
    load_sessions,
    load_speakers,
    run_for_session,
    session_dir,
    track_css_class,
)

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
# Make track_css_class available as a filter in every template.
templates.env.filters["track_css"] = track_css_class
templates.env.globals["static_version"] = STATIC_VERSION

_STATE_DISPLAY = {
    "received":               "received",
    "normalizing":            "normalizing",
    "transcribing":           "transcribing",
    "transcribing_asr":       "transcribing · ASR",
    "transcribing_speaker_id":"transcribing · speaker ID",
    "transcribing_cleaning":  "transcribing · cleaning",
    "transcribing_finalizing":"transcribing · finalizing",
    "done":                   "done",
    "error":                  "error",
}
templates.env.filters["state_label"] = lambda s: _STATE_DISPLAY.get(s, s or "not started")


# --- Lifespan ----------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI):
    check_required_env()
    reconciled = pipeline.reconcile_on_startup()
    if reconciled:
        print(f"ingest: reconciled {len(reconciled)} session(s) on startup:")
        for r in reconciled:
            print(f"  {r['before']} → {r['after']}  {r['dir']}")
    yield


app = FastAPI(title="AI Assembly Ingest", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


# --- Helpers -----------------------------------------------------------------


def _require_session_and_dir(session_id: str) -> tuple[Session, Path]:
    """404 if unknown, 409 if the session's day doesn't map to an overnight run."""
    sessions = load_sessions()
    sess = find_session(sessions, session_id)
    if sess is None:
        raise HTTPException(http.HTTP_404_NOT_FOUND, detail="unknown session_id")
    sdir = session_dir(sess)
    if sdir is None:
        raise HTTPException(
            http.HTTP_409_CONFLICT,
            detail=f"{sess.day} is not offered for overnight processing",
        )
    return sess, sdir


def _forbid_producer_on_vendor(sess: Session, role: str) -> None:
    """Vendor sessions land via flows/vendor_intake.py — there is no producer
    audio for them. Producers hitting these routes by URL get 403 with a
    clear message rather than a confusing upload form they can't usefully fill."""
    if role != "admin" and sess.is_vendor:
        raise HTTPException(
            http.HTTP_403_FORBIDDEN,
            detail=(
                "this session is vendor-supplied (no producer upload). "
                "the operator lands the transcript via flows/vendor_intake.py."
            ),
        )


def _validate_extension(filename: str) -> str:
    """Return the lowercased extension including the dot, or 400."""
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            http.HTTP_400_BAD_REQUEST,
            detail=(
                f"unsupported extension {ext!r}; allowed: "
                f"{', '.join(sorted(ALLOWED_EXTENSIONS))}"
            ),
        )
    return ext


def _existing_audio_info(sdir: Path) -> dict[str, Any] | None:
    """Return info about any already-uploaded audio, or None."""
    p = sdir / "audio.m4a"
    if not p.exists():
        return None
    stat = p.stat()
    return {
        "filename": p.name,
        "size_bytes": stat.st_size,
        "mtime": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(
            timespec="seconds"
        ),
    }


# --- Routes ------------------------------------------------------------------


@app.get("/health")
def health() -> Response:
    """Liveness + disk check for systemd and monitoring."""
    free = pipeline.free_bytes()
    body = {"ok": True, "free_bytes": free, "free_gib": round(free / 1024**3, 1)}
    if free < MIN_FREE_BYTES:
        body["warning"] = f"free space below {MIN_FREE_BYTES // 1024**3} GiB"
    return JSONResponse(body)


@app.get("/logout", response_class=HTMLResponse)
def logout() -> Response:
    """Best-effort HTTP Basic Auth logout.

    The protocol has no real logout: browsers cache Basic creds per
    realm until the cache clears (typically: tab/window close, browser
    restart, or manual clear). This route returns 401 with a DIFFERENT
    realm string than `require_auth` uses ("AI Assembly Ingest" → "AI
    Assembly Ingest · logged out"), which most modern browsers treat as
    a fresh challenge — they discard the cached creds for the original
    realm and re-prompt on the next page load.

    Tested behavior: Chrome, Firefox, Safari, Edge all honor this. If
    a browser stubbornly hangs onto the cached creds, the reliable
    fallback is to close the tab/window.
    """
    body = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Logged out · AI Assembly Ingest</title>
  <link rel="stylesheet" href="/static/style.css">
</head>
<body>
  <header><div class="wrap"><a href="/" class="brand">AI Assembly · Ingest</a></div></header>
  <main class="wrap">
    <h1>Logged out</h1>
    <p>Your browser should now have dropped the cached login.</p>
    <p>
      <a class="primary" href="/">Sign in again</a>
    </p>
    <p class="muted footer-hint">
      HTTP Basic Auth has no real logout in the protocol. If your
      browser still acts as if you're signed in, close this tab/window
      to clear the cached credentials.
    </p>
  </main>
</body>
</html>
"""
    return Response(
        content=body,
        status_code=http.HTTP_401_UNAUTHORIZED,
        media_type="text/html",
        headers={
            # Realm must be ASCII per RFC 7230. The "(logged out)" suffix
            # is what differentiates this realm from the auth-protected
            # routes' realm — most browsers treat the realm change as a
            # fresh challenge and drop the cached creds.
            "WWW-Authenticate": 'Basic realm="AI Assembly Ingest (logged out)"',
            "Cache-Control": "no-store",
        },
    )


@app.get("/", response_class=HTMLResponse)
def index(request: Request, role: str = Depends(require_auth)):
    sessions = load_sessions()
    # Producers see only audio-source sessions — vendor sessions land via
    # flows/vendor_intake.py at the 01_transcription boundary, not via this
    # upload UI, so showing them as "missing upload" rows would mislead.
    # Admins see everything (vendor rows render with a distinct pill).
    if role == "admin":
        flagged = [s for s in sessions if s.ai_assembly]
    else:
        flagged = [s for s in sessions if s.ai_assembly and not s.is_vendor]
    # Group by day_index for the template; also pass a list of days present.
    by_day: dict[str, list[Session]] = {}
    for s in flagged:
        by_day.setdefault(s.day, []).append(s)
    # Attach current state per session so we can color-dot the cards (admin
    # only; producers see "uploaded" boolean only — no pipeline state leak).
    states: dict[str, str | None] = {}
    if role == "admin":
        for s in flagged:
            sdir = session_dir(s)
            if sdir:
                states[s.session_id] = pipeline.infer_state(sdir).get("state")
    else:
        # Producer: collapse pipeline state to a binary marker. Reuse the
        # `done` CSS class (green) for "your upload is recorded" — the
        # tooltip below reads "done" but, from the producer's mental
        # model, that means "your task is taken care of." We don't show
        # downstream pipeline state to producers.
        for s in flagged:
            sdir = session_dir(s)
            if sdir and (
                (sdir / "audio.m4a").exists()
                or any(sdir.glob("audio.upload*"))
            ):
                states[s.session_id] = "done"
            else:
                states[s.session_id] = None
    days_ordered = [d for d in ["Day One", "Day Two", "Day Three"] if d in by_day]
    venues_ordered = sorted({s.venue for s in flagged if s.venue})
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "by_day": by_day,
            "days_ordered": days_ordered,
            "venues_ordered": venues_ordered,
            "states": states,
            "flagged_count": len(flagged),
            "role": role,
        },
    )


@app.get("/status", response_class=HTMLResponse)
def overview(request: Request, role: str = Depends(require_admin)):
    """Cross-session pipeline overview. Admin only — pipeline state is operator
    concern, not producer concern (per C23, 2026-05-03)."""
    sessions = load_sessions()
    flagged = [s for s in sessions if s.ai_assembly]
    rows = []
    for s in flagged:
        sdir = session_dir(s)
        if not sdir:
            continue
        st = pipeline.infer_state(sdir) if sdir.exists() else {"state": None}
        rows.append({"session": s, "status": st})
    # Sort: errors first, then active, then done, then not-started.
    order = {"error": 0, "normalizing": 1, "transcribing": 1, "received": 2, "done": 3, None: 4}
    # Sort by state priority, then day, then time. Use date_time_start (ISO 8601)
    # for time ordering — it sorts lexicographically correctly and is always
    # zero-padded. Fall back to start_time only if date_time_start is absent.
    rows.sort(key=lambda r: (
        order.get(r["status"].get("state"), 9),
        r["session"].day_index,
        r["session"].date_time_start or r["session"].start_time,
    ))
    return templates.TemplateResponse(
        request, "overview.html", {"rows": rows, "role": role}
    )


@app.get("/status.json")
def overview_json(_: str = Depends(require_admin)):
    """Polled by the overview page to update state cells. Admin only."""
    sessions = load_sessions()
    flagged = [s for s in sessions if s.ai_assembly]
    result = []
    for s in flagged:
        sdir = session_dir(s)
        if not sdir:
            continue
        st = pipeline.infer_state(sdir) if sdir.exists() else {"state": None}
        result.append({"session_id": s.session_id, "state": st.get("state"), "substate": st.get("substate")})
    return JSONResponse(result)


@app.get("/session/{session_id}", response_class=HTMLResponse)
def session_detail(session_id: str, request: Request, role: str = Depends(require_auth)):
    sess, sdir = _require_session_and_dir(session_id)
    _forbid_producer_on_vendor(sess, role)
    speakers = load_speakers()
    roster, missing_bios = derive_roster(sess, speakers)
    existing = _existing_audio_info(sdir) if sdir.exists() else None
    # Producers only need to know "is something already uploaded?" — the
    # downstream pipeline state is admin concern. infer_state still runs for
    # admin so they see the current pipeline phase on the detail page.
    if role == "admin":
        current = pipeline.infer_state(sdir) if sdir.exists() else {"state": None}
    else:
        current = {"state": "uploaded" if existing else None}
    return templates.TemplateResponse(
        request,
        "session_detail.html",
        {
            "session": sess,
            "roster": roster,
            "missing_bios": missing_bios,
            "existing": existing,
            "current_state": current.get("state"),
            "run_id": run_for_session(sess),
            "allowed_extensions": sorted(ALLOWED_EXTENSIONS),
            "max_upload_mb": MAX_UPLOAD_BYTES // (1024 * 1024),
            "role": role,
        },
    )


@app.post("/session/{session_id}/upload")
async def upload(
    session_id: str,
    request: Request,
    background: BackgroundTasks,
    role: str = Depends(require_auth),  # both roles can upload audio
):
    """Stream request body to disk, validate, kick off pipeline.

    Query params:
      filename: client-provided filename (we only use its extension)
      overwrite: "true" to allow replacing an existing audio.m4a
    """
    sess, sdir = _require_session_and_dir(session_id)
    # Vendor sessions take no audio — block any uploader (incl. admin via
    # browser quirks) from accidentally writing audio bytes that would
    # never be processed and would just confuse the dashboard.
    if sess.is_vendor:
        raise HTTPException(
            http.HTTP_409_CONFLICT,
            detail=(
                "this session is vendor-supplied (audio_source=vendor); "
                "transcripts land via flows/vendor_intake.py, not the upload form."
            ),
        )

    filename = request.query_params.get("filename", "")
    overwrite = request.query_params.get("overwrite", "").lower() == "true"

    ext = _validate_extension(filename)

    # Disk pre-flight. Refuse before we accept bytes.
    if pipeline.free_bytes() < MIN_FREE_BYTES:
        raise HTTPException(
            http.HTTP_507_INSUFFICIENT_STORAGE,
            detail="not enough free disk space on the ingest VM",
        )

    sdir.mkdir(parents=True, exist_ok=True)
    lock_path = sdir / "upload.lock"

    # Concurrent-upload guard: non-blocking flock. If we can't acquire, another
    # upload is already in flight for this session.
    import fcntl

    lockf = lock_path.open("w")
    try:
        try:
            fcntl.flock(lockf.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            lockf.close()
            raise HTTPException(
                http.HTTP_409_CONFLICT,
                detail="another upload is already in progress for this session",
            )

        # Overwrite guard.
        existing = sdir / "audio.m4a"
        if existing.exists() and not overwrite:
            raise HTTPException(
                http.HTTP_409_CONFLICT,
                detail="audio already uploaded; resend with ?overwrite=true to replace",
            )

        # Stream body to audio.upload.partial, then rename after full receive.
        raw_dst = sdir / f"audio.upload{ext}"
        partial = raw_dst.with_suffix(raw_dst.suffix + ".partial")
        partial.unlink(missing_ok=True)

        bytes_received = 0
        try:
            with partial.open("wb") as f:
                async for chunk in request.stream():
                    if not chunk:
                        continue
                    bytes_received += len(chunk)
                    if bytes_received > MAX_UPLOAD_BYTES:
                        raise HTTPException(
                            http.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                            detail=f"upload exceeds {MAX_UPLOAD_BYTES} bytes",
                        )
                    f.write(chunk)
        except HTTPException:
            partial.unlink(missing_ok=True)
            raise
        except Exception as e:
            partial.unlink(missing_ok=True)
            # Log internally, but don't leak exception details to the client.
            print(f"ingest: upload error for {session_id}: {type(e).__name__}: {e}", flush=True)
            raise HTTPException(
                http.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="upload failed; check server logs",
            )

        if bytes_received == 0:
            partial.unlink(missing_ok=True)
            raise HTTPException(http.HTTP_400_BAD_REQUEST, detail="empty upload body")

        partial.replace(raw_dst)

        # Remove any stale Stage 0 outputs from a previous upload to this session.
        # Normalized audio.m4a is handled by normalize_audio (it's the tmp->rename target).
        for stale in ("out_01_diarized.json", "out_02_speaker_id.json",
                      "out_03_cleaned.json", "session_package.json", "review.md"):
            (sdir / stale).unlink(missing_ok=True)
        # Remove previously normalized audio so ffmpeg starts fresh.
        (sdir / "audio.m4a").unlink(missing_ok=True)

        # Write the session.json for this run (sessions.json + speakers.json join).
        speakers = load_speakers()
        session_json_path = sdir / "session.json"
        write_json_atomic(session_json_path, build_session_json(sess, speakers))

        # Initialize status. Kick off background pipeline.
        pipeline.initialize_status(
            sdir,
            session_id=sess.session_id,
            run_id=run_for_session(sess) or "",
            audio_filename=raw_dst.name,
        )
        background.add_task(
            pipeline.run_normalize_and_transcribe, sdir, raw_dst, session_json_path
        )
    finally:
        # Keep the lockf open only as long as this request; release now so the
        # next (valid) upload attempt can acquire. Background task does its own
        # concurrency via pipeline._gate.
        try:
            fcntl.flock(lockf.fileno(), fcntl.LOCK_UN)
        except Exception:
            pass
        lockf.close()

    return JSONResponse(
        {
            "ok": True,
            "bytes_received": bytes_received,
            "status_url": f"/session/{quote(session_id)}/status",
        }
    )


@app.get("/session/{session_id}/status", response_class=HTMLResponse)
def session_status(session_id: str, request: Request, role: str = Depends(require_auth)):
    """Per-session post-upload state.

    Producer view: truncated to "Received: <filename> at <timestamp>" only.
    No pipeline state, no normalizing/transcribing/done/error. If something
    fails, operator handles out-of-band (per C23, 2026-05-03).

    Admin view: full state machine with substates, polled JS. Existing
    behavior preserved.
    """
    sess, sdir = _require_session_and_dir(session_id)
    if role == "admin":
        return templates.TemplateResponse(
            request, "status.html",
            {"session": sess, "run_id": run_for_session(sess), "role": role},
        )
    # Producer: render the stripped view server-side. No JS polling.
    received = _existing_audio_info(sdir) if sdir.exists() else None
    if received is None:
        # Maybe the upload is still in flight — look for the .partial.
        partials = sorted(sdir.glob("audio.upload*.partial")) if sdir.exists() else []
        if partials:
            stat = partials[0].stat()
            received = {
                "filename": partials[0].name.replace(".partial", ""),
                "size_bytes": stat.st_size,
                "mtime": datetime.fromtimestamp(
                    stat.st_mtime, tz=timezone.utc
                ).isoformat(timespec="seconds"),
            }
    return templates.TemplateResponse(
        request, "status_producer.html",
        {"session": sess, "received": received, "role": role},
    )


@app.get("/session/{session_id}/status.json")
def session_status_json(session_id: str, _: str = Depends(require_admin)):
    """Polled by the admin status page. Admin only — producers don't poll."""
    sess, sdir = _require_session_and_dir(session_id)
    if not sdir.exists():
        return JSONResponse({"state": None, "session_id": sess.session_id})
    return JSONResponse(pipeline.infer_state(sdir))


@app.post("/session/{session_id}/retry")
def session_retry(session_id: str, _: str = Depends(require_admin)):
    """Re-spawn Stage 0 using the existing audio.m4a (after a transient error).

    Admin only — retry is an intervention surface. Per C23, all change/control
    surfaces stay admin-side; producers re-upload via the upload endpoint
    after operator out-of-band asks them to.
    """
    sess, sdir = _require_session_and_dir(session_id)
    if not sdir.exists():
        raise HTTPException(http.HTTP_404_NOT_FOUND, detail="no session dir")
    if sess.is_vendor:
        raise HTTPException(
            http.HTTP_409_CONFLICT,
            detail=(
                "vendor session — retry by re-running flows/vendor_intake.py "
                "from tmux on the VM, not via this endpoint."
            ),
        )
    # Rebuild session.json too — speakers.json may have been updated with new bios.
    speakers = load_speakers()
    session_json_path = sdir / "session.json"
    write_json_atomic(session_json_path, build_session_json(sess, speakers))
    st = pipeline.spawn_retry(sdir, session_json_path)
    return JSONResponse(st)


# --- Admin meta dashboard (C23, 2026-05-03) ----------------------------------


@app.get("/admin/tonight", response_class=HTMLResponse)
def admin_tonight(
    request: Request,
    night: int | None = None,
    _: str = Depends(require_admin),
):
    """Read-only Athens-night meta view.

    Reads filesystem state across the 8 stages (mirrors the orchestrator's
    state model in runtime/scripts/overnight_orchestrator.py). No write
    surfaces; control plane stays at Claude-on-VM via mosh+tmux.
    """
    n = night if night in dashboard.ATHENS_NIGHTS else dashboard.latest_active_night()
    payload = dashboard.collect_night_state(n)
    return templates.TemplateResponse(
        request, "admin_tonight.html",
        {
            "payload": payload,
            "night": n,
            "all_nights": dashboard.ATHENS_NIGHTS,
            "role": "admin",
        },
    )


@app.get("/admin/tonight.json")
def admin_tonight_json(
    night: int | None = None,
    _: str = Depends(require_admin),
):
    """Machine-readable mirror of /admin/tonight. Polled by auto-refresh."""
    n = night if night in dashboard.ATHENS_NIGHTS else dashboard.latest_active_night()
    return JSONResponse(dashboard.collect_night_state(n))


@app.get("/admin/tonight/transcription", response_class=HTMLResponse)
def admin_tonight_transcription(
    request: Request,
    night: int | None = None,
    _: str = Depends(require_admin),
):
    """Per-session transcription stage detail, scoped to one night.

    Replaces "All statuses" as the canonical operator-facing transcription
    drilldown. Filters sessions by ai_assembly + day mapping for the
    selected night, so the table reflects exactly the night the operator
    was just looking at on /admin/tonight.
    """
    n = night if night in dashboard.ATHENS_NIGHTS else dashboard.latest_active_night()
    night_to_day = {1: "Day One", 2: "Day Two", 3: "Day Three"}
    target_day = night_to_day.get(n)

    sessions = load_sessions()
    flagged = [
        s for s in sessions
        if s.ai_assembly and s.day == target_day
    ]
    rows = []
    for s in flagged:
        sdir = session_dir(s)
        if not sdir:
            continue
        st = pipeline.infer_state(sdir) if sdir.exists() else {"state": None}
        # Vendor sidecars: flag the presence so the template can show a
        # "warnings" / "error" file link without re-reading the files.
        has_vendor_warnings = sdir.exists() and (sdir / "vendor.warnings").exists()
        has_vendor_error = sdir.exists() and (sdir / "vendor.error").exists()
        rows.append({
            "session": s,
            "status": st,
            "has_vendor_warnings": has_vendor_warnings,
            "has_vendor_error": has_vendor_error,
        })
    order = {"error": 0, "normalizing": 1, "transcribing": 1, "received": 2, "done": 3, None: 4}
    rows.sort(key=lambda r: (
        order.get(r["status"].get("state"), 9),
        r["session"].day_index,
        r["session"].date_time_start or r["session"].start_time,
    ))
    return templates.TemplateResponse(
        request, "admin_transcription.html",
        {
            "rows": rows,
            "night": n,
            "all_nights": dashboard.ATHENS_NIGHTS,
            "target_day": target_day,
            "role": "admin",
        },
    )


@app.get("/admin/tonight/voice", response_class=HTMLResponse)
def admin_tonight_voice(
    request: Request,
    night: int | None = None,
    _: str = Depends(require_admin),
):
    """Voice Pipeline drilldown: Step 1 grid + validation grid + Step 2 +
    continuity. C23 Phase B (2026-05-03)."""
    n = night if night in dashboard.ATHENS_NIGHTS else dashboard.latest_active_night()
    payload = dashboard.collect_voice_detail(n)
    # Build a (voice, theme) → step1_cell index for fast template lookup.
    s1_index = {(c["voice_slug"], c["theme_id"]): c for c in payload["step1_cells"]}
    v_index = {(c["voice_slug"], c["theme_id"]): c for c in payload["validation_cells"]}
    return templates.TemplateResponse(
        request, "admin_voice.html",
        {
            "payload": payload,
            "night": n,
            "all_nights": dashboard.ATHENS_NIGHTS,
            "s1_index": s1_index,
            "v_index": v_index,
            "role": "admin",
        },
    )


@app.get("/admin/tonight/voice.json")
def admin_tonight_voice_json(
    night: int | None = None,
    _: str = Depends(require_admin),
):
    n = night if night in dashboard.ATHENS_NIGHTS else dashboard.latest_active_night()
    return JSONResponse(dashboard.collect_voice_detail(n))


# --- C23 Phase C drilldowns: Researcher / Provocateur / Publish ------------


@app.get("/admin/tonight/researcher", response_class=HTMLResponse)
def admin_tonight_researcher(
    request: Request,
    night: int | None = None,
    _: str = Depends(require_admin),
):
    """Researcher Pipeline drilldown: theme/cluster tree + per-session
    extraction summary. C23 Phase C (2026-05-03)."""
    n = night if night in dashboard.ATHENS_NIGHTS else dashboard.latest_active_night()
    payload = dashboard.collect_researcher_detail(n)
    return templates.TemplateResponse(
        request, "admin_researcher.html",
        {
            "payload": payload,
            "night": n,
            "all_nights": dashboard.ATHENS_NIGHTS,
            "role": "admin",
        },
    )


@app.get("/admin/tonight/researcher.json")
def admin_tonight_researcher_json(
    night: int | None = None,
    _: str = Depends(require_admin),
):
    n = night if night in dashboard.ATHENS_NIGHTS else dashboard.latest_active_night()
    return JSONResponse(dashboard.collect_researcher_detail(n))


@app.get("/admin/tonight/provocateur", response_class=HTMLResponse)
def admin_tonight_provocateur(
    request: Request,
    night: int | None = None,
    _: str = Depends(require_admin),
):
    """Provocateur Pipeline drilldown: triage matrix + formulation grid +
    theme flags + per-voice triage detail. C23 Phase C (2026-05-03)."""
    n = night if night in dashboard.ATHENS_NIGHTS else dashboard.latest_active_night()
    payload = dashboard.collect_provocateur_detail(n)
    # Build (voice, theme) → cell indices for fast template lookup.
    triage_index = {(c["voice_slug"], c["theme_id"]): c
                    for c in payload.get("triage_cells", [])}
    formulation_index = {(c["voice_slug"], c["theme_id"]): c
                         for c in payload.get("formulation_cells", [])}
    theme_flag_index = {tf.get("theme_id"): tf
                        for tf in payload.get("theme_flags", [])
                        if tf.get("theme_id")}
    return templates.TemplateResponse(
        request, "admin_provocateur.html",
        {
            "payload": payload,
            "night": n,
            "all_nights": dashboard.ATHENS_NIGHTS,
            "triage_index": triage_index,
            "formulation_index": formulation_index,
            "theme_flag_index": theme_flag_index,
            "role": "admin",
        },
    )


@app.get("/admin/tonight/provocateur.json")
def admin_tonight_provocateur_json(
    night: int | None = None,
    _: str = Depends(require_admin),
):
    n = night if night in dashboard.ATHENS_NIGHTS else dashboard.latest_active_night()
    return JSONResponse(dashboard.collect_provocateur_detail(n))


@app.get("/admin/tonight/publish", response_class=HTMLResponse)
def admin_tonight_publish(
    request: Request,
    night: int | None = None,
    _: str = Depends(require_admin),
):
    """Publish stage drilldown: per-voice publish artifact rows +
    night-level index. C23 Phase C (2026-05-03)."""
    n = night if night in dashboard.ATHENS_NIGHTS else dashboard.latest_active_night()
    payload = dashboard.collect_publish_detail(n)
    return templates.TemplateResponse(
        request, "admin_publish.html",
        {
            "payload": payload,
            "night": n,
            "all_nights": dashboard.ATHENS_NIGHTS,
            "role": "admin",
        },
    )


@app.get("/admin/tonight/publish.json")
def admin_tonight_publish_json(
    night: int | None = None,
    _: str = Depends(require_admin),
):
    n = night if night in dashboard.ATHENS_NIGHTS else dashboard.latest_active_night()
    return JSONResponse(dashboard.collect_publish_detail(n))


@app.get("/admin/tonight/editor", response_class=HTMLResponse)
def admin_tonight_editor(
    request: Request,
    night: int | None = None,
    _: str = Depends(require_admin),
):
    """Editor Pipeline drilldown: per-dossier kicker/headline/word count +
    routing decisions + refusals. Post-B1 (2026-05-03 PM)."""
    n = night if night in dashboard.ATHENS_NIGHTS else dashboard.latest_active_night()
    payload = dashboard.collect_editor_detail(n)
    return templates.TemplateResponse(
        request, "admin_editor.html",
        {
            "payload": payload,
            "night": n,
            "all_nights": dashboard.ATHENS_NIGHTS,
            "role": "admin",
        },
    )


@app.get("/admin/tonight/editor.json")
def admin_tonight_editor_json(
    night: int | None = None,
    _: str = Depends(require_admin),
):
    n = night if night in dashboard.ATHENS_NIGHTS else dashboard.latest_active_night()
    return JSONResponse(dashboard.collect_editor_detail(n))


# --- /admin/file: read-only file viewer (C23 UX feedback, 2026-05-03) -------


_VIEWABLE_SUFFIXES = {".json", ".log", ".md", ".txt", ".flag"}
_MAX_VIEWABLE_BYTES = 10 * 1024 * 1024  # 10 MiB


def _resolve_under_project_root(rel_path: str) -> Path:
    """Resolve `rel_path` (operator-supplied) under PROJECT_ROOT safely.

    Traversal protection: normalize the relative path (collapse `..` /
    `.`) and reject if it escapes the root via `..` segments. We do NOT
    `.resolve()` symlinks — operators commonly stage their PROJECT_ROOT
    via symlinks (e.g. `runs/athens_night_1` → an out-of-tree dryrun
    dir, or `published_artifacts` → a network share). Resolving would
    reject those as escapes.

    Rejects:
      - absolute paths
      - paths whose normalized form escapes PROJECT_ROOT via `..`
      - paths to non-regular files
      - paths with disallowed suffixes
      - files larger than _MAX_VIEWABLE_BYTES

    Raises HTTPException on any rejection.
    """
    import os
    from .config import PROJECT_ROOT

    if not rel_path:
        raise HTTPException(http.HTTP_400_BAD_REQUEST, detail="missing path")
    p = Path(rel_path)
    if p.is_absolute():
        raise HTTPException(
            http.HTTP_400_BAD_REQUEST,
            detail="path must be relative to PROJECT_ROOT",
        )
    # Normalize without resolving symlinks. Reject any normalized path
    # that begins with `..` (traversal) or contains `..` segments after
    # normalization.
    normalized = os.path.normpath(rel_path)
    if normalized.startswith("..") or normalized == ".":
        raise HTTPException(
            http.HTTP_403_FORBIDDEN,
            detail="path escapes PROJECT_ROOT",
        )
    parts = Path(normalized).parts
    if any(part == ".." for part in parts):
        raise HTTPException(
            http.HTTP_403_FORBIDDEN,
            detail="path escapes PROJECT_ROOT",
        )
    candidate = PROJECT_ROOT / normalized
    if not candidate.exists():
        raise HTTPException(http.HTTP_404_NOT_FOUND, detail="file not found")
    if not candidate.is_file():
        raise HTTPException(
            http.HTTP_400_BAD_REQUEST, detail="not a regular file",
        )
    suffix = candidate.suffix.lower()
    if suffix not in _VIEWABLE_SUFFIXES:
        raise HTTPException(
            http.HTTP_400_BAD_REQUEST,
            detail=f"suffix {suffix!r} not viewable; allowed: {sorted(_VIEWABLE_SUFFIXES)}",
        )
    if candidate.stat().st_size > _MAX_VIEWABLE_BYTES:
        raise HTTPException(
            http.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"file exceeds {_MAX_VIEWABLE_BYTES} bytes",
        )
    return candidate


@app.get("/admin/file")
def admin_file(
    path: str,
    _: str = Depends(require_admin),
):
    """Read-only viewer for files under PROJECT_ROOT.

    Used by dashboard templates to make file paths clickable. Restricted
    to JSON / log / md / txt / flag files; max 10 MiB; admin-gated;
    path-traversal-protected.
    """
    target = _resolve_under_project_root(path)
    suffix = target.suffix.lower()
    media_types = {
        ".json": "application/json",
        ".log":  "text/plain; charset=utf-8",
        ".md":   "text/plain; charset=utf-8",
        ".txt":  "text/plain; charset=utf-8",
        ".flag": "text/plain; charset=utf-8",
    }
    media_type = media_types.get(suffix, "text/plain; charset=utf-8")
    return Response(
        content=target.read_bytes(),
        media_type=media_type,
        headers={
            "Cache-Control": "no-store",
            # Inline disposition so browsers render JSON/text in-tab,
            # not download.
            "Content-Disposition": f'inline; filename="{target.name}"',
        },
    )


# --- /admin/render: schema-aware artifact viewer (2026-05-03 dryrun) --------


@app.get("/admin/render", response_class=HTMLResponse)
def admin_render(
    request: Request,
    path: str,
    fragment: int = 0,
    _: str = Depends(require_admin),
):
    """Schema-aware HTML view of a known runtime artifact JSON.

    Detects file type by PROJECT_ROOT-relative path pattern (Step 1 reasoning,
    Step 2 artifact, formulation, validation, etc.) and renders the prose-heavy
    fields cleanly instead of dumping raw JSON. Unknown types fall back to a
    pretty-printed JSON view.

    `?fragment=1` returns just the rendered body (no base.html nav/header) —
    used by the modal-overlay JS in app.js so operators can peek at an
    artifact without losing dashboard context.

    Reuses _resolve_under_project_root() for the same security guarantees as
    /admin/file (admin-gated, traversal-protected, .json only here).
    """
    target = _resolve_under_project_root(path)
    if target.suffix.lower() != ".json":
        raise HTTPException(
            http.HTTP_400_BAD_REQUEST,
            detail="render only supports .json files",
        )
    try:
        data = json.loads(target.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise HTTPException(
            http.HTTP_400_BAD_REQUEST,
            detail=f"file is not valid JSON: {e}",
        )

    from .render import detect_artifact
    template_name, label = detect_artifact(path)

    return templates.TemplateResponse(
        request,
        template_name,
        {
            "rel_path": path,
            "label": label,
            "data": data,
            "json_pretty": json.dumps(data, indent=2, ensure_ascii=False),
            "static_version": STATIC_VERSION,
            "parent_template": (
                "admin_render_fragment_base.html" if fragment else "base.html"
            ),
        },
    )
