import { useState, useMemo } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { fetchRunsWithShoes } from "@/lib/api";
import { getUserTimezone } from "@/lib/timezone";
import { RunsTable } from "@/components/RunsTable";
import { LoadingSpinner } from "@/components/LoadingSpinner";
import { Card } from "@/components/ui/card";
import { RunsFilterBar, type RunFilters } from "@/components/RunsFilterBar";
import {
  isCustomTimePeriod,
  getDaysAgo,
  getToday,
  getTimePeriodById,
} from "@/lib/timePeriods";
import { DateRangePickerPanel } from "@/components/DateRangePickerPanel";
import type { RunWithShoes, RunSortBy, SortOrder } from "@/lib/api";
import { queryKeys } from "@/lib/queryKeys";

interface RecentRunsPanelProps {
  className?: string;
}

export function RecentRunsPanel({ className }: RecentRunsPanelProps) {
  const userTimezone = getUserTimezone();
  const queryClient = useQueryClient();
  const [filters, setFilters] = useState<RunFilters>({
    source: "all",
    type: "all",
    timePeriod: "7_days", // Default to 7 days
  });

  // Custom date range state for Recent Runs
  const [customStart, setCustomStart] = useState<Date>(getDaysAgo(7));
  const [customEnd, setCustomEnd] = useState<Date>(getToday());

  // Sorting state
  const [sortBy, setSortBy] = useState<RunSortBy>("date");
  const [sortOrder, setSortOrder] = useState<SortOrder>("desc");

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

  const {
    data: allRuns,
    isPending,
    error,
  } = useQuery({
    queryKey: queryKeys.recentRuns({
      periodId: filters.timePeriod,
      startDate,
      endDate,
      userTimezone,
      sortBy,
      sortOrder,
    }),
    queryFn: () =>
      fetchRunsWithShoes({
        startDate,
        endDate,
        userTimezone,
        sortBy,
        sortOrder,
      }),
    staleTime: 5 * 60 * 1000, // 5 minutes
    enabled: !!startDate && !!endDate,
  });

  // Handle sorting when clicking table headers
  const handleSort = (newSortBy: RunSortBy) => {
    if (newSortBy === sortBy) {
      // Same column clicked, toggle order
      setSortOrder(sortOrder === "asc" ? "desc" : "asc");
    } else {
      // Different column clicked, set new sort field and default to desc for most fields
      setSortBy(newSortBy);
      // Default to ascending for text fields, descending for numeric fields
      const defaultAsc = ["source", "type", "shoes"].includes(newSortBy);
      setSortOrder(defaultAsc ? "asc" : "desc");
    }
  };

  // Apply source/type filters to the runs (sorting is now handled by backend)
  const filteredRuns = useMemo(() => {
    if (!allRuns) return [];
    return allRuns
      .filter((run: RunWithShoes) => {
        // Source filter
        if (filters.source !== "all" && run.source !== filters.source) {
          return false;
        }
        // Type filter
        if (filters.type !== "all" && run.type !== filters.type) {
          return false;
        }
        return true;
      })
      .slice(0, 25); // Limit to 25 after filtering
  }, [allRuns, filters]);

  const handleRunUpdated = () => {
    // Invalidate run queries to refresh data
    queryClient.invalidateQueries({ queryKey: ["recent-runs"] });
    // Also invalidate any other run-related queries
    queryClient.invalidateQueries({ queryKey: ["runs"] });
  };

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
          <p className="text-destructive">Error: {(error as Error).message}</p>
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
              startDate={customStart}
              endDate={customEnd}
              onStartChange={setCustomStart}
              onEndChange={setCustomEnd}
            />
          )}
        </div>
      </div>

      <Card className="w-full shadow-none p-0 overflow-hidden flex-1 min-h-[600px]">
        <RunsTable
          runs={filteredRuns}
          className="h-full"
          sortBy={sortBy}
          sortOrder={sortOrder}
          onSort={handleSort}
          onRunUpdated={handleRunUpdated}
        />
      </Card>
    </div>
  );
}
