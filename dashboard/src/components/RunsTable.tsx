import { useState } from "react";
import { ChevronDown, ChevronRight, MapPin, Clock } from "lucide-react";
import type { Run } from "@/lib/api";
import {
  formatRunDate,
  formatRunDistance,
  calculatePace,
  formatDuration,
  formatHeartRate,
  truncateText,
} from "@/lib/runUtils";
import { cn } from "@/lib/utils";

interface RunsTableProps {
  runs: Run[];
  className?: string;
}

export function RunsTable({ runs, className }: RunsTableProps) {
  const [expandedRows, setExpandedRows] = useState<Set<number>>(new Set());

  const toggleRow = (index: number) => {
    const newExpanded = new Set(expandedRows);
    if (newExpanded.has(index)) {
      newExpanded.delete(index);
    } else {
      newExpanded.add(index);
    }
    setExpandedRows(newExpanded);
  };

  if (runs.length === 0) {
    return (
      <div className="text-center py-8 text-muted-foreground">
        No runs found
      </div>
    );
  }

  return (
    <div className={cn("border rounded-lg overflow-hidden flex flex-col", className)}>
      <div className="overflow-auto flex-1">
        <table className="w-full">
          <thead className="bg-background border-b sticky top-0 z-10">
            <tr className="text-left bg-muted/50">
              <th className="w-8 p-3 bg-muted/50"></th>
              <th className="p-3 font-medium bg-muted/50">Date</th>
              <th className="p-3 font-medium bg-muted/50">Distance</th>
              <th className="p-3 font-medium bg-muted/50 hidden sm:table-cell">Pace</th>
              <th className="p-3 font-medium bg-muted/50 hidden md:table-cell">HR</th>
              <th className="p-3 font-medium bg-muted/50 hidden lg:table-cell">Shoes</th>
            </tr>
          </thead>
          <tbody>
            {runs.map((run, index) => (
              <RunTableRow
                key={`${run.date.toISOString()}-${index}`}
                run={run}
                index={index}
                isExpanded={expandedRows.has(index)}
                onToggle={() => toggleRow(index)}
              />
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

interface RunTableRowProps {
  run: Run;
  index: number;
  isExpanded: boolean;
  onToggle: () => void;
}

function RunTableRow({ run, isExpanded, onToggle }: RunTableRowProps) {
  try {
    return (
      <>
        <tr 
          className="border-b hover:bg-muted/30 cursor-pointer transition-colors"
          onClick={onToggle}
        >
          <td className="p-3">
            <button 
              className="flex items-center justify-center w-6 h-6 rounded hover:bg-muted transition-colors"
              onClick={(e) => {
                e.stopPropagation();
                onToggle();
              }}
            >
              {isExpanded ? (
                <ChevronDown className="h-4 w-4" />
              ) : (
                <ChevronRight className="h-4 w-4" />
              )}
            </button>
          </td>
          <td className="p-3 font-medium">{formatRunDate(run.date)}</td>
          <td className="p-3">{formatRunDistance(run.distance)} mi</td>
          <td className="p-3 font-mono text-sm hidden sm:table-cell">{calculatePace(run.distance, run.duration)}</td>
          <td className="p-3 hidden md:table-cell">{formatHeartRate(run.avg_heart_rate)}</td>
          <td className="p-3 text-sm text-muted-foreground hidden lg:table-cell">
            {truncateText(run.shoes, 20)}
          </td>
        </tr>
        {isExpanded && (
          <tr className="border-b bg-muted/20">
            <td></td>
            <td colSpan={5} className="p-3">
              <RunExpandedDetails run={run} />
            </td>
          </tr>
        )}
      </>
    );
  } catch (error) {
    console.error("Error rendering run row:", error, run);
    return (
      <tr className="border-b">
        <td colSpan={6} className="p-3 text-destructive">
          Error displaying run data
        </td>
      </tr>
    );
  }
}

function RunExpandedDetails({ run }: { run: Run }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 py-2">
      {/* Show pace on mobile (hidden in main row) */}
      <div className="flex items-center gap-2 sm:hidden">
        <span className="text-sm">
          <span className="font-medium">Pace:</span> {calculatePace(run.distance, run.duration)}
        </span>
      </div>
      
      {/* Show HR on mobile and small screens (hidden in main row) */}
      <div className="flex items-center gap-2 md:hidden">
        <span className="text-sm">
          <span className="font-medium">HR:</span> {formatHeartRate(run.avg_heart_rate)} {run.avg_heart_rate ? 'bpm' : ''}
        </span>
      </div>
      
      {/* Show shoes on mobile/tablet (hidden in main row) */}
      {run.shoes && (
        <div className="text-sm lg:hidden">
          <span className="font-medium">Shoes:</span> {run.shoes}
        </div>
      )}
      
      <div className="flex items-center gap-2">
        <Clock className="h-4 w-4 text-muted-foreground" />
        <span className="text-sm">
          <span className="font-medium">Duration:</span> {formatDuration(run.duration)}
        </span>
      </div>
      
      <div className="flex items-center gap-2">
        <MapPin className="h-4 w-4 text-muted-foreground" />
        <span className="text-sm">
          <span className="font-medium">Source:</span> {run.source}
        </span>
      </div>
      
      <div className="text-sm">
        <span className="font-medium">Type:</span> {run.type}
      </div>
      
      <div className="text-sm">
        <span className="font-medium">Full Date:</span> {run.date.toLocaleDateString()}
      </div>
    </div>
  );
}