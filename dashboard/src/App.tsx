import {
  AllTimeStatsPanel,
  ShoesStatsPanel,
  TimePeriodStatsPanel,
} from "./panels";
import { RefreshButton } from "./components/RefreshButton";
import { Toaster } from "./components/ui/sonner";
import { toast } from "sonner";
import type { RefreshDataResponse } from "./lib/api/fetch";

function App() {
  const handleRefreshComplete = (data: RefreshDataResponse) => {
    toast.success(`Loaded ${data.total_runs} runs`);
  };

  return (
    <div className="flex flex-col min-h-screen py-4 px-12">
      <div className="flex justify-between items-start mb-8">
        <h1 className="text-3xl font-semibold">
          Running Dashboard
        </h1>
        <div className="flex flex-col items-end gap-2">
          <RefreshButton onRefreshComplete={handleRefreshComplete} />
        </div>
      </div>
      <div className="flex flex-row justify-between gap-x-6">
        <AllTimeStatsPanel className="w-48 flex-grow-0" />
        <TimePeriodStatsPanel />
        <ShoesStatsPanel className="w-96 flex-grow-0" />
      </div>
      <Toaster />
    </div>
  );
}

export default App;
