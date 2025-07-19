import { useState } from "react";
import {
  AllTimeStatsPanel,
  ShoesStatsPanel,
  TimePeriodStatsPanel,
} from "./panels";
import { RefreshButton } from "./components/RefreshButton";
import type { RefreshDataResponse } from "./lib/api/fetch";

function App() {
  const [refreshStatus, setRefreshStatus] = useState<string | null>(null);

  const handleRefreshComplete = (data: RefreshDataResponse) => {
    setRefreshStatus(`Loaded ${data.total_runs} runs`);
    // Clear the status after 3 seconds
    setTimeout(() => setRefreshStatus(null), 3000);
  };

  return (
    <div className="flex flex-col min-h-screen py-4 px-12">
      <div className="flex justify-between items-start mb-8">
        <h1 className="text-3xl font-semibold">
          Running Dashboard
        </h1>
        <div className="flex flex-col items-end gap-2">
          <RefreshButton onRefreshComplete={handleRefreshComplete} />
          {refreshStatus && (
            <span className="text-sm text-green-600 font-medium">
              {refreshStatus}
            </span>
          )}
        </div>
      </div>
      <div className="flex flex-row justify-between gap-x-6">
        <AllTimeStatsPanel className="w-48 flex-grow-0" />
        <TimePeriodStatsPanel />
        <ShoesStatsPanel className="w-96 flex-grow-0" />
      </div>
    </div>
  );
}

export default App;
