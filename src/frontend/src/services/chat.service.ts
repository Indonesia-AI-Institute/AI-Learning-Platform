import api from "@/lib/api";
import {
  ChatSession,
  ChatSessionCreateRequest,
  ChatHistoryResponse,
} from "@/types/chat.types";

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

  // Direct single session fetch — lebih reliable dari getMySessions().find()
  getSessionById: async (sessionId: string): Promise<ChatSession> => {
    const response = await api.get<ChatSession>(`/chat/sessions/${sessionId}`);
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

  getHistory: async (sessionId: string): Promise<ChatHistoryResponse> => {
    const response = await api.get<ChatHistoryResponse>(
      `/chat/sessions/${sessionId}/history`
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

  deleteSession: async (sessionId: string): Promise<void> => {
    await api.delete(`/chat/sessions/${sessionId}`);
  },
};