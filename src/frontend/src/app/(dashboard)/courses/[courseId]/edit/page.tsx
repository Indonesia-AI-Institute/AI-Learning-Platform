"use client";

import { useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useParams, useRouter } from "next/navigation";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { courseService } from "@/services/course.service";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ArrowLeft, Trash2 } from "lucide-react";

export default function EditCoursePage() {
  const { courseId } = useParams<{ courseId: string }>();
  const router = useRouter();
  const queryClient = useQueryClient();

  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  const { data: course } = useQuery({
    queryKey: ["course", courseId],
    queryFn: () => courseService.getCourseDetail(courseId),
  });

  useEffect(() => {
    if (course) {
      setTitle(course.title);
      setDescription(course.description ?? "");
    }
  }, [course]);

  const updateMutation = useMutation({
    mutationFn: () =>
      courseService.updateCourse(courseId, {
        title,
        description: description || undefined,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["myCourses"] });
      queryClient.invalidateQueries({ queryKey: ["course", courseId] });
      router.push(`/courses/${courseId}`);
    },
    onError: (err: any) => {
      setError(err?.response?.data?.detail ?? "Failed to update course.");
    },
  });

  const deleteMutation = useMutation({
    mutationFn: () => courseService.deleteCourse(courseId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["myCourses"] });
      router.push("/courses");
    },
    onError: (err: any) => {
      setError(err?.response?.data?.detail ?? "Failed to delete course.");
    },
  });

  return (
    <DashboardLayout title="Edit Course">
      <div className="max-w-md space-y-6">

        <Button
          variant="ghost"
          size="sm"
          onClick={() => router.push(`/courses/${courseId}`)}
          className="text-muted-foreground -ml-2"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back
        </Button>

        <h2 className="text-2xl font-semibold">Edit course</h2>

        <div className="space-y-4 border rounded-lg p-5">
          <div className="space-y-2">
            <Label>Course title</Label>
            <Input
              value={title}
              onChange={(e) => setTitle(e.target.value)}
            />
          </div>

          <div className="space-y-2">
            <Label>Description (optional)</Label>
            <Input
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
          </div>

          {error && <p className="text-sm text-destructive">{error}</p>}

          <Button
            className="w-full"
            onClick={() => updateMutation.mutate()}
            disabled={updateMutation.isPending}
          >
            {updateMutation.isPending ? "Saving..." : "Save changes"}
          </Button>
        </div>

        {/* Delete section */}
        <div className="border border-destructive/30 rounded-lg p-5 space-y-3">
          <p className="text-sm font-medium text-destructive">Danger zone</p>
          {!showDeleteConfirm ? (
            <Button
              variant="outline"
              size="sm"
              className="text-destructive border-destructive/30 hover:bg-destructive/5"
              onClick={() => setShowDeleteConfirm(true)}
            >
              <Trash2 className="w-4 h-4 mr-2" />
              Delete course
            </Button>
          ) : (
            <div className="space-y-2">
              <p className="text-sm text-muted-foreground">
                Are you sure? This action cannot be undone.
              </p>
              <div className="flex gap-2">
                <Button
                  size="sm"
                  variant="destructive"
                  onClick={() => deleteMutation.mutate()}
                  disabled={deleteMutation.isPending}
                >
                  {deleteMutation.isPending ? "Deleting..." : "Yes, delete"}
                </Button>
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => setShowDeleteConfirm(false)}
                >
                  Cancel
                </Button>
              </div>
            </div>
          )}
        </div>

      </div>
    </DashboardLayout>
  );
}