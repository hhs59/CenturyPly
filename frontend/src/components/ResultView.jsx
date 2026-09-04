import { Download, RotateCcw, Share2 } from "lucide-react";

function ResultView({ scenarioName, displayUrl, resultBlob, onDownload, onShare, onStartOver }) {
  return (
    <section className="content-card result-card" aria-labelledby="result-heading">
      <div className="card-heading">
        <h2 id="result-heading" tabIndex={-1}>{scenarioName || "Vietnamese heritage portrait"}</h2>
      </div>

      {displayUrl && (
        <div className="result-image-frame">
          <img alt={`${scenarioName || "Vietnamese heritage"} portrait`} src={displayUrl} />
        </div>
      )}

      {resultBlob && (
        <div className="result-actions">
          <button className="secondary-button" type="button" onClick={onShare}>
            <Share2 size={19} aria-hidden="true" /> Share
          </button>
          <button className="primary-button" type="button" onClick={onDownload}>
            <Download size={19} aria-hidden="true" /> Download
          </button>
        </div>
      )}

      <div className="result-secondary-actions">
        <button className="text-button" type="button" onClick={onStartOver}>
          <RotateCcw size={17} aria-hidden="true" /> Start over
        </button>
      </div>
    </section>
  );
}

export default ResultView;
