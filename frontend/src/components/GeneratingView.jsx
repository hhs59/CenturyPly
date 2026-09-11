import { useEffect, useState } from "react";
import { RefreshCw } from "lucide-react";
import ErrorAlert from "./ErrorAlert.jsx";

const GENERATION_MESSAGES = [
  "Preparing your portrait…",
  "Preserving every guest’s features…",
  "Styling the traditional outfits…",
  "Building your selected setting…",
  "Finishing the final details…",
];

function PortraitSpinner() {
  return (
    <div className="portrait-spinner" role="img" aria-label="Portrait generation in progress">
      <span className="portrait-spinner-ring" />
      <span className="portrait-spinner-core">
        <strong>CP</strong>
        <small>Imperial portrait</small>
      </span>
    </div>
  );
}

function GeneratingView({ isGenerating, error, onRetry, onChangePhoto }) {
  const [messageIndex, setMessageIndex] = useState(0);

  useEffect(() => {
    if (!isGenerating) {
      setMessageIndex(0);
      return undefined;
    }

    setMessageIndex(0);
    const timer = window.setInterval(() => {
      setMessageIndex((current) => Math.min(current + 1, GENERATION_MESSAGES.length - 1));
    }, 8000);

    return () => window.clearInterval(timer);
  }, [isGenerating]);

  return (
    <section className="content-card generation-card" aria-labelledby="generation-heading" aria-busy={isGenerating}>
      <div className="card-heading">
        <h2 id="generation-heading" tabIndex={-1}>{error ? "The studio paused" : "Creating your portrait"}</h2>
      </div>

      {isGenerating ? (
        <div className="generation-status" role="status" aria-live="polite">
          <PortraitSpinner />
          <div className="generation-copy">
            <p className="generation-message" key={messageIndex}>{GENERATION_MESSAGES[messageIndex]}</p>
            <p className="generation-note">This may take a moment.</p>
          </div>
        </div>
      ) : (
        <>
          <ErrorAlert error={error} />
          <div className="generation-actions">
            {error ? (
              <button className="primary-button" type="button" onClick={onRetry}>
                <RefreshCw size={19} aria-hidden="true" /> Try again
              </button>
            ) : (
              <button className="secondary-button" type="button" onClick={onChangePhoto}>Change photo</button>
            )}
          </div>
        </>
      )}
    </section>
  );
}

export default GeneratingView;
