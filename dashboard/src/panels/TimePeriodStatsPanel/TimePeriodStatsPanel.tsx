import { SummaryBox } from "@/components/SummaryBox";
import { daysInRange } from "@/lib/utils";
import { useDashboardStore } from "@/store";
import { useQuery } from "@tanstack/react-query";
import { fetchRuns, fetchTotalMileage } from "@/lib/api";
import type { Run } from "@/lib/api";
import { DatePickerPanel } from "./DatePickerPanel";

export function TimePeriodStatsPanel({ className }: { className?: string }) {
  const { timeRangeStart, timeRangeEnd } = useDashboardStore();
  const { runs, miles, isPending, error } = useTimePeriodStats();
  if (isPending) return <p>Loading...</p>;
  if (error) return <p>Error: {error.message}</p>;
  const dayCount = daysInRange(timeRangeStart, timeRangeEnd);

  return (
    <div className={`flex flex-col gap-y-4 ${className}`}>
      <h2 className="text-xl font-semibold">Time Period</h2>
      <DatePickerPanel />
      <div className="flex flex-row w-full gap-x-4">
        <SummaryBox title="Days" value={dayCount} size="sm" />
        <SummaryBox title="Runs" value={runs.length} size="sm" />
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
    </div>
  );
}

type TimePeriodStatsResult =
  | {
    runs: undefined;
    miles: undefined;
    isPending: true;
    error: null;
  }
  | {
    runs: Run[];
    miles: number;
    isPending: false;
    error: null;
  }
  | {
    runs: undefined;
    miles: undefined;
    isPending: false;
    error: Error;
  };

function useTimePeriodStats(): TimePeriodStatsResult {
  const store = useDashboardStore();
  const { timeRangeStart, timeRangeEnd } = store;

  const runsQueryResult = useQuery({
    queryKey: ["runs", { startDate: timeRangeStart, endDate: timeRangeEnd }],
    queryFn: () =>
      fetchRuns({
        startDate: timeRangeStart,
        endDate: timeRangeEnd,
      }),
  });
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
  if (runsQueryResult.isPending || milesQueryResult.isPending) {
    return {
      runs: undefined,
      miles: undefined,
      isPending: true,
      error: null,
    };
  }
  const error = runsQueryResult.error ?? milesQueryResult.error;
  if (error) {
    return {
      runs: undefined,
      miles: undefined,
      isPending: false,
      error,
    };
  }
  return {
    runs: runsQueryResult.data!,
    miles: milesQueryResult.data!,
    isPending: false,
    error: null,
  };
}
