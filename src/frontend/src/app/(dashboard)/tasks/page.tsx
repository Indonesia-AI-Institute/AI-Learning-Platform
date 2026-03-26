"use client";

import { useQuery } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { useCurrentUser } from "@/hooks/useCurrentUser";
import { taskService } from "@/services/task.service";
import { enrollmentService } from "@/services/enrollment.service";
import { classService } from "@/services/class.service";
import { Button } from "@/components/ui/button";
import { ClipboardList, Calendar } from "lucide-react";
import { Task } from "@/types/task.types";

export default function TasksPage() {
  const router = useRouter();
  const { user } = useCurrentUser();
  const isTeacher = user?.role === "teacher";

  // Student: get enrolled class_ids → fetch tasks per class
  const { data: enrollments } = useQuery({
    queryKey: ["myEnrollments"],
    queryFn: () => enrollmentService.getMyEnrollments(),
    enabled: !isTeacher,
  });

  const { data: studentTasks, isLoading: loadingStudentTasks } = useQuery({
    queryKey: ["allStudentTasks", enrollments?.map((e) => e.class_id)],
    queryFn: async () => {
      if (!enrollments?.length) return [];
      const tasksByClass = await Promise.all(
        enrollments.map((e) => taskService.getTasksByClass(e.class_id))
      );
      // Flatten and deduplicate by task id
      const all = tasksByClass.flat();
      const seen = new Set<string>();
      return all.filter((t) => {
        if (seen.has(t.id)) return false;
        seen.add(t.id);
        return true;
      });
    },
    enabled: !isTeacher && !!enrollments,
  });

  // Teacher: get own classes → fetch tasks per class
  const { data: myClasses } = useQuery({
    queryKey: ["myClasses"],
    queryFn: () => classService.getMyClasses(),
    enabled: isTeacher,
  });

  const { data: teacherTasks, isLoading: loadingTeacherTasks } = useQuery({
    queryKey: ["allTeacherTasks", myClasses?.map((c) => c.id)],
    queryFn: async () => {
      if (!myClasses?.length) return [];
      const tasksByClass = await Promise.all(
        myClasses.map((c) => taskService.getTasksByClass(c.id))
      );
      const all = tasksByClass.flat();
      const seen = new Set<string>();
      return all.filter((t) => {
        if (seen.has(t.id)) return false;
        seen.add(t.id);
        return true;
      });
    },
    enabled: isTeacher && !!myClasses,
  });

  const tasks: Task[] = (isTeacher ? teacherTasks : studentTasks) ?? [];
  const isLoading = isTeacher ? loadingTeacherTasks : loadingStudentTasks;

  return (
    <DashboardLayout title="Tasks">
      <div className="space-y-6">

        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-semibold">Tasks</h2>
            <p className="text-muted-foreground text-sm mt-1">
              {isTeacher ? "All tasks across your classes" : "Tasks from your enrolled classes"}
            </p>
          </div>
        </div>

        {isLoading ? (
          <p className="text-muted-foreground text-sm">Loading...</p>
        ) : !tasks.length ? (
          <div className="flex flex-col items-center justify-center py-16 text-center border rounded-lg">
            <ClipboardList className="w-10 h-10 text-muted-foreground mb-3" />
            <p className="font-medium">No tasks yet</p>
            <p className="text-sm text-muted-foreground mt-1">
              {isTeacher
                ? "Add tasks from a class detail page"
                : "Enroll in a class to see tasks"}
            </p>
            {!isTeacher && (
              <Button
                size="sm"
                className="mt-3"
                onClick={() => router.push("/courses")}
              >
                Browse courses
              </Button>
            )}
          </div>
        ) : (
          <div className="space-y-2">
            {tasks.map((task) => (
              <div
                key={task.id}
                className="flex items-center justify-between border rounded-lg p-4 hover:bg-muted/50 cursor-pointer transition-colors"
                onClick={() => router.push(`/tasks/${task.id}`)}
              >
                <div className="space-y-0.5">
                  <p className="font-medium">{task.title}</p>
                  {task.description && (
                    <p className="text-sm text-muted-foreground line-clamp-1">
                      {task.description}
                    </p>
                  )}
                </div>
                {task.due_date && (
                  <div className="flex items-center gap-1.5 text-xs text-muted-foreground shrink-0 ml-4">
                    <Calendar className="w-3.5 h-3.5" />
                    {new Date(task.due_date).toLocaleDateString()}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}