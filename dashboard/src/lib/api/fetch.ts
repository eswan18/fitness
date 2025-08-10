import type {
  Run,
  RawRun,
  RunWithShoes,
  RawRunWithShoes,
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
  SyncedRun,
  SyncResponse,
  SyncStatusResponse,
  RawRunDetail,
  RunDetail,
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

// Deprecated: fetchRunsWithShoes replaced by fetchRunDetails

// Unified run details
export async function fetchRunDetails({
  startDate,
  endDate,
  sortBy = "date",
  sortOrder = "desc",
}: FetchRunsParams = {}): Promise<RunDetail[]> {
  const url = new URL(`${import.meta.env.VITE_API_URL}/runs/details`);
  if (startDate) {
    url.searchParams.set("start", toDateString(startDate));
  }
  if (endDate) {
    url.searchParams.set("end", toDateString(endDate));
  }
  if (sortBy) {
    url.searchParams.set("sort_by", sortBy);
  }
  if (sortOrder) {
    url.searchParams.set("sort_order", sortOrder);
  }

  const res = await fetch(url);
  if (!res.ok) throw new Error("Failed to fetch run details");

  const rawDetails = (await res.json()) as RawRunDetail[];
  return rawDetails.map(runDetailFromRawRunDetail);
}

export interface FetchRecentRunsParams {
  limit?: number;
  userTimezone?: string;
}

// Deprecated: fetchRecentRuns replaced by query with sorting/limit in UI

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

function runWithShoesFromRawRunWithShoes(
  rawRunWithShoes: RawRunWithShoes,
): RunWithShoes {
  if (typeof rawRunWithShoes !== "object" || rawRunWithShoes === null) {
    throw new Error("Invalid run with shoes data");
  }

  // Parse datetime first if available, then extract local date from it
  let datetime: Date | undefined;
  let date: Date | undefined;

  if (rawRunWithShoes.datetime_utc) {
    // Ensure the datetime string is treated as UTC by appending 'Z' if not present
    const utcString = rawRunWithShoes.datetime_utc.endsWith("Z")
      ? rawRunWithShoes.datetime_utc
      : rawRunWithShoes.datetime_utc + "Z";
    datetime = new Date(utcString);
    if (isNaN(datetime.getTime())) {
      console.warn(
        "Invalid datetime_utc:",
        rawRunWithShoes.datetime_utc,
        "in run:",
        rawRunWithShoes,
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

  if (!date) {
    console.warn("Run missing valid datetime_utc field:", rawRunWithShoes);
    throw new Error(`Run missing date field`);
  }

  return {
    id: rawRunWithShoes.id,
    date,
    datetime,
    type: rawRunWithShoes.type,
    distance: rawRunWithShoes.distance,
    duration: rawRunWithShoes.duration,
    source: rawRunWithShoes.source,
    avg_heart_rate: rawRunWithShoes.avg_heart_rate ?? null,
    shoe_id: rawRunWithShoes.shoe_id ?? null,
    shoes: rawRunWithShoes.shoes ?? null,
    deleted_at: rawRunWithShoes.deleted_at
      ? new Date(rawRunWithShoes.deleted_at)
      : null,
  };
}

function runDetailFromRawRunDetail(raw: RawRunDetail): RunDetail {
  // Parse datetime first if available, then derive local date
  let datetime: Date | undefined;
  let date: Date | undefined;
  if (raw.datetime_utc) {
    const utcString = raw.datetime_utc.endsWith("Z")
      ? raw.datetime_utc
      : raw.datetime_utc + "Z";
    const parsed = new Date(utcString);
    if (!isNaN(parsed.getTime())) {
      datetime = parsed;
      date = new Date(
        parsed.getFullYear(),
        parsed.getMonth(),
        parsed.getDate(),
      );
    }
  }
  if (!date) {
    // Backend guarantees datetime_utc; but keep a fallback to today
    date = new Date();
  }

  return {
    id: raw.id,
    date,
    datetime,
    type: raw.type,
    distance: raw.distance,
    duration: raw.duration,
    source: raw.source,
    avg_heart_rate: raw.avg_heart_rate ?? null,
    shoe_id: raw.shoe_id ?? null,
    shoes: raw.shoes ?? null,
    shoe_retirement_notes: raw.shoe_retirement_notes ?? null,
    deleted_at: raw.deleted_at ? new Date(raw.deleted_at) : null,
    version: raw.version ?? null,
    is_synced: !!raw.is_synced,
    sync_status: raw.sync_status ?? null,
    synced_at: raw.synced_at ? new Date(raw.synced_at) : null,
    google_event_id: raw.google_event_id ?? null,
    synced_version: raw.synced_version ?? null,
    error_message: raw.error_message ?? null,
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
  total_external_runs: number;
  existing_in_db: number;
  new_runs_found: number;
  new_runs_inserted: number;
  new_run_ids: string[];
  updated_at: string;
}

export async function refreshData(): Promise<RefreshDataResponse> {
  const url = new URL(`${import.meta.env.VITE_API_URL}/update-data`);
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
  return shoes.map((shoe) => ({
    shoe,
    retired_at: shoe.retired_at!,
    retirement_notes: shoe.retirement_notes,
  }));
}

// Run editing functionality

export interface UpdateRunRequest {
  distance?: number;
  duration?: number;
  avg_heart_rate?: number | null;
  type?: "Outdoor Run" | "Treadmill Run";
  shoe_id?: string | null;
  datetime_utc?: string; // ISO datetime string
  change_reason?: string;
  changed_by: string;
}

export interface UpdateRunResponse {
  status: string;
  message: string;
  // The backend returns a raw run-like JSON object; we don't need a strict type here yet
  run: unknown;
  updated_fields: string[];
  updated_at: string;
  updated_by: string;
}

export async function updateRun(
  runId: string,
  request: UpdateRunRequest,
): Promise<UpdateRunResponse> {
  const url = new URL(
    `${import.meta.env.VITE_API_URL}/runs/${encodeURIComponent(runId)}`,
  );
  const res = await fetch(url, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(request),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(
      errorData.detail || `Failed to update run: ${res.statusText}`,
    );
  }
  return res.json() as Promise<UpdateRunResponse>;
}

export interface EnvironmentResponse {
  environment: string;
}

export async function fetchEnvironment(): Promise<EnvironmentResponse> {
  const url = new URL(`${import.meta.env.VITE_API_URL}/environment`);
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(`Failed to fetch environment: ${res.statusText}`);
  }
  return res.json() as Promise<EnvironmentResponse>;
}

// Google Calendar sync API
// Deprecated: fetchSyncedRuns replaced by embedded sync info from /runs/details

// Deprecated: fetchSyncStatus replaced by embedded sync info from /runs/details

export async function syncRun(runId: string): Promise<SyncResponse> {
  const url = new URL(
    `${import.meta.env.VITE_API_URL}/sync/runs/${encodeURIComponent(runId)}`,
  );
  const res = await fetch(url, { method: "POST" });
  const data = (await res.json().catch(() => ({}))) as Partial<SyncResponse> &
    Record<string, unknown>;
  if (!res.ok || data.success === false) {
    const message =
      (typeof data.message === "string" && data.message) || res.statusText;
    throw new Error(`Failed to sync: ${message}`);
  }
  return data as SyncResponse;
}

export async function unsyncRun(runId: string): Promise<SyncResponse> {
  const url = new URL(
    `${import.meta.env.VITE_API_URL}/sync/runs/${encodeURIComponent(runId)}`,
  );
  const res = await fetch(url, { method: "DELETE" });
  const data = (await res.json().catch(() => ({}))) as Partial<SyncResponse> &
    Record<string, unknown>;
  if (!res.ok || data.success === false) {
    const message =
      (typeof data.message === "string" && data.message) || res.statusText;
    throw new Error(`Failed to unsync: ${message}`);
  }
  return data as SyncResponse;
}
