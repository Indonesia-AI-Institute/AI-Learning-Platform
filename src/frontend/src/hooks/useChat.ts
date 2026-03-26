"use client";

/**
 * useChat.ts
 * ==========
 * Hook untuk handle chat SSE streaming.
 * Manages local message state dan streaming tokens.
 */

import { useState, useCallback, useRef } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { ChatMessage } from "@/types/chat.types";
import api from "@/lib/api";

interface UseChatOptions {
  sessionId: string;
  initialMessages?: ChatMessage[];
}

export function useChat({ sessionId, initialMessages = [] }: UseChatOptions) {
  const queryClient = useQueryClient();
  const [messages, setMessages] = useState<ChatMessage[]>(initialMessages);
  const [streamingContent, setStreamingContent] = useState<string>("");
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  const sendMessage = useCallback(
    async (content: string) => {
      if (!content.trim() || isStreaming) return;

      setError(null);

      // Add user message to UI immediately
      const userMessage: ChatMessage = {
        role: "user",
        content,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, userMessage]);
      setIsStreaming(true);
      setStreamingContent("");

      // Abort any previous stream
      if (abortRef.current) {
        abortRef.current.abort();
      }
      abortRef.current = new AbortController();

      try {
        // Use fetch for SSE with POST body (EventSource only supports GET)
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL}/chat/sessions/${sessionId}/stream`,
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "include", // send httpOnly cookie
            body: JSON.stringify({
              messages: [{ role: "user", content }],
            }),
            signal: abortRef.current.signal,
          }
        );

        if (!response.ok) {
          throw new Error(`Stream error: ${response.status}`);
        }

        const reader = response.body?.getReader();
        const decoder = new TextDecoder();

        if (!reader) throw new Error("No response body");

        let fullContent = "";
        let buffer = "";

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });

          // Parse SSE lines
          const lines = buffer.split("\n");
          buffer = lines.pop() ?? "";

          for (const line of lines) {
            if (!line.startsWith("data: ")) continue;

            const data = line.slice(6).trim();

            if (data === "[DONE]") {
              // Stream complete — add final assistant message
              setMessages((prev) => [
                ...prev,
                {
                  role: "assistant",
                  content: fullContent,
                  created_at: new Date().toISOString(),
                },
              ]);
              setStreamingContent("");
              setIsStreaming(false);
              // Invalidate history cache
              queryClient.invalidateQueries({
                queryKey: ["chatHistory", sessionId],
              });
              return;
            }

            // Append token
            fullContent += data;
            setStreamingContent(fullContent);
          }
        }
      } catch (err: any) {
        if (err.name === "AbortError") return;
        setError("Failed to send message. Please try again.");
        setIsStreaming(false);
        setStreamingContent("");
      }
    },
    [sessionId, isStreaming, queryClient]
  );

  const stopStream = useCallback(() => {
    abortRef.current?.abort();
    setIsStreaming(false);
    setStreamingContent("");
  }, []);

  const resetMessages = useCallback((msgs: ChatMessage[]) => {
    setMessages(msgs);
  }, []);

  return {
    messages,
    streamingContent,
    isStreaming,
    error,
    sendMessage,
    stopStream,
    resetMessages,
  };
}