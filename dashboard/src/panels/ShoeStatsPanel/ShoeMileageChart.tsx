import { useMemo, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ReferenceLine,
  XAxis,
  YAxis,
} from "recharts";
import {
  type ChartConfig,
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import type { ShoeMileage } from "@/lib/api";

const chartConfig = {
  mileage: {
    label: "Mileage",
    color: "hsl(var(--primary))",
  },
} satisfies ChartConfig;

export function ShoeMileageChart({ data }: { data: ShoeMileage[] }) {
  const [sortKey, setSortKey] = useState<"mileage" | "shoe">("mileage");
  const [excludeLowMileage, setExcludeLowMileage] = useState(true);

  const chartData = useMemo(() => {
    return [...data]
      .filter((d) => !excludeLowMileage || d.mileage >= 100)
      .sort((a, b) =>
        sortKey === "mileage"
          ? b.mileage - a.mileage
          : a.shoe.localeCompare(b.shoe)
      )
      .map((d) => ({
        shoe: d.shoe,
        mileage: d.mileage,
      }));
  }, [data, sortKey, excludeLowMileage]);
  const minHeight = excludeLowMileage ? 64 : 120;
  return (
    <div className="w-full flex flex-row gap-x-4">
      <ChartContainer
        config={chartConfig}
        className={`max-w-xl mx-auto min-h-${minHeight} flex-grow-1`}
      >
        <BarChart
          accessibilityLayer
          data={chartData}
          layout="vertical"
          margin={{ top: 10, right: 10, bottom: 10, left: 10 }}
          height={800}
        >
          <ReferenceLine
            x={300}
            stroke="var(--destructive)"
            strokeDasharray="4 2"
            opacity={0.3}
          />
          <ReferenceLine
            x={500}
            stroke="var(--destructive)"
            strokeDasharray="4 2"
          />
          <CartesianGrid strokeDasharray="3 4" horizontal={false} />
          <XAxis type="number" ticks={[0, 100, 200, 300, 400, 500]} />
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
      <div className="py-2 w-48 flex flex-col items-start justify-start gap-y-8 flex-grow-0">
        <div className="flex flex-col gap-y-1">
          <Label
            htmlFor="sort-select"
            className="mx-2 block text-sm font-medium"
          >
            Sort By
          </Label>
          <Select
            value={sortKey}
            onValueChange={(val) => setSortKey(val as "mileage" | "shoe")}
          >
            <SelectTrigger id="sort-select">
              <SelectValue placeholder="Select sort key" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="mileage">Mileage</SelectItem>
              <SelectItem value="shoe">Shoe Name</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div className="flex flex-col items-start justify-between gap-y-1">
          <Label
            htmlFor="exclude-switch"
            className="mx-2 text-sm font-medium text-wrap"
          >
            Shoes under 100 miles
          </Label>
          <div className="mx-2 flex flex-row justify-start items-center gap-x-2">
            <Label htmlFor="exclude-switch" className="text-foreground">Exclude</Label>
            <Switch
              id="exclude-switch"
              checked={excludeLowMileage}
              onCheckedChange={setExcludeLowMileage}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
