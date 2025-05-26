import {
  AllTimeStatsPanel,
  ShoesStatsPanel,
  TimePeriodStatsPanel,
} from "./panels";

function App() {
  return (
    <div className="flex flex-col min-h-screen py-4 px-12">
      <h1 className="text-3xl w-full text-left font-semibold mb-8">
        Fitness Dashboard
      </h1>
      <div className="flex flex-row justify-between">
        <AllTimeStatsPanel className="w-48 flex-grow-0" />
        <TimePeriodStatsPanel />
        <ShoesStatsPanel className="w-88 flex-grow-0" />
      </div>
    </div>
  );
}

export default App;
