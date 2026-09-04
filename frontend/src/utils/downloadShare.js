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

export function downloadBlob({ blob, objectUrl, name }) {
  if (!blob || !blob.size) {
    throw new Error("The final image is not available for download.");
  }
  const url = objectUrl || URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = safePortraitFilename(name, blob.type);
  anchor.rel = "noopener";
  anchor.style.display = "none";
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  if (!objectUrl) {
    window.setTimeout(() => URL.revokeObjectURL(url), 1000);
  }
  return { filename: anchor.download, byteCount: blob.size };
}

export async function sharePortrait({ blob, objectUrl, name }) {
  if (!blob || !blob.size) {
    throw new Error("The final image is not available to share.");
  }
  const filename = safePortraitFilename(name, blob.type);
  const file = new File([blob], filename, { type: blob.type || "image/jpeg" });
  let canShareFiles = false;
  try {
    canShareFiles = typeof navigator !== "undefined"
      && typeof navigator.share === "function"
      && typeof navigator.canShare === "function"
      && navigator.canShare({ files: [file] });
  } catch {
    canShareFiles = false;
  }

  if (!canShareFiles) {
    return { mode: "download", ...downloadBlob({ blob, objectUrl, name }) };
  }

  try {
    await navigator.share({
      title: "Century Ply heritage portrait",
      text: "A Vietnamese heritage portrait from the Century Ply AI Photobooth.",
      files: [file],
    });
    return { mode: "share", filename, byteCount: blob.size };
  } catch (error) {
    if (error?.name === "AbortError") {
      return { mode: "cancelled", filename, byteCount: blob.size };
    }
    throw error;
  }
}
