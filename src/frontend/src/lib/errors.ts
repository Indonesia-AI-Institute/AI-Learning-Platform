import axios from "axios";

// Every mutation's onError handler in this app extracts the backend's
// error body the same way — centralized here so that logic isn't
// reimplemented (and untyped, via `err: any`) at every call site.
// axios.isAxiosError() narrows without needing an explicit cast.
//
// `detail` is a plain string for most errors, but a list of pydantic
// validation-error objects ({msg: string, ...}) for a 422 — both shapes
// are handled so every call site gets a readable message either way.
export function getErrorMessage(error: unknown, fallback: string): string {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail;

    if (typeof detail === "string") return detail;

    if (Array.isArray(detail)) {
      const messages = detail
        .map((item) =>
          item && typeof item === "object" && "msg" in item
            ? String((item as { msg: unknown }).msg)
            : null
        )
        .filter((msg): msg is string => msg !== null);
      if (messages.length > 0) return messages.join(", ");
    }
  }
  return fallback;
}
