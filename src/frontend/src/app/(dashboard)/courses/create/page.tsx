"use client";

import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { courseService } from "@/services/course.service";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ArrowLeft } from "lucide-react";

export default function CreateCoursePage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [error, setError] = useState<string | null>(null);

  const createMutation = useMutation({
    mutationFn: () => courseService.createCourse({ title, description: description || undefined }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["myCourses"] });
      router.push("/courses");
    },
    onError: (err: any) => {
      setError(err?.response?.data?.detail ?? "Failed to create course.");
    },
  });

  const handleSubmit = () => {
    if (!title.trim()) { setError("Course title is required."); return; }
    setError(null);
    createMutation.mutate();
  };

  return (
    <DashboardLayout title="Create Course">
      <div className="max-w-md space-y-6">

        <Button
          variant="ghost"
          size="sm"
          onClick={() => router.push("/courses")}
          className="text-muted-foreground -ml-2"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to courses
        </Button>

        <div>
          <h2 className="text-2xl font-semibold">Create a course</h2>
          <p className="text-muted-foreground text-sm mt-1">
            A course contains tasks for your students.
          </p>
        </div>

        <div className="space-y-4 border rounded-lg p-5">
          <div className="space-y-2">
            <Label htmlFor="title">Course title</Label>
            <Input
              id="title"
              placeholder="e.g. Introduction to AI"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="description">Description (optional)</Label>
            <Input
              id="description"
              placeholder="What will students learn?"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
          </div>

          {error && <p className="text-sm text-destructive">{error}</p>}

          <Button
            className="w-full"
            onClick={handleSubmit}
            disabled={createMutation.isPending}
          >
            {createMutation.isPending ? "Creating..." : "Create course"}
          </Button>
        </div>

      </div>
    </DashboardLayout>
  );
}