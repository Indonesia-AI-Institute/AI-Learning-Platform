"use client";

import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { enrollmentService } from "@/services/enrollment.service";
import { getErrorMessage } from "@/lib/errors";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ArrowLeft } from "lucide-react";

export default function JoinClassPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [classId, setClassId] = useState("");
  const [error, setError] = useState<string | null>(null);

  const enrollMutation = useMutation({
    mutationFn: () => enrollmentService.enroll({ class_id: classId }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["myEnrollments"] });
      queryClient.invalidateQueries({ queryKey: ["enrolledClasses"] });
      router.push("/classes");
    },
    onError: (err: unknown) => {
      setError(getErrorMessage(err, "Failed to join class. Please check the class ID and try again."));
    },
  });

  const handleSubmit = () => {
    if (!classId.trim()) {
      setError("Please enter a class ID.");
      return;
    }
    setError(null);
    enrollMutation.mutate();
  };

  return (
    <DashboardLayout title="Join a Class">
      <div className="max-w-md space-y-6">

        {/* Back */}
        <Button
          variant="ghost"
          size="sm"
          onClick={() => router.push("/classes")}
          className="text-muted-foreground -ml-2"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to classes
        </Button>

        <div>
          <h2 className="text-2xl font-semibold">Join a class</h2>
          <p className="text-muted-foreground text-sm mt-1">
            Enter the class ID provided by your teacher.
          </p>
        </div>

        <div className="space-y-4 border rounded-lg p-5">
          <div className="space-y-2">
            <Label htmlFor="class-id">Class ID</Label>
            <Input
              id="class-id"
              placeholder="e.g. 550e8400-e29b-41d4-a716-446655440000"
              value={classId}
              onChange={(e) => setClassId(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSubmit()}
            />
          </div>

          {error && (
            <p className="text-sm text-destructive">{error}</p>
          )}

          <Button
            className="w-full"
            onClick={handleSubmit}
            disabled={enrollMutation.isPending}
          >
            {enrollMutation.isPending ? "Joining..." : "Join class"}
          </Button>
        </div>

      </div>
    </DashboardLayout>
  );
}