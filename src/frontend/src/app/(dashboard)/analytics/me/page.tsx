"use client";

import { useQuery } from "@tanstack/react-query";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { analyticsService } from "@/services/analytics.service";
import { StatCard } from "@/components/dashboard/StatCard";
import { MessageSquare, Zap, Clock, TrendingUp } from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";

function formatDuration(seconds: number): string {
  if (seconds < 60) return `${seconds}s`;
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m`;
  const hours = Math.floor(minutes / 60);
  return `${hours}h ${minutes % 60}m`;
}

const PROMPT_TYPES = [
  { key: "direct_answer_pct", label: "Direct Answer", color: "#6366f1" },
  { key: "explanation_pct", label: "Explanation", color: "#8b5cf6" },
  { key: "step_by_step_pct", label: "Step-by-Step", color: "#a78bfa" },
  { key: "example_pct", label: "Example", color: "#c4b5fd" },
  { key: "rewrite_pct", label: "Rewrite", color: "#7c3aed" },
  { key: "feedback_pct", label: "Feedback", color: "#5b21b6" },
  { key: "summary_pct", label: "Summary", color: "#4c1d95" },
  { key: "translation_pct", label: "Translation", color: "#ddd6fe" },
  { key: "brainstorm_pct", label: "Brainstorm", color: "#ede9fe" },
];

export default function MyAnalyticsPage() {
  const { data: analytics, isLoading: loadingAnalytics } = useQuery({
    queryKey: ["myAnalytics"],
    queryFn: () => analyticsService.getMyAnalytics(),
  });

  const { data: classification, isLoading: loadingClassification } = useQuery({
    queryKey: ["myClassifications"],
    queryFn: () => analyticsService.getMyClassifications(),
  });

  const chartData = classification
    ? PROMPT_TYPES.map((pt) => ({
        name: pt.label,
        value: (classification as any)[pt.key] ?? 0,
        color: pt.color,
      })).filter((d) => d.value > 0)
    : [];

  return (
    <DashboardLayout title="My Analytics">
      <div className="space-y-6">

        <div>
          <h2 className="text-2xl font-semibold">My Analytics</h2>
          <p className="text-muted-foreground text-sm mt-1">
            Your AI prompting activity and progress
          </p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard title="Total Sessions" value={loadingAnalytics ? "—" : (analytics?.total_sessions ?? 0)} description="Completed sessions" icon={MessageSquare} />
          <StatCard title="Total Prompts" value={loadingAnalytics ? "—" : (analytics?.total_prompts ?? 0)} description="Messages sent" icon={TrendingUp} />
          <StatCard title="Tokens Used" value={loadingAnalytics ? "—" : (analytics?.total_tokens ?? 0).toLocaleString()} description="LLM tokens" icon={Zap} />
          <StatCard title="Learning Time" value={loadingAnalytics ? "—" : formatDuration(analytics?.total_duration_seconds ?? 0)} description="Active chat time" icon={Clock} />
        </div>

        {/* Prompt Classification */}
        {!loadingClassification && classification && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

            {/* Chart */}
            <div className="border rounded-lg p-5 space-y-3">
              <p className="font-medium">Prompt Type Distribution</p>
              <p className="text-xs text-muted-foreground">
                Based on {classification.total_prompts} prompts
              </p>
              <ResponsiveContainer width="100%" height={240}>
                <BarChart data={chartData} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                  <XAxis type="number" domain={[0, 100]} tickFormatter={(v) => `${v}%`} tick={{ fontSize: 11 }} />
                  <YAxis type="category" dataKey="name" tick={{ fontSize: 11 }} width={90} />
                  <Tooltip formatter={(v: any) => `${v}%`} />
                  <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                    {chartData.map((entry, idx) => (
                      <Cell key={idx} fill={entry.color} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Table */}
            <div className="border rounded-lg overflow-hidden">
              <table className="w-full text-sm">
                <thead className="bg-muted/50">
                  <tr>
                    <th className="text-left px-4 py-3 font-medium text-muted-foreground">Prompt Type</th>
                    <th className="text-right px-4 py-3 font-medium text-muted-foreground">%</th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {[
                    { key: "direct_answer_pct", label: "Direct Answer"},
                    { key: "explanation_pct", label: "Explanation"},
                    { key: "step_by_step_pct", label: "Step-by-Step" },
                    { key: "example_pct", label: "Example" },
                    { key: "rewrite_pct", label: "Rewrite" },
                    { key: "feedback_pct", label: "Feedback" },
                    { key: "summary_pct", label: "Summary" },
                    { key: "translation_pct", label: "Translation"},
                    { key: "brainstorm_pct", label: "Brainstorm"},
                  ].map((row) => (
                    <tr key={row.key} className="hover:bg-muted/30">
                      <td className="px-4 py-2.5 font-medium">{row.label}</td>
                      <td className="px-4 py-2.5 text-right font-mono">
                        {((classification as any)[row.key] ?? 0).toFixed(1)}%
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

          </div>
        )}

        {!loadingClassification && !classification && (
          <div className="border rounded-lg p-8 text-center">
            <p className="text-muted-foreground text-sm">
              No classification data yet. Start chatting to see your prompt type distribution.
            </p>
          </div>
        )}

        {/* Token breakdown */}
        {analytics && analytics.total_tokens > 0 && (
          <div className="border rounded-lg p-5 space-y-2">
            <p className="text-sm font-medium">Token breakdown</p>
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
        )}

      </div>
    </DashboardLayout>
  );
}