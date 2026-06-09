const MAX_UPLOAD_BYTES = 25 * 1024 * 1024;
const REQUEST_TIMEOUT_MS = 120000;
const API_BASE = (window.SQWASH_CONFIG && window.SQWASH_CONFIG.apiBase) || "";

const dropZone = document.getElementById("drop-zone");
const fileInput = document.getElementById("file-input");
const fileNameEl = document.getElementById("file-name");
const dpiInput = document.getElementById("dpi-input");
const qualityInput = document.getElementById("quality-input");
const qualityValue = document.getElementById("quality-value");
const flattenBtn = document.getElementById("flatten-btn");
const statusEl = document.getElementById("status");

let selectedFile = null;

function setStatus(message, type = "info") {
  statusEl.textContent = message;
  statusEl.className = `status ${type}`;
}

function setSelectedFile(file) {
  if (!file) {
    selectedFile = null;
    fileNameEl.textContent = "No file selected";
    flattenBtn.disabled = true;
    return;
  }

  if (!file.name.toLowerCase().endsWith(".pdf")) {
    setStatus("Please choose a PDF file.", "error");
    return;
  }

  if (file.size > MAX_UPLOAD_BYTES) {
    setStatus("File exceeds the 25 MB upload limit.", "error");
    return;
  }

  selectedFile = file;
  fileNameEl.textContent = `${file.name} (${formatSize(file.size)})`;
  flattenBtn.disabled = false;
  setStatus("");
}

function formatSize(bytes) {
  const units = ["B", "KB", "MB", "GB"];
  let size = bytes;
  let unitIndex = 0;

  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024;
    unitIndex += 1;
  }

  return `${size.toFixed(unitIndex === 0 ? 0 : 2)} ${units[unitIndex]}`;
}

function parseErrorMessage(response, fallback) {
  return response
    .json()
    .then((data) => data.detail || fallback)
    .catch(() => fallback);
}

function extractFilename(contentDisposition, fallback) {
  if (!contentDisposition) {
    return fallback;
  }

  const match = /filename="([^"]+)"/i.exec(contentDisposition);
  return match ? match[1] : fallback;
}

function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

async function flattenPdf() {
  if (!selectedFile) {
    return;
  }

  const dpi = Number(dpiInput.value);
  const jpgQuality = Number(qualityInput.value);

  if (Number.isNaN(dpi) || dpi < 72 || dpi > 300) {
    setStatus("DPI must be between 72 and 300.", "error");
    return;
  }

  if (Number.isNaN(jpgQuality) || jpgQuality < 0 || jpgQuality > 100) {
    setStatus("JPEG quality must be between 0 and 100.", "error");
    return;
  }

  const formData = new FormData();
  formData.append("file", selectedFile);
  formData.append("dpi", String(dpi));
  formData.append("jpg_quality", String(jpgQuality));

  flattenBtn.disabled = true;
  setStatus("Flattening PDF...", "info");

  const controller = new AbortController();
  const timeoutId = window.setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

  try {
    const response = await fetch(`${API_BASE}/api/flatten`, {
      method: "POST",
      body: formData,
      signal: controller.signal,
    });

    if (!response.ok) {
      const fallback = `Request failed with status ${response.status}.`;
      const message = await parseErrorMessage(response, fallback);
      throw new Error(message);
    }

    const blob = await response.blob();
    const fallbackName = `${selectedFile.name.replace(/\.pdf$/i, "")}-flat-${dpi}.pdf`;
    const filename = extractFilename(
      response.headers.get("Content-Disposition"),
      fallbackName,
    );

    downloadBlob(blob, filename);
    setStatus("Flattened PDF downloaded.", "success");
  } catch (error) {
    if (error.name === "AbortError") {
      setStatus(
        "Request timed out. The server may be waking up on the free tier. Retry in about 30 seconds.",
        "error",
      );
    } else {
      setStatus(error.message || "Failed to flatten PDF.", "error");
    }
  } finally {
    window.clearTimeout(timeoutId);
    flattenBtn.disabled = !selectedFile;
  }
}

dropZone.addEventListener("click", () => fileInput.click());

dropZone.addEventListener("keydown", (event) => {
  if (event.key === "Enter" || event.key === " ") {
    event.preventDefault();
    fileInput.click();
  }
});

fileInput.addEventListener("change", () => {
  const file = fileInput.files[0];
  setSelectedFile(file || null);
});

dropZone.addEventListener("dragover", (event) => {
  event.preventDefault();
  dropZone.classList.add("dragover");
});

dropZone.addEventListener("dragleave", () => {
  dropZone.classList.remove("dragover");
});

dropZone.addEventListener("drop", (event) => {
  event.preventDefault();
  dropZone.classList.remove("dragover");
  const file = event.dataTransfer.files[0];
  setSelectedFile(file || null);
});

qualityInput.addEventListener("input", () => {
  qualityValue.textContent = qualityInput.value;
});

flattenBtn.addEventListener("click", flattenPdf);
