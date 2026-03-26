/**
 * class.types.ts
 * ==============
 */

export interface Class {
  id: string;
  course_id: string;
  name: string;
  description: string | null;
  is_active: boolean;
}