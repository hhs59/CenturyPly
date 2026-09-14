const OUTPUT_WIDTH = 2160;
const PORTRAIT_HEIGHT = 3840;
const FOOTER_HEIGHT = Math.round(PORTRAIT_HEIGHT * 0.12);
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
    }, "image/jpeg", 0.9);
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

function strokeLine(context, startX, startY, endX, endY) {
  context.beginPath();
  context.moveTo(startX, startY);
  context.lineTo(endX, endY);
  context.stroke();
}

function drawCornerDetail(context, x, y, directionX, directionY) {
  strokeLine(context, x, y, x + (directionX * 92), y);
  strokeLine(context, x, y, x, y + (directionY * 92));
  strokeLine(
    context,
    x + (directionX * 22),
    y + (directionY * 22),
    x + (directionX * 62),
    y + (directionY * 62),
  );
}

export async function createPhotoJacket(imageBlob, scenarioName = "Vietnam Imperial Legacy") {
  if (!imageBlob?.size) throw new Error("The generated portrait is not available.");

  await document.fonts.load('600 90px "Cormorant Garamond"');
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
  gold.addColorStop(0, "#f0d990");
  gold.addColorStop(0.18, "#dbba67");
  gold.addColorStop(0.52, "#c59442");
  gold.addColorStop(0.82, "#b1792d");
  gold.addColorStop(1, "#8e571d");
  context.fillStyle = gold;
  context.fillRect(0, footerTop, OUTPUT_WIDTH, FOOTER_HEIGHT);

  context.fillStyle = "rgba(255, 247, 210, 0.48)";
  context.fillRect(0, footerTop, OUTPUT_WIDTH, 8);
  context.strokeStyle = "rgba(82, 43, 17, 0.72)";
  context.lineWidth = 6;
  strokeLine(context, 0, footerTop + 16, OUTPUT_WIDTH, footerTop + 16);

  context.strokeStyle = "rgba(45, 27, 18, 0.9)";
  context.lineWidth = 12;
  context.strokeRect(12, 12, OUTPUT_WIDTH - 24, OUTPUT_HEIGHT - 24);
  context.strokeStyle = "rgba(234, 204, 126, 0.72)";
  context.lineWidth = 3;
  context.strokeRect(31, 31, OUTPUT_WIDTH - 62, OUTPUT_HEIGHT - 62);

  context.strokeStyle = "rgba(82, 43, 17, 0.58)";
  context.lineWidth = 4;
  drawCornerDetail(context, 58, footerTop + 52, 1, 1);
  drawCornerDetail(context, OUTPUT_WIDTH - 58, footerTop + 52, -1, 1);
  drawCornerDetail(context, 58, OUTPUT_HEIGHT - 52, 1, -1);
  drawCornerDetail(context, OUTPUT_WIDTH - 58, OUTPUT_HEIGHT - 52, -1, -1);

  const dividerX = Math.round(OUTPUT_WIDTH * 0.41);
  const footerCenter = footerTop + (FOOTER_HEIGHT / 2);
  context.strokeStyle = "rgba(82, 43, 17, 0.66)";
  context.lineWidth = 4;
  strokeLine(context, dividerX, footerTop + 82, dividerX, OUTPUT_HEIGHT - 82);

  context.fillStyle = "#3f2115";
  context.textAlign = "center";
  context.textBaseline = "middle";
  const brand = "CENTURY PLY";
  const brandSize = fitText(context, brand, dividerX - 150, 88, 48);
  context.font = `600 ${brandSize}px ${JACKET_FONT}`;
  context.fillText(brand, dividerX / 2, footerCenter);

  const title = String(scenarioName).toUpperCase();
  const titleWidth = OUTPUT_WIDTH - dividerX - 170;
  const titleSize = fitText(context, title, titleWidth, 80, 37);
  context.font = `600 ${titleSize}px ${JACKET_FONT}`;
  context.fillText(title, dividerX + ((OUTPUT_WIDTH - dividerX) / 2), footerCenter);

  return canvasToBlob(canvas);
}

export const PHOTO_OUTPUT = Object.freeze({
  width: OUTPUT_WIDTH,
  height: OUTPUT_HEIGHT,
  aspectRatio: "2160:4301",
});
