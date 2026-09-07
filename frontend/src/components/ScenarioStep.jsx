import { useState } from "react";
import { ArrowRight, Check } from "lucide-react";
import { REGION_FILTERS, SCENARIOS, SCENARIO_IDS } from "../config/scenarios.js";
import ErrorAlert from "./ErrorAlert.jsx";

function handlePreviewError(event) {
  event.currentTarget.hidden = true;
  event.currentTarget.parentElement?.classList.add("scenario-art-missing");
}

function ScenarioStep({ scenarioId, error, onScenarioChange, onContinue }) {
  const [regionFilter, setRegionFilter] = useState("all");
  const canContinue = SCENARIO_IDS.has(scenarioId);
  const visibleScenarios = regionFilter === "all"
    ? SCENARIOS
    : SCENARIOS.filter((scenario) => scenario.region === regionFilter);

  return (
    <section className="content-card setup-card scenario-step" aria-labelledby="scenario-heading">
      <div className="card-heading">
        <h2 id="scenario-heading" tabIndex={-1}>Choose your setting</h2>
      </div>

      <div className="scenario-filter-row">
        <div className="scenario-filters" role="radiogroup" aria-label="Filter settings by region">
          {REGION_FILTERS.map((filter) => {
            const selected = regionFilter === filter.id;
            return (
              <button
                aria-checked={selected}
                className={`scenario-filter-button${selected ? " scenario-filter-button-selected" : ""}`}
                key={filter.id}
                onClick={() => setRegionFilter(filter.id)}
                role="radio"
                type="button"
              >
                {filter.label}
              </button>
            );
          })}
        </div>
      </div>

      <fieldset className="setup-fieldset scenario-fieldset">
        <legend className="visually-hidden">Choose a Vietnamese heritage setting</legend>
        <div className="scenario-grid" role="radiogroup" aria-label="Vietnamese heritage settings">
          {visibleScenarios.map((scenario) => {
            const selected = scenario.id === scenarioId;
            return (
              <button
                aria-checked={selected}
                aria-label={`${scenario.name}, ${scenario.regionLabel}. ${scenario.shortDescription}`}
                className={`scenario-option${selected ? " scenario-option-selected" : ""}`}
                key={scenario.id}
                onClick={() => onScenarioChange(scenario.id)}
                role="radio"
                style={{ "--scenario-accent": scenario.accent }}
                type="button"
              >
                <span className="scenario-art" aria-hidden="true">
                  <img src={scenario.previewImage} alt="" onError={handlePreviewError} />
                  <span className="scenario-art-fallback">Preview coming soon</span>
                </span>
                <span className="scenario-copy">
                  <strong>{scenario.name}</strong>
                </span>
                {selected && (
                  <span className="scenario-check" aria-hidden="true"><Check size={15} /></span>
                )}
              </button>
            );
          })}
        </div>
      </fieldset>

      <ErrorAlert error={error} />

      <div className="setup-actions">
        <button className="primary-button" disabled={!canContinue} onClick={onContinue} type="button">
          Continue
          <ArrowRight size={19} aria-hidden="true" />
        </button>
      </div>
    </section>
  );
}

export default ScenarioStep;
