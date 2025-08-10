import { useState } from "react";
import {
  ChevronDown,
  ChevronRight,
  MapPin,
  Clock,
  ArrowUp,
  ArrowDown,
  ArrowUpDown,
  MoreVertical,
  Edit,
  History,
  CalendarCheck,
} from "lucide-react";
import type { Run, RunSortBy, SortOrder, RunDetail } from "@/lib/api";
import {
  formatRunDate,
  formatRunTime,
  formatRunDistance,
  calculatePace,
  formatDuration,
  formatHeartRate,
  truncateText,
} from "@/lib/runUtils";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { RunEditDialog } from "./RunEditDialog";
import { RunHistoryDialog } from "./RunHistoryDialog";
import { SyncStatusBadge } from "@/components/SyncStatusBadge";
import { SyncButton } from "@/components/SyncButton";

interface RunsTableProps {
  runs: (Run | RunDetail)[];
  className?: string;
  sortBy?: RunSortBy;
  sortOrder?: SortOrder;
  onSort?: (sortBy: RunSortBy) => void;
  onRunUpdated?: () => void;
  onSyncChanged?: () => void;
}

export function RunsTable({
  runs,
  className,
  sortBy,
  sortOrder,
  onSort,
  onRunUpdated,
  onSyncChanged,
}: RunsTableProps) {
  const [expandedRows, setExpandedRows] = useState<Set<number>>(new Set());
  const [editRun, setEditRun] = useState<Run | RunDetail | null>(
    null,
  );
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [historyRun, setHistoryRun] = useState<RunDetail | null>(null);
  const [isHistoryDialogOpen, setIsHistoryDialogOpen] = useState(false);

  const toggleRow = (index: number) => {
    const newExpanded = new Set(expandedRows);
    if (newExpanded.has(index)) {
      newExpanded.delete(index);
    } else {
      newExpanded.add(index);
    }
    setExpandedRows(newExpanded);
  };

  const handleEditRun = (run: Run | RunDetail) => {
    setEditRun(run);
    setIsEditDialogOpen(true);
  };

  const handleViewHistory = (run: RunDetail) => {
    setHistoryRun(run);
    setIsHistoryDialogOpen(true);
  };

  const getSortIcon = (column: RunSortBy) => {
    if (sortBy !== column) {
      return <ArrowUpDown className="h-4 w-4 opacity-50" />;
    }
    return sortOrder === "asc" ? (
      <ArrowUp className="h-4 w-4" />
    ) : (
      <ArrowDown className="h-4 w-4" />
    );
  };

  const SortableHeader = ({
    children,
    sortKey,
    className = "",
  }: {
    children: React.ReactNode;
    sortKey: RunSortBy;
    className?: string;
  }) => {
    if (!onSort) {
      return (
        <th className={`p-3 font-medium bg-muted/50 ${className}`}>
          {children}
        </th>
      );
    }

    return (
      <th className={`p-3 font-medium bg-muted/50 ${className}`}>
        <button
          className="flex items-center gap-1 hover:text-foreground transition-colors"
          onClick={() => onSort(sortKey)}
        >
          {children}
          {getSortIcon(sortKey)}
        </button>
      </th>
    );
  };

  if (runs.length === 0) {
    return (
      <div className="text-center py-8 text-muted-foreground">
        <p>No runs found</p>
        <p className="text-sm mt-1">Try adjusting your filters</p>
      </div>
    );
  }

  return (
    <div
      className={cn(
        "border rounded-lg overflow-hidden flex flex-col",
        className,
      )}
    >
      <div className="overflow-auto flex-1">
        <table className="w-full">
          <thead className="bg-background border-b sticky top-0 z-10">
            <tr className="text-left bg-muted/50">
              <th className="w-8 p-3 bg-muted/50"></th>
              <SortableHeader sortKey="date">Date</SortableHeader>
              <th className="w-12 p-3 font-medium bg-muted/50 text-center">Calendar</th>
              <SortableHeader sortKey="distance">Distance</SortableHeader>
              <SortableHeader sortKey="pace" className="hidden sm:table-cell">
                Pace
              </SortableHeader>
              <SortableHeader
                sortKey="heart_rate"
                className="hidden md:table-cell"
              >
                HR
              </SortableHeader>
              <SortableHeader sortKey="shoes" className="hidden lg:table-cell">
                Shoes
              </SortableHeader>
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
                onEdit={() => handleEditRun(run)}
                onViewHistory={() =>
                  "id" in run
                    ? handleViewHistory(run as RunDetail)
                    : undefined
                }
                onSyncChanged={onSyncChanged}
              />
            ))}
          </tbody>
        </table>
      </div>

      <RunEditDialog
        run={editRun}
        open={isEditDialogOpen}
        onOpenChange={setIsEditDialogOpen}
        onRunUpdated={onRunUpdated}
      />

      <RunHistoryDialog
        run={historyRun}
        open={isHistoryDialogOpen}
        onOpenChange={setIsHistoryDialogOpen}
      />
    </div>
  );
}

interface RunTableRowProps {
  run: Run | RunDetail;
  index: number;
  isExpanded: boolean;
  onToggle: () => void;
  onEdit: () => void;
  onViewHistory: () => void;
  onSyncChanged?: () => void;
}

function RunTableRow({
  run,
  isExpanded,
  onToggle,
  onEdit,
  onViewHistory,
  onSyncChanged,
}: RunTableRowProps) {
  try {
    const isRunWithId = "id" in run;
    const runId = isRunWithId ? (run as RunDetail).id : undefined;
    const isSynced = (run as RunDetail & { is_synced?: boolean }).is_synced === true;
    return (
      <>
        <tr
          className="group border-b hover:bg-muted/30 cursor-pointer transition-colors"
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
          <td className="p-3">
            <div className="flex items-center gap-1">
              <div className="flex flex-col">
                <span className="font-medium">{formatRunDate(run.date)}</span>
                {run.datetime && (
                  <span className="text-xs text-muted-foreground">
                    {formatRunTime(run.datetime)}
                  </span>
                )}
              </div>

              {/* Only show edit button for runs with IDs (RunWithShoes) */}
              {"id" in run && (
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-8 w-8 p-0 opacity-0 group-hover:opacity-100 hover:opacity-100 transition-opacity ml-1"
                      onClick={(e) => e.stopPropagation()}
                    >
                      <MoreVertical className="h-4 w-4" />
                      <span className="sr-only">More actions</span>
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    <DropdownMenuItem
                      onClick={(e) => {
                        e.stopPropagation();
                        onEdit();
                      }}
                      className="gap-2"
                    >
                      <Edit className="h-4 w-4" />
                      Edit Run
                    </DropdownMenuItem>
                    {"id" in run && (
                      <DropdownMenuItem
                        onClick={(e) => {
                          e.stopPropagation();
                          onViewHistory();
                        }}
                        className="gap-2"
                      >
                        <History className="h-4 w-4" />
                        View History
                      </DropdownMenuItem>
                    )}
                    {isRunWithId && (
                      <DropdownMenuItem
                        onClick={async (e) => {
                          e.stopPropagation();
                          if (!runId) return;
                          try {
                            if (isSynced) {
                              const { unsyncRun } = await import("@/lib/api");
                              await unsyncRun(runId);
                            } else {
                              const { syncRun } = await import("@/lib/api");
                              await syncRun(runId);
                            }
                            onSyncChanged?.();
                          } catch (err) {
                            console.error(err);
                          }
                        }}
                        className="gap-2"
                      >
                        {isSynced ? "Remove from Google Calendar" : "Sync to Google Calendar"}
                      </DropdownMenuItem>
                    )}
                  </DropdownMenuContent>
                </DropdownMenu>
              )}
            </div>
          </td>
          {/* Calendar column - second column */}
          <td className="w-12 p-3 text-center">
            {isRunWithId && isSynced ? (
              <span
                className="inline-flex items-center justify-center"
                aria-label="Synced to Google Calendar"
                title="Synced to Google Calendar"
              >
                <CalendarCheck className="h-4 w-4 text-emerald-600" />
              </span>
            ) : null}
          </td>
          <td className="p-3">{formatRunDistance(run.distance)} mi</td>
          <td className="p-3 font-mono text-sm hidden sm:table-cell">
            {calculatePace(run.distance, run.duration)}
          </td>
          <td className="p-3 hidden md:table-cell">
            {formatHeartRate(run.avg_heart_rate)}
          </td>
          <td className="p-3 text-sm text-muted-foreground hidden lg:table-cell">
            {truncateText(run.shoes, 20)}
          </td>
        </tr>
        {isExpanded && (
          <tr className="border-b bg-muted/20">
            <td></td>
            <td colSpan={6} className="p-3">
              <RunExpandedDetails run={run} />
              {isRunWithId && (
                <div className="mt-3 flex items-center gap-2">
                  <SyncStatusBadge
                    status={(run as RunDetail & { sync_status?: any }).sync_status}
                    errorMessage={(run as RunDetail & { error_message?: string | null }).error_message || null}
                  />
                  <SyncButton runId={runId!} isSynced={!!isSynced} onDone={onSyncChanged} />
                </div>
              )}
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

function RunExpandedDetails({ run }: { run: Run | RunDetail }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 py-2">
      {/* Show pace on mobile (hidden in main row) */}
      <div className="flex items-center gap-2 sm:hidden">
        <span className="text-sm">
          <span className="font-medium">Pace:</span>{" "}
          {calculatePace(run.distance, run.duration)}
        </span>
      </div>

      {/* Show HR on mobile and small screens (hidden in main row) */}
      <div className="flex items-center gap-2 md:hidden">
        <span className="text-sm">
          <span className="font-medium">HR:</span>{" "}
          {formatHeartRate(run.avg_heart_rate)}{" "}
          {run.avg_heart_rate ? "bpm" : ""}
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
          <span className="font-medium">Duration:</span>{" "}
          {formatDuration(run.duration)}
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
        <span className="font-medium">Full Date:</span>{" "}
        {run.datetime
          ? run.datetime.toLocaleString()
          : run.date.toLocaleDateString()}
      </div>
    </div>
  );
}
