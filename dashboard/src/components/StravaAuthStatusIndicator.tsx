import { useStravaAuthStatus } from "@/lib/useStravaAuthStatus";
import { useDashboardStore } from "@/store";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import { cn } from "@/lib/utils";

export function StravaAuthStatusIndicator() {
  const { isAuthenticated } = useDashboardStore();
  const { data: status, isPending, error } = useStravaAuthStatus();

  // Don't show anything if user is not logged in
  if (!isAuthenticated) return null;

  if (isPending) return null;
  if (error) return null;

  const isAuthorized = status?.authorized ?? false;
  const isTokenValid = status?.access_token_valid ?? false;

  // If not authorized or token is invalid, show a button to authorize/re-authorize
  const needsAuthorization = !isAuthorized || !isTokenValid;

  if (needsAuthorization) {
    const handleAuthorize = () => {
      const apiUrl = import.meta.env.VITE_API_URL;
      window.location.href = `${apiUrl}/oauth/strava/authorize`;
    };

    return (
      <Button
        variant="default"
        size="sm"
        onClick={handleAuthorize}
        className={cn(
          "h-auto px-3 py-1 text-xs font-semibold",
          "bg-primary text-primary-foreground shadow-sm",
          "hover:bg-primary/90 hover:shadow-md",
          "transition-all",
        )}
      >
        {isAuthorized ? "⚠ Re-authorize Strava" : "Authorize Strava"}
      </Button>
    );
  }

  // Show badge when authorized and token is valid
  return (
    <Badge variant="default" className="text-xs font-medium">
      Strava ✓
    </Badge>
  );
}

