"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useParams, useRouter } from "next/navigation";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { analyticsService } from "@/services/analytics.service";
import { Button } from "@/components/ui/button";
import { ArrowLeft, MessageSquare, ChevronDown, ChevronUp } from "lucide-react";
import { cn } from "@/lib/utils";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { ChatMessage } from "@/types/chat.types";

type ViewMode = "conversation" | "prompts";

function ViewToggle({
  mode,
  onChange,
}: {
  mode: ViewMode;
  onChange: (mode: ViewMode) => void;
}) {
  return (
    <div className="flex items-center bg-muted rounded-md p-0.5 gap-0.5">
      <button
        onClick={() => onChange("conversation")}
        className={cn(
          "px-3 py-1 rounded text-xs font-medium transition-colors",
          mode === "conversation"
            ? "bg-background text-foreground shadow-sm"
            : "text-muted-foreground hover:text-foreground"
        )}
      >
        Conversation
      </button>
      <button
        onClick={() => onChange("prompts")}
        className={cn(
          "px-3 py-1 rounded text-xs font-medium transition-colors",
          mode === "prompts"
            ? "bg-background text-foreground shadow-sm"
            : "text-muted-foreground hover:text-foreground"
        )}
      >
        Prompts
      </button>
    </div>
  );
}

function ConversationView({ messages }: { messages: ChatMessage[] }) {
  if (!messages.length) return (
    <p className="text-xs text-muted-foreground p-4 text-center">No messages.</p>
  );

  return (
    <div className="p-4 space-y-3 max-h-[420px] overflow-y-auto">
      {messages.map((msg, idx) => (
        <div
          key={idx}
          className={cn("flex", msg.role === "user" ? "justify-end" : "justify-start")}
        >
          <div
            className={cn(
              "max-w-[80%] rounded-xl px-3 py-2 text-sm",
              msg.role === "user"
                ? "bg-primary text-primary-foreground rounded-br-sm"
                : "bg-muted border rounded-bl-sm"
            )}
          >
            {msg.role === "assistant" ? (
              <div className="prose prose-sm dark:prose-invert max-w-none
                prose-p:my-0.5 prose-headings:my-1 prose-ul:my-0.5 prose-ol:my-0.5
                prose-li:my-0 prose-code:text-xs">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {msg.content}
                </ReactMarkdown>
              </div>
            ) : (
              <p className="whitespace-pre-wrap leading-relaxed">{msg.content}</p>
            )}
            <p className={cn(
              "text-xs mt-1 opacity-50",
              msg.role === "user" ? "text-right" : "text-left"
            )}>
              {msg.role === "user" ? "Student" : "AI"} · {new Date(msg.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
            </p>
          </div>
        </div>
      ))}
    </div>
  );
}

function PromptsView({ messages }: { messages: ChatMessage[] }) {
  const studentMessages = messages.filter((m) => m.role === "user");

  if (!studentMessages.length) return (
    <p className="text-xs text-muted-foreground p-4 text-center">No student prompts.</p>
  );

  return (
    <div className="p-4 space-y-2 max-h-[420px] overflow-y-auto">
      {studentMessages.map((msg, idx) => (
        <div key={idx} className="flex gap-3 items-start">
          <span className="text-xs font-mono text-muted-foreground bg-muted rounded px-1.5 py-0.5 shrink-0 mt-0.5">
            {idx + 1}
          </span>
          <div className="flex-1 border rounded-lg px-3 py-2 bg-background">
            <p className="text-sm whitespace-pre-wrap leading-relaxed">{msg.content}</p>
            <p className="text-xs text-muted-foreground mt-1">
              {new Date(msg.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
            </p>
          </div>
        </div>
      ))}
    </div>
  );
}

function SessionHistoryViewer({
  sessionId,
  viewMode,
}: {
  sessionId: string;
  viewMode: ViewMode;
}) {
  const { data: history, isLoading } = useQuery({
    queryKey: ["teacherSessionHistory", sessionId],
    queryFn: () => analyticsService.getSessionHistory(sessionId),
  });

  if (isLoading) return (
    <p className="text-xs text-muted-foreground p-4">Loading...</p>
  );

  if (!history?.messages?.length) return (
    <p className="text-xs text-muted-foreground p-4 text-center">No messages in this session.</p>
  );

  return viewMode === "conversation"
    ? <ConversationView messages={history.messages} />
    : <PromptsView messages={history.messages} />;
}

function SessionCard({ session }: { session: any }) {
  const [expanded, setExpanded] = useState(false);
  const [viewMode, setViewMode] = useState<ViewMode>("conversation");

  return (
    <div className="border rounded-lg overflow-hidden">
      <button
        className="w-full flex items-center justify-between p-3 hover:bg-muted/50 transition-colors text-left"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="space-y-0.5 flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span className={cn(
              "w-1.5 h-1.5 rounded-full shrink-0",
              session.is_active ? "bg-green-500" : "bg-gray-400"
            )} />
            <p className="text-sm font-medium truncate">
              {session.title ?? "Untitled session"}
            </p>
            <span className={cn(
              "text-xs px-1.5 py-0.5 rounded-full shrink-0",
              session.is_active ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-500"
            )}>
              {session.is_active ? "Active" : "Ended"}
            </span>
          </div>
          <p className="text-xs text-muted-foreground pl-3.5">
            {new Date(session.created_at).toLocaleString()}
            {session.ended_at && ` → ${new Date(session.ended_at).toLocaleString()}`}
          </p>
        </div>
        {expanded
          ? <ChevronUp className="w-4 h-4 text-muted-foreground shrink-0 ml-2" />
          : <ChevronDown className="w-4 h-4 text-muted-foreground shrink-0 ml-2" />
        }
      </button>

      {expanded && (
        <div className="border-t">
          <div className="flex items-center justify-between px-4 py-2 bg-muted/20 border-b">
            <p className="text-xs text-muted-foreground">
              {viewMode === "conversation"
                ? "Showing full conversation with AI responses"
                : "Showing student prompts only"}
            </p>
            <ViewToggle mode={viewMode} onChange={setViewMode} />
          </div>

          <SessionHistoryViewer sessionId={session.id} viewMode={viewMode} />
        </div>
      )}
    </div>
  );
}

const PROMPT_COLS = [
  { key: "direct_answer_pct", label: "Direct Answer" },
  { key: "explanation_pct", label: "Explanation" },
  { key: "step_by_step_pct", label: "Step-by-Step" },
  { key: "example_pct", label: "Example" },
  { key: "rewrite_pct", label: "Rewrite" },
  { key: "feedback_pct", label: "Feedback" },
  { key: "summary_pct", label: "Summary" },
  { key: "translation_pct", label: "Translation" },
  { key: "brainstorm_pct", label: "Brainstorm" },
];

export default function StudentAnalyticsDetailPage() {
  const { studentId } = useParams<{ studentId: string }>();
  const router = useRouter();
  const [taskFilter, setTaskFilter] = useState<string>("");

  const { data: sessions, isLoading: loadingSessions } = useQuery({
    queryKey: ["teacherStudentSessions", studentId],
    queryFn: () => analyticsService.getStudentSessions(studentId),
  });

  const { data: classifications } = useQuery({
    queryKey: ["studentClassifications", studentId],
    queryFn: () => analyticsService.getStudentClassifications(studentId),
  });

  const filteredSessions = sessions?.filter((s) =>
    taskFilter ? s.task_id === taskFilter : true
  ) ?? [];

  const uniqueTasks = sessions
    ? [...new Map(sessions.map((s) => [s.task_id, s.task_id])).entries()].map(([id]) => id)
    : [];

  return (
    <DashboardLayout title="Student Activity">
      <div className="space-y-6 max-w-4xl">
        <div className="flex items-center gap-3">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => router.push("/analytics")}
            className="text-muted-foreground"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to analytics
          </Button>
        </div>

        <div>
          <h2 className="text-2xl font-semibold">Student Activity</h2>
          <p className="text-xs text-muted-foreground font-mono mt-1">ID: {studentId}</p>
        </div>

        {classifications && classifications.length > 0 && (
          <div className="space-y-2">
            <h3 className="font-medium text-sm">Prompt Type Summary</h3>
            <div className="border rounded-lg overflow-x-auto">
              <table className="w-full text-xs">
                <thead className="bg-muted/50">
                  <tr>
                    <th className="text-right px-3 py-2.5 font-medium text-muted-foreground">Total</th>
                    {PROMPT_COLS.map((col) => (
                      <th key={col.key} className="text-right px-3 py-2.5 font-medium text-muted-foreground whitespace-nowrap">
                        {col.label}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {classifications.map((row, idx) => (
                    <tr key={idx}>
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
        )}

        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="font-medium">Sessions ({filteredSessions.length})</h3>
            {uniqueTasks.length > 1 && (
              <select
                value={taskFilter}
                onChange={(e) => setTaskFilter(e.target.value)}
                className="border rounded-md px-2 py-1 text-xs bg-background"
              >
                <option value="">All tasks</option>
                {uniqueTasks.map((taskId) => (
                  <option key={taskId} value={taskId}>
                    Task: {taskId.slice(0, 8)}...
                  </option>
                ))}
              </select>
            )}
          </div>

          {loadingSessions ? (
            <p className="text-muted-foreground text-sm">Loading sessions...</p>
          ) : !filteredSessions.length ? (
            <div className="flex flex-col items-center justify-center py-12 text-center border rounded-lg">
              <MessageSquare className="w-8 h-8 text-muted-foreground mb-2" />
              <p className="text-sm font-medium">No sessions found</p>
            </div>
          ) : (
            <div className="space-y-2">
              {filteredSessions.map((session) => (
                <SessionCard key={session.id} session={session} />
              ))}
            </div>
          )}
        </div>

      </div>
    </DashboardLayout>
  );
}