"use client";

/**
 * ChatInput.tsx
 * =============
 * Message input area with send button.
 */

import { useState, KeyboardEvent } from "react";
import { Button } from "@/components/ui/button";
import { Send, Square } from "lucide-react";
import { cn } from "@/lib/utils";

interface ChatInputProps {
  onSend: (message: string) => void;
  onStop?: () => void;
  isStreaming: boolean;
  disabled?: boolean;
}

export function ChatInput({ onSend, onStop, isStreaming, disabled }: ChatInputProps) {
  const [value, setValue] = useState("");

  const handleSend = () => {
    if (!value.trim() || isStreaming) return;
    onSend(value.trim());
    setValue("");
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="border-t bg-background p-4">
      <div className="flex items-end gap-2 max-w-4xl mx-auto">
        <textarea
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type your message... (Enter to send, Shift+Enter for new line)"
          disabled={disabled || isStreaming}
          rows={1}
          className={cn(
            "flex-1 resize-none rounded-xl border bg-background px-4 py-3 text-sm",
            "focus:outline-none focus:ring-2 focus:ring-ring",
            "min-h-[48px] max-h-[160px] overflow-y-auto",
            "disabled:opacity-50 disabled:cursor-not-allowed"
          )}
          style={{
            height: "auto",
            overflowY: value.split("\n").length > 3 ? "auto" : "hidden",
          }}
          onInput={(e) => {
            const el = e.currentTarget;
            el.style.height = "auto";
            el.style.height = Math.min(el.scrollHeight, 160) + "px";
          }}
        />

        {isStreaming ? (
          <Button
            size="icon"
            variant="outline"
            onClick={onStop}
            className="rounded-xl h-12 w-12 shrink-0"
          >
            <Square className="w-4 h-4" />
          </Button>
        ) : (
          <Button
            size="icon"
            onClick={handleSend}
            disabled={!value.trim() || disabled}
            className="rounded-xl h-12 w-12 shrink-0"
          >
            <Send className="w-4 h-4" />
          </Button>
        )}
      </div>
      <p className="text-xs text-muted-foreground text-center mt-2">
        AI can make mistakes. Verify important information.
      </p>
    </div>
  );
}