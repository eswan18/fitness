import { useQuery } from "@tanstack/react-query";
import { fetchGoogleAuthStatus } from "@/lib/api";
import { queryKeys } from "@/lib/queryKeys";

export function useGoogleAuthStatus() {
  return useQuery({
    queryKey: queryKeys.googleAuthStatus(),
    queryFn: fetchGoogleAuthStatus,
    staleTime: 1 * 60 * 1000, // 1 minute - auth status can change
    refetchOnWindowFocus: false,
  });
}
