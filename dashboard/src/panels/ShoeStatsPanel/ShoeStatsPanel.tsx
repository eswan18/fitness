import { useQuery } from "@tanstack/react-query";
import { fetchShoeMileage } from "@/lib/api";
import { ShoeMileageChart } from "./ShoeMileageChart";
import { Panel } from "@/components/Panel";
import { queryKeys } from "@/lib/queryKeys";

export function ShoeStatsPanel({ className }: { className?: string }) {
  const { data, isPending, error } = useQuery({
    queryKey: queryKeys.shoesMileage(true),
    queryFn: () => fetchShoeMileage(true),
  });

  return (
    <Panel title="Shoe Mileage" className={className} isLoading={isPending} error={error}>
      {data && <ShoeMileageChart data={data} />}
    </Panel>
  );
}