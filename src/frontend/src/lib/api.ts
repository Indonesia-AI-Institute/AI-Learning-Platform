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
      // Clear client state and redirect to login
      if (typeof window !== "undefined") {
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

export default api;