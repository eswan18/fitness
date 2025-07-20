import { useState, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { fetchRecentRuns } from "@/lib/api";
import { getUserTimezone } from "@/lib/timezone";
import { RunsTable } from "@/components/RunsTable";
import { LoadingSpinner } from "@/components/LoadingSpinner";
import { Card } from "@/components/ui/card";
import { RunsFilterBar, type RunFilters } from "@/components/RunsFilterBar";
import { isWithinDateRange } from "@/lib/runUtils";
import type { Run } from "@/lib/api";

interface RecentRunsPanelProps {
  className?: string;
}

export function RecentRunsPanel({ className }: RecentRunsPanelProps) {
  const userTimezone = getUserTimezone();
  const [filters, setFilters] = useState<RunFilters>({
    source: "all",
    type: "all",
    dateRange: "7d", // Default to 7 days
  });

  const { data: allRuns, isPending, error } = useQuery({
    queryKey: ["recent-runs", userTimezone],
    queryFn: () => fetchRecentRuns({ limit: 100, userTimezone }), // Get more runs for filtering
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  // Apply filters to the runs
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

      // Date range filter - use datetime if available, otherwise date
      const runDate = run.datetime || run.date;
      if (!isWithinDateRange(runDate, filters.dateRange)) {
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
    <div className={`flex flex-col h-full gap-y-4 ${className}`}>
      <div className="flex justify-between items-center flex-shrink-0">
        <h2 className="text-xl font-semibold">Recent Runs</h2>
        <span className="text-sm text-muted-foreground">
          {filteredRuns.length} runs
        </span>
      </div>
      
      <div className="flex-shrink-0">
        <RunsFilterBar 
          filters={filters} 
          onFiltersChange={setFilters}
          className="pb-2"
        />
      </div>
      
      <Card className="w-full shadow-none p-0 overflow-hidden flex-1 min-h-0">
        <RunsTable runs={filteredRuns} className="h-full" />
      </Card>
    </div>
  );
}