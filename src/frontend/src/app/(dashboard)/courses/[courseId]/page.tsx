"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useParams, useRouter } from "next/navigation";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { useCurrentUser } from "@/hooks/useCurrentUser";
import { courseService } from "@/services/course.service";
import { classService } from "@/services/class.service";
import { enrollmentService } from "@/services/enrollment.service";
import { Button } from "@/components/ui/button";
import { ArrowLeft, Plus, Users } from "lucide-react";

export default function CourseDetailPage() {
  const { courseId } = useParams<{ courseId: string }>();
  const router = useRouter();
  const queryClient = useQueryClient();
  const { user } = useCurrentUser();
  const isTeacher = user?.role === "teacher";

  const { data: course, isLoading: loadingCourse } = useQuery({
    queryKey: ["course", courseId],
    queryFn: () => courseService.getCourseDetail(courseId),
  });

  const { data: classes, isLoading: loadingClasses } = useQuery({
    queryKey: ["classesByCourse", courseId],
    queryFn: () => classService.getClassesByCourse(courseId),
    enabled: !!courseId,
  });

  // Student: fetch own enrollments to check which classes already joined
  const { data: enrollments } = useQuery({
    queryKey: ["myEnrollments"],
    queryFn: () => enrollmentService.getMyEnrollments(),
    enabled: !isTeacher,
  });

  const enrolledClassIds = new Set(enrollments?.map((e) => e.class_id) ?? []);

  const enrollMutation = useMutation({
    mutationFn: (classId: string) =>
      enrollmentService.enroll({ class_id: classId }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["myEnrollments"] });
      queryClient.invalidateQueries({ queryKey: ["enrolledClasses"] });
    },
  });

  const isLoading = loadingCourse || loadingClasses;

  return (
    <DashboardLayout title={course?.title ?? "Course Detail"}>
      <div className="max-w-2xl space-y-6">

        <Button
          variant="ghost"
          size="sm"
          onClick={() => router.push("/courses")}
          className="text-muted-foreground -ml-2"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to courses
        </Button>

        {isLoading ? (
          <p className="text-muted-foreground text-sm">Loading...</p>
        ) : (
          <>
            {/* Course info */}
            <div className="space-y-2">
              <div className="flex items-center gap-3">
                <h2 className="text-2xl font-semibold">{course?.title}</h2>
                <span className={`text-xs px-2 py-0.5 rounded-full ${
                  course?.is_active
                    ? "bg-green-100 text-green-700"
                    : "bg-gray-100 text-gray-500"
                }`}>
                  {course?.is_active ? "Active" : "Inactive"}
                </span>
              </div>
              {course?.description && (
                <p className="text-muted-foreground text-sm">{course.description}</p>
              )}
            </div>

            {/* Teacher actions */}
            {isTeacher && (
              <div className="flex gap-2">
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => router.push(`/courses/${courseId}/edit`)}
                >
                  Edit course
                </Button>
                <Button
                  size="sm"
                  onClick={() => router.push(`/classes/create?course_id=${courseId}`)}
                >
                  <Plus className="w-4 h-4 mr-2" />
                  Add class
                </Button>
              </div>
            )}

            {/* Classes list */}
            <div className="space-y-3">
              <h3 className="font-medium">Classes</h3>

              {!classes?.length ? (
                <div className="flex flex-col items-center justify-center py-10 text-center border rounded-lg">
                  <Users className="w-8 h-8 text-muted-foreground mb-2" />
                  <p className="text-sm font-medium">No classes yet</p>
                  {isTeacher && (
                    <p className="text-xs text-muted-foreground mt-1">
                      Add a class to this course
                    </p>
                  )}
                </div>
              ) : (
                <div className="space-y-2">
                  {classes.map((cls) => {
                    const isEnrolled = enrolledClassIds.has(cls.id);

                    return (
                      <div
                        key={cls.id}
                        className="flex items-center justify-between border rounded-lg p-3"
                      >
                        <div>
                          <p className="text-sm font-medium">{cls.name}</p>
                          {cls.description && (
                            <p className="text-xs text-muted-foreground mt-0.5">
                              {cls.description}
                            </p>
                          )}
                        </div>

                        <div className="flex items-center gap-2 shrink-0 ml-4">
                          <span className={`text-xs px-2 py-0.5 rounded-full ${
                            cls.is_active
                              ? "bg-green-100 text-green-700"
                              : "bg-gray-100 text-gray-500"
                          }`}>
                            {cls.is_active ? "Active" : "Inactive"}
                          </span>

                          {isTeacher ? (
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => router.push(`/classes/${cls.id}`)}
                            >
                              View
                            </Button>
                          ) : isEnrolled ? (
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => router.push(`/classes/${cls.id}`)}
                            >
                              Open
                            </Button>
                          ) : (
                            <Button
                              size="sm"
                              onClick={() => enrollMutation.mutate(cls.id)}
                              disabled={
                                enrollMutation.isPending || !cls.is_active
                              }
                            >
                              {enrollMutation.isPending ? "Joining..." : "Join"}
                            </Button>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </>
        )}
      </div>
    </DashboardLayout>
  );
}