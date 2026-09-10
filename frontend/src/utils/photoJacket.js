const OUTPUT_WIDTH = 4320;
const PORTRAIT_HEIGHT = 7680;
const FOOTER_HEIGHT = Math.round(PORTRAIT_HEIGHT * 0.14);
const OUTPUT_HEIGHT = PORTRAIT_HEIGHT + FOOTER_HEIGHT;
const JACKET_FONT = '"Cormorant Garamond", Georgia, "Times New Roman", serif';

function fitText(context, text, maxWidth, preferredSize, minimumSize) {
  let size = preferredSize;
  while (size > minimumSize) {
    context.font = `600 ${size}px ${JACKET_FONT}`;
    if (context.measureText(text).width <= maxWidth) break;
    size -= 2;
  }
  return size;
}

function canvasToBlob(canvas) {
  return new Promise((resolve, reject) => {
    canvas.toBlob((blob) => {
      if (blob?.size) resolve(blob);
      else reject(new Error("The branded portrait could not be created."));
    }, "image/jpeg", 0.92);
  });
}

function drawPortrait(context, image) {
  context.fillStyle = "#1c1613";
  context.fillRect(0, 0, OUTPUT_WIDTH, PORTRAIT_HEIGHT);

  // The generated image is requested as 9:16. Cover the full portrait area so
  // the photo remains edge-to-edge without the old blurred side fill.
  const portraitScale = Math.max(OUTPUT_WIDTH / image.width, PORTRAIT_HEIGHT / image.height);
  const portraitWidth = image.width * portraitScale;
  const portraitHeight = image.height * portraitScale;
  context.drawImage(image, (OUTPUT_WIDTH - portraitWidth) / 2, (PORTRAIT_HEIGHT - portraitHeight) / 2, portraitWidth, portraitHeight);
}

export async function createPhotoJacket(imageBlob, scenarioName = "Vietnam Imperial Legacy") {
  if (!imageBlob?.size) throw new Error("The generated portrait is not available.");

  await document.fonts.load('600 180px "Cormorant Garamond"');
  const image = await createImageBitmap(imageBlob);
  const canvas = document.createElement("canvas");
  canvas.width = OUTPUT_WIDTH;
  canvas.height = OUTPUT_HEIGHT;
  const context = canvas.getContext("2d");
  if (!context) {
    image.close();
    throw new Error("The branded portrait could not be created.");
  }

  context.imageSmoothingEnabled = true;
  context.imageSmoothingQuality = "high";
  drawPortrait(context, image);
  image.close();

  const footerTop = PORTRAIT_HEIGHT;
  const gold = context.createLinearGradient(0, footerTop, 0, OUTPUT_HEIGHT);
  gold.addColorStop(0, "#e2bd69");
  gold.addColorStop(0.48, "#c9953d");
  gold.addColorStop(1, "#a96f22");
  context.fillStyle = gold;
  context.fillRect(0, footerTop, OUTPUT_WIDTH, FOOTER_HEIGHT);

  context.fillStyle = "rgba(255, 243, 193, 0.38)";
  context.fillRect(0, footerTop, OUTPUT_WIDTH, 18);
  context.strokeStyle = "rgba(83, 42, 17, 0.55)";
  context.lineWidth = 10;
  context.strokeRect(26, 26, OUTPUT_WIDTH - 52, OUTPUT_HEIGHT - 52);

  const dividerX = Math.round(OUTPUT_WIDTH * 0.42);
  const footerCenter = footerTop + (FOOTER_HEIGHT / 2);
  context.strokeStyle = "rgba(94, 48, 18, 0.62)";
  context.lineWidth = 9;
  context.beginPath();
  context.moveTo(dividerX, footerTop + 190);
  context.lineTo(dividerX, OUTPUT_HEIGHT - 190);
  context.stroke();

  context.fillStyle = "#4c2515";
  context.textAlign = "center";
  context.textBaseline = "middle";
  const brand = "CENTURY PLY";
  const brandSize = fitText(context, brand, dividerX - 260, 190, 100);
  context.font = `600 ${brandSize}px ${JACKET_FONT}`;
  context.fillText(brand, dividerX / 2, footerCenter);

  const title = String(scenarioName).toUpperCase();
  const titleWidth = OUTPUT_WIDTH - dividerX - 260;
  const titleSize = fitText(context, title, titleWidth, 175, 78);
  context.font = `600 ${titleSize}px ${JACKET_FONT}`;
  context.fillText(title, dividerX + ((OUTPUT_WIDTH - dividerX) / 2), footerCenter);

  return canvasToBlob(canvas);
}

export const PHOTO_OUTPUT = Object.freeze({
  width: OUTPUT_WIDTH,
  height: OUTPUT_HEIGHT,
  aspectRatio: "4320:8755",
});
