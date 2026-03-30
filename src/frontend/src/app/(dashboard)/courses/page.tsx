"use client";

import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { useCurrentUser } from "@/hooks/useCurrentUser";
import { courseService } from "@/services/course.service";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { BookOpen, Plus, Search } from "lucide-react";

export default function CoursesPage() {
  const router = useRouter();
  const { user } = useCurrentUser();
  const isTeacher = user?.role === "teacher";

  const [search, setSearch] = useState("");
  const [filterStatus, setFilterStatus] = useState<"all" | "active" | "inactive">("all");

  const { data: courses, isLoading } = useQuery({
    queryKey: isTeacher ? ["myCourses"] : ["allCourses"],
    queryFn: isTeacher ? courseService.getMyCourses : courseService.getAllCourses,
    enabled: !!user,
  });

  const filtered = useMemo(() => {
    if (!courses) return [];
    return courses.filter((c) => {
      const matchSearch =
        c.title.toLowerCase().includes(search.toLowerCase()) ||
        (c.description ?? "").toLowerCase().includes(search.toLowerCase());
      const matchStatus =
        filterStatus === "all"
          ? true
          : filterStatus === "active"
          ? c.is_active
          : !c.is_active;
      return matchSearch && matchStatus;
    });
  }, [courses, search, filterStatus]);

  return (
    <DashboardLayout title="Courses">
      <div className="space-y-6">

        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-semibold">Courses</h2>
            <p className="text-muted-foreground text-sm mt-1">
              {isTeacher ? "Manage your courses" : "Browse available courses"}
            </p>
          </div>
          {isTeacher && (
            <Button onClick={() => router.push("/courses/create")} size="sm">
              <Plus className="w-4 h-4 mr-2" />
              New course
            </Button>
          )}
        </div>

        {/* Search & Filter */}
        <div className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input
              placeholder="Search courses..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-9"
            />
          </div>
          <div className="flex gap-2">
            {(["all", "active", "inactive"] as const).map((status) => (
              <button
                key={status}
                onClick={() => setFilterStatus(status)}
                className={`px-3 py-1.5 rounded-md text-sm capitalize transition-colors ${
                  filterStatus === status
                    ? "bg-primary text-primary-foreground"
                    : "border hover:bg-muted"
                }`}
              >
                {status}
              </button>
            ))}
          </div>
        </div>

        {isLoading ? (
          <p className="text-muted-foreground text-sm">Loading...</p>
        ) : !filtered.length ? (
          <div className="flex flex-col items-center justify-center py-16 text-center border rounded-lg">
            <BookOpen className="w-10 h-10 text-muted-foreground mb-3" />
            <p className="font-medium">
              {search || filterStatus !== "all" ? "No courses match your filter" : "No courses available"}
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filtered.map((course) => (
              <div
                key={course.id}
                className="border rounded-lg p-4 hover:bg-muted/50 cursor-pointer transition-colors space-y-2"
                onClick={() => router.push(`/courses/${course.id}`)}
              >
                <div className="flex items-start justify-between gap-2">
                  <p className="font-medium">{course.title}</p>
                  <span className={`text-xs px-2 py-0.5 rounded-full shrink-0 ${
                    course.is_active
                      ? "bg-green-100 text-green-700"
                      : "bg-gray-100 text-gray-500"
                  }`}>
                    {course.is_active ? "Active" : "Inactive"}
                  </span>
                </div>
                {course.description && (
                  <p className="text-sm text-muted-foreground line-clamp-2">
                    {course.description}
                  </p>
                )}
                <p className="text-xs text-muted-foreground">
                  {new Date(course.created_at).toLocaleDateString()}
                </p>
              </div>
            ))}
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}