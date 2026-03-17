/**
 * task.types.ts
 * =============
 */

export interface Task {
  id: string;
  title: string;
  description: string | null;
  due_date: string | null;
  course_id: string;
}