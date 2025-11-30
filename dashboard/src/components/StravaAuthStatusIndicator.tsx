import { useStravaAuthStatus } from "@/lib/useStravaAuthStatus";
import { useDashboardStore } from "@/store";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import { cn } from "@/lib/utils";

export function StravaAuthStatusIndicator() {
  const { isAuthenticated } = useDashboardStore();
  const { data: status, isPending, error } = useStravaAuthStatus();

  if (isPending) return null;
  if (error) return null;

  const isAuthorized = status?.authorized ?? false;
  const isTokenValid = status?.access_token_valid ?? false;

  // If not authorized or token is invalid, show a button to authorize/re-authorize
  const needsAuthorization = !isAuthorized || !isTokenValid;

  if (needsAuthorization) {
    const handleAuthorize = () => {
      if (!isAuthenticated) return; // Don't allow authorization if not logged in
      const apiUrl = import.meta.env.VITE_API_URL;
      window.location.href = `${apiUrl}/oauth/strava/authorize`;
    };

    return (
      <Button
        variant="outline"
        size="sm"
        onClick={handleAuthorize}
        disabled={!isAuthenticated}
        className={cn(
          "h-auto px-2 py-0.5 text-xs font-medium",
          "border-destructive/50 text-destructive hover:bg-destructive/10 hover:border-destructive",
          !isAuthenticated && "opacity-50 cursor-not-allowed",
        )}
      >
        Strava {isAuthorized ? "⚠ Re-authorize" : "Authorize"}
      </Button>
    );
  }

  // Show badge when authorized and token is valid
  return (
    <Badge
      variant="default"
      className={cn(
        "text-xs font-medium",
        !isAuthenticated && "opacity-50",
      )}
    >
      Strava ✓
    </Badge>
  );
}
