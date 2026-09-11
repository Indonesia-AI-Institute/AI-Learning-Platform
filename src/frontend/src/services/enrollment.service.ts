import api from "@/lib/api";
import { Enrollment, EnrollRequest } from "@/types/enrollment.types";

export const enrollmentService = {
  getMyEnrollments: async (): Promise<Enrollment[]> => {
    const response = await api.get<Enrollment[]>("/enrollments/me");
    return response.data;
  },

  enroll: async (data: EnrollRequest): Promise<Enrollment> => {
    const response = await api.post<Enrollment>("/enrollments/", data);
    return response.data;
  },

  unenroll: async (enrollmentId: string): Promise<void> => {
    await api.delete(`/enrollments/${enrollmentId}`);
  },

  getClassEnrollments: async (classId: string): Promise<Enrollment[]> => {
    const response = await api.get<Enrollment[]>(`/enrollments/class/${classId}`);
    return response.data;
  },
};