/* Ingest app frontend. Three modes depending on which page loaded us.
 *
 * (1) Index page — chip + search filtering of session cards.
 * (2) Session detail — file picker + XHR upload with progress bar.
 * (3) Status page — polls /session/{sid}/status.json every 3s.
 */

(() => {
  "use strict";

  // --- (1) Index filters ----------------------------------------------------

  const chipRow = document.getElementById("day-chips");
  const search = document.getElementById("search");
  const cards = document.querySelectorAll(".session-card");

  function applyFilters() {
    if (!chipRow) return;
    const active = chipRow.querySelector(".chip.active");
    const day = active ? active.dataset.day : "";
    const q = search ? search.value.trim().toLowerCase() : "";

    document.querySelectorAll(".day-section").forEach((sec) => {
      const matchDay = !day || sec.dataset.day === day;
      let anyVisible = false;
      sec.querySelectorAll(".session-card").forEach((card) => {
        const matchQ = !q || (card.dataset.search || "").includes(q);
        const show = matchDay && matchQ;
        card.classList.toggle("hidden", !show);
        if (show) anyVisible = true;
      });
      sec.classList.toggle("hidden", !anyVisible);
    });
  }

  if (chipRow) {
    chipRow.addEventListener("click", (e) => {
      const chip = e.target.closest(".chip");
      if (!chip) return;
      chipRow.querySelectorAll(".chip").forEach((c) => c.classList.remove("active"));
      chip.classList.add("active");
      applyFilters();
    });
  }
  if (search) {
    search.addEventListener("input", applyFilters);
  }

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

  // --- (3) Status polling ---------------------------------------------------

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

    function render(st) {
      const state = st.state || "none";
      badge.className = "state-" + state;
      badge.textContent = state === "none" ? "not started" : state;

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
