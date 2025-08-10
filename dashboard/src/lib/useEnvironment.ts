import { useQuery } from "@tanstack/react-query";
import { fetchEnvironment } from "@/lib/api";
import { queryKeys } from "@/lib/queryKeys";

export function useEnvironment() {
  return useQuery({
    queryKey: queryKeys.environment(),
    queryFn: fetchEnvironment,
    staleTime: 5 * 60 * 1000, // 5 minutes - environment rarely changes
    refetchOnWindowFocus: false,
  });
}