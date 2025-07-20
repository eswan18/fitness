import { useQuery } from "@tanstack/react-query";
import { SummaryBox } from "@/components/SummaryBox";
import { fetchTotalMileage, fetchTotalSeconds } from "@/lib/api";
import { getUserTimezone } from "@/lib/timezone";
import { Card } from "@/components/ui/card";

export function AllTimeStatsPanel({ className }: { className?: string }) {
  const { miles, seconds, isPending, error } = useAllTimeStats();
  if (isPending) {
    return <p>Loading...</p>;
  }
  if (error) {
    return <p>Error: {error.message}</p>;
  }
  return (
    <div className={`flex flex-col gap-y-4 ${className}`}>
      <h2 className="text-xl font-semibold">All Time</h2>
      <Card className="w-full shadow-none flex flex-col items-center gap-y-4">
        <SummaryBox
          title="Miles"
          value={Math.round(miles).toLocaleString()}
          size="sm"
        />
        <SummaryBox
          title="Minutes"
          value={Math.round(seconds / 60).toLocaleString()}
          size="sm"
        />
      </Card>
    </div>
  );
}

type AllTimeStatsResult =
  | {
      miles: undefined;
      seconds: undefined;
      isPending: true;
      error: null;
    }
  | {
      miles: number;
      seconds: number;
      isPending: false;
      error: null;
    }
  | {
      miles: undefined;
      seconds: undefined;
      isPending: false;
      error: Error;
    };

function useAllTimeStats(): AllTimeStatsResult {
  const userTimezone = getUserTimezone();
  const metricsQueryResult = useQuery({
    queryKey: ["miles", "total", userTimezone],
    queryFn: () => fetchTotalMileage({ userTimezone }),
  });
  const secondsQueryResult = useQuery({
    queryKey: ["seconds", "total", userTimezone],
    queryFn: () => fetchTotalSeconds({ userTimezone }),
  });
  const isPending =
    metricsQueryResult.isPending || secondsQueryResult.isPending;
  const error = metricsQueryResult.error ?? secondsQueryResult.error;
  if (isPending) {
    return {
      miles: undefined,
      seconds: undefined,
      isPending: true,
      error: null,
    };
  }
  if (error) {
    return {
      miles: undefined,
      seconds: undefined,
      isPending: false,
      error,
    };
  }
  return {
    miles: metricsQueryResult.data!,
    seconds: secondsQueryResult.data!,
    isPending: false,
    error: null,
  };
}
