export const MAX_UPLOAD_BYTES = 10 * 1024 * 1024;
export const ACCEPTED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/webp"];

const VALIDATION_MESSAGES = {
  IMAGE_REQUIRED: "Choose an image to continue.",
  IMAGE_EMPTY: "That image is empty. Please choose another photo.",
  IMAGE_UNSUPPORTED_TYPE: "Please choose a JPEG, PNG, or WebP image.",
  IMAGE_TOO_LARGE: "That image is larger than 10 MB. Please choose a smaller photo.",
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

  if (file.size > MAX_UPLOAD_BYTES) {
    return { valid: false, code: "IMAGE_TOO_LARGE", message: VALIDATION_MESSAGES.IMAGE_TOO_LARGE };
  }

  return { valid: true, file };
}
