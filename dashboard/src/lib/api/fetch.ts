import type {
  Run,
  RawRun,
  ShoeMileage,
  DayMileage,
  RawDayMileage,
  RawDayTrainingLoad,
  DayTrainingLoad,
  RawDayTrimp,
  DayTrimp,
} from "./types";


// Fetch functions 
//
// To pull data from the API

export async function fetchShoeMileage(): Promise<ShoeMileage[]> {
  const url = new URL(
    `${import.meta.env.VITE_API_URL}/metrics/mileage/by-shoe`,
  );
  const res = await fetch(url);
  if (!res.ok) throw new Error("Failed to fetch shoe mileage");
  return res.json() as Promise<ShoeMileage[]>;
}

export interface FetchDayMileageParams {
  startDate?: Date;
  endDate?: Date;
  userTimezone?: string;
}

export async function fetchDayMileage({
  startDate,
  endDate,
  userTimezone,
}: FetchDayMileageParams = {}): Promise<DayMileage[]> {
  const url = new URL(`${import.meta.env.VITE_API_URL}/metrics/mileage/by-day`);
  if (startDate) {
    url.searchParams.set("start", toDateString(startDate));
  }
  if (endDate) {
    url.searchParams.set("end", toDateString(endDate));
  }
  if (userTimezone) {
    url.searchParams.set("user_timezone", userTimezone);
  }
  const res = await fetch(url);
  if (!res.ok) throw new Error("Failed to fetch day mileage");
  const rawDayMileage = await (res.json() as Promise<RawDayMileage[]>);
  return rawDayMileage.map(dayMileageFromRawDayMileage);
}

export interface FetchRollingDayMileageParams {
  startDate?: Date;
  endDate?: Date;
  window?: number; // Number of days to look back for rolling average
  userTimezone?: string;
}

export async function fetchRollingDayMileage({
  startDate,
  endDate,
  window,
  userTimezone,
}: FetchRollingDayMileageParams = {}): Promise<DayMileage[]> {
  const url = new URL(
    `${import.meta.env.VITE_API_URL}/metrics/mileage/rolling-by-day`,
  );
  if (startDate) {
    url.searchParams.set("start", toDateString(startDate));
  }
  if (endDate) {
    url.searchParams.set("end", toDateString(endDate));
  }
  if (window) {
    url.searchParams.set("window", window.toString());
  }
  if (userTimezone) {
    url.searchParams.set("user_timezone", userTimezone);
  }
  const res = await fetch(url);
  if (!res.ok) throw new Error("Failed to fetch rolling day mileage");
  const rawDayMileage = await (res.json() as Promise<RawDayMileage[]>);
  return rawDayMileage.map(dayMileageFromRawDayMileage);
}

export interface FetchRunsParams {
  startDate?: Date;
  endDate?: Date;
  userTimezone?: string;
}

export async function fetchRuns({
  startDate,
  endDate,
  userTimezone,
}: FetchRunsParams = {}): Promise<Run[]> {
  const url = new URL(`${import.meta.env.VITE_API_URL}/runs`);
  if (startDate) {
    url.searchParams.set("start", toDateString(startDate));
  }
  if (endDate) {
    url.searchParams.set("end", toDateString(endDate));
  }
  if (userTimezone) {
    url.searchParams.set("user_timezone", userTimezone);
  }

  const res = await fetch(url);
  if (!res.ok) throw new Error("Failed to fetch runs");

  const rawRuns = await (res.json() as Promise<RawRun[]>);
  return rawRuns.map(runFromRawRun);
}

export interface FetchRecentRunsParams {
  limit?: number;
  userTimezone?: string;
}

export async function fetchRecentRuns({
  limit = 25,
  userTimezone,
}: FetchRecentRunsParams = {}): Promise<Run[]> {
  const url = new URL(`${import.meta.env.VITE_API_URL}/runs`);
  if (userTimezone) {
    url.searchParams.set("user_timezone", userTimezone);
  }

  const res = await fetch(url);
  if (!res.ok) throw new Error("Failed to fetch recent runs");

  const rawRuns = await (res.json() as Promise<RawRun[]>);
  console.log("Raw runs from API:", rawRuns.slice(0, 3)); // Debug: log first 3 runs
  console.log("Total runs from API:", rawRuns.length);
  
  // Filter out invalid runs instead of throwing errors
  const validRuns: Run[] = [];
  let invalidCount = 0;
  
  for (const rawRun of rawRuns) {
    try {
      const run = runFromRawRun(rawRun);
      validRuns.push(run);
    } catch (error) {
      invalidCount++;
      console.warn(`Skipping invalid run:`, error instanceof Error ? error.message : String(error), rawRun);
    }
  }
  
  if (invalidCount > 0) {
    console.warn(`Filtered out ${invalidCount} invalid runs out of ${rawRuns.length} total`);
  }
  
  return validRuns
    .sort((a, b) => b.date.getTime() - a.date.getTime())
    .slice(0, limit);
}

export interface fetchTotalMileageParams {
  startDate?: Date;
  endDate?: Date;
  userTimezone?: string;
}

export async function fetchTotalMileage({
  startDate,
  endDate,
  userTimezone,
}: fetchTotalMileageParams = {}): Promise<number> {
  const url = new URL(`${import.meta.env.VITE_API_URL}/metrics/mileage/total`);
  if (startDate) {
    url.searchParams.set("start", toDateString(startDate));
  }
  if (endDate) {
    url.searchParams.set("end", toDateString(endDate));
  }
  if (userTimezone) {
    url.searchParams.set("user_timezone", userTimezone);
  }
  const res = await fetch(url);
  if (!res.ok) throw new Error("Failed to fetch mileage");
  const totalMileage = (await res.json()) as number;
  return totalMileage;
}

export interface fetchTotalSecondsParams {
  startDate?: Date;
  endDate?: Date;
  userTimezone?: string;
}

export async function fetchTotalSeconds({
  startDate,
  endDate,
  userTimezone,
}: fetchTotalSecondsParams = {}): Promise<number> {
  const url = new URL(`${import.meta.env.VITE_API_URL}/metrics/seconds/total`);
  if (startDate) {
    url.searchParams.set("start", toDateString(startDate));
  }
  if (endDate) {
    url.searchParams.set("end", toDateString(endDate));
  }
  if (userTimezone) {
    url.searchParams.set("user_timezone", userTimezone);
  }
  const res = await fetch(url);
  if (!res.ok) throw new Error("Failed to fetch seconds");
  const totalSeconds = (await res.json()) as number;
  return totalSeconds;
}

export interface fetchDayTrainingLoadParams {
  startDate: Date;
  endDate: Date;
  maxHr: number;
  restingHr: number;
  sex: 'M' | 'F';
  userTimezone?: string;
}

export async function fetchDayTrainingLoad({
  startDate,
  endDate,
  maxHr,
  restingHr,
  sex,
  userTimezone,
}: fetchDayTrainingLoadParams): Promise<DayTrainingLoad[]> {
  const url = new URL(`${import.meta.env.VITE_API_URL}/metrics/training-load/by-day`);
  url.searchParams.set("start", toDateString(startDate));
  url.searchParams.set("end", toDateString(endDate));
  url.searchParams.set("max_hr", maxHr.toString());
  url.searchParams.set("resting_hr", restingHr.toString());
  url.searchParams.set("sex", sex);
  if (userTimezone) {
    url.searchParams.set("user_timezone", userTimezone);
  }
  const res = await fetch(url);
  if (!res.ok) throw new Error("Failed to fetch training load");
  const rawDayTrainingLoad = await (res.json() as Promise<RawDayTrainingLoad[]>);
  return rawDayTrainingLoad.map(dayTrainingLoadFromRawDayTrainingLoad);
}

// Type conversions
// 
// To convert received data into application types.

function toDateString(d: Date): string {
  return d.toISOString().split("T")[0]; // "YYYY-MM-DD"
}

function runFromRawRun(rawRun: RawRun): Run {
  if (typeof rawRun !== "object" || rawRun === null) {
    throw new Error("Invalid run data");
  }
  
  // Try to get date from either 'date' or 'datetime_utc' field
  let dateString: string | undefined;
  if (rawRun.date) {
    dateString = rawRun.date;
  } else if (rawRun.datetime_utc) {
    // Extract date from datetime_utc
    dateString = rawRun.datetime_utc.split('T')[0];
  }
  
  if (!dateString) {
    console.warn("Run missing both date and datetime_utc fields:", rawRun);
    throw new Error(`Run missing date fields`);
  }
  
  // Convert the date string to a Date object
  const date = new Date(dateString);
  if (isNaN(date.getTime())) {
    console.warn("Invalid date string:", dateString, "in run:", rawRun);
    throw new Error(`Invalid date in run data: ${dateString}`);
  }
  
  return {
    date,
    type: rawRun.type,
    distance: rawRun.distance,
    duration: rawRun.duration,
    source: rawRun.source,
    avg_heart_rate: rawRun.avg_heart_rate ?? null,
    shoes: rawRun.shoes ?? null,
  };
}

function dayMileageFromRawDayMileage(rawDayMileage: RawDayMileage): DayMileage {
  if (typeof rawDayMileage !== "object" || rawDayMileage === null) {
    throw new Error("Invalid day mileage data");
  }
  // Convert the date string to a Date object
  const date = new Date(rawDayMileage.date);
  return {
    date,
    mileage: rawDayMileage.mileage,
  };
}

function dayTrainingLoadFromRawDayTrainingLoad(
  rawDayTrainingLoad: RawDayTrainingLoad,
): DayTrainingLoad {
  if (typeof rawDayTrainingLoad !== "object" || rawDayTrainingLoad === null) {
    throw new Error("Invalid training load data");
  }
  // Convert the date string to a Date object
  // Dates come in like "2025-06-30" and we need to convert them to Date objects, without worrying about timezones.
  const date = new Date(rawDayTrainingLoad.date + "T00:00:00");
  return {
    date,
    training_load: rawDayTrainingLoad.training_load,
  };
}

function dayTrimpFromRawDayTrimp(rawDayTrimp: RawDayTrimp): DayTrimp {
  return {
    date: new Date(rawDayTrimp.date + "T00:00:00"), // Ensure it's treated as local date
    trimp: rawDayTrimp.trimp,
  };
}

export async function fetchDayTrimp(
  start?: Date,
  end?: Date,
  userTimezone?: string,
): Promise<DayTrimp[]> {
  const url = new URL(`${import.meta.env.VITE_API_URL}/metrics/trimp/by-day`);
  if (start) {
    url.searchParams.set("start", toDateString(start));
  }
  if (end) {
    url.searchParams.set("end", toDateString(end));
  }
  if (userTimezone) {
    url.searchParams.set("user_timezone", userTimezone);
  }
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(`Failed to fetch day TRIMP: ${res.statusText}`);
  }
  const rawDayTrimps = await (res.json() as Promise<RawDayTrimp[]>);
  return rawDayTrimps.map(dayTrimpFromRawDayTrimp);
}

export interface RefreshDataResponse {
  status: string;
  message: string;
  total_runs: number;
  refreshed_at: string;
}

export async function refreshData(): Promise<RefreshDataResponse> {
  const url = new URL(`${import.meta.env.VITE_API_URL}/refresh-data`);
  const res = await fetch(url, {
    method: 'POST',
  });
  if (!res.ok) {
    throw new Error(`Failed to refresh data: ${res.statusText}`);
  }
  return res.json() as Promise<RefreshDataResponse>;
}