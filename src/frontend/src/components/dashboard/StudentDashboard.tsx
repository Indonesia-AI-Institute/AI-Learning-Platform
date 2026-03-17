"use client";

/**
 * StudentDashboard.tsx
 * ====================
 * Dashboard content for student role.
 */

import { useQuery } from "@tanstack/react-query";
import { MessageSquare, Zap, Clock, TrendingUp } from "lucide-react";
import { StatCard } from "@/components/dashboard/StatCard";
import { analyticsService } from "@/services/analytics.service";

function formatDuration(seconds: number): string {
  if (seconds < 60) return `${seconds}s`;
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m`;
  const hours = Math.floor(minutes / 60);
  return `${hours}h ${minutes % 60}m`;
}

export function StudentDashboard({ fullName }: { fullName: string }) {
  const { data: analytics, isLoading } = useQuery({
    queryKey: ["myAnalytics"],
    queryFn: () => analyticsService.getMyAnalytics(),
  });

  return (
    <div className="space-y-6">

      {/* Welcome */}
      <div>
        <h2 className="text-2xl font-semibold">Welcome back, {fullName} 👋</h2>
        <p className="text-muted-foreground mt-1">
          Track your AI learning progress below.
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Sessions"
          value={isLoading ? "—" : (analytics?.total_sessions ?? 0)}
          description="Chat sessions completed"
          icon={MessageSquare}
        />
        <StatCard
          title="Total Prompts"
          value={isLoading ? "—" : (analytics?.total_prompts ?? 0)}
          description="Messages sent to AI"
          icon={TrendingUp}
        />
        <StatCard
          title="Tokens Used"
          value={isLoading ? "—" : (analytics?.total_tokens ?? 0).toLocaleString()}
          description="Total LLM tokens consumed"
          icon={Zap}
        />
        <StatCard
          title="Learning Time"
          value={isLoading ? "—" : formatDuration(analytics?.total_duration_seconds ?? 0)}
          description="Total active chat duration"
          icon={Clock}
        />
      </div>

      {/* Avg prompt length */}
      {analytics && analytics.total_prompts > 0 && (
        <div className="rounded-lg border p-4 bg-muted/30">
          <p className="text-sm text-muted-foreground">Average prompt length</p>
          <p className="text-lg font-semibold mt-1">
            {analytics.avg_prompt_length.toFixed(0)} characters
          </p>
          <p className="text-xs text-muted-foreground mt-1">
            Longer prompts generally lead to better AI responses
          </p>
        </div>
      )}

    </div>
  );
}