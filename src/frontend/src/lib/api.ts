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
