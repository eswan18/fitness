import { describe, it, expect } from "vitest";
import { calculatePace, formatDuration } from "@/lib/runUtils";

describe("calculatePace", () => {
  it("rounds seconds and rolls over 60 to minutes", () => {
    // duration 480s over 1 mile => 8:00
    expect(calculatePace(1, 480)).toBe("8:00");
    // 7:59.6 should round to 8:00 (not 7:60)
    const duration = 7 * 60 + 59.6; // 479.6s
    expect(calculatePace(1, duration)).toBe("8:00");
  });
});

describe("formatDuration", () => {
  it("formats under an hour mm:ss with correct rounding", () => {
    expect(formatDuration(59 * 60 + 59)).toBe("59:59");
    // 59.6 seconds rounds to 1:00
    expect(formatDuration(60 - 0.4)).toBe("1:00");
  });

  it("formats hours as Xh Ym without rounding to invalid minutes", () => {
    // 3599.6 seconds ~ 59:59.6 should round to 1:00:00 -> shown as 1h 0m
    expect(formatDuration(3599.6)).toBe("1h 0m");
  });
});
