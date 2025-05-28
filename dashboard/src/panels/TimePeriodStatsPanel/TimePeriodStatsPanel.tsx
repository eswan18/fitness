import { SummaryBox } from "@/components/SummaryBox";
import { daysInRange } from "@/lib/utils";
import { useDashboardStore, useRangePresets } from "@/store";
import { useQuery } from "@tanstack/react-query";
import {
  fetchDayMileage,
  fetchDayTrainingLoad,
  fetchRollingDayMileage,
  fetchTotalMileage,
} from "@/lib/api";
import type { DayMileage, DayTrainingLoad } from "@/lib/api";
import { DateRangePickerPanel } from "./DateRangePanel";
import { BurdenOverTimeChart } from "./BurdenOverTimechart";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

export function TimePeriodStatsPanel({ className }: { className?: string }) {
  const {
    timeRangeStart,
    timeRangeEnd,
    selectedRangePreset,
    setSelectedRangePreset,
  } = useDashboardStore();
  const { miles, dailyMiles, rollingMiles, dayTrainingLoad, isPending, error } =
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
            variant={selectedRangePreset === preset.label
              ? "default"
              : "outline"}
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
      <Tabs defaultValue="load" className="w-full mt-8">
        <TabsList className="w-full">
          <TabsTrigger value="load">Training Load</TabsTrigger>
          <TabsTrigger value="miles">Mileage</TabsTrigger>
        </TabsList>
        <TabsContent value="load">
          <BurdenOverTimeChart
            lineData={dayTrainingLoad.map((d) => ({
              date: d.date,
              score: d.training_load.tsb,
            }))}
            lineLabel="TSB"
          />
        </TabsContent>
        <TabsContent value="miles">
          <BurdenOverTimeChart
            lineData={rollingMiles.map((d) => ({
              date: d.date,
              score: d.mileage,
            }))}
            lineLabel="Cumulative Miles (7 days)"
            barData={dailyMiles.map((d) => ({
              date: d.date,
              score: d.mileage,
            }))}
            barLabel="Daily Miles"
          />
        </TabsContent>
      </Tabs>
    </div>
  );
}

type TimePeriodStatsResult =
  | {
    miles: undefined;
    dailyMiles: undefined;
    rollingMiles: undefined;
    dayTrainingLoad: undefined;
    isPending: true;
    error: null;
  }
  | {
    miles: number;
    dailyMiles: DayMileage[];
    rollingMiles: DayMileage[];
    dayTrainingLoad: DayTrainingLoad[];
    isPending: false;
    error: null;
  }
  | {
    miles: undefined;
    dailyMiles: undefined;
    rollingMiles: undefined;
    dayTrainingLoad: undefined;
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
      "metrics",
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
  const dayTrainingLoadQuery = useQuery({
    queryKey: [
      "metrics",
      "trainingLoad",
      "by-day",
      {
        startDate: timeRangeStart,
        endDate: timeRangeEnd,
        maxHr: 192,
        restingHr: 42,
        sex: "M",
      },
    ],
    queryFn: () =>
      fetchDayTrainingLoad({
        startDate: timeRangeStart,
        endDate: timeRangeEnd,
        maxHr: 192,
        restingHr: 42,
        sex: "M",
      }),
  });
  if (
    dailyMilesQueryResult.isPending ||
    milesQueryResult.isPending ||
    rollingMilesQueryResult.isPending ||
    dayTrainingLoadQuery.isPending
  ) {
    return {
      miles: undefined,
      dailyMiles: undefined,
      rollingMiles: undefined,
      dayTrainingLoad: undefined,
      isPending: true,
      error: null,
    };
  }
  const error = dailyMilesQueryResult.error ??
    milesQueryResult.error ??
    rollingMilesQueryResult.error;
  if (error) {
    return {
      dailyMiles: undefined,
      miles: undefined,
      rollingMiles: undefined,
      dayTrainingLoad: undefined,
      isPending: false,
      error,
    };
  }
  return {
    dailyMiles: dailyMilesQueryResult.data!,
    miles: milesQueryResult.data!,
    rollingMiles: rollingMilesQueryResult.data!,
    dayTrainingLoad: dayTrainingLoadQuery.data!,
    isPending: false,
    error: null,
  };
}
