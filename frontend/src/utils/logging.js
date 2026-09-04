const LOG_LEVELS = new Set(["info", "success", "warning", "error"]);
const SENSITIVE_KEY_PATTERN = /(?:api[_-]?key|apikey|authorization|cookie|password|secret|token|credential|base64|data[_-]?url|header)/i;
const IMAGE_DATA_KEY_PATTERN = /^(?:image|image_url|input_reference|input_references|b64_json)$/i;
const BASE64_LIKE_PATTERN = /^[A-Za-z0-9+/=_-]{128,}$/;
let logSequence = 0;

function createLogId(source = "frontend") {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return `${source}-${crypto.randomUUID()}`;
  }
  logSequence += 1;
  return `${source}-${Date.now()}-${logSequence}`;
}

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

export function createLogEntry(entry, source = "frontend") {
  const timestamp = typeof entry?.timestamp === "string" && !Number.isNaN(Date.parse(entry.timestamp))
    ? entry.timestamp
    : new Date().toISOString();
  return {
    id: entry?.id || createLogId(source),
    source: entry?.source || source,
    timestamp,
    level: LOG_LEVELS.has(entry?.level) ? entry.level : "info",
    event: typeof entry?.event === "string" && entry.event ? entry.event : "application_event",
    message: typeof entry?.message === "string" && entry.message ? entry.message : "Application activity.",
    details: entry?.details && typeof entry.details === "object"
      ? sanitizeLogValue(entry.details)
      : undefined,
  };
}

function logFingerprint(entry) {
  return [entry.source || "unknown", entry.timestamp, entry.event, entry.message].join("|");
}

export function mergeLogEntries(existing, incoming, source = "backend") {
  const current = Array.isArray(existing) ? existing.map((entry) => createLogEntry(entry, entry.source || "frontend")) : [];
  const knownIds = new Set(current.map((entry) => entry.id));
  const knownFingerprints = new Set(current.map(logFingerprint));
  const additions = (Array.isArray(incoming) ? incoming : []).map((entry) => createLogEntry(entry, source)).filter((entry) => {
    const fingerprint = logFingerprint(entry);
    if (knownIds.has(entry.id) || knownFingerprints.has(fingerprint)) {
      return false;
    }
    knownIds.add(entry.id);
    knownFingerprints.add(fingerprint);
    return true;
  });
  return [...current, ...additions]
    .map((entry, index) => ({ entry, index }))
    .sort((left, right) => {
      const timeDifference = Date.parse(left.entry.timestamp) - Date.parse(right.entry.timestamp);
      return timeDifference || left.index - right.index;
    })
    .map(({ entry }) => entry);
}

export function formatLogTime(timestamp) {
  const date = new Date(timestamp);
  if (Number.isNaN(date.getTime())) {
    return "Unknown time";
  }
  try {
    return new Intl.DateTimeFormat(undefined, {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    }).format(date);
  } catch {
    return date.toLocaleTimeString();
  }
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
