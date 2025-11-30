import { useQuery } from "@tanstack/react-query";
import { fetchStravaAuthStatus } from "@/lib/api";
import { queryKeys } from "@/lib/queryKeys";

export function useStravaAuthStatus() {
  return useQuery({
    queryKey: queryKeys.stravaAuthStatus(),
    queryFn: fetchStravaAuthStatus,
    staleTime: 1 * 60 * 1000, // 1 minute - auth status can change
    refetchOnWindowFocus: false,
  });
}
