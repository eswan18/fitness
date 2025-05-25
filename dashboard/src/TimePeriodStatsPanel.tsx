import { DatePicker } from "./components/DatePicker";
import { Label } from "./components/ui/label";
import { useDashboardStore } from "./store";

export function TimePeriodStatsPanel() {
  const store = useDashboardStore();
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
      <Label>{label}</Label>
      <DatePicker value={value} onChange={onChange} />
    </div>
  );
}
