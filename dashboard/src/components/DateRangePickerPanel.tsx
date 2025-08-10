import { DatePicker } from "@/components/DatePicker";
import { Label } from "@/components/ui/label";

export function DateRangePickerPanel({
  disabled,
  className,
  startDate,
  endDate,
  onStartChange,
  onEndChange,
}: {
  disabled?: boolean;
  className?: string;
  startDate: Date;
  endDate: Date;
  onStartChange: (date: Date) => void;
  onEndChange: (date: Date) => void;
}) {
  return (
    <div className={`flex flex-row w-full gap-x-4 ${className ?? ""}`}> 
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