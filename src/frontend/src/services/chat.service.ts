/**
 * chat.service.ts
 * ===============
 */

import api from "@/lib/api";
import { ChatSession, ChatSessionCreateRequest } from "@/types/chat.types";

export const chatService = {
  createSession: async (
    taskId: string,
    data: ChatSessionCreateRequest
  ): Promise<ChatSession> => {
    const response = await api.post<ChatSession>(
      `/chat/sessions/task/${taskId}`,
      data
    );
    return response.data;
  },

  getMySessions: async (): Promise<ChatSession[]> => {
    const response = await api.get<ChatSession[]>("/chat/sessions/my");
    return response.data;
  },

  getSessionsByTask: async (taskId: string): Promise<ChatSession[]> => {
    const response = await api.get<ChatSession[]>(
      `/chat/sessions/task/${taskId}`
    );
    return response.data;
  },

  endSession: async (sessionId: string): Promise<ChatSession> => {
    const response = await api.post<ChatSession>(
      `/chat/sessions/${sessionId}/end`
    );
    return response.data;
  },

  resumeSession: async (sessionId: string): Promise<ChatSession> => {
    const response = await api.post<ChatSession>(
      `/chat/sessions/${sessionId}/resume`
    );
    return response.data;
  },
};