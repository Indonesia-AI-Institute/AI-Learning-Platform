/**
 * user.service.ts
 * ===============
 * User API calls.
 */

import api from "@/lib/api";
import { User } from "@/types/auth.types";

export const userService = {
  getMe: async (): Promise<User> => {
    const response = await api.get<User>("/auth/me");
    return response.data;
  },
};
