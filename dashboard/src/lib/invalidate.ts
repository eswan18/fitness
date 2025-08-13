import type { QueryClient } from "@tanstack/react-query";
import { queryKeys } from "@/lib/queryKeys";

export function invalidateRuns(queryClient: QueryClient) {
  queryClient.invalidateQueries({ queryKey: queryKeys.group.runs() });
}

export function invalidateMetrics(queryClient: QueryClient) {
  // Invalidate multiple related metric groups
  queryClient.invalidateQueries({ queryKey: queryKeys.totalMiles() });
  queryClient.invalidateQueries({ queryKey: queryKeys.milesByDay() });
  queryClient.invalidateQueries({ queryKey: queryKeys.rollingMiles({}) });
  queryClient.invalidateQueries({ queryKey: queryKeys.dayTrimp({}) });
  queryClient.invalidateQueries({ queryKey: ["metrics"] });
}

export function invalidateShoes(queryClient: QueryClient) {
  queryClient.invalidateQueries({ queryKey: queryKeys.shoesMileage(true) });
  queryClient.invalidateQueries({ queryKey: queryKeys.shoesMileage(false) });
}

export function invalidateEnvironment(queryClient: QueryClient) {
  queryClient.invalidateQueries({ queryKey: queryKeys.environment() });
}

export function invalidateAllDash(queryClient: QueryClient) {
  invalidateRuns(queryClient);
  invalidateMetrics(queryClient);
  invalidateShoes(queryClient);
  invalidateEnvironment(queryClient);
}
