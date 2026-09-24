import api from "@/lib/api";
import { StudentAnalytics } from "@/types/analytics.types";
import { ChatSession, ChatHistoryResponse } from "@/types/chat.types";

export interface PromptClassificationRow {
  student_id?: string;
  student_name?: string;
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

  getStudentSessions: async (studentId: string, taskId?: string): Promise<ChatSession[]> => {
    const params = taskId ? `?task_id=${taskId}` : "";
    const response = await api.get<ChatSession[]>(`/chat/teacher/student/${studentId}/sessions${params}`);
    return response.data;
  },

  getSessionHistory: async (sessionId: string): Promise<ChatHistoryResponse> => {
    const response = await api.get<ChatHistoryResponse>(`/chat/teacher/sessions/${sessionId}/history`);
    return response.data;
  },
};