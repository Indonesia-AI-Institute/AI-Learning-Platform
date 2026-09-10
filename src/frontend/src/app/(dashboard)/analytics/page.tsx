"use client";

import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { classService } from "@/services/class.service";
import { courseService } from "@/services/course.service";
import { taskService } from "@/services/task.service";
import { analyticsService, PromptClassificationRow } from "@/services/analytics.service";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { BarChart2, ChevronRight, Search, Eye } from "lucide-react";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer,
} from "recharts";

type FilterLevel = "course" | "class" | "task";

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

function ClassificationTable({
  data,
  onViewStudent,
  selectedTaskId,
}: {
  data: PromptClassificationRow[];
  onViewStudent: (studentId: string) => void;
  selectedTaskId?: string;
}) {
  const [search, setSearch] = useState("");

  const filtered = useMemo(() => {
    if (!search) return data;
    return data.filter((row) =>
      (row.student_id ?? "").toLowerCase().includes(search.toLowerCase())
    );
  }, [data, search]);

  if (!data.length) return (
    <p className="text-sm text-muted-foreground py-8 text-center">No data yet.</p>
  );

  const chartData = PROMPT_COLS.map((col) => ({
    name: col.label,
    avg: data.length
      ? Math.round(data.reduce((sum, row) => sum + ((row as any)[col.key] ?? 0), 0) / data.length)
      : 0,
  }));

  return (
    <div className="space-y-5">
      {/* Chart */}
      <div className="border rounded-lg p-4">
        <p className="text-sm font-medium mb-3">
          Average distribution — {data.length} student(s)
        </p>
        <ResponsiveContainer width="100%" height={180}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} />
            <XAxis dataKey="name" tick={{ fontSize: 11 }} />
            <YAxis tickFormatter={(v) => `${v}%`} tick={{ fontSize: 11 }} />
            <Tooltip formatter={(v: any) => `${v}%`} />
            <Bar dataKey="avg" fill="#6366f1" radius={[4, 4, 0, 0]} name="Avg %" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Search student */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
        <Input
          placeholder="Search by student ID..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="pl-9"
        />
      </div>

      {/* Table */}
      <div className="border rounded-lg overflow-x-auto">
        <table className="w-full text-xs">
          <thead className="bg-muted/50">
            <tr>
              <th className="text-left px-3 py-3 font-medium text-muted-foreground">Student</th>
              <th className="text-right px-3 py-3 font-medium text-muted-foreground">Prompts</th>
              {PROMPT_COLS.map((col) => (
                <th key={col.key} className="text-right px-3 py-3 font-medium text-muted-foreground whitespace-nowrap">
                  {col.label}
                </th>
              ))}
              <th className="text-center px-3 py-3 font-medium text-muted-foreground">Chat</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {filtered.map((row, idx) => (
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
                <td className="px-3 py-2.5 text-center">
                  {row.student_id && (
                    <Button
                      size="sm"
                      variant="ghost"
                      className="h-7 px-2"
                      onClick={() => onViewStudent(row.student_id!)}
                    >
                      <Eye className="w-3.5 h-3.5" />
                    </Button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default function TeacherAnalyticsPage() {
  const router = useRouter();
  const [filterLevel, setFilterLevel] = useState<FilterLevel>("class");
  const [selectedClassId, setSelectedClassId] = useState<string | null>(null);
  const [selectedCourseId, setSelectedCourseId] = useState<string | null>(null);
  const [selectedTaskId, setSelectedTaskId] = useState<string | null>(null);
  const [selectorSearch, setSelectorSearch] = useState("");

  const { data: classes } = useQuery({
    queryKey: ["myClasses"],
    queryFn: () => classService.getMyClasses(),
  });

  const { data: courses } = useQuery({
    queryKey: ["myCourses"],
    queryFn: () => courseService.getMyCourses(),
  });

  const { data: tasks } = useQuery({
    queryKey: ["tasksByClass", selectedClassId],
    queryFn: () => taskService.getTasksByClass(selectedClassId!),
    enabled: filterLevel === "task" && !!selectedClassId,
  });

  const activeId =
    filterLevel === "class" ? selectedClassId :
    filterLevel === "course" ? selectedCourseId :
    selectedTaskId;

  const { data: classificationData, isLoading } = useQuery({
    queryKey: ["classifications", filterLevel, activeId],
    queryFn: async (): Promise<PromptClassificationRow[]> => {
      if (!activeId) return [];
      if (filterLevel === "class") return analyticsService.getClassClassifications(activeId);
      if (filterLevel === "course") return analyticsService.getCourseClassifications(activeId);
      if (filterLevel === "task") return analyticsService.getTaskClassifications(activeId);
      return [];
    },
    enabled: !!activeId,
  });

  const allItems =
    filterLevel === "class" ? (classes ?? []) :
    filterLevel === "course" ? (courses ?? []) :
    (tasks ?? []);

  const filteredItems = useMemo(() => {
    if (!selectorSearch) return allItems;
    return allItems.filter((item: any) =>
      (item.name ?? item.title ?? "").toLowerCase().includes(selectorSearch.toLowerCase())
    );
  }, [allItems, selectorSearch]);

  const getItemLabel = (item: any) => item.name ?? item.title ?? item.id;

  const handleSelectItem = (id: string) => {
    if (filterLevel === "class") { setSelectedClassId(id); setSelectedTaskId(null); }
    else if (filterLevel === "course") { setSelectedCourseId(id); setSelectedTaskId(null); }
    else { setSelectedTaskId(id); }
  };

  const handleViewStudent = (studentId: string) => {
    router.push(`/analytics/student/${studentId}`);
  };

  const handleLevelChange = (level: FilterLevel) => {
    setFilterLevel(level);
    setSelectorSearch("");
    // Only reset the task pick — class/course selection stays so switching
    // back to "task" doesn't lose which class it was scoped to.
    if (level !== "task") setSelectedTaskId(null);
  };

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
          {(["course", "class", "task"] as FilterLevel[]).map((level) => (
            <button
              key={level}
              onClick={() => handleLevelChange(level)}
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

        {/* Task filter note */}
        {filterLevel === "task" && !selectedClassId && (
          <div className="rounded-lg border border-yellow-200 bg-yellow-50 p-3">
            <p className="text-sm text-yellow-800">
              Select a class first from the <strong>By Class</strong> tab, then switch back to By Task to filter tasks.
            </p>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">

          {/* Selector */}
          <div className="space-y-3">
            <p className="text-sm font-medium text-muted-foreground capitalize">
              Select {filterLevel}
            </p>

            {/* Search selector */}
            <div className="relative">
              <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-muted-foreground" />
              <Input
                placeholder={`Search ${filterLevel}...`}
                value={selectorSearch}
                onChange={(e) => setSelectorSearch(e.target.value)}
                className="pl-8 h-8 text-sm"
              />
            </div>

            {!filteredItems.length ? (
              <p className="text-xs text-muted-foreground">
                {filterLevel === "task" && !selectedClassId
                  ? "Select a class first"
                  : `No ${filterLevel}s found`}
              </p>
            ) : (
              <div className="space-y-1.5 max-h-[400px] overflow-y-auto">
                {filteredItems.map((item: any) => (
                  <button
                    key={item.id}
                    onClick={() => handleSelectItem(item.id)}
                    className={`w-full text-left border rounded-lg p-2.5 text-sm transition-colors hover:bg-muted/50 ${
                      activeId === item.id ? "border-primary bg-primary/5" : ""
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-medium truncate text-xs">{getItemLabel(item)}</span>
                      <ChevronRight className="w-3.5 h-3.5 text-muted-foreground shrink-0" />
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Analytics panel */}
          <div className="lg:col-span-3">
            {!activeId ? (
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
              <ClassificationTable
                data={classificationData ?? []}
                onViewStudent={handleViewStudent}
                selectedTaskId={selectedTaskId ?? undefined}
              />
            )}
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}