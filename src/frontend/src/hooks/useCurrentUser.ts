"use client";

import { useQuery } from "@tanstack/react-query";
import { userService } from "@/services/user.service";

export function useCurrentUser() {
  const { data: user, isLoading, isError } = useQuery({
    queryKey: ["currentUser"],
    queryFn: () => userService.getMe(),
    staleTime: 1000 * 60 * 5,
    retry: false,
    // Without this, every tab focus re-fires /auth/me — a 401 there
    // triggers api.ts's redirect guard, looping the user back to login.
    refetchOnWindowFocus: false,
  });

  return { user, isLoading, isError };
}
