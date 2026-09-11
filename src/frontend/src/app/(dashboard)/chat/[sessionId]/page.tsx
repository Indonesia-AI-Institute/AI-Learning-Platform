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

  const resumeCalledRef = useRef(false);

  const {
    data: session,
    isLoading: loadingSession,
    isError: sessionError,
  } = useQuery({
    queryKey: ["session", sessionId],
    queryFn: () => chatService.getSessionById(sessionId),
    staleTime: 0,
    retry: 2,
    retryDelay: 500,
  });

  const resumeMutation = useMutation({
    mutationFn: () => chatService.resumeSession(sessionId),
    onSuccess: (resumed) => {
      queryClient.setQueryData(["session", sessionId], resumed);
    },
  });

  // Depends on the full `session` object rather than session?.is_active —
  // the object reference changes on load, guaranteeing the effect fires.
  useEffect(() => {
    if (!session) return;
    if (session.is_active) return;
    if (resumeCalledRef.current) return;

    resumeCalledRef.current = true;
    resumeMutation.mutate();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [session]);

  const { data: history, isLoading: loadingHistory } = useQuery({
    queryKey: ["chatHistory", sessionId],
    queryFn: () => chatService.getHistory(sessionId),
    enabled: !!sessionId,
    staleTime: 0,
  });

  // No intermediate state: true while resuming (not just after) so new
  // sessions can chat immediately and resumed ones don't wait for resume
  // to fully settle before the input re-enables.
  const canChat = Boolean(
    session?.is_active ||
    resumeMutation.isPending ||
    resumeMutation.isSuccess
  );

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
    isSessionActive: canChat,
  });

  useEffect(() => {
    if (history?.messages && !isStreaming) {
      resetMessages(history.messages);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [history?.messages]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, streamingContent]);

  // Invalidate on unmount so the task page's session list stays in sync
  useEffect(() => {
    return () => {
      if (session?.task_id) {
        queryClient.invalidateQueries({
          queryKey: ["sessionsByTask", session.task_id],
        });
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [session?.task_id]);

  // Only the initial session fetch blocks the page — resume just disables input
  if (loadingSession) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="text-center space-y-2">
          <div className="w-6 h-6 border-2 border-primary border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="text-muted-foreground text-sm">Loading session...</p>
        </div>
      </div>
    );
  }

  if (sessionError || !session) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="text-center space-y-4 max-w-xs px-4">
          <p className="font-medium">Session not found</p>
          <p className="text-sm text-muted-foreground">
            This session may have been deleted.
          </p>
          <Button onClick={() => router.back()}>Go back</Button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-screen bg-background">
      <div className="flex items-center gap-3 px-4 py-3 border-b bg-background shrink-0">
        <Button variant="ghost" size="icon" onClick={() => router.back()}>
          <ArrowLeft className="w-4 h-4" />
        </Button>
        <div className="flex-1 min-w-0">
          <p className="font-medium text-sm truncate">
            {session.title ?? "Untitled session"}
          </p>
          {resumeMutation.isPending && (
            <p className="text-xs text-muted-foreground animate-pulse">
              Resuming...
            </p>
          )}
        </div>
      </div>

      <div className="flex-1 overflow-y-auto px-4 py-6">
        <div className="max-w-3xl mx-auto space-y-4">

          {!loadingHistory && messages.length === 0 && !isStreaming && (
            <div className="flex flex-col items-center justify-center py-16 text-center">
              <p className="font-medium">Start your conversation</p>
              <p className="text-sm text-muted-foreground mt-1">
                Ask the AI anything about this task.
              </p>
            </div>
          )}

          {loadingHistory && (
            <div className="flex justify-center py-8">
              <div className="w-5 h-5 border-2 border-primary border-t-transparent rounded-full animate-spin" />
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

      <ChatInput
        onSend={sendMessage}
        onStop={stopStream}
        isStreaming={isStreaming}
        disabled={!canChat}
      />
    </div>
  );
}