"use client";

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useRouter, useSearchParams } from "next/navigation";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { classService } from "@/services/class.service";
import { courseService } from "@/services/course.service";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ArrowLeft } from "lucide-react";

export default function CreateClassPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const queryClient = useQueryClient();

  // Pre-fill course_id if passed via query param
  const prefilledCourseId = searchParams.get("course_id") ?? "";

  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [courseId, setCourseId] = useState(prefilledCourseId);
  const [error, setError] = useState<string | null>(null);

  const { data: courses } = useQuery({
    queryKey: ["myCourses"],
    queryFn: () => courseService.getMyCourses(),
  });

  const createMutation = useMutation({
    mutationFn: () =>
      classService.createClass({
        name,
        description: description || undefined,
        course_id: courseId,
      }),
    onSuccess: (cls) => {
      queryClient.invalidateQueries({ queryKey: ["myClasses"] });
      queryClient.invalidateQueries({ queryKey: ["classesByCourse", courseId] });
      router.push(`/classes/${cls.id}`);
    },
    onError: (err: any) => {
      setError(err?.response?.data?.detail ?? "Failed to create class.");
    },
  });

  const handleSubmit = () => {
    if (!name.trim()) { setError("Class name is required."); return; }
    if (!courseId) { setError("Please select a course."); return; }
    setError(null);
    createMutation.mutate();
  };

  return (
    <DashboardLayout title="Create Class">
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
          <h2 className="text-2xl font-semibold">Create a class</h2>
          <p className="text-muted-foreground text-sm mt-1">
            Set up a new class for your students.
          </p>
        </div>

        <div className="space-y-4 border rounded-lg p-5">

          <div className="space-y-2">
            <Label htmlFor="course">Course</Label>
            <select
              id="course"
              value={courseId}
              onChange={(e) => setCourseId(e.target.value)}
              className="w-full border rounded-md px-3 py-2 text-sm bg-background"
            >
              <option value="">Select a course</option>
              {courses?.map((c) => (
                <option key={c.id} value={c.id}>{c.title}</option>
              ))}
            </select>
            {!courses?.length && (
              <p className="text-xs text-muted-foreground">
                No courses yet.{" "}
                <span
                  className="text-primary cursor-pointer hover:underline"
                  onClick={() => router.push("/courses/create")}
                >
                  Create a course first.
                </span>
              </p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="name">Class name</Label>
            <Input
              id="name"
              placeholder="e.g. AI Fundamentals — Batch 1"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="description">Description (optional)</Label>
            <Input
              id="description"
              placeholder="Brief description"
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
            {createMutation.isPending ? "Creating..." : "Create class"}
          </Button>
        </div>

      </div>
    </DashboardLayout>
  );
}