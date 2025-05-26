import { SummaryBox } from "@/components/SummaryBox";
import { daysInRange } from "@/lib/utils";
import { useDashboardStore } from "@/store";
import { useQuery } from "@tanstack/react-query";
import {
  fetchDayMileage,
  fetchRollingDayMileage,
  fetchTotalMileage,
} from "@/lib/api";
import type { DayMileage } from "@/lib/api";
import { DatePickerPanel } from "./DatePickerPanel";
import { BurdenOverTimeChart } from "./BurdenOverTimechart";

export function TimePeriodStatsPanel({ className }: { className?: string }) {
  const { timeRangeStart, timeRangeEnd } = useDashboardStore();
  const { miles, dailyMiles, rollingMiles, isPending, error } = useTimePeriodStats();
  if (isPending) return <p>Loading...</p>;
  if (error) return <p>Error: {error.message}</p>;
  const dayCount = daysInRange(timeRangeStart, timeRangeEnd);

  return (
    <div className={`flex flex-col gap-y-4 ${className}`}>
      <h2 className="text-xl font-semibold">Time Period</h2>
      <DatePickerPanel />
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
    queryKey: ["miles", "by-day", {
      startDate: timeRangeStart,
      endDate: timeRangeEnd,
    }],
    queryFn: () =>
      fetchDayMileage({
        startDate: timeRangeStart,
        endDate: timeRangeEnd,
      }),
  });
  const rollingMilesQueryResult = useQuery({
    queryKey: ["miles", "rolling-by-day", {
      startDate: timeRangeStart,
      endDate: timeRangeEnd,
      window: 7,
    }],
    queryFn: () =>
      fetchRollingDayMileage({
        startDate: timeRangeStart,
        endDate: timeRangeEnd,
        window: 7,
      }),
  });
  if (
    dailyMilesQueryResult.isPending || milesQueryResult.isPending ||
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
  const error = dailyMilesQueryResult.error ?? milesQueryResult.error ??
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
