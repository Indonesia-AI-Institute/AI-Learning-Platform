/**
 * analytics.service.ts
 * ====================
 */

import api from "@/lib/api";
import { StudentAnalytics, ClassAnalyticsResponse } from "@/types/analytics.types";

export const analyticsService = {
  getMyAnalytics: async (): Promise<StudentAnalytics> => {
    const response = await api.get<StudentAnalytics>("/analytics/me");
    return response.data;
  },

  getClassAnalytics: async (classId: string): Promise<ClassAnalyticsResponse> => {
    const response = await api.get<ClassAnalyticsResponse>(`/analytics/class/${classId}`);
    return response.data;
  },
};