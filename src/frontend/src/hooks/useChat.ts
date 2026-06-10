"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { ChatMessage } from "@/types/chat.types";

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

  // Ref selalu simpan nilai terbaru — fix stale closure di cleanup effect
  const isActiveRef = useRef(isSessionActive);
  const sessionIdRef = useRef(sessionId);

  useEffect(() => {
    isActiveRef.current = isSessionActive;
  }, [isSessionActive]);

  useEffect(() => {
    sessionIdRef.current = sessionId;
  }, [sessionId]);

  // Auto-end saat component unmount (student navigasi keluar dari chat room)
  // Dependency array [] intentional — cleanup hanya perlu mount/unmount lifecycle
  // Pakai ref bukan state untuk menghindari stale closure
  useEffect(() => {
    return () => {
      if (!sessionIdRef.current) return;
      if (!isActiveRef.current) return; // jangan end session yang sudah ended

      fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/chat/sessions/${sessionIdRef.current}/auto-end`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          credentials: "include",
          keepalive: true, // pastikan request selesai meski page unload
        }
      ).catch(() => {
        // Ignore errors — auto-end adalah best-effort
      });
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // mount/unmount only

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
          `${process.env.NEXT_PUBLIC_API_URL}/chat/sessions/${sessionId}/stream`,
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