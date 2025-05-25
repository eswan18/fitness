import { DatePicker } from "./components/DatePicker";
import { SummaryBox } from "./components/SummaryBox";
import { Label } from "./components/ui/label";
import { daysInRange } from "./lib/utils";
import { useDashboardStore } from "./store";

export function TimePeriodStatsPanel() {
  const store = useDashboardStore();
  const dayCount = daysInRange(store.timeRangeStart, store.timeRangeEnd);
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
