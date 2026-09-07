async function checked(response) {
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    const error = new Error(typeof body.detail === "string" ? body.detail : "Photo temporarily unavailable. Please retry.");
    error.status = response.status;
    throw error;
  }
  return response;
}

export async function publishPhoto(blob, ticket, signal) {
  const form = new FormData();
  form.append("image", blob, "century-ply-portrait.jpg");
  form.append("ticket", ticket);
  const response = await checked(await fetch("/api/photos/publish", { method: "POST", body: form, signal }));
  return response.json();
}

export async function getPhoto(token, signal) {
  const response = await checked(await fetch(`/api/photos/${encodeURIComponent(token)}`, { signal, cache: "no-store" }));
  return response.json();
}

export async function downloadPhoto(token, eventId) {
  const response = await checked(await fetch(`/api/photos/${encodeURIComponent(token)}/download`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ event_id: eventId }),
    signal: AbortSignal.timeout(60000),
  }));
  const blob = await response.blob();
  if (!blob.size || !blob.type.startsWith("image/")) throw new Error("Could not download the photo. Please retry.");
  return blob;
}
