// store.ts
import { create } from "zustand";

const DEFAULT_START_DATE = new Date(2016, 0, 1); // January 1, 2016
const DEFAULT_END_DATE = new Date(); // Today

export type RangePreset = "This Month" | "This Year" | "All Time" | "Custom";

type DashboardState = {
  timeRangeStart: Date;
  setTimeRangeStart: (date: Date) => void;
  timeRangeEnd: Date;
  setTimeRangeEnd: (date: Date) => void;
  selectedRangePreset: RangePreset;
  setSelectedRangePreset: (preset: RangePreset) => void;
};

export const useDashboardStore = create<DashboardState>((set) => ({
  timeRangeStart: DEFAULT_START_DATE,
  setTimeRangeStart: (date) => set({ timeRangeStart: date }),

  timeRangeEnd: DEFAULT_END_DATE,
  setTimeRangeEnd: (date) => set({ timeRangeEnd: date }),

  selectedRangePreset: "This Month",
  setSelectedRangePreset: (preset) => set({ selectedRangePreset: preset }),
}));
