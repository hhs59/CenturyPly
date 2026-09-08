const JACKET_FONT = '"Cormorant Garamond", Georgia, "Times New Roman", serif';

function fitText(context, text, maxWidth, preferredSize, minimumSize) {
  let size = preferredSize;
  while (size > minimumSize) {
    context.font = `600 ${size}px ${JACKET_FONT}`;
    if (context.measureText(text).width <= maxWidth) {
      break;
    }
    size -= 1;
  }
  return size;
}

function drawCorner(context, x, y, horizontalDirection, verticalDirection, length, step) {
  context.beginPath();
  context.moveTo(x, y + (verticalDirection * length));
  context.lineTo(x, y + (verticalDirection * step));
  context.lineTo(x + (horizontalDirection * step), y);
  context.lineTo(x + (horizontalDirection * length), y);
  context.stroke();
}

function canvasToBlob(canvas) {
  return new Promise((resolve, reject) => {
    canvas.toBlob((blob) => {
      if (blob?.size) {
        resolve(blob);
      } else {
        reject(new Error("The branded portrait could not be created."));
      }
    }, "image/jpeg", 0.92);
  });
}

export async function createPhotoJacket(imageBlob, scenarioName = "Vietnam Imperial Legacy") {
  if (!imageBlob?.size) {
    throw new Error("The generated portrait is not available.");
  }

  await document.fonts.load('600 48px "Cormorant Garamond"');
  const image = await createImageBitmap(imageBlob);
  const canvas = document.createElement("canvas");
  canvas.width = image.width;
  canvas.height = image.height;
  const context = canvas.getContext("2d");
  if (!context) {
    image.close();
    throw new Error("The branded portrait could not be created.");
  }

  context.drawImage(image, 0, 0, canvas.width, canvas.height);
  image.close();

  const width = canvas.width;
  const height = canvas.height;
  const unit = Math.min(width, height);
  const inset = Math.max(18, Math.round(unit * 0.025));
  const gold = "#d8ad57";
  const deepGold = "#a66a22";
  const jacketHeight = Math.round(height * 0.17);
  const jacketTop = height - jacketHeight;

  const fade = context.createLinearGradient(0, jacketTop - (jacketHeight * 0.55), 0, height);
  fade.addColorStop(0, "rgba(22, 11, 8, 0)");
  fade.addColorStop(0.42, "rgba(22, 11, 8, 0.72)");
  fade.addColorStop(1, "rgba(22, 11, 8, 0.96)");
  context.fillStyle = fade;
  context.fillRect(0, jacketTop - (jacketHeight * 0.55), width, jacketHeight * 1.55);

  context.strokeStyle = gold;
  context.lineWidth = Math.max(2, unit * 0.0025);
  context.strokeRect(inset, inset, width - (inset * 2), height - (inset * 2));

  const cornerLength = unit * 0.075;
  const cornerStep = unit * 0.018;
  context.lineWidth = Math.max(3, unit * 0.0035);
  drawCorner(context, inset, inset, 1, 1, cornerLength, cornerStep);
  drawCorner(context, width - inset, inset, -1, 1, cornerLength, cornerStep);
  drawCorner(context, inset, height - inset, 1, -1, cornerLength, cornerStep);
  drawCorner(context, width - inset, height - inset, -1, -1, cornerLength, cornerStep);

  const dividerX = Math.round(width * 0.47);
  const textBottom = jacketTop + (jacketHeight * 0.63);
  context.strokeStyle = deepGold;
  context.lineWidth = Math.max(2, unit * 0.002);
  context.beginPath();
  context.moveTo(dividerX, jacketTop + (jacketHeight * 0.22));
  context.lineTo(dividerX, height - inset - (jacketHeight * 0.12));
  context.stroke();

  context.fillStyle = gold;
  context.textBaseline = "middle";
  context.textAlign = "center";
  context.letterSpacing = `${Math.max(1, unit * 0.0015)}px`;
  const brandText = "CENTURY PLY";
  const brandSize = fitText(context, brandText, dividerX - (inset * 3), unit * 0.048, unit * 0.024);
  context.font = `600 ${brandSize}px ${JACKET_FONT}`;
  context.fillText(brandText, dividerX / 2, textBottom);

  const titleX = dividerX + ((width - dividerX) / 2);
  const titleWidth = width - dividerX - (inset * 3);
  const titleText = String(scenarioName).toUpperCase();
  const words = titleText.split(/\s+/);
  const midpoint = Math.ceil(words.length / 2);
  const lines = words.length > 3
    ? [words.slice(0, midpoint).join(" "), words.slice(midpoint).join(" ")]
    : [titleText];
  const longestLine = lines.reduce((longest, line) => line.length > longest.length ? line : longest, "");
  const titleSize = fitText(context, longestLine, titleWidth, unit * 0.036, unit * 0.021);
  context.font = `600 ${titleSize}px ${JACKET_FONT}`;
  lines.forEach((line, index) => {
    const offset = lines.length === 1 ? 0 : (index - 0.5) * titleSize * 1.18;
    context.fillText(line, titleX, textBottom + offset);
  });

  return canvasToBlob(canvas);
}
