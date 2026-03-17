/**
 * auth.store.ts
 * =============
 * Zustand store for auth client state.
 * Only stores minimal info needed for UI.
 * Source of truth for auth is the httpOnly cookie.
 */

import { create } from "zustand";
import { persist } from "zustand/middleware";
import { User } from "@/types/auth.types";

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;

  setUser: (user: User) => void;
  clearAuth: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      isAuthenticated: false,

      setUser: (user) =>
        set({
          user,
          isAuthenticated: true,
        }),

      clearAuth: () =>
        set({
          user: null,
          isAuthenticated: false,
        }),
    }),
    {
      name: "auth-storage", // localStorage key
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);