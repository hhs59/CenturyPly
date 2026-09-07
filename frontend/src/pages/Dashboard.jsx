import { useCallback, useEffect, useMemo, useState } from "react";
import {
  Activity,
  AlertTriangle,
  ArrowLeft,
  BarChart3,
  Camera,
  CheckCircle2,
  ChevronLeft,
  ChevronRight,
  Clock3,
  Download,
  Eye,
  FileDown,
  FileText,
  Filter,
  Image as ImageIcon,
  RefreshCw,
  Search,
  Server,
  Share2,
  Terminal,
  Users,
  X,
} from "lucide-react";
import { SCENARIOS, getScenario } from "../config/scenarios.js";
import "./dashboard.css";

const SCENARIO_COLORS = ["#dca96b", "#83c9bd", "#ef9e72", "#a8a1e6", "#e2c17c", "#9ec4dd"];
const STATUS_LABELS = {
  running: "In progress",
  success: "Completed",
  failed: "Failed",
};

async function fetchJson(url, options) {
  const response = await fetch(url, options);
  let payload = null;
  try {
    payload = await response.json();
  } catch {
    payload = null;
  }
  if (!response.ok || payload?.ok === false) {
    throw new Error(payload?.detail || payload?.error || `Request failed (${response.status})`);
  }
  return payload;
}

function formatDate(value) {
  if (!value) return "—";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "—";
  return date.toLocaleString(undefined, {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function formatBytes(value) {
  const bytes = Number(value) || 0;
  if (!bytes) return "—";
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function scenarioName(scenarioId) {
  return getScenario(scenarioId)?.name || scenarioId || "Unknown story";
}

function statusLabel(status) {
  return STATUS_LABELS[status] || "Unknown";
}

function statusClass(status) {
  return `dashboard-status dashboard-status-${status || "unknown"}`;
}

function StatCard({ label, value, description, tone, icon: Icon }) {
  return (
    <article className={`dashboard-stat-card dashboard-stat-${tone}`}>
      <div className="dashboard-stat-topline">
        <span>{label}</span>
        <span className="dashboard-stat-icon"><Icon size={18} aria-hidden="true" /></span>
      </div>
      <strong>{value}</strong>
      <p>{description}</p>
    </article>
  );
}

function EmptyState({ message }) {
  return (
    <div className="dashboard-empty-state">
      <Activity size={26} aria-hidden="true" />
      <p>{message}</p>
    </div>
  );
}

function TrendChart({ labels = [], values = [] }) {
  const safeValues = values.map((value) => Number(value) || 0);
  const hasData = safeValues.some((value) => value > 0);
  const width = 760;
  const height = 250;
  const padding = { top: 20, right: 16, bottom: 34, left: 32 };
  const innerWidth = width - padding.left - padding.right;
  const innerHeight = height - padding.top - padding.bottom;
  const maxValue = Math.max(1, ...safeValues);
  const points = safeValues.map((value, index) => {
    const x = padding.left + (safeValues.length > 1 ? (index / (safeValues.length - 1)) * innerWidth : innerWidth / 2);
    const y = padding.top + innerHeight - (value / maxValue) * innerHeight;
    return { x, y, value };
  });
  const polyline = points.map((point) => `${point.x},${point.y}`).join(" ");
  const area = points.length > 0
    ? `${padding.left},${padding.top + innerHeight} ${polyline} ${padding.left + innerWidth},${padding.top + innerHeight}`
    : "";
  const visibleLabels = labels.map((label, index) => ({ label, index })).filter(({ index }) => (
    labels.length <= 7 || index === 0 || index === labels.length - 1 || index % 2 === 0
  ));

  return (
    <div className="dashboard-trend-chart">
      {!hasData && <div className="dashboard-chart-empty">Generation activity will appear here.</div>}
      <svg viewBox={`0 0 ${width} ${height}`} role="img" aria-label="Generation activity for the last 14 days">
        <defs>
          <linearGradient id="dashboardTrendFill" x1="0" x2="0" y1="0" y2="1">
            <stop offset="0%" stopColor="#dca96b" stopOpacity="0.28" />
            <stop offset="100%" stopColor="#dca96b" stopOpacity="0" />
          </linearGradient>
        </defs>
        {[0, 0.5, 1].map((ratio) => {
          const y = padding.top + innerHeight * ratio;
          return <line key={ratio} x1={padding.left} x2={padding.left + innerWidth} y1={y} y2={y} className="dashboard-chart-gridline" />;
        })}
        {area && <polygon points={area} fill="url(#dashboardTrendFill)" />}
        {polyline && <polyline points={polyline} className="dashboard-trend-line" />}
        {points.map((point, index) => (
          <circle key={`${point.x}-${index}`} cx={point.x} cy={point.y} r="4" className="dashboard-trend-point">
            <title>{`${labels[index] || "Day"}: ${point.value}`}</title>
          </circle>
        ))}
      </svg>
      <div className="dashboard-chart-labels" aria-hidden="true">
        {visibleLabels.map(({ label, index }) => <span key={`${label}-${index}`}>{label}</span>)}
      </div>
    </div>
  );
}

function ScenarioDonut({ entries }) {
  const total = entries.reduce((sum, entry) => sum + entry.value, 0);
  let cursor = 0;
  const gradientStops = entries.map((entry) => {
    const start = total ? (cursor / total) * 100 : 0;
    cursor += entry.value;
    const end = total ? (cursor / total) * 100 : 100;
    return `${entry.color} ${start}% ${end}%`;
  });

  return (
    <div className="dashboard-donut-wrap">
      {total > 0 ? (
        <div
          className="dashboard-donut"
          style={{ background: `conic-gradient(${gradientStops.join(", ")})` }}
          role="img"
          aria-label="Scenario selection mix"
        >
          <div className="dashboard-donut-hole"><strong>{total}</strong><span>attempts</span></div>
        </div>
      ) : (
        <div className="dashboard-donut dashboard-donut-empty"><div className="dashboard-donut-hole"><strong>0</strong><span>attempts</span></div></div>
      )}
      <div className="dashboard-legend">
        {entries.length === 0 ? (
          <span className="dashboard-muted">No scenario data yet.</span>
        ) : entries.map((entry) => (
          <div className="dashboard-legend-row" key={entry.id}>
            <span className="dashboard-legend-dot" style={{ backgroundColor: entry.color }} />
            <span title={entry.name}>{entry.name}</span>
            <strong>{entry.value}</strong>
          </div>
        ))}
      </div>
    </div>
  );
}

function HourlyChart({ values = [] }) {
  const safeValues = Array.from({ length: 24 }, (_, index) => Number(values[index]) || 0);
  const maxValue = Math.max(1, ...safeValues);
  return (
    <div className="dashboard-hourly-chart" role="img" aria-label="Generation activity by hour">
      <div className="dashboard-hourly-bars">
        {safeValues.map((value, index) => (
          <div className="dashboard-hourly-column" key={index}>
            <span className="dashboard-hourly-value">{value || ""}</span>
            <span
              className="dashboard-hourly-bar"
              style={{ height: `${Math.max(value ? 6 : 2, (value / maxValue) * 100)}%` }}
              title={`${index}:00 — ${value} attempt${value === 1 ? "" : "s"}`}
            />
            <span className="dashboard-hourly-label">{index % 3 === 0 ? `${String(index).padStart(2, "0")}h` : ""}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function SessionThumbnail({ url, alt, onClick, accent = false }) {
  if (!url) {
    return <span className="dashboard-thumb dashboard-thumb-empty"><ImageIcon size={15} aria-hidden="true" /></span>;
  }
  return (
    <button
      type="button"
      className={`dashboard-thumb ${accent ? "dashboard-thumb-accent" : ""}`}
      onClick={onClick}
      title={`Open ${alt.toLowerCase()}`}
    >
      <img src={url} alt={alt} />
      <span className="dashboard-thumb-overlay"><Eye size={14} aria-hidden="true" /></span>
    </button>
  );
}

function LogsModal({ session, onClose }) {
  const logs = Array.isArray(session?.logs) ? session.logs : [];
  return (
    <div className="dashboard-modal-backdrop" role="presentation" onMouseDown={(event) => event.target === event.currentTarget && onClose()}>
      <section className="dashboard-modal dashboard-log-modal" role="dialog" aria-modal="true" aria-labelledby="dashboard-log-title">
        <header className="dashboard-modal-header">
          <div>
            <span className="dashboard-modal-eyebrow"><Terminal size={14} aria-hidden="true" /> Processing log</span>
            <h2 id="dashboard-log-title">{session?.id}</h2>
          </div>
          <button type="button" className="dashboard-icon-button" onClick={onClose} aria-label="Close log"><X size={18} /></button>
        </header>
        <div className="dashboard-log-list">
          {logs.length === 0 ? <EmptyState message="No processing log was recorded for this session." /> : logs.map((log, index) => (
            <div className="dashboard-log-entry" key={`${log.timestamp}-${index}`}>
              <time dateTime={log.timestamp}>{new Date(log.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" })}</time>
              <span className={`dashboard-log-level dashboard-log-${log.level || "info"}`}>{String(log.level || "info").toUpperCase()}</span>
              <div>
                <strong>{log.event || "activity"}</strong>
                <p>{log.message}</p>
                {log.details && <pre>{JSON.stringify(log.details, null, 2)}</pre>}
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

function PhotoModal({ photo, onClose }) {
  if (!photo) return null;
  return (
    <div className="dashboard-modal-backdrop" role="presentation" onMouseDown={(event) => event.target === event.currentTarget && onClose()}>
      <section className="dashboard-modal dashboard-photo-modal" role="dialog" aria-modal="true" aria-labelledby="dashboard-photo-title">
        <header className="dashboard-modal-header">
          <div>
            <span className="dashboard-modal-eyebrow"><ImageIcon size={14} aria-hidden="true" /> Session image</span>
            <h2 id="dashboard-photo-title">{photo.title}</h2>
          </div>
          <button type="button" className="dashboard-icon-button" onClick={onClose} aria-label="Close image"><X size={18} /></button>
        </header>
        <div className="dashboard-photo-body"><img src={photo.url} alt={photo.title} /></div>
        <footer className="dashboard-modal-footer">
          <a href={photo.url} target="_blank" rel="noreferrer" className="dashboard-secondary-button"><Eye size={15} /> Open full image</a>
        </footer>
      </section>
    </div>
  );
}

function JobDetailModal({ detail, loading, onClose }) {
  const [activeTab, setActiveTab] = useState("log");
  const logs = detail?.logs || [];
  const tabs = [
    { id: "log", label: "Processing log", count: logs.length },
    { id: "request", label: "Request", count: null },
    { id: "result", label: "Result", count: null },
  ];
  return (
    <div className="dashboard-modal-backdrop" role="presentation" onMouseDown={(event) => event.target === event.currentTarget && onClose()}>
      <section className="dashboard-modal dashboard-job-modal" role="dialog" aria-modal="true" aria-labelledby="dashboard-job-title">
        <header className="dashboard-modal-header">
          <div>
            <span className="dashboard-modal-eyebrow"><Server size={14} aria-hidden="true" /> Job detail</span>
            <h2 id="dashboard-job-title">{detail?.jobId || "Loading job"}</h2>
          </div>
          <button type="button" className="dashboard-icon-button" onClick={onClose} aria-label="Close job detail"><X size={18} /></button>
        </header>
        {loading || !detail ? (
          <div className="dashboard-modal-loading"><RefreshCw size={24} className="dashboard-spin" /><span>Loading operational details…</span></div>
        ) : (
          <div className="dashboard-job-content">
            <div className="dashboard-job-summary">
              <span className={statusClass(String(detail.status || "").toLowerCase())}>{statusLabel(String(detail.status || "").toLowerCase())}</span>
              <span>{scenarioName(detail.conceptId)}</span>
              <span>{detail.peopleCount || 0} guest(s)</span>
              <span>{formatBytes(detail.result?.output_byte_count)} output</span>
              <span>Updated {formatDate(detail.updatedAt)}</span>
            </div>
            <nav className="dashboard-detail-tabs" aria-label="Job detail sections">
              {tabs.map((tab) => (
                <button type="button" key={tab.id} className={activeTab === tab.id ? "dashboard-detail-tab-active" : ""} onClick={() => setActiveTab(tab.id)}>
                  {tab.label}{tab.count !== null ? ` (${tab.count})` : ""}
                </button>
              ))}
            </nav>
            <div className="dashboard-detail-body">
              {activeTab === "log" && (
                <pre className="dashboard-console">{detail.logContent || "No operational log was recorded."}</pre>
              )}
              {activeTab === "request" && (
                <pre className="dashboard-json-block">{JSON.stringify(detail.request || {}, null, 2)}</pre>
              )}
              {activeTab === "result" && (
                <div className="dashboard-result-detail">
                  <pre className="dashboard-json-block">{JSON.stringify(detail.result || {}, null, 2)}</pre>
                  {detail.finalImageUrl && <img src={detail.finalImageUrl} alt="Generated portrait" />}
                </div>
              )}
            </div>
          </div>
        )}
      </section>
    </div>
  );
}

function SessionTable({ sessions, loading, onPhoto, onLogs }) {
  return (
    <div className="dashboard-table-wrap">
      <table className="dashboard-table">
        <thead>
          <tr>
            <th>Session</th>
            <th>Story</th>
            <th>Status</th>
            <th>Images</th>
            <th>Render</th>
            <th>Downloads</th>
            <th>Shares</th>
            <th>Created</th>
            <th aria-label="Actions" />
          </tr>
        </thead>
        <tbody>
          {loading ? Array.from({ length: 5 }, (_, index) => (
            <tr key={`skeleton-${index}`} className="dashboard-skeleton-row">
              {Array.from({ length: 9 }, (_, cell) => <td key={cell}><span /></td>)}
            </tr>
          )) : sessions.length === 0 ? (
            <tr><td colSpan="9"><EmptyState message="No generation sessions match these filters." /></td></tr>
          ) : sessions.map((session) => (
            <tr key={session.id}>
              <td>
                <div className="dashboard-session-id"><strong>{session.name || "Guest group"}</strong><code>{session.id}</code><span>{session.people_count || 0} guest(s)</span></div>
              </td>
              <td><span className="dashboard-story-pill">{scenarioName(session.scenario_id)}</span></td>
              <td><span className={statusClass(session.status)}>{statusLabel(session.status)}</span>{session.error_message && <small className="dashboard-error-text">{session.error_message}</small>}</td>
              <td>
                <div className="dashboard-thumb-pair">
                  <SessionThumbnail url={session.input_image_url} alt="Original photo" onClick={() => onPhoto({ url: session.input_image_url, title: `Original photo · ${session.id}` })} />
                  <SessionThumbnail url={session.output_image_url} alt="Generated portrait" accent onClick={() => onPhoto({ url: session.output_image_url, title: `Generated portrait · ${session.id}` })} />
                </div>
              </td>
              <td className="dashboard-metric dashboard-metric-warm">{session.render_duration ? `${session.render_duration}s` : "—"}</td>
              <td className="dashboard-metric dashboard-metric-cyan">{session.download_count || 0}</td>
              <td className="dashboard-metric dashboard-metric-purple">{session.share_count || 0}</td>
              <td className="dashboard-date">{formatDate(session.created_at)}</td>
              <td className="dashboard-table-action"><button type="button" className="dashboard-log-button" onClick={() => onLogs(session)}><Terminal size={14} /> Log</button></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function JobsTable({ jobs, loading, onPhoto, onDetail }) {
  return (
    <div className="dashboard-table-wrap">
      <table className="dashboard-table dashboard-jobs-table">
        <thead>
          <tr><th>Job ID</th><th>Status</th><th>Guests</th><th>Story</th><th>Output</th><th>Updated</th><th aria-label="Actions" /></tr>
        </thead>
        <tbody>
          {loading ? Array.from({ length: 5 }, (_, index) => <tr key={`job-skeleton-${index}`} className="dashboard-skeleton-row">{Array.from({ length: 7 }, (_, cell) => <td key={cell}><span /></td>)}</tr>) : jobs.length === 0 ? (
            <tr><td colSpan="7"><EmptyState message="No operational jobs have been recorded yet." /></td></tr>
          ) : jobs.map((job) => (
            <tr key={job.id}>
              <td><code className="dashboard-job-id">{job.id}</code></td>
              <td><span className={statusClass(job.status)}>{statusLabel(job.status)}</span></td>
              <td>{job.people_count || 0}</td>
              <td><span className="dashboard-story-pill">{scenarioName(job.scenario_id)}</span></td>
              <td>{job.output_image_url ? <SessionThumbnail url={job.output_image_url} alt="Generated portrait" accent onClick={() => onPhoto({ url: job.output_image_url, title: `Generated portrait · ${job.id}` })} /> : <span className="dashboard-muted">No output</span>}</td>
              <td className="dashboard-date">{formatDate(job.completed_at || job.created_at)}</td>
              <td className="dashboard-table-action"><button type="button" className="dashboard-log-button" onClick={() => onDetail(job.id)}><Terminal size={14} /> Details</button></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState("sessions");
  const [overview, setOverview] = useState(null);
  const [sessions, setSessions] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [loadingOverview, setLoadingOverview] = useState(true);
  const [loadingSessions, setLoadingSessions] = useState(true);
  const [loadingJobs, setLoadingJobs] = useState(false);
  const [loadingJobDetail, setLoadingJobDetail] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [lastUpdated, setLastUpdated] = useState(null);
  const [health, setHealth] = useState(null);
  const [searchDraft, setSearchDraft] = useState("");
  const [search, setSearch] = useState("");
  const [scenarioFilter, setScenarioFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [page, setPage] = useState(1);
  const [meta, setMeta] = useState({ current_page: 1, total_pages: 1, total_items: 0 });
  const [isExporting, setIsExporting] = useState(false);
  const [photoModal, setPhotoModal] = useState(null);
  const [logModal, setLogModal] = useState(null);
  const [activeJobId, setActiveJobId] = useState("");
  const [activeJobDetail, setActiveJobDetail] = useState(null);

  const loadOverview = useCallback(async () => {
    setLoadingOverview(true);
    try {
      const data = await fetchJson("/api/dashboard/overview");
      setOverview(data);
      setLastUpdated(new Date());
    } catch (loadError) {
      setError(loadError.message || "Could not load dashboard overview.");
    } finally {
      setLoadingOverview(false);
    }
  }, []);

  const loadSessions = useCallback(async () => {
    setLoadingSessions(true);
    try {
      const params = new URLSearchParams({
        page: String(page),
        limit: "10",
        search,
        scenario_id: scenarioFilter,
        status: statusFilter,
      });
      const data = await fetchJson(`/api/dashboard/sessions?${params.toString()}`);
      setSessions(Array.isArray(data.data) ? data.data : []);
      setMeta(data.meta || { current_page: page, total_pages: 1, total_items: 0 });
      setLastUpdated(new Date());
    } catch (loadError) {
      setError(loadError.message || "Could not load session history.");
    } finally {
      setLoadingSessions(false);
    }
  }, [page, scenarioFilter, search, statusFilter]);

  const loadJobs = useCallback(async () => {
    setLoadingJobs(true);
    try {
      const data = await fetchJson("/api/dashboard/jobs");
      setJobs(Array.isArray(data.data) ? data.data : []);
      setLastUpdated(new Date());
    } catch (loadError) {
      setError(loadError.message || "Could not load operational jobs.");
    } finally {
      setLoadingJobs(false);
    }
  }, []);

  const loadHealth = useCallback(async () => {
    try {
      setHealth(await fetchJson("/api/health"));
    } catch {
      setHealth(null);
    }
  }, []);

  useEffect(() => {
    void loadOverview();
    void loadHealth();
  }, [loadHealth, loadOverview]);

  useEffect(() => {
    if (activeTab === "sessions") void loadSessions();
    if (activeTab === "jobs") void loadJobs();
  }, [activeTab, loadJobs, loadSessions]);

  useEffect(() => {
    const timer = window.setInterval(() => {
      void loadOverview();
      if (activeTab === "sessions") void loadSessions();
      if (activeTab === "jobs") void loadJobs();
    }, 30_000);
    return () => window.clearInterval(timer);
  }, [activeTab, loadJobs, loadOverview, loadSessions]);

  useEffect(() => {
    const handleEscape = (event) => {
      if (event.key !== "Escape") return;
      setPhotoModal(null);
      setLogModal(null);
      setActiveJobId("");
      setActiveJobDetail(null);
    };
    window.addEventListener("keydown", handleEscape);
    return () => window.removeEventListener("keydown", handleEscape);
  }, []);

  const scenarioEntries = useMemo(() => SCENARIOS.map((scenario, index) => ({
    id: scenario.id,
    name: scenario.name,
    value: Number(overview?.scenario_counts?.[scenario.id] || overview?.style_counts?.[scenario.id] || 0),
    color: SCENARIO_COLORS[index % SCENARIO_COLORS.length],
  })).filter((entry) => entry.value > 0), [overview]);

  const handleSearchSubmit = (event) => {
    event.preventDefault();
    setPage(1);
    setSearch(searchDraft.trim());
  };

  const handleFilterChange = (setter) => (event) => {
    setter(event.target.value);
    setPage(1);
  };

  const handleRefresh = () => {
    setError("");
    setNotice("");
    void loadOverview();
    void loadHealth();
    void loadSessions();
    void loadJobs();
  };

  const handleOpenJob = async (jobId) => {
    setActiveJobId(jobId);
    setActiveJobDetail(null);
    setLoadingJobDetail(true);
    try {
      const data = await fetchJson(`/api/dashboard/jobs/${encodeURIComponent(jobId)}`);
      setActiveJobDetail(data.data);
    } catch (loadError) {
      setError(loadError.message || "Could not load job details.");
    } finally {
      setLoadingJobDetail(false);
    }
  };

  const handleExport = async () => {
    if (isExporting) return;
    setIsExporting(true);
    setNotice("");
    try {
      const params = new URLSearchParams({ page: "1", limit: "50000", search, scenario_id: scenarioFilter, status: statusFilter });
      const data = await fetchJson(`/api/dashboard/sessions?${params.toString()}`);
      const rows = data.data || [];
      if (rows.length === 0) {
        setNotice("There is no session data to export yet.");
        return;
      }
      const headers = ["Session ID", "Story", "Guest count", "Status", "Render seconds", "Downloads", "Shares", "Created", "Original image", "Generated image"];
      const csvCell = (value) => `"${String(value ?? "").replaceAll("\"", "\"\"")}"`;
      const csv = `\uFEFF${[headers, ...rows.map((row) => [
        row.id,
        scenarioName(row.scenario_id),
        row.people_count,
        statusLabel(row.status),
        row.render_duration,
        row.download_count,
        row.share_count,
        row.created_at ? new Date(row.created_at).toLocaleString() : "",
        row.input_image_url,
        row.output_image_url,
      ])].map((row) => row.map(csvCell).join(",")).join("\n")}`;
      const url = URL.createObjectURL(new Blob([csv], { type: "text/csv;charset=utf-8" }));
      const link = document.createElement("a");
      link.href = url;
      link.download = `century-ply-dashboard-${Date.now()}.csv`;
      link.click();
      window.setTimeout(() => URL.revokeObjectURL(url), 1_000);
      setNotice(`Exported ${rows.length} session${rows.length === 1 ? "" : "s"}.`);
    } catch (exportError) {
      setError(exportError.message || "Could not export session data.");
    } finally {
      setIsExporting(false);
    }
  };

  const overviewValue = (key, fallback = 0) => loadingOverview ? "…" : (overview?.[key] ?? fallback);
  const modelLabel = health?.model ? health.model.split("/").pop() : "service unavailable";

  return (
    <div className="dashboard-page">
      <div className="dashboard-background-glow" aria-hidden="true" />
      <main className="dashboard-container">
        <header className="dashboard-header">
          <div className="dashboard-title-block">
            <div className="dashboard-title-row"><span className="dashboard-title-accent" /><div><p className="dashboard-eyebrow">Century Ply · admin workspace</p><h1>AI Photobooth Dashboard</h1></div></div>
            <p className="dashboard-subtitle">Monitor portrait generation, customer activity, and the health of the image service.</p>
          </div>
          <div className="dashboard-header-actions">
            <span className={`dashboard-service-state ${health ? "dashboard-service-online" : ""}`}><span />{health ? `Service online · ${modelLabel}` : "Service unavailable"}</span>
            <button type="button" className="dashboard-secondary-button" onClick={handleRefresh}><RefreshCw size={15} className={loadingOverview || loadingSessions || loadingJobs ? "dashboard-spin" : ""} /> Refresh</button>
            <a href="/" className="dashboard-primary-button"><Camera size={15} /> Open photobooth</a>
          </div>
        </header>

        {(error || notice) && <div className={`dashboard-notice ${error ? "dashboard-notice-error" : ""}`} role={error ? "alert" : "status"}><AlertTriangle size={16} /><span>{error || notice}</span>{error && <button type="button" onClick={() => setError("")} aria-label="Dismiss message"><X size={15} /></button>}</div>}

        <section className="dashboard-stat-grid" aria-label="Overview metrics">
          <StatCard label="Total attempts" value={overviewValue("total_jobs")} description="Validated generation sessions" tone="gold" icon={Users} />
          <StatCard label="Portraits complete" value={overviewValue("success_jobs")} description="Successful AI outputs" tone="green" icon={CheckCircle2} />
          <StatCard label="Success rate" value={`${overviewValue("success_rate")}%`} description={`${overview?.failed_jobs || 0} failed sessions`} tone="blue" icon={BarChart3} />
          <StatCard label="Average render" value={`${overviewValue("avg_render_time")}s`} description="End-to-end service time" tone="amber" icon={Clock3} />
          <StatCard label="Downloads" value={overviewValue("total_downloads")} description="Customer downloads" tone="cyan" icon={Download} />
          <StatCard label="Shares" value={overviewValue("total_shares")} description="Customer share actions" tone="purple" icon={Share2} />
        </section>

        <section className="dashboard-tab-row" aria-label="Dashboard sections">
          <button type="button" className={activeTab === "sessions" ? "dashboard-tab-active" : ""} onClick={() => setActiveTab("sessions")}><FileText size={15} /> Session reports</button>
          <button type="button" className={activeTab === "jobs" ? "dashboard-tab-active" : ""} onClick={() => setActiveTab("jobs")}><Server size={15} /> Operational jobs</button>
          <span className="dashboard-updated">{lastUpdated ? `Updated ${lastUpdated.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}` : "Loading data…"}</span>
        </section>

        {activeTab === "sessions" ? (
          <>
            <section className="dashboard-chart-grid">
              <article className="dashboard-panel dashboard-trend-panel"><div className="dashboard-panel-heading"><div><p className="dashboard-panel-kicker">Activity</p><h2>Generation trend</h2></div><span className="dashboard-panel-meta">Last 14 days</span></div><TrendChart labels={overview?.trend_labels || []} values={overview?.trend_values || []} /></article>
              <article className="dashboard-panel"><div className="dashboard-panel-heading"><div><p className="dashboard-panel-kicker">Preferences</p><h2>Story mix</h2></div><span className="dashboard-panel-meta">By scenario</span></div><ScenarioDonut entries={scenarioEntries} /></article>
            </section>
            <section className="dashboard-panel dashboard-hourly-panel"><div className="dashboard-panel-heading"><div><p className="dashboard-panel-kicker">Operations</p><h2>Activity by hour</h2></div><span className="dashboard-panel-meta">Local booth time</span></div><HourlyChart values={overview?.hourly_activity || []} /></section>
            <section className="dashboard-panel dashboard-table-panel">
              <div className="dashboard-table-toolbar">
                <form className="dashboard-search" onSubmit={handleSearchSubmit}><Search size={16} aria-hidden="true" /><input value={searchDraft} onChange={(event) => setSearchDraft(event.target.value)} placeholder="Search session ID or story…" aria-label="Search sessions" /><button type="submit" aria-label="Search"><ArrowLeft size={14} /></button></form>
                <div className="dashboard-filter-group"><label><Filter size={14} /><span className="visually-hidden">Story</span><select value={scenarioFilter} onChange={handleFilterChange(setScenarioFilter)}><option value="">All stories</option>{SCENARIOS.map((scenario) => <option value={scenario.id} key={scenario.id}>{scenario.name}</option>)}</select></label><label><span className="visually-hidden">Status</span><select value={statusFilter} onChange={handleFilterChange(setStatusFilter)}><option value="">All statuses</option><option value="success">Completed</option><option value="failed">Failed</option><option value="running">In progress</option></select></label><button type="button" className="dashboard-export-button" onClick={handleExport} disabled={isExporting}><FileDown size={15} />{isExporting ? "Exporting…" : "Export CSV"}</button></div>
              </div>
              <div className="dashboard-table-heading"><div><p className="dashboard-panel-kicker">History</p><h2>Customer sessions</h2></div><span>{meta.total_items || 0} total</span></div>
              <SessionTable sessions={sessions} loading={loadingSessions} onPhoto={setPhotoModal} onLogs={setLogModal} />
              {!loadingSessions && meta.total_pages > 1 && <div className="dashboard-pagination"><span>Page {meta.current_page} of {meta.total_pages}</span><div><button type="button" disabled={page <= 1} onClick={() => setPage((current) => Math.max(1, current - 1))} aria-label="Previous page"><ChevronLeft size={16} /></button><button type="button" disabled={page >= meta.total_pages} onClick={() => setPage((current) => Math.min(meta.total_pages, current + 1))} aria-label="Next page"><ChevronRight size={16} /></button></div></div>}
            </section>
          </>
        ) : (
          <section className="dashboard-panel dashboard-table-panel"><div className="dashboard-jobs-toolbar"><div><p className="dashboard-panel-kicker">Server monitor</p><h2>Operational jobs</h2><p>Inspect the sanitized request and provider timeline for each generation attempt.</p></div><button type="button" className="dashboard-secondary-button" onClick={() => void loadJobs()}><RefreshCw size={15} className={loadingJobs ? "dashboard-spin" : ""} /> Refresh jobs</button></div><JobsTable jobs={jobs} loading={loadingJobs} onPhoto={setPhotoModal} onDetail={handleOpenJob} /></section>
        )}
      </main>

      {photoModal && <PhotoModal photo={photoModal} onClose={() => setPhotoModal(null)} />}
      {logModal && <LogsModal session={logModal} onClose={() => setLogModal(null)} />}
      {activeJobId && <JobDetailModal key={activeJobId} detail={activeJobDetail} loading={loadingJobDetail} onClose={() => { setActiveJobId(""); setActiveJobDetail(null); }} />}
    </div>
  );
}
