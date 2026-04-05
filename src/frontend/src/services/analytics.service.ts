/**
 * analytics.service.ts
 */

import api from "@/lib/api";
import { StudentAnalytics, ClassAnalyticsResponse } from "@/types/analytics.types";

export interface PromptClassificationRow {
  student_id?: string;
  total_prompts: number;
  direct_answer_pct: number;
  explanation_pct: number;
  step_by_step_pct: number;
  example_pct: number;
  rewrite_pct: number;
  feedback_pct: number;
  summary_pct: number;
  translation_pct: number;
  brainstorm_pct: number;
}

export const analyticsService = {
  getMyAnalytics: async (): Promise<StudentAnalytics> => {
    const response = await api.get<StudentAnalytics>("/analytics/me");
    return response.data;
  },

  getMyClassifications: async (): Promise<PromptClassificationRow | null> => {
    const response = await api.get<{ data: PromptClassificationRow | null }>("/analytics/me/classifications");
    return response.data.data;
  },

  getClassAnalytics: async (classId: string): Promise<ClassAnalyticsResponse> => {
    const response = await api.get<ClassAnalyticsResponse>(`/analytics/class/${classId}`);
    return response.data;
  },

  getClassClassifications: async (classId: string): Promise<PromptClassificationRow[]> => {
    const response = await api.get<{ students: PromptClassificationRow[] }>(`/analytics/class/${classId}/classifications`);
    return response.data.students;
  },

  getCourseClassifications: async (courseId: string): Promise<PromptClassificationRow[]> => {
    const response = await api.get<{ students: PromptClassificationRow[] }>(`/analytics/course/${courseId}/classifications`);
    return response.data.students;
  },

  getTaskClassifications: async (taskId: string): Promise<PromptClassificationRow[]> => {
    const response = await api.get<{ students: PromptClassificationRow[] }>(`/analytics/task/${taskId}/classifications`);
    return response.data.students;
  },

  getStudentClassifications: async (studentId: string): Promise<PromptClassificationRow[]> => {
    const response = await api.get<{ data: PromptClassificationRow[] }>(`/analytics/student/${studentId}/classifications`);
    return response.data.data;
  },
};