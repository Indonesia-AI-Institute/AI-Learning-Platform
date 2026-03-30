"use client";

import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { useCurrentUser } from "@/hooks/useCurrentUser";
import { taskService } from "@/services/task.service";
import { enrollmentService } from "@/services/enrollment.service";
import { classService } from "@/services/class.service";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ClipboardList, Calendar, Search } from "lucide-react";
import { Task } from "@/types/task.types";
import { Class } from "@/types/class.types";

// Extended task with class info for display
interface TaskWithClass extends Task {
  className?: string;
  classId?: string;
}

export default function TasksPage() {
  const router = useRouter();
  const { user } = useCurrentUser();
  const isTeacher = user?.role === "teacher";

  const [search, setSearch] = useState("");
  const [filterClass, setFilterClass] = useState<string>("all");

  // Student: enrolled classes → tasks
  const { data: enrollments } = useQuery({
    queryKey: ["myEnrollments"],
    queryFn: () => enrollmentService.getMyEnrollments(),
    enabled: !isTeacher,
  });

  // Teacher: own classes → tasks
  const { data: myClasses } = useQuery({
    queryKey: ["myClasses"],
    queryFn: () => classService.getMyClasses(),
    enabled: isTeacher,
  });

  const classes: Class[] = (isTeacher ? myClasses : undefined) ?? [];

  const classIds = isTeacher
    ? myClasses?.map((c) => c.id) ?? []
    : enrollments?.map((e) => e.class_id) ?? [];

  const { data: tasksWithClass, isLoading } = useQuery({
    queryKey: ["allTasks", classIds],
    queryFn: async (): Promise<TaskWithClass[]> => {
      if (!classIds.length) return [];

      const allClasses = isTeacher
        ? myClasses ?? []
        : await Promise.all(
            (enrollments ?? []).map((e) => classService.getClassDetail(e.class_id))
          );

      const tasksByClass = await Promise.all(
        allClasses.map(async (cls) => {
          const tasks = await taskService.getTasksByClass(cls.id);
          return tasks.map((t) => ({
            ...t,
            className: cls.name,
            classId: cls.id,
          }));
        })
      );

      // Flatten and deduplicate
      const all = tasksByClass.flat();
      const seen = new Set<string>();
      return all.filter((t) => {
        if (seen.has(t.id)) return false;
        seen.add(t.id);
        return true;
      });
    },
    enabled: classIds.length > 0,
  });

  const filtered = useMemo(() => {
    if (!tasksWithClass) return [];
    return tasksWithClass.filter((t) => {
      const matchSearch =
        t.title.toLowerCase().includes(search.toLowerCase()) ||
        (t.description ?? "").toLowerCase().includes(search.toLowerCase()) ||
        (t.className ?? "").toLowerCase().includes(search.toLowerCase());
      const matchClass =
        filterClass === "all" ? true : t.classId === filterClass;
      return matchSearch && matchClass;
    });
  }, [tasksWithClass, search, filterClass]);

  // Unique classes for filter dropdown
  const uniqueClasses = useMemo(() => {
    if (!tasksWithClass) return [];
    const seen = new Set<string>();
    return tasksWithClass
      .filter((t) => {
        if (!t.classId || seen.has(t.classId)) return false;
        seen.add(t.classId);
        return true;
      })
      .map((t) => ({ id: t.classId!, name: t.className! }));
  }, [tasksWithClass]);

  return (
    <DashboardLayout title="Tasks">
      <div className="space-y-6">

        <div>
          <h2 className="text-2xl font-semibold">Tasks</h2>
          <p className="text-muted-foreground text-sm mt-1">
            {isTeacher ? "All tasks across your classes" : "Tasks from your enrolled classes"}
          </p>
        </div>

        {/* Search & Filter */}
        <div className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input
              placeholder="Search tasks or class name..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-9"
            />
          </div>
          {uniqueClasses.length > 1 && (
            <select
              value={filterClass}
              onChange={(e) => setFilterClass(e.target.value)}
              className="border rounded-md px-3 py-2 text-sm bg-background min-w-[160px]"
            >
              <option value="all">All classes</option>
              {uniqueClasses.map((cls) => (
                <option key={cls.id} value={cls.id}>{cls.name}</option>
              ))}
            </select>
          )}
        </div>

        {isLoading ? (
          <p className="text-muted-foreground text-sm">Loading...</p>
        ) : !filtered.length ? (
          <div className="flex flex-col items-center justify-center py-16 text-center border rounded-lg">
            <ClipboardList className="w-10 h-10 text-muted-foreground mb-3" />
            <p className="font-medium">
              {search || filterClass !== "all" ? "No tasks match your filter" : "No tasks yet"}
            </p>
            {!isTeacher && !search && filterClass === "all" && (
              <Button size="sm" className="mt-3" onClick={() => router.push("/courses")}>
                Browse courses
              </Button>
            )}
          </div>
        ) : (
          <div className="space-y-2">
            {filtered.map((task) => (
              <div
                key={task.id}
                className="flex items-center justify-between border rounded-lg p-4 hover:bg-muted/50 cursor-pointer transition-colors"
                onClick={() => router.push(`/tasks/${task.id}`)}
              >
                <div className="space-y-0.5 min-w-0">
                  <p className="font-medium truncate">{task.title}</p>
                  <div className="flex items-center gap-2 flex-wrap">
                    {/* Class name */}
                    {task.className && (
                      <span className="text-xs text-muted-foreground bg-muted px-2 py-0.5 rounded">
                        {task.className}
                      </span>
                    )}
                    {task.description && (
                      <p className="text-xs text-muted-foreground line-clamp-1">
                        {task.description}
                      </p>
                    )}
                  </div>
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