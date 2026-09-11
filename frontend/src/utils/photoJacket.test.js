import assert from "node:assert/strict";
import test from "node:test";
import { createPhotoJacket, PHOTO_OUTPUT } from "./photoJacket.js";

test("photo jacket renders a full 9:16 portrait followed by the branded footer", async () => {
  const calls = [];
  const gradient = { addColorStop() {} };
  const context = {
    beginPath() {},
    createLinearGradient() { return gradient; },
    drawImage(...args) { calls.push(args); },
    fillRect() {},
    fillText() {},
    measureText(text) { return { width: text.length * 80 }; },
    moveTo() {},
    lineTo() {},
    restore() {},
    save() {},
    stroke() {},
    strokeRect() {},
  };
  const canvas = {
    width: 0,
    height: 0,
    getContext: () => context,
    toBlob: (callback) => callback(new Blob(["jpeg"], { type: "image/jpeg" })),
  };
  globalThis.document = {
    fonts: { load: async () => [] },
    createElement: () => canvas,
  };
  globalThis.createImageBitmap = async () => ({ width: 1536, height: 2752, close() {} });

  const blob = await createPhotoJacket(new Blob(["source"], { type: "image/jpeg" }), "Hue Imperial City");

  assert.deepEqual(PHOTO_OUTPUT, { width: 2160, height: 4378, aspectRatio: "2160:4378" });
  assert.equal(canvas.width, 2160);
  assert.equal(canvas.height, 4378);
  assert.equal(blob.type, "image/jpeg");
  assert.equal(calls.length, 1);
});
