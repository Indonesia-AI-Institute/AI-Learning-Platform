import api from "@/lib/api";
import { Class } from "@/types/class.types";

export const classService = {
  getMyClasses: async (): Promise<Class[]> => {
    const response = await api.get<Class[]>("/classes/");
    return response.data;
  },

  getClassesByCourse: async (courseId: string): Promise<Class[]> => {
    const response = await api.get<Class[]>(`/classes/course/${courseId}`);
    return response.data;
  },

  getClassDetail: async (classId: string): Promise<Class> => {
    const response = await api.get<Class>(`/classes/${classId}`);
    return response.data;
  },

  createClass: async (data: Partial<Class> & { course_id: string }): Promise<Class> => {
    const response = await api.post<Class>("/classes/", data);
    return response.data;
  },

  updateClass: async (classId: string, data: Partial<Class>): Promise<Class> => {
    const response = await api.put<Class>(`/classes/${classId}`, data);
    return response.data;
  },

  deleteClass: async (classId: string): Promise<void> => {
    await api.delete(`/classes/${classId}`);
  },
};