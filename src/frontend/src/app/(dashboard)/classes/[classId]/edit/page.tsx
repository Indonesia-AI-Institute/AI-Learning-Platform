"use client";

import { useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useParams, useRouter } from "next/navigation";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { classService } from "@/services/class.service";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ArrowLeft, Trash2 } from "lucide-react";

export default function EditClassPage() {
  const { classId } = useParams<{ classId: string }>();
  const router = useRouter();
  const queryClient = useQueryClient();

  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  const { data: cls } = useQuery({
    queryKey: ["class", classId],
    queryFn: () => classService.getClassDetail(classId),
  });

  useEffect(() => {
    if (cls) {
      setName(cls.name);
      setDescription(cls.description ?? "");
    }
  }, [cls]);

  const updateMutation = useMutation({
    mutationFn: () =>
      classService.updateClass(classId, {
        name,
        description: description || undefined,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["myClasses"] });
      queryClient.invalidateQueries({ queryKey: ["class", classId] });
      router.push(`/classes/${classId}`);
    },
    onError: (err: any) => {
      setError(err?.response?.data?.detail ?? "Failed to update class.");
    },
  });

  const deleteMutation = useMutation({
    mutationFn: () => classService.deleteClass(classId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["myClasses"] });
      router.push("/classes");
    },
    onError: (err: any) => {
      setError(err?.response?.data?.detail ?? "Failed to delete class.");
    },
  });

  return (
    <DashboardLayout title="Edit Class">
      <div className="max-w-md space-y-6">

        <Button
          variant="ghost"
          size="sm"
          onClick={() => router.push(`/classes/${classId}`)}
          className="text-muted-foreground -ml-2"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back
        </Button>

        <h2 className="text-2xl font-semibold">Edit class</h2>

        <div className="space-y-4 border rounded-lg p-5">
          <div className="space-y-2">
            <Label>Class name</Label>
            <Input value={name} onChange={(e) => setName(e.target.value)} />
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
              Delete class
            </Button>
          ) : (
            <div className="space-y-2">
              <p className="text-sm text-muted-foreground">
                Are you sure? This will remove all enrollments.
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