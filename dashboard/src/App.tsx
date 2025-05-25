import { AllTimeStatsPanel } from "./AllTimeStatsPanel";

function App() {
  return (
    <div className="flex flex-col min-h-screen">
      <div className="h-8 border-b w-full"></div>
      <div className="w-3xl mx-auto pt-8 flex flex-col gap-y-8">
        <h1 className="text-3xl w-full text-left font-semibold">
          Fitness Dashboard
        </h1>
        <AllTimeStatsPanel />
      </div>
    </div>
  );
}

export default App;
