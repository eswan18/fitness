import { useQuery } from "@tanstack/react-query";
import { SummaryBox } from "./components/SummaryBox";
import { fetchTotalMileage, fetchTotalSeconds } from "./lib/api";

export function AllTimeStatsPanel() {
  const metricsQueryResult = useQuery({
    queryKey: ["miles", "total"],
    queryFn: fetchTotalMileage,
  });
  const secondsQueryResult = useQuery({
    queryKey: ["seconds", "total"],
    queryFn: fetchTotalSeconds,
  });
  if (metricsQueryResult.isPending || secondsQueryResult.isPending) {
    return <p>Loading...</p>;
  }
  if (metricsQueryResult.error) {
    return <p>Error: {metricsQueryResult.error.message}</p>;
  }
  if (secondsQueryResult.error) {
    return <p>Error: {secondsQueryResult.error.message}</p>;
  }
  return (
    <div className="flex flex-col gap-y-4">
      <h2 className="text-xl font-semibold">All Time</h2>
      <div className="flex flex-row w-full gap-x-4">
        <SummaryBox
          title="Miles"
          value={Math.round(metricsQueryResult.data).toLocaleString()}
          size="md"
          className="flex-grow-1"
        />
        <SummaryBox
          title="Minutes"
          value={Math.round(secondsQueryResult.data / 60).toLocaleString()}
          size="md"
          className="flex-grow-1"
        />
      </div>
    </div>
  );
}
