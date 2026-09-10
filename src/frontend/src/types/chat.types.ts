export interface ChatSession {
  id: string;
  student_id: string;
  task_id: string;
  title: string | null;
  is_active: boolean;
  ended_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface ChatSessionCreateRequest {
  title?: string;
}

export interface ChatMessage {
  role: "user" | "assistant" | "system";
  content: string;
  created_at: string;
}

export interface ChatHistoryResponse {
  session_id: string;
  messages: ChatMessage[];
}