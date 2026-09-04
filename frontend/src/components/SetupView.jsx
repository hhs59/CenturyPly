import { Camera, Check, ImagePlus } from "lucide-react";
import { SCENARIOS } from "../config/scenarios.js";
import ErrorAlert from "./ErrorAlert.jsx";
import PhotoPicker from "./PhotoPicker.jsx";

const PEOPLE_COUNTS = [1, 2, 3, 4];

function SetupView({
  peopleCount,
  scenarioId,
  error,
  uploadStatus,
  onPeopleCountChange,
  onScenarioChange,
  onStartCamera,
  onUploadSelected,
}) {
  const canContinue = Boolean(peopleCount && scenarioId);
  const isCheckingUpload = uploadStatus === "checking";

  return (
    <section className="content-card setup-card" aria-labelledby="setup-heading">
      <div className="card-heading">
        <p className="eyebrow">A portrait of your story</p>
        <h2 id="setup-heading" tabIndex={-1}>Set the scene</h2>
        <p>Choose your group size and a Vietnamese setting. We’ll guide everyone into frame.</p>
      </div>

      <fieldset className="setup-fieldset">
        <legend className="field-label">How many guests?</legend>
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

      <fieldset className="setup-fieldset scenario-fieldset">
        <legend className="field-label">Choose a Vietnamese scenario</legend>
        <div className="scenario-grid" role="radiogroup" aria-label="Vietnamese scenarios">
          {SCENARIOS.map((scenario) => {
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
                  <span className="scenario-sun" />
                  <span className="scenario-arch" />
                  <span className="scenario-lantern" />
                </span>
                <span className="scenario-copy">
                  <strong>{scenario.name}</strong>
                  <span>{scenario.shortDescription}</span>
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
        <button className="primary-button" disabled={!canContinue || isCheckingUpload} onClick={onStartCamera} type="button">
          <Camera size={19} aria-hidden="true" />
          Start camera
        </button>
        <PhotoPicker
          buttonClassName="secondary-button"
          disabled={!canContinue || isCheckingUpload}
          label={isCheckingUpload ? "Checking faces…" : "Upload a photo instead"}
          onFileSelected={onUploadSelected}
        />
      </div>

      <p className="privacy-note">
        <ImagePlus size={15} aria-hidden="true" />
        Live camera frames stay in this browser until you confirm a final photo.
      </p>
      {uploadStatus === "checking" && <p className="inline-status" role="status">Checking the uploaded photo for {peopleCount} {peopleCount === 1 ? "guest" : "guests"}…</p>}
    </section>
  );
}

export default SetupView;
