"use client";

import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { ArrowLeft, StopCircle } from "lucide-react";
import { ChatSession } from "@/types/chat.types";
import { cn } from "@/lib/utils";

interface ChatHeaderProps {
  session: ChatSession;
  onEndSession: () => void;
  isEnding: boolean;
}

export function ChatHeader({ session, onEndSession, isEnding }: ChatHeaderProps) {
  const router = useRouter();

  return (
    <div className="flex items-center justify-between px-4 py-3 border-b bg-background">
      <div className="flex items-center gap-3">
        <Button
          variant="ghost"
          size="icon"
          onClick={() => router.back()}
          className="shrink-0"
        >
          <ArrowLeft className="w-4 h-4" />
        </Button>
        <div>
          <p className="font-medium text-sm">
            {session.title ?? "Untitled session"}
          </p>
          <div className="flex items-center gap-1.5">
            <span className={cn(
              "w-1.5 h-1.5 rounded-full",
              session.is_active ? "bg-green-500" : "bg-gray-400"
            )} />
            <span className="text-xs text-muted-foreground">
              {session.is_active ? "Active" : "Ended"}
            </span>
          </div>
        </div>
      </div>

      {session.is_active && (
        <Button
          size="sm"
          variant="outline"
          onClick={onEndSession}
          disabled={isEnding}
          className="text-destructive border-destructive/30 hover:bg-destructive/5"
        >
          <StopCircle className="w-4 h-4 mr-2" />
          {isEnding ? "Ending..." : "End session"}
        </Button>
      )}
    </div>
  );
}