"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  BookOpen,
  Users,
  MessageSquare,
  BarChart2,
  ClipboardList,
  GraduationCap,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useCurrentUser } from "@/hooks/useCurrentUser";

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

  const navItems = user?.role === "teacher" ? TEACHER_NAV : STUDENT_NAV;

  return (
    <aside className="flex flex-col w-64 h-screen border-r bg-background sticky top-0">

      {/* Logo */}
      <div className="flex items-center gap-2 px-6 py-5 border-b">
        <GraduationCap className="w-6 h-6 text-primary" />
        <span className="font-semibold text-base">AI Learning</span>
      </div>

      {/* Nav Items */}
      <nav className="flex-1 px-3 py-4 space-y-1">
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
              className={cn(
                "flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors",
                isActive
                  ? "bg-primary/10 text-primary font-medium"
                  : "text-muted-foreground hover:bg-muted hover:text-foreground"
              )}
            >
              <Icon className="w-4 h-4 shrink-0" />
              {item.label}
            </Link>
          );
        })}
      </nav>

      {/* User info */}
      {user && (
        <div className="px-4 py-4 border-t">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center shrink-0">
              <span className="text-xs font-medium text-primary">
                {user.full_name.charAt(0).toUpperCase()}
              </span>
            </div>
            <div className="overflow-hidden">
              <p className="text-sm font-medium truncate">{user.full_name}</p>
              <p className="text-xs text-muted-foreground capitalize">{user.role}</p>
            </div>
          </div>
        </div>
      )}
    </aside>
  );
}