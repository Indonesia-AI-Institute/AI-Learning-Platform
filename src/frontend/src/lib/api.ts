/**
 * api.ts
 * ======
 * Axios instance with base config.
 * - Base URL from env
 * - Credentials include (for httpOnly cookie)
 * - Auto redirect to login on 401 (with guard to prevent redirect loop)
 */

import axios from "axios";

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1",
  withCredentials: true,
  headers: {
    "Content-Type": "application/json",
  },
});

// =========================================================
// RESPONSE INTERCEPTOR
// =========================================================

// Guard: pastikan redirect hanya terjadi sekali
// tanpa ini, multiple 401 responses (auth/me + request lain)
// akan trigger window.location.href berkali-kali → page loop
let isRedirecting = false;

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (
      error.response?.status === 401 &&
      typeof window !== "undefined" &&
      !isRedirecting
    ) {
      // Jangan redirect kalau sudah di halaman login
      if (!window.location.pathname.includes("/login")) {
        isRedirecting = true;
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

export default api;
