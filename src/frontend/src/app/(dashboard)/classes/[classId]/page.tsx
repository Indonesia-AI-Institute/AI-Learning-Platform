"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useParams, useRouter } from "next/navigation";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { useCurrentUser } from "@/hooks/useCurrentUser";
import { classService } from "@/services/class.service";
import { taskService } from "@/services/task.service";
import { enrollmentService } from "@/services/enrollment.service";
import { Button } from "@/components/ui/button";
import { ArrowLeft, ClipboardList, Plus, LogOut } from "lucide-react";
import { useState } from "react";

export default function ClassDetailPage() {
  const { classId } = useParams<{ classId: string }>();
  const router = useRouter();
  const queryClient = useQueryClient();
  const { user } = useCurrentUser();
  const isTeacher = user?.role === "teacher";
  const [showUnenrollConfirm, setShowUnenrollConfirm] = useState(false);

  const { data: cls, isLoading: loadingClass } = useQuery({
    queryKey: ["class", classId],
    queryFn: () => classService.getClassDetail(classId),
  });

  const { data: tasks, isLoading: loadingTasks } = useQuery({
    queryKey: ["tasksByClass", classId],
    queryFn: () => taskService.getTasksByClass(classId),
  });

  // Student: get enrollment id for unenroll
  const { data: enrollments } = useQuery({
    queryKey: ["myEnrollments"],
    queryFn: () => enrollmentService.getMyEnrollments(),
    enabled: !isTeacher,
  });

  const enrollment = enrollments?.find((e) => e.class_id === classId);

  const unenrollMutation = useMutation({
    mutationFn: () => enrollmentService.unenroll(enrollment!.id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["myEnrollments"] });
      queryClient.invalidateQueries({ queryKey: ["enrolledClasses"] });
      router.push("/classes");
    },
  });

  const isLoading = loadingClass || loadingTasks;

  return (
    <DashboardLayout title={cls?.name ?? "Class Detail"}>
      <div className="max-w-2xl space-y-6">

        <Button
          variant="ghost"
          size="sm"
          onClick={() => router.push("/classes")}
          className="text-muted-foreground -ml-2"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to classes
        </Button>

        {isLoading ? (
          <p className="text-muted-foreground text-sm">Loading...</p>
        ) : (
          <>
            {/* Class info */}
            <div className="space-y-1">
              <div className="flex items-center gap-3">
                <h2 className="text-2xl font-semibold">{cls?.name}</h2>
                <span className={`text-xs px-2 py-0.5 rounded-full ${
                  cls?.is_active
                    ? "bg-green-100 text-green-700"
                    : "bg-gray-100 text-gray-500"
                }`}>
                  {cls?.is_active ? "Active" : "Inactive"}
                </span>
              </div>
              {cls?.description && (
                <p className="text-muted-foreground text-sm">{cls.description}</p>
              )}
              {isTeacher && (
                <p className="text-xs text-muted-foreground font-mono">
                  ID: {classId}
                </p>
              )}
            </div>

            {/* Teacher actions */}
            {isTeacher && (
              <div className="flex gap-2">
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => router.push(`/classes/${classId}/edit`)}
                >
                  Edit class
                </Button>
                <Button
                  size="sm"
                  onClick={() => router.push(`/tasks/create?course_id=${cls?.course_id}`)}
                >
                  <Plus className="w-4 h-4 mr-2" />
                  Add task
                </Button>
              </div>
            )}

            {/* Tasks */}
            <div className="space-y-3">
              <h3 className="font-medium">Tasks</h3>

              {!tasks?.length ? (
                <div className="flex flex-col items-center justify-center py-12 text-center border rounded-lg">
                  <ClipboardList className="w-8 h-8 text-muted-foreground mb-2" />
                  <p className="text-sm font-medium">No tasks yet</p>
                </div>
              ) : (
                <div className="space-y-2">
                  {tasks.map((task) => (
                    <div
                      key={task.id}
                      className="flex items-center justify-between border rounded-lg p-3 hover:bg-muted/50 cursor-pointer transition-colors"
                      onClick={() => router.push(`/tasks/${task.id}`)}
                    >
                      <div>
                        <p className="text-sm font-medium">{task.title}</p>
                        {task.description && (
                          <p className="text-xs text-muted-foreground mt-0.5 line-clamp-1">
                            {task.description}
                          </p>
                        )}
                      </div>
                      {task.due_date && (
                        <span className="text-xs text-muted-foreground shrink-0 ml-4">
                          Due {new Date(task.due_date).toLocaleDateString()}
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Student: unenroll */}
            {!isTeacher && enrollment && (
              <div className="border border-destructive/30 rounded-lg p-4 space-y-3">
                <p className="text-sm font-medium text-destructive">Leave class</p>
                {!showUnenrollConfirm ? (
                  <Button
                    variant="outline"
                    size="sm"
                    className="text-destructive border-destructive/30"
                    onClick={() => setShowUnenrollConfirm(true)}
                  >
                    <LogOut className="w-4 h-4 mr-2" />
                    Unenroll from this class
                  </Button>
                ) : (
                  <div className="space-y-2">
                    <p className="text-sm text-muted-foreground">
                      Are you sure you want to leave this class?
                    </p>
                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        variant="destructive"
                        onClick={() => unenrollMutation.mutate()}
                        disabled={unenrollMutation.isPending}
                      >
                        {unenrollMutation.isPending ? "Leaving..." : "Yes, leave"}
                      </Button>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => setShowUnenrollConfirm(false)}
                      >
                        Cancel
                      </Button>
                    </div>
                  </div>
                )}
              </div>
            )}
          </>
        )}
      </div>
    </DashboardLayout>
  );
}