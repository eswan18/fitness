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