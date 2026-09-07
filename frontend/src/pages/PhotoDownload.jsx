import { useEffect, useRef, useState } from "react";
import { Download } from "lucide-react";
import { downloadPhoto, getPhoto } from "../services/photoApi.js";
import { downloadBlob } from "../utils/downloadShare.js";

export default function PhotoDownload({ token }) {
  const [photo, setPhoto] = useState(null);
  const [error, setError] = useState(null);
  const [attempt, setAttempt] = useState(0);
  const [busy, setBusy] = useState(false);
  const eventRef = useRef(null);
  const busyRef = useRef(false);

  useEffect(() => {
    const controller = new AbortController();
    setError(null);
    setPhoto(null);
    const timer = setTimeout(() => controller.abort(), 30000);
    let active = true;
    getPhoto(token, controller.signal).then((value) => {
      if (active) setPhoto(value);
    }).catch((failure) => {
      if (active) setError({ message: failure.name === "AbortError" ? "Could not load your photo. Please retry." : failure.message, status: failure.status });
    }).finally(() => clearTimeout(timer));
    return () => { active = false; clearTimeout(timer); controller.abort(); };
  }, [token, attempt]);

  async function download() {
    if (busyRef.current) return;
    busyRef.current = true;
    setBusy(true);
    setError(null);
    try {
      eventRef.current ||= Array.from(crypto.getRandomValues(new Uint8Array(16)), (byte) => byte.toString(16).padStart(2, "0")).join("");
      const blob = await downloadPhoto(token, eventRef.current);
      downloadBlob({ blob, name: "Century Ply" });
      eventRef.current = null;
    } catch (failure) {
      setError({ message: failure.message, status: failure.status });
    } finally {
      busyRef.current = false;
      setBusy(false);
    }
  }

  const gone = error?.status === 404 || error?.status === 410;
  return (
    <main className="app-shell phone-photo-shell">
      <section className="main-panel phone-photo-panel" aria-labelledby="phone-photo-title">
        <p className="brand-wordmark">Century Ply</p>
        <h1 id="phone-photo-title">{gone ? "Photo unavailable" : "Your portrait"}</h1>
        {!photo && !error && <p role="status">Loading your photo…</p>}
        {photo && !gone && <><img className="phone-portrait" src={photo.image_url} alt="Your Century Ply branded portrait" onError={() => setError({ message: "Could not load your photo. Please retry." })} /><button type="button" className="primary-button" disabled={busy} onClick={download}><Download size={19} />{busy ? "Downloading…" : "Download photo"}</button></>}
        {error && <p role="alert">{error.message}</p>}
        {error && !gone && !busy && <button className="secondary-button" type="button" onClick={() => setAttempt((value) => value + 1)}>Retry</button>}
      </section>
    </main>
  );
}
