import { useCallback, useEffect, useMemo, useState } from "react";
import {
  ArrowLeft,
  Check,
  Clipboard,
  FileText,
  Image as ImageIcon,
  RefreshCw,
  RotateCcw,
  Save,
  Trash2,
  Upload,
} from "lucide-react";
import { SCENARIOS, getScenario } from "../config/scenarios.js";
import "./prompts.css";

const REGION_FILTERS = [
  { id: "all", label: "All" },
  { id: "Northern Vietnam", label: "Northern" },
  { id: "Central Vietnam", label: "Central" },
  { id: "Southern Vietnam", label: "Southern" },
];

const REFERENCE_FIELDS = [
  {
    role: "male_clothing",
    label: "Male clothing · ẢNH 2",
    hint: "Clothing shape, material, color, and details.",
  },
  {
    role: "female_clothing",
    label: "Female clothing · ẢNH 3",
    hint: "Clothing shape, material, color, and details.",
  },
  {
    role: "location",
    label: "Location · ẢNH 4",
    hint: "Architectural identity and real landmark details.",
  },
  {
    role: "style",
    label: "Art direction · ẢNH 5",
    hint: "9:16 composition, guest area, lighting, depth, and colour only.",
  },
];

function cloneConfig(config) {
  return JSON.parse(JSON.stringify(config));
}

function configFromResponse(payload) {
  return {
    base_prompt: payload?.base_prompt || "",
    scenarios: payload?.scenarios || {},
  };
}

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

function PromptField({ label, hint, value, onChange, rows = 10 }) {
  return (
    <label className="prompt-field">
      <span className="prompt-field-label">{label}</span>
      {hint && <span className="prompt-field-hint">{hint}</span>}
      <textarea value={value || ""} onChange={onChange} rows={rows} spellCheck="false" />
    </label>
  );
}

function Prompts() {
  const [draft, setDraft] = useState(null);
  const [saved, setSaved] = useState(null);
  const [defaults, setDefaults] = useState(null);
  const [selectedScenarioId, setSelectedScenarioId] = useState(SCENARIOS[0]?.id || "");
  const [regionFilter, setRegionFilter] = useState("all");
  const [activePanel, setActivePanel] = useState("concept");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [referenceUrls, setReferenceUrls] = useState({});
  const [uploadingReferences, setUploadingReferences] = useState({});
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const loadPrompts = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const [currentPayload, defaultPayload] = await Promise.all([
        fetchJson("/api/prompts"),
        fetchJson("/api/prompts/defaults"),
      ]);
      const current = configFromResponse(currentPayload);
      setDraft(current);
      setSaved(cloneConfig(current));
      setDefaults(configFromResponse(defaultPayload));
      setReferenceUrls(currentPayload.references || {});
    } catch (loadError) {
      setError(loadError.message || "Could not load prompts.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadPrompts();
  }, [loadPrompts]);

  const selectedScenario = getScenario(selectedScenarioId) || SCENARIOS[0];
  const filteredScenarios = useMemo(() => (
    SCENARIOS.filter((scenario) => regionFilter === "all" || scenario.regionLabel === regionFilter)
  ), [regionFilter]);
  const isDirty = Boolean(draft && saved && JSON.stringify(draft) !== JSON.stringify(saved));

  useEffect(() => {
    if (filteredScenarios.some((scenario) => scenario.id === selectedScenarioId)) return;
    if (filteredScenarios[0]) setSelectedScenarioId(filteredScenarios[0].id);
  }, [filteredScenarios, selectedScenarioId]);

  const updateScenario = (field) => (event) => {
    const value = event.target.value;
    setDraft((current) => ({
      ...current,
      scenarios: {
        ...current.scenarios,
        [selectedScenarioId]: {
          ...current.scenarios[selectedScenarioId],
          [field]: value,
        },
      },
    }));
    setMessage("");
  };

  const updateBasePrompt = (event) => {
    setDraft((current) => ({ ...current, base_prompt: event.target.value }));
    setMessage("");
  };

  const savePrompts = async () => {
    if (!draft || saving) return;
    setSaving(true);
    setError("");
    setMessage("");
    try {
      const payload = await fetchJson("/api/prompts", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(draft),
      });
      const current = configFromResponse(payload);
      setDraft(current);
      setSaved(cloneConfig(current));
      setReferenceUrls(payload.references || referenceUrls);
      setMessage("Saved");
    } catch (saveError) {
      setError(saveError.message || "Could not save prompts.");
    } finally {
      setSaving(false);
    }
  };

  const resetCurrentScenario = () => {
    if (!defaults || !selectedScenarioId) return;
    setDraft((current) => ({
      ...current,
      scenarios: {
        ...current.scenarios,
        [selectedScenarioId]: cloneConfig(defaults.scenarios[selectedScenarioId]),
      },
    }));
    setMessage("Concept text reset. Save to apply it.");
    setError("");
  };

  const resetSystemPrompt = () => {
    if (!defaults) return;
    setDraft((current) => ({ ...current, base_prompt: defaults.base_prompt }));
    setMessage("System prompt reset. Save to apply it.");
    setError("");
  };

  const resetAllPrompts = () => {
    if (!defaults) return;
    setDraft(cloneConfig(defaults));
    setMessage("All text prompts reset. Save to apply them.");
    setError("");
  };

  const handleReferenceUpload = async (event, role) => {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file || !selectedScenarioId) return;

    const referenceKey = `${selectedScenarioId}:${role}`;
    setUploadingReferences((current) => ({ ...current, [referenceKey]: true }));
    setError("");
    setMessage("");
    try {
      const formData = new FormData();
      formData.append("image", file, file.name);
      const payload = await fetchJson(`/api/prompts/references/${selectedScenarioId}/${role}`, {
        method: "POST",
        body: formData,
      });
      const cacheBustedUrl = `${payload.reference_url}?v=${Date.now()}`;
      setReferenceUrls((current) => ({
        ...current,
        [selectedScenarioId]: {
          ...current[selectedScenarioId],
          [role]: cacheBustedUrl,
        },
      }));
      setMessage("Reference image updated");
    } catch (uploadError) {
      setError(uploadError.message || "Could not upload reference image.");
    } finally {
      setUploadingReferences((current) => ({ ...current, [referenceKey]: false }));
    }
  };

  const resetReference = async (role) => {
    if (!selectedScenarioId) return;
    const referenceKey = `${selectedScenarioId}:${role}`;
    setUploadingReferences((current) => ({ ...current, [referenceKey]: true }));
    setError("");
    setMessage("");
    try {
      const payload = await fetchJson(`/api/prompts/references/${selectedScenarioId}/${role}`, { method: "DELETE" });
      const cacheBustedUrl = `${payload.reference_url}?v=${Date.now()}`;
      setReferenceUrls((current) => ({
        ...current,
        [selectedScenarioId]: {
          ...current[selectedScenarioId],
          [role]: cacheBustedUrl,
        },
      }));
      setMessage("Reference restored to default");
    } catch (resetError) {
      setError(resetError.message || "Could not restore reference image.");
    } finally {
      setUploadingReferences((current) => ({ ...current, [referenceKey]: false }));
    }
  };

  const copyPrompt = async () => {
    if (!draft) return;
    const scenarioConfig = draft.scenarios[selectedScenarioId] || {};
    const text = activePanel === "system"
      ? draft.base_prompt
      : `${scenarioConfig.concept_prompt || ""}\n\nTRANG PHỤC NAM:\n${scenarioConfig.male_clothing || ""}\n\nTRANG PHỤC NỮ:\n${scenarioConfig.female_clothing || ""}\n\n${scenarioConfig.pose_expression || ""}`;
    try {
      await navigator.clipboard.writeText(text);
      setMessage("Copied to clipboard");
    } catch {
      setError("Clipboard access is unavailable in this browser.");
    }
  };

  const scenarioConfig = draft?.scenarios?.[selectedScenarioId] || {};

  return (
    <div className="prompts-page">
      <div className="prompts-background-glow" aria-hidden="true" />
      <main className="prompts-container">
        <header className="prompts-header">
          <div className="prompts-title-block">
            <a className="prompts-back-link" href="/admin/dashboard"><ArrowLeft size={15} /> Dashboard</a>
            <div className="prompts-title-row">
              <span className="prompts-title-accent" />
              <div>
                <p className="prompts-eyebrow">Century Ply · admin workspace</p>
                <h1>Prompt Studio</h1>
              </div>
            </div>
            <p className="prompts-subtitle">Manage the instructions used for each imperial story.</p>
          </div>
          <div className="prompts-header-actions">
            <a href="/" className="prompts-secondary-button">Open photobooth</a>
            <button type="button" className="prompts-primary-button" onClick={savePrompts} disabled={!draft || saving || !isDirty}>
              <Save size={15} /> {saving ? "Saving…" : "Save changes"}
            </button>
          </div>
        </header>

        {(error || message) && (
          <div className={`prompts-notice ${error ? "prompts-notice-error" : ""}`} role={error ? "alert" : "status"}>
            {error ? <RefreshCw size={15} /> : <Check size={15} />}
            <span>{error || message}</span>
          </div>
        )}

        <nav className="prompts-tabs" aria-label="Prompt sections">
          <button type="button" className={activePanel === "concept" ? "active" : ""} onClick={() => setActivePanel("concept")}>
            <FileText size={16} /> Concept prompts
          </button>
          <button type="button" className={activePanel === "system" ? "active" : ""} onClick={() => setActivePanel("system")}>
            <FileText size={16} /> System prompt
          </button>
        </nav>

        {loading && <div className="prompts-loading"><RefreshCw size={18} className="prompts-spin" /> Loading prompts…</div>}

        {!loading && draft && activePanel === "concept" && (
          <section className="prompts-workspace" aria-label="Concept prompt editor">
            <aside className="prompts-sidebar">
              <div className="prompts-section-heading">
                <p className="prompts-kicker">1. Choose concept</p>
                <h2>Imperial stories</h2>
              </div>
              <div className="prompts-filter-tabs" role="tablist" aria-label="Filter concepts by region">
                {REGION_FILTERS.map((filter) => (
                  <button type="button" key={filter.id} className={regionFilter === filter.id ? "active" : ""} onClick={() => setRegionFilter(filter.id)}>
                    {filter.label}
                  </button>
                ))}
              </div>
              <div className="prompts-scenario-list">
                {filteredScenarios.map((scenario) => (
                  <button
                    type="button"
                    className={`prompts-scenario-option ${selectedScenarioId === scenario.id ? "active" : ""}`}
                    key={scenario.id}
                    onClick={() => setSelectedScenarioId(scenario.id)}
                  >
                    <img src={scenario.previewImage} alt="" aria-hidden="true" />
                    <span><strong>{scenario.name}</strong><small>{scenario.regionLabel}</small></span>
                    {selectedScenarioId === scenario.id && <Check size={16} aria-hidden="true" />}
                  </button>
                ))}
              </div>
            </aside>

            <div className="prompts-editor">
              <div className="prompts-editor-heading">
                <div>
                  <p className="prompts-kicker">2. Edit concept prompt</p>
                  <h2>{selectedScenario?.name || "Concept"}</h2>
                  <span>{selectedScenario?.regionLabel}</span>
                </div>
                <button type="button" className="prompts-icon-button" onClick={resetCurrentScenario} title="Reset this concept" aria-label="Reset this concept">
                  <RotateCcw size={16} />
                </button>
              </div>
              <PromptField
                label="Shared concept and location direction"
                hint="Story, required architecture, spatial composition, lighting, palette, and exclusions."
                value={scenarioConfig.concept_prompt}
                onChange={updateScenario("concept_prompt")}
                rows={8}
              />
              <PromptField
                label="Male clothing direction"
                hint="Silhouette, layers, collar, sleeves, fabric, colour, motifs, headwear, lower garment, footwear; clothing only."
                value={scenarioConfig.male_clothing}
                onChange={updateScenario("male_clothing")}
                rows={6}
              />
              <PromptField
                label="Female clothing direction"
                hint="Silhouette, layers, collar, sleeves, fabric, colour, motifs, headwear, lower garment, footwear; clothing only."
                value={scenarioConfig.female_clothing}
                onChange={updateScenario("female_clothing")}
                rows={6}
              />
              <PromptField
                label="Pose and expression signature"
                hint="Three variants; each variant must specify 1, 2, 3, and 4-person staging."
                value={scenarioConfig.pose_expression}
                onChange={updateScenario("pose_expression")}
                rows={8}
              />
              <section className="prompts-reference-section" aria-label="Concept reference images">
                <div className="prompts-reference-heading">
                  <div>
                    <p className="prompts-kicker">Reference images</p>
                    <h3>Clothing, location, and art direction</h3>
                  </div>
                  <span>Used in the next generation</span>
                </div>
                <div className="prompts-reference-grid">
                  {REFERENCE_FIELDS.map((reference) => {
                    const referenceKey = `${selectedScenarioId}:${reference.role}`;
                    const isUploading = Boolean(uploadingReferences[referenceKey]);
                    const referenceUrl = referenceUrls[selectedScenarioId]?.[reference.role];
                    return (
                      <article className="prompts-reference-card" key={reference.role}>
                        <div className="prompts-reference-image">
                          {referenceUrl ? (
                            <img src={referenceUrl} alt={`${selectedScenario?.name || "Concept"} ${reference.label}`} />
                          ) : (
                            <div className="prompts-reference-empty"><ImageIcon size={24} /><span>No image</span></div>
                          )}
                          {isUploading && <div className="prompts-reference-loading"><RefreshCw size={18} className="prompts-spin" /></div>}
                        </div>
                        <div className="prompts-reference-copy">
                          <strong>{reference.label}</strong>
                          <span>{reference.hint}</span>
                        </div>
                        <div className="prompts-reference-actions">
                          <label className="prompts-reference-button">
                            <Upload size={13} /> Replace
                            <input type="file" accept="image/jpeg,image/png,image/webp" onChange={(event) => handleReferenceUpload(event, reference.role)} disabled={isUploading} />
                          </label>
                          <button type="button" className="prompts-reference-reset" onClick={() => resetReference(reference.role)} disabled={isUploading} title="Restore default reference">
                            <Trash2 size={13} /> Default
                          </button>
                        </div>
                      </article>
                    );
                  })}
                </div>
              </section>
              <div className="prompts-editor-actions">
                <button type="button" className="prompts-secondary-button" onClick={copyPrompt}><Clipboard size={15} /> Copy concept prompt</button>
              </div>
            </div>
          </section>
        )}

        {!loading && draft && activePanel === "system" && (
          <section className="prompts-system-panel" aria-label="System prompt editor">
            <div className="prompts-editor-heading">
              <div>
                <p className="prompts-kicker">1. Edit system prompt</p>
                <h2>Shared generation instructions</h2>
                <span>Applied to every concept and guest count.</span>
              </div>
              <button type="button" className="prompts-icon-button" onClick={resetSystemPrompt} title="Reset system prompt" aria-label="Reset system prompt">
                <RotateCcw size={16} />
              </button>
            </div>
            <div className="prompts-placeholder-row" aria-label="Required prompt variables">
              <span>Required variables</span>
              <code>{"{people_count}"}</code>
              <code>{"{variation_hint}"}</code>
              <code>{"{pose_expression}"}</code>
            </div>
            <PromptField
              label="Base prompt"
              hint="Keep the three variables above in the prompt. They are filled automatically for each generation."
              value={draft.base_prompt}
              onChange={updateBasePrompt}
              rows={28}
            />
            <div className="prompts-editor-actions">
              <button type="button" className="prompts-secondary-button" onClick={copyPrompt}><Clipboard size={15} /> Copy system prompt</button>
              <button type="button" className="prompts-secondary-button" onClick={resetAllPrompts}><RotateCcw size={15} /> Reset all defaults</button>
            </div>
          </section>
        )}
      </main>
    </div>
  );
}

export default Prompts;
