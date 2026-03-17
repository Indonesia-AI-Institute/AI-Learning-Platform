"use client";

/**
 * Navbar.tsx
 * ==========
 * Top navigation bar with page title and logout button.
 */

import { useAuth } from "@/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { LogOut } from "lucide-react";

interface NavbarProps {
  title?: string;
}

export function Navbar({ title }: NavbarProps) {
  const { logout, isLogoutLoading } = useAuth();

  return (
    <header className="h-14 border-b bg-background flex items-center justify-between px-6 sticky top-0 z-10">

      {/* Page title */}
      <h1 className="text-sm font-medium text-muted-foreground">
        {title ?? "AI Learning Platform"}
      </h1>

      {/* Actions */}
      <Button
        variant="ghost"
        size="sm"
        onClick={() => logout()}
        disabled={isLogoutLoading}
        className="gap-2 text-muted-foreground"
      >
        <LogOut className="w-4 h-4" />
        {isLogoutLoading ? "Logging out..." : "Logout"}
      </Button>

    </header>
  );
}