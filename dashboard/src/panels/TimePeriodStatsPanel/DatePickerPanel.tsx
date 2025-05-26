import { DatePicker } from "@/components/DatePicker";

import { Label } from "@/components/ui/label";
import { useDashboardStore } from "@/store";

export function DatePickerPanel() {
  const { timeRangeStart, setTimeRangeStart, timeRangeEnd, setTimeRangeEnd } =
    useDashboardStore();
  return (
    <div className="flex flex-row w-full gap-x-4">
      <LabeledDatePicker
        label="Start Date"
        value={timeRangeStart}
        onChange={(date) => setTimeRangeStart(date)}
      />
      <LabeledDatePicker
        label="End Date"
        value={timeRangeEnd}
        onChange={(date) => setTimeRangeEnd(date)}
      />
    </div>
  );
}

function LabeledDatePicker({
  label,
  value,
  onChange,
}: {
  label: string;
  value: Date;
  onChange: (date: Date) => void;
}) {
  return (
    <div className="flex flex-col gap-y-2">
      <Label className="mx-2">{label}</Label>
      <DatePicker value={value} onChange={onChange} />
    </div>
  );
}
