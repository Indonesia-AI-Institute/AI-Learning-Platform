/**
 * course.types.ts
 * ===============
 */

export interface Course {
  id: string;
  teacher_id: string;
  title: string;
  description: string | null;
  is_active: boolean;
  created_at: string;
}