import type { RunDetail } from "@/lib/api";

// Constants matching the API implementation
const DEFAULT_MAX_HR = 192;
const DEFAULT_RESTING_HR = 42;
const DEFAULT_SEX = "M" as const;

/**
 * Calculate the Banister TRaining IMPulse score for a run.
 *
 * TRIMP = Duration (minutes) x HR_Relative x Y
 * where HR_Relative is the relative heart rate:
 *   - HR_Relative = (avg_hr_during_for_activity - resting_hr) / (max_hr - resting_hr)
 * where Y is a sex-based weighting factor:
 *   - For men: Y = 0.64 * e^(1.92 x HR_Relative)
 *   - For women: Y = 0.86 * e^(1.67 x HR_Relative)
 */
export function calculateTrimp(
  run: RunDetail,
  maxHr: number = DEFAULT_MAX_HR,
  restingHr: number = DEFAULT_RESTING_HR,
  sex: "M" | "F" = DEFAULT_SEX,
): number | null {
  if (!run.avg_heart_rate || run.avg_heart_rate <= 0) {
    return null;
  }

  const hrRelative = (run.avg_heart_rate - restingHr) / (maxHr - restingHr);
  // Clamp hr_relative to the range [0, 1]
  const clampedHrRelative = Math.max(0.0, Math.min(1.0, hrRelative));

  let y: number;
  switch (sex) {
    case "M":
      y = 0.64 * Math.exp(1.92 * clampedHrRelative);
      break;
    case "F":
      y = 0.86 * Math.exp(1.67 * clampedHrRelative);
      break;
  }

  const durationMinutes = run.duration / 60;
  return durationMinutes * clampedHrRelative * y;
}

/**
 * Format TRIMP value for display
 */
export function formatTrimp(trimp: number | null): string {
  if (trimp === null || trimp === undefined) {
    return "--";
  }
  return trimp.toFixed(1);
}
