import type {
  Run,
  RawRun,
  Shoe,
  ShoeMileage,
  RetireShoeRequest,
  RetiredShoeInfo,
  DayMileage,
  RawDayMileage,
  RawDayTrainingLoad,
  DayTrainingLoad,
  RawDayTrimp,
  DayTrimp,
  RunSortBy,
  SortOrder,
} from "./types";

// Fetch functions
//
// To pull data from the API

export async function fetchShoeMileage(
  includeRetired: boolean = false,
): Promise<ShoeMileage[]> {
  const url = new URL(
    `${import.meta.env.VITE_API_URL}/metrics/mileage/by-shoe`,
  );
  if (includeRetired) {
    url.searchParams.set("include_retired", "true");
  }
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
  sortBy?: RunSortBy;
  sortOrder?: SortOrder;
}

export async function fetchRuns({
  startDate,
  endDate,
  userTimezone,
  sortBy = "date",
  sortOrder = "desc",
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
  if (sortBy) {
    url.searchParams.set("sort_by", sortBy);
  }
  if (sortOrder) {
    url.searchParams.set("sort_order", sortOrder);
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
      console.warn(
        `Skipping invalid run:`,
        error instanceof Error ? error.message : String(error),
        rawRun,
      );
    }
  }

  if (invalidCount > 0) {
    console.warn(
      `Filtered out ${invalidCount} invalid runs out of ${rawRuns.length} total`,
    );
  }

  return validRuns
    .sort((a, b) => {
      // Use datetime if available (more precise), otherwise fall back to date
      const timeA = a.datetime ? a.datetime.getTime() : a.date.getTime();
      const timeB = b.datetime ? b.datetime.getTime() : b.date.getTime();
      return timeB - timeA; // Most recent first
    })
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
  sex: "M" | "F";
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
  const url = new URL(
    `${import.meta.env.VITE_API_URL}/metrics/training-load/by-day`,
  );
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
  const rawDayTrainingLoad = await (res.json() as Promise<
    RawDayTrainingLoad[]
  >);
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

  // Parse datetime first if available, then extract local date from it
  let datetime: Date | undefined;
  let date: Date | undefined;

  if (rawRun.datetime_utc) {
    // Ensure the datetime string is treated as UTC by appending 'Z' if not present
    const utcString = rawRun.datetime_utc.endsWith("Z")
      ? rawRun.datetime_utc
      : rawRun.datetime_utc + "Z";
    datetime = new Date(utcString);
    if (isNaN(datetime.getTime())) {
      console.warn(
        "Invalid datetime_utc:",
        rawRun.datetime_utc,
        "in run:",
        rawRun,
      );
      datetime = undefined;
    } else {
      // Extract the local date from the timezone-converted datetime
      date = new Date(
        datetime.getFullYear(),
        datetime.getMonth(),
        datetime.getDate(),
      );
    }
  }

  // Fallback to date field if datetime_utc not available or invalid
  if (!date && rawRun.date) {
    date = new Date(rawRun.date);
    if (isNaN(date.getTime())) {
      console.warn("Invalid date string:", rawRun.date, "in run:", rawRun);
      throw new Error(`Invalid date in run data: ${rawRun.date}`);
    }
  }

  if (!date) {
    console.warn(
      "Run missing both valid date and datetime_utc fields:",
      rawRun,
    );
    throw new Error(`Run missing date fields`);
  }

  return {
    date,
    datetime,
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
    method: "POST",
  });
  if (!res.ok) {
    throw new Error(`Failed to refresh data: ${res.statusText}`);
  }
  return res.json() as Promise<RefreshDataResponse>;
}

// Shoe retirement management functions

export async function updateShoe(
  shoeId: string,
  request: RetireShoeRequest,
): Promise<{ message: string }> {
  const url = new URL(
    `${import.meta.env.VITE_API_URL}/shoes/${encodeURIComponent(shoeId)}`,
  );
  const res = await fetch(url, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(request),
  });
  if (!res.ok) {
    throw new Error(`Failed to update shoe: ${res.statusText}`);
  }
  return res.json() as Promise<{ message: string }>;
}

// Legacy function - retire shoe using new PATCH API
export async function retireShoe(
  shoeId: string,
  request: RetireShoeRequest,
): Promise<{ message: string }> {
  return updateShoe(shoeId, request);
}

// Legacy function - unretire shoe using new PATCH API
export async function unretireShoe(
  shoeId: string,
): Promise<{ message: string }> {
  return updateShoe(shoeId, { retired_at: null, retirement_notes: null });
}

export async function fetchShoes(retired?: boolean): Promise<Shoe[]> {
  const url = new URL(`${import.meta.env.VITE_API_URL}/shoes`);
  if (retired !== undefined) {
    url.searchParams.set("retired", retired.toString());
  }
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(`Failed to fetch shoes: ${res.statusText}`);
  }
  return res.json() as Promise<Shoe[]>;
}

// Legacy function - fetch retired shoes using new unified API
export async function fetchRetiredShoes(): Promise<RetiredShoeInfo[]> {
  const shoes = await fetchShoes(true);
  return shoes.map(shoe => ({
    shoe,
    retired_at: shoe.retired_at!,
    retirement_notes: shoe.retirement_notes,
  }));
}
