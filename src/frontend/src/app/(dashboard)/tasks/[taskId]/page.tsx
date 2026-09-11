"use client";

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useParams, useRouter } from "next/navigation";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { useCurrentUser } from "@/hooks/useCurrentUser";
import { taskService } from "@/services/task.service";
import { chatService } from "@/services/chat.service";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  ArrowLeft, Plus, Calendar, Users, Trash2,
  ChevronRight, MessageSquare, Lock,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { ChatSession } from "@/types/chat.types";

function SessionCard({
  session,
  onOpen,
  onDelete,
  isDeleting,
}: {
  session: ChatSession;
  onOpen: (id: string) => void;
  onDelete: (id: string) => void;
  isDeleting: boolean;
}) {
  const [confirmDelete, setConfirmDelete] = useState(false);

  const formatted = new Date(session.created_at).toLocaleDateString("id-ID", {
    day: "numeric", month: "short", year: "numeric",
    hour: "2-digit", minute: "2-digit",
  });

  return (
    <div
      onClick={() => !confirmDelete && onOpen(session.id)}
      className={cn(
        "group relative flex items-center gap-3 border rounded-lg px-4 py-3 transition-all duration-150",
        confirmDelete
          ? "border-destructive/30 bg-destructive/5"
          : "cursor-pointer hover:bg-muted/50 hover:border-primary/30 active:scale-[0.99]"
      )}
    >
      <div className="shrink-0 w-9 h-9 rounded-full bg-muted flex items-center justify-center">
        <MessageSquare className="w-4 h-4 text-muted-foreground" />
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium truncate">
          {session.title ?? "Untitled session"}
        </p>
        <p className="text-xs text-muted-foreground mt-0.5">{formatted}</p>
      </div>
      {!confirmDelete ? (
        <div className="flex items-center gap-1.5 shrink-0">
          <button
            onClick={(e) => { e.stopPropagation(); setConfirmDelete(true); }}
            className="opacity-0 group-hover:opacity-100 transition-opacity p-1.5 rounded hover:bg-destructive/10 text-muted-foreground hover:text-destructive"
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>
          <ChevronRight className="w-4 h-4 text-muted-foreground" />
        </div>
      ) : (
        <div className="flex items-center gap-1.5 shrink-0" onClick={(e) => e.stopPropagation()}>
          <span className="text-xs text-muted-foreground">Delete?</span>
          <button
            disabled={isDeleting}
            onClick={(e) => { e.stopPropagation(); onDelete(session.id); }}
            className="text-xs px-2.5 py-1 rounded bg-destructive text-white hover:bg-destructive/90 disabled:opacity-50"
          >
            {isDeleting ? "..." : "Yes"}
          </button>
          <button
            onClick={(e) => { e.stopPropagation(); setConfirmDelete(false); }}
            className="text-xs px-2.5 py-1 rounded border hover:bg-muted"
          >
            No
          </button>
        </div>
      )}
    </div>
  );
}

export default function TaskDetailPage() {
  const { taskId } = useParams<{ taskId: string }>();
  const router = useRouter();
  const queryClient = useQueryClient();
  const { user } = useCurrentUser();
  const isTeacher = user?.role === "teacher";

  const [newSessionTitle, setNewSessionTitle] = useState("");
  const [showTitleInput, setShowTitleInput] = useState(false);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const { data: task, isLoading: loadingTask } = useQuery({
    queryKey: ["task", taskId],
    queryFn: () => taskService.getTaskDetail(taskId),
  });

  const { data: sessions, isLoading: loadingSessions } = useQuery({
    queryKey: ["sessionsByTask", taskId],
    queryFn: () => chatService.getSessionsByTask(taskId),
    enabled: !isTeacher,
    refetchOnWindowFocus: true,
    staleTime: 0,
  });

  const createSessionMutation = useMutation({
    mutationFn: () =>
      chatService.createSession(taskId, {
        title: newSessionTitle.trim() || undefined,
      }),
    onSuccess: (session) => {
      queryClient.invalidateQueries({ queryKey: ["sessionsByTask", taskId] });
      setShowTitleInput(false);
      setNewSessionTitle("");
      router.push(`/chat/${session.id}`);
    },
  });

  const deleteSessionMutation = useMutation({
    mutationFn: (sessionId: string) => chatService.deleteSession(sessionId),
    onSuccess: () => {
      setDeletingId(null);
      queryClient.invalidateQueries({ queryKey: ["sessionsByTask", taskId] });
    },
    onError: () => setDeletingId(null),
  });

  // A task can go inactive either manually or automatically past its due date
  const isTaskActive = task?.is_active ?? true;

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
          <div className="flex items-center gap-2 py-8">
            <div className="w-5 h-5 border-2 border-primary border-t-transparent rounded-full animate-spin" />
            <p className="text-muted-foreground text-sm">Loading...</p>
          </div>
        ) : (
          <>
            <div className="space-y-3">
              <div className="flex items-start gap-3 flex-wrap">
                <h2 className="text-2xl font-semibold">{task?.title}</h2>
                {!isTaskActive && (
                  <span className="mt-1 text-xs px-2 py-0.5 rounded-full bg-gray-100 text-gray-500 shrink-0">
                    Closed
                  </span>
                )}
              </div>

              <div className="flex flex-wrap gap-2">
                {task?.class_info && (
                  <button
                    onClick={() => router.push(`/classes/${task.class_info!.id}`)}
                    className="inline-flex items-center gap-1.5 text-xs text-muted-foreground bg-muted px-2.5 py-1 rounded-full hover:bg-muted/80 transition-colors"
                  >
                    <Users className="w-3 h-3" />
                    {task.class_info.name}
                  </button>
                )}
                {task?.due_date && (
                  <div className={cn(
                    "inline-flex items-center gap-1.5 text-xs px-2.5 py-1 rounded-full",
                    !isTaskActive && new Date(task.due_date) < new Date()
                      ? "bg-red-50 text-red-600"
                      : "bg-muted text-muted-foreground"
                  )}>
                    <Calendar className="w-3 h-3" />
                    {!isTaskActive && new Date(task.due_date) < new Date()
                      ? `Past due: ${new Date(task.due_date).toLocaleDateString("id-ID", { day: "numeric", month: "short", year: "numeric" })}`
                      : `Due ${new Date(task.due_date).toLocaleDateString("id-ID", { day: "numeric", month: "short", year: "numeric" })}`
                    }
                  </div>
                )}
              </div>

              {task?.description && (
                <p className="text-muted-foreground text-sm leading-relaxed">
                  {task.description}
                </p>
              )}
            </div>

            {!isTeacher && (
              <div className="space-y-4">

                {!isTaskActive ? (
                  <div className="flex items-start gap-3 border border-gray-200 bg-gray-50 rounded-lg p-4">
                    <Lock className="w-4 h-4 text-gray-400 shrink-0 mt-0.5" />
                    <div>
                      <p className="text-sm font-medium text-gray-700">
                        This task is no longer accepting submissions
                      </p>
                      <p className="text-xs text-gray-500 mt-0.5">
                        You can still view your previous sessions below.
                      </p>
                    </div>
                  </div>
                ) : (
                  <div className="border rounded-lg p-4 space-y-3">
                    {showTitleInput ? (
                      <>
                        <p className="text-sm font-medium">Name your session</p>
                        <Input
                          placeholder="e.g. My first attempt (optional)"
                          value={newSessionTitle}
                          onChange={(e) => setNewSessionTitle(e.target.value)}
                          onKeyDown={(e) => {
                            if (e.key === "Enter") createSessionMutation.mutate();
                            if (e.key === "Escape") {
                              setShowTitleInput(false);
                              setNewSessionTitle("");
                            }
                          }}
                          autoFocus
                        />
                        <div className="flex gap-2">
                          <Button
                            onClick={() => createSessionMutation.mutate()}
                            disabled={createSessionMutation.isPending}
                            size="sm"
                          >
                            {createSessionMutation.isPending ? (
                              <span className="flex items-center gap-2">
                                <span className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                                Starting...
                              </span>
                            ) : "Start session"}
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => { setShowTitleInput(false); setNewSessionTitle(""); }}
                          >
                            Cancel
                          </Button>
                        </div>
                      </>
                    ) : (
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-sm font-medium">Start a new session</p>
                          <p className="text-xs text-muted-foreground mt-0.5">
                            Each session keeps its own conversation history
                          </p>
                        </div>
                        <Button
                          size="sm"
                          onClick={() => setShowTitleInput(true)}
                          disabled={createSessionMutation.isPending}
                        >
                          <Plus className="w-4 h-4 mr-1.5" />
                          New session
                        </Button>
                      </div>
                    )}
                  </div>
                )}

                {loadingSessions ? (
                  <div className="flex items-center gap-2 py-4">
                    <div className="w-4 h-4 border-2 border-primary border-t-transparent rounded-full animate-spin" />
                    <p className="text-sm text-muted-foreground">Loading sessions...</p>
                  </div>
                ) : sessions && sessions.length > 0 ? (
                  <div className="space-y-2">
                    <p className="text-xs text-muted-foreground font-medium uppercase tracking-wide">
                      Sessions ({sessions.length})
                    </p>
                    {[...sessions]
                      .sort((a, b) =>
                        new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
                      )
                      .map((session) => (
                        <SessionCard
                          key={session.id}
                          session={session}
                          onOpen={(id) => router.push(`/chat/${id}`)}
                          onDelete={(id) => {
                            setDeletingId(id);
                            deleteSessionMutation.mutate(id);
                          }}
                          isDeleting={deletingId === session.id}
                        />
                      ))}
                  </div>
                ) : null}
              </div>
            )}

            {isTeacher && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => router.push(`/tasks/${taskId}/edit`)}
              >
                Edit task
              </Button>
            )}
          </>
        )}
      </div>
    </DashboardLayout>
  );
}