"use client";

/**
 * useAuth.ts
 * ==========
 * Hook for auth actions — login, register, logout.
 * Combines TanStack Query mutations with Zustand store.
 */

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useRouter, useSearchParams } from "next/navigation";
import { authService } from "@/services/auth.service";
import { useAuthStore } from "@/store/auth.store";
import { LoginRequest, RegisterRequest } from "@/types/auth.types";

export function useAuth() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const queryClient = useQueryClient();
  const { clearAuth } = useAuthStore();

  // =========================================================
  // LOGIN
  // =========================================================

  const loginMutation = useMutation({
    mutationFn: (data: LoginRequest) => authService.login(data),
    onSuccess: () => {
      // Invalidate cache supaya data user baru di-fetch ulang
      queryClient.invalidateQueries({ queryKey: ["currentUser"] });

      const from = searchParams.get("from") ?? "/dashboard";
      router.push(from);
      router.refresh();
    },
  });

  // =========================================================
  // REGISTER
  // =========================================================

  const registerMutation = useMutation({
    mutationFn: (data: RegisterRequest) => authService.register(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["currentUser"] });
      router.push("/dashboard");
      router.refresh();
    },
  });

  // =========================================================
  // LOGOUT
  // =========================================================

  const logoutMutation = useMutation({
    mutationFn: () => authService.logout(),
    onSuccess: () => {
      // Clear semua cache supaya tidak ada data user lama tersisa
      queryClient.clear();
      clearAuth();
      router.push("/login");
      router.refresh();
    },
  });

  return {
    login: loginMutation.mutate,
    register: registerMutation.mutate,
    logout: logoutMutation.mutate,

    isLoginLoading: loginMutation.isPending,
    isRegisterLoading: registerMutation.isPending,
    isLogoutLoading: logoutMutation.isPending,

    loginError: loginMutation.error,
    registerError: registerMutation.error,
  };
}