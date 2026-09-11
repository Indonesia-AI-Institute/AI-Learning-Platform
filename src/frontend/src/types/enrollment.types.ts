export interface Enrollment {
  id: string;
  student_id: string;
  class_id: string;
  enrolled_at: string;
}

export interface EnrollRequest {
  class_id: string;
}