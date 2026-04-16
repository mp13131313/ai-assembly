"""FastAPI ingest app. Routes, lifespan, background tasks.

Design principles (see plan):
  * The filesystem is authoritative; status.json under each session dir is
    the single source of truth.
  * Transcription subprocesses are detached (start_new_session=True); if
    uvicorn restarts mid-run, reconcile_on_startup adopts them.
  * Upload body is streamed chunk-by-chunk, never buffered into RAM.
  * Single worker + asyncio.Semaphore serializes normalize+transcribe.
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

from . import pipeline
from .auth import require_auth
from .config import (
    ALLOWED_EXTENSIONS,
    MAX_UPLOAD_BYTES,
    MIN_FREE_BYTES,
    STATIC_DIR,
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


@app.get("/", response_class=HTMLResponse)
def index(request: Request, _: str = Depends(require_auth)):
    sessions = load_sessions()
    flagged = [s for s in sessions if s.ai_assembly]
    # Group by day_index for the template; also pass a list of days present.
    by_day: dict[str, list[Session]] = {}
    for s in flagged:
        by_day.setdefault(s.day, []).append(s)
    # Attach current state per session so we can color-dot the cards.
    states: dict[str, str | None] = {}
    for s in flagged:
        sdir = session_dir(s)
        if sdir:
            states[s.session_id] = pipeline.infer_state(sdir).get("state")
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
        },
    )


@app.get("/status", response_class=HTMLResponse)
def overview(request: Request, _: str = Depends(require_auth)):
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
    rows.sort(key=lambda r: (order.get(r["status"].get("state"), 9), r["session"].day_index, r["session"].start_time))
    return templates.TemplateResponse(request, "overview.html", {"rows": rows})


@app.get("/status.json")
def overview_json(_: str = Depends(require_auth)):
    """Polled by the overview page to update state cells without a full reload."""
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
def session_detail(session_id: str, request: Request, _: str = Depends(require_auth)):
    sess, sdir = _require_session_and_dir(session_id)
    speakers = load_speakers()
    roster, missing_bios = derive_roster(sess, speakers)
    existing = _existing_audio_info(sdir) if sdir.exists() else None
    current = pipeline.infer_state(sdir) if sdir.exists() else {"state": None}
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
        },
    )


@app.post("/session/{session_id}/upload")
async def upload(
    session_id: str,
    request: Request,
    background: BackgroundTasks,
    _: str = Depends(require_auth),
):
    """Stream request body to disk, validate, kick off pipeline.

    Query params:
      filename: client-provided filename (we only use its extension)
      overwrite: "true" to allow replacing an existing audio.m4a
    """
    sess, sdir = _require_session_and_dir(session_id)

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
            raise HTTPException(
                http.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"upload failed: {e}",
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
def session_status(session_id: str, request: Request, _: str = Depends(require_auth)):
    sess, sdir = _require_session_and_dir(session_id)
    return templates.TemplateResponse(
        request,
        "status.html",
        {
            "session": sess,
            "run_id": run_for_session(sess),
        },
    )


@app.get("/session/{session_id}/status.json")
def session_status_json(session_id: str, _: str = Depends(require_auth)):
    sess, sdir = _require_session_and_dir(session_id)
    if not sdir.exists():
        return JSONResponse({"state": None, "session_id": sess.session_id})
    return JSONResponse(pipeline.infer_state(sdir))


@app.post("/session/{session_id}/retry")
def session_retry(session_id: str, _: str = Depends(require_auth)):
    """Re-spawn Stage 0 using the existing audio.m4a (after a transient error)."""
    sess, sdir = _require_session_and_dir(session_id)
    if not sdir.exists():
        raise HTTPException(http.HTTP_404_NOT_FOUND, detail="no session dir")
    # Rebuild session.json too — speakers.json may have been updated with new bios.
    speakers = load_speakers()
    session_json_path = sdir / "session.json"
    write_json_atomic(session_json_path, build_session_json(sess, speakers))
    st = pipeline.spawn_retry(sdir, session_json_path)
    return JSONResponse(st)
