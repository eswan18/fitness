import { useState } from "react";
import { SummaryBox } from "./components/SummaryBox";

function App() {
  return (
    <div className="flex flex-col min-h-screen">
      <div className="h-8 bg-muted w-full"></div>
      <div className="w-3xl mx-auto pt-4">
        <h1 className="text-3xl w-full text-left font-semibold">
          Fitness Dashboard
        </h1>
        <div className="flex flex-row gap-4 flex-wrap">
          <SummaryBox title="All-time Distance" value="13,204" size="sm" />
          <SummaryBox title="All-time Distance" value="13,204" size="md" />
          <SummaryBox title="All-time Distance" value="13,204" size="lg" />
        </div>
      </div>
    </div>
  );
}

export default App;
