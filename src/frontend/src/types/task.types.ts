export interface ClassInfo {
  id: string;
  name: string;
}

export interface Task {
  id: string;
  title: string;
  description: string | null;
  due_date: string | null;
  course_id: string;
  class_info?: ClassInfo | null;
  class_id?: string | null;
  is_active?: boolean;
}