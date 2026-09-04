import { RefreshCw } from "lucide-react";
import { useEffect, useState } from "react";
import ErrorAlert from "./ErrorAlert.jsx";

const GENERATION_MESSAGES = [
  "Reading the group portrait…",
  "Dressing the moment in Vietnamese heritage…",
  "Building the light and setting…",
  "Finishing your keepsake…",
];

function PortraitSpinner() {
  return (
    <div className="portrait-spinner" role="img" aria-label="Portrait generation in progress">
      <span className="portrait-spinner-ring" />
      <span className="portrait-spinner-core">CP</span>
    </div>
  );
}

function GeneratingView({ isGenerating, error, onRetry, onChangePhoto }) {
  const [completedMessages, setCompletedMessages] = useState([]);

  useEffect(() => {
    if (!isGenerating) {
      setCompletedMessages([]);
      return undefined;
    }
    const timer = window.setInterval(() => {
      setCompletedMessages((current) => {
        if (current.length >= GENERATION_MESSAGES.length) {
          return current;
        }
        return [...current, GENERATION_MESSAGES[current.length]];
      });
    }, 2800);
    return () => window.clearInterval(timer);
  }, [isGenerating]);

  const activeMessage = completedMessages.length < GENERATION_MESSAGES.length
    ? GENERATION_MESSAGES[completedMessages.length]
    : null;
  const visibleMessages = activeMessage ? [...completedMessages, activeMessage] : completedMessages;

  return (
    <section className="content-card generation-card" aria-labelledby="generation-heading" aria-busy={isGenerating}>
      <div className="card-heading">
        <h2 id="generation-heading" tabIndex={-1}>{error ? "The studio paused" : "Creating your portrait"}</h2>
      </div>

      {isGenerating ? (
        <div className="generation-status" role="status" aria-live="polite" aria-label="Creating your portrait">
          <PortraitSpinner />
          <div className="generation-status-list">
            {visibleMessages.map((message, index) => (
              <span className={index === completedMessages.length ? "generation-stage generation-stage-active" : "generation-stage"} key={message}>
                {message}
              </span>
            ))}
          </div>
        </div>
      ) : (
        <>
          <ErrorAlert error={error} />
          <div className="generation-actions">
            {error?.retryable !== false && (
              <button className="primary-button" type="button" onClick={onRetry}>
                <RefreshCw size={19} aria-hidden="true" /> Try again
              </button>
            )}
            <button className="secondary-button" type="button" onClick={onChangePhoto}>Change photo</button>
          </div>
        </>
      )}
    </section>
  );
}

export default GeneratingView;
