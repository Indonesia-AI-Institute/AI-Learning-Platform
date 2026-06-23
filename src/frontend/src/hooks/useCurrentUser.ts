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
    staleTime: 1000 * 60 * 5,  // cache 5 menit
    retry: false,               // jangan retry kalau 401
    refetchOnWindowFocus: false, // FIX: mencegah spam /auth/me tiap window focus
                                 // Tanpa ini: setiap tab switch = 401 → redirect loop
  });

  return { user, isLoading, isError };
}
