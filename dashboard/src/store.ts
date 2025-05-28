// store.ts
import { create } from "zustand";

export type RangePreset = "14 Days" | "30 Days" | "1 Year" | "All Time" | "Custom";

const today = new Date(); // Today
const ago7Days = new Date();
ago7Days.setDate(today.getDate() - 14);
ago7Days.setHours(0, 0, 0, 0);
const ago30Days = new Date();
ago30Days.setDate(today.getDate() - 30);
ago30Days.setHours(0, 0, 0, 0);
const ago1Year = new Date();
ago1Year.setFullYear(today.getFullYear() - 1);
ago1Year.setHours(0, 0, 0, 0);
const allTimeStart = new Date(2016, 0, 1); // January 1, 2016

type DashboardState = {
  timeRangeStart: Date;
  setTimeRangeStart: (date: Date) => void;
  timeRangeEnd: Date;
  setTimeRangeEnd: (date: Date) => void;
  selectedRangePreset: RangePreset;
  setSelectedRangePreset: (preset: RangePreset) => void;
};

export const useDashboardStore = create<DashboardState>((set) => ({
  timeRangeStart: ago30Days,
  setTimeRangeStart: (date) => set({ timeRangeStart: date }),

  timeRangeEnd: today,
  setTimeRangeEnd: (date) => set({ timeRangeEnd: date }),

  selectedRangePreset: "30 Days",
  setSelectedRangePreset: (preset) => set({ selectedRangePreset: preset }),
}));


export interface RangePresetWithDates {
  label: RangePreset;
  start: Date | undefined;
  end: Date | undefined;
}

export function useRangePresets(): RangePresetWithDates[] {
  return [
    { label: "14 Days", start: ago7Days, end: today },
    { label: "30 Days", start: ago30Days, end: today },
    { label: "1 Year", start: ago1Year, end: today },
    { label: "All Time", start: allTimeStart, end: today },
    { label: "Custom", start: undefined, end: undefined },
  ];
}