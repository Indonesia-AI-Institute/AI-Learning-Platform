import { describe, it, expect } from "bun:test";
import { cn } from "@/lib/utils";

describe("cn", () => {
  it("joins plain string classes", () => {
    expect(cn("a", "b", "c")).toBe("a b c");
  });

  it("drops falsy values", () => {
    expect(cn("a", false, null, undefined, "", 0, "b")).toBe("a b");
  });

  it("resolves conflicting Tailwind classes to the last one (tailwind-merge)", () => {
    expect(cn("px-2", "px-4")).toBe("px-4");
    expect(cn("text-red-500", "text-blue-500")).toBe("text-blue-500");
  });

  it("keeps non-conflicting classes from both sides", () => {
    expect(cn("px-2 py-1", "text-sm")).toBe("px-2 py-1 text-sm");
  });

  it("applies conditional classes via clsx object syntax", () => {
    expect(cn("base", { active: true, disabled: false })).toBe("base active");
  });

  it("flattens arrays of classes", () => {
    expect(cn(["a", "b"], "c")).toBe("a b c");
  });

  it("last conflicting class from a later conditional group wins", () => {
    // Mirrors a real usage pattern: a base style overridden by a
    // conditional variant class further down the className chain.
    expect(cn("bg-gray-100", true && "bg-red-500")).toBe("bg-red-500");
  });

  it("returns an empty string for no meaningful input", () => {
    expect(cn()).toBe("");
    expect(cn(false, null, undefined)).toBe("");
  });

  it("resolves conflicts within the same responsive variant scope", () => {
    // This app's grid layouts (StudentDashboard, TeacherDashboard) rely on
    // exactly this: a later sm:/lg:-prefixed class overriding an earlier
    // one at the *same* breakpoint.
    expect(cn("sm:grid-cols-2", "sm:grid-cols-4")).toBe("sm:grid-cols-4");
  });

  it("keeps classes at different responsive breakpoints — they are not the same slot", () => {
    expect(cn("grid-cols-1", "sm:grid-cols-2", "lg:grid-cols-4")).toBe(
      "grid-cols-1 sm:grid-cols-2 lg:grid-cols-4"
    );
  });

  it("resolves conflicts within the same pseudo-class variant (hover:, focus:)", () => {
    expect(cn("hover:bg-red-500", "hover:bg-blue-500")).toBe("hover:bg-blue-500");
  });

  it("does not treat a bare utility and its hover: variant as conflicting", () => {
    expect(cn("bg-red-500", "hover:bg-blue-500")).toBe("bg-red-500 hover:bg-blue-500");
  });

  it("resolves conflicts between arbitrary-value classes for the same property", () => {
    expect(cn("w-[100px]", "w-[200px]")).toBe("w-[200px]");
  });

  it("handles a realistic component pattern: base classes plus a caller override", () => {
    // Mirrors src/components/ui/input.tsx's own className={cn(baseClasses, className)}
    // pattern. px-2 and pr-10 are NOT fully-conflicting here — px-2 sets
    // both left and right padding, and pr-10 only overrides the right
    // side, so tailwind-merge correctly keeps both rather than dropping
    // px-2 entirely (dropping it would silently lose the left padding).
    const base = "h-7 w-full rounded-md border px-2 py-0.5 text-sm";
    expect(cn(base, "pr-10")).toBe("h-7 w-full rounded-md border px-2 py-0.5 text-sm pr-10");

    // A same-property override (both full x-axis padding) DOES fully
    // conflict and resolves to just the later class, as expected.
    expect(cn(base, "px-10")).toBe("h-7 w-full rounded-md border py-0.5 text-sm px-10");
  });

  it("flattens deeply nested arrays mixed with conditional objects", () => {
    expect(cn(["a", ["b", { c: true, d: false }]], "e")).toBe("a b c e");
  });
});
