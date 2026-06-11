"use client";

/**
 * Teacher creates a new task for a course
 */

import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useRouter, useSearchParams } from "next/navigation";

import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { taskService } from "@/services/task.service";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

import { ArrowLeft } from "lucide-react";

export default function CreateTaskContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const queryClient = useQueryClient();

  // course_id passed via query param from class detail page
  const courseId = searchParams.get("course_id") ?? "";

  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [dueDate, setDueDate] = useState("");
  const [error, setError] = useState<string | null>(null);

  const createMutation = useMutation({
    mutationFn: () =>
      taskService.createTask(courseId, {
        title,
        description: description || undefined,
        due_date: dueDate || undefined,
      }),

    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["tasksByClass"],
      });

      queryClient.invalidateQueries({
        queryKey: ["tasksByCourse"],
      });

      router.back();
    },

    onError: (err: any) => {
      setError(
        err?.response?.data?.detail ??
          "Failed to create task."
      );
    },
  });

  const handleSubmit = () => {
    if (!title.trim()) {
      setError("Task title is required.");
      return;
    }

    if (!courseId) {
      setError(
        "Course ID is missing. Go back and try again."
      );
      return;
    }

    setError(null);
    createMutation.mutate();
  };

  return (
    <DashboardLayout title="Create Task">
      <div className="max-w-md space-y-6">
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
          <h2 className="text-2xl font-semibold">
            Create a task
          </h2>

          <p className="text-muted-foreground text-sm mt-1">
            Students will use AI to work on this task.
          </p>
        </div>

        <div className="space-y-4 border rounded-lg p-5">
          <div className="space-y-2">
            <Label htmlFor="title">
              Task title
            </Label>

            <Input
              id="title"
              placeholder="e.g. Explain the concept of neural networks"
              value={title}
              onChange={(e) =>
                setTitle(e.target.value)
              }
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="description">
              Description (optional)
            </Label>

            <Input
              id="description"
              placeholder="Instructions or context for students"
              value={description}
              onChange={(e) =>
                setDescription(e.target.value)
              }
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="due-date">
              Due date (optional)
            </Label>

            <Input
              id="due-date"
              type="datetime-local"
              value={dueDate}
              onChange={(e) =>
                setDueDate(e.target.value)
              }
            />
          </div>

          {error && (
            <p className="text-sm text-destructive">
              {error}
            </p>
          )}

          <Button
            className="w-full"
            onClick={handleSubmit}
            disabled={createMutation.isPending}
          >
            {createMutation.isPending
              ? "Creating..."
              : "Create task"}
          </Button>
        </div>
      </div>
    </DashboardLayout>
  );
}