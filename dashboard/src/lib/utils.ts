import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function daysInRange(start: Date, end: Date): number {
  // Treat inputs as days, not times, can return the number of days between two dates (inclusive on both ends)
  const startDate = new Date(
    start.getFullYear(),
    start.getMonth(),
    start.getDate(),
  );
  const endDate = new Date(end.getFullYear(), end.getMonth(), end.getDate());
  const timeDiff = endDate.getTime() - startDate.getTime();
  const dayDiff = Math.ceil(timeDiff / (1000 * 60 * 60 * 24)) + 1; // +1 to include both start and end dates
  return dayDiff < 0 ? 0 : dayDiff;
}
