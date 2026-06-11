"use client";

import { useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useParams, useRouter } from "next/navigation";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { taskService } from "@/services/task.service";
import { classService } from "@/services/class.service";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { ArrowLeft, AlertCircle } from "lucide-react";

export default function EditTaskPage() {
  const { taskId } = useParams<{ taskId: string }>();
  const router = useRouter();
  const queryClient = useQueryClient();

  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [classId, setClassId] = useState("");
  const [dueDate, setDueDate] = useState("");
  const [isActive, setIsActive] = useState(true);
  const [formError, setFormError] = useState("");

  // Fetch task detail
  const { data: task, isLoading: loadingTask, isError: taskError } = useQuery({
    queryKey: ["task", taskId],
    queryFn: () => taskService.getTaskDetail(taskId),
  });

  // Fetch teacher's classes untuk dropdown
  const { data: classes, isLoading: loadingClasses } = useQuery({
    queryKey: ["myClasses"],
    queryFn: () => classService.getMyClasses(),
  });

  // Pre-fill form saat task data tersedia
  useEffect(() => {
    if (!task) return;

    setTitle(task.title ?? "");
    setDescription(task.description ?? "");

    // FIX: handle dua kemungkinan struktur — class_id langsung atau via class_info
    const resolvedClassId = task.class_id || task.class_info?.id || "";
    setClassId(resolvedClassId);

    // FIX: due_date dari ISO string → ambil hanya tanggal (YYYY-MM-DD)
    if (task.due_date) {
      setDueDate(task.due_date.substring(0, 10));
    } else {
      setDueDate("");
    }

    setIsActive(task.is_active ?? true);
  }, [task]);

  const updateMutation = useMutation({
    mutationFn: () => {
      if (!title.trim()) throw new Error("Title is required");

      return taskService.updateTask(taskId, {
        title: title.trim(),
        description: description.trim() || null,
        class_id: classId || undefined,
        // Kirim ISO string atau null — backend expect nullable datetime
        due_date: dueDate ? new Date(dueDate + "T00:00:00").toISOString() : null,
        is_active: isActive,
      });
    },
    onSuccess: (updatedTask) => {
      // Invalidate semua query yang mungkin cache task ini
      queryClient.invalidateQueries({ queryKey: ["task", taskId] });
      queryClient.invalidateQueries({ queryKey: ["myTasks"] });
      queryClient.invalidateQueries({ queryKey: ["tasksByClass"] });
      router.push(`/tasks/${taskId}`);
    },
    onError: (err: any) => {
      const msg =
        err?.response?.data?.detail ||
        err?.message ||
        "Failed to update task. Please try again.";
      setFormError(typeof msg === "string" ? msg : JSON.stringify(msg));
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setFormError("");

    if (!title.trim()) {
      setFormError("Title cannot be empty.");
      return;
    }

    updateMutation.mutate();
  };

  // ── Loading
  if (loadingTask) {
    return (
      <DashboardLayout title="Edit Task">
        <div className="flex items-center gap-2 py-8">
          <div className="w-5 h-5 border-2 border-primary border-t-transparent rounded-full animate-spin" />
          <p className="text-muted-foreground text-sm">Loading task...</p>
        </div>
      </DashboardLayout>
    );
  }

  // ── Task not found
  if (taskError || !task) {
    return (
      <DashboardLayout title="Edit Task">
        <div className="space-y-4 py-8">
          <div className="flex items-center gap-2 text-destructive">
            <AlertCircle className="w-5 h-5" />
            <p>Task not found.</p>
          </div>
          <Button variant="outline" onClick={() => router.push("/tasks")}>
            Back to tasks
          </Button>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout title={`Edit: ${task.title}`}>
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

        <div>
          <h2 className="text-2xl font-semibold">Edit Task</h2>
          <p className="text-sm text-muted-foreground mt-1">
            Update the task details below
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5 border rounded-lg p-6">

          {/* Title */}
          <div className="space-y-2">
            <Label htmlFor="title">
              Task Title <span className="text-destructive">*</span>
            </Label>
            <Input
              id="title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Enter task title"
              required
            />
          </div>

          {/* Description */}
          <div className="space-y-2">
            <Label htmlFor="description">Description</Label>
            <textarea
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Describe what students should do in this task..."
              className="w-full border rounded-md p-3 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-ring min-h-[120px]"
              rows={5}
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">

            {/* Class */}
            <div className="space-y-2">
              <Label>Class</Label>
              {loadingClasses ? (
                <div className="h-10 border rounded-md flex items-center px-3">
                  <p className="text-sm text-muted-foreground">Loading...</p>
                </div>
              ) : (
                <Select
                  value={classId}
                  onValueChange={setClassId}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select a class" />
                  </SelectTrigger>
                  <SelectContent>
                    {classes?.map((cls) => (
                      <SelectItem key={cls.id} value={cls.id}>
                        {cls.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              )}
            </div>

            {/* Due Date */}
            <div className="space-y-2">
              <Label htmlFor="due-date">Due Date</Label>
              <Input
                id="due-date"
                type="date"
                value={dueDate}
                onChange={(e) => setDueDate(e.target.value)}
              />
            </div>
          </div>

          {/* Status */}
          <div className="space-y-2">
            <Label>Status</Label>
            <Select
              value={isActive ? "active" : "inactive"}
              onValueChange={(val) => setIsActive(val === "active")}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="active">Active — visible to students</SelectItem>
                <SelectItem value="inactive">Inactive — hidden from students</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Error message */}
          {formError && (
            <div className="flex items-start gap-2 rounded-md border border-destructive/30 bg-destructive/5 px-3 py-2">
              <AlertCircle className="w-4 h-4 text-destructive shrink-0 mt-0.5" />
              <p className="text-sm text-destructive">{formError}</p>
            </div>
          )}

          {/* Actions */}
          <div className="flex gap-3 pt-2">
            <Button
              type="submit"
              disabled={updateMutation.isPending}
            >
              {updateMutation.isPending ? (
                <span className="flex items-center gap-2">
                  <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Saving...
                </span>
              ) : (
                "Save changes"
              )}
            </Button>
            <Button
              type="button"
              variant="outline"
              onClick={() => router.back()}
              disabled={updateMutation.isPending}
            >
              Cancel
            </Button>
          </div>

        </form>
      </div>
    </DashboardLayout>
  );
}