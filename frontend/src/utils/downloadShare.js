function extensionForMimeType(mimeType) {
  if (mimeType === "image/png") return "png";
  if (mimeType === "image/webp") return "webp";
  return "jpg";
}

export function safePortraitFilename(name = "Century-Ply-Portrait", mimeType = "image/jpeg") {
  const asciiName = String(name ?? "Century Ply Portrait")
    .normalize("NFKD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-zA-Z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .toLowerCase() || "century-ply-portrait";
  return `${asciiName}-portrait.${extensionForMimeType(mimeType)}`;
}

export function downloadBlob({ blob, name }) {
  if (!blob || !blob.size) {
    throw new Error("The final image is not available for download.");
  }
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = safePortraitFilename(name, blob.type);
  anchor.rel = "noopener";
  anchor.style.display = "none";
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  window.setTimeout(() => URL.revokeObjectURL(url), 1000);
  return { filename: anchor.download, byteCount: blob.size };
}
