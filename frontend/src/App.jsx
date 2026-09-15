import { useCallback, useEffect, useRef, useState } from "react";
import CameraCapture from "./components/CameraCapture.jsx";
import GeneratingView from "./components/GeneratingView.jsx";
import PeopleCountStep from "./components/PeopleCountStep.jsx";
import ResultView from "./components/ResultView.jsx";
import ScenarioStep from "./components/ScenarioStep.jsx";
import { SCENARIO_IDS, getScenario } from "./config/scenarios.js";
import { useFaceDetection } from "./hooks/useFaceDetection.js";
import Dashboard from "./pages/Dashboard.jsx";
import PhotoDownload from "./pages/PhotoDownload.jsx";
import Prompts from "./pages/Prompts.jsx";
import { dataUrlToBlob, GenerationApiError, generateImage } from "./services/generationApi.js";
import { validateImageFile } from "./utils/imageValidation.js";
import { createAppError } from "./utils/logging.js";
import { createPhotoJacket } from "./utils/photoJacket.js";

const CAMERA_STEPS = new Set(["camera_loading", "aligning", "countdown", "capture_check", "camera_error", "photo_ready"]);
const INACTIVITY_PAUSED_STEPS = new Set(["generating", "countdown", "capture_check"]);
const INACTIVITY_RESET_MS = 60_000;
const PRESENCE_ACTIVITY_INTERVAL_MS = 5_000;

function createInitialState() {
  return {
    step: "scenario",
    peopleCount: null,
    scenarioId: "",
    photoFile: null,
    resultBlob: null,
    resultUrl: "",
    photoPublishTicket: "",
    isGenerating: false,
    error: null,
  };
}

function normalizeScenarioId(value) {
  return String(value ?? "").trim().toLowerCase();
}

function setupError(message = "Choose a Vietnamese scenario and guest count first.") {
  return createAppError({ code: "SETUP_REQUIRED", message, retryable: false, field: "setup" });
}

function PhotoboothApp() {
  const [state, setState] = useState(createInitialState);
  const resultUrlRef = useRef("");
  const generationInFlightRef = useRef(false);
  const inactivityPausedRef = useRef(false);
  const inactivityTimerRef = useRef(0);
  const lastPresenceActivityRef = useRef(0);
  const appHeadingRef = useRef(null);
  const previousStepRef = useRef(state.step);
  const [isQrPreparing, setIsQrPreparing] = useState(false);
  const faceDetection = useFaceDetection();

  const revokeResultUrl = useCallback(() => {
    if (resultUrlRef.current) {
      URL.revokeObjectURL(resultUrlRef.current);
      resultUrlRef.current = "";
    }
  }, []);

  const resetExperience = useCallback(() => {
    revokeResultUrl();
    setIsQrPreparing(false);
    setState(createInitialState());
  }, [revokeResultUrl]);

  const restartInactivityTimer = useCallback(() => {
    window.clearTimeout(inactivityTimerRef.current);
    inactivityTimerRef.current = 0;
    if (!inactivityPausedRef.current) {
      inactivityTimerRef.current = window.setTimeout(resetExperience, INACTIVITY_RESET_MS);
    }
  }, [resetExperience]);

  const handleCameraPresence = useCallback(() => {
    const now = Date.now();
    if (now - lastPresenceActivityRef.current < PRESENCE_ACTIVITY_INTERVAL_MS) return;
    lastPresenceActivityRef.current = now;
    restartInactivityTimer();
  }, [restartInactivityTimer]);

  useEffect(() => {
    if (previousStepRef.current !== state.step) {
      if (!CAMERA_STEPS.has(state.step)) {
        appHeadingRef.current?.focus({ preventScroll: true });
      }
      previousStepRef.current = state.step;
    }
  }, [state.step]);

  useEffect(() => () => revokeResultUrl(), [revokeResultUrl]);

  useEffect(() => {
    window.addEventListener("pointerdown", restartInactivityTimer, { passive: true });
    window.addEventListener("keydown", restartInactivityTimer);
    return () => {
      window.clearTimeout(inactivityTimerRef.current);
      window.removeEventListener("pointerdown", restartInactivityTimer);
      window.removeEventListener("keydown", restartInactivityTimer);
    };
  }, [restartInactivityTimer]);

  useEffect(() => {
    inactivityPausedRef.current = INACTIVITY_PAUSED_STEPS.has(state.step) || isQrPreparing;
    restartInactivityTimer();
  }, [isQrPreparing, restartInactivityTimer, state.step]);

  useEffect(() => {
    if (state.step === "people" && state.peopleCount) {
      void faceDetection.ensureReady().catch(() => {});
    }
  }, [faceDetection.ensureReady, state.peopleCount, state.step]);

  const startGeneration = useCallback(async ({
    file = state.photoFile,
    peopleCount = state.peopleCount,
    scenarioId = state.scenarioId,
  } = {}) => {
    if (generationInFlightRef.current) {
      return;
    }

    const imageValidation = validateImageFile(file);
    const normalizedScenarioId = normalizeScenarioId(scenarioId);
    const validScenario = SCENARIO_IDS.has(normalizedScenarioId);
    if (!peopleCount || ![1, 2, 3, 4].includes(peopleCount) || !validScenario) {
      setState((current) => ({ ...current, step: validScenario ? "people" : "scenario", error: setupError() }));
      return;
    }
    if (!imageValidation.valid) {
      setState((current) => ({
        ...current,
        step: "people",
        error: createAppError({ code: imageValidation.code, message: imageValidation.message, retryable: false, field: "photo" }),
      }));
      return;
    }

    generationInFlightRef.current = true;
    revokeResultUrl();
    setState((current) => ({
      ...current,
      step: "generating",
      peopleCount,
      scenarioId: normalizedScenarioId,
      photoFile: file,
      resultBlob: null,
      resultUrl: "",
      photoPublishTicket: "",
      isGenerating: true,
      error: null,
    }));

    try {
      const response = await generateImage({
        peopleCount,
        scenarioId: normalizedScenarioId,
        file,
      });
      const generatedBlob = await dataUrlToBlob(response.resultImage);
      const blob = await createPhotoJacket(generatedBlob, getScenario(normalizedScenarioId)?.name);
      const resultUrl = URL.createObjectURL(blob);
      resultUrlRef.current = resultUrl;
      setState((current) => ({
        ...current,
        step: "result",
        resultBlob: blob,
        resultUrl,
        photoPublishTicket: response.publishTicket,
        isGenerating: false,
        error: null,
      }));
    } catch (error) {
      const apiError = error instanceof GenerationApiError
        ? error
        : new GenerationApiError({ code: "GENERATION_FAILED", message: "The image service had a temporary problem." });
      setState((current) => ({
        ...current,
        step: "generating",
        isGenerating: false,
        error: createAppError({
          code: apiError.code,
          message: apiError.message,
          retryable: apiError.retryable,
          technicalDetails: { status: apiError.status, kind: apiError.kind },
        }),
      }));
    } finally {
      generationInFlightRef.current = false;
    }
  }, [revokeResultUrl, state.peopleCount, state.photoFile, state.scenarioId]);

  const handleCameraPhaseChange = useCallback((phase) => {
    setState((current) => ({
      ...current,
      step: phase === "error" ? "camera_error" : phase,
    }));
  }, []);

  const handleCameraCancel = useCallback(() => {
    setState((current) => ({ ...current, step: "people", photoFile: null, error: null }));
  }, []);

  const handleCameraRetake = useCallback(() => {
    setState((current) => ({ ...current, step: "camera_loading", photoFile: null, error: null }));
  }, []);

  const handlePhotoBackToScenario = useCallback(() => {
    setState((current) => ({ ...current, step: "scenario", photoFile: null, error: null }));
  }, []);

  const handleCaptured = useCallback((file) => {
    setState((current) => ({
      ...current,
      step: "photo_ready",
      photoFile: file,
      error: null,
    }));
  }, []);

  const handlePhotoProceed = useCallback(() => {
    void startGeneration();
  }, [startGeneration]);

  function handlePeopleCountChange(peopleCount) {
    setState((current) => ({ ...current, peopleCount, error: null }));
  }

  function handleScenarioChange(scenarioId) {
    setState((current) => ({ ...current, scenarioId: normalizeScenarioId(scenarioId), error: null }));
  }

  function handleScenarioContinue() {
    const normalizedScenarioId = normalizeScenarioId(state.scenarioId);
    if (!SCENARIO_IDS.has(normalizedScenarioId)) {
      setState((current) => ({ ...current, step: "scenario", error: setupError("Choose a Vietnamese scenario to continue.") }));
      return;
    }
    setState((current) => ({ ...current, step: "people", scenarioId: normalizedScenarioId, error: null }));
  }

  function handlePeopleBack() {
    setState((current) => ({ ...current, step: "scenario", error: null }));
  }

  function handleStartCamera() {
    const normalizedScenarioId = normalizeScenarioId(state.scenarioId);
    if (!SCENARIO_IDS.has(normalizedScenarioId)) {
      setState((current) => ({ ...current, step: "scenario", error: setupError("Choose a Vietnamese scenario to continue.") }));
      return;
    }
    if (!state.peopleCount || ![1, 2, 3, 4].includes(state.peopleCount)) {
      setState((current) => ({ ...current, step: "people", error: setupError("Choose the number of guests to continue.") }));
      return;
    }
    setState((current) => ({
      ...current,
      step: "camera_loading",
      scenarioId: normalizedScenarioId,
      photoFile: null,
      error: null,
    }));
  }

  function handleStartOver() {
    resetExperience();
  }

  function handleChangePhoto() {
    revokeResultUrl();
    setState((current) => ({
      ...current,
      step: "people",
      photoFile: null,
      resultBlob: null,
      resultUrl: "",
      isGenerating: false,
      error: null,
    }));
  }

  function renderStep() {
    if (CAMERA_STEPS.has(state.step)) {
      return (
        <CameraCapture
          error={state.error}
          faceDetection={faceDetection}
          isPhotoReady={state.step === "photo_ready"}
          onBackToScenario={handlePhotoBackToScenario}
          onCancel={handleCameraCancel}
          onCaptured={handleCaptured}
          onGuestPresence={handleCameraPresence}
          onPhaseChange={handleCameraPhaseChange}
          onProceed={handlePhotoProceed}
          onRetake={handleCameraRetake}
          peopleCount={state.peopleCount}
        />
      );
    }
    if (state.step === "generating") {
      return (
        <GeneratingView
          error={state.error}
          isGenerating={state.isGenerating}
          onChangePhoto={handleChangePhoto}
          onRetry={handleStartOver}
        />
      );
    }
    if (state.step === "result") {
      return (
        <ResultView
          displayUrl={state.resultUrl}
          onQrPreparingChange={setIsQrPreparing}
          onStartOver={handleStartOver}
          resultBlob={state.resultBlob}
          publishTicket={state.photoPublishTicket}
          scenarioName={getScenario(state.scenarioId)?.name}
        />
      );
    }
    if (state.step === "people") {
      return (
        <PeopleCountStep
          error={state.error}
          onBack={handlePeopleBack}
          onContinue={handleStartCamera}
          onPeopleCountChange={handlePeopleCountChange}
          peopleCount={state.peopleCount}
          scenarioId={state.scenarioId}
        />
      );
    }
    return (
      <ScenarioStep
        error={state.error}
        onContinue={handleScenarioContinue}
        onScenarioChange={handleScenarioChange}
        scenarioId={state.scenarioId}
      />
    );
  }

  const activeScenario = getScenario(state.scenarioId);

  return (
    <main
      className="app-shell"
      data-step={state.step}
      style={{
        "--story-accent": activeScenario?.accent || "#b8813f",
      }}
    >
      <section className="main-panel" aria-label="Century Ply AI Photobooth">
        <header className="hero-heading">
          <div className="brand-lockup">
            <div className="brand-copy">
              <p className="brand-wordmark">Century Ply</p>
              <h1 id="app-title" ref={appHeadingRef} tabIndex={-1}>The Vietnam Imperial Legacy</h1>
            </div>
          </div>
        </header>

        {renderStep()}
      </section>
    </main>
  );
}

function App() {
  const pathname = window.location.pathname.replace(/\/+$/, "") || "/";
  const photoRoute = /^\/photo\/([^/]+)$/.exec(pathname);
  if (photoRoute) return <PhotoDownload token={photoRoute[1]} />;
  if (pathname === "/dashboard" || pathname === "/admin/dashboard") {
    return <Dashboard />;
  }
  if (pathname === "/prompts" || pathname === "/admin/prompts") {
    return <Prompts />;
  }
  return <PhotoboothApp />;
}

export default App;
