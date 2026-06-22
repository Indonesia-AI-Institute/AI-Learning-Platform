"use client";

/**
 * useCurrentUser.ts
 * =================
 * Fetch and cache current user info.
 * Used by Navbar and Sidebar to display user details.
 */

import { useQuery } from "@tanstack/react-query";
import { userService } from "@/services/user.service";

export function useCurrentUser() {
  const { data: user, isLoading, isError } = useQuery({
    queryKey: ["currentUser"],
    queryFn: () => userService.getMe(),
    staleTime: 1000 * 60 * 5, // cache 5 menit
    retry: false,              // jangan retry kalau 401
    // Prevent automatic refetch on window focus which can cause a
    // race of 401 requests after the session expires.
    refetchOnWindowFocus: false,
  });

  return { user, isLoading, isError };
}