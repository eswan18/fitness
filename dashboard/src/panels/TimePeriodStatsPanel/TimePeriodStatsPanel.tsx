import { SummaryBox } from "@/components/SummaryBox";
import { daysInRange } from "@/lib/utils";
import { type RangePreset, useDashboardStore } from "@/store";
import { useQuery } from "@tanstack/react-query";
import {
  fetchDayMileage,
  fetchRollingDayMileage,
  fetchTotalMileage,
} from "@/lib/api";
import type { DayMileage } from "@/lib/api";
import { DateRangePickerPanel } from "./DateRangePanel";
import { BurdenOverTimeChart } from "./BurdenOverTimechart";
import { Button } from "@/components/ui/button";

export function TimePeriodStatsPanel({ className }: { className?: string }) {
  const {
    timeRangeStart,
    timeRangeEnd,
    selectedRangePreset,
    setSelectedRangePreset,
  } = useDashboardStore();
  const { miles, dailyMiles, rollingMiles, isPending, error } =
    useTimePeriodStats();
  const rangePresets = useRangePresets();
  if (isPending) return <p>Loading...</p>;
  if (error) return <p>Error: {error.message}</p>;
  const dayCount = daysInRange(timeRangeStart, timeRangeEnd);

  return (
    <div className={`flex flex-col gap-y-4 ${className}`}>
      <h2 className="text-xl font-semibold">Time Period</h2>
      <div className="flex flex-row w-full gap-x-4">
        {rangePresets.map((preset) => (
          <Button
            key={preset.label}
            variant={
              selectedRangePreset === preset.label ? "default" : "outline"
            }
            onClick={() => {
              setSelectedRangePreset(preset.label);
              if (preset.start && preset.end) {
                useDashboardStore.setState({
                  timeRangeStart: preset.start,
                  timeRangeEnd: preset.end,
                });
              }
            }}
          >
            {preset.label}
          </Button>
        ))}
      </div>
      <DateRangePickerPanel disabled={selectedRangePreset !== "Custom"} />
      <div className="flex flex-row w-full gap-x-4">
        <SummaryBox title="Days" value={dayCount} size="sm" />
        <SummaryBox
          title="Miles"
          value={Math.round(miles).toLocaleString()}
          size="sm"
        />
        <SummaryBox
          title="Miles/Day"
          value={dayCount > 0 ? (miles / dayCount).toFixed(2) : 0}
          size="sm"
        />
      </div>
      <BurdenOverTimeChart
        lineData={rollingMiles}
        title="Rolling Sum of Miles"
        lineLabel="Cumulative Miles"
        barData={dailyMiles}
        barLabel="Daily Miles"
      />
    </div>
  );
}

type TimePeriodStatsResult =
  | {
      miles: undefined;
      dailyMiles: undefined;
      rollingMiles: undefined;
      isPending: true;
      error: null;
    }
  | {
      miles: number;
      dailyMiles: DayMileage[];
      rollingMiles: DayMileage[];
      isPending: false;
      error: null;
    }
  | {
      miles: undefined;
      dailyMiles: undefined;
      rollingMiles: undefined;
      isPending: false;
      error: Error;
    };

function useTimePeriodStats(): TimePeriodStatsResult {
  const store = useDashboardStore();
  const { timeRangeStart, timeRangeEnd } = store;

  const milesQueryResult = useQuery({
    queryKey: [
      "miles",
      "total",
      {
        startDate: timeRangeStart,
        endDate: timeRangeEnd,
      },
    ],
    queryFn: () =>
      fetchTotalMileage({ startDate: timeRangeStart, endDate: timeRangeEnd }),
  });
  const dailyMilesQueryResult = useQuery({
    queryKey: [
      "miles",
      "by-day",
      {
        startDate: timeRangeStart,
        endDate: timeRangeEnd,
      },
    ],
    queryFn: () =>
      fetchDayMileage({
        startDate: timeRangeStart,
        endDate: timeRangeEnd,
      }),
  });
  const rollingMilesQueryResult = useQuery({
    queryKey: [
      "miles",
      "rolling-by-day",
      {
        startDate: timeRangeStart,
        endDate: timeRangeEnd,
        window: 7,
      },
    ],
    queryFn: () =>
      fetchRollingDayMileage({
        startDate: timeRangeStart,
        endDate: timeRangeEnd,
        window: 7,
      }),
  });
  if (
    dailyMilesQueryResult.isPending ||
    milesQueryResult.isPending ||
    rollingMilesQueryResult.isPending
  ) {
    return {
      miles: undefined,
      dailyMiles: undefined,
      rollingMiles: undefined,
      isPending: true,
      error: null,
    };
  }
  const error =
    dailyMilesQueryResult.error ??
    milesQueryResult.error ??
    rollingMilesQueryResult.error;
  if (error) {
    return {
      dailyMiles: undefined,
      miles: undefined,
      rollingMiles: undefined,
      isPending: false,
      error,
    };
  }
  return {
    dailyMiles: dailyMilesQueryResult.data!,
    miles: milesQueryResult.data!,
    rollingMiles: rollingMilesQueryResult.data!,
    isPending: false,
    error: null,
  };
}

interface RangePresetWithDates {
  label: RangePreset;
  start: Date | undefined;
  end: Date | undefined;
}

function useRangePresets(): RangePresetWithDates[] {
  const beginningOfThisMonth = new Date();
  beginningOfThisMonth.setDate(1);
  beginningOfThisMonth.setHours(0, 0, 0, 0);

  const beginningOfThisYear = new Date();
  beginningOfThisYear.setMonth(0, 1);
  beginningOfThisYear.setHours(0, 0, 0, 0);

  const allTimeStart = new Date(2016, 0, 1); // January 1, 2016
  const today = new Date(); // Today
  return [
    { label: "This Month", start: beginningOfThisMonth, end: today },
    { label: "This Year", start: beginningOfThisYear, end: today },
    { label: "All Time", start: allTimeStart, end: today },
    { label: "Custom", start: undefined, end: undefined },
  ];
}
