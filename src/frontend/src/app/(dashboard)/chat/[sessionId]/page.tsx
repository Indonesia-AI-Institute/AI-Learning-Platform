"use client";

/**
 * app/(dashboard)/chat/[sessionId]/page.tsx
 * ==========================================
 * Main chat room page.
 * - Load history on mount
 * - SSE streaming
 * - End session
 */

import { useEffect, useRef } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useParams, useRouter } from "next/navigation";
import { chatService } from "@/services/chat.service";
import { useChat } from "@/hooks/useChat";
import { ChatMessage } from "@/components/chat/ChatMessage";
import { StreamingMessage } from "@/components/chat/StreamingMessage";
import { ChatInput } from "@/components/chat/ChatInput";
import { ChatHeader } from "@/components/chat/ChatHeader";

export default function ChatRoomPage() {
  const { sessionId } = useParams<{ sessionId: string }>();
  const router = useRouter();
  const queryClient = useQueryClient();
  const bottomRef = useRef<HTMLDivElement>(null);

  // Fetch session detail
  const { data: session, isLoading: loadingSession } = useQuery({
    queryKey: ["session", sessionId],
    queryFn: async () => {
      const sessions = await chatService.getMySessions();
      return sessions.find((s) => s.id === sessionId) ?? null;
    },
  });

  // Fetch history
  const { data: history, isLoading: loadingHistory } = useQuery({
    queryKey: ["chatHistory", sessionId],
    queryFn: () => chatService.getHistory(sessionId),
  });

  const {
    messages,
    streamingContent,
    isStreaming,
    error,
    sendMessage,
    stopStream,
    resetMessages,
  } = useChat({
    sessionId,
    initialMessages: history?.messages ?? [],
  });

  // Sync history into chat state when loaded
  useEffect(() => {
    if (history?.messages) {
      resetMessages(history.messages);
    }
  }, [history, resetMessages]);

  // Auto scroll to bottom
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, streamingContent]);

  // End session
  const endMutation = useMutation({
    mutationFn: () => chatService.endSession(sessionId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["session", sessionId] });
      queryClient.invalidateQueries({ queryKey: ["sessionsByTask"] });
      router.back();
    },
  });

  const isLoading = loadingSession || loadingHistory;
  const isSessionActive = session?.is_active ?? false;

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <p className="text-muted-foreground text-sm">Loading session...</p>
      </div>
    );
  }

  if (!session) {
    return (
      <div className="flex h-screen items-center justify-center">
        <p className="text-muted-foreground text-sm">Session not found.</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-screen bg-background">

      {/* Header */}
      <ChatHeader
        session={session}
        onEndSession={() => endMutation.mutate()}
        isEnding={endMutation.isPending}
      />

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-6">
        <div className="max-w-3xl mx-auto space-y-4">

          {messages.length === 0 && !isStreaming && (
            <div className="flex flex-col items-center justify-center py-16 text-center">
              <p className="font-medium">Start your conversation</p>
              <p className="text-sm text-muted-foreground mt-1">
                Ask the AI anything about this task.
              </p>
            </div>
          )}

          {messages.map((msg, idx) => (
            <ChatMessage key={idx} message={msg} />
          ))}

          {isStreaming && streamingContent && (
            <StreamingMessage content={streamingContent} />
          )}

          {error && (
            <p className="text-sm text-destructive text-center">{error}</p>
          )}

          <div ref={bottomRef} />
        </div>
      </div>

      {/* Input */}
      <ChatInput
        onSend={sendMessage}
        onStop={stopStream}
        isStreaming={isStreaming}
        disabled={!isSessionActive}
      />

      {/* Ended session notice */}
      {!isSessionActive && (
        <div className="px-4 pb-4">
          <p className="text-xs text-center text-muted-foreground">
            This session has ended. Go back to the task to resume.
          </p>
        </div>
      )}
    </div>
  );
}