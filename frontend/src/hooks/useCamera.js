import { useCallback, useEffect, useRef, useState } from "react";

const CAMERA_CONSTRAINTS = {
  video: {
    facingMode: "user",
    width: { ideal: 1080 },
    height: { ideal: 1920 },
  },
  audio: false,
};

function mapCameraError(error) {
  const errorName = error?.name;
  const errors = {
    NotAllowedError: {
      code: "CAMERA_PERMISSION_DENIED",
      message: "Camera permission was denied. Please try again or ask event staff for help.",
      retryable: true,
    },
    SecurityError: {
      code: "CAMERA_PERMISSION_DENIED",
      message: "Camera access is blocked here. Please try again or ask event staff for help.",
      retryable: true,
    },
    NotFoundError: {
      code: "CAMERA_NOT_FOUND",
      message: "No camera was found. Please ask event staff for help.",
      retryable: true,
    },
    NotReadableError: {
      code: "CAMERA_BUSY",
      message: "The camera is busy or unavailable. Close other camera apps and try again.",
      retryable: true,
    },
  };

  return errors[errorName] || {
    code: "CAMERA_START_FAILED",
    message: "The camera could not be started. Please try again.",
    retryable: true,
  };
}

function unsupportedCameraError() {
  return {
    code: "CAMERA_UNSUPPORTED",
    message: "This browser does not support camera access. Please ask event staff for help.",
    retryable: true,
  };
}

export function useCamera() {
  const streamRef = useRef(null);
  const videoElementRef = useRef(null);
  const startTokenRef = useRef(0);
  const [isStarting, setIsStarting] = useState(false);
  const [isActive, setIsActive] = useState(false);
  const [cameraError, setCameraError] = useState(null);

  const stopCamera = useCallback(() => {
    startTokenRef.current += 1;
    streamRef.current?.getTracks().forEach((track) => track.stop());
    streamRef.current = null;
    if (videoElementRef.current) {
      videoElementRef.current.pause();
      videoElementRef.current.srcObject = null;
    }
    setIsStarting(false);
    setIsActive(false);
  }, []);

  const startCamera = useCallback(async (videoElement) => {
    const startToken = startTokenRef.current + 1;
    startTokenRef.current = startToken;
    stopCamera();
    startTokenRef.current = startToken;
    setCameraError(null);
    setIsStarting(true);

    if (typeof navigator === "undefined" || !navigator.mediaDevices?.getUserMedia) {
      const error = unsupportedCameraError();
      setCameraError(error);
      setIsStarting(false);
      return { ok: false, error };
    }

    if (!videoElement) {
      const error = { code: "CAMERA_START_FAILED", message: "The camera preview is unavailable. Please try again.", retryable: true };
      setCameraError(error);
      setIsStarting(false);
      return { ok: false, error };
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia(CAMERA_CONSTRAINTS);
      if (startTokenRef.current !== startToken) {
        stream.getTracks().forEach((track) => track.stop());
        return { ok: false, error: null };
      }

      streamRef.current = stream;
      videoElementRef.current = videoElement;
      videoElement.srcObject = stream;
      videoElement.muted = true;
      videoElement.playsInline = true;
      await videoElement.play();

      if (startTokenRef.current !== startToken || !stream.active) {
        stopCamera();
        return { ok: false, error: null };
      }

      setIsStarting(false);
      setIsActive(true);
      return { ok: true, error: null };
    } catch (error) {
      const mappedError = mapCameraError(error);
      streamRef.current?.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
      videoElement.srcObject = null;
      setCameraError(mappedError);
      setIsStarting(false);
      setIsActive(false);
      return { ok: false, error: mappedError };
    }
  }, [stopCamera]);

  useEffect(() => stopCamera, [stopCamera]);

  return { streamRef, isStarting, isActive, cameraError, startCamera, stopCamera };
}
