export type RunType = "Outdoor Run" | "Treadmill Run";
export type RunSource = "MapMyFitness" | "Strava";

// Sorting types
export type RunSortBy = "date" | "distance" | "duration" | "pace" | "source" | "type" | "shoes";
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

export type RawDayMileage = {
  date: string; // ISO 8601 string (from Python's `date`)
  mileage: number;
};

export type DayMileage = {
  date: Date;
  mileage: number;
};

export type ShoeMileage = {
  shoe: string;
  mileage: number;
};

export type ShoeMileageWithRetirement = {
  shoe: string;
  mileage: number;
  retired: boolean;
  retirement_date?: string | null;
  retirement_notes?: string | null;
};

export type RetireShoeRequest = {
  retirement_date: string; // ISO date string
  notes?: string;
};

export type RetiredShoeInfo = {
  shoe: string;
  retirement_date: string;
  notes?: string | null;
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