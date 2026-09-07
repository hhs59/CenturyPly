import { useEffect, useState } from "react";
import QRCode from "qrcode";
import { publishPhoto } from "../services/photoApi.js";

export default function PhotoQr({ blob, ticket }) {
  const [attempt, setAttempt] = useState(0);
  const [state, setState] = useState({ status: "loading" });

  useEffect(() => {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 60000);
    let active = true;
    setState({ status: "loading" });
    async function publish() {
      try {
        if (!ticket) throw new Error("QR publishing is unavailable.");
        const photo = await publishPhoto(blob, ticket, controller.signal);
        const url = new URL(photo.photo_url, window.location.origin).href;
        const image = await QRCode.toDataURL(url, { width: 240, margin: 4, errorCorrectionLevel: "M" });
        if (active) setState({ status: "ready", url, image });
      } catch {
        if (active) setState({ status: "error" });
      } finally {
        clearTimeout(timer);
      }
    }
    void publish();
    return () => { active = false; clearTimeout(timer); controller.abort(); };
  }, [blob, ticket, attempt]);

  return (
    <aside className="photo-qr" aria-label="Download on your phone" aria-live="polite">
      {state.status === "loading" && <p role="status">Preparing QR…</p>}
      {state.status === "error" && <><p>QR unavailable</p><button type="button" className="secondary-button" onClick={() => setAttempt((value) => value + 1)}>Retry QR</button></>}
      {state.status === "ready" && <><a href={state.url} target="_blank" rel="noreferrer" aria-label="Open your photo download page"><img src={state.image} alt="Scan to download your portrait" width="240" height="240" /></a><p>Scan to download</p></>}
    </aside>
  );
}
