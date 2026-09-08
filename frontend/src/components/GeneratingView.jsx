import { RefreshCw } from "lucide-react";
import ErrorAlert from "./ErrorAlert.jsx";

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
  return (
    <section className="content-card generation-card" aria-labelledby="generation-heading" aria-busy={isGenerating}>
      <div className="card-heading">
        <h2 id="generation-heading" tabIndex={-1}>{error ? "The studio paused" : "Creating your portrait"}</h2>
      </div>

      {isGenerating ? (
        <div className="generation-status" role="status" aria-live="polite" aria-label="Creating your portrait">
          <PortraitSpinner />
          <p className="generation-message">This may take a moment.</p>
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
