import {
  BarChart,
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
  trimp: number;
}

export function DailyTrimpChart({
  title,
  data,
}: {
  title?: string;
  data: DayData[];
}) {
  const chartData = data.map((d) => ({
    date: format(d.date, "MMM d"),
    trimp: Math.round(d.trimp * 10) / 10,
  }));

  const chartConfig: ChartConfig = {
    trimp: {
      label: "TRIMP",
      color: "var(--primary)",
    },
  };

  return (
    <div className="w-full flex flex-col items-start">
      {title && <h3 className="mx-16 font-semibold">{title}</h3>}
      <ChartContainer config={chartConfig} className="w-full max-w-4xl mx-auto">
        <BarChart
          data={chartData}
          margin={{ top: 20, right: 50, bottom: 20, left: 50 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#dddddd"/>
          <XAxis dataKey="date" tick={{ fontSize: 12 }} />
          <YAxis 
            label={{
              value: "TRIMP",
              angle: -90,
              position: "insideLeft",
            }}
          />
          <ChartTooltip content={<ChartTooltipContent />} />
          <Bar dataKey="trimp" fill="var(--primary)" />
        </BarChart>
      </ChartContainer>
    </div>
  );
}