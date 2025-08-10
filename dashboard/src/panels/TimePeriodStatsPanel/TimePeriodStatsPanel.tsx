import { SummaryBox } from "@/components/SummaryBox";
import { daysInRange } from "@/lib/utils";
import { useDashboardStore } from "@/store";
import { useQuery } from "@tanstack/react-query";
import {
  fetchDayMileage,
  fetchDayTrainingLoad,
  fetchDayTrimp,
  fetchRollingDayMileage,
  fetchTotalMileage,
} from "@/lib/api";
import type { DayMileage, DayTrainingLoad, DayTrimp } from "@/lib/api";
import { getUserTimezone } from "@/lib/timezone";
import { DateRangePickerPanel } from "@/components/DateRangePickerPanel";
import { DailyTrimpChart } from "./DailyTrimpChart";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { FreshnessChart } from "./FreshnessChart";
import { StandardTimePeriodSelector } from "@/components/TimePeriodSelector";
import { isCustomTimePeriod } from "@/lib/timePeriods";
import { queryKeys } from "@/lib/queryKeys";
import { Panel } from "@/components/Panel";

export function TimePeriodStatsPanel({ className }: { className?: string }) {
  const {
    timeRangeStart,
    timeRangeEnd,
    selectedTimePeriod,
    selectTimePeriod,
    setTimeRangeStart,
    setTimeRangeEnd,
  } = useDashboardStore();
  const { miles, dayTrainingLoad, dayTrimp, isPending, error } =
    useTimePeriodStats();

  if (isPending || error) {
    return (
      <Panel
        title="Time Period"
        className={className}
        isLoading={isPending}
        error={error}
      >
        {null}
      </Panel>
    );
  }

  const dayCount = daysInRange(timeRangeStart, timeRangeEnd);

  // Prepare daily TRIMP data
  const dailyTrimpData = dayTrimp.map((d: DayTrimp) => ({
    date: d.date,
    trimp: d.trimp,
  }));

  return (
    <Panel title="Time Period" className={className} bodyClassName="gap-y-6">
      <StandardTimePeriodSelector
        selectedPeriod={selectedTimePeriod}
        onPeriodChange={selectTimePeriod}
        className="flex-wrap"
      />
      <DateRangePickerPanel
        disabled={!isCustomTimePeriod(selectedTimePeriod)}
        startDate={timeRangeStart}
        endDate={timeRangeEnd}
        onStartChange={setTimeRangeStart}
        onEndChange={setTimeRangeEnd}
      />
      <div className="flex flex-row w-full gap-x-6">
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
          <TabsTrigger value="load">Freshness</TabsTrigger>
          <TabsTrigger value="miles">Daily Load</TabsTrigger>
        </TabsList>
        <TabsContent value="load">
          <FreshnessChart data={dayTrainingLoad} />
        </TabsContent>
        <TabsContent value="miles">
          <DailyTrimpChart data={dailyTrimpData} />
        </TabsContent>
      </Tabs>
    </Panel>
  );
}

type TimePeriodStatsResult =
  | {
      miles: undefined;
      dailyMiles: undefined;
      rollingMiles: undefined;
      dayTrainingLoad: undefined;
      dayTrimp: undefined;
      isPending: true;
      error: null;
    }
  | {
      miles: number;
      dailyMiles: DayMileage[];
      rollingMiles: DayMileage[];
      dayTrainingLoad: DayTrainingLoad[];
      dayTrimp: DayTrimp[];
      isPending: false;
      error: null;
    }
  | {
      miles: undefined;
      dailyMiles: undefined;
      rollingMiles: undefined;
      dayTrainingLoad: undefined;
      dayTrimp: undefined;
      isPending: false;
      error: Error;
    };

function useTimePeriodStats(): TimePeriodStatsResult {
  const store = useDashboardStore();
  const { timeRangeStart, timeRangeEnd } = store;
  const userTimezone = getUserTimezone();

  const milesQueryResult = useQuery({
    queryKey: queryKeys.totalMiles({
      startDate: timeRangeStart,
      endDate: timeRangeEnd,
      userTimezone,
    }),
    queryFn: () =>
      fetchTotalMileage({
        startDate: timeRangeStart,
        endDate: timeRangeEnd,
        userTimezone,
      }),
  });
  const dailyMilesQueryResult = useQuery({
    queryKey: queryKeys.milesByDay({
      startDate: timeRangeStart,
      endDate: timeRangeEnd,
      userTimezone,
    }),
    queryFn: () =>
      fetchDayMileage({
        startDate: timeRangeStart,
        endDate: timeRangeEnd,
        userTimezone,
      }),
  });
  const rollingMilesQueryResult = useQuery({
    queryKey: queryKeys.rollingMiles({
      startDate: timeRangeStart,
      endDate: timeRangeEnd,
      window: 7,
      userTimezone,
    }),
    queryFn: () =>
      fetchRollingDayMileage({
        startDate: timeRangeStart,
        endDate: timeRangeEnd,
        window: 7,
        userTimezone,
      }),
  });
  const dayTrainingLoadQuery = useQuery({
    queryKey: queryKeys.trainingLoadByDay({
      startDate: timeRangeStart,
      endDate: timeRangeEnd,
      maxHr: 192,
      restingHr: 42,
      sex: "M",
      userTimezone,
    }),
    queryFn: () =>
      fetchDayTrainingLoad({
        startDate: timeRangeStart,
        endDate: timeRangeEnd,
        maxHr: 192,
        restingHr: 42,
        sex: "M",
        userTimezone,
      }),
  });

  const dayTrimpQuery = useQuery({
    queryKey: queryKeys.dayTrimp({
      startDate: timeRangeStart,
      endDate: timeRangeEnd,
      userTimezone,
    }),
    queryFn: () => fetchDayTrimp(timeRangeStart, timeRangeEnd, userTimezone),
  });
  if (
    dailyMilesQueryResult.isPending ||
    milesQueryResult.isPending ||
    rollingMilesQueryResult.isPending ||
    dayTrainingLoadQuery.isPending ||
    dayTrimpQuery.isPending
  ) {
    return {
      miles: undefined,
      dailyMiles: undefined,
      rollingMiles: undefined,
      dayTrainingLoad: undefined,
      dayTrimp: undefined,
      isPending: true,
      error: null,
    };
  }
  const error =
    dailyMilesQueryResult.error ??
    milesQueryResult.error ??
    rollingMilesQueryResult.error ??
    dayTrainingLoadQuery.error ??
    dayTrimpQuery.error;
  if (error) {
    return {
      dailyMiles: undefined,
      miles: undefined,
      rollingMiles: undefined,
      dayTrainingLoad: undefined,
      dayTrimp: undefined,
      isPending: false,
      error,
    };
  }
  return {
    dailyMiles: dailyMilesQueryResult.data!,
    miles: milesQueryResult.data!,
    rollingMiles: rollingMilesQueryResult.data!,
    dayTrainingLoad: dayTrainingLoadQuery.data!,
    dayTrimp: dayTrimpQuery.data!,
    isPending: false,
    error: null,
  };
}
