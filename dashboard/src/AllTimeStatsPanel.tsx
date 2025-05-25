import { SummaryBox } from "./components/SummaryBox";

export function AllTimeStatsPanel() {
  return (
    <div className="flex flex-col gap-y-4">
      <h2 className="text-xl font-semibold">All Time Stats</h2>
      <div className="flex flex-row w-full gap-x-4">
        <SummaryBox
          title="Miles"
          value="13,204"
          size="md"
          className="flex-grow-1"
        />
        <SummaryBox
          title="Minutes"
          value="4,132"
          size="md"
          className="flex-grow-1"
        />
      </div>
    </div>
  );
}
