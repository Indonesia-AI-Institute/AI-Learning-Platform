"use client";

/**
 * TeacherDashboard.tsx
 * ====================
 * Dashboard content for teacher role.
 */

import { useQuery } from "@tanstack/react-query";
import { Users, BookOpen, Link } from "lucide-react";
import { StatCard } from "@/components/dashboard/StatCard";
import { classService } from "@/services/class.service";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";

export function TeacherDashboard({ fullName }: { fullName: string }) {
  const router = useRouter();

  const { data: classes, isLoading } = useQuery({
    queryKey: ["myClasses"],
    queryFn: () => classService.getMyClasses(),
  });

  const activeClasses = classes?.filter((c) => c.is_active).length ?? 0;
  const totalClasses = classes?.length ?? 0;

  return (
    <div className="space-y-6">

      {/* Welcome */}
      <div>
        <h2 className="text-2xl font-semibold">Welcome back, {fullName} 👋</h2>
        <p className="text-muted-foreground mt-1">
          Manage your classes and monitor student AI activity.
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <StatCard
          title="Total Classes"
          value={isLoading ? "—" : totalClasses}
          description="Classes you manage"
          icon={Users}
        />
        <StatCard
          title="Active Classes"
          value={isLoading ? "—" : activeClasses}
          description="Currently active classes"
          icon={BookOpen}
        />
        <StatCard
          title="Inactive Classes"
          value={isLoading ? "—" : totalClasses - activeClasses}
          description="Archived or inactive"
          icon={Link}
        />
      </div>

      {/* Quick actions */}
      <div className="rounded-lg border p-4 space-y-3">
        <p className="text-sm font-medium">Quick actions</p>
        <div className="flex flex-wrap gap-2">
          <Button
            size="sm"
            variant="outline"
            onClick={() => router.push("/courses/create")}
          >
            Create course
          </Button>
          <Button
            size="sm"
            variant="outline"
            onClick={() => router.push("/classes/create")}
          >
            Create class
          </Button>
          <Button
            size="sm"
            variant="outline"
            onClick={() => router.push("/tasks/create")}
          >
            Create task
          </Button>
          <Button
            size="sm"
            variant="outline"
            onClick={() => router.push("/analytics")}
          >
            View analytics
          </Button>
        </div>
      </div>

      {/* Class list preview */}
      {classes && classes.length > 0 && (
        <div className="space-y-2">
          <p className="text-sm font-medium">Your classes</p>
          <div className="space-y-2">
            {classes.slice(0, 5).map((cls) => (
              <div
                key={cls.id}
                className="flex items-center justify-between rounded-lg border p-3 hover:bg-muted/50 cursor-pointer transition-colors"
                onClick={() => router.push(`/classes/${cls.id}`)}
              >
                <div>
                  <p className="text-sm font-medium">{cls.name}</p>
                  {cls.description && (
                    <p className="text-xs text-muted-foreground truncate max-w-sm">
                      {cls.description}
                    </p>
                  )}
                </div>
                <span
                  className={`text-xs px-2 py-0.5 rounded-full ${
                    cls.is_active
                      ? "bg-green-100 text-green-700"
                      : "bg-gray-100 text-gray-500"
                  }`}
                >
                  {cls.is_active ? "Active" : "Inactive"}
                </span>
              </div>
            ))}
          </div>
          {classes.length > 5 && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => router.push("/classes")}
              className="w-full text-muted-foreground"
            >
              View all {classes.length} classes
            </Button>
          )}
        </div>
      )}

    </div>
  );
}