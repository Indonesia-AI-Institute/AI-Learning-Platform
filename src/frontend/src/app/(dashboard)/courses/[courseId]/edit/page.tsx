"use client";

import { useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useParams, useRouter } from "next/navigation";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { courseService } from "@/services/course.service";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { ArrowLeft, AlertCircle } from "lucide-react";

export default function EditCoursePage() {
  const { courseId } = useParams<{ courseId: string }>();
  const router = useRouter();
  const queryClient = useQueryClient();

  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [isActive, setIsActive] = useState(true);
  const [titleError, setTitleError] = useState("");
  const [formError, setFormError] = useState("");

  const { data: course, isLoading } = useQuery({
    queryKey: ["course", courseId],
    queryFn: () => courseService.getCourseDetail(courseId),
  });

  // Pre-fill form saat data tersedia
  useEffect(() => {
    if (!course) return;
    setTitle(course.title ?? "");
    setDescription(course.description ?? "");
    setIsActive(course.is_active ?? true);
  }, [course]);

  const updateMutation = useMutation({
    mutationFn: () =>
      courseService.updateCourse(courseId, {
        title: title.trim(),
        description: description.trim() || null,
        is_active: isActive,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["course", courseId] });
      queryClient.invalidateQueries({ queryKey: ["myCourses"] });
      router.push(`/courses/${courseId}`);
    },
    onError: (err: any) => {
      const detail = err?.response?.data?.detail;
      const msg = typeof detail === "string"
        ? detail
        : Array.isArray(detail)
        ? detail.map((d: any) => d.msg).join(", ")
        : "Failed to update course. Please try again.";
      setFormError(msg);
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setFormError("");
    setTitleError("");

    // Validasi title tidak boleh kosong
    if (!title.trim()) {
      setTitleError("Course title is required and cannot be empty.");
      return;
    }

    updateMutation.mutate();
  };

  if (isLoading) {
    return (
      <DashboardLayout title="Edit Course">
        <div className="flex items-center gap-2 py-8">
          <div className="w-5 h-5 border-2 border-primary border-t-transparent rounded-full animate-spin" />
          <p className="text-muted-foreground text-sm">Loading...</p>
        </div>
      </DashboardLayout>
    );
  }

  if (!course) {
    return (
      <DashboardLayout title="Edit Course">
        <p className="text-muted-foreground text-sm py-8">Course not found.</p>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout title={`Edit: ${course.title}`}>
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
          <h2 className="text-2xl font-semibold">Edit Course</h2>
          <p className="text-sm text-muted-foreground mt-1">
            Update course details and visibility
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5 border rounded-lg p-6">

          {/* Title */}
          <div className="space-y-2">
            <Label htmlFor="title">
              Course Title <span className="text-destructive">*</span>
            </Label>
            <Input
              id="title"
              value={title}
              onChange={(e) => {
                setTitle(e.target.value);
                // Clear error saat user mulai mengetik
                if (e.target.value.trim()) setTitleError("");
              }}
              placeholder="Enter course title"
              className={titleError ? "border-destructive focus-visible:ring-destructive" : ""}
            />
            {titleError && (
              <p className="text-xs text-destructive flex items-center gap-1">
                <AlertCircle className="w-3 h-3" />
                {titleError}
              </p>
            )}
          </div>

          {/* Description */}
          <div className="space-y-2">
            <Label htmlFor="description">Description</Label>
            <textarea
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Course description (optional)"
              className="w-full border rounded-md p-3 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-ring min-h-[100px]"
              rows={4}
            />
          </div>

          {/* Active / Inactive toggle */}
          <div className="flex items-center justify-between border rounded-lg p-4">
            <div className="space-y-0.5">
              <p className="text-sm font-medium">Course Status</p>
              <p className="text-xs text-muted-foreground">
                {isActive
                  ? "Active — visible to students"
                  : "Inactive — hidden from students"}
              </p>
            </div>
            <Switch
              checked={isActive}
              onCheckedChange={setIsActive}
            />
          </div>

          {/* Form-level error */}
          {formError && (
            <div className="flex items-start gap-2 rounded-md border border-destructive/30 bg-destructive/5 px-3 py-2">
              <AlertCircle className="w-4 h-4 text-destructive shrink-0 mt-0.5" />
              <p className="text-sm text-destructive">{formError}</p>
            </div>
          )}

          {/* Actions */}
          <div className="flex gap-3 pt-2">
            <Button type="submit" disabled={updateMutation.isPending}>
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