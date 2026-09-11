import api from "@/lib/api";
import { Course } from "@/types/course.types";

export const courseService = {
  // All active courses (student browse)
  getAllCourses: async (): Promise<Course[]> => {
    const response = await api.get<Course[]>("/courses/all");
    return response.data;
  },

  // My courses (teacher: own courses, student: enrolled courses)
  getMyCourses: async (): Promise<Course[]> => {
    const response = await api.get<Course[]>("/courses/");
    return response.data;
  },

  getCourseDetail: async (courseId: string): Promise<Course> => {
    const response = await api.get<Course>(`/courses/${courseId}`);
    return response.data;
  },

  createCourse: async (data: Partial<Course>): Promise<Course> => {
    const response = await api.post<Course>("/courses/create/", data);
    return response.data;
  },

  updateCourse: async (courseId: string, data: Partial<Course>): Promise<Course> => {
    const response = await api.put<Course>(`/courses/${courseId}`, data);
    return response.data;
  },

  deleteCourse: async (courseId: string): Promise<void> => {
    await api.delete(`/courses/${courseId}`);
  },
};