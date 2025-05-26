import { useQuery } from "@tanstack/react-query";
import { fetchShoeMileage } from "@/lib/api";
import { ShoeMileageChart } from "./ShoeMileageChart";
export function ShoesStatsPanel() {
  const { data, isPending, error } = useQuery({
    queryKey: ["miles", "by-shoe"],
    queryFn: fetchShoeMileage,
  });
  if (isPending) return <p>Loading...</p>;
  if (error) return <p>Error: {error.message}</p>;
  return (
    <div className="flex flex-col gap-y-4">
      <h2 className="text-xl font-semibold">Shoes</h2>
      <div className="flex flex-row w-full gap-x-4 rounded-md border">
        <ShoeMileageChart data={data} />
      </div>
    </div>
  );
}
