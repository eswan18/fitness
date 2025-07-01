import type {
  Run,
  RawRun,
  ShoeMileage,
  DayMileage,
  RawDayMileage,
  RawDayTrainingLoad,
  DayTrainingLoad
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
}

export async function fetchDayMileage({
  startDate,
  endDate,
}: FetchDayMileageParams = {}): Promise<DayMileage[]> {
  const url = new URL(`${import.meta.env.VITE_API_URL}/metrics/mileage/by-day`);
  if (startDate) {
    url.searchParams.set("start", toDateString(startDate));
  }
  if (endDate) {
    url.searchParams.set("end", toDateString(endDate));
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
}

export async function fetchRollingDayMileage({
  startDate,
  endDate,
  window,
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
  const res = await fetch(url);
  if (!res.ok) throw new Error("Failed to fetch rolling day mileage");
  const rawDayMileage = await (res.json() as Promise<RawDayMileage[]>);
  return rawDayMileage.map(dayMileageFromRawDayMileage);
}

export interface FetchRunsParams {
  startDate?: Date;
  endDate?: Date;
}

export async function fetchRuns({
  startDate,
  endDate,
}: FetchRunsParams = {}): Promise<Run[]> {
  const url = new URL(`${import.meta.env.VITE_API_URL}/runs`);
  if (startDate) {
    url.searchParams.set("start", toDateString(startDate));
  }
  if (endDate) {
    url.searchParams.set("end", toDateString(endDate));
  }

  const res = await fetch(url);
  if (!res.ok) throw new Error("Failed to fetch runs");

  const rawRuns = await (res.json() as Promise<RawRun[]>);
  return rawRuns.map(runFromRawRun);
}

export interface fetchTotalMileageParams {
  startDate?: Date;
  endDate?: Date;
}

export async function fetchTotalMileage({
  startDate,
  endDate,
}: fetchTotalMileageParams = {}): Promise<number> {
  const url = new URL(`${import.meta.env.VITE_API_URL}/metrics/mileage/total`);
  if (startDate) {
    url.searchParams.set("start", toDateString(startDate));
  }
  if (endDate) {
    url.searchParams.set("end", toDateString(endDate));
  }
  const res = await fetch(url);
  if (!res.ok) throw new Error("Failed to fetch mileage");
  const totalMileage = (await res.json()) as number;
  return totalMileage;
}

export interface fetchTotalSecondsParams {
  startDate?: Date;
  endDate?: Date;
}

export async function fetchTotalSeconds({
  startDate,
  endDate,
}: fetchTotalSecondsParams = {}): Promise<number> {
  const url = new URL(`${import.meta.env.VITE_API_URL}/metrics/seconds/total`);
  if (startDate) {
    url.searchParams.set("start", toDateString(startDate));
  }
  if (endDate) {
    url.searchParams.set("end", toDateString(endDate));
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
}

export async function fetchDayTrainingLoad({
  startDate,
  endDate,
  maxHr,
  restingHr,
  sex,
}: fetchDayTrainingLoadParams): Promise<DayTrainingLoad[]> {
  const url = new URL(`${import.meta.env.VITE_API_URL}/metrics/training-load/by-day`);
  url.searchParams.set("start", toDateString(startDate));
  url.searchParams.set("end", toDateString(endDate));
  url.searchParams.set("max_hr", maxHr.toString());
  url.searchParams.set("resting_hr", restingHr.toString());
  url.searchParams.set("sex", sex);
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
  // Convert the date string to a Date object
  const date = new Date(rawRun.date);
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