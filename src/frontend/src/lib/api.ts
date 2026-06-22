/**
 * api.ts
 * ======
 * Axios instance with base config.
 * - Base URL from env
 * - Credentials include (for httpOnly cookie)
 * - Auto redirect to login on 401
 */

import axios from "axios";

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1",
  withCredentials: true, // send httpOnly cookie on every request
  headers: {
    "Content-Type": "application/json",
  },
});

// =========================================================
// RESPONSE INTERCEPTOR
// =========================================================

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      if (typeof window !== "undefined") {
        const currentPath = window.location.pathname;
        // Only redirect once and avoid redirect loops.
        if (!currentPath.startsWith("/login")) {
          // Use a simple flag to prevent multiple redirects.
          if (!(window as any).__apiRedirecting) {
            (window as any).__apiRedirecting = true;
            window.location.href = "/login";
          }
        }
      }
    }
    return Promise.reject(error);
  }
);

export default api;