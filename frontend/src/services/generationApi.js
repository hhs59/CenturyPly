const IMAGE_DATA_URL_PATTERN = /^data:image\/(jpeg|png|webp);base64,[A-Za-z0-9+/=_-]+$/;
const GENERATION_REQUEST_TIMEOUT_MS = 150_000;
const NON_RETRYABLE_CODES = new Set([
  "PROVIDER_NOT_CONFIGURED",
  "PROVIDER_AUTH_ERROR",
  "PROVIDER_BILLING_ERROR",
  "PEOPLE_COUNT_INVALID",
  "SCENARIO_INVALID",
  "IMAGE_REQUIRED",
  "IMAGE_INVALID_CONTENT",
]);

export class GenerationApiError extends Error {
  constructor({ code, message, status = 0, kind = "application", retryable = true }) {
    super(message);
    this.name = "GenerationApiError";
    this.code = code;
    this.status = status;
    this.kind = kind;
    this.retryable = Boolean(retryable);
  }
}

async function readResponse(response) {
  try {
    return await response.json();
  } catch {
    throw new GenerationApiError({
      code: "API_INVALID_RESPONSE",
      message: "The app received an invalid response. Please try again.",
      status: response.status,
    });
  }
}

export async function generateImage({ peopleCount, scenarioId, file, signal }) {
  const formData = new FormData();
  formData.append("people_count", String(peopleCount));
  formData.append("scenario_id", scenarioId);
  formData.append("image", file, file.name || "portrait.jpg");

  let response;
  let requestTimedOut = false;
  const requestController = new AbortController();
  const timeoutId = globalThis.setTimeout(() => {
    requestTimedOut = true;
    requestController.abort();
  }, GENERATION_REQUEST_TIMEOUT_MS);
  const abortExternalRequest = () => requestController.abort();
  if (signal) {
    if (signal.aborted) {
      requestController.abort();
    } else {
      signal.addEventListener("abort", abortExternalRequest, { once: true });
    }
  }

  try {
    response = await fetch("/api/generate", {
      method: "POST",
      body: formData,
      signal: requestController.signal,
    });
  } catch (error) {
    if (error?.name === "AbortError") {
      throw new GenerationApiError({
        code: requestTimedOut ? "GENERATION_TIMEOUT" : "REQUEST_ABORTED",
        message: requestTimedOut ? "Generation took too long. Please try again." : "Generation was cancelled.",
        kind: "network",
      });
    }
    throw new GenerationApiError({
      code: "NETWORK_ERROR",
      message: "We couldn’t reach the image service. Check your connection and try again.",
      kind: "network",
    });
  } finally {
    globalThis.clearTimeout(timeoutId);
    signal?.removeEventListener("abort", abortExternalRequest);
  }

  const payload = await readResponse(response);
  if (response.ok && payload?.success === true) {
    if (
      typeof payload.request_id !== "string"
      || !payload.request_id
      || typeof payload.result_image !== "string"
      || !IMAGE_DATA_URL_PATTERN.test(payload.result_image)
    ) {
      throw new GenerationApiError({
        code: "API_INVALID_RESPONSE",
        message: "The image service returned an invalid image. Please try again.",
        status: response.status,
      });
    }
    return { resultImage: payload.result_image, publishTicket: payload.photo_publish_ticket || "" };
  }

  const errorCode = typeof payload?.error?.code === "string" ? payload.error.code : "GENERATION_FAILED";
  const errorMessage = typeof payload?.error?.message === "string"
    ? payload.error.message
    : "The image service had a temporary problem. Please try again.";
  throw new GenerationApiError({
    code: errorCode,
    message: errorMessage,
    status: response.status,
    retryable: typeof payload?.error?.retryable === "boolean"
      ? payload.error.retryable
      : !NON_RETRYABLE_CODES.has(errorCode),
  });
}

export async function dataUrlToBlob(imageSource) {
  if (typeof imageSource !== "string" || !IMAGE_DATA_URL_PATTERN.test(imageSource)) {
    throw new GenerationApiError({
      code: "API_INVALID_RESPONSE",
      message: "The generated image data is invalid. Please try again.",
      retryable: true,
    });
  }

  const blob = await fetch(imageSource).then((response) => response.blob());
  if (!blob.size) {
    throw new GenerationApiError({ code: "API_INVALID_RESPONSE", message: "The generated image is empty." });
  }
  return blob;
}
