// Unified time period system for both TimePeriodStatsPanel and RecentRunsPanel

export type TimePeriodType = 
  // Quick action buttons
  | "7_days"
  | "14_days" 
  | "30_days" 
  | "365_days"
  // Dropdown options  
  | "calendar_month"
  | "calendar_year"
  | "last_calendar_month"
  | "last_calendar_year"
  | "all_time"
  | "custom";

export interface TimePeriodOption {
  id: TimePeriodType;
  label: string;
  start: Date | undefined;
  end: Date | undefined;
}

/**
 * Calculate start of current calendar month
 */
export function getCalendarMonthStart(): Date {
  const now = new Date();
  return new Date(now.getFullYear(), now.getMonth(), 1);
}

/**
 * Calculate start of current calendar year
 */
export function getCalendarYearStart(): Date {
  const now = new Date();
  return new Date(now.getFullYear(), 0, 1);
}

/**
 * Calculate start of last calendar month
 */
export function getLastCalendarMonthStart(): Date {
  const now = new Date();
  return new Date(now.getFullYear(), now.getMonth() - 1, 1);
}

/**
 * Calculate end of last calendar month
 */
export function getLastCalendarMonthEnd(): Date {
  const now = new Date();
  return new Date(now.getFullYear(), now.getMonth(), 0, 23, 59, 59, 999);
}

/**
 * Calculate start of last calendar year
 */
export function getLastCalendarYearStart(): Date {
  const now = new Date();
  return new Date(now.getFullYear() - 1, 0, 1);
}

/**
 * Calculate end of last calendar year
 */
export function getLastCalendarYearEnd(): Date {
  const now = new Date();
  return new Date(now.getFullYear() - 1, 11, 31, 23, 59, 59, 999);
}

/**
 * Calculate date N days ago from today
 */
export function getDaysAgo(days: number): Date {
  const date = new Date();
  date.setDate(date.getDate() - days);
  date.setHours(0, 0, 0, 0);
  return date;
}

/**
 * Get today's date with time set to end of day
 */
export function getToday(): Date {
  const today = new Date();
  today.setHours(23, 59, 59, 999);
  return today;
}

/**
 * All time start date (historical data begins)
 */
export const ALL_TIME_START = new Date(2016, 0, 1); // January 1, 2016

/**
 * Get all available time period options with calculated dates
 */
export function getTimePeriodOptions(): TimePeriodOption[] {
  const today = getToday();
  
  return [
    // Button options (quick actions)
    {
      id: "7_days",
      label: "7 Days",
      start: getDaysAgo(7),
      end: today,
    },
    {
      id: "14_days",
      label: "14 Days",
      start: getDaysAgo(14),
      end: today,
    },
    {
      id: "30_days", 
      label: "30 Days",
      start: getDaysAgo(30),
      end: today,
    },
    {
      id: "365_days",
      label: "365 Days", 
      start: getDaysAgo(365),
      end: today,
    },
    // Dropdown options (more choices)
    {
      id: "calendar_month",
      label: "This Calendar Month",
      start: getCalendarMonthStart(),
      end: today,
    },
    {
      id: "calendar_year",
      label: "This Calendar Year", 
      start: getCalendarYearStart(),
      end: today,
    },
    {
      id: "last_calendar_month",
      label: "Last Calendar Month",
      start: getLastCalendarMonthStart(),
      end: getLastCalendarMonthEnd(),
    },
    {
      id: "last_calendar_year",
      label: "Last Calendar Year",
      start: getLastCalendarYearStart(),
      end: getLastCalendarYearEnd(),
    },
    {
      id: "all_time",
      label: "All Time",
      start: ALL_TIME_START,
      end: today,
    },
    {
      id: "custom",
      label: "Custom",
      start: undefined,
      end: undefined,
    },
  ];
}

/**
 * Get button time period options (quick actions) 
 * Default: 14, 30, 365 days as per issue requirements
 */
export function getButtonTimePeriods(): TimePeriodOption[] {
  return getTimePeriodOptions().filter(option => 
    ["14_days", "30_days", "365_days"].includes(option.id)
  );
}

/**
 * Get all possible button time period options (including 7 days for RecentRuns)
 */
export function getAllButtonTimePeriods(): TimePeriodOption[] {
  return getTimePeriodOptions().filter(option => 
    ["7_days", "14_days", "30_days", "365_days"].includes(option.id)
  );
}

/**
 * Get dropdown time period options (more choices) 
 */
export function getDropdownTimePeriods(): TimePeriodOption[] {
  return getTimePeriodOptions().filter(option =>
    ["calendar_month", "calendar_year", "last_calendar_month", "last_calendar_year", "all_time", "custom"].includes(option.id)
  );
}

/**
 * Find time period option by ID
 */
export function getTimePeriodById(id: TimePeriodType): TimePeriodOption | undefined {
  return getTimePeriodOptions().find(option => option.id === id);
}

/**
 * Check if a time period requires custom date selection
 */
export function isCustomTimePeriod(id: TimePeriodType): boolean {
  return id === "custom";
}

/**
 * Migration utility: convert old RangePreset to new TimePeriodType
 */
export function migrateRangePreset(oldPreset: string): TimePeriodType {
  switch (oldPreset) {
    case "14 Days":
      return "14_days";
    case "30 Days": 
      return "30_days";
    case "1 Year":
      return "365_days";
    case "All Time":
      return "all_time";
    case "Custom":
      return "custom";
    default:
      return "30_days"; // Default fallback
  }
}

/**
 * Migration utility: convert old RunsFilterBar dateRange to new TimePeriodType
 */
export function migrateRunsDateRange(oldDateRange: string): TimePeriodType {
  switch (oldDateRange) {
    case "7d":
      return "7_days";
    case "14d":
      return "14_days";
    case "30d": 
      return "30_days";
    case "all":
      return "all_time";
    default:
      return "7_days"; // Default for RecentRuns
  }
}