import {
  AllTimeStatsPanel,
  ShoesStatsPanel,
  TimePeriodStatsPanel,
  RecentRunsPanel,
} from "./panels";
import { RefreshButton } from "./components/RefreshButton";
import { Toaster } from "./components/ui/sonner";
import { toast } from "sonner";
import type { RefreshDataResponse } from "./lib/api/fetch";

function App() {
  const handleRefreshComplete = (data: RefreshDataResponse) => {
    if (data.new_runs_inserted > 0) {
      toast.success(`Added ${data.new_runs_inserted} new runs`);
    } else {
      toast.info("No new runs found");
    }
  };

  return (
    <div className="flex flex-col min-h-screen py-4 px-12">
      <div className="flex justify-between items-start mb-8 flex-shrink-0">
        <h1 className="text-3xl font-semibold">Running Dashboard</h1>
        <div className="flex flex-col items-end gap-2">
          <RefreshButton onRefreshComplete={handleRefreshComplete} />
        </div>
      </div>
      <div className="flex flex-row justify-between gap-x-4 mb-8 flex-shrink-0">
        <AllTimeStatsPanel className="w-48 flex-grow-0" />
        <TimePeriodStatsPanel />
        <ShoesStatsPanel className="w-96 flex-grow-0" />
      </div>
      <div className="flex-1 min-h-0">
        <RecentRunsPanel />
      </div>
      <Toaster />
    </div>
  );
}

export default App;
