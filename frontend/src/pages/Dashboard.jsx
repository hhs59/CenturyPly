import { useCallback, useEffect, useMemo, useState } from "react";
import {
  Activity,
  AlertTriangle,
  BarChart3,
  Camera,
  CheckCircle2,
  ChevronLeft,
  ChevronRight,
  Clock3,
  Download,
  Eye,
  FileDown,
  Filter,
  Image as ImageIcon,
  RefreshCw,
  Search,
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

function scenarioName(scenarioId) {
  return getScenario(scenarioId)?.name || scenarioId || "Unknown story";
}

function statusLabel(status) {
  return STATUS_LABELS[status] || "Unknown";
}

function statusClass(status) {
  return `dashboard-status dashboard-status-${status || "unknown"}`;
}

function attemptLabel(value) {
  return `${value} attempt${value === 1 ? "" : "s"}`;
}

function DashboardChartTooltip({ label, value, className = "", style }) {
  return (
    <div className={`dashboard-chart-tooltip ${className}`.trim()} style={style} aria-hidden="true">
      <strong>{label}</strong>
      <span>{value}</span>
    </div>
  );
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
  const [hoveredIndex, setHoveredIndex] = useState(null);
  const activePoint = hoveredIndex === null ? null : points[hoveredIndex];

  function handleMouseMove(event) {
    if (!points.length) return;
    const rect = event.currentTarget.getBoundingClientRect();
    const x = Math.max(0, Math.min(width, ((event.clientX - rect.left) / rect.width) * width));
    const nearestIndex = points.reduce((bestIndex, point, index) => (
      Math.abs(point.x - x) < Math.abs(points[bestIndex].x - x) ? index : bestIndex
    ), 0);
    setHoveredIndex(nearestIndex);
  }

  return (
    <div className="dashboard-trend-chart">
      {!hasData && <div className="dashboard-chart-empty">Generation activity will appear here.</div>}
      <svg
        viewBox={`0 0 ${width} ${height}`}
        role="img"
        aria-label="Generation activity for the last 14 days"
        onMouseMove={handleMouseMove}
        onMouseLeave={() => setHoveredIndex(null)}
      >
        <defs>
          <linearGradient id="dashboardTrendFill" x1="0" x2="0" y1="0" y2="1">
            <stop offset="0%" stopColor="#dca96b" stopOpacity="0.28" />
            <stop offset="100%" stopColor="#dca96b" stopOpacity="0" />
          </linearGradient>
        </defs>
        <rect x="0" y="0" width={width} height={height} fill="transparent" pointerEvents="all" />
        {[0, 0.5, 1].map((ratio) => {
          const y = padding.top + innerHeight * ratio;
          return <line key={ratio} x1={padding.left} x2={padding.left + innerWidth} y1={y} y2={y} className="dashboard-chart-gridline" />;
        })}
        {area && <polygon points={area} fill="url(#dashboardTrendFill)" />}
        {polyline && <polyline points={polyline} className="dashboard-trend-line" />}
        {points.map((point, index) => (
          <circle
            key={`${point.x}-${index}`}
            cx={point.x}
            cy={point.y}
            r={hoveredIndex === index ? 6 : 4}
            className={`dashboard-trend-point${hoveredIndex === index ? " dashboard-trend-point-active" : ""}`}
          >
            <title>{`${labels[index] || "Day"}: ${point.value}`}</title>
          </circle>
        ))}
      </svg>
      {activePoint && (
        <DashboardChartTooltip
          className={activePoint.y < 70 ? "dashboard-chart-tooltip-below" : "dashboard-trend-tooltip"}
          label={labels[hoveredIndex] || "Day"}
          value={attemptLabel(activePoint.value)}
          style={{
            left: `${Math.min(88, Math.max(12, (activePoint.x / width) * 100))}%`,
            top: `${(activePoint.y / height) * 100}%`,
          }}
        />
      )}
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
  const [hoveredIndex, setHoveredIndex] = useState(null);
  const activeEntry = hoveredIndex === null ? null : entries[hoveredIndex];

  function handleMouseMove(event) {
    if (!total) return;
    const rect = event.currentTarget.getBoundingClientRect();
    const x = event.clientX - rect.left - (rect.width / 2);
    const y = event.clientY - rect.top - (rect.height / 2);
    if (Math.hypot(x, y) < rect.width * 0.34) {
      setHoveredIndex(null);
      return;
    }

    const degrees = (Math.atan2(y, x) * (180 / Math.PI) + 108 + 360) % 360;
    const target = (degrees / 360) * total;
    let cursorValue = 0;
    const index = entries.findIndex((entry) => {
      cursorValue += entry.value;
      return target < cursorValue;
    });
    setHoveredIndex(index >= 0 ? index : null);
  }

  return (
    <div className="dashboard-donut-wrap">
      {total > 0 ? (
        <div
          className={`dashboard-donut${activeEntry ? " dashboard-donut-active" : ""}`}
          style={{ background: `conic-gradient(${gradientStops.join(", ")})` }}
          role="img"
          aria-label="Scenario selection mix"
          onMouseMove={handleMouseMove}
          onMouseLeave={() => setHoveredIndex(null)}
        >
          <div className="dashboard-donut-hole"><strong>{total}</strong><span>attempts</span></div>
        </div>
      ) : (
        <div className="dashboard-donut dashboard-donut-empty"><div className="dashboard-donut-hole"><strong>0</strong><span>attempts</span></div></div>
      )}
      {activeEntry && (
        <DashboardChartTooltip
          className="dashboard-donut-tooltip"
          label={activeEntry.name}
          value={attemptLabel(activeEntry.value)}
        />
      )}
      <div className="dashboard-legend">
        {entries.length === 0 ? (
          <span className="dashboard-muted">No scenario data yet.</span>
        ) : entries.map((entry, index) => (
          <div
            className={`dashboard-legend-row${hoveredIndex === index ? " dashboard-legend-row-active" : ""}`}
            key={entry.id}
            onMouseEnter={() => setHoveredIndex(index)}
            onMouseLeave={() => setHoveredIndex(null)}
          >
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
  const [hoveredIndex, setHoveredIndex] = useState(null);
  return (
    <div className="dashboard-hourly-chart" role="img" aria-label="Generation activity by hour">
      <div className="dashboard-hourly-bars">
        {safeValues.map((value, index) => (
          <div
            className="dashboard-hourly-column"
            key={index}
            onMouseEnter={() => setHoveredIndex(index)}
            onMouseLeave={() => setHoveredIndex(null)}
          >
            <span className="dashboard-hourly-value">{value || ""}</span>
            <span
              className={`dashboard-hourly-bar${hoveredIndex === index ? " dashboard-hourly-bar-active" : ""}`}
              style={{ height: `${Math.max(value ? 6 : 2, (value / maxValue) * 100)}%` }}
              aria-label={`${index}:00 — ${attemptLabel(value)}`}
              tabIndex={0}
              onFocus={() => setHoveredIndex(index)}
              onBlur={() => setHoveredIndex(null)}
            />
            <span className="dashboard-hourly-label">{index % 3 === 0 ? `${String(index).padStart(2, "0")}h` : ""}</span>
          </div>
        ))}
      </div>
      {hoveredIndex !== null && (
        <DashboardChartTooltip
          className="dashboard-hourly-tooltip"
          label={`${hoveredIndex}:00`}
          value={attemptLabel(safeValues[hoveredIndex])}
          style={{ left: `${((hoveredIndex + 0.5) / safeValues.length) * 100}%` }}
        />
      )}
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
            <th>Created</th>
            <th aria-label="Actions" />
          </tr>
        </thead>
        <tbody>
          {loading ? Array.from({ length: 5 }, (_, index) => (
            <tr key={`skeleton-${index}`} className="dashboard-skeleton-row">
              {Array.from({ length: 8 }, (_, cell) => <td key={cell}><span /></td>)}
            </tr>
          )) : sessions.length === 0 ? (
            <tr className="dashboard-empty-row"><td colSpan="8"><EmptyState message="No generation sessions match these filters." /></td></tr>
          ) : sessions.map((session) => (
            <tr key={session.id} className="dashboard-session-row">
              <td data-label="Session">
                <div className="dashboard-session-id"><strong>{session.name || "Guest group"}</strong><code>{session.id}</code><span>{session.people_count || 0} guest(s)</span></div>
              </td>
              <td data-label="Story"><span className="dashboard-story-pill">{scenarioName(session.scenario_id)}</span></td>
              <td data-label="Status"><span className={statusClass(session.status)}>{statusLabel(session.status)}</span>{session.error_message && <small className="dashboard-error-text">{session.error_message}</small>}</td>
              <td data-label="Images">
                <div className="dashboard-thumb-pair">
                  <SessionThumbnail url={session.input_image_url} alt="Original photo" onClick={() => onPhoto({ url: session.input_image_url, title: `Original photo · ${session.id}` })} />
                  <SessionThumbnail url={session.output_image_url} alt="Generated portrait" accent onClick={() => onPhoto({ url: session.output_image_url, title: `Generated portrait · ${session.id}` })} />
                </div>
              </td>
              <td data-label="Render" className="dashboard-metric dashboard-metric-warm">{session.render_duration ? `${session.render_duration}s` : "—"}</td>
              <td data-label="Downloads" className="dashboard-metric dashboard-metric-cyan">{session.download_count || 0}</td>
              <td data-label="Created" className="dashboard-date">{formatDate(session.created_at)}</td>
              <td data-label="Actions" className="dashboard-table-action"><button type="button" className="dashboard-log-button" onClick={() => onLogs(session)}><Terminal size={14} /> Log</button></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default function Dashboard() {
  const [overview, setOverview] = useState(null);
  const [sessions, setSessions] = useState([]);
  const [loadingOverview, setLoadingOverview] = useState(true);
  const [loadingSessions, setLoadingSessions] = useState(true);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [searchDraft, setSearchDraft] = useState("");
  const [search, setSearch] = useState("");
  const [scenarioFilter, setScenarioFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [page, setPage] = useState(1);
  const [meta, setMeta] = useState({ current_page: 1, total_pages: 1, total_items: 0 });
  const [isExporting, setIsExporting] = useState(false);
  const [photoModal, setPhotoModal] = useState(null);
  const [logModal, setLogModal] = useState(null);

  const loadOverview = useCallback(async () => {
    setLoadingOverview(true);
    try {
      const data = await fetchJson("/api/dashboard/overview");
      setOverview(data);
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
    } catch (loadError) {
      setError(loadError.message || "Could not load session history.");
    } finally {
      setLoadingSessions(false);
    }
  }, [page, scenarioFilter, search, statusFilter]);

  useEffect(() => {
    void loadOverview();
  }, [loadOverview]);

  useEffect(() => {
    void loadSessions();
  }, [loadSessions]);

  useEffect(() => {
    const timer = window.setInterval(() => {
      void loadOverview();
      void loadSessions();
    }, 30_000);
    return () => window.clearInterval(timer);
  }, [loadOverview, loadSessions]);

  useEffect(() => {
    const handleEscape = (event) => {
      if (event.key !== "Escape") return;
      setPhotoModal(null);
      setLogModal(null);
    };
    window.addEventListener("keydown", handleEscape);
    return () => window.removeEventListener("keydown", handleEscape);
  }, []);

  const scenarioEntries = useMemo(() => SCENARIOS.map((scenario, index) => ({
    id: scenario.id,
    name: scenario.name,
    value: Number(overview?.scenario_counts?.[scenario.id] || 0),
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
    void loadSessions();
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
      const headers = ["Session ID", "Story", "Guest count", "Status", "Render seconds", "Downloads", "Created", "Original image", "Generated image"];
      const csvCell = (value) => `"${String(value ?? "").replaceAll("\"", "\"\"")}"`;
      const csv = `\uFEFF${[headers, ...rows.map((row) => [
        row.id,
        scenarioName(row.scenario_id),
        row.people_count,
        statusLabel(row.status),
        row.render_duration,
        row.download_count,
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
  return (
    <div className="dashboard-page">
      <div className="dashboard-background-glow" aria-hidden="true" />
      <main className="dashboard-container">
        <header className="dashboard-header">
          <div className="dashboard-title-block">
            <div className="dashboard-title-row"><span className="dashboard-title-accent" /><div><p className="dashboard-eyebrow">Century Ply · admin workspace</p><h1>AI Photobooth Dashboard</h1></div></div>
            <p className="dashboard-subtitle">Track portrait activity, performance, and guest downloads.</p>
          </div>
          <div className="dashboard-header-actions">
            <button type="button" className="dashboard-secondary-button" onClick={handleRefresh}><RefreshCw size={15} className={loadingOverview || loadingSessions ? "dashboard-spin" : ""} /> Refresh</button>
            <a href="/admin/prompts" className="dashboard-secondary-button">Prompt studio</a>
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
        </section>

        <>
            <section className="dashboard-chart-grid">
              <article className="dashboard-panel dashboard-trend-panel"><div className="dashboard-panel-heading"><div><p className="dashboard-panel-kicker">Activity</p><h2>Generation trend</h2></div><span className="dashboard-panel-meta">Last 14 days</span></div><TrendChart labels={overview?.trend_labels || []} values={overview?.trend_values || []} /></article>
              <article className="dashboard-panel"><div className="dashboard-panel-heading"><div><p className="dashboard-panel-kicker">Preferences</p><h2>Story mix</h2></div><span className="dashboard-panel-meta">By scenario</span></div><ScenarioDonut entries={scenarioEntries} /></article>
            </section>
            <section className="dashboard-panel dashboard-hourly-panel"><div className="dashboard-panel-heading"><div><p className="dashboard-panel-kicker">Operations</p><h2>Activity by hour</h2></div><span className="dashboard-panel-meta">Local booth time</span></div><HourlyChart values={overview?.hourly_activity || []} /></section>
            <section className="dashboard-panel dashboard-table-panel">
              <div className="dashboard-table-toolbar">
                <form className="dashboard-search" onSubmit={handleSearchSubmit}><Search size={16} aria-hidden="true" /><input value={searchDraft} onChange={(event) => setSearchDraft(event.target.value)} placeholder="Search session ID or story…" aria-label="Search sessions" /><button type="submit">Search</button></form>
                <div className="dashboard-filter-group"><label><Filter size={14} /><span className="visually-hidden">Story</span><select value={scenarioFilter} onChange={handleFilterChange(setScenarioFilter)}><option value="">All stories</option>{SCENARIOS.map((scenario) => <option value={scenario.id} key={scenario.id}>{scenario.name}</option>)}</select></label><label><span className="visually-hidden">Status</span><select value={statusFilter} onChange={handleFilterChange(setStatusFilter)}><option value="">All statuses</option><option value="success">Completed</option><option value="failed">Failed</option><option value="running">In progress</option></select></label><button type="button" className="dashboard-export-button" onClick={handleExport} disabled={isExporting}><FileDown size={15} />{isExporting ? "Exporting…" : "Export CSV"}</button></div>
              </div>
              <div className="dashboard-table-heading"><div><p className="dashboard-panel-kicker">History</p><h2>Customer sessions</h2></div><span>{meta.total_items || 0} total</span></div>
              <SessionTable sessions={sessions} loading={loadingSessions} onPhoto={setPhotoModal} onLogs={setLogModal} />
              {!loadingSessions && meta.total_pages > 1 && <div className="dashboard-pagination"><span>Page {meta.current_page} of {meta.total_pages}</span><div><button type="button" disabled={page <= 1} onClick={() => setPage((current) => Math.max(1, current - 1))} aria-label="Previous page"><ChevronLeft size={16} /></button><button type="button" disabled={page >= meta.total_pages} onClick={() => setPage((current) => Math.min(meta.total_pages, current + 1))} aria-label="Next page"><ChevronRight size={16} /></button></div></div>}
            </section>
        </>
      </main>

      {photoModal && <PhotoModal photo={photoModal} onClose={() => setPhotoModal(null)} />}
      {logModal && <LogsModal session={logModal} onClose={() => setLogModal(null)} />}
    </div>
  );
}
