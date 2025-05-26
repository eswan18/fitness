import type { ShoeMileage } from "@/lib/api";
import { useMemo, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

export function ShoeMileageChart({ data }: { data: ShoeMileage[] }) {
  const [sortKey, setSortKey] = useState<"mileage" | "shoe">("mileage");

  const sortedData = useMemo(() => {
    return [...data].sort((a, b) => {
      if (sortKey === "mileage") {
        return b.mileage - a.mileage;
      } else {
        return a.shoe.localeCompare(b.shoe);
      }
    });
  }, [sortKey, data]);

  return (
    <div className="w-full max-w-4xl mx-auto">
      <div className="mb-4 flex justify-end gap-2">
        <button
          onClick={() => setSortKey("mileage")}
          className={`px-3 py-1 rounded border ${
            sortKey === "mileage" ? "bg-primary text-white" : "bg-muted"
          }`}
        >
          Sort by Mileage
        </button>
        <button
          onClick={() => setSortKey("shoe")}
          className={`px-3 py-1 rounded border ${
            sortKey === "shoe" ? "bg-primary text-white" : "bg-muted"
          }`}
        >
          Sort by Shoe
        </button>
      </div>
      <ResponsiveContainer width="100%" height={400}>
        <BarChart
          data={sortedData}
          layout="vertical"
          margin={{ top: 20, right: 40, bottom: 20, left: 120 }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            type="number"
            label={{
              value: "Miles",
              position: "insideBottomRight",
              offset: -5,
            }}
          />
          <YAxis
            type="category"
            dataKey="shoe"
            width={200}
            tick={{ fontSize: 12 }}
          />
          <Tooltip formatter={(value) => `${value.toFixed(1)} mi`} />
          <Bar dataKey="mileage" fill="hsl(var(--primary))" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
