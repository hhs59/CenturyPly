import { AlertCircle } from "lucide-react";

function ErrorAlert({ error }) {
  if (!error) {
    return null;
  }

  const message = typeof error === "string" ? error : error.message || "Something went wrong. Please try again.";

  return (
    <div className="error-alert" role="alert">
      <AlertCircle size={18} aria-hidden="true" />
      <span>{message}</span>
    </div>
  );
}

export default ErrorAlert;
