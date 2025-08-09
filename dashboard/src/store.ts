// store.ts
import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";
import type { TimePeriodType } from "@/lib/timePeriods";
import { getTimePeriodById, migrateRangePreset } from "@/lib/timePeriods";

type DashboardState = {
  timeRangeStart: Date;
  setTimeRangeStart: (date: Date) => void;
  timeRangeEnd: Date;
  setTimeRangeEnd: (date: Date) => void;
  selectedTimePeriod: TimePeriodType;
  setSelectedTimePeriod: (period: TimePeriodType) => void;
  selectTimePeriod: (period: TimePeriodType) => void;
};

// Defaults if nothing persisted
const defaultPeriod: TimePeriodType = "30_days";
const defaultOption = getTimePeriodById(defaultPeriod)!;

export const useDashboardStore = create<DashboardState>()(
  persist(
    (set) => ({
      timeRangeStart: defaultOption.start!,
      setTimeRangeStart: (date) => set({ timeRangeStart: date }),

      timeRangeEnd: defaultOption.end!,
      setTimeRangeEnd: (date) => set({ timeRangeEnd: date }),

      selectedTimePeriod: defaultPeriod,
      setSelectedTimePeriod: (period) => set({ selectedTimePeriod: period }),

      selectTimePeriod: (period) => {
        const option = getTimePeriodById(period);
        if (!option) return;

        set({
          selectedTimePeriod: period,
          ...(option.start && option.end && {
            timeRangeStart: option.start,
            timeRangeEnd: option.end,
          }),
        });
      },
    }),
    {
      name: "dashboard-store",
      version: 2,
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        selectedTimePeriod: state.selectedTimePeriod,
        timeRangeStart: state.timeRangeStart.toISOString(),
        timeRangeEnd: state.timeRangeEnd.toISOString(),
      }),
      migrate: (persisted) => {
        const ps = persisted as unknown as {
          state?: { selectedRangePreset?: string; selectedTimePeriod?: TimePeriodType };
        } | null;
        if (ps?.state?.selectedRangePreset && !ps.state.selectedTimePeriod) {
          ps.state.selectedTimePeriod = migrateRangePreset(ps.state.selectedRangePreset);
          delete ps.state.selectedRangePreset;
        }
        return persisted;
      },
      onRehydrateStorage: () => (state) => {
        if (!state) return;
        const s = state as unknown as {
          timeRangeStart: unknown;
          timeRangeEnd: unknown;
          selectedTimePeriod: TimePeriodType;
        };
        if (typeof s.timeRangeStart === "string") {
          const d = new Date(s.timeRangeStart);
          if (!isNaN(d.getTime())) (state as DashboardState).timeRangeStart = d;
        }
        if (typeof s.timeRangeEnd === "string") {
          const d = new Date(s.timeRangeEnd);
          if (!isNaN(d.getTime())) (state as DashboardState).timeRangeEnd = d;
        }
        const option = getTimePeriodById(s.selectedTimePeriod);
        if (option?.start && option?.end) {
          (state as DashboardState).timeRangeStart = option.start;
          (state as DashboardState).timeRangeEnd = option.end;
        }
      },
    },
  ),
);
