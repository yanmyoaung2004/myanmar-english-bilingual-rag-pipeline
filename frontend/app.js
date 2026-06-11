/* ── Toast notifications ── */
function showToast(message, type = "info") {
  const container = document.getElementById("toast-container");
  const el = document.createElement("div");
  el.className = `toast ${type}`;
  el.textContent = message;
  container.appendChild(el);
  setTimeout(() => { el.style.opacity = "0"; el.style.transition = "opacity 0.3s"; }, 3500);
  setTimeout(() => el.remove(), 4000);
}

/* ── Loading state helpers ── */
function setLoading(btnId, loading) {
  const btn = document.getElementById(btnId);
  if (!btn) return;
  btn.disabled = loading;
  btn.querySelector(".btn-text").classList.toggle("hidden", loading);
  btn.querySelector(".spinner").classList.toggle("hidden", !loading);
}

function showResult(containerId, html, type) {
  const el = document.getElementById(containerId);
  el.className = type || "";
  el.innerHTML = html;
  el.classList.remove("hidden");
}

function hideResult(containerId) {
  document.getElementById(containerId).classList.add("hidden");
}

/* ── Status check on load ── */
async function checkStatus() {
  const badge = document.getElementById("status-badge");
  try {
    const res = await fetch("/");
    if (!res.ok) throw new Error("Not OK");
    badge.textContent = "connected";
    badge.className = "badge connected";
  } catch {
    badge.textContent = "disconnected";
    badge.className = "badge disconnected";
  }
}

/* ── Query ── */
document.getElementById("query-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const input = document.getElementById("query-input");
  const question = input.value.trim();
  if (!question) return;

  hideResult("query-result");
  setLoading("query-btn", true);

  try {
    const res = await fetch("/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || `HTTP ${res.status}`);
    }
    const data = await res.json();
    showResult("query-result", `<h3>Answer</h3><p id="answer-text">${escapeHtml(data.answer)}</p>`);
    showToast("Answer received", "success");
  } catch (err) {
    showResult("query-result", `<p style="color:var(--error)">${escapeHtml(err.message)}</p>`, "error");
    showToast(err.message, "error");
  } finally {
    setLoading("query-btn", false);
  }
});

/* ── File upload (drag & drop + click) ── */
const dropZone = document.getElementById("drop-zone");
const fileInput = document.getElementById("file-input");
const uploadBtn = document.getElementById("upload-btn");

dropZone.addEventListener("click", () => fileInput.click());

dropZone.addEventListener("dragover", (e) => {
  e.preventDefault();
  dropZone.classList.add("drag-over");
});
dropZone.addEventListener("dragleave", () => dropZone.classList.remove("drag-over"));
dropZone.addEventListener("drop", (e) => {
  e.preventDefault();
  dropZone.classList.remove("drag-over");
  if (e.dataTransfer.files.length) {
    fileInput.files = e.dataTransfer.files;
    updateFileLabel();
  }
});

fileInput.addEventListener("change", updateFileLabel);

function updateFileLabel() {
  const file = fileInput.files[0];
  if (!file) {
    dropZone.classList.remove("has-file");
    dropZone.querySelector(".file-name")?.remove();
    uploadBtn.disabled = true;
    return;
  }
  dropZone.classList.add("has-file");
  let existing = dropZone.querySelector(".file-name");
  if (!existing) {
    existing = document.createElement("p");
    existing.className = "file-name";
    dropZone.appendChild(existing);
  }
  existing.textContent = `📄 ${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
  uploadBtn.disabled = false;
}

document.getElementById("upload-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const file = fileInput.files[0];
  if (!file) return;

  hideResult("upload-result");
  setLoading("upload-btn", true);

  const formData = new FormData();
  formData.append("file", file);

  try {
    const res = await fetch("/ingest", { method: "POST", body: formData });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || `HTTP ${res.status}`);
    }
    const data = await res.json();
    showResult(
      "upload-result",
      `<strong>✓ Uploaded successfully</strong><br>
       File: ${escapeHtml(data.file)}<br>
       Chunks indexed: ${data.chunks_added}<br>
       Embedding mode: ${data.embedding_mode}`,
      "success"
    );
    showToast(`Indexed ${data.chunks_added} chunks from ${data.file}`, "success");
    fileInput.value = "";
    updateFileLabel();
  } catch (err) {
    showResult("upload-result", `<strong>✗ Upload failed</strong><br>${escapeHtml(err.message)}`, "error");
    showToast(err.message, "error");
  } finally {
    setLoading("upload-btn", false);
  }
});

/* ── Export ── */
document.getElementById("export-btn").addEventListener("click", async () => {
  const version = document.getElementById("export-version").value.trim() || "v0.1.0";
  hideResult("export-result");
  setLoading("export-btn", true);

  try {
    const res = await fetch(`/export?version=${encodeURIComponent(version)}`);
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || `HTTP ${res.status}`);
    }
    const data = await res.json();
    showResult(
      "export-result",
      `<strong>✓ Export complete</strong><br>
       Version: ${escapeHtml(data.version)}<br>
       Pages: ${data.pages} · Characters: ${data.characters}<br>
       Path: ${escapeHtml(data.path)}`,
      "success"
    );
    showToast(`Exported ${data.pages} pages`, "success");
  } catch (err) {
    showResult("export-result", `<strong>✗ Export failed</strong><br>${escapeHtml(err.message)}`, "error");
    showToast(err.message, "error");
  } finally {
    setLoading("export-btn", false);
  }
});

/* ── Utility ── */
function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

/* ── Init ── */
checkStatus();
