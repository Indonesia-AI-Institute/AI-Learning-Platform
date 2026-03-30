"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useParams, useRouter } from "next/navigation";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { useCurrentUser } from "@/hooks/useCurrentUser";
import { taskService } from "@/services/task.service";
import { chatService } from "@/services/chat.service";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  ArrowLeft,
  MessageSquare,
  Plus,
  RotateCcw,
  Calendar,
  Users,
} from "lucide-react";

export default function TaskDetailPage() {
  const { taskId } = useParams<{ taskId: string }>();
  const router = useRouter();
  const queryClient = useQueryClient();
  const { user } = useCurrentUser();
  const isTeacher = user?.role === "teacher";

  const [newSessionTitle, setNewSessionTitle] = useState("");
  const [showTitleInput, setShowTitleInput] = useState(false);

  const { data: task, isLoading: loadingTask } = useQuery({
    queryKey: ["task", taskId],
    queryFn: () => taskService.getTaskDetail(taskId),
  });

  const { data: sessions, isLoading: loadingSessions } = useQuery({
    queryKey: ["sessionsByTask", taskId],
    queryFn: () => chatService.getSessionsByTask(taskId),
    enabled: !isTeacher,
  });

  const createSessionMutation = useMutation({
    mutationFn: () =>
      chatService.createSession(taskId, {
        title: newSessionTitle.trim() || undefined,
      }),
    onSuccess: (session) => {
      queryClient.invalidateQueries({ queryKey: ["sessionsByTask", taskId] });
      router.push(`/chat/${session.id}`);
    },
  });

  const resumeSessionMutation = useMutation({
    mutationFn: (sessionId: string) => chatService.resumeSession(sessionId),
    onSuccess: (session) => {
      queryClient.invalidateQueries({ queryKey: ["sessionsByTask", taskId] });
      router.push(`/chat/${session.id}`);
    },
  });

  const handleStartChat = () => {
    if (showTitleInput) {
      createSessionMutation.mutate();
      setShowTitleInput(false);
    } else {
      setShowTitleInput(true);
    }
  };

  const activeSessions = sessions?.filter((s) => s.is_active) ?? [];
  const endedSessions = sessions?.filter((s) => !s.is_active) ?? [];

  return (
    <DashboardLayout title={task?.title ?? "Task Detail"}>
      <div className="max-w-2xl space-y-6">

        <Button
          variant="ghost"
          size="sm"
          onClick={() => router.back()}
          className="text-muted-foreground -ml-2"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back
        </Button>

        {loadingTask ? (
          <p className="text-muted-foreground text-sm">Loading...</p>
        ) : (
          <>
            {/* Task info */}
            <div className="space-y-2">
              <h2 className="text-2xl font-semibold">{task?.title}</h2>

              {/* Class info badge */}
              {task?.class_info && (
                <div
                  className="inline-flex items-center gap-1.5 text-xs text-muted-foreground bg-muted px-2.5 py-1 rounded-full cursor-pointer hover:bg-muted/80"
                  onClick={() => router.push(`/classes/${task.class_info!.id}`)}
                >
                  <Users className="w-3 h-3" />
                  {task.class_info.name}
                </div>
              )}

              {task?.description && (
                <p className="text-muted-foreground text-sm">{task.description}</p>
              )}
              {task?.due_date && (
                <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
                  <Calendar className="w-3.5 h-3.5" />
                  Due {new Date(task.due_date).toLocaleDateString()}
                </div>
              )}
            </div>

            {/* STUDENT VIEW */}
            {!isTeacher && (
              <div className="space-y-4">

                {activeSessions.length > 0 && (
                  <div className="rounded-lg border border-yellow-200 bg-yellow-50 p-3">
                    <p className="text-sm text-yellow-800 font-medium">
                      You have an active session
                    </p>
                    <p className="text-xs text-yellow-700 mt-0.5">
                      Continue your ongoing session below.
                    </p>
                  </div>
                )}

                <div className="border rounded-lg p-4 space-y-3">
                  <p className="text-sm font-medium">Start a new session</p>

                  {showTitleInput && (
                    <div className="space-y-2">
                      <Label htmlFor="session-title">Session title (optional)</Label>
                      <Input
                        id="session-title"
                        placeholder="e.g. My first attempt"
                        value={newSessionTitle}
                        onChange={(e) => setNewSessionTitle(e.target.value)}
                        onKeyDown={(e) => e.key === "Enter" && handleStartChat()}
                      />
                    </div>
                  )}

                  <div className="flex gap-2">
                    <Button
                      onClick={handleStartChat}
                      disabled={createSessionMutation.isPending}
                      size="sm"
                    >
                      <Plus className="w-4 h-4 mr-2" />
                      {showTitleInput
                        ? createSessionMutation.isPending ? "Starting..." : "Start session"
                        : "New session"}
                    </Button>
                    {showTitleInput && (
                      <Button variant="ghost" size="sm" onClick={() => setShowTitleInput(false)}>
                        Cancel
                      </Button>
                    )}
                  </div>
                </div>

                {loadingSessions ? (
                  <p className="text-muted-foreground text-sm">Loading sessions...</p>
                ) : sessions && sessions.length > 0 ? (
                  <div className="space-y-3">
                    <p className="text-sm font-medium">Your sessions</p>

                    {activeSessions.map((session) => (
                      <div
                        key={session.id}
                        className="flex items-center justify-between border rounded-lg p-3 bg-green-50 border-green-200"
                      >
                        <div>
                          <p className="text-sm font-medium">
                            {session.title ?? "Untitled session"}
                          </p>
                          <p className="text-xs text-muted-foreground mt-0.5">
                            Started {new Date(session.created_at).toLocaleDateString()}
                          </p>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="text-xs px-2 py-0.5 rounded-full bg-green-100 text-green-700">
                            Active
                          </span>
                          <Button size="sm" onClick={() => router.push(`/chat/${session.id}`)}>
                            <MessageSquare className="w-4 h-4 mr-2" />
                            Continue
                          </Button>
                        </div>
                      </div>
                    ))}

                    {endedSessions.map((session) => (
                      <div
                        key={session.id}
                        className="flex items-center justify-between border rounded-lg p-3"
                      >
                        <div>
                          <p className="text-sm font-medium">
                            {session.title ?? "Untitled session"}
                          </p>
                          <p className="text-xs text-muted-foreground mt-0.5">
                            Ended{" "}
                            {session.ended_at
                              ? new Date(session.ended_at).toLocaleDateString()
                              : "—"}
                          </p>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="text-xs px-2 py-0.5 rounded-full bg-gray-100 text-gray-500">
                            Ended
                          </span>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => resumeSessionMutation.mutate(session.id)}
                            disabled={resumeSessionMutation.isPending}
                          >
                            <RotateCcw className="w-4 h-4 mr-2" />
                            Resume
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : null}
              </div>
            )}

            {/* TEACHER VIEW */}
            {isTeacher && (
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => router.push(`/tasks/${taskId}/edit`)}
                >
                  Edit task
                </Button>
              </div>
            )}
          </>
        )}
      </div>
    </DashboardLayout>
  );
}