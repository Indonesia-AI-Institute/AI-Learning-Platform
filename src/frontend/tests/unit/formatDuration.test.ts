import { describe, it, expect } from "bun:test";
import { formatDuration } from "@/components/dashboard/StudentDashboard";

describe("formatDuration", () => {
  it("formats zero seconds", () => {
    expect(formatDuration(0)).toBe("0s");
  });

  it("formats sub-minute durations in seconds", () => {
    expect(formatDuration(1)).toBe("1s");
    expect(formatDuration(59)).toBe("59s");
  });

  it("switches to minutes at exactly 60 seconds", () => {
    expect(formatDuration(60)).toBe("1m");
  });

  it("floors partial minutes rather than rounding", () => {
    // 119s is 1m59s, not 2m — the seconds remainder is dropped, not rounded up.
    expect(formatDuration(119)).toBe("1m");
  });

  it("formats sub-hour durations in minutes", () => {
    expect(formatDuration(1800)).toBe("30m");
    expect(formatDuration(3599)).toBe("59m");
  });

  it("switches to hours+minutes at exactly 3600 seconds", () => {
    expect(formatDuration(3600)).toBe("1h 0m");
  });

  it("formats multi-hour durations with the remaining minutes", () => {
    expect(formatDuration(3725)).toBe("1h 2m"); // 1h 2m 5s — seconds dropped
    expect(formatDuration(7200)).toBe("2h 0m");
  });

  it("wraps the minutes remainder correctly across an hour boundary", () => {
    // 2h exactly plus 59 minutes: minutes % 60 must not leak the hour back in.
    expect(formatDuration(2 * 3600 + 59 * 60)).toBe("2h 59m");
  });

  it("handles a large multi-day duration without special-casing days", () => {
    // 25 hours — the function has no "days" tier, so this stays "25h Xm".
    expect(formatDuration(25 * 3600 + 15 * 60)).toBe("25h 15m");
  });
});
