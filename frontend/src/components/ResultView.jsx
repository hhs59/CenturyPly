import { useState } from "react";
import { Download, RotateCcw } from "lucide-react";
import PhotoQr from "./PhotoQr.jsx";

function ResultView({ scenarioName, displayUrl, resultBlob, publishTicket, onStartOver }) {
  const [showQr, setShowQr] = useState(false);

  return (
    <section className="content-card result-card" aria-labelledby="result-heading">
      <div className="card-heading">
        <h2 id="result-heading" tabIndex={-1}>Your portrait is ready</h2>
        {scenarioName && <p className="result-story-name">{scenarioName}</p>}
      </div>

      <div className="result-delivery">
        {displayUrl && !showQr && (
          <div className="result-image-frame">
            <img alt={`${scenarioName || "Vietnamese heritage"} portrait`} src={displayUrl} />
          </div>
        )}

        {resultBlob && showQr && (
          <PhotoQr blob={resultBlob} ticket={publishTicket} />
        )}
      </div>

      {resultBlob && (
        <div className={`result-actions ${showQr ? "result-actions-single" : ""}`}>
          <button className="secondary-button" type="button" onClick={onStartOver}>
            <RotateCcw size={17} aria-hidden="true" /> Start over
          </button>
          {!showQr && (
            <button className="primary-button" type="button" onClick={() => setShowQr(true)}>
              <Download size={19} aria-hidden="true" /> Download
            </button>
          )}
        </div>
      )}
    </section>
  );
}

export default ResultView;
