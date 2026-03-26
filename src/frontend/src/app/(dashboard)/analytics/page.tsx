"use client";

/**
 * app/(dashboard)/analytics/page.tsx
 * Teacher analytics — select class or task to drill down
 */

import { useQuery } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { classService } from "@/services/class.service";
import { analyticsService } from "@/services/analytics.service";
import { Button } from "@/components/ui/button";
import { BarChart2, Users, ChevronRight } from "lucide-react";
import { useState } from "react";

function formatDuration(seconds: number): string {
  if (seconds < 60) return `${seconds}s`;
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m`;
  const hours = Math.floor(minutes / 60);
  return `${hours}h ${minutes % 60}m`;
}

export default function TeacherAnalyticsPage() {
  const router = useRouter();
  const [selectedClassId, setSelectedClassId] = useState<string | null>(null);

  const { data: classes, isLoading: loadingClasses } = useQuery({
    queryKey: ["myClasses"],
    queryFn: () => classService.getMyClasses(),
  });

  const { data: classAnalytics, isLoading: loadingAnalytics } = useQuery({
    queryKey: ["classAnalytics", selectedClassId],
    queryFn: () => analyticsService.getClassAnalytics(selectedClassId!),
    enabled: !!selectedClassId,
  });

  return (
    <DashboardLayout title="Analytics">
      <div className="space-y-6">

        <div>
          <h2 className="text-2xl font-semibold">Analytics</h2>
          <p className="text-muted-foreground text-sm mt-1">
            Monitor student AI activity across your classes
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

          {/* Class list */}
          <div className="space-y-3">
            <p className="text-sm font-medium">Select a class</p>
            {loadingClasses ? (
              <p className="text-muted-foreground text-sm">Loading...</p>
            ) : !classes?.length ? (
              <p className="text-sm text-muted-foreground">No classes yet.</p>
            ) : (
              <div className="space-y-2">
                {classes.map((cls) => (
                  <button
                    key={cls.id}
                    onClick={() => setSelectedClassId(cls.id)}
                    className={`w-full text-left border rounded-lg p-3 text-sm transition-colors hover:bg-muted/50 ${
                      selectedClassId === cls.id
                        ? "border-primary bg-primary/5"
                        : ""
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-medium">{cls.name}</span>
                      <ChevronRight className="w-4 h-4 text-muted-foreground" />
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Analytics panel */}
          <div className="lg:col-span-2">
            {!selectedClassId ? (
              <div className="flex flex-col items-center justify-center py-16 text-center border rounded-lg h-full">
                <BarChart2 className="w-10 h-10 text-muted-foreground mb-3" />
                <p className="font-medium">Select a class</p>
                <p className="text-sm text-muted-foreground mt-1">
                  Choose a class to view student analytics
                </p>
              </div>
            ) : loadingAnalytics ? (
              <p className="text-muted-foreground text-sm">Loading analytics...</p>
            ) : !classAnalytics?.students?.length ? (
              <div className="flex flex-col items-center justify-center py-16 text-center border rounded-lg">
                <Users className="w-10 h-10 text-muted-foreground mb-3" />
                <p className="font-medium">No data yet</p>
                <p className="text-sm text-muted-foreground mt-1">
                  Students haven't completed any sessions in this class
                </p>
              </div>
            ) : (
              <div className="space-y-3">
                <p className="text-sm font-medium">
                  {classAnalytics.students.length} student
                  {classAnalytics.students.length !== 1 ? "s" : ""} with activity
                </p>
                <div className="border rounded-lg overflow-hidden">
                  <table className="w-full text-sm">
                    <thead className="bg-muted/50">
                      <tr>
                        <th className="text-left px-4 py-3 font-medium text-muted-foreground">Student</th>
                        <th className="text-right px-4 py-3 font-medium text-muted-foreground">Sessions</th>
                        <th className="text-right px-4 py-3 font-medium text-muted-foreground">Prompts</th>
                        <th className="text-right px-4 py-3 font-medium text-muted-foreground">Avg length</th>
                        <th className="text-right px-4 py-3 font-medium text-muted-foreground">Duration</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y">
                      {classAnalytics.students.map((student) => (
                        <tr
                          key={student.student_id}
                          className="hover:bg-muted/30 cursor-pointer"
                          onClick={() =>
                            router.push(
                              `/analytics/class/${selectedClassId}/student/${student.student_id}`
                            )
                          }
                        >
                          <td className="px-4 py-3 font-mono text-xs text-muted-foreground">
                            {student.student_id.slice(0, 8)}...
                          </td>
                          <td className="px-4 py-3 text-right">{student.total_sessions}</td>
                          <td className="px-4 py-3 text-right">{student.total_prompts}</td>
                          <td className="px-4 py-3 text-right">
                            {student.avg_prompt_length.toFixed(0)} chars
                          </td>
                          <td className="px-4 py-3 text-right">
                            {formatDuration(student.total_duration_seconds)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        </div>

      </div>
    </DashboardLayout>
  );
}