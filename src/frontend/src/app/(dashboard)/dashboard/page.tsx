"use client";

/**
 * app/(dashboard)/dashboard/page.tsx
 */

import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { StudentDashboard } from "@/components/dashboard/StudentDashboard";
import { TeacherDashboard } from "@/components/dashboard/TeacherDashboard";
import { useCurrentUser } from "@/hooks/useCurrentUser";

export default function DashboardPage() {
  const { user, isLoading } = useCurrentUser();

  if (isLoading || !user) {
    return (
      <DashboardLayout title="Dashboard">
        <div className="flex items-center justify-center h-64">
          <p className="text-muted-foreground text-sm">Loading...</p>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout title="Dashboard">
      {user.role === "teacher" ? (
        <TeacherDashboard fullName={user.full_name} />
      ) : (
        <StudentDashboard fullName={user.full_name} />
      )}
    </DashboardLayout>
  );
}