import { useEffect, useMemo, useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { fetchRunDetails, type RunDetail, syncRun } from "@/lib/api";
import { queryKeys } from "@/lib/queryKeys";
import { getUserTimezone } from "@/lib/timezone";
import { formatRunDate, formatRunDistance } from "@/lib/runUtils";
import { toast } from "sonner";
import { runWithConcurrency } from "@/lib/async";

interface BulkSyncDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  startDate?: Date;
  endDate?: Date;
  // Optional client-side type filter to mirror RecentRunsPanel
  typeFilter?: "all" | RunDetail["type"];
  onDone?: () => void; // called after successful bulk sync to refresh data
}

export function BulkSyncDialog({
  open,
  onOpenChange,
  startDate,
  endDate,
  typeFilter = "all",
  onDone,
}: BulkSyncDialogProps) {
  const userTimezone = getUserTimezone();
  const queryClient = useQueryClient();
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [isSyncing, setIsSyncing] = useState(false);
  const [progress, setProgress] = useState<{
    done: number;
    total: number;
  } | null>(null);

  // Reset selection when dialog opens/closes
  useEffect(() => {
    if (!open) {
      setSelectedIds(new Set());
      setProgress(null);
    }
  }, [open]);

  // When dialog opens, drop any cached results so we never show stale unsynced runs
  useEffect(() => {
    if (open && startDate && endDate) {
      queryClient.removeQueries({
        queryKey: queryKeys.bulkSync({
          startDate,
          endDate,
          userTimezone,
          typeFilter,
        }),
      });
    }
  }, [open, startDate, endDate, typeFilter, userTimezone, queryClient]);

  const {
    data: unsyncedRuns,
    isPending,
    error,
  } = useQuery({
    queryKey: queryKeys.bulkSync({
      startDate,
      endDate,
      userTimezone,
      typeFilter,
    }),
    queryFn: async () => {
      const runs = await fetchRunDetails({
        startDate,
        endDate,
        sortBy: "date",
        sortOrder: "desc",
        synced: "unsynced",
      });
      return runs as RunDetail[];
    },
    enabled: open && !!startDate && !!endDate,
    // Always get a fresh list when opening the dialog
    staleTime: 0,
    refetchOnMount: "always",
    refetchOnWindowFocus: false,
  });

  const filteredRuns = useMemo(() => {
    if (!unsyncedRuns) return [] as RunDetail[];
    const byType =
      typeFilter === "all"
        ? unsyncedRuns
        : unsyncedRuns.filter((r) => r.type === typeFilter);
    // Show up to 200 to keep UI responsive
    return byType.slice(0, 200);
  }, [unsyncedRuns, typeFilter]);

  const allSelected =
    filteredRuns.length > 0 && selectedIds.size === filteredRuns.length;
  const someSelected =
    selectedIds.size > 0 && selectedIds.size < filteredRuns.length;

  const toggleSelectAll = (checked: boolean) => {
    if (checked) {
      setSelectedIds(new Set(filteredRuns.map((r) => r.id)));
    } else {
      setSelectedIds(new Set());
    }
  };

  const toggleOne = (id: string, checked: boolean) => {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (checked) next.add(id);
      else next.delete(id);
      return next;
    });
  };

  const handleBulkSync = async () => {
    if (isSyncing || selectedIds.size === 0) return;
    setIsSyncing(true);
    const ids = Array.from(selectedIds);
    const total = ids.length;
    let successCount = 0;
    let failureCount = 0;
    setProgress({ done: 0, total });

    try {
      await runWithConcurrency(ids, 3, async (runId) => {
        try {
          await syncRun(runId);
          successCount++;
        } catch (e) {
          console.error("Bulk sync failed for", runId, e);
          failureCount++;
        } finally {
          setProgress((p) => ({ done: (p?.done ?? 0) + 1, total }));
        }
      });

      if (failureCount === 0) {
        toast.success(`Synced ${successCount} runs to Google Calendar`);
      } else if (successCount === 0) {
        toast.error("Failed to sync selected runs");
      } else {
        toast.message("Bulk sync finished", {
          description: `${successCount} succeeded, ${failureCount} failed`,
        });
      }

      // Ensure any cached bulk-sync results are cleared so the next open shows fresh data
      queryClient.removeQueries({
        queryKey: queryKeys.bulkSync({
          startDate,
          endDate,
          userTimezone,
          typeFilter,
        }),
      });
      onDone?.();
      onOpenChange(false);
    } finally {
      setIsSyncing(false);
      setSelectedIds(new Set());
      setProgress(null);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[720px] max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Bulk Sync to Google Calendar</DialogTitle>
          <DialogDescription>
            Select unsynced runs in the chosen date range and sync them in one
            go.
          </DialogDescription>
        </DialogHeader>

        {isPending ? (
          <div className="py-10 text-center text-muted-foreground">
            Loading unsynced runs…
          </div>
        ) : error ? (
          <div className="py-4 text-destructive">Error loading runs</div>
        ) : filteredRuns.length === 0 ? (
          <div className="py-10 text-center text-muted-foreground">
            No unsynced runs found for this range.
          </div>
        ) : (
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Checkbox
                  id="select-all"
                  checked={allSelected}
                  onCheckedChange={(v) => toggleSelectAll(Boolean(v))}
                  aria-checked={
                    allSelected ? "true" : someSelected ? "mixed" : "false"
                  }
                />
                <Label htmlFor="select-all" className="select-none">
                  Select All ({filteredRuns.length})
                </Label>
              </div>
              {progress && (
                <div className="text-sm text-muted-foreground">
                  {progress.done} / {progress.total}
                </div>
              )}
            </div>

            <div className="border rounded-md divide-y max-h-[50vh] overflow-y-auto">
              {filteredRuns.map((run) => (
                <div key={run.id} className="flex items-center gap-3 p-3">
                  <Checkbox
                    id={`run-${run.id}`}
                    checked={selectedIds.has(run.id)}
                    onCheckedChange={(v) => toggleOne(run.id, Boolean(v))}
                  />
                  <Label
                    htmlFor={`run-${run.id}`}
                    className="flex-1 flex items-center gap-4 select-none"
                  >
                    <span className="w-40 font-medium">
                      {formatRunDate(run.date)}
                    </span>
                    <span className="w-28 text-sm text-muted-foreground">
                      {formatRunDistance(run.distance)} mi
                    </span>
                    <span className="text-sm text-muted-foreground hidden sm:inline">
                      {run.shoes ?? ""}
                    </span>
                  </Label>
                </div>
              ))}
            </div>
          </div>
        )}

        <DialogFooter>
          <div className="flex w-full items-center justify-between gap-3">
            <div className="text-xs text-muted-foreground">
              Calendar authorization may be required on first use.
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                onClick={() => onOpenChange(false)}
                disabled={isSyncing}
              >
                Cancel
              </Button>
              <Button
                onClick={handleBulkSync}
                disabled={isSyncing || selectedIds.size === 0}
              >
                {isSyncing
                  ? `Syncing ${progress ? `${progress.done}/${progress.total}` : "…"}`
                  : selectedIds.size > 0
                    ? `Sync Selected (${selectedIds.size})`
                    : "Sync Selected"}
              </Button>
            </div>
          </div>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
