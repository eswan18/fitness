import type { Run, RunDetail } from "@/lib/api";

export function isRunDetail(run: Run | RunDetail): run is RunDetail {
  const maybeId = (run as Partial<RunDetail>).id;
  return typeof maybeId === "string" && maybeId.length > 0;
}
