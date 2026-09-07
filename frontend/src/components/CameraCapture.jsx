import { ArrowRight, RefreshCw, RotateCcw } from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";
import ErrorAlert from "./ErrorAlert.jsx";
import PhotoPicker from "./PhotoPicker.jsx";
import { useCamera } from "../hooks/useCamera.js";
import { validateImageFile } from "../utils/imageValidation.js";
import {
  areFaceSetsCompatible,
  countMatchedFaces,
  createFaceCountState,
  DETECTION_INTERVAL_MS,
  getCaptureCandidates,
  mirrorFaceBoxes,
  selectPrimaryFaces,
  updateFaceCountState,
} from "../utils/faceTracking.js";

function canvasToBlob(canvas) {
  return new Promise((resolve) => {
    canvas.toBlob(resolve, "image/jpeg", 0.9);
  });
}

function CameraCapture({
  peopleCount,
  error,
  faceDetection,
  isPhotoReady,
  onCancel,
  onCaptured,
  onFileSelected,
  onPhaseChange,
  onProceed,
  uploadStatus,
}) {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const animationFrameRef = useRef(0);
  const lastDetectionAtRef = useRef(-Infinity);
  const phaseRef = useRef("camera_loading");
  const trackerRef = useRef(createFaceCountState(peopleCount));
  const candidateFacesRef = useRef([]);
  const lockedFacesRef = useRef([]);
  const captureInProgressRef = useRef(false);
  const captureTokenRef = useRef(0);
  const uploadedPreviewUrlRef = useRef("");
  const mountedRef = useRef(true);
  const [phase, setPhase] = useState("camera_loading");
  const [countdownValue, setCountdownValue] = useState(null);
  const [captureError, setCaptureError] = useState(null);
  const [uploadedPreviewUrl, setUploadedPreviewUrl] = useState("");
  const { isActive, cameraError, startCamera, stopCamera } = useCamera();
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

  const replacePreview = useCallback((file) => {
    if (uploadedPreviewUrlRef.current) {
      URL.revokeObjectURL(uploadedPreviewUrlRef.current);
      uploadedPreviewUrlRef.current = "";
    }

    const nextPreviewUrl = URL.createObjectURL(file);
    uploadedPreviewUrlRef.current = nextPreviewUrl;
    setUploadedPreviewUrl(nextPreviewUrl);
  }, []);

  const handleFileSelected = useCallback((file) => {
    candidateFacesRef.current = [];
    lockedFacesRef.current = [];
    if (phaseRef.current === "countdown" || phaseRef.current === "capture_check") {
      captureTokenRef.current += 1;
      captureInProgressRef.current = false;
      trackerRef.current = createFaceCountState(peopleCount);
      setCountdownValue(null);
      setCaptureError(null);
      if (phaseRef.current === "capture_check") {
        stopCamera();
      }
      setCameraPhase("aligning");
    }

    const imageValidation = validateImageFile(file);
    if (imageValidation.valid) {
      replacePreview(file);
    } else {
      if (uploadedPreviewUrlRef.current) {
        URL.revokeObjectURL(uploadedPreviewUrlRef.current);
        uploadedPreviewUrlRef.current = "";
      }
      setUploadedPreviewUrl("");
    }
    onFileSelected(file);
  }, [onFileSelected, peopleCount, replacePreview, setCameraPhase, stopCamera]);

  useEffect(() => () => {
    if (uploadedPreviewUrlRef.current) {
      URL.revokeObjectURL(uploadedPreviewUrlRef.current);
    }
  }, []);

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
  }, [setCameraPhase]);

  const resetAlignment = useCallback(() => {
    trackerRef.current = createFaceCountState(peopleCount);
    candidateFacesRef.current = [];
    lockedFacesRef.current = [];
    setCountdownValue(null);
    setCaptureError(null);
    setCameraPhase("aligning");
  }, [peopleCount, setCameraPhase]);

  const capturePhoto = useCallback(async () => {
    if (captureInProgressRef.current) {
      return;
    }
    const captureToken = captureTokenRef.current + 1;
    captureTokenRef.current = captureToken;
    captureInProgressRef.current = true;
    setCameraPhase("capture_check");
    setCountdownValue(null);
    setCaptureError(null);

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
      if (!mountedRef.current || captureTokenRef.current !== captureToken || !captureInProgressRef.current) {
        return;
      }
      if (!blob || !blob.size) {
        throw new Error("The photo could not be captured. Please try again.");
      }
      const file = new File([blob], "century-ply-group-photo.jpg", {
        type: "image/jpeg",
        lastModified: Date.now(),
      });
      const finalDetection = await detectImage(file);
      if (!mountedRef.current || captureTokenRef.current !== captureToken || !captureInProgressRef.current) {
        return;
      }
      const finalMatchedCount = countMatchedFaces(
        finalDetection.faces,
        mirrorFaceBoxes(lockedFacesRef.current, width),
        width,
        height,
      );
      if (finalMatchedCount !== peopleCount) {
        const mismatchError = {
          code: "CAPTURE_COUNT_MISMATCH",
          message: "Please hold position and try again.",
          retryable: true,
        };
        trackerRef.current = createFaceCountState(peopleCount);
        candidateFacesRef.current = [];
        lockedFacesRef.current = [];
        setCaptureError(mismatchError);
        setCameraPhase("aligning");
        return;
      }

      stopCamera();
      replacePreview(file);
      setCameraPhase("photo_ready");
      onCaptured(file, { width, height, faceCount: finalMatchedCount });
    } catch (error) {
      if (!mountedRef.current || captureTokenRef.current !== captureToken || !captureInProgressRef.current) {
        return;
      }
      const mappedError = error?.code === "FACE_DETECTION_FAILED"
        ? error
        : { code: "CAPTURE_FAILED", message: error?.message || "The photo could not be captured. Please try again.", retryable: true };
      setCaptureError(mappedError);
      setCameraPhase("aligning");
    } finally {
      if (captureTokenRef.current === captureToken) {
        captureInProgressRef.current = false;
      }
    }
  }, [detectImage, onCaptured, peopleCount, replacePreview, setCameraPhase, stopCamera]);

  const handleDetection = useCallback((result, timestamp) => {
    if (!mountedRef.current || captureInProgressRef.current || uploadedPreviewUrlRef.current) {
      return;
    }

    const frameWidth = videoRef.current?.videoWidth;
    const frameHeight = videoRef.current?.videoHeight;
    if (!frameWidth || !frameHeight) {
      return;
    }

    const captureCandidates = getCaptureCandidates(result.faces, frameWidth, frameHeight);
    const primaryFaces = selectPrimaryFaces(captureCandidates, peopleCount, frameWidth, frameHeight);
    const isCountdown = trackerRef.current.phase === "countdown";
    let detectedCount = primaryFaces.length;

    if (isCountdown && lockedFacesRef.current.length > 0) {
      detectedCount = countMatchedFaces(captureCandidates, lockedFacesRef.current, frameWidth, frameHeight);
    } else {
      if (!areFaceSetsCompatible(candidateFacesRef.current, primaryFaces, frameWidth, frameHeight)) {
        trackerRef.current = createFaceCountState(peopleCount);
      }
      candidateFacesRef.current = primaryFaces;
    }

    if (detectedCount === peopleCount) {
      setCaptureError((current) => current?.code === "CAPTURE_COUNT_MISMATCH" ? null : current);
    }
    const transition = updateFaceCountState(trackerRef.current, detectedCount, timestamp);
    trackerRef.current = transition.state;
    setCountdownValue(transition.state.countdownValue);

    if (transition.event === "countdown_started") {
      lockedFacesRef.current = primaryFaces;
    }
    if (transition.event === "countdown_reset") {
      lockedFacesRef.current = [];
      candidateFacesRef.current = primaryFaces;
    }
    if (transition.event === "capture_requested") {
      void capturePhoto();
      return;
    }
    if (transition.state.phase !== phaseRef.current) {
      setCameraPhase(transition.state.phase);
    }
  }, [capturePhoto, peopleCount, setCameraPhase]);

  useEffect(() => {
    let cancelled = false;
    mountedRef.current = true;
    setCameraPhase("camera_loading");

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
    }

    void openCamera();
    return () => {
      cancelled = true;
      mountedRef.current = false;
      window.cancelAnimationFrame(animationFrameRef.current);
      stopCamera();
    };
  }, [ensureReady, reportError, setCameraPhase, startCamera, stopCamera]);

  useEffect(() => {
    if (!isActive || detectorStatus !== "ready" || phase === "error" || phase === "capture_check" || uploadStatus === "checking" || uploadedPreviewUrl) {
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
  }, [detectVideo, detectorStatus, handleDetection, isActive, phase, reportError, uploadStatus, uploadedPreviewUrl]);

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
    onCancel();
  }

  const cameraErrorState = captureError || cameraError || (detectorStatus === "error" ? detectorError : null) || error;
  const visibleError = uploadStatus === "checking" ? null : cameraErrorState;
  const isDetectorError = detectorStatus === "error";
  const isUploadLocked = uploadStatus === "checking";

  return (
    <section className="content-card camera-card" aria-label={isPhotoReady ? "Review your photo" : "Camera capture"}>
      {isPhotoReady && (
        <div className="camera-card-heading">
          <h2 id="camera-heading">Review your photo</h2>
        </div>
      )}

      <div className="camera-frame" aria-label={isPhotoReady ? "Photo preview" : uploadedPreviewUrl ? "Uploaded photo preview" : "Live camera preview"}>
        <video ref={videoRef} className="camera-video" playsInline muted autoPlay />
        {uploadedPreviewUrl ? (
          <img className="uploaded-photo-preview" src={uploadedPreviewUrl} alt="Uploaded group photo preview" />
        ) : null}
        {phase === "countdown" && countdownValue && (
          <div className="countdown-overlay" role="timer" aria-live="assertive">
            <span>Get ready</span>
            <strong>{countdownValue}</strong>
          </div>
        )}
        {phase === "capture_check" && <div className="capture-check-overlay"><span className="mini-spinner" /> Checking final frame</div>}
      </div>

      <canvas ref={canvasRef} className="visually-hidden" aria-hidden="true" />
      <ErrorAlert error={visibleError} />

      {isPhotoReady ? (
        <div className="photo-review-actions">
          <button className="secondary-button" type="button" onClick={handleCancel}>
            <RotateCcw size={17} aria-hidden="true" /> Back
          </button>
          <PhotoPicker
            buttonClassName="secondary-button"
            disabled={uploadStatus === "checking"}
            label="Upload image"
            onFileSelected={handleFileSelected}
          />
          <button className="primary-button" type="button" onClick={onProceed} disabled={uploadStatus === "checking"}>
            Continue <ArrowRight size={19} aria-hidden="true" />
          </button>
        </div>
      ) : visibleError ? (
        <div className="camera-fallback">
          {isDetectorError && (
            <button className="secondary-button" type="button" onClick={handleRetryDetector}>
              <RefreshCw size={18} aria-hidden="true" /> Retry face detection
            </button>
          )}
          <PhotoPicker
            onFileSelected={handleFileSelected}
            buttonClassName="primary-button"
            disabled={isUploadLocked}
            label="Upload image"
          />
        </div>
      ) : (
        <div className="camera-actions">
          <button className="secondary-button" type="button" onClick={handleCancel}>
            <RotateCcw size={17} aria-hidden="true" /> Back
          </button>
          <PhotoPicker
            buttonClassName="primary-button"
            disabled={isUploadLocked}
            label="Upload image"
            onFileSelected={handleFileSelected}
          />
        </div>
      )}

      {!isPhotoReady && visibleError && (
        <button className="text-button" type="button" onClick={handleCancel}>
          <RotateCcw size={17} aria-hidden="true" /> Back
        </button>
      )}
    </section>
  );
}

export default CameraCapture;
