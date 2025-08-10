export type RunType = "Outdoor Run" | "Treadmill Run";
export type RunSource = "MapMyFitness" | "Strava";

// Sorting types
export type RunSortBy =
  | "date"
  | "distance"
  | "duration"
  | "pace"
  | "heart_rate"
  | "source"
  | "type"
  | "shoes";
export type SortOrder = "asc" | "desc";

// A run received from the API, before being parsed.
export type RawRun = {
  date?: string; // ISO 8601 string (from Python's `date`) - may be missing
  datetime_utc?: string; // ISO 8601 datetime string (from Python's `datetime`)
  type: RunType;
  distance: number; // in miles
  duration: number; // in seconds
  source: RunSource;
  avg_heart_rate?: number | null;
  shoes?: string | null;
};

export type Run = {
  date: Date;
  datetime?: Date; // Full datetime when available
  type: RunType;
  distance: number; // in miles
  duration: number; // in seconds
  source: RunSource;
  avg_heart_rate?: number | null;
  shoes?: string | null;
};

// Raw run with shoes from the API (explicit shoes field guaranteed)
// Removed legacy RunWithShoes raw/display types; use RunDetail instead

export type RawDayMileage = {
  date: string; // ISO 8601 string (from Python's `date`)
  mileage: number;
};

export type DayMileage = {
  date: Date;
  mileage: number;
};

export type Shoe = {
  id: string;
  name: string;
  retired_at?: string | null;
  retirement_notes?: string | null;
  deleted_at?: string | null;
};

export type ShoeMileage = {
  shoe: Shoe;
  mileage: number;
};

export type RetireShoeRequest = {
  retired_at?: string | null; // ISO date string or null for unretirement
  retirement_notes?: string | null;
};

export type RetiredShoeInfo = {
  shoe: Shoe;
  retired_at: string;
  retirement_notes?: string | null;
};

export type TrainingLoad = {
  atl: number; // Acute Training Load
  ctl: number; // Chronic Training Load
  tsb: number; // Training Stress Balance
};

export type RawDayTrainingLoad = {
  date: string; // ISO 8601 string (from Python's `date`)
  training_load: TrainingLoad;
};

export type DayTrainingLoad = {
  date: Date;
  training_load: TrainingLoad;
};

export type RawDayTrimp = {
  date: string; // ISO 8601 string (from Python's `date`)
  trimp: number;
};

export type DayTrimp = {
  date: Date;
  trimp: number;
};

// Google Calendar sync types
export type SyncStatus = "synced" | "failed" | "pending";

export type SyncedRun = {
  id: number;
  run_id: string;
  run_version: number;
  google_event_id: string; // Backend currently stores empty string on failures
  synced_at: string; // ISO datetime string
  sync_status: SyncStatus;
  error_message?: string | null;
  created_at: string; // ISO datetime string
  updated_at: string; // ISO datetime string
};

export type SyncResponse = {
  success: boolean;
  message: string;
  google_event_id?: string | null;
  sync_status: SyncStatus;
  synced_at?: string | null;
};

export type SyncStatusResponse = {
  run_id: string;
  is_synced: boolean;
  sync_status?: SyncStatus | null;
  synced_at?: string | null;
  google_event_id?: string | null;
  run_version?: number | null;
  error_message?: string | null;
};

// Unified Run Details (for /runs/details)
export type RawRunDetail = {
  id: string;
  datetime_utc: string; // ISO datetime string (UTC)
  type: RunType;
  distance: number; // miles
  duration: number; // seconds
  source: RunSource;
  avg_heart_rate?: number | null;
  shoe_id?: string | null;
  shoes?: string | null;
  shoe_retirement_notes?: string | null;
  deleted_at?: string | null;
  version?: number | null;
  // sync fields
  is_synced: boolean;
  sync_status?: SyncStatus | null;
  synced_at?: string | null;
  google_event_id?: string | null;
  synced_version?: number | null;
  error_message?: string | null;
};

export type RunDetail = {
  // Base run display fields
  id: string;
  date: Date;
  datetime?: Date; // Parsed from datetime_utc
  type: RunType;
  distance: number;
  duration: number;
  source: RunSource;
  avg_heart_rate?: number | null;

  // Shoes/metadata
  shoe_id?: string | null;
  shoes?: string | null;
  shoe_retirement_notes?: string | null;
  deleted_at?: Date | null;
  version?: number | null;

  // Sync info
  is_synced: boolean;
  sync_status?: SyncStatus | null;
  synced_at?: Date | null;
  google_event_id?: string | null;
  synced_version?: number | null;
  error_message?: string | null;
};
