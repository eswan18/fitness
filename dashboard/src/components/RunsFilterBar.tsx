import { Button } from "@/components/ui/button";
import type { RunType, RunSource } from "@/lib/api";

export interface RunFilters {
  source: RunSource | "all";
  type: RunType | "all";
  dateRange: "7d" | "14d" | "30d" | "all";
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

      {/* Date Range Filter */}
      <div className="flex gap-1">
        <Button
          variant={filters.dateRange === "7d" ? "default" : "outline"}
          size="sm"
          onClick={() => updateFilter("dateRange", "7d")}
        >
          7 Days
        </Button>
        <Button
          variant={filters.dateRange === "14d" ? "default" : "outline"}
          size="sm"
          onClick={() => updateFilter("dateRange", "14d")}
        >
          14 Days
        </Button>
        <Button
          variant={filters.dateRange === "30d" ? "default" : "outline"}
          size="sm"
          onClick={() => updateFilter("dateRange", "30d")}
        >
          30 Days
        </Button>
        <Button
          variant={filters.dateRange === "all" ? "default" : "outline"}
          size="sm"
          onClick={() => updateFilter("dateRange", "all")}
        >
          All
        </Button>
      </div>
    </div>
  );
}