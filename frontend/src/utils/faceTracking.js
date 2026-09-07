export const FACE_STABLE_MS = 1_000;
export const FACE_MISMATCH_GRACE_MS = 400;
export const COUNTDOWN_SECONDS = 5;
export const DETECTION_INTERVAL_MS = 125;

const CAPTURE_ZONE = {
  left: 0.08,
  right: 0.92,
  top: 0.08,
  bottom: 0.92,
};
const MIN_FACE_WIDTH_RATIO = 0.035;
const MIN_FACE_WIDTH_PX = 30;
const FACE_TRACK_DISTANCE_RATIO = 0.075;
const FACE_TRACK_SIZE_RATIO = 0.45;

function faceMetrics(face, frameWidth, frameHeight) {
  if (!face || !Number.isFinite(frameWidth) || !Number.isFinite(frameHeight) || frameWidth <= 0 || frameHeight <= 0) {
    return null;
  }
  if (!Number.isFinite(face.x) || !Number.isFinite(face.y) || !Number.isFinite(face.width) || !Number.isFinite(face.height)) {
    return null;
  }
  if (face.width <= 0 || face.height <= 0) {
    return null;
  }
  return {
    centerX: (face.x + face.width / 2) / frameWidth,
    centerY: (face.y + face.height / 2) / frameHeight,
    widthRatio: face.width / frameWidth,
    heightRatio: face.height / frameHeight,
  };
}

function faceMatches(referenceFace, candidateFace, frameWidth, frameHeight) {
  const reference = faceMetrics(referenceFace, frameWidth, frameHeight);
  const candidate = faceMetrics(candidateFace, frameWidth, frameHeight);
  if (!reference || !candidate) {
    return false;
  }

  const centerDistance = Math.hypot(
    reference.centerX - candidate.centerX,
    reference.centerY - candidate.centerY,
  );
  const sizeRatio = Math.min(
    reference.widthRatio / candidate.widthRatio,
    candidate.widthRatio / reference.widthRatio,
  );
  return centerDistance <= Math.max(FACE_TRACK_DISTANCE_RATIO, reference.widthRatio * 1.5)
    && sizeRatio >= FACE_TRACK_SIZE_RATIO;
}

function matchFacesToTargets(detectedFaces, targetFaces, frameWidth, frameHeight) {
  if (!Array.isArray(detectedFaces) || !Array.isArray(targetFaces)) {
    return 0;
  }

  const unmatchedFaces = [...detectedFaces];
  let matchedCount = 0;
  targetFaces.forEach((targetFace) => {
    let bestMatchIndex = -1;
    let bestDistance = Infinity;
    unmatchedFaces.forEach((candidateFace, index) => {
      if (!faceMatches(targetFace, candidateFace, frameWidth, frameHeight)) {
        return;
      }
      const target = faceMetrics(targetFace, frameWidth, frameHeight);
      const candidate = faceMetrics(candidateFace, frameWidth, frameHeight);
      const distance = Math.hypot(
        target.centerX - candidate.centerX,
        target.centerY - candidate.centerY,
      );
      if (distance < bestDistance) {
        bestDistance = distance;
        bestMatchIndex = index;
      }
    });

    if (bestMatchIndex >= 0) {
      unmatchedFaces.splice(bestMatchIndex, 1);
      matchedCount += 1;
    }
  });
  return matchedCount;
}

export function getCaptureCandidates(faces, frameWidth, frameHeight) {
  if (!Array.isArray(faces)) {
    return [];
  }

  const minimumFaceWidth = Math.max(MIN_FACE_WIDTH_PX, frameWidth * MIN_FACE_WIDTH_RATIO);
  return faces.filter((face) => {
    const metrics = faceMetrics(face, frameWidth, frameHeight);
    return metrics
      && metrics.centerX >= CAPTURE_ZONE.left
      && metrics.centerX <= CAPTURE_ZONE.right
      && metrics.centerY >= CAPTURE_ZONE.top
      && metrics.centerY <= CAPTURE_ZONE.bottom
      && face.width >= minimumFaceWidth;
  });
}

export function selectPrimaryFaces(faces, expectedCount, frameWidth, frameHeight) {
  if (!Array.isArray(faces) || !Number.isFinite(expectedCount) || expectedCount <= 0) {
    return [];
  }

  return faces
    .filter((face) => faceMetrics(face, frameWidth, frameHeight))
    .sort((firstFace, secondFace) => {
      const firstMetrics = faceMetrics(firstFace, frameWidth, frameHeight);
      const secondMetrics = faceMetrics(secondFace, frameWidth, frameHeight);
      const areaDifference = (secondMetrics.widthRatio * secondMetrics.heightRatio)
        - (firstMetrics.widthRatio * firstMetrics.heightRatio);
      if (areaDifference !== 0) {
        return areaDifference;
      }
      return Math.abs(firstMetrics.centerX - 0.5) - Math.abs(secondMetrics.centerX - 0.5);
    })
    .slice(0, Math.round(expectedCount))
    .sort((firstFace, secondFace) => (
      faceMetrics(firstFace, frameWidth, frameHeight).centerX
      - faceMetrics(secondFace, frameWidth, frameHeight).centerX
    ));
}

export function areFaceSetsCompatible(previousFaces, currentFaces, frameWidth, frameHeight) {
  if (!Array.isArray(previousFaces) || !Array.isArray(currentFaces)) {
    return false;
  }
  if (previousFaces.length === 0 && currentFaces.length === 0) {
    return true;
  }
  if (previousFaces.length !== currentFaces.length) {
    return false;
  }
  return matchFacesToTargets(currentFaces, previousFaces, frameWidth, frameHeight) === previousFaces.length;
}

export function countMatchedFaces(detectedFaces, lockedFaces, frameWidth, frameHeight) {
  return matchFacesToTargets(detectedFaces, lockedFaces, frameWidth, frameHeight);
}

export function mirrorFaceBoxes(faces, frameWidth) {
  if (!Array.isArray(faces) || !Number.isFinite(frameWidth)) {
    return [];
  }
  return faces.map((face) => ({ ...face, x: frameWidth - face.x - face.width }));
}

export function createFaceCountState(expectedCount) {
  return {
    expectedCount,
    detectedCount: 0,
    phase: "aligning",
    stableSince: null,
    mismatchSince: null,
    countdownStartedAt: null,
    countdownValue: null,
  };
}

function alignmentState(state, detectedCount) {
  return {
    ...state,
    detectedCount,
    phase: "aligning",
    stableSince: null,
    mismatchSince: null,
    countdownStartedAt: null,
    countdownValue: null,
  };
}

/**
 * Advance the camera timing state from one detector result.
 * Keeping this logic pure makes the 1-second stability, 400ms grace period,
 * and single capture transition straightforward to test without a webcam.
 */
export function updateFaceCountState(state, detectedCount, timestamp) {
  const count = Number.isFinite(detectedCount) ? Math.max(0, Math.round(detectedCount)) : 0;
  const now = Number.isFinite(timestamp) ? timestamp : 0;
  const exact = count === state.expectedCount;

  if (state.phase === "capture_check") {
    return { state: { ...state, detectedCount: count }, event: null };
  }

  if (state.phase === "countdown") {
    if (!exact) {
      const mismatchSince = state.mismatchSince ?? now;
      if (now - mismatchSince >= FACE_MISMATCH_GRACE_MS) {
        return {
          state: alignmentState({ ...state, detectedCount: count }, count),
          event: "countdown_reset",
        };
      }
      return {
        state: { ...state, detectedCount: count, mismatchSince },
        event: null,
      };
    }

    const elapsed = Math.max(0, now - (state.countdownStartedAt ?? now));
    if (elapsed >= COUNTDOWN_SECONDS * 1_000) {
      return {
        state: { ...state, detectedCount: count, mismatchSince: null, phase: "capture_check", countdownValue: 0 },
        event: "capture_requested",
      };
    }

    return {
      state: {
        ...state,
        detectedCount: count,
        mismatchSince: null,
        countdownValue: Math.max(1, Math.ceil((COUNTDOWN_SECONDS * 1_000 - elapsed) / 1_000)),
      },
      event: null,
    };
  }

  if (!exact) {
    return {
      state: alignmentState({ ...state, detectedCount: count }, count),
      event: null,
    };
  }

  const stableSince = state.stableSince ?? now;
  if (now - stableSince < FACE_STABLE_MS) {
    return {
      state: { ...state, detectedCount: count, stableSince, mismatchSince: null },
      event: null,
    };
  }

  return {
    state: {
      ...state,
      detectedCount: count,
      phase: "countdown",
      stableSince: null,
      mismatchSince: null,
      countdownStartedAt: now,
      countdownValue: COUNTDOWN_SECONDS,
    },
    event: "countdown_started",
  };
}
