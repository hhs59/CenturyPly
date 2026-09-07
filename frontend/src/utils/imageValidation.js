export const MAX_IMAGE_BYTES = 10 * 1024 * 1024;
export const ACCEPTED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/webp"];

const VALIDATION_MESSAGES = {
  IMAGE_REQUIRED: "Capture a photo to continue.",
  IMAGE_EMPTY: "The captured photo is empty. Please try again.",
  IMAGE_UNSUPPORTED_TYPE: "The captured photo format is not supported. Please try again.",
  IMAGE_TOO_LARGE: "The captured photo is larger than 10 MB. Please try again.",
};

export function validateImageFile(file) {
  if (!file) {
    return { valid: false, code: "IMAGE_REQUIRED", message: VALIDATION_MESSAGES.IMAGE_REQUIRED };
  }

  if (!file.size) {
    return { valid: false, code: "IMAGE_EMPTY", message: VALIDATION_MESSAGES.IMAGE_EMPTY };
  }

  if (!ACCEPTED_IMAGE_TYPES.includes(file.type)) {
    return {
      valid: false,
      code: "IMAGE_UNSUPPORTED_TYPE",
      message: VALIDATION_MESSAGES.IMAGE_UNSUPPORTED_TYPE,
    };
  }

  if (file.size > MAX_IMAGE_BYTES) {
    return { valid: false, code: "IMAGE_TOO_LARGE", message: VALIDATION_MESSAGES.IMAGE_TOO_LARGE };
  }

  return { valid: true, file };
}
