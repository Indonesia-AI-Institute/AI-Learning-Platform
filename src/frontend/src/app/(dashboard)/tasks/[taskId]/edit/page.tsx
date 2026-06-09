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
import { ArrowLeft } from "lucide-react";

export default function EditTaskPage() {
  const { taskId } = useParams<{ taskId: string }>();
  const router = useRouter();
  const queryClient = useQueryClient();

  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [classId, setClassId] = useState("");
  const [dueDate, setDueDate] = useState("");
  const [isActive, setIsActive] = useState(true);

  const { data: task, isLoading: loadingTask } = useQuery({
    queryKey: ["task", taskId],
    queryFn: () => taskService.getTaskDetail(taskId),
  });

  const { data: classes } = useQuery({
    queryKey: ["myClasses"],
    queryFn: () => classService.getMyClasses(),
  });

  useEffect(() => {
    if (task) {
      setTitle(task.title);
      setDescription(task.description || "");
      setClassId(task.class_id || "");
      setDueDate(task.due_date ? task.due_date.split("T")[0] : "");
      setIsActive(task.is_active);
    }
  }, [task]);

  const updateMutation = useMutation({
    mutationFn: () =>
      taskService.updateTask(taskId, {
        title,
        description,
        class_id: classId,
        due_date: dueDate ? new Date(dueDate).toISOString() : null,
        is_active: isActive,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["task", taskId] });
      router.push(`/tasks/${taskId}`);
    },
  });

  if (loadingTask) {
    return (
      <DashboardLayout title="Edit Task">
        <p className="text-muted-foreground">Loading...</p>
      </DashboardLayout>
    );
  }

  if (!task) {
    return (
      <DashboardLayout title="Edit Task">
        <div className="space-y-4">
          <p className="text-muted-foreground">Task not found</p>
          <Button onClick={() => router.push("/tasks")}>Back to tasks</Button>
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
          className="text-muted-foreground"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back
        </Button>

        <form
          onSubmit={(e) => {
            e.preventDefault();
            updateMutation.mutate();
          }}
          className="space-y-4 border rounded-lg p-6"
        >
          <div className="space-y-2">
            <Label htmlFor="title">Task Title *</Label>
            <Input
              id="title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="description">Description</Label>
            <textarea
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Describe the task..."
              className="w-full border rounded-md p-2 text-sm"
              rows={5}
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="class">Class</Label>
              <Select value={classId} onValueChange={setClassId}>
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
            </div>

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

          <div className="space-y-2">
            <Label htmlFor="status">Status</Label>
            <Select value={isActive ? "active" : "inactive"} onValueChange={(val) => setIsActive(val === "active")}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="active">Active</SelectItem>
                <SelectItem value="inactive">Inactive</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="flex gap-2 pt-4">
            <Button
              type="submit"
              disabled={updateMutation.isPending}
            >
              {updateMutation.isPending ? "Saving..." : "Save changes"}
            </Button>
            <Button
              type="button"
              variant="outline"
              onClick={() => router.back()}
            >
              Cancel
            </Button>
          </div>
        </form>

      </div>
    </DashboardLayout>
  );
}