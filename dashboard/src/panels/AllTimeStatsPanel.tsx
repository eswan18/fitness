import { useQuery } from "@tanstack/react-query";
import { SummaryBox } from "@/components/SummaryBox";
import { fetchTotalMileage, fetchTotalSeconds } from "@/lib/api";
import { getUserTimezone } from "@/lib/timezone";
import { Panel } from "@/components/Panel";
import { queryKeys } from "@/lib/queryKeys";

export function AllTimeStatsPanel({ className }: { className?: string }) {
  const { miles, seconds, isPending, error } = useAllTimeStats();

  return (
    <Panel title="All Time" className={className} isLoading={isPending} error={error}>
      <div className="w-full shadow-none flex flex-col items-center gap-y-4">
        <SummaryBox title="Miles" value={Math.round(miles ?? 0).toLocaleString()} size="sm" />
        <SummaryBox title="Minutes" value={Math.round((seconds ?? 0) / 60).toLocaleString()} size="sm" />
      </div>
    </Panel>
  );
}

type AllTimeStatsResult =
  | { miles: undefined; seconds: undefined; isPending: true; error: null }
  | { miles: number; seconds: number; isPending: false; error: null }
  | { miles: undefined; seconds: undefined; isPending: false; error: Error };

function useAllTimeStats(): AllTimeStatsResult {
  const userTimezone = getUserTimezone();
  const metricsQueryResult = useQuery({
    queryKey: queryKeys.totalMiles({ userTimezone }),
    queryFn: () => fetchTotalMileage({ userTimezone }),
  });
  const secondsQueryResult = useQuery({
    queryKey: queryKeys.totalSeconds({ userTimezone }),
    queryFn: () => fetchTotalSeconds({ userTimezone }),
  });
  const isPending = metricsQueryResult.isPending || secondsQueryResult.isPending;
  const error = (metricsQueryResult.error ?? secondsQueryResult.error) as Error | null;
  if (isPending) {
    return { miles: undefined, seconds: undefined, isPending: true, error: null };
  }
  if (error) {
    return { miles: undefined, seconds: undefined, isPending: false, error };
  }
  return {
    miles: metricsQueryResult.data!,
    seconds: secondsQueryResult.data!,
    isPending: false,
    error: null,
  };
}
