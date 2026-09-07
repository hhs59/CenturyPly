import { FaceDetector, FilesetResolver } from "@mediapipe/tasks-vision";
import { useCallback, useEffect, useRef, useState } from "react";

const MODEL_ASSET_PATH = "/models/face_detection_full_range_sparse.tflite";
const WASM_PATH = "/wasm";

function normalizeDetections(result) {
  const detections = Array.isArray(result?.detections) ? result.detections : [];
  const faces = detections
    .map((detection) => {
      const box = detection?.boundingBox;
      if (!box || !Number.isFinite(box.originX) || !Number.isFinite(box.originY)) {
        return null;
      }
      return {
        x: box.originX,
        y: box.originY,
        width: Math.max(0, box.width || 0),
        height: Math.max(0, box.height || 0),
        score: detection.categories?.[0]?.score ?? null,
      };
    })
    .filter(Boolean);

  return { faces, count: faces.length };
}

function createDetectionError(message = "Face detection is unavailable. Please try again.") {
  const error = new Error(message);
  error.code = "FACE_DETECTION_FAILED";
  error.retryable = true;
  return error;
}

async function loadImageSource(file) {
  if (typeof createImageBitmap === "function") {
    const bitmap = await createImageBitmap(file);
    return { source: bitmap, dispose: () => bitmap.close() };
  }

  const objectUrl = URL.createObjectURL(file);
  try {
    const image = await new Promise((resolve, reject) => {
      const element = new Image();
      element.onload = () => resolve(element);
      element.onerror = () => reject(createDetectionError("The captured photo could not be read."));
      element.src = objectUrl;
    });
    return {
      source: image,
      dispose: () => URL.revokeObjectURL(objectUrl),
    };
  } catch (error) {
    URL.revokeObjectURL(objectUrl);
    throw error;
  }
}

export function useFaceDetection() {
  const detectorRef = useRef(null);
  const initializationRef = useRef(null);
  const detectorQueueRef = useRef(Promise.resolve());
  const busyRef = useRef(false);
  const mountedRef = useRef(true);
  const [status, setStatus] = useState("idle");
  const [error, setError] = useState(null);

  const updateStatus = useCallback((nextStatus, nextError = null) => {
    if (!mountedRef.current) {
      return;
    }
    setStatus(nextStatus);
    setError(nextError);
  }, []);

  const createDetector = useCallback(async () => {
    const vision = await FilesetResolver.forVisionTasks(WASM_PATH);
    const options = {
      baseOptions: {
        modelAssetPath: MODEL_ASSET_PATH,
        delegate: "GPU",
      },
      runningMode: "VIDEO",
      minDetectionConfidence: 0.5,
      minSuppressionThreshold: 0.3,
    };

    try {
      return await FaceDetector.createFromOptions(vision, options);
    } catch {
      // GPU is preferred for the booth, but CPU keeps older laptops usable.
      return FaceDetector.createFromOptions(vision, {
        ...options,
        baseOptions: { ...options.baseOptions, delegate: "CPU" },
      });
    }
  }, []);

  const ensureReady = useCallback(async () => {
    if (detectorRef.current) {
      return detectorRef.current;
    }
    if (initializationRef.current) {
      return initializationRef.current;
    }

    updateStatus("loading");
    const initialization = createDetector()
      .then((detector) => {
        if (!mountedRef.current) {
          detector.close();
          throw createDetectionError("Face detection was stopped.");
        }
        detectorRef.current = detector;
        updateStatus("ready");
        return detector;
      })
      .catch((initializationError) => {
        const mappedError = createDetectionError(
          "Face detection could not be prepared. Please try again.",
        );
        mappedError.cause = initializationError;
        updateStatus("error", mappedError);
        throw mappedError;
      })
      .finally(() => {
        initializationRef.current = null;
      });

    initializationRef.current = initialization;
    return initialization;
  }, [createDetector, updateStatus]);

  const runExclusive = useCallback(async (operation) => {
    const previous = detectorQueueRef.current;
    let release;
    detectorQueueRef.current = new Promise((resolve) => {
      release = resolve;
    });
    await previous;
    try {
      return await operation();
    } finally {
      release();
    }
  }, []);

  const detectVideo = useCallback(async (video, timestamp) => {
    const detector = detectorRef.current;
    if (!detector || !video || video.readyState < 2 || busyRef.current) {
      return null;
    }

    busyRef.current = true;
    try {
      return await runExclusive(() => normalizeDetections(detector.detectForVideo(video, timestamp)));
    } catch (detectionError) {
      const mappedError = createDetectionError();
      mappedError.cause = detectionError;
      updateStatus("error", mappedError);
      throw mappedError;
    } finally {
      busyRef.current = false;
    }
  }, [runExclusive, updateStatus]);

  const detectImage = useCallback(async (file) => {
    if (!file) {
      throw createDetectionError("A captured photo is required for checking.");
    }
    const detector = await ensureReady();
    const imageSource = await loadImageSource(file);
    try {
      return await runExclusive(async () => {
        await detector.setOptions({ runningMode: "IMAGE" });
        try {
          return {
            ...normalizeDetections(detector.detect(imageSource.source)),
            width: imageSource.source.width || imageSource.source.naturalWidth,
            height: imageSource.source.height || imageSource.source.naturalHeight,
          };
        } finally {
          await detector.setOptions({ runningMode: "VIDEO" });
        }
      });
    } catch (detectionError) {
      const mappedError = detectionError?.code === "FACE_DETECTION_FAILED"
        ? detectionError
        : createDetectionError("The captured photo could not be checked. Please try again.");
      if (mappedError !== detectionError) {
        mappedError.cause = detectionError;
      }
      updateStatus("error", mappedError);
      throw mappedError;
    } finally {
      imageSource.dispose();
    }
  }, [ensureReady, runExclusive, updateStatus]);

  const dispose = useCallback(() => {
    const detector = detectorRef.current;
    detectorRef.current = null;
    if (detector) {
      detector.close();
    }
    if (mountedRef.current) {
      setStatus("idle");
      setError(null);
    }
  }, []);

  const retry = useCallback(async () => {
    dispose();
    return ensureReady();
  }, [dispose, ensureReady]);

  useEffect(() => {
    mountedRef.current = true;
    return () => {
      mountedRef.current = false;
      const detector = detectorRef.current;
      detectorRef.current = null;
      detector?.close();
    };
  }, []);

  return {
    status,
    error,
    ensureReady,
    detectVideo,
    detectImage,
    retry,
    dispose,
  };
}
