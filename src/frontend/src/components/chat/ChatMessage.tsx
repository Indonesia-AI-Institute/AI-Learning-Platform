"use client";

/**
 * ChatMessage.tsx
 * ===============
 * Single chat message bubble.
 */

import { cn } from "@/lib/utils";
import { ChatMessage as ChatMessageType } from "@/types/chat.types";

interface ChatMessageProps {
  message: ChatMessageType;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === "user";

  return (
    <div
      className={cn(
        "flex w-full",
        isUser ? "justify-end" : "justify-start"
      )}
    >
      <div
        className={cn(
          "max-w-[75%] rounded-2xl px-4 py-2.5 text-sm",
          isUser
            ? "bg-primary text-primary-foreground rounded-br-sm"
            : "bg-muted text-foreground rounded-bl-sm"
        )}
      >
        <p className="whitespace-pre-wrap leading-relaxed">{message.content}</p>
        <p className={cn(
          "text-xs mt-1 opacity-60",
          isUser ? "text-right" : "text-left"
        )}>
          {new Date(message.created_at).toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
          })}
        </p>
      </div>
    </div>
  );
}