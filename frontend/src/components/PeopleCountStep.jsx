import { ArrowLeft, ArrowRight } from "lucide-react";
import { getScenario } from "../config/scenarios.js";
import ErrorAlert from "./ErrorAlert.jsx";

const PEOPLE_COUNTS = [1, 2, 3, 4];

function PeopleCountStep({
  peopleCount,
  scenarioId,
  error,
  onPeopleCountChange,
  onBack,
  onContinue,
}) {
  const canContinue = Boolean(peopleCount && scenarioId);
  const scenario = getScenario(scenarioId);

  return (
    <section className="content-card setup-card people-step" aria-labelledby="people-heading">
      <div className="card-heading">
        <h2 id="people-heading" tabIndex={-1}>How many guests are joining?</h2>
      </div>

      {scenario && (
        <div className="selected-scenario" style={{ "--scenario-accent": scenario.accent }}>
          <span className="selected-scenario-art" aria-hidden="true">
            <img src={scenario.previewImage} alt="" />
          </span>
          <span>
            <small>Your selected scene</small>
            <strong>{scenario.name}</strong>
          </span>
        </div>
      )}

      <fieldset className="setup-fieldset people-fieldset">
        <legend className="visually-hidden">Expected guests</legend>
        <div className="people-count-grid" role="radiogroup" aria-label="Expected number of guests">
          {PEOPLE_COUNTS.map((count) => {
            const selected = peopleCount === count;
            return (
              <button
                aria-checked={selected}
                className={`people-count-option${selected ? " people-count-option-selected" : ""}`}
                key={count}
                onClick={() => onPeopleCountChange(count)}
                role="radio"
                type="button"
              >
                <strong>{count}</strong>
                <span>{count === 1 ? "guest" : "guests"}</span>
              </button>
            );
          })}
        </div>
      </fieldset>

      <ErrorAlert error={error} />

      <div className="setup-actions people-step-actions">
        <button className="secondary-button" onClick={onBack} type="button">
          <ArrowLeft size={19} aria-hidden="true" /> Back to scene
        </button>
        <button className="primary-button" disabled={!canContinue} onClick={onContinue} type="button">
          Continue to camera
          <ArrowRight size={19} aria-hidden="true" />
        </button>
      </div>
    </section>
  );
}

export default PeopleCountStep;
