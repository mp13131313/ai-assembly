/* Ingest app frontend. Three modes depending on which page loaded us.
 *
 * (1) Index page — chip + search filtering of session cards.
 * (2) Session detail — file picker + XHR upload with progress bar.
 * (3) Status page — polls /session/{sid}/status.json every 3s.
 */

(() => {
  "use strict";

  // --- (1) Index filters ----------------------------------------------------

  const dayChips = document.getElementById("day-chips");
  const venueChips = document.getElementById("venue-chips");
  const search = document.getElementById("search");

  function activeValue(row, attr) {
    if (!row) return "";
    const chip = row.querySelector(".chip.active");
    return chip ? chip.dataset[attr] || "" : "";
  }

  function applyFilters() {
    const day = activeValue(dayChips, "day");
    const venue = activeValue(venueChips, "venue");
    const q = search ? search.value.trim().toLowerCase() : "";

    document.querySelectorAll(".day-section").forEach((sec) => {
      const matchDay = !day || sec.dataset.day === day;
      let anyVisible = false;
      sec.querySelectorAll(".session-card").forEach((card) => {
        const matchVenue = !venue || card.dataset.venue === venue;
        const matchQ = !q || (card.dataset.search || "").includes(q);
        const show = matchDay && matchVenue && matchQ;
        card.classList.toggle("hidden", !show);
        if (show) anyVisible = true;
      });
      sec.classList.toggle("hidden", !anyVisible);
    });
  }

  function wireChipRow(row) {
    if (!row) return;
    row.addEventListener("click", (e) => {
      const chip = e.target.closest(".chip");
      if (!chip) return;
      row.querySelectorAll(".chip").forEach((c) => c.classList.remove("active"));
      chip.classList.add("active");
      applyFilters();
    });
  }
  wireChipRow(dayChips);
  wireChipRow(venueChips);
  if (search) search.addEventListener("input", applyFilters);

  // --- (2) Upload form ------------------------------------------------------

  const uploadBox = document.getElementById("upload-box");
  if (uploadBox) {
    const sid = uploadBox.dataset.sessionId;
    const hasExisting = uploadBox.dataset.hasExisting === "true";
    const form = document.getElementById("upload-form");
    const fileInput = document.getElementById("file-input");
    const label = document.querySelector(".file-picker-label");
    const submit = document.getElementById("upload-submit");
    const progressBox = document.getElementById("upload-progress");
    const progressBar = document.getElementById("progress-bar");
    const progressText = document.getElementById("progress-text");
    const errorBox = document.getElementById("upload-error");

    fileInput.addEventListener("change", () => {
      const file = fileInput.files[0];
      if (!file) {
        label.textContent = "Choose an audio file…";
        submit.disabled = true;
        return;
      }
      const mb = (file.size / 1024 / 1024).toFixed(1);
      label.textContent = `${file.name} (${mb} MB)`;
      submit.disabled = false;
    });

    form.addEventListener("submit", (e) => {
      e.preventDefault();
      const file = fileInput.files[0];
      if (!file) return;

      if (hasExisting) {
        const ok = confirm(
          "This session already has audio uploaded. " +
          "Overwriting will discard the existing file and re-run Stage 0. " +
          "Continue?"
        );
        if (!ok) return;
      }

      errorBox.classList.add("hidden");
      progressBox.classList.remove("hidden");
      submit.disabled = true;

      const url =
        `/session/${encodeURIComponent(sid)}/upload` +
        `?filename=${encodeURIComponent(file.name)}` +
        (hasExisting ? `&overwrite=true` : "");

      const xhr = new XMLHttpRequest();
      xhr.open("POST", url, true);
      xhr.upload.addEventListener("progress", (ev) => {
        if (ev.lengthComputable) {
          const pct = Math.round((ev.loaded / ev.total) * 100);
          progressBar.value = pct;
          progressText.textContent =
            `Uploading… ${pct}% ` +
            `(${(ev.loaded / 1024 / 1024).toFixed(1)} / ` +
            `${(ev.total / 1024 / 1024).toFixed(1)} MB)`;
        }
      });
      xhr.addEventListener("load", () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          progressText.textContent = "Upload complete. Redirecting…";
          try {
            const resp = JSON.parse(xhr.responseText);
            window.location = resp.status_url;
          } catch (_) {
            window.location = `/session/${encodeURIComponent(sid)}/status`;
          }
        } else {
          let msg = `Upload failed (HTTP ${xhr.status}).`;
          try {
            const j = JSON.parse(xhr.responseText);
            if (j.detail) msg += ` ${j.detail}`;
          } catch (_) {}
          progressBox.classList.add("hidden");
          errorBox.textContent = msg;
          errorBox.classList.remove("hidden");
          submit.disabled = false;
        }
      });
      xhr.addEventListener("error", () => {
        progressBox.classList.add("hidden");
        errorBox.textContent = "Network error during upload. Retry.";
        errorBox.classList.remove("hidden");
        submit.disabled = false;
      });
      xhr.send(file);
    });
  }

  // --- (3) Overview live update --------------------------------------------

  const overviewTable = document.getElementById("overview-table");
  if (overviewTable) {
    const STATE_LABEL_MAP = {
      "received":               "received",
      "normalizing":            "normalizing",
      "transcribing":           "transcribing",
      "transcribing_asr":       "transcribing · ASR",
      "transcribing_speaker_id":"transcribing · speaker ID",
      "transcribing_cleaning":  "transcribing · cleaning",
      "transcribing_finalizing":"transcribing · finalizing",
      "done":                   "done",
      "error":                  "error",
    };

    async function pollOverview() {
      try {
        const r = await fetch("/status.json");
        const rows = await r.json();
        let anyActive = false;
        rows.forEach(({ session_id, state, substate }) => {
          const tr = overviewTable.querySelector(`tr[data-session-id="${session_id}"]`);
          if (!tr) return;
          const display = (state === "transcribing" && substate) ? substate : state;
          const dot = tr.querySelector(".dot");
          const label = tr.querySelector(".state-label");
          if (dot) dot.className = "dot dot-" + (state || "none");
          if (label) label.textContent = STATE_LABEL_MAP[display] || display || "not started";
          if (state && !["done","error"].includes(state)) anyActive = true;
        });
        if (!anyActive && overviewTimer) {
          clearInterval(overviewTimer);
          overviewTimer = null;
        }
      } catch (_) {}
    }

    let overviewTimer = null;
    if (overviewTable.dataset.hasActive === "true") {
      overviewTimer = setInterval(pollOverview, 3000);
    }
  }

  // --- (4) Pipeline crumbs (status page footer) ----------------------------

  // crumb-id → index in the pipeline sequence
  const CRUMBS = [
    { id: "crumb-received",    activeOn: ["received"],                norm: true },
    { id: "crumb-normalizing", activeOn: ["normalizing"],             norm: true },
    { id: "crumb-asr",         activeOn: ["transcribing","transcribing_asr"] },
    { id: "crumb-speaker-id",  activeOn: ["transcribing_speaker_id"] },
    { id: "crumb-cleaning",    activeOn: ["transcribing_cleaning"]   },
    { id: "crumb-finalizing",  activeOn: ["transcribing_finalizing"] },
    { id: "crumb-done",        activeOn: ["done"]                    },
  ];

  function renderCrumbs(st) {
    const state = st.state || "none";
    const display = (state === "transcribing" && st.substate) ? st.substate : state;
    let activeIdx = -1;
    if (state === "done") {
      activeIdx = CRUMBS.length; // all done
    } else {
      activeIdx = CRUMBS.findIndex(c => c.activeOn.includes(display));
    }

    CRUMBS.forEach((c, i) => {
      const el = document.getElementById(c.id);
      if (!el) return;
      el.className = "";
      if (state === "error") {
        el.className = i === activeIdx ? "crumb-error" : "crumb-pending";
      } else if (i < activeIdx || state === "done") {
        el.className = c.norm ? "crumb-done-norm" : "crumb-done";
      } else if (i === activeIdx) {
        el.className = c.norm ? "crumb-active-norm" : "crumb-active";
      } else {
        el.className = "crumb-pending";
      }
    });
  }

  // --- (5) Status polling ---------------------------------------------------

  const statusBox = document.getElementById("status-box");
  if (statusBox) {
    const sid = statusBox.dataset.sessionId;
    const badge = document.getElementById("state-badge");
    const elapsed = document.getElementById("elapsed");
    const errorDetail = document.getElementById("error-detail");
    const actions = document.getElementById("actions");

    let startedAt = null;
    let pollTimer = null;

    function fmtElapsed(secs) {
      if (secs < 60) return `${secs}s`;
      const m = Math.floor(secs / 60);
      const s = secs % 60;
      return `${m}m ${s.toString().padStart(2, "0")}s`;
    }

    function tickElapsed() {
      if (!startedAt) return;
      const secs = Math.floor((Date.now() - startedAt.getTime()) / 1000);
      elapsed.textContent = `(elapsed ${fmtElapsed(secs)})`;
    }

    async function poll() {
      try {
        const r = await fetch(`/session/${encodeURIComponent(sid)}/status.json`);
        const st = await r.json();
        render(st);
      } catch (e) {
        // network blip — keep polling
      }
    }

    const STATE_LABELS = {
      "none":                   "not started",
      "received":               "received",
      "normalizing":            "normalizing audio",
      "transcribing":           "transcribing",
      "transcribing_asr":       "transcribing · ASR",
      "transcribing_speaker_id":"transcribing · speaker ID",
      "transcribing_cleaning":  "transcribing · cleaning",
      "transcribing_finalizing":"transcribing · finalizing",
      "done":                   "done",
      "error":                  "error",
    };

    function render(st) {
      const state = st.state || "none";
      // Use substate for badge display when the subprocess reports one.
      const displayState = (state === "transcribing" && st.substate) ? st.substate : state;
      badge.className = "state-" + displayState;
      badge.textContent = STATE_LABELS[displayState] || displayState;
      renderCrumbs(st);

      if (st.started_at && !startedAt) {
        startedAt = new Date(st.started_at);
      }
      if (["done", "error"].includes(state)) {
        startedAt = null;
        elapsed.textContent = "";
      } else {
        tickElapsed();
      }

      if (state === "error" && st.error) {
        errorDetail.textContent = "Error: " + st.error;
        errorDetail.classList.remove("hidden");
        actions.innerHTML =
          `<button id="retry-btn">Retry transcription</button>`;
        document.getElementById("retry-btn").addEventListener("click", async () => {
          const ok = confirm("Retry Stage 0 using the already-uploaded audio?");
          if (!ok) return;
          await fetch(`/session/${encodeURIComponent(sid)}/retry`, { method: "POST" });
          poll();
        });
      } else {
        errorDetail.classList.add("hidden");
        if (state === "done") {
          actions.innerHTML =
            `<p>✓ Transcription complete. <a href="/">Back to all sessions</a></p>`;
        } else {
          actions.innerHTML = "";
        }
      }

      if (["done", "error"].includes(state) && pollTimer) {
        clearInterval(pollTimer);
        pollTimer = null;
      }
    }

    poll();
    pollTimer = setInterval(poll, 3000);
    setInterval(tickElapsed, 1000);
  }
})();
