import { Button } from "@/components/ui/button";
import type { RunType, RunSource } from "@/lib/api";
import type { TimePeriodType } from "@/lib/timePeriods";
import { RecentRunsTimePeriodSelector } from "@/components/TimePeriodSelector";

export interface RunFilters {
  source: RunSource | "all";
  type: RunType | "all";
  timePeriod: TimePeriodType;
}

interface RunsFilterBarProps {
  filters: RunFilters;
  onFiltersChange: (filters: RunFilters) => void;
  className?: string;
}

export function RunsFilterBar({ filters, onFiltersChange, className }: RunsFilterBarProps) {
  const updateFilter = <K extends keyof RunFilters>(key: K, value: RunFilters[K]) => {
    onFiltersChange({ ...filters, [key]: value });
  };

  return (
    <div className={`flex flex-wrap gap-4 items-center ${className || ""}`}>
      {/* Source Filter */}
      <div className="flex gap-1">
        <Button
          variant={filters.source === "all" ? "default" : "outline"}
          size="sm"
          onClick={() => updateFilter("source", "all")}
        >
          All Sources
        </Button>
        <Button
          variant={filters.source === "Strava" ? "default" : "outline"}
          size="sm"
          onClick={() => updateFilter("source", "Strava")}
        >
          Strava
        </Button>
        <Button
          variant={filters.source === "MapMyFitness" ? "default" : "outline"}
          size="sm"
          onClick={() => updateFilter("source", "MapMyFitness")}
        >
          MMF
        </Button>
      </div>

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

      {/* Time Period Filter */}
      <RecentRunsTimePeriodSelector
        selectedPeriod={filters.timePeriod}
        onPeriodChange={(period) => updateFilter("timePeriod", period)}
      />
    </div>
  );
}