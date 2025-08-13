import { useCallback } from "react";
import { syncRun, unsyncRun } from "@/lib/api";
import { notifyError, notifySuccess } from "@/lib/errors";

interface UseRunSyncOptions {
  onChanged?: () => void;
  onLoadingChange?: (runId: string, loading: boolean) => void;
}

export function useRunSync(options: UseRunSyncOptions = {}) {
  const { onChanged, onLoadingChange } = options;

  const toggleSync = useCallback(
    async (runId: string, isCurrentlySynced: boolean) => {
      onLoadingChange?.(runId, true);
      try {
        if (isCurrentlySynced) {
          const res = await unsyncRun(runId);
          notifySuccess(res.message || "Removed from Google Calendar");
        } else {
          const res = await syncRun(runId);
          notifySuccess(res.message || "Synced to Google Calendar");
        }
        onChanged?.();
      } catch (err) {
        notifyError(err, "Operation failed");
        throw err;
      } finally {
        onLoadingChange?.(runId, false);
      }
    },
    [onChanged, onLoadingChange],
  );

  const syncOne = useCallback(
    async (runId: string) => {
      await toggleSync(runId, false);
    },
    [toggleSync],
  );

  const unsyncOne = useCallback(
    async (runId: string) => {
      await toggleSync(runId, true);
    },
    [toggleSync],
  );

  return { toggleSync, syncOne, unsyncOne };
}
