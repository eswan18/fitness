import {
  CartesianGrid,
  ComposedChart,
  Line,
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
import { format } from "date-fns";
import type { DayTrainingLoad } from "@/lib/api";

export interface FlatDayTrainingLoad {
  date: string;
  atl: number; // Acute Training Load
  ctl: number; // Chronic Training Load
  tsb: number; // Training Stress Balance
}

export function FreshnessChart({
  title,
  data,
}: {
  title?: string;
  data: DayTrainingLoad[];
}) {
  const chartData = data.map((d) => ({
    date: format(d.date, "MMM d"),
    tsb: d.training_load.tsb,
    atl: d.training_load.atl,
    ctl: d.training_load.ctl,
  })) satisfies FlatDayTrainingLoad[];

  const chartConfig = {
    tsb: {
      label: "Freshness (TSB)",
      color: "var(--primary)",
    },
    atl: {
      label: "Fatigue (ATL)",
      color: "var(--muted-foreground)",
    },
    ctl: {
      label: "Fitness (CTL)",
      color: "var(--destructive)",
    },
  } satisfies ChartConfig;

  return (
    <div className="w-full flex flex-col items-start">
      {title && <h3 className="mx-16 font-semibold">{title}</h3>}
      <ChartContainer config={chartConfig} className="w-full max-w-4xl mx-auto">
        <ComposedChart
          data={chartData}
          margin={{ top: 20, right: 20, bottom: 20, left: 10 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#dddddd"/>
          <XAxis dataKey="date" tick={{ fontSize: 12 }} />
          <YAxis
            label={{
              value: "Score",
              angle: -90,
              dx: -10,
            }}
          />
          <ChartTooltip content={<ChartTooltipContent />} />
          <Line
            type="monotone"
            dataKey="tsb"
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 4 }}
          />
          <Line
            type="monotone"
            dataKey="atl"
            stroke="#b86161"
            strokeWidth={0.7}
            dot={false}
            activeDot={{ r: 4 }}
          />
          <Line
            type="monotone"
            dataKey="ctl"
            stroke="#5c935c"
            strokeWidth={0.7}
            dot={false}
            activeDot={{ r: 4 }}
          />
          <ReferenceLine
            y={0}
            stroke="var(--primary)"
            strokeWidth={1}
            strokeDasharray="3 3"
          />
        </ComposedChart>
      </ChartContainer>
    </div>
  );
}
