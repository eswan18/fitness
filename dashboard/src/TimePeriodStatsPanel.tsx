import { DatePicker } from "./components/DatePicker";
import { Label } from "./components/ui/label";

const DEFAULT_START_DATE = new Date(2016, 0, 1); // January 1, 2016
const DEFAULT_END_DATE = new Date(); // Today

export function TimePeriodStatsPanel() {
  console.log(DEFAULT_START_DATE);
  return (
    <div className="flex flex-col gap-y-4">
      <h2 className="text-xl font-semibold">Time Period</h2>
      <div className="flex flex-row w-full gap-x-4">
        <LabeledDatePicker
          label="Start Date"
          initialDate={DEFAULT_START_DATE}
        />
        <LabeledDatePicker label="End Date" initialDate={DEFAULT_END_DATE} />
      </div>
    </div>
  );
}

function LabeledDatePicker(
  { label, initialDate }: { label: string; initialDate: Date },
) {
  return (
    <div className="flex flex-col gap-y-2">
      <Label>{label}</Label>
      <DatePicker initialDate={initialDate} />
    </div>
  );
}
