import { DatePicker } from "@/components/DatePicker";

import { Label } from "@/components/ui/label";
import { useDashboardStore } from "@/store";

export function DateRangePickerPanel({
  disabled,
  className,
  customStart,
  customEnd,
  onCustomStartChange,
  onCustomEndChange,
}: {
  disabled?: boolean;
  className?: string;
  customStart?: Date;
  customEnd?: Date;
  onCustomStartChange?: (date: Date) => void;
  onCustomEndChange?: (date: Date) => void;
}) {
  const { timeRangeStart, setTimeRangeStart, timeRangeEnd, setTimeRangeEnd } =
    useDashboardStore();

  // Use custom dates if provided, otherwise use store dates
  const startDate = customStart ?? timeRangeStart;
  const endDate = customEnd ?? timeRangeEnd;
  const onStartChange = onCustomStartChange ?? setTimeRangeStart;
  const onEndChange = onCustomEndChange ?? setTimeRangeEnd;

  return (
    <div className={`flex flex-row w-full gap-x-4 ${className}`}>
      <LabeledDatePicker
        label="Start Date"
        value={startDate}
        onChange={onStartChange}
        disabled={disabled}
      />
      <LabeledDatePicker
        label="End Date"
        value={endDate}
        onChange={onEndChange}
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
