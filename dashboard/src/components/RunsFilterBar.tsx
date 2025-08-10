import { Button } from "@/components/ui/button";
import type { RunType } from "@/lib/api";
import type { TimePeriodType } from "@/lib/timePeriods";
import { RecentRunsTimePeriodSelector } from "@/components/TimePeriodSelector";

export interface RunFilters {
  type: RunType | "all";
  timePeriod: TimePeriodType;
  synced?: "all" | "synced" | "unsynced";
}

interface RunsFilterBarProps {
  filters: RunFilters;
  onFiltersChange: (filters: RunFilters) => void;
  className?: string;
}

export function RunsFilterBar({
  filters,
  onFiltersChange,
  className,
}: RunsFilterBarProps) {
  const updateFilter = <K extends keyof RunFilters>(
    key: K,
    value: RunFilters[K],
  ) => {
    onFiltersChange({ ...filters, [key]: value });
  };

  return (
    <div className={`flex flex-wrap gap-4 items-center ${className || ""}`}>
      {/* Type Filter */}
      <div className="flex gap-1">
        <Button
          variant={filters.type === "all" ? "default" : "outline"}
          size="sm"
          onClick={() => updateFilter("type", "all")}
        >
          All Types
        </Button>
        <Button
          variant={filters.type === "Outdoor Run" ? "default" : "outline"}
          size="sm"
          onClick={() => updateFilter("type", "Outdoor Run")}
        >
          Outdoor
        </Button>
        <Button
          variant={filters.type === "Treadmill Run" ? "default" : "outline"}
          size="sm"
          onClick={() => updateFilter("type", "Treadmill Run")}
        >
          Treadmill
        </Button>
      </div>

      {/* Synced Filter */}
      <div className="flex gap-1">
        <Button
          variant={(!filters.synced || filters.synced === "all") ? "default" : "outline"}
          size="sm"
          onClick={() => updateFilter("synced", "all")}
        >
          All
        </Button>
        <Button
          variant={filters.synced === "synced" ? "default" : "outline"}
          size="sm"
          onClick={() => updateFilter("synced", "synced")}
        >
          Synced
        </Button>
        <Button
          variant={filters.synced === "unsynced" ? "default" : "outline"}
          size="sm"
          onClick={() => updateFilter("synced", "unsynced")}
        >
          Unsynced
        </Button>
      </div>

      {/* Time Period Filter */}
      <RecentRunsTimePeriodSelector
        selectedPeriod={filters.timePeriod}
        onPeriodChange={(period) => updateFilter("timePeriod", period)}
      />
    </div>
  );
}
