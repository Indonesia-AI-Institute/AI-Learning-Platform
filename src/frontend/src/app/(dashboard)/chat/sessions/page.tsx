"use client";

/**
 * app/(dashboard)/chat/sessions/page.tsx
 * List all chat sessions for the student.
 */

import { useQuery } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { chatService } from "@/services/chat.service";
import { MessageSquare } from "lucide-react";
import { cn } from "@/lib/utils";

export default function ChatSessionsPage() {
  const router = useRouter();

  const { data: sessions, isLoading } = useQuery({
    queryKey: ["mySessions"],
    queryFn: () => chatService.getMySessions(),
  });

  const activeSessions = sessions?.filter((s) => s.is_active) ?? [];
  const endedSessions = sessions?.filter((s) => !s.is_active) ?? [];

  return (
    <DashboardLayout title="Chat History">
      <div className="space-y-6">

        <div>
          <h2 className="text-2xl font-semibold">Chat History</h2>
          <p className="text-muted-foreground text-sm mt-1">
            All your AI chat sessions
          </p>
        </div>

        {isLoading ? (
          <p className="text-muted-foreground text-sm">Loading...</p>
        ) : !sessions?.length ? (
          <div className="flex flex-col items-center justify-center py-16 text-center border rounded-lg">
            <MessageSquare className="w-10 h-10 text-muted-foreground mb-3" />
            <p className="font-medium">No sessions yet</p>
            <p className="text-sm text-muted-foreground mt-1">
              Start a chat from a task page
            </p>
          </div>
        ) : (
          <div className="space-y-6">

            {/* Active sessions */}
            {activeSessions.length > 0 && (
              <div className="space-y-2">
                <p className="text-sm font-medium text-muted-foreground uppercase tracking-wide">
                  Active
                </p>
                {activeSessions.map((session) => (
                  <div
                    key={session.id}
                    className="flex items-center justify-between border rounded-lg p-4 hover:bg-muted/50 cursor-pointer transition-colors border-green-200 bg-green-50/50"
                    onClick={() => router.push(`/chat/${session.id}`)}
                  >
                    <div className="space-y-0.5">
                      <div className="flex items-center gap-2">
                        <span className="w-2 h-2 rounded-full bg-green-500 shrink-0" />
                        <p className="font-medium text-sm">
                          {session.title ?? "Untitled session"}
                        </p>
                      </div>
                      <p className="text-xs text-muted-foreground pl-4">
                        Started {new Date(session.created_at).toLocaleDateString()}
                      </p>
                    </div>
                    <span className="text-xs px-2 py-0.5 rounded-full bg-green-100 text-green-700">
                      Active
                    </span>
                  </div>
                ))}
              </div>
            )}

            {/* Ended sessions */}
            {endedSessions.length > 0 && (
              <div className="space-y-2">
                <p className="text-sm font-medium text-muted-foreground uppercase tracking-wide">
                  Ended
                </p>
                {endedSessions.map((session) => (
                  <div
                    key={session.id}
                    className="flex items-center justify-between border rounded-lg p-4 hover:bg-muted/50 cursor-pointer transition-colors"
                    onClick={() => router.push(`/tasks/${session.task_id}`)}
                  >
                    <div className="space-y-0.5">
                      <p className="font-medium text-sm">
                        {session.title ?? "Untitled session"}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        Ended{" "}
                        {session.ended_at
                          ? new Date(session.ended_at).toLocaleDateString()
                          : "—"}
                      </p>
                    </div>
                    <span className="text-xs px-2 py-0.5 rounded-full bg-gray-100 text-gray-500">
                      Ended
                    </span>
                  </div>
                ))}
              </div>
            )}

          </div>
        )}
      </div>
    </DashboardLayout>
  );
}