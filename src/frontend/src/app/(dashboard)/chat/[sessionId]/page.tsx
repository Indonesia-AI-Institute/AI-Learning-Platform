"use client";

import { useEffect, useRef } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useParams, useRouter } from "next/navigation";
import { chatService } from "@/services/chat.service";
import { useChat } from "@/hooks/useChat";
import { ChatMessage } from "@/components/chat/ChatMessage";
import { StreamingMessage } from "@/components/chat/StreamingMessage";
import { ChatInput } from "@/components/chat/ChatInput";
import { Button } from "@/components/ui/button";
import { ArrowLeft } from "lucide-react";

export default function ChatRoomPage() {
  const { sessionId } = useParams<{ sessionId: string }>();
  const router = useRouter();
  const queryClient = useQueryClient();
  const bottomRef = useRef<HTMLDivElement>(null);

  const { data: session } = useQuery({
    queryKey: ["session", sessionId],
    queryFn: async () => {
      const sessions = await chatService.getMySessions();
      return sessions.find((s) => s.id === sessionId) ?? null;
    },
  });

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
    isSessionActive: session?.is_active ?? true,
  });

  useEffect(() => {
    if (history?.messages) resetMessages(history.messages);
  }, [history, resetMessages]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, streamingContent]);

  const isSessionActive = session?.is_active ?? false;

  if (loadingHistory) {
    return (
      <div className="flex h-screen items-center justify-center">
        <p className="text-muted-foreground text-sm">Loading session...</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-screen bg-background">

      {/* Header — simplified, no end button */}
      <div className="flex items-center gap-3 px-4 py-3 border-b bg-background">
        <Button
          variant="ghost"
          size="icon"
          onClick={() => router.back()}
        >
          <ArrowLeft className="w-4 h-4" />
        </Button>
        <div className="flex-1 min-w-0">
          <p className="font-medium text-sm truncate">
            {session?.title ?? "Untitled session"}
          </p>
          <div className="flex items-center gap-1.5">
            <span className={`w-1.5 h-1.5 rounded-full ${isSessionActive ? "bg-green-500" : "bg-gray-400"}`} />
            <span className="text-xs text-muted-foreground">
              {isSessionActive ? "Active" : "Ended — read only"}
            </span>
          </div>
        </div>
      </div>

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

      {!isSessionActive && (
        <div className="px-4 pb-3">
          <p className="text-xs text-center text-muted-foreground">
            This session has ended. Go back to the task to resume.
          </p>
        </div>
      )}
    </div>
  );
}