import {
  ComposedChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
} from "recharts";
import {
  type ChartConfig,
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart";
import { format } from "date-fns";

export interface DayData {
  date: Date;
  mileage: number;
  exertion: number;
}

export function MileageExertionChart({
  title,
  data,
}: {
  title?: string;
  data: DayData[];
}) {
  const chartData = data.map((d) => ({
    date: format(d.date, "MMM d"),
    mileage: d.mileage,
    exertion: d.exertion,
  }));

  const chartConfig: ChartConfig = {
    mileage: {
      label: "Daily Miles",
      color: "var(--primary)",
    },
    exertion: {
      label: "TRIMP",
      color: "var(--muted-foreground)",
    },
  };

  return (
    <div className="w-full flex flex-col items-start">
      {title && <h3 className="mx-16 font-semibold">{title}</h3>}
      <ChartContainer config={chartConfig} className="w-full max-w-4xl mx-auto">
        <ComposedChart
          data={chartData}
          margin={{ top: 20, right: 50, bottom: 20, left: 50 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#dddddd"/>
          <XAxis dataKey="date" tick={{ fontSize: 12 }} />
          <YAxis 
            yAxisId="mileage"
            label={{
              value: "Miles",
              angle: -90,
              position: "insideLeft",
            }}
          />
          <YAxis 
            yAxisId="exertion"
            orientation="right"
            label={{
              value: "TRIMP",
              angle: 90,
              position: "insideRight",
            }}
          />
          <ChartTooltip content={<ChartTooltipContent />} />
          <Bar yAxisId="mileage" dataKey="mileage" fill="var(--primary)" />
          <Bar yAxisId="exertion" dataKey="exertion" fill="var(--muted-foreground)" />
        </ComposedChart>
      </ChartContainer>
    </div>
  );
}