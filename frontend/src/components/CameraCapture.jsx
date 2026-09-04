import { Camera, RefreshCw, RotateCcw, ScanFace } from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";
import ErrorAlert from "./ErrorAlert.jsx";
import FaceGuideOverlay from "./FaceGuideOverlay.jsx";
import PhotoPicker from "./PhotoPicker.jsx";
import { useCamera } from "../hooks/useCamera.js";
import {
  createFaceCountState,
  DETECTION_INTERVAL_MS,
  updateFaceCountState,
} from "../utils/faceTracking.js";

function canvasToBlob(canvas) {
  return new Promise((resolve) => {
    canvas.toBlob(resolve, "image/jpeg", 0.9);
  });
}

function countMessage(detectedCount, expectedCount) {
  if (detectedCount < expectedCount) {
    return `We detect ${detectedCount} of ${expectedCount} ${expectedCount === 1 ? "guest" : "guests"}. Ask everyone to face the camera.`;
  }
  if (detectedCount > expectedCount) {
    return `We detect an extra person. Only ${expectedCount} ${expectedCount === 1 ? "guest" : "guests"} should be in the frame.`;
  }
  return "Everyone is ready. Hold still.";
}

function CameraCapture({
  peopleCount,
  faceDetection,
  onCancel,
  onCaptured,
  onFileSelected,
  onLog,
  onCameraError,
  onPhaseChange,
}) {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const animationFrameRef = useRef(0);
  const lastDetectionAtRef = useRef(-Infinity);
  const phaseRef = useRef("camera_loading");
  const trackerRef = useRef(createFaceCountState(peopleCount));
  const captureInProgressRef = useRef(false);
  const mountedRef = useRef(true);
  const [phase, setPhase] = useState("camera_loading");
  const [faces, setFaces] = useState([]);
  const [faceCount, setFaceCount] = useState(0);
  const [captureError, setCaptureError] = useState(null);
  const { isStarting, isActive, cameraError, startCamera, stopCamera } = useCamera();
  const {
    status: detectorStatus,
    error: detectorError,
    ensureReady,
    detectVideo,
    detectImage,
    retry: retryDetector,
  } = faceDetection;

  const setCameraPhase = useCallback((nextPhase) => {
    phaseRef.current = nextPhase;
    setPhase(nextPhase);
    onPhaseChange(nextPhase);
  }, [onPhaseChange]);

  const reportError = useCallback((error) => {
    if (!mountedRef.current) {
      return;
    }
    const mappedError = error || {
      code: "CAMERA_START_FAILED",
      message: "The camera could not be started. Choose a photo instead.",
      retryable: true,
    };
    setCaptureError(mappedError);
    setCameraPhase("error");
    onCameraError(mappedError);
  }, [onCameraError, setCameraPhase]);

  const resetAlignment = useCallback(() => {
    trackerRef.current = createFaceCountState(peopleCount);
    setFaceCount(0);
    setFaces([]);
    setCaptureError(null);
    setCameraPhase("aligning");
  }, [peopleCount, setCameraPhase]);

  const capturePhoto = useCallback(async () => {
    if (captureInProgressRef.current) {
      return;
    }
    captureInProgressRef.current = true;
    setCameraPhase("capture_check");
    setCaptureError(null);
    onLog({ level: "info", event: "capture_started", message: "Capturing the high-resolution group photo." });

    try {
      const video = videoRef.current;
      const canvas = canvasRef.current;
      if (!video || !canvas || !video.videoWidth || !video.videoHeight) {
        throw new Error("The camera is not ready for capture. Please try again.");
      }

      const width = video.videoWidth;
      const height = video.videoHeight;
      canvas.width = width;
      canvas.height = height;
      const context = canvas.getContext("2d");
      if (!context) {
        throw new Error("The photo could not be captured. Please try again.");
      }
      context.save();
      context.translate(width, 0);
      context.scale(-1, 1);
      context.drawImage(video, 0, 0, width, height);
      context.restore();

      const blob = await canvasToBlob(canvas);
      if (!blob || !blob.size) {
        throw new Error("The photo could not be captured. Please try again.");
      }
      const file = new File([blob], "century-ply-group-photo.jpg", {
        type: "image/jpeg",
        lastModified: Date.now(),
      });
      const finalDetection = await detectImage(file);
      if (finalDetection.count !== peopleCount) {
        const mismatchError = {
          code: "CAPTURE_COUNT_MISMATCH",
          message: `The captured photo shows ${finalDetection.count} of ${peopleCount} ${peopleCount === 1 ? "guest" : "guests"}. Please hold position and try again.`,
          retryable: true,
        };
        onLog({
          level: "warning",
          event: "capture_count_mismatch",
          message: "The final captured frame did not match the selected guest count.",
          details: { detected_count: finalDetection.count, expected_count: peopleCount },
        });
        trackerRef.current = createFaceCountState(peopleCount);
        setFaceCount(finalDetection.count);
        setCaptureError(mismatchError);
        setCameraPhase("aligning");
        return;
      }

      stopCamera();
      onLog({
        level: "success",
        event: "capture_validated",
        message: "The captured photo matches the selected guest count.",
        details: { detected_count: finalDetection.count, width, height },
      });
      onCaptured(file, { width, height, faceCount: finalDetection.count });
    } catch (error) {
      const mappedError = error?.code === "FACE_DETECTION_FAILED"
        ? error
        : { code: "CAPTURE_FAILED", message: error?.message || "The photo could not be captured. Please try again.", retryable: true };
      setCaptureError(mappedError);
      setCameraPhase("aligning");
      onCameraError(mappedError);
    } finally {
      captureInProgressRef.current = false;
    }
  }, [detectImage, onCameraError, onCaptured, onLog, peopleCount, setCameraPhase, stopCamera]);

  const handleDetection = useCallback((result, timestamp) => {
    if (!mountedRef.current || captureInProgressRef.current) {
      return;
    }
    setFaces(result.faces);
    setFaceCount(result.count);
    if (result.count === peopleCount) {
      setCaptureError((current) => current?.code === "CAPTURE_COUNT_MISMATCH" ? null : current);
    }
    const transition = updateFaceCountState(trackerRef.current, result.count, timestamp);
    trackerRef.current = transition.state;

    if (transition.event === "countdown_started") {
      onLog({ level: "success", event: "count_stable", message: "The selected guest count stayed stable for one second." });
      onLog({ level: "info", event: "countdown_started", message: "Five-second countdown started." });
    }
    if (transition.event === "countdown_reset") {
      onLog({ level: "warning", event: "countdown_reset", message: "The detected guest count changed, so the countdown was reset." });
    }
    if (transition.event === "capture_requested") {
      void capturePhoto();
      return;
    }
    if (transition.state.phase !== phaseRef.current) {
      setCameraPhase(transition.state.phase);
    }
  }, [capturePhoto, onLog, setCameraPhase]);

  useEffect(() => {
    let cancelled = false;
    mountedRef.current = true;
    setCameraPhase("camera_loading");
    onLog({ level: "info", event: "camera_starting", message: "Starting camera preview and local face detection." });

    async function openCamera() {
      const [cameraResult, detectorResult] = await Promise.all([
        startCamera(videoRef.current),
        ensureReady(),
      ].map((promise) => promise.catch((error) => ({ ok: false, error }))));
      if (cancelled || !mountedRef.current) {
        return;
      }
      if (!cameraResult.ok) {
        reportError(cameraResult.error);
        return;
      }
      if (detectorResult?.ok === false || detectorResult?.error) {
        reportError(detectorResult.error);
        return;
      }
      setCameraPhase("aligning");
      onLog({ level: "success", event: "camera_ready", message: "Camera and face detection are ready." });
    }

    void openCamera();
    return () => {
      cancelled = true;
      mountedRef.current = false;
      window.cancelAnimationFrame(animationFrameRef.current);
      stopCamera();
    };
  }, [ensureReady, onLog, reportError, setCameraPhase, startCamera, stopCamera]);

  useEffect(() => {
    if (!isActive || detectorStatus !== "ready" || phase === "error" || phase === "capture_check") {
      return undefined;
    }

    let cancelled = false;
    lastDetectionAtRef.current = -Infinity;
    const detectFrame = (timestamp) => {
      if (cancelled) {
        return;
      }
      if (timestamp - lastDetectionAtRef.current >= DETECTION_INTERVAL_MS) {
        lastDetectionAtRef.current = timestamp;
        detectVideo(videoRef.current, timestamp)
          .then((result) => {
            if (result && !cancelled) {
              handleDetection(result, timestamp);
            }
          })
          .catch((error) => {
            if (!cancelled) {
              reportError(error);
            }
          });
      }
      animationFrameRef.current = window.requestAnimationFrame(detectFrame);
    };
    animationFrameRef.current = window.requestAnimationFrame(detectFrame);
    return () => {
      cancelled = true;
      window.cancelAnimationFrame(animationFrameRef.current);
    };
  }, [detectVideo, detectorStatus, handleDetection, isActive, phase, reportError]);

  async function handleRetryDetector() {
    setCaptureError(null);
    setCameraPhase("camera_loading");
    try {
      await retryDetector();
      if (mountedRef.current) {
        resetAlignment();
      }
    } catch (error) {
      reportError(error);
    }
  }

  function handleCancel() {
    stopCamera();
    onLog({ level: "info", event: "camera_stopped", message: "Camera preview stopped." });
    onCancel();
  }

  const visibleError = captureError || cameraError || (detectorStatus === "error" ? detectorError : null);
  const isDetectorError = detectorStatus === "error";
  const statusText = phase === "camera_loading"
    ? (isStarting ? "Requesting camera access…" : "Preparing face detection…")
    : phase === "capture_check"
      ? "Checking the captured photo…"
      : phase === "countdown"
        ? (trackerRef.current.detectedCount === peopleCount
          ? "Hold still — capturing soon"
          : "Hold still — checking the group")
        : countMessage(faceCount, peopleCount);

  return (
    <section className="content-card camera-card" aria-labelledby="camera-heading">
      <div className="camera-card-heading">
        <div>
          <p className="eyebrow">Live alignment</p>
          <h2 id="camera-heading">Fit {peopleCount} {peopleCount === 1 ? "guest" : "guests"} in the frame</h2>
        </div>
        <span className="camera-count-pill"><ScanFace size={16} aria-hidden="true" /> {faceCount}/{peopleCount}</span>
      </div>

      <div className="camera-frame" aria-label="Live camera preview">
        <video ref={videoRef} className="camera-video" playsInline muted autoPlay />
        <FaceGuideOverlay faces={faces} width={videoRef.current?.videoWidth} height={videoRef.current?.videoHeight} />
        <div className={`camera-status${visibleError ? " camera-status-error" : ""}`} aria-live="polite">
          {visibleError ? "Face detection needs attention" : statusText}
        </div>
        {phase === "countdown" && trackerRef.current.countdownValue && (
          <div className="countdown-overlay" role="timer" aria-live="assertive">
            <span>Get ready</span>
            <strong>{trackerRef.current.countdownValue}</strong>
          </div>
        )}
        {phase === "capture_check" && <div className="capture-check-overlay"><span className="mini-spinner" /> Checking final frame</div>}
      </div>

      <canvas ref={canvasRef} className="visually-hidden" aria-hidden="true" />
      <ErrorAlert error={visibleError} />

      {visibleError ? (
        <div className="camera-fallback">
          <p>{isDetectorError ? "Face detection could not start. Retry it or use a photo instead." : "You can use a photo instead."}</p>
          {isDetectorError && (
            <button className="secondary-button" type="button" onClick={handleRetryDetector}>
              <RefreshCw size={18} aria-hidden="true" /> Retry face detection
            </button>
          )}
          <PhotoPicker onFileSelected={onFileSelected} buttonClassName="primary-button" label="Upload a photo" />
        </div>
      ) : (
        <p className="camera-instruction" role="status">
          The countdown starts after the exact count stays steady for one second.
        </p>
      )}

      <button className="text-button" type="button" onClick={handleCancel}>
        <RotateCcw size={17} aria-hidden="true" /> Back to setup
      </button>
      <p className="camera-local-note"><Camera size={14} aria-hidden="true" /> Nothing is uploaded while the camera is aligning.</p>
    </section>
  );
}

export default CameraCapture;
