import { Download, RotateCcw } from "lucide-react";

function ResultView({ scenarioName, displayUrl, resultBlob, onDownload, onStartOver }) {
  return (
    <section className="content-card result-card" aria-labelledby="result-heading">
      <div className="card-heading">
        <h2 id="result-heading" tabIndex={-1}>Your portrait is ready</h2>
        {scenarioName && <p className="result-story-name">{scenarioName}</p>}
      </div>

      {displayUrl && (
        <div className="result-image-frame">
          <img alt={`${scenarioName || "Vietnamese heritage"} portrait`} src={displayUrl} />
        </div>
      )}

      {resultBlob && (
        <div className="result-actions">
          <button className="secondary-button" type="button" onClick={onStartOver}>
            <RotateCcw size={17} aria-hidden="true" /> Start over
          </button>
          <button className="primary-button" type="button" onClick={onDownload}>
            <Download size={19} aria-hidden="true" /> Download
          </button>
        </div>
      )}
    </section>
  );
}

export default ResultView;
