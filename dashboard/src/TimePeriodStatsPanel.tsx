import { DatePicker } from "./components/DatePicker";
import { SummaryBox } from "./components/SummaryBox";
import { Label } from "./components/ui/label";
import { daysInRange } from "./lib/utils";
import { useDashboardStore } from "./store";
import { useQuery } from "@tanstack/react-query";
import { fetchRuns } from "@/lib/api";

export function TimePeriodStatsPanel() {
  const store = useDashboardStore();
  const { timeRangeStart, timeRangeEnd } = store;
  const dayCount = daysInRange(timeRangeStart, timeRangeEnd);
  const { data, isLoading, error } = useQuery({
    queryKey: ["runs", { startDate: timeRangeStart, endDate: timeRangeEnd }],
    queryFn: () =>
      fetchRuns({
        startDate: timeRangeStart,
        endDate: timeRangeEnd,
      }),
  });
  if (isLoading) return <p>Loading...</p>;
  if (error instanceof Error) return <p>Error: {error.message}</p>;

  return (
    <div className="flex flex-col gap-y-4">
      <h2 className="text-xl font-semibold">Time Period</h2>
      <div className="flex flex-row w-full gap-x-4">
        <LabeledDatePicker
          label="Start Date"
          value={store.timeRangeStart}
          onChange={(date) => store.setTimeRangeStart(date)}
        />
        <LabeledDatePicker
          label="End Date"
          value={store.timeRangeEnd}
          onChange={(date) => store.setTimeRangeEnd(date)}
        />
      </div>
      <div className="flex flex-row w-full gap-x-4">
        <SummaryBox
          title="Days"
          value={dayCount}
          size="sm"
        />
        <SummaryBox
          title="Miles"
          value={331}
          size="sm"
        />
        <SummaryBox
          title="Miles/Day"
          value={2.3}
          size="sm"
        />
        <SummaryBox
          title="Runs"
          value={data && data.length}
          size="sm"
        />
      </div>
    </div>
  );
}

function LabeledDatePicker(
  { label, value, onChange }: {
    label: string;
    value: Date;
    onChange: (date: Date) => void;
  },
) {
  return (
    <div className="flex flex-col gap-y-2">
      <Label className="mx-2">{label}</Label>
      <DatePicker value={value} onChange={onChange} />
    </div>
  );
}
