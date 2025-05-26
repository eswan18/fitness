import { useMemo, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  XAxis,
  YAxis,
} from "recharts";
import {
  type ChartConfig,
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart";
import { Button } from "@/components/ui/button";
import type { ShoeMileage } from "@/lib/api";

const chartConfig = {
  mileage: {
    label: "Mileage",
    color: "hsl(var(--primary))",
  },
} satisfies ChartConfig;

export function ShoeMileageChart({ data }: { data: ShoeMileage[] }) {
  const [sortKey, setSortKey] = useState<"mileage" | "shoe">("mileage");

  const sortedData = useMemo(() => {
    return [...data]
      .sort((a, b) =>
        sortKey === "mileage"
          ? b.mileage - a.mileage
          : a.shoe.localeCompare(b.shoe)
      )
      .map((d) => ({
        shoe: d.shoe,
        mileage: d.mileage,
      }));
  }, [data, sortKey]);

  return (
    <div className="w-full">
      <div className="mb-4 flex justify-end gap-2">
        <Button
          variant={sortKey === "mileage" ? "default" : "outline"}
          onClick={() => setSortKey("mileage")}
        >
          Sort by Mileage
        </Button>
        <Button
          variant={sortKey === "shoe" ? "default" : "outline"}
          onClick={() => setSortKey("shoe")}
        >
          Sort by Shoe
        </Button>
      </div>
      <ChartContainer config={chartConfig} className="w-full max-w-4xl mx-auto">
        <BarChart
          accessibilityLayer
          data={sortedData}
          layout="vertical"
          margin={{ top: 10, right: 10, bottom: 10, left: 10 }}
          height={800}
        >
          <CartesianGrid strokeDasharray="3 4" horizontal={false} />
          <XAxis type="number" />
          <YAxis
            type="category"
            dataKey="shoe"
            width={200}
            tick={{ fontSize: 12 }}
          />
          <ChartTooltip content={<ChartTooltipContent />} />
          <Bar dataKey="mileage" fill="var(--primary)" radius={4} />
        </BarChart>
      </ChartContainer>
    </div>
  );
}
