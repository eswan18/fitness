import { useQuery } from "@tanstack/react-query";
import { SummaryBox } from "./components/SummaryBox";
import { fetchTotalMileage, fetchTotalSeconds } from "./lib/api";

export function AllTimeStatsPanel() {
  const { miles, seconds, isPending, error } = useAllTimeStats();
  if (isPending) {
    return <p>Loading...</p>;
  }
  if (error) {
    return <p>Error: {error.message}</p>;
  }
  return (
    <div className="flex flex-col gap-y-4">
      <h2 className="text-xl font-semibold">All Time</h2>
      <div className="flex flex-row w-full gap-x-4">
        <SummaryBox
          title="Miles"
          value={Math.round(miles).toLocaleString()}
          size="md"
          className="flex-grow-1"
        />
        <SummaryBox
          title="Minutes"
          value={Math.round(seconds / 60).toLocaleString()}
          size="md"
          className="flex-grow-1"
        />
      </div>
    </div>
  );
}

type AllTimeStatsResult = {
  miles: undefined;
  seconds: undefined;
  isPending: true;
  error: null;
} | {
  miles: number;
  seconds: number;
  isPending: false;
  error: null;
} | {
  miles: undefined;
  seconds: undefined;
  isPending: false
  error: Error;
};

function useAllTimeStats(): AllTimeStatsResult {
  const metricsQueryResult = useQuery({
    queryKey: ["miles", "total"],
    queryFn: () => fetchTotalMileage(),
  });
  const secondsQueryResult = useQuery({
    queryKey: ["seconds", "total"],
    queryFn: () => fetchTotalSeconds(),
  });
  const isPending = metricsQueryResult.isPending ||
    secondsQueryResult.isPending;
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
