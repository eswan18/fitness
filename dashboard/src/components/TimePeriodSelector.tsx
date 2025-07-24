import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuTrigger,
  DropdownMenuItem,
} from "@/components/ui/dropdown-menu";
import { ChevronDown } from "lucide-react";
import type { TimePeriodType } from "@/lib/timePeriods";
import {
  getButtonTimePeriods,
  getDropdownTimePeriods,
} from "@/lib/timePeriods";

interface TimePeriodSelectorProps {
  selectedPeriod: TimePeriodType;
  onPeriodChange: (period: TimePeriodType) => void;
  className?: string;
  // Allow customization of which options to show
  showButtons?: TimePeriodType[];
  showDropdownOptions?: TimePeriodType[];
}

export function TimePeriodSelector({
  selectedPeriod,
  onPeriodChange,
  className = "",
  showButtons,
  showDropdownOptions,
}: TimePeriodSelectorProps) {
  // Get default button and dropdown options, or use custom ones
  const buttonOptions = showButtons
    ? getButtonTimePeriods().filter((option) => showButtons.includes(option.id))
    : getButtonTimePeriods();

  const dropdownOptions = showDropdownOptions
    ? getDropdownTimePeriods().filter((option) =>
        showDropdownOptions.includes(option.id),
      )
    : getDropdownTimePeriods();

  // Check if selected period is in dropdown
  const selectedDropdownOption = dropdownOptions.find(
    (option) => option.id === selectedPeriod,
  );

  return (
    <div className={`flex flex-row items-center gap-2 ${className}`}>
      {/* Quick action buttons */}
      {buttonOptions.map((option) => (
        <Button
          key={option.id}
          variant={selectedPeriod === option.id ? "default" : "outline"}
          size="sm"
          onClick={() => onPeriodChange(option.id)}
          className="whitespace-nowrap"
        >
          {option.label}
        </Button>
      ))}

      {/* More options dropdown */}
      {dropdownOptions.length > 0 && (
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button
              variant={selectedDropdownOption ? "default" : "outline"}
              size="sm"
              className="whitespace-nowrap"
            >
              {selectedDropdownOption ? selectedDropdownOption.label : "More"}
              <ChevronDown className="ml-1 h-3 w-3" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            {dropdownOptions.map((option) => (
              <DropdownMenuItem
                key={option.id}
                onClick={() => onPeriodChange(option.id)}
                className={selectedPeriod === option.id ? "bg-accent" : ""}
              >
                {option.label}
              </DropdownMenuItem>
            ))}
          </DropdownMenuContent>
        </DropdownMenu>
      )}
    </div>
  );
}

// Convenience component for the standard time period selector used in most places
export function StandardTimePeriodSelector({
  selectedPeriod,
  onPeriodChange,
  className,
}: {
  selectedPeriod: TimePeriodType;
  onPeriodChange: (period: TimePeriodType) => void;
  className?: string;
}) {
  return (
    <TimePeriodSelector
      selectedPeriod={selectedPeriod}
      onPeriodChange={onPeriodChange}
      className={className}
      // Use default buttons and dropdown options
    />
  );
}

// Convenience component for Recent Runs panel with different time periods
export function RecentRunsTimePeriodSelector({
  selectedPeriod,
  onPeriodChange,
  className,
}: {
  selectedPeriod: TimePeriodType;
  onPeriodChange: (period: TimePeriodType) => void;
  className?: string;
}) {
  return (
    <TimePeriodSelector
      selectedPeriod={selectedPeriod}
      onPeriodChange={onPeriodChange}
      className={className}
      // Custom buttons: include 7, 14, 30 days for runs
      showButtons={["7_days", "14_days", "30_days"]}
      // Custom dropdown: include last and this calendar periods and custom
      showDropdownOptions={[
        "last_calendar_month",
        "calendar_month",
        "last_calendar_year",
        "calendar_year",
        "custom",
      ]}
    />
  );
}
