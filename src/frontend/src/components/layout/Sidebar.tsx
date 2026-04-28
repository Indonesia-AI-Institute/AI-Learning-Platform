"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard, BookOpen, Users, MessageSquare,
  BarChart2, ClipboardList, GraduationCap, ChevronLeft, ChevronRight,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useCurrentUser } from "@/hooks/useCurrentUser";
import { useState } from "react";

const STUDENT_NAV = [
  { label: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { label: "Courses", href: "/courses", icon: BookOpen },
  { label: "My Classes", href: "/classes", icon: Users },
  { label: "Tasks", href: "/tasks", icon: ClipboardList },
  { label: "Chat", href: "/chat/sessions", icon: MessageSquare },
  { label: "Analytics", href: "/analytics/me", icon: BarChart2 },
];

const TEACHER_NAV = [
  { label: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { label: "Courses", href: "/courses", icon: BookOpen },
  { label: "Classes", href: "/classes", icon: Users },
  { label: "Tasks", href: "/tasks", icon: ClipboardList },
  { label: "Analytics", href: "/analytics", icon: BarChart2 },
];

export function Sidebar() {
  const pathname = usePathname();
  const { user } = useCurrentUser();
  const [collapsed, setCollapsed] = useState(false);

  const navItems = user?.role === "teacher" ? TEACHER_NAV : STUDENT_NAV;

  return (
    <aside
      className={cn(
        "flex flex-col h-screen border-r bg-background sticky top-0 transition-all duration-300",
        collapsed ? "w-16" : "w-64"
      )}
    >
      {/* Logo + collapse button */}
      <div className={cn(
        "flex items-center border-b h-14",
        collapsed ? "justify-center px-2" : "justify-between px-4"
      )}>
        {!collapsed && (
          <div className="flex items-center gap-2">
            <GraduationCap className="w-5 h-5 text-primary shrink-0" />
            <span className="font-semibold text-sm">AI Learning</span>
          </div>
        )}
        {collapsed && <GraduationCap className="w-5 h-5 text-primary" />}
        <button
          onClick={() => setCollapsed(!collapsed)}
          className={cn(
            "p-1 rounded-md hover:bg-muted transition-colors text-muted-foreground",
            collapsed && "mt-0"
          )}
          title={collapsed ? "Expand sidebar" : "Collapse sidebar"}
        >
          {collapsed
            ? <ChevronRight className="w-4 h-4" />
            : <ChevronLeft className="w-4 h-4" />
          }
        </button>
      </div>

      {/* Nav items */}
      <nav className="flex-1 px-2 py-3 space-y-1 overflow-hidden">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive =
            item.href === "/dashboard"
              ? pathname === item.href
              : pathname.startsWith(item.href);

          return (
            <Link
              key={item.href}
              href={item.href}
              title={collapsed ? item.label : undefined}
              className={cn(
                "flex items-center gap-3 rounded-md text-sm transition-colors",
                collapsed ? "justify-center px-2 py-2.5" : "px-3 py-2",
                isActive
                  ? "bg-primary/10 text-primary font-medium"
                  : "text-muted-foreground hover:bg-muted hover:text-foreground"
              )}
            >
              <Icon className="w-4 h-4 shrink-0" />
              {!collapsed && item.label}
            </Link>
          );
        })}
      </nav>

      {/* User info */}
      {user && (
        <div className={cn(
          "border-t",
          collapsed ? "px-2 py-3 flex justify-center" : "px-4 py-3"
        )}>
          <div className={cn(
            "flex items-center gap-3",
            collapsed && "justify-center"
          )}>
            <div
              className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center shrink-0"
              title={collapsed ? `${user.full_name} (${user.role})` : undefined}
            >
              <span className="text-xs font-medium text-primary">
                {user.full_name.charAt(0).toUpperCase()}
              </span>
            </div>
            {!collapsed && (
              <div className="overflow-hidden">
                <p className="text-sm font-medium truncate">{user.full_name}</p>
                <p className="text-xs text-muted-foreground capitalize">{user.role}</p>
              </div>
            )}
          </div>
        </div>
      )}
    </aside>
  );
}