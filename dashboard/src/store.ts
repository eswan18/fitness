// store.ts
import { create } from "zustand";
import type { TimePeriodType } from "@/lib/timePeriods";
import { getTimePeriodById, migrateRangePreset } from "@/lib/timePeriods";

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
        // Use migration function
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
const initialOption = getTimePeriodById(initialTimePeriod)!;

export const useDashboardStore = create<DashboardState>((set) => ({
  timeRangeStart: initialOption.start!,
  setTimeRangeStart: (date) => set({ timeRangeStart: date }),

  timeRangeEnd: initialOption.end!,
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
