"use client";

import { useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useParams, useRouter } from "next/navigation";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { classService } from "@/services/class.service";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { ArrowLeft, AlertCircle } from "lucide-react";

export default function EditClassPage() {
  const { classId } = useParams<{ classId: string }>();
  const router = useRouter();
  const queryClient = useQueryClient();

  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [isActive, setIsActive] = useState(true);
  const [nameError, setNameError] = useState("");
  const [formError, setFormError] = useState("");

  const { data: cls, isLoading } = useQuery({
    queryKey: ["class", classId],
    queryFn: () => classService.getClassDetail(classId),
  });

  // Pre-fill form
  useEffect(() => {
    if (!cls) return;
    setName(cls.name ?? "");
    setDescription(cls.description ?? "");
    setIsActive(cls.is_active ?? true);
  }, [cls]);

  const updateMutation = useMutation({
    mutationFn: () =>
      classService.updateClass(classId, {
        name: name.trim(),
        description: description.trim() || null,
        is_active: isActive,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["class", classId] });
      queryClient.invalidateQueries({ queryKey: ["myClasses"] });
      queryClient.invalidateQueries({ queryKey: ["classesByCourse"] });
      router.push(`/classes/${classId}`);
    },
    onError: (err: any) => {
      const detail = err?.response?.data?.detail;
      const msg = typeof detail === "string"
        ? detail
        : Array.isArray(detail)
        ? detail.map((d: any) => d.msg).join(", ")
        : "Failed to update class. Please try again.";
      setFormError(msg);
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setFormError("");
    setNameError("");

    if (!name.trim()) {
      setNameError("Class name is required and cannot be empty.");
      return;
    }

    updateMutation.mutate();
  };

  if (isLoading) {
    return (
      <DashboardLayout title="Edit Class">
        <div className="flex items-center gap-2 py-8">
          <div className="w-5 h-5 border-2 border-primary border-t-transparent rounded-full animate-spin" />
          <p className="text-muted-foreground text-sm">Loading...</p>
        </div>
      </DashboardLayout>
    );
  }

  if (!cls) {
    return (
      <DashboardLayout title="Edit Class">
        <p className="text-muted-foreground text-sm py-8">Class not found.</p>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout title={`Edit: ${cls.name}`}>
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
          <h2 className="text-2xl font-semibold">Edit Class</h2>
          <p className="text-sm text-muted-foreground mt-1">
            Update class details and visibility
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5 border rounded-lg p-6">

          {/* Name */}
          <div className="space-y-2">
            <Label htmlFor="name">
              Class Name <span className="text-destructive">*</span>
            </Label>
            <Input
              id="name"
              value={name}
              onChange={(e) => {
                setName(e.target.value);
                if (e.target.value.trim()) setNameError("");
              }}
              placeholder="Enter class name"
              className={nameError ? "border-destructive focus-visible:ring-destructive" : ""}
            />
            {nameError && (
              <p className="text-xs text-destructive flex items-center gap-1">
                <AlertCircle className="w-3 h-3" />
                {nameError}
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
              placeholder="Class description (optional)"
              className="w-full border rounded-md p-3 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-ring min-h-[100px]"
              rows={4}
            />
          </div>

          {/* Active / Inactive toggle */}
          <div className="flex items-center justify-between border rounded-lg p-4">
            <div className="space-y-0.5">
              <p className="text-sm font-medium">Class Status</p>
              <p className="text-xs text-muted-foreground">
                {isActive
                  ? "Active — students can enroll and access tasks"
                  : "Inactive — hidden from students, enrollment disabled"}
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