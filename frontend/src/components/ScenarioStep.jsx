import { ArrowRight, Check } from "lucide-react";
import { SCENARIOS, SCENARIO_IDS } from "../config/scenarios.js";
import ErrorAlert from "./ErrorAlert.jsx";

function handlePreviewError(event) {
  event.currentTarget.hidden = true;
  event.currentTarget.parentElement?.classList.add("scenario-art-missing");
}

function ScenarioStep({ scenarioId, error, onScenarioChange, onContinue }) {
  const canContinue = SCENARIO_IDS.has(scenarioId);

  return (
    <section className="content-card setup-card scenario-step" aria-labelledby="scenario-heading">
      <div className="card-heading">
        <h2 id="scenario-heading" tabIndex={-1}>Choose your setting</h2>
      </div>

      <fieldset className="setup-fieldset scenario-fieldset">
        <legend className="visually-hidden">Choose a Vietnamese heritage setting</legend>
        <div className="scenario-grid" role="radiogroup" aria-label="Vietnamese heritage settings">
          {SCENARIOS.map((scenario) => {
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
                  <img
                    src={scenario.previewImage}
                    alt=""
                    decoding="async"
                    loading="lazy"
                    onError={handlePreviewError}
                  />
                  <span className="scenario-art-fallback">Preview coming soon</span>
                </span>
                <span className="scenario-copy">
                  <small>{scenario.regionLabel}</small>
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
