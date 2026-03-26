"use client";

/**
 * app/(dashboard)/analytics/me/page.tsx
 * Student personal analytics
 */

import { useQuery } from "@tanstack/react-query";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { analyticsService } from "@/services/analytics.service";
import { StatCard } from "@/components/dashboard/StatCard";
import { MessageSquare, Zap, Clock, TrendingUp } from "lucide-react";

function formatDuration(seconds: number): string {
  if (seconds < 60) return `${seconds}s`;
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m`;
  const hours = Math.floor(minutes / 60);
  return `${hours}h ${minutes % 60}m`;
}

export default function MyAnalyticsPage() {
  const { data: analytics, isLoading } = useQuery({
    queryKey: ["myAnalytics"],
    queryFn: () => analyticsService.getMyAnalytics(),
  });

  return (
    <DashboardLayout title="My Analytics">
      <div className="space-y-6">

        <div>
          <h2 className="text-2xl font-semibold">My Analytics</h2>
          <p className="text-muted-foreground text-sm mt-1">
            Your AI prompting activity and progress
          </p>
        </div>

        {/* Stats grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            title="Total Sessions"
            value={isLoading ? "—" : (analytics?.total_sessions ?? 0)}
            description="Completed chat sessions"
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
            description="Total LLM tokens"
            icon={Zap}
          />
          <StatCard
            title="Learning Time"
            value={isLoading ? "—" : formatDuration(analytics?.total_duration_seconds ?? 0)}
            description="Total active chat time"
            icon={Clock}
          />
        </div>

        {/* Prompt quality */}
        {analytics && analytics.total_prompts > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">

            <div className="border rounded-lg p-5 space-y-2">
              <p className="text-sm text-muted-foreground">Avg prompt length</p>
              <p className="text-3xl font-semibold">
                {analytics.avg_prompt_length.toFixed(0)}
                <span className="text-base font-normal text-muted-foreground ml-1">chars</span>
              </p>
              <p className="text-xs text-muted-foreground">
                {analytics.avg_prompt_length < 50
                  ? "Try writing more detailed prompts for better AI responses"
                  : analytics.avg_prompt_length < 150
                  ? "Good prompt length — keep it up!"
                  : "Excellent! You write detailed, high-quality prompts"}
              </p>
            </div>

            <div className="border rounded-lg p-5 space-y-2">
              <p className="text-sm text-muted-foreground">Token breakdown</p>
              <div className="space-y-1.5">
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Input tokens</span>
                  <span className="font-medium">{analytics.total_prompt_tokens.toLocaleString()}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Output tokens</span>
                  <span className="font-medium">{analytics.total_completion_tokens.toLocaleString()}</span>
                </div>
                <div className="border-t pt-1.5 flex justify-between text-sm font-medium">
                  <span>Total</span>
                  <span>{analytics.total_tokens.toLocaleString()}</span>
                </div>
              </div>
            </div>

          </div>
        )}

        {analytics && analytics.last_active && (
          <p className="text-xs text-muted-foreground">
            Last active: {new Date(analytics.last_active).toLocaleString()}
          </p>
        )}

      </div>
    </DashboardLayout>
  );
}