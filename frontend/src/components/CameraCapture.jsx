import { ArrowRight, Camera, RefreshCw, RotateCcw, Upload } from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";
import ErrorAlert from "./ErrorAlert.jsx";
import { useCamera } from "../hooks/useCamera.js";
import { ACCEPTED_IMAGE_TYPES, validateImageFile } from "../utils/imageValidation.js";
import {
  areFaceSetsCompatible,
  countMatchedFaces,
  createFaceCountState,
  DETECTION_INTERVAL_MS,
  getCaptureCandidates,
  getDominantForegroundFaces,
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
  onGuestPresence,
  onPhaseChange,
  onProceed,
  onRetake,
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
  const photoPreviewUrlRef = useRef("");
  const uploadRef = useRef(null);
  const mountedRef = useRef(true);
  const [phase, setPhase] = useState("camera_loading");
  const [inputMode, setInputMode] = useState("camera");
  const [countdownValue, setCountdownValue] = useState(null);
  const [captureError, setCaptureError] = useState(null);
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

  const setPhotoPreview = useCallback((file) => {
    if (photoPreviewUrlRef.current) {
      URL.revokeObjectURL(photoPreviewUrlRef.current);
      photoPreviewUrlRef.current = "";
    }

    const nextPreviewUrl = URL.createObjectURL(file);
    photoPreviewUrlRef.current = nextPreviewUrl;
  }, []);

  useEffect(() => () => {
    if (photoPreviewUrlRef.current) {
      URL.revokeObjectURL(photoPreviewUrlRef.current);
    }
  }, []);

  const reportError = useCallback((error) => {
    if (!mountedRef.current) {
      return;
    }
    const mappedError = error || {
      code: "CAMERA_START_FAILED",
      message: "The camera could not be started. Please try again.",
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
      const finalCandidates = getCaptureCandidates(finalDetection.faces, width, height);
      const finalForegroundFaces = getDominantForegroundFaces(finalCandidates, width, height);
      const finalMatchedCount = countMatchedFaces(
        finalForegroundFaces,
        mirrorFaceBoxes(lockedFacesRef.current, width),
        width,
        height,
      );
      if (finalForegroundFaces.length !== peopleCount || finalMatchedCount !== peopleCount) {
        const mismatchError = {
          code: "CAPTURE_COUNT_MISMATCH",
          message: "Make sure only your selected group is in the photo area.",
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
      setPhotoPreview(file);
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
  }, [detectImage, onCaptured, peopleCount, setCameraPhase, setPhotoPreview, stopCamera]);

  const handleDetection = useCallback((result, timestamp) => {
    if (!mountedRef.current || captureInProgressRef.current || photoPreviewUrlRef.current) {
      return;
    }

    const frameWidth = videoRef.current?.videoWidth;
    const frameHeight = videoRef.current?.videoHeight;
    if (!frameWidth || !frameHeight) {
      return;
    }

    const captureCandidates = getCaptureCandidates(result.faces, frameWidth, frameHeight);
    const foregroundFaces = getDominantForegroundFaces(captureCandidates, frameWidth, frameHeight);
    if (foregroundFaces.length > 0) onGuestPresence();
    const primaryFaces = selectPrimaryFaces(foregroundFaces, peopleCount, frameWidth, frameHeight);
    const isCountdown = trackerRef.current.phase === "countdown";
    let detectedCount = foregroundFaces.length;

    if (isCountdown && lockedFacesRef.current.length > 0 && foregroundFaces.length === peopleCount) {
      detectedCount = countMatchedFaces(foregroundFaces, lockedFacesRef.current, frameWidth, frameHeight);
    } else {
      if (!areFaceSetsCompatible(candidateFacesRef.current, primaryFaces, frameWidth, frameHeight)) {
        trackerRef.current = createFaceCountState(peopleCount);
      }
      candidateFacesRef.current = primaryFaces;
    }

    setCaptureError((current) => {
      if (foregroundFaces.length > peopleCount) {
        return current?.code === "FOREGROUND_COUNT_MISMATCH"
          ? current
          : {
              code: "FOREGROUND_COUNT_MISMATCH",
              message: "Make sure only your selected group is in the photo area.",
              retryable: true,
            };
      }
      return current?.code === "CAPTURE_COUNT_MISMATCH" || current?.code === "FOREGROUND_COUNT_MISMATCH"
        ? null
        : current;
    });
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
  }, [capturePhoto, onGuestPresence, peopleCount, setCameraPhase]);

  useEffect(() => {
    let cancelled = false;
    mountedRef.current = true;
    setCameraPhase("camera_loading");

    if (inputMode !== "camera") {
      stopCamera();
      return () => {
        cancelled = true;
        mountedRef.current = false;
        window.cancelAnimationFrame(animationFrameRef.current);
      };
    }

    async function openCamera() {
      const [cameraResult, detectorResult] = await Promise.all([
        startCamera(videoRef.current),
        ensureReady(),
      ].map((promise) => promise.catch((error) => ({ ok: false, error }))));
      if (cancelled || !mountedRef.current || captureInProgressRef.current || photoPreviewUrlRef.current) {
        return;
      }
      if (!cameraResult.ok) {
        if (cameraResult.error) {
          reportError(cameraResult.error);
        }
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
  }, [ensureReady, inputMode, reportError, setCameraPhase, startCamera, stopCamera]);

  useEffect(() => {
    if (!isActive || detectorStatus !== "ready" || phase === "error" || phase === "capture_check" || photoPreviewUrlRef.current) {
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

  async function handleRetryCamera() {
    setCaptureError(null);
    setCameraPhase("camera_loading");
    try {
      if (!isActive) {
        const cameraResult = await startCamera(videoRef.current);
        if (!mountedRef.current) {
          return;
        }
        if (!cameraResult.ok) {
          reportError(cameraResult.error);
          return;
        }
      }
      resetAlignment();
    } catch (error) {
      reportError(error);
    }
  }

  function handleCancel() {
    stopCamera();
    onCancel();
  }

  async function handleBackToCamera() {
    const wasUpload = inputMode === "upload";
    captureTokenRef.current += 1;
    captureInProgressRef.current = false;
    if (photoPreviewUrlRef.current) {
      URL.revokeObjectURL(photoPreviewUrlRef.current);
      photoPreviewUrlRef.current = "";
    }
    setCountdownValue(null);
    setCaptureError(null);
    onRetake();
    setInputMode("camera");
    setCameraPhase("camera_loading");

    // Switching from upload mode reruns the camera initialization effect.
    // A captured camera photo is already in camera mode, so restart its stopped
    // stream explicitly instead of waiting for an unchanged dependency.
    if (wasUpload) return;

    try {
      const cameraResult = await startCamera(videoRef.current);
      if (!mountedRef.current) return;
      if (!cameraResult.ok) {
        if (cameraResult.error) reportError(cameraResult.error);
        return;
      }
      resetAlignment();
    } catch (cameraStartError) {
      reportError(cameraStartError);
    }
  }

  async function handleUpload(event) {
    const file = event.currentTarget.files?.[0];
    event.currentTarget.value = "";
    if (!file) {
      setCameraPhase("aligning");
      return;
    }
    const validation = validateImageFile(file);
    if (!validation.valid) {
      setCaptureError({ code: validation.code, message: validation.message, retryable: false });
      return;
    }

    const uploadToken = captureTokenRef.current + 1;
    captureTokenRef.current = uploadToken;
    captureInProgressRef.current = true;
    setCaptureError(null);
    stopCamera();
    setPhotoPreview(file);
    setCameraPhase("capture_check");

    try {
      const detection = await detectImage(file);
      if (!mountedRef.current || captureTokenRef.current !== uploadToken) return;
      const candidates = getCaptureCandidates(detection.faces, detection.width, detection.height);
      const foregroundFaces = getDominantForegroundFaces(candidates, detection.width, detection.height);
      if (foregroundFaces.length !== peopleCount) {
        setCaptureError({
          code: "UPLOAD_FACE_MISMATCH",
          message: "Make sure only your selected group is in the photo area.",
          retryable: false,
        });
        setCameraPhase("aligning");
        return;
      }

      setCameraPhase("photo_ready");
      onCaptured(file, {
        source: "upload",
        width: detection.width,
        height: detection.height,
        faceCount: foregroundFaces.length,
      });
    } catch (detectionError) {
      if (!mountedRef.current || captureTokenRef.current !== uploadToken) return;
      setCaptureError({
        code: "UPLOAD_DETECTION_FAILED",
        message: detectionError?.message || "The uploaded photo could not be checked. Please try another photo.",
        retryable: false,
      });
      setCameraPhase("aligning");
    } finally {
      if (captureTokenRef.current === uploadToken) captureInProgressRef.current = false;
    }
  }

  const openUpload = () => {
    captureTokenRef.current += 1;
    captureInProgressRef.current = false;
    stopCamera();
    setInputMode("upload");
    setCaptureError(null);
    setCountdownValue(null);
    setCameraPhase("aligning");
    window.requestAnimationFrame(() => uploadRef.current?.click());
  };

  const useCameraInstead = () => {
    captureTokenRef.current += 1;
    captureInProgressRef.current = false;
    if (photoPreviewUrlRef.current) {
      URL.revokeObjectURL(photoPreviewUrlRef.current);
      photoPreviewUrlRef.current = "";
    }
    onRetake();
    setCaptureError(null);
    setCountdownValue(null);
    setInputMode("camera");
    setCameraPhase("camera_loading");
  };

  const cameraErrorState = captureError || cameraError || (detectorStatus === "error" ? detectorError : null) || error;
  const isDetectorError = detectorStatus === "error";
  const visibleError = isPhotoReady ? null : inputMode === "upload" ? captureError : cameraErrorState;
  const isUploadError = captureError?.code?.startsWith("UPLOAD_")
    || captureError?.code?.startsWith("IMAGE_");

  return (
    <section className="content-card camera-card" aria-label={isPhotoReady ? "Review your photo" : "Camera capture"}>
      {isPhotoReady && (
        <div className="camera-card-heading">
          <h2 id="camera-heading">Review your photo</h2>
        </div>
      )}

      <div className="camera-frame" aria-label={isPhotoReady ? "Photo preview" : photoPreviewUrlRef.current ? "Photo preview" : inputMode === "upload" ? "Photo upload" : "Live camera preview"}>
        {inputMode === "camera" && <video ref={videoRef} className="camera-video" playsInline muted autoPlay />}
        {inputMode === "upload" && !photoPreviewUrlRef.current && (
          <div className="camera-upload-placeholder">
            <Upload size={42} aria-hidden="true" />
            <strong>Upload your photo</strong>
            <span>The camera is off</span>
          </div>
        )}
        {photoPreviewUrlRef.current ? (
          <img className="photo-preview" src={photoPreviewUrlRef.current} alt="Captured group photo preview" />
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
      <input
        ref={uploadRef}
        className="visually-hidden"
        type="file"
        accept={ACCEPTED_IMAGE_TYPES.join(",")}
        onChange={handleUpload}
        onCancel={() => setCameraPhase("aligning")}
        tabIndex={-1}
      />
      <ErrorAlert error={visibleError} />

      {isPhotoReady ? (
        <div className="photo-review-actions">
          <button className="secondary-button" type="button" onClick={handleBackToCamera}>
            <RotateCcw size={17} aria-hidden="true" /> Back
          </button>
          <button className="primary-button" type="button" onClick={onProceed}>
            Continue <ArrowRight size={19} aria-hidden="true" />
          </button>
        </div>
      ) : inputMode === "upload" ? (
        <div className="camera-actions">
          <button className="secondary-button" type="button" onClick={useCameraInstead} disabled={phase === "capture_check"}>
            <Camera size={18} aria-hidden="true" /> {visibleError ? "Back" : "Use camera instead"}
          </button>
          <button className="primary-button" type="button" onClick={openUpload} disabled={phase === "capture_check"}>
            <Upload size={18} aria-hidden="true" /> Upload photo
          </button>
        </div>
      ) : visibleError ? (
        <div className="camera-fallback">
          {!isUploadError && isDetectorError && (
            <button className="secondary-button camera-fallback-retry" type="button" onClick={handleRetryDetector}>
              <RefreshCw size={18} aria-hidden="true" /> Retry face detection
            </button>
          )}
          {!isUploadError && !isDetectorError && (
            <button className="primary-button camera-fallback-retry" type="button" onClick={handleRetryCamera}>
              <Camera size={18} aria-hidden="true" /> Try camera again
            </button>
          )}
          <button className="secondary-button" type="button" onClick={isUploadError ? handleBackToCamera : handleCancel}>
            <RotateCcw size={17} aria-hidden="true" /> Back
          </button>
          <button className="secondary-button" type="button" onClick={openUpload}>
            <Upload size={18} aria-hidden="true" /> Upload photo
          </button>
        </div>
      ) : (
        <div className="camera-actions">
          <button className="secondary-button" type="button" onClick={handleCancel}>
            <RotateCcw size={17} aria-hidden="true" /> Back
          </button>
          <button className="primary-button" type="button" onClick={openUpload}>
            <Upload size={18} aria-hidden="true" /> Upload photo
          </button>
        </div>
      )}

    </section>
  );
}

export default CameraCapture;
