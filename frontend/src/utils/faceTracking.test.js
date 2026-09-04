import assert from "node:assert/strict";
import test from "node:test";
import {
  createFaceCountState,
  updateFaceCountState,
} from "./faceTracking.js";

test("exact face count needs one full second before countdown", () => {
  let state = createFaceCountState(2);
  let transition = updateFaceCountState(state, 2, 0);
  state = transition.state;
  assert.equal(transition.event, null);
  transition = updateFaceCountState(state, 2, 999);
  state = transition.state;
  assert.equal(transition.event, null);
  transition = updateFaceCountState(state, 2, 1_000);
  assert.equal(transition.event, "countdown_started");
  assert.equal(transition.state.countdownValue, 5);
});

test("four-person groups use the same stable-count timing", () => {
  let state = createFaceCountState(4);
  state = updateFaceCountState(state, 4, 0).state;
  const transition = updateFaceCountState(state, 4, 1_000);

  assert.equal(transition.event, "countdown_started");
  assert.equal(transition.state.expectedCount, 4);
});

test("countdown value advances on later detection frames", () => {
  let state = createFaceCountState(1);
  state = updateFaceCountState(state, 1, 0).state;
  state = updateFaceCountState(state, 1, 1_000).state;

  let transition = updateFaceCountState(state, 1, 3_001);
  assert.equal(transition.state.countdownValue, 3);

  transition = updateFaceCountState(transition.state, 1, 4_001);
  assert.equal(transition.state.countdownValue, 2);
});

test("a brief mismatch is tolerated, but a sustained mismatch resets", () => {
  let state = createFaceCountState(2);
  state = updateFaceCountState(state, 2, 0).state;
  state = updateFaceCountState(state, 2, 1_000).state;

  let transition = updateFaceCountState(state, 1, 1_200);
  state = transition.state;
  transition = updateFaceCountState(state, 1, 1_500);
  assert.equal(transition.event, null);
  assert.equal(transition.state.phase, "countdown");

  transition = updateFaceCountState(transition.state, 2, 1_600);
  assert.equal(transition.state.phase, "countdown");

  transition = updateFaceCountState(transition.state, 1, 1_700);
  transition = updateFaceCountState(transition.state, 1, 2_100);
  assert.equal(transition.event, "countdown_reset");
  assert.equal(transition.state.phase, "aligning");
});

test("countdown requests one capture at zero", () => {
  let state = createFaceCountState(1);
  state = updateFaceCountState(state, 1, 0).state;
  state = updateFaceCountState(state, 1, 1_000).state;
  const transition = updateFaceCountState(state, 1, 6_000);
  assert.equal(transition.event, "capture_requested");
  assert.equal(transition.state.phase, "capture_check");
  assert.equal(transition.state.countdownValue, 0);
});
