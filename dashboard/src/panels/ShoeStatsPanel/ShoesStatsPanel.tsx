import { useQuery } from "@tanstack/react-query";
import { fetchShoeMileage } from "@/lib/api";
import { ShoeMileageChart } from "./ShoeMileageChart";
import { Card } from "@/components/ui/card";
import { LoadingSpinner } from "@/components/LoadingSpinner";

export function ShoesStatsPanel({ className }: { className?: string }) {
  const { data, isPending, error } = useQuery({
    queryKey: ["miles", "by-shoe", "include-retired"],
    queryFn: () => fetchShoeMileage(true),
  });
  if (isPending) {
    return (
      <div className={`flex flex-col gap-y-4 ${className}`}>
        <h2 className="text-xl font-semibold">Shoe Mileage</h2>
        <Card className="w-full shadow-none flex justify-center py-12">
          <LoadingSpinner />
        </Card>
      </div>
    );
  }
  if (error) return <p>Error: {error.message}</p>;
  return (
    <div className={`flex flex-col gap-y-4 ${className}`}>
      <h2 className="text-xl font-semibold">Shoe Mileage</h2>
      <Card className="w-full shadow-none">
        <ShoeMileageChart data={data} />
      </Card>
    </div>
  );
}
