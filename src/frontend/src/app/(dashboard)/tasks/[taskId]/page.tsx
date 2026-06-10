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
  ArrowLeft,
  Plus,
  Calendar,
  Users,
  Trash2,
  ChevronRight,
  MessageSquare,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { ChatSession } from "@/types/chat.types";

// ─────────────────────────────────────────────────────────────
// SESSION CARD
// Clickable card tanpa status badge dan tombol resume.
// Delete tersembunyi, muncul saat hover.
// ─────────────────────────────────────────────────────────────

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
    day: "numeric",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
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
      {/* Icon */}
      <div className="shrink-0 w-9 h-9 rounded-full bg-muted flex items-center justify-center">
        <MessageSquare className="w-4 h-4 text-muted-foreground" />
      </div>

      {/* Info */}
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium truncate">
          {session.title ?? "Untitled session"}
        </p>
        <p className="text-xs text-muted-foreground mt-0.5">{formatted}</p>
      </div>

      {/* Right controls */}
      {!confirmDelete ? (
        <div className="flex items-center gap-1.5 shrink-0">
          <button
            onClick={(e) => {
              e.stopPropagation();
              setConfirmDelete(true);
            }}
            className="opacity-0 group-hover:opacity-100 transition-opacity p-1.5 rounded hover:bg-destructive/10 text-muted-foreground hover:text-destructive"
            title="Delete session"
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>
          <ChevronRight className="w-4 h-4 text-muted-foreground" />
        </div>
      ) : (
        // Inline confirm delete
        <div
          className="flex items-center gap-1.5 shrink-0"
          onClick={(e) => e.stopPropagation()}
        >
          <span className="text-xs text-muted-foreground">Delete?</span>
          <button
            disabled={isDeleting}
            onClick={(e) => {
              e.stopPropagation();
              onDelete(session.id);
            }}
            className="text-xs px-2.5 py-1 rounded bg-destructive text-white hover:bg-destructive/90 disabled:opacity-50"
          >
            {isDeleting ? "..." : "Yes"}
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation();
              setConfirmDelete(false);
            }}
            className="text-xs px-2.5 py-1 rounded border hover:bg-muted"
          >
            No
          </button>
        </div>
      )}
    </div>
  );
}

// ─────────────────────────────────────────────────────────────
// MAIN PAGE
// ─────────────────────────────────────────────────────────────

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
    // Selalu refetch saat student kembali ke halaman ini — tidak butuh refresh manual
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
      // Langsung navigasi ke chat room — chat room yang handle active state
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

  const handleDelete = (sessionId: string) => {
    setDeletingId(sessionId);
    deleteSessionMutation.mutate(sessionId);
  };

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
            {/* Task info */}
            <div className="space-y-3">
              <h2 className="text-2xl font-semibold">{task?.title}</h2>

              <div className="flex flex-wrap gap-2">
                {task?.class_info && (
                  <button
                    onClick={() =>
                      router.push(`/classes/${task.class_info!.id}`)
                    }
                    className="inline-flex items-center gap-1.5 text-xs text-muted-foreground bg-muted px-2.5 py-1 rounded-full hover:bg-muted/80 transition-colors"
                  >
                    <Users className="w-3 h-3" />
                    {task.class_info.name}
                  </button>
                )}
                {task?.due_date && (
                  <div className="inline-flex items-center gap-1.5 text-xs text-muted-foreground bg-muted px-2.5 py-1 rounded-full">
                    <Calendar className="w-3 h-3" />
                    Due{" "}
                    {new Date(task.due_date).toLocaleDateString("id-ID", {
                      day: "numeric",
                      month: "short",
                      year: "numeric",
                    })}
                  </div>
                )}
              </div>

              {task?.description && (
                <p className="text-muted-foreground text-sm leading-relaxed">
                  {task.description}
                </p>
              )}
            </div>

            {/* ── STUDENT VIEW ── */}
            {!isTeacher && (
              <div className="space-y-4">

                {/* New session box */}
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
                          ) : (
                            "Start session"
                          )}
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => {
                            setShowTitleInput(false);
                            setNewSessionTitle("");
                          }}
                        >
                          Cancel
                        </Button>
                      </div>
                    </>
                  ) : (
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium">
                          Start a new session
                        </p>
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

                {/* Sessions list */}
                {loadingSessions ? (
                  <div className="flex items-center gap-2 py-4">
                    <div className="w-4 h-4 border-2 border-primary border-t-transparent rounded-full animate-spin" />
                    <p className="text-sm text-muted-foreground">
                      Loading sessions...
                    </p>
                  </div>
                ) : sessions && sessions.length > 0 ? (
                  <div className="space-y-2">
                    <p className="text-xs text-muted-foreground font-medium uppercase tracking-wide">
                      Sessions ({sessions.length})
                    </p>
                    {/* Sort: terbaru di atas */}
                    {[...sessions]
                      .sort(
                        (a, b) =>
                          new Date(b.created_at).getTime() -
                          new Date(a.created_at).getTime()
                      )
                      .map((session) => (
                        <SessionCard
                          key={session.id}
                          session={session}
                          onOpen={(id) => router.push(`/chat/${id}`)}
                          onDelete={handleDelete}
                          isDeleting={deletingId === session.id}
                        />
                      ))}
                  </div>
                ) : (
                  <div className="border-dashed border-2 rounded-lg p-8 text-center">
                    <MessageSquare className="w-8 h-8 text-muted-foreground mx-auto mb-2" />
                    <p className="text-sm text-muted-foreground">
                      No sessions yet — start one above.
                    </p>
                  </div>
                )}
              </div>
            )}

            {/* ── TEACHER VIEW ── */}
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