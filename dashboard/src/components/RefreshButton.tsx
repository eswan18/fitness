import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { refreshData } from "@/lib/api";
import { notifyError, notifySuccess } from "@/lib/errors";
import type { RefreshDataResponse } from "@/lib/api";

interface RefreshButtonProps {
  onRefreshComplete?: (data: RefreshDataResponse) => void;
}

export function RefreshButton({ onRefreshComplete }: RefreshButtonProps) {
  const queryClient = useQueryClient();
  const [lastRefresh, setLastRefresh] = useState<Date | null>(null);

  const refreshMutation = useMutation({
    mutationFn: refreshData,
    onSuccess: (data) => {
      // Invalidate all queries to refetch data
      queryClient.invalidateQueries();
      setLastRefresh(new Date(data.updated_at));
      notifySuccess(data.message || "Data refreshed");
      onRefreshComplete?.(data);
    },
    onError: (error) => {
      console.error("Failed to refresh data:", error);
      notifyError(error, "Failed to refresh data");
    },
  });

  const handleRefresh = () => {
    refreshMutation.mutate();
  };

  const formatLastRefresh = (date: Date) => {
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / (1000 * 60));

    if (diffMins < 1) {
      return "Just now";
    } else if (diffMins < 60) {
      return `${diffMins} min${diffMins === 1 ? "" : "s"} ago`;
    } else {
      const diffHours = Math.floor(diffMins / 60);
      if (diffHours < 24) {
        return `${diffHours} hour${diffHours === 1 ? "" : "s"} ago`;
      } else {
        return date.toLocaleDateString();
      }
    }
  };

  return (
    <div className="flex flex-col items-end gap-1">
      <Button
        onClick={handleRefresh}
        disabled={refreshMutation.isPending}
        variant="outline"
        size="sm"
      >
        {refreshMutation.isPending ? (
          <>
            <svg
              className="animate-spin h-4 w-4 mr-2"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              ></circle>
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              ></path>
            </svg>
            Refreshing...
          </>
        ) : (
          <>
            <svg
              className="h-4 w-4 mr-2"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
              />
            </svg>
            Refresh Data
          </>
        )}
      </Button>
      {lastRefresh && (
        <span className="text-xs text-muted-foreground">
          Last updated {formatLastRefresh(lastRefresh)}
        </span>
      )}
      {refreshMutation.isError && (
        <span className="text-xs text-destructive">Failed to refresh data</span>
      )}
    </div>
  );
}
