import { Activity, ChevronDown } from "lucide-react";
import { formatLogTime } from "../utils/logging.js";

function LogViewer({ logs = [] }) {
  return (
    <details className="logs-panel">
      <summary>
        <span className="summary-label">
          <Activity size={16} aria-hidden="true" />
          System activity
        </span>
        <span className="log-count">{logs.length}</span>
      </summary>
      <div className="log-list" aria-label="Sanitized system activity">
        {logs.length === 0 && <p className="log-empty">No activity has been recorded yet.</p>}
        {logs.map((entry) => {
          const hasDetails = entry.details && typeof entry.details === "object" && Object.keys(entry.details).length > 0;
          const row = (
            <span className="log-row-content">
              <time className="log-time" dateTime={entry.timestamp}>{formatLogTime(entry.timestamp)}</time>
              <span className={`log-level log-level-${entry.level}`}>{entry.level.toUpperCase()}</span>
              <span className="log-message">{entry.message}</span>
              {hasDetails && <ChevronDown className="log-chevron" size={15} aria-hidden="true" />}
            </span>
          );
          return hasDetails ? (
            <details className="log-row" key={entry.id}>
              <summary>{row}</summary>
              <pre className="log-details">{JSON.stringify(entry.details, null, 2)}</pre>
            </details>
          ) : (
            <div className="log-row log-row-static" key={entry.id}>{row}</div>
          );
        })}
      </div>
    </details>
  );
}

export default LogViewer;
