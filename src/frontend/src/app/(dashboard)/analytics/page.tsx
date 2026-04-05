"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { classService } from "@/services/class.service";
import { courseService } from "@/services/course.service";
import { taskService } from "@/services/task.service";
import { analyticsService, PromptClassificationRow } from "@/services/analytics.service";
import { BarChart2, ChevronRight } from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";

type FilterLevel = "class" | "course" | "task";

const PROMPT_COLS = [
  { key: "direct_answer_pct", label: "Direct" },
  { key: "explanation_pct", label: "Explain" },
  { key: "step_by_step_pct", label: "Steps" },
  { key: "example_pct", label: "Example" },
  { key: "rewrite_pct", label: "Rewrite" },
  { key: "feedback_pct", label: "Feedback" },
  { key: "summary_pct", label: "Summary" },
  { key: "translation_pct", label: "Translate" },
  { key: "brainstorm_pct", label: "Brainstorm" },
];

function ClassificationTable({ data }: { data: PromptClassificationRow[] }) {
  if (!data.length) return (
    <p className="text-sm text-muted-foreground py-8 text-center">No data yet.</p>
  );

  // Chart data — average per prompt type across students
  const chartData = PROMPT_COLS.map((col) => ({
    name: col.label,
    avg: data.length
      ? Math.round(data.reduce((sum, row) => sum + ((row as any)[col.key] ?? 0), 0) / data.length)
      : 0,
  }));

  return (
    <div className="space-y-6">
      {/* Bar chart */}
      <div className="border rounded-lg p-4">
        <p className="text-sm font-medium mb-3">Average prompt distribution across {data.length} student(s)</p>
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} />
            <XAxis dataKey="name" tick={{ fontSize: 11 }} />
            <YAxis tickFormatter={(v) => `${v}%`} tick={{ fontSize: 11 }} />
            <Tooltip formatter={(v: any) => `${v}%`} />
            <Bar dataKey="avg" fill="#6366f1" radius={[4, 4, 0, 0]} name="Avg %" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Table */}
      <div className="border rounded-lg overflow-x-auto">
        <table className="w-full text-xs">
          <thead className="bg-muted/50">
            <tr>
              <th className="text-left px-3 py-3 font-medium text-muted-foreground whitespace-nowrap">Student ID</th>
              <th className="text-right px-3 py-3 font-medium text-muted-foreground">Prompts</th>
              {PROMPT_COLS.map((col) => (
                <th key={col.key} className="text-right px-3 py-3 font-medium text-muted-foreground whitespace-nowrap">
                  {col.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y">
            {data.map((row, idx) => (
              <tr key={idx} className="hover:bg-muted/30">
                <td className="px-3 py-2.5 font-mono text-muted-foreground">
                  {row.student_id ? row.student_id.slice(0, 8) + "..." : "—"}
                </td>
                <td className="px-3 py-2.5 text-right font-medium">{row.total_prompts}</td>
                {PROMPT_COLS.map((col) => (
                  <td key={col.key} className="px-3 py-2.5 text-right">
                    {((row as any)[col.key] ?? 0).toFixed(1)}%
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default function TeacherAnalyticsPage() {
  const [filterLevel, setFilterLevel] = useState<FilterLevel>("class");
  const [selectedId, setSelectedId] = useState<string | null>(null);

  const { data: classes } = useQuery({
    queryKey: ["myClasses"],
    queryFn: () => classService.getMyClasses(),
  });

  const { data: courses } = useQuery({
    queryKey: ["myCourses"],
    queryFn: () => courseService.getMyCourses(),
  });

  // For task filter we need a class selected first
  const { data: tasks } = useQuery({
    queryKey: ["tasksByClass", selectedId],
    queryFn: () => taskService.getTasksByClass(selectedId!),
    enabled: filterLevel === "task" && !!selectedId,
  });

  const { data: classificationData, isLoading } = useQuery({
    queryKey: ["classifications", filterLevel, selectedId],
    queryFn: async (): Promise<PromptClassificationRow[]> => {
      if (!selectedId) return [];
      if (filterLevel === "class") return analyticsService.getClassClassifications(selectedId);
      if (filterLevel === "course") return analyticsService.getCourseClassifications(selectedId);
      if (filterLevel === "task") return analyticsService.getTaskClassifications(selectedId);
      return [];
    },
    enabled: !!selectedId,
  });

  const filterItems =
    filterLevel === "class" ? classes :
    filterLevel === "course" ? courses :
    tasks ?? [];

  const getItemLabel = (item: any) =>
    item.name ?? item.title ?? item.id;

  return (
    <DashboardLayout title="Analytics">
      <div className="space-y-6">

        <div>
          <h2 className="text-2xl font-semibold">Analytics</h2>
          <p className="text-muted-foreground text-sm mt-1">
            Monitor student prompt behavior
          </p>
        </div>

        {/* Filter level tabs */}
        <div className="flex gap-2 border-b pb-3">
          {(["class", "course", "task"] as FilterLevel[]).map((level) => (
            <button
              key={level}
              onClick={() => { setFilterLevel(level); setSelectedId(null); }}
              className={`px-4 py-1.5 rounded-md text-sm capitalize transition-colors ${
                filterLevel === level
                  ? "bg-primary text-primary-foreground"
                  : "border hover:bg-muted"
              }`}
            >
              By {level}
            </button>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">

          {/* Selector list */}
          <div className="space-y-2">
            <p className="text-sm font-medium text-muted-foreground capitalize">
              Select {filterLevel}
            </p>
            {!filterItems?.length ? (
              <p className="text-xs text-muted-foreground">No {filterLevel}s found.</p>
            ) : (
              filterItems.map((item: any) => (
                <button
                  key={item.id}
                  onClick={() => setSelectedId(item.id)}
                  className={`w-full text-left border rounded-lg p-3 text-sm transition-colors hover:bg-muted/50 ${
                    selectedId === item.id ? "border-primary bg-primary/5" : ""
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-medium truncate">{getItemLabel(item)}</span>
                    <ChevronRight className="w-4 h-4 text-muted-foreground shrink-0" />
                  </div>
                </button>
              ))
            )}
          </div>

          {/* Analytics panel */}
          <div className="lg:col-span-3">
            {!selectedId ? (
              <div className="flex flex-col items-center justify-center py-16 text-center border rounded-lg h-full">
                <BarChart2 className="w-10 h-10 text-muted-foreground mb-3" />
                <p className="font-medium">Select a {filterLevel}</p>
                <p className="text-sm text-muted-foreground mt-1">
                  Choose from the list to view prompt analytics
                </p>
              </div>
            ) : isLoading ? (
              <p className="text-muted-foreground text-sm">Loading...</p>
            ) : (
              <ClassificationTable data={classificationData ?? []} />
            )}
          </div>

        </div>
      </div>
    </DashboardLayout>
  );
}