import { useQuery } from "@tanstack/react-query";
import { fetchRecentRuns } from "@/lib/api";
import { getUserTimezone } from "@/lib/timezone";
import { RunsTable } from "@/components/RunsTable";
import { LoadingSpinner } from "@/components/LoadingSpinner";
import { Card } from "@/components/ui/card";

interface RecentRunsPanelProps {
  className?: string;
}

export function RecentRunsPanel({ className }: RecentRunsPanelProps) {
  const userTimezone = getUserTimezone();
  const { data: runs, isPending, error } = useQuery({
    queryKey: ["recent-runs", userTimezone],
    queryFn: () => fetchRecentRuns({ userTimezone }),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  if (isPending) {
    return (
      <div className={`flex flex-col h-full gap-y-4 ${className}`}>
        <h2 className="text-xl font-semibold">Recent Runs</h2>
        <Card className="w-full shadow-none flex justify-center items-center flex-1">
          <LoadingSpinner />
        </Card>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`flex flex-col h-full gap-y-4 ${className}`}>
        <h2 className="text-xl font-semibold">Recent Runs</h2>
        <Card className="w-full shadow-none flex justify-center items-center flex-1">
          <p className="text-destructive">Error: {error.message}</p>
        </Card>
      </div>
    );
  }

  return (
    <div className={`flex flex-col h-full gap-y-4 ${className}`}>
      <div className="flex justify-between items-center flex-shrink-0">
        <h2 className="text-xl font-semibold">Recent Runs</h2>
        <span className="text-sm text-muted-foreground">
          {runs?.length || 0} runs
        </span>
      </div>
      <Card className="w-full shadow-none p-0 overflow-hidden flex-1 min-h-0">
        <RunsTable runs={runs || []} className="h-full" />
      </Card>
    </div>
  );
}