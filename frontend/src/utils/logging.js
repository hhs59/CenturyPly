const SENSITIVE_KEY_PATTERN = /(?:api[_-]?key|apikey|authorization|cookie|password|secret|token|credential|base64|data[_-]?url|header)/i;
const IMAGE_DATA_KEY_PATTERN = /^(?:image|image_url|input_reference|input_references|b64_json)$/i;
const BASE64_LIKE_PATTERN = /^[A-Za-z0-9+/=_-]{128,}$/;

function looksLikeBase64(value) {
  return BASE64_LIKE_PATTERN.test(value);
}

export function sanitizeLogValue(value, key = "") {
  if (key && SENSITIVE_KEY_PATTERN.test(key)) {
    return "[REDACTED]";
  }
  if (key && IMAGE_DATA_KEY_PATTERN.test(key)) {
    return "[REDACTED IMAGE DATA]";
  }
  if (Array.isArray(value)) {
    return value.map((item) => sanitizeLogValue(item));
  }
  if (value && typeof value === "object") {
    return Object.fromEntries(Object.entries(value).map(([itemKey, itemValue]) => [
      itemKey,
      sanitizeLogValue(itemValue, itemKey),
    ]));
  }
  if (typeof value === "string" && (value.toLowerCase().startsWith("data:image/") || looksLikeBase64(value))) {
    return "[REDACTED]";
  }
  if (value === null || ["boolean", "number", "string"].includes(typeof value)) {
    return value;
  }
  return String(value);
}

export function createAppError({ code, message, retryable = true, technicalDetails, field } = {}) {
  return {
    code: code || "APPLICATION_ERROR",
    message: message || "Something went wrong. Please try again.",
    retryable: Boolean(retryable),
    ...(technicalDetails ? { technicalDetails: sanitizeLogValue(technicalDetails) } : {}),
    ...(field ? { field } : {}),
  };
}
