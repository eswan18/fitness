import { format, isToday, isYesterday } from "date-fns";

export function formatRunDate(date: Date): string {
  try {
    if (isNaN(date.getTime())) {
      return "Invalid Date";
    }
    if (isToday(date)) {
      return "Today";
    }
    if (isYesterday(date)) {
      return "Yesterday";
    }
    return format(date, "MMM d");
  } catch (error) {
    console.warn("Error formatting date:", date, error);
    return "Invalid Date";
  }
}

export function formatRunTime(datetime: Date): string {
  try {
    if (isNaN(datetime.getTime())) {
      return "";
    }
    return format(datetime, "h:mm a");
  } catch (error) {
    console.warn("Error formatting time:", datetime, error);
    return "";
  }
}

export function formatRunDistance(distance: number): string {
  return distance.toFixed(2);
}

export function calculatePace(distance: number, duration: number): string {
  if (distance === 0) return "--:--";
  const secondsPerMile = duration / distance;
  const minutes = Math.floor(secondsPerMile / 60);
  const seconds = Math.round(secondsPerMile % 60);
  return `${minutes}:${seconds.toString().padStart(2, '0')}`;
}

export function formatDuration(duration: number): string {
  const hours = Math.floor(duration / 3600);
  const minutes = Math.floor((duration % 3600) / 60);
  const seconds = duration % 60;
  
  if (hours > 0) {
    return `${hours}h ${minutes}m`;
  }
  return `${minutes}:${seconds.toString().padStart(2, '0')}`;
}

export function formatHeartRate(avgHeartRate: number | null | undefined): string {
  if (avgHeartRate === null || avgHeartRate === undefined) return "--";
  return Math.round(avgHeartRate).toString();
}

export function truncateText(text: string | null | undefined, maxLength: number): string {
  if (!text) return "--";
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength - 3) + "...";
}

export function isWithinDateRange(runDate: Date, dateRange: "7d" | "14d" | "30d" | "all"): boolean {
  if (dateRange === "all") return true;
  
  const now = new Date();
  const dayCount = dateRange === "7d" ? 7 : dateRange === "14d" ? 14 : 30;
  const cutoffDate = new Date(now.getTime() - (dayCount * 24 * 60 * 60 * 1000));
  
  return runDate >= cutoffDate;
}

// Import TimePeriodType and related utilities
import type { TimePeriodType } from "./timePeriods";
import { getTimePeriodById, isCustomTimePeriod } from "./timePeriods";

/**
 * Check if a run date falls within a given time period
 * New function that works with the unified TimePeriodType system
 */
export function isWithinTimePeriod(runDate: Date, timePeriod: TimePeriodType, customStart?: Date, customEnd?: Date): boolean {
  // Handle custom time period with provided dates
  if (isCustomTimePeriod(timePeriod)) {
    if (!customStart || !customEnd) return true; // Show all if custom dates not provided
    return runDate >= customStart && runDate <= customEnd;
  }

  // Get the time period configuration
  const periodConfig = getTimePeriodById(timePeriod);
  if (!periodConfig || !periodConfig.start || !periodConfig.end) {
    return true; // Show all if period not found
  }

  return runDate >= periodConfig.start && runDate <= periodConfig.end;
}

/**
 * Convert new TimePeriodType to legacy dateRange string for backward compatibility
 * Used during migration period
 */
export function timePeriodToDateRange(timePeriod: TimePeriodType): "7d" | "14d" | "30d" | "all" {
  switch (timePeriod) {
    case "7_days":
      return "7d";
    case "14_days":
      return "14d";
    case "30_days":
      return "30d";
    case "all_time":
    case "calendar_month":
    case "calendar_year":
    case "365_days":
    case "custom":
    default:
      return "all";
  }
}