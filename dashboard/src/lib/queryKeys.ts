import { toISODate } from "@/lib/date";
import type { SortOrder, RunSortBy, RunType } from "@/lib/api";

function normalizeRange(params: {
  startDate?: Date;
  endDate?: Date;
  userTimezone?: string;
}) {
  const { startDate, endDate, userTimezone } = params;
  return {
    startDate: startDate ? toISODate(startDate) : undefined,
    endDate: endDate ? toISODate(endDate) : undefined,
    userTimezone,
  };
}

export const queryKeys = {
  totalMiles: (
    params: { startDate?: Date; endDate?: Date; userTimezone?: string } = {},
  ) => ["miles", "total", normalizeRange(params)] as const,
  milesByDay: (
    params: { startDate?: Date; endDate?: Date; userTimezone?: string } = {},
  ) => ["miles", "by-day", normalizeRange(params)] as const,
  rollingMiles: (
    params: {
      startDate?: Date;
      endDate?: Date;
      window?: number;
      userTimezone?: string;
    } = {},
  ) =>
    [
      "metrics",
      "miles",
      "rolling-by-day",
      { ...normalizeRange(params), window: params.window },
    ] as const,
  trainingLoadByDay: (params: {
    startDate: Date;
    endDate: Date;
    maxHr: number;
    restingHr: number;
    sex: "M" | "F";
    userTimezone?: string;
  }) =>
    [
      "metrics",
      "trainingLoad",
      "by-day",
      {
        startDate: toISODate(params.startDate),
        endDate: toISODate(params.endDate),
        maxHr: params.maxHr,
        restingHr: params.restingHr,
        sex: params.sex,
        userTimezone: params.userTimezone,
      },
    ] as const,
  dayTrimp: (
    params: { startDate?: Date; endDate?: Date; userTimezone?: string } = {},
  ) =>
    [
      "day-trimp",
      toISODate(params.startDate),
      toISODate(params.endDate),
      params.userTimezone,
    ] as const,
  recentRuns: (params: {
    periodId: string;
    startDate?: Date;
    endDate?: Date;
    userTimezone?: string;
    sortBy: RunSortBy;
    sortOrder: SortOrder;
    synced?: "all" | "synced" | "unsynced";
  }) =>
    [
      "recent-runs",
      params.userTimezone,
      params.periodId,
      toISODate(params.startDate),
      toISODate(params.endDate),
      params.sortBy,
      params.sortOrder,
      params.synced ?? "all",
    ] as const,
  // Helper groups for invalidation convenience (not for useQuery)
  group: {
    runs: () => ["recent-runs"] as const,
    metrics: () => ["miles", "metrics", "day-trimp", "seconds"] as const,
    shoes: () => ["miles", "by-shoe", "shoes"] as const,
    environment: () => ["environment"] as const,
  },
  bulkSync: (params: {
    startDate?: Date;
    endDate?: Date;
    userTimezone?: string;
    typeFilter?: RunType | "all";
  }) =>
    [
      "bulk-sync",
      normalizeRange({
        startDate: params.startDate,
        endDate: params.endDate,
        userTimezone: params.userTimezone,
      }),
      params.typeFilter ?? "all",
    ] as const,
  shoesMileage: (includeRetired: boolean) =>
    [
      "miles",
      "by-shoe",
      includeRetired ? "include-retired" : "exclude-retired",
    ] as const,
  totalSeconds: (
    params: { startDate?: Date; endDate?: Date; userTimezone?: string } = {},
  ) => ["seconds", "total", normalizeRange(params)] as const,
  environment: () => ["environment"] as const,
  stravaAuthStatus: () => ["oauth", "strava", "status"] as const,
};
