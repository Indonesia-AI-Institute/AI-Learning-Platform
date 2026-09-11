export interface TeacherInfo {
  id: string;
  full_name: string;
}

export interface Course {
  id: string;
  teacher_id: string;
  title: string;
  description: string | null;
  is_active: boolean;
  created_at: string;
  teacher?: TeacherInfo | null;
}