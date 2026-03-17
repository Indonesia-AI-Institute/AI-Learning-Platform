"use client";

import { useQuery } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { useCurrentUser } from "@/hooks/useCurrentUser";
import { courseService } from "@/services/course.service";
import { Button } from "@/components/ui/button";
import { BookOpen, Plus } from "lucide-react";

export default function CoursesPage() {
  const router = useRouter();
  const { user } = useCurrentUser();
  const isTeacher = user?.role === "teacher";

  // Teacher: my courses, Student: all active courses
  const { data: courses, isLoading } = useQuery({
    queryKey: isTeacher ? ["myCourses"] : ["allCourses"],
    queryFn: isTeacher ? courseService.getMyCourses : courseService.getAllCourses,
    enabled: !!user,
  });

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

        {isLoading ? (
          <p className="text-muted-foreground text-sm">Loading...</p>
        ) : !courses?.length ? (
          <div className="flex flex-col items-center justify-center py-16 text-center border rounded-lg">
            <BookOpen className="w-10 h-10 text-muted-foreground mb-3" />
            <p className="font-medium">No courses available</p>
            {isTeacher && (
              <p className="text-sm text-muted-foreground mt-1">
                Create your first course to get started
              </p>
            )}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {courses.map((course) => (
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