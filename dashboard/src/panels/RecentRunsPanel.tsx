import { useState, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { fetchRuns } from "@/lib/api";
import { getUserTimezone } from "@/lib/timezone";
import { RunsTable } from "@/components/RunsTable";
import { LoadingSpinner } from "@/components/LoadingSpinner";
import { Card } from "@/components/ui/card";
import { RunsFilterBar, type RunFilters } from "@/components/RunsFilterBar";
import { isWithinTimePeriod } from "@/lib/runUtils";
import { isCustomTimePeriod, getDaysAgo, getToday, getTimePeriodById } from "@/lib/timePeriods";
import { DateRangePickerPanel } from "@/panels/TimePeriodStatsPanel/DateRangePanel";
import type { Run } from "@/lib/api";

interface RecentRunsPanelProps {
  className?: string;
}

export function RecentRunsPanel({ className }: RecentRunsPanelProps) {
  const userTimezone = getUserTimezone();
  const [filters, setFilters] = useState<RunFilters>({
    source: "all",
    type: "all",
    timePeriod: "7_days", // Default to 7 days
  });

  // Custom date range state for Recent Runs
  const [customStart, setCustomStart] = useState<Date>(getDaysAgo(7));
  const [customEnd, setCustomEnd] = useState<Date>(getToday());

  // Determine start/end for the selected time period
  let startDate: Date | undefined = undefined;
  let endDate: Date | undefined = undefined;
  if (filters.timePeriod === "custom") {
    startDate = customStart;
    endDate = customEnd;
  } else {
    const period = getTimePeriodById(filters.timePeriod);
    startDate = period?.start;
    endDate = period?.end;
  }

  const { data: allRuns, isPending, error } = useQuery({
    queryKey: [
      "recent-runs",
      userTimezone,
      filters.timePeriod,
      startDate?.toISOString(),
      endDate?.toISOString(),
    ],
    queryFn: () => fetchRuns({ startDate, endDate, userTimezone }),
    staleTime: 5 * 60 * 1000, // 5 minutes
    enabled: !!startDate && !!endDate,
  });

  // Apply source/type filters to the runs
  const filteredRuns = useMemo(() => {
    if (!allRuns) return [];
    return allRuns.filter((run: Run) => {
      // Source filter
      if (filters.source !== "all" && run.source !== filters.source) {
        return false;
      }
      // Type filter
      if (filters.type !== "all" && run.type !== filters.type) {
        return false;
      }
      return true;
    }).slice(0, 25); // Limit to 25 after filtering
  }, [allRuns, filters]);

  if (isPending) {
    return (
      <div className={`flex flex-col h-full gap-y-4 ${className}`}>
        <h2 className="text-xl font-semibold">Recent Runs</h2>
        <Card className="w-full shadow-none flex justify-center items-center flex-1">
          <LoadingSpinner />
        </Card>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`flex flex-col h-full gap-y-4 ${className}`}>
        <h2 className="text-xl font-semibold">Recent Runs</h2>
        <Card className="w-full shadow-none flex justify-center items-center flex-1">
          <p className="text-destructive">Error: {error.message}</p>
        </Card>
      </div>
    );
  }

  return (
    <div className={`flex flex-col min-h-full gap-y-4 ${className}`}>
      <div className="flex justify-between items-center flex-shrink-0">
        <h2 className="text-xl font-semibold">Recent Runs</h2>
        <span className="text-sm text-muted-foreground">
          {filteredRuns.length} runs
        </span>
      </div>
      
      <div className="flex-shrink-0">
        <div className="flex flex-wrap items-end gap-4 pb-2">
          <RunsFilterBar 
            filters={filters} 
            onFiltersChange={setFilters}
            className=""
          />
          {isCustomTimePeriod(filters.timePeriod) && (
            <DateRangePickerPanel 
              disabled={false}
              className="px-0"
              customStart={customStart}
              customEnd={customEnd}
              onCustomStartChange={setCustomStart}
              onCustomEndChange={setCustomEnd}
            />
          )}
        </div>
      </div>
      
      <Card className="w-full shadow-none p-0 overflow-hidden flex-1 min-h-[600px]">
        <RunsTable runs={filteredRuns} className="h-full" />
      </Card>
    </div>
  );
}