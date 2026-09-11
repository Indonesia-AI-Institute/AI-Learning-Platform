import axios from "axios";
import { getApiUrl } from "./env";

const api = axios.create({
  baseURL: getApiUrl() ?? "http://localhost:8000/api/v1",
  withCredentials: true,
  headers: {
    "Content-Type": "application/json",
  },
});

// Without this guard, concurrent 401s (e.g. auth/me + another request)
// would each trigger window.location.href, looping the redirect.
let isRedirecting = false;

// Test-only escape hatch. In production this flag never needs resetting —
// setting window.location.href ends the page's JS context entirely. But
// Bun's test runner shares one module registry across every test file in
// the run, so this singleton otherwise leaks between files: whichever
// file's tests trigger a 401 first permanently flips it for every file
// that runs after, in the same process — see tests/unit/api.test.ts's
// "api 401 redirect guard" describe block, which calls this in a
// beforeAll to make its own ordering-sensitive assertions immune to
// whatever ran before it in a full `bun test` run.
export function __resetRedirectGuardForTests() {
  isRedirecting = false;
}

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (
      error.response?.status === 401 &&
      typeof window !== "undefined" &&
      !isRedirecting
    ) {
      if (!window.location.pathname.includes("/login")) {
        isRedirecting = true;
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

export default api;
