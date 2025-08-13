import { describe, it, expect, vi, beforeEach } from "vitest";
import type { QueryClient } from "@tanstack/react-query";
import {
  invalidateRuns,
  invalidateMetrics,
  invalidateShoes,
  invalidateEnvironment,
  invalidateAllDash,
} from "@/lib/invalidate";
import { queryKeys } from "@/lib/queryKeys";

describe("invalidate helpers", () => {
  let qc: QueryClient;
  let calls: Array<unknown>;

  beforeEach(() => {
    calls = [];
    // minimal mock for QueryClient
    qc = {
      invalidateQueries: vi.fn((args: unknown) => {
        calls.push(args);
        return Promise.resolve();
      }),
    } as unknown as QueryClient;
  });

  it("invalidates runs", async () => {
    await invalidateRuns(qc);
    expect(calls).toEqual([{ queryKey: queryKeys.group.runs() }]);
  });

  it("invalidates metrics bundle", async () => {
    await invalidateMetrics(qc);
    // Expect at least these calls; order matters as implemented
    expect(calls[0]).toEqual({ queryKey: queryKeys.totalMiles() });
    expect(calls[1]).toEqual({ queryKey: queryKeys.milesByDay() });
    expect(calls[2]).toEqual({ queryKey: queryKeys.rollingMiles({}) });
    expect(calls[3]).toEqual({ queryKey: queryKeys.dayTrimp({}) });
  });

  it("invalidates shoes", async () => {
    await invalidateShoes(qc);
    expect(calls).toEqual([
      { queryKey: queryKeys.shoesMileage(true) },
      { queryKey: queryKeys.shoesMileage(false) },
    ]);
  });

  it("invalidates environment", async () => {
    await invalidateEnvironment(qc);
    expect(calls).toEqual([{ queryKey: queryKeys.environment() }]);
  });

  it("invalidates all dashboard groups", async () => {
    await invalidateAllDash(qc);
    expect(calls.length).toBeGreaterThan(0);
  });
});
