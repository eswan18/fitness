import {
  AllTimeStatsPanel,
  ShoeStatsPanel,
  TimePeriodStatsPanel,
  RecentRunsPanel,
} from "./panels";
import { RefreshButton } from "./components/RefreshButton";
import { EnvironmentIndicator } from "./components/EnvironmentIndicator";
import { ThemeToggle } from "./components/ThemeToggle";
import { Toaster } from "./components/ui/sonner";
import { notifySuccess, notifyInfo } from "@/lib/errors";
import type { RefreshDataResponse } from "./lib/api/fetch";

function App() {
  const handleRefreshComplete = (data: RefreshDataResponse) => {
    if (data.new_runs_inserted > 0) {
      notifySuccess(`Added ${data.new_runs_inserted} new runs`);
    } else {
      notifyInfo("No new runs found");
    }
  };

  return (
    <div className="flex flex-col min-h-screen py-4 px-12 bg-background text-foreground">
      <div className="flex justify-between items-start mb-8 flex-shrink-0">
        <div className="flex items-center gap-3">
          <h1 className="text-3xl font-semibold">Running Dashboard</h1>
          <EnvironmentIndicator />
        </div>
        <div className="flex items-center gap-2">
          <ThemeToggle />
          <RefreshButton onRefreshComplete={handleRefreshComplete} />
        </div>
      </div>
      <div className="flex flex-row justify-between gap-x-6 mb-8 flex-shrink-0">
        <AllTimeStatsPanel className="w-48 flex-grow-0" />
        <div className="flex-1 min-w-[480px]">
          <TimePeriodStatsPanel />
        </div>
        <ShoeStatsPanel className="w-96 flex-grow-0 flex-shrink-0" />
      </div>
      <div className="flex-1 min-h-0">
        <RecentRunsPanel />
      </div>
      <Toaster />
    </div>
  );
}

export default App;
