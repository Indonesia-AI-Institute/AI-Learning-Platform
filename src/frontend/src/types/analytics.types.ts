/**
 * analytics.types.ts
 * ==================
 */

export interface StudentAnalytics {
  total_sessions: number;
  total_prompts: number;
  total_prompt_tokens: number;
  total_completion_tokens: number;
  total_tokens: number;
  avg_prompt_length: number;
  total_duration_seconds: number;
  last_active: string | null;
}

export interface StudentAnalyticsSummary {
  student_id: string;
  total_sessions: number;
  total_prompts: number;
  total_tokens: number;
  avg_prompt_length: number;
  total_duration_seconds: number;
  last_active: string | null;
}

export interface ClassAnalyticsResponse {
  class_id: string;
  students: StudentAnalyticsSummary[];
}