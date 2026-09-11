import api from "@/lib/api";
import { Task } from "@/types/task.types";

export const taskService = {
  getTasksByCourse: async (courseId: string): Promise<Task[]> => {
    const response = await api.get<Task[]>(`/tasks/course/${courseId}`);
    return response.data;
  },

  getTasksByClass: async (classId: string): Promise<Task[]> => {
    const response = await api.get<Task[]>(`/tasks/class/${classId}`);
    return response.data;
  },

  getTaskDetail: async (taskId: string): Promise<Task> => {
    const response = await api.get<Task>(`/tasks/${taskId}`);
    return response.data;
  },

  createTask: async (courseId: string, data: Partial<Task>): Promise<Task> => {
    const response = await api.post<Task>(`/tasks/course/${courseId}`, data);
    return response.data;
  },

  updateTask: async (taskId: string, data: Partial<Task>): Promise<Task> => {
    const response = await api.put<Task>(`/tasks/${taskId}`, data);
    return response.data;
  },

  deleteTask: async (taskId: string): Promise<void> => {
    await api.delete(`/tasks/${taskId}`);
  },
};