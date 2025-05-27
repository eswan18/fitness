import { DatePicker } from "@/components/DatePicker";

import { Label } from "@/components/ui/label";
import { useDashboardStore } from "@/store";

export function DateRangePickerPanel(
  { disabled, className }: { disabled?: boolean; className?: string },
) {
  const { timeRangeStart, setTimeRangeStart, timeRangeEnd, setTimeRangeEnd } =
    useDashboardStore();
  return (
    <div className={`flex flex-row w-full gap-x-4 ${className}`}>
      <LabeledDatePicker
        label="Start Date"
        value={timeRangeStart}
        onChange={(date) => setTimeRangeStart(date)}
        disabled={disabled}
      />
      <LabeledDatePicker
        label="End Date"
        value={timeRangeEnd}
        onChange={(date) => setTimeRangeEnd(date)}
        disabled={disabled}
      />
    </div>
  );
}

function LabeledDatePicker({
  label,
  value,
  onChange,
  disabled = false,
}: {
  label: string;
  value: Date;
  onChange: (date: Date) => void;
  disabled?: boolean;
}) {
  return (
    <div className="flex flex-col gap-y-2">
      <Label className="mx-2">{label}</Label>
      <DatePicker value={value} onChange={onChange} disabled={disabled} />
    </div>
  );
}
