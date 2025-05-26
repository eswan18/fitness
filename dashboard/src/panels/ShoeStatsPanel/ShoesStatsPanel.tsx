import { useQuery } from "@tanstack/react-query";
import { fetchShoeMileage } from "@/lib/api";
import { ShoeMileageChart } from "./ShoeMileageChart";
import { Card } from "@/components/ui/card";

export function ShoesStatsPanel() {
  const { data, isPending, error } = useQuery({
    queryKey: ["miles", "by-shoe"],
    queryFn: fetchShoeMileage,
  });
  if (isPending) return <p>Loading...</p>;
  if (error) return <p>Error: {error.message}</p>;
  return (
    <div className="flex flex-col gap-y-4">
      <h2 className="text-xl font-semibold">Shoe Mileage</h2>
      <Card className="shadow-none">
        <ShoeMileageChart data={data} />
      </Card>
    </div>
  );
}
