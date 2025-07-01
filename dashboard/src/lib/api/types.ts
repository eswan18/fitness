export type RunType = "Outdoor Run" | "Treadmill Run";
export type RunSource = "MapMyFitness" | "Strava";

// A run received from the API, before being parsed.
export type RawRun = {
  date: string; // ISO 8601 string (from Python's `date`)
  type: RunType;
  distance: number; // in miles
  duration: number; // in seconds
  source: RunSource;
  avg_heart_rate?: number | null;
  shoes?: string | null;
};

export type Run = {
  date: Date;
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