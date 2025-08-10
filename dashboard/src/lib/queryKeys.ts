import { toISODate } from "@/lib/date";
import type { SortOrder, RunSortBy } from "@/lib/api";

function normalizeRange(params: { startDate?: Date; endDate?: Date; userTimezone?: string }) {
  const { startDate, endDate, userTimezone } = params;
  return {
    startDate: startDate ? toISODate(startDate) : undefined,
    endDate: endDate ? toISODate(endDate) : undefined,
    userTimezone,
  };
}

export const queryKeys = {
  totalMiles: (params: { startDate?: Date; endDate?: Date; userTimezone?: string } = {}) => [
    "miles",
    "total",
    normalizeRange(params),
  ] as const,
  milesByDay: (params: { startDate?: Date; endDate?: Date; userTimezone?: string } = {}) => [
    "miles",
    "by-day",
    normalizeRange(params),
  ] as const,
  rollingMiles: (params: { startDate?: Date; endDate?: Date; window?: number; userTimezone?: string } = {}) => [
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
  }) => [
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
  dayTrimp: (params: { startDate?: Date; endDate?: Date; userTimezone?: string } = {}) => [
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
  }) => [
    "recent-runs",
    params.userTimezone,
    params.periodId,
    toISODate(params.startDate),
    toISODate(params.endDate),
    params.sortBy,
    params.sortOrder,
  ] as const,
  shoesMileage: (includeRetired: boolean) => [
    "miles",
    "by-shoe",
    includeRetired ? "include-retired" : "exclude-retired",
  ] as const,
  totalSeconds: (params: { startDate?: Date; endDate?: Date; userTimezone?: string } = {}) => [
    "seconds",
    "total",
    normalizeRange(params),
  ] as const,
  environment: () => ["environment"] as const,
};