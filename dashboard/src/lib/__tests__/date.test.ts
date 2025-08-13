import { describe, it, expect } from "vitest";
import { toLocalDateTimeInputValue } from "@/lib/date";

describe("toLocalDateTimeInputValue", () => {
  it("formats a valid date to yyyy-MM-dd'T'HH:mm", () => {
    const d = new Date(2025, 0, 2, 3, 4); // Jan 2, 2025 03:04 local time
    const s = toLocalDateTimeInputValue(d);
    expect(s).toBe("2025-01-02T03:04");
  });

  it("returns empty string for undefined", () => {
    expect(toLocalDateTimeInputValue(undefined)).toBe("");
  });

  it("returns empty string for invalid Date", () => {
    // @ts-expect-error intentionally pass invalid
    const invalid = new Date("this is not a date");
    expect(toLocalDateTimeInputValue(invalid)).toBe("");
  });
});
