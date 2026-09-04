export const FACE_STABLE_MS = 1_000;
export const FACE_MISMATCH_GRACE_MS = 400;
export const COUNTDOWN_SECONDS = 5;
export const DETECTION_INTERVAL_MS = 125;

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
