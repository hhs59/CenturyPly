import { ArrowRight, Check } from "lucide-react";
import { SCENARIOS, SCENARIO_IDS } from "../config/scenarios.js";
import ErrorAlert from "./ErrorAlert.jsx";

function ScenarioStep({ scenarioId, error, onScenarioChange, onContinue }) {
  const canContinue = SCENARIO_IDS.has(scenarioId);

  return (
    <section className="content-card setup-card scenario-step" aria-labelledby="scenario-heading">
      <div className="card-heading">
        <h2 id="scenario-heading" tabIndex={-1}>Choose your story</h2>
      </div>

      <fieldset className="setup-fieldset scenario-fieldset">
        <legend className="visually-hidden">Choose a scenario</legend>
        <div className="scenario-grid" role="radiogroup" aria-label="Vietnamese scenarios">
          {SCENARIOS.map((scenario, index) => {
            const selected = scenario.id === scenarioId;
            return (
              <button
                aria-checked={selected}
                className={`scenario-option${selected ? " scenario-option-selected" : ""}`}
                key={scenario.id}
                onClick={() => onScenarioChange(scenario.id)}
                role="radio"
                style={{ "--scenario-accent": scenario.accent }}
                type="button"
              >
                <span className="scenario-art" aria-hidden="true">
                  <img src={scenario.previewImage} alt="" />
                </span>
                <span className="scenario-copy">
                  <small>Concept 0{index + 1}</small>
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
