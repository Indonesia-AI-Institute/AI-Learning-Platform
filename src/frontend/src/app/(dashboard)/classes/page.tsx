"use client";

import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { useCurrentUser } from "@/hooks/useCurrentUser";
import { classService } from "@/services/class.service";
import { enrollmentService } from "@/services/enrollment.service";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Users, Plus, ArrowRight, Search } from "lucide-react";

export default function ClassesPage() {
  const router = useRouter();
  const { user } = useCurrentUser();
  const isTeacher = user?.role === "teacher";

  const [search, setSearch] = useState("");
  const [filterStatus, setFilterStatus] = useState<"all" | "active" | "inactive">("all");

  const { data: teacherClasses, isLoading: loadingTeacher } = useQuery({
    queryKey: ["myClasses"],
    queryFn: () => classService.getMyClasses(),
    enabled: isTeacher,
  });

  const { data: enrollments, isLoading: loadingEnrollments } = useQuery({
    queryKey: ["myEnrollments"],
    queryFn: () => enrollmentService.getMyEnrollments(),
    enabled: !isTeacher,
  });

  const { data: enrolledClasses, isLoading: loadingClasses } = useQuery({
    queryKey: ["enrolledClasses", enrollments?.map((e) => e.class_id)],
    queryFn: async () => {
      if (!enrollments?.length) return [];
      return Promise.all(
        enrollments.map((e) => classService.getClassDetail(e.class_id))
      );
    },
    enabled: !isTeacher && !!enrollments,
  });

  const isLoading = isTeacher ? loadingTeacher : loadingEnrollments || loadingClasses;
  const allClasses = isTeacher ? teacherClasses : enrolledClasses;

  const filtered = useMemo(() => {
    if (!allClasses) return [];
    return allClasses.filter((c) => {
      const matchSearch =
        c.name.toLowerCase().includes(search.toLowerCase()) ||
        (c.description ?? "").toLowerCase().includes(search.toLowerCase()) ||
        (c.course?.title ?? "").toLowerCase().includes(search.toLowerCase());
      const matchStatus =
        filterStatus === "all" ? true : filterStatus === "active" ? c.is_active : !c.is_active;
      return matchSearch && matchStatus;
    });
  }, [allClasses, search, filterStatus]);

  return (
    <DashboardLayout title="Classes">
      <div className="space-y-6">

        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-semibold">Classes</h2>
            <p className="text-muted-foreground text-sm mt-1">
              {isTeacher ? "Classes you manage" : "Classes you are enrolled in"}
            </p>
          </div>
          {isTeacher && (
            <Button onClick={() => router.push("/classes/create")} size="sm">
              <Plus className="w-4 h-4 mr-2" />
              New class
            </Button>
          )}
        </div>

        {/* Search & Filter */}
        <div className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input
              placeholder="Search by class name or course..."
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
            <Users className="w-10 h-10 text-muted-foreground mb-3" />
            <p className="font-medium">
              {search || filterStatus !== "all" ? "No classes match your filter" : "No classes yet"}
            </p>
            {!isTeacher && !search && filterStatus === "all" && (
              <Button size="sm" className="mt-3" onClick={() => router.push("/courses")}>
                Browse courses
              </Button>
            )}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filtered.map((cls) => (
              <div
                key={cls.id}
                className="border rounded-lg p-4 hover:bg-muted/50 cursor-pointer transition-colors space-y-3"
                onClick={() => router.push(`/classes/${cls.id}`)}
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="space-y-0.5 min-w-0">
                    <p className="font-medium truncate">{cls.name}</p>
                    {/* Course name */}
                    {cls.course && (
                      <p className="text-xs text-muted-foreground">
                        Course: {cls.course.title}
                      </p>
                    )}
                  </div>
                  <span className={`text-xs px-2 py-0.5 rounded-full shrink-0 ${
                    cls.is_active ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-500"
                  }`}>
                    {cls.is_active ? "Active" : "Inactive"}
                  </span>
                </div>
                {cls.description && (
                  <p className="text-sm text-muted-foreground line-clamp-2">
                    {cls.description}
                  </p>
                )}
                <div className="flex items-center text-xs text-muted-foreground">
                  <ArrowRight className="w-3 h-3 mr-1" />
                  View tasks
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}