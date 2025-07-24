import { CartesianGrid, ComposedChart, Line, XAxis, YAxis } from "recharts";
import {
  type ChartConfig,
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart";
import { format } from "date-fns";

export interface DayScore {
  date: Date;
  score: number;
}

export function BurdenOverTimeChart({
  title,
  lineData,
  lineLabel,
}: {
  title?: string;
  lineData: DayScore[];
  lineLabel: string;
}) {
  const chartData = lineData.map((d) => ({
    date: format(d.date, "MMM d"),
    line: d.score,
  }));

  const chartConfig: ChartConfig = {
    line: {
      label: lineLabel,
      color: "var(--primary)",
    },
  };

  return (
    <div className="w-full flex flex-col items-start">
      {title && <h3 className="mx-16 font-semibold">{title}</h3>}
      <ChartContainer config={chartConfig} className="w-full max-w-4xl mx-auto">
        <ComposedChart
          data={chartData}
          margin={{ top: 20, right: 20, bottom: 20, left: 10 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#dddddd" />
          <XAxis dataKey="date" tick={{ fontSize: 12 }} />
          <YAxis
            label={{
              value: lineLabel,
              angle: -90,
              dx: -10,
            }}
          />
          <ChartTooltip content={<ChartTooltipContent />} />
          <Line
            type="monotone"
            dataKey="line"
            stroke="var(--primary)"
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 4 }}
          />
        </ComposedChart>
      </ChartContainer>
    </div>
  );
}
