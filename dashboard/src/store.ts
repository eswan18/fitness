// store.ts
import { create } from "zustand";
import type { TimePeriodType, TimePeriodOption } from "@/lib/timePeriods";
import {
  getTimePeriodOptions,
  getTimePeriodById,
  getDaysAgo,
  getToday,
} from "@/lib/timePeriods";

// Legacy type for backward compatibility during migration
export type RangePreset =
  | "14 Days"
  | "30 Days"
  | "1 Year"
  | "All Time"
  | "Custom";

type DashboardState = {
  timeRangeStart: Date;
  setTimeRangeStart: (date: Date) => void;
  timeRangeEnd: Date;
  setTimeRangeEnd: (date: Date) => void;
  selectedTimePeriod: TimePeriodType;
  setSelectedTimePeriod: (period: TimePeriodType) => void;
  // Method to set time period and automatically update start/end dates
  selectTimePeriod: (period: TimePeriodType) => void;
};

// Initialize store with migration support
function getInitialTimePeriod(): TimePeriodType {
  // Check if there's a legacy selectedRangePreset in localStorage (if any)
  try {
    const stored = localStorage.getItem("dashboard-store");
    if (stored) {
      const parsed = JSON.parse(stored);
      if (parsed.state?.selectedRangePreset) {
        // Import migration function
        const { migrateRangePreset } = require("@/lib/timePeriods");
        return migrateRangePreset(parsed.state.selectedRangePreset);
      }
    }
  } catch (error) {
    console.warn("Error migrating legacy time period setting:", error);
  }

  // Default to 30 days
  return "30_days";
}

// Initialize with migrated or default period
const initialTimePeriod = getInitialTimePeriod();
const defaultPeriod = getTimePeriodById(initialTimePeriod)!;

export const useDashboardStore = create<DashboardState>((set) => ({
  timeRangeStart: defaultPeriod.start!,
  setTimeRangeStart: (date) => set({ timeRangeStart: date }),

  timeRangeEnd: defaultPeriod.end!,
  setTimeRangeEnd: (date) => set({ timeRangeEnd: date }),

  selectedTimePeriod: initialTimePeriod,
  setSelectedTimePeriod: (period) => set({ selectedTimePeriod: period }),

  selectTimePeriod: (period) => {
    const option = getTimePeriodById(period);
    if (!option) return;

    set({
      selectedTimePeriod: period,
      // Only update dates if they're defined (not custom)
      ...(option.start &&
        option.end && {
          timeRangeStart: option.start,
          timeRangeEnd: option.end,
        }),
    });
  },
}));

// Updated interface for new time period system
export interface TimePeriodWithDates extends TimePeriodOption {
  // Inherits id, label, start, end from TimePeriodOption
}

/**
 * Hook to get all time period options with current dates
 * Replaces the old useRangePresets hook
 */
export function useTimePeriodOptions(): TimePeriodWithDates[] {
  return getTimePeriodOptions();
}

/**
 * Legacy compatibility hook - will be removed after migration
 * @deprecated Use useTimePeriodOptions instead
 */
export function useRangePresets(): {
  label: RangePreset;
  start: Date | undefined;
  end: Date | undefined;
}[] {
  const today = getToday();
  const ago14Days = getDaysAgo(14);
  const ago30Days = getDaysAgo(30);
  const ago1Year = getDaysAgo(365);
  const allTimeStart = new Date(2016, 0, 1);

  return [
    { label: "14 Days", start: ago14Days, end: today },
    { label: "30 Days", start: ago30Days, end: today },
    { label: "1 Year", start: ago1Year, end: today },
    { label: "All Time", start: allTimeStart, end: today },
    { label: "Custom", start: undefined, end: undefined },
  ];
}
