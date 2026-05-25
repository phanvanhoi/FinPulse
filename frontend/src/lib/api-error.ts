import axios from "axios";

/** Extract a readable message from FastAPI / axios errors. */
export function getApiErrorMessage(error: unknown, fallback: string): string {
  if (!axios.isAxiosError(error)) {
    return fallback;
  }

  const detail = error.response?.data?.detail;
  if (typeof detail === "string") {
    return detail;
  }
  if (Array.isArray(detail) && detail.length > 0) {
    const first = detail[0];
    if (typeof first === "object" && first && "msg" in first) {
      return String(first.msg);
    }
  }

  if (error.response?.status === 409) {
    return "Email already registered. Try signing in instead.";
  }
  if (!error.response) {
    return "Cannot reach API server. Check NEXT_PUBLIC_API_URL and nginx.";
  }

  return fallback;
}
