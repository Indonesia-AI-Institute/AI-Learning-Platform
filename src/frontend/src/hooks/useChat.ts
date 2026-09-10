"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { ChatMessage } from "@/types/chat.types";
import { getApiUrl } from "@/lib/env";

interface UseChatOptions {
  sessionId: string;
  initialMessages?: ChatMessage[];
  isSessionActive?: boolean;
}

export function useChat({
  sessionId,
  initialMessages = [],
  isSessionActive = true,
}: UseChatOptions) {
  const queryClient = useQueryClient();
  const [messages, setMessages] = useState<ChatMessage[]>(initialMessages);
  const [streamingContent, setStreamingContent] = useState<string>("");
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  // Refs (not state) so the unmount cleanup below always reads the latest
  // value instead of the one captured when the effect first ran.
  const isActiveRef = useRef(isSessionActive);
  const sessionIdRef = useRef(sessionId);

  useEffect(() => {
    isActiveRef.current = isSessionActive;
  }, [isSessionActive]);

  useEffect(() => {
    sessionIdRef.current = sessionId;
  }, [sessionId]);

  // Ends the session when the student navigates away from the chat room.
  useEffect(() => {
    return () => {
      if (!sessionIdRef.current) return;
      if (!isActiveRef.current) return;

      fetch(
        `${getApiUrl()}/chat/sessions/${sessionIdRef.current}/auto-end`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          credentials: "include",
          keepalive: true, // lets the request finish even after page unload
        }
      ).catch(() => {});
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const sendMessage = useCallback(
    async (content: string) => {
      if (!content.trim() || isStreaming) return;

      setError(null);

      const userMessage: ChatMessage = {
        role: "user",
        content,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, userMessage]);
      setIsStreaming(true);
      setStreamingContent("");

      if (abortRef.current) abortRef.current.abort();
      abortRef.current = new AbortController();

      try {
        const response = await fetch(
          `${getApiUrl()}/chat/sessions/${sessionId}/stream`,
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "include",
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
          const lines = buffer.split("\n");
          buffer = lines.pop() ?? "";

          for (const line of lines) {
            if (!line.startsWith("data: ")) continue;
            const data = line.slice(6).trim();

            if (data === "[DONE]") {
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
              queryClient.invalidateQueries({
                queryKey: ["chatHistory", sessionId],
              });
              return;
            }

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